# -*- coding: utf-8 -*-
"""结构化启动账本(Python 层写入端)。

一行一段 JSON(JSON Lines),四层进程(Rust/shell/Java/Python)经 env 共享同一文件:
  HOROSA_LEDGER_FILE  账本文件绝对路径(缺省=不写,零开销)
  HOROSA_RUN_TAG      本次启动运行标签(Rust/shell 生成,四层同值,可按 run 聚合)
  HOROSA_STARTUP_LEDGER=0  总开关(默认开)

行 schema: {"run","seg","pid","layer":"py","t_ms","ms","extra"}
- t_ms: 自进程可见的最早时刻(见 webchartsrv 顶部 _PY_T0)到打点的毫秒;
- ms:   该段自身耗时(调用方给,可省)。
写入 append + best-effort 吞错:账本绝不影响业务。依赖仅 stdlib(os/json/time)。
"""
import json
import os
import time

_LEDGER_FILE = os.environ.get('HOROSA_LEDGER_FILE') or ''
_RUN_TAG = os.environ.get('HOROSA_RUN_TAG') or ''
_ENABLED = os.environ.get('HOROSA_STARTUP_LEDGER', '1').lower() not in ('0', 'false', 'no', 'off')
_PID = os.getpid()


def ledger_enabled():
    return bool(_ENABLED and _LEDGER_FILE)


def ledger_mark(seg, t0=None, ms=None, extra=None):
    """打一段。t0=perf_counter 基准(算 t_ms 用,可省);ms=段自身耗时毫秒(可省)。"""
    if not ledger_enabled():
        return
    try:
        row = {'run': _RUN_TAG, 'layer': 'py', 'seg': seg, 'pid': _PID}
        if t0 is not None:
            row['t_ms'] = round((time.perf_counter() - t0) * 1000.0, 1)
        if ms is not None:
            row['ms'] = round(float(ms), 1)
        if extra:
            row['extra'] = extra
        with open(_LEDGER_FILE, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')
    except Exception:
        pass
