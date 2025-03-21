import os
import boto3
from flask import Flask, json, request, jsonify, render_template
from config import config

from botocore.exceptions import NoCredentialsError, EndpointConnectionError, ClientError, ParamValidationError

def get_bedrock_client():
    return boto3.client(
        'bedrock-runtime',
        aws_access_key_id=config.AWS_ACCESS_KEY,
        aws_secret_access_key=config.AWS_SECRET_KEY,
        aws_session_token=config.AWS_SESSION_TOKEN,
        region_name=config.AWS_REGION
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
