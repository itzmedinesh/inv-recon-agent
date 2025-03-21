from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.routes import invoice_routes
    app.register_blueprint(invoice_routes)
    return app