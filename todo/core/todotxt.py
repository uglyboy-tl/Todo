from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from shutil import copy2
from typing import Dict, List, Optional, Union, overload

from dateutil.relativedelta import relativedelta

from .todo import TodoItem


@dataclass
class TodoTxt:
    file_path: str = "data/test.txt"
    todo_list: Optional[List[TodoItem]] = None
    read_only: bool = False
    _path: Path = field(init=False, repr=False)
    _init: bool = field(init=False, default=False)
    _dict: Dict[str, List[TodoItem]] = field(init=False, default_factory=dict)
    _completed_dict: Dict[str, List[TodoItem]] = field(init=False, default_factory=dict)

    def __post_init__(self):
        self._path = Path(self.file_path)
        if self.todo_list is None:
            self._load()
        else:
            self._init = True

    def append(self, todo: TodoItem, head: bool = False):
        if head:
            self.todo_list.insert(0, todo)
        else:
            self.todo_list.append(todo)
        for context in todo.context:
            if context not in self.dict:
                self.dict[context] = []
            if context.startswith("#"):
                self.dict[context].append(todo)
            elif not todo.completed:
                self.dict[context].append(todo)

    def remove(self, todo: TodoItem):
        self.todo_list.remove(todo)
        for context in todo.context:
            if context in self.dict and todo in self.dict[context]:
                if context.startswith("#"):
                    self.dict[context].remove(todo)
                elif not todo.completed:
                    self.dict[context].remove(todo)

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
        for context in todo.context:
            if context in self.dict and not context.startswith("#") and todo in self.dict[context]:
                self.dict[context].remove(todo)
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
                creation_date=todo.creation_date if todo.creation_date else datetime.now(),
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
        for context in self.dict:
            self._dict[context] = [todo for todo in self.dict[context] if not todo.completed]

    def sort(self) -> "TodoTxt":
        self.todo_list = sorted(
            self.todo_list,
            key=lambda x: (
                x.completed,
                x.priority if x.priority is not None else str("Z"),
                x.due.date() if x.due is not None else datetime.max.date(),
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

    def search(self, keyword: str, completed=False) -> List[TodoItem]:
        if not completed:
            return self.dict.get(keyword, [])
        else:
            return self.completed_dict.get(keyword, [])

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
            data = self._path.read_text().strip()
            if not data:
                self.todo_list = []
                return
            self.todo_list = [TodoItem.from_string(todo) for todo in data.split("\n")]

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

    @property
    def dict(self):
        if not self._dict:
            for todo in self.todo_list:
                for context in todo.context:
                    if context not in self._dict:
                        self._dict[context] = []
                    if context.startswith("#"):
                        self._dict[context].append(todo)
                    elif not todo.completed:
                        self._dict[context].append(todo)
                    elif context not in self._completed_dict:
                        self._completed_dict[context] = []
                        self._completed_dict[context].append(todo)
        return self._dict

    @property
    def completed_dict(self):
        if not self._completed_dict:
            self.dict  # noqa: B018
        return self._completed_dict

    @property
    def output(self):
        return "\n".join([str(todo) for todo in self.sort() if "SYSTEM" not in todo.project and not todo.completed])


def open_todotxt(file_path: str = "data/todo.txt") -> TodoTxt:
    return TodoTxt(file_path=file_path, read_only=False)
