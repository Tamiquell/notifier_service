from fastapi import HTTPException

from src.models.message import MessageData
from src.services.telegram_notifier.telegram_messenger import TelegramNotifier
from src.services.rocket_chat_notifier.rocket_chat_messenger import (
    RocketChatNotifier
)


class Factory:
    '''
    Factory class for creating messenger objects
    '''

    def __init__(self, service: str = 'telegram') -> None:
        self.messenger = None
        self.service_name = service.lower()

    def get_messenger(self):
        '''
        Returns messenger object
        '''
        if self.service_name == 'telegram':
            self.messenger = TelegramNotifier()
        elif self.service_name == 'rocket_chat':
            self.messenger = RocketChatNotifier()
        else:
            raise HTTPException(
                status_code=400,
                detail=f'No such service: {self.service_name}')
        return self.messenger
