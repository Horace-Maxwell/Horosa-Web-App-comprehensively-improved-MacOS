package xuan.core.bazi.maps;

import java.util.*;

/**
 * 八字 - 干支留意常量
 *
 * @author 善待
 */
public class BaZiGanZhiLiuYiMap {

    /**
     * 天干相生（天干+天干为键）
     */
    public static final Map<String, String> TIAN_GAN_XIANG_SHENG = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲丙", "甲丙相生");
            put("甲丁", "甲丁相生");
            put("乙丙", "乙丙相生");
            put("乙丁", "乙丁相生");
            put("丙戊", "丙戊相生");
            put("丙己", "丙己相生");
            put("丁戊", "丁戊相生");
            put("丁己", "丁己相生");
            put("戊庚", "戊庚相生");
            put("戊辛", "戊辛相生");
            put("己庚", "己庚相生");
            put("己辛", "己辛相生");
            put("庚壬", "庚壬相生");
            put("庚癸", "庚癸相生");
            put("辛壬", "辛壬相生");
            put("辛癸", "辛癸相生");
            put("壬甲", "壬甲相生");
            put("壬乙", "壬乙相生");
            put("癸甲", "癸甲相生");
            put("癸乙", "癸乙相生");
        }
    };

    /**
     * 天干相合（天干+天干为键）
     */
    public static final Map<String, String> TIAN_GAN_XIANG_HE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲己", "甲己合化土");
            put("乙庚", "乙庚合化金");
            put("丙辛", "丙辛合化水");
            put("丁壬", "丁壬合化木");
            put("戊癸", "戊癸合化火");
        }
    };

    /**
     * 天干相冲（天干+天干为键）
     */
    public static final Map<String, String> TIAN_GAN_XIANG_CHONG = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲庚", "甲庚相冲");
            put("乙辛", "乙辛相冲");
            put("丙壬", "丙壬相冲");
            put("丁癸", "丁癸相冲");
        }
    };

    /**
     * 天干相克（天干+天干为键）
     */
    public static final Map<String, String> TIAN_GAN_XIANG_KE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("甲戊", "甲戊相克");
            put("乙己", "乙己相克");
            put("丙庚", "丙庚相克");
            put("丁辛", "丁辛相克");
            put("戊壬", "戊壬相克");
            put("己癸", "己癸相克");
            put("庚甲", "庚甲相克");
            put("辛乙", "辛乙相克");
            put("壬丙", "壬丙相克");
            put("癸丁", "癸丁相克");
        }
    };

    /**
     * 地支半合（地支+地支为键）
     */
    public static final Map<String, String> DI_ZHI_BAN_HE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("寅午", "寅午半合火局");
            put("申子", "申子半合水局");
            put("巳酉", "巳酉半合金局");
            put("亥卯", "亥卯半合木局");
            put("子辰", "子辰半合水局");
            put("午戌", "午戌半合火局");
            put("卯未", "卯未半合木局");
            put("酉丑", "酉丑半合金局");
        }
    };

    /**
     * 地支拱合（地支+地支为键）
     */
    public static final Map<String, String> DI_ZHI_GONG_HE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("申辰", "申辰拱合子");
            put("亥未", "亥未拱合卯");
            put("寅戌", "寅戌拱合午");
            put("巳丑", "巳丑拱合酉");
        }
    };

    /**
     * 地支暗合（地支+地支为键）
     */
    public static final Map<String, String> DI_ZHI_AN_HE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("卯申", "卯申暗合");
            put("午亥", "午亥暗合");
            put("丑寅", "丑寅暗合");
            put("寅未", "寅未暗合");
            put("寅午", "寅午暗合");
            put("子戌", "子戌暗合");
            put("子辰", "子辰暗合");
            put("子巳", "子巳暗合");
            put("巳酉", "巳酉暗合");
        }
    };

    /**
     * 地支六合（地支+地支为键）
     */
    public static final Map<String, String> DI_ZHI_LIU_HE = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子丑", "子丑合化土");
            put("寅亥", "寅亥合化木");
            put("卯戌", "卯戌合化火");
            put("辰酉", "辰酉合化金");
            put("巳申", "巳申合化水");
            put("午未", "午未合化火");
        }
    };

    /**
     * 地支相刑（地支+地支为键）
     */
    public static final Map<String, String> DI_ZHI_XIANG_XING = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("寅巳申", "寅巳申三刑");
            put("丑戌未", "丑戌未三刑");
            put("寅巳", "寅巳相刑");
            put("巳申", "巳申相刑");
            put("申寅", "申寅相刑");
            put("丑戌", "丑戌相刑");
            put("戌未", "戌未相刑");
            put("未丑", "未丑相刑");
            put("子卯", "子卯相刑");
            put("酉酉", "酉酉自刑");
            put("亥亥", "亥亥自刑");
            put("午午", "午午自刑");
            put("辰辰", "辰辰自刑");
        }
    };

    /**
     * 地支相冲（地支+地支为键）
     */
    public static final Map<String, String> DI_ZHI_XIANG_CHONG = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子午", "子午相冲");
            put("丑未", "丑未相冲");
            put("寅申", "寅申相冲");
            put("卯酉", "卯酉相冲");
            put("辰戌", "辰戌相冲");
            put("巳亥", "巳亥相冲");
        }
    };

    /**
     * 地支相破（地支+地支为键）
     */
    public static final Map<String, String> DI_ZHI_XIANG_PO = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子酉", "子酉相破");
            put("寅亥", "寅亥相破");
            put("卯午", "卯午相破");
            put("辰丑", "辰丑相破");
            put("巳申", "巳申相破");
            put("戌未", "戌未相破");
        }
    };

    /**
     * 地支相害（地支+地支为键）
     */
    public static final Map<String, String> DI_ZHI_XIANG_HAI = new HashMap<String, String>() {
        private static final long serialVersionUID = -1;

        {
            put("子未", "子未相害");
            put("丑午", "丑午相害");
            put("寅巳", "寅巳相害");
            put("卯辰", "卯辰相害");
            put("申亥", "申亥相害");
            put("酉戌", "酉戌相害");
        }
    };


}
