from typing import Dict, List, Any, Optional
import logging
from semantic_kernel import Kernel
from pathlib import Path
import json
import asyncio

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """
    Manages and executes semantic kernel workflows.
    Provides functionality for defining, running, and monitoring workflow execution.
    """

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.workflows: Dict[str, Dict] = {}
        self._load_workflow_definitions()
        logger.info("Workflow Orchestrator initialized")

    def _load_workflow_definitions(self) -> None:
        """Load workflow definitions from configuration files"""
        try:
            workflow_dir = Path("config/workflows")
            if workflow_dir.exists():
                for workflow_file in workflow_dir.glob("*.json"):
                    with open(workflow_file, 'r') as f:
                        workflow_def = json.load(f)
                        self.workflows[workflow_file.stem] = workflow_def
                        logger.info(f"Loaded workflow definition: {workflow_file.stem}")
        except Exception as e:
            logger.error(f"Failed to load workflow definitions: {str(e)}")
            raise

    async def execute_workflow(self, 
                             workflow_name: str, 
                             parameters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Execute a defined workflow by name
        
        Args:
            workflow_name: Name of the workflow to execute
            parameters: Optional parameters for the workflow
            
        Returns:
            List of results from each workflow step
        """
        try:
            if workflow_name not in self.workflows:
                raise ValueError(f"Workflow '{workflow_name}' not found")

            workflow_def = self.workflows[workflow_name]
            
            # Validate required parameters
            if "parameters" in workflow_def:
                required_params = workflow_def["parameters"].get("required", [])
                if parameters is None:
                    parameters = {}
                for param in required_params:
                    if param not in parameters:
                        raise ValueError(f"Required parameter '{param}' not provided")
            
            steps = workflow_def.get("steps", [])
            results = []
            
            for step in steps:
                step_result = await self._execute_step(step, parameters)
                results.append(step_result)
                
                # Handle step dependencies and conditional execution
                if not self._should_continue_workflow(step, step_result):
                    logger.info(f"Workflow {workflow_name} stopped after step {step.get('name')}")
                    break
            
            logger.info(f"Workflow {workflow_name} completed successfully")
            return results
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_name}: {str(e)}")
            raise

    async def _execute_step(self, 
                          step: Dict[str, Any], 
                          parameters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a single workflow step
        
        Args:
            step: Step definition
            parameters: Optional parameters for the step
            
        Returns:
            Result of the step execution
        """
        try:
            skill_name = step["skill"]
            function_name = step["function"]
            step_params = {**(parameters or {}), **(step.get("parameters", {}))}
            
            logger.info(f"Executing step: {skill_name}.{function_name}")

            # Get the function from the kernel's registered functions
            function = self.kernel.get_function(skill_name, function_name)
            if not function:
                raise ValueError(f"Function {function_name} not found in skill {skill_name}")

            # Execute the function with parameters
            result = await function.invoke(kernel=self.kernel, **step_params)
            return result

        except Exception as e:
            logger.error(f"Step execution failed: {str(e)}")
            raise

    def _should_continue_workflow(self, 
                                step: Dict[str, Any], 
                                step_result: Any) -> bool:
        """
        Determine if workflow should continue based on step result
        
        Args:
            step: Step definition
            step_result: Result from step execution
            
        Returns:
            Boolean indicating whether to continue workflow
        """
        try:
            conditions = step.get("continue_if", {})
            if not conditions:
                return True

            # Evaluate conditions based on step result
            for condition, value in conditions.items():
                if condition == "equals" and step_result != value:
                    return False
                elif condition == "contains" and value not in str(step_result):
                    return False
                elif condition == "success" and not value:
                    return False

            return True
        except Exception as e:
            logger.error(f"Failed to evaluate workflow conditions: {str(e)}")
            return False

    async def run_parallel_steps(self, 
                               steps: List[Dict[str, Any]], 
                               parameters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Execute multiple workflow steps in parallel
        
        Args:
            steps: List of step definitions to execute
            parameters: Optional parameters for the steps
            
        Returns:
            List of results from parallel execution
        """
        try:
            tasks = [
                self._execute_step(step, parameters)
                for step in steps
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions from parallel execution
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Parallel step execution failed: {str(result)}")
                    raise result
            
            return results
        except Exception as e:
            logger.error(f"Parallel execution failed: {str(e)}")
            raise

    def register_workflow(self, 
                        name: str, 
                        workflow_definition: Dict[str, Any]) -> None:
        """
        Register a new workflow definition
        
        Args:
            name: Name of the workflow
            workflow_definition: Definition of the workflow steps and parameters
        """
        try:
            if name in self.workflows:
                logger.warning(f"Overwriting existing workflow: {name}")
            
            # Validate workflow definition
            required_fields = ["steps"]
            for field in required_fields:
                if field not in workflow_definition:
                    raise ValueError(f"Workflow definition missing required field: {field}")
            
            self.workflows[name] = workflow_definition
            logger.info(f"Registered workflow: {name}")
        except Exception as e:
            logger.error(f"Failed to register workflow: {str(e)}")
            raise

    def get_workflow_status(self, workflow_name: str) -> Dict[str, Any]:
        """
        Get the status and metadata of a registered workflow
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Dictionary containing workflow status and metadata
        """
        try:
            if workflow_name not in self.workflows:
                raise ValueError(f"Workflow '{workflow_name}' not found")
            
            workflow = self.workflows[workflow_name]
            return {
                "name": workflow_name,
                "step_count": len(workflow.get("steps", [])),
                "registered": True,
                "metadata": workflow.get("metadata", {})
            }
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            raise

    def list_workflows(self) -> List[str]:
        """
        List all registered workflows
        
        Returns:
            List of workflow names
        """
        return list(self.workflows.keys())
