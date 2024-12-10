import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
WORKFLOW_DIR = CONFIG_DIR / "workflows"

# Ensure required directories exist
WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
API_CONFIG = {
    "host": os.getenv("SERVICE_HOST", "0.0.0.0"),
    "port": int(os.getenv("SERVICE_PORT", 8000)),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "cors_origins": os.getenv("CORS_ORIGINS", "*").split(","),
}

# LLM Configuration
LLM_CONFIG = {
    "provider": os.getenv("LLM_PROVIDER", "openai"),
    "model": os.getenv("LLM_MODEL", "gpt-4"),
    "api_key": os.getenv("OPENAI_API_KEY"),
    "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "azure_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
}

# Vector Database Configuration
VECTOR_DB_CONFIG = {
    "provider": os.getenv("VECTOR_DB_PROVIDER", "chroma"),
    "host": os.getenv("VECTOR_DB_HOST", "localhost"),
    "port": int(os.getenv("VECTOR_DB_PORT", 8000)),
}

# Memory Configuration
MEMORY_CONFIG = {
    "collection_name": "semantic_memory",
    "min_relevance_score": float(os.getenv("MIN_RELEVANCE_SCORE", 0.7)),
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "sk_service.log",
            "formatter": "standard",
            "level": "INFO",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": True,
        },
    },
}

# Skill Configuration
SKILL_CONFIG = {
    "max_retries": int(os.getenv("SKILL_MAX_RETRIES", 3)),
    "retry_delay": int(os.getenv("SKILL_RETRY_DELAY", 1)),
    "timeout": int(os.getenv("SKILL_TIMEOUT", 30)),
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary"""
    return {
        "api": API_CONFIG,
        "llm": LLM_CONFIG,
        "vector_db": VECTOR_DB_CONFIG,
        "memory": MEMORY_CONFIG,
        "logging": LOGGING_CONFIG,
        "skill": SKILL_CONFIG,
    }

def validate_config() -> None:
    """Validate required configuration values"""
    required_vars = [
        ("OPENAI_API_KEY", LLM_CONFIG["api_key"]),
    ]

    missing_vars = [var for var, value in required_vars if not value]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

# Validate configuration on import
validate_config()
