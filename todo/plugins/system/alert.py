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
            if todo.completed:
                continue
            in_alert_days = self._in_alert_days(todo)
            if self._need_execute(todo) and (not todo.due or in_alert_days):
                process(todo, Option.EXECUTE)
            elif todo.due and in_alert_days and todo.message and "#HIDDEN" not in todo.context:
                diff = todo.due.date() - datetime.now().date()
                notify = TodoItem(f"距离：`{todo.message.strip()}` 还有{diff.days}天 @notify")
                process(notify, Option.EXECUTE)

    def _need_execute(self, todo: TodoItem):
        return any(
            True for context in todo.context if context in self.active_scripts and f"#{context}" not in todo.context
        )

    def _in_alert_days(self, todo: TodoItem):
        today = datetime.now().date()
        due = todo.due.date()
        return due > today and due <= today + timedelta(days=self.alert_days)
