from fastapi import APIRouter, Depends, HTTPException

import services.rag_service as rag_service
import services.rate_limit_service as rate_limit_service
from middleware.auth import CurrentUser, get_current_user
from middleware.sanitize import sanitize_llm_input
from models.query_models import QueryRequest

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", status_code=200)
async def create_query(
    body: QueryRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    sanitized = sanitize_llm_input(body.query)
    rate_result = rate_limit_service.check_and_increment(current_user)
    if not rate_result["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Daily query limit reached",
                "code": "RATE_LIMIT_EXCEEDED",
                "detail": {"resetAt": rate_result["reset_at"], "limit": 3},
            },
        )
    try:
        result = rag_service.query(current_user, sanitized)
    except RuntimeError:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "I couldn't process that question right now. Please try again.",
                "code": "AI_UNAVAILABLE",
            },
        )
    result["queriesRemaining"] = rate_result["queries_remaining"]
    return {"data": result}
