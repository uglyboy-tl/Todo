from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import yaml
from loguru import logger
from pydantic import BaseModel, model_validator
from typing_extensions import Self

from todo.core import TodoItem, TodoTxt

from .context import BaseContext


class Option(Enum):
    FORMAT = 0  # 第0位
    ADD = 1  # 第1位
    EXECUTE = 2  # 第2位
    BREAK = 3  # 第3位
    DONE = 4  # 第4位
    MODIFY_ALL = 5  # 第5位
    REMOVE = 6  # 第6位
    ARCHIVE = 7  # 第7位
    SEARCH = 8  # 第8位
    TYPE = 9  # 第9位
    # 根据需要添加更多选项

    def __or__(self, other: Union["Option", int]) -> int:
        if isinstance(other, Option):
            return 1 << self.value | 1 << other.value
        else:
            return 1 << self.value | other

    def __ror__(self, other: Union["Option", int]) -> int:
        if isinstance(other, Option):
            return 1 << self.value | 1 << other.value
        else:
            return 1 << self.value | other


class Parameter:
    def __init__(self, value: int = 1):
        self.value = value

    def __eq__(self, option: Option):
        mask = 1 << option.value
        return (self.value & mask) != 0

    def __and__(self, option: Option):
        mask = 1 << option.value
        self.value |= mask

    def __rand__(self, option: Option):
        mask = 1 << option.value
        self.value |= mask

    def __sub__(self, option: Option):
        mask = 1 << option.value
        self.value &= ~mask


class BaseConfig(BaseModel):
    name: str = ""
    alias: List[str] = []
    start_script: Optional[str] = None
    script_configs: List[Dict[str, Any]] = []

    @model_validator(mode="after")
    def verify_config(self) -> Self:
        self._get_init_config()
        return self

    def _get_init_config(self):
        if not self.start_script:
            return None
        init_list = [item for item in self.script_configs if item.get("name") == self.start_script]
        assert len(init_list) <= 1, f"Only one init script is allowed in {self.name}"
        if init_list:
            init_config = init_list[0]
        else:
            init_config = {"name": f"{self.start_script}", "type": f"{self.start_script}"}
            self.script_configs.append(init_config)
        return init_config

    def add_init_script(self, todotxt: TodoTxt):
        if not self.start_script:
            return
        need_to_remove = todotxt[self.name].search(self.start_script).copy()
        for todo in need_to_remove:
            todotxt.remove(todo)
        todotxt.append(
            TodoItem(f"@{self.start_script} @#HIDDEN +{self.name}", priority="A", due=datetime.now()), head=True
        )

    def format_todo(self, todo: TodoItem, disable_project_name: bool):
        if self.name not in todo.project and not disable_project_name:
            todo.add_project(self.name)
        return todo

    @staticmethod
    def merge_preset_scripts(script_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return script_configs

    @staticmethod
    def sort_score(script: BaseContext):
        return 0

    @classmethod
    def load(cls, file_path: str, name: str = ""):
        with open(file_path) as f:
            y = yaml.load_all(f, Loader=yaml.FullLoader)
            num = 0
            for data in y:
                num += 1
                if data["name"] == name:
                    obj = data
                    break
            if not name and num == 1:
                obj = data
            assert obj, f'Can\'t find config "{name}" in {file_path}'
            logger.trace(f"Loading config from {file_path}: {obj}")
            return cls.model_validate(obj)

    @classmethod
    def load_all(cls, file_path: str) -> List["BaseConfig"]:
        with open(file_path) as f:
            y = yaml.load_all(f, Loader=yaml.FullLoader)
            return [cls.model_validate(data) for data in y]
