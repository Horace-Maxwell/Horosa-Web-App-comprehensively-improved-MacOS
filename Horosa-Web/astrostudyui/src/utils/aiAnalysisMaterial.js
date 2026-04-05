import { extractMaterialContent } from '../services/aianalysis';

function readFileAsText(file){
	return new Promise((resolve, reject)=>{
		const reader = new FileReader();
		reader.onload = ()=>{
			resolve(`${reader.result || ''}`);
		};
		reader.onerror = ()=>{
			reject(reader.error || new Error('file.read.failed'));
		};
		reader.readAsText(file);
	});
}

function readFileAsArrayBuffer(file){
	return new Promise((resolve, reject)=>{
		const reader = new FileReader();
		reader.onload = ()=>resolve(reader.result);
		reader.onerror = ()=>reject(reader.error || new Error('file.read.failed'));
		reader.readAsArrayBuffer(file);
	});
}

function lowerName(file){
	return `${file && file.name ? file.name : ''}`.toLowerCase();
}

export function guessKind(file){
	const name = lowerName(file);
	if(name.endsWith('.pdf')){
		return 'pdf';
	}
	if(name.endsWith('.docx')){
		return 'docx';
	}
	if(name.endsWith('.doc')){
		return 'doc';
	}
	if(name.endsWith('.md') || name.endsWith('.markdown')){
		return 'md';
	}
	return 'txt';
}

export async function arrayBufferToBase64(buffer){
	const bytes = new Uint8Array(buffer);
	const chunkSize = 0x8000;
	let binary = '';
	for(let i=0; i<bytes.length; i += chunkSize){
		const chunk = bytes.subarray(i, i + chunkSize);
		binary += String.fromCharCode.apply(null, Array.from(chunk));
	}
	return window.btoa(binary);
}

export async function sha256Hex(buffer){
	const digest = await window.crypto.subtle.digest('SHA-256', buffer);
	return Array.from(new Uint8Array(digest)).map((item)=>item.toString(16).padStart(2, '0')).join('');
}

export async function parseMaterialFile(file){
	if(!file){
		throw new Error('material.file.required');
	}
	const kind = guessKind(file);
	const arrayBuffer = await readFileAsArrayBuffer(file);
	const base64Data = await arrayBufferToBase64(arrayBuffer);
	const fileHash = await sha256Hex(arrayBuffer);
	let extracted = null;
	if(kind === 'txt' || kind === 'md'){
		const text = await readFileAsText(file);
		extracted = {
			fileName: file.name || '未命名资料',
			fileExt: kind === 'md' ? '.md' : '.txt',
			mimeType: file.type || (kind === 'md' ? 'text/markdown' : 'text/plain'),
			size: file.size || 0,
			fileHash,
			extractedText: `${text || ''}`.trim(),
			textHash: await sha256Hex(new TextEncoder().encode(`${text || ''}`.trim())),
			extractMeta: {
				extractor: 'browser-text',
			},
		};
	}else{
		const rsp = await extractMaterialContent({
			fileName: file.name || '未命名资料',
			mimeType: file.type || '',
			base64Data,
		});
		extracted = rsp && rsp.Result ? rsp.Result : null;
	}
	if(!extracted){
		throw new Error('material.extract.failed');
	}
	return {
		name: extracted.fileName || file.name || '未命名资料',
		fileName: extracted.fileName || file.name || '未命名资料',
		fileExt: extracted.fileExt || `.${kind}`,
		kind,
		size: extracted.size || file.size || 0,
		mimeType: extracted.mimeType || file.type || '',
		fileHash: extracted.fileHash || fileHash,
		textHash: extracted.textHash || '',
		originBlob: base64Data,
		extractedText: `${extracted.extractedText || ''}`.trim(),
		extractMeta: extracted.extractMeta || {},
	};
}
