import os
from fastapi import FastAPI
from mangum import Mangum
from app.api.api_v1.api import router as api_router

load_dotenv()

app = FastAPI(root_path=os.getenv("ROOT_PATH"))


@app.get("/")
async def root():
  return {"Welcome": "Serveless-blog-api"}

app.include_router(api_router, prefix="/api/v1")

handler = Mangum(app)
