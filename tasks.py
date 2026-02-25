from crewai import Task
from agents import researcher, tech_architect, writer

research_task = Task(
    description="Analyze the current market for {product_idea}. Focus on features and gaps.",
    expected_output="A list of 3 competitors and their pros/cons.",
    agent=researcher
)

tech_task = Task(
    description="Review the market research and identify the biggest optimization bottleneck.",
    expected_output="A technical feasibility summary with 1-2 'ORIE' optimization suggestions.",
    agent=tech_architect
)

prd_task = Task(
    description="Create a full PRD in Markdown format.",
    expected_output="A professional 10-section PRD document.",
    agent=writer
)