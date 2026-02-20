package xuan.core.ziwei.settings;

import lombok.Data;
import org.apache.commons.lang3.StringUtils;
import xuan.utils.DateUtil;

import java.util.Date;

/**
 * 紫微斗数 - 基础设置
 *
 * @author 善待
 */
@Data
public class ZiWeiJiChuSetting {

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
     * 五行局类型（0:按年干+命宫地支计算。1:按命宫天干+命宫地支计算）
     */
    private int wuXingJuType;

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
    public ZiWeiJiChuSetting() {

        this.name = ""; // 姓名（默认→ 空）
        this.occupy = ""; // 占事（默认→ 空）
        this.sex = 1; // 性别（默认→ 男）
        this.date = "2024-01-01 00:00:00"; // 日期（默认→ 2024-01-01 00:00:00）
        this.dateType = 0; // 日期类型（默认→ 公历）
        this.leapMonthType = 0; // 闰月类型，日期类型为1时生效（默认→ 不使用闰月）
        this.xuShiSuiType = 0; // 虚实岁类型（默认→ 虚岁）
        this.jieQiType = 1; // 节气类型（默认→ 按分钟计算）
        this.wuXingJuType = 0; // 五行局类型（默认→ 按年干+命宫地支计算）
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
     * 五行局类型
     *
     * @param wuXingJuType 五行局类型（0:按年干+命宫地支计算。1:按命宫天干+命宫地支计算）
     */
    public void setWuXingJuType(int wuXingJuType) {
        this.wuXingJuType = (wuXingJuType == 0 || wuXingJuType == 1) ? wuXingJuType : 0;
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
