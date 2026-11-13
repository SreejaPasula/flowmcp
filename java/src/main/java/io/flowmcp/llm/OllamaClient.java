package io.flowmcp.llm;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;

/**
 * Ollama LLM client — runs local models, no API key needed.
 */
public class OllamaClient implements LLMClient {

    private final String model;
    private final String baseUrl;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    public OllamaClient(String model) {
        this(model, "http://localhost:11434");
    }

    public OllamaClient(String model, String baseUrl) {
        this.model = model;
        this.baseUrl = baseUrl;
        this.httpClient = HttpClient.newHttpClient();
        this.objectMapper = new ObjectMapper();
    }

    // Constructor for testing with custom/mock HttpClient and ObjectMapper
    public OllamaClient(String model, String baseUrl, HttpClient httpClient, ObjectMapper objectMapper) {
        this.model = model;
        this.baseUrl = baseUrl;
        this.httpClient = httpClient;
        this.objectMapper = objectMapper;
    }

    @Override
    public String complete(String prompt) {
        try {
            String body = objectMapper.writeValueAsString(Map.of(
                "model", model,
                "prompt", prompt != null ? prompt : "",
                "stream", false
            ));

            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/generate"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                throw new RuntimeException("Ollama API returned HTTP status " + response.statusCode() + ": " + response.body());
            }

            JsonNode root = objectMapper.readTree(response.body());
            JsonNode responseNode = root.get("response");
            if (responseNode == null || responseNode.isNull()) {
                throw new RuntimeException("Missing 'response' field in Ollama response: " + response.body());
            }
            return responseNode.asText();
        } catch (Exception e) {
            throw new RuntimeException("Ollama request failed: " + e.getMessage(), e);
        }
    }
}
