from dataclasses import dataclass
from datetime import datetime, timedelta

from todo.core import TodoItem, TodoTxt
from todo.project import BaseContext, BasePreparation, Option


@dataclass
class Unfinished(BaseContext):
    handle_expired: bool = True
    alert_days: int = 1

    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context:
            process(todo, Option.MODIFY_ALL)

    def modify_all(self, _: TodoItem, todotxt: TodoTxt, process):
        for todo in todotxt:
            if todo.completed:
                continue
            in_alert_days = self._in_alert_days(todo)
            if self._need_execute(todo, process) and (not todo.due or in_alert_days):
                process(todo, Option.EXECUTE)
            elif self.handle_expired and todo.due and todo.due.date() < datetime.now().date() and todo.context:
                process(todo, Option.EXECUTE)
            elif todo.due and in_alert_days and todo.message and "#HIDDEN" not in todo.context:
                diff = todo.due.date() - datetime.now().date()
                notify = TodoItem(f"距离：`{todo.message.strip()}` 还有{diff.days}天 @notify")
                process(notify, Option.EXECUTE)

    def _need_execute(self, todo: TodoItem, process):
        type_list = process(todo, Option.TYPE)
        for context in type_list:
            if isinstance(context, BasePreparation):
                return True
        return False

    def _in_alert_days(self, todo: TodoItem):
        if not todo.due:
            return True
        if self.alert_days <= 0:
            return False
        today = datetime.now().date()
        due = todo.due.date()
        return due > today and due <= today + timedelta(days=self.alert_days)
