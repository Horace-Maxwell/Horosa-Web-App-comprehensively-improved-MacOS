# arm64 原生库兼容性加固（Risk 1）

> 日期：2026-05-24
> 范围：Java 后端 `image` 与 `iot` 模块中，x86_64-only JNI 原生库在 Apple Silicon（arm64）上的失败处理
> 性质：**只改失败路径，不改成功路径**——在原生库可正常加载的平台（x86_64 mac / Linux / Windows）上行为逐字节不变
> 给后续 agent / 维护者同步用

---

## 1. 背景

在「全新 M 系列 Mac 拿到即用」的发布风险评估中，发现后端打进了**只有 x86_64、没有 arm64 切片**的 JNI 原生库：

- `image/.../org/pngquant/libimagequant.jnilib` —— 仅 x86_64（PNG 调色板压缩）
- `iot/.../gnu/io/librxtxSerial-x86_64.jnilib` —— i386/x86_64/ppc（串口 / IoT）
- OpenCV：来自 Maven 依赖 `org.openpnp:opencv:3.4.2-2`（2018 年构建，**不含 Apple Silicon 原生库**）

而内置 JRE 是 arm64（`java` 实测 arm64 + Developer ID + hardened runtime 签名）。arm64 进程**无法加载 x86_64 dylib**，所以这些库在 M 芯片上加载必失败。

### 关键判断：不影响启动，只影响个别功能

逐一核实了触发时机，结论是**这些库都不会在 Spring Boot 启动期加载**，因此 **app 在 arm64 上照常启动、核心命理/占星/术数功能不受影响**：

| 库 | 触发方式 | 是否在启动期 | 实际影响面 |
| --- | --- | --- | --- |
| libimagequant | 仅 `PNGUtility.compressByQuantLib(...)` | 否 | **无调用方**，实为死代码 |
| OpenCV | `ImageUtility` 静态块 `initOpenCV()` | 是，但**已 `catch(Throwable)`** | 类正常加载；用到 OpenCV 的方法（`img2Mat`/`toGray`/`detectText`）**已确认全仓库无调用方 = 死代码**，用户路径碰不到 |
| RXTX 串口 | 打开串口时经 `CommPortIdentifier`→`RXTXVersion`→`RXTXInitializer` | 否（仅 `DoorLockController` API 触发） | IoT 门锁，非产品路径 |

实际用到的 PNG 压缩路径是 `PNGUtility.compressQuick` → `PngOptimization` → **pngtastic（纯 Java）**，本就 arm64 安全。

所以这次加固的目标不是「让这些功能在 arm64 上跑起来」（缺 arm64 原生库，做不到且高风险），而是**把失败从「硬崩 / 难懂的报错」变成「干净降级」**，并消除任何潜在的「类初始化被污染」连带风险。

---

## 2. 改了什么

共 5 处改动，全部位于失败路径。

### 2.1 `image` 模块

**a) `org/pngquant/LiqObject.java`** —— 修了一个真实 bug + 降级
- 原静态块 `catch (Exception)`，但错误架构的库抛的是 `UnsatisfiedLinkError`（属 `Error` 而非 `Exception`），**根本没被捕获**，导致 `.so` 兜底从不执行，且 `throw new RuntimeException` 让整个类带 `ExceptionInInitializerError` 被污染。
- 改为 `catch (Throwable)`（两层都改），失败时**不再抛出**，仅置 `nativeAvailable=false`；新增 `public static boolean isNativeAvailable()`。
- 成功路径不变：能加载时 `nativeAvailable=true`，其余逻辑原样。

**b) `org/pngquant/PngQuant.java`** —— 暴露可用性
- 新增 `public static boolean isNativeAvailable()`，委托给 `LiqObject`（`PngQuant` 是 public，供跨包的 `PNGUtility` 调用）。

**c) `boundless/utility/img/PNGUtility.java`** —— `compressByQuantLib` 优雅降级
- 调 `new PngQuant()` 前先判 `PngQuant.isNativeAvailable()`；并用 `try/catch(Throwable)` 兜底。
- 原生不可用 / 量化失败 / 返回 null 时，**回退为直接写出原图**（仍产出合法 PNG，只是没有调色板压缩），保持方法契约。

**d) `boundless/utility/img/CustomOpenCV.java`** —— 清晰的缺库报错
- `extractNativeBinary` 中 `getResourceAsStream` 在 arm64（无 `osx/ARMv8` dylib）返回 null，原会在 `Files.copy` 处抛 `NullPointerException`。
- 改为返回 null 时抛已有类型 `UnsupportedPlatformException` 并记日志。该异常仍被 `ImageUtility.initOpenCV()` 既有的 `catch(Throwable)` 吞掉——**OpenCV 仍是「可选」，只是日志更可读**。

### 2.2 `iot` 模块

**e) `gnu/io/RXTXInitializer.java`** —— 清晰的缺库报错
- `provideNativeLibraries` 在 arm64（`os.arch=aarch64`，无对应 `.jnilib`）会因 null 流在 `copy` 处抛 NPE，逃逸成 `ExceptionInInitializerError`。
- 改为先 `getResource(RESOURCE_NAME) == null` 检查，缺库时抛干净的 `IOException`（静态块本就会把它包成 `IllegalStateException`），且**不再产生 0 字节残留临时文件**。

---

## 3. 为什么保证「不影响已有功能」

统一原则：**所有改动只在原生库加载失败时生效**。

- 在 x86_64 mac / Linux / Windows 上，这些库照常加载，`nativeAvailable=true`、`getResourceAsStream` 非 null、无异常——**所有成功分支一行没动**。
- 仅在 arm64（库本就加载失败）时，行为从「崩溃 / NPE / 类污染」变为「降级 / 干净异常」。
- 没有改任何业务逻辑、方法签名、依赖版本、构建配置。

---

## 4. 验证

- 用项目目标版本 **Zulu JDK 17** 编译：
  - `image` 模块：`mvn -o clean compile` → exit 0，四个改动类均产出 `.class`
  - `iot` 模块：`mvn -o clean compile` → exit 0，`RXTXInitializer.class` 产出
  - 无 `ERROR` / `BUILD FAILURE`
- **未做运行时验证**：本次改动应纳入下一次「干净 arm64 机器」回归（重点点一遍出图 / 图片 / 二维码 / 验证码相关路径）。Risk 2 的干净机器测试是在本改动**之前**做的，请把这批改动一并复测。

---

## 5. 仍未解决 / 已知限制

- **OpenCV 在 arm64 上仍不可用，但已确认不影响任何用户路径。** 用到 OpenCV 的方法只有 `ImageUtility` 里的 `img2Mat`（1013）、`toGray`（1042）、`detectText`（1053）。全仓库调用方追踪结果：`toGray`、`detectText` **零调用方**，`img2Mat` 仅被 `toGray` 调用 → 三者构成一条**自封闭的死代码链**；唯一引用 `ImageUtility` 的控制器 `ImageTestController` 只调 `getQRCodeWithLogoBase64`（纯 Java 二维码，无 OpenCV）。因此 OpenCV 只在 `ImageUtility` 类初始化时**尝试加载**（已被 `catch(Throwable)` 吞掉），运行期没有任何代码会真正调用 OpenCV 方法。
  - **若将来要真正启用 OpenCV（高风险，需专门排期）**：把 `org.openpnp:opencv` 升到带 `osx/ARMv8` 原生库的版本（4.x），但 OpenCV 3.x→4.x 的 Java API 有破坏性变更，必须回归 `ImageUtility` 全部 OpenCV 用法。在死代码被真正接入业务前，这一项不紧急。
- **libimagequant 实为死代码**（`compressByQuantLib` 无调用方）。若未来要在 arm64 真正启用调色板压缩，需提供 arm64 的 `libimagequant`，或改用纯 Java 方案（如已在用的 pngtastic）。
- **RXTX 串口**在 arm64 不可用（IoT 门锁，非产品路径）。

---

## 6. 以后注意事项（给维护者 / 其他 agent）

1. **新增任何 JNI / 原生依赖前，先确认有 arm64（aarch64 / `osx/ARMv8`）切片。** 自查命令：
   ```bash
   find Horosa-Web/astrostudysrv \( -name '*.jnilib' -o -name '*.dylib' -o -name '*.so' \) \
     -exec sh -c 'printf "%s -> " "$1"; lipo -archs "$1" 2>/dev/null || echo "(not macho)"' _ {} \;
   ```
   只出现 `x86_64` 而无 `arm64` 的，都是 arm64 隐患。

2. **构建 / 安装自检本身只跑 `java -version`，抓不到「启动后才加载」的问题。** `package_runtime_payload.sh` 与离线 `postinstall` 只跑 `java -version` 和 `python -c "import swisseph"`，**从不真正启动 Spring Boot**，所以这类 JNI 架构问题默认不会在发布前暴露。
   - **已补：发布前兜底自检脚本** `Horosa_Desktop_Installer/scripts/verify_runtime_backend_boot.sh`。它用与桌面壳完全一致的方式（`HOROSA_REQUIRE_EMBEDDED_RUNTIME=1` + 内置 python/java）把打好的运行时**真正启动一次**，等待后端健康检查（chart `/` 与 backend `/common/time`）通过，再可选地跑一遍 `verify_kentang_runtime_endpoints.py` 的引擎端点冒烟，最后干净关停。
   - **它是独立、按需运行的**：不会被 `build_desktop_release.sh` / `package_runtime_payload.sh` 自动调用，不改动正常发布流程；默认对 `dist/<runtimeAsset>.tar.gz` 解压到临时目录后启动，绝不触碰已安装的 `/Users/Shared/Horosa` 或正在运行的 app。
   - 用法：`scripts/verify_runtime_backend_boot.sh [运行时.tar.gz | 运行时目录]`（不带参数自动探测 `dist/` 归档 → `build/runtime/runtime-payload`）；选项 `--skip-endpoints` / `--timeout <秒>` / `--keep-logs`；退出码 `0` 通过 / `1` 后端未启动健康 / `2` 端点冒烟失败 / `3` 输入错误。
   - **建议接法（均可选）**：发布前手动跑一次；或在 `verify_public_distribution_readiness.sh` 末尾按需调用。

3. **不要为了 arm64 随手升 OpenCV。** 3.4.2 → 4.x 是破坏性 API 变更，会波及 `ImageUtility` 大量调用，必须专门回归。

4. **原生库的失败一律按「可选 / 降级」处理，不要从静态初始化块抛异常。** 静态块抛错会污染整个类（`ExceptionInInitializerError`），常常把同包的无关功能一起带崩——这正是本次 `LiqObject` 修掉的坑。捕获要用 `Throwable`（覆盖 `UnsatisfiedLinkError` 这类 `Error`）。

5. **本次未触碰**：Tauri 壳、Python 运行时、签名 / 公证链路、依赖版本、任何业务逻辑。

---

## 7. 受影响文件清单

```
Horosa-Web/astrostudysrv/image/src/main/java/org/pngquant/LiqObject.java
Horosa-Web/astrostudysrv/image/src/main/java/org/pngquant/PngQuant.java
Horosa-Web/astrostudysrv/image/src/main/java/boundless/utility/img/PNGUtility.java
Horosa-Web/astrostudysrv/image/src/main/java/boundless/utility/img/CustomOpenCV.java
Horosa-Web/astrostudysrv/iot/src/main/java/gnu/io/RXTXInitializer.java
```
