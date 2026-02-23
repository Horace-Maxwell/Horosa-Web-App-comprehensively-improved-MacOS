package xuan.utils;

import org.junit.Test;

import java.util.Date;

/**
 * 真太阳时工具测试
 *
 * @author 善待
 */
public class TrueSolarDateUtilTest {

    /**
     * 获取真太阳时
     */
    @Test
    public void getTrueSolarDate() {

        // 初始化日期
        Date date = new Date(2024 - 1900, 1 - 1, 1, 0, 0 ,0);

        // 获取真太阳时
        String address = "上海市"; // 地区
        double lng = 121; // 经度
//        Date trueSolarTime = TrueSolarDateUtil.getTrueSolarDate(date, address); // 获取真太阳时（根据地区计算）
        Date trueSolarTime = TrueSolarDateUtil.getTrueSolarDate(date, lng); // 获取真太阳时（根据经度计算）

        // 格式化日期
        String dateStr = DateUtil.getDateStr(date, "yyyy-MM-dd HH:mm:ss"); // 标准时刻
        String trueSolarTimeStr = DateUtil.getDateStr(trueSolarTime, "yyyy-MM-dd HH:mm:ss"); // 真太阳时
        System.out.println(address + "，标准时刻→ " + dateStr); // 上海市，标准时刻→ 2024-01-01 00:00:00
        System.out.println(address + "，真太阳时→ " + trueSolarTimeStr); // 上海市，真太阳时→ 2024-01-01 00:00:57

    }


}
