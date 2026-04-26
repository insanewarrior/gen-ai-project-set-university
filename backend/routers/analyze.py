from fastapi import APIRouter, Depends, HTTPException

import services.rag_service as rag_service
import services.rate_limit_service as rate_limit_service
from middleware.auth import UserContext, get_user_context
from middleware.sanitize import sanitize_llm_input
from models.query_models import AnalyzeRequest

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", status_code=200)
async def create_analysis(
    body: AnalyzeRequest,
    user_context: UserContext = Depends(get_user_context),
):
    sanitized = sanitize_llm_input(body.program)
    rate_result = rate_limit_service.check_and_increment(
        user_context["user_id"],
        user_create_date=user_context["user_create_date"],
        is_premium=user_context["is_premium"],
    )
    if not rate_result["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Daily query limit reached",
                "code": "RATE_LIMIT_EXCEEDED",
                "detail": {
                    "resetAt": rate_result["reset_at"],
                    "limit": rate_result.get("tier_limit", 3),
                },
            },
        )
    try:
        result = rag_service.analyze(user_context["user_id"], sanitized)
    except RuntimeError:
        raise HTTPException(
            status_code=500,
            detail={
                "error": (
                    "I couldn't process that question right now. "
                    "Please try again."
                ),
                "code": "AI_UNAVAILABLE",
            },
        )
    result["queriesRemaining"] = rate_result["queries_remaining"]
    result["tierLimit"] = rate_result.get("tier_limit", 3)
    return {"data": result}
