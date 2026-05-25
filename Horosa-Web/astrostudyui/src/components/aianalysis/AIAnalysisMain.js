import React from 'react';
import {
	Checkbox,
	Collapse,
	Empty,
	Form,
	Popconfirm,
	Space,
	Spin,
	Table,
	Tag,
	Tooltip,
	Typography,
	Upload,
	message,
} from 'antd';
import Mustache from 'mustache';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import styles from './AIAnalysisMain.less';
import MonacoEditor from './MonacoField';
import XQIcon from '../xq-icons';
import {
	XQButton as Button,
	XQCard as Card,
	XQDrawer as Drawer,
	XQInput as Input,
	XQModal as Modal,
	XQSelect as Select,
	XQSwitch as Switch,
	XQTabs as Tabs,
} from '../xq-ui';
import {
	AI_ANALYSIS_SCHEMA_VERSION,
	AI_ANALYSIS_STORES,
	buildMaterialSearchText,
	buildTimestampLabel,
	bulkPutStoreRecords,
	deleteStoreRecord,
	deleteWhere,
	ensureTemplateVersion,
	getStoreRecord,
	listConversationMessages,
	listStoreRecords,
	loadUiPrefs,
	migrateWorkspaceData,
	putStoreRecord,
	replaceConversationMessages,
	saveConversationMessage,
	saveUiPrefs,
} from '../../utils/aiAnalysisStore';
import {
	buildContextLayers,
	buildPromptContext,
	clipContextLayers,
	getAnalysisSourceContext,
	getAnalysisTechniqueContexts,
	listAnalysisSources,
	listAnalysisTechniqueOptions,
} from '../../utils/aiAnalysisContext';
import { parseMaterialFile } from '../../utils/aiAnalysisMaterial';
import {
	diagnoseProvider,
	fetchProviderModels,
	requestAIAnalysisChat,
	requestAIAnalysisChatStream,
	requestEmbeddingVectors,
} from '../../services/aianalysis';
import {
	base64ToBlob,
	blobToBase64,
	downloadTextFile,
	exportConversationBundle,
	exportConversationByFormat,
	exportWorkspaceBackupBlob,
	parseWorkspaceBackupBlob,
	saveBlobToBrowser,
} from '../../utils/aiAnalysisExport';
import {
	buildRetrievedContextText,
	ensureMaterialChunks,
	mergeRetrievedChunks,
	rankChunksByKeyword,
	rerankChunksWithVector,
	shouldUseDirectAttach,
} from '../../utils/aiAnalysisRag';
import {
	filterTechniqueKeysBySource,
	getTechniqueContextMode,
} from '../../utils/aiAnalysisSelection';
import {
	isDesktopBridgeAvailable,
	openDesktopBackup,
	pickDesktopFiles,
	pickDesktopFolder,
	saveDesktopFile,
} from '../../utils/aiAnalysisDesktop';
import {
	PROVIDER_OPTIONS,
	getProviderDefaultChatModels,
	getProviderDefaultEmbeddingModels,
	getProviderDisplayName,
	getProviderPreset,
	getProviderProtocolFamily,
	splitProviderModels,
} from '../../utils/aiAnalysisProviders';

const { TextArea, Search } = Input;
const { Title, Text } = Typography;
const { Dragger } = Upload;
const { TabPane } = Tabs;

const SECONDARY_TABS = [
	{ key: 'analysis', label: '分析', icon: <XQIcon name="ai" /> },
	{ key: 'history', label: '历史', icon: <XQIcon name="calendar" /> },
	{ key: 'materials', label: '资料', icon: <XQIcon name="book" /> },
	{ key: 'templates', label: '模版', icon: <XQIcon name="note" /> },
	{ key: 'settings', label: '设置', icon: <XQIcon name="aiSettings" /> },
];

const RETRIEVAL_OPTIONS = [
	{ value: 'auto', label: '自动（推荐）' },
	{ value: 'fulltext', label: '全文优先' },
	{ value: 'rag', label: '检索优先' },
];

const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);

const COMMON_PROVIDER_OPTION_KEYS = ['extraHeaders', 'extraBody', 'apiVersion', 'requestTimeoutMs'];
const PROVIDER_OPTION_KEY_MAP = {
	openai: [],
	openrouter: [],
	custom: [],
	anthropic: ['max_tokens', 'thinking', 'top_p', 'top_k'],
	gemini: ['generationConfig', 'safetySettings'],
	ollama: ['keep_alive', 'num_ctx', 'num_predict', 'top_k', 'top_p', 'repeat_penalty'],
};

function uniqueTextList(list){
	const found = new Set();
	const result = [];
	(list || []).forEach((item)=>{
		const txt = `${item || ''}`.trim();
		if(!txt || found.has(txt)){
			return;
		}
		found.add(txt);
		result.push(txt);
	});
	return result;
}

function safeParseJson(text, defVal = null){
	if(!text){
		return defVal;
	}
	try{
		return JSON.parse(text);
	}catch(e){
		return defVal;
	}
}

function ensureServiceResponse(rsp, messageText = 'service.response.empty'){
	if(!rsp){
		throw new Error(messageText);
	}
	if(rsp.ResultCode !== undefined && rsp.ResultCode !== null && Number(rsp.ResultCode) !== 0){
		throw new Error(rsp.ResultMessage || messageText);
	}
	return rsp;
}

function parseJsonTextAsObject(text, fieldLabel){
	const raw = `${text || ''}`.trim();
	if(!raw){
		return {};
	}
	const parsed = safeParseJson(raw, null);
	if(!parsed || typeof parsed !== 'object' || Array.isArray(parsed)){
		throw new Error(`${fieldLabel} 需要是 JSON 对象`);
	}
	return parsed;
}

function parseJsonTextAsArray(text, fieldLabel){
	const raw = `${text || ''}`.trim();
	if(!raw){
		return [];
	}
	const parsed = safeParseJson(raw, null);
	if(!Array.isArray(parsed)){
		throw new Error(`${fieldLabel} 需要是 JSON 数组`);
	}
	return parsed;
}

function parseNumberText(value, fieldLabel, options = {}){
	const raw = `${value === undefined || value === null ? '' : value}`.trim();
	if(!raw){
		return null;
	}
	const num = options.integer ? Number.parseInt(raw, 10) : Number(raw);
	if(!Number.isFinite(num)){
		throw new Error(`${fieldLabel} 需要是有效数字`);
	}
	return num;
}

function joinModelLines(models){
	return uniqueTextList(models || []).join('\n');
}

function normalizeProviderResultModels(result, providerType, usePresetFallback = true){
	const splitResult = splitProviderModels(
		[]
			.concat(result && Array.isArray(result.chatModels) ? result.chatModels : [])
			.concat(result && Array.isArray(result.embeddingModels) ? result.embeddingModels : [])
			.concat(result && Array.isArray(result.models) ? result.models : []),
		providerType,
	);
	return {
		models: splitResult.models,
		chatModels: splitResult.chatModels.length ? splitResult.chatModels : (usePresetFallback ? getProviderDefaultChatModels(providerType) : []),
		embeddingModels: splitResult.embeddingModels.length ? splitResult.embeddingModels : (usePresetFallback ? getProviderDefaultEmbeddingModels(providerType) : []),
	};
}

function pickCustomProviderOptions(providerType, providerOptions){
	const reserved = new Set(COMMON_PROVIDER_OPTION_KEYS.concat(PROVIDER_OPTION_KEY_MAP[providerType] || []));
	const result = {};
	Object.keys(providerOptions || {}).forEach((key)=>{
		if(!reserved.has(key)){
			result[key] = providerOptions[key];
		}
	});
	return result;
}

function buildProviderFormValues(profile){
	const providerType = profile ? profile.providerType : 'openai';
	const preset = getProviderPreset(providerType);
	const providerOptions = profile && profile.providerOptions ? profile.providerOptions : {};
	const manualModels = profile ? normalizeProfileModels(profile) : getProviderDefaultChatModels(providerType);
	const embeddingModels = profile ? normalizeEmbeddingModels(profile) : getProviderDefaultEmbeddingModels(providerType);
	return {
		name: profile ? profile.name : preset.label,
		providerType,
		apiKey: profile ? profile.apiKey : '',
		baseUrl: profile ? profile.baseUrl : preset.baseUrl,
		manualModels: joinModelLines(manualModels),
		embeddingModels: joinModelLines(embeddingModels),
		extraHeadersText: JSON.stringify(providerOptions.extraHeaders || {}, null, 2),
		extraBodyText: JSON.stringify(providerOptions.extraBody || {}, null, 2),
		requestTimeoutMs: providerOptions.requestTimeoutMs || preset.requestTimeoutMs || 120000,
		anthropicApiVersion: providerOptions.apiVersion || preset.anthropicApiVersion || '2023-06-01',
		anthropicMaxTokens: providerOptions.max_tokens || preset.anthropicMaxTokens || '2048',
		anthropicThinkingBudget: providerOptions.thinking && providerOptions.thinking.budget_tokens ? providerOptions.thinking.budget_tokens : '',
		anthropicTopP: providerOptions.top_p || '',
		anthropicTopK: providerOptions.top_k || '',
		geminiGenerationConfigText: JSON.stringify(providerOptions.generationConfig || {}, null, 2),
		geminiSafetySettingsText: JSON.stringify(providerOptions.safetySettings || [], null, 2),
		ollamaKeepAlive: providerOptions.keep_alive || preset.ollamaKeepAlive || '5m',
		ollamaNumCtx: providerOptions.num_ctx || preset.ollamaNumCtx || '8192',
		ollamaNumPredict: providerOptions.num_predict || preset.ollamaNumPredict || '1024',
		ollamaTopK: providerOptions.top_k || preset.ollamaTopK || '40',
		ollamaTopP: providerOptions.top_p || preset.ollamaTopP || '0.9',
		ollamaRepeatPenalty: providerOptions.repeat_penalty || preset.ollamaRepeatPenalty || '1.1',
		providerOptionsText: JSON.stringify(pickCustomProviderOptions(providerType, providerOptions), null, 2),
		enabled: profile ? profile.enabled !== false : true,
	};
}

function buildProviderOptionsFromForm(values){
	const providerType = values.providerType || 'openai';
	const providerOptions = parseJsonTextAsObject(values.providerOptionsText, '补充高级参数');
	const extraHeaders = parseJsonTextAsObject(values.extraHeadersText, '额外请求头');
	const extraBody = parseJsonTextAsObject(values.extraBodyText, '额外请求体');
	const requestTimeoutMs = parseNumberText(values.requestTimeoutMs, '请求超时', { integer: true });
	if(Object.keys(extraHeaders).length){
		providerOptions.extraHeaders = extraHeaders;
	}
	if(Object.keys(extraBody).length){
		providerOptions.extraBody = extraBody;
	}
	if(requestTimeoutMs){
		providerOptions.requestTimeoutMs = requestTimeoutMs;
	}
	if(providerType === 'anthropic'){
		const maxTokens = parseNumberText(values.anthropicMaxTokens, 'Anthropic max tokens', { integer: true });
		const thinkingBudget = parseNumberText(values.anthropicThinkingBudget, 'Anthropic thinking budget', { integer: true });
		const topP = parseNumberText(values.anthropicTopP, 'Anthropic top_p');
		const topK = parseNumberText(values.anthropicTopK, 'Anthropic top_k', { integer: true });
		if(values.anthropicApiVersion){
			providerOptions.apiVersion = `${values.anthropicApiVersion}`.trim();
		}
		if(maxTokens){
			providerOptions.max_tokens = maxTokens;
		}
		if(thinkingBudget){
			providerOptions.thinking = {
				type: 'enabled',
				budget_tokens: thinkingBudget,
			};
		}
		if(topP !== null){
			providerOptions.top_p = topP;
		}
		if(topK !== null){
			providerOptions.top_k = topK;
		}
	}
	if(providerType === 'gemini'){
		const generationConfig = parseJsonTextAsObject(values.geminiGenerationConfigText, 'Gemini generation config');
		const safetySettings = parseJsonTextAsArray(values.geminiSafetySettingsText, 'Gemini safety settings');
		if(Object.keys(generationConfig).length){
			providerOptions.generationConfig = generationConfig;
		}
		if(safetySettings.length){
			providerOptions.safetySettings = safetySettings;
		}
	}
	if(providerType === 'ollama'){
		const numCtx = parseNumberText(values.ollamaNumCtx, 'Ollama num_ctx', { integer: true });
		const numPredict = parseNumberText(values.ollamaNumPredict, 'Ollama num_predict', { integer: true });
		const topK = parseNumberText(values.ollamaTopK, 'Ollama top_k', { integer: true });
		const topP = parseNumberText(values.ollamaTopP, 'Ollama top_p');
		const repeatPenalty = parseNumberText(values.ollamaRepeatPenalty, 'Ollama repeat_penalty');
		if(values.ollamaKeepAlive){
			providerOptions.keep_alive = `${values.ollamaKeepAlive}`.trim();
		}
		if(numCtx !== null){
			providerOptions.num_ctx = numCtx;
		}
		if(numPredict !== null){
			providerOptions.num_predict = numPredict;
		}
		if(topK !== null){
			providerOptions.top_k = topK;
		}
		if(topP !== null){
			providerOptions.top_p = topP;
		}
		if(repeatPenalty !== null){
			providerOptions.repeat_penalty = repeatPenalty;
		}
	}
	return providerOptions;
}

function normalizeTags(value){
	if(Array.isArray(value)){
		return uniqueTextList(value);
	}
	const raw = `${value || ''}`.trim();
	if(!raw){
		return [];
	}
	return uniqueTextList(raw.split(/[,，\n]/g));
}

function normalizeProfileModels(profile){
	if(!profile){
		return [];
	}
	return uniqueTextList([]
		.concat(profile.chatModelIds || [])
		.concat(profile.availableModels || [])
		.concat(profile.manualModels || []));
}

function normalizeEmbeddingModels(profile){
	if(!profile){
		return [];
	}
	return uniqueTextList(profile.embeddingModelIds || []);
}

function parseModelSelection(selection){
	const text = `${selection || ''}`;
	const idx = text.indexOf('::');
	if(idx < 0){
		return {
			profileId: '',
			model: text,
		};
	}
	return {
		profileId: text.slice(0, idx),
		model: text.slice(idx + 2),
	};
}

function encodeModelSelection(profileId, model){
	return `${profileId || ''}::${model || ''}`;
}

function sortByUpdatedDesc(list){
	return (list || []).slice(0).sort((a, b)=>{
		const ta = Date.parse(a.updatedAt || a.createdAt || '') || 0;
		const tb = Date.parse(b.updatedAt || b.createdAt || '') || 0;
		return tb - ta;
	});
}

function compareByName(list){
	return (list || []).slice(0).sort((a, b)=>`${a.name || ''}`.localeCompare(`${b.name || ''}`, 'zh-Hans-CN'));
}

function buildConversationTitle(prompt, source){
	const trimmed = `${prompt || ''}`.trim();
	if(source && source.title){
		if(!trimmed){
			return `${source.title} 分析`;
		}
		return `${source.title} · ${trimmed.slice(0, 24)}`;
	}
	return trimmed ? trimmed.slice(0, 24) : '未命名对话';
}

function resolveReferenceItems(referenceIds, materials, bundles, templates){
	const refs = Array.isArray(referenceIds) ? referenceIds : [];
	const bundleItems = [];
	const materialItems = [];
	const templateItems = [];
	refs.forEach((id)=>{
		const text = `${id || ''}`;
		if(text.indexOf('bundle:') === 0){
			const bundle = bundles.find((item)=>item.id === text.replace('bundle:', ''));
			if(bundle){
				bundleItems.push(bundle);
				if(bundle.templateId){
					const template = templates.find((item)=>item.id === bundle.templateId);
					if(template){
						templateItems.push(template);
					}
				}
			}
			return;
		}
		if(text.indexOf('material:') === 0){
			const material = materials.find((item)=>item.id === text.replace('material:', ''));
			if(material){
				materialItems.push(material);
			}
		}
	});
	const bundleMaterialIds = bundleItems.flatMap((bundle)=>bundle.defaultMaterialIds && bundle.defaultMaterialIds.length ? bundle.defaultMaterialIds : (bundle.materialIds || []));
	const bundleMaterials = bundleMaterialIds.map((id)=>materials.find((item)=>item.id === id)).filter(Boolean);
	return {
		bundles: bundleItems,
		materials: uniqueById(materialItems.concat(bundleMaterials)),
		templates: uniqueById(templateItems),
		systemPrompt: bundleItems.map((bundle)=>bundle.defaultSystemPrompt || '').filter(Boolean).join('\n\n'),
	};
}

function uniqueById(list){
	const seen = new Set();
	return (list || []).filter((item)=>{
		if(!item || !item.id || seen.has(item.id)){
			return false;
		}
		seen.add(item.id);
		return true;
	});
}

function buildTemplatePreview(template){
	const sampleData = safeParseJson(template.exampleInput, {
		user_prompt: '请分析此案例',
		source_context: '这是案例前提',
		retrieved_context: '这是检索到的资料片段',
		conversation_history: '[user] 上一句问题',
		system_prompt: '系统提示',
	});
	if(template.format === 'json'){
		const schema = safeParseJson(template.jsonSchema, null);
		const output = safeParseJson(template.exampleOutput, null);
		let schemaErrors = [];
		if(schema){
			try{
				const validate = ajv.compile(schema);
				if(output){
					validate(output);
				}
				schemaErrors = validate.errors || [];
			}catch(e){
				schemaErrors = [{ message: e.message }];
			}
		}else{
			schemaErrors = [{ message: 'JSON Schema 解析失败' }];
		}
		return {
			text: JSON.stringify(output || sampleData, null, 2),
			errors: schemaErrors,
		};
	}
	const rendered = Mustache.render(template.instructionText || template.content || '', sampleData);
	return {
		text: rendered,
		errors: [],
	};
}

function buildTemplateVersionSnapshot(values){
	return {
		format: values.format,
		instructionText: values.instructionText || '',
		jsonSchema: values.jsonSchema || '',
		exampleInput: values.exampleInput || '',
		exampleOutput: values.exampleOutput || '',
		content: values.format === 'text' ? (values.instructionText || '') : (values.jsonSchema || ''),
		name: values.name || '',
	};
}

function configureMonaco(monaco){
	if(monaco && monaco.languages && monaco.languages.json){
		monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
			validate: true,
			allowComments: false,
			schemas: [
				{
					uri: 'horosa://json-template-schema.json',
					fileMatch: ['*'],
					schema: {
						type: 'object',
						properties: {
							type: { type: 'string' },
							properties: { type: 'object' },
							required: {
								type: 'array',
								items: { type: 'string' },
							},
							additionalProperties: { type: 'boolean' },
						},
					},
				},
			],
		});
	}
}

marked.setOptions({
	gfm: true,
	breaks: true,
	headerIds: false,
	mangle: false,
});

// 把 AI 输出的 Markdown 渲染为安全 HTML（GFM：标题/列表/表格/代码/引用/链接），再交给气泡渲染。
function renderMarkdownToHtml(text){
	const raw = `${text || ''}`;
	if(!raw.trim()){
		return '';
	}
	try{
		const html = marked.parse(raw);
		return DOMPurify.sanitize(html, { ADD_ATTR: ['target', 'rel'] });
	}catch(e){
		return '';
	}
}

const CONTEXT_STATUS_META = {
	ready: { text: '已就绪', color: 'green' },
	regenerated: { text: '已按盘重算', color: 'blue' },
	missing: { text: '缺失', color: 'red' },
	pending: { text: '待生成', color: 'default' },
};

function getContextStatusMeta(status){
	return CONTEXT_STATUS_META[status] || CONTEXT_STATUS_META.pending;
}

// 从挂载层的 meta 里提取出生/起盘签名，方便核对「挂的是不是这张盘」。
function buildContextSignatureText(meta){
	if(!meta || typeof meta !== 'object'){
		return '';
	}
	const date = `${meta.date || meta.birth || meta.divTime || ''}`.trim();
	const zone = `${meta.zone || ''}`.trim();
	const parts = [];
	if(date){
		parts.push(date);
	}
	if(zone){
		parts.push(zone);
	}
	return parts.join(' · ');
}

function shallowEqualObject(a, b){
	if(a === b){
		return true;
	}
	const left = a && typeof a === 'object' ? a : {};
	const right = b && typeof b === 'object' ? b : {};
	const leftKeys = Object.keys(left);
	const rightKeys = Object.keys(right);
	if(leftKeys.length !== rightKeys.length){
		return false;
	}
	for(let i = 0; i < leftKeys.length; i += 1){
		const key = leftKeys[i];
		if(left[key] !== right[key]){
			return false;
		}
	}
	return true;
}

function sameSourceContext(left, right){
	if(left === right){
		return true;
	}
	if(!left || !right){
		return false;
	}
	return left.content === right.content
		&& left.title === right.title
		&& left.module === right.module
		&& shallowEqualObject(left.meta, right.meta);
}

function buildTechniqueLoadingState(keys, labelMap){
	return (keys || []).map((key)=>({
		key,
		title: labelMap.get(key) || key,
		module: key,
		content: '',
		available: false,
		status: 'loading',
		meta: {},
	}));
}

function mergeTechniqueState(list, nextItem, keys, labelMap){
	const currentMap = new Map((list || []).map((item)=>[item.key, item]));
	if(nextItem && nextItem.key){
		currentMap.set(nextItem.key, nextItem);
	}
	return (keys || []).map((key)=>{
		if(currentMap.has(key)){
			return currentMap.get(key);
		}
		return {
			key,
			title: labelMap.get(key) || key,
			module: key,
			content: '',
			available: false,
			status: 'loading',
			meta: {},
		};
	});
}

function AIAnalysisMain(props){
	const defaultUi = loadUiPrefs();
	const [innerTab, setInnerTab] = React.useState('analysis');
	const [workspaceLoading, setWorkspaceLoading] = React.useState(false);
	const [sending, setSending] = React.useState(false);
	const [sources, setSources] = React.useState([]);
	const [providerProfiles, setProviderProfiles] = React.useState([]);
	const [materials, setMaterials] = React.useState([]);
	const [materialFolders, setMaterialFolders] = React.useState([]);
	const [tagGroups, setTagGroups] = React.useState([]);
	const [templateVersions, setTemplateVersions] = React.useState([]);
	const [templates, setTemplates] = React.useState([]);
	const [bundles, setBundles] = React.useState([]);
	const [conversations, setConversations] = React.useState([]);
	const [activeConversationId, setActiveConversationId] = React.useState('');
	const [messages, setMessages] = React.useState([]);
	const [selectedSourceId, setSelectedSourceId] = React.useState('');
	const [modelSelection, setModelSelection] = React.useState(defaultUi.modelSelection || '');
	const [referenceIds, setReferenceIds] = React.useState(defaultUi.referenceIds || []);
	const [sourceContext, setSourceContext] = React.useState(null);
	const [selectedTechniqueKeys, setSelectedTechniqueKeys] = React.useState(defaultUi.selectedTechniqueKeys || []);
	const [techniqueContexts, setTechniqueContexts] = React.useState([]);
	const [prompt, setPrompt] = React.useState('');
	const [sessionSystemPrompt, setSessionSystemPrompt] = React.useState(defaultUi.sessionSystemPrompt || '');
	const [historyKeyword, setHistoryKeyword] = React.useState('');
	const [historyFilter, setHistoryFilter] = React.useState({
		provider: '',
		model: '',
		sourceType: '',
		favorite: 'all',
		archived: 'active',
	});
	const [selectedHistoryIds, setSelectedHistoryIds] = React.useState([]);
	const [materialKeyword, setMaterialKeyword] = React.useState('');
	const [selectedFolderId, setSelectedFolderId] = React.useState('');
	const [materialSort, setMaterialSort] = React.useState('updated');
	const [templateKeyword, setTemplateKeyword] = React.useState('');
	const [settingKeyword, setSettingKeyword] = React.useState('');
	const [materialModalOpen, setMaterialModalOpen] = React.useState(false);
	const [templateModalOpen, setTemplateModalOpen] = React.useState(false);
	const [bundleModalOpen, setBundleModalOpen] = React.useState(false);
	const [providerModalOpen, setProviderModalOpen] = React.useState(false);
	const [providerSwitchModalOpen, setProviderSwitchModalOpen] = React.useState(false);
	const [providerAdvancedOpen, setProviderAdvancedOpen] = React.useState(false);
	const [previewDrawerOpen, setPreviewDrawerOpen] = React.useState(false);
	const [previewTemplate, setPreviewTemplate] = React.useState(null);
	const [editingMaterial, setEditingMaterial] = React.useState(null);
	const [editingTemplate, setEditingTemplate] = React.useState(null);
	const [editingBundle, setEditingBundle] = React.useState(null);
	const [editingProvider, setEditingProvider] = React.useState(null);
	const [materialForm] = Form.useForm();
	const [templateForm] = Form.useForm();
	const [bundleForm] = Form.useForm();
	const [providerForm] = Form.useForm();
	const abortRef = React.useRef(null);
	const streamBufferRef = React.useRef('');
	const backupRestoreInputRef = React.useRef(null);
	const desktopFileInputRef = React.useRef(null);
	const desktopFolderInputRef = React.useRef(null);

	const height = props.height ? props.height - 18 : (typeof document !== 'undefined' ? document.documentElement.clientHeight - 100 : 620);
	const desktopBridge = isDesktopBridgeAvailable();

	const activeConversation = React.useMemo(()=>{
		return conversations.find((item)=>item.id === activeConversationId) || null;
	}, [conversations, activeConversationId]);

	const activeSource = React.useMemo(()=>{
		return sources.find((item)=>item.id === selectedSourceId) || null;
	}, [sources, selectedSourceId]);

	const sourceOptions = React.useMemo(()=>{
		return sources.map((item)=>({
			value: item.id,
			label: `${item.sourceType === 'chart' ? '命盘' : '事盘'} · ${item.title}`,
			searchText: `${item.title} ${item.module || ''} ${(item.tags || []).join(' ')}`.toLowerCase(),
			item,
		}));
	}, [sources]);

	const techniqueOptions = React.useMemo(()=>{
		return activeSource ? listAnalysisTechniqueOptions(activeSource) : [];
	}, [activeSource]);
	const techniqueLabelMap = React.useMemo(()=>{
		return new Map((techniqueOptions || []).map((item)=>[item.value, item.label]));
	}, [techniqueOptions]);
	const activeTechniqueKeys = React.useMemo(()=>{
		return filterTechniqueKeysBySource(activeSource, techniqueOptions, selectedTechniqueKeys);
	}, [activeSource, techniqueOptions, selectedTechniqueKeys]);
	const sourceContextMode = getTechniqueContextMode(activeTechniqueKeys);

	const modelOptions = React.useMemo(()=>{
		const result = [];
		providerProfiles.forEach((profile)=>{
			if(profile.enabled === false){
				return;
			}
			normalizeProfileModels(profile).forEach((model)=>{
				result.push({
					value: encodeModelSelection(profile.id, model),
					label: `${profile.name || '未命名配置'} / ${model}`,
				});
			});
		});
		return result;
	}, [providerProfiles]);

	const activeProviderProfile = React.useMemo(()=>{
		const parsed = parseModelSelection(modelSelection);
		if(parsed.profileId){
			const selectedProfile = providerProfiles.find((item)=>item.id === parsed.profileId && item.enabled !== false);
			if(selectedProfile){
				return selectedProfile;
			}
		}
		return providerProfiles.find((item)=>item.enabled !== false) || null;
	}, [modelSelection, providerProfiles]);

	const referenceOptions = React.useMemo(()=>{
		const folderLookup = new Map(materialFolders.map((item)=>[item.id, item]));
		const bundleOptions = bundles.map((item)=>({
			value: `bundle:${item.id}`,
			label: `组合 · ${item.name}`,
		}));
		const materialOptions = materials.map((item)=>({
			value: `material:${item.id}`,
			label: `资料 · ${item.name}${item.folderId && folderLookup.get(item.folderId) ? ` / ${folderLookup.get(item.folderId).name}` : ''}`,
		}));
		return bundleOptions.concat(materialOptions);
	}, [materials, bundles, materialFolders]);

	const visibleMessages = React.useMemo(()=>{
		return (messages || []).filter((item)=>item && item.role !== 'system_hidden');
	}, [messages]);

	const filteredConversations = React.useMemo(()=>{
		const keyword = `${historyKeyword || ''}`.trim().toLowerCase();
		return sortByUpdatedDesc(conversations).filter((item)=>{
			if(item.archived && historyFilter.archived === 'active'){
				return false;
			}
			if(!item.archived && historyFilter.archived === 'archived'){
				return false;
			}
			if(historyFilter.favorite !== 'all'){
				const expectFavorite = historyFilter.favorite === 'favorite';
				if(Boolean(item.favorite) !== expectFavorite){
					return false;
				}
			}
			if(historyFilter.provider && `${item.providerName || item.providerType || ''}` !== historyFilter.provider){
				return false;
			}
			if(historyFilter.model && `${item.model || ''}` !== historyFilter.model){
				return false;
			}
			if(historyFilter.sourceType && `${item.sourceRef && item.sourceRef.sourceType ? item.sourceRef.sourceType : ''}` !== historyFilter.sourceType){
				return false;
			}
			if(!keyword){
				return true;
			}
			const text = [
				item.title,
				item.model,
				item.providerName,
				item.providerType,
				item.sourceRef && item.sourceRef.title,
			].join(' ').toLowerCase();
			return text.indexOf(keyword) >= 0;
		});
	}, [conversations, historyKeyword, historyFilter]);

	const filteredMaterials = React.useMemo(()=>{
		const keyword = `${materialKeyword || ''}`.trim().toLowerCase();
		let list = materials.filter((item)=>{
			if(selectedFolderId && item.folderId !== selectedFolderId){
				return false;
			}
			if(!keyword){
				return true;
			}
			return buildMaterialSearchText(item).indexOf(keyword) >= 0;
		});
		if(materialSort === 'name'){
			list = compareByName(list);
		}else if(materialSort === 'size'){
			list = list.slice(0).sort((a, b)=>(b.size || 0) - (a.size || 0));
		}else{
			list = sortByUpdatedDesc(list);
		}
		return list;
	}, [materials, materialKeyword, selectedFolderId, materialSort]);

	const filteredTemplates = React.useMemo(()=>{
		const keyword = `${templateKeyword || ''}`.trim().toLowerCase();
		const allCards = sortByUpdatedDesc(templates).map((item)=>({
			...item,
			cardType: 'template',
		})).concat(sortByUpdatedDesc(bundles).map((item)=>({
			...item,
			cardType: 'bundle',
		})));
		if(!keyword){
			return allCards;
		}
		return allCards.filter((item)=>{
			const text = [
				item.name,
				item.instructionText,
				item.jsonSchema,
				item.defaultSystemPrompt,
			].join(' ').toLowerCase();
			return text.indexOf(keyword) >= 0;
		});
	}, [templates, bundles, templateKeyword]);

	const filteredProfiles = React.useMemo(()=>{
		const keyword = `${settingKeyword || ''}`.trim().toLowerCase();
		const list = sortByUpdatedDesc(providerProfiles);
		if(!keyword){
			return list;
		}
		return list.filter((item)=>{
			const text = [
				item.name,
				item.providerType,
				normalizeProfileModels(item).join(' '),
				normalizeEmbeddingModels(item).join(' '),
				item.baseUrl,
				JSON.stringify(item.providerOptions || {}),
			].join(' ').toLowerCase();
			return text.indexOf(keyword) >= 0;
		});
	}, [providerProfiles, settingKeyword]);

	const lockedContextItems = React.useMemo(()=>{
		const resolved = resolveReferenceItems(referenceIds, materials, bundles, templates);
		const items = [];
		if(activeSource){
			items.push({
				key: `source:${activeSource.id}`,
				title: `案例前提 · ${activeSource.title}`,
				type: activeSource.sourceType === 'chart' ? '命盘' : '事盘',
				content: sourceContext && sourceContext.content ? sourceContext.content : '',
				meta: sourceContext && sourceContext.meta ? sourceContext.meta : null,
				status: sourceContext && sourceContext.content ? 'ready' : 'pending',
				emptyHint: '将自动读取案例快照',
			});
		}
		if(sessionSystemPrompt){
			items.push({
				key: 'session-system-prompt',
				title: '本轮系统提示',
				type: 'system',
				content: sessionSystemPrompt,
				status: 'ready',
			});
		}
		(techniqueContexts || []).forEach((item)=>{
			items.push({
				key: `technique:${item.key}`,
				title: `技法 · ${item.title || item.key}`,
				type: 'technique',
				content: item.content || '',
				meta: item.meta || null,
				status: item.status || (item.content ? 'ready' : 'missing'),
				emptyHint: item.status === 'missing'
					? '当前未找到该技法可用快照，未挂载该技法内容。'
					: '正在按已存案例/命盘数据自动补生成快照。',
			});
		});
		resolved.materials.forEach((item)=>{
			items.push({
				key: `material:${item.id}`,
				title: `资料 · ${item.name}`,
				type: item.kind || 'note',
				content: item.extractedText || '',
				status: item.extractedText ? 'ready' : 'pending',
			});
		});
		resolved.templates.forEach((item)=>{
			items.push({
				key: `template:${item.id}`,
				title: `模版 · ${item.name}`,
				type: item.format || 'text',
				content: item.instructionText || item.jsonSchema || item.content || '',
				status: 'ready',
			});
		});
		return items;
	}, [referenceIds, materials, bundles, templates, activeSource, sourceContext, sessionSystemPrompt, techniqueContexts]);

	// 挂载面板：新出现的层默认展开（否则新加技法时面板看起来是空的）；用户手动收起的保持收起。
	const [contextActiveKeys, setContextActiveKeys] = React.useState([]);
	const seenContextKeysRef = React.useRef(new Set());
	React.useEffect(()=>{
		const keys = lockedContextItems.map((item)=>item.key);
		setContextActiveKeys((prev)=>{
			const next = new Set(prev.filter((k)=>keys.includes(k)));
			keys.forEach((k)=>{
				if(!seenContextKeysRef.current.has(k)){
					next.add(k);
				}
				seenContextKeysRef.current.add(k);
			});
			return Array.from(next);
		});
	}, [lockedContextItems]);

	const loadWorkspace = React.useCallback(async (options = {})=>{
		setWorkspaceLoading(true);
		try{
			await migrateWorkspaceData();
			const [
				nextProfiles,
				nextMaterials,
				nextFolders,
				nextTagGroups,
				nextTemplates,
				nextTemplateVersions,
				nextBundles,
				nextConversations,
			] = await Promise.all([
				listStoreRecords(AI_ANALYSIS_STORES.providerProfiles),
				listStoreRecords(AI_ANALYSIS_STORES.materials),
				listStoreRecords(AI_ANALYSIS_STORES.materialFolders),
				listStoreRecords(AI_ANALYSIS_STORES.tagGroups),
				listStoreRecords(AI_ANALYSIS_STORES.templates),
				listStoreRecords(AI_ANALYSIS_STORES.templateVersions),
				listStoreRecords(AI_ANALYSIS_STORES.bundles),
				listStoreRecords(AI_ANALYSIS_STORES.conversations),
			]);
			setProviderProfiles(sortByUpdatedDesc(nextProfiles));
			setMaterials(sortByUpdatedDesc(nextMaterials));
			setMaterialFolders(compareByName(nextFolders));
			setTagGroups(compareByName(nextTagGroups));
			setTemplates(sortByUpdatedDesc(nextTemplates));
			setTemplateVersions(sortByUpdatedDesc(nextTemplateVersions));
			setBundles(sortByUpdatedDesc(nextBundles));
			setConversations(sortByUpdatedDesc(nextConversations));
			setSources(listAnalysisSources());
			if(options.keepConversation && activeConversationId){
				setMessages(await listConversationMessages(activeConversationId));
			}
		}catch(e){
			console.error(e);
			message.error('AI分析工作区加载失败');
		}finally{
			setWorkspaceLoading(false);
		}
	}, [activeConversationId]);

	React.useEffect(()=>{
		loadWorkspace();
	}, [loadWorkspace]);

	React.useEffect(()=>{
		if(props.hook){
			props.hook.fun = ()=>{
				loadWorkspace({ keepConversation: true });
			};
		}
	}, [props.hook, loadWorkspace]);

	React.useEffect(()=>{
		saveUiPrefs({
			innerTab,
			modelSelection,
			referenceIds,
			selectedTechniqueKeys: activeTechniqueKeys,
			sessionSystemPrompt,
		});
		if(props.dispatch){
			props.dispatch({
				type: 'astro/save',
				payload: {
					currentSubTab: innerTab,
				},
			});
		}
	}, [innerTab, modelSelection, referenceIds, activeTechniqueKeys, sessionSystemPrompt, props.dispatch]);

	React.useEffect(()=>{
		if(!selectedSourceId){
			setSourceContext(null);
			return;
		}
		const source = sources.find((item)=>item.id === selectedSourceId);
		if(!source){
			setSourceContext(null);
			return;
		}
		let cancelled = false;
		getAnalysisSourceContext(source, {
			mode: sourceContextMode,
		}).then((ctx)=>{
			if(!cancelled){
				setSourceContext((prev)=>sameSourceContext(prev, ctx) ? prev : ctx);
			}
		}).catch(()=>{
			if(!cancelled){
				setSourceContext(null);
			}
		});
		return ()=>{
			cancelled = true;
		};
	}, [selectedSourceId, sources, sourceContextMode]);

	React.useEffect(()=>{
		if(!activeSource){
			if(selectedTechniqueKeys.length){
				setSelectedTechniqueKeys([]);
			}
			setTechniqueContexts([]);
			return;
		}
		const allowed = new Set(techniqueOptions.map((item)=>item.value));
		const next = selectedTechniqueKeys.filter((item)=>allowed.has(item));
		if(next.length !== selectedTechniqueKeys.length){
			setSelectedTechniqueKeys(next);
		}
	}, [activeSource, techniqueOptions, selectedTechniqueKeys]);

	React.useEffect(()=>{
		if(!activeSource || !activeTechniqueKeys.length){
			setTechniqueContexts([]);
			return;
		}
		let cancelled = false;
		setTechniqueContexts(buildTechniqueLoadingState(activeTechniqueKeys, techniqueLabelMap));
		activeTechniqueKeys.forEach((techniqueKey)=>{
			getAnalysisTechniqueContexts(activeSource, [techniqueKey], {
				sourceContext,
			}).then((items)=>{
				if(cancelled){
					return;
				}
				const nextItem = items && items[0]
					? items[0]
					: {
						key: techniqueKey,
						title: techniqueLabelMap.get(techniqueKey) || techniqueKey,
						module: techniqueKey,
						content: '',
						available: false,
						status: 'missing',
						meta: {},
					};
				setTechniqueContexts((prev)=>mergeTechniqueState(prev, nextItem, activeTechniqueKeys, techniqueLabelMap));
			}).catch(()=>{
				if(cancelled){
					return;
				}
				setTechniqueContexts((prev)=>mergeTechniqueState(prev, {
					key: techniqueKey,
					title: techniqueLabelMap.get(techniqueKey) || techniqueKey,
					module: techniqueKey,
					content: '',
					available: false,
					status: 'missing',
					meta: {},
				}, activeTechniqueKeys, techniqueLabelMap));
			});
		});
		return ()=>{
			cancelled = true;
		};
	}, [activeSource, activeTechniqueKeys, sourceContext, techniqueLabelMap]);

	React.useEffect(()=>{
		if(!modelOptions.length){
			if(modelSelection){
				setModelSelection('');
			}
			return;
		}
		if(!modelSelection || !modelOptions.some((item)=>item.value === modelSelection)){
			setModelSelection(modelOptions[0].value);
		}
	}, [modelOptions, modelSelection]);

	const applyProviderPresetToForm = React.useCallback((providerType)=>{
		const preset = getProviderPreset(providerType);
		const currentValues = providerForm.getFieldsValue(true);
		providerForm.setFieldsValue({
			...currentValues,
			providerType,
			name: preset.label,
			baseUrl: preset.baseUrl,
			manualModels: joinModelLines(getProviderDefaultChatModels(providerType)),
			embeddingModels: joinModelLines(getProviderDefaultEmbeddingModels(providerType)),
			requestTimeoutMs: preset.requestTimeoutMs || 120000,
			anthropicApiVersion: preset.anthropicApiVersion || '2023-06-01',
			anthropicMaxTokens: preset.anthropicMaxTokens || '2048',
			anthropicThinkingBudget: preset.anthropicThinkingBudget || '',
			anthropicTopP: preset.anthropicTopP || '',
			anthropicTopK: preset.anthropicTopK || '',
			geminiGenerationConfigText: currentValues.geminiGenerationConfigText || '{}',
			geminiSafetySettingsText: currentValues.geminiSafetySettingsText || '[]',
			ollamaKeepAlive: preset.ollamaKeepAlive || '5m',
			ollamaNumCtx: preset.ollamaNumCtx || '8192',
			ollamaNumPredict: preset.ollamaNumPredict || '1024',
			ollamaTopK: preset.ollamaTopK || '40',
			ollamaTopP: preset.ollamaTopP || '0.9',
			ollamaRepeatPenalty: preset.ollamaRepeatPenalty || '1.1',
			enabled: currentValues.enabled !== false,
		});
	}, [providerForm]);

	async function startNewConversation(options = {}){
		if(abortRef.current){
			abortRef.current.abort();
		}
		setActiveConversationId('');
		setMessages([]);
		setPrompt('');
		setSelectedHistoryIds([]);
		if(options.switchTab !== false){
			setInnerTab('analysis');
		}
	}

	async function openConversation(conversation){
		if(!conversation){
			return;
		}
		setActiveConversationId(conversation.id);
		setSelectedSourceId(conversation.sourceRef && conversation.sourceRef.id ? conversation.sourceRef.id : '');
		setReferenceIds(conversation.referenceIds || []);
		setSelectedTechniqueKeys(conversation.techniqueKeys || []);
		setModelSelection(encodeModelSelection(conversation.providerProfileId || '', conversation.model || ''));
		setSessionSystemPrompt(conversation.systemPrompt || '');
		setMessages(await listConversationMessages(conversation.id));
		setInnerTab('analysis');
	}

	async function ensureConversationRecord(currentPrompt, profile, model){
		const now = new Date().toISOString();
		const source = activeSource || null;
		const payload = {
			title: activeConversation ? (activeConversation.title || buildConversationTitle(currentPrompt, source)) : buildConversationTitle(currentPrompt, source),
			sourceRef: source ? {
				id: source.id,
				sourceType: source.sourceType,
				title: source.title,
				module: source.module,
			} : null,
			providerProfileId: profile ? profile.id : '',
			providerName: profile ? profile.name : '',
			providerType: profile ? profile.providerType : '',
			model,
			referenceIds: referenceIds.slice(0),
			techniqueKeys: activeTechniqueKeys.slice(0),
			systemPrompt: sessionSystemPrompt,
			lastMessageAt: now,
			updatedAt: now,
			archived: activeConversation ? activeConversation.archived : false,
			favorite: activeConversation ? activeConversation.favorite : false,
			branchRootId: activeConversation ? (activeConversation.branchRootId || activeConversation.id) : null,
			parentConversationId: activeConversation ? activeConversation.parentConversationId : null,
			schemaVersion: AI_ANALYSIS_SCHEMA_VERSION,
		};
		const conversation = await putStoreRecord(AI_ANALYSIS_STORES.conversations, {
			...(activeConversation || {}),
			...payload,
			createdAt: activeConversation ? activeConversation.createdAt : now,
		}, 'conv');
		setConversations((prev)=>{
			const exists = prev.some((item)=>item.id === conversation.id);
			return sortByUpdatedDesc(exists ? prev.map((item)=>item.id === conversation.id ? conversation : item) : [conversation].concat(prev));
		});
		setActiveConversationId(conversation.id);
		return conversation;
	}

	async function ensureChunkEmbeddings(profile, embeddingModel, chunks){
		if(!profile || !embeddingModel || !(chunks || []).length){
			return chunks || [];
		}
		const allEmbeddings = await listStoreRecords(AI_ANALYSIS_STORES.materialEmbeddings);
		const enriched = [];
		const missing = [];
		(chunks || []).forEach((chunk)=>{
			const found = allEmbeddings.find((item)=>item.chunkId === chunk.id && item.providerProfileId === profile.id && item.embeddingModel === embeddingModel);
			if(found && Array.isArray(found.vector) && found.vector.length){
				enriched.push({
					...chunk,
					vector: found.vector,
				});
			}else{
				missing.push(chunk);
			}
		});
		if(missing.length){
			const rsp = await requestEmbeddingVectors({
				providerType: profile.providerType,
				apiKey: profile.apiKey,
				baseUrl: profile.baseUrl,
				model: embeddingModel,
				embeddingModel,
				input: missing.map((item)=>item.content),
			});
			const vectors = rsp && rsp.Result && Array.isArray(rsp.Result.vectors) ? rsp.Result.vectors : [];
			const saved = await bulkPutStoreRecords(AI_ANALYSIS_STORES.materialEmbeddings, missing.map((chunk, idx)=>({
				id: `emb-${profile.id}-${embeddingModel}-${chunk.id}`,
				materialId: chunk.materialId,
				chunkId: chunk.id,
				providerProfileId: profile.id,
				embeddingModel,
				vector: vectors[idx] || [],
			})), 'emb');
			saved.forEach((item)=>{
				const chunk = missing.find((one)=>one.id === item.chunkId);
				if(chunk){
					enriched.push({
						...chunk,
						vector: item.vector,
					});
				}
			});
		}
		return enriched;
	}

	async function retrieveMaterialContext(query, resolvedRefs, profile){
		const directMaterials = [];
		const ragMaterials = [];
		(resolvedRefs.materials || []).forEach((item)=>{
			if(shouldUseDirectAttach(item)){
				directMaterials.push(item);
			}else{
				ragMaterials.push(item);
			}
		});
		if(!ragMaterials.length){
			return {
				directMaterials,
				retrievedChunks: [],
				retrievedText: '',
			};
		}
		let chunks = [];
		for(let i=0; i<ragMaterials.length; i++){
			const material = ragMaterials[i];
			const materialChunks = await ensureMaterialChunks(material);
			chunks = chunks.concat(materialChunks.map((chunk)=>({
				...chunk,
				materialName: material.name,
			})));
		}
		let ranked = rankChunksByKeyword(query, chunks).slice(0, 12);
		const profileOptions = profile && profile.providerOptions ? profile.providerOptions : {};
		const embeddingModel = profileOptions.embeddingModel || (normalizeEmbeddingModels(profile)[0] || '');
		if(profile && embeddingModel && ranked.length){
			try{
				const queryEmbeddingRsp = await requestEmbeddingVectors({
					providerType: profile.providerType,
					apiKey: profile.apiKey,
					baseUrl: profile.baseUrl,
					model: embeddingModel,
					embeddingModel,
					input: [query],
				});
				const queryVector = queryEmbeddingRsp && queryEmbeddingRsp.Result && Array.isArray(queryEmbeddingRsp.Result.vectors)
					? queryEmbeddingRsp.Result.vectors[0]
					: [];
				if(Array.isArray(queryVector) && queryVector.length){
					const enriched = await ensureChunkEmbeddings(profile, embeddingModel, ranked);
					ranked = rerankChunksWithVector(queryVector, enriched).slice(0, 6);
				}
			}catch(e){
				console.warn('embedding rerank skipped', e);
			}
		}
		const retrievedChunks = mergeRetrievedChunks(ranked, 5200);
		return {
			directMaterials,
			retrievedChunks,
			retrievedText: buildRetrievedContextText(retrievedChunks),
		};
	}

	async function updateConversationMeta(conversation, patch = {}){
		const saved = await putStoreRecord(AI_ANALYSIS_STORES.conversations, {
			...(conversation || {}),
			...(patch || {}),
			updatedAt: new Date().toISOString(),
		}, 'conv');
		setConversations((prev)=>sortByUpdatedDesc(prev.map((item)=>item.id === saved.id ? saved : item)));
		return saved;
	}

	async function streamReply({
		conversation,
		profile,
		model,
		chatMessages,
		appendAssistant = true,
		existingAssistantId = '',
	}) {
		const assistantMessage = await saveConversationMessage({
			id: existingAssistantId || null,
			conversationId: conversation.id,
			role: 'assistant',
			content: '',
			streamStatus: 'streaming',
			createdAt: new Date().toISOString(),
			updatedAt: new Date().toISOString(),
		});
		streamBufferRef.current = '';
		if(appendAssistant){
			setMessages((prev)=>{
				const exists = prev.some((item)=>item.id === assistantMessage.id);
				return exists ? prev.map((item)=>item.id === assistantMessage.id ? assistantMessage : item) : prev.concat(assistantMessage);
			});
		}else{
			setMessages((prev)=>prev.map((item)=>item.id === assistantMessage.id ? assistantMessage : item));
		}
		const abortController = new AbortController();
		abortRef.current = abortController;
		try{
			await requestAIAnalysisChatStream({
				providerType: profile.providerType,
				apiKey: profile.apiKey,
				baseUrl: profile.baseUrl,
				model,
				providerOptions: profile.providerOptions || {},
				messages: chatMessages,
			}, {
				signal: abortController.signal,
				onEvent: (event)=>{
					if(event.type === 'delta'){
						const delta = event.json && event.json.delta ? `${event.json.delta}` : '';
						if(!delta){
							return;
						}
						streamBufferRef.current += delta;
						setMessages((prev)=>prev.map((item)=>item.id === assistantMessage.id ? {
							...item,
							content: streamBufferRef.current,
							streamStatus: 'streaming',
							updatedAt: new Date().toISOString(),
						} : item));
					}
				},
			});
			const finalContent = `${streamBufferRef.current || ''}`.trim();
			const saved = await saveConversationMessage({
				...assistantMessage,
				content: finalContent || '模型未返回可用内容',
				streamStatus: 'done',
				updatedAt: new Date().toISOString(),
			});
			setMessages((prev)=>prev.map((item)=>item.id === saved.id ? saved : item));
			await updateConversationMeta(conversation, {
				lastMessageAt: saved.updatedAt,
			});
			return saved;
		}catch(e){
			const aborted = e && e.name === 'AbortError';
			const saved = await saveConversationMessage({
				...assistantMessage,
				content: streamBufferRef.current || (aborted ? '已停止生成。' : '生成失败。'),
				streamStatus: aborted ? 'aborted' : 'error',
				updatedAt: new Date().toISOString(),
			});
			setMessages((prev)=>prev.map((item)=>item.id === saved.id ? saved : item));
			if(!aborted){
				throw e;
			}
			return saved;
		}finally{
			abortRef.current = null;
		}
	}

	async function buildResolvedPrompt(currentPrompt, profile){
		const resolvedRefs = resolveReferenceItems(referenceIds, materials, bundles, templates);
		const currentSource = activeSource || (activeConversation && activeConversation.sourceRef ? sources.find((item)=>item.id === activeConversation.sourceRef.id) : null);
		const ctx = currentSource && currentSource.record ? await getAnalysisSourceContext(currentSource, {
			mode: activeTechniqueKeys.length ? 'meta' : 'full',
		}) : sourceContext;
		const resolvedTechniqueContexts = currentSource && activeTechniqueKeys.length
			? await getAnalysisTechniqueContexts(currentSource, activeTechniqueKeys, { sourceContext: ctx })
			: [];
		if(ctx){
			setSourceContext(ctx);
		}
		setTechniqueContexts(resolvedTechniqueContexts);
		const retrieval = await retrieveMaterialContext(currentPrompt, resolvedRefs, profile);
		const layers = buildContextLayers({
			sourceContext: ctx,
			techniqueContexts: resolvedTechniqueContexts,
			materials: retrieval.directMaterials.map((item)=>({
				...item,
				retrievedOnly: false,
			})),
			bundles: resolvedRefs.bundles,
			templates: resolvedRefs.templates,
			retrievedChunks: retrieval.retrievedChunks,
			conversationMessages: visibleMessages,
			systemPrompt: [sessionSystemPrompt, resolvedRefs.systemPrompt].filter(Boolean).join('\n\n'),
		});
		const clippedLayers = clipContextLayers(layers, { maxChars: 20000 });
		return {
			systemPrompt: buildPromptContext({
				sourceContext: ctx,
				techniqueContexts: resolvedTechniqueContexts,
				materials: retrieval.directMaterials,
				bundles: resolvedRefs.bundles,
				templates: resolvedRefs.templates,
				retrievedChunks: retrieval.retrievedChunks,
				conversationMessages: visibleMessages,
				systemPrompt: [sessionSystemPrompt, resolvedRefs.systemPrompt].filter(Boolean).join('\n\n'),
				maxChars: 20000,
			}),
			retrieval,
			clippedLayers,
		};
	}

	async function handleSend(){
		const trimmed = `${prompt || ''}`.trim();
		if(!trimmed){
			message.warning('请输入要分析的问题');
			return;
		}
		const { profileId, model } = parseModelSelection(modelSelection);
		const profile = providerProfiles.find((item)=>item.id === profileId);
		if(!profile || !model){
			message.warning('请先选择可用模型');
			return;
		}
		if(!profile.apiKey && profile.providerType !== 'ollama'){
			message.warning('当前配置缺少 API Key，请先到设置中补全');
			return;
		}
		setSending(true);
		try{
			const conversation = await ensureConversationRecord(trimmed, profile, model);
			const promptResult = await buildResolvedPrompt(trimmed, profile);
			const userMessage = await saveConversationMessage({
				conversationId: conversation.id,
				role: 'user',
				content: trimmed,
				streamStatus: 'done',
			});
			setMessages((prev)=>prev.concat(userMessage));
			setPrompt('');
			await streamReply({
				conversation,
				profile,
				model,
				chatMessages: [
					{
						role: 'system',
						content: promptResult.systemPrompt,
					},
				].concat(visibleMessages.concat(userMessage).map((item)=>({
					role: item.role,
					content: item.content,
				}))),
			});
		}catch(e){
			console.error(e);
			message.error('发送分析请求失败');
		}finally{
			setSending(false);
		}
	}

	function handleStopStreaming(){
		if(abortRef.current){
			abortRef.current.abort();
		}
	}

	async function resetConversationDraft(){
		await startNewConversation();
	}

	async function handleDeleteConversation(conversationId){
		await deleteStoreRecord(AI_ANALYSIS_STORES.conversations, conversationId);
		await deleteWhere(AI_ANALYSIS_STORES.messages, (item)=>item.conversationId === conversationId);
		setConversations((prev)=>prev.filter((item)=>item.id !== conversationId));
		setSelectedHistoryIds((prev)=>prev.filter((id)=>id !== conversationId));
		if(activeConversationId === conversationId){
			await resetConversationDraft();
		}
		message.success('对话已删除');
	}

	async function handleDuplicateConversation(conversation){
		const copied = await putStoreRecord(AI_ANALYSIS_STORES.conversations, {
			...conversation,
			id: null,
			title: `${conversation.title || '未命名对话'}（副本）`,
			parentConversationId: conversation.id,
			branchRootId: conversation.branchRootId || conversation.id,
			createdAt: new Date().toISOString(),
			updatedAt: new Date().toISOString(),
		}, 'conv');
		const oldMessages = await listConversationMessages(conversation.id);
		await replaceConversationMessages(copied.id, oldMessages.map((item)=>({
			...item,
			id: null,
			conversationId: copied.id,
			branchConversationId: copied.id,
		})));
		setConversations((prev)=>sortByUpdatedDesc([copied].concat(prev)));
		message.success('对话已复制');
	}

	async function handleRenameConversation(conversation){
		const nextTitle = window.prompt('请输入新的对话标题', conversation.title || '');
		if(nextTitle === null){
			return;
		}
		const title = `${nextTitle || ''}`.trim();
		if(!title){
			message.warning('标题不能为空');
			return;
		}
		await updateConversationMeta(conversation, { title });
		message.success('标题已更新');
	}

	async function handleToggleConversationFlag(conversation, key){
		await updateConversationMeta(conversation, {
			[key]: !conversation[key],
		});
	}

	async function handleArchiveSelected(value){
		await Promise.all(selectedHistoryIds.map(async (id)=>{
			const conversation = conversations.find((item)=>item.id === id);
			if(conversation){
				await updateConversationMeta(conversation, { archived: value });
			}
		}));
		message.success(value ? '已归档所选对话' : '已取消归档');
	}

	async function handleFavoriteSelected(value){
		await Promise.all(selectedHistoryIds.map(async (id)=>{
			const conversation = conversations.find((item)=>item.id === id);
			if(conversation){
				await updateConversationMeta(conversation, { favorite: value });
			}
		}));
		message.success(value ? '已收藏所选对话' : '已取消收藏');
	}

	async function handleBatchDeleteConversations(){
		for(let i=0; i<selectedHistoryIds.length; i++){
			await handleDeleteConversation(selectedHistoryIds[i]);
		}
		setSelectedHistoryIds([]);
	}

	async function exportConversation(conversation, format){
		const msgList = await listConversationMessages(conversation.id);
		const exported = await exportConversationByFormat(conversation, msgList, format);
		if(desktopBridge){
			try{
				const base64Data = await blobToBase64(exported.blob);
				await saveDesktopFile({
					defaultFileName: exported.fileName,
					base64Data,
					mimeType: exported.blob.type,
				});
				return;
			}catch(e){
				console.warn('desktop save failed, fallback to browser', e);
			}
		}
		saveBlobToBrowser(exported.fileName, exported.blob);
	}

	async function exportSelectedConversations(){
		const list = conversations.filter((item)=>selectedHistoryIds.includes(item.id));
		if(!list.length){
			message.warning('请先选择要导出的对话');
			return;
		}
		const blob = await exportConversationBundle(list, async (conversation)=>listConversationMessages(conversation.id));
		if(desktopBridge){
			try{
				const base64Data = await blobToBase64(blob);
				await saveDesktopFile({
					defaultFileName: 'ai-analysis-conversations.zip',
					base64Data,
					mimeType: 'application/zip',
				});
				return;
			}catch(e){
				console.warn('desktop save failed, fallback to browser', e);
			}
		}
		saveBlobToBrowser('ai-analysis-conversations.zip', blob);
	}

	async function handleExportWorkspaceBackup(){
		const workspace = {
			snapshotVersion: AI_ANALYSIS_SCHEMA_VERSION,
			exportedAt: new Date().toISOString(),
			stores: {},
		};
		const storeKeys = Object.values(AI_ANALYSIS_STORES);
		for(let i=0; i<storeKeys.length; i++){
			workspace.stores[storeKeys[i]] = await listStoreRecords(storeKeys[i]);
		}
		const blob = await exportWorkspaceBackupBlob(workspace);
		if(desktopBridge){
			try{
				const base64Data = await blobToBase64(blob);
				await saveDesktopFile({
					defaultFileName: 'horosa-ai-analysis-backup.zip',
					base64Data,
					mimeType: 'application/zip',
				});
				message.success('备份已导出');
				return;
			}catch(e){
				console.warn(e);
			}
		}
		saveBlobToBrowser('horosa-ai-analysis-backup.zip', blob);
		message.success('备份已导出');
	}

	async function restoreWorkspaceBackup(blob){
		const payload = await parseWorkspaceBackupBlob(blob);
		const stores = payload && payload.stores ? payload.stores : {};
		const storeKeys = Object.values(AI_ANALYSIS_STORES);
		for(let i=0; i<storeKeys.length; i++){
			const storeName = storeKeys[i];
			await deleteWhere(storeName, ()=>true);
			await bulkPutStoreRecords(storeName, stores[storeName] || [], storeName);
		}
		await loadWorkspace();
		message.success('备份已恢复');
	}

	async function handleRestoreWorkspaceBackup(){
		if(desktopBridge){
			try{
				const payload = await openDesktopBackup();
				if(payload && payload.base64Data){
					await restoreWorkspaceBackup(base64ToBlob(payload.base64Data, payload.mimeType || 'application/zip'));
					return;
				}
			}catch(e){
				console.warn(e);
			}
		}
		if(backupRestoreInputRef.current){
			backupRestoreInputRef.current.value = '';
			backupRestoreInputRef.current.click();
		}
	}

	async function handleBackupRestoreInputChange(e){
		const file = e && e.target && e.target.files ? e.target.files[0] : null;
		if(file){
			await restoreWorkspaceBackup(file);
		}
		if(backupRestoreInputRef.current){
			backupRestoreInputRef.current.value = '';
		}
	}

	function openMaterialEditor(material){
		setEditingMaterial(material || null);
		materialForm.setFieldsValue({
			name: material ? material.name : '',
			tags: material ? (material.tags || []).join(', ') : '',
			folderId: material ? material.folderId : undefined,
			extractedText: material ? material.extractedText : '',
		});
		setMaterialModalOpen(true);
	}

	async function saveMaterialForm(){
		const values = await materialForm.validateFields();
		const saved = await putStoreRecord(AI_ANALYSIS_STORES.materials, {
			...(editingMaterial || {}),
			name: values.name,
			fileName: editingMaterial && editingMaterial.fileName ? editingMaterial.fileName : values.name,
			kind: editingMaterial && editingMaterial.kind ? editingMaterial.kind : 'note',
			folderId: values.folderId || null,
			tags: normalizeTags(values.tags),
			extractedText: `${values.extractedText || ''}`.trim(),
			searchText: buildMaterialSearchText({
				...(editingMaterial || {}),
				name: values.name,
				tags: normalizeTags(values.tags),
				extractedText: `${values.extractedText || ''}`.trim(),
			}),
		}, 'material');
		setMaterials((prev)=>sortByUpdatedDesc(prev.some((item)=>item.id === saved.id) ? prev.map((item)=>item.id === saved.id ? saved : item) : [saved].concat(prev)));
		setMaterialModalOpen(false);
		setEditingMaterial(null);
		message.success('资料已保存');
	}

	async function saveImportedMaterial(parsed, extra = {}){
		const saved = await putStoreRecord(AI_ANALYSIS_STORES.materials, {
			name: parsed.name,
			fileName: parsed.fileName || parsed.name,
			fileExt: parsed.fileExt || '',
			kind: parsed.kind,
			size: parsed.size || 0,
			mimeType: parsed.mimeType || '',
			fileHash: parsed.fileHash || '',
			textHash: parsed.textHash || '',
			originBlob: parsed.originBlob || '',
			tags: normalizeTags(extra.tags),
			folderId: extra.folderId || null,
			extractedText: parsed.extractedText || '',
			extractMeta: parsed.extractMeta || {},
			searchText: buildMaterialSearchText({
				...parsed,
				tags: normalizeTags(extra.tags),
			}),
			schemaVersion: AI_ANALYSIS_SCHEMA_VERSION,
		}, 'material');
		setMaterials((prev)=>sortByUpdatedDesc([saved].concat(prev.filter((item)=>item.id !== saved.id))));
		return saved;
	}

	async function handleImportFileLike(fileLike){
		const parsed = await parseMaterialFile(fileLike);
		const duplicate = materials.find((item)=>item.fileHash && parsed.fileHash && item.fileHash === parsed.fileHash);
		if(duplicate){
			const action = window.prompt(`发现重复资料「${duplicate.name}」，输入 keep 保留两份，overwrite 覆盖原记录，skip 跳过`, 'skip');
			if(action === 'overwrite'){
				await putStoreRecord(AI_ANALYSIS_STORES.materials, {
					...duplicate,
					...parsed,
					id: duplicate.id,
					name: parsed.name,
					searchText: buildMaterialSearchText(parsed),
				}, 'material');
				await loadWorkspace({ keepConversation: true });
				message.success(`已覆盖资料：${duplicate.name}`);
				return 'overwritten';
			}
			if(action !== 'keep'){
				message.info('已跳过重复资料');
				return 'skipped';
			}
		}
		await saveImportedMaterial(parsed);
		message.success(`资料已导入：${parsed.name}`);
		return 'imported';
	}

	async function importFileLikeList(fileList, options = {}){
		const list = Array.from(fileList || []).filter(Boolean);
		let count = 0;
		for(let i=0; i<list.length; i++){
			const result = await handleImportFileLike(list[i]);
			if(result === 'imported' || result === 'overwritten'){
				count += 1;
			}
		}
		if(count && options.successMessage){
			message.success(options.successMessage(count));
		}
		return count;
	}

	function clearFileInput(ref){
		if(ref && ref.current){
			ref.current.value = '';
		}
	}

	function openFallbackFilePicker(ref){
		if(ref && ref.current){
			ref.current.click();
			return true;
		}
		return false;
	}

	function formatImportError(prefix, error){
		const text = error && error.message ? `${error.message}` : `${error || ''}`;
		if(!text || text === 'Error'){
			return prefix;
		}
		return `${prefix}：${text}`;
	}

	async function handleUploadMaterial(file){
		try{
			await handleImportFileLike(file);
			return false;
		}catch(e){
			console.error(e);
			message.error('资料导入失败');
			return false;
		}
	}

	async function handleDesktopFilePick(){
		try{
			const files = await pickDesktopFiles();
			for(let i=0; i<(files || []).length; i++){
				const item = files[i];
				const blob = base64ToBlob(item.base64Data, item.mimeType || 'application/octet-stream');
				const file = new File([blob], item.fileName, {
					type: item.mimeType || '',
				});
				await handleImportFileLike(file);
			}
		}catch(e){
			console.error(e);
			clearFileInput(desktopFileInputRef);
			if(openFallbackFilePicker(desktopFileInputRef)){
				message.warning('桌面选文件暂时不可用，已切换为浏览器文件选择');
				return;
			}
			message.error(formatImportError('桌面导入失败', e));
		}
	}

	async function handleDesktopFolderImport(){
		try{
			const files = await pickDesktopFolder();
			for(let i=0; i<(files || []).length; i++){
				const item = files[i];
				const blob = base64ToBlob(item.base64Data, item.mimeType || 'application/octet-stream');
				const file = new File([blob], item.fileName, {
					type: item.mimeType || '',
				});
				await handleImportFileLike(file);
			}
			if((files || []).length){
				message.success(`已从目录导入 ${(files || []).length} 份资料`);
			}
		}catch(e){
			console.error(e);
			clearFileInput(desktopFolderInputRef);
			if(openFallbackFilePicker(desktopFolderInputRef)){
				message.warning('目录导入暂时不可用，已切换为浏览器目录选择');
				return;
			}
			message.error(formatImportError('目录导入失败', e));
		}
	}

	async function handleDesktopFileInputChange(e){
		try{
			await importFileLikeList(e && e.target ? e.target.files : [], {
				successMessage: (count)=>`已导入 ${count} 份资料`,
			});
		}catch(error){
			console.error(error);
			message.error(formatImportError('资料导入失败', error));
		}finally{
			clearFileInput(desktopFileInputRef);
		}
	}

	async function handleDesktopFolderInputChange(e){
		try{
			const count = await importFileLikeList(e && e.target ? e.target.files : [], {
				successMessage: (total)=>`已从目录导入 ${total} 份资料`,
			});
			if(!count){
				message.info('当前目录中没有可导入的资料文件');
			}
		}catch(error){
			console.error(error);
			message.error(formatImportError('目录导入失败', error));
		}finally{
			clearFileInput(desktopFolderInputRef);
		}
	}

	async function deleteMaterial(materialId){
		await deleteStoreRecord(AI_ANALYSIS_STORES.materials, materialId);
		await deleteWhere(AI_ANALYSIS_STORES.materialChunks, (item)=>item.materialId === materialId);
		await deleteWhere(AI_ANALYSIS_STORES.materialEmbeddings, (item)=>item.materialId === materialId);
		setMaterials((prev)=>prev.filter((item)=>item.id !== materialId));
		setReferenceIds((prev)=>prev.filter((item)=>item !== `material:${materialId}`));
		message.success('资料已删除');
	}

	async function handleReplaceMaterial(material, file){
		try{
			const parsed = await parseMaterialFile(file);
			const saved = await putStoreRecord(AI_ANALYSIS_STORES.materials, {
				...material,
				...parsed,
				id: material.id,
				name: material.name || parsed.name,
				folderId: material.folderId || null,
				tags: material.tags || [],
				searchText: buildMaterialSearchText({
					...material,
					...parsed,
				}),
			}, 'material');
			setMaterials((prev)=>sortByUpdatedDesc(prev.map((item)=>item.id === saved.id ? saved : item)));
			await deleteWhere(AI_ANALYSIS_STORES.materialChunks, (item)=>item.materialId === material.id);
			await deleteWhere(AI_ANALYSIS_STORES.materialEmbeddings, (item)=>item.materialId === material.id);
			message.success(`已替换文件：${material.name}`);
		}catch(e){
			console.error(e);
			message.error('替换文件失败');
		}
		return false;
	}

	async function exportMaterialOriginal(material){
		if(!material.originBlob){
			message.warning('这份资料没有保存原文件');
			return;
		}
		const blob = base64ToBlob(material.originBlob, material.mimeType || 'application/octet-stream');
		if(desktopBridge){
			try{
				await saveDesktopFile({
					defaultFileName: material.fileName || material.name || 'material.bin',
					base64Data: material.originBlob,
					mimeType: material.mimeType || 'application/octet-stream',
				});
				return;
			}catch(e){
				console.warn(e);
			}
		}
		saveBlobToBrowser(material.fileName || material.name || 'material.bin', blob);
	}

	function exportMaterialText(material){
		downloadTextFile(`${material.name || 'material'}.txt`, material.extractedText || '');
	}

	async function dedupeMaterials(){
		const grouped = new Map();
		const duplicates = [];
		materials.forEach((item)=>{
			const key = item.fileHash || item.textHash;
			if(!key){
				return;
			}
			if(grouped.has(key)){
				duplicates.push(item);
				return;
			}
			grouped.set(key, item);
		});
		if(!duplicates.length){
			message.success('未发现重复资料');
			return;
		}
		const confirm = window.confirm(`检测到 ${duplicates.length} 份重复资料，是否删除重复项？`);
		if(!confirm){
			return;
		}
		for(let i=0; i<duplicates.length; i++){
			await deleteMaterial(duplicates[i].id);
		}
		message.success(`已删除 ${duplicates.length} 份重复资料`);
	}

	function openTemplateEditor(template){
		setEditingTemplate(template || null);
		templateForm.setFieldsValue({
			name: template ? template.name : '',
			format: template ? template.format : 'text',
			instructionText: template ? (template.instructionText || template.content || '') : '',
			jsonSchema: template ? (template.jsonSchema || template.content || '{\n  \"type\": \"object\"\n}') : '{\n  \"type\": \"object\"\n}',
			exampleInput: template ? (template.exampleInput || '{\n  \"user_prompt\": \"请分析这个案例\"\n}') : '{\n  \"user_prompt\": \"请分析这个案例\"\n}',
			exampleOutput: template ? (template.exampleOutput || '{\n  \"summary\": \"示例输出\"\n}') : '{\n  \"summary\": \"示例输出\"\n}',
		});
		setTemplateModalOpen(true);
	}

	async function saveTemplateForm(){
		const values = await templateForm.validateFields();
		const snapshot = buildTemplateVersionSnapshot(values);
		if(values.format === 'json' && !safeParseJson(values.jsonSchema, null)){
			message.error('JSON Schema 解析失败');
			return;
		}
		const current = editingTemplate || {};
		let saved = await putStoreRecord(AI_ANALYSIS_STORES.templates, {
			...current,
			name: values.name,
			format: values.format,
			instructionText: values.instructionText || '',
			jsonSchema: values.jsonSchema || '',
			exampleInput: values.exampleInput || '',
			exampleOutput: values.exampleOutput || '',
			content: values.format === 'text' ? (values.instructionText || '') : (values.jsonSchema || ''),
		}, 'template');
		const versions = templateVersions.filter((item)=>item.templateId === saved.id);
		const version = await putStoreRecord(AI_ANALYSIS_STORES.templateVersions, {
			templateId: saved.id,
			versionNumber: versions.length + 1,
			snapshot,
		}, 'tplver');
		saved = await putStoreRecord(AI_ANALYSIS_STORES.templates, {
			...saved,
			activeVersionId: version.id,
		}, 'template');
		setTemplates((prev)=>sortByUpdatedDesc(prev.some((item)=>item.id === saved.id) ? prev.map((item)=>item.id === saved.id ? saved : item) : [saved].concat(prev)));
		setTemplateVersions((prev)=>sortByUpdatedDesc([version].concat(prev.filter((item)=>item.id !== version.id))));
		setTemplateModalOpen(false);
		setEditingTemplate(null);
		message.success('模版已保存');
	}

	async function deleteTemplate(templateId){
		await deleteStoreRecord(AI_ANALYSIS_STORES.templates, templateId);
		await deleteWhere(AI_ANALYSIS_STORES.templateVersions, (item)=>item.templateId === templateId);
		setTemplates((prev)=>prev.filter((item)=>item.id !== templateId));
		setTemplateVersions((prev)=>prev.filter((item)=>item.templateId !== templateId));
		message.success('模版已删除');
	}

	async function rollbackTemplateVersion(template, version){
		const snapshot = version && version.snapshot ? version.snapshot : null;
		if(!snapshot){
			return;
		}
		const saved = await putStoreRecord(AI_ANALYSIS_STORES.templates, {
			...template,
			...snapshot,
			activeVersionId: version.id,
			content: snapshot.content || (snapshot.format === 'json' ? snapshot.jsonSchema : snapshot.instructionText),
		}, 'template');
		setTemplates((prev)=>sortByUpdatedDesc(prev.map((item)=>item.id === saved.id ? saved : item)));
		message.success('模版已回滚到该版本');
	}

	function openBundleEditor(bundle){
		setEditingBundle(bundle || null);
		bundleForm.setFieldsValue({
			name: bundle ? bundle.name : '',
			templateId: bundle ? bundle.templateId : undefined,
			materialIds: bundle ? (bundle.defaultMaterialIds && bundle.defaultMaterialIds.length ? bundle.defaultMaterialIds : (bundle.materialIds || [])) : [],
			defaultModelSelection: bundle && bundle.defaultProviderProfileId && bundle.defaultModel
				? encodeModelSelection(bundle.defaultProviderProfileId, bundle.defaultModel)
				: undefined,
			defaultEmbeddingModel: bundle ? bundle.defaultEmbeddingModel : '',
			defaultSystemPrompt: bundle ? bundle.defaultSystemPrompt : '',
			defaultRetrievalMode: bundle ? bundle.defaultRetrievalMode || 'auto' : 'auto',
		});
		setBundleModalOpen(true);
	}

	async function saveBundleForm(){
		const values = await bundleForm.validateFields();
		const parsed = parseModelSelection(values.defaultModelSelection || '');
		const saved = await putStoreRecord(AI_ANALYSIS_STORES.bundles, {
			...(editingBundle || {}),
			name: values.name,
			templateId: values.templateId || null,
			materialIds: values.materialIds || [],
			defaultMaterialIds: values.materialIds || [],
			defaultProviderProfileId: parsed.profileId || null,
			defaultModel: parsed.model || null,
			defaultEmbeddingModel: values.defaultEmbeddingModel || null,
			defaultSystemPrompt: values.defaultSystemPrompt || '',
			defaultRetrievalMode: values.defaultRetrievalMode || 'auto',
		}, 'bundle');
		setBundles((prev)=>sortByUpdatedDesc(prev.some((item)=>item.id === saved.id) ? prev.map((item)=>item.id === saved.id ? saved : item) : [saved].concat(prev)));
		setBundleModalOpen(false);
		setEditingBundle(null);
		message.success('组合已保存');
	}

	async function deleteBundle(bundleId){
		await deleteStoreRecord(AI_ANALYSIS_STORES.bundles, bundleId);
		setBundles((prev)=>prev.filter((item)=>item.id !== bundleId));
		setReferenceIds((prev)=>prev.filter((item)=>item !== `bundle:${bundleId}`));
		message.success('组合已删除');
	}

	function applyBundle(bundle){
		const nextRefs = uniqueTextList(referenceIds.filter((item)=>item.indexOf('bundle:') !== 0).concat(`bundle:${bundle.id}`));
		setReferenceIds(nextRefs);
		if(bundle.defaultProviderProfileId && bundle.defaultModel){
			setModelSelection(encodeModelSelection(bundle.defaultProviderProfileId, bundle.defaultModel));
		}
		if(bundle.defaultSystemPrompt){
			setSessionSystemPrompt(bundle.defaultSystemPrompt);
		}
		setInnerTab('analysis');
		message.success(`已应用组合：${bundle.name}`);
	}

	function openProviderEditor(profile){
		setEditingProvider(profile || null);
		providerForm.setFieldsValue(buildProviderFormValues(profile));
		setProviderAdvancedOpen(false);
		setProviderModalOpen(true);
	}

	async function saveProviderForm(){
		const checkedValues = await providerForm.validateFields();
		const values = {
			...providerForm.getFieldsValue(true),
			...checkedValues,
		};
		const providerType = values.providerType || 'openai';
		const preset = getProviderPreset(providerType);
		const providerOptions = buildProviderOptionsFromForm(values);
		const manualModels = uniqueTextList(`${values.manualModels || ''}`.split(/[\n,，]/g)).length
			? uniqueTextList(`${values.manualModels || ''}`.split(/[\n,，]/g))
			: getProviderDefaultChatModels(providerType);
		const embeddingModels = uniqueTextList(`${values.embeddingModels || ''}`.split(/[\n,，]/g)).length
			? uniqueTextList(`${values.embeddingModels || ''}`.split(/[\n,，]/g))
			: getProviderDefaultEmbeddingModels(providerType);
		const normalized = normalizeProviderResultModels({
			models: []
				.concat(editingProvider && Array.isArray(editingProvider.availableModels) ? editingProvider.availableModels : [])
				.concat(manualModels)
				.concat(embeddingModels),
		}, providerType, true);
		const saved = await putStoreRecord(AI_ANALYSIS_STORES.providerProfiles, {
			...(editingProvider || {}),
			name: `${values.name || ''}`.trim() || preset.label,
			providerType,
			protocolFamily: getProviderProtocolFamily(providerType),
			apiKey: `${values.apiKey || ''}`.trim(),
			baseUrl: `${values.baseUrl || ''}`.trim() || preset.baseUrl,
			manualModels,
			chatModelIds: normalized.chatModels,
			embeddingModelIds: normalized.embeddingModels,
			availableModels: normalized.models,
			enabled: values.enabled !== false,
			providerOptions,
			healthStatus: editingProvider && editingProvider.healthStatus ? editingProvider.healthStatus : 'unknown',
		}, 'provider');
		setProviderProfiles((prev)=>sortByUpdatedDesc(prev.some((item)=>item.id === saved.id) ? prev.map((item)=>item.id === saved.id ? saved : item) : [saved].concat(prev)));
		setProviderModalOpen(false);
		setProviderAdvancedOpen(false);
		setEditingProvider(null);
		message.success('接口配置已保存');
	}

	async function deleteProvider(profileId){
		await deleteStoreRecord(AI_ANALYSIS_STORES.providerProfiles, profileId);
		setProviderProfiles((prev)=>prev.filter((item)=>item.id !== profileId));
		if(parseModelSelection(modelSelection).profileId === profileId){
			setModelSelection('');
		}
		message.success('接口配置已删除');
	}

	async function fetchModelsAndEmbeddings(profile){
		try{
			const rsp = ensureServiceResponse(await fetchProviderModels({
				providerType: profile.providerType,
				apiKey: profile.apiKey,
				baseUrl: profile.baseUrl,
				providerOptions: profile.providerOptions || {},
			}), '拉取模型列表失败');
			const result = rsp && rsp.Result ? rsp.Result : {};
			const normalized = normalizeProviderResultModels(result, profile.providerType, false);
			const saved = await putStoreRecord(AI_ANALYSIS_STORES.providerProfiles, {
				...profile,
				protocolFamily: getProviderProtocolFamily(profile.providerType),
				availableModels: normalized.models,
				chatModelIds: uniqueTextList((profile.chatModelIds || []).concat(normalized.chatModels)),
				embeddingModelIds: uniqueTextList((profile.embeddingModelIds || []).concat(normalized.embeddingModels)),
			}, 'provider');
			setProviderProfiles((prev)=>sortByUpdatedDesc(prev.map((item)=>item.id === saved.id ? saved : item)));
			message.success(`已拉取 ${normalized.chatModels.length} 个聊天模型${normalized.embeddingModels.length ? `，${normalized.embeddingModels.length} 个 Embedding 模型` : ''}`);
		}catch(e){
			message.error(e && e.message ? `拉取模型列表失败：${e.message}` : '拉取模型列表失败');
		}
	}

	async function runProviderDiagnostics(profile){
		try{
			const rsp = ensureServiceResponse(await diagnoseProvider({
				providerType: profile.providerType,
				apiKey: profile.apiKey,
				baseUrl: profile.baseUrl,
				providerOptions: profile.providerOptions || {},
			}), '连接诊断失败');
			const diagnostics = rsp && rsp.Result ? rsp.Result : null;
			const saved = await putStoreRecord(AI_ANALYSIS_STORES.providerProfiles, {
				...profile,
				lastDiagnostics: diagnostics,
				healthStatus: diagnostics && diagnostics.healthy ? 'healthy' : 'error',
			}, 'provider');
			setProviderProfiles((prev)=>sortByUpdatedDesc(prev.map((item)=>item.id === saved.id ? saved : item)));
			if(diagnostics && diagnostics.healthy){
				message.success(`连接测试成功${diagnostics.latencyMs ? ` · ${diagnostics.latencyMs}ms` : ''}`);
			}else{
				message.warning(`连接测试完成：${diagnostics && (diagnostics.failureReason || diagnostics.errorDetail || '请检查配置')}`);
			}
		}catch(e){
			message.error(e && e.message ? `连接诊断失败：${e.message}` : '连接诊断失败');
		}
	}

	async function testProfileChat(profile){
		const models = normalizeProfileModels(profile);
		if(models.length === 0){
			message.warning('请先配置至少一个模型');
			return;
		}
		try{
			const rsp = ensureServiceResponse(await requestAIAnalysisChat({
				providerType: profile.providerType,
				apiKey: profile.apiKey,
				baseUrl: profile.baseUrl,
				model: models[0],
				providerOptions: profile.providerOptions || {},
				messages: [
					{
						role: 'user',
						content: '请仅回复“连接成功”。',
					},
				],
			}), '测试连接失败');
			const text = rsp && rsp.Result && rsp.Result.content ? rsp.Result.content : '';
			message.success(text ? `测试成功：${text.slice(0, 24)}` : '测试成功');
		}catch(e){
			message.error(e && e.message ? `测试连接失败：${e.message}` : '测试连接失败');
		}
	}

	async function handleRegenerateLastReply(){
		const { profileId, model } = parseModelSelection(modelSelection || encodeModelSelection(activeConversation && activeConversation.providerProfileId, activeConversation && activeConversation.model));
		const profile = providerProfiles.find((item)=>item.id === profileId);
		if(!activeConversation || !profile || !model){
			message.warning('请先选择一段对话和模型');
			return;
		}
		const list = await listConversationMessages(activeConversation.id);
		let trimmedList = list.slice(0);
		if(trimmedList.length && trimmedList[trimmedList.length - 1].role === 'assistant'){
			const removed = trimmedList.pop();
			await deleteStoreRecord(AI_ANALYSIS_STORES.messages, removed.id);
			setMessages(trimmedList);
		}
		const lastUser = [...trimmedList].reverse().find((item)=>item.role === 'user');
		if(!lastUser){
			message.warning('没有可重新生成的用户提问');
			return;
		}
		setSending(true);
		try{
			const promptResult = await buildResolvedPrompt(lastUser.content || '', profile);
			await streamReply({
				conversation: activeConversation,
				profile,
				model,
				chatMessages: [
					{ role: 'system', content: promptResult.systemPrompt },
				].concat(trimmedList.map((item)=>({
					role: item.role,
					content: item.content,
				}))),
			});
		}catch(e){
			console.error(e);
			message.error('重新生成失败');
		}finally{
			setSending(false);
		}
	}

	async function handleEditLastUserAndBranch(){
		if(!activeConversation){
			message.warning('请先打开一段对话');
			return;
		}
		const list = await listConversationMessages(activeConversation.id);
		let lastUserIndex = -1;
		for(let i=list.length - 1; i>=0; i--){
			if(list[i].role === 'user'){
				lastUserIndex = i;
				break;
			}
		}
		if(lastUserIndex < 0){
			message.warning('没有找到上一条用户消息');
			return;
		}
		const lastUser = list[lastUserIndex];
		const nextText = window.prompt('编辑上一条用户消息，并基于此创建分支对话', lastUser.content || '');
		if(nextText === null){
			return;
		}
		const trimmed = `${nextText || ''}`.trim();
		if(!trimmed){
			return;
		}
		const { profileId, model } = parseModelSelection(modelSelection || encodeModelSelection(activeConversation.providerProfileId, activeConversation.model));
		const profile = providerProfiles.find((item)=>item.id === profileId);
		if(!profile || !model){
			message.warning('请先选择模型');
			return;
		}
		const branchConversation = await putStoreRecord(AI_ANALYSIS_STORES.conversations, {
			...activeConversation,
			id: null,
			title: `${activeConversation.title || '未命名对话'}（分支）`,
			parentConversationId: activeConversation.id,
			branchRootId: activeConversation.branchRootId || activeConversation.id,
			createdAt: new Date().toISOString(),
			updatedAt: new Date().toISOString(),
		}, 'conv');
		const branchMessages = list.slice(0, lastUserIndex).concat({
			...lastUser,
			id: null,
			content: trimmed,
			editedFromMessageId: lastUser.id,
			conversationId: branchConversation.id,
		});
		await replaceConversationMessages(branchConversation.id, branchMessages);
		setConversations((prev)=>sortByUpdatedDesc([branchConversation].concat(prev)));
		await openConversation(branchConversation);
		setSending(true);
		try{
			const promptResult = await buildResolvedPrompt(trimmed, profile);
			await streamReply({
				conversation: branchConversation,
				profile,
				model,
				chatMessages: [
					{ role: 'system', content: promptResult.systemPrompt },
				].concat(branchMessages.map((item)=>({
					role: item.role,
					content: item.content,
				}))),
			});
			message.success('已创建分支对话');
		}catch(e){
			message.error('分支对话生成失败');
		}finally{
			setSending(false);
		}
	}

	async function handleBranchFromMessage(messageRecord){
		if(!activeConversation || !messageRecord){
			return;
		}
		const list = await listConversationMessages(activeConversation.id);
		const idx = list.findIndex((item)=>item.id === messageRecord.id);
		if(idx < 0){
			return;
		}
		const branchConversation = await putStoreRecord(AI_ANALYSIS_STORES.conversations, {
			...activeConversation,
			id: null,
			title: `${activeConversation.title || '未命名对话'}（分支）`,
			parentConversationId: activeConversation.id,
			branchRootId: activeConversation.branchRootId || activeConversation.id,
			createdAt: new Date().toISOString(),
			updatedAt: new Date().toISOString(),
		}, 'conv');
		const copiedMessages = list.slice(0, idx + 1).map((item)=>({
			...item,
			id: null,
			conversationId: branchConversation.id,
			branchConversationId: branchConversation.id,
		}));
		await replaceConversationMessages(branchConversation.id, copiedMessages);
		setConversations((prev)=>sortByUpdatedDesc([branchConversation].concat(prev)));
		await openConversation(branchConversation);
		message.success('已从该轮次创建分支');
	}

	function renderAnalysisPane(){
		return (
			<div className={styles.paneShell}>
				<div className={styles.paneHeader}>
					<Card size="small" className={styles.toolbarCard} bordered={false}>
						<div className={styles.toolbarRow}>
							<div className={styles.toolbarField}>
								<div className={`${styles.toolbarLabel} ${styles.toolbarLabelInline}`}>
									<span>本次分析模型</span>
									<Button
										size="small"
										className={styles.quickApiButton}
										onClick={()=>openProviderEditor(null)}
									>
										配置 API
									</Button>
									<Button
										size="small"
										className={styles.quickApiButton}
										disabled={!activeProviderProfile}
										onClick={()=>activeProviderProfile && fetchModelsAndEmbeddings(activeProviderProfile)}
									>
										拉取模型
									</Button>
									<Button
										size="small"
										className={styles.quickApiButton}
										disabled={!activeProviderProfile}
										onClick={()=>activeProviderProfile && testProfileChat(activeProviderProfile)}
									>
										测试连接
									</Button>
									<Button
										size="small"
										className={styles.quickApiButton}
										onClick={()=>setProviderSwitchModalOpen(true)}
									>
										生效 API
									</Button>
								</div>
								<Select
									showSearch
									value={modelSelection || undefined}
									placeholder="选择已启用的模型"
									style={{ width: '100%' }}
									optionFilterProp="children"
									onChange={(val)=>setModelSelection(val || '')}
								>
									{modelOptions.map((item)=>(
										<Select.Option key={item.value} value={item.value}>{item.label}</Select.Option>
									))}
								</Select>
							</div>
							<div className={styles.toolbarField}>
								<div className={styles.toolbarLabel}>案例选择（命盘 / 事盘）</div>
								<Select
									showSearch
									allowClear
									value={selectedSourceId || undefined}
									placeholder="搜索并选择案例"
									style={{ width: '100%' }}
									filterOption={(input, option)=>{
										const source = sourceOptions.find((item)=>item.value === option.value);
										return source ? source.searchText.indexOf(`${input || ''}`.trim().toLowerCase()) >= 0 : false;
									}}
									onChange={(val)=>setSelectedSourceId(val || '')}
								>
									{sourceOptions.map((item)=>(
										<Select.Option key={item.value} value={item.value}>{item.label}</Select.Option>
									))}
								</Select>
							</div>
							{activeSource ? (
								<div className={styles.toolbarField}>
									<div className={styles.toolbarLabel}>使用技法</div>
									<Select
										mode="multiple"
										allowClear
										value={activeTechniqueKeys}
										placeholder={`选择${activeSource.sourceType === 'chart' ? '命盘' : '事盘'}技法`}
										style={{ width: '100%' }}
										onChange={(vals)=>setSelectedTechniqueKeys(vals || [])}
									>
										{techniqueOptions.map((item)=>(
											<Select.Option key={item.value} value={item.value}>{item.label}</Select.Option>
										))}
									</Select>
								</div>
							) : null}
							<div className={styles.toolbarField}>
								<div className={styles.toolbarLabel}>参考组合 / 资料（多选）</div>
								<Select
									mode="multiple"
									showSearch
									allowClear
									value={referenceIds}
									placeholder="选择固定资料、组合"
									style={{ width: '100%' }}
									onChange={(vals)=>setReferenceIds(vals || [])}
								>
									{referenceOptions.map((item)=>(
										<Select.Option key={item.value} value={item.value}>{item.label}</Select.Option>
									))}
								</Select>
							</div>
						</div>
					</Card>
				</div>
				<div className={styles.paneBody}>
					<div className={styles.chatSplit}>
						<Card
							size="small"
							bordered={false}
							className={styles.chatCard}
							title={activeConversation ? activeConversation.title : '分析对话'}
							extra={activeConversation ? <Text type="secondary">{buildTimestampLabel(activeConversation.updatedAt)}</Text> : null}
							bodyStyle={{ height: 'calc(100% - 46px)', display: 'flex', flexDirection: 'column', minHeight: 0, paddingBottom: 0 }}
						>
							<div className={styles.chatColumn}>
								<div className={styles.chatLog}>
									{visibleMessages.length === 0 ? (
										<div className={styles.emptyPane}>
											<Empty description="选择案例、模型后即可开始流式分析对话" />
										</div>
									) : visibleMessages.map((item)=>(
										<div
											key={item.id}
											className={[
												styles.messageBubble,
												item.role === 'user' ? styles.messageUser : styles.messageAssistant,
											].join(' ')}
										>
											<div className={styles.messageMetaRow}>
												<div className={styles.messageMeta}>
													{item.role === 'user' ? '你' : 'AI'}
													{item.createdAt ? ` · ${buildTimestampLabel(item.createdAt)}` : ''}
													{item.streamStatus === 'streaming' ? ' · 生成中' : ''}
													{item.streamStatus === 'aborted' ? ' · 已停止' : ''}
												</div>
												<Space size={4}>
													<Tooltip title="从此轮次分支">
														<Button size="small" type="link" onClick={()=>handleBranchFromMessage(item)}>分支</Button>
													</Tooltip>
												</Space>
											</div>
											{item.role === 'user'
												? <div className={styles.messageText}>{item.content}</div>
												: <div className={styles.markdownBody} dangerouslySetInnerHTML={{ __html: renderMarkdownToHtml(item.content) }} />}
										</div>
									))}
								</div>
								<div className={styles.composer}>
									<TextArea
										value={prompt}
										rows={4}
										placeholder="输入你的分析问题，系统会自动带上案例、资料、组合与模版约束。"
										onChange={(e)=>setPrompt(e.target.value)}
										onPressEnter={(e)=>{
											if(!e.shiftKey){
												e.preventDefault();
												handleSend();
											}
										}}
									/>
									<div className={styles.composerActions}>
										<Space wrap size={6} className={styles.composerTools}>
											<Button size="small" icon={<XQIcon name="refresh" />} onClick={()=>setSources(listAnalysisSources())}>刷新案例</Button>
											<Button size="small" onClick={resetConversationDraft}>新对话</Button>
											<Button size="small" icon={<XQIcon name="sync" />} onClick={handleRegenerateLastReply} disabled={!activeConversation || sending}>重新生成</Button>
											<Button size="small" icon={<XQIcon name="edit" />} onClick={handleEditLastUserAndBranch} disabled={!activeConversation || sending}>编辑上一条并分支</Button>
											<Button size="small" icon={<XQIcon name="stop" />} danger onClick={handleStopStreaming} disabled={!sending}>停止生成</Button>
										</Space>
										<Space size={10} className={styles.composerSend}>
											<Text type="secondary">Enter 发送，Shift + Enter 换行</Text>
											<Button type="primary" icon={<XQIcon name="send" />} loading={sending} onClick={handleSend}>发送分析</Button>
										</Space>
									</div>
								</div>
							</div>
						</Card>
						<div className={styles.sideColumn}>
							<Card size="small" bordered={false} className={styles.systemPromptCard} title="本轮系统提示">
								<TextArea
									value={sessionSystemPrompt}
									rows={2}
									placeholder="可留空；也可由组合一键带入"
									onChange={(e)=>setSessionSystemPrompt(e.target.value)}
								/>
							</Card>
							<Card size="small" bordered={false} className={styles.contextCard} title="本轮挂载上下文" bodyStyle={{ height: 'calc(100% - 46px)', minHeight: 0 }}>
								<div className={styles.contextScroll}>
									{lockedContextItems.length === 0 ? (
										<Empty description="还没有挂载任何前提" />
									) : (
										<Collapse
											activeKey={contextActiveKeys}
											onChange={(ks)=>setContextActiveKeys(Array.isArray(ks) ? ks : [ks])}
											className={styles.contextCollapse}
										>
											{lockedContextItems.map((item)=>{
												const statusMeta = getContextStatusMeta(item.status);
												const signature = buildContextSignatureText(item.meta);
												return (
													<Collapse.Panel
														key={item.key}
														header={(
															<div className={styles.contextPanelHeader}>
																<span className={styles.contextPanelTitle}>{item.title}</span>
																<span className={styles.contextPanelTags}>
																	<Tag>{item.type}</Tag>
																	<Tag color={statusMeta.color}>{statusMeta.text}</Tag>
																</span>
																{signature ? <span className={styles.contextPanelSig}>{signature}</span> : null}
															</div>
														)}
													>
														{item.content
															? <div className={styles.contextBody}>{item.content}</div>
															: <div className={styles.contextEmptyHint}>{item.emptyHint || '暂无内容'}</div>}
													</Collapse.Panel>
												);
											})}
										</Collapse>
									)}
								</div>
							</Card>
						</div>
					</div>
				</div>
			</div>
		);
	}

	function renderHistoryPane(){
		const providerOptions = uniqueTextList(conversations.map((item)=>item.providerName || item.providerType).filter(Boolean));
		const modelOptionsList = uniqueTextList(conversations.map((item)=>item.model).filter(Boolean));
		return (
			<div className={styles.paneShell}>
				<div className={styles.paneHeader}>
					<div className={styles.historyTop}>
						<Search
							allowClear
							placeholder="搜索历史对话、案例名、模型"
							style={{ maxWidth: 320 }}
							value={historyKeyword}
							onChange={(e)=>setHistoryKeyword(e.target.value)}
						/>
						<Select value={historyFilter.provider || undefined} allowClear placeholder="Provider" style={{ width: 150 }} onChange={(val)=>setHistoryFilter((prev)=>({ ...prev, provider: val || '' }))}>
							{providerOptions.map((item)=><Select.Option key={item} value={item}>{item}</Select.Option>)}
						</Select>
						<Select value={historyFilter.model || undefined} allowClear placeholder="模型" style={{ width: 160 }} onChange={(val)=>setHistoryFilter((prev)=>({ ...prev, model: val || '' }))}>
							{modelOptionsList.map((item)=><Select.Option key={item} value={item}>{item}</Select.Option>)}
						</Select>
						<Select value={historyFilter.sourceType} style={{ width: 130 }} onChange={(val)=>setHistoryFilter((prev)=>({ ...prev, sourceType: val || '' }))}>
							<Select.Option value="">全部案例</Select.Option>
							<Select.Option value="chart">命盘</Select.Option>
							<Select.Option value="case">事盘</Select.Option>
						</Select>
						<Select value={historyFilter.favorite} style={{ width: 120 }} onChange={(val)=>setHistoryFilter((prev)=>({ ...prev, favorite: val }))}>
							<Select.Option value="all">全部收藏</Select.Option>
							<Select.Option value="favorite">仅收藏</Select.Option>
							<Select.Option value="normal">未收藏</Select.Option>
						</Select>
						<Select value={historyFilter.archived} style={{ width: 120 }} onChange={(val)=>setHistoryFilter((prev)=>({ ...prev, archived: val }))}>
							<Select.Option value="active">未归档</Select.Option>
							<Select.Option value="archived">已归档</Select.Option>
							<Select.Option value="all">全部</Select.Option>
						</Select>
					</div>
					<div className={styles.historyBatchBar}>
						<Space wrap>
							<Button onClick={resetConversationDraft}>新建对话</Button>
							<Button icon={<XQIcon name="export" />} onClick={exportSelectedConversations} disabled={!selectedHistoryIds.length}>批量导出</Button>
							<Button onClick={()=>handleArchiveSelected(true)} disabled={!selectedHistoryIds.length}>批量归档</Button>
							<Button onClick={()=>handleArchiveSelected(false)} disabled={!selectedHistoryIds.length}>取消归档</Button>
							<Button onClick={()=>handleFavoriteSelected(true)} disabled={!selectedHistoryIds.length}>批量收藏</Button>
							<Button onClick={()=>handleFavoriteSelected(false)} disabled={!selectedHistoryIds.length}>取消收藏</Button>
							<Popconfirm title="确定删除所选历史吗？" onConfirm={handleBatchDeleteConversations}>
								<Button danger icon={<XQIcon name="delete" />} disabled={!selectedHistoryIds.length}>批量删除</Button>
							</Popconfirm>
						</Space>
					</div>
				</div>
				<div className={styles.paneBody}>
					<div className={styles.historyTableWrap}>
						<Table
							rowKey="id"
							size="small"
							className={styles.historyTable}
							rowSelection={{
								selectedRowKeys: selectedHistoryIds,
								onChange: (keys)=>setSelectedHistoryIds(keys),
							}}
							dataSource={filteredConversations}
							scroll={{ y: Math.max(height - 340, 260), x: 'max-content' }}
							pagination={{ pageSize: 8 }}
							columns={[
								{
									title: '标题',
									dataIndex: 'title',
									render: (value, record)=>(
										<div className={styles.tableTitleCell}>
											<span>{value || '未命名对话'}</span>
											{record.favorite ? <Tag color="gold">收藏</Tag> : null}
											{record.archived ? <Tag>归档</Tag> : null}
										</div>
									),
								},
								{
									title: '案例',
									render: (_, record)=>record.sourceRef && record.sourceRef.title ? record.sourceRef.title : '未绑定',
								},
								{
									title: 'Provider / 模型',
									render: (_, record)=>record.providerName ? `${record.providerName} / ${record.model || ''}` : (record.model || '未设置'),
								},
								{
									title: '更新时间',
									render: (_, record)=>buildTimestampLabel(record.updatedAt),
								},
								{
									title: '操作',
									render: (_, record)=>(
										<Space size={4} wrap>
											<Button size="small" type="primary" onClick={()=>openConversation(record)}>打开</Button>
											<Button size="small" onClick={()=>handleRenameConversation(record)}>重命名</Button>
											<Button size="small" onClick={()=>handleDuplicateConversation(record)}>复制</Button>
											<Button size="small" onClick={()=>handleToggleConversationFlag(record, 'favorite')} icon={<XQIcon name="star" />}>{record.favorite ? '取消收藏' : '收藏'}</Button>
											<Button size="small" onClick={()=>handleToggleConversationFlag(record, 'archived')}>{record.archived ? '取消归档' : '归档'}</Button>
											<Button size="small" onClick={()=>exportConversation(record, 'md')}>Markdown</Button>
											<Button size="small" onClick={()=>exportConversation(record, 'json')}>JSON</Button>
											<Button size="small" onClick={()=>exportConversation(record, 'docx')}>Word</Button>
											<Popconfirm title="确定删除这段历史吗？" onConfirm={()=>handleDeleteConversation(record.id)}>
												<Button size="small" danger icon={<XQIcon name="delete" />}>删除</Button>
											</Popconfirm>
										</Space>
									),
								},
							]}
						/>
					</div>
				</div>
			</div>
		);
	}

	function renderMaterialsPane(){
		return (
			<div className={styles.paneShell}>
				<div className={styles.paneHeader}>
					<div className={styles.materialTop}>
						<Search
							allowClear
							placeholder="搜索资料标题、标签、全文"
							style={{ maxWidth: 360 }}
							value={materialKeyword}
							onChange={(e)=>setMaterialKeyword(e.target.value)}
						/>
						{materialFolders.length ? (
							<Select value={selectedFolderId || undefined} placeholder="全部文件夹" style={{ width: 180 }} onChange={(val)=>setSelectedFolderId(val || '')}>
								<Select.Option value="">全部文件夹</Select.Option>
								{materialFolders.map((item)=><Select.Option key={item.id} value={item.id}>{item.name}</Select.Option>)}
							</Select>
						) : null}
						<Select value={materialSort} style={{ width: 150 }} onChange={setMaterialSort}>
							<Select.Option value="updated">按更新时间</Select.Option>
							<Select.Option value="name">按名称</Select.Option>
							<Select.Option value="size">按大小</Select.Option>
						</Select>
						<Space wrap>
							<Button icon={<XQIcon name="plus" />} type="primary" onClick={()=>openMaterialEditor(null)}>新建资料</Button>
							<Button icon={<XQIcon name="sync" />} onClick={dedupeMaterials}>去重</Button>
							{desktopBridge ? <Button icon={<XQIcon name="import" />} onClick={handleDesktopFilePick}>桌面选文件</Button> : null}
							{desktopBridge ? <Button icon={<XQIcon name="folder" />} onClick={handleDesktopFolderImport}>导入文件夹</Button> : null}
						</Space>
					</div>
					<Card size="small" bordered={false} className={styles.uploadCard}>
						<Dragger multiple showUploadList={false} beforeUpload={handleUploadMaterial} accept=".txt,.md,.markdown,.doc,.docx,.pdf">
							<p className="ant-upload-drag-icon">
								<XQIcon name="folder" />
							</p>
							<p className="ant-upload-text">拖动或点击上传资料文件</p>
							<p className={styles.uploadHint}>支持 TXT / Markdown / DOC / DOCX / PDF，大文件会自动切块供 RAG 检索。</p>
						</Dragger>
					</Card>
				</div>
				<div className={styles.paneBody}>
					<div className={styles.materialScroll}>
						{tagGroups.length ? (
							<Card size="small" bordered={false} className={styles.tagGroupCard} title="标签组">
								<Space wrap>
									{tagGroups.map((group)=>(
										<Tag key={group.id}>{group.name}：{(group.tags || []).join('、') || '空'}</Tag>
									))}
								</Space>
							</Card>
						) : null}
						{filteredMaterials.length === 0 ? (
							<div className={styles.materialEmpty}>
								<Empty description="暂无资料" />
							</div>
						) : (
							<div className={styles.materialGrid}>
								{filteredMaterials.map((item)=>(
								<Card key={item.id} size="small" title={item.name} bordered={false}>
									<div className={styles.cardMeta}>
										<div>类型：{item.kind || 'note'}</div>
										<div>文件夹：{item.folderId ? (materialFolders.find((folder)=>folder.id === item.folderId)?.name || '未知') : '未分类'}</div>
										<div>标签：{(item.tags || []).length ? (item.tags || []).join('、') : '无'}</div>
										<div>更新时间：{buildTimestampLabel(item.updatedAt)}</div>
									</div>
									<div className={styles.summaryBlock}>
										{(item.extractedText || '').slice(0, 300)}
										{(item.extractedText || '').length > 300 ? '...' : ''}
									</div>
									<div className={styles.cardActions}>
										<Button size="small" onClick={()=>openMaterialEditor(item)} icon={<XQIcon name="edit" />}>编辑</Button>
										<Button size="small" onClick={()=>setReferenceIds((prev)=>uniqueTextList(prev.concat(`material:${item.id}`)))}>加入参考</Button>
										<Button size="small" icon={<XQIcon name="download" />} onClick={()=>exportMaterialOriginal(item)}>原文件</Button>
										<Button size="small" onClick={()=>exportMaterialText(item)}>提取文本</Button>
										<Upload showUploadList={false} beforeUpload={(file)=>handleReplaceMaterial(item, file)}>
											<Button size="small">替换文件</Button>
										</Upload>
										<Popconfirm title="确定删除这份资料吗？" onConfirm={()=>deleteMaterial(item.id)}>
											<Button size="small" danger icon={<XQIcon name="delete" />}>删除</Button>
										</Popconfirm>
									</div>
								</Card>
								))}
							</div>
						)}
					</div>
				</div>
			</div>
		);
	}

	function renderTemplatesPane(){
		return (
			<div className={styles.paneShell}>
				<div className={styles.paneHeader}>
					<div className={styles.templateTop}>
						<Search
							allowClear
							placeholder="搜索模版与组合"
							style={{ maxWidth: 360 }}
							value={templateKeyword}
							onChange={(e)=>setTemplateKeyword(e.target.value)}
						/>
						<Space>
							<Button icon={<XQIcon name="plus" />} type="primary" onClick={()=>openTemplateEditor(null)}>新建模版</Button>
							<Button icon={<XQIcon name="plus" />} onClick={()=>openBundleEditor(null)}>新建组合</Button>
						</Space>
					</div>
				</div>
				<div className={styles.paneBody}>
					<div className={styles.paneScroll}>
						<div className={styles.templateGrid}>
							{filteredTemplates.length === 0 ? <Empty description="暂无模版或组合" /> : filteredTemplates.map((item)=>(
						<Card
							key={`${item.cardType}-${item.id}`}
							size="small"
							title={`${item.cardType === 'template' ? '模版' : '组合'} · ${item.name}`}
							bordered={false}
						>
							{item.cardType === 'template' ? (
								<>
									<div className={styles.cardMeta}>
										<div>格式：{item.format || 'text'}</div>
										<div>版本数：{templateVersions.filter((one)=>one.templateId === item.id).length}</div>
										<div>更新时间：{buildTimestampLabel(item.updatedAt)}</div>
									</div>
									<div className={styles.summaryBlock}>
										{(item.instructionText || item.jsonSchema || item.content || '').slice(0, 260)}
										{(item.instructionText || item.jsonSchema || item.content || '').length > 260 ? '...' : ''}
									</div>
									<div className={styles.cardActions}>
										<Button size="small" onClick={()=>openTemplateEditor(item)} icon={<XQIcon name="edit" />}>编辑</Button>
										<Button size="small" onClick={()=>{
											setPreviewTemplate(item);
											setPreviewDrawerOpen(true);
										}}>预览</Button>
										<Popconfirm title="确定删除这个模版吗？" onConfirm={()=>deleteTemplate(item.id)}>
											<Button size="small" danger icon={<XQIcon name="delete" />}>删除</Button>
										</Popconfirm>
									</div>
									<div className={styles.versionList}>
										{templateVersions.filter((one)=>one.templateId === item.id).slice(0, 5).map((version)=>(
											<div key={version.id} className={styles.versionItem}>
												<span>V{version.versionNumber}</span>
												<Text type="secondary">{buildTimestampLabel(version.updatedAt)}</Text>
												<Button size="small" type="link" onClick={()=>rollbackTemplateVersion(item, version)}>回滚</Button>
											</div>
										))}
									</div>
								</>
							) : (
								<>
									<div className={styles.cardMeta}>
										<div>绑定资料：{Array.isArray(item.defaultMaterialIds) ? item.defaultMaterialIds.length : 0} 份</div>
										<div>默认模型：{item.defaultModel || '未设置'}</div>
										<div>更新时间：{buildTimestampLabel(item.updatedAt)}</div>
									</div>
									<div className={styles.summaryBlock}>
										{item.defaultSystemPrompt || '未设置默认系统提示'}
									</div>
									<div className={styles.cardActions}>
										<Button size="small" onClick={()=>openBundleEditor(item)} icon={<XQIcon name="edit" />}>编辑</Button>
										<Button size="small" onClick={()=>applyBundle(item)}>一键应用</Button>
										<Button size="small" onClick={()=>setReferenceIds((prev)=>uniqueTextList(prev.concat(`bundle:${item.id}`)))}>加入参考</Button>
										<Popconfirm title="确定删除这个组合吗？" onConfirm={()=>deleteBundle(item.id)}>
											<Button size="small" danger icon={<XQIcon name="delete" />}>删除</Button>
										</Popconfirm>
									</div>
								</>
							)}
						</Card>
							))}
						</div>
					</div>
				</div>
			</div>
		);
	}

	function renderSettingsPane(){
		const healthSummary = providerProfiles.reduce((acc, item)=>{
			const key = item.healthStatus === 'healthy' ? 'healthy' : item.healthStatus === 'error' ? 'error' : 'unknown';
			acc[key] += 1;
			return acc;
		}, { healthy: 0, error: 0, unknown: 0 });
		return (
			<div className={styles.paneShell}>
				<div className={styles.paneHeader}>
					<div className={styles.settingsTop}>
						<Search
							allowClear
							placeholder="搜索接口、模型、Base URL"
							style={{ maxWidth: 360 }}
							value={settingKeyword}
							onChange={(e)=>setSettingKeyword(e.target.value)}
						/>
						<Space>
							<Button icon={<XQIcon name="plus" />} type="primary" onClick={()=>openProviderEditor(null)}>新增接口配置</Button>
							<Button icon={<XQIcon name="export" />} onClick={handleExportWorkspaceBackup}>导出备份</Button>
							<Button icon={<XQIcon name="import" />} onClick={handleRestoreWorkspaceBackup}>恢复备份</Button>
						</Space>
					</div>
					<div className={styles.summaryBlock}>
						健康概览：健康 {healthSummary.healthy} / 异常 {healthSummary.error} / 未检测 {healthSummary.unknown}
					</div>
				</div>
				<div className={styles.paneBody}>
					<div className={styles.paneScroll}>
						<div className={styles.settingsGrid}>
							{filteredProfiles.length === 0 ? <Empty description="暂无接口配置" /> : filteredProfiles.map((item)=>(
						<Card key={item.id} size="small" title={item.name || '未命名配置'} bordered={false}>
							<div className={styles.cardMeta}>
								<div>类型：{getProviderDisplayName(item.providerType)}</div>
								<div>协议族：{item.protocolFamily || getProviderProtocolFamily(item.providerType)}</div>
								<div>Base URL：{item.baseUrl || '默认'}</div>
								<div>聊天模型：{normalizeProfileModels(item).length ? normalizeProfileModels(item).join('、') : '未配置'}</div>
								<div>Embedding：{normalizeEmbeddingModels(item).length ? normalizeEmbeddingModels(item).join('、') : '未配置'}</div>
								<div>健康状态：<Tag color={item.healthStatus === 'healthy' ? 'green' : item.healthStatus === 'error' ? 'red' : 'default'}>{item.healthStatus || 'unknown'}</Tag></div>
							</div>
							{item.lastDiagnostics ? (
								<div className={styles.summaryBlock}>
									<div>DNS：{item.lastDiagnostics.dns && item.lastDiagnostics.dns.ok ? `OK / ${item.lastDiagnostics.dns.latencyMs || 0}ms` : `失败 / ${item.lastDiagnostics.dns && item.lastDiagnostics.dns.message ? item.lastDiagnostics.dns.message : ''}`}</div>
									<div>TCP：{item.lastDiagnostics.tcp && item.lastDiagnostics.tcp.ok ? `OK / ${item.lastDiagnostics.tcp.latencyMs || 0}ms` : `失败 / ${item.lastDiagnostics.tcp && item.lastDiagnostics.tcp.message ? item.lastDiagnostics.tcp.message : ''}`}</div>
									<div>HTTP：{item.lastDiagnostics.http && item.lastDiagnostics.http.ok ? `OK / ${item.lastDiagnostics.http.latencyMs || 0}ms` : `失败 / ${item.lastDiagnostics.http && item.lastDiagnostics.http.message ? item.lastDiagnostics.http.message : ''}`}</div>
									<div>失败分类：{item.lastDiagnostics.failureReason || '无'}</div>
									<div>建议：{item.lastDiagnostics.recommendation || '无'}</div>
									<div>错误详情：{item.lastDiagnostics.errorDetail || '无'}</div>
								</div>
							) : null}
							<div className={styles.cardActions}>
								<Button size="small" onClick={()=>openProviderEditor(item)} icon={<XQIcon name="edit" />}>编辑</Button>
								<Button size="small" onClick={()=>fetchModelsAndEmbeddings(item)} icon={<XQIcon name="refresh" />}>拉取模型</Button>
								<Button size="small" onClick={()=>testProfileChat(item)}>测试连接</Button>
								<Button size="small" onClick={()=>runProviderDiagnostics(item)} icon={<XQIcon name="search" />}>连通性诊断</Button>
								<Popconfirm title="确定删除这条接口配置吗？" onConfirm={()=>deleteProvider(item.id)}>
									<Button size="small" danger icon={<XQIcon name="delete" />}>删除</Button>
								</Popconfirm>
							</div>
						</Card>
							))}
						</div>
					</div>
				</div>
			</div>
		);
	}

	const historyColumns = [];
	void historyColumns;

	const previewResult = previewTemplate ? buildTemplatePreview(previewTemplate) : null;

	return (
		<div className={`${styles.root} horosa-aianalysis-page`}>
			<input
				ref={backupRestoreInputRef}
				type="file"
				accept=".zip"
				style={{ display: 'none' }}
				onChange={handleBackupRestoreInputChange}
			/>
			<input
				ref={desktopFileInputRef}
				type="file"
				multiple
				accept=".txt,.md,.markdown,.doc,.docx,.pdf"
				style={{ display: 'none' }}
				onChange={handleDesktopFileInputChange}
			/>
			<input
				ref={desktopFolderInputRef}
				type="file"
				multiple
				accept=".txt,.md,.markdown,.doc,.docx,.pdf"
				webkitdirectory=""
				directory=""
				style={{ display: 'none' }}
				onChange={handleDesktopFolderInputChange}
			/>
			<Spin spinning={workspaceLoading}>
				<Tabs
					className={styles.workspaceTabs}
					tabPosition="right"
					activeKey={innerTab}
					onChange={setInnerTab}
					style={{ height }}
				>
					<TabPane tab={<span>{SECONDARY_TABS[0].icon}分析</span>} key="analysis">
						<div className={styles.pane}>{renderAnalysisPane()}</div>
					</TabPane>
					<TabPane tab={<span>{SECONDARY_TABS[1].icon}历史</span>} key="history">
						<div className={styles.pane}>{renderHistoryPane()}</div>
					</TabPane>
					<TabPane tab={<span>{SECONDARY_TABS[2].icon}资料</span>} key="materials">
						<div className={styles.pane}>{renderMaterialsPane()}</div>
					</TabPane>
					<TabPane tab={<span>{SECONDARY_TABS[3].icon}模版</span>} key="templates">
						<div className={styles.pane}>{renderTemplatesPane()}</div>
					</TabPane>
					<TabPane tab={<span>{SECONDARY_TABS[4].icon}设置</span>} key="settings">
						<div className={styles.pane}>{renderSettingsPane()}</div>
					</TabPane>
				</Tabs>
			</Spin>

			<Modal
				title={editingMaterial ? '编辑资料' : '新建资料'}
				open={materialModalOpen}
				onOk={saveMaterialForm}
				onCancel={()=>{
					setMaterialModalOpen(false);
					setEditingMaterial(null);
				}}
			>
				<Form form={materialForm} layout="vertical">
					<Form.Item name="name" label="资料名称" rules={[{ required: true, message: '请输入资料名称' }]}>
						<Input />
					</Form.Item>
					{materialFolders.length ? (
						<Form.Item name="folderId" label="文件夹">
							<Select allowClear placeholder="不设文件夹">
								{materialFolders.map((item)=><Select.Option key={item.id} value={item.id}>{item.name}</Select.Option>)}
							</Select>
						</Form.Item>
					) : null}
					<Form.Item name="tags" label="标签">
						<Input placeholder="支持逗号分隔" />
					</Form.Item>
					<Form.Item name="extractedText" label="资料内容" rules={[{ required: true, message: '请输入资料内容' }]}>
						<TextArea rows={10} />
					</Form.Item>
				</Form>
			</Modal>

			<Modal
				title={editingTemplate ? '编辑模版' : '新建模版'}
				open={templateModalOpen}
				width={960}
				onOk={saveTemplateForm}
				onCancel={()=>{
					setTemplateModalOpen(false);
					setEditingTemplate(null);
				}}
			>
				<Form form={templateForm} layout="vertical">
					<Form.Item name="name" label="模版名称" rules={[{ required: true, message: '请输入模版名称' }]}>
						<Input />
					</Form.Item>
					<Form.Item name="format" label="模版格式" rules={[{ required: true, message: '请选择模版格式' }]}>
						<Select>
							<Select.Option value="text">文字</Select.Option>
							<Select.Option value="json">JSON</Select.Option>
						</Select>
					</Form.Item>
					<Form.Item shouldUpdate noStyle>
						{({ getFieldValue })=>{
							const format = getFieldValue('format');
							if(format === 'json'){
								return (
									<>
										<Form.Item name="instructionText" label="说明文字">
											<TextArea rows={3} placeholder="可选，用于说明模型应该如何输出 JSON" />
										</Form.Item>
										<Form.Item name="jsonSchema" label="JSON Schema" rules={[{ required: true, message: '请输入 JSON Schema' }]}>
											<MonacoEditor height="240px" defaultLanguage="json" beforeMount={configureMonaco} />
										</Form.Item>
										<Form.Item name="exampleInput" label="示例输入">
											<MonacoEditor height="180px" defaultLanguage="json" beforeMount={configureMonaco} />
										</Form.Item>
										<Form.Item name="exampleOutput" label="示例输出">
											<MonacoEditor height="180px" defaultLanguage="json" beforeMount={configureMonaco} />
										</Form.Item>
									</>
								);
							}
							return (
								<>
									<Form.Item name="instructionText" label="模版内容" rules={[{ required: true, message: '请输入模版内容' }]}>
										<TextArea rows={10} placeholder="支持 {{user_prompt}} / {{source_context}} / {{retrieved_context}} / {{conversation_history}} / {{system_prompt}}" />
									</Form.Item>
									<Form.Item name="exampleInput" label="示例输入">
										<MonacoEditor height="180px" defaultLanguage="json" beforeMount={configureMonaco} />
									</Form.Item>
									<Form.Item name="exampleOutput" label="示例输出">
										<TextArea rows={6} />
									</Form.Item>
								</>
							);
						}}
					</Form.Item>
				</Form>
			</Modal>

			<Modal
				title={editingBundle ? '编辑组合' : '新建组合'}
				open={bundleModalOpen}
				width={720}
				onOk={saveBundleForm}
				onCancel={()=>{
					setBundleModalOpen(false);
					setEditingBundle(null);
				}}
			>
				<Form form={bundleForm} layout="vertical">
					<Form.Item name="name" label="组合名称" rules={[{ required: true, message: '请输入组合名称' }]}>
						<Input />
					</Form.Item>
					<Form.Item name="templateId" label="绑定模版">
						<Select allowClear placeholder="可选">
							{templates.map((item)=>(
								<Select.Option key={item.id} value={item.id}>{item.name}</Select.Option>
							))}
						</Select>
					</Form.Item>
					<Form.Item name="materialIds" label="默认资料">
						<Select mode="multiple" allowClear placeholder="可多选">
							{materials.map((item)=>(
								<Select.Option key={item.id} value={item.id}>{item.name}</Select.Option>
							))}
						</Select>
					</Form.Item>
					<Form.Item name="defaultModelSelection" label="默认模型">
						<Select allowClear placeholder="可选">
							{modelOptions.map((item)=>(
								<Select.Option key={item.value} value={item.value}>{item.label}</Select.Option>
							))}
						</Select>
					</Form.Item>
					<Form.Item name="defaultEmbeddingModel" label="默认 Embedding 模型">
						<Input placeholder="可留空" />
					</Form.Item>
					<Form.Item name="defaultSystemPrompt" label="默认系统提示词">
						<TextArea rows={5} />
					</Form.Item>
					<Form.Item name="defaultRetrievalMode" label="默认检索策略">
						<Select>
							{RETRIEVAL_OPTIONS.map((item)=><Select.Option key={item.value} value={item.value}>{item.label}</Select.Option>)}
						</Select>
					</Form.Item>
				</Form>
			</Modal>

			<Modal
				title="生效 API"
				open={providerSwitchModalOpen}
				width={720}
				footer={null}
				bodyStyle={{ maxHeight: 'calc(100vh - 220px)', overflowY: 'auto' }}
				onCancel={()=>setProviderSwitchModalOpen(false)}
			>
				{providerProfiles.length ? (
					<div className={styles.providerSwitchList}>
						{providerProfiles.map((profile)=>{
							const models = normalizeProfileModels(profile);
							const isCurrent = activeProviderProfile && activeProviderProfile.id === profile.id;
							const displayName = profile.name || getProviderDisplayName(profile.providerType);
							return (
								<div
									key={profile.id}
									className={[
										styles.providerSwitchItem,
										isCurrent ? styles.providerSwitchItemActive : '',
									].filter(Boolean).join(' ')}
								>
									<div className={styles.providerSwitchMain}>
										<div className={styles.providerSwitchTitle}>
											<strong>{displayName}</strong>
											{isCurrent ? <Tag color="blue">当前</Tag> : null}
											{profile.enabled === false ? <Tag>未启用</Tag> : <Tag color="green">已启用</Tag>}
										</div>
										<div className={styles.providerSwitchMeta}>
											<span>类型：{getProviderDisplayName(profile.providerType)}</span>
											<span>协议族：{profile.protocolFamily || getProviderProtocolFamily(profile.providerType)}</span>
											<span>模型：{models[0] || '未配置'}</span>
										</div>
										{profile.baseUrl ? (
											<div className={styles.providerSwitchUrl}>{profile.baseUrl}</div>
										) : null}
									</div>
									<Button
										type="primary"
										icon={<XQIcon name="edit" />}
										onClick={()=>{
											setProviderSwitchModalOpen(false);
											openProviderEditor(profile);
										}}
									>
										编辑
									</Button>
								</div>
							);
						})}
					</div>
				) : (
					<Empty description="暂无接口配置" />
				)}
			</Modal>

			<Modal
				title={editingProvider ? '编辑接口配置' : '新增接口配置'}
				open={providerModalOpen}
				width={720}
				bodyStyle={{ maxHeight: 'calc(100vh - 220px)', overflowY: 'auto' }}
				onOk={saveProviderForm}
				onCancel={()=>{
					setProviderModalOpen(false);
					setProviderAdvancedOpen(false);
					setEditingProvider(null);
				}}
			>
				<Form
					form={providerForm}
					layout="vertical"
					onValuesChange={(changedValues)=>{
						if(changedValues.providerType){
							applyProviderPresetToForm(changedValues.providerType);
						}
					}}
				>
					<Form.Item name="name" label="配置名称" rules={[{ required: true, message: '请输入配置名称' }]}>
						<Input />
					</Form.Item>
					<Form.Item name="providerType" label="供应商预设" rules={[{ required: true, message: '请选择接口类型' }]}>
						<Select>
							{PROVIDER_OPTIONS.map((item)=>(
								<Select.Option key={item.value} value={item.value}>{item.label}</Select.Option>
							))}
						</Select>
					</Form.Item>
					<Form.Item name="apiKey" label="API Key">
						<Input type="password" placeholder="留空表示不设置" />
					</Form.Item>
					<Form.Item name="baseUrl" label="Base URL">
						<Input />
					</Form.Item>
					<Form.Item shouldUpdate noStyle>
						{({ getFieldValue })=>(
							<div className={styles.cardMeta}>
								<div>协议族：{getProviderProtocolFamily(getFieldValue('providerType') || 'openai')}</div>
							</div>
						)}
					</Form.Item>
					<div className={styles.providerAdvancedToggle}>
						<Button
							className={styles.providerAdvancedButton}
							icon={<XQIcon name="sliders" />}
							onClick={()=>setProviderAdvancedOpen((prev)=>!prev)}
						>
							{providerAdvancedOpen ? '收起高级参数' : '展开高级参数'}
						</Button>
					</div>
					{providerAdvancedOpen ? (
						<div className={styles.providerAdvancedPanel}>
							<Form.Item name="manualModels" label="聊天模型列表">
								<TextArea rows={4} />
							</Form.Item>
							<Form.Item name="embeddingModels" label="Embedding 模型列表">
								<TextArea rows={3} />
							</Form.Item>
							<Form.Item name="requestTimeoutMs" label="请求超时（毫秒）">
								<Input />
							</Form.Item>
							<Form.Item name="extraHeadersText" label="额外请求头（JSON 对象）">
								<MonacoEditor height="140px" defaultLanguage="json" beforeMount={configureMonaco} />
							</Form.Item>
							<Form.Item name="extraBodyText" label="额外请求体（JSON 对象）">
								<MonacoEditor height="140px" defaultLanguage="json" beforeMount={configureMonaco} />
							</Form.Item>
							<Form.Item name="providerOptionsText" label="补充高级参数（JSON）">
								<MonacoEditor height="160px" defaultLanguage="json" beforeMount={configureMonaco} />
							</Form.Item>
						</div>
					) : null}
					<Form.Item shouldUpdate noStyle>
						{({ getFieldValue })=>{
							const providerType = getFieldValue('providerType');
							if(providerType === 'anthropic'){
								return (
									<>
										<Form.Item name="anthropicApiVersion" label="Anthropic API Version">
											<Input placeholder="默认 2023-06-01" />
										</Form.Item>
										<Form.Item name="anthropicMaxTokens" label="Anthropic max_tokens">
											<Input placeholder="如 2048" />
										</Form.Item>
										<Form.Item name="anthropicThinkingBudget" label="Thinking Budget">
											<Input placeholder="如 1024" />
										</Form.Item>
										<Form.Item name="anthropicTopP" label="Anthropic top_p">
											<Input placeholder="如 0.9" />
										</Form.Item>
										<Form.Item name="anthropicTopK" label="Anthropic top_k">
											<Input placeholder="如 40" />
										</Form.Item>
									</>
								);
							}
							if(providerType === 'gemini'){
								return (
									<>
										<Form.Item name="geminiGenerationConfigText" label="Gemini generationConfig">
											<MonacoEditor height="180px" defaultLanguage="json" beforeMount={configureMonaco} />
										</Form.Item>
										<Form.Item name="geminiSafetySettingsText" label="Gemini safetySettings">
											<MonacoEditor height="180px" defaultLanguage="json" beforeMount={configureMonaco} />
										</Form.Item>
									</>
								);
							}
							if(providerType === 'ollama'){
								return (
									<>
										<Form.Item name="ollamaKeepAlive" label="Ollama keep_alive">
											<Input placeholder="如 5m" />
										</Form.Item>
										<Form.Item name="ollamaNumCtx" label="Ollama num_ctx">
											<Input placeholder="如 8192" />
										</Form.Item>
										<Form.Item name="ollamaNumPredict" label="Ollama num_predict">
											<Input placeholder="如 1024" />
										</Form.Item>
										<Form.Item name="ollamaTopK" label="Ollama top_k">
											<Input placeholder="如 40" />
										</Form.Item>
										<Form.Item name="ollamaTopP" label="Ollama top_p">
											<Input placeholder="如 0.9" />
										</Form.Item>
										<Form.Item name="ollamaRepeatPenalty" label="Ollama repeat_penalty">
											<Input placeholder="如 1.1" />
										</Form.Item>
									</>
								);
							}
							return null;
						}}
					</Form.Item>
					<Form.Item name="enabled" label="启用此配置" valuePropName="checked">
						<Switch />
					</Form.Item>
				</Form>
			</Modal>

			<Drawer
				title={previewTemplate ? `模版预览 · ${previewTemplate.name}` : '模版预览'}
				open={previewDrawerOpen}
				width={520}
				onClose={()=>{
					setPreviewDrawerOpen(false);
					setPreviewTemplate(null);
				}}
			>
				{previewTemplate && previewResult ? (
					<div>
						<div className={styles.previewMeta}>
							<Tag>{previewTemplate.format}</Tag>
							<Tag>版本 {templateVersions.filter((item)=>item.templateId === previewTemplate.id).length}</Tag>
						</div>
						<pre className={styles.previewCode}>{previewResult.text}</pre>
						{previewResult.errors && previewResult.errors.length ? (
							<div className={styles.previewErrors}>
								<Title level={5}>Schema 校验</Title>
								{previewResult.errors.map((item, idx)=>(
									<div key={idx} className={styles.errorLine}>{item.message || JSON.stringify(item)}</div>
								))}
							</div>
						) : (
							<Text type="secondary">Schema 校验通过</Text>
						)}
					</div>
				) : null}
			</Drawer>
		</div>
	);
}

export default AIAnalysisMain;
