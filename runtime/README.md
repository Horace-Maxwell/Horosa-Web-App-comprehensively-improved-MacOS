# runtime 目录说明

该目录用于存放**本机生成的运行时缓存**（例如打包的 Java/Python 运行时、离线 bundle）。

- GitHub 版本默认不提交这些大体积二进制文件。
- 在任意 Mac 上首次运行 `Horosa_OneClick_Mac.command` 时会自动准备所需环境和构建产物。
- 如果你需要制作“完全离线包”，可以本地执行 `tools/mac/Prepare_Runtime_Mac.command` 生成内容，再自行打包分发（不建议直接提交到 GitHub 仓库）。

## 当前保留策略（2026-03-06）

为避免主限法逆向阶段遗留的大量中间产物长期占用磁盘，当前 `runtime/` 已精简为“运行 + 主限法自检 + 关键结果证明”的最小集合：

- `runtime/mac/`
  - 供本地启动/自检脚本复用的一键部署 runtime
- `runtime/pd_auto/run_geo_current540_v1`
  - 主限法自检脚本当前默认使用的 AstroApp case 集
- `runtime/pd_reverse/shared_core_geo_current540_s100_exact_rows_bodycorr.csv`
  - 主限法精度阈值自检所需逐行结果
- `runtime/pd_reverse/shared_core_geo_current540_s100_exact_summary_bodycorr.json`
  - 上述逐行结果对应摘要
- `runtime/pd_reverse/stability_production_summary.json`
  - 当前生产版稳定集摘要
- `runtime/pd_reverse/virtual_only_geo_current540_fullfit_summary.json`
  - 当前大样本虚点专项摘要
- `runtime/pd_reverse/shared_core_geo_current120_v2_exact_summary.json`
  - 当前较新跨度样本摘要

其余大体积推理期中间文件已删除。若未来需要重新做逆向实验，应重新抓取/生成，不再依赖旧缓存。
