from fastapi import APIRouter, Depends, HTTPException, Query

import services.session_service as session_service
from middleware.auth import CurrentUser, get_current_user
from models.session_models import SessionCreate

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", status_code=201)
async def create_session(
    body: SessionCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    data = body.model_dump(by_alias=True)
    session = session_service.create_session(current_user, data)
    year_month = data['sessionDate'][:7]
    month_count = session_service.get_month_count(current_user, year_month)
    return {"data": {"session": session, "monthCount": month_count}}


@router.get("")
async def list_sessions(current_user: CurrentUser = Depends(get_current_user)):
    sessions = session_service.get_sessions(current_user)
    return {"data": {"sessions": sessions}}


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    session_date: str = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
):
    session = session_service.get_session(current_user, session_id, session_date)
    if session is None:
        raise HTTPException(status_code=404, detail={"error": "Not found", "code": "NOT_FOUND"})
    return {"data": {"session": session}}
