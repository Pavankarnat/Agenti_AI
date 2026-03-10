"""
Example demonstrating the Autonomous Research Agent in action.

This script shows how to:
1. Conduct a research query
2. Export results in different formats
3. Access individual components of the research brief
"""

import sys
import json
from pathlib import Path

# Ensure project root is in Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from app.main import research, export_brief
from app.config import AGENT_VERBOSE


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def example_1_basic_research():
    """Example 1: Basic research query."""

    print_section("EXAMPLE 1: BASIC RESEARCH QUERY")

    query = "What are the latest advancements in AI memory systems for agents?"
    print(f"\nQuery: {query}\n")

    # Run research
    brief = research(query)

    print_section("RESEARCH RESULTS")

    print(f"\nTitle: {brief.title}")
    print(f"Confidence Score: {brief.confidence_score:.0%}")
    print(f"Generated: {brief.generation_date}")

    print("\nExecutive Summary:\n")
    print(brief.executive_summary)

    print(f"\nKey Findings ({len(brief.key_findings)}):")

    for i, finding in enumerate(brief.key_findings[:5], 1):
        print(f"\n{i}. {finding.finding}")
        print(f"   Type: {finding.finding_type.upper()}")
        print(f"   Relevance: {finding.relevance_score:.0%}")

    print(f"\nSources Used: {len(brief.sources)}")

    for i, source in enumerate(brief.sources[:5], 1):
        print(f"  {i}. {source}")

    if len(brief.sources) > 5:
        print(f"  ... and {len(brief.sources) - 5} more sources")

    return brief


def example_2_export_formats(brief):
    """Example 2: Export research brief in different formats."""

    print_section("EXAMPLE 2: EXPORTING IN DIFFERENT FORMATS")

    # JSON Export
    print("\nJSON Format Preview")
    print("-" * 80)

    json_output = export_brief(brief, format="json")
    json_preview = json.loads(json_output)

    print(json.dumps({
        "title": json_preview.get("title"),
        "confidence_score": json_preview.get("confidence_score"),
        "key_findings_count": len(json_preview.get("key_findings", [])),
        "sources_count": len(json_preview.get("sources", []))
    }, indent=2))

    # Markdown Export
    print("\nMarkdown Format Preview")
    print("-" * 80)

    markdown = export_brief(brief, format="markdown")
    print(markdown[:500] + "\n... (truncated)\n")

    # Text Export
    print("\nText Format Preview")
    print("-" * 80)

    text = export_brief(brief, format="text")
    lines = text.split("\n")
    print("\n".join(lines[:20]) + "\n... (truncated)\n")

    return json_output, markdown, text


def example_3_save_to_file(brief):
    """Example 3: Save research brief to files."""

    print_section("EXAMPLE 3: SAVING TO FILES")

    output_dir = Path("research_outputs")
    output_dir.mkdir(exist_ok=True)

    # Save JSON
    json_path = output_dir / "research_brief.json"
    json_content = export_brief(brief, format="json")
    json_path.write_text(json_content, encoding="utf-8")
    print(f"Saved JSON: {json_path}")

    # Save Markdown
    md_path = output_dir / "research_brief.md"
    md_content = export_brief(brief, format="markdown")
    md_path.write_text(md_content, encoding="utf-8")
    print(f"Saved Markdown: {md_path}")

    # Save Text
    txt_path = output_dir / "research_brief.txt"
    txt_content = export_brief(brief, format="text")
    txt_path.write_text(txt_content, encoding="utf-8")
    print(f"Saved Text: {txt_path}")

    print(f"\nAll files saved to '{output_dir}' directory")


def example_4_direct_agent_usage():
    """Example 4: Using agents directly without orchestration."""

    print_section("EXAMPLE 4: DIRECT AGENT USAGE")

    from app.agents.planner import planner
    from app.agents.researcher import researcher
    from app.agents.writer import writer

    query = "AI agent frameworks in 2024"

    print("\nSTEP 1: Planning")
    print("-" * 40)

    plan = planner.create_plan(query)

    print(f"Research Approach: {plan.research_approach}")
    print(f"Search Queries ({len(plan.search_queries)}):")

    for q in plan.search_queries[:3]:
        print(f"  • {q}")

    print("\nSTEP 2: Research")
    print("-" * 40)

    search_results, extracted = researcher.conduct_research(plan.search_queries)

    print(f"Found {search_results.total_results} URLs")
    print(f"Extracted content from {len(extracted)} URLs")

    for content in extracted[:2]:
        print(f"  • {content.url}: {content.word_count} words")

    print("\nSTEP 3: Synthesis")
    print("-" * 40)

    brief = writer.synthesize_brief(query, search_results, extracted)

    print(f"Brief Generated: {brief.title}")
    print(f"Confidence: {brief.confidence_score:.0%}")
    print(f"Key Findings: {len(brief.key_findings)}")


def main():
    """Run all examples."""

    print("\n" + "=" * 80)
    print("AUTONOMOUS RESEARCH AGENT - EXAMPLES")
    print("=" * 80)

    try:

        # Example 1
        brief = example_1_basic_research()

        # Example 2
        example_2_export_formats(brief)

        # Example 3
        example_3_save_to_file(brief)

        # Example 4 (only if verbose)
        if AGENT_VERBOSE:
            example_4_direct_agent_usage()

        print_section("EXAMPLES COMPLETED SUCCESSFULLY")

        print("\nAll examples executed successfully!")

        print("\nTips:")
        print(" • Check research_outputs/ directory for saved files")
        print(" • Modify .env file to use different LLM models")
        print(" • Set AGENT_VERBOSE=true for detailed execution logs")
        print(" • Adjust MAX_SEARCH_RESULTS for deeper research")

    except Exception as e:

        print_section("ERROR")

        print(f"\nError: {str(e)}")

        print("\nTroubleshooting:")
        print(" • Ensure .env file has valid API keys")
        print(" • Check internet connection")
        print(" • Verify dependencies: pip install -r requirements.txt")

        raise


if __name__ == "__main__":
    main()