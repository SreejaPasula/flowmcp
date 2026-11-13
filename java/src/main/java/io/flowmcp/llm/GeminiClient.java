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
 * Google Gemini LLM client using HTTP client and Jackson JSON parser.
 */
public class GeminiClient implements LLMClient {

    private static final String DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta";

    private final String model;
    private final String apiKey;
    private final String baseUrl;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    public GeminiClient(String model) {
        this(model, resolveApiKey(), DEFAULT_BASE_URL, HttpClient.newHttpClient(), new ObjectMapper());
    }

    public GeminiClient(String model, String apiKey) {
        this(model, apiKey, DEFAULT_BASE_URL, HttpClient.newHttpClient(), new ObjectMapper());
    }

    public GeminiClient(String model, String apiKey, String baseUrl, HttpClient httpClient, ObjectMapper objectMapper) {
        this.model = model;
        this.apiKey = apiKey;
        this.baseUrl = (baseUrl != null && !baseUrl.isBlank()) ? baseUrl : DEFAULT_BASE_URL;
        this.httpClient = httpClient != null ? httpClient : HttpClient.newHttpClient();
        this.objectMapper = objectMapper != null ? objectMapper : new ObjectMapper();
    }

    private static String resolveApiKey() {
        String key = System.getenv("GEMINI_API_KEY");
        if (key == null || key.isBlank()) {
            key = System.getenv("GOOGLE_API_KEY");
        }
        return key;
    }

    @Override
    public String complete(String prompt) {
        if (apiKey == null || apiKey.isBlank()) {
            throw new IllegalStateException("Neither GEMINI_API_KEY nor GOOGLE_API_KEY environment variable is set.");
        }
        if (model == null || model.isBlank()) {
            throw new IllegalArgumentException("Model cannot be null or empty.");
        }

        try {
            String safePrompt = prompt != null ? prompt : "";
            String body = objectMapper.writeValueAsString(Map.of(
                "contents", List.of(
                    Map.of("parts", List.of(Map.of("text", safePrompt)))
                )
            ));

            String uri = baseUrl + "/models/" + model + ":generateContent?key=" + apiKey;
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(uri))
                .header("Content-Type", "application/json")
                .header("x-goog-api-key", apiKey)
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                throw new RuntimeException("Gemini API returned HTTP " + response.statusCode() + ": " + response.body());
            }

            JsonNode root = objectMapper.readTree(response.body());
            JsonNode candidates = root.get("candidates");
            if (candidates == null || candidates.isEmpty()) {
                throw new RuntimeException("Missing 'candidates' in Gemini response: " + response.body());
            }
            JsonNode parts = candidates.get(0).path("content").path("parts");
            if (parts == null || parts.isEmpty()) {
                throw new RuntimeException("Missing 'parts' in Gemini response: " + response.body());
            }
            return parts.get(0).path("text").asText();
        } catch (Exception e) {
            throw new RuntimeException("Gemini request failed: " + e.getMessage(), e);
        }
    }
}
