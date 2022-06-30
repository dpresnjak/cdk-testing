#!/usr/bin/env python3
import os
import aws_cdk as cdk
from cdk_test.cdk_test_stack import ApiGateway
app = cdk.App()

ApiGateway(app)

app.synth()