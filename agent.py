import uuid

from langchain_core.tools import tool, Tool, StructuredTool
from tools.date import getDate
from flask_app.slack_approval import wait_for_approval
from tools.imageGen import imageGen
from tools.search import search, searchquery
from tools.scrape import scrape_tool
from tools.slack import ask_and_wait_approval
from tools.posting import post_to_discord
from tools.wikipedia import wikipedia
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from llm.llm import model
from llm.llm_summary import summarize_one_line
import json



system_prompt = SystemMessage(
    content=[
        {
            "type": "text",
            "text": (
                "You are a ReAct (Reasoning and Acting) Social Media Posting Agent.\n\n"
                "Your task is to create a high-quality Twitter post AND a historically accurate image prompt "
                "about an invention, discovery, or innovation that happened on this exact day in history.\n\n"
                "IMPORTANT TOOL RULES (STRICT):\n"
                "You MUST call the wikipedia tool to retrieve structured, factual information about the invention. You are allowed to use it only 5 times\n"
                "You MUST call the summmarizeoneline tool if you use the wikipedia tool. The output from the summarizeonlinetool is the image prompt.\n"
                "You MUST use the image generation tool.\n"
                "You MUST use the ask_and_wait_approval tool after image generation\n"
                "You MUST post to discord using the discord post tool, if slack request is approved.\n"

                "You must reason step-by-step and decide whether to use a tool or produce a final answer.\n\n"

                "When responding, use EXACTLY ONE of the following JSON formats.\n\n"

                "If you need to use a tool:\n"
                "{\n"
                "  \"thought\": \"Explain what information is missing and why a tool is required\",\n"
                "  \"action\": {\n"
                "    \"name\": \"Tool name (getDate, search, wikipedia, image_generation)\",\n"
                "    \"reason\": \"Why this tool is necessary\",\n"
                "    \"input\": \"Exact input to the tool\"\n"
                "  }\n"
                "}\n\n"

                "If you have completed ALL required tool steps, it is a MUST to respond with:\n"
                "{\n"
                "    \"tweet_text\": \"A compelling 500 character tweet with a strong hook, year, and why the invention mattered\",\n"
                "    \"image_url\": \"Image url gotten from inage generation tool\"\n"
                "  }\n"

                "STYLE RULES:\n"
                "- Start tweets with 'On this day in history...' or 'Did you know...'\n"
                "- Always include the year\n"
                "- Focus on impact, not trivia\n"
                "- No hashtags unless explicitly requested\n"
                "- If Wikipedia information is insufficient, say so and search again\n"
            )
        }
    ]
)



tools = [getDate, imageGen, search, searchquery, wikipedia, scrape_tool, summarize_one_line, post_to_discord, ask_and_wait_approval]
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt
)

import asyncio

from langchain_core.callbacks import AsyncCallbackHandler

class AgentLogger(AsyncCallbackHandler):
    async def on_agent_action(self, action, **kwargs):
        print(f"[AGENT ACTION] {action}")

    async def on_agent_finish(self, finish, **kwargs):
        print(f"[AGENT FINISH] {finish}")

    async def on_tool_start(self, tool_name, input_text, **kwargs):
        print(f"[TOOL START] {tool_name} with input: {input_text}")

    async def on_tool_end(self, output, **kwargs):
        print(f"[TOOL END] {output}")

# When running your agent
logger = AgentLogger()


async def run_agent():
    user_input = "Create a tweet and image prompt for today's historical inventions, discoveries, or innovations."

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config={"callbacks": [logger]}  # Fixed: callbacks go in config
    )

    # Fixed: extract the last AI message and parse JSON from it
    last_message = response["messages"][-1]
    content = last_message.content

    try:
        # Handle case where model wraps JSON in markdown code fences
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        parsed = json.loads(content.strip())
        tweet_text = parsed.get("tweet_text")
        image_url = parsed.get("image_url")

        print("\n✅ Tweet text:\n", tweet_text)
        print("\n✅ Image url:\n", image_url)
        task_id = f"tweet-{uuid.uuid4()}"
        approval_status = await asyncio.to_thread(wait_for_approval, task_id, 600)
        return approval_status

    except json.JSONDecodeError:
        print("Agent returned non-JSON output:\n", content)
        return content


if __name__ == "__main__":
    asyncio.run(run_agent())
