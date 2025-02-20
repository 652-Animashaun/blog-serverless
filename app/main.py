import os
from fastapi import FastAPI
from mangum import Mangum
from app.api.api_v1.api import router as api_router
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



app = FastAPI(root_path="/dev")
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

# oauth.register(
#   name='oidc',
#   authority='https://cognito-idp.us-east-1.amazonaws.com/us-east-1_QLYE30HNc',
#   client_id='37t1vbfdaft79fa48s67v7tls0',
#   client_secret='<client secret>',
#   server_metadata_url='https://cognito-idp.us-east-1.amazonaws.com/us-east-1_QLYE30HNc/.well-known/openid-configuration',
#   client_kwargs={'scope': 'email openid phone'}
# )

@app.get("/")
async def root():
  return {"Welcome": "Serveless-blog-api"}

app.include_router(api_router, prefix="/api/v1")

handler = Mangum(app)
