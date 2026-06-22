"""
Writer Agent - Synthesizes research findings into a structured brief.
"""
import logging
import json
from typing import List, Optional
from app.models.schemas import (
    ExtractedURL, SearchResults, ResearchBrief, ResearchFinding
)
from app.config import LLM_MODEL

logger = logging.getLogger(__name__)


class WriterAgent:
    """Agent responsible for synthesizing research into a structured brief."""

    def __init__(self, model: str = LLM_MODEL):
        """
        Initialize the Writer Agent.
        
        Args:
            model: The LLM model to use
        """
        self.model = model
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the LLM based on the model selection."""
        if "gpt" in self.model.lower():
            try:
                from openai import OpenAI
                return OpenAI()
            except ImportError:
                logger.warning("OpenAI not installed, using fallback")
                return None
        elif "claude" in self.model.lower():
            try:
                from anthropic import Anthropic
                return Anthropic()
            except ImportError:
                logger.warning("Anthropic not installed, using fallback")
                return None
        elif "gemini" in self.model.lower():
            try:
                import google.generativeai as genai
                from app.config import GOOGLE_API_KEY
                if GOOGLE_API_KEY:
                    genai.configure(api_key=GOOGLE_API_KEY)
                return genai.GenerativeModel(self.model)
            except Exception as e:
                logger.warning(f"Google Generative AI not initialized: {e}")
                return None
        return None

    def synthesize_brief(
        self,
        query: str,
        search_results: SearchResults,
        extracted_content: List[ExtractedURL]
    ) -> ResearchBrief:
        """
        Synthesize research findings into a structured brief.
        
        Args:
            query: The original user query
            search_results: Search results from web search
            extracted_content: Content extracted from URLs
            
        Returns:
            ResearchBrief object
        """
        if self.llm is None:
            logger.warning("No LLM available, using fallback synthesis")
            return self._fallback_synthesis(query, search_results, extracted_content)

        try:
            logger.info("Synthesizing research brief")
            
            # Prepare context from extracted content
            content_context = self._prepare_context(extracted_content)
            
            prompt = f"""You are an expert research analyst. Synthesize the following research content into a comprehensive research brief.

Original Query: {query}

EXTRACTED CONTENT:
{content_context}

Create a research brief in JSON format with the following structure:
{{
    "title": "Concise title for the research",
    "executive_summary": "2-3 paragraph summary of key findings",
    "key_findings": [
        {{"finding": "specific finding", "relevance_score": 0.9, "finding_type": "fact"}},
        {{"finding": "another finding", "relevance_score": 0.85, "finding_type": "insight"}}
    ],
    "confidence_score": 0.85
}}

Focus on extracting the most important and relevant findings. Each finding should be specific and actionable.
"""

            if "gpt" in self.model.lower():
                response = self.llm.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                content = response.choices[0].message.content
            elif "claude" in self.model.lower():
                response = self.llm.messages.create(
                    model="claude-opus",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            elif "gemini" in self.model.lower():
                response = self.llm.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 2000,
                    }
                )
                content = response.text
            else:
                return self._fallback_synthesis(query, search_results, extracted_content)

            # Parse the response
            try:
                brief_data = json.loads(content)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    brief_data = json.loads(json_match.group())
                else:
                    return self._fallback_synthesis(query, search_results, extracted_content)

            # Build the research brief
            findings = []
            for finding_data in brief_data.get("key_findings", []):
                finding = ResearchFinding(
                    finding=finding_data.get("finding", ""),
                    source_url="",  # Will be populated later
                    relevance_score=finding_data.get("relevance_score", 0.8),
                    finding_type=finding_data.get("finding_type", "fact")
                )
                findings.append(finding)

            # Collect sources
            sources = list(set([result.url for result in search_results.results]))

            brief = ResearchBrief(
                query=query,
                title=brief_data.get("title", f"Research Brief: {query}"),
                executive_summary=brief_data.get("executive_summary", ""),
                key_findings=findings,
                sources=sources,
                confidence_score=brief_data.get("confidence_score", 0.8)
            )

            logger.info("Research brief synthesized successfully")
            return brief

        except Exception as e:
            logger.error(f"Error synthesizing brief: {str(e)}")
            return self._fallback_synthesis(query, search_results, extracted_content)

    def _prepare_context(self, extracted_content: List[ExtractedURL]) -> str:
        """
        Prepare content context from extracted URLs.
        
        Args:
            extracted_content: List of extracted content
            
        Returns:
            Formatted context string
        """
        context = ""
        for i, content in enumerate(extracted_content, 1):
            preview = content.content[:1000] if content.content else "[Content extraction failed]"
            context += f"\n--- Source {i}: {content.url} ---\n"
            context += f"Title: {content.title}\n"
            context += f"Content Preview:\n{preview}\n"
        
        return context

    def _fallback_synthesis(
        self,
        query: str,
        search_results: SearchResults,
        extracted_content: List[ExtractedURL]
    ) -> ResearchBrief:
        """
        Fallback synthesis when LLM is not available.
        
        Args:
            query: The original query
            search_results: Search results
            extracted_content: Extracted content
            
        Returns:
            ResearchBrief object
        """
        logger.info("Using fallback synthesis strategy")
        
        # Create findings from search results
        findings = []
        for i, result in enumerate(search_results.results[:5]):
            finding = ResearchFinding(
                finding=result.snippet,
                source_url=result.url,
                relevance_score=0.7 - (i * 0.1),
                finding_type="snippet"
            )
            findings.append(finding)

        # Create summary from extracted content
        if extracted_content:
            summaries = [f"- {content.title}" for content in extracted_content if content.title]
            summary = "Key sources identified:\n" + "\n".join(summaries)
        else:
            summary = f"Research conducted on: {query}"

        sources = list(set([result.url for result in search_results.results]))

        brief = ResearchBrief(
            query=query,
            title=f"Research Brief: {query}",
            executive_summary=summary,
            key_findings=findings,
            sources=sources[:10],  # Limit to 10 sources
            confidence_score=0.6
        )

        return brief


# Global instance
writer = WriterAgent()


def synthesize_brief(
    query: str,
    search_results: SearchResults,
    extracted_content: List[ExtractedURL]
) -> ResearchBrief:
    """
    Convenience function to synthesize a research brief.
    
    Args:
        query: The original query
        search_results: Search results
        extracted_content: Extracted content
        
    Returns:
        ResearchBrief object
    """
    return writer.synthesize_brief(query, search_results, extracted_content)


if __name__ == "__main__":
    # Example usage (would need actual search results)
    print("Writer agent loaded successfully")
