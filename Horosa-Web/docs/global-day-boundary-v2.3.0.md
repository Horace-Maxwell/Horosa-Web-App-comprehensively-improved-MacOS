# 全局日界点（早/晚子时换日）+ 自动更新稳定化 (v2.3.0)

## 一、背景

23:00–24:00（晚子时）的日柱归属——「23点后日柱为次日（子初换日）」vs「24点后日柱为次日（子正换日）」——历来是术数中的分歧。在 v2.3.0 之前，Horosa 的换日开关 `after23NewDay` 已存在，但：

1. **散落在各技法的局部 options 里**，默认值不统一（多数 `0`，三式 `1`），没有全局入口。
2. **前端本地四柱 `buildLocalBaziResult` 硬编码 `setSect(1)`**，完全无视 `after23NewDay`——八字/河洛/参评数选「24点换日」不生效（核心 bug）。
3. **太乙本地四柱 `buildTaiyiBaziLocal`** 没把 `after23NewDay` 传进去，日柱永远 `setSect(1)`。
4. **Java 后端 4 个控制器硬编码 `false`**（`ChartController:75`/`JieQiController:64`/`QueryChartController:40`/`NongliHelper:680`），导致主盘/七政底盘/紫微底盘/28宿/印度/分至/历史/推运的日柱**恒按子正算**——与新默认子初对不上。
5. **奇门 `buildGanzhiForQimen`** 在前端拿到后端已换日的 `nongli.dayGanZi` 后又 `nextGanZhi` 一次——23点+默认设置下出现**双重换日**（次次日）的潜在 bug。
6. **后端 vendored Python 引擎**（wuzhao/nanji/shaozi系/fendjing/shenyishu/qizheng/wangji）日柱硬编码 `if hour==23: day+1`、或公历日直算（恒子正），前端 payload 不传、service 不转发——用户选「24点换日」对这些技法**完全无效**。

同时，应用内**自动更新**（自研 OTA：`reqwest` + GitHub Release + SHA256 + `ditto` 替换 + 公证装订）虽然实现成熟，但 `auto_check_updates` 偏好定义了却**从不被 setup 闭包消费**——所谓"自动检查"从来没生效过，所以体感"自动更新不工作/不稳定"。

## 二、新增「全局设置 · 日界点」

- menu「设置」下拉新增「全局设置」按钮（同 UI 风格），点开 `XQModal`，含单选 `XQSegmented`：
  - 「23点后日柱为次日（默认）」= 子初换日 = `after23NewDay=1`
  - 「24点后日柱为次日」= 子正换日 = `after23NewDay=0`
- 偏好存储：`models/app.js` 的 `dayBoundary`（`'after23'`/`'after24'`），通过现有 `globalSetup` localStorage 通道持久化。
- 新建 `utils/dayBoundary.js`：`normalizeDayBoundary`/`dayBoundaryToAfter23NewDay`/`defaultAfter23NewDay()`（实时读 localStorage，可在模块常量、astro model、纯工具里调用）。
- 关系（已与用户对齐）：**全局默认 + 各技法可单独覆盖**（B 方案）。各技法保留自己的换日下拉，初始默认从全局回退；用户单盘改 → 仅影响该盘。

## 三、改动清单（按层）

### 1. 前端（纯 JS，`npm run build` 即生效）

- **bug 修复**：`utils/baziLunarLocal.js:637` 的 `setSect(1)` 改为按 `params.after23NewDay`（默认 1=维持现状）决定 `setSect(1/2)`，覆盖八字/河洛/参评数/preciseCalcBridge 本地 nongli。
- **bug 修复**：`components/taiyi/TaiYiCalc.js:136` `buildTaiyiBaziLocal` 补传 `after23NewDay`。
- **bug 修复**：`components/dunjia/DunJiaCalc.js:1036` 移除奇门 `buildGanzhiForQimen` 的二次进位（nongli 已按 `after23NewDay` 换日，前端不可再换；附详细注释防回退）。三式合一复用 `DunJiaCalc`，自动受益。
- **各技法默认值统一**接 `defaultAfter23NewDay()`（实时读全局；record/单盘值优先）：`models/astro.js`（两处 fields）、`components/{dunjia/DunJiaMain, taiyi/TaiYiMain, guazhan/GuaZhanMain, ziwei/ZiWeiMain, jinkou/JinKouMain, lrzhan/LiuRengMain, sanshi/SanShiUnitedMain, shusuan/{CanPingMain, HeLuoMain}}`、`utils/aiAnalysisContext.js`（3处）。
- **fieldsToParams 补传 `after23NewDay`**：`models/astro.js` fieldsToParams（主 `/chart`，波及七政四余/紫微底盘/28宿/中点/推运）、`components/hellenastro/AstroChart13.js`、`components/astro/IndiaChart.js`、`components/guolao/GuoLaoChartMain.js`、`components/jieqi/JieQiChartsMain.js` `genParams`、`utils/preciseCalcBridge.js` `JIE_QI_YEAR_KEYS`、`utils/aiAnalysisContext.js` `buildCaseSnapshotParams`。
- **Phase 2 前端 payload 补传**：`components/kinastro/KinAstroMain.js` `buildPayload`（一处覆盖 shaozi/tieban/chunzi/fendjing/nanji/beiji/xianqin/cetian 等 kinastro 系）、`components/wuzhao/WuZhaoMain.js`、`components/huangji/HuangJiMain.js`、`components/shenyishu/ShenYiShuMain.js`；qizheng 经 `GuoLaoChartMain` 的 `...params` 已自动带上。
- 新增「全局设置」UI：`components/homepage/PageHeader.js` 加 `globalsettings` 菜单项 + XQModal；`layouts/app.js` 透传 `dayBoundary`。

### 2. Java 后端（**需重编 `astrostudyboot.jar`**）

`Horosa-Web/astrostudysrv/`：

- `astrostudycn/.../ChartController.java:75` ：`boolean after23NewDay = ConvertUtility.getValueAsInt(args.get("after23NewDay"), 1) == 1;` （/chart 主盘）
- `astrostudycn/.../JieQiController.java:64` ：同（节气盘）
- `astrostudycn/.../QueryChartController.java:40` ：同（历史命例 /querychart）
- `astrostudy/.../NongliHelper.java:680` ：`getNongLi(ad, birth, zone, lon, ConvertUtility.getValueAsInt(params.get("after23NewDay"), 1) == 1)` （/chart13 印度盘/13宫）

重编命令（JDK 17）：

```bash
JH=$(/usr/libexec/java_home -v 17)
JAVA_HOME=$JH mvn -f Horosa-Web/astrostudysrv/astrostudy/pom.xml install -DskipTests
JAVA_HOME=$JH mvn -f Horosa-Web/astrostudysrv/astrostudycn/pom.xml install -DskipTests
JAVA_HOME=$JH mvn -f Horosa-Web/astrostudysrv/astrostudyboot/pom.xml clean package -DskipTests
```

（v2.3.0 已重编，jar mtime = `target/astrostudyboot.jar`。）

### 3. 后端 Python（vendored，**需重打离线 runtime 包**；本地 PYTHONPATH 直接生效）

7 个技法组：

| 技法 | 模式 | 引擎文件 | service |
|---|---|---|---|
| wuzhao（五兆） | A：加 `after23_new_day` 参数 + `and` 条件 | `vendor/kinwuzhao/config.py:120/140`（gangzhi1/gangzhi） | `astropy/websrv/webwuzhaosrv.py` 取 `after23` + 传引擎 |
| nanji（南极神數） | A | `vendor/kinastro/astro/nanji/calculator.py:465 from_solar_datetime` | `webnanjisrv.py` 调用补 `after23_new_day=to_int(...)` |
| shaozi/tieban/chunzi | B：算日柱前 `hour==23 and after23` 时日期+1（时支保留原 hour） | `vendor/kinastro/astro/shaozi/calculator.py:221 calculate_ganzhi_from_datetime`（一处引擎覆盖 3 service） | `webshaozisrv.py`/`webtiebansrv.py`/`webchunzisrv.py` 调用补 `data.get("after23NewDay", 1)` |
| fendjing（鬼谷分定经） | B | `vendor/kinastro/astro/fendjing/fendjing_calculator.py:114` | `webfendjingsrv.py` |
| shenyishu（神易数） | B（日柱进卦，关键） | `vendor/shenyishu/shenyishu.py:300 __init__` | `webshenyishusrv.py` |
| qizheng（七政四余 kin 版） | service 层 jd 调整 | （引擎不动） | `webqizhengkinsrv.py` 在调 `compute_shensha`/`get_bazi_stems_branches` 前 `jd_for_day = jd + (1.0 if hour==23 and after23 else 0.0)`，star ephemeris jd 不动 |
| wangji（皇极经世） | thread-local（避免深透传：`webwangjisrv → display_pan/wanji_four_gua → ... → gangzhi`） | `vendor/kinwangji/kinwangji/wanji.py` + `jieqi.py`（各加 `_AFTER23_LOCAL` + `set_after23_new_day`/`_is_after23_active`，3 处 `if hour==23` 加 `and _is_after23_active()`） | `webwangjisrv.py` 在 `wanji_four_gua` 调用前 import 两个 `set_after23_new_day` 并 set |

**豁免**（agent 审计 + 工程师复核确认）：

- **奇门 kinqimen / 太乙 kintaiyi / 金口 kinjinkou**：日柱由前端 nongli/overlay 决定，引擎内部 `hour==23` 不进入展示，不改。
- **京房/荆诀 jingjue**（纯 seed 起卦）、**太玄 taixuan**（cnlunar 第三方固定 23 点换日、不可参数化）、**北极 beiji**（不显示日柱）、**演禽 xianqin**（农历定宫，不算干支日柱）：不涉及/不可控/收益低。
- **死代码/死副本**：`kinastro/astro/bazi/calculator.py`、`damo`、`diqiyijue`、`liuyao_lifetime`、`kinwangji` 顶层副本、`kinastro/astro/wangji/*`——审计确认无 service import，不改。
- **黄历**：固定 `time=12:00:00`，永不触 23 点边界，天然豁免。
- **`bazi/constants.py:571`**：是**时支索引**（子时 23–01 点→0），不是日柱换日，**不要动**。

### 4. 自动更新（Tauri OTA P0，**需重编 launcher**）

诊断结果：**不是** Tauri 官方 `tauri-plugin-updater`，而是 `main.rs` 内自研 OTA（`reqwest` + GitHub Release + SHA256 + bash helper + ditto 替换 + Apple 公证装订）。已**确认不要迁去官方 plugin**——自研方案承担 app + 独立 runtime.tar.gz 双更新 + 双向回滚 + 离线 pkg 兜底，官方做不到。

**根因 A（修复，本版本）**：`auto_check_updates: bool` 在 `main.rs:257/286` 定义且默认 `true`，但 `setup` 闭包从不消费它——所谓「自动检查更新」开关**从来没生效**。这就是"不稳定/不工作"的核心。

修复（`Horosa_Desktop_Installer/src-tauri/src/main.rs` setup 闭包末尾、`Ok(())` 前）：

```rust
{
    let app_handle = app.handle().clone();
    thread::spawn(move || {
        thread::sleep(std::time::Duration::from_secs(10));
        if !load_preferences(&app_handle).auto_check_updates { return; }
        // 静默检查 plan，仅当发现新版才调原 check_for_updates 弹框；
        // 无更新/网络失败 静默写日志（eprintln!），避免每次启动打扰。
        ...（详见 main.rs setup 末尾插入块）
    });
}
```

重编 launcher：`cd Horosa_Desktop_Installer/src-tauri && cargo build --release`（或走完整 `npm run tauri build`）。

**P1-P3（后续可选加强，未本版做）**：

- P1 GitHub API 回退通道补 SHA256（`main.rs:3539-3575` 回退路径目前 `app_sha256=None`，跳过校验；可从 API 的 asset `digest` 字段填回）。
- P2 把 `in-app` 升级路径纳入 `release_preflight.sh` + `verify_github_release_end_to_end.sh`（沙盒里真跑一次 helper）。
- P3 `/Applications` 提权 UX 加固（升级前明确告知会要求管理员密码）。

## 四、验证

| 层 | 验证 |
|---|---|
| 前端编译 | `npm run build` exit 0 |
| 单测 | `npx umi-test --runInBand` 28 suites / 129 tests 全过 |
| 算法层 | `node` 直调 `lunar-javascript` 验证 `setSect(1)`/`setSect(2)` 方向：2024-01-15 23:30 → 己卯 vs 戊寅（与 2024-01-16/01-15 日柱对照吻合） |
| Java 编译 | `mvn clean package -DskipTests` exit 0；新 `astrostudyboot.jar` mtime 验证 |
| 后端 Python boot | `./stop_horosa_local.sh && ./start_horosa_local.sh` exit 0，boot 自检 import 17 个 kentang service 全过 |
| 引擎直调（shaozi） | embedded python 直调 `calculate_ganzhi_from_datetime(dt, after23)`：23:30 a23=1 → 日柱 **己卯**；a23=0 → **戊寅**；22:30 非子时两值同 |
| 引擎直调（wangji） | embedded python 直调 `wanji.gangzhi(2024,1,15,23,30)` + `set_after23_new_day(1/0)`：a23=1 日柱 **己卯**、a23=0 **戊寅**；jieqi.gangzhi 同；22:30 非子时两值同 |
| UI | 浏览器实测「设置 → 全局设置」Modal 完整：两个单选 + 当前态正确 |
| 八字单盘开关 | 八字页显示「23点算第二天」反映全局 after23 ✓ |

最终用户验收：在某个全局设置下，把出生/起盘时间在 23:00 前后几分钟移动，四柱日柱及其下游（奇门局数/三元/六壬课/金口/太乙/河洛日宫/参评日宫/七政底盘日柱/紫微底盘/28宿/印度盘等）相应跳变。

## 五、是否重编 / 重打

| 部件 | 本版本是否需要 |
|---|---|
| 前端 `dist-file` | 是（`npm run build`） |
| `astrostudyboot.jar` | **是**（含 ChartController/JieQiController/QueryChartController/NongliHelper 4 处 Java 改动） |
| 离线 runtime.tar.gz（vendor + websrv） | **是**（含 7 个引擎 + 7 个 service 的 Python 改动）。脚本：`Horosa_Desktop_Installer/scripts/package_runtime_payload.sh`（rsync `Horosa-Web/vendor/` + `Horosa-Web/astropy/websrv/`） |
| launcher（`Horosa_Desktop_Installer` 的 Tauri app） | **是**（含 main.rs 自动检查更新接线 P0） |

## 六、Windows 同步要点

见 `docs/windows-sync-handoff.md` v2.3.0 条目。Win 端必须：

1. 同步 `Horosa-Web/` 下所有前端 + Python vendor + Java 源（共享）。
2. Java 重编 jar（JDK17）。
3. 前端 `npm run build`。
4. Windows Electron 壳的「自动检查更新」接线属 Win 端自理（main.rs 的 Tauri P0 修复仅适用 macOS Tauri 壳）。
