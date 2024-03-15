from dataclasses import dataclass

from todo.core import TodoItem, TodoTxt
from todo.project import BaseContext, Option


@dataclass
class Archive(BaseContext):
    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context:
            process(todo, Option.MODIFY_ALL)

    def modify_all(self, todo: TodoItem, todotxt: TodoTxt, process):
        process(todo, Option.DONE)
        todotxt.archive()
