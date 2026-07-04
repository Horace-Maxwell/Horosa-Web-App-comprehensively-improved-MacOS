#!/usr/bin/env bash
# ============================================================================
# 启动阶梯 ladder(WS-3a):首启/温启各段耗时基线与回归对比。
#
# 两档:
#   script 档(CI 可跑): bash tools/mac/startup_ladder.sh script [N]
#     —— 循环 N 次(默认 3)start_horosa_local.sh → 收账本 → stop;
#        第 1 轮标 cold(相对冷:进程/JVM/页缓存冷),其余标 warm。
#   report 档(app 档汇总): bash tools/mac/startup_ladder.sh report <jsonl文件或目录>...
#     —— 汇总任意启动账本(含发货 app 的
#        ~/Library/Application Support/<bundle-id>/logs/<run>/horosa-startup-ledger.jsonl,
#        app 档含 rust.* 段;script 档只有 sh./py./java. 三层)。
#
# 输出:每段 count/min/p50/p95/max(冷温分列)+ CSV 落 build/ladder/。
# 用途:任何性能改动 改前跑一轮留档,改后对比——「变快了多少」用数字说话,
#       首启劣化必须能在此给出「换来了什么暖后收益」的交换账。
# ============================================================================
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WEB_ROOT="${REPO_ROOT}/Horosa-Web"
OUT_ROOT="${REPO_ROOT}/Horosa_Desktop_Installer/build/ladder"
mkdir -p "${OUT_ROOT}"

summarize() {
  python3 - "$@" <<'PYSUM'
import csv, json, os, pathlib, statistics, sys, time

paths = []
for arg in sys.argv[1:]:
    p = pathlib.Path(arg)
    if p.is_dir():
        paths.extend(sorted(p.rglob('*.jsonl')))
    elif p.is_file():
        paths.append(p)
if not paths:
    raise SystemExit('没有账本文件可汇总')

# 每个 run: {seg: t_ms};段耗时优先取 extra.ms(显式段长),否则用 t_ms(相对起点的完成时刻)
runs = {}
labels = {}
for p in paths:
    for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        run = str(row.get('run', p.stem))
        seg = row.get('seg')
        if not seg:
            continue
        t = row.get('t_ms')
        extra = row.get('extra') or {}
        ms = extra.get('ms') if isinstance(extra, dict) else None
        runs.setdefault(run, {})[seg] = {'t_ms': t, 'ms': ms}
        labels.setdefault(run, 'cold' if 'cold' in run else ('warm' if 'warm' in run else ''))

def pct(vals, q):
    vals = sorted(vals)
    if not vals:
        return None
    idx = min(len(vals) - 1, max(0, round(q * (len(vals) - 1))))
    return vals[idx]

# 汇总维度:seg × (cold|warm|all)
segs = sorted({s for r in runs.values() for s in r})
groups = {'all': list(runs)}
if any(v == 'cold' for v in labels.values()):
    groups['cold'] = [r for r in runs if labels.get(r) == 'cold']
    groups['warm'] = [r for r in runs if labels.get(r) == 'warm']

out_dir = pathlib.Path(os.environ.get('LADDER_OUT', '.'))
csv_path = out_dir / f"ladder-{time.strftime('%Y%m%d-%H%M%S')}.csv"
rows_out = []
print(f"\n== 启动阶梯汇总({len(runs)} 次启动;t_ms=段完成时刻,ms=段长)==")
for gname, members in groups.items():
    if not members:
        continue
    print(f"\n-- {gname}({len(members)} 次)--")
    print(f"{'seg':<28}{'metric':<7}{'n':>3}{'min':>9}{'p50':>9}{'p95':>9}{'max':>9}")
    for seg in segs:
        for metric in ('t_ms', 'ms'):
            vals = [runs[r][seg][metric] for r in members if seg in runs[r] and runs[r][seg][metric] is not None]
            if not vals:
                continue
            row = dict(group=gname, seg=seg, metric=metric, n=len(vals),
                       min=min(vals), p50=pct(vals, 0.5), p95=pct(vals, 0.95), max=max(vals))
            rows_out.append(row)
            print(f"{seg:<28}{metric:<7}{len(vals):>3}{min(vals):>9}{row['p50']:>9}{row['p95']:>9}{max(vals):>9}")
with open(csv_path, 'w', newline='') as fh:
    writer = csv.DictWriter(fh, fieldnames=['group', 'seg', 'metric', 'n', 'min', 'p50', 'p95', 'max'])
    writer.writeheader()
    writer.writerows(rows_out)
print(f"\nCSV: {csv_path}")
PYSUM
}

mode="${1:-script}"
case "${mode}" in
  script)
    N="${2:-3}"
    STAMP="$(date +%Y%m%d-%H%M%S)"
    RUN_DIR="${OUT_ROOT}/script-${STAMP}"
    mkdir -p "${RUN_DIR}"
    echo "script 档 ladder:${N} 次 start/stop 循环(第 1 次=cold,其余=warm)"
    for i in $(seq 1 "${N}"); do
      label="warm"; [ "${i}" = "1" ] && label="cold"
      tag="ladder-${label}-${i}"
      ledger="${RUN_DIR}/${tag}.jsonl"
      echo "-- 第 ${i}/${N} 次(${label})…"
      (cd "${WEB_ROOT}" && HOROSA_RUN_TAG="${tag}" HOROSA_LEDGER_FILE="${ledger}" \
        bash start_horosa_local.sh >"${RUN_DIR}/${tag}.out" 2>&1) || {
        echo "启动失败,日志: ${RUN_DIR}/${tag}.out" >&2; exit 1; }
      (cd "${WEB_ROOT}" && bash stop_horosa_local.sh >/dev/null 2>&1) || true
      sleep 1
    done
    LADDER_OUT="${RUN_DIR}" summarize "${RUN_DIR}"
    ;;
  report)
    shift
    [ "$#" -ge 1 ] || { echo "用法: startup_ladder.sh report <jsonl文件或目录>..." >&2; exit 1; }
    LADDER_OUT="${OUT_ROOT}" summarize "$@"
    ;;
  *)
    echo "用法: startup_ladder.sh script [N] | report <jsonl文件或目录>..." >&2
    exit 1
    ;;
esac
