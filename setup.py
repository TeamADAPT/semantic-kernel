from setuptools import setup, find_packages

setup(
    name="semantic-kernel-implementation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "semantic-kernel>=0.4.0",
        "python-dotenv>=1.0.0",
        "chromadb>=0.4.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.4.2",
        "python-jose>=3.3.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "black>=23.9.1",
        "isort>=5.12.0",
        "flake8>=6.1.0",
    ],
    python_requires=">=3.8",
)
