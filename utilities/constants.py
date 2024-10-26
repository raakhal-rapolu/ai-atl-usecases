import os
from dotenv import load_dotenv

load_dotenv()

gemini_url = os.environ.get('GEMINI_URL')
anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
gemini_api_key = os.environ.get("GEMINI_API_KEY")

db_password = os.environ.get('DB_PASSWORD')

db_user = os.environ.get('DB_USER')