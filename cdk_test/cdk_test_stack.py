from asyncio.log import logger
import aws_cdk as cdk
import aws_cdk.aws_apigateway as apig
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class ApiGateway(cdk.Stack):
    def __init__(self, apig_client, scope: cdk.App) -> None:
        self.apig_client = apig_client
        self.api_id = None
        self.root_id = None
        self.stage = None

    def create_rest_api(self, api_name="lambda-api"):
        try:
            result = self.apig_client.create_rest_api(name=api_name,
                                                      description="An API Gateway with Lambda Integration")
            self.api_id = result["id"]
            logger.info(f"Created REST API {api_name} with ID {self.api_id}.")
        except ClientError:
            logger.exception(f"Couldn't create REST API {api_name}.")
            raise
        return self.api_id

    def create_resource_post(self, parent_id, resource_path="post"):
        try:
            result = self.apig_client.create_resource(
                restApiId=self.api_id, parentId=parent_id, pathPart=resource_path)
            resource_id = result["id"]
            logger.info(f"Created resource {resource_path}.")
        except ClientError:
            logger.exception(f"Couldn't create resource {resource_path}.")
            raise
        else:
            return resource_id

    def create_resource_get(self, parent_id, resource_path="{filename}"):
        try:
            result = self.apig_client.create_resource(
                restApiId=self.api_id, parentId=parent_id, pathPart=resource_path)
            resource_id = result["id"]
            logger.info(f"Created resource {resource_path}.")
        except ClientError:
            logger.exception(f"Couldn't create resource {resource_path}.")
            raise
        else:
            return resource_id

    def create_method_post(self, resource_id, service_endpoint_prefix,
                      service_action, service_method, role_arn, mapping_template, rest_method="POST"):

        service_uri=(f"arn:aws:apigateway:{self.apig_client.meta.region_name}:{service_endpoint_prefix}:action/{service_action}")

        try:
            self.apig_client.put_method(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpdMethod=rest_method,
                authorizationType="NONE")

            self.apig_client.put_method_response(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpdMethod=rest_method,
                statusCode="200",
                responseModels={"application/json": "Empty"})
            logger.info(f"Created {rest_method} method for resource {resource_id}.")
        except ClientError:
            raise

        try:
            self.apig_client.put_integration(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod=rest_method,
                type="AWS_PROXY",
                passthroughBehaviour="WHEN_NO_MATCH",
                integrationHttpMethod="POST",
                uri=(f"arn:aws:apigateway:{self.apig_client.meta.region_name}:lambda:path/2015-03-31/functions/${LambdaFunctionUpload.Arn}/invocations")
            )
            self.apig_client.put_integration_response(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod=rest_method,
                statusCode="200",
                responseTemplates={"application/json": ""})
            logger.info(
                f"Created integration for resource {resource_id} to service URI {service_uri}."
            )
        except ClientError:
            raise