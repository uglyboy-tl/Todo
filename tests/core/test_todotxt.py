from datetime import datetime, timedelta
from pathlib import Path

from todo.core import TodoItem, TodoTxt


def test_append():
    todo_txt = TodoTxt()
    todo_item = TodoItem("Test todo")
    todo_txt.append(todo_item)
    assert todo_item in todo_txt
    assert todo_item == todo_txt[-1]


def test_done_with_int():
    todo_txt = TodoTxt(todo_list=[])
    todo_item = TodoItem("Test todo")
    todo_txt.append(todo_item)
    todo_txt.done(0)
    assert todo_item.completed


def test_done_with_todo_item():
    todo_txt = TodoTxt()
    todo_item = TodoItem("Test todo")
    todo_txt.append(todo_item)
    todo_txt.done(todo_item)
    assert todo_item.completed


def test_done_with_recurrence():
    todo_txt = TodoTxt(todo_list=[])
    todo_item = TodoItem("Test todo rec:1d", False, "A")
    todo_txt.append(todo_item)
    todo_txt.done(todo_item)
    assert todo_item.completed
    assert len(todo_txt) == 2
    assert todo_txt[0].description == todo_item.description
    assert todo_txt[1].description == todo_item.description
    assert todo_txt[1].due.strftime("%Y-%m-%d") == (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def test_done_without_recurrence():
    todo_txt = TodoTxt(todo_list=[])
    todo_item = TodoItem("Test todo", False, "A")
    todo_txt.append(todo_item)
    todo_txt.done(todo_item)
    assert todo_item.completed
    assert len(todo_txt) == 1


def test_done_with_due_date():
    todo_txt = TodoTxt(todo_list=[])
    todo_item = TodoItem("Test todo rec:1d", False, "A", datetime.now() + timedelta(days=1), datetime.now())
    todo_txt.append(todo_item)
    todo_txt.done(todo_item)
    assert todo_item.completed
    assert len(todo_txt) == 2
    assert todo_txt[1].due is not None


def test_done_with_index():
    todo_txt = TodoTxt(todo_list=[])
    todo_item = TodoItem("Test todo", False, "A")
    todo_txt.append(todo_item)
    todo_txt.done(0)
    assert todo_item.completed


def test_sort():
    todo_txt = TodoTxt(todo_list=[])
    todo_item1 = TodoItem("Test todo 1", False, "A", datetime.now() + timedelta(days=1))
    todo_item2 = TodoItem(
        "Test todo 2",
        False,
        "B",
        datetime.now() + timedelta(days=2),
    )
    todo_txt.append(todo_item1)
    todo_txt.append(todo_item2)
    assert todo_txt[0] == todo_item1
    assert todo_txt[1] == todo_item2


def test_contains():
    todo_txt = TodoTxt(todo_list=[])
    todo_item = TodoItem(
        "Test todo",
        False,
        "A",
    )
    todo_txt.append(todo_item)
    assert todo_item in todo_txt


def test_str():
    todo_txt = TodoTxt(todo_list=[])
    todo_item = TodoItem("Test todo", False, "A")
    todo_txt.append(todo_item)
    assert str(todo_txt) == str(todo_item)


def test_achieve_with_default_done_file():
    todo_txt = TodoTxt(todo_list=[])
    todo_item1 = TodoItem("Test todo 1", False, "A")
    todo_item2 = TodoItem("Test todo 2", True, "B")
    todo_txt.append(todo_item1)
    todo_txt.append(todo_item2)
    todo_txt.achieve()
    assert len(todo_txt) == 1
    assert todo_item1 in todo_txt
    assert todo_item2 not in todo_txt


def test_achieve_with_custom_done_file():
    todo_txt = TodoTxt(todo_list=[])
    todo_item1 = TodoItem("Test todo 1", False, "A")
    todo_item2 = TodoItem("Test todo 2", True, "B")
    todo_txt.append(todo_item1)
    todo_txt.append(todo_item2)
    done_file = "data/test/done.txt"
    todo_txt.achieve(done_file)
    assert len(todo_txt) == 1
    assert todo_item1 in todo_txt
    assert todo_item2 not in todo_txt
    assert Path(done_file).exists()


def test_achieve_with_empty_todo_list():
    todo_txt = TodoTxt(todo_list=[])
    todo_txt.achieve()
    assert len(todo_txt) == 0
