from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import get_users_collection, require_admin_or_professor
from backend.models import AdminEnrollmentRequest, UserInDB

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/enroll")
async def admin_enroll(
    request: AdminEnrollmentRequest,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
):
    result = users_collection.update_one(
        {"username": request.username}, {"$addToSet": {"subjects": request.subject}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "enrolled", "subject": request.subject, "user": request.username}


@router.post("/unenroll")
async def admin_unenroll(
    request: AdminEnrollmentRequest,
    user: UserInDB = Depends(require_admin_or_professor),
    users_collection=Depends(get_users_collection),
):
    result = users_collection.update_one(
        {"username": request.username}, {"$pull": {"subjects": request.subject}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "status": "unenrolled",
        "subject": request.subject,
        "user": request.username,
    }
