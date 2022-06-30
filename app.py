from constructs import Construct
from aws_cdk import (App, Stack, aws_lambda as lamb, aws_apigateway as apigw)

class ApiGateway(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        lambda_upload = lamb.Function(self, "LambdaUploadFunction",
                                      handler="lambda-upload.handler",
                                      runtime=lamb.Runtime.PYTHON_3_9,
                                      code=lamb.Code.from_asset("lambda"))

        lambda_download = lamb.Function(self, "LambdaDownloadFunction",
                                      handler="lambda-download.handler",
                                      runtime=lamb.Runtime.PYTHON_3_9,
                                      code=lamb.Code.from_asset("lambda"))

        base_api = apigw.RestApi(
            self, "ApiGateway",
            rest_api_name="ApiGateway",
            description="An API Gateway with Lambda Integration"
        )

        integration_options = apigw.IntegrationOptions(
            connection_type=apigw.ConnectionType("INTERNET"),
            passthrough_behavior=apigw.PassthroughBehavior("WHEN_NO_MATCH")
        )

        get_integration = apigw.Integration(
            type=apigw.IntegrationType("AWS_PROXY"),
            integration_http_method="POST",
            # uri=(f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_download.arn}/invocations"),
            options=integration_options
        )

        post_integration = apigw.Integration(
            type=apigw.IntegrationType("AWS_PROXY"),
            integration_http_method="POST",
            # uri=(f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_upload.arn}/invocations"),
            options=integration_options
        )

        method_get = apigw.IResource.add_method(self,
            http_method="GET",
            # integration=get_integration,
            authorization_type="NONE",
            operation_name="api-get"
        )

        method_post = apigw.IResource.add_method(self,
            http_method="POST",
            # integration=post_integration,
            authorization_type="NONE",
            operation_name="api-get"
        )

        # method_post = apigw.Resource.add_method("POST", api=base_api, http_method="POST")


        example_entity = base_api.root.add_resource(
            'example',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'POST'],
                allow_origins=apigw.Cors.ALL_ORIGINS))

        example_entity_lambda_integration = apigw.LambdaIntegration(
            lambda_upload,
            proxy=False,
            integration_responses=[
                apigw.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )

        example_entity.add_method(
            'GET', example_entity_lambda_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )

app = App()
ApiGateway(app, "ApiG-stack-cdk")
app.synth()