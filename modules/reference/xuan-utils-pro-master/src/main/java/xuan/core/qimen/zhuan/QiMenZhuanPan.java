package xuan.core.qimen.zhuan;

import java.time.LocalDate;
import java.time.Period;
import java.time.ZoneId;
import java.util.*;

import com.nlf.calendar.JieQi;
import xuan.utils.DateUtil;
import xuan.utils.CommonUtil;
import com.nlf.calendar.Lunar;
import com.nlf.calendar.Solar;
import xuan.core.qimen.zhuan.maps.QiMenZhuanPanJiChuMap;
import xuan.core.qimen.zhuan.utils.QiMenZhuanPanJiChuUtil;
import xuan.core.qimen.zhuan.settings.QiMenZhuanPanJiChuSetting;

/**
 * 转盘奇门
 *
 * @author 善待
 */
public class QiMenZhuanPan {

    /**
     * 转盘奇门 - 基础设置
     */
    private QiMenZhuanPanJiChuSetting qiMenZhuanPanJiChuSetting;

    /**
     * 公历日期（Solar型，如：2024-01-01）
     */
    private Solar solar;
    /**
     * 农历日期（Lunar型，如：二〇二三年冬月二十）
     */
    private Lunar lunar;
    /**
     * 公历日期（String型，如：2024-01-01 00:00:00）
     */
    private String solarStr;
    /**
     * 农历日期（String型，如：2023-11-20 00:00:00）
     */
    private String lunarStr;
    /**
     * 公历日期（String型，如：2024年01月01日00时00分00秒）
     */
    private String solarStr2;
    /**
     * 农历日期（String型，如：二〇二三年冬月二十(早)子时）
     */
    private String lunarStr2;
    /**
     * 公历日期（Date型，如：Mon Jan 01 00:00:00 CST 2024）
     */
    private Date solarDate;
    /**
     * 农历日期（Date型，如：Mon Nov 20 00:00:00 CST 2023）
     */
    private Date lunarDate;

    /**
     * 年干
     */
    private String yearGan;
    /**
     * 月干
     */
    private String monthGan;
    /**
     * 日干
     */
    private String dayGan;
    /**
     * 时干
     */
    private String hourGan;

    /**
     * 年支
     */
    private String yearZhi;
    /**
     * 月支
     */
    private String monthZhi;
    /**
     * 日支
     */
    private String dayZhi;
    /**
     * 时支
     */
    private String hourZhi;

    /**
     * 年干支
     */
    private String yearGanZhi;
    /**
     * 月干支
     */
    private String monthGanZhi;
    /**
     * 日干支
     */
    private String dayGanZhi;
    /**
     * 时干支
     */
    private String hourGanZhi;

    /**
     * 符头
     */
    private String fuTou;
    /**
     * 节气
     */
    private String jieQi;
    /**
     * 三元
     */
    private String sanYuan;
    /**
     * 阴阳遁
     */
    private String yinYangDun;
    /**
     * 局数
     */
    private int juShu;
    /**
     * 旬首
     */
    private String xunShou;
    /**
     * 旬首仪仗
     */
    private String xunShouYiZhang;
    /**
     * 旬首宫位
     */
    private int xunShouGongWei;
    /**
     * 地盘中的奇仪（1~9宫）
     */
    private List<String> diQiYi;
    /**
     * 地盘中的六甲（1~9宫）
     */
    private List<String> diLiuJia;
    /**
     * 值符
     */
    private String zhiFu;
    /**
     * 值使
     */
    private String zhiShi;

    /**
     * 值符旋转前宫位
     */
    private int oldZhiFuGongWei;
    /**
     * 值符旋转后宫位
     */
    private int newZhiFuGongWei;

    /**
     * 值使旋转前宫位
     */
    private int oldZhiShiGongWei;
    /**
     * 值使旋转后宫位
     */
    private int newZhiShiGongWei;

    /**
     * 地盘（1~9宫）
     */
    private List<String> diPan;
    /**
     * 天盘（1~9宫）
     */
    private List<String> tianPan;
    /**
     * 人盘（1~9宫）
     */
    private List<String> renPan;
    /**
     * 神盘（1~9宫）
     */
    private List<String> shenPan;

    /**
     * 天盘旋转后九星携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
     */
    private List<String> tianPanQiYiTianQinYes;
    /**
     * 天盘旋转后九星携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
     */
    private List<String> tianPanQiYiTianQinNo;

    /**
     * 上一节
     */
    private JieQi prevJie;
    /**
     * 下一节
     */
    private JieQi nextJie;
    /**
     * 上一气
     */
    private JieQi prevQi;
    /**
     * 下一气
     */
    private JieQi nextQi;

//*******************************************************************************************************************************

    /**
     * 使用基础设置初始化
     *
     * @param qiMenZhuanPanJiChuSetting 转盘奇门 - 基础设置
     */
    public QiMenZhuanPan(QiMenZhuanPanJiChuSetting qiMenZhuanPanJiChuSetting) {

        this.qiMenZhuanPanJiChuSetting = qiMenZhuanPanJiChuSetting; // 基础设置

        // 1、获取基础设置
        String date = qiMenZhuanPanJiChuSetting.getDate(); // 日期
        int dateType = qiMenZhuanPanJiChuSetting.getDateType(); // 日期类型
        int leapMonthType = qiMenZhuanPanJiChuSetting.getLeapMonthType(); // 闰月类型
        int yearGanZhiType = qiMenZhuanPanJiChuSetting.getYearGanZhiType(); // 年干支类型
        int monthGanZhiType = qiMenZhuanPanJiChuSetting.getMonthGanZhiType(); // 月干支类型
        int dayGanZhiType = qiMenZhuanPanJiChuSetting.getDayGanZhiType(); // 日干支类型

        // 2、获取日期及四柱干支
        Map<String, Object> dateAndGanZhi = CommonUtil.getDateAndGanZhi(date, dateType, leapMonthType, yearGanZhiType, monthGanZhiType, dayGanZhiType);
        this.solar = (Solar) dateAndGanZhi.get("solar"); // 公历日期（Solar型，如：2024-01-01）
        this.lunar = (Lunar) dateAndGanZhi.get("lunar"); // 农历日期（Lunar型，如：二〇二三年冬月二十）
        this.solarStr = (String) dateAndGanZhi.get("solarStr"); // 公历日期（String型，如：2024-01-01 00:00:00）
        this.lunarStr = (String) dateAndGanZhi.get("lunarStr"); // 农历日期（String型，如：2023-11-20 00:00:00）
        this.solarStr2 = (String) dateAndGanZhi.get("solarStr2"); // 公历日期（String型，如：2024年01月01日00时00分00秒）
        this.lunarStr2 = (String) dateAndGanZhi.get("lunarStr2"); // 农历日期（String型，如：二〇二三年冬月二十(早)子时）
        this.solarDate = (Date) dateAndGanZhi.get("solarDate"); // 公历日期（Date型，如：Mon Jan 01 00:00:00 CST 2024）
        this.lunarDate = (Date) dateAndGanZhi.get("lunarDate"); // 农历日期（Date型，如：Mon Nov 20 00:00:00 CST 2023）
        this.yearGanZhi = (String) dateAndGanZhi.get("yearGanZhi"); // 年干支
        this.monthGanZhi = (String) dateAndGanZhi.get("monthGanZhi"); // 月干支
        this.dayGanZhi = (String) dateAndGanZhi.get("dayGanZhi"); // 日干支
        this.hourGanZhi = (String) dateAndGanZhi.get("hourGanZhi"); // 时干支
        this.yearGan = this.yearGanZhi.substring(0, 1); // 年干
        this.monthGan = this.monthGanZhi.substring(0, 1); // 月干
        this.dayGan = this.dayGanZhi.substring(0, 1); // 日干
        this.hourGan = this.hourGanZhi.substring(0, 1); // 时干
        this.yearZhi = this.yearGanZhi.substring(1, 2); // 年支
        this.monthZhi = this.monthGanZhi.substring(1, 2); // 月支
        this.dayZhi = this.dayGanZhi.substring(1, 2); // 日支
        this.hourZhi = this.hourGanZhi.substring(1, 2); // 时支

        // 3、初始化必要数据
        initializeShangXiaJieQi(); // 初始化上下节气
        initializeFuTouAndJieQi(); // 初始化符头、节气
        initializeSanYuanAndJuShu(); // 初始化三元、局数
        initializeYinYangDun(); // 初始化阴阳遁
        initializeXunShou(); // 初始化旬首
        initializeDiQiYiLiuJiaFuShi(); // 初始化地盘奇仪、地盘六甲、值符、值使
        initializeDiPan(); // 初始化地盘
        initializeTianPan(); // 初始化天盘
        initializeRenPan(); // 初始化人盘
        initializeShenPan(); // 初始化神盘

    }

    /**
     * 初始化上下节气
     */
    private void initializeShangXiaJieQi() {

        int jieQiType = this.qiMenZhuanPanJiChuSetting.getJieQiType();

        this.prevJie = this.lunar.getPrevJie(jieQiType == 0); // 上一节
        this.nextJie = this.lunar.getNextJie(jieQiType == 0); // 下一节
        this.prevQi = this.lunar.getPrevQi(jieQiType == 0); // 上一气
        this.nextQi = this.lunar.getNextQi(jieQiType == 0); // 下一气

    }

    /**
     * 初始化符头、节气
     */
    private void initializeFuTouAndJieQi() {

        // 1、年家奇门、月家奇门
        if (this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 0 || this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 1) {
            this.fuTou = QiMenZhuanPanJiChuMap.RI_ZHU_FU_TOU.get(this.dayGanZhi); // 符头
            this.jieQi = getLunar().getPrevJieQi(this.qiMenZhuanPanJiChuSetting.getJieQiType() == 0).getName(); // 获取上一个节气
            return;
        }

        // 2、日家奇门、时家奇门
        if (this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 2 || this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 3) {
            /*
                情况一：当天日干支是符头、当天是节气，则保存符头和节气。
                情况二：当天日干支是符头、但当天不是节气，需保存符头并向前查找节气。
                情况三：当天日干支不是符头、当天是节气，需保存节气并向前查找符头。
                情况四：当天日干支不是符头、当天不是节气，需要按天向前查找符头和节气。
                   1、情况四之一：既碰到符头又碰到节气，则保存符头和节气；
                   2、情况四之二：若先碰到符头但未碰到节气，需保存符头并向前查找节气；
                   3、情况四之三：若先碰到节气但未碰到符头，需保存节气并向前查找符头；
            */
            String dayGanZhi = this.dayGanZhi; // 日干支
            String[] sanYuanFuTou = QiMenZhuanPanJiChuMap.SAN_YUAN_FU_TOU; // 三元符头
            for (int i = 0; i < sanYuanFuTou.length; i++) {
                // 情况一：当天日干支是符头、当天是节气，则保存符头和节气（▲例：农历二〇二二年八月廿八）
                if (dayGanZhi.equals(sanYuanFuTou[i]) && !"".equals(this.lunar.getJieQi())) {
                    this.fuTou = dayGanZhi; // 符头
                    this.jieQi = this.lunar.getJieQi(); // 节气
                    return;
                }
                // 情况二：当天日干支是符头、但当天不是节气，需保存符头并向前查找节气（▲例：农历二〇二二年八月十八）
                if (dayGanZhi.equals(sanYuanFuTou[i]) && "".equals(this.lunar.getJieQi())) {
                    this.fuTou = dayGanZhi; // 符头
                    this.jieQi = this.lunar.getPrevJieQi(this.qiMenZhuanPanJiChuSetting.getJieQiType() == 0).getName(); // 获取上一个节气
                    return;
                }
                // 情况三：当天日干支不是符头、当天是节气，需保存节气并向前查找符头（▲例：农历二〇二二年八月十二）
                if (!dayGanZhi.equals(sanYuanFuTou[i]) && !"".equals(this.lunar.getJieQi())) {
                    String jieQi = this.lunar.getPrevJieQi(this.qiMenZhuanPanJiChuSetting.getJieQiType() == 0).getName(); // 当天节气
                    // 获取向前第i天的日干支
                    dayGanZhi = (this.qiMenZhuanPanJiChuSetting.getDayGanZhiType() == 1) ? this.lunar.next(-i).getDayInGanZhiExact() : this.lunar.next(-i).getDayInGanZhiExact2();
                    // 若向前第i天的日柱为符头则记录符头
                    for (String key : sanYuanFuTou) {
                        if (dayGanZhi.equals(key)) {
                            this.fuTou = dayGanZhi; // 符头
                            this.jieQi = jieQi; // 节气
                            return;
                        }
                    }
                }
                // 情况四：当天日干支不是符头、当天不是节气，需要按天向前查找符头和节气
                if (!dayGanZhi.equals(sanYuanFuTou[i]) && "".equals(this.lunar.getJieQi())) {
                    // 获取向前第i天的日干支
                    dayGanZhi = (this.qiMenZhuanPanJiChuSetting.getDayGanZhiType() == 1) ? this.lunar.next(-i).getDayInGanZhiExact() : this.lunar.next(-i).getDayInGanZhiExact2();
                    String jieQi = this.lunar.next(-i).getJieQi(); // 获取向前第i天的节气
                    // 情况四之一：既碰到符头又碰到节气，则保存符头和节气（▲例：农历二〇二二年八月廿九）
                    for (String key : sanYuanFuTou) {
                        if (dayGanZhi.equals(key) && !"".equals(jieQi)) {
                            this.fuTou = dayGanZhi; // 符头
                            this.jieQi = jieQi; // 节气
                            return;
                        }
                    }
                    // 情况四之二：若先碰到符头但未碰到节气，需保存符头并向前查找节气（▲例：农历二〇二二年八月十四）
                    for (String key : sanYuanFuTou) {
                        if (dayGanZhi.equals(key) && "".equals(jieQi)) {
                            this.fuTou = dayGanZhi; // 符头
                            this.jieQi = this.lunar.getPrevJieQi(this.qiMenZhuanPanJiChuSetting.getJieQiType() == 0).getName(); // 节气
                            return;
                        }
                    }
                    // 4情况四之三：若先碰到节气但未碰到符头，需保存节气并向前查找符头（▲例：农历二〇二〇年八月廿八）
                    for (int j = 0; j < sanYuanFuTou.length; j++) {
                        if (!"".equals(jieQi) && !dayGanZhi.equals(sanYuanFuTou[i])) {
                            // 获取向前第i天的日干支
                            dayGanZhi = (this.qiMenZhuanPanJiChuSetting.getDayGanZhiType() == 1) ? this.lunar.next(-i).getDayInGanZhiExact() : this.lunar.next(-i).getDayInGanZhiExact2();
                            // 若向前第i天的日柱为符头则记录符头
                            for (String key : sanYuanFuTou) {
                                if (dayGanZhi.equals(key)) {
                                    this.fuTou = dayGanZhi; // 符头
                                    this.jieQi = jieQi; // 节气
                                    return;
                                }
                            }
                        }
                    }
                }
            }
        }

    }

    /**
     * 初始化三元、局数
     */
    private void initializeSanYuanAndJuShu() {

        // 1、年家奇门
        if (this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 0) {
            Map<Integer, List<Object>> sanYuanDateRangeMap = QiMenZhuanPanJiChuMap.SAN_YUAN_DATE_RANGE; // 公历0~9999年两个日期范围内的三元、局数（年家奇门）
            // 遍历数据并计算局数（即：[甲子戊]所落入的宫位）
            for (int i = 0; i < sanYuanDateRangeMap.size(); i++) {
                List<Object> list = sanYuanDateRangeMap.get(i);
                int startDate = Integer.parseInt(list.get(0).toString()); // 开始日期
                int endDate = Integer.parseInt(list.get(1).toString()); // 结束日期
                if (this.solar.getYear() >= startDate && this.solar.getYear() <= endDate) {
                    this.sanYuan = list.get(2).toString(); // 三元
                    this.juShu = Integer.parseInt(list.get(3).toString()); // 局数
                    break;
                }
            }
            return;
        }

        // 2、月家奇门
        if (this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 1) {
            // 2.1、判断起局方式（0:使用年支起局。1:使用年干支的符头地支起局）
            String diZhi; // 地支
            if (this.qiMenZhuanPanJiChuSetting.getYueJiaQiJuType() == 0) {
                // 使用年支起局
                diZhi = this.yearZhi; // 年支
            } else {
                // 使用年干支的符头地支起局
                diZhi = QiMenZhuanPanJiChuMap.SIX_JIA_ZI_XUN_SHOU_AND_YI_ZHANG.get(this.yearGanZhi).get(0).substring(1, 2); // 年干支的符头地支
            }
            // 2.2、年支或年干符头的地支为[寅、申、巳、亥]时，使用上元，即：阴遁一局
            if ("寅".equals(diZhi) || "申".equals(diZhi) || "巳".equals(diZhi) || "亥".equals(diZhi)) {
                this.sanYuan = "上元"; // 三元
                this.juShu = 1; // 局数
            }
            // 2.3、年支或年干符头的地支为[子、午、卯、酉]时，使用中元，即：阴遁七局
            if ("子".equals(diZhi) || "午".equals(diZhi) || "卯".equals(diZhi) || "酉".equals(diZhi)) {
                this.sanYuan = "中元"; // 三元
                this.juShu = 7; // 局数
            }
            // 2.4、年支或年干符头的地支为[辰、戌、丑、未]时，使用下元，即：阴遁四局
            if ("辰".equals(diZhi) || "戌".equals(diZhi) || "丑".equals(diZhi) || "未".equals(diZhi)) {
                this.sanYuan = "下元"; // 三元
                this.juShu = 4; // 局数
            }
            return;
        }

        // 3、日家奇门
        if (this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 2) {
            // 3.1、计算三元
            Map<String, String> riZhuFuTouMap = QiMenZhuanPanJiChuMap.RI_ZHU_SAN_YUAN; // 日柱对应的三元
            this.sanYuan = riZhuFuTouMap.get(this.dayGanZhi); // 三元
            // 3.2、计算局数，获取日期是当年中的第几天
            Calendar c = Calendar.getInstance();
            c.set(this.solar.getYear(), this.solar.getMonth() - 1, this.solar.getDay());
            int day = c.get(Calendar.DAY_OF_YEAR);
            if (day <= 60) this.juShu = 1; // 1~60天用阳遁一局
            if (day > 60 && day <= 120) this.juShu = 7; // 61~120天用阳遁七局
            if (day > 120 && day <= 180) this.juShu = 4; // 121~180天用阳遁四局
            if (day > 180 && day <= 240) this.juShu = 9; // 181~240天用阴遁九局
            if (day > 240 && day <= 300) this.juShu = 3; // 241~300天用阴遁三局
            if (day > 300) this.juShu = 6; // 大于300天用阴遁六局
            return;
        }

        // 4、时家奇门
        if (this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 3) {
            // 4.1、计算三元
            this.sanYuan = QiMenZhuanPanJiChuMap.RI_ZHU_SAN_YUAN.get(this.dayGanZhi); // 根据日干支获取三元
            // 4.2、计算局数
            List<Integer> juShu = QiMenZhuanPanJiChuMap.JU_SHU.get(this.jieQi); // 根据节气获取[上元、中元、下元]对应的局数
            // 4.3、根据三元判断所用局数
            if ("上元".equals(this.sanYuan)) this.juShu = juShu.get(0);
            if ("中元".equals(this.sanYuan)) this.juShu = juShu.get(1);
            if ("下元".equals(this.sanYuan)) this.juShu = juShu.get(2);
        }

    }

    /**
     * 初始化阴阳遁
     */
    private void initializeYinYangDun() {

        // 1、年家奇门、月家奇门
        if (this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 0 || this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 1) {
            this.yinYangDun = "阴遁";
            return;
        }

        // 2、日家奇门
        if (this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 2) {
            this.yinYangDun = "阴遁";
            Map<String, List<String>> map = QiMenZhuanPanJiChuMap.YIN_YANG_DUN_JIE_QI; // 阴阳遁对应的二十四节气
            // 若节气在[冬至~夏至前]，则使用阳遁
            List<String> yangJie = map.get("阳遁"); // 阳遁节气
            for (String key : yangJie) {
                if (key.equals(getJieQi())) {
                    this.yinYangDun = "阳遁";
                    break;
                }
            }
            return;
        }

        // 3、时家奇门
        if (this.qiMenZhuanPanJiChuSetting.getPaiPanType() == 3) {
            Map<String, String> map = QiMenZhuanPanJiChuMap.JIE_QI_YIN_YANG_DUN; // 二十四节气对应阴阳遁
            this.yinYangDun = map.get(this.jieQi);
        }

    }

    /**
     * 初始化旬首
     */
    private void initializeXunShou() {

        Map<String, List<String>> sixJiaZiXunShouAndYiZhangMap = QiMenZhuanPanJiChuMap.SIX_JIA_ZI_XUN_SHOU_AND_YI_ZHANG; // 六十甲子对应的旬首及仪仗（六十甲子为键）
        this.xunShou = sixJiaZiXunShouAndYiZhangMap.get(this.hourGanZhi).get(0); // 旬首（如：甲子）
        this.xunShouYiZhang = sixJiaZiXunShouAndYiZhangMap.get(this.hourGanZhi).get(1); // 旬首仪仗（如：戊）

    }

    /**
     * 初始化地盘奇仪、地盘六甲、值符、值使
     */
    private void initializeDiQiYiLiuJiaFuShi() {

        // 1.1、阳遁
        if ("阳遁".equals(this.yinYangDun)) {
            this.diQiYi = QiMenZhuanPanJiChuMap.DI_YANG_QI_YI.get(this.juShu); // 奇仪
            this.diLiuJia = QiMenZhuanPanJiChuMap.DI_YANG_LIU_JIA.get(this.juShu); // 六甲
        } else {
            // 1.2、阴遁
            this.diQiYi = QiMenZhuanPanJiChuMap.DI_YIN_QI_YI.get(this.juShu); // 奇仪
            this.diLiuJia = QiMenZhuanPanJiChuMap.DI_YIN_LIU_JIA.get(this.juShu); // 六甲
        }

        // 2、根据旬首和六甲获取旬首落宫
        for (int i = 0; i < this.diLiuJia.size(); i++) {
            if (this.xunShou.equals(this.diLiuJia.get(i))) {
                this.xunShouGongWei = i + 1; // 旬首落宫（即：值符落宫）
                this.oldZhiFuGongWei = i + 1; // 值符旋转前落宫
                this.oldZhiShiGongWei = i + 1; // 值使旋转前落宫
                break;
            }
        }

        // 3、根据旬首落宫获取[值符]和[值使]
        // 3.1、设置值符
        this.zhiFu = QiMenZhuanPanJiChuMap.JIU_XING_INITIAL[this.xunShouGongWei - 1];
        // 3.2、设置值使
        if ("天禽".equals(QiMenZhuanPanJiChuMap.JIU_XING_INITIAL[this.xunShouGongWei - 1]) || this.xunShouGongWei == 5) {
            if (this.qiMenZhuanPanJiChuSetting.getZhiShiType() == 1) {
                this.zhiShi = QiMenZhuanPanJiChuUtil.getZhiShi2(this.yinYangDun); // 计算并返回值使（天禽星为值符时：根据阴阳遁判断）
            } else if (this.qiMenZhuanPanJiChuSetting.getZhiShiType() == 2) {
                this.zhiShi = QiMenZhuanPanJiChuUtil.getZhiShi3(this.jieQi); // 计算并返回值使（天禽星为值符时：根据节气判断）
            } else {
                this.zhiShi = QiMenZhuanPanJiChuUtil.getZhiShi1(); // 计算并返回值使（天禽星为值符时：一律用[死门]为值使）
            }
        } else {
            this.zhiShi = QiMenZhuanPanJiChuMap.BA_MEN_INITIAL[this.xunShouGongWei - 1];
        }

    }

    /**
     * 初始化地盘
     */
    private void initializeDiPan() {
        this.diPan = this.diQiYi;
    }

    /**
     * 初始化天盘
     */
    private void initializeTianPan() {

        // 1、若时干为甲，则使用旬首仪仗进行判断
        String hourGan = "甲".equals(this.hourGan) ? this.xunShouYiZhang : this.hourGan;

        // 2、计算时干落宫
        for (int i = 0; i < this.diQiYi.size(); i++) {
            if (hourGan.equals(this.diQiYi.get(i))) {
                // 2.1、设置值符旋转后落入的宫位，若落中五宫则寄坤二宫
                this.newZhiFuGongWei = (i + 1 == 5) ? 2 : i + 1;
                break;
            }
        }

        // 3、将九星依次加入宫位中
        Map<Integer, List<String>> jiuXingShun = QiMenZhuanPanJiChuMap.JIU_XING_SHUN; // 九星位置（顺转九宫）
        for (int i = 0; i < jiuXingShun.size(); i++) {
            List<String> jiuXing = jiuXingShun.get(i);
            // 3.1、若值符为'天禽'，则使用'天芮'进行判断
            String zhiFu = getZhiFu();
            if ("天禽".equals(zhiFu)) zhiFu = "天芮";
            // 3.2、将'天芮'更换为：芮禽
            if (zhiFu.equals(jiuXing.get(this.newZhiFuGongWei - 1))) {
                List<String> tianPan = new ArrayList<>(jiuXing);
                for (int j = 0; j < jiuXing.size(); j++) {
                    if ("天芮".equals(jiuXing.get(j))) {
                        tianPan.set(j, "芮禽");
                        break;
                    }
                }
                this.tianPan = tianPan;
                break;
            }
        }

        // 4、计算原宫九星所携带的奇仪（只包含'天禽星'所携带的奇仪）
        List<String> tianPanQiYiTianQinYes = CommonUtil.addCharToList(9, ""); // 天盘旋转后九星携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
        for (int i = 0; i < this.tianPan.size(); i++) {
            if (!"".equals(this.tianPan.get(i))) {
                if ("天禽".substring(1, 2).equals(this.tianPan.get(i).substring(1, 2))) {
                    tianPanQiYiTianQinYes.set(i, this.diQiYi.get(4));
                }
            }
        }
        this.tianPanQiYiTianQinYes = tianPanQiYiTianQinYes;

        // 5、计算原宫九星所携带的奇仪（不包含'天禽星'所携带的奇仪）
        Map<String, Integer> jiuXingInitial = QiMenZhuanPanJiChuMap.JIU_XING_INITIAL2; // 九星原始宫位（1~9宫）
        List<String> tianPanQiYiTianQinNo = new ArrayList<>(); // 天盘旋转后九星携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
        int index;
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < this.diQiYi.size(); j++) {
                if (i == 4) {
                    tianPanQiYiTianQinNo.add(i, this.diQiYi.get(i)); // 九星原始宫位所携带的奇仪
                } else {
                    if ("芮禽".substring(0, 1).equals(this.tianPan.get(i).substring(0, 1))) {
                        index = jiuXingInitial.get("天芮") - 1; // 九星原始宫位
                    } else if ("天禽".substring(1, 2).equals(this.tianPan.get(i).substring(1, 2))) {
                        index = jiuXingInitial.get("天禽") - 1; // 九星原始宫位
                    } else {
                        index = jiuXingInitial.get(this.tianPan.get(i)) - 1; // 九星原始宫位
                    }
                    tianPanQiYiTianQinNo.add(i, this.diQiYi.get(index)); // 九星原始宫位所携带的奇仪
                }
                i++;
            }
        }
        this.tianPanQiYiTianQinNo = tianPanQiYiTianQinNo;

    }

    /**
     * 初始化人盘
     */
    private void initializeRenPan() {

        String hourZhi = getHourZhi(); // 时支
        String[] diZhi = QiMenZhuanPanJiChuMap.DI_ZHI; // 地支
        String xunShouZhi = getXunShou().substring(1, 2); // 旬首的地支

        // 1、获取旬首中的地支在第几号索引
        int xunShouZhiIndex = 0; // 记录旬首中的地支索引
        for (int i = 0; i < diZhi.length; i++) {
            if (xunShouZhi.equals(diZhi[i])) {
                xunShouZhiIndex = i;
                break;
            }
        }

        // 2、接着旬首中的地支索引值向后查找时支所在位置
        int hourZhiCount = 0; // 记录找到时支时所需要查找的次数
        for (int i = 0; i < diZhi.length; i++) {
            if (xunShouZhiIndex == diZhi.length) {
                // 2.1、若查找至最后一个元素时仍未找到地支，则重置旬首中的地支索引值
                xunShouZhiIndex = 0;
            } else if (!hourZhi.equals(diZhi[xunShouZhiIndex])) {
                // 2.2、未找到元素，继续查找
                hourZhiCount++; // 查找次数+1
                xunShouZhiIndex++; // 旬首中的地支索引+1
            } else {
                // 2.3、已找到元素，停止查找
                break;
            }
        }

        // 3、若[旬首中的地支]和[时支]不相同，说明值使落宫已改变
        int xunShouGong = this.xunShouGongWei; // 旬首落宫（即：值符和值使的落宫）
        if (!xunShouZhi.equals(hourZhi)) {
            // 3.1、计算值使旋转后的宫位
            if ("阳遁".equals(this.yinYangDun)) {
                // 3.2、阳遁用[值使旋转前宫位+一共查找的次数]获取旋转后值使所落宫位，顺排九宫
                for (int i = 0; i < hourZhiCount; i++) {
                    // 3.3、若值使旋转后的宫位大于等于9，则重新从第一宫开始判断
                    if (xunShouGong >= 9) {
                        xunShouGong = 1;
                    } else {
                        xunShouGong++;
                    }
                }
            } else {
                // 3.4、阴遁用[值使旋转前宫位+一共查找的次数]获取旋转后值使所落宫位，逆排九宫
                for (int i = 0; i < hourZhiCount; i++) {
                    // 3.5、若值使旋转后的宫位小于等于0，则重新从第九宫开始判断
                    if (xunShouGong <= 1) {
                        xunShouGong = 9;
                    } else {
                        xunShouGong--;
                    }
                }
            }
        }

        // 4、若值使旋转后落中五宫则寄坤二宫
        this.newZhiShiGongWei = xunShouGong == 5 ? 2 : xunShouGong;

        // 5、计算人盘
        List<String> list = new ArrayList<>();
        Map<Integer, List<String>> baMenShun = QiMenZhuanPanJiChuMap.BA_MEN_SHUN_ZHUAN; // 八门位置（顺转九宫）
        for (int i = 0; i < baMenShun.size(); i++) {
            List<String> baMen = baMenShun.get(i);
            for (int j = 0; j < baMen.size(); j++) {
                if (baMen.get(this.newZhiShiGongWei - 1).equals(this.zhiShi)) {
                    list = baMen;
                    break;
                }
            }
        }

        // 6、设置人盘
        this.renPan = list;

    }

    /**
     * 初始化神盘
     */
    private void initializeShenPan() {

        /*
            根据小值符随大值符的原则，即：将小值符加在天盘大值符宫位上即可。
         */

        // 1、若值符落中五宫则寄二宫
        int newZhiFuGong = this.newZhiFuGongWei == 5 ? 2 : this.newZhiFuGongWei; // [值符]旋转后宫位

        // 2、判断阴阳遁
        if ("阳遁".equals(getYinYangDun())) {
            // 2.1、阳遁顺转九宫【此处按小值符追随天盘大值符计算。当然还有另外一种方式：小值符追随地盘值符】
            this.shenPan = QiMenZhuanPanJiChuMap.BA_SHEN_SHUN_ZHUAN.get(newZhiFuGong);
        } else {
            // 2.2、阴遁逆转九宫【此处按小值符追随天盘大值符计算。当然还有另外一种方式：小值符追随地盘值符】
            this.shenPan = QiMenZhuanPanJiChuMap.BA_SHEN_NI_ZHUAN.get(newZhiFuGong);
        }

    }

//===============================================================================================================================

    /**
     * 获取公历日期（Solar型，如：2024-01-01）
     *
     * @return 公历日期
     */
    public Solar getSolar() {
        return this.solar;
    }

    /**
     * 获取农历日期（Lunar型，如：二〇二三年冬月二十）
     *
     * @return 农历日期
     */
    public Lunar getLunar() {
        return this.lunar;
    }

    /**
     * 获取公历日期（String型，如：2024-01-01 00:00:00）
     *
     * @return 公历日期
     */
    public String getSolarStr() {
        return this.solarStr;
    }

    /**
     * 获取农历日期（String型，如：2023-11-20 00:00:00）
     *
     * @return 农历日期
     */
    public String getLunarStr() {
        return this.lunarStr;
    }

    /**
     * 获取公历日期（String型，如：2024年01月01日00时00分00秒）
     *
     * @return 公历日期
     */
    public String getSolarStr2() {
        return this.solarStr2;
    }

    /**
     * 获取农历日期（String型，如：二〇二三年冬月二十(早)子时）
     *
     * @return 农历日期
     */
    public String getLunarStr2() {
        return this.lunarStr2;
    }

    /**
     * 获取公历日期（Date型，如：Mon Jan 01 00:00:00 CST 2024）
     *
     * @return 公历日期
     */
    public Date getSolarDate() {
        return this.solarDate;
    }

    /**
     * 获取农历日期（Date型，如：Mon Nov 20 00:00:00 CST 2023）
     *
     * @return 农历日期
     */
    public Date getLunarDate() {
        return this.lunarDate;
    }


    /**
     * 获取姓名
     *
     * @return 姓名（如：命主）
     */
    public String getName() {
        return this.qiMenZhuanPanJiChuSetting.getName();
    }

    /**
     * 获取占事
     *
     * @return 占事（如：未填写）
     */
    public String getOccupy() {
        return this.qiMenZhuanPanJiChuSetting.getOccupy();
    }

    /**
     * 获取性别
     *
     * @return 性别（如：男）
     */
    public String getSex() {
        return this.qiMenZhuanPanJiChuSetting.getSex() == 0 ? "女" : "男";
    }

    /**
     * 获取年龄
     */
    public int getAge() {

        LocalDate nowDate = LocalDate.now(); // 当前日期
        LocalDate birthDate = this.solarDate.toInstant().atZone(ZoneId.systemDefault()).toLocalDate(); // 出生日期

        // 1.1、计算实岁
        int age = Period.between(birthDate, nowDate).getYears();
        // 1.2、计算虚岁
        if (this.qiMenZhuanPanJiChuSetting.getXuShiSuiType() == 0) {
            age = age + (nowDate.getMonthValue() > birthDate.getMonthValue() || (nowDate.getMonthValue() == birthDate.getMonthValue() && nowDate.getDayOfMonth() >= birthDate.getDayOfMonth()) ? 1 : 0);
        }

        return age;

    }

    /**
     * 获取造
     *
     * @return 造（如：乾造）
     */
    public String getZao() {
        return this.qiMenZhuanPanJiChuSetting.getSex() == 0 ? "坤造" : "乾造";
    }

    /**
     * 获取星期
     *
     * @return 星期（如：周一）
     */
    public String getXingQi() {
        return "周" + this.lunar.getWeekInChinese();
    }

    /**
     * 获取季节
     *
     * @return 季节（如：孟春）
     */
    public String getJiJie() {
        return this.lunar.getSeason();
    }

    /**
     * 获取生肖
     *
     * @return 生肖（如：鼠）
     */
    public String getShengXiao() {

        if (this.qiMenZhuanPanJiChuSetting.getYearGanZhiType() == 0) {
            return this.lunar.getYearShengXiao(); // 以正月初一起算
        } else if (this.qiMenZhuanPanJiChuSetting.getYearGanZhiType() == 1) {
            return this.lunar.getYearShengXiaoByLiChun(); // 以立春当天起算
        } else if (this.qiMenZhuanPanJiChuSetting.getYearGanZhiType() == 2) {
            return this.lunar.getYearShengXiaoExact(); // 以立春交接时刻起算
        }

        return this.lunar.getYearShengXiao();

    }

    /**
     * 获取星座
     *
     * @return 星座（如：魔羯座）
     */
    public String getXingZuo() {
        return this.solar.getXingZuo() + "座";
    }

    /**
     * 获取五不遇时
     *
     * @return 五不遇时（true:符合。false:不符合）
     */
    public boolean getWuBuYuShi() {
        return this.hourGanZhi.equals(QiMenZhuanPanJiChuMap.WU_BU_YU_SHI.get(this.dayGan));
    }


    /**
     * 获取年干
     *
     * @return 年干（如：甲）
     */
    public String getYearGan() {
        return this.yearGan;
    }

    /**
     * 获取月干
     *
     * @return 月干（如：甲）
     */
    public String getMonthGan() {
        return this.monthGan;
    }

    /**
     * 获取日干
     *
     * @return 日干（如：甲）
     */
    public String getDayGan() {
        return this.dayGan;
    }

    /**
     * 获取时干
     *
     * @return 时干（如：甲）
     */
    public String getHourGan() {
        return this.hourGan;
    }


    /**
     * 获取年支
     *
     * @return 年支（如：子）
     */
    public String getYearZhi() {
        return this.yearZhi;
    }

    /**
     * 获取月支
     *
     * @return 月支（如：子）
     */
    public String getMonthZhi() {
        return this.monthZhi;
    }

    /**
     * 获取日支
     *
     * @return 日支（如：子）
     */
    public String getDayZhi() {
        return this.dayZhi;
    }

    /**
     * 获取时支
     *
     * @return 时支（如：子）
     */
    public String getHourZhi() {
        return this.hourZhi;
    }


    /**
     * 获取年干支
     *
     * @return 年干支（如：甲子）
     */
    public String getYearGanZhi() {
        return this.yearGanZhi;
    }

    /**
     * 获取月干支
     *
     * @return 月干支（如：甲子）
     */
    public String getMonthGanZhi() {
        return this.monthGanZhi;
    }

    /**
     * 获取日干支
     *
     * @return 日干支（如：甲子）
     */
    public String getDayGanZhi() {
        return this.dayGanZhi;
    }

    /**
     * 获取时干支
     *
     * @return 时干支（如：甲子）
     */
    public String getHourGanZhi() {
        return this.hourGanZhi;
    }


    /**
     * 获取年干五行
     *
     * @return 年干五行（如：木）
     */
    public String getYearGanWuXing() {
        return QiMenZhuanPanJiChuMap.TIAN_GAN_WU_XING.get(this.yearGan);
    }

    /**
     * 获取月干五行
     *
     * @return 月干五行（如：木）
     */
    public String getMonthGanWuXing() {
        return QiMenZhuanPanJiChuMap.TIAN_GAN_WU_XING.get(this.monthGan);
    }

    /**
     * 获取日干五行
     *
     * @return 日干五行（如：木）
     */
    public String getDayGanWuXing() {
        return QiMenZhuanPanJiChuMap.TIAN_GAN_WU_XING.get(this.dayGan);
    }

    /**
     * 获取时干五行
     *
     * @return 时干五行（如：木）
     */
    public String getHourGanWuXing() {
        return QiMenZhuanPanJiChuMap.TIAN_GAN_WU_XING.get(this.hourGan);
    }


    /**
     * 获取年支五行
     *
     * @return 年支五行（如：木）
     */
    public String getYearZhiWuXing() {
        return QiMenZhuanPanJiChuMap.DI_ZHI_WU_XING.get(this.yearZhi);
    }

    /**
     * 获取月支五行
     *
     * @return 月支五行（如：木）
     */
    public String getMonthZhiWuXing() {
        return QiMenZhuanPanJiChuMap.DI_ZHI_WU_XING.get(this.monthZhi);
    }

    /**
     * 获取日支五行
     *
     * @return 日支五行（如：木）
     */
    public String getDayZhiWuXing() {
        return QiMenZhuanPanJiChuMap.DI_ZHI_WU_XING.get(this.dayZhi);
    }

    /**
     * 获取时支五行
     *
     * @return 时支五行（如：木）
     */
    public String getHourZhiWuXing() {
        return QiMenZhuanPanJiChuMap.DI_ZHI_WU_XING.get(this.hourZhi);
    }


    /**
     * 获取年干支五行
     *
     * @return 年干支五行（如：木水）
     */
    public String getYearGanZhiWuXing() {
        return getYearGanWuXing() + getYearZhiWuXing();
    }

    /**
     * 获取月干支五行
     *
     * @return 月干支五行（如：木水）
     */
    public String getMonthGanZhiWuXing() {
        return getMonthGanWuXing() + getMonthZhiWuXing();
    }

    /**
     * 获取日干支五行
     *
     * @return 日干支五行（如：木水）
     */
    public String getDayGanZhiWuXing() {
        return getDayGanWuXing() + getDayZhiWuXing();
    }

    /**
     * 获取时干支五行
     *
     * @return 时干支五行（如：木水）
     */
    public String getHourGanZhiWuXing() {
        return getHourGanWuXing() + getHourZhiWuXing();
    }


    /**
     * 获取年干支纳音
     *
     * @return 年干支纳音（如：天上火）
     */
    public String getYearGanZhiNaYin() {
        return QiMenZhuanPanJiChuMap.NA_YIN.get(this.yearGanZhi);
    }

    /**
     * 获取月干支纳音
     *
     * @return 月干支纳音（如：天上火）
     */
    public String getMonthGanZhiNaYin() {
        return QiMenZhuanPanJiChuMap.NA_YIN.get(this.monthGanZhi);
    }

    /**
     * 获取日干支纳音
     *
     * @return 日干支纳音（如：天上火）
     */
    public String getDayGanZhiNaYin() {
        return QiMenZhuanPanJiChuMap.NA_YIN.get(this.dayGanZhi);
    }

    /**
     * 获取时干支纳音
     *
     * @return 时干支纳音（如：天上火）
     */
    public String getHourGanZhiNaYin() {
        return QiMenZhuanPanJiChuMap.NA_YIN.get(this.hourGanZhi);
    }


    /**
     * 获取年干支空亡
     *
     * @return 年干支空亡（如：子丑）
     */
    public String getYearGanZhiKongWang() {
        return QiMenZhuanPanJiChuMap.KONG_WANG.get(this.yearGanZhi);
    }

    /**
     * 获取月干支空亡
     *
     * @return 月干支空亡（如：子丑）
     */
    public String getMonthGanZhiKongWang() {
        return QiMenZhuanPanJiChuMap.KONG_WANG.get(this.monthGanZhi);
    }

    /**
     * 获取日干支空亡
     *
     * @return 日干支空亡（如：子丑）
     */
    public String getDayGanZhiKongWang() {
        return QiMenZhuanPanJiChuMap.KONG_WANG.get(this.dayGanZhi);
    }

    /**
     * 获取时干支空亡
     *
     * @return 时干支空亡（如：子丑）
     */
    public String getHourGanZhiKongWang() {
        return QiMenZhuanPanJiChuMap.KONG_WANG.get(this.hourGanZhi);
    }


    /**
     * 获取上一节
     *
     * @return 上一节（如：大雪）
     */
    public String getPrevJie() {
        return this.prevJie.toString();
    }

    /**
     * 获取上一节日期
     *
     * @return 上一节日期（如：2023-12-07 17:32:44）
     */
    public String getPrevJieDateStr() {
        return this.prevJie.getSolar().toYmdHms();
    }

    /**
     * 获取距上一节天数
     *
     * @return 距上一节天数（如：24）
     */
    public int getPrevJieDay() {
        return Math.toIntExact(DateUtil.dateInterval(getPrevJieDateStr(), this.solarStr).get("day"));
    }

    /**
     * 获取下一节
     *
     * @return 下一节（如：小寒）
     */
    public String getNextJie() {
        return this.nextJie.toString();
    }

    /**
     * 获取下一节日期
     *
     * @return 下一节日期（如：2024-01-06 04:49:08）
     */
    public String getNextJieDateStr() {
        return this.nextJie.getSolar().toYmdHms();
    }

    /**
     * 获取距下一节天数
     *
     * @return 距下一节天数（如：5）
     */
    public int getNextJieDay() {
        return Math.toIntExact(DateUtil.dateInterval(this.solarStr, getNextJieDateStr()).get("day"));
    }

    /**
     * 获取出生节
     *
     * @return 出生节（如：大雪后24天6小时27分16秒、小寒前5天4小时49分8秒）
     */
    public String getChuShengJie() {

        Map<String, Long> prevMap = DateUtil.dateInterval(getPrevJieDateStr(), this.solarStr); // 计算上一节气与排盘日期的时间间隔
        Map<String, Long> nextMap = DateUtil.dateInterval(this.solarStr, getNextJieDateStr()); // 计算排盘日期与下一节气的时间间隔

        long prevDay = prevMap.get("day") > 0 ? prevMap.get("day") : -prevMap.get("day"); // 天
        long prevHours = prevMap.get("hour") > 0 ? prevMap.get("hour") : -prevMap.get("hour"); // 小时
        long prevMinutes = prevMap.get("minute") > 0 ? prevMap.get("minute") : -prevMap.get("minute"); // 分
        long prevSeconds = prevMap.get("second") > 0 ? prevMap.get("second") : -prevMap.get("second"); // 秒

        long nextDay = nextMap.get("day") > 0 ? nextMap.get("day") : -nextMap.get("day"); // 天
        long nextHours = nextMap.get("hour") > 0 ? nextMap.get("hour") : -nextMap.get("hour"); // 小时
        long nextMinutes = nextMap.get("minute") > 0 ? nextMap.get("minute") : -nextMap.get("minute"); // 分
        long nextSeconds = nextMap.get("second") > 0 ? nextMap.get("second") : -nextMap.get("second"); // 秒

        String prevStr = getPrevJie() + "后" + prevDay + "天" + prevHours + "小时" + prevMinutes + "分" + prevSeconds + "秒";
        String nextStr = getNextJie() + "前" + nextDay + "天" + nextHours + "小时" + nextMinutes + "分" + nextSeconds + "秒";

        return prevStr + "、" + nextStr;

    }


    /**
     * 获取上一气
     *
     * @return 上一气（如：冬至）
     */
    public String getPrevQi() {
        return this.prevQi.toString();
    }

    /**
     * 获取上一气日期
     *
     * @return 上一气日期（如：2023-12-22 11:27:09）
     */
    public String getPrevQiDateStr() {
        return this.prevQi.getSolar().toYmdHms();
    }

    /**
     * 获取距上一气天数
     *
     * @return 距上一气天数（如：9）
     */
    public int getPrevQiDay() {
        return Math.toIntExact(DateUtil.dateInterval(getPrevQiDateStr(), this.solarStr).get("day"));
    }

    /**
     * 获取下一气
     *
     * @return 下一气（如：大寒）
     */
    public String getNextQi() {
        return this.nextQi.toString();
    }

    /**
     * 获取下一气日期
     *
     * @return 下一气日期（如：2024-01-20 22:07:08）
     */
    public String getNextQiDateStr() {
        return this.nextQi.getSolar().toYmdHms();
    }

    /**
     * 获取距下一气天数
     *
     * @return 距下一节天数（如：19）
     */
    public int getNextQiDay() {
        return Math.toIntExact(DateUtil.dateInterval(this.solarStr, getNextQiDateStr()).get("day"));
    }

    /**
     * 获取出生气
     *
     * @return 出生气（如：冬至后9天12小时32分51秒、大寒前19天22小时7分8秒）
     */
    public String getChuShengQi() {

        Map<String, Long> prevMap = DateUtil.dateInterval(getPrevQiDateStr(), this.solarStr); // 计算上一节气与排盘日期的时间间隔
        Map<String, Long> nextMap = DateUtil.dateInterval(this.solarStr, getNextQiDateStr()); // 计算排盘日期与下一节气的时间间隔

        long prevDay = prevMap.get("day") > 0 ? prevMap.get("day") : -prevMap.get("day"); // 天
        long prevHours = prevMap.get("hour") > 0 ? prevMap.get("hour") : -prevMap.get("hour"); // 小时
        long prevMinutes = prevMap.get("minute") > 0 ? prevMap.get("minute") : -prevMap.get("minute"); // 分
        long prevSeconds = prevMap.get("second") > 0 ? prevMap.get("second") : -prevMap.get("second"); // 秒

        long nextDay = nextMap.get("day") > 0 ? nextMap.get("day") : -nextMap.get("day"); // 天
        long nextHours = nextMap.get("hour") > 0 ? nextMap.get("hour") : -nextMap.get("hour"); // 小时
        long nextMinutes = nextMap.get("minute") > 0 ? nextMap.get("minute") : -nextMap.get("minute"); // 分
        long nextSeconds = nextMap.get("second") > 0 ? nextMap.get("second") : -nextMap.get("second"); // 秒

        String prevStr = getPrevQi() + "后" + prevDay + "天" + prevHours + "小时" + prevMinutes + "分" + prevSeconds + "秒";
        String nextStr = getNextQi() + "前" + nextDay + "天" + nextHours + "小时" + nextMinutes + "分" + nextSeconds + "秒";

        return prevStr + "、" + nextStr;

    }


    /**
     * 获取月相
     *
     * @return 月相（如：朔）
     */
    public String getYueXiang() {
        return this.lunar.getYueXiang();
    }

    /**
     * 获取月将
     *
     * @return 月将（如：子）
     */
    public String getYueJiang() {
        return QiMenZhuanPanJiChuMap.YUE_JIANG.get(getPrevQi() + getNextQi()).get(0);
    }

    /**
     * 获取月将神
     *
     * @return 月将神（如：神后）
     */
    public String getYueJiangShen() {
        return QiMenZhuanPanJiChuMap.YUE_JIANG.get(getPrevQi() + getNextQi()).get(1);
    }


    /**
     * 获取符头
     *
     * @return 符头（如：甲子）
     */
    public String getFuTou() {
        return this.fuTou;
    }

    /**
     * 获取节气
     *
     * @return 节气（如：冬至）
     */
    public String getJieQi() {
        return this.jieQi;
    }

    /**
     * 获取三元
     *
     * @return 三元（如：下元）
     */
    public String getSanYuan() {
        return this.sanYuan;
    }

    /**
     * 获取局数
     *
     * @return 局数（如：7）
     */
    public Integer getJuShu() {
        return this.juShu;
    }

    /**
     * 获取阴阳遁
     *
     * @return 阴阳遁（如：阳遁）
     */
    public String getYinYangDun() {
        return this.yinYangDun;
    }

    /**
     * 获取旬首
     *
     * @return 旬首（如：甲子）
     */
    public String getXunShou() {
        return this.xunShou;
    }

    /**
     * 获取旬首仪仗
     *
     * @return 旬首仪仗（如：戊）
     */
    public String getXunShouYiZhang() {
        return this.xunShouYiZhang;
    }

    /**
     * 获取值符
     *
     * @return 值符（如：天任）
     */
    public String getZhiFu() {
        return this.zhiFu;
    }

    /**
     * 获取值使
     *
     * @return 值使（如：开门）
     */
    public String getZhiShi() {
        return this.zhiShi;
    }


    /**
     * 获取六甲旬空（1~9宫）
     *
     * @return 六甲旬空（如：[戌, 亥]）
     */
    public List<String> getLiuJiaXunKong() {
        return QiMenZhuanPanJiChuMap.LIU_JIA_XUN_KONG.get(this.xunShou);
    }

    /**
     * 获取六甲旬空宫位（1~9宫）
     *
     * @return 六甲旬空宫位（如：[6]）
     */
    public List<Integer> getLiuJiaXunKongGongWei() {
        return QiMenZhuanPanJiChuMap.LIU_JIA_XUN_KONG_GONG.get(getLiuJiaXunKong());
    }

    /**
     * 获取六甲旬空宫位标识（1~9宫）
     *
     * @return 六甲旬空宫位标识（如：[, , , , , ○, , , ]）
     */
    public List<String> getLiuJiaXunKongGongWeiMark() {

        List<String> list = CommonUtil.addCharToList(9, "");
        for (int i = 0; i < getLiuJiaXunKongGongWei().size(); i++) {
            list.set(getLiuJiaXunKongGongWei().get(i) - 1, "○"); // ○
        }
        return list;

    }


    /**
     * 获取驿马
     *
     * @return 驿马（如：寅）
     */
    public String getYiMa() {
        return QiMenZhuanPanJiChuMap.YI_MA.get(this.hourZhi);
    }

    /**
     * 获取驿马宫位
     *
     * @return 驿马宫位（如：8）
     */
    public Integer getYiMaGongWei() {
        return QiMenZhuanPanJiChuMap.YI_MA_GONG.get(getYiMa());
    }

    /**
     * 获取驿马宫位标识（1~9宫）
     *
     * @return 驿马宫位标识（如：[, , , , , , , 马, ]）
     */
    public List<String> getYiMaGongWeiMark() {

        List<String> list = CommonUtil.addCharToList(9, "");
        list.set(getYiMaGongWei() - 1, "马");
        return list;

    }


    /**
     * 获取地盘（1~9宫）
     *
     * @return 地盘（如：[戊, 己, 庚, 辛, 壬, 癸, 丁, 丙, 乙]）
     */
    public List<String> getDiPan() {
        return this.diPan;
    }

    /**
     * 获取天盘（1~9宫）
     *
     * @return 天盘（如：[天蓬, 芮禽, 天冲, 天辅, , 天心, 天柱, 天任, 天英]）
     */
    public List<String> getTianPan() {
        return this.tianPan;
    }

    /**
     * 获取人盘（1~9宫）
     *
     * @return 人盘（如：[休门, 死门, 伤门, 杜门, , 开门, 惊门, 生门, 景门]）
     */
    public List<String> getRenPan() {
        return this.renPan;
    }

    /**
     * 获取神盘（1~9宫）
     *
     * @return 神盘（如：[值符, 玄武, 太阴, 六合, , 九天, 九地, 螣蛇, 白虎]）
     */
    public List<String> getShenPan() {
        return this.shenPan;
    }


    /**
     * 获取天盘旋转后九星携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
     *
     * @return 天盘旋转后九星携带的奇仪，不包含[天禽星]携带的奇仪（如：[, 壬, , , , , , , ]）
     */
    public List<String> getTianPanQiYiTianQinNo() {
        return this.tianPanQiYiTianQinNo;
    }

    /**
     * 获取天盘旋转后九星携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
     *
     * @return 天盘旋转后九星携带的奇仪，只包含[天禽星]携带的奇仪（如：[戊, 己, 庚, 辛, 壬, 癸, 丁, 丙, 乙]）
     */
    public List<String> getTianPanQiYiTianQinYes() {
        return this.tianPanQiYiTianQinYes;
    }


    /**
     * 获取天乙
     *
     * @return 天乙（如：天任）
     */
    public String getTianYi() {
        return QiMenZhuanPanJiChuMap.JIU_XING_INITIAL[this.newZhiFuGongWei - 1]; // 天乙
    }

    /**
     * 获取地乙
     *
     * @return 地乙（如：开门）
     */
    public String getDiYi() {
        return QiMenZhuanPanJiChuMap.BA_MEN_INITIAL[this.newZhiShiGongWei - 1]; // 地乙
    }

    /**
     * 获取太乙
     *
     * @return 太乙（如：开门）
     */
    public String getTaiYi() {
        return this.zhiShi; // 太乙
    }


    /**
     * 获取九遁（1~9宫）
     *
     * @return 九遁（如：{0=[], 1=[], 2=[], 3=[], 4=[], 5=[], 6=[], 7=[], 8=[]}）
     */
    public List<List<String>> getJiuDun() {

        List<String> listOne = new ArrayList<>(); //  保存单宫九遁
        List<List<String>> listAll = new ArrayList<>(); // 保存九宫九遁

        // 1、计算九遁
        List<String> tianDun = computeTianDun(); // 天遁
        List<String> diDun = computeDiDun(); // 地遁
        List<String> renDun = computeRenDun(); // 人遁
        List<String> shenDun = computeShenDun(); // 神遁
        List<String> guiDun = computeGuiDun(); // 鬼遁
        List<String> fengDun = computeFengDun(); // 风遁
        List<String> yunDun = computeYunDun(); // 云遁
        List<String> longDun = computeLongDun(); // 龙遁
        List<String> huDun = computeHuDun(); // 虎遁

        // 2、整合九遁
        for (int i = 0; i < 9; i++) {
            if (!"".equals(tianDun.get(i))) listOne.add(tianDun.get(i));
            if (!"".equals(diDun.get(i))) listOne.add(diDun.get(i));
            if (!"".equals(renDun.get(i))) listOne.add(renDun.get(i));
            if (!"".equals(shenDun.get(i))) listOne.add(shenDun.get(i));
            if (!"".equals(guiDun.get(i))) listOne.add(guiDun.get(i));
            if (!"".equals(fengDun.get(i))) listOne.add(fengDun.get(i));
            if (!"".equals(yunDun.get(i))) listOne.add(yunDun.get(i));
            if (!"".equals(longDun.get(i))) listOne.add(longDun.get(i));
            if (!"".equals(huDun.get(i))) listOne.add(huDun.get(i));
            listAll.add(listOne);
            listOne = new ArrayList<>();
        }

        return listAll;

    }


    /**
     * 获取内外宫位标识
     *
     * @return 内外宫位标识（如：[内, 外, 内, 内, , 外, 外, 内, 外]）
     */
    public List<String> getNeiWaiGongWeiMark() {
        return QiMenZhuanPanJiChuMap.YIN_YANG_GONG_MARK.get(this.yinYangDun);
    }

    /**
     * 获取内外宫位信息
     *
     * @return 内外宫位信息（如：[日干【甲】在内盘，落坎一宫，主近、主快。, 时干【甲】在内盘，落坎一宫，主近、主快。]）
     */
    public List<String> getNeiWaiGongWeiInfo() {

        List<String> list = new ArrayList<>();

        int dglg = 0; // 日干落宫
        int hglg = 0; // 时干落宫
        for (int i = 0; i < 9; i++) {
            if (getDayGan().equals(this.tianPanQiYiTianQinYes.get(i))) {
                dglg = i; // 日干落宫
                break;
            }
            if (getDayGan().equals(this.tianPanQiYiTianQinNo.get(i))) {
                dglg = i; // 日干落宫
                break;
            }
        }
        for (int i = 0; i < 9; i++) {
            if (getHourGan().equals(this.tianPanQiYiTianQinYes.get(i))) {
                hglg = i; // 时干落宫
                break;
            }
            if (getHourGan().equals(this.tianPanQiYiTianQinNo.get(i))) {
                hglg = i; // 时干落宫
                break;
            }
        }

        Map<Integer, String> jggw = QiMenZhuanPanJiChuMap.JIU_GONG_GONG_WEI; // 九宫宫位（1~9为键）
        List<String> neiWaiGongWeiMark = getNeiWaiGongWeiMark(); // 获取内外宫位标识

        String dayGanIfo;
        if (neiWaiGongWeiMark.get(dglg).equals("内")) {
            dayGanIfo = "主近、主快。";
        } else {
            dayGanIfo = "主远、主慢。";
        }
        String dayGanInfo = "日干【" + getDayGan() + "】在" + neiWaiGongWeiMark.get(dglg) + "盘，落" + jggw.get(dglg) + "，" + dayGanIfo;

        String hourGanIfo;
        if (neiWaiGongWeiMark.get(hglg).equals("内")) {
            hourGanIfo = "主近、主快。";
        } else {
            hourGanIfo = "主远、主慢。";
        }
        String hourGanInfo = "时干【" + getHourGan() + "】在" + neiWaiGongWeiMark.get(hglg) + "盘，落" + jggw.get(hglg) + "，" + hourGanIfo;

        list.add(dayGanInfo);
        list.add(hourGanInfo);

        return list;

    }


    /**
     * 获取天门（1~9宫）
     *
     * @return 天门（如：[大吉, 传送_从魁, 天罡, 太乙_胜光, , 神后_登明, 河魁, 太冲_功曹, 小吉]）
     */
    public List<String> getTianMen() {
        return QiMenZhuanPanJiChuMap.YUE_JIANG_SHEN_LUO_GONG.get(getYueJiang() + this.hourZhi);
    }

    /**
     * 获取地户（1~9宫）
     *
     * @return 地户（如：[建, 危_成, 平, 定_执, , 闭_开, 收, 满_除, 破]）
     */
    public List<String> getDiHu() {
        return QiMenZhuanPanJiChuMap.YUE_JIAN_LUO_GONG.get(this.hourZhi);
    }


    /**
     * 获取伏吟
     *
     * @return 伏吟（如：[奇仪伏吟, 九星伏吟, 八门伏吟, 八神伏吟]）
     */
    public List<String> getFuYin() {
        return QiMenZhuanPanJiChuUtil.getFuYin(getDiPan(), getTianPan(), getRenPan(), getShenPan(), this.tianPanQiYiTianQinNo);
    }

    /**
     * 获取反吟
     *
     * @return 反吟（如：[]）
     */
    public List<String> getFanYin() {
        return QiMenZhuanPanJiChuUtil.getFanYin(getDiPan(), getTianPan(), getRenPan(), getShenPan(), this.tianPanQiYiTianQinNo);
    }


    /**
     * 获取六仪击刑（1~9宫）
     *
     * @return 六仪击刑（如：[↗己击刑（坤二宫）]）
     */
    public List<String> getLiuYiJiXing() {
        return QiMenZhuanPanJiChuUtil.getLiuYiJiXing(this.tianPanQiYiTianQinYes, this.tianPanQiYiTianQinNo);
    }

    /**
     * 获取奇仪入墓（1~9宫）
     *
     * @return 奇仪入墓（如：[↖辛入墓（巽四宫）]）
     */
    public List<String> getQiYiRuMu() {
        return QiMenZhuanPanJiChuUtil.getQiYiRuMu(this.tianPanQiYiTianQinYes, this.tianPanQiYiTianQinNo);
    }


    /**
     * 获取六仪击邢入墓状态，不包含[天禽星]携带的奇仪（1~9宫）
     *
     * @return 六仪击邢入墓状态，不包含[天禽星]携带的奇仪（如：[, 击邢, , 入墓, , , , , ]）
     */
    public List<String> getLiuYiJiXingRuMuTianQinNoStatus() {
        return QiMenZhuanPanJiChuUtil.getJiXingRuMuStatus(null, this.tianPanQiYiTianQinNo).get("jiXingRuMuLinkTianPanQiYiTianQinNo");
    }

    /**
     * 获取六仪击邢入墓状态，只包含[天禽星]携带的奇仪（1~9宫）
     *
     * @return 六仪击邢入墓状态，只包含[天禽星]携带的奇仪（如：[, , , , , , , , ]）
     */
    public List<String> getLiuYiJiXingRuMuTianQinYesStatus() {
        return QiMenZhuanPanJiChuUtil.getJiXingRuMuStatus(this.tianPanQiYiTianQinYes, null).get("jiXingRuMuLinkTianPanQiYiTianQinYes");
    }

    /**
     * 获取门迫状态（1~9宫）
     *
     * @return 门迫状态（如：[, , , , , , , , ]）
     */
    public List<String> getMenPoStatus() {
        return QiMenZhuanPanJiChuUtil.getMenPoStatus(this.renPan);
    }


    /**
     * 获取十干克应（1~9宫）
     *
     * @return 十干克应（如：）
     */
    public List<List<String>> getShiGanKeYing() {
        return QiMenZhuanPanJiChuUtil.getShiGanKeYing(this.diPan, this.tianPanQiYiTianQinYes, this.tianPanQiYiTianQinNo);
    }

    /**
     * 获取八门克应（1~9宫）
     *
     * @return 八门克应（如：）
     */
    public List<List<String>> getBaMenKeYing() {
        return QiMenZhuanPanJiChuUtil.getBaMenKeYing(this.renPan, this.diPan, this.tianPanQiYiTianQinYes, this.tianPanQiYiTianQinNo);
    }

    /**
     * 获取八门静应（1~9宫）
     *
     * @return 八门静应（如：）
     */
    public List<List<String>> getBaMenJingYing() {
        return QiMenZhuanPanJiChuUtil.getMenDongJingYing(QiMenZhuanPanJiChuMap.BA_MEN_KE_YING, this.renPan);
    }

    /**
     * 获取八门动应（1~9宫）
     *
     * @return 八门动应（如：）
     */
    public List<List<String>> getBaMenDongYing() {
        return QiMenZhuanPanJiChuUtil.getMenDongJingYing(QiMenZhuanPanJiChuMap.BA_MEN_DONG_YING, this.renPan);
    }

    /**
     * 获取星门克应（1~9宫）
     *
     * @return 星门克应（如：）
     */
    public List<List<String>> getXingMenKeYing() {
        return QiMenZhuanPanJiChuUtil.getXingMenKeYing(this.tianPan, this.renPan);
    }

    /**
     * 获取九星时应（1~9宫）
     *
     * @return 九星时应（如：）
     */
    public List<List<String>> getJiuXingShiYing() {
        return QiMenZhuanPanJiChuUtil.getJiuXingShiYing(this.hourZhi, this.tianPan);
    }


    /**
     * 获取八卦旺衰（1~9宫）
     *
     * @return 八卦旺衰（如：[[坎宫, 旺], [坤宫, 囚], [震宫, 相], [巽宫, 相], [中宫, ], [乾宫, 休], [兑宫, 休], [艮宫, 囚], [离宫, 死]]）
     */
    public List<List<String>> getBaGuaWangShuai() {
        return QiMenZhuanPanJiChuUtil.getBaGuaWangShuai(QiMenZhuanPanJiChuMap.DI_ZHI_JI_JIE.get(this.monthZhi));
    }

    /**
     * 获取八门旺衰（1~9宫）
     *
     * @return 八门旺衰（如：[[休门, 旺], [死门, 囚], [伤门, 相], [杜门, 相], [中宫, ], [开门, 休], [惊门, 休], [生门, 囚], [景门, 死]]）
     */
    public List<List<String>> getBaMenWangShuai() {
        return QiMenZhuanPanJiChuUtil.getBaMenWangShuai(this.renPan, QiMenZhuanPanJiChuMap.DI_ZHI_JI_JIE.get(this.monthZhi));
    }

    /**
     * 获取九星旺衰（1~9宫）
     *
     * @return 九星旺衰（如：[[天蓬, 相], [芮禽, 休休], [天冲, 废], [天辅, 废], [中宫, ], [天心, 旺], [天柱, 旺], [天任, 休], [天英, 囚]]）
     */
    public List<List<String>> getJiuXingWangShuai() {
        return QiMenZhuanPanJiChuUtil.getJiuXingWangShuai(this.tianPan, this.monthZhi);
    }


    /**
     * 获取八神落宫状态（1~9宫）
     *
     * @return 八神落宫状态（如：[[值符, 吉], [玄武, 凶], [太阴, 吉], [六合, 吉], [中宫, ], [九天, 吉], [九地, 吉], [螣蛇, 凶], [白虎, 凶]]）
     */
    public List<List<String>> getBaShenLuoGongStatus() {
        return QiMenZhuanPanJiChuUtil.getBaShenLuoGongStatus(this.shenPan);
    }

    /**
     * 获取八门落宫状态（1~9宫）
     *
     * @return 八门落宫状态（如：[[休门, 伏吟], [死门, 伏吟], [伤门, 伏吟], [杜门, 伏吟], [中宫, ], [开门, 伏吟], [惊门, 伏吟], [生门, 伏吟], [景门, 伏吟]]）
     */
    public List<List<String>> getBaMenLuoGongStatus() {
        return QiMenZhuanPanJiChuUtil.getBaMenLuoGongStatus(this.renPan);
    }

    /**
     * 获取九星落宫状态（1~9宫）
     *
     * @return 九星落宫状态（如：[[天蓬, 相], [芮禽, 相相], [天冲, 相], [天辅, 相], [中宫, ], [天心, 相], [天柱, 相], [天任, 相], [天英, 相]]）
     */
    public List<List<String>> getJiuXingLuoGongStatus() {
        return QiMenZhuanPanJiChuUtil.getJiuXingLuoGongStatus(this.tianPan);
    }


    /**
     * 获取地盘奇仪与落宫地支的关系
     *
     * @return 地盘奇仪与落宫地支的关系（如：[[[子, 胎], [, ]], [[未, 冠带], [申, 沐浴]], [[卯, 胎], [, ]], [[辰, 墓], [巳, 死]], [[, ], [, ]], [[戌, 衰], [亥, 帝旺]], [[酉, 长生], [, ]], [[丑, 养], [寅, 长生]], [[午, 长生], [, ]]]）
     */
    public List<List<List<String>>> getDiPanQiYiLuoGongLink() {
        return QiMenZhuanPanJiChuUtil.getDiPanQiYiLuoGongLink(this.diPan);
    }

    /**
     * 获取天盘奇仪与落宫地支的关系，只包含[天禽星]携带的奇仪（1~9宫）
     *
     * @return 天盘奇仪与落宫地支的关系，只包含[天禽星]携带的奇仪（如：[[[子, 胎], [, ]], [[未, 冠带], [申, 沐浴]], [[卯, 胎], [, ]], [[辰, 墓], [巳, 死]], [[, ], [, ]], [[戌, 衰], [亥, 帝旺]], [[酉, 长生], [, ]], [[丑, 养], [寅, 长生]], [[午, 长生], [, ]]]）
     */
    public List<List<List<String>>> getTianPanQiYiLuoGongTianQinYesLink() {
        return QiMenZhuanPanJiChuUtil.getTianPanQiYiLuoGongTianQinYesLink(this.tianPanQiYiTianQinYes);
    }

    /**
     * 获取天盘奇仪与落宫地支的关系，不包含[天禽星]携带的奇仪（1~9宫）
     *
     * @return 天盘奇仪与落宫地支的关系，不包含[天禽星]携带的奇仪（如：[[[, ], [, ]], [[未, 养], [申, 长生]], [[, ], [, ]], [[, ], [, ]], [[, ], [, ]], [[, ], [, ]], [[, ], [, ]], [[, ], [, ]], [[, ], [, ]]]）
     */
    public List<List<List<String>>> getTianPanQiYiLuoGongTianQinNoLink() {
        return QiMenZhuanPanJiChuUtil.getTianPanQiYiLuoGongTianQinNoLink(this.tianPanQiYiTianQinNo);
    }

//-------------------------------------------------------------------------------------------------------------------------------

    /**
     * 计算天遁（1~9宫）
     *
     * @return 天遁（如：[天, , , , , , , , ]）
     */
    private List<String> computeTianDun() {

        /*
            天盘[丙奇(月奇)]加地盘[六丁]合人盘[开门、休门、生门]。即【丙+丁+开门、休门、生门】。
         */

        List<String> list = CommonUtil.addCharToList(9, "");

        for (int i = 0; i < 9; i++) {
            String tianQinYes = this.tianPanQiYiTianQinYes.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
            String tianQinNo = this.tianPanQiYiTianQinNo.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
            String diPan = this.diPan.get(i); // 每一宫位中的奇仪
            String renPan = this.renPan.get(i); // 每一宫位中的门
            // 判断宫位信息是否符合→ 天盘[丙奇(月奇)]加地盘[六丁]合人盘[开门、休门、生门]。
            if (("丙".equals(tianQinYes) || "丙".equals(tianQinNo)) && "丁".equals(diPan) && ("开门".equals(renPan) || "休门".equals(renPan) || "生门".equals(renPan))) {
                list.set(i, "天");
            }
        }

        return list;

    }

    /**
     * 计算地遁（1~9宫）
     *
     * @return 地遁（如：[地, , , , , , , , ]）
     */
    private List<String> computeDiDun() {

        /*
            天盘[乙奇(日奇)]加地盘[六己]合人盘[开门、休门、生门]。即【乙+己+开门、休门、生门】。
         */

        List<String> list = CommonUtil.addCharToList(9, "");

        for (int i = 0; i < 9; i++) {
            String tianQinYes = this.tianPanQiYiTianQinYes.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
            String tianQinNo = this.tianPanQiYiTianQinNo.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
            String diPan = this.diPan.get(i); // 每一宫位中的奇仪
            String renPan = this.renPan.get(i); // 每一宫位中的门
            // 判断宫位信息是否符合→ 天盘[乙奇(日奇)]加地盘[六己]合人盘[开门、休门、生门]。
            if (("乙".equals(tianQinYes) || "乙".equals(tianQinNo)) && "己".equals(diPan) && ("开门".equals(renPan) || "休门".equals(renPan) || "生门".equals(renPan))) {
                list.set(i, "地");
            }
        }

        return list;

    }

    /**
     * 计算人遁（1~9宫）
     *
     * @return 人遁（如：[人遁, , , , , , , , ]）
     */
    private List<String> computeRenDun() {

        /*
            天盘[丁奇(星奇)]加神盘[太阴]合人盘[休门]。即【丁+太阴+休门】。
         */

        List<String> list = CommonUtil.addCharToList(9, "");

        for (int i = 0; i < 9; i++) {
            String tianQinYes = this.tianPanQiYiTianQinYes.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
            String tianQinNo = this.tianPanQiYiTianQinNo.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
            String shenPan = this.shenPan.get(i); // 每一宫位中的神
            String renPan = this.renPan.get(i); // 每一宫位中的门
            // 判断宫位信息是否符合→ 天盘[丁奇(星奇)]加神盘[太阴]合人盘[休门]。
            if (("丁".equals(tianQinYes) || "丁".equals(tianQinNo)) && "太阴".equals(shenPan) && "休门".equals(renPan)) {
                list.set(i, "人");
            }
        }

        return list;

    }

    /**
     * 计算神遁（1~9宫）
     *
     * @return 神遁（如：[神, , , , , , , , ]）
     */
    private List<String> computeShenDun() {

        /*
            天盘[丙奇(月奇)]加神盘[九天]合人盘[生门]。即【丙+九天+生门】。
         */

        List<String> list = CommonUtil.addCharToList(9, "");

        for (int i = 0; i < 9; i++) {
            String tianQinYes = this.tianPanQiYiTianQinYes.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
            String tianQinNo = this.tianPanQiYiTianQinNo.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
            String shenPan = this.shenPan.get(i); // 每一宫位中的神
            String renPan = this.renPan.get(i); // 每一宫位中的门
            // 判断宫位信息是否符合→ 天盘[丙奇(月奇)]加神盘[九天]合人盘[生门]。
            if (("丙".equals(tianQinYes) || "丙".equals(tianQinNo)) && "九天".equals(shenPan) && "生门".equals(renPan)) {
                list.set(i, "神");
            }
        }

        return list;

    }

    /**
     * 计算鬼遁（1~9宫）
     *
     * @return 鬼遁（如：[鬼, , , , , , , , ]）
     */
    private List<String> computeGuiDun() {

        /*
            天盘[丁奇(星奇)]加神盘[九地]合人盘[杜门、开门]。即【丙+九天+生门】。
         */

        List<String> list = CommonUtil.addCharToList(9, "");

        for (int i = 0; i < 9; i++) {
            String tianQinYes = this.tianPanQiYiTianQinYes.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
            String tianQinNo = this.tianPanQiYiTianQinNo.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
            String shenPan = this.shenPan.get(i); // 每一宫位中的神
            String renPan = this.renPan.get(i); // 每一宫位中的门
            // 判断宫位信息是否符合→ 天盘[丁奇(星奇)]加神盘[九地]合人盘[杜门、开门]。
            if (("丁".equals(tianQinYes) || "丁".equals(tianQinNo)) && "九地".equals(shenPan) && ("杜门".equals(renPan) || "开门".equals(renPan))) {
                list.set(i, "鬼");
            }
        }

        return list;

    }

    /**
     * 计算风遁（1~9宫）
     *
     * @return 风遁（如：[风, , , , , , , , ]）
     */
    private List<String> computeFengDun() {

        /*
            天盘[乙奇(日奇)]加人盘[开门、休门、生门]临[巽四宫]。即【乙+巽四宫+开门、休门、生门】。
         */

        List<String> list = CommonUtil.addCharToList(9, "");

        // 1、获取巽四宫信息
        int gongWei = 3; // 巽四宫对应索引值为3
        String tianQinYes = this.tianPanQiYiTianQinYes.get(gongWei); // 巽四宫天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
        String tianQinNo = this.tianPanQiYiTianQinNo.get(gongWei); // 巽四宫天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
        String renPan = this.renPan.get(gongWei); // 巽四宫中的门

        // 2、判断巽四宫信息是否符合→ 天盘[乙奇(日奇)]加人盘[开门、休门、生门]临[巽四宫]。
        if (("乙".equals(tianQinYes) || "乙".equals(tianQinNo)) && ("开门".equals(renPan) || "休门".equals(renPan) || "生门".equals(renPan))) {
            list.set(gongWei, "风");
        }

        return list;

    }

    /**
     * 计算云遁（1~9宫）
     *
     * @return 云遁（如：[云, , , , , , , , ]）
     */
    private List<String> computeYunDun() {

        /*
            天盘[乙奇(日奇)]加地盘[六辛]合人盘[开门、休门、生门]。即【乙+辛+开门、休门、生门】。
         */

        List<String> list = CommonUtil.addCharToList(9, "");

        for (int i = 0; i < 9; i++) {
            String tianQinYes = this.tianPanQiYiTianQinYes.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
            String tianQinNo = this.tianPanQiYiTianQinNo.get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
            String diPan = this.diPan.get(i); // 每一宫位中的奇仪
            String renPan = this.renPan.get(i); // 每一宫位中的门
            // 宫位信息是否符合→ 天盘[乙奇(日奇)]加地盘[六辛]合人盘[开门、休门、生门]。
            if (("乙".equals(tianQinYes) || "乙".equals(tianQinNo)) && "六辛".equals(diPan) && ("开门".equals(renPan) || "休门".equals(renPan) || "生门".equals(renPan))) {
                list.set(i, "云");
            }
        }

        return list;

    }

    /**
     * 计算龙遁（1~9宫）
     *
     * @return 龙遁（如：[龙, , , , , , , , ]）
     */
    private List<String> computeLongDun() {

        /*
            1、天盘[乙奇(日奇)]加人盘[开门、休门、生门]临[坎一宫]。即【乙+坎一宫+开门、休门、生门】
            2、天盘[乙奇(日奇)]加地盘[六癸]合人盘[开门、休门、生门]。即【乙+癸+开门、休门、生门】
         */

        List<String> list = CommonUtil.addCharToList(9, "");

        // 1、获取坎一宫信息
        int gongWei = 0; // 坎一宫对应索引值为0
        String tianQinYes = this.tianPanQiYiTianQinYes.get(gongWei); // 每一宫位中的天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
        String tianQinNo = this.tianPanQiYiTianQinNo.get(gongWei); // 每一宫位中的天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
        String renPan = this.renPan.get(gongWei); // 坎一宫门

        // 2、判断坎一宫信息是否符合→ 天盘[乙奇(日奇)]加人盘[开门、休门、生门]临[坎一宫]。
        if (("乙".equals(tianQinYes) || "乙".equals(tianQinNo)) && ("开门".equals(renPan) || "休门".equals(renPan) || "生门".equals(renPan))) {
            list.set(gongWei, "龙");
        } else {
            // 2.1、判断1~9宫信息
            for (int i = 0; i < 9; i++) {
                String tianQinYes2 = getTianPanQiYiTianQinYes().get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
                String tianQinNo2 = getTianPanQiYiTianQinNo().get(i); // 每一宫位中的天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
                String diPan2 = getDiPan().get(i); // 每一宫位中的奇仪
                String renPan2 = getRenPan().get(i); // 每一宫位中的八门
                // 2.2、判断宫位信息是否符合→ 天盘[乙奇(日奇)]加地盘[六癸]合人盘[开门、休门、生门]。
                if (("乙".equals(tianQinYes2) || "乙".equals(tianQinNo2)) && "癸".equals(diPan2) && ("开门".equals(renPan2) || "休门".equals(renPan2) || "生门".equals(renPan2))) {
                    list.set(i, "龙");
                }
            }
        }

        return list;

    }

    /**
     * 计算虎遁（1~9宫）
     *
     * @return 虎遁（如：[虎, , , , , , , , ]）
     */
    private List<String> computeHuDun() {

        /*
            1、天盘[六庚]加人盘[开门]临[兑七宫]。即【庚+兑七宫+开门】
            2、天盘[乙奇(日奇)]加地盘[六辛]合人盘[休门、生门]临[艮八宫]。即【乙+辛+艮八宫+休门、生门】
         */

        List<String> list = CommonUtil.addCharToList(9, "");

        // 1、获取兑七宫信息
        int gongWei = 6; // 兑七宫对应索引值为6
        String tianQinYes = getTianPanQiYiTianQinYes().get(gongWei); // 每一宫位中的天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
        String tianQinNo = getTianPanQiYiTianQinNo().get(gongWei); // 每一宫位中的天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
        String renPan = getRenPan().get(gongWei); // 兑七宫门

        // 2、获取艮八宫信息
        int gongWei2 = 7; // 艮八宫对应索引值为7
        String tianQinYes2 = getTianPanQiYiTianQinYes().get(gongWei); // 每一宫位中的天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
        String tianQinNo2 = getTianPanQiYiTianQinNo().get(gongWei); // 每一宫位中的天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
        String diPan2 = getDiPan().get(gongWei2); // 艮八宫奇仪
        String renPan2 = getRenPan().get(gongWei2); // 艮八宫门

        // 3、判断兑七宫信息是否符合→ 天盘[六庚]加人盘[开门]临[兑七宫]。
        if (("庚".equals(tianQinYes) || "庚".equals(tianQinNo)) && "开门".equals(renPan)) {
            list.set(gongWei, "虎");
        } else {
            // 3.1、判断艮八宫信息是否符合→ 天盘[乙奇(日奇)]加地盘[六辛]合人盘[休门、生门]临[艮八宫]
            if (("乙".equals(tianQinYes2) || "乙".equals(tianQinNo2)) && "辛".equals(diPan2) && ("休门".equals(renPan2) || "生门".equals(renPan2))) {
                list.set(gongWei, "虎");
            }
        }

        return list;

    }

//-------------------------------------------------------------------------------------------------------------------------------

    @Override
    public String toString() {

        return "公历:" + getSolarStr2() + "   " +
                "农历:" + getLunarStr2() + "   " +
                "星期:" + getXingQi() + "   " +
                "季节:" + getJiJie() + "   " +
                "生肖:" + getShengXiao() + "   " +
                "星座:" + getXingZuo() + "   " +
                "月相:" + getYueXiang() + "   " +
                "月将:" + getYueJiang() + "   " +
                "月将神:" + getYueJiangShen() + "   " +
                "五不遇时:" + getWuBuYuShi() + "   " +
                "符头:" + getFuTou() + "   " +
                "节气:" + getJieQi() + getSanYuan() + "   " +
                "局数:" + getYinYangDun() + getJuShu() + "局" + "   " +
                "旬首:" + getXunShou() + "   " +
                "值符:" + getZhiFu() + "   " +
                "值使:" + getZhiShi() + "   " +
                "天乙:" + getTianYi() + "   " +
                "地乙:" + getDiYi() + "   " +
                "太乙:" + getZhiShi() + "   " +
                "地盘:" + getDiPan() + "   " +
                "天盘:" + getTianPan() + "   " +
                "人盘:" + getRenPan() + "   " +
                "神盘:" + getShenPan() + "   " +
                "六仪击刑:" + getLiuYiJiXing() + "   " +
                "奇仪入墓:" + getQiYiRuMu();

    }


}
