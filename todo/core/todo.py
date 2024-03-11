import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional


def is_date(date: str) -> bool:
    match = re.compile(r"\d{4}-\d{2}-\d{2}")
    return bool(match.match(date))


@dataclass
class TodoItem:
    description: str
    completed: bool = field(default=False, compare=False)
    priority: Optional[Literal["A", "B", "C", "D", "E"]] = field(default=None, compare=False)
    completion_date: Optional[datetime] = field(default=None, compare=False)
    creation_date: Optional[datetime] = field(default_factory=datetime.now)
    project: List[str] = field(init=False, compare=False, default_factory=list)
    context: List[str] = field(init=False, compare=False, default_factory=list)
    recurrence: Optional[str] = field(init=False, compare=False, default=None)
    due: Optional[datetime] = field(init=False, compare=False, default=None)

    def __post_init__(self):
        assert self.creation_date is None or self.completion_date is None or self.creation_date <= self.completion_date
        self._get_metadata()

    def _get_metadata(self):
        if self.description == "":
            raise ValueError("No description")
        tags = self.description.split(" ")
        for tag in tags:
            if is_date(tag):
                try:
                    datetime.strptime(tag, "%Y-%m-%d")
                    flag = True
                except Exception:
                    flag = False
                if flag:
                    raise ValueError("Invalid multiple date")
            if tag.startswith("+"):
                self.project.append(tag[1:])
            if tag.startswith("@"):
                self.context.append(tag[1:])
            if tag.startswith("rec:"):
                if self.recurrence is not None:
                    raise ValueError("Recurrence already set")
                recurrence = re.match(r"rec:(\d+)(.*)", tag)
                num = int(recurrence.group(1))
                period = recurrence.group(2)
                if period == "d":
                    self.recurrence = num
                elif period == "w":
                    self.recurrence = num * 7
                elif period == "m":
                    self.recurrence = num * 30
                else:
                    raise ValueError("Invalid period")
            if tag.startswith("due:"):
                if self.due is not None:
                    raise ValueError("Due date already set")
                if not is_date(tag[4:]):
                    raise ValueError("Invalid due date")
                self.due = datetime.strptime(tag[4:], "%Y-%m-%d")

    def __str__(self):
        strings = []
        if self.completed:
            strings.append("x")
        if self.priority:
            strings.append(f"({self.priority})")
        if self.completion_date:
            strings.append(self.completion_date.strftime("%Y-%m-%d"))
        if self.creation_date:
            strings.append(self.creation_date.strftime("%Y-%m-%d"))
        strings.append(self.description)
        return " ".join(strings)

    def done(self):
        self.completed = True
        self.completion_date = datetime.now()

    @classmethod
    def from_string(cls, todo: str) -> "TodoItem":
        todo = todo.strip().split(" ")
        if todo[0] == "x":
            completed = True
            todo = todo[1:]
        else:
            completed = False
        if todo[0].startswith("(") and todo[0].endswith(")"):
            priority = todo[0][1]
            todo = todo[1:]
        else:
            priority = None
        if completed is True and is_date(todo[0]):
            try:
                completion_date = datetime.strptime(todo[0], "%Y-%m-%d")
            except ValueError as err:
                raise ValueError("Invalid completion date") from err
            todo = todo[1:]
        else:
            completion_date = None
        if is_date(todo[0]):
            try:
                creation_date = datetime.strptime(todo[0], "%Y-%m-%d")
            except ValueError as err:
                raise ValueError("Invalid creation date") from err
            todo = todo[1:]
        else:
            creation_date = None
        if len(todo) == 0 or todo[0] == "":
            raise ValueError("No description")
        description = " ".join(todo)
        return cls(
            completed=completed,
            priority=priority,
            completion_date=completion_date,
            creation_date=creation_date,
            description=description,
        )
