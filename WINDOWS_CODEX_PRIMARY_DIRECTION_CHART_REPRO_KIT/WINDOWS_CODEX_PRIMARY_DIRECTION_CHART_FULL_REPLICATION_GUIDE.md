# Windows Codex 复刻指南：主限法 + 主限法盘

## 1. 目标

这次要复刻的不是单一表格，而是一整条主限法实现链：

1. 后端主限法计算
2. `AstroAPP-Alchabitius` 与 `Horosa原方法` 双分支
3. `/chart` 与 `/predict/pd` 的一致性
4. 浏览器 `主/界限法` 表格显示
5. 浏览器 `主限法盘` 的任意时间投影
6. `AI导出 / AI导出设置` 接线

你必须把它理解成一套联动系统，而不是“改一个页面”。

## 2. 这次新增的主功能是什么

新增页面：

- `推运盘 -> 主限法盘`

页面结构：

- 左侧：双盘
  - 内圈：本命盘
  - 外圈：主限法盘
- 右侧：
  - 时间选择
  - 推运方法
  - 度数换算
  - 当前状态与说明

功能要求：

- 任意选定时间都要能推导主限法外圈位置
- 外圈位置最终必须投影回黄道，以便和本命盘对齐
- 外圈必须高亮当前 `ASC` 所在 `Term`，并在当前 `ASC` 精确度数上给出可见标记
- 如果所选时间刚好命中 `主/界限法` 表格某行日期，则：
  - `当前主限法年龄` 必须显示那一行的精确 Arc
  - `外圈时间` 必须等于那一行日期
  - 盘面必须与该行主限法状态对应

## 3. 关键实现文件

### 前端

- `snapshot/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js`
  - 主/界限法页
  - 负责主限法设置同步、重算按钮逻辑、表格显示
- `snapshot/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirectionChart.js`
  - 主限法盘页
  - 负责任意时间外圈投影和状态显示
- `snapshot/Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js`
  - 将 `主限法盘` 加入推运盘右侧技术页
- `snapshot/Horosa-Web/astrostudyui/src/utils/aiExport.js`
  - 主限法盘 AI 导出接线
- `snapshot/Horosa-Web/astrostudyui/src/utils/constants.js`
  - 本地 server root 推断逻辑
- `snapshot/Horosa-Web/astrostudyui/src/utils/request.js`
  - 请求缓存模式规范化
- `snapshot/Horosa-Web/astrostudyui/scripts/verifyPrimaryDirectionRuntime.js`
  - 验证 `/chart` 与 `/predict/pd` 一致性

### Python

- `snapshot/Horosa-Web/astropy/astrostudy/perpredict.py`
  - 主限法核心算法
  - `AstroAPP-Alchabitius` 生产实现
- `snapshot/Horosa-Web/astropy/astrostudy/perchart.py`
  - `pdMethod / pdTimeKey / pdtype` 参数入口
- `snapshot/Horosa-Web/astropy/astrostudy/helper.py`
  - `/chart` 返回对象组装
  - `pdSyncRev` 写回
- `snapshot/Horosa-Web/astropy/websrv/webchartsrv.py`
  - `/chart` Python 服务入口
- `snapshot/Horosa-Web/astropy/websrv/webpredictsrv.py`
  - `/predict/pd` Python 服务入口

### Java

- `snapshot/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/ChartController.java`
- `snapshot/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/QueryChartController.java`
- `snapshot/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/PredictiveController.java`
- `snapshot/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/IndiaChartController.java`

这些控制器必须统一透传：

- `pdMethod`
- `pdTimeKey`
- `pdtype`
- `_wireRev = pd_method_sync_v6`

### 模型

必须完整复制：

- `snapshot/Horosa-Web/astropy/astrostudy/models/*`

尤其是：

- `astroapp_pd_asc_case_corr_et_v1.joblib`
- `astroapp_pd_virtual_body_corr_*.joblib`

缺模型会直接让主限法虚点分支退化。

## 4. 复制规则

在 Windows 目标仓库里，按相对路径覆盖以下内容：

1. 把 `snapshot/Horosa-Web/...` 覆盖到目标仓库 `Horosa-Web/...`
2. 把 `snapshot/scripts/...` 覆盖到目标仓库 `scripts/...`
3. 保留目标仓库其他业务内容不动

不要只复制前端。  
不要只复制 `AstroPrimaryDirectionChart.js`。  
不要漏掉模型、Python 服务层、Java 控制器和验证脚本。

## 5. 缓存与旧结果处理

这是这次最容易踩的坑。

如果目标仓库以前跑过旧主限法版本，必须清理：

- `Horosa-Web/.horosa-cache`

原因：

- 旧缓存会让 `/chart` 命中旧 rows
- `/predict/pd` 可能走新实现
- 最终你会得到“广德盘第一页表格和 AstroApp 差很大”的假象

这次生产版本专门把同步修订号升到了：

- `pd_method_sync_v6`

所以：

- 目标仓库里所有相关文件必须带 `pd_method_sync_v6`
- 清缓存后重新构建

## 6. 推荐复刻步骤

以下顺序不要打乱。

### 步骤 1：覆盖源码

按 `snapshot/` 的相对路径覆盖目标仓库。

### 步骤 2：删除旧缓存

删除：

- `Horosa-Web/.horosa-cache`

如果目标仓库还有旧的前端构建产物，也建议删除后重建：

- `Horosa-Web/astrostudyui/dist-file`
- `Horosa-Web/astrostudyui/.umi`

### 步骤 3：安装/确认运行环境

Windows 侧至少要有：

- Python
- Node.js + npm
- Java 17+

### 步骤 4：重建前端

在目标仓库执行：

```powershell
cd Horosa-Web/astrostudyui
npm install --legacy-peer-deps
npm run build:file
```

### 步骤 5：重建 Java 后端

确保后端按目标仓库原有方式重新构建。  
不要沿用旧 jar。

### 步骤 6：启动本地服务

让本地：

- chart python
- java backend
- html server

全部重新起来。

### 步骤 7：跑主限法专项验证

先跑：

```powershell
node Horosa-Web/astrostudyui/scripts/verifyPrimaryDirectionRuntime.js
```

通过标准：

- 不再报 `astroapp_alchabitius /chart and /predict/pd rows are not aligned`

### 步骤 8：跑广德盘浏览器专项

再跑：

```powershell
python scripts/browser_primary_direction_chart_guangde_check.py
```

通过标准：

- `status = ok`
- 无 `dialogs`
- 无 `pageErrors`
- 无 `consoleErrors`
- `browser_table_first_rows` 与 `backend_first_rows` 对齐
- `row_time_pd_chart_state` 命中 `1度33分 / 2008-04-21 15:49:15`

### 步骤 9：跑整站巡检

再跑：

```powershell
python scripts/browser_horosa_master_check.py
python scripts/browser_horosa_final_layout_check.py
python scripts/check_horosa_full_integration.py
python scripts/check_primary_direction_astroapp_integration.py
```

## 6.1 这轮全站提速到底是怎么做的

这一节请 Windows 侧认真看。

这次性能优化的核心不是“把公式算粗一点”，而是把错误的请求路径、重复计算和同一请求内的重复查表去掉。所有优化都必须在“不降低算法最终精度”的前提下复刻。

### 一、主限法：从全站默认附带计算改成显式惰性计算

以前很多页面共用 `/chart`，一旦右侧时间变了，底层会把主限法也跟着算出来。这会拖慢：

- 星盘
- 3D盘
- 节气单盘
- 七政四余
- 印度律盘
- 希腊星术

这轮优化后的正确策略是：

1. `/chart` 默认不返回 `predictives.primaryDirection`
2. 只有显式传 `includePrimaryDirection=true` 时，才允许返回主限法 rows
3. `推运盘 -> 主/界限法` 与 `推运盘 -> 主限法盘` 再按需取主限法

也就是说，优化点是“真正不算”，不是“先算再隐藏”。

Windows 侧如果把这条惰性路径做丢了，整个站的很多页面都会重新变慢。

相关验证：

- `Horosa-Web/astrostudyui/scripts/verifyPrimaryDirectionRuntime.js`
- `Horosa-Web/astrostudyui/scripts/verifyHorosaPerformanceRuntime.js`

这两个脚本会明确检查：

- `/chart` 默认不能 eager-load `primaryDirection`
- 显式传 `includePrimaryDirection=true` 时，`/chart` 与 `/predict/pd` 结果必须一致

### 二、节气盘：按首屏数据和单盘图层拆分加载

节气盘提速主要靠两件事：

1. `二十四节气` 首屏不再重复请求
2. 四季图盘改为按当前标签单盘懒加载

正确结构是：

- 首次进入节气盘：
  - 只请求 `24` 条节气列表
  - 每条都带完整 `bazi.fourColumns`
  - 不再并发一条冗余 `seedOnly`
- 用户点 `春分星盘 / 春分宿盘 / 春分3D盘 / ...` 时：
  - 只加载当前点击的那一张盘
  - 不再通过 `/jieqi/year` 一次性把四季所有图整包拉回
- 已打开过的图盘：
  - 直接命中前端内存缓存，不再重复请求

旧的 `legacy /jieqi/year` 四季批量图接口仍保留兼容，但它已经不是用户真实交互路径。Windows 端不要把它重新接回首屏主链路。

另外，节气盘的性能优化绝不允许带来这些副作用：

- `24` 条节气缺项
- `bazi.fourColumns` 丢失
- 四季 `星盘 / 宿盘 / 3D盘` 入口消失

相关实现重点：

- `snapshot/Horosa-Web/astrostudyui/src/components/jieqi/JieQiChartsMain.js`
- `snapshot/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/JieQiController.java`

### 三、万年历：把逐日重复计算改成单请求批量复用

`万年历 /calendar/month` 以前慢，不是因为历法公式本身重，而是因为月视图会对 `38 + 6` 个日期逐日反复做：

- 农历日信息查找
- 农历月表读取
- 节气年表读取
- 同一请求内大量重复缓存 IO

这轮优化后的正确思路是：

1. 新增批量路径 `NongliHelper.getNongLiSeries(...)`
2. 在一次月视图请求内共享：
   - `dayCache`
   - `monthCache`
   - `jieqiYearCache`
3. 同月/跨月连续日期复用当前年/次年的农历月表和节气年数据
4. 避免对同一月视图里的 `44` 个连续日期做逐日持久缓存读写

注意：

- 这里只是把“重复查同一批中间结果”的开销砍掉
- 实际农历、节气、月将、干支、真太阳时、朔望判定等算法链路没有换公式

相关实现重点：

- `snapshot/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/helper/NongliHelper.java`
- `snapshot/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/helper/CalendarHelper.java`

### 四、冷启动慢：靠预热，不靠降精度

为了降低服务刚启动后第一次打开页面的抖动，这轮把运行预热做进了启动链路。

正确行为：

- 本地服务启动完成后自动预热：
  - `/chart`
  - `二十四节气` 首屏 `/jieqi/year`
- 这样用户第一次进星盘/节气盘时，不会再撞上冷初始化的重型抖动

这是“把第一次重活提前做掉”，不是“把结果算粗”。

相关实现重点：

- `snapshot/Horosa-Web/astrostudyui/scripts/warmHorosaRuntime.js`
- `snapshot/Horosa-Web/start_horosa_local.sh`

可选跳过：

- `HOROSA_SKIP_RUNTIME_WARMUP=1`

但默认路径必须保留预热。

### 五、最终桌面端问题已经固化进一键验收

这轮最后几个桌面端问题，不能只靠肉眼临时检查。现在已经固化成固定脚本：

- `scripts/browser_horosa_final_layout_check.py`

它专门检查：

- 窗口缩放后比例是否异常
- 节气盘 13 个入口是否都存在
- 双层盘是否压住右栏
- `宿盘 / 七政四余 / 三式合一` 是否和 footer 冲突
- `三式合一` 的 `直接时间 / 真太阳时` 是否仍完整可见
- footer 备案图标 / `996` / 左侧 `...` 是否再次出现

而且它已经接入：

- `Horosa-Web/verify_horosa_local.sh`
- `scripts/mac/self_check_horosa.sh`

所以以后跑一键自检时，Windows 侧也必须把这层验收一起保留。

## 6.2 绝对不要做的“伪优化”

如果 Windows 端为了提速做了下面任何一条，都算复刻失败：

1. 改主限法、节气、农历、干支、真太阳时、朔望的数学公式
2. 少返回 `24` 条节气或删掉 `bazi.fourColumns`
3. 把节气盘入口改成按条件渲染，导致按钮消失
4. 把 `/chart` 重新改回默认顺带算主限法
5. 把 `万年历` 月视图字段裁剪掉来换速度
6. 用截断、降采样、跳步、低精度结果来压时间

Windows 侧要记住：

- 这轮优化砍的是重复工作，不是精度。
- 如果结果和 Mac 端不同，优先查请求路径、缓存、懒加载和批量复用是否掉了，不要先改公式。

## 7. 广德盘验收标准

输入：

- 日期：`2006-10-04`
- 时间：`09:58`
- 纬度：`30N53`
- 经度：`119E25`
- 地点：`guangde`
- 方法：`AstroAPP-Alchabitius`
- 度数换算：`Ptolemy`

### 浏览器表格第一页前几行应接近

1. `-0度4分 / 2006-10-25 10:54:14`
2. `0度21分 / 2007-02-11 16:06:12`
3. `-0度48分 / 2007-07-23 11:01:34`
4. `0度57分 / 2007-09-14 13:37:20`
5. `1度33分 / 2008-04-21 15:49:15`
6. `-1度48分 / 2008-07-21 15:24:41`
7. `2度8分 / 2008-11-20 17:10:15`

### `主限法盘` 命中第 5 行时应显示

- `当前主限法年龄：1度33分`
- `外圈时间：2008-04-21 15:49:15`
- `当前ASC所在界：木星界（射手 0度0分 - 12度0分）`
- 左侧双盘外圈中，对应 `ASC` 所在 `Term` 必须出现明确可见高亮与 `ASC` 标记

### 任意时间测试

当把 `主限法盘` 时间切到：

- `2008-01-01 00:00:00`

应出现：

- `当前主限法年龄：1度15分`
- `外圈时间：2008-01-01 00:00:00`
- 外圈 SVG 与表格第 5 行命中时不同

### 方法切换测试

切换到：

- `Horosa原方法`

应出现：

- `当前已应用方法：Horosa原方法`
- `当前主限法年龄：0度5分`
- `外圈时间：2006-11-03 12:50:45`

再切回：

- `AstroAPP-Alchabitius`

应恢复到初始 AstroAPP 结果。

## 8. 为什么 Windows 端容易翻车

最常见有四类：

1. 只复制了前端，没复制 Python/Java/模型
2. 复制了源码，但没删旧 `.horosa-cache`
3. 重新构建前端了，但 Java 还在跑旧 jar
4. `/chart` 与 `/predict/pd` 验证没做，导致页面看起来能用，实际上主限法已分叉
5. 目标仓库的 venv 来自别的绝对路径，旧 `bin/pip` shebang 已失效，但脚本没有自动自愈

## 9. 失败时的排查顺序

### 情况 A：广德盘表格明显不对

先查：

1. `verifyPrimaryDirectionRuntime.js` 是否通过
2. 目标仓库是否已清理 `Horosa-Web/.horosa-cache`
3. `pd_method_sync_v6` 是否真的出现在目标仓库所有相关文件

### 情况 B：表格对，但主限法盘不对

先查：

1. `AstroPrimaryDirectionChart.js` 是否来自 `snapshot/`
2. `AstroDirectMain.js` 是否真的加了 `主限法盘`
3. `AI导出` 和状态读取逻辑是否被旧文件覆盖

### 情况 C：`/chart` 与 `/predict/pd` 不一致

先查：

1. Java 控制器是否都已同步
2. Python `webchartsrv.py / helper.py / perpredict.py` 是否都已同步
3. 是否清掉了旧缓存
4. 是否已经把 `ChartController / QueryChartController` 中的 `/chart` rows 回写逻辑同步过去

### 情况 D：一键部署首启或重建直接挂掉

先查：

1. `scripts/mac/bootstrap_and_run.sh` 是否来自 `snapshot/`
2. 目标仓库是否还在调用旧的 `bin/pip`
3. 是否真的保留了“检测损坏 venv -> 删除 -> 重建”的逻辑

## 10. 这份包里的关键参考结果

直接看这些文件：

- `expected_results/runtime/guangde_primarydirchart_browser_check.json`
- `expected_results/runtime/guangde_primarydirect_browser_table.png`
- `expected_results/runtime/guangde_primarydirchart_browser.png`
- `expected_results/runtime/pd_auto/debug_guangde_case/dirs.csv`
- `expected_results/runtime/pd_reverse/debug_guangde_exact_summary.json`
- `expected_results/runtime/pd_reverse/virtual_only_geo_current540_fullfit_summary.json`
- `expected_results/runtime/pd_reverse/stability_production_summary.json`

## 11. 最终交付标准

只有同时满足以下条件，才算 Windows 复刻成功：

1. 前端构建通过
2. `/chart` 与 `/predict/pd` 主限法分支对齐
3. `主/界限法` 表格浏览器显示 = 后端 rows
4. `主限法盘` 任意时间外圈投影正确
5. `主限法盘` 当前 `ASC` 所在 `Term` 高亮正确，且与右侧状态文本同步
6. 广德盘浏览器专项通过
7. `AstroAPP-Alchabitius` 与 `Horosa原方法` 切换无串台
8. AI 导出与 AI 导出设置仍保留主限法盘接线
9. 一键部署在命中重建路径时，坏 venv 也能自愈成功

达不到这 9 条，就不能算“完美复刻”。
