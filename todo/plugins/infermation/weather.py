import json
from dataclasses import dataclass
from typing import Optional
from urllib import parse

from todo.core import TodoItem
from todo.project import Option

from .webhook import Webhook

WEATHER_URL = "https://{}wttr.in/{}?format=j1"


@dataclass
class Weather(Webhook):
    url: str = WEATHER_URL
    language: str = "zh"
    location: Optional[str] = None
    notify: bool = False

    def __post_init__(self):
        subdomain: str = f"{self.language}." if self.language != "en" else ""
        location: str = self.location or ""
        self.url = self.url.format(subdomain, parse.quote(location))

    def _process(self, content: str, process):
        data = json.loads(content)
        weather = f"今日天气: {data['current_condition'][0]['lang_zh'][0]['value']}。"
        weather += f"气温：{data['weather'][0]['mintempC']}°C-{data['weather'][0]['maxtempC']}°C，现在温度：{data['current_condition'][0]['temp_C']}°C，风力：{data['current_condition'][0]['windspeedKmph']}km/h\n"

        if self.notify:
            notify = TodoItem(f"{weather.strip()} @#weather @notify @done")
            process(notify, Option.FORMAT | Option.ADD | Option.EXECUTE)
        else:
            notify = TodoItem(f"{weather.strip()} @#weather @#HIDDEN")
            notify.done()
            process(notify, Option.FORMAT | Option.ADD)
