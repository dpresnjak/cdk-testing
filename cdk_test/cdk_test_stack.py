from asyncio.log import logger
import aws_cdk as cdk
import aws_cdk.aws_apigateway as apig

import argparse
import json
import logging
from pprint import pprint
import boto3
from botocore.exceptions import ClientError
import requests

logger = logging.getLogger(__name__)

class ApiGateway:
    def __init__(self, apig_client):
        self.apig_client = apig_client
        self.api_id = None
        self.root_id = None
        self.stage = None

    def create_rest_api(self, api_name):
        try:
            result = self.apig_client.create_rest_api(name=api_name)
            self.api_id = result["id"]
            logger.info(f"Created REST API {api_name} with ID {self.api_id}.")
        except ClientError:
            logger.exception(f"Couldn't create REST API {api_name}.")
            raise
        return self.api_id

    def create_resource(self, parent_id, resource_path):
        try:
            result = self.apig_client.create_resource(
                restApiId=self.api_id, parentId=parent_id, pathPart=resource_path)
            resource_id = result["id"]
            logger.info(f"Created resource {resource_path}.")
        return resource_id

    def create_method(self, resource_id, rest_method, ):