from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from loguru import logger

from todo.core import TodoItem, TodoTxt
from todo.project import BaseFilter, Option


@dataclass
class WeatherFilter(BaseFilter):
    regex: str = r"^\d{5}$"

    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context:
            process(todo, Option.MODIFY_ALL)

    def modify_all(self, todo: TodoItem, todotxt: TodoTxt, process):
        weather = self._get_weather(todotxt)
        if weather is not None:
            if not self._check(weather):
                process(todo, Option.BREAK)
        else:
            if self._no_weather_todo(todotxt):
                get_weather = TodoItem("@weather @done +SYSTEM")
                process(get_weather, Option.ADD)
                process(get_weather, Option.EXECUTE)
            process(todo, Option.BREAK)
            process(todo, Option.EXECUTE)

    def _get_weather(self, todotxt: TodoTxt) -> Optional[TodoItem]:
        for todo in todotxt.search("#weather"):
            if todo.creation_date.date() == datetime.now().date():
                return todo
        return None

    def _no_weather_todo(self, todotxt: TodoTxt):
        for todo in todotxt.search("weather"):
            if todo.creation_date.date() == datetime.now().date():
                return False
        return True

    def _check(self, weather: TodoItem):
        return False


if __name__ == "__main__":
    todotxt = TodoTxt("data/todotest.txt")
    weather = WeatherFilter("weather")
    logger.debug(weather._get_weather(todotxt))
    logger.debug(weather._no_weather_todo(todotxt))
