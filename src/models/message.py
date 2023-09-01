# from pydantic import BaseModel
from pydantic import BaseModel
import json
from typing import Union, Literal


class MessageData(BaseModel):
    service: Literal['telegram', 'rocket_chat']
    text: str
    destination: Union[int, str]
    title: Union[str, None] = None
    author: Union[str, None] = None

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    class Config:
        schema_extra = {
            'example': {
                'service': 'telegram',
                'text': 'Someone accessed your security code! Change it quickly!!!',
                'destination': -829479897,
                'title': 'Critical issue',
                'author': 'Security office',
            }
        }
