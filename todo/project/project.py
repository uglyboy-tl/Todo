from dataclasses import dataclass, field
from typing import Any, Dict, List, Type

import yaml
from loguru import logger
from pydantic import BaseModel
from stevedore import ExtensionManager

from todo.core import TodoTxt

from .context import BaseContext


class Config(BaseModel):
    name: str
    context_configs: List[Dict[str, Any]] = []

    @classmethod
    def load(cls, file_path: str):
        with open(file_path) as f:
            obj = yaml.load(f, Loader=yaml.FullLoader)
            print(obj)
            return cls.model_validate(obj)


@dataclass
class Project:
    name: str = ""
    contexts: List[BaseContext] = field(default_factory=list)

    def __call__(self, todotxt: TodoTxt):
        for todo in todotxt[self.name].alert():
            for context in self.contexts:
                if context.name in todo.context:
                    context(todo, todotxt)

    @classmethod
    def load(cls, file_path: str):
        config: Config = Config.load(file_path)
        context_plugins: List[[Type[BaseContext]]] = ExtensionManager(namespace="todo.project", invoke_on_load=False)
        context_type_set = {context.name for context in context_plugins}

        contexts = []
        for context in config.context_configs:
            if context["type"] not in context_type_set:
                logger.warning(f"Function {context['type']} not found, skipping")
                continue
            context = context_plugins[context.pop("type")].plugin(**context)
            contexts.append(context)
        return cls(config.name, contexts)
