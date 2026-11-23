package io.flowmcp.rag.loader;

import java.io.File;
import java.util.Locale;

/**
 * Document types the RAG loader has a dedicated reader for, matched by file extension.
 */
public enum DocumentType {

    PDF("pdf", "application/pdf"),
    TXT("txt", "text/plain"),
    MARKDOWN("md", "text/markdown");

    private final String extension;
    private final String mimeType;

    DocumentType(String extension, String mimeType) {
        this.extension = extension;
        this.mimeType = mimeType;
    }

    public String getExtension() {
        return extension;
    }

    public String getMimeType() {
        return mimeType;
    }

    public boolean matches(File file) {
        return file.getName()
                .toLowerCase(Locale.ROOT)
                .endsWith("." + extension);
    }
}
