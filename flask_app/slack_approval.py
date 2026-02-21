
from langchain.tools import tool
import requests, time, os, dotenv, redis

dotenv.load_dotenv()

r = redis.Redis(
    host=os.getenv("SLACK_HOST"),
    port=16219,
    decode_responses=True,
    username="default",
    password=os.getenv("SLACK_PASSWORD"),
)


def ask_for_approval(task_id, title, body):

    SLACK_BOT_TOKEN = os.environ["BOT_USER_OAUTH_TOKEN"]
    CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]

    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-type": "application/json",
    }

    data = {
        "channel": CHANNEL_ID,
        "text": title,
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": body},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve"},
                        "style": "primary",
                        "value": f"approve|{task_id}",
                        "action_id": "approve_button",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Reject"},
                        "style": "danger",
                        "value": f"reject|{task_id}",
                        "action_id": "reject_button",
                    },
                ],
            },
        ],
    }

    response = requests.post("https://slack.com/api/chat.postMessage", json=data, headers=headers)
    print(response.json())
    r.set(task_id, "pending")


def wait_for_approval(task_id, timeout=600):
    for _ in range(timeout):
        status = r.get(task_id)
        if status and status != "pending":
            return status
        time.sleep(1)
    return "timeout"

