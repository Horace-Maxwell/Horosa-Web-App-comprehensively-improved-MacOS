package xuan.core.liuyao.maps;

import java.util.*;

/**
 * 六爻 - 神煞常量
 *
 * @author 善待
 */
public class LiuYaoShenShaMap {

    /**
     * 太极贵人（年干\日干+四柱地支为键）
     */
    public static final Map<String, String> TAI_JI_GUI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /*
            一、略解：
                【以年干\日干查四柱地支】甲见'子\午'。乙见'子\午'。丙见'卯\酉'。丁见'卯\酉'。戊见'辰\戌\丑\未'。己见'辰\戌\丑\未'。庚见'寅\亥'。辛见'寅\亥'。壬见'巳\申'。癸见'巳\申'

            二、详解：
                年干\日干是甲，并且四柱地支有子\午
                年干\日干是乙，并且四柱地支有子\午
                年干\日干是丙，并且四柱地支有卯\酉
                年干\日干是丁，并且四柱地支有卯\酉
                年干\日干是戊，并且四柱地支有辰\戌\丑\未
                年干\日干是己，并且四柱地支有辰\戌\丑\未
                年干\日干是庚，并且四柱地支有寅\亥
                年干\日干是辛，并且四柱地支有寅\亥
                年干\日干是壬，并且四柱地支有巳\申
                年干\日干是癸，并且四柱地支有巳\申
         */

        {
            put("甲子", "子");
            put("甲午", "午");
            put("乙子", "子");
            put("乙午", "午");
            put("丙卯", "卯");
            put("丙酉", "酉");
            put("丁卯", "卯");
            put("丁酉", "酉");
            put("戊辰", "辰");
            put("戊戌", "戌");
            put("戊丑", "丑");
            put("戊未", "未");
            put("己辰", "辰");
            put("己戌", "戌");
            put("己丑", "丑");
            put("己未", "未");
            put("庚寅", "寅");
            put("庚亥", "亥");
            put("辛寅", "寅");
            put("辛亥", "亥");
            put("壬巳", "巳");
            put("壬申", "申");
            put("癸巳", "巳");
            put("癸申", "申");
        }
    };

    /**
     * 天乙贵人（日干为键）
     */
    public static final Map<String, String> TIAN_YI_GUI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日干查→ 甲在'丑未'。乙在'申子'。丙在'酉亥'。丁在'酉亥'。戊在'丑未'。己在'申子'。庚在'寅午'。辛在'寅午'。壬在'卯巳'。癸在'卯巳' */

        {
            put("甲", "丑未");
            put("乙", "申子");
            put("丙", "酉亥");
            put("丁", "酉亥");
            put("戊", "丑未");
            put("己", "申子");
            put("庚", "寅午");
            put("辛", "寅午");
            put("壬", "卯巳");
            put("癸", "卯巳");
        }
    };

    /**
     * 福星贵人（日干+四柱地支为键）
     */
    public static final Map<String, String> FU_XING_GUI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /*
            一、略解：
                【以日干查四柱地支】甲见'寅'。乙见'丑\卯'。丙见'寅'。丁见'亥'。戊见'申'。己见'未'。庚见'午'。辛见'巳'。壬见'辰'。癸见'丑\卯'

            二、详解：
                日干是甲，并且四柱地支有寅
                日干是乙，并且四柱地支有丑\卯
                日干是丙，并且四柱地支有寅
                日干是丁，并且四柱地支有亥
                日干是戊，并且四柱地支有申
                日干是己，并且四柱地支有未
                日干是庚，并且四柱地支有午
                日干是辛，并且四柱地支有巳
                日干是壬，并且四柱地支有辰
                日干是癸，并且四柱地支有丑\卯
         */

        {
            put("甲寅", "寅");
            put("乙丑", "丑");
            put("乙卯", "卯");
            put("丙寅", "寅");
            put("丁亥", "亥");
            put("戊申", "申");
            put("己未", "未");
            put("庚午", "午");
            put("辛巳", "巳");
            put("壬辰", "辰");
            put("癸丑", "丑");
            put("癸卯", "卯");
        }
    };

    /**
     * 文昌贵人（日干为键）
     */
    public static final Map<String, String> WEN_CHANG_GUI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日干查→ 甲在'巳'。乙在'午'。丙在'申'。丁在'酉'。戊在'申'。己在'酉'。庚在'亥'。辛在'子'。壬在'寅'。癸在'卯' */

        {
            put("甲", "巳");
            put("乙", "午");
            put("丙", "申");
            put("丁", "酉");
            put("戊", "申");
            put("己", "酉");
            put("庚", "亥");
            put("辛", "子");
            put("壬", "寅");
            put("癸", "卯");
        }
    };

    /**
     * 天厨贵人（日干为键）
     */
    public static final Map<String, String> TIAN_CHU_GUI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日干查→ 甲在'巳'。乙在'午'。丙在'子'。丁在'巳'。戊在'午'。己在'申'。庚在'寅'。辛在'午'。壬在'酉'。癸在'亥' */

        {
            put("甲", "巳");
            put("乙", "午");
            put("丙", "子");
            put("丁", "巳");
            put("戊", "午");
            put("己", "申");
            put("庚", "寅");
            put("辛", "午");
            put("壬", "酉");
            put("癸", "亥");
        }
    };

    /**
     * 月德贵人（月支为键）
     */
    public static final Map<String, String> YUE_DE_GUI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以月支查→ 子在'庚'。丑在'庚'。寅在'丙'。卯在'甲'。辰在'庚'。巳在'庚'。午在'丙'。未在'甲'。申在'庚'。酉在'庚'。戌在'丙'。亥在'甲' */

        {
            put("子", "庚");
            put("丑", "庚");
            put("寅", "丙");
            put("卯", "甲");
            put("辰", "庚");
            put("巳", "庚");
            put("午", "丙");
            put("未", "甲");
            put("申", "庚");
            put("酉", "庚");
            put("戌", "丙");
            put("亥", "甲");
        }
    };

    /**
     * 天德贵人（月支为键）
     */
    public static final Map<String, String> TIAN_DE_GUI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以月支查→ 子在'巽巳'。丑在'庚申'。寅在'丁未'。卯在'坤申'。辰在'壬亥'。巳在'辛戌'。午在'乾亥'。未在'甲寅'。申在'癸丑'。酉在'寅'。戌在'丙巳'。亥在'乙辰' */

        {
            put("子", "巽巳");
            put("丑", "庚申");
            put("寅", "丁未");
            put("卯", "坤申");
            put("辰", "庚亥");
            put("巳", "辛戌");
            put("午", "乾亥");
            put("未", "甲寅");
            put("申", "癸丑");
            put("酉", "寅");
            put("戌", "丙巳");
            put("亥", "乙辰");
        }
    };

    /**
     * 唐符国印（年支为键）
     */
    public static final Map<String, String> TANG_FU_GUO_YIN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以年支查→ 子在'卯酉'。丑在'辰戌'。寅在'巳亥'。卯在'子午'。辰在'丑未'。巳在'寅申'。午在'卯酉'。未在'辰戌'。申在'巳亥'。酉在'子午'。戌在'丑未'。亥在'寅申' */

        {
            put("子", "卯酉");
            put("丑", "辰戌");
            put("寅", "巳亥");
            put("卯", "子午");
            put("辰", "丑未");
            put("巳", "寅申");
            put("午", "卯酉");
            put("未", "辰戌");
            put("申", "巳亥");
            put("酉", "子午");
            put("戌", "丑未");
            put("亥", "寅申");
        }
    };

    /**
     * 天元禄（日干为键）
     */
    public static final Map<String, String> TIAN_YUAN_LU = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日干查→ 甲在'寅'。乙在'卯'。丙在'巳'。丁在'午'。戊在'巳'。己在'午'。庚在'申'。辛在'酉'。壬在'亥'。癸在'子' */

        {
            put("甲", "寅");
            put("乙", "卯");
            put("丙", "巳");
            put("丁", "午");
            put("戊", "巳");
            put("己", "午");
            put("庚", "申");
            put("辛", "酉");
            put("壬", "亥");
            put("癸", "子");
        }
    };

    /**
     * 华盖（年支\日支+其余地支为键）
     */
    public static final Map<String, String> HUA_GAI = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /*
            一、略解：
                【以年支\日支查其余地支】子见'辰'。丑见'丑'。寅见'戌'。卯见'未'。辰见'辰'。巳见'丑'。午见'戌'。未见'未'。申见'辰'。酉见'丑'。戌见'戌'。亥见'未'

            二、详解：
                年支\日支是子，并且其余地支有辰
                年支\日支是丑，并且其余地支有丑
                年支\日支是寅，并且其余地支有戌
                年支\日支是卯，并且其余地支有未
                年支\日支是辰，并且其余地支有辰
                年支\日支是巳，并且其余地支有丑
                年支\日支是午，并且其余地支有戌
                年支\日支是未，并且其余地支有未
                年支\日支是申，并且其余地支有辰
                年支\日支是酉，并且其余地支有丑
                年支\日支是戌，并且其余地支有戌
                年支\日支是亥，并且其余地支有未
         */

        {
            put("子辰", "辰");
            put("丑丑", "丑");
            put("寅戌", "戌");
            put("卯未", "未");
            put("辰辰", "辰");
            put("巳丑", "丑");
            put("午戌", "戌");
            put("未未", "未");
            put("申辰", "辰");
            put("酉丑", "丑");
            put("戌戌", "戌");
            put("亥未", "未");
        }
    };

    /**
     * 驿马（日支为键）
     */
    public static final Map<String, String> YI_MA = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日支查→ 子在'寅'。丑在'亥'。寅在'申'。卯在'巳'。辰在'寅'。巳在'亥'。午在'申'。未在'巳'。申在'寅'。酉在'亥'。戌在'申'。亥在'巳' */

        {
            put("子", "寅");
            put("丑", "亥");
            put("寅", "申");
            put("卯", "巳");
            put("辰", "寅");
            put("巳", "亥");
            put("午", "申");
            put("未", "巳");
            put("申", "寅");
            put("酉", "亥");
            put("戌", "申");
            put("亥", "巳");
        }
    };

    /**
     * 天马（月支为键）
     */
    public static final Map<String, String> TIAN_MA = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日支查→ 子在'寅'。丑在'辰'。寅在'午'。卯在'申'。辰在'戌'。巳在'子'。午在'寅'。未在'辰'。申在'午'。酉在'申'。戌在'戌'。亥在'子' */

        {
            put("子", "寅");
            put("丑", "辰");
            put("寅", "午");
            put("卯", "申");
            put("辰", "戌");
            put("巳", "子");
            put("午", "寅");
            put("未", "辰");
            put("申", "午");
            put("酉", "申");
            put("戌", "戌");
            put("亥", "子");
        }
    };

    /**
     * 禄马（日干为键）
     */
    public static final Map<String, String> LU_MA = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日干查→ 甲在'寅'。乙在'卯'。丙在'巳'。丁在'午'。戊在'巳'。己在'午'。庚在'申'。辛在'酉'。壬在'亥'。癸在'子' */

        {
            put("甲", "寅");
            put("乙", "卯");
            put("丙", "巳");
            put("丁", "午");
            put("戊", "巳");
            put("己", "午");
            put("庚", "申");
            put("辛", "酉");
            put("壬", "亥");
            put("癸", "子");
        }
    };

    /**
     * 劫煞（日支为键）
     */
    public static final Map<String, String> JIE_SHA = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日支查→ 子在'巳'。丑在'寅'。寅在'亥'。卯在'申'。辰在'巳'。巳在'寅'。午在'亥'。未在'申'。申在'巳'。酉在'寅'。戌在'亥'。亥在'申' */

        {
            put("子", "巳");
            put("丑", "寅");
            put("寅", "亥");
            put("卯", "申");
            put("辰", "巳");
            put("巳", "寅");
            put("午", "亥");
            put("未", "申");
            put("申", "巳");
            put("酉", "寅");
            put("戌", "亥");
            put("亥", "申");
        }

    };

    /**
     * 将星（年支\日支+其余地支为键）
     */
    public static final Map<String, String> JIANG_XING = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /*
            一、略解：
                【以年支\日支查其余地支】子见'子'。丑见'酉'。寅见'午'。卯见'卯'。辰见'子'。巳见'酉'。午见'午'。未见'卯'。申见'子'。酉见'酉'。戌见'午'。亥见'卯'

            二、详解：
                年支\日支是子，并且其余地支有子
                年支\日支是丑，并且其余地支有酉
                年支\日支是寅，并且其余地支有午
                年支\日支是卯，并且其余地支有卯
                年支\日支是辰，并且其余地支有子
                年支\日支是巳，并且其余地支有酉
                年支\日支是午，并且其余地支有午
                年支\日支是未，并且其余地支有卯
                年支\日支是申，并且其余地支有子
                年支\日支是酉，并且其余地支有酉
                年支\日支是戌，并且其余地支有午
                年支\日支是亥，并且其余地支有卯
         */

        {
            put("子子", "子");
            put("丑酉", "酉");
            put("寅午", "午");
            put("卯卯", "卯");
            put("辰子", "子");
            put("巳酉", "酉");
            put("午午", "午");
            put("未卯", "卯");
            put("申子", "子");
            put("酉酉", "酉");
            put("戌午", "午");
            put("亥卯", "卯");
        }
    };

    /**
     * 咸池（日支为键）
     */
    public static final Map<String, String> XIAN_CHI = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日支查→ 子在'酉'。丑在'午'。寅在'卯'。卯在'子'。辰在'酉'。巳在'午'。午在'卯'。未在'子'。申在'酉'。酉在'午'。戌在'卯'。亥在'子' */

        {
            put("子", "酉");
            put("丑", "午");
            put("寅", "卯");
            put("卯", "子");
            put("辰", "酉");
            put("巳", "午");
            put("午", "卯");
            put("未", "子");
            put("申", "酉");
            put("酉", "午");
            put("戌", "卯");
            put("亥", "子");
        }
    };

    /**
     * 天喜（月支为键）
     */
    public static final Map<String, String> TIAN_XI = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以月支查→ 子在'未'。丑在'未'。寅在'戌'。卯在'戌'。辰在'戌'。巳在'丑'。午在'丑'。未在'丑'。申在'辰'。酉在'辰'。戌在'辰'。亥在'未' */

        {
            put("子", "未");
            put("丑", "未");
            put("寅", "戌");
            put("卯", "戌");
            put("辰", "戌");
            put("巳", "丑");
            put("午", "丑");
            put("未", "丑");
            put("申", "辰");
            put("酉", "辰");
            put("戌", "辰");
            put("亥", "未");
        }
    };

    /**
     * 灾煞（日支为键）
     */
    public static final Map<String, String> ZAI_SHA = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日支查→ 子在'午'。丑在'卯'。寅在'子'。卯在'酉'。辰在'午'。巳在'卯'。午在'子'。未在'酉'。申在'午'。酉在'卯'。戌在'子'。亥在'酉' */

        {
            put("子", "午");
            put("丑", "卯");
            put("寅", "子");
            put("卯", "酉");
            put("辰", "午");
            put("巳", "卯");
            put("午", "子");
            put("未", "酉");
            put("申", "午");
            put("酉", "卯");
            put("戌", "子");
            put("亥", "酉");
        }
    };

    /**
     * 天医（月支为键）
     */
    public static final Map<String, String> TIAN_YI = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以月支查→ 子在'亥'。丑在'子'。寅在'丑'。卯在'寅'。辰在'卯'。巳在'辰'。午在'巳'。未在'午'。申在'未'。酉在'申'。戌在'酉'。亥在'戌' */

        {
            put("子", "亥");
            put("丑", "子");
            put("寅", "丑");
            put("卯", "寅");
            put("辰", "卯");
            put("巳", "辰");
            put("午", "巳");
            put("未", "午");
            put("申", "未");
            put("酉", "申");
            put("戌", "酉");
            put("亥", "戌");
        }
    };

    /**
     * 谋星（日支为键）
     */
    public static final Map<String, String> MOU_XING = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日支查→ 子在'戌'。丑在'未'。寅在'辰'。卯在'丑'。辰在'戌'。巳在'未'。午在'辰'。未在'丑'。申在'戌'。酉在'未'。戌在'辰'。亥在'丑' */

        {
            put("子", "戌");
            put("丑", "未");
            put("寅", "辰");
            put("卯", "丑");
            put("辰", "戌");
            put("巳", "未");
            put("午", "辰");
            put("未", "丑");
            put("申", "戌");
            put("酉", "未");
            put("戌", "辰");
            put("亥", "丑");
        }
    };

    /**
     * 皇恩（月支为键）
     */
    public static final Map<String, String> HUANG_EN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以月支查→ 子在'卯'。丑在'巳'。寅在'未'。卯在'酉'。辰在'亥'。巳在'丑'。午在'卯'。未在'巳'。申在'未'。酉在'酉'。戌在'亥'。亥在'丑' */

        {
            put("子", "卯");
            put("丑", "巳");
            put("寅", "未");
            put("卯", "酉");
            put("辰", "亥");
            put("巳", "丑");
            put("午", "卯");
            put("未", "巳");
            put("申", "未");
            put("酉", "酉");
            put("戌", "亥");
            put("亥", "丑");
        }
    };

    /**
     * 阳刃（日干为键）
     */
    public static final Map<String, String> TIAN_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日干查→ 甲在'卯'。乙在'辰'。丙在'午'。丁在'巳'。戊在'午'。己在'巳'。庚在'酉'。辛在'申'。壬在'子'。癸在'亥' */

        {
            put("甲", "卯");
            put("乙", "辰");
            put("丙", "午");
            put("丁", "巳");
            put("戊", "午");
            put("己", "巳");
            put("庚", "酉");
            put("辛", "申");
            put("壬", "子");
            put("癸", "亥");
        }
    };

    /**
     * 飞刃（日干为键）
     */
    public static final Map<String, String> FEI_REN = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;
        /* 以日干查→ 甲在'酉'。乙在'戌'。丙在'子'。丁在'亥'。戊在'子'。己在'亥'。庚在'卯'。辛在'寅'。壬在'午'。癸在'巳' */

        {
            put("甲", "酉");
            put("乙", "戌");
            put("丙", "子");
            put("丁", "亥");
            put("戊", "子");
            put("己", "亥");
            put("庚", "卯");
            put("辛", "寅");
            put("壬", "午");
            put("癸", "巳");
        }
    };


}
