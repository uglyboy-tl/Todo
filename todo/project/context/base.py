from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from todo.core import TodoItem


@dataclass
class BaseContext(metaclass=ABCMeta):
    name: str

    @abstractmethod
    def __call__(self, todo: TodoItem):
        pass
