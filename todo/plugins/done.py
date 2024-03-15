from dataclasses import dataclass

from todo.core import TodoItem
from todo.project import BaseContext, Option


@dataclass
class Done(BaseContext):
    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context:
            process(todo, Option.DONE)
