# Windows 启动稳健化 — 镜像清单(给 Windows Electron 仓库)

> 读者:在 **Windows 仓库**(`Horosa-Web-App-comprehensively-improved-Windows`,Electron 外壳)干活的 Claude Code / 开发者。
> 背景:mac 端(Tauri/Rust)与共享层(`Horosa-Web/`)已做启动稳健化;本清单是 **Windows Electron 壳要镜像的对应改动**,直击用户反馈最多的 **「启动卡住/白屏/进不去主界面」** 与 **「端口被占用/后端起不来」**。
> 基线:Windows HEAD `ea500e22`(v2.5.3)。文件 = `desktop_installer_bundle/electron/service-manager.js` / `main.js`。
> **总原则(与 mac 同):每条都是纯增量 + 安全回退,最坏 = 现状,绝不降级;不弹防火墙、不需用户手动操作。**

> Windows 现状(已做对、**勿重做**):动态端口 `findPort(50)`(`service-manager.js:143`)+ 注端口到前端、签名匹配 reclaim(`Get-NetTCPConnection`+cmdline marker)、`-Dhorosa.runtime.owner`、`waitForBackendHeartbeat`→`/heartbeat`(`:259/266`,非 trusted 路径)、`waitForChartProbe`(`:294`)、`windowsHide:true`(无黑框)、崩溃连带杀兄弟、`taskkill /T /F`、单实例(`main.js:2014 app.requestSingleInstanceLock()`)、系统代理(#9/#14)。

---

## ① 修「白屏/进不去」根因:trusted 快路径仍要发 HTTP `/heartbeat`(最高优先)

**根因**:`service-manager.js:1618` 处,trusted runtime 快路径把后端就绪探测降级为「仅端口探测」:
```js
const backendProbePromise = Promise.resolve({ ... bodyExcerpt: 'trusted runtime port probe' });
const [backendProbe, chartProbe] = await Promise.all([ backendProbePromise, waitForChartProbe(chartPort, readyTimeoutMs) ]);
```
端口 open ≠ Java 真就绪。若上次验证过的 trusted 缓存遇到这次 Java 变慢/半坏,UI 会**先加载 → 白屏/进不去**。

**改法(增量 + 回退)**:trusted 路径也发一次**短超时**的真心跳探测,失败则**降级到完整 `waitForBackendHeartbeat`**(而非直接放行):
```js
const backendProbePromise = (async () => {
  try {
    // 短超时(如 readyTimeoutMs 但更短,例如 Math.min(8000, readyTimeoutMs)),发真 /heartbeat 2XX
    return await waitForBackendHeartbeat(serverRoot, Math.min(8000, readyTimeoutMs));
  } catch (e) {
    // trusted 缓存失效:不直接放行,退回完整就绪等待(与非 trusted 同),绝不先加载 UI
    return await waitForBackendHeartbeat(serverRoot, STARTUP_READY_TIMEOUT_MS);
  }
})();
```
- 对应 mac:`start_horosa_local.sh` 一律轮询 HTTP `/`(Python)+ 签名 `/common/time`(Java),从不「仅端口」。
- 回退:Java 正常时短探测立即通过,trusted 提速不变;只有「缓存说 trusted 但实际没就绪」时多等几秒,**换掉白屏**。
- 不降级:非 trusted 路径(`waitForBackendHeartbeat`)完全不动。

---

## ② 修「端口被占用/孤儿后端」:Windows Job Object 让子进程随父死

**根因**:`service-manager.js:~1388` spawn `python.exe/java.exe` 只设 `windowsHide:true`,**无 Job Object**;注释里也明说「故意不扫杀孤儿,靠 findPort 绕」。Electron 崩溃/被强杀 → 子进程成孤儿、持续占口占内存,日积月累出现「端口被占/后端起不来」。

**改法(增量 + 回退)**:用 Job Object `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`,在 **spawn 子进程之前**把当前 Electron 进程关联到 job,子进程继承该 job → 父进程一旦退出(含崩溃),OS 自动连带终止所有子进程。
- 调用序列(Win32,等价 `win32job-rs` 文档):`CreateJobObjectW` → `SetInformationJobObject(JobObjectExtendedLimitInformation, LimitFlags |= JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)` → `AssignProcessToJobObject(job, GetCurrentProcess())`,在 ServiceManager 初始化(任何 spawn 之前)执行一次。
- Node 落地:`win32-api` / `koffi`(替代不维护的 `ffi-napi`)/ 小型 N-API addon;参考 https://learn.microsoft.com/windows/win32/procthread/job-objects 与 https://github.com/ohadravid/win32job-rs。
- **保留** 现有 `taskkill /T /F`(计划内退出)+ `findPort`(绕占用)+ 崩溃连带杀兄弟,作为双保险。
- 回退:Job Object 创建失败时 `try/catch` 吞掉、退回现状(taskkill/findPort),**绝不因此阻断启动**。
- 对应 mac:`main.rs` 用进程组 `setpgid` + 退出/信号 `killpg`(同义,平台 API 不同)。

---

## ③ 修防火墙弹窗:Java 只绑 127.0.0.1

**根因**:`buildJavaArgs`(`service-manager.js:~1351`)无 `--server.address`,Spring Boot 默认绑 `0.0.0.0` → **Windows 首启防火墙弹窗**(吓退非技术用户 / 可能挡启动)。

**改法(增量)**:`buildJavaArgs` 的 `javaArgs` 加一项:
```js
'--server.address=127.0.0.1',
```
- 安全:Java 只被本机渲染进程经 `127.0.0.1` 访问;Mongo/Redis/AI 是 Java 作客户端外连,不受 `server.address` 影响。
- **不改共享 `application.properties`**(那会波及独立的服务器部署仓库,可能需 `0.0.0.0`);用命令行 arg(Spring 优先级高于 properties),桌面专属、零波及。
- 对应 mac:`start_horosa_local.sh` 同样加 `--server.address=127.0.0.1`。

---

## ④(可选,低优先)stdout 端口握手

- 共享后端已在监听后打印 `HOROSA_READY chart_port=<p>`(Python)。若需更强的「此端口确为本次起的后端」确认,可在 spawn 的 stdout 流里 grep 该行;但 Windows 已用 `findPort` 显式分配 + 注入端口,优先级低。

## ⑤(可选)AppCDS 冷启动提速(配合共享层打包)

- 若 runtime 包内含 `app.jsa`(打包期生成),`buildJavaArgs` 加 `-XX:SharedArchiveFile=<path>/app.jsa -Xshare:auto`(`-Xshare:auto` = 归档失效自动退普通启动,绝不阻断)。显著缩短 JVM 冷启动 → 进一步压缩白屏窗口。
- **关键:bundled JDK = 17 → 勿用 `-XX:+AutoCreateSharedArchive`(那是 JDK 19+,JDK17 上是未知标志会致 JVM 起不来=回归)。** 归档须由打包期 `-XX:ArchiveClassesAtExit=app.jsa`(跑一次 warmup 后优雅退出)生成;详见 `docs/启动稳健化-P1P2-与打包spec.md`。

---

## 验证(Windows 真机)
- **白屏**:制造 trusted 缓存后,人为拖慢 Java(或断 Java)→ 应显示就绪等待 / 可操作错误,**不再先加载到白屏**;Java 起来后正常进主界面。
- **端口/孤儿**:任务管理器强杀 Electron → `python.exe/java.exe` 应随之消失(Job Object 生效),不再残留占口;下次启动直接干净。
- **防火墙**:全新机器首启**无防火墙弹窗**(Java 绑 127.0.0.1)。
- **不降级**:四方位法主限法 v10 / 量化盘 / AI / 排盘 / 更新 全部照常;冷启动时间 ≤ 现状。
