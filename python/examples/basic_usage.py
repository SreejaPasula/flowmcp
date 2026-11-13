"""
Basic usage example for flowmcp.
Run: python examples/basic_usage.py
"""
from flowmcp import Pipeline

# Example 1: Simple question answering with your own documents
pipeline = Pipeline(
    llm="openai/gpt-4",
    docs="./my-docs",
)
answer = pipeline.ask("What is our refund policy?")
print(answer)


# Example 2: With MCP tools
pipeline = Pipeline(
    llm="anthropic/claude-3-5-sonnet",
    docs="./my-docs",
    tools=["filesystem", "github"]
)
answer = pipeline.ask("What changed in the codebase last week?")
print(answer)


# Example 3: Local model with Ollama (no API key needed)
pipeline = Pipeline(llm="ollama/llama3")
answer = pipeline.ask("Explain what a RAG pipeline is in simple terms.")
print(answer)
