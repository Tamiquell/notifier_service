import httpx
import requests
from typing import List, Optional, Union
from multiprocessing import current_process

from fastapi import Form, UploadFile, File, APIRouter
from fastapi import UploadFile, Response, HTTPException
from fastapi.responses import JSONResponse
from monolog.monolog import MongoLogger

from src.models.message import MessageData
from src.services.factory import Factory
from config.config import settings
from src.handlers.tg_response_messages import start_message
from src.helpers.exception import CannotParseTheInputData
from src.services.cache.cache_redis import RedisCache

import time
router = APIRouter()


client = httpx.AsyncClient()

cache = RedisCache(host=settings.REDIS.REDIS_HOST,
                   port=settings.REDIS.REDIS_PORT,
                   rate_limit=settings.REDIS.RATE_LIMIT,
                   time_in_seconds=settings.REDIS.TIME_IN_SECONDS)


@router.on_event('startup')
async def startup_event():
    response = setwebhook()
    logger = MongoLogger(__name__, current_process())
    if response.status_code == 200:
        await logger.info('Webhook has been set successfully')
    else:
        await logger.error('Webhook has not been set')
        raise HTTPException(status_code=500,
                            detail='Webhook has not been set')


@router.post('/notify_with_text', tags=['notify'])
async def notify_with_text(messageData: MessageData) -> Response:
    start = time.perf_counter()
    logger = MongoLogger(__name__, current_process())

    await logger.info(f'/{notify_with_text.__name__} triggered')
    try:
        messageData = MessageData(**messageData)
    except:
        raise CannotParseTheInputData('Cannot parse the input data')
    messenger = Factory(messageData.service).get_messenger()

    redis_key = ':'.join(
        [messageData.service, str(messageData.destination), messageData.text])
    redis_key = hash(redis_key)
    if cache.request_is_limited(redis_key):
        await logger.info('Request is limited')
        return JSONResponse(status_code=429,
                            content={
                                'message': 'Can\'t send more than 3 same messages within 5 minutes'},
                            )

    await logger.info('Send text message')
    response = await messenger.send_message(messageData, logger)
    await logger.info(f'Get response with status code: {response.status_code}')

    return Response(content='Text has been sent successfully',
                    status_code=response.status_code,
                    headers={'content-type': 'text'},
                    )


@router.post('/notify_with_files', tags=['notify'])
async def notify_with_files(service: str = Form(example={'service': 'telegram'}),
                            destination: Union[str, int] = Form(...),
                            text: str = Form(
                                example={'text': 'some text notification'}),
                            title: str = Form(None),
                            author: str = Form(None),
                            files: Optional[List[UploadFile]] = File(None)
                            ) -> Response:
    start = time.perf_counter()
    logger = MongoLogger(__name__, current_process())

    await logger.info(f'/{notify_with_files.__name__} triggered')

    try:
        messageData = MessageData(
            service=service,
            text=text,
            destination=destination,
            title=title,
            author=author)
    except:
        raise CannotParseTheInputData('Cannot parse the input data')
    messenger = Factory(messageData.service).get_messenger()

    redis_key = ':'.join(
        [messageData.service, str(messageData.destination), messageData.text])
    redis_key = hash(redis_key)
    if cache.request_is_limited(redis_key):
        await logger.info('Request is limited')
        return JSONResponse(status_code=429,
                            content={
                                'message': 'Can\'t send more than 3 same messages within 5 minutes'},
                            )

    # send files
    for file in files or []:
        response = await messenger.send_file(
            messageData.destination,
            messageData.author,
            file,
            logger
        )

    await logger.info(
        f'execution time of files message = {time.perf_counter() - start}')

    # send text
    await logger.info('Send text message')

    response = await messenger.send_message(messageData, logger)
    await logger.info(f'Get response with status code: {response.status_code}')

    if response.status_code == 400:
        raise HTTPException(
            status_code=400, detail='Bad Request')
    if response.status_code == 404:
        raise HTTPException(
            status_code=404, detail='Wrong chat_id')

    await logger.info(f'total execution time = {time.perf_counter() - start}')

    return Response(
        content='Files have been sent successfully',
        status_code=response.status_code,
        headers={'content-type': 'text'},
    )


def setwebhook() -> Response:
    '''This function is used to set webhook for telegram bot'''
    url = f'{settings.BOT.WEBHOOK_HOST}{settings.BOT.WEBHOOK_PATH}'
    token = settings.BOT.BOT_TOKEN
    s = requests.get(
        f'https://api.telegram.org/bot{token}/setWebhook?url={url}')

    if s:
        return Response(content='Webhook has been set successfully',
                        status_code=s.status_code)
    else:
        return Response(content='Webhook can\'t be set',
                        status_code=s.status_code)


def sendmessage(chatid: int, text: str) -> None:
    '''This function is used to send messages to telegram'''
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(
        settings.BOT.BOT_TOKEN)
    payload = {
        'text': text,
        'chat_id': chatid
    }
    _ = requests.post(url, params=payload)


@router.post('/', tags=['parse_message'])
async def parse_message(body: dict) -> None:
    ''' This function is used to parse messages from telegram'''
    try:
        user_input = body['message']['text']
        if user_input.endswith(settings.BOT.BOT_NAME):
            at = user_input.find('@')
            user_input = user_input[:at]
        chat_id = body['message']['chat']['id']

        if user_input == '/start':
            sendmessage(chat_id, start_message)
        elif user_input == '/my_id':
            user_id = body['message']['from']['id']
            sendmessage(chat_id, f'Your id is: {user_id}')
        elif user_input == '/group_id':
            if body['message']['chat']['type'] == 'group':
                group_id = body['message']['chat']['id']
                sendmessage(chat_id, f'This group id is: {group_id}')
            else:
                user_id = body['message']['from']['id']
                sendmessage(
                    chat_id, 'You can\'t use this method outside of chat-group'
                )
    except:  # if there is no text key, we just ignore it
        pass
