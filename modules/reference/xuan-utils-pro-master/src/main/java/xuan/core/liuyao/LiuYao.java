package xuan.core.liuyao;

import java.time.LocalDate;
import java.time.Period;
import java.time.ZoneId;
import java.util.*;

import com.nlf.calendar.JieQi;
import xuan.utils.DateUtil;
import xuan.utils.CommonUtil;
import com.nlf.calendar.Lunar;
import com.nlf.calendar.Solar;
import xuan.core.liuyao.maps.LiuYaoJiChuMap;
import xuan.core.liuyao.utils.LiuYaoJiChuUtil;
import xuan.core.liuyao.utils.LiuYaoShenShaUtil;
import xuan.core.liuyao.settings.LiuYaoJiChuSetting;
import xuan.core.liuyao.settings.LiuYaoShenShaSetting;

/**
 * 六爻
 *
 * @author 善待
 */
public class LiuYao {

    /**
     * 六爻 - 基础设置
     */
    private LiuYaoJiChuSetting liuYaoJiChuSetting;
    /**
     * 六爻 - 神煞设置
     */
    private LiuYaoShenShaSetting liuYaoShenShaSetting = new LiuYaoShenShaSetting();

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
     * 初始六爻爻象（如：[—, - -, - -, - -, - -, —]）
     */
    private List<String> liuYaoAs;
    /**
     * 初始六爻爻象标识（如：[○, ×, , ×, , ]）
     */
    private List<String> liuYaoAsMark;
    /**
     * 初始六爻爻象标识名称（如：[老阳, 老阴, 少阴, 老阴, 少阴, 少阳]）
     */
    private List<String> liuYaoAsMarkName;

    /**
     * 变卦六爻爻象（如：[- -, —, - -, —, - -, —]）
     */
    private List<String> bianGuaLiuYaoAs;

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
     * @param liuYaoJiChuSetting 六爻 - 基础设置
     */
    public LiuYao(LiuYaoJiChuSetting liuYaoJiChuSetting) {

        this.liuYaoJiChuSetting = liuYaoJiChuSetting; // 基础设置

        // 1、获取基础设置
        String date = liuYaoJiChuSetting.getDate(); // 日期
        int dateType = liuYaoJiChuSetting.getDateType(); // 日期类型
        int leapMonthType = liuYaoJiChuSetting.getLeapMonthType(); // 闰月类型
        int yearGanZhiType = liuYaoJiChuSetting.getYearGanZhiType(); // 年干支类型
        int monthGanZhiType = liuYaoJiChuSetting.getMonthGanZhiType(); // 月干支类型
        int dayGanZhiType = liuYaoJiChuSetting.getDayGanZhiType(); // 日干支类型

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
        initializeLiuYaoData(liuYaoJiChuSetting); // 初始化六爻爻象、六爻爻象标识、六爻爻象标识名称

    }

    /**
     * 神煞设置（可选）
     * <p>
     * <hr/>
     * 可选，若不设置则使用默认值，详情请在设置中查看
     */
    public void liuYaoShenShaSetting(LiuYaoShenShaSetting liuYaoShenShaSetting) {
        this.liuYaoShenShaSetting = liuYaoShenShaSetting;
    }

    /**
     * 初始化上下节气
     */
    private void initializeShangXiaJieQi() {

        int jieQiType = this.liuYaoJiChuSetting.getJieQiType();

        this.prevJie = this.lunar.getPrevJie(jieQiType == 0); // 上一节
        this.nextJie = this.lunar.getNextJie(jieQiType == 0); // 下一节
        this.prevQi = this.lunar.getPrevQi(jieQiType == 0); // 上一气
        this.nextQi = this.lunar.getNextQi(jieQiType == 0); // 下一气

    }

    /**
     * 初始化六爻爻象、六爻爻象标识、六爻爻象标识名称
     *
     * @param liuYaoJiChuSetting 六爻 - 基础设置
     */
    protected void initializeLiuYaoData(LiuYaoJiChuSetting liuYaoJiChuSetting) {

        // 1、计算初始六爻爻象、六爻爻象标识、六爻爻象标识名称（★可用于排盘模式扩展）
        Map<String, List<String>> map = LiuYaoJiChuUtil.getLiuYaoData(liuYaoJiChuSetting, this.lunar, this.yearZhi, this.hourZhi);
        this.liuYaoAs = map.get("liuYaoAs"); // 六爻爻象
        this.liuYaoAsMark = map.get("liuYaoAsMark"); // 六爻爻象标识
        this.liuYaoAsMarkName = map.get("liuYaoAsMarkName"); // 六爻爻象标识名称

        // 2、根据六爻爻象计算变卦六爻爻象
        List<String> bianGuaLiuYaoAs = new ArrayList<>();
        for (int i = 0; i < this.liuYaoAsMark.size(); i++) {
            // 阳爻变阴爻，阴爻变阳爻
            if (!"".equals(this.liuYaoAsMark.get(i))) {
                bianGuaLiuYaoAs.add("—".equals(this.liuYaoAs.get(i)) ? "--" : "—");
            } else {
                bianGuaLiuYaoAs.add(this.liuYaoAs.get(i));
            }
        }
        this.bianGuaLiuYaoAs = bianGuaLiuYaoAs;

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
        return this.liuYaoJiChuSetting.getName();
    }

    /**
     * 获取占事
     *
     * @return 占事（如：未填写）
     */
    public String getOccupy() {
        return this.liuYaoJiChuSetting.getOccupy();
    }

    /**
     * 获取性别
     *
     * @return 性别（如：男）
     */
    public String getSex() {
        return this.liuYaoJiChuSetting.getSex() == 0 ? "女" : "男";
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
        if (this.liuYaoJiChuSetting.getXuShiSuiType() == 0) {
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
        return this.liuYaoJiChuSetting.getSex() == 0 ? "坤造" : "乾造";
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

        if (this.liuYaoJiChuSetting.getYearGanZhiType() == 0) {
            return this.lunar.getYearShengXiao(); // 以正月初一起算
        } else if (this.liuYaoJiChuSetting.getYearGanZhiType() == 1) {
            return this.lunar.getYearShengXiaoByLiChun(); // 以立春当天起算
        } else if (this.liuYaoJiChuSetting.getYearGanZhiType() == 2) {
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
        return this.hourGanZhi.equals(LiuYaoJiChuMap.WU_BU_YU_SHI.get(this.dayGan));
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
        return LiuYaoJiChuMap.TIAN_GAN_WU_XING.get(this.yearGan);
    }

    /**
     * 获取月干五行
     *
     * @return 月干五行（如：木）
     */
    public String getMonthGanWuXing() {
        return LiuYaoJiChuMap.TIAN_GAN_WU_XING.get(this.monthGan);
    }

    /**
     * 获取日干五行
     *
     * @return 日干五行（如：木）
     */
    public String getDayGanWuXing() {
        return LiuYaoJiChuMap.TIAN_GAN_WU_XING.get(this.dayGan);
    }

    /**
     * 获取时干五行
     *
     * @return 时干五行（如：木）
     */
    public String getHourGanWuXing() {
        return LiuYaoJiChuMap.TIAN_GAN_WU_XING.get(this.hourGan);
    }


    /**
     * 获取年支五行
     *
     * @return 年支五行（如：木）
     */
    public String getYearZhiWuXing() {
        return LiuYaoJiChuMap.DI_ZHI_WU_XING.get(this.yearZhi);
    }

    /**
     * 获取月支五行
     *
     * @return 月支五行（如：木）
     */
    public String getMonthZhiWuXing() {
        return LiuYaoJiChuMap.DI_ZHI_WU_XING.get(this.monthZhi);
    }

    /**
     * 获取日支五行
     *
     * @return 日支五行（如：木）
     */
    public String getDayZhiWuXing() {
        return LiuYaoJiChuMap.DI_ZHI_WU_XING.get(this.dayZhi);
    }

    /**
     * 获取时支五行
     *
     * @return 时支五行（如：木）
     */
    public String getHourZhiWuXing() {
        return LiuYaoJiChuMap.DI_ZHI_WU_XING.get(this.hourZhi);
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
        return LiuYaoJiChuMap.NA_YIN.get(this.yearGanZhi);
    }

    /**
     * 获取月干支纳音
     *
     * @return 月干支纳音（如：天上火）
     */
    public String getMonthGanZhiNaYin() {
        return LiuYaoJiChuMap.NA_YIN.get(this.monthGanZhi);
    }

    /**
     * 获取日干支纳音
     *
     * @return 日干支纳音（如：天上火）
     */
    public String getDayGanZhiNaYin() {
        return LiuYaoJiChuMap.NA_YIN.get(this.dayGanZhi);
    }

    /**
     * 获取时干支纳音
     *
     * @return 时干支纳音（如：天上火）
     */
    public String getHourGanZhiNaYin() {
        return LiuYaoJiChuMap.NA_YIN.get(this.hourGanZhi);
    }


    /**
     * 获取年干支空亡
     *
     * @return 年干支空亡（如：子丑）
     */
    public String getYearGanZhiKongWang() {
        return LiuYaoJiChuMap.KONG_WANG.get(this.yearGanZhi);
    }

    /**
     * 获取月干支空亡
     *
     * @return 月干支空亡（如：子丑）
     */
    public String getMonthGanZhiKongWang() {
        return LiuYaoJiChuMap.KONG_WANG.get(this.monthGanZhi);
    }

    /**
     * 获取日干支空亡
     *
     * @return 日干支空亡（如：子丑）
     */
    public String getDayGanZhiKongWang() {
        return LiuYaoJiChuMap.KONG_WANG.get(this.dayGanZhi);
    }

    /**
     * 获取时干支空亡
     *
     * @return 时干支空亡（如：子丑）
     */
    public String getHourGanZhiKongWang() {
        return LiuYaoJiChuMap.KONG_WANG.get(this.hourGanZhi);
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
        return LiuYaoJiChuMap.YUE_JIANG.get(getPrevQi() + getNextQi()).get(0);
    }

    /**
     * 获取月将神
     *
     * @return 月将神（如：神后）
     */
    public String getYueJiangShen() {
        return LiuYaoJiChuMap.YUE_JIANG.get(getPrevQi() + getNextQi()).get(1);
    }


    /**
     * 获取神煞
     *
     * @return 神煞（如：{tianYuanLu=寅}）
     */
    public Map<String, String> getShenSha() {

        LiuYaoShenShaUtil liuYaoShenShaUtil = new LiuYaoShenShaUtil(this.liuYaoShenShaSetting, this.yearGanZhi, this.monthGanZhi, this.dayGanZhi, this.hourGanZhi);
        return liuYaoShenShaUtil.getShenSha();

    }


    /**
     * 获取上卦卦名
     *
     * @return 上卦卦名（如：乾）
     */
    public String getShangGuaName() {
        return LiuYaoJiChuMap.GUA_NAME_AND_AS.get(this.liuYaoAs).get(0);
    }

    /**
     * 获取下卦卦名
     *
     * @return 下卦卦名（如：乾）
     */
    public String getXiaGuaName() {
        return LiuYaoJiChuMap.GUA_NAME_AND_AS.get(this.liuYaoAs).get(2);
    }

    /**
     * 获取本卦卦名
     *
     * @return 本卦卦名（如：乾为天）
     */
    public String getBenGuaName() {
        return LiuYaoJiChuMap.GUA_NAME_AND_AS.get(this.liuYaoAs).get(4);
    }

    /**
     * 获取变卦卦名
     *
     * @return 变卦卦名（如：乾为天）
     */
    public String getBianGuaName() {
        return LiuYaoJiChuMap.GUA_NAME_AND_AS.get(this.bianGuaLiuYaoAs).get(4);
    }

    /**
     * 获取互卦卦名
     *
     * @return 互卦卦名（如：乾为天）
     */
    public String getHuGuaName() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA.get(getHuGuaAs());
    }

    /**
     * 获取错卦卦名
     *
     * @return 错卦卦名（如：乾为天）
     */
    public String getCuoGuaName() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA.get(getCuoGuaAs());
    }

    /**
     * 获取综卦卦名
     *
     * @return 综卦卦名（如：乾为天）
     */
    public String getZongGuaName() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA.get(getZongGuaAs());
    }

    /**
     * 获取伏卦卦名
     *
     * @return 伏卦卦名（如：乾为天）
     */
    public String getFuGuaName() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA.get(getFuGuaAs());
    }


    /**
     * 获取上卦卦象
     *
     * @return 上卦卦象（如：☰）
     */
    public String getShangGuaAs() {
        return LiuYaoJiChuMap.GUA_NAME_AND_AS.get(this.liuYaoAs).get(1);
    }

    /**
     * 获取下卦卦象
     *
     * @return 下卦卦象（如：☰）
     */
    public String getXiaGuaAs() {
        return LiuYaoJiChuMap.GUA_NAME_AND_AS.get(this.liuYaoAs).get(3);
    }

    /**
     * 获取本卦卦象
     *
     * @return 本卦卦象（如：䷀）
     */
    public String getBenGuaAs() {
        return LiuYaoJiChuMap.GUA_NAME_AND_AS.get(this.liuYaoAs).get(5);
    }

    /**
     * 获取变卦卦象
     *
     * @return 变卦卦象（如：䷀）
     */
    public String getBianGuaAs() {
        return LiuYaoJiChuMap.GUA_NAME_AND_AS.get(this.bianGuaLiuYaoAs).get(5);
    }

    /**
     * 获取互卦卦象
     *
     * @return 互卦卦象（如：䷀）
     */
    public String getHuGuaAs() {
        return LiuYaoJiChuMap.HU_CUO_ZONG_FU.get(getBenGuaAs()).get(0);
    }

    /**
     * 获取错卦卦象
     *
     * @return 错卦卦象（如：䷀）
     */
    public String getCuoGuaAs() {
        return LiuYaoJiChuMap.HU_CUO_ZONG_FU.get(getBenGuaAs()).get(1);
    }

    /**
     * 获取综卦卦象
     *
     * @return 综卦卦象（如：䷀）
     */
    public String getZongGuaAs() {
        return LiuYaoJiChuMap.HU_CUO_ZONG_FU.get(getBenGuaAs()).get(2);
    }

    /**
     * 获取伏卦卦象
     *
     * @return 伏卦卦象（如：䷀）
     */
    public String getFuGuaAs() {
        return LiuYaoJiChuMap.HU_CUO_ZONG_FU.get(getBenGuaAs()).get(3);
    }


    /**
     * 获取本卦类型
     *
     * @return 本卦类型（如：一世）
     */
    public String getBenGuaType() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getBenGuaName()).get(0);
    }

    /**
     * 获取变卦类型
     *
     * @return 变卦类型（如：一世）
     */
    public String getBianGuaType() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getBianGuaName()).get(0);
    }

    /**
     * 获取互卦类型
     *
     * @return 互卦类型（如：一世）
     */
    public String getHuGuaType() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getHuGuaName()).get(0);
    }

    /**
     * 获取错卦类型
     *
     * @return 错卦类型（如：一世）
     */
    public String getCuoGuaType() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getCuoGuaName()).get(0);
    }

    /**
     * 获取综卦类型
     *
     * @return 综卦类型（如：一世）
     */
    public String getZongGuaType() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getZongGuaName()).get(0);
    }

    /**
     * 获取伏卦类型
     *
     * @return 伏卦类型（如：一世）
     */
    public String getFuGuaType() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getFuGuaName()).get(0);
    }


    /**
     * 获取本卦卦身
     *
     * @return 本卦卦身（如：子）
     */
    public String getBenGuaGuaShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getBenGuaName()).get(1);
    }

    /**
     * 获取变卦卦身
     *
     * @return 变卦卦身（如：子）
     */
    public String getBianGuaGuaShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getBianGuaName()).get(1);
    }

    /**
     * 获取互卦卦身
     *
     * @return 互卦卦身（如：子）
     */
    public String getHuGuaGuaShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getHuGuaName()).get(1);
    }

    /**
     * 获取错卦卦身
     *
     * @return 错卦卦身（如：子）
     */
    public String getCuoGuaGuaShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getCuoGuaName()).get(1);
    }

    /**
     * 获取综卦卦身
     *
     * @return 综卦卦身（如：子）
     */
    public String getZongGuaGuaShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getZongGuaName()).get(1);
    }

    /**
     * 获取伏卦卦身
     *
     * @return 伏卦卦身（如：子）
     */
    public String getFuGuaGuaShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getFuGuaName()).get(1);
    }


    /**
     * 获取本卦卦辞
     *
     * @return 本卦卦辞（如：元，亨，利，贞。）
     */
    public String getBenGuaGuaCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getBenGuaName()).get(2);
    }

    /**
     * 获取变卦卦辞
     *
     * @return 变卦卦辞（如：元，亨，利，贞。）
     */
    public String getBianGuaGuaCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getBianGuaName()).get(2);
    }

    /**
     * 获取互卦卦辞
     *
     * @return 互卦卦辞（如：元，亨，利，贞。）
     */
    public String getHuGuaGuaCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getHuGuaName()).get(2);
    }

    /**
     * 获取错卦卦辞
     *
     * @return 错卦卦辞（如：元，亨，利，贞。）
     */
    public String getCuoGuaGuaCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getCuoGuaName()).get(2);
    }

    /**
     * 获取综卦卦辞
     *
     * @return 综卦卦辞（如：元，亨，利，贞。）
     */
    public String getZongGuaGuaCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getZongGuaName()).get(2);
    }

    /**
     * 获取伏卦卦辞
     *
     * @return 伏卦卦辞（如：元，亨，利，贞。）
     */
    public String getFuGuaGuaCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_SHEN_CI.get(getFuGuaName()).get(2);
    }


    /**
     * 获取本卦六爻爻名
     *
     * @return 本卦六爻爻名（如：[初九, 九二, 九三, 九四, 九五, 上九]）
     */
    public List<String> getBenGuaLiuYaoName() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_MING.get(getBenGuaAs());
    }

    /**
     * 获取变卦六爻爻名
     *
     * @return 变卦六爻爻名（如：[初九, 九二, 九三, 九四, 九五, 上九]）
     */
    public List<String> getBianGuaLiuYaoName() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_MING.get(getBianGuaAs());
    }

    /**
     * 获取互卦六爻爻名
     *
     * @return 互卦六爻爻名（如：[初九, 九二, 九三, 九四, 九五, 上九]）
     */
    public List<String> getHuGuaLiuYaoName() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_MING.get(getHuGuaAs());
    }

    /**
     * 获取错卦六爻爻名
     *
     * @return 错卦六爻爻名（如：[初九, 九二, 九三, 九四, 九五, 上九]）
     */
    public List<String> getCuoGuaLiuYaoName() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_MING.get(getCuoGuaAs());
    }

    /**
     * 获取综卦六爻爻名
     *
     * @return 综卦六爻爻名（如：[初九, 九二, 九三, 九四, 九五, 上九]）
     */
    public List<String> getZongGuaLiuYaoName() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_MING.get(getZongGuaAs());
    }

    /**
     * 获取伏卦六爻爻名
     *
     * @return 伏卦六爻爻名（如：[初九, 九二, 九三, 九四, 九五, 上九]）
     */
    public List<String> getFuGuaLiuYaoName() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_MING.get(getFuGuaAs());
    }


    /**
     * 获取本卦六爻爻象
     *
     * @return 本卦六爻爻象（如：[—, —, —, —, —, —]）
     */
    public List<String> getBenGuaLiuYaoAs() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_AS.get(getBenGuaAs());
    }

    /**
     * 获取变卦六爻爻象
     *
     * @return 变卦六爻爻象（如：[—, —, —, —, —, —]）
     */
    public List<String> getBianGuaLiuYaoAs() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_AS.get(getBianGuaAs());
    }

    /**
     * 获取互卦六爻爻象
     *
     * @return 互卦六爻爻象（如：[—, —, —, —, —, —]）
     */
    public List<String> getHuGuaLiuYaoAs() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_AS.get(getHuGuaAs());
    }

    /**
     * 获取错卦六爻爻象
     *
     * @return 错卦六爻爻象（如：[—, —, —, —, —, —]）
     */
    public List<String> getCuoGuaLiuYaoAs() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_AS.get(getCuoGuaAs());
    }

    /**
     * 获取综卦六爻爻象
     *
     * @return 综卦六爻爻象（如：[—, —, —, —, —, —]）
     */
    public List<String> getZongGuaLiuYaoAs() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_AS.get(getZongGuaAs());
    }

    /**
     * 获取伏卦六爻爻象
     *
     * @return 伏卦六爻爻象（如：[—, —, —, —, —, —]）
     */
    public List<String> getFuGuaLiuYaoAs() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_AS.get(getFuGuaAs());
    }


    /**
     * 获取本卦六爻世应
     *
     * @return 本卦六爻世应（如：[, , 应, , , 世]）
     */
    public List<String> getBenGuaLiuYaoShiYing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_SHI_YING.get(getBenGuaAs());
    }

    /**
     * 获取变卦六爻世应
     *
     * @return 变卦六爻世应（如：[, , 应, , , 世]）
     */
    public List<String> getBianGuaLiuYaoShiYing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_SHI_YING.get(getBianGuaAs());
    }

    /**
     * 获取互卦六爻世应
     *
     * @return 互卦六爻世应（如：[, , 应, , , 世]）
     */
    public List<String> getHuGuaLiuYaoShiYing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_SHI_YING.get(getHuGuaAs());
    }

    /**
     * 获取错卦六爻世应
     *
     * @return 错卦六爻世应（如：[, , 应, , , 世]）
     */
    public List<String> getCuoGuaLiuYaoShiYing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_SHI_YING.get(getCuoGuaAs());
    }

    /**
     * 获取综卦六爻世应
     *
     * @return 综卦六爻世应（如：[, , 应, , , 世]）
     */
    public List<String> getZongGuaLiuYaoShiYing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_SHI_YING.get(getZongGuaAs());
    }

    /**
     * 获取伏卦六爻世应
     *
     * @return 伏卦六爻世应（如：[, , 应, , , 世]）
     */
    public List<String> getFuGuaLiuYaoShiYing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_SHI_YING.get(getFuGuaAs());
    }


    /**
     * 获取本卦六爻六亲
     *
     * @return 本卦六爻六亲（如：[子孙, 妻财, 父母, 官鬼, 兄弟, 父母]）
     */
    public List<String> getBenGuaLiuYaoLiuQin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_QIN.get(getBenGuaAs());
    }

    /**
     * 获取变卦六爻六亲
     *
     * @return 变卦六爻六亲（如：[子孙, 妻财, 父母, 官鬼, 兄弟, 父母]）
     */
    public List<String> getBianGuaLiuYaoLiuQin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_QIN.get(getBianGuaAs());
    }

    /**
     * 获取互卦六爻六亲
     *
     * @return 互卦六爻六亲（如：[子孙, 妻财, 父母, 官鬼, 兄弟, 父母]）
     */
    public List<String> getHuGuaLiuYaoLiuQin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_QIN.get(getHuGuaAs());
    }

    /**
     * 获取错卦六爻六亲
     *
     * @return 错卦六爻六亲（如：[子孙, 妻财, 父母, 官鬼, 兄弟, 父母]）
     */
    public List<String> getCuoGuaLiuYaoLiuQin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_QIN.get(getCuoGuaAs());
    }

    /**
     * 获取综卦六爻六亲
     *
     * @return 综卦六爻六亲（如：[子孙, 妻财, 父母, 官鬼, 兄弟, 父母]）
     */
    public List<String> getZongGuaLiuYaoLiuQin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_QIN.get(getZongGuaAs());
    }

    /**
     * 获取伏卦六爻六亲
     *
     * @return 伏卦六爻六亲（如：[子孙, 妻财, 父母, 官鬼, 兄弟, 父母]）
     */
    public List<String> getFuGuaLiuYaoLiuQin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_QIN.get(getFuGuaAs());
    }


    /**
     * 获取本卦六爻干支
     *
     * @return 本卦六爻干支（如：[甲子, 甲寅, 甲辰, 壬午, 壬申, 壬戌]）
     */
    public List<String> getBenGuaLiuYaoGanZhi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_GAN_ZHI.get(getBenGuaAs());
    }

    /**
     * 获取变卦六爻干支
     *
     * @return 变卦六爻干支（如：[甲子, 甲寅, 甲辰, 壬午, 壬申, 壬戌]）
     */
    public List<String> getBianGuaLiuYaoGanZhi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_GAN_ZHI.get(getBianGuaAs());
    }

    /**
     * 获取互卦六爻干支
     *
     * @return 互卦六爻干支（如：[甲子, 甲寅, 甲辰, 壬午, 壬申, 壬戌]）
     */
    public List<String> getHuGuaLiuYaoGanZhi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_GAN_ZHI.get(getHuGuaAs());
    }

    /**
     * 获取错卦六爻干支
     *
     * @return 错卦六爻干支（如：[甲子, 甲寅, 甲辰, 壬午, 壬申, 壬戌]）
     */
    public List<String> getCuoGuaLiuYaoGanZhi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_GAN_ZHI.get(getCuoGuaAs());
    }

    /**
     * 获取综卦六爻干支
     *
     * @return 综卦六爻干支（如：[甲子, 甲寅, 甲辰, 壬午, 壬申, 壬戌]）
     */
    public List<String> getZongGuaLiuYaoGanZhi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_GAN_ZHI.get(getZongGuaAs());
    }

    /**
     * 获取伏卦六爻干支
     *
     * @return 伏卦六爻干支（如：[甲子, 甲寅, 甲辰, 壬午, 壬申, 壬戌]）
     */
    public List<String> getFuGuaLiuYaoGanZhi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_GAN_ZHI.get(getFuGuaAs());
    }


    /**
     * 获取本卦六爻五行
     *
     * @return 本卦六爻五行（如：[水, 木, 土, 火, 金, 土]）
     */
    public List<String> getBenGuaLiuYaoWuXing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_WU_XING.get(getBenGuaAs());
    }

    /**
     * 获取变卦六爻五行
     *
     * @return 变卦六爻五行（如：[水, 木, 土, 火, 金, 土]）
     */
    public List<String> getBianGuaLiuYaoWuXing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_WU_XING.get(getBianGuaAs());
    }

    /**
     * 获取互卦六爻五行
     *
     * @return 互卦六爻五行（如：[水, 木, 土, 火, 金, 土]）
     */
    public List<String> getHuGuaLiuYaoWuXing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_WU_XING.get(getHuGuaAs());
    }

    /**
     * 获取错卦六爻五行
     *
     * @return 错卦六爻五行（如：[水, 木, 土, 火, 金, 土]）
     */
    public List<String> getCuoGuaLiuYaoWuXing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_WU_XING.get(getCuoGuaAs());
    }

    /**
     * 获取综卦六爻五行
     *
     * @return 综卦六爻五行（如：[水, 木, 土, 火, 金, 土]）
     */
    public List<String> getZongGuaLiuYaoWuXing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_WU_XING.get(getZongGuaAs());
    }

    /**
     * 获取伏卦六爻五行
     *
     * @return 伏卦六爻五行（如：[水, 木, 土, 火, 金, 土]）
     */
    public List<String> getFuGuaLiuYaoWuXing() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_WU_XING.get(getFuGuaAs());
    }


    /**
     * 获取本卦六爻六神
     *
     * @return 本卦六爻六神（如：[青龙, 朱雀, 勾陈, 螣蛇, 白虎, 玄武]）
     */
    public List<String> getBenGuaLiuYaoLiuShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_SHEN.get(this.dayGan);
    }

    /**
     * 获取变卦六爻六神
     *
     * @return 变卦六爻六神（如：[青龙, 朱雀, 勾陈, 螣蛇, 白虎, 玄武]）
     */
    public List<String> getBianGuaLiuYaoLiuShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_SHEN.get(this.dayGan);
    }

    /**
     * 获取互卦六爻六神
     *
     * @return 互卦六爻六神（如：[青龙, 朱雀, 勾陈, 螣蛇, 白虎, 玄武]）
     */
    public List<String> getHuGuaLiuYaoLiuShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_SHEN.get(this.dayGan);
    }

    /**
     * 获取错卦六爻六神
     *
     * @return 错卦六爻六神（如：[青龙, 朱雀, 勾陈, 螣蛇, 白虎, 玄武]）
     */
    public List<String> getCuoGuaLiuYaoLiuShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_SHEN.get(this.dayGan);
    }

    /**
     * 获取综卦六爻六神
     *
     * @return 综卦六爻六神（如：[青龙, 朱雀, 勾陈, 螣蛇, 白虎, 玄武]）
     */
    public List<String> getZongGuaLiuYaoLiuShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_SHEN.get(this.dayGan);
    }

    /**
     * 获取伏卦六爻六神
     *
     * @return 伏卦六爻六神（如：[青龙, 朱雀, 勾陈, 螣蛇, 白虎, 玄武]）
     */
    public List<String> getFuGuaLiuYaoLiuShen() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_LIU_SHEN.get(this.dayGan);
    }


    /**
     * 获取本卦六爻爻辞
     *
     * @return 本卦六爻爻辞（如：[潜龙勿用。, 见龙在田，利见大人。, 君子终日乾乾，夕惕若厉，无咎。, 或跃在渊，无咎。, 飞龙在天，利见大人。, 亢龙有悔。]）
     */
    public List<String> getBenGuaLiuYaoYaoCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_CI.get(getBenGuaAs());
    }

    /**
     * 获取变卦六爻爻辞
     *
     * @return 变卦六爻爻辞（如：[潜龙勿用。, 见龙在田，利见大人。, 君子终日乾乾，夕惕若厉，无咎。, 或跃在渊，无咎。, 飞龙在天，利见大人。, 亢龙有悔。]）
     */
    public List<String> getBianGuaLiuYaoYaoCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_CI.get(getBianGuaAs());
    }

    /**
     * 获取互卦六爻爻辞
     *
     * @return 互卦六爻爻辞（如：[潜龙勿用。, 见龙在田，利见大人。, 君子终日乾乾，夕惕若厉，无咎。, 或跃在渊，无咎。, 飞龙在天，利见大人。, 亢龙有悔。]）
     */
    public List<String> getHuGuaLiuYaoYaoCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_CI.get(getHuGuaAs());
    }

    /**
     * 获取错卦六爻爻辞
     *
     * @return 错卦六爻爻辞（如：[潜龙勿用。, 见龙在田，利见大人。, 君子终日乾乾，夕惕若厉，无咎。, 或跃在渊，无咎。, 飞龙在天，利见大人。, 亢龙有悔。]）
     */
    public List<String> getCuoGuaLiuYaoYaoCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_CI.get(getCuoGuaAs());
    }

    /**
     * 获取综卦六爻爻辞
     *
     * @return 综卦六爻爻辞（如：[潜龙勿用。, 见龙在田，利见大人。, 君子终日乾乾，夕惕若厉，无咎。, 或跃在渊，无咎。, 飞龙在天，利见大人。, 亢龙有悔。]）
     */
    public List<String> getZongGuaLiuYaoYaoCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_CI.get(getZongGuaAs());
    }

    /**
     * 获取伏卦六爻爻辞
     *
     * @return 伏卦六爻爻辞（如：[潜龙勿用。, 见龙在田，利见大人。, 君子终日乾乾，夕惕若厉，无咎。, 或跃在渊，无咎。, 飞龙在天，利见大人。, 亢龙有悔。]）
     */
    public List<String> getFuGuaLiuYaoYaoCi() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_YAO_CI.get(getFuGuaAs());
    }


    /**
     * 获取本卦六爻纳音
     *
     * @return 本卦六爻纳音（如：[海中金, 大溪水, 覆灯火, 杨柳木, 剑锋金, 大海水]）
     */
    public List<String> getBenGuaLiuYaoNaYin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_NA_YIN.get(getBenGuaAs());
    }

    /**
     * 获取变卦六爻纳音
     *
     * @return 变卦六爻纳音（如：[海中金, 大溪水, 覆灯火, 杨柳木, 剑锋金, 大海水]）
     */
    public List<String> getBianGuaLiuYaoNaYin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_NA_YIN.get(getBianGuaAs());
    }

    /**
     * 获取互卦六爻纳音
     *
     * @return 互卦六爻纳音（如：[海中金, 大溪水, 覆灯火, 杨柳木, 剑锋金, 大海水]）
     */
    public List<String> getHuGuaLiuYaoNaYin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_NA_YIN.get(getHuGuaAs());
    }

    /**
     * 获取错卦六爻纳音
     *
     * @return 错卦六爻纳音（如：[海中金, 大溪水, 覆灯火, 杨柳木, 剑锋金, 大海水]）
     */
    public List<String> getCuoGuaLiuYaoNaYin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_NA_YIN.get(getCuoGuaAs());
    }

    /**
     * 获取综卦六爻纳音
     *
     * @return 综卦六爻纳音（如：[海中金, 大溪水, 覆灯火, 杨柳木, 剑锋金, 大海水]）
     */
    public List<String> getZongGuaLiuYaoNaYin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_NA_YIN.get(getZongGuaAs());
    }

    /**
     * 获取伏卦六爻纳音
     *
     * @return 伏卦六爻纳音（如：[海中金, 大溪水, 覆灯火, 杨柳木, 剑锋金, 大海水]）
     */
    public List<String> getFuGuaLiuYaoNaYin() {
        return LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_YAO_NA_YIN.get(getFuGuaAs());
    }


    /**
     * 获取伏卦六爻伏神
     *
     * @return 伏卦六爻伏神（如：[, , , , , ]）
     */
    public List<String> getFuGuaLiuYaoFuShen() {

        List<String> fuGuaLiuYaoFuShen = CommonUtil.addCharToList(6, "");
        List<String> liuQinQueShi = LiuYaoJiChuMap.LIU_SHI_SI_GUA_LIU_QIN_QUE_SHI.get(getBenGuaName()); // 本卦缺失的六亲（最多缺失两个）
        if (null != liuQinQueShi) {
            if (liuQinQueShi.size() == 1) {
                // 缺失一个六亲
                for (int i = 0; i < 6; i++) {
                    if (getFuGuaLiuYaoLiuQin().get(i).equals(liuQinQueShi.get(0))) {
                        fuGuaLiuYaoFuShen.set(i, "伏");
                    }
                }
            } else {
                // 缺失两个六亲
                for (int i = 0; i < 6; i++) {
                    if (getFuGuaLiuYaoLiuQin().get(i).equals(liuQinQueShi.get(0))) {
                        fuGuaLiuYaoFuShen.set(i, "伏");
                    }
                    if (getFuGuaLiuYaoLiuQin().get(i).equals(liuQinQueShi.get(1))) {
                        fuGuaLiuYaoFuShen.set(i, "伏");
                    }
                }
            }
        }

        return fuGuaLiuYaoFuShen;

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
                "上卦:" + getShangGuaName() + "(" + getShangGuaAs() + ")" + "   " +
                "下卦:" + getXiaGuaName() + "(" + getXiaGuaAs() + ")" + "   " +
                "本卦:" + getBenGuaName() + "(" + getBenGuaAs() + ")" + "   " +
                "变卦:" + getBianGuaName() + "(" + getBianGuaAs() + ")" + "   " +
                "互卦:" + getHuGuaName() + "(" + getHuGuaAs() + ")" + "   " +
                "错卦:" + getCuoGuaName() + "(" + getCuoGuaAs() + ")" + "   " +
                "综卦:" + getZongGuaName() + "(" + getZongGuaAs() + ")" + "   " +
                "伏卦:" + getFuGuaName() + "(" + getFuGuaAs() + ")";

    }


}
