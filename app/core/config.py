from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Football API"
    API_KEY: str
    DATABASE_URL: str
    SECRET_KEY: Optional[str] = None
    REDIS_URL: Optional[str] = None

    # .env ဖိုင်ကနေ အလိုအလျောက် ဖတ်ခိုင်းခြင်း
    # extra="ignore" ထည့်ခြင်းဖြင့် class ထဲမှာမပါတဲ့ env variables တွေကြောင့် crash မဖြစ်အောင် ကာကွယ်ပေးသည်
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()