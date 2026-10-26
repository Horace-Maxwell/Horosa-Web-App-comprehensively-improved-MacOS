#!/usr/bin/env bash
# 桌面壳外部接口真栈联调(零窗口):真桌面壳本机服务(Rust,REST 开)+ 真工具层(无头运行时当「页面」)+ 真桌面二进制的终端命令 + curl。
#   页面侧:Horosa-Web/astrostudyui/headless/pagehost.js(与壳 → 页面桥同一入口语义);
#   壳侧:mcp_server.rs 的 e2e_real_page_host(#[ignore],cargo test 拉起,写端点文件);
#   终端命令:target/debug 的桌面二进制 --horosa-cli(main() 建窗口前分流,零界面);REST / MCP:curl。
# 数据全在临时目录(HOROSA_HOME),不碰用户数据;不起 App、不开任何窗口。本机计算服务(:9999 / :8899)在跑时起盘类断言才有意义。
# 用法:bash Horosa_Desktop_Installer/scripts/verify_desktop_api_e2e.sh   退出码 0 = 全过。
set -u
# [exit-guard] bash 3.2:set -u 因未赋值变量中止时,EXIT trap 里拿到的 $? 是 0(失败会被报成成功)。显式 exit 都经下面的
#   exit 记一笔;进 EXIT 时没记过 = 中止,按失败计。EXIT trap 一律写成 trap 'hx_on_exit <原处理>' EXIT(处理函数里读到的 $?
#   已是改判后的值);脚本末尾必须显式 exit。检查器 check_shell_exit_guard.py 机检。
HX_EXITED=0; exit(){ local _hx_s=$?; HX_EXITED=1; if [ "$#" -eq 0 ]; then builtin exit "${_hx_s}"; fi; builtin exit "$@"; }
hx_status(){ return "$1"; }
hx_on_exit(){ local _hx_r=$?; if [ "${_hx_r}" = "0" ] && [ "${HX_EXITED}" != "1" ]; then _hx_r=1; fi; set +e; hx_status "${_hx_r}"; "$@"; builtin exit "${_hx_r}"; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UI="${ROOT}/Horosa-Web/astrostudyui"
TAURI="${ROOT}/Horosa_Desktop_Installer/src-tauri"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/horosa-desktop-e2e.XXXXXX")"
export HOROSA_HOME="${WORK}/home"
export HOROSA_NO_AUTOSTART=1
NODE_BIN="${HOROSA_NODE:-$(command -v node || true)}"
[ -x "${ROOT}/.runtime/mac/node/bin/node" ] && [ -z "${HOROSA_NODE:-}" ] && NODE_BIN="${ROOT}/.runtime/mac/node/bin/node"
pass=0; failn=0
ok(){ pass=$((pass+1)); printf '  ✅ %s\n' "$1"; }
no(){ failn=$((failn+1)); printf '  ❌ %s\n' "$1"; [ -n "${2:-}" ] && printf '     %s\n' "$(printf '%s' "$2" | tr '\n' ' ' | cut -c1-240)"; }
has(){ printf '%s' "$1" | grep -qF -- "$2"; }
PAGE_PID=""; SHELL_PID=""
cleanup(){
  touch "${WORK}/stop" 2>/dev/null
  [ -n "${PAGE_PID}" ] && kill "${PAGE_PID}" 2>/dev/null
  [ -n "${SHELL_PID}" ] && wait "${SHELL_PID}" 2>/dev/null
  rm -rf "${WORK}"
}
trap 'hx_on_exit cleanup' EXIT

[ -n "${NODE_BIN}" ] || { echo "需要 Node.js 18+(./horosa setup 会装)" >&2; exit 2; }
echo "== 编译桌面壳(debug)与联调宿主"
cargo build --manifest-path "${TAURI}/Cargo.toml" >"${WORK}/build.log" 2>&1 || { tail -20 "${WORK}/build.log"; exit 1; }
BIN="${TAURI}/target/debug/horosa-desktop-installer"
cargo test --manifest-path "${TAURI}/Cargo.toml" --no-run >"${WORK}/build-test.log" 2>&1 || { tail -20 "${WORK}/build-test.log"; exit 1; }

echo "== 起页面宿主(真工具层)"
"${NODE_BIN}" "${UI}/headless/pagehost.js" 0 "${WORK}/page.ready" >"${WORK}/page.log" 2>&1 &
PAGE_PID=$!
for _ in $(seq 1 100); do [ -s "${WORK}/page.ready" ] && break; sleep 0.2; done
[ -s "${WORK}/page.ready" ] || { cat "${WORK}/page.log"; exit 1; }
PAGE_PORT="$(head -1 "${WORK}/page.ready")"

echo "== 起桌面壳本机服务(REST 开)"
HOROSA_E2E_PAGE_URL="http://127.0.0.1:${PAGE_PORT}" HOROSA_E2E_ENDPOINT="${WORK}/endpoint.json" HOROSA_E2E_STOP="${WORK}/stop" \
  cargo test --manifest-path "${TAURI}/Cargo.toml" -- --ignored e2e_real_page_host --nocapture >"${WORK}/shell.log" 2>&1 &
SHELL_PID=$!
for _ in $(seq 1 150); do [ -s "${WORK}/endpoint.json" ] && break; sleep 0.2; done
[ -s "${WORK}/endpoint.json" ] || { tail -20 "${WORK}/shell.log"; exit 1; }
EP="${WORK}/endpoint.json"
TOKEN="$("${NODE_BIN}" -p "require('${EP}').token")"
MCP="$("${NODE_BIN}" -p "require('${EP}').url")"
REST="${MCP%/mcp}/api/v1"
H(){ "${BIN}" --horosa-cli --endpoint "${EP}" "$@"; }

echo "== 终端命令(桌面二进制 --horosa-cli)"
out="$(H status 2>&1)"; [ $? -eq 0 ] && has "${out}" "运行中" && ok "status" || no "status" "${out}"
out="$(H tools 2>&1)"; has "${out}" "search_celebrities" && has "${out}" "cast_technique" && ok "tools 含名人库与起盘" || no "tools" "${out}"
out="$(H call create_chart_record name=桌面联调 "birth=1990-01-01 08:00" place=北京 gender=male --json 2>&1)"
CID="$(printf '%s' "${out}" | "${NODE_BIN}" -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{console.log(JSON.parse(s).structuredContent.cid)}catch(e){console.log("")}})')"
[ -n "${CID}" ] && ok "建命盘 ${CID}" || no "建命盘" "${out}"
out="$(H records 桌面联调 2>&1)"; has "${out}" "桌面联调" && ok "records 简写" || no "records" "${out}"
out="$(H call cast_technique technique=bazi "source:={\"kind\":\"record\",\"cid\":\"${CID}\"}" maxChars:=800 2>&1)"; [ $? -eq 0 ] && [ ${#out} -gt 100 ] && ok "起盘(八字)" || no "起盘" "${out}"
out="$(H call search_celebrities query=爱因斯坦 limit:=2 --json 2>&1)"; has "${out}" "adb-2939" && ok "名人库检索" || no "名人库检索" "${out}"
out="$(H call search_zeri school=qimen start=2026-04-01 end=2026-04-10 place=北京 'conditions:={"type":"door","params":{"values":["开"],"palaces":[2]}}' --progress 2>&1 >/dev/null)"; [ $? -eq 0 ] && has "${out}" "[" && ok "奇门择日 + 进度行" || no "奇门择日" "${out}"
out="$(H read "horosa://chart/${CID}" 2>&1)"; rc=$?; [ "${rc}" -eq 0 ] && [ ${#out} -gt 50 ] && has "${out}" "桌面联调" && ok "读资源" || no "读资源(退出码 ${rc})" "${out}"
out="$(H prompts 2>&1)"; has "${out}" "guide:horosa" && ok "提示" || no "提示" "${out}"
H frobnicate >/dev/null 2>&1; [ $? -eq 2 ] && ok "用法错回 2" || no "用法错回 2"
"${NODE_BIN}" -e "const f='${EP}';const j=require(f);j.token='tok_WRONGWRONGWRONGWRONGWRONG000';require('fs').writeFileSync('${WORK}/bad.json',JSON.stringify(j))"
"${BIN}" --horosa-cli --endpoint "${WORK}/bad.json" tools >/dev/null 2>&1; [ $? -eq 4 ] && ok "令牌不对回 4" || no "令牌不对回 4"
# 区间取几十年、条件放宽:0.4 秒内不可能跑完 —— 退出码 0 不再记绿(旧写法把「调用已跑完」也算过,Ctrl-C 坏了照样绿)
"${BIN}" --horosa-cli --endpoint "${EP}" call search_zeri school=bazi start=1950-01-01 end=2049-12-31 place=北京 'conditions:={"type":"day_ganzhi","params":{"values":["甲","乙","丙","丁","戊"]}}' >/dev/null 2>"${WORK}/cc.err" &
CC=$!; sleep 0.4; kill -INT "${CC}" 2>/dev/null; wait "${CC}"; rc=$?
[ "${rc}" -eq 130 ] && ok "Ctrl-C 回 130" || no "Ctrl-C 回 130(实际 ${rc};0 = 中断前已跑完,说明中断没生效或区间不够长)" "$(cat "${WORK}/cc.err")"

echo "== REST(curl)"
code="$(curl -s -o /dev/null -w '%{http_code}' "${REST}/tools")"; [ "${code}" = "401" ] && ok "REST 无令牌 401" || no "REST 无令牌 401(实际 ${code})"
A=(-H "Authorization: Bearer ${TOKEN}")
# 壳侧限流(每分钟 60、突发 10)是真实行为:被限流就按提示等一下再试(最多 5 次)
C(){ local r i; for i in 1 2 3 4 5; do r="$(curl -s "$@")"; case "${r}" in *'"rate limited"'*|*'"code":-32004'*) sleep 1.2;; *) break;; esac; done; printf '%s' "${r}"; }
out="$(C "${A[@]}" "${REST}")"; has "${out}" '"base":"/api/v1"' && ok "REST 索引" || no "REST 索引" "${out}"
out="$(C "${A[@]}" "${REST}/records?query=%E6%A1%8C%E9%9D%A2")"; has "${out}" "桌面联调" && ok "REST GET 简写" || no "REST GET 简写" "${out}"
out="$(C "${A[@]}" -H 'Content-Type: application/json' -d '{"query":"爱因斯坦","limit":2}' "${REST}/tools/search_celebrities")"; has "${out}" "adb-2939" && ok "REST 调用(名人库)" || no "REST 调用" "${out}"
out="$(C "${A[@]}" -H 'Content-Type: application/json' -d '{"school":"huangli","start":"2026-03-01","end":"2026-03-31","conditions":{"type":"jianchu","params":{"values":["成"]}}}' "${REST}/tools/search_zeri?stream=1")"
# 失败结果同样以 event: result 收尾:还要没有出错标记、结果里真有命中日
if has "${out}" "event: result" && has "${out}" '"ok":true' && ! has "${out}" '"ok":false' && ! has "${out}" "event: error" && has "${out}" "2026-03"; then ok "REST 事件流"; else no "REST 事件流(缺结果 / 结果是出错 / 没有命中日)" "${out}"; fi
out="$(C "${A[@]}" "${REST}/openapi.json")"; has "${out}" "/tools/create_celebrity_chart" && ok "REST OpenAPI" || no "REST OpenAPI" "${out}"
out="$(C "${A[@]}" "${REST}/resources/read?uri=horosa%3A%2F%2Fchart%2F${CID}")"; has "${out}" '"contents"' && ok "REST 读资源" || no "REST 读资源" "${out}"
echo "== MCP(curl)"
out="$(C "${A[@]}" -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' "${MCP}")"; has "${out}" "create_celebrity_chart" && ok "MCP tools/list" || no "MCP tools/list" "${out}"

echo "== 结果:${pass} 过 / ${failn} 没过"
[ "${failn}" -eq 0 ]
exit "$?"
