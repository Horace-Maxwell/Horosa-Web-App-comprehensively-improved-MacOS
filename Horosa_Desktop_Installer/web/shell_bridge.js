// 壳自带页面(启动器 / 设置 / 诊断)调用壳命令的唯一入口。
// 三个页面都经 WebviewUrl::App 载入,打包版只注入 window.__TAURI_INTERNALS__(tauri.conf.json 没开
// withGlobalTauri,全局 Tauri 对象不存在,cargo 用例与预检都锁着这一点)。页面在浏览器 / 审计台架里
// 直接打开时没有桥,调用即以一句中文失败。
(function (root) {
  'use strict';

  function internals() {
    return root ? root.__TAURI_INTERNALS__ : undefined;
  }

  // 有桥 = 在桌面壳里;没有桥时页面照常渲染,只是命令调不通。
  function available() {
    return Boolean(internals());
  }

  async function invoke(cmd, args) {
    const bridge = internals();
    if (bridge?.invoke) {
      return bridge.invoke(cmd, args);
    }
    throw new Error('无法连接桌面程序，请重新打开星阙后重试');
  }

  const api = { invoke, available };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.HorosaShellBridge = api;
})(typeof window !== 'undefined' ? window : null);
