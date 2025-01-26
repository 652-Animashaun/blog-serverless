from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def all_posts():
    return {"message": "Posts!"}