package io.flowmcp.rag.loader;

import io.flowmcp.rag.loader.reader.MarkdownReader;
import io.flowmcp.rag.loader.reader.PDFReader;
import io.flowmcp.rag.loader.reader.PlainTextReader;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

public class DocumentReaderRegistryTest {

    private final DocumentReaderRegistry registry = new DocumentReaderRegistry(
        List.of(new PlainTextReader(), new MarkdownReader(), new PDFReader())
    );

    @Test
    void resolvesPlainTextReaderForTxtFile() {
        Optional<DocumentReader> reader = registry.getReader(new File("notes.txt"));

        assertTrue(reader.isPresent());
        assertInstanceOf(PlainTextReader.class, reader.get());
    }

    @Test
    void resolvesMarkdownReaderForMdFile() {
        Optional<DocumentReader> reader = registry.getReader(new File("README.md"));

        assertTrue(reader.isPresent());
        assertInstanceOf(MarkdownReader.class, reader.get());
    }

    @Test
    void resolvesPdfReaderForPdfFileRegardlessOfCase() {
        Optional<DocumentReader> reader = registry.getReader(new File("report.PDF"));

        assertTrue(reader.isPresent());
        assertInstanceOf(PDFReader.class, reader.get());
    }

    @Test
    void returnsEmptyForUnsupportedExtension() {
        Optional<DocumentReader> reader = registry.getReader(new File("image.png"));

        assertTrue(reader.isEmpty());
    }
}
