from fastapi_camelcase import CamelModel
from typing import Optional


class OrganisationCreateRequest(CamelModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    user_id: str

class OrganisationCreateResponse(CamelModel):
    id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    invite_code: str

class UserOrganisationJoinRequest(CamelModel):
    invite_code: str
    user_id: str

