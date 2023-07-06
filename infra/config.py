import pulumi
import pulumi_aws as aws

config = pulumi.Config()

# Project
env = config.require("env")
service_name = pulumi.get_project()
prefix = f"{env}-{service_name}"
domain_name = f"{service_name}.com"
region = "us-east-2"
PROD = "prod"
DEV = "dev"
origin_header_name = "X-Origin-Verify"
origin_header_value = config.require("origin-header")

# CloudFront is in us-east-1. So you must create certain resources in
# us-east-1 regardless of your default AWS region
us_east_1 = aws.Provider("us-east-1", region="us-east-1")

# UI
static_site_path = "../ui/build"
# TODO - ADD WAF with CORE RULES TO CLOUDFRONT DISTRO
