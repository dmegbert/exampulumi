import pulumi


config = pulumi.Config()

# Project
env = config.require("env")
service_name = pulumi.get_project()
prefix = f"{env}-{service_name}"
domain_name = f"{service_name}.com"
region = "us-east-2"
PROD = "prod"
DEV = "dev"

# UI
static_site_path = "../ui/build"
