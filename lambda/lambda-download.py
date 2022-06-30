import json
import boto3
import base64


def lambda_handler(event, context):
    print(event)

    s3 = boto3.client("s3")

    file_name = (event["pathParameters"])
    file_key = file_name['filename']

    contents = s3.get_object(Bucket="apig-lambda-testing", Key=file_key)["Body"].read()

    contents_json = json.loads(contents)

    response = {
        'statusCode': 200,
        'body': json.dumps(contents_json)
    }

    return response