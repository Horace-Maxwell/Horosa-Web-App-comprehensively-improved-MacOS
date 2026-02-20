# 荀爽纳气风水 · 可视化辅助盘

这是一个本地运行的可视化辅助工具，支持精美 UI、手动框选房屋主体、纳气盘叠合、家具与设施标注、结果提示与报告导出。

## 使用方式（macOS）

1. 直接双击打开 `index.html`。
2. 或在终端进入项目目录后运行：

```bash
python3 -m http.server 8080
```

然后在浏览器打开本地服务页面即可使用。

## macOS App 版本（Tauri）

已在 `/Users/horacedong/Documents/New project/naqi-tauri` 准备好 Tauri 工程，可打包为 `.app`。
参考该目录下的 `README.md` 完成 Rust 与 CLI 安装后即可构建。

## Windows 版本（Tauri）

Windows 版本需要在 Windows 机器上构建（Tauri 不能跨平台打包）。

1. 安装 Node.js（建议 18+）与 Rust（rustup）。
2. 进入 `/Users/horacedong/Documents/New project/naqi-tauri` 目录执行：

```bash
npm install
npm run build
```

3. 构建产物会在 `src-tauri/target/release/bundle/` 目录下（包含 `.msi` 或 `.exe` 安装包）。

## 操作要点

- 上传户型图后手动框选房屋主体，并可旋转微调。
- 输入单元门真北角度后，再用画线方式标注入户门方向。
- 纳气盘支持透明度、大小、盘心位置与运期模式切换。
- 放置标记后会自动判断当前气位/水位是否匹配。
- 自定义盘心：按住 Shift 在画布点击设定。
- 可导出当前视图 PNG，并导出判定报告 PNG/PDF。
- 支持撤销/重做、吸附对齐、项目文件导入/导出与本地项目列表。

如需进一步扩展（例如龙虎法可视化、墙体连贯性分析），告诉我你希望的具体交互方式。
