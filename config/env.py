from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(".env")

# Accessing variables
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
ENVIRONMENT = os.getenv('ENVIRONMENT')
PROJECT_ID = os.getenv('PROJECT_ID')

