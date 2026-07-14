import os
from pathlib import Path

FRONTEND_ORIGINS = [
    os.getenv('FRONTEND_URL', 'http://localhost:5173'),
    'http://127.0.0.1:5173',
]
AUTH_SECRET_KEY = os.getenv('AUTH_SECRET_KEY', 'library-management-secret')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))
PASSWORD_ITERATIONS = int(os.getenv('PASSWORD_ITERATIONS', '100000'))
PRIVILEGED_REGISTRATION_CODE = os.getenv('PRIVILEGED_REGISTRATION_CODE')
REPORTS_DIR = str(Path(__file__).resolve().parents[1] / 'reports')
