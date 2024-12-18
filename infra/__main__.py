import pulumi

from config import service_name
from resources.ecr import image
from resources.rds import db
from resources.route_53 import hosted_zone
from resources.acm import cert
from resources.api_gateway import api_gw_deployment
from resources.aws_lambda import fastapi_lambda
from resources.s3 import cf_log_bucket, static_bucket
from resources.cloud_front import cf_distro, a_record, aaaa_record
from resources.vpc import default_vpc, private_vpc, db_security_group

# from resources.waf import web_acl, web_acl_association
# from resources.waf_v2 import aws_managed_rules_acl

# Add your exports here
pulumi.export("service name", service_name)
pulumi.export("hosted_zone_id", hosted_zone.id)
pulumi.export("certificate", cert.arn)
pulumi.export("static_bucket_arn", static_bucket.arn)
pulumi.export("cf_log_bucket_arn", cf_log_bucket.arn)
pulumi.export("cloudfront_distro_id", cf_distro.id)
pulumi.export("a_record", a_record.name)
pulumi.export("aaaa_record", aaaa_record.name)
pulumi.export("image_uri", image.image_uri)
pulumi.export("lambda_function_name", fastapi_lambda.name)
pulumi.export("api_gw_deployment_execution_arn", api_gw_deployment.execution_arn)
pulumi.export("vpc_id", default_vpc.vpc_id)
pulumi.export("vpc_id", private_vpc.vpc_id)
pulumi.export("public_subnet_ids", private_vpc.public_subnet_ids)
pulumi.export("private_subnet_ids", private_vpc.private_subnet_ids)
pulumi.export("db_security_group_id", db_security_group.id)
pulumi.export(
    "rds_instance_endpoint",
    db.endpoint.apply(lambda endpoint: endpoint.replace(":5432", "")),
)
# pulumi.export("web_acl_rules", web_acl.rules)
# pulumi.export("web_acl_association", web_acl_association.id)
# pulumi.export("waf_v2", aws_managed_rules_acl.rules)
