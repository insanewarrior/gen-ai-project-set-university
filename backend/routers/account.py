from fastapi import APIRouter, Depends

from middleware.auth import CurrentUser, get_current_user
import services.account_service as account_service

router = APIRouter(prefix="/account", tags=["account"])


@router.delete("")
async def delete_account(
    current_user: CurrentUser = Depends(get_current_user),
):
    account_service.delete_account(current_user)
    return {"deleted": True}
