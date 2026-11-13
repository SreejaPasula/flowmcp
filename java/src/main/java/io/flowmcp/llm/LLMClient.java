package io.flowmcp.llm;

/**
 * Base interface for all LLM clients.
 * Contributors: implement this to add a new provider.
 */
public interface LLMClient {

    String complete(String prompt);

    static LLMClient fromString(String modelString) {
        if (!modelString.contains("/")) {
            throw new IllegalArgumentException("Invalid model format. Use 'provider/model' e.g. 'openai/gpt-4'");
        }
        String[] parts = modelString.split("/", 2);
        String provider = parts[0];
        String model = parts[1];

        return switch (provider) {
            case "openai" -> new OpenAIClient(model);
            case "anthropic" -> new AnthropicClient(model);
            case "ollama" -> new OllamaClient(model);
            case "gemini" -> new GeminiClient(model);
            default -> throw new IllegalArgumentException("Unsupported provider: " + provider);
        };
    }
}
