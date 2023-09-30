# Securing Serverless - Protect Lambda Apps with an API Gateway and WAF via Pulumi IaC
*Keep unwanted traffic and bad actors far away from your applications using AWS Web Application Firewalls (WAFs).*
![Zombies storm a castle wall](https://cdn-images-1.medium.com/max/800/1*bLlQCma1HLZ-sH3-hhyu1w.jpeg)

Keep the baddies out! (Generated on https://stablediffusionweb.com)

Table of Contents
· Prerequisites
· What we are building
· What we are destroying
· Add an API Gateway
· Connect your API Gateway to your CloudFront Distribution
· Protect your API Gateway with a Regional WAF
· Conclusion

## Prerequisites
- An AWS account where you have full permissions
- A Pulumi account
- Basic to intermediate knowledge of AWS

## What we are building
- An API Gateway that will act as a conduit between CloudFront and your dockerized FastAPI app on AWS Lambda
- A Regional WAF to protect your API Gateway
- Updating your CloudFront distribution to connect to the API

## What we are destroying
That brief glimmer of hope that was sparked in your heart from last blog's mostly misleading and now completely false title that began ["Simplifying Serverless..."](https://medium.com/aws-in-plain-english/simplifying-serverless-deploy-a-docker-based-api-using-aws-lambda-function-urls-no-api-gateway-c18016591663)

Why are we destroying simplicity??? Simple is great. It is easy to understand, debug, and fix. You can fit the architecture diagram on one screen. Unfortunately, simple can also be insecure. The new AWS Lambda URL feature is really great and I hope AWS continues to improve it. However, for the Lambda URL to work with CloudFront, it needed to be configured as public with no auth and this presents security concerns.

While it is unlikely, it is possible that a bad actor could obtain your Lambda URL and invoke it for nefarious purposes. You can (and should) secure your application running in the Lambda via various auth methods. However, any bogus requests that generate 403 or 401 responses from your app still count as an execution. That means each one counts towards your lambda usage bill and is running a Lambda instance that could be serving legitimate users. It's just not worth the risk. So it's best to switch to a service that enables better security. So goodbye Lambda Function URL and hello my old friend, API Gateway.

![Deleted lambda function url code from GitHub](https://cdn-images-1.medium.com/max/800/1*J93JIY9pRQcw_lMZs-S4zQ.png)
*Remove the Lambda Function URL and thank it for it's service.*

## Add an API Gateway
Using an API Gateway in conjunction with an AWS Lambda has been the de facto standard pairing for serverless applications. Since this is a topic that has been thoroughly covered by other writers, I will focus on the details that are pertinent to ensuring that you choose the settings that enable your API Gateway to be secured by a WAF. There are a number of resources that are needed to fully configure the API Gateway. You can see the full file on the GitHub branch for this blog.](https://github.com/dmegbert/exampulumi/tree/3-secure-api-and-cdn-with-waf)

First up-add a RestAPI and ensure that you choose the endpoint configuration type of "REGIONAL." Only regional API Gateways can have WAFs. The default is EDGE and those do not have the capability of being behind a WAF.
```python
api_gw = aws.apigateway.RestApi(
    f"{prefix}-api-gateway",
    name=f"{prefix}-api-gateway",
    endpoint_configuration=aws.apigateway.RestApiEndpointConfigurationArgs(
        types="REGIONAL",
    ),
    opts=pulumi.ResourceOptions(depends_on=lambda_alias),
)
```

Next, you will add a `Resource` which is a specific route, an `Integration` which defines the relationship between the API Gateway and the Lambda Function, a `Method` which defines the HTTP verb(s) allowed for the resource and authorization, a `Deployment` which enables you to version your API Gateway should that be of interest to you down the line (I've never really used the feature, but it's still needed), and a `Stage` which is in the same category of usefulness as the `Deployment.`

I've set my API Gateway to have a single resource that uses a special wildcard resource of `{proxy+}` and HTTP Method of `ANY` that the REST diehards will recognize is not a verb much less an HTTP verb. But AWS doesn't care - it says toss the magic `{proxy+}` and `ANY` combo on an API Gateway endpoint, and it'll route EVERY http verb and request to that endpoint so your underlying backend running in your Lambda can handle the actual API routing you need.
![AWS console view of API Gateway stage showing a proxy resource and all the associated HTTP verbs.](https://cdn-images-1.medium.com/max/800/1*MaNVyuwabi-XEgMYKE4klA.png)
*All the HTTP Methods!*

Here's the code:
```python
# Much of this code was copied from Pulumi's example repo at: https://github.com/pulumi/examples/tree/master/aws-py-apigateway-lambda-serverless
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

    # This is weird right? Why is this POST?
    # Well, all Lambda Functions take events in as POST requests.
    # This is a really confusing AWS implementation detail that Pulumi will
    # hopefully just handle for us in a future release.
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
    # This is a comment from Pulumi's repo ^
    stage_name="",
    opts=pulumi.ResourceOptions(depends_on=api_gw_integration),
)

# Create a stage, which is an addressable instance of the Rest API. Set it to point at the latest deployment.
# This is also a comment from Pulumi's repo ^
api_gw_stage = aws.apigateway.Stage(
    f"{prefix}-api-gateway-stage",
    rest_api=api_gw.id,
    deployment=api_gw_deployment.id,
    stage_name=env,
)
```
The last piece of the API Gateway is the permission that enables the API Gateway to invoke the Lambda Function. My use of a {proxy+} endpoint slightly differed from the example code and as a result I spent the better part of an afternoon in permission hell. Until finally figuring out that I needed to add another slash and the proxy plus: `... + "*/*/{proxy+}"` to the end of the `source_arn` argument 🤯.

```python
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
```
Now run `pulumi up` and your API Gateway should spin up and be connected to your Lambda function. You can go to the API Gateway in the console and select your gateway, click stages, click on the stage name, and then you can copy / paste the invoke url into your browser and hit your app running in your lambda via the API Gateway. Remember to append `/api/items/1?q=hooray` if you're following along with my example app. I went to https://r7tpe319yi.execute-api.us-east-2.amazonaws.com/prod/api/items/1?q=cool to validate my setup.

![Screenshot of API Gateway showing how to find the Invoke URL.](https://cdn-images-1.medium.com/max/800/1*gc8V3OiuDOkhWBDAMnuDfw.png)

*Your API Gateway is alive and ready to receive requests from the internet*

## Connect your API Gateway to your CloudFront Distribution
We can now update our CloudFront distribution so that it continues acting as a reverse proxy and sends all /api/* requests to our API Gateway. This is essentially swapping out the Lambda Function URL for the API Gateway. To view all the changes needed pull up the full diff on GitHub. Here's two things to take note of when updating the origins section, the domain_name and `origin_path`:
```python
origins=[
      aws.cloudfront.DistributionOriginArgs(
          domain_name=bucket.bucket_domain_name,
          origin_id=s3_origin_id,
          origin_access_control_id=origin_access_control.id,
      ),
      aws.cloudfront.DistributionOriginArgs(
          # The end of the invoke url contains the stage name. I am naming
          # the stages after the environment so strip that from the url
          # to get the domain name. Needs to be "domain.com" -- no https or slashes
          domain_name=api_gateway_stage.invoke_url.apply(
              lambda url: url.replace("https://", "").replace(f"/{env}", "")
          ),
          origin_id=api_gateway_origin_id,
          # The origin path is a new argument to make the integration
          # work with the API Gateway. Since the invoke url has the stage
          # name, we are going to add that stage name to our requests. This
          # will allow the requests to flow through the API Gateway to the Lambda
          # and we do not need to update the routing of the Fast API app.
          origin_path=f"/{env}",
          custom_origin_config=aws.cloudfront.DistributionOriginCustomOriginConfigArgs(
              http_port=80,
              https_port=443,
              origin_protocol_policy="https-only",
              origin_ssl_protocols=["TLSv1.2"],
          ),
      ),
  ],
```
Run `pulumi up` and then validate that your api is available through your friendly url:

## Protect your API Gateway with a Regional WAF
So now we are essentially at the same place as we were in the prior blog in terms of security. Just like with the Lambda Function URL, the API Gateway's Invoke URL is exposed to the internet and could be abused. So now we'll add a WAF so that only traffic from your CloudFront Distribution is able to reach your API Gateway. While WAFs can become incredibly complex, they're fundamentally a filter that blocks requests that do not pass its set of rules. So to block all requests that do not originate from our CloudFront Distribution, we are going to have our distro add a custom header to each request and then the WAF will inspect all requests and only allow those with the header to pass through.

The header's name and value do not really matter. The value just needs to be a secret that only CloudFront and API Gateway "know." So the header value should be treated in a similar fashion as other sensitive values like API keys, database passwords, etc. Ideally, you'd use something like AWS Secrets Manager to automate the rotation of the value. For now, we'll leave that for another day and use Pulumi's CLI `config --secret` as a way to encrypt the header value and make it easily available to our CloudFront distribution and API Gateway.

I like to just use python's uuid to get arbitrary and complex values:
```shell
➜  ~ python
>>> import uuid
>>> str(uuid.uuid4()).replace("-", "")
'd44deafc0df242ef8b318a38f37f9a7c'
```
And then add that to your pulumi.yml config file via: `pulumi config set origin-header d44deafc0df242ef8b318a38f37f9a7c --secret` Make sure you add the secret flag at the end so that the value is encrypted. Go to your .yml file and confirm it was saved:
```yaml
config:
  aws:region: us-east-2
  exampulumi:env: prod
  exampulumi:origin-header:
    secure: AAABAAGTxfly+nVfVejz6VD9tuekpWkOc6+OFe6vdr5j+wo1e33L+322v/IHGKFvVNWPg024DtbdHezw5wuBQg==
```
Open up your `config.py` file and add a header name and then set the header value to the encrypted string you just created in the prior step.
```python
# config.py
<...things>

origin_header_name = "X-Origin-Verify"
origin_header_value = config.require("origin-header")
```
Update your CloudFront distribution to pass this header along to all `/api/*` requests. This will be a new argument in the `origins` block:
```python
# Imports
from config import (
    env,
    prefix,
    domain_name,
    # Add these from config.py
    origin_header_value,
    origin_header_name,
)

origins=[
  aws.cloudfront.DistributionOriginArgs(
      domain_name=bucket.bucket_domain_name,
      origin_id=s3_origin_id,
      origin_access_control_id=origin_access_control.id,
  ),
  aws.cloudfront.DistributionOriginArgs(
      domain_name=api_gateway_stage.invoke_url.apply(
          lambda url: url.replace("https://", "").replace(f"/{env}", "")
      ),
      origin_id=api_gateway_origin_id,
      origin_path=f"/{env}",
      custom_origin_config=aws.cloudfront.DistributionOriginCustomOriginConfigArgs(
          http_port=80,
          https_port=443,
          origin_protocol_policy="https-only",
          origin_ssl_protocols=["TLSv1.2"],
      ),
      # Here is where you add the header name and value.
      custom_headers=[
          aws.cloudfront.DistributionOriginCustomHeaderArgs(
              name=origin_header_name,
              value=origin_header_value,
          )
      ],
  ),
],
```
Now that we have a secret header value being added to all our requests that flow through our CloudFront distribution, we will use a WAF to block all requests that do not contain it.
```python
import pulumi_aws as aws

from config import prefix, env, origin_header_name, origin_header_value
from resources.api_gateway import api_gw_stage

# Create a regex pattern set that uses the origin_header_value
regex_pattern_set = aws.wafregional.RegexPatternSet(
    f"{prefix}-regex-pattern-set", regex_pattern_strings=[origin_header_value]
)

# Create a regex match that instructs the WAF to evaluate the `X-Origin-Verify`
# header matches the pattern
regex_match_set = aws.wafregional.RegexMatchSet(
    f"{prefix}-regex-match-set",
    regex_match_tuples=[
        aws.wafregional.RegexMatchSetRegexMatchTupleArgs(
            field_to_match=aws.wafregional.RegexMatchSetRegexMatchTupleFieldToMatchArgs(
                data=origin_header_name,
                type="HEADER",
            ),
            regex_pattern_set_id=regex_pattern_set.id,
            text_transformation="NONE",
        )
    ],
)

# Add the regex match set as a rule
waf_rule = aws.wafregional.Rule(
    f"{prefix}-cf-waf-rule",
    metric_name=f"{env}WafMetric",
    predicates=[
        aws.wafregional.RulePredicateArgs(
            type="RegexMatch",
            data_id=regex_match_set.id,
            negated=False,
        ),
    ],
)

# Create an acl (a collection of rules) and add the Header rule to it.
# The default action is to block traffic
# Then it only allows traffic that passes the rule created above.
web_acl = aws.wafregional.WebAcl(
    f"{prefix}-web-acl",
    metric_name="apiGwMetricName",
    default_action=aws.wafregional.WebAclDefaultActionArgs(type="BLOCK"),
    rules=[
        aws.wafregional.WebAclRuleArgs(
            type="REGULAR",
            priority=1,
            rule_id=waf_rule.id,
            action=aws.wafregional.WebAclRuleActionArgs(
                type="ALLOW",
            ),
        ),
    ],
)

# Connect this WAF with the API Gateway.
web_acl_association = aws.wafregional.WebAclAssociation(
    f"{prefix}-web-acl-association",
    resource_arn=api_gw_stage.arn,
    web_acl_id=web_acl.id,
)
```
Run `pulumi up` and now when you try to directly access your api via your API Gateway's invoke url, you should receive a 403 forbidden error.

![Forbidden Error](https://cdn-images-1.medium.com/max/800/1*yrBonb1Xpz0dPnGKhO8rxw.png)

But, you should be able to get to it via the friendly URL that is routed through the CloudFront distribution.

![API Response](https://cdn-images-1.medium.com/max/800/1*CQdMB5zqJUp8ZOZv7oMBEA.png)

## Conclusion
Now you have secured your Lambda application by placing it behind an API Gateway and then securing the API Gateway with a firewall - AWS WAF. You can rest a bit easier now. In the next article, we will further secure our application by adding a version 2 WAF to our CloudFront distribution (AWS's CDN service).
