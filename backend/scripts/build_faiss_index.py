"""Build FAISS vector index from knowledge base markdown documents."""

import json
import re
import sys
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DIR = Path("backend/data/knowledge")
OUTPUT_DIR = Path("backend/data/faiss_index")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


def _extract_doc_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# ") and not line.startswith("## "):
            return line[2:].strip()
    return fallback


def chunk_document(filepath: Path) -> list[dict]:
    text = filepath.read_text()
    doc_title = _extract_doc_title(text, filepath.stem)
    sections = re.split(r"\n(?=## )", text)
    chunks = []
    for section in sections:
        lines = section.strip().split("\n")
        if not lines:
            continue
        header = lines[0].replace("## ", "").strip() if lines[0].startswith("##") else filepath.stem
        body = "\n".join(lines[1:]).strip()
        paragraphs = [p.strip() for p in body.split("\n\n") if len(p.strip()) >= 50]
        if not paragraphs:
            if len(body) >= 50:
                paragraphs = [body]
            else:
                continue
        for para in paragraphs:
            chunks.append({
                "source": filepath.name,
                "doc_title": doc_title,
                "principle": header,
                "text": para,
            })
    return chunks


def main():
    if not KNOWLEDGE_DIR.exists():
        print(f"ERROR: Knowledge directory not found: {KNOWLEDGE_DIR}", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(KNOWLEDGE_DIR.glob("**/*.md"))
    if not md_files:
        print(f"ERROR: No .md files found in {KNOWLEDGE_DIR}", file=sys.stderr)
        sys.exit(1)

    all_chunks = []
    for filepath in md_files:
        doc_chunks = chunk_document(filepath)
        all_chunks.extend(doc_chunks)
        print(f"  Chunked {filepath.name}: {len(doc_chunks)} chunks")

    if not all_chunks:
        print("ERROR: No chunks produced from knowledge documents.", file=sys.stderr)
        sys.exit(1)

    texts = [c["text"] for c in all_chunks]
    print(f"\nEmbedding {len(texts)} chunks with {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(embeddings)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    index_path = OUTPUT_DIR / "index.faiss"
    metadata_path = OUTPUT_DIR / "index_metadata.json"

    faiss.write_index(index, str(index_path))
    with open(metadata_path, "w") as f:
        json.dump(all_chunks, f, indent=2)

    index_size = index_path.stat().st_size
    metadata_size = metadata_path.stat().st_size
    total_size = index_size + metadata_size

    print(f"\nBuilt FAISS index with {len(all_chunks)} chunks from {len(md_files)} documents.")
    print(f"Index size: {total_size:,} bytes ({total_size / 1_048_576:.2f} MB)")
    print(f"  index.faiss:         {index_size:,} bytes")
    print(f"  index_metadata.json: {metadata_size:,} bytes")
    print(f"Output: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
