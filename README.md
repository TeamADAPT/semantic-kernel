# Semantic Kernel Implementation

A comprehensive implementation of Semantic Kernel for orchestrating LLM workflows, with integrated memory storage and reusable skills/plugins.

## Features

- **LLM Integration**: Seamless integration with OpenAI/Azure OpenAI
- **Memory Management**: Vector-based memory storage using Chroma
- **Skill System**: Extensible skill framework with pre-built capabilities
- **Workflow Orchestration**: Flexible workflow definition and execution
- **REST API**: FastAPI-based endpoints for all functionality
- **Comprehensive Testing**: Full test coverage with pytest

## Prerequisites

- Python 3.8+
- pip or poetry for package management
- OpenAI API key or Azure OpenAI credentials

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd semantic-kernel
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Project Structure

```
semantic-kernel/
├── src/
│   ├── api/            # FastAPI endpoints
│   ├── memory/         # Vector memory implementation
│   ├── skills/         # Semantic Kernel skills
│   └── workflows/      # Workflow orchestration
├── tests/              # Test suite
├── config/             # Configuration files
│   └── workflows/      # Workflow definitions
└── docs/              # Documentation
```

## Usage

### Starting the API Server

```bash
uvicorn src.api.endpoints:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example: Using the Summarization Skill

```python
from src.main import SemanticKernelApp

async def main():
    app = SemanticKernelApp()
    
    # Summarize text
    result = await app.run_skill(
        "SummarizationSkill",
        "summarize_text",
        {"text": "Your text here", "max_length": 100}
    )
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Example: Running a Workflow

```python
from src.workflows.orchestrator import WorkflowOrchestrator
from semantic_kernel import Kernel

async def main():
    kernel = Kernel()
    orchestrator = WorkflowOrchestrator(kernel)
    
    # Execute research workflow
    results = await orchestrator.execute_workflow(
        "research_workflow",
        {"text": "Research content here"}
    )
    print(results)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Available Skills

### SummarizationSkill
- `summarize_text`: Generate concise summaries
- `extract_key_points`: Extract main points from text
- `generate_title`: Create appropriate titles
- `analyze_sentiment`: Analyze text sentiment
- `create_abstract`: Generate academic-style abstracts

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key (if using Azure)
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint (if using Azure)
- `VECTOR_DB_HOST`: Vector database host
- `VECTOR_DB_PORT`: Vector database port
- `SERVICE_HOST`: API service host
- `SERVICE_PORT`: API service port
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

### Workflow Configuration

Workflows are defined in JSON files under `config/workflows/`. Example:

```json
{
    "name": "research_workflow",
    "steps": [
        {
            "name": "summarize",
            "skill": "SummarizationSkill",
            "function": "summarize_text",
            "parameters": {
                "max_length": 100
            }
        }
    ]
}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest -m unit
pytest -m integration
pytest -m api

# Generate coverage report
pytest --cov=src --cov-report=html
```

### Code Style

The project uses:
- black for code formatting
- isort for import sorting
- flake8 for linting

```bash
# Format code
black src tests
isort src tests

# Check style
flake8 src tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Microsoft Semantic Kernel team for the original framework
- OpenAI for the LLM capabilities
- ChromaDB team for the vector database

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue if needed

## Roadmap

- [ ] Additional skill implementations
- [ ] Enhanced workflow templates
- [ ] Improved memory persistence
- [ ] Performance optimizations
- [ ] Additional LLM provider support
