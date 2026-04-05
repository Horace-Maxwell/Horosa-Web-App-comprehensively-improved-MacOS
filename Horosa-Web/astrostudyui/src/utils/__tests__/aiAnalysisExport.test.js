import {
	exportConversationByFormat,
	exportWorkspaceBackupBlob,
	parseWorkspaceBackupBlob,
} from '../aiAnalysisExport';

describe('aiAnalysisExport', ()=>{
	test('exportConversationByFormat supports markdown and json', async ()=>{
		const conversation = { title: '测试对话' };
		const messages = [{ role: 'user', content: '你好' }];
		const mdExport = await exportConversationByFormat(conversation, messages, 'md');
		expect(mdExport.fileName).toBe('测试对话.md');
		const mdText = await new Response(mdExport.blob).text();
		expect(mdText).toContain('# 测试对话');

		const jsonExport = await exportConversationByFormat(conversation, messages, 'json');
		expect(jsonExport.fileName).toBe('测试对话.json');
		const jsonText = await new Response(jsonExport.blob).text();
		expect(jsonText).toContain('"role": "user"');
	});

	test('workspace backup can roundtrip manifest payload', async ()=>{
		const workspace = {
			snapshotVersion: 2,
			stores: {
				provider_profiles: [{ id: 'provider-1' }],
				materials: [{ id: 'material-1' }],
			},
		};
		const blob = await exportWorkspaceBackupBlob(workspace);
		const parsed = await parseWorkspaceBackupBlob(blob);
		expect(parsed.snapshotVersion).toBe(2);
		expect(parsed.stores.provider_profiles[0].id).toBe('provider-1');
	});
});
