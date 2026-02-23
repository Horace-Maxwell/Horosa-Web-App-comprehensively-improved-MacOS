package xuan.core.bazi.utils;

import xuan.utils.CommonUtil;
import xuan.core.bazi.maps.BaZiGanZhiLiuYiMap;
import xuan.core.bazi.settings.BaZiGanZhiLiuYiSetting;

import java.util.*;

/**
 * 八字 - 干支留意工具
 *
 * @author 善待
 */
public class BaZiGanZhiLiuYiUtil {

    /**
     * 计算天干留意
     *
     * @param baZiGanZhiLiuYiSetting 八字 - 干支留意设置
     * @param yearGan                年干
     * @param monthGan               月干
     * @param dayGan                 日干
     * @param hourGan                时干
     * @param daYunGan               大运干
     * @param liuNianGan             流年干
     * @param liuYueGan              流月干
     * @param liuRiGan               流日干
     * @param liuShiGan              流时干
     */
    public static List<String> tanGanLiuYi(BaZiGanZhiLiuYiSetting baZiGanZhiLiuYiSetting, String yearGan, String monthGan, String dayGan, String hourGan, String daYunGan, String liuNianGan, String liuYueGan, String liuRiGan, String liuShiGan) {

        Set<String> set = new HashSet<>();

        if (baZiGanZhiLiuYiSetting.getTianGanXiangSheng() == 0) addGanZhiLiuYi(yearGan, monthGan, dayGan, hourGan, daYunGan, liuNianGan, liuYueGan, liuRiGan, liuShiGan, baZiGanZhiLiuYiSetting.getTianGanXiangShengType() == 0, set, BaZiGanZhiLiuYiMap.TIAN_GAN_XIANG_SHENG); // 天干相生
        if (baZiGanZhiLiuYiSetting.getTianGanXiangHe() == 0) addGanZhiLiuYi(yearGan, monthGan, dayGan, hourGan, daYunGan, liuNianGan, liuYueGan, liuRiGan, liuShiGan, baZiGanZhiLiuYiSetting.getTianGanXiangHeType() == 0, set, BaZiGanZhiLiuYiMap.TIAN_GAN_XIANG_HE); // 天干相合
        if (baZiGanZhiLiuYiSetting.getTianGanXiangChong() == 0) addGanZhiLiuYi(yearGan, monthGan, dayGan, hourGan, daYunGan, liuNianGan, liuYueGan, liuRiGan, liuShiGan, baZiGanZhiLiuYiSetting.getTianGanXiangChongType() == 0, set, BaZiGanZhiLiuYiMap.TIAN_GAN_XIANG_CHONG); // 天干相冲
        if (baZiGanZhiLiuYiSetting.getTianGanXiangKe() == 0) addGanZhiLiuYi(yearGan, monthGan, dayGan, hourGan, daYunGan, liuNianGan, liuYueGan, liuRiGan, liuShiGan, baZiGanZhiLiuYiSetting.getTianGanXiangKeType() == 0, set, BaZiGanZhiLiuYiMap.TIAN_GAN_XIANG_KE); // 天干相克
        if (baZiGanZhiLiuYiSetting.getJiaBingXiangSheng() == 1) set.remove("甲丙相生");
        if (baZiGanZhiLiuYiSetting.getJiaDingXiangSheng() == 1) set.remove("甲丁相生");
        if (baZiGanZhiLiuYiSetting.getYiBingXiangSheng() == 1) set.remove("乙丙相生");
        if (baZiGanZhiLiuYiSetting.getYiDingXiangSheng() == 1) set.remove("乙丁相生");
        if (baZiGanZhiLiuYiSetting.getBingWuXiangSheng() == 1) set.remove("丙戊相生");
        if (baZiGanZhiLiuYiSetting.getBingWuXiangSheng() == 1) set.remove("丙己相生");
        if (baZiGanZhiLiuYiSetting.getDingWuXiangSheng() == 1) set.remove("丁戊相生");
        if (baZiGanZhiLiuYiSetting.getDingJiXiangSheng() == 1) set.remove("丁己相生");
        if (baZiGanZhiLiuYiSetting.getWuGengXiangSheng() == 1) set.remove("戊庚相生");
        if (baZiGanZhiLiuYiSetting.getWuXinXiangSheng() == 1) set.remove("戊辛相生");
        if (baZiGanZhiLiuYiSetting.getJiGengXiangSheng() == 1) set.remove("己庚相生");
        if (baZiGanZhiLiuYiSetting.getJiXinXiangSheng() == 1) set.remove("己辛相生");
        if (baZiGanZhiLiuYiSetting.getGengRenXiangSheng() == 1) set.remove("庚壬相生");
        if (baZiGanZhiLiuYiSetting.getGengGuiXiangSheng() == 1) set.remove("庚癸相生");
        if (baZiGanZhiLiuYiSetting.getXinRenXiangSheng() == 1) set.remove("辛壬相生");
        if (baZiGanZhiLiuYiSetting.getXinGuiXiangSheng() == 1) set.remove("辛癸相生");
        if (baZiGanZhiLiuYiSetting.getRenJiaXiangSheng() == 1) set.remove("壬甲相生");
        if (baZiGanZhiLiuYiSetting.getRenYiXiangSheng() == 1) set.remove("壬乙相生");
        if (baZiGanZhiLiuYiSetting.getGuiJiaXiangSheng() == 1) set.remove("癸甲相生");
        if (baZiGanZhiLiuYiSetting.getGuiYiXiangSheng() == 1) set.remove("癸乙相生");
        if (baZiGanZhiLiuYiSetting.getJiaJiXiangHe() == 1) set.remove("甲己相合");
        if (baZiGanZhiLiuYiSetting.getYiGengXiangHe() == 1) set.remove("乙庚相合");
        if (baZiGanZhiLiuYiSetting.getBingXinXiangHe() == 1) set.remove("丙辛相合");
        if (baZiGanZhiLiuYiSetting.getDingRenXiangHe() == 1) set.remove("丁壬相合");
        if (baZiGanZhiLiuYiSetting.getWuGuiXiangHe() == 1) set.remove("戊癸相合");
        if (baZiGanZhiLiuYiSetting.getJiaGengXiangChong() == 1) set.remove("甲庚相冲");
        if (baZiGanZhiLiuYiSetting.getYiXinXiangChong() == 1) set.remove("乙辛相冲");
        if (baZiGanZhiLiuYiSetting.getBingRenXiangChong() == 1) set.remove("丙壬相冲");
        if (baZiGanZhiLiuYiSetting.getDingGuiXiangChong() == 1) set.remove("丁癸相冲");
        if (baZiGanZhiLiuYiSetting.getJiaWuXiangKe() == 1) set.remove("甲戊相克");
        if (baZiGanZhiLiuYiSetting.getYiJiXiangKe() == 1) set.remove("乙己相克");
        if (baZiGanZhiLiuYiSetting.getBingGengXiangKe() == 1) set.remove("丙庚相克");
        if (baZiGanZhiLiuYiSetting.getDingXinXiangKe() == 1) set.remove("丁辛相克");
        if (baZiGanZhiLiuYiSetting.getWuRenXiangKe() == 1) set.remove("戊壬相克");
        if (baZiGanZhiLiuYiSetting.getJiGuiXiangKe() == 1) set.remove("己癸相克");
        if (baZiGanZhiLiuYiSetting.getGengJiaXiangKe() == 1) set.remove("庚甲相克");
        if (baZiGanZhiLiuYiSetting.getXinYiXiangKe() == 1) set.remove("辛乙相克");
        if (baZiGanZhiLiuYiSetting.getRenBingXiangKe() == 1) set.remove("壬丙相克");
        if (baZiGanZhiLiuYiSetting.getGuiDingXiangKe() == 1) set.remove("癸丁相克");

        return CommonUtil.removeDuplicatesList(new ArrayList<>(set));

    }

    /**
     * 计算地支留意
     *
     * @param baZiGanZhiLiuYiSetting 八字 - 干支留意设置
     * @param yearZhi                年支
     * @param monthZhi               月支
     * @param dayZhi                 日支
     * @param hourZhi                时支
     * @param daYunZhi               大运支
     * @param liuNianZhi             流年支
     * @param liuYueZhi              流月支
     * @param liuRiZhi               流日支
     * @param liuShiZhi              流时支
     */
    public static List<String> diZhiLiuYi(BaZiGanZhiLiuYiSetting baZiGanZhiLiuYiSetting, String yearZhi, String monthZhi, String dayZhi, String hourZhi, String daYunZhi, String liuNianZhi, String liuYueZhi, String liuRiZhi, String liuShiZhi) {

        Set<String> set = new HashSet<>();

        if (baZiGanZhiLiuYiSetting.getDiZhiBanHe() == 0) addGanZhiLiuYi(yearZhi, monthZhi, dayZhi, hourZhi, daYunZhi, liuNianZhi, liuYueZhi, liuRiZhi, liuShiZhi, baZiGanZhiLiuYiSetting.getDiZhiBanHeType() == 0, set, BaZiGanZhiLiuYiMap.DI_ZHI_BAN_HE); // 地支半合
        if (baZiGanZhiLiuYiSetting.getDiZhiGongHe() == 0) addGanZhiLiuYi(yearZhi, monthZhi, dayZhi, hourZhi, daYunZhi, liuNianZhi, liuYueZhi, liuRiZhi, liuShiZhi, baZiGanZhiLiuYiSetting.getDiZhiGongHeType() == 0, set, BaZiGanZhiLiuYiMap.DI_ZHI_GONG_HE); // 地支拱合
        if (baZiGanZhiLiuYiSetting.getDiZhiAnHe() == 0) addGanZhiLiuYi(yearZhi, monthZhi, dayZhi, hourZhi, daYunZhi, liuNianZhi, liuYueZhi, liuRiZhi, liuShiZhi, baZiGanZhiLiuYiSetting.getDiZhiAnHeType() == 0, set, BaZiGanZhiLiuYiMap.DI_ZHI_AN_HE); // 地支暗合
        if (baZiGanZhiLiuYiSetting.getDiZhiLiuHe() == 0) addGanZhiLiuYi(yearZhi, monthZhi, dayZhi, hourZhi, daYunZhi, liuNianZhi, liuYueZhi, liuRiZhi, liuShiZhi, baZiGanZhiLiuYiSetting.getDiZhiLiuHeType() == 0, set, BaZiGanZhiLiuYiMap.DI_ZHI_LIU_HE); // 地支六合
        if (baZiGanZhiLiuYiSetting.getDiZhiXiangXing() == 0) addGanZhiLiuYi(yearZhi, monthZhi, dayZhi, hourZhi, daYunZhi, liuNianZhi, liuYueZhi, liuRiZhi, liuShiZhi, baZiGanZhiLiuYiSetting.getDiZhiXiangXingType() == 0, set, BaZiGanZhiLiuYiMap.DI_ZHI_XIANG_XING); // 地支相刑
        if (baZiGanZhiLiuYiSetting.getDiZhiXiangChong() == 0) addGanZhiLiuYi(yearZhi, monthZhi, dayZhi, hourZhi, daYunZhi, liuNianZhi, liuYueZhi, liuRiZhi, liuShiZhi, baZiGanZhiLiuYiSetting.getDiZhiXiangChongType() == 0, set, BaZiGanZhiLiuYiMap.DI_ZHI_XIANG_CHONG); // 地支相冲
        if (baZiGanZhiLiuYiSetting.getDiZhiXiangPo() == 0) addGanZhiLiuYi(yearZhi, monthZhi, dayZhi, hourZhi, daYunZhi, liuNianZhi, liuYueZhi, liuRiZhi, liuShiZhi, baZiGanZhiLiuYiSetting.getDiZhiXiangPoType() == 0, set, BaZiGanZhiLiuYiMap.DI_ZHI_XIANG_PO); // 地支相破
        if (baZiGanZhiLiuYiSetting.getDiZhiXiangHai() == 0) addGanZhiLiuYi(yearZhi, monthZhi, dayZhi, hourZhi, daYunZhi, liuNianZhi, liuYueZhi, liuRiZhi, liuShiZhi, baZiGanZhiLiuYiSetting.getDiZhiXiangHaiType() == 0, set, BaZiGanZhiLiuYiMap.DI_ZHI_XIANG_HAI); // 地支相害
        if (baZiGanZhiLiuYiSetting.getYinWuBanHe() == 1) set.remove("寅午半合火局");
        if (baZiGanZhiLiuYiSetting.getShenZiBanHe() == 1) set.remove("申子半合水局");
        if (baZiGanZhiLiuYiSetting.getSiYouBanHe() == 1) set.remove("巳酉半合金局");
        if (baZiGanZhiLiuYiSetting.getHaiMaoBanHe() == 1) set.remove("亥卯半合木局");
        if (baZiGanZhiLiuYiSetting.getZiChenBanHe() == 1) set.remove("子辰半合水局");
        if (baZiGanZhiLiuYiSetting.getWuXuBanHe() == 1) set.remove("午戌半合火局");
        if (baZiGanZhiLiuYiSetting.getMaoWeiBanHe() == 1) set.remove("卯未半合木局");
        if (baZiGanZhiLiuYiSetting.getYouChouBanHe() == 1) set.remove("酉丑半合金局");
        if (baZiGanZhiLiuYiSetting.getShenChenGongHe() == 1) set.remove("申辰拱合子");
        if (baZiGanZhiLiuYiSetting.getHaiWeiGongHe() == 1) set.remove("亥未拱合卯");
        if (baZiGanZhiLiuYiSetting.getYinXuGongHe() == 1) set.remove("寅戌拱合午");
        if (baZiGanZhiLiuYiSetting.getSiChouGongHe() == 1) set.remove("巳丑拱合酉");
        if (baZiGanZhiLiuYiSetting.getMaoShenAnHe() == 1) set.remove("卯申暗合");
        if (baZiGanZhiLiuYiSetting.getWuHaiAnHe() == 1) set.remove("午亥暗合");
        if (baZiGanZhiLiuYiSetting.getChouYinAnHe() == 1) set.remove("丑寅暗合");
        if (baZiGanZhiLiuYiSetting.getYinWeiAnHe() == 1) set.remove("寅未暗合");
        if (baZiGanZhiLiuYiSetting.getYinWuAnHe() == 1) set.remove("寅午暗合");
        if (baZiGanZhiLiuYiSetting.getZiXuAnHe() == 1) set.remove("子戌暗合");
        if (baZiGanZhiLiuYiSetting.getZiChenAnHe() == 1) set.remove("子辰暗合");
        if (baZiGanZhiLiuYiSetting.getZiSiAnHe() == 1) set.remove("子巳暗合");
        if (baZiGanZhiLiuYiSetting.getSiYouAnHe() == 1) set.remove("巳酉暗合");
        if (baZiGanZhiLiuYiSetting.getZiChouLiuHe() == 1) set.remove("子丑合化土");
        if (baZiGanZhiLiuYiSetting.getYinHaiLiuHe() == 1) set.remove("寅亥合化木");
        if (baZiGanZhiLiuYiSetting.getMaoXuLiuHe() == 1) set.remove("卯戌合化火");
        if (baZiGanZhiLiuYiSetting.getChenYouLiuHe() == 1) set.remove("辰酉合化金");
        if (baZiGanZhiLiuYiSetting.getSiShenLiuHe() == 1) set.remove("巳申合化水");
        if (baZiGanZhiLiuYiSetting.getWuWeiLiuHe() == 1) set.remove("午未合化火");
        if (baZiGanZhiLiuYiSetting.getYinSiXiangXing() == 1) set.remove("寅巳相刑");
        if (baZiGanZhiLiuYiSetting.getSiShenXiangXing() == 1) set.remove("巳申相刑");
        if (baZiGanZhiLiuYiSetting.getShenYinXiangXing() == 1) set.remove("申寅相刑");
        if (baZiGanZhiLiuYiSetting.getChouXuXiangXing() == 1) set.remove("丑戌相刑");
        if (baZiGanZhiLiuYiSetting.getXuWeiXiangXing() == 1) set.remove("戌未相刑");
        if (baZiGanZhiLiuYiSetting.getWeiChouXiangXing() == 1) set.remove("未丑相刑");
        if (baZiGanZhiLiuYiSetting.getZiMaoXiangXing() == 1) set.remove("子卯相刑");
        if (baZiGanZhiLiuYiSetting.getYouYouXiangXing() == 1) set.remove("酉酉自刑");
        if (baZiGanZhiLiuYiSetting.getHaiHaiXiangXing() == 1) set.remove("亥亥自刑");
        if (baZiGanZhiLiuYiSetting.getWuWuXiangXing() == 1) set.remove("午午自刑");
        if (baZiGanZhiLiuYiSetting.getChenChenXiangXing() == 1) set.remove("辰辰自刑");
        if (baZiGanZhiLiuYiSetting.getZiWuXiangChong() == 1) set.remove("子午相冲");
        if (baZiGanZhiLiuYiSetting.getChouWeiXiangChong() == 1) set.remove("丑未相冲");
        if (baZiGanZhiLiuYiSetting.getYinShenXiangChong() == 1) set.remove("寅申相冲");
        if (baZiGanZhiLiuYiSetting.getMaoYouXiangChong() == 1) set.remove("卯酉相冲");
        if (baZiGanZhiLiuYiSetting.getChenXuXiangChong() == 1) set.remove("辰戌相冲");
        if (baZiGanZhiLiuYiSetting.getSiHaiXiangChong() == 1) set.remove("巳亥相冲");
        if (baZiGanZhiLiuYiSetting.getZiYouXiangPo() == 1) set.remove("子酉相破");
        if (baZiGanZhiLiuYiSetting.getYinHaiXiangPo() == 1) set.remove("寅亥相破");
        if (baZiGanZhiLiuYiSetting.getMaoWuXiangPo() == 1) set.remove("卯午相破");
        if (baZiGanZhiLiuYiSetting.getChenChouXiangPo() == 1) set.remove("辰丑相破");
        if (baZiGanZhiLiuYiSetting.getSiShenXiangPo() == 1) set.remove("巳申相破");
        if (baZiGanZhiLiuYiSetting.getXuWeiXiangPo() == 1) set.remove("戌未相破");
        if (baZiGanZhiLiuYiSetting.getZiWeiXiangHai() == 1) set.remove("子未相害");
        if (baZiGanZhiLiuYiSetting.getChouWuXiangHai() == 1) set.remove("丑午相害");
        if (baZiGanZhiLiuYiSetting.getYinSiXiangHai() == 1) set.remove("寅巳相害");
        if (baZiGanZhiLiuYiSetting.getMaoChenXiangHai() == 1) set.remove("卯辰相害");
        if (baZiGanZhiLiuYiSetting.getShenHaiXiangHai() == 1) set.remove("申亥相害");
        if (baZiGanZhiLiuYiSetting.getYouXuXiangHai() == 1) set.remove("酉戌相害");

        return CommonUtil.removeDuplicatesList(new ArrayList<>(set));

    }

//===============================================================================================================================

    /**
     * 添加天干\地支留意
     *
     * @param yearGanOrZhi    年干\年支
     * @param monthGanOrZhi   月干\月支
     * @param dayGanOrZhi     日干\日支
     * @param hourGanOrZhi    时干\时支
     * @param daYunGanOrZhi   大运干\大运支
     * @param liuNianGanOrZhi 流年干\流年支
     * @param liuYueGanOrZhi  流月干\流月支
     * @param liuRiGanOrZhi   流日干\流日支
     * @param liuShiGanOrZhi  流时干\流时支
     * @param type            是否以任意两干计算（true:以任意两干计算。false:以相邻两干计算）
     * @param set             天干\地支组合
     * @param map             天干\地支关系
     */
    private static void addGanZhiLiuYi(String yearGanOrZhi, String monthGanOrZhi, String dayGanOrZhi, String hourGanOrZhi, String daYunGanOrZhi, String liuNianGanOrZhi, String liuYueGanOrZhi, String liuRiGanOrZhi, String liuShiGanOrZhi, boolean type, Set<String> set, Map<String, String> map) {

        set.add(map.get(yearGanOrZhi + monthGanOrZhi));
        set.add(map.get(monthGanOrZhi + yearGanOrZhi));
        set.add(map.get(monthGanOrZhi + dayGanOrZhi));
        set.add(map.get(dayGanOrZhi + monthGanOrZhi));
        set.add(map.get(dayGanOrZhi + hourGanOrZhi));
        set.add(map.get(hourGanOrZhi + dayGanOrZhi));
        set.add(map.get(hourGanOrZhi + daYunGanOrZhi));
        set.add(map.get(daYunGanOrZhi + hourGanOrZhi));
        set.add(map.get(daYunGanOrZhi + liuNianGanOrZhi));
        set.add(map.get(liuNianGanOrZhi + daYunGanOrZhi));
        set.add(map.get(liuNianGanOrZhi + liuYueGanOrZhi));
        set.add(map.get(liuYueGanOrZhi + liuNianGanOrZhi));
        set.add(map.get(liuYueGanOrZhi + liuRiGanOrZhi));
        set.add(map.get(liuRiGanOrZhi + liuYueGanOrZhi));
        set.add(map.get(liuRiGanOrZhi + liuShiGanOrZhi));
        set.add(map.get(liuShiGanOrZhi + liuRiGanOrZhi));

        // 若以相邻两干计算时，则停止
        if (!type) return;

        set.add(map.get(yearGanOrZhi + dayGanOrZhi));
        set.add(map.get(yearGanOrZhi + hourGanOrZhi));
        set.add(map.get(yearGanOrZhi + daYunGanOrZhi));
        set.add(map.get(yearGanOrZhi + liuNianGanOrZhi));
        set.add(map.get(yearGanOrZhi + liuYueGanOrZhi));
        set.add(map.get(yearGanOrZhi + liuRiGanOrZhi));
        set.add(map.get(yearGanOrZhi + liuShiGanOrZhi));
        set.add(map.get(monthGanOrZhi + hourGanOrZhi));
        set.add(map.get(monthGanOrZhi + daYunGanOrZhi));
        set.add(map.get(monthGanOrZhi + liuNianGanOrZhi));
        set.add(map.get(monthGanOrZhi + liuYueGanOrZhi));
        set.add(map.get(monthGanOrZhi + liuRiGanOrZhi));
        set.add(map.get(monthGanOrZhi + liuShiGanOrZhi));
        set.add(map.get(dayGanOrZhi + yearGanOrZhi));
        set.add(map.get(dayGanOrZhi + daYunGanOrZhi));
        set.add(map.get(dayGanOrZhi + liuNianGanOrZhi));
        set.add(map.get(dayGanOrZhi + liuYueGanOrZhi));
        set.add(map.get(dayGanOrZhi + liuRiGanOrZhi));
        set.add(map.get(dayGanOrZhi + liuShiGanOrZhi));
        set.add(map.get(hourGanOrZhi + yearGanOrZhi));
        set.add(map.get(hourGanOrZhi + monthGanOrZhi));
        set.add(map.get(hourGanOrZhi + liuNianGanOrZhi));
        set.add(map.get(hourGanOrZhi + liuYueGanOrZhi));
        set.add(map.get(hourGanOrZhi + liuRiGanOrZhi));
        set.add(map.get(hourGanOrZhi + liuShiGanOrZhi));
        set.add(map.get(daYunGanOrZhi + yearGanOrZhi));
        set.add(map.get(daYunGanOrZhi + monthGanOrZhi));
        set.add(map.get(daYunGanOrZhi + dayGanOrZhi));
        set.add(map.get(daYunGanOrZhi + liuYueGanOrZhi));
        set.add(map.get(daYunGanOrZhi + liuRiGanOrZhi));
        set.add(map.get(daYunGanOrZhi + liuShiGanOrZhi));
        set.add(map.get(liuNianGanOrZhi + yearGanOrZhi));
        set.add(map.get(liuNianGanOrZhi + monthGanOrZhi));
        set.add(map.get(liuNianGanOrZhi + dayGanOrZhi));
        set.add(map.get(liuNianGanOrZhi + hourGanOrZhi));
        set.add(map.get(liuNianGanOrZhi + liuRiGanOrZhi));
        set.add(map.get(liuNianGanOrZhi + liuShiGanOrZhi));
        set.add(map.get(liuYueGanOrZhi + yearGanOrZhi));
        set.add(map.get(liuYueGanOrZhi + monthGanOrZhi));
        set.add(map.get(liuYueGanOrZhi + dayGanOrZhi));
        set.add(map.get(liuYueGanOrZhi + hourGanOrZhi));
        set.add(map.get(liuYueGanOrZhi + daYunGanOrZhi));
        set.add(map.get(liuYueGanOrZhi + liuShiGanOrZhi));
        set.add(map.get(liuRiGanOrZhi + yearGanOrZhi));
        set.add(map.get(liuRiGanOrZhi + monthGanOrZhi));
        set.add(map.get(liuRiGanOrZhi + dayGanOrZhi));
        set.add(map.get(liuRiGanOrZhi + hourGanOrZhi));
        set.add(map.get(liuRiGanOrZhi + daYunGanOrZhi));
        set.add(map.get(liuRiGanOrZhi + liuNianGanOrZhi));
        set.add(map.get(liuShiGanOrZhi + yearGanOrZhi));
        set.add(map.get(liuShiGanOrZhi + monthGanOrZhi));
        set.add(map.get(liuShiGanOrZhi + dayGanOrZhi));
        set.add(map.get(liuShiGanOrZhi + hourGanOrZhi));
        set.add(map.get(liuShiGanOrZhi + daYunGanOrZhi));
        set.add(map.get(liuShiGanOrZhi + liuNianGanOrZhi));
        set.add(map.get(liuShiGanOrZhi + liuYueGanOrZhi));

    }


}
