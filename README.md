# PRD Creation Tool

An agentic AI workflow that uses 7 specialized AI agents to generate detailed, grounded Product Requirements Documents (PRDs) — or analyze and improve existing ones.

Built with [CrewAI](https://crewai.com), [Google Gemini](https://aistudio.google.com), [Tavily](https://tavily.com), and [Streamlit](https://streamlit.io).

---

## Features

- **Generate a PRD from scratch** — enter a product idea and 7 agents collaborate sequentially to produce a fully fleshed-out, 10-section PRD grounded in real market data
- **Analyze an existing PRD** — upload a PDF and the Critic agent scores it across 5 dimensions, identifies weak assumptions, blind spots, and missing sections
- **Regenerate an improved PRD** — after critique, the Researcher and Writer agents produce a stronger version that addresses every flagged gap
- **Download outputs** — every generated or improved PRD and critique report is downloadable as a Markdown file

---

## Agent Roster

| Agent | Role |
|---|---|---|
| Market Research Analyst | Competitive landscape, market sizing, pricing benchmarks |
| UX Research Lead | User personas, journey mapping, design implications | 
| Technical Architect | Bottlenecks, MVP tech stack, optimization insights | 
| Startup Financial Analyst | TAM/SAM/SOM, pricing tiers, MVP cost, unit economics | 
| Risk & Compliance Officer | Regulatory, security, and market risks with mitigations | 
| Product Critic / Red Team | Challenges assumptions, flags contradictions, blind spots | 
| Lead Product Manager | Synthesizes all outputs into the final PRD | 

---

## Project Structure

```
auto-pm/
├── app.py              # Streamlit UI — two tabs: Generate and Analyze
├── agents.py           # All 7 CrewAI agent definitions
├── tasks.py            # Task definitions with context chaining
├── prd_analyzer.py     # PDF extraction, critique, and rewrite pipeline
```

---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/your-username/auto-pm-optimizer.git
cd auto-pm-optimizer
```

### 2. Create and activate a virtual environment

```bash
python -m venv autopm
source autopm/bin/activate        # Mac/Linux
autopm\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install "crewai[google-genai]" streamlit tavily-python pdfplumber python-dotenv
```

### 4. Set up your API keys

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_key_here
TAVILY_API_KEY=your_tavily_key_here
```

- **Gemini API key** → [aistudio.google.com](https://aistudio.google.com) (free tier available)
- **Tavily API key** → [tavily.com](https://tavily.com) (free tier available)

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Usage

### Generate a new PRD

1. Open the **Generate New PRD** tab
2. Enter a product idea (e.g. *"A meal planning app for college students"*)
3. Click ** Generate PRD**
4. Wait ~3–5 minutes for all 7 agents to complete
5. Download the result as a `.md` file

### Analyze an existing PRD

1. Open the **Analyze Existing PRD** tab
2. Upload a text-based PDF of your PRD
3. Click **Run Critique** — the Critic agent scores and red-teams the document (~1 min)
4. Optionally click **Regenerate Improved PRD** — the Researcher and Writer rebuild it (~2 min)
5. Download the critique report and/or improved PRD

> **Note:** Uploaded PDFs must be text-based (exported from Google Docs or Word). Scanned/image PDFs are not supported.

---

## Tech Stack

- [CrewAI](https://crewai.com) — multi-agent orchestration framework
- [Google Gemini](https://aistudio.google.com) — LLM backbone
- [Tavily](https://tavily.com) — real-time web search for agents
- [Streamlit](https://streamlit.io) — web UI
- [pdfplumber](https://github.com/jsvine/pdfplumber) — PDF text extraction

---

## License

MIT
