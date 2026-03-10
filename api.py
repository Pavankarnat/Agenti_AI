"""
FastAPI backend for AGENTIC_AI Dashboard.
Exposes the ResearchAgent pipeline via REST + Server-Sent Events (SSE) for live streaming.

Run with:
    pip install fastapi uvicorn sse-starlette
    uvicorn api:app --reload --port 8000
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ── Import your existing pipeline ────────────────────────────────────────────
from app.agents.planner import planner
from app.agents.researcher import researcher
from app.agents.writer import writer
from app.main import ResearchAgent, export_brief

logger = logging.getLogger(__name__)

app = FastAPI(title="AGENTIC_AI API", version="1.0.0")

# Allow React dev server (localhost:5173 / 3000) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ────────────────────────────────────────────────
class ResearchRequest(BaseModel):
    query: str


class SSEEvent(BaseModel):
    agent: str          # "planner" | "researcher" | "writer" | "websearch" | "system"
    type: str           # "log" | "status" | "result" | "error"
    message: str
    data: dict | None = None


# ── SSE helper ────────────────────────────────────────────────────────────────
def make_event(agent: str, type: str, message: str, data: dict = None) -> str:
    payload = SSEEvent(agent=agent, type=type, message=message, data=data)
    return f"data: {payload.model_dump_json()}\n\n"


# ── Streaming research pipeline ───────────────────────────────────────────────
async def run_pipeline_stream(query: str) -> AsyncGenerator[str, None]:
    """
    Runs the full 4-agent pipeline and yields SSE events at each step.
    Each blocking Python call is wrapped in asyncio.to_thread so the event
    loop stays responsive.
    """

    yield make_event("system", "status", "Pipeline started", {"query": query})

    try:
        # ── PHASE 1 · PLANNER ────────────────────────────────────────────────
        yield make_event("planner", "status", "RUNNING")
        yield make_event("planner", "log", "Initializing task decomposition engine...")

        plan = await asyncio.to_thread(planner.create_plan, query)

        yield make_event("planner", "log", f"Research approach: {plan.research_approach}")
        yield make_event("planner", "log", f"Generated {len(plan.search_queries)} search queries")
        for i, q in enumerate(plan.search_queries, 1):
            yield make_event("planner", "log", f"  Query {i}: {q}")
        yield make_event("planner", "log", f"Focus areas: {', '.join(plan.expected_focus_areas)}")
        yield make_event("planner", "status", "DONE", {
            "search_queries": plan.search_queries,
            "research_approach": plan.research_approach,
            "focus_areas": plan.expected_focus_areas,
        })

        # ── PHASE 2a · WEB SEARCH (part of researcher) ───────────────────────
        yield make_event("websearch", "status", "RUNNING")
        yield make_event("websearch", "log", "Constructing DuckDuckGo queries...")

        search_results = await asyncio.to_thread(
            researcher.execute_searches, plan.search_queries
        )

        yield make_event("websearch", "log", f"Found {search_results.total_results} unique URLs")
        for r in search_results.results[:5]:
            yield make_event("websearch", "log", f"  ↳ {r.title[:60]}  —  {r.url}")
        yield make_event("websearch", "status", "DONE", {
            "total_results": search_results.total_results,
            "urls": [r.url for r in search_results.results],
        })

        # ── PHASE 2b · RESEARCHER (content extraction) ───────────────────────
        yield make_event("researcher", "status", "RUNNING")
        yield make_event("researcher", "log", f"Extracting content from top {min(len(search_results.results), researcher.max_url_extractions)} URLs...")

        extracted_content = await asyncio.to_thread(
            researcher.extract_content, search_results
        )

        for ec in extracted_content:
            status_icon = "✓" if ec.extraction_status == "success" else "✗"
            yield make_event("researcher", "log",
                f"{status_icon} {ec.url}  ({ec.word_count} words)")

        yield make_event("researcher", "log",
            f"Extraction complete — {len(extracted_content)} pages processed")
        yield make_event("researcher", "status", "DONE", {
            "extracted_count": len(extracted_content),
            "sources": [{"url": e.url, "words": e.word_count,
                         "status": e.extraction_status} for e in extracted_content],
        })

        # ── PHASE 3 · WRITER ─────────────────────────────────────────────────
        yield make_event("writer", "status", "RUNNING")
        yield make_event("writer", "log", "Receiving research brief from Researcher...")
        yield make_event("writer", "log", "Analysing tone, format and source quality...")

        brief = await asyncio.to_thread(
            writer.synthesize_brief, query, search_results, extracted_content
        )

        yield make_event("writer", "log", f"Title: {brief.title}")
        yield make_event("writer", "log", f"Confidence score: {brief.confidence_score:.0%}")
        yield make_event("writer", "log", f"Key findings: {len(brief.key_findings)}")
        yield make_event("writer", "log", f"Sources cited: {len(brief.sources)}")
        yield make_event("writer", "status", "DONE")

        # ── FINAL RESULT ─────────────────────────────────────────────────────
        agent = ResearchAgent.__new__(ResearchAgent)
        markdown_output = agent._export_markdown(brief)

        yield make_event("system", "result", "Pipeline completed successfully", {
            "title": brief.title,
            "query": brief.query,
            "confidence_score": brief.confidence_score,
            "executive_summary": brief.executive_summary,
            "key_findings": [
                {
                    "type": f.finding_type,
                    "finding": f.finding,
                    "relevance": f.relevance_score,
                }
                for f in brief.key_findings
            ],
            "sources": brief.sources,
            "markdown": markdown_output,
            "generation_date": str(brief.generation_date),
        })

    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        yield make_event("system", "error", str(e))


# ── API Routes ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.post("/api/research/stream")
async def research_stream(req: ResearchRequest):
    """
    POST { "query": "..." }
    Returns an SSE stream of pipeline events.
    Each event is:
        data: {"agent": "planner"|"researcher"|"writer"|"websearch"|"system",
                "type": "log"|"status"|"result"|"error",
                "message": "...",
                "data": {...} | null }
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    return StreamingResponse(
        run_pipeline_stream(req.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering
        },
    )


@app.post("/api/research")
async def research_sync(req: ResearchRequest):
    """
    Synchronous endpoint — returns full ResearchBrief JSON.
    Use /api/research/stream for live progress.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        agent = ResearchAgent()
        brief = await asyncio.to_thread(agent.research, req.query)
        return json.loads(export_brief(brief, format="json"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))