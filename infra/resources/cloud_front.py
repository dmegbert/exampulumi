import pulumi_aws as aws

from config import env, prefix, domain_name, PROD
from resources.acm import cert
from resources.route_53 import hosted_zone
from resources.s3 import cf_log_bucket, static_bucket

alias = domain_name if env == PROD else f"{env}.{domain_name}"


def create_cloudfront_distribution(
    certificate: aws.acm.Certificate, bucket: aws.s3.Bucket
) -> aws.cloudfront.Distribution:
    s3_origin_id = f"{prefix}-s3-origin-id"
    origin_access_control = aws.cloudfront.OriginAccessControl(
        f"{prefix}-origin-access-control",
        description="S3 Bucket Policy",
        origin_access_control_origin_type="s3",
        signing_behavior="always",
        signing_protocol="sigv4",
    )

    return aws.cloudfront.Distribution(
        f"{prefix}-distribution",
        aliases=[alias],
        custom_error_responses=[
            aws.cloudfront.DistributionCustomErrorResponseArgs(
                error_code=404,
                response_code=200,
                error_caching_min_ttl=0,
                response_page_path="/index.html",
            ),
            aws.cloudfront.DistributionCustomErrorResponseArgs(
                error_code=403,
                response_code=200,
                error_caching_min_ttl=0,
                response_page_path="/index.html",
            ),
        ],
        default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
            allowed_methods=[
                "GET",
                "HEAD",
            ],
            cached_methods=[
                "GET",
                "HEAD",
            ],
            target_origin_id=s3_origin_id,
            forwarded_values=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
                query_string=False,
                cookies=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                    forward="none",
                ),
            ),
            viewer_protocol_policy="redirect-to-https",
            min_ttl=0,
            default_ttl=0,
            max_ttl=0,
        ),
        default_root_object="index.html",
        enabled=True,
        is_ipv6_enabled=True,
        logging_config=aws.cloudfront.DistributionLoggingConfigArgs(
            include_cookies=False,
            bucket=cf_log_bucket.bucket_domain_name,
        ),
        origins=[
            aws.cloudfront.DistributionOriginArgs(
                domain_name=bucket.bucket_domain_name,
                origin_id=s3_origin_id,
                origin_access_control_id=origin_access_control.id,
            )
        ],
        restrictions=aws.cloudfront.DistributionRestrictionsArgs(
            geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                restriction_type="none",
            ),
        ),
        viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
            acm_certificate_arn=certificate.arn,
            minimum_protocol_version="TLSv1.2_2021",
            ssl_support_method="sni-only",
        ),
    )


cf_distro = create_cloudfront_distribution(certificate=cert, bucket=static_bucket)


def create_dns_records(
    distribution: aws.cloudfront.Distribution,
) -> (aws.route53.Record, aws.route53.Record):
    alias_a_record = aws.route53.Record(
        f"{env}-a-record",
        name=alias,
        zone_id=hosted_zone.id,
        type="A",
        aliases=[
            aws.route53.RecordAliasArgs(
                name=distribution.domain_name,
                zone_id=distribution.hosted_zone_id,
                evaluate_target_health=True,
            )
        ],
    )

    alias_aaaa_record = aws.route53.Record(
        f"{env}-aaaa-record",
        name=alias,
        zone_id=hosted_zone.id,
        type="AAAA",
        aliases=[
            aws.route53.RecordAliasArgs(
                name=distribution.domain_name,
                zone_id=distribution.hosted_zone_id,
                evaluate_target_health=True,
            )
        ],
    )
    return alias_a_record, alias_aaaa_record


a_record, aaaa_record = create_dns_records(distribution=cf_distro)
