# Protect Your Apps with AWS Managed Rules for WAF v2 via Pulumi IaC

**Leverage AWS Managed Rule Groups to enact a comprehensive suite of first-layer defenses to address many of the OWASP Top Ten threats.**

![AWS WAF diagram](https://miro.medium.com/v2/resize:fit:720/format:webp/1*Bl5ipNcQww5ARqZsg6KlfA.png)

## Table of Contents
Prerequisites
Cost Warning
What we are building
Other Service Options
Create a WAF v2
AWS Managed Rules
Connect the WAF v2 to the CloudFront distribution
Block traffic by geography
Conclusion

## Prerequisites
- An AWS account where you have full permissions
- A Pulumi account
- Basic to intermediate knowledge of AWS

## Cost Warning
A WAF v2 with the Managed Rules does cost ~$25/mo — be sure to check your billing and destroy the WAF v2 if you do not wish to incur those costs.

## What we are building
- A WAF v2 configured with AWS Managed Rule Groups
- Attaching the WAF v2 to our existing CloudFront distribution
- Updating CloudFront to block traffic from certain countries

## Other Service Options
A WAF v2 with Managed Rules can be used in conjunction with a number of AWS services. CloudFront is only one option and will be the example used in the rest of this article. However, you could connect the same WAF v2 to any of the following services. Check the [WAF v2 AWS developer guide](https://docs.aws.amazon.com/waf/latest/APIReference/Welcome.html) to verify as new services may be added.

- CloudFront distribution
- API Gateway REST API
- Application Load Balancer
- AWS AppSync GraphQL API
- Amazon Cognito user pool
- AWS App Runner service
- AWS Verified Access instance

## Create a WAF v2
In AWS you will see the newer WAF called WAF v2 or simply WAF. And the older WAF will be called WAF Classic. As with so many things AWS, it can be confusing. In your `infra/resources` directory, create a new file named `waf_v2.py` and add the following to it:
```python
import pulumi
import pulumi_aws as aws

from config import prefix, us_east_1

aws_managed_rules_acl = aws.wafv2.WebAcl(
    f"{prefix}-aws-managed-rules-acl",
    opts=pulumi.ResourceOptions(provider=us_east_1),
    default_action=aws.wafv2.WebAclDefaultActionArgs(
        allow=aws.wafv2.WebAclDefaultActionAllowArgs(),
    ),
    description="AWS Managed Rules ACL",
    name=f"{prefix}-aws-managed-rules-acl",
    scope="CLOUDFRONT",
    visibility_config=aws.wafv2.WebAclVisibilityConfigArgs(
        cloudwatch_metrics_enabled=True,
        metric_name=f"{prefix}-aws-managed-rules-acl-metric",
        sampled_requests_enabled=True,
    ),
)
```

## AWS Managed Rules
At times, using AWS feels like a burden and unnecessarily complex. But then I encounter a feature like AWS Managed Rules. For example, one group of rules is the `IpReputationList`. Who wants to keep track of an ever-evolving list of ip addresses used by hackers and scammers? Not me. I’m more than happy to let AWS keep that list up-to-date for me, so I can focus of shipping new features for our customers.

To add AWS Managed Rules to our WAF v2, we update the above resource with a list of rules. To view the managed rules available go to the [AWS developer guide](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-list.html) for the full list of rules available. You might need others than the ones I have selected below. Also, the following article maps the [OWASP Top Ten to the AWS Managed Rules](https://globaldatanet.com/tech-blog/owasp-top-10-mapped-to-aws-managed-rules) so you can see the remaining gaps in security after adding these rules.

```python
aws_managed_rules_acl = aws.wafv2.WebAcl(
    # stuff from above...
    rules=[
        aws.wafv2.WebAclRuleArgs(
            name="AWS-AWSManagedRulesSQLiRuleSet",
            priority=3,
            override_action=aws.wafv2.WebAclRuleOverrideActionArgs(
                count=aws.wafv2.WebAclRuleOverrideActionCountArgs(),
            ),
            statement=aws.wafv2.WebAclRuleStatementArgs(
                managed_rule_group_statement=aws.wafv2.WebAclRuleStatementManagedRuleGroupStatementArgs(
                    name="AWSManagedRulesSQLiRuleSet",
                    vendor_name="AWS",
                ),
            ),
            visibility_config=aws.wafv2.WebAclRuleVisibilityConfigArgs(
                cloudwatch_metrics_enabled=True,
                metric_name="AWS-AWSManagedRulesSQLiRuleSet",
                sampled_requests_enabled=True,
            ),
        ),
        aws.wafv2.WebAclRuleArgs(
            name="AWS-AWSManagedRulesKnownBadInputsRuleSet",
            priority=2,
            override_action=aws.wafv2.WebAclRuleOverrideActionArgs(
                count=aws.wafv2.WebAclRuleOverrideActionCountArgs(),
            ),
            statement=aws.wafv2.WebAclRuleStatementArgs(
                managed_rule_group_statement=aws.wafv2.WebAclRuleStatementManagedRuleGroupStatementArgs(
                    name="AWSManagedRulesKnownBadInputsRuleSet",
                    vendor_name="AWS",
                ),
            ),
            visibility_config=aws.wafv2.WebAclRuleVisibilityConfigArgs(
                cloudwatch_metrics_enabled=True,
                metric_name="AWS-AWSManagedRulesKnownBadInputsRuleSet",
                sampled_requests_enabled=True,
            ),
        ),
        aws.wafv2.WebAclRuleArgs(
            name="AWS-AWSManagedRulesCommonRuleSet",
            priority=1,
            override_action=aws.wafv2.WebAclRuleOverrideActionArgs(
                count=aws.wafv2.WebAclRuleOverrideActionCountArgs(),
            ),
            statement=aws.wafv2.WebAclRuleStatementArgs(
                managed_rule_group_statement=aws.wafv2.WebAclRuleStatementManagedRuleGroupStatementArgs(
                    name="AWSManagedRulesCommonRuleSet",
                    vendor_name="AWS",
                ),
            ),
            visibility_config=aws.wafv2.WebAclRuleVisibilityConfigArgs(
                cloudwatch_metrics_enabled=True,
                metric_name="AWS-AWSManagedRulesCommonRuleSet",
                sampled_requests_enabled=True,
            ),
        ),
        aws.wafv2.WebAclRuleArgs(
            name="AWS-AWSManagedRulesAmazonIpReputationList",
            priority=0,
            override_action=aws.wafv2.WebAclRuleOverrideActionArgs(
                count=aws.wafv2.WebAclRuleOverrideActionCountArgs(),
            ),
            statement=aws.wafv2.WebAclRuleStatementArgs(
                managed_rule_group_statement=aws.wafv2.WebAclRuleStatementManagedRuleGroupStatementArgs(
                    name="AWSManagedRulesAmazonIpReputationList",
                    vendor_name="AWS",
                ),
            ),
            visibility_config=aws.wafv2.WebAclRuleVisibilityConfigArgs(
                cloudwatch_metrics_enabled=True,
                metric_name="AWS-AWSManagedRulesAmazonIpReputationList",
                sampled_requests_enabled=True,
            ),
        ),
    ],
)
```
Add the WAF v2 resource to your `__main__.py` file:

```python
import pulumi

from config import service_name
from resources.ecr import image
# ... more imports
# NEW!
from resources.waf_v2 import aws_managed_rules_acl 

# Add your exports here
pulumi.export("service name", service_name)
pulumi.export("hosted_zone_id", hosted_zone.id)
# Other exports...
# NEW!
pulumi.export("waf_v2", aws_managed_rules_acl.rules)
```
## Connect the WAF v2 to the CloudFront distribution
Within the existing `cloud_front.py` resource file we make a couple additions to enable all incoming requests to flow through our new WAF v2 firewall prior to hitting our distribution.

```python
import pulumi_aws as aws

from config import (
    env,
    prefix,
    domain_name,
    PROD,
    origin_header_value,
    origin_header_name,
)
from resources.acm import cert
from resources.api_gateway import api_gw_stage
from resources.route_53 import hosted_zone
from resources.s3 import cf_log_bucket, static_bucket
from resources.waf_v2 import aws_managed_rules_acl # Import the acl here

alias = domain_name if env == PROD else f"{env}.{domain_name}"


def create_cloudfront_distribution(
    certificate: aws.acm.Certificate,
    bucket: aws.s3.Bucket,
    api_gateway_stage: aws.apigateway.Stage,
) -> aws.cloudfront.Distribution:
    return aws.cloudfront.Distribution(...
    ########################################################
    # Lots of code (see github repo or earlier articles)   #
    ########################################################
    ...    
        # To specify a web ACL created using the latest version of AWS WAF (WAFv2), use the ACL ARN
        web_acl_id=aws_managed_rules_acl.arn,
    )
```
A strange thing to note is that the argument name in the `aws.cloudfront.Distribution` resource is `web_acl_id`. However, you need to specify the `arn` of the WAF v2 acl for it to work. Not the id.

## Block traffic by geography
Another common security, compliance, or business requirement is to block traffic from reaching your application based on geography. For instance, U.S. based companies are forbidden from doing business within a [handful of countries where sanctions are in place.](https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/sanctioned-destinations) You can block access via country of request origin by updating your CloudFront distribution. So still within the same code block where we added the WAF v2, you can do the following:

```python
def create_cloudfront_distribution(
    certificate: aws.acm.Certificate,
    bucket: aws.s3.Bucket,
    api_gateway_stage: aws.apigateway.Stage,
) -> aws.cloudfront.Distribution:
    return aws.cloudfront.Distribution(...
    ########################################################
    # Lots of code (see github repo or earlier articles)   #
    ########################################################
    ...    
        # To specify a web ACL created using the latest version of AWS WAF (WAFv2), use the ACL ARN
        web_acl_id=aws_managed_rules_acl.arn,
        restrictions=aws.cloudfront.DistributionRestrictionsArgs(
            geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                restriction_type="blacklist",
                locations=[
                    # https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/sanctioned-destinations
                    "CU",
                    "IR",
                    "KP",
                    "SY",
                    "RU",
                ],
            ),
        ),
    )
```
Run `pulumi preview` and verify that everything looks okay. Do not worry about the deprecation warnings. We are not using `excluded_rules` so not sure why that is popping up. Maybe it’s used behind-the-scenes by the Managed Rule groups.

```shell
(venv) ➜  infra git:(3-secure-api-and-cdn-with-waf) ✗ pulumi preview
Previewing update (prod)

View in Browser (Ctrl+O): https://app.pulumi.com/****/exampulumi/prod/previews/1b6***

     Type                            Name                                   Plan       Info
     pulumi:pulumi:Stack             exampulumi-prod                                   4 warnings
 +   ├─ aws:wafv2:WebAcl             prod-exampulumi-aws-managed-rules-acl  create
     ├─ awsx:ecr:Image               prod-exampulumi-fast-api-lambda-image
 ~   └─ aws:cloudfront:Distribution  prod-exampulumi-distribution           update     [diff: ~webAclId]


Diagnostics:
  pulumi:pulumi:Stack (exampulumi-prod):
    warning: excluded_rules is deprecated: Use rule_action_override instead
    warning: excluded_rules is deprecated: Use rule_action_override instead
    warning: excluded_rules is deprecated: Use rule_action_override instead
    warning: excluded_rules is deprecated: Use rule_action_override instead

Outputs:
  + waf_v2                         : [
  +     [0]: {
          + name             : "AWS-AWSManagedRulesSQLiRuleSet"
          + override_action  : {}
          + priority         : 3
          + rule_labels      : []
          + statement        : {
              + managed_rule_group_statement: {
                  + excluded_rules            : []
                  + managed_rule_group_configs: []
                  + name                      : "AWSManagedRulesSQLiRuleSet"
                  + rule_action_overrides     : []
                  + vendor_name               : "AWS"
                  + version                   : ""
                }
            }
...
Resources:
    + 1 to create
    ~ 1 to update
    2 changes. 44 unchanged
```
Then run `pulumi up` to make your app a whole lot safer. As with any other CloudFront update, the deployment can take a few minutes to complete.
```python
(venv) ➜  infra git:(3-secure-api-and-cdn-with-waf) ✗ pulumi up --skip-preview
Updating (prod)

View in Browser (Ctrl+O): https://app.pulumi.com/***/exampulumi/prod/updates/91

     Type                            Name                                   Status             Info
     pulumi:pulumi:Stack             exampulumi-prod                        running...         warning: excluded_rules is depre
 +   ├─ aws:wafv2:WebAcl             prod-exampulumi-aws-managed-rules-acl  created (1s)
     ├─ awsx:ecr:Image               prod-exampulumi-fast-api-lambda-image                     Image push succeeded.
 ~   └─ aws:cloudfront:Distribution  prod-exampulumi-distribution           updating (24s)...  [diff: ~webAclId]

Resources:
    + 1 created
    ~ 1 updated
    2 changes. 44 unchanged

Duration: 3m48s
```
## Conclusion
Now you have a more secure CloudFront distribution. Since that is the point of entry to your application, your entire stack is also more secure. You must still enact other security measures such as authentication, authorization, encryption, and isolation of data stores from the internet. But this is a great addition and the peace of mind.