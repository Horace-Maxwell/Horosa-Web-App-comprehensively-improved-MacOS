# AI 分析页全面修复（v2.1.5）

> 首发版本：**v2.1.5 / 2.1.5-runtime1**
> 日期：2026-05-26
> 范围：「AI 分析」整页 —— 供应商切换/鉴权、发送与流式安全、静默失败透出、若干打磨。
> 来源：issue #4 的新评论（owner 已确认要修）暴露了 v2.1.4 未覆盖的真 bug；并按要求**全面审计整个 AI 分析页**（3 个 Explore agent 通审前后端，分级修复高把握项，剔除误报/过度设计）。
> 面向 Windows 同步：**本版后端有改动 → 必须重编 `astrostudyboot.jar`**；前端需重建包。详见第 5 节。

---

## 1. 根因与背景

issue #4 报告者在 v2.1.4 之后追加评论，指出两个 v2.1.4 没修的真 bug，owner 回复确认：
- **Bug A：切换供应商形同虚设 / 「新 URL + 旧 Key」401。**
- **Bug B：OpenAI/自定义预设强制拼 `Authorization: Bearer` → 直连 Gemini 等原生接口报 `ACCESS_TOKEN_TYPE_UNSUPPORTED` / `invalid_token`。**

随后对整页做了系统审计，又发现一批静默失败、并发、超时被忽略等问题，一并修复。`#5`（gpt-5.5）已由 v2.1.4 覆盖，本版不重复。

---

## 2. 修复内容（按组）

### A. 供应商选择 / 配置（前端 `components/aianalysis/AIAnalysisMain.js`）
- **卡片可切换 + 「设为当前」按钮**：「切换供应商」弹窗里的卡片原来只有「编辑」、整块不可点。现在卡片整块 `onClick` + 一个明确「设为当前」按钮，调用新函数 `setProviderAsCurrent(profile)` → 把 `modelSelection` 设为 `encodeModelSelection(profile.id, 首个模型)`（按钮内 `e.stopPropagation()` 避免与卡片点击冲突）。
- **切 provider 类型清空旧 key**：`applyProviderPresetToForm` 原来 `...currentValues` 保留旧 `apiKey`、只换 `baseUrl` → 存出「新 URL + 旧 Key」。现在切换 providerType 时显式 `apiKey: ''`。（注意：打开编辑器用 `setFieldsValue` 不触发 `onValuesChange`，故只在用户主动改类型时清空，不会误清已加载的 key。）
- **删当前供应商自动补选**：`deleteProvider` 删的是当前项时，自动选剩余第一个启用 profile 的首个模型，而非留空。
- **打开已删配置的会话**：`openConversation` 检测 `conversation.providerProfileId` 已不存在时 `message.info` 提示「原配置已删除，已切换…」（既有的 modelOptions effect 会把选择校正到可用项）。
- **所选模型被删**：已有 effect（modelOptions 变化时若所选不在选项内则重置）覆盖，无需新增。

### B. 鉴权 / 请求层
- **后端 `AIAnalysisProxyService.buildAuthHeaders`**：
  - `gemini` 不再加 `Authorization`（它走 URL `?key=`，多加 Bearer 会被原生接口拒）。
  - 默认仍 `Authorization: Bearer`；新增 `providerOptions.authHeaderName` / `authPrefix` 覆盖（`authPrefix:""` 即发原始 key），兼容要求非 Bearer 的官方原生 key。
  - 这两个 key 已加入 `buildProviderBodyOptions` 的**保留键**，避免漏进请求体。
- **前端 `services/aianalysis.js`**：新增 `resolveRequestTimeout(values)`，所有请求/流式从 `values.providerOptions.requestTimeoutMs`（1s~10min，回退 120s）取超时；之前写死 120000 忽略了用户设置。embedding 请求补传 `providerOptions`。

### C. 发送 / 流式 / 会话安全（前端）
- **并发发送守卫**：`handleSend` 开头 `if(sending) return;`；`onPressEnter` 判 `!sending`；发送按钮加 `disabled={sending}`。
- **切换/删除会话中止流**：`openConversation`、`handleDeleteConversation`（删当前时）先 `abortRef.current?.abort()`。
- **丢弃迟到 delta**：`streamReply` 的 `onEvent` delta 分支开头 `if(abortController.signal.aborted) return;`。
- **流式 catch flush**：`requestAIAnalysisChatStream` catch 里 `parser.end()`，网络中断时 flush 缓冲事件。
- **自动滚到底**：新增 `chatLogRef` + `useEffect([visibleMessages]) → el.scrollTop = el.scrollHeight`。

### D. 静默失败透出（前端）
- 向量重排失败：原 `console.warn` 静默 → 增 `message.warning('向量检索失败，本次仅用关键词排序')`。
- 资料分块：按材料 `try/catch`，单个失败 toast「资料『X』分块失败，本次检索已跳过」，不再因一个材料毁掉整次检索。
- Markdown：`renderMarkdownToHtml` 解析异常时退回 `DOMPurify.sanitize(raw)`（纯文本）而非空串。

### E. 存储健壮性（前端 `utils/aiAnalysisStore.js`）
- `saveUiPrefs` 配额超限不再静默吞，`console.warn` 记录（UI 提示交调用方，util 不直接弹）。

### F. 打磨
- 后端 `isOpenAIReasoningModel` 前缀加 `o5`（防新模型回归）。

---

## 3. 明确「不做」（误报 / 过度设计 / 需更大决策）
- **ollama `/models`**：OpenAI-compat 模式 `/v1/models` 可用，非 bug。
- **IndexedDB 乐观锁 / 内存态定期回写**：本地单用户过度设计，未引入。
- **导出含上下文层（技法快照）**：属功能增强而非 bug，本轮不做。
- **`isSnapshotMetaCompatible`**：经只读核实，date/time/zone/lon/lat 不一致时确为 `return false`（reject），「绝不挂错盘」不变量完好，**未改动**。

---

## 4. 测试
- 后端 JUnit `AIAnalysisProxyServiceTest`：新增 `buildAuthHeadersOmitsBearerForGeminiAndSupportsOverride`（gemini 无 `Authorization`、custom 覆盖头、默认 Bearer、ollama 无 auth）。共 16 项全过。
- 前端 Jest 既有用例全过；`npm run build` + `build:file` 通过（webpack 编译含全部改动）。
- `release_preflight.sh` 全绿。

---

## 5. Windows 同步注意事项（关键）

1. **后端改了 `AIAnalysisProxyService.java` → 必须重编 `astrostudyboot.jar`**。仓库无 root reactor pom，模块版本固定。JDK 17：
   ```bash
   cd Horosa-Web/astrostudysrv
   mvn -f astrostudy/pom.xml install -DskipTests       # boundless 本版未改,已在 .m2
   mvn -f astrostudyboot/pom.xml clean package -DskipTests   # clean 必须,否则增量复用旧 fat jar
   ```
   产物 `astrostudyboot/target/astrostudyboot.jar` 放到 Windows 运行时打包位置（mac 对应 `runtime/mac/bundle/`）。自检：解包 fat jar 内 `astrostudy-1.0.0.jar` 的 `AIAnalysisProxyService.class` 应含 `authHeaderName`。
2. **前端是共享的**：同步 `astrostudyui/{components/aianalysis/AIAnalysisMain.js, services/aianalysis.js, utils/aiAnalysisStore.js}` 后 `npm run build && npm run build:file`（顺序）。
3. 纯 Java/JS，无平台分支；外壳/运行时各自维护。
4. 验证：多供应商切换（卡片/「设为当前」）生效、切类型不串 key、Gemini 直连不再 401、流式中回车不并发、停止/切换会话中止流、嵌入缺失有提示。

---

## 6. 受影响文件清单

```
Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java   (B 鉴权 + body 保留键 + reasoning o5)
Horosa-Web/astrostudysrv/astrostudy/src/test/java/spacex/astrostudy/service/AIAnalysisProxyServiceTest.java (新增 auth 用例)
Horosa-Web/astrostudyui/src/components/aianalysis/AIAnalysisMain.js   (A 供应商选择 + C 发送/流式 + D 透出 + F)
Horosa-Web/astrostudyui/src/services/aianalysis.js                    (B 超时透传 + 流式 flush)
Horosa-Web/astrostudyui/src/utils/aiAnalysisStore.js                  (E 配额提示)
Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar     (重建 fat jar)
+ 版本 lockstep / config/release_notes/2.1.5.md / README×3 / UPGRADE_LOG / windows-sync-handoff / skill
```

> 逐版本「Windows 要做什么」的精简台账见 [`windows-sync-handoff.md`](windows-sync-handoff.md)；本文是 v2.1.5 的完整技术细节。
