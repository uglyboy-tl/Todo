from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from shutil import copy2
from typing import List, Optional, Union, overload

from dateutil.relativedelta import relativedelta

from .todo import TodoItem


@dataclass
class TodoTxt:
    file_path: str = "data/test/test.txt"
    todo_list: Optional[List[TodoItem]] = None
    read_only: bool = False
    _path: Path = field(init=False, repr=False)
    _init: bool = field(init=False, default=False)

    def __post_init__(self):
        self._path = Path(self.file_path)
        if self.todo_list is None:
            self._load()
        else:
            self._init = True

    def append(self, todo: TodoItem):
        self.todo_list.append(todo)

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
        if todo.completed:
            return
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
                creation_date=todo.creation_date,
                _description=description,
                recurrence=todo.recurrence,
                due=due,
            )
            self.todo_list.append(new_todo)

    def archive(self, done_file: Optional[str] = None):
        if self.read_only:
            return
        if done_file is None:
            done_file = self._path.with_name("done.txt")
        else:
            done_file = Path(done_file)
        done_file.parent.mkdir(parents=True, exist_ok=True)
        with open(done_file, "a") as file:
            for todo in self.todo_list:
                if todo.completed:
                    file.write(str(todo) + "\n")
        self.todo_list = [todo for todo in self.todo_list if not todo.completed]
        self._save()

    def sort(self) -> "TodoTxt":
        self.todo_list = sorted(
            self.todo_list,
            key=lambda x: (
                x.completed,
                x.priority if x.priority is not None else str("Z"),
                x.due if x.due is not None else datetime.max,
                x.creation_date if x.creation_date is not None else datetime.max,
            ),
        )
        return self

    def alert(self) -> "TodoTxt":
        todo_list = [
            todo
            for todo in self.todo_list
            if todo.due and todo.due.date() == datetime.now().date() and not todo.completed
        ]
        todotxt = TodoTxt(todo_list=todo_list, read_only=True)
        return todotxt

    def _save(self):
        if self.read_only:
            return
        if self._path.exists() and not self._init:
            self._backup()
        if self.todo_list or not self._init:
            self._path.write_text(str(self))
            self._init = False

    def _load(self):
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._init = True
            self.todo_list = []
        else:
            self.todo_list = [TodoItem.from_string(todo) for todo in self._path.read_text().split("\n")]

    def _backup(self):
        backup_path = self._path.with_suffix(self._path.suffix + "." + datetime.now().strftime("%Y%m%d%H%M%S") + ".bak")
        copy2(self._path, backup_path)

    def __iter__(self):
        return iter(self.todo_list)

    @overload
    def __getitem__(self, index: int) -> TodoItem:
        pass

    @overload
    def __getitem__(self, index: str) -> "TodoTxt":
        pass

    def __getitem__(self, index: Union[int, str]):
        if isinstance(index, int):
            return self.todo_list[index]
        elif isinstance(index, str):
            return TodoTxt(todo_list=[todo for todo in self.todo_list if index in todo.project], read_only=True)

    def __contains__(self, todo: TodoItem):
        return todo in self.todo_list

    def __len__(self):
        return len(self.todo_list)

    def __str__(self):
        return "\n".join([str(todo) for todo in self.todo_list])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._save()
