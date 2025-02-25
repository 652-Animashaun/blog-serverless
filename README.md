# blog-serverless


## Introduction

So we’ve been playing with local builds of some interesting python frameworks.

About now lets put our application out there, in world wide web, where wild things pop.  
It’s always interesting to deploy what you’ve built so other people can look at it or better yet interact with it.

In this post we won’t be looking at setting up the application itself or it’s containerisation in details. Rather, I want to zoom in on deploying to serverless architecture in the cloud. On AWS Lambda, and in a subsequent post, on Google Cloud Functions (yeh, its cloudy, with a chance of code-rain).

I’m not promising this will be published serially but, fingers crossed.

## Prerequisite

To follow along, couple of assumptions had been made. First, you already have an AWS account with sufficient IAM permissions, and [AWS command line interface setup](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).

Python3.12

[Docker desktop](https://www.docker.com/products/docker-desktop/)

## /src\_code

The source code is a python Framework - Fast API, it’s especially lightweight, extensively extendable and quite useful for pretty much any API exposure use-case.

I need to emphasis that though for the purpose of this post, the api is written in Fast API serverlette framework, it is not the focus, therefore the deploy configurations exemplified here can be used for any other python framework, Flask for example.

This is because we can wrap startup server command of any framework with the Mangum adapter and pass the modularised “app” into an handler with the `Mangum() class`.

Here I’ll show you. Clone the repo [https://github.com/652-Animashaun/blog-serverless.git](https://github.com/652-Animashaun/blog-serverless.git)

## an\_ASGI\_Framework

**If you** `cd blog-serverless/app` **the main.py file looks like this:**

```python
from fastapi import FastAPI
from mangum import Mangum
from app.api.api_v1.api import router as api_router


app = FastAPI()


@app.get("/")
async def root():
  return {"Welcome": "Serveless-blog-api"}

app.include_router(api_router, prefix="/api/v1")

handler = Mangum(app)
```

While a Flask app will be wrapped like so:

<details data-node-type="hn-details-summary"><summary>this flask app code isn’t part of the cloned project</summary><div data-type="detailsContent">from flask import Flask from mangum import Mangum app = Flask(__name__) @app.route('/') def hello_world(): return 'Hello, World!' handler = Mangum(app)</div></details>

```python
from flask import Flask
from mangum import Mangum

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

handler = Mangum(app)
```

This is possible because Mangum provides support for any Asynchronous Server Gateway Interface. Read more about [Mangum](https://mangum.fastapiexpert.com/asgi-frameworks/).

## Dockerfile

AWS provides it’s own centOS based python image, which has the same environment as the lambda runtime.

###### Example Dockerfile

```dockerfile
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY ./app ${LAMBDA_TASK_ROOT}/app

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.main.handler" ]
```

Using os-only based image or just any alternate image, we must build the final image with the runtime interface awslambdaric.

For this project we’re using python3.12 and python3.12-slim as base image. awslambdaric will be installed during image build, its already in the requirements.txt file

Example Dockefile with runtime interface

```dockerfile

# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.12 AS build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}

# Install the function's dependencies
RUN pip install \
    --target ${FUNCTION_DIR} \
        -r ${FUNCTION_DIR}/requirements.txt

# Use a slim version of the base Python image to reduce the final image size
FROM python:3.12-slim

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
CMD [ "app.main.handler" ]
```

This allows us set runtime interface client as default at container runtime and pass the app.main handler as command at runtime. Read more [https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-clients](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-clients)

## Build Image and Deploy to AWS Container Registry

Build image with `docker build —platform linux/amd64 -t blog-serverless .`

The platform flag is building for environment similar to what AWS Lambda environment. Remember it’s serverless, meaning you really can't change anything about the platform its built upon since we did not provision it. Which is part of the gifts of Lambda functions.

If you’ve set up your AWS CLI correctly then you can run the command:  
`aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 111122223333.dkr.ecr.us-east-1.amazonaws.com`

or a slightly different command with the flag —profile to indicate what profile you want to log in with if you have multiple profiles configured, like so:

`aws ecr get-login-password --profile lambda-user --region us-east-1 | docker login --username AWS --password-stdin 111122223333.dkr.ecr.us-east-1.amazonaws.com`

Create repository:

`aws ecr create-repository --repository-name blog-serverless --region us-east-1 --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE`

Copy repositoryUri from the response looks something like:  
`"111122223333.dkr.ecr.us-east-1.amazonaws.com/blog-serverless"`  
Include uri in next command to tag your local build to ecr repo you just created:  
`docker tag blog-serverless` `111122223333.dkr.ecr.us-east-1.amazonaws.com/blog-serverless`

Then `docker push 111122223333.dkr.ecr.us-east-1.amazonaws.com/blog-serverless:latest`

Now we need to create an execution role which would be attached to the function. Basically granting the function permissions to access AWS resources it needs to operate.

`aws iam create-role --role-name LambdaExecutionRole --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'`

In the response object, copy the ARN which would look something like this, we need it in next steps.

`arn:aws:iam::111122223333:role/LambdaExecutionRole`

The role has been created, now we can create a lambda function “blog-serverless-dev” from our ECR repo blog-serverless:latest like so:

`aws lambda create-function --function-name blog-serverless-dev --package-type Image --code ImageUri=111122223333.dkr.ecr.us-east-1.amazonaws.com/blog-serverless:latest --role arn:aws:iam::111122223333:role/LambdaExecutionRole`

This would also return a response, telling all about the deploy.

You can now head over to AWS lambda and check the function blog-serverless-dev.

## Testing

In AWS Lambda dashboard select function code. Don’t worry, because the function code itself and other artefacts lives in a container, lambda dashboard won’t be able to display source code the way it usually does when the artefact is derived directly from .zip file, or written directly in the GUI editor.

But, we can still test the function code, make sure we’re handling ASGI requests and responding properly.

Select Test on the lower tab on the dashboard, on the Template selection dropdown, select apigateway-aws-proxy. Scroll down to examine the generated JSON payload snippet.

We need to edit the JSON payload snippet, just the first bits:

```plaintext
{
  "body": "eyJ0ZXN0IjoiYm9keSJ9",
  "resource": "/{proxy+}",
  "path": "/api/v1/posts/",
  "httpMethod": "GET",
  "isBase64Encoded": true,
  "queryStringParameters": {
    "foo": "bar"
  },
```

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1737922929040/a7180db2-2263-4f68-9e29-5989282b9a2f.gif align="center")

In the response object notice `“statusCode“: “200”` and `"body": "{"message":"Posts!"}"` .

And check this, we can follow the logs to cloudWatch to see logs. Isn’t that awesome, even when we didn’t provision a logging interface.

## AWS API Gateway

There are so many reasons to use the API Gateway vs the application load balance

AWS Lambda + API Gateway: No infrastructure to manage

Support for the WebSocket Protocol

Handle API versioning (v1, v2...)

Handle different environments (dev, test, prod...)

Handle security (Authentication and Authorisation) • Create API keys, handle request throttling

Swagger / Open API import to quickly define APIs • Transform and validate requests and responses

Generate SDK and API specifications

Cache API responses

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1737924704223/cd7a930f-8258-480b-a56e-90e0c6b1d188.png align="center")

We create an API blog-restful-api choose the rest build. Create a method ANY for any proxy connection select lambda integration and select the lambda ARN.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1738002823552/13582670-2ff1-4dda-873b-42a2c702dac9.gif align="center")

Create a proxy resource /{proxy+} which will proxy any requests to the appropriate route.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1738002932703/b2580d0a-47ae-45fe-8910-6b8806a1694f.gif align="center")

Deploy API and give it a stage name like “dev”. Then endpoint url would be provided if you look in stages you should see the url endpoint for the API you just deployed.

If you visit {url\_endpoint}/{stage\_name}/api/v1/posts/ in the browser to view posts endpoint you should be greeted with a response.

Well that’s it! You’ve done well to follow till this point.

Drop a comment.

# Reference

1 - https://docs.authlib.org/en/latest/client/fastapi.html
2 - https://docs.aws.amazon.com/cli/latest/reference/cognito-idp/
3- https://pyjwt.readthedocs.io/en/stable/usage.html#retrieve-rsa-signing-keys-from-a-jwks-endpoint
