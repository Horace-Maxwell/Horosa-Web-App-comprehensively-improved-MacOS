import {
	buildRetrievedContextText,
	mergeRetrievedChunks,
	rankChunksByKeyword,
	rerankChunksWithVector,
	shouldUseDirectAttach,
	splitTextIntoChunks,
} from '../aiAnalysisRag';

describe('aiAnalysisRag', ()=>{
	test('shouldUseDirectAttach respects threshold', ()=>{
		expect(shouldUseDirectAttach({ extractedText: '短文本' })).toBe(true);
		expect(shouldUseDirectAttach({ extractedText: 'a'.repeat(13000) })).toBe(false);
	});

	test('splitTextIntoChunks creates ordered chunks with overlap', ()=>{
		const chunks = splitTextIntoChunks('a'.repeat(2600), { chunkSize: 1000, overlap: 100 });
		expect(chunks.length).toBeGreaterThan(2);
		expect(chunks[0].chunkIndex).toBe(0);
		expect(chunks[1].startOffset).toBeLessThan(chunks[0].endOffset);
	});

	test('rank and rerank keep strongest chunks first', ()=>{
		const ranked = rankChunksByKeyword('事业 财务', [
			{ id: 'a', content: '事业与财务都有提升', searchText: '事业与财务都有提升' },
			{ id: 'b', content: '只谈健康', searchText: '只谈健康' },
		]);
		expect(ranked[0].id).toBe('a');

		const reranked = rerankChunksWithVector([1, 0], [
			{ id: 'a', keywordScore: 0.5, vector: [0.9, 0.1] },
			{ id: 'b', keywordScore: 0.9, vector: [0.1, 0.9] },
		]);
		expect(reranked[0].id).toBe('a');
	});

	test('mergeRetrievedChunks and buildRetrievedContextText produce bounded context', ()=>{
		const merged = mergeRetrievedChunks([
			{ materialName: '资料一', content: 'A'.repeat(1200) },
			{ materialName: '资料二', content: 'B'.repeat(1200) },
			{ materialName: '资料三', content: 'C'.repeat(1200) },
		], 2100);
		expect(merged.length).toBe(2);
		const text = buildRetrievedContextText(merged);
		expect(text).toContain('资料片段 1');
		expect(text).toContain('来源：资料一');
	});
});
