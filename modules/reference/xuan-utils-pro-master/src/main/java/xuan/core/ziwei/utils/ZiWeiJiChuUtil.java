package xuan.core.ziwei.utils;

import java.util.List;

/**
 * 紫微斗数 - 基础工具
 *
 * @author 善待
 */
public class ZiWeiJiChuUtil {

    /**
     * 获取星位宫位
     *
     * @param zhuXing  诸星
     * @param xingMing 星名
     * @return 星位宫位
     */
    public static int getXingWeiGongWei(List<String> zhuXing, String xingMing) {

        int xingWeiGongWei = 0;

        A:
        for (int i = 0; i < zhuXing.size(); i++) {
            if (!"".equals(zhuXing.get(i))) {
                String[] oneGongXing = zhuXing.get(i).split("_");
                if (oneGongXing.length == 1) {
                    if (xingMing.equals(zhuXing.get(i))) {
                        xingWeiGongWei = i + 1;
                        break;
                    }
                } else {
                    for (String item : oneGongXing) {
                        if (xingMing.equals(item)) {
                            xingWeiGongWei = i + 1;
                            break A;
                        }
                    }
                }
            }
        }

        return xingWeiGongWei;

    }

    /**
     * 添加诸星
     *
     * @param zhuXing 诸星
     * @param oneList 每一个宫位中的诸星
     * @param index   索引（0 ~ 11）
     * @param mark    标识
     */
    public static void addZhuXing(List<String> zhuXing, List<String> oneList, int index, String mark) {

        if (!"".equals(zhuXing.get(index))) {
            String[] oneGongXing = zhuXing.get(index).split("_");
            if (oneGongXing.length == 1) {
                oneList.add(mark + zhuXing.get(index));
            } else {
                for (String item : oneGongXing) {
                    oneList.add(mark + item);
                }
            }
        }

    }


}
