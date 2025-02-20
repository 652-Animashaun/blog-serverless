from fastapi import APIRouter, Depends, HTTPException, status
from typing_extensions import Annotated
from app.utils.auth import oauth, verify_token, get_current_user
from app.models.users import User
from starlette.requests import Request
from starlette.responses import RedirectResponse

router = APIRouter()

@router.get("/")
async def all_posts(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        return RedirectResponse(url="/api/v1/users/login")
    print("current_user", current_user)
    return {"Welcome": "Shaun's Blog", "user": current_user}