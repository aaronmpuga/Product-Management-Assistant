"""
prd_analyzer.py

Two-stage pipeline for analyzing an uploaded PRD:
  Stage 1 — critique_prd()   : Critic agent scores and red-teams the document.
  Stage 2 — rewrite_prd()    : Writer agent produces an improved PRD using the critique.

Both functions accept the raw extracted text of the PDF so the calling code
(app.py) only needs to handle file I/O once.
"""

import pdfplumber
from crewai import Crew, Process, Task
from agents import critic, writer, researcher

# ── PDF TEXT EXTRACTION ───────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract all text from a Streamlit UploadedFile object using pdfplumber.
    Returns the combined text of all pages, or raises ValueError if empty.
    """
    with pdfplumber.open(uploaded_file) as pdf:
        pages_text = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

    if not pages_text:
        raise ValueError(
            "Could not extract any text from the uploaded PDF. "
            "The file may be scanned/image-based. Please upload a text-based PDF."
        )

    return "\n\n".join(pages_text)


# ── STAGE 1: CRITIQUE ─────────────────────────────────────────────────────────

def critique_prd(prd_text: str) -> str:
    """
    Run the Critic agent against the supplied PRD text.
    Returns a structured critique report as a string.
    """
    critique_task = Task(
        description=(
            "You have been given an existing Product Requirements Document (PRD) to review.\n\n"
            "=== START OF PRD ===\n"
            f"{prd_text}\n"
            "=== END OF PRD ===\n\n"
            "Your job is to produce a thorough, structured critique. Specifically:\n\n"
            "1. **Section Coverage Score** — Check which of these 10 standard PRD sections are present, "
            "partially present, or missing entirely: Executive Summary, Problem Statement, User Personas, "
            "Market Opportunity, Product Vision & Goals, Feature Requirements, Technical Architecture, "
            "Financial Model, Risk Register, Open Questions & Next Steps. "
            "For each, give a score: ✅ Present | ⚠️ Weak/Incomplete | ❌ Missing.\n\n"
            "2. **Top 3 Weakest Assumptions** — Identify the claims or assumptions in the PRD that are "
            "most likely to be wrong, optimistic, or unvalidated. For each: state the assumption, "
            "explain why it is shaky, and recommend the fastest way to validate or falsify it.\n\n"
            "3. **Blind Spots** — Call out 2 risks, user segments, competitors, or technical constraints "
            "that are not mentioned in the PRD but should be. Be specific — name the risk or gap.\n\n"
            "4. **Contradictions or Internal Tensions** — Flag any places where two sections of the PRD "
            "disagree or create unrealistic expectations (e.g. the timeline conflicts with the feature scope, "
            "the pricing conflicts with the target persona's budget).\n\n"
            "5. **Overall PRD Quality Score** — Give a single score out of 10 with a 2-sentence justification. "
            "Be honest. A score of 6/10 is not a failure — it is useful calibration.\n\n"
            "6. **Top 5 Recommended Improvements** — List the 5 highest-impact changes the author could make "
            "to strengthen this PRD, ranked by priority."
        ),
        expected_output=(
            "A structured Critique Report in Markdown with these exact sections:\n"
            "## PRD Critique Report\n"
            "### 1. Section Coverage Scorecard (table with Section | Status | Notes)\n"
            "### 2. Top 3 Weakest Assumptions (each with: Assumption | Why It's Shaky | How to Validate)\n"
            "### 3. Blind Spots (2 specific gaps with explanation)\n"
            "### 4. Contradictions & Internal Tensions\n"
            "### 5. Overall Quality Score (X/10 with 2-sentence justification)\n"
            "### 6. Top 5 Recommended Improvements (ranked list)"
        ),
        agent=critic
    )

    crew = Crew(
        agents=[critic],
        tasks=[critique_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    return str(result)


# ── STAGE 2: REWRITE ──────────────────────────────────────────────────────────

def rewrite_prd(prd_text: str, critique_text: str) -> str:
    """
    Run the Researcher + Writer agents to produce an improved PRD.
    The writer receives both the original PRD and the critique as context.
    The researcher validates any market or competitive claims in parallel context.
    """

    # Task 1: researcher validates competitive/market claims in the original PRD
    validate_task = Task(
        description=(
            "An existing PRD has been critiqued and is being rewritten. "
            "Your job is to validate or correct the market and competitive claims in the original PRD.\n\n"
            "=== ORIGINAL PRD (excerpt — focus on market/competitor sections) ===\n"
            f"{prd_text[:6000]}\n"  # cap to avoid token overflow on large docs
            "=== END EXCERPT ===\n\n"
            "Search for:\n"
            "1. Whether the competitors named are real, current, and accurately described.\n"
            "2. Whether the market size figures are realistic (search for recent reports).\n"
            "3. Any major competitors that were missed.\n"
            "Provide corrections and additions — do not just confirm what the PRD already says."
        ),
        expected_output=(
            "A Market Validation Note with:\n"
            "(1) Competitor accuracy check — confirmed, corrected, or supplemented,\n"
            "(2) Market size validation — is the TAM/SAM realistic?,\n"
            "(3) Missing competitors — any significant players not in the original PRD."
        ),
        agent=researcher
    )

    # Task 2: writer produces the improved PRD
    rewrite_task = Task(
        description=(
            "You are rewriting an existing PRD to make it significantly better. "
            "You have three inputs:\n\n"
            "=== INPUT 1: ORIGINAL PRD ===\n"
            f"{prd_text}\n"
            "=== END ORIGINAL PRD ===\n\n"
            "=== INPUT 2: CRITIQUE REPORT ===\n"
            f"{critique_text}\n"
            "=== END CRITIQUE ===\n\n"
            "=== INPUT 3: MARKET VALIDATION (from researcher above) ===\n"
            "[Use the researcher's output from the previous task]\n\n"
            "Your instructions:\n"
            "- Preserve everything that was already strong in the original PRD.\n"
            "- Fix every section flagged as ⚠️ Weak or ❌ Missing in the critique scorecard.\n"
            "- Address each of the Top 5 Recommended Improvements from the critique.\n"
            "- Incorporate the corrected market intelligence from the researcher.\n"
            "- Add an 'Open Questions & Next Steps' section that directly maps to the "
            "  3 weakest assumptions identified in the critique, with a concrete validation action for each.\n"
            "- Do NOT add filler text. If a section is genuinely unknown, say so clearly and flag it as TBD.\n"
            "- The improved PRD must be strictly better — not just longer."
        ),
        expected_output=(
            "A complete, improved PRD in Markdown with all 10 standard sections:\n"
            "1. Executive Summary\n"
            "2. Problem Statement\n"
            "3. User Personas\n"
            "4. Market Opportunity (with validated competitive data)\n"
            "5. Product Vision & Goals\n"
            "6. Feature Requirements (P0/P1/P2 prioritized)\n"
            "7. Technical Architecture\n"
            "8. Financial Model\n"
            "9. Risk Register\n"
            "10. Open Questions & Next Steps (mapped to the 3 critique assumptions)\n\n"
            "Each section must be specific and actionable — no placeholder language except explicit TBDs."
        ),
        agent=writer,
        context=[validate_task]
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[validate_task, rewrite_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    return str(result)