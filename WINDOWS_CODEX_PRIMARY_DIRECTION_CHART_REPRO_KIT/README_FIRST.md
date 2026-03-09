# Windows Codex 主限法盘复现包

这份文件夹的目标不是“提供一些参考资料”，而是让 Windows 上的 Codex 在拿到它之后，可以按当前 Mac 主仓库的真实状态，把以下内容完整复刻到目标仓库里：

- `推运盘 -> 主/界限法`
- `推运盘 -> 主限法盘`
- `AstroAPP-Alchabitius` 主限法算法
- `Horosa原方法` 与 `AstroAPP-Alchabitius` 的双分支切换
- `主限法盘` 的任意时间外圈投影
- `主限法盘` 外圈当前 `ASC` 所在 `Term` 的可视高亮
- `AI导出 / AI导出设置` 对 `主限法盘` 的接线
- `/chart` 与 `/predict/pd` 的主限法结果一致性
- `/chart` 默认不再 eager-load `primaryDirection`，主限法只在显式需要时按需计算
- 广德盘浏览器实测结果与 AstroApp 当前输出近似对齐

这份复现包包含三类内容：

- `reference_docs/`
  - 当前主仓库的说明文档副本
  - 主限法实现记录与反推记录副本
- `snapshot/`
  - 直接作为“源事实”的关键源码快照
  - 模型文件
  - 验证脚本
- `expected_results/`
  - 广德盘浏览器验收结果
  - Guangde 对 AstroApp 的原始样本
  - 当前生产版主限法摘要结果

## 你应该怎么用

如果你是把这个文件夹交给 Windows 上的 Codex，请先让它读：

1. `WINDOWS_CODEX_PRIMARY_DIRECTION_CHART_FULL_REPLICATION_GUIDE.md`
2. `WINDOWS_CODEX_TASK_PROMPT.md`
3. `FILE_MANIFEST.md`

然后要求它：

- 以 `snapshot/` 里的文件为准，把目标仓库改到和当前 Mac 版一致
- 不要自行发明主限法公式
- 不要只修前端，不修 `/chart`、`/predict/pd`、模型和缓存修订号
- 必须跑完文档里要求的验证

## 这份包的核心验收标准

复现完成后，至少要同时满足：

1. `主/界限法` 页面显示的浏览器表格 = 当前后端 `/chart` 返回的 `predictives.primaryDirection`
2. `/chart` 与 `/predict/pd` 在 `astroapp_alchabitius` 分支上行级一致
3. `主限法盘` 能在任意时间下更新外圈位置，不是只会显示表格行时间
4. `主限法盘` 外圈会高亮当前 `ASC` 所在 `Term`，且右侧 `当前ASC所在界：...` 文本与图面同步
5. 普通星盘/3D 盘/节气盘/七政四余/印度律盘/希腊星术等右侧改时间时，不会再顺带触发一次主限法计算
6. 广德盘：
   - 出生：`2006-10-04 09:58`
   - 经纬：`30N53 / 119E25`
   - 地点：`guangde`
   - 方法：`AstroAPP-Alchabitius + Ptolemy`
   - 浏览器第一页前几行应接近：
     - `-0度4分 / 2006-10-25 10:54:14`
     - `0度21分 / 2007-02-11 16:06:12`
     - `-0度48分 / 2007-07-23 11:01:34`
     - `0度57分 / 2007-09-14 13:37:20`
     - `1度33分 / 2008-04-21 15:49:15`
7. 用户点名的主技法页性能需维持在 `1s` 内，且现在也包括 `万年历 /calendar/month`，可参考 `expected_results/horosa_runtime_perf_check.json`
8. `主限法盘` 命中表格第 5 行时，状态应接近：
  - `当前主限法年龄：1度33分`
  - `外圈时间：2008-04-21 15:49:15`
  - `当前ASC所在界：木星界（射手 0度0分 - 12度0分）`

## 特别注意

当前版本为了防止旧主限法缓存污染结果，已经把同步修订号统一到：

- `pd_method_sync_v6`

同时还必须保证：

- `/chart`、`/qry/chart` 只允许在显式要求主限法时，才用当前请求参数强制回写 `predictives.primaryDirection`
- 普通 `/chart` 不能默认把 `primaryDirection` 算进去
- 运行环境重建时使用 `python -m pip`，并能在发现损坏 venv 后自动重建

如果 Windows 目标仓库里：

- `/chart` 和 `/predict/pd` 不一致
- 广德盘结果偏离很大
- 页面显示还是旧表

首先检查：

- 是否真的复制了 `snapshot/` 中的全部关键文件
- 是否复制了 `snapshot/Horosa-Web/astropy/astrostudy/models/` 里的全部模型
- 是否清理了目标仓库旧的 `.horosa-cache`
- 是否重新构建了前端和 Java 后端

## 这份包不是干什么的

它不是一个可直接运行的完整 Windows 安装包。  
它是一个“让 Windows 上的 Codex 精确复刻当前 Mac 主限法实现”的操作包。

如果你的目标只是阅读背景，再去看：

- `reference_docs/主限法推演/PRIMARY_DIRECTION_ASTROAPP_ALCHABITIUS_REPLICATION.md`
- `reference_docs/主限法推演/PRIMARY_DIRECTION_ASTROAPP_ALCHABITIUS_MATH_FLOW.md`

如果你的目标是直接复刻，请不要跳过详细指南。
