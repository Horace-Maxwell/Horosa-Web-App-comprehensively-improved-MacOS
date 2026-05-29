# 占星地图（ACG / 地理占星）实现与升级技术文档

> 功能位置：**辅盘 → 占星地图**（内部 key `locastro`，子组件 `AstroAcg`）。
> 性质：标准地理占星（astrocartography）——在世界地图上叠加行星的四轴线（中天/天底/上升/下降）、
> 地理参考线、Parans（交映纬线）、Local Space（本地空间）线，并支持点击任意地点出「落点分析」。
> 本文是**给 Windows 端同步**与**本仓后续维护**的权威参考，含算法、数据契约、关键坑。

---

## 一、架构与数据流

```
前端 AstroAcg (src/components/acg/AstroAcg.js)
  ├─ POST /location/acg       → 全部线条几何
  └─ POST /location/acgpoint  → 落点 within-orb 行星 + 迁移四轴
        │  Java AcgController(/location/*) → AstroHelper.getAcg / getAcgPoint
        │  → Python CherryPy AcgSrv (astropy/websrv/webacgsrv.py, 挂在 /location)
        │  → astropy/astrostudy/acg/ACGraph.py（核心计算，基于 flatlib + swisseph）
        ▼
  AcgD3Map (src/components/acg/AcgD3Map.js)  —— D3-geo 渲染
   - 内置 world.geo.json（Natural Earth 110m 国界，开源数据，自 TopoJSON 转 GeoJSON）
   - 行星四轴线 / 地理线 / Parans / Local Space / 落点标记
   - 明暗双主题、4 种底图样式、等距/墨卡托投影
  AcgPointPanel (src/components/acg/AcgPointPanel.js) —— 落点抽屉（命中行星-轴 + 解读 + 迁移四轴）
  interpretations.zh.js —— 自备简体中文解读（公版含义原创撰写）
```

Java 仅做**透明转发**，返回结构经 `TransData.set` 包成顶层 `Result`，前端读 `data.Result`。

### 计算输出 JSON（`/location/acg`）
```jsonc
{
  "meta": { "gmst": <deg>, "obliquity": <deg>, "jd": <float>, "birth": {"lat":<deg>,"lon":<deg>} },
  "planets": { "Sun": {
      "ra":<deg>,"decl":<deg>,"lon":<eclLon>,"lat":<eclLat>,
      "lines": { "mc":{"lon":<deg>}, "ic":{"lon":<deg>},
                 "asc":[{"lat","lon"}...], "desc":[...], "ls":[...] } }, ... },
  "geo": { "equator":[...], "ecliptic":[...], "tropicN":[...], "tropicS":[...] },
  "parans": [ {"lat":<deg>,"a":"Sun","aEvent":"rise","b":"Mars","bEvent":"mc","type":"RSCA"}, ... ]
}
```
`/location/acgpoint`（额外入参 `clickLat/clickLon/orb`）→ `{lat,lon,orb,hits:[{planet,angle,orb}],relocAngles:{Asc,Desc,MC,IC}}`。

---

## 二、算法（解析法，闭式；约定经度东正、归一化到 (−180,180]）

- **GMST**：`theta0 = swisseph.sidtime(jd_ut) * 15`（度；失败回退用 `swisseph.houses` 的 ARMC − 出生经度）。
- **RA/Dec**：每个天体取 `swisseph.cotrans([lon, lat, 1], -eps)`（`eps`=真黄赤交角，来自 `calc_ut(jd, ECL_NUT)`）。对所有对象通用，含计算点（月孛/紫炁）。
- **MC/IC 线**：`λ_MC = norm180(α − theta0)`；`λ_IC = λ_MC + 180`（竖直经线）。
- **ASC/DSC 线**：地平时角 `cos H = −tanφ·tanδ`，`λ_asc = norm180(α − H − theta0)`，`λ_desc = norm180(α + H − theta0)`。
  有效带 `|φ| ≤ 90−|δ|`。**逐 0.5° 采样并在带边界加精确端点**（`H=0`→落在 MC 经度、`H=180`→落在 IC 经度），曲线因此平滑、且"钩子"在极区闭合到 MC/IC 竖线。
- **地理线**：赤道 φ=0；南北回归线 φ=±eps；黄道（天顶轨迹）`φ(λ)=atan(tan eps · sin(theta0+λ))`。横线一律**多点采样**（见坑①）。
- **Parans**：天体对×事件（rise/set/mc/ic）令两者 LST 相等解纬度；mc/ic 一方为定值时闭式、rise/set×rise/set 数值求根；`|纬|≤66`。
- **Local Space**：出生地按方位角 `Az = atan2(−cosδ sinH0, cosφ0 sinδ − sinφ0 cosδ cosH0)` 发大圆，采样 0..360°。
- **落点 report**：把星盘重定位到点击点，逐天体求其黄经到本地 ASC/DESC/MC/IC 的最小夹角，列 within-orb。

自洽校验：在算出的 ASC/MC/DESC 点重定位，太阳（黄纬≈0）落在对应轴偏差 0.0000°；落点命中偏差 ~0.003°。

---

## 三、前端渲染要点

- **D3-geo + 内置 GeoJSON**：`d3.geoEquirectangular()`（默认，MC 竖直）/`geoMercator()`；`geoPath`+`geoGraticule10`；`d3.zoom` 缩放。**零新 npm 依赖**（复用已装 `d3@7`，含 d3-geo/zoom）。
- **明暗双主题**：读 `:root[data-horosa-appearance]`（由 `src/utils/appearance.js` 维护，值 `dark`/`light`），`MutationObserver` 实时切换。亮=浅海陆+白描边+加深行星色；暗=深底+亮线+深底浅框胶囊。
- **标注胶囊**：每条线端点一个圆角矩形（`chipBg`/`chipBorder` 随主题反色）+ 字形（ywastro 字体）。
- **地图样式**：`STYLES`（标准/简约/政区/单色），与明暗正交，仅改地形配色。
- **Parans 三态**：关 / 日月（只显示含日月的，前端过滤）/ 全部；并按 1° 纬度去重 + 细淡显示。

---

## 四、关键坑（务必照搬 / 后人勿踩）

1. **横向整宽线退化 bug（最坑）**：`LineString [[-180,lat],[180,lat]]` 两端都落在反子午线上，
   `d3.geoPath` 会把它裁成两个零长度点（线不显示），前端 `splitAtDateline` 还会对 Δlon=360 算出 `t=0/0=NaN`。
   → 赤道/回归线/Parans 这类整宽横线**必须多点采样**（`-179..179`，后端 `_hLine`、前端 paran 同理）。竖直 MC/IC 两点线不受影响。
2. **ASC/DSC 断裂**：近极区临界处 λ 随 φ 变化极快，1° 采样会误判跨180°断线、且升落曲线不与 MC/IC 闭合。
   → 后端 0.5° 采样 + 带边界精确端点；前端 `splitAtDateline` 在 ±180 处**插值边缘点**（分段贴边，不留缝）。
3. **SVG 文字被全局 `text { stroke }` 描边**：本仓有全局规则给 SVG `text` 上 1px 描边（占星盘字形共用）。
   标注若不显式覆盖会继承该描边、字形发糊。**CSS 规则会盖过 presentation 属性**，所以必须用 **inline `style('stroke','none')`**（`attr('stroke','none')` 无效）。
4. **`getAcg` 改 `requestNoCache`**：Java 默认 `request()` 按参数缓存一天；改后端 ACGraph 后同一张盘会命中旧缓存看到旧结果。
   ACG 计算很快，已改 `requestNoCache`。**这是 Java 改动 → 必须重编 `astrostudyboot.jar`**（JDK17，`mvn -f astrostudy install` + `astrostudyboot clean package`；`clean` 必须）。
5. **嵌入式 Python**：本地用 `runtime/mac/python/bin/python3`（PYTHONPATH=`flatlib-ctrad2:astropy:vendor`），裸跑别的 python 缺 chart 依赖会崩。

---

## 五、Windows 同步要点

- **共享业务码在 `Horosa-Web/`**，全部改动都在这里：
  - Python：`astropy/astrostudy/acg/ACGraph.py`、`astropy/websrv/webacgsrv.py`（加 `acgpoint`）。
  - Java：`astrostudysrv/.../controller/AcgController.java`（加 `/acgpoint`）、`.../helper/AstroHelper.java`（`getAcg→requestNoCache` + `getAcgPoint`）。
  - 前端：`astrostudyui/src/components/acg/{AstroAcg.js, AcgD3Map.js, AcgPointPanel.js, interpretations.zh.js, world.geo.json}`。
- **动了 Java → Windows 也必须重编 `astrostudyboot.jar`**（坑④）。
- **动了前端 → `npm run build` 然后 `npm run build:file`**（顺序,勿并行）。`world.geo.json` 是源码资产,随源码走,会被打进包。
- 无新增 npm 依赖、无新增 Python 依赖、无新增后端路由端口（`acgpoint` 复用 `/location` 挂载）。

---

## 六、改动文件清单（本次升级）
- 后端：`astropy/astrostudy/acg/ACGraph.py`（重写为解析法 + ls/parans/pointReport + 多点横线 + 曲线平滑闭合）、`astropy/websrv/webacgsrv.py`（`acgpoint`）、`astropy/astrostudy/acg/validate_acg.py`（回归自检，见 §七）。
- Java：`AcgController.java`、`AstroHelper.java`（重编 jar）。
- 前端：`AstroAcg.js`（开关/样式/落点接线）、新增 `AcgD3Map.js`/`AcgPointPanel.js`/`interpretations.zh.js`/`world.geo.json`。

## 七、回归自检 / 算法对齐（）

四轴线是**天文学定义**：MC/IC=行星正在上/下中天（位于本地子午线）；ASC/DESC=行星正在升/落（真高度=0）。
`validate_acg.py` 用 Swiss Ephemeris **权威的地平坐标函数 `swisseph.azalt()`** 反验 ACGraph 算出的线是否满足这些定义——
`azalt` 内部用它自己的恒星时，**与 ACGraph 的 GMST/公式完全独立**，因此是对算法的独立精度校验；
又因本项目与同类专业软件都用**同一套 Swiss Ephemeris**，本检验即"与业界标准对齐"（比肉眼对照地图精确得多）。

运行（任意平台，路径自适配）：
```
runtime/mac/python/bin/python3 Horosa-Web/astropy/astrostudy/acg/validate_acg.py   # Windows 用对应运行时 python
```
覆盖 3 张盘（北京 / 圣保罗南半球 / 纽约）× 10 行星。**期望：worst < 1e-3°（实测 0.000000°），退出码 0=PASS。**
改动 `ACGraph.py` 的解析法后**必跑此自检**；可接入 CI / 发布前 gate。
（范围：覆盖四轴线这一 ACG 定义性线条；Local Space/Parans/地理线由同一套球面天文公式与已校验的 RA/Dec·GMST 机制派生。）
