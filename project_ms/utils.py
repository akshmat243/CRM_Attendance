def calculate_percentage(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100)


def percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


from datetime import timedelta

WEEKDAY_MAP = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}

def calculate_end_date(start_date, duration_weeks, working_days):
    total_working_days = duration_weeks * len(working_days)
    days_added = 0
    current = start_date

    working_indexes = [WEEKDAY_MAP[d] for d in working_days]

    while days_added < total_working_days:
        if current.weekday() in working_indexes:
            days_added += 1
        current += timedelta(days=1)

    return current - timedelta(days=1)

#############################################################################################################################################
import re
from django.contrib.auth import get_user_model

User = get_user_model()

MENTION_REGEX = r'@([\w.@+-]+)'


def extract_mentions(text):
    """
    Extract usernames/emails from @mentions
    """
    if not text:
        return []

    usernames = set(re.findall(MENTION_REGEX, text))

    return list(
        User.objects.filter(
            username__in=usernames
        )
    )


#############################################################################################################################################

from project_ms.models import AuditLog


def log_audit(
    *,
    user,
    action,
    instance,
    old_data=None,
    new_data=None,
    ip_address=None
):
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        old_data=old_data,
        new_data=new_data,
        ip_address=ip_address,
    )


from django.forms.models import model_to_dict
from datetime import date, datetime
from uuid import UUID


def serialize_instance(instance):
    data = model_to_dict(instance)

    for key, value in data.items():
        if isinstance(value, (datetime, date)):
            data[key] = value.isoformat()
        elif isinstance(value, UUID):
            data[key] = str(value)

    return data
