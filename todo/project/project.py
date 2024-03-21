from dataclasses import dataclass, field
from typing import List, Set, Type

from loguru import logger
from stevedore import ExtensionManager

from .base import BaseProject
from .context import BaseContext, BaseFilter, BaseNotify


@dataclass
class Project(BaseProject):
    alias: List[str] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if self.config and not self.name:
            self.name = self.config.name
        if not self.alias:
            if self.config.alias:
                self.alias = self.config.alias
            else:
                self.alias.append(self.name)
        logger.trace(f"Project:{self.name}\nAlias: {self.alias}")
        if self.config and not self.scripts:
            context_plugins_list: List[List[Type[BaseContext]]] = []
            context_type_list: List[Set[str]] = []
            context_plugins_list.append(ExtensionManager(namespace="todo.project", invoke_on_load=False))
            for alias in self.alias:
                context_plugins_list.append(ExtensionManager(namespace=f"todo.project.{alias}", invoke_on_load=False))
            for context_plugins in context_plugins_list:
                context_type_list.append({context.name for context in context_plugins})

            for script in self.config.merge_preset_scripts(self.config.script_configs):
                assert "name" in script.keys()
                if "type" not in script.keys():
                    script["type"] = script["name"]
                for context_type, context_plugins in zip(context_type_list, context_plugins_list, strict=False):
                    if script["type"] in context_type:
                        script = context_plugins[script.pop("type")].plugin(**script)
                        break
                else:
                    logger.warning(f"Context `@{script['type']}` not found, skipping")
                    continue
                self.scripts.append(script)

            self.scripts.sort(
                key=lambda x: 2
                if isinstance(x, BaseFilter)
                else 0
                if x.name in ["done", "update"] or isinstance(x, BaseNotify)
                else 1,
                reverse=True,
            )
            logger.trace(f"Project:{self.name}\nScripts: {[script.name for script in self.scripts]}")
