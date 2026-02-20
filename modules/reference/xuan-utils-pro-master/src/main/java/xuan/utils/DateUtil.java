package xuan.utils;

import java.util.*;

import com.nlf.calendar.Lunar;
import com.nlf.calendar.Solar;

import java.time.LocalDateTime;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.temporal.ChronoUnit;
import java.time.format.DateTimeFormatter;

/**
 * 日期工具
 *
 * @author 善待
 */
public class DateUtil {

    /**
     * 日期格式（格式：yyyy年MM月dd日HH时mm分ss秒）
     */
    public static final String DATE_TIME_FORMAT = "yyyy年MM月dd日HH时mm分ss秒";

    /**
     * 日期格式（格式：yyyy-MM-dd HH:mm:ss）
     */
    public static final String DATE_TIME_FORMAT_2 = "yyyy-MM-dd HH:mm:ss";

//*******************************************************************************************************************************

    /**
     * 格式化Solar公历日期
     *
     * @param solar 公历日期（格式：Solar）
     * @return 公历日期（如：2024-01-01 00:00:00）
     */
    public static String getSolarStr(Solar solar) {

        return solar.toYmdHms();

    }

    /**
     * 格式化Solar公历日期
     *
     * @param solar 公历日期（格式：Solar）
     * @return 公历日期（如：2024年01月01日00时00分00秒）
     */
    public static String getSolarStr2(Solar solar) {

        DateTimeFormatter inputFormatter = DateTimeFormatter.ofPattern(DATE_TIME_FORMAT_2);
        DateTimeFormatter outputFormatter = DateTimeFormatter.ofPattern(DATE_TIME_FORMAT);
        LocalDateTime dateTime = LocalDateTime.parse(solar.toYmdHms(), inputFormatter);
        return dateTime.format(outputFormatter);

    }

    /**
     * 格式化Lunar农历日期
     *
     * @param lunar 农历日期（格式：Lunar）
     * @return 农历日期（如：2023-10-18 00:00:00）
     */
    public static String getLunarStr(Lunar lunar) {

        String yearStr = String.valueOf(lunar.getYear()); // 年
        String monthStr = String.valueOf(lunar.getMonth() > 0 ? lunar.getMonth() : -lunar.getMonth()); // 月（因为闰月为负数，需要转为正数）
        String dayStr = String.valueOf(lunar.getDay()); // 日
        String hourStr = String.valueOf(lunar.getHour()); // 时
        String minuteStr = String.valueOf(lunar.getMinute()); // 分
        String secondStr = String.valueOf(lunar.getSecond()); // 秒

        String year = yearStr; // 年
        String month = monthStr.length() < 2 ? ("0" + monthStr) : monthStr; // 月
        String day = dayStr.length() < 2 ? ("0" + dayStr) : dayStr; // 日
        String hour = hourStr.length() < 2 ? ("0" + hourStr) : hourStr; // 时
        String minute = minuteStr.length() < 2 ? ("0" + minuteStr) : minuteStr; // 分
        String second = secondStr.length() < 2 ? ("0" + secondStr) : secondStr; // 秒

        return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second;

    }

    /**
     * 格式化Lunar农历日期
     *
     * @param lunar 农历日期（格式：Lunar）
     * @return 农历日期（如：二〇二三年十月十八(早)子时）
     */
    public static String getLunarStr2(Lunar lunar) {

        String lunarStr;

        // 判断时辰
        int hour = lunar.getHour();
        if (hour >= 23 || hour < 1) {
            // 判断早晚子时
            if (hour >= 23) {
                lunarStr = lunar + "(晚)子时";
            } else {
                lunarStr = lunar + "(早)子时";
            }
        } else {
            final String[] HOUR_ZHI = {"子", "丑", "丑", "寅", "寅", "卯", "卯", "辰", "辰", "巳", "巳", "午", "午", "未", "未", "申", "申", "酉", "酉", "戌", "戌", "亥", "亥", "子"};
            lunarStr = lunar + HOUR_ZHI[hour] + "时";
        }

        return lunarStr;

    }

    /**
     * 获取Date型日期
     *
     * @param dateStr String型日期
     * @return Date型日期
     */
    public static Date stringToDate(String dateStr) {

        Date date = new Date();
        SimpleDateFormat df = new SimpleDateFormat(DateUtil.DATE_TIME_FORMAT_2);
//        df.setTimeZone(TimeZone.getTimeZone("GMT+8"));
        try {
            date = df.parse(dateStr);
        } catch (ParseException e) {
            e.printStackTrace();
        }
        return date;

    }

    /**
     * 获取日期的[年月日时分秒]
     *
     * @param date 日期
     * @return 年月日时分秒
     */
    public static Map<String, Integer> getDateMap(Date date) {

        Calendar c = Calendar.getInstance();
        c.setTime(date);

        Map<String, Integer> map = new HashMap<>();
        map.put("year", c.get(Calendar.YEAR)); // 年
        map.put("month", c.get(Calendar.MONTH) + 1); // 月
        map.put("day", c.get(Calendar.DATE)); // 日
        map.put("hour", c.get(Calendar.HOUR_OF_DAY)); // 时
        map.put("minute", c.get(Calendar.MINUTE)); // 分
        map.put("second", c.get(Calendar.SECOND)); // 秒

        return map;

    }

    /**
     * 计算两个日期的时间间隔
     *
     * @param startDate 开始日期
     * @param endDate   结束日期
     * @return 时间间隔
     */
    public static Map<String, Long> dateInterval(String startDate, String endDate) {

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern(DATE_TIME_FORMAT_2);
        LocalDateTime sDate = LocalDateTime.parse(startDate, formatter); // 开始日期
        LocalDateTime eDate = LocalDateTime.parse(endDate, formatter); // 结束日期

        Long year = ChronoUnit.YEARS.between(sDate, eDate);
        Long month = ChronoUnit.MONTHS.between(sDate, eDate);
        Long day = ChronoUnit.DAYS.between(sDate, eDate);
        Long hour = ChronoUnit.HOURS.between(sDate, eDate) % 24;
        Long minute = ChronoUnit.MINUTES.between(sDate, eDate) % 60;
        Long second = ChronoUnit.SECONDS.between(sDate, eDate) % 60;

        Map<String, Long> map = new HashMap<>();
        map.put("year", year); // 相差年数
        map.put("month", month); // 相差月数
        map.put("day", day); // 相差天数
        map.put("hour", hour); // 相差小时数
        map.put("minute", minute); // 相差分钟数
        map.put("second", second); // 相差秒数

        return map;

    }

    /**
     * 获取指定日期字符串
     *
     * @param date       Date型日期
     * @param dateFormat 日期格式
     * @return String型日期
     */
    public static String getDateStr(Date date, String dateFormat) {

        String dateStr;
        SimpleDateFormat sdf = new SimpleDateFormat(dateFormat);
//        sdf.setTimeZone(TimeZone.getTimeZone("GMT+8"));
        dateStr = sdf.format(date);
        return dateStr;

    }

    /**
     * 年月日时分秒 转 Date
     *
     * @param year   年
     * @param month  月
     * @param day    日
     * @param time   时
     * @param minute 分
     * @param second 秒
     * @return date型日期
     */
    public static Date timeToDate(int year, int month, int day, int time, int minute, int second) {

        Date date = null;
        String sDate = (year + "-" + month + "-" + day + " " + time + ":" + minute + ":" + second);
        try {
            date = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").parse(sDate);
        } catch (ParseException e) {
            e.printStackTrace();
        }
        return date;

    }

    /**
     * 获取日期字符串（格式：yyyy-MM-dd HH:mm:ss）
     *
     * @param year   年
     * @param month  月
     * @param day    日
     * @param time   时
     * @param minute 分
     * @param second 秒
     * @return 日期字符串
     */
    public static String getDateStr(int year, int month, int day, int time, int minute, int second) {

        Date date = new Date(year - 1900, month - 1, day, time, minute, second);
        String dateStr;
        SimpleDateFormat df = new SimpleDateFormat(DateUtil.DATE_TIME_FORMAT_2);
        dateStr = df.format(date);
        return dateStr;

    }

    /**
     * 判断日期格式是否为：yyyy-MM-dd HH:mm:ss
     *
     * @param dateStr 日期字符串（格式：yyyy-MM-dd HH:mm:ss）
     * @return true:符合。false:不符合
     */
    public static boolean isValidDate(String dateStr) {

        if (null == dateStr) return false;

        SimpleDateFormat simpleDateFormat = new SimpleDateFormat(DATE_TIME_FORMAT_2);
//        df.setTimeZone(TimeZone.getTimeZone("GMT+8"));
        simpleDateFormat.setLenient(false); // 严格检查模式

        try {
            simpleDateFormat.parse(dateStr);
            return true;
        } catch (Exception e) {
            return false;
        }

    }

    /**
     * 根据日期字符串（格式：yyyy-MM-dd HH:mm:ss）获取年、月、日、时、分、秒
     *
     * @param dateStr 字符串型日期（格式：yyyy-MM-dd HH:mm:ss）
     * @return 年、月、日、时、分、秒
     */
    public static Map<String, Integer> getDateInfo(String dateStr) {

//        if (!isValidDate(dateStr)) dateStr = "2024-01-01 00:00:00";

        String[] s1 = dateStr.split(" ");
        String yearMonthDay = s1[0]; // 年、月、日
        String hourMinuteSecond = s1[1]; // 时、分、秒

        String[] s2 = yearMonthDay.split("-");
        int year = Integer.parseInt(s2[0]); // 年
        int month = Integer.parseInt(s2[1]); // 月
        int day = Integer.parseInt(s2[2]); // 日
        String[] s3 = hourMinuteSecond.split(":");
        int hour = Integer.parseInt(s3[0]); // 时
        int minute = Integer.parseInt(s3[1]); // 分
        int second = Integer.parseInt(s3[2]); // 秒

        Map<String, Integer> map = new HashMap<>();
        map.put("year", year); // 年
        map.put("month", month); // 月
        map.put("day", day); // 日
        map.put("hour", hour); // 时
        map.put("minute", minute); // 分
        map.put("second", second); // 秒
        return map;

    }

    /**
     * 在日期上增加（+）或减少（-）年数、月数、日数、时数、分数、秒数
     *
     * @param date    日期
     * @param iYear   要增加或减少的年数
     * @param iMonth  要增加或减少的月数
     * @param iDay    要增加或减少的日数
     * @param iHour   要增加或减少的时数
     * @param iMinute 要增加或减少的分数
     * @param iSecond 要增加或减少的秒数
     */
    public static Date updateDate(Date date, int iYear, int iMonth, int iDay, int iHour, int iMinute, int iSecond) {

        Calendar c = Calendar.getInstance();
//        c.setTimeZone(TimeZone.getTimeZone("GMT+8"));
        c.setTime(date);

        c.add(Calendar.YEAR, iYear); // 年数
        c.add(Calendar.MONTH, iMonth); // 月数
        c.add(Calendar.DAY_OF_MONTH, iDay); // 日数
        c.add(Calendar.HOUR_OF_DAY, iHour); // 小时
        c.add(Calendar.MINUTE, iMinute); // 分钟
        c.add(Calendar.SECOND, iSecond); // 秒

        return c.getTime();

    }


}
