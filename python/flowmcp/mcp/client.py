from typing import List, Optional


class MCP:
    """
    MCP (Model Context Protocol) client.
    Connects to MCP servers and runs tools.

    Example:
        mcp = MCP(["filesystem", "github"])
        result = mcp.run("List files in /src")
    """

    def __init__(self, tools: List[str]):
        self.tools = tools
        self._servers = {}
        self._connect()

    def _connect(self):
        for tool in self.tools:
            try:
                self._servers[tool] = MCPServer(tool)
            except Exception as e:
                print(f"[flowmcp] Warning: Could not connect to MCP tool '{tool}': {e}")

    def run(self, query: str) -> str:
        results = []
        for name, server in self._servers.items():
            try:
                result = server.execute(query)
                if result:
                    results.append(f"[{name}]: {result}")
            except Exception as e:
                results.append(f"[{name}]: Error — {e}")
        return "\n".join(results)

    def list_tools(self) -> List[str]:
        return list(self._servers.keys())


class MCPServer:
    """
    Represents a connection to a single MCP server.
    Contributors: implement specific MCP server integrations here.
    """

    def __init__(self, name: str):
        self.name = name

    def execute(self, query: str) -> Optional[str]:
        # Contributors: add real MCP server communication here
        # See: https://modelcontextprotocol.io/docs
        return None
