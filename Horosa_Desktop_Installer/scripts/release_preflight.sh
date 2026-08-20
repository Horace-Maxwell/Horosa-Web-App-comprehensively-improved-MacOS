#!/usr/bin/env bash
# Release pre-flight self-check —— 在发布前运行,把历次流程复盘发现的漏洞编码成可执行检查。
# 任何一项失败即 exit 1。新发现的检查项请持续追加到这里(见 skill「Pre-flight self-check」)。
#
#   用法:  Horosa_Desktop_Installer/scripts/release_preflight.sh
#   跳过某项:对应 env(见各检查),仅在你确认无误时用。
#
# 设计原则:能强制的就强制(脚本),不要只写在文档里靠自觉。
set -uo pipefail   # 故意不开 -e:要跑完所有检查再汇总

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "${INSTALLER_ROOT}/.." && pwd)"
fail=0
ok()   { printf '  \033[32m✅\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m❌\033[0m %s\n' "$1" >&2; fail=1; }
warn() { printf '  \033[33m⚠️\033[0m  %s\n' "$1"; }

# keg-only node@22 不在默认 PATH 的终端会让 node -e 检查假阳性失败、误拦 pre-push;缺 node 则自动补常见位置的 node。
if ! command -v node >/dev/null 2>&1; then
	for _nd in /opt/homebrew/opt/node@22/bin /opt/homebrew/opt/node@20/bin /opt/homebrew/opt/node@18/bin /opt/homebrew/bin /usr/local/opt/node@22/bin /usr/local/opt/node@18/bin /usr/local/bin; do
		[ -x "${_nd}/node" ] && { PATH="${_nd}:${PATH}"; export PATH; break; }
	done
fi

VERSION="$(python3 -c "import json,os;print(json.load(open(os.path.join('${INSTALLER_ROOT}','package.json')))['version'])" 2>/dev/null || echo "")"
RUNTIME_VERSION="$(python3 -c "import json,os;print(json.load(open(os.path.join('${INSTALLER_ROOT}','config','release_config.json'))).get('runtimeVersion',''))" 2>/dev/null || echo "")"
[ -n "${VERSION}" ] || { echo "无法读取 package.json version,终止" >&2; exit 2; }
echo "== Release pre-flight: version ${VERSION} / runtime ${RUNTIME_VERSION} =="

# 1. 版本号 lockstep:所有该带版本号的文件都必须含当前 VERSION
echo "[1] 版本号一致性"
grep -q "\"version\": \"${VERSION}\"" "${INSTALLER_ROOT}/package.json"            && ok "package.json"        || bad "package.json version != ${VERSION}"
grep -q "^version = \"${VERSION}\"" "${INSTALLER_ROOT}/src-tauri/Cargo.toml"       && ok "Cargo.toml"          || bad "Cargo.toml version != ${VERSION}"
grep -q "\"version\": \"${VERSION}\"" "${INSTALLER_ROOT}/src-tauri/tauri.conf.json" && ok "tauri.conf.json"     || bad "tauri.conf.json version != ${VERSION}"
# CITATION.cff 须对版本（缺席即跳过，不误报）。
if [ -f "${REPO_ROOT}/CITATION.cff" ]; then
  grep -q "version: \"${VERSION}\"" "${REPO_ROOT}/CITATION.cff"                     && ok "CITATION.cff"        || bad "CITATION.cff version != ${VERSION}"
else
  ok "CITATION.cff(本仓无此文件，跳过)"
fi
grep -q "APP_VERSION = '${VERSION}'" "${INSTALLER_ROOT}/web/app.js"                 && ok "web/app.js"          || bad "web/app.js APP_VERSION != ${VERSION}"
# Cargo.lock: 本项目包的版本
if awk '/^name = "horosa-desktop-installer"$/{getline; print}' "${INSTALLER_ROOT}/src-tauri/Cargo.lock" | grep -q "version = \"${VERSION}\""; then ok "Cargo.lock"; else bad "Cargo.lock horosa-desktop-installer version != ${VERSION}"; fi
# runtimeVersion 必须是 {VERSION}-runtimeN
case "${RUNTIME_VERSION}" in "${VERSION}-runtime"*) ok "release_config runtimeVersion (${RUNTIME_VERSION})";; *) bad "runtimeVersion '${RUNTIME_VERSION}' 不是 ${VERSION}-runtimeN";; esac
# 运行时版本闸字面量单源已迁 basecomm RuntimeWire(各控制器只引用不手抄);须与 runtimeVersion lockstep(改后须 mvn install basecomm 起整链+重建 boot)
S1_RW="${REPO_ROOT}/Horosa-Web/astrostudysrv/basecomm/src/main/java/spacex/basecomm/constants/RuntimeWire.java"
grep -q "RUNTIME_VERSION = \"${RUNTIME_VERSION}\"" "${S1_RW}" 2>/dev/null && ok "RuntimeWire.RUNTIME_VERSION=${RUNTIME_VERSION}" || bad "RuntimeWire.RUNTIME_VERSION != ${RUNTIME_VERSION}(改后须 mvn install basecomm 起整链+重建 boot)"
# verify_launcher_console_states.py 硬编码 launcher 的 "来源 pkg <VERSION>" 断言(launcher 用 APP_VERSION 渲染该行)——
# 每版必须同步,否则 verify_desktop_packaging 在「编译+签名+公证」之后才报 ready-state 失败(v2.1.8 复盘:白白跑完一次签名公证)。
grep -q "来源 pkg ${VERSION}" "${INSTALLER_ROOT}/scripts/verify_launcher_console_states.py" && ok "verify_launcher_console_states.py(launcher 版本断言)" || bad "verify_launcher_console_states.py 仍断言旧版本 —— 改 '来源 pkg ${VERSION}' 及注入 detail 的 '本机组件版本 ${VERSION}'"
# 同文件另有一处 offline_ready 夹具串「本机组件版本 <VERSION>」—— 历版皆随版本改,却一直靠人记得。
# 2026-08-12 v3.9.1 lockstep 时发现它是唯一没被守住的一处,补进本闸。
grep -q "本机组件版本 ${VERSION} 已可直接使用" "${INSTALLER_ROOT}/scripts/verify_launcher_console_states.py" && ok "verify_launcher_console_states.py(offline_ready 夹具版本)" || bad "verify_launcher_console_states.py 的 offline_ready 夹具版本 != ${VERSION}"

# 2. 本版 release notes 文件必须存在且非空(否则发布页只剩通用模板 —— v2.1.4 复盘 #1)
echo "[2] 本版发布说明"
[ -s "${INSTALLER_ROOT}/config/release_notes/${VERSION}.md" ] && ok "config/release_notes/${VERSION}.md 存在" || bad "缺 config/release_notes/${VERSION}.md —— 发布页会只显示通用说明"

# 3. UPGRADE_LOG 有本版条目
echo "[3] UPGRADE_LOG 条目"
grep -q "${VERSION}" "${REPO_ROOT}/UPGRADE_LOG.md" && ok "UPGRADE_LOG 提及 ${VERSION}" || bad "UPGRADE_LOG.md 没有 ${VERSION} 条目"


# 4. settings.local.json 绝不可被 git 跟踪(里面有 token / 机器路径 —— 本次复盘的泄露风险)
echo "[4] 机密文件未入库"
if git -C "${REPO_ROOT}" ls-files --error-unmatch .claude/settings.local.json >/dev/null 2>&1; then bad ".claude/settings.local.json 被 git 跟踪了(含 token,有泄露风险!)"; else ok ".claude/settings.local.json 未被跟踪"; fi
# .claude 配置 JSON 必须可解析(曾有加 token 时漏逗号弄坏过)
for f in settings.json settings.local.json launch.json; do
  p="${REPO_ROOT}/.claude/${f}"
  [ -f "${p}" ] || continue
  python3 -m json.tool "${p}" >/dev/null 2>&1 && ok ".claude/${f} 可解析" || bad ".claude/${f} JSON 解析失败"
done

# 5. 编译产物新鲜度(后端 jar / 前端 dist-file 不能比源码旧 —— 复盘 #2;打包时也会再拦一次)
echo "[5] 编译产物新鲜度"
JAR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
DIST="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file/index.html"
# 内容感知豁免(制度化 2026-07-14,git-op mtime 假旧类):git checkout/reset/merge 会平移「工作树源文件」
# 的 mtime(gitignored 的 target/jar、dist-file 产物不被触碰),令「find src -newer 产物」在切分支/reset
# 后误判产物假旧、阻断发布。真判据 = 内容可证现行,而非 mtime。仅当内容可证现行时豁免 mtime 裁决;否则(含
# 真·未提交改动/未重建)照旧按 mtime 拦——两门并存的设计不破(见 [122])。
if [ -f "${JAR}" ]; then
  # jar 无 build-info 指纹 ⟹ 现行判据:后端工作树对 HEAD 干净(无未提交改动) ∧ jar 构建时刻 ≥ 最近一次
  # 改后端源(src/main、pom.xml)的提交时刻(git-op 不动 gitignored 的 target/jar,其 mtime 是真实构建时刻)。
  _JAR_MT="$(stat -f %m "${JAR}" 2>/dev/null || echo 0)"
  _JAR_LASTSRC_CT="$(git -C "${REPO_ROOT}" log -1 --format=%ct -- ':(glob)Horosa-Web/astrostudysrv/**/src/main/**' ':(glob)Horosa-Web/astrostudysrv/**/pom.xml' 2>/dev/null || echo 0)"
  if [ "${_JAR_LASTSRC_CT}" != "0" ] && [ "${_JAR_MT}" -ge "${_JAR_LASTSRC_CT}" ] && git -C "${REPO_ROOT}" diff --quiet HEAD -- Horosa-Web/astrostudysrv 2>/dev/null; then
    ok "astrostudyboot.jar 现行(后端工作树干净 ∧ jar 构建≥最近后端提交;git-op mtime 假旧已内容感知豁免)"
  elif [ -n "$(find "${REPO_ROOT}"/Horosa-Web/astrostudysrv/*/src/main -type f -newer "${JAR}" -print -quit 2>/dev/null || true)" ]; then bad "astrostudyboot.jar 比后端源码旧 —— 需 mvn clean package 重建"; else ok "astrostudyboot.jar 比源码新"; fi
else warn "astrostudyboot.jar 不存在(发布会回退到 runtime bundle 旧 jar —— 后端有改动务必先重建)"; fi
if [ -f "${DIST}" ]; then
  # dist-file 由 build-info 指纹背书 ⟹ 现行判据(与 [122] 同):前端工作树对 HEAD 干净 ∧ build-info.dirty==0 ∧
  # build-info.commit 为 HEAD(或 HEAD 祖先且前端源面零 diff)。满足即产物源自 HEAD 前端源,mtime 假旧可豁免。
  _DINFO="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file/build-info.json"
  _DIST_FRESH=0
  if [ -f "${_DINFO}" ] && git -C "${REPO_ROOT}" diff --quiet HEAD -- Horosa-Web/astrostudyui/src 2>/dev/null; then
    _DC="$(python3 -c "import json;print(json.load(open('${_DINFO}')).get('commit',''))" 2>/dev/null || echo "")"
    _DD="$(python3 -c "import json;print(1 if json.load(open('${_DINFO}')).get('dirty') else 0)" 2>/dev/null || echo "1")"
    _DH="$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo "")"
    if [ "${_DD}" = "0" ] && [ -n "${_DC}" ]; then
      if [ "${_DC}" = "${_DH}" ]; then _DIST_FRESH=1
      elif git -C "${REPO_ROOT}" merge-base --is-ancestor "${_DC}" "${_DH}" 2>/dev/null \
           && [ -z "$(git -C "${REPO_ROOT}" diff --name-only "${_DC}" "${_DH}" -- Horosa-Web/astrostudyui/src Horosa-Web/astrostudyui/package.json Horosa-Web/astrostudyui/.umirc.js Horosa-Web/astrostudyui/public 2>/dev/null)" ]; then _DIST_FRESH=1; fi
    fi
  fi
  if [ "${_DIST_FRESH}" = "1" ]; then
    ok "dist-file 现行(build-info 指纹背书源自 HEAD ∧ 前端源干净;git-op mtime 假旧已内容感知豁免)"
  elif [ -n "$(find "${REPO_ROOT}/Horosa-Web/astrostudyui/src" -type f -not -path "*/.umi/*" -not -path "*/node_modules/*" -newer "${DIST}" -print -quit 2>/dev/null || true)" ]; then bad "dist-file 比前端源码旧 —— 需 npm run build && build:file"; else ok "dist-file 比源码新"; fi
else bad "dist-file 不存在 —— 需 npm run build:file"; fi

# 6. CI 必须对当前 HEAD 通过(功能回归靠 CI 兜 —— 复盘 #3)。需要 gh。
echo "[6] CI 状态(当前 HEAD)"
if command -v gh >/dev/null 2>&1; then
  HEAD_SHA="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
  CI_JSON="$(gh run list --repo Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS --branch main --limit 10 --json headSha,status,conclusion,workflowName 2>/dev/null || echo '[]')"
  CONCL="$(printf '%s' "${CI_JSON}" | python3 -c "import sys,json;sha='${HEAD_SHA}';rs=[r for r in json.load(sys.stdin) if r.get('headSha')==sha];print((rs[0].get('conclusion') or rs[0].get('status')) if rs else 'none')" 2>/dev/null || echo 'err')"
  case "${CONCL}" in
    success) ok "CI 对 HEAD(${HEAD_SHA:0:7})成功";;
    none)    warn "CI 还没有 HEAD(${HEAD_SHA:0:7})的运行记录 —— 先 push 并等 CI 跑完";;
    *)       bad "CI 对 HEAD(${HEAD_SHA:0:7})状态=${CONCL}(需 success 才发)";;
  esac
else warn "未装 gh,跳过 CI 检查 —— 请手动确认 CI 绿"; fi

# 7. Issue #8(AI 分析 SSE)修复哨兵:catch 必须先记原始异常,SSE 流必须心跳。
#    Windows 端 v2.2.1 调试复盘:Ollama 慢首 token 时空闲断连,catch 块 sendEvent 撞 ClientAbort
#    把 RuntimeException 抛回 ai-analysis-chat-stream 线程,且原始一级异常被 safeErrorMessage
#    吞掉没记日志。本检查保证两个修复都不会被回退。
echo "[7] Issue #8(AI 分析 SSE)修复哨兵"
AIPROXY="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
if [ -f "${AIPROXY}" ]; then
  grep -q "QueueLog.error(AppLoggers.ErrorLogger" "${AIPROXY}" \
    && ok "AIAnalysisProxyService catch 已记原始异常(Fix 1)" \
    || bad "AIAnalysisProxyService catch 缺 QueueLog.error 记日志 —— Issue #8 一级异常会被吞掉"
  grep -q "keep-alive" "${AIPROXY}" \
    && ok "AIAnalysisProxyService SSE 心跳在位(Fix 2)" \
    || bad "AIAnalysisProxyService 缺 SSE 心跳 keep-alive —— Issue #8 Ollama 慢首 token 会触发 ClientAbort"
else
  warn "AIAnalysisProxyService.java 不存在,跳过 #8 哨兵"
fi

# 8. v2.2.1 收尾哨兵:(a) Anthropic content 块必须带 type(否则对话/测试连接 503);
#    (b) 晚子时时柱 (1,0) 对称分支必须在(否则 Java 系技法 (1,0) 回退到 庚子,与钉定 戊子 不一致)。
echo "[8] v2.2.1 收尾修复哨兵(Anthropic type + 晚子时对称分支)"
if [ -f "${AIPROXY}" ]; then
  grep -q "buildAnthropicTextPart" "${AIPROXY}" \
    && ok "Anthropic content 块带 type(buildAnthropicTextPart)" \
    || bad "AIAnalysisProxyService 缺 buildAnthropicTextPart —— Anthropic content 会漏 type 触发 503(Mac #9)"
fi
BZHELPER="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/helper/BaZiHelper.java"
if [ -f "${BZHELPER}" ]; then
  grep -q "after23NewDay && !lateZiHourUseNextDay" "${BZHELPER}" \
    && ok "晚子时时柱 (1,0) 对称分支在位(BaZiHelper)" \
    || bad "BaZiHelper 缺 (after23 && !lateZi) 对称分支 —— (1,0) 边界会回退 庚子,跨技法不一致"
else
  warn "BaZiHelper.java 不存在,跳过 (1,0) 对称分支哨兵"
fi

# 9. 更新后启动卡顿修复哨兵(本次复盘):防「更新后重启卡在 100% / 反复走 300s 全量慢路径」回归。
#    根因复盘见 docs/更新后启动卡顿修复-v2.3.1.md:① 标记仅成功时消费→失败残留致次次慢;
#    ② pid 仅判存在→残留死 pid 误拦截;③ 首启进度停住无反馈像死机;④ warmup 同步阻塞启动。
echo "[9] 更新后启动卡顿修复哨兵"
MAINRS="${INSTALLER_ROOT}/src-tauri/src/main.rs"
STARTSH="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
if [ -f "${MAINRS}" ]; then
  if grep -q "fn consume_update_complete_marker_into_state" "${MAINRS}" \
     && grep -q "consume_update_complete_marker_into_state(&app)" "${MAINRS}"; then
    ok "C① 更新标记读取即消费(consume_update_complete_marker_into_state)"
  else
    bad "main.rs 缺 consume_update_complete_marker_into_state 或未在 runtime_bootstrap 调用 —— 首启失败会残留标记致次次走 300s 慢路径"
  fi
  # 注:emit_indeterminate_progress 调用会被 cargo fmt 拆成多行(`(` 后换行),故不能 grep `(&window`(会漏报);
  # 用「函数名存在」+「首启提示文案存在」双重确认 —— 两者 cargo fmt 都不会拆。(2.3.1 踩过此误报)
  # (v2.3.2 文案已从「需完整校验 30-60 秒」改为快路径版「正在恢复启动」,哨兵同步跟改。)
  if grep -q "emit_indeterminate_progress" "${MAINRS}" \
     && grep -q "正在恢复启动" "${MAINRS}"; then
    ok "A 首启 indeterminate 等待提示在位"
  else
    bad "main.rs 首启缺 emit_indeterminate_progress 调用或提示文案 —— 更新后首启进度停住会被当成卡死"
  fi
  # D (v2.3.2):更新后首启「预写 fast-path 标记 + 不再强制全量」修复哨兵。
  # 根因:runtime 安装前已 sha256 验签,首启再走 300s 全量属冗余;且 fast-path 标记仅在「整轮成功」
  # 后才写,用户把冷首启当卡死强退 → 标记没写 → 下次又全量 → 反复重启(实测 18:23/18:26/18:28 三启)。
  # 修法:对已验签 runtime 在 start_runtime 之前预写标记,首启即走快路径,强退也不回退全量。
  # 详见 docs/更新后自启修复-v2.3.2.md。哨兵 grep 注释 sentinel(comment,cargo fmt 不拆)。
  if grep -q "需重启两三次" "${MAINRS}"; then
    ok "D 更新后首启预写 fast-path 标记(已验签 runtime 不再 300s 全量)"
  else
    bad "main.rs 缺 v2.3.2 预写 fast-path 标记修复 —— 更新后首启回到冷全量、强退反复(见 docs/更新后自启修复-v2.3.2.md)"
  fi
  # E (2.4.0 重发·真因哨兵):首启分支**删掉 cleanup_state** —— 它会 `web_shutdown.store(true)` 关掉本次刚
  # `start_static_server` 起的静态服务器(web_port)→ `emit_ready` 导航的 `frontend_url` 连不上 → 卡启动页/
  # 进不了主界面/按钮死(真机实测真因,前两次误诊弹框/慢校验都没修好)。grep 修复说明注释(cargo fmt 不拆)。
  # 真因详见 docs/更新后卡启动页-真因cleanup_state误杀静态服务器-v2.4.0.md。**铁律:首启 start_static_server 后绝不调会触发 web_shutdown 的清理。**
  if grep -q "误杀静态服务器" "${MAINRS}"; then
    ok "E 首启分支不调 cleanup_state(真因修复·静态服务器不被误杀)"
  else
    bad "main.rs 缺「误杀静态服务器」修复说明/铁律 —— 首启分支若(再)调 cleanup_state 会关掉静态服务器致更新后卡启动页(见 docs/更新后卡启动页-真因cleanup_state误杀静态服务器-v2.4.0.md)"
  fi
  # F:快路径回退从静默一行升级为醒目说明(属正常保护)+账本留痕。
  if grep -q "已自动切换完整校验" "${MAINRS}" && grep -q "rust.fast_path_fallback" "${MAINRS}"; then
    ok "F 快速启动回退醒目说明+账本留痕在位"
  else
    bad "main.rs 缺快速启动回退醒目说明(已自动切换完整校验)或账本留痕(rust.fast_path_fallback)—— 回退退化回静默一行,用户又会把回退当卡死"
  fi
else
  warn "main.rs 不存在,跳过更新卡顿哨兵(C①/A/D/E)"
fi
if [ -f "${STARTSH}" ]; then
  grep -q "reclaim_or_block_pid_file" "${STARTSH}" \
    && ok "C② pid 判存活 + 精准回收自家残留(reclaim_or_block_pid_file,取代 prune_stale_pid_file)" \
    || bad "start_horosa_local.sh 缺 reclaim_or_block_pid_file —— 残留死 pid / 卡死自家后端会误拦截启动(修法3)"
  grep -q "runtime warmup begin (background)" "${STARTSH}" \
    && ok "B warmup 后台非阻塞" \
    || bad "start_horosa_local.sh warmup 未后台化 —— 更新后首启会多等预热阻塞"
else
  warn "start_horosa_local.sh 不存在,跳过更新卡顿哨兵(C②/B)"
fi

# 10. Issue #10「服务不稳定」修复哨兵(SSE 并发竞态 + SSE 标志跨请求污染)。
#     根因复盘见 docs/服务不稳定-SSE并发与签名污染修复-v2.3.1.md:① 心跳/读流并发写非线程安全 SseEmitter→AI 断流;
#     ② __sse__ 标志(绑 request 对象)被 Tomcat 复用残留→污染排盘/predict→间歇 signature.error。
echo "[10] Issue #10(SSE 并发 + SSE 标志污染)修复哨兵"
if [ -f "${AIPROXY}" ]; then
  grep -q "class SseChannel" "${AIPROXY}" \
    && ok "A SseChannel 线程安全收口 emitter" \
    || bad "AIAnalysisProxyService 缺 SseChannel —— SSE 心跳/读流并发写 race 会让 AI 几句话后断流(#10)"
else
  warn "AIAnalysisProxyService.java 不存在,跳过 #10(A)哨兵"
fi
RHINTERCEPTOR="${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/spring/help/interceptor/RequestHeaderInterceptor.java"
if [ -f "${RHINTERCEPTOR}" ]; then
  if grep -q "getDispatcherType() != DispatcherType.REQUEST" "${RHINTERCEPTOR}" \
     && grep -q "TransData.setSSE(false)" "${RHINTERCEPTOR}"; then
    ok "B preHandle async 早返回 + setSSE(false) 归零(SSE 标志跨请求污染防护)"
  else
    bad "RequestHeaderInterceptor.preHandle 缺 async 早返回 或 setSSE(false) 归零 —— SSE 标志会污染排盘/predict 致间歇 signature.error(#10)"
  fi
else
  warn "RequestHeaderInterceptor.java 不存在,跳过 #10(B)哨兵"
fi

echo "[11] 西占推运 + 宫制修复哨兵(v2.5.0)"
PERCHART="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py"
ASTROCONST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/constants/AstroConst.js"
PERSIAN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroPersianDirected.js"
BALB="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/balbillus.js"
# A. 宫制数量前后端同步(后端 hsys[] vs 前端 HOUSE_SYSTEM_OPTIONS):改一处必改另一处,否则 index 错位读错宫制
if [ -f "${PERCHART}" ] && [ -f "${ASTROCONST}" ]; then
  HSYS_BE="$(python3 -c "import re;t=open('${PERCHART}').read();m=re.search(r'hsys=\[(.*?)\]',t,re.S);print(len([x for x in m.group(1).split(',') if x.strip()]) if m else -1)" 2>/dev/null || echo -2)"
  HSYS_FE="$(python3 -c "import re;t=open('${ASTROCONST}').read();m=re.search(r'HOUSE_SYSTEM_OPTIONS = \[(.*?)\];',t,re.S);print(len(re.findall(r'value:',m.group(1))) if m else -1)" 2>/dev/null || echo -3)"
  if [ "${HSYS_BE}" = "${HSYS_FE}" ] && [ "${HSYS_BE}" -gt 0 ] 2>/dev/null; then
    ok "A 宫制数量前后端同步(${HSYS_BE})"
  else
    bad "A 宫制数量不同步:后端 hsys[]=${HSYS_BE} vs 前端 HOUSE_SYSTEM_OPTIONS=${HSYS_FE} —— index 错位会读错宫制"
  fi
else
  warn "perchart.py / AstroConst.js 不存在,跳过宫制同步哨兵"
fi
# B. 福点整宫制:自定义整宫制宫头必须 house.hsys=const.HOUSES_WHOLE_SIGN,否则 flatlib inHouse 加 -5° 偏移致落宫差一宫
if [ -f "${PERCHART}" ] && grep -q "custHouse_Fortuna_Whole" "${PERCHART}"; then
  if grep -q "house.hsys = const.HOUSES_WHOLE_SIGN" "${PERCHART}" && ! grep -q "house.hsys = custHouse_Fortuna_Whole" "${PERCHART}"; then
    ok "B 福点整宫制宫头走 HOUSES_WHOLE_SIGN(inHouse 无 -5° 偏移)"
  else
    bad "B 福点整宫制宫头未设 const.HOUSES_WHOLE_SIGN(或回退自定义标记) —— inHouse -5° 偏移致落宫 off-by-one"
  fi
fi
# C. 双圈盘内圈本命冻结修复:AstroPersianDirected.requestData 每次从 props.value 重算 natalParams
if [ -f "${PERSIAN}" ]; then
  grep -q "natalParams(this.props.value)" "${PERSIAN}" \
    && ok "C 波斯向运 requestData 重算 natalParams(内圈本命不冻结)" \
    || bad "C AstroPersianDirected 未从 props.value 重算 natalParams —— 换盘后内圈本命会冻结成旧盘"
fi
# D. Balbillus 旺距削减公式 N×(1−d/360) + 七星小年表(独立引擎,勿退回 k 标度实验版)
if [ -f "${BALB}" ]; then
  grep -q "1 - d / 360" "${BALB}" && grep -q "BALBILLUS_YEARS" "${BALB}" \
    && ok "D Balbillus 旺距削减公式在位" \
    || bad "D balbillus.js 缺 N×(1−d/360) 削减公式 或 BALBILLUS_YEARS"
fi

echo "[12] 本地服务端口健壮性哨兵(v2.5.0)"
WEBCHART="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
STARTSH="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
if [ -f "${WEBCHART}" ]; then
  if grep -q "def ensure_chart_port_free" "${WEBCHART}" && grep -q "ensure_chart_port_free('127.0.0.1', chart_port)" "${WEBCHART}"; then
    ok "A webchartsrv.py 绑定前回收僵尸端口(ensure_chart_port_free)"
  else
    bad "A webchartsrv.py 缺 ensure_chart_port_free —— 僵尸占 8899 会让排盘服务起不来(portend code 70)"
  fi
else
  warn "webchartsrv.py 不存在,跳过端口健壮性哨兵"
fi
if [ -f "${STARTSH}" ]; then
  grep -q "reclaim_stale_port" "${STARTSH}" \
    && ok "B start_horosa_local.sh 回收自己的僵尸端口(reclaim_stale_port)" \
    || bad "B start_horosa_local.sh 缺 reclaim_stale_port —— 端口被自己僵尸占住会阻死启动"
fi

echo "[13] 时区/夏令时(DST)自动校正哨兵(v2.5.0)"
UI_SRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
UI_PKG="${REPO_ROOT}/Horosa-Web/astrostudyui/package.json"
TZUTIL="${UI_SRC}/utils/timezone.js"
DSTIND="${UI_SRC}/components/comp/DstZoneIndicator.js"
if [ -f "${UI_PKG}" ]; then
  grep -q '"tz-lookup"' "${UI_PKG}" \
    && ok "A package.json 含 tz-lookup 依赖(经纬度→IANA 时区,离线)" \
    || bad "A package.json 缺 tz-lookup —— DST 自动校正无法离线求时区"
fi
if [ -f "${TZUTIL}" ]; then
  grep -q "applyDstToFields" "${TZUTIL}" && grep -q "dstAwareZoneAt" "${TZUTIL}" && grep -q "longOffset" "${TZUTIL}" \
    && ok "B timezone.js 在位(applyDstToFields + dstAwareZoneAt + Intl longOffset)" \
    || bad "B timezone.js 缺 applyDstToFields/dstAwareZoneAt/longOffset —— DST 引擎不完整"
else
  bad "B timezone.js 不存在 —— DST 自动校正引擎缺失"
fi
[ -f "${DSTIND}" ] \
  && ok "C DstZoneIndicator.js 共享指示器组件在位" \
  || bad "C DstZoneIndicator.js 不存在 —— 三表单 DST 指示器缺失"
dst_forms_ok=1
for f in "components/comp/ChartFormData.js" "components/user/ChartData.js" "components/user/CaseData.js"; do
  fp="${UI_SRC}/${f}"
  if [ -f "${fp}" ]; then
    grep -q "applyDstToFields" "${fp}" && grep -q "DstZoneIndicator" "${fp}" && grep -q "zoneManual" "${fp}" \
      || { bad "D ${f} 未接 DST(applyDstToFields/DstZoneIndicator/zoneManual) —— 该表单时区不自动校正"; dst_forms_ok=0; }
  else
    bad "D ${f} 不存在"; dst_forms_ok=0
  fi
done
[ "${dst_forms_ok}" -eq 1 ] && ok "D 三表单(ChartFormData/ChartData/CaseData)均接 DST 自动校正"

# 14-19. 启动机制稳健化哨兵(端口被占/后端未启动 根治,详见 docs/启动机制稳健化-端口与就绪.md)。
UISRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
WARMJS="${REPO_ROOT}/Horosa-Web/astrostudyui/scripts/warmHorosaRuntime.js"

echo "[14] 端口冲突重试哨兵(修法1:backend/chart 换口重试;web 不入环)"
if [ -f "${MAINRS}" ]; then
  if grep -q "fn start_runtime_with_port_retry" "${MAINRS}" \
     && grep -q "start_runtime_with_port_retry(" "${MAINRS}" \
     && grep -q "fn error_is_port_conflict" "${MAINRS}"; then
    ok "修法1 端口冲突重试封装在位(start_runtime_with_port_retry + error_is_port_conflict)"
  else
    bad "main.rs 缺端口冲突重试封装 —— 端口被瞬时抢走会一次失败即报死(修法1)"
  fi
  # 铁律(防 v2.4.0 [9]E 重演):重试环只重选 backend/chart,绝不读写 web_shutdown / 不重起静态服务器。
  grep -q "绝不在此被读写" "${MAINRS}" \
    && ok "修法1 铁律注释在位(web 端口/web_shutdown 不入重试环)" \
    || bad "main.rs 缺「web_shutdown 绝不在此被读写」铁律注释 —— 重试环若动 web_shutdown 会重演 [9]E 静态服务器误杀"
else
  warn "main.rs 不存在,跳过修法1 哨兵"
fi

echo "[15] 脚本端口冲突退出码哨兵(修法2:exit 3 + bind 错精确匹配)"
if [ -f "${STARTSH}" ]; then
  if grep -q "bind_err_re=" "${STARTSH}" \
     && grep -q "Address already in use" "${STARTSH}" \
     && grep -q "BindException" "${STARTSH}" \
     && grep -q "exit 3" "${STARTSH}"; then
    ok "修法2 端口冲突 exit 3 + bind 错精确匹配(Address already in use / BindException)"
  else
    bad "start_horosa_local.sh 缺 exit 3 / bind_err_re 精确 token —— 端口竞态无法被 Rust 识别重试(修法2)"
  fi
  # 防回归(红队 C2):bind 错正则绝不能含裸小写 'port' 分支(否则 Spring banner/--server.port= 会被误判)。
  if grep "bind_err_re=" "${STARTSH}" | grep -qF "|port"; then
    bad "bind_err_re 含裸 'port' 分支 —— 会把正常输出误判为端口冲突(红队 C2),请改回精确 token"
  else
    ok "修法2 bind_err_re 不含裸 port(精确匹配,无误判)"
  fi
else
  warn "start_horosa_local.sh 不存在,跳过修法2 哨兵"
fi

echo "[16] 卡死自家后端精准回收哨兵(修法3:仅杀签名核实的自家 PID)"
if [ -f "${STARTSH}" ]; then
  if grep -q "reclaim_or_block_pid_file" "${STARTSH}" \
     && grep -q "refuse to kill" "${STARTSH}" \
     && grep -q "horosa.runtime.owner" "${STARTSH}"; then
    ok "修法3 仅在 cmdline 签名核实为自家后端时 kill 续启,否则维持 exit 1(不误杀)"
  else
    bad "start_horosa_local.sh 缺修法3 精准回收(reclaim_or_block_pid_file + 签名核实 + refuse to kill)—— 可能误杀或拦死启动"
  fi
fi

echo "[17] 就绪前最小热身 + curl 兜底哨兵(修法4)"
if [ -f "${STARTSH}" ]; then
  if grep -q "warm_runtime_routes_min_sync" "${STARTSH}" \
     && grep -q "HOROSA_WARM_MINIMAL" "${STARTSH}"; then
    ok "修法4 就绪前最小同步热身在位(非致命有界,预热排盘冷 bean)"
  else
    bad "start_horosa_local.sh 缺 warm_runtime_routes_min_sync/HOROSA_WARM_MINIMAL —— 首次排盘会打到冷 bean 弹「未就绪」(修法4)"
  fi
  grep -q "urllib.request" "${STARTSH}" \
    && ok "修法4 curl 缺失时用内置 python urllib 探测(不静默放行)" \
    || bad "start_horosa_local.sh 缺 curl 缺失的 python urllib 兜底 —— 无 curl 时就绪判定会静默空转(红队 M5)"
fi
if [ -f "${WARMJS}" ]; then
  grep -q "HOROSA_WARM_MINIMAL" "${WARMJS}" \
    && ok "修法4 warmHorosaRuntime.js 支持最小热身模式(仅 /chart)" \
    || bad "warmHorosaRuntime.js 缺 HOROSA_WARM_MINIMAL 最小模式 —— 同步热身会跑全量拖慢启动(修法4)"
fi

echo "[18] 前端排盘透明重试哨兵(修法5:幂等 raw-fetch 重试,SSE/AI 排除)"
CHARTFETCH="${UISRC}/utils/chartFetch.js"
REQJS="${UISRC}/utils/request.js"
if [ -f "${CHARTFETCH}" ] && [ -f "${REQJS}" ]; then
  # [R3-A3 起] 合法接入=cachedKentangFetch(缓存壳,内部走 fetchChartWithRetry,重试语义
  # 由调用方 cfg 控制:原四引擎保默认重试,原裸 fetch 站点传 {retries:0} 保旧单发)。
  if grep -q "export async function fetchChartWithRetry" "${CHARTFETCH}" \
     && grep -q "fetchChartWithRetry(url, fetchOpts, cfg)" "${UISRC}/utils/kentangCache.js" \
     && grep -q "cachedKentangFetch" "${UISRC}/components/dunjia/DunJiaCalc.js" \
     && grep -q "cachedKentangFetch" "${UISRC}/components/taiyi/TaiYiCalc.js" \
     && grep -q "cachedKentangFetch" "${UISRC}/components/jinkou/JinKouCalc.js" \
     && grep -q "cachedKentangFetch" "${UISRC}/services/qizheng.js"; then
    ok "修法5 缓存壳(内含 fetchChartWithRetry)接入四引擎 raw-fetch 主路径"
  else
    bad "排盘 raw-fetch 站点未全部接入缓存壳/壳内失去重试 —— 冷启动首个排盘无重试会弹「未就绪」(修法5)"
  fi
  # SSE 必须排除重试:requestStream 函数体内不得出现重试封装(防双发/重复计费)。
  if grep -q "export async function requestStream" "${REQJS}" \
     && ! awk '/export async function requestStream/,/^}/' "${REQJS}" | grep -q "fetchWithRetryConnRefused"; then
    ok "修法5 SSE(requestStream)未接入重试(防双发/重复计费)"
  else
    bad "requestStream 疑似接入重试封装 —— SSE/AI 流绝不可重试(会双发/重复计费,红队)"
  fi
else
  warn "chartFetch.js/request.js 不存在,跳过修法5 哨兵"
fi

echo "[19] 离线判定精准性哨兵(修法6:只认 TypeError,排除超时/签名/业务错误)"
SVCSTATUS="${UISRC}/utils/serviceStatus.js"
if [ -f "${SVCSTATUS}" ]; then
  if grep -q "isBackendUnreachableError" "${SVCSTATUS}" \
     && grep -q "instanceof TypeError" "${SVCSTATUS}" \
     && grep -q "err.headers" "${SVCSTATUS}" \
     && grep -q "TimeoutError" "${SVCSTATUS}"; then
    ok "修法6 离线判定只认网络级 TypeError,排除超时/带响应头业务错误(含 signature.error)"
  else
    bad "serviceStatus.isBackendUnreachableError 判定不严 —— 可能把超时/signature.error 误判离线乱弹横幅(红队 H2)"
  fi
else
  warn "serviceStatus.js 不存在,跳过修法6 哨兵"
fi
# 20. 紫微 运限(ZiWeiLuck)/格局(ZiWeiPattern) 深度增强完整性(v2.5.8)
echo "[20] 紫微 运限/格局深度增强"
ZW_HELPER_DIR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/helper"
ZW_MODEL_DIR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model"
ZW_FAT_JAR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
ZW_MAIN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/ZiWeiMain.js"
zw_src_ok=1
for f in "${ZW_MODEL_DIR}/ZiWeiLuck.java" "${ZW_MODEL_DIR}/ZiWeiPattern.java" "${ZW_HELPER_DIR}/ziweige.json" "${ZW_HELPER_DIR}/ziweiliuchangqu.json"; do
  [ -f "$f" ] || { bad "[20] 缺文件 $(basename "$f")"; zw_src_ok=0; }
done
[ "$zw_src_ok" -eq 1 ] && ok "[20] ZiWeiLuck/ZiWeiPattern + ziweige/ziweiliuchangqu 源齐全"
if grep -q "startidx - idx" "${ZW_HELPER_DIR}/ZiWeiHelper.java" 2>/dev/null; then ok "[20] getSmallDirectioinHouse 女命分支已修正(startidx - idx)"; else bad "[20] getSmallDirectioinHouse 女命分支疑似未修正(应为 startidx - idx)"; fi
if grep -q "ZWLuckPanel" "${ZW_MAIN}" 2>/dev/null && grep -q "ZWPatternPanel" "${ZW_MAIN}" 2>/dev/null; then ok "[20] ZiWeiMain 已挂 ZWLuckPanel/ZWPatternPanel"; else bad "[20] ZiWeiMain 未挂 运限/格局 TabPane"; fi
if [ -f "${ZW_FAT_JAR}" ] && command -v unzip >/dev/null 2>&1; then
  zw_cn="$(unzip -Z1 "${ZW_FAT_JAR}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${zw_cn}" ]; then
    zw_list="$(cd "$(mktemp -d)" && unzip -oq "${ZW_FAT_JAR}" "${zw_cn}" 2>/dev/null && unzip -Z1 "${zw_cn}" 2>/dev/null)"
    if echo "${zw_list}" | grep -q "ZiWeiLuck.class" && echo "${zw_list}" | grep -q "ZiWeiPattern.class" && echo "${zw_list}" | grep -q "ziweige.json" && echo "${zw_list}" | grep -q "ziweiliuchangqu.json"; then
      ok "[20] fat jar 已含 ZiWeiLuck/ZiWeiPattern + ziweige/ziweiliuchangqu(gotcha #10)"
    else
      bad "[20] fat jar 缺紫微运限/格局类或数据 —— 需 astrostudycn install + astrostudyboot clean package"
    fi
  else
    warn "[20] fat jar 内未找到 astrostudycn dep jar,跳过内容校验"
  fi
else
  warn "[20] 未找到 fat jar 或无 unzip,跳过 jar 内容校验"
fi

# 20b. 紫微 全面增强 P0–P2(杂曜显示/流派四化表/格局详情/天伤天使) 完整性
echo "[20b] 紫微 全面增强 P0–P2"
ZW_HOUSE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/ZWHouse.js"
ZW_CONST_JS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/constants/ZWConst.js"
ZW_CHART_JAVA="${ZW_MODEL_DIR}/ZiWeiChart.java"
ZW_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/__tests__/ziweiEnhance.test.js"
zw2_ok=1
grep -q "drawSihuaSmallStars" "${ZW_HOUSE}" 2>/dev/null || { bad "[20b] ZWHouse 缺 drawSihuaSmallStars(十二神角格)"; zw2_ok=0; }
grep -q "starsOthersGood" "${ZW_HOUSE}" 2>/dev/null || { bad "[20b] ZWHouse 主四化盘未补显杂曜(starsOthersGood)"; zw2_ok=0; }
{ grep -q "SiHuaTables" "${ZW_CONST_JS}" && grep -q "getActiveSiHuaGan" "${ZW_CONST_JS}"; } 2>/dev/null || { bad "[20b] ZWConst 缺多流派四化表(SiHuaTables/getActiveSiHuaGan)"; zw2_ok=0; }
grep -q "setupStarsTianShangShi" "${ZW_CHART_JAVA}" 2>/dev/null || { bad "[20b] ZiWeiChart 缺天伤天使安星"; zw2_ok=0; }
{ grep -q "inOpp" "${ZW_PATTERN_JAVA:-${ZW_MODEL_DIR}/ZiWeiPattern.java}" && grep -q "sandwichHua" "${ZW_MODEL_DIR}/ZiWeiPattern.java"; } 2>/dev/null || { bad "[20b] ZiWeiPattern 缺新 op inOpp/sandwichHua"; zw2_ok=0; }
[ -f "${ZW_TEST}" ] || { bad "[20b] 缺自检 ziweiEnhance.test.js"; zw2_ok=0; }
[ "$zw2_ok" -eq 1 ] && ok "[20b] 杂曜显示/流派四化表/天伤天使/新op/自检 源齐全"
if grep -q "school: 'beipai'" "${ZW_CONST_JS}" 2>/dev/null; then ok "[20b] 四化流派默认 beipai(=现状零回归)"; else bad "[20b] 四化流派默认非 beipai —— 恐改动存量盘四化(回归风险)"; fi
if [ -f "${ZW_FAT_JAR}" ] && command -v unzip >/dev/null 2>&1; then
  zw2_cn="$(unzip -Z1 "${ZW_FAT_JAR}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${zw2_cn}" ]; then
    zw2_dir="$(mktemp -d)"; ( cd "${zw2_dir}" && unzip -oq "${ZW_FAT_JAR}" "${zw2_cn}" 2>/dev/null )
    if unzip -p "${zw2_dir}/${zw2_cn}" spacex/astrostudycn/model/ZiWeiPattern.class 2>/dev/null | strings | grep -q "inOpp"; then ok "[20b] fat jar ZiWeiPattern 含新 op(inOpp)"; else bad "[20b] fat jar 未含新 op —— 需 astrostudycn install + astrostudyboot clean package"; fi
    if unzip -p "${zw2_dir}/${zw2_cn}" spacex/astrostudycn/model/ZiWeiChart.class 2>/dev/null | grep -aq "setupStarsTianShangShi"; then ok "[20b] fat jar ZiWeiChart 含天伤天使"; else bad "[20b] fat jar 未含天伤天使 —— 需重编"; fi
  fi
fi

# 21. 六壬 起课法/换将/分昼夜(纯前端 castOverride 机制,不动 Java)
echo "[21] 六壬 起课法/换将/分昼夜哨兵"
LR_MAIN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js"
LR_COMM="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js"
LR_AICTX="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js"
LR_CONST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRConst.js"
if grep -q "buildLiuRengCastOverride" "${LR_MAIN}" 2>/dev/null && grep -q "function computeQiXY" "${LR_MAIN}" 2>/dev/null; then ok "[21] LiuRengMain 含起课法引擎(buildLiuRengCastOverride/computeQiXY)"; else bad "[21] LiuRengMain 缺起课法引擎"; fi
if grep -q "castOverride" "${LR_COMM}" 2>/dev/null; then ok "[21] LRCommChart 渲染侧读 castOverride(中心盘随起课法,与右栏断辞同源)"; else bad "[21] LRCommChart 未读 castOverride —— 中心盘不随起课法变,会与右栏断辞不一致"; fi
if grep -q "isDiurnalOverride" "${LR_CONST}" 2>/dev/null; then ok "[21] LRConst.getGuiZi 接受昼夜覆盖(分昼夜法)"; else bad "[21] LRConst.getGuiZi 缺昼夜覆盖参 —— 分昼夜法失效"; fi
if grep -q "castMethod: this.state.castMethod" "${LR_MAIN}" 2>/dev/null && grep -q "fenZhouYe: this.state.fenZhouYe" "${LR_MAIN}" 2>/dev/null; then ok "[21] 占案 payload 含起课法/换将/分昼夜(储存可复现)"; else bad "[21] 占案 payload 缺起课法字段 —— 存档不可复现"; fi
if grep -q "yueJiangMethod: payload.yueJiangMethod" "${LR_AICTX}" 2>/dev/null; then ok "[21] AI挂载 事盘重建透传 castOpts(挂载与显示一致)"; else bad "[21] AI挂载 六壬事盘未透传 castOpts —— 八客/选时案例会挂成默认正时正将"; fi
if grep -q "'xuanshi'" "${LR_MAIN}" 2>/dev/null && grep -q "'yanshu'" "${LR_MAIN}" 2>/dev/null && grep -q "'alnr'" "${LR_MAIN}" 2>/dev/null; then ok "[21] 起课法含 选时/演数/四柱对齐"; else bad "[21] 起课法缺 选时/演数/对齐 选项"; fi
# 次客=筹支加时(重排天地盘),勿退回只改三传;月将高亮认真实月将 actualYue;ChuangChart 必无 applyCiChou。
LR_CHUANG="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.js"
if grep -q "function liurengChouBranch" "${LR_MAIN}" 2>/dev/null && grep -q "case 'cike3':" "${LR_MAIN}" 2>/dev/null; then ok "[21] 次客=筹支加时(liurengChouBranch + computeQiXY cike 分支,重排天地盘)"; else bad "[21] 次客缺筹支加时引擎 —— 退回了「只改三传」的错误实现"; fi
if grep -q "actualYue" "${LR_MAIN}" 2>/dev/null; then ok "[21] 月将/盘式高亮认真实月将 actualYue(非起课法天盘起支 X)"; else bad "[21] 缺 actualYue —— 加时/次客法的月将高亮会错显为起课法 X"; fi
if grep -q "applyCiChou" "${LR_CHUANG}" 2>/dev/null; then bad "[21] ChuangChart 残留 applyCiChou —— 次客退回「只改三传」错误实现,必删"; else ok "[21] ChuangChart 无 applyCiChou(次客在新天盘正常发用三传)"; fi
# 天地盘月将/时辰可视高亮:必须认 actualYue/realTimeBranch,不能用起课法的 X(this.yue)/Y(this.timezi) 对齐支。
LR_COMM2="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js"
LR_CIRCLE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRCircleChart.js"
LR_SQUARE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRTextSquareChart.js"
if grep -q "this.actualYue" "${LR_COMM2}" 2>/dev/null && grep -q "this.realTimeBranch" "${LR_COMM2}" 2>/dev/null; then ok "[21] LRCommChart 暴露 actualYue/realTimeBranch(高亮真源)"; else bad "[21] LRCommChart 缺 actualYue/realTimeBranch —— 月将/时辰高亮会落到起课法对齐支"; fi
if grep -q "highLightData: \[this.actualYue\]" "${LR_CIRCLE}" 2>/dev/null && grep -q "highLightData: \[this.realTimeBranch\]" "${LR_CIRCLE}" 2>/dev/null; then ok "[21] 圆盘高亮=真实月将(天盘)+真实时支(地盘)"; else bad "[21] 圆盘高亮仍用 this.yue(X) —— 会高亮起课法对齐的两格而非月将/时辰"; fi
{ grep -q "upBranch === this.actualYue" "${LR_SQUARE}" 2>/dev/null && grep -q "downBranch === this.realTimeBranch" "${LR_SQUARE}" 2>/dev/null; } || { bad "[21] 方盘 drawHouse 高亮仍用 this.yue/this.timezi —— 应改 actualYue/realTimeBranch"; }
# 中间盘小屏可下滑:RengChart.draw 设模式最小高度 + inline !important 撑高 svg + 读 host 视口高度。
LR_RENG="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/lrzhan/RengChart.js"
if grep -q "minChartH" "${LR_RENG}" 2>/dev/null && grep -q "setProperty('height'" "${LR_RENG}" 2>/dev/null; then ok "[21] 中间盘按模式最小高度绘制 + 撑高 svg(小屏 overflow-y 可下滑)"; else bad "[21] RengChart 缺 minChartH/撑高 svg —— 小屏方盘会裁切且无法下滑"; fi

# 24. AI 分析页 v2.5.1 复审整改不变量（起课兜底 / 卜卦择日挂载 / 六爻护栏 / 数算流年 / 导出注册 + 自检 / 城市库）
echo "[24] AI 分析页 v2.5.1 复审整改哨兵"
AIEXPORT_JS="${UISRC}/utils/aiExport.js"
PRECISE_JS="${UISRC}/utils/preciseCalcBridge.js"
HELUO_JS="${UISRC}/utils/heluoLocal.js"
AIEXPORT_TEST_JS="${UISRC}/utils/__tests__/aiExport.test.js"
# B1：fetchPreciseNongli 本地兜底须对软失败(!result)生效(出现≥2次=try+catch),不能只在 catch → 否则奇门/太乙离线缺失
precise_fb_cnt=$(awk '/export async function fetchPreciseNongli/,/^}/' "${PRECISE_JS}" 2>/dev/null | grep -c "buildLocalNongliFallback")
if [ "${precise_fb_cnt:-0}" -ge 2 ]; then ok "[24] fetchPreciseNongli 软失败也走本地兜底(B1:奇门/太乙离线不缺失)"; else bad "[24] fetchPreciseNongli 兜底疑似仍只在 catch(B1 回退风险)"; fi
# New3：卜卦盘/择日盘进白名单
if awk '/TIME_CASTABLE_DIVINATION =/' "${LR_AICTX}" 2>/dev/null | grep -q "horary" && awk '/TIME_CASTABLE_DIVINATION =/' "${LR_AICTX}" 2>/dev/null | grep -q "election"; then ok "[24] 卜卦盘/择日盘已入 TIME_CASTABLE_DIVINATION"; else bad "[24] TIME_CASTABLE_DIVINATION 缺 horary/election"; fi
# 🔒 铁律：六爻永不入时间确定白名单(否则按时间伪造卦象)
if awk '/TIME_CASTABLE_DIVINATION =/' "${LR_AICTX}" 2>/dev/null | grep -q "sixyao"; then bad "[24] 🔒 铁律破:六爻进了 TIME_CASTABLE_DIVINATION"; else ok "[24] 🔒 六爻未入时间确定白名单(护栏在)"; fi
# F：河洛快照出流年卦(调 liuNian)
if awk '/export function buildSnapshotText/,/return lines.join/' "${HELUO_JS}" 2>/dev/null | grep -q "liuNian("; then ok "[24] 河洛 buildSnapshotText 已出流年卦(调 liuNian)"; else bad "[24] 河洛快照未调 liuNian —— 仍缺整层流年卦"; fi
# F：canping/heluo 进导出注册(否则导出设置隐身+免自检)
if grep -q "key: 'canping'" "${AIEXPORT_JS}" 2>/dev/null && grep -q "key: 'heluo'" "${AIEXPORT_JS}" 2>/dev/null; then ok "[24] canping/heluo 已进 AI_EXPORT_TECHNIQUES"; else bad "[24] canping/heluo 未进 AI_EXPORT_TECHNIQUES(导出设置隐身)"; fi
# F：preset⊆AI_EXPORT_TECHNIQUES 自检断言在(堵隐身回归)
if grep -q "getAIExportPresetKeys" "${AIEXPORT_JS}" 2>/dev/null && grep -q "getAIExportPresetKeys" "${AIEXPORT_TEST_JS}" 2>/dev/null; then ok "[24] preset⊆AI_EXPORT_TECHNIQUES 自检断言在"; else bad "[24] 缺 preset⊆techniques 自检断言(canping/heluo 隐身会复发)"; fi
# atlas：全量城市库存在
if [ -f "${UISRC}/data/citiesFull.json" ]; then ok "[24] atlas 全量城市库 citiesFull.json 存在"; else bad "[24] 缺 citiesFull.json(跑 scripts/build-cities.js 生成)"; fi
# 星运页每个 TabPane key 必须在 VALID_DIRECTION_SUB_TABS,否则点该 tab 会先被 normalize 重定向到主限法(点一次跳主限法、点两次才进)
ASTRODIR_JS="${UISRC}/components/direction/AstroDirectMain.js"
PDSYNC_JS="${UISRC}/utils/primaryDirectionSync.js"
dir_tab_miss=""
for k in $(grep -oE '<TabPane tab="[^"]*" key="[^"]*"' "${ASTRODIR_JS}" 2>/dev/null | grep -oE 'key="[^"]*"' | sed 's/key="//; s/"//'); do
  grep -q "'${k}'" "${PDSYNC_JS}" 2>/dev/null || dir_tab_miss="${dir_tab_miss} ${k}"
done
[ -z "${dir_tab_miss}" ] && ok "[24] 星运页所有 TabPane key 均在 VALID_DIRECTION_SUB_TABS(点 tab 不会先跳主限法)" || bad "[24] 星运 tab 不在白名单、点击会先跳主限法,补入 primaryDirectionSync VALID 表:${dir_tab_miss}"
# AI 四同步(导出/设置/挂载/储存)完备性:migration 必须覆盖占星/星运核心,否则预设新段升级后不入老用户设置(astrochart 的 12分度/主宰链/寿命格局曾受此坑)。
if awk '/AI_EXPORT_SECTION_MIGRATION_KEYS = \[/,/\];/' "${AIEXPORT_JS}" 2>/dev/null | grep -q "'astrochart'" \
  && awk '/AI_EXPORT_SECTION_MIGRATION_KEYS = \[/,/\];/' "${AIEXPORT_JS}" 2>/dev/null | grep -q "'primarydirect'" \
  && awk '/AI_EXPORT_SECTION_MIGRATION_KEYS = \[/,/\];/' "${AIEXPORT_JS}" 2>/dev/null | grep -q "'firdaria'"; then
  ok "[24] AI导出 migration 覆盖占星/星运核心(astrochart/primarydirect/firdaria)"
else
  bad "[24] AI导出 migration 漏占星/星运核心 → 预设新段升级不入老用户设置(补进 AI_EXPORT_SECTION_MIGRATION_KEYS)"
fi
# 四同步跨系统自检断言须在(任何技法漏接 导出/设置/挂载/储存 其一即在 jest 红)
if grep -q "四同步跨系统一致性" "${AIEXPORT_TEST_JS}" 2>/dev/null; then ok "[24] AI 四同步跨系统自检断言在(导出/设置/挂载/储存)"; else bad "[24] 缺 AI 四同步跨系统自检断言"; fi

# 26. 奇门法奇门叠加层(荀爽:化解/用神/取象;纯前端,无 jar)四同步 + 引擎自检
echo "[26] 奇门法奇门叠加层(化解/用神/取象)"
DUNJIA_FACALC="${UISRC}/components/dunjia/DunJiaFaCalc.js"
DUNJIA_FADOC="${UISRC}/components/dunjia/DunJiaFaDoc.js"
DUNJIA_CALC_JS="${UISRC}/components/dunjia/DunJiaCalc.js"
if [ -f "${DUNJIA_FACALC}" ] && [ -f "${DUNJIA_FADOC}" ]; then ok "[26] DunJiaFaCalc/DunJiaFaDoc 在"; else bad "[26] 法奇门叠加层文件缺失"; fi
# 快照 8 段必须在(漏接=AI 导出/挂载/储存看不到化解·用神)
if grep -q "\[六害总览\]" "${DUNJIA_CALC_JS}" 2>/dev/null && grep -q "\[化解方案\]" "${DUNJIA_CALC_JS}" 2>/dev/null && grep -q "\[用神分论\]" "${DUNJIA_CALC_JS}" 2>/dev/null; then ok "[26] buildDunJiaSnapshotText 含法奇门段(六害/化解/用神)"; else bad "[26] 快照漏法奇门段(AI 四同步看不到化解·用神)"; fi
# 导出段表同步(漏=导出设置隐身)
if grep -q "'六害总览', '化解方案'" "${AIEXPORT_JS}" 2>/dev/null; then ok "[26] aiExport.qimen 段表含法奇门段"; else bad "[26] aiExport.qimen 段表漏法奇门段(导出设置隐身)"; fi
# 八神勾雀→虎玄归一(白虎检测两遁通用)必在
if grep -q "replace(/勾/g" "${DUNJIA_CALC_JS}" 2>/dev/null; then ok "[26] 八神勾雀→虎玄归一在(白虎检测两遁通用)"; else bad "[26] 缺勾雀→虎玄归一(阳遁白虎检测会失效)"; fi
# 神煞判语全覆盖自检 + 法奇门引擎单测在
if grep -q "神煞判语全覆盖" "${UISRC}/components/dunjia/__tests__/DunJiaFaDoc.test.js" 2>/dev/null; then ok "[26] 神煞判语全覆盖自检在"; else bad "[26] 缺神煞判语全覆盖自检"; fi
# 相关人员→生年干→八门化气大阵(命盘库选人,捕获各人生年干喂保护清单;未选则不显示该类)
if grep -q "export function birthToYearGan" "${DUNJIA_CALC_JS}" 2>/dev/null && grep -q "CHART_CATEGORY_OPTIONS" "${DUNJIA_CALC_JS}" 2>/dev/null; then ok "[26] DunJiaCalc 含 birthToYearGan(生年干)+CHART_CATEGORY_OPTIONS(命盘/事盘)"; else bad "[26] 缺 birthToYearGan/CHART_CATEGORY_OPTIONS"; fi
if grep -q "faRelatedPeople" "${DUNJIA_FACALC}" 2>/dev/null && ! grep -q "示本盘年干" "${DUNJIA_FACALC}" 2>/dev/null; then ok "[26] computeProtect 生年干来自相关人员(占位『示本盘年干』已移除)"; else bad "[26] computeProtect 仍用本盘年干占位/未读 faRelatedPeople"; fi
if grep -q "onRelatedPeopleChange" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null && grep -q "applyFaRelatedToPan" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 相关人员多选已接线(stamp pan.faRelatedPeople→AI 四同步单源)"; else bad "[26] 相关人员多选未接线/未 stamp pan"; fi
# 命盘/事盘双库:命盘复用命盘库(localCharts)、跨技法自用,奇门设置存 payload.qimen;新增命盘表单须透传 payload(否则丢)
if grep -q "saveAsMingChart" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null && grep -q "qimen: qimenSettings" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 命盘存 payload.qimen(复用命盘库,跨技法可用)"; else bad "[26] 命盘保存未走 payload.qimen"; fi
if grep -q "this.props.fields.payload" "${UISRC}/components/user/ChartAddFormComp.js" 2>/dev/null; then ok "[26] ChartAddFormComp 新增命盘透传 payload(修『新增命盘丢 payload』漏洞)"; else bad "[26] ChartAddFormComp 未透传 payload(奇门命盘设置会丢)"; fi
# 命盘信息完整(命盘管理完整显示):注入性别/经纬度+newCurrentChart honor;命盘保存恒弹新增抽屉(不静默原地更新)
if grep -q "gender: this.state.options" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null && grep -q "values.gender" "${UISRC}/models/user.js" 2>/dev/null; then ok "[26] 奇门命盘信息完整(注入性别/经纬度+newCurrentChart honor)"; else bad "[26] 奇门命盘信息不全(命盘管理缺性别等)"; fi
if ! grep -q "已更新该命盘的奇门设置" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 命盘保存恒弹新增星盘抽屉(无 cid 静默原地更新)"; else bad "[26] 命盘保存仍有 cid 静默原地更新(应恒弹新增抽屉)"; fi
# AI 四同步挂载无遗漏:重算 pan 路径补 faRelatedPeople(regenerate)+computeProtect 全局兜底
if grep -q "qs.faRelatedPeople" "${UISRC}/utils/aiAnalysisContext.js" 2>/dev/null; then ok "[26] AI 挂载 regenerateQimenSnapshot 补 faRelatedPeople(四同步无遗漏)"; else bad "[26] AI 挂载重算 pan 漏 faRelatedPeople(相关人员挂载缺失)"; fi
if grep -q "__horosa_qimen_related_people" "${DUNJIA_FACALC}" 2>/dev/null; then ok "[26] computeProtect 全局兜底相关人员(覆盖未 stamp 的重算路径)"; else bad "[26] computeProtect 缺全局兜底(部分挂载路径漏相关人员)"; fi

# 25. 经纬度/时区 全半球转换 + 真太阳时/直接时间(用户验收追加)
echo "[25] 经纬度/时区转换 + timeAlg 哨兵"
ASTROHELPER_JS="${UISRC}/components/astro/AstroHelper.js"
GEO_TEST_JS="${UISRC}/components/astro/__tests__/AstroHelperGeo.test.js"
# 正向规范转换器:方向按【原始值符号】判(非 deg[0]>=0,否则 |值|<1 小负值如伦敦会判错向)
if grep -q "? 's' : 'n'" "${ASTROHELPER_JS}" 2>/dev/null && grep -q "? 'w' : 'e'" "${ASTROHELPER_JS}" 2>/dev/null; then ok "[25] convertLat/LonToStr 方向按原始值符号(修 (-1,0) 判向)"; else bad "[25] convertLat/LonToStr 方向疑似仍用 deg[0]>=0(小负值判向错)"; fi
# 反向解析:min/60(非 1.0/min)
if grep -q "min / 60" "${ASTROHELPER_JS}" 2>/dev/null; then ok "[25] convertLat/LonStrToDegree 用 min/60(修 1.0/min 致 gpsLat 偏)"; else bad "[25] 反向解析疑似仍 1.0/min(手输经纬度算出 gpsLat 偏、地图/时区偏)"; fi
# 6 手抄坐标转换无「分取负」畸形残留(西经/南纬 param error 源)
GEO_MANUAL_FILES="${UISRC}/components/user/ChartData.js ${UISRC}/components/user/CaseData.js ${UISRC}/components/comp/ChartFormData.js ${UISRC}/components/dice/DiceMain.js ${UISRC}/components/commtools/Azimuth.js ${UISRC}/components/astro/AstroDirectionForm.js"
geo_bad=""
for gf in ${GEO_MANUAL_FILES}; do grep -q "deg\[1\] = -" "$gf" 2>/dev/null && geo_bad="${geo_bad} $(basename "$gf")"; done
[ -z "${geo_bad}" ] && ok "[25] 6 手抄坐标转换无「分取负」畸形残留(西经/南纬不产 121w0-44)" || bad "[25] 仍有「分取负」畸形:${geo_bad}"
# 🔒 buildFieldObject 读 record.timeAlg(真太阳时=0/直接时间=1 不写死),否则八字快照对直接时间盘错用真太阳时校正
if grep -q "timeAlg: { value: (record.timeAlg" "${LR_AICTX}" 2>/dev/null; then ok "[25] 🔒 buildFieldObject 透传 record.timeAlg(直接时间盘不被强施真太阳时)"; else bad "[25] 🔒 buildFieldObject 疑似写死 timeAlg(canping/heluo 等对直接时间盘会错用真太阳时)"; fi
# 坐标转换自检测试存在
if [ -f "${GEO_TEST_JS}" ]; then ok "[25] AstroHelperGeo.test 全半球坐标自检在(回归门禁)"; else bad "[25] 缺 AstroHelperGeo.test"; fi

# 26. 占卜/星盘各页 changeGeo 选地点 → 时区自动校正(resolveGeoZone 单一真源,11 时刻敏感页全接入)
echo "[26] 占卜/星盘选地点时区自动校正哨兵(resolveGeoZone)"
TZUTIL_JS="${UISRC}/utils/timezone.js"
RGZ_TEST_JS="${UISRC}/utils/__tests__/timezone.resolveGeoZone.test.js"
if grep -q "export function resolveGeoZone" "${TZUTIL_JS}" 2>/dev/null; then ok "[26] timezone.js 导出 resolveGeoZone(单一真源:手改优先/坐标推断/缺日期兜底今天)"; else bad "[26] timezone.js 缺 resolveGeoZone 导出"; fi
RGZ_PAGES="components/lrzhan/LiuRengInput.js components/lrzhan/LiuRengBirthInput.js components/suzhan/SuZhanInput.js components/guazhan/GuaZhanInput.js components/dunjia/DunJiaMain.js components/taiyi/TaiYiMain.js components/sanshi/SanShiUnitedMain.js components/divination/DivinationChartShell.js components/astro/IndiaChartMain.js components/astro3d/AstroChartMain3D.js components/dice/DiceMain.js"
rgz_miss=""
for pg in ${RGZ_PAGES}; do
  f="${UISRC}/${pg}"
  grep -q "resolveGeoZone" "$f" 2>/dev/null || rgz_miss="${rgz_miss} $(basename "$pg")"
done
[ -z "${rgz_miss}" ] && ok "[26] 11 时刻敏感页 changeGeo 均接入 resolveGeoZone(六壬/六壬命课/宿占/六爻/奇门/太乙/三式/卜卦择日/印度/3D/骰子)" || bad "[26] 以下页未接入 resolveGeoZone(选地点时区不校正):${rgz_miss}"
if [ -f "${RGZ_TEST_JS}" ]; then ok "[26] resolveGeoZone 全半球自检在(回归门禁)"; else bad "[26] 缺 timezone.resolveGeoZone.test"; fi
# 重锚 date/time:占卜 changeGeo 须 clone+setZone(z) 重锚(否则改时区只动字段、瞬时仍按旧时区→真太阳时/四柱错)
REANCHOR_PAGES="components/lrzhan/LiuRengInput.js components/suzhan/SuZhanInput.js components/guazhan/GuaZhanInput.js components/lrzhan/LiuRengBirthInput.js components/taiyi/TaiYiMain.js components/dunjia/DunJiaMain.js components/sanshi/SanShiUnitedMain.js components/kinastro/KinAstroMain.js"
reanchor_miss=""
for pg in ${REANCHOR_PAGES}; do
  grep -q "setZone(z)" "${UISRC}/${pg}" 2>/dev/null || reanchor_miss="${reanchor_miss} $(basename "$pg")"
done
[ -z "${reanchor_miss}" ] && ok "[26] 占卜各页 changeGeo 重锚 date/time(setZone(z)),改时区瞬时随之偏移、实时重算正确" || bad "[26] 以下页 changeGeo 未重锚 date/time(改时区真太阳时/四柱会错):${reanchor_miss}"
# 策天 KinAstroMain(cetian)选地点已接线(原 showLocation 但无 onGeoChange→选点失效)
if grep -q "onGeoChange={this.changeGeo}" "${UISRC}/components/kinastro/KinAstroMain.js" 2>/dev/null; then ok "[26] 策天 KinAstroMain 已接 onGeoChange+changeGeo(cetian 选点生效)"; else bad "[26] 策天 KinAstroMain 缺 onGeoChange(选地点失效)"; fi
# 奇门 changeGeo 延后 requestNongli 重排(避 hook 预取竞态以旧盘覆盖)
if grep -q "_geoRecalcTimer" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 奇门 changeGeo 延后强制重排(避竞态、改地点实时重算)在"; else bad "[26] 奇门 changeGeo 缺延后重排(改地点不重算风险)"; fi
# 六壬中间盘头部默认显真太阳时(非公历钟表时)
if grep -q "formatTrueSolarTime" "${UISRC}/components/lrzhan/RengChart.js" 2>/dev/null; then ok "[26] 六壬头部显真太阳时(formatTrueSolarTime)在"; else bad "[26] 六壬头部缺真太阳时显示(应默认显真太阳时)"; fi

# 22. 发布范围完整性（防漏合本地分支）—— **铁律**：判断「发布收敛哪些分支 / 哪些 ready」时,绝不凭记忆或部分列表,
#     必枚举所有本地分支并逐个查领先 main 的提交。v2.5.0 险些漏合 feature/ziwei-depth(紫微运限深化 + 六壬Phase4)→ 差点发出残缺版本。
echo "[22] 发布范围完整性(本地分支全枚举,防漏合)"
AHEAD_FEAT=""
while read -r b; do
  [ -n "$b" ] || continue
  n="$(git -C "${REPO_ROOT}" rev-list --count "main..${b}" 2>/dev/null || echo 0)"
  [ "${n:-0}" -gt 0 ] && AHEAD_FEAT="${AHEAD_FEAT} ${b}(+${n})"
done < <(git -C "${REPO_ROOT}" for-each-ref --format='%(refname:short)' refs/heads/ | grep -E '^feature/' || true)
if [ -n "${AHEAD_FEAT}" ]; then
  if [ "${HOROSA_KNOWN_UNMERGED:-}" = "1" ]; then
    warn "feature/* 领先 main,但已 HOROSA_KNOWN_UNMERGED=1 确认非本版:${AHEAD_FEAT}"
  else
    bad "feature/* 分支领先 main,可能漏入本版:${AHEAD_FEAT} —— 必逐个确认应否合并(漏 ziwei-depth 教训);确属未来版本则 HOROSA_KNOWN_UNMERGED=1 跳过"
  fi
else
  ok "无 feature/* 分支领先 main(本地 feature 分支均已纳入/合并)"
fi


# 27. #14（跨平台）本地回环不走系统代理 —— Mac 与 Windows 同因：启动器设 -Djava.net.useSystemProxies=true,
#     开 Clash/v2ray 时 JVM 会把 127.0.0.1/localhost 出站也塞进代理 → 代理转发回环卡顿/超时 →「本地排盘服务未就绪」。
#     修法：doCmd 对回环目标 setProxy(null) 直连；外部请求(api.openai.com 等)仍 getHttpHost 走代理。
echo "[27] #14 本地回环不走系统代理哨兵(跨平台:Mac 同步 Windows)"
HYSTRIX_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/net/http/HttpUriRequestHystrixCommand.java"
if [ -f "${HYSTRIX_JAVA}" ]; then
  if grep -q "isLoopbackTarget" "${HYSTRIX_JAVA}" && grep -q "setProxy(isLoopbackTarget(request) ? null :" "${HYSTRIX_JAVA}"; then
    ok "[27] doCmd 回环目标直连(isLoopbackTarget→setProxy(null)),外部请求仍走 getHttpHost(开系统代理时本地排盘不再被代理转发卡顿)"
  else
    bad "[27] HttpUriRequestHystrixCommand 缺 isLoopbackTarget 回环旁路 —— 开 Clash/v2ray 时本地排盘会被代理转发超时(Win #14 同因,跨平台);务必先补回 doCmd"
  fi
else
  warn "[27] 未找到 HttpUriRequestHystrixCommand.java(boundless 结构变动?手动核实回环旁路仍在)"
fi


# 28. 主 README 版本一致性 —— 教训:v2.5.1 首发漏更三主 README(仍停在 2.5.0,下载链接指向旧 pkg →
#     用户点了拿不到新版)。[1] 只校验 package.json/Cargo/tauri 等,不含 README,故漏网。这里补门禁。
echo "[28] 主 README 版本一致性(徽章 + 下载链接随 app 版本 lockstep)"
README_BAD=0
for rf in README.md README_EN.md README_ZH.md; do
  rp="${REPO_ROOT}/${rf}"
  if [ ! -f "${rp}" ]; then warn "[28] 缺 ${rf}"; continue; fi
  if ! grep -q "version-${VERSION}-" "${rp}"; then bad "[28] ${rf} 版本徽章不是 ${VERSION}(README 漏跟随 app 版本)"; README_BAD=1; fi
  if grep -oE "releases/download/v[0-9]+\.[0-9]+\.[0-9]+/" "${rp}" 2>/dev/null | grep -qv "releases/download/v${VERSION}/"; then bad "[28] ${rf} 有指向非 v${VERSION} 的下载链接(陈旧,用户会下到旧包)"; README_BAD=1; fi
done
[ "${README_BAD}" = "0" ] && ok "[28] 三主 README 版本徽章 + 下载链接均为 v${VERSION}"


# 29. 汉堡中点盘(双技法)哨兵 —— 字形/AI 同步/param error 护栏(2026-06-01 大改)。
echo "[29] 汉堡中点盘 双技法 + AI 段同步 + param error 护栏"
DIAL29_BAD=0
grep -q "AstroText.AstroMsg\[s.rep\]" "${UISRC}/components/germany/UranianDial.js" 2>/dev/null || { bad "[29] 折叠盘扇区字形未用 AstroMsg[名](会渲染成 emoji 彩块,须配 AstroChartFont)"; DIAL29_BAD=1; }
[ -f "${UISRC}/components/germany/UranianModulusDial.js" ] || { bad "[29] 缺 UranianModulusDial.js(多环模数盘技法丢失,用户要求两种盘并存)"; DIAL29_BAD=1; }
grep -q "'90°中点盘'" "${UISRC}/utils/aiExport.js" 2>/dev/null || { bad "[29] aiExport germany 预设缺 '90°中点盘' 段"; DIAL29_BAD=1; }
grep -q "\[90°中点盘\]" "${UISRC}/components/germany/AstroMidpoint.js" 2>/dev/null || { bad "[29] buildGermanySnapshotText 缺 [90°中点盘] 段(AI 挂载/导出/储存漏盘)"; DIAL29_BAD=1; }
grep -q "invalid_date" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" 2>/dev/null || { bad "[29] webchartsrv 缺 NaN 日期护栏(invalid_date,param error 会复发)"; DIAL29_BAD=1; }
[ "${DIAL29_BAD}" = "0" ] && ok "[29] 中点盘双技法/字形 AstroMsg/AI 段同步/webchartsrv NaN 护栏 均在"


# 30. Windows #15：Ollama 走原生 /api/chat（num_ctx 才生效）。Java 改需重编 jar 同步 Win。
echo "[30] Ollama num_ctx：原生 /api/chat 分支(修 Windows #15)"
AIPROXY="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
if [ -f "${AIPROXY}" ]; then
  if grep -q "streamOllamaNative" "${AIPROXY}" && grep -q "/api/chat" "${AIPROXY}" && grep -q "ollamaNativeBase" "${AIPROXY}"; then
    ok "[30] Ollama 聊天走原生 /api/chat + options 嵌套(num_ctx 生效);其它 provider 不变"
  else
    bad "[30] AIAnalysisProxyService 缺 Ollama 原生 /api/chat 分支 —— num_ctx 会被 OpenAI 兼容口忽略、回退 4096 截断(Win #15 复发)"
  fi
else
  warn "[30] 未找到 AIAnalysisProxyService.java(结构变动?手动核实 Ollama 原生分支仍在)"
fi


# 31. 中点盘 UI 验收口径 + Ollama 嵌入 num_ctx (2026-06-02)：
#  - Δ 三角形已替换为短横线("-",仅在读数+树前;Δ 似三角,用户口径)
#  - TNP 关 → 全链路过滤(filterByTnp 在 natalPoints/buildRings 出口,而非 request 入口)
#  - 行运/SA 地点可调(renderLocOverride)
#  - saKey 持久化(UranianDialStyle.DEFAULTS+读取)
#  - Ollama embedding 走原生 /api/embed + options.num_ctx
echo "[31] 中点盘 UI 收尾验收 + Ollama 嵌入 num_ctx"
DIAL31_BAD=0
DIALMAIN="${UISRC}/components/germany/UranianDialMain.js"
if [ -f "${DIALMAIN}" ]; then
  # ① Δ 已删:UranianDialMain 不能再出现「Δ」(指针读数+中点树前)。
  if grep -q "Δ" "${DIALMAIN}"; then bad "[31] UranianDialMain 仍含 Δ(三角形)字符,须用短横线 '-'(用户验收口径)"; DIAL31_BAD=1; fi
  # ② TNP 全链路过滤(filterByTnp 出现 ≥3 次:定义 + natalPoints 出口 + buildRings 行运入口)。
  if ! grep -q "filterByTnp" "${DIALMAIN}"; then bad "[31] UranianDialMain 缺 filterByTnp(TNP 关→读数/中点树不同步隐藏,Win #15 类问题再发)"; DIAL31_BAD=1; fi
  # ③ 地点覆盖:renderLocOverride / transitLat / saLat 三件齐全。
  if ! grep -q "renderLocOverride" "${DIALMAIN}"; then bad "[31] UranianDialMain 缺 renderLocOverride(行运/SA 地点不可调)"; DIAL31_BAD=1; fi
  if ! grep -q "transitLat" "${DIALMAIN}"; then bad "[31] UranianDialMain 缺 transitLat state(地点覆盖未接线)"; DIAL31_BAD=1; fi
  # ④ "拖动定向" 废话已删(防左栏被截断)。
  if grep -q "拖动定向" "${DIALMAIN}"; then bad "[31] UranianDialMain 仍含「拖动定向」废话字样(左栏会被截断,用户验收口径)"; DIAL31_BAD=1; fi
else
  bad "[31] 缺 UranianDialMain.js"
  DIAL31_BAD=1
fi
# ⑤ saKey 入 Style DEFAULTS(刷新页面持久)。
DIALSTYLE="${UISRC}/components/germany/UranianDialStyle.js"
if [ -f "${DIALSTYLE}" ] && ! grep -q "saKey" "${DIALSTYLE}"; then
  bad "[31] UranianDialStyle 缺 saKey 字段(Naibod/1°选择不持久化、刷新即丢)"
  DIAL31_BAD=1
fi
# ⑥ Ollama embedding 原生分支(修 Win #15 嵌入子项)。
if [ -f "${AIPROXY}" ]; then
  if grep -q "embeddingsOllamaNative" "${AIPROXY}" && grep -q "/api/embed" "${AIPROXY}" && grep -q "extractOllamaEmbedVectors" "${AIPROXY}"; then
    :
  else
    bad "[31] AIAnalysisProxyService 缺 Ollama 原生 /api/embed 分支 —— 嵌入仍走兼容口、num_ctx 被忽略(Win #15 嵌入子项复发)"
    DIAL31_BAD=1
  fi
fi
[ "${DIAL31_BAD}" = "0" ] && ok "[31] 中点盘 UI(Δ→短横线/TNP全链路/地点可调/拖动定向已删/saKey 持久) + Ollama 嵌入原生口 均在"


# [32] 主限法方位+时间补全·铁律①守卫
#  - perpredict.py: _byZCoreKernel 函数指针仍在(纯公式 Alcabitius 主路径不被改名/重排)
#  - perpredict.py: CORE_PD_VIRTUAL_BODY_CORR_MODELS(ΔT 取数映射) + ΔT 注入 + 显示窗 + 宿命点闭式 在位
#  - perpredict.py: STATIC_TIME_KEY_SCALES['Ptolemy'] 严格 == 1.0(必须是数值字面量,不接受公式)
#  - perpredict.py: _PD_METHOD_REGISTRY 含 'core_alchabitius' 且默认 fallback 路径正确
#  - 540 case byte-perfect 测试存在并能跑通
echo "[32] 主限法方位+时间补全·铁律①守卫(Alcabitius+Ptolemy 字节级一致)"
PD32_BAD=0
PERPREDICT="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perpredict.py"
if [ -f "${PERPREDICT}" ]; then
  if ! grep -q "def getPrimaryDirectionByZCoreKernel" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 getPrimaryDirectionByZCoreKernel —— Alcabitius+Ptolemy 纯公式主路径被改名/移除(540 case 字节级将失效)"
    PD32_BAD=1
  fi
  if ! grep -q "CORE_PD_VIRTUAL_BODY_CORR_MODELS" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 CORE_PD_VIRTUAL_BODY_CORR_MODELS —— ΔT 校准批量取数映射表不在(_corePdDeltaTPointMap 依赖)"
    PD32_BAD=1
  fi
  if ! grep -q "_corePdDeltaTPointMap" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _corePdDeltaTPointMap —— 未来盘 ΔT 注入失效"
    PD32_BAD=1
  fi
  if ! grep -q "def _passesCoreDisplayWindow" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _passesCoreDisplayWindow —— 行星对显示窗(pre-norm 原值,|Δ|<107.5)被移除"
    PD32_BAD=1
  fi
  if ! grep -q "def _coreVertexArc" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _coreVertexArc —— 宿命点(Vertex)应星闭式被移除"
    PD32_BAD=1
  fi
  if ! grep -q "def _extendCorePdRecurrences" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _extendCorePdRecurrences —— 整圈复发/互补统一扩展被移除(180+ 互补与 3000 年多圈直达都走它)"
    PD32_BAD=1
  fi
  if ! grep -q "min(3000, int(round(float(data\['pdYears'\])))" "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py"; then
    bad "[32] perchart.py pdYears 上限不是 3000 —— 年数选择上限回退"
    PD32_BAD=1
  fi
  # 前端 pdYears clamp 必须四处全 3000(任一回落 360 → 选 3000 在该路径被截断,LIVE 实测真踩过):
  #   AstroPrimaryDirection.normalizePdYears(表格组件) / AstroDirectMain.normalizePdYears(主限tab容器·真fetch路径)
  #   / aiAnalysisContext.normalizePdYearsValue(AI挂载·buildFieldObject) / techniqueMountSettings pdYears max
  PD_CLAMP_360=$(grep -rIl "Math.min(360, n)" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js" 2>/dev/null | wc -l | tr -d ' ')
  PD_CLAMP_3000=$(grep -rl "Math.min(3000, n)" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js" 2>/dev/null | wc -l | tr -d ' ')
  if [ "${PD_CLAMP_360}" != "0" ] || [ "${PD_CLAMP_3000}" != "2" ]; then
    bad "[32] 前端 pdYears clamp 未全 3000(残留 Math.min(360,n)=${PD_CLAMP_360} 处 / 应为 0;3000 命中=${PD_CLAMP_3000} / 应为 2)—— LIVE 实测过:任一处回落会让 3000 年在该路径被截到 360"
    PD32_BAD=1
  fi
  if ! grep -q "Math.min(3000, n)" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js"; then
    bad "[32] aiAnalysisContext.normalizePdYearsValue 上限不是 3000 —— AI 挂载路径会把 3000 截到 360"
    PD32_BAD=1
  fi
  # STATIC_TIME_KEY_SCALES['Ptolemy'] 必须严格 == 1.0 (数值字面量)
  if ! grep -qE "['\"]Ptolemy['\"]\s*:\s*1\.0" "${PERPREDICT}"; then
    bad "[32] STATIC_TIME_KEY_SCALES['Ptolemy'] 必须 == 1.0(数值字面量),不能写成公式或近似值;否则 Ptolemy 默认路径将失去字节级一致"
    PD32_BAD=1
  fi
  if ! grep -q "_PD_METHOD_REGISTRY" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _PD_METHOD_REGISTRY —— strategy 分发被回退(P0 方位法补全失效)"
    PD32_BAD=1
  fi
else
  bad "[32] 缺 perpredict.py"
  PD32_BAD=1
fi
# byte-perfect 测试存在
PD_BYTEPERFECT="${REPO_ROOT}/Horosa-Web/astropy/tests/test_pd_alcabitius_byteperfect.py"
# 金标语料现为 gzip 压缩(.ndjson.gz,test_pd_alcabitius_byteperfect.py 用 gzip.open 读);兼容旧未压缩名。
PD_GOLDEN_GZ="${REPO_ROOT}/Horosa-Web/astropy/tests/data/pd_calibration_corpus/golden_alcabitius_ptolemy_v266.ndjson.gz"
PD_GOLDEN_RAW="${REPO_ROOT}/Horosa-Web/astropy/tests/data/pd_calibration_corpus/golden_alcabitius_ptolemy_v266.ndjson"
if [ ! -f "${PD_BYTEPERFECT}" ]; then
  bad "[32] 缺 tests/test_pd_alcabitius_byteperfect.py —— byte-perfect 守卫缺失,540 case 回归无法跑"
  PD32_BAD=1
fi
if [ ! -f "${PD_GOLDEN_GZ}" ] && [ ! -f "${PD_GOLDEN_RAW}" ]; then
  bad "[32] 缺 tests/data/pd_calibration_corpus/golden_alcabitius_ptolemy_v266.ndjson(.gz) —— byte-perfect 基线缺失"
  PD32_BAD=1
fi
# 实跑 byte-perfect 子集 —— 「golden 与代码脱节(stale fixture)」事故的根因守卫。
# 仅做结构 grep 无法发现 golden 过期(v2.5.4 即因 golden 由中间态生成、从未与代码一致而带病发布,
# 且本门只查文件存在故未拦住);必须实跑确认 golden == 当前 Alcabitius+Ptolemy 输出。
# 默认前 12 case(~20s);HOROSA_PD_BYTEPERFECT_LIMIT 可调,HOROSA_PD_PREFLIGHT_SKIP_BP=1 跳过实跑。
if [ -f "${PD_BYTEPERFECT}" ] && [ "${HOROSA_PD_PREFLIGHT_SKIP_BP:-0}" != "1" ] && command -v python3 >/dev/null 2>&1; then
  PD_BP_LIMIT="${HOROSA_PD_BYTEPERFECT_LIMIT:-12}"
  PD_BP_OUT="$(cd "${REPO_ROOT}/Horosa-Web/astropy" 2>/dev/null && HOROSA_PD_BYTEPERFECT_LIMIT="${PD_BP_LIMIT}" PYTHONPATH="../flatlib-ctrad2:." python3 -m pytest tests/test_pd_alcabitius_byteperfect.py -q 2>&1)"
  if printf '%s\n' "${PD_BP_OUT}" | grep -qE "[0-9]+ passed"; then
    ok "[32] byte-perfect 实跑前 ${PD_BP_LIMIT} case 通过 —— golden 与当前代码字节级一致(防 stale fixture)"
  elif printf '%s\n' "${PD_BP_OUT}" | grep -qE "[0-9]+ failed|Error|Traceback"; then
    bad "[32] byte-perfect 实跑失败 —— Alcabitius+Ptolemy 与 golden 不一致(代码漂移或 golden 过期);末行:$(printf '%s\n' "${PD_BP_OUT}" | tail -1)"
    PD32_BAD=1
  else
    warn "[32] byte-perfect 实跑无法判定(python/依赖?),仅结构校验;末行:$(printf '%s\n' "${PD_BP_OUT}" | tail -1)"
  fi
fi
[ "${PD32_BAD}" = "0" ] && ok "[32] 铁律① Alcabitius+Ptolemy 字节级守卫 + byte-perfect 测试基线 + 子集实跑 均通过"


# [33] 主限法方位+时间补全·strategy 分发完整性 + 前端选项扩 (含铺满/盘宫制/label 收口)
#  - perchart.py: pdMethod 白名单与本仓核验集一致 + pdDirect 解析
#  - 前端 primaryDirectionSync.js: PD_SYNC_REV = 'pd_method_sync_v15' + SUPPORTED_PD_METHODS(核验集)
#  - 后端 helper.py / webchartsrv.py: PD_SYNC_REV 对齐 v10(否则新盘恒误判重算)
#  - pd_engine.py: build_directions + solar_arc_for_years(真太阳弧动态钥匙逆函数)
#  - 表格工具栏单行(无 advanced 第二行,不遮表格);TabPane 名「主限法」
#  - AstroPrimaryDirectionChart.js getTablePdTimeKey 不再强制降级 Naibod
#  - aiAnalysisContext.js 主限法 case 不再硬编码覆盖 pdMethod/pdTimeKey
echo "[33] 主限法方位+时间补全·strategy 分发 + 前端选项扩 (v10+v11)"
PD33_BAD=0
PERCHART="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py"
# 本仓方位法以逐位核验白名单为准(Alchabitius/Meridian/Porphyry/Equal)。
PD_SYNC="${UISRC}/utils/primaryDirectionSync.js"
if [ -f "${PD_SYNC}" ]; then
  if ! grep -q "pd_method_sync_v15" "${PD_SYNC}"; then
    bad "[33] primaryDirectionSync.js PD_SYNC_REV 未升到 'pd_method_sync_v15' —— 旧缓存不重算,新 方位法/世俗/顺逆/真太阳弧 不生效"
    PD33_BAD=1
  fi
  if ! grep -q "SUPPORTED_PD_METHODS" "${PD_SYNC}"; then
    bad "[33] primaryDirectionSync.js 缺 SUPPORTED_PD_METHODS 白名单"
    PD33_BAD=1
  fi
  # 核方位法须在前端白名单(否则下拉选了被 normalize 回退默认)
  for m in meridian porphyry equal_ecliptic equal_hour_circle; do
    grep -q "'${m}'" "${PD_SYNC}" || { bad "[33] primaryDirectionSync.js SUPPORTED_PD_METHODS 缺 '${m}'"; PD33_BAD=1; }
  done
fi
# v10:后端 PD_SYNC_REV 必须与前端一致(均 v10),否则每张新盘首查都误判需重算
for f in "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/helper.py" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"; do
  [ -f "$f" ] && { grep -q "pd_method_sync_v15" "$f" || { bad "[33] 后端 $(basename $f) PD_SYNC_REV 未对齐到 v11(与前端不一致→新盘恒误判重算)"; PD33_BAD=1; }; }
done
# perchart 白名单含核方位法 + pdDirect 解析存在(顺逆同选)
if [ -f "${PERCHART}" ]; then
  for m in meridian porphyry equal_ecliptic equal_hour_circle; do
    grep -q "'${m}'" "${PERCHART}" || { bad "[33] perchart.py pdMethod 白名单缺 '${m}'"; PD33_BAD=1; }
  done
  grep -q "pdDirect" "${PERCHART}" || { bad "[33] perchart.py 缺 pdDirect 解析(顺向 direct,顺逆同选的前提)"; PD33_BAD=1; }
fi
# v10:pd_engine 必备(动态真太阳弧逆函数 solar_arc_for_years + 世俗数值法)
PD_ENGINE="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/pd_engine.py"
if [ -f "${PD_ENGINE}" ]; then
  grep -q "def solar_arc_for_years" "${PD_ENGINE}" || { bad "[33] pd_engine.py 缺 solar_arc_for_years(盘的真太阳弧动态钥匙,否则盘把 TrueSolarArc 当 Ptolemy)"; PD33_BAD=1; }
else
  bad "[33] 缺 pd_engine.py —— 主限法时间钥匙引擎(真太阳弧/太阳弧动态钥匙)不存在"; PD33_BAD=1
fi
# v10:主限法表格工具栏须为单行(无第二行,否则遮挡表格);tab 名为「主限法」
PD_TABLE="${UISRC}/components/astro/AstroPrimaryDirection.js"
if [ -f "${PD_TABLE}" ]; then
  grep -q "horosa-primary-direction-toolbar-advanced" "${PD_TABLE}" && { bad "[33] AstroPrimaryDirection.js 仍有第二行工具栏(advanced)—— 会遮挡表格,须并回单行"; PD33_BAD=1; }
fi
DIRECT_MAIN="${UISRC}/components/direction/AstroDirectMain.js"
if [ -f "${DIRECT_MAIN}" ] && grep -q 'tab="主/界限法"' "${DIRECT_MAIN}"; then
  bad "[33] AstroDirectMain.js 主限法 TabPane 仍名「主/界限法」,应改为「主限法」"
  PD33_BAD=1
fi
# v10 真因守卫:Java getParams 必须透传 pdDirect/pdConverse/pdAntiscia/pdTerms,否则前端传了到不了 Python
#   (ParamHashCache 键=params,缺这些 → direct/converse 同哈希命中同缓存 → 「推运方向选了没用」)
PD_CTRL="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/PredictiveController.java"
if [ -f "${PD_CTRL}" ]; then
  for p in pdDirect pdConverse pdAntiscia pdTerms; do
    grep -q "\"${p}\"" "${PD_CTRL}" || { bad "[33] PredictiveController.java getParams 未透传 '${p}' —— 前端选项到不了 Python(ParamHashCache 还会致顺逆同缓存,选了没用),须补 params.put + 重编 jar"; PD33_BAD=1; }
  done
  # 单源化后控制器不再含字面量:判「引用 PdWire.REV」且「PdWire 定义 = v15」(旧判据只认字面量→误红)
  if ! grep -q "PdWire.REV" "${PD_CTRL}"; then
    bad "[33] PredictiveController.java _wireRev 未引用 PdWire.REV(缓存盐单源破)"; PD33_BAD=1
  elif ! grep -q "pd_method_sync_v15" "${REPO_ROOT}/Horosa-Web/astrostudysrv/basecomm/src/main/java/spacex/basecomm/constants/PdWire.java"; then
    bad "[33] PdWire.REV 未升 v15 —— 旧 ParamHashCache 哈希不失效,新参可能读到旧缓存"; PD33_BAD=1
  fi
fi
PD_CHART="${UISRC}/components/astro/AstroPrimaryDirectionChart.js"
if [ -f "${PD_CHART}" ] && grep -qE "key === 'Naibod' \? DEFAULT_PD_TIME_KEY" "${PD_CHART}"; then
  bad "[33] AstroPrimaryDirectionChart.getTablePdTimeKey 仍强制把 Naibod 降级为 Ptolemy —— P0 起 Naibod 应直接进表格"
  PD33_BAD=1
fi
AIANALYSISCTX="${UISRC}/utils/aiAnalysisContext.js"
if [ -f "${AIANALYSISCTX}" ] && grep -qE "pdMethod: 'core_alchabitius'," "${AIANALYSISCTX}"; then
  bad "[33] aiAnalysisContext.js 主限法 case 仍硬编码 pdMethod='core_alchabitius' —— LLM 上下文永远显示 Alchabitius、与用户实选不符"
  PD33_BAD=1
fi
# v11:主限法盘宫制随方法(_PD_CHART_METHOD_HSYS)——盘的宫头随方位法变,缺则盘恒用本命宫制(方法选了盘不动)
PERPREDICT_V11="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perpredict.py"
if [ -f "${PERPREDICT_V11}" ]; then
  grep -q "_PD_CHART_METHOD_HSYS" "${PERPREDICT_V11}" || { bad "[33] perpredict.py 缺 _PD_CHART_METHOD_HSYS —— 主限法盘宫头不随方位法变"; PD33_BAD=1; }
  grep -q "def _pdChartHouseSystem" "${PERPREDICT_V11}" || { bad "[33] perpredict.py 缺 _pdChartHouseSystem 解析器(盘宫制 fallback 本命制的入口)"; PD33_BAD=1; }
fi
# v11:方位法白名单与时间钥匙铺满——少一处下拉选了被 normalize 回退
if [ -f "${PD_SYNC}" ]; then
  for m in meridian porphyry equal_ecliptic equal_hour_circle; do
    grep -q "'${m}'" "${PD_SYNC}" || { bad "[33] primaryDirectionSync.js SUPPORTED_PD_METHODS 缺 v11 方位法 '${m}'"; PD33_BAD=1; }
  done
  for k in Naibod Cardano SelfMeasure; do
    grep -q "'${k}'" "${PD_SYNC}" || { bad "[33] primaryDirectionSync.js SUPPORTED_PD_TIME_KEYS 缺 v11 时间钥匙 '${k}'"; PD33_BAD=1; }
  done
fi
# 铁律:方位法以逐位核验白名单为准——前端两份白名单(同步层/方法下拉)与 Python 注册表
#   集合必须精确等于 [43] 的核验集;pd_engine 只保留时间钥匙与共享量度原语。
PD_TABLE_OS="${UISRC}/components/astro/AstroPrimaryDirection.js"
PDENG_OS="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/pd_engine.py"
PD33_TABLE="$(python3 - "${REPO_ROOT}" <<'PY33'
import re, sys
src = open(sys.argv[1] + '/Horosa-Web/astrostudyui/src/utils/primaryDirectionSync.js', encoding='utf-8').read()
m = re.search(r"SUPPORTED_PD_METHODS\s*=\s*\[(.*?)\]", src, re.S)
methods = sorted(re.findall(r"'([a-z_]+)'", m.group(1))) if m else []
print(','.join(methods))
PY33
)"
# 方位法白名单:不再硬编码期望串(主限法解禁后本仓法集会随上游增长,硬串每次都要手改)。
# 判据换成「核心必备法齐 + 非空」——真正会出的事故是误删/取不到,而不是"多了名字"。
if [ -z "${PD33_TABLE}" ]; then
  bad "[33] 取不到 SUPPORTED_PD_METHODS(解析源或常量名变了)"; PD33_BAD=1
else
  for _m in core_alchabitius meridian porphyry equal_ecliptic equal_hour_circle; do
    case ",${PD33_TABLE}," in *",${_m},"*) : ;; *) bad "[33] 方位法白名单缺核心法 '${_m}': ${PD33_TABLE}"; PD33_BAD=1 ;; esac
  done
fi
# 方位法全谱开放(2026-07-30):pd_engine 必须含闭式引擎函数(缺=功能残缺),断言随之反转。
[ -f "${PDENG_OS}" ] && ! grep -qE "^def arc_" "${PDENG_OS}" && { bad "[33] pd_engine.py 缺方位法闭式引擎函数(全谱开放后必须在位)"; PD33_BAD=1; }
# v11:AI 导出/挂载快照方法名必走共享 label 字典——AstroDirectMain 的 method/timeKey 文本函数不能再有 'Alchabitius' 字面回退
if [ -f "${DIRECT_MAIN}" ]; then
  grep -q "getPdMethodLabel" "${DIRECT_MAIN}" || { bad "[33] AstroDirectMain.js 未 import/使用 getPdMethodLabel —— 非默认方位法/钥匙的快照名会回退误标 Alchabitius"; PD33_BAD=1; }
  # 旧 bug 模式:primaryDirectionMethodText 内 `return 'Alchabitius'` 字面回退(非 label 字典)
  if grep -A3 "function primaryDirectionMethodText" "${DIRECT_MAIN}" | grep -q "return 'Alchabitius'"; then
    bad "[33] AstroDirectMain.primaryDirectionMethodText 仍字面回退 'Alchabitius' —— 须 delegate 到 getPdMethodLabel(非默认选项导出/挂载会被误标)"
    PD33_BAD=1
  fi
fi
# v11:主限法盘宫制自检测试存在
PD_DIAL_TEST="${REPO_ROOT}/Horosa-Web/astropy/tests/test_pd_dial_house_system.py"
[ -f "${PD_DIAL_TEST}" ] || { bad "[33] 缺 tests/test_pd_dial_house_system.py —— 盘宫制随方法的自检守卫缺失"; PD33_BAD=1; }
[ "${PD33_BAD}" = "0" ] && ok "[33] strategy 分发 + 前端白名单精确集 + 盘宫制随方法 + 共享 label 字典 + AI 上下文实选透传 均到位"


# [34] 七政四余 二十八宿度·自有恒星案三制(回归今制活体距星 / 开禧+岁差 / 郑氏恒星基值)
#  - perchart.py: MOIRA_DISTAR_J2000 (28 距星) + _moira_distar_lon + _moira_ayanamsha 在
#  - perchart.py: setPlanetSu28 支持 byLon (黄道置宿)
#  - 回归今制不再直接用冻结 15.9 当今制(必经活体距星)
#  - 回归测试存在
echo "[34] 七政四余 二十八宿度·自有恒星案三制"
GUO34_BAD=0
if [ -f "${PERCHART}" ]; then
  grep -q "MOIRA_DISTAR_J2000" "${PERCHART}" || { bad "[34] perchart.py 缺 MOIRA_DISTAR_J2000(28 距星表)—— 回归今制活体距星失效"; GUO34_BAD=1; }
  grep -q "_moira_distar_lon" "${PERCHART}" || { bad "[34] perchart.py 缺 _moira_distar_lon(距星严格岁差投射)"; GUO34_BAD=1; }
  grep -q "_moira_ayanamsha" "${PERCHART}" || { bad "[34] perchart.py 缺 _moira_ayanamsha(开禧/恒星制基准)"; GUO34_BAD=1; }
  grep -q "byLon" "${PERCHART}" || { bad "[34] perchart.py setPlanetSu28 缺 byLon(自有恒星案三制须沿黄道置宿)"; GUO34_BAD=1; }
else
  bad "[34] 缺 perchart.py"; GUO34_BAD=1
fi
GUO_TEST="${REPO_ROOT}/Horosa-Web/astropy/tests/test_guolao_su28_moira.py"
[ -f "${GUO_TEST}" ] || { bad "[34] 缺 tests/test_guolao_su28_moira.py(七政四余宿度回归)"; GUO34_BAD=1; }
[ "${GUO34_BAD}" = "0" ] && ok "[34] 七政四余 28 距星表 + 严格岁差 + 黄道置宿 + 回归测试 均在"


# [35] 启动/运行稳健化(P0):白屏兜底 + 后端就绪契约 + Java 绑 127.0.0.1 + Windows 镜像清单
#  - 前端 StartupGate(白屏兜底覆盖层)存在且挂载到 layouts/app.js
#  - webchartsrv.py: /healthz 就绪探针 + HOROSA_READY stdout 握手
#  - start_horosa_local.sh: --server.address=127.0.0.1(根治 Windows 防火墙弹窗,镜像 Windows spec)
#  - docs/windows-启动稳健化-镜像清单.md 在(给 Windows Electron 壳的镜像 spec)
echo "[35] 启动/运行稳健化(P0)"
ST35_BAD=0
ST_GATE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/StartupGate.js"
ST_APP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.js"
ST_CHART="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
ST_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
ST_WINDOC="${REPO_ROOT}/docs/windows-启动稳健化-镜像清单.md"
[ -f "${ST_GATE}" ] || { bad "[35] 缺 StartupGate.js(白屏兜底覆盖层)"; ST35_BAD=1; }
{ [ -f "${ST_APP}" ] && grep -q "StartupGate" "${ST_APP}"; } || { bad "[35] layouts/app.js 未挂载 StartupGate —— 白屏兜底失效"; ST35_BAD=1; }
{ [ -f "${ST_CHART}" ] && grep -q "def healthz" "${ST_CHART}"; } || { bad "[35] webchartsrv.py 缺 /healthz 就绪探针"; ST35_BAD=1; }
{ [ -f "${ST_CHART}" ] && grep -q "HOROSA_READY" "${ST_CHART}"; } || { bad "[35] webchartsrv.py 缺 HOROSA_READY stdout 握手"; ST35_BAD=1; }
{ [ -f "${ST_START}" ] && grep -q "server.address=127.0.0.1" "${ST_START}"; } || { bad "[35] start_horosa_local.sh 缺 --server.address=127.0.0.1(根治防火墙弹窗)"; ST35_BAD=1; }
[ -f "${ST_WINDOC}" ] || { bad "[35] 缺 docs/windows-启动稳健化-镜像清单.md(Windows 镜像 spec)"; ST35_BAD=1; }
[ "${ST35_BAD}" = "0" ] && ok "[35] StartupGate 挂载 + /healthz + HOROSA_READY + 127.0.0.1 绑定 + Windows 镜像清单 均在"


echo "[36] 城市搜索专业化(简体显示 + 拼音/首字母 + 繁简折叠;全技法经纬度共用 GeoCoordSelector)"
CITY_BAD=0
CM_JS="${UISRC}/components/amap/cityMatch.js"
CM_TEST="${UISRC}/components/amap/__tests__/cityMatch.test.js"
CITY_FULL="${UISRC}/data/citiesFull.json"
CITY_MAP="${UISRC}/data/cityTradSimpMap.json"
CITY_SEL="${UISRC}/components/amap/GeoCoordSelector.js"
[ -f "${CM_JS}" ] || { bad "[36] 缺 cityMatch.js(城市检索纯函数,简繁/拼音核心)"; CITY_BAD=1; }
[ -f "${CM_TEST}" ] || { bad "[36] 缺 cityMatch.test.js(城市检索自检)"; CITY_BAD=1; }
[ -f "${CITY_MAP}" ] || { bad "[36] 缺 cityTradSimpMap.json(繁→简折叠表;繁体查询会失效)"; CITY_BAD=1; }
{ [ -f "${CITY_SEL}" ] && grep -q "from './cityMatch'" "${CITY_SEL}"; } || { bad "[36] GeoCoordSelector 未委托 cityMatch(搜索退回旧逻辑)"; CITY_BAD=1; }
# citiesFull 必须带拼音字段 p(中国城市可拼音搜)且已转简体;抽查北京市 + 全表无残留繁体字。
if [ -f "${CITY_FULL}" ]; then
  node -e 'const a=require(process.argv[1]);const bj=a.find(c=>c.n==="北京市");if(!bj||!bj.p||bj.p.indexOf("bei jing")<0){console.error("NO_PINYIN");process.exit(2);}const trad=a.find(c=>/[門臺廣烏齊]/.test(c.n));if(trad){console.error("STILL_TRAD:"+trad.n);process.exit(3);}' "${CITY_FULL}" 2>/dev/null \
    || { bad "[36] citiesFull.json 缺拼音字段 p 或仍含繁体名(须 npm run build:cities 重建)"; CITY_BAD=1; }
else
  bad "[36] 缺 citiesFull.json"; CITY_BAD=1
fi
# 构建依赖只能在 devDependencies(不得进运行时 bundle)。
node -e 'const p=require(process.argv[1]);if((p.dependencies||{})["pinyin-pro"]||(p.dependencies||{})["opencc-js"]){console.error("IN_DEPS");process.exit(2);}if(!(p.devDependencies||{})["pinyin-pro"]||!(p.devDependencies||{})["opencc-js"]){console.error("MISSING_DEV");process.exit(3);}' "${UISRC}/../package.json" 2>/dev/null \
  || { bad "[36] pinyin-pro/opencc-js 必须在 devDependencies(build-only),不得进 dependencies/运行时"; CITY_BAD=1; }
[ "${CITY_BAD}" = "0" ] && ok "[36] cityMatch + 折叠表 + citiesFull(简体+拼音) + GeoCoordSelector 委托 + 构建依赖隔离 均在"


# [37] 起课时间挂载 13 技法 + 5 builder opts 透传 + buildFieldObject divTime 兜底 (2026-06-08)
echo "[37] 起课时间挂载 13 技法 + builder opts 透传 + divTime 兜底"
T37_BAD=0
T37_AICTX="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js"
T37_TMS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/techniqueMountSettings.js"
T37_TMS_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/techniqueMountSettings.test.js"
T37_AICTX_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/aiAnalysisContext.test.js"
T37_TAIXUAN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/taixuan/TaiXuanMain.js"
T37_JINGJUE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/jingjue/JingJueMain.js"
T37_WUZHAO="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/wuzhao/WuZhaoMain.js"
T37_SHENYI="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/shenyishu/ShenYiShuMain.js"
if [ -f "${T37_AICTX}" ]; then
  for k in huangji taixuan jingjue wuzhao shenyishu; do
    awk '/TIMEPOINT_CASTABLE_SET =/' "${T37_AICTX}" | grep -q "${k}" || { bad "[37] TIMEPOINT_CASTABLE_SET 缺 ${k}(下拉能选但显「缺失」)"; T37_BAD=1; }
  done
  grep -q "record.birth || record.divTime" "${T37_AICTX}" || { bad "[37] buildFieldObject 未兜底 record.divTime → timepoint 源 5 法时间出 NaN-undefined"; T37_BAD=1; }
  for k in huangji taixuan jingjue wuzhao shenyishu; do
    grep -qE "case '${k}':" "${T37_AICTX}" || { bad "[37] regenerateCaseTechniqueSnapshot 缺 case '${k}'(改 settings 不重算)"; T37_BAD=1; }
  done
fi
{ [ -f "${T37_TAIXUAN}" ] && grep -q "buildTaiXuanSnapshotForFields(fields, opts)" "${T37_TAIXUAN}"; } || { bad "[37] TaiXuanMain 缺 buildTaiXuanSnapshotForFields(fields, opts)"; T37_BAD=1; }
{ [ -f "${T37_JINGJUE}" ] && grep -q "buildJingJueSnapshotForFields(fields, opts)" "${T37_JINGJUE}"; } || { bad "[37] JingJueMain 缺 buildJingJueSnapshotForFields(fields, opts)"; T37_BAD=1; }
{ [ -f "${T37_WUZHAO}" ] && grep -q "buildWuZhaoSnapshotForFields(fields, opts)" "${T37_WUZHAO}"; } || { bad "[37] WuZhaoMain 缺 buildWuZhaoSnapshotForFields(fields, opts)"; T37_BAD=1; }
{ [ -f "${T37_SHENYI}" ] && grep -q "buildShenYiShuSnapshotForFields(fields, opts)" "${T37_SHENYI}"; } || { bad "[37] ShenYiShuMain 缺 buildShenYiShuSnapshotForFields(fields, opts)"; T37_BAD=1; }
if [ -f "${T37_TMS}" ]; then
  for k in taixuan jingjue wuzhao shenyishu; do
    grep -qE "${k}: \{ kind: 'payload'" "${T37_TMS}" || { bad "[37] techniqueMountSettings ${k} 必 kind:'payload'(sectionsOnly 不调 regenerate)"; T37_BAD=1; }
  done
fi
if [ -f "${T37_TMS_TEST}" ]; then
  awk '/SECTIONS_ONLY =/' "${T37_TMS_TEST}" | grep -q "tongshefa" || { bad "[37] SECTIONS_ONLY 常量被改"; T37_BAD=1; }
fi
[ -f "${T37_AICTX_TEST}" ] && grep -q "timepoint) 必含全 13 项" "${T37_AICTX_TEST}" || { bad "[37] aiAnalysisContext.test.js 缺 13 项 timepoint 锁定断言"; T37_BAD=1; }
[ "${T37_BAD}" = "0" ] && ok "[37] timepoint 13 技法 + 4 builder opts + divTime 兜底 + 5 switch case + 4 payload schema + 测试锁 均到位"


# [38] 合盘 (AstroRelative) 端点 :9999 + 子盘交互全链路 + 黄道 Select 局部定宽 (2026-06-08)
echo "[38] 合盘端点 + 子盘交互全链路 + 黄道 Select 定宽"
R38_BAD=0
R38_REL="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroRelative.js"
R38_LESS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.less"
R38_INDEX="${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js"
if [ -f "${R38_REL}" ]; then
  grep -q "Constants.ServerRoot}/modern/relative" "${R38_REL}" || { bad "[38] AstroRelative 合盘端点必走 :9999 Java"; R38_BAD=1; }
  # 检查非注释行(忽略 // 开头的历史解释注释)
  grep -vE "^\s*//" "${R38_REL}" | grep -q "resolveKentangServiceRoot" && { bad "[38] AstroRelative 残留 resolveKentangServiceRoot active 代码(:8899 不解密)"; R38_BAD=1; }
  grep -q "handleRelativeOnChange" "${R38_REL}" || { bad "[38] AstroRelative 缺 handleRelativeOnChange"; R38_BAD=1; }
  grep -q "ResizeObserver" "${R38_REL}" || { bad "[38] AstroRelative 缺 ResizeObserver(子盘下端空白真因)"; R38_BAD=1; }
fi
if [ -f "${R38_INDEX}" ]; then
  awk '/<AstroRelative/,/\/>/' "${R38_INDEX}" | grep -q "chartStyle={chartStyle}" || { bad "[38] index.js AstroRelative 缺 chartStyle 透传"; R38_BAD=1; }
  awk '/<AstroRelative/,/\/>/' "${R38_INDEX}" | grep -q "onChange={changeCond}" || { bad "[38] index.js AstroRelative 缺 onChange"; R38_BAD=1; }
fi
for f in AstroSynastry AstroMarks AstroComposite AstroTimeSpace; do
  FP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/relative/${f}.js"
  [ -f "${FP}" ] || continue
  grep -q "hidezodiacal={1}" "${FP}" && { bad "[38] ${f} 仍有 hidezodiacal={1}(popover 空白)"; R38_BAD=1; }
  grep -q "hidehsys={1}" "${FP}" && { bad "[38] ${f} 仍有 hidehsys={1}"; R38_BAD=1; }
  awk '/function paramsToFields/,/^}/' "${FP}" | grep -q "value: param.zodiacal" && { bad "[38] ${f} paramsToFields 仍覆盖 zodiacal(左栏改了显示不变)"; R38_BAD=1; }
done
if [ -f "${R38_LESS}" ]; then
  grep -q ".horosa-relative-page .horosa-field-block .ant-select-selector" "${R38_LESS}" || { bad "[38] app.less 缺合盘局部 Select CSS"; R38_BAD=1; }
fi
[ "${R38_BAD}" = "0" ] && ok "[38] 合盘 :9999 + 5 props 透传 + handleRelativeOnChange + ResizeObserver + paramsToFields 净化 + 黄道局部定宽 均到位"


# [39] Python helper 接受数值 geo (地图选点存浮点) (2026-06-08)
echo "[39] Python helper 接受数值 geo"
GE39_BAD=0
GE39_HELP="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/helper.py"
GE39_REAL="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/jieqi/realsuntime.py"
if [ -f "${GE39_HELP}" ]; then
  grep -q "isinstance(lon," "${GE39_HELP}" || { bad "[39] helper.py 缺 isinstance(lon, ...)"; GE39_BAD=1; }
  grep -q "isinstance(lat," "${GE39_HELP}" || { bad "[39] helper.py 缺 isinstance(lat, ...)"; GE39_BAD=1; }
fi
if [ -f "${GE39_REAL}" ]; then
  grep -q "isinstance(zone," "${GE39_REAL}" || { bad "[39] realsuntime.py 缺 isinstance(zone, ...)"; GE39_BAD=1; }
fi
[ "${GE39_BAD}" = "0" ] && ok "[39] helper.py + realsuntime.py 数值 geo 容错 均在"


# [40] 本地工作文件不入库
echo "[40] 本地工作文件未入库"
S40_BAD=0
for f in AGENTS.md CLAUDE.md Horosa-Web/AGENTS.md Horosa-Web/CLAUDE.md; do
  if git -C "${REPO_ROOT}" ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    bad "[40] ${f} 被 git 跟踪(应保持本地,见 .gitignore)"; S40_BAD=1
  fi
done
[ "${S40_BAD}" = "0" ] && ok "[40] 本地工作文件未入库"


# [41] 已修缺陷模式负向门禁 (2026-06-10 算法/设置/渲染扫雷批)
# 这批模式都是实战修掉的 bug 形态,任何一处再现 = 回归(grep -a:部分源码含 emoji 会被 grep 误判二进制)。
echo "[41] 已修缺陷模式负向门禁"
R41_BAD=0
R41_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
R41_PY="${REPO_ROOT}/Horosa-Web/astropy/astrostudy"
# ① antd 按钮直挂带参 handler:点击事件会被当首参串化成 "[object Object]" 发出
grep -ran "onClick={handleSend}" "${R41_UI}" --include="*.js" >/dev/null && { bad "[41] 发送按钮直挂 onClick={handleSend} 再现(事件对象会被当文本发出)"; R41_BAD=1; }
# ② 接口家族判定写死 'openai':预设实际值是 'openai-compatible',判定永假
grep -ran "protoFamily === 'openai'" "${R41_UI}" --include="*.js" >/dev/null && { bad "[41] protoFamily === 'openai' 死分支再现(应走 isOpenAiFamily)"; R41_BAD=1; }
# ③ 列表 key 用随机串(每次渲染重挂,丢焦点/白耗)。全仓存量待清(legacy 惯用法,百余处),
#    本门禁先钉「已修文件零回归」;新文件请直接用稳定 key。
for R41_F in components/calendar/NongLi.js components/calendar/NongLiMain.js components/ziwei/ZiWeiMain.js components/deeplearn/DLFeature.js components/germany/Midpoint.js components/reader/BookReader.js components/dice/DiceMain.js; do
  grep -an "key={randomStr(" "${R41_UI}/${R41_F}" >/dev/null 2>&1 && { bad "[41] ${R41_F} 的 randomStr key 回归"; R41_BAD=1; }
done
# ④ SVG 属性拼写:stroke-dashanray 会被静默忽略
grep -ran "stroke-dashanray" "${R41_UI}" --include="*.js" >/dev/null && { bad "[41] stroke-dashanray 拼写再现(应为 stroke-dasharray)"; R41_BAD=1; }
# ⑤ 经纬度分换算公式回退:deg + 1.0/min(应为 min/60)
grep -rn "(1.0 / min)" "${R41_PY}" --include="*.py" >/dev/null && { bad "[41] 经纬度 deg+(1.0/min) 公式回退"; R41_BAD=1; }
# ⑥ 圆周距离常量回退:delta = 360 - 180
grep -ran "delta = 360 - 180" "${R41_UI}" --include="*.js" >/dev/null && { bad "[41] distanceInCircleAbs 360-180 常量回退"; R41_BAD=1; }
# ⑦ absDistance 第二窗口符号回退
grep -rn "360 - ang2 - ang1" "${R41_PY}" --include="*.py" >/dev/null && { bad "[41] absDistance 360-ang2-ang1 符号回退"; R41_BAD=1; }
[ "${R41_BAD}" = "0" ] && ok "[41] 7 类已修缺陷模式零再现"

# [42] 发布脚本 config 交接必须 TAB 分隔 (appName 含空格时空格分词会整串右移,
#      RUNTIME_ASSET 变成名字后半截 → "missing runtime archive" 假报,打包中断)
echo "[42] 发布脚本 config 交接 TAB 安全"
S42_BAD=0
for S42_F in build_desktop_release.sh verify_github_release_end_to_end.sh verify_desktop_packaging.sh; do
  S42_P="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/${S42_F}"
  [ -f "${S42_P}" ] || continue
  grep -Eq "IFS=.+ read -r APP_NAME" "${S42_P}" || { bad "[42] ${S42_F} 的 APP_NAME read 缺 IFS 限定(空格 appName 会右移)"; S42_BAD=1; }
  grep -q "sep='\\\\t'" "${S42_P}" || { bad "[42] ${S42_F} 的 python 配置打印缺 sep='\\\\t'"; S42_BAD=1; }
done
[ "${S42_BAD}" = "0" ] && ok "[42] config 交接 TAB 分隔在位"

# [43] 更新通道隔离 (2026-06-10): 本仓 app 身份/更新源四件套必须自洽,且 publish 带产物身份硬闸。
#      防两类事故: ①壳层兜底配置漂移 → 装机用户的自动更新拉错源; ②误把别处构建的产物传进本仓 release。
echo "[43] 更新通道隔离(身份四件套 + publish 硬闸)"
U43_BAD=0
U43_TAURI="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/tauri.conf.json"
U43_RC="${REPO_ROOT}/Horosa_Desktop_Installer/config/release_config.json"
U43_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
U43_PUBSH="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh"
U43_ID="$(python3 -c "import json;print(json.load(open('${U43_TAURI}'))['identifier'])" 2>/dev/null)"
U43_PN="$(python3 -c "import json;print(json.load(open('${U43_TAURI}'))['productName'])" 2>/dev/null)"
U43_AN="$(python3 -c "import json;print(json.load(open('${U43_RC}'))['appName'])" 2>/dev/null)"
U43_RN="$(python3 -c "import json;print(json.load(open('${U43_RC}'))['repoName'])" 2>/dev/null)"
[ "${U43_ID}" = "com.horacedong.horosa" ] || { bad "[43] tauri identifier=${U43_ID} ≠ com.horacedong.horosa"; U43_BAD=1; }
[ "${U43_PN}" = "星阙" ] || { bad "[43] tauri productName=${U43_PN} ≠ 星阙"; U43_BAD=1; }
[ "${U43_AN}" = "星阙" ] || { bad "[43] release_config appName=${U43_AN} ≠ 星阙"; U43_BAD=1; }
[ "${U43_RN}" = "Horosa-Web-App-comprehensively-improved-MacOS" ] || { bad "[43] release_config repoName=${U43_RN} ≠ Horosa-Web-App-comprehensively-improved-MacOS(更新会拉错源!)"; U43_BAD=1; }
grep -q 'const APP_NAME: &str = "星阙"' "${U43_MAIN}" || { bad "[43] main.rs APP_NAME 兜底 ≠ 星阙"; U43_BAD=1; }
grep -q 'const APP_IDENTIFIER: &str = "com.horacedong.horosa"' "${U43_MAIN}" || { bad "[43] main.rs APP_IDENTIFIER 兜底 ≠ com.horacedong.horosa"; U43_BAD=1; }
grep -q 'const DEFAULT_REPO_NAME: &str = "Horosa-Web-App-comprehensively-improved-MacOS"' "${U43_MAIN}" || { bad "[43] main.rs DEFAULT_REPO_NAME 兜底漂移(配置缺失时更新会拉错源)"; U43_BAD=1; }
grep -q "更新通道隔离硬闸" "${U43_PUBSH}" || { bad "[43] publish_github_release.sh 缺产物身份硬闸"; U43_BAD=1; }
# 共享目录单源化:安装器与壳层必须同目录;runtime 须带 appName 身份戳并在安装时验明
U43_SRN="$(python3 -c "import json;print(json.load(open('${U43_RC}')).get('sharedRootName',''))" 2>/dev/null)"
[ "${U43_SRN}" = "Horosa" ] || { bad "[43] release_config sharedRootName=${U43_SRN} ≠ Horosa"; U43_BAD=1; }
U43_TPL="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template"
grep -q "__SHARED_ROOT_NAME__" "${U43_TPL}" || { bad "[43] postinstall 模板缺 __SHARED_ROOT_NAME__ 占位"; U43_BAD=1; }
grep -q 'manifest_app.*APP_NAME' "${U43_TPL}" || { bad "[43] postinstall 缺 runtime 身份验明"; U43_BAD=1; }
grep -q "__SHARED_ROOT_NAME__" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh" || { bad "[43] build 脚本未渲染 __SHARED_ROOT_NAME__"; U43_BAD=1; }
grep -q '"appName": "\${PAYLOAD_APP_NAME}"' "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh" || { bad "[43] runtime manifest 缺 appName 身份戳"; U43_BAD=1; }
# 主限法方位法白名单精确集合(本仓=逐位核验核集;白名单之外任何名字混入即红,无需枚举黑名单)
U43_PD="$(python3 - "${REPO_ROOT}" <<'PY43'
import re, sys
src = open(sys.argv[1] + '/Horosa-Web/astrostudyui/src/utils/primaryDirectionSync.js', encoding='utf-8').read()
m = re.search(r'SUPPORTED_PD_METHODS\s*=\s*\[(.*?)\]', src, re.S)
methods = sorted(re.findall(r"'([a-z_]+)'", m.group(1))) if m else []
print(','.join(methods))
PY43
)"
# JS 侧白名单取值(与下面 Python registry 互校;不硬编码期望串——法集会随上游解禁增长)
U43_REG="$(cd "${REPO_ROOT}/Horosa-Web/astropy" && python3 -c "
import re
src = open('astrostudy/perpredict.py', encoding='utf-8').read()
m = re.search(r'_PD_METHOD_REGISTRY\s*=\s*\{(.*?)\n\}', src, re.S)
keys = sorted(set(re.findall(r\"'([a-z_]+)':\", m.group(1)))) if m else []
print(','.join(keys))" 2>/dev/null)"
# 🔴 真正的判据是「两端一致」而非「等于某个写死的集合」:
#    前端白名单与后端 registry 不同步,才会出"下拉能选、后端不认(或反之)"的静默故障。
#    主限法解禁后本仓法集会随上游增长,硬编码期望串每次同步都得手改、且必然滞后判红。
if [ -z "${U43_PD}" ] || [ -z "${U43_REG}" ]; then
  bad "[43] 方位法集合取不到(JS='${U43_PD}' Py='${U43_REG}')—— 解析源或常量名变了"; U43_BAD=1
elif [ "${U43_PD}" != "${U43_REG}" ]; then
  bad "[43] 前端白名单与 Python _PD_METHOD_REGISTRY 不一致 —— 会出「能选但后端不认」: JS=${U43_PD} / Py=${U43_REG}"; U43_BAD=1
else
  U43_N="$(printf '%s' "${U43_PD}" | awk -F, '{print NF}')"
  [ "${U43_N}" -ge 6 ] || { bad "[43] 方位法集合只剩 ${U43_N} 项(<6)—— 疑误删: ${U43_PD}"; U43_BAD=1; }
  for _m in core_alchabitius meridian porphyry equal_ecliptic equal_hour_circle; do
    case ",${U43_PD}," in *",${_m},"*) : ;; *) bad "[43] 方位法集合缺核心法 '${_m}'"; U43_BAD=1 ;; esac
  done
fi
[ "${U43_BAD}" = "0" ] && ok "[43] 身份四件套 + publish 硬闸 + 共享目录单源 + 方位法白名单精确集 在位"

# [44] 远端隔离白名单 (2026-06-10): 本仓所有 git remote URL 只允许指向本仓自身,
#      杜绝接错远端互推;publish 的 runtime 内嵌前端一致性闸也必须在位。
echo "[44] 远端隔离白名单 + runtime 内嵌前端闸"
R44_BAD=0
while IFS= read -r R44_URL; do
  case "${R44_URL}" in
    *github.com[:/]Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS*) : ;;
    *) bad "[44] 远端 URL 不在本仓白名单: ${R44_URL}"; R44_BAD=1 ;;
  esac
done <<EOF44
$(git -C "${REPO_ROOT}" remote -v | awk '{print $2}' | sort -u)
EOF44
grep -q "runtime 包内嵌前端" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh" || { bad "[44] publish 缺 runtime 内嵌前端一致性闸"; R44_BAD=1; }
[ "${R44_BAD}" = "0" ] && ok "[44] 远端全在白名单 + runtime 前端闸在位"

# [45] 发布敏感词扫描 (2026-06-11): 工作树全部 tracked 内容 + origin/main..HEAD 每个
#      commit 树 + 全部 commit message,逐一过本地敏感词模式表(token/调试标记/工作
#      笔记词汇等,表不入库)。模式表丢失 = 视为未审,直接红(fail-closed)。
echo "[45] 发布敏感词扫描(工作树 + 未推区间)"
S45_BAD=0
S45_PAT="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/.secrecy_patterns.sh"
if [ ! -f "${S45_PAT}" ]; then
  bad "[45] 本地敏感词模式表缺失(${S45_PAT} 不入库,换机/重 clone 后须先恢复) —— 缺表=未审,不放行"
else
  # shellcheck disable=SC1090
  . "${S45_PAT}"
  S45_A_ARGS=()
  for S45_P in "${HOROSA_FORBIDDEN_A[@]}"; do S45_A_ARGS+=(-e "${S45_P}"); done
  S45_VENDOR_EXCL=":(exclude)Horosa-Web/vendor/"
  # 玄学史(xuanshi)data 永久豁免本扫描(2026-06-28 用户拍板·制度化):公有古籍编纂模块,
  #   其历史名词经人工逐条核实纯属公有典籍引用、无任何受限内容 → 整 data 目录永不入扫描。
  #   (注:本注释刻意不写具体历史名词,以免本 preflight 文件自身命中扫描。)
  S45_XUANSHI_EXCL=":(exclude)Horosa-Web/astropy/astrostudy/xuanshi/data/"
  # -a 强制文本扫描(替换原 -I:它会静默跳过被判 binary 的 unicode 密集 JS,曾致盲漏过中文禁词);
  # 真二进制资产按扩展名排除,防随机字节伪命中。
  S45_BIN_EXCL=(":(exclude)*.png" ":(exclude)*.icns" ":(exclude)*.jar" ":(exclude)*.gz" ":(exclude)*.zip" ":(exclude)*.woff" ":(exclude)*.woff2" ":(exclude)*.ttf" ":(exclude)*.ico" ":(exclude)*.jpg" ":(exclude)*.dat")
  # ① 工作树 tracked 内容(含未提交修改)
  S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_A_ARGS[@]}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | head -5)"
  [ -n "${S45_HITS}" ] && { bad "[45] 工作树命中敏感词:"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  for S45_ROW in "${HOROSA_FORBIDDEN_B[@]}"; do
    S45_P="${S45_ROW%%$'\t'*}"; S45_ALLOW="${S45_ROW#*$'\t'}"
    S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_P}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | grep -Ev "${S45_ALLOW}" | head -5)"
    [ -n "${S45_HITS}" ] && { bad "[45] 工作树命中敏感词(豁免外): ${S45_P}"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  done
  # ①' W 组(机器路径/PII/内部代号):仅工作树查 —— 保证最新快照干净;旧历史 + tag
  #     已公开的同类痕迹归 filter-repo 全历史改写(碰 GitHub 决策),不在此误红历史。
  if [ "${#HOROSA_FORBIDDEN_W[@]}" -gt 0 ]; then
    S45_W_ARGS=()
    for S45_P in "${HOROSA_FORBIDDEN_W[@]}"; do S45_W_ARGS+=(-e "${S45_P}"); done
    S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -F "${S45_W_ARGS[@]}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | head -5)"
    [ -n "${S45_HITS}" ] && { bad "[45] 工作树命中机器路径/PII(W 组):"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  fi
  # ② 未推区间每个 commit 的树(防「工作树已清但历史 blob 仍带」—— 推上去即留痕)
  for S45_C in $(git -C "${REPO_ROOT}" rev-list origin/main..HEAD 2>/dev/null); do
    S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_A_ARGS[@]}" "${S45_C}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | head -5)"
    [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit ${S45_C:0:9} 树内命中敏感词:"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
    for S45_ROW in "${HOROSA_FORBIDDEN_B[@]}"; do
      S45_P="${S45_ROW%%$'\t'*}"; S45_ALLOW="${S45_ROW#*$'\t'}"
      S45_HITS="$(cd "${REPO_ROOT}" && git grep -a -n -E "${S45_P}" "${S45_C}" -- "${S45_VENDOR_EXCL}" "${S45_XUANSHI_EXCL}" "${S45_BIN_EXCL[@]}" 2>/dev/null | grep -Ev "${S45_ALLOW}" | head -5)"
      [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit ${S45_C:0:9} 命中敏感词(豁免外): ${S45_P}"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
    done
  done
  # ③ 未推区间全部 commit message
  S45_HITS="$(git -C "${REPO_ROOT}" log --format='%h %B' origin/main..HEAD 2>/dev/null | grep -E "${S45_A_ARGS[@]}" | head -5)"
  [ -n "${S45_HITS}" ] && { bad "[45] 未推 commit message 命中敏感词:"; printf '%s\n' "${S45_HITS}" >&2; S45_BAD=1; }
  [ "${S45_BAD}" = "0" ] && ok "[45] 工作树 + $(git -C "${REPO_ROOT}" rev-list --count origin/main..HEAD 2>/dev/null) 个未推 commit + message 敏感词零命中"
fi

# [46] 后端只绑回环 (2026-06-12): :9999 默认 0.0.0.0 局域网可达(AI 代理持用户 key)。双保险。
echo "[46] 后端回环绑定双保险"
S46_BAD=0
grep -q "^server.address=127.0.0.1" "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/application.properties" || { bad "[46] application.properties 缺 server.address=127.0.0.1"; S46_BAD=1; }
grep -q -- "--server.address=127.0.0.1" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || { bad "[46] start 脚本缺 --server.address=127.0.0.1"; S46_BAD=1; }
[ "${S46_BAD}" = "0" ] && ok "[46] properties + start 脚本 双双只绑 127.0.0.1"

# [47] Java component-scan 集合不漂移 (2026-06-12): spring-mvc.xml base-package = 注册真相,
#      新增包须过可达性评审(遗留死模块绝不悄然激活)。
echo "[47] Java 扫描包集合"
S47_GOT="$(python3 -c "
import re
src = open('${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/conf/spring-mvc.xml', encoding='utf-8').read()
m = re.search(r'base-package=\"(.*?)\"', src, re.S)
pkgs = sorted(p.strip() for p in m.group(1).split(',') if p.strip()) if m else []
print(','.join(pkgs))" 2>/dev/null)"
S47_WANT="boundless.spring.help.controller,boundless.spring.help.springcomp,spacex.astrodeeplearn.controller,spacex.astroesp.controller,spacex.astroreader.controller,spacex.astrostudy.controller,spacex.astrostudy.service,spacex.astrostudycn.controller,spacex.basecomm.controller"
[ "${S47_GOT}" = "${S47_WANT}" ] && ok "[47] component-scan 9 包精确不漂移" || bad "[47] 扫描包集合漂移: ${S47_GOT}"

# [48] didMount 副作用必须有清理 (2026-06-12): 持续副作用(listener/interval/observer)无
#      willUnmount = SPA 反复挂卸的累积泄漏。负向门禁,新增即红。
echo "[48] 前端挂载副作用清理"
S48_HITS="$(python3 - "${REPO_ROOT}/Horosa-Web/astrostudyui/src" <<'PY48'
import os, re, sys
root = sys.argv[1]
bad = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in ('__tests__', 'node_modules')]
    for fn in filenames:
        if not fn.endswith('.js') or fn.endswith('.test.js'):
            continue
        path = os.path.join(dirpath, fn)
        try:
            src = open(path, encoding='utf-8').read()
        except Exception:
            continue
        m = re.search(r'componentDidMount\s*\(', src)
        if not m:
            continue
        # didMount 起到下一个同级方法名的粗块
        block = src[m.start():m.start() + 4000]
        nxt = re.search(r'\n\t(?:async )?[a-zA-Z_$][\w$]*\s*\(', block[20:])
        if nxt:
            block = block[:20 + nxt.start()]
        if re.search(r'addEventListener|setInterval|new (Resize|Mutation|Intersection)Observer', block):
            if 'componentWillUnmount' not in src:
                bad.append(os.path.relpath(path, root))
print('\n'.join(sorted(bad)))
PY48
)"
[ -z "${S48_HITS}" ] && ok "[48] didMount 持续副作用均有 willUnmount" || { bad "[48] 以下组件 didMount 注册持续副作用但无 willUnmount:"; printf '%s\n' "${S48_HITS}" >&2; }

# [49] CSP 双表面在位 (2026-06-12): 主界面经 tiny_http(main.rs),launcher 经 tauri.conf。
echo "[49] CSP 双表面"
S49_BAD=0
grep -q "Content-Security-Policy" "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs" || { bad "[49] main.rs 静态服务器缺 CSP 头"; S49_BAD=1; }
python3 -c "
import json
c = json.load(open('${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/tauri.conf.json'))
csp = c['app']['security'].get('csp')
raise SystemExit(0 if csp and 'default-src' in csp else 1)" || { bad "[49] tauri.conf launcher CSP 为空"; S49_BAD=1; }
[ "${S49_BAD}" = "0" ] && ok "[49] 主界面 + launcher CSP 均在位"

# [50] 安装分发守卫 (2026-06-12): arm64-only + macOS 12+ gate + entitlements,缺一不可
#      (productbuild 默认 Distribution 允许 x86_64,Intel/旧 OS 用户装完即崩)。
echo "[50] 安装分发守卫"
S50_BAD=0
S50_DIST="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/distribution.xml.template"
[ -f "${S50_DIST}" ] || { bad "[50] distribution.xml.template 缺失"; S50_BAD=1; }
grep -q 'hostArchitectures="arm64"' "${S50_DIST}" 2>/dev/null || { bad "[50] Distribution 缺 arm64-only gate"; S50_BAD=1; }
grep -q 'os-version min="12.0"' "${S50_DIST}" 2>/dev/null || { bad "[50] Distribution 缺 macOS 12+ gate"; S50_BAD=1; }
grep -q -- "--distribution" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh" || { bad "[50] build 脚本未走 --distribution"; S50_BAD=1; }
grep -q 'uname -m' "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template" || { bad "[50] postinstall 缺 arch 兜底守卫"; S50_BAD=1; }
[ -f "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/horosa.entitlements" ] || { bad "[50] entitlements 文件缺失"; S50_BAD=1; }
grep -q "horosa.entitlements" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh" || { bad "[50] build 脚本未默认挂 entitlements"; S50_BAD=1; }
[ "${S50_BAD}" = "0" ] && ok "[50] arm64+12.0 gate / postinstall 兜底 / entitlements 全在位"

# [51] 退出不阻塞 + 启动不冻结 (2026-06-12):
#      ① 退出两臂(ExitRequested/Exit)禁同步 cleanup_state/.status()(macOS Quit=terminate: 只回调
#        Exit,同步子进程=主循环停摆=not responding),必须走 detached+去重的 spawn_exit_cleanup;
#      ② 运行时脚本端口检查禁 lsof(全进程 FD 扫描遇卡死进程单次 stall 30~100s,实测),必须 netstat;
#      ③ start_runtime 的全树元数据清理必须在 !trusted_runtime 守卫下(冷缓存下遍历数十秒=卡 36%),
#        且重活前必须先发 indeterminate 进度。
echo "[51] 退出不阻塞 + 启动不冻结"
S51_BAD=0
S51_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S51_EXIT_BLOCK="$(awk '/RunEvent::ExitRequested \{ .. \} =>/,/^            _ => \{\}/' "${S51_MAIN}")"
[ -n "${S51_EXIT_BLOCK}" ] || { bad "[51] 未能定位 run loop 退出两臂(结构变了?同步更新本哨兵)"; S51_BAD=1; }
printf '%s' "${S51_EXIT_BLOCK}" | grep -q "cleanup_state(" && { bad "[51] 退出臂回归了同步 cleanup_state(会阻塞主循环)"; S51_BAD=1; }
printf '%s' "${S51_EXIT_BLOCK}" | grep -q "\.status()" && { bad "[51] 退出臂出现同步 .status()"; S51_BAD=1; }
[ "$(printf '%s' "${S51_EXIT_BLOCK}" | grep -c "spawn_exit_cleanup(app)")" -ge 2 ] || { bad "[51] 退出两臂缺 spawn_exit_cleanup"; S51_BAD=1; }
for S51_SCRIPT in "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"; do
  if grep -v '^[[:space:]]*#' "${S51_SCRIPT}" | grep -q "lsof"; then
    bad "[51] $(basename "${S51_SCRIPT}") 非注释行出现 lsof(必须 netstat 读内核表)"; S51_BAD=1
  fi
done
grep -q "netstat -anv -p tcp" "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" || { bad "[51] stop 脚本缺 netstat 端口扫描"; S51_BAD=1; }
grep -Fq 'grep -Fq "${ROOT}"' "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" || { bad "[51] stop 脚本丢了工作区守卫(会误杀第二份 checkout)"; S51_BAD=1; }
grep -q "sleep 0.1" "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" || { bad "[51] stop 脚本 0.1s 轮询丢失"; S51_BAD=1; }
grep -v '^[[:space:]]*#' "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh" | grep -Eq '^[[:space:]]*sleep 1([[:space:]]|$)' && { bad "[51] stop 脚本回归整秒 sleep"; S51_BAD=1; }
grep -A1 "if !trusted_runtime {" "${S51_MAIN}" | grep -q "prepare_runtime_dir" || { bad "[51] start_runtime 的 prepare_runtime_dir 失去 !trusted_runtime 守卫(冷缓存全树遍历会卡 36%)"; S51_BAD=1; }
grep -q '正在准备启动环境' "${S51_MAIN}" || { bad "[51] start_runtime 入口缺 indeterminate 进度(重活前进度会冻在 36%)"; S51_BAD=1; }
grep -q "'lsof', '-nP'" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" || { bad "[51] webchartsrv.py 的 lsof 回退缺 -nP(DNS 反查会超 timeout 假阴性)"; S51_BAD=1; }
# 首启稳定性 (2026-06-12 安装包卡死根治后增):
S51_PROBE_NOPROXY="$(grep -cE "curl -s --noproxy '\\*'" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || true)"
[ "${S51_PROBE_NOPROXY}" -ge 2 ] || { bad "[51] start 脚本探测 curl 缺 --noproxy '*'(代理环境会卡首启)"; S51_BAD=1; }
grep -q "ProxyHandler({})" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || { bad "[51] start 脚本 urllib 回退缺禁代理 opener"; S51_BAD=1; }
grep -Eq 'port_listening "\$\{CHART_PORT\}" && port_listening "\$\{BACKEND_PORT\}" *; *then' "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" && { bad "[51] 等待循环回归 netstat 端口硬闸"; S51_BAD=1; }
grep -q 'command.env_remove(proxy_var)' "${S51_MAIN}" || { bad "[51] main.rs 未在 spawn 脚本前 env_remove 代理变量"; S51_BAD=1; }
grep -q 'chmod -R a+rwX "${SHARED_ROOT}"' "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template" || { bad "[51] postinstall 缺 a+rwX"; S51_BAD=1; }
grep -q 'chmod -R a+rX "${SHARED_ROOT}"' "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template" && { bad "[51] postinstall 回归只读 a+rX"; S51_BAD=1; }
[ "${S51_BAD}" = "0" ] && ok "[51] 退出 detached+去重 / 端口检查 netstat 化 / 探测防代理 / http 直判就绪 / 共享树可写 全在位"

# [52] 占星地图 ACG 全流派:引擎 golden(validate_acg 对 swisseph 独立反验,退0)+
#      三层透传(Java AcgController 白名单是唯一闸门,漏登=前端参数静默丢)+ 前端接线。
S52_BAD=0
S52_PY="${REPO_ROOT}/Horosa-Web/astropy"
S52_ENG="${S52_PY}/astrostudy/acg/ACGraph.py"
S52_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/AcgController.java"
S52_FE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/acg/AstroAcg.js"
S52_MAP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/acg/AcgD3Map.js"
echo "[52] 占星地图 ACG 全流派(口径/线型/坐标系/CCG/关系盘/固定星/寻宝图)"
for fn in "_aspectLines" "_eastWestLines" "_antisciaLines" "_vertexLines" "_cuspLines" "_lotsLines" "_midpointLines" "_geodeticLines" "_crossings" "_starLines" "_starParans" "_ccgLines" "findMundaneEvent" "_lsRhumb"; do
  grep -q "${fn}" "${S52_ENG}" 2>/dev/null || { bad "[52] ACGraph 缺 ${fn}"; S52_BAD=1; }
done
for p in "mode" "lsMode" "geodetic" "cuspLines" "coord" "ayanamsa" "stars" "ccgDate" "ccgMix" "relMode" "relDate"; do
  grep -q "containsParam(\"${p}\")" "${S52_JAVA}" 2>/dev/null || { bad "[52] AcgController 白名单缺 ${p}"; S52_BAD=1; }
done
grep -q "drawTreasure" "${S52_MAP}" 2>/dev/null || { bad "[52] AcgD3Map 缺寻宝图热力层"; S52_BAD=1; }
grep -q "ayanamsa:" "${S52_FE}" 2>/dev/null || { bad "[52] AstroAcg 缺参数接线"; S52_BAD=1; }
if [ "${S52_BAD}" = "0" ] && command -v python3 >/dev/null 2>&1 && [ "${HOROSA_ACG_PREFLIGHT_SKIP:-0}" != "1" ]; then
  S52_OUT="$(cd "${S52_PY}" 2>/dev/null && PYTHONPATH="../flatlib-ctrad2:." python3 astrostudy/acg/validate_acg.py 2>&1)" || {
    bad "[52] 🔴 validate_acg golden 未退0: $(printf '%s' "${S52_OUT}" | tail -2 | head -1)"; S52_BAD=1; }
  printf '%s' "${S52_OUT}" | grep -q "ACG alignment PASS" || { bad "[52] validate_acg 输出无 PASS"; S52_BAD=1; }
fi
[ "${S52_BAD}" = "0" ] && ok "[52] 占星地图 引擎golden+白名单+前端接线 在位" || bad "[52] 占星地图 护栏 有缺失"

# [53] 性能资产护栏:exploded/CDS 启动、请求去重、前端分包、pyc 预编译、启动骨架、计算缓存面。
S53_BAD=0
S53_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S53_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S53_UMIRC="${REPO_ROOT}/Horosa-Web/astrostudyui/.umirc.js"
S53_DEDUPE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/requestDedupe.js"
S53_REQ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/request.js"
S53_EJS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/document.ejs"
S53_HELPER="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/helper/AstroHelper.java"
echo "[53] 性能资产(exploded/CDS·分包·去重·pyc·骨架屏·计算缓存面)"
grep -q "JAVA_EXPLODED_MODE" "${S53_START}" 2>/dev/null || { bad "[53] start 脚本缺 exploded 启动分支"; S53_BAD=1; }
grep -q "maybe_train_cds_background" "${S53_START}" 2>/dev/null || { bad "[53] start 脚本缺 CDS 自训练"; S53_BAD=1; }
grep -q "boot-exploded" "${S53_PKG}" 2>/dev/null || { bad "[53] 打包脚本缺 exploded 布局"; S53_BAD=1; }
grep -q "compileall" "${S53_PKG}" 2>/dev/null || { bad "[53] 打包脚本缺 pyc 预编译"; S53_BAD=1; }
grep -q "astropy/__init__.py" "${S53_PKG}" 2>/dev/null && { bad "[53] 打包脚本引用已删除的 astropy/__init__.py"; S53_BAD=1; }
grep -q "splitChunks" "${S53_UMIRC}" 2>/dev/null || { bad "[53] .umirc 缺 splitChunks 分包"; S53_BAD=1; }
grep -q "ContextReplacementPlugin" "${S53_UMIRC}" 2>/dev/null || { bad "[53] .umirc 缺 moment locale 裁剪(须 ContextReplacement 保 zh-cn)"; S53_BAD=1; }
[ -f "${S53_DEDUPE}" ] || { bad "[53] 缺 requestDedupe.js"; S53_BAD=1; }
grep -q "dedupeEligible" "${S53_REQ}" 2>/dev/null || { bad "[53] request.js 未接去重层"; S53_BAD=1; }
grep -q "predict/dice" "${S53_DEDUPE}" 2>/dev/null || { bad "[53] 去重层缺 dice 随机排除"; S53_BAD=1; }
grep -q "horosa-boot-splash" "${S53_EJS}" 2>/dev/null || { bad "[53] document.ejs 缺启动骨架"; S53_BAD=1; }
grep -q "return request(Acg, params)" "${S53_HELPER}" 2>/dev/null || { bad "[53] getAcg 未走缓存"; S53_BAD=1; }
grep -q "return requestNoCache(Dice, params)" "${S53_HELPER}" 2>/dev/null || { bad "[53] 🔴 Dice 被缓存(随机端点缓存=功能错误)"; S53_BAD=1; }
grep -q "return requestNoCache(PlanetariumState, params)" "${S53_HELPER}" 2>/dev/null || { bad "[53] 🔴 PlanetariumState 被缓存(实时端点)"; S53_BAD=1; }
[ "${S53_BAD}" = "0" ] && ok "[53] 性能资产 全在位" || bad "[53] 性能资产 有缺失"

# ============================================================================
# [54] 择日西方深化:五档流派轴 + 默认档零回归守卫 + golden 锚 + 数据完整性
#   默认(现代主流)输出与 golden 逐字一致;modern_main extraWeights 必须为空
#   (空表 = 新增分析模块不进默认总分,评分构成与既往字节不变)。
# ============================================================================
S54_BAD=0
S54_DIR="${REPO_ROOT}/Horosa-Web/astrostudyui/src/divination"
S54_WS="${S54_DIR}/election/westernSchools.js"
S54_SNAP="${S54_DIR}/election/__tests__/__snapshots__/electionGolden.test.js.snap"
echo "[54] 择日西方深化(流派轴·golden·28宿·交映)"
[ -f "${S54_WS}" ] || { bad "[54] 缺 westernSchools.js 流派真值源"; S54_BAD=1; }
for s54k in modern_main hellenistic persian renaissance modern_revival; do
	grep -q "${s54k}: {" "${S54_WS}" 2>/dev/null || { bad "[54] 流派档缺失: ${s54k}"; S54_BAD=1; }
done
awk '/modern_main: \{/,/\},/' "${S54_WS}" 2>/dev/null | grep -q "extraWeights: {}," || { bad "[54] 🔴 modern_main extraWeights 非空(默认总分构成被改=零回归破坏)"; S54_BAD=1; }
awk '/modern_main: \{/,/\},/' "${S54_WS}" 2>/dev/null | grep -q "hsys: null" || { bad "[54] modern_main 宫制联动未保持 null(默认不得改用户宫制)"; S54_BAD=1; }
[ -f "${S54_SNAP}" ] || { bad "[54] 缺 electionGolden 快照(默认输出法律)"; S54_BAD=1; }
[ -f "${S54_DIR}/election/__tests__/electionFixture.js" ] || { bad "[54] 缺 golden 固定盘 fixture"; S54_BAD=1; }
S54_MANSIONS=$(grep -c "{ n: " "${S54_DIR}/data/lunarMansions.js" 2>/dev/null || echo 0)
[ "${S54_MANSIONS}" = "28" ] || { bad "[54] lunarMansions 应 28 条,实际 ${S54_MANSIONS}"; S54_BAD=1; }
grep -q "360 / 28" "${S54_DIR}/data/lunarMansions.js" 2>/dev/null || { bad "[54] 28 宿缺 Agrippa 均分锚"; S54_BAD=1; }
S54_EGY=$(grep -oE "\[[0-9]+, [0-9]+\]" "${S54_DIR}/data/egyptianDays.js" 2>/dev/null | wc -l | tr -d ' ')
[ "${S54_EGY}" = "12" ] || { bad "[54] 埃及凶日应 12 月×2 日,实际 ${S54_EGY} 组"; S54_BAD=1; }
grep -q "tanφ·tanδ" "${S54_DIR}/engine/paransLocal.js" 2>/dev/null || { bad "[54] paransLocal 缺公式口径注释"; S54_BAD=1; }
grep -q "riseHourAngle" "${S54_DIR}/engine/paransLocal.js" 2>/dev/null || { bad "[54] paransLocal 缺升落时角"; S54_BAD=1; }
grep -q "\['sun', 10\]" "${S54_DIR}/engine/timeLords.js" 2>/dev/null || { bad "[54] Firdaria 昼表缺日10"; S54_BAD=1; }
grep -q "capricorn: 27, aquarius: 30" "${S54_DIR}/engine/timeLords.js" 2>/dev/null || { bad "[54] ZR 小年表锚缺(摩羯27/水瓶30)"; S54_BAD=1; }
grep -q "§" "${S54_DIR}/election/electionSnapshot.js" 2>/dev/null && { bad "[54] 快照文本含 § 内部章节引用"; S54_BAD=1; }
[ "${S54_BAD}" = "0" ] && ok "[54] 择日西方深化 全在位" || bad "[54] 择日西方深化 有缺失"

# ============================================================================
# [55] 性能资产·第二轮(瘦身/启动门/恒星memo/连接池/3D动态化)
# ============================================================================
S55_BAD=0
S55_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S55_CHARTSRV="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
S55_SWE="${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/flatlib/ephem/swe.py"
S55_HTTP="${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/net/http/HttpUriRequestHystrixCommand.java"
S55_IDX="${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js"
echo "[55] 性能资产R2(瘦身排除表·启动门·恒星memo·连接池·3D动态化)"
grep -q "site-packages 重依赖排除表" "${S55_PKG}" 2>/dev/null || { bad "[55] 打包脚本缺重依赖排除表"; S55_BAD=1; }
grep -q "for heavy in streamlit pyarrow plotly altair pydeck" "${S55_PKG}" 2>/dev/null || { bad "[55] 排除表重依赖清单漂移(pandas 属 chunzi 真依赖不得入表)"; S55_BAD=1; }
grep -q "_ensure_streamlit_stub" "${REPO_ROOT}/Horosa-Web/astropy/websrv/kentang/kinastro_common.py" 2>/dev/null || { bad "[55] kinastro_common 缺 streamlit 桩(kentang adapter 在瘦身 runtime 会挂)"; S55_BAD=1; }
grep -E "name '\*\.pyc'" "${S55_PKG}" 2>/dev/null | grep -q "delete" && { bad "[55] 打包清理行又包含 *.pyc -delete(会删光预编译产物)"; S55_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astropy/tests/test_runtime_deps_slim.py" ] || { bad "[55] 缺瘦身哨兵测试"; S55_BAD=1; }
grep -q "STARTUP_GATE" "${S55_CHARTSRV}" 2>/dev/null || { bad "[55] webchartsrv 缺启动就绪门"; S55_BAD=1; }
grep -q "HOROSA_PY_WARMUP_SYNC" "${S55_CHARTSRV}" 2>/dev/null || { bad "[55] 启动门缺同步回退 kill-switch"; S55_BAD=1; }
grep -q "_fixstarUtCached" "${S55_SWE}" 2>/dev/null || { bad "[55] flatlib 缺恒星 memo"; S55_BAD=1; }
grep -q "_sidCtxKey" "${S55_SWE}" 2>/dev/null || { bad "[55] 恒星 memo 缓存键缺 sidereal 语境"; S55_BAD=1; }
grep -q "PoolingHttpClientConnectionManager" "${S55_HTTP}" 2>/dev/null || { bad "[55] Java 出站客户端缺连接池"; S55_BAD=1; }
grep -q "AstroChartMain3D = lazyPreloadable" "${S55_IDX}" 2>/dev/null || { bad "[55] 3D 星盘未动态化(回流主包)"; S55_BAD=1; }
[ "${S55_BAD}" = "0" ] && ok "[55] 性能资产R2 全在位" || bad "[55] 性能资产R2 有缺失"

# ============================================================================
# [56] 增量更新制度(部件切分/manifest v2/发布复用/客户端分支;边界三处 lockstep)
# ============================================================================
S56_BAD=0
S56_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S56_BUILD="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh"
S56_PUB="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh"
S56_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S56_LOCK="${REPO_ROOT}/Horosa_Desktop_Installer/dist/components/components-lock.json"
echo "[56] 增量更新制度(部件化 runtime)"
# 打包端:部件段结构 + 部件名单锚(改边界必须同步 SOP 文档与本哨兵)+ 内建校验 + lock 进全量 tar
grep -q "HOROSA_BUILD_COMPONENTS" "${S56_PKG}" 2>/dev/null || { bad "[56] 打包脚本缺部件切分段"; S56_BAD=1; }
for comp in "py-runtime" "jdk-runtime" "ephe-data" "xuanshi-data" "web-app" "java-lib" "java-app"; do
  grep -q "'${comp}'" "${S56_PKG}" 2>/dev/null || { bad "[56] 部件名单缺 ${comp}(边界漂移:脚本/SOP/哨兵三处须 lockstep)"; S56_BAD=1; }
done
grep -q "component split drift" "${S56_PKG}" 2>/dev/null || { bad "[56] 打包脚本缺零遗漏零重叠内建校验"; S56_BAD=1; }
grep -q "lock 同步进 stage 根" "${S56_PKG}" 2>/dev/null || { bad "[56] components-lock 未写入全量 tar(增量本地基准会缺失)"; S56_BAD=1; }
# 发布端:manifest v2 + asset 复用
grep -q "componentsLockUrl" "${S56_BUILD}" 2>/dev/null || { bad "[56] build 脚本缺 manifest v2 部件字段"; S56_BAD=1; }
grep -q "manifest_version = 2" "${S56_BUILD}" 2>/dev/null || { bad "[56] build 脚本缺 manifestVersion 2 升级"; S56_BAD=1; }
grep -q "PYCOMPREUSE" "${S56_PUB}" 2>/dev/null || { bad "[56] publish 脚本缺跨版本 asset 复用决策"; S56_BAD=1; }
# 客户端:diff/下载/应用/回退四件套 + kill-switch
for anchor in "plan_component_diff" "download_component_updates" "apply_component_updates" "HOROSA_UPDATE_FULL_ONLY" "staged_components"; do
  grep -q "${anchor}" "${S56_MAIN}" 2>/dev/null || { bad "[56] main.rs 缺增量客户端锚 ${anchor}"; S56_BAD=1; }
done
# 产物自洽(仅当本地已构建部件时;发版构建必产):lock 结构 + 部件文件在位 + sha 实测一致
if [ -f "${S56_LOCK}" ]; then
  S56_VERIFY="$(python3 - "${S56_LOCK}" 2>&1 <<'PY74'
import hashlib, json, pathlib, sys
lock_path = pathlib.Path(sys.argv[1])
lock = json.loads(lock_path.read_text())
names = sorted(c['name'] for c in lock['components'])
expect = sorted(['py-runtime', 'jdk-runtime', 'ephe-data', 'xuanshi-data', 'web-app', 'java-lib', 'java-app'])
if names != expect:
    raise SystemExit(f'部件集合漂移: {names}')
for c in lock['components']:
    f = lock_path.parent / c['file']
    if not f.is_file():
        raise SystemExit(f"部件文件缺失: {c['file']}")
    h = hashlib.sha256()
    with open(f, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    if h.hexdigest() != c['sha256']:
        raise SystemExit(f"部件 sha 不一致: {c['name']}(lock 与实物漂移,须重跑打包)")
    if c['type'] == 'tree' and not c.get('paths'):
        raise SystemExit(f"tree 部件缺 paths: {c['name']}")
    if c['type'] == 'files' and not c.get('files'):
        raise SystemExit(f"files 部件缺 files: {c['name']}")
print('OK')
PY74
)"
  if [ "${S56_VERIFY}" = "OK" ]; then
    ok "[56] 本地部件产物自洽(7 部件 sha 全核)"
  else
    bad "[56] 部件产物自检失败: ${S56_VERIFY}"; S56_BAD=1
  fi
fi
[ "${S56_BAD}" = "0" ] && ok "[56] 增量更新制度 全在位" || bad "[56] 增量更新制度 有缺失"

# ============================================================================
# [57] 法律文档与隐私声明一致性(协议说的必须就是代码做的)
# ============================================================================
S57_BAD=0
S57_LEGAL="${REPO_ROOT}/docs/legal"
S57_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
echo "[57] 法律文档随库完整 + 声明↔代码一致"
for doc in "最终用户许可协议与服务条款.md" "隐私政策.md" "安全说明.md" "网络与数据传输说明.md" "开源与第三方组件声明.md"; do
  [ -f "${S57_LEGAL}/${doc}" ] || { bad "[57] 缺法律文档 ${doc}"; S57_BAD=1; }
done
for doc in "Terms-of-Service-and-EULA.md" "Privacy-Policy.md" "Security-Statement.md" "Network-and-Data-Transmission-Statement.md" "Open-Source-and-Third-Party-Notices.md"; do
  [ -f "${S57_LEGAL}/en/${doc}" ] || { bad "[57] 缺英文法律文档 ${doc}"; S57_BAD=1; }
done
# 占位符必须清零(对外文档不得携带待填占位)
grep -rl "〔" "${S57_LEGAL}" --include='*.md' 2>/dev/null | grep -v "README.md" | while read -r f; do bad "[57] 法律文档残留占位符: ${f}"; done
[ "$(grep -rl '〔' "${S57_LEGAL}" --include='*.md' 2>/dev/null | grep -cv 'README.md')" = "0" ] || S57_BAD=1
# 关于对话框内嵌声明 + 官方链接接线
grep -q "aboutLegal" "${S57_UI}/components/homepage/PageHeader.js" 2>/dev/null || { bad "[57] 关于对话框缺法律声明区块"; S57_BAD=1; }
grep -q "HOROSA_OFFICIAL_REPO" "${S57_UI}/components/homepage/PageHeader.js" 2>/dev/null || { bad "[57] 关于对话框缺官方渠道链接常量"; S57_BAD=1; }
# 隐私声明↔代码一致性执行锚:
#   ① 在线地图须有一次性同意闸(隐私政策 5.3 的事实基础)
grep -q "hasMapConsent" "${S57_UI}/components/amap/MapV2.js" 2>/dev/null || { bad "[57] MapV2 缺地图加载同意闸(隐私政策 5.3 将失实)"; S57_BAD=1; }
#   ② 历史 3D 模型远端域名不得回流(网络说明「不连历史域名」的执行锚)
grep -rq "chart3d\.horosa\.com" "${S57_UI}" 2>/dev/null && { bad "[57] 前端出现 chart3d 历史域名回流(网络说明将失实)"; S57_BAD=1; }
[ "${S57_BAD}" = "0" ] && ok "[57] 法律文档与一致性 全在位" || bad "[57] 法律文档与一致性 有缺失"

# ============================================================================
# [61] 风水 十三派:理气六派(八宅/玄空/三合/金锁/乾坤/紫白)+ 水法(辅星/净阴净阳)+ 玄空大卦 + 形势 + 择日
#      纯计算引擎 + 流派选择器 UI + 户型图两法(纳气盘/八卦阳宅)画布引擎零回归
# ============================================================================
S61_BAD=0
S61_FS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/fengshui"
echo "[61] 风水 十三派 引擎+流派UI+玄空进阶(替卦/城门/打劫)+深化(黄泉/拨砂/线法/九水位/门主灶/日时紫白)+新派+户型图两法零回归"
for f in fengshuiData.js liqiCore.js xuankong.js sanhe.js zibai.js qiankun.js bazhai.js jinsuo.js LiqiWorkspace.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水理气 ${f}"; S61_BAD=1; }
done
# 新增五派引擎(辅星/净阴净阳/玄空大卦/形势/择日)
for f in fuxing.js jingyin.js dagua.js xingshi.js zeri.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水新派 ${f}"; S61_BAD=1; }
done
for f in charts/LuoshuGrid.js charts/TwentyFourShanRing.js charts/EightPalaceDisk.js charts/SixtyFourGuaRing.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水盘面 ${f}"; S61_BAD=1; }
done
# 六派深化 + 新派核心纯函数(仅核对导出符号在位)
grep -qE "export function sanheXiangFaAll" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺三合十二向 sanheXiangFaAll"; S61_BAD=1; }
grep -qE "export function boshaWuGe" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺拨砂五格 boshaWuGe"; S61_BAD=1; }
grep -qE "export function huangquanBaYao" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺黄泉八煞 huangquanBaYao"; S61_BAD=1; }
grep -qE "export function (chuanshanAt|toudiAt|fenjinAt)" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺线法穿山透地分金"; S61_BAD=1; }
grep -qE "export function qkgbFullPositions" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺乾坤九水位 qkgbFullPositions"; S61_BAD=1; }
grep -qE "export function jianXiangByDeg" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺玄空兼向度数判别 jianXiangByDeg"; S61_BAD=1; }
grep -qE "export function gua64Of" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺玄空大卦识卦 gua64Of"; S61_BAD=1; }
grep -qE "export function guaRelation" "${S61_FS}/bazhai.js" 2>/dev/null || { bad "[61] 缺八宅门主灶 guaRelation"; S61_BAD=1; }
grep -qE "export function dayCenter" "${S61_FS}/zibai.js" 2>/dev/null || { bad "[61] 缺日紫白 dayCenter"; S61_BAD=1; }
grep -qE "export function yearGods" "${S61_FS}/zeri.js" 2>/dev/null || { bad "[61] 缺择日年神 yearGods"; S61_BAD=1; }
# 数据底座(纳甲/纳音/64卦/黄泉/三煞)
grep -qE "NAJIA_GUA|NAYIN_60|GUA64_TABLE|BA_YAO_SHA|SANSHA_BY_JU" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 缺数据底座(纳甲/纳音/64卦/黄泉/三煞)"; S61_BAD=1; }
# 玄空进阶:替卦/替星/城门/七星打劫
grep -qE "export function flyChartTi" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺替卦 flyChartTi"; S61_BAD=1; }
grep -qE "export function tixingOf" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺替星 tixingOf"; S61_BAD=1; }
grep -qE "TIXING_VARIANTS" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 缺替星3方案"; S61_BAD=1; }
grep -qE "function cityGate" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] 缺城门诀 cityGate"; S61_BAD=1; }
grep -qE "function sevenStarRob" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] 缺七星打劫 sevenStarRob"; S61_BAD=1; }
# 下卦默认零回归:替卦必须 opt-in(默认走 flyChart 非 flyChartTi)
grep -qE "jian \? flyChartTi" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] xuankong 替卦未 opt-in(下卦零回归风险)"; S61_BAD=1; }
# FengShuiMain:流派选择器 + 户型图两法画布引擎保活(理气派 display:none 零回归)
grep -qE "import FengShuiEngine" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain 丢画布引擎(户型图两法回归)"; S61_BAD=1; }
grep -qE "LIQI_SET|SCHOOL_GROUPS" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain 缺流派选择器"; S61_BAD=1; }
grep -qE "canvas-body" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain 缺 canvas 保活(零回归)"; S61_BAD=1; }
# onVm 守:理气/新派激活时画布引擎 vm 不得覆盖当前流派快照(否则 AI 导出取到纳气盘)
grep -qE "snapshotText && !LIQI_SET.has" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain onVm 缺理气快照防覆盖守(AI导出会取错派)"; S61_BAD=1; }
# 测试在位(下卦 byte 守 + 深化/新派锚 + 压测)
for t in liqiCore.test.js xuankong.test.js schools.test.js xuankongAdvanced.test.js charts.test.js fengshuiOptionMatrix.test.js fengshuiQaRound2.test.js fengshuiManualAnchor.test.js \
         sanheAugment.test.js qiankunAugment.test.js bazhaiAugment.test.js xuankongAugment.test.js zibaiAugment.test.js newSchools.test.js fengshuiStress.test.js; do
  [ -f "${S61_FS}/__tests__/${t}" ] || { bad "[61] 缺风水测试 ${t}"; S61_BAD=1; }
done
# nav 可发现十三派(理气六派 + 新派关键词)
grep -qE "key: 'fengshui'.*金锁玉关.*乾坤国宝" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js" 2>/dev/null || { bad "[61] nav 缺理气六派关键词"; S61_BAD=1; }
grep -qE "key: 'fengshui'.*玄空大卦.*形势.*择日" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js" 2>/dev/null || { bad "[61] nav 缺新派关键词(大卦/形势/择日)"; S61_BAD=1; }
[ "${S61_BAD}" = "0" ] && ok "[61] 风水 十三派 引擎+玄空进阶(替卦/城门/打劫)+深化(黄泉/拨砂/线法/九水位/门主灶/日时紫白)+新派(辅星/净阴净阳/大卦/形势/择日)+盘面+测试+户型图两法零回归 在位" || bad "[61] 风水 有缺失"


# 79. 打包产物全路由冒烟已跑且绿(哈希绑定,防拿旧包结果充数)
echo "[79] 全路由真实冒烟 stamp(哈希绑定)"
S79_STAMP="${INSTALLER_ROOT}/build/runtime-smoke/last_smoke.json"
S79_ASSET="$(python3 -c "import json;print(json.load(open('${INSTALLER_ROOT}/config/release_config.json')).get('runtimeAssetName','horosa-runtime-macos-arm64.tar.gz'))" 2>/dev/null || echo horosa-runtime-macos-arm64.tar.gz)"
S79_ARCHIVE="${INSTALLER_ROOT}/dist/${S79_ASSET}"
if [ ! -f "${S79_ARCHIVE}" ]; then
  warn "[79] dist 无运行时归档(${S79_ASSET}),冒烟 stamp 校验跳过(构建后会强制)"
elif [ ! -f "${S79_STAMP}" ]; then
  bad "[79] 缺 build/runtime-smoke/last_smoke.json —— 先跑 scripts/verify_runtime_smoke.sh"
else
  S79_RES="$(python3 - "$S79_STAMP" "$S79_ARCHIVE" <<'PY'
import hashlib, json, sys
stamp = json.load(open(sys.argv[1], encoding="utf-8"))
sha = hashlib.sha256(open(sys.argv[2], "rb").read()).hexdigest()
if not stamp.get("pass"):
    print("stamp=FAIL")
elif stamp.get("runtimeSha256") != sha:
    print("sha-mismatch stamp=%s dist=%s" % (str(stamp.get("runtimeSha256"))[:16], sha[:16]))
else:
    print("ok")
PY
)"
  if [ "${S79_RES}" = "ok" ]; then
    ok "[79] 冒烟 stamp PASS 且 sha 与 dist 归档一致"
  else
    bad "[79] 冒烟 stamp 无效(${S79_RES}):对当前归档重跑 verify_runtime_smoke.sh"
  fi
fi
grep -q "runtime-smoke" "${INSTALLER_ROOT}/SELFCHECK_LOG.md" 2>/dev/null \
  && ok "[79] SELFCHECK_LOG 有冒烟留档行" \
  || warn "[79] SELFCHECK_LOG 尚无冒烟留档(首次构建后自动追加)"

# 80. 路由挂载 ↔ 冒烟探针清单 漂移=0(挂载无探针/探针无挂载 皆 FAIL)
echo "[80] 路由挂载↔探针清单漂移"
if python3 "${INSTALLER_ROOT}/scripts/check_route_probe_drift.py" >/dev/null 2>&1; then
  ok "[80] 挂载↔探针 双向一致(含 kinastro importer 覆盖名单)"
else
  python3 "${INSTALLER_ROOT}/scripts/check_route_probe_drift.py" 2>&1 | sed 's/^/    /' >&2 || true
  bad "[80] 挂载↔探针漂移:新增技法漏配探针或僵尸探针(详见上)"
fi

# 81. 太乙静默404三层守卫在位(2026-07-04 事故复盘;grep 特征串,不用文件存在性)
echo "[81] 太乙静默404三层守卫"
S81_BAD=0
S81_PY="${REPO_ROOT}/Horosa-Web/astropy"
grep -q "stub_dunder_guard_v1" "${S81_PY}/websrv/kentang/kinastro_common.py" 2>/dev/null || { bad "[81] 桩 dunder 守卫(stub_dunder_guard_v1)缺位"; S81_BAD=1; }
grep -q 'raise AttributeError(_name)' "${S81_PY}/websrv/kentang/kinastro_common.py" 2>/dev/null || { bad "[81] 桩 dunder 拒答语句缺位"; S81_BAD=1; }
[ "$(grep -c "__horosa_slim_stub__ = True" "${S81_PY}/websrv/kentang/kinastro_common.py" 2>/dev/null)" -ge 3 ] || { bad "[81] 子桩哨兵标记不足三处(顶桩+components+v1)"; S81_BAD=1; }
grep -q "class KentangServiceLoadError" "${S81_PY}/websrv/kentang/registry.py" 2>/dev/null || { bad "[81] registry 缺 KentangServiceLoadError 响亮失败类型"; S81_BAD=1; }
grep -q "KENTANG_LAZY_MOUNT_SELF_HEAL" "${S81_PY}/websrv/kentang/registry.py" 2>/dev/null || { bad "[81] registry 缺 sys.modules 自愈净化守卫"; S81_BAD=1; }
grep -q "_warm_real_astropy" "${S81_PY}/websrv/webchartsrv.py" 2>/dev/null || { bad "[81] webchartsrv 缺真 astropy 预热(顺序免疫层)"; S81_BAD=1; }
grep -q "stub_first" "${S81_PY}/tests/test_kentang_import_order.py" 2>/dev/null || { bad "[81] 双向导入门测试缺位/缺 stub_first 方向"; S81_BAD=1; }
[ "${S81_BAD}" = "0" ] && ok "[81] 三层守卫+双向导入门 全在位"

# 83. 更新链下载/解压核(WS-1b/1c):续传协议+原生流式解压+kill-switch+回归测试+Range 发布哨兵
echo "[83] 断点续传下载核+原生流式解压"
S83_BAD=0
S83_MAIN="${INSTALLER_ROOT}/src-tauri/src/main.rs"
grep -q "fn download_resumable_once" "${S83_MAIN}" 2>/dev/null || { bad "[83] 下载核 download_resumable_once 缺位"; S83_BAD=1; }
grep -q "HOROSA_DOWNLOAD_NO_RESUME" "${S83_MAIN}" 2>/dev/null || { bad "[83] kill-switch HOROSA_DOWNLOAD_NO_RESUME 缺位"; S83_BAD=1; }
grep -q "RESUME_MAX_ATTEMPTS" "${S83_MAIN}" 2>/dev/null || { bad "[83] 续传次数封顶 RESUME_MAX_ATTEMPTS 缺位"; S83_BAD=1; }
grep -q '\.part\.meta' "${S83_MAIN}" 2>/dev/null || { bad "[83] .part.meta 续传元数据协议缺位"; S83_BAD=1; }
grep -q "resume_completes_via_range_206" "${S83_MAIN}" 2>/dev/null || { bad "[83] 续传 206 回归测试缺位"; S83_BAD=1; }
grep -q 'r 0-1023' "${INSTALLER_ROOT}/scripts/verify_github_release_end_to_end.sh" 2>/dev/null || { bad "[83] e2e 缺 GitHub Range(206)发布实测哨兵"; S83_BAD=1; }
grep -q "fn extract_tar_gz_native_with" "${S83_MAIN}" 2>/dev/null || { bad "[83] 原生流式解压 extract_tar_gz_native_with 缺位"; S83_BAD=1; }
grep -q "HOROSA_EXTRACT_NATIVE" "${S83_MAIN}" 2>/dev/null || { bad "[83] kill-switch HOROSA_EXTRACT_NATIVE 缺位"; S83_BAD=1; }
grep -q "HOROSA_EXTRACT_CONCURRENCY" "${S83_MAIN}" 2>/dev/null || { bad "[83] 物化并发开关 HOROSA_EXTRACT_CONCURRENCY 缺位"; S83_BAD=1; }
grep -q "native_extract_parity_with_external_tar" "${S83_MAIN}" 2>/dev/null || { bad "[83] 解压 parity 回归测试缺位"; S83_BAD=1; }
grep -q "native_extract_rejects_path_escape" "${S83_MAIN}" 2>/dev/null || { bad "[83] 解压路径逃逸防护测试缺位"; S83_BAD=1; }
grep -q "tar_extract_external" "${S83_MAIN}" 2>/dev/null || { bad "[83] 外部 tar 回退路径缺位(native 出错须可退)"; S83_BAD=1; }
[ "${S83_BAD}" = "0" ] && ok "[83] 下载核+解压核 协议/开关/测试/发布哨兵 全在位"

echo "[84] 更新验证基建(事件镜像+假release隔离)"
# (manifest 分离签名机制已整体移除;本节保留事件镜像与假 release 入口隔离锚,
#  并以反向锚确保签名代码不以「半拆」状态残留。)
S84_BAD=0
S84_MAIN="${INSTALLER_ROOT}/src-tauri/src/main.rs"
grep -q "fn log_updater_event" "${S84_MAIN}" 2>/dev/null || { bad "[84] updater 事件镜像 log_updater_event 缺位(用户更新出问题拿不到证据)"; S84_BAD=1; }
grep -q "updater-events.log" "${S84_MAIN}" 2>/dev/null || { bad "[84] 事件镜像日志文件锚缺位"; S84_BAD=1; }
grep -q 'feature = "update-url-override"' "${S84_MAIN}" 2>/dev/null || { bad "[84] URL override 未按 feature 隔离"; S84_BAD=1; }
if grep -q "update-url-override" "${INSTALLER_ROOT}/scripts/build_desktop_release.sh" 2>/dev/null; then
  bad "[84] 发布构建脚本出现 update-url-override(假 release 入口绝不可进发布二进制)"; S84_BAD=1
fi
grep -q "manifest_fetch_three_outcomes" "${S84_MAIN}" 2>/dev/null || { bad "[84] manifest 获取三态回归测试缺位"; S84_BAD=1; }
# 反向锚:签名制度已取消,残留即「半拆」状态(比有或无都危险)
for zombie in "UPDATE_MANIFEST_PUBKEY_HEX" "verify_manifest_signature" "HOROSA_UPDATE_REQUIRE_SIG" "ed25519"; do
  if grep -qi "${zombie}" "${S84_MAIN}" 2>/dev/null; then
    bad "[84] 签名制度已取消但 main.rs 残留 ${zombie}(半拆状态,拆干净或整体恢复)"; S84_BAD=1
  fi
done
grep -q "horosa-update-manifest-sign" "${INSTALLER_ROOT}/scripts/build_desktop_release.sh" 2>/dev/null && { bad "[84] build 脚本残留签名段(制度已取消)"; S84_BAD=1; }
[ "${S84_BAD}" = "0" ] && ok "[84] 事件镜像+假release隔离 全在位(签名制度已取消且拆净)"

# 85. 启动健康看门狗(WS-1d,A/B 自愈):状态机/回滚/ready 确认/回归测试全在位
echo "[85] 启动健康看门狗"
S85_BAD=0
grep -q "WATCHDOG_ROLLBACK_THRESHOLD" "${S84_MAIN}" 2>/dev/null || { bad "[85] 看门狗阈值缺位"; S85_BAD=1; }
grep -q "fn rollback_runtime_to_previous" "${S84_MAIN}" 2>/dev/null || { bad "[85] previous 槽回滚函数缺位"; S85_BAD=1; }
grep -q "launch_health_confirm" "${S84_MAIN}" 2>/dev/null || { bad "[85] ready 确认(pending 归零)缺位"; S85_BAD=1; }
grep -q "cleanup_previous_slots" "${S84_MAIN}" 2>/dev/null || { bad "[85] previous 槽 ready 后回收缺位"; S85_BAD=1; }
grep -q "watchdog_health_state_machine_and_rollback" "${S84_MAIN}" 2>/dev/null || { bad "[85] 看门狗回归测试缺位"; S85_BAD=1; }
[ "${S85_BAD}" = "0" ] && ok "[85] 看门狗 状态机/回滚/确认/测试 全在位"

# 86. 增量八不变量(WS-1e):I3 三方 sha/I5 全量回退字段/I7 尺寸真值/I8 kill-switch 矩阵
#     (I1 合成校验+I2 边界 lockstep+I6 lock 进 tar 由[74]强制;I4 差分门在 publish 内)
echo "[86] 增量八不变量(I3/I5/I7/I8)"
S86_BAD=0
S86_MAIN="${INSTALLER_ROOT}/src-tauri/src/main.rs"
# I8:四个 kill-switch + I4 门锚静态在位
for anchor in "HOROSA_UPDATE_FULL_ONLY" "HOROSA_DOWNLOAD_NO_RESUME" "HOROSA_EXTRACT_NATIVE" "HOROSA_MENU_UPDATE_LEGACY"; do
  grep -q "${anchor}" "${S86_MAIN}" 2>/dev/null || { bad "[86·I8] kill-switch ${anchor} 缺位"; S86_BAD=1; }
done
grep -q "HOROSA_ALLOW_LARGE_DELTA" "${INSTALLER_ROOT}/scripts/publish_github_release.sh" 2>/dev/null || { bad "[86·I4] publish 缺差分效率门"; S86_BAD=1; }
grep -q "HOROSA_DELTA_BUDGET_MB" "${INSTALLER_ROOT}/scripts/publish_github_release.sh" 2>/dev/null || { bad "[86·I4] 差分门缺预算参数"; S86_BAD=1; }
# I3/I5/I7:dist manifest 已产时做真值核对(manifest↔lock 逐名 sha / v1 全字段 / 尺寸↔实物)
S86_MANIFEST="${INSTALLER_ROOT}/dist/horosa-latest.json"
if [ -f "${S86_MANIFEST}" ]; then
  S86_RES="$(python3 - "${S86_MANIFEST}" "${INSTALLER_ROOT}/dist" <<'PY86'
import json, pathlib, sys
manifest = json.loads(pathlib.Path(sys.argv[1]).read_text())
dist = pathlib.Path(sys.argv[2])
problems = []
for key, entry in (manifest.get('platforms') or {}).items():
    # I5:v2 必含 v1 全量回退字段(老壳/降级路径的生命线)
    for field in ('appUrl', 'appSha256', 'runtimeUrl', 'runtimeSha256', 'runtimeVersion'):
        if not entry.get(field):
            problems.append(f"I5:{key} 缺 {field}")
    # I7:尺寸字段完备且与 dist 实物一致(检查更新「要下多大」的真值)
    for field, fname in (
        ('appSizeBytes', entry.get('appUrl', '').rsplit('/', 1)[-1]),
        ('runtimeSizeBytes', entry.get('runtimeUrl', '').rsplit('/', 1)[-1]),
    ):
        declared = entry.get(field)
        if declared is None:
            problems.append(f"I7:{key} 缺 {field}")
            continue
        f = dist / fname
        if f.is_file() and f.stat().st_size != declared:
            problems.append(f"I7:{key} {field}={declared} 与实物 {f.stat().st_size} 不一致({fname})")
    # I3:manifest.components ↔ lock ↔ 实物 逐名 sha 三方核对
    comps = entry.get('components') or []
    if comps:
        lock_path = dist / 'components' / 'components-lock.json'
        if not lock_path.is_file():
            problems.append('I3:dist/components/components-lock.json 缺失')
        else:
            lock = json.loads(lock_path.read_text())
            lock_sha = {c['name']: c['sha256'] for c in lock.get('components') or []}
            man_sha = {c['name']: c['sha256'] for c in comps}
            if set(lock_sha) != set(man_sha):
                problems.append(f"I3:{key} manifest/lock 部件集合漂移")
            for name in set(lock_sha) & set(man_sha):
                if lock_sha[name] != man_sha[name]:
                    problems.append(f"I3:{key} 部件 {name} manifest/lock sha 漂移")
print('; '.join(problems) if problems else 'OK')
PY86
)"
  if [ "${S86_RES}" = "OK" ]; then
    ok "[86] dist manifest I3/I5/I7 真值核对通过"
  else
    bad "[86] 不变量违约: ${S86_RES}"; S86_BAD=1
  fi
else
  warn "[86] dist 未打包,跳过 I3/I5/I7 真值核对(I4/I8 静态锚已核)"
fi
[ "${S86_BAD}" = "0" ] && ok "[86] 增量八不变量 全在位"

# 87. kentang 懒挂载(WS-3d):代理/开关/预热/失败响亮/回归测试全在位
echo "[87] kentang 懒挂载"
S87_BAD=0
S87_REG="${REPO_ROOT}/Horosa-Web/astropy/websrv/kentang/registry.py"
grep -q "class _LazyMountedService" "${S87_REG}" 2>/dev/null || { bad "[87] 懒挂载代理缺位"; S87_BAD=1; }
grep -q "HOROSA_KENTANG_LAZY" "${S87_REG}" 2>/dev/null || { bad "[87] kill-switch HOROSA_KENTANG_LAZY 缺位"; S87_BAD=1; }
grep -q "def prewarm_kentang_services" "${S87_REG}" 2>/dev/null || { bad "[87] 空闲预热入口缺位(首点兜底)"; S87_BAD=1; }
grep -q "prewarm_kentang_services" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" 2>/dev/null || { bad "[87] webchartsrv 未接预热(懒挂载首点无人兜)"; S87_BAD=1; }
grep -q "test_lazy_proxy_load_failure_is_loud_not_404" "${REPO_ROOT}/Horosa-Web/astropy/tests/test_kentang_lazy_mount.py" 2>/dev/null || { bad "[87] 失败响亮(非404)回归测试缺位"; S87_BAD=1; }
[ "${S87_BAD}" = "0" ] && ok "[87] 懒挂载 代理/开关/预热/测试 全在位"

# 88. AppCDS 链(WS-3e):base 再生+预训练+增量豁免 全在位;payload 已产则验实物
echo "[88] AppCDS base+预置链"
S88_BAD=0
S88_PKG="${INSTALLER_ROOT}/scripts/package_runtime_payload.sh"
grep -q "Xshare:dump" "${S88_PKG}" 2>/dev/null || { bad "[88] 打包缺 base CDS 再生(jlink 不产 classes.jsa=自训链静默死)"; S88_BAD=1; }
grep -q "HOROSA_SKIP_CDS_PRESEED" "${S88_PKG}" 2>/dev/null || { bad "[88] 打包缺 CDS 预训练段"; S88_BAD=1; }
grep -q "app-cds.jsa'" "${S88_PKG}" 2>/dev/null || grep -q "app-cds.jsa" "${S88_PKG}" 2>/dev/null || { bad "[88] 打包缺 .jsa 部件豁免"; S88_BAD=1; }
S88_STAGE="${INSTALLER_ROOT}/build/runtime-payload"
if [ -d "${S88_STAGE}" ]; then
  S88_BASE="${S88_STAGE}/runtime/mac/java/lib/server/classes.jsa"
  S88_SEED="${S88_STAGE}/runtime/mac/bundle/boot-exploded/.app-cds.jsa"
  if [ -s "${S88_BASE}" ]; then
    ok "[88] stage base classes.jsa 在位($(du -h "${S88_BASE}" | cut -f1))"
  else
    bad "[88] stage 缺 base classes.jsa(用户端动态 dump 必败)"; S88_BAD=1
  fi
  if [ -s "${S88_SEED}" ] && [ "$(stat -f%z "${S88_SEED}")" -gt 20000000 ]; then
    ok "[88] stage 预置 .app-cds.jsa 在位($(du -h "${S88_SEED}" | cut -f1))"
  else
    warn "[88] stage 无预置 .jsa(>20MB)——首启走自训兜底(非阻断,但失去首启即 CDS)"
  fi
else
  warn "[88] payload stage 未构建,跳过实物核(代码面锚已核)"
fi
[ "${S88_BAD}" = "0" ] && ok "[88] AppCDS 链 全在位"

# 89. 瞬时化性能资产(WS-3b/3c/3f):账本段名/缓存 flag/自热身/空闲预热/预算测试 全在位
echo "[89] 瞬时化性能资产"
S89_BAD=0
S89_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
grep -q "techniqueCacheEnabled" "${S89_UI}/utils/requestDedupe.js" 2>/dev/null || { bad "[89] L2 技法缓存缺位"; S89_BAD=1; }
grep -q "horosa.perf.techniqueCache" "${S89_UI}/utils/perfFlags.js" 2>/dev/null || { bad "[89] techniqueCache perfFlag 缺位"; S89_BAD=1; }
grep -q "startIdleWarmQueue" "${S89_UI}/utils/idleWarmQueue.js" 2>/dev/null || { bad "[89] 空闲预热队列缺位"; S89_BAD=1; }
grep -q "startIdleWarmQueue" "${S89_UI}/pages/index.js" 2>/dev/null || { bad "[89] 空闲预热未接线 pages/index"; S89_BAD=1; }
grep -q "order: opts.order" "${S89_UI}/pages/index.js" 2>/dev/null || { bad "[89] 预载概率序缺位"; S89_BAD=1; }
grep -q "preloadNavByLabel" "${S89_UI}/pages/index.js" 2>/dev/null || { bad "[89] 悬停预取缺位"; S89_BAD=1; }
grep -q "selfWarmupAsync" "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/java/spacex/astrostudyboot/StartupLedgerListener.java" 2>/dev/null || { bad "[89] Java 自热身缺位"; S89_BAD=1; }
[ -f "${S89_UI}/utils/__tests__/techniquePerfBudget.test.js" ] || { bad "[89] 性能预算测试缺位"; S89_BAD=1; }
for seg in "rust.bootstrap_begin" "rust.emit_ready"; do
  grep -q "${seg}" "${INSTALLER_ROOT}/src-tauri/src/main.rs" 2>/dev/null || { bad "[89] 账本段 ${seg} 缺位"; S89_BAD=1; }
done
grep -q "py.warmup_kentang" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" 2>/dev/null || { bad "[89] 账本段 py.warmup_kentang 缺位"; S89_BAD=1; }
[ "${S89_BAD}" = "0" ] && ok "[89] 瞬时化资产 全在位"

# 92. runtime 自包含:pip editable/direct_url 工件内嵌构建机绝对路径,随 runtime tar 发出
#     即不自包含(import 链依赖 PYTHONPATH 先于 meta_path 末位 finder 才不炸)。四面锚:
#     staging 零残留 + .pth 零绝对路径 + 打包脚本 fail-closed 净化在位 + flatlib 导入源随包;
#     dist 已有 runtime/py-runtime tar 时清单亦须零残留(扫过且 tar 未变则记号免重扫)。
echo "[92] runtime 自包含(editable/direct_url 零残留)"
S92_BAD=0
S92_SP="${REPO_ROOT}/runtime/mac/python/lib/python3.12/site-packages"
if [ -d "${S92_SP}" ]; then
  S92_N="$(find "${S92_SP}" \( -name 'direct_url.json' -o -name '__editable__*' \) 2>/dev/null | wc -l | tr -d ' ' || true)"
  [ "${S92_N}" = "0" ] || { bad "[92] staging site-packages 残留 editable/direct_url ${S92_N} 个"; S92_BAD=1; }
  S92_P="$(grep -l '/Users/' "${S92_SP}"/*.pth 2>/dev/null | wc -l | tr -d ' ' || true)"
  [ "${S92_P}" = "0" ] || { bad "[92] staging .pth 含构建机绝对路径 ${S92_P} 个"; S92_BAD=1; }
else
  warn "[92] runtime staging 不在本机,跳过实物核(脚本面锚照核)"
fi
grep -q "自包含净化" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh" || { bad "[92] 打包脚本缺自包含净化守卫"; S92_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/flatlib-ctrad2/flatlib/__init__.py" ] || { bad "[92] flatlib 导入源(flatlib-ctrad2)缺失"; S92_BAD=1; }
for S92_T in "${REPO_ROOT}/Horosa_Desktop_Installer/dist/horosa-runtime-macos-arm64.tar.gz" \
             "${REPO_ROOT}/Horosa_Desktop_Installer/dist/components/horosa-comp-py-runtime-macos-arm64.tar.gz"; do
  [ -f "${S92_T}" ] || continue
  S92_MARK="${S92_T}.selfcontain-ok"
  if [ -f "${S92_MARK}" ] && [ "${S92_MARK}" -nt "${S92_T}" ]; then
    continue
  fi
  S92_TN="$(tar -tzf "${S92_T}" 2>/dev/null | grep -c -E '__editable__|direct_url\.json' || true)"
  if [ "${S92_TN}" = "0" ]; then
    touch "${S92_MARK}" 2>/dev/null || true
  else
    bad "[92] $(basename "${S92_T}") 清单含 editable/direct_url 残留 ${S92_TN} 条(守卫前的旧产物,须重打)"; S92_BAD=1
  fi
done
[ "${S92_BAD}" = "0" ] && ok "[92] runtime 自包含 全绿"

# 93. WebView 兼容(macOS 12.0-12.2 = Safari 15.0-15.3):ES2022 微填充 + :has() 类回退。
#     :has 仅 Safari 15.4+ 支持;app.less 每条 :has 规则须有同义 class 回退(由
#     legacyWebkitCompat 在旧引擎维护回退类)。:has 用点收敛于 app.less 且数量钉死——
#     新增 :has 必须同步配回退并更新本哨兵计数。
echo "[93] WebView 兼容(polyfill + :has 类回退)"
S93_BAD=0
S93_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S93_COMPAT="${S93_UI}/src/utils/legacyWebkitCompat.js"
{ [ -f "${S93_COMPAT}" ] && grep -q "selector(:has(\*))" "${S93_COMPAT}"; } || { bad "[93] legacyWebkitCompat 缺失或缺 :has 探测"; S93_BAD=1; }
grep -q "legacyWebkitCompat" "${S93_UI}/src/global.js" || { bad "[93] global.js 未接线兼容层(必须最先执行)"; S93_BAD=1; }
S93_LESS="${S93_UI}/src/layouts/app.less"
S93_HAS_N="$(grep -o ':has(' "${S93_LESS}" 2>/dev/null | wc -l | tr -d ' ' || true)"
[ "${S93_HAS_N}" = "1" ] || { bad "[93] app.less :has( 数=${S93_HAS_N}(钉死 1);新增须配同义 class 回退并更新本哨兵"; S93_BAD=1; }
grep -q "horosa-main-tab-hidden-parent" "${S93_LESS}" || { bad "[93] app.less 缺 tab 隐藏回退类规则"; S93_BAD=1; }
S93_OTHER="$(grep -rl ':has(' "${S93_UI}/src" --include='*.less' --include='*.css' 2>/dev/null | grep -v 'layouts/app.less' | wc -l | tr -d ' ' || true)"
[ "${S93_OTHER}" = "0" ] || { bad "[93] app.less 之外出现 :has 用点(${S93_OTHER} 文件)——须走回退配套或收敛"; S93_BAD=1; }
[ -f "${S93_UI}/src/utils/__tests__/legacyWebkitCompat.test.js" ] || { bad "[93] 缺兼容层回归测试"; S93_BAD=1; }
if [ -d "${S93_UI}/dist-file" ]; then
  grep -rq "horosa-main-tab-hidden-parent" "${S93_UI}/dist-file" 2>/dev/null || { bad "[93] dist-file 缺 tab 回退类(前端未重建)"; S93_BAD=1; }
  grep -rq "selector(:has(" "${S93_UI}/dist-file" 2>/dev/null || { bad "[93] dist-file 缺兼容层产物(前端未重建)"; S93_BAD=1; }
fi
[ "${S93_BAD}" = "0" ] && ok "[93] WebView 兼容 全在位"

# 94. 会话自愈与停服安全(运行期可靠性):
#     ① 服务存活看门狗(启动看门狗管「起不来」,这管「跑着跑着死了」)+ 限频自动重启
#        + 菜单「重启本地服务」人工兜底;
#     ② 停服链跨实例安全:pid 文件端口后缀(双实例互覆→误杀/漏杀)+ 杀前进程指纹校验
#        (pid 复用防误杀无辜)+ stop_runtime 传真实端口(否则动态口会话停不干净)。
echo "[94] 会话自愈与停服安全"
S94_BAD=0
S94_RS="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
grep -q "fn start_service_supervisor" "${S94_RS}" || { bad "[94] 缺服务存活看门狗"; S94_BAD=1; }
grep -q "fn restart_local_services" "${S94_RS}" || { bad "[94] 缺服务重启例程"; S94_BAD=1; }
grep -q "MENU_RESTART_SERVICES" "${S94_RS}" || { bad "[94] 缺「重启本地服务」菜单"; S94_BAD=1; }
grep -q "struct BootstrapBusyGuard" "${S94_RS}" || { bad "[94] 缺引导互斥守卫(看门狗会与更新/修复抢跑)"; S94_BAD=1; }
grep -q "fn stop_runtime(paths: &RuntimePaths, ports: Option<(u16, u16)>)" "${S94_RS}" || { bad "[94] stop_runtime 缺端口参数"; S94_BAD=1; }
grep -q "指纹不符的进程绝不能被停服脚本误杀" "${S94_RS}" || { bad "[94] 缺停服误杀回归测试"; S94_BAD=1; }
S94_STOP="${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh"
grep -q '\.horosa_py\.\${CHART_PORT}\.pid' "${S94_STOP}" || { bad "[94] stop 脚本 pid 文件缺端口后缀"; S94_BAD=1; }
grep -q 'expected_pattern' "${S94_STOP}" || { bad "[94] stop 脚本缺杀前指纹校验"; S94_BAD=1; }
grep -q '\.horosa_py\.\${CHART_PORT}\.pid' "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" || { bad "[94] start 脚本 pid 文件缺端口后缀"; S94_BAD=1; }
[ "${S94_BAD}" = "0" ] && ok "[94] 会话自愈与停服安全 全在位"

# 95. 确定性运行环境(不因系统设置/其它软件/长期运行而变):JVM locale 钉死(泰语系统
#     默认佛历=年+543)/桌面 Redis 禁用(不触碰用户自装 :6379)/本地文档缓存每用户
#     (共享无锁 JSON 会互踩)/日志保留策略(防写满盘)/安装器拒绝文案双语。
echo "[95] 确定性运行环境"
S95_BAD=0
S95_SH="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
grep -q '\-Duser\.language=zh' "${S95_SH}" || { bad "[95] java 启动缺 locale 钉死"; S95_BAD=1; }
grep -q 'paramhash\.cache\.redis\.enable=false' "${S95_SH}" || { bad "[95] 桌面 redis 未禁用"; S95_BAD=1; }
grep -q '\${HOME}/\.horosa-cache/mongo-fallback' "${S95_SH}" || { bad "[95] 文档缓存默认未每用户化"; S95_BAD=1; }
grep -q 'HOROSA_MONGO_FALLBACK_DIR' "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs" || { bad "[95] 壳未传每用户缓存目录"; S95_BAD=1; }
grep -q 'fn prune_logs_dir_best_effort' "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs" || { bad "[95] 壳缺日志修剪"; S95_BAD=1; }
S95_LOG="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/src/main/resources/log4j2.xml"
grep -q '<Delete basePath' "${S95_LOG}" || { bad "[95] log4j2 缺 Delete 保留策略"; S95_BAD=1; }
grep -q 'SizeBasedTriggeringPolicy' "${S95_LOG}" || { bad "[95] log4j2 缺按量滚转"; S95_BAD=1; }
grep -q 'Apple Silicon Required' "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/distribution.xml.template" || { bad "[95] 安装器拒绝文案缺英文"; S95_BAD=1; }
grep -q 'pkgutil --forget' "${REPO_ROOT}/Horosa_Desktop_Installer/UNINSTALL.md" || { bad "[95] 卸载文档缺收据清除"; S95_BAD=1; }
[ "${S95_BAD}" = "0" ] && ok "[95] 确定性运行环境 全在位"

# 96. web 一键启动链(OneClick 家族):启停约定散在多文件而此前零门覆盖,
#     单侧改动即会静默漂移(pid 命名断裂=停服漏杀)。守四面:全家族语法 / pid 约定跨文件互锚 /
#     历史断裂回归钉 / 入口健壮化与文档在位。动启停约定必须保本哨兵绿(AGENTS.md 铁律)。
echo "[96] web 一键启动链"
S96_BAD=0
for S96_F in \
  "${REPO_ROOT}/Horosa_OneClick_Mac.command" \
  "${REPO_ROOT}/Horosa_Stop_Mac.command" \
  "${REPO_ROOT}/tools/mac/Horosa_Local.command" \
  "${REPO_ROOT}/tools/mac/startup_ladder.sh" \
  "${REPO_ROOT}/scripts/mac/bootstrap_and_run.sh" \
  "${REPO_ROOT}/scripts/mac/self_check_horosa.sh" \
  "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" \
  "${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh"; do
  if [ ! -f "${S96_F}" ]; then
    bad "[96] 家族文件缺失: ${S96_F#"${REPO_ROOT}"/}"; S96_BAD=1; continue
  fi
  bash -n "${S96_F}" 2>/dev/null || { bad "[96] 语法错误: ${S96_F#"${REPO_ROOT}"/}"; S96_BAD=1; }
done
S96_LOCAL="${REPO_ROOT}/tools/mac/Horosa_Local.command"
S96_STOP="${REPO_ROOT}/Horosa-Web/stop_horosa_local.sh"
S96_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
grep -q '\.horosa_web\.\${WEB_PORT}\.pid' "${S96_LOCAL}" || { bad "[96] Local 缺 web pid 端口后缀"; S96_BAD=1; }
grep -q '\.horosa_web\.\${WEB_PORT}\.pid' "${S96_STOP}" || { bad "[96] stop 缺 web pid 端口后缀"; S96_BAD=1; }
grep -q '\.horosa_py\.\${CHART_PORT}\.pid' "${S96_START}" || { bad "[96] start 缺 py pid 端口后缀"; S96_BAD=1; }
grep -q '\.horosa_py\.\${CHART_PORT}\.pid' "${S96_STOP}" || { bad "[96] stop 缺 py pid 端口后缀"; S96_BAD=1; }
grep -q 'get_listener_pids' "${S96_LOCAL}" && { bad "[96] Local 回潮未定义函数 get_listener_pids"; S96_BAD=1; }
grep -q 'port_listener_pids' "${S96_LOCAL}" || { bad "[96] Local 缺 port_listener_pids"; S96_BAD=1; }
grep -q 'lsof -tiTCP' "${S96_LOCAL}" && { bad "[96] Local 回潮全表扫描 lsof(卡死类,已封杀)"; S96_BAD=1; }
grep -q '项目完整性检查' "${REPO_ROOT}/Horosa_OneClick_Mac.command" || { bad "[96] OneClick 缺完整性检查"; S96_BAD=1; }
grep -q 'HOROSA_STOP_ALL' "${REPO_ROOT}/Horosa_Stop_Mac.command" || { bad "[96] Stop 入口缺 STOP_ALL"; S96_BAD=1; }
grep -q 'HOROSA_STOP_ALL' "${S96_STOP}" || { bad "[96] stop 脚本缺 STOP_ALL 模式"; S96_BAD=1; }
grep -q 'download_with_fallback' "${REPO_ROOT}/scripts/mac/bootstrap_and_run.sh" || { bad "[96] bootstrap 缺镜像回退"; S96_BAD=1; }
grep -q 'HOROSA_SKIP_DB_SETUP:-1' "${REPO_ROOT}/scripts/mac/bootstrap_and_run.sh" || { bad "[96] bootstrap DB 默认未跳过"; S96_BAD=1; }
grep -q '网页版一键启动' "${REPO_ROOT}/README.md" || { bad "[96] README 缺一键启动教程"; S96_BAD=1; }
[ -f "${REPO_ROOT}/docs/WEB_LOCAL_LAUNCH.md" ] || { bad "[96] 缺 WEB_LOCAL_LAUNCH.md"; S96_BAD=1; }
[ "${S96_BAD}" = "0" ] && ok "[96] web 一键启动链 全在位"


# ── [97] 七政天星择日双轮(Moira 对照)链完整性 ──────────────────────────────
echo "[97] 七政择日双轮链"
S97_BAD=0
S97_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S97_PY="${REPO_ROOT}/Horosa-Web/astropy"
for S97_F in \
  "${S97_UI}/components/guolao/electionGeomag.js" \
  "${S97_UI}/components/guolao/electionCore.js" \
  "${S97_UI}/components/guolao/moiraWheelLayout.js" \
  "${S97_UI}/components/guolao/guolaoMoiraTables.js" \
  "${S97_UI}/components/guolao/guolaoStarNotes.js" \
  "${S97_UI}/components/guolao/GuoLaoElectionTable.js" \
  "${S97_UI}/components/guolao/GuoLaoWheelCaptions.js" \
  "${S97_UI}/components/common/QuickDockBar.js" \
  "${S97_PY}/websrv/webqizhengelectionsrv.py"; do
  [ -f "${S97_F}" ] || { bad "[97] 缺文件: ${S97_F#"${REPO_ROOT}"/}"; S97_BAD=1; }
done
# WMM 系数完整性:两套历元且每套 90 行系数(截断即红)
S97_WMM_EPOCHS=$(grep -c 'epoch: 20' "${S97_UI}/components/guolao/electionGeomag.js" 2>/dev/null || echo 0)
[ "${S97_WMM_EPOCHS}" -ge 2 ] || { bad "[97] WMM 历元数 ${S97_WMM_EPOCHS} < 2"; S97_BAD=1; }
S97_WMM_ROWS=$(grep -cE '^\s*\[(1[0-2]|[1-9]), ' "${S97_UI}/components/guolao/electionGeomag.js" 2>/dev/null || echo 0)
[ "${S97_WMM_ROWS}" -ge 180 ] || { bad "[97] WMM 系数行 ${S97_WMM_ROWS} < 180(截断?)"; S97_BAD=1; }
# 端点挂载在位
grep -q "qizhengelection" "${S97_PY}/websrv/webchartsrv.py" || { bad "[97] webchartsrv 未挂载 /qizhengelection"; S97_BAD=1; }
# 快捷栏契约测试在位(信息不进栏/禁复现守卫)
[ -f "${S97_UI}/components/common/__tests__/quickDockContract.test.js" ] || { bad "[97] 缺 quickDockContract 契约测试"; S97_BAD=1; }
[ "${S97_BAD}" = "0" ] && ok "[97] 择日双轮链完整(WMM ${S97_WMM_EPOCHS} 历元/${S97_WMM_ROWS} 行系数)"

# ── [98] kill-atomic 对换(U-A):renamex_np 单点互换+启动撕裂探测 ──────────────
echo "[98] kill-atomic 对换"
S98_BAD=0
S98_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S98_TOML="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/Cargo.toml"
grep -q 'renamex_np' "${S98_MAIN}" || { bad "[98] 缺 renamex_np 系统调用"; S98_BAD=1; }
grep -q 'RENAME_SWAP' "${S98_MAIN}" || { bad "[98] 缺 RENAME_SWAP 旗标"; S98_BAD=1; }
grep -q 'fn atomic_swap_dirs' "${S98_MAIN}" || { bad "[98] 缺 atomic_swap_dirs"; S98_BAD=1; }
grep -q 'fn repair_torn_runtime_slots' "${S98_MAIN}" || { bad "[98] 缺启动撕裂探测 repair_torn_runtime_slots"; S98_BAD=1; }
grep -q 'HOROSA_SWAP_DISABLE' "${S98_MAIN}" || { bad "[98] 缺回退分支逃生阀 HOROSA_SWAP_DISABLE"; S98_BAD=1; }
grep -qE '^libc' "${S98_TOML}" || { bad "[98] Cargo.toml 缺 libc 依赖"; S98_BAD=1; }
# 两处对换必须都走 swap(全量 extracted↔current、增量 stage↔current);删 swap 只留两段 rename=静默回退,红
grep -q 'atomic_swap_dirs(&extracted_runtime, &final_runtime)' "${S98_MAIN}" || { bad "[98] 全量对换未走 swap"; S98_BAD=1; }
grep -q 'atomic_swap_dirs(&stage, &current)' "${S98_MAIN}" || { bad "[98] 增量对换未走 swap"; S98_BAD=1; }
grep -q 'repair_torn_runtime_slots(root)' "${S98_MAIN}" || { bad "[98] bootstrap 未接线撕裂探测"; S98_BAD=1; }
grep -q 'rust.torn_slot_repaired' "${S98_MAIN}" || { bad "[98] 缺撕裂修复账本段"; S98_BAD=1; }
grep -q 'atomic_swap_dirs_exchanges_trees_on_apfs' "${S98_MAIN}" || { bad "[98] 缺 swap 回归测试"; S98_BAD=1; }
grep -q 'torn_slot_repair_promotes_complete_candidate' "${S98_MAIN}" || { bad "[98] 缺撕裂修复回归测试"; S98_BAD=1; }
[ "${S98_BAD}" = "0" ] && ok "[98] kill-atomic 对换链在位(swap 双点+撕裂探测+回退阀)"

# ── [102] 部件级重试(U-E):单部件先重试再整链降级 ──────────────────────────
echo "[102] 部件级重试"
S102_BAD=0
S102_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
grep -q 'COMPONENT_RETRY_MAX' "${S102_MAIN}" || { bad "[102] 缺 COMPONENT_RETRY_MAX"; S102_BAD=1; }
grep -q 'fn download_component_with_retry' "${S102_MAIN}" || { bad "[102] 缺重试壳函数"; S102_BAD=1; }
grep -q 'download_component_with_retry(' "${S102_MAIN}" || { bad "[102] 逐部件循环未走重试壳"; S102_BAD=1; }
grep -q '次重试' "${S102_MAIN}" || { bad "[102] 缺重试可视事件文案"; S102_BAD=1; }
grep -q 'component_download_retry_then_success_and_exhaust' "${S102_MAIN}" || { bad "[102] 缺重试回归测试"; S102_BAD=1; }
grep -q 'U-E' "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_update_experience_local.sh" || { bad "[102] s2 剧本缺重试语义注记"; S102_BAD=1; }
[ "${S102_BAD}" = "0" ] && ok "[102] 部件级重试在位(sha 失配全新下/网络错续传接力)"

# ── [99] .app helper 加固(U-B):stage-first+主二进制 swap 旗标+失败重开臂 ──
echo "[99] helper 加固"
S99_BAD=0
S99_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S99_FLAGS=$(grep -c '\-\-horosa-atomic-swap' "${S99_MAIN}" 2>/dev/null || true)
[ "${S99_FLAGS}" -ge 2 ] || { bad "[99] swap 旗标出现 ${S99_FLAGS} < 2(main 分支+helper 模板须两处)"; S99_BAD=1; }
grep -q 'fn run_swap_cli' "${S99_MAIN}" || { bad "[99] 缺 swap CLI 本体"; S99_BAD=1; }
grep -q 'update-stage.app' "${S99_MAIN}" || { bad "[99] helper 缺 stage-first 暂存位"; S99_BAD=1; }
grep -q 'if ! install_app; then' "${S99_MAIN}" || { bad "[99] helper 缺 install 失败守卫臂"; S99_BAD=1; }
grep -q 'reopening previous app' "${S99_MAIN}" || { bad "[99] helper 失败臂缺重开旧 app"; S99_BAD=1; }
grep -q 'insufficient disk space' "${S99_MAIN}" || { bad "[99] helper 缺磁盘预检"; S99_BAD=1; }
# 反向锚:危险旧序(新版长时间 ditto 直写 TARGET)不得回潮
grep -q 'ditto \\"\${{SRC}}\\" \\"\${{TARGET}}\\"' "${S99_MAIN}" && { bad "[99] helper 回潮 ditto 直写 TARGET(长窗口)"; S99_BAD=1; }
grep -q 'update_helper_script_stages_before_swap' "${S99_MAIN}" || { bad "[99] 缺 helper 契约测试"; S99_BAD=1; }
grep -q 'atomic_swap_cli_flag_swaps_and_exits' "${S99_MAIN}" || { bad "[99] 缺 swap CLI 测试"; S99_BAD=1; }
[ "${S99_BAD}" = "0" ] && ok "[99] helper 加固在位(stage-first+swap 旗标+失败重开+磁盘预检)"

# ── [100] staged 持久化+断点恢复(U-C) ─────────────────────────────────────
echo "[100] staged 持久化"
S100_BAD=0
S100_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
grep -q 'staged-update.json' "${S100_MAIN}" || { bad "[100] 缺暂存档文件"; S100_BAD=1; }
grep -q 'fn load_staged_update_file_at' "${S100_MAIN}" || { bad "[100] 缺读档函数"; S100_BAD=1; }
grep -q 'STAGED_UPDATE_MAX_AGE_MS' "${S100_MAIN}" || { bad "[100] 缺过期常量"; S100_BAD=1; }
grep -q 'rust.staged_update_restored' "${S100_MAIN}" || { bad "[100] 缺恢复账本段"; S100_BAD=1; }
grep -q '此前已下载完成' "${S100_MAIN}" || { bad "[100] 缺恢复 ready 独有文案(s5 锚)"; S100_BAD=1; }
# 读档必须逐资产 sha 重验(load 函数体内含 sha256_digest)
awk '/fn load_staged_update_file_at/,/^}/' "${S100_MAIN}" | grep -q 'sha256_digest' || { bad "[100] 读档未逐资产重验 sha"; S100_BAD=1; }
# 写点+两清点+部件档清理都在
grep -q 'persist_staged_update_file(app, &staged)' "${S100_MAIN}" || { bad "[100] 下载完成未落盘"; S100_BAD=1; }
S100_CLEARS=$(grep -c 'clear_staged_update_file(app)' "${S100_MAIN}" 2>/dev/null || true)
[ "${S100_CLEARS}" -ge 2 ] || { bad "[100] 消费清点 ${S100_CLEARS} < 2(helper 交接+runtime-only 成功)"; S100_BAD=1; }
S100_CLEANUPS=$(grep -c 'cleanup_consumed_component_archives(&staged)' "${S100_MAIN}" 2>/dev/null || true)
[ "${S100_CLEANUPS}" -ge 2 ] || { bad "[100] 部件档清理点 ${S100_CLEANUPS} < 2(磁盘漏回潮)"; S100_BAD=1; }
grep -q 'staged_update_file_roundtrip_and_sha_gate' "${S100_MAIN}" || { bad "[100] 缺往返/篡改回归测试"; S100_BAD=1; }
grep -q "'此前已下载完成'" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_update_experience_local.sh" || { bad "[100] 假 release 缺 s5 断言"; S100_BAD=1; }
[ "${S100_BAD}" = "0" ] && ok "[100] staged 持久化断点恢复在位(sha 门+过期门+双清点)"

# ── [101] 更新链防降级(U-D):单调判定+双逃生阀+内联手抄零回潮 ──────────────
echo "[101] 更新防降级"
S101_BAD=0
S101_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
grep -q 'fn compute_runtime_update_decision' "${S101_MAIN}" || { bad "[101] 缺单一判定函数 compute_runtime_update_decision"; S101_BAD=1; }
grep -q 'runtime_version_rank(remote)' "${S101_MAIN}" || { bad "[101] 判定未走 runtime_version_rank 单调比较"; S101_BAD=1; }
grep -q 'HOROSA_ALLOW_DOWNGRADE' "${S101_MAIN}" || { bad "[101] 缺 env 逃生阀 HOROSA_ALLOW_DOWNGRADE"; S101_BAD=1; }
grep -q 'allowDowngrade' "${S101_MAIN}" || { bad "[101] 缺 manifest 逃生阀字段 allowDowngrade"; S101_BAD=1; }
grep -q 'rust.update_downgrade_blocked' "${S101_MAIN}" || { bad "[101] 缺降级拦截账本段"; S101_BAD=1; }
# 反向锚:runtime 判定的「remote.trim() != local.trim()」内联手抄曾散在 3 处,回潮即红
S101_NEQ=$(grep -c 'remote.trim() != local.trim()' "${S101_MAIN}" 2>/dev/null || true)
[ "${S101_NEQ}" = "0" ] || { bad "[101] runtime 判定内联手抄回潮 ${S101_NEQ} 处(必须走统一入口)"; S101_BAD=1; }
# 消费面:菜单/静默检查/后台下载/自动检查 四处必须都走统一入口
S101_CALLS=$(grep -cE 'runtime_update_decision\(&?app' "${S101_MAIN}" 2>/dev/null || true)
[ "${S101_CALLS}" -ge 4 ] || { bad "[101] runtime_update_decision 消费点 ${S101_CALLS} < 4(有路径漏收口)"; S101_BAD=1; }
grep -q 'allowDowngrade' "${REPO_ROOT}/Horosa_Desktop_Installer/INCREMENTAL_UPDATE_SOP.md" || { bad "[101] SOP §4.3 缺 allowDowngrade 退版剧本"; S101_BAD=1; }
grep -q 'runtime_update_monotonic_gate' "${S101_MAIN}" || { bad "[101] 缺单调判定回归测试"; S101_BAD=1; }
[ "${S101_BAD}" = "0" ] && ok "[101] 防降级链在位(单调判定+双逃生阀+手抄零回潮)"

# ── [103] 看门狗深探+越限UX+web 监督+横幅自愈(U-F) ────────────────────────
echo "[103] 看门狗深探链"
S103_BAD=0
S103_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S103_BANNER="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/ServiceStatusBanner.js"
S103_RECOVERY="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/serviceRecovery.js"
grep -q 'fn probe_identity' "${S103_MAIN}" || { bad "[103] 缺深度身份探针"; S103_BAD=1; }
grep -q 'fn supervisor_step' "${S103_MAIN}" || { bad "[103] 缺双 streak 状态机"; S103_BAD=1; }
grep -q 'SUPERVISOR_SILENT_ROUNDS' "${S103_MAIN}" || { bad "[103] 缺 HttpSilent 慢判常量"; S103_BAD=1; }
grep -q 'rust.web_server_restarted' "${S103_MAIN}" || { bad "[103] web 静态服务器未纳管"; S103_BAD=1; }
grep -q 'fn restart_local_services_command' "${S103_MAIN}" || { bad "[103] 缺轻量重启命令"; S103_BAD=1; }
# 命令必须注册进 generate_handler(定义了没注册=前端调不到)
awk '/generate_handler!\[/,/\]\)/' "${S103_MAIN}" | grep -q 'restart_local_services_command' || { bad "[103] 轻量重启命令未注册"; S103_BAD=1; }
grep -q 'supervisor_gave_up' "${S103_MAIN}" || { bad "[103] 缺越限事件"; S103_BAD=1; }
grep -q 'gave_up_latched' "${S103_MAIN}" || { bad "[103] 越限未闩锁(账本刷屏回潮)"; S103_BAD=1; }
grep -q '__horosaServiceEvent' "${S103_MAIN}" || { bad "[103] 缺服务监督事件通道"; S103_BAD=1; }
# 前端:自动轮询+事件钩子+错线修复(反向锚:横幅不得再直调全量修复命令作首选)
[ -f "${S103_RECOVERY}" ] || { bad "[103] 缺 serviceRecovery.js"; S103_BAD=1; }
grep -q 'startRecoveryPolling' "${S103_BANNER}" || { bad "[103] 横幅缺自动恢复轮询"; S103_BAD=1; }
grep -q 'verifyBackendIdentity' "${S103_BANNER}" || { bad "[103] 横幅重试未走身份探测"; S103_BAD=1; }
grep -q '__horosaServiceEvent' "${S103_BANNER}" || { bad "[103] 横幅缺 gave_up 事件钩子"; S103_BAD=1; }
grep -q 'restart_local_services_command' "${S103_BANNER}" || { bad "[103] 横幅重启按钮未换轻量命令"; S103_BAD=1; }
grep -q 'identity_probe_classifies_squatter_and_silence' "${S103_MAIN}" || { bad "[103] 缺探针分类回归测试"; S103_BAD=1; }
grep -q 'supervisor_streak_state_machine' "${S103_MAIN}" || { bad "[103] 缺状态机回归测试"; S103_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/serviceRecovery.test.js" ] || { bad "[103] 缺 serviceRecovery jest"; S103_BAD=1; }
[ "${S103_BAD}" = "0" ] && ok "[103] 看门狗深探链在位(四分类+双streak+web纳管+横幅自愈)"

# ── [104] 耐久更新台账+轮转保代+诊断包导出(U-G) ───────────────────────────
echo "[104] 更新台账/诊断包"
S104_BAD=0
S104_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S104_DHTML="${REPO_ROOT}/Horosa_Desktop_Installer/web/diagnostics.html"
S104_DJS="${REPO_ROOT}/Horosa_Desktop_Installer/web/diagnostics.js"
grep -q 'update-history.jsonl' "${S104_MAIN}" || { bad "[104] 缺耐久台账文件"; S104_BAD=1; }
grep -q 'fn rotate_log_keep_one' "${S104_MAIN}" || { bad "[104] 缺轮转保代函数"; S104_BAD=1; }
# 写点覆盖:staged_ready/download_error/apply_begin/helper_handoff/apply_runtime_ok/
# apply_failed/install_confirmed/watchdog_rollback/downgrade_blocked/check_failed ≥10 调用
S104_WRITES=$(grep -c 'append_update_history(' "${S104_MAIN}" 2>/dev/null || true)
[ "${S104_WRITES}" -ge 10 ] || { bad "[104] 台账写点 ${S104_WRITES} < 10(事件面漏挂)"; S104_BAD=1; }
grep -q '"event": "install_confirmed"' "${S104_MAIN}" || { bad "[104] 缺 vX→vY 结果闭环行"; S104_BAD=1; }
# 反向锚:updater-events.log 的 File::create 截断毁证旧样式不得回潮(排除注释行——
# 函数内说明性注释提到旧样式字样不算回潮)
awk '/fn log_updater_event/,/^}/' "${S104_MAIN}" | grep -v '^[[:space:]]*//' | grep -q 'File::create' && { bad "[104] events 日志截断毁证旧样式回潮"; S104_BAD=1; }
grep -q 'fn export_diagnostics_bundle' "${S104_MAIN}" || { bad "[104] 缺一键诊断包命令"; S104_BAD=1; }
awk '/generate_handler!\[/,/\]\)/' "${S104_MAIN}" | grep -q 'export_diagnostics_bundle' || { bad "[104] 诊断包命令未注册"; S104_BAD=1; }
grep -q 'update_history_lines' "${S104_MAIN}" || { bad "[104] 诊断载荷缺台账尾部"; S104_BAD=1; }
grep -q 'updateHistoryOutput' "${S104_DHTML}" || { bad "[104] 诊断页缺更新历史卡"; S104_BAD=1; }
grep -q 'exportBundleBtn' "${S104_DHTML}" || { bad "[104] 诊断页缺导出按钮"; S104_BAD=1; }
grep -q 'export_diagnostics_bundle' "${S104_DJS}" || { bad "[104] 诊断页未接导出命令"; S104_BAD=1; }
grep -q 'update_history_append_and_rotation_keeps_tail' "${S104_MAIN}" || { bad "[104] 缺台账回归测试"; S104_BAD=1; }
grep -q 'rotate_log_keep_one_generation' "${S104_MAIN}" || { bad "[104] 缺轮转保代回归测试"; S104_BAD=1; }
[ "${S104_BAD}" = "0" ] && ok "[104] 更新台账/诊断包在位(写点 ${S104_WRITES}/轮转保代/一键导出)"

# ── [105] 周期检查+节流+检查失败显式化(U-H) ──────────────────────────────
echo "[105] 更新检查节流/周期"
S105_BAD=0
S105_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S105_UN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/update/UpdateNotifier.js"
grep -q 'last-update-check.json' "${S105_MAIN}" || { bad "[105] 缺检查戳记文件"; S105_BAD=1; }
grep -q 'fn should_run_auto_check' "${S105_MAIN}" || { bad "[105] 缺节流纯函数"; S105_BAD=1; }
grep -q 'fn run_auto_update_check' "${S105_MAIN}" || { bad "[105] 缺自动检查本体函数"; S105_BAD=1; }
grep -q 'AUTO_CHECK_CYCLE_SECS' "${S105_MAIN}" || { bad "[105] 缺 24h 周期常量"; S105_BAD=1; }
grep -q 'HOROSA_UPDATE_CHECK_INTERVAL_SECS' "${S105_MAIN}" || { bad "[105] 缺 dev 周期覆盖 env"; S105_BAD=1; }
grep -q 'rust.update_check_failed' "${S105_MAIN}" || { bad "[105] 检查失败未落账本"; S105_BAD=1; }
grep -q '"check-failed"' "${S105_MAIN}" || { bad "[105] 检查失败未发显式事件"; S105_BAD=1; }
# 反向锚:检查失败只 eprintln 吞掉的旧样式(auto check skipped)不得回潮
grep -q 'auto check skipped' "${S105_MAIN}" && { bad "[105] 检查失败静默吞掉旧样式回潮"; S105_BAD=1; }
# 手动检查两路径写戳记(菜单+前端 silent);消费点 ≥3(auto+2 手动)
S105_STAMPS=$(grep -c 'write_update_check_stamp(' "${S105_MAIN}" 2>/dev/null || true)
[ "${S105_STAMPS}" -ge 3 ] || { bad "[105] 检查戳记写点 ${S105_STAMPS} < 3(手动路径漏写)"; S105_BAD=1; }
grep -q "check-failed" "${S105_UN}" || { bad "[105] 前端缺 check-failed 低打扰处理"; S105_BAD=1; }
grep -q "downgrade-blocked" "${S105_UN}" || { bad "[105] 前端缺 downgrade-blocked 提示"; S105_BAD=1; }
grep -q 'auto_check_throttle_gate' "${S105_MAIN}" || { bad "[105] 缺节流回归测试"; S105_BAD=1; }
[ "${S105_BAD}" = "0" ] && ok "[105] 检查节流/周期/失败显式化在位"

# ── [106] 安装链收尾组合锚(U-I:编码钉死/CLT桩清零/降级门/六包门/缓存实物锚/本机直连钉/搬迁) ──
echo "[106] 安装链收尾"
S106_BAD=0
S106_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S106_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S106_POST="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template"
# G1:三条 Java 启动路径都钉 file.encoding+sun.jnu.encoding;LANG 兜底(脚本+壳)
S106_ENC=$(grep -c 'Dfile.encoding=UTF-8' "${S106_START}" 2>/dev/null || true)
[ "${S106_ENC}" -ge 3 ] || { bad "[106] file.encoding 钉死 ${S106_ENC} < 3 条启动路径"; S106_BAD=1; }
S106_JNU=$(grep -c 'Dsun.jnu.encoding=UTF-8' "${S106_START}" 2>/dev/null || true)
[ "${S106_JNU}" -ge 3 ] || { bad "[106] sun.jnu.encoding 钉死 ${S106_JNU} < 3"; S106_BAD=1; }
grep -q 'export LANG=zh_CN.UTF-8' "${S106_START}" || { bad "[106] start 脚本缺 LANG 兜底"; S106_BAD=1; }
grep -q '"LANG"' "${S106_MAIN}" || { bad "[106] 壳 spawn 缺 LANG 兜底"; S106_BAD=1; }
# G2:postinstall 零 /usr/bin/python3 实调(注释里提及不算——查行首非注释调用)
grep -vE '^\s*#' "${S106_POST}" | grep -q '/usr/bin/python3' && { bad "[106] postinstall 回潮 /usr/bin/python3(CLT 弹窗桩)"; S106_BAD=1; }
# G3:降级门
grep -q 'downgrade guard' "${S106_POST}" || { bad "[106] postinstall 缺 runtime 降级门"; S106_BAD=1; }
grep -q 'sort -V' "${S106_POST}" || { bad "[106] 降级门缺 sort -V 版本比较"; S106_BAD=1; }
# G4:可用门六包(壳+postinstall 两处)
grep -q "'cherrypy','jsonpickle','swisseph','cn2an','sxtwl','cnlunar'" "${S106_MAIN}" || { bad "[106] 壳可用门未对齐 6 包"; S106_BAD=1; }
grep -q 'cherrypy, jsonpickle, swisseph, cn2an, sxtwl, cnlunar' "${S106_POST}" || { bad "[106] postinstall 可用门未对齐 6 包"; S106_BAD=1; }
# G5:健康缓存实物锚
grep -q 'fn runtime_health_probe_files_present' "${S106_MAIN}" || { bad "[106] 缺健康缓存实物锚"; S106_BAD=1; }
grep -q 'runtime_health_probe_files_present(runtime_dir)' "${S106_MAIN}" || { bad "[106] 快路径未接实物锚"; S106_BAD=1; }
# G7:本机直连钉死(三路径)
S106_NPH=$(grep -c 'Dhttp.nonProxyHosts=localhost' "${S106_START}" 2>/dev/null || true)
[ "${S106_NPH}" -ge 3 ] || { bad "[106] nonProxyHosts 钉死 ${S106_NPH} < 3"; S106_BAD=1; }
# G8:Translocation 搬迁菜单
grep -q 'MENU_RELOCATE_APP' "${S106_MAIN}" || { bad "[106] 缺搬迁菜单"; S106_BAD=1; }
grep -q 'fn relocate_app_to_applications' "${S106_MAIN}" || { bad "[106] 缺搬迁实现"; S106_BAD=1; }
[ "${S106_BAD}" = "0" ] && ok "[106] 安装链收尾在位(编码×${S106_ENC}/降级门/六包门/实物锚/直连钉×${S106_NPH}/搬迁)"

echo "[107] AI 导出链(剪贴板/PDF/BOM)+ 紫微运限方向 防回归"
S107_BAD=0
S107_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S107_TAURI="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri"
# 剪贴板:arboard 原生主路 + pbcopy 必钉 LC_CTYPE(GUI .app 无 locale → MacRoman 乱码)
grep -q 'arboard = { version = "3", default-features = false' "${S107_TAURI}/Cargo.toml" || { bad "[107] Cargo.toml 缺 arboard"; S107_BAD=1; }
grep -q 'arboard::Clipboard' "${S107_TAURI}/src/main.rs" || { bad "[107] main.rs 缺 arboard 原生主路"; S107_BAD=1; }
python3 - "${S107_TAURI}/src/main.rs" <<'PY107' || { bad "[107] main.rs 存在未钉 LC_CTYPE 的 pbcopy 调用(MacRoman 乱码复发)"; S107_BAD=1; }
import sys, re
src = open(sys.argv[1], encoding='utf-8').read()
for m in re.finditer(r'Command::new\("[^"]*pbcopy"\)', src):
    if '.env("LC_CTYPE"' not in src[m.start():m.start() + 200]:
        sys.exit(1)
sys.exit(0)
PY107
# 前端:复制唯一入口 + 组件层裸 writeText 归零(grep -a 防含 NUL 档被当二进制漏检)
[ -f "${S107_UI}/src/utils/clipboardText.js" ] || { bad "[107] 缺复制共享件 clipboardText.js"; S107_BAD=1; }
grep -q "from './clipboardText'" "${S107_UI}/src/utils/aiExport.js" || { bad "[107] aiExport 未走复制共享件"; S107_BAD=1; }
S107_RAW="$(grep -rla 'navigator.clipboard.writeText' "${S107_UI}/src/components" --include='*.js' 2>/dev/null | grep -v __tests__ | wc -l | tr -d ' ')"
[ "${S107_RAW}" = "0" ] || { bad "[107] 组件层仍有 ${S107_RAW} 档裸 navigator.clipboard.writeText(APP 内静默失败)"; S107_BAD=1; }
# PDF:负锚大负值离屏定位(仅 aiExport)+ 守卫正锚
grep -q 'left:-99999px' "${S107_UI}/src/utils/aiExport.js" && { bad "[107] aiExport PDF 宿主又用大负值离屏定位(全白 PDF)"; S107_BAD=1; }
grep -q 'canvasHasInk' "${S107_UI}/src/utils/aiExport.js" || { bad "[107] PDF 墨迹守卫缺失(空白假成功)"; S107_BAD=1; }
grep -q 'skipFonts: true' "${S107_UI}/src/utils/aiExport.js" || { bad "[107] PDF skipFonts 缺失"; S107_BAD=1; }
grep -q "output('blob')" "${S107_UI}/src/utils/aiExport.js" || { bad "[107] PDF blob 尺寸守卫缺失"; S107_BAD=1; }
# BOM 单源
grep -q 'withUtf8Bom' "${S107_UI}/src/utils/aiAnalysisExport.js" || { bad "[107] BOM 政策单源 withUtf8Bom 缺失"; S107_BAD=1; }
# 紫微运限方向(财=+8/官=+4,地支逆行宫序)
grep -q 'const caibo = (idx + 8) % 12' "${S107_UI}/src/components/ziwei/ZiWeiHelper.js" || { bad "[107] getSanheIndices 财帛方向丢失(应为 命+8)"; S107_BAD=1; }
grep -q 'const guanlu = (idx + 4) % 12' "${S107_UI}/src/components/ziwei/ZiWeiHelper.js" || { bad "[107] getSanheIndices 官禄方向丢失(应为 命+4)"; S107_BAD=1; }
# 测试在位
for t in utils/__tests__/clipboardText.test.js utils/__tests__/aiExportPdfGuard.test.js components/ziwei/__tests__/ziweiSanheDirection.test.js; do
  [ -f "${S107_UI}/src/${t}" ] || { bad "[107] 缺测试 ${t}"; S107_BAD=1; }
done
[ "${S107_BAD}" = "0" ] && ok "[107] AI 导出链 + 紫微运限方向 防回归 全在位"

# ---- [122] dist 构建指纹门(发布产物必须可追溯到干净 HEAD;杜绝「脏工作树构建」产物无对应 commit) ----
S122_BAD=0
S122_INFO="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file/build-info.json"
if [ ! -f "${S122_INFO}" ]; then
  bad "[122] dist-file 缺 build-info.json(旧产物或 build 链未挂指纹)—— npm run build:file 重建"; S122_BAD=1
else
  S122_COMMIT=$(python3 -c "import json;print(json.load(open('${S122_INFO}')).get('commit',''))" 2>/dev/null || echo "")
  S122_DIRTY=$(python3 -c "import json;print(1 if json.load(open('${S122_INFO}')).get('dirty') else 0)" 2>/dev/null || echo "1")
  S122_HEAD=$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo "")
  [ "${S122_DIRTY}" = "0" ] || { bad "[122] dist-file 由脏工作树构建(含未提交改动)——先 commit 再重 build"; S122_BAD=1; }
  if [ -n "${S122_COMMIT}" ] && [ "${S122_COMMIT}" = "${S122_HEAD}" ]; then
    :  # 指纹=HEAD,最严格等价
  elif [ -n "${S122_COMMIT}" ] && git -C "${REPO_ROOT}" merge-base --is-ancestor "${S122_COMMIT}" "${S122_HEAD}" 2>/dev/null \
       && [ -z "$(git -C "${REPO_ROOT}" diff --name-only "${S122_COMMIT}" "${S122_HEAD}" -- Horosa-Web/astrostudyui/src Horosa-Web/astrostudyui/package.json Horosa-Web/astrostudyui/.umirc.js Horosa-Web/astrostudyui/public 2>/dev/null)" ]; then
    :  # 指纹 commit 是 HEAD 祖先且前端源面零 diff:产物与 HEAD 源码等价,仍可追溯(scripts/docs-only 前进不逼重 build)
  else
    bad "[122] dist-file 构建 commit(${S122_COMMIT:0:12}) ≠ 当前 HEAD(${S122_HEAD:0:12}) 且前端源面有 diff——重 build"; S122_BAD=1
  fi
fi
grep -q "write-build-info.js dist-file" "${REPO_ROOT}/Horosa-Web/astrostudyui/package.json" 2>/dev/null || { bad "[122] build:file 未挂构建指纹脚本(write-build-info)"; S122_BAD=1; }
[ "${S122_BAD}" = "0" ] && ok "[122] dist 构建指纹(干净 HEAD ${S122_HEAD:0:12} · 与源码可对应)"

# ---- [123] 会话投毒防线+全站防白屏+浮层不透明+产物冒烟脚本(根因:request() 吞错 resolve
#      undefined 被缓存层当成功缓存=会话投毒(紫微选项永远选不中/dedupe 同参 10min 无反应);
#      直接 import 技法页无 ErrorBoundary=单组件崩整页白屏;portal 浮层消费容器作用域
#      CSS 变量=断链透明底。四防线全为可执行护栏。) ----
S123_BAD=0
S123_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
echo "[123] 会话投毒/防白屏/浮层不透明/产物冒烟"
grep -q "响应为空" "${S123_UI}/src/services/rules.js" 2>/dev/null || { bad "[123] rules.js 缺空载荷剔缓存防线(会话投毒回潮)"; S123_BAD=1; }
grep -q "吞错型失败" "${S123_UI}/src/utils/__tests__/ziweiRulesCache.test.js" 2>/dev/null || { bad "[123] 缺 rules 投毒回归测试"; S123_BAD=1; }
grep -q "空载荷不入缓存" "${S123_UI}/src/utils/requestDedupe.js" 2>/dev/null || { bad "[123] requestDedupe 缺空载荷防线(10min 投毒回潮)"; S123_BAD=1; }
grep -q "吞错型失败" "${S123_UI}/src/utils/__tests__/requestDedupe.test.js" 2>/dev/null || { bad "[123] 缺 dedupe 投毒回归测试"; S123_BAD=1; }
grep -q "TechniqueErrorBoundary" "${S123_UI}/src/components/comp/FreezeInactive.js" 2>/dev/null || { bad "[123] FreezeInactive 未集成 ErrorBoundary(直接 import 技法页白屏回潮)"; S123_BAD=1; }
[ -f "${S123_UI}/src/components/comp/__tests__/freezeInactiveBoundary.test.js" ] || { bad "[123] 缺防白屏接线测试"; S123_BAD=1; }
grep -q "horosa-floating-surface" "${S123_UI}/src/layouts/app.less" 2>/dev/null || { bad "[123] app.less 缺 floating-surface 基类"; S123_BAD=1; }
awk '/\.horosa-guolao-moira-tooltip \{/,/^\}/' "${S123_UI}/src/components/guolao/GuoLaoMoiraWheel.less" 2>/dev/null | grep -q -- "--moira-tooltip-bg" || { bad "[123] moira tooltip 变量未自带(portal 断链透明回潮)"; S123_BAD=1; }
grep -q -- "--horosa-surface-solid" "${S123_UI}/src/utils/helper.js" 2>/dev/null || { bad "[123] setupFloatingTooltip 背景未用 surface-solid(浮层微透明回潮)"; S123_BAD=1; }
[ -x "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_packaged_frontend.sh" ] || { bad "[123] 缺 verify_packaged_frontend.sh(打包产物冒烟制度)"; S123_BAD=1; }
[ "${S123_BAD}" = "0" ] && ok "[123] 投毒防线×2+防白屏接线+浮层不透明+产物冒烟脚本 全在位"

# ---- [124] 推运盘星体白名单防线(历史事故:
#      根因:星运页三个推运 TabPane 漏传 planetDisplay 等显示 props,
#      AstroDoubleChart/AstroChart 把「漏传(undefined)」当「空白名单」→ 双盘有框架无星体,
#      且 dev 源码恒正常(props 齐)——只有打包产物坏,preview 永远测不出。
#      判据:推运盘 svg texts=64(坏)/250(好)。防线两层:①三 TabPane 显式传 planetDisplay
#      ②两 chart 组件对漏传回落 DEFAULT_OBJECTS/DEFAULT_LOTS(漏传≠全空盘)。) ----
S124_BAD=0
S124_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
echo "[124] 推运盘星体白名单(漏传≠全空盘)"
S124_CNT=$(grep -c "planetDisplay={this.props.planetDisplay}" "${S124_UI}/src/components/direction/AstroDirectMain.js" 2>/dev/null || echo 0)
[ "${S124_CNT}" -ge 6 ] || { bad "[124] AstroDirectMain planetDisplay 透传少于 6 处(推运 TabPane 漏传回潮,现=${S124_CNT})"; S124_BAD=1; }
grep -q "DEFAULT_OBJECTS" "${S124_UI}/src/components/astro/AstroDoubleChart.js" 2>/dev/null || { bad "[124] AstroDoubleChart 缺 planetDisplay 漏传回落(空盘回潮)"; S124_BAD=1; }
grep -q "DEFAULT_OBJECTS" "${S124_UI}/src/components/astro/AstroChart.js" 2>/dev/null || { bad "[124] AstroChart 缺 planetDisplay 漏传回落(空盘回潮)"; S124_BAD=1; }
[ "${S124_BAD}" = "0" ] && ok "[124] 推运 TabPane 透传×${S124_CNT}+双 chart 组件漏传回落 全在位"

# ---- [125] 存储配额治理(FL 级「一个都没修好」终局根因:黄历缓存写满 localStorage
#      5MB origin 级配额 → 全 App 一切 setItem 抛 QuotaExceededError → 页页炸错误卡。
#      防线:①派生缓存迁 IndexedDB(字节预算+LRU,与 5MB 绝缘)+首启迁移清尸键
#      ②全站裸 localStorage.setItem 白名单制(新增裸写=红)③错误卡 quota 自愈按钮
#      ④quota 注错金标。) ----
S125_BAD=0
S125_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
echo "[125] 存储配额治理(缓存分层+裸写白名单+自愈)"
# ① 缓存分层:localCalcCache 走 IndexedDB 后端+迁移器
grep -q "idbCacheStore" "${S125_UI}/src/utils/localCalcCache.js" 2>/dev/null || { bad "[125] localCalcCache 未走 IndexedDB 后端(5MB 定时炸弹回潮)"; S125_BAD=1; }
grep -q "migrateLegacyLocalStorage" "${S125_UI}/src/utils/localCalcCache.js" 2>/dev/null || { bad "[125] 缺首启迁移器(老设备尸键不清)"; S125_BAD=1; }
grep -q "TOTAL_BUDGET_BYTES" "${S125_UI}/src/utils/idbCacheStore.js" 2>/dev/null || { bad "[125] idbCacheStore 缺字节预算(磁盘无限膨胀)"; S125_BAD=1; }
# ② 裸 setItem 白名单:只允许 safeStorage/deferredStorage(自带 quota 防线)出现裸写
S125_BARE=$(grep -rln "localStorage\.setItem" "${S125_UI}/src" --include="*.js" 2>/dev/null | grep -v "__tests__" | grep -v "safeStorage.js" | grep -v "deferredStorage.js" | head -5)
[ -z "${S125_BARE}" ] || { bad "[125] 发现白名单外裸 localStorage.setItem(须走 safeStorage): ${S125_BARE}"; S125_BAD=1; }
# ③ 错误卡 quota 自愈
grep -q "clearRecoverableCaches" "${S125_UI}/src/components/common/TechniqueErrorBoundary.js" 2>/dev/null || { bad "[125] 错误卡缺 quota 一键清理自愈"; S125_BAD=1; }
# ④ quota 注错金标
[ -f "${S125_UI}/src/utils/__tests__/storageQuotaGuard.test.js" ] || { bad "[125] 缺 quota 注错回归金标"; S125_BAD=1; }
[ "${S125_BAD}" = "0" ] && ok "[125] 缓存分层+迁移器+字节预算+裸写白名单+自愈+金标 全在位"

# ---- [126] 盘面可见性重画+失败泊车(推运/恒星推运「表新盘旧」根治。
#      根因:antd Tabs 切换只切 CSS(children element 引用不变→React bail out,子树零 render);
#      隐藏期(svg 0×0,draw 尺寸早退)数据已更新的 d3 手绘盘切回后无任何重画触发 → 盘停旧数据、
#      右表已是新数据,永久不吻合。防线:①watchChartSvgResize(ResizeObserver,0→非0 必重画)
#      ②四个无自愈路径的 chart 组件挂接 ③load 失败绝不记 key 为已完成(失败泊车,窗口期后重试)
#      ④可见性重画+泊车金标。铁律:「隐藏期 0×0 不记签名」必须搭配变可见重画触发器。) ----
S126_BAD=0
S126_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
echo "[126] 盘面可见性重画+失败泊车(表盘严格吻合)"
# ① 共享工具在位
grep -q "export function watchChartSvgResize" "${S126_UI}/src/utils/chartDrawGuard.js" 2>/dev/null || { bad "[126] chartDrawGuard 缺 watchChartSvgResize(隐藏盘切回不重画回潮)"; S126_BAD=1; }
# ② 四个无自愈路径组件挂接(AstroDoubleChart/AstroChart=案发地;JinKouChart/GuaZhanChart=同病)
for S126_F in astro/AstroDoubleChart.js astro/AstroChart.js jinkou/JinKouChart.js guazhan/GuaZhanChart.js; do
	grep -q "watchChartSvgResize" "${S126_UI}/src/components/${S126_F}" 2>/dev/null || { bad "[126] ${S126_F} 未挂可见性重画"; S126_BAD=1; }
done
# ③ 推运面板+三容器 失败泊车(catch 记 key=表盘永久分叉)
grep -q "parkLoadFailure" "${S126_UI}/src/components/astro/AstroProgChart.js" 2>/dev/null || { bad "[126] ProgMethodPanel 缺失败泊车(load 失败吞更新回潮)"; S126_BAD=1; }
for S126_C in AstroProgressions AstroVedicProgressions AstroJaynesProgressions; do
	grep -q "parkLoadFailure" "${S126_UI}/src/components/astro/${S126_C}.js" 2>/dev/null || { bad "[126] ${S126_C} 缺失败泊车"; S126_BAD=1; }
done
# ④ 金标在位
[ -f "${S126_UI}/src/utils/__tests__/chartVisibilityRedraw.test.js" ] || { bad "[126] 缺可见性重画+泊车金标"; S126_BAD=1; }
[ "${S126_BAD}" = "0" ] && ok "[126] 可见性重画工具+4组件挂接+失败泊车×4+金标 全在位"

# ── [127] helper 全量 runtime 原子化(手术收进 TARGET 二进制/定义不执行/wait 后时序/
#     previous 保留/撕裂候选 _update/失败臂不写标记/孤儿清扫/旧危险序仅存于 _legacy 逃生阀) ──
echo "[127] helper 全量 runtime 原子化"
S127_BAD=0
S127_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
# ① 新协议生成器:非 legacy 函数体必须经 --horosa-runtime-swap,且零两段 mv 危险序
S127_NEWBODY=$(awk '/^fn build_single_runtime_update_command\(/{f=1} /^fn build_single_runtime_update_command_legacy\(/{f=0} f{print}' "${S127_MAIN}")
printf '%s' "${S127_NEWBODY}" | grep -q -- '--horosa-runtime-swap' || { bad "[127] 新协议生成器未经 TARGET 二进制对换"; S127_BAD=1; }
printf '%s' "${S127_NEWBODY}" | grep -qF 'mv \"${WORK_ROOT}/runtime-payload\"' && { bad "[127] 新协议生成器回潮两段 mv 危险序"; S127_BAD=1; }
# ② 逃生阀成对:legacy 函数 + 开关门都在(单删其一=半拆)
grep -q 'fn build_single_runtime_update_command_legacy' "${S127_MAIN}" || { bad "[127] 缺 legacy 逃生阀函数"; S127_BAD=1; }
grep -q 'fn helper_runtime_swap_enabled' "${S127_MAIN}" || { bad "[127] 缺 HOROSA_HELPER_RUNTIME_SWAP 开关门"; S127_BAD=1; }
# ③ CLI 钩 + 协议统一(CLI 必须走 extract_runtime_archive_with 同一协议 → previous 保留/版本闸/磁盘预检全继承)
grep -q 'fn run_runtime_swap_cli' "${S127_MAIN}" || { bad "[127] 缺 runtime-swap CLI 实现"; S127_BAD=1; }
awk '/^fn run_runtime_swap_cli\(/{f=1} f&&/^}$/{exit} f{print}' "${S127_MAIN}" | grep -q 'extract_runtime_archive_with' || { bad "[127] CLI 未复用进程内 extract 协议(previous 保留失守)"; S127_BAD=1; }
# ④ 模板时序:runtime 调用必须在 install_app 之后(sleep 1 之后)且失败臂 exit 73 在 mark 之前
grep -qF 'sleep 1\nif ! run_runtime_installs; then' "${S127_MAIN}" || { bad "[127] 模板时序失守(runtime 未在 install_app 之后)"; S127_BAD=1; }
grep -qF 'exit 73\nfi\nmark_update_complete \"pending_manual\"' "${S127_MAIN}" || { bad "[127] 失败臂/完成标记相对序失守(铁律14)"; S127_BAD=1; }
# ⑤ 撕裂候选含旧协议暂存位 _update/runtime-payload
grep -qF 'root.join("_update").join("runtime-payload")' "${S127_MAIN}" || { bad "[127] 撕裂候选缺 _update(旧协议过渡跳撕裂成孤儿)"; S127_BAD=1; }
# ⑥ 孤儿清扫 + 账本段
grep -q 'fn sweep_stale_runtime_stage_dirs' "${S127_MAIN}" || { bad "[127] 缺孤儿暂存清扫"; S127_BAD=1; }
grep -q 'rust.stale_stage_swept' "${S127_MAIN}" || { bad "[127] 清扫缺账本段"; S127_BAD=1; }
# ⑦ helper_handoff 事件带协议指纹(排障时区分新旧协议)
grep -q '"helperProtocol"' "${S127_MAIN}" || { bad "[127] helper_handoff 缺协议指纹字段"; S127_BAD=1; }
# ⑧ 回归测试在位(契约钉住:时序/铁律14/开关闭环/版本闸/previous 保留/收养)
for t in update_helper_script_runtime_swap_after_wait_and_app update_helper_runtime_failure_arm_never_marks update_helper_legacy_killswitch_restores_old_template runtime_swap_cli_rejects_version_mismatch runtime_swap_cli_promotes_and_keeps_previous repair_torn_slots_adopts_legacy_update_dir; do
  grep -q "fn ${t}" "${S127_MAIN}" || { bad "[127] 缺回归测试 ${t}"; S127_BAD=1; }
done
[ "${S127_BAD}" = "0" ] && ok "[127] helper 全量 runtime 原子化在位(CLI 协议统一/时序/previous 保留/撕裂候选/清扫/测试×6)"

# ── [128] 跨进程手术互斥锁(flock 五叶子/上层禁取反锚/多实例更新感知) ──
echo "[128] 跨进程手术互斥锁"
S128_BAD=0
S128_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S128_BANNER="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/ServiceStatusBanner.js"
# ① 锁原语三件:锁文件名常量 / flock 系调 / 开关门
grep -q '\.horosa-surgery\.lock' "${S128_MAIN}" || { bad "[128] 缺锁文件名常量"; S128_BAD=1; }
grep -q 'libc::flock(fd, libc::LOCK_EX | libc::LOCK_NB)' "${S128_MAIN}" || { bad "[128] 缺 flock 非阻塞轮询"; S128_BAD=1; }
grep -q 'HOROSA_SURGERY_LOCK_DISABLE' "${S128_MAIN}" || { bad "[128] 缺锁开关门"; S128_BAD=1; }
# ② 五叶各含锁调用(required×2 + optional×3),少一叶=写窗口裸奔
for leaf in extract_runtime_archive_with apply_component_updates_with; do
  awk "/^fn ${leaf}\(/{f=1} f&&/^}\$/{exit} f{print}" "${S128_MAIN}" | grep -q 'acquire_surgery_lock_required' || { bad "[128] ${leaf} 缺 required 锁"; S128_BAD=1; }
done
for leaf in rollback_runtime_to_previous repair_torn_runtime_slots cleanup_previous_slots; do
  awk "/^fn ${leaf}\(/{f=1} f&&/^}\$/{exit} f{print}" "${S128_MAIN}" | grep -q 'acquire_surgery_lock_optional' || { bad "[128] ${leaf} 缺 optional 锁"; S128_BAD=1; }
done
# ③ 反向锚:锁调用总数=5(五叶各一)+定义处;上层乱取=同进程 fd 互斥自死锁
S128_REQ=$(grep -c 'acquire_surgery_lock_required(' "${S128_MAIN}" || true)
S128_OPT=$(grep -c 'acquire_surgery_lock_optional(' "${S128_MAIN}" || true)
[ "${S128_REQ}" -eq 3 ] || { bad "[128] required 锁出现 ${S128_REQ} 次 ≠ 3(定义1+两叶;上层禁取)"; S128_BAD=1; }
[ "${S128_OPT}" -eq 4 ] || { bad "[128] optional 锁出现 ${S128_OPT} 次 ≠ 4(定义1+三叶;上层禁取)"; S128_BAD=1; }
# ④ 收养复核:repair 拿锁后必须复核 current(等锁期间对方可能已产出)
awk '/^fn repair_torn_runtime_slots\(/{f=1} f&&/^}$/{exit} f{print}' "${S128_MAIN}" | grep -q '拿锁后复核' || { bad "[128] repair 缺拿锁后复核"; S128_BAD=1; }
# ⑤ 多实例更新感知(V11):纯函数+supervisor 接线+账本+前端信息横幅
grep -q 'fn runtime_change_step' "${S128_MAIN}" || { bad "[128] 缺 runtime_change_step 纯函数"; S128_BAD=1; }
grep -q 'rust.runtime_updated_elsewhere' "${S128_MAIN}" || { bad "[128] 缺多实例更新账本段"; S128_BAD=1; }
grep -q 'runtime_updated_elsewhere' "${S128_BANNER}" || { bad "[128] 前端横幅未接多实例更新事件"; S128_BAD=1; }
# ⑥ 账本段 + 回归测试
grep -q 'rust.surgery_lock_timeout' "${S128_MAIN}" || { bad "[128] 缺锁超时账本段"; S128_BAD=1; }
for t in surgery_lock_blocks_second_acquire_same_process surgery_lock_cross_process_contention surgery_lock_released_on_sigkill surgery_lock_disable_env_bypasses torn_repair_skips_when_locked runtime_change_step_detects_version_drift; do
  grep -q "fn ${t}" "${S128_MAIN}" || { bad "[128] 缺回归测试 ${t}"; S128_BAD=1; }
done
[ "${S128_BAD}" = "0" ] && ok "[128] 跨进程手术锁在位(五叶插桩/上层禁取反锚/复核/V11 感知/测试×6)"

# ── [129] API 回退源 sha 闭环(manifest asset 取回 / 守门无条件 / notify-only 不触网) ──
echo "[129] API 回退源 sha 闭环"
S129_BAD=0
S129_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S129_NOTIFIER="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/update/UpdateNotifier.js"
# ① 反向锚(最重要):旧「按来源豁免 sha 守门」条件式零回潮——无 sha 绝不自动安装
grep -q 'plan.source == UpdateSource::Manifest' "${S129_MAIN}" && { bad "[129] sha 守门回潮按来源豁免(GithubApi 回退将无 sha 自动安装)"; S129_BAD=1; }
# ② 守门无条件在位(两处消费点:菜单检查 + 后台下载)
S129_GUARD=$(grep -c 'plan.latest_version > current && plan.app_sha256.is_none()' "${S129_MAIN}" || true)
[ "${S129_GUARD}" -ge 2 ] || { bad "[129] 无条件 app sha 守门 ${S129_GUARD} < 2 处"; S129_BAD=1; }
S129_RTG=$(grep -c 'runtime_needs_update && plan.runtime_sha256.is_none()' "${S129_MAIN}" || true)
[ "${S129_RTG}" -ge 2 ] || { bad "[129] 无条件 runtime sha 守门 ${S129_RTG} < 2 处"; S129_BAD=1; }
# ③ 一级回退:经 API 定位 manifest asset 取回真 manifest(引用 update_manifest_name 配置)
grep -q 'fn fetch_manifest_via_release_asset' "${S129_MAIN}" || { bad "[129] 缺 manifest asset 取回"; S129_BAD=1; }
awk '/^fn fetch_manifest_via_release_asset\(/{f=1} f&&/^}$/{exit} f{print}' "${S129_MAIN}" | grep -q 'a.name == manifest_name' || { bad "[129] asset 取回未按 updateManifestName 匹配"; S129_BAD=1; }
grep -q 'UpdateSource::ManifestViaApi' "${S129_MAIN}" || { bad "[129] 缺 ManifestViaApi 来源变体"; S129_BAD=1; }
# ④ 纯映射单一真值(主通道与回退通道共用,防手抄分叉)
grep -q 'fn plan_from_manifest' "${S129_MAIN}" || { bad "[129] 缺 plan_from_manifest 纯映射"; S129_BAD=1; }
S129_PFM=$(grep -c 'plan_from_manifest(' "${S129_MAIN}" || true)
[ "${S129_PFM}" -ge 4 ] || { bad "[129] plan_from_manifest 调用 ${S129_PFM} < 4(定义1+主通道1+回退1+测试)"; S129_BAD=1; }
# ⑤ 二级降级 notify-only:plan 字段 + 三消费点短路 + 账本 + 台账
grep -q 'notify_only: bool' "${S129_MAIN}" || { bad "[129] UpdatePlan 缺 notify_only"; S129_BAD=1; }
grep -q 'rust.update_notify_only' "${S129_MAIN}" || { bad "[129] 缺 notify-only 账本段"; S129_BAD=1; }
grep -q 'rust.update_manifest_via_api' "${S129_MAIN}" || { bad "[129] 缺 asset 取回账本段"; S129_BAD=1; }
grep -q '"event": "notify_only"' "${S129_MAIN}" || { bad "[129] notify-only 未写耐久台账"; S129_BAD=1; }
grep -q '"phase": "notify-only"' "${S129_MAIN}" || { bad "[129] 缺 notify-only 事件"; S129_BAD=1; }
awk '/^fn run_background_update_download\(/{f=1} f&&/^}$/{exit} f{print}' "${S129_MAIN}" | grep -q 'if plan.notify_only' || { bad "[129] 后台下载未短路 notify-only(会触网无 sha 下载)"; S129_BAD=1; }
# ⑥ 前端:notifyOnly 判空退化 + 「打开发布页」形态
grep -q 'payload.notifyOnly === true' "${S129_NOTIFIER}" || { bad "[129] 前端 notifyOnly 未判空退化(老壳不安全)"; S129_BAD=1; }
grep -q '打开发布页' "${S129_NOTIFIER}" || { bad "[129] 前端缺发布页出口"; S129_BAD=1; }
# ⑦ 开关(只允许「跳过 asset 取回」,不提供「恢复无 sha 安装」的回魂路)+ 回归测试
grep -q 'HOROSA_UPDATE_API_MANIFEST_FETCH' "${S129_MAIN}" || { bad "[129] 缺 asset 取回开关"; S129_BAD=1; }
for t in api_fallback_fetches_manifest_asset_and_keeps_sha api_fallback_manifest_asset_missing_yields_none api_fallback_manifest_asset_bad_json_yields_none api_manifest_fetch_killswitch_forces_notify_only_path plan_from_manifest_without_sha_leaves_none_for_guard; do
  grep -q "fn ${t}" "${S129_MAIN}" || { bad "[129] 缺回归测试 ${t}"; S129_BAD=1; }
done
[ "${S129_BAD}" = "0" ] && ok "[129] API 回退源 sha 闭环在位(asset 取回/守门无条件×${S129_GUARD}/notify-only 不触网/前端退化/测试×5)"

# ── [130] 就绪门 progress-aware 续命(进展指纹/续命/cap 夹钳/判死引用进展/壳脚同步) ──
echo "[130] 就绪门 progress-aware 续命"
S130_BAD=0
S130_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S130_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
grep -q '_progress_fingerprint()' "${S130_START}" || { bad "[130] 缺进展指纹函数"; S130_BAD=1; }
grep -q 'sh.ready_extend' "${S130_START}" || { bad "[130] 缺续命账本段"; S130_BAD=1; }
grep -q 'sh.ready_giveup' "${S130_START}" || { bad "[130] 缺判死账本段"; S130_BAD=1; }
grep -q 'HOROSA_READY_PROGRESS_EXTEND' "${S130_START}" || { bad "[130] 缺总开关"; S130_BAD=1; }
grep -q 'HOROSA_READY_TOTAL_CAP_SECS' "${S130_START}" || { bad "[130] 缺总 cap(无限等防线)"; S130_BAD=1; }
# 反锚①:判死分支必须引用 last_progress_epoch(续命被删回硬超时=红)
awk '/-ge "\$\{deadline_epoch\}"/{f=1} f' "${S130_START}" | head -30 | grep -q 'last_progress_epoch' || { bad "[130] 判死分支未引用 last_progress_epoch(硬超时回潮)"; S130_BAD=1; }
# 反锚②:续命必须被 cap 夹钳(超冲 59s 病零回潮)
grep -q 'cap_epoch=' "${S130_START}" || { bad "[130] 续命缺 cap 夹钳"; S130_BAD=1; }
# 反锚③:指纹函数禁 lsof(慢探针拖死就绪门)
awk '/_progress_fingerprint\(\)/{f=1} f&&/^}$/{exit} f{print}' "${S130_START}" | grep -q 'lsof' && { bad "[130] 指纹函数混入 lsof"; S130_BAD=1; }
# 壳脚同步:心跳读 ready_extend 段给续命可视文案
grep -q 'sh.ready_extend' "${S130_MAIN}" || { bad "[130] 壳心跳未接续命段(慢机用户会当卡死)"; S130_BAD=1; }
grep -q 'fn start_script_keeps_progress_extend_guard' "${S130_MAIN}" || { bad "[130] 缺契约测试"; S130_BAD=1; }
[ "${S130_BAD}" = "0" ] && ok "[130] progress-aware 就绪门在位(指纹/续命/cap 夹钳/判死引用进展/壳脚同步/契约)"

# ── [131] 探针深化(OOM 转硬死/deep 真算双端 proto2 一致/壳 proto 门代数差免疫) ──
echo "[131] 探针深化(OOM+deep)"
S131_BAD=0
S131_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S131_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S131_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/HorosaIdentityController.java"
S131_PY="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
# ① JVM OOM 旗:走集中变量(三启动分支共用)+ 开关
grep -q 'ExitOnOutOfMemoryError' "${S131_START}" || { bad "[131] 缺 ExitOnOutOfMemoryError(软 OOM 假活盲区回潮)"; S131_BAD=1; }
grep -q 'HOROSA_JAVA_EXIT_ON_OOM' "${S131_START}" || { bad "[131] 缺 OOM 旗开关"; S131_BAD=1; }
# ② 双端 proto 一致升 2(单边升协议=红)+ deep 实现 + dev 注错钩
grep -q '\\"proto\\":2' "${S131_JAVA}" || { bad "[131] Java 身份端 proto 未升 2"; S131_BAD=1; }
grep -q "'proto': 2" "${S131_PY}" || { bad "[131] Python 身份端 proto 未升 2"; S131_BAD=1; }
grep -q 'runDeepProbe' "${S131_JAVA}" || { bad "[131] Java 缺深探真算"; S131_BAD=1; }
grep -q '_identity_deep_ok' "${S131_PY}" || { bad "[131] Python 缺深探真算"; S131_BAD=1; }
grep -q 'HOROSA_IDENTITY_DEEP_FAIL' "${S131_JAVA}" || { bad "[131] Java 缺注错钩"; S131_BAD=1; }
grep -q 'HOROSA_IDENTITY_DEEP_FAIL' "${S131_PY}" || { bad "[131] Python 缺注错钩"; S131_BAD=1; }
# ③ 壳侧:DeepFail/DeepUnsupported 分类 + deep_step + 周期常量 + 开关 + proto 门包裹
grep -q 'DeepFail' "${S131_MAIN}" || { bad "[131] 缺 DeepFail 分类"; S131_BAD=1; }
grep -q 'DeepUnsupported' "${S131_MAIN}" || { bad "[131] 缺 DeepUnsupported(代数差免疫)"; S131_BAD=1; }
grep -q 'fn deep_step' "${S131_MAIN}" || { bad "[131] 缺 deep_step 状态机"; S131_BAD=1; }
grep -q 'SUPERVISOR_DEEP_EVERY_ROUNDS' "${S131_MAIN}" || { bad "[131] 缺深探周期常量"; S131_BAD=1; }
grep -q 'HOROSA_DEEP_PROBE' "${S131_MAIN}" || { bad "[131] 缺深探开关"; S131_BAD=1; }
# 反锚:probe_identity 内 deep 判定必须被 proto 门包裹(proto<2 直通,防误杀旧 runtime)
awk '/^fn probe_identity\(/{f=1} f&&/^}$/{exit} f{print}' "${S131_MAIN}" | grep -q 'proto < 2' || { bad "[131] deep 判定缺 proto 门(新壳×旧 runtime 会被误杀)"; S131_BAD=1; }
# ④ 账本段 + 回归测试
grep -q 'rust.deep_probe_fail' "${S131_MAIN}" || { bad "[131] 缺深探失败账本段"; S131_BAD=1; }
grep -q 'rust.deep_probe_unsupported' "${S131_MAIN}" || { bad "[131] 缺 unsupported 账本段"; S131_BAD=1; }
for t in deep_step_state_machine probe_identity_deep_unsupported_on_proto1 probe_identity_deep_fail_on_proto2 probe_identity_deep_ok_on_proto2; do
  grep -q "fn ${t}" "${S131_MAIN}" || { bad "[131] 缺回归测试 ${t}"; S131_BAD=1; }
done
grep -q 'test_horosa_identity_deep_ok' "${REPO_ROOT}/Horosa-Web/astropy/tests/test_horosa_identity.py" || { bad "[131] 缺 Python 深探 pytest"; S131_BAD=1; }
[ "${S131_BAD}" = "0" ] && ok "[131] 探针深化在位(OOM 旗/双端 proto2/deep 真算/proto 门/账本/测试)"

# ── [132] 观测一致性(状态灯真话/三处重启统一轻量/诊断包收 Java 日志) ──
echo "[132] 观测一致性"
S132_BAD=0
S132_DOT="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/BackendStatusDot.js"
S132_MODAL="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/ChartServiceErrorModal.js"
S132_BANNER="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/ServiceStatusBanner.js"
S132_RECOVERY="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/serviceRecovery.js"
S132_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
# ① 真话灯:状态灯必须走身份握手;反锚 /heartbeat 裸 fetch 零回潮(404/毒200 点绿灯的病)
grep -q 'verifyBackendIdentity' "${S132_DOT}" || { bad "[132] 状态灯未走身份握手"; S132_BAD=1; }
grep -q '/heartbeat' "${S132_DOT}" && { bad "[132] 状态灯回潮 /heartbeat 裸探(主后端无此 HTTP 路由,灯会撒谎)"; S132_BAD=1; }
# ② 三处「重启后端」统一轻量入口(共享 util,禁再内联 trigger_runtime_repair_command 直连)
grep -q 'fn invokeLightServiceRestart\|function invokeLightServiceRestart\|invokeLightServiceRestart' "${S132_RECOVERY}" || { bad "[132] 缺共享轻量重启 util"; S132_BAD=1; }
for f in "${S132_DOT}" "${S132_MODAL}" "${S132_BANNER}"; do
  grep -q 'invokeLightServiceRestart' "${f}" || { bad "[132] $(basename "${f}") 未走统一重启入口"; S132_BAD=1; }
done
grep -q "onClick={() => tauriInvoke('trigger_runtime_repair_command'" "${S132_MODAL}" && { bad "[132] 弹窗回潮全量修复直连"; S132_BAD=1; }
grep -q "invoke('trigger_runtime_repair_command')" "${S132_DOT}" && { bad "[132] 状态灯回潮全量修复直连"; S132_BAD=1; }
# ③ 诊断包收 Java 结构化日志(选取器 + java-logs 目录 + 20MB cap)
grep -q 'fn select_recent_files_by_mtime' "${S132_MAIN}" || { bad "[132] 缺 Java 日志选取器"; S132_BAD=1; }
grep -q '"java-logs"' "${S132_MAIN}" || { bad "[132] 诊断包未收 java-logs"; S132_BAD=1; }
grep -q '.horosa-logs' "${S132_MAIN}" || { bad "[132] 诊断包未指向 log4j2 落点"; S132_BAD=1; }
# ④ 回归测试
grep -q 'fn select_recent_files_prefers_newest_within_cap' "${S132_MAIN}" || { bad "[132] 缺选取器测试"; S132_BAD=1; }
grep -q 'invokeLightServiceRestart' "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/serviceRecovery.test.js" || { bad "[132] 缺轻量重启 jest"; S132_BAD=1; }
[ "${S132_BAD}" = "0" ] && ok "[132] 观测一致性在位(真话灯/三处统一轻量/诊断包 java-logs/测试)"

# ── [133] 运行期资源自感知(磁盘水位闩/权限写测定因/失败上浮) ──
echo "[133] 运行期资源自感知"
S133_BAD=0
S133_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S133_BANNER="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/ServiceStatusBanner.js"
grep -q 'fn disk_low_step' "${S133_MAIN}" || { bad "[133] 缺磁盘水位闩纯函数"; S133_BAD=1; }
grep -q 'HOROSA_DISK_WATCH' "${S133_MAIN}" || { bad "[133] 缺磁盘监控开关"; S133_BAD=1; }
grep -q 'HOROSA_DISK_MIN_MB' "${S133_MAIN}" || { bad "[133] 缺阈值参数"; S133_BAD=1; }
grep -q 'rust.disk_low' "${S133_MAIN}" || { bad "[133] 缺磁盘水位账本段"; S133_BAD=1; }
grep -q '"kind": "disk_low"' "${S133_MAIN}" || { bad "[133] 缺 disk_low 事件"; S133_BAD=1; }
grep -q "'disk_low'" "${S133_BANNER}" || { bad "[133] 前端横幅未接 disk_low"; S133_BAD=1; }
# 权限定因:写测函数 + 失败包装(restart 失败必须过定因)+ 账本
grep -q 'fn classify_permission_issue' "${S133_MAIN}" || { bad "[133] 缺权限写测定因"; S133_BAD=1; }
grep -q 'fn restart_local_services_inner' "${S133_MAIN}" || { bad "[133] restart 失败未过定因包装"; S133_BAD=1; }
grep -q 'rust.permission_probe_failed' "${S133_MAIN}" || { bad "[133] 缺权限定因账本段"; S133_BAD=1; }
# 解闩防抖反锚:disk_low_step 内必须有 2× 恢复阈值(防阈值附近抖动刷屏)
awk '/^fn disk_low_step\(/{f=1} f&&/^}$/{exit} f{print}' "${S133_MAIN}" | grep -q 'saturating_mul(2)' || { bad "[133] 缺 2× 解闩防抖"; S133_BAD=1; }
for t in disk_low_step_latch_and_recovery classify_permission_issue_detects_readonly_dir; do
  grep -q "fn ${t}" "${S133_MAIN}" || { bad "[133] 缺回归测试 ${t}"; S133_BAD=1; }
done
[ "${S133_BAD}" = "0" ] && ok "[133] 资源自感知在位(水位闩/2×防抖/权限定因/失败上浮/测试×2)"

# 114. 签名产物防误发():ad-hoc 构建落 UNSIGNED-DEV-BUILD.txt 标记+警告;
#      publish 上传前 stapler validate 硬门(逃生 HOROSA_ALLOW_UNSTAPLED=1 仅测试 release)。
#      堵「本地未签名误建版被 publish 流入公开 release、他机 Gatekeeper 拦装」这条路。
echo "[134] 签名产物防误发(build 标记 + publish 装订门)"
S134_BAD=0
S134_BUILD="${INSTALLER_ROOT}/scripts/build_desktop_release.sh"
S134_PUB="${INSTALLER_ROOT}/scripts/publish_github_release.sh"
grep -q 'UNSIGNED-DEV-BUILD.txt' "${S134_BUILD}" || { bad "[134] build 缺 ad-hoc 标记文件落点"; S134_BAD=1; }
grep -q 'ad-hoc 构建(未签名/未公证)' "${S134_BUILD}" || { bad "[134] build 缺 ad-hoc 显眼警告"; S134_BAD=1; }
awk '/UNSIGNED-DEV-BUILD.txt/{n++} END{exit !(n>=2)}' "${S134_BUILD}" || { bad "[134] build 标记须双臂(降档写入+签名档清除)"; S134_BAD=1; }
grep -q 'xcrun stapler validate "${DIST_ROOT}/${DESKTOP_OFFLINE_PKG}"' "${S134_PUB}" || { bad "[134] publish 缺 stapler validate 硬门(须验 offline pkg 本体)"; S134_BAD=1; }
grep -q 'HOROSA_ALLOW_UNSTAPLED' "${S134_PUB}" || { bad "[134] publish 装订门缺逃生阀(内网测试 release 需要)"; S134_BAD=1; }
grep -q 'UNSIGNED-DEV-BUILD.txt' "${S134_PUB}" || { bad "[134] publish 未检查 ad-hoc 标记文件"; S134_BAD=1; }
# 顺序锚:装订门必须先于上传(资产一旦上传,门就形同虚设)
S134_GATE_LN="$(grep -n 'xcrun stapler validate "${DIST_ROOT}' "${S134_PUB}" | head -1 | cut -d: -f1 || true)"
S134_UP_LN="$(grep -n '^upload_asset()' "${S134_PUB}" | head -1 | cut -d: -f1 || true)"
{ [ -n "${S134_GATE_LN}" ] && [ -n "${S134_UP_LN}" ] && [ "${S134_GATE_LN}" -lt "${S134_UP_LN}" ]; } || { bad "[134] 装订门(${S134_GATE_LN:-?})未先于上传函数(${S134_UP_LN:-?})"; S134_BAD=1; }
[ "${S134_BAD}" = "0" ] && ok "[134] 签名产物防误发在位(标记双臂/装订门/逃生阀/门先于上传)"

# ---- [135] AI段勾选「所见即所得」(四症=清空按钮死/勾了不纳入/挂载与导出分叉/五技法强推段
#      取消不掉。根因:①空数组被当「未自定义」→ effective 回 preset 全勾;②导出主链运行时强推段
#      而挂载封装不强推 → 两链分叉;③事盘/命盘源上下文(full 模式)全文裸发不过段;④planetInfo
#      开关仅导出消费。防线:v45 语义(空数组=显式全清)+迁移(尸块删键+强推 union 显式化)+
#      源层读出后过滤+planetInfo 挂载消费+金标。铁律:「设置面显示什么,导出与挂载就吃什么」。) ----
S135_BAD=0
S135_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
echo "[135] AI段勾选所见即所得(空数组=显式全清+强推迁移+源层过滤)"
grep -q "hasCustom" "${S135_UI}/src/utils/aiExport.js" 2>/dev/null || { bad "[135] effective 缺 hasCustom 空数组语义(清空按钮回潮死)"; S135_BAD=1; }
grep -q "AI_EXPORT_FORCED_INCLUDE_SECTIONS" "${S135_UI}/src/utils/aiExport.js" 2>/dev/null || { bad "[135] 缺强推段迁移表(老用户强推段将静默丢失)"; S135_BAD=1; }
grep -q "picked.push('六壬大格'" "${S135_UI}/src/utils/aiExport.js" 2>/dev/null && { bad "[135] 导出主链运行时强推段回潮(用户取消不掉事故复发)"; S135_BAD=1; }
grep -q "filterSourceContextBySections" "${S135_UI}/src/utils/aiAnalysisContext.js" 2>/dev/null || { bad "[135] 源上下文段过滤缺失(事盘全文裸发回潮)"; S135_BAD=1; }
grep -q "exportSettingKeyForSnapshotModule" "${S135_UI}/src/utils/aiAnalysisContext.js" 2>/dev/null || { bad "[135] 源层缺 module→设置键反查(六爻 guazhan 打不中设置)"; S135_BAD=1; }
grep -q "applyPlanetInfoFilterByContext" "${S135_UI}/src/utils/aiAnalysisContext.js" 2>/dev/null || { bad "[135] 挂载链缺星曜后天信息消费(开关静默失效回潮)"; S135_BAD=1; }
[ -f "${S135_UI}/src/utils/__tests__/aiExportSectionSemantics.test.js" ] || { bad "[135] 缺段勾选语义金标"; S135_BAD=1; }
[ "${S135_BAD}" = "0" ] && ok "[135] v45 空数组语义+强推迁移+源层过滤+planetInfo 挂载消费+金标 全在位"

# ---- [136] 在线地图(高德)CSP 白名单完整性(FL 装机专发类) ----
#   ★真表面 = main.rs 的 tiny_http 响应头 CSP,非 tauri.conf.json!主界面走本机静态服务器
#   (http://127.0.0.1:PORT)加载,不走 tauri:// 协议 → tauri.conf 的 csp 管不到主界面(地图在此)。
#   病根一(host)——main.rs CSP 的 script/style/img/connect 未放行 AMap 域(*.amap.com/*.autonavi.com)。
#   病根二(eval/wasm)——AMap 2.0 运行时用 eval()+WebAssembly.compile,须 script-src 含 'unsafe-eval'
#   (同时放行 eval 与 wasm)+ worker-src 含 blob:(瓦片解码走 blob worker)。
#   macOS WKWebView 严格执行响应头 CSP → 缺任一 = 地图白屏;preview 无 CSP、Windows WebView2 宽松
#   → dev/Win 假绿,唯 Mac 装机版暴露。iframe 实证:加齐后 map-COMPLETE 零违规。与 mapCsp.test.js 双护。
S136_BAD=0
S136_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S136_CONF="${INSTALLER_ROOT}/src-tauri/tauri.conf.json"
S136_MAINRS="${INSTALLER_ROOT}/src-tauri/src/main.rs"
echo "[136] 高德地图 CSP 白名单完整(真表面=main.rs tiny_http 响应头)"
if grep -q "amap-jsapi-loader" "${S136_UI}/src/components/amap/MapV2.js" 2>/dev/null \
   || grep -q "AMapKey" "${S136_UI}/src/utils/constants.js" 2>/dev/null; then
  S136_RES="$(python3 - "${S136_MAINRS}" "${S136_CONF}" <<'PY'
import json, re, sys
def parse(csp):
    dirs = {}
    for seg in csp.split(";"):
        seg = seg.strip()
        if seg:
            p = seg.split(); dirs[p[0]] = p[1:]
    return dirs
def eff(dirs, d): return dirs.get(d, dirs.get("default-src", []))
def allows(sources, host):
    for s in sources:
        if s == "https://" + host: return True
        if s.startswith("https://*."):
            suf = s[len("https://*"):]
            if host.endswith(suf) and host != suf[1:]: return True
    return False
def check(csp, label):
    dirs = parse(csp); probs = []
    for h in ("webapi.amap.com", "restapi.amap.com", "jsapi.amap.com"):
        for d in ("script-src", "connect-src", "img-src"):
            if not allows(eff(dirs, d), h): probs.append("%s:%s 未放行 %s" % (label, d, h))
    if "blob:" not in eff(dirs, "worker-src"): probs.append("%s:worker-src 缺 blob:" % label)
    if "'unsafe-eval'" not in eff(dirs, "script-src"): probs.append("%s:script-src 缺 'unsafe-eval'(eval+wasm→白屏)" % label)
    return probs
problems = []
try:
    src = open(sys.argv[1], encoding="utf-8").read()
    m = re.search(r'&b"(default-src[^"]*)"', src)
    if not m: problems.append("main.rs 找不到 tiny_http CSP 字节串(地图真表面无法校验)")
    else: problems += check(m.group(1), "main.rs主界面")
except OSError:
    problems.append("main.rs 读取失败(地图真表面无法校验)")
try:
    csp2 = json.load(open(sys.argv[2], encoding="utf-8")).get("app", {}).get("security", {}).get("csp", "")
    problems += check(csp2, "tauri.conf")
except OSError:
    problems.append("tauri.conf.json 读取失败")
if problems: sys.stdout.write("; ".join(problems))
PY
)"
  if [ -n "${S136_RES}" ]; then bad "[136] Mac 装机版地图将白屏 → CSP 缺放行: ${S136_RES}"; S136_BAD=1; fi
  grep -q "hasMapConsent" "${S136_UI}/src/components/amap/MapV2.js" 2>/dev/null || { bad "[136] 地图一次性同意闸丢失(放行外部域后须仍受同意 gate)"; S136_BAD=1; }
fi
[ "${S136_BAD}" = "0" ] && ok "[136] 高德地图 CSP(main.rs真表面+launcher:script/connect/img/worker-blob/unsafe-eval)白名单齐 + 同意闸在位"

# ---- [137] 可选中文字 PDF 矢量字体必须 TrueType(glyf) 整嵌 —— 防 CJK 乱码回归(2026-07-14 FL) ----
#   血泪根因:内嵌 .otf(CFF)经 pdf-lib 产出结构非法内嵌字体文件 → macOS Preview/poppler 拒渲染 =
#   整份中文乱码(pdffonts 报 "Embedded font file may be invalid");且 fontkit subset:true 静默丢字形。
#   修法=字体 CFF→TrueType(glyf,cu2qu)+ embedFont subset:false 整嵌。守卫与 aiExportPdfVector.test.js 双护。
S137_BAD=0
S137_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S137_ENGINE="${S137_UI}/src/utils/aiExportPdfVector.js"
S137_FONT="${S137_UI}/public/fonts/HorosaCJK-subset.ttf"
echo "[137] 矢量 PDF 字体 TrueType 整嵌(防 CJK 乱码回归)"
if [ -f "${S137_ENGINE}" ]; then
  if [ ! -f "${S137_FONT}" ]; then
    bad "[137] 缺 TrueType 字体 HorosaCJK-subset.ttf(引擎取不到→矢量 PDF 失败)"; S137_BAD=1
  else
    S137_TAG="$(python3 -c "import sys;sys.stdout.write(open('${S137_FONT}','rb').read(4).decode('latin1'))" 2>/dev/null || echo '??')"
    [ "${S137_TAG}" = "OTTO" ] && { bad "[137] 字体是 CFF/OTF('OTTO')→pdf-lib 产非法内嵌=乱码;须转 TrueType(glyf)"; S137_BAD=1; }
  fi
  grep -q "HorosaCJK-subset.ttf" "${S137_ENGINE}" || { bad "[137] 引擎 FONT_URLS 未指向 .ttf"; S137_BAD=1; }
  grep -q "subset: false" "${S137_ENGINE}" || { bad "[137] 引擎 embedFont 未用 subset:false(subset:true 会静默丢字形)"; S137_BAD=1; }
  grep -q "embedFont(fontBytes, { subset: true })" "${S137_ENGINE}" && { bad "[137] 引擎仍试 subset:true(丢字形回潮)"; S137_BAD=1; }
  [ -f "${S137_UI}/public/fonts/HorosaCJK-subset.otf" ] && { bad "[137] 旧 CFF 字体 .otf 仍在(乱码源,应删)"; S137_BAD=1; }
  grep -q "fontSfntKind" "${S137_UI}/src/utils/__tests__/aiExportPdfVector.test.js" 2>/dev/null || { bad "[137] aiExportPdfVector.test 缺字体乱码守卫(fontSfntKind 双锚)"; S137_BAD=1; }
fi
[ "${S137_BAD}" = "0" ] && ok "[137] 矢量 PDF 字体 TrueType(glyf)整嵌 + 旧 .otf 已除 + jest 双锚守卫在位"

# ---- [138] 导出截图星符号字体内嵌 —— 防「A/B/C/D 裸字母不成 glyph」回归(2026-07-14 FL) ----
#   血泪根因:PDF/Word 导出的图盘截图走 html-to-image,旧代码 skipFonts:true 跳过所有 @font-face →
#   星符号字体(字母→glyph 映射)不内嵌 → canvas 回退裸字母 A/B/C/D…。
#   修法:buildScreenshotFontEmbedCSS 预取同源小字体 base64 内联成 fontEmbedCSS(避 WKWebView 全量扫 hang),
#   URL 必经 new URL(raw, sheet.href) 相对样式表解析(相对页面会取 SPA 兜底 index.html→字体损坏),
#   magic-byte 挡 HTML 兜底。守卫与 pageScreenshot.test.js 双护。
S138_BAD=0
S138_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S138_PS="${S138_UI}/src/utils/pageScreenshot.js"
echo "[138] 导出截图星符号字体内嵌(防裸字母回归)"
if [ -f "${S138_PS}" ]; then
  grep -q "buildScreenshotFontEmbedCSS" "${S138_PS}" || { bad "[138] 缺 buildScreenshotFontEmbedCSS(截图不内嵌符号字体=裸字母)"; S138_BAD=1; }
  grep -q "fontEmbedCSS" "${S138_PS}" || { bad "[138] toCanvas 未用 fontEmbedCSS(回到 skipFonts=裸字母)"; S138_BAD=1; }
  grep -q "new URL(m\[1\], sheets\[s\].href" "${S138_PS}" || { bad "[138] 字体 URL 未相对样式表解析(相对页面会取 SPA 兜底 HTML→字体损坏)"; S138_BAD=1; }
  grep -q "wOF2" "${S138_PS}" || { bad "[138] 缺 magic-byte 校验(不挡 HTML 兜底=把 index.html 当字体)"; S138_BAD=1; }
  grep -q "buildScreenshotFontEmbedCSS" "${S138_UI}/src/utils/__tests__/pageScreenshot.test.js" 2>/dev/null || { bad "[138] pageScreenshot.test 缺截图字体守卫"; S138_BAD=1; }
fi
[ "${S138_BAD}" = "0" ] && ok "[138] 截图 fontEmbedCSS 内嵌(符号字体成 glyph)+ URL 相对样式表解析 + magic 挡兜底 + jest 守卫在位"

# ── [139] 离线安装链真装门(渲染占位符/内嵌档 gz/净化 PATH 可解/成品 pkg e2e stamp) ──
#   守 2026-07-20 双案:①模板占位符 __OFFLINE_RUNTIME_ASSET__ 渲染表漏键 → postinstall 找不到
#   内嵌档 → 降级 pending;②内嵌 .tar.zst 而 macOS 系统 tar(libarchive 无 zstd 滤器)在
#   PKInstallSandbox 净化 PATH 下无第三方 zstd 兜底 → 解压必败 → 降级;两案 App 首启都读到
#   旧版缓存报「版本不符」。全链自检此前只测「runtime 归档能启动」,从未测「成品 .pkg 的
#   postinstall 在安装沙盒等价环境下真装成功」—— 本哨兵 + build 内联断言 + e2e 门三层补死。
echo "[139] 离线安装链真装门"
S139_BAD=0
S139_BUILD="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh"
S139_RD="${REPO_ROOT}/Horosa_Desktop_Installer/build/installer-scripts-rendered-offline"
S139_STAMP="${REPO_ROOT}/Horosa_Desktop_Installer/build/offline-pkg-e2e.stamp"
grep -q 'HOROSA_OFFLINE_ZSTD:-0' "${S139_BUILD}" 2>/dev/null || { bad "[139] 🔴 build 未默认 gz 内嵌(HOROSA_OFFLINE_ZSTD:-0)——zst 在安装沙盒必败"; S139_BAD=1; }
grep -q 'env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin /usr/bin/tar -tf' "${S139_BUILD}" 2>/dev/null || { bad "[139] 🔴 build 缺净化 PATH 内嵌档探测"; S139_BAD=1; }
grep -q '渲染后硬断言' "${S139_BUILD}" 2>/dev/null || { bad "[139] 🔴 build 缺渲染后硬断言块(占位符/档在位/可解)"; S139_BAD=1; }
grep -q 'verify_offline_pkg_install_e2e.sh' "${S139_BUILD}" 2>/dev/null || { bad "[139] 🔴 build 未接离线 pkg 真装 e2e 门"; S139_BAD=1; }
[ -x "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_offline_pkg_install_e2e.sh" ] || { bad "[139] 缺 verify_offline_pkg_install_e2e.sh"; S139_BAD=1; }
if [ -f "${S139_RD}/postinstall" ]; then
  grep -qE '__[A-Z_]+__' "${S139_RD}/postinstall" && { bad "[139] 🔴 rendered postinstall 残留未替换占位符"; S139_BAD=1; }
  S139_AN="$(sed -n 's/^ARCHIVE_NAME="\(.*\)"$/\1/p' "${S139_RD}/postinstall" | head -n 1)"
  if [ -z "${S139_AN}" ] || [ ! -s "${S139_RD}/${S139_AN}" ]; then
    bad "[139] 🔴 rendered Scripts 缺内嵌档(${S139_AN:-<空>})"; S139_BAD=1
  elif ! env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin /usr/bin/tar -tf "${S139_RD}/${S139_AN}" >/dev/null 2>&1; then
    bad "[139] 🔴 rendered 内嵌档净化 PATH(≈PKInstallSandbox)不可解——系统 tar 无此压缩滤器"; S139_BAD=1
  fi
fi
S139_PKG_NAME="$(python3 -c "import json;print(json.load(open('${REPO_ROOT}/Horosa_Desktop_Installer/config/release_config.json'))['desktopOfflinePkgName'])" 2>/dev/null || true)"
S139_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/dist/${S139_PKG_NAME}"
if [ -n "${S139_PKG_NAME}" ] && [ -s "${S139_PKG}" ]; then
  if [ ! -f "${S139_STAMP}" ]; then
    bad "[139] 🔴 有离线 pkg 但缺真装 e2e stamp(HOROSA_SKIP_PKG_E2E 跳过未补跑?)"; S139_BAD=1
  else
    S139_SHA="$(shasum -a 256 "${S139_PKG}" | awk '{print $1}')"
    S139_MATCH="$(awk -F'\t' -v sha="${S139_SHA}" '$1=="OK" && $2==sha {print "MATCH"}' "${S139_STAMP}" | head -n 1)"
    [ "${S139_MATCH}" = "MATCH" ] || { bad "[139] 🔴 e2e stamp 非 OK 或与成品 pkg sha 不符——对当前 pkg 补跑 verify_offline_pkg_install_e2e.sh"; S139_BAD=1; }
  fi
fi
[ "${S139_BAD}" = "0" ] && ok "[139] 离线安装链真装门全在位(gz 默认/净化探测/渲染断言/e2e stamp 绑定成品)"

# ── [140] R3 性能宗师轮防回归(kentang 缓存/选步长预取/覆盖矩阵零 todo/预置信任/warmup 并行/惰性工厂/让路)──
echo "[140] R3 性能宗师轮防回归"
S140_BAD=0
S140_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S140_KC="${S140_UI}/utils/kentangCache.js"
[ -s "${S140_KC}" ] || { bad "[140] 缺 kentangCache.js"; S140_BAD=1; }
grep -aq 'kt\.\${pathOf(url)}' "${S140_KC}" 2>/dev/null || { bad "[140] 🔴 kentangCache 键未去端口化"; S140_BAD=1; }
grep -aq "obj.ResultCode !== undefined && obj.ResultCode !== 0" "${S140_KC}" 2>/dev/null || { bad "[140] 🔴 载荷守卫缺位"; S140_BAD=1; }
grep -aq "modulePolicy(moduleKey) !== 'deterministic'" "${S140_KC}" 2>/dev/null || { bad "[140] 🔴 预取纪律锚缺位"; S140_BAD=1; }
S140_RAW="$(grep -rn "fetchChartWithRetry(" "${S140_UI}/components" "${S140_UI}/services" 2>/dev/null | grep -av "kentangCache" | grep -av "__tests__" || true)"
[ -z "${S140_RAW}" ] || { bad "[140] 🔴 存在绕过缓存壳的 fetchChartWithRetry 裸调用"; S140_BAD=1; }
grep -aq "fireStepSelectPrefetch(val)" "${S140_UI}/components/comp/DateTimeSelector.js" 2>/dev/null || { bad "[140] 🔴 选步长触发点缺位"; S140_BAD=1; }
grep -aq "stepSelectPrefetch=" "${S140_UI}/components/astro/PlusMinusTime.js" 2>/dev/null || { bad "[140] 🔴 PlusMinusTime 未挂全链 prop"; S140_BAD=1; }
grep -aq "registerStepSelectHandler((unit)" "${S140_UI}/models/astro.js" 2>/dev/null || { bad "[140] 🔴 选步长处理器未注册"; S140_BAD=1; }
S140_TODO="$(grep -ac ": 'todo'" "${S140_UI}/utils/perfCoverageManifest.js" 2>/dev/null || true)"
[ "${S140_TODO:-0}" = "0" ] || { bad "[140] 🔴 perfCoverage 矩阵仍有 ${S140_TODO} 个 todo"; S140_BAD=1; }
S140_MAIN="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
grep -q -- "--horosa-preseed-health" "${S140_MAIN}" 2>/dev/null || { bad "[140] 🔴 缺预置信任子命令"; S140_BAD=1; }
grep -q -- "--horosa-preseed-health" "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template" 2>/dev/null || { bad "[140] 🔴 postinstall 未调用预置信任"; S140_BAD=1; }
grep -q "_warmup_stage_kentang" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" 2>/dev/null || { bad "[140] 🔴 warmup 三段化缺位"; S140_BAD=1; }
grep -q "class LazyCacheFactory" "${REPO_ROOT}/Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/types/cache/LazyCacheFactory.java" 2>/dev/null || { bad "[140] 🔴 缺 LazyCacheFactory"; S140_BAD=1; }
S140_LZ="$(grep -c -- "-Dhorosa.cache.lazyinit=true" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" 2>/dev/null || true)"
[ "${S140_LZ:-0}" = "3" ] || { bad "[140] 🔴 惰性属性注入应恰 3 处,现 ${S140_LZ}"; S140_BAD=1; }
grep -q "HOROSA_WARM_MIN_ASYNC" "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" 2>/dev/null || { bad "[140] 🔴 min-warmup 让路开关缺位"; S140_BAD=1; }
[ "${S140_BAD}" = "0" ] && ok "[140] R3 性能宗师轮资产全在位"

# [62] 壳缩放链四层病理锁 —— 2026-07-31 真机彻查定案(主限天球时间轴被滚上去/底部露白):
#   ①layouts/app.js 内联 100vh 与 clientHeight 域劈叉(缩放≠1 差出可平移空间);
#   ②缩放注入走 localStorage 跨 origin 断链——唯一确定性通道=emit_ready 的 URL query
#     (shellZoom)+ init script 挂 __HOROSA_APPLY_SHELL_ZOOM(每 document 必挂);
#   ③取证探针(FORENSIC-TEMP)绝不入发版;④jest 守卫套件在位。
echo "[62] 壳缩放链四层病理锁(URL query 通道 + 100vh 禁令 + 探针剥离 + jest 守卫)"
S62_BAD=0
S62_MAIN_RS="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S62_APP_JS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.js"
S62_GUARD="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/shellZoomGuard.test.js"
if grep -q "FORENSIC-TEMP" "${S62_MAIN_RS}"; then
    S62_BAD=1; bad "[62]③ main.rs 残留 FORENSIC-TEMP 取证探针 —— 硬编码缩放/采样代码禁入发版"
fi
if ! grep -q "shellZoom={zoom}" "${S62_MAIN_RS}"; then
    S62_BAD=1; bad "[62]② emit_ready 缺 shellZoom URL query 注入 —— 缩放回退到跨 origin 断链的 localStorage 通道"
fi
if ! grep -q "__HOROSA_APPLY_SHELL_ZOOM" "${S62_MAIN_RS}"; then
    S62_BAD=1; bad "[62]② init script 缺 __HOROSA_APPLY_SHELL_ZOOM —— 导航后缩放应用函数丢失"
fi
if sed -e 's://.*$::' "${S62_APP_JS}" | grep -q "100vh"; then
    S62_BAD=1; bad "[62]① layouts/app.js 内联 100vh 回归 —— 域劈叉,缩放≠1 时底空+可平移空间复发"
fi
if [ ! -f "${S62_GUARD}" ]; then
    S62_BAD=1; bad "[62]④ jest 守卫 shellZoomGuard.test.js 缺失"
fi
[ "${S62_BAD}" = "0" ] && ok "[62] 壳缩放链四层病理锁全绿"

# [63] marker 投影悬空锁 —— 2026-07-31 辅盘干净安装必炸实案制度化:marker 块内 import
#   绑定名在块外仍被引用,strip 后成未定义自由变量 → 模块顶层 ReferenceError;首爆被预载
#   catch 吞 + webpack 中毒缓存 → 二次点击伪装成「Lazy chunk resolved empty」。
#   本仓为投影侧:①全仓残留 marker 的悬空扫描;②jest lazyTargetsSmoke(全技法模块可
#   require 且有默认导出——投影后任何顶层炸在 jest 即红)。
echo "[63] marker 投影悬空锁(全仓扫描 + lazy smoke 守卫)"
S63_BAD=0
S63_SCRIPT="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/check_marker_projection.py"
if [ ! -f "${S63_SCRIPT}" ]; then
    S63_BAD=1; bad "[63] 缺 check_marker_projection.py"
else
    S63_OUT=$(python3 "${S63_SCRIPT}" "${REPO_ROOT}/Horosa-Web/astrostudyui/src" 2>&1)
    if [ -n "${S63_OUT}" ]; then
        S63_BAD=1; bad "[63] 投影悬空引用: ${S63_OUT}"
    fi
fi
[ -f "${REPO_ROOT}/Horosa-Web/astrostudyui/src/test/lazyTargetsSmoke.test.js" ] || { S63_BAD=1; bad "[63] 缺 jest lazyTargetsSmoke 守卫"; }
[ "${S63_BAD}" = "0" ] && ok "[63] marker 投影悬空锁全绿"

# [64] 干支年基准 / 性别接线 / AI 输出预算键 三合一锁（与 private[179] 同判据）：
#   ①术数流年 base 必须是干支年(立春前出生者用公历年会整体错一年);
#   ②左栏性别下拉须宿主下发 + 组件 props 优先(曾恒读命盘性别=死开关);
#   ③AI 输出预算键走单源 maxTokensKeyForModel + 后端代际归一(gpt-5+ 不收 max_tokens)。
echo "[64] 干支年基准 + 性别接线 + AI 预算键代际(三合一)"
S64_BAD=0
S64_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S64_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
[ -f "${S64_UI}/utils/ganzhiYearBase.js" ] || { S64_BAD=1; bad "[64]① 缺干支年基准单源"; }
for F in components/shusuan/HeLuoMain.js components/shusuan/CanPingMain.js utils/aiAnalysisContext.js; do
    grep -aq "ganzhiYearBase(" "${S64_UI}/${F}" 2>/dev/null || { S64_BAD=1; bad "[64]① ${F} 未经 ganzhiYearBase"; }
done
grep -aq "gender={this.state.gender}" "${S64_UI}/components/kinastro/KinAstroMain.js" 2>/dev/null || { S64_BAD=1; bad "[64]② 宿主未下发 gender"; }
for F in components/shusuan/CanPingMain.js components/shusuan/ZhengChuanMain.js components/shusuan/HeLuoMain.js; do
    grep -aq "this.props.gender !== undefined" "${S64_UI}/${F}" 2>/dev/null || { S64_BAD=1; bad "[64]② ${F} 未 props.gender 优先"; }
done
grep -aq "maxTokensKeyForModel" "${S64_UI}/utils/aiAnalysisProviders.js" 2>/dev/null || { S64_BAD=1; bad "[64]③ 缺 AI 预算键单源"; }
grep -aq "normalizeOpenAIMaxTokensKey" "${S64_JAVA}" 2>/dev/null || { S64_BAD=1; bad "[64]③ Java 代理缺代际归一"; }
[ -f "${S64_UI}/utils/__tests__/ganzhiYearBaseGuard.test.js" ] || { S64_BAD=1; bad "[64] 缺 jest 金标"; }
[ "${S64_BAD}" = "0" ] && ok "[64] 三合一锁全绿"

echo "[180] 构建产物路径脱敏(构建机用户名与仓目录名不得进 bundle)"
# 病灶(2026-08-01 v3.6.1 保密复查抓到,存量):umi 的插件注册把运行时文件的**绝对路径**
# 原样写进 bundle —— register({apply:a, path:"/Users/<用户名>/Desktop/<仓目录名>/.../runtime.tsx"}),
# 于是发布产物里同时躺着构建机用户名(PII)与本地仓目录名。禁词表扫源码扫不到它(产物不在源码树),
# 人工逐条读 diff 也看不见(产物不入 git),只有直接 grep 打包产物才现形。
S180_BAD=0
S180_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
[ -f "${S180_UI}/scripts/scrub-build-paths.js" ] || { S180_BAD=1; bad "[180] 缺脱敏脚本 scripts/scrub-build-paths.js"; }
# ① 两条构建链都必须接:漏一条 → 那个产物照样带路径
for S180_K in '"build":' '"build:file":'; do
  S180_LINE="$(grep -a "${S180_K}" "${S180_UI}/package.json" 2>/dev/null | head -1)"
  printf '%s' "${S180_LINE}" | grep -aq "scrub-build-paths" \
    || { S180_BAD=1; bad "[180] package.json ${S180_K} 未接脱敏步骤 —— 该产物会带构建机路径"; }
  # ② 顺序:必须在 write-build-info 之前(脱敏改文件内容,后写指纹才对得上产物)
  printf '%s' "${S180_LINE}" | awk '{ i=index($0,"scrub-build-paths"); j=index($0,"write-build-info"); exit !(i>0 && j>0 && i<j) }' \
    || { S180_BAD=1; bad "[180] ${S180_K} 脱敏步骤必须排在 write-build-info 之前(否则指纹与产物不符)"; }
done
# ③ 终判据:直接 grep 现有产物,残留即红(不信脚本"跑过了",只认产物本身)
for S180_D in dist dist-file; do
  if [ -d "${S180_UI}/${S180_D}" ]; then
    if grep -rlaE '/(Users|home)/[A-Za-z0-9._-]+/' "${S180_UI}/${S180_D}" --include=*.js --include=*.css --include=*.html 2>/dev/null | head -1 | grep -q .; then
      S180_BAD=1; bad "[180] ${S180_D} 产物内仍有构建机绝对路径 —— 重跑 npm run build/build:file"
    fi
  fi
done
[ "${S180_BAD}" = "0" ] && ok "[180] 产物路径脱敏链完好(脚本在位·两链已接·顺序正确·产物零残留)"

echo "[181] 重引擎按需加载锁(页面不得静态引 3D/图表引擎)"
# 病灶(2026-08-01 用户实报「进入星运台卡死」):页面组件**静态** import 了重可视化组件,
# webpack 遂把整个引擎变成该页 chunk 的**同步依赖** —— 用户只要进这个页,模块求值期就得先
# 解析完整个引擎,哪怕他从不打开那个 3D 子页签。实报那次星运页静态引 AstroPDSphere→
# PDSphereEngine→three(vendors-gl 862KB+引擎 90KB),而该页默认停在「主限法」表格、
# 二十多个子页签里只有一个用得着 3D;配置一般的机器足以让主线程长时间无响应。同族共三处
# (星运/节气/玄史),玄史那处引的是 echarts(1291KB,比 three 还大)。
# 四道判据:单一真值源在位 → 三处接线正确 → 主锁测试在位 → **直接扫产物**(不信源码,只认产物)。
S181_BAD=0
S181_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
# ① 懒边界单一真值源(空模块自愈住这里 —— 组件内各写一份必然丢掉它,那是 v3.6.0 的坑)
S181_LB="${S181_UI}/src/utils/lazyBoundary.js"
if [ ! -f "${S181_LB}" ]; then
  S181_BAD=1; bad "[181] 缺懒边界单一真值源 utils/lazyBoundary.js"
else
  grep -aq "export function makeLazyBoundary" "${S181_LB}" || { S181_BAD=1; bad "[181] lazyBoundary 未导出 makeLazyBoundary"; }
  grep -aq "Lazy chunk resolved empty" "${S181_LB}" || { S181_BAD=1; bad "[181] lazyBoundary 丢了空模块自愈(坏结果进 React.lazy 缓存会被永久钉死)"; }
fi
# ② 三处宿主页不得静态 import 重组件(剥注释后再判 —— 注释里提到不算)
S181_CHECK(){   # $1=文件 $2=被禁的静态 import 正则 $3=人话
  local F="${S181_UI}/src/components/$1"
  [ -f "${F}" ] || { S181_BAD=1; bad "[181] 缺文件 $1"; return; }
  local CODE; CODE=$(sed -E 's://.*$::' "${F}" 2>/dev/null)
  if printf '%s' "${CODE}" | grep -qE "$2"; then
    S181_BAD=1; bad "[181] $3 —— 静态 import 会把引擎拖回本页 chunk,进该页即须解析整个引擎"
  fi
}
S181_CHECK "direction/AstroDirectMain.js"   "^import AstroPDSphere from"    "星运页又静态引了主限天球"
S181_CHECK "jieqi/JieQiChartsMain.js"       "^import AstroChartMain3D from" "节气页又静态引了 3D 盘"
S181_CHECK "xuanshi/XuanShiMain.js"         "^import (XuanShiCelestial|XuanShiMap) from" "玄史页又静态引了 echarts 宿主"
S181_CHECK "astro3d/AstroChartMain3D.js"    "^import AstroPDSphere from"    "3D 星盘页又静态引了主限天球(那条分支恒 false,纯拖累)"
# ③ 主锁(AST import 图遍历)在位 —— 它才是覆盖「未来任意新增页面」的那一道
[ -f "${S181_UI}/src/utils/__tests__/heavyEngineImportGraph.test.js" ] \
  || { S181_BAD=1; bad "[181] 缺主锁 heavyEngineImportGraph.test.js(AST 图遍历,自动覆盖新增页面)"; }
grep -aq "重引擎不得与页面同 chunk" "${S181_UI}/scripts/check-chunk-dup.js" 2>/dev/null \
  || { S181_BAD=1; bad "[181] check-chunk-dup 缺产物层判据(锁 C)"; }
# ④ 终判据:直接扫产物 —— 任何 async chunk 不得同时含引擎标记与页面懒边界
#    (vendors 前缀是引擎独占 chunk,本就该含引擎,豁免)
for S181_D in dist dist-file; do
  [ -d "${S181_UI}/${S181_D}" ] || continue
  for S181_F in "${S181_UI}/${S181_D}"/*.async.js; do
    [ -f "${S181_F}" ] || continue
    case "$(basename "${S181_F}")" in vendors-*|vendors~*) continue ;; esac
    if grep -aq "WebGLRenderer" "${S181_F}" 2>/dev/null && grep -aq "LazyBoundary" "${S181_F}" 2>/dev/null; then
      S181_BAD=1; bad "[181] ${S181_D}/$(basename "${S181_F}") 同时含 three 与页面懒边界 —— 引擎被拖进页面 chunk"
    fi
  done
done
# ⑤ 首屏批次判据:引擎不得与「基础设施库」编在同一个 cacheGroup
#    ④ 只查「引擎与页面同 chunk」,查不到这条隐形通道:引擎跟一个首屏必需的基础设施库
#    (d3——星盘 SVG 绘制用,全仓 101 个文件在用)共处同一个 vendors chunk → 首屏把整包
#    拉走,引擎虽规规矩矩待在 vendors 里(④ 全绿)、页面也确实懒加载了(①②③ 全绿),
#    用户照样开机就得下载解析它。实锤:原 vendors-viz 1228KB 含 echarts,在首屏批次里。
#    拆成 vendors-d3(129KB 首屏)+ vendors-echarts(1132KB 只随玄史两子页)后首屏净省 1.1MB。
grep -aq "vendorsD3" "${S181_UI}/.umirc.js" 2>/dev/null \
  && grep -aq "name: 'vendors-echarts'" "${S181_UI}/.umirc.js" 2>/dev/null \
  || { S181_BAD=1; bad "[181] .umirc.js 的 echarts 与 d3 未分组 —— 图表引擎会被首屏必需的 d3 捎带下载,玄史页懒加载等于白做"; }
grep -aq "首屏批次不得含重引擎" "${S181_UI}/scripts/check-chunk-dup.js" 2>/dev/null \
  || { S181_BAD=1; bad "[181] check-chunk-dup 缺首屏批次判据(锁 E)"; }
#    终判据同样只认产物,但**不在这里重写一遍**:minify 后是单行巨串,shell 正则解析
#    极易错配成虚绿(本条初版就栽在这)。直接跑 check-chunk-dup.js 本体 —— 它已就
#    「首屏批次无引擎」做过正反双验(病态配置下 exit 1 实测),复用比重写可靠。
if command -v node >/dev/null 2>&1; then
  for S181_D in dist dist-file; do
    [ -d "${S181_UI}/${S181_D}" ] || continue
    S181_OUT="$(cd "${S181_UI}" && node scripts/check-chunk-dup.js "${S181_D}" 2>&1)" || {
      S181_BAD=1; bad "[181] ${S181_D}: check-chunk-dup 未过 —— $(printf '%s' "${S181_OUT}" | head -2 | tr '\n' ' ')"
    }
    printf '%s' "${S181_OUT}" | grep -q "首屏批次\[" \
      || { S181_BAD=1; bad "[181] ${S181_D}: check-chunk-dup 没打出首屏批次 —— 该判据未真正执行(拒绝虚绿)"; }
  done
else
  S181_BAD=1; bad "[181] 找不到 node,首屏批次判据无法执行 —— 判据失效即红,不许静默放行"
fi
[ "${S181_BAD}" = "0" ] && ok "[181] 重引擎按需加载锁全绿(单源在位·四处接线·主锁与产物锁在位·产物零同居·首屏批次无引擎)"

echo "[182] 部件包可复现(内容不变 ⇒ sha 不变;否则增量复用恒 0)"
# 🔴 2026-08-01 实测抓出:增量更新的复用判据是「本地 lock 的部件 sha == 新 manifest 的部件 sha」
# (plan_component_diff)。打包若不可复现,内容一字未改的稳定部件也会 sha 漂移 → 判为「变了」
# → 每版每个用户全量重下,I4 不变量(稳定部件不得变)恒不成立。
# 实锤:上一版已装的 ephe-data 与本版新包逐文件内容完全一致(158 档同摘要),包 sha 却不同;
# 七部件无一复用,reusePct=0、downloadBytes=690MB。
# 两个与内容无关的漂移源:① gzip 头 MTIME=打包时刻;② 目录条目 mtime 被 staging 拷贝刷新。
S182_BAD=0
S182_PK="${INSTALLER_ROOT}/scripts/package_runtime_payload.sh"
# ① 实现在位:gzip -n(归零头时间戳)+ 目录 mtime 归一
grep -aq "'/usr/bin/gzip', '-n'" "${S182_PK}" 2>/dev/null \
  || { S182_BAD=1; bad "[182] 部件打包未走 gzip -n —— gzip 头会写入打包时刻,sha 每版必漂,增量复用恒 0"; }
grep -aq "def normalize_dir_mtimes" "${S182_PK}" 2>/dev/null \
  && grep -aq "normalize_dir_mtimes(stage)" "${S182_PK}" 2>/dev/null \
  || { S182_BAD=1; bad "[182] 部件打包前未归一目录 mtime —— staging 拷贝会刷新目录时间戳,sha 照样漂"; }
# ② 反向锚:旧写法(-czf 一步压)不得回潮
grep -aqE "'-czf', str\(out\)" "${S182_PK}" 2>/dev/null \
  && { S182_BAD=1; bad "[182] 部件打包又出现 -czf 一步压 —— 那正是把打包时刻写进 gzip 头的写法"; }
# ③ 终判据:直接扫**真产物**的 gzip 头 MTIME 字段,必须为 0(不信源码,只认产物)
S182_CD="${INSTALLER_ROOT}/dist/components"
if [ -d "${S182_CD}" ]; then
  S182_N=0
  for S182_F in "${S182_CD}"/horosa-comp-*.tar.gz; do
    [ -f "${S182_F}" ] || continue
    S182_N=$((S182_N+1))
    S182_MT="$(python3 -c "
import struct,sys
h=open(sys.argv[1],'rb').read(10)
print(struct.unpack('<I', h[4:8])[0] if len(h)>=8 else -1)
" "${S182_F}" 2>/dev/null || echo -1)"
    [ "${S182_MT}" = "0" ] || { S182_BAD=1; bad "[182] $(basename "${S182_F}") 的 gzip 头 MTIME=${S182_MT}(应为 0)—— 该包 sha 与内容无关地每版漂移"; }
  done
  [ "${S182_N}" -ge 7 ] || { S182_BAD=1; bad "[182] dist/components 只有 ${S182_N} 个部件包(应 ≥7)—— 判据没扫到东西,拒绝虚绿"; }
fi
[ "${S182_BAD}" = "0" ] && ok "[182] 部件包可复现(gzip -n + 目录 mtime 归一在位·旧写法未回潮·产物 gzip 头 MTIME 全 0)"

# ── [184] 天星择日征象搜索:条件类型注册表 前↔后端 双向差空 ──
# 前端多键=用户可选而后端 invalid_conditions(死开关);后端多键=功能藏而不露。
# 键抓取契约:py 一键一行 '键': {...} / js 一键一行 \t键: {(两侧文件头均有注记);
# jest 哨兵(conditionTypesSync.test.js)带注错自证,此处再做 bash 轻量双向差(零依赖秒级)。
echo "== [184] 择日征象条件类型 前↔后端一致性 =="
S184_BAD=0
S184_PY="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/election_scan.py"
S184_JS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/divination/zeri/conditionTypes.js"
S184_JEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/divination/zeri/__tests__/conditionTypesSync.test.js"
# R4 对齐制度化:tab 对拍资产(页签↔扫描引擎双端锁)与 explain 全类契约不许缺席/缩水:
# 「选了什么→搜出来→点开右栏严密符合」的机械保证。
S184_PARITY="${REPO_ROOT}/Horosa-Web/astropy/tests/test_election_scan_tab_parity.py"
S184_ENDP="${REPO_ROOT}/Horosa-Web/astropy/tests/test_election_scan_endpoint.py"
for f in "${S184_PY}" "${S184_JS}" "${S184_JEST}" "${S184_PARITY}" "${S184_ENDP}"; do
  [ -f "${f}" ] || { bad "[184] 🔴 缺真值源/哨兵文件:${f}"; S184_BAD=1; }
done
if [ -f "${S184_PARITY}" ]; then
  S184_NPAR=$(grep -ac "^def test_" "${S184_PARITY}" || true)
  [ "${S184_NPAR}" -ge 9 ] || { bad "[184] 🔴 tab 对拍资产缩水(${S184_NPAR}<9)——对齐护栏被删?"; S184_BAD=1; }
fi
if [ -f "${S184_ENDP}" ]; then
  grep -aq "test_explain_contract_all_types_and_scan_agreement" "${S184_ENDP}"     || { bad "[184] 🔴 explain 全类契约测试缺席(新类可无实测文本=详情面板哑)"; S184_BAD=1; }
fi
if [ "${S184_BAD}" = "0" ]; then
  S184_PYKEYS=$(sed -n "/^CONDITION_TYPES = {/,/^}/p" "${S184_PY}" | grep -aoE "^    '[a-z_]+':" | tr -d " ':" | sort)
  S184_JSKEYS=$(sed -n "/^export const CONDITION_TYPES = {/,/^};/p" "${S184_JS}" | grep -aoE $'^\t[a-z_]+:' | tr -d $'\t:' | sort)
  S184_NPY=$(printf '%s\n' "${S184_PYKEYS}" | grep -ac . || true)
  S184_NJS=$(printf '%s\n' "${S184_JSKEYS}" | grep -ac . || true)
  if [ "${S184_NPY}" -lt 10 ] || [ "${S184_NJS}" -lt 10 ]; then
    bad "[184] 🔴 键抓取塌缩(py=${S184_NPY}/js=${S184_NJS} <10)——一键一行格式契约被破或 regex 失配"; S184_BAD=1;
  elif [ "${S184_PYKEYS}" != "${S184_JSKEYS}" ]; then
    bad "[184] 🔴 条件类型键集不一致(前端死开关或后端藏功能):"; S184_BAD=1;
    diff <(printf '%s\n' "${S184_PYKEYS}") <(printf '%s\n' "${S184_JSKEYS}") | sed 's/^/[184]   /' >&2 || true
  fi
  grep -aq "注错自证" "${S184_JEST}" 2>/dev/null || { bad "[184] 🔴 jest 哨兵缺注错自证断言(哨兵可能已死)"; S184_BAD=1; }
fi
[ "${S184_BAD}" = "0" ] && ok "[184] 择日条件类型前后端恒等(py=${S184_NPY} 键)+jest 哨兵自证在位"

# ── [185] 六壬伏吟子卯互刑末传取冲(#62) ──
# 病史:伏吟中末传沿刑链取(中=初刑,末=中刑,唯中传自刑取冲),而刑表子↔卯为唯一二环——
# 中传所刑还回初传时旧码照取,丁卯/己卯/辛卯日伏吟排出「卯子卯」(#62 实报,应卯子午)。
# 勘正:初中两传恰为子卯互刑(传行杜塞)→ 末传取中传所冲;明令仅此一对,不作更泛抽象。
# 🔴 [160] 型「对拍在位」哨兵抓不到本类病:720 对拍 oracle 的伏吟段曾与引擎同盲区(对拍恒绿)。
# 故本哨兵直接锁:引擎守卫+三分支接线+oracle 同口径+用户实报课式金标锚+反越界锚。
echo "== [185] 六壬伏吟子卯互刑末传取冲(#62) =="
S185_BAD=0
S185_ENG="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.js"
S185_ORACLE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/__tests__/liurengNineMethodOracle.test.js"
S185_GOLD="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/__tests__/liurengSanChuanGolden.test.js"
grep -aq "getFuYinLastCuang(cuang0, cuang1){" "${S185_ENG}" 2>/dev/null || { bad "[185] 🔴 引擎伏吟末传守卫函数缺失(getFuYinLastCuang)"; S185_BAD=1; }
grep -aq "cuang0 === '子' && cuang1 === '卯'" "${S185_ENG}" 2>/dev/null || { bad "[185] 🔴 引擎子卯互刑字面守卫缺失(或被泛化改写)"; S185_BAD=1; }
S185_WIRE=$(grep -ac "this.getFuYinLastCuang(cuang0, cuang1)" "${S185_ENG}" 2>/dev/null)
S185_WIRE=${S185_WIRE:-0}
[ "${S185_WIRE}" -ge 3 ] || { bad "[185] 🔴 伏吟三分支(不虞/自任·杜传/自信·杜传)末传接线不足(需≥3,现 ${S185_WIRE})"; S185_BAD=1; }
grep -aqF "(x1.selfX || ziMaoLoop)" "${S185_ORACLE}" 2>/dev/null || { bad "[185] 🔴 720 对拍 oracle 未同步子卯口径(半截修复:引擎与 oracle 将再度同盲或互红)"; S185_BAD=1; }
grep -aq "#62" "${S185_GOLD}" 2>/dev/null || { bad "[185] 🔴 金标缺 #62 勘正区块标记"; S185_BAD=1; }
grep -aq "'卯', '子', '午'" "${S185_GOLD}" 2>/dev/null || { bad "[185] 🔴 金标缺 #62 实报课式锚(丁卯/己卯/辛卯伏吟→卯子午)"; S185_BAD=1; }
grep -aq "'辰', '卯', '子'" "${S185_GOLD}" 2>/dev/null || { bad "[185] 🔴 金标缺反越界锚(乙卯不虞辰卯子:守卫只认初中互刑环)"; S185_BAD=1; }
grep -aq "'亥', '子', '卯'" "${S185_GOLD}" 2>/dev/null || { bad "[185] 🔴 金标缺反越界锚(壬子杜传亥子卯:中末子卯相邻不得改写)"; S185_BAD=1; }
grep -aE "\.skip|xdescribe|xit\(" "${S185_GOLD}" >/dev/null 2>&1 && { bad "[185] 🔴 金标文件被 skip 旁路"; S185_BAD=1; }
[ "${S185_BAD}" = "0" ] && ok "[185] 六壬伏吟子卯守卫(引擎+三分支接线+oracle 同口径+金标/反越界锚)全在位"

# ── [186] 奇门择日(zeri 子技法)全链完整性 ──
# 择日页「奇门择日」= scope 化复用 DunJiaMain + 纯本地找局引擎。本哨兵锁四类静默退化:
# ①资产在位+新测试零 skip ②条件注册表一键一行契约(Tab 缩进抓键,塌缩判红)+格局清单加性导出
#   (zeri 侧零手抄的根,机械同源 jest 含注错自证) ③对偶锁:SubTabRegistry⇔ZeriMain TabPane
#   (缺一=切走切回被打回首档)、aiExport preset 追加三段⇔快照 builder 三段头(逐字成对)
# ④DunJiaMain scope 化回归锚(硬编码 qimen 槽回潮=keep-alive 双实例竞写复发)+aiExport
#   「择日」子串启发式次序锚(奇门择日<天星择日<裸择日,乱序=zeri 页导出串成辅盘择日盘)。
S186_BAD=0
echo "== [186] 奇门择日全链完整性 =="
S186_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S186_REG="${S186_UI}/src/divination/zeri/qimenConditionTypes.js"
S186_T1="${S186_UI}/src/divination/zeri/__tests__/qimenConditionTypes.test.js"
S186_T2="${S186_UI}/src/divination/zeri/__tests__/qimenScanEngine.test.js"
S186_T3="${S186_UI}/src/divination/zeri/__tests__/qimenZeriFourLedger.test.js"
S186_T5="${S186_UI}/src/components/dunjia/__tests__/dunjiaMainScopeContract.test.js"
for f in \
	"${S186_REG}" \
	"${S186_UI}/src/divination/zeri/qimenScanEngine.js" \
	"${S186_UI}/src/divination/zeri/qimenZeriSnapshot.js" \
	"${S186_UI}/src/components/zeri/QimenZeriMain.js" \
	"${S186_UI}/src/components/zeri/QimenZeriWorkbench.js" \
	"${S186_UI}/src/components/zeri/QimenMiniBoardPopup.js" \
	"${S186_UI}/src/components/help/ZeriHelpDoc.js" \
	"${S186_T1}" "${S186_T2}" "${S186_T3}" "${S186_T5}"; do
	[ -f "${f}" ] || { bad "[186] 🔴 奇门择日资产缺失: ${f#${REPO_ROOT}/}"; S186_BAD=1; }
done
for f in "${S186_T1}" "${S186_T2}" "${S186_T3}" "${S186_T5}"; do
	grep -aE "\.skip|xdescribe|xit\(" "${f}" >/dev/null 2>&1 && { bad "[186] 🔴 奇门择日测试被 skip 旁路: $(basename "${f}")"; S186_BAD=1; }
done
grep -aq "注错自证" "${S186_T1}" 2>/dev/null || { bad "[186] 🔴 格局机械同源哨兵缺注错自证(T1 可能已死)"; S186_BAD=1; }
S186_NKEYS=$(grep -acE $'^\t[a-z_]+: \{' "${S186_REG}" 2>/dev/null || true)
[ "${S186_NKEYS}" -ge 13 ] || { bad "[186] 🔴 奇门条件注册表键抓取塌缩(现 ${S186_NKEYS},需≥13;一键一行 Tab 缩进契约被破?)"; S186_BAD=1; }
grep -aq "^export const QIMEN_JI_PATTERN_NAMES" "${S186_UI}/src/components/dunjia/DunJiaBaGongRules.js" 2>/dev/null || { bad "[186] 🔴 吉格清单加性导出缺失(DunJiaBaGongRules)"; S186_BAD=1; }
grep -aq "^export const QIMEN_XIONG_PATTERN_NAMES" "${S186_UI}/src/components/dunjia/DunJiaBaGongRules.js" 2>/dev/null || { bad "[186] 🔴 凶格清单加性导出缺失(DunJiaBaGongRules)"; S186_BAD=1; }
grep -aq "'qimenzeri'" "${S186_UI}/src/constants/SubTabRegistry.js" 2>/dev/null || { bad "[186] 🔴 ZERI_SUBTABS 缺 qimenzeri(切走切回被打回首档)"; S186_BAD=1; }
grep -aq 'key="qimenzeri"' "${S186_UI}/src/components/zeri/ZeriMain.js" 2>/dev/null || { bad "[186] 🔴 ZeriMain 缺 qimenzeri TabPane"; S186_BAD=1; }
grep -aq "AI_EXPORT_PRESET_SECTIONS.qimenzeri = \[\.\.\.AI_EXPORT_PRESET_SECTIONS.qimen, '择日搜索配置', '择日条件', '命中时辰'\]" "${S186_UI}/src/utils/aiExport.js" 2>/dev/null || { bad "[186] 🔴 qimenzeri preset 段表缺失或改形(须=qimen 全段+择日三段)"; S186_BAD=1; }
for s in '\[择日搜索配置\]' '\[择日条件\]' '\[命中时辰\]'; do
	grep -aq "${s}" "${S186_UI}/src/divination/zeri/qimenZeriSnapshot.js" 2>/dev/null || { bad "[186] 🔴 奇门择日快照缺段头 ${s}"; S186_BAD=1; }
done
S186_L1=$(grep -an "topInfo.includes('奇门择日')" "${S186_UI}/src/utils/aiExport.js" 2>/dev/null | head -1 | cut -d: -f1)
S186_L2=$(grep -an "topInfo.includes('天星择日')" "${S186_UI}/src/utils/aiExport.js" 2>/dev/null | head -1 | cut -d: -f1)
S186_L3=$(grep -an "topInfo.includes('择日')" "${S186_UI}/src/utils/aiExport.js" 2>/dev/null | head -1 | cut -d: -f1)
{ [ -n "${S186_L1}" ] && [ -n "${S186_L2}" ] && [ -n "${S186_L3}" ] && [ "${S186_L1}" -lt "${S186_L2}" ] && [ "${S186_L2}" -lt "${S186_L3}" ]; } || { bad "[186] 🔴 aiExport 择日子串启发式次序被破(奇门择日=${S186_L1:-缺} 天星=${S186_L2:-缺} 裸择日=${S186_L3:-缺};乱序=zeri 页导出串盘)"; S186_BAD=1; }
grep -aq "case 'zeri':" "${S186_UI}/src/utils/aiExport.js" 2>/dev/null || { bad "[186] 🔴 resolveContextByAstroState 缺 zeri 分流(store 兜底根治缺位)"; S186_BAD=1; }
grep -aq "this.scope = props.techniqueScope || 'qimen';" "${S186_UI}/src/components/dunjia/DunJiaMain.js" 2>/dev/null || { bad "[186] 🔴 DunJiaMain techniqueScope 默认锚缺失"; S186_BAD=1; }
S186_HARD=$(grep -ac "saveModuleAISnapshot('qimen'" "${S186_UI}/src/components/dunjia/DunJiaMain.js" 2>/dev/null || true)
[ "${S186_HARD}" = "0" ] || { bad "[186] 🔴 DunJiaMain 出现硬编码 qimen 快照槽(${S186_HARD} 处;scope 化被回潮=双实例竞写复发)"; S186_BAD=1; }
grep -aq "horosa-zeri-host .horosa-dunjia-redesign" "${S186_UI}/src/layouts/app.less" 2>/dev/null || { bad "[186] 🔴 zeri 页 dunjia dock 行样式条缺失(底部 64px 空带回归)"; S186_BAD=1; }
[ "${S186_BAD}" = "0" ] && ok "[186] 奇门择日全链(资产11+注册表${S186_NKEYS}键+格局同源导出+对偶锁+scope回归锚+启发式次序锚)在位"

# ── [187] R4-B1 预取底座:运行时白名单闸+连点泵保底+组式数据预热+L1 真 LRU ──
# 病史:①白名单只是注释+jest 快照,运行时零拦截,且裸 '/pan' 条目匹配不到任何真实路径;
# ②连点时预取泵被「丢旧代耗整拍+rIC 长 timeout」饿死(实测 20 连点 0 派发);
# ③registerIdleWarmTask 启动瞬间快照一次,启动后登记永不执行(注册表空转);
# ④dedupe L1 是 FIFO 冒充 LRU(热条目被预取挤出,预取自己活着)。
# 本哨兵锁四件资产 + Mac 政策修正点(taixuan=seedInBody 绝不入预取白名单——Windows 版此处是漏洞)。
echo "== [187] R4-B1 预取底座(白名单闸+泵保底+组式预热+L1 LRU) =="
S187_BAD=0
S187_SP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/stepPrefetch.js"
S187_REQ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/request.js"
S187_CF="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/chartFetch.js"
S187_IWQ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/idleWarmQueue.js"
S187_RD="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/requestDedupe.js"
S187_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/stepPrefetch.test.js"
grep -aq "export function guardPrefetchUrl(url){" "${S187_SP}" 2>/dev/null || { bad "[187] 🔴 运行时白名单闸函数缺失(guardPrefetchUrl)"; S187_BAD=1; }
grep -aq "'/qimen/pan'," "${S187_SP}" 2>/dev/null || { bad "[187] 🔴 kentang 逐条枚举缺失(白名单塌回通配即随机起卦可被预取)"; S187_BAD=1; }
grep -aqE "^	'/pan'," "${S187_SP}" 2>/dev/null && { bad "[187] 🔴 裸 '/pan' 条目回潮(形同虚设的假白名单)"; S187_BAD=1; }
grep -aq "'/taixuan/pan'" "${S187_SP}" 2>/dev/null && { bad "[187] 🔴 taixuan(seedInBody 蓍法种子)混入预取白名单——预取即钉死起课"; S187_BAD=1; }
grep -aq "'taixuan'," "${S187_SP}" 2>/dev/null || { bad "[187] 🔴 FORBIDDEN 缺 taixuan 禁词"; S187_BAD=1; }
grep -aq "guardPrefetchUrl(url)" "${S187_REQ}" 2>/dev/null || { bad "[187] 🔴 request.js 纵深闸未接线"; S187_BAD=1; }
grep -aq "guardPrefetchUrl(url)" "${S187_CF}" 2>/dev/null || { bad "[187] 🔴 chartFetch.js 纵深闸未接线(kentang 族裸 fetch 不经 request)"; S187_BAD=1; }
grep -aq "horosa_prefetch_pump_livelock_v1" "${S187_SP}" 2>/dev/null || { bad "[187] 🔴 连点泵保底改造缺失(20 连点将回到 0 派发)"; S187_BAD=1; }
grep -aq "export function scheduleDataWarmGroup(generationKey, tasks){" "${S187_IWQ}" 2>/dev/null || { bad "[187] 🔴 组式数据预热调度缺失(scheduleDataWarmGroup)"; S187_BAD=1; }
grep -aq "horosa_dedupe_l1_lru_v1" "${S187_RD}" 2>/dev/null || { bad "[187] 🔴 dedupe L1 真 LRU 命中重插缺失(FIFO 会把热条目挤给预取)"; S187_BAD=1; }
grep -aq "连点泵保底:20 次连点" "${S187_TEST}" 2>/dev/null || { bad "[187] 🔴 连点保底金标缺失(≥15/20 硬指标失守)"; S187_BAD=1; }
grep -aq "kentang 枚举 ≡ 政策表" "${S187_TEST}" 2>/dev/null || { bad "[187] 🔴 白名单↔政策表单一真值源对拍测试缺失"; S187_BAD=1; }
grep -aE "\.skip|xdescribe|xit\(" "${S187_TEST}" >/dev/null 2>&1 && { bad "[187] 🔴 stepPrefetch 测试被 skip 旁路"; S187_BAD=1; }
[ "${S187_BAD}" = "0" ] && ok "[187] R4-B1 预取底座(白名单闸+泵保底+组式预热+L1 LRU+政策修正)全在位"

# ── [188] R4-B2 武装引擎:四时机武装+技法登记表复活+紫微空烧止血 ──
# 病史:①「选完步长第一下卡」——预取单位只来自上次步进 hint,选新档第一下必 miss;
# ②registerStepPrefetcher 注册表零组件登记(死表),且旧 builder 把【基准 fields】传给登记方
# (构出「此刻」参数,预取白打——死表期潜伏未爆);③紫微 chartFree 页选步长走全局 handler
# 空烧 4 个 /chart。武装=四时机(unit-select/settle 兜底/local-settle/tab-activate)按当前
# 档位 ±depth 预好;NO_ARM 含 zeri(Mac 差异化:择日 fields 自持+找局纯本地,全局武装错轴)。
echo "== [188] R4-B2 武装引擎(四时机+登记表+紫微止血) =="
S188_BAD=0
S188_ARM="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/stepPrefetchArm.js"
S188_AST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/models/astro.js"
S188_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
[ -f "${S188_ARM}" ] || { bad "[188] 🔴 武装引擎文件缺失(stepPrefetchArm.js)"; S188_BAD=1; }
grep -aq "'zeri'," "${S188_ARM}" 2>/dev/null || { bad "[188] 🔴 NO_ARM_TABS 缺 zeri(择日 fields 自持,全局武装=错轴白打)"; S188_BAD=1; }
grep -aq "'guazhan', 'planetarium', 'aianalysis'" "${S188_ARM}" 2>/dev/null || { bad "[188] 🔴 NO_ARM_TABS 随机/取现时/流式三禁缺失"; S188_BAD=1; }
grep -aq "registerArmPlanBuilder((fieldValues, hint, astroState)=>buildStepPrefetchTasks" "${S188_AST}" 2>/dev/null || { bad "[188] 🔴 构造器注入缺失(武装线拿不到 builder=全线哑火)"; S188_BAD=1; }
grep -aq "const more = extra(f2, stepHint);" "${S188_AST}" 2>/dev/null || { bad "[188] 🔴 f2 修正回退(登记方又拿基准 fields=预取白打)"; S188_BAD=1; }
S188_SETTLE=$(grep -ac "currentStepUnit(astroState.currentTab)" "${S188_AST}" 2>/dev/null)
S188_SETTLE=${S188_SETTLE:-0}
[ "${S188_SETTLE}" -ge 2 ] || { bad "[188] 🔴 settle 兜底武装不足(快车道+常规两分支须各一,现 ${S188_SETTLE})"; S188_BAD=1; }
S188_REG=$(grep -arl "registerStepPrefetcher('" "${S188_UI}/src/components" 2>/dev/null | wc -l | tr -d ' ')
[ "${S188_REG}" -ge 4 ] || { bad "[188] 🔴 技法登记组件数不足(需≥4:ziwei/dunjia/taiyi/liureng,现 ${S188_REG})"; S188_BAD=1; }
S188_UNREG=$(grep -arl "unregisterStepPrefetcher('" "${S188_UI}/src/components" 2>/dev/null | wc -l | tr -d ' ')
[ "${S188_UNREG}" -ge 4 ] || { bad "[188] 🔴 反注册配对不足(卸载后闭包吃死组件态,现 ${S188_UNREG})"; S188_BAD=1; }
grep -aq "armStepPrefetch('unit-select', { unit, skipChart: true })" "${S188_UI}/src/components/ziwei/ZiWeiInput.js" 2>/dev/null || { bad "[188] 🔴 紫微选步长止血缺失(chartFree 页又空烧 /chart)"; S188_BAD=1; }
grep -aq "armStepPrefetch('tab-activate'" "${S188_UI}/src/pages/index.js" 2>/dev/null || { bad "[188] 🔴 切页武装时机缺失(进页第一下步进恒冷)"; S188_BAD=1; }
grep -aq "armStepPrefetch('local-settle', { fieldsOverride: fields, skipChart: true })" "${S188_UI}/src/components/ziwei/ZiWeiMain.js" 2>/dev/null || { bad "[188] 🔴 紫微本地漏斗 settle 武装缺失"; S188_BAD=1; }
[ "${S188_BAD}" = "0" ] && ok "[188] R4-B2 武装引擎(四时机+登记 ${S188_REG} 件+f2 修正+紫微止血)全在位"

# ── [189] R4 B3-B6/P1-P3a 综合资产锚(数据预热/三段链/错轴止血/缓存补全/静态供给/门观察位) ──
# 一段多锚:各批已由独立 commit+测试验收,此处锁「资产在位性」防未来无意识拆除;
# 逐行一罪,任一缺位即红。详细病史见各 perf(R4-*) commit 信息。
echo "== [189] R4 B3-B6/P1-P3a 综合资产锚 =="
S189_BAD=0
S189_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S189_DWT="${S189_UI}/src/utils/dataWarmTasks.js"
S189_OPT="${S189_UI}/src/utils/optionPrefetch.js"
S189_MAIN_RS="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/main.rs"
S189_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S189_PYSRV="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
# B3:数据预热注册表(登记≥4)+pages 接线+七政三段链
S189_NWARM=$(grep -ac "^registerDataWarmTask('" "${S189_DWT}" 2>/dev/null); S189_NWARM=${S189_NWARM:-0}
[ "${S189_NWARM}" -ge 4 ] || { bad "[189] 🔴 dataWarmTasks 登记数不足(需≥4,现 ${S189_NWARM})"; S189_BAD=1; }
grep -aq "registry.buildDataWarmTasks(warmFields, warmChartObj)" "${S189_UI}/src/pages/index.js" 2>/dev/null || { bad "[189] 🔴 pages 数据预热接线缺失(注册表空转回潮)"; S189_BAD=1; }
S189_RULES=$(grep -ac "fetchMoiraQizhengRules({" "${S189_UI}/src/components/guolao/GuoLaoChartMain.js" 2>/dev/null); S189_RULES=${S189_RULES:-0}
[ "${S189_RULES}" -ge 3 ] || { bad "[189] 🔴 七政规则段调用不足(主链两路+预取链一处须≥3,现 ${S189_RULES}——三段链的第三段被拆即步进回到每步必付)"; S189_BAD=1; }
grep -aq "warmAllStages = transitTime !== null" "${S189_UI}/src/components/guolao/GuoLaoChartMain.js" 2>/dev/null || { bad "[189] 🔴 七政取现时红线守卫缺失(默认「现在」态后两段白打)"; S189_BAD=1; }
# B4:PD 正轴预取+错轴止血
grep -aq "prefetchPdStepSelect(unit){" "${S189_UI}/src/components/astro/AstroPrimaryDirectionChart.js" 2>/dev/null || { bad "[189] 🔴 主限法正轴预取器缺失"; S189_BAD=1; }
grep -aq "path: '/predict/pdchart'," "${S189_UI}/src/components/astro/AstroPrimaryDirectionChart.js" 2>/dev/null || { bad "[189] 🔴 PD 预取任务 path 契约缺失"; S189_BAD=1; }
grep -aq "R4-B4 错轴止血" "${S189_UI}/src/components/astro/AstroPersianDirected.js" 2>/dev/null || { bad "[189] 🔴 波斯向运错轴止血被拆(选步长回到空烧 natal /chart)"; S189_BAD=1; }
# B6:dedupe 精确条目+chartMem validOnly
grep -aq "'/bazi/birth'," "${S189_UI}/src/utils/requestDedupe.js" 2>/dev/null || { bad "[189] 🔴 dedupe 缺 /bazi/birth 精确条目"; S189_BAD=1; }
grep -aqE "^	'/bazi/'," "${S189_UI}/src/utils/requestDedupe.js" 2>/dev/null && { bad "[189] 🔴 /bazi/ 整前缀回潮(族内有写端点 pattern/update)"; S189_BAD=1; }
grep -aq "chartMem_valid_only_v1" "${S189_UI}/src/services/astro.js" 2>/dev/null || { bad "[189] 🔴 chartMem validOnly 被拆(错误信封会进缓存)"; S189_BAD=1; }
# B5a:FE-18+optionPrefetch
grep -aq "horosa_change_cond_no_mutate_v1" "${S189_UI}/src/pages/index.js" 2>/dev/null || { bad "[189] 🔴 changeCond 就地变异根治被拆(渲染 memo 全部白加)"; S189_BAD=1; }
S189_AXES=$(grep -ac "	{ key: '" "${S189_OPT}" 2>/dev/null); S189_AXES=${S189_AXES:-0}
[ "${S189_AXES}" = "4" ] || { bad "[189] 🔴 BINARY_CHART_AXES 非恰四轴(现 ${S189_AXES};多值轴须组件登记不许 util 臆造)"; S189_BAD=1; }
S189_SPEC=$(grep -ac "speculateChartOptions(fieldValues, astroState);" "${S189_UI}/src/models/astro.js" 2>/dev/null); S189_SPEC=${S189_SPEC:-0}
[ "${S189_SPEC}" -ge 2 ] || { bad "[189] 🔴 选项投机 settle 接线不足(快车道+常规两分支须各一,现 ${S189_SPEC})"; S189_BAD=1; }
# P1cd:preload 六前缀+对拍⑤段
grep -aq "'shared-technique', 'vendors-d3'" "${S189_UI}/scripts/inject-preload.js" 2>/dev/null || { bad "[189] 🔴 preload 清单缺 shared-technique/vendors-d3(首屏最大件回到串行瀑布)"; S189_BAD=1; }
grep -aq "check-chunk-dup ⑤" "${S189_UI}/scripts/check-chunk-dup.js" 2>/dev/null || { bad "[189] 🔴 preload↔首屏批次对拍⑤段缺失(清单漂移无人看守)"; S189_BAD=1; }
# P2c:latch 终确认+listen 观察位
grep -aq "sh.java_listen_ready" "${S189_START}" 2>/dev/null || { bad "[189] 🔴 sh.java_listen_ready 观察位缺失(P4-3 裁决数据断供)"; S189_BAD=1; }
grep -aq "HOROSA_READY_PROBE_LATCH" "${S189_START}" 2>/dev/null || { bad "[189] 🔴 就绪探测 latch 合并被拆(每轮回到 4 次 curl fork)"; S189_BAD=1; }
# P3a:PD 并行组+门观察位
grep -aq "HOROSA_PY_PD_PARALLEL" "${S189_PYSRV}" 2>/dev/null || { bad "[189] 🔴 PD 并行组开关缺失"; S189_BAD=1; }
grep -aq "ledger_mark('py.gate_open'" "${S189_PYSRV}" 2>/dev/null || { bad "[189] 🔴 py.gate_open 观察位缺失"; S189_BAD=1; }
grep -aq "py.gate_first_wait" "${S189_PYSRV}" 2>/dev/null || { bad "[189] 🔴 py.gate_first_wait 观察位缺失(P3-b 分级门裁决数据断供)"; S189_BAD=1; }
# P1ab+P2ab:Rust 静态供给+串行点
grep -aq "HOROSA_STATIC_POOL" "${S189_MAIN_RS}" 2>/dev/null || { bad "[189] 🔴 静态服务器线程池被拆(首屏回到单线程串行供给)"; S189_BAD=1; }
grep -aq "fn respond_static_from_ram(" "${S189_MAIN_RS}" 2>/dev/null || { bad "[189] 🔴 静态 RAM 缓存应答缺失"; S189_BAD=1; }
grep -aq "fn make_static_etag(" "${S189_MAIN_RS}" 2>/dev/null || { bad "[189] 🔴 ETag 公式单源定义缺失(fn make_static_etag)"; S189_BAD=1; }
S189_ETAG=$(grep -ac "make_static_etag(" "${S189_MAIN_RS}" 2>/dev/null); S189_ETAG=${S189_ETAG:-0}
[ "${S189_ETAG}" -ge 3 ] || { bad "[189] 🔴 ETag 公式单源共用不足(定义+RAM 两处须≥3(public 磁盘路径简化版不发 ETag),现 ${S189_ETAG}——两路分叉即 304 连续性破)"; S189_BAD=1; }
grep -aq "rust.prestop_done" "${S189_MAIN_RS}" 2>/dev/null || { bad "[189] 🔴 stop 预检账本位缺失"; S189_BAD=1; }
grep -aq "HOROSA_PRUNE_LOGS_ASYNC" "${S189_MAIN_RS}" 2>/dev/null || { bad "[189] 🔴 日志清扫后台化被拆"; S189_BAD=1; }
[ "${S189_BAD}" = "0" ] && ok "[189] R4 B3-B6/P1-P3a 综合资产(预热 ${S189_NWARM} 条+三段链+止血+精确缓存+preload 对拍+门观察位+静态池/RAM)全在位"

# ── [190] R4-B7 渲染批资产锚(convert memo/图守卫/双提交合一/弹窗短路/子页签冻结) ──
# 病史:R10 实测四靶点(三式闪帧/659 行弹窗白建/无关状态抖动)+FL-20260712-5 同型「表新盘旧」。
echo "== [190] R4-B7 渲染批资产锚 =="
S190_BAD=0
S190_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
# C15:convertToArray memo(五处 useMemo,身份稳定供下游 memo)
grep -aq "horosa_convert_memo_v1" "${S190_UI}/src/pages/index.js" 2>/dev/null || { bad "[190] 🔴 convertToArray memo 标记缺失"; S190_BAD=1; }
S190_CM=$(grep -ac "React.useMemo(()=>convertToArray(" "${S190_UI}/src/pages/index.js" 2>/dev/null); S190_CM=${S190_CM:-0}
[ "${S190_CM}" -ge 5 ] || { bad "[190] 🔴 convertToArray useMemo 不足五处(现 ${S190_CM}——数组引用每 render 新建,下游 memo 全 miss)"; S190_BAD=1; }
# C17:七政盘 svg resize 守卫(隐藏期数据更新→切回表新盘旧)
grep -aq "watchChartSvgResize(this.state.chartid, this.drawChart)" "${S190_UI}/src/components/guolao/GuoLaoChart.js" 2>/dev/null || { bad "[190] 🔴 GuoLaoChart svg resize 守卫缺失(FL-20260712-5 同型回潮)"; S190_BAD=1; }
# C16 靶①:三式重算双提交合一(盘结果与 loading:false 同帧)
grep -aq "payload.commitPatch" "${S190_UI}/src/components/sanshi/SanShiUnitedMain.js" 2>/dev/null || { bad "[190] 🔴 三式 commitPatch 防抖透传被拆"; S190_BAD=1; }
grep -aq '\.\.\.(commitPatch || null),' "${S190_UI}/src/components/sanshi/SanShiUnitedMain.js" 2>/dev/null || { bad "[190] 🔴 三式双提交合一被拆(新盘+转圈中间帧回潮)"; S190_BAD=1; }
# C16 靶②:择日两弹窗「从未打开过」粘性短路(~650 行元素树白建)
for S190_F in "src/components/zeri/ConditionBuilderModal.js" "src/components/zeri/QimenZeriWorkbench.js"; do
	grep -aq "if(!everOpenRef.current){ return null; }" "${S190_UI}/${S190_F}" 2>/dev/null || { bad "[190] 🔴 ${S190_F} 粘性短路缺失(弹窗关着每 render 白建元素树)"; S190_BAD=1; }
done
# C16-⑤:FreezeSubTab 三技法接线(六壬 8 面板/奇门 5 面板/七政 map 全面板)
S190_LR=$(grep -ac "<FreezeSubTab active={activeTabKey ===" "${S190_UI}/src/components/lrzhan/LiuRengMain.js" 2>/dev/null); S190_LR=${S190_LR:-0}
[ "${S190_LR}" -ge 8 ] || { bad "[190] 🔴 六壬右栏 FreezeSubTab 不足 8 面板(现 ${S190_LR})"; S190_BAD=1; }
S190_DJ=$(grep -ac "<FreezeSubTab active={panelTab ===" "${S190_UI}/src/components/dunjia/DunJiaMain.js" 2>/dev/null); S190_DJ=${S190_DJ:-0}
[ "${S190_DJ}" -ge 5 ] || { bad "[190] 🔴 奇门右栏 FreezeSubTab 不足 5 面板(现 ${S190_DJ})"; S190_BAD=1; }
grep -aq "<FreezeSubTab active={active === item.key}>" "${S190_UI}/src/components/guolao/GuoLaoChartMain.js" 2>/dev/null || { bad "[190] 🔴 七政右栏 FreezeSubTab map 接线缺失"; S190_BAD=1; }
for S190_F in "src/components/lrzhan/LiuRengMain.js" "src/components/dunjia/DunJiaMain.js" "src/components/guolao/GuoLaoChartMain.js"; do
	grep -aq "import { FreezeSubTab } from '../comp/FreezeInactive';" "${S190_UI}/${S190_F}" 2>/dev/null || { bad "[190] 🔴 ${S190_F} FreezeSubTab import 缺失"; S190_BAD=1; }
done
[ "${S190_BAD}" = "0" ] && ok "[190] R4-B7 渲染批资产(convert memo ${S190_CM} 处+七政守卫+三式同帧+双弹窗短路+子页签冻结 ${S190_LR}/${S190_DJ}/map)全在位"

# ── [191] R4-B5b 选项防抖+主链 Abort 资产锚 ──
echo "== [191] R4-B5b 选项防抖+主链 Abort 资产锚 =="
S191_BAD=0
S191_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
# 选项通道:调度器在位+delta/fresh-base 形态+接线
grep -aq "horosa_option_debounce_v1" "${S191_UI}/src/utils/optionDispatchScheduler.js" 2>/dev/null || { bad "[191] 🔴 optionDispatchScheduler 缺失"; S191_BAD=1; }
grep -aq "pendingDelta = { ...(pendingDelta || {}), ...(delta || {}) };" "${S191_UI}/src/utils/optionDispatchScheduler.js" 2>/dev/null || { bad "[191] 🔴 delta 累积被拆(trailing 只发末次快照=陈旧时间键覆盖时间轴在途变更)"; S191_BAD=1; }
grep -aq "scheduleOptionDispatch((payload)=>{" "${S191_UI}/src/components/astro/ChartDisplaySelector.js" 2>/dev/null || { bad "[191] 🔴 古典参数选项通道接线缺失(连拨回到逐发全算)"; S191_BAD=1; }
# 主链 Abort 三防线:models 挂载+request 短路序+services 共享隔离
grep -aq "chartMainAbortCtl = new AbortController();" "${S191_UI}/src/models/astro.js" 2>/dev/null || { bad "[191] 🔴 主链 AbortController 挂载缺失"; S191_BAD=1; }
S191_GUARD=$(grep -ac "options.signal && options.signal.aborted" "${S191_UI}/src/utils/request.js" 2>/dev/null); S191_GUARD=${S191_GUARD:-0}
[ "${S191_GUARD}" -ge 2 ] || { bad "[191] 🔴 request 层 abort 短路不足两路(requestCore+requestRaw 须各一,现 ${S191_GUARD}——缺者 abort 触发身份再协商)"; S191_BAD=1; }
grep -aq "const shareKey = opts.signal ? '' : key;" "${S191_UI}/src/services/astro.js" 2>/dev/null || { bad "[191] 🔴 chartInflight signal 隔离被拆(A abort 连坐同参搭车 B)"; S191_BAD=1; }
grep -aq "err.name === 'TimeoutError' || err.name === 'AbortError'" "${S191_UI}/src/utils/serviceStatus.js" 2>/dev/null || { bad "[191] 🔴 AbortError 离线白名单被拆(abort 弹离线横幅/触发重试)"; S191_BAD=1; }
[ "${S191_BAD}" = "0" ] && ok "[191] R4-B5b 资产(选项通道 delta+fresh base/Abort 三防线 ${S191_GUARD} 路短路)全在位"

# ── [199] CDS 两处训练端点清单 lockstep(打包预训 ↔ 用户侧自训) ──
# 病史:两处清单各自演化=预置 .jsa 与自训 .jsa 类面分叉,增量后回退自训档时首交互链覆盖骤缩。
echo "== [199] CDS 训练端点清单 lockstep =="
S199_A=$(grep -a 'for _cds_ep in ' "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh" 2>/dev/null | head -1 | sed 's/^[[:space:]]*//')
S199_B=$(grep -a 'for _cds_ep in ' "${REPO_ROOT}/Horosa-Web/start_horosa_local.sh" 2>/dev/null | head -1 | sed 's/^[[:space:]]*//')
if [ -z "${S199_A}" ] || [ -z "${S199_B}" ]; then
	bad "[199] 🔴 CDS 训练端点循环缺失(打包侧='${S199_A}' 自训侧='${S199_B}')"
elif [ "${S199_A}" != "${S199_B}" ]; then
	bad "[199] 🔴 两处 CDS 训练清单分叉——打包预训与用户侧自训类面不一致:打包=${S199_A} 自训=${S199_B}"
else
	if echo "${S199_A}" | grep -aq '"/rules/ziwei"'; then
		ok "[199] CDS 两处训练清单逐字一致(含 /rules/ziwei)"
	else
		bad "[199] 🔴 训练清单缺 /rules/ziwei(R4-P4-2 扩容被拆)"
	fi
fi

# ── [192] 三式连续进退流畅度四资产(丢击根治/不等回流/快照idle/三pan预取+蒙层撤) ──
# 病史:用户实告「连续进退卡很久」——实测三因叠加:①loading 期点击被 clickPlot 静默丢弃
# ②每步硬等 /chart 回流的 1200ms 兜底 timer(回流常缺席=步步吃满)③快照 ~950ms 同步大构建
# 恰插进下一步 recalc timer 之前顶住。另:全屏 Spin 蒙层挡盘(用户圈报)。
echo "== [192] 三式连续进退流畅度四资产 =="
S192_BAD=0
S192_F="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js"
for S192_M in horosa_sanshi_no_drop_step_v1 horosa_sanshi_no_wait_chart_v1 horosa_sanshi_snapshot_idle_v1 horosa_sanshi_step_prefetch_v1; do
	grep -aq "${S192_M}" "${S192_F}" 2>/dev/null || { bad "[192] 🔴 资产标记缺失:${S192_M}"; S192_BAD=1; }
done
grep -aq "registerStepPrefetcher('sanshiunited'" "${S192_F}" 2>/dev/null || { bad "[192] 🔴 三式步进预取登记缺失(连击回到每步真发 HTTP)"; S192_BAD=1; }
grep -aq "unregisterStepPrefetcher('sanshiunited'" "${S192_F}" 2>/dev/null || { bad "[192] 🔴 预取反注册缺失(卸载后登记表泄漏)"; S192_BAD=1; }
grep -aqE "awaitingSyncTimer = setTimeout\(" "${S192_F}" 2>/dev/null && { bad "[192] 🔴 1200ms 兜底 timer 回潮(每步硬等回流)"; S192_BAD=1; }
grep -aq "horosa-workspace-updating horosa-sanshi-updating" "${S192_F}" 2>/dev/null || { bad "[192] 🔴 中栏小加载徽标缺失(或 Spin 蒙层回潮)"; S192_BAD=1; }
grep -aq "sanshiStepFluency" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/__tests__/sanshiStepFluency.test.js" 2>/dev/null || { bad "[192] 🔴 流畅度金标文件缺失"; S192_BAD=1; }
[ "${S192_BAD}" = "0" ] && ok "[192] 三式连续进退四资产(四标记+登记配对+兜底负锚+徽标+金标)全在位"

# ── [193] 增量部件可复现性三资产(FL-20260804-1:pyc/文件 mtime 归一 + CDS 豁免 + 签名缓存) ──
# 增量更新的复用判据是「本地部件 sha == 新 manifest 部件 sha」。打包一旦不可复现,内容
# 一字未改的部件也被判「变了」⇒ 每版每个用户全量重下(实测曾复用率仅 14%、白耗 167MB)。
# 三条修复缺一即回退到「白下载」,故逐条钉死;另钉可执行护栏脚本在位。
echo "== [193] 增量部件可复现性三资产 =="
S193_BAD=0
S193_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S193_SIGN="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/sign_payload_cached.py"
S193_VERIFY="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_component_reproducibility.sh"
S193_TEST="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/test_sign_payload_cached.py"
# 修一:文件 mtime 归一(且 .py 必须豁免——动它会让全量 pyc 失效、用户首启重编译)
grep -aq "def normalize_file_mtimes" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修一缺失:文件 mtime 归一函数不在(xuanshi/jdk 将每版重下)"; S193_BAD=1; }
grep -aqE "if fn\.endswith\('\.py'\):" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修一危险:.py 豁免不在——归一 .py 的 mtime 会让全量 pyc 失效"; S193_BAD=1; }
grep -aq "normalize_file_mtimes(stage)" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修一未接线:归一函数定义了但没调用"; S193_BAD=1; }
# 修二:base CDS archive 豁免出增量部件
grep -aq "JDK_CDS_REL = 'runtime/mac/java/lib/server/classes.jsa'" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修二缺失:classes.jsa 豁免锚不在"; S193_BAD=1; }
grep -aq "HOROSA_CDS_IN_COMPONENTS" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修二 kill-switch 缺失"; S193_BAD=1; }
# 修三:签名产物缓存(且缓存键必须排除 .jsa——它每次 dump 都不同,纳入键则缓存永不命中)
[ -f "${S193_SIGN}" ] || { bad "[193] 🔴 修三缺失:签名缓存层脚本不在"; S193_BAD=1; }
grep -aq "horosa_repro_sign_cache_v1" "${S193_SIGN}" 2>/dev/null || { bad "[193] 🔴 修三资产标记缺失"; S193_BAD=1; }
grep -aq 'KEY_EXCLUDE_SUFFIXES = (".jsa",)' "${S193_SIGN}" 2>/dev/null || { bad "[193] 🔴 修三键污染防线缺失:.jsa 未排出缓存键(实测踩过——键每次都变、缓存永不命中)"; S193_BAD=1; }
grep -aq "HOROSA_SIGN_CACHE" "${S193_SIGN}" 2>/dev/null || { bad "[193] 🔴 修三 kill-switch 缺失"; S193_BAD=1; }
grep -aq "sign_payload_cached.py" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修三未接线:打包脚本仍直呼原签名脚本(缓存不生效)"; S193_BAD=1; }
# 护栏与金标在位
[ -x "${S193_VERIFY}" ] || { bad "[193] 🔴 可复现性护栏脚本缺失或不可执行"; S193_BAD=1; }
[ -f "${S193_TEST}" ] || { bad "[193] 🔴 签名缓存金标缺失"; S193_BAD=1; }
[ "${S193_BAD}" = "0" ] && ok "[193] 增量可复现三资产(mtime 归一+.py 豁免+CDS 豁免+签名缓存+键防污+护栏+金标)全在位"

# ── [194] 时间即时传导 + 择日空闲预挂载 ──────────────────────────────────────
# 用户定版语义:未起盘=改时间只落草稿(首盘必须显式起盘);已起盘=改时间即刻重算中栏右栏。
# 旧病:onTimeChanged 只认 confirmed(Popover 改年月日时分秒带 false)⇒「时间改了盘不动」。
echo "== [194] 时间即时传导 + 择日空闲预挂载 =="
S194_BAD=0
S194_SS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js"
S194_DJ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js"
S194_ZR="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/zeri/ZeriMain.js"
S194_T="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/__tests__/liveTimePropagation.test.js"
grep -aq "horosa_live_time_propagation_v1" "${S194_SS}" 2>/dev/null || { bad "[194] 🔴 三式时间传导资产标记缺失"; S194_BAD=1; }
grep -aq "const liveReplot = !confirmed && !!this.state.hasPlotted;" "${S194_SS}" 2>/dev/null || { bad "[194] 🔴 三式 liveReplot 判据缺失(改时间盘不动会复发)"; S194_BAD=1; }
grep -aq "horosa_live_time_propagation_v1" "${S194_DJ}" 2>/dev/null || { bad "[194] 🔴 遁甲时间传导资产标记缺失"; S194_BAD=1; }
grep -aqE "if\(this\.state\.hasPlotted\)\{[[:space:]]*$" "${S194_DJ}" 2>/dev/null || grep -aq "this.requestNongli(localFields, true);" "${S194_DJ}" 2>/dev/null || { bad "[194] 🔴 遁甲已起盘重算接线缺失"; S194_BAD=1; }
# 反向锚:首盘显式门不得被抹掉(否则未起盘也自动出盘,违用户定版)
grep -aq "点击左侧“起盘”后显示三式合一盘" "${S194_SS}" 2>/dev/null || { bad "[194] 🔴 三式未起盘提示缺失(首盘显式门被抹)"; S194_BAD=1; }
grep -aq "点击左侧“起盘”后显示遁甲盘" "${S194_DJ}" 2>/dev/null || { bad "[194] 🔴 遁甲未起盘提示缺失(首盘显式门被抹)"; S194_BAD=1; }
# 择日空闲预挂载
grep -aq "horosa_zeri_idle_prerender_v1" "${S194_ZR}" 2>/dev/null || { bad "[194] 🔴 择日空闲预挂载资产标记缺失"; S194_BAD=1; }
grep -aq "forceRender={this.state.prerenderQimenZeri}" "${S194_ZR}" 2>/dev/null || { bad "[194] 🔴 择日 forceRender 未接线(首次点击回到冷态建树)"; S194_BAD=1; }
grep -aq "horosa.perf.zeriPrerender" "${S194_ZR}" 2>/dev/null || { bad "[194] 🔴 择日预挂载 kill-switch 缺失"; S194_BAD=1; }
[ -f "${S194_T}" ] || { bad "[194] 🔴 时间传导金标缺失"; S194_BAD=1; }
[ "${S194_BAD}" = "0" ] && ok "[194] 时间即时传导(三式/遁甲 liveReplot+首盘显式门)+择日空闲预挂载(forceRender+kill-switch)+金标 全在位"

# ── [195] 二十八宿相关六修(节气距离/宿度表/环长/锚点/死代码/天才双端) ─────────
# 全部经独立复核+史料查证落定,判据写在各自注释里;拆任一条即回到静默错值。
echo "== [195] 二十八宿六修资产 =="
S195_BAD=0
S195_JQ="${REPO_ROOT}/Horosa-Web/vendor/kintaiyi/src/kintaiyi/jieqi.py"
S195_CFG="${REPO_ROOT}/Horosa-Web/vendor/kintaiyi/src/kintaiyi/config.py"
S195_PC="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py"
S195_ZJS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/ZiweiCalc.js"
S195_ZJV="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model/ZiWeiChart.java"
S195_T="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/__tests__/ziweiTianCaiParity.test.js"
# ① distancejq 取当前节气(不得回潮 year-1)
grep -aq "get_jieqi_start_date(year, month, day, hour, minute)" "${S195_JQ}" 2>/dev/null || { bad "[195] 🔴 distancejq 未取当前节气起点"; S195_BAD=1; }
# 🔴 负锚必须只认【真代码形态】:文档字符串里引述旧写法时会误报(本哨兵初版即栽在这)。
# 旧代码独有形态 = 同一行里既有 `return int( Date(` 又有 `find_jq_date(year-1`。
grep -aE "return int\( *Date\(.*find_jq_date\(year-1," "${S195_JQ}" >/dev/null 2>&1 && { bad "[195] 🔴 distancejq 的 year-1 回潮(春分当天会返回 365)"; S195_BAD=1; }
# ①' 全年份域:distancejq 取 now 必须走 ephem.Date,不得用 datetime.datetime。
#     datetime 只支持公元 1..9999,而本函数经 starhouse 服务于太乙全年份域 ——
#     ①的首版改用 datetime 取 now,公元前 1 年/16798 年直接 ValueError 炸掉整个
#     taiyi/pan(极端年矩阵三例转红)。负锚只认 now 赋值这一真代码形态。
grep -aq "now = Date(" "${S195_JQ}" 2>/dev/null || { bad "[195] 🔴 distancejq 的 now 未走 ephem.Date(全年份域会炸)"; S195_BAD=1; }
grep -aE "^\s*now = datetime\.datetime\(year," "${S195_JQ}" >/dev/null 2>&1 && { bad "[195] 🔴 distancejq 回潮 datetime.datetime 取 now(公元前/远未来 ValueError,taiyi/pan 全炸)"; S195_BAD=1; }
S195_JQT="${REPO_ROOT}/Horosa-Web/astropy/tests/test_kintaiyi_jieqi_distance.py"
[ -f "${S195_JQT}" ] || { bad "[195] 🔴 节气距离金标缺失(纯单元,不依赖 :8899——极端年矩阵要服务在线,单靠它守不住离线自检)"; S195_BAD=1; }
# ② 虚宿距度(汉书10/授时9,原误作25)
grep -aq "numlist = \[13, 9, 16, 5, 5, 17, 10, 24, 7, 11, 10, 18," "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 虛宿距度非 10(汉书/授时两源皆远小于原值 25)"; S195_BAD=1; }
# ③ 环长按表长取模(不得写死 360)
grep -aq "zhoutian = len(gensulist)" "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 周天写死回潮(表长 363 与 360 不符即静默混叠)"; S195_BAD=1; }
grep -aqE "new_num = num -360" "${S195_CFG}" 2>/dev/null && { bad "[195] 🔴 旧 -360 环绕回潮"; S195_BAD=1; }
# ④ 三处节气锚点(判据=24 步间隔须 13~17)
grep -aq '\["井", 12\]' "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 夏至锚点非井12(原井1 致 4/26 度畸形步)"; S195_BAD=1; }
grep -aq '\["箕",4\]' "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 大雪锚点非箕4(原箕24 越出箕宿致岁末倒退)"; S195_BAD=1; }
grep -aq '\["氐", 2\],\["房",1\]' "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 霜降/立冬 氐房顺序回潮(原序为全环唯一逆行)"; S195_BAD=1; }
# ⑤ 节气名对不上须硬报错(不得静默取首宿)
grep -aq "starhouse: 节气" "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 锚点缺失时的硬报错缺失(会把错误伪装成宿名交出)"; S195_BAD=1; }
# ⑥ MOIRA 赤经死代码停用
grep -aq "_moira_distar_ra 已停用" "${S195_PC}" 2>/dev/null || { bad "[195] 🔴 _moira_distar_ra 停用守卫缺失(按赤经定宿会偏 10–44°)"; S195_BAD=1; }
# ⑦ 天才双端同式(JS/Java 必须同改,否则前后端分叉)
grep -aq "placeRec((lifeIdx + yearZiIdx) % 12, '天才', 3)" "${S195_ZJS}" 2>/dev/null || { bad "[195] 🔴 JS 天才落宫式回潮(宫名反查恒偏一位)"; S195_BAD=1; }
grep -aq "int caiIdx = (this.lifeHouseIndex + yearziIdx0 + 24) % 12;" "${S195_ZJV}" 2>/dev/null || { bad "[195] 🔴 Java 天才落宫式未同改(前后端分叉)"; S195_BAD=1; }
[ -f "${S195_T}" ] || { bad "[195] 🔴 天才/马星金标缺失"; S195_BAD=1; }
[ "${S195_BAD}" = "0" ] && ok "[195] 二十八宿六修(节气距离/虛10/环长/三锚点/硬报错/死代码/天才双端)全在位"

# ── [196] 三式外圈随时间校正 + 遁甲/择日遮罩 + 六壬环角宫排版 ─────────────────
# 用户实测三轮才定位的一类**静默错值**:三式已起盘后按时间步进,中栏表头与奇门/太乙盘都跟着走,
# 唯独外圈星度(顶/升/金/日/月,唯一数据源 props.chartObj)冻在起盘那一刻;同一时辰内奇门局与
# 太乙局本就不变,于是整盘看上去「完全没动」。差分实证(同一时刻):点「确定」盘更新、按步进不更新。
# 三道判据缺一即复发,故逐条钉死。
echo "[196] 三式外圈随时间校正 + 遮罩 + 角宫排版"
S196_BAD=0
S196_SS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js"
S196_FLAGS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/perfFlags.js"
S196_DJ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js"
S196_LESS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.less"
S196_T="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/__tests__/outerRingFollowsTime.test.js"
# ① chartObj 校正不得被 awaitingChartSync 闸死(实时传导路径下它恒为 false)
grep -aq "if(this.state.hasPlotted && chartChanged){" "${S196_SS}" 2>/dev/null || { bad "[196] 🔴 三式 chartObj 校正判据缺失(外圈会冻在起盘那一刻)"; S196_BAD=1; }
grep -aq "if(this.awaitingChartSync && this.state.hasPlotted && chartChanged)" "${S196_SS}" 2>/dev/null && { bad "[196] 🔴 awaitingChartSync 前置条件回潮(它恒 false,校正整个被跳过)"; S196_BAD=1; }
# ② outerChartKey 不得含随机 chartId(否则同刻重复回流也判「变了」,每次全量重算)
grep -aE "^\s+chartId,\s*$" "${S196_SS}" >/dev/null 2>&1 && { bad "[196] 🔴 getOuterChartKey 回潮纳入随机 chartId"; S196_BAD=1; }
# ③ /chart 主链 abort 必须默认关 —— 两个并发请求会互相残杀致 chartObj 永不更新
grep -aq "=== '1'" "${S196_FLAGS}" 2>/dev/null || { bad "[196] 🔴 mainChainAbort 未保持默认关(双杀致盘不跟时间走)"; S196_BAD=1; }
grep -aq "return flagEnabled('horosa.perf.mainChainAbort')" "${S196_FLAGS}" 2>/dev/null && { bad "[196] 🔴 mainChainAbort 回潮为默认开"; S196_BAD=1; }
# ④ 遁甲/择日全屏遮罩已撤为中栏小徽标(择日内嵌的正是 DunJiaMain,一处守两处)
grep -aq "<Spin spinning={this.state.loading}>" "${S196_DJ}" 2>/dev/null && { bad "[196] 🔴 遁甲全屏 Spin 遮罩回潮(用户明令只留中栏小徽标)"; S196_BAD=1; }
grep -aq "horosa-workspace-updating horosa-dunjia-updating" "${S196_DJ}" 2>/dev/null || { bad "[196] 🔴 遁甲中栏小徽标缺失"; S196_BAD=1; }
grep -aq "horosa-dunjia-updating" "${S196_LESS}" 2>/dev/null || { bad "[196] 🔴 遁甲徽标样式缺失(absolute 会飞到窗口角)"; S196_BAD=1; }
# ⑤ 六壬环角宫:落点回重心 + 外推调小(原 3.1 会把字压出外框)
grep -aq "巳: { left: '29.6%', top: '25.9%'" "${S196_SS}" 2>/dev/null || { bad "[196] 🔴 六壬环角宫落点非重心原值"; S196_BAD=1; }
grep -aq "const outerShift = 3.1;" "${S196_SS}" 2>/dev/null && { bad "[196] 🔴 角宫径向外推回潮 3.1(字会压出外框)"; S196_BAD=1; }
[ -f "${S196_T}" ] || { bad "[196] 🔴 外圈随时间校正金标缺失"; S196_BAD=1; }
[ "${S196_BAD}" = "0" ] && ok "[196] 外圈随时间校正(校正闸/键去随机/abort默认关)+遁甲择日小徽标+角宫排版 全在位"

# ── [197] 调试插桩不得混进发布产物 ──────────────────────────────────────────
# 🔴 病史(v3.7.3 真机拆包抓出):排查「三式改时间盘不动」时往 SanShiUnitedMain / models/astro
# 临时插了 console.log 探针,收尾撤除用的正则只覆盖了「独占一行的 try{ console.log(...) }」形态,
# **漏掉了 `try{ if(cond) console.log(...) }catch(e){} ` 这种带条件的单行写法** ⇒ 一条 `[D] didUpdate`
# 探针随前端进了已公证的 public .pkg,是拆开 web-app 部件搜字符串才发现的(源码 grep 当时也能查到,
# 但收尾时只按自己记得的形态搜,没做全类扫)。
# 判据:src 全树不得出现本类调试标记(业务代码里作为**注释**说明日志门的 "[D] 调试日志门" 不算,
# 故只认 console.log 同行出现标记的真代码形态)。
echo "[197] 调试插桩零残留"
S197_BAD=0
S197_SRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S197_HITS="$(grep -rn -E "console\.(log|debug|info)\([^)]*\[(DBG|D|M)[0-9]*\]" "${S197_SRC}" 2>/dev/null | head -5)"
[ -n "${S197_HITS}" ] && { bad "[197] 🔴 发现调试插桩残留(会随前端进 .pkg):"; printf '%s\n' "${S197_HITS}" >&2; S197_BAD=1; }
S197_HITS2="$(grep -rn -E "window\.__(EPOCHLOG|MARK|probe|netProbe)" "${S197_SRC}" 2>/dev/null | head -5)"
[ -n "${S197_HITS2}" ] && { bad "[197] 🔴 发现挂在 window 上的临时探针残留:"; printf '%s\n' "${S197_HITS2}" >&2; S197_BAD=1; }
[ "${S197_BAD}" = "0" ] && ok "[197] src 全树无调试插桩残留"

# ── [207] 盘面美术(wheel art)五档全链(2026-08-09) ────────────────────────────
# 病灶预防:①wheelArt 不进 AstroChart sCU 白名单=改档不重绘死开关;②app model globalSetup 白名单漏键=静默不存;
# ③重绘签名缺维度=方盘切回圆盘白屏;④中世纪坐标表(徽章=宫头线中点/星体=三角质心/宫号贴内方形)金标锁死。
echo "[207] 盘面美术五档全链"
S207_BAD=0
S207_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
grep -qF "'wheelArt'," "${S207_UI}/components/astro/AstroChart.js" \
  || { bad "[207] 🔴 wheelArt 不在 AstroChart sCU 白名单(改档不重绘=死开关)"; S207_BAD=1; }
grep -qF 'wheelArt: st.wheelArt' "${S207_UI}/models/app.js" \
  || { bad "[207] 🔴 app model globalSetup 白名单缺 wheelArt(跨会话保存静默失效)"; S207_BAD=1; }
grep -qF 'export function normalizeWheelArt' "${S207_UI}/constants/AstroConst.js" \
  || { bad "[207] 🔴 wheelArt 归一函数缺失"; S207_BAD=1; }
grep -qF 'renderWheelStyleGrid' "${S207_UI}/components/astro/AstroChartMain.js" \
  || { bad "[207] 🔴 星盘样式双下拉单源方法被拆(外环样式+盘面美术)"; S207_BAD=1; }
[ -s "${S207_UI}/components/astro/__tests__/wheelArtChart.test.js" ] \
  || { bad "[207] 🔴 盘面美术金标缺失(中世纪几何校准规格失锁)"; S207_BAD=1; }
grep -qF '每个 <AstroChart 渲染点' "${S207_UI}/components/astro/__tests__/wheelArtChart.test.js" \
  || { bad "[207] 🔴 消费点完备性总锁被拆(新增 AstroChart 渲染点漏接 wheelArt 将无人拦截)"; S207_BAD=1; }
grep -qF '至少一个宿主渲染点传了 wheelArt' "${S207_UI}/components/astro/__tests__/wheelArtChart.test.js" \
  || { bad "[207] 🔴 宿主链断点总锁被拆(组件接了 props 宿主没传=选了无效死开关)"; S207_BAD=1; }
grep -qF 'wheelArt: this.props.wheelArt' "${S207_UI}/components/astro/AstroChart.js" \
  || { bad "[207] 🔴 重绘签名缺 wheelArt 维度(方盘切回圆盘白屏)"; S207_BAD=1; }
[ "${S207_BAD}" = "0" ] && ok "[207] 盘面美术 sCU键/持久化白名单/归一/双下拉/几何金标/双总锁/签名维度 全绿"

# ── [210] pyc 不得嵌打包机绝对路径 ───────────────────────────────────────────
# 病症:compileall 不带 -s/-p 时,code object 的 co_filename 记的是打包机绝对路径,
# 于是 /Users/<用户名>/... 随每一个 pyc 进了已公证的 .pkg(实测 runtime tar 内数千个全带)。
# 构建机用户名属 PII。与 [136] 前端 bundle 路径脱敏是同类病、不同表面 —— 那条只钉了
# 前端产物,pyc 这一面此前无人看守;它扫源码扫不到(产物不在源码树)、读 diff 也看不见
# (产物不入 git),只有拆产物 grep 才现形。
# 附带收益:脱敏后同源跨机编译的 pyc 字节恒等,增量部件不再因换目录名被判「变了」。
echo "[210] pyc 路径脱敏(co_filename 不得含构建机路径)"
S210_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S210_BAD=0
[ -s "${S210_PKG}" ] || { bad "[210] 🔴 打包脚本缺失"; S210_BAD=1; }
if [ -s "${S210_PKG}" ]; then
  grep -qE '^\s*-s "\$\{STAGE_ROOT\}" -p "horosa-runtime" \\' "${S210_PKG}" \
    || { bad "[210] 🔴 compileall 未带 -s ${STAGE_ROOT} -p horosa-runtime —— pyc 会重新嵌构建机绝对路径"; S210_BAD=1; }
  grep -qF 'PYTHONHASHSEED=0 "${STAGE_PY_BIN}" -m compileall -q -j1 -f --invalidation-mode unchecked-hash' "${S210_PKG}" \
    || { bad "[210] 🔴 compileall 的种子/单进程/hash 失效模式三件套被改动(pyc 可复现性依赖它)"; S210_BAD=1; }
fi
# pip 的 console_scripts 把安装当时的 python 绝对路径写死进 shebang,同样要脱敏
grep -qF 'console_scripts shebang 脱敏' "${S210_PKG}" \
  || { bad "[210] 🔴 console_scripts shebang 脱敏段缺失 —— pip 入口脚本会带构建机绝对路径"; S210_BAD=1; }
# 终判据:直接扫已产出的**全部**部件,残留即红(不信脚本「跑过了」,只认产物本身)。
# 🔴 曾只扫一个部件 → 另一个部件里的残留照样漏过去;判据面窄 = 假绿。
S210_DIR="${REPO_ROOT}/Horosa_Desktop_Installer/dist/components"
if [ -d "${S210_DIR}" ]; then
  for S210_COMP in "${S210_DIR}"/horosa-comp-*.tar.gz; do
    [ -s "${S210_COMP}" ] || continue
    S210_HIT="$(tar -xzOf "${S210_COMP}" 2>/dev/null | LC_ALL=C grep -ac "/Users/${USER}/" || true)"
    [ "${S210_HIT:-0}" = "0" ] \
      || { bad "[210] 🔴 部件 $(basename "${S210_COMP}") 内仍有构建机路径(${S210_HIT} 处)——重跑 package_runtime_payload.sh"; S210_BAD=1; }
  done
fi
[ "${S210_BAD}" = "0" ] && ok "[210] compileall 带 -s/-p + 可复现三件套完整 + 产物零构建机路径"


# ── [211] 天文地占:改设置/改时地必须实时重排,且重排绝不换卦 ────────────────
# 病症一:改设置或换地点后盘面纹丝不动,非得再点一次「起盘」—— 而再点起盘就是重新揲卦,
#   手上那一卦当场就没了。根因:时地接入计算之后,无人在时地变化时重新请求判读。
# 病症二:用报数起卦的盘,切一次流派就被重新揲一次(母图全变,等于换了一卦)——
#   重排时只带种子、不带那十六个数,计算端遂改由随机数重揲。八种起卦法逐一实测,唯此档失败;
#   时间档另有隐患:它只认时间种子,钉成普通种子即退化成真随机。
# 病症三:「据所选时地起真实上升」「真实星历落星」两档从未生效 —— 界面送出的是度分记法的经纬
#   (如 119e19),计算端按十进制度解读:'26n04' 解不出;'119e19' 更隐蔽,会被当成科学记数法的
#   合法浮点(1.19e21),过了数值转换却卡在经度范围检查上,于是整体静默回落成「无真实盘」。
# 判据两层:jest/pytest 立行为判据 + 此处钉住关键接线与判据文件不被摘掉。
echo "[211] 天文地占实时重排 + 重排不换卦"
S211_SRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/geomancy/GeomancyMain.js"
S211_T="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/geomancy/__tests__/geomancyLiveRecast.test.js"
S211_PY="${REPO_ROOT}/Horosa-Web/astropy/websrv/webgeomancysrv.py"
S211_PT="${REPO_ROOT}/Horosa-Web/astropy/tests/test_geomancy_kernel.py"
S211_BAD=0
[ -s "${S211_SRC}" ] || { bad "[211] 🔴 GeomancyMain.js 缺失"; S211_BAD=1; }
[ -s "${S211_T}" ]   || { bad "[211] 🔴 判据文件 geomancyLiveRecast.test.js 缺失(行为判据没了=无人看守)"; S211_BAD=1; }
if [ -s "${S211_SRC}" ]; then
  # ① 时地判据须取「真正送进请求体的值」,而非 fields 引用 —— 按引用判会因无关状态更新白打后端
  grep -qF 'castParamSig(){' "${S211_SRC}" \
    || { bad "[211] 🔴 castParamSig 缺失 —— 时地变化判据回落引用比较"; S211_BAD=1; }
  # ② 载入存档那一拍不得重排(否则存档盘被覆盖),且签名照样同步(否则下一拍误触发)
  grep -qF 'if(changed && !restored && !this._suppressRecast){ this.scheduleRecastPinned(); }' "${S211_SRC}" \
    || { bad "[211] 🔴 didUpdate 的「变了才算 + 载档不算」守卫被改动"; S211_BAD=1; }
  # ③ 载档抑制窗口:状态更新是异步的,清本地时地草稿要到下一拍才生效,届时「刚载过档」的标志
  #    已复位而签名已变 —— 无此窗口则刚载入的存档盘会被重排覆盖。
  grep -qF 'this._suppressRecast = true;' "${S211_SRC}" \
    || { bad "[211] 🔴 载档抑制窗口缺失 —— 存档盘会在下一拍被重排覆盖"; S211_BAD=1; }
  # ④ 重排须回带该盘自己的起卦源(报数十六数),否则报数盘一改设置就被重新揲卦
  grep -qF "fzMethod === 'numbers' && Array.isArray(fz.cast_numbers)" "${S211_SRC}" \
    || { bad "[211] 🔴 重排未回带十六数 —— 报数盘改设置即被重新揲卦"; S211_BAD=1; }
  # ⑤ 时间档只认时间种子
  grep -qF "if(fzMethod === 'time'){ payload.castMethod = 'time'; payload.timeSeed = pinned; }" "${S211_SRC}" \
    || { bad "[211] 🔴 时间档未走 timeSeed —— 钉成普通种子即退化真随机"; S211_BAD=1; }
  # ⑥ 会改判读的左栏控件须全汇到同一入口(曾散着四份各自钉种子的重复实现)
  S211_N="$(grep -c 'this.recastPinned()' "${S211_SRC}" || true)"
  [ "${S211_N:-0}" -ge 7 ] \
    || { bad "[211] 🔴 recastPinned 调用点仅 ${S211_N} 处(应 ≥7:流派/传本/行星盘/问类/所问宫/转宫/问题+时地)"; S211_BAD=1; }
fi
# ⑦-⑨ 服务层时地解析:经纬是度分记法、时区是偏移串,直接数值转换会让两档成为死开关
if [ -s "${S211_PY}" ]; then
  grep -qF 'lon = _parse_geo(data.get("lon"))' "${S211_PY}" \
    || { bad "[211] 🔴 地占服务未走 _parse_geo —— 真实上升/真实星历落星回落成死开关"; S211_BAD=1; }
  grep -qF 'zone = _parse_zone(data.get("zone"))' "${S211_PY}" \
    || { bad "[211] 🔴 地占服务未按偏移串解析时区 —— 非东八区的真实盘时刻整体偏"; S211_BAD=1; }
  grep -qF 'from websrv.horosa_engine_common import coord_to_float' "${S211_PY}" \
    || { bad "[211] 🔴 未复用既有 coord_to_float(度分解析口径会分叉)"; S211_BAD=1; }
else
  bad "[211] 🔴 webgeomancysrv.py 缺失"; S211_BAD=1
fi
# ⑩ 判据文件里的关键断言不得被摘:每条都对应上述三项修复中的一个具体失效形态
if [ -s "${S211_T}" ]; then
  for S211_A in \
    '报数盘:重算必带回那十六个数' \
    '时间档只认 timeSeed' \
    '载档那一拍不许重算' \
    '时地无关的重渲染'
  do
    grep -qF "${S211_A}" "${S211_T}" \
      || { bad "[211] 🔴 判据文件缺关键断言:${S211_A}"; S211_BAD=1; }
  done
fi
grep -qF 'def test_time_place_reaches_real_chart_with_frontend_payload' "${S211_PT}" 2>/dev/null \
  || { bad "[211] 🔴 pytest 缺「按界面原样请求体须起得出真实盘」判据"; S211_BAD=1; }
grep -qF 'def test_real_chart_switch_off_means_time_place_never_matters' "${S211_PT}" 2>/dev/null \
  || { bad "[211] 🔴 pytest 缺零回归判据(未选真实盘档时喂不喂时地必恒等)"; S211_BAD=1; }
[ "${S211_BAD}" = "0" ] && ok "[211] 时地/设置改动即重排 + 八档起卦源原样回带 + 载档不被覆盖"

# ── [219] 源码文本文件禁裸控制字节(NUL):裸 \x00 会让 file(1) 判 data、BSD grep 判 binary
# 静默弃扫 —— 一切基于 grep 的护栏/审计/临时排查在该文件上失明(2026-08-17 实抓:
# KaTeX 占位哨兵写成裸字节,致该文件对无 -a 的 grep 完全不可见)。哨兵/分隔符一律写
# \x00 转义序列(运行时字节串等价),绝不落裸字节。──
echo "[219] 文本源码禁裸 NUL"
S219_HITS="$(cd "${REPO_ROOT}" && git ls-files -z -- '*.js' '*.jsx' '*.ts' '*.md' '*.less' '*.css' '*.json' '*.py' '*.java' '*.sh' '*.rs' '*.html' | python3 -c '
import sys
files = sys.stdin.buffer.read().split(b"\x00")
bad = []
for f in files:
    if not f:
        continue
    try:
        data = open(f, "rb").read()
    except Exception:
        continue
    if b"\x00" in data:
        bad.append(f.decode())
print("\n".join(bad))
')"
if [ -n "${S219_HITS}" ]; then
  bad "[219] 🔴 文本源码含裸 NUL 字节(grep 类护栏对其静默失明,改用 \\x00 转义): $(printf '%s' "${S219_HITS}" | tr '\n' ' ')"
else
  ok "[219] 文本源码零裸 NUL(grep 类护栏可信)"
fi

echo "== 结果 =="
if [ "${fail}" -ne 0 ]; then echo "pre-flight 有 ❌,先修再发。" >&2; exit 1; fi
echo "pre-flight 全部通过 ✅(注意:功能层 e2e 仍需另测,如 AI 用真 key、八字切换显示)。"
