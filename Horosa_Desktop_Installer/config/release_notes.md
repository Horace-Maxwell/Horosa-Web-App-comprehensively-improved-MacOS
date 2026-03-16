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
- 本次 app release 提升到 `v1.0.21`，继续复用已验收通过的独立 runtime `1.0.18-runtime1`，算法与 runtime 内容不变。
