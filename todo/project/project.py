from dataclasses import dataclass
from typing import List, Type

from loguru import logger
from stevedore import ExtensionManager

from .base import BaseProject
from .context import BaseContext, BaseFilter, BaseNotify


@dataclass
class Project(BaseProject):
    def __post_init__(self):
        super().__post_init__()
        if self.config and not self.name:
            self.name = self.config.name
        if self.config and not self.scripts:
            context_plugins: List[Type[BaseContext]] = ExtensionManager(namespace="todo.project", invoke_on_load=False)
            context_private_plugins: List[Type[BaseContext]] = ExtensionManager(
                namespace=f"todo.project.{self.name}", invoke_on_load=False
            )

            context_type_set = {context.name for context in context_plugins}
            context_private_type_set = {context.name for context in context_private_plugins}

            for script in self.config.merge_preset_scripts(self.config.script_configs):
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
