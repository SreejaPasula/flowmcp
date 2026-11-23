package io.flowmcp.rag.loader.reader;

import io.flowmcp.rag.loader.DocumentReader;
import io.flowmcp.rag.loader.DocumentType;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

/**
 * Reads plain text (.txt) files as UTF-8. Also, the fallback for files given directly
 * whose type has no dedicated reader.
 */
public class PlainTextReader implements DocumentReader {

    @Override
    public DocumentType supportedType() {
        return DocumentType.TXT;
    }

    @Override
    public String read(File file) throws IOException {
        return new String(Files.readAllBytes(file.toPath()), StandardCharsets.UTF_8);
    }
}
