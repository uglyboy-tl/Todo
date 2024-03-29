import yaml

from todo.core import TodoItem, TodoTxt
from todo.project.schema import BaseConfig, Option


def test_config_load():
    # Setup
    file_path = "tests/data/test.yaml"
    data = {
        "name": "test",
    }
    with open(file_path, "w") as f:
        yaml.dump(data, f)

    # Call
    config = BaseConfig.load(file_path)

    # Assert
    assert isinstance(config, BaseConfig)
    assert config.name == "test"
    assert isinstance(config.script_configs, list)
    assert len(config.script_configs) == 0  # Assuming the config file is empty


def test_config_load_with_data():
    # Setup
    file_path = "tests/data/test.yaml"
    data = {
        "name": "test",
        "script_configs": [
            {"name": "alert1", "priority": 1},
            {"name": "reminder", "priority": 2},
        ],
    }
    with open(file_path, "w") as f:
        yaml.dump(data, f)

    # Call
    config = BaseConfig.load(file_path)

    # Assert
    assert isinstance(config, BaseConfig)
    assert config.name == "test"
    assert isinstance(config.script_configs, list)
    assert len(config.script_configs) == 2
    assert config.script_configs[0]["name"] == "alert1"
    assert config.script_configs[0]["priority"] == 1
    assert config.script_configs[1]["name"] == "reminder"
    assert config.script_configs[1]["priority"] == 2


def test_base_config_get_init_config():
    # Setup
    config = BaseConfig(
        name="test",
        start_script="start",
        script_configs=[{"name": "alert1", "priority": 1}, {"name": "reminder", "priority": 2}],
    )

    # Call
    init_config = config._get_init_config()

    # Assert
    assert isinstance(init_config, dict)
    assert init_config["name"] == "start"
    assert init_config["type"] == "start"
    assert len(config.script_configs) == 3


def test_base_config_add_init_script():
    # Setup
    config = BaseConfig(name="test")
    todotxt = TodoTxt(todo_list=[])
    todo = TodoItem("Test todo item")

    # Call
    config.add_init_script(todotxt)
    formatted_todo = config.format_todo(todo, False)

    # Assert
    assert len(todotxt.todo_list) == 0
    assert formatted_todo.project == ["test"]


def test_base_config_load():
    # Setup
    file_path = "tests/data/test.yaml"

    # Call
    config = BaseConfig.load(file_path, name="test")

    # Assert
    assert isinstance(config, BaseConfig)
    assert config.name == "test"
    assert isinstance(config.script_configs, list)
    assert len(config.script_configs) == 2
    assert config.script_configs[0]["name"] == "alert1"
    assert config.script_configs[0]["priority"] == 1
    assert config.script_configs[1]["name"] == "reminder"
    assert config.script_configs[1]["priority"] == 2


def test_base_config_load_all():
    # Setup
    file_path = "tests/data/test.yaml"

    # Call
    configs = BaseConfig.load_all(file_path)

    # Assert
    assert isinstance(configs, list)
    assert len(configs) == 1
    assert isinstance(configs[0], BaseConfig)
    assert configs[0].name == "test"
    assert isinstance(configs[0].script_configs, list)
    assert len(configs[0].script_configs) == 2
    assert configs[0].script_configs[0]["name"] == "alert1"
    assert configs[0].script_configs[0]["priority"] == 1
    assert configs[0].script_configs[1]["name"] == "reminder"
    assert configs[0].script_configs[1]["priority"] == 2


def test_option_bitwise_or():
    # Setup
    option1 = Option.FORMAT
    option2 = Option.ADD
    option3 = Option.EXECUTE

    # Call
    result1 = option1 | option2
    result2 = option1 | option3
    result3 = option2 | option3
    result4 = option1 | 5

    # Assert
    assert result1 == 3
    assert result2 == 5
    assert result3 == 6
    assert result4 == 5


def test_option_bitwise_or_with_int():
    # Setup
    option = Option.FORMAT

    # Call
    result1 = option | 2
    result2 = option | 4

    # Assert
    assert result1 == 3
    assert result2 == 5


def test_option_bitwise_or_reverse():
    # Setup
    option1 = Option.FORMAT
    option2 = Option.ADD
    option3 = Option.EXECUTE

    # Call
    result1 = option1 | option2
    result2 = option1 | option3
    result3 = option2 | option3
    result4 = 5 | option1

    # Assert
    assert result1 == 3
    assert result2 == 5
    assert result3 == 6
    assert result4 == 5
