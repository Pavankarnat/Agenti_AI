"""
Planner Agent - Plans the research approach based on user query.
"""
import logging
import json
from typing import Optional
from app.models.schemas import ResearchPlan
from app.config import LLM_MODEL

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Agent responsible for planning the research approach."""

    def __init__(self, model: str = LLM_MODEL):
        """
        Initialize the Planner Agent.
        
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

    def create_plan(self, query: str) -> ResearchPlan:
        """
        Create a research plan based on the user query.
        
        Args:
            query: The user's research query
            
        Returns:
            ResearchPlan object
        """
        if self.llm is None:
            logger.warning("No LLM available, using default planning strategy")
            return self._default_plan(query)

        try:
            logger.info(f"Creating research plan for query: {query}")
            
            prompt = f"""You are an expert research planner. Analyze the following research query and create a comprehensive research plan.

Query: {query}

Provide your response in JSON format with the following structure:
{{
    "search_queries": ["query1", "query2", "query3"],
    "research_approach": "Description of the research approach",
    "expected_focus_areas": ["area1", "area2", "area3"]
}}

Create 3-5 specific, targeted search queries that will help answer the original query comprehensively.
"""

            if "gpt" in self.model.lower():
                response = self.llm.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1000
                )
                content = response.choices[0].message.content
            elif "claude" in self.model.lower():
                response = self.llm.messages.create(
                    model="claude-opus",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            elif "gemini" in self.model.lower():
                response = self.llm.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 1000,
                    }
                )
                content = response.text
            else:
                return self._default_plan(query)

            # Parse the response
            try:
                plan_data = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    plan_data = json.loads(json_match.group())
                else:
                    return self._default_plan(query)

            plan = ResearchPlan(
                original_query=query,
                search_queries=plan_data.get("search_queries", [query]),
                research_approach=plan_data.get("research_approach", ""),
                expected_focus_areas=plan_data.get("expected_focus_areas", [])
            )
            
            logger.info(f"Research plan created with {len(plan.search_queries)} search queries")
            return plan

        except Exception as e:
            logger.error(f"Error creating research plan: {str(e)}")
            return self._default_plan(query)

    def _default_plan(self, query: str) -> ResearchPlan:
        """
        Create a default research plan when LLM is not available.
        
        Args:
            query: The user's research query
            
        Returns:
            Default ResearchPlan object
        """
        logger.info(f"Using default planning strategy for: {query}")
        
        # Create simple variations of the query
        search_queries = [
            query,
            f"{query} latest 2024",
            f"{query} advances",
            f"{query} research",
            f"{query} guide"
        ]
        
        return ResearchPlan(
            original_query=query,
            search_queries=search_queries,
            research_approach="Comprehensive search using multiple query variations",
            expected_focus_areas=["Latest developments", "Key findings", "Expert insights"]
        )


planner = PlannerAgent()


def create_plan(query: str) -> ResearchPlan:
    """
    Convenience function to create a research plan.
    
    Args:
        query: The research query
        
    Returns:
        ResearchPlan object
    """
    return planner.create_plan(query)
