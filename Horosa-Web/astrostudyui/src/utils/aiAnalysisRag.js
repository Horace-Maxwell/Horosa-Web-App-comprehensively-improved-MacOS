import { AI_ANALYSIS_STORES, bulkPutStoreRecords, listStoreRecords } from './aiAnalysisStore';

const DEFAULT_CHUNK_SIZE = 1200;
const DEFAULT_CHUNK_OVERLAP = 180;
const DIRECT_ATTACH_THRESHOLD = 12000;

function normalizeText(text){
	return `${text || ''}`.replace(/\r/g, '').trim();
}

function tokenize(text){
	return normalizeText(text)
		.toLowerCase()
		.split(/[^a-z0-9\u4e00-\u9fa5]+/g)
		.filter(Boolean);
}

export function shouldUseDirectAttach(material){
	return normalizeText(material && material.extractedText).length <= DIRECT_ATTACH_THRESHOLD;
}

export function splitTextIntoChunks(text, options = {}){
	const raw = normalizeText(text);
	if(!raw){
		return [];
	}
	const chunkSize = Math.max(400, options.chunkSize || DEFAULT_CHUNK_SIZE);
	const overlap = Math.max(0, options.overlap || DEFAULT_CHUNK_OVERLAP);
	const chunks = [];
	let start = 0;
	while(start < raw.length){
		const end = Math.min(raw.length, start + chunkSize);
		const content = raw.slice(start, end).trim();
		if(content){
			chunks.push({
				chunkIndex: chunks.length,
				content,
				startOffset: start,
				endOffset: end,
				searchText: content.toLowerCase(),
			});
		}
		if(end >= raw.length){
			break;
		}
		start = Math.max(end - overlap, start + 1);
	}
	return chunks;
}

export async function ensureMaterialChunks(material, options = {}){
	if(!material || !material.id){
		return [];
	}
	const existing = (await listStoreRecords(AI_ANALYSIS_STORES.materialChunks)).filter((item)=>item.materialId === material.id);
	if(existing.length){
		return existing.sort((a, b)=>a.chunkIndex - b.chunkIndex);
	}
	const chunks = splitTextIntoChunks(material.extractedText || '', options).map((item)=>({
		...item,
		materialId: material.id,
	}));
	if(chunks.length === 0){
		return [];
	}
	return bulkPutStoreRecords(AI_ANALYSIS_STORES.materialChunks, chunks, 'chunk');
}

function keywordScore(queryTokens, chunk){
	if(!queryTokens.length){
		return 0;
	}
	const text = `${chunk && chunk.searchText ? chunk.searchText : chunk && chunk.content ? chunk.content : ''}`.toLowerCase();
	let score = 0;
	queryTokens.forEach((token)=>{
		if(text.indexOf(token) >= 0){
			score += 1;
		}
	});
	return score / queryTokens.length;
}

function cosineSimilarity(a, b){
	if(!Array.isArray(a) || !Array.isArray(b) || a.length === 0 || b.length === 0){
		return 0;
	}
	const len = Math.min(a.length, b.length);
	let dot = 0;
	let na = 0;
	let nb = 0;
	for(let i=0; i<len; i++){
		const va = Number(a[i]) || 0;
		const vb = Number(b[i]) || 0;
		dot += va * vb;
		na += va * va;
		nb += vb * vb;
	}
	if(!na || !nb){
		return 0;
	}
	return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

export function rerankChunksWithVector(queryVector, chunkEntries){
	return (chunkEntries || []).map((item)=>({
		...item,
		vectorScore: cosineSimilarity(queryVector, item.vector || []),
		totalScore: (item.keywordScore || 0) * 0.45 + cosineSimilarity(queryVector, item.vector || []) * 0.55,
	})).sort((a, b)=>b.totalScore - a.totalScore);
}

export function rankChunksByKeyword(query, chunkEntries){
	const queryTokens = tokenize(query);
	return (chunkEntries || []).map((item)=>({
		...item,
		keywordScore: keywordScore(queryTokens, item),
		totalScore: keywordScore(queryTokens, item),
	})).sort((a, b)=>b.totalScore - a.totalScore);
}

export function mergeRetrievedChunks(scoredChunks, maxChars = 5000){
	const picked = [];
	let total = 0;
	for(let i=0; i<(scoredChunks || []).length; i++){
		const item = scoredChunks[i];
		const content = normalizeText(item.content);
		if(!content){
			continue;
		}
		if(total >= maxChars && picked.length > 0){
			break;
		}
		picked.push(item);
		total += content.length;
	}
	return picked;
}

export function buildRetrievedContextText(scoredChunks){
	return (scoredChunks || []).map((item, idx)=>[
		`资料片段 ${idx + 1}`,
		item.materialName ? `来源：${item.materialName}` : '',
		item.content || '',
	].filter(Boolean).join('\n')).join('\n\n').trim();
}
