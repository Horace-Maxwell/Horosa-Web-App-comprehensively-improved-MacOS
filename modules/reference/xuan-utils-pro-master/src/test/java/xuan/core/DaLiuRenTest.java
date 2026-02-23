package xuan.core;

import org.junit.Test;
import xuan.core.daliuren.DaLiuRen;
import xuan.core.daliuren.settings.DaLiuRenJiChuSetting;

/**
 * 大六壬测试
 *
 * @author 善待
 */
public class DaLiuRenTest {

    /**
     * 大六壬排盘
     */
    @Test
    public void daLiuRenTest() {

        // 1、基础设置
        DaLiuRenJiChuSetting daLiuRenJiChuSetting = new DaLiuRenJiChuSetting();
        daLiuRenJiChuSetting.setName("某人"); // 姓名
        daLiuRenJiChuSetting.setOccupy("某事"); // 占事
        daLiuRenJiChuSetting.setSex(1); // 性别（0:女。1:男）
        daLiuRenJiChuSetting.setDate("2024-01-01 00:00:00"); // 日期
        daLiuRenJiChuSetting.setDateType(0); // 日期类型（0:公历。1:农历）
        daLiuRenJiChuSetting.setLeapMonthType(0); // 闰月类型，日期类型为1时生效（0:不使用闰月。1:使用闰月）
        daLiuRenJiChuSetting.setXuShiSuiType(0); // 虚实岁类型（0:虚岁。1:实岁）
        daLiuRenJiChuSetting.setJieQiType(1); // 节气类型（0:按天计算。1:按分钟计算）
        daLiuRenJiChuSetting.setGuiRenType(0); // 贵人类型（0:自动切换。1:昼贵。2:夜贵）
        daLiuRenJiChuSetting.setYearGanZhiType(2); // 年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接的时刻作为新年的开始）
        daLiuRenJiChuSetting.setMonthGanZhiType(1); // 月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
        daLiuRenJiChuSetting.setDayGanZhiType(0); // 日干支类型（0:晚子时日干支算当天。1:晚子时日干支算明天）


        // 2、神煞设置（可选）
//        DaLiuRenShenShaSetting daLiuRenShenShaSetting = new DaLiuRenShenShaSetting();


        // 3、初始化
        DaLiuRen daLiuRen = new DaLiuRen(daLiuRenJiChuSetting); // 使用基础设置初始化
//        daLiuRen.daLiuRenShenShaSetting(daLiuRenShenShaSetting); // 神煞设置


        // 4、数据
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ ☯ 大六壬 ☯ ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐\n");

        System.out.println("公历日期（Solar型）：" + daLiuRen.getSolar());
        System.out.println("农历日期（Lunar型）：" + daLiuRen.getLunar());
        System.out.println("公历日期（String型）：" + daLiuRen.getSolarStr());
        System.out.println("农历日期（String型）：" + daLiuRen.getLunarStr());
        System.out.println("公历日期（String型）：" + daLiuRen.getSolarStr2());
        System.out.println("农历日期（String型）：" + daLiuRen.getLunarStr2());
        System.out.println("公历日期（Date型）：" + daLiuRen.getSolarDate());
        System.out.println("农历日期（Date型）：" + daLiuRen.getLunarDate());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("姓名：" + daLiuRen.getName());
        System.out.println("占事：" + daLiuRen.getOccupy());
        System.out.println("性别：" + daLiuRen.getSex());
        System.out.println("年龄：" + daLiuRen.getAge());
        System.out.println("造：" + daLiuRen.getZao());
        System.out.println("星期：" + daLiuRen.getXingQi());
        System.out.println("季节：" + daLiuRen.getJiJie());
        System.out.println("生肖：" + daLiuRen.getShengXiao());
        System.out.println("星座：" + daLiuRen.getXingZuo());
        System.out.println("五不遇时：" + daLiuRen.getWuBuYuShi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干：" + daLiuRen.getYearGan());
        System.out.println("月干：" + daLiuRen.getMonthGan());
        System.out.println("日干：" + daLiuRen.getDayGan());
        System.out.println("时干：" + daLiuRen.getHourGan());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支：" + daLiuRen.getYearZhi());
        System.out.println("月支：" + daLiuRen.getMonthZhi());
        System.out.println("日支：" + daLiuRen.getDayZhi());
        System.out.println("时支：" + daLiuRen.getHourZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支：" + daLiuRen.getYearGanZhi());
        System.out.println("月干支：" + daLiuRen.getMonthGanZhi());
        System.out.println("日干支：" + daLiuRen.getDayGanZhi());
        System.out.println("时干支：" + daLiuRen.getHourGanZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干五行：" + daLiuRen.getYearGanWuXing());
        System.out.println("月干五行：" + daLiuRen.getMonthGanWuXing());
        System.out.println("日干五行：" + daLiuRen.getDayGanWuXing());
        System.out.println("时干五行：" + daLiuRen.getHourGanWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支五行：" + daLiuRen.getYearZhiWuXing());
        System.out.println("月支五行：" + daLiuRen.getMonthZhiWuXing());
        System.out.println("日支五行：" + daLiuRen.getDayZhiWuXing());
        System.out.println("时支五行：" + daLiuRen.getHourZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支五行：" + daLiuRen.getYearGanZhiWuXing());
        System.out.println("月干支五行：" + daLiuRen.getMonthGanZhiWuXing());
        System.out.println("日干支五行：" + daLiuRen.getDayGanZhiWuXing());
        System.out.println("时干支五行：" + daLiuRen.getHourGanZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支纳音：" + daLiuRen.getYearGanZhiNaYin());
        System.out.println("月干支纳音：" + daLiuRen.getMonthGanZhiNaYin());
        System.out.println("日干支纳音：" + daLiuRen.getDayGanZhiNaYin());
        System.out.println("时干支纳音：" + daLiuRen.getHourGanZhiNaYin());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支空亡：" + daLiuRen.getYearGanZhiKongWang());
        System.out.println("月干支空亡：" + daLiuRen.getMonthGanZhiKongWang());
        System.out.println("日干支空亡：" + daLiuRen.getDayGanZhiKongWang());
        System.out.println("时干支空亡：" + daLiuRen.getHourGanZhiKongWang());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("五行旺衰：" + daLiuRen.getWuXingWangShuai());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一节：" + daLiuRen.getPrevJie());
        System.out.println("上一节日期：" + daLiuRen.getPrevJieDateStr());
        System.out.println("距上一节天数：" + daLiuRen.getPrevJieDay());
        System.out.println();
        System.out.println("下一节：" + daLiuRen.getNextJie());
        System.out.println("下一节日期：" + daLiuRen.getNextJieDateStr());
        System.out.println("距下一节天数：" + daLiuRen.getNextJieDay());
        System.out.println();
        System.out.println("出生节：" + daLiuRen.getChuShengJie());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一气：" + daLiuRen.getPrevQi());
        System.out.println("上一气日期：" + daLiuRen.getPrevQiDateStr());
        System.out.println("距上一气天数：" + daLiuRen.getPrevQiDay());
        System.out.println();
        System.out.println("下一气：" + daLiuRen.getNextQi());
        System.out.println("下一气日期：" + daLiuRen.getNextQiDateStr());
        System.out.println("距下一气天数：" + daLiuRen.getNextQiDay());
        System.out.println();
        System.out.println("出生气：" + daLiuRen.getChuShengQi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("月相：" + daLiuRen.getYueXiang());
        System.out.println("月将：" + daLiuRen.getYueJiang());
        System.out.println("月将神：" + daLiuRen.getYueJiangShen());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("天地盘类型：" + daLiuRen.getTianDiPanType());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("地盘（1~12宫）：" + daLiuRen.getDiPan());
        System.out.println("天盘（1~12宫）：" + daLiuRen.getTianPan());
        System.out.println("神盘（1~12宫）：" + daLiuRen.getShenPan());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("天干（1~12宫）：" + daLiuRen.getTianGan());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("四课：" + daLiuRen.getSiKe());
        System.out.println("四课遁干：" + daLiuRen.getSiKeDunGan());
        System.out.println("四课神将：" + daLiuRen.getSiKeShenJiang());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("三传：" + daLiuRen.getSanChuan());
        System.out.println("三传遁干：" + daLiuRen.getSanChuanDunGan());
        System.out.println("三传神将：" + daLiuRen.getSanChuanShenJiang());
        System.out.println("三传六亲：" + daLiuRen.getSanChuanLiuQin());

    }


}
