# 卸载星阙

1. 退出 app（菜单栏 → 退出）。
2. 把 `/Applications/星阙.app` 拖入废纸篓。
3. 清理本机组件与数据（可选，彻底卸载时执行）：

```bash
rm -rf "/Users/Shared/Horosa"
rm -rf "$HOME/Library/Application Support/com.horacedong.horosa"
rm -rf "$HOME/Library/WebKit/com.horacedong.horosa"
rm -rf "$HOME/Library/Caches/com.horacedong.horosa"
rm -rf "$HOME/.horosa-cache" "$HOME/.horosa-logs"
defaults delete com.horacedong.horosa 2>/dev/null || true
# 清除安装器收据（可选；让系统不再把本包记为「已安装」）
sudo pkgutil --forget com.horacedong.horosa 2>/dev/null || true
```

> 第 3 步会删除全部本地档案与设置，请先在 app 内导出需要保留的数据。
