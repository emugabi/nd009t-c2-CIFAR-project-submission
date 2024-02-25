########################################################
###### imageserialiser-model-workflow-project ##########
########################################################

import json
import os
import boto3
import base64
from botocore.exceptions import ClientError

def download_data(s3_input_uri):
    s3 = boto3.client('s3')
    input_bucket = s3_input_uri.split('/')[0]
    input_object = '/'.join(s3_input_uri.split('/')[1:])
    file_name = '/tmp/' + os.path.basename(input_object)
    s3.download_file(input_bucket, input_object, file_name)
    return file_name

def lambda_handler(event, context):
    """ A function to serialise the data from s3"""
    
    print("Event: ", event.keys())
    
    bucket = event["s3_bucket"]
    key = event["s3_key"]
    uri = "/".join([bucket, key])
    print("attempting to download ", uri)
    saved_file = download_data(uri)
    print("saved file to ", saved_file)
        
    # Download data from s3 to /tmp/image.png
    with open(saved_file, "rb") as f:
        image_data = base64.b64encode(f.read())
    
    
    return {
        'statusCode': 200,
        'body': {
            'image_data' : image_data,
            's3_bucket' : bucket,
            's3_key' : key,
            'inferences' : []
        }
    }


########################################################
###### inferenceThreshold-model-workflow ###############
########################################################

import json
import boto3
import base64

THRESHOLD = .93

def lambda_handler(event, context):
    """ A function to serialise the data from s3"""
    
    inferences = event["inferences"] 
    
    meets_threshold = inferences[0] >= THRESHOLD
    
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")
    
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }


#########################################################
###### images_classifly-model-workflow-project ##########
#########################################################

import json
import boto3
import base64
import array
#import sagemaker
#from sagemaker.serializers import IdentitySerializer

def lambda_handler(event, context):
    """ A function to serialise the data from s3"""
    
    print("Event: ", event.keys())
    
    image = base64.b64decode(event["image_data"])
    
    runtime = boto3.client("sagemaker-runtime")
    
    endpoint_name="image-classification-2024-02-24-17-39-08-767"
    
    content_type = "image/png"
    
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType=content_type,
        Body=image
    )
    

    inferences = json.loads(response["Body"].read())
    
    print(inferences)
    event["inferences"] = (inferences)
    
    return {
        'statusCode': 200,
        'body': (event)
    }
