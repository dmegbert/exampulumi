import pulumi_awsx as awsx
from config import prefix

repository = awsx.ecr.Repository(f"{prefix}-repo")

image = awsx.ecr.Image(
    f"{prefix}-fast-api-lambda-image",
    repository_url=repository.url,
    path="../backend",
    extra_options=["--quiet"],
)
