import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    """Configuration settings for the application."""
    
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
    AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

    # Add any other configuration parameters here

# Load the config
config = Config()
