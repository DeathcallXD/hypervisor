import pulumi
import pulumi_awsx as awsx
import pulumi_eks as eks
import pulumi_kubernetes as k8s

from pulumi_awsx import Provider as AwsProvider
from pulumi_kubernetes import Provider as K8sProvider, core

from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs
from pulumi_kubernetes.core.v1 import ContainerArgs, PodSpecArgs, PodTemplateSpecArgs, EnvFromSourceArgs, EnvVarArgs

from pulumi import automation as auto
from pulumi import get_stack, ResourceOptions, StackReference

from lib.logging_conf import set_logger

from src.domains.cluster.schemas import Resources

logger = set_logger(__name__)


PROJECT_NAME = "hypervisor"
"""
    All machines in a cluster, I am assuming to be t2.micro
    thus RAM in each is 1GB and CPU is 1 vCPU
"""

class PulumiUtils:
    def __init__(self):
        self.ws = auto.LocalWorkspace(project_settings=auto.ProjectSettings(name=PROJECT_NAME, runtime="python"))

    def is_stack_exists(self, organisation_id: str) -> bool:
        try:
            # List all stacks in the project
            all_stacks = self.ws.list_stacks()
            
            # Check if the specified stack exists in the list
            for stack in all_stacks:
                if stack.name == organisation_id:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking if stack exists: {e}")
            return False


    def get_stack_reference(self, organisation_id: str) -> StackReference:
        return StackReference(f"hypervisor/{organisation_id}")


    async def create_stack(self, organisation_id: str):
        if self.is_stack_exists(organisation_id):
            return StackReference(f"hypervisor/{organisation_id}")

        stack = await auto.create_or_select_stack(
            stack_name=f"{organisation_id}",
            program=lambda: {
                'vpc': awsx.ec2.Vpc(f'eks-vpc-{organisation_id}')
            },
            project_name="hypervisor"
        )

        await stack.workspace.install_plugin("aws", "v4.0.0")
        await stack.set_config(
            "aws:region", 
            auto.ConfigValue(value="ap-south-1")
        )
        await stack.up()

        return StackReference(f"hypervisor/{organisation_id}")

    async def create_cluster(self, organisation_id: str, cluster_id: str, resources: Resources):
        stack = await auto.create_or_select_stack(stack_name=organisation_id)

        infra = StackReference(f"hypervisor/{organisation_id}")
        eks_node_instance_type = 't2.micro'
        provider = AwsProvider("vpc", vars=infra.outputs)

        eks_vpc = awsx.ec2.Vpc(f"eks-vpc-{organisation_id}", provider=provider)


        cluster_size = max(resources.memory_allocated, resources.cpu_allocated) + 1 

        eks_cluster = eks.Cluster(
            f"eks-{organisation_id}-{cluster_id}",
            vpc_id=eks_vpc.vpc_id,
            public_subnet_ids=eks_vpc.public_subnet_ids,
            private_subnet_ids=eks_vpc.private_subnet_ids,
            instance_type=eks_node_instance_type,
            desired_capacity=cluster_size,
            min_size=cluster_size,
            max_size=cluster_size,
            node_associate_public_ip_address=False,
            endpoint_private_access=False,
            endpoint_public_access=True
        )
        
        await stack.up()
        return eks_cluster.kubeconfig

    async def create_deployment(self, organisation_id: str, cluster_id: str, deployment_id: str, resources: Resources, path_to_docker_image: str, name: str):
        stack = await auto.create_or_select_stack(stack_name=organisation_id)

        infra = StackReference(f"hypervisor/{organisation_id}")

        provider = K8sProvider("k8s", kubeconfig=infra.get_output("kubeConfig"))
        # service = core.v1.Service(f"eks-{organisation_id}-{cluster_id}", ResourceOptions(provider=provider))

        eks_cluster = eks.Cluster.get_kubeconfig("eks", f"eks-{organisation_id}-{cluster_id}", provider=provider)
        eks_cluster_provider = eks.Cluster.get_provider("k8s", kubeconfig=eks_cluster)

        deployment_namespace = k8s.core.v1.Namespace(
            f"deployment-{cluster_id}",
            pulumi.ResourceOptions(provider=eks_cluster_provider)
        )

        labels = {
            "app": f"deployment-{cluster_id}"
        }

        deployment = k8s.apps.v1.Deployment(
            f"deployment-{deployment_id}",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                namespace=deployment_namespace.metadata["name"],
            ),
            spec=DeploymentSpecArgs(
                selector=LabelSelectorArgs(match_labels=labels),
                replicas=1,
                template=PodTemplateSpecArgs(
                    metadata=ObjectMetaArgs(labels=labels),
                    spec=PodSpecArgs(
                        containers=[
                            ContainerArgs(
                                name=f"deployment-{deployment_id}", 
                                image=path_to_docker_image
                            )
                        ]
                    )
                )
            )
        )

        await stack.up()
        return deployment