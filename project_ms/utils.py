def calculate_percentage(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100)


def percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)
