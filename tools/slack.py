from langchain.tools import tool
from flask_app.slack_approval import ask_for_approval, wait_for_approval

@tool
def ask_and_wait_approval(task_id: str, title: str, body: str, timeout: int=600):
    """
    Sends an interactive Slack message requesting human approval for a task,
    then waits for the user's decision by polling Redis.

    Returns "approved", "rejected", or "timeout".
    """
    ask_for_approval(task_id, title, body)
    return wait_for_approval(task_id, timeout)