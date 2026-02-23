package xuan.core.bazi.utils;

import java.util.*;

import xuan.core.bazi.settings.BaZiShenShaSetting;
import xuan.utils.DateUtil;
import xuan.utils.CommonUtil;
import com.nlf.calendar.JieQi;
import com.nlf.calendar.Lunar;
import com.nlf.calendar.Solar;
import xuan.core.bazi.maps.BaZiJiChuMap;
import com.nlf.calendar.eightchar.DaYun;
import com.nlf.calendar.eightchar.LiuNian;
import com.nlf.calendar.eightchar.LiuYue;
import com.nlf.calendar.eightchar.XiaoYun;
import org.apache.commons.lang3.StringUtils;
import xuan.core.bazi.maps.BaZiDaYunLiuNianMap;

/**
 * 八字 - 大运流年工具
 *
 * @author 善待
 */
public class BaZiDaYunLiuNianUtil {

    /**
     * 八字 - 神煞设置
     */
    private BaZiShenShaSetting baZiShenShaSetting;

    /**
     * 公历日期
     */
    private Solar solar;
    /**
     * 农历日期
     */
    private Lunar lunar;
    /**
     * 性别（0:女。1:男）
     */
    private int sex;
    /**
     * 季节
     */
    private String jiJie;
    /**
     * 起运流派类型（0:按天数和时辰数计算：3天1年、1天4个月、1时辰10天。1:按分钟数计算：4320分=1年、360分=1月、12分=1天、1分=2小时）
     */
    private int qiYunLiuPaiType;
    /**
     * 年干支纳音五行
     */
    private String yearGanZhiNaYinWuXing;

    /**
     * 日干
     */
    private String dayGan;
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
     * 大运
     */
    private List<List<String>> daYun;
    /**
     * 流年
     */
    private List<List<String>> liuNian;
    /**
     * 小运
     */
    private List<List<String>> xiaoYun;
    /**
     * 流月
     */
    private List<List<String>> liuYue;
    /**
     * 流日
     */
    private List<List<String>> liuRi;
    /**
     * 流时
     */
    private List<List<String>> liuShi;

    /**
     * 大运原数据
     */
    protected DaYun[] daYunSource;
    /**
     * 流年原数据
     */
    protected LiuNian[] liuNianSource;
    /**
     * 小运持续的年数
     */
    protected int xiaoYunYearSum;

    /**
     * 年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接时刻作为新年的开始）
     */
    protected int yearGanZhiType;
    /**
     * 月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
     */
    protected int monthGanZhiType;
    /**
     * 日干支类型（0:晚子时日柱按明天。1:晚子时日柱按当天）
     */
    protected int dayGanZhiType;

//****************************************************************************************************************************************************

    /**
     * 初始化
     *
     * @param baZiShenShaSetting 八字 - 神煞设置
     * @param solarDate          公历出生日期
     * @param sex                性别（0:女。1:男）
     * @param qiYunLiuPaiType    起运流派类型（0:按天数和时辰数计算：3天1年、1天4个月、1时辰10天。1:按分钟数计算：4320分=1年、360分=1月、12分=1天、1分=2小时）
     * @param yearGanZhiType     年干支类型（0:以正月初一作为新年的开始。1:以立春当天作为新年的开始。2:以立春交接时刻作为新年的开始）
     * @param monthGanZhiType    月干支类型（0:以节交接当天起算。1:以节交接时刻起算）
     * @param dayGanZhiType      日干支类型（0:晚子时日柱按明天。1:晚子时日柱按当天）
     */
    public BaZiDaYunLiuNianUtil(BaZiShenShaSetting baZiShenShaSetting, Date solarDate, int sex, int qiYunLiuPaiType, int yearGanZhiType, int monthGanZhiType, int dayGanZhiType) {

        this.baZiShenShaSetting = baZiShenShaSetting;

        this.solar = new Solar(solarDate); // 初始化公历日期
        this.lunar = this.solar.getLunar(); // 初始化农历日期
        this.sex = sex; // 性别（0:女。1:男）
        if (yearGanZhiType == 0) {
            this.yearGanZhi = this.lunar.getYearInGanZhi(); // 以正月初一作为新年的开始
            this.yearGanZhiNaYinWuXing = BaZiJiChuMap.NA_YIN.get(this.yearGanZhi).substring(2, 3); // 年干支纳音
        } else if (yearGanZhiType == 1) {
            this.yearGanZhi = this.lunar.getYearInGanZhiByLiChun(); // 以立春当天作为新年的开始
            this.yearGanZhiNaYinWuXing = BaZiJiChuMap.NA_YIN.get(this.yearGanZhi).substring(2, 3); // 年干支纳音
        } else {
            this.yearGanZhi = this.lunar.getYearInGanZhiExact(); // 以立春交接的时刻作为新年的开始
            this.yearGanZhiNaYinWuXing = BaZiJiChuMap.NA_YIN.get(this.yearGanZhi).substring(2, 3); // 年干支纳音
        }
        this.monthGanZhi = (monthGanZhiType == 0) ? this.lunar.getMonthInGanZhi() : this.lunar.getMonthInGanZhiExact(); // 以节交接当天起算 \ 以节交接时刻起算
        this.dayGanZhi = (dayGanZhiType == 0) ? this.lunar.getDayInGanZhiExact() : this.lunar.getDayInGanZhiExact2(); // 晚子时日干算明天 \ 晚子时日干算当天
        this.dayGan = (StringUtils.isNotBlank(this.dayGanZhi) && this.dayGanZhi.length() == 2) ? this.dayGanZhi.substring(0, 1) : CommonUtil.EMPTY1; // 日干
        this.hourGanZhi = lunar.getTimeInGanZhi(); // 时干支
        this.qiYunLiuPaiType = qiYunLiuPaiType; // 起运流派类型
        this.jiJie = (!"".equals(this.lunar.getSeason()) && this.lunar.getSeason().length() >= 2) ? this.lunar.getSeason().substring(1, 2) : "春"; // 季节
        this.yearGanZhiType = yearGanZhiType; // 年干支类型
        this.monthGanZhiType = monthGanZhiType; // 月干支类型
        this.dayGanZhiType = dayGanZhiType; // 日干支类型

    }

//====================================================================================================================================================

    /**
     * 获取大运
     *
     * @param daYunLunShu 一共需要计算多少轮大运
     * @return 大运（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历年、年龄、公历日期）
     */
    public List<List<String>> getDaYun(int daYunLunShu) {

        initializeDaYun(daYunLunShu); // 初始化大运

        return this.daYun;

    }

    /**
     * 获取流年
     *
     * @param daYunLunShu 一共需要计算多少轮大运
     * @param daYunLun    第几轮大运
     * @return 流年（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历年、年龄、公历日期）
     */
    public List<List<String>> getLiuNian(int daYunLunShu, int daYunLun) {

        initializeDaYun(daYunLunShu); // 初始化大运
        initializeLiuNian(daYunLun); // 初始化流年

        return this.liuNian;

    }

    /**
     * 获取小运
     *
     * @param daYunLunShu 一共需要计算多少轮大运
     * @param daYunLun    第几轮大运
     * @return 小运（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历年、年龄、公历日期）
     */
    public List<List<String>> getXiaoYun(int daYunLunShu, int daYunLun) {

        initializeDaYun(daYunLunShu); // 初始化大运
        initializeXiaoYun(daYunLun); // 初始化小运

        return this.xiaoYun;

    }

    /**
     * 获取流月
     *
     * @param daYunLunShu 一共需要计算多少轮大运
     * @param daYunLun    第几轮大运
     * @param liuNianLun  流年轮
     * @param solarYear   公历年
     * @return 流月（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历几月几日、十二节农历月、十二节、公历日期）
     */
    public List<List<String>> getLiuYue(int daYunLunShu, int daYunLun, int liuNianLun, int solarYear) {

        initializeDaYun(daYunLunShu); // 初始化大运
        initializeLiuNian(daYunLun); // 初始化流年
        initializeLiuYue(daYunLun, liuNianLun, solarYear); // 初始化流月

        return this.liuYue;

    }

    /**
     * 获取流日
     *
     * @param solarYear  公历年
     * @param solarMonth 公历月
     * @return 流日（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历日、农历日、公历日期）
     */
    public List<List<String>> getLiuRi(int solarYear, int solarMonth) {

        initializeLiuRi(solarYear, solarMonth); // 初始化流日

        return this.liuRi;

    }

    /**
     * 获取流时
     *
     * @param solarYear  公历年
     * @param solarMonth 公历月
     * @param solarDay   公历日
     * @return 流时（主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历时、汉代命名、公历日期）
     */
    public List<List<String>> getLiuShi(int solarYear, int solarMonth, int solarDay) {

        initializeLiuShi(solarYear, solarMonth, solarDay); // 初始化流时

        return this.liuShi;

    }

//----------------------------------------------------------------------------------------------------------------------------------------------------

    /**
     * 初始化大运
     *
     * @param daYunLunShu 一共需要计算多少轮大运
     */
    private void initializeDaYun(int daYunLunShu) {

        Map<String, String> shiErZhangShengMap = BaZiJiChuMap.SHI_ER_ZHANG_SHENG; // 十二长生（天干+地支为键）
        Map<String, List<String>> diZhiCangGanMap = BaZiJiChuMap.DI_ZHI_CANG_GAN; // 地支藏干（地支为键）
        Map<String, String> shiShenMap = BaZiJiChuMap.SHI_SHEN; // 十神（日干+其他天干\地支为键）
        Map<String, String> kongWangMap = BaZiJiChuMap.KONG_WANG; // 空亡（干支为键）
        Map<String, String> naYinMap = BaZiJiChuMap.NA_YIN; // 纳音（干支为键）

        List<List<String>> daYun = new ArrayList<>(); // 大运

        // 1、添加全部大运数据
        DaYun[] daYunSource = this.lunar.getEightChar().getYun(this.sex, this.qiYunLiuPaiType).getDaYun(daYunLunShu); // 获取大运原数据
        String zhuXing = ""; // 主星
        String tianGan = ""; // 天干
        String diZhi = ""; // 地支
        String ziZuo = ""; // 自坐
        String xingYun = ""; // 星运
        String cangGan = ""; // 藏干
        String fuXing = ""; // 副星
        String kongWang = ""; // 空亡
        String naYin = ""; // 纳音
        String shenSha = ""; // 神煞
        for (DaYun dy : daYunSource) {
            String ganZhi = dy.getGanZhi(); // 干支
            if (StringUtils.isNotBlank(ganZhi) && ganZhi.length() >= 2) {
                tianGan = ganZhi.substring(0, 1); // 天干
                diZhi = ganZhi.substring(1, 2); // 地支
                zhuXing = shiShenMap.get(this.dayGan + tianGan); // 主星
                ziZuo = shiErZhangShengMap.get(ganZhi); // 自坐
                xingYun = shiErZhangShengMap.get(this.dayGan + diZhi); // 星运
                List<String> cangGanList = diZhiCangGanMap.get(diZhi); // 藏干集合
                cangGan = String.join(CommonUtil.EMPTY1, cangGanList);  // 藏干
                List<String> fuXingList = new ArrayList<>(); // 副星集合
                for (String item : cangGanList) {
                    fuXingList.add(shiShenMap.get(this.dayGan + item));
                }
                fuXing = String.join(CommonUtil.EMPTY1, fuXingList);  // 副星
                kongWang = kongWangMap.get(ganZhi); // 空亡
                naYin = naYinMap.get(ganZhi); // 纳音
                BaZiShenShaUtil shenShaUtil = new BaZiShenShaUtil(this.baZiShenShaSetting, this.sex, this.jiJie, this.yearGanZhiNaYinWuXing, this.yearGanZhi, this.monthGanZhi, this.dayGanZhi, this.hourGanZhi, ganZhi);
                shenSha = String.join(CommonUtil.EMPTY1, shenShaUtil.getArbitraryGanZhiShenSha()); // 神煞
            }
            String solarDate = DateUtil.getDateStr(dy.getStartYear(), 1, 1, 0, 0, 0); // 公历日期
            daYun.add(Arrays.asList(zhuXing, tianGan, diZhi, cangGan, fuXing, ziZuo, xingYun, kongWang, naYin, shenSha, String.valueOf(dy.getStartYear()), String.valueOf(dy.getStartAge()), solarDate)); // 主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历年、年龄、公历日期
        }

        // 2、计算并设置小运持续的年数（根据公历年计算）
        this.xiaoYunYearSum = Integer.parseInt(daYun.get(1).get(10)) - Integer.parseInt(daYun.get(0).get(10));

        // 3、处理第一轮大运的年龄数据
        if (this.xiaoYunYearSum < 1) {
            // 3.1、若小运持续年数小于1年，则将大运的第一轮数据的岁数重置为：1~10
            daYun.set(0, daYun.get(0)).set(11, "1~10");
        } else if (this.xiaoYunYearSum == 1) {
            // 3.2、若小运持续年数等于1年，则将大运的第一轮数据的岁数重置为：1
            daYun.set(0, daYun.get(0)).set(11, String.valueOf(this.xiaoYunYearSum));
        } else {
            // 3.3、若小运持续年数大于1年，则将大运的第一轮数据的岁数重置为：1~?
            daYun.set(0, daYun.get(0)).set(11, "1~" + this.xiaoYunYearSum);
        }

        // 4、处理全部大运岁数
        for (int i = 1; i < daYun.size() - 1; i++) {
            int startAge = Integer.parseInt(daYun.get(i).get(11));
            int endAge = startAge + 9;
            daYun.set(i, daYun.get(i)).set(11, startAge + "~" + endAge);
        }

        // 5、设置数据
        this.daYun = daYun; // 大运
        this.daYunSource = daYunSource; // 大运原数据

    }

    /**
     * 初始化流年
     *
     * @param daYunLun 第几轮大运
     */
    private void initializeLiuNian(int daYunLun) {

        Map<String, String> shiErZhangShengMap = BaZiJiChuMap.SHI_ER_ZHANG_SHENG; // 十二长生（天干+地支为键）
        Map<String, List<String>> diZhiCangGanMap = BaZiJiChuMap.DI_ZHI_CANG_GAN; // 地支藏干（地支为键）
        Map<String, String> shiShenMap = BaZiJiChuMap.SHI_SHEN; // 十神（日干+其他天干\地支为键）
        Map<String, String> kongWangMap = BaZiJiChuMap.KONG_WANG; // 空亡（干支为键）
        Map<String, String> naYinMap = BaZiJiChuMap.NA_YIN; // 纳音（干支为键）

        // 1、添加全部流年原数据
        LiuNian[] liuNianSource = null;
        List<List<String>> liuNianSourceTemporary = new ArrayList<>(); // 临时存储流年原数据
        for (DaYun dy : this.daYunSource) {
            liuNianSource = dy.getLiuNian(10); // 获取流年
            for (LiuNian ln : liuNianSource) {
                liuNianSourceTemporary.add(Arrays.asList(ln.getGanZhi(), String.valueOf(ln.getYear()), String.valueOf(ln.getAge()))); // 干支、公历年、年龄
            }
        }

        // 2、计算开始索引与结束索引
        int start = 0; // 开始索引
        int end; // 结束索引
        if (daYunLun == 1) {
            if (this.xiaoYunYearSum == 0) {
                end = 10; // 结束索引
            } else {
                end = this.xiaoYunYearSum; // 结束索引
            }
        } else {
            start = this.xiaoYunYearSum + 10 * (daYunLun - 2); // 开始索引
            end = start + 10; // 结束索引
        }

        // 3、添加流年数据
        String zhuXing = ""; // 主星
        String tianGan = ""; // 天干
        String diZhi = ""; // 地支
        String ziZuo = ""; // 自坐
        String xingYun = ""; // 星运
        String cangGan = ""; // 藏干
        String fuXing = ""; // 副星
        String kongWang = ""; // 空亡
        String naYin = ""; // 纳音
        String shenSha = ""; // 神煞
        List<List<String>> liuNian = new ArrayList<>(); // 流年
        for (int i = start; i < end; i++) {
            List<String> ln = liuNianSourceTemporary.get(i);
            String ganZhi = ln.get(0); // 干支
            if (StringUtils.isNotBlank(ganZhi) && ganZhi.length() >= 2) {
                tianGan = ganZhi.substring(0, 1); // 天干
                diZhi = ganZhi.substring(1, 2); // 地支
                zhuXing = shiShenMap.get(this.dayGan + tianGan); // 主星
                ziZuo = shiErZhangShengMap.get(ganZhi); // 自坐
                xingYun = shiErZhangShengMap.get(this.dayGan + diZhi); // 星运
                List<String> cangGanList = diZhiCangGanMap.get(diZhi); // 藏干集合
                cangGan = String.join(CommonUtil.EMPTY1, cangGanList);  // 藏干
                List<String> fuXingList = new ArrayList<>(); // 副星集合
                for (String item : cangGanList) {
                    fuXingList.add(shiShenMap.get(this.dayGan + item));
                }
                fuXing = String.join(CommonUtil.EMPTY1, fuXingList);  // 副星
                kongWang = kongWangMap.get(ganZhi); // 空亡
                naYin = naYinMap.get(ganZhi); // 纳音
                BaZiShenShaUtil shenShaUtil = new BaZiShenShaUtil(this.baZiShenShaSetting, this.sex, this.jiJie, this.yearGanZhiNaYinWuXing, this.yearGanZhi, this.monthGanZhi, this.dayGanZhi, this.hourGanZhi, ganZhi);
                shenSha = String.join(CommonUtil.EMPTY1, shenShaUtil.getArbitraryGanZhiShenSha()); // 神煞
            }
            String solarDate = DateUtil.getDateStr(Integer.parseInt(ln.get(1)), 1, 1, 0, 0, 0); // 公历日期
            liuNian.add(Arrays.asList(zhuXing, tianGan, diZhi, cangGan, fuXing, ziZuo, xingYun, kongWang, naYin, shenSha, ln.get(1), ln.get(2), solarDate)); // 主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历年、年龄、公历日期
        }

        // 4、设置数据
        this.liuNian = liuNian; // 流年
        this.liuNianSource = liuNianSource; // 流年原数据

    }

    /**
     * 初始化小运
     *
     * @param daYunLun 第几轮大运
     */
    private void initializeXiaoYun(int daYunLun) {

        Map<String, String> shiErZhangShengMap = BaZiJiChuMap.SHI_ER_ZHANG_SHENG; // 十二长生（天干+地支为键）
        Map<String, List<String>> diZhiCangGanMap = BaZiJiChuMap.DI_ZHI_CANG_GAN; // 地支藏干（地支为键）
        Map<String, String> shiShenMap = BaZiJiChuMap.SHI_SHEN; // 十神（日干+其他天干\地支为键）
        Map<String, String> kongWangMap = BaZiJiChuMap.KONG_WANG; // 空亡（干支为键）
        Map<String, String> naYinMap = BaZiJiChuMap.NA_YIN; // 纳音（干支为键）

        // 1、添加全部小运数据
        List<List<String>> xiaoYunSourceTemporary = new ArrayList<>(); // 临时存储小运原数据
        for (DaYun dy : this.daYunSource) {
            XiaoYun[] xiaoYunSource = dy.getXiaoYun(10); // 获取小运
            for (XiaoYun xy : xiaoYunSource) {
                xiaoYunSourceTemporary.add(Arrays.asList(xy.getGanZhi(), String.valueOf(xy.getYear()), String.valueOf(xy.getAge()))); // 干支、公历年、年龄
            }
        }

        // 2、计算开始索引与结束索引
        int start = 0; // 开始索引
        int end; // 结束索引
        if (daYunLun == 1) {
            if (this.xiaoYunYearSum == 0) {
                end = 10; // 结束索引
            } else {
                end = this.xiaoYunYearSum; // 结束索引
            }
        } else {
            start = this.xiaoYunYearSum + 10 * (daYunLun - 2); // 开始索引
            end = start + 10; // 结束索引
        }

        // 3、添加小运数据
        String zhuXing = ""; // 主星
        String tianGan = ""; // 天干
        String diZhi = ""; // 地支
        String ziZuo = ""; // 自坐
        String xingYun = ""; // 星运
        String cangGan = ""; // 藏干
        String fuXing = ""; // 副星
        String kongWang = ""; // 空亡
        String naYin = ""; // 纳音
        String shenSha = ""; // 神煞
        List<List<String>> xiaoYun = new ArrayList<>(); // 小运
        for (int i = start; i < end; i++) {
            List<String> xy = xiaoYunSourceTemporary.get(i);
            String ganZhi = xy.get(0); // 干支
            if (StringUtils.isNotBlank(ganZhi) && ganZhi.length() >= 2) {
                tianGan = ganZhi.substring(0, 1); // 天干
                diZhi = ganZhi.substring(1, 2); // 地支
                zhuXing = shiShenMap.get(this.dayGan + tianGan); // 主星
                ziZuo = shiErZhangShengMap.get(ganZhi); // 自坐
                xingYun = shiErZhangShengMap.get(this.dayGan + diZhi); // 星运
                List<String> cangGanList = diZhiCangGanMap.get(diZhi); // 藏干集合
                cangGan = String.join(CommonUtil.EMPTY1, cangGanList);  // 藏干
                List<String> fuXingList = new ArrayList<>(); // 副星集合
                for (String item : cangGanList) {
                    fuXingList.add(shiShenMap.get(this.dayGan + item));
                }
                fuXing = String.join(CommonUtil.EMPTY1, fuXingList);  // 副星
                kongWang = kongWangMap.get(ganZhi); // 空亡
                naYin = naYinMap.get(ganZhi); // 纳音
                BaZiShenShaUtil shenShaUtil = new BaZiShenShaUtil(this.baZiShenShaSetting, this.sex, this.jiJie, this.yearGanZhiNaYinWuXing, this.yearGanZhi, this.monthGanZhi, this.dayGanZhi, this.hourGanZhi, ganZhi);
                shenSha = String.join(CommonUtil.EMPTY1, shenShaUtil.getArbitraryGanZhiShenSha()); // 神煞
            }
            String solarDate = DateUtil.getDateStr(Integer.parseInt(xy.get(1)), 1, 1, 0, 0, 0); // 公历日期
            xiaoYun.add(Arrays.asList(zhuXing, tianGan, diZhi, cangGan, fuXing, ziZuo, xingYun, kongWang, naYin, shenSha, xy.get(1), xy.get(2), solarDate)); // 主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历年、年龄、公历日期
        }

        // 4、设置数据
        this.xiaoYun = xiaoYun; // 小运

    }

    /**
     * 初始化流月
     *
     * @param daYunLun          第几轮大运
     * @param liuNianXiaoYunLun 流年\小运轮
     * @param solarYear         公历年
     */
    private void initializeLiuYue(int daYunLun, int liuNianXiaoYunLun, int solarYear) {

        Map<String, String> shiErZhangShengMap = BaZiJiChuMap.SHI_ER_ZHANG_SHENG; // 十二长生（天干+地支为键）
        Map<String, List<String>> diZhiCangGanMap = BaZiJiChuMap.DI_ZHI_CANG_GAN; // 地支藏干（地支为键）
        Map<String, String> shiShenMap = BaZiJiChuMap.SHI_SHEN; // 十神（日干+其他天干\地支为键）
        Map<String, String> kongWangMap = BaZiJiChuMap.KONG_WANG; // 空亡（干支为键）
        Map<String, String> naYinMap = BaZiJiChuMap.NA_YIN; // 纳音（干支为键）

        // 1、添加全部大运流月数据
        Map<String, List<String>> liuYueShiErJieSolarMonthDay = computeLiuYueShiErJieSolarMonthDay(solarYear); // 计算流月的十二节公历月日、农历月、十二节
        List<String> solarMonthDay = liuYueShiErJieSolarMonthDay.get("solarMonthDay"); // 十二节公历月日
        List<String> lunarMonth = liuYueShiErJieSolarMonthDay.get("lunarMonth"); // 十二节农历月
        List<String> jie = liuYueShiErJieSolarMonthDay.get("jie"); // 十二节
        List<List<String>> daYunLiuYueTemporary = new ArrayList<>(); // 临时存储全部大运流月
        for (LiuNian ln : this.liuNianSource) {
            LiuYue[] liuYueSource = ln.getLiuYue(); // 获取流月
            for (int i = 0; i < liuYueSource.length; i++) {
                daYunLiuYueTemporary.add(Arrays.asList(liuYueSource[i].getGanZhi(), BaZiDaYunLiuNianMap.SHI_ER_SOLAR_MONTH[i], solarMonthDay.get(i), lunarMonth.get(i), jie.get(i))); // 干支、公历月、公历几月几日、十二节农历月、十二节
            }
        }

        // 2、遍历大运流月，查找月干支所处的索引
        Lunar lunar = new Solar(this.solar.getYear(), 2, 10).getLunar();
        String liChunMonthGanZhi = (this.monthGanZhiType == 0) ? lunar.getMonthInGanZhi() : lunar.getMonthInGanZhiExact(); // 以节交接当天起算 \ 以节交接时刻起算
        int dayOffset = 0; // 天数偏移量
        int monthGanZhiIndex = 0; // 月干支所处的索引
        if (!"立春".equals(lunar.getPrevJie().toString())) {
            if ("小寒".equals(lunar.getPrevJie().toString())) {
                // 2.1、上一节为[小寒]时，则向后推算日期，直至当天节为[立春]停止
                while (true) {
                    dayOffset++;
                    lunar = lunar.next(dayOffset); // 向后n天
                    if (!"小寒".equals(lunar.getPrevJie().toString())) {
                        liChunMonthGanZhi = (this.monthGanZhiType == 0) ? lunar.getMonthInGanZhi() : lunar.getMonthInGanZhiExact(); // 以节交接当天起算 \ 以节交接时刻起算
                        break;
                    }
                }
            } else if ("惊蛰".equals(lunar.getNextJie().toString())) {
                // 2.2、下一节为[惊蛰]时，则向前推算日期，直至当天节为[立春]停止
                while (true) {
                    dayOffset++;
                    lunar = lunar.next(-dayOffset); // 向前n天
                    if (!"惊蛰".equals(lunar.getPrevJie().toString())) {
                        liChunMonthGanZhi = (this.monthGanZhiType == 0) ? lunar.getMonthInGanZhi() : lunar.getMonthInGanZhiExact(); // 以节交接当天起算 \ 以节交接时刻起算
                        break;
                    }
                }
            }
        }
        for (int i = 0; i < daYunLiuYueTemporary.size(); i++) {
            String ganZhi = daYunLiuYueTemporary.get(i).get(0);
            if (ganZhi.equals(liChunMonthGanZhi)) {
                monthGanZhiIndex = i;
                break;
            } else {
                monthGanZhiIndex++;
            }
        }
        if (monthGanZhiIndex == 1 || this.xiaoYunYearSum == 10) monthGanZhiIndex = 0;

        // 3、从月干支索引处向后依次添加流月数据
        List<List<String>> xiaoYunLiuYueTemporary = new ArrayList<>(); // 临时存储全部小运流月
        int xiaoYunLiuYueCount = this.xiaoYunYearSum * 12;
        for (int i = 0; i < xiaoYunLiuYueCount; i++) {
            int count = i + monthGanZhiIndex;
            if (count > 119) {
                i = 0;
                count = 59;
                if (xiaoYunLiuYueCount > 59) xiaoYunLiuYueCount -= 59;
            } else {
                count = i + monthGanZhiIndex;
            }
            List<String> ly = daYunLiuYueTemporary.get(count);
            xiaoYunLiuYueTemporary.add(Arrays.asList(ly.get(0), ly.get(1), ly.get(2), ly.get(3), ly.get(4))); // 干支、公历月、公历几月几日、十二节农历月、十二节
        }

        String zhuXing = ""; // 主星
        String tianGan = ""; // 天干
        String diZhi = ""; // 地支
        String ziZuo = ""; // 自坐
        String xingYun = ""; // 星运
        String cangGan = ""; // 藏干
        String fuXing = ""; // 副星
        String kongWang = ""; // 空亡
        String naYin = ""; // 纳音
        String shenSha = ""; // 神煞
        List<List<String>> liuYue = new ArrayList<>(); // 流月

        // 4、添加流月数据
        int start; // 开始索引
        int end; // 结束索引
        if (daYunLun == 1) {
            if (this.xiaoYunYearSum == 0) {
                // 4.1、第一轮大运，若小运持续的年数为0，则获取第一轮大运中第一到十二轮流月数据（说明：当起运时间小于1年时才会出现这种情况）
                for (int i = 0; i < 12; i++) {
                    List<String> ly = daYunLiuYueTemporary.get(i);
                    String ganZhi = ly.get(0); // 干支
                    if (StringUtils.isNotBlank(ganZhi) && ganZhi.length() >= 2) {
                        tianGan = ganZhi.substring(0, 1); // 天干
                        diZhi = ganZhi.substring(1, 2); // 地支
                        zhuXing = shiShenMap.get(this.dayGan + tianGan); // 主星
                        ziZuo = shiErZhangShengMap.get(ganZhi); // 自坐
                        xingYun = shiErZhangShengMap.get(this.dayGan + diZhi); // 星运
                        List<String> cangGanList = diZhiCangGanMap.get(diZhi); // 藏干集合
                        cangGan = String.join(CommonUtil.EMPTY1, cangGanList);  // 藏干
                        List<String> fuXingList = new ArrayList<>(); // 副星集合
                        for (String item : cangGanList) {
                            fuXingList.add(shiShenMap.get(this.dayGan + item));
                        }
                        fuXing = String.join(CommonUtil.EMPTY1, fuXingList);  // 副星
                        kongWang = kongWangMap.get(ganZhi); // 空亡
                        naYin = naYinMap.get(ganZhi); // 纳音
                        BaZiShenShaUtil shenShaUtil = new BaZiShenShaUtil(this.baZiShenShaSetting, this.sex, this.jiJie, this.yearGanZhiNaYinWuXing, this.yearGanZhi, this.monthGanZhi, this.dayGanZhi, this.hourGanZhi, ganZhi);
                        shenSha = String.join(CommonUtil.EMPTY1, shenShaUtil.getArbitraryGanZhiShenSha()); // 神煞
                    }
                    if (i == 11) solarYear++;
                    String solarDate = DateUtil.getDateStr(solarYear, Integer.parseInt(ly.get(1)), 1, 0, 0, 0); // 公历日期
                    liuYue.add(Arrays.asList(zhuXing, tianGan, diZhi, cangGan, fuXing, ziZuo, xingYun, kongWang, naYin, shenSha, ly.get(2), ly.get(3), ly.get(4), solarDate)); // 主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历几月几日、十二节农历月、十二节、公历日期
                }
            } else {
                // 4.2、第一轮大运，小运持续的年数不为0，则获取小运的十二轮流月数据
                start = 12 * (liuNianXiaoYunLun - 1); // 开始索引
                end = start + 12; // 结束索引
                for (int i = start; i < end; i++) {
                    List<String> ly = xiaoYunLiuYueTemporary.get(i);
                    String ganZhi = ly.get(0); // 干支
                    if (StringUtils.isNotBlank(ganZhi) && ganZhi.length() >= 2) {
                        tianGan = ganZhi.substring(0, 1); // 天干
                        diZhi = ganZhi.substring(1, 2); // 地支
                        zhuXing = shiShenMap.get(this.dayGan + tianGan); // 主星
                        ziZuo = shiErZhangShengMap.get(ganZhi); // 自坐
                        xingYun = shiErZhangShengMap.get(this.dayGan + diZhi); // 星运
                        List<String> cangGanList = diZhiCangGanMap.get(diZhi); // 藏干集合
                        cangGan = String.join(CommonUtil.EMPTY1, cangGanList);  // 藏干
                        List<String> fuXingList = new ArrayList<>(); // 副星集合
                        for (String item : cangGanList) {
                            fuXingList.add(shiShenMap.get(this.dayGan + item));
                        }
                        fuXing = String.join(CommonUtil.EMPTY1, fuXingList);  // 副星
                        kongWang = kongWangMap.get(ganZhi); // 空亡
                        naYin = naYinMap.get(ganZhi); // 纳音
                        BaZiShenShaUtil shenShaUtil = new BaZiShenShaUtil(this.baZiShenShaSetting, this.sex, this.jiJie, this.yearGanZhiNaYinWuXing, this.yearGanZhi, this.monthGanZhi, this.dayGanZhi, this.hourGanZhi, ganZhi);
                        shenSha = String.join(CommonUtil.EMPTY1, shenShaUtil.getArbitraryGanZhiShenSha()); // 神煞
                    }
                    if (i == end - 1) solarYear++;
                    String solarDate = DateUtil.getDateStr(solarYear, Integer.parseInt(ly.get(1)), 1, 0, 0, 0); // 公历日期
                    liuYue.add(Arrays.asList(zhuXing, tianGan, diZhi, cangGan, fuXing, ziZuo, xingYun, kongWang, naYin, shenSha, ly.get(2), ly.get(3), ly.get(4), solarDate)); // 主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历几月几日、十二节农历月、十二节、公历日期
                }
            }
        } else {
            // 4.3、非第一轮大运
            start = (12 * (liuNianXiaoYunLun - 1)) == 120 ? 0 : 12 * (liuNianXiaoYunLun - 1); // 开始索引
            end = start + 12; // 结束索引
            for (int i = start; i < end; i++) {
                List<String> ly = daYunLiuYueTemporary.get(i);
                String ganZhi = ly.get(0); // 干支
                if (StringUtils.isNotBlank(ganZhi) && ganZhi.length() >= 2) {
                    tianGan = ganZhi.substring(0, 1); // 天干
                    diZhi = ganZhi.substring(1, 2); // 地支
                    zhuXing = shiShenMap.get(this.dayGan + tianGan); // 主星
                    ziZuo = shiErZhangShengMap.get(ganZhi); // 自坐
                    xingYun = shiErZhangShengMap.get(this.dayGan + diZhi); // 星运
                    List<String> cangGanList = diZhiCangGanMap.get(diZhi); // 藏干集合
                    cangGan = String.join(CommonUtil.EMPTY1, cangGanList);  // 藏干
                    List<String> fuXingList = new ArrayList<>(); // 副星集合
                    for (String item : cangGanList) {
                        fuXingList.add(shiShenMap.get(this.dayGan + item));
                    }
                    fuXing = String.join(CommonUtil.EMPTY1, fuXingList);  // 副星
                    kongWang = kongWangMap.get(ganZhi); // 空亡
                    naYin = naYinMap.get(ganZhi); // 纳音
                    BaZiShenShaUtil shenShaUtil = new BaZiShenShaUtil(this.baZiShenShaSetting, this.sex, this.jiJie, this.yearGanZhiNaYinWuXing, this.yearGanZhi, this.monthGanZhi, this.dayGanZhi, this.hourGanZhi, ganZhi);
                    shenSha = String.join(CommonUtil.EMPTY1, shenShaUtil.getArbitraryGanZhiShenSha()); // 神煞
                }
                if (i == end - 1) solarYear++;
                String solarDate = DateUtil.getDateStr(solarYear, Integer.parseInt(ly.get(1)), 1, 0, 0, 0); // 公历日期
                liuYue.add(Arrays.asList(zhuXing, tianGan, diZhi, cangGan, fuXing, ziZuo, xingYun, kongWang, naYin, shenSha, ly.get(2), ly.get(3), ly.get(4), solarDate)); // 主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历几月几日、十二节农历月、十二节、公历日期
            }
        }

        // 5、设置数据
        this.liuYue = liuYue;

    }

    /**
     * 初始化流日
     *
     * @param solarYear  公历年
     * @param solarMonth 公历月
     */
    private void initializeLiuRi(int solarYear, int solarMonth) {

        Map<String, String> shiErZhangShengMap = BaZiJiChuMap.SHI_ER_ZHANG_SHENG; // 十二长生（天干+地支为键）
        Map<String, List<String>> diZhiCangGanMap = BaZiJiChuMap.DI_ZHI_CANG_GAN; // 地支藏干（地支为键）
        Map<String, String> shiShenMap = BaZiJiChuMap.SHI_SHEN; // 十神（日干+其他天干\地支为键）
        Map<String, String> kongWangMap = BaZiJiChuMap.KONG_WANG; // 空亡（干支为键）
        Map<String, String> naYinMap = BaZiJiChuMap.NA_YIN; // 纳音（干支为键）

        // 1、根据公历年、公历月初始化日期
        Lunar lunar = new Lunar(new Solar(solarYear, solarMonth, 15));

        // 2、获取上一节、下一节
        JieQi prevJie = lunar.getPrevJie(true); // 上一节（按天计算）
        JieQi nextJie = lunar.getNextJie(true); // 下一节（按天计算）

        // 3、获取上一节的农历日期
        Lunar startLunar = prevJie.getSolar().getLunar();

        String zhuXing = ""; // 主星
        String tianGan = ""; // 天干
        String diZhi = ""; // 地支
        String ziZuo = ""; // 自坐
        String xingYun = ""; // 星运
        String cangGan = ""; // 藏干
        String fuXing = ""; // 副星
        String kongWang = ""; // 空亡
        String naYin = ""; // 纳音
        String shenSha = ""; // 神煞
        List<List<String>> liuRi = new ArrayList<>(); // 流日

        // 4、添加流日数据
        for (int i = 0; i < 60; i++) {
            Solar nextSolar = startLunar.next(i).getSolar(); // 向后推第n天的公历日期
            Lunar nextLunar = startLunar.next(i); // 向后推第n天的农历日期
            // 若未到下一节则继续添加
            if (!nextLunar.getJie().equals(nextJie.toString())) {
                String ganZhi = (this.dayGanZhiType == 0) ? nextLunar.getDayInGanZhiExact() : nextLunar.getDayInGanZhiExact2(); // 日干支（晚子时日柱算明天\晚子时日柱算当天）
                if (StringUtils.isNotBlank(ganZhi) && ganZhi.length() >= 2) {
                    tianGan = ganZhi.substring(0, 1); // 天干
                    diZhi = ganZhi.substring(1, 2); // 地支
                    zhuXing = shiShenMap.get(this.dayGan + tianGan); // 主星
                    ziZuo = shiErZhangShengMap.get(ganZhi); // 自坐
                    xingYun = shiErZhangShengMap.get(this.dayGan + diZhi); // 星运
                    List<String> cangGanList = diZhiCangGanMap.get(diZhi); // 藏干集合
                    cangGan = String.join(CommonUtil.EMPTY1, cangGanList);  // 藏干
                    List<String> fuXingList = new ArrayList<>(); // 副星集合
                    for (String item : cangGanList) {
                        fuXingList.add(shiShenMap.get(this.dayGan + item));
                    }
                    fuXing = String.join(CommonUtil.EMPTY1, fuXingList);  // 副星
                    kongWang = kongWangMap.get(ganZhi); // 空亡
                    naYin = naYinMap.get(ganZhi); // 纳音
                    BaZiShenShaUtil shenShaUtil = new BaZiShenShaUtil(this.baZiShenShaSetting, this.sex, this.jiJie, this.yearGanZhiNaYinWuXing, this.yearGanZhi, this.monthGanZhi, this.dayGanZhi, this.hourGanZhi, ganZhi);
                    shenSha = String.join(CommonUtil.EMPTY1, shenShaUtil.getArbitraryGanZhiShenSha()); // 神煞
                }
                String solarDate = DateUtil.getDateStr(nextSolar.getYear(), nextSolar.getMonth(), nextSolar.getDay(), 0, 0, 0); // 公历日期
                liuRi.add(Arrays.asList(zhuXing, tianGan, diZhi, ziZuo, xingYun, cangGan, fuXing, kongWang, naYin, shenSha, nextSolar.getDay() + "日", nextLunar.getDayInChinese(), solarDate)); // 主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历日、农历日、公历日期
            } else break;
        }

        // 5、设置数据
        this.liuRi = liuRi;

    }

    /**
     * 初始化流时
     *
     * @param solarYear  公历年
     * @param solarMonth 公历月
     * @param solarDay   公历日
     */
    private void initializeLiuShi(int solarYear, int solarMonth, int solarDay) {

        Map<String, String> shiErZhangShengMap = BaZiJiChuMap.SHI_ER_ZHANG_SHENG; // 十二长生（天干+地支为键）
        Map<String, List<String>> diZhiCangGanMap = BaZiJiChuMap.DI_ZHI_CANG_GAN; // 地支藏干（地支为键）
        Map<String, String> shiShenMap = BaZiJiChuMap.SHI_SHEN; // 十神（日干+其他天干\地支为键）
        Map<String, String> kongWangMap = BaZiJiChuMap.KONG_WANG; // 空亡（干支为键）
        Map<String, String> naYinMap = BaZiJiChuMap.NA_YIN; // 纳音（干支为键）

        String zhuXing = ""; // 主星
        String tianGan = ""; // 天干
        String diZhi = ""; // 地支
        String ziZuo = ""; // 自坐
        String xingYun = ""; // 星运
        String cangGan = ""; // 藏干
        String fuXing = ""; // 副星
        String kongWang = ""; // 空亡
        String naYin = ""; // 纳音
        String shenSha = ""; // 神煞
        List<List<String>> liuShi = new ArrayList<>(); // 流时

        // 1、添加流时数据
        int hour = 0; // 小时数
        Solar solar = new Solar(solarYear, solarMonth, solarDay);
        for (int i = 0; i < 12; i++) {
            // 通过公历日期初始化
            Lunar lunar = new Lunar(DateUtil.timeToDate(solar.getYear(), solar.getMonth(), solar.getDay(), hour, 0, 0));
            String ganZhi = lunar.getTimeInGanZhi(); // 干支
            if (StringUtils.isNotBlank(ganZhi) && ganZhi.length() >= 2) {
                tianGan = ganZhi.substring(0, 1); // 天干
                diZhi = ganZhi.substring(1, 2); // 地支
                zhuXing = shiShenMap.get(this.dayGan + tianGan); // 主星
                ziZuo = shiErZhangShengMap.get(ganZhi); // 自坐
                xingYun = shiErZhangShengMap.get(this.dayGan + diZhi); // 星运
                List<String> cangGanList = diZhiCangGanMap.get(diZhi); // 藏干集合
                cangGan = String.join(CommonUtil.EMPTY1, cangGanList);  // 藏干
                List<String> fuXingList = new ArrayList<>(); // 副星集合
                for (String item : cangGanList) {
                    fuXingList.add(shiShenMap.get(this.dayGan + item));
                }
                fuXing = String.join(CommonUtil.EMPTY1, fuXingList);  // 副星
                kongWang = kongWangMap.get(ganZhi); // 空亡
                naYin = naYinMap.get(ganZhi); // 纳音
                BaZiShenShaUtil shenShaUtil = new BaZiShenShaUtil(this.baZiShenShaSetting, this.sex, this.jiJie, this.yearGanZhiNaYinWuXing, this.yearGanZhi, this.monthGanZhi, this.dayGanZhi, this.hourGanZhi, ganZhi);
                shenSha = String.join(CommonUtil.EMPTY1, shenShaUtil.getArbitraryGanZhiShenSha()); // 神煞
            }
            String solarDate = DateUtil.getDateStr(solarYear, solarMonth, solarDay, BaZiDaYunLiuNianMap.SHI_ER_SHI_2[i], 0, 0); // 公历日期
            liuShi.add(Arrays.asList(zhuXing, tianGan, diZhi, cangGan, fuXing, ziZuo, xingYun, kongWang, naYin, shenSha, BaZiDaYunLiuNianMap.SHI_ER_SHI[i], BaZiDaYunLiuNianMap.DI_ZHI_HAN_MING[i], solarDate)); // 主星、天干、地支、藏干、副星、自坐、星运、空亡、纳音、神煞、公历时、汉代命名、公历日期
            hour += 2;
        }

        // 2、设置数据
        this.liuShi = liuShi;

    }

//----------------------------------------------------------------------------------------------------------------------------------------------------

    /**
     * 计算流月的计十二节公历月日、农历月、十二节
     *
     * @param solarYear 公历年
     * @return 十二节公历月日、农历月、十二节
     */
    protected Map<String, List<String>> computeLiuYueShiErJieSolarMonthDay(int solarYear) {

        Map<String, List<String>> map = new HashMap<>();
        List<String> solarMonthDay = new ArrayList<>(); // 保存十二节公历月日
        List<String> lunarMonth = new ArrayList<>(); // 保存十二节农历月
        List<String> jie = new ArrayList<>(); // 保存十二节

        Lunar lunar = new Solar(solarYear, 1, 1).getLunar();

        int i = 0; // 十二节索引
        int day = 0; // 向后查询的天数
        while (true) {
            Lunar nextLunar = lunar.next(day); // 向后第n天的农历日期
            if (nextLunar.getJie().equals(BaZiDaYunLiuNianMap.SHI_ER_JIE[i])) {
                Solar nextSolar = nextLunar.getSolar(); // 向后第n天的公历日期
                solarMonthDay.add(nextSolar.getMonth() + "/" + nextSolar.getDay()); // 十二节公历月日
                lunarMonth.add(nextLunar.getMonthInChinese() + "月"); // 十二节农历月
                jie.add(BaZiDaYunLiuNianMap.SHI_ER_JIE[i]); // 十二节
                map.put("solarMonthDay", solarMonthDay);
                map.put("lunarMonth", lunarMonth);
                map.put("jie", jie);
                i++;
                if (i > 11) break;
                day += 26;
            }
            day++;
        }

        return map;

    }


}
