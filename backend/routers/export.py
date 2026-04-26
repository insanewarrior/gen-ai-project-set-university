from fastapi import APIRouter, Depends, Response

import services.export_service as export_service
import services.session_service as session_service
from middleware.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/export", tags=["export"])


@router.post("")
async def export_training_data(
    current_user: CurrentUser = Depends(get_current_user),
):
    sessions = session_service.get_sessions(current_user)
    csv_content = export_service.generate_csv(sessions)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=training-data.csv"},
    )
