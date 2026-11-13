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

public class AnthropicClientTest {

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteParsesResponse() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);

        String anthropicResponse = "{"
            + "\"id\":\"msg_123\","
            + "\"type\":\"message\","
            + "\"role\":\"assistant\","
            + "\"content\":[{\"type\":\"text\",\"text\":\"Claude response answer\"}],"
            + "\"model\":\"claude-3-5-sonnet-20241022\","
            + "\"stop_reason\":\"end_turn\""
            + "}";

        when(mockResponse.body()).thenReturn(anthropicResponse);
        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        AnthropicClient client = new AnthropicClient("claude-3-5-sonnet-20241022", "test-key-123", "https://api.anthropic.com/v1", 1024, mockHttpClient, new ObjectMapper());
        String result = client.complete("Hello Claude");

        assertEquals("Claude response answer", result);
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteBuildsValidRequestHeadersAndPayload() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);
        when(mockResponse.body()).thenReturn("{\"content\":[{\"type\":\"text\",\"text\":\"ok\"}]}");

        ArgumentCaptor<HttpRequest> captor = ArgumentCaptor.forClass(HttpRequest.class);
        when(mockHttpClient.send(captor.capture(), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        AnthropicClient client = new AnthropicClient("claude-3-5-sonnet-20241022", "sk-ant-test123", "https://api.anthropic.com/v1", 1024, mockHttpClient, new ObjectMapper());
        client.complete("Test prompt");

        HttpRequest req = captor.getValue();
        assertEquals("https://api.anthropic.com/v1/messages", req.uri().toString());
        assertEquals("POST", req.method());
        assertEquals("sk-ant-test123", req.headers().firstValue("x-api-key").orElse(""));
        assertEquals("2023-06-01", req.headers().firstValue("anthropic-version").orElse(""));
        assertEquals("application/json", req.headers().firstValue("Content-Type").orElse(""));
    }

    @Test
    public void testMissingApiKeyThrowsIllegalStateException() {
        AnthropicClient client = new AnthropicClient("claude-3-5-sonnet-20241022", null, "https://api.anthropic.com/v1", 1024, mock(HttpClient.class), new ObjectMapper());
        Exception exception = assertThrows(IllegalStateException.class, () -> client.complete("Hello"));
        assertTrue(exception.getMessage().contains("ANTHROPIC_API_KEY"));
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testCompleteHandlesHttpError() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(401);
        when(mockResponse.body()).thenReturn("{\"type\":\"error\",\"error\":{\"type\":\"authentication_error\",\"message\":\"invalid x-api-key\"}}");

        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        AnthropicClient client = new AnthropicClient("claude-3-5-sonnet-20241022", "bad-key", "https://api.anthropic.com/v1", 1024, mockHttpClient, new ObjectMapper());
        assertThrows(RuntimeException.class, () -> client.complete("Hello"));
    }

    @Test
    public void testFactoryFromStringCreatesAnthropicClient() {
        LLMClient client = LLMClient.fromString("anthropic/claude-3-5-sonnet-20241022");
        assertInstanceOf(AnthropicClient.class, client);
    }

    @Test
    public void testNullModelThrowsIllegalArgumentException() {
        AnthropicClient client = new AnthropicClient(null, "key", "https://api.anthropic.com/v1", 1024, mock(HttpClient.class), new ObjectMapper());
        assertThrows(IllegalArgumentException.class, () -> client.complete("test"));
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testNullPromptHandledAsEmptyString() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);
        when(mockResponse.body()).thenReturn("{\"content\":[{\"type\":\"text\",\"text\":\"ok\"}]}");

        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        AnthropicClient client = new AnthropicClient("claude-3-5-sonnet-20241022", "test-key", "https://api.anthropic.com/v1", 1024, mockHttpClient, new ObjectMapper());
        assertDoesNotThrow(() -> client.complete(null));
    }

    @Test
    @SuppressWarnings("unchecked")
    public void testMissingContentThrowsRuntimeException() throws IOException, InterruptedException {
        HttpClient mockHttpClient = mock(HttpClient.class);
        HttpResponse<String> mockResponse = mock(HttpResponse.class);
        when(mockResponse.statusCode()).thenReturn(200);
        when(mockResponse.body()).thenReturn("{\"id\":\"msg_1\"}");

        when(mockHttpClient.send(any(HttpRequest.class), any(HttpResponse.BodyHandler.class)))
            .thenReturn(mockResponse);

        AnthropicClient client = new AnthropicClient("claude-3-5-sonnet-20241022", "test-key", "https://api.anthropic.com/v1", 1024, mockHttpClient, new ObjectMapper());
        assertThrows(RuntimeException.class, () -> client.complete("Hello"));
    }
}
