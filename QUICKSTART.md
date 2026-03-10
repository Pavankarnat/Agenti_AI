"""
QUICK START GUIDE for Autonomous Research Agent
================================================

This file provides step-by-step instructions to get started quickly.
"""

# ============================================================================
# STEP 1: INSTALLATION (5 minutes)
# ============================================================================

"""
1. Open terminal in the project directory
2. Create virtual environment:
   
   python -m venv venv
   
3. Activate it:
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate

4. Install dependencies:
   
   pip install -r requirements.txt
"""

# ============================================================================
# STEP 2: SETUP API KEYS (2 minutes)
# ============================================================================

"""
1. Open the .env file in the project root
2. Add your LLM API key. Choose ONE:
   
   # For OpenAI
   OPENAI_API_KEY=sk-...
   LLM_MODEL=gpt-4-turbo
   
   # OR for Anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   LLM_MODEL=claude-opus
   
   # OR for Google
   GOOGLE_API_KEY=AIza...
   LLM_MODEL=gemini-pro

3. (Optional) Add observability keys if you have them:
   
   USE_LANGSMITH=true
   LANGSMITH_API_KEY=...
"""

# ============================================================================
# STEP 3: RUN YOUR FIRST RESEARCH (1 minute)
# ============================================================================

"""
Option A: Run the example script
   python example.py

Option B: Run your own research in Python
   from app.main import research
   
   brief = research("Your research question here?")
   print(brief.title)
   print(brief.executive_summary)

Option C: Run the main module directly
   python -m app.main
"""

# ============================================================================
# STEP 4: EXPLORE RESULTS (2 minutes)
# ============================================================================

"""
After running research, you can:

1. Export the brief:
   from app.main import research, export_brief
   
   brief = research("query")
   
   # Export as JSON
   json_data = export_brief(brief, format="json")
   
   # Export as Markdown
   markdown = export_brief(brief, format="markdown")
   
   # Export as Text
   text = export_brief(brief, format="text")

2. Save to file:
   with open("research_output.md", "w") as f:
       f.write(markdown)

3. Check saved files:
   Look in the 'research_outputs/' directory after running example.py
"""

# ============================================================================
# COMMON CONFIGURATION OPTIONS
# ============================================================================

"""
Adjust these in .env based on your needs:

FASTER RESEARCH (less thorough):
  MAX_SEARCH_RESULTS=3
  MAX_URL_EXTRACTIONS=1
  
DEEPER RESEARCH (more thorough):
  MAX_SEARCH_RESULTS=10
  MAX_URL_EXTRACTIONS=5
  
MORE CREATIVE RESULTS:
  LLM_TEMPERATURE=0.9
  
MORE FACTUAL RESULTS:
  LLM_TEMPERATURE=0.3
  
DETAILED LOGGING:
  DEBUG=true
  LOG_LEVEL=DEBUG
  AGENT_VERBOSE=true
"""

# ============================================================================
# EXAMPLE USAGE PATTERNS
# ============================================================================

# Pattern 1: Simple query and print results
def pattern_1_simple():
    from app.main import research
    
    brief = research("What is machine learning?")
    print(brief.title)
    print(brief.executive_summary)


# Pattern 2: Save to file
def pattern_2_save():
    from app.main import research, export_brief
    from pathlib import Path
    
    brief = research("Latest AI trends")
    
    # Save as Markdown
    output = export_brief(brief, format="markdown")
    Path("research.md").write_text(output)
    print("Saved to research.md")


# Pattern 3: Access detailed findings
def pattern_3_detailed():
    from app.main import research
    
    brief = research("Quantum computing advances")
    
    print(f"Title: {brief.title}")
    print(f"Confidence: {brief.confidence_score:.0%}")
    print(f"\nKey Findings:")
    for finding in brief.key_findings:
        print(f"  - {finding.finding}")
        print(f"    Relevance: {finding.relevance_score:.0%}")
    
    print(f"\nSources:")
    for source in brief.sources:
        print(f"  - {source}")


# Pattern 4: Use individual agents
def pattern_4_agents():
    from app.agents.planner import planner
    from app.agents.researcher import researcher
    from app.agents.writer import writer
    
    # Step 1: Create a plan
    plan = planner.create_plan("Your research question")
    
    # Step 2: Conduct research
    search_results, extracted = researcher.conduct_research(plan.search_queries)
    
    # Step 3: Write brief
    brief = writer.synthesize_brief("Your query", search_results, extracted)
    
    return brief


# Pattern 5: Use tools directly
def pattern_5_tools():
    from app.tools.web_search import search
    from app.tools.url_scraper import scrape
    
    # Search the web
    results = search("AI memory systems")
    print(f"Found {results.total_results} results")
    
    # Scrape a URL
    for result in results.results[:1]:
        content = scrape(result.url)
        print(f"Extracted {content.word_count} words from {result.url}")


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Problem: "[Errno -2] Name or service not known"
Solution: Check your internet connection

Problem: "API Key not found" or "Unauthorized"
Solution: 
  1. Check .env file has correct API key
  2. Verify API key has proper permissions
  3. Try a test request with the API provider

Problem: "Failed to extract from URL"
Solution:
  1. Increase REQUEST_TIMEOUT in .env
  2. Some websites block automated access
  3. Reduce MAX_URL_EXTRACTIONS

Problem: "No LLM available"
Solution:
  1. Install LLM library: pip install openai
  2. Add API key to .env
  3. System will use fallback synthesis (lower quality)

Problem: Research is too slow
Solution:
  1. Reduce MAX_SEARCH_RESULTS
  2. Reduce MAX_URL_EXTRACTIONS
  3. Reduce REQUEST_TIMEOUT (but not too much)
"""

# ============================================================================
# NEXT STEPS
# ============================================================================

"""
After getting started:

1. Customize the research approach:
   - Edit planner.py to change search strategy
   - Modify writer.py to change brief format

2. Add new tools:
   - Create new tool in app/tools/
   - Integrate with agents

3. Set up observability:
   - Enable LangSmith or Langfuse
   - Monitor agent behavior

4. Deploy:
   - Create Flask/FastAPI endpoint
   - Package as Docker container
   - Deploy to cloud platform

Want to learn more? Check README.md for complete documentation.
"""

if __name__ == "__main__":
    print(__doc__)
    print("\nReady to start? Follow the steps above!")
