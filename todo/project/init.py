import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from todo.core import TodoItem, TodoTxt

from .context import BaseContext
from .schema import Option


@dataclass
class Init(BaseContext):
    due_with_unfinished: bool = False
    alert_days: int = 0

    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context:
            process(todo, Option.MODIFY_ALL)

    def modify_all(self, todo: TodoItem, todotxt: TodoTxt, process):
        # 优先级A的未完成任务执行脚本
        if self.due_with_unfinished:
            if not self._check("unfinished", todotxt):
                due_script = self._fetch("unfinished", todotxt, process)
                if due_script and due_script.due.date() != datetime.now().date():
                    due_script.due = datetime.now()
                    process(due_script, Option.EXECUTE)
                elif not due_script:
                    due_script = TodoItem("@unfinished @done @#HIDDEN", due=datetime.now())
                    process(due_script, Option.FORMAT | Option.ADD | Option.EXECUTE)
                due_script.recurrence = "1d"
                due_script.priority = "A"
        else:
            due_script = self._fetch("unfinished", todotxt, process)
            if due_script:
                process(due_script, Option.REMOVE)

        # 代办提醒脚本
        if self.alert_days:
            if not self._check("alert", todotxt):
                alert_script = self._fetch("alert", todotxt, process)
                if alert_script and alert_script.due.date() != datetime.now().date():
                    alert_script.due = datetime.now()
                    process(alert_script, Option.EXECUTE)
                elif not alert_script:
                    alert_script = TodoItem("@alert @done @#HIDDEN", due=datetime.now())
                    process(alert_script, Option.FORMAT | Option.ADD | Option.EXECUTE)
                alert_script.recurrence = "1d"
        else:
            alert_script = self._fetch("alert", todotxt, process)
            if alert_script:
                process(alert_script, Option.REMOVE)

    # 检查脚本是否已经执行过
    def _check(self, script: str, todotxt: TodoTxt) -> bool:
        for todo in todotxt.search(script, completed=True):
            if todo.due.date() == datetime.now().date():
                return True
        return False

    # 获取最新脚本，如果有多个脚本，删除多余的脚本
    def _fetch(self, script: str, todotxt: TodoTxt, process) -> Optional[TodoItem]:
        new = None
        for todo in todotxt.search(script):
            if todo.completed:
                continue
            elif new is None:
                new = todo
            elif todo.due.date() < new.due.date():
                process(todo, Option.REMOVE)
            else:
                process(new, Option.REMOVE)
                new = todo
        return new


@dataclass
class SysInit(Init):
    archive_recurrence: str = ""

    def modify_all(self, todo: TodoItem, todotxt: TodoTxt, process):
        # 优先级A的归档脚本
        if self.archive_recurrence:
            pattern = re.compile(r"\d+[dwmy]")
            assert pattern.match(self.archive_recurrence), "Invalid archive due format"
            archive_script = self._fetch("archive", todotxt, process)
            if archive_script:
                archive_script.priority = "A"
                archive_script.recurrence = self.archive_recurrence
            else:
                archive_script = TodoItem(
                    "@archive @done @#HIDDEN", priority="A", recurrence=self.archive_recurrence, due=datetime.now()
                )
                process(archive_script, Option.FORMAT | Option.ADD | Option.EXECUTE)
        else:
            archive_script = self._fetch("archive", todotxt, process)
            if archive_script:
                process(archive_script, Option.FORMAT | Option.REMOVE)
        super().modify_all(todo, todotxt, process)