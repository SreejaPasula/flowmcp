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

public class OpenAIClientTest {

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteParsesResponse() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);

        String openAiResponse = "{"
            + "\"id\":\"chatcmpl-123\","
            + "\"choices\":[{"
            + "  \"index\":0,"
            + "  \"message\":{\"role\":\"assistant\",\"content\":\"OpenAI response answer\"},"
            + "  \"finish_reason\":\"stop\""
            + "}]"
            + "}";

        when(mockResponse.body()).thenReturn(openAiResponse);
        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        OpenAIClient client = new OpenAIClient("gpt-4", "test-key-123", "https://api.openai.com/v1", mockHttpClient, new ObjectMapper());
        String result = client.complete("Hello");

        assertEquals("OpenAI response answer", result);
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteBuildsValidRequestHeadersAndPayload() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);
        when(mockResponse.body()).thenReturn("{\"choices\":[{\"message\":{\"content\":\"ok\"}}]}");

        ArgumentCaptor<HttpRequest> captor = ArgumentCaptor.forClass(HttpRequest.class);
        when(mockHttpClient.send(captor.capture(), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        OpenAIClient client = new OpenAIClient("gpt-4o", "sk-secret123", "https://api.openai.com/v1", mockHttpClient, new ObjectMapper());
        client.complete("Test prompt");

        HttpRequest req = captor.getValue();
        assertEquals("https://api.openai.com/v1/chat/completions", req.uri().toString());
        assertEquals("POST", req.method());
        assertEquals("Bearer sk-secret123", req.headers().firstValue("Authorization").orElse(""));
        assertEquals("application/json", req.headers().firstValue("Content-Type").orElse(""));
    }

    @Test
    public void testMissingApiKeyThrowsIllegalStateException() {
        OpenAIClient client = new OpenAIClient("gpt-4", null, "https://api.openai.com/v1", mock(HttpClient.class), new ObjectMapper());
        Exception exception = assertThrows(IllegalStateException.class, () -> client.complete("Hello"));
        assertTrue(exception.getMessage().contains("OPENAI_API_KEY"));
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteHandlesHttpError() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(401);
        when(mockResponse.body()).thenReturn("{\"error\":{\"message\":\"Invalid API key\"}}");

        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        OpenAIClient client = new OpenAIClient("gpt-4", "bad-key", "https://api.openai.com/v1", mockHttpClient, new ObjectMapper());
        assertThrows(RuntimeException.class, () -> client.complete("Hello"));
    }

    @Test
    public void testFactoryFromStringCreatesOpenAIClient() {
        LLMClient client = LLMClient.fromString("openai/gpt-4o");
        assertInstanceOf(OpenAIClient.class, client);
    }

    @Test
    public void testNullModelThrowsIllegalArgumentException() {
        OpenAIClient client = new OpenAIClient(null, "key", "https://api.openai.com/v1", mock(HttpClient.class), new ObjectMapper());
        assertThrows(IllegalArgumentException.class, () -> client.complete("test"));
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testNullPromptHandledAsEmptyString() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);
        when(mockResponse.body()).thenReturn("{\"choices\":[{\"message\":{\"content\":\"ok\"}}]}");

        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        OpenAIClient client = new OpenAIClient("gpt-4", "test-key", "https://api.openai.com/v1", mockHttpClient, new ObjectMapper());
        assertDoesNotThrow(() -> client.complete(null));
    }
}
