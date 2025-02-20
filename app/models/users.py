
from pydantic import ConfigDict, BaseModel, Field, EmailStr

class User(BaseModel):
	username: str
	email: str | None = None
