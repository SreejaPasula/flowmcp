package io.flowmcp.llm;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

/**
 * Ollama LLM client — runs local models, no API key needed.
 */
public class OllamaClient implements LLMClient {

    private final String model;
    private final String baseUrl;
    private final HttpClient httpClient;

    public OllamaClient(String model) {
        this(model, "http://localhost:11434");
    }

    public OllamaClient(String model, String baseUrl) {
        this.model = model;
        this.baseUrl = baseUrl;
        this.httpClient = HttpClient.newHttpClient();
    }

    @Override
    public String complete(String prompt) {
        try {
            String body = String.format("{\"model\":\"%s\",\"prompt\":\"%s\",\"stream\":false}",
                model, prompt.replace("\"", "\\\"").replace("\n", "\\n"));

            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/generate"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            // Parse "response" field from JSON — contributors can replace with a proper JSON library
            String json = response.body();
            int start = json.indexOf("\"response\":\"") + 12;
            int end = json.indexOf("\"", start);
            return json.substring(start, end).replace("\\n", "\n");
        } catch (Exception e) {
            throw new RuntimeException("Ollama request failed: " + e.getMessage(), e);
        }
    }
}
