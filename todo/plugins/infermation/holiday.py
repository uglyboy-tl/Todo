import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from todo.core import TodoItem
from todo.project import Option

from .webhook import Webhook

HOLIDAY_URL = "https://timor.tech/api/holiday/info/{}"


@dataclass
class Holiday(Webhook):
    url: str = HOLIDAY_URL
    language: str = "zh"
    location: Optional[str] = None
    notify: bool = False

    def __post_init__(self):
        self.url = self.url.format(datetime.now().strftime("%Y-%m-%d"))

    def _process(self, content: str, process):
        data = json.loads(content)
        obj = {
            "name": data.get("holiday", {}).get("name", ""),
            "type": data["type"]["type"],
        }

        holiday_data = TodoItem(f"{json.dumps(obj)} @#holiday @#HIDDEN")
        holiday_data.done()
        process(holiday_data, Option.FORMAT | Option.ADD)
