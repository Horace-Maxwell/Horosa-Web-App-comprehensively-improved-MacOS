#!/usr/bin/env bash
set -euo pipefail

# 星阙 web 版一键停止:双击即回收本项目启动的全部本地服务(Java / Python / 网页服务,
# 含多实例与自动换口的副本)。只停带本产品指纹的进程,绝不误伤其它软件(校验语义
# 集中在 stop_horosa_local.sh 的 HOROSA_STOP_ALL 模式,本文件只是壳)。
ROOT="$(cd "$(dirname "$0")" && pwd)"
STOP_SH="${ROOT}/Horosa-Web/stop_horosa_local.sh"

if [ ! -f "${STOP_SH}" ]; then
  echo "[Horosa] 未找到 ${STOP_SH};请把本脚本放在完整项目文件夹内运行。"
  echo "[Horosa] Please keep this file inside the full project folder."
  read -r -p "按回车退出 / Press Enter to exit..." _
  exit 1
fi
[ -x "${STOP_SH}" ] || chmod +x "${STOP_SH}" 2>/dev/null || true

echo "[Horosa] 正在停止本地服务(含所有端口实例) / Stopping all local services..."
HOROSA_STOP_ALL=1 bash "${STOP_SH}" || true
echo "[Horosa] 完成 / Done."
read -r -p "按回车关闭窗口 / Press Enter to close..." _
