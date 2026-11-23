package io.flowmcp.rag.loader.reader;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class MarkdownReaderTest {

    @Test
    void readsFileContentVerbatim(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("README.md");
        Files.writeString(file, "# Title\n\nSome **markdown** content.");

        String content = new MarkdownReader().read(file.toFile());

        assertEquals("# Title\n\nSome **markdown** content.", content);
    }
}
