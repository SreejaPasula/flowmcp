package io.flowmcp.rag.loader;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class DocumentLoaderTest {

    private final DocumentLoader loader = new DocumentLoader();

    @Test
    void loadsSingleTextFile(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("notes.txt");
        Files.writeString(file, "hello world");

        List<String> documents = loader.load(file.toString());

        assertEquals(List.of("hello world"), documents);
    }

    @Test
    void readsDirectlyGivenFileOfUnknownTypeAsPlainText(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("data.csv");
        Files.writeString(file, "name,age\nada,36");

        List<String> documents = loader.load(file.toString());

        assertEquals(List.of("name,age\nada,36"), documents);
    }

    @Test
    void treatsNonExistentPathAsRawText() throws IOException {
        List<String> documents = loader.load("just some raw text, not a path");

        assertEquals(List.of("just some raw text, not a path"), documents);
    }

    @Test
    void loadDirectorySkipsUnsupportedFileButKeepsOthers(@TempDir Path tempDir) throws IOException {
        Files.writeString(tempDir.resolve("notes.txt"), "good text content");
        Files.writeString(tempDir.resolve("image.png"), "not a real image, just bytes");

        List<String> documents = loader.load(tempDir.toString());

        assertEquals(List.of("good text content"), documents);
    }

    @Test
    void loadDirectorySkipsUnreadableFileButKeepsOthers(@TempDir Path tempDir) throws IOException {
        Files.writeString(tempDir.resolve("notes.txt"), "good text content");
        Files.writeString(tempDir.resolve("broken.pdf"), "not a real pdf");

        List<String> documents = loader.load(tempDir.toString());

        assertEquals(List.of("good text content"), documents);
    }

    @Test
    void loadDirectorySilentlySkipsSubdirectoriesAndUnsupportedFiles(@TempDir Path tempDir) throws IOException {
        Files.writeString(tempDir.resolve("notes.txt"), "good text content");
        Files.writeString(tempDir.resolve(".DS_Store"), "finder metadata");
        Path subdirectory = Files.createDirectory(tempDir.resolve("nested"));
        Files.writeString(subdirectory.resolve("inner.txt"), "not loaded, directories are not walked");

        ByteArrayOutputStream stderr = new ByteArrayOutputStream();
        PrintStream originalErr = System.err;
        System.setErr(new PrintStream(stderr, true, StandardCharsets.UTF_8));
        List<String> documents;
        try {
            documents = loader.load(tempDir.toString());
        } finally {
            System.setErr(originalErr);
        }

        assertEquals(List.of("good text content"), documents);
        assertEquals("", stderr.toString(StandardCharsets.UTF_8));
    }

    @Test
    void loadDirectoryReturnsDocumentsInFileNameOrder(@TempDir Path tempDir) throws IOException {
        Files.writeString(tempDir.resolve("b.txt"), "second");
        Files.writeString(tempDir.resolve("a.md"), "first");
        Files.writeString(tempDir.resolve("c.txt"), "third");

        List<String> documents = loader.load(tempDir.toString());

        assertEquals(List.of("first", "second", "third"), documents);
    }
}
