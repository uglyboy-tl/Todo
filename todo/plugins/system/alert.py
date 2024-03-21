from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from todo.core import TodoItem, TodoTxt
from todo.project import BaseContext, Option


@dataclass
class Alert(BaseContext):
    alert_days: int = 1
    active_scripts: List[str] = field(default_factory=list)

    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context:
            process(todo, Option.MODIFY_ALL)

    def modify_all(self, _: TodoItem, todotxt: TodoTxt, process):
        for todo in todotxt:
            if (
                not todo.completed
                and todo.due
                and todo.due.date() > datetime.now().date()
                and todo.due.date() <= datetime.now().date() + timedelta(days=self.alert_days)
            ):
                if any(True for context in todo.context if context in self.active_scripts):
                    process(todo, Option.EXECUTE)
                elif todo.message and "#HIDDEN" not in todo.context:
                    diff = todo.due.date() - datetime.now().date()
                    notify = TodoItem(f"距离：`{todo.message.strip()}` 还有{diff.days}天 @notify")
                    process(notify, Option.EXECUTE)
