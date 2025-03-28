import os
import boto3
import botocore.session
from flask import Flask, json, request, jsonify, render_template
from config import config

from botocore.exceptions import NoCredentialsError, EndpointConnectionError, ClientError, ParamValidationError

def get_bedrock_client():
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    session = boto3.Session(region_name=region)
    sts_client = session.client("sts")

    assumed_role = sts_client.assume_role(
        RoleArn="arn:aws:iam::730335296638:role/microcrafts.sandbox",
        RoleSessionName="InvReconSession"
    )
    
    assumed_session = boto3.Session(
        aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
        aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
        aws_session_token=assumed_role["Credentials"]["SessionToken"],
        region_name=region
    )
    
    return assumed_session.client(
        'bedrock-runtime',
        region_name=os.environ['AWS_REGION']
    )

def get_bedrock_response(context, question):
    bedrock_client = get_bedrock_client()
    try:
        response = bedrock_client.invoke_model(
            body=json.dumps({
                'messages': [{'role': 'user', 'content': [{'text': f'Context: {context} Question: {question}'}]}]
            }),
            modelId='amazon.nova-pro-v1:0',
            accept='application/json',
            contentType='application/json',
        )
        result = json.loads(response['body'].read())
        return result['output']['message']['content'][0]['text']
    except (NoCredentialsError, EndpointConnectionError, ClientError, ParamValidationError, Exception) as e:
        print(f"Error: {e}")
        return None
