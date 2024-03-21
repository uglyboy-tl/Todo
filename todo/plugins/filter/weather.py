import re
from dataclasses import dataclass

from todo.project import BaseFilter


@dataclass
class WeatherFilter(BaseFilter):
    regex: str = r"^晴天|小雨$"
    data_name: str = "#Weather"
    script_name: str = "fetch_weather"

    def _check(self, weather: str, weather_filter: str):
        pattern = re.compile(r"^今日天气: (.*)。")
        weather = pattern.search(weather).group(1)
        if weather_filter == weather:
            return True
        return False
