package xuan.core;

import org.junit.Test;
import xuan.core.qimen.zhuan.QiMenZhuanPan;
import xuan.core.qimen.zhuan.settings.QiMenZhuanPanJiChuSetting;

/**
 * 奇门遁甲测试
 *
 * @author 善待
 */
public class QiMenTest {

    /**
     * 转盘奇门排盘
     */
    @Test
    public void zhuanPanQiMenTest() {

        // 1、基础设置
        QiMenZhuanPanJiChuSetting qiMenZhuanPanJiChuSetting = new QiMenZhuanPanJiChuSetting();
        qiMenZhuanPanJiChuSetting.setName("某人"); // 姓名
        qiMenZhuanPanJiChuSetting.setOccupy("某事"); // 占事
        qiMenZhuanPanJiChuSetting.setSex(1); // 性别（0:女。1:男）
        qiMenZhuanPanJiChuSetting.setDate("2024-01-01 00:00:00"); // 日期
        qiMenZhuanPanJiChuSetting.setDateType(0); // 日期类型（0:公历。1:农历）
        qiMenZhuanPanJiChuSetting.setLeapMonthType(0); // 闰月类型，日期类型为1时生效（0:不使用闰月。1:使用闰月）
        qiMenZhuanPanJiChuSetting.setXuShiSuiType(0); // 虚实岁类型（0:虚岁。1:实岁）
        qiMenZhuanPanJiChuSetting.setJieQiType(1); // 节气类型（0:按天计算。1:按分钟计算）
        qiMenZhuanPanJiChuSetting.setPaiPanType(3); // 排盘类型（0:年家奇门。1:月家奇门。2:日家奇门。3:时家奇门）
        qiMenZhuanPanJiChuSetting.setZhiShiType(0); // 值使类型（0:天禽星为值符时，一律用[死门]为值使。1:天禽星为值符时，根据阴阳遁判断。2:天禽星为值符时，根据节气判断）
        qiMenZhuanPanJiChuSetting.setYueJiaQiJuType(1); // 月家奇门起局类型，排盘类型为1时生效（0:使用年支起局。1:使用年干支的符头地支起局）
        qiMenZhuanPanJiChuSetting.setYearGanZhiType(2); // 年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接的时刻作为新年的开始）
        qiMenZhuanPanJiChuSetting.setMonthGanZhiType(1); // 月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
        qiMenZhuanPanJiChuSetting.setDayGanZhiType(0); // 日干支类型（0:晚子时日干支算当天。1:晚子时日干支算明天）


        // 2、初始化
        QiMenZhuanPan qiMen = new QiMenZhuanPan(qiMenZhuanPanJiChuSetting); // 使用基础设置初始化


        // 3、数据
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ ☯ 转盘奇门 ☯ ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐\n");

        System.out.println("公历日期（Solar型）：" + qiMen.getSolar());
        System.out.println("农历日期（Lunar型）：" + qiMen.getLunar());
        System.out.println("公历日期（String型）：" + qiMen.getSolarStr());
        System.out.println("农历日期（String型）：" + qiMen.getLunarStr());
        System.out.println("公历日期（String型）：" + qiMen.getSolarStr2());
        System.out.println("农历日期（String型）：" + qiMen.getLunarStr2());
        System.out.println("公历日期（Date型）：" + qiMen.getSolarDate());
        System.out.println("农历日期（Date型）：" + qiMen.getLunarDate());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("姓名：" + qiMen.getName());
        System.out.println("占事：" + qiMen.getOccupy());
        System.out.println("性别：" + qiMen.getSex());
        System.out.println("年龄：" + qiMen.getAge());
        System.out.println("造：" + qiMen.getZao());
        System.out.println("星期：" + qiMen.getXingQi());
        System.out.println("季节：" + qiMen.getJiJie());
        System.out.println("生肖：" + qiMen.getShengXiao());
        System.out.println("星座：" + qiMen.getXingZuo());
        System.out.println("五不遇时：" + qiMen.getWuBuYuShi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干：" + qiMen.getYearGan());
        System.out.println("月干：" + qiMen.getMonthGan());
        System.out.println("日干：" + qiMen.getDayGan());
        System.out.println("时干：" + qiMen.getHourGan());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支：" + qiMen.getYearZhi());
        System.out.println("月支：" + qiMen.getMonthZhi());
        System.out.println("日支：" + qiMen.getDayZhi());
        System.out.println("时支：" + qiMen.getHourZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支：" + qiMen.getYearGanZhi());
        System.out.println("月干支：" + qiMen.getMonthGanZhi());
        System.out.println("日干支：" + qiMen.getDayGanZhi());
        System.out.println("时干支：" + qiMen.getHourGanZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干五行：" + qiMen.getYearGanWuXing());
        System.out.println("月干五行：" + qiMen.getMonthGanWuXing());
        System.out.println("日干五行：" + qiMen.getDayGanWuXing());
        System.out.println("时干五行：" + qiMen.getHourGanWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支五行：" + qiMen.getYearZhiWuXing());
        System.out.println("月支五行：" + qiMen.getMonthZhiWuXing());
        System.out.println("日支五行：" + qiMen.getDayZhiWuXing());
        System.out.println("时支五行：" + qiMen.getHourZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支五行：" + qiMen.getYearGanZhiWuXing());
        System.out.println("月干支五行：" + qiMen.getMonthGanZhiWuXing());
        System.out.println("日干支五行：" + qiMen.getDayGanZhiWuXing());
        System.out.println("时干支五行：" + qiMen.getHourGanZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支纳音：" + qiMen.getYearGanZhiNaYin());
        System.out.println("月干支纳音：" + qiMen.getMonthGanZhiNaYin());
        System.out.println("日干支纳音：" + qiMen.getDayGanZhiNaYin());
        System.out.println("时干支纳音：" + qiMen.getHourGanZhiNaYin());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支空亡：" + qiMen.getYearGanZhiKongWang());
        System.out.println("月干支空亡：" + qiMen.getMonthGanZhiKongWang());
        System.out.println("日干支空亡：" + qiMen.getDayGanZhiKongWang());
        System.out.println("时干支空亡：" + qiMen.getHourGanZhiKongWang());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一节：" + qiMen.getPrevJie());
        System.out.println("上一节日期：" + qiMen.getPrevJieDateStr());
        System.out.println("距上一节天数：" + qiMen.getPrevJieDay());
        System.out.println();
        System.out.println("下一节：" + qiMen.getNextJie());
        System.out.println("下一节日期：" + qiMen.getNextJieDateStr());
        System.out.println("距下一节天数：" + qiMen.getNextJieDay());
        System.out.println();
        System.out.println("出生节：" + qiMen.getChuShengJie());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一气：" + qiMen.getPrevQi());
        System.out.println("上一气日期：" + qiMen.getPrevQiDateStr());
        System.out.println("距上一气天数：" + qiMen.getPrevQiDay());
        System.out.println();
        System.out.println("下一气：" + qiMen.getNextQi());
        System.out.println("下一气日期：" + qiMen.getNextQiDateStr());
        System.out.println("距下一气天数：" + qiMen.getNextQiDay());
        System.out.println();
        System.out.println("出生气：" + qiMen.getChuShengQi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("月相：" + qiMen.getYueXiang());
        System.out.println("月将：" + qiMen.getYueJiang());
        System.out.println("月将神：" + qiMen.getYueJiangShen());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("符头：" + qiMen.getFuTou());
        System.out.println("节气：" + qiMen.getJieQi());
        System.out.println("三元：" + qiMen.getSanYuan());
        System.out.println("局数：" + qiMen.getJuShu());
        System.out.println("阴阳遁：" + qiMen.getYinYangDun());
        System.out.println("旬首：" + qiMen.getXunShou());
        System.out.println("旬首仪仗：" + qiMen.getXunShouYiZhang());
        System.out.println("值符：" + qiMen.getZhiFu());
        System.out.println("值使：" + qiMen.getZhiShi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("六甲旬空：" + qiMen.getLiuJiaXunKong());
        System.out.println("六甲旬空落宫：" + qiMen.getLiuJiaXunKongGongWei());
        System.out.println("六甲旬空落宫标识：" + qiMen.getLiuJiaXunKongGongWeiMark());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("驿马：" + qiMen.getYiMa());
        System.out.println("驿马落宫：" + qiMen.getYiMaGongWei());
        System.out.println("驿马落宫标识：" + qiMen.getYiMaGongWeiMark());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("★地盘：" + qiMen.getDiPan());
        System.out.println("★天盘：" + qiMen.getTianPan());
        System.out.println("★人盘：" + qiMen.getRenPan());
        System.out.println("★神盘：" + qiMen.getShenPan());
        System.out.println();
        System.out.println("天盘奇仪（不包含[天禽星]）：" + qiMen.getTianPanQiYiTianQinNo());
        System.out.println("天盘奇仪（只包含[天禽星]）：" + qiMen.getTianPanQiYiTianQinYes());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("天乙：" + qiMen.getTianYi());
        System.out.println("地乙：" + qiMen.getDiYi());
        System.out.println("太乙：" + qiMen.getTaiYi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("九遁：" + qiMen.getJiuDun());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("内外宫位标识：" + qiMen.getNeiWaiGongWeiMark());
        System.out.println("内外宫位信息：" + qiMen.getNeiWaiGongWeiInfo());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("天门：" + qiMen.getTianMen());
        System.out.println("地户：" + qiMen.getDiHu());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("伏吟：" + qiMen.getFuYin());
        System.out.println("反吟：" + qiMen.getFanYin());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("六仪击刑：" + qiMen.getLiuYiJiXing());
        System.out.println("奇仪入墓：" + qiMen.getQiYiRuMu());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("六仪击刑、奇仪入墓状态（不包含[天禽星]）：" + qiMen.getLiuYiJiXingRuMuTianQinNoStatus());
        System.out.println("六仪击刑、奇仪入墓状态（只包含[天禽星]）：" + qiMen.getLiuYiJiXingRuMuTianQinYesStatus());
        System.out.println("门迫状态：" + qiMen.getMenPoStatus());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("十干克应：" + qiMen.getShiGanKeYing());
        System.out.println();
        System.out.println("八门克应：" + qiMen.getBaMenKeYing());
        System.out.println();
        System.out.println("八门静应：" + qiMen.getBaMenJingYing());
        System.out.println();
        System.out.println("八门动应：" + qiMen.getBaMenDongYing());
        System.out.println();
        System.out.println("星门克应：" + qiMen.getXingMenKeYing());
        System.out.println();
        System.out.println("九星时应：" + qiMen.getJiuXingShiYing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("八卦旺衰：" + qiMen.getBaGuaWangShuai());
        System.out.println();
        System.out.println("八门旺衰：" + qiMen.getBaMenWangShuai());
        System.out.println();
        System.out.println("九星旺衰：" + qiMen.getJiuXingWangShuai());

        System.out.println("\n----------------------------------------------------------------------------------------------------------------\n");

        System.out.println("八神落宫状态：" + qiMen.getBaShenLuoGongStatus());
        System.out.println();
        System.out.println("八门落宫状态：" + qiMen.getBaMenLuoGongStatus());
        System.out.println();
        System.out.println("九星落宫状态：" + qiMen.getJiuXingLuoGongStatus());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("地盘奇仪与落宫地支的关系：" + qiMen.getDiPanQiYiLuoGongLink());
        System.out.println();
        System.out.println("天盘奇仪与落宫地支的关系（不包含[天禽星]）：" + qiMen.getTianPanQiYiLuoGongTianQinNoLink());
        System.out.println();
        System.out.println("天盘奇仪与落宫地支的关系（只包含[天禽星]）：" + qiMen.getTianPanQiYiLuoGongTianQinYesLink());

    }


}
