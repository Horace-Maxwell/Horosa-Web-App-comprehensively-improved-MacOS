package xuan.core.liuyao.settings;

import lombok.Data;
import org.apache.commons.lang3.StringUtils;
import xuan.utils.DateUtil;

import java.util.Date;

/**
 * 六爻 - 基础设置
 *
 * @author 善待
 */
@Data
public class LiuYaoJiChuSetting {

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
     * 排盘类型（0:日期。1:自动。2:手动）
     */
    private int paiPanType;

    /**
     * 上爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    private int liuYao;

    /**
     * 五爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    private int wuYao;

    /**
     * 四爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    private int siYao;

    /**
     * 三爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    private int sanYao;

    /**
     * 二爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    private int erYao;

    /**
     * 初爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    private int yiYao;

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
    public LiuYaoJiChuSetting() {

        this.name = ""; // 姓名（默认→ 空）
        this.occupy = ""; // 占事（默认→ 空）
        this.sex = 1; // 性别（默认→ 男）
        this.date = "2024-01-01 00:00:00"; // 日期（默认→ 2024-01-01 00:00:00）
        this.dateType = 0; // 日期类型（默认→ 公历）
        this.leapMonthType = 0; // 闰月类型，日期类型为1时生效（默认→ 不使用闰月）
        this.jieQiType = 1; // 节气类型（默认→ 按分钟计算）
        this.paiPanType = 0; // 排盘类型（默认→ 日期）
        this.liuYao = 0; // 上爻，排盘类型为2时生效（默认→ 2正1背）
        this.wuYao = 0; // 五爻，排盘类型为2时生效（默认→ 2正1背）
        this.siYao = 0; // 四爻，排盘类型为2时生效（默认→ 2正1背）
        this.sanYao = 0; // 三爻，排盘类型为2时生效（默认→ 2正1背）
        this.erYao = 0; // 二爻，排盘类型为2时生效（默认→ 2正1背）
        this.yiYao = 0; // 初爻，排盘类型为2时生效（默认→ 2正1背）
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
     * @param paiPanType 排盘类型（0:日期。1:自动。2:手动）
     */
    public void setPaiPanType(int paiPanType) {
        this.paiPanType = (paiPanType == 0 || paiPanType == 1 || paiPanType == 2) ? paiPanType : 0;
    }

    /**
     * 上爻，排盘类型为2时生效
     *
     * @param liuYao 上爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    public void setLiuYao(int liuYao) {
        this.liuYao = (liuYao == 0 || liuYao == 1 || liuYao == 2 || liuYao == 3) ? liuYao : 0;
    }

    /**
     * 五爻，排盘类型为2时生效
     *
     * @param wuYao 五爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    public void setWuYao(int wuYao) {
        this.wuYao = (wuYao == 0 || wuYao == 1 || wuYao == 2 || wuYao == 3) ? wuYao : 0;
    }

    /**
     * 四爻，排盘类型为2时生效
     *
     * @param siYao 四爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    public void setSiYao(int siYao) {
        this.siYao = (siYao == 0 || siYao == 1 || siYao == 2 || siYao == 3) ? siYao : 0;
    }

    /**
     * 三爻，排盘类型为2时生效
     *
     * @param sanYao 三爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    public void setSanYao(int sanYao) {
        this.sanYao = (sanYao == 0 || sanYao == 1 || sanYao == 2 || sanYao == 3) ? sanYao : 0;
    }

    /**
     * 二爻，排盘类型为2时生效
     *
     * @param erYao 二爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    public void setErYao(int erYao) {
        this.erYao = (erYao == 0 || erYao == 1 || erYao == 2 || erYao == 3) ? erYao : 0;
    }

    /**
     * 初爻，排盘类型为2时生效
     *
     * @param yiYao 初爻，排盘类型为2时生效（0:—（2正1背）。1:- -（1正2背）。2:— ○（0正3背）。3:- - ×（3正0背））
     */
    public void setYiYao(int yiYao) {
        this.yiYao = (yiYao == 0 || yiYao == 1 || yiYao == 2 || yiYao == 3) ? yiYao : 0;
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
