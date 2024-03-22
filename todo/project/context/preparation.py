from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from todo.core import TodoItem

from ..schema import Option
from .base import BaseContext


@dataclass
class BasePreparation(BaseContext, metaclass=ABCMeta):
    notify: bool = True
    message: str = "{}"

    def __call__(self, todo: TodoItem, process):
        assert self.name in todo.context
        if self.notify and todo.due and todo.message and "#HIDDEN" not in todo.context:
            diff = todo.due.date() - datetime.now().date()
            if diff.days > 0:
                notify = TodoItem(f"距离：`{todo.message.strip()}` 还有{diff.days}天 @notify")
                process(notify, Option.EXECUTE)
            elif diff.days == 0:
                notify = TodoItem(f"{self.message.format(todo.message.strip())} @notify")
                process(notify, Option.EXECUTE)
        if f"#{self.name}" in todo.context:
            return
        else:
            self._process(todo, process)

    @abstractmethod
    def _process(self, todo: TodoItem, process):
        todo.add_context(f"#{self.name}")
