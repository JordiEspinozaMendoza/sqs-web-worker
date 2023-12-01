from dotenv import load_dotenv
import boto3
import json
import sys
import os 
import requests

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
                url = f'{os.environ.get("API_URL")}/image/uploaded/'
                print(object_key)
                params = {"object_key": object_key}
                
                req = requests.post(url, json=params)
                print(req.text) 
            

            
            # s3image.upload_file('new.jpg', bucket_name,
                     # f'small/{filename}',  extra_args={'ACL': 'public-read'}) 
            # print('imagen almacenada')
            
            client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
            
        except Exception as e:
            print(e)
            client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle )
    
