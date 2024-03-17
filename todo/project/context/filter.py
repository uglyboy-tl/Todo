from abc import ABCMeta
from dataclasses import dataclass

from .base import BaseContext


@dataclass
class BaseFilter(BaseContext, metaclass=ABCMeta):
    pass
