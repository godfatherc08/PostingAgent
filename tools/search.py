import urllib

from langchain.tools import tool
import http.client
from rank_bm25 import BM25Okapi
import json
import os
import dotenv

dotenv.load_dotenv()
serper_key = os.getenv("SERPER_API_KEY")



def reranker(results, search_query):
    documents = [
        f"{item.get('title', '')} {item.get('snippet', '')}"
        for item in results
    ]

    tokenized_corpus = [doc.split(" ") for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = search_query.split()
    top_result = bm25.get_top_n(tokenized_query, documents, n=1)
    return top_result


@tool
def search(datetime: str):
    """
        Perform Google search with exact phrase and rank the results.
        Args:
            datetime(string): The date included in the search.
        Returns:
            str: The search results.
        """

    query = f"inventions, breakthroughs and innovations on the{datetime}"

    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": query
    })
    headers = {
        'X-API-KEY': serper_key,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    res = json.loads(data.decode())

    top_result= reranker(res["organic"], query)
    return res


@tool
def searchquery(query: str):
    """
        use to search internet for any information needed.
        Args:
            query(string): The agent search.
        Returns:
            str: The search results.
        """

    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": query
    })
    headers = {
        'X-API-KEY': serper_key,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    res = json.loads(data.decode())
    top_result= reranker(res["organic"], query)
    return top_result
