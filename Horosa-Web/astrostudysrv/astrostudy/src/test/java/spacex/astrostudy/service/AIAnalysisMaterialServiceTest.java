package spacex.astrostudy.service;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.io.ByteArrayOutputStream;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Map;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.junit.Test;

public class AIAnalysisMaterialServiceTest {

	@Test
	public void extractPlainTextKeepsMetadataAndHashes() {
		AIAnalysisMaterialService service = new AIAnalysisMaterialService();
		Map<String, Object> result = service.extract(buildParams("notes.txt", "text/plain", "这是一份测试资料"));
		assertEquals("notes.txt", result.get("fileName"));
		assertEquals(".txt", result.get("fileExt"));
		assertEquals("text/plain", result.get("mimeType"));
		assertEquals("这是一份测试资料", result.get("extractedText"));
		assertTrue(String.valueOf(result.get("fileHash")).length() > 10);
		assertTrue(String.valueOf(result.get("textHash")).length() > 10);
	}

	@Test
	public void extractDocxReadsParagraphs() throws Exception {
		AIAnalysisMaterialService service = new AIAnalysisMaterialService();
		ByteArrayOutputStream output = new ByteArrayOutputStream();
		try(XWPFDocument document = new XWPFDocument()) {
			XWPFParagraph paragraph = document.createParagraph();
			paragraph.createRun().setText("DOCX 测试正文");
			document.write(output);
		}
		Map<String, Object> params = new LinkedHashMap<String, Object>();
		params.put("fileName", "demo.docx");
		params.put("mimeType", "application/vnd.openxmlformats-officedocument.wordprocessingml.document");
		params.put("base64Data", Base64.getEncoder().encodeToString(output.toByteArray()));
		Map<String, Object> result = service.extract(params);
		assertEquals(".docx", result.get("fileExt"));
		assertTrue(String.valueOf(result.get("extractedText")).contains("DOCX 测试正文"));
		assertEquals("poi-xwpf", ((Map<String, Object>)result.get("extractMeta")).get("extractor"));
	}

	@Test
	public void extractPdfReadsPageText() throws Exception {
		AIAnalysisMaterialService service = new AIAnalysisMaterialService();
		ByteArrayOutputStream output = new ByteArrayOutputStream();
		try(PDDocument document = new PDDocument()) {
			PDPage page = new PDPage();
			document.addPage(page);
			try(PDPageContentStream stream = new PDPageContentStream(document, page)) {
				stream.beginText();
				stream.setFont(PDType1Font.HELVETICA, 12);
				stream.newLineAtOffset(50, 700);
				stream.showText("PDF TEST BODY");
				stream.endText();
			}
			document.save(output);
		}
		Map<String, Object> params = new LinkedHashMap<String, Object>();
		params.put("fileName", "demo.pdf");
		params.put("mimeType", "application/pdf");
		params.put("base64Data", Base64.getEncoder().encodeToString(output.toByteArray()));
		Map<String, Object> result = service.extract(params);
		assertEquals(".pdf", result.get("fileExt"));
		assertTrue(String.valueOf(result.get("extractedText")).contains("PDF TEST BODY"));
		assertEquals("pdfbox", ((Map<String, Object>)result.get("extractMeta")).get("extractor"));
	}

	private static Map<String, Object> buildParams(String fileName, String mimeType, String text){
		Map<String, Object> params = new LinkedHashMap<String, Object>();
		params.put("fileName", fileName);
		params.put("mimeType", mimeType);
		params.put("base64Data", Base64.getEncoder().encodeToString(text.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
		return params;
	}
}
