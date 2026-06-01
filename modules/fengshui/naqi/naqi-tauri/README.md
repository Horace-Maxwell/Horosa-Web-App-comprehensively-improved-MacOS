# 荀爽纳气风水 · macOS App (Tauri)

## 结构

- `src/` 前端静态资源（本项目 UI）
- `src-tauri/` Tauri 配置与 Rust 入口

## 首次准备

1. 安装 Rust（如果未安装）：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
```

2. 安装 Tauri CLI：

```bash
npm install
```

## 开发运行

```bash
npm run dev
```

## 构建 App

```bash
npm run build
```

构建后 `.app` 会在 `src-tauri/target/release/bundle` 下生成。
