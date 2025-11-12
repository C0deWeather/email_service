from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # RabbitMQ Settings
    RABBITMQ_HOST: str
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    
    # Redis Settings
    REDIS_HOST: str
    REDIS_PORT: int
    
    # Email (MailHog) Settings
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    EMAIL_SENDER: str

    class Config:
        # This tells Pydantic to load from environment variables
        env_file = '.env'
        env_file_encoding = 'utf-8'

# Create a single, reusable instance of the settings
settings = Settings()