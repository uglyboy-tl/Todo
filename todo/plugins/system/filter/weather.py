import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from loguru import logger

from todo.core import TodoItem, TodoTxt
from todo.project import BaseFilter, Option


@dataclass
class WeatherFilter(BaseFilter):
    regex: str = r"^晴天|阴天$"

    def __call__(self, todo: TodoItem, process):
        process(todo, Option.MODIFY_ALL)

    def modify_all(self, todo: TodoItem, todotxt: TodoTxt, process):
        weather = self._get_weather(todotxt)
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
            if self._no_weather_todo(todotxt, process):
                get_weather = TodoItem("@weather @done @#HIDDEN")
                process(get_weather, Option.FORMAT | Option.ADD | Option.EXECUTE)
            process(todo, Option.BREAK)
            process(todo, Option.EXECUTE)

    def _get_weather(self, todotxt: TodoTxt) -> Optional[TodoItem]:
        for todo in todotxt.search("#weather"):
            if todo.creation_date.date() == datetime.now().date():
                return todo
        return None

    def _no_weather_todo(self, todotxt: TodoTxt, process):
        """
        for todo in todotxt.search("weather"):
            if todo.due.date() == datetime.now().date():
                return False
        return True
        """
        new = None
        for todo in todotxt.search("weather"):
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


if __name__ == "__main__":
    todotxt = TodoTxt("data/todotest.txt")
    weather = WeatherFilter("weather")
    logger.debug(weather._get_weather(todotxt))
    logger.debug(weather._no_weather_todo(todotxt))
