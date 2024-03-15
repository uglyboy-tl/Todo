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
    scripts: List[BaseContext] = field(default_factory=list)
    config: Config = field(default_factory=Config)

    def __call__(self, todotxt: TodoTxt):
        if self.name == "SYSTEM":
            todolist = todotxt.alert().sort().todo_list
        else:
            todolist = todotxt[self.name].alert().sort().todo_list

        def process(todo: TodoItem, type: Union[Parameter, int] = 1) -> TodoItem:
            if isinstance(type, int):
                type = Parameter(type)
            if type == Option.FORMAT:
                todo = self._format(todo)
            if type == Option.ADD:
                todotxt.append(todo)
            if type == Option.EXECUTE:
                todolist.append(todo)
            if type == Option.BREAK:
                todo.context.append("break")
            if type == Option.DONE:
                todotxt.done(todo)
            return todo

        index = 0
        while index < len(todolist):
            todo = todolist[index]
            logger.trace(f"Processing: {todo}")
            for script in self.scripts:
                if script.match(todo.context):
                    script(todo, process)
                    if "break" in todo.context:
                        todo.context.remove("break")
                        break
            index += 1

    def _format(self, todo: TodoItem):
        if self.name not in todo.project:
            todo.add_project(self.name)
        return todo

    @classmethod
    def load(cls, file_path: str):
        config: Config = Config.load(file_path)
        context_plugins: List[[Type[BaseContext]]] = ExtensionManager(namespace="todo.project", invoke_on_load=False)
        context_type_set = {context.name for context in context_plugins}

        scripts = []
        for context in config.context_configs:
            if context["type"] not in context_type_set:
                logger.warning(f"Context `@{context['type']}` not found, skipping")
                continue
            context = context_plugins[context.pop("type")].plugin(**context)
            scripts.append(context)
        return cls(config.name, scripts, config)
