import JSZip from 'jszip';
import { Document, Packer, Paragraph, TextRun } from 'docx';

function downloadBlob(fileName, blob){
	const url = (window.URL || window.webkitURL).createObjectURL(blob);
	const link = document.createElement('a');
	link.style.display = 'none';
	link.href = url;
	link.setAttribute('download', fileName);
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
	(window.URL || window.webkitURL).revokeObjectURL(url);
}

export function base64ToBlob(base64Data, mimeType = 'application/octet-stream'){
	const clean = `${base64Data || ''}`.split(',').pop();
	const binary = window.atob(clean);
	const bytes = new Uint8Array(binary.length);
	for(let i=0; i<binary.length; i++){
		bytes[i] = binary.charCodeAt(i);
	}
	return new Blob([bytes], { type: mimeType });
}

export function blobToBase64(blob){
	return new Promise((resolve, reject)=>{
		const reader = new FileReader();
		reader.onload = ()=>resolve(`${reader.result || ''}`.split(',').pop() || '');
		reader.onerror = ()=>reject(reader.error || new Error('blob.to.base64.failed'));
		reader.readAsDataURL(blob);
	});
}

export function downloadTextFile(fileName, content, type = 'text/plain;charset=utf-8'){
	downloadBlob(fileName, new Blob([content], { type }));
}

export async function exportConversationDocx(conversation, messages){
	const title = conversation && conversation.title ? conversation.title : 'AI分析会话';
	const lines = [];
	lines.push(new Paragraph({
		children: [
			new TextRun({
				text: title,
				bold: true,
				size: 30,
			}),
		],
	}));
	(messages || []).forEach((item)=>{
		lines.push(new Paragraph({
			children: [
				new TextRun({
					text: `[${item.role}] `,
					bold: true,
				}),
				new TextRun({
					text: item.content || '',
				}),
			],
		}));
	});
	const doc = new Document({
		sections: [
			{
				children: lines,
			},
		],
	});
	return Packer.toBlob(doc);
}

export async function exportConversationByFormat(conversation, messages, format){
	if(format === 'json'){
		return {
			fileName: `${conversation.title || 'conversation'}.json`,
			blob: new Blob([
				JSON.stringify({
					conversation,
					messages,
				}, null, 2),
			], { type: 'application/json;charset=utf-8' }),
		};
	}
	if(format === 'md'){
		const body = (messages || []).map((item)=>`## ${item.role}\n\n${item.content || ''}`).join('\n\n');
		return {
			fileName: `${conversation.title || 'conversation'}.md`,
			blob: new Blob([`# ${conversation.title || 'AI分析会话'}\n\n${body}`], { type: 'text/markdown;charset=utf-8' }),
		};
	}
	if(format === 'docx'){
		return {
			fileName: `${conversation.title || 'conversation'}.docx`,
			blob: await exportConversationDocx(conversation, messages),
		};
	}
	return {
		fileName: `${conversation.title || 'conversation'}.txt`,
		blob: new Blob([(messages || []).map((item)=>`[${item.role}] ${item.content || ''}`).join('\n\n')], { type: 'text/plain;charset=utf-8' }),
	};
}

export async function exportConversationBundle(conversations, getMessages){
	const zip = new JSZip();
	const manifest = [];
	for(let i=0; i<(conversations || []).length; i++){
		const conversation = conversations[i];
		const messages = await getMessages(conversation);
		const mdExport = await exportConversationByFormat(conversation, messages, 'md');
		const jsonExport = await exportConversationByFormat(conversation, messages, 'json');
		zip.file(mdExport.fileName, mdExport.blob);
		zip.file(jsonExport.fileName, jsonExport.blob);
		manifest.push({
			id: conversation.id,
			title: conversation.title,
			model: conversation.model,
			providerName: conversation.providerName,
			lastMessageAt: conversation.lastMessageAt,
		});
	}
	zip.file('manifest.json', JSON.stringify({ conversations: manifest }, null, 2));
	return zip.generateAsync({ type: 'blob' });
}

export async function exportWorkspaceBackupBlob(workspace){
	const zip = new JSZip();
	zip.file('manifest.json', JSON.stringify(workspace || {}, null, 2));
	return zip.generateAsync({ type: 'blob' });
}

export async function parseWorkspaceBackupBlob(blob){
	const zip = await JSZip.loadAsync(blob);
	const manifest = zip.file('manifest.json');
	if(!manifest){
		throw new Error('backup.manifest.missing');
	}
	const text = await manifest.async('string');
	return JSON.parse(text);
}

export function saveBlobToBrowser(fileName, blob){
	downloadBlob(fileName, blob);
}
