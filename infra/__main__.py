import pulumi

from config import service_name
from resources.ecr import image
from resources.route_53 import hosted_zone
from resources.acm import cert
from resources.aws_lambda import (
    fastapi_lambda,
    fastapi_lambda_url,
)
from resources.s3 import cf_log_bucket, static_bucket
from resources.cloud_front import cf_distro, a_record, aaaa_record

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
pulumi.export("function_url", fastapi_lambda_url.function_url)
