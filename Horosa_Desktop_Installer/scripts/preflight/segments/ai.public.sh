#!/usr/bin/env bash
# 发布前自检 · AI(分析 / 导出 / 助手 / 本机接口 / 无头)(续)
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。

seg_u107() {
echo "[107] AI 导出链(剪贴板/PDF/BOM)+ 紫微运限方向 防回归"
S107_BAD=0
S107_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S107_TAURI="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri"
# 剪贴板:arboard 原生主路 + pbcopy 必钉 LC_CTYPE(GUI .app 无 locale → MacRoman 乱码)
grep -q 'arboard = { version = "3", default-features = false' "${S107_TAURI}/Cargo.toml" || { bad "[107] Cargo.toml 缺 arboard"; S107_BAD=1; }
grep -q 'arboard::Clipboard' "$(pf_shell_rs_prod)" || { bad "[107] main.rs 缺 arboard 原生主路"; S107_BAD=1; }
python3 - "$(pf_shell_rs_prod)" <<'PY107' || { bad "[107] main.rs 存在未钉 LC_CTYPE 的 pbcopy 调用(MacRoman 乱码复发)"; S107_BAD=1; }
import sys, re
src = open(sys.argv[1], encoding='utf-8').read()
for m in re.finditer(r'Command::new\("[^"]*pbcopy"\)', src):
    if '.env("LC_CTYPE"' not in src[m.start():m.start() + 200]:
        sys.exit(1)
sys.exit(0)
PY107
# 前端:复制唯一入口 + 组件层裸 writeText 归零(grep -a 防含 NUL 档被当二进制漏检)
[ -f "${S107_UI}/src/utils/clipboardText.js" ] || { bad "[107] 缺复制共享件 clipboardText.js"; S107_BAD=1; }
grep -q "from '../clipboardText'" "$(pf_src_set "${S107_UI}/src/utils/aiExport.js")" || { bad "[107] aiExport 未走复制共享件"; S107_BAD=1; }
S107_RAW="$(grep -rla 'navigator.clipboard.writeText' "${S107_UI}/src/components" --include='*.js' 2>/dev/null | grep -v __tests__ | wc -l | tr -d ' ')"
[ "${S107_RAW}" = "0" ] || { bad "[107] 组件层仍有 ${S107_RAW} 档裸 navigator.clipboard.writeText(APP 内静默失败)"; S107_BAD=1; }
# PDF:负锚大负值离屏定位(仅 aiExport)+ 守卫正锚
grep -q 'left:-99999px' "$(pf_src_set "${S107_UI}/src/utils/aiExport.js")" && { bad "[107] aiExport PDF 宿主又用大负值离屏定位(全白 PDF)"; S107_BAD=1; }
grep -q 'canvasHasInk' "$(pf_src_set "${S107_UI}/src/utils/aiExport.js")" || { bad "[107] PDF 墨迹守卫缺失(空白假成功)"; S107_BAD=1; }
grep -q 'skipFonts: true' "$(pf_src_set "${S107_UI}/src/utils/aiExport.js")" || { bad "[107] PDF skipFonts 缺失"; S107_BAD=1; }
grep -q "output('blob')" "$(pf_src_set "${S107_UI}/src/utils/aiExport.js")" || { bad "[107] PDF blob 尺寸守卫缺失"; S107_BAD=1; }
# BOM 单源
grep -q 'withUtf8Bom' "${S107_UI}/src/utils/aiAnalysisExport.js" || { bad "[107] BOM 政策单源 withUtf8Bom 缺失"; S107_BAD=1; }
# 紫微运限方向(财=+8/官=+4,地支逆行宫序)
grep -q 'const caibo = (idx + 8) % 12' "${S107_UI}/src/components/ziwei/ZiWeiHelper.js" || { bad "[107] getSanheIndices 财帛方向丢失(应为 命+8)"; S107_BAD=1; }
grep -q 'const guanlu = (idx + 4) % 12' "${S107_UI}/src/components/ziwei/ZiWeiHelper.js" || { bad "[107] getSanheIndices 官禄方向丢失(应为 命+4)"; S107_BAD=1; }
# 测试在位
for t in utils/__tests__/clipboardText.test.js utils/__tests__/aiExportPdfGuard.test.js components/ziwei/__tests__/ziweiSanheDirection.test.js; do
  [ -f "${S107_UI}/src/${t}" ] || { bad "[107] 缺测试 ${t}"; S107_BAD=1; }
done
[ "${S107_BAD}" = "0" ] && ok "[107] AI 导出链 + 紫微运限方向 防回归 全在位"

# ---- [122] dist 构建指纹门(发布产物必须可追溯到干净 HEAD;杜绝「脏工作树构建」产物无对应 commit) ----
S122_BAD=0
S122_INFO="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file/build-info.json"
# 前端源面清单:单源 fe-source-paths.txt(本脚本顶部读入;构建时判脏与产物冒烟同读这一份,[123]⑤b 机械锁)。
#   清单必须覆盖「会改变产物字节」的全部受控输入 —— 只列源码四项时,构建之后只改构建前处理脚本(浮层对齐补丁直接进 bundle)
#   或依赖锁的提交会被判成「产物仍可对应」,装进包里的却是旧补丁 / 旧依赖编出来的 bundle。
S122_FE_PATHS="${FE_SRC_PATHS}"
if [ -z "${S122_FE_PATHS// /}" ]; then bad "[122] 前端源面清单缺失或为空(Horosa-Web/astrostudyui/scripts/fe-source-paths.txt)—— 无从判定产物与源码是否对应"; S122_BAD=1; fi
for S122_REQ in src public package.json package-lock.json .umirc.js scripts/patch-dom-align-zoom.js scripts/patch_quill_domnodeinserted.js scripts/scrub-build-paths.js scripts/inject-preload.js scripts/write-build-info.js scripts/check-chunk-dup.js scripts/fe-source-paths.txt; do
  case " ${S122_FE_PATHS} " in *" Horosa-Web/astrostudyui/${S122_REQ} "*) : ;; *) bad "[122] 前端源面清单缺必备项:${S122_REQ}(构建之后只改它的提交会被误判成产物仍可对应)"; S122_BAD=1 ;; esac
done
if [ ! -f "${S122_INFO}" ]; then
  bad "[122] dist-file 缺 build-info.json(旧产物或 build 链未挂指纹)—— npm run build:file 重建"; S122_BAD=1
else
  S122_COMMIT=$(python3 -c "import json;print(json.load(open('${S122_INFO}')).get('commit',''))" 2>/dev/null || echo "")
  S122_DIRTY=$(python3 -c "import json;print(1 if json.load(open('${S122_INFO}')).get('dirty') else 0)" 2>/dev/null || echo "1")
  S122_HEAD=$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo "")
  [ "${S122_DIRTY}" = "0" ] || { bad "[122] dist-file 由脏工作树构建(含未提交改动)——先 commit 再重 build"; S122_BAD=1; }
  if [ -n "${S122_COMMIT}" ] && [ "${S122_COMMIT}" = "${S122_HEAD}" ]; then
    :  # 指纹=HEAD,最严格等价
  elif [ -n "${S122_COMMIT}" ] && git -C "${REPO_ROOT}" merge-base --is-ancestor "${S122_COMMIT}" "${S122_HEAD}" 2>/dev/null \
       && [ -z "$(git -C "${REPO_ROOT}" diff --name-only "${S122_COMMIT}" "${S122_HEAD}" -- ${S122_FE_PATHS} 2>/dev/null)" ]; then
    :  # 指纹 commit 是 HEAD 祖先且前端源面零 diff:产物与 HEAD 源码等价,仍可追溯(scripts/docs-only 前进不逼重 build)
  else
    bad "[122] dist-file 构建 commit(${S122_COMMIT:0:12}) ≠ 当前 HEAD(${S122_HEAD:0:12}) 且前端源面有 diff——重 build"; S122_BAD=1
  fi
fi
grep -q "write-build-info.js dist-file" "${REPO_ROOT}/Horosa-Web/astrostudyui/package.json" 2>/dev/null || { bad "[122] build:file 未挂构建指纹脚本(write-build-info)"; S122_BAD=1; }
[ "${S122_BAD}" = "0" ] && ok "[122] dist 构建指纹(干净 HEAD ${S122_HEAD:0:12} · 与源码可对应)"
}

seg_u240() {
# [240] 自检收口锁(接口 key 静态加密钩 G1:provider_profiles 读四处解密/写一处加密/主密钥命令)
echo "[240] 自检收口锁(接口 key 静态加密钩)"
S240_BAD=0
S240_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S240_STORE="${S240_UI}/src/utils/aiAnalysisStore.js"
S240_RS="$(pf_shell_rs_prod)"
s240_code(){ sed -E 's#//.*$##' "$1"; }
[ -f "${S240_UI}/src/utils/secureKeyStore.js" ] || { bad "[240] secureKeyStore.js 缺失"; S240_BAD=1; }
[ "$(s240_code "${S240_STORE}" | grep -acF "from './secureKeyStore'")" != "0" ] || { bad "[240] aiAnalysisStore 未接 secureKeyStore(接口 key 明文落库)"; S240_BAD=1; }
[ "$(s240_code "${S240_STORE}" | grep -acF "encryptSecretText(")" != "0" ] || { bad "[240] aiAnalysisStore 写路径未加密 apiKey"; S240_BAD=1; }
[ "$(s240_code "${S240_STORE}" | grep -acF "decryptProfileRecord(rec, storeName)")" -ge 3 ] || { bad "[240] aiAnalysisStore 读路径解密不足三处(list/batched/readByIndex)"; S240_BAD=1; }
[ "$(s240_code "${S240_STORE}" | grep -acF "return decryptProfileRecord(record, storeName);")" != "0" ] || { bad "[240] getStoreRecord 未解密 provider 记录"; S240_BAD=1; }
[ "$(s240_code "${S240_STORE}" | grep -acF "apiKeyDecryptFailed: true")" != "0" ] || { bad "[240] 解密失败未置空+标记(密文会流进请求头)"; S240_BAD=1; }
grep -aqF "fn ai_master_key_command()" "${S240_RS}" || { bad "[240] main.rs 缺主密钥命令 ai_master_key_command(canEncryptSecrets 恒假=明文)"; S240_BAD=1; }
grep -aqF "            ai_master_key_command," "${S240_RS}" || { bad "[240] ai_master_key_command 未注册进 generate_handler"; S240_BAD=1; }
grep -aqF "find-generic-password" "${S240_RS}" || { bad "[240] 主密钥未走登录钥匙串"; S240_BAD=1; }
[ -f "${S240_UI}/src/utils/__tests__/aiSecureKeyStore.test.js" ] || { bad "[240] aiSecureKeyStore.test.js 缺失"; S240_BAD=1; }
[ -f "${S240_UI}/src/utils/__tests__/aiSettingsFacetsWhitelist.test.js" ] || { bad "[240] aiSettingsFacetsWhitelist.test.js 缺失(AI 可写键 ⊆ 登记键 无人看守)"; S240_BAD=1; }
[ "$(s240_code "${S240_UI}/src/utils/__tests__/aiSettingsFacetsWhitelist.test.js" 2>/dev/null | grep -acF "bogusKey")" != "0" ] || { bad "[240] 白名单测试缺注错自证向量"; S240_BAD=1; }
[ -f "${S240_UI}/src/utils/__tests__/aiExportContentAuditRatchet.test.js" ] || { bad "[240] aiExportContentAuditRatchet.test.js 缺失(内容 gap 无棘轮)"; S240_BAD=1; }
[ "${S240_BAD}" = "0" ] && ok "[240] 自检收口锁(接口 key 静态加密钩/AI 可写设置键白名单/测试在位)"
}
