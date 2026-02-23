package xuan.core;

import org.junit.Test;
import xuan.core.meihua.MeiHua;
import xuan.core.meihua.settings.MeiHuaJiChuSetting;

/**
 * 梅花易数测试
 *
 * @author 善待
 */
public class MeiHuaTest {

    /**
     * 梅花易数排盘
     */
    @Test
    public void meiHuaTest() {

        // 1、基础设置
        MeiHuaJiChuSetting meiHuaJiChuSetting = new MeiHuaJiChuSetting();
        meiHuaJiChuSetting.setName("某人"); // 姓名
        meiHuaJiChuSetting.setOccupy("某事"); // 占事
        meiHuaJiChuSetting.setSex(1); // 性别（0:女。1:男）
        meiHuaJiChuSetting.setDate("2024-01-01 00:00:00"); // 日期
        meiHuaJiChuSetting.setDateType(0); // 日期类型（0:公历。1:农历）
        meiHuaJiChuSetting.setLeapMonthType(0); // 闰月类型，日期类型为1时生效（0:不使用闰月。1:使用闰月）
        meiHuaJiChuSetting.setXuShiSuiType(0); // 虚实岁类型（0:虚岁。1:实岁）
        meiHuaJiChuSetting.setJieQiType(1); // 节气类型（0:按天计算。1:按分钟计算）
        meiHuaJiChuSetting.setPaiPanType(0); // 排盘类型（0:日期。1:自动。2:数字。3:单数。4:双数）
        meiHuaJiChuSetting.setShu(111); // 数字，排盘类型为2时生效
        meiHuaJiChuSetting.setDanShu(111); // 单数，排盘类型为3时生效
        meiHuaJiChuSetting.setShuangShuOne(111); // 双数1，排盘类型为4时生效
        meiHuaJiChuSetting.setShuangShuTwo(111); // 双数2，排盘类型为4时生效
        meiHuaJiChuSetting.setShangXiaGuaType(1); // 上下卦类型，排盘类型为4时生效（0:双数求和计算上下卦。1:双数不求和计算上下卦）
        meiHuaJiChuSetting.setDongYaoType(0); // 动爻类型，排盘类型为4时生效（0:双数求和计算动爻。1:双数求和加时辰数计算动爻）
        meiHuaJiChuSetting.setYearGanZhiType(2); // 年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接的时刻作为新年的开始）
        meiHuaJiChuSetting.setMonthGanZhiType(1); // 月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
        meiHuaJiChuSetting.setDayGanZhiType(0); // 日干支类型（0:晚子时日干支算当天。1:晚子时日干支算明天）


        // 2、初始化
        MeiHua meiHua = new MeiHua(meiHuaJiChuSetting); // 使用基础设置初始化


        // 3、数据
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ ☯ 梅花易数 ☯ ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐\n");

        System.out.println("公历日期（Solar型）：" + meiHua.getSolar());
        System.out.println("农历日期（Lunar型）：" + meiHua.getLunar());
        System.out.println("公历日期（String型）：" + meiHua.getSolarStr());
        System.out.println("农历日期（String型）：" + meiHua.getLunarStr());
        System.out.println("公历日期（String型）：" + meiHua.getSolarStr2());
        System.out.println("农历日期（String型）：" + meiHua.getLunarStr2());
        System.out.println("公历日期（Date型）：" + meiHua.getSolarDate());
        System.out.println("农历日期（Date型）：" + meiHua.getLunarDate());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("姓名：" + meiHua.getName());
        System.out.println("占事：" + meiHua.getOccupy());
        System.out.println("性别：" + meiHua.getSex());
        System.out.println("年龄：" + meiHua.getAge());
        System.out.println("造：" + meiHua.getZao());
        System.out.println("星期：" + meiHua.getXingQi());
        System.out.println("季节：" + meiHua.getJiJie());
        System.out.println("生肖：" + meiHua.getShengXiao());
        System.out.println("星座：" + meiHua.getXingZuo());
        System.out.println("五不遇时：" + meiHua.getWuBuYuShi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干：" + meiHua.getYearGan());
        System.out.println("月干：" + meiHua.getMonthGan());
        System.out.println("日干：" + meiHua.getDayGan());
        System.out.println("时干：" + meiHua.getHourGan());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支：" + meiHua.getYearZhi());
        System.out.println("月支：" + meiHua.getMonthZhi());
        System.out.println("日支：" + meiHua.getDayZhi());
        System.out.println("时支：" + meiHua.getHourZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支：" + meiHua.getYearGanZhi());
        System.out.println("月干支：" + meiHua.getMonthGanZhi());
        System.out.println("日干支：" + meiHua.getDayGanZhi());
        System.out.println("时干支：" + meiHua.getHourGanZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干五行：" + meiHua.getYearGanWuXing());
        System.out.println("月干五行：" + meiHua.getMonthGanWuXing());
        System.out.println("日干五行：" + meiHua.getDayGanWuXing());
        System.out.println("时干五行：" + meiHua.getHourGanWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支五行：" + meiHua.getYearZhiWuXing());
        System.out.println("月支五行：" + meiHua.getMonthZhiWuXing());
        System.out.println("日支五行：" + meiHua.getDayZhiWuXing());
        System.out.println("时支五行：" + meiHua.getHourZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支五行：" + meiHua.getYearGanZhiWuXing());
        System.out.println("月干支五行：" + meiHua.getMonthGanZhiWuXing());
        System.out.println("日干支五行：" + meiHua.getDayGanZhiWuXing());
        System.out.println("时干支五行：" + meiHua.getHourGanZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支纳音：" + meiHua.getYearGanZhiNaYin());
        System.out.println("月干支纳音：" + meiHua.getMonthGanZhiNaYin());
        System.out.println("日干支纳音：" + meiHua.getDayGanZhiNaYin());
        System.out.println("时干支纳音：" + meiHua.getHourGanZhiNaYin());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支空亡：" + meiHua.getYearGanZhiKongWang());
        System.out.println("月干支空亡：" + meiHua.getMonthGanZhiKongWang());
        System.out.println("日干支空亡：" + meiHua.getDayGanZhiKongWang());
        System.out.println("时干支空亡：" + meiHua.getHourGanZhiKongWang());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一节：" + meiHua.getPrevJie());
        System.out.println("上一节日期：" + meiHua.getPrevJieDateStr());
        System.out.println("距上一节天数：" + meiHua.getPrevJieDay());
        System.out.println();
        System.out.println("下一节：" + meiHua.getNextJie());
        System.out.println("下一节日期：" + meiHua.getNextJieDateStr());
        System.out.println("距下一节天数：" + meiHua.getNextJieDay());
        System.out.println();
        System.out.println("出生节：" + meiHua.getChuShengJie());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一气：" + meiHua.getPrevQi());
        System.out.println("上一气日期：" + meiHua.getPrevQiDateStr());
        System.out.println("距上一气天数：" + meiHua.getPrevQiDay());
        System.out.println();
        System.out.println("下一气：" + meiHua.getNextQi());
        System.out.println("下一气日期：" + meiHua.getNextQiDateStr());
        System.out.println("距下一气天数：" + meiHua.getNextQiDay());
        System.out.println();
        System.out.println("出生气：" + meiHua.getChuShengQi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("月相：" + meiHua.getYueXiang());
        System.out.println("月将：" + meiHua.getYueJiang());
        System.out.println("月将神：" + meiHua.getYueJiangShen());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上卦卦名：" + meiHua.getShangGuaName());
        System.out.println("下卦卦名：" + meiHua.getXiaGuaName());
        System.out.println("本卦卦名：" + meiHua.getBenGuaName());
        System.out.println("变卦卦名：" + meiHua.getBianGuaName());
        System.out.println("互卦卦名：" + meiHua.getHuGuaName());
        System.out.println("错卦卦名：" + meiHua.getCuoGuaName());
        System.out.println("综卦卦名：" + meiHua.getZongGuaName());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上卦卦象：" + meiHua.getShangGuaAs());
        System.out.println("下卦卦象：" + meiHua.getXiaGuaAs());
        System.out.println("本卦卦象：" + meiHua.getBenGuaAs());
        System.out.println("变卦卦象：" + meiHua.getBianGuaAs());
        System.out.println("互卦卦象：" + meiHua.getHuGuaAs());
        System.out.println("错卦卦象：" + meiHua.getCuoGuaAs());
        System.out.println("综卦卦象：" + meiHua.getZongGuaAs());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦卦辞：" + meiHua.getBenGuaGuaCi());
        System.out.println("变卦卦辞：" + meiHua.getBianGuaGuaCi());
        System.out.println("互卦卦辞：" + meiHua.getHuGuaGuaCi());
        System.out.println("错卦卦辞：" + meiHua.getCuoGuaGuaCi());
        System.out.println("综卦卦辞：" + meiHua.getZongGuaGuaCi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦的上卦卦名：" + meiHua.getBenGuaShangGuaName());
        System.out.println("变卦的上卦卦名：" + meiHua.getBianGuaShangGuaName());
        System.out.println("互卦的上卦卦名：" + meiHua.getHuGuaShangGuaName());
        System.out.println("错卦的上卦卦名：" + meiHua.getCuoGuaShangGuaName());
        System.out.println("综卦的上卦卦名：" + meiHua.getZongGuaShangGuaName());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦的下卦卦名：" + meiHua.getBenGuaXiaGuaName());
        System.out.println("变卦的下卦卦名：" + meiHua.getBianGuaXiaGuaName());
        System.out.println("互卦的下卦卦名：" + meiHua.getHuGuaXiaGuaName());
        System.out.println("错卦的下卦卦名：" + meiHua.getCuoGuaXiaGuaName());
        System.out.println("综卦的下卦卦名：" + meiHua.getZongGuaXiaGuaName());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦的上卦卦象：" + meiHua.getBenGuaShangGuaAs());
        System.out.println("变卦的上卦卦象：" + meiHua.getBianGuaShangGuaAs());
        System.out.println("互卦的上卦卦象：" + meiHua.getHuGuaShangGuaAs());
        System.out.println("错卦的上卦卦象：" + meiHua.getCuoGuaShangGuaAs());
        System.out.println("综卦的上卦卦象：" + meiHua.getZongGuaShangGuaAs());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦的下卦卦象：" + meiHua.getBenGuaXiaGuaAs());
        System.out.println("变卦的下卦卦象：" + meiHua.getBianGuaXiaGuaAs());
        System.out.println("互卦的下卦卦象：" + meiHua.getHuGuaXiaGuaAs());
        System.out.println("错卦的下卦卦象：" + meiHua.getCuoGuaXiaGuaAs());
        System.out.println("综卦的下卦卦象：" + meiHua.getZongGuaXiaGuaAs());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻爻名：" + meiHua.getBenGuaLiuYaoName());
        System.out.println("变卦六爻爻名：" + meiHua.getBianGuaLiuYaoName());
        System.out.println("互卦六爻爻名：" + meiHua.getHuGuaLiuYaoName());
        System.out.println("错卦六爻爻名：" + meiHua.getCuoGuaLiuYaoName());
        System.out.println("综卦六爻爻名：" + meiHua.getZongGuaLiuYaoName());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻爻象：" + meiHua.getBenGuaLiuYaoAs());
        System.out.println("变卦六爻爻象：" + meiHua.getBianGuaLiuYaoAs());
        System.out.println("互卦六爻爻象：" + meiHua.getHuGuaLiuYaoAs());
        System.out.println("错卦六爻爻象：" + meiHua.getCuoGuaLiuYaoAs());
        System.out.println("综卦六爻爻象：" + meiHua.getZongGuaLiuYaoAs());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻爻辞：" + meiHua.getBenGuaLiuYaoYaoCi());
        System.out.println("变卦六爻爻辞：" + meiHua.getBianGuaLiuYaoYaoCi());
        System.out.println("互卦六爻爻辞：" + meiHua.getHuGuaLiuYaoYaoCi());
        System.out.println("错卦六爻爻辞：" + meiHua.getCuoGuaLiuYaoYaoCi());
        System.out.println("综卦六爻爻辞：" + meiHua.getZongGuaLiuYaoYaoCi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦关系：" + meiHua.getBenGuaLink());
        System.out.println("变卦关系：" + meiHua.getBianGuaLink());
        System.out.println("互卦关系：" + meiHua.getHuGuaLink());
        System.out.println("错卦关系：" + meiHua.getCuoGuaLink());
        System.out.println("综卦关系：" + meiHua.getZongGuaLink());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("动爻：" + meiHua.getDongYao());
        System.out.println("动爻文字：" + meiHua.getDongYaoStr());
        System.out.println("卦码：" + meiHua.getGuaMa());

    }


}
