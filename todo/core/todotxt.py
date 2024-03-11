from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from shutil import copy2
from typing import List, Optional, Union, overload

from dateutil.relativedelta import relativedelta

from .todo import TodoItem


@dataclass
class TodoTxt:
    file_path: str = "data/test.txt"
    todo_list: Optional[List[TodoItem]] = None
    _path: Path = field(init=False, repr=False)
    _init: bool = field(init=False, default=False)

    def __post_init__(self):
        self._path = Path(self.file_path)
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self.todo_list = []
            self._init = True
        elif self.todo_list is None:
            self._load()
        else:
            self._init = True
        self._sort()

    def append(self, todo: TodoItem):
        self.todo_list.append(todo)
        self._save()

    @overload
    def done(self, todo: int):
        pass

    @overload
    def done(self, todo: TodoItem):
        pass

    def done(self, todo: Union[TodoItem, int]):
        if isinstance(todo, int):
            todo = self.todo_list[todo]
        elif isinstance(todo, TodoItem):
            assert todo in self
        todo.done()
        if todo.recurrence:
            description = todo.description
            if todo.recurrence.endswith("d"):
                delta = timedelta(days=int(todo.recurrence[:-1]))
            elif todo.recurrence.endswith("w"):
                delta = timedelta(weeks=int(todo.recurrence[:-1]))
            elif todo.recurrence.endswith("m"):
                delta = relativedelta(months=1)
            elif todo.recurrence.endswith("y"):
                delta = relativedelta(years=1)
            due = datetime.now() + delta
            new_todo = TodoItem(
                completed=False,
                priority=todo.priority,
                creation_date=datetime.now(),
                description=description,
                recurrence=todo.recurrence,
                due=due,
            )
            self.append(new_todo)
        self._save()

    def _sort(self):
        self.todo_list = sorted(
            self.todo_list,
            key=lambda x: (
                x.completed,
                x.priority if x.priority is not None else str("Z"),
                x.due if x.due is not None else datetime.max,
                x.creation_date if x.creation_date is not None else datetime.max,
            ),
        )

    def _save(self):
        self._sort()
        if self._path.exists() and not self._init:
            self._backup()
        if self.todo_list or not self._init:
            self._path.write_text(str(self))
            self._init = False

    def _load(self):
        self.todo_list = [TodoItem.from_string(todo) for todo in self._path.read_text().split("\n")]

    def _backup(self):
        backup_path = self._path.with_suffix(self._path.suffix + "." + datetime.now().strftime("%Y%m%d%H%M%S") + ".bak")
        copy2(self._path, backup_path)

    def __iter__(self):
        return iter(self.todo_list)

    def __getitem__(self, index: int):
        return self.todo_list[index]

    def __contains__(self, todo: TodoItem):
        return todo in self.todo_list

    def __len__(self):
        return len(self.todo_list)

    def __str__(self):
        return "\n".join([str(todo) for todo in self.todo_list])
