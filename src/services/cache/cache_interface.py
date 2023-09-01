from abc import ABC, abstractmethod


class Cache(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get(self, key: str) -> str:
        pass

    @abstractmethod
    def set(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def request_is_limited(self, key: str) -> bool:
        pass
