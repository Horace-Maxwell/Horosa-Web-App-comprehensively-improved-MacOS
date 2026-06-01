# 更新后卡在启动页 / 不进主界面 /「进入主界面」按钮无效 —— 真因与修复（v2.4.0 重发）

> **真因是 `cleanup_state` 误杀了刚起的静态服务器,不是弹框、也不是慢校验。** 前两次误诊(快路径、模态弹框)都没修好;靠**真机实测**才定位。本文记录完整排查链,供校对。

## 症状(真机)
2.x→2.4.0 软件内更新后,启动器停在「100% Ready · 正在进入主界面…」,不自动进主界面;「进入主界面」按钮也点不动。日志显示后端 ~7s 已就绪。普通重启(退出再开)却正常 —— 这是关键线索:**问题只在「更新后首次启动」分支**。

## 误诊历程(为何前两次没修好)
1. **误诊一:慢校验**。以为首启走 300s 全量慢校验像卡死。改成快路径(预写 fast-path 标记)。→ 实测仍卡。
2. **误诊二:模态弹框阻塞**。以为 `show_post_update_notice` 的阻塞式 `MessageDialog` 冻结主线程、挡住 `setTimeout` 导航。移除弹框。→ **实测仍卡**(built 二进制确认弹框已去除,但 `curl web_port` 仍 connection-refused、进程零监听端口)。
3. **真机实测定位**:写假 `update-complete.txt` 标记 → 启动 built app → 截图仍是启动页 + `curl web_port`=000 + `lsof` 零监听 → **静态服务器死了**。顺藤摸瓜到 `cleanup_state`。

## 真因
`runtime_bootstrap`(`src-tauri/src/main.rs`)流程:
1. `start_static_server(frontend_dir, web_port, shutdown)` 起静态服务器(serve 前端 dist),把 `shutdown` 句柄存进 `AppState.web_shutdown`。
2. **`first_launch_after_update` 分支里调 `cleanup_state(&app)`** —— 它 `web_shutdown.take()` 后 `flag.store(true)`。
3. `start_static_server` 的循环是 `while !shutdown.load(...)` —— shutdown 被置 true → **静态服务器立刻退出**。
4. 之后 `emit_ready` 让 webview `window.location.replace("http://127.0.0.1:{web_port}/index.html?...")`(`__horosaReady` 里 `setTimeout 450ms`)→ 但 web_port 上服务器已死 → 导航连不上 → **永远停在启动页**;「进入主界面」按钮调同一个 `window.location.replace` → 同样连不上 → 看着像「按钮没用」。

`cleanup_state` 在此处对 `session` 是 no-op(`start_runtime` 还没跑、session=None),**唯一实际效果就是误杀本次刚起的静态服务器**。普通启动不走 `first_launch_after_update` 分支、不调它,故正常 → 这正是「退出重开就好」的原因,也解释了为何每次更新都复发(2.3.0→2.3.1 同病)。

## 修法
`runtime_bootstrap` 的 `first_launch_after_update` 分支里**删掉 `cleanup_state(&app)` 调用**(保留 1s 缓冲)。`cleanup_state` 函数本身保留(还被退出/错误/重装等其它路径合法调用)。**铁律:首启路径在 `start_static_server` 之后绝不调任何会触发 `web_shutdown` 的清理。** 另:`show_post_update_notice` 的阻塞式 `MessageDialog` 一并去掉、只留非阻塞 macOS 通知(首启关键路径不做模态阻塞,作为防御性加固,虽非本次真因)。

## 实测验证(发布前,二进制级)
- 重编 binary(含修复)→ 拷进 /tmp 的 .app 副本 + ad-hoc 签名 + 写假更新标记 → 启动。
- **结果:`curl http://127.0.0.1:38991/index.html` = HTTP 200(静态服务器活着,修复前是 000)+ 截图显示已进入主界面(完整本命星盘 + 占星界面),不再是启动页。** ✅ 端到端确认修好。

## 生效范围 / 发布
随 **2.4.0 重发**(版本号不变,覆盖原 GitHub release)。纯 Tauri 外壳改动,不涉 jar / 前端 / Python。

## Windows
macOS 专属(Tauri 外壳 `main.rs` + `web_shutdown`/静态服务器实现)。Windows 若有「更新后卡启动页」,排查其首启路径有没有在起好本地 web/静态服务后又把它关掉。
