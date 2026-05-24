import traceback

import cherrypy
import jsonpickle

from websrv.helper import enable_crossdomain
from websrv.kentang.kinastro_common import (
    build_snapshot,
    clean_text,
    coord_to_float,
    ensure_kinastro_path,
    gender_cn,
    json_safe,
    kinastro_source_sections,
    parse_datetime,
    row,
    timezone_to_float,
)


ensure_kinastro_path()

from astro.cetian_ziwei import (  # noqa: E402
    CETIAN_18_FLYING_STARS,
    CETIAN_AUX_STAR_NAMES,
    CETIAN_FLYING_RULES,
    CETIAN_MAIN_STAR_NAMES,
    CETIAN_PATTERNS,
    CETIAN_SIHUA_TABLE,
    CETIAN_STAR_ATTRIBUTES,
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    HOUR_BRANCH_NAMES,
    LUNAR_MONTH_NAMES,
    WU_XING_JU_NAMES,
    compute_cetian_ziwei_chart,
)


def _day_to_chinese(day):
    units = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    if day <= 10:
        return units[day]
    if day < 20:
        return f"十{units[day - 10]}"
    if day == 20:
        return "二十"
    if day < 30:
        return f"二十{units[day - 20]}"
    return "三十"


def _palace_rows(palace):
    return [
        row("宫名", palace.get("name")),
        row("干支", f"{palace.get('stem_name')}{palace.get('branch_name')}"),
        row("正曜", palace.get("stars")),
        row("副曜", palace.get("aux_stars")),
        row("亮度", palace.get("brightness")),
        row("四化", palace.get("sihua")),
        row("大限", palace.get("da_xian")),
        row("飞星", palace.get("flying_stars")),
        row("格局", palace.get("patterns")),
    ]


def _build_sections(pan):
    chart = pan.get("cetian", {})
    lunar = pan.get("lunar", {})
    sections = [
        {
            "title": "起盘",
            "rows": [
                row("起盘时间", f"{pan.get('dateStr', '')} {pan.get('timeStr', '')}".strip()),
                row("时区", f"UTC{pan.get('timezone'):+.1f}"),
                row("经度", pan.get("longitude")),
                row("纬度", pan.get("latitude")),
                row("地点", pan.get("location")),
                row("性别", chart.get("gender")),
                row("阴阳", chart.get("yin_yang")),
            ],
        },
        {
            "title": "农历与命身",
            "rows": [
                row("农历", lunar.get("text")),
                row("时辰", pan.get("hourBranch")),
                row("命宫", pan.get("mingGong")),
                row("身宫", pan.get("shenGong")),
                row("五行局", pan.get("wuXingJu")),
                row("紫微", pan.get("ziwei")),
                row("节气", chart.get("solar_term_influence")),
            ],
        },
        {
            "title": "四化",
            "rows": [row(star, hua) for star, hua in (chart.get("sihua") or {}).items()],
        },
        {
            "title": "飞星",
            "rows": [
                row(star, f"{EARTHLY_BRANCHES.get(f.get('from_branch'), f.get('from_branch')) if isinstance(EARTHLY_BRANCHES, dict) else EARTHLY_BRANCHES[f.get('from_branch', 0)]} → {EARTHLY_BRANCHES[f.get('to_branch', 0)]}；{f.get('nature')}")
                for star, f in (chart.get("star_flight") or {}).items()
            ],
        },
        {
            "title": "格局",
            "rows": [
                row(item.get("name"), f"{item.get('stars')}；{item.get('meaning')}；{EARTHLY_BRANCHES[item.get('palace_branch', 0)]}宫")
                for item in (chart.get("active_patterns") or [])
            ],
        },
    ]
    for palace in chart.get("palaces", []):
        sections.append({"title": palace.get("name", "宫位"), "rows": _palace_rows(palace)})
    sections.append({
        "title": "星曜属性",
        "rows": [
            row(star, f"{attrs[0]} · {attrs[1]}")
            for star, attrs in CETIAN_STAR_ATTRIBUTES.items()
        ],
    })
    sections.append({
        "title": "正曜副曜",
        "rows": [
            row("十二正曜", CETIAN_MAIN_STAR_NAMES),
            row("七副曜", CETIAN_AUX_STAR_NAMES),
        ],
    })
    sections.append({
        "title": "宫干四化表",
        "rows": [
            row(HEAVENLY_STEMS[idx], {
                "禄": item[0],
                "权": item[1],
                "科": item[2],
                "忌": item[3],
            })
            for idx, item in enumerate(CETIAN_SIHUA_TABLE)
        ],
    })
    sections.append({
        "title": "飞化规则",
        "rows": [row(key, value) for key, value in CETIAN_FLYING_RULES.items()],
    })
    sections.append({
        "title": "古法格局规则",
        "rows": [row(key, value) for key, value in CETIAN_PATTERNS.items()],
    })
    sections.append({
        "title": "三合组",
        "rows": [
            row(f"三合{idx + 1}", [EARTHLY_BRANCHES[item] for item in group])
            for idx, group in enumerate(chart.get("sanhe_groups") or [])
        ],
    })
    return sections


class CeTianSrv:
    exposed = True

    def OPTIONS(*args, **kwargs):
        enable_crossdomain()

    @cherrypy.expose
    @cherrypy.config(**{"tools.cors.on": True})
    @cherrypy.tools.json_in()
    def pan(self):
        enable_crossdomain()
        try:
            if cherrypy.request.method == "OPTIONS":
                return jsonpickle.encode({"ResultCode": 0, "Result": "ok"}, unpicklable=False)
            data = cherrypy.request.json or {}
            dt = parse_datetime(data)
            timezone = timezone_to_float(data.get("zone") or data.get("timezone"), 8.0)
            latitude = coord_to_float(data.get("lat") or data.get("latitude"), 26.0667)
            longitude = coord_to_float(data.get("lon") or data.get("longitude"), 119.3167)
            location = clean_text(data.get("location") or data.get("place"), "星阙地点")
            gender = gender_cn(data.get("gender"), "男")
            chart = json_safe(compute_cetian_ziwei_chart(
                year=dt.year,
                month=dt.month,
                day=dt.day,
                hour=dt.hour,
                minute=dt.minute,
                timezone=timezone,
                latitude=latitude,
                longitude=longitude,
                location_name=location,
                gender=gender,
            ))
            lunar_text = (
                f"{chart.get('lunar_year')}年"
                f"{HEAVENLY_STEMS[chart.get('lunar_year_stem', 0)]}{EARTHLY_BRANCHES[chart.get('lunar_year_branch', 0)]}年 "
                f"{LUNAR_MONTH_NAMES[chart.get('lunar_month', 1) - 1]}"
                f"{'闰' if chart.get('is_leap_month') else ''}"
                f"初{_day_to_chinese(chart.get('lunar_day', 1))}"
            )
            pan = {
                "source": "kinastro",
                "engine": "kinastro-cetian",
                "technique": "cetian",
                "title": "策天飞星",
                "dateStr": data.get("date", dt.strftime("%Y-%m-%d")),
                "timeStr": data.get("time", dt.strftime("%H:%M:%S")),
                "timezone": timezone,
                "latitude": latitude,
                "longitude": longitude,
                "location": location,
                "lunar": {"text": lunar_text},
                "hourBranch": HOUR_BRANCH_NAMES[chart.get("hour_branch", 0)],
                "mingGong": f"{EARTHLY_BRANCHES[chart.get('ming_gong_branch', 0)]}宫",
                "shenGong": f"{EARTHLY_BRANCHES[chart.get('shen_gong_branch', 0)]}宫",
                "wuXingJu": WU_XING_JU_NAMES.get(chart.get("wu_xing_ju"), chart.get("wu_xing_ju")),
                "ziwei": f"{EARTHLY_BRANCHES[chart.get('ziwei_branch', 0)]}宫",
                "cetian": chart,
                "rules": {
                    "stars": json_safe(CETIAN_18_FLYING_STARS),
                    "starAttributes": json_safe(CETIAN_STAR_ATTRIBUTES),
                    "mainStars": json_safe(CETIAN_MAIN_STAR_NAMES),
                    "auxStars": json_safe(CETIAN_AUX_STAR_NAMES),
                    "sihuaTable": json_safe(CETIAN_SIHUA_TABLE),
                    "flyingRules": json_safe(CETIAN_FLYING_RULES),
                    "patterns": json_safe(CETIAN_PATTERNS),
                },
                "classics": kinastro_source_sections("策天飞星", "十八飞星、十一正曜七副曜、飞星四化与单宫独断。"),
                "capabilities": {
                    "inputs": ["date", "time", "gender", "timezone", "latitude", "longitude", "location"],
                    "outputs": ["lunarDate", "mingShen", "wuXingJu", "palaces", "18Stars", "starAttributes", "brightness", "sihua", "palaceStemSihua", "flyingStars", "flyingRules", "patterns", "sanheGroups", "solarTermInfluence"],
                },
            }
            pan["sections"] = _build_sections(pan)
            pan["snapshot"] = build_snapshot(pan)
            return jsonpickle.encode({"ResultCode": 0, "Result": pan}, unpicklable=False)
        except Exception:
            traceback.print_exc()
            return jsonpickle.encode({"ResultCode": -1, "Result": "cetian calculation failed"}, unpicklable=False)
