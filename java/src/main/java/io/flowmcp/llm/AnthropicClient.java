package io.flowmcp.llm;

/**
 * Anthropic LLM client.
 * Contributors: implement complete() using the Anthropic Java SDK.
 * Dependency: https://github.com/anthropics/anthropic-sdk-java
 */
public class AnthropicClient implements LLMClient {

    private final String model;

    public AnthropicClient(String model) {
        this.model = model;
    }

    @Override
    public String complete(String prompt) {
        // TODO: implement using Anthropic Java SDK
        // See: https://github.com/anthropics/anthropic-sdk-java
        throw new UnsupportedOperationException("Anthropic Java client not yet implemented. Contributions welcome!");
    }
}
