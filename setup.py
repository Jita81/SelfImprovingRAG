from setuptools import setup, find_packages

setup(
    name="selfimprovingrag",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.4.2",
        "langchain==0.0.330",
        "openai==1.3.0",
        "chromadb==0.4.15",
        "numpy==1.24.3",
        "beautifulsoup4==4.12.2",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "pytest==7.4.3",
        "duckduckgo-search==3.9.3"
    ]
) 