//! 端口选择与前端静态服务。

use super::*;

pub(crate) fn choose_free_port() -> Result<u16> {
    let listener = TcpListener::bind("127.0.0.1:0")?;
    let port = listener.local_addr()?.port();
    drop(listener);
    Ok(port)
}

pub(crate) fn choose_port_with_preference(preferred_port: u16) -> Result<u16> {
    // 端口防漂移阶梯:偏好口被占(另一实例在跑/他进程占用)不再直接跳随机口——
    // localStorage/IndexedDB 按 origin(含端口)分域,随机漂移=该实例的本地缓存/偏好全部
    // 换域「看起来清零」。改为 preferred..preferred+8 顺位试绑:第二实例稳定落 38992、
    // 第三落 38993……各实例跨重启口径稳定,域不再漂;九口全占才落随机兜底(账本可见)。
    for offset in 0..=8u16 {
        let candidate = match preferred_port.checked_add(offset) {
            Some(p) => p,
            None => break,
        };
        if let Ok(listener) = TcpListener::bind(("127.0.0.1", candidate)) {
            let port = listener.local_addr()?.port();
            drop(listener);
            if offset > 0 {
                ledger_mark(
                    "rust.web_port_ladder",
                    Some(serde_json::json!({"preferred": preferred_port, "chosen": port})),
                );
            }
            return Ok(port);
        }
    }
    let fallback = choose_free_port()?;
    ledger_mark(
        "rust.web_port_random_fallback",
        Some(serde_json::json!({"preferred": preferred_port, "chosen": fallback})),
    );
    Ok(fallback)
}

// 静态资产 RAM 缓存条目:dist 在进程运行期不变(更新=换树重启;repair=新 bootstrap
// 新 server 新缓存),故一次性构建、零失效逻辑。raw/gz 双体;etag 与磁盘路径共用同一公式
// (make_static_etag)——跨「缓存命中/磁盘回退/进程重启」三态 304 连续性逐字节不破。
pub(crate) struct StaticRamAsset {
    pub(crate) raw: Vec<u8>,
    pub(crate) gz: Option<Vec<u8>>,
    etag_raw: String,
    etag_gz: Option<String>,
    mime: String,
}

/// 在限时内轮询某口能否在 127.0.0.1 上绑定(绑上即放);到时仍绑不上回 false。
fn wait_port_bindable(port: u16, budget: Duration) -> bool {
    let deadline = Instant::now() + budget;
    loop {
        if TcpListener::bind(("127.0.0.1", port)).is_ok() {
            return true;
        }
        if Instant::now() >= deadline {
            return false;
        }
        thread::sleep(Duration::from_millis(50));
    }
}

/// 换静态服务器关停旗标:旧旗标先置 true 再换(旧服务器的工作线程 250 ms 内收工、监听口随之释放),
/// 不留一台没人管、一直占着口的旧服务器。
pub(crate) fn replace_web_shutdown(
    slot: &Mutex<Option<Arc<AtomicBool>>>,
    next: Option<Arc<AtomicBool>>,
) {
    if let Ok(mut guard) = slot.lock() {
        if let Some(old) = guard.take() {
            old.store(true, Ordering::SeqCst);
        }
        *guard = next;
    }
}

/// 引导选前端口。同一进程里再次引导(菜单「重装运行时」、重启服务失败后的回退修复)时,
/// 本进程上一台静态服务器还占着原口:先把它收掉、等原口放出来(至多 1.5 s),再按原口优先选口
/// —— 页面 origin(含端口)不变,本地数据分区不换。否则新服务器只能落到下一个口,
/// 页面换了 origin,命盘 / 事盘 / 设置 / 对话全都「不见了」,这次会话里写的数据下次正常启动也看不到。
/// 首次引导(没有旧服务器、没有旧会话)与原来一样:按 38991 起的阶梯选口。
pub(crate) fn pick_web_port_for_bootstrap(
    web_shutdown: &Mutex<Option<Arc<AtomicBool>>>,
    previous_web_port: Option<u16>,
) -> Result<u16> {
    let retired = match web_shutdown.lock() {
        Ok(mut guard) => match guard.take() {
            Some(old) => {
                old.store(true, Ordering::SeqCst);
                true
            }
            None => false,
        },
        Err(_) => false,
    };
    let preferred = previous_web_port.unwrap_or(DEFAULT_FRONTEND_PORT);
    if retired || previous_web_port.is_some() {
        let freed = wait_port_bindable(preferred, Duration::from_millis(1500));
        ledger_mark(
            "rust.web_port_rebootstrap",
            Some(serde_json::json!({
                "preferred": preferred,
                "retired_previous": retired,
                "freed": freed,
            })),
        );
    }
    choose_port_with_preference(preferred)
}

/// 静态服务器端口绑定失败(探口空闲到真正绑定之间被别的进程抢走)后重选:仍从首选口起走阶梯,
/// 不跳随机口 —— 随机口的实例在页面眼里既不是主实例也不是阶梯上的独立实例。
pub(crate) fn retry_web_port_after_bind_race(preferred: u16) -> Result<u16> {
    choose_port_with_preference(preferred)
}

// umi 内容 hash 判定:文件名含「.xxxxxxxx.」8 位十六进制段(umi.3425e23b.js /
// p__index.4d77b5f4.async.js / umi.d1758af4.css)= 内容寻址,可 immutable 长缓存;
// 其余(index.html 等)走 no-cache 重校验。
fn static_asset_has_content_hash(name: &str) -> bool {
    let bytes = name.as_bytes();
    let mut i = 0usize;
    while i < bytes.len() {
        if bytes[i] == b'.' {
            let start = i + 1;
            let mut j = start;
            while j < bytes.len() && bytes[j].is_ascii_hexdigit() {
                j += 1;
            }
            if j - start == 8 && j < bytes.len() && bytes[j] == b'.' {
                return true;
            }
            i = if j > start { j } else { i + 1 };
        } else {
            i += 1;
        }
    }
    false
}

// 弱 ETag 公式单源:len-mtime(-gz)。缓存构建与磁盘旧路径共用 —— 谁改公式必须
// 两路同改,否则同一文件在命中/回退两态给出不同 ETag = 客户端缓存被无谓打穿。
fn make_static_etag(len: u64, mtime_secs: u64, gz: bool) -> String {
    format!(
        "W/\"{}-{}{}\"",
        len,
        mtime_secs,
        if gz { "-gz" } else { "" }
    )
}

fn static_file_mtime_secs(meta: &fs::Metadata) -> u64 {
    meta.modified()
        .ok()
        .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

// 构建 RAM 缓存:清单**解析 index.html 的 script/link 引用**自维护(零硬编码
// chunk 名 —— preload 清单扩容/chunk 改名后自动跟随);加 index.html 自身。每项载入
// raw + .gz 旁件。单件 >8MB 跳过、总预算 40MB(现首屏 raw ~10.2MB + gz ~2.9MB)。
fn build_static_ram_cache(
    frontend_dir: &std::path::Path,
) -> std::collections::HashMap<String, StaticRamAsset> {
    let mut map = std::collections::HashMap::new();
    let html_path = frontend_dir.join("index.html");
    let html = match fs::read_to_string(&html_path) {
        Ok(h) => h,
        Err(_) => return map,
    };
    let mut rels: Vec<String> = vec!["index.html".to_string()];
    for cap in html.split(|c| c == '"' || c == '\'') {
        let cand = cap.trim_start_matches("./").trim_start_matches('/');
        if (cand.ends_with(".js") || cand.ends_with(".css"))
            && !cand.contains("://")
            && !cand.is_empty()
            && static_rel_path_is_safe(cand)
            && !rels.iter().any(|r| r == cand)
        {
            rels.push(cand.to_string());
        }
    }
    const SINGLE_CAP: u64 = 8 * 1024 * 1024;
    const TOTAL_CAP: usize = 40 * 1024 * 1024;
    let mut total: usize = 0;
    for rel in rels {
        let path = frontend_dir.join(&rel);
        let meta = match fs::metadata(&path) {
            Ok(m) if m.is_file() && m.len() <= SINGLE_CAP => m,
            _ => continue,
        };
        let raw = match fs::read(&path) {
            Ok(b) => b,
            Err(_) => continue,
        };
        if total + raw.len() > TOTAL_CAP {
            break;
        }
        total += raw.len();
        let etag_raw = make_static_etag(meta.len(), static_file_mtime_secs(&meta), false);
        let gz_path = PathBuf::from(format!("{}.gz", path.to_string_lossy()));
        let (gz, etag_gz) = match fs::metadata(&gz_path) {
            Ok(gm) if gm.is_file() => match fs::read(&gz_path) {
                Ok(gb) if total + gb.len() <= TOTAL_CAP => {
                    total += gb.len();
                    let et = make_static_etag(gm.len(), static_file_mtime_secs(&gm), true);
                    (Some(gb), Some(et))
                }
                _ => (None, None),
            },
            _ => (None, None),
        };
        let mime = from_path(&path).first_or_octet_stream().to_string();
        map.insert(
            rel,
            StaticRamAsset {
                raw,
                gz,
                etag_raw,
                etag_gz,
                mime,
            },
        );
    }
    map
}

// RAM 命中应答:响应头语义(ETag/304/Cache-Control/Vary/Content-Encoding/CSP)与
// 磁盘路径**逐字段一致**(下方磁盘路径是语义权威;两处改动必须同步)。
fn respond_static_from_ram(request: tiny_http::Request, rel: &str, asset: &StaticRamAsset) {
    let immutable = static_asset_has_content_hash(rel.rsplit('/').next().unwrap_or(rel));
    let cache_control: &str = if immutable {
        "public, max-age=31536000, immutable"
    } else {
        "no-cache"
    };
    let accepts_gzip = request.headers().iter().any(|h| {
        h.field.equiv("Accept-Encoding") && h.value.as_str().to_ascii_lowercase().contains("gzip")
    });
    let use_gz = accepts_gzip && asset.gz.is_some();
    let etag = if use_gz {
        asset.etag_gz.as_deref().unwrap_or(asset.etag_raw.as_str())
    } else {
        asset.etag_raw.as_str()
    };
    let inm_hit = request
        .headers()
        .iter()
        .any(|h| h.field.equiv("If-None-Match") && h.value.as_str().trim() == etag);
    if inm_hit {
        let mut resp = Response::empty(StatusCode(304));
        if let Ok(hd) = Header::from_bytes(&b"ETag"[..], etag.as_bytes()) {
            resp = resp.with_header(hd);
        }
        if let Ok(hd) = Header::from_bytes(&b"Cache-Control"[..], cache_control.as_bytes()) {
            resp = resp.with_header(hd);
        }
        if let Ok(hd) = Header::from_bytes(&b"Vary"[..], &b"Accept-Encoding"[..]) {
            resp = resp.with_header(hd);
        }
        let _ = request.respond(resp);
        return;
    }
    let body: Vec<u8> = if use_gz {
        asset
            .gz
            .as_ref()
            .cloned()
            .unwrap_or_else(|| asset.raw.clone())
    } else {
        asset.raw.clone()
    };
    let mut response = Response::from_data(body);
    if let Ok(header) = Header::from_bytes(&b"Content-Type"[..], asset.mime.as_bytes()) {
        response = response.with_header(header);
    }
    if use_gz {
        if let Ok(hd) = Header::from_bytes(&b"Content-Encoding"[..], &b"gzip"[..]) {
            response = response.with_header(hd);
        }
    }
    if let Ok(hd) = Header::from_bytes(&b"Vary"[..], &b"Accept-Encoding"[..]) {
        response = response.with_header(hd);
    }
    if let Ok(hd) = Header::from_bytes(&b"Cache-Control"[..], cache_control.as_bytes()) {
        response = response.with_header(hd);
    }
    if let Ok(hd) = Header::from_bytes(&b"ETag"[..], etag.as_bytes()) {
        response = response.with_header(hd);
    }
    if asset.mime == "text/html" {
        if let Ok(csp) = Header::from_bytes(
                            &b"Content-Security-Policy"[..],
                            &b"default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval' https://*.amap.com; style-src 'self' 'unsafe-inline' https://*.amap.com; img-src 'self' data: blob: https://*.amap.com https://*.autonavi.com; font-src 'self' data:; connect-src 'self' http://127.0.0.1:* http://localhost:* ws://127.0.0.1:* ws://localhost:* https://*.amap.com https://*.autonavi.com; worker-src 'self' blob:; media-src 'self' blob: data:; object-src 'none'; base-uri 'none'; form-action 'self'; frame-src 'self'"[..],
        ) {
            response = response.with_header(csp);
        }
    }
    let _ = request.respond(response);
}

/// 前端静态服务器的请求路径(已去掉开头的 `/`,未做百分号解码)是否安全:
/// 拒空串、NUL、反斜杠、绝对路径、`..` 段,以及编码过的点 / 斜杠 / 反斜杠 / NUL(`%2e` `%2f` `%5c` `%00`,不分大小写)。
pub(crate) fn static_rel_path_is_safe(rel: &str) -> bool {
    if rel.is_empty() || rel.contains('\0') || rel.contains('\\') || rel.starts_with('/') {
        return false;
    }
    let lower = rel.to_ascii_lowercase();
    if ["%2e", "%2f", "%5c", "%00"]
        .iter()
        .any(|enc| lower.contains(enc))
    {
        return false;
    }
    Path::new(rel).components().all(|c| {
        matches!(
            c,
            std::path::Component::Normal(_) | std::path::Component::CurDir
        )
    })
}

/// 文件解析符号链接后是否仍在前端目录之内(root 为已解析过符号链接的前端目录)。
fn static_path_within_root(path: &Path, canonical_root: &Path) -> bool {
    match fs::canonicalize(path) {
        Ok(real) => real.starts_with(canonical_root),
        Err(_) => false,
    }
}

/// 解析静态请求要读的文件:路径不安全 → None(回 404);文件不存在 → 只回落 index.html(单页路由);
/// 存在但经符号链接解析后落到前端目录外 → None。
pub(crate) fn resolve_static_target(
    frontend_dir: &Path,
    canonical_root: Option<&Path>,
    rel: &str,
) -> Option<PathBuf> {
    if !static_rel_path_is_safe(rel) {
        return None;
    }
    let target = frontend_dir.join(rel);
    if !target.exists() {
        return Some(frontend_dir.join("index.html"));
    }
    let fallback_root;
    let root = match canonical_root {
        Some(r) => r,
        None => {
            fallback_root = fs::canonicalize(frontend_dir).ok()?;
            fallback_root.as_path()
        }
    };
    if static_path_within_root(&target, root) {
        Some(target)
    } else {
        None
    }
}

/// 静态服务器只认本机回环的 Host 头(127.0.0.1 / localhost / [::1],带不带端口都行);
/// 没有 Host 头(HTTP/1.0)放行。
pub(crate) fn static_host_allowed(host: Option<&str>) -> bool {
    let Some(raw) = host else {
        return true;
    };
    let h = raw.trim().to_ascii_lowercase();
    let name = if let Some(rest) = h.strip_prefix('[') {
        match rest.find(']') {
            Some(end) => format!("[{}]", &rest[..end]),
            None => return false,
        }
    } else {
        h.split(':').next().unwrap_or("").to_string()
    };
    matches!(name.as_str(), "127.0.0.1" | "localhost" | "[::1]")
}

pub(crate) fn start_static_server(
    frontend_dir: PathBuf,
    port: u16,
    shutdown: Arc<AtomicBool>,
) -> Result<thread::JoinHandle<()>> {
    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    let server = Server::http(addr).map_err(|e| anyhow!(e.to_string()))?;
    // 线程池:tiny_http Server 是 Sync,官方多线程模式 = Arc<Server> + N worker 各自
    // recv_timeout。旧单线程串行供给首屏 ~10MB×12 响应排队;WKWebView 同源并发 ≤6,默认 4
    // worker(>4 与 JVM 引导抢核边际负)。HOROSA_STATIC_POOL:0/1=单线程旧行为,2..8 夹取。
    let pool: usize = std::env::var("HOROSA_STATIC_POOL")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .map(|n| if n <= 1 { 1 } else { n.min(8) })
        .unwrap_or(4);
    // RAM 缓存后台构建:建成前 worker 走磁盘旧路径(优雅降级,早到请求零等待)。
    // kill-switch:HOROSA_STATIC_RAM_CACHE=0。
    let ram_enabled = std::env::var("HOROSA_STATIC_RAM_CACHE")
        .map(|v| v != "0")
        .unwrap_or(true);
    let ram_cache: Arc<
        std::sync::RwLock<Option<std::collections::HashMap<String, StaticRamAsset>>>,
    > = Arc::new(std::sync::RwLock::new(None));
    if ram_enabled {
        let cache_slot = Arc::clone(&ram_cache);
        let dir_for_cache = frontend_dir.clone();
        let t0 = std::time::Instant::now();
        thread::spawn(move || {
            let built = build_static_ram_cache(&dir_for_cache);
            let files = built.len();
            let bytes: usize = built
                .values()
                .map(|a| a.raw.len() + a.gz.as_ref().map(|g| g.len()).unwrap_or(0))
                .sum();
            if let Ok(mut w) = cache_slot.write() {
                *w = Some(built);
            }
            ledger_mark(
                "rust.static_cache_ready",
                Some(serde_json::json!({
                    "files": files,
                    "bytes": bytes,
                    "ms": t0.elapsed().as_millis() as u64,
                })),
            );
        });
    }
    let server = Arc::new(server);
    // 前端目录的真实路径(解析过符号链接):判请求文件是否仍在目录之内用;取不到时逐请求现取。
    let canonical_root: Option<PathBuf> = fs::canonicalize(&frontend_dir).ok();
    let mut workers: Vec<thread::JoinHandle<()>> = Vec::new();
    for _ in 0..pool {
        let server = Arc::clone(&server);
        let shutdown = Arc::clone(&shutdown);
        let frontend_dir = frontend_dir.clone();
        let ram_cache = Arc::clone(&ram_cache);
        let canonical_root = canonical_root.clone();
        workers.push(thread::spawn(move || {
        while !shutdown.load(Ordering::Relaxed) {
            let request = match server.recv_timeout(Duration::from_millis(250)) {
                Ok(Some(req)) => req,
                Ok(None) => continue,
                Err(_) => continue,
            };
            if request.method() != &Method::Get && request.method() != &Method::Head {
                let _ = request.respond(Response::empty(StatusCode(405)));
                continue;
            }
            // 只认本机回环的 Host(防 DNS 重绑定把外站页面伪装成本机来源)
            let host_ok = static_host_allowed(
                request
                    .headers()
                    .iter()
                    .find(|h| h.field.equiv("Host"))
                    .map(|h| h.value.as_str()),
            );
            if !host_ok {
                let _ = request.respond(Response::empty(StatusCode(403)));
                continue;
            }
            let url = request.url().split('?').next().unwrap_or("/");
            let rel = if url == "/" {
                "index.html".to_string()
            } else {
                url.trim_start_matches('/').to_string()
            };
            // 路径只许落在前端目录之内:`..` 段、绝对路径、编码过的点 / 斜杠一律 404(请求行里的路径
            // 原样交到这里,不做规范化;直接拼到目录后面会被系统解析成目录外的任意文件)。
            if !static_rel_path_is_safe(&rel) {
                let _ = request.respond(Response::empty(StatusCode(404)));
                continue;
            }
            // RAM 命中:首屏关键件(index.html 引用的 js/css+gz 旁件)零磁盘 IO 应答。
            // try_read 失败(构建中持写锁的瞬间)按 miss 走磁盘 —— 永不阻塞请求。
            if let Ok(guard) = ram_cache.try_read() {
                if let Some(map) = guard.as_ref() {
                    if let Some(asset) = map.get(&rel) {
                        respond_static_from_ram(request, &rel, asset);
                        continue;
                    }
                }
            }
            // 不存在 → 只回落 index.html(单页路由);存在但经符号链接解析后落到前端目录外 → 404。
            let target = match resolve_static_target(&frontend_dir, canonical_root.as_deref(), &rel)
            {
                Some(t) => t,
                None => {
                    let _ = request.respond(Response::empty(StatusCode(404)));
                    continue;
                }
            };
            // 缓存头三件套:hash 资源 immutable 一年;非 hash(index.html)no-cache 重校验;
            // 弱 ETag=len-mtime(免逐请求读 6.9MB 算摘要),If-None-Match 命中 → 304 连盘都不读。
            // 温启收益:WKWebView 对 hash 资源零重下载零重传输,index.html 一次 304 即定。
            let file_name = target
                .file_name()
                .and_then(|s| s.to_str())
                .unwrap_or("")
                .to_string();
            let immutable = static_asset_has_content_hash(&file_name);
            let cache_control: &str = if immutable {
                "public, max-age=31536000, immutable"
            } else {
                "no-cache"
            };
            let accepts_gzip = request.headers().iter().any(|h| {
                h.field.equiv("Accept-Encoding")
                    && h.value.as_str().to_ascii_lowercase().contains("gzip")
            });
            // 旁置预压缩:构建期为 js/css 等生成 <file>.gz;客户端接受 gzip 且旁件在 → 传压缩体
            // (Content-Type 仍为原 mime + Content-Encoding: gzip)。直接请求 *.gz 的不做二次包装。
            let gz_target = if file_name.ends_with(".gz") {
                None
            } else {
                let cand = PathBuf::from(format!("{}.gz", target.to_string_lossy()));
                if accepts_gzip
                    && cand.is_file()
                    && canonical_root
                        .as_deref()
                        .map_or(false, |root| static_path_within_root(&cand, root))
                {
                    Some(cand)
                } else {
                    None
                }
            };
            let body_path: &PathBuf = gz_target.as_ref().unwrap_or(&target);
            // ETag 公式走单源 make_static_etag —— 与 RAM 缓存路径共用,
            // 跨「缓存命中 / 磁盘回退」两态 304 连续。
            let etag_value = match fs::metadata(body_path) {
                Ok(meta) => Some(make_static_etag(
                    meta.len(),
                    static_file_mtime_secs(&meta),
                    gz_target.is_some(),
                )),
                Err(_) => None,
            };
            if let Some(ref etag) = etag_value {
                let inm_hit = request.headers().iter().any(|h| {
                    h.field.equiv("If-None-Match") && h.value.as_str().trim() == etag.as_str()
                });
                if inm_hit {
                    let mut resp = Response::empty(StatusCode(304));
                    if let Ok(hd) = Header::from_bytes(&b"ETag"[..], etag.as_bytes()) {
                        resp = resp.with_header(hd);
                    }
                    if let Ok(hd) =
                        Header::from_bytes(&b"Cache-Control"[..], cache_control.as_bytes())
                    {
                        resp = resp.with_header(hd);
                    }
                    if let Ok(hd) = Header::from_bytes(&b"Vary"[..], &b"Accept-Encoding"[..]) {
                        resp = resp.with_header(hd);
                    }
                    let _ = request.respond(resp);
                    continue;
                }
            }
            match fs::read(body_path) {
                Ok(bytes) => {
                    let mime = from_path(&target).first_or_octet_stream().to_string();
                    // Header 构造改 infallible 兜底:异常 mime 字节序列不再 panic 静态服务线程。
                    let mut response = Response::from_data(bytes);
                    if let Ok(header) = Header::from_bytes(&b"Content-Type"[..], mime.as_bytes()) {
                        response = response.with_header(header);
                    }
                    if gz_target.is_some() {
                        if let Ok(hd) = Header::from_bytes(&b"Content-Encoding"[..], &b"gzip"[..]) {
                            response = response.with_header(hd);
                        }
                    }
                    if let Ok(hd) = Header::from_bytes(&b"Vary"[..], &b"Accept-Encoding"[..]) {
                        response = response.with_header(hd);
                    }
                    if let Ok(hd) =
                        Header::from_bytes(&b"Cache-Control"[..], cache_control.as_bytes())
                    {
                        response = response.with_header(hd);
                    }
                    if let Some(ref etag) = etag_value {
                        if let Ok(hd) = Header::from_bytes(&b"ETag"[..], etag.as_bytes()) {
                            response = response.with_header(hd);
                        }
                    }
                    // CSP 纵深防御:主界面经本静态服务器加载(不走 tauri 协议,tauri.conf 的
                    // csp 管不到这里——这才是地图真正生效的表面)。umi 产物含 inline script/style,
                    // antd 动态注入样式,3D(three/Babylon) 需 wasm;AI/排盘走本机回环端口。
                    // 高德地图(AMap JSAPI 2.0):注入 https://webapi.amap.com 脚本 + WebGL 瓦片/逆地理走
                    // *.amap.com/*.autonavi.com。故 script/style/img/connect 均须放行这两域(worker-src
                    // 已含 blob:,eval/wasm 已由 'unsafe-eval'+'wasm-unsafe-eval' 放行)。缺域 = Mac 装机版
                    // 地图白屏(WKWebView 严格执行响应头 CSP;preview/Win 宽松故假绿)。发版预检逐域核对这份 CSP。
                    if mime == "text/html" {
                        if let Ok(csp) = Header::from_bytes(
                            &b"Content-Security-Policy"[..],
                            &b"default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval' https://*.amap.com; style-src 'self' 'unsafe-inline' https://*.amap.com; img-src 'self' data: blob: https://*.amap.com https://*.autonavi.com; font-src 'self' data:; connect-src 'self' http://127.0.0.1:* http://localhost:* ws://127.0.0.1:* ws://localhost:* https://*.amap.com https://*.autonavi.com; worker-src 'self' blob:; media-src 'self' blob: data:; object-src 'none'; base-uri 'none'; form-action 'self'; frame-src 'self'"[..],
                        ) {
                            response = response.with_header(csp);
                        }
                    }
                    let _ = request.respond(response);
                }
                Err(_) => {
                    let _ = request.respond(Response::empty(StatusCode(404)));
                }
            }
        }
        }));
    }
    // 签名不变:返回一个「join 全部 worker」的监督线程 handle(调用方 TOCTOU 重试环零改动)。
    let handle = thread::spawn(move || {
        for w in workers {
            let _ = w.join();
        }
    });
    Ok(handle)
}
