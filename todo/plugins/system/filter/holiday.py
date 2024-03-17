import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib import error, request

from loguru import logger

from todo.core import TodoItem
from todo.project import BaseContext, Option

HOLIDAY_URL = "https://timor.tech/api/holiday/info/{}"
HEADERS = {"User-Agent": "Mozilla/5.0 3578.98 Safari/537.36"}


@dataclass
class HolidayFilter(BaseContext):
    check: str = "holiday"

    def __call__(self, todo: TodoItem, process):
        if not self._check(todo.due):
            todo.due += timedelta(days=1)
            process(todo, Option.BREAK)

    def _check(self, time: datetime):
        try:
            url = request.Request(HOLIDAY_URL.format(time.strftime("%Y-%m-%d")), headers=HEADERS)
            with request.urlopen(url) as response:
                content = response.read().decode("utf-8")
                data = json.loads(content)
                logger.trace(f"请求成功: {data}")
            if self.check == "workday":
                return data["type"]["type"] in [0, 3]
            elif self.check == "holiday":
                return data["type"]["type"] in [1, 2]
            else:
                response = data["holiday"]
                return response is not None and response["name"] == self.check
        except error.URLError as e:
            logger.error(f"URL错误: {e.reason}")
        except Exception as e:
            logger.error(f"请求失败: {e}")
