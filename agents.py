import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from crewai.tools import tool
from tavily import TavilyClient

# 1. Load the keys from your .env file
load_dotenv()

# 2. Setup the Gemini "Brain" using CrewAI's native LLM class
# NOTE: gemini-1.5-flash is deprecated. Use gemini-2.0-flash or gemini-2.5-pro.
gemini_llm = LLM(
    model="gemini/gemini-2.0-flash-lite",
    temperature=0.5,
    api_key=os.getenv("GEMINI_API_KEY")
)

# 3. Setup the Search Tool using CrewAI's native @tool decorator
@tool("Tavily Search")
def search_tool(query: str) -> str:
    """Search the web for current, accurate information. Input should be a search query string."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    results = client.search(query=query, max_results=5)
    return str(results)

# 4. Define the Agents
researcher = Agent(
    role='Market Research Analyst',
    goal='Find real-world 2026 competitors for {product_idea}.',
    backstory="Expert analyst identifying market gaps and pricing models.",
    tools=[search_tool],
    llm=gemini_llm,
    verbose=True
)

tech_architect = Agent(
    role='ORIE Technical Architect',
    goal='Identify 3 technical bottlenecks and resource constraints for {product_idea}.',
    backstory="ORIE expert focusing on optimization, scalability, and system math.",
    llm=gemini_llm,
    verbose=True
)

writer = Agent(
    role='Lead Product Manager',
    goal='Synthesize research and tech constraints into a professional Markdown PRD.',
    backstory="Senior PM skilled at balancing business value with technical reality.",
    llm=gemini_llm,
    verbose=True
)