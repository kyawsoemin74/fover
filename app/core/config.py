from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Football API"
    API_KEY: str
    DATABASE_URL: str

    # .env ဖိုင်ကနေ အလိုအလျောက် ဖတ်ခိုင်းခြင်း
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()