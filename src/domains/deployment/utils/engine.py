import json

from lib.redis import RedisManager
from lib.http_exception_detail import HttpExceptionDetail
from lib.logging_conf import set_logger

from ....config import settings
from ..constants import DeploymentStatus

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD


DEPLOYMENT_PRIORITY_MAP = {
    f"{DeploymentStatus.QUEUED.value}": 3,
    f"{DeploymentStatus.IN_PROGRESS.value}": 2,
    f"{DeploymentStatus.DEPLOYED.value}": 1
}


"""
    Assumptions:
    assuming max memory allocated to a deployment is 1TiB
    assuming max cpu allocated to a deployment is 256vCPU

    Also for each deployment I am assuming that memory and cpu will always be whole numbers, 

    We can fix it by simply a scaling factor of 10
"""


logger = set_logger(__name__)

def custom_sort_deployment_map(deployment: dict):
    return (DEPLOYMENT_PRIORITY_MAP[deployment["status"]], deployment["priority"])


class DeploymentEngine:
    def __init__(self):
        self.redis_manager = RedisManager(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)

        self.deployment_cluster_map = self._fetch_deployment_map()
        self.cluster_usage_map = self._fetch_cluster_usage_map()

    def _fetch_deployment_map(self):
        cluster_deployment_map = self.redis_manager.get_key("cluster_deployment_map")
        if not cluster_deployment_map:
            cluster_deployment_map = {}
        else:
            cluster_deployment_map = json.loads(cluster_deployment_map)

        return cluster_deployment_map

    
    def _fetch_cluster_usage_map(self):
        cluster_free_resources_map = self.redis_manager.get_key("cluster_free_resources_map")
        if not cluster_free_resources_map:
            cluster_free_resources_map = {}
        else:
            cluster_free_resources_map = json.loads(cluster_free_resources_map)

        return cluster_free_resources_map
    
    def _add_free_resource_to_map(self, cluster_id, cpu_available, memory_available):
        cluster_free_resources_map = self.redis_manager.get_key("cluster_free_resources_map")
        if not cluster_free_resources_map:
            cluster_free_resources_map = {}
        else:
            cluster_free_resources_map = json.loads(cluster_free_resources_map)

        cluster_free_resources_map[cluster_id] = {
            "cpu_available": cpu_available,
            "memory_available": memory_available
        }

        self.redis_manager.set_key("cluster_free_resources_map", json.dumps(cluster_free_resources_map))
        self.cluster_usage_map = cluster_free_resources_map
    
    def _add_deployment_to_queue(self, cluster_id, deployment_id, priority, cpu_allocated, memory_allocated, status):
        deployment_map = self.redis_manager.get_key("cluster_deployment_map")

        if not deployment_map:
            deployment_map = {}
        else:
            deployment_map = json.loads(deployment_map)
        
        deployments_scheduled = deployment_map.get(cluster_id)
        if not deployments_scheduled:
            deployments_scheduled = []
        
        deployments_scheduled.append({
            "deployment_id": deployment_id,
            "priority": priority,
            "cpu_allocated": cpu_allocated,
            "memory_allocated": memory_allocated,
            "status": status
        })

        deployment_map[cluster_id] = sorted(deployments_scheduled, key=custom_sort_deployment_map, reverse=True)
        self.redis_manager.set_key("cluster_deployment_map", json.dumps(deployment_map))
        self.deployment_cluster_map = deployment_map

    def _remove_deployment_from_queue(self, cluster_id, deployment_id, cpu_allocated, memory_allocated):
        deployment_map = self._fetch_deployment_map()
        deployments_scheduled = deployment_map.get(cluster_id)
        if not deployments_scheduled:
            deployments_scheduled = []
        
        deployment_present_in_queue = deployment_id in [deployment["deployment_id"] for deployment in deployments_scheduled]
        if deployment_present_in_queue:
            deployments_scheduled = [deployment for deployment in deployments_scheduled if deployment["deployment_id"] != deployment_id]
            deployments_scheduled = sorted(deployments_scheduled, key=custom_sort_deployment_map, reverse=True)
            deployment_map[cluster_id] = deployments_scheduled
            self.redis_manager.set_key("cluster_deployment_map", json.dumps(deployment_map))
            self.deployment_cluster_map = deployment_map

            cluster_usage = self.cluster_usage_map[cluster_id]
            cluster_usage["cpu_available"] -= cpu_allocated
            cluster_usage["memory_available"] -= memory_allocated
            self.redis_manager.set_key("cluster_free_resources_map", json.dumps(cluster_usage))
            self.cluster_usage_map = cluster_usage


    """
        Will optimise on priority,
        If not then number of deployments,
        then maximum average resource consumption
    """

    def _get_deployments_to_deploy_from_same_priority(self, deployment_list: list[dict], available_cpu: int, available_memory: int):
        """
            This method will try to accomodate as many deployments as possible in the same priority
            with least amount of resources utilised

            Resource utilisation is calculated based on the following formula
            cpu_utilisation = (cpu_allocated - cpu_utilised) / cpu_allocated
            memory_utilisation = (memory_allocated - memory_utilised) / memory_allocated

            total utilisation = (cpu_utilisation + memory_utilisation) / 2
        """
        n = len(deployment_list)
    
        # Initialize the DP table
        dp = [[[float('inf')] * (available_cpu + 1) for _ in range(available_memory + 1)] for _ in range(n + 1)]
        dp[0][0][0] = 0

        # Track the choices
        choice = [[[None] * (available_cpu + 1) for _ in range(available_memory + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            memory_used = deployment_list[i - 1]["memory_allocated"]
            cpu_used = deployment_list[i - 1]["cpu_allocated"]

            deployment_id = deployment_list[i - 1]["deployment_id"]

            for mem in range(available_memory + 1):
                for cpu in range(available_cpu + 1):
                    # Do not take the item
                    dp[i][mem][cpu] = dp[i - 1][mem][cpu]
                    choice[i][mem][cpu] = (mem, cpu, False, deployment_id, {"memory_allocated": memory_used, "cpu_allocated": cpu_used})
                    # Take the item if it fits
                    if mem >= memory_used and cpu >= cpu_used and dp[i - 1][mem - memory_used][cpu - cpu_used] != float('inf'):
                        if dp[i][mem][cpu] > dp[i - 1][mem - memory_used][cpu - cpu_used] + 1:
                            dp[i][mem][cpu] = dp[i - 1][mem - memory_used][cpu - cpu_used] + 1
                            choice[i][mem][cpu] = (mem - memory_used, cpu - cpu_used, True, deployment_id, {"memory_allocated": memory_used, "cpu_allocated": cpu_used})

        # Find the minimum resource usage
        min_usage = float('inf')
        end_mem = 0
        end_cpu = 0
        for mem in range(available_memory + 1):
            for cpu in range(available_cpu + 1):
                if dp[n][mem][cpu] != float('inf'):
                    cpu_utilisation = (available_cpu - cpu) / available_cpu
                    memory_utilisation = (available_memory - mem) / available_memory
                    resource_usage = (cpu_utilisation + memory_utilisation) / 2
                    if resource_usage < min_usage:
                        min_usage = resource_usage
                        end_mem = mem
                        end_cpu = cpu

        # Reconstruct the chosen items
        chosen_items = []
        i = n
        mem = end_mem
        cpu = end_cpu

        total_cpu_used = 0
        total_memory_used = 0

        while i > 0:
            prev_mem, prev_cpu, took, deployment_id, resource = choice[i][mem][cpu]
            if took:
                chosen_items.append(i - 1)
                total_cpu_used += resource["cpu_allocated"]
                total_memory_used += resource["memory_allocated"]
            i -= 1
            mem = prev_mem
            cpu = prev_cpu

        chosen_items.reverse()
        
        
        return chosen_items, total_cpu_used, total_memory_used

    def _is_cluster_locked(self, cluster_id):
        cluster_locked = self.redis_manager.get_key(f"locked_cluster_{cluster_id}")
        return cluster_locked == "true"
        
    def _lock_cluster(self, cluster_id):
        self.redis_manager.set_key(f"locked_cluster_{cluster_id}", "true")

        locked_clusters: str = self.redis_manager.get_key("locked_clusters")
        if locked_clusters:
            locked_clusters_arr = locked_clusters.split(",")
            if cluster_id not in locked_clusters_arr:
                locked_clusters_arr.append(cluster_id)
                self.redis_manager.set_key("locked_clusters", ",".join(locked_clusters_arr))
        else:
            self.redis_manager.set_key("locked_clusters", cluster_id)

    def _unlock_cluster(self, cluster_id):
        self.redis_manager.set_key(f"locked_cluster_{cluster_id}", "false")
        locked_clusters: str = self.redis_manager.get_key("locked_clusters")
        if locked_clusters:
            locked_clusters_arr = locked_clusters.split(",")
            if cluster_id in locked_clusters_arr:
                locked_clusters_arr.remove(cluster_id)
                self.redis_manager.set_key("locked_clusters", ",".join(locked_clusters_arr))

        self.redis_manager.set_key("locked_clusters", json.dumps(locked_clusters))

    def _get_locked_clusters(self):
        locked_clusters: str = self.redis_manager.get_key("locked_clusters")
        if locked_clusters:
            return locked_clusters.split(",")

    def _predict_deployments_to_deploy(self, cluster_id):
        if not self._is_cluster_locked(cluster_id):
            self._lock_cluster(cluster_id)

            free_resource = self.cluster_usage_map.get(cluster_id)

            cpu_remaining = free_resource["cpu_available"]
            memory_remaining = free_resource["memory_available"]

            deployments_to_deploy = []
            deployments_scheduled = self.deployment_cluster_map.get(cluster_id)
            if deployments_scheduled:
                deps_list = [] 

                prev_priority = deployments_scheduled[0]["priority"]
                for deployment in deployments_scheduled:
                    if deployment["status"] == DeploymentStatus.QUEUED.value:
                        if deployment["priority"] == prev_priority:
                            if len(deps_list) == 0:
                                deps_list.append([])
                            deps_list[deps_list[len(deps_list)-1]].append(deployment)
                        else:
                            prev_priority = deployment["priority"]
                            deps_list.append([])
                            deps_list[deps_list[len(deps_list)-1]].append(deployment)

                for deps in deps_list:
                    deployments_to_deploy, cpu_used, memory_used = self._get_deployments_to_deploy_from_same_priority(deps, cpu_remaining, memory_remaining)

                    cpu_remaining -= cpu_used
                    memory_remaining -= memory_used

            return deployments_to_deploy
        
        else:
            logger.error(f"Cluster is locked: {cluster_id}")
            raise HttpExceptionDetail(
                error_code="CLUSTER_LOCKED",
                message="Cluster is locked",
                status_code=400
            )
