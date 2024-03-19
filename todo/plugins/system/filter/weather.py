import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from todo.core import TodoItem
from todo.project import BaseFilter, Option


@dataclass
class WeatherFilter(BaseFilter):
    regex: str = r"^晴天|阴天$"

    def __call__(self, todo: TodoItem, process):
        weather = self._get_weather(process)
        weather_filter = None
        for context in todo.context:
            if self.pattern.match(context):
                weather_filter = context
        if not weather_filter:
            return
        if weather is not None:
            if not self._check(weather, weather_filter):
                process(todo, Option.BREAK)
        else:
            if self._no_weather_todo(process):
                get_weather = TodoItem("@weather @done @#HIDDEN +SYSTEM")
                process(get_weather, Option.ADD | Option.EXECUTE)
            process(todo, Option.BREAK)
            process(todo, Option.EXECUTE)

    def _get_weather(self, process) -> Optional[TodoItem]:
        for todo in process(TodoItem("@#weather"), Option.SEARCH):
            if todo.creation_date.date() == datetime.now().date():
                return todo
        return None

    def _no_weather_todo(self, process):
        new = None
        for todo in process(TodoItem("@weather"), Option.SEARCH):
            if todo.completed:
                continue
            elif new is None:
                new = todo
            elif todo.due.date() < new.due.date():
                process(todo, Option.REMOVE)
            else:
                process(new, Option.REMOVE)
                new = todo
        if not new:
            return True
        new.due = datetime.now()
        return False

    def _check(self, todo: TodoItem, weather_filter: str):
        pattern = re.compile(r"^今日天气: (.*)。")
        weather = pattern.search(todo.description).group(1)
        if weather_filter == weather:
            return True
        return False
