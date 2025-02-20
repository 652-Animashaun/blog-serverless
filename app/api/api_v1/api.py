from fastapi import APIRouter

from app.api.api_v1.endpoints import posts, users

router = APIRouter()
router.include_router(posts.router, prefix="/posts", tags=["Posts"])
router.include_router(users.router, prefix="/users", tags=["Users"])
