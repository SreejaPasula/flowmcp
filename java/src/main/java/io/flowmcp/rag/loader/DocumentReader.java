package io.flowmcp.rag.loader;

import java.io.File;
import java.io.IOException;

/**
 * Reads one document type into plain text.
 */
public interface DocumentReader {
    DocumentType supportedType();
    String read(File file) throws IOException;

    default boolean supports(File file) {
        return supportedType().matches(file);
    }
}
