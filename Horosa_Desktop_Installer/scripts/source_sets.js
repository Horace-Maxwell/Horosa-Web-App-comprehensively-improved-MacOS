// 前端拆成子模块的大文件:检查器按「子模块 + 门面」全集读源码。
//
// AIAnalysisMain.js / aiExport.js / aiAnalysisContext.js / LiuRengMain.js / PlanetariumBabylon.js / IndiaChartMain.js / GuoLaoChartMain.js 原先各是一份大文件,
// 现按职责拆进子目录,原路径留作门面(对外导入路径不变);全站样式 layouts/app.less 按区段拆进 layouts/app/。
// 登记表单源 = Horosa-Web/astrostudyui/scripts/source-sets.json(jest 的 helpers/sourceSet.js、发布前自检的 pf_src_set 读同一份)。
//   sourceSetFiles(全路径) —— 路径是某个 astrostudyui/src 下登记过的门面:返回 [子模块…(登记次序), 门面](登记表取该 astrostudyui 自己的那份);
//                             其余路径只含它自己。
//   readSourceSet(全路径)  —— 按上面的清单把内容首尾相接成一份文本(拼出来的是文本,要解析 AST 的检查按 sourceSetFiles 逐个文件解析);
//                             样式门面(layouts/app.less)则把门面里的区段 @import 原位展开(= 拆分前的整份样式)。
// Python 计算引擎的门面(登记表 pySets,路径相对 Horosa-Web/astropy:perchart.py / india/jyotish_engine.py / astroextra.py)同样处理:
//   路径尾部是 …/astropy/<门面> 时,全集 = [子模块…(登记次序), 门面](登记表取该仓 Horosa-Web/astrostudyui/scripts 下那份)。
const fs = require('fs');
const path = require('path');

const _manifests = new Map();
function manifestFor(uiRoot){
	if(!_manifests.has(uiRoot)){
		let sets = null;
		try{ sets = JSON.parse(fs.readFileSync(path.join(uiRoot, 'scripts', 'source-sets.json'), 'utf8')).sets || null; }catch(e){ sets = null; }
		_manifests.set(uiRoot, sets);
	}
	return _manifests.get(uiRoot);
}

const _pyManifests = new Map();
function pyManifestFor(astropyRoot){
	if(!_pyManifests.has(astropyRoot)){
		let sets = null;
		try{ sets = JSON.parse(fs.readFileSync(path.join(astropyRoot, '..', 'astrostudyui', 'scripts', 'source-sets.json'), 'utf8')).pySets || null; }catch(e){ sets = null; }
		_pyManifests.set(astropyRoot, sets);
	}
	return _pyManifests.get(astropyRoot);
}

function sourceSetFiles(full){
	const abs = path.resolve(`${full}`);
	const norm = abs.split(path.sep).join('/');
	const pyAt = norm.lastIndexOf('/astropy/');
	if(pyAt >= 0 && /\.py$/.test(norm)){
		const pyRoot = abs.slice(0, pyAt + 8);
		const pySet = (pyManifestFor(pyRoot) || {})[norm.slice(pyAt + 9)];
		if(pySet){ return [...pySet.files.map((f)=>path.join(pyRoot, pySet.dir, f)), abs]; }
		return [abs];
	}
	const at = norm.lastIndexOf('/src/');
	if(at < 0){ return [abs]; }
	const uiRoot = abs.slice(0, at);
	const rel = norm.slice(at + 5);
	const sets = manifestFor(uiRoot);
	const set = sets && sets[rel];
	if(!set){ return [abs]; }
	return [...set.files.map((f)=>path.join(uiRoot, 'src', set.dir, f)), abs];
}

// 样式门面(.less):门面里指向登记区段的 `@import './…';` 行原位换成区段全文(= 拆分前的整份样式)
function expandLessFacade(facadeAbs, partAbs){
	const parts = new Set(partAbs);
	return fs.readFileSync(facadeAbs, 'utf8').split('\n').map((ln)=>{
		const m = ln.match(/^@import '(\.\/[^']+\.less)';\s*$/);
		const p = m ? path.join(path.dirname(facadeAbs), m[1]) : null;
		return p && parts.has(p) ? fs.readFileSync(p, 'utf8').replace(/\n$/, '') : ln;
	}).join('\n');
}

function readSourceSet(full){
	const files = sourceSetFiles(full);
	if(files.length > 1 && /\.less$/.test(full)){ return expandLessFacade(files[files.length - 1], files.slice(0, -1)); }
	return files.map((f)=>fs.readFileSync(f, 'utf8')).join('');
}

module.exports = { sourceSetFiles, readSourceSet };
