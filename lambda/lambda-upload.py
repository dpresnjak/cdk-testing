import json
import boto3


def lambda_handler(event, context):
    print(event)

    s3 = boto3.client("s3")

    contents = (event["body"])
    print(f"Contents: {contents}")

    body_dict = json.loads(contents)

    # Getting first and last name for filename
    first_name = body_dict.get("first_name")
    last_name = body_dict.get("last_name")
    filename = first_name + "_" + last_name + ".json"

    body_bytes = json.dumps(body_dict, indent=2).encode('utf-8')

    s3.put_object(Bucket="apig-lambda-testing", Key=filename, Body=body_bytes)

    response = {
        'statusCode': 200,
        'body': "Succesfully uploaded a file called " + filename
    }

    return response