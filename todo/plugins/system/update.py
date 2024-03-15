from dataclasses import dataclass
from datetime import datetime

from todo.core import TodoItem
from todo.project import BaseContext


@dataclass
class Update(BaseContext):
    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context and todo.due and todo.due.date() < datetime.now().date():
            todo.due = datetime.now()
