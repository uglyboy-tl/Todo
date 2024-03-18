from dataclasses import dataclass, field
from typing import Any, Dict, List, Type, Union

from loguru import logger
from stevedore import ExtensionManager

from todo.core import TodoItem, TodoTxt

from .context import BaseContext, BaseFilter
from .schema import Config, Option, Parameter

SYSTEM_SCRIPTS = [
    "done",
    "update",
    "time_filter",
    "date_filter",
    "weather_filter",
    "weather",
    "notify",
]

OPTION_SCRITPS = [
    "weather",
    "notify",
]


@dataclass
class Project:
    name: str = ""
    scripts: List[BaseContext] = field(default_factory=list)
    config: Config = field(default_factory=Config)

    def __call__(self, todotxt: TodoTxt):
        self._init(todotxt)
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
                logger.trace(f"Append todo: {todo}")
            if type == Option.EXECUTE:
                todolist.append(todo)
            if type == Option.REMOVE:
                todotxt.remove(todo)
                logger.trace(f"Remove todo: {todo}")
                if todo in todolist:
                    todolist.remove(todo)
            if type == Option.BREAK:
                todo.context.append("#break")
            if type == Option.DONE:
                todotxt.done(todo)
            if type == Option.MODIFY_ALL:
                todo.context.append("#all")
            return todo

        index = 0
        while index < len(todolist):
            todo = todolist[index]
            logger.trace(f"Processing: {todo}")
            if "#break" in todo.context:
                todo.context.remove("#break")
            if "#all" in todo.context:
                todo.context.remove("#all")
            for script in self.scripts:
                if script.match(todo.context):
                    script(todo, process)
                    if "#all" in todo.context:
                        logger.trace(f"Modifying All: {todo}")
                        todo.context.remove("#all")
                        script.modify_all(todo, todotxt, process)
                    if "#break" in todo.context:
                        logger.trace(f"Skipping: {todo}")
                        todo.context.remove("#break")
                        break
            index += 1

    def _format(self, todo: TodoItem):
        if self.name not in todo.project and self.name != "SYSTEM":
            todo.add_project(self.name)
        return todo

    def _init(self, todotxt: TodoTxt):
        self.config.init(todotxt)

    @classmethod
    def load(cls, file_path: str, name: str = ""):
        config: Config = Config.load(file_path, name)
        context_plugins: List[Type[BaseContext]] = ExtensionManager(namespace="todo.project", invoke_on_load=False)
        context_private_plugins: List[Type[BaseContext]] = ExtensionManager(
            namespace=f"todo.project.{config.name}", invoke_on_load=False
        )

        # context_plugins.extend(list(ExtensionManager(namespace=f"todo.project.{config.name}", invoke_on_load=False)))
        context_type_set = {context.name for context in context_plugins}
        context_private_type_set = {context.name for context in context_private_plugins}

        scripts = []
        for script in cls.merge_system_scripts(config.script_configs):
            assert "name" in script.keys()
            if "type" not in script.keys():
                script["type"] = script["name"]
            if script["type"] in context_type_set:
                script = context_plugins[script.pop("type")].plugin(**script)
            elif script["type"] in context_private_type_set:
                script = context_private_plugins[script.pop("type")].plugin(**script)
            else:
                logger.warning(f"Context `@{script['type']}` not found, skipping")
                continue
            scripts.append(script)
        scripts.sort(key=lambda x: 1 if isinstance(x, BaseFilter) else 0, reverse=True)
        logger.trace(f"Project:{config.name}\nScripts: {[script.name for script in scripts]}")
        return cls(config.name, scripts, config)

    @staticmethod
    def merge_system_scripts(script_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        option_scripts = [script["name"] for script in script_configs if script["name"] in OPTION_SCRITPS]
        if option_scripts:
            merge_scripts = [
                {"name": script, "type": script} for script in SYSTEM_SCRIPTS if script not in option_scripts
            ]
        else:
            merge_scripts = [{"name": script, "type": script} for script in SYSTEM_SCRIPTS]
        merge_scripts.extend(
            [
                script
                for script in script_configs
                if script["name"] not in SYSTEM_SCRIPTS or script["name"] in OPTION_SCRITPS
            ]
        )
        return merge_scripts
