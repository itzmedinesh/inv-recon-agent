from flask import Blueprint, request, jsonify
from app.services.invoice_processor import process_invoice
from app.utils.pdf_utils import download_pdf

invoice_routes = Blueprint('invoice_routes', __name__)

@invoice_routes.route('/', methods=['POST'])
def parse_invoice():
    invoice_url = request.json.get('downloadUrl')

    if not invoice_url:
        return jsonify({'error': 'No invoice URL provided'}), 400

    pdf_content = download_pdf(invoice_url)
    pdf_type = process_invoice(pdf_content)

    return jsonify({'status': 'success', 'invoice_url': invoice_url, 'pdf_type': pdf_type})
