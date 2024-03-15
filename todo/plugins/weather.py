import json
from dataclasses import dataclass
from typing import Optional
from urllib import error, parse, request

from loguru import logger

from todo.core import TodoItem
from todo.project import BaseContext, Option

WEATHER_URL = "https://{}wttr.in/{}?format=j1"


@dataclass
class Weather(BaseContext):
    language: str = "zh"
    location: Optional[str] = None

    def __call__(self, todo: TodoItem, process):
        subdomain: str = f"{self.language}." if self.language != "en" else ""
        location: str = self.location or ""
        try:
            with request.urlopen(WEATHER_URL.format(subdomain, parse.quote(location))) as response:
                content = response.read().decode("utf-8")
                data = json.loads(content)
            weather = f"今日天气: {data['current_condition'][0]['lang_zh'][0]['value']}。"
            weather += f"气温：{data['weather'][0]['mintempC']}°C-{data['weather'][0]['maxtempC']}°C，现在温度：{data['current_condition'][0]['temp_C']}°C，风力：{data['current_condition'][0]['windspeedKmph']}km/h\n"

            notify = TodoItem(weather)
            notify.add_context("notify")
            process(notify, Option.FORMAT | Option.ADD | Option.EXECUTE)
            process(todo, Option.DONE)
        except error.URLError as e:
            logger.error(f"URL错误: {e.reason}")
        except Exception as e:
            logger.error(f"请求失败: {e}")
