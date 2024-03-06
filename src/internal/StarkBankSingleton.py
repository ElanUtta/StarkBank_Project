from abc import ABC, abstractmethod
from typing import Optional, Union

import starkbank
from starkcore import Project, Organization

from config.env import ENVIROMENT, PROJECT_ID
from src.utils import CredentialsEnv
from src.utils import Credentials


class StarkBank(ABC):
    @abstractmethod
    def initialize_project(self, credentials: Credentials):
        pass


class StarkBankSingleton(StarkBank):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.client = cls._instance.initialize_project(*args, **kwargs)
        return cls._instance

    def initialize_project(self, credentials: Credentials):
        project = starkbank.Project(
            environment=ENVIROMENT,
            id=PROJECT_ID,
            private_key=credentials.get()
        )

        starkbank.user = project
        return starkbank


def get_client() -> StarkBankSingleton:
    credentials = CredentialsEnv()
    return StarkBankSingleton(credentials)

