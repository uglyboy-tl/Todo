import smtplib
import time
from email.mime.text import MIMEText
from typing import List, Type
from unittest.mock import patch

from stevedore import ExtensionManager

from todo.core import TodoItem, TodoTxt
from todo.plugins.email import Email
from todo.project import BaseContext


def test_load_as_extensions():
    context_plugins: List[Type[BaseContext]] = ExtensionManager(namespace="todo.project", invoke_on_load=False)
    assert "email" in [context.name for context in context_plugins]
    for context_type in context_plugins:
        if context_type.name != "email":
            continue
        context = context_type.plugin("alert", "uglyboy@uglyboy.cn")
        assert context.name == "alert"


def test_email_notification():
    email = Email("alert", "uglyboy@uglyboy.cn")
    todo = TodoItem("Test Todo")
    todotxt = TodoTxt()

    with (
        patch.object(smtplib.SMTP_SSL, "login") as mock_login,
        patch.object(smtplib.SMTP_SSL, "sendmail") as mock_sendmail,
        patch.object(smtplib.SMTP_SSL, "quit") as mock_quit,
    ):
        email(todo, todotxt)

        msg = MIMEText(f"{str(todo)}", "plain", "utf-8")
        msg["Subject"] = "[代办提醒]" + todo.message
        msg["From"] = "Notice <" + email.email + ">"
        msg["To"] = email.id
        msg["Date"] = time.strftime("%a, %d %b %Y %H:%M:%S %z")

        mock_login.assert_called_once_with(email.email, email.password)
        mock_sendmail.assert_called_once_with(email.email, email.id, msg.as_string())
        mock_quit.assert_called_once()


def test_validate_email():
    email = Email("alert", "uglyboy@uglyboy.cn")
    invalid_email = "invalid_email"

    try:
        email._validate(invalid_email)
        raise AssertionError("Expected ValueError to be raised")
    except ValueError as e:
        assert str(e) == "Invalid email address"
