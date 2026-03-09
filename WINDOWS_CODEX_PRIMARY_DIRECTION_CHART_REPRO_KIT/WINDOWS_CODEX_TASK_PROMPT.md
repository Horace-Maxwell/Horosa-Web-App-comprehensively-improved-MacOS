# 给 Windows 上 Codex 的执行提示

你的任务是把目标 Horosa 仓库改到与这份复现包中的 Mac 生产实现一致，重点是：

- `推运盘 -> 主/界限法`
- `推运盘 -> 主限法盘`
- `AstroAPP-Alchabitius` 主限法算法
- `/chart` 与 `/predict/pd` 主限法结果一致
- `/chart` 默认不得再 eager-load `primaryDirection`
- 广德盘浏览器实测结果与 `expected_results/` 中样本一致

## 约束

1. 以本包 `snapshot/` 里的源码为准，不要自行推导新公式。
2. 必须同步前端、Python、Java、模型文件，不能只改 UI。
3. 必须清理目标仓库旧的 `Horosa-Web/.horosa-cache`。
4. 必须确认同步修订号是 `pd_method_sync_v6`。
5. 必须保证 `/chart` 和 `/qry/chart` 只在显式要求主限法时，才会用当前请求参数回写 `predictives.primaryDirection`。
6. 一键部署脚本必须能在发现损坏 venv 时自动删除并重建，且安装依赖应使用 `python -m pip`。
7. 必须保留主限法懒加载结构：普通星盘/3D盘/节气盘/七政四余/印度律盘/希腊星术等右侧改时间时，不能顺带再算一遍主限法。
8. 必须跑完以下验证：
   - `node Horosa-Web/astrostudyui/scripts/verifyPrimaryDirectionRuntime.js`
   - `node Horosa-Web/astrostudyui/scripts/verifyHorosaPerformanceRuntime.js`
   - `python scripts/browser_primary_direction_chart_guangde_check.py`
   - `python scripts/browser_horosa_master_check.py`
   - `python scripts/browser_horosa_final_layout_check.py`
   - `python scripts/check_primary_direction_astroapp_integration.py`
   - `Horosa-Web/verify_horosa_local.sh` 必须保留这条一键验收入口
   - `scripts/mac/self_check_horosa.sh` 必须继续串上最终桌面布局验收，不得回退成只测后端

## 这轮提速必须原样保留的手段

这部分非常重要。Windows 端如果只看到“现在变快了”，却不知道“为什么变快”，很容易把真正的优化点做丢，或者为了提速误改公式。

### A. 主限法必须继续保持真正的惰性计算

- `/chart` 默认不得再返回 `predictives.primaryDirection`
- 只有显式传 `includePrimaryDirection=true` 时，`/chart` 才允许回写并返回当前请求参数对应的主限法 rows
- `推运盘 -> 主/界限法` 与 `推运盘 -> 主限法盘` 以外的页面，改右侧时间时不能顺带再算一遍主限法
- 这条惰性路径直接决定了以下页面的速度：
  - 星盘
  - 3D盘
  - 节气单盘
  - 七政四余
  - 印度律盘
  - 希腊星术
- 不能把这条优化误做成“主限法先算了但不显示”；必须是“不请求就不算”

### B. 节气盘提速不是减内容，而是分层加载

- `二十四节气` 首屏现在只发一条完整 `bazi` 请求，不再重复并发一条 `seedOnly`
- 节气图盘不再走旧的 `/jieqi/year` 四季整包批量图路径；现在是：
  - 首屏：只拿 `24` 条节气 + 每条完整四柱
  - 点 `春分星盘 / 春分宿盘 / 春分3D盘 / ...` 时：只按当前标签懒加载当前那一张盘
  - 已打开过的节气盘命中前端内存缓存，不再重复请求
- 旧的 `legacy /jieqi/year` 批量四季图接口仍保留兼容，但它已经不是用户实际交互路径，不能把它重新接回首屏主路径
- 不能为了快而少返回任何节气项、四柱字段或入口 tab；13 个入口必须始终可见

### C. 万年历提速不是简化历法，而是批量复用同一请求内的中间结果

- `万年历 /calendar/month` 之所以从约 `3s` 压到亚秒，不是换了算法，而是把同月 `44` 个连续日期的农历/节气相关中间结果改成单次请求内共享
- 必须保留这条批量路径：
  - `NongliHelper.getNongLiSeries(...)`
  - 单次月视图请求内共享 `dayCache / monthCache / jieqiYearCache`
  - 同月/跨月连续日期复用当年的农历月表和节气年数据
- 不能回退到“月视图里每一天都独立调一次 `getNongLi(...)`”的旧路径
- 不能为提速而删减：农历、节气、月将、干支、真太阳时、朔望判定等任何公式或字段

### D. 冷启动抖动靠预热解决，不靠降低精度

- `warmHorosaRuntime.js + start_horosa_local.sh` 的运行预热必须保留
- 当前预热目标至少包括：
  - `/chart`
  - `二十四节气` 首屏 `/jieqi/year`
- 目的只是把服务冷启动的首次重型初始化提前做掉，不是改算法结果
- 可通过 `HOROSA_SKIP_RUNTIME_WARMUP=1` 跳过预热；但默认路径必须保留预热

### E. 页面快的前提是请求路径不走错

- `verifyHorosaPerformanceRuntime.js` 的校验口径必须保留：
  - `/chart` 默认不 eager-load `primaryDirection`
  - `节气盘 /jieqi/year 二十四节气首屏` 必须 `24` 条全量返回且每条有 `bazi.fourColumns`
  - `万年历 /calendar/month` 必须作为正式强制阈值页，不得再降回 auxiliary
- 不允许为了“让性能报告好看”而把真实交互页从强制阈值移出去

## 绝对禁止的错误优化

Windows 端如果为了追求更低耗时，做出下面这些改动，都算错：

1. 改主限法、节气、农历、干支、真太阳时、朔望、节气时刻的数学公式
2. 减少 `二十四节气` 的返回条数或去掉 `bazi.fourColumns`
3. 把节气盘 13 个入口改成按条件渲染，导致按钮消失
4. 把 `/chart` 重新改回默认顺带计算主限法
5. 把 `万年历` 的月视图信息裁剪成“只保留部分字段”
6. 用降低精度、截断结果、跳步计算来换速度

## Windows 端要理解的性能目标

这次目标不是“单个主限法页快”，而是“所有主要技法和页面的真实交互路径都保持亚秒”。

必须重点盯住这些真实路径：

- 星盘 / 3D盘 / 节气单盘：底层 `/chart`
- 推运盘：`/predict/pd`、`/predict/pdchart`、`/predict/zr` 等
- 节气盘首屏：`/jieqi/year`
- 三式合一 / 易与三式：`/nongli/time`、`/liureng/gods`
- 万年历：`/calendar/month`

对 Windows Codex 的明确要求是：

- 如果某页突然变慢，先检查是不是惰性加载丢了、缓存共享丢了、或用户真实路径被接回旧批量接口
- 不要先去改公式

## 复制范围

把本包 `snapshot/` 下的文件按相对路径覆盖到目标仓库：

- `snapshot/Horosa-Web/...` -> `Horosa-Web/...`
- `snapshot/scripts/...` -> `scripts/...`

## 必须保留的行为

- `主限法盘` 左侧双盘：内圈本命，外圈主限法盘
- 右侧设置：时间选择、推运方法、度数换算
- 任意时间都能投影外圈
- 命中表格时间时，外圈时间与 Arc 必须和表格一致
- `主限法盘` 外圈必须高亮当前 `ASC` 所在 `Term`，并且右侧保留 `当前ASC所在界：...` 文本；两者必须同步
- `Horosa原方法` 与 `AstroAPP-Alchabitius` 切换后，表格和盘面都必须同步变化
- 用户点名的主技法页性能应维持在 `1s` 内，且现在也包括 `万年历 /calendar/month`，可对照 `expected_results/horosa_runtime_perf_check.json`

## 验收重点

广德盘输入：

- `2006-10-04 09:58`
- `30N53 / 119E25`
- `guangde`
- `AstroAPP-Alchabitius + Ptolemy`

应接近：

- `-0度4分 / 2006-10-25 10:54:14`
- `0度21分 / 2007-02-11 16:06:12`
- `-0度48分 / 2007-07-23 11:01:34`
- `0度57分 / 2007-09-14 13:37:20`
- `1度33分 / 2008-04-21 15:49:15`

主限法盘命中第 5 行时，应显示：

- `当前主限法年龄：1度33分`
- `外圈时间：2008-04-21 15:49:15`
- `当前ASC所在界：木星界（射手 0度0分 - 12度0分）`
- 左侧双盘外圈对应 `Term` 有明确可见高亮，并带 `ASC` 标记

## 失败优先排查

如果你发现目标仓库结果和预期差很大，优先检查：

1. 旧 `.horosa-cache` 是否还在
2. `pd_method_sync_v6` 是否真的同步到所有关键文件
3. 模型目录是否完整复制
4. `/chart` 与 `/predict/pd` 是否先已经对齐

不要在没完成这些检查前去改主限法数学。
