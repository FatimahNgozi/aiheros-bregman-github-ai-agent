"""search_agent.py — configures the Gemini search agent"""

from pydantic_ai import Agent
from application.search_tools import hybrid_search

def init_agent(index, repo_owner: str, repo_name: str):
    """Initialize Gemini agent with search capabilities."""
    agent = Agent(
        name="bregman_agent",
        model="gemini-1.5-pro",
        instructions=(
            f"You are an expert assistant for the GitHub repository '{repo_owner}/{repo_name}'. "
            "You can search the repository files to answer questions accurately. "
            "Always include relevant details or snippets from the repository in your responses."
        ),
        tools=[lambda query: hybrid_search(index, query)]
    )
    return agent
