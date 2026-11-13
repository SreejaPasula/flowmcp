package io.flowmcp.rag;

import java.util.List;

/**
 * RAG pipeline — loads documents, chunks them, retrieves relevant ones.
 * Contributors: enhance the retriever with vector embeddings for better results.
 */
public class RAGPipeline {

    private final Retriever retriever;

    public RAGPipeline(List<String> sources) {
        this.retriever = new Retriever();
        for (String source : sources) {
            load(source);
        }
    }

    private void load(String source) {
        java.io.File file = new java.io.File(source);
        if (file.isDirectory()) {
            loadDirectory(file);
        } else if (file.isFile()) {
            loadFile(file);
        } else {
            retriever.add(Chunker.chunk(source));
        }
    }

    private void loadDirectory(java.io.File dir) {
        java.io.File[] files = dir.listFiles();
        if (files == null) return;
        for (java.io.File file : files) {
            if (file.isFile() && (file.getName().endsWith(".txt") || file.getName().endsWith(".md"))) {
                loadFile(file);
            }
        }
    }

    private void loadFile(java.io.File file) {
        try {
            String content = new String(java.nio.file.Files.readAllBytes(file.toPath()));
            retriever.add(Chunker.chunk(content));
        } catch (Exception e) {
            System.err.println("[flowmcp] Warning: Could not load file " + file.getName() + ": " + e.getMessage());
        }
    }

    public List<String> retrieve(String query) {
        return retriever.search(query, 3);
    }
}
