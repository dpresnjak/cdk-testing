from constructs import Construct
from aws_cdk import (App, Stack, Duration,
                     aws_lambda as lamb,
                     aws_apigateway as apigw,
                     aws_iam as awsiam,
                     aws_cloudwatch as cw,
                     aws_sns as sns,
                     aws_sns_subscriptions as sns_sub,
                     aws_cloudwatch_actions as cw_actions)

# from cdk_test.lambdas import lambda_download, lambda_upload

class ApiGateway(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # myBucket.grantRead(myLambda)

        # Creating Lambda functions using the code from ./lambda/
        lambda_upload = lamb.Function(self, "LambdaUploadFunction",
                                      handler="lambda-upload.lambda_handler",
                                      runtime=lamb.Runtime.PYTHON_3_9,
                                      code=lamb.Code.from_asset("lambda"))

        lambda_download = lamb.Function(self, "LambdaDownloadFunction",
                                      handler="lambda-download.lambda_handler",
                                      runtime=lamb.Runtime.PYTHON_3_9,
                                      code=lamb.Code.from_asset("lambda"))

        # Adding policy statements to Lambda service roles
        lambda_download.add_to_role_policy(awsiam.PolicyStatement(
                    actions=["s3:GetObject"],
                    resources=["arn:aws:s3:::*"]
                )
        )

        lambda_upload.add_to_role_policy(awsiam.PolicyStatement(
                    actions=["s3:PutObject"],
                    resources=["arn:aws:s3:::*"]
                )
        )

        # API Gateway policy statements
        agw_policy = awsiam.PolicyDocument(
                                statements=[
                                    awsiam.PolicyStatement(
                                        actions=["execute-api:Invoke"],
                                        principals=[awsiam.AnyPrincipal()],
                                        resources=["execute-api:/*/*/*"],
                                    ),
                                    awsiam.PolicyStatement(
                                        effect=awsiam.Effect.ALLOW,
                                        principals=[awsiam.AnyPrincipal()],
                                        actions=["lambda:*"],
                                        resources=["arn:aws:lambda:us-east-1:176984903748:function:*"],
                                    )
                                ]
                            )

        # Lambda Integrations to connect with an APIG method
        lambda_upload_int = apigw.LambdaIntegration(
            lambda_upload,
            proxy=True,
        )

        lambda_download_int = apigw.LambdaIntegration(
            lambda_download,
            proxy=True,
        )

        # Creating API Gateway
        base_api = apigw.RestApi(
            self, "ApiGateway",
            rest_api_name="ApiGateway",
            description="An API Gateway with Lambda Integration",
            policy = agw_policy
        )

        # Adding API Gateway resources and methods
        post = base_api.root.add_resource("post")
        post.add_method("POST", lambda_upload_int, authorization_type=None)

        get = base_api.root.add_resource("{filename}")
        get.add_method("GET", lambda_download_int, authorization_type=None)

        # Cloudwatch alarms
        lambda_alarm_metric_upl=lambda_upload.metric_all_errors(label="LambdaUploadErrors",
                                                            period=Duration.seconds(60),
                                                            statistic="sum")
        lambda_alarm_metric_dl=lambda_upload.metric_all_errors(label="LambdaDownloadErrors",
                                                            period=Duration.seconds(60),
                                                            statistic="sum")

        alarm_up = cw.Alarm(self, "CW Alarm upload",
                            metric=lambda_alarm_metric_upl,
                            evaluation_periods=1,
                            threshold=5,
                            alarm_description="Lambda function has triggered five (5) errors.",
                            comparison_operator=cw.ComparisonOperator("GREATER_THAN_THRESHOLD"),
                            datapoints_to_alarm=1,
                            )

        alarm_down = cw.Alarm(self, "CW Alarm download",
                            metric=lambda_alarm_metric_dl,
                            evaluation_periods=1,
                            threshold=5,
                            alarm_description="Lambda function has triggered five (5) errors.",
                            comparison_operator=cw.ComparisonOperator("GREATER_THAN_THRESHOLD"),
                            datapoints_to_alarm=1,
                            )
        # SNS Topics
        sns_upl_topic = sns.Topic(self, "SNS Lambda upload Topic",
                                  topic_name = "api-lambda-upload-errors-cdk")

        sns_dl_topic = sns.Topic(self, "SNS Lambda download Topic",
                                  topic_name = "api-lambda-download-errors-cdk")

        alarm_up.add_alarm_action(cw_actions.SnsAction(sns_upl_topic))
        alarm_down.add_alarm_action(cw_actions.SnsAction(sns_dl_topic))


        # Email subscriptions
        sns_upl_sub = sns_sub.EmailSubscription(email_address="dpresnjak@iolap.com", json=True)
        sns_dl_sub = sns_sub.EmailSubscription(email_address="dpresnjak@iolap.com", json=True)

        sns_upl_topic.add_subscription(subscription=sns_upl_sub)
        sns_dl_topic.add_subscription(subscription=sns_dl_sub)

        sns_upl_topic_conf = sns.TopicSubscriptionConfig(endpoint="dpresnjak@iolap.com",
                                                         protocol=sns.SubscriptionProtocol.EMAIL,
                                                         subscriber_id="sns_upload")

        sns_dl_topic_conf = sns.TopicSubscriptionConfig(endpoint="dpresnjak@iolap.com",
                                                         protocol=sns.SubscriptionProtocol.EMAIL,
                                                         subscriber_id="sns_download")


app = App()
ApiGateway(app, "ApiG-stack-cdk")
Alarms(app, "CW-alarms")

app.synth()