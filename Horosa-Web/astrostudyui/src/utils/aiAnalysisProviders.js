const PROVIDER_PRESET_ORDER = [
	'openai',
	'deepseek',
	'anthropic',
	'gemini',
	'openrouter',
	'ollama',
	'moonshot',
	'zhipu',
	'siliconflow',
	'groq',
	'xai',
	'custom',
];

export const PROVIDER_PRESETS = {
	openai: {
		label: 'OpenAI',
		protocolFamily: 'openai-compatible',
		baseUrl: 'https://api.openai.com/v1',
		defaultChatModels: ['gpt-4.1-mini'],
		defaultEmbeddingModels: ['text-embedding-3-small'],
		requestTimeoutMs: 120000,
	},
	deepseek: {
		label: 'DeepSeek',
		protocolFamily: 'openai-compatible',
		baseUrl: 'https://api.deepseek.com',
		defaultChatModels: ['deepseek-chat', 'deepseek-reasoner'],
		defaultEmbeddingModels: [],
		requestTimeoutMs: 120000,
	},
	anthropic: {
		label: 'Anthropic',
		protocolFamily: 'anthropic',
		baseUrl: 'https://api.anthropic.com',
		defaultChatModels: [],
		defaultEmbeddingModels: [],
		requestTimeoutMs: 120000,
		anthropicApiVersion: '2023-06-01',
		anthropicMaxTokens: '2048',
		anthropicThinkingBudget: '',
		anthropicTopP: '',
		anthropicTopK: '',
	},
	gemini: {
		label: 'Gemini',
		protocolFamily: 'gemini',
		baseUrl: 'https://generativelanguage.googleapis.com/v1beta',
		defaultChatModels: ['gemini-2.5-flash', 'gemini-2.5-pro'],
		defaultEmbeddingModels: ['text-embedding-004'],
		requestTimeoutMs: 120000,
	},
	openrouter: {
		label: 'OpenRouter',
		protocolFamily: 'openai-compatible',
		baseUrl: 'https://openrouter.ai/api/v1',
		defaultChatModels: [],
		defaultEmbeddingModels: [],
		requestTimeoutMs: 120000,
	},
	ollama: {
		label: 'Ollama',
		protocolFamily: 'ollama',
		baseUrl: 'http://127.0.0.1:11434/v1',
		defaultChatModels: [],
		defaultEmbeddingModels: [],
		requestTimeoutMs: 120000,
		ollamaKeepAlive: '5m',
		ollamaNumCtx: '8192',
		ollamaNumPredict: '1024',
		ollamaTopK: '40',
		ollamaTopP: '0.9',
		ollamaRepeatPenalty: '1.1',
	},
	moonshot: {
		label: 'Moonshot / Kimi',
		protocolFamily: 'openai-compatible',
		baseUrl: 'https://api.moonshot.cn/v1',
		defaultChatModels: ['kimi-k2.5', 'kimi-k2-turbo-preview'],
		defaultEmbeddingModels: [],
		requestTimeoutMs: 120000,
	},
	zhipu: {
		label: '智谱 AI',
		protocolFamily: 'openai-compatible',
		baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
		defaultChatModels: [],
		defaultEmbeddingModels: [],
		requestTimeoutMs: 120000,
	},
	siliconflow: {
		label: '硅基流动',
		protocolFamily: 'openai-compatible',
		baseUrl: 'https://api.siliconflow.cn/v1',
		defaultChatModels: [],
		defaultEmbeddingModels: [],
		requestTimeoutMs: 120000,
	},
	groq: {
		label: 'Groq',
		protocolFamily: 'openai-compatible',
		baseUrl: 'https://api.groq.com/openai/v1',
		defaultChatModels: [],
		defaultEmbeddingModels: [],
		requestTimeoutMs: 120000,
	},
	xai: {
		label: 'xAI',
		protocolFamily: 'openai-compatible',
		baseUrl: 'https://api.x.ai/v1',
		defaultChatModels: [],
		defaultEmbeddingModels: [],
		requestTimeoutMs: 120000,
	},
	custom: {
		label: '自定义兼容接口',
		protocolFamily: 'openai-compatible',
		baseUrl: '',
		defaultChatModels: [],
		defaultEmbeddingModels: [],
		requestTimeoutMs: 120000,
	},
};

export const PROVIDER_OPTIONS = PROVIDER_PRESET_ORDER.map((value)=>({
	value,
	label: PROVIDER_PRESETS[value].label,
}));

function uniqueTextList(list){
	const found = new Set();
	const result = [];
	(list || []).forEach((item)=>{
		const text = `${item || ''}`.trim();
		if(!text || found.has(text)){
			return;
		}
		found.add(text);
		result.push(text);
	});
	return result;
}

export function getProviderPreset(providerType = 'openai'){
	const key = `${providerType || 'openai'}`.trim().toLowerCase();
	return PROVIDER_PRESETS[key] || PROVIDER_PRESETS.openai;
}

export function getProviderDisplayName(providerType = 'openai'){
	return getProviderPreset(providerType).label;
}

export function getProviderProtocolFamily(providerType = 'openai'){
	return getProviderPreset(providerType).protocolFamily;
}

export function getProviderDefaultChatModels(providerType = 'openai'){
	return uniqueTextList(getProviderPreset(providerType).defaultChatModels || []);
}

export function getProviderDefaultEmbeddingModels(providerType = 'openai'){
	return uniqueTextList(getProviderPreset(providerType).defaultEmbeddingModels || []);
}

export function splitProviderModels(models, providerType = 'openai'){
	const presetEmbedding = new Set(getProviderDefaultEmbeddingModels(providerType));
	const allModels = uniqueTextList(models || []);
	const embeddingModels = allModels.filter((item)=>presetEmbedding.has(item) || /(?:^|[-_/])(embedding|embed)(?:$|[-_/])|bge|bce/i.test(item));
	const chatModels = allModels.filter((item)=>embeddingModels.indexOf(item) < 0);
	return {
		chatModels,
		embeddingModels,
		models: allModels,
	};
}
