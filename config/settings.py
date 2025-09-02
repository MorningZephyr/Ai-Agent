"""
Configuration management for the AI Representative System.
Handles environment variables, validation, and default values.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Settings:
    """
    Configuration settings for the AI Representative System.
    
    This class manages all environment variables and configuration
    with proper validation and default values.
    """
    
    # Database Configuration
    db_url: str
    
    # Google AI Configuration
    google_api_key: str
    
    # Application Configuration
    app_name: str = "AI_Representative_System"
    model_name: str = "gemini-2.0-flash"
    
    # Session Configuration
    default_communication_style: str = "friendly"
    
    # Logging Configuration
    log_level: str = "INFO"
    debug_mode: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
    
    def _validate_config(self) -> None:
        """
        Validate that all required configuration is present and valid.
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        # Validate required fields
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        if not self.db_url:
            raise ValueError("DB_URL environment variable is required")
        
        # Validate API key format (basic check)
        if len(self.google_api_key) < 10:
            raise ValueError("GOOGLE_API_KEY appears to be invalid (too short)")
        
        # Validate database URL format
        if not self.db_url.startswith(("postgresql://", "sqlite://")):
            raise ValueError("DB_URL must be a valid PostgreSQL or SQLite URL")
        
        # Validate model name
        valid_models = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
        if self.model_name not in valid_models:
            raise ValueError(f"Model must be one of: {', '.join(valid_models)}")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_log_levels)}")
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """
        Create Settings instance from environment variables.
        
        Returns:
            Settings instance with values from environment
            
        Raises:
            ValueError: If required environment variables are missing
        """
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # Get required environment variables
        google_api_key = os.getenv("GOOGLE_API_KEY")
        db_url = os.getenv("DB_URL", "postgresql://zhen_bot_user:your_password@localhost:5432/zhen_bot")
        
        # Provide helpful error message if GOOGLE_API_KEY is missing
        if not google_api_key:
            print("⚠️  GOOGLE_API_KEY not found in environment variables.")
            print("💡 Please set your Google AI API key:")
            print("   - Create a .env file in the project root")
            print("   - Add: GOOGLE_API_KEY=your_actual_api_key")
            print("   - Or set it as an environment variable")
            print("   - You can get an API key from: https://aistudio.google.com/app/apikey")
            print(f"   - Current working directory: {os.getcwd()}")
            print(f"   - .env file exists: {os.path.exists('.env')}")
        
        # Get optional environment variables with defaults
        app_name = os.getenv("APP_NAME", "AI_Representative_System")
        model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
        default_communication_style = os.getenv("DEFAULT_COMMUNICATION_STYLE", "friendly")
        log_level = os.getenv("LOG_LEVEL", "INFO")
        debug_mode = os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")
        
        return cls(
            db_url=db_url,
            google_api_key=google_api_key,
            app_name=app_name,
            model_name=model_name,
            default_communication_style=default_communication_style,
            log_level=log_level,
            debug_mode=debug_mode
        )
    
    def to_dict(self) -> dict:
        """
        Convert settings to dictionary for logging/debugging.
        
        Returns:
            Dictionary representation of settings (with sensitive data masked)
        """
        return {
            "db_url": self._mask_sensitive_data(self.db_url),
            "google_api_key": self._mask_sensitive_data(self.google_api_key),
            "app_name": self.app_name,
            "model_name": self.model_name,
            "default_communication_style": self.default_communication_style,
            "log_level": self.log_level,
            "debug_mode": self.debug_mode
        }
    
    def _mask_sensitive_data(self, value: str) -> str:
        """
        Mask sensitive data for logging purposes.
        
        Args:
            value: The value to mask
            
        Returns:
            Masked version of the value
        """
        if not value:
            return ""
        
        if len(value) <= 8:
            return "*" * len(value)
        
        # Show first 4 and last 4 characters, mask the middle
        return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"
    
    def get_database_config(self) -> dict:
        """
        Get database configuration for connection.
        
        Returns:
            Dictionary with database connection parameters
        """
        return {
            "db_url": self.db_url,
            "app_name": self.app_name
        }
    
    def get_ai_config(self) -> dict:
        """
        Get AI model configuration.
        
        Returns:
            Dictionary with AI model parameters
        """
        return {
            "model_name": self.model_name,
            "google_api_key": self.google_api_key
        }
    
    def is_development(self) -> bool:
        """
        Check if running in development mode.
        
        Returns:
            True if in development mode
        """
        return self.debug_mode or self.log_level.upper() == "DEBUG"
    
    def is_production(self) -> bool:
        """
        Check if running in production mode.
        
        Returns:
            True if in production mode
        """
        return not self.is_development()


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings instance (creates one if it doesn't exist)
    """
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment variables.
    
    Returns:
        New Settings instance
    """
    global _settings
    _settings = Settings.from_env()
    return _settings


def validate_environment() -> bool:
    """
    Validate that the environment is properly configured.
    
    Returns:
        True if environment is valid, False otherwise
    """
    try:
        settings = Settings.from_env()
        print("✅ Environment configuration is valid")
        print(f"   📊 App: {settings.app_name}")
        print(f"   🤖 Model: {settings.model_name}")
        print(f"   🗄️ Database: {settings._mask_sensitive_data(settings.db_url)}")
        print(f"   🔑 API Key: {settings._mask_sensitive_data(settings.google_api_key)}")
        print(f"   🐛 Debug Mode: {settings.debug_mode}")
        return True
    except ValueError as e:
        print(f"❌ Environment configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error validating environment: {e}")
        return False


if __name__ == "__main__":
    # Test configuration when run directly
    print("🔧 Testing AI Representative System Configuration")
    print("=" * 60)
    
    if validate_environment():
        print("\n🎉 Configuration test passed!")
        settings = get_settings()
        print(f"\n📋 Configuration Summary:")
        for key, value in settings.to_dict().items():
            print(f"   {key}: {value}")
    else:
        print("\n❌ Configuration test failed!")
        print("\n💡 Make sure you have:")
        print("   - GOOGLE_API_KEY environment variable set")
        print("   - DB_URL environment variable set (or use default)")
        print("   - .env file in the project root (optional)")
