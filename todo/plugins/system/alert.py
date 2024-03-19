from dataclasses import dataclass
from datetime import datetime, timedelta

from todo.core import TodoItem, TodoTxt
from todo.project import BaseContext, Option


@dataclass
class Alert(BaseContext):
    days: int = 1

    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context:
            process(todo, Option.MODIFY_ALL)

    def modify_all(self, _: TodoItem, todotxt: TodoTxt, process):
        for todo in todotxt:
            if (
                not todo.completed
                and todo.due
                and todo.due.date() > datetime.now().date()
                and todo.due.date() <= datetime.now().date() + timedelta(days=self.days)
            ):
                if todo.message and "#HIDDEN" not in todo.context:
                    diff = todo.due.date() - datetime.now().date()
                    notify = TodoItem(f"距离：`{todo.message.strip()}` 还有{diff.days}天 @notify")
                    process(notify, Option.EXECUTE)
