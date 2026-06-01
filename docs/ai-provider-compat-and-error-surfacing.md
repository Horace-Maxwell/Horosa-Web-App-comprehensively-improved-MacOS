# AI 分析：供应商兼容 + 错误透传 + 凭据脱敏

> 首发版本：**v2.1.4 / 2.1.4-runtime1**
> 日期：2026-05-26
> 范围：「AI 分析」聊天链路（前端 React + 后端 Java 代理 + 共享 HTTP 库）。
> 来源：发布 v2.1.3 时排查仓库 issue #4 / #5，全面修复同类问题。
> 面向 Windows 端同步：本次**主修复在后端 Java**，与 v2.1.3（前端为主）不同——**必须重编 `astrostudyboot.jar`**，详见第 5 节。

---

## 1. 根因（三个家族）

**A. 参数不兼容（issue #5 根因）**
`AIAnalysisProxyService.buildOpenAIChatBody` 对所有 OpenAI 兼容模型**无条件发送 `temperature:0.7`**，并把 token 上限发为 `max_tokens`。但 OpenAI 的推理系列（`gpt-5.x` / `o1` / `o3` / `o4`）**只接受默认 `temperature`(=1)**，且要求用 **`max_completion_tokens`** 取代 `max_tokens`，否则上游返回 400。`gpt-4.1` 接受 0.7，所以「4.1 行、5.5 不行」。

**B. 错误被吞（issue #5 表象「模型未返回可用内容」）**
- 后端流式 `ensureSuccess` 只取状态码、**丢弃上游响应体**（真正的原因如「temperature 只支持默认值」全没了）。
- 前端流式 `onEvent` **只处理 `delta` 事件，忽略后端发来的 `error` 事件** → 流「正常结束」但零内容 → 落到兜底文案「模型未返回可用内容」。

**C. 凭据泄露（issue #4）**
共享库 `HttpUriRequestHystrixCommand.doCmd` 在上游非 2xx 时，把**完整请求头**（含 `Authorization: Bearer <key>`、`x-api-key`、`LocalIp`）拼进错误信息并经 `DefaultExceptionHandler` 回给客户端。issue #4 里泄露的正是用户填进 OpenAI 兼容模式的 Gemini key。

> 配置持久（issue #4 次症「每次配置完得重新配置」）经审计**不是 bug**：apiKey 已存 IndexedDB（`aiAnalysisStore.js`）并在重开编辑框时回填（`AIAnalysisMain.js` `buildProviderFormValues`），只是 `type=password` 视觉为空。未改代码。

---

## 2. 修复内容

### 2.1 后端参数适配（A）
`AIAnalysisProxyService.java`：
- 新增 `static boolean isOpenAIReasoningModel(String model)`：小写、去掉 `provider/` 前缀（兼容 openrouter 的 `openai/gpt-5`），命中 `gpt-5` / `gpt-6` / `o1` / `o3` / `o4` 前缀。
- `buildOpenAIChatBody`（流式与非流式共用）：reasoning 时**省略 `temperature`**、token 上限发 **`max_completion_tokens`**；非 reasoning 维持 `temperature:0.7` + `max_tokens`，**既有模型零改动**。

### 2.2 后端错误透传（B）
`AIAnalysisProxyService.ensureSuccess`：非 2xx 时读取 `response.body()`（流式 `InputStream`，仅错误分支消费），截断（≤1KB）并入异常信息 → 上游真因进入 `error` SSE 事件。新增 `readErrorBody(Object)`。

### 2.3 前端错误透传（B）
`AIAnalysisMain.js` 流式块：`onEvent` 新增 `error` 分支，捕获 `event.json.message` 存入 `streamError`；流结束后若无内容则显示 `⚠️ <真实错误>`、状态置 `error`；catch 块也优先用 `streamError || e.message`。覆盖「干净结束」与「抛错」两条终止路径。

### 2.4 凭据脱敏（C）
`HttpUriRequestHystrixCommand.java`：
- 新增 `redactSensitiveHeaders(Map)`：把 `authorization` / `x-api-key` / `api-key` / `apikey` / `x-goog-api-key` / `cookie` / `set-cookie` / `proxy-authorization` / `localip`（不分大小写）的值替换为 `***redacted***`，保留其余头与**响应体**（有用部分）。错误信息里改用脱敏副本。
- 新增 `stripQuery(String)`：错误日志的 URL 去掉 `?...`，防止 Gemini 的 `?key=` 进日志。
- **影响面**：仅改错误字符串/日志，不动任何请求/响应处理逻辑；对全 app 出站请求都是纯安全增强。

---

## 3. reasoning 检测与参数对照

| 模型示例 | 是否 reasoning | temperature | token 上限字段 |
| --- | --- | --- | --- |
| `gpt-5.5`, `gpt-5.5-2026-04-23`, `o1`, `o3-mini`, `o4-mini`, `openai/gpt-5` | 是 | 省略 | `max_completion_tokens`（仅当用户设了 maxTokens） |
| `gpt-4.1`, `gpt-4o`, `deepseek-chat`, `deepseek-reasoner`, 其它 | 否 | `0.7` | `max_tokens`（仅当设了 maxTokens） |

注：检测只看模型名，因此非 OpenAI 的 openai-compatible 供应商（deepseek 等）天然不受影响。

---

## 4. 验证

- **后端 JUnit**：`AIAnalysisProxyServiceTest`（reasoning 命中/不命中、body 构造 14 项）+ `HttpUriRequestHystrixCommandTest`（脱敏 + 去查询串 2 项）全绿。
- **编译**：`astrostudy` + `boundless`（JDK 17）通过；`astrostudyboot.jar` 重建并确认 fat jar 内含 `max_completion_tokens`、`redacted`。
- **前端**：Jest 全绿；`npm run build` + `build:file` 通过。
- **应用内预览**：错误透传（必 400 请求 → 显示上游真因）、凭据脱敏（错 key 401 → 错误里显示 `***redacted***`）、配置持久复核。

---

## 5. Windows 端注意事项（关键，与 v2.1.3 不同）

1. **本次主修复在后端 Java**，不是纯前端。Windows 同步**必须重编 `astrostudyboot.jar`**，否则改动不生效。
2. 仓库**没有 root reactor pom**，模块各自独立、版本固定（boundless `1.2.1.2`、astrostudy/astrostudyboot `1.0.0`）。重编顺序（JDK 17）：
   ```bash
   cd Horosa-Web/astrostudysrv
   mvn -f boundless/pom.xml  install -DskipTests      # 先把改过的 boundless 装进本地 .m2
   mvn -f astrostudy/pom.xml install -DskipTests      # 再装改过的 astrostudy（依赖 boundless）
   mvn -f astrostudyboot/pom.xml clean package -DskipTests   # 重打 fat jar（必须 clean，否则增量跳过不重打）
   ```
   产物 `astrostudyboot/target/astrostudyboot.jar` 会被发布链路（`package_runtime_payload.sh`，优先 target 后回退 `runtime/.../bundle`）与本地启动（`start_horosa_local.sh`）采用。
   - **坑**：不 `clean` 直接 `package` 时，因 astrostudyboot 自身源码未变，maven 会增量复用旧 fat jar（不会重新打包依赖）→ 改动不进 jar。**务必 `clean`**。
3. **前端**是共享的：`AIAnalysisMain.js` 改动随 `astrostudyui` 打包生效。
4. **凭据脱敏在共享库 `boundless`**：任何重编都会带上；纯 Java、无平台依赖。
5. 仅处理「AI 分析」链路；其它技法不受影响。

---

## 6. 受影响文件清单

```
Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java   (A 参数适配 + B 后端错误透传)
Horosa-Web/astrostudysrv/boundless/src/main/java/boundless/net/http/HttpUriRequestHystrixCommand.java       (C 凭据脱敏 + 日志去查询串)
Horosa-Web/astrostudyui/src/components/aianalysis/AIAnalysisMain.js                                          (B 前端错误透传)
Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIAnalysisProxyServiceTest.java  (新增测试)
Horosa-Web/astrostudysrv/boundless/src/test/java/boundless/net/http/HttpUriRequestHystrixCommandTest.java    (新增测试)
Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar                                            (重建 fat jar)
```
