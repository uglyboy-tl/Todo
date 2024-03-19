from typing import Any, List, Optional

from todo.core import TodoItem

from .schema import BaseConfig


class Config(BaseConfig):
    archive_recurrence: str = "1d"
    due_with_unfinished: bool = False
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
