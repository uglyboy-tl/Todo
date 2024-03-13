import time
from dataclasses import dataclass

import yaml

from todo.core import TodoItem, TodoTxt
from todo.project import BaseContext, Project
from todo.project.project import Config

TODAY = time.strftime("%Y-%m-%d")


@dataclass
class TestContext(BaseContext):
    name: str = "alert"

    def __call__(self, todo, todotxt):
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

    project.contexts = [TestContext()]

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
    project.contexts = [TestContext()]

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
    project.contexts = []

    # Call
    project(todo_txt)

    # Assert
    assert todo_item.description == "Test todo @alert +project1"


def test_config_load():
    # Setup
    file_path = "tests/project/example.yaml"
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
    file_path = "tests/project/example.yaml"
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
