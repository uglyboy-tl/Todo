import re
from dataclasses import dataclass, field

from gotify import Gotify as Notify

from todo.core import TodoItem
from todo.project import BaseNotify
from todo.utils import config


@dataclass
class Gotify(BaseNotify):
    url: str = config.gotify_url
    _client: Notify = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self._client = Notify(base_url=self.url, app_token=self.id)

    @staticmethod
    def _validate(id: str):
        pattern = re.compile(r"^A[a-zA-Z0-9.\-_]{14}$")
        if not pattern.match(id):
            raise ValueError("Invalid Gotify app token")

    def __call__(self, todo: TodoItem, process):
        self._client.create_message(
            todo.message,
            title="消息提醒",
        )
