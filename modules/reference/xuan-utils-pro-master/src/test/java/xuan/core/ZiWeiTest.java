package xuan.core;

import org.junit.Test;
import xuan.core.ziwei.ZiWei;
import xuan.core.ziwei.settings.ZiWeiJiChuSetting;

/**
 * 紫微斗数测试
 *
 * @author 善待
 */
public class ZiWeiTest {

    /**
     * 紫微斗数排盘
     */
    @Test
    public void ziWeiTest() {

        // 1、基础设置
        ZiWeiJiChuSetting ziWeiJiChuSetting = new ZiWeiJiChuSetting();
        ziWeiJiChuSetting.setName("某人"); // 姓名
        ziWeiJiChuSetting.setOccupy("某事"); // 占事
        ziWeiJiChuSetting.setSex(1); // 性别（0:女。1:男）
        ziWeiJiChuSetting.setDate("2024-01-01 00:00:00"); // 日期
        ziWeiJiChuSetting.setDateType(0); // 日期类型（0:公历。1:农历）
        ziWeiJiChuSetting.setLeapMonthType(0); // 闰月类型，日期类型为1时生效（0:不使用闰月。1:使用闰月）
        ziWeiJiChuSetting.setXuShiSuiType(0); // 虚实岁类型（0:虚岁。1:实岁）
        ziWeiJiChuSetting.setJieQiType(1); // 节气类型（0:按天计算。1:按分钟计算）
        ziWeiJiChuSetting.setWuXingJuType(0); // 五行局类型（0:按年干+命宫地支计算。1:按命宫天干+命宫地支计算）
        ziWeiJiChuSetting.setYearGanZhiType(2); // 年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接的时刻作为新年的开始）
        ziWeiJiChuSetting.setMonthGanZhiType(1); // 月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
        ziWeiJiChuSetting.setDayGanZhiType(0); // 日干支类型（0:晚子时日干支算当天。1:晚子时日干支算明天）


        // 2、初始化
        ZiWei ziWei = new ZiWei(ziWeiJiChuSetting); // 使用基础设置初始化


        // 3、数据
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ ☯ 紫微斗数 ☯ ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐\n");

        System.out.println("公历日期（Solar型）：" + ziWei.getSolar());
        System.out.println("农历日期（Lunar型）：" + ziWei.getLunar());
        System.out.println("公历日期（String型）：" + ziWei.getSolarStr());
        System.out.println("农历日期（String型）：" + ziWei.getLunarStr());
        System.out.println("公历日期（String型）：" + ziWei.getSolarStr2());
        System.out.println("农历日期（String型）：" + ziWei.getLunarStr2());
        System.out.println("公历日期（Date型）：" + ziWei.getSolarDate());
        System.out.println("农历日期（Date型）：" + ziWei.getLunarDate());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("姓名：" + ziWei.getName());
        System.out.println("占事：" + ziWei.getOccupy());
        System.out.println("性别：" + ziWei.getSex());
        System.out.println("年龄：" + ziWei.getAge());
        System.out.println("造：" + ziWei.getZao());
        System.out.println("星期：" + ziWei.getXingQi());
        System.out.println("季节：" + ziWei.getJiJie());
        System.out.println("生肖：" + ziWei.getShengXiao());
        System.out.println("星座：" + ziWei.getXingZuo());
        System.out.println("五不遇时：" + ziWei.getWuBuYuShi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干：" + ziWei.getYearGan());
        System.out.println("月干：" + ziWei.getMonthGan());
        System.out.println("日干：" + ziWei.getDayGan());
        System.out.println("时干：" + ziWei.getHourGan());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支：" + ziWei.getYearZhi());
        System.out.println("月支：" + ziWei.getMonthZhi());
        System.out.println("日支：" + ziWei.getDayZhi());
        System.out.println("时支：" + ziWei.getHourZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支：" + ziWei.getYearGanZhi());
        System.out.println("月干支：" + ziWei.getMonthGanZhi());
        System.out.println("日干支：" + ziWei.getDayGanZhi());
        System.out.println("时干支：" + ziWei.getHourGanZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干五行：" + ziWei.getYearGanWuXing());
        System.out.println("月干五行：" + ziWei.getMonthGanWuXing());
        System.out.println("日干五行：" + ziWei.getDayGanWuXing());
        System.out.println("时干五行：" + ziWei.getHourGanWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支五行：" + ziWei.getYearZhiWuXing());
        System.out.println("月支五行：" + ziWei.getMonthZhiWuXing());
        System.out.println("日支五行：" + ziWei.getDayZhiWuXing());
        System.out.println("时支五行：" + ziWei.getHourZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支五行：" + ziWei.getYearGanZhiWuXing());
        System.out.println("月干支五行：" + ziWei.getMonthGanZhiWuXing());
        System.out.println("日干支五行：" + ziWei.getDayGanZhiWuXing());
        System.out.println("时干支五行：" + ziWei.getHourGanZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支纳音：" + ziWei.getYearGanZhiNaYin());
        System.out.println("月干支纳音：" + ziWei.getMonthGanZhiNaYin());
        System.out.println("日干支纳音：" + ziWei.getDayGanZhiNaYin());
        System.out.println("时干支纳音：" + ziWei.getHourGanZhiNaYin());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支空亡：" + ziWei.getYearGanZhiKongWang());
        System.out.println("月干支空亡：" + ziWei.getMonthGanZhiKongWang());
        System.out.println("日干支空亡：" + ziWei.getDayGanZhiKongWang());
        System.out.println("时干支空亡：" + ziWei.getHourGanZhiKongWang());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一节：" + ziWei.getPrevJie());
        System.out.println("上一节日期：" + ziWei.getPrevJieDateStr());
        System.out.println("距上一节天数：" + ziWei.getPrevJieDay());
        System.out.println();
        System.out.println("下一节：" + ziWei.getNextJie());
        System.out.println("下一节日期：" + ziWei.getNextJieDateStr());
        System.out.println("距下一节天数：" + ziWei.getNextJieDay());
        System.out.println();
        System.out.println("出生节：" + ziWei.getChuShengJie());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一气：" + ziWei.getPrevQi());
        System.out.println("上一气日期：" + ziWei.getPrevQiDateStr());
        System.out.println("距上一气天数：" + ziWei.getPrevQiDay());
        System.out.println();
        System.out.println("下一气：" + ziWei.getNextQi());
        System.out.println("下一气日期：" + ziWei.getNextQiDateStr());
        System.out.println("距下一气天数：" + ziWei.getNextQiDay());
        System.out.println();
        System.out.println("出生气：" + ziWei.getChuShengQi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("月相：" + ziWei.getYueXiang());
        System.out.println("月将：" + ziWei.getYueJiang());
        System.out.println("月将神：" + ziWei.getYueJiangShen());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("十二宫地支：" + ziWei.getShiErGongDiZhi());
        System.out.println("十二宫天干：" + ziWei.getShiErGongTianGan());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("命宫宫位：" + ziWei.getMingGongGongWei());
        System.out.println("身宫宫位：" + ziWei.getShenGongGongWei());
        System.out.println("紫微星宫位：" + ziWei.getZiWeiXingGongWei());
        System.out.println("天府星宫位：" + ziWei.getTianFuXingGongWei());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("命宫宫位地支：" + ziWei.getMingGongDiZhi());
        System.out.println("身宫宫位地支：" + ziWei.getShenGongDiZhi());
        System.out.println("紫微星宫位地支：" + ziWei.getZiWeiXingGongDiZhi());
        System.out.println("天府星宫位地支：" + ziWei.getTianFuXingGongDiZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("十二命宫（1~12宫）：" + ziWei.getShiErMingGong());
        System.out.println("十二身宫（1~12宫）：" + ziWei.getShiErShenGong());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("五行局：" + ziWei.getWuXingJu());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("紫微星系诸星（1~12宫）：" + ziWei.getZiWeiXingXiZhuXing());
        System.out.println("天府星系诸星（1~12宫）：" + ziWei.getTianFuXingXiZhuXing());

        System.out.println("时支诸星（1~12宫）：" + ziWei.getShiZhiZhuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("月支诸星（1~12宫）：" + ziWei.getYueZhiZhuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干诸星（1~12宫）：" + ziWei.getNianGanZhuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支诸星（1~12宫）：" + ziWei.getNianZhiZhuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("日诸星（1~12宫）：" + ziWei.getDayZhuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("十二长生（1~12宫）：" + ziWei.getShiErZhangSheng());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("截路空亡（1~12宫）：" + ziWei.getJieLuKongWang());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("旬中空亡（1~12宫）：" + ziWei.getXunZhongKongWang());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("天伤星、天使星（1~12宫）：" + ziWei.getTianShangTianShiXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("大限：" + ziWei.getDaXian());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("小限：" + ziWei.getXiaoXian());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("十二宫博士（1~12宫）：" + ziWei.getShiErGongBoShi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("流年岁前诸星（1~12宫）：" + ziWei.getLiuNianSuiQianZhuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("流年将前诸星（1~12宫）：" + ziWei.getLiuNianJiangQianZhuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("★ 十二个宫位中每个宫位中的诸星（1~12宫）：" + ziWei.getShiErGongZhuXing(false));
        System.out.println();
        System.out.println("★ 十二个宫位中每个宫位中的诸星庙旺平陷关系（1~12宫）：" + ziWei.getShiErGongZhuXingGuanXi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("十二个宫位中每个宫位中的四化星（1~12宫）：" + ziWei.getShiErGongSiHuaXing());
        System.out.println("十二个宫位中每个宫位中的四化星庙旺平陷关系（1~12宫）：" + ziWei.getShiErGongSiHuaXingGuanXi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("化禄星宫位解读：" + ziWei.getHuaLuXingGongWeiJieDu());
        System.out.println("化权星宫位解读：" + ziWei.getHuaQuanXingGongWeiJieDu());
        System.out.println("化科星宫位解读：" + ziWei.getHuaKeXingGongWeiJieDu());
        System.out.println("化忌星宫位解读：" + ziWei.getHuaJiXingGongWeiJieDu());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("命主：" + ziWei.getMingZhu());
        System.out.println("身主：" + ziWei.getShenZhu());
        System.out.println("子斗：" + ziWei.getZiDou());
        System.out.println("流斗：" + ziWei.getLiuDou());

    }


}
