package spacex.astrostudy.helper;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

import boundless.io.FileUtility;
import boundless.utility.ConvertUtility;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.DataFormatter;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.ss.usermodel.WorkbookFactory;

public class QiMengHelper {
	private static Map<Integer, String> yearGua = new HashMap<Integer, String>();
	
	static {
		try {
			byte[] raw = FileUtility.getBytesFromClassPath("qimeng/奇门年卦.xlsx");
			DataFormatter formatter = new DataFormatter();
			try(InputStream bins = new ByteArrayInputStream(raw);
				Workbook workbook = WorkbookFactory.create(bins)) {
				Sheet sheet = workbook.getSheet("qimeng");
				if(sheet == null && workbook.getNumberOfSheets() > 0) {
					sheet = workbook.getSheetAt(0);
				}
				if(sheet == null) {
					throw new IllegalStateException("qimeng sheet missing in 奇门年卦.xlsx");
				}
				for(int i=1; i<=sheet.getLastRowNum(); i++) {
					Row row = sheet.getRow(i);
					if(row == null) {
						continue;
					}
					Cell yearCell = row.getCell(0);
					Cell guaCell = row.getCell(1);
					if(yearCell == null || guaCell == null) {
						continue;
					}
					int year = ConvertUtility.getValueAsInt(formatter.formatCellValue(yearCell));
					String gua = formatter.formatCellValue(guaCell);
					if(year > 0 && gua != null && !gua.trim().isEmpty()) {
						yearGua.put(year, gua.trim());
					}
				}
			}
		}catch(Exception e) {
			throw new RuntimeException(e);
		}
	}
	
	public static String getGua(int year) {
		return yearGua.get(year);
	}
	
	public static void main(String[] args) {
		System.out.println(yearGua);
	}
}
