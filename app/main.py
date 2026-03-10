"""
Main orchestrator for the Autonomous Research Agent.
Coordinates the planning, research, and writing phases.
"""
import logging
from datetime import datetime
from typing import Optional
import json

from app.models.schemas import AgentState, ResearchBrief
from app.agents.planner import planner
from app.agents.researcher import researcher
from app.agents.writer import writer
from app.config import ENABLE_MULTI_AGENT, AGENT_VERBOSE, USE_LANGSMITH, USE_LANGFUSE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchAgent:
    """Main Autonomous Research Agent that orchestrates the research process."""

    def __init__(self, use_multi_agent: bool = ENABLE_MULTI_AGENT, verbose: bool = AGENT_VERBOSE):
        """
        Initialize the Research Agent.
        
        Args:
            use_multi_agent: Whether to use multi-agent approach
            verbose: Whether to print verbose output
        """
        self.use_multi_agent = use_multi_agent
        self.verbose = verbose
        self.planner = planner
        self.researcher = researcher
        self.writer = writer
        self._setup_observability()

    def _setup_observability(self):
        """Set up observability traces with LangSmith or Langfuse if configured."""
        if USE_LANGSMITH:
            try:
                import os
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
                logger.info("LangSmith tracing enabled")
            except Exception as e:
                logger.warning(f"Failed to setup LangSmith: {e}")

        if USE_LANGFUSE:
            try:
                from langfuse import Langfuse
                logger.info("Langfuse tracing enabled")
            except Exception as e:
                logger.warning(f"Failed to setup Langfuse: {e}")

    def research(self, query: str) -> ResearchBrief:
        """
        Execute the complete research workflow.
        
        Args:
            query: The user's research query
            
        Returns:
            ResearchBrief with findings
        """
        logger.info("=" * 80)
        logger.info(f"STARTING RESEARCH: {query}")
        logger.info("=" * 80)
        
        # Initialize agent state
        state = AgentState(query=query)
        state.execution_metadata["start_time"] = datetime.now().isoformat()

        try:
            # PHASE 1: PLANNING
            if self.verbose:
                print("\n📋 PHASE 1: PLANNING RESEARCH APPROACH")
                print("-" * 60)
            
            logger.info("PHASE 1: Creating research plan")
            plan = self.planner.create_plan(query)
            state.plan = plan

            if self.verbose:
                print(f"Research Approach: {plan.research_approach}")
                print(f"Search Queries ({len(plan.search_queries)}):")
                for i, q in enumerate(plan.search_queries, 1):
                    print(f"  {i}. {q}")
                print(f"Focus Areas: {', '.join(plan.expected_focus_areas)}")

            # PHASE 2: RESEARCH (Search & Extraction)
            if self.verbose:
                print("\n🔍 PHASE 2: CONDUCTING RESEARCH (SEARCH & EXTRACTION)")
                print("-" * 60)
            
            logger.info("PHASE 2: Executing searches and content extraction")
            search_results, extracted_content = self.researcher.conduct_research(
                plan.search_queries
            )
            state.search_results = search_results
            state.extracted_content = extracted_content

            if self.verbose:
                print(f"Search Results: {search_results.total_results} unique URLs found")
                print(f"Content Extracted: {len(extracted_content)} URLs successfully processed")
                print("\nExtracted Content Summary:")
                for content in extracted_content:
                    status_icon = "✓" if content.extraction_status == "success" else "✗"
                    print(f"  {status_icon} {content.url} ({content.word_count} words)")

            # PHASE 3: SYNTHESIS
            if self.verbose:
                print("\n✍️  PHASE 3: SYNTHESIZING FINDINGS")
                print("-" * 60)
            
            logger.info("PHASE 3: Synthesizing research brief")
            brief = self.writer.synthesize_brief(
                query,
                search_results,
                extracted_content
            )
            state.final_brief = brief

            if self.verbose:
                print(f"Brief Title: {brief.title}")
                print(f"Confidence Score: {brief.confidence_score:.2%}")
                print(f"Sources Used: {len(brief.sources)}")
                print(f"Key Findings: {len(brief.key_findings)}")

            state.execution_metadata["end_time"] = datetime.now().isoformat()
            state.execution_metadata["status"] = "completed"

            if self.verbose:
                print("\n" + "=" * 60)
                print("✅ RESEARCH COMPLETED SUCCESSFULLY")
                print("=" * 60)

            logger.info("Research completed successfully")
            return brief

        except Exception as e:
            logger.error(f"Error during research: {str(e)}", exc_info=True)
            state.errors.append(str(e))
            state.execution_metadata["error"] = str(e)
            state.execution_metadata["status"] = "failed"
            
            if self.verbose:
                print(f"\n❌ ERROR: {str(e)}")
            
            raise

    def export_brief(self, brief: ResearchBrief, format: str = "json") -> str:
        """
        Export the research brief in various formats.
        
        Args:
            brief: The ResearchBrief object
            format: Export format ('json', 'markdown', 'text')
            
        Returns:
            Formatted string
        """
        if format == "json":
            return json.dumps(brief.model_dump(), indent=2, default=str)
        elif format == "markdown":
            return self._export_markdown(brief)
        elif format == "text":
            return self._export_text(brief)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_markdown(self, brief: ResearchBrief) -> str:
        """Export brief as Markdown."""
        md = f"# {brief.title}\n\n"
        md += f"**Query:** {brief.query}\n"
        md += f"**Confidence Score:** {brief.confidence_score:.0%}\n\n"
        md += f"## Executive Summary\n\n{brief.executive_summary}\n\n"
        
        if brief.key_findings:
            md += "## Key Findings\n\n"
            for i, finding in enumerate(brief.key_findings, 1):
                md += f"{i}. **{finding.finding_type.upper()}:** {finding.finding}\n"
                md += f"   - Relevance: {finding.relevance_score:.0%}\n\n"
        
        if brief.sources:
            md += "## Sources\n\n"
            for url in brief.sources:
                md += f"- {url}\n"
        
        return md

    def _export_text(self, brief: ResearchBrief) -> str:
        """Export brief as plain text."""
        text = f"{'=' * 80}\n"
        text += f"{brief.title}\n"
        text += f"{'=' * 80}\n\n"
        text += f"Query: {brief.query}\n"
        text += f"Confidence Score: {brief.confidence_score:.0%}\n"
        text += f"Generated: {brief.generation_date}\n\n"
        
        text += f"{'─' * 80}\n"
        text += "EXECUTIVE SUMMARY\n"
        text += f"{'─' * 80}\n\n"
        text += f"{brief.executive_summary}\n\n"
        
        if brief.key_findings:
            text += f"{'─' * 80}\n"
            text += "KEY FINDINGS\n"
            text += f"{'─' * 80}\n\n"
            for i, finding in enumerate(brief.key_findings, 1):
                text += f"{i}. [{finding.finding_type.upper()}] {finding.finding}\n"
                text += f"   Relevance Score: {finding.relevance_score:.0%}\n\n"
        
        if brief.sources:
            text += f"{'─' * 80}\n"
            text += "SOURCES\n"
            text += f"{'─' * 80}\n\n"
            for i, url in enumerate(brief.sources[:10], 1):
                text += f"{i}. {url}\n"
            if len(brief.sources) > 10:
                text += f"... and {len(brief.sources) - 10} more sources\n"
        
        text += f"\n{'=' * 80}\n"
        return text


# Global instance
research_agent = ResearchAgent()


def research(query: str) -> ResearchBrief:
    """
    Convenience function to conduct research.
    
    Args:
        query: The research query
        
    Returns:
        ResearchBrief object
    """
    return research_agent.research(query)


def export_brief(brief: ResearchBrief, format: str = "json") -> str:
    """
    Convenience function to export a brief.
    
    Args:
        brief: The ResearchBrief object
        format: Export format
        
    Returns:
        Formatted string
    """
    return research_agent.export_brief(brief, format)


if __name__ == "__main__":
    # Example usage
    query = "What are the latest advancements in AI memory systems for agents?"
    
    try:
        brief = research(query)
        
        # Export in different formats
        print("\n" + "=" * 80)
        print("RESEARCH BRIEF (Markdown Format)")
        print("=" * 80)
        markdown = export_brief(brief, format="markdown")
        print(markdown)
        
        # Also show text format
        print("\n" + "=" * 80)
        print("RESEARCH BRIEF (Text Format)")
        print("=" * 80)
        text = export_brief(brief, format="text")
        print(text)
        
    except Exception as e:
        logger.error(f"Failed to conduct research: {e}")
        raise
