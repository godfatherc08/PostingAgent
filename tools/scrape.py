
from firecrawl import Firecrawl
from langchain.tools import tool
import os
import dotenv

dotenv.load_dotenv()
token = os.getenv("FIRECRAWL_API_KEY")

@tool
def scrape_tool(link: str):
    """
    Scrape a link
    input: link (str) to scrape
    return: summary of scraped data
    """
    app = Firecrawl(api_key=token)

    scrape = app.scrape(link, formats=["summary", "json"])
    return scrape.summary
