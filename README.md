## Ahli Task

AWS Information:

    * S3 bucket: serverless-upload-file-20-01-2022
    * Lambda Functions Roles: LambdaToS3AndCloudWatch
    * Lambda Functions Roles Policies:
        * AWSLambdaBasicExecutionRole
        * LambdaToS3ReadCreateDeleteObj
    * API Gateway: Wshah-API, Invoke URL: https://rdql2qvwm3.execute-api.us-east-1.amazonaws.com
    * Lambda Functions: (working with python 3.8)
        * upload-file
        * read-file
        * delete-file
    * Lambda Layers:
        * python_layer (working with python 3.8)

###### **Testing Guide and information:**

I sent invitation to Motasem and Omar Email's

In case invitation not worked you can import collection in postman using this below link 

https://www.postman.com/collections/21669f91d6d23436f718

If above solution didn't work you can use cURL requests as following:

1. **Upload File**:
   1. URL: https://rdql2qvwm3.execute-api.us-east-1.amazonaws.com/file
   2. Method: POST
   3. Data-type: JSON
   4. JSON Params:
      1. file_name: string represent file name. eg: detect-loop-in-a-linked-list.png
      2. file_base64: base64 encoded string represent file content. eg: data:image/png;base64,iVBORw0KG... you can use this website to encode images (https://www.base64-image.de/)
   5. cURL request:

      `curl --location --request POST 'https://rdql2qvwm3.execute-api.us-east-1.amazonaws.com/file' \
--header 'Content-Type: application/json' \
--data-raw '{
    "file_name": "detect-loop-in-a-linked-list.png",
    "file_base64": "data:image/png;base64,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"
}'`
 
  
2. Read File:
   1. URL: https://rdql2qvwm3.execute-api.us-east-1.amazonaws.com/file
   2. Method: GET
   3. Data-type: JSON
   4. JSON Params:
      1. file_name: string represent file name. eg: detect-loop-in-a-linked-list.png
   5. cURL request:
      `curl --location --request GET 'https://rdql2qvwm3.execute-api.us-east-1.amazonaws.com/file' \
--header 'Content-Type: application/json' \
--data-raw '{
    "file_name": "detect-loop-in-a-linked-list.png"
}'`
   
3. Delete File
   1. URL: https://rdql2qvwm3.execute-api.us-east-1.amazonaws.com/file
   2. Method: DELETE
   3. Data-type: JSON
   4. JSON Params:
      1. file_name: string represent file name. eg: detect-loop-in-a-linked-list.png
   5. cURL request:
      `curl --location --request DELETE 'https://rdql2qvwm3.execute-api.us-east-1.amazonaws.com/file' \
--header 'Content-Type: application/json' \
--data-raw '{
    "file_name": "detect-loop-in-a-linked-list.png"
}'`


