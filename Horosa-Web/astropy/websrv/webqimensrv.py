import os
import sys
import traceback
from numbers import Integral, Real

import cherrypy
import jsonpickle

from websrv.helper import enable_crossdomain


_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
_HOROSA_WEB_ROOT = os.path.abspath(os.path.join(_CUR_DIR, "..", ".."))
_KINQIMEN_SRC = os.path.join(_HOROSA_WEB_ROOT, "vendor", "kinqimen")
if os.path.isfile(os.path.join(_KINQIMEN_SRC, "kinqimen.py")) and _KINQIMEN_SRC not in sys.path:
    sys.path.insert(0, _KINQIMEN_SRC)

import config  # noqa: E402
import kinqimen  # noqa: E402


MODE_LABELS = {
    "year": "年家奇门",
    "hour": "时家奇门",
    "minute": "刻家奇门",
    "golden": "金函玉镜",
    "overall": "综合排盘",
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


def _palace_rows(raw):
    rows = []
    for gua in list("巽離坤震中兌艮坎乾"):
        parts = []
        for label, key in [("天盘", "天盤"), ("地盘", "地盤"), ("门", "門"), ("星", "星"), ("神", "神")]:
            val = raw.get(key, {}).get(gua, "") if isinstance(raw.get(key), dict) else ""
            if val:
                parts.append(f"{label}{val}")
        if parts:
            rows.append({"label": f"{gua}宫", "value": "、".join(parts)})
    return rows


def _build_sections(selected, all_raw, mode, option):
    sections = [{
        "title": "起盘",
        "rows": [
            _row("起盘方式", MODE_LABELS.get(mode, mode)),
            _row("排盘方式", selected.get("排盤方式", {1: "拆補", 2: "置閏"}.get(option, ""))),
            _row("干支", selected.get("干支")),
            _row("节气", selected.get("節氣")),
            _row("排局", selected.get("排局") or selected.get("局")),
            _row("旬首", selected.get("旬首")),
            _row("旬空", selected.get("旬空")),
            _row("局日", selected.get("局日")),
            _row("天乙", selected.get("天乙")),
        ],
    }]
    zfzs = selected.get("值符值使")
    if isinstance(zfzs, dict):
        sections.append({
            "title": "值符值使",
            "rows": [_row(key, val) for key, val in zfzs.items()],
        })
    palace = _palace_rows(selected)
    if palace:
        sections.append({"title": "九宫", "rows": palace})
    for title, key in [("马星", "馬星"), ("长生运", "長生運"), ("暗干飞干", "暗干")]:
        val = selected.get(key)
        if val:
            rows = [_row(key, val)]
            if key == "暗干" and selected.get("飛干"):
                rows.append(_row("飛干", selected.get("飛干")))
            sections.append({"title": title, "rows": rows})
    golden = all_raw.get("金函玉鏡(日家奇門)") if isinstance(all_raw, dict) else None
    if isinstance(golden, dict):
        sections.append({
            "title": "金函玉镜",
            "rows": [
                _row("局", golden.get("局")),
                _row("鹤神", golden.get("鶴神")),
                _row("星", golden.get("星")),
                _row("门", golden.get("門")),
                _row("神", golden.get("神")),
            ],
        })
    minute = all_raw.get("刻家奇門") if isinstance(all_raw, dict) else None
    if isinstance(minute, dict) and minute is not selected:
        sections.append({
            "title": "刻家奇门",
            "rows": [
                _row("干支", minute.get("干支")),
                _row("排局", minute.get("排局")),
                _row("值符值使", minute.get("值符值使")),
                _row("暗干", minute.get("暗干")),
                _row("飞干", minute.get("飛干")),
            ],
        })
    year_pan = ""
    if isinstance(selected.get("年家"), str):
        year_pan = selected.get("年家")
    elif isinstance(all_raw, dict) and isinstance(all_raw.get("年家奇門"), str):
        year_pan = all_raw.get("年家奇門")
    if year_pan:
        sections.append({"title": "年家", "rows": [_row("年家奇门", year_pan)]})
    return sections


def _mode_result(qimen_obj, mode, option):
    if mode == "year":
        return {"年家": qimen_obj.ypan()}
    if mode == "minute":
        return qimen_obj.pan_minute(option)
    if mode == "golden":
        return qimen_obj.gpan()
    if mode == "overall":
        return qimen_obj.pan(option)
    return qimen_obj.pan(option)


class QiMenSrv:
    exposed = True

    def OPTIONS(*args, **kwargs):
        enable_crossdomain()

    @cherrypy.expose
    @cherrypy.config(**{"tools.cors.on": True})
    @cherrypy.tools.json_in()
    def pan(self):
        enable_crossdomain()
        try:
            data = cherrypy.request.json or {}
            year = _to_int(data.get("year"), 0)
            month = _to_int(data.get("month"), 1)
            day = _to_int(data.get("day"), 1)
            hour = _to_int(data.get("hour"), 0)
            minute = _to_int(data.get("minute"), 0)
            option = 2 if _clean_text(data.get("qijuMethod")) == "zhirun" or _to_int(data.get("option"), 2) == 2 else 1
            mode = _clean_text(data.get("qimenMode"), "hour")
            if mode not in MODE_LABELS:
                mode = "hour"

            qimen_obj = kinqimen.Qimen(year, month, day, hour, minute)
            selected = _json_safe(_mode_result(qimen_obj, mode, option))
            all_raw = _json_safe(qimen_obj.overall(option))
            all_raw["年家奇門"] = qimen_obj.ypan()
            if mode == "golden":
                selected["年家"] = qimen_obj.ypan()
            normalized = {
                "source": "kinqimen",
                "engine": "kinqimen",
                "mode": mode,
                "modeLabel": MODE_LABELS.get(mode, mode),
                "dateStr": data.get("date", ""),
                "timeStr": data.get("time", ""),
                "realSunTime": data.get("realSunTime", ""),
                "jiedelta": data.get("jiedelta", ""),
                "qijuMethod": "zhirun" if option == 2 else "chaibu",
                "option": option,
                "selected": selected,
                "raw": selected,
                "allRaw": all_raw,
                "sections": _build_sections(selected, all_raw, mode, option),
                "capabilities": {
                    "modes": ["year", "hour", "minute", "golden", "overall"],
                    "methods": ["chaibu", "zhirun"],
                    "unsupportedByKinqimen": ["月家完整盘"],
                },
            }
            return jsonpickle.encode({
                "ResultCode": 0,
                "Result": normalized,
            }, unpicklable=False)
        except Exception:
            traceback.print_exc()
            return jsonpickle.encode({
                "ResultCode": -1,
                "Result": "qimen calculation failed",
            }, unpicklable=False)
