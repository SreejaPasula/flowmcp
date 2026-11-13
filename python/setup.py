from setuptools import setup, find_packages

setup(
    name="flowmcp",
    version="0.1.0",
    description="Simple RAG + MCP + LLM pipeline framework — a clean alternative to LangChain",
    long_description=open("../README.md").read(),
    long_description_content_type="text/markdown",
    author="SreejaPasula",
    url="https://github.com/SreejaPasula/flowmcp",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.20.0"],
        "all": ["openai>=1.0.0", "anthropic>=0.20.0"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
