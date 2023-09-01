from abc import ABC, abstractmethod
from typing import Union
from fastapi import UploadFile, Response

from monolog.monolog import MongoLogger

from src.models.message import MessageData


class NotifierInterface(ABC):
    @abstractmethod
    async def send_message(self,
                           msg: MessageData,
                           logger: MongoLogger = None) -> Response:
        '''Send message to user'''
        pass

    @abstractmethod
    async def send_file(self,
                        destination: Union[str, int],
                        author: Union[str, None] = None,
                        file: Union[UploadFile, None] = None,
                        logger: MongoLogger = None) -> Response:
        '''Send message with files to user'''
        pass
