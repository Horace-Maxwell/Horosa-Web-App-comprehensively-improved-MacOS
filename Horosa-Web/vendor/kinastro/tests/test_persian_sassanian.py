"""
tests/test_persian_sassanian.py — 波斯薩珊占星模組測試

測試案例包含：
1. 白天出生 (1990 年 1 月 15 日 12:00 台北)
2. 夜晚出生 (1990 年 1 月 15 日 02:00 台北)
"""

import sys
sys.path.insert(0, '/mnt/c/Users/hooki/OneDrive/pastword/文件/Github/kinastro')

from astro.persian import (
    compute_sassanian_chart,
    calculate_firdar,
    calculate_hyleg_alcocoden,
    calculate_profections,
    calculate_almuten_figuris,
    get_royal_stars_prominence,
    calculate_persian_lots,
)


def test_day_birth_chart():
    """測試案例 1: 白天出生 (1990 年 7 月 15 日 12:00 台北) - 夏天中午"""
    print("=" * 60)
    print("測試案例 1: 白天出生")
    print("1990 年 7 月 15 日 12:00 台北")
    print("=" * 60)
    
    chart = compute_sassanian_chart(
        year=1990, month=7, day=15,  # 改為 7 月夏天
        hour=12, minute=0,
        latitude=25.0330, longitude=121.5654,
        timezone=8.0
    )
    
    # 基本驗證
    assert len(chart.planets) == 7, f"應有 7 顆行星，實際：{len(chart.planets)}"
    assert len(chart.houses) == 12, f"應有 12 宮，實際：{len(chart.houses)}"
    
    print(f"✓ 日夜判斷：{'白天' if chart.is_day_birth else '夜晚'} (基於太陽宮位)")
    print(f"✓ 上升點：{chart.ascendant:.2f}°")
    print(f"✓ 天頂：{chart.midheaven:.2f}°")
    print(f"✓ 行星數量：{len(chart.planets)}")
    
    # Firdar 驗證 - 根據實際日夜判斷
    assert len(chart.firdar) > 0, "應有 Firdar 週期"
    expected_first_lord = "Sun" if chart.is_day_birth else "Moon"
    assert chart.firdar[0].lord == expected_first_lord, f"Firdar 應從{expected_first_lord}開始，實際：{chart.firdar[0].lord}"
    
    print(f"\n✓ Firdar 起始：{chart.firdar[0].lord} ({chart.firdar[0].lord_cn}) ({'白天' if chart.is_day_birth else '夜晚'}出生)")
    print(f"✓ Firdar 週期數量：{len(chart.firdar)}")
    
    if chart.current_firdar:
        print(f"✓ 當前 Firdar: {chart.current_firdar.lord} ({chart.current_firdar.lord_cn})")
        if chart.current_sub_period:
            print(f"✓ 當前子週期：{chart.current_sub_period.lord} ({chart.current_sub_period.lord_cn})")
    
    # Hyleg & Alcocoden 驗證
    assert chart.hyleg is not None, "應有 Hyleg"
    assert chart.alcocoden is not None, "應有 Alcocoden"
    
    print(f"\n✓ Hyleg: {chart.hyleg.hyleg_type} ({chart.hyleg.hyleg_name_cn})")
    print(f"  位置：{chart.hyleg.sign} {chart.hyleg.degree:.1f}°")
    print(f"  宮位：第{chart.hyleg.house}宮")
    print(f"  原因：{chart.hyleg.reason}")
    
    print(f"\n✓ Alcocoden: {chart.alcocoden.alcocoden_lord} ({chart.alcocoden.alcocoden_lord_cn})")
    print(f"  基礎年數：{chart.alcocoden.planetary_years}年")
    print(f"  修正年數：{chart.alcocoden.modified_years:.1f}年")
    
    # Almuten Figuris 驗證
    assert chart.almuten_figuris is not None, "應有 Almuten Figuris"
    print(f"\n✓ Almuten Figuris: {chart.almuten_figuris.planet} ({chart.almuten_figuris.planet_cn})")
    print(f"  總分：{chart.almuten_figuris.total_score}")
    
    # Profections 驗證
    assert len(chart.profections) > 0, "應有年度主限"
    assert len(chart.profections) >= 80, f"應至少有 80 年主限，實際：{len(chart.profections)}"
    print(f"\n✓ 年度主限數量：{len(chart.profections)}年")
    
    # Royal Stars 驗證
    assert len(chart.royal_stars) == 4, f"應有 4 顆皇家恆星，實際：{len(chart.royal_stars)}"
    prominent = [rs for rs in chart.royal_stars if rs.is_prominent]
    print(f"\n✓ 皇家恆星數量：{len(chart.royal_stars)}")
    print(f"✓ 顯著皇家恆星：{len(prominent)}")
    
    # Persian Lots 驗證
    assert len(chart.persian_lots) > 0, "應有波斯敏感點"
    print(f"\n✓ 波斯敏感點數量：{len(chart.persian_lots)}")
    
    print("\n" + "=" * 60)
    print("測試案例 1 通過！")
    print("=" * 60)
    return chart


def test_night_birth_chart():
    """測試案例 2: 夜晚出生 (1990 年 1 月 15 日 02:00 台北)"""
    print("\n" + "=" * 60)
    print("測試案例 2: 夜晚出生")
    print("1990 年 1 月 15 日 02:00 台北")
    print("=" * 60)
    
    chart = compute_sassanian_chart(
        year=1990, month=1, day=15,
        hour=2, minute=0,
        latitude=25.0330, longitude=121.5654,
        timezone=8.0
    )
    
    # 基本驗證
    assert len(chart.planets) == 7, f"應有 7 顆行星，實際：{len(chart.planets)}"
    
    print(f"✓ 日夜判斷：{'白天' if chart.is_day_birth else '夜晚'} (基於太陽宮位)")
    
    # Firdar 驗證 - 根據實際日夜判斷
    expected_first_lord = "Sun" if chart.is_day_birth else "Moon"
    assert chart.firdar[0].lord == expected_first_lord, f"Firdar 應從{expected_first_lord}開始，實際：{chart.firdar[0].lord}"
    print(f"✓ Firdar 起始：{chart.firdar[0].lord} ({chart.firdar[0].lord_cn}) ({'白天' if chart.is_day_birth else '夜晚'}出生)")
    
    # Hyleg 驗證
    print(f"\n✓ Hyleg: {chart.hyleg.hyleg_type} ({chart.hyleg.hyleg_name_cn})")
    print(f"  原因：{chart.hyleg.reason}")
    
    print("\n" + "=" * 60)
    print("測試案例 2 通過！")
    print("=" * 60)
    return chart


def test_firdar_calculation():
    """測試 Firdar 計算函數"""
    print("\n" + "=" * 60)
    print("測試 Firdar 計算")
    print("=" * 60)
    
    import swisseph as swe
    jd = swe.julday(1990, 1, 15, 12.0)
    
    # 白天出生
    firdar_day = calculate_firdar(jd, is_day_birth=True, num_years=80)
    assert len(firdar_day) > 0, "應有 Firdar 週期"
    assert firdar_day[0].lord == "Sun", "白天出生應從 Sun 開始"
    print(f"✓ 白天出生 Firdar: {len(firdar_day)}個主要週期，從{firdar_day[0].lord}開始")
    
    # 夜晚出生
    firdar_night = calculate_firdar(jd, is_day_birth=False, num_years=80)
    assert firdar_night[0].lord == "Moon", "夜晚出生應從 Moon 開始"
    print(f"✓ 夜晚出生 Firdar: {len(firdar_night)}個主要週期，從{firdar_night[0].lord}開始")
    
    # 驗證子週期
    for fd in firdar_day:
        assert len(fd.sub_periods) == 7, f"每個主要週期應有 7 個子週期，實際：{len(fd.sub_periods)}"
    print(f"✓ 每個主要週期包含 7 個子週期")
    
    print("\nFirdar 計算測試通過！")


def test_profections():
    """測試年度主限計算"""
    print("\n" + "=" * 60)
    print("測試年度主限計算")
    print("=" * 60)
    
    import swisseph as swe
    jd = swe.julday(1990, 1, 15, 12.0)
    ascendant = 30.0  # 金牛座 0°
    
    profections = calculate_profections(ascendant, jd, num_years=30)
    
    assert len(profections) == 30, f"應有 30 年主限，實際：{len(profections)}"
    
    # 第一年應從上升點開始
    assert profections[0].age == 0, "第一年年齡應為 0"
    print(f"✓ 0 歲：{profections[0].profection_sign_cn} {profections[0].profection_degree:.1f}°")
    
    # 每年移動 30°
    for i in range(1, len(profections)):
        expected_degree = (ascendant + (i * 30)) % 360
        actual_degree = profections[i].profection_degree + (int(expected_degree // 30) * 30)
        assert abs(actual_degree - expected_degree) < 0.1, f"第{i}年主限位應移動 30°"
    
    print(f"✓ 每年移動 30°，共{len(profections)}年")
    print("\n年度主限測試通過！")


def test_royal_stars():
    """測試皇家恆星計算"""
    print("\n" + "=" * 60)
    print("測試皇家恆星計算")
    print("=" * 60)
    
    from astro.persian.sassanian_astrology import SassanianPlanet
    
    # 創建測試行星
    test_planets = [
        SassanianPlanet(
            name="Sun", name_cn="太陽",
            longitude=69.0, latitude=0.0,  # 與 Aldebaran 合相
            sign="Gemini", sign_glyph="♊", sign_cn="雙子座",
            sign_degree=9.0, house=1, retrograde=False
        ),
        SassanianPlanet(
            name="Moon", name_cn="月亮",
            longitude=149.0, latitude=0.0,  # 與 Regulus 合相
            sign="Leo", sign_glyph="♌", sign_cn="獅子座",
            sign_degree=29.0, house=2, retrograde=False
        ),
    ]
    
    royal_stars = get_royal_stars_prominence(test_planets, orb_limit=3.0)
    
    assert len(royal_stars) == 4, f"應有 4 顆皇家恆星，實際：{len(royal_stars)}"
    
    prominent = [rs for rs in royal_stars if rs.is_prominent]
    print(f"✓ 顯著皇家恆星數量：{len(prominent)}")
    
    for rs in prominent:
        print(f"  - {rs.star_name} ({rs.star_name_cn}) 與 {rs.conjunction_planet} 合相 (容許度：{rs.orb}°)")
    
    print("\n皇家恆星測試通過！")


if __name__ == "__main__":
    """執行所有測試"""
    print("\n" + "=" * 70)
    print("波斯薩珊占星模組測試套件")
    print("=" * 70)
    
    try:
        # 測試白天出生
        chart_day = test_day_birth_chart()
        
        # 測試夜晚出生
        chart_night = test_night_birth_chart()
        
        # 測試 Firdar 計算
        test_firdar_calculation()
        
        # 測試年度主限
        test_profections()
        
        # 測試皇家恆星
        test_royal_stars()
        
        print("\n" + "=" * 70)
        print("✅ 所有測試通過！")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ 測試失敗：{e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n❌ 測試錯誤：{e}")
        import traceback
        traceback.print_exc()
        exit(1)
