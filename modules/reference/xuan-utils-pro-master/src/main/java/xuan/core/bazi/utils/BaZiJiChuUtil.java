package xuan.core.bazi.utils;

import xuan.utils.CommonUtil;

import java.util.Map;

/**
 * 八字 - 基础工具
 *
 * @author 善待
 */
public class BaZiJiChuUtil {

    /**
     * 返回干支加分
     *
     * @param shengKe   天干和干支五行的生克关系
     * @param ganOrZhi1 天干或地支
     * @param ganOrZhi2 天干或地支
     * @param jiaFen    加分
     * @return 干支加分
     */
    public static int ganZhiJiaFen(Map<String, String> shengKe, String ganOrZhi1, String ganOrZhi2, int jiaFen) {

        int ganZhiJiaFen = 0;
        String qiangOrRuo = shengKe.get(ganOrZhi1 + ganOrZhi2); // '身强'或'身弱'
        if ("身强".equals(qiangOrRuo)) ganZhiJiaFen += jiaFen;
        return ganZhiJiaFen;

    }

    /**
     * 骨重转为文字
     *
     * @param guZhong 骨重
     * @return 骨重文字（如：七两）
     */
    public static String guZhongCharacters(Integer guZhong) {

        long liang = Long.parseLong(guZhong.toString().substring(0, 1)); // 两重
        long qian = Long.parseLong(guZhong.toString().substring(1, 2)); // 钱重
        String newGuZhong = CommonUtil.shuToHan(liang) + "两";
        if (0 != qian) newGuZhong += CommonUtil.shuToHan(qian) + "钱";
        return newGuZhong;

    }


}
