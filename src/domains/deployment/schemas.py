from typing import Optional
from fastapi_camelcase import CamelModel

class DeploymentCreateRequest(CamelModel):
    class Resources(CamelModel):
        cpu_allocated: float
        memory_allocated: float


    name: str
    description: Optional[str]
    
    cluster_id: str
    user_id: str
    
    path_to_docker_image: str
    resources: Resources
    priority: int
    
    