package spacex.astrostudy.service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.ProxySelector;
import java.net.Socket;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import boundless.exception.ErrorCodeException;
import boundless.log.AppLoggers;
import boundless.log.QueueLog;
import boundless.net.http.HttpClientUtility;
import boundless.spring.help.interceptor.SseHelper;
import boundless.utility.JsonUtility;
import boundless.utility.StringUtility;

@Service
public class AIAnalysisProxyService {

	private static final String DEFAULT_OPENAI_BASE = "https://api.openai.com/v1";
	private static final String DEFAULT_DEEPSEEK_BASE = "https://api.deepseek.com";
	private static final String DEFAULT_OPENROUTER_BASE = "https://openrouter.ai/api/v1";
	private static final String DEFAULT_OLLAMA_BASE = "http://127.0.0.1:11434/v1";
	private static final String DEFAULT_ANTHROPIC_BASE = "https://api.anthropic.com";
	private static final String DEFAULT_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta";
	private static final String DEFAULT_MOONSHOT_BASE = "https://api.moonshot.cn/v1";
	private static final String DEFAULT_ZHIPU_BASE = "https://open.bigmodel.cn/api/paas/v4";
	private static final String DEFAULT_SILICONFLOW_BASE = "https://api.siliconflow.cn/v1";
	private static final String DEFAULT_GROQ_BASE = "https://api.groq.com/openai/v1";
	private static final String DEFAULT_XAI_BASE = "https://api.x.ai/v1";
	private static final Duration DEFAULT_TIMEOUT = Duration.ofSeconds(120);

	// #9:流式 AI 请求经系统代理(配合启动器 -Djava.net.useSystemProxies=true)。
	// JDK HttpClient 不调用 .proxy() 时默认完全不走代理;此处显式取 ProxySelector.getDefault(),
	// 无系统代理时返回 DIRECT、localhost 自动 bypass,行为不变。
	private final HttpClient streamHttpClient = HttpClient.newBuilder()
		.connectTimeout(Duration.ofSeconds(15))
		.proxy(ProxySelector.getDefault())
		.followRedirects(HttpClient.Redirect.NORMAL)
		.build();

	// Issue #8 Fix 2: 长时 SSE 流的心跳调度池。Ollama 慢首 token 时若全程零字节，
	// 客户端/中间件会按空闲超时切断 socket → 后端首次 sendEvent 撞 ClientAbortException。
	// 每 15s 给 emitter 写一个 ": keep-alive" 注释帧，防止空闲断连。15s 安全门槛
	// 低于浏览器/中间件常见空闲阈值（30–60s）。
	private static final long SSE_HEARTBEAT_SECONDS = 15L;
	private static final ScheduledExecutorService SSE_HEARTBEAT_EXECUTOR = Executors.newScheduledThreadPool(2, r -> {
		Thread t = new Thread(r, "ai-analysis-sse-heartbeat");
		t.setDaemon(true);
		return t;
	});

	@FunctionalInterface
	private interface StreamBody {
		void run() throws Exception;
	}

	/**
	 * 修复 #10(A):SseEmitter.send()/complete() 非线程安全。心跳线程(每 15s)与读流线程并发写
	 * 同一 emitter、且心跳失败时自行 complete,会与读流的 send 撞 "ResponseBodyEmitter has already
	 * completed"(见 sendEvent)→ 断流(deepseek-reasoner 长流「几句话之后就停止」)。SseChannel 用
	 * 单锁串行化所有写;complete/completeWithError 幂等;一旦关闭,后续 send 返回 false(不抛、也不再
	 * complete),心跳与读流再不会互相踩。
	 */
	private static final class SseChannel {
		private final SseEmitter emitter;
		private final Object lock = new Object();
		private boolean closed = false;

		SseChannel(SseEmitter emitter) {
			this.emitter = emitter;
		}

		/** 线程安全发送;已关闭返回 false(不抛)。底层发送失败(客户端已断)则标记关闭并上抛,供上层进 catch 记日志。 */
		boolean send(SseEmitter.SseEventBuilder event) throws IOException {
			synchronized (lock) {
				if (closed) {
					return false;
				}
				try {
					emitter.send(event);
					return true;
				} catch (IOException | RuntimeException e) {
					closed = true;
					throw e;
				}
			}
		}

		/** 幂等完成:只会真正 complete 一次,重复调用静默返回。 */
		void complete() {
			synchronized (lock) {
				if (closed) {
					return;
				}
				closed = true;
				try {
					emitter.complete();
				} catch (Exception ignore) {
					// 已完成或客户端已断
				}
			}
		}

		/** 幂等错误完成。 */
		void completeWithError(Throwable e) {
			synchronized (lock) {
				if (closed) {
					return;
				}
				closed = true;
				try {
					emitter.completeWithError(e);
				} catch (Exception ignore) {
					// 已完成或客户端已断
				}
			}
		}
	}

	private void withHeartbeat(SseChannel channel, StreamBody body) throws Exception {
		final AtomicBoolean stopped = new AtomicBoolean(false);
		ScheduledFuture<?> heartbeat = SSE_HEARTBEAT_EXECUTOR.scheduleAtFixedRate(() -> {
			if (stopped.get()) {
				return;
			}
			try {
				SseHelper.markCurrentThread();
				// 修复 #10(A):经 SseChannel 串行化写;已关闭则返回 false。心跳不再自行 complete,
				// 收尾统一交给 chatStream 主流程,避免心跳 complete 与读流 send 竞态(keep-alive 帧本身不变)。
				if (!channel.send(SseEmitter.event().comment("keep-alive"))) {
					stopped.set(true);
				}
			} catch (Exception e) {
				// 客户端已断。停止后续心跳;读流下次 send 也会返回 false/抛异常 → 进 catch → 记日志。
				stopped.set(true);
			}
		}, SSE_HEARTBEAT_SECONDS, SSE_HEARTBEAT_SECONDS, TimeUnit.SECONDS);

		try {
			body.run();
		} finally {
			stopped.set(true);
			heartbeat.cancel(false);
		}
	}

	public Map<String, Object> listModels(Map<String, Object> params){
		String providerType = normalizedProviderType(params);
		String responseText = "";
		if(isOpenAICompatible(providerType)) {
			String url = joinUrl(resolveBaseUrl(providerType, stringVal(params, "baseUrl")), "/models");
			Map<String, String> headers = buildAuthHeaders(providerType, stringVal(params, "apiKey"), params);
			responseText = HttpClientUtility.getString(url, null, headers);
		}else if("anthropic".equals(providerType)) {
			String url = joinUrl(resolveBaseUrl(providerType, stringVal(params, "baseUrl")), "/v1/models");
			Map<String, String> headers = buildAuthHeaders(providerType, stringVal(params, "apiKey"), params);
			responseText = HttpClientUtility.getString(url, null, headers);
		}else if("gemini".equals(providerType)) {
			String apiKey = stringVal(params, "apiKey");
			String url = joinUrl(resolveBaseUrl(providerType, stringVal(params, "baseUrl")), "/models");
			Map<String, String> query = new HashMap<String, String>();
			query.put("key", apiKey);
			responseText = HttpClientUtility.getString(url, query, null);
		}else {
			throw new ErrorCodeException(580002, "暂不支持该 providerType");
		}
		Map<String, Object> payload = JsonUtility.toDictionary(responseText);
		Map<String, Object> modelGroups = splitProviderModels(extractModelIds(payload), providerType);
		Map<String, Object> result = new LinkedHashMap<String, Object>();
		result.put("models", modelGroups.get("models"));
		result.put("chatModels", modelGroups.get("chatModels"));
		result.put("embeddingModels", modelGroups.get("embeddingModels"));
		result.put("providerType", providerType);
		result.put("protocolFamily", protocolFamily(providerType));
		return result;
	}

	public Map<String, Object> chat(Map<String, Object> params){
		String providerType = normalizedProviderType(params);
		String model = requireModel(params);
		if(isEmbeddingModel(model, providerType)){
			throw new ErrorCodeException(580014, "所选模型是 Embedding 模型，不能用于对话，请选择聊天模型");
		}
		List<Map<String, Object>> messages = getMessageList(params.get("messages"));
		String responseText = "";
		Map<String, String> headers = buildAuthHeaders(providerType, stringVal(params, "apiKey"), params);
		if(isOpenAICompatible(providerType)) {
			Map<String, Object> requestBody = buildOpenAIChatBody(model, params, messages, false);
			String url = joinUrl(resolveBaseUrl(providerType, stringVal(params, "baseUrl")), "/chat/completions");
			responseText = HttpClientUtility.uploadString(url, headers, "application/json; charset=UTF-8", JsonUtility.encode(requestBody));
		}else if("anthropic".equals(providerType)) {
			String url = joinUrl(resolveBaseUrl(providerType, stringVal(params, "baseUrl")), "/v1/messages");
			Map<String, Object> body = buildAnthropicBody(model, params, messages, false);
			responseText = HttpClientUtility.uploadString(url, headers, "application/json; charset=UTF-8", JsonUtility.encode(body));
		}else if("gemini".equals(providerType)) {
			String apiKey = stringVal(params, "apiKey");
			String url = joinUrl(resolveBaseUrl(providerType, stringVal(params, "baseUrl")), String.format("/models/%s:generateContent?key=%s", urlEncode(model), urlEncode(apiKey)));
			Map<String, Object> body = buildGeminiBody(params, messages);
			responseText = HttpClientUtility.uploadString(url, headers, "application/json; charset=UTF-8", JsonUtility.encode(body));
		}else {
			throw new ErrorCodeException(580013, "暂不支持该 providerType");
		}
		Map<String, Object> payload = JsonUtility.toDictionary(responseText);
		Map<String, Object> result = new LinkedHashMap<String, Object>();
		result.put("content", extractChatContent(providerType, payload));
		result.put("model", model);
		result.put("providerType", providerType);
		return result;
	}

	public void chatStream(Map<String, Object> params, SseEmitter emitter){
		// 修复 #10(A):所有写经线程安全的 SseChannel,心跳与读流不再 race(详见 SseChannel)。
		SseChannel channel = new SseChannel(emitter);
		String providerType = normalizedProviderType(params);
		String model = requireModel(params);
		if(isEmbeddingModel(model, providerType)){
			throw new ErrorCodeException(580014, "所选模型是 Embedding 模型，不能用于对话，请选择聊天模型");
		}
		List<Map<String, Object>> messages = getMessageList(params.get("messages"));
		try{
			if(isOpenAICompatible(providerType)) {
				streamOpenAICompatible(params, model, messages, channel);
			}else if("anthropic".equals(providerType)) {
				streamAnthropic(params, model, messages, channel);
			}else if("gemini".equals(providerType)) {
				streamGemini(params, model, messages, channel);
			}else {
				throw new ErrorCodeException(580013, "暂不支持该 providerType");
			}
			sendEvent(channel, "done", buildMap("providerType", providerType, "model", model));
			channel.complete();   // 幂等:SseChannel 保证只 complete 一次,客户端已断也不抛
		}catch(Exception e){
			// Issue #8 Fix 1: catch 第一件事必须是把"一级"异常写日志。
			// 之前这一步缺失，导致 ClientAbort 二级异常掩盖了 Ollama 上游真实失败，
			// 调试时只能看到 sendEvent 抛 RuntimeException 的镜像 stack，根因黑盒。
			try {
				QueueLog.error(AppLoggers.ErrorLogger, e, String.format(
					"AIAnalysisProxyService.chatStream failed: providerType=%s, model=%s",
					providerType, model));
			}catch(Throwable logEx){
				// 日志层异常永远不能让 catch 自己炸。
			}
			// sendEvent 给前端发"error"事件——若客户端已断,SseChannel.send 返回 false 不抛;根因已记。
			try {
				sendEvent(channel, "error", buildMap(
					"providerType", providerType,
					"model", model,
					"message", safeErrorMessage(e)
				));
			}catch(Exception sendEx){
				// 客户端已断；放弃前端通知。
			}
			// 幂等错误完成(SseChannel 保证只 complete 一次,并清理 SseEmitter 状态)。
			channel.completeWithError(e);
		}
	}

	public Map<String, Object> diagnose(Map<String, Object> params){
		String providerType = normalizedProviderType(params);
		String baseUrl = resolveBaseUrl(providerType, stringVal(params, "baseUrl"));
		Map<String, Object> result = new LinkedHashMap<String, Object>();
		result.put("providerType", providerType);
		result.put("protocolFamily", protocolFamily(providerType));
		result.put("baseUrl", baseUrl);
		result.put("healthy", false);
		result.put("failureReason", "");
		result.put("errorDetail", "");
		result.put("recommendation", "");
		try{
			URI uri = URI.create(baseUrl);
			String host = uri.getHost();
			int port = uri.getPort();
			if(port <= 0){
				port = "https".equalsIgnoreCase(uri.getScheme()) ? 443 : 80;
			}
			result.put("dns", diagnoseDns(host));
			result.put("tcp", diagnoseTcp(host, port));
			Instant httpStart = Instant.now();
			Map<String, Object> models = listModels(params);
			long httpMs = Duration.between(httpStart, Instant.now()).toMillis();
			result.put("http", buildMap(
				"ok", true,
				"latencyMs", httpMs
			));
			result.put("models", models.get("models"));
			result.put("chatModels", models.get("chatModels"));
			result.put("embeddingModels", models.get("embeddingModels"));
			result.put("latencyMs", httpMs);
			result.put("healthy", true);
			result.put("recommendation", "连接正常，可直接用于模型拉取与分析对话。");
		}catch(Exception e){
			String failureReason = classifyFailure(e);
			result.put("http", buildMap(
				"ok", false,
				"message", safeErrorMessage(e)
			));
			result.put("failureReason", failureReason);
			result.put("errorDetail", safeErrorMessage(e));
			result.put("recommendation", buildFailureRecommendation(providerType, failureReason));
		}
		return result;
	}

	public Map<String, Object> embeddings(Map<String, Object> params){
		String providerType = normalizedProviderType(params);
		String model = requireEmbeddingModel(params);
		List<String> inputs = getStringList(params.get("input"));
		if(inputs.isEmpty()){
			throw new ErrorCodeException(580031, "缺少 embedding 输入");
		}
		Map<String, Object> result = new LinkedHashMap<String, Object>();
		result.put("providerType", providerType);
		result.put("model", model);
		if(isOpenAICompatible(providerType)) {
			Map<String, Object> body = new LinkedHashMap<String, Object>();
			body.put("model", model);
			body.put("input", inputs);
			String url = joinUrl(resolveBaseUrl(providerType, stringVal(params, "baseUrl")), "/embeddings");
			String rsp = HttpClientUtility.uploadString(
				url,
				buildAuthHeaders(providerType, stringVal(params, "apiKey"), params),
				"application/json; charset=UTF-8",
				JsonUtility.encode(body)
			);
			Map<String, Object> payload = JsonUtility.toDictionary(rsp);
			result.put("vectors", extractEmbeddingVectors(payload));
			return result;
		}
		if("gemini".equals(providerType)) {
			List<List<Double>> vectors = new ArrayList<List<Double>>();
			String baseUrl = resolveBaseUrl(providerType, stringVal(params, "baseUrl"));
			String apiKey = stringVal(params, "apiKey");
			for(String input : inputs) {
				String url = joinUrl(baseUrl, String.format("/models/%s:embedContent?key=%s", urlEncode(model), urlEncode(apiKey)));
				Map<String, Object> body = new LinkedHashMap<String, Object>();
				body.put("content", buildMap("parts", Arrays.asList(buildTextPart(input))));
				String rsp = HttpClientUtility.uploadString(
					url,
					buildAuthHeaders(providerType, apiKey, params),
					"application/json; charset=UTF-8",
					JsonUtility.encode(body)
				);
				Map<String, Object> payload = JsonUtility.toDictionary(rsp);
				vectors.add(extractGeminiEmbedding(payload));
			}
			result.put("vectors", vectors);
			return result;
		}
		throw new ErrorCodeException(580032, "当前 provider 暂不支持 embedding");
	}

	private void streamOpenAICompatible(Map<String, Object> params, String model, List<Map<String, Object>> messages, SseChannel channel) throws Exception{
		withHeartbeat(channel, () -> {
			Map<String, Object> body = buildOpenAIChatBody(model, params, messages, true);
			String url = joinUrl(resolveBaseUrl(normalizedProviderType(params), stringVal(params, "baseUrl")), "/chat/completions");
			HttpRequest request = buildJsonRequest(url, buildAuthHeaders(normalizedProviderType(params), stringVal(params, "apiKey"), params), JsonUtility.encode(body), params);
			HttpResponse<InputStream> response = streamHttpClient.send(request, HttpResponse.BodyHandlers.ofInputStream());
			ensureSuccess(response);
			readSseStream(response.body(), (eventName, dataText)->{
				if(StringUtility.isNullOrEmpty(dataText)){
					return;
				}
				if("[DONE]".equalsIgnoreCase(dataText.trim())) {
					return;
				}
				Map<String, Object> payload = JsonUtility.toDictionary(dataText);
				String delta = extractOpenAIStreamDelta(payload);
				if(!StringUtility.isNullOrEmpty(delta)) {
					sendEvent(channel, "delta", buildMap("delta", delta));
				}
			});
		});
	}

	private void streamAnthropic(Map<String, Object> params, String model, List<Map<String, Object>> messages, SseChannel channel) throws Exception{
		withHeartbeat(channel, () -> {
			Map<String, Object> body = buildAnthropicBody(model, params, messages, true);
			String url = joinUrl(resolveBaseUrl("anthropic", stringVal(params, "baseUrl")), "/v1/messages");
			HttpRequest request = buildJsonRequest(url, buildAuthHeaders("anthropic", stringVal(params, "apiKey"), params), JsonUtility.encode(body), params);
			HttpResponse<InputStream> response = streamHttpClient.send(request, HttpResponse.BodyHandlers.ofInputStream());
			ensureSuccess(response);
			readSseStream(response.body(), (eventName, dataText)->{
				if(StringUtility.isNullOrEmpty(dataText)){
					return;
				}
				Map<String, Object> payload = JsonUtility.toDictionary(dataText);
				String delta = extractAnthropicStreamDelta(eventName, payload);
				if(!StringUtility.isNullOrEmpty(delta)) {
					sendEvent(channel, "delta", buildMap("delta", delta));
				}
			});
		});
	}

	private void streamGemini(Map<String, Object> params, String model, List<Map<String, Object>> messages, SseChannel channel) throws Exception{
		withHeartbeat(channel, () -> {
			String apiKey = stringVal(params, "apiKey");
			String url = joinUrl(resolveBaseUrl("gemini", stringVal(params, "baseUrl")), String.format("/models/%s:streamGenerateContent?alt=sse&key=%s", urlEncode(model), urlEncode(apiKey)));
			Map<String, Object> body = buildGeminiBody(params, messages);
			HttpRequest request = buildJsonRequest(url, buildAuthHeaders("gemini", apiKey, params), JsonUtility.encode(body), params);
			HttpResponse<InputStream> response = streamHttpClient.send(request, HttpResponse.BodyHandlers.ofInputStream());
			ensureSuccess(response);
			readSseStream(response.body(), (eventName, dataText)->{
				if(StringUtility.isNullOrEmpty(dataText)){
					return;
				}
				Map<String, Object> payload = JsonUtility.toDictionary(dataText);
				String delta = extractGeminiContent(payload);
				if(!StringUtility.isNullOrEmpty(delta)) {
					sendEvent(channel, "delta", buildMap("delta", delta));
				}
			});
		});
	}

	static String protocolFamily(String providerType){
		String normalized = providerType == null ? "" : providerType.trim().toLowerCase();
		if("anthropic".equals(normalized)) {
			return "anthropic";
		}
		if("gemini".equals(normalized)) {
			return "gemini";
		}
		if("ollama".equals(normalized)) {
			return "ollama";
		}
		return "openai-compatible";
	}

	static boolean isOpenAICompatible(String providerType) {
		String family = protocolFamily(providerType);
		return "openai-compatible".equals(family) || "ollama".equals(family);
	}

	static String resolveBaseUrl(String providerType, String baseUrl){
		if(!StringUtility.isNullOrEmpty(baseUrl)) {
			return trimTrailingSlash(baseUrl.trim());
		}
		if("deepseek".equals(providerType)) {
			return DEFAULT_DEEPSEEK_BASE;
		}
		if("openrouter".equals(providerType)) {
			return DEFAULT_OPENROUTER_BASE;
		}
		if("ollama".equals(providerType)) {
			return DEFAULT_OLLAMA_BASE;
		}
		if("anthropic".equals(providerType)) {
			return DEFAULT_ANTHROPIC_BASE;
		}
		if("gemini".equals(providerType)) {
			return DEFAULT_GEMINI_BASE;
		}
		if("moonshot".equals(providerType)) {
			return DEFAULT_MOONSHOT_BASE;
		}
		if("zhipu".equals(providerType)) {
			return DEFAULT_ZHIPU_BASE;
		}
		if("siliconflow".equals(providerType)) {
			return DEFAULT_SILICONFLOW_BASE;
		}
		if("groq".equals(providerType)) {
			return DEFAULT_GROQ_BASE;
		}
		if("xai".equals(providerType)) {
			return DEFAULT_XAI_BASE;
		}
		return DEFAULT_OPENAI_BASE;
	}

	static String trimTrailingSlash(String text){
		String val = text == null ? "" : text.trim();
		while(val.endsWith("/")) {
			val = val.substring(0, val.length() - 1);
		}
		return val;
	}

	static String joinUrl(String baseUrl, String path){
		String base = trimTrailingSlash(baseUrl);
		String suffix = path == null ? "" : path.trim();
		if(suffix.startsWith("http://") || suffix.startsWith("https://")) {
			return suffix;
		}
		if(!suffix.startsWith("/")) {
			suffix = "/" + suffix;
		}
		return base + suffix;
	}

	static Map<String, String> buildAuthHeaders(String providerType, String apiKey){
		return buildAuthHeaders(providerType, apiKey, null);
	}

	static Map<String, String> buildAuthHeaders(String providerType, String apiKey, Map<String, Object> params){
		Map<String, String> headers = new HashMap<String, String>();
		headers.put("Content-Type", "application/json; charset=UTF-8");
		String key = apiKey == null ? "" : apiKey.trim();
		if("anthropic".equals(providerType)) {
			headers.put("x-api-key", key);
			String apiVersion = stringFromAny(providerOptionsMap(params).get("apiVersion"));
			headers.put("anthropic-version", StringUtility.isNullOrEmpty(apiVersion) ? "2023-06-01" : apiVersion);
		}else if(!StringUtility.isNullOrEmpty(key) && !"ollama".equals(providerType) && !"gemini".equals(providerType)) {
			// Gemini 走 URL ?key=,不能再加 Authorization,否则原生接口报 ACCESS_TOKEN_TYPE_UNSUPPORTED。
			// 其它默认 Authorization: Bearer;允许 custom 用 providerOptions.authHeaderName/authPrefix 覆盖,
			// 以兼容要求非 Bearer 方案的官方原生 key(authPrefix 设为 "" 即发原始 key)。
			String authHeaderName = stringFromAny(providerOptionsMap(params).get("authHeaderName"));
			if(StringUtility.isNullOrEmpty(authHeaderName)) {
				authHeaderName = "Authorization";
			}
			Object prefixObj = providerOptionsMap(params).get("authPrefix");
			String authPrefix;
			if(prefixObj == null) {
				authPrefix = "Authorization".equalsIgnoreCase(authHeaderName) ? "Bearer " : "";
			}else {
				authPrefix = stringFromAny(prefixObj);
			}
			headers.put(authHeaderName, authPrefix + key);
		}
		if("openrouter".equals(providerType)) {
			headers.put("HTTP-Referer", "https://www.horosa.com");
			headers.put("X-Title", "Horosa AI Analysis");
		}
		Map<String, Object> extraHeaders = mapVal(providerOptionsMap(params).get("extraHeaders"));
		for(Map.Entry<String, Object> entry : extraHeaders.entrySet()) {
			String headerName = entry.getKey();
			String headerValue = stringFromAny(entry.getValue());
			if(!StringUtility.isNullOrEmpty(headerName) && !StringUtility.isNullOrEmpty(headerValue)) {
				headers.put(headerName, headerValue);
			}
		}
		return headers;
	}

	static List<String> extractModelIds(Map<String, Object> payload){
		List<String> result = new ArrayList<String>();
		if(payload == null) {
			return result;
		}
		Object data = payload.get("data");
		appendModelIds(result, data);
		appendModelIds(result, payload.get("models"));
		if(result.isEmpty() && payload.get("model") instanceof String) {
			result.add((String)payload.get("model"));
		}
		return uniqueStrings(result);
	}

	static Map<String, Object> splitProviderModels(List<String> models, String providerType){
		List<String> allModels = uniqueStrings(models == null ? new ArrayList<String>() : models);
		List<String> embeddingModels = new ArrayList<String>();
		List<String> chatModels = new ArrayList<String>();
		for(String model : allModels) {
			if(isEmbeddingModel(model, providerType)) {
				embeddingModels.add(model);
			}else{
				chatModels.add(model);
			}
		}
		Map<String, Object> result = new LinkedHashMap<String, Object>();
		result.put("models", allModels);
		result.put("chatModels", chatModels);
		result.put("embeddingModels", embeddingModels);
		return result;
	}

	private static boolean isEmbeddingModel(String model, String providerType){
		String normalized = model == null ? "" : model.trim().toLowerCase();
		if(StringUtility.isNullOrEmpty(normalized)) {
			return false;
		}
		if(normalized.contains("embedding")
			|| normalized.contains("embed")
			|| normalized.contains("bge")
			|| normalized.contains("bce")) {
			return true;
		}
		if("gemini".equals(providerType) && normalized.startsWith("text-embedding")) {
			return true;
		}
		return "openai".equals(providerType) && normalized.startsWith("text-embedding");
	}

	private static void appendModelIds(List<String> target, Object obj){
		if(!(obj instanceof List)) {
			return;
		}
		for(Object item : (List)obj) {
			if(item instanceof Map) {
				Map map = (Map)item;
				String id = stringFromAny(map.get("id"));
				if(StringUtility.isNullOrEmpty(id)) {
					id = stringFromAny(map.get("name"));
				}
				if(StringUtility.isNullOrEmpty(id)) {
					id = stringFromAny(map.get("model"));
				}
				if(!StringUtility.isNullOrEmpty(id)) {
					target.add(id);
				}
			}else if(item instanceof String) {
				target.add((String)item);
			}
		}
	}

	static String extractChatContent(String providerType, Map<String, Object> payload){
		if(payload == null) {
			return "";
		}
		if("anthropic".equals(providerType)) {
			return extractAnthropicContent(payload);
		}
		if("gemini".equals(providerType)) {
			return extractGeminiContent(payload);
		}
		return extractOpenAIContent(payload);
	}

	static List<Map<String, Object>> getMessageList(Object obj){
		List<Map<String, Object>> result = new ArrayList<Map<String, Object>>();
		if(!(obj instanceof List)) {
			return result;
		}
		for(Object item : (List)obj) {
			if(item instanceof Map) {
				Map map = (Map)item;
				Map<String, Object> next = new LinkedHashMap<String, Object>();
				next.put("role", stringFromAny(map.get("role")));
				next.put("content", stringFromAny(map.get("content")));
				result.add(next);
			}
		}
		return result;
	}

	static String extractOpenAIContent(Map<String, Object> payload){
		Object choicesObj = payload.get("choices");
		if(!(choicesObj instanceof List) || ((List)choicesObj).isEmpty()) {
			return "";
		}
		Object first = ((List)choicesObj).get(0);
		if(!(first instanceof Map)) {
			return "";
		}
		Map choice = (Map)first;
		Object message = choice.get("message");
		if(message instanceof Map) {
			Object content = ((Map)message).get("content");
			if(content instanceof String) {
				return (String)content;
			}
			if(content instanceof List) {
				return joinTextParts((List)content);
			}
		}
		Object text = choice.get("text");
		return text instanceof String ? (String)text : "";
	}

	static String extractAnthropicContent(Map<String, Object> payload){
		Object contentObj = payload.get("content");
		if(!(contentObj instanceof List)) {
			return "";
		}
		return joinTextParts((List)contentObj);
	}

	static String extractGeminiContent(Map<String, Object> payload){
		Object candidatesObj = payload.get("candidates");
		if(!(candidatesObj instanceof List) || ((List)candidatesObj).isEmpty()) {
			return "";
		}
		Object first = ((List)candidatesObj).get(0);
		if(!(first instanceof Map)) {
			return "";
		}
		Object content = ((Map)first).get("content");
		if(!(content instanceof Map)) {
			return "";
		}
		Object parts = ((Map)content).get("parts");
		if(!(parts instanceof List)) {
			return "";
		}
		return joinTextParts((List)parts);
	}

	static String extractOpenAIStreamDelta(Map<String, Object> payload){
		if(payload == null) {
			return "";
		}
		Object choicesObj = payload.get("choices");
		if(!(choicesObj instanceof List) || ((List)choicesObj).isEmpty()) {
			return "";
		}
		Object first = ((List)choicesObj).get(0);
		if(!(first instanceof Map)) {
			return "";
		}
		Map choice = (Map)first;
		Object deltaObj = choice.get("delta");
		if(deltaObj instanceof Map) {
			Object content = ((Map)deltaObj).get("content");
			if(content instanceof String) {
				return (String)content;
			}
			if(content instanceof List) {
				return joinTextParts((List)content);
			}
		}
		Object messageObj = choice.get("message");
		if(messageObj instanceof Map) {
			Object content = ((Map)messageObj).get("content");
			if(content instanceof String) {
				return (String)content;
			}
			if(content instanceof List) {
				return joinTextParts((List)content);
			}
		}
		return "";
	}

	static String extractAnthropicStreamDelta(String eventName, Map<String, Object> payload){
		if(payload == null) {
			return "";
		}
		String type = stringVal(payload, "type");
		if(StringUtility.isNullOrEmpty(type)) {
			type = eventName;
		}
		if("content_block_delta".equals(type)) {
			Object delta = payload.get("delta");
			if(delta instanceof Map) {
				return stringFromAny(((Map)delta).get("text"));
			}
		}
		return "";
	}

	static List<List<Double>> extractEmbeddingVectors(Map<String, Object> payload){
		List<List<Double>> result = new ArrayList<List<Double>>();
		if(payload == null) {
			return result;
		}
		Object dataObj = payload.get("data");
		if(!(dataObj instanceof List)) {
			return result;
		}
		for(Object item : (List)dataObj) {
			if(!(item instanceof Map)) {
				continue;
			}
			Object embObj = ((Map)item).get("embedding");
			result.add(numberList(embObj));
		}
		return result;
	}

	static List<Double> extractGeminiEmbedding(Map<String, Object> payload){
		if(payload == null) {
			return new ArrayList<Double>();
		}
		Object embObj = payload.get("embedding");
		if(embObj instanceof Map) {
			return numberList(((Map)embObj).get("values"));
		}
		return new ArrayList<Double>();
	}

	private static String joinTextParts(List list){
		List<String> parts = new ArrayList<String>();
		for(Object item : list) {
			if(item instanceof String) {
				parts.add((String)item);
				continue;
			}
			if(item instanceof Map) {
				Map map = (Map)item;
				String text = stringFromAny(map.get("text"));
				if(StringUtility.isNullOrEmpty(text)) {
					text = stringFromAny(map.get("output_text"));
				}
				if(!StringUtility.isNullOrEmpty(text)) {
					parts.add(text);
				}
			}
		}
		return String.join("\n", parts).trim();
	}

	// OpenAI 的 gpt-5.x / o-系列推理模型只接受默认 temperature(=1)，且用 max_completion_tokens 取代 max_tokens；
	// 命中前缀即按推理模型口径构造请求体。去掉 provider 前缀以兼容 openrouter 的 "openai/gpt-5" 写法。
	static boolean isOpenAIReasoningModel(String model){
		if(model == null) {
			return false;
		}
		String m = model.trim().toLowerCase();
		int slash = m.lastIndexOf('/');
		if(slash >= 0) {
			m = m.substring(slash + 1);
		}
		return m.startsWith("gpt-5") || m.startsWith("gpt5")
			|| m.startsWith("gpt-6") || m.startsWith("gpt6")
			|| m.startsWith("o1") || m.startsWith("o3") || m.startsWith("o4") || m.startsWith("o5");
	}

	static Map<String, Object> buildOpenAIChatBody(String model, Map<String, Object> params, List<Map<String, Object>> messages, boolean stream){
		Map<String, Object> requestBody = new LinkedHashMap<String, Object>();
		requestBody.put("model", model);
		requestBody.put("messages", messages);
		boolean reasoning = isOpenAIReasoningModel(model);
		if(!reasoning) {
			requestBody.put("temperature", numVal(params.get("temperature"), 0.7));
		}
		requestBody.put("stream", stream);
		int maxTokens = intVal(params.get("maxTokens"), 0);
		if(maxTokens > 0) {
			requestBody.put(reasoning ? "max_completion_tokens" : "max_tokens", maxTokens);
		}
		requestBody.putAll(buildProviderBodyOptions(params));
		return requestBody;
	}

	private static Map<String, Object> buildAnthropicBody(String model, Map<String, Object> params, List<Map<String, Object>> messages, boolean stream){
		Map<String, Object> body = new LinkedHashMap<String, Object>();
		body.put("model", model);
		body.put("max_tokens", intVal(params.get("maxTokens"), 2048));
		body.put("temperature", numVal(params.get("temperature"), 0.7));
		body.put("stream", stream);
		List<Map<String, Object>> normalized = new ArrayList<Map<String, Object>>();
		List<String> systemParts = new ArrayList<String>();
		for(Map<String, Object> one : messages) {
			String role = stringVal(one, "role");
			String content = stringVal(one, "content");
			if(StringUtility.isNullOrEmpty(content)) {
				continue;
			}
			if("system".equals(role)) {
				systemParts.add(content);
				continue;
			}
			Map<String, Object> item = new LinkedHashMap<String, Object>();
			item.put("role", "assistant".equals(role) ? "assistant" : "user");
			// v2.2.1 (Mac #9):Anthropic /v1/messages 的 content 块必须带 type:"text",
			// 否则上游报 "messages.content: missing field `type`"(503)。
			// 旧代码复用了 Gemini 用的 buildTextPart(只有 text 字段)→ Anthropic 对话与测试连接全失败。
			item.put("content", Arrays.asList(buildAnthropicTextPart(content)));
			normalized.add(item);
		}
		if(!systemParts.isEmpty()) {
			body.put("system", String.join("\n\n", systemParts));
		}
		body.putAll(buildProviderBodyOptions(params));
		body.put("messages", normalized);
		return body;
	}

	private static Map<String, Object> buildGeminiBody(Map<String, Object> params, List<Map<String, Object>> messages){
		Map<String, Object> body = new LinkedHashMap<String, Object>();
		List<Map<String, Object>> normalized = new ArrayList<Map<String, Object>>();
		List<String> systemParts = new ArrayList<String>();
		for(Map<String, Object> one : messages) {
			String role = stringVal(one, "role");
			String content = stringVal(one, "content");
			if(StringUtility.isNullOrEmpty(content)) {
				continue;
			}
			if("system".equals(role)) {
				systemParts.add(content);
				continue;
			}
			Map<String, Object> item = new LinkedHashMap<String, Object>();
			item.put("role", "assistant".equals(role) ? "model" : "user");
			item.put("parts", Arrays.asList(buildTextPart(content)));
			normalized.add(item);
		}
		body.put("contents", normalized);
		if(!systemParts.isEmpty()) {
			Map<String, Object> instruction = new LinkedHashMap<String, Object>();
			instruction.put("parts", Arrays.asList(buildTextPart(String.join("\n\n", systemParts))));
			body.put("systemInstruction", instruction);
		}
		body.putAll(buildProviderBodyOptions(params));
		return body;
	}

	private static Map<String, Object> buildTextPart(String content){
		Map<String, Object> part = new LinkedHashMap<String, Object>();
		part.put("text", content);
		return part;
	}

	// v2.2.1 (Mac #9):Anthropic content block 需要 type:"text"(Gemini 的 parts 不需要,故单独一个)。
	private static Map<String, Object> buildAnthropicTextPart(String content){
		Map<String, Object> part = new LinkedHashMap<String, Object>();
		part.put("type", "text");
		part.put("text", content);
		return part;
	}

	private HttpRequest buildJsonRequest(String url, Map<String, String> headers, String json, Map<String, Object> params){
		int timeoutMs = intVal(providerOptionsMap(params).get("requestTimeoutMs"), 0);
		HttpRequest.Builder builder = HttpRequest.newBuilder()
			.uri(URI.create(url))
			.POST(HttpRequest.BodyPublishers.ofString(json, StandardCharsets.UTF_8));
		// streaming exchanges: only cap when the user set an explicit timeout; otherwise let slow local LLMs run (connectTimeout still guards connect)
		if(timeoutMs > 0){
			builder.timeout(Duration.ofMillis(timeoutMs));
		}
		headers.forEach(builder::header);
		return builder.build();
	}

	private static Map<String, Object> providerOptionsMap(Map<String, Object> params){
		Object providerOptions = params == null ? null : params.get("providerOptions");
		if(providerOptions instanceof Map) {
			return (Map<String, Object>)providerOptions;
		}
		return new LinkedHashMap<String, Object>();
	}

	private static Map<String, Object> mapVal(Object value){
		if(value instanceof Map) {
			return (Map<String, Object>)value;
		}
		return new LinkedHashMap<String, Object>();
	}

	static Map<String, Object> buildProviderBodyOptions(Map<String, Object> params){
		Map<String, Object> options = providerOptionsMap(params);
		Map<String, Object> result = new LinkedHashMap<String, Object>();
		Map<String, Object> extraBody = mapVal(options.get("extraBody"));
		result.putAll(extraBody);
		for(Map.Entry<String, Object> entry : options.entrySet()) {
			String key = entry.getKey();
			if("extraHeaders".equals(key)
				|| "extraBody".equals(key)
				|| "apiVersion".equals(key)
				|| "requestTimeoutMs".equals(key)
				|| "embeddingModel".equals(key)
				|| "authHeaderName".equals(key)
				|| "authPrefix".equals(key)) {
				continue;
			}
			result.put(key, entry.getValue());
		}
		return result;
	}

	private void ensureSuccess(HttpResponse<?> response){
		int status = response.statusCode();
		if(status >= 200 && status < 300) {
			return;
		}
		String detail = readErrorBody(response.body());
		String msg = "上游 provider 请求失败，状态码：" + status;
		if(!StringUtility.isNullOrEmpty(detail)) {
			msg = msg + "；" + detail;
		}
		throw new ErrorCodeException(580021, msg);
	}

	// 仅在非 2xx 分支消费流式响应体，截断后并入错误信息，让上游真因(如 temperature/参数不支持)透传到 error 事件。
	static String readErrorBody(Object body){
		if(!(body instanceof InputStream)) {
			return "";
		}
		try(InputStream in = (InputStream) body){
			byte[] buf = in.readNBytes(4096);
			String text = new String(buf, StandardCharsets.UTF_8).trim();
			if(text.length() > 1000) {
				text = text.substring(0, 1000);
			}
			return text;
		}catch(Exception e){
			return "";
		}
	}

	private void readSseStream(InputStream stream, SseLineHandler handler) throws IOException{
		BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8));
		String line;
		String eventName = "";
		StringBuilder dataBuilder = new StringBuilder();
		while((line = reader.readLine()) != null) {
			if(line.isEmpty()) {
				if(dataBuilder.length() > 0) {
					handler.onEvent(eventName, dataBuilder.toString().trim());
					dataBuilder.setLength(0);
					eventName = "";
				}
				continue;
			}
			if(line.startsWith("event:")) {
				eventName = line.substring(6).trim();
				continue;
			}
			if(line.startsWith("data:")) {
				if(dataBuilder.length() > 0) {
					dataBuilder.append('\n');
				}
				dataBuilder.append(line.substring(5).trim());
			}
		}
		if(dataBuilder.length() > 0) {
			handler.onEvent(eventName, dataBuilder.toString().trim());
		}
	}

	private void sendEvent(SseChannel channel, String eventName, Map<String, Object> payload){
		try{
			SseHelper.markCurrentThread();
			channel.send(SseEmitter.event()
				.name(eventName)
				.data(JsonUtility.encode(payload)));
		}catch(Exception e){
			throw new RuntimeException(e);
		}
	}

	private Map<String, Object> diagnoseDns(String host){
		Instant st = Instant.now();
		try{
			InetAddress[] addresses = InetAddress.getAllByName(host);
			long latencyMs = Duration.between(st, Instant.now()).toMillis();
			List<String> ips = new ArrayList<String>();
			for(InetAddress address : addresses) {
				ips.add(address.getHostAddress());
			}
			return buildMap(
				"ok", true,
				"latencyMs", latencyMs,
				"addresses", ips
			);
		}catch(Exception e){
			return buildMap(
				"ok", false,
				"message", safeErrorMessage(e)
			);
		}
	}

	private Map<String, Object> diagnoseTcp(String host, int port){
		Instant st = Instant.now();
		try(Socket socket = new Socket()) {
			socket.connect(new InetSocketAddress(host, port), 6000);
			long latencyMs = Duration.between(st, Instant.now()).toMillis();
			return buildMap(
				"ok", true,
				"latencyMs", latencyMs,
				"host", host,
				"port", port
			);
		}catch(Exception e){
			return buildMap(
				"ok", false,
				"host", host,
				"port", port,
				"message", safeErrorMessage(e)
			);
		}
	}

	private String normalizedProviderType(Map<String, Object> params){
		String providerType = stringVal(params, "providerType");
		if(StringUtility.isNullOrEmpty(providerType)) {
			throw new ErrorCodeException(580001, "缺少 providerType");
		}
		return providerType.trim().toLowerCase();
	}

	private String requireModel(Map<String, Object> params){
		String model = stringVal(params, "model");
		if(StringUtility.isNullOrEmpty(model)) {
			throw new ErrorCodeException(580012, "缺少 model");
		}
		return model;
	}

	private String requireEmbeddingModel(Map<String, Object> params){
		String model = stringVal(params, "embeddingModel");
		if(StringUtility.isNullOrEmpty(model)) {
			model = stringVal(params, "model");
		}
		if(StringUtility.isNullOrEmpty(model)) {
			throw new ErrorCodeException(580030, "缺少 embeddingModel");
		}
		return model;
	}

	private static List<String> getStringList(Object obj){
		List<String> result = new ArrayList<String>();
		if(obj instanceof List) {
			for(Object one : (List)obj) {
				String text = stringFromAny(one);
				if(!StringUtility.isNullOrEmpty(text)) {
					result.add(text);
				}
			}
		}else {
			String text = stringFromAny(obj);
			if(!StringUtility.isNullOrEmpty(text)) {
				result.add(text);
			}
		}
		return result;
	}

	private static List<Double> numberList(Object obj){
		List<Double> result = new ArrayList<Double>();
		if(!(obj instanceof List)) {
			return result;
		}
		for(Object item : (List)obj) {
			try{
				result.add(Double.parseDouble(String.valueOf(item)));
			}catch(Exception e){
			}
		}
		return result;
	}

	private static List<String> uniqueStrings(List<String> list){
		Set<String> result = new LinkedHashSet<String>();
		for(String item : list) {
			String text = item == null ? "" : item.trim();
			if(!StringUtility.isNullOrEmpty(text)) {
				result.add(text);
			}
		}
		return new ArrayList<String>(result);
	}

	private static String classifyFailure(Exception e){
		String text = safeErrorMessage(e).toLowerCase();
		if(text.contains("unknownhost") || text.contains("name or service not known")) {
			return "dns";
		}
		if(text.contains("connect") || text.contains("timeout") || text.contains("timed out")) {
			return "network";
		}
		if(text.contains("401") || text.contains("403") || text.contains("unauthorized")) {
			return "auth";
		}
		return "http";
	}

	private static String buildFailureRecommendation(String providerType, String failureReason){
		if("dns".equals(failureReason)) {
			return "请检查 Base URL 是否正确，以及当前网络的 DNS 解析是否正常。";
		}
		if("network".equals(failureReason)) {
			if("ollama".equals(providerType)) {
				return "请确认 Ollama 本地服务已启动，并且地址与端口填写正确。";
			}
			return "请检查网络连通性、代理设置和服务端口是否可访问。";
		}
		if("auth".equals(failureReason)) {
			return "请检查 API Key、请求头和供应商类型是否匹配。";
		}
		if("gemini".equals(providerType)) {
			return "请确认 Gemini API Key 可用，并检查是否启用了对应模型权限。";
		}
		return "请检查 Base URL、模型权限和供应商预设是否匹配。";
	}

	private static String urlEncode(String text){
		return URLEncoder.encode(text == null ? "" : text, StandardCharsets.UTF_8);
	}

	private static String safeErrorMessage(Exception e){
		if(e == null){
			return "未知错误";
		}
		String text = e.getMessage();
		return StringUtility.isNullOrEmpty(text) ? e.getClass().getSimpleName() : text;
	}

	private static Map<String, Object> buildMap(Object... args){
		Map<String, Object> map = new LinkedHashMap<String, Object>();
		for(int i=0; i<args.length; i += 2) {
			map.put(String.valueOf(args[i]), args[i + 1]);
		}
		return map;
	}

	private static String stringVal(Map<String, Object> map, String key){
		if(map == null || key == null) {
			return "";
		}
		return stringFromAny(map.get(key));
	}

	private static String stringFromAny(Object obj){
		return obj == null ? "" : String.valueOf(obj).trim();
	}

	private static double numVal(Object obj, double defVal){
		try {
			return obj == null ? defVal : Double.parseDouble(String.valueOf(obj));
		}catch(Exception e) {
			return defVal;
		}
	}

	private static int intVal(Object obj, int defVal){
		try {
			return obj == null ? defVal : Integer.parseInt(String.valueOf(obj));
		}catch(Exception e) {
			return defVal;
		}
	}

	private interface SseLineHandler {
		void onEvent(String eventName, String dataText) throws IOException;
	}
}
