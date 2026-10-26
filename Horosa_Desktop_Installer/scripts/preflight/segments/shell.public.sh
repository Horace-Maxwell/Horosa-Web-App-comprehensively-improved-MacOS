#!/usr/bin/env bash
# 发布前自检 · 桌面壳(启动 / 服务 / 缩放 / 性能)(续)
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。

seg_u63() {
# [63] 模块顶层悬空引用锁 —— 2026-07-31 辅盘干净安装必炸实案制度化:模块顶层引用未定义
#   的名字 → 模块求值即 ReferenceError;首爆被预载 catch 吞 + webpack 中毒缓存 → 二次点击
#   伪装成「Lazy chunk resolved empty」。jest lazyTargetsSmoke 逐个 require 全技法模块并断言
#   有默认导出,任何顶层炸在 jest 即红。
echo "[63] 模块顶层悬空引用锁(lazy smoke 守卫)"
S63_BAD=0
[ -f "${REPO_ROOT}/Horosa-Web/astrostudyui/src/test/lazyTargetsSmoke.test.js" ] || { S63_BAD=1; bad "[63] 缺 jest lazyTargetsSmoke 守卫"; }
[ "${S63_BAD}" = "0" ] && ok "[63] 模块顶层悬空引用锁在位"
}

seg_u224() {
# [224] 布局诊断浮层零残留:global.js 不得含布局诊断浮层及其快捷键痕迹。
echo "[224] global.js 布局诊断浮层零残留"
S224_BAD=0
S224_F="${REPO_ROOT}/Horosa-Web/astrostudyui/src/global.js"
S224_LEAK="$(grep -aciE "layout-probe|布局诊断浮层|KeyL" "${S224_F}")"
[ "${S224_LEAK}" = "0" ] || { bad "[224] global.js 残留诊断浮层痕迹 ×${S224_LEAK}"; S224_BAD=1; }
[ "${S224_BAD}" = "0" ] && ok "[224] global.js 零诊断浮层痕迹"
}

seg_u264() {
# ── [264] 启动并行三件套(壳 early-nav):静态服务一起来就让前端开始下载解析,与后端引导并行 ──
#   三件缺一即回退:① 早导航块(early=1 + HOROSA_EARLY_NAV 回退开关 + rust.early_nav 段)
#   ② init 脚本 __horosaReady:后端就绪时的第二次 ready 同参不重载,只置 __horosaBackendConfirmed 并派事件
#   (缺它 = 后端就绪时整页重载,并行成果全部作废)③ 端口阶梯段(偏好口被占顺位 +1,本地缓存域不漂)。
echo "[264] 启动并行三件套(early-nav / 同参不重载 / 端口阶梯)"
S264_BAD=0
S264_MAIN="$(pf_shell_rs_prod)"
for S264_K in "early=1" "HOROSA_EARLY_NAV" "HOROSA_EARLY_NAV_POST_UPDATE" "fn early_nav_url(" "rust.early_nav" "window.__horosaReady = function" "__horosaBackendConfirmed" "horosa:backend-confirmed" "rust.web_port_ladder"; do
  grep -aqF "${S264_K}" "${S264_MAIN}" || { bad "[264] 🔴 壳缺启动并行件「${S264_K}」"; S264_BAD=1; }
done
for S264_K in "fn desktop_init_script_has_same_target_ready_guard" "fn web_port_ladder_steps_instead_of_random_drift"; do
  grep -aqF "${S264_K}" "$(pf_shell_rs_tests)" || { bad "[264] 🔴 壳缺启动并行件用例「${S264_K}」"; S264_BAD=1; }
done
grep -aq "BACKEND_CONFIRMED_EVENT" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/backendBootGate.js" 2>/dev/null || { bad "[264] 前端就绪门未监听壳确认事件"; S264_BAD=1; }
#   同一进程再次引导(重装运行时 / 重启服务失败后的回退修复)必须先收掉本进程上一台静态服务器、沿用原口;
#   绑定竞态重试走阶梯不跳随机口;旗标换新先置旧旗标。缺任一 = 修一次前端口漂一位、页面换 origin、数据「消失」。
{ grep -aqF 'let preferred_web_port = previous_web_port.unwrap_or(DEFAULT_FRONTEND_PORT);' "${S264_MAIN}" \
  && grep -aqF 'Some(state) => pick_web_port_for_bootstrap(&state.web_shutdown, previous_web_port)?,' "${S264_MAIN}" \
  && grep -aqF 'None => choose_port_with_preference(preferred_web_port)?,' "${S264_MAIN}"; } \
  || { bad "[264] 🔴 再次引导未沿用原前端口(页面换 origin = 本地数据看起来清零)"; S264_BAD=1; }
grep -aqF 'web_port = retry_web_port_after_bind_race(preferred_web_port)?;' "${S264_MAIN}" \
  || { bad "[264] 🔴 静态服务器绑定竞态重试退回随机口"; S264_BAD=1; }
grep -aqF 'replace_web_shutdown(&state.web_shutdown, Some(shutdown));' "${S264_MAIN}" \
  || { bad "[264] 🔴 静态服务器旗标换新未先置旧旗标(旧服务器泄漏占口)"; S264_BAD=1; }
grep -aqF 'fn rebootstrap_keeps_web_port_when_own_static_server_still_listening()' "$(pf_shell_rs_tests)" \
  || { bad "[264] 🔴 缺「再次引导前端口不变」回归测试"; S264_BAD=1; }
#   同口重起后旧服务器上的空闲长连接必须当场关掉:浏览器按「主机+端口」复用连接,旧连接 30 秒读超时内
#   再发的请求会拿到「服务已停」的 503(浏览器不重试 → 白页 / 分包加载失败)。仓内 tiny_http 副本退役时关读方向。
grep -aqF 'ConnectionRegistry::close_all(&self.connections);' "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/vendor/tiny_http/src/lib.rs" \
  || { bad "[264] 🔴 本机 HTTP 服务退役时不再关闭空闲长连接(同口重起后旧连接吃 503 白页)"; S264_BAD=1; }
grep -aqF 'fn retired_http_server_closes_idle_keepalive_connections()' "$(pf_shell_rs_tests)" \
  || { bad "[264] 🔴 缺「退役后旧长连接不回 503」回归测试"; S264_BAD=1; }
[ "${S264_BAD}" = "0" ] && ok "[264] 启动并行三件套在位(早导航 + 同参不重载确认 + 端口阶梯 + 前端就绪门事件化)"
}
