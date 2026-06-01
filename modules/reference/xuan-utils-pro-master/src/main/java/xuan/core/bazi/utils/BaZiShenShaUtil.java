package xuan.core.bazi.utils;

import java.util.Map;
import java.util.List;
import java.util.ArrayList;

import org.apache.commons.lang3.StringUtils;
import xuan.utils.CommonUtil;
import xuan.core.bazi.maps.BaZiJiChuMap;
import xuan.core.bazi.maps.BaZiShenShaMap;
import xuan.core.bazi.settings.BaZiShenShaSetting;

/**
 * 八字 - 神煞工具
 *
 * @author 善待
 */
public class BaZiShenShaUtil {

    /**
     * 八字 - 神煞设置
     */
    private BaZiShenShaSetting baZiShenShaSetting;

    /**
     * 性别（0:女。1:男）
     */
    private int sex;
    /**
     * 季节
     */
    private String jiJie;
    /**
     * 年干支纳音五行
     */
    private String yearGanZhiNaYinWuXing;

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
     * 任意干
     */
    private String arbitraryGan;

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
     * 任意支（除四柱之外）
     */
    private String arbitraryZhi;

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
     * 任意干支（除四柱之外）
     */
    private String arbitraryGanZhi;

    /**
     * 年干支神煞
     */
    private List<String> yearGanZhiShenSha = new ArrayList<>();
    /**
     * 月干支神煞
     */
    private List<String> monthGanZhiShenSha = new ArrayList<>();
    /**
     * 日干支神煞
     */
    private List<String> dayGanZhiShenSha = new ArrayList<>();
    /**
     * 时干支神煞
     */
    private List<String> hourGanZhiShenSha = new ArrayList<>();
    /**
     * 任意干支神煞（除四柱之外）
     */
    private List<String> arbitraryGanZhiShenSha = new ArrayList<>();

//*******************************************************************************************************************************

    /**
     * 初始化
     *
     * @param baZiShenShaSetting    八字 - 神煞设置
     * @param sex                   性别（0:女。1:男）
     * @param jiJie                 季节
     * @param yearGanZhiNaYinWuXing 年干支纳音五行
     * @param yearGanZhi            年干支（若为空或格式错误则不计算此柱神煞）
     * @param monthGanZhi           月干支（若为空或格式错误则不计算此柱神煞）
     * @param dayGanZhi             日干支（若为空或格式错误则不计算此柱神煞）
     * @param hourGanZhi            时干支（若为空或格式错误则不计算此柱神煞）
     * @param arbitraryGanZhi       任意干支，除四柱之外（若为空或格式错误则不计算此柱神煞）
     */
    public BaZiShenShaUtil(BaZiShenShaSetting baZiShenShaSetting, int sex, String jiJie, String yearGanZhiNaYinWuXing, String yearGanZhi, String monthGanZhi, String dayGanZhi, String hourGanZhi, String arbitraryGanZhi) {

        // 1、八字设置
        this.baZiShenShaSetting = baZiShenShaSetting; // 八字 - 神煞设置

        // 2、处理数据
        this.sex = sex; // 性别
        this.jiJie = jiJie; // 季节
        this.yearGanZhiNaYinWuXing = yearGanZhiNaYinWuXing; // 年干支纳音五行
        this.yearGanZhi = (StringUtils.isNoneBlank(yearGanZhi) && yearGanZhi.length() == 2) ? yearGanZhi : CommonUtil.EMPTY2; // 年干支
        this.monthGanZhi = (StringUtils.isNoneBlank(monthGanZhi) && monthGanZhi.length() == 2) ? monthGanZhi : CommonUtil.EMPTY2; // 月干支
        this.dayGanZhi = (StringUtils.isNoneBlank(dayGanZhi) && dayGanZhi.length() == 2) ? dayGanZhi : CommonUtil.EMPTY2; // 日干支
        this.hourGanZhi = (StringUtils.isNoneBlank(hourGanZhi) && hourGanZhi.length() == 2) ? hourGanZhi : CommonUtil.EMPTY2; // 时干支
        this.arbitraryGanZhi = (StringUtils.isNoneBlank(arbitraryGanZhi) && arbitraryGanZhi.length() == 2) ? arbitraryGanZhi : CommonUtil.EMPTY2; // 任意干支，除四柱之外
        this.yearGan = this.yearGanZhi.substring(0, 1); // 年干
        this.monthGan = this.monthGanZhi.substring(0, 1); // 月干
        this.dayGan = this.dayGanZhi.substring(0, 1); // 日干
        this.hourGan = this.hourGanZhi.substring(0, 1); // 时干
        this.arbitraryGan = this.arbitraryGanZhi.substring(0, 1); // 任意干，除四柱之外
        this.yearZhi = this.yearGanZhi.substring(1, 2); // 年支
        this.monthZhi = this.monthGanZhi.substring(1, 2); // 月支
        this.dayZhi = this.dayGanZhi.substring(1, 2); // 日支
        this.hourZhi = this.hourGanZhi.substring(1, 2); // 时支
        this.arbitraryZhi = this.arbitraryGanZhi.substring(1, 2); // 任意支，除四柱之外

        // 3、初始化数据
        initializeShenSha(); // 初始化神煞

    }

    /**
     * 初始化神煞
     */
    private void initializeShenSha() {

        // 1、计算数据
        if (this.baZiShenShaSetting.getTaiJiGuiRen() == 0) taiJiGuiRen(); // 太极贵人
        if (this.baZiShenShaSetting.getTianYiGuiRen() == 0) tianYiGuiRen(); // 天乙贵人
        if (this.baZiShenShaSetting.getFuXingGuiRen() == 0) fuXingGuiRen(); // 福星贵人
        if (this.baZiShenShaSetting.getWenChangGuiRen() == 0) wenChangGuiRen(); // 文昌贵人
        if (this.baZiShenShaSetting.getTianChuGuiRen() == 0) tianChuGuiRen(); // 天厨贵人
        if (this.baZiShenShaSetting.getYueDeGuiRen() == 0) yueDeGuiRen(); // 月德贵人
        if (this.baZiShenShaSetting.getDeXiuGuiRen() == 0) deXiuGuiRen(); // 德秀贵人
        if (this.baZiShenShaSetting.getTianDeGuiRen() == 0) tianDeGuiRen(); // 天德贵人
        if (this.baZiShenShaSetting.getTianGuanGuiRen() == 0) tianGuanGuiRen(); // 天官贵人
        if (this.baZiShenShaSetting.getSanQiGuiRen() == 0) sanQiGuiRen(); // 三奇贵人
        if (this.baZiShenShaSetting.getYinZhuYangShou() == 0) yinZhuYangShou(); // 阴注阳受
        if (this.baZiShenShaSetting.getShiEDaBai() == 0) shiEDaBai(); // 十恶大败
        if (this.baZiShenShaSetting.getYinChaYangCuo() == 0) yinChaYangCuo(); // 阴差阳错
        if (this.baZiShenShaSetting.getTianLuoDiWang() == 0) tianLuoDiWang(); // 天罗地网
        if (this.baZiShenShaSetting.getTianDeHe() == 0) tianDeHe(); // 天德合
        if (this.baZiShenShaSetting.getYueDeHe() == 0) yueDeHe(); // 月德合
        if (this.baZiShenShaSetting.getLiuXiuRi() == 0) liuXiuRi(); // 六秀日
        if (this.baZiShenShaSetting.getShiLingRi() == 0) shiLingRi(); // 十灵日
        if (this.baZiShenShaSetting.getKuiGangRi() == 0) kuiGangRi(); // 魁罡日
        if (this.baZiShenShaSetting.getBaZhuanRi() == 0) baZhuanRi(); // 八专日
        if (this.baZiShenShaSetting.getJiuChouRi() == 0) jiuChouRi(); // 九丑日
        if (this.baZiShenShaSetting.getSiFeiRi() == 0) siFeiRi(); // 四废日
        if (this.baZiShenShaSetting.getGuLuanSha() == 0) guLuanSha(); // 孤鸾煞
        if (this.baZiShenShaSetting.getHongYanSha() == 0) hongYanSha(); // 红艳煞
        if (this.baZiShenShaSetting.getGouJiaoSha() == 0) gouJiaoSha(); // 勾绞煞
        if (this.baZiShenShaSetting.getTongZiSha() == 0) tongZiSha(); // 童子煞
        if (this.baZiShenShaSetting.getChongTianSha() == 0) chongTianSha(); // 冲天煞
        if (this.baZiShenShaSetting.getCiGuan() == 0) ciGuan(); // 词馆
        if (this.baZiShenShaSetting.getXueTang() == 0) xueTang(); // 学堂
        if (this.baZiShenShaSetting.getHuaGai() == 0) huaGai(); // 华盖
        if (this.baZiShenShaSetting.getGuoYin() == 0) guoYin(); // 国印
        if (this.baZiShenShaSetting.getJinShen() == 0) jinShen(); // 金神
        if (this.baZiShenShaSetting.getJinYu() == 0) jinYu(); // 金舆
        if (this.baZiShenShaSetting.getGongLu() == 0) gongLu(); // 拱禄
        if (this.baZiShenShaSetting.getLuShen() == 0) luShen(); // 禄神
        if (this.baZiShenShaSetting.getJiangXing() == 0) jiangXing(); // 将星
        if (this.baZiShenShaSetting.getTaoHua() == 0) taoHua(); // 桃花
        if (this.baZiShenShaSetting.getTianXi() == 0) tianXi(); // 天喜
        if (this.baZiShenShaSetting.getHongLuan() == 0) hongLuan(); // 红鸾
        if (this.baZiShenShaSetting.getTianYi() == 0) tianYi(); // 天医
        if (this.baZiShenShaSetting.getTianShe() == 0) tianShe(); // 天赦
        if (this.baZiShenShaSetting.getYiMa() == 0) yiMa(); // 驿马
        if (this.baZiShenShaSetting.getKongWang() == 0) kongWang(); // 空亡
        if (this.baZiShenShaSetting.getJieKong() == 0) jieKong(); // 截空
        if (this.baZiShenShaSetting.getYangRen() == 0) yangRen(); // 羊刃
        if (this.baZiShenShaSetting.getFeiRen() == 0) feiRen(); // 飞刃
        if (this.baZiShenShaSetting.getLiuXia() == 0) liuXia(); // 流霞
        if (this.baZiShenShaSetting.getJieSha() == 0) jieSha(); // 劫煞
        if (this.baZiShenShaSetting.getWangShen() == 0) wangShen(); // 亡神
        if (this.baZiShenShaSetting.getDiaoKe() == 0) diaoKe(); // 吊客
        if (this.baZiShenShaSetting.getPiMa() == 0) piMa(); // 披麻
        if (this.baZiShenShaSetting.getSangMen() == 0) sangMen(); // 丧门
        if (this.baZiShenShaSetting.getZaiSha() == 0) zaiSha(); // 灾煞
        if (this.baZiShenShaSetting.getGuChen() == 0) guChen(); // 孤辰
        if (this.baZiShenShaSetting.getGuaXiu() == 0) guaXiu(); // 寡宿
        if (this.baZiShenShaSetting.getYuanChen() == 0) yuanChen(); // 元辰
        if (this.baZiShenShaSetting.getXueRen() == 0) xueRen(); // 血刃
        if (this.baZiShenShaSetting.getTianZhuan() == 0) tianZhuan(); // 天转
        if (this.baZiShenShaSetting.getDiZhuan() == 0) diZhuan(); // 地转
        if (this.baZiShenShaSetting.getLiuE() == 0) liuE(); // 六厄

        // 2、删除重复数据
        this.yearGanZhiShenSha = CommonUtil.removeDuplicatesList(this.yearGanZhiShenSha); // 年干支神煞
        this.monthGanZhiShenSha = CommonUtil.removeDuplicatesList(this.monthGanZhiShenSha); // 月干支神煞
        this.dayGanZhiShenSha = CommonUtil.removeDuplicatesList(this.dayGanZhiShenSha); // 日干支神煞
        this.hourGanZhiShenSha = CommonUtil.removeDuplicatesList(this.hourGanZhiShenSha); // 时干支神煞
        this.arbitraryGanZhiShenSha = CommonUtil.removeDuplicatesList(this.arbitraryGanZhiShenSha); // 任意干支神煞（除四柱之外）

    }

//===============================================================================================================================

    /**
     * 获取年干支神煞
     *
     * @return 年干支神煞（如：[太极贵人]）
     */
    public List<String> getYearGanZhiShenSha() {
        return this.yearGanZhiShenSha;
    }

    /**
     * 获取月干支神煞
     *
     * @return 月干支神煞（如：[太极贵人]）
     */
    public List<String> getMonthGanZhiShenSha() {
        return this.monthGanZhiShenSha;
    }

    /**
     * 获取日干支神煞
     *
     * @return 日干支神煞（如：[太极贵人]）
     */
    public List<String> getDayGanZhiShenSha() {
        return this.dayGanZhiShenSha;
    }

    /**
     * 获取时干支神煞
     *
     * @return 时干支神煞（如：[太极贵人]）
     */
    public List<String> getHourGanZhiShenSha() {
        return this.hourGanZhiShenSha;
    }

    /**
     * 获取任意干支神煞（除四柱之外）
     *
     * @return 任意干支神煞，除四柱之外（如：[太极贵人]）
     */
    public List<String> getArbitraryGanZhiShenSha() {
        return this.arbitraryGanZhiShenSha;
    }

//-------------------------------------------------------------------------------------------------------------------------------

    /**
     * 计算太极贵人
     */
    private void taiJiGuiRen() {

        Map<String, String> map = BaZiShenShaMap.TAI_JI_GUI_REN; // 太极贵人（年干\日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.yearGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearGan + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算天乙贵人
     */
    private void tianYiGuiRen() {

        Map<String, String> map = BaZiShenShaMap.TIAN_YI_GUI_REN; // 天乙贵人（年干\日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.yearGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearGan + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算福星贵人
     */
    private void fuXingGuiRen() {

        Map<String, String> map = BaZiShenShaMap.FU_XING_GUI_REN; // 福星贵人（年干\日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.yearGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearGan + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算文昌贵人
     */
    private void wenChangGuiRen() {

        Map<String, String> map = BaZiShenShaMap.WEN_CHANG_GUI_REN; // 文昌贵人（年干\日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.yearGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearGan + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算天厨贵人
     */
    private void tianChuGuiRen() {

        Map<String, String> map = BaZiShenShaMap.TIAN_CHU_GUI_REN; // 天厨贵人（年干\日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.yearGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearGan + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算国印
     */
    private void guoYin() {

        Map<String, String> map = BaZiShenShaMap.GUO_YIN; // 国印（年干\日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.yearGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearGan + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算金舆
     */
    private void jinYu() {

        Map<String, String> map = BaZiShenShaMap.JIN_YU; // 金舆（年干\日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.yearGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearGan + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算红艳煞
     */
    private void hongYanSha() {

        Map<String, String> map = BaZiShenShaMap.HONG_YAN_SHA; // 红艳煞（日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算羊刃
     */
    private void yangRen() {

        Map<String, String> map = BaZiShenShaMap.YANG_REN; // 羊刃（日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算飞刃
     */
    private void feiRen() {

        Map<String, String> map = BaZiShenShaMap.FEI_REN; // 飞刃（日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算流霞
     */
    private void liuXia() {

        Map<String, String> map = BaZiShenShaMap.LIU_XIA; // 流霞（日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算禄神
     */
    private void luShen() {

        Map<String, String> map = BaZiShenShaMap.LU_SHEN; // 禄神（日干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.dayGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.dayGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGan + this.arbitraryZhi));

    }

    /**
     * 计算驿马
     */
    private void yiMa() {

        Map<String, String> map = BaZiShenShaMap.YI_MA; // 驿马（年支\日支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayZhi + this.monthZhi));
//        this.dayGanZhiShenSha.add(map.get(this.dayZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayZhi + this.arbitraryZhi));

    }

    /**
     * 计算劫煞
     */
    private void jieSha() {

        Map<String, String> map = BaZiShenShaMap.JIE_SHA; // 劫煞（年支\日支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayZhi + this.monthZhi));
//        this.dayGanZhiShenSha.add(map.get(this.dayZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayZhi + this.arbitraryZhi));
    }

    /**
     * 计算将星
     */
    private void jiangXing() {

        Map<String, String> map = BaZiShenShaMap.JIANG_XING; // 将星（年支\日支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayZhi + this.monthZhi));
//        this.dayGanZhiShenSha.add(map.get(this.dayZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayZhi + this.arbitraryZhi));

    }

    /**
     * 计算桃花
     */
    private void taoHua() {

        Map<String, String> map = BaZiShenShaMap.TAO_HUA; // 桃花（年支\日支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayZhi + this.monthZhi));
//        this.dayGanZhiShenSha.add(map.get(this.dayZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayZhi + this.arbitraryZhi));

    }

    /**
     * 计算亡神
     */
    private void wangShen() {

        Map<String, String> map = BaZiShenShaMap.WANG_SHEN; // 亡神（年支\日支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayZhi + this.monthZhi));
//        this.dayGanZhiShenSha.add(map.get(this.dayZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayZhi + this.arbitraryZhi));

    }

    /**
     * 计算吊客
     */
    private void diaoKe() {

        Map<String, String> map = BaZiShenShaMap.DIAO_KE; // 吊客（年支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

    }

    /**
     * 计算披麻
     */
    private void piMa() {

        Map<String, String> map = BaZiShenShaMap.PI_MA; // 披麻（年支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

    }

    /**
     * 计算天官贵人
     */
    private void tianGuanGuiRen() {

        Map<String, String> map = BaZiShenShaMap.TIAN_GUAN_GUI_REN; // 天官贵人（年干+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.yearGan + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearGan + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearGan + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGan + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearGan + this.arbitraryZhi));

    }

    /**
     * 计算天喜
     */
    private void tianXi() {

        Map<String, String> map = BaZiShenShaMap.TIAN_XI; // 天喜（年支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

    }

    /**
     * 计算勾绞煞
     */
    private void gouJiaoSha() {

        Map<String, String> map = BaZiShenShaMap.GOU_JIAO_SHA; // 勾绞煞（年支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

    }

    /**
     * 计算红鸾
     */
    private void hongLuan() {

        Map<String, String> map = BaZiShenShaMap.HONG_LUAN; // 红鸾（年支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

    }

    /**
     * 计算丧门
     */
    private void sangMen() {

        Map<String, String> map = BaZiShenShaMap.SANG_MEN; // 丧门（年支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

    }

    /**
     * 计算灾煞
     */
    private void zaiSha() {

        Map<String, String> map = BaZiShenShaMap.ZAI_SHA; // 灾煞（年支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

    }

    /**
     * 计算孤辰
     */
    private void guChen() {

        Map<String, String> map = BaZiShenShaMap.GU_CHEN; // 孤辰（年支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

    }

    /**
     * 计算寡宿
     */
    private void guaXiu() {

        Map<String, String> map = BaZiShenShaMap.GUA_XIU; // 寡宿（年支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

    }

    /**
     * 计算元辰
     */
    private void yuanChen() {

        Map<String, String> map1 = BaZiShenShaMap.YUAN_CHEN_YANG_NAN; // 元辰（年支+其余地支），阳男阴女
        Map<String, String> map2 = BaZiShenShaMap.YUAN_CHEN_YIN_NAN; // 元辰（年支+其余地支），阴男阳女

        Map<String, String> map;
        String sex = this.sex == 0 ? "女" : "男";
        String yearGanYinYangSex = BaZiJiChuMap.TIAN_GAN_YIN_YANG.get(this.yearGan) + sex;
        if ("阳男".equals(yearGanYinYangSex) || "阴女".equals(yearGanYinYangSex)) {
            map = map1;
        } else {
            map = map2;
        }

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

    }

    /**
     * 计算血刃
     */
    private void xueRen() {

        Map<String, String> map = BaZiShenShaMap.XUE_REN; // 血刃（月支+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryZhi));

    }

    /**
     * 计算天医
     */
    private void tianYi() {

        Map<String, String> map = BaZiShenShaMap.TIAN_YI; // 天医（月支+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearZhi));
//        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryZhi));

    }

    /**
     * 计算天德合
     */
    private void tianDeHe() {

        Map<String, String> map = BaZiShenShaMap.TIAN_DE_HE; // 天德合（月支+其余天干或地支为键）

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearGan));
        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthGan));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayGan));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourGan));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryGan));

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearZhi));
//        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryZhi));

    }

    /**
     * 计算月德合
     */
    private void yueDeHe() {

        Map<String, String> map = BaZiShenShaMap.YUE_DE_HE; // 月德合（月支+其余天干为键）

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearGan));
        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthGan));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayGan));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourGan));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryGan));

    }

    /**
     * 计算词馆
     */
    private void ciGuan() {

        Map<String, String> map = BaZiShenShaMap.CI_GUAN_LU_MING; // 词馆（年柱纳音五行+干支为键），禄命法

//        if (null != map.get(this.yearGanZhiNaYinWuXing + this.yearZhi) && null == map.get(this.yearGanZhiNaYinWuXing + this.yearGanZhi)) {
//            this.yearGanZhiShenSha.add("词馆");
//        } else if (null != map.get(this.yearGanZhiNaYinWuXing + this.yearGanZhi)) {
//            this.yearGanZhiShenSha.add("正词馆");
//        }

        if (null != map.get(this.yearGanZhiNaYinWuXing + this.monthZhi) && null == map.get(this.yearGanZhiNaYinWuXing + this.monthGanZhi)) {
            this.monthGanZhiShenSha.add("词馆");
        } else if (null != map.get(this.yearGanZhiNaYinWuXing + this.monthGanZhi)) {
            this.monthGanZhiShenSha.add("正词馆");
        }

        if (null != map.get(this.yearGanZhiNaYinWuXing + this.dayZhi) && null == map.get(this.yearGanZhiNaYinWuXing + this.dayGanZhi)) {
            this.dayGanZhiShenSha.add("词馆");
        } else if (null != map.get(this.yearGanZhiNaYinWuXing + this.dayGanZhi)) {
            this.dayGanZhiShenSha.add("正词馆");
        }

        if (null != map.get(this.yearGanZhiNaYinWuXing + this.hourZhi) && null == map.get(this.yearGanZhiNaYinWuXing + this.hourGanZhi)) {
            this.hourGanZhiShenSha.add("词馆");
        } else if (null != map.get(this.yearGanZhiNaYinWuXing + this.hourGanZhi)) {
            this.hourGanZhiShenSha.add("正词馆");
        }

        if (null != map.get(this.yearGanZhiNaYinWuXing + this.arbitraryZhi) && null == map.get(this.yearGanZhiNaYinWuXing + this.arbitraryGanZhi)) {
            this.arbitraryGanZhiShenSha.add("词馆");
        } else if (null != map.get(this.yearGanZhiNaYinWuXing + this.arbitraryGanZhi)) {
            this.arbitraryGanZhiShenSha.add("正词馆");
        }

    }

    /**
     * 计算学堂
     */
    private void xueTang() {

        Map<String, String> map = BaZiShenShaMap.XUE_TANG_LU_MING; // 学堂（年柱纳音五行+干支为键），禄命法

//        if (null != map.get(this.yearGanZhiNaYinWuXing + this.yearZhi) && null == map.get(this.yearGanZhiNaYinWuXing + this.yearGanZhi)) {
//            this.yearGanZhiShenSha.add("学堂");
//        } else if (null != map.get(this.yearGanZhiNaYinWuXing + this.yearGanZhi)) {
//            this.yearGanZhiShenSha.add("正学堂");
//        }

        if (null != map.get(this.yearGanZhiNaYinWuXing + this.monthZhi) && null == map.get(this.yearGanZhiNaYinWuXing + this.monthGanZhi)) {
            this.monthGanZhiShenSha.add("学堂");
        } else if (null != map.get(this.yearGanZhiNaYinWuXing + this.monthGanZhi)) {
            this.monthGanZhiShenSha.add("正学堂");
        }

        if (null != map.get(this.yearGanZhiNaYinWuXing + this.dayZhi) && null == map.get(this.yearGanZhiNaYinWuXing + this.dayGanZhi)) {
            this.dayGanZhiShenSha.add("学堂");
        } else if (null != map.get(this.yearGanZhiNaYinWuXing + this.dayGanZhi)) {
            this.dayGanZhiShenSha.add("正学堂");
        }

        if (null != map.get(this.yearGanZhiNaYinWuXing + this.hourZhi) && null == map.get(this.yearGanZhiNaYinWuXing + this.hourGanZhi)) {
            this.hourGanZhiShenSha.add("学堂");
        } else if (null != map.get(this.yearGanZhiNaYinWuXing + this.hourGanZhi)) {
            this.hourGanZhiShenSha.add("正学堂");
        }

        if (null != map.get(this.yearGanZhiNaYinWuXing + this.arbitraryZhi) && null == map.get(this.yearGanZhiNaYinWuXing + this.arbitraryGanZhi)) {
            this.arbitraryGanZhiShenSha.add("学堂");
        } else if (null != map.get(this.yearGanZhiNaYinWuXing + this.arbitraryGanZhi)) {
            this.arbitraryGanZhiShenSha.add("正学堂");
        }

    }

    /**
     * 计算天赦
     */
    private void tianShe() {

        Map<String, String> map = BaZiShenShaMap.TIAN_SHE; // 天赦（月支+日干支为键）

        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayGanZhi));

    }

    /**
     * 计算天转
     */
    private void tianZhuan() {

        Map<String, String> map = BaZiShenShaMap.TIAN_ZHUAN; // 天转（月支+日干支为键）

        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayGanZhi));

    }

    /**
     * 计算地转
     */
    private void diZhuan() {

        Map<String, String> map = BaZiShenShaMap.DI_ZHUAN; // 地转（月支+日干支为键）

        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayGanZhi));

    }

    /**
     * 计算月德贵人
     */
    private void yueDeGuiRen() {

        Map<String, String> map = BaZiShenShaMap.YUE_DE_GUI_REN; // 月德贵人（月支+其余天干为键）

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearGan));
        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthGan));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayGan));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourGan));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryGan));

    }

    /**
     * 计算德秀贵人
     */
    private void deXiuGuiRen() {

        Map<String, String> map = BaZiShenShaMap.DE_XIU_GUI_REN; // 德秀贵人（月支+其余天干为键）

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearGan));
        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthGan));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayGan));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourGan));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryGan));

    }

    /**
     * 计算天德贵人
     */
    private void tianDeGuiRen() {

        Map<String, String> map = BaZiShenShaMap.TIAN_DE_GUI_REN; // 天德贵人（月支+其余天干或地支为键）

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearGan));
        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthGan));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayGan));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourGan));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryGan));

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearZhi));
//        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryZhi));

    }

    /**
     * 计算拱禄
     */
    private void gongLu() {

        Map<String, String> map = BaZiShenShaMap.GONG_LU; // 拱禄（日干支+时干支+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearGan));
        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthGan));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayGan));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourGan));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryGan));

    }

    /**
     * 计算华盖
     */
    private void huaGai() {

        Map<String, String> map = BaZiShenShaMap.HUA_GAI; // 华盖（年支\日支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayZhi + this.monthZhi));
//        this.dayGanZhiShenSha.add(map.get(this.dayZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayZhi + this.arbitraryZhi));

    }

    /**
     * 计算童子煞
     */
    private void tongZiSha() {

        Map<String, String> map = BaZiShenShaMap.TONG_ZI_SHA; // 童子煞（季节+日支\时支为键。年柱纳音五行+日支\时支为键）

        this.dayGanZhiShenSha.add(map.get(this.jiJie + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.jiJie + this.hourZhi));

        this.dayGanZhiShenSha.add(map.get(this.yearGanZhiNaYinWuXing + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGanZhiNaYinWuXing + this.hourZhi));

    }

    /**
     * 计算冲天煞
     */
    private void chongTianSha() {

        // 判断年干支与月干支是否相同
        if (this.yearGanZhi.equals(this.monthGanZhi)) {
            this.yearGanZhiShenSha.add("冲天煞");
            this.monthGanZhiShenSha.add("冲天煞");
        }

        // 判断日干支与时干支是否相同
        if (this.dayGanZhi.equals(this.hourGanZhi)) {
            this.dayGanZhiShenSha.add("冲天煞");
            this.hourGanZhiShenSha.add("冲天煞");
        }

    }

    /**
     * 计算四废日
     */
    private void siFeiRi() {

        Map<String, String> map = BaZiShenShaMap.SI_FEI_RI; // 四废日（月支+日干支为键）

        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayGanZhi));

    }

    /**
     * 计算阴注阳受
     */
    private void yinZhuYangShou() {

        Map<String, String> map = BaZiShenShaMap.YIN_ZHU_YANG_SHOU; // 阴注阳受（月支+其余地支为键）

        this.yearGanZhiShenSha.add(map.get(this.monthZhi + this.yearZhi));
//        this.monthGanZhiShenSha.add(map.get(this.monthZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.monthZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.monthZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.monthZhi + this.arbitraryZhi));

    }

    /**
     * 计算天罗地网
     */
    private void tianLuoDiWang() {

        Map<String, String> map = BaZiShenShaMap.TIAN_LUO_DI_WANG; // 天罗地网（年支\日支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearZhi + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayZhi + this.monthZhi));
//        this.dayGanZhiShenSha.add(map.get(this.dayZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayZhi + this.arbitraryZhi));

    }

    /**
     * 计算空亡
     */
    private void kongWang() {

        Map<String, String> map = BaZiShenShaMap.KONG_WANG; // 空亡（年干支\日干支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearGanZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearGanZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearGanZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGanZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearGanZhi + this.arbitraryZhi));

        this.yearGanZhiShenSha.add(map.get(this.dayGanZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.dayGanZhi + this.monthZhi));
//        this.dayGanZhiShenSha.add(map.get(this.dayGanZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.dayGanZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.dayGanZhi + this.arbitraryZhi));

    }

    /**
     * 计算截空
     */
    private void jieKong() {

        Map<String, String> map = BaZiShenShaMap.JIE_KONG; // 截空（日干+时支为键）

        this.hourGanZhiShenSha.add(map.get(this.dayGan + this.hourZhi));

    }

    /**
     * 计算六厄
     */
    private void liuE() {

        Map<String, String> map = BaZiShenShaMap.LIU_E; // 六厄（年支+其余地支为键）

//        this.yearGanZhiShenSha.add(map.get(this.yearGanZhi + this.yearZhi));
        this.monthGanZhiShenSha.add(map.get(this.yearGanZhi + this.monthZhi));
        this.dayGanZhiShenSha.add(map.get(this.yearGanZhi + this.dayZhi));
        this.hourGanZhiShenSha.add(map.get(this.yearGanZhi + this.hourZhi));
        this.arbitraryGanZhiShenSha.add(map.get(this.yearGanZhi + this.arbitraryZhi));

    }

    /**
     * 计算三奇贵人
     */
    private void sanQiGuiRen() {

        Map<String, String> map = BaZiShenShaMap.SAN_QI_GUI_REN; // 三奇贵人（年干+月干+日干\月干+日干+时干为键）

        String yearMonthDayGan = map.get(this.yearGan + this.monthGan + this.dayGan); // 年干+月干+日干
        String monthDayHourGan = map.get(this.monthGan + this.dayGan + this.hourGan); // 月干+日干+时干
        if (null != yearMonthDayGan) this.dayGanZhiShenSha.add("三奇贵人");
        if (null != monthDayHourGan) this.dayGanZhiShenSha.add("三奇贵人");

    }

    /**
     * 计算十恶大败
     */
    private void shiEDaBai() {

        String[] strings = BaZiShenShaMap.SHI_E_DA_BAI; // 十恶大败（日干支）

        for (String value : strings) {
            if (this.dayGanZhi.equals(value)) this.dayGanZhiShenSha.add("十恶大败");
        }

    }

    /**
     * 计算阴差阳错
     */
    private void yinChaYangCuo() {

        String[] strings = BaZiShenShaMap.YIN_CHA_YANG_CUO; // 阴差阳错（日干支）

        for (String value : strings) {
            if (this.dayGanZhi.equals(value)) this.dayGanZhiShenSha.add("阴差阳错");
        }

    }

    /**
     * 计算孤鸾煞
     */
    private void guLuanSha() {

        String[] strings = BaZiShenShaMap.GU_LUAN_SHA; // 孤鸾煞（日干支）

        for (String value : strings) {
            if (this.dayGanZhi.equals(value)) this.dayGanZhiShenSha.add("孤鸾煞");
        }

    }

    /**
     * 计算六秀日
     */
    private void liuXiuRi() {

        String[] strings = BaZiShenShaMap.LIU_XIU_RI; // 六秀日（日干支）

        for (String value : strings) {
            if (this.dayGanZhi.equals(value)) this.dayGanZhiShenSha.add("六秀日");
        }

    }

    /**
     * 计算十灵日
     */
    private void shiLingRi() {

        String[] strings = BaZiShenShaMap.SHI_LING_RI; // 十灵日（日干支）

        for (String value : strings) {
            if (this.dayGanZhi.equals(value)) this.dayGanZhiShenSha.add("十灵日");
        }

    }

    /**
     * 计算魁罡日
     */
    private void kuiGangRi() {

        String[] strings = BaZiShenShaMap.KUI_GANG_RI; // 魁罡日（日干支）

        for (String value : strings) {
            if (this.dayGanZhi.equals(value)) this.dayGanZhiShenSha.add("魁罡日");
        }

    }

    /**
     * 计算八专日
     */
    private void baZhuanRi() {

        String[] strings = BaZiShenShaMap.BA_ZHUAN_RI; // 八专日（日干支）

        for (String value : strings) {
            if (this.dayGanZhi.equals(value)) this.dayGanZhiShenSha.add("八专日");
        }

    }

    /**
     * 计算九丑日
     */
    private void jiuChouRi() {

        String[] strings = BaZiShenShaMap.JIU_CHOU_RI; // 九丑日（日干支）

        for (String value : strings) {
            if (this.dayGanZhi.equals(value)) this.dayGanZhiShenSha.add("九丑日");
        }

    }

    /**
     * 计算金神
     */
    private void jinShen() {

        String[] strings = BaZiShenShaMap.JIN_SHEN; // 金神（日干支\时干支）

        for (String value : strings) {
            if (this.dayGanZhi.equals(value)) this.dayGanZhiShenSha.add("金神");
        }
        for (String value : strings) {
            if (this.hourGanZhi.equals(value)) this.hourGanZhiShenSha.add("金神");
        }

    }


}
