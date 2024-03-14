import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional


def is_date(date: str) -> bool:
    pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    return bool(pattern.match(date))


@dataclass
class TodoItem:
    _description: str
    completed: bool = field(default=False, compare=False)
    priority: Optional[Literal["A", "B", "C", "D", "E"]] = field(default=None, compare=False)
    completion_date: Optional[datetime] = field(default=None, compare=False)
    creation_date: Optional[datetime] = field(default_factory=datetime.now)
    recurrence: Optional[str] = field(compare=True, default=None)
    due: Optional[datetime] = field(compare=True, default=None)
    project: List[str] = field(init=False, compare=False, default_factory=list)
    context: List[str] = field(init=False, compare=False, default_factory=list)
    message: str = field(init=False, compare=False, default="")

    def __post_init__(self):
        assert (
            self.creation_date is None
            or self.completion_date is None
            or self.creation_date.date() <= self.completion_date.date()
        )
        self._validate()

    def done(self):
        self.completed = True
        self.completion_date = datetime.now().date()

    def _validate(self) -> None:
        self._description = self._description.strip()
        tags = self._description.split(" ")
        for tag in tags.copy():
            self._validate_not_date(tag)
            if tag.startswith("+"):
                self.project.append(tag[1:])
                continue
            if tag.startswith("@"):
                self.context.append(tag[1:])
                continue
            if tag.startswith("rec:"):
                if self.recurrence is not None:
                    raise ValueError("Recurrence already set")
                self.recurrence = self._validate_recurrence(tag)
                tags.remove(tag)
                continue
            if tag.startswith("due:"):
                if self.due is not None:
                    raise ValueError("Due date already set")
                self.due = self._validate_date(tag[4:], "due")
                if self.due:
                    tags.remove(tag)
                else:
                    raise ValueError("Invalid due date")
                continue
            self.message += tag + " "
        if len(tags) == 0:
            raise ValueError("No description")
        self._description = " ".join(tags)
        if self._description == "":
            raise ValueError("No description")

    @staticmethod
    def _validate_x(x: str) -> bool:
        if x == "x":
            return True
        else:
            return False

    @staticmethod
    def _validate_not_date(date: str) -> None:
        if is_date(date):
            try:
                datetime.strptime(date, "%Y-%m-%d")
                flag = True
            except ValueError:
                flag = False
            if flag:
                raise ValueError("Invalid date")

    @staticmethod
    def _validate_date(date: str, info: str = "") -> Optional[bool]:
        if is_date(date):
            try:
                return datetime.strptime(date, "%Y-%m-%d")
            except ValueError as err:
                raise ValueError(f"Invalid {info} date") from err
        else:
            return None

    @staticmethod
    def _validate_priority(priority: str) -> Optional[bool]:
        if priority.startswith("(") and priority.endswith(")"):
            priority = priority[1]
            if priority in ["A", "B", "C", "D", "E"]:
                return priority
        return None

    @staticmethod
    def _validate_recurrence(recurrence: str) -> Optional[str]:
        pattern = re.compile(r"rec:\d+[dwmy]")
        if pattern.match(recurrence):
            return recurrence[4:]
        else:
            raise ValueError("Invalid recurrence format")

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
        if self.recurrence is not None:
            strings.append(f"rec:{self.recurrence}")
        if self.due:
            strings.append(f"due:{self.due.strftime('%Y-%m-%d')}")
        return " ".join(strings)

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value
        self._validate()

    def add_project(self, project: str) -> None:
        self.description += f" +{project}"

    def add_context(self, context: str) -> None:
        self.description += f" @{context}"

    @classmethod
    def from_string(cls, todo: str) -> "TodoItem":
        todo = todo.strip().split(" ")

        # Check if the todo is completed
        completed = cls._validate_x(todo[0])
        if completed:
            todo = todo[1:]

        # Check if the todo has a priority
        priority = cls._validate_priority(todo[0])
        if priority:
            todo = todo[1:]

        # Check if the todo has a completion date
        if completed is True:
            completion_date = cls._validate_date(todo[0], "completion")
            if completion_date:
                todo = todo[1:]
        else:
            completion_date = None

        # Check if the todo has a creation date
        creation_date = cls._validate_date(todo[0], "creation")
        if creation_date:
            todo = todo[1:]

        # The rest of the todo is the description
        description = " ".join(todo)

        # Return a new TodoItem instance
        return cls(
            completed=completed,
            priority=priority,
            completion_date=completion_date,
            creation_date=creation_date,
            _description=description,
        )
