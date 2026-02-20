package xuan.core;

import java.util.Date;
import java.util.List;

import org.junit.Test;
import xuan.core.bazi.BaZi;
import xuan.utils.DateUtil;
import xuan.core.bazi.settings.BaZiJiChuSetting;
import xuan.core.bazi.settings.BaZiShenShaSetting;
import xuan.core.bazi.settings.BaZiGanZhiLiuYiSetting;
import xuan.core.bazi.utils.BaZiDaYunLiuNianUtil;

/**
 * 八字测试
 *
 * @author 善待
 */
public class BaZiTest {

    /**
     * 八字排盘
     */
    @Test
    public void baZiTest() {

        // 1、基础设置（可选）
        BaZiJiChuSetting baZiJiChuSetting = new BaZiJiChuSetting();
        baZiJiChuSetting.setName("某人"); // 姓名
        baZiJiChuSetting.setOccupy("某事"); // 占事
        baZiJiChuSetting.setSex(1); // 性别（0:女。1:男）
        baZiJiChuSetting.setDate("2024-01-01 00:00:00"); // 日期
        baZiJiChuSetting.setDateType(0); // 日期类型（0:公历。1:农历）
        baZiJiChuSetting.setLeapMonthType(0); // 闰月类型，日期类型为1时生效（0:不使用闰月。1:使用闰月）
        baZiJiChuSetting.setXuShiSuiType(0); // 虚实岁类型（0:虚岁。1:实岁）
        baZiJiChuSetting.setJieQiType(1); //  节气类型（0:按天计算。1:按分钟计算）
        baZiJiChuSetting.setQiYunLiuPaiType(0); // 起运流派类型（0:按天数和时辰数计算：3天1年、1天4个月、1时辰10天。1:按分钟数计算：4320分=1年、360分=1月、12分=1天、1分=2小时）
        baZiJiChuSetting.setRenYuanType(0); // 人元司令分野类型（0:子平真诠法诀。1:渊海子平法诀。2:星平会海法诀。3:三命通会法诀。4:神峰通考法诀。5:万育吾之法诀）
        baZiJiChuSetting.setDaYunLunShu(10); // 大运轮数（最小10轮，最大16轮）
        baZiJiChuSetting.setYearGanZhiType(2); // 年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接的时刻作为新年的开始）
        baZiJiChuSetting.setMonthGanZhiType(1); // 月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
        baZiJiChuSetting.setDayGanZhiType(0); // 日干支类型（0:晚子时日干支算当天。1:晚子时日干支算明天）


        // 2、神煞设置（可选）
        BaZiShenShaSetting baZiShenShaSetting = new BaZiShenShaSetting();
//        baZiShenShaSetting.setTaiJiGuiRen(0); // 太极贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setTianYiGuiRen(0); // 天乙贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setFuXingGuiRen(0); // 福星贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setWenChangGuiRen(0); // 文昌贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setTianChuGuiRen(0); // 天厨贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setYueDeGuiRen(0); // 月德贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setDeXiuGuiRen(0); // 德秀贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setTianDeGuiRen(0); // 天德贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setTianGuanGuiRen(0); // 天官贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setSanQiGuiRen(0); // 三奇贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setShiEDaBai(0); // 十恶大败（0:显示。1:关闭）
//        baZiShenShaSetting.setYinZhuYangShou(0); // 阴注阳受（0:显示。1:关闭）
//        baZiShenShaSetting.setYinChaYangCuo(0); // 阴差阳错（0:显示。1:关闭）
//        baZiShenShaSetting.setTianDeHe(0); // 天德合（0:显示。1:关闭）
//        baZiShenShaSetting.setYueDeHe(0); // 月德合（0:显示。1:关闭）
//        baZiShenShaSetting.setSiFeiRi(0); // 四废日（0:显示。1:关闭）
//        baZiShenShaSetting.setLiuXiuRi(0); // 六秀日（0:显示。1:关闭）
//        baZiShenShaSetting.setShiLingRi(0); // 十灵日（0:显示。1:关闭）
//        baZiShenShaSetting.setKuiGangRi(0); // 魁罡日（0:显示。1:关闭）
//        baZiShenShaSetting.setBaZhuanRi(0); // 八专日（0:显示。1:关闭）
//        baZiShenShaSetting.setJiuChouRi(0); // 九丑日（0:显示。1:关闭）
//        baZiShenShaSetting.setGuLuanSha(0); // 孤鸾煞（0:显示。1:关闭）
//        baZiShenShaSetting.setHongYanSha(0); // 红艳煞（0:显示。1:关闭）
//        baZiShenShaSetting.setGouJiaoSha(0); // 勾绞煞（0:显示。1:关闭）
//        baZiShenShaSetting.setChongTianSha(0); // 冲天煞（0:显示。1:关闭）
//        baZiShenShaSetting.setTongZiSha(0); // 童子煞（0:显示。1:关闭）
//        baZiShenShaSetting.setHuaGai(0); // 华盖（0:显示。1:关闭）
//        baZiShenShaSetting.setGuoYin(0); // 国印（0:显示。1:关闭）
//        baZiShenShaSetting.setJinYu(0); // 金舆（0:显示。1:关闭）
//        baZiShenShaSetting.setYangRen(0); // 羊刃（0:显示。1:关闭）
//        baZiShenShaSetting.setFeiRen(0); // 飞刃（0:显示。1:关闭）
//        baZiShenShaSetting.setLiuXia(0); // 流霞（0:显示。1:关闭）
//        baZiShenShaSetting.setLuShen(0); // 禄神（0:显示。1:关闭）
//        baZiShenShaSetting.setYiMa(0); // 驿马（0:显示。1:关闭）
//        baZiShenShaSetting.setTianLuoDiWang(0); // 天罗\地网（0:显示。1:关闭）
//        baZiShenShaSetting.setKongWang(0); // 空亡（0:显示。1:关闭）
//        baZiShenShaSetting.setJieKong(0); // 截空（0:显示。1:关闭）
//        baZiShenShaSetting.setJieSha(0); // 劫煞（0:显示。1:关闭）
//        baZiShenShaSetting.setJiangXing(0); // 将星（0:显示。1:关闭）
//        baZiShenShaSetting.setTaoHua(0); // 桃花（0:显示。1:关闭）
//        baZiShenShaSetting.setWangShen(0); // 亡神（0:显示。1:关闭）
//        baZiShenShaSetting.setDiaoKe(0); // 吊客（0:显示。1:关闭）
//        baZiShenShaSetting.setPiMa(0); // 披麻（0:显示。1:关闭）
//        baZiShenShaSetting.setTianXi(0); // 天喜（0:显示。1:关闭）
//        baZiShenShaSetting.setHongLuan(0); // 红鸾（0:显示。1:关闭）
//        baZiShenShaSetting.setSangMen(0); // 丧门（0:显示。1:关闭）
//        baZiShenShaSetting.setZaiSha(0); // 灾煞（0:显示。1:关闭）
//        baZiShenShaSetting.setGuChen(0); // 孤辰（0:显示。1:关闭）
//        baZiShenShaSetting.setGuaXiu(0); // 寡宿（0:显示。1:关闭）
//        baZiShenShaSetting.setYuanChen(0); // 元辰（0:显示。1:关闭）
//        baZiShenShaSetting.setXueRen(0); // 血刃（0:显示。1:关闭）
//        baZiShenShaSetting.setTianYi(0); // 天医（0:显示。1:关闭）
//        baZiShenShaSetting.setCiGuan(0); // 词馆（0:显示。1:关闭）
//        baZiShenShaSetting.setXueTang(0); // 学堂（0:显示。1:关闭）
//        baZiShenShaSetting.setTianShe(0); // 天赦（0:显示。1:关闭）
//        baZiShenShaSetting.setTianZhuan(0); // 天转（0:显示。1:关闭）
//        baZiShenShaSetting.setDiZhuan(0); // 地转（0:显示。1:关闭）
//        baZiShenShaSetting.setGongLu(0); // 拱禄（0:显示。1:关闭）
//        baZiShenShaSetting.setJinShen(0); // 金神（0:显示。1:关闭）
//        baZiShenShaSetting.setLiuE(0); // 六厄（0:显示。1:关闭）


        // 3、干支留意设置（可选）
        BaZiGanZhiLiuYiSetting baZiGanZhiLiuYiSetting = new BaZiGanZhiLiuYiSetting();
//        baZiGanZhiLiuYiSetting.setTianGanXiangSheng(0); // 天干相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setTianGanXiangKe(0); // 天干相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setTianGanXiangHe(0); // 天干相合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setTianGanXiangChong(0); // 天干相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setTianGanXiangShengType(0); // 天干相生类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setTianGanXiangKeType(0); // 天干相克类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setTianGanXiangHeType(0); // 天干相合类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setTianGanXiangChongType(0); // 天干相冲类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setJiaBingXiangSheng(0); // 天干相生：甲丙相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setJiaDingXiangSheng(0); // 天干相生：甲丁相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYiBingXiangSheng(0); // 天干相生：乙丙相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYiDingXiangSheng(0); // 天干相生：乙丁相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setBingWuXiangSheng(0); // 天干相生：丙戊相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setBingJiXiangSheng(0); // 天干相生：丙己相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDingWuXiangSheng(0); // 天干相生：丁戊相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDingJiXiangSheng(0); // 天干相生：丁己相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setWuGengXiangSheng(0); // 天干相生：戊庚相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setWuXinXiangSheng(0); // 天干相生：戊辛相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setJiGengXiangSheng(0); // 天干相生：己庚相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setJiXinXiangSheng(0); // 天干相生：己辛相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setGengRenXiangSheng(0); // 天干相生：庚壬相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setGengGuiXiangSheng(0); // 天干相生：庚癸相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setXinRenXiangSheng(0); // 天干相生：辛壬相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setXinGuiXiangSheng(0); // 天干相生：辛癸相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setRenJiaXiangSheng(0); // 天干相生：壬甲相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setRenYiXiangSheng(0); // 天干相生：壬乙相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setGuiJiaXiangSheng(0); // 天干相生：癸甲相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setGuiYiXiangSheng(0); // 天干相生：癸乙相生（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setJiaJiXiangHe(0); // 天干相合：甲己相合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYiGengXiangHe(0); // 天干相合：乙庚相合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setBingXinXiangHe(0); // 天干相合：丙辛相合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDingRenXiangHe(0); // 天干相合：丁壬相合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setWuGuiXiangHe(0); // 天干相合：戊癸相合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setJiaGengXiangChong(0); // 天干相冲：甲庚相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYiXinXiangChong(0); // 天干相冲：乙辛相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setBingRenXiangChong(0); // 天干相冲：丙壬相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDingGuiXiangChong(0); // 天干相冲：丁癸相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setJiaWuXiangKe(0); // 天干相克：甲戊相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYiJiXiangKe(0); // 天干相克：乙己相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setBingGengXiangKe(0); // 天干相克：丙庚相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDingXinXiangKe(0); // 天干相克：丁辛相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setWuRenXiangKe(0); // 天干相克：戊壬相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setJiGuiXiangKe(0); // 天干相克：己癸相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setGengJiaXiangKe(0); // 天干相克：庚甲相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setXinYiXiangKe(0); // 天干相克：辛乙相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setRenBingXiangKe(0); // 天干相克：壬丙相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setGuiDingXiangKe(0); // 天干相克：癸丁相克（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDiZhiBanHe(0); // 地支半合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDiZhiGongHe(0); // 地支拱合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDiZhiAnHe(0); // 地支暗合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDiZhiLiuHe(0); // 地支六合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDiZhiXiangXing(0); // 地支相刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDiZhiXiangChong(0); // 地支相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDiZhiXiangPo(0); // 地支相破（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDiZhiXiangHai(0); // 地支相害（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setDiZhiBanHeType(0); // 地支半合类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setDiZhiGongHeType(0); // 地支拱合类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setDiZhiAnHeType(0); // 地支暗合类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setDiZhiLiuHeType(0); // 地支六合类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setDiZhiXiangXingType(0); // 地支相刑类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setDiZhiXiangChongType(0); // 地支相冲类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setDiZhiXiangPoType(0); // 地支相破类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setDiZhiXiangHaiType(0); // 地支相害类型（0:以任意两干计算。1:以相邻两干计算）
//        baZiGanZhiLiuYiSetting.setYinWuBanHe(0); // 地支半合：寅午半合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setShenZiBanHe(0); // 地支半合：申子半合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setSiYouBanHe(0); // 地支半合：巳酉半合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setHaiMaoBanHe(0); // 地支半合：亥卯半合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setZiChenBanHe(0); // 地支半合：子辰半合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setWuXuBanHe(0); // 地支半合：午戌半合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setMaoWeiBanHe(0); // 地支半合：卯未半合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYouChouBanHe(0); // 地支半合：酉丑半合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setShenChenGongHe(0); // 地支拱合：申辰拱合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setHaiWeiGongHe(0); // 地支拱合：亥未拱合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYinXuGongHe(0); // 地支拱合：寅戌拱合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setSiChouGongHe(0); // 地支拱合：巳丑拱合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setMaoShenAnHe(0); // 地支暗合：卯申暗合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setWuHaiAnHe(0); // 地支暗合：午亥暗合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setChouYinAnHe(0); // 地支暗合：丑寅暗合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYinWeiAnHe(0); // 地支暗合：寅未暗合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYinWuAnHe(0); // 地支暗合：寅午暗合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setZiXuAnHe(0); // 地支暗合：子戌暗合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setZiChenAnHe(0); // 地支暗合：子辰暗合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setZiSiAnHe(0); // 地支暗合：子巳暗合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setSiYouAnHe(0); // 地支暗合：巳酉暗合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setZiChouLiuHe(0); // 地支六合：子丑六合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYinHaiLiuHe(0); // 地支六合：寅亥六合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setMaoXuLiuHe(0); // 地支六合：卯戌六合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setChenYouLiuHe(0); // 地支六合：辰酉六合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setSiShenLiuHe(0); // 地支六合：巳申六合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setWuWeiLiuHe(0); // 地支六合：午未六合（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYinSiXiangXing(0); // 地支相刑：寅巳相刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setSiShenXiangXing(0); // 地支相刑：巳申相刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setShenYinXiangXing(0); // 地支相刑：申寅相刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setChouXuXiangXing(0); // 地支相刑：丑戌相刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setXuWeiXiangXing(0); // 地支相刑：戌未相刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setWeiChouXiangXing(0); // 地支相刑：未丑相刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setZiMaoXiangXing(0); // 地支相刑：子卯相刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYouYouXiangXing(0); // 地支相刑：酉酉自刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setHaiHaiXiangXing(0); // 地支相刑：亥亥自刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setWuWuXiangXing(0); // 地支相刑：午午自刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setChenChenXiangXing(0); // 地支相刑：辰辰自刑（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setZiWuXiangChong(0); // 地支相冲：子午相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setChouWeiXiangChong(0); // 地支相冲：丑未相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYinShenXiangChong(0); // 地支相冲：寅申相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setMaoYouXiangChong(0); // 地支相冲：卯酉相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setChenXuXiangChong(0); // 地支相冲：辰戌相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setSiHaiXiangChong(0); // 地支相冲：巳亥相冲（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setZiYouXiangPo(0); // 地支相破：子酉相破（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYinHaiXiangPo(0); // 地支相破：寅亥相破（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setMaoWuXiangPo(0); // 地支相破：卯午相破（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setChenChouXiangPo(0); // 地支相破：辰丑相破（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setSiShenXiangPo(0); // 地支相破：巳申相破（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setXuWeiXiangPo(0); // 地支相破：戌未相破（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setXuWeiXiangPo(0); // 地支相害：子未相害（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setChouWuXiangHai(0); // 地支相害：丑午相害（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYinSiXiangHai(0); // 地支相害：寅巳相害（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setMaoChenXiangHai(0); // 地支相害：卯辰相害（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setShenHaiXiangHai(0); // 地支相害：申亥相害（0:显示。1:关闭）
//        baZiGanZhiLiuYiSetting.setYouXuXiangHai(0); // 地支相害：酉戌相害（0:显示。1:关闭）


        // 4、初始化
        BaZi baZi = new BaZi(baZiJiChuSetting); // 使用基础设置初始化
        baZi.baZiShenShaSetting(baZiShenShaSetting); // 神煞设置（可选）
        baZi.baZiGanZhiLiuYiSetting(baZiGanZhiLiuYiSetting); // 干支留意设置（可选）


        // 5、数据
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ ☯ 八字 ☯ ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐\n");

        System.out.println("公历日期（Solar型）：" + baZi.getSolar());
        System.out.println("农历日期（Lunar型）：" + baZi.getLunar());
        System.out.println("公历日期（String型）：" + baZi.getSolarStr());
        System.out.println("农历日期（String型）：" + baZi.getLunarStr());
        System.out.println("公历日期（String型）：" + baZi.getSolarStr2());
        System.out.println("农历日期（String型）：" + baZi.getLunarStr2());
        System.out.println("公历日期（Date型）：" + baZi.getSolarDate());
        System.out.println("农历日期（Date型）：" + baZi.getLunarDate());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("姓名：" + baZi.getName());
        System.out.println("占事：" + baZi.getOccupy());
        System.out.println("性别：" + baZi.getSex());
        System.out.println("年龄：" + baZi.getAge());
        System.out.println("造：" + baZi.getZao());
        System.out.println("星期：" + baZi.getXingQi());
        System.out.println("季节：" + baZi.getJiJie());
        System.out.println("生肖：" + baZi.getShengXiao());
        System.out.println("年冲生肖：" + baZi.getYearChongShengXiao());
        System.out.println("月冲生肖：" + baZi.getMonthChongShengXiao());
        System.out.println("日冲生肖：" + baZi.getDayChongShengXiao());
        System.out.println("时冲生肖：" + baZi.getHourChongShengXiao());
        System.out.println("星座：" + baZi.getXingZuo());
        System.out.println("五不遇时：" + baZi.getWuBuYuShi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("值年九星五行：" + baZi.getYearJiuXingWuXing());
        System.out.println("值月九星五行：" + baZi.getMonthJiuXingWuXing());
        System.out.println("值日九星五行：" + baZi.getDayJiuXingWuXing());
        System.out.println("值时九星五行：" + baZi.getHourJiuXingWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("值年九星方位：" + baZi.getYearJiuXingFangWei());
        System.out.println("值月九星方位：" + baZi.getMonthJiuXingFangWei());
        System.out.println("值日九星方位：" + baZi.getDayJiuXingFangWei());
        System.out.println("值时九星方位：" + baZi.getHourJiuXingFangWei());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("值年九星方位描述：" + baZi.getYearJiuXingFangWeiMiaoShu());
        System.out.println("值月九星方位描述：" + baZi.getMonthJiuXingFangWeiMiaoShu());
        System.out.println("值日九星方位描述：" + baZi.getDayJiuXingFangWeiMiaoShu());
        System.out.println("值时九星方位描述：" + baZi.getHourJiuXingFangWeiMiaoShu());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("值年九星之玄空九星：" + baZi.getYearJiuXingXuanKong());
        System.out.println("值月九星之玄空九星：" + baZi.getMonthJiuXingXuanKong());
        System.out.println("值日九星之玄空九星：" + baZi.getDayJiuXingXuanKong());
        System.out.println("值时九星之玄空九星：" + baZi.getHourJiuXingXuanKong());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("值年九星之北斗九星：" + baZi.getYearJiuXingBeiDou());
        System.out.println("值月九星之北斗九星：" + baZi.getMonthJiuXingBeiDou());
        System.out.println("值日九星之北斗九星：" + baZi.getDayJiuXingBeiDou());
        System.out.println("值时九星之北斗九星：" + baZi.getHourJiuXingBeiDou());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("值年九星之奇门九星：" + baZi.getYearJiuXingQiMen());
        System.out.println("值月九星之奇门九星：" + baZi.getMonthJiuXingQiMen());
        System.out.println("值日九星之奇门九星：" + baZi.getDayJiuXingQiMen());
        System.out.println("值时九星之奇门九星：" + baZi.getHourJiuXingQiMen());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("值年九星之太乙九星：" + baZi.getYearJiuXingTaiYi());
        System.out.println("值月九星之太乙九星：" + baZi.getMonthJiuXingTaiYi());
        System.out.println("值日九星之太乙九星：" + baZi.getDayJiuXingTaiYi());
        System.out.println("值时九星之太乙九星：" + baZi.getHourJiuXingTaiYi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("八字：" + baZi.getBaZi());
        System.out.println("八字五行：" + baZi.getBaZiWuXing());
        System.out.println("八字纳音：" + baZi.getBaZiNaYin());
        System.out.println("八字空亡：" + baZi.getBaZiKongWang());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干：" + baZi.getYearGan());
        System.out.println("月干：" + baZi.getMonthGan());
        System.out.println("日干：" + baZi.getDayGan());
        System.out.println("时干：" + baZi.getHourGan());
        System.out.println("胎元干：" + baZi.getTaiYuanGan());
        System.out.println("胎息干：" + baZi.getTaiXiGan());
        System.out.println("命宫干：" + baZi.getMingGongGan());
        System.out.println("身宫干：" + baZi.getShenGongGan());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支：" + baZi.getYearZhi());
        System.out.println("月支：" + baZi.getMonthZhi());
        System.out.println("日支：" + baZi.getDayZhi());
        System.out.println("时支：" + baZi.getHourZhi());
        System.out.println("胎元支：" + baZi.getTaiYuanZhi());
        System.out.println("胎息支：" + baZi.getTaiXiZhi());
        System.out.println("命宫支：" + baZi.getMingGongZhi());
        System.out.println("身宫支：" + baZi.getShenGongZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支：" + baZi.getYearGanZhi());
        System.out.println("月干支：" + baZi.getMonthGanZhi());
        System.out.println("日干支：" + baZi.getDayGanZhi());
        System.out.println("时干支：" + baZi.getHourGanZhi());
        System.out.println("胎元干支：" + baZi.getTaiYuanGanZhi());
        System.out.println("胎息干支：" + baZi.getTaiXiGanZhi());
        System.out.println("命宫干支：" + baZi.getMingGongGanZhi());
        System.out.println("身宫干支：" + baZi.getShenGongGanZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干五行：" + baZi.getYearGanWuXing());
        System.out.println("月干五行：" + baZi.getMonthGanWuXing());
        System.out.println("日干五行：" + baZi.getDayGanWuXing());
        System.out.println("时干五行：" + baZi.getHourGanWuXing());
        System.out.println("胎元干五行：" + baZi.getTaiYuanGanWuXing());
        System.out.println("胎息干五行：" + baZi.getTaiXiGanWuXing());
        System.out.println("命宫干五行：" + baZi.getMingGongGanWuXing());
        System.out.println("身宫干五行：" + baZi.getShenGongGanWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支五行：" + baZi.getYearZhiWuXing());
        System.out.println("月支五行：" + baZi.getMonthZhiWuXing());
        System.out.println("日支五行：" + baZi.getDayZhiWuXing());
        System.out.println("时支五行：" + baZi.getHourZhiWuXing());
        System.out.println("胎元支五行：" + baZi.getTaiYuanZhiWuXing());
        System.out.println("胎息支五行：" + baZi.getTaiXiZhiWuXing());
        System.out.println("命宫支五行：" + baZi.getMingGongZhiWuXing());
        System.out.println("身宫支五行：" + baZi.getShenGongZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支五行：" + baZi.getYearGanZhiWuXing());
        System.out.println("月干支五行：" + baZi.getMonthGanZhiWuXing());
        System.out.println("日干支五行：" + baZi.getDayGanZhiWuXing());
        System.out.println("时干支五行：" + baZi.getHourGanZhiWuXing());
        System.out.println("胎元干支五行：" + baZi.getTaiYuanGanZhiWuXing());
        System.out.println("胎息干支五行：" + baZi.getTaiXiGanZhiWuXing());
        System.out.println("命宫干支五行：" + baZi.getMingGongGanZhiWuXing());
        System.out.println("身宫干支五行：" + baZi.getShenGongGanZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支纳音：" + baZi.getYearGanZhiNaYin());
        System.out.println("月干支纳音：" + baZi.getMonthGanZhiNaYin());
        System.out.println("日干支纳音：" + baZi.getDayGanZhiNaYin());
        System.out.println("时干支纳音：" + baZi.getHourGanZhiNaYin());
        System.out.println("胎元干支纳音：" + baZi.getTaiYuanGanZhiNaYin());
        System.out.println("胎息干支纳音：" + baZi.getTaiXiGanZhiNaYin());
        System.out.println("命宫干支纳音：" + baZi.getMingGongGanZhiNaYin());
        System.out.println("身宫干支纳音：" + baZi.getShenGongGanZhiNaYin());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支空亡：" + baZi.getYearGanZhiKongWang());
        System.out.println("月干支空亡：" + baZi.getMonthGanZhiKongWang());
        System.out.println("日干支空亡：" + baZi.getDayGanZhiKongWang());
        System.out.println("时干支空亡：" + baZi.getHourGanZhiKongWang());
        System.out.println("胎元干支空亡：" + baZi.getTaiYuanGanZhiKongWang());
        System.out.println("胎息干支空亡：" + baZi.getTaiXiGanZhiKongWang());
        System.out.println("命宫干支空亡：" + baZi.getMingGongGanZhiKongWang());
        System.out.println("身宫干支空亡：" + baZi.getShenGongGanZhiKongWang());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支主星：" + baZi.getYearGanZhiZhuXing());
        System.out.println("月干支主星：" + baZi.getMonthGanZhiZhuXing());
        System.out.println("日干支主星：" + baZi.getDayGanZhiZhuXing());
        System.out.println("时干支主星：" + baZi.getHourGanZhiZhuXing());
        System.out.println("胎元干支主星：" + baZi.getTaiYuanGanZhiZhuXing());
        System.out.println("胎息干支主星：" + baZi.getTaiXiGanZhiZhuXing());
        System.out.println("命宫干支主星：" + baZi.getMingGongGanZhiZhuXing());
        System.out.println("身宫干支主星：" + baZi.getShenGongGanZhiZhuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支藏干：" + baZi.getYearZhiCangGan());
        System.out.println("月支藏干：" + baZi.getMonthZhiCangGan());
        System.out.println("日支藏干：" + baZi.getDayZhiCangGan());
        System.out.println("时支藏干：" + baZi.getHourZhiCangGan());
        System.out.println("胎元支藏干：" + baZi.getTaiYuanZhiCangGan());
        System.out.println("胎息支藏干：" + baZi.getTaiXiZhiCangGan());
        System.out.println("命宫支藏干：" + baZi.getMingGongZhiCangGan());
        System.out.println("身宫支藏干：" + baZi.getShenGongZhiCangGan());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支藏干五行：" + baZi.getYearZhiCangGanWuXing());
        System.out.println("月支藏干五行：" + baZi.getMonthZhiCangGanWuXing());
        System.out.println("日支藏干五行：" + baZi.getDayZhiCangGanWuXing());
        System.out.println("时支藏干五行：" + baZi.getHourZhiCangGanWuXing());
        System.out.println("胎元支藏干五行：" + baZi.getTaiYuanZhiCangGanWuXing());
        System.out.println("胎息支藏干五行：" + baZi.getTaiXiZhiCangGanWuXing());
        System.out.println("命宫支藏干五行：" + baZi.getMingGongZhiCangGanWuXing());
        System.out.println("身宫支藏干五行：" + baZi.getShenGongZhiCangGanWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支副星：" + baZi.getYearGanZhiFuXing());
        System.out.println("月干支副星：" + baZi.getMonthGanZhiFuXing());
        System.out.println("日干支副星：" + baZi.getDayGanZhiFuXing());
        System.out.println("时干支副星：" + baZi.getHourGanZhiFuXing());
        System.out.println("胎元干支副星：" + baZi.getTaiYuanGanZhiFuXing());
        System.out.println("胎息干支副星：" + baZi.getTaiXiGanZhiFuXing());
        System.out.println("命宫干支副星：" + baZi.getMingGongGanZhiFuXing());
        System.out.println("身宫干支副星：" + baZi.getShenGongGanZhiFuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支自坐：" + baZi.getYearGanZhiZiZuo());
        System.out.println("月干支自坐：" + baZi.getMonthGanZhiZiZuo());
        System.out.println("日干支自坐：" + baZi.getDayGanZhiZiZuo());
        System.out.println("时干支自坐：" + baZi.getHourGanZhiZiZuo());
        System.out.println("胎元干支自坐：" + baZi.getTaiYuanGanZhiZiZuo());
        System.out.println("胎息干支自坐：" + baZi.getTaiXiGanZhiZiZuo());
        System.out.println("命宫干支自坐：" + baZi.getMingGongGanZhiZiZuo());
        System.out.println("身宫干支自坐：" + baZi.getShenGongGanZhiZiZuo());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支星运：" + baZi.getYearGanZhiXingYun());
        System.out.println("月干支星运：" + baZi.getMonthGanZhiXingYun());
        System.out.println("日干支星运：" + baZi.getDayGanZhiXingYun());
        System.out.println("时干支星运：" + baZi.getHourGanZhiXingYun());
        System.out.println("胎元干支星运：" + baZi.getTaiYuanGanZhiXingYun());
        System.out.println("胎息干支星运：" + baZi.getTaiXiGanZhiXingYun());
        System.out.println("命宫干支星运：" + baZi.getMingGongGanZhiXingYun());
        System.out.println("身宫干支星运：" + baZi.getShenGongGanZhiXingYun());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支神煞：" + baZi.getYearGanZhiShenSha());
        System.out.println("月干支神煞：" + baZi.getMonthGanZhiShenSha());
        System.out.println("日干支神煞：" + baZi.getDayGanZhiShenSha());
        System.out.println("时干支神煞：" + baZi.getHourGanZhiShenSha());
        System.out.println("胎元干支神煞：" + baZi.getTaiYuanGanZhiShenSha());
        System.out.println("胎息干支神煞：" + baZi.getTaiXiGanZhiShenSha());
        System.out.println("命宫干支神煞：" + baZi.getMingGongGanZhiShenSha());
        System.out.println("身宫干支神煞：" + baZi.getShenGongGanZhiShenSha());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("五行木数量（不包含地支藏干）：" + baZi.getMuCount());
        System.out.println("五行火数量（不包含地支藏干）：" + baZi.getHuoCount());
        System.out.println("五行土数量（不包含地支藏干）：" + baZi.getTuCount());
        System.out.println("五行金数量（不包含地支藏干）：" + baZi.getJinCount());
        System.out.println("五行水数量（不包含地支藏干）：" + baZi.getShuiCount());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("五行木数量（包含地支藏干）：" + baZi.getMuCangGanCount());
        System.out.println("五行火数量（包含地支藏干）：" + baZi.getHuoCangGanCount());
        System.out.println("五行土数量（包含地支藏干）：" + baZi.getTuCangGanCount());
        System.out.println("五行金数量（包含地支藏干）：" + baZi.getJinCangGanCount());
        System.out.println("五行水数量（包含地支藏干）：" + baZi.getShuiCangGanCount());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("五行旺衰：" + baZi.getWuXingWangShuai());
        System.out.println("五行缺失：" + baZi.getWuXingQueShi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("天干留意：" + baZi.getTianGanLiuYi());
        System.out.println("地支留意：" + baZi.getDiZhiLiuYi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一节：" + baZi.getPrevJie());
        System.out.println("上一节日期：" + baZi.getPrevJieDateStr());
        System.out.println("距上一节天数：" + baZi.getPrevJieDay());
        System.out.println();
        System.out.println("下一节：" + baZi.getNextJie());
        System.out.println("下一节日期：" + baZi.getNextJieDateStr());
        System.out.println("距下一节天数：" + baZi.getNextJieDay());
        System.out.println();
        System.out.println("出生节：" + baZi.getChuShengJie());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一气：" + baZi.getPrevQi());
        System.out.println("上一气日期：" + baZi.getPrevQiDateStr());
        System.out.println("距上一气天数：" + baZi.getPrevQiDay());
        System.out.println();
        System.out.println("下一气：" + baZi.getNextQi());
        System.out.println("下一气日期：" + baZi.getNextQiDateStr());
        System.out.println("距下一气天数：" + baZi.getNextQiDay());
        System.out.println();
        System.out.println("出生气：" + baZi.getChuShengQi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("月相：" + baZi.getYueXiang());
        System.out.println("月将：" + baZi.getYueJiang());
        System.out.println("月将神：" + baZi.getYueJiangShen());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("人元司令分野：" + baZi.getRenYuanSiLingFenYe());
        System.out.println("身体强弱：" + baZi.getShenTiQiangRuo());
        System.out.println("喜用神：" + baZi.getXiYongShen());
        System.out.println("喜用神方位：" + baZi.getXiYongShenFangWei());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("骨重：" + baZi.getGuZhong().get(0));
        System.out.println("骨重批注：" + baZi.getGuZhong().get(1));

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("公历起运日期：" + baZi.getSolarQiYunDateStr());
        System.out.println("公历起运信息：" + baZi.getSolarQiYun());
        System.out.println("公历交运信息：" + baZi.getSolarJiaoYun());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("星宿：" + baZi.getXingXiu());
        System.out.println("星宿吉凶：" + baZi.getXingXiuJiXiong());
        System.out.println("星宿吉凶歌诀：" + baZi.getXingXiuJiXiongGeJue());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("彭祖百忌：" + baZi.getPengZuBaiJi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("命卦：" + baZi.getMingGua());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("日柱论命：" + baZi.getRiZhuLunMing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("五行分析：" + baZi.getWuXingFenXi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("运势分析：" + baZi.getYunShiFenXi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("性格分析：" + baZi.getXingGeFenXi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("正财运：" + baZi.getZhengCaiYun());
        System.out.println();
        System.out.println("正财运：" + baZi.getPianCaiYun());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("正桃花运：" + baZi.getZhengTaoHuaYun());
        System.out.println();
        System.out.println("偏桃花运：" + baZi.getPianTaoHuaYun());

    }

    /**
     * 大运流年
     */
    @Test
    public void daYunTest() {

        // 1、神煞设置
        BaZiShenShaSetting baZiShenShaSetting = new BaZiShenShaSetting();
//        baZiShenShaSetting.setTaiJiGuiRen(0); // 太极贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setTianYiGuiRen(0); // 天乙贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setFuXingGuiRen(0); // 福星贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setWenChangGuiRen(0); // 文昌贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setTianChuGuiRen(0); // 天厨贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setYueDeGuiRen(0); // 月德贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setDeXiuGuiRen(0); // 德秀贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setTianDeGuiRen(0); // 天德贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setTianGuanGuiRen(0); // 天官贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setSanQiGuiRen(0); // 三奇贵人（0:显示。1:关闭）
//        baZiShenShaSetting.setShiEDaBai(0); // 十恶大败（0:显示。1:关闭）
//        baZiShenShaSetting.setYinZhuYangShou(0); // 阴注阳受（0:显示。1:关闭）
//        baZiShenShaSetting.setYinChaYangCuo(0); // 阴差阳错（0:显示。1:关闭）
//        baZiShenShaSetting.setTianDeHe(0); // 天德合（0:显示。1:关闭）
//        baZiShenShaSetting.setYueDeHe(0); // 月德合（0:显示。1:关闭）
//        baZiShenShaSetting.setSiFeiRi(0); // 四废日（0:显示。1:关闭）
//        baZiShenShaSetting.setLiuXiuRi(0); // 六秀日（0:显示。1:关闭）
//        baZiShenShaSetting.setShiLingRi(0); // 十灵日（0:显示。1:关闭）
//        baZiShenShaSetting.setKuiGangRi(0); // 魁罡日（0:显示。1:关闭）
//        baZiShenShaSetting.setBaZhuanRi(0); // 八专日（0:显示。1:关闭）
//        baZiShenShaSetting.setJiuChouRi(0); // 九丑日（0:显示。1:关闭）
//        baZiShenShaSetting.setGuLuanSha(0); // 孤鸾煞（0:显示。1:关闭）
//        baZiShenShaSetting.setHongYanSha(0); // 红艳煞（0:显示。1:关闭）
//        baZiShenShaSetting.setGouJiaoSha(0); // 勾绞煞（0:显示。1:关闭）
//        baZiShenShaSetting.setChongTianSha(0); // 冲天煞（0:显示。1:关闭）
//        baZiShenShaSetting.setTongZiSha(0); // 童子煞（0:显示。1:关闭）
//        baZiShenShaSetting.setHuaGai(0); // 华盖（0:显示。1:关闭）
//        baZiShenShaSetting.setGuoYin(0); // 国印（0:显示。1:关闭）
//        baZiShenShaSetting.setJinYu(0); // 金舆（0:显示。1:关闭）
//        baZiShenShaSetting.setYangRen(0); // 羊刃（0:显示。1:关闭）
//        baZiShenShaSetting.setFeiRen(0); // 飞刃（0:显示。1:关闭）
//        baZiShenShaSetting.setLiuXia(0); // 流霞（0:显示。1:关闭）
//        baZiShenShaSetting.setLuShen(0); // 禄神（0:显示。1:关闭）
//        baZiShenShaSetting.setYiMa(0); // 驿马（0:显示。1:关闭）
//        baZiShenShaSetting.setTianLuoDiWang(0); // 天罗\地网（0:显示。1:关闭）
//        baZiShenShaSetting.setKongWang(0); // 空亡（0:显示。1:关闭）
//        baZiShenShaSetting.setJieKong(0); // 截空（0:显示。1:关闭）
//        baZiShenShaSetting.setJieSha(0); // 劫煞（0:显示。1:关闭）
//        baZiShenShaSetting.setJiangXing(0); // 将星（0:显示。1:关闭）
//        baZiShenShaSetting.setTaoHua(0); // 桃花（0:显示。1:关闭）
//        baZiShenShaSetting.setWangShen(0); // 亡神（0:显示。1:关闭）
//        baZiShenShaSetting.setDiaoKe(0); // 吊客（0:显示。1:关闭）
//        baZiShenShaSetting.setPiMa(0); // 披麻（0:显示。1:关闭）
//        baZiShenShaSetting.setTianXi(0); // 天喜（0:显示。1:关闭）
//        baZiShenShaSetting.setHongLuan(0); // 红鸾（0:显示。1:关闭）
//        baZiShenShaSetting.setSangMen(0); // 丧门（0:显示。1:关闭）
//        baZiShenShaSetting.setZaiSha(0); // 灾煞（0:显示。1:关闭）
//        baZiShenShaSetting.setGuChen(0); // 孤辰（0:显示。1:关闭）
//        baZiShenShaSetting.setGuaXiu(0); // 寡宿（0:显示。1:关闭）
//        baZiShenShaSetting.setYuanChen(0); // 元辰（0:显示。1:关闭）
//        baZiShenShaSetting.setXueRen(0); // 血刃（0:显示。1:关闭）
//        baZiShenShaSetting.setTianYi(0); // 天医（0:显示。1:关闭）
//        baZiShenShaSetting.setCiGuan(0); // 词馆（0:显示。1:关闭）
//        baZiShenShaSetting.setXueTang(0); // 学堂（0:显示。1:关闭）
//        baZiShenShaSetting.setTianShe(0); // 天赦（0:显示。1:关闭）
//        baZiShenShaSetting.setTianZhuan(0); // 天转（0:显示。1:关闭）
//        baZiShenShaSetting.setDiZhuan(0); // 地转（0:显示。1:关闭）
//        baZiShenShaSetting.setGongLu(0); // 拱禄（0:显示。1:关闭）
//        baZiShenShaSetting.setJinShen(0); // 金神（0:显示。1:关闭）
//        baZiShenShaSetting.setLiuE(0); // 六厄（0:显示。1:关闭）


        // 2、初始化
        Date solarDate = new Date(2024 - 1900, 1 - 1, 1, 0, 0, 0); // 公历日期
        BaZiDaYunLiuNianUtil baZiDaYunLiuNianUtil = new BaZiDaYunLiuNianUtil(baZiShenShaSetting, solarDate, 1, 1, 2, 1, 0);


        // 3.1、获取大运（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历年、年龄、公历日期）
        List<List<String>> daYun = baZiDaYunLiuNianUtil.getDaYun(10); // 获取大运

        // 3.2、获取流年（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历年、年龄、公历日期）
        List<List<String>> liuNian = baZiDaYunLiuNianUtil.getLiuNian(10, 1); // 获取流年

        // 3.3、获取小运（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历年、年龄、公历日期）
        List<List<String>> xiaoYun = baZiDaYunLiuNianUtil.getXiaoYun(10, 1); // 获取小运

        // 3.4、获取流月（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历几月几日、十二节农历月、十二节、公历日期）
        List<List<String>> liuYue = baZiDaYunLiuNianUtil.getLiuYue(10, 1, 1, 2024); // 获取流月【注意：公历年需动态获取，此处仅用于演示】

        // 3.5、获取流日（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历日、农历日、公历日期）
        List<List<String>> liuRi = baZiDaYunLiuNianUtil.getLiuRi(2024, 2); // 获取流日【注意：公历年、公历月需动态获取，此处仅用于演示】

        // 3.6、获取流时（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历时、汉代命名、公历日期）
        List<List<String>> liuShi = baZiDaYunLiuNianUtil.getLiuShi(2024, 2, 4); // 获取流时【注意：公历年、公历月、公历日需动态获取，此处仅用于演示】


        // 4、数据
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ ☯ 大运流年 ☯ ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐\n");

        System.out.println("公历日期：" + DateUtil.getDateStr(solarDate, DateUtil.DATE_TIME_FORMAT));

        System.out.println("\n\n----------------------------------------------------- 大运 -----------------------------------------------------\n");
        for (List<String> value : daYun) {
            System.out.println(value);
        }

        System.out.println("\n\n----------------------------------------------------- 流年 -----------------------------------------------------\n");
        for (List<String> value : liuNian) {
            System.out.println(value);
        }

        System.out.println("\n\n----------------------------------------------------- 小运 -----------------------------------------------------\n");
        for (List<String> value : xiaoYun) {
            System.out.println(value);
        }

        System.out.println("\n\n----------------------------------------------------- 流月 -----------------------------------------------------\n");
        for (List<String> value : liuYue) {
            System.out.println(value);
        }

        System.out.println("\n\n----------------------------------------------------- 流日 -----------------------------------------------------\n");
        for (List<String> value : liuRi) {
            System.out.println(value);
        }

        System.out.println("\n\n----------------------------------------------------- 流时 -----------------------------------------------------\n");
        for (List<String> value : liuShi) {
            System.out.println(value);
        }

    }


}
