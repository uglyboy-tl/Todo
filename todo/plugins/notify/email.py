import re
import smtplib
import time
from dataclasses import dataclass, field
from email.mime.text import MIMEText

from todo.core import TodoItem
from todo.project import BaseNotify
from todo.utils import config


@dataclass
class Email(BaseNotify):
    smtp: str = config.smtp_host
    port: int = config.smtp_port
    email: str = config.smtp_email
    password: str = config.smtp_password
    _smtp: smtplib.SMTP_SSL = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        self._smtp = smtplib.SMTP_SSL(self.smtp, self.port)

    def __call__(self, todo: TodoItem, process):
        msg = MIMEText(f"{str(todo)}", "plain", "utf-8")
        msg["Subject"] = "[代办提醒]" + todo.message
        msg["From"] = "Notice <" + self.email + ">"
        msg["To"] = self.id
        msg["Date"] = time.strftime("%a, %d %b %Y %H:%M:%S %z")

        self._smtp.login(self.email, self.password)
        self._smtp.sendmail(self.email, self.id, msg.as_string())
        self._smtp.quit()

    @staticmethod
    def _validate(id: str):
        pattern = re.compile(
            r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
        )
        if not pattern.match(id):
            raise ValueError("Invalid email address")
