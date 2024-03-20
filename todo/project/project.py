from dataclasses import dataclass
from typing import List, Type

from loguru import logger
from stevedore import ExtensionManager

from .base import BaseProject
from .config import Config, merge_system_scripts
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

            for script in merge_system_scripts(self.config.script_configs):
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
                else 1
                if x.name not in ["done", "update"] or isinstance(x, BaseNotify)
                else 0,
                reverse=True,
            )
            logger.trace(f"Project:{self.name}\nScripts: {[script.name for script in self.scripts]}")

    @classmethod
    def load(cls, file_path: str, name: str = "SYSTEM"):
        config: Config = Config.load(file_path, name)
        return cls(config)
