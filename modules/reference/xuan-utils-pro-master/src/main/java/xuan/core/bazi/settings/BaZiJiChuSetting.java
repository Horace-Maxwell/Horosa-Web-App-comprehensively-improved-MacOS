package xuan.core.bazi.settings;

import lombok.Data;
import org.apache.commons.lang3.StringUtils;
import xuan.utils.DateUtil;

import java.util.Date;

/**
 * 八字 - 基础设置
 *
 * @author 善待
 */
@Data
public class BaZiJiChuSetting {

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
     * 起运流派类型（0:按天数和时辰数计算：3天1年、1天4个月、1时辰10天。1:按分钟数计算：4320分=1年、360分=1月、12分=1天、1分=2小时）
     */
    private int qiYunLiuPaiType;

    /**
     * 人元司令分野类型（0:子平真诠法诀。1:渊海子平法诀。2:星平会海法诀。3:三命通会法诀。4:神峰通考法诀。5:万育吾之法诀）
     */
    private int renYuanType;

    /**
     * 大运轮数（最小10轮，最大16轮）
     */
    private int daYunLunShu;

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
    public BaZiJiChuSetting() {

        this.name = ""; // 姓名（默认→ 空）
        this.occupy = ""; // 占事（默认→ 空）
        this.sex = 1; // 性别（默认→ 男）
        this.date = "2024-01-01 00:00:00"; // 日期（默认→ 2024-01-01 00:00:00）
        this.dateType = 0; // 日期类型（默认→ 公历）
        this.leapMonthType = 0; // 闰月类型，日期类型为1时生效（默认→ 不使用闰月）
        this.xuShiSuiType = 0; // 虚实岁类型（默认→ 虚岁）
        this.jieQiType = 1; // 节气类型（默认→ 按分钟计算）
        this.qiYunLiuPaiType = 1; // 起运流派类型（默认→ 按分钟数计算：4320分=1年、360分=1月、12分=1天、1分=2小时）
        this.renYuanType = 0; // 人元司令分野类型（默认→ 子平真诠法诀）
        this.daYunLunShu = 10; // 大运轮数（默认→ 10轮）
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
     * @param date 日期
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
     * 起运流派类型
     *
     * @param qiYunLiuPaiType 起运流派类型（0:按天数和时辰数计算：3天1年、1天4个月、1时辰10天。1:按分钟数计算：4320分=1年、360分=1月、12分=1天、1分=2小时）
     */
    public void setQiYunLiuPaiType(int qiYunLiuPaiType) {
        this.qiYunLiuPaiType = (qiYunLiuPaiType == 0 || qiYunLiuPaiType == 1) ? qiYunLiuPaiType : 1;
    }

    /**
     * 人元司令分野类型
     *
     * @param renYuanType 人元司令分野类型（0:子平真诠法诀。1:渊海子平法诀。2:星平会海法诀。3:三命通会法诀。4:神峰通考法诀。5:万育吾之法诀）
     */
    public void setRenYuanType(int renYuanType) {
        this.renYuanType = (renYuanType == 0 || renYuanType == 1 || renYuanType == 2 || renYuanType == 3 || renYuanType == 4 || renYuanType == 5) ? renYuanType : 0;
    }

    /**
     * 大运轮数
     *
     * @param daYunLunShu 大运轮数（最小10轮，最大16轮）
     */
    public void setDaYunLunShu(int daYunLunShu) {
        if (daYunLunShu < 10 || daYunLunShu > 16) {
            this.daYunLunShu = 10;
        } else {
            this.daYunLunShu = daYunLunShu;
        }
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
