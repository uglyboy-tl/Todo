import json
import urllib
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from loguru import logger

from todo.core import TodoItem
from todo.project import BaseContext, Option

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}


@dataclass
class Webhook(BaseContext):
    url: str
    method: Literal["GET", "POST"] = "GET"
    save_data: bool = False

    def __call__(self, todo: TodoItem, process):
        try:
            data = json.loads(todo.message)
            params = urllib.parse.urlencode(data).encode("utf-8")
        except Exception:
            params = None
        try:
            request = urllib.request.Request(self.url, data=params, headers=HEADERS, method=self.method)
            with urllib.request.urlopen(request) as response:
                content = response.read().decode("utf-8")
            self._process(content, process)
        except urllib.error.URLError as e:
            logger.error(f"URL错误: {e.reason}")
        except Exception as e:
            logger.error(f"请求失败: {e}")

    def _process(self, content: str, process):
        if self.save_data:
            data = TodoItem(content, completed=True, completion_date=datetime.now())
            process(data, Option.FORMAT | Option.ADD)
        notify = TodoItem(f"{self.name} 请求成功 @notify")
        process(notify, Option.EXECUTE)
