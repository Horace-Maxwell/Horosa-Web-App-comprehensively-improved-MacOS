import { ServerRoot } from '../../utils/constants';

export const KENTANG_SERVICE_CONFIG = {
	taiyi: {
		engine: 'kintaiyi',
		path: 'taiyi',
		queryKeys: ['taiyiSrv', 'kintaiyiSrv'],
		defaultLocalPort: 8898,
	},
	jinkou: {
		engine: 'kinjinkou',
		path: 'jinkou',
		queryKeys: ['jinkouSrv', 'kinjinkouSrv'],
		defaultLocalPort: 8898,
	},
	qimen: {
		engine: 'kinqimen',
		path: 'qimen',
		queryKeys: ['qimenSrv', 'kinqimenSrv'],
		defaultLocalPort: 8898,
	},
	wangji: {
		engine: 'kinwangji',
		path: 'wangji',
		queryKeys: ['wangjiSrv', 'huangjiSrv', 'kinwangjiSrv'],
		defaultLocalPort: 8898,
	},
	wuzhao: {
		engine: 'kinwuzhao',
		path: 'wuzhao',
		queryKeys: ['wuzhaoSrv', 'kinwuzhaoSrv'],
		defaultLocalPort: 8898,
	},
	taixuan: {
		engine: 'taixuanshifa',
		path: 'taixuan',
		queryKeys: ['taixuanSrv', 'taixuanshifaSrv'],
		defaultLocalPort: 8895,
	},
	jingjue: {
		engine: 'jingjue',
		path: 'jingjue',
		queryKeys: ['jingjueSrv'],
		defaultLocalPort: 8894,
	},
	shenyishu: {
		engine: 'shenyishu',
		path: 'shenyishu',
		queryKeys: ['shenyishuSrv'],
		defaultLocalPort: 8893,
	},
	shaozi: {
		engine: 'kinastro-shaozi',
		path: 'shaozi',
		queryKeys: ['shaoziSrv', 'shusuanSrv', 'kinastroSrv'],
		defaultLocalPort: 8892,
	},
	tieban: {
		engine: 'kinastro-tieban',
		path: 'tieban',
		queryKeys: ['tiebanSrv', 'shusuanSrv', 'kinastroSrv'],
		defaultLocalPort: 8892,
	},
	fendjing: {
		engine: 'kinastro-fendjing',
		path: 'fendjing',
		queryKeys: ['fendjingSrv', 'guiguSrv', 'shusuanSrv', 'kinastroSrv'],
		defaultLocalPort: 8892,
	},
	beiji: {
		engine: 'kinastro-beiji',
		path: 'beiji',
		queryKeys: ['beijiSrv', 'shusuanSrv', 'kinastroSrv'],
		defaultLocalPort: 8892,
	},
	nanji: {
		engine: 'kinastro-nanji',
		path: 'nanji',
		queryKeys: ['nanjiSrv', 'shusuanSrv', 'kinastroSrv'],
		defaultLocalPort: 8892,
	},
	chunzi: {
		engine: 'kinastro-chunzi',
		path: 'chunzi',
		queryKeys: ['chunziSrv', 'shusuanSrv', 'kinastroSrv'],
		defaultLocalPort: 8892,
	},
	xianqin: {
		engine: 'kinastro-xianqin',
		path: 'xianqin',
		queryKeys: ['xianqinSrv', 'yanqinSrv', 'kinastroSrv'],
		defaultLocalPort: 8892,
	},
	cetian: {
		engine: 'kinastro-cetian',
		path: 'cetian',
		queryKeys: ['cetianSrv', 'mingOtherSrv', 'kinastroSrv'],
		defaultLocalPort: 8892,
	},
	qizhengkin: {
		engine: 'kinastro-qizheng',
		path: 'qizhengkin',
		queryKeys: ['qizhengKinSrv', 'qizhengSrv', 'kinastroSrv'],
		defaultLocalPort: 8892,
	},
};

const COMMON_QUERY_KEYS = ['kentangSrv', 'kinSrv'];

export function isValidHttpUrl(value){
	return !!(value && /^https?:\/\/.+/i.test(`${value}`));
}

export function replacePort(url, port){
	try{
		const u = new URL(url);
		u.port = `${port}`;
		return u.toString().replace(/\/$/, '');
	}catch(e){
		return url;
	}
}

function queryValue(keys){
	if(typeof window === 'undefined'){
		return '';
	}
	try{
		const params = new URLSearchParams(window.location.search || '');
		for(let i=0; i<keys.length; i++){
			const val = params.get(keys[i]);
			if(isValidHttpUrl(val)){
				return val.replace(/\/$/, '');
			}
		}
	}catch(e){}
	return '';
}

export function resolveKentangServiceRoot(moduleKey){
	const config = KENTANG_SERVICE_CONFIG[moduleKey] || {};
	const explicit = queryValue([...(config.queryKeys || []), ...COMMON_QUERY_KEYS]);
	if(explicit){
		return explicit;
	}
	if(/:9999(?:\/)?$/i.test(ServerRoot)){
		return replacePort(ServerRoot, config.defaultLocalPort || 8898);
	}
	return ServerRoot;
}

export function buildKentangEndpoint(moduleKey, action){
	const config = KENTANG_SERVICE_CONFIG[moduleKey] || {};
	const path = config.path || moduleKey;
	const route = action || 'pan';
	return `${resolveKentangServiceRoot(moduleKey)}/${path}/${route}`;
}
