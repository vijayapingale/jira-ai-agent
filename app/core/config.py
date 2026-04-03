"""
Application configuration and settings
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://user:pass@localhost/jira_ai"
    
    # Jira
    jira_url: str = ""
    jira_username: str = ""
    jira_api_token: str = ""
    
    # AI/ML
    openai_api_key: str = ""
    model_name: str = "gpt-4"
    
    # Vector DB
    vector_db_url: str = ""
    
    class Config:
        env_file = ".env"


settings = Settings()
