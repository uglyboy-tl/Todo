from dataclasses import dataclass

from todo.core import TodoItem
from todo.project import BasePreparation


@dataclass
class Outing(BasePreparation):
    message: str = "别忘了出门要带的东西,今日行程：{}"

    def _process(self, todo: TodoItem, process):
        todo.add_context(f"#{self.name}")
