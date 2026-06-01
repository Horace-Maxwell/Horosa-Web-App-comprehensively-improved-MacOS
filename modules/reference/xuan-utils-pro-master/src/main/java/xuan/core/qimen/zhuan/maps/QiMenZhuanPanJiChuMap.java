package xuan.core.qimen.zhuan.maps;

import java.util.*;

/**
 * 转盘奇门 - 基础常量
 *
 * @author 善待
 */
public class QiMenZhuanPanJiChuMap {

    /**
     * 月将、月将神（上一气+下一气为键）
     */
    public static final Map<String, List<String>> YUE_JIANG = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("大寒雨水", Arrays.asList("子", "神后")); // 大寒至雨水：月将为子，月将神为神后
            put("冬至大寒", Arrays.asList("丑", "大吉"));
            put("小雪冬至", Arrays.asList("寅", "功曹"));
            put("霜降小雪", Arrays.asList("卯", "太冲"));
            put("秋分霜降", Arrays.asList("辰", "天罡"));
            put("处暑秋分", Arrays.asList("巳", "太乙"));
            put("大暑处暑", Arrays.asList("午", "胜光"));
            put("夏至大暑", Arrays.asList("未", "小吉"));
            put("小满夏至", Arrays.asList("申", "传送"));
            put("谷雨小满", Arrays.asList("酉", "从魁"));
            put("春分谷雨", Arrays.asList("戌", "河魁"));
            put("雨水春分", Arrays.asList("亥", "登明"));
        }
    };

    /**
     * 五不遇时（日干为键）
     */
    public static final Map<String, String> WU_BU_YU_SHI = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲", "庚午"); // 甲日庚午时
            put("乙", "辛巳");
            put("丙", "壬辰");
            put("丁", "癸卯");
            put("戊", "甲寅");
            put("己", "乙丑");
            put("庚", "丙子");
            put("辛", "丁酉");
            put("壬", "戊申");
            put("癸", "己未");
        }
    };

    /**
     * 天干五行（天干为键）
     */
    public static final Map<String, String> TIAN_GAN_WU_XING = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲", "木");
            put("乙", "木");
            put("丙", "火");
            put("丁", "火");
            put("戊", "土");
            put("己", "土");
            put("庚", "金");
            put("辛", "金");
            put("壬", "水");
            put("癸", "水");
        }
    };

    /**
     * 地支五行（地支为键）
     */
    public static final Map<String, String> DI_ZHI_WU_XING = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子", "水");
            put("丑", "土");
            put("寅", "木");
            put("卯", "木");
            put("辰", "土");
            put("巳", "火");
            put("午", "火");
            put("未", "土");
            put("申", "金");
            put("酉", "金");
            put("戌", "土");
            put("亥", "水");
        }
    };

    /**
     * 纳音（干支为键）
     */
    public static final Map<String, String> NA_YIN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲子", "海中金");
            put("丙寅", "炉中火");
            put("戊辰", "大林木");
            put("庚午", "路旁土");
            put("壬申", "剑锋金");
            put("甲戌", "山头火");
            put("丙子", "涧下水");
            put("戊寅", "城头土");
            put("庚辰", "白蜡金");
            put("壬午", "杨柳木");
            put("甲申", "泉中水");
            put("丙戌", "屋上土");
            put("戊子", "霹雳火");
            put("庚寅", "松柏木");
            put("壬辰", "长流水");
            put("甲午", "沙中金");
            put("丙申", "山下火");
            put("戊戌", "平地木");
            put("庚子", "壁上土");
            put("壬寅", "金箔金");
            put("甲辰", "覆灯火");
            put("丙午", "天河水");
            put("戊申", "大驿土");
            put("庚戌", "钗钏金");
            put("壬子", "桑柘木");
            put("甲寅", "大溪水");
            put("丙辰", "沙中土");
            put("戊午", "天上火");
            put("庚申", "石榴木");
            put("壬戌", "大海水");
            put("乙丑", "海中金");
            put("丁卯", "炉中火");
            put("己巳", "大林木");
            put("辛未", "路旁土");
            put("癸酉", "剑锋金");
            put("乙亥", "山头火");
            put("丁丑", "涧下水");
            put("己卯", "城头土");
            put("辛巳", "白蜡金");
            put("癸未", "杨柳木");
            put("乙酉", "泉中水");
            put("丁亥", "屋上土");
            put("己丑", "霹雳火");
            put("辛卯", "松柏木");
            put("癸巳", "长流水");
            put("乙未", "沙中金");
            put("丁酉", "山下火");
            put("己亥", "平地木");
            put("辛丑", "壁上土");
            put("癸卯", "金箔金");
            put("乙巳", "覆灯火");
            put("丁未", "天河水");
            put("己酉", "大驿土");
            put("辛亥", "钗钏金");
            put("癸丑", "桑柘木");
            put("乙卯", "大溪水");
            put("丁巳", "沙中土");
            put("己未", "天上火");
            put("辛酉", "石榴木");
            put("癸亥", "大海水");
        }
    };

    /**
     * 空亡（干支为键）
     */
    public static final Map<String, String> KONG_WANG = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲子", "戌亥");
            put("乙丑", "戌亥");
            put("丙寅", "戌亥");
            put("丁卯", "戌亥");
            put("戊辰", "戌亥");
            put("己巳", "戌亥");
            put("庚午", "戌亥");
            put("辛未", "戌亥");
            put("壬申", "戌亥");
            put("癸酉", "戌亥");
            put("甲戌", "申酉");
            put("乙亥", "申酉");
            put("丙子", "申酉");
            put("丁丑", "申酉");
            put("戊寅", "申酉");
            put("己卯", "申酉");
            put("庚辰", "申酉");
            put("辛巳", "申酉");
            put("壬午", "申酉");
            put("癸未", "申酉");
            put("甲申", "午未");
            put("乙酉", "午未");
            put("丙戌", "午未");
            put("丁亥", "午未");
            put("戊子", "午未");
            put("己丑", "午未");
            put("庚寅", "午未");
            put("辛卯", "午未");
            put("壬辰", "午未");
            put("癸巳", "午未");
            put("甲午", "辰巳");
            put("乙未", "辰巳");
            put("丙申", "辰巳");
            put("丁酉", "辰巳");
            put("戊戌", "辰巳");
            put("己亥", "辰巳");
            put("庚子", "辰巳");
            put("辛丑", "辰巳");
            put("壬寅", "辰巳");
            put("癸卯", "辰巳");
            put("甲辰", "寅卯");
            put("乙巳", "寅卯");
            put("丙午", "寅卯");
            put("丁未", "寅卯");
            put("戊申", "寅卯");
            put("己酉", "寅卯");
            put("庚戌", "寅卯");
            put("辛亥", "寅卯");
            put("壬子", "寅卯");
            put("癸丑", "寅卯");
            put("甲寅", "子丑");
            put("乙卯", "子丑");
            put("丙辰", "子丑");
            put("丁巳", "子丑");
            put("戊午", "子丑");
            put("己未", "子丑");
            put("庚申", "子丑");
            put("辛酉", "子丑");
            put("壬戌", "子丑");
            put("癸亥", "子丑");
        }
    };

    /**
     * 地支
     * <p>十二时辰命名：夜半、鸡鸣、平旦、日出、早食、隅中、日中、日昳、晡时、日入、黄昏、人定</p>
     */
    public static final String[] DI_ZHI = {"子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"};

    /**
     * 公历0~9999年两个日期范围内的三元、局数（年家奇门）
     */
    public static final Map<Integer, List<Object>> SAN_YUAN_DATE_RANGE = new HashMap<Integer, List<Object>>() {
        private static final long serialVersionUID = -1;

        {
            put(0, Arrays.asList(0, 3, "中元", 4));         // 公历0~3年：中元，阴遁4局
            put(1, Arrays.asList(4, 63, "下元", 7));        // 公历4~63年：下元，阴遁7局
            put(2, Arrays.asList(64, 123, "上元", 1));      // 公历64~123年：上元，阴遁1局
            put(3, Arrays.asList(124, 183, "中元", 4));     // 公历124~183年：中元，阴遁4局
            put(4, Arrays.asList(184, 243, "下元", 7));     // 公历184~243年：下元，阴遁7局
            put(5, Arrays.asList(244, 303, "上元", 1));     // 公历244~303年：上元，阴遁1局
            put(6, Arrays.asList(304, 363, "中元", 4));     // 公历304~363年：中元，阴遁4局
            put(7, Arrays.asList(364, 423, "下元", 7));     // 公历364~423年：下元，阴遁7局
            put(8, Arrays.asList(424, 483, "上元", 1));     // 公历424~483年：上元，阴遁1局
            put(9, Arrays.asList(484, 543, "中元", 4));     // 公历484~543年：中元，阴遁4局
            put(10, Arrays.asList(544, 603, "下元", 7));    // 公历544~603年：下元，阴遁7局
            put(11, Arrays.asList(604, 663, "上元", 1));    // 公历604~663年：上元，阴遁1局
            put(12, Arrays.asList(664, 723, "中元", 4));    // 公历664~723年：中元，阴遁4局
            put(13, Arrays.asList(724, 783, "下元", 7));    // 公历724~783年：下元，阴遁7局
            put(14, Arrays.asList(784, 843, "上元", 1));    // 公历784~843年：上元，阴遁1局
            put(15, Arrays.asList(844, 903, "中元", 4));    // 公历844~903年：中元，阴遁4局
            put(16, Arrays.asList(904, 963, "下元", 7));    // 公历904~963年：下元，阴遁7局
            put(17, Arrays.asList(964, 1023, "上元", 1));   // 公历964~1023年：上元，阴遁1局
            put(18, Arrays.asList(1024, 1083, "中元", 4));  // 公历1024~1083年：中元，阴遁4局
            put(19, Arrays.asList(1084, 1143, "下元", 7));  // 公历1084~1143年：下元，阴遁7局
            put(20, Arrays.asList(1144, 1203, "上元", 1));  // 公历1144~1203年：上元，阴遁1局
            put(21, Arrays.asList(1204, 1263, "中元", 4));  // 公历1204~1263年：中元，阴遁4局
            put(22, Arrays.asList(1264, 1323, "下元", 7));  // 公历1264~1323年：下元，阴遁7局
            put(23, Arrays.asList(1324, 1383, "上元", 1));  // 公历1324~1383年：上元，阴遁1局
            put(24, Arrays.asList(1384, 1433, "中元", 4));  // 公历1384~1433年：中元，阴遁4局
            put(25, Arrays.asList(1444, 1503, "下元", 7));  // 公历1444~1503年：下元，阴遁7局
            put(26, Arrays.asList(1504, 1563, "上元", 1));  // 公历1504~1563年：上元，阴遁1局
            put(27, Arrays.asList(1564, 1623, "中元", 4));  // 公历1564~1623年：中元，阴遁4局
            put(28, Arrays.asList(1624, 1683, "下元", 7));  // 公历1624~1683年：下元，阴遁7局
            put(29, Arrays.asList(1684, 1743, "上元", 1));  // 公历1684~1743年：上元，阴遁1局
            put(30, Arrays.asList(1744, 1803, "中元", 4));  // 公历1744~1803年：中元，阴遁4局
            put(31, Arrays.asList(1804, 1863, "下元", 7));  // 公历1804~1863年：下元，阴遁7局
            put(32, Arrays.asList(1864, 1923, "上元", 1));  // 公历1864~1923年：上元，阴遁1局
            put(33, Arrays.asList(1924, 1983, "中元", 4));  // 公历1924~1983年：中元，阴遁4局
            put(34, Arrays.asList(1984, 2043, "下元", 7));  // 公历1984~2043年：下元，阴遁7局
            put(35, Arrays.asList(2044, 2103, "上元", 1));  // 公历2044~2103年：上元，阴遁1局
            put(36, Arrays.asList(2104, 2163, "中元", 4));  // 公历2104~2163年：中元，阴遁4局
            put(37, Arrays.asList(2164, 2223, "下元", 7));  // 公历2164~2223年：下元，阴遁7局
            put(38, Arrays.asList(2224, 2283, "上元", 1));  // 公历2224~2283年：上元，阴遁1局
            put(39, Arrays.asList(2284, 2343, "中元", 4));  // 公历2284~2343年：中元，阴遁4局
            put(40, Arrays.asList(2344, 2403, "下元", 7));  // 公历2344~2403年：下元，阴遁7局
            put(41, Arrays.asList(2404, 2463, "上元", 1));  // 公历2404~2463年：上元，阴遁1局
            put(42, Arrays.asList(2464, 2523, "中元", 4));  // 公历2464~2523年：中元，阴遁4局
            put(43, Arrays.asList(2524, 2583, "下元", 7));  // 公历2524~2583年：下元，阴遁7局
            put(44, Arrays.asList(2584, 2643, "上元", 1));  // 公历2584~2643年：上元，阴遁1局
            put(45, Arrays.asList(2644, 2703, "中元", 4));  // 公历2644~2703年：中元，阴遁4局
            put(46, Arrays.asList(2704, 2763, "下元", 7));  // 公历2704~2763年：下元，阴遁7局
            put(47, Arrays.asList(2764, 2823, "上元", 1));  // 公历2764~2823年：上元，阴遁1局
            put(48, Arrays.asList(2824, 2883, "中元", 4));  // 公历2824~2883年：中元，阴遁4局
            put(49, Arrays.asList(2884, 2943, "下元", 7));  // 公历2884~2943年：下元，阴遁7局
            put(50, Arrays.asList(2944, 3003, "上元", 1));  // 公历2944~3003年：上元，阴遁1局
            put(51, Arrays.asList(3004, 3063, "中元", 4));  // 公历3004~3063年：中元，阴遁4局
            put(52, Arrays.asList(3064, 3123, "下元", 7));  // 公历3064~3123年：下元，阴遁7局
            put(53, Arrays.asList(3124, 3183, "上元", 1));  // 公历3124~3183年：上元，阴遁1局
            put(54, Arrays.asList(3184, 3243, "中元", 4));  // 公历3184~3243年：中元，阴遁4局
            put(55, Arrays.asList(3244, 3303, "下元", 7));  // 公历3244~3303年：下元，阴遁7局
            put(56, Arrays.asList(3304, 3363, "上元", 1));  // 公历3304~3363年：上元，阴遁1局
            put(57, Arrays.asList(3364, 3423, "中元", 4));  // 公历3364~3423年：中元，阴遁4局
            put(58, Arrays.asList(3424, 3483, "下元", 7));  // 公历3424~3483年：下元，阴遁7局
            put(59, Arrays.asList(3484, 3543, "上元", 1));  // 公历3484~3543年：上元，阴遁1局
            put(60, Arrays.asList(3544, 3603, "中元", 4));  // 公历3544~3603年：中元，阴遁4局
            put(61, Arrays.asList(3604, 3663, "下元", 7));  // 公历3604~3663年：下元，阴遁7局
            put(62, Arrays.asList(3664, 3723, "上元", 1));  // 公历3664~3723年：上元，阴遁1局
            put(63, Arrays.asList(3724, 3783, "中元", 4));  // 公历3724~3783年：中元，阴遁4局
            put(64, Arrays.asList(3784, 3843, "下元", 7));  // 公历3784~3843年：下元，阴遁7局
            put(65, Arrays.asList(3844, 3903, "上元", 1));  // 公历3844~3903年：上元，阴遁1局
            put(66, Arrays.asList(3904, 3963, "中元", 4));  // 公历3904~3963年：中元，阴遁4局
            put(67, Arrays.asList(3964, 4023, "下元", 7));  // 公历3964~4023年：下元，阴遁7局
            put(68, Arrays.asList(4024, 4083, "上元", 1));  // 公历4024~4083年：上元，阴遁1局
            put(69, Arrays.asList(4084, 4143, "中元", 4));  // 公历4084~4143年：中元，阴遁4局
            put(71, Arrays.asList(4144, 4203, "下元", 7));  // 公历4144~4203年：下元，阴遁7局
            put(72, Arrays.asList(4204, 4263, "上元", 1));  // 公历4204~4263年：上元，阴遁1局
            put(73, Arrays.asList(4264, 4323, "中元", 4));  // 公历4264~4323年：中元，阴遁4局
            put(74, Arrays.asList(4324, 4383, "下元", 7));  // 公历4324~4383年：下元，阴遁7局
            put(75, Arrays.asList(4384, 4443, "上元", 1));  // 公历4384~4443年：上元，阴遁1局
            put(76, Arrays.asList(4444, 4503, "中元", 4));  // 公历4444~4503年：中元，阴遁4局
            put(77, Arrays.asList(4504, 4563, "下元", 7));  // 公历4504~4563年：下元，阴遁7局
            put(78, Arrays.asList(4564, 4623, "上元", 1));  // 公历4564~4623年：上元，阴遁1局
            put(79, Arrays.asList(4624, 4683, "中元", 4));  // 公历4624~4683年：中元，阴遁4局
            put(81, Arrays.asList(4684, 4743, "下元", 7));  // 公历4684~4743年：下元，阴遁7局
            put(82, Arrays.asList(4744, 4803, "上元", 1));  // 公历4744~4803年：上元，阴遁1局
            put(83, Arrays.asList(4804, 4863, "中元", 4));  // 公历4804~4863年：中元，阴遁4局
            put(84, Arrays.asList(4864, 4923, "下元", 7));  // 公历4864~4923年：下元，阴遁7局
            put(85, Arrays.asList(4924, 4983, "上元", 1));  // 公历4924~4983年：上元，阴遁1局
            put(86, Arrays.asList(4984, 5043, "中元", 4));  // 公历4984~5043年：中元，阴遁4局
            put(87, Arrays.asList(5044, 5103, "下元", 7));  // 公历5044~5103年：下元，阴遁7局
            put(88, Arrays.asList(5104, 5163, "上元", 1));  // 公历5104~5163年：上元，阴遁1局
            put(89, Arrays.asList(5164, 5223, "中元", 4));  // 公历5164~5223年：中元，阴遁4局
            put(91, Arrays.asList(5224, 5283, "下元", 7));  // 公历5224~5283年：下元，阴遁7局
            put(92, Arrays.asList(5284, 5343, "上元", 1));  // 公历5284~5343年：上元，阴遁1局
            put(93, Arrays.asList(5344, 5403, "中元", 4));  // 公历5344~5403年：中元，阴遁4局
            put(94, Arrays.asList(5404, 5463, "下元", 7));  // 公历5404~5463年：下元，阴遁7局
            put(95, Arrays.asList(5464, 5523, "上元", 1));  // 公历5464~5523年：上元，阴遁1局
            put(96, Arrays.asList(5524, 5583, "中元", 4));  // 公历5524~5583年：中元，阴遁4局
            put(97, Arrays.asList(5584, 5643, "下元", 7));  // 公历5584~5643年：下元，阴遁7局
            put(98, Arrays.asList(5644, 5703, "上元", 1));  // 公历5644~5703年：上元，阴遁1局
            put(99, Arrays.asList(5704, 5763, "中元", 4));  // 公历5704~5763年：中元，阴遁4局
            put(100, Arrays.asList(5764, 5823, "下元", 7)); // 公历5764~5823年：下元，阴遁7局
            put(101, Arrays.asList(5824, 5883, "上元", 1)); // 公历5824~5883年：上元，阴遁1局
            put(102, Arrays.asList(5884, 5943, "中元", 4)); // 公历5884~5943年：中元，阴遁4局
            put(103, Arrays.asList(5944, 6003, "下元", 7)); // 公历5944~6003年：下元，阴遁7局
            put(104, Arrays.asList(6004, 6063, "上元", 1)); // 公历6004~6063年：上元，阴遁1局
            put(105, Arrays.asList(6064, 6123, "中元", 4)); // 公历6064~6123年：中元，阴遁4局
            put(106, Arrays.asList(6124, 6183, "下元", 7)); // 公历6124~6183年：下元，阴遁7局
            put(107, Arrays.asList(6184, 6243, "上元", 1)); // 公历6184~6243年：上元，阴遁1局
            put(108, Arrays.asList(6244, 6303, "中元", 4)); // 公历6244~6303年：中元，阴遁4局
            put(109, Arrays.asList(6304, 6363, "下元", 7)); // 公历6304~6363年：下元，阴遁7局
            put(110, Arrays.asList(6364, 6423, "上元", 1)); // 公历6364~6423年：上元，阴遁1局
            put(111, Arrays.asList(6424, 6483, "中元", 4)); // 公历6424~6483年：中元，阴遁4局
            put(112, Arrays.asList(6484, 6543, "下元", 7)); // 公历6484~6543年：下元，阴遁7局
            put(113, Arrays.asList(6544, 6603, "上元", 1)); // 公历6544~6603年：上元，阴遁1局
            put(114, Arrays.asList(6604, 6663, "中元", 4)); // 公历6604~6663年：中元，阴遁4局
            put(115, Arrays.asList(6664, 6723, "下元", 7)); // 公历6664~6723年：下元，阴遁7局
            put(116, Arrays.asList(6724, 6783, "上元", 1)); // 公历6724~6783年：上元，阴遁1局
            put(117, Arrays.asList(6784, 6843, "中元", 4)); // 公历6784~6843年：中元，阴遁4局
            put(118, Arrays.asList(6844, 6903, "下元", 7)); // 公历6844~6903年：下元，阴遁7局
            put(119, Arrays.asList(6904, 6963, "上元", 1)); // 公历6904~6963年：上元，阴遁1局
            put(120, Arrays.asList(6964, 7023, "中元", 4)); // 公历6964~7023年：中元，阴遁4局
            put(121, Arrays.asList(7024, 7083, "下元", 7)); // 公历7024~7083年：下元，阴遁7局
            put(122, Arrays.asList(7084, 7143, "上元", 1)); // 公历7084~7143年：上元，阴遁1局
            put(123, Arrays.asList(7144, 7203, "中元", 4)); // 公历7144~7203年：中元，阴遁4局
            put(124, Arrays.asList(7204, 7263, "下元", 7)); // 公历7204~7263年：下元，阴遁7局
            put(125, Arrays.asList(7264, 7323, "上元", 1)); // 公历7264~7323年：上元，阴遁1局
            put(126, Arrays.asList(7324, 7383, "中元", 4)); // 公历7324~7383年：中元，阴遁4局
            put(127, Arrays.asList(7384, 7443, "下元", 7)); // 公历7384~7443年：下元，阴遁7局
            put(128, Arrays.asList(7444, 7503, "上元", 1)); // 公历7444~7503年：上元，阴遁1局
            put(129, Arrays.asList(7504, 7563, "中元", 4)); // 公历7504~7563年：中元，阴遁4局
            put(130, Arrays.asList(7564, 7623, "下元", 7)); // 公历7564~7623年：下元，阴遁7局
            put(131, Arrays.asList(7624, 7683, "上元", 1)); // 公历7624~7683年：上元，阴遁1局
            put(132, Arrays.asList(7684, 7743, "中元", 4)); // 公历7684~7743年：中元，阴遁4局
            put(133, Arrays.asList(7744, 7803, "下元", 7)); // 公历7744~7803年：下元，阴遁7局
            put(134, Arrays.asList(7804, 7863, "上元", 1)); // 公历7804~7863年：上元，阴遁1局
            put(135, Arrays.asList(7864, 7923, "中元", 4)); // 公历7864~7923年：中元，阴遁4局
            put(136, Arrays.asList(7924, 7983, "下元", 7)); // 公历7924~7983年：下元，阴遁7局
            put(137, Arrays.asList(7984, 8043, "上元", 1)); // 公历7984~8043年：上元，阴遁1局
            put(138, Arrays.asList(8044, 8103, "中元", 4)); // 公历8044~8103年：中元，阴遁4局
            put(139, Arrays.asList(8104, 8163, "下元", 7)); // 公历8104~8163年：下元，阴遁7局
            put(140, Arrays.asList(8164, 8223, "上元", 1)); // 公历8164~8223年：上元，阴遁1局
            put(141, Arrays.asList(8224, 8283, "中元", 4)); // 公历8224~8283年：中元，阴遁4局
            put(142, Arrays.asList(8284, 8343, "下元", 7)); // 公历8284~8343年：下元，阴遁7局
            put(143, Arrays.asList(8344, 8403, "上元", 1)); // 公历8344~8403年：上元，阴遁1局
            put(144, Arrays.asList(8404, 8463, "中元", 4)); // 公历8404~8463年：中元，阴遁4局
            put(145, Arrays.asList(8464, 8523, "下元", 7)); // 公历8464~8523年：下元，阴遁7局
            put(146, Arrays.asList(8524, 8583, "上元", 1)); // 公历8524~8583年：上元，阴遁1局
            put(147, Arrays.asList(8584, 8643, "中元", 4)); // 公历8584~8643年：中元，阴遁4局
            put(148, Arrays.asList(8644, 8703, "下元", 7)); // 公历8644~8703年：下元，阴遁7局
            put(149, Arrays.asList(8704, 8763, "上元", 1)); // 公历8704~8763年：上元，阴遁1局
            put(150, Arrays.asList(8764, 8823, "中元", 4)); // 公历8764~8823年：中元，阴遁4局
            put(151, Arrays.asList(8824, 8883, "下元", 7)); // 公历8824~8883年：下元，阴遁7局
            put(152, Arrays.asList(8884, 8943, "上元", 1)); // 公历8884~8943年：上元，阴遁1局
            put(153, Arrays.asList(8944, 9003, "中元", 4)); // 公历8944~9003年：中元，阴遁4局
            put(154, Arrays.asList(9004, 9063, "下元", 7)); // 公历9004~9063年：下元，阴遁7局
            put(155, Arrays.asList(9064, 9123, "上元", 1)); // 公历9064~9123年：上元，阴遁1局
            put(156, Arrays.asList(9124, 9183, "中元", 4)); // 公历9124~9183年：中元，阴遁4局
            put(157, Arrays.asList(9184, 9243, "下元", 7)); // 公历9184~9243年：下元，阴遁7局
            put(158, Arrays.asList(9244, 9303, "上元", 1)); // 公历9244~9303年：上元，阴遁1局
            put(159, Arrays.asList(9304, 9363, "中元", 4)); // 公历9304~9363年：中元，阴遁4局
            put(160, Arrays.asList(9364, 9423, "下元", 7)); // 公历9364~9423年：下元，阴遁7局
            put(161, Arrays.asList(9424, 9483, "上元", 1)); // 公历9424~9483年：上元，阴遁1局
            put(162, Arrays.asList(9484, 9543, "中元", 4)); // 公历9484~9543年：中元，阴遁4局
            put(163, Arrays.asList(9544, 9603, "下元", 7)); // 公历9544~9603年：下元，阴遁7局
            put(164, Arrays.asList(9604, 9663, "上元", 1)); // 公历9604~9663年：上元，阴遁1局
            put(165, Arrays.asList(9664, 9723, "中元", 4)); // 公历9664~9723年：中元，阴遁4局
            put(166, Arrays.asList(9724, 9783, "下元", 7)); // 公历9724~9783年：下元，阴遁7局
            put(167, Arrays.asList(9784, 9843, "上元", 1)); // 公历9784~9843年：上元，阴遁1局
            put(168, Arrays.asList(9844, 9903, "中元", 4)); // 公历9844~9903年：中元，阴遁4局
            put(169, Arrays.asList(9904, 9963, "下元", 7)); // 公历9904~9963年：下元，阴遁7局
            put(170, Arrays.asList(9964, 9999, "上元", 1)); // 公历9964~9999年：上元，阴遁1局

        }
    };

    /**
     * 十二地支对应季节
     */
    public static final Map<String, String> DI_ZHI_JI_JIE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子", "冬季");   // 子：冬季
            put("丑", "四季末"); // 丑：冬季（四季末）
            put("寅", "春季");   // 寅：春季
            put("卯", "春季");   // 卯：春季
            put("辰", "四季末"); // 辰：春季（四季末）
            put("巳", "夏季");   // 巳：夏季
            put("午", "夏季");   // 午：夏季
            put("未", "四季末"); // 未：夏季（四季末）
            put("申", "秋季");   // 申：秋季
            put("酉", "秋季");   // 酉：秋季
            put("戌", "四季末"); // 戌：秋季（四季末）
            put("亥", "冬季");   // 亥：冬季
        }
    };

    /**
     * 三元符头
     */
    public static final String[] SAN_YUAN_FU_TOU = {"甲子", "甲午", "甲寅", "甲申", "甲辰", "甲戌", "己卯", "己酉", "己巳", "己亥", "己丑", "己未"};

    /**
     * 日柱对应的符头
     */
    public static final Map<String, String> RI_ZHU_FU_TOU = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲子", "甲子");
            put("甲午", "甲午");
            put("乙丑", "甲子");
            put("乙未", "甲午");
            put("丙寅", "甲子");
            put("丙申", "甲午");
            put("丁卯", "甲子");
            put("丁酉", "甲午");
            put("戊辰", "甲子");
            put("戊戌", "甲午");
            put("己卯", "己卯");
            put("己酉", "己酉");
            put("庚辰", "己卯");
            put("庚戌", "己酉");
            put("辛巳", "己卯");
            put("辛亥", "己酉");
            put("壬午", "己卯");
            put("壬子", "己酉");
            put("癸未", "己卯");
            put("癸丑", "己酉");
            put("甲申", "甲申");
            put("甲寅", "甲寅");
            put("乙酉", "甲申");
            put("乙卯", "甲寅");
            put("丙戌", "甲申");
            put("丙辰", "甲寅");
            put("丁亥", "甲申");
            put("丁巳", "甲寅");
            put("戊子", "甲申");
            put("戊午", "甲寅");
            put("己巳", "己巳");
            put("己亥", "己亥");
            put("庚午", "己巳");
            put("庚子", "己亥");
            put("辛未", "己巳");
            put("辛丑", "己亥");
            put("壬申", "己巳");
            put("壬寅", "己亥");
            put("癸酉", "己巳");
            put("癸卯", "己亥");
            put("甲戌", "甲戌");
            put("甲辰", "甲辰");
            put("乙亥", "甲戌");
            put("乙巳", "甲辰");
            put("丙子", "甲戌");
            put("丙午", "甲辰");
            put("丁丑", "甲戌");
            put("丁未", "甲辰");
            put("戊寅", "甲戌");
            put("戊申", "甲辰");
            put("己丑", "己丑");
            put("己未", "己未");
            put("庚寅", "己丑");
            put("庚申", "己未");
            put("辛卯", "己丑");
            put("辛酉", "己未");
            put("壬辰", "己丑");
            put("壬戌", "己未");
            put("癸巳", "己丑");
            put("癸亥", "己未");
        }
    };

    /**
     * 日柱对应的三元
     */
    public static final Map<String, String> RI_ZHU_SAN_YUAN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲子", "上元");
            put("甲午", "上元");
            put("乙丑", "上元");
            put("乙未", "上元");
            put("丙寅", "上元");
            put("丙申", "上元");
            put("丁卯", "上元");
            put("丁酉", "上元");
            put("戊辰", "上元");
            put("戊戌", "上元");
            put("己卯", "上元");
            put("己酉", "上元");
            put("庚辰", "上元");
            put("庚戌", "上元");
            put("辛巳", "上元");
            put("辛亥", "上元");
            put("壬午", "上元");
            put("壬子", "上元");
            put("癸未", "上元");
            put("癸丑", "上元");
            put("甲申", "中元");
            put("甲寅", "中元");
            put("乙酉", "中元");
            put("乙卯", "中元");
            put("丙戌", "中元");
            put("丙辰", "中元");
            put("丁亥", "中元");
            put("丁巳", "中元");
            put("戊子", "中元");
            put("戊午", "中元");
            put("己巳", "中元");
            put("己亥", "中元");
            put("庚午", "中元");
            put("庚子", "中元");
            put("辛未", "中元");
            put("辛丑", "中元");
            put("壬申", "中元");
            put("壬寅", "中元");
            put("癸酉", "中元");
            put("癸卯", "中元");
            put("甲戌", "下元");
            put("甲辰", "下元");
            put("乙亥", "下元");
            put("乙巳", "下元");
            put("丙子", "下元");
            put("丙午", "下元");
            put("丁丑", "下元");
            put("丁未", "下元");
            put("戊寅", "下元");
            put("戊申", "下元");
            put("己丑", "下元");
            put("己未", "下元");
            put("庚寅", "下元");
            put("庚申", "下元");
            put("辛卯", "下元");
            put("辛酉", "下元");
            put("壬辰", "下元");
            put("壬戌", "下元");
            put("癸巳", "下元");
            put("癸亥", "下元");
        }
    };

    /**
     * 阴阳遁对应的二十四节气
     */
    public static final Map<String, List<String>> YIN_YANG_DUN_JIE_QI = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("阳遁", Arrays.asList("冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种"));
            put("阴遁", Arrays.asList("夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"));
        }
    };

    /**
     * 二十四节气对应的阴阳遁
     */
    public static final Map<String, String> JIE_QI_YIN_YANG_DUN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("冬至", "阳遁");
            put("小寒", "阳遁");
            put("大寒", "阳遁");
            put("立春", "阳遁");
            put("雨水", "阳遁");
            put("惊蛰", "阳遁");
            put("春分", "阳遁");
            put("清明", "阳遁");
            put("谷雨", "阳遁");
            put("立夏", "阳遁");
            put("小满", "阳遁");
            put("芒种", "阳遁");
            put("夏至", "阴遁");
            put("小暑", "阴遁");
            put("大暑", "阴遁");
            put("立秋", "阴遁");
            put("处暑", "阴遁");
            put("白露", "阴遁");
            put("秋分", "阴遁");
            put("寒露", "阴遁");
            put("霜降", "阴遁");
            put("立冬", "阴遁");
            put("小雪", "阴遁");
            put("大雪", "阴遁");
        }
    };

    /**
     * 二十四节气对应局数
     */
    public static final Map<String, List<Integer>> JU_SHU = new HashMap<String, List<Integer>>() {
        private static final long serialVersionUID = -1;

        /*
            阳遁：
                冬至、惊蛰一七四，小寒二八五，
                大寒、春分三九六，雨水九六三，
                清明、立夏四一七，立春八五二，
                谷雨、小满五二八，芒种六三九。

            阴遁：
                夏至、白露九三六，小暑八二五，
                大暑、秋分七一四，立秋二五八，
                寒露、立冬六九三，处暑一四七，
                霜降、小雪五八二，大雪四七一。
         */ {
            put("冬至", Arrays.asList(1, 7, 4)); // 冬至：上元用阳遁1局，中元用阳遁7局，下元用阳遁4局
            put("小寒", Arrays.asList(2, 8, 5)); // 小寒：上元用阳遁2局，中元用阳遁8局，下元用阳遁5局
            put("大寒", Arrays.asList(3, 9, 6)); // 大寒：上元用阳遁3局，中元用阳遁9局，下元用阳遁6局
            put("立春", Arrays.asList(8, 5, 2)); // 立春：上元用阳遁8局，中元用阳遁5局，下元用阳遁2局
            put("雨水", Arrays.asList(9, 6, 3)); // 雨水：上元用阳遁9局，中元用阳遁6局，下元用阳遁3局
            put("惊蛰", Arrays.asList(1, 7, 4)); // 惊蛰：上元用阳遁1局，中元用阳遁7局，下元用阳遁4局
            put("春分", Arrays.asList(3, 9, 6)); // 春分：上元用阳遁3局，中元用阳遁9局，下元用阳遁6局
            put("清明", Arrays.asList(4, 1, 7)); // 清明：上元用阳遁4局，中元用阳遁1局，下元用阳遁7局
            put("谷雨", Arrays.asList(5, 2, 8)); // 谷雨：上元用阳遁5局，中元用阳遁2局，下元用阳遁8局
            put("立夏", Arrays.asList(4, 1, 7)); // 立夏：上元用阳遁4局，中元用阳遁1局，下元用阳遁7局
            put("小满", Arrays.asList(5, 2, 8)); // 小满：上元用阳遁5局，中元用阳遁2局，下元用阳遁8局
            put("芒种", Arrays.asList(6, 3, 9)); // 芒种：上元用阳遁6局，中元用阳遁3局，下元用阳遁9局
            put("夏至", Arrays.asList(9, 3, 6)); // 夏至：上元用阴遁9局，中元用阴遁3局，下元用阴遁6局
            put("小暑", Arrays.asList(8, 2, 5)); // 小暑：上元用阴遁8局，中元用阴遁2局，下元用阴遁5局
            put("大暑", Arrays.asList(7, 1, 4)); // 大暑：上元用阴遁7局，中元用阴遁1局，下元用阴遁4局
            put("立秋", Arrays.asList(2, 5, 8)); // 立秋：上元用阴遁2局，中元用阴遁5局，下元用阴遁8局
            put("处暑", Arrays.asList(1, 4, 7)); // 处暑：上元用阴遁1局，中元用阴遁4局，下元用阴遁7局
            put("白露", Arrays.asList(9, 3, 6)); // 白露：上元用阴遁9局，中元用阴遁3局，下元用阴遁6局
            put("秋分", Arrays.asList(7, 1, 4)); // 秋分：上元用阴遁7局，中元用阴遁1局，下元用阴遁4局
            put("寒露", Arrays.asList(6, 9, 3)); // 寒露：上元用阴遁6局，中元用阴遁9局，下元用阴遁3局
            put("霜降", Arrays.asList(5, 8, 2)); // 霜降：上元用阴遁5局，中元用阴遁8局，下元用阴遁2局
            put("立冬", Arrays.asList(6, 9, 3)); // 立冬：上元用阴遁6局，中元用阴遁9局，下元用阴遁3局
            put("小雪", Arrays.asList(5, 8, 2)); // 小雪：上元用阴遁5局，中元用阴遁8局，下元用阴遁2局
            put("大雪", Arrays.asList(4, 7, 1)); // 大雪：上元用阴遁4局，中元用阴遁7局，下元用阴遁1局
        }
    };

    /**
     * 六十甲子对应的旬首及仪仗（六十甲子为键）
     */
    public static final Map<String, List<String>> SIX_JIA_ZI_XUN_SHOU_AND_YI_ZHANG = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("甲子", Arrays.asList("甲子", "戊"));
            put("甲戌", Arrays.asList("甲戌", "己"));
            put("甲申", Arrays.asList("甲申", "庚"));
            put("甲午", Arrays.asList("甲午", "辛"));
            put("甲辰", Arrays.asList("甲辰", "壬"));
            put("甲寅", Arrays.asList("甲寅", "癸"));
            put("乙丑", Arrays.asList("甲子", "戊"));
            put("乙亥", Arrays.asList("甲戌", "己"));
            put("乙酉", Arrays.asList("甲申", "庚"));
            put("乙未", Arrays.asList("甲午", "辛"));
            put("乙巳", Arrays.asList("甲辰", "壬"));
            put("乙卯", Arrays.asList("甲寅", "癸"));
            put("丙寅", Arrays.asList("甲子", "戊"));
            put("丙子", Arrays.asList("甲戌", "己"));
            put("丙戌", Arrays.asList("甲申", "庚"));
            put("丙申", Arrays.asList("甲午", "辛"));
            put("丙午", Arrays.asList("甲辰", "壬"));
            put("丙辰", Arrays.asList("甲寅", "癸"));
            put("丁卯", Arrays.asList("甲子", "戊"));
            put("丁丑", Arrays.asList("甲戌", "己"));
            put("丁亥", Arrays.asList("甲申", "庚"));
            put("丁酉", Arrays.asList("甲午", "辛"));
            put("丁未", Arrays.asList("甲辰", "壬"));
            put("丁巳", Arrays.asList("甲寅", "癸"));
            put("戊辰", Arrays.asList("甲子", "戊"));
            put("戊寅", Arrays.asList("甲戌", "己"));
            put("戊子", Arrays.asList("甲申", "庚"));
            put("戊戌", Arrays.asList("甲午", "辛"));
            put("戊申", Arrays.asList("甲辰", "壬"));
            put("戊午", Arrays.asList("甲寅", "癸"));
            put("己巳", Arrays.asList("甲子", "戊"));
            put("己卯", Arrays.asList("甲戌", "己"));
            put("己丑", Arrays.asList("甲申", "庚"));
            put("己亥", Arrays.asList("甲午", "辛"));
            put("己酉", Arrays.asList("甲辰", "壬"));
            put("己未", Arrays.asList("甲寅", "癸"));
            put("庚午", Arrays.asList("甲子", "戊"));
            put("庚辰", Arrays.asList("甲戌", "己"));
            put("庚寅", Arrays.asList("甲申", "庚"));
            put("庚子", Arrays.asList("甲午", "辛"));
            put("庚戌", Arrays.asList("甲辰", "壬"));
            put("庚申", Arrays.asList("甲寅", "癸"));
            put("辛未", Arrays.asList("甲子", "戊"));
            put("辛巳", Arrays.asList("甲戌", "己"));
            put("辛卯", Arrays.asList("甲申", "庚"));
            put("辛丑", Arrays.asList("甲午", "辛"));
            put("辛亥", Arrays.asList("甲辰", "壬"));
            put("辛酉", Arrays.asList("甲寅", "癸"));
            put("壬申", Arrays.asList("甲子", "戊"));
            put("壬午", Arrays.asList("甲戌", "己"));
            put("壬辰", Arrays.asList("甲申", "庚"));
            put("壬寅", Arrays.asList("甲午", "辛"));
            put("壬子", Arrays.asList("甲辰", "壬"));
            put("壬戌", Arrays.asList("甲寅", "癸"));
            put("癸酉", Arrays.asList("甲子", "戊"));
            put("癸未", Arrays.asList("甲戌", "己"));
            put("癸巳", Arrays.asList("甲申", "庚"));
            put("癸卯", Arrays.asList("甲午", "辛"));
            put("癸丑", Arrays.asList("甲辰", "壬"));
            put("癸亥", Arrays.asList("甲寅", "癸"));
        }
    };

    /**
     * 地盘奇仪（阳遁1~9宫）
     */
    public static final Map<Integer, List<String>> DI_YANG_QI_YI = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        // 例如→ 阳遁一局：戊落坎一宫，己落坤二宫，庚落震三宫，辛落巽四宫，壬落中五宫，癸落乾六宫，丁落兑七宫，丙落艮八宫，乙落离九宫
        {
            put(1, Arrays.asList("戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙")); // 阳遁一局（1~9宫）
            put(2, Arrays.asList("乙", "戊", "己", "庚", "辛", "壬", "癸", "丁", "丙")); // 阳遁二局（1~9宫）
            put(3, Arrays.asList("丙", "乙", "戊", "己", "庚", "辛", "壬", "癸", "丁")); // 阳遁三局（1~9宫）
            put(4, Arrays.asList("丁", "丙", "乙", "戊", "己", "庚", "辛", "壬", "癸")); // 阳遁四局（1~9宫）
            put(5, Arrays.asList("癸", "丁", "丙", "乙", "戊", "己", "庚", "辛", "壬")); // 阳遁五局（1~9宫）
            put(6, Arrays.asList("壬", "癸", "丁", "丙", "乙", "戊", "己", "庚", "辛")); // 阳遁六局（1~9宫）
            put(7, Arrays.asList("辛", "壬", "癸", "丁", "丙", "乙", "戊", "己", "庚")); // 阳遁七局（1~9宫）
            put(8, Arrays.asList("庚", "辛", "壬", "癸", "丁", "丙", "乙", "戊", "己")); // 阳遁八局（1~9宫）
            put(9, Arrays.asList("己", "庚", "辛", "壬", "癸", "丁", "丙", "乙", "戊")); // 阳遁九局（1~9宫）
        }
    };

    /**
     * 地盘奇仪（阴遁1~9宫）
     */
    public static final Map<Integer, List<String>> DI_YIN_QI_YI = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        // 例如→ 阴遁一局：戊落坎一宫，乙落坤二宫，丙落震三宫，丁落巽四宫，癸落中五宫，壬落乾六宫，辛落兑七宫，庚落艮八宫，己落离九宫
        {
            put(1, Arrays.asList("戊", "乙", "丙", "丁", "癸", "壬", "辛", "庚", "己")); // 阴遁一局（1~9宫）
            put(2, Arrays.asList("己", "戊", "乙", "丙", "丁", "癸", "壬", "辛", "庚")); // 阴遁二局（1~9宫）
            put(3, Arrays.asList("庚", "己", "戊", "乙", "丙", "丁", "癸", "壬", "辛")); // 阴遁三局（1~9宫）
            put(4, Arrays.asList("辛", "庚", "己", "戊", "乙", "丙", "丁", "癸", "壬")); // 阴遁四局（1~9宫）
            put(5, Arrays.asList("壬", "辛", "庚", "己", "戊", "乙", "丙", "丁", "癸")); // 阴遁五局（1~9宫）
            put(6, Arrays.asList("癸", "壬", "辛", "庚", "己", "戊", "乙", "丙", "丁")); // 阴遁六局（1~9宫）
            put(7, Arrays.asList("丁", "癸", "壬", "辛", "庚", "己", "戊", "乙", "丙")); // 阴遁七局（1~9宫）
            put(8, Arrays.asList("丙", "丁", "癸", "壬", "辛", "庚", "己", "戊", "乙")); // 阴遁八局（1~9宫）
            put(9, Arrays.asList("乙", "丙", "丁", "癸", "壬", "辛", "庚", "己", "戊")); // 阴遁九局（1~9宫）
        }
    };

    /**
     * 地盘六甲（阳遁1~9宫）
     */
    public static final Map<Integer, List<String>> DI_YANG_LIU_JIA = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        // 例如→ 阳遁一局：甲子隐坎一宫，甲戌隐坤二宫，甲申隐震三宫，甲午隐巽四宫，甲辰隐中五宫，甲寅隐乾六宫。
        {
            put(1, Arrays.asList("甲子", "甲戌", "甲申", "甲午", "甲辰", "甲寅", "", "", "")); // 阳遁一局（1~9宫）
            put(2, Arrays.asList("", "甲子", "甲戌", "甲申", "甲午", "甲辰", "甲寅", "", "")); // 阳遁二局（1~9宫）
            put(3, Arrays.asList("", "", "甲子", "甲戌", "甲申", "甲午", "甲辰", "甲寅", "")); // 阳遁三局（1~9宫）
            put(4, Arrays.asList("", "", "", "甲子", "甲戌", "甲申", "甲午", "甲辰", "甲寅")); // 阳遁四局（1~9宫）
            put(5, Arrays.asList("甲寅", "", "", "", "甲子", "甲戌", "甲申", "甲午", "甲辰")); // 阳遁五局（1~9宫）
            put(6, Arrays.asList("甲辰", "甲寅", "", "", "", "甲子", "甲戌", "甲申", "甲午")); // 阳遁六局（1~9宫）
            put(7, Arrays.asList("甲午", "甲辰", "甲寅", "", "", "", "甲子", "甲戌", "甲申")); // 阳遁七局（1~9宫）
            put(8, Arrays.asList("甲申", "甲午", "甲辰", "甲寅", "", "", "", "甲子", "甲戌")); // 阳遁八局（1~9宫）
            put(9, Arrays.asList("甲戌", "甲申", "甲午", "甲辰", "甲寅", "", "", "", "甲子")); // 阳遁九局（1~9宫）
        }
    };

    /**
     * 地盘六甲（阴遁1~9宫）
     */
    public static final Map<Integer, List<String>> DI_YIN_LIU_JIA = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        // 例如→ 阴遁一局：甲子隐坎一宫，甲戌隐离九宫，甲申隐艮八宫，甲午隐兑七宫，甲辰隐乾六宫，甲寅隐中五宫。
        {
            put(1, Arrays.asList("甲子", "", "", "", "甲寅", "甲辰", "甲午", "甲申", "甲戌")); // 阴遁一局（1~9宫）
            put(2, Arrays.asList("甲戌", "甲子", "", "", "", "甲寅", "甲辰", "甲午", "甲申")); // 阴遁二局（1~9宫）
            put(3, Arrays.asList("甲申", "甲戌", "甲子", "", "", "", "甲寅", "甲辰", "甲午")); // 阴遁三局（1~9宫）
            put(4, Arrays.asList("甲午", "甲申", "甲戌", "甲子", "", "", "", "甲寅", "甲辰")); // 阴遁四局（1~9宫）
            put(5, Arrays.asList("甲辰", "甲午", "甲申", "甲戌", "甲子", "", "", "", "甲寅")); // 阴遁五局（1~9宫）
            put(6, Arrays.asList("甲寅", "甲辰", "甲午", "甲申", "甲戌", "甲子", "", "", "")); // 阴遁六局（1~9宫）
            put(7, Arrays.asList("", "甲寅", "甲辰", "甲午", "甲申", "甲戌", "甲子", "", "")); // 阴遁七局（1~9宫）
            put(8, Arrays.asList("", "", "甲寅", "甲辰", "甲午", "甲申", "甲戌", "甲子", "")); // 阴遁八局（1~9宫）
            put(9, Arrays.asList("", "", "", "甲寅", "甲辰", "甲午", "甲申", "甲戌", "甲子")); // 阴遁九局（1~9宫）
        }
    };

    /**
     * 根据二十四节气获取八门
     */
    public static final Map<Integer, List<String>> IS_BA_MEN = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put(0, Arrays.asList("冬至", "小寒", "大寒")); // 冬至、小寒、大寒：休门
            put(1, Arrays.asList("立春", "雨水", "惊蛰")); // 立春、雨水、惊蛰：生门
            put(2, Arrays.asList("春分", "清明", "谷雨")); // 春分、清明、谷雨：伤门
            put(3, Arrays.asList("立夏", "小满", "芒种")); // 立夏、小满、芒种：杜门
            put(4, Arrays.asList("夏至", "小暑", "大暑")); // 夏至、小暑、大暑：景门
            put(5, Arrays.asList("立秋", "处暑", "白露")); // 立秋、处暑、白露：死门
            put(6, Arrays.asList("秋分", "寒露", "霜降")); // 秋分、寒露、霜降：惊门
            put(7, Arrays.asList("立冬", "小雪", "大雪")); // 立冬、小雪、大雪：开门
        }
    };

    /**
     * 六甲旬空
     */
    public static final Map<String, List<String>> LIU_JIA_XUN_KONG = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        /*
            甲子旬戌亥空，甲戌旬申酉空；
            甲申旬午未空，甲午旬辰巳空；
            甲辰旬寅卯空，甲寅旬子丑空。

            ☞ 注：忌神落空则为喜、喜神落空则为凶
         */ {
            put("甲子", Arrays.asList("戌", "亥"));
            put("甲戌", Arrays.asList("申", "酉"));
            put("甲申", Arrays.asList("午", "未"));
            put("甲午", Arrays.asList("辰", "巳"));
            put("甲辰", Arrays.asList("寅", "卯"));
            put("甲寅", Arrays.asList("子", "丑"));
        }
    };

    /**
     * 六甲旬空落宫
     */
    public static final Map<List<String>, List<Integer>> LIU_JIA_XUN_KONG_GONG = new HashMap<List<String>, List<Integer>>() {
        private static final long serialVersionUID = -1;

        {
            put(Arrays.asList("戌", "亥"), Collections.singletonList(6));
            put(Arrays.asList("申", "酉"), Arrays.asList(2, 7));
            put(Arrays.asList("午", "未"), Arrays.asList(9, 2));
            put(Arrays.asList("辰", "巳"), Collections.singletonList(4));
            put(Arrays.asList("寅", "卯"), Arrays.asList(8, 3));
            put(Arrays.asList("子", "丑"), Arrays.asList(1, 8));
        }
    };

    /**
     * 驿马
     */
    public static final Map<String, String> YI_MA = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        /* 根据时支判断→ 申子辰马在寅，寅午戌马在申，巳酉丑马在亥，亥卯未马在巳 */ {
            put("申", "寅"); // 申：马在寅
            put("子", "寅"); // 子：马在寅
            put("辰", "寅"); // 辰：马在寅
            put("寅", "申"); // 寅：马在申
            put("午", "申"); // 午：马在申
            put("戌", "申"); // 戌：马在申
            put("巳", "亥"); // 巳：马在亥
            put("酉", "亥"); // 酉：马在亥
            put("丑", "亥"); // 丑：马在亥
            put("亥", "巳"); // 亥：马在巳
            put("卯", "巳"); // 卯：马在巳
            put("未", "巳"); // 未：马在巳
        }
    };

    /**
     * 驿马落宫
     */
    public static final Map<String, Integer> YI_MA_GONG = new HashMap<String, Integer>() {
        private static final long serialVersionUID = -1;

        /* 根据时支判断→ 寅马在艮八宫，申马在坤二宫，巳马在巽四宫，亥马在乾六宫 */ {
            put("寅", 8); // 寅：马在艮八宫
            put("申", 2); // 申：马在坤二宫
            put("巳", 4); // 巳：马在巽四宫
            put("亥", 6); // 亥：马在乾六宫
        }
    };

    /**
     * 九星原始宫位（1~9宫）
     */
    public static final String[] JIU_XING_INITIAL = {"天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"};

    /**
     * 九星原始宫位（1~9宫）
     */
    public static final Map<String, Integer> JIU_XING_INITIAL2 = new HashMap<String, Integer>() {
        private static final long serialVersionUID = -1;

        {
            put("天蓬", 1); // 天蓬：坎一宫
            put("天芮", 2); // 天芮：坤二宫
            put("天冲", 3); // 天冲：震三宫
            put("天辅", 4); // 天辅：巽四宫
            put("天禽", 5); // 天禽：中五宫（寄二宫）
            put("天心", 6); // 天心：乾六宫
            put("天柱", 7); // 天柱：兑七宫
            put("天任", 8); // 天任：艮八宫
            put("天英", 9); // 天英：离九宫
        }
    };

    /**
     * 九星位置（顺转九宫）
     */
    public static final Map<Integer, List<String>> JIU_XING_SHUN = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put(0, Arrays.asList("天蓬", "天芮", "天冲", "天辅", "", "天心", "天柱", "天任", "天英")); // 天蓬星落坎一宫
            put(1, Arrays.asList("天辅", "天蓬", "天芮", "天柱", "", "天冲", "天任", "天英", "天心")); // 天蓬星落坤二宫
            put(2, Arrays.asList("天柱", "天辅", "天蓬", "天任", "", "天芮", "天英", "天心", "天冲")); // 天蓬星落朕三宫
            put(3, Arrays.asList("天芮", "天冲", "天心", "天蓬", "", "天英", "天辅", "天柱", "天任")); // 天蓬星落巽四宫
            put(4, Arrays.asList("天任", "天柱", "天辅", "天英", "", "天蓬", "天心", "天冲", "天芮")); // 天蓬星落乾六宫
            put(5, Arrays.asList("天冲", "天心", "天英", "天芮", "", "天任", "天蓬", "天辅", "天柱")); // 天蓬星落兑七宫
            put(6, Arrays.asList("天心", "天英", "天任", "天冲", "", "天柱", "天芮", "天蓬", "天辅")); // 天蓬星落艮八宫
            put(7, Arrays.asList("天英", "天任", "天柱", "天心", "", "天辅", "天冲", "天芮", "天蓬")); // 天蓬星落离九宫
        }
    };

    /**
     * 八门原始宫位（1~9宫）
     */
    public static final String[] BA_MEN_INITIAL = {"休门", "死门", "伤门", "杜门", "", "开门", "惊门", "生门", "景门"};

    /**
     * 八门位置（顺转九宫）
     */
    public static final Map<Integer, List<String>> BA_MEN_SHUN_ZHUAN = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put(0, Arrays.asList("休门", "死门", "伤门", "杜门", "", "开门", "惊门", "生门", "景门")); // 休门落坎一宫
            put(1, Arrays.asList("杜门", "休门", "死门", "惊门", "", "伤门", "生门", "景门", "开门")); // 休门落坤二宫
            put(2, Arrays.asList("惊门", "杜门", "休门", "生门", "", "死门", "景门", "开门", "伤门")); // 休门落震三宫
            put(3, Arrays.asList("死门", "伤门", "开门", "休门", "", "景门", "杜门", "惊门", "生门")); // 休门落巽四宫
            put(4, Arrays.asList("杜门", "休门", "死门", "惊门", "", "伤门", "生门", "景门", "开门")); // 休门落中五宫（按坤二宫计算）
            put(5, Arrays.asList("生门", "惊门", "杜门", "景门", "", "休门", "开门", "伤门", "死门")); // 休门落乾六宫
            put(6, Arrays.asList("伤门", "开门", "景门", "死门", "", "生门", "休门", "杜门", "惊门")); // 休门落兑七宫
            put(7, Arrays.asList("开门", "景门", "生门", "伤门", "", "惊门", "死门", "休门", "杜门")); // 休门落艮八宫
            put(8, Arrays.asList("景门", "生门", "惊门", "开门", "", "杜门", "伤门", "死门", "休门")); // 休门落离九宫
        }
    };

    /**
     * 八神位置（顺转九宫）
     */
    public static final Map<Integer, List<String>> BA_SHEN_SHUN_ZHUAN = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put(1, Arrays.asList("值符", "玄武", "太阴", "六合", "", "九天", "九地", "螣蛇", "白虎")); // 大值符旋转后落坎一宫
            put(2, Arrays.asList("六合", "值符", "玄武", "九地", "", "太阴", "螣蛇", "白虎", "九天")); // 大值符旋转后落坤二宫
            put(3, Arrays.asList("九地", "六合", "值符", "螣蛇", "", "玄武", "白虎", "九天", "太阴")); // 大值符旋转后落震三宫
            put(4, Arrays.asList("玄武", "太阴", "九天", "值符", "", "白虎", "六合", "九地", "螣蛇")); // 大值符旋转后落巽四宫
            put(5, Arrays.asList("六合", "值符", "玄武", "九地", "", "太阴", "螣蛇", "白虎", "九天")); // 五宫寄二宫
            put(6, Arrays.asList("螣蛇", "九地", "六合", "白虎", "", "值符", "九天", "太阴", "玄武")); // 大值符旋转后落乾六宫
            put(7, Arrays.asList("太阴", "九天", "白虎", "玄武", "", "螣蛇", "值符", "六合", "九地")); // 大值符旋转后落兑七宫
            put(8, Arrays.asList("九天", "白虎", "螣蛇", "太阴", "", "九地", "玄武", "值符", "六合")); // 大值符旋转后落艮八宫
            put(9, Arrays.asList("白虎", "螣蛇", "九地", "九天", "", "六合", "太阴", "玄武", "值符")); // 大值符旋转后落离九宫
        }
    };

    /**
     * 八神位置（逆转九宫）
     */
    public static final Map<Integer, List<String>> BA_SHEN_NI_ZHUAN = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put(1, Arrays.asList("值符", "六合", "九地", "玄武", "", "螣蛇", "太阴", "九天", "白虎")); // 大值符旋转后落坎一宫
            put(2, Arrays.asList("玄武", "值符", "六合", "太阴", "", "九地", "九天", "白虎", "螣蛇")); // 大值符旋转后落坤二宫
            put(3, Arrays.asList("太阴", "玄武", "值符", "九天", "", "六合", "白虎", "螣蛇", "九地")); // 大值符旋转后落震三宫
            put(4, Arrays.asList("六合", "九地", "螣蛇", "值符", "", "白虎", "玄武", "太阴", "九天")); // 大值符旋转后落巽四宫
            put(5, Arrays.asList("玄武", "值符", "六合", "太阴", "", "九地", "九天", "白虎", "螣蛇")); // 五宫寄二宫
            put(6, Arrays.asList("九天", "太阴", "玄武", "白虎", "", "值符", "螣蛇", "九地", "六合")); // 大值符旋转后落乾六宫
            put(7, Arrays.asList("九地", "螣蛇", "白虎", "六合", "", "九天", "值符", "玄武", "太阴")); // 大值符旋转后落兑七宫
            put(8, Arrays.asList("螣蛇", "白虎", "九天", "九地", "", "太阴", "六合", "值符", "玄武")); // 大值符旋转后落艮八宫
            put(9, Arrays.asList("白虎", "九天", "太阴", "螣蛇", "", "玄武", "九地", "六合", "值符")); // 大值符旋转后落离九宫
        }
    };

    /**
     * 八神吉凶
     */
    public static final Map<String, String> BA_SHEN_JI_XIONG = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("值符", "吉");
            put("螣蛇", "凶");
            put("太阴", "吉");
            put("六合", "吉");
            put("白虎", "凶");
            put("玄武", "凶");
            put("九地", "吉");
            put("九天", "吉");
        }
    };

    /**
     * 十干克应
     */
    public static final Map<List<String>, List<String>> SHI_GAN_KE_YING = new HashMap<List<String>, List<String>>() {
        private static final long serialVersionUID = -1;

        /*
            十干克应：天盘天干和地盘天干相遇后的各种克应关系。

                1、奇门遁甲将甲隐遁起来，其余九干又分成三奇和六仪，所以也就是奇仪之间的克应关系；
                2、即天盘[乙、丙、丁、戊、己、庚、辛、壬、癸]和地盘[乙、丙、丁、戊、己、庚、辛、壬、癸]相遇后的各种关系。
        */ {
            // 例如→ 天盘乙奇+地盘乙奇（日奇伏吟）：宜安分守已、积粮藏宝、莳花种果等；不宜见上层领导、贵人、求名求利等。
            put(Arrays.asList("乙", "乙"), Arrays.asList("日奇伏吟", "宜静宜守、不利谒贵、不利求名。注解：宜安分守已、积粮藏宝、莳花种果等；不宜见上层领导、贵人、求名求利等。"));
            put(Arrays.asList("乙", "丙"), Arrays.asList("奇仪顺遂", "吉星升迁、凶星离别、红杏出墙。注解：吉星迁官晋职，凶星夫妻反目离别。"));
            put(Arrays.asList("乙", "丁"), Arrays.asList("奇仪相佐", "文书事吉、利于合作、百事可为。注解：最利文书、考试，百事可为。"));
            put(Arrays.asList("乙", "戊"), Arrays.asList("阴害阳门", "门凶墓迫、破财伤人、不利公开。注解：利于阴人、阴事，不利阳人、阳事，得门吉尚可谋为，得门凶、门迫则破财伤人。"));
            put(Arrays.asList("乙", "己"), Arrays.asList("日奇入墓", "被土暗昧、门凶事凶、门吉有救。注解：门凶事必凶，得生、开二吉门为地遁。"));
            put(Arrays.asList("乙", "庚"), Arrays.asList("日奇被刑", "争讼财产、夫妻怀私、未婚同居。注解：为争讼财产，夫妻怀有私意。"));
            put(Arrays.asList("乙", "辛"), Arrays.asList("青龙逃走", "奴仆拐带、六畜皆伤、女人弃婚。注解：此时不宜举兵，主将士逃窜，临阵败亡，所谋百事皆凶，财利倾覆，身遭残毁；通常代表君子主动离开恶劣环境、人才流失、人才出走、君子遭遇困境、险境而主动逃离等。测婚一般主女方先提出离婚。"));
            put(Arrays.asList("乙", "壬"), Arrays.asList("日奇入地", "尊卑悖乱、官灾是非、有人谋害。注解：尊卑悖乱，官讼是非，有人谋害之事。"));
            put(Arrays.asList("乙", "癸"), Arrays.asList("华盖逢星", "遁迹隐形、躲灾避难、退吉进凶。注解：遁迹修道，隐匿藏形，躲灾避难为吉。"));
            put(Arrays.asList("丙", "乙"), Arrays.asList("日月并行", "阴阳得位、刚柔结合、谋为皆吉。注解：公谋私为皆吉。"));
            put(Arrays.asList("丙", "丙"), Arrays.asList("月奇悖师", "文书逼迫、票据文章、破耗遗失。注解：文书逼迫，破耗遗失，主单据票证不明遗失。"));
            put(Arrays.asList("丙", "丁"), Arrays.asList("星奇朱雀", "文书吉利、常人宜静、炎症病变。注解：贵人文书吉利，常人平静安乐，得三吉门为天遁。"));
            put(Arrays.asList("丙", "戊"), Arrays.asList("飞鸟跌穴", "谋为洞彻、迫墓击刑、减吉至凶。注解：百事吉，事业可为，可谋大事。"));
            put(Arrays.asList("丙", "己"), Arrays.asList("大悖入刑", "囚人刑杖、文书不行、吉凶看门。注解：坐监牢，被杖责，文书公文不能传递，得吉门则吉，得凶门则转吉为凶。"));
            put(Arrays.asList("丙", "庚"), Arrays.asList("萤入太白", "门户破财、盗耗遗失、贼病皆去。注解：门户破败，盗贼耗失，事业亦凶；火入金乡贼即去。"));
            put(Arrays.asList("丙", "辛"), Arrays.asList("丙辛相和", "凶象被合、谋事成就、病人不凶。注解：故谋事能成，为疾病人不凶。"));
            put(Arrays.asList("丙", "壬"), Arrays.asList("火入天罗", "为客不利、是非颇多、越来越乱。注解：为客不利，是非颇多。"));
            put(Arrays.asList("丙", "癸"), Arrays.asList("华盖悖师", "暗昧不明、阴人害事、灾祸颇多。注解：阴人害事，灾祸频生。"));
            put(Arrays.asList("丁", "乙"), Arrays.asList("人遁吉格", "加官进禄、婚姻财喜、利于文章。注解：贵人加官晋爵，常人婚姻财帛有喜。"));
            put(Arrays.asList("丁", "丙"), Arrays.asList("星随月转", "小人得志、贵人高升、常人生悲。注解：贵人越级高升，常人乐极生悲；需忍耐，否则会因小失大而不幸。"));
            put(Arrays.asList("丁", "丁"), Arrays.asList("星奇伏吟", "文书即至、喜事遂心、万事如意。注解：文书证件即至，喜事从心，万事如意。"));
            put(Arrays.asList("丁", "戊"), Arrays.asList("青龙转光", "官人升迁、常人威昌、利婚求学。注解：官人升迁，常人威昌。"));
            put(Arrays.asList("丁", "己"), Arrays.asList("火入勾陈", "奸私仇冤、事因女人、谋为不利。注解：奸私仇怨，事因女人。"));
            put(Arrays.asList("丁", "庚"), Arrays.asList("文书阻隔", "文书阻隔、消息不通、行人必归。注解：行人必归。"));
            put(Arrays.asList("丁", "辛"), Arrays.asList("朱雀入狱", "罪人释囚、官人失位、牢狱之灾。注解：罪人释囚，官人失位。"));
            put(Arrays.asList("丁", "壬"), Arrays.asList("丁壬相合", "凡事能成、贵人辅助、测婚苟合。注解：主贵人恩诏，讼狱公平，测婚多为苟合。"));
            put(Arrays.asList("丁", "癸"), Arrays.asList("朱雀投江", "文书口舌、音信沉溺、官府词讼。注解：文书口舌是非，惊动官府，词讼不利，音信沉溺不到。"));
            put(Arrays.asList("戊", "乙"), Arrays.asList("甲乙会和", "有贵人助、合主病多、吉凶看门。注解：又名青龙会和，门吉事吉，门凶事凶。"));
            put(Arrays.asList("戊", "丙"), Arrays.asList("青龙返首", "大吉大利、墓迫击刑、吉事成凶。注解：为事所谋，大吉大利，若逢迫墓击邢，吉事也凶。"));
            put(Arrays.asList("戊", "丁"), Arrays.asList("青龙耀明", "谒贵求名、墓迫击刑、减吉至凶。注解：谒贵求名吉利，若值墓、迫，惹是生非。"));
            put(Arrays.asList("戊", "戊"), Arrays.asList("青龙伏吟", "凡事闭塞、静守为吉、六甲可谋。注解：各谓伏吟，凡事不利，道路闭塞，以守为好。"));
            put(Arrays.asList("戊", "己"), Arrays.asList("贵人入狱", "公私不利、冲出墓库、方有转机。注解：公司皆不利。"));
            put(Arrays.asList("戊", "庚"), Arrays.asList("值符飞宫", "吉事不吉、凶事更凶、移换逃迁。注解：吉事不吉，凶事更凶，求财没利益，测病也主凶，同时甲庚相冲，也主换地方。"));
            put(Arrays.asList("戊", "辛"), Arrays.asList("青龙折足", "吉门可谋、凶门灾破、足疾折伤。注解：子午相冲，吉门有生助，尚能谋事，若逢凶门，则招灾、失财或有足疾、折伤。"));
            put(Arrays.asList("戊", "壬"), Arrays.asList("青龙天牢", "诸事不利、投资亏本、测病主凶。注解：凡阴阳事皆不吉利。"));
            put(Arrays.asList("戊", "癸"), Arrays.asList("青龙华盖", "为利而合、事有合绊、吉凶看门。注解：甲为青龙，癸为天网，逢吉门为吉，可招福临门，逢凶门事多不利，为凶。"));
            put(Arrays.asList("己", "乙"), Arrays.asList("墓神不明", "墓神不明、遁迹隐形、前途渺茫。注解：地户逢星，宜遁迹隐形为吉利。"));
            put(Arrays.asList("己", "丙"), Arrays.asList("火悖地户", "男被冤害、女被淫污、感情出轨。注解：男人冤冤相害，女人必致淫污。"));
            put(Arrays.asList("己", "丁"), Arrays.asList("朱雀入墓", "文书词讼、先曲后直、拨云见日。注解：文书词讼，先曲后直。"));
            put(Arrays.asList("己", "戊"), Arrays.asList("犬遇青龙", "门吉可谋、门凶徒劳、吉凶看门。注解：门吉为谋望遂意，上人见喜，若门凶，枉费心机。"));
            put(Arrays.asList("己", "己"), Arrays.asList("地户逢鬼", "病者必死、百事不遂、不可谋为。注解：病者发凶或必死，百事不遂，暂不谋为，谋为则凶。"));
            put(Arrays.asList("己", "庚"), Arrays.asList("刑格返名", "谋为徒劳、先动不利、谨防谋害。注解：词讼先动者不利，如临阴星则有谋害之情。"));
            put(Arrays.asList("己", "辛"), Arrays.asList("游魂入墓", "人鬼相侵、鬼魅作祟、凡事谨慎。注解：易遭阴邪鬼魅作祟。"));
            put(Arrays.asList("己", "壬"), Arrays.asList("地网高张", "狡童佚女、奸情伤杀、事多变动。注解：狡童佚女，奸情伤杀，凶。"));
            put(Arrays.asList("己", "癸"), Arrays.asList("地刑玄武", "疾病垂危、囚狱词讼、事关私欲。注解：男女疾病垂危，有囚狱词讼之灾。"));
            put(Arrays.asList("庚", "乙"), Arrays.asList("太白逢星", "流连牵绊、退吉进凶、夫妻不和。注解：退吉进凶，谋为不利。"));
            put(Arrays.asList("庚", "丙"), Arrays.asList("太白入萤", "占贼必来、为客进利、为主破财。注解：占贼贼必来，须防贼来偷营。宜于西北方伏击之。以固守为吉。为客进利，为主破财。"));
            put(Arrays.asList("庚", "丁"), Arrays.asList("亭亭之格", "婚外有情、私匿官司、门吉有救。注解：因私匿或男女关系起官司是非，门吉有救，门凶事必凶。"));
            put(Arrays.asList("庚", "戊"), Arrays.asList("天乙伏宫", "破财伤人、不利合作、百事皆凶。注解：百事不可谋，大凶。"));
            put(Arrays.asList("庚", "己"), Arrays.asList("官符刑格", "私欲伤害、官讼判刑、主客不利。注解：主有官司口舌，因官讼被判刑，住牢狱更凶。"));
            put(Arrays.asList("庚", "庚"), Arrays.asList("太白同宫", "官灾横祸、兄弟不和、变动争财。注解：又名战格，官灾横祸，兄弟或同辈朋友相冲撞，不利为事。"));
            put(Arrays.asList("庚", "辛"), Arrays.asList("白虎干格", "远行不利、车折马死、诸事灾殃。注解：不宜远行，远行车折马伤，求财更为大凶。"));
            put(Arrays.asList("庚", "壬"), Arrays.asList("移荡之格", "远行迷失、音信皆阻、多主变动。注解：远行道路迷失，男女音信难通。"));
            put(Arrays.asList("庚", "癸"), Arrays.asList("反吟大格", "行人不至、官司破财、生产皆伤。注解：多主车祸，行人不至，官事不止，生育母子俱伤，大凶。"));
            put(Arrays.asList("辛", "乙"), Arrays.asList("白虎猖狂", "家破人亡、远行多殃、男人弃婚。注解：家败人亡，远行多遭殃；测婚离散，主因男人。"));
            put(Arrays.asList("辛", "丙"), Arrays.asList("干合悖师", "合中有乱、因财致讼、吉凶看门。注解：门吉则事吉，门凶事凶，测事易因财物致讼。"));
            put(Arrays.asList("辛", "丁"), Arrays.asList("狱神得奇", "经商倍利、囚人赦免、意外收获。注解：经商求财获利百倍，囚人逢天赦释免。"));
            put(Arrays.asList("辛", "戊"), Arrays.asList("困龙被伤", "屈抑守分、妄动祸殃、官司破财。注解：主官司破财，屈抑守分尚可，妄动则带来灾祸。"));
            put(Arrays.asList("辛", "己"), Arrays.asList("入狱自刑", "奴仆背主、狱讼难伸、自错破财。注解：奴仆背主，有苦诉讼难伸。"));
            put(Arrays.asList("辛", "庚"), Arrays.asList("白虎出力", "主客相残、强进血衫、退避尚可。注解：刀刃相交，主客相残，逊让退步稍可，强进血溅衣衫。"));
            put(Arrays.asList("辛", "辛"), Arrays.asList("伏吟天庭", "公废私就、讼狱由己、自罹罪名。注解：伏吟天庭，公废私就，讼狱自罹罪名。"));
            put(Arrays.asList("辛", "壬"), Arrays.asList("凶蛇入狱", "两男争女、讼狱不息、先动失理。注解：两男争女，讼狱不息，先动失理。"));
            put(Arrays.asList("辛", "癸"), Arrays.asList("天牢华盖", "日月失明、误入天网、动辄乖张。注解：日月失明，误入天网，动止乖张。"));
            put(Arrays.asList("壬", "乙"), Arrays.asList("小蛇得势", "女子温柔、男子发达、占孕生子。注解：女人柔顺，男人通达，测孕育生子，禄马光荣。"));
            put(Arrays.asList("壬", "丙"), Arrays.asList("水蛇入火", "官灾刑禁、络绎不绝、两败俱伤。注解：主官灾刑禁，络绎不绝。"));
            put(Arrays.asList("壬", "丁"), Arrays.asList("干合蛇刑", "文书牵连、贵人匆匆、男吉女凶。注解：文书牵连，贵人匆匆，男吉女凶。"));
            put(Arrays.asList("壬", "戊"), Arrays.asList("小蛇化龙", "升迁得势、男人发达、女产婴童。注解：男人发达，女人产婴童。"));
            put(Arrays.asList("壬", "己"), Arrays.asList("反吟蛇刑", "官司败诉、大祸将至、顺守可吉。注解：主官讼败诉，大祸将至，顺守可吉，妄动必灾。"));
            put(Arrays.asList("壬", "庚"), Arrays.asList("太白擒蛇", "难以发展、刑狱公平、立判邪正。注解：刑狱公平，立部刑正。"));
            put(Arrays.asList("壬", "辛"), Arrays.asList("腾蛇相缠", "琐事缠绕、动荡不安、被人欺瞒。注解：纵得吉门，亦不能安宁，若有谋望，被人欺瞒。"));
            put(Arrays.asList("壬", "壬"), Arrays.asList("蛇入地罗", "求谋无成、内起祸患、诸事破败。注解：外人缠绕，内事索索，吉门吉星，庶免蹉跎。"));
            put(Arrays.asList("壬", "癸"), Arrays.asList("幼女奸淫", "奸私隐情、家丑外扬、测婚乱搞。注解：主有家丑外扬之事发生，门吉星凶，易反福为祸。"));
            put(Arrays.asList("癸", "乙"), Arrays.asList("华盖逢星", "贵人禄位、常人平安、吉凶看门。注解：贵人禄位，常人平安，门吉则吉，门凶则凶。"));
            put(Arrays.asList("癸", "丙"), Arrays.asList("华盖悖师", "贵贱不利、因势利导、反凶为吉。注解：贵贱逢之皆不利，惟上人见喜。"));
            put(Arrays.asList("癸", "丁"), Arrays.asList("螣蛇夭矫", "口舌是非、文书官司、火焚难逃。注解：文书官司，火焚也难逃。"));
            put(Arrays.asList("癸", "戊"), Arrays.asList("天乙会和", "婚姻财喜、合作投资、吉门可行。注解：吉门易求财，婚姻喜美，吉人赞助成合；门凶迫制，反祸官非。"));
            put(Arrays.asList("癸", "己"), Arrays.asList("华盖地户", "阴阳不和、音信皆阻、躲避为吉。注解：男女测之，音信皆阻，此格宜躲灾避难方为吉。"));
            put(Arrays.asList("癸", "庚"), Arrays.asList("太白入网", "吉事成空、暴力争讼、自罹罪责。注解：主以暴力争讼，自罹罪责。"));
            put(Arrays.asList("癸", "辛"), Arrays.asList("网盖天牢", "官司败诉、死罪难逃、测病大凶。注解：主官司败讼，死罪难逃，测病亦大凶。"));
            put(Arrays.asList("癸", "壬"), Arrays.asList("复见螣蛇", "嫁娶重婚、后嫁无子、不保年华。注解：主嫁娶重婚，后嫁无子，不保年华。"));
            put(Arrays.asList("癸", "癸"), Arrays.asList("天网四张", "行人失伴、病讼皆伤、不可谋为。注解：主行人失伴，病讼皆伤。"));
        }
    };

    /**
     * 八门克应
     */
    public static final Map<List<String>, String> BA_MEN_KE_YING = new HashMap<List<String>, String>() {
        private static final long serialVersionUID = -1;

        /*
            八门克应：人盘八门与地盘八门、地盘奇仪、天盘奇仪的生克制化关系。

                1、休门：休门最好娶资财，牛马猪羊自送来。外口婚姻南方应，迁宫进职坐京台。定进羽音入产业，居家安庆永无灾。
                2、生门：生门临着土星辰，人旺畜孳每称情。子丑年中三七月，黄衣捧笏到门庭。蚕丝谷帛皆丰足，朱紫儿孙守帝廷。南方商音田土地，子孙禄位至公卿。
                3、伤门：疮疼行不得，折损血财身。天灾人枉死，经年有病人。商音难得好，余事不堪闻。
                4、杜门：杜门原是木，犯者灾祸频。亥卯未年月，遭官入狱屯。生离并死别，六畜逐时瘟。落树生脓血，祸害及子孙。
                5、景门：景门主血光，官符卖田庄。祸灾应多有，子孙受苦殃。外亡并恶死，六畜也见伤。生离与死别，用者须提防。
                6、死门：死门之方最为凶，修造逢之祸必侵。犯者年年财产退，更防孝服死人丁。
                7、惊门：惊门不可论，瘟疫死人丁。辰年并酉月，非祸入门庭。
                8、开门：开门欲腹照临来，奴婢牛羊百日回。财宝进时地户入，兴隆宅舍有资财。田园招得商音送，巳酉丑年绝户来。印信子孙多拜受，经衣金带拜荣回。
         */ {
            // 例如→ 休门+休门：求财、进人口、谒贵吉，朝见、上官、修造亦大利。
            put(Arrays.asList("休门", "休门"), "求财、进人口、谒贵吉，朝见、上官、修造亦大利。");
            put(Arrays.asList("休门", "生门"), "主得阴人财物。干贵谋望，虽迟应吉。");
            put(Arrays.asList("休门", "伤门"), "主上官、吉庆，求财不得。有亲故分产。变动事不吉。");
            put(Arrays.asList("休门", "杜门"), "主破财，失物难寻。");
            put(Arrays.asList("休门", "景门"), "主求望文书印信事不至，反招口舌小凶。");
            put(Arrays.asList("休门", "死门"), "主求文书印信官司事，或僧道，远行事，不吉，占病凶。");
            put(Arrays.asList("休门", "惊门"), "主损财、招非并疾病、惊恐事。");
            put(Arrays.asList("休门", "开门"), "主开张店肆及见贵、求财、喜庆事，大吉。");
            put(Arrays.asList("休门", "乙"), "求谋重，不得；求轻，可得。");
            put(Arrays.asList("休门", "丙"), "文书和合喜庆。");
            put(Arrays.asList("休门", "丁"), "百讼休歇。");
            put(Arrays.asList("休门", "戊"), "财物和合。");
            put(Arrays.asList("休门", "己"), "暗昧不宁。");
            put(Arrays.asList("休门", "庚"), "文书词讼先结后解。");
            put(Arrays.asList("休门", "辛"), "疾病退愈，失物不得。");
            put(Arrays.asList("休门", "壬"), "阴人词讼牵连。");
            put(Arrays.asList("休门", "癸"), "阴人词讼牵连。");
            put(Arrays.asList("生门", "休门"), "主阴人处求望财利，吉。");
            put(Arrays.asList("生门", "生门"), "主远行、求财吉。");
            put(Arrays.asList("生门", "伤门"), "主亲友变动，道路不吉。");
            put(Arrays.asList("生门", "杜门"), "主阴谋，阴人破财，不利。");
            put(Arrays.asList("生门", "景门"), "主阴人、小口不宁及文书事后吉。");
            put(Arrays.asList("生门", "死门"), "主田宅官司，病主难救。");
            put(Arrays.asList("生门", "惊门"), "主尊长财产、词讼，病迟愈，吉。");
            put(Arrays.asList("生门", "开门"), "主见贵人，求财大发。");
            put(Arrays.asList("生门", "乙"), "主阴人生产迟吉。");
            put(Arrays.asList("生门", "丙"), "主贵人印绶、婚姻、书信喜事。");
            put(Arrays.asList("生门", "丁"), "主词讼、婚姻、财利大吉。");
            put(Arrays.asList("生门", "戊"), "嫁娶、求财、谒贵皆吉。");
            put(Arrays.asList("生门", "己"), "主得贵人维持吉。");
            put(Arrays.asList("生门", "庚"), "主财产争讼破产，不利。");
            put(Arrays.asList("生门", "辛"), "主官事、产妇疾病，后吉。");
            put(Arrays.asList("生门", "壬"), "主遗失财产后得，盗贼易获。");
            put(Arrays.asList("生门", "癸"), "主婚姻不成，余事皆吉。");
            put(Arrays.asList("伤门", "休门"), "主男人变动或托人办事，财名不利。");
            put(Arrays.asList("伤门", "生门"), "主房产、种植事业，凶。");
            put(Arrays.asList("伤门", "伤门"), "主变动、远得折伤，凶。");
            put(Arrays.asList("伤门", "杜门"), "主变动、失脱、官司桎梏，百事皆凶。");
            put(Arrays.asList("伤门", "景门"), "主文书印信、口舌，惹是生非。");
            put(Arrays.asList("伤门", "死门"), "主官司印信凶，出行大忌，点病凶。");
            put(Arrays.asList("伤门", "惊门"), "主亲人疾病忧惧，媒伐不利，凶。");
            put(Arrays.asList("伤门", "开门"), "主贵人开张有走失变动之事，不利。");
            put(Arrays.asList("伤门", "乙"), "主求谋不得，反防盗失财。");
            put(Arrays.asList("伤门", "丙"), "主道路损失。");
            put(Arrays.asList("伤门", "丁"), "主音信不实。");
            put(Arrays.asList("伤门", "戊"), "主失脱难获。");
            put(Arrays.asList("伤门", "己"), "主财散人亡。");
            put(Arrays.asList("伤门", "庚"), "主讼狱被刑杖，凶。");
            put(Arrays.asList("伤门", "辛"), "主夫妻怀私恣怨。");
            put(Arrays.asList("伤门", "壬"), "主因盗牵连。");
            put(Arrays.asList("伤门", "癸"), "讼狱被冤，有理难伸。");
            put(Arrays.asList("杜门", "休门"), "主求财有益。");
            put(Arrays.asList("杜门", "生门"), "主阳人小口破财及田宅，求财不利。");
            put(Arrays.asList("杜门", "伤门"), "主兄弟相争田产，破财不利。");
            put(Arrays.asList("杜门", "杜门"), "主因父母疾病，田宅出脱事，凶。");
            put(Arrays.asList("杜门", "景门"), "主文书印信阻隔，阳人小口疾病，迟疑不利。");
            put(Arrays.asList("杜门", "死门"), "主田宅文书失落，官司破财，小凶。");
            put(Arrays.asList("杜门", "惊门"), "主门户内忧疑惊恐，并有词讼事。");
            put(Arrays.asList("杜门", "开门"), "主见贵人官长，谋事主先破己财，后吉。");
            put(Arrays.asList("杜门", "乙"), "主宜暗求阳人财物，得主不明至讼。");
            put(Arrays.asList("杜门", "丙"), "主文契遗失。");
            put(Arrays.asList("杜门", "丁"), "主男人入狱。");
            put(Arrays.asList("杜门", "戊"), "主谋事不成，密处求财得。");
            put(Arrays.asList("杜门", "己"), "主私害人招非。");
            put(Arrays.asList("杜门", "庚"), "主因女人讼狱被刑。");
            put(Arrays.asList("杜门", "辛"), "主打伤人，词讼阳人小口凶。");
            put(Arrays.asList("杜门", "壬"), "主奸盗事，凶。");
            put(Arrays.asList("杜门", "癸"), "主百事皆阻，病者不食。");
            put(Arrays.asList("景门", "休门"), "主文书遗失，争讼不休。");
            put(Arrays.asList("景门", "生门"), "主阴人生产大喜，更主求财旺利，行人皆吉。");
            put(Arrays.asList("景门", "伤门"), "主姻亲小口口舌。");
            put(Arrays.asList("景门", "杜门"), "主失脱文书，散财后平。");
            put(Arrays.asList("景门", "景门"), "主文状未动有预先见之意，内有小口忧患。");
            put(Arrays.asList("景门", "死门"), "主官讼，因田宅事争竞，惹麻烦。");
            put(Arrays.asList("景门", "惊门"), "主官讼，女人小口疾病，凶。");
            put(Arrays.asList("景门", "开门"), "主官人升迁，吉；求文印更吉。");
            put(Arrays.asList("景门", "乙"), "主讼事不成。");
            put(Arrays.asList("景门", "丙"), "主文书急迫火速不利。");
            put(Arrays.asList("景门", "丁"), "主因文书印状招非。");
            put(Arrays.asList("景门", "戊"), "主因财产词讼。远行吉。");
            put(Arrays.asList("景门", "己"), "主官事牵连。");
            put(Arrays.asList("景门", "庚"), "主讼人自讼。");
            put(Arrays.asList("景门", "辛"), "主阴人词讼。");
            put(Arrays.asList("景门", "壬"), "主因贼牵连。");
            put(Arrays.asList("景门", "癸"), "主因奴婢刑。");
            put(Arrays.asList("死门", "休门"), "主求财物事不吉，若问生道求方吉。");
            put(Arrays.asList("死门", "生门"), "主丧事，求财得，占病死者复生。");
            put(Arrays.asList("死门", "伤门"), "主官事动而被刑杖，凶。");
            put(Arrays.asList("死门", "杜门"), "主破财，妇人风疾，凶。");
            put(Arrays.asList("死门", "景门"), "主因文契印信财产事见官，先怒后喜，不凶。");
            put(Arrays.asList("死门", "死门"), "主官而留，印信无气，凶。");
            put(Arrays.asList("死门", "惊门"), "主因官司不给，忧疑患病，凶。");
            put(Arrays.asList("死门", "开门"), "主见贵人，求印信文书事大利。");
            put(Arrays.asList("死门", "乙"), "主求事不成。");
            put(Arrays.asList("死门", "丙"), "主信息忧疑。");
            put(Arrays.asList("死门", "丁"), "主老阳人疾病。");
            put(Arrays.asList("死门", "戊"), "主作伪财。");
            put(Arrays.asList("死门", "己"), "主病讼牵连不已，凶。");
            put(Arrays.asList("死门", "庚"), "主女人生产，母子俱凶。");
            put(Arrays.asList("死门", "辛"), "主盗贼失脱难获。");
            put(Arrays.asList("死门", "壬"), "主讼人自讼自招。");
            put(Arrays.asList("死门", "癸"), "主妇女嫁娶事凶。");
            put(Arrays.asList("惊门", "休门"), "主求财事或因口舌求财事，迟吉。");
            put(Arrays.asList("惊门", "生门"), "主因妇人生忧惊，或因求财生忧惊，皆吉。");
            put(Arrays.asList("惊门", "伤门"), "主因商议同谋害人，事泄惹讼，凶。");
            put(Arrays.asList("惊门", "杜门"), "主因失脱破财惊恐，不凶。");
            put(Arrays.asList("惊门", "景门"), "主词讼不息，小口疾病，凶。");
            put(Arrays.asList("惊门", "死门"), "主因宅中怪异而生是非，凶。");
            put(Arrays.asList("惊门", "惊门"), "主疾病、忧疑、惊疑。");
            put(Arrays.asList("惊门", "开门"), "主忧疑、官司、惊恐；能见贵人，不凶。");
            put(Arrays.asList("惊门", "乙"), "主谋财不得。");
            put(Arrays.asList("惊门", "丙"), "主文书印信惊恐。");
            put(Arrays.asList("惊门", "丁"), "主词讼牵连。");
            put(Arrays.asList("惊门", "戊"), "主损财，信阻。");
            put(Arrays.asList("惊门", "己"), "主恶犬伤人成讼。");
            put(Arrays.asList("惊门", "庚"), "主道路损折、遇贼盗，凶。");
            put(Arrays.asList("惊门", "辛"), "主女人成讼，凶。");
            put(Arrays.asList("惊门", "壬"), "主官司因禁，病者大凶。");
            put(Arrays.asList("惊门", "癸"), "主被盗，失物难获。");
            put(Arrays.asList("开门", "休门"), "主见贵人财喜及开张铺店，贸易大吉。");
            put(Arrays.asList("开门", "生门"), "主见贵人，谋望所求遂意。");
            put(Arrays.asList("开门", "伤门"), "主变动、更改、移徙，事皆不吉。");
            put(Arrays.asList("开门", "杜门"), "主失脱，刊印书契小凶。");
            put(Arrays.asList("开门", "景门"), "主见贵人，因文书事不利。");
            put(Arrays.asList("开门", "死门"), "主官司惊忧，先忧后喜。");
            put(Arrays.asList("开门", "惊门"), "主百事不利。");
            put(Arrays.asList("开门", "开门"), "主贵人定物财喜。");
            put(Arrays.asList("开门", "乙"), "小财可求。");
            put(Arrays.asList("开门", "丙"), "贵人印绶。");
            put(Arrays.asList("开门", "丁"), "远信心至。");
            put(Arrays.asList("开门", "戊"), "财名俱得。");
            put(Arrays.asList("开门", "己"), "事绪不定。");
            put(Arrays.asList("开门", "庚"), "道路词讼，谋为两歧。");
            put(Arrays.asList("开门", "辛"), "阴人道路。");
            put(Arrays.asList("开门", "壬"), "远得有失。");
            put(Arrays.asList("开门", "癸"), "阴人人财小凶。");
        }
    };

    /**
     * 八门克应之动应
     */
    public static final Map<List<String>, String> BA_MEN_DONG_YING = new HashMap<List<String>, String>() {
        private static final long serialVersionUID = -1;

        /*
            八门动应：门与门相对时，在出门等路上所遇到的兆应，主要用于择吉。
        */ {
            put(Arrays.asList("休门", "休门"), "一里或十一里，逢青衣夫妻歌唱为应。");
            put(Arrays.asList("休门", "生门"), "八里或十八里，逢妇人下黑土黄土或皂衣公吏人。");
            put(Arrays.asList("休门", "伤门"), "三里或十三里，逢匠人拿木棍或皂衣公吏人。");
            put(Arrays.asList("休门", "杜门"), "四里或十四里，逢青衣妇人拉或抱孩童边走边唱。");
            put(Arrays.asList("休门", "景门"), "九里或十九里，逢皂衣公吏人骑骡马或乘车。");
            put(Arrays.asList("休门", "死门"), "二里或十二里，逢孝服人哭泣，更有绿衣人相伴。");
            put(Arrays.asList("休门", "惊门"), "七里或十七里，逢皂衣人打足，妇人拉、抱孩童。");
            put(Arrays.asList("休门", "开门"), "六里或十六里，逢人打架叹气，畜物争斗。");
            put(Arrays.asList("生门", "休门"), "一里或十一里，逢皂衣人及打钱人。");
            put(Arrays.asList("生门", "生门"), "八里或十八里，逢朱衣贵人。");
            put(Arrays.asList("生门", "伤门"), "三里或十三里，逢公吏人持棍，或培土栽树。");
            put(Arrays.asList("生门", "杜门"), "四里或十四里，逢人拿彩色物品边走边唱并长叹息人。");
            put(Arrays.asList("生门", "景门"), "九里或十九里，逢贵人车马多人相随。");
            put(Arrays.asList("生门", "死门"), "二里或十二里，逢孝服人哭泣。");
            put(Arrays.asList("生门", "惊门"), "七里或十七里，逢人赶畜，及有人讲诉讼事情。");
            put(Arrays.asList("生门", "开门"), "六里或十六里，逢贵车马并有蛇咬猪者。");
            put(Arrays.asList("伤门", "休门"), "一里或十一里，逢老妇与少男同行。");
            put(Arrays.asList("伤门", "生门"), "八里或十八里，逢人伐树或培土。");
            put(Arrays.asList("伤门", "伤门"), "三里或十三里，逢二车堵塞道路争行。");
            put(Arrays.asList("伤门", "杜门"), "四里或十四里，逢公吏人及木匠伐树，并有妇人抱小儿经过。");
            put(Arrays.asList("伤门", "景门"), "九里或十九里，逢色衣人骑骡马坐车经过。");
            put(Arrays.asList("伤门", "死门"), "二里或十二里，逢埋葬及孝服人哭泣。");
            put(Arrays.asList("伤门", "惊门"), "七里或十七里，逢人争斗及赶牲畜，并有妇人与少女同行。");
            put(Arrays.asList("伤门", "开门"), "六里或十六里，逢人拆墙安门解板或二猪相咬。");
            put(Arrays.asList("杜门", "休门"), "一里或十一里，逢唱戏或皂衣人抱孩童。");
            put(Arrays.asList("杜门", "生门"), "八里或十八里，逢人扛钱或手拿食物并唱歌。");
            put(Arrays.asList("杜门", "伤门"), "三里或十三里，逢木匠拿着木棍。");
            put(Arrays.asList("杜门", "杜门"), "四里或十四里，逢妇人引孩子童着绿衣。");
            put(Arrays.asList("杜门", "景门"), "九里或十九里，逢孕妇着色衣或公吏人骑赤马或开、坐红车。");
            put(Arrays.asList("杜门", "死门"), "二里或十二里，逢丧服人哭泣。");
            put(Arrays.asList("杜门", "惊门"), "七里或十七里，逢人唱歌、锣声或有人讲公讼事。");
            put(Arrays.asList("杜门", "开门"), "六里或十六里，逢人唱歌及狗咬猪。");
            put(Arrays.asList("景门", "休门"), "一里或十一里，逢女人哭泣，与卖鱼人并行。");
            put(Arrays.asList("景门", "生门"), "八里或十八里，逢小儿赶牛，人背钱以袋和箱装之。");
            put(Arrays.asList("景门", "伤门"), "三里或十三里，逢色衣女人坐车或乘骡马。");
            put(Arrays.asList("景门", "杜门"), "四里或十四里，逢老少女领黑衣童孩行。");
            put(Arrays.asList("景门", "景门"), "九里或十九里，逢人抱文书，更有火光惊恐。");
            put(Arrays.asList("景门", "死门"), "二里或十二里，逢霄服人哭泣，色衣人骑马或开、坐车。");
            put(Arrays.asList("景门", "惊门"), "七里或十七里，逢争讼争斗，宜避之。");
            put(Arrays.asList("景门", "开门"), "六里或十六里，逢人成队行走，官人骑马。");
            put(Arrays.asList("死门", "休门"), "一里或十一里，逢青衣妇人哭泣。");
            put(Arrays.asList("死门", "生门"), "八里或十八里，逢孝子拿生物大恸。");
            put(Arrays.asList("死门", "伤门"), "三里或十三里，逢人抬棺材。");
            put(Arrays.asList("死门", "杜门"), "四里或十四里，逢埋葬及纸扎彩色物。");
            put(Arrays.asList("死门", "景门"), "九里或十九里，逢重孝人哭泣，退吉进凶。");
            put(Arrays.asList("死门", "死门"), "二里或十二里逢妇人哭泣，凶。");
            put(Arrays.asList("死门", "惊门"), "七里或十七里，逢丧哭泣或死畜物类。");
            put(Arrays.asList("死门", "开门"), "六里或十六里，逢开坟、哭泣或是见畜类争斗。");
            put(Arrays.asList("惊门", "休门"), "一里或十一里，逢青衣妇人说官司。");
            put(Arrays.asList("惊门", "生门"), "八里或十八里，逢女人引孩童赶牛，小儿拿吃的东西。");
            put(Arrays.asList("惊门", "伤门"), "三里或十三里，逢男女吵闹，打孩子，宜退不宜进，若强进有车折马死，凶。");
            put(Arrays.asList("惊门", "杜门"), "四里或十四里，逢僧道同行或男女相商。");
            put(Arrays.asList("惊门", "景门"), "九里或十九里，逢色衣妇人说官司。");
            put(Arrays.asList("惊门", "死门"), "二里或十二里，逢女人哭泣及丧亡事情。");
            put(Arrays.asList("惊门", "惊门"), "七里或十七里，逢二女吵闹，傍人说打官司事。");
            put(Arrays.asList("惊门", "开门"), "六里或十六里，逢官吏役人争讼。");
            put(Arrays.asList("开门", "休门"), "一里、十一里，逢四足畜物相斗，妇人著皂衣及文人言功名事。");
            put(Arrays.asList("开门", "生门"), "八里、十八里，逢阴人并四足物，或阳人言争产财帛事。");
            put(Arrays.asList("开门", "伤门"), "三里、十三里，逢妇人车马，随人弄火。");
            put(Arrays.asList("开门", "杜门"), "四里、十四里，逢阳人急唱，或僧道为应。");
            put(Arrays.asList("开门", "景门"), "九里、十九里，逢贵人骑马坐车，或拿文书为应。");
            put(Arrays.asList("开门", "死门"), "二里、十二里，逢老人啼哭，或开土埋葬为应。");
            put(Arrays.asList("开门", "惊门"), "七里、十七里，逢兄妹同行为应。");
            put(Arrays.asList("开门", "开门"), "六里、六十里，见贵人及打斗者为应。");
        }
    };

    /**
     * 星门克应
     */
    public static final Map<List<String>, String> XING_MEN_KE_YING = new HashMap<List<String>, String>() {
        private static final long serialVersionUID = -1;

        /*
            星门克应：星加门形成的格局及其吉凶。
        */ {
            // 例如→ 天蓬星+休门：披枷戴锁，锒铛入狱；小凶
            put(Arrays.asList("天蓬", "休门"), "披枷戴锁，锒铛入狱；小凶。");
            put(Arrays.asList("天蓬", "生门"), "纵欲无度，尽兴不返；大吉。");
            put(Arrays.asList("天蓬", "伤门"), "大难临头，六宅不安；小凶。");
            put(Arrays.asList("天蓬", "杜门"), "十年寒窗，不得一举；小凶。");
            put(Arrays.asList("天蓬", "景门"), "万事具备，只欠东风；小凶。");
            put(Arrays.asList("天蓬", "死门"), "夺戒口食，剥戒身衣；小凶。");
            put(Arrays.asList("天蓬", "惊门"), "别生枝节，何所取义；小凶。");
            put(Arrays.asList("天蓬", "开门"), "三年不鸣，一鸣惊人；大吉。");
            put(Arrays.asList("天任", "休门"), "因材施教，青出于蓝；大吉。");
            put(Arrays.asList("天任", "生门"), "前山后海，进退两难；小凶。");
            put(Arrays.asList("天任", "伤门"), "饥不择食，饮鸩止渴；小凶。");
            put(Arrays.asList("天任", "杜门"), "积劳成疾，病入膏肓；小凶。");
            put(Arrays.asList("天任", "景门"), "衣暖食饱，琼楼玉宇；小吉。");
            put(Arrays.asList("天任", "死门"), "明目张胆，坐地分赃；大凶。");
            put(Arrays.asList("天任", "惊门"), "一无所得，人财两空；小凶。");
            put(Arrays.asList("天任", "开门"), "仓斗库实，有备无患；大吉。");
            put(Arrays.asList("天冲", "休门"), "履险如夷，转危为安；大吉。");
            put(Arrays.asList("天冲", "生门"), "塞翁失马，安之非福；大吉。");
            put(Arrays.asList("天冲", "伤门"), "遍体鳞伤，痛入骨髓；大凶。");
            put(Arrays.asList("天冲", "杜门"), "墨守成规，不知改变；小凶。");
            put(Arrays.asList("天冲", "景门"), "车载斗量，指不胜屈；小吉。");
            put(Arrays.asList("天冲", "死门"), "刀光剑影，枕戈待旦；小凶。");
            put(Arrays.asList("天冲", "惊门"), "遇人不淑，劳燕分飞；大凶。");
            put(Arrays.asList("天冲", "开门"), "力行不怠，一日千重；大吉。");
            put(Arrays.asList("天辅", "休门"), "雾消云散，重见光明；大吉。");
            put(Arrays.asList("天辅", "生门"), "心心相印，海誓山盟；大吉。");
            put(Arrays.asList("天辅", "伤门"), "先天不足，后天未补；小凶。");
            put(Arrays.asList("天辅", "杜门"), "七颠八倒，自相矛盾；大凶。");
            put(Arrays.asList("天辅", "景门"), "春风一度，始乱终弃；小吉。");
            put(Arrays.asList("天辅", "死门"), "花天酒地，玩物丧志；小凶。");
            put(Arrays.asList("天辅", "惊门"), "天罗地网，插翅难飞；小凶。");
            put(Arrays.asList("天辅", "开门"), "字无分文，牛衣对泣；小凶。");
            put(Arrays.asList("天英", "休门"), "寸进尺退，一事无成；小凶。");
            put(Arrays.asList("天英", "生门"), "游山玩水，走遍天下；大吉。");
            put(Arrays.asList("天英", "伤门"), "龙争虎斗，两败俱伤；小凶。");
            put(Arrays.asList("天英", "杜门"), "倚官仗势，作威作福；小凶。");
            put(Arrays.asList("天英", "景门"), "春风一度，始乱终弃；小凶。");
            put(Arrays.asList("天英", "死门"), "连年征战，劳民伤财；小凶。");
            put(Arrays.asList("天英", "惊门"), "目瞪口呆，方寸已乱；小凶。");
            put(Arrays.asList("天英", "开门"), "金碧辉煌，前呼后拥；大吉。");
            put(Arrays.asList("天芮", "休门"), "一以当千，南争北战；大吉。");
            put(Arrays.asList("天芮", "生门"), "力不从心，望尘莫及；小凶。");
            put(Arrays.asList("天芮", "伤门"), "七窃生烟，九世之仇；小凶。");
            put(Arrays.asList("天芮", "杜门"), "安生而食，用钱如水；小凶。");
            put(Arrays.asList("天芮", "景门"), "才情卓越，大智若愚；小吉。");
            put(Arrays.asList("天芮", "死门"), "日落西山，旦不保夕；大凶。");
            put(Arrays.asList("天芮", "惊门"), "风吹草动，一夕数惊；小凶。");
            put(Arrays.asList("天芮", "开门"), "堆金积玉，安富尊荣；大吉。");
            put(Arrays.asList("天柱", "休门"), "孤云野鹤，枕流漱石；大吉。");
            put(Arrays.asList("天柱", "生门"), "怜我怜卿，鸾凤和鸣；大吉。");
            put(Arrays.asList("天柱", "伤门"), "上下其手，一手遮天；大凶。");
            put(Arrays.asList("天柱", "杜门"), "七颠八倒，自相矛盾；大凶。");
            put(Arrays.asList("天柱", "景门"), "先著祖鞭，长治久安；小吉。");
            put(Arrays.asList("天柱", "死门"), "引狼入室，虎视耽耽；小凶。");
            put(Arrays.asList("天柱", "惊门"), "投机取巧，惟利是图；大凶。");
            put(Arrays.asList("天柱", "开门"), "有勇有谋，果决前进；大吉。");
            put(Arrays.asList("天心", "休门"), "官明如镜，吏清如水；大吉。");
            put(Arrays.asList("天心", "生门"), "六根清净，山林隐逸；大吉。");
            put(Arrays.asList("天心", "伤门"), "飞来横祸，轩然大波；小凶。");
            put(Arrays.asList("天心", "杜门"), "山穷水尽，千辛万苦；大凶。");
            put(Arrays.asList("天心", "景门"), "相见恨晚，握手言欢；小吉。");
            put(Arrays.asList("天心", "死门"), "生死有命，回天乏术；小凶。");
            put(Arrays.asList("天心", "惊门"), "千变万化，不可捉摸；小凶。");
            put(Arrays.asList("天心", "开门"), "四海漂泊，何处是家；小凶。");
            put(Arrays.asList("天禽", "休门"), "披枷戴锁，锒铛入狱；小凶。");
            put(Arrays.asList("天禽", "生门"), "前山后海，进退两难；小凶。");
            put(Arrays.asList("天禽", "伤门"), "遍体鳞伤，痛入骨髓；大凶。");
            put(Arrays.asList("天禽", "杜门"), "七颠八倒，自相矛盾；大凶。");
            put(Arrays.asList("天禽", "景门"), "春风一度，始乱终弃；小凶。");
            put(Arrays.asList("天禽", "死门"), "日落西山，旦不保夕；大凶。");
            put(Arrays.asList("天禽", "惊门"), "投机取巧，惟利是图；大凶。");
            put(Arrays.asList("天禽", "开门"), "四海漂泊，何处是家；小凶。");
        }
    };

    /**
     * 九星时应
     */
    public static final Map<List<String>, String> JIU_XING_SHI_YING = new HashMap<List<String>, String>() {
        private static final long serialVersionUID = -1;

        /*
            九星时应：指天盘上的[天蓬、天任、天冲、天辅、天禽、天英、天芮、天柱、天心]九星为值符时，与其所对应的时辰地支之间的生克关系及其吉凶。
        */ {
            // 例如→ 天蓬星值子时：不利入宅、安坟、上官、下穴，主有口舌争讼。作用之时，有鸡鸣、犬吠、宿鸟闹林，或鸟北方争斗而飞，造葬后主有缺唇人至。至六十日应鸡生肉卵，有官讼至，主退财。
            put(Arrays.asList("天蓬", "子"), "不利入宅、安坟、上官、下穴，主有口舌争讼。作用之时，有鸡鸣、犬吠、宿鸟闹林，或鸟北方争斗而飞，造葬后主有缺唇人至。至六十日应鸡生肉卵，有官讼至，主退财。");
            put(Arrays.asList("天任", "子"), "主有风雨至，水畔鸡鸣，东南方有持刀人过为应。造葬后百日内，主新妇自离，点水性人上门抵赖，退田产后，出人男盗女娼凶。");
            put(Arrays.asList("天冲", "子"), "主有大风雨至。仙禽噪、钟鸣为应。造葬后，六十日有生气物入屋，周年后田蚕倍收，新妇有孕。会因口舌得财。");
            put(Arrays.asList("天辅", "子"), "若为反吟，主西方有人穿红白衣服人前来大叫为应。造葬后，六十日进商音人、物产，野猿猴入屋，宝瓶鸣时，主加官晋禄，生贵子。若门奇到，有十二年大旺。");
            put(Arrays.asList("天英", "子"), "有锣声自西北至，及三五人拿火伐木为应，造葬后，主有残病人破家业，三年内血光自刎，小儿因汤火伤。");
            put(Arrays.asList("天芮", "子"), "秋冬用之吉，春夏凶。主有走禽惊，西南火光，二人相逐为应。造葬后，主有猫狗疯癫伤人，惹官非，六十日内有女人自缢事，秋冬作用，当进羽音人、田地及妻女。");
            put(Arrays.asList("天柱", "子"), "主有风雨，火从东方起，缺唇人为应，造葬后六十日内主有蛇犬伤人，血光破财。");
            put(Arrays.asList("天心", "子"), "主有人争斗。鼓声从西北起为应。造葬后百日内赤面人作牙，进商音人、古器及画轴，家内生白鸡，十二年内田蚕大旺，后因赌博、见讼破财。");
            put(Arrays.asList("天禽", "子"), "主有怀孕女人来，及紫衣人至为应，造葬后五十日鸡上篱，犬衔花，儒人送物至为应，主因武得官，进田土、财物。二十年后财谷大旺，人丁千口。");
            put(Arrays.asList("天蓬", "丑"), "主树倒伤人。有雷电大作及风雨为应。造葬后七日内，鸡生鹅子卵，犬上主屋，主伤小孩。三年后白头翁作牙，进商音人、田契，大旺财谷，十年后即退败。");
            put(Arrays.asList("天任", "丑"), "有青衫女人携酒至，四方有鼓声为应。造葬后半年，进无名财物，一年后有鹦鹉入屋，主口舌得财，三年后猫犬相咬，主发科吉。");
            put(Arrays.asList("天冲", "丑"), "主云雾四合，以小儿成群来及妇人为应，造葬后黑猫生白子，拾得古镜发财，一年后得僧道、田契、生贵子。");
            put(Arrays.asList("天辅", "丑"), "主东方有几只犬吠，有人持刀杀人斗叫。造葬后，有白兔野鸡入室，六十日内僧道送物，及东南方羽音人送文契至，远信至，一年后添进人口，大旺血财，加官晋禄。");
            put(Arrays.asList("天英", "丑"), "东北方有师巫人至，及锣声为应。造葬后一月内主火烧屋，一年内狗作人言，百怪俱见，死亡大败。");
            put(Arrays.asList("天芮", "丑"), "有金鼓声向西北至，造葬后七日，有乌龟自林中出，六十日被盗贼退财，口舌官事至。");
            put(Arrays.asList("天柱", "丑"), "北方有匠人携斧至，树木上生金花为应，造葬后六十日进羽音姓人金银器，三年遇大火一贫彻骨，出人捉蛇养狗。");
            put(Arrays.asList("天心", "丑"), "主南方有火光, 跛足人送物至，五日内双猫自来为应，作用后，四十日有远方人送物，进商音人财产文契。");
            put(Arrays.asList("天禽", "丑"), "有孝妇人持锡器来，小儿拍掌笑，吹笛打鼓叫闹为应。造葬后赌博获财，或拾财发富，三年后因获盗贼致富。");
            put(Arrays.asList("天蓬", "寅"), "有青衣童子持花来，北方有和尚裹衣至，女人着衫裙至。造葬后有贼劫家财，六十日内有蛇入屋咬人，因马牛死伤人，及鬼打屋，三年后进田地，大旺财谷。");
            put(Arrays.asList("天任", "寅"), "女人成队拿火前行，童子拍手大笑为应，西北有人轿马至。造葬后六十日内，家中老人死。百日内进六畜，女人财宝自至，田蚕大旺后因缺唇人争讼婚事，败。");
            put(Arrays.asList("天冲", "寅"), "有贵人乘轿（开车）至，及童子执金银器至。造葬后二十日进角音人、契字、及琉璃器物，六十日鸡母啼家，主死。因口舌争讼得财。主乙巳丁年生人发福。");
            put(Arrays.asList("天辅", "寅"), "见公吏人手执铁器至，及艺人携物至为应。造葬后六十日内白鼻猫儿咬鸡时，有贼送财宝至，赤面人作牙，进羽音人、田契、二年大发，生贵子。");
            put(Arrays.asList("天英", "寅"), "东方有兵马来，及捕鱼猎网人至。造葬后，女人因行路拾得财宝，六十日内进寡妇田产契书。百日内雷打屋即败。");
            put(Arrays.asList("天芮", "寅"), "有瘦妇怀孕至，更有蓑衣人至。造葬后有奇门旺相，六十日有水牛入屋，大进血财，加官晋禄，子孙大吉。");
            put(Arrays.asList("天柱", "寅"), "有牛马喧叫，及僧道人持伞至，有大雷雨、喜鹊喧噪为应。造葬后六十日内有贼牵连公事，因公事说讼破财，女人堕胎，难产死。");
            put(Arrays.asList("天心", "寅"), "有白鹭鸟及水禽至，金鼓四鸣，女人穿青衣携篮至。造葬后火烧伤小口，六十日内由公事至，百日内大进金银，因拾得古窖，三年内因妻得财生贵子。");
            put(Arrays.asList("天禽", "寅"), "金鸡乱鸣，犬吠，有人带深笠至。造葬后六十日进羽音人、契字、田财，人丁大旺。");
            put(Arrays.asList("天蓬", "卯"), "黄云四起，妇人拿铁器前来，大蛇横过路。造葬后十日内，徵音人相请，半月内，有徵音人送财物。六十日内，女人因贼害而大破财。百日内，得横财大发。");
            put(Arrays.asList("天任", "卯"), "有老人持杖至，及喜鹊喧噪为应。造葬后七日内，有人进古器物，六十日内，因女人获财宝，进牛羊六畜；因赌博得财，加官进职。");
            put(Arrays.asList("天冲", "卯"), "有女人穿红色衣送物，及贵人骑马至，两犬相咬，水牛作声。造葬后六十日，进东方人产业，因汤火伤小儿，进财。三年内妇人堕胎，产死。");
            put(Arrays.asList("天辅", "卯"), "女人挑伞至，及师巫吹角声，造葬后六十日，大发，添人丁，有生气入屋，旺财谷，因女人公事得财帛、田地契字。");
            put(Arrays.asList("天英", "卯"), "有女人持灯笼来应，或执木棍来应。若见雷鸣应，六十日内，进女人财宝，因而大发。");
            put(Arrays.asList("天芮", "卯"), "有女人穿红色衣送物，及贵人骑马至，两犬相咬，水牛作声。造葬后六十日进东方人产业，因汤火伤小儿，进财。三年内妇人堕胎，产死。");
            put(Arrays.asList("天柱", "卯"), "有人伐树，及男人持鼓过，黄衣老人持锄至。造葬后六十日内鸡母啼昼鸣，犬上屋。一年内少妇疫病死，凶。");
            put(Arrays.asList("天心", "卯"), "有跛脚妇人相打及犬吠声，北方有轿车至，造葬七日内进横财，三年后有牛自来，大旺六畜，参军得财，大发。");
            put(Arrays.asList("天禽", "卯"), "大风东起，禽鸟鸣叫，怀孕妇人至，造葬后半年猫儿自来园内，二年得财大发。");
            put(Arrays.asList("天蓬", "辰"), "东北树倒打人，鼓声四起，女人穿红衣至。造葬后，鸟雀四鸣绕屋，被贼盗财。六十日内有病脚人上门抵赖。三年后生贵子，大发财。");
            put(Arrays.asList("天任", "辰"), "主有白衣男女同行，或孕妇抱小儿为应。造葬后，有人送活物至，大吉。");
            put(Arrays.asList("天冲", "辰"), "主有鱼上树，白虎出山，僧道成群至。造葬后四十日内，拾得黄金白银之物，大发横财。七十日内家主的伤折之灾。");
            put(Arrays.asList("天辅", "辰"), "白羊与黄犬相闹，卖油人与卖菜米人相撞，白衣小儿哭，怀孕妇人至。造葬后一年内生贵子，大发财谷。");
            put(Arrays.asList("天英", "辰"), "西北方大雨至，鸡飞上树，女人持物携篮至。造葬后七日内，有生气入屋，六十日内活物入宅，进横财大发。");
            put(Arrays.asList("天芮", "辰"), "东方树倒伤人，鼓乐声四起，女人穿红衣至为应。造葬后雀绕屋飞鸣、因贼破财。六十日内有病脚人上门的抵赖。三年后生贵子，大发旺。");
            put(Arrays.asList("天柱", "辰"), "有人西方拿金器来。造葬后七日内进阴人财物，寡妇送契至，三年大发。");
            put(Arrays.asList("天心", "辰"), "有云从西北起，青衣人携鱼至，女人僧道同行。造葬后，井中气如云出，三日内生贵子，主科第富贵。");
            put(Arrays.asList("天禽", "辰"), "有师巫术人相争大叫，及东方鸦噪，造葬后六十日内有僧道人及绝户人送物产至。");
            put(Arrays.asList("天蓬", "巳"), "有驼背老人披蓑衣至，女携酒及师巫人至。造葬后一百日，因火大获横财，一年后，因武获职，加官进禄。");
            put(Arrays.asList("天任", "巳"), "有两犬争一物，野人负柴薪过，吏人持伞盖至。造葬后六十日内，获异路人财，南方人送鱼。一年后生贵子，异路显达，进田财。");
            put(Arrays.asList("天冲", "巳"), "有牛相打，羊争行，女人相骂，西南方有鼓声喧闹。造葬后六十日内，蛇咬鸡，牛入室，有女人送契至。一百日后，犬生花子，大旺田财。");
            put(Arrays.asList("天辅", "巳"), "有人相打，女人抱布来，风四起，小童哭叫。造葬后六十日内，进东方人财物，有鬼神运来大发。");
            put(Arrays.asList("天英", "巳"), "主有人抱文书，持伞盖至或抱锡磁器为应，造葬后六十日内，得异姓人财产，南方人送活物来。一年内生贵子发达。");
            put(Arrays.asList("天芮", "巳"), "有妇人少女同至为应，造葬后四十日进绝户人田契，一年内因水火发财。");
            put(Arrays.asList("天柱", "巳"), "有黑牛过，钟声鸣，猪上山。造葬后二十日内进商音姓人财物。六十日内家内女人下水，有活物入屋。大发大贵之兆。");
            put(Arrays.asList("天心", "巳"), "有女人穿青衣抱小儿至，紫衣人骑马至，乌龟上树。造葬后半月内，得远方人财物，跛人作牙，进商音产契，六畜兴旺。三年内，女人成家，寡母坐堂。");
            put(Arrays.asList("天禽", "巳"), "有白颈鸭（鸟）成队飞鸣，及师巫人相打，贵人骑马过。造葬后七十日有妇人来，生贵子，成家立产。三年后田产大旺。");
            put(Arrays.asList("天蓬", "午"), "有人持刀上山，妇人领青衣童子至。造葬后四十日内家主亡。六十日内犬来做人语，入屋为怪。赤面风脚人上门行凶破财，三年后才发旺。");
            put(Arrays.asList("天任", "午"), "西方黄色飞禽来，僧道与儒士同行为应。造葬后四十日进外宝、贵人财物，紫衣人入屋，生贵子。");
            put(Arrays.asList("天冲", "午"), "东方人家火起，穿白衣前来大唤，山禽噪闹。六十日内拾得古铜器物，大发财产。");
            put(Arrays.asList("天辅", "午"), "有僧道持物来，女人穿红衣至，有石火光。造葬后六十日内有贵人至，送异物，进西方人金银。一年内得寡妇人绝户物。");
            put(Arrays.asList("天英", "午"), "南方有人来，穿红衣或骑马持文书至为应，造葬后六十日内被木石伤死，及自缢人命官司败。");
            put(Arrays.asList("天芮", "午"), "主天中有人缺唇，白衣人至，有孕妇过。六十日内有猫鬼咬人，因买卖发横财，一年内得东邻或妻财产大发。");
            put(Arrays.asList("天柱", "午"), "西方有人骑马至，冬月有雪，夏秋有鸦飞鸣为应。造葬后五日内孕妇先病行丧哭泣。六十日内水边得古铜器，退财小口凶。");
            put(Arrays.asList("天心", "午"), "主大风雨骤至。蛇横路，女人穿红裙携酒至。造葬后六十日蚕鸣，有跛足人送活物。五年内进金银，大发大旺。");
            put(Arrays.asList("天禽", "午"), "有白衣女人来，狗衔花，山鸡斗叫，风雨从东来。六十日内有犬自外来，或野犬入屋，主进东北方人财，更赌博公事得财，一年后乌鸡生白雏，田蚕大旺。");
            put(Arrays.asList("天蓬", "未"), "童子牵二牛至，白鹭群北方飞来，有女人穿红衣至，造葬后六十日内军贼入屋劫掠财物，凶败。");
            put(Arrays.asList("天任", "未"), "主有白鸟飞来，飞禽自西南方至，北方大斗闹，鼓声喧天，风雨大至。造葬后七日内，女人送白色衣物或白纸。六十日内家生异白气物，得六畜大旺。");
            put(Arrays.asList("天冲", "未"), "有鼓乐响声，小儿穿孝衣至，牛马成群过，西北方有人叫喊声，造葬后六十日内有白羊入屋，六畜大旺。");
            put(Arrays.asList("天辅", "未"), "群犬争吠，丐者携蓑衣至，僧道成群过，西北方有争财，造葬后一百日内，有文书契字，进商音人财物金银。");
            put(Arrays.asList("天英", "未"), "有孕妇过，及西北方有鼓声为应。造葬后六十日内家主落水淹死，一年后因瘟疫大败。");
            put(Arrays.asList("天芮", "未"), "有捕猎人至，及白衣道人携茶过。造葬后七日有乌鸦绕屋鸣噪，一年内动瘟疫、火烧屋荡败。");
            put(Arrays.asList("天柱", "未"), "有瘦妇与僧道同行东北方，有人携伞骑马过。造葬后一百日内因女人见狐狸猫而败。");
            put(Arrays.asList("天心", "未"), "主有艺人法术人拿空器过，白衣人至为应。造葬后，得商音姓人方契，田宅发富。");
            put(Arrays.asList("天禽", "未"), "有老人及跛足人担花过，或青衣人携物至。造葬后六十日内进羽音人铁器，六畜大旺。");
            put(Arrays.asList("天蓬", "申"), "有取水人持伞笠至，西方有小儿打水鼓叫喊为应。造葬后三十日内，鸡窝内蛇伤人。一百日内，有新妇自缢，淫欲公事败。");
            put(Arrays.asList("天任", "申"), "主大风雨至，人打鼓至，僧道穿黄衣为应。造葬后七日内，女人被火汤烧，凶败。");
            put(Arrays.asList("天冲", "申"), "东方白衣人骑马过，吏卒人持刀相杀，造葬后一百日内，女人人作牙，进绝户田产。");
            put(Arrays.asList("天辅", "申"), "有青肿患脚人携酒至，三色衣人至，西北金鼓声。造葬后半年内，因妇人财大发，蛇从井中出，外人送牛羊至，得女人财发家。");
            put(Arrays.asList("天英", "申"), "有怀孕妇人大哭，西方有金鼓声，及僧道持伞盖，造葬后，七十日内大凶。");
            put(Arrays.asList("天芮", "申"), "主东方凉伞青帽，及僧道胡须人至，及牛斗伤人，犬咬人。造葬后一百日当进羽音人产物。一年内有水牛入屋、野鸟入家，家主大病。");
            put(Arrays.asList("天柱", "申"), "主鹰擒禽鸟坠地，及青衣人携篮至。造葬后，三年内因失火丧家，烧屋大败。");
            put(Arrays.asList("天心", "申"), "僧道前来，金鼓四鸣，百鸟交噪，红裙女人送酒至。造葬后寡妇持家，开土得财。");
            put(Arrays.asList("天禽", "申"), "主天中飞鸟大叫，师巫将符纸物来。造葬后百日内女人拾得珠翠归。一年后新妇昌盛，生贵子，大旺田产。");
            put(Arrays.asList("天蓬", "酉"), "主西方有马至，群鸦飞鸣四噪。造葬后百日内，家生贵子，僧道作牙，进商音人田地，大发。");
            put(Arrays.asList("天任", "酉"), "主僧道尼姑拿火自西南来，北方有钟鼓声为应。造葬后七十日，进牛马，官员财喜，喜信至，大利财丁。");
            put(Arrays.asList("天冲", "酉"), "远方人送书(现指电子通讯等)至，东方狐狸咬叫，妇人拿火来。造葬后一年，生贵子，得横财大发。");
            put(Arrays.asList("天辅", "酉"), "远方人送书至，东方有人叫喊或说狐狸，妇人拿火来。造葬后一年，生贵子，得横财大发。");
            put(Arrays.asList("天英", "酉"), "主西方有人吵闹，鸟雀鸣叫，白衣女人经过为应，造葬后，主小孩女人足疾，百日内因唇舌得财。");
            put(Arrays.asList("天芮", "酉"), "西方有鸟飞过，群鸟飞鸣为应，造葬后百日内僧道作合，进商音人财产，生贵子发旺。");
            put(Arrays.asList("天柱", "酉"), "主东方有大小车连络数十辆为应，造葬后，七十日内得女人首饰发财。");
            put(Arrays.asList("天心", "酉"), "主僧道尼姑拿火自西南来，北方有钟鼓声。造葬后七十日内进商音姓人骡马，官员财喜，送远信至，大利。");
            put(Arrays.asList("天禽", "酉"), "主西方起火，人家吵架，鼓声喧闹为应，造葬后，一年生贵子发旺。");
            put(Arrays.asList("天蓬", "戌"), "主有老人持杖来，西方雷雨至，胡须人担箩来。造葬后，有白狗至。六十日内，因拾得车器，得横财大发。");
            put(Arrays.asList("天任", "戌"), "有女人拿布至，西方有鼓声，北方树木伤人为应。造葬后六十日，蛇虫入宅咬人，瘟疫死，大败。若有老人与小孩同来，可解转祸为福。");
            put(Arrays.asList("天冲", "戌"), "西方三五人寻失物，师巫人对走为应。造葬后六十日，鸡上树啼，远方有信，获羽音人财。一年内小口被牛踏伤。");
            put(Arrays.asList("天辅", "戌"), "西方三五人寻失物，师巫人对走为应。造葬后六十日，鸡上树啼，远方有信，获女人财。一年内小口被牛踏伤。");
            put(Arrays.asList("天英", "戌"), "有女人拿瓷瓦器或铁物至。造葬后六十日蛇虫入宅咬人，瘟疫死，大败。");
            put(Arrays.asList("天芮", "戌"), "主有老人持杖来，西方雷雨至，胡须人担物来。造葬后有白狗至。六十日内因拾得军器，得横财大发。");
            put(Arrays.asList("天柱", "戌"), "有女人拿白布物至，西方有鼓声，东北方树倒伤人为应。造葬后六十日蛇虫入宅咬人，瘟疫死，大败。");
            put(Arrays.asList("天心", "戌"), "主南方大叫贼惊，小儿骑牛至，造葬后百日内生贵子，金鸡石上鸣，犬吠，二年后中科举。");
            put(Arrays.asList("天禽", "戌"), "东北方有钟声及铙钹声，有青衣童子携篮至。造葬后六十日白龟至，得寡妇财物大发；有人中科举。");
            put(Arrays.asList("天蓬", "亥"), "主小儿成群，女人穿孝服至。造葬后，因捉贼得财。三年内，出人入道法，卖符咒水起家。");
            put(Arrays.asList("天任", "亥"), "主西方有钟声响声，有人持火叫喧。造葬后，因救火得财，大发。");
            put(Arrays.asList("天冲", "亥"), "有足跛青衣人至，东方人家有火光。造葬后百日内，猫儿捕白鼠，进商音人田契大发，财得妻财。");
            put(Arrays.asList("天辅", "亥"), "有足跛人至，青衣人往东北方去，家人点亮火光。造葬后百日内，猫儿捕白鼠，进商音人田契大发，财得妻财。");
            put(Arrays.asList("天英", "亥"), "女人持火来。造葬后百日内有疯癫人上门耍赖，身死破财。");
            put(Arrays.asList("天芮", "亥"), "主小儿成群，女人穿孝服至。造葬后，因捉贼得财谷。三年后出人入道法，卖符咒水起家。");
            put(Arrays.asList("天柱", "亥"), "主西方有钟声，山下人持火叫喧。造葬后，因救火得财，大发。");
            put(Arrays.asList("天心", "亥"), "有鸡鸣狗叫，老人戴皮帽执铁器至。造葬后七日内有不识姓名人上门借宿，遗下财物去。");
            put(Arrays.asList("天禽", "亥"), "西北方有妇人笑声，大风从西起，树倒拆屋，有人大叫。造葬后六十日内进铁匠财物，商音人请吃饭，进僧道财产。");
        }
    };

    /**
     * 后天八卦（1~9宫）
     */
    public static final String[] HOU_TIAN_BA_GUA = {"坎", "坤", "震", "巽", "", "乾", "兑", "艮", "离"};

    /**
     * 四季索引
     */
    public static final Map<String, Integer> SI_JI_INDEX = new HashMap<String, Integer>() {
        private static final long serialVersionUID = -1;

        {
            put("春季", 0);
            put("夏季", 1);
            put("秋季", 2);
            put("冬季", 3);
            put("四季末", 4);
        }
    };

    /**
     * 十二地支索引
     */
    public static final Map<String, Integer> DI_ZHI_INDEX = new HashMap<String, Integer>() {
        private static final long serialVersionUID = -1;

        {
            put("子", 0);   // 子
            put("丑", 1); // 丑
            put("寅", 2);  // 寅
            put("卯", 3);  // 卯
            put("辰", 4); // 辰
            put("巳", 5);   // 巳
            put("午", 6);   // 午
            put("未", 7);  // 未
            put("申", 8); // 申
            put("酉", 9);  // 酉
            put("戌", 10);  // 戌
            put("亥", 11); // 亥
        }
    };

    /**
     * 九宫中的地支（1~9宫）
     */
    public static final Map<Integer, List<String>> JIU_GONG_DI_ZHI = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put(0, Arrays.asList("子", ""));   // 坎一宫：子
            put(1, Arrays.asList("未", "申")); // 坤二宫：未、申
            put(2, Arrays.asList("卯", ""));   // 震三宫：卯
            put(3, Arrays.asList("辰", "巳")); // 巽四宫：辰、巳
            put(4, Arrays.asList("", ""));     // 中五宫
            put(5, Arrays.asList("戌", "亥")); // 乾六宫：戌、亥
            put(6, Arrays.asList("酉", ""));   // 兑七宫：酉
            put(7, Arrays.asList("丑", "寅")); // 艮八宫：丑、寅
            put(8, Arrays.asList("午", ""));   // 离九宫：午
        }
    };

    /**
     * 八卦旺衰（根据季节计算）
     */
    public static final Map<String, List<String>> BA_GUA_WANG_SHUAI_JI_JIE = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("坎", Arrays.asList("休", "囚", "相", "旺", "死")); // 坎一宫：春季休、夏季囚、秋季相、冬季旺、四季末死
            put("坤", Arrays.asList("死", "相", "休", "囚", "旺")); // 坤二宫：春季死、夏季相、秋季休、冬季囚、四季末旺
            put("震", Arrays.asList("旺", "休", "死", "相", "囚")); // 震三宫：春季旺、夏季休、秋季死、冬季相、四季末囚
            put("巽", Arrays.asList("旺", "休", "死", "相", "囚")); // 巽四宫：春季旺、夏季休、秋季死、冬季相、四季末囚
            put("", Collections.singletonList("四季旺"));           // 中五宫：四季旺
            put("乾", Arrays.asList("囚", "死", "旺", "休", "相")); // 乾六宫：春季囚、夏季死、秋季旺、冬季休、四季末相
            put("兑", Arrays.asList("囚", "死", "旺", "休", "相")); // 兑七宫：春季囚、夏季死、秋季旺、冬季休、四季末相
            put("艮", Arrays.asList("死", "相", "休", "囚", "旺")); // 艮八宫：春季死、夏季相、秋季休、冬季囚、四季末旺
            put("离", Arrays.asList("相", "旺", "囚", "死", "休")); // 离九宫：春季相、夏季旺、秋季囚、冬季死、四季末休
        }

    };

    /**
     * 八门旺衰（根据季节计算）
     */
    public static final Map<String, List<String>> BA_MEN_WANG_SHUAI_JI_JIE = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("休门", Arrays.asList("休", "囚", "相", "旺", "死")); // 休门：春季休、夏季囚、秋季相、冬季旺、四季末死
            put("死门", Arrays.asList("死", "相", "休", "囚", "旺")); // 死门：春季死、夏季相、秋季休、冬季囚、四季末旺
            put("伤门", Arrays.asList("旺", "休", "死", "相", "囚")); // 伤门：春季旺、夏季休、秋季死、冬季相、四季末囚
            put("杜门", Arrays.asList("旺", "休", "死", "相", "囚")); // 杜门：春季旺、夏季休、秋季死、冬季相、四季末囚
            put("", Collections.singletonList(""));
            put("开门", Arrays.asList("囚", "死", "旺", "休", "相")); // 开门：春季囚、夏季死、秋季旺、冬季休、四季末相
            put("惊门", Arrays.asList("囚", "死", "旺", "休", "相")); // 惊门：春季囚、夏季死、秋季旺、冬季休、四季末相
            put("生门", Arrays.asList("死", "相", "休", "囚", "旺")); // 生门：春季死、夏季相、秋季休、冬季囚、四季末旺
            put("景门", Arrays.asList("相", "旺", "囚", "死", "休")); // 景门：春季相、夏季旺、秋季囚、冬季死、四季末休
        }

    };

    /**
     * 九星旺衰（根据月支计算）
     */
    public static final Map<String, List<String>> JIU_XING_WANG_SHUAI_MONTH_ZHI = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        /*
            　　　     蓬 芮 冲 辅 禽 心 柱 任 英
                        ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓
            　　子月→  相 休 废 废 休 旺 旺 休 囚
            　　丑月→  囚 相 休 休 相 废 废 相 旺
            　　寅月→  旺 囚 相 相 囚 休 休 囚 废
            　　卯月→  旺 囚 相 相 囚 休 休 囚 废
            　　辰月→  囚 相 休 休 相 废 废 相 旺
            　　巳月→  休 废 旺 旺 废 囚 囚 废 相
            　　午月→  休 废 旺 旺 废 囚 囚 废 相
            　　未月→  囚 相 休 休 相 废 废 相 旺
            　　申月→  废 旺 囚 囚 旺 相 相 旺 休
            　　酉月→  废 旺 囚 囚 旺 相 相 旺 休
            　　戌月→  囚 相 休 休 相 废 废 相 旺
            　　亥月→  相 休 废 废 休 旺 旺 休 囚
         */

        {
            put("天蓬", Arrays.asList("相", "囚", "旺", "旺", "囚", "休", "休", "囚", "废", "废", "囚", "相")); // 天蓬：子月相、丑月囚、寅月旺、卯月旺、辰月囚、巳月休、午月休、未月囚、申月废、酉月废、戌月囚、亥月相
            put("天芮", Arrays.asList("休", "相", "囚", "囚", "相", "废", "废", "相", "旺", "旺", "相", "休")); // 天芮：子月休、丑月相、寅月囚、卯月囚、辰月相、巳月废、午月废、未月相、申月旺、酉月旺、戌月相、亥月休
            put("天冲", Arrays.asList("废", "休", "相", "相", "休", "旺", "旺", "休", "囚", "囚", "休", "废")); // 天冲：子月废、丑月休、寅月相、卯月相、辰月休、巳月旺、午月旺、未月休、申月囚、酉月囚、戌月休、亥月废
            put("天辅", Arrays.asList("废", "休", "相", "相", "休", "旺", "旺", "休", "囚", "囚", "休", "废")); // 天辅：子月废、丑月休、寅月相、卯月相、辰月休、巳月旺、午月旺、未月休、申月囚、酉月囚、戌月休、亥月废
            put("天禽", Arrays.asList("休", "相", "囚", "囚", "相", "废", "废", "相", "旺", "旺", "相", "休")); // 天禽：子月休、丑月相、寅月囚、卯月囚、辰月相、巳月废、午月废、未月相、申月旺、酉月旺、戌月相、亥月休
            put("天心", Arrays.asList("旺", "废", "休", "休", "废", "囚", "囚", "废", "相", "相", "废", "旺")); // 天心：子月旺、丑月废、寅月休、卯月休、辰月废、巳月囚、午月囚、未月废、申月相、酉月相、戌月废、亥月旺
            put("天柱", Arrays.asList("旺", "废", "休", "休", "废", "囚", "囚", "废", "相", "相", "废", "旺")); // 天柱：子月旺、丑月废、寅月休、卯月休、辰月废、巳月囚、午月囚、未月废、申月相、酉月相、戌月废、亥月旺
            put("天任", Arrays.asList("休", "相", "囚", "囚", "相", "废", "废", "相", "旺", "旺", "相", "休")); // 天任：子月休、丑月相、寅月囚、卯月囚、辰月相、巳月废、午月废、未月相、申月旺、酉月旺、戌月相、亥月休
            put("天英", Arrays.asList("囚", "旺", "废", "废", "旺", "相", "相", "旺", "休", "休", "旺", "囚")); // 天英：子月囚、丑月旺、寅月废、卯月废、辰月旺、巳月相、午月相、未月旺、申月休、酉月休、戌月旺、亥月囚
        }

    };

    /**
     * 八门落宫状态
     */
    public static final Map<String, List<String>> BA_MEN_LUO_GONG_STATUS = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        /*
                    　　 休门 死门 伤门 杜门 开门 惊门 生门 景门
                           ↓    ↓    ↓    ↓    ↓    ↓    ↓    ↓
                坎一宫→  伏吟 门迫 门义 门义 门和 门和 门迫 反吟
                坤二宫→  门制 伏吟 入墓 入墓 门义 门义 反吟 门和
                震三宫→  门和 门制 伏吟 比和 门迫 反吟 门制 门义
                巽四宫→  入墓 入墓 比和 伏吟 反吟 门迫 入墓 门义
                乾六宫→  门义 门和 门制 反吟 伏吟 比和 门和 入墓
                兑七宫→  门义 门和 反吟 门制 比和 伏吟 门和 门迫
                艮八宫→  门制 反吟 门迫 门迫 入墓 入墓 伏吟 门和
                离九宫→  反吟 门义 门和 门和 门制 门制 门义 伏吟

         ========================================================================

         ★解释
                伏吟：八门落入原宫位。
                反吟：八门落入与原宫对冲宫位。
                门迫：八门五行克落宫五行。
                门制：落宫五行克八门五行。
                门和：八门五行生落宫五行。
                门义：落宫五行生八门五行。
                比和：八门五行和落宫五行相同。
                入墓：休门、生门、死门落[巽四宫]为入墓。伤门、杜门落[坤二宫]为入墓。惊门开落[八宫]为入墓。景门落[乾六宫]为入墓。
         */

        // 例如：休门→ 落[坎一宫]为伏吟，落[坤二宫]为门制，落[震三宫]为门和，落[巽四宫]为入墓，落[乾六宫]为门义，落[兑七宫]为门义，落[艮八宫]为门制，落[离九宫]为反吟。
        {
            put("休门", Arrays.asList("伏吟", "门制", "门和", "入墓", "", "门义", "门义", "门制", "反吟"));
            put("死门", Arrays.asList("门迫", "伏吟", "门制", "入墓", "", "门和", "门和", "反吟", "门义"));
            put("伤门", Arrays.asList("门义", "入墓", "伏吟", "比和", "", "门制", "反吟", "门迫", "门和"));
            put("杜门", Arrays.asList("门义", "入墓", "比和", "伏吟", "", "反吟", "门制", "门迫", "门和"));
            put("开门", Arrays.asList("门和", "门义", "门迫", "反吟", "", "伏吟", "比和", "入墓", "门制"));
            put("惊门", Arrays.asList("门和", "门义", "反吟", "门迫", "", "比和", "伏吟", "入墓", "门制"));
            put("生门", Arrays.asList("门迫", "反吟", "门制", "入墓", "", "门和", "门和", "伏吟", "门义"));
            put("景门", Arrays.asList("反吟", "门和", "门义", "门义", "", "入墓", "门迫", "门和", "伏吟"));
        }

    };

    /**
     * 九星落宫状态
     */
    public static final Map<String, List<String>> JIU_XING_LUO_GONG_STATUS = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        /*
                    　　 蓬 芮 冲 辅 禽 心 柱 任 英
                          ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓
                坎一宫→  相 休 废 废 休 旺 旺 休 囚
                坤二宫→  囚 相 休 休 相 废 废 相 旺
                震三宫→  旺 囚 相 相 囚 休 休 囚 废
                巽四宫→  旺 囚 相 相 囚 休 休 囚 废
                中五宫→  囚 相 休 休 相 废 废 相 旺
                乾六宫→  废 旺 囚 囚 旺 相 相 旺 休
                兑七宫→  废 旺 囚 囚 旺 相 相 旺 休
                艮八宫→  囚 相 休 休 相 废 废 相 旺
                离九宫→  休 废 旺 旺 废 囚 囚 废 相
         */ {
            put("天蓬", Arrays.asList("相", "囚", "旺", "旺", "囚", "废", "废", "囚", "休")); // 天蓬：坎一宫相，坤二宫囚，震三宫旺，巽四宫旺，中五宫囚，乾六宫废，兑七宫废，艮八宫囚，离九宫休
            put("天芮", Arrays.asList("休", "相", "囚", "囚", "相", "旺", "旺", "相", "废")); // 天芮：坎一宫休，坤二宫相，震三宫囚，巽四宫囚，中五宫相，乾六宫旺，兑七宫旺，艮八宫相，离九宫废
            put("天冲", Arrays.asList("废", "休", "相", "相", "休", "囚", "囚", "休", "旺")); // 天冲：坎一宫废，坤二宫休，震三宫相，巽四宫相，中五宫休，乾六宫囚，兑七宫囚，艮八宫休，离九宫旺
            put("天辅", Arrays.asList("废", "休", "相", "相", "休", "囚", "囚", "休", "旺")); // 天辅：坎一宫废，坤二宫休，震三宫相，巽四宫相，中五宫休，乾六宫囚，兑七宫囚，艮八宫休，离九宫旺
            put("天禽", Arrays.asList("休", "相", "囚", "囚", "相", "旺", "旺", "相", "废")); // 天禽：坎一宫休，坤二宫相，震三宫囚，巽四宫囚，中五宫相，乾六宫旺，兑七宫旺，艮八宫相，离九宫废
            put("天心", Arrays.asList("旺", "废", "休", "休", "废", "相", "相", "废", "囚")); // 天心：坎一宫旺，坤二宫废，震三宫休，巽四宫休，中五宫废，乾六宫相，兑七宫相，艮八宫废，离九宫囚
            put("天柱", Arrays.asList("旺", "废", "休", "休", "废", "相", "相", "废", "囚")); // 天柱：坎一宫旺，坤二宫废，震三宫休，巽四宫休，中五宫废，乾六宫相，兑七宫相，艮八宫废，离九宫囚
            put("天任", Arrays.asList("休", "相", "囚", "囚", "相", "旺", "旺", "相", "废")); // 天任：坎一宫休，坤二宫相，震三宫囚，巽四宫囚，中五宫相，乾六宫旺，兑七宫旺，艮八宫相，离九宫废
            put("天英", Arrays.asList("囚", "旺", "废", "废", "旺", "休", "休", "旺", "相")); // 天英：坎一宫囚，坤二宫旺，震三宫废，巽四宫废，中五宫旺，乾六宫休，兑七宫休，艮八宫旺，离九宫相
        }
    };

    /**
     * 奇仪落宫状态
     */
    public static final Map<List<String>, String> QI_YI_LUO_GONG_STATUS = new HashMap<List<String>, String>() {
        private static final long serialVersionUID = -1;

        /*
                    　　      甲    乙    丙    丁    戊    己    庚    辛    壬    癸
                               ↓     ↓     ↓     ↓     ↓     ↓     ↓     ↓     ↓     ↓
                坎一宫(子)→  沐浴  病    胎    绝    胎    绝    死    长生  帝旺  临官
                艮八宫(丑)→  冠带  衰    养    墓    养    墓    墓    养    衰    冠带
                艮八宫(寅)→  临官  帝旺  长生  死    长生  死    绝    胎    病    沐浴
                震三宫(卯)→  帝旺  临官  沐浴  病    沐浴  病    胎    绝    死    长生
                巽四宫(辰)→  衰    冠带  冠带  衰    冠带  衰    养    墓    墓    养
                巽四宫(巳)→  病    沐浴  临官  帝旺  临官  帝旺  长生  死    绝    胎
                离九宫(午)→  死    长生  帝旺  临官  帝旺  临官  沐浴  病    胎    绝
                坤二宫(未)→  墓    养    衰    冠带  衰    冠带  冠带  衰    养    墓
                坤二宫(申)→  绝    胎    病    沐浴  病    沐浴  临官  帝旺  长生  死
                兑七宫(酉)→  胎    绝    死    长生  死    长生  帝旺  临官  沐浴  病
                乾六宫(戌)→  养    墓    墓    养    墓    养    衰    冠带  冠带  衰
                乾六宫(亥)→  长生  死    绝    胎    绝    胎    病    沐浴  临官  帝旺
         */ {
            put(Arrays.asList("甲", "子"), "沐浴"); // 甲+子：沐浴
            put(Arrays.asList("甲", "丑"), "冠带"); // 甲+丑：冠带
            put(Arrays.asList("甲", "寅"), "临官"); // 甲+寅：临官
            put(Arrays.asList("甲", "卯"), "帝旺"); // 甲+卯：帝旺
            put(Arrays.asList("甲", "辰"), "衰");   // 甲+辰：衰
            put(Arrays.asList("甲", "巳"), "病");   // 甲+巳：病
            put(Arrays.asList("甲", "午"), "死");   // 甲+午：死
            put(Arrays.asList("甲", "未"), "墓");   // 甲+未：墓
            put(Arrays.asList("甲", "申"), "绝");   // 甲+申：绝
            put(Arrays.asList("甲", "酉"), "胎");   // 甲+酉：胎
            put(Arrays.asList("甲", "戌"), "养");   // 甲+戌：养
            put(Arrays.asList("甲", "亥"), "长生"); // 甲+亥：长生
            put(Arrays.asList("乙", "子"), "病");   // 乙+子：病
            put(Arrays.asList("乙", "丑"), "衰");   // 乙+丑：衰
            put(Arrays.asList("乙", "寅"), "帝旺"); // 乙+寅：帝旺
            put(Arrays.asList("乙", "卯"), "临官"); // 乙+卯：临官
            put(Arrays.asList("乙", "辰"), "冠带"); // 乙+辰：冠带
            put(Arrays.asList("乙", "巳"), "沐浴"); // 乙+巳：沐浴
            put(Arrays.asList("乙", "午"), "长生"); // 乙+午：长生
            put(Arrays.asList("乙", "未"), "养");   // 乙+未：养
            put(Arrays.asList("乙", "申"), "胎");   // 乙+申：胎
            put(Arrays.asList("乙", "酉"), "绝");   // 乙+酉：绝
            put(Arrays.asList("乙", "戌"), "墓");   // 乙+戌：墓
            put(Arrays.asList("乙", "亥"), "死");   // 乙+亥：死
            put(Arrays.asList("丙", "子"), "胎");   // 丙+子：胎
            put(Arrays.asList("丙", "丑"), "养");   // 丙+丑：养
            put(Arrays.asList("丙", "寅"), "长生"); // 丙+寅：长生
            put(Arrays.asList("丙", "卯"), "沐浴"); // 丙+卯：沐浴
            put(Arrays.asList("丙", "辰"), "冠带"); // 丙+辰：冠带
            put(Arrays.asList("丙", "巳"), "临官"); // 丙+巳：临官
            put(Arrays.asList("丙", "午"), "帝旺"); // 丙+午：帝旺
            put(Arrays.asList("丙", "未"), "衰");   // 丙+未：衰
            put(Arrays.asList("丙", "申"), "病");   // 丙+申：病
            put(Arrays.asList("丙", "酉"), "死");   // 丙+酉：死
            put(Arrays.asList("丙", "戌"), "墓");   // 丙+戌：墓
            put(Arrays.asList("丙", "亥"), "绝");   // 丙+亥：绝
            put(Arrays.asList("丁", "子"), "绝");   // 丁+子：绝
            put(Arrays.asList("丁", "丑"), "墓");   // 丁+丑：墓
            put(Arrays.asList("丁", "寅"), "死");   // 丁+寅：死
            put(Arrays.asList("丁", "卯"), "病");   // 丁+卯：病
            put(Arrays.asList("丁", "辰"), "衰");   // 丁+辰：衰
            put(Arrays.asList("丁", "巳"), "帝旺"); // 丁+巳：帝旺
            put(Arrays.asList("丁", "午"), "临官"); // 丁+午：临官
            put(Arrays.asList("丁", "未"), "冠带"); // 丁+未：冠带
            put(Arrays.asList("丁", "申"), "沐浴"); // 丁+申：沐浴
            put(Arrays.asList("丁", "酉"), "长生"); // 丁+酉：长生
            put(Arrays.asList("丁", "戌"), "养");   // 丁+戌：养
            put(Arrays.asList("丁", "亥"), "胎");   // 丁+亥：胎
            put(Arrays.asList("戊", "子"), "胎");   // 戊+子：胎
            put(Arrays.asList("戊", "丑"), "养");   // 戊+丑：养
            put(Arrays.asList("戊", "寅"), "长生"); // 戊+寅：长生
            put(Arrays.asList("戊", "卯"), "沐浴"); // 戊+卯：沐浴
            put(Arrays.asList("戊", "辰"), "冠带"); // 戊+辰：冠带
            put(Arrays.asList("戊", "巳"), "临官"); // 戊+巳：临官
            put(Arrays.asList("戊", "午"), "帝旺"); // 戊+午：帝旺
            put(Arrays.asList("戊", "未"), "衰");   // 戊+未：衰
            put(Arrays.asList("戊", "申"), "病");   // 戊+申：病
            put(Arrays.asList("戊", "酉"), "死");   // 戊+酉：死
            put(Arrays.asList("戊", "戌"), "墓");   // 戊+戌：墓
            put(Arrays.asList("戊", "亥"), "绝");   // 戊+亥：绝
            put(Arrays.asList("己", "子"), "绝");   // 己+子：绝
            put(Arrays.asList("己", "丑"), "墓");   // 己+丑：墓
            put(Arrays.asList("己", "寅"), "死");   // 己+寅：死
            put(Arrays.asList("己", "卯"), "病");   // 己+卯：病
            put(Arrays.asList("己", "辰"), "衰");   // 己+辰：衰
            put(Arrays.asList("己", "巳"), "帝旺"); // 己+巳：帝旺
            put(Arrays.asList("己", "午"), "临官"); // 己+午：临官
            put(Arrays.asList("己", "未"), "冠带"); // 己+未：冠带
            put(Arrays.asList("己", "申"), "沐浴"); // 己+申：沐浴
            put(Arrays.asList("己", "酉"), "长生"); // 己+酉：长生
            put(Arrays.asList("己", "戌"), "养");   // 己+戌：养
            put(Arrays.asList("己", "亥"), "胎");   // 己+亥：胎
            put(Arrays.asList("庚", "子"), "死");   // 庚+子：死
            put(Arrays.asList("庚", "丑"), "墓");   // 庚+丑：墓
            put(Arrays.asList("庚", "寅"), "绝");   // 庚+寅：绝
            put(Arrays.asList("庚", "卯"), "胎");   // 庚+卯：胎
            put(Arrays.asList("庚", "辰"), "养");   // 庚+辰：养
            put(Arrays.asList("庚", "巳"), "长生"); // 庚+巳：长生
            put(Arrays.asList("庚", "午"), "沐浴"); // 庚+午：沐浴
            put(Arrays.asList("庚", "未"), "冠带"); // 庚+未：冠带
            put(Arrays.asList("庚", "申"), "临官"); // 庚+申：临官
            put(Arrays.asList("庚", "酉"), "帝旺"); // 庚+酉：帝旺
            put(Arrays.asList("庚", "戌"), "衰");   // 庚+戌：衰
            put(Arrays.asList("庚", "亥"), "病");   // 庚+亥：病
            put(Arrays.asList("辛", "子"), "长生"); // 辛+子：长生
            put(Arrays.asList("辛", "丑"), "养");   // 辛+丑：养
            put(Arrays.asList("辛", "寅"), "胎");   // 辛+寅：胎
            put(Arrays.asList("辛", "卯"), "绝");   // 辛+卯：绝
            put(Arrays.asList("辛", "辰"), "墓");   // 辛+辰：墓
            put(Arrays.asList("辛", "巳"), "死");   // 辛+巳：死
            put(Arrays.asList("辛", "午"), "病");   // 辛+午：病
            put(Arrays.asList("辛", "未"), "衰");   // 辛+未：衰
            put(Arrays.asList("辛", "申"), "帝旺"); // 辛+申：帝旺
            put(Arrays.asList("辛", "酉"), "临官"); // 辛+酉：临官
            put(Arrays.asList("辛", "戌"), "冠带"); // 辛+戌：冠带
            put(Arrays.asList("辛", "亥"), "沐浴"); // 辛+亥：沐浴
            put(Arrays.asList("壬", "子"), "帝旺"); // 壬+子：帝旺
            put(Arrays.asList("壬", "丑"), "衰");   // 壬+丑：衰
            put(Arrays.asList("壬", "寅"), "病");   // 壬+寅：病
            put(Arrays.asList("壬", "卯"), "死");   // 壬+卯：死
            put(Arrays.asList("壬", "辰"), "墓");   // 壬+辰：墓
            put(Arrays.asList("壬", "巳"), "绝");   // 壬+巳：绝
            put(Arrays.asList("壬", "午"), "胎");   // 壬+午：胎
            put(Arrays.asList("壬", "未"), "养");   // 壬+未：养
            put(Arrays.asList("壬", "申"), "长生"); // 壬+申：长生
            put(Arrays.asList("壬", "酉"), "沐浴"); // 壬+酉：沐浴
            put(Arrays.asList("壬", "戌"), "冠带"); // 壬+戌：冠带
            put(Arrays.asList("壬", "亥"), "临官"); // 壬+亥：临官
            put(Arrays.asList("癸", "子"), "临官"); // 癸+子：临官
            put(Arrays.asList("癸", "丑"), "冠带"); // 癸+丑：冠带
            put(Arrays.asList("癸", "寅"), "沐浴"); // 癸+寅：沐浴
            put(Arrays.asList("癸", "卯"), "长生"); // 癸+卯：长生
            put(Arrays.asList("癸", "辰"), "养");   // 癸+辰：养
            put(Arrays.asList("癸", "巳"), "胎");   // 癸+巳：胎
            put(Arrays.asList("癸", "午"), "绝");   // 癸+午：绝
            put(Arrays.asList("癸", "未"), "墓");   // 癸+未：墓
            put(Arrays.asList("癸", "申"), "死");   // 癸+申：死
            put(Arrays.asList("癸", "酉"), "病");   // 癸+酉：病
            put(Arrays.asList("癸", "戌"), "衰");   // 癸+戌：衰
            put(Arrays.asList("癸", "亥"), "帝旺"); // 癸+亥：帝旺
            put(Arrays.asList("甲", ""), "");
            put(Arrays.asList("乙", ""), "");
            put(Arrays.asList("丙", ""), "");
            put(Arrays.asList("丁", ""), "");
            put(Arrays.asList("戊", ""), "");
            put(Arrays.asList("己", ""), "");
            put(Arrays.asList("庚", ""), "");
            put(Arrays.asList("辛", ""), "");
            put(Arrays.asList("壬", ""), "");
            put(Arrays.asList("癸", ""), "");
        }
    };

    /**
     * 阴阳遁内外盘宫位标识（阴\阳遁为键）
     */
    public static final Map<String, List<String>> YIN_YANG_GONG_MARK = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("阳遁", Arrays.asList("内", "外", "内", "内", "", "外", "外", "内", "外")); // 阳遁
            put("阴遁", Arrays.asList("外", "内", "外", "外", "", "内", "内", "外", "内")); // 阴遁
        }
    };

    /**
     * 九宫宫位（0~8为键）
     */
    public static final Map<Integer, String> JIU_GONG_GONG_WEI = new HashMap<Integer, String>() {
        private static final long serialVersionUID = -1;

        {
            put(0, "坎一宫");
            put(1, "坤二宫");
            put(2, "震三宫");
            put(3, "巽四宫");
            put(4, "中五宫");
            put(5, "乾六宫");
            put(6, "兑七宫");
            put(7, "艮八宫");
            put(8, "离九宫");
        }
    };

    /**
     * 六仪击刑（天盘干+宫位为键）
     */
    public static final Map<String, String> LIU_YI_JI_XING = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("戊3", "戊击刑（震三宫）");
            put("己2", "己击刑（坤二宫）");
            put("庚8", "庚击刑（艮八宫）");
            put("辛9", "辛击刑（离九宫）");
            put("壬4", "壬击刑（巽四宫）");
            put("癸4", "癸击刑（巽四宫）");
        }
    };

    /**
     * 奇仪入墓（天盘干+宫位为键）
     */
    public static final Map<String, String> QI_YI_RU_MU = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲2", "甲入墓（坤二宫）");
            put("乙6", "乙入墓（乾六宫）");
            put("丙6", "丙入墓（乾六宫）");
            put("丁8", "丁入墓（艮八宫）");
            put("戊6", "戊入墓（乾六宫）");
            put("己8", "己入墓（艮八宫）");
            put("庚8", "庚入墓（艮八宫）");
            put("辛4", "辛入墓（巽四宫）");
            put("壬4", "壬入墓（巽四宫）");
            put("癸2", "癸入墓（坤二宫）");
        }
    };

    /**
     * 门迫（八门+宫位为键）
     */
    public static final Map<String, String> MEN_PO = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("休门9", "休门门迫（离九宫）");
            put("生门1", "生门门迫（坎一宫）");
            put("伤门8", "伤门门迫（艮八宫）");
            put("伤门2", "伤门门迫（坤二宫）");
            put("杜门8", "杜门门迫（艮八宫）");
            put("杜门2", "杜门门迫（坤二宫）");
            put("景门7", "景门门迫（兑七宫）");
            put("景门6", "景门门迫（乾六宫）");
            put("死门1", "死门门迫（坎一宫）");
            put("惊门3", "惊门门迫（震三宫）");
            put("惊门4", "惊门门迫（巽四宫）");
            put("开门3", "开门门迫（震三宫）");
            put("开门4", "开门门迫（巽四宫）");
        }
    };

    /**
     * 月建落宫顺时针旋转（时支为键）
     */
    public static final Map<String, List<String>> YUE_JIAN_LUO_GONG = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("子", Arrays.asList("建", "危_成", "平", "定_执", "", "闭_开", "收", "满_除", "破")); // 1~9宫
            put("丑", Arrays.asList("闭", "破_危", "满", "平_定", "", "开_收", "成", "除_建", "执"));
            put("寅", Arrays.asList("开", "执_破", "除", "满_平", "", "收_成", "危", "建_闭", "定"));
            put("卯", Arrays.asList("收", "定_执", "建", "除_满", "", "成_危", "破", "闭_开", "平"));
            put("辰", Arrays.asList("成", "平_定", "闭", "建_除", "", "危_破", "执", "开_收", "满"));
            put("巳", Arrays.asList("危", "满_平", "开", "闭_建", "", "破_执", "定", "收_成", "除"));
            put("午", Arrays.asList("破", "除_满", "收", "开_闭", "", "执_定", "平", "成_危", "建"));
            put("未", Arrays.asList("执", "建_除", "成", "收_开", "", "定_平", "满", "危_破", "闭"));
            put("申", Arrays.asList("定", "闭_建", "危", "成_收", "", "平_满", "除", "破_执", "开"));
            put("酉", Arrays.asList("平", "开_闭", "破", "危_成", "", "满_除", "建", "执_定", "收"));
            put("戌", Arrays.asList("满", "收_开", "执", "破_危", "", "除_建", "闭", "定_平", "成"));
            put("亥", Arrays.asList("除", "成_收", "定", "执_破", "", "建_闭", "开", "平_满", "危"));
        }
    };

    /**
     * 月将神落宫顺时针旋转（月将+时支为键）
     */
    public static final Map<String, List<String>> YUE_JIANG_SHEN_LUO_GONG = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("子子", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光")); // 1~9宫
            put("子丑", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("子寅", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("子卯", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("子辰", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("子巳", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("子午", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("子未", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("子申", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("子酉", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("子戌", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("子亥", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));

            put("丑子", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("丑丑", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
            put("丑寅", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("丑卯", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("丑辰", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("丑巳", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("丑午", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("丑未", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("丑申", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("丑酉", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("丑戌", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("丑亥", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));

            put("寅子", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("寅丑", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("寅寅", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
            put("寅卯", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("寅辰", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("寅巳", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("寅午", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("寅未", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("寅申", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("寅酉", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("寅戌", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("寅亥", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));

            put("卯子", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("卯丑", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("卯寅", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("卯卯", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
            put("卯辰", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("卯巳", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("卯午", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("卯未", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("卯申", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("卯酉", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("卯戌", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("卯亥", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));

            put("辰子", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("辰丑", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("辰寅", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("辰卯", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("辰辰", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
            put("辰巳", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("辰午", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("辰未", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("辰申", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("辰酉", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("辰戌", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("辰亥", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));

            put("巳子", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("巳丑", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("巳寅", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("巳卯", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("巳辰", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("巳巳", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
            put("巳午", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("巳未", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("巳申", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("巳酉", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("巳戌", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("巳亥", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));

            put("午子", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("午丑", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("午寅", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("午卯", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("午辰", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("午巳", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("午午", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
            put("午未", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("午申", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("午酉", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("午戌", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("午亥", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));

            put("未子", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("未丑", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("未寅", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("未卯", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("未辰", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("未巳", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("未午", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("未未", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
            put("未申", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("未酉", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("未戌", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("未亥", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));

            put("申子", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("申丑", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("申寅", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("申卯", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("申辰", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("申巳", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("申午", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("申未", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("申申", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
            put("申酉", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("申戌", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("申亥", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));

            put("酉子", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("酉丑", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("酉寅", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("酉卯", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("酉辰", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("酉巳", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("酉午", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("酉未", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("酉申", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("酉酉", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
            put("酉戌", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("酉亥", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));

            put("戌子", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("戌丑", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("戌寅", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("戌卯", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("戌辰", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("戌巳", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("戌午", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("戌未", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("戌申", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("戌酉", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("戌戌", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
            put("戌亥", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));

            put("亥子", Arrays.asList("登明", "胜光_小吉", "功曹", "太冲_天罡", "", "河魁_从魁", "传送", "大吉_神后", "太乙"));
            put("亥丑", Arrays.asList("河魁", "太乙_胜光", "大吉", "功曹_太冲", "", "从魁_传送", "小吉", "神后_登明", "天罡"));
            put("亥寅", Arrays.asList("从魁", "天罡_太乙", "神后", "大吉_功曹", "", "传送_小吉", "胜光", "登明_河魁", "太冲"));
            put("亥卯", Arrays.asList("传送", "太冲_天罡", "登明", "神后_大吉", "", "小吉_胜光", "太乙", "河魁_从魁", "功曹"));
            put("亥辰", Arrays.asList("小吉", "功曹_太冲", "河魁", "登明_神后", "", "胜光_太乙", "天罡", "从魁_传送", "大吉"));
            put("亥巳", Arrays.asList("胜光", "大吉_功曹", "从魁", "河魁_登明", "", "太乙_天罡", "太冲", "传送_小吉", "神后"));
            put("亥午", Arrays.asList("太乙", "神后_大吉", "传送", "从魁_河魁", "", "天罡_太冲", "功曹", "小吉_胜光", "登明"));
            put("亥未", Arrays.asList("天罡", "登明_神后", "小吉", "传送_从魁", "", "太冲_功曹", "大吉", "胜光_太乙", "河魁"));
            put("亥申", Arrays.asList("太冲", "河魁_登明", "胜光", "小吉_传送", "", "功曹_大吉", "神后", "太乙_天罡", "从魁"));
            put("亥酉", Arrays.asList("功曹", "从魁_河魁", "太乙", "胜光_小吉", "", "大吉_神后", "登明", "天罡_太冲", "传送"));
            put("亥戌", Arrays.asList("大吉", "传送_从魁", "天罡", "太乙_胜光", "", "神后_登明", "河魁", "太冲_功曹", "小吉"));
            put("亥亥", Arrays.asList("神后", "小吉_传送", "太冲", "天罡_太乙", "", "登明_河魁", "从魁", "功曹_大吉", "胜光"));
        }
    };


}
