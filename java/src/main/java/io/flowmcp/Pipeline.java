package io.flowmcp;

import io.flowmcp.llm.LLMClient;
import io.flowmcp.rag.RAGPipeline;
import io.flowmcp.mcp.MCPClient;

import java.util.List;

/**
 * Main entry point for flowmcp Java SDK.
 *
 * Example:
 *   Pipeline pipeline = new Pipeline.Builder()
 *       .llm("openai/gpt-4")
 *       .docs("./my-docs")
 *       .tools(List.of("filesystem", "github"))
 *       .build();
 *
 *   String answer = pipeline.ask("What is our refund policy?");
 */
public class Pipeline {

    private final LLMClient llm;
    private final RAGPipeline rag;
    private final MCPClient mcp;

    private Pipeline(Builder builder) {
        this.llm = builder.llm;
        this.rag = builder.rag;
        this.mcp = builder.mcp;
    }

    public String ask(String question) {
        StringBuilder prompt = new StringBuilder();

        if (rag != null) {
            List<String> chunks = rag.retrieve(question);
            if (!chunks.isEmpty()) {
                prompt.append("Context from documents:\n");
                prompt.append(String.join("\n\n", chunks));
                prompt.append("\n\n");
            }
        }

        if (mcp != null) {
            String toolResults = mcp.run(question);
            if (toolResults != null && !toolResults.isEmpty()) {
                prompt.append("Tool results:\n").append(toolResults).append("\n\n");
            }
        }

        prompt.append("Question: ").append(question);
        return llm.complete(prompt.toString());
    }

    public static class Builder {
        private LLMClient llm;
        private RAGPipeline rag;
        private MCPClient mcp;

        public Builder llm(String modelString) {
            this.llm = LLMClient.fromString(modelString);
            return this;
        }

        public Builder llm(LLMClient client) {
            this.llm = client;
            return this;
        }

        public Builder docs(String... paths) {
            this.rag = new RAGPipeline(List.of(paths));
            return this;
        }

        public Builder tools(List<String> tools) {
            this.mcp = new MCPClient(tools);
            return this;
        }

        public Pipeline build() {
            if (llm == null) throw new IllegalStateException("LLM is required");
            return new Pipeline(this);
        }
    }
}
