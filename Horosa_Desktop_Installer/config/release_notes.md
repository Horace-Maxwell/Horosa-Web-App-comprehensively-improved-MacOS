## 安装包怎么选 / Which Package Should I Download?

- 轻量在线版：`Horosa-Installer-macos-universal-pkg.zip`
  - 适合：网络稳定、能正常访问 GitHub Release 的用户
  - 特点：首包更小，`.pkg` 只安装 app；首次启动时再下载并准备 runtime
- 完整离线版：`Horosa-Installer-macos-universal-offline-pkg.zip`
  - 适合：中国大陆用户、弱网环境、离线分发、想一次装完的用户
  - 特点：安装包更大，但安装过程中不再额外下载 runtime

- 轻量在线版安装期不再在 `postinstall` 里联网下载 runtime；安装成功率更高，失败时也不会把 `.pkg` 整体判死。
- 首次启动会继续沿用现有安装/初始化页，在 app 内完成 runtime 下载、校验、切换和启动。
- fresh install 现在优先把 runtime 落到 shared runtime 路径，和后续应用内更新保持同一套运行目录。
- 完整离线版保持“安装即自带 runtime”的能力，适合中国大陆、弱网和离线转发。
- 删除了全站底部旧备案/版权页脚，不再在所有页面底部额外占位。
- 最外层桌面窗口不再接管纵向滚动；滚动职责改回各页面内部自己的次级滚动区域。
- 针对 `推运盘 / 易与三式 / 八字紫微 / 风水` 补了根窗口滚动专项回归，确认窗口本身不再滚动。
- 修正了“app 壳已更新，但前端仍继续读取旧 runtime”的发布链问题。
- 运行时选择逻辑现在会在 shared runtime 和 user runtime 都可用时优先选择更新版本，避免旧用户目录 runtime 挡住新版本。
- Python 图盘服务关闭 CherryPy autoreloader，避免首启阶段因为 runtime 目录文件变化被误判为源码变更而自重启。
- 发布脚本新增 runtime 变更防呆：如果本地 runtime 内容已经变化，但 `runtimeVersion` 仍指向旧 tag，会直接中止发布。
- 本次 release 提升到 `v1.0.24`，并同步发布新的独立 runtime `1.0.24-runtime1`，确保这次前端改动与 Python 服务稳定性修复都会真正落到软件内更新和首次启动链。
