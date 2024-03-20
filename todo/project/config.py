from typing import Any, Dict, List, Optional

from todo.core import TodoItem

from .schema import BaseConfig

PRESET_SCRIPTS = [
    "done",
    "update",
    "time_filter",
    "date_filter",
    "weather_filter",
    "check_holiday",
    "weather",
    "notify",
]

OPTION_SCRITPS = [
    "weather",
    "notify",
]


class Config(BaseConfig):
    archive_recurrence: str = "1d"
    due_with_unfinished: bool = True
    alert_days: int = 0

    def model_post_init(self, __context: Any):
        super().model_post_init(__context)

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

    def _get_init_config(self):
        init_config = super()._get_init_config()
        init_config["due_with_unfinished"] = self.due_with_unfinished
        init_config["alert_days"] = self.alert_days
        if self.name == "SYSTEM":
            init_config["archive_recurrence"] = self.archive_recurrence
        return init_config

    def format_todo(self, todo: TodoItem):
        todo = super().format_todo(todo)
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
