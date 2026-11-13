package io.flowmcp.rag;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Chunker {

    public static List<String> chunk(String text, int chunkSize, int overlap) {
        String[] words = text.split("\\s+");
        List<String> chunks = new ArrayList<>();
        int i = 0;
        while (i < words.length) {
            int end = Math.min(i + chunkSize, words.length);
            String chunk = String.join(" ", Arrays.copyOfRange(words, i, end));
            if (!chunk.isBlank()) chunks.add(chunk);
            i += chunkSize - overlap;
        }
        return chunks;
    }

    public static List<String> chunk(String text) {
        return chunk(text, 500, 50);
    }
}
