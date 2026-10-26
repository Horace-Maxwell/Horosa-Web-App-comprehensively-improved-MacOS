//! 增量部件:差异计划、下载与应用。

use super::*;

// ══════════════════════════ 增量部件更新(manifest v2) ══════════════════════════
// 全量 tar 自带 components-lock.json(打包脚本写进 stage 根),故任何全量安装路径
// (首装 pkg/离线/修复/回退)之后本地即有部件清单;增量更新按 manifest.components
// 与本地 lock 的 sha 差集只下载变化部件,应用采用「clone 暂存 → 部件手术 → 原子
// 对换」协议(与全量 extract_runtime_archive 的 current/previous 语义一致),任何
// 一步失败 current 纹丝不动,调用方回落全量。kill-switch:HOROSA_UPDATE_FULL_ONLY=1。

/// 本地已装部件清单(<root>/current/components-lock.json)。
fn read_local_components_lock(runtime_root: &Path) -> Option<serde_json::Value> {
    let path = runtime_root.join("current").join("components-lock.json");
    let text = fs::read_to_string(path).ok()?;
    serde_json::from_str(&text).ok()
}

fn lock_component_map(lock: &serde_json::Value) -> HashMap<String, serde_json::Value> {
    let mut out = HashMap::new();
    if let Some(items) = lock.get("components").and_then(|v| v.as_array()) {
        for item in items {
            if let Some(name) = item.get("name").and_then(|v| v.as_str()) {
                out.insert(name.to_string(), item.clone());
            }
        }
    }
    out
}

/// 增量可行性判定 + diff。返回需下载的部件集(可为空 = 纯版本标记更新);None = 走全量。
pub(crate) fn plan_component_diff(
    plan: &UpdatePlan,
    runtime_roots: &[PathBuf],
) -> Option<Vec<ManifestComponent>> {
    if std::env::var("HOROSA_UPDATE_FULL_ONLY").ok().as_deref() == Some("1") {
        return None;
    }
    let components = plan.components.as_ref()?;
    plan.components_lock_url.as_ref()?;
    plan.components_lock_sha256.as_ref()?;
    if components.is_empty() {
        return None;
    }
    // 多 root(共享+用户罕见修复态)一律全量:各 root 已装态可能不同,增量按单基准
    // diff 会漏;单 root 覆盖绝大多数常规更新场景。
    if runtime_roots.len() != 1 {
        return None;
    }
    let local = read_local_components_lock(&runtime_roots[0])?;
    let local_map = lock_component_map(&local);
    if local_map.is_empty() {
        return None;
    }
    let changed: Vec<ManifestComponent> = components
        .iter()
        .filter(|c| {
            local_map
                .get(&c.name)
                .and_then(|v| v.get("sha256"))
                .and_then(|v| v.as_str())
                != Some(c.sha256.as_str())
        })
        .cloned()
        .collect();
    Some(changed)
}

/// 下载并校验:components-lock + 变化部件。lock 与 manifest 逐部件核对(防两 asset 漂移)。
// 单部件失败先原地重试,仍败才上抛(由上游整链降级全量——此前一个
// 部件坏一次就整链退全量重下 ~600MB)。按错误类型分治:sha 失配=坏资产,清 dest+续传
// 残档全新下;下载错=网络抖动,保留 .part 让断点续传接力(续传自身次数上限由
// .part.meta 的 attempts 管,与本层「整资产重试」正交)。
pub(crate) const COMPONENT_RETRY_MAX: u32 = 2;

pub(crate) fn download_component_with_retry(
    dest: &Path,
    download: &mut dyn FnMut() -> Result<()>,
    verify: &mut dyn FnMut() -> Result<()>,
    on_retry: &mut dyn FnMut(u32),
) -> Result<()> {
    let mut last_err: Option<anyhow::Error> = None;
    for attempt in 0..=COMPONENT_RETRY_MAX {
        if attempt > 0 {
            on_retry(attempt);
        }
        match download() {
            Ok(()) => {}
            Err(err) => {
                // 下载失败:保留 .part/.meta → 下一轮断点续传接力
                last_err = Some(err);
                continue;
            }
        }
        match verify() {
            Ok(()) => return Ok(()),
            Err(err) => {
                // sha 失配=坏资产:清 dest 与续传残档,下一轮全新下
                let _ = fs::remove_file(dest);
                let (part, meta) = download_part_paths(dest);
                clear_part_files(&part, &meta);
                last_err = Some(err);
            }
        }
    }
    Err(last_err.unwrap_or_else(|| anyhow!("component download failed")))
}

pub(crate) fn download_component_updates(
    app: &AppHandle,
    plan: &UpdatePlan,
    config: &ReleaseConfig,
    changed: &[ManifestComponent],
    start_pct: u8,
    end_pct: u8,
) -> Result<StagedComponents> {
    let lock_url = plan
        .components_lock_url
        .as_ref()
        .context("manifest 缺 componentsLockUrl")?;
    let lock_sha = plan
        .components_lock_sha256
        .as_deref()
        .context("manifest 缺 componentsLockSha256")?;
    let cache_dir = cached_runtime_archive_path(app, config)?
        .parent()
        .map(|p| p.to_path_buf())
        .context("runtime 缓存目录不可用")?;
    ensure_dir(&cache_dir)?;
    let lock_path = cache_dir.join("components-lock.update.json");
    update_ledger_begin_asset("components-lock", 0, 0);
    download_update_asset(
        app,
        lock_url,
        &lock_path,
        start_pct,
        start_pct,
        "下载部件清单",
    )?;
    verify_sha256(&lock_path, Some(lock_sha), "部件清单")?;
    let new_lock_text = fs::read_to_string(&lock_path)?;
    let new_lock_json: serde_json::Value =
        serde_json::from_str(&new_lock_text).context("解析部件清单 JSON")?;
    // 身份与一致性:lock 必须与 manifest 同 runtimeVersion/appName,且逐部件 sha 一致。
    let lock_rt = new_lock_json
        .get("runtimeVersion")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    if Some(lock_rt) != plan.runtime_version.as_deref() {
        return Err(anyhow!(
            "部件清单 runtimeVersion({}) 与更新计划({:?})不符",
            lock_rt,
            plan.runtime_version
        ));
    }
    let lock_app = new_lock_json
        .get("appName")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    if lock_app != APP_NAME {
        return Err(anyhow!(
            "部件清单归属({})与本应用({})不符,拒绝增量",
            lock_app,
            APP_NAME
        ));
    }
    let lock_map = lock_component_map(&new_lock_json);
    if let Some(manifest_comps) = plan.components.as_ref() {
        for c in manifest_comps {
            let ok = lock_map
                .get(&c.name)
                .and_then(|v| v.get("sha256"))
                .and_then(|v| v.as_str())
                == Some(c.sha256.as_str());
            if !ok {
                return Err(anyhow!("部件 {} 在清单与 manifest 间 sha 不一致", c.name));
            }
        }
    }
    let mut archives = Vec::new();
    let total = changed.len().max(1) as u32;
    for (idx, comp) in changed.iter().enumerate() {
        let dest = cache_dir.join(&comp.file);
        let seg = (end_pct - start_pct) as u32;
        let s = start_pct + (seg * idx as u32 / total) as u8;
        let e = start_pct + (seg * (idx as u32 + 1) / total) as u8;
        update_ledger_begin_asset(&comp.name, idx as u32 + 1, changed.len() as u32);
        let label = format!("下载组件 {}({}/{})", comp.name, idx + 1, changed.len());
        download_component_with_retry(
            &dest,
            &mut || download_update_asset(app, &comp.url, &dest, s, e, &label),
            &mut || verify_sha256(&dest, Some(&comp.sha256), &format!("组件 {}", comp.name)),
            &mut |attempt| {
                // 重试:进度段回卷重进(账本重挂当前资产),事件可视
                update_ledger_begin_asset(&comp.name, idx as u32 + 1, changed.len() as u32);
                emit_update_event(
                    app,
                    &serde_json::json!({
                        "phase": "downloading",
                        "pct": s,
                        "message": format!(
                            "组件 {} 下载/校验未过,第 {}/{} 次重试…",
                            comp.name, attempt, COMPONENT_RETRY_MAX
                        ),
                    })
                    .to_string(),
                );
            },
        )?;
        archives.push((comp.clone(), dest));
    }
    Ok(StagedComponents {
        archives,
        new_lock_json,
        new_lock_text,
    })
}

/// 对单个 runtime root 应用增量部件:clone 暂存 → 手术 → 原子对换(失败 current 不动)。
/// 生产链走 apply_component_updates_with(notify);本包装是 component_apply_* 协议测试的
/// 入口(锁定 notify=None 的默认语义),故仅测试构建可见 —— 非测试构建豁免 dead_code。
#[cfg_attr(not(test), allow(dead_code))]
pub(crate) fn apply_component_updates(dest_root: &Path, staged: &StagedComponents) -> Result<()> {
    apply_component_updates_with(dest_root, staged, None)
}

/// notify:安装阶段可视化(WS-1c)。None=现状逐字节一致(既有 component_apply_* 测试全绿即证明)。
pub(crate) fn apply_component_updates_with(
    dest_root: &Path,
    staged: &StagedComponents,
    notify: Option<&dyn Fn(&str)>,
) -> Result<()> {
    let say = |msg: &str| {
        if let Some(cb) = notify {
            cb(msg);
        }
    };
    let current = dest_root.join("current");
    if !current.exists() {
        return Err(anyhow!("增量前提缺失:{} 不存在", current.display()));
    }
    // required 锁:部件手术全程独占(clone→部件对换→swap;防两实例 _comp_stage 互踩)。
    let _surgery = acquire_surgery_lock_required(dest_root)?;
    let stage = dest_root.join("_comp_stage");
    remove_dir_if_exists(&stage)?;
    // 磁盘预检:非 APFS 退化拷贝最多需要一份 runtime 副本 + 解压余量。
    if let Some(avail) = available_disk_bytes(dest_root) {
        let need: u64 = staged
            .archives
            .iter()
            .map(|(_, p)| fs::metadata(p).map(|m| m.len()).unwrap_or(0))
            .sum::<u64>()
            .saturating_mul(3)
            .saturating_add(1_000_000_000);
        if avail < need {
            return Err(anyhow!(
                "磁盘空间不足:增量更新约需 {:.1} GB 可用空间,当前仅 {:.1} GB",
                need as f64 / 1e9,
                avail as f64 / 1e9
            ));
        }
    }
    let result = (|| -> Result<()> {
        stage_runtime_copy(&current, &stage, &say)?;
        let old_lock = fs::read_to_string(stage.join("components-lock.json"))
            .ok()
            .and_then(|t| serde_json::from_str::<serde_json::Value>(&t).ok())
            .context("暂存副本缺已装部件清单(增量基准丢失)")?;
        let old_map = lock_component_map(&old_lock);
        let new_map = lock_component_map(&staged.new_lock_json);
        let comp_total = staged.archives.len();
        for (comp_idx, (comp, archive)) in staged.archives.iter().enumerate() {
            let comp_tag = format!("部件 {}/{}·{}", comp_idx + 1, comp_total, comp.name);
            let detail = new_map
                .get(&comp.name)
                .with_context(|| format!("新清单缺部件 {}", comp.name))?;
            if comp.kind == "tree" {
                // preserve:兄弟数据部件的子树先挪出(本部件 tar 不含它们),解压后放回。
                let preserve: Vec<String> = detail
                    .get("preserve")
                    .and_then(|v| v.as_array())
                    .map(|a| {
                        a.iter()
                            .filter_map(|v| v.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default();
                let preserve_tmp = stage.join("_preserve_tmp");
                remove_dir_if_exists(&preserve_tmp)?;
                let mut moved = Vec::new();
                for (idx, rel) in preserve.iter().enumerate() {
                    let from = stage.join(rel);
                    if from.exists() {
                        let to = preserve_tmp.join(idx.to_string());
                        ensure_dir(preserve_tmp.as_path())?;
                        fs::rename(&from, &to).with_context(|| format!("暂存保留子树 {}", rel))?;
                        moved.push((rel.clone(), to));
                    }
                }
                let paths: Vec<String> = detail
                    .get("paths")
                    .and_then(|v| v.as_array())
                    .map(|a| {
                        a.iter()
                            .filter_map(|v| v.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default();
                if paths.is_empty() {
                    return Err(anyhow!("tree 部件 {} 无 paths 声明", comp.name));
                }
                say(&format!("{}:清理旧内容…", comp_tag));
                for rel in &paths {
                    remove_dir_if_exists(&stage.join(rel))?;
                }
                let on_extract = |read: u64, total: u64, files: u64| {
                    if total == 0 {
                        return;
                    }
                    say(&format!(
                        "{}:解压 {}% · {} 个文件",
                        comp_tag,
                        ((read as f64 / total as f64) * 100.0).min(100.0).round() as u32,
                        files
                    ));
                };
                let extract_progress: Option<&dyn Fn(u64, u64, u64)> = if notify.is_some() {
                    Some(&on_extract)
                } else {
                    None
                };
                tar_extract_strip1_with(archive, &stage, extract_progress)?;
                for (rel, tmp) in moved {
                    let back = stage.join(&rel);
                    if back.exists() {
                        // 新 tar 已带该子树(部件边界调整),保留新内容。
                        remove_dir_if_exists(&tmp)?;
                    } else {
                        if let Some(parent) = back.parent() {
                            ensure_dir(parent)?;
                        }
                        fs::rename(&tmp, &back).with_context(|| format!("放回保留子树 {}", rel))?;
                    }
                }
                remove_dir_if_exists(&preserve_tmp)?;
            } else {
                // files 型:消失文件 =(旧清单 files − 新清单 files)逐个删除,再覆盖解压。
                let files_of = |v: &serde_json::Value| -> Vec<String> {
                    v.get("files")
                        .and_then(|x| x.as_array())
                        .map(|a| {
                            a.iter()
                                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                                .collect()
                        })
                        .unwrap_or_default()
                };
                let new_files: std::collections::HashSet<String> =
                    files_of(detail).into_iter().collect();
                if new_files.is_empty() {
                    return Err(anyhow!("files 部件 {} 无 files 清单", comp.name));
                }
                if let Some(old_detail) = old_map.get(&comp.name) {
                    for f in files_of(old_detail) {
                        if !new_files.contains(&f) {
                            let _ = fs::remove_file(stage.join(&f));
                        }
                    }
                }
                say(&format!("{}:更新文件…", comp_tag));
                tar_extract_strip1(archive, &stage)?;
            }
        }
        say("写入部件清单…");
        // 新部件清单 + runtime-manifest(version/builtAt/appName 从新 lock 派生)落盘。
        // 树根散文件是拷贝不是链接;再删一次条目是硬链接防写穿的通用写法(回退克隆路同样无害)
        let _ = fs::remove_file(stage.join("components-lock.json"));
        fs::write(stage.join("components-lock.json"), &staged.new_lock_text)?;
        let manifest_json = serde_json::json!({
            "version": staged.new_lock_json.get("runtimeVersion").and_then(|v| v.as_str()).unwrap_or(""),
            "built_at": staged.new_lock_json.get("builtAt").and_then(|v| v.as_str()).unwrap_or(""),
            "appName": staged.new_lock_json.get("appName").and_then(|v| v.as_str()).unwrap_or(APP_NAME),
        });
        let _ = fs::remove_file(stage.join("runtime-manifest.json"));
        fs::write(
            stage.join("runtime-manifest.json"),
            serde_json::to_string_pretty(&manifest_json)? + "\n",
        )?;
        prepare_runtime_dir(&stage)?;
        Ok(())
    })();
    if let Err(err) = result {
        let _ = remove_dir_if_exists(&stage);
        return Err(err);
    }
    // 原子对换(与全量 extract_runtime_archive_with 同款协议):
    // 首选 renamex_np 单点互换,current 恒为全旧或全新;回退两段 rename(kill 窗口
    // 由启动期 repair_torn_runtime_slots 撕裂探测兜底)。
    say("原子切换运行时…");
    let backup = dest_root.join("previous");
    remove_dir_if_exists(&backup)?;
    if atomic_swap_dirs(&stage, &current)? {
        // swap 后 stage 位置上是旧树 → 挪 previous;挪失败即撤销 swap 恢复原状
        if let Err(err) = fs::rename(&stage, &backup) {
            let _ = atomic_swap_dirs(&stage, &current);
            let _ = remove_dir_if_exists(&stage);
            return Err(anyhow::Error::from(err).context("旧运行时挪 previous 槽失败"));
        }
    } else {
        fs::rename(&current, &backup)?;
        if let Err(err) = fs::rename(&stage, &current) {
            let _ = fs::rename(&backup, &current);
            let _ = remove_dir_if_exists(&stage);
            return Err(err.into());
        }
    }
    let _ = Command::new("/usr/bin/xattr")
        .arg("-dr")
        .arg("com.apple.quarantine")
        .arg(&current)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    seal_shared_tree_permissions(&current);
    // WS-1d 看门狗:previous 槽保留到首次成功 ready(同 extract_runtime_archive_with 语义)。
    clear_runtime_pending_marker(&current)?;
    Ok(())
}
