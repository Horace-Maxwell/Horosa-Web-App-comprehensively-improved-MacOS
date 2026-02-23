package xuan.core.ziwei;

import java.time.LocalDate;
import java.time.Period;
import java.time.ZoneId;
import java.util.*;

import com.nlf.calendar.JieQi;
import xuan.utils.DateUtil;
import xuan.utils.CommonUtil;
import com.nlf.calendar.Lunar;
import com.nlf.calendar.Solar;
import xuan.core.ziwei.maps.ZiWeiJiChuMap;
import xuan.core.ziwei.utils.ZiWeiJiChuUtil;
import xuan.core.ziwei.settings.ZiWeiJiChuSetting;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;

/**
 * 紫微斗数
 *
 * @author 善待
 */
public class ZiWei {

    /**
     * 紫微斗数 - 基础设置
     */
    private ZiWeiJiChuSetting ziWeiJiChuSetting;

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
     * 命宫宫位
     */
    private int mingGongGongWei;
    /**
     * 身宫宫位
     */
    private int shenGongGongWei;

    /**
     * 五行局
     */
    private String wuXingJu;

    /**
     * 十二个宫位中每个宫位中的诸星
     */
    private List<List<String>> shiErGongZhuXing;
    /**
     * 十二个宫位中每个宫位中的诸星（带标识）
     */
    private List<List<String>> shiErGongZhuXingMark;

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
     * @param ziWeiJiChuSetting 紫微斗数 - 基础设置
     */
    public ZiWei(ZiWeiJiChuSetting ziWeiJiChuSetting) {

        this.ziWeiJiChuSetting = ziWeiJiChuSetting; // 基础设置

        // 1、获取基础设置
        String date = ziWeiJiChuSetting.getDate(); // 日期
        int dateType = ziWeiJiChuSetting.getDateType(); // 日期类型
        int leapMonthType = ziWeiJiChuSetting.getLeapMonthType(); // 闰月类型
        int yearGanZhiType = ziWeiJiChuSetting.getYearGanZhiType(); // 年干支类型
        int monthGanZhiType = ziWeiJiChuSetting.getMonthGanZhiType(); // 月干支类型
        int dayGanZhiType = ziWeiJiChuSetting.getDayGanZhiType(); // 日干支类型

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

    }

    /**
     * 初始化上下节气
     */
    private void initializeShangXiaJieQi() {

        int jieQiType = this.ziWeiJiChuSetting.getJieQiType();

        this.prevJie = this.lunar.getPrevJie(jieQiType == 0); // 上一节
        this.nextJie = this.lunar.getNextJie(jieQiType == 0); // 下一节
        this.prevQi = this.lunar.getPrevQi(jieQiType == 0); // 上一气
        this.nextQi = this.lunar.getNextQi(jieQiType == 0); // 下一气

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
        return this.ziWeiJiChuSetting.getName();
    }

    /**
     * 获取占事
     *
     * @return 占事（如：未填写）
     */
    public String getOccupy() {
        return this.ziWeiJiChuSetting.getOccupy();
    }

    /**
     * 获取性别
     *
     * @return 性别（如：男）
     */
    public String getSex() {
        return this.ziWeiJiChuSetting.getSex() == 0 ? "女" : "男";
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
        if (this.ziWeiJiChuSetting.getXuShiSuiType() == 0) {
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
        return this.ziWeiJiChuSetting.getSex() == 0 ? "坤造" : "乾造";
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

        if (this.ziWeiJiChuSetting.getYearGanZhiType() == 0) {
            return this.lunar.getYearShengXiao(); // 以正月初一起算
        } else if (this.ziWeiJiChuSetting.getYearGanZhiType() == 1) {
            return this.lunar.getYearShengXiaoByLiChun(); // 以立春当天起算
        } else if (this.ziWeiJiChuSetting.getYearGanZhiType() == 2) {
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
        return this.hourGanZhi.equals(ZiWeiJiChuMap.WU_BU_YU_SHI.get(this.dayGan));
    }

    /**
     * 获取男女阴阳
     *
     * @return 男女阴阳（如：阳男）
     */
    public String getNanNvYinYang() {
        return ZiWeiJiChuMap.TIAN_GAN_YIN_YANG.get(getYearGan()) + getSex();
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
        return ZiWeiJiChuMap.TIAN_GAN_WU_XING.get(this.yearGan);
    }

    /**
     * 获取月干五行
     *
     * @return 月干五行（如：木）
     */
    public String getMonthGanWuXing() {
        return ZiWeiJiChuMap.TIAN_GAN_WU_XING.get(this.monthGan);
    }

    /**
     * 获取日干五行
     *
     * @return 日干五行（如：木）
     */
    public String getDayGanWuXing() {
        return ZiWeiJiChuMap.TIAN_GAN_WU_XING.get(this.dayGan);
    }

    /**
     * 获取时干五行
     *
     * @return 时干五行（如：木）
     */
    public String getHourGanWuXing() {
        return ZiWeiJiChuMap.TIAN_GAN_WU_XING.get(this.hourGan);
    }


    /**
     * 获取年支五行
     *
     * @return 年支五行（如：木）
     */
    public String getYearZhiWuXing() {
        return ZiWeiJiChuMap.DI_ZHI_WU_XING.get(this.yearZhi);
    }

    /**
     * 获取月支五行
     *
     * @return 月支五行（如：木）
     */
    public String getMonthZhiWuXing() {
        return ZiWeiJiChuMap.DI_ZHI_WU_XING.get(this.monthZhi);
    }

    /**
     * 获取日支五行
     *
     * @return 日支五行（如：木）
     */
    public String getDayZhiWuXing() {
        return ZiWeiJiChuMap.DI_ZHI_WU_XING.get(this.dayZhi);
    }

    /**
     * 获取时支五行
     *
     * @return 时支五行（如：木）
     */
    public String getHourZhiWuXing() {
        return ZiWeiJiChuMap.DI_ZHI_WU_XING.get(this.hourZhi);
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
        return ZiWeiJiChuMap.NA_YIN.get(this.yearGanZhi);
    }

    /**
     * 获取月干支纳音
     *
     * @return 月干支纳音（如：天上火）
     */
    public String getMonthGanZhiNaYin() {
        return ZiWeiJiChuMap.NA_YIN.get(this.monthGanZhi);
    }

    /**
     * 获取日干支纳音
     *
     * @return 日干支纳音（如：天上火）
     */
    public String getDayGanZhiNaYin() {
        return ZiWeiJiChuMap.NA_YIN.get(this.dayGanZhi);
    }

    /**
     * 获取时干支纳音
     *
     * @return 时干支纳音（如：天上火）
     */
    public String getHourGanZhiNaYin() {
        return ZiWeiJiChuMap.NA_YIN.get(this.hourGanZhi);
    }


    /**
     * 获取年干支空亡
     *
     * @return 年干支空亡（如：子丑）
     */
    public String getYearGanZhiKongWang() {
        return ZiWeiJiChuMap.KONG_WANG.get(this.yearGanZhi);
    }

    /**
     * 获取月干支空亡
     *
     * @return 月干支空亡（如：子丑）
     */
    public String getMonthGanZhiKongWang() {
        return ZiWeiJiChuMap.KONG_WANG.get(this.monthGanZhi);
    }

    /**
     * 获取日干支空亡
     *
     * @return 日干支空亡（如：子丑）
     */
    public String getDayGanZhiKongWang() {
        return ZiWeiJiChuMap.KONG_WANG.get(this.dayGanZhi);
    }

    /**
     * 获取时干支空亡
     *
     * @return 时干支空亡（如：子丑）
     */
    public String getHourGanZhiKongWang() {
        return ZiWeiJiChuMap.KONG_WANG.get(this.hourGanZhi);
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
        return ZiWeiJiChuMap.YUE_JIANG.get(getPrevQi() + getNextQi()).get(0);
    }

    /**
     * 获取月将神
     *
     * @return 月将神（如：神后）
     */
    public String getYueJiangShen() {
        return ZiWeiJiChuMap.YUE_JIANG.get(getPrevQi() + getNextQi()).get(1);
    }


    /**
     * 获取十二宫地支
     *
     * @return 十二宫地支（左下角寅宫为第一宫，依次顺时针旋转排列。如：[寅, 卯, 辰, 巳, 午, 未, 申, 酉, 戌, 亥, 子, 丑]）
     */
    public List<String> getShiErGongDiZhi() {
        return ZiWeiJiChuMap.SHI_ER_GONG_DI_ZHI;
    }

    /**
     * 获取十二宫天干
     *
     * @return 十二宫地支（左下角寅宫为第一宫，依次顺时针旋转排列。如：[甲, 乙, 丙, 丁, 戊, 己, 庚, 辛, 壬, 癸, 甲, 乙]）
     */
    public List<String> getShiErGongTianGan() {

        List<String> list = new ArrayList<>();
        for (int i = 0; i < 12; i++) {
            list.add(ZiWeiJiChuMap.SHI_ER_GONG_TIAN_GAN.get(this.yearGan + getShiErGongDiZhi().get(i)));
        }
        return list;

    }


    /**
     * 获取命宫宫位
     *
     * @return 命宫宫位（如：1）
     */
    public Integer getMingGongGongWei() {

        // 命宫宫位（从出生月落宫起子时，逆时针数，计算命宫落入出生时的宫位）
        int mingGongGongWei = this.lunar.getMonth() > 0 ? this.lunar.getMonth() : -this.lunar.getMonth() + 1;
        for (int i = 0; i < 12; i++) {
            if (!ZiWeiJiChuMap.DI_ZHI[i].equals(getHourZhi())) {
                mingGongGongWei--;
                if (mingGongGongWei == 0) mingGongGongWei = 12; // 若命宫等于0，则重置为第12宫
            } else break;
        }
        this.mingGongGongWei = mingGongGongWei;
        return mingGongGongWei;

    }

    /**
     * 获取身宫宫位
     *
     * @return 身宫宫位（如：1）
     */
    public Integer getShenGongGongWei() {

        // 身宫宫位（从出生月落宫起子时，顺时针数，计算命宫落入出生时的宫位）
        int shenGongGongWei = this.lunar.getMonth() > 0 ? this.lunar.getMonth() : -this.lunar.getMonth() + 1;
        for (int i = 0; i < 12; i++) {
            if (!ZiWeiJiChuMap.DI_ZHI[i].equals(getHourZhi())) {
                shenGongGongWei++;
                if (shenGongGongWei == 13) shenGongGongWei = 1; // 若身宫等于13，则重置为第1宫
            } else break;
        }
        this.shenGongGongWei = shenGongGongWei;
        return shenGongGongWei;

    }


    /**
     * 获取命宫地支
     *
     * @return 命宫地支（如：子）
     */
    public String getMingGongDiZhi() {
        return ZiWeiJiChuMap.GONG_WEI_SHI_ER_GONG_DI_ZHI.get(this.mingGongGongWei == 0 ? getMingGongGongWei() : this.mingGongGongWei);
    }

    /**
     * 获取身宫地支
     *
     * @return 身宫地支（如：子）
     */
    public String getShenGongDiZhi() {
        return ZiWeiJiChuMap.GONG_WEI_SHI_ER_GONG_DI_ZHI.get(this.shenGongGongWei == 0 ? getShenGongGongWei() : this.shenGongGongWei);
    }


    /**
     * 获取十二命宫
     *
     * @return 十二命宫（如：[福德, 田宅, 官禄, 交友, 迁移, 疾厄, 财帛, 子女, 夫妻, 兄弟, 命宫, 父母]）
     */
    public List<String> getShiErMingGong() {

        int mingGongGongWei = this.mingGongGongWei == 0 ? getMingGongGongWei() : this.mingGongGongWei; // 获取命宫宫位
        List<String> shiErMingGong = CommonUtil.addCharToList(12, "");
        shiErMingGong.set(mingGongGongWei - 1, "命宫");
        int index = 0;
        for (int i = mingGongGongWei - 2; i < 12; i--) {
            if (i < 0) i = 11;
            shiErMingGong.set(i, ZiWeiJiChuMap.SHI_ER_GONG[index]);
            index++;
            if (index >= 11) break;
        }

        return shiErMingGong;

    }

    /**
     * 获取十二身宫
     *
     * @return 十二身宫（如：[, , , , , , , , , , 身宫, ]）
     */
    public List<String> getShiErShenGong() {

        int shenGongGongWei = this.shenGongGongWei == 0 ? getShenGongGongWei() : this.shenGongGongWei; // 获取身宫宫位
        List<String> shiErShenGong = CommonUtil.addCharToList(12, "");
        shiErShenGong.set(shenGongGongWei - 1, "身宫");
        return shiErShenGong;

    }


    /**
     * 获取五行局
     *
     * @return 十二身宫（如：木三局）
     */
    public String getWuXingJu() {

        int mingGongGongWei = this.mingGongGongWei == 0 ? getMingGongGongWei() : this.mingGongGongWei; // 获取命宫宫位

        if (this.ziWeiJiChuSetting.getWuXingJuType() == 0) {
            // 按年干+命宫地支计算
            this.wuXingJu = ZiWeiJiChuMap.WU_XING_JU_1.get(this.yearGan + getShiErGongDiZhi().get(mingGongGongWei - 1));
        } else {
            // 按命宫天干+命宫地支计算
            this.wuXingJu = ZiWeiJiChuMap.WU_XING_JU_2.get(getShiErGongTianGan().get(mingGongGongWei - 1) + getShiErGongDiZhi().get(mingGongGongWei - 1));
        }

        return this.wuXingJu;

    }


    /**
     * 获取紫微星宫位
     *
     * @return 紫微星宫位（如：1）
     */
    public Integer getZiWeiXingGongWei() {
        // 通过【农历日+五行局】计算紫微星宫位
        int lunarDay = getLunar().getDay() < 0 ? -getLunar().getDay() : getLunar().getDay(); // 农历月
        return ZiWeiJiChuMap.SHI_ER_GONG_DI_ZHI_GONG_WEI.get(ZiWeiJiChuMap.ZI_WEI_XING_GONG_WEI.get(lunarDay + getWuXingJu()));
    }

    /**
     * 获取天府星宫位
     *
     * @return 天府星宫位（如：1）
     */
    public Integer getTianFuXingGongWei() {
        // 通过【紫微星宫位】计算天府星宫位
        return ZiWeiJiChuMap.SHI_ER_GONG_DI_ZHI_GONG_WEI.get(ZiWeiJiChuMap.TIAN_FU_ZI_WEI.get(ZiWeiJiChuMap.GONG_WEI_SHI_ER_GONG_DI_ZHI.get(getZiWeiXingGongWei())));
    }


    /**
     * 获取紫微星宫位地支
     *
     * @return 紫微星宫位（如：子）
     */
    public String getZiWeiXingGongDiZhi() {
        return ZiWeiJiChuMap.GONG_WEI_SHI_ER_GONG_DI_ZHI.get(getZiWeiXingGongWei());
    }

    /**
     * 获取天府星宫位地支
     *
     * @return 天府星宫位地支（如：子）
     */
    public String getTianFuXingGongDiZhi() {
        return ZiWeiJiChuMap.GONG_WEI_SHI_ER_GONG_DI_ZHI.get(getTianFuXingGongWei());
    }


    /**
     * 获取紫微星系诸星
     *
     * @return 紫微星系诸星（如：[武曲, 太阳, , 天机, 紫微, , , , 廉贞, , , 天同]）
     */
    public List<String> getZiWeiXingXiZhuXing() {
        return ZiWeiJiChuMap.ZI_WEI_XING_XING_XI_ZHU_XING.get(getZiWeiXingGongDiZhi());
    }

    /**
     * 获取天府星系诸星
     *
     * @return 天府星系诸星（如：[天相, 天梁, 七杀, , , , 破军, , 天府, 太阴, 贪狼, 巨门]）
     */
    public List<String> getTianFuXingXiZhuXing() {
        return ZiWeiJiChuMap.TIAN_FU_XING_XING_XI_ZHU_XING.get(getTianFuXingGongDiZhi());
    }

    /**
     * 获取时支诸星
     *
     * @return 时支诸星（如：[封诰, , 文曲, , 台辅, , , 火星, 文昌_铃星, 地劫_地空, , ]）
     */
    public List<String> getShiZhiZhuXing() {
        return ZiWeiJiChuMap.SHI_ZHI_ZHU_XING.get(this.hourZhi + this.yearZhi);
    }

    /**
     * 获取月支诸星
     *
     * @return 月支诸星（如：[左辅_天马_天巫, , , , 解神_阴煞, 天邢, , , 天月, 天姚, 右弼, ]）
     */
    public List<String> getYueZhiZhuXing() {
        return ZiWeiJiChuMap.YUE_ZHI_ZHU_XING.get(this.monthZhi);
    }

    /**
     * 获取年干诸星
     *
     * @return 年干诸星（如：[, 天魁, , 天钺_天福, 天官, , , , , 陀罗, 禄存, 擎羊]）
     */
    public List<String> getNianGanZhuXing() {
        return ZiWeiJiChuMap.NIAN_GAN_ZHU_XING.get(this.yearGan);
    }

    /**
     * 获取年支诸星
     *
     * @return 年支诸星（如：[, 天哭_天寿, 天空, 蜚廉_破碎_孤辰, 天喜, 龙池_凤阁, , 天虚, , , 红鸾, 寡宿]）
     */
    public List<String> getNianZhiZhuXing() {

        String[] diZhi = ZiWeiJiChuMap.DI_ZHI; // 十二地支
        Map<String, List<String>> nianZhiZhuXingMap = ZiWeiJiChuMap.NIAN_ZHI_ZHU_XING; // 年支诸星（年支为键）
        Map<String, String> nianZhiTianCaiXingGongWeiMap = ZiWeiJiChuMap.NIAN_ZHI_TIAN_CAI_XING_GONG_WEI; // 年支诸星之天才星十二宫位名称（年支为键）

        List<String> nianZhiZhuXing; // 年支诸星

        // 1、计算天空星、天哭星、天虚星、龙池星、凤阁星、红鸾星、天喜星、蜚廉星、破碎星、孤辰星、寡宿星
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            String jsonString = objectMapper.writeValueAsString(nianZhiZhuXingMap.get(this.yearZhi));
            nianZhiZhuXing = objectMapper.readValue(jsonString, objectMapper.getTypeFactory().constructCollectionType(List.class, String.class));
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }

        // 2、计算天才星
        String tianCaiXingGongName = nianZhiTianCaiXingGongWeiMap.get(this.yearZhi); // 天才星落入十二命宫的宫位名称（例如：命宫）
        List<String> shiErMingGong = getShiErMingGong(); // 获取十二命宫
        for (int i = 0; i < shiErMingGong.size(); i++) {
            if (tianCaiXingGongName.equals(shiErMingGong.get(i))) {
                // 若宫位中存在星则追加数据
                String oneGongXing = nianZhiZhuXing.get(i);
                if ("".equals(oneGongXing)) {
                    nianZhiZhuXing.set(i, oneGongXing + "天才");
                } else {
                    nianZhiZhuXing.set(i, oneGongXing + "_天才");
                }
                break;
            }
        }

        // 3、计算天寿星（由身宫起子顺排至年支宫位）
        for (int i = 0; i < diZhi.length; i++) {
            if (getYearZhi().equals(diZhi[i])) {
                // 计算从子到年支的个数
                int shenGongGongWei = this.shenGongGongWei == 0 ? getShenGongGongWei() : this.shenGongGongWei; // 获取身宫宫位
                int gongWei = shenGongGongWei + i > 12 ? shenGongGongWei + i - 12 : shenGongGongWei + i;
                // 若宫位中存在星则追加数据
                String oneGongXing = nianZhiZhuXing.get(gongWei - 1);
                if ("".equals(oneGongXing)) {
                    nianZhiZhuXing.set(gongWei - 1, "天寿");
                } else {
                    nianZhiZhuXing.set(gongWei - 1, oneGongXing + "_天寿");
                }
                break;
            }
        }

        return nianZhiZhuXing;

    }

    /**
     * 获取日诸星
     *
     * @return 日诸星（如：[, , 恩光, 八座, , , , 三台, 天贵, , , ]）
     */
    public List<String> getDayZhuXing() {

        // 1、计算农历出生日距初一共有多少天
        int days = this.lunar.getDay() - 1;

        // 2、计算三台星（从左辅星落宫起初一，顺排至农历出生日）
        int zuoFuXingGongWei = ZiWeiJiChuUtil.getXingWeiGongWei(getYueZhiZhuXing(), "左辅"); // 计算左辅星宫位
        int sanTaiXingGongWei = zuoFuXingGongWei + days; // 三台星宫位
        while (true) {
            if (sanTaiXingGongWei > 12) {
                sanTaiXingGongWei -= 12;
            } else break;
        }

        // 3、计算八座星（从右弼星落宫起初一，逆排至农历出生日）
        int youBiXingGongWei = ZiWeiJiChuUtil.getXingWeiGongWei(getYueZhiZhuXing(), "右弼"); // 计算右弼星宫位
        int baZuoXingGongWei = youBiXingGongWei - days; // 八座星宫位
        while (true) {
            if (baZuoXingGongWei < 0) {
                baZuoXingGongWei += 12;
            } else break;
        }
        baZuoXingGongWei = baZuoXingGongWei == 0 ? 1 : baZuoXingGongWei;

        // 4、计算恩光星（从文昌星落宫起初一，顺排至农历出生日，再后退一个宫位）
        int wenChangXingGongWei = ZiWeiJiChuUtil.getXingWeiGongWei(getShiZhiZhuXing(), "文昌"); // 计算文昌星宫位
        int enGuangXingGongWei = wenChangXingGongWei + days; // 恩光星宫位
        while (true) {
            if (enGuangXingGongWei > 12) {
                enGuangXingGongWei -= 12;
            } else break;
        }
        enGuangXingGongWei = enGuangXingGongWei - 1 == 0 ? 12 : enGuangXingGongWei - 1;

        // 5、计算天贵星（从文曲星落宫起初一，顺排至农历出生日，再后退一个宫位）
        int wenQuXingGongWei = ZiWeiJiChuUtil.getXingWeiGongWei(getShiZhiZhuXing(), "文曲"); // 计算文曲星宫位
        int tianGuiXingGongWei = wenQuXingGongWei + days; // 天贵星宫位
        while (true) {
            if (tianGuiXingGongWei > 12) {
                tianGuiXingGongWei -= 12;
            } else break;
        }
        tianGuiXingGongWei = tianGuiXingGongWei - 1 == 0 ? 12 : tianGuiXingGongWei - 1;

        // 6、添加日诸星并返回
        List<String> riZhuXing = CommonUtil.addCharToList(12, "");
        riZhuXing.set(sanTaiXingGongWei - 1, "三台");
        riZhuXing.set(baZuoXingGongWei - 1, "八座");
        riZhuXing.set(enGuangXingGongWei - 1, "恩光");
        riZhuXing.set(tianGuiXingGongWei - 1, "天贵");
        return riZhuXing;

    }

    /**
     * 获取十二长生
     *
     * @return 十二长生（如：[临官, 冠带, 沐浴, 长生, 养, 胎, 绝, 墓, 死, 病, 衰, 帝旺]）
     */
    public List<String> getShiErZhangSheng() {

        String yinYang = getNanNvYinYang();
        if ("阳女".equals(yinYang)) {
            yinYang = "阴男";
        } else if ("阴女".equals(yinYang)) {
            yinYang = "阳男";
        }
        return ZiWeiJiChuMap.SHI_ER_ZHANG_SHENG.get(yinYang + getWuXingJu());

    }

    /**
     * 获取截路空亡
     *
     * @return 截路空亡（如：[, , , , , , , , , , , 截路]）
     */
    public List<String> getJieLuKongWang() {

        int luoGong = ZiWeiJiChuMap.SHI_ER_GONG_DI_ZHI_GONG_WEI.get(ZiWeiJiChuMap.JIE_LU_KONG_WANG.get(this.yearGan));
        List<String> jieLuKongWang = CommonUtil.addCharToList(12, "");
        jieLuKongWang.set(luoGong - 1, "截路");
        return jieLuKongWang;

    }

    /**
     * 获取旬中空亡
     *
     * @return 旬中空亡（如：[, , 旬空, 副旬, , , , , , , , ]）
     */
    public List<String> getXunZhongKongWang() {

        List<String> kongWang = ZiWeiJiChuMap.XUN_ZHONG_KONG_WANG.get(getYearGan() + getYearZhi());
        int kongWangLuoGong1 = ZiWeiJiChuMap.SHI_ER_GONG_DI_ZHI_GONG_WEI.get(kongWang.get(0)); // 旬中空亡落宫1
        int kongWangLuoGong2 = ZiWeiJiChuMap.SHI_ER_GONG_DI_ZHI_GONG_WEI.get(kongWang.get(1)); // 旬中空亡落宫2
        List<String> xunZhongKongWang = CommonUtil.addCharToList(12, "");
        xunZhongKongWang.set(kongWangLuoGong1 - 1, "旬空");
        xunZhongKongWang.set(kongWangLuoGong2 - 1, "副旬");
        return xunZhongKongWang;

    }

    /**
     * 获取天伤星、天使星
     *
     * @return 天伤星、天使星（如：[, , , 天伤, , 天使, , , , , , ]）
     */
    public List<String> getTianShangTianShiXing() {

        List<String> kongWang = ZiWeiJiChuMap.TIAN_SHANG_TIAN_SHI_XING_GONG_WEI.get(getMingGongDiZhi());
        int kongWangLuoGong1 = ZiWeiJiChuMap.SHI_ER_GONG_DI_ZHI_GONG_WEI.get(kongWang.get(0)); // 天伤星落宫
        int kongWangLuoGong2 = ZiWeiJiChuMap.SHI_ER_GONG_DI_ZHI_GONG_WEI.get(kongWang.get(1)); // 天使星落宫
        List<String> tianShangTianShiXing = CommonUtil.addCharToList(12, "");
        tianShangTianShiXing.set(kongWangLuoGong1 - 1, "天伤");
        tianShangTianShiXing.set(kongWangLuoGong2 - 1, "天使");
        return tianShangTianShiXing;

    }

    /**
     * 获取大限
     *
     * @return 大限（如：[104-113, 94-103, 84-93, 74-83, 64-73, 54-63, 44-53, 34-43, 24-33, 14-23, 4-13, 114-123]）
     */
    public List<String> getDaXian() {

        String yinYang = getNanNvYinYang();
        if ("阳女".equals(yinYang)) {
            yinYang = "阴男";
        } else if ("阴女".equals(yinYang)) {
            yinYang = "阳男";
        }

        // 从命宫宫位依次向后添加大限
        List<String> daXian = CommonUtil.addCharToList(12, "");
        int luCunXingGongWei = (this.mingGongGongWei == 0 ? getMingGongGongWei() : this.mingGongGongWei) - 1; // 数组索引是从0开始。此处需减1
        for (int i = 0; i < 12; i++) {
            daXian.set(luCunXingGongWei, ZiWeiJiChuMap.DA_XIAN.get(yinYang + getWuXingJu()).get(i));
            luCunXingGongWei++;
            if (luCunXingGongWei > 11) luCunXingGongWei = 0;
        }

        return daXian;

    }

    /**
     * 获取小限
     *
     * @return 小限（如：[2,14,26,38,50,62, 3,15,27,39,51,63, 4,16,28,40,52,64, 5,17,29,41,53,65, 6,18,30,42,54,66, 7,19,31,43,55,67, 8,20,32,44,56,68, 9,21,33,45,57,69, 10,22,34,46,58,70, 11,23,35,47,59,71, 12,24,36,48,60,72, 1,13,25,37,49,61]）
     */
    public List<String> getXiaoXian() {
        return ZiWeiJiChuMap.XIAO_XIAN.get(this.yearZhi + getSex());
    }

    /**
     * 获取十二宫博士
     *
     * @return 十二宫博士（如：[伏兵, 大耗, 病符, 喜神, 飞廉, 奏书, 将军, 小耗, 青龙, 力士, 博士, 官府]）
     */
    public List<String> getShiErGongBoShi() {

        String[] shiErGongBoShiShun = ZiWeiJiChuMap.SHI_ER_GONG_BO_SHI_SHUN; // 十二宫博士

        //从禄存星起博士，阳男阴女顺排、阴男阳女逆排
        int luCunXingGongWei = ZiWeiJiChuUtil.getXingWeiGongWei(getNianGanZhuXing(), "禄存"); // 计算禄存星宫位

        List<String> shiErGongBoShi = CommonUtil.addCharToList(12, "");

        luCunXingGongWei -= 1; // 数组索引是从0开始。此处需减1
        if ("阳男".equals(getNanNvYinYang()) || "阴女".equals(getNanNvYinYang())) {
            // 阳男阴女顺排
            for (int i = 0; i < 12; i++) {
                shiErGongBoShi.set(luCunXingGongWei, shiErGongBoShiShun[i]);
                luCunXingGongWei++;
                if (luCunXingGongWei > 11) luCunXingGongWei = 0;
            }
        } else if ("阴男".equals(getNanNvYinYang()) || "阳女".equals(getNanNvYinYang())) {
            // 阴男阳女逆排
            for (int i = 0; i < 12; i++) {
                shiErGongBoShi.set(luCunXingGongWei, shiErGongBoShiShun[i]);
                luCunXingGongWei--;
                if (luCunXingGongWei < 0) luCunXingGongWei = 11;
            }
        }

        return shiErGongBoShi;

    }

    /**
     * 获取流年岁前诸星（不再考虑流年支）
     *
     * @return 流年岁前诸星（如：[病符, 岁建, 晦气, 丧门, 贯索, 官符, 小耗, 大耗, 龙德, 白虎, 天德, 吊客]）
     */
    public List<String> getLiuNianSuiQianZhuXing() {
        return ZiWeiJiChuMap.LIU_NIAN_SUI_QIAN_ZHU_XING.get(this.yearZhi);
    }

    /**
     * 获取流年将前诸星（不再考虑流年支）
     *
     * @return 流年将前诸星（如：[亡神, 将星, 攀鞍, 岁驿, 息神, 华盖, 劫煞, 灾煞, 天煞, 指背, 咸池, 月煞]）
     */
    public List<String> getLiuNianJiangQianZhuXing() {
        return ZiWeiJiChuMap.LIU_NIAN_JIANG_QIAN_ZHU_XING.get(this.yearZhi);
    }


    /**
     * 获取十二个宫位中每个宫位中的诸星
     *
     * @param isMark 是否带标识（true:是。false:否）
     * @return 十二个宫位中每个宫位中的诸星
     */
    public List<List<String>> getShiErGongZhuXing(boolean isMark) {

        List<List<String>> shiErGongZhuXing = new ArrayList<>(); // 保存十二个宫位中的诸星
        List<List<String>> shiErGongZhuXingMark = new ArrayList<>(); // 保存十二个宫位中的诸星（带标识）

        // 1、添加诸星
        for (int i = 0; i < 12; i++) {
            List<String> oneGongZhuXing = new ArrayList<>(); // 保存每一个宫位中的诸星
            List<String> oneGongZhuXingMark = new ArrayList<>(); // 保存每一个宫位中的诸星（带标识）
            // 1.1、添加每一个宫位中的紫微星系诸星
            List<String> ziWeiXingXiZhuXing = getZiWeiXingXiZhuXing();
            if (!"".equals(ziWeiXingXiZhuXing.get(i))) {
                oneGongZhuXing.add(ziWeiXingXiZhuXing.get(i));
                oneGongZhuXingMark.add("1_" + ziWeiXingXiZhuXing.get(i));
            }
            // 1.2、添加每一个宫位中的天府星系诸星
            List<String> tianFuXingXiZhuXing = getTianFuXingXiZhuXing();
            if (!"".equals(tianFuXingXiZhuXing.get(i))) {
                oneGongZhuXing.add(tianFuXingXiZhuXing.get(i));
                oneGongZhuXingMark.add("2_" + tianFuXingXiZhuXing.get(i));
            }
            // 1.3、添加每一个宫位中的时支诸星
            List<String> shiZhiZhuXing = getShiZhiZhuXing();
            ZiWeiJiChuUtil.addZhuXing(shiZhiZhuXing, oneGongZhuXing, i, "");
            ZiWeiJiChuUtil.addZhuXing(shiZhiZhuXing, oneGongZhuXingMark, i, "3_");
            // 1.4、添加每一个宫位中的月支诸星
            List<String> yueZhiZhuXing = getYueZhiZhuXing();
            ZiWeiJiChuUtil.addZhuXing(yueZhiZhuXing, oneGongZhuXing, i, "");
            ZiWeiJiChuUtil.addZhuXing(yueZhiZhuXing, oneGongZhuXingMark, i, "4_");
            // 1.5、添加每一个宫位中的年干诸星
            List<String> nianGanZhuXing = getNianGanZhuXing();
            ZiWeiJiChuUtil.addZhuXing(nianGanZhuXing, oneGongZhuXing, i, "");
            ZiWeiJiChuUtil.addZhuXing(nianGanZhuXing, oneGongZhuXingMark, i, "5_");
            // 1.6、添加每一个宫位中的年支诸星
            List<String> nianZhiZhuXing = getNianZhiZhuXing();
            ZiWeiJiChuUtil.addZhuXing(nianZhiZhuXing, oneGongZhuXing, i, "");
            ZiWeiJiChuUtil.addZhuXing(nianZhiZhuXing, oneGongZhuXingMark, i, "6_");
            // 1.7、添加每一个宫位中的日诸星
            List<String> dayZhuXing = getDayZhuXing();
            if (!"".equals(dayZhuXing.get(i))) {
                oneGongZhuXing.add(dayZhuXing.get(i));
                oneGongZhuXingMark.add("7_" + dayZhuXing.get(i));
            }
            // 1.8、添加每一个宫位中的日诸星
            List<String> tianShangTianShiXing = getTianShangTianShiXing();
            if (!"".equals(tianShangTianShiXing.get(i))) {
                oneGongZhuXing.add(tianShangTianShiXing.get(i));
                oneGongZhuXingMark.add("8_" + tianShangTianShiXing.get(i));
            }
            // 1.9、添加每一个宫位中的截路空亡
            List<String> jieLuKongWang = getJieLuKongWang();
            if (!"".equals(jieLuKongWang.get(i))) {
                oneGongZhuXing.add(jieLuKongWang.get(i));
                oneGongZhuXingMark.add("9_" + jieLuKongWang.get(i));
            }
            // 1.10、添加每一个宫位中的旬中空亡
            List<String> xunZhongKongWang = getXunZhongKongWang();
            if (!"".equals(xunZhongKongWang.get(i))) {
                oneGongZhuXing.add(xunZhongKongWang.get(i));
                oneGongZhuXingMark.add("10_" + xunZhongKongWang.get(i));
            }
            shiErGongZhuXing.add(oneGongZhuXing); // 添加每一个宫位中全部诸星
            shiErGongZhuXingMark.add(oneGongZhuXingMark); // 添加每一个宫位中全部诸星（带标识）
        }

        this.shiErGongZhuXing = shiErGongZhuXing;
        this.shiErGongZhuXingMark = shiErGongZhuXingMark;

        if (isMark) {
            return shiErGongZhuXingMark; // 十二个宫位中每个宫位中的诸星（带标识）
        } else {
            return shiErGongZhuXing; // 十二个宫位中每个宫位中的诸星
        }

    }

    /**
     * 获取十二个宫位中每个宫位中的诸星庙旺平陷关系
     *
     * @return 十二个宫位中每个宫位中的诸星庙旺平陷关系
     */
    public List<List<String>> getShiErGongZhuXingGuanXi() {

        Map<String, List<String>> zhuXingGuanXiMap = ZiWeiJiChuMap.ZHU_XING_GUAN_XI; // 诸星庙旺平陷关系（诸星为键）

        List<List<String>> shiErGongZhuXingGuanXi = new ArrayList<>(); // 保存十二个宫位中的诸星关系
        List<List<String>> shiErGongZhuXing = (null != this.shiErGongZhuXing) ? this.shiErGongZhuXing : getShiErGongZhuXing(false); // 十二个宫位中每个宫位中的诸星
        for (int i = 0; i < 12; i++) {
            List<String> oneGongZhuXingGuanXi = new ArrayList<>(); // 保存每一个宫位中的诸星关系
            List<String> oneGongXing = shiErGongZhuXing.get(i); // 每一个宫位中的诸星
            for (String item : oneGongXing) {
                if (null != zhuXingGuanXiMap.get(item)) {
                    oneGongZhuXingGuanXi.add(zhuXingGuanXiMap.get(item).get(i));
                } else if ("".equals(zhuXingGuanXiMap.get(item).get(i))) {
                    oneGongZhuXingGuanXi.add("~");
                } else {
                    oneGongZhuXingGuanXi.add("~");
                }
            }
            shiErGongZhuXingGuanXi.add(oneGongZhuXingGuanXi);
        }

        return shiErGongZhuXingGuanXi;

    }


    /**
     * 获取化禄星宫位
     *
     * @return 化禄星宫位（如：1）
     */
    public Integer getHuaLuXingGongWei() {

        List<List<String>> shiErGongZhuXing = (null != this.shiErGongZhuXing) ? this.shiErGongZhuXing : getShiErGongZhuXing(false); // 十二个宫位中每个宫位中的诸星
        for (int i = 0; i < 12; i++) {
            List<String> oneZhuXing = shiErGongZhuXing.get(i);
            for (String item : oneZhuXing) {
                if (item.equals(ZiWeiJiChuMap.SI_HUA_GONG_WEI.get(getYearGan()).get(0))) return i + 1;
            }
        }
        return 1;

    }

    /**
     * 获取化权星宫位
     *
     * @return 化权星宫位（如：1）
     */
    public Integer getHuaQuanXingGongWei() {

        List<List<String>> shiErGongZhuXing = (null != this.shiErGongZhuXing) ? this.shiErGongZhuXing : getShiErGongZhuXing(false); // 十二个宫位中每个宫位中的诸星
        for (int i = 0; i < 12; i++) {
            List<String> oneZhuXing = shiErGongZhuXing.get(i);
            for (String item : oneZhuXing) {
                if (item.equals(ZiWeiJiChuMap.SI_HUA_GONG_WEI.get(getYearGan()).get(1))) return i + 1;
            }
        }
        return 1;

    }

    /**
     * 获取化科星宫位
     *
     * @return 化科星宫位（如：1）
     */
    public Integer getHuaKeXingGongWei() {

        List<List<String>> shiErGongZhuXing = (null != this.shiErGongZhuXing) ? this.shiErGongZhuXing : getShiErGongZhuXing(false); // 十二个宫位中每个宫位中的诸星
        for (int i = 0; i < 12; i++) {
            List<String> oneZhuXing = shiErGongZhuXing.get(i);
            for (String item : oneZhuXing) {
                if (item.equals(ZiWeiJiChuMap.SI_HUA_GONG_WEI.get(getYearGan()).get(2))) return i + 1;
            }
        }
        return 1;

    }

    /**
     * 获取化忌星宫位
     *
     * @return 化忌星宫位（如：1）
     */
    public Integer getHuaJiXingGongWei() {

        List<List<String>> shiErGongZhuXing = (null != this.shiErGongZhuXing) ? this.shiErGongZhuXing : getShiErGongZhuXing(false); // 十二个宫位中每个宫位中的诸星
        for (int i = 0; i < 12; i++) {
            List<String> oneZhuXing = shiErGongZhuXing.get(i);
            for (String item : oneZhuXing) {
                if (item.equals(ZiWeiJiChuMap.SI_HUA_GONG_WEI.get(getYearGan()).get(3))) return i + 1;
            }
        }
        return 1;

    }


    /**
     * 计算化禄星宫位解读
     *
     * @return 化禄星宫位解读
     */
    public String getHuaLuXingGongWeiJieDu() {
        String huaLuLuoGong = getShiErMingGong().get(getHuaLuXingGongWei() - 1); // 化禄星落宫
        return "化禄星落" + huaLuLuoGong + "宫，" + ZiWeiJiChuMap.SI_HUA_XING_SHI_ER_GONG.get("禄" + huaLuLuoGong);
    }

    /**
     * 计算化权星宫位解读
     *
     * @return 化权星宫位解读
     */
    public String getHuaQuanXingGongWeiJieDu() {
        String huaLuLuoGong = getShiErMingGong().get(getHuaQuanXingGongWei() - 1); // 化禄星落宫
        return "化权星落" + huaLuLuoGong + "宫，" + ZiWeiJiChuMap.SI_HUA_XING_SHI_ER_GONG.get("权" + huaLuLuoGong);
    }

    /**
     * 计算化科星宫位解读
     *
     * @return 化科星宫位解读
     */
    public String getHuaKeXingGongWeiJieDu() {
        String huaLuLuoGong = getShiErMingGong().get(getHuaKeXingGongWei() - 1); // 化禄星落宫
        return "化科星落" + huaLuLuoGong + "宫，" + ZiWeiJiChuMap.SI_HUA_XING_SHI_ER_GONG.get("科" + huaLuLuoGong);
    }

    /**
     * 计算化忌星宫位解读
     *
     * @return 化忌星宫位解读
     */
    public String getHuaJiXingGongWeiJieDu() {
        String huaLuLuoGong = getShiErMingGong().get(getHuaJiXingGongWei() - 1); // 化禄星落宫
        return "化忌星落" + huaLuLuoGong + "宫，" + ZiWeiJiChuMap.SI_HUA_XING_SHI_ER_GONG.get("忌" + huaLuLuoGong);
    }


    /**
     * 获取十二个宫位中每个宫位中的四化星
     *
     * @return 十二个宫位中每个宫位中的四化星
     */
    public List<List<String>> getShiErGongSiHuaXing() {

        List<String> siHuaList = ZiWeiJiChuMap.SI_HUA_GONG_WEI.get(getYearGan()); // 四化星宫位（年干为键）
        Map<String, List<String>> zhuXingGuanXiMap = ZiWeiJiChuMap.ZHU_XING_GUAN_XI; // 诸星庙旺平陷关系（诸星为键）

        List<List<String>> siHuaXing = new ArrayList<>(); // 保存全部宫位中的四化星
        List<List<String>> shiErGongZhuXing = (null != this.shiErGongZhuXing) ? this.shiErGongZhuXing : getShiErGongZhuXing(false); // 十二个宫位中每个宫位中的诸星
        for (int i = 0; i < 12; i++) {
            List<String> oneSiHuaXing = new ArrayList<>(); // 保存每一宫位中的四化星
            List<String> oneZhuXing = shiErGongZhuXing.get(i); // 每一个宫位中的诸星
            for (String item : oneZhuXing) {
                if (item.equals(siHuaList.get(0))) oneSiHuaXing.add("禄"); // 化禄星
                if (item.equals(siHuaList.get(1))) oneSiHuaXing.add("权"); // 化权星
                if (item.equals(siHuaList.get(2))) oneSiHuaXing.add("科"); // 化科星
                if (item.equals(siHuaList.get(3))) oneSiHuaXing.add("忌"); // 化忌星
            }
            siHuaXing.add(oneSiHuaXing);
        }

        return siHuaXing;

    }

    /**
     * 获取十二个宫位中每个宫位中的四化星庙旺平陷关系
     *
     * @return 十二个宫位中每个宫位中的四化星庙旺平陷关系
     */
    public List<List<String>> getShiErGongSiHuaXingGuanXi() {

        List<String> siHuaList = ZiWeiJiChuMap.SI_HUA_GONG_WEI.get(getYearGan()); // 四化星宫位（年干为键）
        Map<String, List<String>> zhuXingGuanXiMap = ZiWeiJiChuMap.ZHU_XING_GUAN_XI; // 诸星庙旺平陷关系（诸星为键）

        List<List<String>> siHuaXingGuanXi = new ArrayList<>(); // 保存全部宫位中的四化星庙旺平陷关系
        List<List<String>> shiErGongZhuXing = (null != this.shiErGongZhuXing) ? this.shiErGongZhuXing : getShiErGongZhuXing(false); // 十二个宫位中每个宫位中的诸星
        for (int i = 0; i < 12; i++) {
            List<String> oneSiHuaXingGuanXi = new ArrayList<>(); // 保存每一宫位中的四化星庙旺平陷关系
            List<String> oneZhuXing = shiErGongZhuXing.get(i); // 每一个宫位中的诸星
            for (String item : oneZhuXing) {
                if (item.equals(siHuaList.get(0))) oneSiHuaXingGuanXi.add(zhuXingGuanXiMap.get("禄").get(i)); // 化禄星
                if (item.equals(siHuaList.get(1))) oneSiHuaXingGuanXi.add(zhuXingGuanXiMap.get("权").get(i)); // 化权星
                if (item.equals(siHuaList.get(2))) oneSiHuaXingGuanXi.add(zhuXingGuanXiMap.get("科").get(i)); // 化科星
                if (item.equals(siHuaList.get(3))) oneSiHuaXingGuanXi.add(zhuXingGuanXiMap.get("忌").get(i)); // 化忌星
            }
            siHuaXingGuanXi.add(oneSiHuaXingGuanXi);
        }

        return siHuaXingGuanXi;

    }


    /**
     * 获取命主
     *
     * @return 命主（如：文曲）
     */
    public String getMingZhu() {
        return ZiWeiJiChuMap.MING_ZHU.get(getMingGongDiZhi());
    }

    /**
     * 获取身主
     *
     * @return 身主（如：天机）
     */
    public String getShenZhu() {
        return ZiWeiJiChuMap.SHEN_ZHU.get(this.yearZhi);
    }

    /**
     * 获取子斗
     *
     * @return 子斗（如：子）
     */
    public String getZiDou() {
        return ZiWeiJiChuMap.ZI_DOU.get(this.monthZhi + this.hourZhi);
    }

    /**
     * 获取流斗
     *
     * @return 流斗（如：子）
     */
    public String getLiuDou() {

        int ziDouGongWei = ZiWeiJiChuMap.SHI_ER_GONG_DI_ZHI_GONG_WEI.get(getZiDou()); // 获取子斗宫位

        // 从子斗宫位起子，顺数至年支
        for (int i = 0; i < 12; i++) {
            if (!ZiWeiJiChuMap.DI_ZHI[i].equals(this.yearZhi)) {
                ziDouGongWei++;
                if (ziDouGongWei > 12) ziDouGongWei = 1;
            } else break;
        }

        return ZiWeiJiChuMap.GONG_WEI_SHI_ER_GONG_DI_ZHI.get(ziDouGongWei);

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
                "五行局:" + getWuXingJu() + "   " +
                "化禄星宫位解读:" + getHuaLuXingGongWeiJieDu() + "   " +
                "化权星宫位解读:" + getHuaQuanXingGongWeiJieDu() + "   " +
                "化科星宫位解读:" + getHuaKeXingGongWeiJieDu() + "   " +
                "化忌星宫位解读:" + getHuaJiXingGongWeiJieDu();

    }


}
