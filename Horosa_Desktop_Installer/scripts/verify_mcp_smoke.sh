#!/usr/bin/env bash
# 外部智能体连接(本机 MCP 服务)冒烟:读端点文件 → /healthz → 无令牌 401 → 坏 Origin 403 → GET 405
# → initialize / tools/list / tools/call(只读工具) 全链;可选 --expect-down 断言零监听+端点文件消失。
# 用法: bash scripts/verify_mcp_smoke.sh [--expect-down] [--endpoint <path>] [--log] [--stdio <App 二进制>] [--headless] [--modern]
#   --modern:再走一遍 2026-07-28 无状态纪元(server/discover · 每请求 _meta · MCP-Protocol-Version/Mcp-Method/Mcp-Name 三头校验 · resultType/ttlMs/cacheScope · subscriptions/listen);与 --stdio 同用时 stdio 代理也走现代两行
#   --stdio <binary>:再经「<binary> --horosa-mcp-stdio <端点文件>」走一遍 ping/tools/list(stdio 代理形态,Claude Desktop 用)
#   --headless:断言 tools/list 含 run_analysis 并调一次(须先在「外部连接」里开「无头分析出口」)
#   --log:全绿后往 SELFCHECK_LOG.md 追加一行留档(发版门 HOROSA_RELEASE_GATE=1 时 preflight 会查这行)
#   缺省腿另查:2025-11-25 握手 · completions · 工具 title/outputSchema 透传 · 补全 · 坏游标 · 进度帧(本请求响应流)
set -euo pipefail
EXPECT_DOWN=0
ENDPOINT=""
WRITE_LOG=0
STDIO_BIN=""
HEADLESS=0
MODERN=0
while [ $# -gt 0 ]; do
  case "$1" in
    --expect-down) EXPECT_DOWN=1 ;;
    --log) WRITE_LOG=1 ;;
    --endpoint) shift; ENDPOINT="$1" ;;
    --stdio) shift; STDIO_BIN="$1" ;;
    --headless) HEADLESS=1 ;;
    --modern) MODERN=1 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done
if [ -z "$ENDPOINT" ]; then
  for d in "$HOME/Library/Application Support"/*orosa*; do
    [ -f "$d/mcp-endpoint.json" ] && ENDPOINT="$d/mcp-endpoint.json" && break
  done
fi
fail(){ echo "✗ $*" >&2; exit 1; }
ok(){ echo "✓ $*"; }

if [ "$EXPECT_DOWN" = "1" ]; then
  [ -z "$ENDPOINT" ] || [ ! -f "$ENDPOINT" ] || fail "端点文件仍在: $ENDPOINT"
  if grep -q LISTEN < <(lsof -nP -iTCP:39991-39999 -sTCP:LISTEN 2>/dev/null); then fail "39991-39999 仍有监听"; fi
  ok "关闭态:零监听、零端点文件"
  exit 0
fi

[ -n "$ENDPOINT" ] && [ -f "$ENDPOINT" ] || fail "找不到端点文件(服务未开启?)"
URL=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['url'])" "$ENDPOINT")
TOKEN=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['token'])" "$ENDPOINT")
PID=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['pid'])" "$ENDPOINT")
BASE=${URL%/mcp}
kill -0 "$PID" 2>/dev/null || fail "端点文件 pid $PID 不存活(陈旧文件)"
ok "端点 $URL pid=$PID"

code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/healthz"); [ "$code" = "200" ] || fail "/healthz 期望 200 得 $code"; ok "/healthz 200"
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"ping"}'); [ "$code" = "401" ] || fail "无令牌期望 401 得 $code"; ok "无令牌 401"
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Origin: https://evil.example' -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"ping"}'); [ "$code" = "403" ] || fail "坏 Origin 期望 403 得 $code"; ok "坏 Origin 403"
# GET /mcp 已是 SSE 通道:门在语义之前(无令牌 401);带令牌但不声明 Accept → 406;PUT 仍 405
code=$(curl -s -o /dev/null -w '%{http_code}' "$URL"); [ "$code" = "401" ] || fail "GET 无令牌期望 401 得 $code"; ok "GET 无令牌 401"
code=$(curl -s -o /dev/null -w '%{http_code}' "$URL" -H "Authorization: Bearer $TOKEN"); [ "$code" = "406" ] || fail "GET 无 Accept 期望 406 得 $code"; ok "GET 无 Accept 406"
code=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$URL" -H "Authorization: Bearer $TOKEN"); [ "$code" = "405" ] || fail "PUT 期望 405 得 $code"; ok "PUT 405"
rpc(){ curl -s -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H 'MCP-Protocol-Version: 2025-06-18' -d "$1"; }
init=$(rpc '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}')
grep -q '"serverInfo"' <<< "$init" || fail "initialize 无 serverInfo: $init"; ok "initialize"
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'); [ "$code" = "202" ] || fail "通知期望 202 得 $code"; ok "notification 202"
list=$(rpc '{"jsonrpc":"2.0","id":2,"method":"tools/list"}')
grep -q '"create_chart_record"' <<< "$list" || fail "tools/list 缺 create_chart_record(页面桥未就绪或总开关关?): $list"
grep -q 'delete' <<< "$list" && fail "tools/list 出现删除类工具名"
ok "tools/list 含只增工具、零删改类"
call=$(rpc '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_current_context","arguments":{}}}')
grep -q '"content"' <<< "$call" || fail "tools/call 无 content: $call"
grep -q '"isError":false' <<< "$call" || fail "tools/call isError 非 false: $call"
ok "tools/call get_current_context"
batch=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '[{"jsonrpc":"2.0","id":1,"method":"ping"}]'); [ "$batch" = "400" ] || fail "batch 期望 400 得 $batch"; ok "batch 拒 400"
# ── 协议层补齐:2025-11-25 握手 / completions 能力 / 工具全字段透传 / 补全 / 坏游标 / 进度帧走本请求响应流 ──
i25=$(curl -s -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":40,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}')
grep -q '"protocolVersion":"2025-11-25"' <<< "$i25" || fail "2025-11-25 握手未原样协商: $i25"
grep -q '"completions"' <<< "$i25" || fail "initialize 未宣告 completions: $i25"
ok "initialize 2025-11-25 + completions 能力"
grep -q '"title"' <<< "$list" || fail "tools/list 未透传 title(中文展示名): $list"
grep -q '"outputSchema"' <<< "$list" || fail "tools/list 未透传 outputSchema: $list"
grep -qE '"level":"(read|additive)"' <<< "$list" && fail "tools/list 泄出内部字段 level"
ok "tools/list 透传 title / outputSchema,内部字段不出壳"
cmp=$(rpc '{"jsonrpc":"2.0","id":41,"method":"completion/complete","params":{"ref":{"type":"ref/resource","uri":"horosa://chart/{cid}"},"argument":{"name":"cid","value":""}}}')
grep -q '"completion"' <<< "$cmp" || fail "completion/complete 无 completion: $cmp"
ok "completion/complete(命盘 cid)"
bc=$(rpc '{"jsonrpc":"2.0","id":42,"method":"resources/list","params":{"cursor":"__bad__"}}')
grep -q -- '-32602' <<< "$bc" || fail "坏游标期望 -32602: $bc"
ok "resources/list 坏游标 → -32602"
pg_sse=$(curl -s -N --max-time 30 -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2025-11-25' -d '{"jsonrpc":"2.0","id":43,"method":"tools/call","params":{"name":"get_current_context","arguments":{},"_meta":{"progressToken":"smoke-p"}}}')
grep -q 'notifications/progress' <<< "$pg_sse" || fail "带 progressToken 的调用未收到进度帧: $pg_sse"
grep -q '"progressToken":"smoke-p"' <<< "$pg_sse" || fail "进度帧未带回客户端的令牌: $pg_sse"
grep -q '"id":43' <<< "$pg_sse" || fail "响应流里缺最终回包: $pg_sse"
ok "进度帧 + 回包同一响应流(分块收尾)"

# ── 无头出口:run_analysis 只在 MCP 目录里出现(页面内模型永远看不到)──
# 长分析可能超过页面缺省预算(117 s):客户端应带 _meta.timeoutMs(这里 300 s;壳钳 1..600 s)
if [ "$HEADLESS" = "1" ]; then
  grep -q '"run_analysis"' <<< "$list" || fail "--headless:tools/list 缺 run_analysis(先在「外部连接」里开「无头分析出口」)"
  ha=$(rpc '{"jsonrpc":"2.0","id":30,"method":"tools/call","params":{"name":"run_analysis","arguments":{"question":"一句话自我介绍(冒烟)"},"_meta":{"timeoutMs":300000}}}')
  grep -q '"content"' <<< "$ha" || fail "run_analysis 无 content: $ha"
  grep -q '"isError":false' <<< "$ha" || fail "run_analysis isError 非 false: $ha"
  ok "run_analysis 无头出口"
fi
# ── stdio 代理:同一份 App 二进制 + 端点文件,一行进一行出 ──
if [ -n "$STDIO_BIN" ]; then
  [ -x "$STDIO_BIN" ] || fail "--stdio 二进制不可执行: $STDIO_BIN"
  sio=$(printf '%s\n%s\n%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke-stdio","version":"0"}}}' '{"jsonrpc":"2.0","method":"notifications/initialized"}' '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | "$STDIO_BIN" --horosa-mcp-stdio "$ENDPOINT" 2>/dev/null)
  [ "$(printf '%s\n' "$sio" | grep -c '"jsonrpc"')" = "2" ] || fail "stdio 代理应恰回两行(initialize + tools/list),实际: $sio"
  grep -q '"serverInfo"' <<< "$sio" || fail "stdio 代理 initialize 无 serverInfo"
  grep -q '"create_chart_record"' <<< "$sio" || fail "stdio 代理 tools/list 缺工具"
  grep -q "$TOKEN" <<< "$sio" && fail "stdio 代理输出里出现令牌"
  ok "stdio 代理 initialize/tools/list(通知零输出、令牌不外泄)"
fi
# ── v2:能力位 / 资源面 / 提示面 / SSE / 会话 ──────────────────────────
grep -q '"resources"' <<< "$init" || fail "initialize 未宣告 resources 能力: $init"
grep -q '"prompts"' <<< "$init" || fail "initialize 未宣告 prompts 能力: $init"
grep -q '"listChanged":true' <<< "$init" || fail "initialize 未宣告 listChanged: $init"
ok "initialize 宣告 tools/resources/prompts/logging"
grep -q '"ext_' <<< "$list" && fail "tools/list 出现外部接进来的工具(ext_ 前缀不得再导出)"
ok "tools/list 零 ext_ 前缀"
res=$(rpc '{"jsonrpc":"2.0","id":10,"method":"resources/list"}')
grep -q '"resources"' <<< "$res" || fail "resources/list 无 resources: $res"
grep -q 'horosa://' <<< "$res" || fail "resources/list 无 horosa:// URI(页面桥未就绪?): $res"
ok "resources/list"
tpl=$(rpc '{"jsonrpc":"2.0","id":11,"method":"resources/templates/list"}')
grep -q 'horosa://chart/{cid}' <<< "$tpl" || fail "resources/templates/list 缺命盘模板: $tpl"
ok "resources/templates/list"
uri=$(echo "$res" | sed -n 's/.*"uri":"\(horosa:\/\/[^"]*\)".*/\1/p' | head -1)
if [ -n "$uri" ]; then
  read=$(rpc "{\"jsonrpc\":\"2.0\",\"id\":12,\"method\":\"resources/read\",\"params\":{\"uri\":\"$uri\"}}")
  grep -q '"contents"' <<< "$read" || fail "resources/read 无 contents: $read"
  ok "resources/read $uri"
else
  ok "resources/read 跳过(本机无命盘/事盘/资料)"
fi
bad=$(rpc '{"jsonrpc":"2.0","id":13,"method":"resources/read","params":{"uri":"horosa://chart/__nope__"}}')
grep -q '"error"' <<< "$bad" || fail "未知资源应报错: $bad"; ok "未知资源 → error"
pl=$(rpc '{"jsonrpc":"2.0","id":14,"method":"prompts/list"}')
grep -q 'technique:' <<< "$pl" || fail "prompts/list 缺技法提示卡: $pl"; ok "prompts/list"
pg=$(rpc '{"jsonrpc":"2.0","id":15,"method":"prompts/get","params":{"name":"technique:bazi","arguments":{}}}')
grep -q '"messages"' <<< "$pg" || fail "prompts/get 无 messages: $pg"
grep -q 'cast_technique' <<< "$pg" || fail "提示卡未指向 cast_technique: $pg"; ok "prompts/get technique:bazi"
lg=$(rpc '{"jsonrpc":"2.0","id":16,"method":"logging/setLevel","params":{"level":"info"}}')
grep -q '"result"' <<< "$lg" || fail "logging/setLevel 失败: $lg"; ok "logging/setLevel"
# SSE:15s 内至少收到一条帧(keep-alive 或通知);curl 到点自断
sse=$(curl -s --max-time 3 "$URL" -H "Authorization: Bearer $TOKEN" -H 'Accept: text/event-stream' | head -c 200 || true)
grep -q ':' <<< "$sse" || fail "SSE 未收到任何帧: $sse"; ok "SSE 建流(收到首帧)"
# 会话:initialize 回的 Mcp-Session-Id 可用;DELETE 关闭后再用即 404
sid=$(curl -s -D - -o /dev/null -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":20,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' | tr -d '\r' | sed -n 's/^[Mm]cp-[Ss]ession-[Ii]d: //p' | head -1)
[ -n "$sid" ] || fail "initialize 未回 Mcp-Session-Id"
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H "Mcp-Session-Id: $sid" -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":21,"method":"ping"}'); [ "$code" = "200" ] || fail "带会话 ping 期望 200 得 $code"
code=$(curl -s -o /dev/null -w '%{http_code}' -X DELETE "$URL" -H "Authorization: Bearer $TOKEN" -H "Mcp-Session-Id: $sid"); [ "$code" = "204" ] || fail "DELETE 期望 204 得 $code"
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H "Mcp-Session-Id: $sid" -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":22,"method":"ping"}'); [ "$code" = "404" ] || fail "已关会话期望 404 得 $code"
ok "会话:发放 → 可用 → DELETE 204 → 再用 404"
# ── 2026-07-28 无状态纪元(--modern):无 initialize / 无会话;每请求带 _meta 与三头;错误码 -32020/-32022/-32601 各走一遍 ──
if [ "$MODERN" = "1" ]; then
  M='"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"smoke-modern","version":"0"},"io.modelcontextprotocol/clientCapabilities":{}}'
  mrpc(){ if [ -n "${2:-}" ]; then curl -s -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2026-07-28' -H "Mcp-Method: $1" -H "Mcp-Name: $2" -d "$3"; else curl -s -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2026-07-28' -H "Mcp-Method: $1" -d "$3"; fi; }
  mcode(){ if [ -n "${2:-}" ]; then curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2026-07-28' -H "Mcp-Method: $1" -H "Mcp-Name: $2" -d "$3"; else curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2026-07-28' -H "Mcp-Method: $1" -d "$3"; fi; }
  hdrs=/tmp/horosa_smoke_h.$$
  disc=$(curl -s -D "$hdrs" -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' -d "{\"jsonrpc\":\"2.0\",\"id\":101,\"method\":\"server/discover\",\"params\":{$M}}")
  grep -q '"resultType":"complete"' <<< "$disc" || fail "server/discover 无 resultType: $disc"
  grep -q '"supportedVersions":\["2026-07-28"\]' <<< "$disc" || fail "server/discover 无 supportedVersions: $disc"
  grep -q 'io.modelcontextprotocol/serverInfo' <<< "$disc" || fail "server/discover 无 serverInfo: $disc"
  grep -qi 'mcp-session-id' "$hdrs" && fail "现代纪元不该发会话头"
  rm -f "$hdrs"
  ok "modern server/discover(resultType/supportedVersions/serverInfo,无会话头)"
  ml=$(mrpc tools/list "" "{\"jsonrpc\":\"2.0\",\"id\":102,\"method\":\"tools/list\",\"params\":{$M}}")
  grep -q '"create_chart_record"' <<< "$ml" || fail "modern tools/list 缺 create_chart_record: $ml"
  grep -q '"ttlMs"' <<< "$ml" || fail "modern tools/list 缺 ttlMs: $ml"
  grep -q '"cacheScope"' <<< "$ml" || fail "modern tools/list 缺 cacheScope: $ml"
  grep -q 'delete' <<< "$ml" && fail "modern tools/list 出现删除类工具名"
  grep -q '"ext_' <<< "$ml" && fail "modern tools/list 出现 ext_ 前缀(再导出回环)"
  ok "modern tools/list(ttlMs/cacheScope;只增、零 ext_)"
  mc=$(mrpc tools/call get_current_context "{\"jsonrpc\":\"2.0\",\"id\":103,\"method\":\"tools/call\",\"params\":{\"name\":\"get_current_context\",\"arguments\":{},$M}}")
  grep -q '"content"' <<< "$mc" || fail "modern tools/call 无 content: $mc"
  grep -q '"isError":false' <<< "$mc" || fail "modern tools/call isError 非 false: $mc"
  ok "modern tools/call get_current_context(Mcp-Name)"
  body104="{\"jsonrpc\":\"2.0\",\"id\":104,\"method\":\"tools/call\",\"params\":{\"name\":\"get_current_context\",\"arguments\":{},$M}}"
  code=$(mcode tools/call wrong "$body104"); [ "$code" = "400" ] || fail "Mcp-Name 不一致期望 400 得 $code"
  mm=$(mrpc tools/call wrong "$body104"); grep -q -- '-32020' <<< "$mm" || fail "Mcp-Name 不一致期望 -32020: $mm"
  ok "modern Mcp-Name 不一致 → 400 -32020"
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H 'MCP-Protocol-Version: 2026-07-28' -d "{\"jsonrpc\":\"2.0\",\"id\":105,\"method\":\"tools/list\",\"params\":{$M}}"); [ "$code" = "400" ] || fail "缺 Mcp-Method 期望 400 得 $code"
  ok "modern 缺 Mcp-Method → 400"
  MB='"_meta":{"io.modelcontextprotocol/protocolVersion":"2099-01-01","io.modelcontextprotocol/clientCapabilities":{}}'
  mv=$(curl -s -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H 'MCP-Protocol-Version: 2099-01-01' -H 'Mcp-Method: tools/list' -d "{\"jsonrpc\":\"2.0\",\"id\":106,\"method\":\"tools/list\",\"params\":{$MB}}")
  grep -q -- '-32022' <<< "$mv" || fail "不支持版本期望 -32022: $mv"
  grep -q '"supported"' <<< "$mv" || fail "不支持版本应带 supported 清单: $mv"
  ok "modern 不支持版本 → -32022(带 supported)"
  code=$(mcode nope/x "" "{\"jsonrpc\":\"2.0\",\"id\":107,\"method\":\"nope/x\",\"params\":{$M}}"); [ "$code" = "404" ] || fail "未知方法期望 404 得 $code"
  code=$(mcode ping "" "{\"jsonrpc\":\"2.0\",\"id\":108,\"method\":\"ping\",\"params\":{$M}}"); [ "$code" = "404" ] || fail "modern ping 期望 404(该修订已移除 ping)得 $code"
  ok "modern 未知方法 / ping → 404 -32601"
  b64=$(printf '%s' get_current_context | base64 | tr -d '\n')
  mb=$(mrpc tools/call "=?base64?${b64}?=" "{\"jsonrpc\":\"2.0\",\"id\":109,\"method\":\"tools/call\",\"params\":{\"name\":\"get_current_context\",\"arguments\":{},$M}}")
  grep -q '"content"' <<< "$mb" || fail "base64 哨兵编码的 Mcp-Name 未被解码: $mb"
  ok "modern Mcp-Name base64 哨兵"
  if [ -n "$uri" ]; then
    mr=$(mrpc resources/read "$uri" "{\"jsonrpc\":\"2.0\",\"id\":110,\"method\":\"resources/read\",\"params\":{\"uri\":\"$uri\",$M}}")
    grep -q '"contents"' <<< "$mr" || fail "modern resources/read 无 contents: $mr"
    grep -q '"ttlMs":0' <<< "$mr" || fail "modern resources/read 应 ttlMs:0: $mr"
    ok "modern resources/read(Mcp-Name=uri;ttlMs 0)"
  fi
  ml2=$(curl -s -N --max-time 3 -X POST "$URL" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: subscriptions/listen' -d "{\"jsonrpc\":\"2.0\",\"id\":111,\"method\":\"subscriptions/listen\",\"params\":{\"notifications\":{\"toolsListChanged\":true},$M}}" | head -c 600 || true)
  grep -q 'notifications/subscriptions/acknowledged' <<< "$ml2" || fail "subscriptions/listen 未收到确认帧: $ml2"
  grep -q 'io.modelcontextprotocol/subscriptionId' <<< "$ml2" || fail "确认帧缺 subscriptionId: $ml2"
  ok "modern subscriptions/listen(确认帧带 subscriptionId)"
  if [ -n "$STDIO_BIN" ]; then
    sio2=$(printf '%s\n%s\n' "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"server/discover\",\"params\":{$M}}" "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\",\"params\":{$M}}" | "$STDIO_BIN" --horosa-mcp-stdio "$ENDPOINT" 2>/dev/null)
    [ "$(printf '%s\n' "$sio2" | grep -c '"jsonrpc"')" = "2" ] || fail "stdio 代理现代两行应恰回两行: $sio2"
    grep -q '"supportedVersions"' <<< "$sio2" || fail "stdio 代理 server/discover 无 supportedVersions: $sio2"
    grep -q '"ttlMs"' <<< "$sio2" || fail "stdio 代理现代 tools/list 无 ttlMs: $sio2"
    grep -q "$TOKEN" <<< "$sio2" && fail "stdio 代理输出里出现令牌"
    ok "stdio 代理现代纪元(server/discover + tools/list;令牌不外泄)"
  fi
fi
if [ "$WRITE_LOG" = "1" ]; then
  # 发版留档:全绿才写;单行、可 grep(preflight 在 HOROSA_RELEASE_GATE=1 时查它)
  LOGF="$(cd "$(dirname "$0")/.." && pwd)/SELFCHECK_LOG.md"
  printf '%s\n' "- $(date '+%Y-%m-%d %H:%M') mcp-smoke 全绿(端点 ${ENDPOINT}$([ "$EXPECT_DOWN" = "1" ] && echo " · expect-down" || echo ""))" >> "$LOGF" 2>/dev/null \
    && echo "已写入 SELFCHECK_LOG:$LOGF" || echo "⚠️ SELFCHECK_LOG 写入失败(不影响冒烟结论)"
fi
echo "全部通过"
