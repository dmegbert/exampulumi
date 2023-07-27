import pulumi
import pulumi_aws as aws

from config import env, prefix
from resources.aws_lambda import fastapi_lambda, lambda_alias


# https://github.com/pulumi/examples/tree/master/aws-py-apigateway-lambda-serverless
api_gw = aws.apigateway.RestApi(
    f"{prefix}-api-gateway",
    name=f"{prefix}-api-gateway",
    endpoint_configuration=aws.apigateway.RestApiEndpointConfigurationArgs(
        types="REGIONAL",
    ),
    opts=pulumi.ResourceOptions(depends_on=lambda_alias),
)

api_gw_resource = aws.apigateway.Resource(
    f"{prefix}-api-gateway-resource",
    rest_api=api_gw.id,
    parent_id=api_gw.root_resource_id,
    path_part="{proxy+}",
)

api_gw_integration = aws.apigateway.Integration(
    f"{prefix}-api-gateway-integration",
    rest_api=api_gw.id,
    resource_id=api_gw_resource.id,
    http_method="ANY",
    integration_http_method="POST",
    type="AWS_PROXY",
    uri=lambda_alias.invoke_arn,
)

# method
api_gw_method = aws.apigateway.Method(
    f"{prefix}-api-gateway-method",
    rest_api=api_gw.id,
    resource_id=api_gw_resource.id,
    http_method="ANY",
    authorization="NONE",
)


# Create a deployment of the Rest API.
api_gw_deployment = aws.apigateway.Deployment(
    f"{prefix}-api-gateway-deployment",
    rest_api=api_gw.id,
    # Note: Set to empty to avoid creating an implicit stage, we'll create it
    # explicitly below instead.
    stage_name="",
    opts=pulumi.ResourceOptions(depends_on=api_gw_integration),
)

# Create a stage, which is an addressable instance of the Rest API. Set it to point at the latest deployment.
api_gw_stage = aws.apigateway.Stage(
    f"{prefix}-api-gateway-stage",
    rest_api=api_gw.id,
    deployment=api_gw_deployment.id,
    stage_name=env,
)

# Give API Gateway permissions to invoke the Lambda
lambda_permission = aws.lambda_.Permission(
    f"{prefix}-lambda-permission-for-api-gw",
    action="lambda:invokeFunction",
    principal="apigateway.amazonaws.com",
    function=fastapi_lambda.name,
    qualifier=lambda_alias.name,
    # This ruined most of a day - https://github.com/pulumi/examples/blob/master/aws-py-apigateway-lambda-serverless/__main__.py#L125
    source_arn=api_gw_deployment.execution_arn.apply(lambda arn: arn + "*/*/{proxy+}"),
)
