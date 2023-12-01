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

load_dotenv()


QUEUE_URL = os.environ.get("SQS_URL")

client = boto3.client('sqs')

stop = len(sys.argv) > 1 and sys.argv[1] == 'stop'

run = True

while run:
    if stop:
        
        run = False
    
    
    message = client.receive_message(QueueUrl=QUEUE_URL, WaitTimeSeconds=2)
    
    if message and 'Messages' in message and message['Messages']:

        try:
            # Parse the JSON
            records = ""
            object_key = ""
            bucket_name = os.environ.get("BUCKET_NAME")

            receipt_handle = message['Messages'][0]['ReceiptHandle']
            body =  json.loads(message['Messages'][0]['Body'])
            
            object_key = body['Records'][0]['s3']['object']['key']
            filename = object_key.split('/')[-1]
            
            if object_key:
                s3 = boto3.resource('s3')
                
                image = s3.Object(bucket_name, object_key).get()
                metadata = image['Metadata']
                socketId = metadata.get("socketid")
                image = image['Body'].read()
                
                print(metadata)
                
                detections = getPredictionFromRoboflow(image)
                
                file = Image.open(io.BytesIO(image))

                newImage = labelImage(file, detections)
                newImage = Image.open(io.BytesIO(newImage))
                s3=boto3.client("s3")
                s3.upload_fileobj(
                    io.BytesIO(newImage),
                    bucket_name,
                    filename,
                    ExtraArgs={
                        "Metadata": {"socketId": socketId, "status": "uploaded"},
                    }
                )
                # Save image s3
                #s3.Bucket(bucket_name).put_object(Key=f'processed/{filename}', Body=newImage)
            
            
            # s3image.upload_file('new.jpg', bucket_name,
                     # f'small/{filename}',  extra_args={'ACL': 'public-read'}) 
            # print('imagen almacenada')
            
                url = f'{os.environ.get("API_URL")}/image/uploaded/'
                params = {"object_key": object_key}
                    
                req = requests.post(url, json=params)
            client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
            
        except Exception as e:
            print(e)
            client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle )
    
