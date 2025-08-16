"""
Simple configuration for Zhen's AI representative.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Simple application configuration."""
    
    # Database Configuration
    DB_URL: str = os.getenv("DB_URL", "postgresql://zhen_bot_user:your_password@localhost:5432/zhen_bot_production")
    
    # Google API Configuration
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # ADK Configuration
    ADK_MODEL: str = "gemini-2.0-flash"
    APP_NAME: str = "Zhen's AI Representative"
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        if not cls.DB_URL:
            raise ValueError("DB_URL environment variable is required")

# Global config instance
config = Config()
