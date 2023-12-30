import json
import boto3
import base64
import uuid

_s3 = boto3.client('s3')
    

def process_image(s3_uri):
    bucket, key = s3_uri.split('/',2)[-1].split('/',1)
    s3_response = _s3.get_object(
        Bucket=bucket,
        Key=key
    )
    content = json.loads(s3_response.get('Body').read().decode())
    image = content["artifacts"][0]["base64"]
    image_decoded = base64.b64decode(image)
    image_file_name = "{}.png".format(str(uuid.uuid4()))
    image_file_path = "/tmp/{}".format(image_file_name)
    image_file = open(image_file_path, 'wb')
    image_file.write(image_decoded)
    image_file.close()    
    print(image_file_path, bucket, image_file_name)
    return image_file_path, bucket, image_file_name
    

def upload_to_s3(file_path, bucket, key):
    _s3.upload_file(file_path, bucket, key)
    presigned_url = _s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=3600
    )

    return presigned_url

def handler(event, context):
    print(event)
    title = event["title"]
    description = event["description"]
    image = event["image"]
    local_file_path, bucket, key = process_image(image)
    presigned_url = upload_to_s3(local_file_path, bucket, key)
    response = {"title":title,"description":description,"image":presigned_url}
    return response
