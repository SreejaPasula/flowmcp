package io.flowmcp.rag.loader.reader;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

public class PDFReaderTest {

    @Test
    void extractsTextFromPdf(@TempDir Path tempDir) throws Exception {
        File pdfFile = tempDir.resolve("doc.pdf").toFile();
        TestPdfs.write(pdfFile, "Hello from PDF");

        String content = new PDFReader().read(pdfFile);

        assertTrue(content.contains("Hello from PDF"));
    }

    @Test
    void throwsIOExceptionForEncryptedPdf(@TempDir Path tempDir) throws Exception {
        File pdfFile = tempDir.resolve("secret.pdf").toFile();
        TestPdfs.write(pdfFile, "Secret content", "owner-pass");

        IOException exception = assertThrows(IOException.class, () -> new PDFReader().read(pdfFile));
        assertTrue(exception.getMessage().contains("encrypted"));
    }

    @Test
    void propagatesIOExceptionForUnreadablePdf(@TempDir Path tempDir) throws IOException {
        File fakePdf = tempDir.resolve("broken.pdf").toFile();
        Files.writeString(fakePdf.toPath(), "this is not a real pdf");

        assertThrows(IOException.class, () -> new PDFReader().read(fakePdf));
    }
}
