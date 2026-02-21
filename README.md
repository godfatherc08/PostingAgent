# 🤖 Historical Facts Social Media Agent

A human-in-the-loop LLM agent that generates historically accurate social media content and publishes it only after explicit human approval via Slack.

---

## Overview

This agent researches inventions, discoveries, or innovations tied to the current date in history, generates a post and an AI image, requests human approval through Slack, and posts to Discord only if approved.

```mermaid
flowchart TD
    U[User] --> A[LLM Agent]
    A --> T[Agent Tools]
    T --> C[Content Generator]
    T --> S[Slack Approval Tool]
    S --> SL[Slack Message - Approve / Reject]
    SL --> W[Flask Webhook]
    W --> R[(Redis)]
    R -->|status| A
    A -->|approved| P[Posting Tool]
    P --> SM[Social Media APIs]
    A -->|rejected / timeout| X[Abort Task]
```

---

## How It Works

The agent is implemented as a **ReAct-style agent** (Reasoning + Acting). Rather than following a fixed pipeline, it reasons step-by-step and invokes tools dynamically. The execution flow is:

1. **Date lookup** — retrieves today's date to anchor the historical search
2. **Research** — uses Google SERP and Wikipedia to find relevant inventions or discoveries
3. **Summarization** — distills findings into a concise social media post and image prompt
4. **Image generation** — calls Leonardo AI to generate a historically themed image
5. **Slack approval** — sends an interactive Slack message with Approve / Reject buttons
6. **Posting** — publishes to Discord only if a human approves within the timeout window

---

## Architecture

The system is split into three cooperating layers:

| Layer | Responsibility |
|---|---|
| **LLM Agent** | ReAct reasoning, tool orchestration, content generation |
| **Tool Layer** | Date, search, Wikipedia, image gen, Slack, Discord posting |
| **Flask + Redis** | Approval state management and webhook handling |

State is managed with a simple polling loop against Redis — intentionally straightforward over a more complex event-driven architecture. Each component is independently replaceable as requirements grow.

---

## Project Structure

```
.
├── agent.py                  # Main agent definition and runner
├── llm/
│   ├── llm.py                # LLM model setup
│   └── llm_summary.py        # One-line summarization tool
├── tools/
│   ├── date.py               # Get today's date
│   ├── imageGen.py           # Leonardo AI image generation
│   ├── search.py             # Google SERP search + BM25 reranker
│   ├── wikipedia.py          # Wikipedia lookup
│   ├── scrape.py             # Web scraping tool
│   ├── slack.py              # Slack approval tool
│   └── posting.py            # Discord webhook posting
└── flask_app/
    ├── app.py                # Flask webhook server
    └── slack_approval.py     # Redis polling for approval status
```

---

## Tools Reference

### `getDate`
Returns today's date in `DD/MM` format to ground the agent's historical search.

```python
@tool
def getDate():
    """Objective: To get today's date in format: DD/MM"""
    date = datetime.date.today()
    return concat(date.day, date.month)
```

---

### `search` + `searchquery`
Queries Google via the Serper API. Results are reranked using **BM25** to surface the most relevant sources before being passed back to the agent.

```python
def reranker(results, search_query):
    documents = [f"{item.get('title', '')} {item.get('snippet', '')}" for item in results]
    tokenized_corpus = [doc.split(" ") for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25.get_top_n(search_query.split(), documents, n=1)
```

> **Scaling note:** The BM25 reranker has been written but is not yet integrated into the live pipeline — this is a planned improvement. 

---

### `imageGen`
Generates an image via the [Leonardo AI API](https://leonardo.ai). Submits a generation job, then polls asynchronously until the image is ready.

```python
@tool
async def imageGen(prompt: str):
    """Generating Images from summarized prompt"""
    gen_id = create_image(prompt)
    image_url = await wait_for_image(gen_id)
    return image_url
```

---

### `ask_and_wait_approval`
Sends an interactive Slack message with **Approve** and **Reject** buttons. Stores a `task_id` in Redis as `"pending"`, then polls until a human responds or the timeout elapses.

```python
def wait_for_approval(task_id, timeout=600):
    for _ in range(timeout):
        status = r.get(task_id)
        if status and status != "pending":
            return status
        time.sleep(1)
    return "timeout"
```

---

### `post_to_discord`
Posts the generated text and image to a Discord channel via webhook embed.

```python
@tool
def post_to_discord(tweet_text: str, image_url: str):
    payload = {
        "content": tweet_text,
        "embeds": [{"image": {"url": image_url}}]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)
```

---

## Agent Prompt & Rules

The agent operates under a strict set of tool-use rules enforced in the system prompt:

- **Must** call `wikipedia` to retrieve factual information (max 5 calls)
- **Must** call `summarizeoneline` on Wikipedia output to produce the image prompt
- **Must** use `imageGen` to generate an image
- **Must** call `ask_and_wait_approval` before any posting
- **Must** call `post_to_discord` only if Slack approval is received

Posts must follow this style:
- Start with `"On this day in history..."` or `"Did you know..."`
- Always include the year
- Focus on impact, not trivia
- No hashtags unless explicitly requested

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd <repo-name>
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
# Leonardo AI
LEONARDO_AI_API_KEY=your_leonardo_key

# Google Serper
SERPER_API_KEY=your_serper_key

# COHERE API KEY
COHERE_API_KEY=your_cohere_key

#
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Slack
BOT_USER_OAUTH_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=your_channel_id

# Redis (for approval state)
SLACK_HOST=your_redis_host
SLACK_PASSWORD=your_redis_password

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### 3. Run the application

The three steps below must be run **in order**, each in its own terminal tab:

**Step 1** — Expose your local server to the internet so Slack can reach it:
```bash
ngrok http 5000
```
Copy the `https://` forwarding URL ngrok gives you and set it as your Slack app's interactivity request URL.

**Step 2** — Start the Flask webhook server:
```bash
python main.py
```

**Step 3** — Run the agent:
```bash
python agent.py
```


---

## Slack

<img width="1920" height="1080" alt="postingagentslack" src="https://github.com/user-attachments/assets/250c8c87-3161-4fa9-8db4-a420ccaac0fe" />

## Discord

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/97fbe819-4f84-4c3e-89c2-693a4ed62496" />


## Scalability Notes

Each component has a clear upgrade path without requiring architectural changes:

| Component | Current | Upgrade Path |
|---|---|---|
| LLM | Currently Cohere` | Swap to more capable model |
| Search ranking | BM25 reranker | Implement Reranker for searches from serper |
| Image generation | Leonardo AI | Better IMage Prompts|
| Approval state | Redis polling |  |
| Posting targets | Discord only | Additional social media APIs like twitter |

---

## Requirements

- Python 3.10+
- Redis instance (cloud or local)
- Slack app with interactive components enabled
- Leonardo AI account
- Serper API key
- Discord webhook URL
