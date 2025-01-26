from fastapi import FastAPI
from mangum import Mangum
from app.api.api_v1.endpoints.posts import router as user_api


app = FastAPI()


@app.get("/")
async def root():
  return {"Welcome": "Serveless-blog-api"}

app.include_router(user_api, prefix="/api/v1")

handler = Mangum(app)
