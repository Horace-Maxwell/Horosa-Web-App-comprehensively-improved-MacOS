package xuan.core.daliuren.maps;

import java.util.Map;
import java.util.List;
import java.util.Arrays;
import java.util.HashMap;

/**
 * 大六壬 - 基础常量
 *
 * @author 善待
 */
public class DaLiuRenJiChuMap {

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
     * 天干阴阳（天干为键）
     */
    public static final Map<String, String> TIAN_GAN_YIN_YANG = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲", "阳");
            put("乙", "阴");
            put("丙", "阳");
            put("丁", "阴");
            put("戊", "阳");
            put("己", "阴");
            put("庚", "阳");
            put("辛", "阴");
            put("壬", "阳");
            put("癸", "阴");
        }
    };

    /**
     * 地支阴阳（地支为键）
     */
    public static final Map<String, String> DI_ZHI_YIN_YANG = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子", "阳");
            put("丑", "阴");
            put("寅", "阳");
            put("卯", "阴");
            put("辰", "阳");
            put("巳", "阴");
            put("午", "阳");
            put("未", "阴");
            put("申", "阳");
            put("酉", "阴");
            put("戌", "阳");
            put("亥", "阴");
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
     * 五行旺衰（月支为键）
     */
    public static final Map<String, List<String>> WU_XING_WANG_SHUAI = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("子", Arrays.asList("水旺", "木相", "金休", "土囚", "火死"));
            put("丑", Arrays.asList("土旺", "金相", "火休", "木囚", "水死"));
            put("寅", Arrays.asList("木旺", "火相", "水休", "金囚", "土死"));
            put("卯", Arrays.asList("木旺", "火相", "水休", "金囚", "土死"));
            put("辰", Arrays.asList("土旺", "金相", "火休", "木囚", "水死"));
            put("巳", Arrays.asList("火旺", "土相", "木休", "水囚", "金死"));
            put("午", Arrays.asList("火旺", "土相", "木休", "水囚", "金死"));
            put("未", Arrays.asList("土旺", "金相", "火休", "木囚", "水死"));
            put("申", Arrays.asList("金旺", "水相", "土休", "火囚", "木死"));
            put("酉", Arrays.asList("金旺", "水相", "土休", "火囚", "木死"));
            put("戌", Arrays.asList("土旺", "金相", "火休", "木囚", "水死"));
            put("亥", Arrays.asList("水旺", "木相", "金休", "土囚", "火死"));
        }
    };

    /**
     * 十二宫地支（左下角为第一宫，依次顺时针旋转）
     */
    public static final List<String> SHI_ER_GONG_DI_ZHI = Arrays.asList("寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑");

    /**
     * 地支顺排（地支为键）
     */
    public static final Map<String, List<String>> DI_ZHI_SHUN_PAI = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("子", Arrays.asList("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"));
            put("丑", Arrays.asList("丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子"));
            put("寅", Arrays.asList("寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"));
            put("卯", Arrays.asList("卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅"));
            put("辰", Arrays.asList("辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯"));
            put("巳", Arrays.asList("巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰"));
            put("午", Arrays.asList("午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳"));
            put("未", Arrays.asList("未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午"));
            put("申", Arrays.asList("申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"));
            put("酉", Arrays.asList("酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申"));
            put("戌", Arrays.asList("戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉"));
            put("亥", Arrays.asList("亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌"));
        }
    };

    /**
     * 天地盘类型（月将+时支为键）
     */
    public static final Map<String, String> TIAN_DI_PAN_TYPE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子子", "伏吟盘");
            put("子丑", "退连茹盘");
            put("子寅", "退间传盘");
            put("子卯", "病元胎盘");
            put("子辰", "逆三合盘");
            put("子巳", "四正临绝盘");
            put("子午", "返吟盘");
            put("子未", "四墓覆生盘");
            put("子申", "顺三合盘");
            put("子酉", "生元胎盘");
            put("子戌", "进间传盘");
            put("子亥", "进连茹盘");

            put("丑子", "进连茹盘");
            put("丑丑", "伏吟盘");
            put("丑寅", "退连茹盘");
            put("丑卯", "退间传盘");
            put("丑辰", "病元胎盘");
            put("丑巳", "逆三合盘");
            put("丑午", "四正临绝盘");
            put("丑未", "返吟盘");
            put("丑申", "四墓覆生盘");
            put("丑酉", "顺三合盘");
            put("丑戌", "生元胎盘");
            put("丑亥", "进间传盘");

            put("寅子", "进间传盘");
            put("寅丑", "进连茹盘");
            put("寅寅", "伏吟盘");
            put("寅卯", "退连茹盘");
            put("寅辰", "退间传盘");
            put("寅巳", "病元胎盘");
            put("寅午", "逆三合盘");
            put("寅未", "四正临绝盘");
            put("寅申", "返吟盘");
            put("寅酉", "四墓覆生盘");
            put("寅戌", "顺三合盘");
            put("寅亥", "生元胎盘");

            put("卯子", "生元胎盘");
            put("卯丑", "进间传盘");
            put("卯寅", "进连茹盘");
            put("卯卯", "伏吟盘");
            put("卯辰", "退连茹盘");
            put("卯巳", "退间传盘");
            put("卯午", "病元胎盘");
            put("卯未", "逆三合盘");
            put("卯申", "四正临绝盘");
            put("卯酉", "返吟盘");
            put("卯戌", "四墓覆生盘");
            put("卯亥", "顺三合盘");

            put("辰子", "顺三合盘");
            put("辰丑", "生元胎盘");
            put("辰寅", "进间传盘");
            put("辰卯", "进连茹盘");
            put("辰辰", "伏吟盘");
            put("辰巳", "退连茹盘");
            put("辰午", "退间传盘");
            put("辰未", "病元胎盘");
            put("辰申", "逆三合盘");
            put("辰酉", "四正临绝盘");
            put("辰戌", "返吟盘");
            put("辰亥", "四墓覆生盘");

            put("巳子", "四墓覆生盘");
            put("巳丑", "顺三合盘");
            put("巳寅", "生元胎盘");
            put("巳卯", "进间传盘");
            put("巳辰", "进连茹盘");
            put("巳巳", "伏吟盘");
            put("巳午", "退连茹盘");
            put("巳未", "退间传盘");
            put("巳申", "病元胎盘");
            put("巳酉", "逆三合盘");
            put("巳戌", "四正临绝盘");
            put("巳亥", "返吟盘");

            put("午子", "返吟盘");
            put("午丑", "四墓覆生盘");
            put("午寅", "顺三合盘");
            put("午卯", "生元胎盘");
            put("午辰", "进间传盘");
            put("午巳", "进连茹盘");
            put("午午", "伏吟盘");
            put("午未", "退连茹盘");
            put("午申", "退间传盘");
            put("午酉", "病元胎盘");
            put("午戌", "逆三合盘");
            put("午亥", "四正临绝盘");

            put("未子", "四正临绝盘");
            put("未丑", "返吟盘");
            put("未寅", "四墓覆生盘");
            put("未卯", "顺三合盘");
            put("未辰", "生元胎盘");
            put("未巳", "进间传盘");
            put("未午", "进连茹盘");
            put("未未", "伏吟盘");
            put("未申", "退连茹盘");
            put("未酉", "退间传盘");
            put("未戌", "病元胎盘");
            put("未亥", "逆三合盘");

            put("申子", "逆三合盘");
            put("申丑", "四正临绝盘");
            put("申寅", "返吟盘");
            put("申卯", "四墓覆生盘");
            put("申辰", "顺三合盘");
            put("申巳", "生元胎盘");
            put("申午", "进间传盘");
            put("申未", "进连茹盘");
            put("申申", "伏吟盘");
            put("申酉", "退连茹盘");
            put("申戌", "退间传盘");
            put("申亥", "病元胎盘");

            put("酉子", "病元胎盘");
            put("酉丑", "逆三合盘");
            put("酉寅", "四正临绝盘");
            put("酉卯", "返吟盘");
            put("酉辰", "四墓覆生盘");
            put("酉巳", "顺三合盘");
            put("酉午", "生元胎盘");
            put("酉未", "进间传盘");
            put("酉申", "进连茹盘");
            put("酉酉", "伏吟盘");
            put("酉戌", "退连茹盘");
            put("酉亥", "退间传盘");

            put("戌子", "退间传盘");
            put("戌丑", "病元胎盘");
            put("戌寅", "逆三合盘");
            put("戌卯", "四正临绝盘");
            put("戌辰", "返吟盘");
            put("戌巳", "四墓覆生盘");
            put("戌午", "顺三合盘");
            put("戌未", "生元胎盘");
            put("戌申", "进间传盘");
            put("戌酉", "进连茹盘");
            put("戌戌", "伏吟盘");
            put("戌亥", "退连茹盘");

            put("亥子", "退连茹盘");
            put("亥丑", "退间传盘");
            put("亥寅", "病元胎盘");
            put("亥卯", "逆三合盘");
            put("亥辰", "四正临绝盘");
            put("亥巳", "返吟盘");
            put("亥午", "四墓覆生盘");
            put("亥未", "顺三合盘");
            put("亥申", "生元胎盘");
            put("亥酉", "进间传盘");
            put("亥戌", "进连茹盘");
            put("亥亥", "伏吟盘");
        }
    };

    /**
     * 十干寄宫（天干为键）
     */
    public static final Map<String, String> SHI_GAN_JI_GONG = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲", "寅");
            put("乙", "辰");
            put("丙", "巳");
            put("丁", "未");
            put("戊", "巳");
            put("己", "未");
            put("庚", "申");
            put("辛", "戌");
            put("壬", "亥");
            put("癸", "丑");
        }
    };

    /**
     * 贵人排列顺序
     */
    public static final List<String> GUI_REN_SHUN_XU = Arrays.asList("贵人", "螣蛇", "朱雀", "六合", "勾陈", "青龙", "天空", "白虎", "太常", "玄武", "太阴", "天后");

    /**
     * 贵人排列方向（0为顺排，1为逆排。地盘地支为键）
     */
    public static final Map<String, Integer> GUI_REN_FANG_XIANG = new HashMap<String, Integer>() {
        private static final long serialVersionUID = -1;

        {
            put("子", 0);
            put("丑", 0);
            put("寅", 0);
            put("卯", 0);
            put("辰", 0);
            put("巳", 1);
            put("午", 1);
            put("未", 1);
            put("申", 1);
            put("酉", 1);
            put("戌", 1);
            put("亥", 0);
        }
    };

    /**
     * 昼贵人（日干为键）
     */
    public static final Map<String, String> ZHOU_GUI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        /*
            甲、戊、庚日：昼贵在丑
            乙、己日：昼贵在子
            丙、丁日：昼贵在亥
            壬、癸日：昼贵在巳
            辛日：昼贵在午
         */

        {
            put("甲", "丑");
            put("乙", "子");
            put("丙", "亥");
            put("丁", "亥");
            put("戊", "丑");
            put("己", "子");
            put("庚", "丑");
            put("辛", "午");
            put("壬", "巳");
            put("癸", "巳");
        }
    };

    /**
     * 夜贵人（日干为键）
     */
    public static final Map<String, String> YE_GUI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        /*
            甲、戊、庚日：夜贵在未
            乙、己日：夜贵在申
            丙、丁日：夜贵在酉
            壬、癸日：夜贵在卯
            辛日：夜贵在寅
         */

        {
            put("甲", "未");
            put("乙", "申");
            put("丙", "酉");
            put("丁", "酉");
            put("戊", "未");
            put("己", "申");
            put("庚", "未");
            put("辛", "寅");
            put("壬", "卯");
            put("癸", "卯");
        }
    };

    /**
     * 昼贵人、夜贵人（日干+时支为键）
     */
    public static final Map<String, String> ZHOU_YE_GUI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        /*
            卯、辰、巳、午、未、申时为昼时
            子、丑、寅、酉、戌、亥时为夜时

            甲、戊、庚日：昼贵在丑，夜贵在未
            乙、己日：昼贵在子，夜贵在申
            丙、丁日：昼贵在亥，夜贵在酉
            壬、癸日：昼贵在巳，夜贵在卯
            辛日：昼贵在午，夜贵在寅
         */

        {
            // 例如：甲子日甲子时，子为夜时，则甲日夜贵在未
            put("甲子", "未");
            put("甲丑", "未");
            put("甲寅", "未");
            put("甲卯", "丑");
            put("甲辰", "丑");
            put("甲巳", "丑");
            put("甲午", "丑");
            put("甲未", "丑");
            put("甲申", "丑");
            put("甲酉", "未");
            put("甲戌", "未");
            put("甲亥", "未");

            put("乙子", "申");
            put("乙丑", "申");
            put("乙寅", "申");
            put("乙卯", "子");
            put("乙辰", "子");
            put("乙巳", "子");
            put("乙午", "子");
            put("乙未", "子");
            put("乙申", "子");
            put("乙酉", "申");
            put("乙戌", "申");
            put("乙亥", "申");

            put("丙子", "酉");
            put("丙丑", "酉");
            put("丙寅", "酉");
            put("丙卯", "亥");
            put("丙辰", "亥");
            put("丙巳", "亥");
            put("丙午", "亥");
            put("丙未", "亥");
            put("丙申", "亥");
            put("丙酉", "酉");
            put("丙戌", "酉");
            put("丙亥", "酉");

            put("丁子", "酉");
            put("丁丑", "酉");
            put("丁寅", "酉");
            put("丁卯", "亥");
            put("丁辰", "亥");
            put("丁巳", "亥");
            put("丁午", "亥");
            put("丁未", "亥");
            put("丁申", "亥");
            put("丁酉", "酉");
            put("丁戌", "酉");
            put("丁亥", "酉");

            put("戊子", "未");
            put("戊丑", "未");
            put("戊寅", "未");
            put("戊卯", "丑");
            put("戊辰", "丑");
            put("戊巳", "丑");
            put("戊午", "丑");
            put("戊未", "丑");
            put("戊申", "丑");
            put("戊酉", "未");
            put("戊戌", "未");
            put("戊亥", "未");

            put("己子", "申");
            put("己丑", "申");
            put("己寅", "申");
            put("己卯", "子");
            put("己辰", "子");
            put("己巳", "子");
            put("己午", "子");
            put("己未", "子");
            put("己申", "子");
            put("己酉", "申");
            put("己戌", "申");
            put("己亥", "申");

            put("庚子", "未");
            put("庚丑", "未");
            put("庚寅", "未");
            put("庚卯", "丑");
            put("庚辰", "丑");
            put("庚巳", "丑");
            put("庚午", "丑");
            put("庚未", "丑");
            put("庚申", "丑");
            put("庚酉", "未");
            put("庚戌", "未");
            put("庚亥", "未");

            put("辛子", "寅");
            put("辛丑", "寅");
            put("辛寅", "寅");
            put("辛卯", "午");
            put("辛辰", "午");
            put("辛巳", "午");
            put("辛午", "午");
            put("辛未", "午");
            put("辛申", "午");
            put("辛酉", "寅");
            put("辛戌", "寅");
            put("辛亥", "寅");

            put("壬子", "卯");
            put("壬丑", "卯");
            put("壬寅", "卯");
            put("壬卯", "巳");
            put("壬辰", "巳");
            put("壬巳", "巳");
            put("壬午", "巳");
            put("壬未", "巳");
            put("壬申", "巳");
            put("壬酉", "卯");
            put("壬戌", "卯");
            put("壬亥", "卯");

            put("癸子", "卯");
            put("癸丑", "卯");
            put("癸寅", "卯");
            put("癸卯", "巳");
            put("癸辰", "巳");
            put("癸巳", "巳");
            put("癸午", "巳");
            put("癸未", "巳");
            put("癸申", "巳");
            put("癸酉", "卯");
            put("癸戌", "卯");
            put("癸亥", "卯");
        }
    };

    /**
     * 贼克法：下克上（地支+天干\地支为键）
     */
    public static final Map<String, List<String>> ZE_KE_XIA_KE_SHANG = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("子戊", Arrays.asList("子", "重审课")); // 贼：下克上，初传为子，重审课
            put("子己", Arrays.asList("子", "重审课"));
            put("子丑", Arrays.asList("子", "重审课"));
            put("子辰", Arrays.asList("子", "重审课"));
            put("子未", Arrays.asList("子", "重审课"));
            put("子戌", Arrays.asList("子", "重审课"));

            put("丑甲", Arrays.asList("丑", "重审课"));
            put("丑乙", Arrays.asList("丑", "重审课"));
            put("丑寅", Arrays.asList("丑", "重审课"));
            put("丑卯", Arrays.asList("丑", "重审课"));

            put("寅庚", Arrays.asList("寅", "重审课"));
            put("寅辛", Arrays.asList("寅", "重审课"));
            put("寅申", Arrays.asList("寅", "重审课"));
            put("寅酉", Arrays.asList("寅", "重审课"));

            put("卯庚", Arrays.asList("卯", "重审课"));
            put("卯辛", Arrays.asList("卯", "重审课"));
            put("卯申", Arrays.asList("卯", "重审课"));
            put("卯酉", Arrays.asList("卯", "重审课"));

            put("辰甲", Arrays.asList("辰", "重审课"));
            put("辰乙", Arrays.asList("辰", "重审课"));
            put("辰寅", Arrays.asList("辰", "重审课"));
            put("辰卯", Arrays.asList("辰", "重审课"));

            put("巳壬", Arrays.asList("巳", "重审课"));
            put("巳癸", Arrays.asList("巳", "重审课"));
            put("巳子", Arrays.asList("巳", "重审课"));
            put("巳亥", Arrays.asList("巳", "重审课"));

            put("午壬", Arrays.asList("午", "重审课"));
            put("午癸", Arrays.asList("午", "重审课"));
            put("午子", Arrays.asList("午", "重审课"));
            put("午亥", Arrays.asList("午", "重审课"));

            put("未甲", Arrays.asList("未", "重审课"));
            put("未乙", Arrays.asList("未", "重审课"));
            put("未寅", Arrays.asList("未", "重审课"));
            put("未卯", Arrays.asList("未", "重审课"));

            put("申丙", Arrays.asList("申", "重审课"));
            put("申丁", Arrays.asList("申", "重审课"));
            put("申巳", Arrays.asList("申", "重审课"));
            put("申午", Arrays.asList("申", "重审课"));

            put("酉丙", Arrays.asList("酉", "重审课"));
            put("酉丁", Arrays.asList("酉", "重审课"));
            put("酉巳", Arrays.asList("酉", "重审课"));
            put("酉午", Arrays.asList("酉", "重审课"));

            put("戌甲", Arrays.asList("戌", "重审课"));
            put("戌乙", Arrays.asList("戌", "重审课"));
            put("戌寅", Arrays.asList("戌", "重审课"));
            put("戌卯", Arrays.asList("戌", "重审课"));

            put("亥戊", Arrays.asList("亥", "重审课"));
            put("亥己", Arrays.asList("亥", "重审课"));
            put("亥丑", Arrays.asList("亥", "重审课"));
            put("亥辰", Arrays.asList("亥", "重审课"));
            put("亥未", Arrays.asList("亥", "重审课"));
            put("亥戌", Arrays.asList("亥", "重审课"));
        }
    };

    /**
     * 贼克法：上克下（地支+天干\地支为键）
     */
    public static final Map<String, List<String>> ZE_KE_SHANG_KE_XIA = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("子丙", Arrays.asList("子", "元首课")); // 克：上克下，初传为丙，元首课
            put("子丁", Arrays.asList("子", "元首课"));
            put("子巳", Arrays.asList("子", "元首课"));
            put("子午", Arrays.asList("子", "元首课"));

            put("丑壬", Arrays.asList("丑", "元首课"));
            put("丑癸", Arrays.asList("丑", "元首课"));
            put("丑子", Arrays.asList("丑", "元首课"));
            put("丑亥", Arrays.asList("丑", "元首课"));

            put("寅戊", Arrays.asList("寅", "元首课"));
            put("寅己", Arrays.asList("寅", "元首课"));
            put("寅丑", Arrays.asList("寅", "元首课"));
            put("寅辰", Arrays.asList("寅", "元首课"));
            put("寅未", Arrays.asList("寅", "元首课"));
            put("寅戌", Arrays.asList("寅", "元首课"));

            put("卯戊", Arrays.asList("卯", "元首课"));
            put("卯己", Arrays.asList("卯", "元首课"));
            put("卯丑", Arrays.asList("卯", "元首课"));
            put("卯辰", Arrays.asList("卯", "元首课"));
            put("卯未", Arrays.asList("卯", "元首课"));
            put("卯戌", Arrays.asList("卯", "元首课"));

            put("辰壬", Arrays.asList("辰", "元首课"));
            put("辰癸", Arrays.asList("辰", "元首课"));
            put("辰子", Arrays.asList("辰", "元首课"));
            put("辰亥", Arrays.asList("辰", "元首课"));

            put("巳庚", Arrays.asList("巳", "元首课"));
            put("巳辛", Arrays.asList("巳", "元首课"));
            put("巳申", Arrays.asList("巳", "元首课"));
            put("巳酉", Arrays.asList("巳", "元首课"));

            put("午庚", Arrays.asList("午", "元首课"));
            put("午辛", Arrays.asList("午", "元首课"));
            put("午申", Arrays.asList("午", "元首课"));
            put("午酉", Arrays.asList("午", "元首课"));

            put("未壬", Arrays.asList("未", "元首课"));
            put("未癸", Arrays.asList("未", "元首课"));
            put("未子", Arrays.asList("未", "元首课"));
            put("未亥", Arrays.asList("未", "元首课"));

            put("申甲", Arrays.asList("申", "元首课"));
            put("申乙", Arrays.asList("申", "元首课"));
            put("申寅", Arrays.asList("申", "元首课"));
            put("申卯", Arrays.asList("申", "元首课"));

            put("酉甲", Arrays.asList("酉", "元首课"));
            put("酉乙", Arrays.asList("酉", "元首课"));
            put("酉寅", Arrays.asList("酉", "元首课"));
            put("酉卯", Arrays.asList("酉", "元首课"));

            put("戌壬", Arrays.asList("戌", "元首课"));
            put("戌癸", Arrays.asList("戌", "元首课"));
            put("戌子", Arrays.asList("戌", "元首课"));
            put("戌亥", Arrays.asList("戌", "元首课"));

            put("亥丙", Arrays.asList("亥", "元首课"));
            put("亥丁", Arrays.asList("亥", "元首课"));
            put("亥巳", Arrays.asList("亥", "元首课"));
            put("亥午", Arrays.asList("亥", "元首课"));
        }
    };

    /**
     * 地支对应孟仲季（地支为键）
     */
    public static final Map<String, String> DI_ZHI_MENG_ZHONG_JI = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子", "仲");
            put("丑", "季");
            put("寅", "孟");
            put("卯", "仲");
            put("辰", "季");
            put("巳", "孟");
            put("午", "仲");
            put("未", "季");
            put("申", "孟");
            put("酉", "仲");
            put("戌", "季");
            put("亥", "孟");
        }
    };

    /**
     * 干支相克（地支+天干为键）
     */
    public static final Map<String, String> ZHI_GAN_XIANG_KE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("申甲", "克"); // 地支[申]克天干[甲]
            put("酉甲", "克");

            put("申乙", "克");
            put("酉乙", "克");

            put("子丙", "克");
            put("亥丙", "克");

            put("子丁", "克");
            put("亥丁", "克");

            put("寅戊", "克");
            put("卯戊", "克");

            put("寅己", "克");
            put("卯己", "克");

            put("巳庚", "克");
            put("午庚", "克");

            put("巳辛", "克");
            put("午辛", "克");

            put("丑壬", "克");
            put("辰壬", "克");
            put("未壬", "克");
            put("戌壬", "克");

            put("丑癸", "克");
            put("辰癸", "克");
            put("未癸", "克");
            put("戌癸", "克");
        }
    };

    /**
     * 干支相克（天干+地支为键）
     */
    public static final Map<String, String> GAN_ZHI_XIANG_KE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        // 木克土、火克金、土克水、金克木、水克火

        {
            put("甲丑", "克"); // 天干[甲]克地支[丑]
            put("甲辰", "克");
            put("甲未", "克");
            put("甲戌", "克");

            put("乙丑", "克");
            put("乙辰", "克");
            put("乙未", "克");
            put("乙戌", "克");

            put("丙申", "克");
            put("丙酉", "克");

            put("丁申", "克");
            put("丁酉", "克");

            put("戊子", "克");
            put("戊癸", "克");

            put("己子", "克");
            put("己癸", "克");

            put("庚甲", "克");
            put("庚乙", "克");

            put("辛甲", "克");
            put("辛乙", "克");

            put("壬巳", "克");
            put("壬午", "克");

            put("癸巳", "克");
            put("癸午", "克");
        }
    };

    /**
     * 天干相合（天干为键）
     */
    public static final Map<String, String> TIAN_GAN_XIANG_HE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲", "己");
            put("乙", "庚");
            put("丙", "辛");
            put("丁", "壬");
            put("戊", "癸");

            put("己", "甲");
            put("庚", "乙");
            put("辛", "丙");
            put("壬", "丁");
            put("癸", "戊");
        }
    };

    /**
     * 地支相刑（地支为键）
     */
    public static final Map<String, String> DI_ZHI_XIANG_XING = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子", "卯");
            put("丑", "戌");
            put("寅", "巳");
            put("卯", "子");
            put("辰", "辰");
            put("巳", "申");
            put("午", "午");
            put("未", "丑");
            put("申", "寅");
            put("酉", "酉");
            put("戌", "未");
            put("亥", "亥");
        }
    };

    /**
     * 地支相冲（地支为键）
     */
    public static final Map<String, String> DI_ZHI_XIANG_CHONG = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子", "午");
            put("丑", "未");
            put("寅", "申");
            put("卯", "酉");
            put("辰", "戌");
            put("巳", "亥");
            put("午", "子");
            put("未", "丑");
            put("申", "寅");
            put("酉", "卯");
            put("戌", "辰");
            put("亥", "巳");
        }
    };

    /**
     * 地支三合前一个地支，顺时针（地支为键）
     */
    public static final Map<String, String> DI_ZHI_SAN_HE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子", "辰");
            put("丑", "巳");
            put("寅", "午");
            put("卯", "未");
            put("辰", "申");
            put("巳", "酉");
            put("午", "戌");
            put("未", "亥");
            put("申", "子");
            put("酉", "丑");
            put("戌", "寅");
            put("亥", "卯");
        }
    };

    /**
     * 驿马（地支为键）
     */
    public static final Map<String, String> YI_MA = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("申", "寅");
            put("子", "寅");
            put("辰", "寅");
            put("寅", "申");
            put("午", "申");
            put("戌", "申");
            put("巳", "亥");
            put("酉", "亥");
            put("丑", "亥");
            put("亥", "巳");
            put("卯", "巳");
            put("未", "巳");
        }
    };

    /**
     * 遁干，顺时针（最后空亡宫位（1~12宫）为键）
     */
    public static final Map<Integer, List<String>> DUN_GAN_SHUN = new HashMap<Integer, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put(1, Arrays.asList("○", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "○"));
            put(2, Arrays.asList("○", "○", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"));
            put(3, Arrays.asList("癸", "○", "○", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬"));
            put(4, Arrays.asList("壬", "癸", "○", "○", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛"));
            put(5, Arrays.asList("辛", "壬", "癸", "○", "○", "甲", "乙", "丙", "丁", "戊", "己", "庚"));
            put(6, Arrays.asList("庚", "辛", "壬", "癸", "○", "○", "甲", "乙", "丙", "丁", "戊", "己"));
            put(7, Arrays.asList("己", "庚", "辛", "壬", "癸", "○", "○", "甲", "乙", "丙", "丁", "戊"));
            put(8, Arrays.asList("戊", "己", "庚", "辛", "壬", "癸", "○", "○", "甲", "乙", "丙", "丁"));
            put(9, Arrays.asList("丁", "戊", "己", "庚", "辛", "壬", "癸", "○", "○", "甲", "乙", "丙"));
            put(10, Arrays.asList("丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "○", "○", "甲", "乙"));
            put(11, Arrays.asList("乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "○", "○", "甲"));
            put(12, Arrays.asList("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "○", "○"));
        }
    };

    /**
     * 干支生克对应六亲（天干+地支为键）
     */
    public static final Map<String, String> GAN_ZHI_SHENG_KE_LIU_QIN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲子", "父母"); // 甲+子（生我。子生甲→水生木）
            put("甲丑", "妻财"); // 甲+丑（我克。甲克丑→木克土）
            put("甲寅", "兄弟"); // 甲+寅（同我。甲同寅→木同木）
            put("甲卯", "兄弟"); // 甲+卯（同我。甲同卯→木同木）
            put("甲辰", "妻财"); // 甲+辰（我克。甲克辰→木克土）
            put("甲巳", "子孙"); // 甲+巳（我生。甲生巳→木生火）
            put("甲午", "子孙"); // 甲+午（我生。甲生午→木生火）
            put("甲未", "妻财"); // 甲+未（我克。甲克未→木克土）
            put("甲申", "官鬼"); // 甲+申（克我。申克甲→金克木）
            put("甲酉", "官鬼"); // 甲+酉（克我。酉克甲→金克木）
            put("甲戌", "妻财"); // 甲+戌（我克。甲克戌→木克土）
            put("甲亥", "父母"); // 甲+亥（生我。亥生甲→水生木）

            put("乙子", "父母"); // 乙+子（生我。子生乙→水生木）
            put("乙丑", "妻财"); // 乙+丑（我克。乙克丑→木克土）
            put("乙寅", "兄弟"); // 乙+寅（同我。乙同寅→木同木）
            put("乙卯", "兄弟"); // 乙+卯（同我。乙同卯→木同木）
            put("乙辰", "妻财"); // 乙+辰（我克。乙克辰→木克土）
            put("乙巳", "子孙"); // 乙+巳（我生。乙生巳→木生火）
            put("乙午", "子孙"); // 乙+午（我生。乙生午→木生火）
            put("乙未", "妻财"); // 乙+未（我克。乙克未→木克土）
            put("乙申", "官鬼"); // 乙+申（克我。申克乙→金克木）
            put("乙酉", "官鬼"); // 乙+酉（克我。酉克乙→金克木）
            put("乙戌", "妻财"); // 乙+戌（我克。乙克戌→木克土）
            put("乙亥", "父母"); // 乙+亥（生我。亥生乙→水生木）

            put("丙子", "官鬼"); // 丙+子（克我。子克丙→水克火）
            put("丙丑", "子孙"); // 丙+丑（我生。丙生丑→火生土）
            put("丙寅", "父母"); // 丙+寅（生我。丙生寅→木生火）
            put("丙卯", "父母"); // 丙+卯（生我。丙生卯→木生火）
            put("丙辰", "子孙"); // 丙+辰（我生。丙生辰→火生土）
            put("丙巳", "兄弟"); // 丙+巳（同我。丙同巳→火同火）
            put("丙午", "兄弟"); // 丙+午（同我。丙同午→火同火）
            put("丙未", "子孙"); // 丙+未（我生。丙生未→火生土）
            put("丙申", "妻财"); // 丙+申（我克。丙克申→火克金）
            put("丙酉", "妻财"); // 丙+酉（我克。丙克酉→火克金）
            put("丙戌", "子孙"); // 丙+戌（我生。丙生戌→火生土）
            put("丙亥", "官鬼"); // 丙+亥（克我。亥克丙→水克火）

            put("丁子", "官鬼"); // 丁+子（克我。子克丁→水克火）
            put("丁丑", "子孙"); // 丁+丑（我生。丁生丑→火生土）
            put("丁寅", "父母"); // 丁+寅（生我。丁生寅→木生火）
            put("丁卯", "父母"); // 丁+卯（生我。丁生卯→木生火）
            put("丁辰", "子孙"); // 丁+辰（我生。丁生辰→火生土）
            put("丁巳", "兄弟"); // 丁+巳（同我。丁同巳→火同火）
            put("丁午", "兄弟"); // 丁+午（同我。丁同午→火同火）
            put("丁未", "子孙"); // 丁+未（我生。丁生未→火生土）
            put("丁申", "妻财"); // 丁+申（我克。丁克申→火克金）
            put("丁酉", "妻财"); // 丁+酉（我克。丁克酉→火克金）
            put("丁戌", "子孙"); // 丁+戌（我生。丁生戌→火生土）
            put("丁亥", "官鬼"); // 丁+亥（克我。亥克丁→水克火）

            put("戊子", "妻财"); // 戊+子（我克。戊克子→土克水）
            put("戊丑", "兄弟"); // 戊+丑（同我。戊同丑→土同土）
            put("戊寅", "官鬼"); // 戊+寅（克我。寅克戊→木克土）
            put("戊卯", "官鬼"); // 戊+卯（克我。卯克戊→木克土）
            put("戊辰", "兄弟"); // 戊+辰（同我。戊同辰→土同土）
            put("戊巳", "父母"); // 戊+巳（生我。巳生戊→火生土）
            put("戊午", "父母"); // 戊+午（生我。午生戊→火生土）
            put("戊未", "兄弟"); // 戊+未（同我。戊同未→土同土）
            put("戊申", "子孙"); // 戊+申（我生。戊生申→土生金）
            put("戊酉", "子孙"); // 戊+酉（我生。戊生酉→土生金）
            put("戊戌", "兄弟"); // 戊+戌（同我。戊同戌→土同土）
            put("戊亥", "妻财"); // 戊+亥（我克。戊克亥→土克水）

            put("己子", "妻财"); // 己+子（我克。己克子→土克水）
            put("己丑", "兄弟"); // 己+丑（同我。己同丑→土同土）
            put("己寅", "官鬼"); // 己+寅（克我。寅克己→木克土）
            put("己卯", "官鬼"); // 己+卯（克我。卯克己→木克土）
            put("己辰", "兄弟"); // 己+辰（同我。己同辰→土同土）
            put("己巳", "父母"); // 己+巳（生我。巳生己→火生土）
            put("己午", "父母"); // 己+午（生我。午生己→火生土）
            put("己未", "兄弟"); // 己+未（同我。己同未→土同土）
            put("己申", "子孙"); // 己+申（我生。己生申→土生金）
            put("己酉", "子孙"); // 己+酉（我生。己生酉→土生金）
            put("己戌", "兄弟"); // 己+戌（同我。己同戌→土同土）
            put("己亥", "妻财"); // 己+亥（我克。己克亥→土克水）

            put("庚子", "子孙"); // 庚+子（我生。庚生子→金生水）
            put("庚丑", "父母"); // 庚+丑（生我。丑生庚→土生金）
            put("庚寅", "妻财"); // 庚+寅（我克。庚克寅→金克木）
            put("庚卯", "妻财"); // 庚+卯（我克。庚克卯→金克木）
            put("庚辰", "父母"); // 庚+辰（生我。辰生庚→土生金）
            put("庚巳", "官鬼"); // 庚+巳（克我。巳克庚→火克金）
            put("庚午", "官鬼"); // 庚+午（克我。午克庚→火克金）
            put("庚未", "父母"); // 庚+未（生我。未生庚→土生金）
            put("庚申", "兄弟"); // 庚+申（同我。庚同申→金同金）
            put("庚酉", "兄弟"); // 庚+酉（同我。庚同酉→金同金）
            put("庚戌", "父母"); // 庚+戌（生我。戌生庚→土生金）
            put("庚亥", "子孙"); // 庚+亥（我生。庚生亥→金生水）

            put("辛子", "子孙"); // 辛+子（我生。辛生子→金生水）
            put("辛丑", "父母"); // 辛+丑（生我。丑生辛→土生金）
            put("辛寅", "妻财"); // 辛+寅（我克。辛克寅→金克木）
            put("辛卯", "妻财"); // 辛+卯（我克。辛克卯→金克木）
            put("辛辰", "父母"); // 辛+辰（生我。辰生辛→土生金）
            put("辛巳", "官鬼"); // 辛+巳（克我。巳克辛→火克金）
            put("辛午", "官鬼"); // 辛+午（克我。午克辛→火克金）
            put("辛未", "父母"); // 辛+未（生我。未生辛→土生金）
            put("辛申", "兄弟"); // 辛+申（同我。辛同申→金同金）
            put("辛酉", "兄弟"); // 辛+酉（同我。辛同酉→金同金）
            put("辛戌", "父母"); // 辛+戌（生我。戌生辛→土生金）
            put("辛亥", "子孙"); // 辛+亥（我生。辛生亥→金生水）

            put("壬子", "兄弟"); // 壬+子（同我。壬同子→水同水）
            put("壬丑", "官鬼"); // 壬+丑（克我。丑克壬→土克水）
            put("壬寅", "子孙"); // 壬+寅（我生。寅生壬→水生木）
            put("壬卯", "子孙"); // 壬+卯（我生。卯生壬→水生木）
            put("壬辰", "官鬼"); // 壬+辰（克我。辰克壬→土克水）
            put("壬巳", "妻财"); // 壬+巳（我克。壬克巳→水克火）
            put("壬午", "妻财"); // 壬+午（我克。壬克午→水克火）
            put("壬未", "官鬼"); // 壬+未（克我。未克壬→土克水）
            put("壬申", "父母"); // 壬+申（生我。申生壬→金生水）
            put("壬酉", "父母"); // 壬+酉（生我。酉生壬→金生水）
            put("壬戌", "官鬼"); // 壬+戌（克我。戌克壬→土克水）
            put("壬亥", "兄弟"); // 壬+亥（同我。壬同亥→水同水）

            put("癸子", "兄弟"); // 癸+子（同我。癸同子→水同水）
            put("癸丑", "官鬼"); // 癸+丑（克我。丑克癸→土克水）
            put("癸寅", "子孙"); // 癸+寅（我生。寅生癸→水生木）
            put("癸卯", "子孙"); // 癸+卯（我生。卯生癸→水生木）
            put("癸辰", "官鬼"); // 癸+辰（克我。辰克癸→土克水）
            put("癸巳", "妻财"); // 癸+巳（我克。癸克巳→水克火）
            put("癸午", "妻财"); // 癸+午（我克。癸克午→水克火）
            put("癸未", "官鬼"); // 癸+未（克我。未克癸→土克水）
            put("癸申", "父母"); // 癸+申（生我。申生癸→金生水）
            put("癸酉", "父母"); // 癸+酉（生我。酉生癸→金生水）
            put("癸戌", "官鬼"); // 癸+戌（克我。戌克癸→土克水）
            put("癸亥", "兄弟"); // 癸+亥（同我。癸同亥→水同水）
        }
    };

    /**
     * 三传（日干支+第一课天盘为键）
     */
    public static final Map<String, List<String>> SAN_CHUAN = new HashMap<String, List<String>>() {
        private static final long serialVersionUID = -1;

        {
            put("甲子子", Arrays.asList("戌", "申", "午"));
            put("甲子丑", Arrays.asList("子", "亥", "戌"));
            put("甲子寅", Arrays.asList("寅", "巳", "申"));
            put("甲子卯", Arrays.asList("辰", "巳", "午"));
            put("甲子辰", Arrays.asList("辰", "午", "申"));
            put("甲子巳", Arrays.asList("申", "亥", "寅"));
            put("甲子午", Arrays.asList("申", "亥", "寅"));
            put("甲子未", Arrays.asList("辰", "申", "子"));
            put("甲子申", Arrays.asList("子", "巳", "戌"));
            put("甲子酉", Arrays.asList("寅", "申", "寅"));
            put("甲子戌", Arrays.asList("寅", "酉", "辰"));
            put("甲子亥", Arrays.asList("戌", "午", "寅"));

            put("甲戌子", Arrays.asList("午", "辰", "寅"));
            put("甲戌丑", Arrays.asList("子", "亥", "戌"));
            put("甲戌寅", Arrays.asList("寅", "巳", "申"));
            put("甲戌卯", Arrays.asList("辰", "巳", "午"));
            put("甲戌辰", Arrays.asList("辰", "午", "申"));
            put("甲戌巳", Arrays.asList("申", "亥", "寅"));
            put("甲戌午", Arrays.asList("寅", "午", "戌"));
            put("甲戌未", Arrays.asList("子", "巳", "戌"));
            put("甲戌申", Arrays.asList("寅", "申", "寅"));
            put("甲戌酉", Arrays.asList("子", "未", "寅"));
            put("甲戌戌", Arrays.asList("戌", "午", "寅"));
            put("甲戌亥", Arrays.asList("申", "巳", "寅"));

            put("甲申子", Arrays.asList("午", "辰", "寅"));
            put("甲申丑", Arrays.asList("子", "亥", "戌"));
            put("甲申寅", Arrays.asList("寅", "巳", "申"));
            put("甲申卯", Arrays.asList("辰", "巳", "午"));
            put("甲申辰", Arrays.asList("辰", "午", "申"));
            put("甲申巳", Arrays.asList("申", "亥", "寅"));
            put("甲申午", Arrays.asList("辰", "申", "子"));
            put("甲申未", Arrays.asList("子", "巳", "戌"));
            put("甲申申", Arrays.asList("寅", "申", "寅"));
            put("甲申酉", Arrays.asList("戌", "巳", "子"));
            put("甲申戌", Arrays.asList("戌", "午", "寅"));
            put("甲申亥", Arrays.asList("巳", "寅", "亥"));

            put("甲午子", Arrays.asList("寅", "子", "戌"));
            put("甲午丑", Arrays.asList("子", "亥", "戌"));
            put("甲午寅", Arrays.asList("寅", "巳", "申"));
            put("甲午卯", Arrays.asList("辰", "巳", "午"));
            put("甲午辰", Arrays.asList("辰", "午", "申"));
            put("甲午巳", Arrays.asList("申", "亥", "寅"));
            put("甲午午", Arrays.asList("寅", "午", "戌"));
            put("甲午未", Arrays.asList("子", "巳", "戌"));
            put("甲午申", Arrays.asList("寅", "申", "寅"));
            put("甲午酉", Arrays.asList("酉", "辰", "亥"));
            put("甲午戌", Arrays.asList("戌", "午", "寅"));
            put("甲午亥", Arrays.asList("申", "巳", "寅"));

            put("甲辰子", Arrays.asList("寅", "子", "戌"));
            put("甲辰丑", Arrays.asList("子", "亥", "戌"));
            put("甲辰寅", Arrays.asList("寅", "巳", "申"));
            put("甲辰卯", Arrays.asList("辰", "巳", "午"));
            put("甲辰辰", Arrays.asList("辰", "午", "申"));
            put("甲辰巳", Arrays.asList("申", "亥", "寅"));
            put("甲辰午", Arrays.asList("申", "子", "辰"));
            put("甲辰未", Arrays.asList("子", "巳", "戌"));
            put("甲辰申", Arrays.asList("寅", "申", "寅"));
            put("甲辰酉", Arrays.asList("午", "丑", "申"));
            put("甲辰戌", Arrays.asList("子", "申", "辰"));
            put("甲辰亥", Arrays.asList("申", "巳", "寅"));

            put("甲寅子", Arrays.asList("戌", "申", "午"));
            put("甲寅丑", Arrays.asList("子", "亥", "戌"));
            put("甲寅寅", Arrays.asList("寅", "巳", "申"));
            put("甲寅卯", Arrays.asList("辰", "巳", "午"));
            put("甲寅辰", Arrays.asList("辰", "午", "申"));
            put("甲寅巳", Arrays.asList("申", "亥", "寅"));
            put("甲寅午", Arrays.asList("申", "午", "午"));
            put("甲寅未", Arrays.asList("子", "巳", "戌"));
            put("甲寅申", Arrays.asList("寅", "申", "寅"));
            put("甲寅酉", Arrays.asList("酉", "辰", "亥"));
            put("甲寅戌", Arrays.asList("戌", "午", "寅"));
            put("甲寅亥", Arrays.asList("丑", "亥", "亥"));

            put("乙丑子", Arrays.asList("巳", "丑", "酉"));
            put("乙丑丑", Arrays.asList("丑", "戌", "未"));
            put("乙丑寅", Arrays.asList("亥", "酉", "未"));
            put("乙丑卯", Arrays.asList("子", "亥", "戌"));
            put("乙丑辰", Arrays.asList("辰", "丑", "戌"));
            put("乙丑巳", Arrays.asList("寅", "卯", "辰"));
            put("乙丑午", Arrays.asList("申", "戌", "子"));
            put("乙丑未", Arrays.asList("未", "戌", "丑"));
            put("乙丑申", Arrays.asList("酉", "丑", "巳"));
            put("乙丑酉", Arrays.asList("寅", "未", "子"));
            put("乙丑戌", Arrays.asList("戌", "辰", "戌"));
            put("乙丑亥", Arrays.asList("卯", "戌", "巳"));

            put("乙亥子", Arrays.asList("未", "卯", "亥"));
            put("乙亥丑", Arrays.asList("丑", "戌", "未"));
            put("乙亥寅", Arrays.asList("酉", "未", "巳"));
            put("乙亥卯", Arrays.asList("戌", "酉", "申"));
            put("乙亥辰", Arrays.asList("辰", "亥", "巳"));
            put("乙亥巳", Arrays.asList("丑", "寅", "卯"));
            put("乙亥午", Arrays.asList("申", "戌", "子"));
            put("乙亥未", Arrays.asList("未", "戌", "丑"));
            put("乙亥申", Arrays.asList("未", "亥", "卯"));
            put("乙亥酉", Arrays.asList("寅", "未", "子"));
            put("乙亥戌", Arrays.asList("巳", "亥", "巳"));
            put("乙亥亥", Arrays.asList("午", "丑", "申"));

            put("乙酉子", Arrays.asList("巳", "丑", "酉"));
            put("乙酉丑", Arrays.asList("丑", "戌", "未"));
            put("乙酉寅", Arrays.asList("未", "巳", "卯"));
            put("乙酉卯", Arrays.asList("申", "未", "午"));
            put("乙酉辰", Arrays.asList("辰", "酉", "卯"));
            put("乙酉巳", Arrays.asList("亥", "子", "丑"));
            put("乙酉午", Arrays.asList("申", "戌", "子"));
            put("乙酉未", Arrays.asList("未", "戌", "丑"));
            put("乙酉申", Arrays.asList("申", "子", "辰"));
            put("乙酉酉", Arrays.asList("未", "子", "巳"));
            put("乙酉戌", Arrays.asList("卯", "酉", "卯"));
            put("乙酉亥", Arrays.asList("亥", "午", "丑"));

            put("乙未子", Arrays.asList("卯", "亥", "未"));
            put("乙未丑", Arrays.asList("丑", "戌", "未"));
            put("乙未寅", Arrays.asList("亥", "寅", "巳"));
            put("乙未卯", Arrays.asList("戌", "卯", "午"));
            put("乙未辰", Arrays.asList("辰", "未", "丑"));
            put("乙未巳", Arrays.asList("酉", "戌", "亥"));
            put("乙未午", Arrays.asList("申", "戌", "子"));
            put("乙未未", Arrays.asList("未", "戌", "丑"));
            put("乙未申", Arrays.asList("亥", "卯", "未"));
            put("乙未酉", Arrays.asList("巳", "戌", "卯"));
            put("乙未戌", Arrays.asList("戌", "辰", "戌"));
            put("乙未亥", Arrays.asList("午", "丑", "申"));

            put("乙巳子", Arrays.asList("酉", "巳", "丑"));
            put("乙巳丑", Arrays.asList("丑", "戌", "未"));
            put("乙巳寅", Arrays.asList("丑", "亥", "酉"));
            put("乙巳卯", Arrays.asList("卯", "寅", "丑"));
            put("乙巳辰", Arrays.asList("辰", "巳", "申"));
            put("乙巳巳", Arrays.asList("未", "申", "酉"));
            put("乙巳午", Arrays.asList("申", "戌", "子"));
            put("乙巳未", Arrays.asList("未", "戌", "丑"));
            put("乙巳申", Arrays.asList("酉", "丑", "巳"));
            put("乙巳酉", Arrays.asList("寅", "未", "子"));
            put("乙巳戌", Arrays.asList("巳", "亥", "巳"));
            put("乙巳亥", Arrays.asList("午", "丑", "申"));

            put("乙卯子", Arrays.asList("未", "卯", "亥"));
            put("乙卯丑", Arrays.asList("丑", "戌", "未"));
            put("乙卯寅", Arrays.asList("亥", "酉", "未"));
            put("乙卯卯", Arrays.asList("丑", "子", "亥"));
            put("乙卯辰", Arrays.asList("辰", "卯", "子"));
            put("乙卯巳", Arrays.asList("辰", "巳", "午"));
            put("乙卯午", Arrays.asList("申", "戌", "子"));
            put("乙卯未", Arrays.asList("酉", "子", "卯"));
            put("乙卯申", Arrays.asList("亥", "卯", "未"));
            put("乙卯酉", Arrays.asList("寅", "未", "子"));
            put("乙卯戌", Arrays.asList("卯", "酉", "卯"));
            put("乙卯亥", Arrays.asList("午", "丑", "申"));

            put("丙子子", Arrays.asList("子", "未", "寅"));
            put("丙子丑", Arrays.asList("申", "辰", "子"));
            put("丙子寅", Arrays.asList("午", "卯", "子"));
            put("丙子卯", Arrays.asList("丑", "亥", "酉"));
            put("丙子辰", Arrays.asList("戌", "酉", "申"));
            put("丙子巳", Arrays.asList("巳", "申", "寅"));
            put("丙子午", Arrays.asList("寅", "卯", "辰"));
            put("丙子未", Arrays.asList("辰", "午", "申"));
            put("丙子申", Arrays.asList("申", "亥", "寅"));
            put("丙子酉", Arrays.asList("酉", "丑", "巳"));
            put("丙子戌", Arrays.asList("巳", "戌", "卯"));
            put("丙子亥", Arrays.asList("午", "子", "午"));

            put("丙戌子", Arrays.asList("子", "未", "寅"));
            put("丙戌丑", Arrays.asList("酉", "巳", "丑"));
            put("丙戌寅", Arrays.asList("亥", "申", "巳"));
            put("丙戌卯", Arrays.asList("丑", "亥", "酉"));
            put("丙戌辰", Arrays.asList("卯", "寅", "丑"));
            put("丙戌巳", Arrays.asList("巳", "申", "寅"));
            put("丙戌午", Arrays.asList("亥", "子", "丑"));
            put("丙戌未", Arrays.asList("子", "寅", "辰"));
            put("丙戌申", Arrays.asList("申", "亥", "寅"));
            put("丙戌酉", Arrays.asList("酉", "丑", "巳"));
            put("丙戌戌", Arrays.asList("申", "丑", "午"));
            put("丙戌亥", Arrays.asList("巳", "亥", "巳"));

            put("丙申子", Arrays.asList("戌", "巳", "子"));
            put("丙申丑", Arrays.asList("子", "申", "辰"));
            put("丙申寅", Arrays.asList("巳", "寅", "亥"));
            put("丙申卯", Arrays.asList("丑", "亥", "酉"));
            put("丙申辰", Arrays.asList("卯", "寅", "丑"));
            put("丙申巳", Arrays.asList("巳", "申", "寅"));
            put("丙申午", Arrays.asList("酉", "戌", "亥"));
            put("丙申未", Arrays.asList("子", "寅", "辰"));
            put("丙申申", Arrays.asList("申", "亥", "寅"));
            put("丙申酉", Arrays.asList("酉", "丑", "巳"));
            put("丙申戌", Arrays.asList("卯", "申", "丑"));
            put("丙申亥", Arrays.asList("寅", "申", "寅"));

            put("丙午子", Arrays.asList("子", "未", "寅"));
            put("丙午丑", Arrays.asList("戌", "午", "寅"));
            put("丙午寅", Arrays.asList("子", "酉", "午"));
            put("丙午卯", Arrays.asList("丑", "亥", "酉"));
            put("丙午辰", Arrays.asList("卯", "寅", "丑"));
            put("丙午巳", Arrays.asList("巳", "申", "寅"));
            put("丙午午", Arrays.asList("申", "酉", "戌"));
            put("丙午未", Arrays.asList("申", "戌", "子"));
            put("丙午申", Arrays.asList("申", "亥", "寅"));
            put("丙午酉", Arrays.asList("酉", "丑", "巳"));
            put("丙午戌", Arrays.asList("辰", "酉", "寅"));
            put("丙午亥", Arrays.asList("午", "子", "午"));

            put("丙辰子", Arrays.asList("午", "丑", "申"));
            put("丙辰丑", Arrays.asList("子", "申", "辰"));
            put("丙辰寅", Arrays.asList("亥", "申", "巳"));
            put("丙辰卯", Arrays.asList("丑", "亥", "酉"));
            put("丙辰辰", Arrays.asList("卯", "寅", "丑"));
            put("丙辰巳", Arrays.asList("巳", "申", "寅"));
            put("丙辰午", Arrays.asList("亥", "午", "午"));
            put("丙辰未", Arrays.asList("申", "戌", "子"));
            put("丙辰申", Arrays.asList("申", "亥", "寅"));
            put("丙辰酉", Arrays.asList("酉", "丑", "巳"));
            put("丙辰戌", Arrays.asList("寅", "未", "子"));
            put("丙辰亥", Arrays.asList("巳", "亥", "巳"));

            put("丙寅子", Arrays.asList("子", "未", "寅"));
            put("丙寅丑", Arrays.asList("戌", "午", "寅"));
            put("丙寅寅", Arrays.asList("亥", "申", "巳"));
            put("丙寅卯", Arrays.asList("丑", "亥", "酉"));
            put("丙寅辰", Arrays.asList("子", "亥", "戌"));
            put("丙寅巳", Arrays.asList("巳", "申", "寅"));
            put("丙寅午", Arrays.asList("辰", "巳", "午"));
            put("丙寅未", Arrays.asList("辰", "午", "申"));
            put("丙寅申", Arrays.asList("申", "亥", "寅"));
            put("丙寅酉", Arrays.asList("酉", "丑", "巳"));
            put("丙寅戌", Arrays.asList("子", "巳", "戌"));
            put("丙寅亥", Arrays.asList("寅", "申", "寅"));

            put("丁丑子", Arrays.asList("巳", "戌", "卯"));
            put("丁丑丑", Arrays.asList("亥", "未", "丑"));
            put("丁丑寅", Arrays.asList("卯", "戌", "巳"));
            put("丁丑卯", Arrays.asList("巳", "丑", "酉"));
            put("丁丑辰", Arrays.asList("子", "辰", "戌"));
            put("丁丑巳", Arrays.asList("亥", "酉", "未"));
            put("丁丑午", Arrays.asList("子", "亥", "戌"));
            put("丁丑未", Arrays.asList("丑", "戌", "未"));
            put("丁丑申", Arrays.asList("申", "酉", "戌"));
            put("丁丑酉", Arrays.asList("酉", "亥", "丑"));
            put("丁丑戌", Arrays.asList("午", "戌", "辰"));
            put("丁丑亥", Arrays.asList("酉", "丑", "巳"));

            put("丁亥子", Arrays.asList("巳", "戌", "卯"));
            put("丁亥丑", Arrays.asList("巳", "亥", "巳"));
            put("丁亥寅", Arrays.asList("午", "丑", "申"));
            put("丁亥卯", Arrays.asList("未", "卯", "亥"));
            put("丁亥辰", Arrays.asList("巳", "亥", "寅"));
            put("丁亥巳", Arrays.asList("酉", "未", "巳"));
            put("丁亥午", Arrays.asList("戌", "酉", "申"));
            put("丁亥未", Arrays.asList("亥", "未", "丑"));
            put("丁亥申", Arrays.asList("申", "酉", "戌"));
            put("丁亥酉", Arrays.asList("酉", "亥", "丑"));
            put("丁亥戌", Arrays.asList("午", "戌", "寅"));
            put("丁亥亥", Arrays.asList("未", "亥", "卯"));

            put("丁酉子", Arrays.asList("未", "子", "巳"));
            put("丁酉丑", Arrays.asList("卯", "酉", "卯"));
            put("丁酉寅", Arrays.asList("亥", "午", "丑"));
            put("丁酉卯", Arrays.asList("巳", "丑", "酉"));
            put("丁酉辰", Arrays.asList("午", "卯", "子"));
            put("丁酉巳", Arrays.asList("丑", "巳", "巳"));
            put("丁酉午", Arrays.asList("申", "未", "午"));
            put("丁酉未", Arrays.asList("酉", "未", "丑"));
            put("丁酉申", Arrays.asList("亥", "子", "丑"));
            put("丁酉酉", Arrays.asList("酉", "亥", "丑"));
            put("丁酉戌", Arrays.asList("子", "卯", "午"));
            put("丁酉亥", Arrays.asList("亥", "卯", "未"));

            put("丁未子", Arrays.asList("巳", "戌", "卯"));
            put("丁未丑", Arrays.asList("巳", "丑", "丑"));
            put("丁未寅", Arrays.asList("酉", "辰", "亥"));
            put("丁未卯", Arrays.asList("卯", "亥", "未"));
            put("丁未辰", Arrays.asList("亥", "辰", "辰"));
            put("丁未巳", Arrays.asList("丑", "巳", "巳"));
            put("丁未午", Arrays.asList("卯", "午", "午"));
            put("丁未未", Arrays.asList("未", "丑", "戌"));
            put("丁未申", Arrays.asList("申", "酉", "戌"));
            put("丁未酉", Arrays.asList("酉", "亥", "丑"));
            put("丁未戌", Arrays.asList("亥", "戌", "戌"));
            put("丁未亥", Arrays.asList("亥", "卯", "未"));

            put("丁巳子", Arrays.asList("巳", "戌", "卯"));
            put("丁巳丑", Arrays.asList("巳", "亥", "巳"));
            put("丁巳寅", Arrays.asList("酉", "辰", "亥"));
            put("丁巳卯", Arrays.asList("亥", "未", "卯"));
            put("丁巳辰", Arrays.asList("亥", "申", "巳"));
            put("丁巳巳", Arrays.asList("丑", "亥", "酉"));
            put("丁巳午", Arrays.asList("卯", "寅", "丑"));
            put("丁巳未", Arrays.asList("巳", "申", "寅"));
            put("丁巳申", Arrays.asList("申", "酉", "戌"));
            put("丁巳酉", Arrays.asList("酉", "亥", "丑"));
            put("丁巳戌", Arrays.asList("申", "亥", "寅"));
            put("丁巳亥", Arrays.asList("酉", "丑", "巳"));

            put("丁卯子", Arrays.asList("巳", "戌", "卯"));
            put("丁卯丑", Arrays.asList("卯", "酉", "卯"));
            put("丁卯寅", Arrays.asList("戌", "巳", "子"));
            put("丁卯卯", Arrays.asList("未", "卯", "亥"));
            put("丁卯辰", Arrays.asList("子", "酉", "午"));
            put("丁卯巳", Arrays.asList("亥", "酉", "未"));
            put("丁卯午", Arrays.asList("丑", "子", "亥"));
            put("丁卯未", Arrays.asList("卯", "子", "午"));
            put("丁卯申", Arrays.asList("辰", "巳", "午"));
            put("丁卯酉", Arrays.asList("酉", "亥", "丑"));
            put("丁卯戌", Arrays.asList("酉", "子", "卯"));
            put("丁卯亥", Arrays.asList("亥", "卯", "未"));

            put("戊子子", Arrays.asList("子", "未", "寅"));
            put("戊子丑", Arrays.asList("巳", "申", "丑"));
            put("戊子寅", Arrays.asList("寅", "亥", "申"));
            put("戊子卯", Arrays.asList("丑", "亥", "酉"));
            put("戊子辰", Arrays.asList("戌", "酉", "申"));
            put("戊子巳", Arrays.asList("巳", "申", "寅"));
            put("戊子午", Arrays.asList("寅", "卯", "辰"));
            put("戊子未", Arrays.asList("辰", "午", "申"));
            put("戊子申", Arrays.asList("卯", "午", "酉"));
            put("戊子酉", Arrays.asList("辰", "申", "子"));
            put("戊子戌", Arrays.asList("巳", "戌", "卯"));
            put("戊子亥", Arrays.asList("午", "子", "午"));

            put("戊戌子", Arrays.asList("子", "未", "寅"));
            put("戊戌丑", Arrays.asList("寅", "戌", "午"));
            put("戊戌寅", Arrays.asList("寅", "亥", "申"));
            put("戊戌卯", Arrays.asList("丑", "亥", "酉"));
            put("戊戌辰", Arrays.asList("卯", "寅", "丑"));
            put("戊戌巳", Arrays.asList("巳", "申", "寅"));
            put("戊戌午", Arrays.asList("亥", "子", "丑"));
            put("戊戌未", Arrays.asList("子", "寅", "辰"));
            put("戊戌申", Arrays.asList("亥", "寅", "巳"));
            put("戊戌酉", Arrays.asList("寅", "午", "戌"));
            put("戊戌戌", Arrays.asList("申", "丑", "午"));
            put("戊戌亥", Arrays.asList("亥", "巳", "亥"));

            put("戊申子", Arrays.asList("子", "未", "寅"));
            put("戊申丑", Arrays.asList("子", "申", "辰"));
            put("戊申寅", Arrays.asList("寅", "亥", "申"));
            put("戊申卯", Arrays.asList("丑", "亥", "酉"));
            put("戊申辰", Arrays.asList("卯", "寅", "丑"));
            put("戊申巳", Arrays.asList("巳", "申", "寅"));
            put("戊申午", Arrays.asList("戌", "酉", "午"));
            put("戊申未", Arrays.asList("子", "寅", "辰"));
            put("戊申申", Arrays.asList("寅", "巳", "申"));
            put("戊申酉", Arrays.asList("辰", "申", "子"));
            put("戊申戌", Arrays.asList("卯", "申", "丑"));
            put("戊申亥", Arrays.asList("寅", "申", "寅"));

            put("戊午子", Arrays.asList("子", "未", "寅"));
            put("戊午丑", Arrays.asList("戌", "午", "申"));
            put("戊午寅", Arrays.asList("寅", "亥", "申"));
            put("戊午卯", Arrays.asList("丑", "亥", "酉"));
            put("戊午辰", Arrays.asList("卯", "寅", "丑"));
            put("戊午巳", Arrays.asList("巳", "申", "寅"));
            put("戊午午", Arrays.asList("寅", "午", "午"));
            put("戊午未", Arrays.asList("申", "戌", "子"));
            put("戊午申", Arrays.asList("酉", "子", "卯"));
            put("戊午酉", Arrays.asList("寅", "午", "戌"));
            put("戊午戌", Arrays.asList("辰", "酉", "寅"));
            put("戊午亥", Arrays.asList("午", "子", "午"));

            put("戊辰子", Arrays.asList("子", "未", "寅"));
            put("戊辰丑", Arrays.asList("子", "申", "辰"));
            put("戊辰寅", Arrays.asList("寅", "亥", "申"));
            put("戊辰卯", Arrays.asList("丑", "亥", "酉"));
            put("戊辰辰", Arrays.asList("卯", "寅", "丑"));
            put("戊辰巳", Arrays.asList("巳", "申", "寅"));
            put("戊辰午", Arrays.asList("寅", "午", "午"));
            put("戊辰未", Arrays.asList("申", "戌", "子"));
            put("戊辰申", Arrays.asList("亥", "寅", "巳"));
            put("戊辰酉", Arrays.asList("子", "辰", "申"));
            put("戊辰戌", Arrays.asList("寅", "未", "子"));
            put("戊辰亥", Arrays.asList("亥", "巳", "亥"));

            put("戊寅子", Arrays.asList("子", "未", "寅"));
            put("戊寅丑", Arrays.asList("戌", "午", "寅"));
            put("戊寅寅", Arrays.asList("寅", "亥", "申"));
            put("戊寅卯", Arrays.asList("丑", "亥", "酉"));
            put("戊寅辰", Arrays.asList("子", "亥", "戌"));
            put("戊寅巳", Arrays.asList("巳", "申", "寅"));
            put("戊寅午", Arrays.asList("辰", "巳", "午"));
            put("戊寅未", Arrays.asList("辰", "午", "申"));
            put("戊寅申", Arrays.asList("申", "亥", "寅"));
            put("戊寅酉", Arrays.asList("丑", "午", "酉"));
            put("戊寅戌", Arrays.asList("子", "巳", "戌"));
            put("戊寅亥", Arrays.asList("寅", "申", "寅"));

            put("己丑子", Arrays.asList("巳", "戌", "卯"));
            put("己丑丑", Arrays.asList("亥", "未", "丑"));
            put("己丑寅", Arrays.asList("卯", "戌", "巳"));
            put("己丑卯", Arrays.asList("卯", "亥", "未"));
            put("己丑辰", Arrays.asList("子", "辰", "戌"));
            put("己丑巳", Arrays.asList("亥", "酉", "未"));
            put("己丑午", Arrays.asList("子", "亥", "戌"));
            put("己丑未", Arrays.asList("丑", "戌", "未"));
            put("己丑申", Arrays.asList("寅", "卯", "辰"));
            put("己丑酉", Arrays.asList("卯", "巳", "未"));
            put("己丑戌", Arrays.asList("午", "戌", "辰"));
            put("己丑亥", Arrays.asList("酉", "丑", "巳"));

            put("己亥子", Arrays.asList("巳", "戌", "卯"));
            put("己亥丑", Arrays.asList("巳", "亥", "巳"));
            put("己亥寅", Arrays.asList("午", "丑", "申"));
            put("己亥卯", Arrays.asList("未", "卯", "亥"));
            put("己亥辰", Arrays.asList("巳", "寅", "亥"));
            put("己亥巳", Arrays.asList("卯", "丑", "亥"));
            put("己亥午", Arrays.asList("戌", "酉", "申"));
            put("己亥未", Arrays.asList("亥", "未", "丑"));
            put("己亥申", Arrays.asList("丑", "寅", "卯"));
            put("己亥酉", Arrays.asList("丑", "卯", "巳"));
            put("己亥戌", Arrays.asList("寅", "巳", "申"));
            put("己亥亥", Arrays.asList("亥", "卯", "未"));

            put("己酉子", Arrays.asList("未", "子", "巳"));
            put("己酉丑", Arrays.asList("卯", "酉", "卯"));
            put("己酉寅", Arrays.asList("亥", "午", "丑"));
            put("己酉卯", Arrays.asList("卯", "亥", "未"));
            put("己酉辰", Arrays.asList("午", "卯", "子"));
            put("己酉巳", Arrays.asList("卯", "丑", "亥"));
            put("己酉午", Arrays.asList("戌", "午", "申"));
            put("己酉未", Arrays.asList("酉", "未", "丑"));
            put("己酉申", Arrays.asList("亥", "子", "丑"));
            put("己酉酉", Arrays.asList("丑", "卯", "巳"));
            put("己酉戌", Arrays.asList("卯", "午", "酉"));
            put("己酉亥", Arrays.asList("亥", "卯", "未"));

            put("己未子", Arrays.asList("巳", "戌", "卯"));
            put("己未丑", Arrays.asList("巳", "丑", "丑"));
            put("己未寅", Arrays.asList("酉", "辰", "亥"));
            put("己未卯", Arrays.asList("卯", "亥", "未"));
            put("己未辰", Arrays.asList("亥", "辰", "辰"));
            put("己未巳", Arrays.asList("丑", "巳", "巳"));
            put("己未午", Arrays.asList("卯", "午", "午"));
            put("己未未", Arrays.asList("未", "丑", "戌"));
            put("己未申", Arrays.asList("未", "申", "申"));
            put("己未酉", Arrays.asList("酉", "酉", "酉"));
            put("己未戌", Arrays.asList("亥", "戌", "戌"));
            put("己未亥", Arrays.asList("亥", "卯", "未"));

            put("己巳子", Arrays.asList("巳", "戌", "卯"));
            put("己巳丑", Arrays.asList("巳", "亥", "巳"));
            put("己巳寅", Arrays.asList("酉", "辰", "亥"));
            put("己巳卯", Arrays.asList("卯", "亥", "未"));
            put("己巳辰", Arrays.asList("寅", "亥", "申"));
            put("己巳巳", Arrays.asList("丑", "亥", "酉"));
            put("己巳午", Arrays.asList("卯", "寅", "丑"));
            put("己巳未", Arrays.asList("巳", "申", "寅"));
            put("己巳申", Arrays.asList("申", "申", "午"));
            put("己巳酉", Arrays.asList("亥", "丑", "卯"));
            put("己巳戌", Arrays.asList("申", "亥", "寅"));
            put("己巳亥", Arrays.asList("酉", "丑", "巳"));

            put("己卯子", Arrays.asList("巳", "戌", "卯"));
            put("己卯丑", Arrays.asList("卯", "酉", "卯"));
            put("己卯寅", Arrays.asList("戌", "巳", "子"));
            put("己卯卯", Arrays.asList("未", "卯", "亥"));
            put("己卯辰", Arrays.asList("子", "酉", "午"));
            put("己卯巳", Arrays.asList("亥", "酉", "未"));
            put("己卯午", Arrays.asList("丑", "子", "亥"));
            put("己卯未", Arrays.asList("卯", "子", "午"));
            put("己卯申", Arrays.asList("辰", "巳", "午"));
            put("己卯酉", Arrays.asList("亥", "丑", "卯"));
            put("己卯戌", Arrays.asList("酉", "子", "卯"));
            put("己卯亥", Arrays.asList("亥", "卯", "未"));

            put("庚子子", Arrays.asList("辰", "申", "子"));
            put("庚子丑", Arrays.asList("巳", "戌", "卯"));
            put("庚子寅", Arrays.asList("寅", "申", "寅"));
            put("庚子卯", Arrays.asList("戌", "巳", "子"));
            put("庚子辰", Arrays.asList("子", "申", "辰"));
            put("庚子巳", Arrays.asList("午", "卯", "子"));
            put("庚子午", Arrays.asList("午", "辰", "寅"));
            put("庚子未", Arrays.asList("戌", "酉", "申"));
            put("庚子申", Arrays.asList("申", "寅", "巳"));
            put("庚子酉", Arrays.asList("寅", "卯", "辰"));
            put("庚子戌", Arrays.asList("辰", "午", "申"));
            put("庚子亥", Arrays.asList("午", "酉", "子"));

            put("庚戌子", Arrays.asList("辰", "申", "子"));
            put("庚戌丑", Arrays.asList("申", "丑", "午"));
            put("庚戌寅", Arrays.asList("寅", "申", "寅"));
            put("庚戌卯", Arrays.asList("戌", "巳", "子"));
            put("庚戌辰", Arrays.asList("子", "申", "辰"));
            put("庚戌巳", Arrays.asList("巳", "寅", "亥"));
            put("庚戌午", Arrays.asList("午", "辰", "寅"));
            put("庚戌未", Arrays.asList("午", "巳", "辰"));
            put("庚戌申", Arrays.asList("申", "寅", "巳"));
            put("庚戌酉", Arrays.asList("亥", "子", "丑"));
            put("庚戌戌", Arrays.asList("子", "寅", "辰"));
            put("庚戌亥", Arrays.asList("寅", "巳", "申"));

            put("庚申子", Arrays.asList("辰", "申", "子"));
            put("庚申丑", Arrays.asList("卯", "丑", "丑"));
            put("庚申寅", Arrays.asList("寅", "申", "寅"));
            put("庚申卯", Arrays.asList("戌", "巳", "子"));
            put("庚申辰", Arrays.asList("子", "申", "辰"));
            put("庚申巳", Arrays.asList("巳", "寅", "亥"));
            put("庚申午", Arrays.asList("午", "辰", "寅"));
            put("庚申未", Arrays.asList("酉", "未", "未"));
            put("庚申申", Arrays.asList("申", "寅", "巳"));
            put("庚申酉", Arrays.asList("亥", "酉", "酉"));
            put("庚申戌", Arrays.asList("子", "寅", "辰"));
            put("庚申亥", Arrays.asList("丑", "亥", "亥"));

            put("庚午子", Arrays.asList("辰", "申", "子"));
            put("庚午丑", Arrays.asList("辰", "酉", "寅"));
            put("庚午寅", Arrays.asList("寅", "申", "寅"));
            put("庚午卯", Arrays.asList("戌", "巳", "子"));
            put("庚午辰", Arrays.asList("子", "申", "辰"));
            put("庚午巳", Arrays.asList("巳", "寅", "亥"));
            put("庚午午", Arrays.asList("寅", "子", "戌"));
            put("庚午未", Arrays.asList("午", "巳", "辰"));
            put("庚午申", Arrays.asList("申", "寅", "巳"));
            put("庚午酉", Arrays.asList("戌", "未", "酉"));
            put("庚午戌", Arrays.asList("申", "戌", "子"));
            put("庚午亥", Arrays.asList("酉", "子", "卯"));

            put("庚辰子", Arrays.asList("辰", "申", "子"));
            put("庚辰丑", Arrays.asList("寅", "未", "子"));
            put("庚辰寅", Arrays.asList("寅", "申", "寅"));
            put("庚辰卯", Arrays.asList("午", "丑", "申"));
            put("庚辰辰", Arrays.asList("子", "申", "辰"));
            put("庚辰巳", Arrays.asList("巳", "寅", "亥"));
            put("庚辰午", Arrays.asList("寅", "子", "戌"));
            put("庚辰未", Arrays.asList("卯", "寅", "丑"));
            put("庚辰申", Arrays.asList("申", "寅", "巳"));
            put("庚辰酉", Arrays.asList("午", "未", "申"));
            put("庚辰戌", Arrays.asList("申", "戌", "子"));
            put("庚辰亥", Arrays.asList("寅", "巳", "申"));

            put("庚寅子", Arrays.asList("辰", "申", "子"));
            put("庚寅丑", Arrays.asList("子", "巳", "戌"));
            put("庚寅寅", Arrays.asList("寅", "申", "寅"));
            put("庚寅卯", Arrays.asList("戌", "巳", "子"));
            put("庚寅辰", Arrays.asList("子", "申", "辰"));
            put("庚寅巳", Arrays.asList("巳", "寅", "亥"));
            put("庚寅午", Arrays.asList("午", "辰", "寅"));
            put("庚寅未", Arrays.asList("子", "亥", "戌"));
            put("庚寅申", Arrays.asList("申", "寅", "巳"));
            put("庚寅酉", Arrays.asList("辰", "巳", "午"));
            put("庚寅戌", Arrays.asList("辰", "午", "申"));
            put("庚寅亥", Arrays.asList("申", "亥", "寅"));

            put("辛丑子", Arrays.asList("卯", "巳", "未"));
            put("辛丑丑", Arrays.asList("巳", "丑", "丑"));
            put("辛丑寅", Arrays.asList("酉", "丑", "巳"));
            put("辛丑卯", Arrays.asList("卯", "申", "丑"));
            put("辛丑辰", Arrays.asList("亥", "未", "辰"));
            put("辛丑巳", Arrays.asList("卯", "戌", "巳"));
            put("辛丑午", Arrays.asList("巳", "丑", "酉"));
            put("辛丑未", Arrays.asList("巳", "未", "未"));
            put("辛丑申", Arrays.asList("亥", "酉", "未"));
            put("辛丑酉", Arrays.asList("子", "亥", "戌"));
            put("辛丑戌", Arrays.asList("丑", "戌", "未"));
            put("辛丑亥", Arrays.asList("寅", "卯", "辰"));

            put("辛亥子", Arrays.asList("丑", "卯", "巳"));
            put("辛亥丑", Arrays.asList("巳", "申", "亥"));
            put("辛亥寅", Arrays.asList("未", "亥", "卯"));
            put("辛亥卯", Arrays.asList("卯", "申", "丑"));
            put("辛亥辰", Arrays.asList("巳", "亥", "巳"));
            put("辛亥巳", Arrays.asList("午", "丑", "申"));
            put("辛亥午", Arrays.asList("未", "卯", "亥"));
            put("辛亥未", Arrays.asList("巳", "寅", "亥"));
            put("辛亥申", Arrays.asList("午", "辰", "寅"));
            put("辛亥酉", Arrays.asList("戌", "酉", "申"));
            put("辛亥戌", Arrays.asList("亥", "戌", "未"));
            put("辛亥亥", Arrays.asList("丑", "寅", "卯"));

            put("辛酉子", Arrays.asList("丑", "卯", "巳"));
            put("辛酉丑", Arrays.asList("卯", "午", "酉"));
            put("辛酉寅", Arrays.asList("寅", "午", "戌"));
            put("辛酉卯", Arrays.asList("未", "子", "巳"));
            put("辛酉辰", Arrays.asList("卯", "酉", "卯"));
            put("辛酉巳", Arrays.asList("亥", "午", "丑"));
            put("辛酉午", Arrays.asList("巳", "丑", "酉"));
            put("辛酉未", Arrays.asList("午", "卯", "子"));
            put("辛酉申", Arrays.asList("午", "辰", "寅"));
            put("辛酉酉", Arrays.asList("丑", "酉", "酉"));
            put("辛酉戌", Arrays.asList("酉", "戌", "未"));
            put("辛酉亥", Arrays.asList("亥", "子", "丑"));

            put("辛未子", Arrays.asList("寅", "辰", "午"));
            put("辛未丑", Arrays.asList("亥", "丑", "丑"));
            put("辛未寅", Arrays.asList("亥", "卯", "未"));
            put("辛未卯", Arrays.asList("巳", "戌", "卯"));
            put("辛未辰", Arrays.asList("巳", "丑", "辰"));
            put("辛未巳", Arrays.asList("酉", "辰", "亥"));
            put("辛未午", Arrays.asList("卯", "亥", "未"));
            put("辛未未", Arrays.asList("亥", "未", "未"));
            put("辛未申", Arrays.asList("午", "辰", "寅"));
            put("辛未酉", Arrays.asList("巳", "辰", "卯"));
            put("辛未戌", Arrays.asList("未", "丑", "戌"));
            put("辛未亥", Arrays.asList("申", "亥", "寅"));

            put("辛巳子", Arrays.asList("寅", "辰", "午"));
            put("辛巳丑", Arrays.asList("申", "亥", "寅"));
            put("辛巳寅", Arrays.asList("酉", "丑", "巳"));
            put("辛巳卯", Arrays.asList("卯", "申", "丑"));
            put("辛巳辰", Arrays.asList("巳", "亥", "巳"));
            put("辛巳巳", Arrays.asList("未", "寅", "酉"));
            put("辛巳午", Arrays.asList("午", "寅", "戌"));
            put("辛巳未", Arrays.asList("寅", "亥", "申"));
            put("辛巳申", Arrays.asList("丑", "亥", "酉"));
            put("辛巳酉", Arrays.asList("卯", "寅", "丑"));
            put("辛巳戌", Arrays.asList("巳", "申", "寅"));
            put("辛巳亥", Arrays.asList("午", "未", "申"));

            put("辛卯子", Arrays.asList("巳", "未", "酉"));
            put("辛卯丑", Arrays.asList("酉", "子", "卯"));
            put("辛卯寅", Arrays.asList("亥", "卯", "未"));
            put("辛卯卯", Arrays.asList("卯", "申", "丑"));
            put("辛卯辰", Arrays.asList("卯", "酉", "卯"));
            put("辛卯巳", Arrays.asList("戌", "巳", "子"));
            put("辛卯午", Arrays.asList("未", "卯", "亥"));
            put("辛卯未", Arrays.asList("子", "未", "子"));
            put("辛卯申", Arrays.asList("亥", "酉", "未"));
            put("辛卯酉", Arrays.asList("丑", "子", "亥"));
            put("辛卯戌", Arrays.asList("卯", "子", "午"));
            put("辛卯亥", Arrays.asList("辰", "巳", "午"));

            put("壬子子", Arrays.asList("寅", "卯", "辰"));
            put("壬子丑", Arrays.asList("辰", "午", "申"));
            put("壬子寅", Arrays.asList("午", "酉", "子"));
            put("壬子卯", Arrays.asList("未", "亥", "卯"));
            put("壬子辰", Arrays.asList("巳", "戌", "卯"));
            put("壬子巳", Arrays.asList("午", "子", "午"));
            put("壬子午", Arrays.asList("午", "丑", "申"));
            put("壬子未", Arrays.asList("未", "卯", "亥"));
            put("壬子申", Arrays.asList("午", "卯", "子"));
            put("壬子酉", Arrays.asList("戌", "申", "午"));
            put("壬子戌", Arrays.asList("戌", "酉", "申"));
            put("壬子亥", Arrays.asList("亥", "子", "卯"));

            put("壬戌子", Arrays.asList("亥", "子", "丑"));
            put("壬戌丑", Arrays.asList("子", "寅", "辰"));
            put("壬戌寅", Arrays.asList("辰", "未", "戌"));
            put("壬戌卯", Arrays.asList("未", "亥", "卯"));
            put("壬戌辰", Arrays.asList("辰", "酉", "寅"));
            put("壬戌巳", Arrays.asList("巳", "亥", "巳"));
            put("壬戌午", Arrays.asList("午", "丑", "申"));
            put("壬戌未", Arrays.asList("未", "卯", "亥"));
            put("壬戌申", Arrays.asList("巳", "寅", "亥"));
            put("壬戌酉", Arrays.asList("午", "辰", "寅"));
            put("壬戌戌", Arrays.asList("戌", "酉", "申"));
            put("壬戌亥", Arrays.asList("亥", "戌", "未"));

            put("壬申子", Arrays.asList("丑", "寅", "卯"));
            put("壬申丑", Arrays.asList("子", "寅", "辰"));
            put("壬申寅", Arrays.asList("巳", "申", "亥"));
            put("壬申卯", Arrays.asList("未", "亥", "卯"));
            put("壬申辰", Arrays.asList("辰", "酉", "寅"));
            put("壬申巳", Arrays.asList("寅", "申", "寅"));
            put("壬申午", Arrays.asList("午", "丑", "申"));
            put("壬申未", Arrays.asList("子", "申", "辰"));
            put("壬申申", Arrays.asList("巳", "寅", "亥"));
            put("壬申酉", Arrays.asList("午", "辰", "寅"));
            put("壬申戌", Arrays.asList("戌", "酉", "申"));
            put("壬申亥", Arrays.asList("亥", "申", "寅"));

            put("壬午子", Arrays.asList("丑", "寅", "卯"));
            put("壬午丑", Arrays.asList("申", "戌", "子"));
            put("壬午寅", Arrays.asList("酉", "子", "卯"));
            put("壬午卯", Arrays.asList("未", "亥", "卯"));
            put("壬午辰", Arrays.asList("辰", "酉", "寅"));
            put("壬午巳", Arrays.asList("午", "子", "午"));
            put("壬午午", Arrays.asList("午", "丑", "申"));
            put("壬午未", Arrays.asList("戌", "午", "寅"));
            put("壬午申", Arrays.asList("巳", "寅", "亥"));
            put("壬午酉", Arrays.asList("寅", "子", "戌"));
            put("壬午戌", Arrays.asList("戌", "酉", "申"));
            put("壬午亥", Arrays.asList("亥", "午", "子"));

            put("壬辰子", Arrays.asList("丑", "寅", "卯"));
            put("壬辰丑", Arrays.asList("申", "戌", "子"));
            put("壬辰寅", Arrays.asList("戌", "丑", "辰"));
            put("壬辰卯", Arrays.asList("未", "亥", "卯"));
            put("壬辰辰", Arrays.asList("寅", "未", "子"));
            put("壬辰巳", Arrays.asList("巳", "亥", "巳"));
            put("壬辰午", Arrays.asList("午", "丑", "申"));
            put("壬辰未", Arrays.asList("子", "申", "辰"));
            put("壬辰申", Arrays.asList("巳", "寅", "亥"));
            put("壬辰酉", Arrays.asList("寅", "子", "戌"));
            put("壬辰戌", Arrays.asList("戌", "酉", "申"));
            put("壬辰亥", Arrays.asList("亥", "辰", "戌"));

            put("壬寅子", Arrays.asList("辰", "巳", "午"));
            put("壬寅丑", Arrays.asList("辰", "午", "申"));
            put("壬寅寅", Arrays.asList("申", "亥", "寅"));
            put("壬寅卯", Arrays.asList("未", "亥", "卯"));
            put("壬寅辰", Arrays.asList("子", "巳", "戌"));
            put("壬寅巳", Arrays.asList("寅", "申", "寅"));
            put("壬寅午", Arrays.asList("午", "丑", "申"));
            put("壬寅未", Arrays.asList("戌", "午", "寅"));
            put("壬寅申", Arrays.asList("巳", "寅", "亥"));
            put("壬寅酉", Arrays.asList("戌", "申", "午"));
            put("壬寅戌", Arrays.asList("子", "亥", "戌"));
            put("壬寅亥", Arrays.asList("亥", "寅", "巳"));

            put("癸丑子", Arrays.asList("子", "亥", "戌"));
            put("癸丑丑", Arrays.asList("丑", "戌", "未"));
            put("癸丑寅", Arrays.asList("寅", "卯", "辰"));
            put("癸丑卯", Arrays.asList("卯", "巳", "未"));
            put("癸丑辰", Arrays.asList("辰", "未", "戌"));
            put("癸丑巳", Arrays.asList("酉", "丑", "巳"));
            put("癸丑午", Arrays.asList("午", "亥", "辰"));
            put("癸丑未", Arrays.asList("未", "丑", "未"));
            put("癸丑申", Arrays.asList("卯", "戌", "巳"));
            put("癸丑酉", Arrays.asList("巳", "丑", "酉"));
            put("癸丑戌", Arrays.asList("戌", "未", "辰"));
            put("癸丑亥", Arrays.asList("亥", "酉", "未"));

            put("癸亥子", Arrays.asList("戌", "酉", "申"));
            put("癸亥丑", Arrays.asList("丑", "戌", "未"));
            put("癸亥寅", Arrays.asList("丑", "寅", "卯"));
            put("癸亥卯", Arrays.asList("丑", "卯", "巳"));
            put("癸亥辰", Arrays.asList("辰", "未", "戌"));
            put("癸亥巳", Arrays.asList("酉", "丑", "巳"));
            put("癸亥午", Arrays.asList("午", "亥", "辰"));
            put("癸亥未", Arrays.asList("巳", "亥", "巳"));
            put("癸亥申", Arrays.asList("卯", "戌", "巳"));
            put("癸亥酉", Arrays.asList("未", "卯", "亥"));
            put("癸亥戌", Arrays.asList("巳", "寅", "亥"));
            put("癸亥亥", Arrays.asList("未", "巳", "卯"));

            put("癸酉子", Arrays.asList("未", "午", "巳"));
            put("癸酉丑", Arrays.asList("丑", "戌", "未"));
            put("癸酉寅", Arrays.asList("亥", "子", "丑"));
            put("癸酉卯", Arrays.asList("丑", "卯", "巳"));
            put("癸酉辰", Arrays.asList("辰", "未", "戌"));
            put("癸酉巳", Arrays.asList("酉", "丑", "巳"));
            put("癸酉午", Arrays.asList("未", "子", "巳"));
            put("癸酉未", Arrays.asList("卯", "酉", "卯"));
            put("癸酉申", Arrays.asList("亥", "午", "丑"));
            put("癸酉酉", Arrays.asList("巳", "丑", "酉"));
            put("癸酉戌", Arrays.asList("午", "卯", "子"));
            put("癸酉亥", Arrays.asList("未", "巳", "卯"));

            put("癸未子", Arrays.asList("巳", "辰", "卯"));
            put("癸未丑", Arrays.asList("丑", "戌", "未"));
            put("癸未寅", Arrays.asList("申", "寅", "申"));
            put("癸未卯", Arrays.asList("巳", "未", "酉"));
            put("癸未辰", Arrays.asList("辰", "未", "戌"));
            put("癸未巳", Arrays.asList("酉", "丑", "巳"));
            put("癸未午", Arrays.asList("巳", "戌", "卯"));
            put("癸未未", Arrays.asList("未", "丑", "未"));
            put("癸未申", Arrays.asList("卯", "戌", "巳"));
            put("癸未酉", Arrays.asList("卯", "亥", "未"));
            put("癸未戌", Arrays.asList("戌", "未", "辰"));
            put("癸未亥", Arrays.asList("巳", "卯", "丑"));

            put("癸巳子", Arrays.asList("卯", "寅", "丑"));
            put("癸巳丑", Arrays.asList("丑", "戌", "未"));
            put("癸巳寅", Arrays.asList("未", "申", "酉"));
            put("癸巳卯", Arrays.asList("未", "酉", "亥"));
            put("癸巳辰", Arrays.asList("申", "亥", "寅"));
            put("癸巳巳", Arrays.asList("酉", "丑", "巳"));
            put("癸巳午", Arrays.asList("午", "亥", "辰"));
            put("癸巳未", Arrays.asList("巳", "亥", "巳"));
            put("癸巳申", Arrays.asList("卯", "戌", "巳"));
            put("癸巳酉", Arrays.asList("巳", "丑", "酉"));
            put("癸巳戌", Arrays.asList("戌", "未", "辰"));
            put("癸巳亥", Arrays.asList("丑", "亥", "酉"));

            put("癸卯子", Arrays.asList("丑", "子", "亥"));
            put("癸卯丑", Arrays.asList("丑", "戌", "未"));
            put("癸卯寅", Arrays.asList("辰", "巳", "午"));
            put("癸卯卯", Arrays.asList("未", "酉", "亥"));
            put("癸卯辰", Arrays.asList("酉", "子", "卯"));
            put("癸卯巳", Arrays.asList("酉", "丑", "巳"));
            put("癸卯午", Arrays.asList("午", "亥", "辰"));
            put("癸卯未", Arrays.asList("卯", "酉", "卯"));
            put("癸卯申", Arrays.asList("卯", "戌", "巳"));
            put("癸卯酉", Arrays.asList("未", "亥", "卯"));
            put("癸卯戌", Arrays.asList("戌", "未", "辰"));
            put("癸卯亥", Arrays.asList("亥", "酉", "未"));
        }
    };


}
