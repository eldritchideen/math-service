from aws_cdk import core as cdk
import aws_cdk.aws_ecs as ecs
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk.aws_ecs_patterns import ApplicationLoadBalancedFargateService
import aws_cdk.aws_elasticloadbalancingv2 as alb
from aws_cdk.aws_apigatewayv2 import HttpApi, HttpMethod
from aws_cdk.aws_apigatewayv2_integrations import LambdaProxyIntegration
import aws_cdk.aws_lambda as lambda_


class MathServiceStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        image = DockerImageAsset(self, "Image", directory="src")

        math_task = ecs.FargateTaskDefinition(
            self,
            "MathTask",
            memory_limit_mib=1024,
            cpu=512,
        )
        math_task.add_container(
            "MathServiceContainer",
            image=ecs.ContainerImage.from_ecr_repository(
                image.repository, image.asset_hash
            ),
            memory_limit_mib=1024,
            cpu=512,
            port_mappings=[{"containerPort": 80}],
            entry_point=["uvicorn"],
            command=["main:app", "--host", "0.0.0.0", "--port", "80"],
        )

        service = ApplicationLoadBalancedFargateService(
            self,
            "MathService",
            cpu=512,
            memory_limit_mib=1024,
            task_definition=math_task,
            desired_count=1,
            protocol=alb.ApplicationProtocol.HTTP,
        )

        image.repository.grant_pull(
            service.task_definition.execution_role.grant_principal
        )

        handler = lambda_.DockerImageFunction(
            self,
            "MathServiceLambda",
            code=lambda_.DockerImageCode.from_ecr(
                repository=image.repository, tag=image.asset_hash
            ),
        )

        http_api = HttpApi(self, "MathAPI")
        http_api.add_routes(
            path="/math/add",
            methods=[HttpMethod.GET],
            integration=LambdaProxyIntegration(handler=handler),
        )
