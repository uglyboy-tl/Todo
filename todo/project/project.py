from dataclasses import dataclass
from typing import Any, Dict, List, Type

from loguru import logger
from stevedore import ExtensionManager

from .base import BaseProject
from .config import Config
from .context import BaseContext, BaseFilter

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
    "alert",
    "weather",
    "notify",
]


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

            for script in self.merge_system_scripts(self.config.script_configs):
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
                if x.name not in ["done", "update", "notify"]
                else 0,
                reverse=True,
            )
            logger.trace(f"Project:{self.name}\nScripts: {[script.name for script in self.scripts]}")

    @classmethod
    def load(cls, file_path: str, name: str = "SYSTEM"):
        config: Config = Config.load(file_path, name)
        return cls(config)

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
