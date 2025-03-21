import pymupdf
import re
from app.utils.regex_patterns import patterns
from app.services.aws_client import get_bedrock_response
from app.utils.json_parser import extract_json_from_response
from app.services.validation import create_prompt

def process_invoice(pdf_content):
    doc = pymupdf.open(stream=pdf_content, filetype="pdf")
    text = "".join([page.get_text() for page in doc])

    extracted_data = {key: (match.group(1) if (match := re.search(pattern, text)) else None) for key, pattern in patterns.items()}

    final_prompt = create_prompt(
        extracted_data["Invoice ID"],
        extracted_data["Customer ID"],
        extracted_data["Subscription ID"],
        extracted_data["Customer Email ID"]
    )

    response = get_bedrock_response(text, final_prompt)
    return extract_json_from_response(response)
