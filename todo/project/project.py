from dataclasses import dataclass, field
from typing import List, Type, Union

from loguru import logger
from stevedore import ExtensionManager

from todo.core import TodoItem, TodoTxt

from .context import BaseContext
from .schema import Config, Option, Parameter


@dataclass
class Project:
    name: str = ""
    contexts: List[BaseContext] = field(default_factory=list)
    config: Config = field(default_factory=Config)

    def __call__(self, todotxt: TodoTxt):
        todolist = todotxt[self.name].alert().sort().todo_list

        def format(todo: TodoItem, type: Union[Parameter, int] = 1):
            if isinstance(type, int):
                type = Parameter(type)
            if type == Option.FORMAT:
                todo = self.format(todo)
            if type == Option.ADD:
                todotxt.append(self.format(todo))
            if type == Option.EXECUTE:
                todolist.append(todo)
            return todo

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
            todo.add_project(self.name)
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
