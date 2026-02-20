package xuan.core.meihua.maps;

import java.util.*;

/**
 * 梅花易数 - 基础常量
 *
 * @author 善待
 */
public class MeiHuaJiChuMap {

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
     * 地支对应的数字（地支为键）
     */
    public static final Map<String, Integer> DI_ZHI_SHU = new HashMap<String, Integer>() {
        private static final long serialVersionUID = -1;

        {
            put("子", 1);
            put("丑", 2);
            put("寅", 3);
            put("卯", 4);
            put("辰", 5);
            put("巳", 6);
            put("午", 7);
            put("未", 8);
            put("申", 9);
            put("酉", 10);
            put("戌", 11);
            put("亥", 12);
        }
    };

    /**
     * 先天八卦（索引为键）
     */
    public static final Map<Integer, String> XIAN_TIAN_BA_GUA = new HashMap<Integer, String>() {
        private static final long serialVersionUID = -1;

        {
            put(1, "乾");
            put(2, "兑");
            put(3, "离");
            put(4, "震");
            put(5, "巽");
            put(6, "坎");
            put(7, "艮");
            put(8, "坤");
        }
    };

    /**
     * 八卦卦象（八卦卦名为键）
     */
    public static final Map<String, String> BA_GUA_AS = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("乾", "☰");
            put("兑", "☱");
            put("离", "☲");
            put("震", "☳");
            put("巽", "☴");
            put("坎", "☵");
            put("艮", "☶");
            put("坤", "☷");
        }
    };

    /**
     * 八卦五行（八卦卦名为键）
     */
    public static final Map<String, String> BA_GUA_WU_XING = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("乾", "金");
            put("兑", "金");
            put("离", "火");
            put("震", "木");
            put("巽", "木");
            put("坎", "水");
            put("艮", "土");
            put("坤", "土");
        }
    };

    /**
     * 六十四卦卦名（六十四卦卦象为键）
     */
    public static final Map<String, String> LIU_SHI_SI_GUA = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("䷀", "乾为天");
            put("䷁", "坤为地");
            put("䷂", "水雷屯");
            put("䷃", "山水蒙");
            put("䷄", "水天需");
            put("䷅", "天水讼");
            put("䷆", "地水师");
            put("䷇", "水地比");
            put("䷈", "风天小畜");
            put("䷉", "天泽履");
            put("䷊", "地天泰");
            put("䷋", "天地否");
            put("䷌", "天火同人");
            put("䷍", "火天大有");
            put("䷎", "地山谦");
            put("䷏", "雷地豫");
            put("䷐", "泽雷随");
            put("䷑", "山风蛊");
            put("䷒", "地泽临");
            put("䷓", "风地观");
            put("䷔", "火雷噬嗑");
            put("䷕", "山火贲");
            put("䷖", "山地剥");
            put("䷗", "地雷复");
            put("䷘", "天雷无妄");
            put("䷙", "山天大畜");
            put("䷚", "山雷颐");
            put("䷛", "泽风大过");
            put("䷜", "坎为水");
            put("䷝", "离为火");
            put("䷞", "泽山咸");
            put("䷟", "雷风恒");
            put("䷠", "天山遁");
            put("䷡", "雷天大壮");
            put("䷢", "火地晋");
            put("䷣", "地火明夷");
            put("䷤", "风火家人");
            put("䷥", "火泽睽");
            put("䷦", "水山蹇");
            put("䷧", "雷水解");
            put("䷨", "山泽损");
            put("䷩", "风雷益");
            put("䷪", "泽天夬");
            put("䷫", "天风姤");
            put("䷬", "泽地萃");
            put("䷭", "地风升");
            put("䷮", "泽水困");
            put("䷯", "水风井");
            put("䷰", "泽火革");
            put("䷱", "火风鼎");
            put("䷲", "震为雷");
            put("䷳", "艮为山");
            put("䷴", "风山渐");
            put("䷵", "雷泽归妹");
            put("䷶", "雷火丰");
            put("䷷", "火山旅");
            put("䷸", "巽为风");
            put("䷹", "兑为泽");
            put("䷺", "风水涣");
            put("䷻", "水泽节");
            put("䷼", "风泽中孚");
            put("䷽", "雷山小过");
            put("䷾", "水火既济");
            put("䷿", "火水未济");
        }
    };

    /**
     * 六十四卦卦象（六十四卦卦名为键）
     */
    public static final Map<String, String> LIU_SHI_SI_GUA_AS = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("乾为天", "䷀");
            put("坤为地", "䷁");
            put("水雷屯", "䷂");
            put("山水蒙", "䷃");
            put("水天需", "䷄");
            put("天水讼", "䷅");
            put("地水师", "䷆");
            put("水地比", "䷇");
            put("风天小畜", "䷈");
            put("天泽履", "䷉");
            put("地天泰", "䷊");
            put("天地否", "䷋");
            put("天火同人", "䷌");
            put("火天大有", "䷍");
            put("地山谦", "䷎");
            put("雷地豫", "䷏");
            put("泽雷随", "䷐");
            put("山风蛊", "䷑");
            put("地泽临", "䷒");
            put("风地观", "䷓");
            put("火雷噬嗑", "䷔");
            put("山火贲", "䷕");
            put("山地剥", "䷖");
            put("地雷复", "䷗");
            put("天雷无妄", "䷘");
            put("山天大畜", "䷙");
            put("山雷颐", "䷚");
            put("泽风大过", "䷛");
            put("坎为水", "䷜");
            put("离为火", "䷝");
            put("泽山咸", "䷞");
            put("雷风恒", "䷟");
            put("天山遁", "䷠");
            put("雷天大壮", "䷡");
            put("火地晋", "䷢");
            put("地火明夷", "䷣");
            put("风火家人", "䷤");
            put("火泽睽", "䷥");
            put("水山蹇", "䷦");
            put("雷水解", "䷧");
            put("山泽损", "䷨");
            put("风雷益", "䷩");
            put("泽天夬", "䷪");
            put("天风姤", "䷫");
            put("泽地萃", "䷬");
            put("地风升", "䷭");
            put("泽水困", "䷮");
            put("水风井", "䷯");
            put("泽火革", "䷰");
            put("火风鼎", "䷱");
            put("震为雷", "䷲");
            put("艮为山", "䷳");
            put("风山渐", "䷴");
            put("雷泽归妹", "䷵");
            put("雷火丰", "䷶");
            put("火山旅", "䷷");
            put("巽为风", "䷸");
            put("兑为泽", "䷹");
            put("风水涣", "䷺");
            put("水泽节", "䷻");
            put("风泽中孚", "䷼");
            put("雷山小过", "䷽");
            put("水火既济", "䷾");
            put("火水未济", "䷿");
        }

    };

    /**
     * 六十四卦卦名（上卦数+下卦数为键）
     */
    public static final Map<List<Integer>, String> LIU_SHI_SI_GUA_NAME = new HashMap<List<Integer>, String>() {
        private static final long serialVersionUID = -1;

        {
            put(Arrays.asList(1, 1), "乾为天");
            put(Arrays.asList(8, 8), "坤为地");
            put(Arrays.asList(6, 4), "水雷屯");
            put(Arrays.asList(7, 6), "山水蒙");
            put(Arrays.asList(6, 1), "水天需");
            put(Arrays.asList(1, 6), "天水讼");
            put(Arrays.asList(8, 6), "地水师");
            put(Arrays.asList(6, 8), "水地比");
            put(Arrays.asList(5, 1), "风天小畜");
            put(Arrays.asList(1, 2), "天泽履");
            put(Arrays.asList(8, 1), "地天泰");
            put(Arrays.asList(1, 8), "天地否");
            put(Arrays.asList(1, 3), "天火同人");
            put(Arrays.asList(3, 1), "火天大有");
            put(Arrays.asList(8, 7), "地山谦");
            put(Arrays.asList(4, 8), "雷地豫");
            put(Arrays.asList(2, 4), "泽雷随");
            put(Arrays.asList(7, 5), "山风蛊");
            put(Arrays.asList(8, 2), "地泽临");
            put(Arrays.asList(5, 8), "风地观");
            put(Arrays.asList(3, 4), "火雷噬嗑");
            put(Arrays.asList(7, 3), "山火贲");
            put(Arrays.asList(7, 8), "山地剥");
            put(Arrays.asList(8, 4), "地雷复");
            put(Arrays.asList(1, 4), "天雷无妄");
            put(Arrays.asList(7, 1), "山天大畜");
            put(Arrays.asList(7, 4), "山雷颐");
            put(Arrays.asList(2, 5), "泽风大过");
            put(Arrays.asList(6, 6), "坎为水");
            put(Arrays.asList(3, 3), "离为火");
            put(Arrays.asList(2, 7), "泽山咸");
            put(Arrays.asList(4, 5), "雷风恒");
            put(Arrays.asList(1, 7), "天山遁");
            put(Arrays.asList(4, 1), "雷天大壮");
            put(Arrays.asList(3, 8), "火地晋");
            put(Arrays.asList(8, 3), "地火明夷");
            put(Arrays.asList(5, 3), "风火家人");
            put(Arrays.asList(3, 2), "火泽睽");
            put(Arrays.asList(6, 7), "水山蹇");
            put(Arrays.asList(4, 6), "雷水解");
            put(Arrays.asList(7, 2), "山泽损");
            put(Arrays.asList(5, 4), "风雷益");
            put(Arrays.asList(2, 1), "泽天夬");
            put(Arrays.asList(1, 5), "天风姤");
            put(Arrays.asList(2, 8), "泽地萃");
            put(Arrays.asList(8, 5), "地风升");
            put(Arrays.asList(2, 6), "泽水困");
            put(Arrays.asList(6, 5), "水风井");
            put(Arrays.asList(2, 3), "泽火革");
            put(Arrays.asList(3, 5), "火风鼎");
            put(Arrays.asList(4, 4), "震为雷");
            put(Arrays.asList(7, 7), "艮为山");
            put(Arrays.asList(5, 7), "风山渐");
            put(Arrays.asList(4, 2), "雷泽归妹");
            put(Arrays.asList(4, 3), "雷火丰");
            put(Arrays.asList(3, 7), "火山旅");
            put(Arrays.asList(5, 5), "巽为风");
            put(Arrays.asList(2, 2), "兑为泽");
            put(Arrays.asList(5, 6), "风水涣");
            put(Arrays.asList(6, 2), "水泽节");
            put(Arrays.asList(5, 2), "风泽中孚");
            put(Arrays.asList(4, 7), "雷山小过");
            put(Arrays.asList(6, 3), "水火既济");
            put(Arrays.asList(3, 6), "火水未济");
        }

    };

    /**
     * 六十四卦包含的两个卦名（六十四卦卦名为键）
     */
    public static final Map<String, List<String>> LIU_SHI_SI_GUA_TWO_GUA_NAME = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("乾为天", Arrays.asList("乾", "乾"));
            put("坤为地", Arrays.asList("坤", "坤"));
            put("水雷屯", Arrays.asList("坎", "震"));
            put("山水蒙", Arrays.asList("艮", "坎"));
            put("水天需", Arrays.asList("坎", "乾"));
            put("天水讼", Arrays.asList("乾", "坎"));
            put("地水师", Arrays.asList("坤", "坎"));
            put("水地比", Arrays.asList("坎", "坤"));
            put("风天小畜", Arrays.asList("巽", "乾"));
            put("天泽履", Arrays.asList("乾", "兑"));
            put("地天泰", Arrays.asList("坤", "乾"));
            put("天地否", Arrays.asList("乾", "坤"));
            put("天火同人", Arrays.asList("乾", "离"));
            put("火天大有", Arrays.asList("离", "乾"));
            put("地山谦", Arrays.asList("坤", "艮"));
            put("雷地豫", Arrays.asList("震", "坤"));
            put("泽雷随", Arrays.asList("兑", "震"));
            put("山风蛊", Arrays.asList("艮", "巽"));
            put("地泽临", Arrays.asList("坤", "兑"));
            put("风地观", Arrays.asList("巽", "坤"));
            put("火雷噬嗑", Arrays.asList("离", "震"));
            put("山火贲", Arrays.asList("艮", "离"));
            put("山地剥", Arrays.asList("艮", "坤"));
            put("地雷复", Arrays.asList("坤", "震"));
            put("天雷无妄", Arrays.asList("乾", "震"));
            put("山天大畜", Arrays.asList("艮", "乾"));
            put("山雷颐", Arrays.asList("艮", "震"));
            put("泽风大过", Arrays.asList("兑", "巽"));
            put("坎为水", Arrays.asList("坎", "坎"));
            put("离为火", Arrays.asList("离", "离"));
            put("泽山咸", Arrays.asList("兑", "艮"));
            put("雷风恒", Arrays.asList("震", "巽"));
            put("天山遁", Arrays.asList("乾", "艮"));
            put("雷天大壮", Arrays.asList("震", "乾"));
            put("火地晋", Arrays.asList("离", "坤"));
            put("地火明夷", Arrays.asList("坤", "离"));
            put("风火家人", Arrays.asList("巽", "离"));
            put("火泽睽", Arrays.asList("离", "兑"));
            put("水山蹇", Arrays.asList("坎", "艮"));
            put("雷水解", Arrays.asList("震", "坎"));
            put("山泽损", Arrays.asList("艮", "兑"));
            put("风雷益", Arrays.asList("巽", "震"));
            put("泽天夬", Arrays.asList("兑", "乾"));
            put("天风姤", Arrays.asList("乾", "巽"));
            put("泽地萃", Arrays.asList("兑", "坤"));
            put("地风升", Arrays.asList("坤", "巽"));
            put("泽水困", Arrays.asList("兑", "坎"));
            put("水风井", Arrays.asList("坎", "巽"));
            put("泽火革", Arrays.asList("兑", "离"));
            put("火风鼎", Arrays.asList("离", "巽"));
            put("震为雷", Arrays.asList("震", "震"));
            put("艮为山", Arrays.asList("艮", "艮"));
            put("风山渐", Arrays.asList("巽", "艮"));
            put("雷泽归妹", Arrays.asList("震", "兑"));
            put("雷火丰", Arrays.asList("震", "离"));
            put("火山旅", Arrays.asList("离", "艮"));
            put("巽为风", Arrays.asList("巽", "巽"));
            put("兑为泽", Arrays.asList("兑", "兑"));
            put("风水涣", Arrays.asList("巽", "坎"));
            put("水泽节", Arrays.asList("坎", "兑"));
            put("风泽中孚", Arrays.asList("巽", "兑"));
            put("雷山小过", Arrays.asList("震", "艮"));
            put("水火既济", Arrays.asList("坎", "离"));
            put("火水未济", Arrays.asList("离", "坎"));
        }
    };

    /**
     * 六十四卦类型、卦身、卦辞（六十四卦卦名为键）
     */
    public static final Map<String, List<String>> LIU_SHI_SI_GUA_SHEN_CI = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("乾为天", Arrays.asList("八纯", "巳", "元，亨，利，贞。"));
            put("坤为地", Arrays.asList("八纯", "亥", "元，亨，利牝马之贞。君子有攸往，先迷后得主利，西南得朋，东北丧朋。安贞吉。"));
            put("水雷屯", Arrays.asList("二世", "未", "元亨，利贞。勿用有攸往，利建侯。"));
            put("山水蒙", Arrays.asList("四世", "酉", "亨。匪我求童蒙，童蒙求我。初筮告，再三渎，渎则不告。利贞。"));
            put("水天需", Arrays.asList("游魂", "酉", "有孚，光亨贞吉。利涉大川。"));
            put("天水讼", Arrays.asList("游魂", "卯", "有孚，窒惕。中吉，终凶。利见大人，不利涉大川。"));
            put("地水师", Arrays.asList("归魂", "申", "贞，丈人吉，无咎。"));
            put("水地比", Arrays.asList("归魂", "申", "吉。原筮，元永贞，无咎。不宁方来，后夫凶。"));
            put("风天小畜", Arrays.asList("一世", "子", "亨。密云不雨，自我西郊。"));
            put("天泽履", Arrays.asList("五世", "辰", "虎尾，不咥人，亨。"));
            put("地天泰", Arrays.asList("三世", "寅", "小往大来，吉，亨。"));
            put("天地否", Arrays.asList("三世", "申", "否之匪人，不利君子贞，大往小来。"));
            put("天火同人", Arrays.asList("归魂", "寅", "同人于野，亨。利涉大川，利君子贞。"));
            put("火天大有", Arrays.asList("归魂", "寅", "元亨。"));
            put("地山谦", Arrays.asList("五世", "戌", "亨，君子有终。"));
            put("雷地豫", Arrays.asList("一世", "午", "利建侯，行师。"));
            put("泽雷随", Arrays.asList("归魂", "申", "元亨，利贞，无咎。"));
            put("山风蛊", Arrays.asList("归魂", "寅", "元亨，利涉大川，先甲三日，后甲三日。"));
            put("地泽临", Arrays.asList("二世", "丑", "元亨，利贞。至于八月有凶。"));
            put("风地观", Arrays.asList("四世", "酉", "盥而不荐，有孚颙若。"));
            put("火雷噬嗑", Arrays.asList("五世", "戌", "亨，利用狱。"));
            put("山火贲", Arrays.asList("一世", "子", "亨，小利有攸往。"));
            put("山地剥", Arrays.asList("五世", "戌", "不利有攸往。"));
            put("地雷复", Arrays.asList("一世", "子", "亨，出入无疾，朋来，无吝。反复其道，七日来复，利有攸往。"));
            put("天雷无妄", Arrays.asList("四世", "卯", "元亨利贞。其匪正有眚，不利有攸往。"));
            put("山天大畜", Arrays.asList("二世", "丑", "利贞。不家食、吉。利涉大川。"));
            put("山雷颐", Arrays.asList("游魂", "酉", "贞吉。观颐，自求口实。"));
            put("泽风大过", Arrays.asList("游魂", "卯", "栋桡，利于攸往，亨。"));
            put("坎为水", Arrays.asList("八纯", "亥", "习坎有孚维心，亨，行有尚。"));
            put("离为火", Arrays.asList("八纯", "巳", "利贞，亨。畜牛牝，吉。"));
            put("泽山咸", Arrays.asList("三世", "寅", "亨，利贞。娶女，吉。"));
            put("雷风恒", Arrays.asList("三世", "寅", "亨，无吝，利贞，利有攸往。"));
            put("天山遁", Arrays.asList("二世", "未", "亨，小利贞。"));
            put("雷天大壮", Arrays.asList("四世", "卯", "利贞。"));
            put("火地晋", Arrays.asList("游魂", "卯", "康侯用锡马蕃蔗，昼日三接。"));
            put("地火明夷", Arrays.asList("游魂", "酉", "利艰贞。"));
            put("风火家人", Arrays.asList("二世", "未", "利女贞。"));
            put("火泽睽", Arrays.asList("四世", "卯", "小事吉。"));
            put("水山蹇", Arrays.asList("四世", "辰", "利西南，不利东北，利见大人，贞吉。"));
            put("雷水解", Arrays.asList("二世", "丑", "利西南，无所往，其来复，吉。有攸往，夙吉。"));
            put("山泽损", Arrays.asList("三世", "申", "有孚，元吉，无咎，可贞，利有攸往。曷之用？二簋可用享。"));
            put("风雷益", Arrays.asList("三世", "申", "利有攸往，利涉大川。"));
            put("泽天夬", Arrays.asList("五世", "辰", "杨于王庭，孚号有厉，告自邑，不利即戎，利有攸往。"));
            put("天风姤", Arrays.asList("一世", "午", "女壮，勿用取女。"));
            put("泽地萃", Arrays.asList("二世", "未", "亨。王假有庙。利见大人，亨，利贞，用大牲吉，利有攸往。"));
            put("地风升", Arrays.asList("四世", "酉", "元亨，用见大人，勿恤，南征吉。"));
            put("泽水困", Arrays.asList("一世", "午", "亨，贞，大人吉，无咎。有言不信。"));
            put("水风井", Arrays.asList("五世", "辰", "改邑不改井。无丧无得，往来井井。汔至，亦未繘井，赢其瓶，凶。"));
            put("泽火革", Arrays.asList("四世", "卯", "巳日乃孚，元亨利贞，悔亡。"));
            put("火风鼎", Arrays.asList("二世", "丑", "元吉，亨。"));
            put("震为雷", Arrays.asList("八纯", "亥", "亨，震来虩虩，笑言哑哑，震惊百里，不丧匕鬯。"));
            put("艮为山", Arrays.asList("八纯", "巳", "艮其背，不获其身，行其庭，不见其人，无咎。"));
            put("风山渐", Arrays.asList("归魂", "寅", "女归，吉，利贞。"));
            put("雷泽归妹", Arrays.asList("归魂", "申", "征凶，无攸利。"));
            put("雷火丰", Arrays.asList("五世", "戌", "亨，王假之，勿忧，宜日中。"));
            put("火山旅", Arrays.asList("一世", "午", "小亨，旅，贞吉。"));
            put("巽为风", Arrays.asList("八纯", "巳", "小亨，利有攸往，利见大人。"));
            put("兑为泽", Arrays.asList("八纯", "亥", "亨，利贞。"));
            put("风水涣", Arrays.asList("五世", "辰", "亨。王假有庙，利涉大川，利贞。"));
            put("水泽节", Arrays.asList("一世", "子", "亨，苦节不可贞。"));
            put("风泽中孚", Arrays.asList("游魂", "酉", "豚鱼吉。利涉大川。利贞。"));
            put("雷山小过", Arrays.asList("游魂", "卯", "亨，利贞，可小事，不可大事；飞鸟遗之音，不宜上，宜下，大吉。"));
            put("水火既济", Arrays.asList("三世", "寅", "亨小，利贞。初吉，终乱。"));
            put("火水未济", Arrays.asList("三世", "申", "亨。小狐汔济，濡其尾，无攸利。"));
        }
    };

    /**
     * 六十四卦的六爻爻象（六十四卦卦象为键）
     */
    public static final Map<String, List<String>> LIU_SHI_SI_GUA_LIU_YAO_AS = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        /* 依次为：初爻、二爻、三爻、四爻、五爻、上爻 */ {
            put("䷀", Arrays.asList("—", "—", "—", "—", "—", "—"));
            put("䷁", Arrays.asList("--", "--", "--", "--", "--", "--"));
            put("䷂", Arrays.asList("—", "--", "--", "--", "—", "--"));
            put("䷃", Arrays.asList("--", "—", "--", "--", "--", "—"));
            put("䷄", Arrays.asList("—", "—", "—", "--", "—", "--"));
            put("䷅", Arrays.asList("--", "—", "--", "—", "—", "—"));
            put("䷆", Arrays.asList("--", "—", "--", "--", "--", "--"));
            put("䷇", Arrays.asList("--", "--", "--", "--", "—", "--"));
            put("䷈", Arrays.asList("—", "—", "—", "--", "—", "—"));
            put("䷉", Arrays.asList("—", "—", "--", "—", "—", "—"));
            put("䷊", Arrays.asList("—", "—", "—", "--", "--", "--"));
            put("䷋", Arrays.asList("--", "--", "--", "—", "—", "—"));
            put("䷌", Arrays.asList("—", "--", "—", "—", "—", "—"));
            put("䷍", Arrays.asList("—", "—", "—", "—", "--", "—"));
            put("䷎", Arrays.asList("--", "--", "—", "--", "--", "--"));
            put("䷏", Arrays.asList("--", "--", "--", "—", "--", "--"));
            put("䷐", Arrays.asList("—", "--", "--", "—", "—", "--"));
            put("䷑", Arrays.asList("--", "—", "—", "--", "--", "—"));
            put("䷒", Arrays.asList("—", "—", "--", "--", "--", "--"));
            put("䷓", Arrays.asList("--", "--", "--", "--", "—", "—"));
            put("䷔", Arrays.asList("—", "--", "--", "—", "--", "—"));
            put("䷕", Arrays.asList("—", "--", "—", "--", "--", "—"));
            put("䷖", Arrays.asList("--", "--", "--", "--", "--", "—"));
            put("䷗", Arrays.asList("—", "--", "--", "--", "--", "--"));
            put("䷘", Arrays.asList("—", "--", "--", "—", "—", "—"));
            put("䷙", Arrays.asList("—", "—", "—", "--", "--", "—"));
            put("䷚", Arrays.asList("—", "--", "--", "--", "--", "—"));
            put("䷛", Arrays.asList("--", "—", "—", "—", "—", "--"));
            put("䷜", Arrays.asList("--", "—", "--", "--", "—", "--"));
            put("䷝", Arrays.asList("—", "--", "—", "—", "--", "—"));
            put("䷞", Arrays.asList("--", "--", "—", "—", "—", "--"));
            put("䷟", Arrays.asList("--", "—", "—", "—", "--", "--"));
            put("䷠", Arrays.asList("--", "--", "—", "—", "—", "—"));
            put("䷡", Arrays.asList("—", "—", "—", "—", "--", "--"));
            put("䷢", Arrays.asList("--", "--", "--", "—", "--", "—"));
            put("䷣", Arrays.asList("—", "--", "—", "--", "--", "--"));
            put("䷤", Arrays.asList("—", "--", "—", "--", "—", "—"));
            put("䷥", Arrays.asList("—", "—", "--", "—", "--", "—"));
            put("䷦", Arrays.asList("--", "--", "—", "--", "—", "--"));
            put("䷧", Arrays.asList("--", "—", "--", "—", "--", "--"));
            put("䷨", Arrays.asList("—", "—", "--", "--", "--", "—"));
            put("䷩", Arrays.asList("—", "--", "--", "--", "—", "—"));
            put("䷪", Arrays.asList("—", "—", "—", "—", "—", "--"));
            put("䷫", Arrays.asList("--", "—", "—", "—", "—", "—"));
            put("䷬", Arrays.asList("--", "--", "--", "—", "—", "--"));
            put("䷭", Arrays.asList("--", "—", "—", "--", "--", "--"));
            put("䷮", Arrays.asList("--", "—", "--", "—", "—", "--"));
            put("䷯", Arrays.asList("--", "—", "—", "--", "—", "--"));
            put("䷰", Arrays.asList("—", "--", "—", "—", "—", "--"));
            put("䷱", Arrays.asList("--", "—", "—", "—", "--", "—"));
            put("䷲", Arrays.asList("—", "--", "--", "—", "--", "--"));
            put("䷳", Arrays.asList("--", "--", "—", "--", "--", "—"));
            put("䷴", Arrays.asList("--", "--", "—", "--", "—", "—"));
            put("䷵", Arrays.asList("—", "—", "--", "—", "--", "--"));
            put("䷶", Arrays.asList("—", "--", "—", "—", "--", "--"));
            put("䷷", Arrays.asList("--", "--", "—", "—", "--", "—"));
            put("䷸", Arrays.asList("--", "—", "—", "--", "—", "—"));
            put("䷹", Arrays.asList("—", "—", "--", "—", "—", "--"));
            put("䷺", Arrays.asList("--", "—", "--", "--", "—", "—"));
            put("䷻", Arrays.asList("—", "—", "--", "--", "—", "--"));
            put("䷼", Arrays.asList("—", "—", "--", "--", "—", "—"));
            put("䷽", Arrays.asList("--", "--", "—", "—", "--", "--"));
            put("䷾", Arrays.asList("—", "--", "—", "--", "—", "--"));
            put("䷿", Arrays.asList("--", "—", "--", "—", "--", "—"));
        }

    };

    /**
     * 六十四卦的六爻爻名（六十四卦卦象为键）
     */
    public static final Map<String, List<String>> LIU_SHI_SI_GUA_LIU_YAO_YAO_MING = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        /* 依次为：初爻、二爻、三爻、四爻、五爻、上爻 */ {
            put("䷀", Arrays.asList("初九", "九二", "九三", "九四", "九五", "上九"));
            put("䷁", Arrays.asList("初六", "六二", "六三", "六四", "六五", "上六"));
            put("䷂", Arrays.asList("初九", "六二", "六三", "六四", "九五", "上六"));
            put("䷃", Arrays.asList("初六", "九二", "六三", "六四", "六五", "上九"));
            put("䷄", Arrays.asList("初九", "九二", "九三", "六四", "九五", "上六"));
            put("䷅", Arrays.asList("初六", "九二", "六三", "九四", "九五", "上九"));
            put("䷆", Arrays.asList("初六", "九二", "六三", "六四", "六五", "上六"));
            put("䷇", Arrays.asList("初六", "六二", "六三", "六四", "九五", "上六"));
            put("䷈", Arrays.asList("初九", "九二", "九三", "六四", "九五", "上九"));
            put("䷉", Arrays.asList("初九", "九二", "六三", "九四", "九五", "上九"));
            put("䷊", Arrays.asList("初九", "九二", "九三", "六四", "六五", "上六"));
            put("䷋", Arrays.asList("初六", "六二", "六三", "九四", "九五", "上九"));
            put("䷌", Arrays.asList("初九", "六二", "九三", "九四", "九五", "上九"));
            put("䷍", Arrays.asList("初九", "九二", "九三", "九四", "六五", "上九"));
            put("䷎", Arrays.asList("初六", "六二", "九三", "六四", "六五", "上六"));
            put("䷏", Arrays.asList("初六", "六二", "六三", "九四", "六五", "上六"));
            put("䷐", Arrays.asList("初九", "六二", "六三", "九四", "九五", "上六"));
            put("䷑", Arrays.asList("初六", "九二", "九三", "六四", "六五", "上九"));
            put("䷒", Arrays.asList("初九", "九二", "六三", "六四", "六五", "上六"));
            put("䷓", Arrays.asList("初六", "六二", "六三", "六四", "九五", "上九"));
            put("䷔", Arrays.asList("初九", "六二", "六三", "九四", "六五", "上九"));
            put("䷕", Arrays.asList("初九", "六二", "九三", "六四", "六五", "上九"));
            put("䷖", Arrays.asList("初六", "六二", "六三", "六四", "六五", "上九"));
            put("䷗", Arrays.asList("初九", "六二", "六三", "六四", "六五", "上六"));
            put("䷘", Arrays.asList("初九", "六二", "六三", "九四", "九五", "上九"));
            put("䷙", Arrays.asList("初九", "九二", "九三", "六四", "六五", "上九"));
            put("䷚", Arrays.asList("初九", "六二", "六三", "六四", "六五", "上九"));
            put("䷛", Arrays.asList("初六", "九二", "九三", "九四", "九五", "上六"));
            put("䷜", Arrays.asList("初六", "九二", "六三", "六四", "九五", "上六"));
            put("䷝", Arrays.asList("初九", "六二", "九三", "九四", "六五", "上九"));
            put("䷞", Arrays.asList("初六", "六二", "九三", "九四", "九五", "上六"));
            put("䷟", Arrays.asList("初六", "九二", "九三", "九四", "六五", "上六"));
            put("䷠", Arrays.asList("初六", "六二", "九三", "九四", "九五", "上九"));
            put("䷡", Arrays.asList("初九", "九二", "九三", "九四", "六五", "上六"));
            put("䷢", Arrays.asList("初六", "六二", "六三", "九四", "六五", "上九"));
            put("䷣", Arrays.asList("初九", "六二", "九三", "六四", "六五", "上六"));
            put("䷤", Arrays.asList("初九", "六二", "九三", "六四", "九五", "上九"));
            put("䷥", Arrays.asList("初九", "九二", "六三", "九四", "六五", "上九"));
            put("䷦", Arrays.asList("初六", "六二", "九三", "六四", "九五", "上六"));
            put("䷧", Arrays.asList("初六", "九二", "六三", "九四", "六五", "上六"));
            put("䷨", Arrays.asList("初九", "九二", "六三", "六四", "六五", "上九"));
            put("䷩", Arrays.asList("初九", "六二", "六三", "六四", "九五", "上九"));
            put("䷪", Arrays.asList("初九", "九二", "九三", "九四", "九五", "上六"));
            put("䷫", Arrays.asList("初六", "九二", "九三", "九四", "九五", "上九"));
            put("䷬", Arrays.asList("初六", "六二", "六三", "九四", "九五", "上六"));
            put("䷭", Arrays.asList("初六", "九二", "九三", "六四", "六五", "上六"));
            put("䷮", Arrays.asList("初六", "九二", "六三", "九四", "九五", "上六"));
            put("䷯", Arrays.asList("初六", "九二", "九三", "六四", "九五", "上六"));
            put("䷰", Arrays.asList("初九", "六二", "九三", "九四", "九五", "上六"));
            put("䷱", Arrays.asList("初六", "九二", "九三", "九四", "六五", "上九"));
            put("䷲", Arrays.asList("初九", "六二", "六三", "九四", "六五", "上六"));
            put("䷳", Arrays.asList("初六", "六二", "九三", "六四", "六五", "上九"));
            put("䷴", Arrays.asList("初六", "六二", "九三", "六四", "九五", "上九"));
            put("䷵", Arrays.asList("初九", "九二", "六三", "九四", "六五", "上六"));
            put("䷶", Arrays.asList("初九", "六二", "九三", "九四", "六五", "上六"));
            put("䷷", Arrays.asList("初六", "六二", "九三", "九四", "六五", "上九"));
            put("䷸", Arrays.asList("初六", "九二", "九三", "六四", "九五", "上九"));
            put("䷹", Arrays.asList("初九", "九二", "六三", "九四", "九五", "上六"));
            put("䷺", Arrays.asList("初六", "九二", "六三", "六四", "九五", "上九"));
            put("䷻", Arrays.asList("初九", "九二", "六三", "六四", "九五", "上六"));
            put("䷼", Arrays.asList("初九", "九二", "六三", "六四", "九五", "上九"));
            put("䷽", Arrays.asList("初六", "六二", "九三", "九四", "六五", "上六"));
            put("䷾", Arrays.asList("初九", "六二", "九三", "六四", "九五", "上六"));
            put("䷿", Arrays.asList("初六", "九二", "六三", "九四", "六五", "上九"));
        }
    };

    /**
     * 六十四卦的六爻爻辞（六十四卦卦象为键）
     */
    public static final Map<String, List<String>> LIU_SHI_SI_GUA_LIU_YAO_YAO_CI = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        /* 依次为：初爻、二爻、三爻、四爻、五爻、上爻 */ {
            put("䷀", Arrays.asList("潜龙勿用。", "见龙在田，利见大人。", "君子终日乾乾，夕惕若厉，无咎。", "或跃在渊，无咎。", "飞龙在天，利见大人。", "亢龙有悔。"));
            put("䷁", Arrays.asList("履霜坚冰至。", "直方大，不习，无不利。", "含章可贞，或从王事，无成有终。", "括囊，无咎无誉。", "黄裳元吉。", "龙战于野，其血玄黄。"));
            put("䷂", Arrays.asList("磐桓，利居贞，利建侯。", "屯如邅如，乘马班如。匪寇，婚媾。女子贞不字，十年乃字。", "即鹿无虞，惟入于林中。君子几，不如舍，往吝。", "乘马班如，求婚媾，往吉，无不利。", "屯其膏，小贞吉，大贞凶。", "乘马班如，泣血涟如。"));
            put("䷃", Arrays.asList("发蒙，利用刑人，用说桎梏。以往吝。", "包蒙，吉。纳妇，吉。子克家。", "勿用取女，见金夫，不有躬，无攸利。", "困蒙，吝。", "童蒙，吉。", "击蒙，不利为寇，利御寇。"));
            put("䷄", Arrays.asList("需于郊，利用恒，无咎。", "需于沙，小有言，终吉。", "需于泥，致寇至。", "需于血，出自穴。", "需于酒食，贞吉。", "入于穴，有不速之客三人来，敬之，终吉。"));
            put("䷅", Arrays.asList("不永所事，小有言，终吉。", "不克讼，归而逋。其邑人三百户，无眚。", "食旧德，贞厉，终吉。或从王事，无成。", "不克讼，复既命，渝，安贞吉。", "讼元，吉。", "或锡之鞶带，终朝三褫之。"));
            put("䷆", Arrays.asList("师出以律，否臧凶。", "在师，中吉，无咎，王三锡命。", "师或舆尸，凶。", "师左次，无咎。", "田有禽，利执；言，无咎。长子帅师；弟子舆尸。贞凶。", "大君有命，开国承家，小人勿用。"));
            put("䷇", Arrays.asList("有孚比之，无咎。有孚盈缶，终来有它吉。", "比之自内，贞吉。", "比之匪人。", "外比之，贞吉。", "显比，王用三驱，失前禽，邑人不诫，吉。", "比之无首，凶。"));
            put("䷈", Arrays.asList("复自道，何其咎？吉。", "牵复，吉。", "舆说辐，夫妻反目。", "有孚，血去惕出，无咎。", "有孚挛如，富以其邻。", "既雨既处，尚德载。妇贞厉，月几望。君子征凶。"));
            put("䷉", Arrays.asList("素履，往无咎。", "履道坦坦，幽人贞吉。", "眇能视，跛能履，履虎尾，咥人，凶。武人为于大君。", "履虎尾，愬愬，终吉。", "夬履，贞厉。", "视履考祥，其旋元吉。"));
            put("䷊", Arrays.asList("拔茅茹，以其汇，征吉。", "包荒，用冯河，不遐遗。朋亡，得尚于中行。", "无平不陂，无往不复，艰贞无咎。勿恤其孚，于食有福。", "翩翩，不富以其邻，不戒以孚。", "帝乙归妹，以祉元吉。", "城复于隍，勿用师。自邑告命，贞吝。"));
            put("䷋", Arrays.asList("拔茅茹，以其汇，贞吉，亨。", "包承，小人吉，大人否，亨。", "包羞。", "有命无咎，畴离祉。", "休否，大人吉，其亡其亡，系于苞桑。", "倾否，先否后喜。"));
            put("䷌", Arrays.asList("同人于门，无咎。", "同人于宗，吝。", "伏戎于莽，升其高陵，三岁不兴。", "乘其墉。弗克攻。吉。", "同人，先号啕而后笑，大师克，相遇。", "同人于郊，无悔。"));
            put("䷍", Arrays.asList("无交害，匪咎，艰者无咎。", "大车以载，有攸往，无咎。", "公用亨于天子，小人弗克。", "匪其彭，无咎。", "厥孚交加，威加，吉。", "自天佑之，吉无不利。"));
            put("䷎", Arrays.asList("谦谦君子，用涉大川，吉。", "鸣谦，贞吉。", "劳谦，君子有终，吉。", "无不利，㧑谦。", "不富以其邻，利用侵伐，无不利。", "鸣谦，利用行师，征邑国。"));
            put("䷏", Arrays.asList("鸣豫，凶。", "介于石，不终日，贞吉。", "盱豫，悔。 迟，有悔。", "由豫，大有得。勿疑， 朋盍簪。", "贞疾，恒不死。", "冥豫，成有渝，无咎。"));
            put("䷐", Arrays.asList("官有渝，贞吉。出门交有功。", "系小子，失丈夫。", "系丈夫，失小子，随有求，得，利居贞。", "随有获，贞凶。有孚在道以明，何咎？", "孚于嘉，吉。", "拘系之，乃从维之，王用亨于西山。"));
            put("䷑", Arrays.asList("干父之蛊，有子，考无咎，厉终吉。", "干母之蛊，不可贞。", "干父之蛊，小有晦，无大咎。", "裕父之蛊，往见吝。", "干父之蛊，用誉。", "不事王侯，高尚其事。"));
            put("䷒", Arrays.asList("咸临，贞吉。", "咸临，吉无不利。", "甘临，无攸利。既忧之，无咎。", "至临，无咎。", "知临，大君之宜，吉。", "敦临，吉，无咎。"));
            put("䷓", Arrays.asList("童观，小人无咎，君子吝。", "窥观，利女贞。", "观我生，进退。", "观国之光，利用宾于王。", "观我生，君子无咎。", "观其生，君子无咎。"));
            put("䷔", Arrays.asList("屦校灭趾，无咎。", "噬肤，灭鼻，无咎。", "噬腊肉，遇毒；小吝，无咎。", "噬干胏，得金矢，利艰贞，吉。", "噬干肉，得黄金，贞厉，无咎。", "何校灭耳，凶。"));
            put("䷕", Arrays.asList("贲其趾，舍车而徒。", "贲其须。", "贲如濡如，永贞吉。", "贲如皤如，白马翰如。匪寇，婚媾。", "贲于丘园，束帛戋戋。吝，终吉。", "白贲，无咎。"));
            put("䷖", Arrays.asList("剥床以足，蔑贞凶。", "剥床以辨，蔑贞凶。", "剥之，无咎。", "剥床以肤，凶。", "贯鱼，以宫人宠，无不利。", "硕果不食，君子得舆，小人剥庐。"));
            put("䷗", Arrays.asList("不远复，无祗悔，元吉。", "休复，吉。", "频复，厉，无咎。", "中行独复。", "敦复，无悔。", "迷复，凶，有灾眚。用行师，终以大败。以其国君凶，至于十年不克征。"));
            put("䷘", Arrays.asList("无妄，往吉。", "不耕获，不菑畲，则利有攸往。", "无妄之灾，或系之牛，行人之得，邑人之灾。", "可贞，无咎。", "无妄之疾，勿药有喜。", "无妄，行有眚，无攸利。"));
            put("䷙", Arrays.asList("有厉，利已。", "舆说輹。", "良马逐，利艰贞。日闲舆卫，利有攸往。", "童牛之牿，元吉。", "豶豕之牙，吉。", "何天之衢，亨。"));
            put("䷚", Arrays.asList("舍尔灵龟，观我朵颐，凶。", "颠颐，拂经于丘颐，征凶。", "拂颐，贞凶。十年勿用，无攸利。", "颠颐，吉。虎视眈眈，其欲逐逐，无咎。", "拂经，居贞吉，不可涉大川。", "由颐，厉吉。利涉大川。"));
            put("䷛", Arrays.asList("藉用白茅，无咎。", "枯杨生稊，老夫得其女妻，无不利。", "栋桡，凶。", "栋隆，吉，有它吝。", "枯杨生华，老妇得其士夫，无咎无誉。", "过涉灭顶，凶，无咎。"));
            put("䷜", Arrays.asList("习坎，入于坎窞，凶。", "坎有险，求小得。", "来之坎坎，险且枕。入于坎窞，勿用。", "樽酒，簋贰，用缶，纳约自牖，终无咎。", "坎不盈，祗既平，无咎。", "系用徽纆，置于丛棘，三岁不得，凶。"));
            put("䷝", Arrays.asList("履错，然，敬之，无咎。", "黄离，元吉。", "日昃之离，不鼓缶而歌，则大耋之嗟，凶。", "突如其来如，焚如，死如，弃如。", "出涕沱若，戚嗟若，吉。", "王用出征，用嘉折首，获匪其丑，无咎。"));
            put("䷞", Arrays.asList("咸其拇。", "咸其腓，凶。居吉。", "咸其股，执其随，往吝。", "贞吉。悔亡。憧憧往来，朋从尔思。", "咸其脢，无悔。", "咸其辅颊舌。"));
            put("䷟", Arrays.asList("浚恒，贞凶，无攸利。", "悔亡。", "不恒其德，或承之羞；贞吝。", "田无禽。", "恒其德，贞。妇人吉，夫子凶。", "振恒，凶。"));
            put("䷠", Arrays.asList("遁尾，厉，勿用有攸往。", "执之，用黄牛之革，莫之胜说。", "系遁，有疾厉。畜臣妾，吉。", "好遁，君子吉，小人否。", "嘉遁，贞吉。", "肥遁，无不利。"));
            put("䷡", Arrays.asList("壮于趾，征凶，有孚。", "贞吉。", "小人用壮，君子用罔，贞厉。羝羊触藩，羸其角。", "贞吉，悔亡。藩决不羸，壮于大舆之輹。", "丧羊于易，无悔。", "羝羊触藩，不能退，不能遂，无攸利。艰则吉。"));
            put("䷢", Arrays.asList("晋如，摧如，贞吉。罔孚，裕无咎。", "晋如愁如，贞吉。受兹介福，于其王母。", "众允，悔亡。", "晋如鼫鼠，贞厉。", "悔亡，失得勿恤。往吉，无不利。", "晋其角，维用伐邑，厉吉，无咎。贞吝。"));
            put("䷣", Arrays.asList("明夷于飞，垂其翼。 君子于行，三日不食， 有攸往，主人有言。", "明夷，夷于左股，用拯马壮，吉。", "明夷于南狩，得其大首。不可疾贞。", "入于左腹，获明夷之心，出于门庭。", "箕子之明夷，利贞。", "不明晦，初登于天，后入于地。"));
            put("䷤", Arrays.asList("闲有家，悔亡。", "无攸遂，在中馈，贞吉。", "家人嗃嗃，悔厉，吉。妇子嘻嘻，终吝。", "富家，大吉。", "王假有家，勿恤，吉。", "有孚，威如，终吉。"));
            put("䷥", Arrays.asList("悔亡；丧马勿逐，自复。见恶人，无咎。", "遇主于巷，无咎。", "见舆曳，其牛掣，其人天且劓。无初有终。", "睽孤，遇元夫，交孚，厉无咎。", "悔亡，厥宗噬肤，往何咎？", "睽孤，见豕负涂，载鬼一车。先张之弧，后说之弧。匪寇，婚媾，往遇雨则吉。"));
            put("䷦", Arrays.asList("往蹇，来誉。", "王臣蹇蹇，匪躬之故。", "往蹇，来反。", "往蹇，来连。", "大蹇，朋来。", "往蹇，来硕。吉，利见大人。"));
            put("䷧", Arrays.asList("无咎。", "田获三狐，得黄矢，贞吉。", "负且乘，致寇至，贞吝。", "解而拇，朋至斯孚。", "君子维有解，吉。有孚于小人。", "公用射隼于高墉之上，获之，无不利。"));
            put("䷨", Arrays.asList("已事遄往，无咎，酌损之。", "利贞，征凶。弗损，益之。", "三人行，则损一人。一人行，则得其友。", "损其疾，使遄有喜，无咎。", "或益之十朋之龟，弗克违，元吉。", "弗损益之，无咎，贞吉，利有攸往。得臣无家。"));
            put("䷩", Arrays.asList("利用为大作，元吉，无咎。", "或益之十朋之龟，弗克违，永贞吉。王用享于帝，吉。", "益之用凶事，无咎。有孚中行，告公用圭。", "中行，告公从，利用为依迁国。", "有孚惠心，勿问，元吉。有孚惠我德。", "莫益之，或击之，立心勿恒，凶。"));
            put("䷪", Arrays.asList("壮于前趾，往不胜，为咎。", "惕号，莫夜有戎，勿恤。", "壮于頄，有凶。君子夬夬，独行遇雨，若濡有愠，无咎。", "臀无肤，其行次且。牵羊悔亡，闻言不信。", "苋陆夬夬，中行无咎。", "无号，终有凶。"));
            put("䷫", Arrays.asList("系于金柅，贞吉。有攸往，见凶，羸豕孚蹢躅。", "包有鱼，无咎，不利宾。", "臀无肤，其行次且，厉，无大咎。", "包无鱼，起凶。", "以杞包瓜，含章，有陨自天。", "姤其角，吝，无咎。"));
            put("䷬", Arrays.asList("有孚不终，乃乱乃萃。若号，一握为笑，勿恤，往无咎。", "引吉，无咎。孚乃利用禴。", "萃如嗟如，无攸利。往无咎，小吝。", "大吉，无咎。", "萃有位，无咎。匪孚，元永贞，悔亡。", "赍咨涕洟，无咎。"));
            put("䷭", Arrays.asList("允升，大吉。", "孚乃利用禴，无咎。", "升虚邑。", "王用亨于岐山，吉，无咎。", "贞吉，升阶。", "冥升，利于不息之贞。"));
            put("䷮", Arrays.asList("臀困于株木，入于幽谷，三岁不觌。", "困于酒食，朱绂方来，利用享祀。征凶，无咎。", "困于石，据于蒺藜，入于其宫，不见其妻，凶", "来徐徐，困于金车，吝，有终。", "劓刖，困于赤绂；乃徐有说，利用祭祀。", "困于葛藟，于臲兀危，曰动悔。有悔，征吉。"));
            put("䷯", Arrays.asList("井泥不食，旧井无禽。", "井谷射鲋，瓮敝漏。", "井渫不食，为我心恻。可用汲，王明并受其福。", "井甃，无咎。", "井冽，寒泉食。", "井收，勿幕。有孚，元吉。"));
            put("䷰", Arrays.asList("巩用黄牛之革。", "巳日乃革之，征吉，无咎。", "征凶，贞厉。革言三就，有孚。", "悔亡，有孚改命，吉。", "大人虎变，未占有孚。", "君子豹变，小人革面，征凶，居贞吉。"));
            put("䷱", Arrays.asList("鼎颠趾，利出否。得妾以其子，无咎。", "鼎有实，我仇有疾，不我能即，吉。", "鼎耳革，其行塞，雉膏不食。方雨亏悔，终吉。", "鼎折足，覆公餗，其形渥，凶。", "鼎黄耳金铉，利贞。", "鼎玉铉，大吉，无不利。"));
            put("䷲", Arrays.asList("震来虩虩，后笑言哑哑，吉。", "震来厉，亿丧贝，跻于九陵，勿逐，七日得。", "震苏苏，震行无眚。", "震遂泥。", "震往来厉，意无丧有事。", "震索索，视矍矍，征凶。震不于其躬，于其邻，无咎。婚媾有言。"));
            put("䷳", Arrays.asList("艮其趾，无咎，利永贞。", "艮其腓，不拯其随，其心不快。", "艮其限，列其夤，厉熏心。", "艮其身，无咎。", "艮其辅，言有序，悔亡。", "敦艮，吉。"));
            put("䷴", Arrays.asList("鸿渐于干，小子厉，有言，无咎。", "鸿渐于磐，饮食衎衎，吉。", "鸿渐于陆，夫征不复，妇孕不育，凶。利御寇。", "鸿渐于木，或得其桷，无咎。", "鸿渐于陵，妇三岁不孕，终莫之胜，吉。", "鸿渐于陆，其羽可用为仪，吉。"));
            put("䷵", Arrays.asList("归妹以娣，跛能履，征吉。", "眇能视，利幽人之贞。", "归妹以须，反归以娣。", "归妹愆期，迟归有时。", "帝乙归妹，其君之袂，不如其娣之袂良。月几望，吉。", "女承筐无实，士刲羊无血，无攸利。"));
            put("䷶", Arrays.asList("遇其配主，虽旬无咎，往有尚。", "丰其蔀，日中见斗，往得疑疾。有孚发若，吉。", "丰其沛，日中见沬，折其右肱，无咎。", "丰其蔀，日中见斗，遇其夷主，吉。", "来章，有庆誉，吉。", "丰其屋，蔀其家，闚其户，阒其无人，三岁不觌，凶。"));
            put("䷷", Arrays.asList("旅琐琐，斯其所取灾。", "旅即次，怀其资，得童仆贞。", "旅焚其次，丧其童仆，贞厉。", "旅于处，得其资斧，我心不快。", "射雉，一矢亡，终以誉命。", "鸟焚其巢，旅人先笑后号啕。丧牛于易，凶。"));
            put("䷸", Arrays.asList("进退，利武人之贞。", "巽在床下，用史巫纷若，吉，无咎。", "频巽，吝。", "悔亡，田获三品。", "贞吉，悔亡，无不利。无初有终。先庚三日，后庚三日，吉。", "巽在床下，丧其资斧，贞凶。"));
            put("䷹", Arrays.asList("和兑，吉。", "孚兑，吉，悔亡。", "和兑，吉。", "商兑未宁，介疾有喜。", "孚于剥，有厉。", "引兑。"));
            put("䷺", Arrays.asList("用拯马壮，吉。", "涣奔其机，悔亡。", "涣其躬，无悔。", "涣其群，元吉。涣有丘，匪夷所思。", "涣汗其大号，涣王居，无咎。", "涣其血，去逖出，无咎。"));
            put("䷻", Arrays.asList("不出户庭，无咎。", "不出门庭，凶。", "不节若，则嗟若，无咎。", "安节，亨。", "甘节，吉。往有尚。", "苦节，贞凶，悔亡。"));
            put("䷼", Arrays.asList("虞吉，有它不燕。", "鹤鸣在阴，其子和之。我有好爵，吾与尔靡之。", "得敌，或鼓或罢，或泣或歌。", "月几望，马匹亡，无咎。", "有孚挛如，无咎。", "翰音登于天，贞凶。"));
            put("䷽", Arrays.asList("飞鸟以凶。", "过其祖，遇其妣，不及其君，遇其臣，无咎。", "弗过防之，从或戕之，凶。", "无咎，弗过遇之，往厉必戒，勿用永贞。", "密云不雨，自我西郊，公弋取彼在穴。", "弗遇过之，飞鸟离之，凶，是谓灾眚。"));
            put("䷾", Arrays.asList("曳其轮，濡其尾，无咎。", "妇丧其茀，勿逐，七日得。", "高宗伐鬼方，三年克之，小人勿用。", "繻有衣袽，终日戒。", "东邻杀牛，不如西郊之禴祭，实受其福。", "濡其首，厉。"));
            put("䷿", Arrays.asList("濡其尾，吝。", "曳其轮，贞吉。", "未济，征凶，利涉大川。", "吉，悔亡，震用伐鬼方，三年有赏于大国。", "贞吉，无悔，君子之光，有孚吉。", "有孚于饮酒，无咎。濡其首，有孚失是。"));
        }
    };

    /**
     * 本卦 变 变卦（索引为键）
     */
    public static final Map<Integer, List<Integer>> BIAN_GUA = new HashMap<Integer, List<Integer>>() {
        private static final long serialVersionUID = -1;

        {
            put(1, Arrays.asList(5, 3, 2)); // 乾卦（☰），动爻数为：1或4时变为巽[☴]，2或5时变为离[☲]，3或6时变为兑[☱]
            put(2, Arrays.asList(6, 4, 1)); // 兑卦（☱），动爻数为：1或4时变为坎[☵]，2或5时变为震[☳]，3或6时变为乾[☰]
            put(3, Arrays.asList(7, 1, 4)); // 离卦（☲），动爻数为：1或4时变为艮[☶]，2或5时变为乾[☰]，3或6时变为震[☳]
            put(4, Arrays.asList(8, 2, 3)); // 震卦（☳），动爻数为：1或4时变为坤[☷]，2或5时变为兑[☱]，3或6时变为离[☲]
            put(5, Arrays.asList(1, 7, 6)); // 巽卦（☴），动爻数为：1或4时变为乾[☰]，2或5时变为艮[☶]，3或6时变为坎[☵]
            put(6, Arrays.asList(2, 8, 5)); // 坎卦（☵），动爻数为：1或4时变为兑[☱]，2或5时变为坤[☷]，3或6时变为巽[☴]
            put(7, Arrays.asList(3, 5, 8)); // 艮卦（☶），动爻数为：1或4时变为离[☲]，2或5时变为巽[☴]，3或6时变为坤[☷]
            put(8, Arrays.asList(4, 6, 7)); // 坤卦（☷），动爻数为：1或4时变为震[☳]，2或5时变为坎[☵]，3或6时变为艮[☶]

        }
    };

    /**
     * 本卦 变 互卦、错卦、综卦、伏卦（本卦卦象为键）
     * <p></p>
     * <p> 1、互卦：本卦的二三四爻做为下卦、本卦的三四五爻做为上卦 </p>
     * <p> 2、错卦：本卦阳爻变阴爻，阴爻变阳爻</p>
     * <p> 3、综卦：本卦上下180°旋转</p>
     * <p> 4、伏卦：本卦对应的八纯卦</p>
     */
    public static final Map<String, List<String>> HU_CUO_ZONG_FU = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            // 例如→ 本卦为䷀（乾为天）。变化后→ 互卦为䷀（乾为天），错卦为䷁（坤为地），综卦为䷀（乾为天），伏卦为䷀（乾为天）

            //  本卦               互卦  错卦  综卦  伏卦
            put("䷀", Arrays.asList("䷀", "䷁", "䷀", "䷀")); // 1、本卦为䷀（乾为天）。   变化后→ 互卦为䷀（乾为天），错卦为䷁（坤为地），综卦为䷀（乾为天），伏卦为䷀（乾为天）
            put("䷁", Arrays.asList("䷁", "䷀", "䷁", "䷁")); // 2、本卦为䷁（坤为地）。   变化后→ 互卦为䷁（坤为地），错卦为䷀（乾为天），综卦为䷁（坤为地），伏卦为䷁（坤为地）
            put("䷂", Arrays.asList("䷖", "䷱", "䷃", "䷜")); // 3、本卦为䷂（水雷屯）。   变化后→ 互卦为䷖（山地剥），错卦为䷱（火风鼎），综卦为䷃（山水蒙），伏卦为䷜（坎为水）
            put("䷃", Arrays.asList("䷗", "䷰", "䷂", "䷝")); // 4、本卦为䷃（山水蒙）。   变化后→ 互卦为䷗（地雷复），错卦为䷰（泽火革），综卦为䷂（水雷屯），伏卦为䷝（离为火）
            put("䷄", Arrays.asList("䷥", "䷢", "䷅", "䷁")); // 5、本卦为䷄（水天需）。   变化后→ 互卦为䷥（火泽睽），错卦为䷢（火地晋），综卦为䷅（天水讼），伏卦为䷁（坤为地）
            put("䷅", Arrays.asList("䷤", "䷣", "䷄", "䷝")); // 6、本卦为䷅（天水讼）。   变化后→ 互卦为䷤（风火家人），错卦为䷣（地火明夷），综卦为䷄（水天需），伏卦为䷝（离为火）
            put("䷆", Arrays.asList("䷗", "䷌", "䷇", "䷜")); // 7、本卦为䷆（地水师）。   变化后→ 互卦为䷗（地雷复），错卦为䷌（天火同人），综卦为䷇（水地比），伏卦为䷜（坎为水）
            put("䷇", Arrays.asList("䷖", "䷍", "䷆", "䷁")); // 8、本卦为䷇（水地比）。   变化后→ 互卦为䷖（山地剥），错卦为䷍（火天大有），综卦为䷆（地水师），伏卦为䷁（坤为地）
            put("䷈", Arrays.asList("䷥", "䷏", "䷉", "䷸")); // 9、本卦为䷈（风天小畜)。  变化后→ 互卦为䷥（火泽睽），错卦为䷏（雷地豫），综卦为䷉（天泽履），伏卦为䷸（巽为风）
            put("䷉", Arrays.asList("䷤", "䷎", "䷈", "䷳")); // 10、本卦为䷉（天泽履）。  变化后→ 互卦为䷤（风火家人），错卦为䷎（地山谦），综卦为䷈（风天小畜），伏卦为䷳（艮为山）
            put("䷊", Arrays.asList("䷵", "䷋", "䷋", "䷁")); // 11、本卦为䷊（地天泰）。  变化后→ 互卦为䷵（雷泽归妹），错卦为䷋（天地否），综卦为䷋（天地否），伏卦为䷁（坤为地）
            put("䷋", Arrays.asList("䷴", "䷊", "䷊", "䷀")); // 12、本卦为䷋（天地否）。  变化后→ 互卦为䷴（风山渐），错卦为䷊（地天泰），综卦为䷊（地天泰），伏卦为䷀（乾为天）
            put("䷌", Arrays.asList("䷫", "䷆", "䷍", "䷝")); // 13、本卦为䷌（天火同人）。变化后→ 互卦为䷫（天风姤），错卦为䷆（地水师），综卦为䷍（火天大有），伏卦为䷝（离为火）
            put("䷍", Arrays.asList("䷪", "䷇", "䷌", "䷀")); // 14、本卦为䷍（火天大有）。变化后→ 互卦为䷪（泽天夬），错卦为䷇（水地比），综卦为䷌（天火同人），伏卦为䷀（乾为天）
            put("䷎", Arrays.asList("䷧", "䷉", "䷏", "䷹")); // 15、本卦为䷎（地山谦）。  变化后→ 互卦为䷧（雷水解），错卦为䷉（天泽履），综卦为䷏（雷地豫），伏卦为䷹（兑为泽）
            put("䷏", Arrays.asList("䷦", "䷈", "䷎", "䷲")); // 16、本卦为䷏（雷地豫）。  变化后→ 互卦为䷦（水山蹇），错卦为䷈（风天小畜），综卦为䷎（地山谦），伏卦为䷲（震为雷）
            put("䷐", Arrays.asList("䷴", "䷑", "䷑", "䷲")); // 17、本卦为䷐（泽雷随）。  变化后→ 互卦为䷴（风山渐），错卦为䷑（山风蛊），综卦为䷑（山风蛊），伏卦为䷲（震为雷）
            put("䷑", Arrays.asList("䷵", "䷐", "䷐", "䷸")); // 18、本卦为䷑（山风蛊）。  变化后→ 互卦为䷵（雷泽归妹），错卦为䷐（泽雷随），综卦为䷐（泽雷随），伏卦为䷸（巽为风）
            put("䷒", Arrays.asList("䷗", "䷠", "䷓", "䷁")); // 19、本卦为䷒（地泽临）。  变化后→ 互卦为䷗（地雷复），错卦为䷠（天山遁），综卦为䷓（风地观），伏卦为䷁（坤为地）
            put("䷓", Arrays.asList("䷖", "䷡", "䷒", "䷀")); // 20、本卦为䷓（风地观）。  变化后→ 互卦为䷖（山地剥），错卦为䷡（雷天大壮），综卦为䷒（地泽临），伏卦为䷀（乾为天）
            put("䷔", Arrays.asList("䷦", "䷯", "䷕", "䷸")); // 21、本卦为䷔（火雷噬嗑）。变化后→ 互卦为䷦（水山蹇），错卦为䷯（水风井），综卦为䷕（山火贲），伏卦为䷸（巽为风）
            put("䷕", Arrays.asList("䷧", "䷮", "䷔", "䷳")); // 22、本卦为䷕（山火贲）。  变化后→ 互卦为䷧（雷水解），错卦为䷮（泽水困），综卦为䷔（火雷噬嗑），伏卦为䷳（艮为山）
            put("䷖", Arrays.asList("䷁", "䷪", "䷗", "䷀")); // 23、本卦为䷖（山地剥）。  变化后→ 互卦为䷁（坤为地），错卦为䷪（泽天夬），综卦为䷗（地雷复），伏卦为䷀（乾为天）
            put("䷗", Arrays.asList("䷁", "䷫", "䷖", "䷁")); // 24、本卦为䷗（地雷复）。  变化后→ 互卦为䷁（坤为地），错卦为䷫（天风姤），综卦为䷖（山地剥），伏卦为䷁（坤为地）
            put("䷘", Arrays.asList("䷴", "䷭", "䷙", "䷸")); // 25、本卦为䷘（天雷无妄）。变化后→ 互卦为䷴（风山渐），错卦为䷭（地风升），综卦为䷙（山天大畜），伏卦为䷸（巽为风）
            put("䷙", Arrays.asList("䷵", "䷬", "䷘", "䷳")); // 26、本卦为䷙（山天大畜）。变化后→ 互卦为䷵（雷泽归妹），错卦为䷬（泽地萃），综卦为䷘（天雷无妄），伏卦为䷳（艮为山）
            put("䷚", Arrays.asList("䷁", "䷛", "䷚", "䷸")); // 27、本卦为䷚（山雷颐）。  变化后→ 互卦为䷁（坤为地），错卦为䷛（泽风大过），综卦为䷚（山雷颐），伏卦为䷸（巽为风）
            put("䷛", Arrays.asList("䷀", "䷚", "䷛", "䷲")); // 28、本卦为䷛（泽风大过）。变化后→ 互卦为䷀（乾为天），错卦为䷚（山雷颐），综卦为䷛（泽风大过），伏卦为䷲（震为雷）
            put("䷜", Arrays.asList("䷚", "䷝", "䷜", "䷜")); // 29、本卦为䷜（坎为水）。  变化后→ 互卦为䷚（山雷颐），错卦为䷝（离为火），综卦为䷜（坎为水），伏卦为䷜（坎为水）
            put("䷝", Arrays.asList("䷛", "䷜", "䷝", "䷝")); // 30、本卦为䷝（离为火）。  变化后→ 互卦为䷛（泽风大过），错卦为䷜（坎为水），综卦为䷝（离为火），伏卦为䷝（离为火）
            put("䷞", Arrays.asList("䷫", "䷨", "䷟", "䷹")); // 31、本卦为䷞（泽山咸）。  变化后→ 互卦为䷫（天风姤），错卦为䷨（山泽损），综卦为䷟（雷风恒），伏卦为䷹（兑为泽）
            put("䷟", Arrays.asList("䷪", "䷩", "䷞", "䷲")); // 32、本卦为䷟（雷风恒）。  变化后→ 互卦为䷪（泽天夬），错卦为䷩（风雷益），综卦为䷞（泽山咸），伏卦为䷲（震为雷）
            put("䷠", Arrays.asList("䷫", "䷒", "䷡", "䷀")); // 33、本卦为䷠（天山遁）。  变化后→ 互卦为䷫（天风姤），错卦为䷒（地泽临），综卦为䷡（雷天大壮），伏卦为䷀（乾为天）
            put("䷡", Arrays.asList("䷪", "䷓", "䷠", "䷁")); // 34、本卦为䷡（雷天大壮）。变化后→ 互卦为䷪（泽天夬），错卦为䷓（风地观），综卦为䷠（天山遁），伏卦为䷁（坤为地）
            put("䷢", Arrays.asList("䷦", "䷄", "䷣", "䷀")); // 35、本卦为䷢（火地晋）。  变化后→ 互卦为䷦（水山蹇），错卦为䷄（水天需），综卦为䷣（地火明夷），伏卦为䷀（乾为天）
            put("䷣", Arrays.asList("䷧", "䷅", "䷢", "䷜")); // 36、本卦为䷣（地火明夷）。变化后→ 互卦为䷧（雷水解），错卦为䷅（天水讼），综卦为䷢（火地晋），伏卦为䷜（坎为水）
            put("䷤", Arrays.asList("䷿", "䷧", "䷥", "䷸")); // 37、本卦为䷤（风火家人）。变化后→ 互卦为䷿（火水未济），错卦为䷧（雷水解），综卦为䷥（火泽睽），伏卦为䷸（巽为风）
            put("䷥", Arrays.asList("䷾", "䷦", "䷤", "䷁")); // 38、本卦为䷥（火泽睽）。  变化后→ 互卦为䷾（水火既济），错卦为䷦（水山蹇），综卦为䷤（风火家人），伏卦为䷁（坤为地）
            put("䷦", Arrays.asList("䷿", "䷥", "䷧", "䷹")); // 39、本卦为䷦（水山蹇）。  变化后→ 互卦为䷿（火水未济），错卦为䷥（火泽睽），综卦为䷧（雷水解），伏卦为䷹（兑为泽）
            put("䷧", Arrays.asList("䷾", "䷤", "䷦", "䷲")); // 40、本卦为䷧（雷水解）。  变化后→ 互卦为䷾（水火既济），错卦为䷤（风火家人），综卦为䷦（水山蹇），伏卦为䷲（震为雷）
            put("䷨", Arrays.asList("䷗", "䷞", "䷩", "䷳")); // 41、本卦为䷨（山泽损）。  变化后→ 互卦为䷗（地雷复），错卦为䷞（泽山咸），综卦为䷩（风雷益），伏卦为䷳（艮为山）
            put("䷩", Arrays.asList("䷖", "䷟", "䷨", "䷸")); // 42、本卦为䷩（风雷益）。  变化后→ 互卦为䷖（山地剥），错卦为䷟（雷风恒），综卦为䷨（山泽损），伏卦为䷸（巽为风）
            put("䷪", Arrays.asList("䷀", "䷖", "䷫", "䷁")); // 43、本卦为䷪（泽天夬）。  变化后→ 互卦为䷀（乾为天），错卦为䷖（山地剥），综卦为䷫（天风姤），伏卦为䷁（坤为地）
            put("䷫", Arrays.asList("䷀", "䷗", "䷪", "䷀")); // 44、本卦为䷫（天风姤）。  变化后→ 互卦为䷀（乾为天），错卦为䷗（地雷复），综卦为䷪（泽天夬），伏卦为䷀（乾为天）
            put("䷬", Arrays.asList("䷴", "䷙", "䷭", "䷹")); // 45、本卦为䷬（泽地萃）。  变化后→ 互卦为䷴（风山渐），错卦为䷙（山天大畜），综卦为䷭（地风升），伏卦为䷹（兑为泽）
            put("䷭", Arrays.asList("䷵", "䷘", "䷬", "䷲")); // 46、本卦为䷭（地风升）。  变化后→ 互卦为䷵（雷泽归妹），错卦为䷘（天雷无妄），综卦为䷬（泽地萃），伏卦为䷲（震为雷）
            put("䷮", Arrays.asList("䷤", "䷕", "䷯", "䷹")); // 47、本卦为䷮（泽水困）。  变化后→ 互卦为䷤（风火家人），错卦为䷕（山火贲），综卦为䷯（水风井），伏卦为䷹（兑为泽）
            put("䷯", Arrays.asList("䷥", "䷔", "䷮", "䷲")); // 48、本卦为䷯（水风井）。  变化后→ 互卦为䷥（火泽睽），错卦为䷔（火雷噬嗑），综卦为䷮（泽水困），伏卦为䷲（震为雷）
            put("䷰", Arrays.asList("䷫", "䷃", "䷱", "䷜")); // 49、本卦为䷰（泽火革）。  变化后→ 互卦为䷫（天风姤），错卦为䷃（山水蒙），综卦为䷱（火风鼎），伏卦为䷜（坎为水）
            put("䷱", Arrays.asList("䷪", "䷂", "䷰", "䷝")); // 50、本卦为䷱（火风鼎）。  变化后→ 互卦为䷪（泽天夬），错卦为䷂（水雷屯），综卦为䷰（泽火革），伏卦为䷝（离为火）
            put("䷲", Arrays.asList("䷦", "䷸", "䷳", "䷲")); // 51、本卦为䷲（震为雷）。  变化后→ 互卦为䷦（水山蹇），错卦为䷸（巽为风），综卦为䷳（艮为山），伏卦为䷲（震为雷）
            put("䷳", Arrays.asList("䷧", "䷹", "䷲", "䷳")); // 52、本卦为䷳（艮为山）。  变化后→ 互卦为䷧（雷水解），错卦为䷹（兑为泽），综卦为䷲（震为雷），伏卦为䷳（艮为山）
            put("䷴", Arrays.asList("䷿", "䷵", "䷵", "䷳")); // 53、本卦为䷴（风山渐）。  变化后→ 互卦为䷿（火水未济），错卦为䷵（雷泽归妹），综卦为䷵（雷泽归妹），伏卦为䷳（艮为山）
            put("䷵", Arrays.asList("䷾", "䷴", "䷴", "䷹")); // 54、本卦为䷵（雷泽归妹）。变化后→ 互卦为䷾（水火既济），错卦为䷴（风山渐），综卦为䷴（风山渐），伏卦为䷹（兑为泽）
            put("䷶", Arrays.asList("䷛", "䷺", "䷷", "䷜")); // 55、本卦为䷶（雷火丰）。  变化后→ 互卦为䷛（泽风大过），错卦为䷺（风水涣），综卦为䷷（火山旅），伏卦为䷜（坎为水）
            put("䷷", Arrays.asList("䷛", "䷻", "䷶", "䷝")); // 56、本卦为䷷（火山旅）。  变化后→ 互卦为䷛（泽风大过），错卦为䷻（水泽节），综卦为䷶（雷火丰），伏卦为䷝（离为火）
            put("䷸", Arrays.asList("䷥", "䷲", "䷹", "䷸")); // 57、本卦为䷸（巽为风）。  变化后→ 互卦为䷥（火泽睽），错卦为䷲（震为雷），综卦为䷹（兑为泽），伏卦为䷸（巽为风）
            put("䷹", Arrays.asList("䷤", "䷳", "䷸", "䷹")); // 58、本卦为䷹（兑为泽）。  变化后→ 互卦为䷤（风火家人），错卦为䷳（艮为山），综卦为䷸（巽为风），伏卦为䷹（兑为泽）
            put("䷺", Arrays.asList("䷚", "䷶", "䷻", "䷝")); // 59、本卦为䷺（风水涣）。  变化后→ 互卦为䷚（山雷颐），错卦为䷶（雷火丰），综卦为䷻（水泽节），伏卦为䷝（离为火）
            put("䷻", Arrays.asList("䷚", "䷷", "䷺", "䷜")); // 60、本卦为䷻（水泽节）。  变化后→ 互卦为䷚（山雷颐），错卦为䷷（火山旅），综卦为䷺（风水涣），伏卦为䷜（坎为水）
            put("䷼", Arrays.asList("䷚", "䷽", "䷽", "䷳")); // 61、本卦为䷼（风泽中孚）。变化后→ 互卦为䷚（山雷颐），错卦为䷽（雷山小过），综卦为䷽（雷山小过），伏卦为䷳（艮为山）
            put("䷽", Arrays.asList("䷛", "䷼", "䷼", "䷹")); // 62、本卦为䷽（雷山小过）。变化后→ 互卦为䷛（泽风大过），错卦为䷼（风泽中孚），综卦为䷼（风泽中孚），伏卦为䷹（兑为泽）
            put("䷾", Arrays.asList("䷿", "䷿", "䷿", "䷜")); // 63、本卦为䷾（水火既济）。变化后→ 互卦为䷿（火水未济），错卦为䷿（火水未济），综卦为䷿（火水未济），伏卦为䷜（坎为水）
            put("䷿", Arrays.asList("䷾", "䷾", "䷾", "䷝")); // 64、本卦为䷿（火水未济）。变化后→ 互卦为䷾（水火既济），错卦为䷾（水火既济），综卦为䷾（水火既济），伏卦为䷝（离为火）

        }
    };

    /**
     * 用卦与体卦的关系（用卦+体卦为键）
     */
    public static final Map<String, String> YONG_TI_GUAN_XI = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("乾乾", YONG_TI_BI_HE); // 用卦为乾、体卦为乾
            put("乾坤", TI_SHENG_YONG); // 用卦为乾、体卦为坤
            put("乾震", YONG_KE_TI);    // 用卦为乾、体卦为震
            put("乾巽", YONG_KE_TI);    // 用卦为乾、体卦为巽
            put("乾坎", YONG_SHENG_TI); // 用卦为乾、体卦为坎
            put("乾离", TI_KE_YONG);    // 用卦为乾、体卦为离
            put("乾艮", TI_SHENG_YONG); // 用卦为乾、体卦为艮
            put("乾兑", YONG_TI_BI_HE); // 用卦为乾、体卦为兑
            put("兑乾", YONG_TI_BI_HE); // 用卦为兑、体卦为乾
            put("兑坤", TI_SHENG_YONG); // 用卦为兑、体卦为坤
            put("兑震", YONG_KE_TI);    // 用卦为兑、体卦为震
            put("兑巽", YONG_KE_TI);    // 用卦为兑、体卦为巽
            put("兑坎", YONG_SHENG_TI); // 用卦为兑、体卦为坎
            put("兑离", TI_KE_YONG);    // 用卦为兑、体卦为离
            put("兑艮", TI_SHENG_YONG); // 用卦为兑、体卦为艮
            put("兑兑", YONG_TI_BI_HE); // 用卦为兑、体卦为兑
            put("离乾", YONG_KE_TI);    // 用卦为离、体卦为乾
            put("离坤", YONG_SHENG_TI); // 用卦为离、体卦为坤
            put("离震", TI_SHENG_YONG); // 用卦为离、体卦为震
            put("离巽", TI_SHENG_YONG); // 用卦为离、体卦为巽
            put("离坎", TI_KE_YONG);    // 用卦为离、体卦为坎
            put("离离", YONG_TI_BI_HE); // 用卦为离、体卦为离
            put("离艮", YONG_SHENG_TI); // 用卦为离、体卦为艮
            put("离兑", YONG_KE_TI);    // 用卦为离、体卦为兑
            put("震乾", TI_KE_YONG);    // 用卦为震、体卦为乾
            put("震坤", YONG_KE_TI);    // 用卦为震、体卦为坤
            put("震震", YONG_TI_BI_HE); // 用卦为震、体卦为震
            put("震巽", YONG_TI_BI_HE); // 用卦为震、体卦为巽
            put("震坎", TI_SHENG_YONG); // 用卦为震、体卦为坎
            put("震离", YONG_SHENG_TI); // 用卦为震、体卦为离
            put("震艮", YONG_KE_TI);    // 用卦为震、体卦为艮
            put("震兑", TI_KE_YONG);    // 用卦为震、体卦为兑
            put("巽乾", TI_KE_YONG);    // 用卦为巽、体卦为乾
            put("巽坤", YONG_KE_TI);    // 用卦为巽、体卦为坤
            put("巽震", YONG_TI_BI_HE); // 用卦为巽、体卦为震
            put("巽巽", YONG_TI_BI_HE); // 用卦为巽、体卦为巽
            put("巽坎", TI_SHENG_YONG); // 用卦为巽、体卦为坎
            put("巽离", YONG_SHENG_TI); // 用卦为巽、体卦为离
            put("巽艮", YONG_KE_TI);    // 用卦为巽、体卦为艮
            put("巽兑", TI_KE_YONG);    // 用卦为巽、体卦为兑
            put("坎乾", TI_SHENG_YONG); // 用卦为坎、体卦为乾
            put("坎坤", TI_KE_YONG);    // 用卦为坎、体卦为坤
            put("坎震", YONG_SHENG_TI); // 用卦为坎、体卦为震
            put("坎巽", YONG_SHENG_TI); // 用卦为坎、体卦为巽
            put("坎坎", YONG_TI_BI_HE); // 用卦为坎、体卦为坎
            put("坎离", YONG_KE_TI);    // 用卦为坎、体卦为离
            put("坎艮", TI_KE_YONG);    // 用卦为坎、体卦为艮
            put("坎兑", TI_SHENG_YONG); // 用卦为坎、体卦为兑
            put("艮乾", YONG_SHENG_TI); // 用卦为艮、体卦为乾
            put("艮坤", YONG_TI_BI_HE); // 用卦为艮、体卦为坤
            put("艮震", TI_KE_YONG);    // 用卦为艮、体卦为震
            put("艮巽", TI_KE_YONG);    // 用卦为艮、体卦为巽
            put("艮坎", YONG_KE_TI);    // 用卦为艮、体卦为坎
            put("艮离", TI_SHENG_YONG); // 用卦为艮、体卦为离
            put("艮艮", YONG_TI_BI_HE); // 用卦为艮、体卦为艮
            put("艮兑", YONG_SHENG_TI); // 用卦为艮、体卦为兑
            put("坤乾", YONG_SHENG_TI); // 用卦为坤、体卦为乾
            put("坤坤", YONG_TI_BI_HE); // 用卦为坤、体卦为坤
            put("坤震", TI_KE_YONG);    // 用卦为坤、体卦为震
            put("坤巽", TI_KE_YONG);    // 用卦为坤、体卦为巽
            put("坤坎", YONG_KE_TI);    // 用卦为坤、体卦为坎
            put("坤离", TI_SHENG_YONG); // 用卦为坤、体卦为离
            put("坤艮", YONG_TI_BI_HE); // 用卦为坤、体卦为艮
            put("坤兑", YONG_SHENG_TI); // 用卦为坤、体卦为兑
        }
    };

//----------------------------------------------------------------------------------------------------------------------------------------------------

    /* 用卦与体卦的关系 */

    /**
     * 用卦生体卦
     */
    public static final String YONG_SHENG_TI = "用卦一般代表这件事情，体卦一般代表自身，用卦生体卦，大吉，这件事情极有可能成功（成功率在90%左右）。";
    /**
     * 用卦与体卦比和
     */
    public static final String YONG_TI_BI_HE = "用卦一般代表这件事情，体卦一般代表自身，用卦与体卦比和，次吉，这件事情很容易成功（成功率在70%左右）。";
    /**
     * 体卦克用卦
     */
    public static final String TI_KE_YONG = "用卦一般代表这件事情，体卦一般代表自身，体卦克用卦，中平，这件事情再努力一下就可能会成功（成功率在40%~60%左右）。";
    /**
     * 体卦生用卦
     */
    public static final String TI_SHENG_YONG = "用卦一般代表这件事情，体卦一般代表自身，体卦生用卦，小凶，这件事情成功的可能性比较小（成功率在30%左右）。";
    /**
     * 用卦克体卦
     */
    public static final String YONG_KE_TI = "用卦一般代表这件事情，体卦一般代表自身，用卦克体卦，大凶，这件事情极有可能不成功（成功率仅在10%左右）。";


}
