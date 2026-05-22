from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str

    # Automatically loads variables from a .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()