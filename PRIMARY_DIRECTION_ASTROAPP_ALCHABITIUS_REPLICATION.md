# AstroApp-Alchabitius 主限法复刻说明

本文档说明当前 Horosa 中 `AstroAPP-Alchabitius` 主限法分支是如何实现的，以及如何在不依赖 AstroApp API 的前提下，在本地完整复刻同一套结果生成链路。

配套数学版与流程图见：

- [PRIMARY_DIRECTION_ASTROAPP_ALCHABITIUS_MATH_FLOW.md](/Users/horacedong/Desktop/Horosa-Primary%20Direction%20Trial/PRIMARY_DIRECTION_ASTROAPP_ALCHABITIUS_MATH_FLOW.md)

目标不是泛泛而谈“阿尔卡比提乌斯主限法”，而是精确描述当前工程内已经落地的、可复现 AstroApp `Primary Directions -> Direction Method = Alcabitius -> Time Key = Ptolemy -> Type = In Zodiaco` 的实现。

## 1. 目标范围

当前复刻范围：

- `Primary Directions`
- `Direction Method = Alcabitius`
- `Time Key = Ptolemy`
- `Type = In Zodiaco`
- 常规主相位：`0 / 60 / 90 / 120 / 180`
- direct + converse 同时保留
- 结果按 `|Arc|` 从小到大排序

当前不在这份复刻保证内的内容：

- Node 相关行
- AstroApp 未显示、但 Horosa 自有的扩展对象集差异
- Mundo 主限法
- 非 `Ptolemy` 时间键

## 2. 当前工程内对应文件

后端主限法分发：

- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astropy/astrostudy/perchart.py`
- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astropy/astrostudy/perpredict.py`
- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astropy/astrostudy/signasctime.py`
- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astropy/astrostudy/helper.py`

前端设置、计算与显示：

- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astrostudyui/src/models/app.js`
- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astrostudyui/src/models/astro.js`
- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js`
- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js`
- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astrostudyui/src/utils/aiExport.js`

## 3. 行结构

Horosa 后端返回的主限法每一行是固定五元组：

```json
[
  arc,
  promittor_id,
  significator_id,
  "Z",
  date_str
]
```

含义：

- `元素0 arc`
  - 主限 Arc，单位为度
  - 正值表示 direct
  - 负值表示 converse
- `元素1 promittor_id`
  - 迫星编码
- `元素2 significator_id`
  - 应星编码
- `元素3`
  - `Z` 表示 In Zodiaco
- `元素4 date_str`
  - 由 Arc 换算得到的事件日期字符串

Promittor / Significator 编码规则沿用 Horosa / flatlib 原编码：

- `T_xxx_sign`：界
- `D_xxx_angle`：右相位
- `S_xxx_angle`：左相位
- `A_xxx_0`：映点
- `C_xxx_0`：反映点
- `N_xxx_0 / 180`：合相或对冲

## 4. 输入条件

要在本地复刻当前实现，最少需要以下输入：

- 出生日期
- 出生时间
- 时区
- 出生纬度
- 出生经度
- 宫制
- 黄道体系
- `pdtype = 0`（主限法 Zodiaco）
- `pdMethod = astroapp_alchabitius`
- `pdTimeKey = Ptolemy`
- `pdaspects = [0, 60, 90, 120, 180]`

当前工程里，这些输入最终都进入 `PerChart(data)`。

## 5. 双内核分流

后端主入口：

```python
def getPrimaryDirectionByZ(self):
    if getattr(self.perchart, 'pdMethod', 'astroapp_alchabitius') == 'horosa_legacy':
        pdlist = self.getPrimaryDirectionByZLegacy()
    else:
        pdlist = self.getPrimaryDirectionByZAstroAppKernel()
    self.appendDateStr(pdlist)
    return pdlist
```

这意味着：

- `horosa_legacy`：恢复原版 Horosa 算法
- `astroapp_alchabitius`：使用当前 AstroApp 对齐内核

## 6. Horosa 原方法

`Horosa原方法` 是原版 Horosa 的 `zodiaco主限法`，实现是：

```python
chart = self.perchart.getChart()
pd = PrimaryDirections(chart)
pdlist = []
for item in pd.getList(self.perchart.pdaspects):
    if len(item) > 3 and item[3] == 'Z':
        pdlist.append(item)
```

它不是 AstroApp 复刻核，而是原 Horosa 行为保留分支。

## 7. AstroApp-Alchabitius 复刻核

### 7.1 Significators

当前实现中，Significators 由三部分组成：

```python
sig_objs = pd._elements(pd.SIG_OBJECTS, pd.N, [0])
sig_houses = pd._elements(pd.SIG_HOUSES, pd.N, [0])
sig_angles = pd._elements(pd.SIG_ANGLES, pd.N, [0])
significators = sig_objs + sig_houses + sig_angles
```

### 7.2 Promissors

Promissors 由两部分组成：

```python
prom_objs = pd._elements(pd.SIG_OBJECTS, pd.N, aspList)
prom_terms = pd._terms()
promissors = prom_objs + prom_terms
```

说明：

- `AstroAPP-Alchabitius` 当前不再把 `A_` / `C_`，也就是映点 / 反映点，加入 promissor 集
- `Horosa原方法` 仍然保留原版 Horosa 的完整对象范围

### 7.3 Node 排除

AstroApp 这条复刻分支中，Node 相关行直接排除：

```python
significators = [obj for obj in significators if not self._isNodeDirectionId(obj.get('id'))]
promissors = [obj for obj in promissors if not self._isNodeDirectionId(obj.get('id'))]
```

原因：

- AstroApp 的 Node 行在当前样本下并不稳定
- 单核复刻时，Node 会引入明显噪声
- 当前工程明确把 Node 放在复刻保证范围之外

## 8. Arc 核公式

当前 AstroApp-Alchabitius 核使用的公式是：

```text
arc = norm180( RA(sig, true_lat) - RA(promissor_aspected, zero_lat) )
```

在当前代码里对应为：

```python
arc = self._norm180(sig_ra - prom_ra_z)
```

其中：

- `sig_ra = sig.get('ra')`
  - 应星使用 `ra`
  - 即 true latitude 分支
- `prom_ra_z = prom.get('raZ')`
  - 迫星使用 `raZ`
  - 即 zero latitude 分支
  - 这里的 `prom` 已经是“相位化后的迫星对象”，不是原始黄经点

归一化函数：

```python
def _norm180(self, deg):
    return (float(deg) + 180.0) % 360.0 - 180.0
```

所以 Arc 最终总在 `(-180, 180]` 的等价区间内，再结合后续裁剪，保留 `|arc| <= 100`。

## 9. 行过滤规则

### 9.1 基本过滤

当前代码会先剔除以下情况：

```python
if prom_id == sig_id:
    continue
if self._baseDirectionObjectId(prom_id) == self._baseDirectionObjectId(sig_id):
    continue
if abs(arc) <= eps:
    continue
if abs(arc) > 100.0:
    continue
```

这几条分别对应：

- 同一编码对象不保留
- 同一基础对象本体互指不保留
- 极小 Arc 视作零，不保留
- 超出 100 度 Arc 的行不保留

### 9.2 AstroApp 普通行星显示窗

对“普通行星 -> 普通行星”这类行，还会额外套 AstroApp 的显示窗裁剪：

```python
raw_delta = float(sig.get('lon')) - float(prom.get('lon'))
if abs(raw_delta) <= 3.0:
    keep
elif arc > 0 and 3.0 < raw_delta < 107.5:
    keep
elif arc < 0 and -107.5 < raw_delta < -3.0:
    keep
else:
    drop
```

代码常量：

```python
ASTROAPP_PD_DISPLAY_EPS = 3.0
ASTROAPP_PD_DISPLAY_WINDOW = 107.5
```

这一步不是阿尔卡比提乌斯理论公式，而是当前对 AstroApp 页面显示逻辑的经验复刻。

## 10. 排序规则

最终输出排序是：

```python
pdlist.sort(key=lambda item: (abs(item[0]), item[0], item[1], item[2]))
```

也就是：

1. `|Arc|` 从小到大
2. 同 `|Arc|` 时按带符号 `Arc`
3. 再按 `promittor_id`
4. 再按 `significator_id`

这一步非常关键，因为 AstroApp 页面显示顺序就是先看 `|Arc|`。

## 11. 日期换算：Ptolemy

当前工程里，`Ptolemy` 时间键的换算不再是简单的：

```text
birth_jd + |arc| * 365.2421904
```

而是使用“按整年周年日拆分，再按下一周年跨度做线性插值”的写法：

```python
magnitude = abs(float(arc))
years = int(math.floor(magnitude + 1e-12))
fraction = magnitude - years

birth_utc = self._birth_local.astimezone(timezone.utc)
current_local = self._add_years_safe(self._birth_local, years)
next_local = self._add_years_safe(self._birth_local, years + 1)

whole_days = (current_local.astimezone(timezone.utc) - birth_utc).total_seconds() / 86400.0
span_days = (next_local.astimezone(timezone.utc) - current_local.astimezone(timezone.utc)).total_seconds() / 86400.0
jd = self.birth.jd + whole_days + fraction * span_days
```

关键点：

- 日期换算使用 `abs(arc)`，即 converse 不会换算到出生前
- 先走整年周年日，再走当前周年到下一周年之间的比例插值
- 最终显示使用 UTC 风格：

```python
dt = Datetime.fromJD(jd, 0)
return dt.toCNString()
```

这部分是当前与 AstroApp 日期对齐最关键的一步。

## 12. 最小复刻伪代码

下面这段伪代码足够复现当前实现的主路径：

```python
perchart = PerChart(payload)
chart = perchart.getChart()
pd = PrimaryDirections(chart)

sigs = (
    pd._elements(pd.SIG_OBJECTS, pd.N, [0]) +
    pd._elements(pd.SIG_HOUSES, pd.N, [0]) +
    pd._elements(pd.SIG_ANGLES, pd.N, [0])
)

proms = (
    pd._elements(pd.SIG_OBJECTS, pd.N, [0, 60, 90, 120, 180]) +
    pd._terms() +
    pd._elements(pd.SIG_OBJECTS, pd.A, [0]) +
    pd._elements(pd.SIG_OBJECTS, pd.C, [0])
)

sigs = [x for x in sigs if not is_node(x['id'])]
proms = [x for x in proms if not is_node(x['id'])]

rows = []
for prom in proms:
    for sig in sigs:
        if prom['id'] == sig['id']:
            continue
        if base_object_id(prom['id']) == base_object_id(sig['id']):
            continue
        arc = norm180(sig['ra'] - prom['raZ'])
        if abs(arc) <= 1e-12:
            continue
        if abs(arc) > 100:
            continue
        if is_plain_planet_pair(prom['id'], sig['id']):
            raw_delta = sig['lon'] - prom['lon']
            if not pass_display_window(raw_delta, arc):
                continue
        rows.append([arc, prom['id'], sig['id'], 'Z'])

rows.sort(key=lambda row: (abs(row[0]), row[0], row[1], row[2]))

for row in rows:
    jd = ptolemy_jd_from_arc(abs(row[0]), birth_local_dt)
    row.append(format_utc_like_datetime(jd))
```

## 13. 前端显示与方法切换

当前前端不是“改一下下拉框就立即改整张表”，而是：

1. 用户选择 `推运方法`
2. 用户选择 `度数换算`
3. 点击 `计算`
4. 前端把 `pdMethod/pdTimeKey` 发给后端
5. 后端返回新的 `chartObj`
6. 主限法表格根据 `chartObj.params.pdMethod/pdTimeKey` 渲染

当前对应文件：

- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js`
- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js`

当前页面支持：

- `Horosa原方法`
- `AstroAPP-Alchabitius`
- `Ptolemy`

并且 AI 导出、设置恢复、页面表格都已同步这两个设置值。

## 14. 可复现验证脚本

当前仓库内已有对照脚本：

- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/scripts/compare_pd_backend_rows.py`

它会：

- 读取 AstroApp 抓取样本
- 本地重新起盘
- 用同一 `promissor_id + significator_id + signed_aspect` 分桶
- 在桶内按最近 Arc 配对
- 输出 Arc / 日期误差统计

## 15. 当前验证结果

现成回归结果：

- `runtime/pd_reverse/selfcheck_astroapp60_summary.json`
  - `cases = 60`
  - `rows_matched = 20196`
  - `arc_mae = 0.0006809858679562894`
  - `arc_p95 = 0.0020499340130015753`
  - `date_mae_days = 0.36691450927855057`
  - `date_p95_days = 1.0361553514376283`

- `runtime/pd_reverse/uicheck_rows_120_summary.json`
  - `cases = 120`
  - `rows_matched = 39981`
  - `arc_mae = 0.0006701327243638771`
  - `arc_p95 = 0.002102649671769541`
  - `date_mae_days = 0.36411480203960234`
  - `date_p95_days = 1.0394334513694048`

- `runtime/pd_reverse/local_backend_vs_astroapp_rows_all300_after_displayfilter_summary.json`
  - `cases = 300`
  - `rows_matched = 102032`
  - `arc_mae = 0.0006788783645654379`
  - `arc_p95 = 0.0023601959956351948`
  - `date_mae_days = 0.37174043900477144`
  - `date_p95_days = 1.1138273822143674`

## 16. 复刻时必须注意的三个坑

### 16.1 不要把 Arc 当成单纯黄经差

当前复刻核不是：

- 纯黄经差
- 纯 RA 差
- 纯 OA 差

而是：

- `应星 = true latitude 的 ra`
- `迫星 = zero latitude 的 raZ`

### 16.2 日期不要直接按固定回归年乘

若直接：

```text
jd = birth_jd + |arc| * 365.2421904
```

Arc 可能仍然很近，但日期会慢慢漂。

### 16.3 只比较同一对象集

Horosa 自有扩展对象，如：

- 紫气
- 月孛
- 某些 Horosa 扩展虚点

这些如果直接和 AstroApp 混比，会让人误判为“算法没对齐”。  
比较时必须先限定到 AstroApp 实际输出的对象集。

## 17. 当前工程给出的最终做法

如果你的目标是“在 Horosa 页面里保留原版 Horosa，同时给用户一键切到 AstroApp 复刻”，当前工程的方案就是：

- `Horosa原方法`
  - 完整保留原版 Horosa `zodiaco主限法`
- `AstroAPP-Alchabitius`
  - 使用本文档描述的复刻核
- 页面、设置、AI 导出三处共用同一组 `pdMethod/pdTimeKey`

这也是当前仓库里已经落地并可运行的结构。

## 18. 一句话总结

当前 AstroApp 复刻核的核心不是“照搬传统书本里的单一 RA/OA 公式”，而是：

```text
Arc = norm180( sig.ra(true_lat) - prom.raZ(zero_lat_after_aspect) )
```

再叠加：

- `|arc| <= 100`
- 普通行星对的显示窗裁剪
- `|Arc|` 排序
- 基于周年日插值的 Ptolemy 日期换算

只要这四层同时满足，当前本地实现就能复现现在这套 Horosa 中的 `AstroAPP-Alchabitius` 分支。
