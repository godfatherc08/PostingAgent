import time

from langchain_classic.chains.summarize.map_reduce_prompt import prompt_template
from langchain_core.prompts import PromptTemplate
from langchain_cohere import ChatCohere
from langchain.tools import tool
import cohere
import asyncio
from cohere.errors import UnprocessableEntityError

import os
import dotenv

dotenv.load_dotenv()

async def model(prompt):
    while True:
        try:
            co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

            response = co.chat(
                model="command-xlarge-nightly",
                messages=[{"role": "user", "content": prompt}]
            )

            return response.message.content[0].text
        except UnprocessableEntityError as e:
            print("Cohere 422 error encountered. Restarting agent...")
            print("Error message:", e.body.get("message") if hasattr(e, "body") else e)
            time.sleep(5)
            await asyncio.sleep(1)
            continue

def summarize(text):
    prompt_template_obj = PromptTemplate(
        template=prompt_template,
        input_variables=["text"]
    )
    prompt = prompt_template_obj.format(text=text)
    summary = model(prompt)
    return summary


@tool
async def summarize_one_line(text:str):
    """
    Generate an image prompt

    Args: text(str): Text to summarize

    Return: summary(str): Prompt for the Image
    """
    prompt_template = """  "Generate a 1000 character(including spaces) image prompt that visually represents the invention, discovery, or innovation.\n"
                    "   - Include relevant objects, environment, and action if applicable.\n"""
    prompt_template_obj = PromptTemplate(
        template=prompt_template,
        input_variables=["text"]
    )
    prompt = prompt_template_obj.format(text=text)
    if len(prompt) > 1500:
        prompt = prompt[:1400]
    summary = await model(prompt)
    return summary
