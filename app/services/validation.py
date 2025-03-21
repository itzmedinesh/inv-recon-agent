def create_prompt(invoice_id, customer_id, subscription_id, customer_email):
    return f"""
    You are an AI assistant specializing in document processing and data validation. Extract and validate the following fields:
    - Invoice ID: {invoice_id}
    - Customer ID: {customer_id}
    - Subscription ID: {subscription_id}
    - Customer Email ID: {customer_email}

    Generate a JSON validation report:
    {{
       "matched_fields": {{
           "Invoice ID": "value",
           "Customer ID": "value",
           "Subscription ID": "value",
           "Customer Email ID": "value"
       }},
       "mismatched_fields": {{}},
       "missing_fields": []
    }}
    """