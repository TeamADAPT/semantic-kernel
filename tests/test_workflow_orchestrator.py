import pytest
import logging
from pathlib import Path
import json
from src.workflows.orchestrator import WorkflowOrchestrator
from semantic_kernel import Kernel
from src.skills.summarization_skill import SummarizationSkill

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def kernel():
    """Fixture to create a Semantic Kernel instance"""
    kernel = Kernel()
    # Register the summarization skill
    skill = SummarizationSkill()
    kernel.add_plugin(skill, "SummarizationSkill")
    return kernel

@pytest.fixture
def orchestrator(kernel):
    """Fixture to create a WorkflowOrchestrator instance"""
    return WorkflowOrchestrator(kernel)

@pytest.fixture
def sample_workflow():
    """Fixture providing a sample workflow definition"""
    return {
        "name": "test_workflow",
        "description": "A test workflow",
        "version": "1.0.0",
        "steps": [
            {
                "name": "summarize",
                "skill": "SummarizationSkill",
                "function": "summarize_text",
                "parameters": {
                    "context": "Sample text for testing",
                    "max_length": 100
                }
            },
            {
                "name": "extract_points",
                "skill": "SummarizationSkill",
                "function": "extract_key_points",
                "parameters": {
                    "context": "Sample text for testing",
                    "num_points": 3
                }
            }
        ]
    }

@pytest.fixture
def workflow_file(sample_workflow, tmp_path):
    """Fixture to create a temporary workflow file"""
    workflow_path = tmp_path / "workflows"
    workflow_path.mkdir()
    file_path = workflow_path / "test_workflow.json"
    
    with open(file_path, 'w') as f:
        json.dump(sample_workflow, f)
    
    return file_path

@pytest.mark.asyncio
async def test_workflow_registration(orchestrator, sample_workflow):
    """Test workflow registration"""
    try:
        orchestrator.register_workflow("test_workflow", sample_workflow)
        
        # Verify workflow was registered
        assert "test_workflow" in orchestrator.workflows
        assert orchestrator.workflows["test_workflow"] == sample_workflow
        
        logger.info("Workflow registration test passed successfully")
    except Exception as e:
        logger.error(f"Workflow registration test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_workflow_execution(orchestrator, sample_workflow):
    """Test workflow execution"""
    try:
        # Register workflow
        orchestrator.register_workflow("test_workflow", sample_workflow)
        
        # Execute workflow
        results = await orchestrator.execute_workflow(
            "test_workflow",
            {"text": "Sample text for workflow testing"}
        )
        
        assert results is not None
        assert isinstance(results, list)
        assert len(results) == len(sample_workflow["steps"])
        
        logger.info("Workflow execution test passed successfully")
    except Exception as e:
        logger.error(f"Workflow execution test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_parallel_step_execution(orchestrator):
    """Test parallel step execution"""
    try:
        parallel_steps = [
            {
                "name": "step1",
                "skill": "SummarizationSkill",
                "function": "summarize_text",
                "parameters": {
                    "context": "Sample text for parallel execution"
                }
            },
            {
                "name": "step2",
                "skill": "SummarizationSkill",
                "function": "extract_key_points",
                "parameters": {
                    "context": "Sample text for parallel execution"
                }
            }
        ]
        
        results = await orchestrator.run_parallel_steps(parallel_steps)
        
        assert results is not None
        assert isinstance(results, list)
        assert len(results) == len(parallel_steps)
        
        logger.info("Parallel step execution test passed successfully")
    except Exception as e:
        logger.error(f"Parallel step execution test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_workflow_status(orchestrator, sample_workflow):
    """Test getting workflow status"""
    try:
        # Register workflow
        orchestrator.register_workflow("test_workflow", sample_workflow)
        
        # Get status
        status = orchestrator.get_workflow_status("test_workflow")
        
        assert status is not None
        assert isinstance(status, dict)
        assert status["name"] == "test_workflow"
        assert status["step_count"] == len(sample_workflow["steps"])
        assert status["registered"] is True
        
        logger.info("Workflow status test passed successfully")
    except Exception as e:
        logger.error(f"Workflow status test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_workflow_listing(orchestrator, sample_workflow):
    """Test listing workflows"""
    try:
        # Register workflow
        orchestrator.register_workflow("test_workflow", sample_workflow)
        
        # List workflows
        workflows = orchestrator.list_workflows()
        
        assert workflows is not None
        assert isinstance(workflows, list)
        assert "test_workflow" in workflows
        
        logger.info("Workflow listing test passed successfully")
    except Exception as e:
        logger.error(f"Workflow listing test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_workflow_conditions(orchestrator):
    """Test workflow conditional execution"""
    try:
        workflow_with_conditions = {
            "name": "conditional_workflow",
            "steps": [
                {
                    "name": "step1",
                    "skill": "SummarizationSkill",
                    "function": "summarize_text",
                    "parameters": {
                        "context": "Sample text for testing"
                    },
                    "continue_if": {
                        "success": True
                    }
                }
            ]
        }
        
        orchestrator.register_workflow("conditional_workflow", workflow_with_conditions)
        results = await orchestrator.execute_workflow("conditional_workflow")
        
        assert results is not None
        assert isinstance(results, list)
        
        logger.info("Workflow conditions test passed successfully")
    except Exception as e:
        logger.error(f"Workflow conditions test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_error_handling(orchestrator):
    """Test error handling in workflows"""
    try:
        # Test with non-existent workflow
        with pytest.raises(ValueError):
            await orchestrator.execute_workflow("non_existent_workflow", {})
        
        # Test with invalid step configuration
        invalid_workflow = {
            "name": "invalid_workflow",
            "steps": [
                {
                    "name": "invalid_step",
                    "skill": "NonExistentSkill",
                    "function": "non_existent_function"
                }
            ]
        }
        
        orchestrator.register_workflow("invalid_workflow", invalid_workflow)
        with pytest.raises(Exception):
            await orchestrator.execute_workflow("invalid_workflow", {})
        
        logger.info("Error handling test passed successfully")
    except Exception as e:
        logger.error(f"Error handling test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_workflow_parameters(orchestrator, sample_workflow):
    """Test workflow parameter handling"""
    try:
        # Modify workflow to include parameter validation
        workflow_with_params = {
            **sample_workflow,
            "parameters": {
                "required": ["text"],
                "optional": ["max_length"]
            }
        }
        
        orchestrator.register_workflow("parameterized_workflow", workflow_with_params)
        
        # Test with valid parameters
        valid_params = {"text": "Sample text", "max_length": 100}
        results = await orchestrator.execute_workflow("parameterized_workflow", valid_params)
        assert results is not None
        
        # Test with missing required parameter
        invalid_params = {"max_length": 100}
        with pytest.raises(ValueError):
            await orchestrator.execute_workflow("parameterized_workflow", invalid_params)
        
        logger.info("Workflow parameters test passed successfully")
    except Exception as e:
        logger.error(f"Workflow parameters test failed: {str(e)}")
        raise
