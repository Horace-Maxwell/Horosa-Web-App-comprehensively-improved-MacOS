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

	private static Map<String, Object> buildMap(Object... args){
		Map<String, Object> map = new LinkedHashMap<String, Object>();
		for(int i=0; i<args.length; i += 2) {
			map.put(String.valueOf(args[i]), args[i + 1]);
		}
		return map;
	}
}
