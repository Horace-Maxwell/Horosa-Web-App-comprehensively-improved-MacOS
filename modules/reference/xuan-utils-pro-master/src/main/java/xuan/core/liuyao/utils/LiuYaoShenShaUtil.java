package xuan.core.liuyao.utils;

import java.util.Map;
import java.util.HashMap;

import lombok.Data;
import org.apache.commons.lang3.StringUtils;
import xuan.utils.CommonUtil;
import xuan.core.liuyao.maps.LiuYaoShenShaMap;
import xuan.core.liuyao.settings.LiuYaoShenShaSetting;

/**
 * 六爻 - 神煞工具
 *
 * @author 善待
 */
@Data
public class LiuYaoShenShaUtil {

    /**
     * 六爻 - 神煞设置
     */
    private LiuYaoShenShaSetting liuYaoShenShaSetting;

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
     * 神煞
     */
    private Map<String, String> shenSha = new HashMap<>();

//*******************************************************************************************************************************

    /**
     * 初始化
     *
     * @param liuYaoShenShaSetting 六爻 - 神煞设置
     * @param yearGanZhi           年干支
     * @param monthGanZhi          月干支
     * @param dayGanZhi            日干支
     * @param hourGanZhi           时干支
     */
    public LiuYaoShenShaUtil(LiuYaoShenShaSetting liuYaoShenShaSetting, String yearGanZhi, String monthGanZhi, String dayGanZhi, String hourGanZhi) {

        // 1、八字设置
        this.liuYaoShenShaSetting = liuYaoShenShaSetting; // 六爻 - 神煞设置

        // 2、处理数据
        this.yearGanZhi = (StringUtils.isNotBlank(yearGanZhi) && yearGanZhi.length() == 2) ? yearGanZhi : CommonUtil.EMPTY2; // 年干支
        this.yearGan = this.yearGanZhi.substring(0, 1); // 年干
        this.yearZhi = this.yearGanZhi.substring(1, 2); // 年支
        this.monthGanZhi = (StringUtils.isNotBlank(monthGanZhi) && monthGanZhi.length() == 2) ? monthGanZhi : CommonUtil.EMPTY2; // 月干支
        this.monthGan = this.monthGanZhi.substring(0, 1); // 月干
        this.monthZhi = this.monthGanZhi.substring(1, 2); // 月支
        this.dayGanZhi = (StringUtils.isNotBlank(dayGanZhi) && dayGanZhi.length() == 2) ? dayGanZhi : CommonUtil.EMPTY2; // 日干支
        this.dayGan = this.dayGanZhi.substring(0, 1); // 日干
        this.dayZhi = this.dayGanZhi.substring(1, 2); // 日支
        this.hourGanZhi = (StringUtils.isNotBlank(hourGanZhi) && hourGanZhi.length() == 2) ? hourGanZhi : CommonUtil.EMPTY2; // 时干支
        this.hourGan = this.hourGanZhi.substring(0, 1); // 时干
        this.hourZhi = this.hourGanZhi.substring(1, 2); // 时支

        // 3、初始化数据
        initializeShenSha(); // 初始化神煞

    }

    /**
     * 初始化神煞
     */
    private void initializeShenSha() {

        Map<String, String> shenSha = new HashMap<>();
        if (this.liuYaoShenShaSetting.getTaiJiGuiRen() == 0) shenSha.put("taiJiGuiRen", getShenSha2(LiuYaoShenShaMap.TAI_JI_GUI_REN)); // 太极贵人
        if (this.liuYaoShenShaSetting.getTianYiGuiRen() == 0) shenSha.put("tianYiGuiRen", LiuYaoShenShaMap.TIAN_YI_GUI_REN.get(getDayGan())); // 天乙贵人
        if (this.liuYaoShenShaSetting.getFuXingGuiRen() == 0) shenSha.put("fuXingGuiRen", getShenSha3(LiuYaoShenShaMap.FU_XING_GUI_REN)); // 福星贵人
        if (this.liuYaoShenShaSetting.getWenChangGuiRen() == 0) shenSha.put("wenChangGuiRen", LiuYaoShenShaMap.WEN_CHANG_GUI_REN.get(getDayGan())); // 文昌贵人
        if (this.liuYaoShenShaSetting.getTianChuGuiRen() == 0) shenSha.put("tianChuGuiRen", LiuYaoShenShaMap.TIAN_CHU_GUI_REN.get(getDayGan())); // 天厨贵人
        if (this.liuYaoShenShaSetting.getYueDeGuiRen() == 0) shenSha.put("yueDeGuiRen", LiuYaoShenShaMap.YUE_DE_GUI_REN.get(getMonthZhi())); // 月德贵人
        if (this.liuYaoShenShaSetting.getTianDeGuiRen() == 0) shenSha.put("tianDeGuiRen", LiuYaoShenShaMap.TIAN_DE_GUI_REN.get(getMonthZhi())); // 天德贵人
        if (this.liuYaoShenShaSetting.getTangFuGuoYin() == 0) shenSha.put("tangFuGuoYin", LiuYaoShenShaMap.TANG_FU_GUO_YIN.get(getYearZhi())); // 唐符国印
        if (this.liuYaoShenShaSetting.getTianYuanLu() == 0) shenSha.put("tianYuanLu", LiuYaoShenShaMap.TIAN_YUAN_LU.get(getDayGan())); // 天元禄
        if (this.liuYaoShenShaSetting.getHuaGai() == 0) shenSha.put("huaGai", getShenSha1(LiuYaoShenShaMap.HUA_GAI)); // 华盖
        if (this.liuYaoShenShaSetting.getYiMa() == 0) shenSha.put("yiMa", LiuYaoShenShaMap.YI_MA.get(getDayZhi())); // 驿马
        if (this.liuYaoShenShaSetting.getTianMa() == 0) shenSha.put("tianMa", LiuYaoShenShaMap.TIAN_MA.get(getDayZhi())); // 天马
        if (this.liuYaoShenShaSetting.getLuMa() == 0) shenSha.put("luMa", LiuYaoShenShaMap.LU_MA.get(getDayGan())); // 禄马
        if (this.liuYaoShenShaSetting.getJieSha() == 0) shenSha.put("jieSha", LiuYaoShenShaMap.JIE_SHA.get(getDayZhi())); // 劫煞
        if (this.liuYaoShenShaSetting.getJiangXing() == 0) shenSha.put("jiangXing", getShenSha1(LiuYaoShenShaMap.JIANG_XING)); // 将星
        if (this.liuYaoShenShaSetting.getXianChi() == 0) shenSha.put("xianChi", LiuYaoShenShaMap.XIAN_CHI.get(getDayZhi())); // 咸池
        if (this.liuYaoShenShaSetting.getTianXi() == 0) shenSha.put("tianXi", LiuYaoShenShaMap.TIAN_XI.get(getMonthZhi())); // 天喜
        if (this.liuYaoShenShaSetting.getZaiSha() == 0) shenSha.put("zaiSha", LiuYaoShenShaMap.ZAI_SHA.get(getDayZhi())); // 灾煞
        if (this.liuYaoShenShaSetting.getTianYi() == 0) shenSha.put("tianYi", LiuYaoShenShaMap.TIAN_YI.get(getMonthZhi())); // 天医
        if (this.liuYaoShenShaSetting.getMouXing() == 0) shenSha.put("mouXing", LiuYaoShenShaMap.MOU_XING.get(getDayZhi())); // 谋星
        if (this.liuYaoShenShaSetting.getHuangEn() == 0) shenSha.put("huangEn", LiuYaoShenShaMap.HUANG_EN.get(getMonthZhi())); // 皇恩
        if (this.liuYaoShenShaSetting.getYangRen() == 0) shenSha.put("yangRen", LiuYaoShenShaMap.TIAN_REN.get(getDayGan())); // 阳刃
        if (this.liuYaoShenShaSetting.getFeiRen() == 0) shenSha.put("feiRen", LiuYaoShenShaMap.FEI_REN.get(getDayGan())); // 飞刃
        this.shenSha = shenSha;

    }

//===============================================================================================================================

    /**
     * 获取神煞
     *
     * @return 神煞（如：{tianYuanLu=寅}）
     */
    public Map<String, String> getShenSha() {
        return this.shenSha;
    }

//-------------------------------------------------------------------------------------------------------------------------------

    /**
     * 通用：添加神煞【华盖、将星】
     *
     * @param map 神煞常量
     * @return 神煞
     */
    private String getShenSha1(Map<String, String> map) {

        if (null != map.get(getYearZhi() + getMonthZhi())) return map.get(getYearZhi() + getMonthZhi());
        if (null != map.get(getYearZhi() + getDayZhi())) return map.get(getYearZhi() + getDayZhi());
        if (null != map.get(getYearZhi() + getHourZhi())) return map.get(getYearZhi() + getHourZhi());
        if (null != map.get(getDayZhi() + getYearZhi())) return map.get(getDayZhi() + getYearZhi());
        if (null != map.get(getDayZhi() + getMonthZhi())) return map.get(getDayZhi() + getMonthZhi());
        if (null != map.get(getDayZhi() + getHourZhi())) return map.get(getDayZhi() + getHourZhi());

        return CommonUtil.EMPTY1;

    }

    /**
     * 通用：添加神煞【太极贵人】
     *
     * @param map 神煞常量
     * @return 神煞
     */
    private String getShenSha2(Map<String, String> map) {

        if (null != map.get(getYearGan() + getYearZhi())) return map.get(getYearGan() + getYearZhi());
        if (null != map.get(getYearGan() + getMonthZhi())) return map.get(getYearGan() + getMonthZhi());
        if (null != map.get(getYearGan() + getDayZhi())) return map.get(getYearGan() + getDayZhi());
        if (null != map.get(getYearGan() + getHourZhi())) return map.get(getYearGan() + getHourZhi());
        if (null != map.get(getDayGan() + getYearZhi())) return map.get(getDayGan() + getYearZhi());
        if (null != map.get(getDayGan() + getMonthZhi())) return map.get(getDayGan() + getMonthZhi());
        if (null != map.get(getDayGan() + getDayZhi())) return map.get(getDayGan() + getDayZhi());
        if (null != map.get(getDayGan() + getHourZhi())) return map.get(getDayGan() + getHourZhi());

        return CommonUtil.EMPTY1;

    }

    /**
     * 通用：添加神煞【福星贵人】
     *
     * @param map 神煞常量
     * @return 神煞
     */
    private String getShenSha3(Map<String, String> map) {

        if (null != map.get(getDayGan() + getYearZhi())) return map.get(getDayGan() + getYearZhi());
        if (null != map.get(getDayGan() + getMonthZhi())) return map.get(getDayGan() + getMonthZhi());
        if (null != map.get(getDayGan() + getDayZhi())) return map.get(getDayGan() + getDayZhi());
        if (null != map.get(getDayGan() + getHourZhi())) return map.get(getDayGan() + getHourZhi());

        return CommonUtil.EMPTY1;

    }


}
