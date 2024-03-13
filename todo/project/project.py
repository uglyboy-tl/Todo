from dataclasses import dataclass, field
from typing import Any, Dict, List, Type

import yaml
from loguru import logger
from pydantic import BaseModel
from stevedore import ExtensionManager

from todo.core import TodoItem, TodoTxt

from .context import BaseContext


class Config(BaseModel):
    name: str = ""
    context_configs: List[Dict[str, Any]] = []

    @classmethod
    def load(cls, file_path: str):
        with open(file_path) as f:
            obj = yaml.load(f, Loader=yaml.FullLoader)
            logger.debug(f"Loading config from {file_path}: {obj}")
            return cls.model_validate(obj)


@dataclass
class Project:
    name: str = ""
    contexts: List[BaseContext] = field(default_factory=list)
    config: Config = field(default_factory=Config)

    def __call__(self, todotxt: TodoTxt):
        todolist = todotxt[self.name].alert().todo_list

        def format(todo: TodoItem, type=0):
            if type == 1:
                todotxt.append(self.format(todo))
                todolist.append(todo)
            return self.format(todo)

        index = 0
        while index < len(todolist):
            todo = todolist[index]
            logger.debug(f"Processing: {todo}")
            for context in self.contexts:
                if context.name in todo.context:
                    context(todo, todotxt, format)
            index += 1

    def format(self, todo: TodoItem):
        if self.name not in todo.project:
            todo.description += f" +{self.name}"
            todo._validate()
        return todo

    @classmethod
    def load(cls, file_path: str):
        config: Config = Config.load(file_path)
        context_plugins: List[[Type[BaseContext]]] = ExtensionManager(namespace="todo.project", invoke_on_load=False)
        context_type_set = {context.name for context in context_plugins}

        contexts = []
        for context in config.context_configs:
            if context["type"] not in context_type_set:
                logger.warning(f"Context `@{context['type']}` not found, skipping")
                continue
            context = context_plugins[context.pop("type")].plugin(**context)
            contexts.append(context)
        return cls(config.name, contexts, config)
