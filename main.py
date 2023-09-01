import uvicorn
from fastapi import FastAPI

from src.handlers.api import router as api_router
from config.config import settings


app = FastAPI()

app.include_router(api_router)


if __name__ == '__main__':

    uvicorn.run('main:app', host=settings.WEB_APP.WEB_APP_HOST,
                port=settings.WEB_APP.WEB_APP_PORT,
                log_level='info',
                reload=True)
