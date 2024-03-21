from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional

from todo.core import TodoItem, TodoTxt

from ..schema import Option
from .base import BaseContext


@dataclass
class BaseInit(BaseContext):
    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context:
            process(todo, Option.MODIFY_ALL)

    # 处理预设脚本
    def _update_preset_todo(
        self,
        name: str,
        condition: bool,
        todotxt: TodoTxt,
        process: Callable,
        need_execute_today: bool = True,
        preset: Optional[TodoItem] = None,
    ):
        if not preset:
            preset = TodoItem("Preset", priority="A", recurrence="1d")
        if condition:
            if not self._is_script_completed_today(name, todotxt):
                script = self._find_newest_todo(name, todotxt, process)
                if script and not (need_execute_today and script.due.date() == datetime.now().date()):
                    if need_execute_today:
                        script.due = datetime.now()
                        process(script, Option.EXECUTE)
                elif not script:
                    script = TodoItem(f"@{name} @done @#HIDDEN", due=datetime.now())
                    process(script, Option.FORMAT | Option.ADD | Option.EXECUTE)
                script.priority = preset.priority
                script.recurrence = preset.recurrence
        else:
            script = self._find_newest_todo(name, todotxt, process)
            if script:
                process(script, Option.REMOVE)

    # 检查脚本是否已经执行过
    def _is_script_completed_today(self, name: str, todotxt: TodoTxt) -> bool:
        for todo in todotxt.search(name, completed=True):
            if todo.due.date() == datetime.now().date():
                return True
        return False

    # 获取最新脚本，如果有多个脚本，删除多余的脚本
    def _find_newest_todo(self, name: str, todotxt: TodoTxt, process) -> Optional[TodoItem]:
        newest = None
        for todo in todotxt.search(name):
            if todo.completed:
                continue
            elif newest is None:
                newest = todo
            elif todo.due.date() < newest.due.date():
                process(todo, Option.REMOVE)
            else:
                process(newest, Option.REMOVE)
                newest = todo
        return newest
