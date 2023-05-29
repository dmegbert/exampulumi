# Simplifying Serverless-Deploy a Docker Based API using AWS  Lambda Function URLs. No API Gateway!
![Photo by Josh Felise on Unsplash](https://raw.githubusercontent.com/dmegbert/exampulumi/main/blog/img/shipPortal.jpg "Ship Portal")

_Learn how to launch an API in AWS using a Lambda Function URL and enable a custom domain name via CloudFront._

## Full Stack Application Deployment Series
This is the second in a series of articles that details how to set up a production-grade, full stack web application in AWS using Pulumi for our Infrastructure as Code (IaC) needs. The first article contains code and set up instructions that we will build on in this post.
1. Deploying a Production Grade Static Site on AWS using Route53, CloudFront, and S3 with Pulumi Infrastructure as Code (IaC)
2. This article
3. TBD--Maybe Adding a database
4. TBD--Maybe Adding CI/CD tool
5. TBD--Maybe Adding an Auth as a Service Provider

## Table of Contents
- [Prerequisites](#prerequisites)
- [What we are building](#what-we-are-building)
- [Code and Site](#code-and-site)
- [Project Directory Structure](#project-directory-structure)
- [Docker Image Creation and Uploading to AWS ECR](#docker-image-creation-and-uploading-to-aws-ecr)
- [AWS Lambda Configuration](#aws-lambda-configuration)
- [Update CloudFront with Reverse Proxy Capabilities](#update-cloudfront-with-reverse-proxy-capabilities)
- [API Routing Updates](#api-routing-updates)
- [Static Site Hitting API and FastAPI Docs](#static-site-hitting-api-and-fastapi-docs)
- [Caveats](#caveats)
- [Conclusion](#conclusion)

## Prerequisites
- An AWS account where you have full permissions
- A Pulumi account
- Basic to intermediate knowledge of AWS
- Basic to intermediate understanding of Docker
- Basic API knowledge--we will deploy a Python API using the FastAPI framework. Any containerized web application should work.

## What we are building
- A simple, containerized api using Python and FastAPI
- An AWS ECR (Elastic Container Registry) repository to store the image used by the Lambda function
- An AWS Lambda function using a docker image
- An IAM role to enable the Lambda function to create logs.
- An update to the basic React app built in the prior article so that it calls our API
- An updated CloudFront distribution that extends the functionality of the one we built in the prior article

## Code and Site
The code that accompanies this blog can be found on GitHub: https://github.com/dmegbert/exampulumi
The site is live and can be found at: https://exampulumi.com/ It is a very minimal site.

## Project Directory Structure
The main change to the structure in this article is the addition of the backend directory. This holds all the code for the API as well as the `Dockerfile` that will build the docker image to be hosted in ECR and used by AWS Lambda. Copy or recreate that directory from my [Github repo](https://medium.com/r/?url=https%3A%2F%2Fgithub.com%2Fdmegbert%2Fexampulumi%2Ftree%2F2-api-lambda%2Fbackend) to be able to follow the rest of the steps.
```shell
(env) ➜  exampulumi git:(2-api-lambda) tree -L 2
.
├── LICENSE
├── README.md
├── backend
│   ├── Dockerfile
│   ├── __init__.py
│   ├── env
│   ├── lambda_handler.py
│   ├── local_request.py
│   ├── requirements.txt
│   └── src
├── blog
│   ├── ...
├── infra
│   ├── ...
└── ui
    ├── ...
```

## Docker Image Creation and Uploading to AWS ECR
One of the best, newish features (released Dec. 2020) of AWS Lambda is the ability to use Docker images to package your Lambda applications. As Docker usage has become the de facto standard for setting up your local development environment, it makes sense to also use it for your deployed applications. We will also take advantage of a Pulumi feature to make creating an ECR repository a breeze - Pulumi Crosswalk:
> Pulumi Crosswalk for AWS is a collection of libraries that use automatic well-architected best practices to make common infrastructure-as-code tasks in AWS easier and more secure.
> - Pulumi intro

Pulumi crosswalk is a separate library so you will need to install it.
```shell
➜  exampulumi: cd infra
➜  infra: source venv/bin/activate
(venv) ➜  infra: pip install pulumi-awsx
...<installation logging>
```
The specific crosswalk we'll use is found here. Create a new file in your `infra->resources` directory and name it `ecr.py` And then add these few lines of code that creates a private repository for your docker images and builds and pushes your Docker image to that repo.
```python
import pulumi_awsx as awsx
from config import prefix

repository = awsx.ecr.Repository(f"{prefix}-repo")

image = awsx.ecr.Image(
    f"{prefix}-fast-api-lambda-image",
    repository_url=repository.url,
    path="../backend",
    extra_options=["--quiet"],
)
```
One lovely line to create a repo and another few lines to build and upload your Docker image. Note that the `path` argument is a relative path to the directory where the API's Dockerfile is located. If you choose to structure your project differently, make sure to update that path to point to the correct location. The `extra_options` argument of `["--quiet"]` prevents a bunch of unnecessary docker logs from displaying each time you run pulumi preview or pulumi up.

Before we upload our Docker image to the soon-to-be created ECR repo via Pulumi, let's make sure the image is built correctly and will properly respond to an API request. If you are new to Docker, there is an abundance of resource available to help you get up to speed. Additionally, FastAPI has tremendous [documentation on its official site](https://fastapi.tiangolo.com/) and many other tutorials. 

To build the image and run the container locally, open a terminal window and navigate to the backend directory. Once there you will build and tag the image via `docker build -t pulumi .` Make sure to include the period as that tells Docker to use the current directory as the build context. You will see many logs as the image builds:

```shell
(venv) ➜  backend git:(2-api-lambda) docker build -t pulumi .
[+] Building 42.3s (11/11) FINISHED
 => [internal] load build definition from Dockerfile                                                                       0.0s
 => => transferring dockerfile: 494B                                                                                       0.0s
 => [internal] load .dockerignore                                                                                          0.0s
 => => transferring context: 2B                                                                                            0.0s
 => [internal] load metadata for docker.io/amazon/aws-lambda-python:3.10                                                   1.1s
 => [1/6] FROM docker.io/amazon/aws-lambda-python:3.10@sha256:5b9fba87717e1584c7c180b9758b693b445decf867807f206df0cd945e6  8.6s
 => => resolve docker.io/amazon/aws-lambda-python:3.10@sha256:5b9fba87717e1584c7c180b9758b693b445decf867807f206df0cd945e6  0.0s
 => => sha256:528a9fd2768017f19c40ea279892dbeefccc4a1d81c52cbedde4e8a50079bc20 3.00kB / 3.00kB                             0.0s
 => => sha256:3d03dde9ded6ae265086b19245bb93eadc7694b13754d216f3d874a24aefd3c5 104.78MB / 104.78MB                         2.8s
 => => sha256:abeac2522dec12eecf3920bf073acf419f2a48c3fbce4589a27ea7a54e00e234 85.88kB / 85.88kB                           0.2s
 => => sha256:dbe66dd9d9d5f0e1a2b14ad33178e40e0c1ff2fe812c0a41f8246f0e4a92fce4 415B / 415B                                 0.1s
 => => sha256:5b9fba87717e1584c7c180b9758b693b445decf867807f206df0cd945e6b177b 1.58kB / 1.58kB                             0.0s
 => => sha256:1c13ed764ff2bfe6633e91f0511e7459838d0ad82a582853cb2b9c66df1ebb9a 2.51MB / 2.51MB                             0.3s
 => => sha256:63cb9d715d76cc9166d1f8c9adf85bb7dbee5dae30ea0ae68c7e107a99301764 64.39MB / 64.39MB                           2.2s
 => => sha256:63e822183613a7fd1ebe7335aaa71b2f17f3a99b22ab2fb90f8c5a358a3ef016 12.39MB / 12.39MB                           1.6s
 => => extracting sha256:3d03dde9ded6ae265086b19245bb93eadc7694b13754d216f3d874a24aefd3c5                                  2.3s
 => => extracting sha256:abeac2522dec12eecf3920bf073acf419f2a48c3fbce4589a27ea7a54e00e234                                  0.0s
 => => extracting sha256:dbe66dd9d9d5f0e1a2b14ad33178e40e0c1ff2fe812c0a41f8246f0e4a92fce4                                  0.0s
 => => extracting sha256:1c13ed764ff2bfe6633e91f0511e7459838d0ad82a582853cb2b9c66df1ebb9a                                  0.1s
 => => extracting sha256:63cb9d715d76cc9166d1f8c9adf85bb7dbee5dae30ea0ae68c7e107a99301764                                  2.0s
 => => extracting sha256:63e822183613a7fd1ebe7335aaa71b2f17f3a99b22ab2fb90f8c5a358a3ef016                                  0.7s
 => [internal] load build context                                                                                          0.0s
 => => transferring context: 6.79kB                                                                                        0.0s
 => [2/6] COPY requirements.txt  .                                                                                         1.3s
 => [3/6] RUN  pip3 install -r requirements.txt --target "/var/task"                                                      29.7s
 => [4/6] WORKDIR /var/task                                                                                                0.0s
 => [5/6] ADD src src                                                                                                      0.0s
 => [6/6] COPY lambda_handler.py .                                                                                         0.0s
 => exporting to image                                                                                                     1.5s
 => => exporting layers                                                                                                    1.5s
 => => writing image sha256:29c6c9e7d8f823eec9bb5e9bdb6f85bae6ba48bea23e1b7cadddcf882be02064                               0.0s
 => => naming to docker.io/library/pulumi
```
Now that the image is built, you can run it and then test it out to make sure everything is functioning properly. I often, in new dockerized python applications, have deployed them to Lambda only to run into import errors or other bugs. Running the image locally allows us to more quickly identify and fix those bugs. To assist with this effort, I created a simple script in the backend directory called local_request.py. It uses the requests library so install it if you do not already have it. To invoke the lambd image locally, you need to hit a special url `http://localhost:9000/2015–03–31/functions/function/invocations` with a POST request that contains json data that is structured as an event that lambda's process. All of that is handled for you in the script.

In one terminal window run the docker image and follow the logs: 
```shell
(venv) ➜  backend git:(2-api-lambda) docker run -d --rm -p 9000:8080 --name pulumi pulumi:latest && docker logs -f pulumi
eddcccc306fb557c51373383e019bb692482903ba7a63247e4b942ceef7dcffd
24 Jun 2023 17:01:52,845 [INFO] (rapid) exec '/var/runtime/bootstrap' (cwd=/var/task, handler=)
```
In a separate terminal window, run the `local_request.py` script. There's a breakpoint in the script so you can inspect the api response:
```shell
(venv) ➜  backend git:(2-api-lambda) python local_request.py
> /Users/egbert/projects/exampulumi/backend/local_request.py(84)main()
-> print(resp)
(Pdb) resp.json()
{'statusCode': 200, 'body': '{"item_id":555,"q":"boo"}', 'headers': {'content-length': '25', 'content-type': 'application/json'}, 'isBase64Encoded': False}
(Pdb) resp.status_code
200
(Pdb) c
<Response [200]>
{'statusCode': 200, 'body': '{"item_id":555,"q":"boo"}', 'headers': {'content-length': '25', 'content-type': 'application/json'}, 'isBase64Encoded': False}
In the terminal running the docker container, you should see many logs as I have added some basic logging to the application. These are the same logs you will see in AWS CloudWatch for your lambda application.
24 Jun 2023 17:09:59,603 [INFO] (rapid) extensionsDisabledByLayer(/opt/disable-extensions-jwigqn8j) -> stat /opt/disable-extensions-jwigqn8j: no such file or directory
24 Jun 2023 17:09:59,603 [INFO] (rapid) Configuring and starting Operator Domain
24 Jun 2023 17:09:59,603 [INFO] (rapid) Starting runtime domain
24 Jun 2023 17:09:59,603 [WARNING] (rapid) Cannot list external agents error=open /opt/extensions: no such file or directory
START RequestId: a870f13e-c4db-467a-bd53-276f62cfe943 Version: $LATEST
24 Jun 2023 17:09:59,603 [INFO] (rapid) Starting runtime without AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN , Expected?: false
{"asctime": "2023-06-24 17:09:59,841", "levelname": "INFO", "message": "", "log_type": "incoming_http_request", "path_params": {}, "query_params": "q=boo", "path": "/api/items/555", "method": "GET", "headers": "Headers({'cloudfront-is-android-viewer': 'false', 'cloudfront-viewer-country': 'US', 'x-amzn-tls-version': 'TLSv1.2', 'sec-fetch-site': 'none', 'cloudfront-viewer-postal-code': '44119', 'cloudfront-viewer-tls': 'TLSv1.3:TLS_AES_128_GCM_SHA256:fullHandshake', 'x-forwarded-port': '443', 'sec-fetch-user': '?1', 'via': '2.0 ee57d6770700357db4b696b4c5250b82.cloudfront.net (CloudFront)', 'x-amzn-tls-cipher-suite': 'ECDHE-RSA-AES128-GCM-SHA256', 'sec-ch-ua-mobile': '?0', 'cloudfront-is-desktop-viewer': 'true', 'cloudfront-viewer-asn': '7018', 'cloudfront-viewer-country-name': 'United States', 'host': 'xnn2voft2wbn7eyfqrnkow2gg40xycus.lambda-url.us-east-2.on.aws', 'upgrade-insecure-requests': '1', 'cache-control': 'max-age=0', 'cloudfront-viewer-city': 'Cleveland', 'sec-fetch-mode': 'navigate', 'cloudfront-viewer-http-version': '2.0', 'accept-language': 'en-US,en;q=0.9', 'cloudfront-viewer-address': '2600:1700:6640:e4d0:29c0:9cf7:9107:5eca:50235', 'x-forwarded-proto': 'https', 'cloudfront-is-ios-viewer': 'false', 'cloudfront-viewer-metro-code': '510', 'x-forwarded-for': '2600:1700:6640:e4d0:29c0:9cf7:9107:5eca', 'cloudfront-viewer-country-region': 'OH', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 'cloudfront-viewer-time-zone': 'America/New_York', 'cloudfront-is-smarttv-viewer': 'false', 'sec-ch-ua': '\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"', 'x-amzn-trace-id': 'Root=1-647cef1a-4937ab91132730a238bbdaa6', 'cloudfront-viewer-longitude': '-81.54920', 'cloudfront-is-tablet-viewer': 'false', 'sec-ch-ua-platform': '\"macOS\"', 'cloudfront-forwarded-proto': 'https', 'cloudfront-viewer-latitude': '41.58820', 'cloudfront-viewer-country-region-name': 'Ohio', 'accept-encoding': 'gzip, deflate, br', 'x-amz-cf-id': 'oexs8TSd7pccNPrijTKorXl6PqvJRgRTROgup8zoyu2k28l8HT7f3Q==', 'cloudfront-is-mobile-viewer': 'false', 'sec-fetch-dest': 'document', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'})", "aws_event": {"version": "2.0", "routeKey": "$default", "rawPath": "/api/items/555", "rawQueryString": "q=boo", "headers": {"cloudfront-is-android-viewer": "false", "cloudfront-viewer-country": "US", "x-amzn-tls-version": "TLSv1.2", "sec-fetch-site": "none", "cloudfront-viewer-postal-code": "44119", "cloudfront-viewer-tls": "TLSv1.3:TLS_AES_128_GCM_SHA256:fullHandshake", "x-forwarded-port": "443", "sec-fetch-user": "?1", "via": "2.0 ee57d6770700357db4b696b4c5250b82.cloudfront.net (CloudFront)", "x-amzn-tls-cipher-suite": "ECDHE-RSA-AES128-GCM-SHA256", "sec-ch-ua-mobile": "?0", "cloudfront-is-desktop-viewer": "true", "cloudfront-viewer-asn": "7018", "cloudfront-viewer-country-name": "United States", "host": "xnn2voft2wbn7eyfqrnkow2gg40xycus.lambda-url.us-east-2.on.aws", "upgrade-insecure-requests": "1", "cache-control": "max-age=0", "cloudfront-viewer-city": "Cleveland", "sec-fetch-mode": "navigate", "cloudfront-viewer-http-version": "2.0", "accept-language": "en-US,en;q=0.9", "cloudfront-viewer-address": "2600:1700:6640:e4d0:29c0:9cf7:9107:5eca:50235", "x-forwarded-proto": "https", "cloudfront-is-ios-viewer": "false", "cloudfront-viewer-metro-code": "510", "x-forwarded-for": "2600:1700:6640:e4d0:29c0:9cf7:9107:5eca", "cloudfront-viewer-country-region": "OH", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "cloudfront-viewer-time-zone": "America/New_York", "cloudfront-is-smarttv-viewer": "false", "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"", "x-amzn-trace-id": "Root=1-647cef1a-4937ab91132730a238bbdaa6", "cloudfront-viewer-longitude": "-81.54920", "cloudfront-is-tablet-viewer": "false", "sec-ch-ua-platform": "\"macOS\"", "cloudfront-forwarded-proto": "https", "cloudfront-viewer-latitude": "41.58820", "cloudfront-viewer-country-region-name": "Ohio", "accept-encoding": "gzip, deflate, br", "x-amz-cf-id": "oexs8TSd7pccNPrijTKorXl6PqvJRgRTROgup8zoyu2k28l8HT7f3Q==", "cloudfront-is-mobile-viewer": "false", "sec-fetch-dest": "document", "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}, "queryStringParameters": {"q": "boo"}, "requestContext": {"accountId": "anonymous", "apiId": "xnn2voft2wbn7eyfqrnkow2gg40xycus", "domainName": "xnn2voft2wbn7eyfqrnkow2gg40xycus.lambda-url.us-east-2.on.aws", "domainPrefix": "xnn2voft2wbn7eyfqrnkow2gg40xycus", "http": {"method": "GET", "path": "/api/items/555", "protocol": "HTTP/1.1", "sourceIp": "15.158.47.172", "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}, "requestId": "66c6f5ee-eafc-402f-95ca-1ec5343eea00", "routeKey": "$default", "stage": "$default", "time": "04/Jun/2023:20:07:54 +0000", "timeEpoch": 1685909274380}, "isBase64Encoded": false}}
{"asctime": "2023-06-24 17:09:59,845", "levelname": "INFO", "message": "GET /api/items/555 200"}
END RequestId: 332e9fac-8c59-4cfb-ae99-f767c9748c65
REPORT RequestId: 332e9fac-8c59-4cfb-ae99-f767c9748c65 Init Duration: 0.19 ms Duration: 243.75 ms Billed Duration: 244 msMemory Size: 3008 MB Max Memory Used: 3008 MB
```
If you are like me and often run into issues with correctly nesting files and using import statements correctly, you might see something like this instead when you do the above workflow.
```shell
(venv) ➜  backend git:(2-api-lambda) python local_request.py
> /Users/egbert/projects/exampulumi/backend/local_request.py(84)main()
-> print(resp)
(Pdb) resp.status_code
200
(Pdb) resp.json()
{'errorMessage': "Unable to import module 'lambda_handler': No module named 'main'", 'errorType': 'Runtime.ImportModuleError', 'requestId': '73eae281-f90e-4b93-910c-c47dcf1f8a01', 'stackTrace': []}
(Pdb)
```
And in the docker logs:
```shell
(venv) ➜  backend git:(2-api-lambda) ✗ docker run -d --rm -p 9000:8080 --name pulumi pulumi:latest && docker logs -f pulumi
33cce8da5111ab719deb1e34537e949f646e17453b608d50ae17cbeba6d8e0e5
24 Jun 2023 17:19:22,822 [INFO] (rapid) exec '/var/runtime/bootstrap' (cwd=/var/task, handler=)
24 Jun 2023 17:19:27,369 [INFO] (rapid) extensionsDisabledByLayer(/opt/disable-extensions-jwigqn8j) -> stat /opt/disable-extensions-jwigqn8j: no such file or directory
24 Jun 2023 17:19:27,369 [INFO] (rapid) Configuring and starting Operator Domain
24 Jun 2023 17:19:27,369 [INFO] (rapid) Starting runtime domain
24 Jun 2023 17:19:27,369 [WARNING] (rapid) Cannot list external agents error=open /opt/extensions: no such file or directory
24 Jun 2023 17:19:27,369 [INFO] (rapid) Starting runtime without AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN , Expected?: false
START RequestId: d3fec6b1-16a3-4f94-9aad-28e94603fc5d Version: $LATEST
Traceback (most recent call last): Unable to import module 'lambda_handler': No module named 'main'
END RequestId: 73eae281-f90e-4b93-910c-c47dcf1f8a01
REPORT RequestId: 73eae281-f90e-4b93-910c-c47dcf1f8a01 Init Duration: 0.16 ms Duration: 134.80 ms Billed Duration: 135 msMemory Size: 3008 MB Max Memory Used: 3008 MB
```
With that information, you can now go into your `lambda_handler.py` file and fix the import issue, rebuild the docker image, and rerun the `local_request.py` script to see if you have a functioning lambda. As your application progresses, you can continue to use this to debug thorny application failure bugs.

Now that we know that our docker image is properly built and ready to be deployed, let's use pulumi to create the resources and push the image to AWS. In the `infra` directory, update the `__main__.py` file by importing the image and creating an export of the image uri. You can export any attribute of your choosing, the important part is to get a resource from the `ecr.py` imported into the `__main__.py` file so pulumi will recognize it and create the resources in AWS.

```python
import pulumi

from config import service_name
from resources.route_53 import hosted_zone
from resources.acm import cert
from resources.ecr import image  # New code
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
pulumi.export("image_uri", image.image_uri)  # New code
```
And run pulumi up 

```shell
(venv) ➜  infra git:(2-api-lambda) ✗ pulumi up
Previewing update (dev)

View in Browser (Ctrl+O): https://app.pulumi.com/**/exampulumi/dev/previews/b3250a81-e33d-4d31-bb1d-75de5a995017

     Type                           Name                                  Plan
     pulumi:pulumi:Stack            exampulumi-dev
 +   ├─ awsx:ecr:Repository         dev-exampulumi-repo                   create
 +   │  ├─ aws:ecr:Repository       dev-exampulumi-repo                   create
 +   │  └─ aws:ecr:LifecyclePolicy  dev-exampulumi-repo                   create
 +   └─ awsx:ecr:Image              dev-exampulumi-fast-api-lambda-image  create

Outputs:
  + image_uri           : output<string>

Resources:
    + 4 to create
    22 unchanged

Do you want to perform this update?  [Use arrows to move, type to filter]
> yes
  no
  details

Updating (dev)

View in Browser (Ctrl+O): https://app.pulumi.com/**/exampulumi/dev/updates/87

     Type                           Name                                  Status              Info
     pulumi:pulumi:Stack            exampulumi-dev
 +   ├─ awsx:ecr:Repository         dev-exampulumi-repo                   created (2s)
 +   │  ├─ aws:ecr:Repository       dev-exampulumi-repo                   created (0.40s)
 +   │  └─ aws:ecr:LifecyclePolicy  dev-exampulumi-repo                   created (0.21s)
 +   └─ awsx:ecr:Image              dev-exampulumi-fast-api-lambda-image  created (0.41s)     1 warning

Outputs:
    a_record            : "dev.exampulumi.com"
    aaaa_record         : "dev.exampulumi.com"
    certificate         : "arn:aws:acm:us-east-1:<**>:certificate/<**>"
    cf_log_bucket_arn   : "arn:aws:s3:::dev-exampulumi-cf-logs-bucket"
    cloudfront_distro_id: "**"
    hosted_zone_id      : "**"
  + image_uri           : "<**>.dkr.ecr.us-east-2.amazonaws.com/dev-exampulumi-repo-**"
    service name        : "exampulumi"
    static_bucket_arn   : "arn:aws:s3:::dev-exampulumi-static-bucket"

Resources:
    + 4 created
    22 unchanged

Duration: 34s
```
If you log in to your AWS console and go to ECR, you'll have a repo and an image within the repo.

## AWS Lambda Configuration
Now that we have our web application packaged as a Docker image, and it is located in our ECR repository, we need to create a Lambda function that will run a container based on that image. In this step, you will create two files in the `resources` directory: `iam.py` and `aws_lambda.py` and add to the `__main__.py` file in the `infra` directory. First, we'll look at the `iam` resources needed. In the following code, we create a role for our lambda and create and add a policy to it that enables the lambda function to create logs in CloudWatch. Having the ability to inspect application logs for an API is pretty standard practice and this enables it for our application.
```python
import pulumi_aws as aws
from config import prefix

lambda_role = aws.iam.Role(
    f"{prefix}-lambda-role",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }""",
)

lambda_role_policy = aws.iam.RolePolicy(
    f"{prefix}-lambda-role-policy",
    role=lambda_role.id,
    policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }""",
)
```
Next, we'll create the lambda function itself in the `aws_lambda.py` file. Note that I've named the file with the prefix `aws_` as `lambda` is a reserved keyword in python so we want to avoid naming files or variables as lambda.
```python
import platform

import pulumi_aws as aws

from config import env, prefix
from resources.ecr import image
from resources.iam import lambda_role

# Sets the architecture properly. This makes it possible to build
# this on machines with different CPU architectures.
def get_arch():
    cpu_arch = platform.processor()
    if cpu_arch == "arm":
        return ["arm64"]
    return ["x86_64"]

fastapi_lambda = aws.lambda_.Function(
    f"{prefix}-lambda",
    name=f"{prefix}-lambda",
    architectures=get_arch(),
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            "FUNCTION_NAME": f"{prefix}-lambda",
            "ENV_NAME": env,
        }
    ),
    image_uri=image.image_uri,
    memory_size=256,
    package_type="Image",
    publish=True,
    role=lambda_role.arn,
    timeout=600,
)

lambda_alias = aws.lambda_.Alias(
    f"{prefix}-lambda-alias",
    name=f"{prefix}-lambda-alias",
    description="Alias for fastapi lambda",
    function_name=fastapi_lambda.name,
    function_version=fastapi_lambda.version,
)

fastapi_lambda_url = aws.lambda_.FunctionUrl(
    f"{prefix}-lambda-url",
    function_name=fastapi_lambda.name,
    qualifier=lambda_alias.name,
    authorization_type="NONE",
    cors=aws.lambda_.FunctionUrlCorsArgs(
        allow_credentials=True,
        allow_methods=["*"],
        allow_origins=["*"],
        allow_headers=["*"],
        max_age=600,
    ),
)
```
A few things that are worth pointing out:
- In the `aws.lambda_.Function` call, the `package_type` and `image_uri` are how we tell the Lambda that it is going to be using a docker image and which docker image it should use.
- In that function, we also add the `role` we created in the `iam.py` file so that the lambda can create CloudWatch logs.
- The `Alias` is a useful feature of AWS Lambda. It is a pointer that you can configure to route traffic to a specified version of the Lambda function. For now, we are just pointing it to the most recently published version. Aliases can be paired with other tools to enable advanced deployment practices like canary releases, blue/green deployments, etc. We will look at those in later articles. 🤞
- The final function call to `aws.lambda_.FunctionUrl` is the implementation of a really cool new feature that AWS rolled out in April, 2022. It lets you add an HTTPS endpoints to your Lambda function so you can hit your lambda from the internet without needing an Application Load Balancer or API Gateway in front of it. We have ours configured with auth and CORS effectively disabled as our python application will handle those concerns for us.

Now update `__main__.py` and we are ready to deploy our lambda function.
```python
import pulumi

from config import service_name
from resources.route_53 import hosted_zone
from resources.acm import cert
from resources.ecr import image
from resources.aws_lambda import (
    fastapi_lambda,
    fastapi_lambda_url,
)  # New code
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
pulumi.export("lambda_function_name", fastapi_lambda.name)  # New code
pulumi.export("function_url", fastapi_lambda_url.function_url) # New code
```
Run pulumi
```shell
(venv) ➜  infra git:(2-api-lambda) ✗ pulumi up
Previewing update (dev)

View in Browser (Ctrl+O): https://app.pulumi.com/**/exampulumi/dev/previews/**

     Type                       Name                                  Plan       Info
     pulumi:pulumi:Stack        exampulumi-dev
 +   ├─ aws:iam:Role            dev-exampulumi-lambda-role            create
 +   ├─ aws:iam:RolePolicy      dev-exampulumi-lambda-role-policy     create
     ├─ awsx:ecr:Image          dev-exampulumi-fast-api-lambda-image             1 warning
 +   ├─ aws:lambda:Function     dev-exampulumi-lambda                 create
 +   ├─ aws:lambda:Alias        dev-exampulumi-lambda-alias           create
 +   └─ aws:lambda:FunctionUrl  dev-exampulumi-lambda-url             create

Outputs:
  + function_url        : output<string>
  + lambda_function_name: "dev-exampulumi-lambda"

Do you want to perform this update? yes
Updating (dev)

View in Browser (Ctrl+O): https://app.pulumi.com/**/exampulumi/dev/updates/88

     Type                       Name                                  Status              Info
     pulumi:pulumi:Stack        exampulumi-dev
 +   ├─ aws:iam:Role            dev-exampulumi-lambda-role            created (0.51s)
 +   ├─ aws:iam:RolePolicy      dev-exampulumi-lambda-role-policy     created (0.24s)
     ├─ awsx:ecr:Image          dev-exampulumi-fast-api-lambda-image                      1 warning
 +   ├─ aws:lambda:Function     dev-exampulumi-lambda                 created (22s)
 +   ├─ aws:lambda:Alias        dev-exampulumi-lambda-alias           created (0.29s)
 +   └─ aws:lambda:FunctionUrl  dev-exampulumi-lambda-url             created (0.49s)

Outputs:
    a_record            : "dev.exampulumi.com"
    aaaa_record         : "dev.exampulumi.com"
    certificate         : "arn:aws:acm:us-east-1:**:certificate/f64d6b92-6675-4bc3-a4d1-e98003b5e22e"
    cf_log_bucket_arn   : "arn:aws:s3:::dev-exampulumi-cf-logs-bucket"
    cloudfront_distro_id: "E1M0VI1WKCGOKW"
  + function_url        : "https://<random-url>.lambda-url.us-east-2.on.aws/"
    hosted_zone_id      : "**"
    image_uri           : "**.dkr.ecr.us-east-2.amazonaws.com/dev-exampulumi-repo-997e9de:**"
  + lambda_function_name: "dev-exampulumi-lambda"
    service name        : "exampulumi"
    static_bucket_arn   : "arn:aws:s3:::dev-exampulumi-static-bucket"

Resources:
    + 5 created
    26 unchanged

Duration: 33s
```
Now you have a lambda function that is running your API AND it is already accessible via any browser through that really nasty url that is generated by AWS. If you go to whatever yours is (mine, currently is `https://kiwq5lxz4lz6tkv77pelgubloa0lpozs.lambda-url.us-east-2.on.aws`) but that can change. So go to `https://your-gross-url/api/docs` and you'll see:
![Fast API Docs on Function URL](https://raw.githubusercontent.com/dmegbert/exampulumi/main/blog/img/LambdaUrlApiDocs.png "FastAPI Docs")

To address the ugly and prone-to-change url issue, we'll leverage CloudFront in the next section.

## Update CloudFront with Reverse Proxy Capabilities
This is the section of the blog where the title is a bit misleading--the updates to CloudFront are not simple. What we are simplifying is that we are extending an existing resource and AWS service versus the typical Serverless architecture pattern of that uses API Gateway. Discussing why I am going with this pattern is probably a topic worthy of its own blog.  For now, let's focus on the "How" instead of the "Why".

First, get the latest frontend code from the `ui` directory on the `2-api-lambda` branch: [https://github.com/dmegbert/exampulumi/tree/2-api-lambda](https://github.com/dmegbert/exampulumi/tree/2-api-lambda). Open a terminal and go to the `ui` directory and run `yarn && yarn run build` to install the new JavaScript dependencies and build the assets for the static site.

We are now going to basically turn our CloudFront distribution into a reverse proxy server. What is especially powerful about this pattern is that you still get all the benefits of CloudFront's significant capabilities as a content delivery network (CDN). This includes things such as globally distributed edge locations, fine-grained caching controls, built-in DDoS protection, integration with AWS WAF and AWS Shield for even more robust security.

![Architecture Diagram showing reverse proxy routing](https://raw.githubusercontent.com/dmegbert/exampulumi/main/blog/img/architecture.png "Architecture Diagram showing reverse proxy routing")

As you can see in the diagram above, API calls are routed to the lambda function when they match the pattern exampulumi.com/api/*. All other traffic is routed to the S3 bucket hosting the React frontend app. Within our frontend application, you make API calls to `exampulumi.com/api/*` This means that as far as users' browsers are concerned, both the API and frontend are of the same origin so there is no need for the extra round trip `OPTIONS` preflight request. And you can just use `window.location.href` in your React code as the base url for your API calls and that will work for all of your deployment environments: `dev.exampulumi.com`, `staging.exampulumi.com`, `exampulumi.com`. No need for multiple environment variables in your React app to ensure it hits the correct API. I use this utility function:
```typescript
function getBaseUrl(): string {
    if (process.env.NODE_ENV !== 'production') return 'http://0.0.0.0:8000/api'
  return `${window.location.href}api`
}
```
Ok, let's update our CloudFront distribution so that we can reap all these benefits. It might also help to look at the [diff in GitHub.](https://medium.com/r/?url=https%3A%2F%2Fgithub.com%2Fdmegbert%2Fexampulumi%2Fpull%2F2%2Ffiles%23diff-fb4fc94bdddcd31e14f2d58f00892e884538734c2cd94bcba1234498f74c50ed) Here is the file with all the updates. We'll step through the changes below.
```python
import pulumi_aws as aws

from config import env, prefix, domain_name, PROD
from resources.acm import cert
from resources.aws_lambda import fastapi_lambda_url
from resources.route_53 import hosted_zone
from resources.s3 import cf_log_bucket, static_bucket

alias = domain_name if env == PROD else f"{env}.{domain_name}"

def create_cloudfront_distribution(
    certificate: aws.acm.Certificate,
    bucket: aws.s3.Bucket,
    lambda_function_url: aws.lambda_.FunctionUrl,
) -> aws.cloudfront.Distribution:
    s3_origin_id = f"{prefix}-s3-origin-id"
    origin_access_control = aws.cloudfront.OriginAccessControl(
        f"{prefix}-origin-access-control",
        description="S3 Bucket Policy",
        origin_access_control_origin_type="s3",
        signing_behavior="always",
        signing_protocol="sigv4",
    )
# 1
    lambda_origin_id = f"{prefix}-lambda-origin-id"
# 2
    lambda_cache_policy = aws.cloudfront.get_cache_policy(
        name="Managed-CachingDisabled"
    )
# 3
    lambda_origin_request_policy = aws.cloudfront.get_origin_request_policy(
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
# 4
        ordered_cache_behaviors=[
            aws.cloudfront.DistributionOrderedCacheBehaviorArgs(
                path_pattern="api/*",
                target_origin_id=lambda_origin_id,
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
                cache_policy_id=lambda_cache_policy.id,
                origin_request_policy_id=lambda_origin_request_policy.id,
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
# 5
            aws.cloudfront.DistributionOriginArgs(
                domain_name=lambda_function_url.function_url.apply(
                    lambda url: url.replace("https://", "").replace("/", "")
                ),
                origin_id=lambda_origin_id,
                custom_origin_config=aws.cloudfront.DistributionOriginCustomOriginConfigArgs(
                    http_port=80,
                    https_port=443,
                    origin_protocol_policy="https-only",
                    origin_ssl_protocols=["TLSv1.2"],
                ),
            ),
        ],
        restrictions=aws.cloudfront.DistributionRestrictionsArgs(
            geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                restriction_type="none",
            ),
        ),
        viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
            acm_certificate_arn=certificate.arn,
            minimum_protocol_version="TLSv1",
            ssl_support_method="sni-only",
        ),
    )

# 6
cf_distro = create_cloudfront_distribution(
    certificate=cert, bucket=static_bucket, lambda_function_url=fastapi_lambda_url
)

############################################
# Rest of file is unchanged from last blog #
############################################
```
1. The `lambda_origin_id` is just an arbitrary string that is needed as an argument in later parts of the CloudFront code.
2. The `lambda_cache_policy` is one of the managed cache policies that AWS provides for common use cases. The `CachingDisabled` policy means that we want CloudFront to forward all `/api/*` requests to our lambda application so that our backend can handle the requests.
3. The `lambda_origin_request_policy` is set to another managed policy. This one is the `AllViewerExceptHostHeader` that ensures CloudFront passes all headers, query strings, and cookies to the API. It does not pass the `Host` header from the viewer. Instead, it replaces the `Host` header with the origin's domain name. This is necessary as Lambda function URLs expect the `Host` to contain the origin domain name, not the CloudFront distribution domain name. Without this policy, you'll just get a 502 error for all API calls.
4. The `ordered_cache_behavior` is where you configure the CloudFront distribution to route requests that match the `path_pattern` of `api/*` to the Lambda Function URL. You set the `allowed_methods` to all the methods so that your API can handle all of them. And you add the `cache_policy_id` from the policy in step 2 and the `origin_request_policy_id` from step 3. This is also where the lambda_origin_id comes into play as that id connects the cache behavior to the origin for the Lambda Function URL that is in the next step.
5. In the `origins` list, we are now adding the Lambda Function URL as an origin. This will enable CloudFront to route the `/api/*` requests to the API running on the lambda function. And it'll also make that API available via a friendly URL `exampulumi.com/api` instead of the long, ugly url auto-generated by AWS for Lambda Function URLs. Note that the `origin_id` is again present and set for the same string that we used in the `ordered_cache_behavior` section. We are also parsing the `Lambda Function URL` to make it into the format that CloudFront requires for `domain_name` arguments. So we strip off the `https://` from the start of the output and the trailing `/` from the end using pulumi's .apply method. This is a callback method that is run against the returned value of an output once it's available. In this case, it is the Lambda Function URL. So if the Lambda Function URL changes in a future deployment, pulumi will grab that new value, parse it, and connect it to the CloudFront distribution. For our `origin_protocol_policy` we are using `https-only` as there's no need to support `http` as the `ordered_cache_behavior's` `viewer_protocol_policy` is set to `redirect-to-https` so that should mean all requests going to the Lambda Function URL origin are `https` requests.
6. The CloudFront distribution is created by a custom function, `create_cloudfront_distribution` to encapsulate some of the complexity. So we are now adding a new argument for our `lambda_function_url` and using it to pass our Lambda Function URL that we created in the `aws_lambda.py` resource file.

Before we deploy the new changes to our CloudFront distribution, let's look at some of the tweaks that are needed for the FastAPI backend to work in tandem with the CloudFront distribution.

## API Routing Updates
Now that our CloudFront distribution will be routing all requests that match `/api/*` to the FastAPI backend app running on a Lambda Function, we need to ensure that the endpoints are configured properly. The application needs to know that requests are going to have the /api/ prefix. It's possible to strip that from requests in AWS using a Lambda@Edge  function but most API frameworks make it really easy to handle a prefix. Here's the changes to the backend/src/main.py file to prepend the /api prefix to all routes. Create a router and use it to decorate your endpoint functions. Then add the router to your FastAPI app with the prefix argument set to /api and you are set.

```python
# imports...
from fastapi import APIRouter, FastAPI # Add APIRouter
# more imports...

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

# Unchanged ...

router = APIRouter()

@router.get("/hello")
def read_root():
    return {"Hello": "World"}

@router.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@router.post("/items", response_model=ItemResponse, status_code=201)
def create_item(*, item: Item):
    return ItemResponse(
        **item.dict(),
        id=uuid.uuid4(),
    )

app.include_router(router=router, prefix="/api")
```
Now that we have rebuilt our frontend code, updated our CloudFront distribution to route `/api/*` traffic to our Lambda Function URL, and updated our FastAPI app to expect requests with the `/api` prefix, let's deploy everything! `pulumi up.` CloudFront updates can take a while so this deployment might go on for a few minutes.
```shell
(venv) ➜  infra git:(2-api-lambda) pulumi up
Previewing update (dev)

View in Browser (Ctrl+O): https://app.pulumi.com/**/exampulumi/dev/previews/**

     Type                            Name                                    Plan       Info
     pulumi:pulumi:Stack             exampulumi-dev
     ├─ awsx:ecr:Image               dev-exampulumi-fast-api-lambda-image               1 warning
 ~   ├─ aws:lambda:Function          dev-exampulumi-lambda                   update     [diff: ~imageUri]
     ├─ aws:s3:Bucket                dev-exampulumi-static-bucket
 ~   │  ├─ aws:s3:BucketObject       index.html                              update     [diff: ~source]
 +   │  ├─ aws:s3:BucketObject       static/js/main.7bbbc739.js.LICENSE.txt  create
 ~   │  ├─ aws:s3:BucketObject       asset-manifest.json                     update     [diff: ~source]
 +   │  ├─ aws:s3:BucketObject       static/js/main.7bbbc739.js              create
 +   │  ├─ aws:s3:BucketObject       static/js/main.7bbbc739.js.map          create
 -   │  ├─ aws:s3:BucketObject       static/js/main.1a088b93.js.LICENSE.txt  delete
 -   │  ├─ aws:s3:BucketObject       static/js/main.1a088b93.js              delete
 -   │  └─ aws:s3:BucketObject       static/js/main.1a088b93.js.map          delete
 ~   ├─ aws:lambda:Alias             dev-exampulumi-lambda-alias             update     [diff: ~functionVersion]
 ~   └─ aws:cloudfront:Distribution  dev-exampulumi-distribution             update     [diff: ~customErrorResponses,orderedCac

Do you want to perform this update? yes
Updating (dev)

View in Browser (Ctrl+O): https://app.pulumi.com/**/exampulumi/dev/updates/90

     Type                            Name                                    Status              Info
     pulumi:pulumi:Stack             exampulumi-dev
     ├─ awsx:ecr:Image               dev-exampulumi-fast-api-lambda-image                        1 warning
     ├─ aws:s3:Bucket                dev-exampulumi-static-bucket
 ~   │  ├─ aws:s3:BucketObject       index.html                              updated (0.53s)     [diff: ~source]
 ~   │  ├─ aws:s3:BucketObject       asset-manifest.json                     updated (0.37s)     [diff: ~source]
 +   │  ├─ aws:s3:BucketObject       static/js/main.7bbbc739.js.LICENSE.txt  created (0.51s)
 +   │  ├─ aws:s3:BucketObject       static/js/main.7bbbc739.js              created (0.91s)
 +   │  ├─ aws:s3:BucketObject       static/js/main.7bbbc739.js.map          created (1s)
 -   │  ├─ aws:s3:BucketObject       static/js/main.1a088b93.js.map          deleted (0.31s)
 -   │  ├─ aws:s3:BucketObject       static/js/main.1a088b93.js              deleted (0.40s)
 -   │  └─ aws:s3:BucketObject       static/js/main.1a088b93.js.LICENSE.txt  deleted (0.53s)
 ~   ├─ aws:lambda:Function          dev-exampulumi-lambda                   updated (19s)       [diff: ~imageUri]
 ~   ├─ aws:lambda:Alias             dev-exampulumi-lambda-alias             updated (0.25s)     [diff: ~functionVersion]
 ~   └─ aws:cloudfront:Distribution  dev-exampulumi-distribution             updated (310s)      [diff: ~customErrorResponses,o

Outputs:
    a_record            : "dev.exampulumi.com"
    aaaa_record         : "dev.exampulumi.com"
    certificate         : "arn:aws:acm:us-east-1:**:certificate/**"
    cf_log_bucket_arn   : "arn:aws:s3:::dev-exampulumi-cf-logs-bucket"
    cloudfront_distro_id: "**"
    function_url        : "https://kiwq5lxz4lz6tkv77pelgubloa0lpozs.lambda-url.us-east-2.on.aws/"
    hosted_zone_id      : "**"
  ~ image_uri           : "**.dkr.ecr.us-east-2.amazonaws.com/dev-exampulumi-repo-997e9de:29c6c9e7d8f823eec9bb5e9bdb6f85bae6ba48bea23e1b7cadddcf882be02064" => "282753966079.dkr.ecr.us-east-2.amazonaws.com/dev-exampulumi-repo-**:**"
    lambda_function_name: "dev-exampulumi-lambda"
    service name        : "exampulumi"
    static_bucket_arn   : "arn:aws:s3:::dev-exampulumi-static-bucket"

Resources:
    + 3 created
    ~ 5 updated
    - 3 deleted
    11 changes. 23 unchanged

Duration: 5m40s
```

## Static Site Hitting API and FastAPI Docs
The API only returns dummy data as we have yet to set up a database. But you can still see a basic hello world app that is now hitting your API and peek in at the network tab of your dev tools to see that it really is happening.
![App screenshot with network tab showing api call](https://raw.githubusercontent.com/dmegbert/exampulumi/main/blog/img/appWithApi.png "App screenshot with network tab showing api call")
And the interactive documentation for the API is now at a friendly url:
![Openapi interactive documentation at a friendly url](https://raw.githubusercontent.com/dmegbert/exampulumi/main/blog/img/apiDocsFriendlyUrl.png "Openapi interactive documentation at a friendly url")
## Caveats
There are a couple of problems with the above setup that do not have great solutions.
1. The CloudFront distribution is configured to handle the client side routing of the React App, any 403 and 404 errors from the API will also be converted to 200 response codes and the user will receive the 404 error code page. We could possibly add a Lambda@Edge function to intercept error responses from the API but I'm not certain it's worth the effort as 403 and 404 errors from the app do not have the kind of specific information that a user might need like a 400 error with info on why the request was invalid.
2. The Lambda Function URL is openly accessible to anyone with the url. If a bad actor obtains the URL, they could spam the lambda and cause high charges, a DDoS attack by bypassing CloudFront's protections, and other issues. This might be more of a theoretical issue than an actual one and I plan on monitoring my lambda logs to see if there is any spamming occurring. Perhaps security through obscurity along with adding auth to the application code and some rate limiting is sufficient. If this is a concern, it might be better to not use a function url and use API Gateway and add a WAF to the Gateway to prevent unwanted traffic.

## Conclusion
I hope that this was a useful tutorial. Please share any feedback, questions, alternative ideas in the comments. And look for future articles in this series.
