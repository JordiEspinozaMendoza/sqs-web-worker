from dotenv import load_dotenv
import boto3
import json
import sys
import os 
import requests
from PIL import Image
import io
from utils.images import labelImage
from utils.utils import getPredictionFromRoboflow
import base64

load_dotenv()


QUEUE_URL = os.environ.get("SQS_URL")

client = boto3.client('sqs')

stop = len(sys.argv) > 1 and sys.argv[1] == 'stop'

run = True

print("Waiting to poll messages")

        
while run:
    if stop:
        
        run = False
    message = client.receive_message(QueueUrl=QUEUE_URL, WaitTimeSeconds=2)
    
    if message and 'Messages' in message and message['Messages']:

        try:
            records = ""
            object_key = ""
            bucket_name = os.environ.get("BUCKET_NAME")

            receipt_handle = message['Messages'][0]['ReceiptHandle']
            body =  json.loads(message['Messages'][0]['Body'])
            
            object_key = body['Records'][0]['s3']['object']['key']
            filename = object_key.split('/')[-1]
            
            if object_key:
                s3 = boto3.resource('s3')
                s3Client = boto3.client("s3")
                
                imageResponse = s3.Object(bucket_name, object_key).get()
                metadata = imageResponse['Metadata']
                socketId = metadata.get("socketid")
                status = metadata.get("status")
                image_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"

                if status is None:
                    requestImage = requests.get(image_url, stream=True)
                    requestImage.raw.decode_content = True
                    
                    if requestImage.status_code == 200:
                        file_image = Image.open(requestImage.raw)
                        
                        if file_image:
                            detections = getPredictionFromRoboflow(image_url)
                            
                            newImage = labelImage(file_image, detections)
    
                            response = s3Client.upload_fileobj(
                                io.BytesIO(newImage),
                                bucket_name,
                                filename,
                                ExtraArgs={
                                    "ContentType": file_image.format,
                                    "Metadata": {"socketId": socketId, "status": "uploaded"},
                                }
                            )

                    else:
                        print(f"Error: Unable to fetch image from {image_url}. Status code: {requestImage.status_code}")
                else:
                    url = f'{os.environ.get("API_URL")}/image/uploaded/'
                    params = {"object_key": object_key, "url": image_url,"socketId": socketId}
                        
                    req = requests.post(url, json=params)
                    
            client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)

            
        except Exception as e:
            error = str(e)

            print(error, sys.exc_info()[-1].tb_lineno)
            client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
    
