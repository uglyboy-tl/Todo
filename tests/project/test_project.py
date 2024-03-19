import time
from dataclasses import dataclass

import yaml

from todo.core import TodoItem, TodoTxt
from todo.project import BaseContext, Option, Project
from todo.project.config import SYSTEM_SCRIPTS

TODAY = time.strftime("%Y-%m-%d")


@dataclass
class TestContext1(BaseContext):
    name: str = "alert"

    def __call__(self, todo, process=lambda x, _: x):
        process(TodoItem("Test New todo"), Option.FORMAT | Option.ADD | Option.EXECUTE)
        process(todo, Option.DONE)


@dataclass
class TestContext2(BaseContext):
    name: str = "alert"

    def __call__(self, todo, _):
        todo.description = "Modified"


def project_init(file_path: str):
    data = {
        "name": "test",
        "due_with_unfinished": False,
        "alert_days": 0,
        "script_configs": [
            {"name": "addone", "type": "test1"},
            {"name": "test2"},
            {"name": "addone", "type": "notest"},
        ],
    }
    with open(file_path, "w") as f:
        yaml.dump(data, f)


def test_project_load():
    # Setup
    file_path = "tests/data/test.yaml"
    project_init(file_path)
    project = Project.load(file_path, "test")
    print(project.scripts)
    assert len(project.scripts) == 3 + len(SYSTEM_SCRIPTS)

    # Call
    todo_txt1 = TodoTxt(todo_list=[])
    todo_item = TodoItem(f"Test todo @test2 +test due:{TODAY}")
    todo_txt1.append(todo_item)
    project(todo_txt1)
    assert todo_item.description == "Modified"

    todo_txt2 = TodoTxt(todo_list=[])
    todo_item = TodoItem(f"Test todo @addone +test due:{TODAY}")
    todo_txt2.append(todo_item)
    project(todo_txt2)
    assert len(todo_txt2) == 3
    assert todo_txt2[1].completed is True
    assert todo_txt2[2].description == "Test New todo +test"


def test_project_load_contexts():
    # Setup
    file_path = "tests/data/test.yaml"
    project_init(file_path)
    todo_txt = TodoTxt(todo_list=[])
    project = Project.load(file_path, "test")
    assert len(project.scripts) == 3 + len(SYSTEM_SCRIPTS)
    print(project.scripts)
    reminder = project.scripts[len(SYSTEM_SCRIPTS) - 3]
    alert = project.scripts[len(SYSTEM_SCRIPTS) - 2]

    assert reminder.name == "addone"
    assert alert.name == "test2"
    # assert isinstance(reminder, TestContext)

    todo_item = TodoItem(f"Test todo @alert +test due:{TODAY}")
    todo_txt.append(todo_item)
    reminder(todo_item, process=lambda x, _: x)
    assert len(todo_txt) == 1
    assert todo_item.completed is False
    # assert todo_txt[0].description == "Test New todo"

    todo_item = TodoItem(f"Test todo @alert +test due:{TODAY}")
    alert(todo_item, lambda x, _: x)
    assert todo_item.description == "Modified"
