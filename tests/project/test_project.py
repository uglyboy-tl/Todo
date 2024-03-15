import time
from dataclasses import dataclass

import yaml

from todo.core import TodoItem, TodoTxt
from todo.project import BaseContext, Config, Option, Project

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


def test_call_with_alerts_and_contexts():
    # Setup
    todo_txt = TodoTxt()
    todo_item1 = TodoItem(f"Test todo @alert +project1 due:{TODAY}")
    todo_item2 = TodoItem(f"Test todo @noalert +project1 due:{TODAY}")
    todo_txt.append(todo_item1)
    todo_txt.append(todo_item2)
    project = Project("project1")

    assert len(todo_txt["project1"].alert()) == 2

    project.scripts = [TestContext2()]

    # Call
    project(todo_txt)

    # Assert
    assert todo_item1.description == "Modified"
    assert todo_item2.description == "Test todo @noalert +project1"


def test_call_with_no_alerts():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @noalert +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    assert len(todo_txt["project1"].alert()) == 1
    project = Project("project1")
    project.scripts = [TestContext2()]

    # Call
    project(todo_txt)

    # Assert
    assert todo_item.description == "Test todo @noalert +project1"


def test_call_with_no_contexts():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @alert +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    assert len(todo_txt["project1"].alert()) == 1
    project = Project("project1")
    project.scripts = []

    # Call
    project(todo_txt)

    # Assert
    assert todo_item.description == "Test todo @alert +project1"


def test_config_load():
    # Setup
    file_path = "data/project/test.yaml"
    data = {
        "name": "example",
    }
    with open(file_path, "w") as f:
        yaml.dump(data, f)

    # Call
    config = Config.load(file_path)

    # Assert
    assert isinstance(config, Config)
    assert config.name == "example"
    assert isinstance(config.context_configs, list)
    assert len(config.context_configs) == 0  # Assuming the config file is empty


def test_config_load_with_data():
    # Setup
    file_path = "data/project/test.yaml"
    data = {
        "name": "example",
        "context_configs": [
            {"name": "alert", "priority": 1},
            {"name": "reminder", "priority": 2},
        ],
    }
    with open(file_path, "w") as f:
        yaml.dump(data, f)

    # Call
    config = Config.load(file_path)

    # Assert
    assert isinstance(config, Config)
    assert config.name == "example"
    assert isinstance(config.context_configs, list)
    assert len(config.context_configs) == 2
    assert config.context_configs[0]["name"] == "alert"
    assert config.context_configs[0]["priority"] == 1
    assert config.context_configs[1]["name"] == "reminder"
    assert config.context_configs[1]["priority"] == 2


def project_init(file_path: str):
    data = {
        "name": "example",
        "context_configs": [
            {"name": "addone", "type": "test1"},
            {"name": "test2"},
            {"name": "addone", "type": "notest"},
        ],
    }
    with open(file_path, "w") as f:
        yaml.dump(data, f)


def test_project_load():
    # Setup
    file_path = "data/project/test.yaml"
    project_init(file_path)
    project = Project.load(file_path)
    assert len(project.scripts) == 2

    # Call
    todo_txt1 = TodoTxt()
    todo_item = TodoItem(f"Test todo @test2 +example due:{TODAY}")
    todo_txt1.append(todo_item)
    project(todo_txt1)
    assert todo_item.description == "Modified"

    todo_txt2 = TodoTxt(todo_list=[])
    todo_item = TodoItem(f"Test todo @addone +example due:{TODAY}")
    todo_txt2.append(todo_item)
    project(todo_txt2)
    assert len(todo_txt2) == 2
    assert todo_txt2[0].completed is True
    assert todo_txt2[1].description == "Test New todo +example"


def test_project_load_contexts():
    # Setup
    file_path = "data/project/test.yaml"
    project_init(file_path)
    todo_txt = TodoTxt(todo_list=[])
    project = Project.load(file_path)
    assert len(project.scripts) == 2
    reminder = project.scripts[0]
    alert = project.scripts[1]

    assert reminder.name == "addone"
    assert alert.name == "test2"
    # assert isinstance(reminder, TestContext)

    todo_item = TodoItem(f"Test todo @alert +example due:{TODAY}")
    todo_txt.append(todo_item)
    reminder(todo_item, process=lambda x, _: x)
    assert len(todo_txt) == 1
    assert todo_item.completed is False
    # assert todo_txt[0].description == "Test New todo"

    todo_item = TodoItem(f"Test todo @alert +example due:{TODAY}")
    alert(todo_item, lambda x, _: x)
    assert todo_item.description == "Modified"
