import os
from typing import List

class Settings:
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Alternative React dev port
    ]
    
    # Add production frontend URL from environment variable
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    if FRONTEND_URL:
        CORS_ORIGINS.append(FRONTEND_URL)

settings = Settings()
