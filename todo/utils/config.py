#!/usr/bin/env python3

import os
from dataclasses import dataclass

from .singleton import singleton


@singleton
@dataclass
class Config:
    # SMTP
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", 465))
    smtp_email: str = os.getenv("SMTP_EMAIL", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    # Gotify
    gotify_url: str = os.getenv("GOTIFY_URL", "https://notify.uglyboy.cn")


config = Config()
