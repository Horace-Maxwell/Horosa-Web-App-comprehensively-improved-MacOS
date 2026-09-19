#!/usr/bin/env bash
# 打包产物前端冒烟(制度化,v3.3.3 脏构建事故后新增;踩坑记录 #48/#49/#50)。
#
# 干什么:对「会进 .pkg 的同一份 dist-file」做自动化健康检查——不等装机、不靠肉眼。
#   ①指纹可追溯:build-info.json 在位 + dirty=false + 构建 commit 与当前 HEAD 可对应(与 preflight[122] 同判据:
#     构建 commit = HEAD;或它是 HEAD 的祖先且两者之间前端源面零差异 —— 构建之后只有文档 / 发布脚本类提交时,产物仍与源码一一对应)。
#     「前端源面」= astrostudyui/scripts/fe-source-paths.txt 这一份清单(构建时判脏 / preflight[122] / 本脚本三处同读):
#     源码、静态资源、依赖清单与锁、构建配置、构建前后处理脚本;清单读不到 = 无从判定 → 按对应不上处理(fail-closed);
#   ②产物完整性:index.html/umi 主 bundle 在位且 index 引用的 hash 文件真实存在(打包取的就是这套字节);
#   ③静态服务可起:python3 -m http.server 试起并 curl index(200)——踩坑记录 #48 最廉判别的自动化前半;
#     端口按「真绑定」取空闲口、就绪按轮询等、服务进程无条件回收并复核端口已释放;
#   ④防回归锚:dist-file 内含 A 系列关键修复的编译产物特征(会话投毒守卫/浮层不透明变量)。
# 后半(浏览器实点推运盘/紫微/择日/悬浮窗)仍需人or preview 驱动——本脚本把「能自动的」全自动。
#
# 用法: bash scripts/verify_packaged_frontend.sh              (仓根或 Installer 目录均可)
#       bash scripts/verify_packaged_frontend.sh --self-test  (判据自证:指纹判定 / 端口探测各自的判别向量)
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DIST="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file"
fail=0
ok(){ printf '  \033[32m✅\033[0m %s\n' "$1"; }
bad(){ printf '  \033[31m❌\033[0m %s\n' "$1"; fail=1; }

# 前端源面:单源清单(与 write-build-info.js / preflight[122] 同读这一份;一行一个、相对 astrostudyui/、# 为注释)
FE_SRC_LIST_FILE="${REPO_ROOT}/Horosa-Web/astrostudyui/scripts/fe-source-paths.txt"
read_fe_src_paths(){ grep -avE '^[[:space:]]*(#|$)' "$1" 2>/dev/null | sed -e 's/[[:space:]]*$//' -e 's#^#Horosa-Web/astrostudyui/#' | tr '\n' ' '; }
FE_SRC_PATHS="$(read_fe_src_paths "${FE_SRC_LIST_FILE}")"

# 指纹判定:$1=构建 commit  $2=HEAD  [$3=仓根,缺省本仓] → same / ancestor-clean / mismatch
fingerprint_verdict(){
  local c="$1" h="$2" repo="${3:-${REPO_ROOT}}"
  if [ -z "${c}" ] || [ -z "${h}" ]; then echo mismatch; return; fi
  if [ -z "${FE_SRC_PATHS// /}" ]; then echo mismatch; return; fi     # 清单读不到:不猜,按对应不上处理
  if [ "${c}" = "${h}" ]; then echo same; return; fi
  # shellcheck disable=SC2086
  if git -C "${repo}" merge-base --is-ancestor "${c}" "${h}" 2>/dev/null \
     && [ -z "$(git -C "${repo}" diff --name-only "${c}" "${h}" -- ${FE_SRC_PATHS} 2>/dev/null)" ]; then
    echo ancestor-clean; return
  fi
  echo mismatch
}

# 取空闲端口:逐个「真绑定」试(不带地址复用)。只查监听表会漏掉由系统服务代持的口 —— 选中后服务起不来、请求悬挂到超时。
PICK_PORT_PY='
import socket, sys
start = int(sys.argv[1])
for port in range(start, start + 60):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
    except OSError:
        continue
    finally:
        s.close()
    print(port)
    break
'
pick_free_port(){ python3 -c "${PICK_PORT_PY}" "${1:-8019}" 2>/dev/null; }

if [ "${1:-}" = "--self-test" ]; then
  echo "== 打包产物前端冒烟 · 判据自证 =="
  ST_HEAD=$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo "")
  expect(){ if [ "$2" = "$3" ]; then ok "$1 → $2"; else bad "$1 → $2(应为 $3)"; fi; }
  expect "指纹 = HEAD" "$(fingerprint_verdict "${ST_HEAD}" "${ST_HEAD}")" same
  expect "指纹为空" "$(fingerprint_verdict "" "${ST_HEAD}")" mismatch
  expect "指纹不是仓内对象" "$(fingerprint_verdict 0000000000000000000000000000000000000000 "${ST_HEAD}")" mismatch
  # 沿一阶父链回溯:最近的「前端源面零差异」祖先必判 ancestor-clean;第一个「有差异」的祖先必判 mismatch
  ST_CLEAN=""; ST_DIFF=""
  for c in $(git -C "${REPO_ROOT}" rev-list --first-parent -n 200 "${ST_HEAD}" 2>/dev/null | tail -n +2); do
    # shellcheck disable=SC2086
    if [ -z "$(git -C "${REPO_ROOT}" diff --name-only "${c}" "${ST_HEAD}" -- ${FE_SRC_PATHS} 2>/dev/null)" ]; then
      [ -n "${ST_CLEAN}" ] || ST_CLEAN="${c}"
    else
      ST_DIFF="${c}"; break
    fi
  done
  if [ -n "${ST_CLEAN}" ]; then
    expect "祖先且前端源面零差异(${ST_CLEAN:0:12})" "$(fingerprint_verdict "${ST_CLEAN}" "${ST_HEAD}")" ancestor-clean
  else
    echo "  -  HEAD 自身改了前端源面,本仓此刻没有「零差异祖先」向量(不适用)"
  fi
  if [ -n "${ST_DIFF}" ]; then
    expect "祖先但前端源面有差异(${ST_DIFF:0:12})" "$(fingerprint_verdict "${ST_DIFF}" "${ST_HEAD}")" mismatch
  else
    bad "回溯 200 个提交未找到前端源面有差异的祖先 —— 向量缺席,拒绝出结论"
  fi
  # 合成仓向量(不依赖本仓历史):构建之后「只动构建脚本」「只动依赖锁」必须判对应不上,「只动文档」必须判可对应
  ST_T="$(mktemp -d)"
  ( cd "${ST_T}" && git init -q && git config user.email t@t && git config user.name t \
    && mkdir -p Horosa-Web/astrostudyui/src Horosa-Web/astrostudyui/scripts docs \
    && echo a > Horosa-Web/astrostudyui/src/a.js && echo p > Horosa-Web/astrostudyui/scripts/patch-dom-align-zoom.js \
    && echo l > Horosa-Web/astrostudyui/package-lock.json && echo d > docs/x.md \
    && git add -A >/dev/null && git commit -qm base \
    && echo p2 > Horosa-Web/astrostudyui/scripts/patch-dom-align-zoom.js && git commit -qam script \
    && echo d2 > docs/x.md && git commit -qam docs \
    && echo l2 > Horosa-Web/astrostudyui/package-lock.json && git commit -qam lock ) >/dev/null 2>&1
  ST_A="$(git -C "${ST_T}" rev-parse HEAD~3 2>/dev/null || echo "")"; ST_B="$(git -C "${ST_T}" rev-parse HEAD~2 2>/dev/null || echo "")"
  ST_C="$(git -C "${ST_T}" rev-parse HEAD~1 2>/dev/null || echo "")"; ST_D="$(git -C "${ST_T}" rev-parse HEAD 2>/dev/null || echo "")"
  if [ -n "${ST_A}" ] && [ -n "${ST_D}" ]; then
    expect "合成仓:构建后只动了构建前处理脚本" "$(fingerprint_verdict "${ST_A}" "${ST_B}" "${ST_T}")" mismatch
    expect "合成仓:构建后只动了文档" "$(fingerprint_verdict "${ST_B}" "${ST_C}" "${ST_T}")" ancestor-clean
    expect "合成仓:构建后只动了依赖锁" "$(fingerprint_verdict "${ST_C}" "${ST_D}" "${ST_T}")" mismatch
  else
    bad "合成仓没建起来 —— 向量缺席,拒绝出结论"
  fi
  find "${ST_T}" -mindepth 1 -delete 2>/dev/null; rmdir "${ST_T}" 2>/dev/null
  # 清单读不到时必须 fail-closed
  ST_KEEP="${FE_SRC_PATHS}"; FE_SRC_PATHS=""
  expect "清单为空(读不到)" "$(fingerprint_verdict "${ST_HEAD}" "${ST_HEAD}")" mismatch
  FE_SRC_PATHS="${ST_KEEP}"
  # 端口探测:占住首选口之后再取,必须避开它
  ST_P1=$(pick_free_port 8019)
  if [ -z "${ST_P1}" ]; then
    bad "端口探测没有给出任何端口"
  else
    python3 -c "import socket,sys,time; s=socket.socket(); s.bind(('127.0.0.1',int(sys.argv[1]))); s.listen(1); time.sleep(4)" "${ST_P1}" &
    ST_HOLD=$!
    sleep 0.8
    ST_P2=$(pick_free_port "${ST_P1}")
    kill "${ST_HOLD}" 2>/dev/null; wait "${ST_HOLD}" 2>/dev/null
    if [ -n "${ST_P2}" ] && [ "${ST_P2}" != "${ST_P1}" ]; then ok "端口探测避开已占用口(${ST_P1} → ${ST_P2})"; else bad "端口探测没有避开已占用口(${ST_P1} → ${ST_P2:-空})"; fi
  fi
  if [ "${fail}" -ne 0 ]; then echo "❌ 判据自证未过。" >&2; exit 1; fi
  echo "✅ 判据自证通过。"; exit 0
fi

echo "== 打包产物前端冒烟(${DIST}) =="

# ① 指纹可追溯
INFO="${DIST}/build-info.json"
if [ ! -f "${INFO}" ]; then
  bad "缺 build-info.json —— 旧产物或构建链未挂指纹,npm run build:file 重建"
else
  COMMIT=$(python3 -c "import json;print(json.load(open('${INFO}')).get('commit',''))" 2>/dev/null || echo "")
  DIRTY=$(python3 -c "import json;print(1 if json.load(open('${INFO}')).get('dirty') else 0)" 2>/dev/null || echo "1")
  HEAD=$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo "")
  [ "${DIRTY}" = "0" ] && ok "指纹 dirty=false(干净树构建)" || bad "指纹 dirty=true —— 脏树构建,先 commit 再重 build"
  [ -n "${FE_SRC_PATHS// /}" ] && ok "前端源面清单在位($(echo ${FE_SRC_PATHS} | wc -w | tr -d ' ') 项)" || bad "前端源面清单缺失或为空(${FE_SRC_LIST_FILE#${REPO_ROOT}/})—— 无从判定产物与源码是否对应"
  case "$(fingerprint_verdict "${COMMIT}" "${HEAD}")" in
    same) ok "指纹 commit=当前 HEAD(${COMMIT:0:12})" ;;
    ancestor-clean) ok "指纹 commit(${COMMIT:0:12}) 是 HEAD(${HEAD:0:12}) 的祖先且前端源面零差异(产物与源码可对应)" ;;
    *) bad "指纹 commit(${COMMIT:0:12}) 与 HEAD(${HEAD:0:12}) 对应不上(不是其祖先,或前端源面有差异) —— 重 build:file" ;;
  esac
fi

# ② 产物完整性:index 引用的 umi hash bundle 真实存在
if [ ! -f "${DIST}/index.html" ]; then
  bad "缺 index.html"
else
  UMI_JS=$(grep -oE 'umi\.[0-9a-f]+\.js' "${DIST}/index.html" | head -1)
  UMI_CSS=$(grep -oE 'umi\.[0-9a-f]+\.css' "${DIST}/index.html" | head -1)
  [ -n "${UMI_JS}" ] && [ -f "${DIST}/${UMI_JS}" ] && ok "index 引用的主 bundle 在位(${UMI_JS})" || bad "index 引用的 umi js 缺失(${UMI_JS:-未引用})"
  [ -z "${UMI_CSS}" ] || [ -f "${DIST}/${UMI_CSS}" ] && true || bad "index 引用的 umi css 缺失(${UMI_CSS})"
fi

# ③ 静态服务可起(踩坑记录 #48 最廉判别自动化)。服务直接后台起(`$!` 就是服务进程本身,不隔一层子 shell),
#    就绪按轮询等(冷盘首起可能超过 1 秒),无条件回收并复核端口已释放 —— 每跑一次不留一个残留进程。
HTTPD_PID=""
cleanup_httpd(){ if [ -n "${HTTPD_PID}" ]; then kill "${HTTPD_PID}" >/dev/null 2>&1; wait "${HTTPD_PID}" 2>/dev/null; HTTPD_PID=""; fi; }
trap cleanup_httpd EXIT
PORT=$(pick_free_port 8019)
CODE="000"
if [ -z "${PORT}" ]; then
  bad "静态服务冒烟:8019 起 60 个端口全部被占,无法试起"
else
  python3 -m http.server "${PORT}" --bind 127.0.0.1 --directory "${DIST}" >/dev/null 2>&1 &
  HTTPD_PID=$!
  for _ in $(seq 1 40); do
    kill -0 "${HTTPD_PID}" 2>/dev/null || break
    CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:${PORT}/index.html" 2>/dev/null)
    CODE="${CODE:-000}"
    [ "${CODE}" = "200" ] && break
    sleep 0.25
  done
  SRV_PID="${HTTPD_PID}"
  cleanup_httpd
  [ "${CODE}" = "200" ] && ok "静态服务冒烟 index 200(:${PORT});需人工深验时 launch.json horosa-prod(:8011) 连 dev 后端实点四症状" || bad "静态服务 index 非 200(${CODE})"
  # 回收复核看「进程已退 + 该口不再接受连接」;不拿「能否重新绑定」当判据 —— 刚断开的连接会让端口短暂不可重绑,那不是残留
  STILL_UP=$(python3 -c "import socket,sys; s=socket.socket(); s.settimeout(1); print(1 if s.connect_ex(('127.0.0.1',int(sys.argv[1])))==0 else 0)" "${PORT}" 2>/dev/null || echo 1)
  if ! kill -0 "${SRV_PID}" 2>/dev/null && [ "${STILL_UP}" = "0" ]; then ok "静态服务进程已回收(:${PORT} 不再监听)"; else bad "静态服务进程未回收(:${PORT} 仍在监听)"; fi
fi

# ④ 防回归锚:关键修复的编译产物特征(minify 后字符串字面量仍在)
BUNDLE="${DIST}/${UMI_JS:-}"
# ⚠️ 判据两坑(2026-07-12 实踩):①必须扫「全目录」——技法组件全走 React.lazy,守卫串在
#    *.async.js 懒 chunk、layouts 样式在 layouts__index.*.chunk.css,只查 umi.js/umi.css 恒伪红;
#    ②中文在压缩产物里可能是 \uXXXX 转义形态,grep 原文找不到 → 用 python 双形态检测。
if [ -n "${UMI_JS:-}" ] && [ -f "${BUNDLE}" ]; then
  GUARD_HIT=$(python3 - "${DIST}" <<'PYEOF'
import glob, sys
probe = '后端服务尚未就绪'
esc = ''.join('\\u%04x' % ord(c) for c in probe)
for f in glob.glob(sys.argv[1] + '/*.js'):
    s = open(f, encoding='utf-8', errors='ignore').read()
    if probe in s or esc in s:
        print('hit'); break
PYEOF
)
  [ "${GUARD_HIT}" = "hit" ] && ok "会话投毒守卫已入产物(空载荷人话提示)" || bad "产物缺会话投毒守卫特征——dist-file 陈旧?重 build:file"
  grep -alq -- "--horosa-surface-solid" "${DIST}"/*.css "${DIST}"/*.js 2>/dev/null && ok "浮层不透明变量已入产物" || bad "产物缺浮层不透明特征"
  grep -alq "horosa-floating-surface" "${DIST}"/*.css 2>/dev/null && ok "floating-surface 基类已入产物" || bad "产物缺 floating-surface 基类"
fi

echo "== 结果 =="
if [ "${fail}" -ne 0 ]; then echo "❌ 打包产物冒烟未过,禁止交付/发布。" >&2; exit 1; fi
echo "✅ 打包产物冒烟通过(自动面);人工面按 踩坑记录 #48:horosa-prod 起 :8011 实点 推运盘星体/紫微选项/择日控件/悬浮窗底。"
