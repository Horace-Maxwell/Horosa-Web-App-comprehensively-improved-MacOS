package xuan.utils;

import java.util.*;
import java.math.BigDecimal;

import com.nlf.calendar.Lunar;
import com.nlf.calendar.Solar;
import org.apache.commons.validator.routines.InetAddressValidator;
import org.omg.CORBA.SystemException;

/**
 * 通用工具
 *
 * @author 善待
 */
public class CommonUtil {

    /**
     * 占位符1（-）
     */
    public static final String EMPTY1 = "-";

    /**
     * 占位符2（--）
     */
    public static final String EMPTY2 = "--";

    /**
     * 数字转换汉字
     *
     * @param number 数字
     * @return 汉字（例如：一）
     */
    public static String shuToHan(long number) {

        final String[] unit = {"", "十", "百", "千", "万", "十", "百", "千", "亿", "十", "百", "千"};
        final String[] lowercaseNumber = {"零", "一", "二", "三", "四", "五", "六", "七", "八", "九"};

        int count = 0;
        StringBuilder sb = new StringBuilder();
        while (number > 0) {
            sb.insert(0, (lowercaseNumber[Math.toIntExact(number % 10)] + unit[count]));
            number = (number / 10);
            count++;
        }

        return sb.toString().replaceAll("零[千百十]", "零").replaceAll("零+万", "万")
                .replaceAll("零+亿", "亿").replaceAll("亿万", "亿零")
                .replaceAll("零+", "零").replaceAll("零$", "");

    }

    /**
     * 获取一个数的随机数
     *
     * @param range 范围（如→ 0:产生0，1:产生1~1中的随机一位数字，2:产生1~2中的随机一位数字，... ）
     * @return List随机数集合
     */
    public static Integer randomList(int range) {

        int nextInt = new Random().nextInt(range);
        return nextInt == 0 ? 1 : nextInt;

    }

    /**
     * 保留Double型数据的N位小数
     *
     * @param number double类型数据
     * @param count  保留小数的位数
     * @return double型数据
     */
    public static Double getDouble(double number, int count) {

        BigDecimal bigDec = new BigDecimal(number);
        return bigDec.setScale(count, BigDecimal.ROUND_FLOOR).doubleValue();

    }

    /**
     * 将N个数据封装为List集合
     *
     * @param parameter 数据
     * @return List集合
     */
    public static List<Integer> packageList(int... parameter) {

        List<Integer> list = new ArrayList<>();
        for (int i : parameter) {
            if (i < 0) i = 0;
            if (i > 3) i = 3;
            list.add(i);
        }
        return list;

    }

    /**
     * 获取指定个数的随机数
     *
     * @param count 数量
     * @param range 范围（如→ 0:产生0，1:产生0~1中的随机一位数字，2:产生0~2中的随机一位数字，... ）
     * @return List随机数集合
     */
    public static List<Integer> randomList(long count, int range) {

        List<Integer> list = new ArrayList<>();

        for (int i = 0; i < count; i++) {
            list.add(new Random().nextInt(range + 1));
        }

        return list;

    }

    /**
     * 删除list集合中的重复数据（包括NULL）
     *
     * @param list list集合
     * @return list数组
     */
    public static List<String> removeDuplicatesList(List<String> list) {

        list.removeIf(Objects::isNull);
        return new ArrayList<>(new LinkedHashSet<>(list));

    }

    /**
     * 向List集合中添加指定个数的字符串
     *
     * @param count 元素数量
     * @return 空list集合
     */
    public static List<String> addCharToList(int count, String text) {

        List<String> list = new ArrayList<>();
        for (int i = 0; i <= count - 1; i++) {
            list.add(text);
        }
        return list;

    }

    /**
     * 获取两个List数组中的不同元素
     *
     * @param list1 数组1
     * @param list2 数组2
     * @return 不同元素的数组
     */
    public static List<String> getListUnlike(List<String> list1, List<String> list2) {

        List<String> maxList = list1;
        List<String> minList = list2;
        if (list2.size() > list1.size()) {
            maxList = list2;
            minList = list1;
        }

        Map<String, Integer> map = new HashMap<>(list1.size() + list2.size());
        for (String string : maxList) {
            map.put(string, 1);
        }
        for (String string : minList) {
            Integer count = map.get(string);
            if (null != count) {
                map.put(string, ++count);
                continue;
            }
            map.put(string, 1);
        }

        List<String> unlike = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            if (entry.getValue() == 1) {
                unlike.add(entry.getKey());
            }
        }

        return unlike;

    }

    /**
     * 获取日期及四柱干支
     *
     * @param date            日期（格式：yyyy-MM-dd HH:mm:ss）
     * @param dateType        日期类型（0:公历。1:农历）
     * @param leapMonthType   闰月类型（0:不使用闰月。1:使用闰月）
     * @param yearGanZhiType  年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接时刻作为新年的开始）
     * @param monthGanZhiType 月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
     * @param dayGanZhiType   日干支类型（0:晚子时日柱按明天。1:晚子时日柱按当天）
     * @return 日期及四柱干支
     */
    public static Map<String, Object> getDateAndGanZhi(String date, int dateType, int leapMonthType, int yearGanZhiType, int monthGanZhiType, int dayGanZhiType) {

        Solar solar; // 公历日期（Solar型）
        Lunar lunar; // 农历日期（Lunar型）
        String solarStr; // 公历日期（String型）
        String lunarStr; // 农历日期（String型）
        String solarStr2; // 公历日期（String型）
        String lunarStr2; // 农历日期（String型）
        Date solarDate; // 公历日期（Date型）
        Date lunarDate; // 农历日期（Date型）

        // 1、获取年、月、日、时、分、秒
        Map<String, Integer> dateInfo = DateUtil.getDateInfo(date);
        int year = dateInfo.get("year"); // 年
        int month = dateInfo.get("month"); // 月
        int day = dateInfo.get("day"); // 日
        int hour = dateInfo.get("hour"); // 时
        int minute = dateInfo.get("minute"); // 分
        int second = dateInfo.get("second"); // 秒

        // 2、判断日期类型
        if (dateType == 0) {
            // 2.1、按公历日期计算
            solar = new Solar(year, month, day, hour, minute, second); // 公历日期（Solar型）
            lunar = solar.getLunar(); // 农历日期（Lunar型）
            solarStr = DateUtil.getSolarStr(solar); // 公历日期（String型）
            lunarStr = DateUtil.getLunarStr(lunar); // 农历日期（String型）
            solarStr2 = DateUtil.getSolarStr2(solar); // 公历日期（String型）
            lunarStr2 = DateUtil.getLunarStr2(lunar); // 农历日期（String型）
            solarDate = DateUtil.stringToDate(solarStr); // 公历日期（Date型）
            lunarDate = DateUtil.stringToDate(lunarStr); // 农历日期（Date型）
        } else {
            // 2.2、按农历日期计算
            try {
                lunar = new Lunar(year, (leapMonthType == 0 ? month : -month), day, hour, minute, second); // 农历日期（Lunar型）
                solar = lunar.getSolar(); // 公历日期（Solar型）
                solarStr = DateUtil.getSolarStr(solar); // 公历日期（String型）
                lunarStr = DateUtil.getLunarStr(lunar); // 农历日期（String型）
                solarStr2 = DateUtil.getSolarStr2(solar); // 公历日期（String型）
                lunarStr2 = DateUtil.getLunarStr2(lunar); // 农历日期（String型）
                solarDate = DateUtil.stringToDate(solarStr); // 公历日期（Date型）
                lunarDate = DateUtil.stringToDate(lunarStr); // 农历日期（Date型）
            } catch (IllegalArgumentException e) {
//                lunar = new Lunar(); // 农历日期（Lunar型）
//                solar = lunar.getSolar(); // 公历日期（Solar型）
//                solarStr = DateUtil.getSolarStr(solar); // 公历日期（String型）
//                lunarStr = DateUtil.getLunarStr(lunar); // 农历日期（String型）
//                solarStr2 = DateUtil.getSolarStr2(solar); // 公历日期（String型）
//                lunarStr2 = DateUtil.getLunarStr2(lunar); // 农历日期（String型）
//                solarDate = DateUtil.stringToDate(solarStr); // 公历日期（Date型）
//                lunarDate = DateUtil.stringToDate(lunarStr); // 农历日期（Date型）
                throw new IllegalArgumentException(e.getMessage());
            }
        }

        // 3、判断年干支类型
        String yearGanZhi; // 年干支
        if (yearGanZhiType == 0) {
            yearGanZhi = lunar.getYearInGanZhi(); // 以正月初一作为新年的开始
        } else if (yearGanZhiType == 1) {
            yearGanZhi = lunar.getYearInGanZhiByLiChun(); // 以立春当天作为新年的开始
        } else if (yearGanZhiType == 2) {
            yearGanZhi = lunar.getYearInGanZhiExact(); // 以立春交接的时刻作为新年的开始
        } else {
            yearGanZhi = lunar.getYearInGanZhi(); // 以正月初一作为新年的开始
        }

        // 4、判断月干支类型
        String monthGanZhi; // 月干支
        if (monthGanZhiType == 0) {
            monthGanZhi = lunar.getMonthInGanZhi(); // 以节交接当天起算
        } else if (monthGanZhiType == 1) {
            monthGanZhi = lunar.getMonthInGanZhiExact(); // 以节交接时刻起算
        } else {
            monthGanZhi = lunar.getMonthInGanZhi(); // 以节交接当天起算
        }

        // 5、判断日干支类型
        String dayGanZhi; // 日干支
        if (dayGanZhiType == 0) {
            dayGanZhi = lunar.getDayInGanZhiExact(); // 晚子时日干支算明天
        } else if (dayGanZhiType == 1) {
            dayGanZhi = lunar.getDayInGanZhiExact2(); // 晚子时日干支算当天
        } else {
            dayGanZhi = lunar.getDayInGanZhiExact(); // 晚子时日干支算明天
        }

        // 6、早子时和晚子时
        String hourGanZhi = lunar.getTimeInGanZhi(); // 时干支

        // 7、封装数据并返回
        Map<String, Object> map = new HashMap<>();
        map.put("solar", solar); // 公历日期（Solar型，如：2024-01-01）
        map.put("lunar", lunar); // 农历日期（Lunar型，如：二〇二三年冬月二十）
        map.put("solarStr", solarStr); // 公历日期（String型，如：2024-01-01 00:00:00）
        map.put("lunarStr", lunarStr); // 农历日期（String型，如：2023-11-20 00:00:00）
        map.put("solarStr2", solarStr2); // 公历日期（String型，如：2024年01月01日00时00分00秒）
        map.put("lunarStr2", lunarStr2); // 农历日期（String型，如：二〇二三年冬月二十(早)子时）
        map.put("solarDate", solarDate); // 公历日期（Date型，如：Mon Jan 01 00:00:00 CST 2024）
        map.put("lunarDate", lunarDate); // 农历日期（Date型，如：Mon Nov 20 00:00:00 CST 2023）
        map.put("yearGanZhi", yearGanZhi); // 年干支
        map.put("monthGanZhi", monthGanZhi); // 月干支
        map.put("dayGanZhi", dayGanZhi); // 日干支
        map.put("hourGanZhi", hourGanZhi); // 时干支
        return map;

    }


}
