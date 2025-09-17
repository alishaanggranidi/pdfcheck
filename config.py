import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Simple settings class using environment variables directly"""
    
    def __init__(self):
        # Google Gemini API
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        
        # Langfuse Configuration
        self.langfuse_public_key = os.getenv("LF_PUBLIC_KEY", "")
        self.langfuse_secret_key = os.getenv("LF_SECRET_KEY", "")
        self.langfuse_host = os.getenv("LF_HOST", "https://api.langfuse.com")
        
        # Application Configuration
        self.app_name = os.getenv("APP_NAME", "PDF_Validator_Agent")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # PDF Processing Configuration
        self.min_signatures = int(os.getenv("MIN_SIGNATURES", "3"))
        self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "10"))

settings = Settings()
