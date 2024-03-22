from dataclasses import dataclass

from loguru import logger

from todo.core import TodoItem
from todo.project import BaseNotify


@dataclass
class Notify(BaseNotify):
    id: str = "Notify"

    def __post_init__(self):
        if not self.id:
            self.id = self.name
        super().__post_init__()

    def __call__(self, todo: TodoItem, process):
        logger.info(f"{self.id}: {todo.message}")

    @staticmethod
    def _validate(id: str):
        pass
