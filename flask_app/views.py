
import redis
from flask import Blueprint, render_template, request, jsonify
import json
import os

views = Blueprint("views", __name__)

r = redis.Redis(
    host=os.getenv("SLACK_HOST"),
    port=16219,
    decode_responses=True,
    username="default",
    password=os.getenv("SLACK_PASSWORD"),
)


@views.route("/slack/interactions", methods=["POST"])
def slack_interactions():
    """
    This endpoint is called by Slack when a user clicks
    Approve or Reject.
    """
    payload = json.loads(request.form["payload"])

    action = payload["actions"][0]
    action_value = action["value"]

    decision, task_id = action_value.split("|", 1)

    if decision == "approve":
        r.set(task_id, "approved")
        response_text = "Approved"

    elif decision == "reject":
        r.set(task_id, "rejected")
        response_text = "Rejected"

    else:
        return jsonify({"text": "Unknown action"}), 400

    return jsonify({
        "replace_original": False,
        "text": f"{response_text} (task `{task_id}`)"
    })