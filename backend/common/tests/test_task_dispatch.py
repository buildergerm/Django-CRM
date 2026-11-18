"""Tests for no-worker email task dispatch."""

from unittest.mock import MagicMock

from common.task_dispatch import dispatch_email_task


def test_runs_email_task_inline_without_requiring_a_worker():
    task = MagicMock()
    task.apply.return_value = "sent"

    result = dispatch_email_task(task, "user-123", important=True)

    assert result == "sent"
    task.apply.assert_called_once_with(
        args=("user-123",), kwargs={"important": True}, throw=True
    )
    task.delay.assert_not_called()


def test_email_failure_does_not_escape_account_creation_flow():
    task = MagicMock()
    task.apply.side_effect = RuntimeError("Email provider unavailable")

    assert dispatch_email_task(task, "user-123") is None
    task.apply.assert_called_once_with(
        args=("user-123",), kwargs={}, throw=True
    )
