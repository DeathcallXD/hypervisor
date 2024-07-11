from enum import Enum

class DeploymentStatus(Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    DEPLOYED = "deployed"