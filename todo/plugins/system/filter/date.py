import json
from dataclasses import dataclass

from todo.project import BaseFilter


@dataclass
class DateFilter(BaseFilter):
    regex: str = r"^holiday|workday$"
    data_name: str = "#holiday"
    script_name: str = "check_holiday"

    def _check(self, data: str, date_filter: str):
        obj = json.loads(data)
        if date_filter == "workday":
            return obj["type"] in [0, 3]
        elif date_filter == "holiday":
            return obj["type"] in [1, 2]
        else:
            return date_filter == obj["name"]
