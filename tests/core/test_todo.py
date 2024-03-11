from datetime import datetime

import pytest

from todo.core import TodoItem


def test_post_init_creation_date_before_completion_date():
    todo = TodoItem(
        "test",
        creation_date=datetime.strptime("2022-01-01", "%Y-%m-%d"),
        completion_date=datetime.strptime("2022-01-02", "%Y-%m-%d"),
    )
    assert todo.creation_date < todo.completion_date


def test_post_init_creation_date_after_completion_date():
    with pytest.raises(AssertionError):
        TodoItem(
            "test",
            creation_date=datetime.strptime("2022-01-02", "%Y-%m-%d"),
            completion_date=datetime.strptime("2022-01-01", "%Y-%m-%d"),
        )


def test_post_init_creation_date_equal_to_completion_date():
    with pytest.raises(AssertionError):
        TodoItem(
            "test",
            creation_date=datetime.strptime("2022-01-02", "%Y-%m-%d"),
            completion_date=datetime.strptime("2022-01-01", "%Y-%m-%d"),
        )


def test_get_metadata_projects():
    todo = TodoItem("+project1 +project2")
    assert todo.project == ["project1", "project2"]


def test_get_metadata_contexts():
    todo = TodoItem("@context1 @context2")
    assert todo.context == ["context1", "context2"]


def test_get_metadata_recurrence_days():
    todo = TodoItem("t rec:5d")
    assert todo.recurrence == "5d"


def test_get_metadata_recurrence_weeks():
    todo = TodoItem("t rec:2w")
    assert todo.recurrence == "2w"


def test_get_metadata_recurrence_months():
    todo = TodoItem("t rec:3m")
    assert todo.recurrence == "3m"


def test_get_metadata_invalid_recurrence():
    with pytest.raises(ValueError):
        TodoItem("rec:3y")


def test_get_metadata_due_date():
    todo = TodoItem("t due:2022-12-31")
    assert todo.due == datetime.strptime("2022-12-31", "%Y-%m-%d")


def test_get_metadata_multiple_recurrence():
    with pytest.raises(ValueError):
        TodoItem("rec:5d rec:2w")


def test_get_metadata_multiple_due_dates():
    with pytest.raises(ValueError):
        TodoItem("due:2022-12-31 due:2023-01-01")


def test_from_string_completed():
    todo = TodoItem.from_string("x 2022-01-02 2022-01-01 Test todo item")
    assert todo.completed is True
    assert todo.completion_date == datetime.strptime("2022-01-02", "%Y-%m-%d")
    assert todo.creation_date == datetime.strptime("2022-01-01", "%Y-%m-%d")
    assert todo.description == "Test todo item"


def test_from_string_incomplete():
    todo = TodoItem.from_string("2022-01-02 Test todo item")
    assert todo.completed is False
    assert todo.completion_date is None
    assert todo.creation_date == datetime.strptime("2022-01-02", "%Y-%m-%d")
    assert todo.description == "Test todo item"


def test_from_string_with_priority():
    todo = TodoItem.from_string("(A) 2022-01-02 Test todo item")
    assert todo.completed is False
    assert todo.completion_date is None
    assert todo.creation_date == datetime.strptime("2022-01-02", "%Y-%m-%d")
    assert todo.description == "Test todo item"
    assert todo.priority == "A"


def test_from_string_invalid_completion_date():
    with pytest.raises(ValueError):
        TodoItem.from_string("x 2022-01-02-01 2022-01-01 Test todo item")


def test_from_string_invalid_creation_date():
    with pytest.raises(ValueError):
        TodoItem.from_string("2022-01-01-01 Test todo item")


def test_from_string_no_description():
    with pytest.raises(ValueError):
        TodoItem.from_string("2022-01-02")


def test_from_string_multiple_dates():
    with pytest.raises(ValueError):
        TodoItem.from_string("x 2022-01-02 2022-01-01 2022-01-03 Test todo item")


def test_todo_item_to_string_completed():
    todo = TodoItem(
        completed=True,
        completion_date=datetime.strptime("2022-01-02", "%Y-%m-%d"),
        creation_date=datetime.strptime("2022-01-01", "%Y-%m-%d"),
        description="Test todo item",
    )
    expected_output = "x 2022-01-02 2022-01-01 Test todo item"
    assert str(todo) == expected_output


def test_todo_item_to_string_incomplete():
    todo = TodoItem(
        completed=False,
        creation_date=datetime.strptime("2022-01-02", "%Y-%m-%d"),
        description="Test todo item",
    )
    expected_output = "2022-01-02 Test todo item"
    assert str(todo) == expected_output


def test_todo_item_to_string_with_priority():
    todo = TodoItem(
        completed=False,
        creation_date=datetime.strptime("2022-01-02", "%Y-%m-%d"),
        description="Test todo item",
        priority="A",
    )
    expected_output = "(A) 2022-01-02 Test todo item"
    assert str(todo) == expected_output


def test_todo_item_to_string_no_completion_date():
    todo = TodoItem(
        completed=True,
        creation_date=datetime.strptime("2022-01-02", "%Y-%m-%d"),
        description="Test todo item",
    )
    expected_output = "x 2022-01-02 Test todo item"
    assert str(todo) == expected_output


def test_todo_item_to_string_no_creation_date():
    todo = TodoItem(
        completed=True,
        completion_date=datetime.strptime("2025-01-01", "%Y-%m-%d"),
        description="Test todo item",
    )
    expected_output = f"x 2025-01-01 {datetime.now().strftime('%Y-%m-%d')} Test todo item"
    assert str(todo) == expected_output


def test_todo_item_to_string_no_dates():
    todo = TodoItem(completed=False, description="Test todo item", creation_date=None)
    expected_output = "Test todo item"
    assert str(todo) == expected_output


def test_todo_item_to_string_empty_description():
    with pytest.raises(ValueError):
        TodoItem(
            completed=False,
            creation_date=datetime.strptime("2022-01-02", "%Y-%m-%d"),
            description="",
        )


def test_done():
    todo = TodoItem("test")
    assert todo.completed is False
    assert todo.completion_date is None

    todo.done()
    assert todo.completed is True
    assert todo.completion_date is not None
