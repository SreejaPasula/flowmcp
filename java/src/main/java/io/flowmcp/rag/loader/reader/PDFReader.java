package io.flowmcp.rag.loader.reader;

import io.flowmcp.rag.loader.DocumentReader;
import io.flowmcp.rag.loader.DocumentType;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;

import java.io.File;
import java.io.IOException;

/**
 * Extracts text from PDF files using Apache PDFBox.
 */
public class PDFReader implements DocumentReader {
    @Override
    public DocumentType supportedType() {
        return DocumentType.PDF;
    }

    @Override
    public String read(File file) throws IOException {
        try (PDDocument document = Loader.loadPDF(file)) {
            if (document.isEncrypted()) {
                throw new IOException("PDF is encrypted; unlock or supply password before extracting.");
            }

            PDFTextStripper stripper = new PDFTextStripper();
            stripper.setSortByPosition(true);

            String rawText = stripper.getText(document);
            return normalizeText(rawText);
        } catch (RuntimeException e) {
            throw new IOException("Failed to parse PDF " + file.getName() + ": " + e.getMessage(), e);
        }
    }

    private static String normalizeText(String text) {
        if (text == null) return "";
        return text
            .replace("\r\n", "\n")
            .replace('\r', '\n')
            .replaceAll("\n{3,}", "\n\n")
            .replaceAll("[ \t]{2,}", " ")
            .trim();
    }
}
