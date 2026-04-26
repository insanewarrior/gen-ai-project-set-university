from fastapi import APIRouter, Depends

import services.profile_service as profile_service
import services.rate_limit_service as rate_limit_service
from middleware.auth import UserContext, get_user_context

router = APIRouter(prefix="/profile", tags=["profile"])

_TIER_LIMITS = {"free": 3, "onboarding": 10, "premium": -1}


@router.get("")
async def get_profile(user_context: UserContext = Depends(get_user_context)):
    user_id = user_context["user_id"]
    tier = profile_service.resolve_tier(
        user_context["user_create_date"],
        user_context["is_premium"],
    )
    tier_limit = _TIER_LIMITS[tier]

    today_count = rate_limit_service.get_today_count(user_id)
    if tier_limit == -1:
        queries_remaining = -1  # premium: unlimited
    else:
        queries_remaining = max(0, tier_limit - today_count)

    return {
        "data": {
            "totalSessions": profile_service.get_total_session_count(user_id),
            "totalQueries": profile_service.get_total_query_count(user_id),
            "tier": tier,
            "accountCreatedAt": user_context["user_create_date"],
            "queriesRemainingToday": queries_remaining,
            "tierLimit": tier_limit,
        }
    }
