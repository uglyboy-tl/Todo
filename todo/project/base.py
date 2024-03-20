from dataclasses import dataclass, field
from typing import List, Union

from loguru import logger

from todo.core import TodoItem, TodoTxt

from .context import BaseContext
from .schema import BaseConfig, Option, Parameter


@dataclass
class BaseProject:
    config: BaseConfig = field(default_factory=BaseConfig)
    name: str = ""
    scripts: List[BaseContext] = field(default_factory=list)

    def __post_init__(self):
        if self.name and not self.config.name:
            self.config.name = self.name

    def __call__(self, todotxt: TodoTxt):
        self._add_init_script(todotxt)
        todolist = todotxt[self.name].alert().sort()
        logger.info(f"Start Project: {self.name}")
        logger.trace(f"TodoList:\n{todolist}")
        todolist = todolist.todo_list

        def process(todo: TodoItem, type: Union[Parameter, int] = 1) -> Union[TodoItem, List[TodoItem]]:
            if isinstance(type, int):
                type = Parameter(type)
            if type == Option.SEARCH:
                assert len(todo.context) == 1
                query = todo.context[0]
                return todotxt.search(query)
            if type == Option.FORMAT:
                todo = self._format_todo(todo, self.name == todotxt._root_project)
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
            if type == Option.ARCHIVE:
                todo.context.append("#archive")
            return todo

        index = 0
        while index < len(todolist):
            todo = todolist[index]
            logger.trace(f"Processing: {todo}")
            if "#break" in todo.context:
                todo.context.remove("#break")
            if "#all" in todo.context:
                todo.context.remove("#all")
            if "#archive" in todo.context:
                todo.context.remove("#archive")
            for script in self.scripts:
                if script.match(todo.context):
                    script(todo, process)
                    if "#all" in todo.context:
                        logger.trace(f"Modifying All with @{script.name}: {todo}")
                        todo.context.remove("#all")
                        script.modify_all(todo, todotxt[self.name], process)
                    if "#archive" in todo.context:
                        logger.trace("Archiving TodoTXT")
                        todo.context.remove("#archive")
                        todotxt.archive()
                    if "#break" in todo.context:
                        logger.trace(f"Skipping: {todo}")
                        todo.context.remove("#break")
                        break
            index += 1

    def _format_todo(self, todo: TodoItem, is_system: bool):
        return self.config.format_todo(todo, is_system)

    def _add_init_script(self, todotxt: TodoTxt):
        self.config.add_init_script(todotxt)
