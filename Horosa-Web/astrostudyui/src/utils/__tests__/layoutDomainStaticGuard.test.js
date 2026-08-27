// [版面域根治] 静态复发哨兵:任何「视口读数 ÷ 缩放值」的写法一律判红。
//
// 为什么必须有静态哨兵:行为测试只能覆盖今天已知的那几处消费点;真正的复发形态是
// 「半年后有人为新页面又写了一遍 innerHeight/zoom」,而那处没有任何测试会经过。
// 2026-08-27 的事故就是这个形状,一次同时坑了主工作区、奇门、三式合一、启动页四处。
//
// 判红后的两条正路(任选其一,都要留下判定依据):
//   ① 需要布局域尺寸 ⇒ 直接量容器(el.clientHeight)或 zoomDomain.measureLayoutViewport();
//   ② 该处确实要物理域数值(如与鼠标 rect 坐标同域比较)⇒ 进 EXEMPT 并写明为何同域。
// 严禁只为「让测试变绿」而加豁免 —— 理由必须能自证。
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SRC = path.resolve(__dirname, '..', '..');
// 壳内三页(启动/诊断/偏好)。这次事故里它们的密度探测犯了同样的错,却因为不在任何
// 扫描范围内而无人发觉 —— 所以哨兵必须把它们一并纳入。
const SHELL_WEB = path.resolve(SRC, '..', '..', '..', 'Horosa_Desktop_Installer', 'web');

const EXEMPT = [];

// 「视口读数 ÷ 标识符/调用」。除以数字字面量(如 /2 居中)是正常算术,不在此列。
const PATTERN = '(clientHeight|clientWidth|innerHeight|innerWidth)[[:space:]]*/[[:space:]]*[a-zA-Z_$]';

function scanDir(dir, includes){
	if(!fs.existsSync(dir)){ return []; }
	let out = '';
	try{
		// -a:仓内曾有裸 NUL 字节导致 grep 判二进制而整文件失明(FL 已落账)
		out = execSync(`grep -rnaE ${includes} ${JSON.stringify(PATTERN)} .`, { cwd: dir, encoding: 'utf8' });
	}catch(e){
		out = e.stdout || '';   // grep 无命中 exit 1
	}
	return out.split('\n').filter(Boolean).map((line) => {
		const m = /^([^:]+):(\d+):(.*)$/.exec(line);
		return m ? { file: m[1], line: Number(m[2]), text: m[3] } : null;
	}).filter(Boolean);
}

// 注释行不算违规(踩过两次:哨兵是纯文本 grep,不分代码与注释)
function isComment(text){
	return /^\s*(\/\/|\*|\/\*)/.test(text);
}

describe('T1 哨兵判别力自证(绿本身不是证据)', () => {
	it('扫描器在人造违规上必须判红', () => {
		const tmp = path.join(SRC, 'utils', '__tests__', '__probe_layout_domain__.js');
		fs.writeFileSync(tmp, 'const h = window.innerHeight / shellZoom;\nexport default h;\n');
		try{
			const hits = scanDir(SRC, "--include='*.js'").filter((h) => h.file.indexOf('__probe_layout_domain__') >= 0);
			expect(hits.length).toBeGreaterThan(0);
		}finally{
			fs.unlinkSync(tmp);
		}
	});

	it('扫描器确实看得见文件(防 grep 失效导致空集假绿)', () => {
		const any = scanDir(SRC, "--include='*.js'");
		expect(Array.isArray(any)).toBe(true);
		// 至少要能读到源码树本身
		expect(fs.existsSync(path.join(SRC, 'utils', 'zoomDomain.js'))).toBe(true);
	});
});

describe('T2 主应用:零「视口读数 ÷ 缩放」', () => {
	it('🔴 src 全树无此形状(注释除外)', () => {
		const bad = scanDir(SRC, "--include='*.js'")
			.filter((h) => h.file.indexOf('__tests__') < 0)
			.filter((h) => !isComment(h.text))
			.filter((h) => !EXEMPT.some((e) => h.file.indexOf(e) >= 0))
			.map((h) => `  ${h.file}:${h.line}  ${h.text.trim().slice(0, 78)}`);
		expect(bad.join('\n')).toBe('');
	});
});

describe('T3 壳内三页:同一标准', () => {
	// 形态自适应:该目录在精简发行形态下可能不存在,缺席跳过而非判红。
	const present = fs.existsSync(SHELL_WEB);

	it('🔴 启动/诊断/偏好三页无此形状(注释除外)', () => {
		if(!present){ return; }
		const bad = scanDir(SHELL_WEB, "--include='*.js' --include='*.css'")
			.filter((h) => !isComment(h.text))
			.map((h) => `  web/${h.file}:${h.line}  ${h.text.trim().slice(0, 78)}`);
		expect(bad.join('\n')).toBe('');
	});

	it('本仓若含壳内页,密度探测必须是直接量(防改回「÷ 声明缩放」)', () => {
		if(!present){ return; }
		const appJs = path.join(SHELL_WEB, 'app.js');
		if(!fs.existsSync(appJs)){ return; }
		const src = fs.readFileSync(appJs, 'utf8');
		expect(src.indexOf('function layoutSpace') >= 0).toBe(true);
		expect(src.indexOf('position:fixed;left:0;top:0;right:0;bottom:0') >= 0).toBe(true);
	});
});
