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

public class GeminiClientTest {

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteParsesResponse() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);

        String geminiResponse = "{"
            + "\"candidates\":[{"
            + "  \"content\":{"
            + "    \"parts\":[{\"text\":\"Gemini generated answer\"}],"
            + "    \"role\":\"model\""
            + "  },"
            + "  \"finishReason\":\"STOP\""
            + "}]"
            + "}";

        when(mockResponse.body()).thenReturn(geminiResponse);
        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        GeminiClient client = new GeminiClient("gemini-1.5-flash", "test-key-123", "https://generativelanguage.googleapis.com/v1beta", mockHttpClient, new ObjectMapper());
        String result = client.complete("Hello Gemini");

        assertEquals("Gemini generated answer", result);
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteBuildsValidRequestHeadersAndPayload() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);
        when(mockResponse.body()).thenReturn("{\"candidates\":[{\"content\":{\"parts\":[{\"text\":\"ok\"}]}}]}");

        ArgumentCaptor<HttpRequest> captor = ArgumentCaptor.forClass(HttpRequest.class);
        when(mockHttpClient.send(captor.capture(), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        GeminiClient client = new GeminiClient("gemini-1.5-flash", "test-key-xyz", "https://generativelanguage.googleapis.com/v1beta", mockHttpClient, new ObjectMapper());
        client.complete("Test prompt");

        HttpRequest req = captor.getValue();
        assertEquals("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=test-key-xyz", req.uri().toString());
        assertEquals("POST", req.method());
        assertEquals("test-key-xyz", req.headers().firstValue("x-goog-api-key").orElse(""));
        assertEquals("application/json", req.headers().firstValue("Content-Type").orElse(""));
    }

    @Test
    public void testMissingApiKeyThrowsIllegalStateException() {
        GeminiClient client = new GeminiClient("gemini-1.5-flash", null, "https://generativelanguage.googleapis.com/v1beta", mock(HttpClient.class), new ObjectMapper());
        Exception exception = assertThrows(IllegalStateException.class, () -> client.complete("Hello"));
        assertTrue(exception.getMessage().contains("GEMINI_API_KEY"));
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteHandlesHttpError() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(400);
        when(mockResponse.body()).thenReturn("{\"error\":{\"message\":\"API key not valid\"}}");

        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        GeminiClient client = new GeminiClient("gemini-1.5-flash", "bad-key", "https://generativelanguage.googleapis.com/v1beta", mockHttpClient, new ObjectMapper());
        assertThrows(RuntimeException.class, () -> client.complete("Hello"));
    }

    @Test
    public void testFactoryFromStringCreatesGeminiClient() {
        LLMClient client = LLMClient.fromString("gemini/gemini-1.5-flash");
        assertInstanceOf(GeminiClient.class, client);
    }

    @Test
    public void testNullModelThrowsIllegalArgumentException() {
        GeminiClient client = new GeminiClient(null, "key", "https://generativelanguage.googleapis.com/v1beta", mock(HttpClient.class), new ObjectMapper());
        assertThrows(IllegalArgumentException.class, () -> client.complete("test"));
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testNullPromptHandledAsEmptyString() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);
        when(mockResponse.body()).thenReturn("{\"candidates\":[{\"content\":{\"parts\":[{\"text\":\"ok\"}]}}]}");

        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        GeminiClient client = new GeminiClient("gemini-1.5-flash", "test-key", "https://generativelanguage.googleapis.com/v1beta", mockHttpClient, new ObjectMapper());
        assertDoesNotThrow(() -> client.complete(null));
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testMissingCandidatesThrowsRuntimeException() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);
        when(mockResponse.body()).thenReturn("{\"candidates\":[]}");

        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        GeminiClient client = new GeminiClient("gemini-1.5-flash", "test-key", "https://generativelanguage.googleapis.com/v1beta", mockHttpClient, new ObjectMapper());
        assertThrows(RuntimeException.class, () -> client.complete("Hello"));
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testMissingPartsThrowsRuntimeException() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);
        when(mockResponse.body()).thenReturn("{\"candidates\":[{\"content\":{\"parts\":[]}}]}");

        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        GeminiClient client = new GeminiClient("gemini-1.5-flash", "test-key", "https://generativelanguage.googleapis.com/v1beta", mockHttpClient, new ObjectMapper());
        assertThrows(RuntimeException.class, () -> client.complete("Hello"));
    }
}
