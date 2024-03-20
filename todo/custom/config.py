from typing import Any, Dict, List, Optional

from todo.core import TodoItem
from todo.project.schema import BaseConfig

# 相当于 context 的保留字段
PRESET_SCRIPTS = [
    "done",
    "update",
    "time_filter",
    "date_filter",
    "weather_filter",
    "fetch_date",
    "fetch_weather",
    "notify",
]

# 可配置的保留字段
OPTION_SCRITPS = [
    "fetch_weather",
    "notify",
]


class Config(BaseConfig):
    archive_recurrence: str = "1d"
    due_with_unfinished: bool = True
    alert_days: int = 0

    def model_post_init(self, __context: Any):
        self._dict: [str, Dict[str, Any]] = {
            item.get("type") if item.get("type") else item["name"]: item for item in self.script_configs
        }

        self._init_config = self._get_init_config(self.name == "SYSTEM")

        self._process_script_config("archive", self.archive_recurrence and self.name == "SYSTEM")
        self._process_script_config("unfinished", self.due_with_unfinished)
        self._process_script_config("alert", self.alert_days, ["alert_days"])

    def _process_script_config(self, name: str, condition: bool, params: Optional[List[str]] = None):
        if condition:
            if name not in self._dict:
                config = {"name": name, "type": name}
                if params:
                    config.update({param: self._init_config[param] for param in params})
                self.script_configs.append(config)
            elif params:
                self._dict[name].update({param: self._init_config[param] for param in params})
        else:
            if name in self._dict:
                config = self._dict.pop(name)
                self.script_configs.remove(config)

    def _get_init_config(self, is_system: bool = False):
        init_config = super()._get_init_config(is_system)
        self._dict[self.start_script] = init_config
        init_config["due_with_unfinished"] = self.due_with_unfinished
        init_config["alert_days"] = self.alert_days
        if is_system:
            init_config["archive_recurrence"] = self.archive_recurrence
        return init_config

    def format_todo(self, todo: TodoItem, is_system: bool):
        todo = super().format_todo(todo, is_system)
        return todo

    @staticmethod
    def merge_preset_scripts(script_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        option_scripts = [script["name"] for script in script_configs if script["name"] in OPTION_SCRITPS]
        if option_scripts:
            merge_scripts = [
                {"name": script, "type": script} for script in PRESET_SCRIPTS if script not in option_scripts
            ]
        else:
            merge_scripts = [{"name": script, "type": script} for script in PRESET_SCRIPTS]
        merge_scripts.extend(
            [
                script
                for script in script_configs
                if script["name"] not in PRESET_SCRIPTS or script["name"] in OPTION_SCRITPS
            ]
        )
        return merge_scripts
