from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from .base import BaseContext


@dataclass
class BaseNotify(BaseContext, metaclass=ABCMeta):
    id: str

    def __post_init__(self):
        self._validate(self.id)

    @staticmethod
    @abstractmethod
    def _validate(id: str):
        pass
