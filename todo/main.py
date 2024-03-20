from loguru import logger

from todo.core import open_todotxt
from todo.custom import Config
from todo.project import Project

file_path = "data/project/core.yaml"
configs = Config.load_all(file_path)
project = {}
for config in configs:
    project[config.name] = Project(config)

with open_todotxt("data/todo.txt") as todotxt:
    if todotxt.root_project in project.keys():
        project[todotxt.root_project](todotxt)
    for project_name in [key for key in project.keys() if key != todotxt.root_project]:
        project[project_name](todotxt)
    logger.success(f"\n{todotxt}")
