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
from resources.waf_v2 import aws_managed_rules_acl

alias = domain_name if env == PROD else f"{env}.{domain_name}"


def create_cloudfront_distribution(
    certificate: aws.acm.Certificate,
    bucket: aws.s3.Bucket,
    api_gateway_stage: aws.apigateway.Stage,
) -> aws.cloudfront.Distribution:
    s3_origin_id = f"{prefix}-s3-origin-id"
    origin_access_control = aws.cloudfront.OriginAccessControl(
        f"{prefix}-origin-access-control",
        description="S3 Bucket Policy",
        origin_access_control_origin_type="s3",
        signing_behavior="always",
        signing_protocol="sigv4",
    )
    api_gateway_origin_id = f"{prefix}-fastapi_gateway-origin-id"
    api_gateway_cache_policy = aws.cloudfront.get_cache_policy(
        name="Managed-CachingDisabled"
    )
    api_gateway_origin_request_policy = aws.cloudfront.get_origin_request_policy(
        name="Managed-AllViewerExceptHostHeader"
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
        ordered_cache_behaviors=[
            aws.cloudfront.DistributionOrderedCacheBehaviorArgs(
                path_pattern="api/*",
                target_origin_id=api_gateway_origin_id,
                viewer_protocol_policy="redirect-to-https",
                cached_methods=["GET", "HEAD"],
                allowed_methods=[
                    "GET",
                    "HEAD",
                    "OPTIONS",
                    "PUT",
                    "POST",
                    "PATCH",
                    "DELETE",
                ],
                cache_policy_id=api_gateway_cache_policy.id,
                origin_request_policy_id=api_gateway_origin_request_policy.id,
            )
        ],
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
                custom_headers=[
                    aws.cloudfront.DistributionOriginCustomHeaderArgs(
                        name=origin_header_name,
                        value=origin_header_value,
                    )
                ],
            ),
        ],
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
        viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
            acm_certificate_arn=certificate.arn,
            minimum_protocol_version="TLSv1",
            ssl_support_method="sni-only",
        ),
        # To specify a web ACL created using the latest version of AWS WAF (WAFv2), use the ACL ARN - REALLY?!?!
        web_acl_id=aws_managed_rules_acl.arn,
    )


cf_distro = create_cloudfront_distribution(
    certificate=cert, bucket=static_bucket, api_gateway_stage=api_gw_stage
)


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
