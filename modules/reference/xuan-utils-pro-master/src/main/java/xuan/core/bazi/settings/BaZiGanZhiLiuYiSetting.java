package xuan.core.bazi.settings;

import lombok.Data;

/**
 * 八字 - 干支留意设置
 *
 * @author 善待
 */
@Data
public class BaZiGanZhiLiuYiSetting {

    /**
     * 天干相生（0:显示。1:关闭）
     */
    private int tianGanXiangSheng;

    /**
     * 天干相克（0:显示。1:关闭）
     */
    private int tianGanXiangKe;

    /**
     * 天干相合（0:显示。1:关闭）
     */
    private int tianGanXiangHe;

    /**
     * 天干相冲（0:显示。1:关闭）
     */
    private int tianGanXiangChong;


    /**
     * 天干相生类型（0:以任意两干计算。1:以相邻两干计算）
     */
    private int tianGanXiangShengType;

    /**
     * 天干相克类型（0:以任意两干计算。1:以相邻两干计算）
     */
    private int tianGanXiangKeType;

    /**
     * 天干相合类型（0:以任意两干计算。1:以相邻两干计算）
     */
    private int tianGanXiangHeType;

    /**
     * 天干相冲类型（0:以任意两干计算。1:以相邻两干计算）
     */
    private int tianGanXiangChongType;


    /**
     * 天干相生：甲丙相生（0:显示。1:关闭）
     */
    private int jiaBingXiangSheng;

    /**
     * 天干相生：甲丁相生（0:显示。1:关闭）
     */
    private int jiaDingXiangSheng;

    /**
     * 天干相生：乙丙相生（0:显示。1:关闭）
     */
    private int yiBingXiangSheng;

    /**
     * 天干相生：乙丁相生（0:显示。1:关闭）
     */
    private int yiDingXiangSheng;

    /**
     * 天干相生：丙戊相生（0:显示。1:关闭）
     */
    private int bingWuXiangSheng;

    /**
     * 天干相生：丙己相生（0:显示。1:关闭）
     */
    private int bingJiXiangSheng;

    /**
     * 天干相生：丁戊相生（0:显示。1:关闭）
     */
    private int dingWuXiangSheng;

    /**
     * 天干相生：丁己相生（0:显示。1:关闭）
     */
    private int dingJiXiangSheng;

    /**
     * 天干相生：戊庚相生（0:显示。1:关闭）
     */
    private int wuGengXiangSheng;

    /**
     * 天干相生：戊辛相生（0:显示。1:关闭）
     */
    private int wuXinXiangSheng;

    /**
     * 天干相生：己庚相生（0:显示。1:关闭）
     */
    private int jiGengXiangSheng;

    /**
     * 天干相生：己辛相生（0:显示。1:关闭）
     */
    private int jiXinXiangSheng;

    /**
     * 天干相生：庚壬相生（0:显示。1:关闭）
     */
    private int gengRenXiangSheng;

    /**
     * 天干相生：庚癸相生（0:显示。1:关闭）
     */
    private int gengGuiXiangSheng;

    /**
     * 天干相生：辛壬相生（0:显示。1:关闭）
     */
    private int xinRenXiangSheng;

    /**
     * 天干相生：辛癸相生（0:显示。1:关闭）
     */
    private int xinGuiXiangSheng;

    /**
     * 天干相生：壬甲相生（0:显示。1:关闭）
     */
    private int renJiaXiangSheng;

    /**
     * 天干相生：壬乙相生（0:显示。1:关闭）
     */
    private int renYiXiangSheng;

    /**
     * 天干相生：癸甲相生（0:显示。1:关闭）
     */
    private int guiJiaXiangSheng;

    /**
     * 天干相生：癸乙相生（0:显示。1:关闭）
     */
    private int guiYiXiangSheng;


    /**
     * 天干相合：甲己相合（0:显示。1:关闭）
     */
    private int jiaJiXiangHe;

    /**
     * 天干相合：乙庚相合（0:显示。1:关闭）
     */
    private int yiGengXiangHe;

    /**
     * 天干相合：丙辛相合（0:显示。1:关闭）
     */
    private int bingXinXiangHe;

    /**
     * 天干相合：丁壬相合（0:显示。1:关闭）
     */
    private int dingRenXiangHe;

    /**
     * 天干相合：戊癸相合（0:显示。1:关闭）
     */
    private int wuGuiXiangHe;


    /**
     * 天干相冲：甲庚相冲（0:显示。1:关闭）
     */
    private int jiaGengXiangChong;

    /**
     * 天干相冲：乙辛相冲（0:显示。1:关闭）
     */
    private int yiXinXiangChong;

    /**
     * 天干相冲：丙壬相冲（0:显示。1:关闭）
     */
    private int bingRenXiangChong;

    /**
     * 天干相冲：丁癸相冲（0:显示。1:关闭）
     */
    private int dingGuiXiangChong;


    /**
     * 天干相克：甲戊相克（0:显示。1:关闭）
     */
    private int jiaWuXiangKe;

    /**
     * 天干相克：乙己相克（0:显示。1:关闭）
     */
    private int yiJiXiangKe;

    /**
     * 天干相克：丙庚相克（0:显示。1:关闭）
     */
    private int bingGengXiangKe;

    /**
     * 天干相克：丁辛相克（0:显示。1:关闭）
     */
    private int dingXinXiangKe;

    /**
     * 天干相克：戊壬相克（0:显示。1:关闭）
     */
    private int wuRenXiangKe;

    /**
     * 天干相克：己癸相克（0:显示。1:关闭）
     */
    private int jiGuiXiangKe;

    /**
     * 天干相克：庚甲相克（0:显示。1:关闭）
     */
    private int gengJiaXiangKe;

    /**
     * 天干相克：辛乙相克（0:显示。1:关闭）
     */
    private int xinYiXiangKe;

    /**
     * 天干相克：壬丙相克（0:显示。1:关闭）
     */
    private int renBingXiangKe;

    /**
     * 天干相克：癸丁相克（0:显示。1:关闭）
     */
    private int guiDingXiangKe;


    /**
     * 地支半合（0:显示。1:关闭）
     */
    private int diZhiBanHe;

    /**
     * 地支拱合（0:显示。1:关闭）
     */
    private int diZhiGongHe;

    /**
     * 地支暗合（0:显示。1:关闭）
     */
    private int diZhiAnHe;

    /**
     * 地支六合（0:显示。1:关闭）
     */
    private int diZhiLiuHe;

    /**
     * 地支相刑（0:显示。1:关闭）
     */
    private int diZhiXiangXing;

    /**
     * 地支相冲（0:显示。1:关闭）
     */
    private int diZhiXiangChong;

    /**
     * 地支相破（0:显示。1:关闭）
     */
    private int diZhiXiangPo;

    /**
     * 地支相害（0:显示。1:关闭）
     */
    private int diZhiXiangHai;


    /**
     * 地支半合类型（0:以任意两支计算。1:以相邻两支计算）
     */
    private int diZhiBanHeType;

    /**
     * 地支拱合类型（0:以任意两支计算。1:以相邻两支计算）
     */
    private int diZhiGongHeType;

    /**
     * 地支暗合类型（0:以任意两支计算。1:以相邻两支计算）
     */
    private int diZhiAnHeType;

    /**
     * 地支六合类型（0:以任意两支计算。1:以相邻两支计算）
     */
    private int diZhiLiuHeType;

    /**
     * 地支相刑类型（0:以任意两支计算。1:以相邻两支计算）
     */
    private int diZhiXiangXingType;

    /**
     * 地支相冲类型（0:以任意两支计算。1:以相邻两支计算）
     */
    private int diZhiXiangChongType;

    /**
     * 地支相破位置（0:以任意两支计算。1:以相邻两支计算）
     */
    private int diZhiXiangPoType;

    /**
     * 地支相害类型（0:以任意两支计算。1:以相邻两支计算）
     */
    private int diZhiXiangHaiType;


    /**
     * 地支半合：寅午半合（0:显示。1:关闭）
     */
    private int yinWuBanHe;

    /**
     * 地支半合：申子半合（0:显示。1:关闭）
     */
    private int shenZiBanHe;

    /**
     * 地支半合：巳酉半合（0:显示。1:关闭）
     */
    private int siYouBanHe;

    /**
     * 地支半合：亥卯半合（0:显示。1:关闭）
     */
    private int haiMaoBanHe;

    /**
     * 地支半合：子辰半合（0:显示。1:关闭）
     */
    private int ziChenBanHe;

    /**
     * 地支半合：午戌半合（0:显示。1:关闭）
     */
    private int wuXuBanHe;

    /**
     * 地支半合：卯未半合（0:显示。1:关闭）
     */
    private int maoWeiBanHe;

    /**
     * 地支半合：酉丑半合（0:显示。1:关闭）
     */
    private int youChouBanHe;


    /**
     * 地支拱合：申辰拱合（0:显示。1:关闭）
     */
    private int shenChenGongHe;

    /**
     * 地支拱合：亥未拱合（0:显示。1:关闭）
     */
    private int haiWeiGongHe;

    /**
     * 地支拱合：寅戌拱合 （0:显示。1:关闭）
     */
    private int yinXuGongHe;

    /**
     * 地支拱合：巳丑拱合（0:显示。1:关闭）
     */
    private int siChouGongHe;


    /**
     * 地支暗合：卯申暗合（0:显示。1:关闭）
     */
    private int maoShenAnHe;

    /**
     * 地支暗合：午亥暗合（0:显示。1:关闭）
     */
    private int wuHaiAnHe;

    /**
     * 地支暗合：丑寅暗合（0:显示。1:关闭）
     */
    private int chouYinAnHe;

    /**
     * 地支暗合：寅未暗合（0:显示。1:关闭）
     */
    private int yinWeiAnHe;

    /**
     * 地支暗合：寅午暗合（0:显示。1:关闭）
     */
    private int yinWuAnHe;

    /**
     * 地支暗合：子戌暗合（0:显示。1:关闭）
     */
    private int ziXuAnHe;

    /**
     * 地支暗合：子辰暗合（0:显示。1:关闭）
     */
    private int ziChenAnHe;

    /**
     * 地支暗合：子巳暗合（0:显示。1:关闭）
     */
    private int ziSiAnHe;

    /**
     * 地支暗合：巳酉暗合（0:显示。1:关闭）
     */
    private int siYouAnHe;


    /**
     * 地支六合：子丑六合（0:显示。1:关闭）
     */
    private int ziChouLiuHe;

    /**
     * 地支六合：寅亥六合（0:显示。1:关闭）
     */
    private int yinHaiLiuHe;

    /**
     * 地支六合：卯戌六合（0:显示。1:关闭）
     */
    private int maoXuLiuHe;

    /**
     * 地支六合：辰酉六合（0:显示。1:关闭）
     */
    private int chenYouLiuHe;

    /**
     * 地支六合：巳申六合（0:显示。1:关闭）
     */
    private int siShenLiuHe;

    /**
     * 地支六合：午未六合（0:显示。1:关闭）
     */
    private int wuWeiLiuHe;


    /**
     * 地支相刑：寅巳相刑（0:显示。1:关闭）
     */
    private int yinSiXiangXing;

    /**
     * 地支相刑：巳申相刑（0:显示。1:关闭）
     */
    private int siShenXiangXing;

    /**
     * 地支相刑：申寅相刑（0:显示。1:关闭）
     */
    private int shenYinXiangXing;

    /**
     * 地支相刑：丑戌相刑（0:显示。1:关闭）
     */
    private int chouXuXiangXing;

    /**
     * 地支相刑：戌未相刑（0:显示。1:关闭）
     */
    private int xuWeiXiangXing;

    /**
     * 地支相刑：未丑相刑（0:显示。1:关闭）
     */
    private int weiChouXiangXing;

    /**
     * 地支相刑：子卯相刑（0:显示。1:关闭）
     */
    private int ziMaoXiangXing;

    /**
     * 地支相刑：酉酉自刑（0:显示。1:关闭）
     */
    private int youYouXiangXing;

    /**
     * 地支相刑：亥亥自刑（0:显示。1:关闭）
     */
    private int haiHaiXiangXing;

    /**
     * 地支相刑：午午自刑（0:显示。1:关闭）
     */
    private int wuWuXiangXing;

    /**
     * 地支相刑：辰辰自刑（0:显示。1:关闭）
     */
    private int chenChenXiangXing;


    /**
     * 地支相冲：子午相冲（0:显示。1:关闭）
     */
    private int ziWuXiangChong;

    /**
     * 地支相冲：丑未相冲（0:显示。1:关闭）
     */
    private int chouWeiXiangChong;

    /**
     * 地支相冲：寅申相冲（0:显示。1:关闭）
     */
    private int yinShenXiangChong;

    /**
     * 地支相冲：卯酉相冲（0:显示。1:关闭）
     */
    private int maoYouXiangChong;

    /**
     * 地支相冲：辰戌相冲（0:显示。1:关闭）
     */
    private int chenXuXiangChong;

    /**
     * 地支相冲：巳亥相冲（0:显示。1:关闭）
     */
    private int siHaiXiangChong;


    /**
     * 地支相破：子酉相破（0:显示。1:关闭）
     */
    private int ziYouXiangPo;

    /**
     * 地支相破：寅亥相破（0:显示。1:关闭）
     */
    private int yinHaiXiangPo;

    /**
     * 地支相破：卯午相破（0:显示。1:关闭）
     */
    private int maoWuXiangPo;

    /**
     * 地支相破：辰丑相破（0:显示。1:关闭）
     */
    private int chenChouXiangPo;

    /**
     * 地支相破：巳申相破（0:显示。1:关闭）
     */
    private int siShenXiangPo;

    /**
     * 地支相破：戌未相破（0:显示。1:关闭）
     */
    private int xuWeiXiangPo;


    /**
     * 地支相害：子未相害（0:显示。1:关闭）
     */
    private int ziWeiXiangHai;

    /**
     * 地支相害：丑午相害（0:显示。1:关闭）
     */
    private int chouWuXiangHai;

    /**
     * 地支相害：寅巳相害（0:显示。1:关闭）
     */
    private int yinSiXiangHai;

    /**
     * 地支相害：卯辰相害（0:显示。1:关闭）
     */
    private int maoChenXiangHai;

    /**
     * 地支相害：申亥相害（0:显示。1:关闭）
     */
    private int shenHaiXiangHai;

    /**
     * 地支相害：酉戌相害（0:显示。1:关闭）
     */
    private int youXuXiangHai;

//*******************************************************************************************************************************

    /**
     * 初始化设置
     */
    public BaZiGanZhiLiuYiSetting() {

        this.tianGanXiangSheng = 0; // 天干相生（默认→ 显示）
        this.tianGanXiangKe = 0; // 天干相克（默认→ 显示）
        this.tianGanXiangHe = 0; // 天干相合（默认→ 显示）
        this.tianGanXiangChong = 0; // 天干相冲（默认→ 显示）

        this.tianGanXiangShengType = 0; // 天干相生类型（默认→ 以任意两干计算）
        this.tianGanXiangKeType = 0; // 天干相克类型（默认→ 以任意两干计算）
        this.tianGanXiangHeType = 0; // 天干相合类型（默认→ 以任意两干计算）
        this.tianGanXiangChongType = 0; // 天干相冲类型（默认→ 以任意两干计算）

        this.jiaBingXiangSheng = 0; // 天干相生：甲丙相生（默认→ 显示）
        this.jiaDingXiangSheng = 0; // 天干相生：甲丁相生（默认→ 显示）
        this.yiBingXiangSheng = 0; // 天干相生：乙丙相生（默认→ 显示）
        this.yiDingXiangSheng = 0; // 天干相生：乙丁相生（默认→ 显示）
        this.bingWuXiangSheng = 0; // 天干相生：丙戊相生（默认→ 显示）
        this.bingJiXiangSheng = 0; // 天干相生：丙己相生（默认→ 显示）
        this.dingWuXiangSheng = 0; // 天干相生：丁戊相生（默认→ 显示）
        this.dingJiXiangSheng = 0; // 天干相生：丁己相生（默认→ 显示）
        this.wuGengXiangSheng = 0; // 天干相生：戊庚相生（默认→ 显示）
        this.wuXinXiangSheng = 0; // 天干相生：戊辛相生（默认→ 显示）
        this.jiGengXiangSheng = 0; // 天干相生：己庚相生（默认→ 显示）
        this.jiXinXiangSheng = 0; // 天干相生：己辛相生（默认→ 显示）
        this.gengRenXiangSheng = 0; // 天干相生：庚壬相生（默认→ 显示）
        this.gengGuiXiangSheng = 0; // 天干相生：庚癸相生（默认→ 显示）
        this.xinRenXiangSheng = 0; // 天干相生：辛壬相生（默认→ 显示）
        this.xinGuiXiangSheng = 0; // 天干相生：辛癸相生（默认→ 显示）
        this.renJiaXiangSheng = 0; // 天干相生：壬甲相生（默认→ 显示）
        this.renYiXiangSheng = 0; // 天干相生：壬乙相生（默认→ 显示）
        this.guiJiaXiangSheng = 0; // 天干相生：癸甲相生（默认→ 显示）
        this.guiYiXiangSheng = 0; // 天干相生：癸乙相生（默认→ 显示）

        this.jiaJiXiangHe = 0; // 天干相合：甲己相合（默认→ 显示）
        this.yiGengXiangHe = 0; // 天干相合：乙庚相合（默认→ 显示）
        this.bingXinXiangHe = 0; // 天干相合：丙辛相合（默认→ 显示）
        this.dingRenXiangHe = 0; // 天干相合：丁壬相合（默认→ 显示）
        this.wuGuiXiangHe = 0; // 天干相合：戊癸相合（默认→ 显示）

        this.jiaGengXiangChong = 0; // 天干相冲：甲庚相冲（默认→ 显示）
        this.yiXinXiangChong = 0; // 天干相冲：乙辛相冲（默认→ 显示）
        this.bingRenXiangChong = 0; // 天干相冲：丙壬相冲（默认→ 显示）
        this.dingGuiXiangChong = 0; // 天干相冲：丁癸相冲（默认→ 显示）

        this.jiaWuXiangKe = 0; // 天干相克：甲戊相克（默认→ 显示）
        this.yiJiXiangKe = 0; // 天干相克：乙己相克（默认→ 显示）
        this.bingGengXiangKe = 0; // 天干相克：丙庚相克（默认→ 显示）
        this.dingXinXiangKe = 0; // 天干相克：丁辛相克（默认→ 显示）
        this.wuRenXiangKe = 0; // 天干相克：戊壬相克（默认→ 显示）
        this.jiGuiXiangKe = 0; // 天干相克：己癸相克（默认→ 显示）
        this.gengJiaXiangKe = 0; // 天干相克：庚甲相克（默认→ 显示）
        this.xinYiXiangKe = 0; // 天干相克：辛乙相克（默认→ 显示）
        this.renBingXiangKe = 0; // 天干相克：壬丙相克（默认→ 显示）
        this.guiDingXiangKe = 0; // 天干相克：癸丁相克（默认→ 显示）


        this.diZhiBanHe = 0; // 地支半合（默认→ 显示）
        this.diZhiGongHe = 0; // 地支拱合（默认→ 显示）
        this.diZhiAnHe = 0; // 地支暗合（默认→ 显示）
        this.diZhiLiuHe = 0; // 地支六合（默认→ 显示）
        this.diZhiXiangXing = 0; // 地支相刑（默认→ 显示）
        this.diZhiXiangChong = 0; // 地支相冲（默认→ 显示）
        this.diZhiXiangPo = 0; // 地支相破（默认→ 显示）
        this.diZhiXiangHai = 0; // 地支相害（默认→ 显示）

        this.diZhiBanHeType = 0; // 地支半合类型（默认→ 以任意两支计算）
        this.diZhiGongHeType = 0; // 地支拱合类型（默认→ 以任意两支计算）
        this.diZhiAnHeType = 0; // 地支暗合类型（默认→ 以任意两支计算）
        this.diZhiLiuHeType = 0; // 地支六合类型（默认→ 以任意两支计算）
        this.diZhiXiangXingType = 0; // 地支相刑类型（默认→ 以任意两支计算）
        this.diZhiXiangChongType = 0; // 地支相冲类型（默认→ 以任意两支计算）
        this.diZhiXiangPoType = 0; // 地支相破类型（默认→ 以任意两支计算）
        this.diZhiXiangHaiType = 0; // 地支相害类型（默认→ 以任意两支计算）

        this.yinWuBanHe = 0; // 地支半合：寅午半合（默认→ 显示）
        this.shenZiBanHe = 0; // 地支半合：申子半合（默认→ 显示）
        this.siYouBanHe = 0; // 地支半合：巳酉半合（默认→ 显示）
        this.haiMaoBanHe = 0; // 地支半合：亥卯半合（默认→ 显示）
        this.ziChenBanHe = 0; // 地支半合：子辰半合（默认→ 显示）
        this.wuXuBanHe = 0; // 地支半合：午戌半合（默认→ 显示）
        this.maoWeiBanHe = 0; // 地支半合：卯未半合（默认→ 显示）
        this.youChouBanHe = 0; // 地支半合：酉丑半合（默认→ 显示）

        this.shenChenGongHe = 0; // 地支拱合：申辰拱合（默认→ 显示）
        this.haiWeiGongHe = 0; // 地支拱合：亥未拱合（默认→ 显示）
        this.yinXuGongHe = 0; // 地支拱合：寅戌拱合（默认→ 显示）
        this.siChouGongHe = 0; // 地支拱合：巳丑拱合（默认→ 显示）

        this.maoShenAnHe = 0; // 地支暗合：卯申暗合（默认→ 显示）
        this.wuHaiAnHe = 0; // 地支暗合：午亥暗合（默认→ 显示）
        this.chouYinAnHe = 0; // 地支暗合：丑寅暗合（默认→ 显示）
        this.yinWeiAnHe = 0; // 地支暗合：寅未暗合（默认→ 显示）
        this.yinWuAnHe = 0; // 地支暗合：寅午暗合（默认→ 显示）
        this.ziXuAnHe = 0; // 地支暗合：子戌暗合（默认→ 显示）
        this.ziChenAnHe = 0; // 地支暗合：子辰暗合（默认→ 显示）
        this.ziSiAnHe = 0; // 地支暗合：子巳暗合（默认→ 显示）
        this.siYouAnHe = 0; // 地支暗合：巳酉暗合（默认→ 显示）

        this.ziChouLiuHe = 0; // 地支六合：子丑六合（默认→ 显示）
        this.yinHaiLiuHe = 0; // 地支六合：寅亥六合（默认→ 显示）
        this.maoXuLiuHe = 0; // 地支六合：卯戌六合（默认→ 显示）
        this.chenYouLiuHe = 0; // 地支六合：辰酉六合（默认→ 显示）
        this.siShenLiuHe = 0; // 地支六合：巳申六合（默认→ 显示）
        this.wuWeiLiuHe = 0; // 地支六合：午未六合（默认→ 显示）

        this.yinSiXiangXing = 0; // 地支相刑：寅巳相刑（默认→ 显示）
        this.siShenXiangXing = 0; // 地支相刑：巳申相刑（默认→ 显示）
        this.shenYinXiangXing = 0; // 地支相刑：申寅相刑（默认→ 显示）
        this.chouXuXiangXing = 0; // 地支相刑：丑戌相刑（默认→ 显示）
        this.xuWeiXiangXing = 0; // 地支相刑：戌未相刑（默认→ 显示）
        this.weiChouXiangXing = 0; // 地支相刑：未丑相刑（默认→ 显示）
        this.ziMaoXiangXing = 0; // 地支相刑：子卯相刑（默认→ 显示）
        this.youYouXiangXing = 0; // 地支相刑：酉酉自刑（默认→ 显示）
        this.haiHaiXiangXing = 0; // 地支相刑：亥亥自刑（默认→ 显示）
        this.wuWuXiangXing = 0; // 地支相刑：午午自刑（默认→ 显示）
        this.chenChenXiangXing = 0; // 地支相刑：辰辰自刑（默认→ 显示）

        this.ziWuXiangChong = 0; // 地支相冲：子午相冲（默认→ 显示）
        this.chouWeiXiangChong = 0; // 地支相冲：丑未相冲（默认→ 显示）
        this.yinShenXiangChong = 0; // 地支相冲：寅申相冲（默认→ 显示）
        this.maoYouXiangChong = 0; // 地支相冲：卯酉相冲（默认→ 显示）
        this.chenXuXiangChong = 0; // 地支相冲：辰戌相冲（默认→ 显示）
        this.siHaiXiangChong = 0; // 地支相冲：巳亥相冲（默认→ 显示）

        this.ziYouXiangPo = 0; // 地支相破：子酉相破（默认→ 显示）
        this.yinHaiXiangPo = 0; // 地支相破：寅亥相破（默认→ 显示）
        this.maoWuXiangPo = 0; // 地支相破：卯午相破（默认→ 显示）
        this.chenChouXiangPo = 0; // 地支相破：辰丑相破（默认→ 显示）
        this.siShenXiangPo = 0; // 地支相破：巳申相破（默认→ 显示）
        this.xuWeiXiangPo = 0; // 地支相破：戌未相破（默认→ 显示）

        this.ziWeiXiangHai = 0; // 地支相害：子未相害（默认→ 显示）
        this.chouWuXiangHai = 0; // 地支相害：丑午相害（默认→ 显示）
        this.yinSiXiangHai = 0; // 地支相害：寅巳相害（默认→ 显示）
        this.maoChenXiangHai = 0; // 地支相害：卯辰相害（默认→ 显示）
        this.shenHaiXiangHai = 0; // 地支相害：申亥相害（默认→ 显示）
        this.youXuXiangHai = 0; // 地支相害：酉戌相害（默认→ 显示）

    }

//===============================================================================================================================

    /**
     * 天干相生
     *
     * @param tianGanXiangSheng 天干相生（0:显示。1:关闭）
     */
    public void setTianGanXiangSheng(int tianGanXiangSheng) {
        this.tianGanXiangSheng = (tianGanXiangSheng == 0 || tianGanXiangSheng == 1) ? tianGanXiangSheng : 0;
    }

    /**
     *天干相克
     *
     * @param tianGanXiangKe 天干相克（0:显示。1:关闭）
     */
    public void setTianGanXiangKe(int tianGanXiangKe) {
        this.tianGanXiangKe = (tianGanXiangKe == 0 || tianGanXiangKe == 1) ? tianGanXiangKe : 0;
    }

    /**
     *天干相合
     *
     * @param tianGanXiangHe 天干相合（0:显示。1:关闭）
     */
    public void setTianGanXiangHe(int tianGanXiangHe) {
        this.tianGanXiangHe = (tianGanXiangHe == 0 || tianGanXiangHe == 1) ? tianGanXiangHe : 0;
    }

    /**
     *天干相冲
     *
     * @param tianGanXiangChong 天干相冲（0:显示。1:关闭）
     */
    public void setTianGanXiangChong(int tianGanXiangChong) {
        this.tianGanXiangChong = (tianGanXiangChong == 0 || tianGanXiangChong == 1) ? tianGanXiangChong : 0;
    }

    /**
     *天干相生类型
     *
     * @param tianGanXiangShengType 天干相生类型（0:显示。1:关闭）
     */
    public void setTianGanXiangShengType(int tianGanXiangShengType) {
        this.tianGanXiangShengType = (tianGanXiangShengType == 0 || tianGanXiangShengType == 1) ? tianGanXiangShengType : 0;
    }

    /**
     *天干相克类型
     *
     * @param tianGanXiangKeType 天干相克类型（0:显示。1:关闭）
     */
    public void setTianGanXiangKeType(int tianGanXiangKeType) {
        this.tianGanXiangKeType = (tianGanXiangKeType == 0 || tianGanXiangKeType == 1) ? tianGanXiangKeType : 0;
    }

    /**
     *天干相合类型
     *
     * @param tianGanXiangHeType 天干相合类型（0:显示。1:关闭）
     */
    public void setTianGanXiangHeType(int tianGanXiangHeType) {
        this.tianGanXiangHeType = (tianGanXiangHeType == 0 || tianGanXiangHeType == 1) ? tianGanXiangHeType : 0;
    }

    /**
     *天干相冲类型
     *
     * @param tianGanXiangChongType 天干相冲类型（0:显示。1:关闭）
     */
    public void setTianGanXiangChongType(int tianGanXiangChongType) {
        this.tianGanXiangChongType = (tianGanXiangChongType == 0 || tianGanXiangChongType == 1) ? tianGanXiangChongType : 0;
    }

    /**
     *天干相生：甲丙相生
     *
     * @param jiaBingXiangSheng 天干相生：甲丙相生（0:显示。1:关闭）
     */
    public void setJiaBingXiangSheng(int jiaBingXiangSheng) {
        this.jiaBingXiangSheng = (jiaBingXiangSheng == 0 || jiaBingXiangSheng == 1) ? jiaBingXiangSheng : 0;
    }

    /**
     *天干相生：甲丁相生
     *
     * @param jiaDingXiangSheng 天干相生：甲丁相生（0:显示。1:关闭）
     */
    public void setJiaDingXiangSheng(int jiaDingXiangSheng) {
        this.jiaDingXiangSheng = (jiaDingXiangSheng == 0 || jiaDingXiangSheng == 1) ? jiaDingXiangSheng : 0;
    }

    /**
     *天干相生：乙丙相生
     *
     * @param yiBingXiangSheng 天干相生：乙丙相生（0:显示。1:关闭）
     */
    public void setYiBingXiangSheng(int yiBingXiangSheng) {
        this.yiBingXiangSheng = (yiBingXiangSheng == 0 || yiBingXiangSheng  == 1) ? yiBingXiangSheng : 0;
    }

    /**
     *天干相生：乙丁相生
     *
     * @param yiDingXiangSheng 天干相生：乙丁相生（0:显示。1:关闭）
     */
    public void setYiDingXiangSheng(int yiDingXiangSheng) {
        this.yiDingXiangSheng = (yiDingXiangSheng == 0 || yiDingXiangSheng == 1) ? yiDingXiangSheng : 0;
    }

    /**
     *天干相生：丙戊相生
     *
     * @param bingWuXiangSheng 天干相生：丙戊相生（0:显示。1:关闭）
     */
    public void setBingWuXiangSheng(int bingWuXiangSheng) {
        this.bingWuXiangSheng = (bingWuXiangSheng == 0 || bingWuXiangSheng == 1) ? bingWuXiangSheng : 0;
    }

    /**
     *天干相生：丙己相生
     *
     * @param bingJiXiangSheng 天干相生：丙己相生（0:显示。1:关闭）
     */
    public void setBingJiXiangSheng(int bingJiXiangSheng) {
        this.bingJiXiangSheng = (bingJiXiangSheng == 0 || bingJiXiangSheng == 1) ? bingJiXiangSheng : 0;
    }

    /**
     *天干相生：丁戊相生
     *
     * @param dingWuXiangSheng 天干相生：丁戊相生（0:显示。1:关闭）
     */
    public void setDingWuXiangSheng(int dingWuXiangSheng) {
        this.dingWuXiangSheng = (dingWuXiangSheng == 0 || dingWuXiangSheng == 1) ? dingWuXiangSheng : 0;
    }

    /**
     *天干相生：丁己相生
     *
     * @param dingJiXiangSheng 天干相生：丁己相生（0:显示。1:关闭）
     */
    public void setDingJiXiangSheng(int dingJiXiangSheng) {
        this.dingJiXiangSheng = (dingJiXiangSheng == 0 || dingJiXiangSheng == 1) ? dingJiXiangSheng : 0;
    }

    /**
     *天干相生：戊庚相生
     *
     * @param wuGengXiangSheng 天干相生：戊庚相生（0:显示。1:关闭）
     */
    public void setWuGengXiangSheng(int wuGengXiangSheng) {
        this.wuGengXiangSheng = (wuGengXiangSheng == 0 || wuGengXiangSheng == 1) ? wuGengXiangSheng : 0;
    }

    /**
     *天干相生：戊辛相生
     *
     * @param  wuXinXiangSheng 天干相生：戊辛相生（0:显示。1:关闭）
     */
    public void setWuXinXiangSheng(int wuXinXiangSheng) {
        this.wuXinXiangSheng = (wuXinXiangSheng == 0 || wuXinXiangSheng == 1) ? wuXinXiangSheng : 0;
    }

    /**
     *天干相生：己庚相生
     *
     * @param jiGengXiangSheng 天干相生：己庚相生（0:显示。1:关闭）
     */
    public void setJiGengXiangSheng(int jiGengXiangSheng) {
        this.jiGengXiangSheng = (jiGengXiangSheng == 0 || jiGengXiangSheng == 1) ? jiGengXiangSheng : 0;
    }

    /**
     *天干相生：己辛相生
     *
     * @param jiXinXiangSheng 天干相生：己辛相生（0:显示。1:关闭）
     */
    public void setJiXinXiangSheng(int jiXinXiangSheng) {
        this.jiXinXiangSheng = (jiXinXiangSheng == 0 || jiXinXiangSheng == 1) ? jiXinXiangSheng : 0;
    }

    /**
     *天干相生：庚壬相生
     *
     * @param gengRenXiangSheng 天干相生：庚壬相生（0:显示。1:关闭）
     */
    public void setGengRenXiangSheng(int gengRenXiangSheng) {
        this.gengRenXiangSheng = (gengRenXiangSheng == 0 || gengRenXiangSheng == 1) ? gengRenXiangSheng : 0;
    }

    /**
     *天干相生：庚癸相生
     *
     * @param gengGuiXiangSheng 天干相生：庚癸相生（0:显示。1:关闭）
     */
    public void setGengGuiXiangSheng(int gengGuiXiangSheng) {
        this.gengGuiXiangSheng = (gengGuiXiangSheng == 0 || gengGuiXiangSheng == 1) ? gengGuiXiangSheng : 0;
    }

    /**
     *天干相生：辛壬相生
     *
     * @param xinRenXiangSheng 天干相生：辛壬相生（0:显示。1:关闭）
     */
    public void setXinRenXiangSheng(int xinRenXiangSheng) {
        this.xinRenXiangSheng = (xinRenXiangSheng == 0 || xinRenXiangSheng == 1) ? xinRenXiangSheng : 0;
    }

    /**
     *天干相生：辛癸相生
     *
     * @param xinGuiXiangSheng 天干相生：辛癸相生（0:显示。1:关闭）
     */
    public void setXinGuiXiangSheng(int xinGuiXiangSheng) {
        this.xinGuiXiangSheng = ( xinGuiXiangSheng== 0 || xinGuiXiangSheng == 1) ? xinGuiXiangSheng : 0;
    }

    /**
     *天干相生：壬甲相生
     *
     * @param renJiaXiangSheng 天干相生：壬甲相生（0:显示。1:关闭）
     */
    public void setRenJiaXiangSheng(int renJiaXiangSheng) {
        this.renJiaXiangSheng = (renJiaXiangSheng == 0 || renJiaXiangSheng == 1) ? renJiaXiangSheng : 0;
    }

    /**
     *天干相生：壬乙相生
     *
     * @param renYiXiangSheng 天干相生：壬乙相生（0:显示。1:关闭）
     */
    public void setRenYiXiangSheng(int renYiXiangSheng) {
        this.renYiXiangSheng = (renYiXiangSheng == 0 || renYiXiangSheng == 1) ? renYiXiangSheng : 0;
    }

    /**
     *天干相生：癸甲相生
     *
     * @param guiJiaXiangSheng 天干相生：癸甲相生（0:显示。1:关闭）
     */
    public void setGuiJiaXiangSheng(int guiJiaXiangSheng) {
        this.guiJiaXiangSheng = (guiJiaXiangSheng == 0 || guiJiaXiangSheng == 1) ? guiJiaXiangSheng : 0;
    }

    /**
     *天干相生：癸乙相生
     *
     * @param guiYiXiangSheng 天干相生：癸乙相生（0:显示。1:关闭）
     */
    public void setGuiYiXiangSheng(int guiYiXiangSheng) {
        this.guiYiXiangSheng = (guiYiXiangSheng == 0 || guiYiXiangSheng == 1) ? guiYiXiangSheng : 0;
    }

    /**
     *天干相合：甲己相合
     *
     * @param jiaJiXiangHe 天干相合：甲己相合（0:显示。1:关闭）
     */
    public void setJiaJiXiangHe(int jiaJiXiangHe) {
        this.jiaJiXiangHe = (jiaJiXiangHe == 0 || jiaJiXiangHe == 1) ? jiaJiXiangHe : 0;
    }

    /**
     *天干相合：乙庚相合
     *
     * @param yiGengXiangHe 天干相合：乙庚相合（0:显示。1:关闭）
     */
    public void setYiGengXiangHe(int yiGengXiangHe) {
        this.yiGengXiangHe = (yiGengXiangHe == 0 || yiGengXiangHe == 1) ? yiGengXiangHe : 0;
    }

    /**
     *天干相合：丙辛相合
     *
     * @param bingXinXiangHe 天干相合：丙辛相合（0:显示。1:关闭）
     */
    public void setBingXinXiangHe(int bingXinXiangHe) {
        this.bingXinXiangHe = (bingXinXiangHe == 0 || bingXinXiangHe == 1) ? bingXinXiangHe : 0;
    }

    /**
     *天干相合：丁壬相合
     *
     * @param dingRenXiangHe 天干相合：丁壬相合（0:显示。1:关闭）
     */
    public void setDingRenXiangHe(int dingRenXiangHe) {
        this.dingRenXiangHe = (dingRenXiangHe == 0 || dingRenXiangHe == 1) ? dingRenXiangHe : 0;
    }

    /**
     *天干相合：戊癸相合
     *
     * @param wuGuiXiangHe 天干相合：戊癸相合（0:显示。1:关闭）
     */
    public void setWuGuiXiangHe(int wuGuiXiangHe) {
        this.wuGuiXiangHe = (wuGuiXiangHe == 0 || wuGuiXiangHe == 1) ? wuGuiXiangHe : 0;
    }

    /**
     *天干相冲：甲庚相冲
     *
     * @param jiaGengXiangChong 天干相冲：甲庚相冲（0:显示。1:关闭）
     */
    public void setJiaGengXiangChong(int jiaGengXiangChong) {
        this.jiaGengXiangChong = (jiaGengXiangChong == 0 || jiaGengXiangChong == 1) ? jiaGengXiangChong : 0;
    }

    /**
     *天干相冲：乙辛相冲
     *
     * @param yiXinXiangChong 天干相冲：乙辛相冲（0:显示。1:关闭）
     */
    public void setYiXinXiangChong(int yiXinXiangChong) {
        this.yiXinXiangChong = (yiXinXiangChong == 0 || yiXinXiangChong == 1) ? yiXinXiangChong : 0;
    }

    /**
     *天干相冲：丙壬相冲
     *
     * @param bingRenXiangChong 天干相冲：丙壬相冲（0:显示。1:关闭）
     */
    public void setBingRenXiangChong(int bingRenXiangChong) {
        this.bingRenXiangChong = (bingRenXiangChong == 0 || bingRenXiangChong == 1) ? bingRenXiangChong : 0;
    }

    /**
     *天干相冲：丁癸相冲
     *
     * @param dingGuiXiangChong 天干相冲：丁癸相冲（0:显示。1:关闭）
     */
    public void setDingGuiXiangChong(int dingGuiXiangChong) {
        this.dingGuiXiangChong = (dingGuiXiangChong == 0 || dingGuiXiangChong == 1) ? dingGuiXiangChong : 0;
    }

    /**
     *天干相克：甲戊相克
     *
     * @param jiaWuXiangKe 天干相克：甲戊相克（0:显示。1:关闭）
     */
    public void setJiaWuXiangKe(int jiaWuXiangKe) {
        this.jiaWuXiangKe = (jiaWuXiangKe == 0 || jiaWuXiangKe == 1) ? jiaWuXiangKe : 0;
    }

    /**
     *天干相克：乙己相克
     *
     * @param yiJiXiangKe 天干相克：乙己相克（0:显示。1:关闭）
     */
    public void setYiJiXiangKe(int yiJiXiangKe) {
        this.yiJiXiangKe = (yiJiXiangKe == 0 || yiJiXiangKe == 1) ? yiJiXiangKe : 0;
    }

    /**
     *天干相克：丙庚相克
     *
     * @param bingGengXiangKe 天干相克：丙庚相克（0:显示。1:关闭）
     */
    public void setBingGengXiangKe(int bingGengXiangKe) {
        this.bingGengXiangKe = (bingGengXiangKe == 0 || bingGengXiangKe == 1) ? bingGengXiangKe : 0;
    }

    /**
     *天干相克：丁辛相克
     *
     * @param dingXinXiangKe 天干相克：丁辛相克（0:显示。1:关闭）
     */
    public void setDingXinXiangKe(int dingXinXiangKe) {
        this.dingXinXiangKe = (dingXinXiangKe == 0 || dingXinXiangKe == 1) ? dingXinXiangKe : 0;
    }

    /**
     *天干相克：戊壬相克
     *
     * @param wuRenXiangKe 天干相克：戊壬相克（0:显示。1:关闭）
     */
    public void setWuRenXiangKe(int wuRenXiangKe) {
        this.wuRenXiangKe = ( wuRenXiangKe== 0 || wuRenXiangKe == 1) ? wuRenXiangKe : 0;
    }

    /**
     *天干相克：己癸相克
     *
     * @param jiGuiXiangKe 天干相克：己癸相克（0:显示。1:关闭）
     */
    public void setJiGuiXiangKe(int jiGuiXiangKe) {
        this.jiGuiXiangKe = (jiGuiXiangKe == 0 || jiGuiXiangKe == 1) ? jiGuiXiangKe : 0;
    }

    /**
     *天干相克：庚甲相克
     *
     * @param gengJiaXiangKe 天干相克：庚甲相克（0:显示。1:关闭）
     */
    public void setGengJiaXiangKe(int gengJiaXiangKe) {
        this.gengJiaXiangKe = (gengJiaXiangKe == 0 || gengJiaXiangKe == 1) ? gengJiaXiangKe : 0;
    }

    /**
     *天干相克：辛乙相克
     *
     * @param xinYiXiangKe 天干相克：辛乙相克（0:显示。1:关闭）
     */
    public void setXinYiXiangKe(int xinYiXiangKe) {
        this.xinYiXiangKe = (xinYiXiangKe == 0 || xinYiXiangKe == 1) ? xinYiXiangKe : 0;
    }

    /**
     *天干相克：壬丙相克
     *
     * @param renBingXiangKe 天干相克：壬丙相克（0:显示。1:关闭）
     */
    public void setRenBingXiangKe(int renBingXiangKe) {
        this.renBingXiangKe = (renBingXiangKe == 0 || renBingXiangKe == 1) ? renBingXiangKe : 0;
    }

    /**
     *天干相克：癸丁相克
     *
     * @param guiDingXiangKe 天干相克：癸丁相克（0:显示。1:关闭）
     */
    public void setGuiDingXiangKe(int guiDingXiangKe) {
        this.guiDingXiangKe = (guiDingXiangKe == 0 || guiDingXiangKe == 1) ? guiDingXiangKe : 0;
    }

    /**
     *地支半合
     *
     * @param diZhiBanHe 地支半合（0:显示。1:关闭）
     */
    public void setDiZhiBanHe(int diZhiBanHe) {
        this.diZhiBanHe = (diZhiBanHe == 0 || diZhiBanHe == 1) ? diZhiBanHe : 0;
    }

    /**
     *地支拱合
     *
     * @param diZhiGongHe 地支拱合（0:显示。1:关闭）
     */
    public void setDiZhiGongHe(int diZhiGongHe) {
        this.diZhiGongHe = (diZhiGongHe == 0 || diZhiGongHe == 1) ? diZhiGongHe : 0;
    }

    /**
     *地支暗合
     *
     * @param diZhiAnHe 地支暗合（0:显示。1:关闭）
     */
    public void setDiZhiAnHe(int diZhiAnHe) {
        this.diZhiAnHe = (diZhiAnHe == 0 || diZhiAnHe == 1) ? diZhiAnHe : 0;
    }

    /**
     *地支六合
     *
     * @param diZhiLiuHe 地支六合（0:显示。1:关闭）
     */
    public void setDiZhiLiuHe(int diZhiLiuHe) {
        this.diZhiLiuHe = (diZhiLiuHe == 0 || diZhiLiuHe == 1) ? diZhiLiuHe : 0;
    }

    /**
     *地支相刑
     *
     * @param diZhiXiangXing 地支相刑（0:显示。1:关闭）
     */
    public void setDiZhiXiangXing(int diZhiXiangXing) {
        this.diZhiXiangXing = (diZhiXiangXing == 0 || diZhiXiangXing == 1) ? diZhiXiangXing : 0;
    }

    /**
     *地支相冲
     *
     * @param diZhiXiangChong 地支相冲（0:显示。1:关闭）
     */
    public void setDiZhiXiangChong(int diZhiXiangChong) {
        this.diZhiXiangChong = (diZhiXiangChong == 0 || diZhiXiangChong == 1) ? diZhiXiangChong : 0;
    }

    /**
     *地支相破
     *
     * @param diZhiXiangPo 地支相破（0:显示。1:关闭）
     */
    public void setDiZhiXiangPo(int diZhiXiangPo) {
        this.diZhiXiangPo = (diZhiXiangPo == 0 || diZhiXiangPo == 1) ? diZhiXiangPo : 0;
    }

    /**
     *地支相害
     *
     * @param diZhiXiangHai 地支相害（0:显示。1:关闭）
     */
    public void setDiZhiXiangHai(int diZhiXiangHai) {
        this.diZhiXiangHai = (diZhiXiangHai == 0 || diZhiXiangHai == 1) ? diZhiXiangHai : 0;
    }

    /**
     *地支半合类型
     *
     * @param diZhiBanHeType 地支半合类型（0:显示。1:关闭）
     */
    public void setDiZhiBanHeType(int diZhiBanHeType) {
        this.diZhiBanHeType = (diZhiBanHeType == 0 || diZhiBanHeType == 1) ? diZhiBanHeType : 0;
    }

    /**
     *地支拱合类型
     *
     * @param diZhiGongHeType 地支拱合类型（0:显示。1:关闭）
     */
    public void setDiZhiGongHeType(int diZhiGongHeType) {
        this.diZhiGongHeType = (diZhiGongHeType == 0 || diZhiGongHeType == 1) ? diZhiGongHeType : 0;
    }

    /**
     *地支暗合类型
     *
     * @param diZhiAnHeType 地支暗合类型（0:显示。1:关闭）
     */
    public void setDiZhiAnHeType(int diZhiAnHeType) {
        this.diZhiAnHeType = (diZhiAnHeType == 0 || diZhiAnHeType == 1) ? diZhiAnHeType : 0;
    }

    /**
     *地支六合类型
     *
     * @param diZhiLiuHeType 地支六合类型（0:显示。1:关闭）
     */
    public void setDiZhiLiuHeType(int diZhiLiuHeType) {
        this.diZhiLiuHeType = (diZhiLiuHeType == 0 || diZhiLiuHeType == 1) ? diZhiLiuHeType : 0;
    }

    /**
     *地支相刑类型
     *
     * @param diZhiXiangXingType 地支相刑类型（0:显示。1:关闭）
     */
    public void setDiZhiXiangXingType(int diZhiXiangXingType) {
        this.diZhiXiangXingType = (diZhiXiangXingType == 0 || diZhiXiangXingType == 1) ? diZhiXiangXingType : 0;
    }

    /**
     *地支相冲类型
     *
     * @param diZhiXiangChongType 地支相冲类型（0:显示。1:关闭）
     */
    public void setDiZhiXiangChongType(int diZhiXiangChongType) {
        this.diZhiXiangChongType = (diZhiXiangChongType == 0 || diZhiXiangChongType == 1) ? diZhiXiangChongType : 0;
    }

    /**
     *地支相破类型
     *
     * @param diZhiXiangPoType 地支相破类型（0:显示。1:关闭）
     */
    public void setDiZhiXiangPoType(int diZhiXiangPoType) {
        this.diZhiXiangPoType = (diZhiXiangPoType == 0 || diZhiXiangPoType == 1) ? diZhiXiangPoType : 0;
    }

    /**
     *地支相害类型
     *
     * @param diZhiXiangHaiType 地支相害类型（0:显示。1:关闭）
     */
    public void setDiZhiXiangHaiType(int diZhiXiangHaiType) {
        this.diZhiXiangHaiType = (diZhiXiangHaiType == 0 || diZhiXiangHaiType == 1) ? diZhiXiangHaiType : 0;
    }

    /**
     *地支半合：寅午半合
     *
     * @param yinWuBanHe 地支半合：寅午半合（0:显示。1:关闭）
     */
    public void setYinWuBanHe(int yinWuBanHe) {
        this.yinWuBanHe = (yinWuBanHe == 0 || yinWuBanHe == 1) ? yinWuBanHe : 0;
    }

    /**
     *地支半合：申子半合
     *
     * @param shenZiBanHe 地支半合：申子半合（0:显示。1:关闭）
     */
    public void setShenZiBanHe(int shenZiBanHe) {
        this.shenZiBanHe = (shenZiBanHe == 0 || shenZiBanHe == 1) ? shenZiBanHe : 0;
    }

    /**
     *地支半合：巳酉半合
     *
     * @param siYouBanHe 地支半合：巳酉半合（0:显示。1:关闭）
     */
    public void setSiYouBanHe(int siYouBanHe) {
        this.siYouBanHe = (siYouBanHe == 0 || siYouBanHe == 1) ? siYouBanHe : 0;
    }

    /**
     *地支半合：亥卯半合
     *
     * @param haiMaoBanHe 地支半合：亥卯半合（0:显示。1:关闭）
     */
    public void setHaiMaoBanHe(int haiMaoBanHe) {
        this.haiMaoBanHe = (haiMaoBanHe == 0 || haiMaoBanHe == 1) ? haiMaoBanHe : 0;
    }

    /**
     *地支半合：子辰半合
     *
     * @param ziChenBanHe 地支半合：子辰半合（0:显示。1:关闭）
     */
    public void setZiChenBanHe(int ziChenBanHe) {
        this.ziChenBanHe = (ziChenBanHe == 0 || ziChenBanHe == 1) ? ziChenBanHe : 0;
    }

    /**
     *地支半合：午戌半合
     *
     * @param wuXuBanHe 地支半合：午戌半合（0:显示。1:关闭）
     */
    public void setWuXuBanHe(int wuXuBanHe) {
        this.wuXuBanHe = (wuXuBanHe == 0 || wuXuBanHe == 1) ? wuXuBanHe : 0;
    }

    /**
     *地支半合：卯未半合
     *
     * @param maoWeiBanHe 地支半合：卯未半合（0:显示。1:关闭）
     */
    public void setMaoWeiBanHe(int maoWeiBanHe) {
        this.maoWeiBanHe = (maoWeiBanHe == 0 || maoWeiBanHe == 1) ? maoWeiBanHe : 0;
    }

    /**
     *地支半合：酉丑半合
     *
     * @param youChouBanHe 地支半合：酉丑半合（0:显示。1:关闭）
     */
    public void setYouChouBanHe(int youChouBanHe) {
        this.youChouBanHe = (youChouBanHe == 0 || youChouBanHe == 1) ? youChouBanHe : 0;
    }

    /**
     *地支拱合：申辰拱合
     *
     * @param shenChenGongHe 地支拱合：申辰拱合（0:显示。1:关闭）
     */
    public void setShenChenGongHe(int shenChenGongHe) {
        this.shenChenGongHe = (shenChenGongHe == 0 || shenChenGongHe == 1) ? shenChenGongHe : 0;
    }

    /**
     *地支拱合：亥未拱合
     *
     * @param haiWeiGongHe 地支拱合：亥未拱合（0:显示。1:关闭）
     */
    public void setHaiWeiGongHe(int haiWeiGongHe) {
        this.haiWeiGongHe = (haiWeiGongHe == 0 || haiWeiGongHe == 1) ? haiWeiGongHe : 0;
    }

    /**
     *地支拱合：寅戌拱合
     *
     * @param yinXuGongHe 地支拱合：寅戌拱合（0:显示。1:关闭）
     */
    public void setYinXuGongHe(int yinXuGongHe) {
        this.yinXuGongHe = (yinXuGongHe == 0 || yinXuGongHe == 1) ? yinXuGongHe : 0;
    }

    /**
     *地支拱合：巳丑拱合
     *
     * @param siChouGongHe 地支拱合：巳丑拱合（0:显示。1:关闭）
     */
    public void setSiChouGongHe(int siChouGongHe) {
        this.siChouGongHe = (siChouGongHe == 0 || siChouGongHe == 1) ? siChouGongHe : 0;
    }

    /**
     *地支暗合：卯申暗合
     *
     * @param maoShenAnHe 地支暗合：卯申暗合（0:显示。1:关闭）
     */
    public void setMaoShenAnHe(int maoShenAnHe) {
        this.maoShenAnHe = (maoShenAnHe == 0 || maoShenAnHe == 1) ? maoShenAnHe : 0;
    }

    /**
     *地支暗合：午亥暗合
     *
     * @param wuHaiAnHe 地支暗合：午亥暗合（0:显示。1:关闭）
     */
    public void setWuHaiAnHe(int wuHaiAnHe) {
        this.wuHaiAnHe = (wuHaiAnHe == 0 || wuHaiAnHe == 1) ? wuHaiAnHe : 0;
    }

    /**
     *地支暗合：丑寅暗合
     *
     * @param chouYinAnHe 地支暗合：丑寅暗合（0:显示。1:关闭）
     */
    public void seChouYinAnHe(int chouYinAnHe) {
        this.chouYinAnHe = (chouYinAnHe == 0 || chouYinAnHe == 1) ? chouYinAnHe : 0;
    }

    /**
     *地支暗合：寅未暗合
     *
     * @param yinWeiAnHe 地支暗合：寅未暗合（0:显示。1:关闭）
     */
    public void setYinWeiAnHe(int yinWeiAnHe) {
        this.yinWeiAnHe = (yinWeiAnHe == 0 || yinWeiAnHe == 1) ? yinWeiAnHe : 0;
    }

    /**
     *地支暗合：寅午暗合
     *
     * @param yinWuAnHe 地支暗合：寅午暗合（0:显示。1:关闭）
     */
    public void setYinWuAnHe(int yinWuAnHe) {
        this.yinWuAnHe = (yinWuAnHe == 0 || yinWuAnHe == 1) ? yinWuAnHe : 0;
    }

    /**
     *地支暗合：子戌暗合
     *
     * @param ziXuAnHe 地支暗合：子戌暗合（0:显示。1:关闭）
     */
    public void setZiXuAnHe(int ziXuAnHe) {
        this.ziXuAnHe = (ziXuAnHe == 0 || ziXuAnHe == 1) ? ziXuAnHe : 0;
    }

    /**
     *地支暗合：子辰暗合
     *
     * @param ziChenAnHe 地支暗合：子辰暗合（0:显示。1:关闭）
     */
    public void setZiChenAnHe(int ziChenAnHe) {
        this.ziChenAnHe = (ziChenAnHe == 0 || ziChenAnHe == 1) ? ziChenAnHe : 0;
    }

    /**
     *地支暗合：子巳暗合
     *
     * @param ziSiAnHe 地支暗合：子巳暗合（0:显示。1:关闭）
     */
    public void setZiSiAnHe(int ziSiAnHe) {
        this.ziSiAnHe = (ziSiAnHe == 0 || ziSiAnHe == 1) ? ziSiAnHe : 0;
    }

    /**
     *地支暗合：巳酉暗合
     *
     * @param siYouAnHe 地支暗合：巳酉暗合（0:显示。1:关闭）
     */
    public void setSiYouAnHe(int siYouAnHe) {
        this.siYouAnHe = (siYouAnHe == 0 || siYouAnHe == 1) ? siYouAnHe : 0;
    }

    /**
     *地支六合：子丑六合
     *
     * @param ziChouLiuHe 地支六合：子丑六合（0:显示。1:关闭）
     */
    public void setZiChouLiuHe(int ziChouLiuHe) {
        this.ziChouLiuHe = (ziChouLiuHe == 0 || ziChouLiuHe == 1) ? ziChouLiuHe : 0;
    }

    /**
     *地支六合：寅亥六合
     *
     * @param yinHaiLiuHe 地支六合：寅亥六合（0:显示。1:关闭）
     */
    public void setYinHaiLiuHe(int yinHaiLiuHe) {
        this.yinHaiLiuHe = (yinHaiLiuHe == 0 || yinHaiLiuHe == 1) ? yinHaiLiuHe : 0;
    }

    /**
     *地支六合：卯戌六合
     *
     * @param maoXuLiuHe 地支六合：卯戌六合（0:显示。1:关闭）
     */
    public void setMaoXuLiuHe(int maoXuLiuHe) {
        this.maoXuLiuHe = (maoXuLiuHe == 0 || maoXuLiuHe == 1) ? maoXuLiuHe : 0;
    }

    /**
     *地支六合：辰酉六合
     *
     * @param chenYouLiuHe 地支六合：辰酉六合（0:显示。1:关闭）
     */
    public void setChenYouLiuHe(int chenYouLiuHe) {
        this.chenYouLiuHe = (chenYouLiuHe == 0 || chenYouLiuHe == 1) ? chenYouLiuHe : 0;
    }

    /**
     *地支六合：巳申六合
     *
     * @param siShenLiuHe 地支六合：巳申六合（0:显示。1:关闭）
     */
    public void setSiShenLiuHe(int siShenLiuHe) {
        this.siShenLiuHe = (siShenLiuHe == 0 || siShenLiuHe == 1) ? siShenLiuHe : 0;
    }

    /**
     *地支六合：午未六合
     *
     * @param wuWeiLiuHe 地支六合：午未六合（0:显示。1:关闭）
     */
    public void setWuWeiLiuHe(int wuWeiLiuHe) {
        this.wuWeiLiuHe = (wuWeiLiuHe == 0 || wuWeiLiuHe == 1) ? wuWeiLiuHe : 0;
    }

    /**
     *地支相刑：寅巳相刑
     *
     * @param yinSiXiangXing 地支相刑：寅巳相刑（0:显示。1:关闭）
     */
    public void setYinSiXiangXing(int yinSiXiangXing) {
        this.yinSiXiangXing = (yinSiXiangXing == 0 || yinSiXiangXing == 1) ? yinSiXiangXing : 0;
    }

    /**
     *地支相刑：巳申相刑
     *
     * @param siShenXiangXing 地支相刑：巳申相刑（0:显示。1:关闭）
     */
    public void setSiShenXiangXing(int siShenXiangXing) {
        this.siShenXiangXing = (siShenXiangXing == 0 || siShenXiangXing == 1) ? siShenXiangXing : 0;
    }

    /**
     *地支相刑：申寅相刑
     *
     * @param shenYinXiangXing 地支相刑：申寅相刑（0:显示。1:关闭）
     */
    public void setShenYinXiangXing(int shenYinXiangXing) {
        this.shenYinXiangXing = (shenYinXiangXing == 0 || shenYinXiangXing == 1) ? shenYinXiangXing : 0;
    }

    /**
     *地支相刑：丑戌相刑
     *
     * @param chouXuXiangXing 地支相刑：丑戌相刑（0:显示。1:关闭）
     */
    public void setChouXuXiangXing(int chouXuXiangXing) {
        this.chouXuXiangXing = (chouXuXiangXing == 0 || chouXuXiangXing == 1) ? chouXuXiangXing : 0;
    }

    /**
     *地支相刑：戌未相刑
     *
     * @param xuWeiXiangXing 地支相刑：戌未相刑（0:显示。1:关闭）
     */
    public void setXuWeiXiangXing(int xuWeiXiangXing) {
        this.xuWeiXiangXing = (xuWeiXiangXing == 0 || xuWeiXiangXing == 1) ? xuWeiXiangXing : 0;
    }

    /**
     *地支相刑：未丑相刑
     *
     * @param weiChouXiangXing 地支相刑：未丑相刑（0:显示。1:关闭）
     */
    public void setWeiChouXiangXing(int weiChouXiangXing) {
        this.weiChouXiangXing = (weiChouXiangXing == 0 || weiChouXiangXing == 1) ? weiChouXiangXing : 0;
    }

    /**
     *地支相刑：子卯相刑
     *
     * @param ziMaoXiangXing 地支相刑：子卯相刑（0:显示。1:关闭）
     */
    public void setZiMaoXiangXing(int ziMaoXiangXing) {
        this.ziMaoXiangXing = (ziMaoXiangXing == 0 || ziMaoXiangXing == 1) ? ziMaoXiangXing : 0;
    }

    /**
     *地支相刑：酉酉自刑
     *
     * @param youYouXiangXing 地支相刑：酉酉自刑（0:显示。1:关闭）
     */
    public void setYouYouXiangXing(int youYouXiangXing) {
        this.youYouXiangXing = (youYouXiangXing == 0 || youYouXiangXing == 1) ? youYouXiangXing : 0;
    }

    /**
     *地支相刑：亥亥自刑
     *
     * @param haiHaiXiangXing 地支相刑：亥亥自刑（0:显示。1:关闭）
     */
    public void setHaiHaiXiangXing(int haiHaiXiangXing) {
        this.haiHaiXiangXing = (haiHaiXiangXing == 0 || haiHaiXiangXing == 1) ? haiHaiXiangXing : 0;
    }

    /**
     *地支相刑：午午自刑
     *
     * @param wuWuXiangXing 地支相刑：午午自刑（0:显示。1:关闭）
     */
    public void setWuWuXiangXing(int wuWuXiangXing) {
        this.wuWuXiangXing = (wuWuXiangXing == 0 || wuWuXiangXing == 1) ? wuWuXiangXing : 0;
    }

    /**
     *地支相刑：辰辰自刑
     *
     * @param chenChenXiangXing 地支相刑：辰辰自刑（0:显示。1:关闭）
     */
    public void setChenChenXiangXing(int chenChenXiangXing) {
        this.chenChenXiangXing = (chenChenXiangXing == 0 || chenChenXiangXing == 1) ? chenChenXiangXing : 0;
    }

    /**
     *地支相冲：子午相冲
     *
     * @param ziWuXiangChong 地支相冲：子午相冲（0:显示。1:关闭）
     */
    public void setZiWuXiangChong(int ziWuXiangChong) {
        this.ziWuXiangChong = (ziWuXiangChong == 0 || ziWuXiangChong == 1) ? ziWuXiangChong : 0;
    }

    /**
     *地支相冲：丑未相冲
     *
     * @param chouWeiXiangChong 地支相冲：丑未相冲（0:显示。1:关闭）
     */
    public void setChouWeiXiangChong(int chouWeiXiangChong) {
        this.chouWeiXiangChong = (chouWeiXiangChong == 0 || chouWeiXiangChong == 1) ? chouWeiXiangChong : 0;
    }

    /**
     *地支相冲：寅申相冲
     *
     * @param yinShenXiangChong 地支相冲：寅申相冲（0:显示。1:关闭）
     */
    public void setYinShenXiangChong(int yinShenXiangChong) {
        this.yinShenXiangChong = (yinShenXiangChong == 0 || yinShenXiangChong == 1) ? yinShenXiangChong : 0;
    }

    /**
     *地支相冲：卯酉相冲
     *
     * @param maoYouXiangChong 地支相冲：卯酉相冲（0:显示。1:关闭）
     */
    public void setMaoYouXiangChong(int maoYouXiangChong) {
        this.maoYouXiangChong = (maoYouXiangChong == 0 || maoYouXiangChong == 1) ? maoYouXiangChong : 0;
    }

    /**
     *地支相冲：辰戌相冲
     *
     * @param chenXuXiangChong 地支相冲：辰戌相冲（0:显示。1:关闭）
     */
    public void setChenXuXiangChong(int chenXuXiangChong) {
        this.chenXuXiangChong = (chenXuXiangChong == 0 || chenXuXiangChong == 1) ? chenXuXiangChong : 0;
    }

    /**
     *地支相冲：巳亥相冲
     *
     * @param siHaiXiangChong 地支相冲：巳亥相冲（0:显示。1:关闭）
     */
    public void setSiHaiXiangChong(int siHaiXiangChong) {
        this.siHaiXiangChong = (siHaiXiangChong == 0 || siHaiXiangChong == 1) ? siHaiXiangChong : 0;
    }

    /**
     *地支相破：子酉相破
     *
     * @param ziYouXiangPo 地支相破：子酉相破（0:显示。1:关闭）
     */
    public void setZiYouXiangPo(int ziYouXiangPo) {
        this.ziYouXiangPo = (ziYouXiangPo == 0 || ziYouXiangPo == 1) ? ziYouXiangPo : 0;
    }

    /**
     *地支相破：寅亥相破
     *
     * @param yinHaiXiangPo 地支相破：寅亥相破（0:显示。1:关闭）
     */
    public void setYinHaiXiangPo(int yinHaiXiangPo) {
        this.yinHaiXiangPo = (yinHaiXiangPo == 0 || yinHaiXiangPo == 1) ? yinHaiXiangPo : 0;
    }

    /**
     *地支相破：卯午相破
     *
     * @param maoWuXiangPo 地支相破：卯午相破（0:显示。1:关闭）
     */
    public void setMaoWuXiangPo(int maoWuXiangPo) {
        this.maoWuXiangPo = (maoWuXiangPo == 0 || maoWuXiangPo == 1) ? maoWuXiangPo : 0;
    }

    /**
     *地支相破：辰丑相破
     *
     * @param chenChouXiangPo 地支相破：辰丑相破（0:显示。1:关闭）
     */
    public void setChenChouXiangPo(int chenChouXiangPo) {
        this.chenChouXiangPo = (chenChouXiangPo == 0 || chenChouXiangPo == 1) ? chenChouXiangPo : 0;
    }

    /**
     *地支相破：巳申相破
     *
     * @param siShenXiangPo 地支相破：巳申相破（0:显示。1:关闭）
     */
    public void setSiShenXiangPo(int siShenXiangPo) {
        this.siShenXiangPo = (siShenXiangPo == 0 || siShenXiangPo == 1) ? siShenXiangPo : 0;
    }

    /**
     *地支相破：戌未相破
     *
     * @param xuWeiXiangPo 地支相破：戌未相破（0:显示。1:关闭）
     */
    public void setXuWeiXiangPo(int xuWeiXiangPo) {
        this.xuWeiXiangPo = (xuWeiXiangPo == 0 || xuWeiXiangPo == 1) ? xuWeiXiangPo : 0;
    }

    /**
     *地支相害：子未相害
     *
     * @param ziWeiXiangHai 地支相害：子未相害（0:显示。1:关闭）
     */
    public void setZiWeiXiangHai(int ziWeiXiangHai) {
        this.ziWeiXiangHai = (ziWeiXiangHai == 0 || ziWeiXiangHai == 1) ? ziWeiXiangHai : 0;
    }

    /**
     *地支相害：丑午相害
     *
     * @param chouWuXiangHai 地支相害：丑午相害（0:显示。1:关闭）
     */
    public void setChouWuXiangHai(int chouWuXiangHai) {
        this.chouWuXiangHai = (chouWuXiangHai == 0 || chouWuXiangHai == 1) ? chouWuXiangHai : 0;
    }

    /**
     *地支相害：寅巳相害
     *
     * @param yinSiXiangHai 地支相害：寅巳相害（0:显示。1:关闭）
     */
    public void setYinSiXiangHai(int yinSiXiangHai) {
        this.yinSiXiangHai = (yinSiXiangHai == 0 || yinSiXiangHai == 1) ? yinSiXiangHai : 0;
    }

    /**
     *地支相害：卯辰相害
     *
     * @param maoChenXiangHai 地支相害：卯辰相害（0:显示。1:关闭）
     */
    public void setMaoChenXiangHai(int maoChenXiangHai) {
        this.maoChenXiangHai = (maoChenXiangHai == 0 || maoChenXiangHai == 1) ? maoChenXiangHai : 0;
    }

    /**
     *地支相害：申亥相害
     *
     * @param shenHaiXiangHai 地支相害：申亥相害（0:显示。1:关闭）
     */
    public void setShenHaiXiangHai(int shenHaiXiangHai) {
        this.shenHaiXiangHai = (shenHaiXiangHai == 0 || shenHaiXiangHai == 1) ? shenHaiXiangHai : 0;
    }

    /**
     *地支相害：酉戌相害
     *
     * @param youXuXiangHai 地支相害：酉戌相害（0:显示。1:关闭）
     */
    public void setYouXuXiangHai(int youXuXiangHai) {
        this.youXuXiangHai = (youXuXiangHai == 0 || youXuXiangHai == 1) ? youXuXiangHai : 0;
    }


}
