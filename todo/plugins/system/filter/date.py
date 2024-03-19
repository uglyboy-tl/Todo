import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib import error, request

from loguru import logger

from todo.core import TodoItem, TodoTxt
from todo.project import BaseFilter, Option

HOLIDAY_URL = "https://timor.tech/api/holiday/info/{}"
HEADERS = {"User-Agent": "Mozilla/5.0 3578.98 Safari/537.36"}


@dataclass
class DateFilter(BaseFilter):
    regex: str = r"^holiday|workday$"

    def __call__(self, todo: TodoItem, process):
        process(todo, Option.MODIFY_ALL)

    def modify_all(self, todo: TodoItem, todotxt: TodoTxt, process):
        if not self._check(todo.context, self._get_holiday(todotxt), process):
            process(todo, Option.BREAK)

    def _check(self, contexts: list[str], data: Optional[str], process):
        date_filter = None
        for context in contexts:
            if self.pattern.match(context):
                date_filter = context
        if not date_filter:
            return False
        if not data:
            try:
                url = request.Request(HOLIDAY_URL.format(datetime.now().strftime("%Y-%m-%d")), headers=HEADERS)
                with request.urlopen(url) as response:
                    data = response.read().decode("utf-8")
                    logger.trace(f"请求成功: {data}")
                    holiday_data = TodoItem(f"{data} @#holiday @#HIDDEN")
                    holiday_data.done()
                    process(holiday_data, Option.FORMAT | Option.ADD)
            except error.URLError as e:
                logger.error(f"URL错误: {e.reason}")
                return False
            except Exception as e:
                logger.error(f"请求失败: {e}")
                return False
        obj = json.loads(data)
        if date_filter == "workday":
            return obj["type"]["type"] in [0, 3]
        elif date_filter == "holiday":
            return obj["type"]["type"] in [1, 2]
        else:
            response = obj["holiday"]
            return response is not None and date_filter == response["name"]

    def _get_holiday(self, todotxt: TodoTxt) -> Optional[str]:
        for todo in todotxt.search("#holiday"):
            if todo.creation_date.date() == datetime.now().date():
                return todo.message
        return None
