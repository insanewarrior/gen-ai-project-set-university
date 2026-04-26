from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

import services.feedback_service as feedback_service
from middleware.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    queryId: str
    rating: str

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v not in ('up', 'down'):
            raise ValueError('rating must be "up" or "down"')
        return v


@router.post("", status_code=200)
async def submit_feedback(
    body: FeedbackRequest,
    user_id: CurrentUser = Depends(get_current_user),
):
    feedback_service.submit_feedback(body.queryId, user_id, body.rating)
    return {"data": {"queryId": body.queryId, "rating": body.rating}}
