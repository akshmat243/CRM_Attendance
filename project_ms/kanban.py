TASK_STATUS_FLOW = {
    "todo": ["in_progress"],
    "in_progress": ["review", "blocked"],
    "review": ["done", "in_progress"],
    "blocked": ["in_progress"],
    "done": [],
}

KANBAN_STATUSES = ["todo", "in_progress", "review", "done"]
