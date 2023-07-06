import platform

import pulumi_aws as aws

from config import env, prefix
from resources.ecr import image
from resources.iam import lambda_role


def get_arch():
    cpu_arch = platform.processor()
    if cpu_arch == "arm":
        return ["arm64"]
    return ["x86_64"]


fastapi_lambda = aws.lambda_.Function(
    f"{prefix}-lambda",
    name=f"{prefix}-lambda",
    architectures=get_arch(),
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            "FUNCTION_NAME": f"{prefix}-lambda",
            "ENV_NAME": env,
        }
    ),
    image_uri=image.image_uri,
    memory_size=256,
    package_type="Image",
    publish=True,
    role=lambda_role.arn,
    timeout=600,
)

lambda_alias = aws.lambda_.Alias(
    f"{prefix}-lambda-alias",
    name=f"{prefix}-lambda-alias",
    description="Alias for fastapi lambda",
    function_name=fastapi_lambda.name,
    function_version=fastapi_lambda.version,
)
