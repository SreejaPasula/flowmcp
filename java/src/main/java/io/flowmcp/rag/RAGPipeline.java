package io.flowmcp.rag;

import io.flowmcp.rag.loader.DocumentLoader;

import java.io.IOException;
import java.util.List;

/**
 * RAG pipeline — loads documents, chunks them, retrieves relevant ones.
 * Contributors: enhance the retriever with vector embeddings for better results.
 */
public class RAGPipeline {

    private final Retriever retriever;
    private final DocumentLoader documentLoader;

    public RAGPipeline(List<String> sources) {
        this.retriever = new Retriever();
        this.documentLoader = new DocumentLoader();
        for (String source : sources) {
            ingest(source);
        }
    }

    private void ingest(String source) {
        List<String> documents;
        try {
            documents = documentLoader.load(source);
        } catch (IOException e) {
            System.err.println("[flowmcp] Warning: Could not load source " + source + ": " + e.getMessage());
            return;
        }

        for (String document : documents) {
            retriever.add(Chunker.chunk(document));
        }
    }

    public List<String> retrieve(String query) {
        return retriever.search(query, 3);
    }
}
