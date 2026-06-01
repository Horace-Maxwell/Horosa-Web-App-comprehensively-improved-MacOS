package spacex.astrostudy.service;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.junit.Test;

public class AIAnalysisProxyServiceTest {

	@Test
	public void resolveBaseUrlUsesProviderDefaults() {
		assertEquals("https://api.openai.com/v1", AIAnalysisProxyService.resolveBaseUrl("openai", ""));
		assertEquals("https://api.deepseek.com", AIAnalysisProxyService.resolveBaseUrl("deepseek", null));
		assertEquals("https://openrouter.ai/api/v1", AIAnalysisProxyService.resolveBaseUrl("openrouter", null));
		assertEquals("http://127.0.0.1:11434/v1", AIAnalysisProxyService.resolveBaseUrl("ollama", null));
		assertEquals("https://api.moonshot.cn/v1", AIAnalysisProxyService.resolveBaseUrl("moonshot", null));
		assertEquals("https://open.bigmodel.cn/api/paas/v4", AIAnalysisProxyService.resolveBaseUrl("zhipu", null));
		assertEquals("https://api.siliconflow.cn/v1", AIAnalysisProxyService.resolveBaseUrl("siliconflow", null));
		assertEquals("https://api.groq.com/openai/v1", AIAnalysisProxyService.resolveBaseUrl("groq", null));
		assertEquals("https://api.x.ai/v1", AIAnalysisProxyService.resolveBaseUrl("xai", null));
	}

	@Test
	public void protocolFamilySupportsMainstreamProviderPresets() {
		assertEquals("openai-compatible", AIAnalysisProxyService.protocolFamily("deepseek"));
		assertEquals("openai-compatible", AIAnalysisProxyService.protocolFamily("moonshot"));
		assertEquals("openai-compatible", AIAnalysisProxyService.protocolFamily("zhipu"));
		assertEquals("openai-compatible", AIAnalysisProxyService.protocolFamily("siliconflow"));
		assertEquals("openai-compatible", AIAnalysisProxyService.protocolFamily("groq"));
		assertEquals("openai-compatible", AIAnalysisProxyService.protocolFamily("xai"));
		assertEquals("anthropic", AIAnalysisProxyService.protocolFamily("anthropic"));
		assertEquals("gemini", AIAnalysisProxyService.protocolFamily("gemini"));
		assertEquals("ollama", AIAnalysisProxyService.protocolFamily("ollama"));
	}

	@Test
	public void extractModelIdsSupportsOpenAIAndOllamaShapes() {
		Map<String, Object> payload = new HashMap<String, Object>();
		payload.put("data", Arrays.asList(
			buildMap("id", "gpt-4.1"),
			buildMap("id", "gpt-4.1-mini")
		));
		payload.put("models", Arrays.asList(
			buildMap("name", "llama3.1")
		));
		List<String> ids = AIAnalysisProxyService.extractModelIds(payload);
		assertEquals(Arrays.asList("gpt-4.1", "gpt-4.1-mini", "llama3.1"), ids);
	}

	@Test
	public void splitProviderModelsSeparatesEmbeddingModels() {
		Map<String, Object> split = AIAnalysisProxyService.splitProviderModels(
			Arrays.asList("deepseek-chat", "text-embedding-3-small", "mock-embedding-1"),
			"deepseek"
		);
		assertEquals(Arrays.asList("deepseek-chat"), split.get("chatModels"));
		assertEquals(Arrays.asList("text-embedding-3-small", "mock-embedding-1"), split.get("embeddingModels"));
	}

	@Test
	public void extractChatContentSupportsOpenAIAndGeminiShapes() {
		Map<String, Object> openai = new LinkedHashMap<String, Object>();
		openai.put("choices", Arrays.asList(
			buildMap("message", buildMap("content", "分析结果"))
		));
		assertEquals("分析结果", AIAnalysisProxyService.extractChatContent("openai", openai));

		Map<String, Object> gemini = new LinkedHashMap<String, Object>();
		gemini.put("candidates", Arrays.asList(
			buildMap("content", buildMap("parts", Arrays.asList(buildMap("text", "Gemini结果"))))
		));
		assertEquals("Gemini结果", AIAnalysisProxyService.extractChatContent("gemini", gemini));
	}

	@Test
	public void extractOpenAIStreamDeltaReadsDeltaAndContentList() {
		Map<String, Object> payload = new LinkedHashMap<String, Object>();
		payload.put("choices", Arrays.asList(
			buildMap("delta", buildMap("content", "流式结果"))
		));
		assertEquals("流式结果", AIAnalysisProxyService.extractOpenAIStreamDelta(payload));

		Map<String, Object> richPayload = new LinkedHashMap<String, Object>();
		richPayload.put("choices", Arrays.asList(
			buildMap("delta", buildMap("content", Arrays.asList(buildMap("text", "分段"))))
		));
		assertEquals("分段", AIAnalysisProxyService.extractOpenAIStreamDelta(richPayload));
	}

	@Test
	public void extractAnthropicStreamDeltaOnlyReadsContentBlockDelta() {
		Map<String, Object> payload = buildMap(
			"type", "content_block_delta",
			"delta", buildMap("text", "Anthropic流")
		);
		assertEquals("Anthropic流", AIAnalysisProxyService.extractAnthropicStreamDelta("content_block_delta", payload));
		assertEquals("", AIAnalysisProxyService.extractAnthropicStreamDelta("message_stop", buildMap("type", "message_stop")));
	}

	@Test
	public void extractEmbeddingVectorsSupportsOpenAIShape() {
		Map<String, Object> payload = buildMap(
			"data", Arrays.asList(
				buildMap("embedding", Arrays.asList(0.1d, 0.2d)),
				buildMap("embedding", Arrays.asList(0.3d, 0.4d))
			)
		);
		List<List<Double>> vectors = AIAnalysisProxyService.extractEmbeddingVectors(payload);
		assertEquals(2, vectors.size());
		assertEquals(Arrays.asList(0.1d, 0.2d), vectors.get(0));
	}

	@Test
	public void extractModelIdsSkipsEmptyValues() {
		Map<String, Object> payload = buildMap(
			"data", Arrays.asList(
				buildMap("id", ""),
				buildMap("name", "model-a"),
				"",
				null
			)
		);
		List<String> ids = AIAnalysisProxyService.extractModelIds(payload);
		assertEquals(1, ids.size());
		assertEquals("model-a", ids.get(0));
		assertFalse(ids.contains(""));
	}

	@Test
	public void getMessageListNormalizesInput() {
		List<Map<String, Object>> messages = AIAnalysisProxyService.getMessageList(Arrays.asList(
			buildMap("role", "system", "content", "你是助手"),
			buildMap("role", "user", "content", "请分析")
		));
		assertEquals(2, messages.size());
		assertEquals("system", messages.get(0).get("role"));
		assertTrue(messages.get(1).containsKey("content"));
	}

	@Test
	public void buildAuthHeadersSupportsAnthropicApiVersionAndExtraHeaders() {
		Map<String, Object> params = buildMap(
			"providerOptions", buildMap(
				"apiVersion", "2024-02-29",
				"extraHeaders", buildMap("x-test-header", "demo")
			)
		);
		Map<String, String> headers = AIAnalysisProxyService.buildAuthHeaders("anthropic", "anth-key", params);
		assertEquals("2024-02-29", headers.get("anthropic-version"));
		assertEquals("demo", headers.get("x-test-header"));
		assertEquals("anth-key", headers.get("x-api-key"));
	}

	@Test
	public void buildProviderBodyOptionsMergesExtraBodyAndSkipsReservedKeys() {
		Map<String, Object> params = buildMap(
			"providerOptions", buildMap(
				"extraHeaders", buildMap("x-debug", "1"),
				"extraBody", buildMap("response_format", buildMap("type", "json_object")),
				"requestTimeoutMs", 15000,
				"top_p", 0.8d
			)
		);
		Map<String, Object> bodyOptions = AIAnalysisProxyService.buildProviderBodyOptions(params);
		assertTrue(bodyOptions.containsKey("response_format"));
		assertEquals(0.8d, bodyOptions.get("top_p"));
		assertFalse(bodyOptions.containsKey("extraHeaders"));
		assertFalse(bodyOptions.containsKey("requestTimeoutMs"));
	}

	@Test
	public void isOpenAIReasoningModelMatchesGpt5AndOSeries() {
		assertTrue(AIAnalysisProxyService.isOpenAIReasoningModel("gpt-5.5"));
		assertTrue(AIAnalysisProxyService.isOpenAIReasoningModel("gpt-5.5-2026-04-23"));
		assertTrue(AIAnalysisProxyService.isOpenAIReasoningModel("o3-mini"));
		assertTrue(AIAnalysisProxyService.isOpenAIReasoningModel("o1"));
		assertTrue(AIAnalysisProxyService.isOpenAIReasoningModel("openai/gpt-5"));
		assertFalse(AIAnalysisProxyService.isOpenAIReasoningModel("gpt-4.1"));
		assertFalse(AIAnalysisProxyService.isOpenAIReasoningModel("gpt-4o"));
		assertFalse(AIAnalysisProxyService.isOpenAIReasoningModel("deepseek-reasoner"));
		assertFalse(AIAnalysisProxyService.isOpenAIReasoningModel(null));
	}

	@Test
	public void buildOpenAIChatBodyAdaptsReasoningModels() {
		List<Map<String, Object>> messages = AIAnalysisProxyService.getMessageList(Arrays.asList(
			buildMap("role", "user", "content", "hi")
		));
		Map<String, Object> params = buildMap("maxTokens", 1024);

		Map<String, Object> reasoning = AIAnalysisProxyService.buildOpenAIChatBody("gpt-5.5", params, messages, false);
		assertFalse(reasoning.containsKey("temperature"));
		assertFalse(reasoning.containsKey("max_tokens"));
		assertEquals(Integer.valueOf(1024), reasoning.get("max_completion_tokens"));

		Map<String, Object> classic = AIAnalysisProxyService.buildOpenAIChatBody("gpt-4.1", params, messages, false);
		assertEquals(0.7d, classic.get("temperature"));
		assertEquals(Integer.valueOf(1024), classic.get("max_tokens"));
		assertFalse(classic.containsKey("max_completion_tokens"));
	}

	@Test
	public void readErrorBodyDecodesAndTruncatesUpstreamError() {
		java.io.InputStream small = new java.io.ByteArrayInputStream(
			"temperature does not support 0.7".getBytes(java.nio.charset.StandardCharsets.UTF_8));
		assertEquals("temperature does not support 0.7", AIAnalysisProxyService.readErrorBody(small));

		// non-InputStream input yields empty (no crash)
		assertEquals("", AIAnalysisProxyService.readErrorBody("not a stream"));
		assertEquals("", AIAnalysisProxyService.readErrorBody(null));

		// oversized body is truncated to 1000 chars
		byte[] big = new byte[2000];
		java.util.Arrays.fill(big, (byte) 'x');
		String truncated = AIAnalysisProxyService.readErrorBody(new java.io.ByteArrayInputStream(big));
		assertEquals(1000, truncated.length());
	}

	@Test
	public void buildAuthHeadersOmitsBearerForGeminiAndSupportsOverride() {
		Map<String, String> gemini = AIAnalysisProxyService.buildAuthHeaders("gemini", "AIza-key", buildMap());
		assertFalse(gemini.containsKey("Authorization"));

		Map<String, String> openai = AIAnalysisProxyService.buildAuthHeaders("openai", "sk-key", buildMap());
		assertEquals("Bearer sk-key", openai.get("Authorization"));

		Map<String, Object> overrideParams = buildMap("providerOptions", buildMap("authHeaderName", "x-api-key", "authPrefix", ""));
		Map<String, String> custom = AIAnalysisProxyService.buildAuthHeaders("custom", "raw-key", overrideParams);
		assertEquals("raw-key", custom.get("x-api-key"));
		assertFalse(custom.containsKey("Authorization"));

		Map<String, String> ollama = AIAnalysisProxyService.buildAuthHeaders("ollama", "", buildMap());
		assertFalse(ollama.containsKey("Authorization"));
	}

	private static Map<String, Object> buildMap(Object... args){
		Map<String, Object> map = new LinkedHashMap<String, Object>();
		for(int i=0; i<args.length; i += 2) {
			map.put(String.valueOf(args[i]), args[i + 1]);
		}
		return map;
	}
}
