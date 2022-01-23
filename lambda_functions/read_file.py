import json
import os
from hashlib import md5
import logging
import boto3
from botocore.exceptions import ClientError
import traceback


def lambda_handler(event, context):
    """
    :param event: dict contain body that come from API Gateway
    :param context: dict context of the request
    :return: statusCode: (200, 400, 417) , body: json object {message_key, message, data}
    """
    try:
        body = json.loads(event["body"])
        file_name = body.get('file_name')
        bucket = 'serverless-upload-file-20-01-2022'

        if file_name is None or file_name == '':
            return {
                'statusCode': 400,
                'body': json.dumps(generate_response('file_name_required'))
            }
        file_name = file_name.replace(' ', "_")
        name, extension = os.path.splitext(file_name)
        key = md5(name.encode('utf-8')).hexdigest() + extension
        file_presigned_url = create_presigned_url(bucket, key)
        if file_presigned_url is None:
            return {
                'statusCode': 400,
                'body': json.dumps(generate_response('file_not_exists'))
            }

        response = generate_response('file_fetch_succ')
        response['data']['file_url'] = file_presigned_url
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }

    except Exception as e:
        print(str(traceback.format_exc()))
        return {
            'statusCode': 417,
            'body': json.dumps(generate_response('exception_msg'))
        }


def create_presigned_url(bucket_name, object_name, expiration=3600):
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        # generate_presigned_url not raising exception if file not exists so i called get_object to raise this exception
        s3_client.get_object(Bucket=bucket_name, Key=object_name)

        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def generate_response(message_key):
    messages = {
        "file_fetch_succ": "File retrieve successfully",
        "file_name_required": "file_name is required",
        "file_not_exists": "file not exists",
        "exception_msg": "Something went wrong..."
    }
    response = {
        "message_key": message_key,
        "message": messages.get(message_key),
        "data": {}
    }
    return response
