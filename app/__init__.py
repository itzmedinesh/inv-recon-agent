from flask import Flask
from app.routes import invoice_routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(invoice_routes, url_prefix='/invoice-reconciliation')
    return app

