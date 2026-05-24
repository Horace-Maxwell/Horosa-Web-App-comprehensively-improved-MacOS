import os
import sys
import traceback
from numbers import Integral, Real

import cherrypy
import jsonpickle

from websrv.helper import enable_crossdomain


_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
_HOROSA_WEB_ROOT = os.path.abspath(os.path.join(_CUR_DIR, "..", ".."))
_KINWUZHAO_SRC = os.path.join(_HOROSA_WEB_ROOT, "vendor", "kinwuzhao")


def _import_kinwuzhao():
    """Import kinwuzhao without leaking its top-level config.py to other adapters."""
    previous_modules = {name: sys.modules.get(name) for name in ("config", "jieqi", "kinwuzhao")}
    for name in previous_modules:
        sys.modules.pop(name, None)
    inserted = False
    if _KINWUZHAO_SRC not in sys.path:
        sys.path.insert(0, _KINWUZHAO_SRC)
        inserted = True
    try:
        import config as wuzhao_config  # noqa: E402
        import jieqi as wuzhao_jieqi  # noqa: E402
        import kinwuzhao as wuzhao_core  # noqa: E402
        return wuzhao_config, wuzhao_jieqi, wuzhao_core
    finally:
        for name, module in previous_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
        if inserted:
            try:
                sys.path.remove(_KINWUZHAO_SRC)
            except ValueError:
                pass


wuzhao_config, wuzhao_jieqi, wuzhao_core = _import_kinwuzhao()


POSITION_ORDER = ["兆", "木鄉", "火鄉", "土鄉", "金鄉", "水鄉"]
POSITION_LABELS = {
    "兆": "兆",
    "木鄉": "木乡",
    "火鄉": "火乡",
    "土鄉": "土乡",
    "金鄉": "金乡",
    "水鄉": "水乡",
}
FLAG_LABELS = {
    "孤": "孤",
    "虛": "虚",
    "關": "关",
    "籥": "籥",
    "將軍": "将军",
    "六獸死": "六兽死",
    "六獸害": "六兽害",
}
MODE_LABELS = {
    "ganzhi": "干支起盘",
    "day": "日干起盘",
    "hour": "时干起盘",
    "minute": "分干起盘",
    "tang": "唐代正法揲筮",
}


def _to_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default


def _clean_text(value, default=""):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _json_safe(value):
    if isinstance(value, dict):
        return {_clean_text(key): _json_safe(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Integral) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, Real) and not isinstance(value, bool):
        return float(value)
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except Exception:
            return _clean_text(value)
    return value


def _format_value(value):
    if value is None or value == "":
        return ""
    if isinstance(value, dict):
        parts = []
        for key, val in value.items():
            text = _format_value(val)
            if text:
                parts.append(f"{key}：{text}")
        return "；".join(parts)
    if isinstance(value, list):
        return "、".join([_format_value(item) for item in value if _format_value(item)])
    return _clean_text(value)


def _row(label, value):
    return {"label": label, "value": _format_value(value) or "—"}


def _read_vendor_markdown(filename, fallback=""):
    path = os.path.join(_KINWUZHAO_SRC, filename)
    if not os.path.isfile(path):
        return fallback
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read().strip()
    return content or fallback


def _related_links():
    return [
        {
            "name": "堅六壬 Kinliuren",
            "url": "https://github.com/kentang2017/kinliuren",
            "description": "六壬天地盘，用于五兆关籥与将军等辅助计算。",
        },
        {
            "name": "堅奇門 Kinqimen",
            "url": "https://github.com/kentang2017/kinqimen",
            "description": "kentang2017 奇门遁甲计算项目。",
        },
        {
            "name": "堅太乙 Kintaiyi",
            "url": "https://github.com/kentang2017/kintaiyi",
            "description": "kentang2017 太乙神数计算项目。",
        },
    ]


def _lunar_text(lunar):
    if not isinstance(lunar, dict):
        return "—"
    month = lunar.get("農曆月") or lunar.get("月") or ""
    day = lunar.get("日") or ""
    return f"{lunar.get('年', '')}年{month}{day}日".strip()


def _normalize_positions(raw):
    positions = []
    for key in POSITION_ORDER:
        item = raw.get(key, {}) if isinstance(raw, dict) else {}
        flags = [FLAG_LABELS.get(name, name) for name in ["孤", "虛", "關", "籥", "將軍", "六獸死", "六獸害"] if item.get(name)]
        positions.append({
            "key": key,
            "label": POSITION_LABELS.get(key, key),
            "palace": item.get("宮位1", ""),
            "prosperity": item.get("旺相", ""),
            "number": item.get("數字", ""),
            "element": item.get("五行", ""),
            "beast": item.get("六獸", ""),
            "relation": item.get("六親", ""),
            "flags": flags,
            "raw": _json_safe(item),
            "rows": [
                _row("宫位", item.get("宮位1")),
                _row("旺相", item.get("旺相")),
                _row("数字", item.get("數字")),
                _row("五行", item.get("五行")),
                _row("六兽", item.get("六獸")),
                _row("六亲", item.get("六親")),
                _row("特殊", "、".join(flags)),
            ],
        })
    return positions


def _classic_sections():
    sections = [
        {
            "title": "五兆古籍书目",
            "content": _read_vendor_markdown("guji.md", "暂无五兆古籍目录。"),
        },
        {
            "title": "占卜案例",
            "content": _read_vendor_markdown("example.md", "上游 example.md 暂无案例内容。"),
        },
        {
            "title": "更新日志",
            "content": _read_vendor_markdown("log.md", "暂无更新日志。"),
        },
    ]
    link_lines = [
        f"{item['name']}：{item['description']}（{item['url']}）"
        for item in _related_links()
    ]
    sections.append({
        "title": "相关项目",
        "content": "\n".join(link_lines),
    })
    return {
        "meta": [{
            "key": "wuzhao_bibliography",
            "title": "kinwuzhao 来源内容",
            "author": "kentang2017 / kinwuzhao 汇编",
            "description": "承接上游 Streamlit 应用的古籍、案例、更新与相关项目内容，并在星阙右栏统一展示。",
        }],
        "selectedKey": "wuzhao_bibliography",
        "sections": sections,
        "links": _related_links(),
    }


def _build_sections(payload, positions):
    gz = payload.get("ganzhi", {})
    sections = [
        {
            "title": "起盘",
            "rows": [
                _row("起盘时间", f"{payload.get('dateStr', '')} {payload.get('timeStr', '')}".strip()),
                _row("起盘方式", payload.get("modeLabel")),
                _row("报数", payload.get("number")),
                _row("节气", payload.get("solarTerm")),
                _row("农历", payload.get("lunarDate", {}).get("text")),
                _row("年柱", gz.get("year")),
                _row("月柱", gz.get("month")),
                _row("日柱", gz.get("day")),
                _row("时柱", gz.get("hour")),
                _row("分柱", gz.get("minute")),
            ],
        },
        {
            "title": "揲筮",
            "rows": [
                _row("揲筮模式", "手动复现" if payload.get("manual") else "自动随机/干支计算"),
                _row("手动六数", payload.get("manualSplits")),
                _row("上柱", payload.get("upperGanzhi")),
                _row("下柱", payload.get("lowerGanzhi")),
            ],
        },
    ]
    sections.extend([{"title": item["label"], "rows": item["rows"]} for item in positions])
    flags = []
    for item in positions:
        for flag in item.get("flags", []):
            flags.append(f"{item['label']}：{flag}")
    sections.append({"title": "特殊标记", "rows": [_row("标记", "；".join(flags) if flags else "无")]})
    return sections


def _build_snapshot(pan):
    lines = []
    for section in pan.get("sections", []):
        lines.append(f"[{section.get('title', '')}]")
        for row in section.get("rows", []):
            lines.append(f"{row.get('label')}：{row.get('value')}")
        lines.append("")
    return "\n".join(lines).strip()


def _manual_splits(data):
    if not data.get("manual"):
        return None
    raw = data.get("manualSplits") or []
    values = [_to_int(item, 1) for item in raw[:6]]
    while len(values) < 6:
        values.append(1)
    return [max(1, min(35, item)) for item in values]


def _calculate(mode, ganzhi, number, solar_term, lunar_month, manual_splits):
    if mode == "day":
        return wuzhao_core.five_zhao_paipan(number, solar_term, lunar_month, ganzhi[1], ganzhi[2], manual_splits=manual_splits), ganzhi[1], ganzhi[2]
    if mode == "hour":
        return wuzhao_core.five_zhao_paipan(number, solar_term, lunar_month, ganzhi[2], ganzhi[3], manual_splits=manual_splits), ganzhi[2], ganzhi[3]
    if mode == "minute":
        return wuzhao_core.five_zhao_paipan(number, solar_term, lunar_month, ganzhi[3], ganzhi[4], manual_splits=manual_splits), ganzhi[3], ganzhi[4]
    if mode == "tang":
        divination = wuzhao_core.WuzhaoDivination(
            jq=solar_term,
            cm=lunar_month,
            gz1=ganzhi[2],
            gz2=ganzhi[3],
            manual_splits=manual_splits,
        )
        return divination.divine(), ganzhi[2], ganzhi[3]
    return wuzhao_core.gangzhi_paipan(ganzhi, number, solar_term, lunar_month), ganzhi[3], ganzhi[4]


class WuZhaoSrv:
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
            year = _to_int(data.get("year"), 2025)
            month = _to_int(data.get("month"), 1)
            day = _to_int(data.get("day"), 1)
            hour = _to_int(data.get("hour"), 0)
            minute = _to_int(data.get("minute"), 0)
            mode = _clean_text(data.get("mode"), "ganzhi")
            if mode not in MODE_LABELS:
                mode = "ganzhi"
            number = max(0, min(90, _to_int(data.get("number"), 0)))
            if number > 9:
                number = number % 9
            manual_splits = _manual_splits(data)

            ganzhi = _json_safe(wuzhao_config.gangzhi(year, month, day, hour, minute))
            solar_term = wuzhao_jieqi.jq(year, month, day, hour, minute)
            lunar = _json_safe(wuzhao_config.lunar_date_d(year, month, day))
            lunar_month = _clean_text(lunar.get("農曆月", ""))[0] if lunar.get("農曆月") else "正"
            raw, upper_gz, lower_gz = _calculate(mode, ganzhi, number, solar_term, lunar_month, manual_splits)
            raw = _json_safe(raw)
            if isinstance(raw, dict) and raw.get("錯誤"):
                return jsonpickle.encode({"ResultCode": -1, "Result": raw.get("錯誤")}, unpicklable=False)

            positions = _normalize_positions(raw)
            normalized = {
                "source": "kinwuzhao",
                "engine": "kinwuzhao",
                "mode": mode,
                "modeLabel": MODE_LABELS[mode],
                "number": number,
                "manual": bool(manual_splits),
                "manualSplits": manual_splits or [],
                "dateStr": data.get("date", f"{year:04d}-{month:02d}-{day:02d}"),
                "timeStr": data.get("time", f"{hour:02d}:{minute:02d}:00"),
                "solarTerm": solar_term,
                "lunarDate": {
                    "raw": lunar,
                    "text": _lunar_text(lunar),
                    "month": lunar_month,
                },
                "ganzhi": {
                    "year": ganzhi[0] if len(ganzhi) > 0 else "",
                    "month": ganzhi[1] if len(ganzhi) > 1 else "",
                    "day": ganzhi[2] if len(ganzhi) > 2 else "",
                    "hour": ganzhi[3] if len(ganzhi) > 3 else "",
                    "minute": ganzhi[4] if len(ganzhi) > 4 else "",
                    "raw": ganzhi,
                },
                "upperGanzhi": upper_gz,
                "lowerGanzhi": lower_gz,
                "positions": positions,
                "raw": raw,
                "classics": _classic_sections(),
                "capabilities": {
                    "inputs": [
                        "date",
                        "time",
                        "mode",
                        "number",
                        "manualSplits",
                    ],
                    "modes": [{"key": key, "label": label} for key, label in MODE_LABELS.items()],
                    "outputs": [
                        "sixPositions",
                        "fiveElements",
                        "sixBeasts",
                        "sixRelations",
                        "guxu",
                        "lockKeyGeneral",
                        "prosperity",
                        "classicsBibliography",
                        "examples",
                        "updateLog",
                        "relatedLinks",
                    ],
                },
            }
            normalized["sections"] = _build_sections(normalized, positions)
            normalized["snapshot"] = _build_snapshot(normalized)
            return jsonpickle.encode({"ResultCode": 0, "Result": normalized}, unpicklable=False)
        except Exception:
            traceback.print_exc()
            return jsonpickle.encode({"ResultCode": -1, "Result": "wuzhao calculation failed"}, unpicklable=False)
