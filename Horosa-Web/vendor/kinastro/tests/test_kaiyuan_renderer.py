from __future__ import annotations

import pytest

from astro.kaiyuan import renderer as kaiyuan_renderer


class _FakeSwe:
    def julday(self, year: int, month: int, day: int, decimal_hour: float) -> float:
        return 2460000.5 + decimal_hour

    def calc_ut(self, jd: float, body_id: int):
        longitude_map = {
            1: 210.2,   # 月 -> 角
            5: 244.1,   # 木 -> 房
            4: 251.4,   # 火 -> 心
            6: 18.4,    # 土 -> 壁
            3: 128.0,   # 金 -> 鬼
            2: 334.2,   # 水 -> 危
        }
        speed_map = {1: 12.5, 5: 0.08, 4: 0.45, 6: -0.03, 3: 1.1, 2: 1.2}
        return [longitude_map[body_id], 0.0, 0.0, speed_map[body_id]], 0


def test_build_mansion_ranges_cover_full_circle() -> None:
    ranges = kaiyuan_renderer._build_mansion_ranges()
    assert len(ranges) == 28
    assert ranges[0]["name"] == "角"
    total_width = sum(entry["end"] - entry["start"] for entry in ranges)
    assert total_width == pytest.approx(360.0)


def test_build_twelve_palace_ranges_cover_full_circle() -> None:
    ranges = kaiyuan_renderer._build_twelve_palace_ranges()
    assert len(ranges) == 12
    assert ranges[0]["name"] == "戌宮"
    assert ranges[0]["station"] == "降婁"
    total_width = sum(entry["end"] - entry["start"] for entry in ranges)
    assert total_width == pytest.approx(360.0)


def test_has_live_chart_params_requires_date_fields() -> None:
    assert kaiyuan_renderer._has_live_chart_params({"year": 2026, "month": 5, "day": 18})
    assert not kaiyuan_renderer._has_live_chart_params({"year": 2026, "month": 5, "day": 0})


def test_compute_live_observations_uses_current_chart_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kaiyuan_renderer, "init_swisseph", lambda: _FakeSwe())
    params = {
        "year": 2026,
        "month": 5,
        "day": 18,
        "hour": 12,
        "minute": 30,
        "timezone": 8.0,
        "latitude": 22.3193,
        "longitude": 114.1694,
        "location_name": "Hong Kong",
    }

    observations = kaiyuan_renderer._compute_live_observations(params)

    assert [obs.key for obs in observations] == [
        "moon",
        "歲星（木）",
        "熒惑（火）",
        "填星（土）",
        "太白（金）",
        "辰星（水）",
    ]
    assert observations[0].mansion_name == "角"
    assert observations[1].mansion_name == "房"
    assert observations[2].mansion_name == "心"
    assert observations[3].retrograde is True


def test_build_astrolabe_svg_contains_chart_metadata() -> None:
    observations = [
        kaiyuan_renderer.KaiyuanObservation(
            key="moon",
            label="月",
            short_label="月",
            icon="☽",
            color="#f6d365",
            longitude=210.2,
            mansion_name="角",
            mansion_degree=6.4,
        ),
        kaiyuan_renderer.KaiyuanObservation(
            key="jupiter",
            label="歲星（木）",
            short_label="歲",
            icon="♃",
            color="#4caf50",
            longitude=244.1,
            mansion_name="房",
            mansion_degree=1.2,
        ),
    ]
    params = {
        "year": 2026,
        "month": 5,
        "day": 18,
        "hour": 12,
        "minute": 30,
        "timezone": 8.0,
        "location_name": "Hong Kong",
    }

    svg = kaiyuan_renderer._build_astrolabe_svg(observations, params, width=420)

    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert "開元星盤" in svg
    assert "Hong Kong" in svg
    assert "☽ 月・角" in svg
    assert "♃ 歲星（木）・房" in svg
    assert "戌宮" in svg
    assert "玄枵" in svg


def test_collect_live_omens_reads_planet_and_moon_entries() -> None:
    observations = [
        kaiyuan_renderer.KaiyuanObservation(
            key="moon",
            label="月",
            short_label="月",
            icon="☽",
            color="#f6d365",
            longitude=210.2,
            mansion_name="角",
            mansion_degree=6.4,
        ),
        kaiyuan_renderer.KaiyuanObservation(
            key="jupiter",
            label="歲星（木）",
            short_label="歲",
            icon="♃",
            color="#4caf50",
            longitude=244.1,
            mansion_name="房",
            mansion_degree=1.2,
        ),
    ]
    five_planet_data = {
        "歲星（木）": {"房": {"開元占經": "歲星入房，主德令行。"}}
    }
    moon_data = {"角": {"開元占經": "月犯角，主朝廷有憂。"}}

    rows = kaiyuan_renderer._collect_live_omens(observations, five_planet_data, moon_data)

    assert len(rows) == 2
    assert rows[0]["is_moon"] is True
    assert rows[0]["mansion"] == "角"
    assert rows[0]["omen"] == {"開元占經": "月犯角，主朝廷有憂。"}
    assert rows[1]["label"] == "歲星（木）"
    assert rows[1]["omen"] == {"開元占經": "歲星入房，主德令行。"}
