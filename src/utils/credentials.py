from abc import ABC, abstractmethod

from loguru import logger

from config.env import PRIVATE_KEY


class Credentials(ABC):
    @abstractmethod
    def set(self):
        pass

    @abstractmethod
    def get(self):
        pass


class CredentialsEnv(Credentials):

    def __init__(self):
        self._private_key = None

    def set(self):
        try:
            self._private_key = PRIVATE_KEY
        except Exception as e:
            logger.error(f"Something went wrong Error: {e}")

    def get(self):
        if self._private_key is None:
            self.set()
            return self._private_key
        else:
            return self._private_key
