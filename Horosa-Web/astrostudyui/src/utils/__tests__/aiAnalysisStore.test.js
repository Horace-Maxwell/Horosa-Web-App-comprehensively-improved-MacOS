import {
	AI_ANALYSIS_SCHEMA_VERSION,
	AI_ANALYSIS_STORES,
	buildTimestampLabel,
	loadUiPrefs,
	migrateRecord,
	saveUiPrefs,
} from '../aiAnalysisStore';

describe('aiAnalysisStore ui prefs', ()=>{
	beforeEach(()=>{
		window.localStorage.clear();
	});

	test('saveUiPrefs merges with existing values', ()=>{
		saveUiPrefs({ innerTab: 'analysis' });
		const merged = saveUiPrefs({ modelSelection: 'provider::model' });
		expect(merged).toEqual({
			innerTab: 'analysis',
			modelSelection: 'provider::model',
		});
		expect(loadUiPrefs()).toEqual(merged);
	});

	test('buildTimestampLabel returns compact local label', ()=>{
		expect(buildTimestampLabel('2026-04-04T12:34:56.000Z')).toMatch(/^2026-04-04 \d{2}:\d{2}$/);
	});

	test('migrateRecord upgrades legacy provider profile with preset defaults', ()=>{
		const migrated = migrateRecord(AI_ANALYSIS_STORES.providerProfiles, {
			id: 'provider-legacy',
			providerType: 'deepseek',
			manualModels: [],
			availableModels: [],
			providerOptions: {},
			schemaVersion: 2,
		});
		expect(migrated.protocolFamily).toBe('openai-compatible');
		expect(migrated.name).toBe('DeepSeek');
		expect(migrated.chatModelIds).toEqual(['deepseek-chat', 'deepseek-reasoner']);
		expect(migrated.embeddingModelIds).toEqual([]);
		expect(migrated.providerOptions.requestTimeoutMs).toBe(120000);
		expect(migrated.healthStatus).toBe('unknown');
		expect(migrated.schemaVersion).toBe(AI_ANALYSIS_SCHEMA_VERSION);
	});
});
