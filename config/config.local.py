from pydantic import BaseModel


class TelegramBot(BaseModel):
    BOT_TOKEN: str = ''
    BOT_NAME: str = ''
    WEBHOOK_PATH: str = ''
    WEBHOOK_HOST: str = ''


class RocketChatBot(BaseModel):
    BOT_NAME: str = ''
    PASSWORD: str = ''
    SERVER_URL: str = ''
    AUTH_TOKEN: str = ''
    BOT_USER_ID: str = ''


class WebApp(BaseModel):
    WEB_APP_HOST: str = '127.0.0.1'
    WEB_APP_PORT: int = 8000


class RedisDB(BaseModel):
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ''
    REDIS_DB: int = 0
    RATE_LIMIT: int = 3
    TIME_IN_SECONDS = 60 * 5


class Settings(BaseModel):
    BOT: TelegramBot = TelegramBot()
    ROCKET: RocketChatBot = RocketChatBot()
    WEB_APP: WebApp = WebApp()
    REDIS: RedisDB = RedisDB()
    PROJECT_NAME: str = 'herald'


settings = Settings()
