from typing import Optional
from datetime import datetime
from fastapi_camelcase import CamelModel


class UserCreateRequest(CamelModel):
    name: str
    username: str
    organisation_id: Optional[str]
    password: str

class UserCreateResponse(CamelModel):
    id: str
    name: str
    organisation_id: Optional[str] = None

class UserLoginRequest(CamelModel):
    username: str
    password: str

class UserLoginResponse(CamelModel):
    id: str
    name: str
    username: str
    organisation_id: Optional[str] = None
    expires_at: datetime
    session_id: str