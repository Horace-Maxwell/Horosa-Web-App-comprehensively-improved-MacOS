package xuan.core.qimen.zhuan.utils;

import xuan.core.qimen.zhuan.maps.QiMenZhuanPanJiChuMap;
import xuan.utils.CommonUtil;

import java.util.*;

/**
 * 转盘奇门 - 基础工具
 *
 * @author 善待
 */
public class QiMenZhuanPanJiChuUtil {

    /**
     * 获取值使
     * <p>
     * <p> 天禽星为值符时：一律用[死门]为值使</p>
     *
     * @return 值使
     */
    public static String getZhiShi1() {
        return "死门";
    }

    /**
     * 获取值使
     * <hr/>
     * <p> 天禽星为值符时：阳遁用[生门]为值使</p>
     * <p> 天禽星为值符时：阴遁用[死门]为值使</p>
     *
     * @param yinYangDun 阴阳遁
     * @return 值使
     */
    public static String getZhiShi2(String yinYangDun) {
        return "阳遁".equals(yinYangDun) ? "生门" : "死门";
    }

    /**
     * 获取值使
     * <hr/>
     * <p>天禽星为值符时：（冬至、小寒、大寒）三个节气，用[休门]为值使</p>
     * <p>天禽星为值符时：（立春，雨水，惊蛰）三个节气，用[生门]为值使</p>
     * <p>天禽星为值符时：（春分、清明、谷雨）三个节气，用[伤门]为值使</p>
     * <p>天禽星为值符时：（立夏、小满、芒种）三个节气，用[杜门]为值使</p>
     * <p>天禽星为值符时：（夏至、小暑、大暑）三个节气，用[景门]为值使</p>
     * <p>天禽星为值符时：（立秋、处暑、白露）三个节气，用[死门]为值使</p>
     * <p>天禽星为值符时：（秋分、寒露、霜降）三个节气，用[惊门]为值使</p>
     * <p>天禽星为值符时：（立冬、小雪、大雪）三个节气，用[开门]为值使</p>
     *
     * @param jieQi 节气
     * @return 值使
     */
    public static String getZhiShi3(String jieQi) {

        Map<Integer, List<String>> isBaMenMap = QiMenZhuanPanJiChuMap.IS_BA_MEN; // 根据二十四节气获取八门
        for (int i = 0; i < isBaMenMap.size(); i++) {
            for (int j = 0; j < isBaMenMap.get(i).size(); j++) {
                String s = isBaMenMap.get(i).get(j);
                if (s.equals(jieQi)) {
                    switch (i) {
                        case 0:
                            return "休门";
                        case 1:
                            return "生门";
                        case 2:
                            return "伤门";
                        case 3:
                            return "杜门";
                        case 4:
                            return "景门";
                        case 5:
                            return "死门";
                        case 6:
                            return "惊门";
                        case 7:
                            return "开门";
                    }
                }
            }
        }
        return "";

    }

    /**
     * 获取伏吟
     *
     * @param diPan                地盘
     * @param tianPan              天盘
     * @param renPan               人盘
     * @param shenPan              神盘
     * @param tianPanQiYiTianQinNo 天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
     * @return 伏吟
     */
    public static List<String> getFuYin(List<String> diPan, List<String> tianPan, List<String> renPan, List<String> shenPan, List<String> tianPanQiYiTianQinNo) {

        List<String> list = new ArrayList<>(); // 保存伏吟数据

        // 1、奇仪伏吟（判断宫位数据是否符合：坎一宫中的地盘奇仪和天盘奇仪是否相同）
        if (diPan.get(0).equals(tianPanQiYiTianQinNo.get(0))) {
            list.add("奇仪伏吟");
        }

        // 2、星伏吟（判断宫位数据是否符合：坎一宫有天蓬星，离九宫有天英星）
        if ("天蓬".equals(tianPan.get(0)) && "天英".equals(tianPan.get(8))) {
            list.add("九星伏吟");
        }

        // 3、门伏吟（判断宫位数据是否符合：坎一宫有休门，离九宫有景门）
        if ("休门".equals(renPan.get(0)) && "景门".equals(renPan.get(8))) {
            list.add("八门伏吟");
        }

        // 4、神伏吟（判断宫位数据是否符合：坎一宫有值符，离九宫有白虎）
        if ("值符".equals(shenPan.get(0)) && "白虎".equals(shenPan.get(8))) {
            list.add("八神伏吟");
        }

        return list;

    }

    /**
     * 获取反吟
     *
     * @param diPan                地盘
     * @param tianPan              天盘
     * @param renPan               人盘
     * @param shenPan              神盘
     * @param tianPanQiYiTianQinNo 天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
     * @return 反吟
     */
    public static List<String> getFanYin(List<String> diPan, List<String> tianPan, List<String> renPan, List<String> shenPan, List<String> tianPanQiYiTianQinNo) {

        List<String> list = new ArrayList<>(); // 保存反吟数据

        // 1、六仪反吟
        /*
            天盘甲子戊+地盘甲午辛
            天盘甲戌己+地盘甲辰壬
            天盘甲申庚+地盘甲寅癸
            天盘甲午辛+地盘甲子戊
            天盘甲辰壬+地盘甲戌己
            天盘甲寅癸+地盘甲申庚
         */

        for (int i = 0; i < 9; i++) {
            // 1.1、天盘甲子戊+地盘甲午辛
            if ("戊".equals(tianPanQiYiTianQinNo.get(i)) && "辛".equals(diPan.get(i))) {
                list.add("六仪反吟");
                break;
            }
            // 1.2、天盘甲戌己+地盘甲辰壬
            if ("己".equals(tianPanQiYiTianQinNo.get(i)) && "壬".equals(diPan.get(i))) {
                list.add("六仪反吟");
                break;
            }
            // 1.3、天盘甲申庚+地盘甲寅癸
            if ("庚".equals(tianPanQiYiTianQinNo.get(i)) && "癸".equals(diPan.get(i))) {
                list.add("六仪反吟");
                break;
            }
            // 1.4、天盘甲午辛+地盘甲子戊
            if ("辛".equals(tianPanQiYiTianQinNo.get(i)) && "戊".equals(diPan.get(i))) {
                list.add("六仪反吟");
                break;
            }
            // 1.5、天盘甲辰壬+地盘甲戌己
            if ("壬".equals(tianPanQiYiTianQinNo.get(i)) && "己".equals(diPan.get(i))) {
                list.add("六仪反吟");
                break;
            }
            // 1.6、天盘甲寅癸+地盘甲申庚
            if ("癸".equals(tianPanQiYiTianQinNo.get(i)) && "庚".equals(diPan.get(i))) {
                list.add("六仪反吟");
                break;
            }
        }

        // 2、星反吟（判断宫位数据是否符合：坎一宫有天英星，离九宫有天蓬星）
        if ("天英".equals(tianPan.get(0)) && "天蓬".equals(tianPan.get(8))) {
            list.add("九星反吟");
        }

        // 3、门反吟（判断宫位数据是否符合：坎一宫有景门，离九宫有休门）
        if ("景门".equals(renPan.get(0)) && "休门".equals(renPan.get(8))) {
            list.add("八门反吟");
        }

        // 4、神反吟（判断宫位数据是否符合：坎一宫有白虎，离九宫有值符）
        if ("白虎".equals(shenPan.get(0)) && "值符".equals(shenPan.get(8))) {
            list.add("八神反吟");
        }

        return list;

    }

    /**
     * 获取六仪击刑
     *
     * @param tianPanQiYiTianQinYes 天盘奇仪与落宫地支的关系，只包含[天禽星]携带的奇仪（1~9宫）
     * @param tianPanQiYiTianQinNo  天盘奇仪与落宫地支的关系，不包含[天禽星]携带的奇仪（1~9宫）
     * @return 六仪击刑
     */
    public static List<String> getLiuYiJiXing(List<String> tianPanQiYiTianQinYes, List<String> tianPanQiYiTianQinNo) {

        /*
            1、甲子戊：'戊'落震三宫，子卯相刑。（东方）
            2、甲戌己：'己'落坤二宫，戌未相刑。（西南方）
            3、甲申庚：'庚'落艮八宫，申寅相刑。（东北方）
            4、甲午辛：'辛'落离九宫，午午自刑。（南方）
            5、甲辰壬：'壬'落巽四宫，辰辰自刑。（东南方）
            6、甲寅癸：'癸'落巽四宫，寅巳相刑。（东南方）
        */

        Map<String, String> liuYiJiXingMap = QiMenZhuanPanJiChuMap.LIU_YI_JI_XING; // 六仪击刑（天盘干+宫位为键）

        List<String> list = new ArrayList<>(); // 保存六仪击刑

        for (int i = 0; i < 9; i++) {
            String jiXingTianPanQiYiTianQinYes = liuYiJiXingMap.get(tianPanQiYiTianQinYes.get(i) + (i + 1));
            String jiXingTianPanQiYiTianQinNo = liuYiJiXingMap.get(tianPanQiYiTianQinNo.get(i) + (i + 1));
            if (null != jiXingTianPanQiYiTianQinYes) list.add(jiXingTianPanQiYiTianQinYes);
            if (null != jiXingTianPanQiYiTianQinNo) list.add(jiXingTianPanQiYiTianQinNo);
        }

        return list;

    }

    /**
     * 获取奇仪入墓
     *
     * @param tianPanQiYiTianQinYes 天盘奇仪与落宫地支的关系，只包含[天禽星]携带的奇仪（1~9宫）
     * @param tianPanQiYiTianQinNo  天盘奇仪与落宫地支的关系，不包含[天禽星]携带的奇仪（1~9宫）
     * @return 奇仪入墓
     */
    public static List<String> getQiYiRuMu(List<String> tianPanQiYiTianQinYes, List<String> tianPanQiYiTianQinNo) {

        /*
            1、'甲'落坤二宫。（西南方）
            2、'乙'落乾六宫。（西北方）
            3、'丙'落乾六宫。（西北方）
            4、'丁'落艮八宫。（东北方）
            5、'戊'落乾六宫。（西北方）
            6、'己'落艮八宫。（东北方）
            7、'庚'落艮八宫。（东北方）
            8、'辛'落巽四宫。（东南方）
            9、'壬'落巽四宫。（东南方）
            10、'癸'落坤二宫。（西南方）
        */

        Map<String, String> qiYiRuMuMap = QiMenZhuanPanJiChuMap.QI_YI_RU_MU; // 奇仪入墓（天盘干+宫位为键）

        List<String> list = new ArrayList<>(); // 保存奇仪入墓

        for (int i = 0; i < 9; i++) {
            String ruMuTianPanQiYiTianQinYes = qiYiRuMuMap.get(tianPanQiYiTianQinYes.get(i) + (i + 1));
            String ruMuTianPanQiYiTianQinNo = qiYiRuMuMap.get(tianPanQiYiTianQinNo.get(i) + (i + 1));
            if (null != ruMuTianPanQiYiTianQinYes) list.add(ruMuTianPanQiYiTianQinYes);
            if (null != ruMuTianPanQiYiTianQinNo) list.add(ruMuTianPanQiYiTianQinNo);
        }

        return list;

    }

    /**
     * 获取六仪击邢、奇仪入墓状态
     *
     * @param tianPanQiYiTianQinYes 天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
     * @param tianPanQiYiTianQinNo  天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
     * @return 六仪击邢、奇仪入墓状态
     */
    public static Map<String, List<String>> getJiXingRuMuStatus(List<String> tianPanQiYiTianQinYes, List<String> tianPanQiYiTianQinNo) {

        Map<String, String> liuYiJiXingMap = QiMenZhuanPanJiChuMap.LIU_YI_JI_XING; // 六仪击刑（天盘干+宫位为键）
        Map<String, String> qiYiRuMuMap = QiMenZhuanPanJiChuMap.QI_YI_RU_MU; // 奇仪入墓（天盘干+宫位为键）

        Map<String, List<String>> map = new HashMap<>();
        List<String> jiXingRuMuLinkTianPanQiYiTianQinYes = new ArrayList<>(); // 保存六仪击刑、奇仪入墓状态，只包含[天禽星]携带的奇仪（1~9宫）
        List<String> jiXingRuMuLinkTianPanQiYiTianQinNo = new ArrayList<>(); // 保存六仪击刑、奇仪入墓状态，不包含[天禽星]携带的奇仪（1~9宫）

        // 1、计算每一个宫位的击邢、入墓
        for (int i = 0; i < 9; i++) {
            // 1.1、判断只包含[天禽星]携带的奇仪是否构成六仪击邢与奇仪入墓
            if (null != tianPanQiYiTianQinYes) {
                String jiXingTianPanQiYiTianQinYes = liuYiJiXingMap.get(tianPanQiYiTianQinYes.get(i) + (i + 1)); // 六仪击邢
                String qiYiRuMuTianPanQiYiTianQinYes = qiYiRuMuMap.get(tianPanQiYiTianQinYes.get(i) + (i + 1)); // 奇仪入墓
                if (null == jiXingTianPanQiYiTianQinYes && null == qiYiRuMuTianPanQiYiTianQinYes) {
                    jiXingRuMuLinkTianPanQiYiTianQinYes.add("");
                } else if (null != jiXingTianPanQiYiTianQinYes && null != qiYiRuMuTianPanQiYiTianQinYes) {
                    jiXingRuMuLinkTianPanQiYiTianQinYes.add("击邢入墓");
                } else {
                    if (null != jiXingTianPanQiYiTianQinYes) {
                        jiXingRuMuLinkTianPanQiYiTianQinYes.add("击邢");
                    } else {
                        jiXingRuMuLinkTianPanQiYiTianQinYes.add("入墓");
                    }
                }
                map.put("jiXingRuMuLinkTianPanQiYiTianQinYes", jiXingRuMuLinkTianPanQiYiTianQinYes);
            }
            // 1.2、判断不包含[天禽星]携带的奇仪是否构成六仪击邢与奇仪入墓
            if (null != tianPanQiYiTianQinNo) {
                String jiXingTianPanQiYiTianQinNo = liuYiJiXingMap.get(tianPanQiYiTianQinNo.get(i) + (i + 1)); // 六仪击邢
                String qiYiRuMuTianPanQiYiTianQinNo = qiYiRuMuMap.get(tianPanQiYiTianQinNo.get(i) + (i + 1)); // 奇仪入墓
                if (null == jiXingTianPanQiYiTianQinNo && null == qiYiRuMuTianPanQiYiTianQinNo) {
                    jiXingRuMuLinkTianPanQiYiTianQinNo.add("");
                } else if (null != jiXingTianPanQiYiTianQinNo && null != qiYiRuMuTianPanQiYiTianQinNo) {
                    jiXingRuMuLinkTianPanQiYiTianQinNo.add("击邢入墓");
                } else {
                    if (null != jiXingTianPanQiYiTianQinNo) {
                        jiXingRuMuLinkTianPanQiYiTianQinNo.add("击邢");
                    } else {
                        jiXingRuMuLinkTianPanQiYiTianQinNo.add("入墓");
                    }
                }
                map.put("jiXingRuMuLinkTianPanQiYiTianQinNo", jiXingRuMuLinkTianPanQiYiTianQinNo);
            }
        }

        return map;

    }

    /**
     * 获取门迫状态
     *
     * @param renPan 人盘
     * @return 门迫状态
     */
    public static List<String> getMenPoStatus(List<String> renPan) {

        Map<String, String> menPoMap = QiMenZhuanPanJiChuMap.MEN_PO; // 门迫（八门+宫位为键）

        List<String> list = new ArrayList<>(); // 保存门迫状态（1~9宫）

        // 1、计算每一个宫位的门迫
        for (int i = 0; i < 9; i++) {
            // 1.1、判断八门是否构成门迫
            String menPo = menPoMap.get(renPan.get(i) + (i + 1));
            if (null == menPo) {
                list.add("");
            } else {
                list.add("门迫");
            }
        }

        return list;

    }

    /**
     * 获取十干克应
     *
     * @param diPan                 地盘
     * @param tianPanQiYiTianQinYes 天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
     * @param tianPanQiYiTianQinNo  天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
     * @return 十干克应
     */
    public static List<List<String>> getShiGanKeYing(List<String> diPan, List<String> tianPanQiYiTianQinYes, List<String> tianPanQiYiTianQinNo) {

        Map<List<String>, List<String>> shiGanKeYingMap = QiMenZhuanPanJiChuMap.SHI_GAN_KE_YING; // 十干克应

        // 计算九宫中的[天盘天干+地盘天干]对应的十干克应关系
        List<List<String>> list = new ArrayList<>();
        for (int i = 0; i < 9; i++) {
            List<String> tianQinYes = Arrays.asList(tianPanQiYiTianQinYes.get(i), diPan.get(i)); // 天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪
            List<String> tianQinNo = Arrays.asList(tianPanQiYiTianQinNo.get(i), diPan.get(i)); // 天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪
            if (i != 4) {
                List<String> keYingTianQinNoList = shiGanKeYingMap.get(tianQinNo); // 天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪的十干克应关系
                String keYingTianQinNo = tianQinNo.get(0) + "+" + tianQinNo.get(1) + "（" + keYingTianQinNoList.get(0) + "）→" + keYingTianQinNoList.get(1);
                List<String> keYingTianQinYesList = shiGanKeYingMap.get(tianQinYes); // 天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪的十干克应关系
                if (null != keYingTianQinYesList) {
                    // 该宫位中存在两个天盘天干，追加十干克应数据
                    String keYingTianQinYes = tianQinYes.get(0) + "+" + tianQinYes.get(1) + "（" + keYingTianQinYesList.get(0) + "）→" + keYingTianQinYesList.get(1);
                    list.add(Arrays.asList(keYingTianQinYes, keYingTianQinNo));
                } else {
                    list.add(Collections.singletonList(keYingTianQinNo));
                }
            } else {
                list.add(Collections.singletonList("")); // 中五宫
            }
        }

        return list;

    }

    /**
     * 获取八门克应
     *
     * @param renPan                人盘
     * @param diPan                 地盘
     * @param tianPanQiYiTianQinYes 天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
     * @param tianPanQiYiTianQinNo  天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
     * @return 八门克应
     */
    public static List<List<String>> getBaMenKeYing(List<String> renPan, List<String> diPan, List<String> tianPanQiYiTianQinYes, List<String> tianPanQiYiTianQinNo) {

        String[] baMenInitial = QiMenZhuanPanJiChuMap.BA_MEN_INITIAL;// 八门原始宫位（1~9宫）
        Map<List<String>, String> baMenKeYingMap = QiMenZhuanPanJiChuMap.BA_MEN_KE_YING; // 八门克应

        List<String> menMen = new ArrayList<>(); // 保存[人盘八门+地盘八门]的生克制化关系
        List<String> menDiGan = new ArrayList<>(); // 保存[人盘八门+地盘天干]的生克制化关系
        List<String> menTianGanTianPanQiYiTianQinYes = new ArrayList<>(); // 保存[人盘八门+天盘天干]的生克制化关系（只包含[天禽星]携带的奇仪）
        List<String> menTianGanTianPanQiYiTianQinNo = new ArrayList<>(); // 保存[人盘八门+天盘天干]的生克制化关系（不包含[天禽星]携带的奇仪）
        for (int i = 0; i < 9; i++) {
            String newMen = renPan.get(i); // 人盘八门
            // 1、计算[人盘八门+地盘八门]的生克制化关系
            String oldMen = baMenInitial[i]; // 宫位中的原始八门
            List<String> menAndMen = Arrays.asList(newMen, oldMen); // 例如：开+休
            if (null != baMenKeYingMap.get(menAndMen)) {
                menMen.add(newMen + "+" + oldMen + "→" + baMenKeYingMap.get(menAndMen)); // 例如→ 开门+休门：主见贵人财喜及开张铺店，贸易大吉。
            } else {
                menMen.add("");
            }
            // 2、计算[人盘八门+地盘天干]的生克制化关系
            String diPanGan = diPan.get(i); // 地盘天干
            List<String> menAndDiGan = Arrays.asList(newMen, diPanGan); // 例如：开门+乙
            if (null != baMenKeYingMap.get(menAndDiGan)) {
                menDiGan.add(newMen + "+" + diPanGan + "→" + baMenKeYingMap.get(menAndDiGan)); // 例如→ 开门+乙:小财可求。
            } else {
                menDiGan.add("");
            }
            // 3、计算[人盘八门+天盘天干]的生克制化关系
            String tianGanTianPanQiYiTianQinYes = tianPanQiYiTianQinYes.get(i); // 只包含[天禽星]携带的天干
            String tianGanTianPanQiYiTianQinNo = tianPanQiYiTianQinNo.get(i); // 不包含[天禽星]携带的天干
            List<String> menAndTianGanTianPanQiYiTianQinYes = Arrays.asList(newMen, tianGanTianPanQiYiTianQinYes); // 例如：开门+乙
            List<String> menAndTianGanExTTq = Arrays.asList(newMen, tianGanTianPanQiYiTianQinNo); // 例如：开门+乙
            if (null != baMenKeYingMap.get(menAndTianGanTianPanQiYiTianQinYes)) {
                menTianGanTianPanQiYiTianQinYes.add(newMen + "+" + tianGanTianPanQiYiTianQinYes + "→" + baMenKeYingMap.get(menAndTianGanTianPanQiYiTianQinYes)); // 例如→ 开门+乙:小财可求。
            } else {
                menTianGanTianPanQiYiTianQinYes.add("");
            }
            if (null != baMenKeYingMap.get(menAndTianGanExTTq)) {
                menTianGanTianPanQiYiTianQinNo.add(newMen + "+" + tianGanTianPanQiYiTianQinNo + "→" + baMenKeYingMap.get(menAndTianGanExTTq)); // 例如→ 开门+乙:小财可求。
            } else {
                menTianGanTianPanQiYiTianQinNo.add("");
            }
        }

        // 4、整合[人盘八门+地盘八门]、[人盘八门+地盘天干]、[人盘八门+天盘天干]的生克制化关系
        List<List<String>> list = new ArrayList<>();
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                if (null != menTianGanTianPanQiYiTianQinYes.get(i)) {
                    list.add(Arrays.asList(menMen.get(i), menDiGan.get(i), menTianGanTianPanQiYiTianQinYes.get(i), menTianGanTianPanQiYiTianQinNo.get(i)));
                } else {
                    list.add(Arrays.asList(menMen.get(i), menDiGan.get(i), menTianGanTianPanQiYiTianQinNo.get(i)));
                }
            } else {
                list.add(Collections.singletonList("")); // 中五宫
            }
        }

        // 5、去除空数据、重复数据
        List<List<String>> newList = new ArrayList<>();
        for (List<String> value : list) {
            List<String> newListOne = new ArrayList<>();
            for (String item : value) {
                if (!"".equals(item)) newListOne.add(item);
            }
            newList.add(CommonUtil.removeDuplicatesList(newListOne));
        }

        // 6、返回数据
        return newList;

    }

    /**
     * 获取八门静应\动应
     *
     * @param menDongOrJing 八门静应\八门动应
     * @param renPan        人盘
     * @return 八门静应\八门动应
     */
    public static List<List<String>> getMenDongJingYing(Map<List<String>, String> menDongOrJing, List<String> renPan) {

        String[] baMenInitial = QiMenZhuanPanJiChuMap.BA_MEN_INITIAL; // 八门初始位置

        List<List<String>> list = new ArrayList<>(); // 存放[门+门]信息
        for (int i = 0; i < renPan.size(); i++) {
            if (i != 4) {
                String oldMen = renPan.get(i); // 人盘八门
                String newMen = baMenInitial[i]; // 原宫八门
                List<String> men = Arrays.asList(oldMen, newMen);
                if (null != menDongOrJing.get(men)) {
                    list.add(Collections.singletonList(oldMen + "+" + newMen + "→" + menDongOrJing.get(men)));
                } else {
                    list.add(Collections.singletonList(""));
                }
            } else {
                list.add(Collections.singletonList("")); // 中五宫
            }
        }

        return list;

    }

    /**
     * 获取星门克应
     *
     * @param tianPan 天盘
     * @param renPan  人盘
     * @return 星门克应
     */
    public static List<List<String>> getXingMenKeYing(List<String> tianPan, List<String> renPan) {

        Map<List<String>, String> xingMenKeYingMap = QiMenZhuanPanJiChuMap.XING_MEN_KE_YING; // 星门克应

        List<String> listOne = new ArrayList<>(); // 存放单宫的[九星+八门]对应信息
        List<List<String>> listAll = new ArrayList<>(); // 存放九宫的[九星+八门]对应信息
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                String xing = tianPan.get(i).substring(0, 1); // 天 或 芮
                if ("天".equals(xing)) {
                    // 1.1、宫位中不包含'天禽星'
                    List<String> xingMen = Arrays.asList(tianPan.get(i), renPan.get(i));
                    listAll.add(Collections.singletonList(tianPan.get(i) + "星+" + renPan.get(i) + "→" + xingMenKeYingMap.get(xingMen)));
                } else {
                    // 1.2、宫位中包含'天芮星'和'天禽星'
                    List<String> xingMen = Arrays.asList("天芮", renPan.get(i));
                    listOne.add("天芮星+" + renPan.get(i) + "→" + xingMenKeYingMap.get(xingMen));
                    listOne.add("天禽星+" + renPan.get(i) + "→" + xingMenKeYingMap.get(xingMen));
                    listAll.add(listOne);
                }
            } else {
                listAll.add(Collections.singletonList("")); // 中五宫
            }
        }

        // 2、返回数据
        return listAll;

    }

    /**
     * 获取九星时应
     *
     * @param hourZhi 时支
     * @param tianPan 天盘
     * @return 九星时应
     */
    public static List<List<String>> getJiuXingShiYing(String hourZhi, List<String> tianPan) {

        Map<List<String>, String> jiuXingShiYingMap = QiMenZhuanPanJiChuMap.JIU_XING_SHI_YING; // 九星时应

        List<String> listOne = new ArrayList<>(); // 存放单宫的[九星+时辰]对应信息
        List<List<String>> listAll = new ArrayList<>(); // 存放九宫的[九星+时辰]对应信息
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                String xing = tianPan.get(i).substring(0, 1); // 天 或 芮
                if ("天".equals(xing)) {
                    // 1.1、宫位中不包含'天禽星'
                    List<String> xingMen = Arrays.asList(tianPan.get(i), hourZhi);
                    listAll.add(Collections.singletonList(tianPan.get(i) + "星值" + hourZhi + "时→" + jiuXingShiYingMap.get(xingMen)));
                } else {
                    // 1.2、宫位中包含'天芮星'和'天禽星'
                    List<String> tianRui = Arrays.asList("天芮", hourZhi);
                    List<String> tianQin = Arrays.asList("天禽", hourZhi);
                    listOne.add("天芮星值" + hourZhi + "时→" + jiuXingShiYingMap.get(tianRui));
                    listOne.add("天禽星值" + hourZhi + "时→" + jiuXingShiYingMap.get(tianQin));
                    listAll.add(listOne);
                }
            } else {
                listAll.add(Collections.singletonList("")); // 中五宫
            }
        }

        return listAll;

    }

    /**
     * 获取八卦旺衰（根据季节计算）
     *
     * @param jiJie 季节
     * @return 八卦旺衰
     */
    public static List<List<String>> getBaGuaWangShuai(String jiJie) {

        String[] houTianBaGua = QiMenZhuanPanJiChuMap.HOU_TIAN_BA_GUA; // 八卦（后天八卦1~9宫）
        Map<String, Integer> siJiIndexMap = QiMenZhuanPanJiChuMap.SI_JI_INDEX; // 四季索引
        Map<String, List<String>> baGuaWangShuaiMap = QiMenZhuanPanJiChuMap.BA_GUA_WANG_SHUAI_JI_JIE; // 八卦旺衰（根据季节计算）

        List<List<String>> list = new ArrayList<>(); // 保存八卦旺衰
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                List<String> gongWeiList = baGuaWangShuaiMap.get(houTianBaGua[i]); // 每一宫位
                String wangShuai = gongWeiList.get(siJiIndexMap.get(jiJie)); // 每一宫位的八卦旺衰
                list.add(Arrays.asList(houTianBaGua[i] + "宫", wangShuai));
            } else {
                list.add(Arrays.asList("中宫", "")); // 中五宫
            }
        }

        return list;

    }

    /**
     * 获取八门旺衰（根据季节计算）
     *
     * @param renPan 人盘
     * @param jiJie  季节
     * @return 八门旺衰
     */
    public static List<List<String>> getBaMenWangShuai(List<String> renPan, String jiJie) {

        Map<String, Integer> siJiIndexMap = QiMenZhuanPanJiChuMap.SI_JI_INDEX; // 四季索引
        Map<String, List<String>> baMenWangShuaiMap = QiMenZhuanPanJiChuMap.BA_MEN_WANG_SHUAI_JI_JIE; // 八门旺衰（根据季节计算）

        List<List<String>> list = new ArrayList<>(); // 保存八门旺衰
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                String men = renPan.get(i); // 每一宫位中的门
                List<String> gongWeiList = baMenWangShuaiMap.get(men); // 每一宫位
                list.add(Arrays.asList(men, gongWeiList.get(siJiIndexMap.get(jiJie))));
            } else {
                list.add(Arrays.asList("中宫", "")); // 中五宫
            }
        }

        return list;

    }

    /**
     * 获取九星旺衰（根据月支计算）
     *
     * @param tianPan  天盘
     * @param monthZhi 月支
     * @return 九星旺衰
     */
    public static List<List<String>> getJiuXingWangShuai(List<String> tianPan, String monthZhi) {

        Map<String, Integer> diZhiIndexMap = QiMenZhuanPanJiChuMap.DI_ZHI_INDEX; // 十二地支索引
        Map<String, List<String>> jiuXingWangShuaiMap = QiMenZhuanPanJiChuMap.JIU_XING_WANG_SHUAI_MONTH_ZHI; // 九星旺衰（根据月支计算）

        List<List<String>> list = new ArrayList<>(); // 保存九星旺衰
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                String xing = tianPan.get(i); // 每一宫位中的星
                if (xing.equals("芮禽")) {
                    List<String> gongWeiList = jiuXingWangShuaiMap.get("天芮"); // 每一宫位
                    String wangShuai = gongWeiList.get(diZhiIndexMap.get(monthZhi)); // 每一宫位的九星旺衰
                    list.add(Arrays.asList("芮禽", wangShuai + wangShuai));
                } else {
                    List<String> gongWeiList = jiuXingWangShuaiMap.get(xing); // 每一宫位
                    String wangShuai = gongWeiList.get(diZhiIndexMap.get(monthZhi)); // 每一宫位的九星旺衰
                    list.add(Arrays.asList(xing, wangShuai));
                }
            } else {
                list.add(Arrays.asList("中宫", "")); // 中五宫
            }
        }

        return list;

    }

    /**
     * 获取八神落宫状态
     *
     * @param shenPan 神盘
     * @return 八神落宫状态
     */
    public static List<List<String>> getBaShenLuoGongStatus(List<String> shenPan) {

        Map<String, String> baShenJiXiongMap = QiMenZhuanPanJiChuMap.BA_SHEN_JI_XIONG; // 八神吉凶

        List<List<String>> list = new ArrayList<>(); // 保存八神落宫状态
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                String shen = shenPan.get(i); // 每一宫位中的神
                String gongWeiList = baShenJiXiongMap.get(shen); // 每一宫位的八神落宫状态
                list.add(Arrays.asList(shen, gongWeiList));
            } else {
                list.add(Arrays.asList("中宫", "")); // 中五宫
            }
        }

        // 2、返回数据
        return list;

    }

    /**
     * 获取八门落宫状态
     *
     * @param renPan 人盘
     * @return 八门落宫状态
     */
    public static List<List<String>> getBaMenLuoGongStatus(List<String> renPan) {

        Map<String, List<String>> baMenLuoGongStatusMap = QiMenZhuanPanJiChuMap.BA_MEN_LUO_GONG_STATUS; // 八门落宫状态

        List<List<String>> list = new ArrayList<>(); // 保存八门落宫状态
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                String men = renPan.get(i); // 每一宫位中的门
                List<String> gongWeiList = baMenLuoGongStatusMap.get(men); // 每一宫位
                String wangShuai = gongWeiList.get(i); // 每一宫位的八门落宫状态
                list.add(Arrays.asList(men, wangShuai));
            } else {
                list.add(Arrays.asList("中宫", "")); // 中五宫
            }
        }

        return list;

    }

    /**
     * 获取九星落宫状态
     *
     * @param tianPan 天盘
     * @return 九星落宫状态
     */
    public static List<List<String>> getJiuXingLuoGongStatus(List<String> tianPan) {

        Map<String, List<String>> jiuXingLuoGongStatusMap = QiMenZhuanPanJiChuMap.JIU_XING_LUO_GONG_STATUS; // 九星落宫状态

        List<List<String>> list = new ArrayList<>(); // 保存九星落宫状态
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                String xing = tianPan.get(i); // 每一宫位中的星
                if (xing.equals("芮禽")) {
                    List<String> gongWeiList = jiuXingLuoGongStatusMap.get("天芮"); // 每一宫位
                    String wangShuai = gongWeiList.get(i); // 每一宫位的九星落宫状态
                    list.add(Arrays.asList("芮禽", wangShuai + wangShuai));
                } else {
                    List<String> gongWeiList = jiuXingLuoGongStatusMap.get(xing); // 每一宫位
                    String wangShuai = gongWeiList.get(i); // 每一宫位的九星落宫状态
                    list.add(Arrays.asList(xing, wangShuai));
                }
            } else {
                list.add(Arrays.asList("中宫", "")); // 中五宫
            }
        }

        return list;

    }

    /**
     * 获取地盘奇仪与落宫地支的关系（1~9宫）
     *
     * @param diPan 地盘（1~9宫）
     * @return 地盘奇仪与落宫地支的关系（1~9宫）
     */
    public static List<List<List<String>>> getDiPanQiYiLuoGongLink(List<String> diPan) {

        Map<List<String>, String> qiYiLuoGongStatusMap = QiMenZhuanPanJiChuMap.QI_YI_LUO_GONG_STATUS; // 奇仪落宫状态
        Map<Integer, List<String>> jiuGongDiZhiMap = QiMenZhuanPanJiChuMap.JIU_GONG_DI_ZHI; // 九宫中的地支（1~9宫）

        List<List<List<String>>> list = new ArrayList<>(); // 保存地盘奇仪与落宫地支的关系
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                List<String> oneList = new ArrayList<>();
                List<List<String>> oneList2 = new ArrayList<>();
                String diPanQiYi = diPan.get(i); // 每一宫位的地盘奇仪
                List<String> diZhiList = jiuGongDiZhiMap.get(i); // 每一宫位中包含的地支
                for (String key : diZhiList) {
                    List<String> qiYiDiZhi = Arrays.asList(diPanQiYi, key); // 每一宫位中的地盘奇仪+地支
                    String status = qiYiLuoGongStatusMap.get(qiYiDiZhi);
                    oneList.add(key);
                    oneList.add(status);
                    oneList2.add(oneList);
                    oneList = new ArrayList<>();
                }
                list.add(oneList2);
            } else {
                list.add(Arrays.asList(Arrays.asList("", ""), Arrays.asList("", ""))); // 中五宫
            }
        }

        return list;

    }

    /**
     * 获取天盘奇仪与落宫地支的关系，只包含[天禽星]携带的奇仪（1~9宫）
     *
     * @param tianPanQiYiTianQinYes 天盘旋转后九星所携带的奇仪，只包含[天禽星]携带的奇仪（1~9宫）
     * @return 天盘奇仪与落宫地支的关系（1~9宫）
     */
    public static List<List<List<String>>> getTianPanQiYiLuoGongTianQinYesLink(List<String> tianPanQiYiTianQinYes) {

        Map<List<String>, String> qiYiLuoGongStatusMap = QiMenZhuanPanJiChuMap.QI_YI_LUO_GONG_STATUS; // 奇仪落宫状态
        Map<Integer, List<String>> jiuGongDiZhiMap = QiMenZhuanPanJiChuMap.JIU_GONG_DI_ZHI; // 九宫中的地支（后天八卦1~9宫）

        // 1、计算天盘奇仪与落宫地支的关系
        List<List<List<String>>> tianPanQiYiTianQinYesMap = new ArrayList<>(); // 保存天盘奇仪与落宫地支的关系（只包含[天禽星]携带的奇仪）
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                List<String> oneListTianPanQiYiTianQinYes = new ArrayList<>();
                List<List<String>> oneList2tianPanQiYiTianQinYes = new ArrayList<>();
                String tianPanQiYiTianPanQiYiTianQinYes = tianPanQiYiTianQinYes.get(i); // 每一宫位天盘奇仪（只包含[天禽星]携带的奇仪）
                List<String> diZhiList = jiuGongDiZhiMap.get(i); // 每一宫位中包含的地支
                String statusTianPanQiYiTianQinYes = null;
                for (String key : diZhiList) {
                    List<String> qiYiDiZhiTianPanQiYiTianQinYes = Arrays.asList(tianPanQiYiTianPanQiYiTianQinYes, key); // 每一宫位中的天盘奇仪+地支（只包含[天禽星]携带的奇仪）
                    statusTianPanQiYiTianQinYes = qiYiLuoGongStatusMap.get(qiYiDiZhiTianPanQiYiTianQinYes);
                    oneListTianPanQiYiTianQinYes.add(key);
                    oneListTianPanQiYiTianQinYes.add(statusTianPanQiYiTianQinYes);
                    oneList2tianPanQiYiTianQinYes.add(oneListTianPanQiYiTianQinYes);
                    oneListTianPanQiYiTianQinYes = new ArrayList<>();
                }
                if (null == statusTianPanQiYiTianQinYes) {
                    tianPanQiYiTianQinYesMap.add( Arrays.asList(Arrays.asList("", ""), Arrays.asList("", "")));
                } else {
                    tianPanQiYiTianQinYesMap.add(oneList2tianPanQiYiTianQinYes);
                }
            } else {
                tianPanQiYiTianQinYesMap.add(Arrays.asList(Arrays.asList("", ""), Arrays.asList("", ""))); // 中五宫
            }
        }

        // 3、返回数据
        return tianPanQiYiTianQinYesMap;

    }

    /**
     * 获取天盘奇仪与落宫地支的关系，不包含[天禽星]携带的奇仪（1~9宫）
     *
     * @param tianPanQiYiTianQinNo  天盘旋转后九星所携带的奇仪，不包含[天禽星]携带的奇仪（1~9宫）
     * @return 天盘奇仪与落宫地支的关系（1~9宫）
     */
    public static List<List<List<String>>> getTianPanQiYiLuoGongTianQinNoLink(List<String> tianPanQiYiTianQinNo) {

        Map<List<String>, String> qiYiLuoGongStatusMap = QiMenZhuanPanJiChuMap.QI_YI_LUO_GONG_STATUS; // 奇仪落宫状态
        Map<Integer, List<String>> jiuGongDiZhiMap = QiMenZhuanPanJiChuMap.JIU_GONG_DI_ZHI; // 九宫中的地支（后天八卦1~9宫）

        // 1、计算天盘奇仪与落宫地支的关系
        List<List<List<String>>> tianPanQiYiTianQinNoMap = new ArrayList<>(); // 保存天盘奇仪与落宫地支的关系（不包含[天禽星]携带的奇仪）
        for (int i = 0; i < 9; i++) {
            if (i != 4) {
                List<String> oneListTianPanQiYiTianQinNo = new ArrayList<>();
                List<List<String>> oneList2tianPanQiYiTianQinNo = new ArrayList<>();
                String tianPanQiYiTianPanQiYiTianQinNo = tianPanQiYiTianQinNo.get(i); // 每一宫位天盘奇仪（不包含[天禽星]携带的奇仪）
                List<String> diZhiList = jiuGongDiZhiMap.get(i); // 每一宫位中包含的地支
                for (String key : diZhiList) {
                    List<String> qiYiDiZhiTianPanQiYiTianQinNo = Arrays.asList(tianPanQiYiTianPanQiYiTianQinNo, key); // 每一宫位中的天盘奇仪+地支（不包含[天禽星]携带的奇仪）
                    String statusTianPanQiYiTianQinNo = qiYiLuoGongStatusMap.get(qiYiDiZhiTianPanQiYiTianQinNo);
                    oneListTianPanQiYiTianQinNo.add(key);
                    oneListTianPanQiYiTianQinNo.add(statusTianPanQiYiTianQinNo);
                    oneList2tianPanQiYiTianQinNo.add(oneListTianPanQiYiTianQinNo);
                    oneListTianPanQiYiTianQinNo = new ArrayList<>();
                }
                tianPanQiYiTianQinNoMap.add(oneList2tianPanQiYiTianQinNo);
            } else {
                tianPanQiYiTianQinNoMap.add(Arrays.asList(Arrays.asList("", ""), Arrays.asList("", ""))); // 中五宫
            }
        }

        // 3、返回数据
        return tianPanQiYiTianQinNoMap;

    }


}
