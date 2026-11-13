package io.flowmcp.llm;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;

/**
 * Anthropic LLM client using HTTP client and Jackson JSON parser.
 */
public class AnthropicClient implements LLMClient {

    private static final String DEFAULT_BASE_URL = "https://api.anthropic.com/v1";
    private static final String ANTHROPIC_VERSION = "2023-06-01";
    private static final int DEFAULT_MAX_TOKENS = 1024;

    private final String model;
    private final String apiKey;
    private final String baseUrl;
    private final int maxTokens;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    public AnthropicClient(String model) {
        this(model, System.getenv("ANTHROPIC_API_KEY"), DEFAULT_BASE_URL, DEFAULT_MAX_TOKENS, HttpClient.newHttpClient(), new ObjectMapper());
    }

    public AnthropicClient(String model, String apiKey) {
        this(model, apiKey, DEFAULT_BASE_URL, DEFAULT_MAX_TOKENS, HttpClient.newHttpClient(), new ObjectMapper());
    }

    public AnthropicClient(String model, String apiKey, String baseUrl, int maxTokens, HttpClient httpClient, ObjectMapper objectMapper) {
        this.model = model;
        this.apiKey = apiKey;
        this.baseUrl = (baseUrl != null && !baseUrl.isBlank()) ? baseUrl : DEFAULT_BASE_URL;
        this.maxTokens = maxTokens > 0 ? maxTokens : DEFAULT_MAX_TOKENS;
        this.httpClient = httpClient != null ? httpClient : HttpClient.newHttpClient();
        this.objectMapper = objectMapper != null ? objectMapper : new ObjectMapper();
    }

    @Override
    public String complete(String prompt) {
        if (apiKey == null || apiKey.isBlank()) {
            throw new IllegalStateException("ANTHROPIC_API_KEY environment variable is not set.");
        }
        if (model == null || model.isBlank()) {
            throw new IllegalArgumentException("Model cannot be null or empty.");
        }

        try {
            String safePrompt = prompt != null ? prompt : "";
            String body = objectMapper.writeValueAsString(Map.of(
                "model", model,
                "max_tokens", maxTokens,
                "messages", List.of(Map.of("role", "user", "content", safePrompt))
            ));

            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/messages"))
                .header("Content-Type", "application/json")
                .header("x-api-key", apiKey)
                .header("anthropic-version", ANTHROPIC_VERSION)
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                throw new RuntimeException("Anthropic API returned HTTP " + response.statusCode() + ": " + response.body());
            }

            JsonNode root = objectMapper.readTree(response.body());
            JsonNode content = root.get("content");
            if (content == null || content.isEmpty()) {
                throw new RuntimeException("Missing 'content' in Anthropic response: " + response.body());
            }
            return content.get(0).path("text").asText();
        } catch (Exception e) {
            throw new RuntimeException("Anthropic request failed: " + e.getMessage(), e);
        }
    }
}
