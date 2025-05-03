import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Settings application
SECRET_KEY = os.getenv('SECRET_KEY')

# Settings database
BASE_DIR = Path(__file__).parent / 'database'
BASE_DIR.mkdir(exist_ok = True, parents = True)

DB_BASE_URL = os.getenv('DB_BASE_URL')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'app_parking')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

try:
    if os.environ['TERM_PROGRAM'] == 'vscode':
        database = f"{DB_BASE_URL}:///{BASE_DIR}/{DB_NAME}"
except Exception:
    database = f"{DB_BASE_URL}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
