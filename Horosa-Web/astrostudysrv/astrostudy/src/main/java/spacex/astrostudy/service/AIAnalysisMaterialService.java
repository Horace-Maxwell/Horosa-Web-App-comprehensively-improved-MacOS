package spacex.astrostudy.service;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Map;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.poi.hwpf.HWPFDocument;
import org.apache.poi.hwpf.extractor.WordExtractor;
import org.apache.poi.xwpf.extractor.XWPFWordExtractor;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.springframework.stereotype.Service;

import boundless.exception.ErrorCodeException;
import boundless.io.FileUtility;
import boundless.utility.StringUtility;

@Service
public class AIAnalysisMaterialService {

	public Map<String, Object> extract(Map<String, Object> params){
		String fileName = stringVal(params, "fileName");
		String mimeType = stringVal(params, "mimeType");
		String base64Data = stringVal(params, "base64Data");
		if(StringUtility.isNullOrEmpty(base64Data)) {
			throw new ErrorCodeException(580101, "缺少 base64Data");
		}
		byte[] bytes = Base64.getDecoder().decode(base64Data);
		String ext = lowerExt(fileName);
		if(StringUtility.isNullOrEmpty(mimeType)) {
			try{
				mimeType = FileUtility.getContentType(bytes);
			}catch(Exception e){
				mimeType = "";
			}
		}
		Map<String, Object> result = new LinkedHashMap<String, Object>();
		result.put("fileName", fileName);
		result.put("fileExt", ext);
		result.put("mimeType", mimeType);
		result.put("size", bytes.length);
		result.put("fileHash", sha256(bytes));
		String extractedText;
		Map<String, Object> extractMeta = new LinkedHashMap<String, Object>();
		try{
			if(".pdf".equals(ext) || mimeType.contains("pdf")) {
				PdfExtract pdfExtract = extractPdf(bytes);
				extractedText = pdfExtract.text;
				extractMeta.put("pageCount", pdfExtract.pageCount);
				extractMeta.put("extractor", "pdfbox");
			}else if(".docx".equals(ext)) {
				DocExtract docxExtract = extractDocx(bytes);
				extractedText = docxExtract.text;
				extractMeta.put("paragraphCount", docxExtract.paragraphCount);
				extractMeta.put("extractor", "poi-xwpf");
			}else if(".doc".equals(ext)) {
				DocExtract docExtract = extractDoc(bytes);
				extractedText = docExtract.text;
				extractMeta.put("paragraphCount", docExtract.paragraphCount);
				extractMeta.put("extractor", "poi-hwpf");
			}else {
				extractedText = new String(bytes, StandardCharsets.UTF_8);
				extractMeta.put("extractor", "plain-text");
			}
		}catch(Exception e){
			throw new ErrorCodeException(580102, "资料抽取失败：" + e.getMessage());
		}
		extractedText = extractedText == null ? "" : extractedText.trim();
		result.put("extractedText", extractedText);
		result.put("textHash", sha256(extractedText.getBytes(StandardCharsets.UTF_8)));
		result.put("extractMeta", extractMeta);
		return result;
	}

	private PdfExtract extractPdf(byte[] bytes) throws IOException{
		try(PDDocument document = PDDocument.load(bytes)) {
			PDFTextStripper stripper = new PDFTextStripper();
			PdfExtract result = new PdfExtract();
			result.text = stripper.getText(document);
			result.pageCount = document.getNumberOfPages();
			return result;
		}
	}

	private DocExtract extractDocx(byte[] bytes) throws IOException{
		try(
			ByteArrayInputStream input = new ByteArrayInputStream(bytes);
			XWPFDocument document = new XWPFDocument(input);
			XWPFWordExtractor extractor = new XWPFWordExtractor(document)
		){
			DocExtract result = new DocExtract();
			result.text = extractor.getText();
			result.paragraphCount = document.getParagraphs().size();
			return result;
		}
	}

	private DocExtract extractDoc(byte[] bytes) throws IOException{
		try(
			ByteArrayInputStream input = new ByteArrayInputStream(bytes);
			HWPFDocument document = new HWPFDocument(input);
			WordExtractor extractor = new WordExtractor(document)
		){
			DocExtract result = new DocExtract();
			result.text = extractor.getText();
			result.paragraphCount = document.getRange() == null ? 0 : document.getRange().numParagraphs();
			return result;
		}
	}

	private String lowerExt(String fileName){
		String text = fileName == null ? "" : fileName.trim();
		int idx = text.lastIndexOf('.');
		if(idx < 0){
			return "";
		}
		return text.substring(idx).toLowerCase();
	}

	private String sha256(byte[] bytes){
		try{
			MessageDigest digest = MessageDigest.getInstance("SHA-256");
			byte[] hash = digest.digest(bytes);
			StringBuilder sb = new StringBuilder();
			for(byte item : hash) {
				sb.append(String.format("%02x", item));
			}
			return sb.toString();
		}catch(Exception e){
			throw new RuntimeException(e);
		}
	}

	private String stringVal(Map<String, Object> map, String key){
		Object val = map == null ? null : map.get(key);
		return val == null ? "" : String.valueOf(val).trim();
	}

	private static class PdfExtract {
		String text;
		int pageCount;
	}

	private static class DocExtract {
		String text;
		int paragraphCount;
	}
}
