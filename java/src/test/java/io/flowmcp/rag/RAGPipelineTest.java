package io.flowmcp.rag;

import io.flowmcp.rag.loader.reader.TestPdfs;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertTrue;

public class RAGPipelineTest {

    @Test
    void ingestsEveryDirectlyGivenFileIncludingUnknownTypes(@TempDir Path tempDir) throws IOException {
        Path textFile = tempDir.resolve("notes.txt");
        Files.writeString(textFile, "the quick brown fox jumps over the lazy dog");

        Path csvFile = tempDir.resolve("animals.csv");
        Files.writeString(csvFile, "zebra,giraffe");

        RAGPipeline pipeline = new RAGPipeline(List.of(textFile.toString(), csvFile.toString()));

        assertTrue(pipeline.retrieve("fox").stream().anyMatch(chunk -> chunk.contains("fox")));
        assertTrue(pipeline.retrieve("zebra").stream().anyMatch(chunk -> chunk.contains("zebra")));
    }

    @Test
    void skipsBadFileWithinDirectoryWithoutLosingSiblingFiles(@TempDir Path tempDir) throws IOException {
        Path dirA = tempDir.resolve("dirA");
        Files.createDirectory(dirA);
        Files.writeString(dirA.resolve("notes.txt"), "alpha content about cats");
        Files.writeString(dirA.resolve("broken.pdf"), "not a real pdf");

        Path dirB = tempDir.resolve("dirB");
        Files.createDirectory(dirB);
        Files.writeString(dirB.resolve("more.txt"), "beta content about dogs");

        RAGPipeline pipeline = new RAGPipeline(List.of(dirA.toString(), dirB.toString()));

        assertTrue(pipeline.retrieve("cats").stream().anyMatch(chunk -> chunk.contains("cats")));
        assertTrue(pipeline.retrieve("dogs").stream().anyMatch(chunk -> chunk.contains("dogs")));
    }

    @Test
    void retrievesTextFromPdfInDirectory(@TempDir Path tempDir) throws IOException {
        TestPdfs.write(tempDir.resolve("report.pdf").toFile(), "quarterly pelican migration report");
        Files.writeString(tempDir.resolve("notes.txt"), "unrelated notes about cats");

        RAGPipeline pipeline = new RAGPipeline(List.of(tempDir.toString()));

        assertTrue(pipeline.retrieve("pelican").stream().anyMatch(chunk -> chunk.contains("pelican migration")));
    }
}
