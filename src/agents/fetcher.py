
from crewai import Agent

class FetcherAgent(Agent):
    def __init__(self, **kwargs):
        config = {
            "role": "News Fetcher",
            "goal": "Fetch and retrieve news articles from Supabase.",
            "backstory": "You are a specialized agent capable of querying the database.",
            "allow_delegation": False,
            "verbose": True
        }
        config.update(kwargs)
        super().__init__(**config)
