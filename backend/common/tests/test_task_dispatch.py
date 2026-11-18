"""Tests for no-worker email task dispatch."""

from unittest.mock import MagicMock, patch

from django.test import override_settings

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


@override_settings(QSTASH_TOKEN="test-token")
def test_publishes_to_qstash_when_callback_is_configured(monkeypatch):
    task = MagicMock()
    task.name = "common.tasks.send_welcome_email"
    monkeypatch.setenv(
        "QSTASH_EMAIL_CALLBACK_URL",
        "https://example.test/api/email/deliver/",
    )
    with patch("common.task_dispatch.publish_json", return_value={"messageId": "m1"}) as publish:
        result = dispatch_email_task(task, "user-123")

    assert result == "queued"
    publish.assert_called_once_with(
        "https://example.test/api/email/deliver/",
        {
            "task": "common.tasks.send_welcome_email",
            "args": ["user-123"],
            "kwargs": {},
        },
        retries=3,
    )
    task.apply.assert_not_called()


@override_settings(QSTASH_TOKEN="test-token")
def test_falls_back_inline_when_qstash_publish_fails(monkeypatch):
    from common.qstash_delivery import QStashError

    task = MagicMock()
    task.apply.return_value = "sent"
    monkeypatch.setenv(
        "QSTASH_EMAIL_CALLBACK_URL",
        "https://example.test/api/email/deliver/",
    )
    with patch("common.task_dispatch.publish_json", side_effect=QStashError("offline")):
        result = dispatch_email_task(task, "user-123")

    assert result == "sent"
    task.apply.assert_called_once_with(
        args=("user-123",), kwargs={}, throw=True
    )
