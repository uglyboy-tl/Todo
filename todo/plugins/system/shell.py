import subprocess
from dataclasses import dataclass

from loguru import logger

from todo.core import TodoItem
from todo.project import BaseContext, Option


@dataclass
class Shell(BaseContext):
    command: str

    def __call__(self, todo: TodoItem, process):
        try:
            result = subprocess.run(self.command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                notify = TodoItem(f"{self.name} 执行成功 @notify")
                logger.success(f"执行成功: {result.stdout}")
            else:
                notify = TodoItem(f"{self.name} 执行失败 @notify")
                logger.error(f"执行失败: {result.stderr}")
            process(notify, Option.EXECUTE)
        except Exception as e:
            logger.error(f"执行失败: {e}")
