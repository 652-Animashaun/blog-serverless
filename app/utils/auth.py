import os
import jwt
from jwt import PyJWKClient
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, status, Depends, Security, HTTPException
from datetime import date, datetime, time, timedelta, timezone
from typing import Annotated
from app.models.users import User
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from starlette.responses import RedirectResponse
from starlette.requests import Request


signin_url = 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_ftTN1aEr4/.well-known/jwks.json'
security = HTTPBearer(auto_error=False)

CLIENT_SECRET = os.environ["CLIENT_SECRET"]
CLIENT_ID = os.environ["CLIENT_ID"]
ISSUER = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_ftTN1aEr4"


oauth = OAuth()
oauth.register(
  name='oidc',
  authority=ISSUER,
  client_id=CLIENT_ID,
  client_secret=CLIENT_SECRET,
  server_metadata_url='https://cognito-idp.us-east-1.amazonaws.com/us-east-1_ftTN1aEr4/.well-known/openid-configuration',
  client_kwargs={'scope': 'email openid phone'}
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")

async def verify_token(token:str)-> User:
	jwks_client = PyJWKClient(signin_url)
	

	try:
		signing_key = jwks_client.get_signing_key_from_jwt(token)
		payload = jwt.decode(
						token,
						signing_key,
						audience=CLIENT_ID,
						options={"verify_exp": True},
						algorithms=["RS256"],
					)
		user = User(username=payload["cognito:username"], email=payload["email"])
		return user
	except jwt.ExpiredSignatureError:
		raise HTTPException(status_code=401, detail="Token has expired")
	except jwt.InvalidTokenError as e:
		raise HTTPException(status_code=403, detail="Invalid token")

async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Security(security)]):
	if not credentials:
		return False
	try:
		return await verify_token(credentials.credentials)
	except HTTPException:
		return False


		

	