from flask import Flask
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Flask application
app = Flask(__name__)

from backend import routes
