import json
import logging
import os
import uuid
from pathlib import Path

from google import genai
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

import config
import services.session_service as session_service

logger = logging.getLogger(__name__)

_index = None
_metadata = None
_source_to_title: dict[str, str] = {}
_model = SentenceTransformer("all-MiniLM-L6-v2")

PLAN_KEYWORDS = (
    "plan", "program", "routine", "schedule",
    "next week", "weekly", "this week",
    "structure my", "lay out", "design a",
)


def _download_from_s3(dest_path: Path) -> None:
    import boto3
    dest_path.mkdir(parents=True, exist_ok=True)
    s3 = boto3.client("s3")
    bucket = config.S3_FAISS_BUCKET
    for fname in ["index.faiss", "index_metadata.json"]:
        s3.download_file(bucket, f"faiss_index/{fname}", str(dest_path / fname))


def _load_index() -> None:
    global _index, _metadata, _source_to_title
    index_path = Path(config.FAISS_INDEX_PATH)
    if not (index_path / "index.faiss").exists():
        if config.S3_FAISS_BUCKET:
            _download_from_s3(index_path)
        else:
            raise FileNotFoundError(
                f"FAISS index not found at {index_path} and S3_FAISS_BUCKET is not configured"
            )
    _index = faiss.read_index(str(index_path / "index.faiss"))
    with open(index_path / "index_metadata.json") as f:
        _metadata = json.load(f)
    _source_to_title = {
        c["source"]: c.get("doc_title", c["source"])
        for c in _metadata if c.get("source")
    }
    logger.info("FAISS index loaded: %d vectors", _index.ntotal)


try:
    _load_index()
except Exception as exc:
    logger.error("Failed to load FAISS index at startup: %s", exc)


def _embed_query(query_text: str) -> np.ndarray:
    emb = _model.encode([query_text], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(emb)
    return emb


def _search_knowledge(query_emb: np.ndarray, k: int = 3) -> list[dict]:
    if _index is None or _metadata is None:
        return []
    distances, indices = _index.search(query_emb, k)
    results = []
    for idx in indices[0]:
        if idx != -1 and idx < len(_metadata):
            results.append(_metadata[idx])
    return results


def _format_sessions(sessions: list) -> tuple[str, int]:
    recent = sessions[:10]
    lines = []
    for s in recent:
        date = s.get("sessionDate", "unknown")
        sport = s.get("sport", "")
        for ex in s.get("exercises", []):
            name = ex.get("exerciseName", ex.get("exercise_name", ""))
            sets = ex.get("sets", [])
            set_str = ", ".join(
                f"{float(st.get('weight', 0))}kg x{st.get('reps', 0)} @RPE{float(st.get('rpe', 0))}"
                for st in sets if st.get('weight')
            )
            lines.append(f"{date} | {sport}: {name} — {set_str}")
    if not lines:
        return "No training sessions logged yet.", len(sessions)
    return "\n".join(lines), len(sessions)


def _confidence_label(session_count: int) -> str:
    if session_count <= 5:
        return "low"
    if session_count <= 30:
        return "medium"
    return "high"


def _confidence_framing(session_count: int) -> str:
    if session_count <= 5:
        return "Based on your first few sessions..."
    if session_count <= 30:
        return "Looking at your recent training data..."
    return "Based on your training history, a clear pattern shows..."


def _is_planning_query(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in PLAN_KEYWORDS)


def _build_prompt(
    query: str,
    personal_context: str,
    session_count: int,
    knowledge_chunks: list[dict],
) -> str:
    knowledge_text = "\n".join(
        f"[{chunk.get('source', '')} — {chunk.get('principle', '')}]: {chunk.get('text', '')}"
        for chunk in knowledge_chunks
    )
    framing = _confidence_framing(session_count)

    if _is_planning_query(query):
        response_guidance = (
            'A concrete training plan in markdown. Use a day-by-day structure '
            '(### Day 1, ### Day 2, ...). For every exercise specify sets × reps '
            '@ target weight, deriving target weights from the athlete\'s most '
            'recent logged maxes (apply percentages from the retrieved cycle '
            'templates). Open with one short paragraph explaining the plan\'s '
            'rationale (why these days, lifts, intensities), then the day-by-day '
            'breakdown, then close with a one-line note on what to track. '
            'Cite the cycle templates you drew from.'
        )
    else:
        response_guidance = 'Your coaching response here (2-3 paragraphs).'

    return f"""You are StrengthWise, an AI strength coach. Analyze the athlete's question using their personal training data and general strength science knowledge provided below.

ATHLETE QUESTION: {query}

PERSONAL TRAINING DATA ({session_count} sessions):
{personal_context}

STRENGTH SCIENCE KNOWLEDGE:
{knowledge_text}

{framing}

Respond with a JSON object in this exact format:
{{
  "response": "{response_guidance}",
  "personal_citations": [
    {{"sessionDate": "YYYY-MM-DD", "exercise": "exercise name", "detail": "specific metric or observation"}}
  ],
  "knowledge_citations": [
    {{"source": "filename.md", "principle": "section header"}}
  ]
}}

Rules:
- Only cite sessions that are directly relevant to the question
- Only cite knowledge chunks that appear in the provided knowledge above
- If data is insufficient, say so honestly in the response; return empty citation arrays
- The "response" field must be a single JSON string. Use \\n for line breaks inside it.
- Return ONLY the JSON object, no markdown code blocks around it"""


def _call_gemini(prompt: str) -> dict:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
    )
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"response": text, "personal_citations": [], "knowledge_citations": []}


def _build_analyze_prompt(
    program_text: str,
    personal_context: str,
    session_count: int,
    knowledge_chunks: list[dict],
) -> str:
    knowledge_text = "\n".join(
        f"[{chunk.get('source', '')} — {chunk.get('principle', '')}]: {chunk.get('text', '')}"
        for chunk in knowledge_chunks
    )
    framing = _confidence_framing(session_count)
    return f"""You are StrengthWise, an AI strength coach. Evaluate the athlete's training program using general strength science principles and their personal training history.

TRAINING PROGRAM TO EVALUATE:
{program_text}

ATHLETE'S PERSONAL TRAINING DATA ({session_count} sessions):
{personal_context}

STRENGTH SCIENCE KNOWLEDGE:
{knowledge_text}

{framing}

Respond with a JSON object in this exact format:
{{
  "response": "Your program evaluation here (2-4 paragraphs). Cover: alignment with principles, fit with athlete's current patterns, specific modifications suggested.",
  "personal_citations": [
    {{"sessionDate": "YYYY-MM-DD", "exercise": "exercise name", "detail": "specific metric or observation"}}
  ],
  "knowledge_citations": [
    {{"source": "filename.md", "principle": "section header"}}
  ]
}}

Rules:
- Evaluate program structure, volume, intensity, and exercise selection
- Only cite sessions that relate to the exercises or patterns in the submitted program
- Only cite knowledge chunks provided above
- If data is insufficient, acknowledge it honestly; return empty citation arrays
- Return ONLY the JSON object, no markdown code blocks"""


def analyze(user_id: str, program_text: str) -> dict:
    try:
        query_emb = _embed_query(program_text)
        knowledge_chunks = _search_knowledge(query_emb)
        sessions = session_service.get_sessions(user_id)
        personal_context, session_count = _format_sessions(sessions)
        prompt = _build_analyze_prompt(program_text, personal_context, session_count, knowledge_chunks)
        parsed = _call_gemini(prompt)
    except Exception as exc:
        if isinstance(exc, RuntimeError):
            raise
        logger.error("Gemini API error in analyze: %s", exc)
        raise RuntimeError("AI_UNAVAILABLE") from exc

    personal_citations = [
        {"sessionDate": c.get("sessionDate", ""), "exercise": c.get("exercise", ""), "detail": c.get("detail", "")}
        for c in parsed.get("personal_citations", [])
    ]
    knowledge_citations = [
        {
            "source": c.get("source", ""),
            "doc_title": _source_to_title.get(c.get("source", ""), c.get("source", "")),
            "principle": c.get("principle", ""),
        }
        for c in parsed.get("knowledge_citations", [])
    ]

    return {
        "queryId": str(uuid.uuid4()),
        "response": parsed.get("response", ""),
        "citations": {
            "personal": personal_citations,
            "knowledge": knowledge_citations,
        },
        "confidence": _confidence_label(session_count),
    }


def query(user_id: str, query_text: str) -> dict:
    try:
        query_emb = _embed_query(query_text)
        knowledge_chunks = _search_knowledge(query_emb)
        sessions = session_service.get_sessions(user_id)
        personal_context, session_count = _format_sessions(sessions)
        prompt = _build_prompt(query_text, personal_context, session_count, knowledge_chunks)
        parsed = _call_gemini(prompt)
    except Exception as exc:
        if isinstance(exc, RuntimeError):
            raise
        logger.error("Gemini API error: %s", exc)
        raise RuntimeError("AI_UNAVAILABLE") from exc

    personal_citations = [
        {"sessionDate": c.get("sessionDate", ""), "exercise": c.get("exercise", ""), "detail": c.get("detail", "")}
        for c in parsed.get("personal_citations", [])
    ]
    knowledge_citations = [
        {
            "source": c.get("source", ""),
            "doc_title": _source_to_title.get(c.get("source", ""), c.get("source", "")),
            "principle": c.get("principle", ""),
        }
        for c in parsed.get("knowledge_citations", [])
    ]

    return {
        "queryId": str(uuid.uuid4()),
        "response": parsed.get("response", ""),
        "citations": {
            "personal": personal_citations,
            "knowledge": knowledge_citations,
        },
        "confidence": _confidence_label(session_count),
    }
