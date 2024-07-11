from typing import Optional
from fastapi_camelcase import CamelModel

class Resources(CamelModel):
    cpu_allocated: float
    memory_allocated: float

class ClusterCreateRequest(CamelModel):
    name: str
    description: Optional[str]
    
    user_id: str
    organisation_id: str
    
    resources: Resources
    
    