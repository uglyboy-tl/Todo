from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Union

from todo.core import TodoItem


@dataclass
class BaseContext(metaclass=ABCMeta):
    name: str

    def match(self, contexts: List[str]) -> bool:
        if self.name in contexts:
            return True
        return False

    @abstractmethod
    def __call__(
        self, todo: TodoItem, process: Callable[[TodoItem, int], Union[TodoItem, List[TodoItem]]] = lambda x: x
    ):
        pass

    def modify_all(
        self, todo: TodoItem, todotxt, process: Callable[[TodoItem, int], Union[TodoItem, List[TodoItem]]] = lambda x: x
    ):
        return
