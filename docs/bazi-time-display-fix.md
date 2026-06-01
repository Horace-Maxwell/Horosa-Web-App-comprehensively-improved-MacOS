# 八字「直接时间 / 真太阳时」显示修复

> 首发版本：**v2.1.3 / 2.1.3-runtime1**
> 日期：2026-05-26
> 范围：八字（BaZi）排盘页面的时间显示。切换左栏「时间算法」时，「真太阳时」显示会跳（直接时间模式显示直接时间、真太阳时模式显示真太阳时），且标签写死成「真太阳时」。
> 目标：**直接时间与真太阳时两个时间都恒定显示、不随切换跳动**；切换只改变「计算基准」；排盘按所选基准计算。
> 面向 Windows 端同步：说明改了哪里、为什么、以及 Windows 打包需注意什么。

---

## 1. 根因（关键，务必先看）

**八字盘是前端本地计算的，不是后端排盘。**

- `components/cntradition/BaZi.js` 的 `fetchBaziCached` / `fetchBaziDirectCached` **先调用 `buildLocalBaziResult`**（`utils/baziLunarLocal.js`，基于 `lunar-javascript`）。只有当本地计算**抛异常**（极少数老旧边缘日期）才回退到后端 `/bazi/birth`。
- 因此正常情况下，页面显示的 `nongli` 完全来自**本地 JS 计算**，后端响应根本不参与显示。
- 本地计算里 `nongli.birth = applyApparentSolarTime(rawParts, params).toYmdHms()`，而 `applyApparentSolarTime` **只在 `timeAlg===0`（真太阳时）时**做「经度 + 时差(EoT)」校正、其它模式原样返回 → `nongli.birth` 随 `timeAlg` 变化 → 显示「真太阳时」时回退到这个会变的值 → **跳**。
- 本地 `nongli` 原本**没有**独立的「直接时间 / 真太阳时」字段，显示组件只能退而读 `nongli.birth`。

> 之前一版只改了 Java 后端 + 显示组件，但因为页面走本地计算，后端改动对显示不起作用——这是最初没修好的原因。

---

## 2. 修复内容

### 2.1 前端本地计算（**主修复**）
`Horosa-Web/astrostudyui/src/utils/baziLunarLocal.js` → `buildLocalBaziResult()`：
始终额外计算并写入两个**与 `timeAlg` 无关**的字段：
- `nongli.clockTime` = 原始输入（钟表/直接时间），`solarFromParts(rawParts)`；
- `nongli.solarTime` = 真太阳时，**强制**按真太阳时校正：`applyApparentSolarTime(rawParts, { ...params, timeAlg: 0 })`。

排盘基准（`nongli.birth` 与四柱、大运等）**保持不变**，仍按所选 `timeAlg` 计算。

### 2.2 Java 后端（回退路径 + 一致性）
`Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model/BaZi.java` → `setup()`：
同样始终在 `nongli` 里写 `clockTime`（`oldBirth`）与 `solarTime`（用 `RealSunTimeOffset` 始终算真太阳时），计算基准不变。
- 覆盖 `/bazi/birth`（`BaZi`）与 `PaiBaZiController`（`BaZiDirect extends BaZi`，走 `super()` 继承）。
- 作用：本地计算抛异常回退到后端时、以及 AI 导出/分析走后端取数时，字段口径与前端本地一致。

### 2.3 显示统一（4 处）
全部改为读取 `nongli.clockTime` / `nongli.solarTime`，统一展示「**直接时间 / 真太阳时 / 计算基准**」；`直接时间` 在缺字段时回退到表单输入（永远稳定）：
- `components/cntradition/PaiBaZi.js` —— 新 UI 中栏表头；
- `components/cntradition/BaZiAppInfoPanel.js` —— 新 UI 右栏信息卡；
- `components/cntradition/BaZiLegacyView.js` —— 旧星阙 UI 表头；
- `components/cntradition/BaZi.js` —— AI 结构化快照（同时修掉了「时间算法：直接时间…真太阳时：<直接时间>」自相矛盾）。

`计算基准` 文案映射：`{0:真太阳时, 1:直接时间, 2:春分定卯时, 3:地方卯时}`。

---

## 3. 数据契约（前后端一致）

| 字段 | 含义 | 是否随 timeAlg 变 |
| --- | --- | --- |
| `nongli.clockTime` | 直接 / 钟表时间（输入原值） | 否（恒定） |
| `nongli.solarTime` | 真太阳时（始终校正） | 否（恒定） |
| `nongli.birth` | **排盘计算基准时间**（直接时间模式≈钟表；真太阳时模式=真太阳） | 是 |
| `timeAlg` | 0=真太阳时 / 1=直接时间 / 2=春分定卯时 / 3=地方卯时 | — |

显示规则：`直接时间` 取 `clockTime`、`真太阳时` 取 `solarTime`、`计算基准` 取 `timeAlg` 文案。三者中只有「计算基准」随切换变化，时间值不跳。

---

## 4. 验证

- **前端本地计算单测**（throwaway，已删）：固定生日 `1990-05-20 08:56:00`、zone `+08:00`，对多个经度跑两种 timeAlg：

  | 地点 | 经度 | 直接时间(clock) | 真太阳时(solar) | 差值 |
  | --- | --- | --- | --- | --- |
  | 乌鲁木齐(西) | 87°E | 08:56:00 | 06:47:36 | −2h08m |
  | 北京 | 116.3°E | 08:56:00 | 08:44:52 | −11m |
  | 用户测试点 | 119.3°E | 08:56:00 | 08:56:52 | +52s |
  | 子午线 | 120°E | 08:56:00 | 08:59:36 | +3m36s（仅均时差 EoT） |
  | 远东 | 135°E | 08:56:00 | 09:59:36 | +1h03m |

  - clock / solar 在 `timeAlg=0` 与 `timeAlg=1` 下**完全一致（不跳）**；`birth`（排盘基准）随模式变。
  - **只要经度偏离 +08:00 的 120°E 子午线，真太阳时 ≠ 直接时间**（西边更早、东边更晚，幅度随经度差变化）；即使正好在 120°E，也会因均时差(EoT)相差几分钟。这正是「经纬度与北京时间不同时两者应不同」的要求。
- **后端实测**（签名明文直连 `/bazi/birth`）：两模式 `clockTime`/`solarTime` 一致。
- 编译：`astrostudycn`（JDK 17）编译通过；前端 `build:file` 通过。
- in-app 预览：经 `Horosa_OneClick_Mac.command` 启动（本地计算 + 重建前端包）后在八字页核对。

> 注：本地用近似 `equationOfTime`、后端用 `RealSunTimeOffset` 表，真太阳时数值会差几十秒（如本地 06:17:32 vs 后端 06:15:32），但**都稳定、不跳**。八字盘默认走本地计算，所以页面显示的是本地值。

---

## 5. Windows 端注意事项

1. **前端是共享的**：Windows 打包同一份 `astrostudyui`，`baziLunarLocal.js` 的本地修复随包生效——这是**关键修复**，无需 Windows 特有处理。
2. **后端共享**：Windows 若打包 `astrostudyboot.jar`，用当前源码重编即带上 `BaZi.java` 改动；该改动是纯 Java（`RealSunTimeOffset` 表 + 日期运算），无平台相关依赖。
3. **不要只改后端**：八字盘默认走前端本地计算，单改后端在 Windows 上同样不会生效——必须包含 `baziLunarLocal.js` 的改动。
4. **其它技法**：本次只处理八字。紫微早已正确（按 `timeAlg` 切标签）；星盘/星运/七政等无「时间算法」开关，不受影响；占卜类（奇门/六壬/太乙等）不在范围内。

---

## 6. 受影响文件清单

```
Horosa-Web/astrostudyui/src/utils/baziLunarLocal.js                         (主修复：本地计算加 clockTime/solarTime)
Horosa-Web/astrostudyui/src/components/cntradition/PaiBaZi.js                (中栏表头)
Horosa-Web/astrostudyui/src/components/cntradition/BaZiAppInfoPanel.js       (右栏信息卡)
Horosa-Web/astrostudyui/src/components/cntradition/BaZiLegacyView.js         (旧 UI 表头)
Horosa-Web/astrostudyui/src/components/cntradition/BaZi.js                   (AI 结构化快照)
Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model/BaZi.java  (后端回退路径)
```
