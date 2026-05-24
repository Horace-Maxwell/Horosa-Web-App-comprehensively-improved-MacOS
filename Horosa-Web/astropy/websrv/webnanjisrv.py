import traceback

import cherrypy
import jsonpickle

from websrv.helper import enable_crossdomain
from websrv.kentang.kinastro_common import (
    build_snapshot,
    clean_text,
    display_text,
    ensure_kinastro_path,
    gender_cn,
    json_safe,
    kinastro_source_sections,
    parse_datetime,
    row,
    to_float,
    to_int,
    timezone_to_float,
)


ensure_kinastro_path()

from astro.nanji.calculator import NanJiShenShu, TiaowenDatabase  # noqa: E402
from astro.nanji.constants import DIZHI, JIANCHU, PASSWORDS, TIANGAN, XIU28_ORDER  # noqa: E402


SECTIONS = [f"{branch}部" for branch in DIZHI]
JIANCHU_ALIASES = {
    "满": "滿",
    "执": "執",
    "开": "開",
    "闭": "閉",
}
XIU_ALIASES = {
    "氐": "氏",
    "氏": "氏",
    "虚": "虛",
    "娄": "婁",
    "毕": "畢",
    "参": "參",
    "张": "張",
    "翼": "翼",
    "翌": "翼",
    "轸": "軫",
    "嘴": "觜",
}
XIU_LOOKUP_VARIANTS = {
    "翼": ["翼", "翌"],
    "觜": ["觜", "嘴"],
    "婁": ["婁", "娄"],
    "畢": ["畢", "毕"],
    "張": ["張", "张"],
    "軫": ["軫", "轸"],
    "虛": ["虛", "虚"],
    "氏": ["氏", "氐"],
    "參": ["參", "参"],
}


def _option(value, label=None):
    return {"value": value, "label": display_text(label or value)}


SECTION_OPTIONS = [_option(item) for item in SECTIONS]
JIANCHU_OPTIONS = [_option(item) for item in JIANCHU]
XIU_OPTIONS = [_option(item) for item in XIU28_ORDER]
PASSWORD_OPTIONS = [_option(item) for item in PASSWORDS.keys()]


def _valid(value, choices, fallback):
    text = clean_text(value)
    return text if text in choices else fallback


def _normalize_jianchu(value):
    text = clean_text(value, "建")
    text = JIANCHU_ALIASES.get(text, text)
    return _valid(text, JIANCHU, "建")


def _normalize_xiu(value):
    text = clean_text(value, "角")
    text = XIU_ALIASES.get(text, text)
    return _valid(text, XIU28_ORDER, "角")


def _entry_to_dict(entry):
    return {
        "section": display_text(entry.section),
        "rawSection": entry.section,
        "code": display_text(entry.code),
        "rawCode": entry.code,
        "verse": display_text(entry.verse),
        "comment": display_text(entry.comment),
    }


def _dayun_to_dict(item):
    data = json_safe(item)
    start_age = to_int(data.get("start_age"), 1)
    return {
        "index": data.get("index"),
        "ganzhi": display_text(data.get("ganzhi")),
        "startAge": start_age,
        "endAge": start_age + 9,
    }


def _lookup_entries(njs, section, jianchu, xiu):
    variants = XIU_LOOKUP_VARIANTS.get(xiu, [xiu])
    entries = []
    seen = set()
    for item in variants:
        for entry in njs.lookup_tiaowen(section=section, code=f"{jianchu}{item}"):
            key = (entry.section, entry.code, entry.verse)
            if key not in seen:
                seen.add(key)
                entries.append(entry)
    return entries


def _build_manual_chart(data, gender):
    lunar_year = to_int(data.get("nanjiLunarYear") or data.get("lunarYear"), 2026)
    solar_month = max(1, min(12, to_int(data.get("nanjiSolarMonth") or data.get("solarMonth"), 1)))
    day = max(1, min(31, to_int(data.get("nanjiDay") or data.get("day"), 1)))
    hour_zhi = _valid(clean_text(data.get("nanjiHourZhi") or data.get("hourZhi")), DIZHI, "子")
    after_lichun = clean_text(data.get("nanjiAfterLichun") or data.get("afterLichun"), "1") != "0"
    njs = NanJiShenShu(
        lunar_year=lunar_year,
        solar_month=solar_month,
        day=day,
        hour_zhi=hour_zhi,
        gender=gender,
        after_lichun=after_lichun,
    )
    day_gan = _valid(clean_text(data.get("nanjiDayGan") or data.get("dayGan")), TIANGAN, "")
    day_zhi = _valid(clean_text(data.get("nanjiDayZhi") or data.get("dayZhi")), DIZHI, "")
    if day_gan:
        njs.set_day_pillar(day_gan, day_zhi or None)
        njs.set_hour_pillar()
    return njs


def _build_sections(pan):
    nanji = pan.get("nanji", {})
    fp = nanji.get("fourPillars", {})
    query = nanji.get("query", {})
    palace_entries = nanji.get("palaceEntries", [])
    query_entries = query.get("entries", [])
    password = nanji.get("password", {})
    return [
        {
            "title": "起盘",
            "rows": [
                row("起盘时间", f"{pan.get('dateStr', '')} {pan.get('timeStr', '')}".strip()),
                row("性别", pan.get("gender")),
                row("时区", pan.get("timezoneText")),
                row("起盘方式", nanji.get("modeLabel")),
                row("宫部", nanji.get("palaceSection")),
                row("年干阴阳", fp.get("yearYinyang")),
            ],
        },
        {
            "title": "四柱",
            "rows": [
                row("年柱", fp.get("year")),
                row("月柱", fp.get("month")),
                row("日柱", fp.get("day")),
                row("时柱", fp.get("hour")),
            ],
        },
        {
            "title": "宫部条文",
            "rows": [
                row("宫部", nanji.get("palaceSection")),
                row("条文数", nanji.get("palaceEntryCount")),
                *[
                    row(f"{item.get('code')} · {item.get('section')}", f"{item.get('verse')}｜{item.get('comment')}")
                    for item in palace_entries[:12]
                ],
            ],
        },
        {
            "title": "条文查询",
            "rows": [
                row("宫部", query.get("section")),
                row("密码", query.get("code")),
                row("命中数", query.get("count")),
                *[
                    row(f"{item.get('code')} · {item.get('section')}", f"{item.get('verse')}｜{item.get('comment')}")
                    for item in query_entries
                ],
            ],
        },
        {
            "title": "大运",
            "rows": [
                row(
                    f"第{item.get('index')}运 {item.get('startAge')}-{item.get('endAge')}岁",
                    item.get("ganzhi"),
                )
                for item in nanji.get("daYun", [])
            ],
        },
        {
            "title": "密码",
            "rows": [
                row("密码", password.get("code")),
                row("解义", password.get("meaning")),
            ],
        },
        {
            "title": "星图推演",
            "rows": [
                row("星图", nanji.get("divine", {}).get("chart")),
                row("宫位", nanji.get("divine", {}).get("palace")),
                row("宿度", nanji.get("divine", {}).get("degree")),
                row("密码", nanji.get("divine", {}).get("extraCode")),
                row("断语", nanji.get("divine", {}).get("text")),
            ],
        },
    ]


class NanJiSrv:
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
            gender = gender_cn(data.get("gender"), "男")
            timezone_value = timezone_to_float(data.get("zone") or data.get("timezone"), 8.0)
            mode = clean_text(data.get("nanjiMode") or data.get("mode"), "solar")
            if mode == "manual":
                njs = _build_manual_chart(data, gender)
                mode_label = "手动古法"
            else:
                njs = NanJiShenShu.from_solar_datetime(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    gender=gender,
                )
                mode = "solar"
                mode_label = "公历精算"

            result = njs.compute()
            db = TiaowenDatabase.get_instance()
            section = _valid(clean_text(data.get("nanjiSection") or data.get("section")), SECTIONS, njs.palace_section)
            jianchu = _normalize_jianchu(data.get("nanjiJianchu") or data.get("jianchu"))
            xiu = _normalize_xiu(data.get("nanjiXiu") or data.get("xiu"))
            query_entries = [_entry_to_dict(item) for item in _lookup_entries(njs, section, jianchu, xiu)]
            palace_entries = [_entry_to_dict(item) for item in njs.lookup_all_tiaowen_for_palace(njs.palace_section)]
            password_code = clean_text(data.get("nanjiPasswordCode") or data.get("passwordCode"))
            if not password_code:
                password_code = next(iter(PASSWORDS.keys()))
            password_meaning = njs.lookup_password(password_code)
            divine_chart = max(1, min(18, to_int(data.get("nanjiChart") or data.get("chart"), 1)))
            divine_palace = _valid(clean_text(data.get("nanjiPalace") or data.get("palace")), DIZHI, section[0])
            divine_degree = max(0.0, min(30.0, to_float(data.get("nanjiDegree") or data.get("degree"), 1.0)))
            divine_text = display_text(
                njs.divine(
                    chart=divine_chart,
                    palace=divine_palace,
                    jianchu=jianchu,
                    xiu=xiu,
                    degree=divine_degree,
                    extra_code=password_code,
                )
            )
            fp = result.four_pillars
            nanji = {
                "mode": mode,
                "modeLabel": mode_label,
                "palaceSection": display_text(njs.palace_section),
                "rawPalaceSection": njs.palace_section,
                "fourPillars": {
                    "year": display_text(fp.year),
                    "month": display_text(fp.month),
                    "day": display_text(fp.day),
                    "hour": display_text(fp.hour),
                    "yearYinyang": display_text(fp.year_yinyang),
                    "gender": display_text(fp.gender),
                },
                "daYun": [_dayun_to_dict(item) for item in result.da_yun],
                "palaceEntries": palace_entries,
                "palaceEntryCount": len(palace_entries),
                "query": {
                    "section": display_text(section),
                    "rawSection": section,
                    "jianchu": display_text(jianchu),
                    "rawJianchu": jianchu,
                    "xiu": display_text(xiu),
                    "rawXiu": xiu,
                    "code": display_text(jianchu + xiu),
                    "entries": query_entries,
                    "count": len(query_entries),
                },
                "password": {
                    "code": display_text(password_code),
                    "meaning": display_text(password_meaning),
                    "all": [{"code": display_text(key), "meaning": display_text(value)} for key, value in PASSWORDS.items()],
                },
                "divine": {
                    "chart": divine_chart,
                    "palace": display_text(divine_palace),
                    "degree": divine_degree,
                    "extraCode": display_text(password_code),
                    "text": divine_text,
                },
                "verseCount": db.total,
                "sampleResults": [_entry_to_dict(item) for item in result.tiaowen_results],
                "raw": json_safe(result),
            }
            pan = {
                "source": "kinastro",
                "engine": "kinastro-nanji",
                "technique": "nanji",
                "title": "南极神数",
                "dateStr": data.get("date", dt.strftime("%Y-%m-%d")),
                "timeStr": data.get("time", dt.strftime("%H:%M:%S")),
                "gender": gender,
                "timezone": timezone_value,
                "timezoneText": f"UTC{timezone_value:+g}",
                "nanji": nanji,
                "classics": kinastro_source_sections("南极神数", "接入 kinastro 的南极神数，以四柱、宫部、建除十二辰、二十八宿和 246 条手稿条文进行查询与推演。"),
                "capabilities": {
                    "inputs": ["date", "time", "timezone", "gender", "mode", "manualPillars", "section", "jianchu", "xiu", "password", "chart", "palace", "degree"],
                    "outputs": ["fourPillars", "palaceSection", "daYun", "palaceTiaowen", "queryTiaowen", "password", "divine"],
                    "sections": SECTION_OPTIONS,
                    "jianchu": JIANCHU_OPTIONS,
                    "xiu": XIU_OPTIONS,
                    "passwords": PASSWORD_OPTIONS,
                    "charts": list(range(1, 19)),
                    "palaces": [_option(item) for item in DIZHI],
                    "degreeRange": {"min": 0, "max": 30, "step": 0.5},
                },
            }
            pan["sections"] = _build_sections(pan)
            pan["snapshot"] = build_snapshot(pan)
            return jsonpickle.encode({"ResultCode": 0, "Result": pan}, unpicklable=False)
        except Exception:
            traceback.print_exc()
            return jsonpickle.encode({"ResultCode": -1, "Result": "nanji calculation failed"}, unpicklable=False)
