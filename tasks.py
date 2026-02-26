from crewai import Task
from agents import (
    researcher, tech_architect, writer,
    ux_researcher, financial_analyst, risk_analyst, critic
)

# ── TASK 1: Market Research ───────────────────────────────────────────────────
research_task = Task(
    description=(
        'Conduct a deep competitive analysis of the current market for {product_idea}. '
        'Search for real companies active in this space in 2025-2026. '
        'For each competitor, identify: their product name, pricing model, core features, '
        'stated weaknesses (from reviews, forums, or analyst reports), and the gap they leave open. '
        'Also identify the overall market trend (growing, consolidating, disrupted?).'
    ),
    expected_output=(
        'A structured competitive landscape report containing: '
        '(1) A market overview paragraph (2-3 sentences on trend and size), '
        '(2) A detailed breakdown of 3-5 real competitors with name, pricing, 3 pros, 3 cons, and key gap, '
        '(3) A "Market Opportunity" paragraph summarizing where {product_idea} can win.'
    ),
    agent=researcher
)

# ── TASK 2: UX Research ───────────────────────────────────────────────────────
ux_task = Task(
    description=(
        'Define the human side of {product_idea}. '
        'Based on the competitive research above, identify 3 distinct user personas who would use this product. '
        'For each persona include: a name and demographic snapshot, their primary job-to-be-done, '
        'their top 3 frustrations with current solutions, their success metric '
        '("I\'ll know this works when..."), and any behavioral data or statistics you can find via search.'
        'Then map the primary user journey for the most important persona — '
        'from first awareness of the problem to becoming a power user.'
    ),
    expected_output=(
        'A UX Research Report with: '
        '(1) 3 detailed user personas (name, demographic, JTBD, frustrations, success metric), '
        '(2) A primary user journey map for Persona 1 with 5-7 stages, '
        '(3) A "Design Implications" section listing 3-5 specific product requirements implied by the research.'
    ),
    agent=ux_researcher,
    context=[research_task]
)

# ── TASK 3: Technical Architecture ───────────────────────────────────────────
tech_task = Task(
    description=(
        'Perform a technical feasibility assessment for {product_idea}. '
        'Review the competitive landscape and user research above. '
        'Identify the 3 most critical technical bottlenecks — these are the problems '
        'that, if unsolved, would cause the product to fail at scale or in production. '
        'For each bottleneck, describe: what it is, why it matters, a rough quantification '
        '(e.g. latency budget, storage cost at 100k users, API rate limits), '
        'and your recommended technical approach. '
        'Also suggest the minimal viable tech stack for an MVP.'
    ),
    expected_output=(
        'A Technical Feasibility Report with: '
        '(1) 3 named bottlenecks, each with a description, quantified impact, and mitigation approach, '
        '(2) A recommended MVP tech stack (frontend, backend, data layer, infra), '
        '(3) An "ORIE Insight" — one optimization or systems-design observation '
        'that could give {product_idea} a structural performance or cost advantage.'
    ),
    agent=tech_architect,
    context=[research_task, ux_task]
)

# ── TASK 4: Financial Analysis ────────────────────────────────────────────────
financial_task = Task(
    description=(
        'Build a financial profile for {product_idea}. '
        'Use the competitive landscape to benchmark pricing. '
        'Estimate the TAM (total addressable market), SAM (serviceable addressable market), '
        'and SOM (realistic 3-year target). '
        'Recommend a pricing model with 2-3 tiers and justify each tier based on persona willingness to pay. '
        'Estimate MVP build cost range (low/mid/high) based on the tech stack identified. '
        'Identify the top 3 unit economics metrics to track and the milestone that signals product-market fit.'
    ),
    expected_output=(
        'A Financial Feasibility Profile with: '
        '(1) TAM / SAM / SOM estimates with sourced justification, '
        '(2) A 2-3 tier pricing model with rationale, '
        '(3) MVP cost range (low / mid / high) with key cost drivers, '
        '(4) 3 key unit economics metrics (e.g. CAC, LTV, churn) with target benchmarks, '
        '(5) A "PMF Signal" — the one metric that, if achieved, confirms product-market fit.'
    ),
    agent=financial_analyst,
    context=[research_task, ux_task, tech_task]
)

# ── TASK 5: Risk Assessment ───────────────────────────────────────────────────
risk_task = Task(
    description=(
        'Conduct a risk assessment for {product_idea}. '
        'Review all prior outputs and identify the top 5 material risks across these categories: '
        'regulatory/legal (what laws or compliance requirements apply?), '
        'technical/security (what are the failure modes and attack surfaces?), '
        'and market/execution (what are the realistic ways this product fails to gain traction?). '
        'For each risk: name it, categorize it, rate severity (High/Medium/Low), '
        'explain the realistic scenario in which it materializes, '
        'and recommend a concrete mitigation strategy.'
    ),
    expected_output=(
        'A Risk Register with: '
        '(1) 5 named risks in a structured format: '
        'Risk Name | Category | Severity | Scenario | Mitigation, '
        '(2) A "Top 2 Risks" summary paragraph calling out the two risks '
        'that deserve immediate attention before launch.'
    ),
    agent=risk_analyst,
    context=[research_task, ux_task, tech_task, financial_task]
)

# ── TASK 6: Red Team / Critique ───────────────────────────────────────────────
critic_task = Task(
    description=(
        'Red-team all prior research and analysis for {product_idea}. '
        'Read the competitive research, UX personas, technical assessment, '
        'financial projections, and risk register carefully. '
        'Your job is to find: '
        '(1) The 3 weakest or most optimistic assumptions that could collapse the business case if wrong, '
        '(2) Any contradictions or tensions between agents\' outputs '
        '(e.g. the financial model assumes X users but the tech bottleneck suggests that\'s hard), '
        '(3) One "unknown unknown" — a blind spot nobody mentioned that is worth flagging. '
        'Be direct and specific. The goal is to make the PRD stronger, not to reject the idea.'
    ),
    expected_output=(
        'A Red Team Report with: '
        '(1) 3 challenged assumptions, each with: the assumption, why it\'s shaky, and what to validate first, '
        '(2) 1-2 cross-agent contradictions or tensions explained clearly, '
        '(3) 1 blind spot / unknown unknown with a recommended investigation action.'
    ),
    agent=critic,
    context=[research_task, ux_task, tech_task, financial_task, risk_task]
)

# ── TASK 7: PRD Synthesis ─────────────────────────────────────────────────────
prd_task = Task(
    description=(
        'You are the final synthesizer. Write a complete, professional Product Requirements Document (PRD) '
        'for {product_idea} in Markdown format. '
        'You MUST incorporate findings from ALL prior agents: '
        'competitive research, user personas, technical architecture, financial analysis, '
        'risk register, and the red team critique. '
        'Every section must be specific — no placeholder text, no vague goals. '
        'Where the critic flagged a weak assumption, acknowledge it and note how the team will validate it.'
    ),
    expected_output=(
        'A complete PRD in Markdown with exactly these 10 sections:\n'
        '1. Executive Summary — 1 paragraph pitch + the single most important metric for success\n'
        '2. Problem Statement — the specific pain, who feels it, and why current solutions fail\n'
        '3. User Personas — the 3 personas from UX research, summarized\n'
        '4. Market Opportunity — TAM/SAM/SOM + competitive positioning\n'
        '5. Product Vision & Goals — 3 measurable goals for v1.0\n'
        '6. Feature Requirements — MVP features (P0/P1/P2 prioritized) tied to personas\n'
        '7. Technical Architecture — stack, bottlenecks, and ORIE optimization insight\n'
        '8. Financial Model — pricing tiers, cost estimates, key unit economics\n'
        '9. Risk Register — top 5 risks with severity and mitigation\n'
        '10. Open Questions & Next Steps — the 3 assumptions to validate first (from red team), '
        'with a concrete action for each'
    ),
    agent=writer,
    context=[research_task, ux_task, tech_task, financial_task, risk_task, critic_task]
)