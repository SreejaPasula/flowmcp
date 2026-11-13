package io.flowmcp.llm;

/**
 * OpenAI LLM client.
 * Contributors: implement complete() using the OpenAI Java SDK.
 * Dependency: https://github.com/openai/openai-java
 */
public class OpenAIClient implements LLMClient {

    private final String model;

    public OpenAIClient(String model) {
        this.model = model;
    }

    @Override
    public String complete(String prompt) {
        // TODO: implement using OpenAI Java SDK
        // See: https://github.com/openai/openai-java
        throw new UnsupportedOperationException("OpenAI Java client not yet implemented. Contributions welcome!");
    }
}
