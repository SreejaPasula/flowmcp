package io.flowmcp.mcp;

import java.util.List;

/**
 * MCP (Model Context Protocol) client.
 * Contributors: implement real MCP server connections here.
 * See: https://modelcontextprotocol.io/docs
 */
public class MCPClient {

    private final List<String> tools;

    public MCPClient(List<String> tools) {
        this.tools = tools;
    }

    public String run(String query) {
        // TODO: implement MCP server communication
        // Contributors: connect to MCP servers and execute tools
        return "";
    }

    public List<String> listTools() {
        return tools;
    }
}
