from fastapi import APIRouter, Depends, HTTPException, Query

import services.exercise_service as exercise_service
from middleware.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("")
async def get_exercises(
    sport_type: str | None = Query(None, alias="sportType"),
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        exercises = exercise_service.get_exercises(sport_type)
        return {"data": {"exercises": exercises}}
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid sportType",
                "code": "VALIDATION_ERROR",
                "detail": {"validValues": ["grip", "armwrestling", "powerlifting", "general"]},
            },
        )
