from constructs import Construct
from aws_cdk import (App, Stack, aws_lambda as lamb, aws_apigateway as apigw, aws_iam as awsiam)

class ApiGateway(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        lambda_upload = lamb.Function(self, "LambdaUploadFunction",
                                      handler="lambda-upload.lambda_handler",
                                      runtime=lamb.Runtime.PYTHON_3_9,
                                      code=lamb.Code.from_asset("lambda"))

        lambda_download = lamb.Function(self, "LambdaDownloadFunction",
                                      handler="lambda-download.lambda_handler",
                                      runtime=lamb.Runtime.PYTHON_3_9,
                                      code=lamb.Code.from_asset("lambda"))

        s3_policy = awsiam.IManagedPolicy("arn:aws:iam::aws:policy/AmazonS3FullAccess")
        lambda_upload_int = apigw.LambdaIntegration(
            lambda_upload,
            proxy=True,
            # credentials_role=awsiam.IRole.add_managed_policy(s3_policy)
        )

        lambda_download_int = apigw.LambdaIntegration(
            lambda_download,
            proxy=True,
            # credentials_role=awsiam.IRole.add_managed_policy(s3_policy)
        )

        base_api = apigw.RestApi(
            self, "ApiGateway",
            rest_api_name="ApiGateway",
            description="An API Gateway with Lambda Integration"
        )

        # integration_options = apigw.IntegrationOptions(
        #     connection_type=apigw.ConnectionType("INTERNET"),
        #     passthrough_behavior=apigw.PassthroughBehavior("WHEN_NO_MATCH")
        # )
        #
        # get_integration = apigw.Integration(
        #     type=apigw.IntegrationType("AWS_PROXY"),
        #     integration_http_method="POST",
        #     # uri=(f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_download.arn}/invocations"),
        #     options=integration_options
        # )
        #
        # post_integration = apigw.Integration(
        #     type=apigw.IntegrationType("AWS_PROXY"),
        #     integration_http_method="POST",
        #     # uri=(f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_upload.arn}/invocations"),
        #     options=integration_options
        # )
        #
        # method_get = apigw.IResource.add_method(self,
        #     http_method="GET",
        #     # integration=get_integration,
        #     authorization_type="NONE",
        #     operation_name="api-get"
        # )
        #
        # method_post = apigw.IResource.add_method(self,
        #     http_method="POST",
        #     # integration=post_integration,
        #     authorization_type="NONE",
        #     operation_name="api-get"
        # )
        # base_api.root.add_method("ANY")

        post = base_api.root.add_resource("post")
        post.add_method("POST", lambda_upload_int, authorization_type=None)

        get = base_api.root.add_resource("{filename}")
        get.add_method("GET", lambda_download_int, authorization_type=None)

        # method_post = base_api.root.add_method("POST", http_method="POST")


app = App()
ApiGateway(app, "ApiG-stack-cdk")
app.synth()