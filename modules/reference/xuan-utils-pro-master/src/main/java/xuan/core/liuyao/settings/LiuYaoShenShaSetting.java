package xuan.core.liuyao.settings;

import lombok.Data;

/**
 * 六爻 - 神煞设置
 *
 * @author 善待
 */
@Data
public class LiuYaoShenShaSetting {

    /**
     * 太极贵人（0:显示。1:关闭）
     */
    private int taiJiGuiRen;

    /**
     * 天乙贵人（0:显示。1:关闭）
     */
    private int tianYiGuiRen;

    /**
     * 福星贵人（0:显示。1:关闭）
     */
    private int fuXingGuiRen;

    /**
     * 文昌贵人（0:显示。1:关闭）
     */
    private int wenChangGuiRen;

    /**
     * 天厨贵人（0:显示。1:关闭）
     */
    private int tianChuGuiRen;

    /**
     * 月德贵人（0:显示。1:关闭）
     */
    private int yueDeGuiRen;

    /**
     * 天德贵人（0:显示。1:关闭）
     */
    private int tianDeGuiRen;

    /**
     * 唐符国印（0:显示。1:关闭）
     */
    private int tangFuGuoYin;

    /**
     * 天元禄（0:显示。1:关闭）
     */
    private int tianYuanLu;

    /**
     * 华盖（0:显示。1:关闭）
     */
    private int huaGai;

    /**
     * 驿马（0:显示。1:关闭）
     */
    private int yiMa;

    /**
     * 天马（0:显示。1:关闭）
     */
    private int tianMa;

    /**
     * 禄马（0:显示。1:关闭）
     */
    private int luMa;

    /**
     * 劫煞（0:显示。1:关闭）
     */
    private int jieSha;

    /**
     * 将星（0:显示。1:关闭）
     */
    private int jiangXing;

    /**
     * 咸池（0:显示。1:关闭）
     */
    private int xianChi;

    /**
     * 天喜（0:显示。1:关闭）
     */
    private int tianXi;

    /**
     * 灾煞（0:显示。1:关闭）
     */
    private int zaiSha;

    /**
     * 天医（0:显示。1:关闭）
     */
    private int tianYi;

    /**
     * 谋星（0:显示。1:关闭）
     */
    private int mouXing;

    /**
     * 皇恩（0:显示。1:关闭）
     */
    private int huangEn;

    /**
     * 阳刃（0:显示。1:关闭）
     */
    private int yangRen;

    /**
     * 飞刃（0:显示。1:关闭）
     */
    private int feiRen;

//*******************************************************************************************************************************

    /**
     * 初始化设置
     */
    public LiuYaoShenShaSetting() {

        this.taiJiGuiRen = 0; // 太极贵人（默认→ 显示）
        this.tianYiGuiRen = 0; // 天乙贵人（默认→ 显示）
        this.fuXingGuiRen = 0; // 福星贵人（默认→ 显示）
        this.wenChangGuiRen = 0; // 文昌贵人（默认→ 显示）
        this.tianChuGuiRen = 0; // 天厨贵人（默认→ 显示）
        this.yueDeGuiRen = 0; // 月德贵人（默认→ 显示）
        this.tianDeGuiRen = 0; // 天德贵人（默认→ 显示）
        this.tangFuGuoYin = 0; // 唐符国印（默认→ 显示）
        this.tianYuanLu = 0; // 天元禄（默认→ 显示）
        this.huaGai = 0; // 华盖（默认→ 显示）
        this.yiMa = 0; // 驿马（默认→ 显示）
        this.tianMa = 0; // 天马（默认→ 显示）
        this.luMa = 0; // 禄马（默认→ 显示）
        this.jieSha = 0; // 劫煞（默认→ 显示）
        this.jiangXing = 0; // 将星（默认→ 显示）
        this.xianChi = 0; // 咸池（默认→ 显示）
        this.tianXi = 0; // 天喜（默认→ 显示）
        this.zaiSha = 0; // 灾煞（默认→ 显示）
        this.tianYi = 0; // 天医（默认→ 显示）
        this.mouXing = 0; // 谋星（默认→ 显示）
        this.huangEn = 0; // 皇恩（默认→ 显示）
        this.yangRen = 0; // 阳刃（默认→ 显示）
        this.feiRen = 0; // 飞刃（默认→ 显示）

    }

//===============================================================================================================================

    /**
     * 太极贵人
     *
     * @param taiJiGuiRen 太极贵人（0:显示。1:关闭）
     */
    public void setTaiJiGuiRen(int taiJiGuiRen) {
        this.taiJiGuiRen = (taiJiGuiRen == 0 || taiJiGuiRen == 1) ? taiJiGuiRen : 0;
    }

    /**
     * 天乙贵人
     *
     * @param tianYiGuiRen 天乙贵人（0:显示。1:关闭）
     */
    public void setTianYiGuiRen(int tianYiGuiRen) {
        this.tianYiGuiRen = (tianYiGuiRen == 0 || tianYiGuiRen == 1) ? tianYiGuiRen : 0;
    }

    /**
     * 福星贵人
     *
     * @param fuXingGuiRen 福星贵人（0:显示。1:关闭）
     */
    public void setFuXingGuiRen(int fuXingGuiRen) {
        this.fuXingGuiRen = (fuXingGuiRen == 0 || fuXingGuiRen == 1) ? fuXingGuiRen : 0;
    }

    /**
     * 文昌贵人
     *
     * @param wenChangGuiRen 文昌贵人（0:显示。1:关闭）
     */
    public void setWenChangGuiRen(int wenChangGuiRen) {
        this.wenChangGuiRen = (wenChangGuiRen == 0 || wenChangGuiRen == 1) ? wenChangGuiRen : 0;
    }

    /**
     * 天厨贵人
     *
     * @param tianChuGuiRen 天厨贵人（0:显示。1:关闭）
     */
    public void setTianChuGuiRen(int tianChuGuiRen) {
        this.tianChuGuiRen = (tianChuGuiRen == 0 || tianChuGuiRen == 1) ? tianChuGuiRen : 0;
    }

    /**
     * 月德贵人
     *
     * @param yueDeGuiRen 月德贵人（0:显示。1:关闭）
     */
    public void setYueDeGuiRen(int yueDeGuiRen) {
        this.yueDeGuiRen = (yueDeGuiRen == 0 || yueDeGuiRen == 1) ? yueDeGuiRen : 0;
    }

    /**
     * 天德贵人
     *
     * @param tianDeGuiRen 天德贵人（0:显示。1:关闭）
     */
    public void setTianDeGuiRen(int tianDeGuiRen) {
        this.tianDeGuiRen = (tianDeGuiRen == 0 || tianDeGuiRen == 1) ? tianDeGuiRen : 0;
    }

    /**
     * 唐符国印
     *
     * @param tangFuGuoYin 唐符国印（0:显示。1:关闭）
     */
    public void setTangFuGuoYin(int tangFuGuoYin) {
        this.tangFuGuoYin = (tangFuGuoYin == 0 || tangFuGuoYin == 1) ? tangFuGuoYin : 0;
    }

    /**
     * 天元禄
     *
     * @param tianYuanLu 天元禄（0:显示。1:关闭）
     */
    public void setTianYuanLu(int tianYuanLu) {
        this.tianYuanLu = (tianYuanLu == 0 || tianYuanLu == 1) ? tianYuanLu : 0;
    }

    /**
     * 华盖
     *
     * @param huaGai 华盖（0:显示。1:关闭）
     */
    public void setHuaGai(int huaGai) {
        this.huaGai = (huaGai == 0 || huaGai == 1) ? huaGai : 0;
    }

    /**
     * 驿马
     *
     * @param yiMa 驿马（0:显示。1:关闭）
     */
    public void setYiMa(int yiMa) {
        this.yiMa = (yiMa == 0 || yiMa == 1) ? yiMa : 0;
    }

    /**
     * 天马
     *
     * @param tianMa 天马（0:显示。1:关闭）
     */
    public void setTianMa(int tianMa) {
        this.tianMa = (tianMa == 0 || tianMa == 1) ? tianMa : 0;
    }

    /**
     * 禄马
     *
     * @param luMa 禄马（0:显示。1:关闭）
     */
    public void setLuMa(int luMa) {
        this.luMa = (luMa == 0 || luMa == 1) ? luMa : 0;
    }

    /**
     * 劫煞
     *
     * @param jieSha 劫煞（0:显示。1:关闭）
     */
    public void setJieSha(int jieSha) {
        this.jieSha = (jieSha == 0 || jieSha == 1) ? jieSha : 0;
    }

    /**
     * 将星
     *
     * @param jiangXing 将星（0:显示。1:关闭）
     */
    public void setJiangXing(int jiangXing) {
        this.jiangXing = (jiangXing == 0 || jiangXing == 1) ? jiangXing : 0;
    }

    /**
     * 咸池
     *
     * @param xianChi 咸池（0:显示。1:关闭）
     */
    public void setXianChi(int xianChi) {
        this.xianChi = (xianChi == 0 || xianChi == 1) ? xianChi : 0;
    }

    /**
     * 天喜
     *
     * @param tianXi 天喜（0:显示。1:关闭）
     */
    public void setTianXi(int tianXi) {
        this.tianXi = (tianXi == 0 || tianXi == 1) ? tianXi : 0;
    }

    /**
     * 灾煞
     *
     * @param zaiSha 灾煞（0:显示。1:关闭）
     */
    public void setZaiSha(int zaiSha) {
        this.zaiSha = (zaiSha == 0 || zaiSha == 1) ? zaiSha : 0;
    }

    /**
     * 天医
     *
     * @param tianYi 天医（0:显示。1:关闭）
     */
    public void setTianYi(int tianYi) {
        this.tianYi = (tianYi == 0 || tianYi == 1) ? tianYi : 0;
    }

    /**
     * 谋星
     *
     * @param mouXing 谋星（0:显示。1:关闭）
     */
    public void setMouXing(int mouXing) {
        this.mouXing = (mouXing == 0 || mouXing == 1) ? mouXing : 0;
    }

    /**
     * 皇恩
     *
     * @param huangEn 皇恩（0:显示。1:关闭）
     */
    public void setHuangEn(int huangEn) {
        this.huangEn = (huangEn == 0 || huangEn == 1) ? huangEn : 0;
    }

    /**
     * 阳刃
     *
     * @param yangRen 阳刃（0:显示。1:关闭）
     */
    public void setYangRen(int yangRen) {
        this.yangRen = (yangRen == 0 || yangRen == 1) ? yangRen : 0;
    }

    /**
     * 飞刃
     *
     * @param feiRen 飞刃（0:显示。1:关闭）
     */
    public void setFeiRen(int feiRen) {
        this.feiRen = (feiRen == 0 || feiRen == 1) ? feiRen : 0;
    }


}
