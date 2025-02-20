# blog-serverless
source code for blog post 'Dockerizing Python frameworks - FastApi for Nerveless Deployments - AWS Lambda, GoogleCloud, MS Azure


I figured I needed to add a logical next step to securing the app. I was also partly inspired by the course by Steven Marek towards AWS Solutions Architect Certification, which I'm studying. 

## /src_code

The GitHub code repo for this project is here: 

Its written in Python - FastApi, deployed to AWS Lambda, we then put an API Gateway in front to route client requests to appropriate endpoints. That's it you're all caught up. 

While code example used here is Fast API framework, I implore you the implementation discussed is python framework agnostic. Come on I'll show you.

# Reference

1 - https://docs.authlib.org/en/latest/client/fastapi.html
2 - https://docs.aws.amazon.com/cli/latest/reference/cognito-idp/
3- https://pyjwt.readthedocs.io/en/stable/usage.html#retrieve-rsa-signing-keys-from-a-jwks-endpoint
