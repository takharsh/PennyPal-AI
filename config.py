import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'pennypal-ai-secure-secret-key-2026-btech-project')
    
    # MySQL Database Config
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'pennypal_ai')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Gemini AI API Config
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
