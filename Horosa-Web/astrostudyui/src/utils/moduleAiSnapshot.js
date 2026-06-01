const MODULE_SNAPSHOT_PREFIX = 'horosa.ai.snapshot.module.v1.';
const MODULE_SNAPSHOT_MEMORY = new Map();
const MODULE_SNAPSHOT_GLOBAL_KEY = '__horosa_module_ai_snapshot_map';

function snapshotKey(moduleName){
	return `${MODULE_SNAPSHOT_PREFIX}${moduleName}`;
}

function getGlobalSnapshotMap(){
	try{
		if(typeof window === 'undefined'){
			return null;
		}
		if(!window[MODULE_SNAPSHOT_GLOBAL_KEY] || typeof window[MODULE_SNAPSHOT_GLOBAL_KEY] !== 'object'){
			window[MODULE_SNAPSHOT_GLOBAL_KEY] = {};
		}
		return window[MODULE_SNAPSHOT_GLOBAL_KEY];
	}catch(e){
		return null;
	}
}

function saveToMemoryAndGlobal(moduleName, payload){
	if(!moduleName || !payload || !payload.content){
		return;
	}
	MODULE_SNAPSHOT_MEMORY.set(moduleName, payload);
	const globalMap = getGlobalSnapshotMap();
	if(globalMap){
		globalMap[moduleName] = payload;
	}
}

function loadFromMemoryAndGlobal(moduleName){
	const mem = MODULE_SNAPSHOT_MEMORY.get(moduleName);
	if(mem && mem.content){
		return mem;
	}
	const globalMap = getGlobalSnapshotMap();
	if(globalMap && globalMap[moduleName] && globalMap[moduleName].content){
		const payload = globalMap[moduleName];
		MODULE_SNAPSHOT_MEMORY.set(moduleName, payload);
		return payload;
	}
	return null;
}

export function saveModuleAISnapshot(moduleName, content, meta){
	try{
		if(!moduleName){
			return null;
		}
		const text = (content || '').trim();
		if(!text){
			return null;
		}
		const payload = {
			module: moduleName,
			version: 1,
			createdAt: new Date().toISOString(),
			meta: meta || {},
			content: text,
		};
		saveToMemoryAndGlobal(moduleName, payload);
		if(typeof window !== 'undefined' && window.localStorage){
			window.localStorage.setItem(snapshotKey(moduleName), JSON.stringify(payload));
		}
		return payload;
	}catch(e){
		// localStorage 写入失败时，仍保留本次会话内快照，保证 AI 导出可用。
		try{
			if(moduleName && content){
				const text = `${content}`.trim();
				if(text){
					const payload = {
						module: moduleName,
						version: 1,
						createdAt: new Date().toISOString(),
						meta: meta || {},
						content: text,
					};
					saveToMemoryAndGlobal(moduleName, payload);
					return payload;
				}
			}
		}catch(inner){
			// ignore
		}
		return null;
	}
}

export function loadModuleAISnapshot(moduleName){
	try{
		if(!moduleName){
			return null;
		}
		if(typeof window !== 'undefined' && window.localStorage){
			const raw = window.localStorage.getItem(snapshotKey(moduleName));
			if(raw){
				try{
					const data = JSON.parse(raw);
					if(data && data.content){
						saveToMemoryAndGlobal(moduleName, data);
						return data;
					}
				}catch(parseErr){
					// 兼容旧版本：localStorage 里可能直接保存纯文本而非 JSON。
					const txt = `${raw}`.trim();
					if(txt){
						const legacy = {
							module: moduleName,
							version: 1,
							createdAt: '',
							meta: {},
							content: txt,
						};
						saveToMemoryAndGlobal(moduleName, legacy);
						return legacy;
					}
				}
			}
		}
		return loadFromMemoryAndGlobal(moduleName);
	}catch(e){
		return loadFromMemoryAndGlobal(moduleName);
	}
}
