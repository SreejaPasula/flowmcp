package io.flowmcp.rag.loader;

import io.flowmcp.rag.loader.reader.MarkdownReader;
import io.flowmcp.rag.loader.reader.PDFReader;
import io.flowmcp.rag.loader.reader.PlainTextReader;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Turns a source (a file, a directory, or raw text) into a list of document texts.
 */
public class DocumentLoader {
    private final DocumentReaderRegistry readerRegistry;
    private final PlainTextReader plainTextReader;

    public DocumentLoader() {
        this.plainTextReader = new PlainTextReader();
        this.readerRegistry = new DocumentReaderRegistry(List.of(
            plainTextReader, new MarkdownReader(), new PDFReader()
        ));
    }

    public List<String> load(String source) throws IOException {
        File file = new File(source);

        if (file.isDirectory()) {
            return loadDirectory(file);
        }

        if (file.isFile()) {
            return List.of(loadDocument(file));
        }

        return List.of(source);
    }

    private List<String> loadDirectory(File dir) {
        File[] files = dir.listFiles();
        if (files == null) return Collections.emptyList();
        Arrays.sort(files);

        List<String> documents = new ArrayList<>();
        for (File file : files) {
            if (!isSupportedDocument(file)) continue;

            try {
                documents.add(loadDocument(file));
            } catch (IOException e) {
                System.err.println("[flowmcp] Warning: Could not load file " + file.getName() + ": " + e.getMessage());
            }
        }
        return documents;
    }

    private boolean isSupportedDocument(File file) {
        return file.isFile() && readerRegistry.getReader(file).isPresent();
    }

    private String loadDocument(File file) throws IOException {
        DocumentReader reader = readerRegistry.getReader(file).orElse(plainTextReader);
        return reader.read(file);
    }
}
