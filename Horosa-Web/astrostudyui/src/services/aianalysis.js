import {
	ClientApp,
	ClientChannel,
	ClientVer,
	ServerRoot,
	TokenKey,
} from '../utils/constants';
import { signRequest } from '../utils/request';

function safeParseJson(text, defVal = null){
	try{
		return text ? JSON.parse(text) : defVal;
	}catch(e){
		return defVal;
	}
}

// 尊重用户在 providerOptions.requestTimeoutMs 配置的超时(1s~10min),否则回退 120s。
function resolveRequestTimeout(values){
	const raw = values && values.providerOptions ? Number(values.providerOptions.requestTimeoutMs) : NaN;
	if(Number.isFinite(raw) && raw >= 1000){
		return Math.min(raw, 600000);
	}
	return 120000;
}

function unwrapServicePayload(payload){
	if(!payload || typeof payload !== 'object'){
		return payload;
	}
	if(payload.Result && typeof payload.Result === 'object' && !Array.isArray(payload.Result) && Object.prototype.hasOwnProperty.call(payload.Result, 'Result')){
		return {
			...payload,
			Result: payload.Result.Result,
		};
	}
	return payload;
}

function createSseParser(onEvent){
	let buffer = '';
	let eventName = 'message';
	let dataLines = [];

	function normalizeLine(rawLine){
		const line = `${rawLine || ''}`;
		if(!line){
			return line;
		}
		const eventIdx = line.indexOf('event:');
		const dataIdx = line.indexOf('data:');
		let idx = -1;
		if(eventIdx >= 0 && dataIdx >= 0){
			idx = Math.min(eventIdx, dataIdx);
		}else if(eventIdx >= 0){
			idx = eventIdx;
		}else if(dataIdx >= 0){
			idx = dataIdx;
		}
		return idx > 0 ? line.slice(idx) : line;
	}

	function flushEvent(){
		if(dataLines.length === 0){
			eventName = 'message';
			return;
		}
		const data = dataLines.join('\n');
		onEvent({
			type: eventName || 'message',
			data,
			json: safeParseJson(data, null),
		});
		eventName = 'message';
		dataLines = [];
	}

	return {
		push(chunk){
			buffer += chunk || '';
			let idx = buffer.indexOf('\n');
			while(idx >= 0){
				const rawLine = buffer.slice(0, idx);
				buffer = buffer.slice(idx + 1);
				const line = normalizeLine(rawLine.replace(/\r$/, ''));
				if(!line){
					flushEvent();
				}else if(line.indexOf('event:') === 0){
					eventName = line.slice(6).trim() || 'message';
				}else if(line.indexOf('data:') === 0){
					dataLines.push(line.slice(5).trim());
				}
				idx = buffer.indexOf('\n');
			}
		},
		end(){
			if(buffer){
				this.push('\n');
			}
			flushEvent();
		},
	};
}

function getTokenSafe(){
	try{
		if(typeof window !== 'undefined' && window.localStorage){
			return window.localStorage.getItem(TokenKey) || '';
		}
	}catch(e){
	}
	return '';
}

function buildAIAnalysisHeaders(bodyText = '', extraHeaders = {}){
	return {
		'Content-Type': 'application/json; charset=UTF-8',
		Token: getTokenSafe(),
		ClientChannel,
		ClientApp,
		ClientVer,
		Signature: signRequest(bodyText || ''),
		...extraHeaders,
	};
}

function withTimeout(promiseFactory, timeoutMs, externalSignal){
	const timeout = Number(timeoutMs) > 0 ? Math.floor(Number(timeoutMs)) : 0;
	if(!timeout && !externalSignal){
		return promiseFactory(null);
	}
	const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
	const cleanup = [];
	if(controller && externalSignal && typeof externalSignal.addEventListener === 'function'){
		const abortListener = ()=>controller.abort();
		externalSignal.addEventListener('abort', abortListener, { once: true });
		cleanup.push(()=>externalSignal.removeEventListener('abort', abortListener));
	}
	let timer = null;
	if(controller && timeout){
		timer = setTimeout(()=>{
			controller.abort();
		}, timeout);
	}
	return promiseFactory(controller ? controller.signal : externalSignal).finally(()=>{
		if(timer){
			clearTimeout(timer);
		}
		cleanup.forEach((fn)=>fn());
	});
}

async function requestJson(url, values, options = {}){
	return withTimeout(async (signal)=>{
		const bodyText = JSON.stringify(values || {});
		const response = await fetch(url, {
			method: 'POST',
			cache: 'no-store',
			headers: buildAIAnalysisHeaders(bodyText, options.headers),
			body: bodyText,
			signal,
		});
		const text = await response.text();
		const payload = safeParseJson(text, null);
		if(!response.ok){
			const errorText = payload && (payload.ResultMessage || payload.Result || payload.message)
				? (payload.ResultMessage || payload.Result || payload.message)
				: `${response.status} ${response.statusText || ''}`.trim();
			throw new Error(errorText || 'request.failed');
		}
		if(payload === null){
			throw new Error('service.response.invalid');
		}
		return unwrapServicePayload(payload);
	}, options.timeoutMs, options.signal);
}

export function fetchProviderModels(values){
	return requestJson(`${ServerRoot}/aianalysis/providers/models`, values, {
		timeoutMs: resolveRequestTimeout(values),
	});
}

export function diagnoseProvider(values){
	return requestJson(`${ServerRoot}/aianalysis/providers/diagnose`, values, {
		timeoutMs: resolveRequestTimeout(values),
	});
}

export function extractMaterialContent(values){
	return requestJson(`${ServerRoot}/aianalysis/materials/extract`, values, {
		timeoutMs: resolveRequestTimeout(values),
	});
}

export function requestEmbeddingVectors(values){
	return requestJson(`${ServerRoot}/aianalysis/embeddings`, values, {
		timeoutMs: resolveRequestTimeout(values),
	});
}

export function requestAIAnalysisChat(values){
	return requestJson(`${ServerRoot}/aianalysis/chat`, values, {
		timeoutMs: resolveRequestTimeout(values),
	});
}

export async function requestAIAnalysisChatStream(values, handlers = {}){
	const response = await withTimeout(async (signal)=>{
		const bodyText = JSON.stringify(values || {});
		const rsp = await fetch(`${ServerRoot}/aianalysis/chat/stream`, {
			method: 'POST',
			cache: 'no-store',
			headers: buildAIAnalysisHeaders(bodyText),
			body: bodyText,
			signal,
		});
		if(!rsp.ok){
			const text = await rsp.text();
			const payload = safeParseJson(text, null);
			const errorText = payload && (payload.ResultMessage || payload.Result || payload.message)
				? (payload.ResultMessage || payload.Result || payload.message)
				: `${rsp.status} ${rsp.statusText || ''}`.trim();
			throw new Error(errorText || 'chat.stream.failed');
		}
		return rsp;
	}, handlers.timeoutMs || resolveRequestTimeout(values), handlers.signal);
	const reader = response.body && response.body.getReader ? response.body.getReader() : null;
	if(!reader){
		throw new Error('chat.stream.not.supported');
	}
	const decoder = new TextDecoder('utf-8');
	const parser = createSseParser((event)=>{
		if(handlers.onEvent){
			handlers.onEvent(event);
		}
	});
	try{
		while(true){
			const chunk = await reader.read();
			if(chunk.done){
				break;
			}
			parser.push(decoder.decode(chunk.value, { stream: true }));
		}
		parser.end();
		if(handlers.onDone){
			handlers.onDone();
		}
	}catch(e){
		try{ parser.end(); }catch(_){ /* flush buffered SSE (e.g. a final error event) before propagating */ }
		if(handlers.onError){
			handlers.onError(e);
		}
		throw e;
	}
}
