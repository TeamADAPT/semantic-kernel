from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json

from ..main import SemanticKernelApp
from ..workflows.orchestrator import WorkflowOrchestrator

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Semantic Kernel API",
    description="REST API for Semantic Kernel functionality",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class SummarizeRequest(BaseModel):
    text: str
    max_length: Optional[int] = None

class KeyPointsRequest(BaseModel):
    text: str
    num_points: Optional[int] = 5

class WorkflowRequest(BaseModel):
    workflow_name: str
    parameters: Optional[Dict[str, Any]] = None

class MemoryStoreRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class MemorySearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    min_relevance_score: Optional[float] = 0.7

# Dependency for getting app instance
async def get_app():
    try:
        return SemanticKernelApp()
    except Exception as e:
        logger.error(f"Failed to initialize Semantic Kernel App: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize application")

# Dependency for getting workflow orchestrator
async def get_orchestrator(app: SemanticKernelApp = Depends(get_app)):
    try:
        return WorkflowOrchestrator(app.kernel)
    except Exception as e:
        logger.error(f"Failed to initialize Workflow Orchestrator: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize workflow orchestrator")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/summarize")
async def summarize_text(
    request: SummarizeRequest,
    app: SemanticKernelApp = Depends(get_app)
):
    """Summarize text using the summarization skill"""
    try:
        result = await app.run_skill(
            "SummarizationSkill",
            "summarize_text",
            {"context": request.text, "max_length": request.max_length}
        )
        return {"summary": result}
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-key-points")
async def extract_key_points(
    request: KeyPointsRequest,
    app: SemanticKernelApp = Depends(get_app)
):
    """Extract key points from text"""
    try:
        result = await app.run_skill(
            "SummarizationSkill",
            "extract_key_points",
            {"context": request.text, "num_points": request.num_points}
        )
        return {"key_points": result}
    except Exception as e:
        logger.error(f"Key points extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow/execute")
async def execute_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    orchestrator: WorkflowOrchestrator = Depends(get_orchestrator)
):
    """Execute a workflow by name"""
    try:
        # Start workflow execution in background
        background_tasks.add_task(
            orchestrator.execute_workflow,
            request.workflow_name,
            request.parameters
        )
        return {
            "status": "accepted",
            "message": f"Workflow {request.workflow_name} execution started"
        }
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/list")
async def list_workflows(
    orchestrator: WorkflowOrchestrator = Depends(get_orchestrator)
):
    """List all available workflows"""
    try:
        workflows = orchestrator.list_workflows()
        return {"workflows": workflows}
    except Exception as e:
        logger.error(f"Failed to list workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/{workflow_name}/status")
async def get_workflow_status(
    workflow_name: str,
    orchestrator: WorkflowOrchestrator = Depends(get_orchestrator)
):
    """Get status of a specific workflow"""
    try:
        status = orchestrator.get_workflow_status(workflow_name)
        return status
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/store")
async def store_memory(
    request: MemoryStoreRequest,
    app: SemanticKernelApp = Depends(get_app)
):
    """Store text in memory"""
    try:
        memory_id = await app.memory.store_memory(
            request.text,
            request.metadata,
            request.tags
        )
        return {"memory_id": memory_id}
    except Exception as e:
        logger.error(f"Failed to store memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/search")
async def search_memory(
    request: MemorySearchRequest,
    app: SemanticKernelApp = Depends(get_app)
):
    """Search for similar memories"""
    try:
        results = await app.memory.retrieve_similar(
            request.query,
            request.limit,
            request.min_relevance_score
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Memory search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/stats")
async def get_memory_stats(
    app: SemanticKernelApp = Depends(get_app)
):
    """Get memory storage statistics"""
    try:
        stats = await app.memory.get_memory_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get memory stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "status": "error",
        "message": "An unexpected error occurred",
        "detail": str(exc)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
