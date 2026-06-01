#!/usr/bin/env node

const DEFAULT_URL = 'http://127.0.0.1:18000/index.html?srv=http%3A%2F%2F127.0.0.1%3A19999#/';

async function main(){
	const url = process.env.PLANETARIUM_URL || DEFAULT_URL;
	let chromium = null;
	try{
		({ chromium } = await import('playwright'));
	}catch(err){
		console.log('planetarium perf smoke skipped: install playwright to run browser timing checks.');
		console.log(`target: ${url}`);
		return;
	}

	const browser = await chromium.launch({ headless: true });
	const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
	const started = Date.now();
	await page.goto(url, { waitUntil: 'networkidle' });
	const before = await page.evaluate(()=>({
		canvasCount: document.querySelectorAll('canvas').length,
		hasBabylon: Array.from(document.scripts).some((s)=>s.src.indexOf('/vendor/babylon/babylon.js') >= 0),
	}));
	await page.getByText('知道了').click({ timeout: 1000 }).catch(()=>{});
	await page.locator('button').filter({ hasText: '占星' }).click();
	await page.locator('button').filter({ hasText: /^天文馆$/ }).click();
	await page.waitForFunction(()=>document.body.innerText.indexOf('恒星') >= 0 && document.querySelector('.planetarium-canvas'), { timeout: 20000 });
	await page.waitForTimeout(2500);
	const active = await page.evaluate(()=>({
		text: document.body.innerText,
		canvasCount: document.querySelectorAll('canvas').length,
		hasBabylon: Array.from(document.scripts).some((s)=>s.src.indexOf('/vendor/babylon/babylon.js') >= 0),
		perfLog: window.__horosaPlanetariumPerf || [],
		memory: performance && performance.memory ? {
			usedJSHeapSize: performance.memory.usedJSHeapSize,
			totalJSHeapSize: performance.memory.totalJSHeapSize,
		} : null,
	}));
	await page.locator('button').filter({ hasText: '导航' }).click();
	await page.getByText('占星').last().click();
	await page.waitForTimeout(1200);
	const afterLeave = await page.evaluate(()=>({
		canvasCount: document.querySelectorAll('canvas').length,
		hasPlanetariumCanvas: !!document.querySelector('.planetarium-canvas'),
		perfLog: window.__horosaPlanetariumPerf || [],
	}));
	await browser.close();

	const summary = {
		url,
		totalMs: Date.now() - started,
		before,
		active: {
			canvasCount: active.canvasCount,
			hasBabylon: active.hasBabylon,
			hasFailure: active.text.indexOf('天文馆数据载入失败') >= 0,
			hasStars: /恒星\s+\d+/.test(active.text),
			perfLog: active.perfLog,
			memory: active.memory,
		},
		afterLeave,
	};
	console.log(JSON.stringify(summary, null, 2));
	if(summary.active.hasFailure || before.canvasCount !== 0 || !active.hasBabylon || active.canvasCount < 1 || afterLeave.canvasCount !== 0){
		process.exit(1);
	}
}

main().catch((err)=>{
	console.error(err);
	process.exit(1);
});
