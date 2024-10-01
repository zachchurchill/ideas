from abc import ABCMeta, abstractmethod
from typing import List


class Secret(metaclass=ABCMeta):
    @property
    @abstractmethod
    def user(self) -> str:
        """Provide username for secret"""

    @property
    @abstractmethod
    def pwd(self) -> str:
        """Provide encoded password for secret"""

    @abstractmethod
    def show_pwd(self) -> str:
        """Provide raw password for secret"""


class GenericSecret(Secret):

    def __init__(self, usr, pwd):
        self._usr = usr
        self._pwd = pwd

    @property
    def user(self) -> str:
        return self._usr

    @property
    def pwd(self) -> str:
        return "*" * len(self._pwd)

    def show_pwd(self) -> str:
        return self._pwd


class DbSecret(GenericSecret):

    def __init__(self, usr, pwd, connection_string):
        super().__init__(usr, pwd)
        self._conn = connection_string

    @property
    def conn_str(self) -> str:
        return self._conn


class SecretStore:

    def __init__(self):
        self._secrets: List[Secret] = []

    @property
    def secrets(self) -> List[Secret]:
        return self._secrets

    # TODO see if I can use metaprogramming to create `add` methods for each secret type