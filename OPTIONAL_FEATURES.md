"""
OPTIONAL FEATURES GUIDE
========================

This guide covers optional enhancements you can add to the Autonomous Research Agent.
"""

# ============================================================================
# 1. LANGSMITH INTEGRATION (Observability & Debugging)
# ============================================================================

LANGSMITH_GUIDE = """
LANGSMITH INTEGRATION
═════════════════════

LangSmith provides observability into your LLM calls and agent execution.

SETUP:
──────
1. Create account at https://smith.langchain.com/
2. Get your API key from settings
3. Update .env:
   
   USE_LANGSMITH=true
   LANGSMITH_API_KEY=your_api_key_here
   LANGSMITH_PROJECT=agentic-ai-research

USAGE:
──────
from app.main import research

# Traces will be automatically recorded
brief = research("Your query")

# View traces at: https://smith.langchain.com/

BENEFITS:
─────────
✓ See all LLM calls and responses
✓ Track token usage
✓ Debug agent behavior
✓ Performance monitoring
✓ Cost analysis
"""


# ============================================================================
# 2. LANGFUSE INTEGRATION (Analytics & Monitoring)
# ============================================================================

LANGFUSE_GUIDE = """
LANGFUSE INTEGRATION
════════════════════

Langfuse provides detailed analytics about your LLM usage.

SETUP:
──────
1. Create account at https://langfuse.com/
2. Get API keys from settings
3. Update .env:
   
   USE_LANGFUSE=true
   LANGFUSE_API_KEY=your_public_key
   LANGFUSE_SECRET_KEY=your_secret_key

USAGE:
──────
from app.main import research
from langfuse import Langfuse

langfuse = Langfuse()

# Your research calls
brief = research("Your query")

# View analytics at: https://langfuse.com/

BENEFITS:
─────────
✓ Detailed analytics dashboard
✓ Cost tracking
✓ Model comparison
✓ Performance trends
✓ Error analysis
"""


# ============================================================================
# 3. MCP SERVER INTEGRATION
# ============================================================================

MCP_GUIDE = """
MODEL CONTEXT PROTOCOL (MCP) SERVER INTEGRATION
═══════════════════════════════════════════════════

Use MCP servers to provide your tools to Claude or other MCP-compatible platforms.

BASIC SETUP:
────────────
1. Install MCP SDK:
   pip install mcp

2. Create app/mcp_server.py:
   
   from mcp.server import Server
   from app.tools.web_search import search
   from app.tools.url_scraper import scrape
   
   server = Server("agentic-ai-research")
   
   @server.call_tool()
   async def web_search(query: str):
       return search(query)
   
   @server.call_tool()
   async def url_scrape(url: str):
       return scrape(url)
   
   if __name__ == "__main__":
       server.run()

3. Configure in Claude settings or MCP client:
   
   {
       "mcpServers": {
           "agentic-ai": {
               "command": "python",
               "args": ["app/mcp_server.py"]
           }
       }
   }

BENEFITS:
─────────
✓ Use your tools in Claude/other MCP clients
✓ Standardized tool interface
✓ Seamless integration
✓ No custom API needed
"""


# ============================================================================
# 4. FLASK API ENDPOINT
# ============================================================================

FLASK_API_GUIDE = """
CREATE A FLASK API ENDPOINT
════════════════════════════

Expose your research agent as a web API.

SETUP:
──────
1. Install Flask:
   pip install flask

2. Create app/api.py:
   
   from flask import Flask, request, jsonify
   from app.main import research, export_brief
   import json
   from datetime import datetime
   
   app = Flask(__name__)
   
   @app.route('/research', methods=['POST'])
   def research_endpoint():
       data = request.json
       query = data.get('query')
       format = data.get('format', 'json')
       
       try:
           brief = research(query)
           output = export_brief(brief, format=format)
           
           return jsonify({
               'success': True,
               'data': json.loads(output) if format == 'json' else output,
               'timestamp': datetime.now().isoformat()
           })
       except Exception as e:
           return jsonify({
               'success': False,
               'error': str(e)
           }), 400
   
   @app.route('/health', methods=['GET'])
   def health():
       return jsonify({'status': 'healthy'})
   
   if __name__ == '__main__':
       app.run(debug=True, port=5000)

3. Run the API:
   python app/api.py

4. Test:
   curl -X POST http://localhost:5000/research \\
     -H "Content-Type: application/json" \\
     -d '{"query": "AI memory systems", "format": "json"}'

USAGE:
──────
async def fetch_research(query):
    response = await client.post('http://localhost:5000/research', 
                                 json={'query': query})
    return response.json()
"""


# ============================================================================
# 5. DOCKER DEPLOYMENT
# ============================================================================

DOCKER_GUIDE = """
DOCKER DEPLOYMENT
═════════════════

Package your research agent in a Docker container.

SETUP:
──────
1. Create Dockerfile in project root:
   
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   ENV PYTHONUNBUFFERED=1
   
   CMD ["python", "app/main.py"]

2. Create .dockerignore:
   
   __pycache__
   *.pyc
   .env
   research_outputs/
   .git

3. Build image:
   docker build -t agentic-ai-research .

4. Run container:
   docker run -e OPENAI_API_KEY=sk-... agentic-ai-research

DOCKER-COMPOSE:
────────────────
Create docker-compose.yml for easier management:

   version: '3.8'
   
   services:
     research-agent:
       build: .
       environment:
         - OPENAI_API_KEY=\${OPENAI_API_KEY}
         - LLM_MODEL=gpt-4-turbo
       volumes:
         - ./research_outputs:/app/research_outputs
       ports:
         - "5000:5000"

Run with: docker-compose up

DEPLOYMENT:
───────────
• Docker Hub: docker push username/agentic-ai-research
• AWS ECR: Push to Elastic Container Registry
• Google Cloud Run: Deploy as serverless function
• Kubernetes: Use with orchestration tools
"""


# ============================================================================
# 6. STREAMLIT WEB INTERFACE
# ============================================================================

STREAMLIT_GUIDE = """
STREAMLIT WEB INTERFACE
═══════════════════════

Create a beautiful web UI for your research agent.

SETUP:
──────
1. Install Streamlit:
   pip install streamlit

2. Create app_streamlit.py:
   
   import streamlit as st
   from app.main import research, export_brief
   
   st.set_page_config(page_title="Research Agent")
   st.title("🤖 Autonomous Research Agent")
   
   query = st.text_input("Enter your research question:")
   
   if query:
       with st.spinner("Conducting research..."):
           brief = research(query)
       
       st.success("Research completed!")
       
       tab1, tab2, tab3 = st.tabs(["Summary", "Details", "Export"])
       
       with tab1:
           st.metric("Confidence", f"{brief.confidence_score:.0%}")
           st.write(brief.executive_summary)
       
       with tab2:
           st.subheader("Key Findings")
           for finding in brief.key_findings:
               st.write(f"• {finding.finding}")
               st.write(f"  Relevance: {finding.relevance_score:.0%}")
       
       with tab3:
           format = st.selectbox("Export format:", ["json", "markdown", "text"])
           output = export_brief(brief, format=format)
           st.download_button(
               label=f"Download {format.upper()}",
               data=output,
               file_name=f"research.{format}"
           )

3. Run:
   streamlit run app_streamlit.py

FEATURES:
─────────
✓ Real-time research execution
✓ Beautiful UI
✓ Export functionality
✓ Result visualization
✓ History tracking (optional)
"""


# ============================================================================
# 7. BACKGROUND TASK QUEUE
# ============================================================================

CELERY_GUIDE = """
BACKGROUND TASK PROCESSING (CELERY)
═════════════════════════════════════

Process research requests asynchronously with Celery.

SETUP:
──────
1. Install Celery and Redis:
   pip install celery redis

2. Create app/tasks.py:
   
   from celery import Celery
   from app.main import research
   
   app = Celery('agentic_ai')
   app.config_from_object('celeryconfig')
   
   @app.task
   def conduct_research_task(query):
       brief = research(query)
       return brief.model_dump()

3. Create celeryconfig.py:
   
   broker_url = 'redis://localhost:6379'
   result_backend = 'redis://localhost:6379'

4. Start worker:
   celery -A app.tasks worker --loglevel=info

USAGE:
──────
from app.tasks import conduct_research_task

# Async execution
result = conduct_research_task.delay("Your query")
research_brief = result.get()  # Wait for result

BENEFITS:
─────────
✓ Non-blocking API calls
✓ Automatic retry logic
✓ Multiple workers
✓ Result caching
✓ Rate limiting
"""


# ============================================================================
# 8. KNOWLEDGE BASE INTEGRATION
# ============================================================================

KNOWLEDGE_BASE_GUIDE = """
INTEGRATE WITH KNOWLEDGE BASE
══════════════════════════════

Connect your research agent to a knowledge base (RAG - Retrieval Augmented Generation).

SETUP WITH PINECONE:
────────────────────
1. Create Pinecone account
2. Create vector index
3. Update agent to use RAG:
   
   from pinecone import Pinecone
   from langchain.vectorstores import Pinecone as PineconeStore
   
   # Index research findings in Pinecone
   # Augment synthesis with relevant past findings

SETUP WITH CHROMA:
──────────────────
1. Install: pip install chromadb
2. Store embeddings: 
   from chromadb import Client
   client = Client()
   
   # Add research findings to collection
   collection = client.create_collection("research")

BENEFITS:
─────────
✓ Reference previous research
✓ Faster synthesis
✓ Consistency across queries
✓ Learning over time
✓ Better context
"""


# ============================================================================
# 9. ADVANCED MONITORING & METRICS
# ============================================================================

MONITORING_GUIDE = """
ADVANCED MONITORING & METRICS
══════════════════════════════

Track detailed metrics about your research agent's performance.

SETUP WITH PROMETHEUS:
──────────────────────
1. Install: pip install prometheus-client
2. Create metrics:
   
   from prometheus_client import Counter, Histogram
   
   research_count = Counter('research_total', 'Total research requests')
   research_duration = Histogram('research_duration', 'Research duration')

3. Expose metrics:
   from prometheus_client import start_http_server
   start_http_server(8000)

GRAFANA DASHBOARDS:
───────────────────
• Create dashboards for:
  - Research count over time
  - Average execution time
  - Error rate
  - Token usage
  - Cost per query

METRICS TO TRACK:
────────────────
✓ Total research requests
✓ Success/failure rates
✓ Execution time
✓ LLM token usage
✓ Cost per query
✓ Cache hit rate
✓ Error types
"""


# ============================================================================
# SUMMARY TABLE
# ============================================================================

SUMMARY = """
FEATURE MATRIX
═══════════════

Feature                 | Complexity | Benefit       | Time to Setup
─────────────────────────────────────────────────────────────────────
LangSmith              | Low        | Debugging     | 10 minutes
Langfuse               | Low        | Analytics     | 10 minutes
MCP Server             | Medium     | Integration   | 30 minutes
Flask API              | Medium     | Web Access    | 20 minutes
Streamlit Web UI       | Low        | User UI       | 30 minutes
Docker                 | Medium     | Deployment    | 20 minutes
Celery Background Jobs | High       | Scalability   | 45 minutes
Knowledge Base (RAG)   | High       | Intelligence  | 60 minutes
Prometheus Monitoring  | High       | Observability | 45 minutes

RECOMMENDED STARTING POINT:
1. Flask API (access from anywhere)
2. LangSmith (understand behavior)
3. Streamlit (nice UI)
"""


def print_guide(title, content):
    """Print formatted guide section."""
    print(f"\n{'──'*40}")
    print(f"{title}")
    print(f"{'──'*40}\n")
    print(content)


def main():
    """Display all optional features."""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + "  OPTIONAL FEATURES & ENHANCEMENTS".center(78) + "║")
    print("║" + "  for Autonomous Research Agent".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    print_guide("1. LANGSMITH INTEGRATION", LANGSMITH_GUIDE)
    print_guide("2. LANGFUSE INTEGRATION", LANGFUSE_GUIDE)
    print_guide("3. MCP SERVER", MCP_GUIDE)
    print_guide("4. FLASK API", FLASK_API_GUIDE)
    print_guide("5. STREAMLIT UI", STREAMLIT_GUIDE)
    print_guide("6. DOCKER DEPLOYMENT", DOCKER_GUIDE)
    print_guide("7. CELERY TASK QUEUE", CELERY_GUIDE)
    print_guide("8. KNOWLEDGE BASE (RAG)", KNOWLEDGE_BASE_GUIDE)
    print_guide("9. MONITORING & METRICS", MONITORING_GUIDE)
    print_guide("FEATURE SUMMARY", SUMMARY)
    
    print("\n" + "="*80)
    print("START WITH:")
    print("="*80)
    print("""
1. Core functionality (already built) ✓
2. LangSmith for debugging (easy)
3. Flask API for web access (medium)
4. Streamlit for nice UI (easy)

Then add advanced features as needed!
    """)


if __name__ == "__main__":
    main()
