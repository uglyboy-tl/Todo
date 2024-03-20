import time
from dataclasses import dataclass

from todo.core import TodoItem, TodoTxt
from todo.project import BaseContext, Option
from todo.project.base import BaseProject

TODAY = time.strftime("%Y-%m-%d")


@dataclass
class TestContext1(BaseContext):
    name: str = "test"

    def __call__(self, todo, process=lambda x, _: x):
        process(TodoItem("Test New todo"), Option.FORMAT | Option.ADD | Option.EXECUTE)
        process(todo, Option.DONE)


@dataclass
class TestContext2(BaseContext):
    name: str = "test"

    def __call__(self, todo, _):
        todo.description = "Modified"


@dataclass
class TestContext3(BaseContext):
    name: str = "remove"

    def __call__(self, todo, process=lambda x, _: x):
        process(todo, Option.REMOVE)


@dataclass
class TestContext4(BaseContext):
    name: str = "break"

    def __call__(self, todo, process=lambda x, _: x):
        process(todo, Option.BREAK)


@dataclass
class TestContext5(BaseContext):
    name: str = "done"

    def __call__(self, todo, process=lambda x, _: x):
        process(todo, Option.DONE)


@dataclass
class TestContext6(BaseContext):
    name: str = "modify_all"

    def __call__(self, todo, process=lambda x, _: x):
        process(todo, Option.MODIFY_ALL)

    def modify_all(self, _: TodoItem, todotxt: TodoTxt, process):
        for todo in todotxt:
            process(todo, Option.REMOVE)


@dataclass
class TestContext7(BaseContext):
    name: str = "archive"

    def __call__(self, todo, process=lambda x, _: x):
        process(todo, Option.ARCHIVE)


@dataclass
class TestContext8(BaseContext):
    name: str = "search"

    def __call__(self, todo, process=lambda x, _: x):
        list = process(TodoItem("@test"), Option.SEARCH)
        print(list)
        todo.description = str(len(list))


def test_call_with_alerts_and_contexts():
    # Setup
    todo_txt = TodoTxt(todo_list=[])
    todo_item1 = TodoItem(f"Test todo @test +project1 due:{TODAY}")
    todo_item2 = TodoItem(f"Test todo @notest +project1 due:{TODAY}")
    todo_txt.append(todo_item1)
    todo_txt.append(todo_item2)
    project = BaseProject(name="project1")

    assert len(todo_txt["project1"].alert()) == 2

    project.scripts = [TestContext2()]

    # Call
    project(todo_txt)

    # Assert
    assert todo_item1.description == "Modified"
    assert todo_item2.description == "Test todo @notest +project1"


def test_call_with_no_alerts():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @notest +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    assert len(todo_txt["project1"].alert()) == 1
    project = BaseProject(name="project1")
    project.scripts = [TestContext2()]

    # Call
    project(todo_txt)

    # Assert
    assert todo_item.description == "Test todo @notest +project1"


def test_call_with_no_contexts():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @test +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    assert len(todo_txt["project1"].alert()) == 1
    project = BaseProject(name="project1")
    project.scripts = []

    # Call
    project(todo_txt)

    # Assert
    assert todo_item.description == "Test todo @test +project1"


def test_process_search_option():
    # Setup
    todo_txt = TodoTxt()
    todo_item1 = TodoItem(f"Test todo @test +project1 due:{TODAY}")
    todo_item2 = TodoItem(f"Another todo @test +project1 due:{TODAY}")
    todo_item = TodoItem(f"Run todo @search +project1 due:{TODAY}")
    todo_txt.append(todo_item1)
    todo_txt.append(todo_item2)
    todo_txt.append(todo_item)
    project = BaseProject(name="project1")
    project.scripts = [TestContext8()]

    # Call
    project(todo_txt)
    print(todo_txt)

    # Assert
    assert todo_item.description == "2"


def test_process_format_option():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @test +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    project = BaseProject(name="project1")
    project.scripts = [TestContext1()]

    # Call
    project(todo_txt)

    # Assert
    assert todo_txt[-1].message.strip() == "Test New todo"


def test_process_add_option():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @test +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    project = BaseProject(name="project1")
    project.scripts = [TestContext1()]

    # Call
    project(todo_txt)

    # Assert
    assert len(todo_txt["project1"]) == 2


def test_process_execute_option():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @test +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    project = BaseProject(name="project1")
    project.scripts = [TestContext1()]

    # Call
    project(todo_txt)

    # Assert
    assert len(todo_txt["project1"].alert()) == 0


def test_process_remove_option():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @remove +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    project = BaseProject(name="project1")
    project.scripts = [TestContext3()]

    # Call
    project(todo_txt)

    # Assert
    assert len(todo_txt["project1"]) == 0


def test_process_break_option():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @break @test +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    project = BaseProject(name="project1")
    project.scripts = [TestContext4(), TestContext1()]

    # Call
    project(todo_txt)

    # Assert
    assert len(todo_txt["project1"]) == 1


def test_process_done_option():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @done +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    project = BaseProject(name="project1")
    project.scripts = [TestContext5()]

    # Call
    project(todo_txt)

    # Assert
    assert todo_item.completed


def test_process_modify_all_option():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @modify_all +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    project = BaseProject(name="project1")
    project.scripts = [TestContext6()]

    # Call
    project(todo_txt)

    # Assert
    assert len(todo_txt["project1"]) == 0


def test_process_archive_option():
    # Setup
    todo_txt = TodoTxt()
    todo_item = TodoItem(f"Test todo @archive @done +project1 due:{TODAY}")
    todo_txt.append(todo_item)
    project = BaseProject(name="project1")
    project.scripts = [TestContext5(), TestContext7()]

    # Call
    project(todo_txt)

    # Assert
    assert len(todo_txt["project1"]) == 0
