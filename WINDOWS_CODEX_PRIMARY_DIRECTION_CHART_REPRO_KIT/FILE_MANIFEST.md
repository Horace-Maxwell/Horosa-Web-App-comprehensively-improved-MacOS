# 文件清单

## 顶层文档

- `README_FIRST.md`
  - 这份包怎么用
- `WINDOWS_CODEX_PRIMARY_DIRECTION_CHART_FULL_REPLICATION_GUIDE.md`
  - Windows Codex 复刻详细指南
- `WINDOWS_CODEX_TASK_PROMPT.md`
  - 可直接交给 Windows Codex 的任务提示
- `FILE_MANIFEST.md`
  - 当前清单
- `SHA256SUMS.txt`
  - 完整哈希校验

## `reference_docs/`

- `README.md`
- `UPGRADE_LOG.md`
- `PROJECT_STRUCTURE.md`
- `主限法推演/PRIMARY_DIRECTION_ASTROAPP_ALCHABITIUS_REPLICATION.md`
- `主限法推演/PRIMARY_DIRECTION_ASTROAPP_ALCHABITIUS_MATH_FLOW.md`
- `主限法推演/ASTROAPP_ALCHABITIUS_PTOLEMY_REVERSE_ENGINEERING_FULL_PROCESS.md`
- `主限法推演/ASTROAPP_ALCHABITIUS_PTOLEMY_REVERSE_ENGINEERING_PUBLIC_EDITION.md`

用途：

- 作为背景和实现记录参考
- 解释主限法算法、主限法盘页面、缓存修订号、广德盘验收等

## `snapshot/`

### 前端

- `Horosa-Web/astrostudyui/src/components/astro/AstroChartCircle.js`
- `Horosa-Web/astrostudyui/src/components/astro/AstroDoubleChart.js`
- `Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js`
- `Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirectionChart.js`
- `Horosa-Web/astrostudyui/src/components/jieqi/JieQiChartsMain.js`
- `Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js`
- `Horosa-Web/astrostudyui/src/models/app.js`
- `Horosa-Web/astrostudyui/src/models/astro.js`
- `Horosa-Web/astrostudyui/src/utils/aiExport.js`
- `Horosa-Web/astrostudyui/src/utils/constants.js`
- `Horosa-Web/astrostudyui/src/utils/request.js`
- `Horosa-Web/astrostudyui/scripts/verifyPrimaryDirectionRuntime.js`
- `Horosa-Web/astrostudyui/scripts/verifyHorosaRuntimeFull.js`
- `Horosa-Web/astrostudyui/scripts/verifyHorosaPerformanceRuntime.js`

### Python

- `Horosa-Web/astropy/astrostudy/helper.py`
- `Horosa-Web/astropy/astrostudy/perchart.py`
- `Horosa-Web/astropy/astrostudy/perpredict.py`
- `Horosa-Web/astropy/websrv/webchartsrv.py`
- `Horosa-Web/astropy/websrv/webpredictsrv.py`

### 模型

- `Horosa-Web/astropy/astrostudy/models/*`

### Java

- `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/helper/NongliHelper.java`
- `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/ChartController.java`
- `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/QueryChartController.java`
- `Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/helper/CalendarHelper.java`
- `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/PredictiveController.java`
- `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/IndiaChartController.java`

### 运行与验证脚本

- `Horosa-Web/start_horosa_local.sh`
- `Horosa-Web/verify_horosa_local.sh`
- `scripts/mac/bootstrap_and_run.sh`
- `scripts/check_primary_direction_astroapp_integration.py`
- `scripts/check_horosa_full_integration.py`
- `scripts/browser_primary_direction_chart_guangde_check.py`
- `scripts/browser_horosa_master_check.py`
- `scripts/browser_horosa_final_layout_check.py`

用途：

- 这些文件是 Windows 复刻时应优先覆盖到目标仓库的“源事实”
- 其中 `AstroChartCircle.js + AstroDoubleChart.js + AstroPrimaryDirectionChart.js` 共同负责 `主限法盘` 的 `ASC` 所在 `Term` 高亮
- `JieQiChartsMain.js + app.js` 共同覆盖这轮最后两项全局可见问题：节气盘四季入口恢复、桌面端 live resize 后工作区高度实时同步
- `browser_horosa_final_layout_check.py + verify_horosa_local.sh` 共同把这轮最后几个桌面端排版问题固化进一键自检链路

## `expected_results/`

### 浏览器专项

- `runtime/guangde_primarydirchart_browser_check.json`
- `runtime/guangde_primarydirchart_browser.png`
- `runtime/guangde_primarydirect_browser_table.png`
- `runtime/browser_horosa_master_check.json`
- `runtime/browser_horosa_master_check.png`
- `runtime/horosa_runtime_perf_check.json`
- `runtime/resize_layout_audit_postfix.json`
- `runtime/resize_astrochart_compact2.png`
- `runtime/resize_direction_solararc_compact2.png`
- `runtime/resize_jieqi_spring_compact2.png`
- `runtime/resize_cnyibu_suzhan_compact2.png`
- `runtime/resize_guolao_compact2.png`
- `runtime/resize_calendar_compact2.png`
- `runtime/sanshi_time_header_current.png`
- `runtime/sanshi_time_header_current_compact.png`
- `runtime/final_layout_master_check.json`
- `runtime/mastercheck_global_shell.png`
- `runtime/mastercheck_jieqi_entries.png`
- `runtime/mastercheck_solararc_std.png`
- `runtime/mastercheck_solararc_compact.png`
- `runtime/mastercheck_suzhan_compact.png`
- `runtime/mastercheck_guolao_compact.png`
- `runtime/mastercheck_sanshi_std.png`
- `runtime/mastercheck_sanshi_compact.png`

### Guangde AstroApp 样本

- `runtime/pd_auto/debug_guangde_case/chartSubmit_response.xml`
- `runtime/pd_auto/debug_guangde_case/dirs.csv`
- `runtime/pd_auto/debug_guangde_case/dirs.json`
- `runtime/pd_auto/debug_guangde_case/meta.json`
- `runtime/pd_auto/debug_guangde_case/th_response.xml`

### 摘要结果

- `runtime/pd_reverse/debug_guangde_exact_summary.json`
- `runtime/pd_reverse/debug_guangde_exact_rows.csv`
- `runtime/pd_reverse/shared_core_geo_current120_v2_exact_summary.json`
- `runtime/pd_reverse/shared_core_geo_current540_s100_exact_summary_bodycorr.json`
- `runtime/pd_reverse/stability_production_summary.json`
- `runtime/pd_reverse/virtual_only_geo_current540_fullfit_summary.json`

用途：

- 用于验证 Windows 端复刻结果是否接近当前 Mac 生产实现
- 其中 `runtime/guangde_primarydirchart_browser_check.json` 现已包含 `initial_pd_chart_term_highlight / arbitrary_pd_chart_term_highlight` 字段，可直接核对 `ASC` Term 高亮是否存在
- `runtime/resize_layout_audit_postfix.json` 与对应 `compact2` 截图可直接核对“窗口缩放后是否仍残留旧高度”
- `runtime/final_layout_master_check.json` 与 `mastercheck_*.png` 可直接核对这轮最后几个桌面端问题是否全部收口
