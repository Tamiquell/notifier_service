from typing import Union
import requests
import base64

from fastapi import UploadFile, HTTPException, Response
from monolog.monolog import MongoLogger
from rocketchat_API.rocketchat import RocketChat

from src.models.message import MessageData
from src.services.messenger_interface import NotifierInterface
from config.config import settings


class RocketChatNotifier(NotifierInterface):

    def __init__(self) -> None:
        self.rocket = RocketChat(
            user=settings.ROCKET.BOT_NAME,
            password=settings.ROCKET.PASSWORD,
            server_url=settings.ROCKET.SERVER_URL,
        )
        self.POST_URL = settings.ROCKET.SERVER_URL + "/api/v1/chat.postMessage"
        self.AUTH_TOKEN = settings.ROCKET.AUTH_TOKEN
        self.BOT_USER_ID = settings.ROCKET.BOT_USER_ID

    async def send_message(self,
                           msg: MessageData,
                           logger: MongoLogger = None) -> Response:
        '''Send message to user'''

        text = ''
        if msg.title:
            text += msg.title + '\n'
        text += msg.text
        if msg.author:
            text += '\n' + 'send by \'' + msg.author + '\''
        await logger.info('RocketChatNotifier.send_message')
        response = self.rocket.chat_post_message(
            channel=msg.destination, text=text)
        if response.status_code in [400, 404]:
            raise HTTPException(
                status_code=400, detail='Wrong channel(chat) name or wrong input format')
        return Response(response.text, response.status_code)

    async def send_file(self,
                        destination: Union[str, int],
                        author: Union[str, None] = None,
                        file: Union[UploadFile, None] = None,
                        logger: MongoLogger = None) -> Response:
        '''Send message with files to user'''

        target_file = await file.read()
        file_data = base64.b64encode(target_file).decode()
        file_name = file.filename

        if file_name.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
        ):
            await logger.info('RocketChatNotifier.send_file')
            attachment = {
                "image_url": f"data:image/jpeg;base64,{file_data}",
                "type": "image/png",
                "title": "Image title",
                "description": "Image description"
            }

            # Define the post message payload
            caption = ''
            if author:
                caption = 'send by: ' + author
            payload = {
                "channel": f"#{destination}",
                "text": caption,
                "attachments": [attachment]
            }

            # Send the post message request with the attachment
            response = requests.post(
                self.POST_URL,
                json=payload,
                headers={
                    "X-Auth-Token": self.AUTH_TOKEN,
                    "X-User-Id": self.BOT_USER_ID}
            )
        else:
            # raise HTTPException(
            #     status_code=501, detail='Method does not work with text files yet')
            # add text file to attachment
            attachment = {
                "file_url": f"data:text/plain;base64,{file_data}",
                # "text": f"data:text/plain;base64,{file_data}",
                "type": "text/plain",
                "title": "Text file title",
                "description": "Text file description"
            }

            payload = {
                "channel": "#test_rocket_bot_public",
                "text": "Notifying with text file",
                # "attachments": [attachment]

            }

            response = requests.post(
                self.POST_URL,
                json=payload,
                files=[{"file": file}],
                headers={
                    "Content-Type": "multipart/form-data",
                    "X-Auth-Token": self.AUTH_TOKEN,
                    "X-User-Id": self.BOT_USER_ID
                }
            )
        if response.status_code == 400:
            raise HTTPException(
                status_code=400, detail='Bad Request')
        if response.status_code == 404:
            raise HTTPException(
                status_code=404, detail='Wrong chat_id')

        return Response(response.text, response.status_code)
