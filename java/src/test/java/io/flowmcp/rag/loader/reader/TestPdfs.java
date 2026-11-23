package io.flowmcp.rag.loader.reader;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.encryption.AccessPermission;
import org.apache.pdfbox.pdmodel.encryption.StandardProtectionPolicy;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.apache.pdfbox.pdmodel.font.Standard14Fonts;

import java.io.File;
import java.io.IOException;

/**
 * Builds small single-page PDFs for tests.
 */
public final class TestPdfs {

    private TestPdfs() {
    }

    public static void write(File file, String text) throws IOException {
        write(file, text, null);
    }

    public static void write(File file, String text, String ownerPassword) throws IOException {
        try (PDDocument document = new PDDocument()) {
            PDPage page = new PDPage();
            document.addPage(page);

            try (PDPageContentStream stream = new PDPageContentStream(document, page)) {
                stream.beginText();
                stream.setFont(new PDType1Font(Standard14Fonts.FontName.HELVETICA), 12);
                stream.newLineAtOffset(50, 700);
                stream.showText(text);
                stream.endText();
            }

            if (ownerPassword != null) {
                AccessPermission permission = new AccessPermission();
                StandardProtectionPolicy policy = new StandardProtectionPolicy(ownerPassword, "", permission);
                policy.setEncryptionKeyLength(128);
                document.protect(policy);
            }

            document.save(file);
        }
    }
}
