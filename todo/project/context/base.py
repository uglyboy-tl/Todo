import re
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from todo.core import TodoItem


@dataclass
class BaseContext(metaclass=ABCMeta):
    name: str
    regex: Optional[str] = field(init=False, default=None)
    pattern: Optional[re.Pattern] = field(init=False, default=None)

    def __post_init__(self):
        if self.regex is not None:
            self.pattern = re.compile(self.regex)

    def match(self, contexts: List[str]) -> bool:
        if self.name in contexts:
            return True
        elif self.pattern is not None:
            for context in contexts:
                if self.pattern.match(context):
                    return True
        return False

    @abstractmethod
    def __call__(self, todo: TodoItem, process: Callable[[TodoItem, int], TodoItem] = lambda x: x):
        pass
