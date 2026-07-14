// 高德地图 CSP 白名单完整性守卫（制度化·FL 装机专发类 2026-07-13）。
// 病根：打包 CSP 未放行 AMap 域 → macOS WKWebView 严格执行 → 地图白屏；preview 无 CSP、
// Windows WebView2 宽松执行故 dev/Win 假绿，唯 Mac 装机版暴露。铁律：前端依赖的每个外部域，
// 打包 CSP 必须放行。此测与 release_preflight.sh [128] 双护（jest 每次跑=早警，preflight=发布硬闸）。
import fs from 'fs';
import path from 'path';
import { AMapKey } from '../../../utils/constants';

// 向上搜 tauri.conf.json（对仓库布局稳健；缺失则跳过，不误伤 public 单仓 jest）。
function findTauriConf(start) {
	let dir = start;
	for (let i = 0; i < 8; i++) {
		const p = path.join(dir, 'Horosa_Desktop_Installer', 'src-tauri', 'tauri.conf.json');
		if (fs.existsSync(p)) { return p; }
		const up = path.dirname(dir);
		if (up === dir) { break; }
		dir = up;
	}
	return null;
}

function parseCsp(csp) {
	const dirs = {};
	`${csp || ''}`.split(';').map((s)=> s.trim()).filter(Boolean).forEach((seg)=>{
		const p = seg.split(/\s+/);
		dirs[p[0]] = p.slice(1);
	});
	return dirs;
}
function eff(dirs, d) { return dirs[d] || dirs['default-src'] || []; }
function allows(sources, host) {
	return (sources || []).some((s)=>{
		if (s === `https://${host}`) { return true; }
		if (s.startsWith('https://*.')) { const suf = s.slice('https://*'.length); return host.endsWith(suf) && host !== suf.slice(1); }
		return false;
	});
}

const confPath = findTauriConf(__dirname);

describe('高德地图 CSP 白名单完整性（Mac WKWebView 严格执行 → 缺则装机白屏）', () => {
	test('前端确实用 AMap（AMapKey 非空）—— 故 CSP 必须放行', () => {
		expect(typeof AMapKey === 'string' && AMapKey.length > 0).toBe(true);
	});

	// 实测 AMap JSAPI 2.0 用到的域：webapi(脚本/UI)、restapi(地名搜索/逆地理)、jsapi(瓦片资源)。
	(confPath ? test : test.skip)('打包 CSP 放行全部实测 AMap 域(script/connect/img) + worker blob', () => {
		const conf = JSON.parse(fs.readFileSync(confPath, 'utf8'));
		const dirs = parseCsp(conf.app.security.csp);
		['webapi.amap.com', 'restapi.amap.com', 'jsapi.amap.com'].forEach((h)=>{
			['script-src', 'connect-src', 'img-src'].forEach((d)=>{
				expect({ host: h, dir: d, allowed: allows(eff(dirs, d), h) }).toEqual({ host: h, dir: d, allowed: true });
			});
		});
		// AMap 2.0 WebGL 瓦片解码走 blob worker，WKWebView 亦严格 gate worker-src。
		expect(eff(dirs, 'worker-src')).toContain('blob:');
	});

	(confPath ? test : test.skip)('放行外部域后仍受一次性同意 gate（隐私锚不失守）', () => {
		const mapV2 = fs.readFileSync(path.join(__dirname, '..', 'MapV2.js'), 'utf8');
		expect(mapV2).toMatch(/hasMapConsent/);
	});
});
