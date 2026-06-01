# Issue #10「服务不稳定」修复:SSE 并发竞态 + SSE 标志跨请求污染（v2.3.1）

> Windows repo issue #10(@zhmmartin)。从 v2.1.2 升级到 v2.3.0 后出现。代码全部在**共享后端** `Horosa-Web/astrostudysrv`,Windows 同步。

## 现象（含用户截图/日志）
- AI 分析(deepseek-reasoner)**几句话之后就停止**(截断)。
- AI 有时**直接回 `signature.error`**;同样输入一分钟后又**成功** → **间歇性**。
- 排盘弹「**排盘失败:本地排盘服务未就绪。请确认 Horosa 本地服务仍在运行后重试。**」。
- 「**访问 http://127.0.0.1:9999/predict/pd 错误。statusCode: 200**」(HTTP 200 却被判错)。
- Java 日志:`RuntimeException: IllegalStateException: ResponseBodyEmitter has already completed`(`AIAnalysisProxyService.sendEvent:995`)+ `IOException: Stream closed` + `boundless.SignatureException: signature.error`(`RequestHeaderInterceptor.checkSignature`,处于 `AsyncContextImpl.asyncDispatch` 路径)。

## 根因:两个独立的共享后端 bug

### (A) SSE emitter 并发写竞态 → AI 截断
v2.2.1 为 #8 加的 keep-alive 心跳(`SSE_HEARTBEAT_EXECUTOR`,每 15s)与读流线程**并发写同一个非线程安全的 `SseEmitter`**:
- 心跳线程:`emitter.send(comment("keep-alive"))`,失败时**自行 `emitter.complete()`**。
- 读流线程:`sendEvent → emitter.send(delta)`。

`SseEmitter.send()/complete()` 非线程安全。长流上两者交错、或心跳 `complete()` 抢在读流 `send` 之前 → 读流下次 `send` 撞 `ResponseBodyEmitter has already completed` → 包成 RuntimeException → 断流 =「几句话之后停止」。

### (B) SSE 标志跨请求污染 + async 重复验签 → signature.error 打挂排盘/AI/predict
- SSE 标志 `__sse__` 由 `TransData.setSSE(true)` 写,而 `setReqeustAttribute` 实为 **`request.setAttribute("__sse__", true)` —— 绑在 `HttpServletRequest` 对象上**(不是 ThreadLocal)。
- `AIAnalysisController.chatStream` 在 Tomcat 工作线程 `SseHelper.push()→setSSE(true)`,再用裸 `new Thread`+`Thread.sleep(50)`「等 async 进入」的 hack 异步跑流,请求随即转 async。
- **Tomcat 会池化复用 `HttpServletRequest` 对象**。SSE 请求的 `__sse__=true` 在 async/复用时序下残留到被复用的 request 对象;`pureClearTransData()` 只 `.clear()` 五个 ThreadLocal map,**根本不碰 request attribute**,清不掉。
- 下一个落到该 request 对象的请求(排盘 `/predict/pd`、普通 AI)在 `RequestHeaderInterceptor.complete():595` 和 `afterCompletion:744` 被 `isSSE()` 误判为 SSE —— 且该判定**排在可靠的「handler 返回类型是否 `SseEmitter`」(`afterCompletion:755`)之前** —— 响应被设为 `text/event-stream` 直接返回、跳过正常 JSON → 前端解析/验签失败 → `signature.error` /「本地服务未就绪」/ `predict 200 报错`。命中与否取决于线程/对象池复用 → **间歇性**(失败、一分钟后又成功)。
- 另:SSE 完成后 Tomcat **ASYNC re-dispatch** 再次进 `preHandle→checkSignature`,但 body 已被首次 `getInputStream()` 消费 → 用空 body 重算签名必然 `signature.error`(日志中 `AsyncContextImpl.asyncDispatch→checkSignature` 路径)。

> 注:前后端签名算法本身一致(前端 `request.js:sign` = `token+SignatureKey+(channel+app+ver)+body` 的 SHA256,后端 `checkSignature:316` 同式),正常请求不该签名错——签名错全部是上面 (B) 的污染/重复验签所致,**不是签名算法 bug**。

## 修复（纯 Java:`astrostudy` + `boundless`;**必须重编 `astrostudyboot.jar`** — gotcha #10）

### (A) `SseChannel` 线程安全收口 — `AIAnalysisProxyService.java`
新增 `SseChannel`:单锁串行化 `send/complete/completeWithError`;`closed` 守卫使 `complete` 幂等、关闭后 `send` 返回 `false` 不抛。`chatStream` 建一个 `SseChannel` 贯穿心跳 + 3 个 `stream*` 方法 + `sendEvent`;**心跳不再自行 `complete`**(收尾统一在 `chatStream`)。保留 #8 的 `QueueLog.error` 一级异常日志 + `keep-alive` 帧。

### (B) `RequestHeaderInterceptor.preHandle` — `boundless`
- 非 `REQUEST` dispatcher(ASYNC/ERROR/FORWARD re-dispatch)在 `setRequestObject` 后**早返回**,跳过 body 解码 + `checkSignature`(body 已消费,重验必失败)→ 消除 async re-dispatch `signature.error`;request 绑定仍保留供 `afterCompletion` 收尾(SSE 的 `__sse__` 绑在同一 request,仍能正确读到)。
- `REQUEST` dispatch 进来先 **`TransData.setSSE(false)` 归零** → 即便 request 对象被复用且残留 `__sse__=true`,本请求也从 `false` 开始 → 堵死跨请求污染(真正 SSE 端点之后会自行 `SseHelper.push→setSSE(true)`)。

> 未改动 `boundless` 的签名算法、async 线程模型、controller 的 worker-thread,以把回归面压到最小;`Thread.sleep(50)` hack 暂留(去掉它属另一项独立改动,本次不并入以免扩面）。

## 验证
- 重编 `astrostudyboot.jar`(JDK17:`boundless install → astrostudy install → astrostudyboot clean package`),确认 jar 内 `astrostudy-1.0.0.jar`/`boundless-*.jar` 含新 class。
- 起本地 stack,**功能零降级三套**:`verify_kentang_runtime_endpoints.py`(17 引擎 200)、`verifyHorosaRuntimeFull.js`(exit 0)、`verifyPrimaryDirectionRuntime.js`(exit 0)。
- 排盘 `/predict/pd` 反复请求 + 与 AI 流交错并发,确认不再出现 `signature.error` / event-stream 误判。
- (有真实 provider key 时)AI 长流完整不截断。

## 平台 / 版本
共享后端,Windows 同步同两文件(`AIAnalysisProxyService.java`、`RequestHeaderInterceptor.java`)+ 重编 jar。版本 **2.3.1**(app+runtime 一起 bump:已自动更新到 2.3.0 的用户,只有版本号变化才会再收到推送)。
