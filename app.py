import streamlit as st
from crewai import Crew, Process
from agents import researcher, tech_architect, writer
from tasks import research_task, tech_task, prd_task

st.set_page_config(page_title="Auto-PM Optimizer", layout="wide")

st.title("🤖 Auto-PM Agentic Workflow")

user_idea = st.text_input("Enter your product idea:", placeholder="e.g. A decentralized energy grid for Bethesda")

if st.button("Generate Optimized PRD"):
    if user_idea:
        with st.spinner("Agents are collaborating on your PRD..."):
            # Assemble the Crew
            auto_pm_crew = Crew(
                agents=[researcher, tech_architect, writer],
                tasks=[research_task, tech_task, prd_task],
                process=Process.sequential
            )
            
            # Execute
            result = auto_pm_crew.kickoff(inputs={'product_idea': user_idea})
            
            # Display Result
            st.success("PRD Generated Successfully!")
            st.markdown(result)
    else:
        st.warning("Please enter an idea first.")
        