package xuan.core.daliuren;

import java.time.LocalDate;
import java.time.Period;
import java.time.ZoneId;
import java.util.*;

import com.nlf.calendar.JieQi;
import xuan.core.daliuren.settings.DaLiuRenShenShaSetting;
import xuan.utils.DateUtil;
import xuan.utils.CommonUtil;
import com.nlf.calendar.Lunar;
import com.nlf.calendar.Solar;
import xuan.core.daliuren.maps.DaLiuRenJiChuMap;
import xuan.core.daliuren.utils.DaLiuRenJiChuUtil;
import xuan.core.daliuren.settings.DaLiuRenJiChuSetting;

/**
 * 大六壬
 *
 * @author 善待
 */
public class DaLiuRen {

    /**
     * 大六壬 - 基础设置
     */
    private DaLiuRenJiChuSetting daLiuRenJiChuSetting;
    /**
     * 大六壬 - 神煞设置
     */
    private DaLiuRenShenShaSetting daLiuRenShenShaSetting;

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
     * 天干（1~12宫）
     */
    private List<String> tianGan;
    /**
     * 地盘（1~12宫）
     */
    private List<String> diPan;
    /**
     * 天盘（1~12宫）
     */
    private List<String> tianPan;
    /**
     * 神盘（1~12宫）
     */
    private List<String> shenPan;

    /**
     * 四课
     */
    private List<List<String>> siKe;

    /**
     * 三传
     */
    private List<String> sanChuan;
    /**
     * 三传取法
     */
    private String sanChuanQuFa;

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
     * @param daLiuRenJiChuSetting 大六壬 - 基础设置
     */
    public DaLiuRen(DaLiuRenJiChuSetting daLiuRenJiChuSetting) {

        this.daLiuRenJiChuSetting = daLiuRenJiChuSetting; // 基础设置

        // 1、获取基础设置
        String date = daLiuRenJiChuSetting.getDate(); // 日期
        int dateType = daLiuRenJiChuSetting.getDateType(); // 日期类型
        int leapMonthType = daLiuRenJiChuSetting.getLeapMonthType(); // 闰月类型
        int yearGanZhiType = daLiuRenJiChuSetting.getYearGanZhiType(); // 年干支类型
        int monthGanZhiType = daLiuRenJiChuSetting.getMonthGanZhiType(); // 月干支类型
        int dayGanZhiType = daLiuRenJiChuSetting.getDayGanZhiType(); // 日干支类型

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
        initializeDiPan(); // 初始化地盘
        initializeTianPan(); // 初始化天盘
        initializeTianGan(); // 初始化天干
        initializeShenPan(); // 初始化神盘
        initializeSiKe(); // 初始化四课
        initializeSanChuan(); // 初始化三传

    }

    /**
     * 神煞设置（可选）
     * <p>
     * <hr/>
     * 可选，若不设置则使用默认值，详情请在设置中查看
     */
    public void daLiuRenShenShaSetting(DaLiuRenShenShaSetting daLiuRenShenShaSetting) {
        this.daLiuRenShenShaSetting = daLiuRenShenShaSetting;
    }

    /**
     * 初始化上下节气
     */
    private void initializeShangXiaJieQi() {

        int jieQiType = this.daLiuRenJiChuSetting.getJieQiType();

        this.prevJie = this.lunar.getPrevJie(jieQiType == 0); // 上一节
        this.nextJie = this.lunar.getNextJie(jieQiType == 0); // 下一节
        this.prevQi = this.lunar.getPrevQi(jieQiType == 0); // 上一气
        this.nextQi = this.lunar.getNextQi(jieQiType == 0); // 下一气

    }

    /**
     * 初始化地盘
     */
    private void initializeDiPan() {
        this.diPan = DaLiuRenJiChuMap.SHI_ER_GONG_DI_ZHI;
    }

    /**
     * 初始化天盘
     */
    private void initializeTianPan() {

        /* 口诀：月将加占时，顺行十二辰（将月将加于地盘的时支上，依次顺排十二天将，即天盘） */

        // 1、获取月将落入时支（地盘地支）的宫位
        int yueJiangGongWei = 0; // 月将落入的宫位
        for (int i = 0; i < 12; i++) {
            if (this.diPan.get(i).equals(this.hourZhi)) {
                yueJiangGongWei = i;
                break;
            }
        }

        // 2、从月将落入的宫位开始顺时针添加天盘
        List<String> diZhiShunPai = DaLiuRenJiChuMap.DI_ZHI_SHUN_PAI.get(getYueJiang());
        List<String> tianPan = CommonUtil.addCharToList(12, "");
        for (int i = 0; i < 12; i++) {
            tianPan.set(yueJiangGongWei, diZhiShunPai.get(i));
            yueJiangGongWei++;
            if (yueJiangGongWei > 11) yueJiangGongWei = 0;
        }

        this.tianPan = tianPan;

    }

    /**
     * 初始化天干
     */
    private void initializeTianGan() {

        // 获取日干支空亡的天干落在天地盘中天盘的哪个宫位
        final String daGanZhiKongWang = this.getDayGanZhiKongWang().substring(1, 2);
        for (int i = 0; i < 12; i++) {
            if (this.tianPan.get(i).equals(daGanZhiKongWang)) {
                this.tianGan = DaLiuRenJiChuMap.DUN_GAN_SHUN.get(i + 1);
            }
        }

    }

    /**
     * 初始化神盘
     */
    private void initializeShenPan() {

        // 判断贵人计算类型
        if (this.daLiuRenJiChuSetting.getGuiRenType() == 0) {
            // 1、自动切换
            this.shenPan = computeShiErGuiRen(DaLiuRenJiChuMap.ZHOU_YE_GUI_REN);
        } else if (this.daLiuRenJiChuSetting.getGuiRenType() == 1) {
            // 2、昼贵
            this.shenPan = computeShiErGuiRen(DaLiuRenJiChuMap.ZHOU_GUI_REN);
        } else if (this.daLiuRenJiChuSetting.getGuiRenType() == 2) {
            // 3、夜贵
            this.shenPan = computeShiErGuiRen(DaLiuRenJiChuMap.YE_GUI_REN);
        }

    }

    /**
     * 初始化四课
     */
    private void initializeSiKe() {

        List<List<String>> siKe = new ArrayList<>();

        // 1、计算第一课
        String jiGongDiZhi = DaLiuRenJiChuMap.SHI_GAN_JI_GONG.get(getDayGan()); // 获取十干寄宫地盘地支
        String ganYang = ""; // 干阳
        for (int i = 0; i < 12; i++) {
            if (this.diPan.get(i).equals(jiGongDiZhi)) {
                ganYang = this.tianPan.get(i);
            }
        }
        siKe.add(Arrays.asList(ganYang, getDayGan()));

        // 2、计算第二课
        String ganYin = ""; // 干阴
        for (int i = 0; i < 12; i++) {
            if (this.diPan.get(i).equals(ganYang)) {
                ganYin = this.tianPan.get(i);
            }
        }
        siKe.add(Arrays.asList(ganYin, ganYang));

        // 3、计算第三课
        String zhiYang = ""; // 支阳
        for (int i = 0; i < 12; i++) {
            if (this.diPan.get(i).equals(getDayZhi())) {
                zhiYang = this.tianPan.get(i);
            }
        }
        siKe.add(Arrays.asList(zhiYang, getDayZhi()));

        // 4、计算第四课
        String zhiYin = ""; // 支阴
        for (int i = 0; i < 12; i++) {
            if (this.diPan.get(i).equals(zhiYang)) {
                zhiYin = this.tianPan.get(i);
            }
        }
        siKe.add(Arrays.asList(zhiYin, zhiYang));

        this.siKe = siKe;

    }

    /**
     * 初始化三传
     */
    private void initializeSanChuan() {
        this.sanChuan = DaLiuRenJiChuMap.SAN_CHUAN.get(this.dayGanZhi + this.siKe.get(0).get(0));
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
     * 获取年龄
     */
    public int getAge() {

        LocalDate nowDate = LocalDate.now(); // 当前日期
        LocalDate birthDate = this.solarDate.toInstant().atZone(ZoneId.systemDefault()).toLocalDate(); // 出生日期

        // 1.1、计算实岁
        int age = Period.between(birthDate, nowDate).getYears();
        // 1.2、计算虚岁
        if (this.daLiuRenJiChuSetting.getXuShiSuiType() == 0) {
            age = age + (nowDate.getMonthValue() > birthDate.getMonthValue() || (nowDate.getMonthValue() == birthDate.getMonthValue() && nowDate.getDayOfMonth() >= birthDate.getDayOfMonth()) ? 1 : 0);
        }

        return age;

    }

    /**
     * 获取姓名
     *
     * @return 姓名（如：缘主）
     */
    public String getName() {
        return this.daLiuRenJiChuSetting.getName();
    }

    /**
     * 获取性别
     *
     * @return 性别（如：男）
     */
    public String getSex() {
        return this.daLiuRenJiChuSetting.getSex() == 0 ? "女" : "男";
    }

    /**
     * 获取占事
     *
     * @return 占事（如：未填写）
     */
    public String getOccupy() {
        return this.daLiuRenJiChuSetting.getOccupy();
    }

    /**
     * 获取造
     *
     * @return 造（如：乾造）
     */
    public String getZao() {
        return this.daLiuRenJiChuSetting.getSex() == 0 ? "坤造" : "乾造";
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

        if (this.daLiuRenJiChuSetting.getYearGanZhiType() == 0) {
            return this.lunar.getYearShengXiao(); // 以正月初一起算
        } else if (this.daLiuRenJiChuSetting.getYearGanZhiType() == 1) {
            return this.lunar.getYearShengXiaoByLiChun(); // 以立春当天起算
        } else if (this.daLiuRenJiChuSetting.getYearGanZhiType() == 2) {
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
        return this.hourGanZhi.equals(DaLiuRenJiChuMap.WU_BU_YU_SHI.get(this.dayGan));
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
        return DaLiuRenJiChuMap.TIAN_GAN_WU_XING.get(this.yearGan);
    }

    /**
     * 获取月干五行
     *
     * @return 月干五行（如：木）
     */
    public String getMonthGanWuXing() {
        return DaLiuRenJiChuMap.TIAN_GAN_WU_XING.get(this.monthGan);
    }

    /**
     * 获取日干五行
     *
     * @return 日干五行（如：木）
     */
    public String getDayGanWuXing() {
        return DaLiuRenJiChuMap.TIAN_GAN_WU_XING.get(this.dayGan);
    }

    /**
     * 获取时干五行
     *
     * @return 时干五行（如：木）
     */
    public String getHourGanWuXing() {
        return DaLiuRenJiChuMap.TIAN_GAN_WU_XING.get(this.hourGan);
    }


    /**
     * 获取年支五行
     *
     * @return 年支五行（如：木）
     */
    public String getYearZhiWuXing() {
        return DaLiuRenJiChuMap.DI_ZHI_WU_XING.get(this.yearZhi);
    }

    /**
     * 获取月支五行
     *
     * @return 月支五行（如：木）
     */
    public String getMonthZhiWuXing() {
        return DaLiuRenJiChuMap.DI_ZHI_WU_XING.get(this.monthZhi);
    }

    /**
     * 获取日支五行
     *
     * @return 日支五行（如：木）
     */
    public String getDayZhiWuXing() {
        return DaLiuRenJiChuMap.DI_ZHI_WU_XING.get(this.dayZhi);
    }

    /**
     * 获取时支五行
     *
     * @return 时支五行（如：木）
     */
    public String getHourZhiWuXing() {
        return DaLiuRenJiChuMap.DI_ZHI_WU_XING.get(this.hourZhi);
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
        return DaLiuRenJiChuMap.NA_YIN.get(this.yearGanZhi);
    }

    /**
     * 获取月干支纳音
     *
     * @return 月干支纳音（如：天上火）
     */
    public String getMonthGanZhiNaYin() {
        return DaLiuRenJiChuMap.NA_YIN.get(this.monthGanZhi);
    }

    /**
     * 获取日干支纳音
     *
     * @return 日干支纳音（如：天上火）
     */
    public String getDayGanZhiNaYin() {
        return DaLiuRenJiChuMap.NA_YIN.get(this.dayGanZhi);
    }

    /**
     * 获取时干支纳音
     *
     * @return 时干支纳音（如：天上火）
     */
    public String getHourGanZhiNaYin() {
        return DaLiuRenJiChuMap.NA_YIN.get(this.hourGanZhi);
    }


    /**
     * 获取年干支空亡
     *
     * @return 年干支空亡（如：子丑）
     */
    public String getYearGanZhiKongWang() {
        return DaLiuRenJiChuMap.KONG_WANG.get(this.yearGanZhi);
    }

    /**
     * 获取月干支空亡
     *
     * @return 月干支空亡（如：子丑）
     */
    public String getMonthGanZhiKongWang() {
        return DaLiuRenJiChuMap.KONG_WANG.get(this.monthGanZhi);
    }

    /**
     * 获取日干支空亡
     *
     * @return 日干支空亡（如：子丑）
     */
    public String getDayGanZhiKongWang() {
        return DaLiuRenJiChuMap.KONG_WANG.get(this.dayGanZhi);
    }

    /**
     * 获取时干支空亡
     *
     * @return 时干支空亡（如：子丑）
     */
    public String getHourGanZhiKongWang() {
        return DaLiuRenJiChuMap.KONG_WANG.get(this.hourGanZhi);
    }


    /**
     * 获取五行旺衰
     *
     * @return 五行旺衰（如：[木旺, 火相, 水休, 金囚, 土死]）
     */
    public List<String> getWuXingWangShuai() {
        return DaLiuRenJiChuMap.WU_XING_WANG_SHUAI.get(this.monthZhi);
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
        return DaLiuRenJiChuMap.YUE_JIANG.get(getPrevQi() + getNextQi()).get(0);
    }

    /**
     * 获取月将神
     *
     * @return 月将神（如：神后）
     */
    public String getYueJiangShen() {
        return DaLiuRenJiChuMap.YUE_JIANG.get(getPrevQi() + getNextQi()).get(1);
    }


    /**
     * 获取三传取法
     *
     * @return 三传取法（如：贼克法）
     */
    public String getSanChuanQuFa() {
        return this.sanChuanQuFa;
    }

    /**
     * 获取天地盘类型
     *
     * @return 天地盘类型（如：伏吟盘）
     */
    public String getTianDiPanType() {
        return DaLiuRenJiChuMap.TIAN_DI_PAN_TYPE.get(getYueJiang() + this.hourZhi);
    }


    /**
     * 获取天干
     *
     * @return 天干（如：）
     */
    public List<String> getTianGan() {
        return this.tianGan;
    }

    /**
     * 获取地盘
     *
     * @return 地盘（如：[寅, 卯, 辰, 巳, 午, 未, 申, 酉, 戌, 亥, 子, 丑]）
     */
    public List<String> getDiPan() {
        return this.diPan;
    }

    /**
     * 获取天盘
     *
     * @return 天盘（如：[寅, 卯, 辰, 巳, 午, 未, 申, 酉, 戌, 亥, 子, 丑]）
     */
    public List<String> getTianPan() {
        return this.tianPan;
    }

    /**
     * 获取神盘
     *
     * @return 神盘（如：[太阴, 天后, 贵人, 螣蛇, 朱雀, 六合, 勾陈, 青龙, 天空, 白虎, 太常, 玄武]）
     */
    public List<String> getShenPan() {
        return this.shenPan;
    }


    /**
     * 获取四课
     *
     * @return 四课（如：[[午, 乙], [申, 午], [酉, 未], [亥, 酉]]）
     */
    public List<List<String>> getSiKe() {
        return this.siKe;
    }

    /**
     * 获取四课遁干
     *
     * @return 四课遁干（如：[[戊, ], [辛, 戊], [庚, 丁], [癸, 庚]]）
     */
    public List<List<String>> getSiKeDunGan() {

        // 处理第一课地盘天干
        String newYiKeDiPan = DaLiuRenJiChuMap.SHI_GAN_JI_GONG.get(this.siKe.get(0).get(1)); // 处理第一课，将地盘天干转换为寄宫地支
        List<List<String>> newSiKe = new ArrayList<>();
        newSiKe.add(0, Arrays.asList(this.siKe.get(0).get(0), newYiKeDiPan));
        newSiKe.add(1, this.siKe.get(1));
        newSiKe.add(2, this.siKe.get(2));
        newSiKe.add(3, this.siKe.get(3));

        List<List<String>> list = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            List<String> oneKe = new ArrayList<>(); // 每一课
            for (int j = 0; j < 2; j++) {
                for (int z = 0; z < 12; z++) {
                    if (newSiKe.get(i).get(j).equals(this.tianPan.get(z))) {
                        oneKe.add(this.tianGan.get(z));
                        break;
                    }
                }
            }
//            if (i == 0) oneKe.add(""); // 此处无需置空
            list.add(oneKe);
        }

        return list;

    }

    /**
     * 获取四课神将
     *
     * @return 四课神将（如：[[螣蛇, ], [太阴, 螣蛇], [天后, 朱雀], [太常, 天后]]）
     */
    public List<List<String>> getSiKeShenJiang() {

        // 处理第一课地盘天干
        String newYiKeDiPan = DaLiuRenJiChuMap.SHI_GAN_JI_GONG.get(this.siKe.get(0).get(1)); // 处理第一课，将地盘天干转换为寄宫地支
        List<List<String>> newSiKe = new ArrayList<>();
        newSiKe.add(0, Arrays.asList(this.siKe.get(0).get(0), newYiKeDiPan));
        newSiKe.add(1, this.siKe.get(1));
        newSiKe.add(2, this.siKe.get(2));
        newSiKe.add(3, this.siKe.get(3));

        List<List<String>> list = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            List<String> oneKe = new ArrayList<>(); // 每一课
            for (int j = 0; j < 2; j++) {
                for (int z = 0; z < 12; z++) {
                    if (newSiKe.get(i).get(j).equals(this.tianPan.get(z))) {
                        oneKe.add(this.shenPan.get(z));
                        break;
                    }
                }
            }
//            if (i == 0) oneKe.add(""); // 此处无需置空
            list.add(oneKe);
        }

        return list;

    }


    /**
     * 获取三传
     *
     * @return 三传（如：（如：[亥, 未, 丑]）
     */
    public List<String> getSanChuan() {
        return this.sanChuan;
    }

    /**
     * 获取三传遁干
     *
     * @return 三传遁干（如：[己, 乙, 辛]）
     */
    public List<String> getSanChuanDunGan() {

        List<String> list = new ArrayList<>();

        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 12; j++) {
                if (this.sanChuan.get(i).equals(this.tianPan.get(j))) {
                    list.add(this.tianGan.get(j));
                    break;
                }
            }
        }

        return list;

    }

    /**
     * 获取三传神将
     *
     * @return 三传神将（如：[太阴, 天后, 贵人]）
     */
    public List<String> getSanChuanShenJiang() {

        List<String> list = new ArrayList<>();

        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 12; j++) {
                if (this.sanChuan.get(i).equals(this.tianPan.get(j))) {
                    list.add(this.shenPan.get(j));
                    break;
                }
            }
        }

        return list;

    }

    /**
     * 获取三传六亲
     *
     * @return 三传六亲（如：[兄弟, 子孙, 子孙]）
     */
    public List<String> getSanChuanLiuQin() {

        Map<String, String> ganZhiShengKeLiuQinMap = DaLiuRenJiChuMap.GAN_ZHI_SHENG_KE_LIU_QIN; // 干支生克对应六亲（天干+地支为键）

        String chuChuanLiuQin = ganZhiShengKeLiuQinMap.get(this.dayGan + this.sanChuan.get(0)); // 初传六亲
        String zhongChuanLiuQin = ganZhiShengKeLiuQinMap.get(this.dayGan + this.sanChuan.get(1)); // 初传六亲
        String moChuanLiuQin = ganZhiShengKeLiuQinMap.get(this.dayGan + this.sanChuan.get(2)); // 初传六亲

        return Arrays.asList(chuChuanLiuQin, zhongChuanLiuQin, moChuanLiuQin);

    }

//-------------------------------------------------------------------------------------------------------------------------------

    /**
     * 计算十二贵人
     *
     * @param guiRenMap 贵人集合
     * @return 十二贵人（如：[太阴, 天后, 贵人, 螣蛇, 朱雀, 六合, 勾陈, 青龙, 天空, 白虎, 太常, 玄武]）
     */
    private List<String> computeShiErGuiRen(Map<String, String> guiRenMap) {

        List<String> guiRenShunXu = DaLiuRenJiChuMap.GUI_REN_SHUN_XU; // 贵人排列顺序

        String guiRen = guiRenMap.get(this.dayGan + this.hourZhi); // 贵人
        int guiRenGongWei = 1; // 贵人落入天盘的宫位
        for (int i = 0; i < 12; i++) {
            if (this.tianPan.get(i).equals(guiRen)) {
                guiRenGongWei = i;
                break;
            }
        }

        List<String> shiErGuiRen = CommonUtil.addCharToList(12, "");

        // 判断贵人排列方向（根据贵人落宫的地盘地支计算）
        if (DaLiuRenJiChuMap.GUI_REN_FANG_XIANG.get(this.diPan.get(guiRenGongWei)) == 0) {
            // 顺排
            for (int i = 0; i < 12; i++) {
                shiErGuiRen.set(guiRenGongWei, guiRenShunXu.get(i));
                guiRenGongWei++;
                if (guiRenGongWei > 11) guiRenGongWei = 0;
            }
        } else {
            // 逆排
            for (int i = 0; i < 12; i++) {
                shiErGuiRen.set(guiRenGongWei, guiRenShunXu.get(i));
                guiRenGongWei--;
                if (guiRenGongWei < 0) guiRenGongWei = 11;
            }
        }

        return shiErGuiRen;

    }

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
                "天地盘类型:" + getTianDiPanType() + "   " +
                "地盘:" + getDiPan() + "   " +
                "天盘:" + getTianPan() + "   " +
                "神盘:" + getShenPan() + "   " +
                "四课:" + getSiKe() + "   " +
                "三传:" + getSanChuan();

    }


}
