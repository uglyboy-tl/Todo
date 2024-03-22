from dataclasses import dataclass, field
from typing import List, Union

from loguru import logger

from todo.core import TodoItem, TodoTxt

from .context import BaseContext, BaseFilter, BasePreparation
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

        def process(
            todo: TodoItem, param: Union[Parameter, int] = 1
        ) -> Union[TodoItem, List[TodoItem], List[BaseContext]]:
            if isinstance(param, int):
                param = Parameter(param)
            if param == Option.SEARCH:
                assert len(todo.context) == 1
                query = todo.context[0]
                return todotxt.search(query)
            if param == Option.FORMAT:
                todo = self._format_todo(todo, self.name == todotxt.root_project)
            if param == Option.ADD:
                todotxt.append(todo)
                logger.trace(f"Append todo: {todo}")
            if param == Option.EXECUTE:
                todolist.append(todo)
            if param == Option.REMOVE:
                todotxt.remove(todo)
                logger.trace(f"Remove todo: {todo}")
                if todo in todolist:
                    todolist.remove(todo)
            if param == Option.BREAK:
                todo.context.append("#break")
            if param == Option.DONE:
                todotxt.done(todo)
            if param == Option.MODIFY_ALL:
                todo.context.append("#all")
            if param == Option.ARCHIVE:
                todotxt.archive()
                logger.trace("Archiving completed todos")
            if param == Option.TYPE:
                type_list = []
                for script in self.scripts:
                    if script.match(todo.context):
                        type_list.append(script)
                return type_list
            return todo

        index = 0
        while index < len(todolist):
            todo = todolist[index]
            logger.trace(f"Processing: {todo}")
            if "#all" in todo.context:
                todo.context.remove("#all")
            if "#break" in todo.context:
                todo.context.remove("#break")
            for script in self.scripts:
                if script.match(todo.context):
                    script(todo, process)
                    if "#all" in todo.context:
                        todo.context.remove("#all")
                        logger.trace(f"Modifying All with @{script.name}: {todo}")
                        script.modify_all(todo, todotxt[self.name], process)
                    if "#break" in todo.context:
                        todo.context.remove("#break")
                        # Filter 和 Preparation 才可以跳过
                        if not isinstance(script, BaseFilter) and not isinstance(script, BasePreparation):
                            continue
                        logger.trace(f"Skipping: {todo}")
                        break
            index += 1

    def _format_todo(self, todo: TodoItem, disable_project_name: bool):
        return self.config.format_todo(todo, disable_project_name)

    def _add_init_script(self, todotxt: TodoTxt):
        self.config.add_init_script(todotxt)
