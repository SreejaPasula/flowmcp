package io.flowmcp.llm;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

public class OllamaClientTest {

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteParsesComplexResponse() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);

        // A complex JSON response from Ollama containing quotes, newlines, and code blocks
        String complexOllamaJson = "{"
            + "\"model\":\"llama3\","
            + "\"created_at\":\"2026-11-14T00:00:00Z\","
            + "\"response\":\"Here is the code:\\n```json\\n{\\\"key\\\": \\\"value\\\"}\\n```\\nHe said: \\\"Done!\\\"\","
            + "\"done\":true"
            + "}";

        when(mockResponse.body()).thenReturn(complexOllamaJson);
        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        OllamaClient client = new OllamaClient("llama3", "http://localhost:11434", mockHttpClient, new ObjectMapper());
        String result = client.complete("Generate json example");

        String expected = "Here is the code:\n```json\n{\"key\": \"value\"}\n```\nHe said: \"Done!\"";
        assertEquals(expected, result);
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteBuildsValidJsonPayload() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);
        when(mockResponse.body()).thenReturn("{\"response\":\"ok\"}");

        ArgumentCaptor<HttpRequest> requestCaptor = ArgumentCaptor.forClass(HttpRequest.class);
        when(mockHttpClient.send(requestCaptor.capture(), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        OllamaClient client = new OllamaClient("llama3", "http://localhost:11434", mockHttpClient, new ObjectMapper());
        String result = client.complete("Quotes: \"hello\" and newlines:\nworld");

        assertEquals("ok", result);
        HttpRequest captured = requestCaptor.getValue();
        assertEquals("http://localhost:11434/api/generate", captured.uri().toString());
        assertEquals("POST", captured.method());
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteThrowsOnHttpError() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(500);
        when(mockResponse.body()).thenReturn("{\"error\":\"model not found\"}");

        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        OllamaClient client = new OllamaClient("llama3", "http://localhost:11434", mockHttpClient, new ObjectMapper());
        assertThrows(RuntimeException.class, () -> client.complete("test"));
    }
}
