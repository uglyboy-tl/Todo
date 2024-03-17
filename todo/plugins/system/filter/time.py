from dataclasses import dataclass
from datetime import datetime
from typing import List

from todo.core import TodoItem
from todo.project import BaseContext, Option


@dataclass
class TimeFilter(BaseContext):
    regex: str = r"^\d{2}:\d{2}-\d{2}:\d{2}$"

    def __call__(self, todo: TodoItem, process):
        if not self._check(todo.context):
            process(todo, Option.BREAK)

    def _check(self, contexts: List[str]):
        for context in contexts:
            if self.pattern.match(context):
                time_period = context
        if not time_period:
            return False
        # 解析时间段以获取开始时间和结束时间
        start_time_str, end_time_str = time_period.split("-")
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
        current_time = datetime.now().time()

        if start_time > end_time:
            return start_time <= current_time or current_time <= end_time
        else:
            return current_time >= start_time and current_time <= end_time
