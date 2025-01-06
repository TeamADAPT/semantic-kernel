import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.memory import VectorMemory
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sk_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SemanticKernelApp:
    def __init__(self):
        self._setup_environment()
        self.kernel = Kernel()
        self.setup_llm()
        self.setup_memory()
        self._load_skills()
        logger.info("Semantic Kernel App initialized")

    def _setup_environment(self):
        """Load environment variables"""
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv()
        else:
            logger.warning(".env file not found, using system environment variables")

    def setup_llm(self):
        """Configure LLM integration"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found in environment variables")
            
            self.kernel.add_text_completion_service(
                "openai",
                "gpt-4",
                api_key=api_key
            )
            logger.info("LLM service configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure LLM service: {str(e)}")
            raise

    def setup_memory(self):
        """Configure vector memory storage"""
        try:
            self.memory = VectorMemory("chroma")
            self.kernel.add_memory(self.memory)
            logger.info("Memory service configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure memory service: {str(e)}")
            raise

    def _load_skills(self):
        """Load all available skills"""
        try:
            skills_dir = Path(__file__).parent / "skills"
            if not skills_dir.exists():
                logger.warning("Skills directory not found")
                return

            for skill_file in skills_dir.glob("*_skill.py"):
                skill_name = skill_file.stem
                logger.info(f"Loading skill: {skill_name}")
                # Import and register skill (to be implemented)
                
        except Exception as e:
            logger.error(f"Failed to load skills: {str(e)}")
            raise

    async def verify_setup(self):
        """Verify the setup by running a test prompt"""
        try:
            result = await self.kernel.skills.text_completion("Test: Semantic Kernel is working.")
            logger.info("Setup verification completed successfully")
            return result
        except Exception as e:
            logger.error(f"Setup verification failed: {str(e)}")
            raise

    async def run_skill(self, skill_name: str, function_name: str, parameters: dict = None):
        """
        Run a specific skill function
        
        Args:
            skill_name: Name of the skill to run
            function_name: Name of the function to execute
            parameters: Optional parameters for the function
            
        Returns:
            The result of the skill execution
        """
        try:
            if parameters is None:
                parameters = {}
            
            result = await self.kernel.run_skill(
                skill_name,
                function_name,
                parameters
            )
            logger.info(f"Successfully executed skill: {skill_name}.{function_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to execute skill {skill_name}.{function_name}: {str(e)}")
            raise

def create_app():
    """Create and configure the Semantic Kernel application"""
    try:
        app = SemanticKernelApp()
        logger.info("Semantic Kernel application created successfully")
        return app
    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}")
        raise

if __name__ == "__main__":
    app = create_app()
