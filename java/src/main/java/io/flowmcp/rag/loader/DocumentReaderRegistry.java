package io.flowmcp.rag.loader;

import java.io.File;
import java.util.List;
import java.util.Optional;

/**
 * Picks the first registered {@link DocumentReader} that supports a given file.
 */
public class DocumentReaderRegistry {
    private final List<DocumentReader> readers;

    public DocumentReaderRegistry(List<DocumentReader> readers) {
        this.readers = List.copyOf(readers);
    }

    public Optional<DocumentReader> getReader(File file) {
        return readers.stream()
            .filter(reader -> reader.supports(file))
            .findFirst();
    }
}
