import pulumi_awsx as awsx
from config import prefix

repository = awsx.ecr.Repository(f"{prefix}-lambda-repo", name=f"{prefix}-lambda-repo")

image = awsx.ecr.Image(
    f"{prefix}-fast-api-lambda-image",
    repository_url=repository.url,
    path="../backend",
    extra_options=["--quiet"],
)
