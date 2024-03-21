import re
from dataclasses import dataclass

from todo.core import TodoItem, TodoTxt
from todo.project import BaseInit, Option


@dataclass
class Init(BaseInit):

    def __call__(self, todo: TodoItem, process):
        if self.name in todo.context:
            process(todo, Option.MODIFY_ALL)

    def modify_all(self, _: TodoItem, todotxt: TodoTxt, process):
        # 未完成任务处理脚本
        self._update_preset_todo("unfinished", True, todotxt, process)


@dataclass
class SysInit(Init):
    archive_recurrence: str = ""

    def __post_init__(self):
        if self.archive_recurrence:
            pattern = re.compile(r"\d+[dwmy]")
            assert pattern.match(self.archive_recurrence), "Invalid archive due format"

    def modify_all(self, _: TodoItem, todotxt: TodoTxt, process):
        # 优先级A的归档脚本
        self._update_preset_todo(
            "archive",
            bool(self.archive_recurrence),
            todotxt,
            process,
            False,
            TodoItem("Preset", priority="A", recurrence=self.archive_recurrence),
        )

        super().modify_all(_, todotxt, process)
