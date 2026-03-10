# Autonomous Research Agent 🤖

A sophisticated multi-agent system that autonomously conducts research by planning searches, gathering information from multiple sources, and synthesizing findings into structured research briefs.

## Overview

The Autonomous Research Agent implements a functional agentic loop with the following architecture:

```
User Query
    ↓
[PLANNER AGENT] ← Creates research plan & search strategy
    ↓
[RESEARCHER AGENT] ← Executes searches & extracts content from URLs
    ↓
[WRITER AGENT] ← Synthesizes findings into structured brief
    ↓
Research Brief Output
```

## Features

✅ **Multi-Agent Architecture**
- Planner Agent: Creates research plans and search strategies
- Researcher Agent: Executes web searches and content extraction
- Writer Agent: Synthesizes findings into structured briefs

✅ **Autonomous Research Loop**
- Natural language query input
- Intelligent search planning
- Multi-source content extraction
- Intelligent synthesis

✅ **Robust Tool Integration**
- Web Search: DuckDuckGo integration (no API key required)
- URL Scraper: Extracts and cleans content from webpages
- Error Handling: Graceful degradation for failed URLs

✅ **Structured Output**
- JSON-compatible data models
- Multiple export formats (JSON, Markdown, Text)
- Confidence scores and source attribution
- Comprehensive metadata

✅ **Observability**
- LangSmith integration (optional)
- Langfuse integration (optional)
- Detailed logging
- Execution metadata tracking

✅ **LLM Flexibility**
- Support for GPT-4, Claude, Gemini
- Fallback strategies when LLM unavailable
- Temperature and token configuration

## Project Structure

```
Agentic_AI/
│
├── app/
│   ├── __init__.py
│   ├── config.py                 # Configuration & environment variables
│   ├── main.py                   # Main orchestrator
│   │
│   ├── agents/                   # Agent implementations
│   │   ├── __init__.py
│   │   ├── planner.py           # Planning agent
│   │   ├── researcher.py        # Research execution agent
│   │   └── writer.py            # Synthesis agent
│   │
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic schemas
│   │
│   └── tools/                    # Tool implementations
│       ├── __init__.py
│       ├── web_search.py        # Web search tool
│       └── url_scraper.py       # URL content extraction
│
├── .env                          # Environment variables
├── README.md                     # This file
└── requirements.txt              # Python dependencies
```

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup Steps

1. **Clone/Setup Repository**
```bash
cd Agentic_AI
```

2. **Create Virtual Environment** (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**
```bash
# Copy and edit .env file with your API keys
# Required: At least one LLM API key
# Optional: LangSmith or Langfuse keys for observability
```

### Environment Variables Configuration

Create a `.env` file in the project root with the following variables:

```env
# LLM Configuration (at least one is required)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here

# Select which model to use
LLM_MODEL=gpt-4-turbo          # Options: gpt-4-turbo, claude-opus, gemini-pro
LLM_TEMPERATURE=0.7            # Controls creativity (0-1)
LLM_MAX_TOKENS=2000

# Observability (Optional)
USE_LANGSMITH=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=agentic-ai-research

USE_LANGFUSE=false
LANGFUSE_API_KEY=
LANGFUSE_SECRET_KEY=

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
MAX_SEARCH_RESULTS=5
MAX_URL_EXTRACTIONS=3
REQUEST_TIMEOUT=10
ENABLE_MULTI_AGENT=true
AGENT_VERBOSE=true
```

## Usage

### Basic Usage

```python
from app.main import research

# Simple query
brief = research("What are the latest advancements in AI memory systems for agents?")

# Access results
print(f"Title: {brief.title}")
print(f"Confidence: {brief.confidence_score:.0%}")
print(f"Summary: {brief.executive_summary}")
print(f"Sources: {len(brief.sources)}")
```

### With Export Options

```python
from app.main import research, export_brief

query = "Latest developments in AI agents"
brief = research(query)

# Export as JSON
json_output = export_brief(brief, format="json")

# Export as Markdown
markdown_output = export_brief(brief, format="markdown")

# Export as Plain Text
text_output = export_brief(brief, format="text")

# Save to file
with open("research_brief.md", "w") as f:
    f.write(markdown_output)
```

### Direct Agent Usage

```python
from app.agents.planner import planner
from app.agents.researcher import researcher
from app.agents.writer import writer

# Step 1: Plan
plan = planner.create_plan("Your research question")

# Step 2: Research
search_results, extracted_content = researcher.conduct_research(plan.search_queries)

# Step 3: Synthesize
brief = writer.synthesize_brief("Your query", search_results, extracted_content)
```

### Tool Usage

```python
from app.tools.web_search import search
from app.tools.url_scraper import scrape

# Web Search
search_results = search("AI agents memory architecture")

# URL Scraping
extracted = scrape("https://example.com")
print(f"Extracted: {extracted.word_count} words from {extracted.url}")
```

## Example Run

### Command Line Execution

```bash
python app/main.py
```

This runs the example query: `"What are the latest advancements in AI memory systems for agents?"`

### Expected Output

```
================================================================================
STARTING RESEARCH: What are the latest advancements in AI memory systems for agents?
================================================================================

📋 PHASE 1: PLANNING RESEARCH APPROACH
────────────────────────────────────────────────────────────────
Research Approach: Comprehensive search using multiple query variations
Search Queries (5):
  1. What are the latest advancements in AI memory systems for agents?
  2. What are the latest advancements in AI memory systems for agents? latest 2024
  3. What are the latest advancements in AI memory systems for agents? advances
  4. What are the latest advancements in AI memory systems for agents? research
  5. What are the latest advancements in AI memory systems for agents? guide
Focus Areas: Latest developments, Key findings, Expert insights

🔍 PHASE 2: CONDUCTING RESEARCH (SEARCH & EXTRACTION)
────────────────────────────────────────────────────────────────
Search Results: 15 unique URLs found
Content Extracted: 3 URLs successfully processed

Extracted Content Summary:
  ✓ https://example.com/ai-memory-1 (2847 words)
  ✓ https://example.com/ai-memory-2 (3102 words)
  ✓ https://example.com/ai-memory-3 (1950 words)

✍️  PHASE 3: SYNTHESIZING FINDINGS
────────────────────────────────────────────────────────────────
Brief Title: Research Brief: What are the latest advancements...
Confidence Score: 85%
Sources Used: 15
Key Findings: 8

============================================================
✅ RESEARCH COMPLETED SUCCESSFULLY
============================================================

# Research Brief: Latest AI Memory Systems

**Query:** What are the latest advancements in AI memory systems for agents?
**Confidence Score:** 85%

## Executive Summary

Recent advancements in AI memory systems for agents focus on three main areas...

## Key Findings

1. **FACT:** Vector databases enable efficient semantic search
   - Relevance: 92%

2. **INSIGHT:** Hybrid memory architectures combining short and long-term memory improve agent performance
   - Relevance: 88%

... (more findings)

## Sources

- https://example.com/ai-memory-1
- https://example.com/ai-memory-2
- https://example.com/ai-memory-3
... (more sources)
```

## Technical Architecture

### Agentic Loop Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   PLANNING PHASE                             │
│  Input: Natural language query                               │
│  Process: Create research plan with search queries          │
│  Output: ResearchPlan object                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  RESEARCH PHASE                              │
│  Step 1: Execute multiple web searches                       │
│  Step 2: Aggregate unique results                            │
│  Step 3: Extract content from top URLs                       │
│  Output: SearchResults + ExtractedURL list                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  SYNTHESIS PHASE                             │
│  Input: Search results + Extracted content                   │
│  Process: Synthesize into structured brief with LLM          │
│  Output: ResearchBrief object                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
              Output to User
```

### Data Flow

```
Query
  │
  ├─→ planner.create_plan()
  │   └─→ ResearchPlan (with search_queries)
  │
  ├─→ researcher.conduct_research()
  │   ├─→ web_search.search() × N
  │   │   └─→ SearchResults
  │   │
  │   └─→ url_scraper.scrape() × M
  │       └─→ ExtractedURL[]
  │
  └─→ writer.synthesize_brief()
      └─→ ResearchBrief
```

## Error Handling

The system gracefully handles various error scenarios:

- **Failed Web Searches**: Continues with alternative queries
- **Unreachable URLs**: Skips and continues with remaining URLs
- **LLM Unavailable**: Falls back to heuristic-based synthesis
- **Extraction Failures**: Returns partial results with error metadata
- **Timeout Issues**: Respects timeout settings and gracefully degrades

## Optional Enhancements

### LangSmith Integration

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_langsmith_key"

# Traces will be recorded automatically
brief = research("Your query")
```

### Langfuse Integration

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="your_public_key",
    secret_key="your_secret_key"
)

# Integrate with your trace
brief = research("Your query")
```

## API Models Supported

### Frontier LLMs
- **OpenAI**: GPT-4 Turbo, GPT-4, GPT-3.5 Turbo
- **Anthropic**: Claude 3 Opus, Claude 3 Sonnet, Claude 2
- **Google**: Gemini Pro

### How to Switch Models

Edit `.env`:
```env
LLM_MODEL=gpt-4-turbo  # or claude-opus or gemini-pro
```

Or set environment variable:
```bash
export LLM_MODEL=claude-opus
python app/main.py
```

## Configuration Guide

### Search Settings
```env
MAX_SEARCH_RESULTS=5        # Number of search results per query
MAX_URL_EXTRACTIONS=3       # Number of URLs to extract content from
REQUEST_TIMEOUT=10          # Timeout for web requests in seconds
```

### LLM Behavior
```env
LLM_TEMPERATURE=0.7         # 0=deterministic, 1=creative
LLM_MAX_TOKENS=2000        # Maximum response length
```

### Verbosity
```env
DEBUG=false                 # Detailed debug output
AGENT_VERBOSE=true         # Show agent execution steps
```

## Troubleshooting

### "API Key not found" Error
**Solution**: Update `.env` file with valid API key:
```bash
OPENAI_API_KEY=sk-...
```

### "Failed to extract content" Warnings
**Cause**: Website blocking automated access
**Solution**: Increase `REQUEST_TIMEOUT` or adjust headers

### "No LLM available" Warning
**Cause**: LLM library not installed
**Solution**: 
```bash
pip install openai  # for OpenAI
pip install anthropic  # for Anthropic
```

### Slow Research Execution
**Cause**: Too many URLs being scraped
**Solution**: Reduce `MAX_URL_EXTRACTIONS` in `.env`

## Performance Metrics

Typical execution times (varies by internet speed):
- **Planning Phase**: 2-5 seconds
- **Search Phase**: 5-15 seconds (for 3-5 queries)
- **Content Extraction**: 10-30 seconds (for 3 URLs)
- **Synthesis Phase**: 5-10 seconds
- **Total**: 25-60 seconds for complete research

## Contributing

To extend the system:

1. **Add New Tools**: Implement in `app/tools/`
2. **Custom Agents**: Extend in `app/agents/`
3. **New Models**: Update `config.py` with model support
4. **Export Formats**: Add methods to `ResearchAgent.export_brief()`

## License

MIT License - Feel free to use for research and development

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review environment configuration
3. Check logs with `LOG_LEVEL=DEBUG`
4. Verify API keys are valid

## Future Roadmap

- [ ] Direct MCP server integration for tools
- [ ] Multi-language support
- [ ] Citation formatting (APA, MLA, Chicago)
- [ ] PDF export capability
- [ ] Real-time streaming of findings
- [ ] Agent customization via prompt templates
- [ ] Integration with knowledge bases
- [ ] Fact-checking capabilities

---

**Built with ❤️ for autonomous research**
