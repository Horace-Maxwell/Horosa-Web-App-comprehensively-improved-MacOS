package xuan.core;

import org.junit.Test;
import xuan.core.liuyao.LiuYao;
import xuan.core.liuyao.settings.LiuYaoJiChuSetting;
import xuan.core.liuyao.settings.LiuYaoShenShaSetting;

/**
 * 六爻测试
 *
 * @author 善待
 */
public class LiuYaoTest {

    /**
     * 六爻排盘
     */
    @Test
    public void liuYaoTest() {

        // 1、基础设置（可选）
        LiuYaoJiChuSetting liuYaoJiChuSetting = new LiuYaoJiChuSetting();
        liuYaoJiChuSetting.setName("某人"); // 姓名
        liuYaoJiChuSetting.setOccupy("某事"); // 占事
        liuYaoJiChuSetting.setSex(1); // 性别（0:女。1:男）
        liuYaoJiChuSetting.setDate("2024-01-01 00:00:00"); // 日期
        liuYaoJiChuSetting.setDateType(0); // 日期类型（0:公历。1:农历）
        liuYaoJiChuSetting.setLeapMonthType(0); // 闰月类型，日期类型为1时生效（0:不使用闰月。1:使用闰月）
        liuYaoJiChuSetting.setJieQiType(1); //  节气类型（0:按天计算。1:按分钟计算）
        liuYaoJiChuSetting.setPaiPanType(0); // 排盘类型（0:日期。1:自动。2:手动）
        liuYaoJiChuSetting.setLiuYao(0); // 上爻，排盘类型为2时生效（0:—（2正1背） 1:- -（1正2背） 2:— ○（0正3背） 3:- - ×（3正0背））
        liuYaoJiChuSetting.setWuYao(0); // 五爻，排盘类型为2时生效（ 0:—（2正1背） 1:- -（1正2背） 2:— ○（0正3背） 3:- - ×（3正0背））
        liuYaoJiChuSetting.setSiYao(0); // 四爻，排盘类型为2时生效（ 0:—（2正1背） 1:- -（1正2背） 2:— ○（0正3背） 3:- - ×（3正0背））
        liuYaoJiChuSetting.setSanYao(0); // 三爻，排盘类型为2时生效（ 0:—（2正1背） 1:- -（1正2背） 2:— ○（0正3背） 3:- - ×（3正0背））
        liuYaoJiChuSetting.setErYao(0); // 二爻，排盘类型为2时生效（ 0:—（2正1背） 1:- -（1正2背） 2:— ○（0正3背） 3:- - ×（3正0背））
        liuYaoJiChuSetting.setYiYao(0); // 初爻，排盘类型为2时生效（ 0:—（2正1背） 1:- -（1正2背） 2:— ○（0正3背） 3:- - ×（3正0背））
        liuYaoJiChuSetting.setYearGanZhiType(2); // 年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接的时刻作为新年的开始）
        liuYaoJiChuSetting.setMonthGanZhiType(1); // 月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
        liuYaoJiChuSetting.setDayGanZhiType(0); // 日干支类型（0:晚子时日干支算当天。1:晚子时日干支算明天）


        // 2、神煞设置（可选）
        LiuYaoShenShaSetting liuYaoShenShaSetting = new LiuYaoShenShaSetting();
//        liuYaoShenShaSetting.setTaiJiGuiRen(0); // 太极贵人（0:显示。1:关闭）
//        liuYaoShenShaSetting.setTianYiGuiRen(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setFuXingGuiRen(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setWenChangGuiRen(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setTianChuGuiRen(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setYueDeGuiRen(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setTianDeGuiRen(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setTangFuGuoYin(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setTianYuanLu(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setHuaGai(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setYiMa(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setTianMa(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setLuMa(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setJieSha(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setJiangXing(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setXianChi(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setTianXi(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setZaiSha(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setTianYi(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setMouXing(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setHuangEn(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setYangRen(0); // （0:显示。1:关闭）
//        liuYaoShenShaSetting.setFeiRen(0); // （0:显示。1:关闭）


        // 3、初始化
        LiuYao liuYao = new LiuYao(liuYaoJiChuSetting); // 使用基础设置初始化
        liuYao.liuYaoShenShaSetting(liuYaoShenShaSetting); // 神煞设置


        // 4、数据
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ ☯ 六爻 ☯ ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐");
        System.out.println("⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐\n");

        System.out.println("公历日期（Solar型）：" + liuYao.getSolar());
        System.out.println("农历日期（Lunar型）：" + liuYao.getLunar());
        System.out.println("公历日期（String型）：" + liuYao.getSolarStr());
        System.out.println("农历日期（String型）：" + liuYao.getLunarStr());
        System.out.println("公历日期（String型）：" + liuYao.getSolarStr2());
        System.out.println("农历日期（String型）：" + liuYao.getLunarStr2());
        System.out.println("公历日期（Date型）：" + liuYao.getSolarDate());
        System.out.println("农历日期（Date型）：" + liuYao.getLunarDate());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("姓名：" + liuYao.getName());
        System.out.println("占事：" + liuYao.getOccupy());
        System.out.println("性别：" + liuYao.getSex());
        System.out.println("年龄：" + liuYao.getAge());
        System.out.println("造：" + liuYao.getZao());
        System.out.println("星期：" + liuYao.getXingQi());
        System.out.println("季节：" + liuYao.getJiJie());
        System.out.println("生肖：" + liuYao.getShengXiao());
        System.out.println("星座：" + liuYao.getXingZuo());
        System.out.println("五不遇时：" + liuYao.getWuBuYuShi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干：" + liuYao.getYearGan());
        System.out.println("月干：" + liuYao.getMonthGan());
        System.out.println("日干：" + liuYao.getDayGan());
        System.out.println("时干：" + liuYao.getHourGan());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支：" + liuYao.getYearZhi());
        System.out.println("月支：" + liuYao.getMonthZhi());
        System.out.println("日支：" + liuYao.getDayZhi());
        System.out.println("时支：" + liuYao.getHourZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支：" + liuYao.getYearGanZhi());
        System.out.println("月干支：" + liuYao.getMonthGanZhi());
        System.out.println("日干支：" + liuYao.getDayGanZhi());
        System.out.println("时干支：" + liuYao.getHourGanZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干五行：" + liuYao.getYearGanWuXing());
        System.out.println("月干五行：" + liuYao.getMonthGanWuXing());
        System.out.println("日干五行：" + liuYao.getDayGanWuXing());
        System.out.println("时干五行：" + liuYao.getHourGanWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年支五行：" + liuYao.getYearZhiWuXing());
        System.out.println("月支五行：" + liuYao.getMonthZhiWuXing());
        System.out.println("日支五行：" + liuYao.getDayZhiWuXing());
        System.out.println("时支五行：" + liuYao.getHourZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支五行：" + liuYao.getYearGanZhiWuXing());
        System.out.println("月干支五行：" + liuYao.getMonthGanZhiWuXing());
        System.out.println("日干支五行：" + liuYao.getDayGanZhiWuXing());
        System.out.println("时干支五行：" + liuYao.getHourGanZhiWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支纳音：" + liuYao.getYearGanZhiNaYin());
        System.out.println("月干支纳音：" + liuYao.getMonthGanZhiNaYin());
        System.out.println("日干支纳音：" + liuYao.getDayGanZhiNaYin());
        System.out.println("时干支纳音：" + liuYao.getHourGanZhiNaYin());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("年干支空亡：" + liuYao.getYearGanZhiKongWang());
        System.out.println("月干支空亡：" + liuYao.getMonthGanZhiKongWang());
        System.out.println("日干支空亡：" + liuYao.getDayGanZhiKongWang());
        System.out.println("时干支空亡：" + liuYao.getHourGanZhiKongWang());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一节：" + liuYao.getPrevJie());
        System.out.println("上一节日期：" + liuYao.getPrevJieDateStr());
        System.out.println("距上一节天数：" + liuYao.getPrevJieDay());
        System.out.println();
        System.out.println("下一节：" + liuYao.getNextJie());
        System.out.println("下一节日期：" + liuYao.getNextJieDateStr());
        System.out.println("距下一节天数：" + liuYao.getNextJieDay());
        System.out.println();
        System.out.println("出生节：" + liuYao.getChuShengJie());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上一气：" + liuYao.getPrevQi());
        System.out.println("上一气日期：" + liuYao.getPrevQiDateStr());
        System.out.println("距上一气天数：" + liuYao.getPrevQiDay());
        System.out.println();
        System.out.println("下一气：" + liuYao.getNextQi());
        System.out.println("下一气日期：" + liuYao.getNextQiDateStr());
        System.out.println("距下一气天数：" + liuYao.getNextQiDay());
        System.out.println();
        System.out.println("出生气：" + liuYao.getChuShengQi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("月相：" + liuYao.getYueXiang());
        System.out.println("月将：" + liuYao.getYueJiang());
        System.out.println("月将神：" + liuYao.getYueJiangShen());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("神煞：" + liuYao.getShenSha());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上卦卦名：" + liuYao.getShangGuaName());
        System.out.println("下卦卦名：" + liuYao.getXiaGuaName());
        System.out.println("本卦卦名：" + liuYao.getBenGuaName());
        System.out.println("变卦卦名：" + liuYao.getBianGuaName());
        System.out.println("互卦卦名：" + liuYao.getHuGuaName());
        System.out.println("错卦卦名：" + liuYao.getCuoGuaName());
        System.out.println("综卦卦名：" + liuYao.getZongGuaName());
        System.out.println("伏卦卦名：" + liuYao.getFuGuaName());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("上卦卦象：" + liuYao.getShangGuaAs());
        System.out.println("下卦卦象：" + liuYao.getXiaGuaAs());
        System.out.println("本卦卦象：" + liuYao.getBenGuaAs());
        System.out.println("变卦卦象：" + liuYao.getBianGuaAs());
        System.out.println("互卦卦象：" + liuYao.getHuGuaAs());
        System.out.println("错卦卦象：" + liuYao.getCuoGuaAs());
        System.out.println("综卦卦象：" + liuYao.getZongGuaAs());
        System.out.println("伏卦卦象：" + liuYao.getFuGuaAs());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦类型：" + liuYao.getBenGuaType());
        System.out.println("变卦类型：" + liuYao.getBianGuaType());
        System.out.println("互卦类型：" + liuYao.getHuGuaType());
        System.out.println("错卦类型：" + liuYao.getCuoGuaType());
        System.out.println("综卦类型：" + liuYao.getZongGuaType());
        System.out.println("伏卦类型：" + liuYao.getFuGuaType());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦卦身：" + liuYao.getBenGuaGuaShen());
        System.out.println("变卦卦身：" + liuYao.getBianGuaGuaShen());
        System.out.println("互卦卦身：" + liuYao.getHuGuaGuaShen());
        System.out.println("错卦卦身：" + liuYao.getCuoGuaGuaShen());
        System.out.println("综卦卦身：" + liuYao.getZongGuaGuaShen());
        System.out.println("伏卦卦身：" + liuYao.getFuGuaGuaShen());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦卦辞：" + liuYao.getBenGuaGuaCi());
        System.out.println("变卦卦辞：" + liuYao.getBianGuaGuaCi());
        System.out.println("互卦卦辞：" + liuYao.getHuGuaGuaCi());
        System.out.println("错卦卦辞：" + liuYao.getCuoGuaGuaCi());
        System.out.println("综卦卦辞：" + liuYao.getZongGuaGuaCi());
        System.out.println("伏卦卦辞：" + liuYao.getFuGuaGuaCi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻爻名：" + liuYao.getBenGuaLiuYaoName());
        System.out.println("变卦六爻爻名：" + liuYao.getBianGuaLiuYaoName());
        System.out.println("互卦六爻爻名：" + liuYao.getHuGuaLiuYaoName());
        System.out.println("错卦六爻爻名：" + liuYao.getCuoGuaLiuYaoName());
        System.out.println("综卦六爻爻名：" + liuYao.getZongGuaLiuYaoName());
        System.out.println("伏卦六爻爻名：" + liuYao.getFuGuaLiuYaoName());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻爻象：" + liuYao.getBenGuaLiuYaoAs());
        System.out.println("变卦六爻爻象：" + liuYao.getBianGuaLiuYaoAs());
        System.out.println("互卦六爻爻象：" + liuYao.getHuGuaLiuYaoAs());
        System.out.println("错卦六爻爻象：" + liuYao.getCuoGuaLiuYaoAs());
        System.out.println("综卦六爻爻象：" + liuYao.getZongGuaLiuYaoAs());
        System.out.println("伏卦六爻爻象：" + liuYao.getFuGuaLiuYaoAs());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻世应：" + liuYao.getBenGuaLiuYaoShiYing());
        System.out.println("变卦六爻世应：" + liuYao.getBianGuaLiuYaoShiYing());
        System.out.println("互卦六爻世应：" + liuYao.getHuGuaLiuYaoShiYing());
        System.out.println("错卦六爻世应：" + liuYao.getCuoGuaLiuYaoShiYing());
        System.out.println("综卦六爻世应：" + liuYao.getZongGuaLiuYaoShiYing());
        System.out.println("伏卦六爻世应：" + liuYao.getFuGuaLiuYaoShiYing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻六亲：" + liuYao.getBenGuaLiuYaoLiuQin());
        System.out.println("变卦六爻六亲：" + liuYao.getBianGuaLiuYaoLiuQin());
        System.out.println("互卦六爻六亲：" + liuYao.getHuGuaLiuYaoLiuQin());
        System.out.println("错卦六爻六亲：" + liuYao.getCuoGuaLiuYaoLiuQin());
        System.out.println("综卦六爻六亲：" + liuYao.getZongGuaLiuYaoLiuQin());
        System.out.println("伏卦六爻六亲：" + liuYao.getFuGuaLiuYaoLiuQin());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻干支：" + liuYao.getBenGuaLiuYaoGanZhi());
        System.out.println("变卦六爻干支：" + liuYao.getBianGuaLiuYaoGanZhi());
        System.out.println("互卦六爻干支：" + liuYao.getHuGuaLiuYaoGanZhi());
        System.out.println("错卦六爻干支：" + liuYao.getCuoGuaLiuYaoGanZhi());
        System.out.println("综卦六爻干支：" + liuYao.getZongGuaLiuYaoGanZhi());
        System.out.println("伏卦六爻干支：" + liuYao.getFuGuaLiuYaoGanZhi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻五行：" + liuYao.getBenGuaLiuYaoWuXing());
        System.out.println("变卦六爻五行：" + liuYao.getBianGuaLiuYaoWuXing());
        System.out.println("互卦六爻五行：" + liuYao.getHuGuaLiuYaoWuXing());
        System.out.println("错卦六爻五行：" + liuYao.getCuoGuaLiuYaoWuXing());
        System.out.println("综卦六爻五行：" + liuYao.getZongGuaLiuYaoWuXing());
        System.out.println("伏卦六爻五行：" + liuYao.getFuGuaLiuYaoWuXing());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻六神：" + liuYao.getBenGuaLiuYaoLiuShen());
        System.out.println("变卦六爻六神：" + liuYao.getBianGuaLiuYaoLiuShen());
        System.out.println("互卦六爻六神：" + liuYao.getHuGuaLiuYaoLiuShen());
        System.out.println("错卦六爻六神：" + liuYao.getCuoGuaLiuYaoLiuShen());
        System.out.println("综卦六爻六神：" + liuYao.getZongGuaLiuYaoLiuShen());
        System.out.println("伏卦六爻六神：" + liuYao.getFuGuaLiuYaoLiuShen());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻爻辞：" + liuYao.getBenGuaLiuYaoYaoCi());
        System.out.println("变卦六爻爻辞：" + liuYao.getBianGuaLiuYaoYaoCi());
        System.out.println("互卦六爻爻辞：" + liuYao.getHuGuaLiuYaoYaoCi());
        System.out.println("错卦六爻爻辞：" + liuYao.getCuoGuaLiuYaoYaoCi());
        System.out.println("综卦六爻爻辞：" + liuYao.getZongGuaLiuYaoYaoCi());
        System.out.println("伏卦六爻爻辞：" + liuYao.getFuGuaLiuYaoYaoCi());

        System.out.println("\n--------------------------------------------------------------------------------------------------------------\n");

        System.out.println("本卦六爻纳音：" + liuYao.getBenGuaLiuYaoNaYin());
        System.out.println("变卦六爻纳音：" + liuYao.getBianGuaLiuYaoNaYin());
        System.out.println("互卦六爻纳音：" + liuYao.getHuGuaLiuYaoNaYin());
        System.out.println("错卦六爻纳音：" + liuYao.getCuoGuaLiuYaoNaYin());
        System.out.println("综卦六爻纳音：" + liuYao.getZongGuaLiuYaoNaYin());
        System.out.println("伏卦六爻纳音：" + liuYao.getFuGuaLiuYaoNaYin());
        System.out.println("伏卦六爻伏神：" + liuYao.getFuGuaLiuYaoFuShen());

    }


}
