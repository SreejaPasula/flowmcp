from typing import Optional, List, Union
from .llm.base import LLM
from .rag.loader import RAG
from .mcp.client import MCP


class Pipeline:
    """
    Main entry point. Combines LLM + RAG + MCP in one simple interface.

    Example:
        pipeline = Pipeline(
            llm="openai/gpt-4",
            docs="./my-docs",
            tools=["filesystem", "github"]
        )
        answer = pipeline.ask("What is our refund policy?")
    """

    def __init__(
        self,
        llm: Union[str, LLM],
        docs: Optional[Union[str, List[str]]] = None,
        tools: Optional[List[str]] = None,
    ):
        self.llm = LLM.from_string(llm) if isinstance(llm, str) else llm
        self.rag = RAG(docs) if docs else None
        self.mcp = MCP(tools) if tools else None

    def ask(self, question: str) -> str:
        context = ""

        if self.rag:
            chunks = self.rag.retrieve(question)
            context = "\n\n".join(chunks)

        tool_results = ""
        if self.mcp:
            tool_results = self.mcp.run(question)

        prompt = self._build_prompt(question, context, tool_results)
        return self.llm.complete(prompt)

    def _build_prompt(self, question: str, context: str, tool_results: str) -> str:
        parts = []
        if context:
            parts.append(f"Context from documents:\n{context}")
        if tool_results:
            parts.append(f"Tool results:\n{tool_results}")
        parts.append(f"Question: {question}")
        return "\n\n".join(parts)
