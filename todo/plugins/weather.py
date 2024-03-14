from dataclasses import dataclass
from typing import Optional
from urllib import error, request

from loguru import logger

from todo.core import TodoItem, TodoTxt
from todo.project import BaseContext

WEATHER_URL = "https://{}wttr.in/{}?format=%C+%t+%w"


@dataclass
class Weather(BaseContext):
    language: str = "zh"
    location: Optional[str] = None

    def __call__(self, todo: TodoItem, todotxt: TodoTxt, format=lambda x, _: x):
        subdomain: str = f"{self.language}." if self.language != "en" else ""
        location: str = self.location or ""
        try:
            with request.urlopen(WEATHER_URL.format(subdomain, location)) as response:
                content = response.read().decode("utf-8")
            notify = TodoItem(content)
            notify.add_context("notify")
            format(notify, 1)
            todotxt.done(todo)
        except error.URLError as e:
            logger.error(f"URL错误: {e.reason}")
        except Exception as e:
            logger.error(f"请求失败: {e}")
