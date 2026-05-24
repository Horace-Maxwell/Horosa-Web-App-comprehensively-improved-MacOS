#!/usr/bin/env python3
"""
tests/test_sabian.py — Sabian Symbols 模組測試

測試 Marc Edmund Jones 1953 原著 Sabian Symbols 模組的功能。
"""

import sys
import json
from pathlib import Path

# 加入專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_sabian_data_loaded():
    """測試 Sabian Symbols 資料正確載入。"""
    from astro.sabian import _SABIAN_DATA, _SABIAN_INDEX
    
    assert len(_SABIAN_DATA) == 360, f"應有 360 個符號，實際有 {len(_SABIAN_DATA)} 個"
    assert len(_SABIAN_INDEX) == 360, f"索引應有 360 個項目"
    print("✓ Sabian 資料正確載入 (360 個符號)")


def test_get_sabian_symbol():
    """測試 get_sabian_symbol() 函數。"""
    from astro.sabian import get_sabian_symbol
    
    # 測試白羊座 1°
    sabian = get_sabian_symbol(0.0)
    assert sabian['degree'] == 1
    assert sabian['sign'] == 'Aries'
    assert sabian['degree_in_sign'] == 1
    assert sabian['keyword'] == 'Emergence'
    print("✓ 白羊座 1° 正確")
    
    # 測試金牛座 16°
    sabian = get_sabian_symbol(45.5)
    assert sabian['degree'] == 46
    assert sabian['sign'] == 'Taurus'
    assert sabian['degree_in_sign'] == 16
    print("✓ 金牛座 16° 正確")
    
    # 測試雙魚座 30° (最後一度)
    sabian = get_sabian_symbol(359.9)
    assert sabian['degree'] == 360
    assert sabian['sign'] == 'Pisces'
    assert sabian['degree_in_sign'] == 30
    print("✓ 雙魚座 30° 正確")
    
    # 測試邊界
    sabian = get_sabian_symbol(360.0)  # 應回到白羊座 1°
    assert sabian['degree'] == 1
    print("✓ 360° 循環正確")


def test_get_sabian_for_planet():
    """測試 get_sabian_for_planet() 函數。"""
    from astro.sabian import get_sabian_for_planet
    
    chart = {
        "planets": [
            {"name": "Sun", "longitude": 294.5},
            {"name": "Moon", "longitude": 70.3},
            {"name": "Ascendant", "longitude": 15.0},
        ]
    }
    
    # 測試太陽
    sabian = get_sabian_for_planet(chart, "Sun")
    assert sabian is not None
    assert sabian['planet'] == 'Sun'
    assert sabian['planet_longitude'] == 294.5
    assert sabian['sign'] == 'Capricorn'
    print("✓ 太陽 Sabian Symbol 正確")
    
    # 測試月亮
    sabian = get_sabian_for_planet(chart, "Moon")
    assert sabian is not None
    assert sabian['sign'] == 'Gemini'
    print("✓ 月亮 Sabian Symbol 正確")
    
    # 測試上升點
    sabian = get_sabian_for_planet(chart, "Ascendant")
    assert sabian is not None
    assert sabian['sign'] == 'Aries'
    print("✓ 上升點 Sabian Symbol 正確")
    
    # 測試不存在的行星
    sabian = get_sabian_for_planet(chart, "Pluto")
    assert sabian is None
    print("✓ 不存在的行星回傳 None")


def test_render_sabian_svg():
    """測試 render_sabian_svg() 函數。"""
    from astro.sabian import render_sabian_svg
    
    svg = render_sabian_svg(294.5, size=300)
    
    assert svg.startswith('<svg')
    assert svg.endswith('</svg>')
    assert 'width="300"' in svg
    assert 'height="300"' in svg
    assert 'Capricorn' in svg
    print("✓ SVG 生成正確")


def test_to_context_sabian():
    """測試 to_context_sabian() XML 序列化。"""
    from astro.sabian import get_sabian_symbol, to_context_sabian
    
    sabian = get_sabian_symbol(294.5)
    xml = to_context_sabian(sabian)
    
    assert '<sabian_symbol>' in xml
    assert '</sabian_symbol>' in xml
    assert '<degree>295</degree>' in xml
    assert '<sign>Capricorn</sign>' in xml
    assert '<keyword>Access</keyword>' in xml
    print("✓ XML 序列化正確")


def test_serialize_sabian_for_context():
    """測試 serialize_sabian_for_context() 函數。"""
    from astro.sabian import serialize_sabian_for_context
    
    chart = {
        "planets": [
            {"name": "Sun", "longitude": 294.5},
            {"name": "Moon", "longitude": 70.3},
        ]
    }
    
    xml = serialize_sabian_for_context(chart, ["Sun", "Moon"])
    
    assert '<sabian_symbols>' in xml
    assert '</sabian_symbols>' in xml
    assert xml.count('<sabian_symbol>') == 2
    print("✓ 批量 XML 序列化正確")


def test_get_all_sabian_symbols_for_sign():
    """測試 get_all_sabian_symbols_for_sign() 函數。"""
    from astro.sabian import get_all_sabian_symbols_for_sign
    
    # 測試白羊座
    aries = get_all_sabian_symbols_for_sign("Aries")
    assert len(aries) == 30
    assert aries[0]['degree_in_sign'] == 1
    assert aries[29]['degree_in_sign'] == 30
    print("✓ 白羊座 30 個符號正確")
    
    # 測試所有星座
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    for sign in signs:
        symbols = get_all_sabian_symbols_for_sign(sign)
        assert len(symbols) == 30, f"{sign} 應有 30 個符號"
    print("✓ 所有 12 星座各有 30 個符號")


def test_context_serializer_integration():
    """測試與 context_serializer 的整合。"""
    from astro.context_serializer import to_context
    
    # 使用 dict 格式
    chart = {
        "western": {
            "planets": [
                {"name": "Sun", "longitude": 294.5},
                {"name": "Moon", "longitude": 70.3},
            ]
        }
    }
    
    # 測試不包含 Sabian
    xml = to_context(chart, system="all", include_sabian=False)
    assert '<western>' in xml
    assert '<sabian_symbols>' not in xml
    print("✓ 不包含 Sabian 時正確")
    
    # 測試包含 Sabian
    xml = to_context(chart, system="all", include_sabian=True)
    assert '<western>' in xml
    assert '<sabian_symbols>' in xml
    assert 'Capricorn' in xml  # 太陽的星座
    assert 'Gemini' in xml  # 月亮的星座
    print("✓ 包含 Sabian 時正確")


def test_cross_compare_integration():
    """測試與 cross_compare 的整合。"""
    try:
        from astro.cross_compare import compute_cross_comparison, SABIAN_AVAILABLE
        
        if SABIAN_AVAILABLE:
            print("✓ Sabian Symbols 在 cross_compare 中可用")
        else:
            print("⚠ Sabian Symbols 在 cross_compare 中不可用（預期的 ImportError）")
    except ImportError as e:
        print(f"⚠ cross_compare 匯入失敗：{e}")


def test_json_data_structure():
    """測試 JSON 資料結構的完整性。"""
    data_path = Path(__file__).parent.parent / "astro" / "data" / "sabian_symbols.json"
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert len(data) == 360, f"應有 360 筆資料，實際有 {len(data)} 筆"
    
    # 檢查每筆資料的欄位
    required_fields = ["degree", "sign", "degree_in_sign", "symbol", 
                       "keyword", "positive", "negative", "formula", "interpretation"]
    
    for i, item in enumerate(data):
        for field in required_fields:
            assert field in item, f"第 {i+1} 筆資料缺少 {field} 欄位"
        
        # 檢查度數正確性
        assert item['degree'] == i + 1, f"第 {i+1} 筆資料的 degree 應為 {i+1}"
    
    print("✓ JSON 資料結構完整 (360 筆，每筆 9 個欄位)")


def run_all_tests():
    """執行所有測試。"""
    print("=" * 60)
    print("Sabian Symbols 模組測試套件")
    print("=" * 60)
    print()
    
    tests = [
        test_sabian_data_loaded,
        test_get_sabian_symbol,
        test_get_sabian_for_planet,
        test_render_sabian_svg,
        test_to_context_sabian,
        test_serialize_sabian_for_context,
        test_get_all_sabian_symbols_for_sign,
        test_context_serializer_integration,
        test_cross_compare_integration,
        test_json_data_structure,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n執行 {test.__name__}...")
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} 失敗：{e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} 錯誤：{e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"測試結果：{passed} 通過，{failed} 失敗")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
