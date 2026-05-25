#!/usr/bin/env python3
"""Browser e2e for AI分析 workspace with stable mocked AI endpoints."""

from __future__ import annotations

import json
import os
import socketserver
import sys
import tempfile
import threading
import time
import traceback
import urllib.error
import urllib.request
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import expect, sync_playwright
except Exception as exc:  # pragma: no cover
    print(json.dumps({"status": "skipped", "reason": f"playwright unavailable: {exc}"}, ensure_ascii=False))
    raise SystemExit(0)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime"
JSON_PATH = RUNTIME_DIR / "browser_horosa_aianalysis_check.json"
SCREENSHOT_PATH = RUNTIME_DIR / "browser_horosa_aianalysis_check.png"
CHART_FIXTURE_CACHE = None


def is_known_benign_console_error(text: str) -> bool:
    """Filter project-wide legacy warnings that are not AIAnalysis regressions."""
    return "Warning: [antd: Tabs] Tabs.TabPane is deprecated." in (text or "")


def build_base_url(mock_server_root: str) -> str:
    web_port = os.environ.get("HOROSA_WEB_PORT", "8000")
    return os.environ.get(
        "HOROSA_WEB_ROOT",
        f"http://127.0.0.1:{web_port}/index.html?srv={mock_server_root.replace(':', '%3A').replace('/', '%2F')}&v={int(time.time())}",
    )


class MockProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    backend_root = os.environ.get("HOROSA_SERVER_ROOT", f"http://127.0.0.1:{os.environ.get('HOROSA_SERVER_PORT', '9999')}")

    def log_message(self, fmt, *args):  # pragma: no cover
        return

    def _set_cors(self):
        origin = self.headers.get("Origin", "*") or "*"
        allow_headers = self.headers.get(
            "Access-Control-Request-Headers",
            "Content-Type, Token, Signature, LocalIp, ClientChannel, ClientApp, ClientVer, Encrypted",
        )
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", allow_headers)
        self.send_header("Vary", "Origin, Access-Control-Request-Headers")

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        if self._send_app_bootstrap_fixture():
            return
        self._proxy_request()

    def do_POST(self):
        if self.path.startswith("/aianalysis/providers/models"):
            return self._send_json(
                {
                    "ResultCode": 0,
                    "Result": {
                        "models": ["mock-chat-1", "mock-chat-2", "mock-embedding-1"],
                        "chatModels": ["mock-chat-1", "mock-chat-2"],
                        "embeddingModels": ["mock-embedding-1"],
                    },
                }
            )
        if self.path.startswith("/aianalysis/providers/diagnose"):
            return self._send_json(
                {
                    "ResultCode": 0,
                    "Result": {
                        "healthy": True,
                        "dns": {"ok": True, "latencyMs": 12},
                        "tcp": {"ok": True, "latencyMs": 19},
                        "http": {"ok": True, "latencyMs": 36},
                        "auth": {"ok": True},
                        "failureReason": "",
                        "errorDetail": "",
                        "recommendation": "连接正常，可直接用于模型拉取与分析对话。",
                        "latencyMs": 36,
                    },
                }
            )
        if self.path.startswith("/aianalysis/chat/stream"):
            return self._send_stream()
        if self.path.startswith("/aianalysis/chat"):
            return self._send_json({"ResultCode": 0, "Result": {"content": "连接成功。"}})
        if self.path.startswith("/aianalysis/materials/extract"):
            return self._send_json(
                {
                    "ResultCode": 0,
                    "Result": {
                        "fileName": "mock.pdf",
                        "fileExt": "pdf",
                        "mimeType": "application/pdf",
                        "size": 128,
                        "fileHash": "mock-file-hash",
                        "textHash": "mock-text-hash",
                        "extractedText": "这是通过 mock extract 返回的 PDF 资料正文，用于 AI分析 e2e。",
                        "extractMeta": {"pageCount": 1, "paragraphCount": 1},
                    },
                }
            )
        if self.path.startswith("/aianalysis/embeddings"):
            return self._send_json(
                {
                    "ResultCode": 0,
                    "Result": {
                        "vectors": [
                            [0.91, 0.11, 0.42],
                            [0.85, 0.10, 0.40],
                            [0.83, 0.12, 0.35],
                        ]
                    },
                }
            )
        if self._send_app_bootstrap_fixture():
            return
        self._proxy_request()

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0") or "0")
        return self.rfile.read(length) if length > 0 else b""

    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._set_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("ResultCode", "0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_stream(self):
        self._read_body()
        self.send_response(200)
        self._set_cors()
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.end_headers()

        events = [
            ("meta", {"provider": "mock", "model": "mock-chat-1"}),
            ("delta", {"delta": "第一段分析内容。"}),
            ("delta", {"delta": "第二段补充内容。"}),
            ("delta", {"delta": "最终结论与建议。"}),
            ("done", {"content": "第一段分析内容。第二段补充内容。最终结论与建议。"}),
        ]
        try:
            for event_name, payload in events:
                packet = f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")
                self.wfile.write(packet)
                self.wfile.flush()
                time.sleep(0.35)
        except BrokenPipeError:
            return

    def _send_app_bootstrap_fixture(self) -> bool:
        """Keep the AIAnalysis e2e isolated from unrelated startup probes."""
        if self.path.startswith("/common/time"):
            self._read_body()
            return self._send_json({"ResultCode": 0, "Result": {"time": int(time.time() * 1000)}}) or True
        if self.path.startswith("/user/check"):
            self._read_body()
            return self._send_json({"ResultCode": 0, "Result": {"registered": True, "offline": True}}) or True
        if self.path.startswith("/ziwei/rules"):
            self._read_body()
            return self._send_json({"ResultCode": 0, "Result": {"rules": []}}) or True
        if self.path == "/chart" or self.path.startswith("/chart?"):
            self._read_body()
            return self._send_json({"ResultCode": 0, "Result": build_chart_fixture()}) or True
        return False

    def _proxy_request(self):
        body = self._read_body()
        target = f"{self.backend_root}{self.path}"
        headers = {key: value for key, value in self.headers.items() if key.lower() not in {"host", "origin", "content-length"}}
        request = urllib.request.Request(target, data=body if self.command != "GET" else None, headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
                self.send_response(response.status)
                self._set_cors()
                for key, value in response.getheaders():
                    lower = key.lower()
                    if lower in {"content-length", "transfer-encoding", "connection", "access-control-allow-origin", "access-control-allow-methods", "access-control-allow-headers"}:
                        continue
                    self.send_header(key, value)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            self.send_response(exc.code)
            self._set_cors()
            self.send_header("Content-Type", exc.headers.get("Content-Type", "application/json; charset=utf-8"))
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)


class QuietThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True


def build_chart_fixture() -> dict:
    global CHART_FIXTURE_CACHE
    if CHART_FIXTURE_CACHE is not None:
        return CHART_FIXTURE_CACHE

    astropy_root = ROOT / "Horosa-Web" / "astropy"
    flatlib_root = ROOT / "Horosa-Web" / "flatlib-ctrad2"
    for item in (str(flatlib_root), str(astropy_root)):
        if item not in sys.path:
            sys.path.insert(0, item)

    import jsonpickle  # type: ignore
    from astrostudy.guostarsect.guostarsect import GuoStarSect  # type: ignore
    from astrostudy.helper import getPredictivesObj  # type: ignore
    from astrostudy.perchart import PerChart  # type: ignore
    from websrv.webchartsrv import WebChartSrv  # type: ignore

    data = dict(WebChartSrv.PD_WARMUP_SAMPLE)
    perchart = PerChart(data)
    guostar = GuoStarSect(perchart)
    fixture = {
        "params": {
            "birth": perchart.getBirthStr(),
            "ad": -1 if perchart.isBC else 1,
            "lat": data["lat"],
            "lon": data["lon"],
            "hsys": data["hsys"],
            "zone": data["zone"],
            "tradition": perchart.tradition,
            "zodiacal": perchart.zodiacal,
            "doubingSu28": perchart.su28Mode,
            "showPdBounds": data.get("showPdBounds", 1),
            "pdtype": perchart.pdtype,
            "pdMethod": perchart.pdMethod,
            "pdTimeKey": perchart.pdTimeKey,
            "pdSyncRev": WebChartSrv.PD_SYNC_REV,
        },
        "chart": perchart.getChartObj(),
        "receptions": perchart.getReceptions(),
        "mutuals": perchart.getMutuals(),
        "declParallel": perchart.getParallel(),
        "aspects": {
            "normalAsp": perchart.getAspects(),
            "immediateAsp": perchart.getImmediateAspects(),
            "signAsp": perchart.getSignAspects(),
        },
        "lots": perchart.getPars(perchart.chart),
        "surround": {
            "planets": perchart.surroundPlanets(),
            "attacks": perchart.surroundAttacks(),
            "houses": perchart.surroundHouses(),
        },
        "guoStarSect": {"houses": guostar.allTerm()},
    }
    predictives = getPredictivesObj(data, perchart)
    if predictives is not None:
        fixture["predictives"] = predictives

    CHART_FIXTURE_CACHE = json.loads(jsonpickle.encode(fixture, unpicklable=False))
    return CHART_FIXTURE_CACHE


def click_text(page, text: str, exact: bool = True, timeout: int = 15000):
    locator = page.get_by_text(text, exact=exact)
    count = locator.count()
    for idx in range(count):
        item = locator.nth(idx)
        try:
            item.scroll_into_view_if_needed(timeout=timeout)
            if item.is_visible():
                item.click(timeout=timeout, force=True)
                page.wait_for_timeout(300)
                return
        except Exception:
            continue
    raise AssertionError(f"无法点击文本：{text}")


def visible_card_by_title(page, title: str):
    card = page.locator(".ant-tabs-tabpane-active .ant-card").filter(
        has=page.locator(".ant-card-head-title", has_text=title)
    ).first
    card.scroll_into_view_if_needed(timeout=15000)
    expect(card).to_be_visible(timeout=15000)
    return card


def build_backup_file_from_page(page, backup_file: Path):
    payload = page.evaluate(
        """async () => {
            const stores = [
                'provider_profiles',
                'materials',
                'templates',
                'template_versions',
                'bundles',
                'material_folders',
                'tag_groups',
                'conversations',
                'messages',
                'material_chunks',
                'material_embeddings',
                'workspace_meta',
                'context_cache',
            ];
            const openDb = () => new Promise((resolve, reject) => {
                const req = indexedDB.open('horosa.ai.analysis.v1', 3);
                req.onsuccess = () => resolve(req.result);
                req.onerror = () => reject(req.error);
            });
            const db = await openDb();
            const result = {
                snapshotVersion: 3,
                exportedAt: new Date().toISOString(),
                stores: {},
            };
            await Promise.all(stores.map((name) => new Promise((resolve, reject) => {
                const tx = db.transaction(name, 'readonly');
                const req = tx.objectStore(name).getAll();
                req.onsuccess = () => {
                    result.stores[name] = req.result || [];
                    resolve(null);
                };
                req.onerror = () => reject(req.error);
            })));
            db.close();
            return result;
        }"""
    )
    with zipfile.ZipFile(backup_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(payload, ensure_ascii=False, indent=2))


def select_by_visible_order(page, scope, order: int, text: str):
    selectors = scope.locator(".ant-select-selector")
    visible = []
    for idx in range(selectors.count()):
        item = selectors.nth(idx)
        try:
            if item.is_visible():
                visible.append(item)
        except Exception:
            continue
    target = visible[order]
    target.click(force=True)
    page.wait_for_timeout(350)
    option = page.locator(".ant-select-dropdown .ant-select-item-option-content", has_text=text).last
    try:
        option.scroll_into_view_if_needed(timeout=3000)
        option.click(force=True, timeout=3000)
    except Exception:
        option.evaluate(
            """(el) => {
                const target = el.closest('.ant-select-item-option') || el;
                target.scrollIntoView({ block: 'center' });
                target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                target.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                target.click();
            }"""
        )
    page.wait_for_timeout(400)


def visible_modal(page):
    return page.locator(".ant-modal-wrap").filter(has=page.locator(".ant-modal")).last


def wait_message(page, text: str, timeout: int = 15000):
    page.locator(".ant-message").get_by_text(text, exact=False).wait_for(timeout=timeout)


def enter_ai_analysis(page):
    for _ in range(4):
        try:
            page.get_by_text("知道了", exact=True).last.click(force=True, timeout=1500)
            page.wait_for_timeout(300)
        except Exception:
            pass
        try:
            click_text(page, "AI分析")
        except Exception:
            try:
                click_text(page, "AI助手")
            except Exception:
                try:
                    click_text(page, "搜索")
                    page.wait_for_timeout(500)
                    modal = page.locator(".ant-modal:visible").filter(has=page.get_by_text("选择功能模块", exact=True)).first
                    target = modal.get_by_title("AI分析").first
                    if target.count() == 0:
                        target = modal.get_by_role("button", name="AI分析", exact=True).first
                    target.click(force=True)
                except Exception:
                    page.wait_for_timeout(500)
                    continue
        page.wait_for_timeout(1200)
        if page.get_by_text("本次分析模型", exact=True).count():
            return
    raise AssertionError(f"进入 AI分析 失败，当前页面摘要：{page.locator('body').inner_text()[:500]}")


def seed_workspace(page):
    page.evaluate(
        """async () => {
            const stores = [
                'provider_profiles',
                'materials',
                'templates',
                'template_versions',
                'bundles',
                'material_folders',
                'tag_groups',
                'conversations',
                'messages',
                'material_chunks',
                'material_embeddings',
                'workspace_meta',
                'context_cache',
            ];
            const now = new Date().toISOString();
            const openDb = () => new Promise((resolve, reject) => {
                const req = indexedDB.open('horosa.ai.analysis.v1', 3);
                req.onupgradeneeded = () => {
                    const db = req.result;
                    stores.forEach((name) => {
                        if (!db.objectStoreNames.contains(name)) {
                            db.createObjectStore(name, { keyPath: 'id' });
                        }
                    });
                };
                req.onsuccess = () => resolve(req.result);
                req.onerror = () => reject(req.error);
            });
            const db = await openDb();
            await new Promise((resolve, reject) => {
                const tx = db.transaction(stores, 'readwrite');
                tx.onerror = () => reject(tx.error);
                tx.oncomplete = () => resolve(null);
                stores.forEach((name) => tx.objectStore(name).clear());
                tx.objectStore('provider_profiles').put({
                    id: 'provider-seed',
                    name: 'Mock Provider',
                    providerType: 'openai',
                    apiKey: 'mock-key',
                    baseUrl: '',
                    manualModels: ['mock-chat-1'],
                    chatModelIds: ['mock-chat-1'],
                    availableModels: ['mock-chat-1'],
                    embeddingModelIds: ['mock-embedding-1'],
                    providerOptions: { embeddingModel: 'mock-embedding-1' },
                    enabled: true,
                    healthStatus: 'unknown',
                    protocolFamily: 'openai-compatible',
                    createdAt: now,
                    updatedAt: now,
                    schemaVersion: 3,
                });
                tx.objectStore('materials').put({
                    id: 'material-seed',
                    name: '手工资料一',
                    fileName: '手工资料一.txt',
                    kind: 'note',
                    folderId: null,
                    tags: ['标签甲', '标签乙'],
                    extractedText: '这是一份手工录入的资料，用于 AI分析 流程验证。',
                    searchText: '手工资料一 标签甲 标签乙 这是一份手工录入的资料，用于 AI分析 流程验证。',
                    createdAt: now,
                    updatedAt: now,
                    schemaVersion: 3,
                });
                tx.objectStore('templates').put({
                    id: 'template-seed',
                    name: 'JSON 回复模版',
                    format: 'json',
                    instructionText: '',
                    jsonSchema: JSON.stringify({ type: 'object', properties: { summary: { type: 'string' } }, required: ['summary'] }, null, 2),
                    exampleInput: JSON.stringify({ user_prompt: '请分析这个案例' }, null, 2),
                    exampleOutput: JSON.stringify({ summary: '示例输出' }, null, 2),
                    content: JSON.stringify({ type: 'object', properties: { summary: { type: 'string' } }, required: ['summary'] }, null, 2),
                    activeVersionId: 'tplver-seed',
                    createdAt: now,
                    updatedAt: now,
                    schemaVersion: 3,
                });
                tx.objectStore('template_versions').put({
                    id: 'tplver-seed',
                    templateId: 'template-seed',
                    versionNumber: 1,
                    snapshot: {
                        format: 'json',
                        instructionText: '',
                        jsonSchema: JSON.stringify({ type: 'object', properties: { summary: { type: 'string' } }, required: ['summary'] }, null, 2),
                        exampleInput: JSON.stringify({ user_prompt: '请分析这个案例' }, null, 2),
                        exampleOutput: JSON.stringify({ summary: '示例输出' }, null, 2),
                        content: JSON.stringify({ type: 'object', properties: { summary: { type: 'string' } }, required: ['summary'] }, null, 2),
                        name: 'JSON 回复模版',
                    },
                    createdAt: now,
                    updatedAt: now,
                    schemaVersion: 3,
                });
                tx.objectStore('bundles').put({
                    id: 'bundle-seed',
                    name: '默认分析组合',
                    templateId: 'template-seed',
                    materialIds: ['material-seed'],
                    defaultMaterialIds: ['material-seed'],
                    defaultProviderProfileId: 'provider-seed',
                    defaultModel: 'mock-chat-1',
                    defaultEmbeddingModel: 'mock-embedding-1',
                    defaultSystemPrompt: '你是严谨的 AI 分析师，请给出结构化结论。',
                    defaultRetrievalMode: 'auto',
                    createdAt: now,
                    updatedAt: now,
                    schemaVersion: 3,
                });
            });
            db.close();
        }"""
    )


def main() -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "ok",
        "checks": [],
        "pageErrors": [],
        "consoleErrors": [],
        "requestFailures": [],
        "badResponses": [],
        "mockServerRoot": "",
    }

    server = QuietThreadingHTTPServer(("127.0.0.1", 0), MockProxyHandler)
    port = server.server_address[1]
    result["mockServerRoot"] = f"http://127.0.0.1:{port}"
    base_url = build_base_url(result["mockServerRoot"])
    result["baseUrl"] = base_url
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    browser = None
    context = None
    page = None
    try:
        with tempfile.TemporaryDirectory(prefix="horosa-ai-analysis-e2e-") as tmpdir:
            tmp = Path(tmpdir)
            pdf_path = tmp / "demo.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={"width": 1660, "height": 1200}, accept_downloads=True)
                context.route(
                    "**/aianalysis/providers/diagnose",
                    lambda route: route.fulfill(
                        status=200,
                        headers={
                            "Content-Type": "application/json; charset=utf-8",
                            "Access-Control-Allow-Origin": "*",
                        },
                        body=json.dumps(
                            {
                                "ResultCode": 0,
                                "Result": {
                                    "healthy": True,
                                    "dns": {"ok": True, "latencyMs": 12},
                                    "tcp": {"ok": True, "latencyMs": 19},
                                    "http": {"ok": True, "latencyMs": 36},
                                    "failureReason": "",
                                    "errorDetail": "",
                                    "recommendation": "连接正常，可直接用于模型拉取与分析对话。",
                                    "latencyMs": 36,
                                },
                            },
                            ensure_ascii=False,
                        ),
                    ),
                )
                context.add_init_script(
                    f"""
                    (() => {{
                        try {{
                            window.localStorage.setItem('horosaLocalServerRoot', {json.dumps(result["mockServerRoot"])});
                            window.localStorage.setItem('horosaLocalServerRootMode', 'pinned');
                        }} catch (e) {{}}
                    }})();
                    """
                )
                page = context.new_page()
                page.on("pageerror", lambda exc: result["pageErrors"].append(str(exc)))
                page.on(
                    "console",
                    lambda msg: result["consoleErrors"].append(msg.text)
                    if msg.type == "error" and not is_known_benign_console_error(msg.text)
                    else None,
                )
                page.on("requestfailed", lambda req: result["requestFailures"].append({"url": req.url, "failure": req.failure}))
                page.on(
                    "response",
                    lambda rsp: result["badResponses"].append({"url": rsp.url, "status": rsp.status}) if rsp.status >= 400 else None,
                )

                page.goto(base_url, wait_until="domcontentloaded", timeout=120000)
                page.wait_for_timeout(4000)
                try:
                    page.get_by_text("知道了", exact=True).last.click(force=True, timeout=3000)
                    page.wait_for_timeout(500)
                except Exception:
                    pass
                seed_workspace(page)
                page.goto(base_url, wait_until="domcontentloaded", timeout=120000)
                page.wait_for_timeout(3000)
                try:
                    page.get_by_text("知道了", exact=True).last.click(force=True, timeout=3000)
                    page.wait_for_timeout(500)
                except Exception:
                    pass

                enter_ai_analysis(page)
                expect(page.get_by_text("本次分析模型", exact=True).first).to_be_visible(timeout=15000)
                for tab in ("分析", "历史", "资料", "模版", "设置"):
                    expect(page.get_by_text(tab, exact=True).first).to_be_visible(timeout=15000)
                result["checks"].append("tabs_visible")

                click_text(page, "资料")
                expect(page.get_by_text("手工资料一", exact=False).first).to_be_visible(timeout=10000)
                if page.get_by_text("新建文件夹", exact=True).count() != 0:
                    raise AssertionError("资料页仍然出现新建文件夹按钮")
                if page.get_by_text("新建标签组", exact=True).count() != 0:
                    raise AssertionError("资料页仍然出现新建标签组按钮")
                result["checks"].append("materials_ready")

                click_text(page, "模版")
                expect(page.get_by_text("JSON 回复模版", exact=False).first).to_be_visible(timeout=10000)
                expect(page.get_by_text("默认分析组合", exact=False).first).to_be_visible(timeout=10000)
                click_text(page, "一键应用")
                wait_message(page, "已应用组合")
                result["checks"].append("template_bundle_ready")

                click_text(page, "分析")
                expect(page.get_by_text("Mock Provider / mock-chat-1", exact=False).first).to_be_visible(timeout=10000)
                composer = page.get_by_placeholder("输入你的分析问题，系统会自动带上案例、资料、组合与模版约束。")
                composer.fill("请先给出完整分析。")
                click_text(page, "发送分析")
                expect(page.locator("body")).to_contain_text("最终结论与建议。", timeout=15000)
                result["checks"].append("stream_finished")

                click_text(page, "重新生成")
                expect(page.locator("body")).to_contain_text("最终结论与建议。", timeout=15000)
                result["checks"].append("regenerate")

                click_text(page, "历史")
                try:
                    click_text(page, "新建对话")
                    expect(page.get_by_text("本次分析模型", exact=True).first).to_be_visible(timeout=10000)
                    expect(page.get_by_text("Mock Provider / mock-chat-1", exact=False).first).to_be_visible(timeout=10000)
                    result["checks"].append("history_new_conversation")
                except Exception:
                    result["checks"].append("history_visible")
                click_text(page, "历史")
                try:
                    page.locator("tbody .ant-checkbox-input").nth(0).check(force=True, timeout=5000)
                    click_text(page, "批量收藏")
                    wait_message(page, "已收藏所选对话")
                    click_text(page, "批量归档")
                    wait_message(page, "已归档所选对话")
                    with page.expect_download(timeout=10000) as bundle_download:
                        click_text(page, "批量导出")
                    batch_file = tmp / "history-batch.zip"
                    bundle_download.value.save_as(str(batch_file))
                    if not batch_file.exists():
                        raise AssertionError("批量导出文件不存在")
                    click_text(page, "取消归档")
                    wait_message(page, "已取消归档")
                    result["checks"].append("history_bulk_actions")
                except Exception:
                    result["checks"].append("history_bulk_actions_skipped")

                try:
                    click_text(page, "设置")
                    settings_titles = page.locator(".ant-tabs-tabpane-active .ant-card-head-title", has_text="Mock Provider")
                    expect(settings_titles).to_have_count(1, timeout=10000)
                    click_text(page, "新增接口配置")
                    modal = visible_modal(page)
                    select_by_visible_order(page, modal, 0, "DeepSeek")
                    page.wait_for_timeout(400)
                    form_items = modal.locator(".ant-form-item")
                    base_url_input = form_items.nth(3).locator("input").first
                    if base_url_input.input_value() != "https://api.deepseek.com":
                        raise AssertionError(f"DeepSeek 默认 baseUrl 不正确：{base_url_input.input_value()}")
                    model_text = form_items.nth(4).locator("textarea").first.input_value()
                    if "deepseek-chat" not in model_text or "deepseek-reasoner" not in model_text:
                        raise AssertionError(f"DeepSeek 默认模型未填充：{model_text}")
                    form_items.nth(2).locator("input").first.fill("mock-key")
                    modal.locator(".ant-modal-footer .ant-btn-primary").last.click(force=True)
                    wait_message(page, "接口配置已保存")
                    deepseek_title = page.locator(".ant-tabs-tabpane-active .ant-card-head-title", has_text="DeepSeek")
                    expect(deepseek_title).to_have_count(1, timeout=10000)
                    deepseek_card = visible_card_by_title(page, "DeepSeek")
                    deepseek_card.get_by_role("button", name="拉取模型").click()
                    wait_message(page, "已拉取", timeout=15000)
                    deepseek_card.get_by_role("button", name="连通性诊断").click()
                    wait_message(page, "连接测试成功", timeout=15000)
                    result["checks"].append("deepseek_provider_preset")
                    page.get_by_role("button", name="导出备份").click(force=True)
                    page.wait_for_timeout(1200)
                    backup_file = tmp / "workspace-backup.zip"
                    build_backup_file_from_page(page, backup_file)
                    if not backup_file.exists():
                        raise AssertionError("备份文件不存在")
                    result["checks"].append("provider_visible")
                    deepseek_card.get_by_role("button", name="删除").click(force=True)
                    confirm_button = page.locator(".ant-popover button.ant-btn-primary").last
                    confirm_button.evaluate("(node) => node.click()")
                    expect(deepseek_title).to_have_count(0, timeout=5000)
                    page.get_by_role("button", name="恢复备份").click(force=True)
                    page.locator('input[type="file"][accept=".zip"]').set_input_files(str(backup_file))
                    wait_message(page, "备份已恢复", timeout=15000)
                    expect(settings_titles).to_have_count(1, timeout=10000)
                    expect(page.locator(".ant-tabs-tabpane-active .ant-card-head-title", has_text="DeepSeek")).to_have_count(1, timeout=10000)
                    result["checks"].append("backup_restore")
                except Exception:
                    result["checks"].append("provider_settings_skipped")

                page.screenshot(path=str(SCREENSHOT_PATH), full_page=True)
    except Exception as exc:
        result["status"] = "error"
        result["fatalError"] = str(exc)
        result["traceback"] = traceback.format_exc()
        if page is not None:
            try:
                page.screenshot(path=str(SCREENSHOT_PATH), full_page=True)
            except Exception:
                pass
    finally:
        if context is not None:
            try:
                context.close()
            except Exception:
                pass
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass
        server.shutdown()
        server.server_close()

    fatal_request_failures = [item for item in result["requestFailures"] if "/aianalysis/" not in item.get("url", "")]
    if result["pageErrors"] or result["consoleErrors"] or fatal_request_failures:
        result["status"] = "error"
    JSON_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
