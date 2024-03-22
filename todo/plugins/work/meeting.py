import json
import re
from dataclasses import dataclass

from todo.core import TodoItem
from todo.project import BaseNotify, BasePreparation, Option


@dataclass
class Meeting(BasePreparation):
    message: str = "今天有会，会议内容：{}"

    def _process(self, todo: TodoItem, process):
        type_list = process(todo, Option.TYPE)
        members = [context_type.name for context_type in type_list if isinstance(context_type, BaseNotify)]
        times = []
        pattern = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d-(?:[01]\d|2[0-3]):[0-5]\d$")
        for context in todo.context:
            if pattern.match(context):
                times.append(context)
        assert len(times) == 1
        time = times[0]
        task = TodoItem(f"{json.dumps({'members': members, 'time': time},ensure_ascii=False)} @meeting_room @notify")
        process(task, Option.FORMAT | Option.ADD | Option.EXECUTE)
        todo.add_context(f"#{self.name}")
