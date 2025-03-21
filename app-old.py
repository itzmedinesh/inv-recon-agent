import json
import os
import re
import boto3
import docx
import pymupdf
import requests
from botocore.exceptions import NoCredentialsError, EndpointConnectionError, ClientError, ParamValidationError
from flask import Flask, request, jsonify, render_template
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from werkzeug.utils import secure_filename

app = Flask(__name__)

template = "You are an intelligent assistant. Answer the following question based on the following context: {context} Question: {question}"
prompt = PromptTemplate(input_variables=["context", "question"], template=template)

# Initialize Amazon Bedrock client
bedrock_client = boto3.client(
    'bedrock-runtime',
    aws_access_key_id='ASIA2UC3AHR7JIRK5GD5',
    aws_secret_access_key='yA+gNAJddoJtKpB63hS2kYD4FGSbdzaEWSblBwPC',
    aws_session_token='FwoGZXIvYXdzEF0aDAA+RyQe+nEKIHgZPSKqAWnX/leGeGcpch7njnKuwNyMQYQMO7gRXCoVaEyREOYAWmJAa/9LXfqwRl7GX22133agPF59ihjAFaJg6lh11vSlzyDW7Q1V7EvFWUIRQ8929HYO0RVszdVHo3cBCKiK9ZmdoFLYI0zb7p8cRW5H6SaXmFrBcxNsGtwbjB+u9ttyOdbLzUZTwMwODxdLBNiwxqFoE3aQlWAazPf3W2Xz0feyrcCcnPtgKC07KPmS9b4GMi2PNdIXiEK5hR1XjKVHOrh2S4GXCIaT3zxS1aIRBy1jDQyNlN3oCibBhn4wXRQ=',
    region_name='us-east-1'
)

def get_bedrock_response(context, question):
    try:
        response = bedrock_client.invoke_model(
            body=json.dumps({
                'messages': [
                    {'role': 'user', 'content': [{'text':f'Context: {context} Question: {question}'}]}
                ]
            }),
            modelId='amazon.nova-pro-v1:0',
            accept='application/json',
            contentType='application/json',
        )
        result = json.loads(response['body'].read())
        return result['output']['message']['content'][0]['text']
    except AttributeError as e:
        print(f"AttributeError: {e}")
    except NoCredentialsError:
        print("Error: No AWS credentials provided.")
    except EndpointConnectionError as e:
        print(f"EndpointConnectionError: {e}")
    except ClientError as e:
        print(f"ClientError: {e}")
    except ParamValidationError as e:
        print(f"ParamValidationError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


@app.route('/invoice-reconcilation/<path:invoiceid>', methods=['POST'])
def parse_invoice(invoiceid: str):
    invoiceurl = request.json.get('downloadUrl')

    if invoiceurl is None:
        return jsonify({'error': 'No invoice url provided'})
    else:
        print(invoiceurl)
    pdf_content =  download_pdf(invoiceurl)
    pdf_type = process_invoice(pdf_content)
    
    
    print(f"Pdf type : {pdf_type}")

    return jsonify({'status': 'success', 'invoiceurl': invoiceurl})

def download_pdf(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")
        return None

def process_invoice(pdf_content):
    """Determines if a PDF contains text, images, or both."""
    doc = pymupdf.open(stream=pdf_content, filetype="pdf")

    has_text = False

    patterns = {
        "Invoice ID": r"Invoice\s*#\s*[-–—]\s*(\d+)",  # Extracts Invoice number
        "Customer ID": r"Customer ID\s*[-–—]\s*([\w\d]+)",  # Extracts Customer ID (single word)
        "Customer Email ID": r"([\w.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",  # Extracts email address
        "Subscription ID": r"SUBSCRIPTION\s+ID\s*[-–—]\s*([\w\d]+)"  # Ensures only Subscription ID is extracted
    }
    
    extracted_data = {}

    text = ""

    for page in doc:
        text+=page.get_text()
        
    if text.strip():
        has_text = True
            
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            extracted_data[key] = match.group(1) if match else None
                
        final_prompt = create_prompt(extracted_data["Invoice ID"], extracted_data["Customer ID"], extracted_data["Subscription ID"], extracted_data["Customer Email ID"])
            
        response = get_bedrock_response(text, final_prompt)
        print(extract_json_from_response(response))
            
    # Determine PDF type
    if has_text:
        return "T"
    else:
        return "E"


def extract_json_from_response(response_text):
    """Extracts JSON content from an LLM response text."""
    match = re.search(r"```json\n([\s\S]+?)\n```", response_text)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)  # Convert to a dictionary
        except json.JSONDecodeError:
            print("Error: Extracted JSON is not valid")
            return None
    else:
        print("Error: No JSON found in response")
        return None

def create_prompt(invoice_id, customer_id, subscription_id, customer_email):
    invoice_validation_prompt = """
    You are an AI assistant specializing in document processing and data validation. Your task is to extract and validate key details from the attached invoice PDF.

    Instructions:
    1. Extract the following fields exactly as they appear in the PDF:
       - Invoice ID
       - Customer ID
       - Subscription ID
       - Customer Email ID

    2. Compare the extracted values against the expected values provided below:

       Expected Values:
       - Invoice ID: {invoice_id}
       - Customer ID: {customer_id}
       - Subscription ID: {subscription_id}
       - Customer Email ID: {customer_email}

    3. Generate a validation report using the following structure:

    {{
       "matched_fields": {{
           "Invoice ID": "value" (if matched),
           "Customer ID": "value" (if matched),
           "Subscription ID": "value" (if matched),
           "Customer Email ID": "value" (if matched)
       }},
       "mismatched_fields": {{
           "Invoice ID": {{"expected": "{invoice_id}", "extracted": "value_if_different"}},
           "Customer ID": {{"expected": "{customer_id}", "extracted": "value_if_different"}},
           "Subscription ID": {{"expected": "{subscription_id}", "extracted": "value_if_different"}},
           "Customer Email ID": {{"expected": "{customer_email}", "extracted": "value_if_different"}}
       }},
       "missing_fields": ["List of missing fields if any"]
    }}

    4. Validation Rules:
       - Extract values exactly as they appear in the PDF.
       - Ignore formatting differences (e.g., `abc@example.com` vs `ABC@EXAMPLE.COM` should be considered a match).
       - If a field is missing, state it explicitly.
       - Do not infer or guess values—only validate what is present.

    Now, process the attached invoice PDF and return the validation report.
    """

    return invoice_validation_prompt.format(
        invoice_id=invoice_id,
        customer_id=customer_id,
        subscription_id=subscription_id,
        customer_email=customer_email
    )


if __name__ == '__main__':
    app.run(debug=True)