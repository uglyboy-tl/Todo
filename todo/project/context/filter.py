import re
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List, Optional

from todo.core import TodoItem

from ..schema import Option
from .base import BaseContext


@dataclass
class BaseFilter(BaseContext, metaclass=ABCMeta):
    regex: Optional[str] = field(init=False, default=None)
    pattern: Optional[re.Pattern] = field(init=False, default=None)
    data_name: str = ""
    script_name: str = ""

    def __post_init__(self):
        if self.regex is not None:
            self.pattern = re.compile(self.regex)

    def match(self, contexts: List[str]) -> bool:
        if self.pattern is not None:
            for context in contexts:
                if self.pattern.match(context):
                    return True
        return False

    def __call__(self, todo: TodoItem, process):
        matched_context = None
        for context in todo.context:
            if self.pattern.match(context):
                matched_context = context
        if not matched_context:
            return
        data = self._get_data(self.data_name, process)
        if data is not None:
            if not self._check(data, matched_context):
                process(todo, Option.BREAK)
        else:
            if self._no_getdata_todo(self.script_name, process):
                getdata_todo = TodoItem(f"@{self.script_name} @done @#HIDDEN +SYSTEM")
                process(getdata_todo, Option.ADD | Option.EXECUTE)
            process(todo, Option.BREAK)
            process(todo, Option.EXECUTE)

    def _get_data(self, name: str, process: Callable) -> Optional[str]:
        if name == "":
            return "Empty"
        for todo in process(TodoItem(f"@{name}"), Option.SEARCH):
            if todo.creation_date.date() == datetime.now().date():
                return todo.message
        return None

    def _no_getdata_todo(self, name: str, process: Callable) -> Optional[TodoItem]:
        new = None
        for todo in process(TodoItem(f"@{name}"), Option.SEARCH):
            if todo.completed:
                continue
            elif new is None:
                new = todo
            elif todo.due.date() < new.due.date():
                process(todo, Option.REMOVE)
            else:
                process(new, Option.REMOVE)
                new = todo
        if not new:
            return True
        new.due = datetime.now()
        return False

    @abstractmethod
    def _check(self, data: str, matched_context: str):
        pass
