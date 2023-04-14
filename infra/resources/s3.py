import mimetypes
import os

from pulumi import FileAsset, ResourceOptions
import pulumi_aws as aws

from config import prefix, static_site_path

# Much of this file was taken from pulumi's static site example:
# https://github.com/pulumi/examples/tree/master/aws-py-static-website


def create_static_bucket() -> aws.s3.Bucket:
    bucket = aws.s3.Bucket(
        f"{prefix}-static-bucket",
        acl="private",
        bucket=f"{prefix}-static-bucket",
        lifecycle_rules=[
            aws.s3.BucketLifecycleRuleArgs(
                enabled=True,
                noncurrent_version_expiration=aws.s3.BucketLifecycleRuleNoncurrentVersionExpirationArgs(
                    days=7,
                ),
            )
        ],
        server_side_encryption_configuration=aws.s3.BucketServerSideEncryptionConfigurationArgs(
            rule=aws.s3.BucketServerSideEncryptionConfigurationRuleArgs(
                apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultArgs(
                    sse_algorithm="AES256",
                ),
                bucket_key_enabled=True,
            ),
        ),
        versioning=aws.s3.BucketVersioningArgs(
            enabled=True,
        ),
    )
    aws.s3.BucketOwnershipControls(
        f"{prefix}-static-bucket-ownership-controls",
        bucket=bucket.id,
        rule=aws.s3.BucketOwnershipControlsRuleArgs(
            object_ownership="ObjectWriter",
        ),
    )
    aws.s3.BucketPublicAccessBlock(
        f"{prefix}-static-bucket-public-access-block",
        bucket=bucket.id,
        block_public_acls=False,
        block_public_policy=False,
        ignore_public_acls=False,
        restrict_public_buckets=False,
    )
    return bucket


def create_cloudfront_log_bucket() -> aws.s3.BucketV2:
    current_user = aws.s3.get_canonical_user_id()
    log_delivery_user = aws.cloudfront.get_log_delivery_canonical_user_id()

    logs_bucket = aws.s3.BucketV2(
        f"{prefix}-cf-logs-bucket", bucket=f"{prefix}-cf-logs-bucket"
    )

    aws.s3.BucketOwnershipControls(
        f"{prefix}-cf-logs-bucket-ownership-controls",
        bucket=logs_bucket.id,
        rule=aws.s3.BucketOwnershipControlsRuleArgs(
            object_ownership="ObjectWriter",
        ),
    )
    aws.s3.BucketPublicAccessBlock(
        f"{prefix}-cf-logs-bucket-public-access-block",
        bucket=logs_bucket.id,
        block_public_acls=False,
        block_public_policy=False,
        ignore_public_acls=False,
        restrict_public_buckets=False,
    )
    aws.s3.BucketAclV2(
        f"{prefix}-cf-logs-bucket-acl-v2",
        bucket=logs_bucket.id,
        access_control_policy=aws.s3.BucketAclV2AccessControlPolicyArgs(
            grants=[
                aws.s3.BucketAclV2AccessControlPolicyGrantArgs(
                    grantee=aws.s3.BucketAclV2AccessControlPolicyGrantGranteeArgs(
                        id=current_user.id,
                        type="CanonicalUser",
                    ),
                    permission="FULL_CONTROL",
                ),
                aws.s3.BucketAclV2AccessControlPolicyGrantArgs(
                    grantee=aws.s3.BucketAclV2AccessControlPolicyGrantGranteeArgs(
                        id=log_delivery_user.id,
                        type="CanonicalUser",
                    ),
                    permission="FULL_CONTROL",
                ),
            ],
            owner=aws.s3.BucketAclV2AccessControlPolicyOwnerArgs(
                id=current_user.id,
            ),
        ),
    )
    return logs_bucket


static_bucket = create_static_bucket()
cf_log_bucket = create_cloudfront_log_bucket()


def get_web_contents_root_path() -> str:
    return os.path.join(os.getcwd(), static_site_path)


def crawl_static_dir(static_dir, converter_function, bucket) -> None:
    for file in os.listdir(static_dir):
        filepath = os.path.join(static_dir, file)

        if os.path.isdir(filepath):
            crawl_static_dir(filepath, converter_function, bucket)
        elif os.path.isfile(filepath):
            converter_function(filepath, bucket=bucket)


def bucket_object_converter(filepath, bucket) -> None:
    """
    Takes a file path and returns a bucket object managed by Pulumi
    """
    web_contents_root_path = get_web_contents_root_path()
    relative_path = filepath.replace(web_contents_root_path + "/", "")
    # Determine the mimetype using the `mimetypes` module.
    mime_type, _ = mimetypes.guess_type(filepath)
    aws.s3.BucketObject(
        relative_path,
        key=relative_path,
        acl="public-read",
        bucket=bucket.id,
        content_type=mime_type,
        source=FileAsset(filepath),
        opts=ResourceOptions(parent=bucket),
    )


static_web_contents_root_path = get_web_contents_root_path()
crawl_static_dir(static_web_contents_root_path, bucket_object_converter, static_bucket)
