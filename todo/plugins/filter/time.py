from dataclasses import dataclass
from datetime import datetime

from todo.project import BaseFilter


@dataclass
class TimeFilter(BaseFilter):
    regex: str = r"^(?:[01]\d|2[0-3]):[0-5]\d-(?:[01]\d|2[0-3]):[0-5]\d$"

    def _check(self, _, matched_context: str):
        # 解析时间段以获取开始时间和结束时间
        start_time_str, end_time_str = matched_context.split("-")
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
        current_time = datetime.now().time()

        if start_time > end_time:
            return start_time <= current_time or current_time <= end_time
        else:
            return current_time >= start_time and current_time <= end_time
