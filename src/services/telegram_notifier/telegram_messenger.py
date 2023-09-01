from typing import Union

import httpx
import requests
from fastapi import UploadFile, HTTPException, Response
from monolog.monolog import MongoLogger

from src.models.message import MessageData
from src.helpers.exception import InvalidFileFormat
from src.services.messenger_interface import NotifierInterface
from config.config import settings


class TelegramNotifier(NotifierInterface):

    def __init__(self) -> None:
        self.client = httpx.AsyncClient()
        self.TELEGRAM_BOT_TOKEN = settings.BOT.BOT_TOKEN
        self.TEXT_URL = 'https://api.telegram.org/bot' + \
            str(self.TELEGRAM_BOT_TOKEN) + '/sendMessage'
        self.PHOTO_URL = 'https://api.telegram.org/bot' + \
            str(self.TELEGRAM_BOT_TOKEN) + '/sendPhoto'
        self.DOCUMENT_URL = 'https://api.telegram.org/bot' + \
            str(self.TELEGRAM_BOT_TOKEN) + '/sendDocument'

    async def send_message(self,
                           msg: MessageData,
                           logger: MongoLogger = None) -> Response:
        '''
        Takes MessageData type parameter with logger and send message 
        to telegram in the following format:
         - Title
         - Some notification text
         - send by Author
        '''

        text = ''
        if msg.title:
            text += msg.title + '\n'
        text += msg.text
        if msg.author:
            text += '\n' + 'send by \'' + msg.author + '\''

        tg_msg = {'chat_id': str(msg.destination),
                  'text': text,
                  'parse_mode': 'Markdown'}

        await logger.info('TelegramNotifier.send_message')
        response = await self.client.post(self.TEXT_URL, data=tg_msg)
        if response.status_code in [400, 404]:
            raise HTTPException(
                status_code=400, detail='Wrong chat_id or wrong input format')
        return Response(response.text, response.status_code)

    async def send_file(self,
                        destination: Union[str, int],
                        author: Union[str, None] = None,
                        file: Union[UploadFile, None] = None,
                        logger: MongoLogger = None) -> Response:
        await logger.info('TelegramNotifier.send_file')
        file_name = file.filename
        try:
            target_file = await file.read()
        except:
            raise InvalidFileFormat('Invalid file format')

        caption = ''
        if author:
            caption = 'send by: ' + author

        if file_name.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
        ):
            response = requests.post(
                self.PHOTO_URL,
                data={'chat_id': str(destination),
                      'caption': caption},
                files={'photo': target_file})
        else:
            response = requests.post(
                self.DOCUMENT_URL,
                data={'chat_id': str(destination),
                      'filename': f'{file_name}',
                      'caption': caption,
                      'parse_mode': 'Markdown'},
                files={'document': target_file})
        if response.status_code == 400:
            raise HTTPException(
                status_code=400, detail='Bad Request')
        if response.status_code == 404:
            raise HTTPException(
                status_code=404, detail='Wrong chat_id')
        return Response(response.text, response.status_code)
