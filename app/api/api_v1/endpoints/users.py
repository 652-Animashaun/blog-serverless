
import os
import jwt
from pprint import pprint
from fastapi import APIRouter, HTTPException, status, Depends
from starlette.requests import Request
from app.utils.auth import oauth, verify_token
from starlette.responses import RedirectResponse


BASE_URL = os.environ["BASE_URL"]


router = APIRouter()

@router.get("/login")
async def login(request: Request):
    redirect_uri = f"{BASE_URL}/api/v1/users/token"
    return await oauth.oidc.authorize_redirect(request, redirect_uri)

@router.get("/token")
async def authorize(request: Request):
    payload = await oauth.oidc.authorize_access_token(request)
    token = payload["id_token"]
    res = await verify_token(token)
    user = payload["userinfo"]
    return res