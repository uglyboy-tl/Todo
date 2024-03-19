from dataclasses import dataclass
from datetime import datetime
from urllib import error, request

from loguru import logger

from todo.core import TodoItem
from todo.project import BaseContext, Option


@dataclass
class WebHook(BaseContext):
    url: str
    save_data: bool = False

    def __call__(self, todo: TodoItem, process):
        try:
            with request.urlopen(self.url) as response:
                content = response.read().decode("utf-8")
            logger.success(f"请求成功，返回结果: {content}")
            if self.save_data:
                data = TodoItem(f"{content} @#{self.name}", completed=True, completion_date=datetime.now())
                process(data, Option.FORMAT | Option.ADD)
            notify = TodoItem(f"{self.name} 请求成功 @notify")
            process(notify, Option.EXECUTE)
        except error.URLError as e:
            logger.error(f"URL错误: {e.reason}")
        except Exception as e:
            logger.error(f"请求失败: {e}")
