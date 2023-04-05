import pulumi
import pulumi_aws as aws

from config import domain_name, env, prefix, PROD
from resources.route_53 import hosted_zone

# CloudFront is in us-east-1. So you must create the certificate in
# us-east-1 regardless of your default AWS region
us_east_1 = aws.Provider("us-east-1", region="us-east-1")


def create_certificate(hosted_zone_id: str) -> aws.acm.Certificate:
    cert_domain_name = domain_name if env == PROD else f"{env}.{domain_name}"
    certificate = aws.acm.Certificate(
        f"{prefix}-certificate",
        domain_name=cert_domain_name,
        validation_method="DNS",
        validation_options=[
            aws.acm.CertificateValidationOptionArgs(
                domain_name=cert_domain_name, validation_domain="exampulumi.com"
            ),
        ],
        # Must be in us-east-1 to be used by cloudfront
        opts=pulumi.ResourceOptions(provider=us_east_1),
    )
    cert_validation_cname = aws.route53.Record(
        f"{prefix}-cert-validation-cname",
        name=certificate.domain_validation_options[0].resource_record_name,
        records=[certificate.domain_validation_options[0].resource_record_value],
        ttl=60,
        type=certificate.domain_validation_options[0].resource_record_type,
        zone_id=hosted_zone_id,
    )
    aws.acm.CertificateValidation(
        f"{prefix}-cert-validation",
        certificate_arn=certificate.arn,
        validation_record_fqdns=[cert_validation_cname.fqdn],
        opts=pulumi.ResourceOptions(provider=us_east_1),
    )
    return certificate


cert = create_certificate(hosted_zone.id)
