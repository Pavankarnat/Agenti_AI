"""
Pydantic models and schemas for data validation and serialization.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# =============== SEARCH RESULTS ===============
class SearchResult(BaseModel):
    """Model for a single search result."""
    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the search result")
    snippet: str = Field(..., description="Brief snippet from the search result")
    source: str = Field(default="", description="Source of the search result")


class SearchResults(BaseModel):
    """Model for search results from the web."""
    query: str = Field(..., description="The search query used")
    results: List[SearchResult] = Field(default_factory=list, description="List of search results")
    total_results: int = Field(default=0, description="Total number of results found")


# =============== EXTRACTED CONTENT ===============
class ExtractedURL(BaseModel):
    """Model for content extracted from a URL."""
    url: str = Field(..., description="The URL that was extracted")
    title: str = Field(default="", description="Page title")
    content: str = Field(default="", description="Extracted text content")
    word_count: int = Field(default=0, description="Number of words extracted")
    extraction_date: datetime = Field(default_factory=datetime.now, description="When the content was extracted")
    extraction_status: str = Field(default="success", description="Status of extraction (success/failed)")
    error_message: Optional[str] = Field(default=None, description="Error message if extraction failed")


# =============== RESEARCH PLANNING ===============
class ResearchPlan(BaseModel):
    """Model for the research plan."""
    original_query: str = Field(..., description="The original user query")
    search_queries: List[str] = Field(default_factory=list, description="List of search queries to execute")
    research_approach: str = Field(default="", description="Description of the research approach")
    expected_focus_areas: List[str] = Field(default_factory=list, description="Key areas to focus on")


# =============== RESEARCH FINDINGS ===============
class ResearchFinding(BaseModel):
    """Model for a single research finding."""
    finding: str = Field(..., description="The research finding")
    source_url: str = Field(..., description="Source URL for this finding")
    relevance_score: float = Field(default=0.8, description="Relevance score (0-1)")
    finding_type: str = Field(default="fact", description="Type of finding (fact/insight/statistic/etc)")


class ResearchBrief(BaseModel):
    """Model for the final research brief output."""
    query: str = Field(..., description="Original user query")
    title: str = Field(..., description="Title of the research brief")
    executive_summary: str = Field(..., description="High-level summary of findings")
    key_findings: List[ResearchFinding] = Field(default_factory=list, description="Detailed findings")
    sources: List[str] = Field(default_factory=list, description="List of sources used")
    confidence_score: float = Field(default=0.8, description="Confidence score of the research (0-1)")
    research_metadata: dict = Field(default_factory=dict, description="Additional metadata")
    generation_date: datetime = Field(default_factory=datetime.now, description="When the brief was generated")


# =============== AGENT STATE ===============
class AgentState(BaseModel):
    """Model for tracking agent state during execution."""
    query: str = Field(..., description="The user query")
    plan: Optional[ResearchPlan] = Field(default=None, description="The research plan")
    search_results: Optional[SearchResults] = Field(default=None, description="Search results")
    extracted_content: List[ExtractedURL] = Field(default_factory=list, description="Extracted content from URLs")
    final_brief: Optional[ResearchBrief] = Field(default=None, description="Final research brief")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
    execution_metadata: dict = Field(default_factory=dict, description="Execution metadata")
