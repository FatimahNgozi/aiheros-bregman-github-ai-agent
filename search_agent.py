# application/search_agent.py

from pydantic_ai import Agent
from application.search_tools import hybrid_search

def init_agent(index, repo_owner: str, repo_name: str):
    system_prompt = f"""
You are a knowledgeable assistant for the GitHub repository:
https://github.com/{repo_owner}/{repo_name}

Answer questions using only the repository's content. Cite filenames or code snippets where relevant.
"""

    # Use hybrid_search as the tool
    agent = Agent(
        model="gemini-2.0-flash",
        instructions=system_prompt,
        tools=[lambda query: hybrid_search(index, query)]
    )

    return agent

