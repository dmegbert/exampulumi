# Exampulumi

## Table of Contents
- [Introduction](#introduction)
- [Organization](#organization)
- [Tech Stack](#tech-stack)
- [Topics](#topics)
  1. [Static Site](#1-static-site)
  2. [Dockerized API on AWS Lambda](#2-dockerized-api-on-aws-lambda)
  3. [Securing your serverless stack with WAF](#3-securing-your-serverless-stack-with-waf)
  4. [Protect your apps with WAF v2 and AWS Managed Rules](#4-aws-waf-v2-with-managed-rules)

## Introduction
_For basic information on pulumi, sign up, go to their site at
[pulumi.com](https://pulumi.com). This project is not affiliated with pulumi._

This project provides examples of provisioning infrastructure on AWS using pulumi.
Since I started using pulumi, I have found it to be a great infrastructure as code (IaC)
tool. When learning pulumi, or any IaC tool for that matter, it has been
difficult to find tutorials / examples that go beyond the basics. This project
seeks to show how to set up a production-grade, full stack application.

## Organization
Each branch of the repo attempts to segment an application setup into a reasonably-sized
chunk of work that is related. For instance, the first branch is for setting up a static
site and is creatively named `1-static-site`. For each branch there is an accompanying
blog article that is published on my site, [gingerbeans.tech/blog](https://gingerbeans.tech/blog).

Each branch builds off of the previous one. However, I attempted to isolate topics so that
folks can opt in and review a particular section of the stack that is most interesting to 
them.

## Tech Stack
I am using Python (FastAPI) for the backend web application and React/TypeScript on the
frontend. It is my hope that folks using other stacks will still find this project useful. 
However, different stacks do lead to different infrastructure needs and YMMV, etc. etc.

## Topics

### 1.) Static Site
- Branch is `1-static-site`
- AWS services used: Route53, ACM, CloudFront, S3
- The blog that accompanies this code can be read at the following locations:
  - In this repo at [static site blog](https://github.com/dmegbert/exampulumi/blob/main/blog/static_site_blog.md)
  - It is also [on Medium here.](https://medium.com/@dmegbert/deploying-a-production-grade-static-site-on-aws-using-route53-cloudfront-and-s3-with-pulumi-17d95f9a283a)
  - And on [my website here.](https://gingerbeans.tech/blog/static_site_blog)

### 2.) Dockerized API on AWS Lambda
- Branch is `2-api-lambda`
- AWS services used: Cloudfront, AWS Lambda, ECR, IAM
- The blog that accompanies this code can be read at the following locations:
  - In this repo at [API Lambda](https://github.com/dmegbert/exampulumi/blob/main/blog/api_aws_lambda.md)
  - It is also [on Medium here.](https://aws.plainenglish.io/simplifying-serverless-deploy-a-docker-based-api-using-aws-lambda-function-urls-no-api-gateway-c18016591663)
  - And on [my website here.](https://gingerbeans.tech/blog/api_aws_lambda)

### 3) Securing your serverless stack with WAF
- Branch is `3-secure-api-and-cdn-with-waf`
- AWS services used: API Gateway, WAF
- The blog that accompanies this code can be read at the following locations:
  - In this repo at [Securing Serverless](https://github.com/dmegbert/exampulumi/blob/main/blog/securing_serverless.md)
  - It is also [on Medium here.](https://aws.plainenglish.io/securing-serverless-protect-lambda-apps-with-an-api-gateway-and-waf-via-pulumi-iac-fbf018d3ef4a)
  - And on [my website here.](https://gingerbeans.tech/blog/securing_serverless)

### 4) AWS WAF v2 with Managed Rules
- Branch is `3-secure-api-and-cdn-with-waf`
- AWS Services used: WAF v2 and CloudFront
- The blog that accompanies this code can be read at the following locations:
  - In this repo at [WAF v2 and AWS Managed Rules](https://github.com/dmegbert/exampulumi/blob/main/blog/waf_v2.md)
  - It is also [on Medium here.](https://aws.plainenglish.io/protect-your-apps-with-aws-managed-rules-for-waf-v2-via-pulumi-iac-74fcdc568a51)
  - And on [my website here.](https://gingerbeans.tech/blog/waf_v2)
