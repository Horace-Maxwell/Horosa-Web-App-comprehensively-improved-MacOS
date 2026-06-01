import { normalizeDesktopImportItems } from '../aiAnalysisDesktop';

describe('aiAnalysisDesktop', ()=>{
	test('normalizes camelCase desktop payloads', ()=>{
		expect(normalizeDesktopImportItems([
			{
				fileName: 'demo.md',
				mimeType: 'text/markdown',
				base64Data: 'ZGVtbw==',
				relativePath: 'demo.md',
			},
		])).toEqual([
			{
				fileName: 'demo.md',
				mimeType: 'text/markdown',
				base64Data: 'ZGVtbw==',
				relativePath: 'demo.md',
			},
		]);
	});

	test('normalizes snake_case desktop payloads', ()=>{
		expect(normalizeDesktopImportItems([
			{
				file_name: 'folder/demo.md',
				mime_type: 'text/markdown',
				base64_data: 'ZGVtbw==',
				relative_path: 'folder/demo.md',
			},
		])).toEqual([
			{
				fileName: 'folder/demo.md',
				mimeType: 'text/markdown',
				base64Data: 'ZGVtbw==',
				relativePath: 'folder/demo.md',
			},
		]);
	});

	test('filters malformed payloads', ()=>{
		expect(normalizeDesktopImportItems([
			null,
			{},
			{ fileName: 'bad.md' },
			{ base64Data: 'ZGVtbw==' },
		])).toEqual([]);
	});
});
