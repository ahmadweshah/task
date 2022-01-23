import json
import os
from hashlib import md5
import logging
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    """
    :param event: dict contain body that come from API Gateway
    :param context: dict context of the request
    :return: statusCode: (200, 400, 417) , body: json object {message_key, message, data}
    """

    s3 = boto3.client('s3')
    bucket = 'serverless-upload-file-20-01-2022'
    body = json.loads(event["body"])
    file_name = body.get('file_name')

    if file_name is None or file_name == '':
        return {
            'statusCode': 400,
            'body': json.dumps(generate_response('file_name_required'))
        }
    file_name = file_name.replace(' ', "_")
    name, extension = os.path.splitext(file_name)
    key = md5(name.encode('utf-8')).hexdigest() + extension
    check_object_status = check_object(s3, bucket, key)
    if check_object_status is None:
        return {
            'statusCode': 400,
            'body': json.dumps(generate_response('file_not_exists'))
        }
    try:
        s3.delete_object(Bucket=bucket, Key=key)
    except ClientError as e:
        return {
            'statusCode': 417,
            'body': json.dumps(generate_response('error_delete_file'))
        }

    return {
        'statusCode': 200,
        'body': json.dumps(generate_response('file_deleted_succ'))
    }


def check_object(s3, bucket_name, object_name):
    try:

        response = s3.get_object(Bucket=bucket_name, Key=object_name)

    except ClientError as e:

        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def generate_response(message_key):
    messages = {
        "file_deleted_succ": "File deleted successfully",
        "file_name_required": "file_name is required",
        "file_not_exists": "file not exists",
        "error_delete_file": "error while deleting file",
        "exception_msg": "Something went wrong..."
    }
    response = {
        "message_key": message_key,
        "message": messages.get(message_key),
        "data": {}
    }
    return response
