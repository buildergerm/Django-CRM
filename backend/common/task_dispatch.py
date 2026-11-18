"""Small-deployment email dispatch without requiring a Celery worker.

The hosted free-tier deployment has no always-on worker. Running these bounded,
idempotent email tasks inline after the database commit ensures welcome and
onboarding messages are actually attempted. Passwordless sign-in delivery has
its own QStash callback path; this helper is for ordinary notification emails.
"""
import logging

logger = logging.getLogger(__name__)


def dispatch_email_task(task, *args, **kwargs):
    """Execute an email task inline so deployments without workers still send.

    Resend calls have a bounded HTTP timeout and task failures are logged rather
    than allowed to break account or organization creation. If a dedicated
    worker is provisioned later, this helper can be switched to queue mode.
    """
    try:
        return task.apply(args=args, kwargs=kwargs, throw=True)
    except Exception:
        logger.exception(
            "Inline email task %s failed",
            getattr(task, "name", repr(task)),
        )
        return None
