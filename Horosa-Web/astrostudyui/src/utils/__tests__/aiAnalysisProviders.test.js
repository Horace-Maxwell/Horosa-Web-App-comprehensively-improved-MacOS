import {
	getProviderDefaultChatModels,
	getProviderDefaultEmbeddingModels,
	getProviderDisplayName,
	getProviderPreset,
	getProviderProtocolFamily,
	splitProviderModels,
} from '../aiAnalysisProviders';

describe('aiAnalysisProviders', ()=>{
	test('deepseek preset exposes expected defaults', ()=>{
		const preset = getProviderPreset('deepseek');
		expect(preset.baseUrl).toBe('https://api.deepseek.com');
		expect(getProviderDisplayName('deepseek')).toBe('DeepSeek');
		expect(getProviderProtocolFamily('deepseek')).toBe('openai-compatible');
		expect(getProviderDefaultChatModels('deepseek')).toEqual(['deepseek-chat', 'deepseek-reasoner']);
		expect(getProviderDefaultEmbeddingModels('deepseek')).toEqual([]);
	});

	test('moonshot preset exposes expected defaults', ()=>{
		const preset = getProviderPreset('moonshot');
		expect(preset.baseUrl).toBe('https://api.moonshot.cn/v1');
		expect(getProviderDefaultChatModels('moonshot')).toEqual(['kimi-k2.5', 'kimi-k2-turbo-preview']);
	});

	test('gemini preset exposes chat models distinct from embedding models', ()=>{
		const preset = getProviderPreset('gemini');
		expect(preset.baseUrl).toBe('https://generativelanguage.googleapis.com/v1beta');
		expect(getProviderProtocolFamily('gemini')).toBe('gemini');
		expect(getProviderDefaultChatModels('gemini')).toEqual(['gemini-2.5-flash', 'gemini-2.5-pro']);
		expect(getProviderDefaultEmbeddingModels('gemini')).toEqual(['text-embedding-004']);
	});

	test('splitProviderModels separates embedding-like ids', ()=>{
		expect(splitProviderModels(['deepseek-chat', 'text-embedding-3-small', 'bge-large-zh'], 'deepseek')).toEqual({
			models: ['deepseek-chat', 'text-embedding-3-small', 'bge-large-zh'],
			chatModels: ['deepseek-chat'],
			embeddingModels: ['text-embedding-3-small', 'bge-large-zh'],
		});
	});
});
