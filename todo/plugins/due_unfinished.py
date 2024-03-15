from dataclasses import dataclass
from datetime import datetime

from todo.core import TodoItem, TodoTxt
from todo.project import BaseContext, Option


@dataclass
class DueUnfinished(BaseContext):
    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context:
            process(todo, Option.MODIFY_ALL)

    def modify_all(self, _: TodoItem, todotxt: TodoTxt, process):
        for todo in todotxt:
            if not todo.completed and todo.due and todo.due.date() < datetime.now().date():
                process(todo, Option.EXECUTE)
        process(todo, Option.DONE)
