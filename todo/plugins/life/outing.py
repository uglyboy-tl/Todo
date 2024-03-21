from dataclasses import dataclass
from datetime import datetime

from todo.core import TodoItem
from todo.project import BasePreparation, Option


@dataclass
class Outing(BasePreparation):
    message: str = "别忘了出门要带的东西"

    def _process(self, todo, process):
        if todo.due.date() == datetime.now().date():
            notify = TodoItem(f"{self.message} @notify")
            process(notify, Option.EXECUTE)
