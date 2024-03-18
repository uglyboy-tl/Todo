from dataclasses import dataclass

from loguru import logger

from todo.core import TodoItem
from todo.project import BaseNotify


@dataclass
class Notify(BaseNotify):
    id: str = "Notify"

    @staticmethod
    def _validate(id: str):
        pass

    def __call__(self, todo: TodoItem, process):
        logger.info(f"{self.id}: {todo.message}")
