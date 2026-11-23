package io.flowmcp.rag.loader.reader;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class PlainTextReaderTest {

    @Test
    void readsFileContentVerbatim(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("notes.txt");
        Files.writeString(file, "hello world");

        String content = new PlainTextReader().read(file.toFile());

        assertEquals("hello world", content);
    }

    @Test
    void supportsOnlyTxtExtension() {
        PlainTextReader reader = new PlainTextReader();

        assertTrue(reader.supports(new File("notes.txt")));
        assertFalse(reader.supports(new File("notes.md")));
    }
}
