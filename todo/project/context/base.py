from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Callable

from todo.core import TodoItem


@dataclass
class BaseContext(metaclass=ABCMeta):
    name: str

    @abstractmethod
    def __call__(self, todo: TodoItem, process: Callable[[TodoItem, int], TodoItem] = lambda x: x):
        pass
