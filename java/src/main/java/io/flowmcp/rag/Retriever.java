package io.flowmcp.rag;

import java.util.*;
import java.util.stream.Collectors;

public class Retriever {

    private final List<String> chunks = new ArrayList<>();

    public void add(List<String> newChunks) {
        chunks.addAll(newChunks);
    }

    public List<String> search(String query, int topK) {
        if (chunks.isEmpty()) return Collections.emptyList();

        Set<String> queryTerms = Arrays.stream(query.toLowerCase().split("\\s+"))
            .collect(Collectors.toSet());

        return chunks.stream()
            .map(chunk -> {
                long score = queryTerms.stream()
                    .filter(term -> chunk.toLowerCase().contains(term))
                    .count();
                return Map.entry(score, chunk);
            })
            .filter(e -> e.getKey() > 0)
            .sorted((a, b) -> Long.compare(b.getKey(), a.getKey()))
            .limit(topK)
            .map(Map.Entry::getValue)
            .collect(Collectors.toList());
    }
}
