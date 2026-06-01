package xuan.core.meihua.settings;

import java.util.Date;

import lombok.Data;
import org.apache.commons.lang3.StringUtils;
import xuan.utils.DateUtil;

/**
 * 梅花易数 - 基础设置
 *
 * @author 善待
 */
@Data
public class MeiHuaJiChuSetting {

    /**
     * 姓名
     */
    private String name;

    /**
     * 占事
     */
    private String occupy;

    /**
     * 性别（0:女。1:男）
     */
    private int sex;

    /**
     * 日期（类型：yyyy-MM-dd HH:mm:ss）
     */
    private String date;

    /**
     * 日期类型（0:公历。1:农历）
     */
    private int dateType;

    /**
     * 闰月类型，日期类型为1时生效（0:不使用闰月。1:使用闰月）
     */
    private int leapMonthType;

    /**
     * 虚实岁类型（0:虚岁。1:实岁）
     */
    private int xuShiSuiType;

    /**
     * 节气类型（0:按天计算。1:按分钟计算）
     */
    private int jieQiType;

    /**
     * 排盘类型（0:日期。1:自动。2:数字。3:单数。4:双数）
     */
    private int paiPanType;

    /**
     * 数字，排盘类型为2时生效
     */
    private int shu;

    /**
     * 单数，排盘类型为3时生效
     */
    private int danShu;

    /**
     * 双数1，排盘类型为4时生效
     */
    private int shuangShuOne;

    /**
     * 双数2，排盘类型为4时生效
     */
    private int shuangShuTwo;

    /**
     * 上下卦类型，排盘类型为4时生效（0:双数求和计算上下卦。1:双数不求和计算上下卦）
     */
    private int shangXiaGuaType;

    /**
     * 动爻类型，排盘类型为4时生效（0:双数求和计算动爻。1:双数求和加时辰数计算动爻）
     */
    private int dongYaoType;

    /**
     * 年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接时刻作为新年的开始）
     */
    private int yearGanZhiType;

    /**
     * 月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
     */
    private int monthGanZhiType;

    /**
     * 日干支类型（0:晚子时日柱按明天。1:晚子时日柱按当天）
     */
    private int dayGanZhiType;

//*******************************************************************************************************************************

    /**
     * 初始化设置
     */
    public MeiHuaJiChuSetting() {

        this.name = ""; // 姓名（默认→ 空）
        this.occupy = ""; // 占事（默认→ 空）
        this.sex = 1; // 性别（默认→ 男）
        this.date = "2024-01-01 00:00:00"; // 日期（默认→ 2024-01-01 00:00:00）
        this.dateType = 0; // 日期类型（默认→ 公历）
        this.leapMonthType = 0; // 闰月类型（默认→ 不使用闰月）
        this.xuShiSuiType = 0; // 虚实岁类型（默认→ 虚岁）
        this.jieQiType = 1; // 节气类型（默认→ 按分钟计算）
        this.paiPanType = 0; // 排盘类型（默认→ 日期）
        this.shu = 111; // 数字，排盘类型为2时生效（默认→ 111）
        this.danShu = 111; // 单数，排盘类型为3时生效（默认→ 111）
        this.shuangShuOne = 111; // 双数1，排盘类型为4时生效（默认→ 111）
        this.shuangShuTwo = 111; // 双数2，排盘类型为4时生效（默认→ 111）
        this.shangXiaGuaType = 1; // 上下卦类型，排盘类型为4时生效（默认→ 双数不求和计算上下卦）
        this.dongYaoType = 0; // 动爻类型，排盘类型为4时生效（默认→ 双数求和计算动爻）
        this.yearGanZhiType = 2; // 年干支类型（默认→ 以立春交接时刻作为新年的开始）
        this.monthGanZhiType = 1; // 月干支类型（默认→ 以节交接时刻起算）
        this.dayGanZhiType = 0; // 日干支类型（默认→ 晚子时日柱按当天）

    }

//===============================================================================================================================

    /**
     * 姓名
     *
     * @param name 姓名
     */
    public void setName(String name) {
        this.name = StringUtils.isNotBlank(name) ? name : "";
    }

    /**
     * 占事
     *
     * @param occupy 占事
     */
    public void setOccupy(String occupy) {
        this.occupy = StringUtils.isNotBlank(occupy) ? occupy : "";
    }

    /**
     * 性别
     *
     * @param sex 性别（0:女。1:男）
     */
    public void setSex(int sex) {
        this.sex = (sex == 0 || sex == 1) ? sex : 1;
    }

    /**
     * 日期
     *
     * @param date 日期（类型：yyyy-MM-dd HH:mm:ss）
     */
    public void setDate(String date) {
        this.date = DateUtil.isValidDate(date) ? date : "2024-01-01 00:00:00";
    }

    /**
     * 日期类型
     *
     * @param dateType 日期类型（0:公历。1:农历）
     */
    public void setDateType(int dateType) {
        this.dateType = (dateType == 0 || dateType == 1) ? dateType : 0;
    }

    /**
     * 闰月类型，日期类型为1时生效
     *
     * @param leapMonthType 闰月类型，日期类型为1时生效（0:不使用闰月。1:使用闰月）
     */
    public void setLeapMonthType(int leapMonthType) {
        this.leapMonthType = (leapMonthType == 0 || leapMonthType == 1) ? leapMonthType : 0;
    }

    /**
     * 虚实岁类型
     *
     * @param xuShiSuiType 虚实岁类型（0:虚岁。1:实岁）
     */
    public void setXuShiSuiType(int xuShiSuiType) {
        this.xuShiSuiType = (xuShiSuiType == 0 || xuShiSuiType == 1) ? xuShiSuiType : 0;
    }

    /**
     * 节气类型
     *
     * @param jieQiType 节气类型（0:按天计算。1:按分钟计算）
     */
    public void setJieQiType(int jieQiType) {
        this.jieQiType = (jieQiType == 0 || jieQiType == 1) ? jieQiType : 1;
    }

    /**
     * 排盘类型
     *
     * @param paiPanType 排盘类型（0:日期。1:自动。2:数字。3:单数。4:双数）
     */
    public void setPaiPanType(int paiPanType) {
        this.paiPanType = (paiPanType == 0 || paiPanType == 1 || paiPanType == 2 || paiPanType == 3 || paiPanType == 4) ? paiPanType : 0;
    }

    /**
     * 数字，排盘类型为2时生效
     *
     * @param shu 数字
     */
    public void setShu(int shu) {
        this.shu = (shu > 100 && shu < 999) ? shu : 111;
    }

    /**
     * 单数，排盘类型为3时生效
     *
     * @param danShu 单数
     */
    public void setDanShu(int danShu) {
        this.danShu = (danShu > 0 && danShu < 2147483647) ? danShu : 111;
    }

    /**
     * 双数1，排盘类型为4时生效
     *
     * @param shuangShuOne 双数1
     */
    public void setShuangShuOne(int shuangShuOne) {
        this.shuangShuOne = (shuangShuOne > 0 && shuangShuOne < 2147483647) ? shuangShuOne : 111;
    }

    /**
     * 双数2，排盘类型为4时生效
     *
     * @param shuangShuTwo 双数2
     */
    public void setShuangShuTwo(int shuangShuTwo) {
        this.shuangShuTwo = (shuangShuTwo > 0 && shuangShuTwo < 2147483647) ? shuangShuTwo : 111;
    }

    /**
     * 上下卦类型，排盘类型为4时生效
     *
     * @param shangXiaGuaType 上下卦类型，排盘类型为4时生效（0:双数求和计算上下卦。1:双数不求和计算上下卦）
     */
    public void setShangXiaGuaType(int shangXiaGuaType) {
        this.shangXiaGuaType = (shangXiaGuaType == 0 || shangXiaGuaType == 1) ? shangXiaGuaType : 1;
    }

    /**
     * 动爻类型，排盘类型为4时生效
     *
     * @param dongYaoType 动爻类型，排盘类型为4时生效（0:双数求和计算动爻。1:双数求和加时辰数计算动爻）
     */
    public void setDongYaoType(int dongYaoType) {
        this.dongYaoType = (dongYaoType == 0 || dongYaoType == 1) ? dongYaoType : 0;
    }

    /**
     * 年干支类型
     *
     * @param yearGanZhiType 年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接时刻作为新年的开始）
     */
    public void setYearGanZhiType(int yearGanZhiType) {
        this.yearGanZhiType = (yearGanZhiType == 0 || yearGanZhiType == 1 || yearGanZhiType == 2) ? yearGanZhiType : 2;
    }

    /**
     * 月干支类型
     *
     * @param monthGanZhiType 月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
     */
    public void setMonthGanZhiType(int monthGanZhiType) {
        this.monthGanZhiType = (monthGanZhiType == 0 || monthGanZhiType == 1) ? monthGanZhiType : 1;
    }

    /**
     * 日干支类型
     *
     * @param dayGanZhiType 日干支类型（0:晚子时日干支按当天。1:晚子时日干支按明天）
     */
    public void setDayGanZhiType(int dayGanZhiType) {
        this.dayGanZhiType = (dayGanZhiType == 0 || dayGanZhiType == 1) ? dayGanZhiType : 0;
    }


}
