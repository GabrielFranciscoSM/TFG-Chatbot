import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot:8080")
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME", "tfg_chatbot")
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


settings = Settings()
