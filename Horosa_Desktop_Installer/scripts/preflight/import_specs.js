#!/usr/bin/env node
// 发布前自检的「导入了某名」判据(lib.sh 的 pf_imports 调它):按 AST 读 import,与同一条里还有哪些名字、先后、换行、注释无关。
//   node import_specs.js <前端根 astrostudyui> <文件> <import 语句>
//   import 语句照源码写(例:import { a, b } from './x';),逐个名字核「该文件(登记过的门面按全集逐文件)从同一来源导入了它(本地名相同)」。
//   全有 → 退出 0;缺 → 每缺一个打印一行「来源 名字」并退出 1;语句本身读不出 → 退出 2。
// 解析与测试同一份助手:astrostudyui/src/utils/__tests__/helpers/importSpecs.js(文件读不全 / 有语法错也尽量读完)。
const fs = require('fs');
const path = require('path');

const [, , uiRoot, file, stmt] = process.argv;
if(!uiRoot || !file || !stmt){
	console.error('用法: node import_specs.js <astrostudyui 目录> <文件> <import 语句>');
	process.exit(2);
}
const helpers = path.join(path.resolve(uiRoot), 'src', 'utils', '__tests__', 'helpers');
const { importBindings } = require(path.join(helpers, 'importSpecs'));
const { sourceSetFiles } = require(path.join(helpers, 'sourceSet'));

let want;
try{ want = importBindings(stmt, { tolerant: true }); }catch(e){ want = []; }
if(!want.length){
	console.error(`读不出 import 语句:${stmt}`);
	process.exit(2);
}
let have = [];
try{
	sourceSetFiles(file).forEach((f)=>{
		if(!fs.existsSync(f)){ return; }
		try{ have = have.concat(importBindings(fs.readFileSync(f, 'utf8'), { tolerant: true })); }catch(e){ /* 读不出的一份当没有导入 */ }
	});
}catch(e){ have = []; }
const missing = want.filter((w)=>!have.some((h)=>h.source === w.source && h.imported === w.imported && h.local === w.local));
missing.forEach((m)=>console.log(`${m.source} ${m.imported === m.local ? m.imported : `${m.imported} as ${m.local}`}`));
process.exit(missing.length ? 1 : 0);
