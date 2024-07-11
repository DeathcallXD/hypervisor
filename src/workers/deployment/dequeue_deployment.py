import os
import asyncio
from lib.logging_conf import set_logger

from ...domains.deployment.services import DeploymentService
from ...dependencies import get_async_session_1

logger = set_logger(__name__)

async def dequeue_deployment() -> None:
    async with get_async_session_1() as session:
        try:
            await DeploymentService(session)._dequeue_deployment()
        except Exception as e:
            import traceback
            logger.error(f"error in dequeue_deployment worker: {traceback.format_exc()}")

if __name__ == "__main__":
    while(True):
        try:
            asyncio.run(dequeue_deployment())
        except Exception as e:
            import traceback
            logger.error(f"error in dequeue_deployment worker: {traceback.format_exc()}")