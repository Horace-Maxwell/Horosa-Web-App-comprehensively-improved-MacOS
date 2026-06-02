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
		defaultEmbeddingModels: ['bge-m3', 'nomic-embed-text'],
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

// —— issue #13：聊天高级参数（思考档 + reasoning 模型识别）——
// 思考档：关/低/中/高。前端按 provider/model 映射成各家请求参数，写进 providerOptions（后端零改）。
export const THINKING_LEVELS = [
	{ value: 'off', label: '关闭' },
	{ value: 'low', label: '低' },
	{ value: 'medium', label: '中' },
	{ value: 'high', label: '高' },
];

const THINKING_BUDGET = { low: 2048, medium: 8192, high: 16000 };

// reasoning 模型（自带思考、拒绝 temperature）——与后端 isOpenAIReasoningModel 同步。
export function isReasoningModel(model){
	const m = ('' + (model || '')).toLowerCase();
	return /(^|\/)(gpt-5|gpt6|o1|o3|o4|o5)/.test(m) || /reasoner|-?r1\b|thinking/.test(m);
}

// 把通用「思考档」映射进 providerOptions（不破坏既有键）。
export function applyThinkingLevel(opts, level, providerType, model){
	if(!level || level === 'off'){
		return opts || {};
	}
	const o = { ...(opts || {}) };
	const budget = THINKING_BUDGET[level] || THINKING_BUDGET.medium;
	if(providerType === 'anthropic'){
		o.thinking = { type: 'enabled', budget_tokens: budget };
	}else if(/(^|\/)(gpt-5|gpt6|o1|o3|o4|o5)/.test(('' + (model || '')).toLowerCase())){
		o.reasoning_effort = level; // low|medium|high
	}else if(providerType === 'gemini'){
		o.generationConfig = { ...(o.generationConfig || {}), thinkingConfig: { thinkingBudget: budget } };
	}
	// deepseek-reasoner(R1) / ollama 等无标准思考参数 → 不动（友好降级）。
	return o;
}
