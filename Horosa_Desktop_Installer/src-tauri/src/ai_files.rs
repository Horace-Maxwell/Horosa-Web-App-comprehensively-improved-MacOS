//! AI 分析的主密钥与文件 / 图片 / 目录对话框。

use super::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct AiAnalysisFilePayload {
    pub(crate) file_name: String,
    mime_type: String,
    pub(crate) base64_data: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    relative_path: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct AiAnalysisSavePayload {
    default_file_name: String,
    pub(crate) base64_data: String,
    #[serde(default)]
    mime_type: String,
}

/// AI 接口 key 静态加密主密钥:存 macOS 登录钥匙串(service 唯一定位),首次调用生成
/// 32 字节随机密钥。返回 base64;任何失败走 Err → 前端回落明文兼容路径(不阻断功能)。
/// 密钥本身绝不落日志/落盘文件。
fn get_or_create_ai_master_key() -> Result<String> {
    get_or_create_ai_master_key_with(&|args: &[&str]| {
        Command::new("/usr/bin/security")
            .args(args)
            .stdin(Stdio::null())
            .output()
    })
}

/// 主密钥取/建逻辑与 `security` 命令解耦(测试注入执行器):find 命中且非空 ⇒ 原样回;find 退出码 44(不存在)⇒ 生成 32 字节随机 → add-generic-password -U;find 其它失败 / 命中空串 ⇒ Err(不动旧钥,前端回退明文路径);add 失败 ⇒ Err
pub(crate) fn get_or_create_ai_master_key_with(
    run: &dyn Fn(&[&str]) -> std::io::Result<std::process::Output>,
) -> Result<String> {
    const KEYCHAIN_SERVICE: &str = "com.horosa.ai-provider-master";
    const KEYCHAIN_ACCOUNT: &str = "horosa";
    let find = run(&[
        "find-generic-password",
        "-s",
        KEYCHAIN_SERVICE,
        "-a",
        KEYCHAIN_ACCOUNT,
        "-w",
    ]);
    // 只有「条目不存在」(security 退出码 44 = errSecItemNotFound)才允许新建主密钥。
    // 此前任何 find 失败(钥匙串锁定 / 权限拒绝 / 命令跑不起来 / 命中但空串)都直接生成新钥并 -U 覆盖 →
    // 旧主密钥被替换,库内全部密文永久解不开。现在其它失败一律 Err(前端回退明文路径且不动旧钥)。
    let find = find.context("run security find-generic-password for ai master key")?;
    if find.status.success() {
        let existing = String::from_utf8_lossy(&find.stdout).trim().to_string();
        if !existing.is_empty() {
            return Ok(existing);
        }
        return Err(anyhow!(
            "keychain returned an empty ai master key; refusing to overwrite it"
        ));
    }
    if find.status.code() != Some(44) {
        return Err(anyhow!(
            "keychain lookup failed (status {:?}); refusing to create a new ai master key",
            find.status.code()
        ));
    }
    let mut key_bytes = [0u8; 32];
    File::open("/dev/urandom")
        .and_then(|mut f| f.read_exact(&mut key_bytes))
        .context("read urandom for ai master key")?;
    let key_b64 = BASE64_STANDARD.encode(key_bytes);
    let add = run(&[
        "add-generic-password",
        "-s",
        KEYCHAIN_SERVICE,
        "-a",
        KEYCHAIN_ACCOUNT,
        "-w",
        &key_b64,
        "-U",
    ])
    .context("add-generic-password for ai master key")?;
    if !add.status.success() {
        return Err(anyhow!(
            "keychain add failed (status {:?})",
            add.status.code()
        ));
    }
    Ok(key_b64)
}

#[tauri::command]
pub(crate) fn ai_master_key_command() -> std::result::Result<String, String> {
    get_or_create_ai_master_key().map_err(|err| err.to_string())
}

fn ai_analysis_async_dialog() -> AsyncFileDialog {
    let mut dialog = AsyncFileDialog::new();
    dialog = dialog.add_filter("AI Analysis Files", &AI_ANALYSIS_IMPORT_EXTENSIONS);
    dialog
}

fn build_ai_analysis_payload_from_bytes(
    path: &Path,
    root: Option<&Path>,
    bytes: Vec<u8>,
) -> AiAnalysisFilePayload {
    let relative_path = root
        .and_then(|base| path.strip_prefix(base).ok())
        .map(|value| value.to_string_lossy().replace('\\', "/"));
    AiAnalysisFilePayload {
        file_name: path
            .file_name()
            .map(|value| value.to_string_lossy().to_string())
            .unwrap_or_else(|| "unknown.bin".to_string()),
        mime_type: from_path(path)
            .first_or_octet_stream()
            .essence_str()
            .to_string(),
        base64_data: BASE64_STANDARD.encode(bytes),
        relative_path,
    }
}

fn build_ai_analysis_file_payload(
    path: &Path,
    root: Option<&Path>,
) -> std::result::Result<AiAnalysisFilePayload, String> {
    let bytes = fs::read(path).map_err(|err| format!("{err:#}"))?;
    Ok(build_ai_analysis_payload_from_bytes(path, root, bytes))
}

#[tauri::command]
pub(crate) async fn pick_ai_analysis_files_command(
) -> std::result::Result<Vec<AiAnalysisFilePayload>, String> {
    let Some(handles) = ai_analysis_async_dialog().pick_files().await else {
        return Ok(Vec::new());
    };
    let mut items = Vec::new();
    for handle in handles.iter() {
        let bytes = handle.read().await;
        items.push(build_ai_analysis_payload_from_bytes(
            handle.path(),
            None,
            bytes,
        ));
    }
    Ok(items)
}

#[tauri::command]
pub(crate) async fn pick_ai_analysis_folder_command(
) -> std::result::Result<Vec<AiAnalysisFilePayload>, String> {
    let Some(root_handle) = AsyncFileDialog::new().pick_folder().await else {
        return Ok(Vec::new());
    };
    let root = root_handle.path().to_path_buf();
    let mut items = Vec::new();
    let mut first_error = None;
    for entry in WalkDir::new(&root)
        .into_iter()
        .filter_map(|entry| entry.ok())
    {
        let path = entry.path();
        if !path.is_file() {
            continue;
        }
        let ext = path
            .extension()
            .and_then(|value| value.to_str())
            .unwrap_or_default()
            .to_ascii_lowercase();
        if !AI_ANALYSIS_IMPORT_EXTENSIONS.contains(&ext.as_str()) {
            continue;
        }
        match build_ai_analysis_file_payload(path, Some(&root)) {
            Ok(payload) => items.push(payload),
            Err(err) => {
                if first_error.is_none() {
                    first_error = Some(format!(
                        "读取文件失败：{} ({})",
                        path.to_string_lossy(),
                        err
                    ));
                }
            }
        }
    }
    if items.is_empty() {
        if let Some(err) = first_error {
            return Err(err);
        }
    }
    Ok(items)
}

#[tauri::command]
pub(crate) fn save_ai_analysis_file_command(
    payload: AiAnalysisSavePayload,
) -> std::result::Result<String, String> {
    let suggested_name = if payload.default_file_name.trim().is_empty() {
        "ai-analysis-export.bin".to_string()
    } else {
        payload.default_file_name.trim().to_string()
    };
    let Some(target_path) = FileDialog::new().set_file_name(&suggested_name).save_file() else {
        return Err("用户取消保存".to_string());
    };
    let bytes = BASE64_STANDARD
        .decode(payload.base64_data.as_bytes())
        .map_err(|err| format!("{err:#}"))?;
    if let Some(parent) = target_path.parent() {
        fs::create_dir_all(parent).map_err(|err| format!("{err:#}"))?;
    }
    fs::write(&target_path, bytes).map_err(|err| format!("{err:#}"))?;
    Ok(target_path.to_string_lossy().to_string())
}

#[tauri::command]
pub(crate) fn open_ai_analysis_backup_command(
) -> std::result::Result<Option<AiAnalysisFilePayload>, String> {
    let Some(path) = FileDialog::new()
        .add_filter("AI Analysis Backup", &AI_ANALYSIS_BACKUP_EXTENSIONS)
        .pick_file()
    else {
        return Ok(None);
    };
    build_ai_analysis_file_payload(&path, None).map(Some)
}
