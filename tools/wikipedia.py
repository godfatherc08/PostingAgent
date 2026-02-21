
from typing import Optional
from langchain.tools import tool
import wikipediaapi
import json

@tool
def wikipedia(query: str) -> Optional[str]:
    """
    Fetch Wikipedia information for a given search query using Wikipedia-API and return as JSON.

    Args:
        query (str): The search query string.

    Returns:
        Optional[str]: A JSON string containing the query, title, and summary, or None if no result is found.
    """

    wiki = wikipediaapi.Wikipedia(user_agent='SocialMediaPostingAgent/1.0 (email: godfatherc23@gmail.com)',
                                  language='en')

    try:
        print(f"Searching Wikipedia for: {query}")
        page = wiki.page(query)

        if page.exists():
            result = {
                "query": query,
                "title": page.title,
                "summary": page.summary
            }
            print(f"Successfully retrieved summary for: {query}")
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            print(f"No results found for query: {query}")
            return None

    except Exception as e:
        print(f"An error occurred while processing the Wikipedia query: {e}")
        return None

