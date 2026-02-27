import streamlit as st
from crewai import Crew, Process
from agents import researcher, tech_architect, writer, ux_researcher, financial_analyst, risk_analyst, critic
from tasks import research_task, ux_task, tech_task, financial_task, risk_task, critic_task, prd_task
from prd_analyzer import extract_text_from_pdf, critique_prd, rewrite_prd

st.set_page_config(page_title="Auto-PM Optimizer", layout="wide")

st.title("🤖 Auto-PM Agentic Workflow")
st.caption(
    "7 specialized AI agents collaborate to produce or improve a detailed, grounded PRD."
)

#Sidebar: Agent Roster on Main page
with st.sidebar:
    st.header("Agent Roster")
    agents_info = [
        ("Market Research Analyst",   "Competitive landscape & market gaps"),
        ("UX Research Lead",          "User personas & journey mapping"),
        ("Technical Architect",  "Bottlenecks, stack & optimization"),
        ("Startup Financial Analyst", "TAM/SAM/SOM, pricing & MVP cost"),
        ("Risk & Compliance Officer", "Regulatory, security & market risks"),
        ("Product Critic / Red Team", "Challenges assumptions & blind spots"),
        ("Lead Product Manager",      "Synthesizes everything into the PRD"),
    ]
    for role, description in agents_info:
        with st.expander(f"{role}"):
            st.caption(description)

# Page Tabs 
tab_generate, tab_analyze = st.tabs(["Generate New PRD", "Analyze Existing PRD"])


# TAB 1 — GENERATE NEW PRD
with tab_generate:
    st.subheader("Generate a PRD from scratch")
    user_idea = st.text_input(
        "Enter your product idea:",
        placeholder="Can literally be anything bro",
        key="generate_idea"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        run_button = st.button("Generate PRD", use_container_width=True, key="generate_btn")
    with col2:
        st.caption("Expect ~3–5 minutes. Seven agents run at the same time, each building on the last, so just vibe out for now.")
    if run_button:
        if not user_idea.strip():
            st.warning("Please enter a product idea first.")
        else:
            progress_bar = st.progress(0)
            status_text  = st.empty()

            agent_steps = [
                "Agent 1/7: Researching the competitive landscape...",
                "Agent 2/7: Mapping user personas & journeys...",
                "Agent 3/7: Assessing technical feasibility...",
                "Agent 4/7: Building the financial profile...",
                "Agent 5/7: Running risk & compliance review...",
                "Agent 6/7: Red-teaming all assumptions...",
                "Agent 7/7: Synthesizing the full PRD...",
            ]
            
            #Fix Progress Bar it doesn't update 
            def update_progress(step: int):
                progress_bar.progress(int((step / len(agent_steps)) * 100))
                status_text.info(agent_steps[step - 1])

            update_progress(1)

            try:
                auto_pm_crew = Crew(
                    agents=[researcher, ux_researcher, tech_architect, financial_analyst, risk_analyst, critic, writer],
                    tasks=[research_task, ux_task, tech_task, financial_task, risk_task, critic_task, prd_task],
                    process=Process.sequential,
                    verbose=True,
                    step_callback=lambda step: update_progress(
                        min(step.get("task_index", 0) + 1, len(agent_steps))
                    ) if isinstance(step, dict) else None
                )

                result = auto_pm_crew.kickoff(inputs={'product_idea': user_idea})

                progress_bar.progress(100)
                status_text.success("All 7 agents complete!")

                st.success("PRD Generated Successfully!")
                st.divider()
                st.subheader(f"📄 PRD: {user_idea}")
                st.markdown(str(result))

                st.download_button(
                    label="⬇️ Download PRD as Markdown",
                    data=str(result),
                    file_name=f"PRD_{user_idea[:40].replace(' ', '_')}.md",
                    mime="text/markdown"
                )

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"An error occurred during agent execution: {e}")
                st.exception(e)


# TAB 2 — ANALYZE EXISTING PRD

with tab_analyze:
    st.subheader("Analyze & improve an existing PRD")
    st.caption(
        "Upload a PDF of your PRD. The Critic agent will score it across 5 dimensions and identify "
        "weak assumptions, blind spots, and missing sections. You can then optionally regenerate "
        "an improved version."
    )

    uploaded_file = st.file_uploader(
        "Upload your PRD (PDF only)",
        type=["pdf"],
        help="Upload a text-based PDF. Scanned/image PDFs are not supported."
    )

    #Stage 1: Critique 
    if uploaded_file is not None:
        st.info(f"Uploaded: **{uploaded_file.name}** ({round(uploaded_file.size / 1024, 1)} KB)")

        if st.button("Run Critique", use_container_width=False, key="critique_btn"):
            with st.spinner("Extracting text from PDF..."):
                try:
                    prd_text = extract_text_from_pdf(uploaded_file)
                    st.session_state["prd_text"]        = prd_text
                    st.session_state["critique_done"]   = False
                    st.session_state["critique_result"] = None
                    st.session_state["improved_prd"]    = None
                except ValueError as e:
                    st.error(str(e))
                    st.stop()

            word_count = len(prd_text.split())
            st.success(f"Extracted {word_count:,} words across the document.")

            with st.spinner("Critic agent is analyzing your PRD — this takes ~1 minute..."):
                try:
                    critique_result = critique_prd(prd_text)
                    st.session_state["critique_result"] = critique_result
                    st.session_state["critique_done"]   = True
                except Exception as e:
                    st.error(f"Critique failed: {e}")
                    st.exception(e)
                    st.stop()

        # Render critique if available in session
        if st.session_state.get("critique_done") and st.session_state.get("critique_result"):
            critique_result = st.session_state["critique_result"]

            st.divider()
            st.subheader("Critique Report")
            st.markdown(critique_result)

            st.download_button(
                label="Download Critique as Markdown",
                data=critique_result,
                file_name=f"Critique_{uploaded_file.name.replace('.pdf', '')}.md",
                mime="text/markdown",
                key="download_critique"
            )

            #Stage 2: Rewrite
            st.divider()
            st.subheader("Generate an Improved PRD")
            st.caption(
                "Based on the critique above, the Market Researcher and Lead PM will collaborate "
                "to produce a stronger, fully fleshed-out PRD. All flagged gaps will be addressed."
            )

            if st.button("Regenerate Improved PRD", use_container_width=False, key="rewrite_btn"):
                with st.spinner("Researcher validating market claims... Writer rebuilding PRD... (~2 min)"):
                    try:
                        improved_prd = rewrite_prd(
                            prd_text=st.session_state["prd_text"],
                            critique_text=critique_result
                        )
                        st.session_state["improved_prd"] = improved_prd
                    except Exception as e:
                        st.error(f"Rewrite failed: {e}")
                        st.exception(e)
                        st.stop()

            if st.session_state.get("improved_prd"):
                improved_prd = st.session_state["improved_prd"]

                st.divider()
                st.subheader("Improved PRD")
                st.markdown(improved_prd)

                st.download_button(
                    label="Download Improved PRD as Markdown",
                    data=improved_prd,
                    file_name=f"Improved_PRD_{uploaded_file.name.replace('.pdf', '')}.md",
                    mime="text/markdown",
                    key="download_improved"
                )