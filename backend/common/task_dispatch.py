"""QStash-first email dispatch with an inline fallback for small deployments."""

import logging
import os

from django.conf import settings

from common.qstash_delivery import QStashError, publish_json

logger = logging.getLogger(__name__)


def dispatch_email_task(task, *args, **kwargs):
    """Publish email work to QStash when configured, otherwise run inline.

    The QStash callback is restricted to an explicit allowlist in
    QStashEmailDeliveryView. If publishing is unavailable, the bounded Resend
    task runs inline so signup does not silently lose the email on deployments
    without a Celery worker.
    """
    callback_url = os.environ.get("QSTASH_EMAIL_CALLBACK_URL", "").strip()
    if callback_url and getattr(settings, "QSTASH_TOKEN", ""):
        try:
            publish_json(
                callback_url,
                {
                    "task": getattr(task, "name", ""),
                    "args": list(args),
                    "kwargs": kwargs,
                },
                retries=3,
            )
            return "queued"
        except QStashError:
            logger.warning(
                "Could not publish email task %s; attempting inline delivery",
                getattr(task, "name", repr(task)),
                exc_info=True,
            )

    try:
        return task.apply(args=args, kwargs=kwargs, throw=True)
    except Exception:
        logger.exception(
            "Inline email task %s failed",
            getattr(task, "name", repr(task)),
        )
        return None
