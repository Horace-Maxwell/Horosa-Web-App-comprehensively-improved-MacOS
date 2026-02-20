package xuan.utils;

import java.util.*;

/**
 * 真太阳时工具
 *
 * @author 善待
 */
public class TrueSolarDateUtil {

    /**
     * 十二个月的太阳运行时间修正（单位：分）【暂未区分年份】
     */
    private static final Map<Integer, List<Integer>> SHI_CHA_MINUTE = new HashMap<Integer, List<Integer>>() {
        private static final long serialVersionUID = -1;

        {
            // 例如：公历1月1日需要在平太阳时的基础上减3分钟，1月2日减3分钟，1月3日减4分钟，...
            put(1, Arrays.asList(0, -3, -3, -4, -4, -5, -5, -5, -6, -6, -7, -7, -7, -8, -8, -9, -9, -9, -10, -10, -10, -11, -11, -11, -11, -12, -12, -12, -12, -13, -13, -13));
            put(2, Arrays.asList(0, -13, -13, -13, -14, -14, -14, -14, -14, -14, -14, -14, -14, -14, -14, -14, -14, -13, -13, -13, -13, -13, -13, -13, -11, -12, -12, -12, -12, -12));
            put(3, Arrays.asList(0, -11, -11, -11, -11, -11, -10, -10, -10, -10, -9, -9, -9, -8, -8, -8, -8, -7, -7, -7, -6, -6, -6, -5, -5, -5, -5, -4, -4, -4, -3, -3));
            put(4, Arrays.asList(0, -3, -2, -2, -2, -2, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3));
            put(5, Arrays.asList(0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2));
            put(6, Arrays.asList(0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -2, -2, -2, -2, -3, -3, -3, -3, -3, -4, -4));
            put(7, Arrays.asList(0, -4, -4, -4, -4, -5, -5, -5, -5, -5, -5, -5, -5, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6, -6));
            put(8, Arrays.asList(0, -6, -5, -5, -5, -5, -5, -5, -5, -5, -4, -4, -4, -4, -4, -3, -3, -3, -3, -2, -2, -2, -2, -1, -1, -1, 0, 0, 0, 0, 0, 0));
            put(9, Arrays.asList(0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10));
            put(10, Arrays.asList(0, 10, 11, 11, 11, 11, 12, 12, 12, 13, 13, 13, 13, 13, 13, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 15, 16, 16, 16, 16, 16, 16));
            put(11, Arrays.asList(0, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 15, 15, 15, 15, 15, 15, 15, 14, 14, 14, 14, 13, 13, 13, 12, 12, 12, 12, 11, 11));
            put(12, Arrays.asList(0, 10, 10, 10, 9, 9, 8, 8, 8, 7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0, 0, 0, 0, -1, -1, -2, -2, -3));
        }

    };

    /**
     * 十二个月的太阳运行时间修正（单位：秒）【暂未区分年份】
     */
    private static final Map<Integer, List<Integer>> SHI_CHA_SECOND = new HashMap<Integer, List<Integer>>() {
        private static final long serialVersionUID = -1;

        {
            // 例如：公历1月1日需要在平太阳时的基础上减9秒钟，1月2日减38秒钟，1月3日减6秒钟，...
            put(1, Arrays.asList(0, -9, -38, -6, -33, -1, -27, -54, -20, -45, -10, -35, -59, -22, -45, -7, -28, -49, -9, -28, -47, -5, -22, -38, -54, -8, -22, -35, -59, -10, -19, -37));
            put(2, Arrays.asList(0, -44, -50, -56, -1, -5, -9, -11, -13, -14, -15, -14, -13, -11, -8, -5, -1, -56, -51, -44, -38, -30, -22, -13, -4, -54, -43, -32, -21, -8));
            put(3, Arrays.asList(0, -56, -43, -29, -15, -1, -47, -32, -16, -1, -45, -28, -12, -55, -38, -21, -4, -46, -29, -11, -53, -35, -17, -58, -40, -22, -4, -45, -27, -9, -51, -33));
            put(4, Arrays.asList(0, -16, -58, -41, -24, -7, -50, -33, -17, -1, 46, 30, 16, 1, 13, 27, 41, 54, 6, 19, 31, 42, 53, 4, 14, 23, 33, 41, 49, 57, 4));
            put(5, Arrays.asList(0, 10, 16, 21, 26, 30, 37, 36, 39, 40, 42, 42, 42, 42, 41, 39, 37, 34, 31, 27, 23, 18, 13, 7, 1, 54, 47, 39, 31, 22, 13, 4));
            put(6, Arrays.asList(0, 54, 44, 34, 23, 12, 0, 48, 36, 24, 12, 1, 14, 39, 52, -5, -18, -31, -45, -57, -10, -23, -36, -48, -1, -13, -25, -37, -49, -0, -11));
            put(7, Arrays.asList(0, -22, -33, -43, -53, -2, -11, -20, -28, -36, -43, -50, -56, -2, -8, -12, -16, -20, -23, -25, -27, -29, -29, -29, -29, -28, -26, -24, -24, -17, -13, -8));
            put(8, Arrays.asList(0, -3, -57, -51, -44, -36, -28, -19, -10, 0, -50, -39, -27, -15, -2, -49, -36, -21, -7, -51, -36, -20, -3, -47, -29, -12, 54, 35, 17, 2, 21, 41));
            put(9, Arrays.asList(0, 0, 20, 40, 1, 21, 42, 3, 3, 24, 45, 6, 27, 48, 10, 31, 53, 14, 35, 57, 18, 39, 0, 21, 42, 2, 22, 42, 2, 21, 40));
            put(10, Arrays.asList(0, 59, 18, 36, 36, 53, 11, 28, 44, 0, 16, 16, 31, 45, 59, 13, 26, 38, 50, 1, 12, 21, 31, 40, 48, 55, 1, 7, 12, 16, 20, 22));
            put(11, Arrays.asList(0, 24, 25, 25, 24, 23, 21, 17, 13, 9, 3, 56, 49, 41, 32, 22, 11, 0, 47, 34, 20, 6, 50, 34, 17, 59, 40, 21, 1, 40, 18));
            put(12, Arrays.asList(0, 56, 33, 9, 45, 21, 55, 29, 3, 36, 9, 42, 14, 46, 17, 48, 19, 50, 21, 51, 22, 52, 22, 52, 23, 7, 37, -6, -36, -5, -34, -3));
        }

    };

//*******************************************************************************************************************************

    /**
     * 获取真太阳时（根据地区计算）
     *
     * @param date    标准时间（东八区120°经度时刻）
     * @param address 地区
     * @return 真太阳时
     */
    public static Date getTrueSolarDate(Date date, String address) {

        // 1、通过地区获取经度
        Map<String, Double> lngAndLat = BaiduMapsUtil.getLngAndLat(address);

        // 2、计算平太阳时
        Date meanSolarTime = findMeanSolarDate(date, lngAndLat.get("lng"));

        // 3、计算真太阳时
        return findTrueSolarDate(meanSolarTime);

    }

    /**
     * 获取真太阳时（根据经度计算）
     *
     * @param date 标准时间（东八区120°经度时刻）
     * @param lng  经度
     * @return 真太阳时
     */
    public static Date getTrueSolarDate(Date date, double lng) {

        // 1、计算平太阳时
        Date meanSolarTime = findMeanSolarDate(date, lng);

        // 2、计算真太阳时
        return findTrueSolarDate(meanSolarTime);

    }

//-------------------------------------------------------------------------------------------------------------------------------

    /**
     * 计算平太阳时
     *
     * @param date 标准时间（东八区120°经度时刻）
     * @param lng  经度
     * @return 平太阳时
     */
    private static Date findMeanSolarDate(Date date, double lng) {

        /*
            地球经线360度，自转一周，需要23时59分4秒，即1439分4秒，
            所以每一经度的时差为：1439.4/360≈3.997分钟，约等于4分钟（此处直接按4分钟计算），
            因此，由经度造成的时差，每向东增加一度，加上4分钟；每向西增加一度，减去4分钟。
         */

        // 1、保留经度的两位小数
        lng = CommonUtil.getDouble(lng, 2);

        // 2、计算经度时差
        double longitudeDifference = lng - 120; // 经度差（正数：所在地区的经度大于120°，真太阳时比平太阳时快。负数：所在地区的经度小于120°，真太阳时比平太阳时慢。）
        longitudeDifference = CommonUtil.getDouble(longitudeDifference, 2); // 保留经度差的两位小数
        double timeDifference = longitudeDifference * 4; // 时差（每一经度的时差约等于4分钟）

        // 3.1、获取小时数、分钟数、秒数
        String[] split = String.valueOf(timeDifference).split("\\.");
        int hour = 0; // 小时
        int minute = Integer.parseInt(split[0]); // 分钟
        // 3.2、若分钟数为负数，则临时转为正数
        if (minute < 0) minute = -minute;
        int second = Integer.parseInt(split[1]); // 秒钟

        // 4.1、若秒钟大于60，则需减去60秒钟，并且分钟+1
        if (second > 60) {
            second -= 60; // 秒钟减去60秒钟
            minute += 1; // 分钟增加1分钟
        }
        // 4.2、若分钟大于60，则需减去60分钟，并且小时+1
        if (minute > 60) {
            minute -= 60; // 秒钟减去60分钟
            hour += 1; // 小时增加1小时
        }

        // 5、若经度差为负数，则时、分、秒也转为负数
        if (longitudeDifference < 0) {
            hour = -hour; // 时
            minute = -minute; // 分
            second = -second; // 秒
        }

        // 6、计算平太阳时
        return DateUtil.updateDate(date, 0, 0, 0, hour, minute, second); // 在日期上增加（+）或减少（-）年数、月数、日数、时数、分数、秒数

    }

    /**
     * 计算真太阳时
     *
     * @param date 平太阳时
     * @return 真太阳时
     */
    private static Date findTrueSolarDate(Date date) {

        // 1、获取日期的[年月日时分秒]
        Map<String, Integer> dateMap = DateUtil.getDateMap(date);

        // 2、获取真太阳时的修正时间
        Integer minute = SHI_CHA_MINUTE.get(dateMap.get("month")).get(dateMap.get("day")); // 需要增加或减少的分钟数
        Integer second = SHI_CHA_SECOND.get(dateMap.get("month")).get(dateMap.get("day")); // 需要增加或减少的秒数
        minute = null != minute ? minute : 0;
        second = null != second ? minute : 0;

        // 3、计算真太阳时
        return DateUtil.updateDate(date, 0, 0, 0, 0, minute, second); // 在日期上增加（+）或减少（-）年数、月数、日数、时数、分数、秒数

    }


}
