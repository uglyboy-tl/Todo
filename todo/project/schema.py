from enum import Enum
from typing import Any, Dict, List, Union

import yaml
from loguru import logger
from pydantic import BaseModel


class Option(Enum):
    FORMAT = 0  # 第0位
    ADD = 1  # 第1位
    EXECUTE = 2  # 第2位
    BREAK = 3  # 第3位
    DONE = 4  # 第4位
    MODIFY_ALL = 5  # 第5位
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


class Config(BaseModel):
    name: str = ""
    context_configs: List[Dict[str, Any]] = []

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
