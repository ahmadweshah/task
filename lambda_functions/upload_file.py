import hashlib
import json
import boto3
from hashlib import md5
import base64
from mimetypes import guess_extension
import os
import traceback

"""
For upload I used base64 methodology not multipart because the following reasons:
1. Lambda has payload limit of 6mb for synchronous call and 256KB for async call. 
    (https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)
2. Also api gateway has limit of 10MB for RESTfull APIs and 128KB for socket message
    https://docs.aws.amazon.com/apigateway/latest/developerguide/limits.html
3. and the most important from cost wise: you pay for lambda execution while uploading. It is just a waste of lambda's time.
4. the better way in Multipart to use Pre-Signed URL for an Amazon S3 PUT Operation (which is out of scope in this task)
    https://docs.aws.amazon.com/sdk-for-go/v1/developer-guide/s3-example-presigned-urls.html
"""


def lambda_handler(event, context):
    """
    :param event: dict contain body that come from API Gateway
    :param context: dict context of the request
    :return: statusCode: (200, 400, 417) , body: json object {message_key, message, data}
    """
    bucket_name = 'serverless-upload-file-20-01-2022'
    try:
        s3 = boto3.resource('s3')
        body = json.loads(event["body"])

        file_name = body.get('file_name')
        file_base64 = body.get('file_base64')

        if file_name is None or file_name == '':
            return {
                'statusCode': 400,
                'body': json.dumps(generate_response("file_name_required"))
            }

        if file_base64 is None or file_base64 == '':
            return {
                'statusCode': 400,
                'body': json.dumps(generate_response("file_base64_required"))
            }

        file = decode_file_base64(file_base64)
        file_extension = file[0]
        if file_extension is None:
            return {
                'statusCode': 400,
                'body': json.dumps(generate_response("wrong_base64_encoding"))
            }
        file_string_postfix = file[1]
        file_name = file_name.replace(' ', "_")
        name, extension = os.path.splitext(file_name)
        # Double check between extension in file_name field and in base64
        if file_extension != extension:
            return {
                'statusCode': 400,
                'body': json.dumps(generate_response("wrong_extension"))
            }
        final_file_name = md5(name.encode('utf-8')).hexdigest() + extension
        uploaded_file_path = '/tmp/' + final_file_name
        try:
            decoded_data = base64.b64decode(file_string_postfix.encode('utf-8'), validate=True)
            # upload file to tmp directory
            with open(uploaded_file_path, "wb") as fh:
                fh.write(decoded_data)
            # Get file content to send to S3
            with open(uploaded_file_path, 'rb') as f:
                file_content = f.read()
        except Exception as e:
            print(str(traceback.format_exc()))
            return {
                'statusCode': 417,
                'body': json.dumps(generate_response("exception_msg"))
            }

        # This function calculate digest for content to use to comapre files content
        content_digest = get_file_content_digest(uploaded_file_path)

        check_content_status, old_file_key = check_content(content_digest, bucket_name)
        # If same content and different rename file name to the new one.
        if check_content_status and old_file_key != final_file_name:
            copy_source = bucket_name + '/' + old_file_key
            s3.Object(bucket_name, final_file_name).copy_from(CopySource=copy_source)
            s3.Object(bucket_name, old_file_key).delete()
        # Put object in S3 and add content digest in metadata
        else:
            s3.Bucket(bucket_name).put_object(Key=final_file_name, Body=file_content,
                                              Metadata={'content-digest': content_digest})

        return {
            'statusCode': 200,
            'body': json.dumps(generate_response("file_uploaded_succ"))
        }

    except Exception as e:
        print(str(traceback.format_exc()))
        return {
            'statusCode': 417,
            'body': json.dumps(generate_response("exception_msg"))
        }


def get_file_content_digest(f_path):
    h = hashlib.md5()
    with open(f_path, 'rb') as file:
        # make content in blocks to make memory optimization
        block = file.read(512)
        while block:
            h.update(block)
            block = file.read(512)

    return h.hexdigest()


def decode_file_base64(file_string_full):
    file_base64_prefix = file_string_full.find('base64,')
    file_string_prefix = file_string_full[:file_base64_prefix]
    file_string_prefix_ = file_string_prefix.find('data:')
    file_string_prefix = file_string_prefix[file_string_prefix_ + 5:]
    file_string_prefix = file_string_prefix[:-1]

    file_extension = guess_extension(file_string_prefix)

    file_string_postfix = file_string_full[file_base64_prefix + 7:]
    return [file_extension, file_string_postfix]


# This way need to enhancement and optimization to be scalable, but this issue need more time to dig deep in S3 to
# find a better way to check content similar
def check_content(content_digest, bucket):
    old_file_key = ''
    s3_client = boto3.client("s3")
    contents = s3_client.list_objects_v2(Bucket=bucket).get('Contents')
    if contents:
        for content in contents:
            meta_data_content_digest = content.get('ETag').replace('"', '')
            old_file_key = content.get('Key')
            if meta_data_content_digest == content_digest:
                return [True, old_file_key]
    return [False, old_file_key]


def generate_response(message_key):
    messages = {
        "file_uploaded_succ": "File Uploaded successfully",
        "file_name_required": "file_name is required",
        "file_base64_required": "file_base64 is required",
        "wrong_base64_encoding": "file_base64 field must start with eg: data:image/png;base64",
        "wrong_extension": "Make sure file_name extension the same as content extension",
        "exception_msg": "Something went wrong..."
    }
    response = {
        "message_key": message_key,
        "message": messages.get(message_key),
        "data": {}
    }
    return response
