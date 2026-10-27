#!/usr/bin/env bash
# 发布前自检 · 发布链(版本 / 产物 / 签名 / 安装 / 增量 / 发布)
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。段号用 ${PF_NO}(登记表第二列)。

seg_2() {
# 2. 本版 release notes 文件必须存在且非空(否则发布页只剩通用模板 —— v2.1.4 复盘 #1)
echo "[2] 本版发布说明"
[ -s "${INSTALLER_ROOT}/config/release_notes/${VERSION}.md" ] && ok "config/release_notes/${VERSION}.md 存在" || bad "缺 config/release_notes/${VERSION}.md —— 发布页会只显示通用说明"
}

seg_4() {
# 4. settings.local.json 绝不可被 git 跟踪(里面有 token / 机器路径 —— 本次复盘的泄露风险)
echo "[4] 机密文件未入库"
if git -C "${REPO_ROOT}" ls-files --error-unmatch .claude/settings.local.json >/dev/null 2>&1; then bad ".claude/settings.local.json 被 git 跟踪了(含 token,有泄露风险!)"; else ok ".claude/settings.local.json 未被跟踪"; fi
# .claude 配置 JSON 必须可解析(曾有加 token 时漏逗号弄坏过)
for f in settings.json settings.local.json launch.json; do
  p="${REPO_ROOT}/.claude/${f}"
  [ -f "${p}" ] || continue
  python3 -m json.tool "${p}" >/dev/null 2>&1 && ok ".claude/${f} 可解析" || bad ".claude/${f} JSON 解析失败"
done
}

seg_5() {
# 5. 编译产物新鲜度(后端 jar / 前端 dist-file 不能比源码旧 —— 复盘 #2;打包时也会再拦一次)
echo "[5] 编译产物新鲜度"
JAR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
DIST="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file/index.html"
# 内容感知豁免(制度化 2026-07-14,git-op mtime 假旧类):git checkout/reset/merge 会平移「工作树源文件」
# 的 mtime(gitignored 的 target/jar、dist-file 产物不被触碰),令「find src -newer 产物」在切分支/reset
# 后误判产物假旧、阻断发布。真判据 = 内容可证现行,而非 mtime。仅当内容可证现行时豁免 mtime 裁决;否则(含
# 真·未提交改动/未重建)照旧按 mtime 拦——两门并存的设计不破(见 [122])。
if [ -f "${JAR}" ]; then
  # jar 无 build-info 指纹 ⟹ 现行判据:后端工作树对 HEAD 干净(无未提交改动) ∧ jar 构建时刻 ≥ 最近一次
  # 改后端源(src/main、pom.xml)的提交时刻(git-op 不动 gitignored 的 target/jar,其 mtime 是真实构建时刻)。
  _JAR_MT="$(stat -f %m "${JAR}" 2>/dev/null || echo 0)"
  _JAR_LASTSRC_CT="$(git -C "${REPO_ROOT}" log -1 --format=%ct -- ':(glob)Horosa-Web/astrostudysrv/**/src/main/**' ':(glob)Horosa-Web/astrostudysrv/**/pom.xml' 2>/dev/null || echo 0)"
  if [ "${_JAR_LASTSRC_CT}" != "0" ] && [ "${_JAR_MT}" -ge "${_JAR_LASTSRC_CT}" ] && git -C "${REPO_ROOT}" diff --quiet HEAD -- Horosa-Web/astrostudysrv 2>/dev/null; then
    ok "astrostudyboot.jar 现行(后端工作树干净 ∧ jar 构建≥最近后端提交;git-op mtime 假旧已内容感知豁免)"
  elif [ -n "$(find "${REPO_ROOT}"/Horosa-Web/astrostudysrv/*/src/main -type f -newer "${JAR}" -print -quit 2>/dev/null || true)" ]; then bad "astrostudyboot.jar 比后端源码旧 —— 需按聚合 pom 重建(mvn -f Horosa-Web/astrostudysrv/pom.xml clean install -DskipTests)"; else ok "astrostudyboot.jar 比源码新"; fi
else warn "astrostudyboot.jar 不存在(发布会回退到 runtime bundle 旧 jar —— 后端有改动务必先重建)"; fi
if [ -f "${DIST}" ]; then
  # dist-file 由 build-info 指纹背书 ⟹ 现行判据(与 [122] 同):前端工作树对 HEAD 干净 ∧ build-info.dirty==0 ∧
  # build-info.commit 为 HEAD(或 HEAD 祖先且前端源面零 diff)。满足即产物源自 HEAD 前端源,mtime 假旧可豁免。
  _DINFO="${REPO_ROOT}/Horosa-Web/astrostudyui/dist-file/build-info.json"
  _DIST_FRESH=0
  # shellcheck disable=SC2086
  if [ -f "${_DINFO}" ] && [ -n "${FE_SRC_PATHS// /}" ] && git -C "${REPO_ROOT}" diff --quiet HEAD -- ${FE_SRC_PATHS} 2>/dev/null; then
    _DC="$(python3 -c "import json;print(json.load(open('${_DINFO}')).get('commit',''))" 2>/dev/null || echo "")"
    _DD="$(python3 -c "import json;print(1 if json.load(open('${_DINFO}')).get('dirty') else 0)" 2>/dev/null || echo "1")"
    _DH="$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo "")"
    if [ "${_DD}" = "0" ] && [ -n "${_DC}" ]; then
      if [ "${_DC}" = "${_DH}" ]; then _DIST_FRESH=1
      elif git -C "${REPO_ROOT}" merge-base --is-ancestor "${_DC}" "${_DH}" 2>/dev/null \
           && [ -z "$(git -C "${REPO_ROOT}" diff --name-only "${_DC}" "${_DH}" -- ${FE_SRC_PATHS} 2>/dev/null)" ]; then _DIST_FRESH=1; fi
    fi
  fi
  if [ "${_DIST_FRESH}" = "1" ]; then
    ok "dist-file 现行(build-info 指纹背书源自 HEAD ∧ 前端源干净;git-op mtime 假旧已内容感知豁免)"
  elif [ -n "$(find "${REPO_ROOT}/Horosa-Web/astrostudyui/src" -type f -not -path "*/.umi/*" -not -path "*/node_modules/*" -newer "${DIST}" -print -quit 2>/dev/null || true)" ]; then bad "dist-file 比前端源码旧 —— 需 npm run build && build:file"; else ok "dist-file 比源码新"; fi
else bad "dist-file 不存在 —— 需 npm run build:file"; fi
}

seg_6() {
# 6. 本机发版基线戳(2026-10-06 改:CI 工作流 2026-05-31 已随「精简仓库附属目录」删除,原「CI 对 HEAD 成功」只剩空门)。
#    基线 = jest 全量 / pytest / mvn 四模块(含四柱全年份域矩阵)/ cargo fmt + test,由 scripts/run_release_baseline.sh 在本机跑完落戳
#    build/release-baseline.json;这里认戳:对当前 HEAD(或戳提交与 HEAD 两棵树只差非源码路径)五套件全绿 → ok;无戳 / 戳过期 / 缺套件 → warn
#    (发布脚本设 HOROSA_REQUIRE_BASELINE=1 时 → bad);任一套件真红 → bad。校验器先自证。
echo "[6] 本机发版基线戳(当前 HEAD)"
S6_PY="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/release_baseline_stamp.py"
if [ -f "${S6_PY}" ]; then
  /usr/bin/python3 "${S6_PY}" --self-test >/dev/null 2>&1 || bad "[6] 基线戳校验器自证失败"
  grep -qF 'export HOROSA_REQUIRE_BASELINE=1' "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh" 2>/dev/null || bad "[6] 发布脚本未强制要基线戳(HOROSA_REQUIRE_BASELINE=1)"
  S6_OUT="$(/usr/bin/python3 "${S6_PY}" check --repo "${REPO_ROOT}" $( [ "${HOROSA_REQUIRE_BASELINE:-0}" = "1" ] && echo --require ) 2>&1)"; S6_RC=$?
  case "${S6_RC}" in
    0) ok "[6] ${S6_OUT}";;
    2) warn "[6] ${S6_OUT}";;
    *) bad "[6] ${S6_OUT}";;
  esac
else bad "[6] 缺 scripts/release_baseline_stamp.py(本机基线戳校验器)"; fi
# 需 :8899 的 pytest 金标:服务不在线时整模块 skip、pytest 照样退 0 → 基线必须 HOROSA_REQUIRE_SRV=1 跑,并逐文件核「有用例且 0 skip」。
#   清单不手写(经 tests/srv_gate.py 单源判据的文件即是);lint 抓「打 :8899 却不经单源判据」「自己读 HOROSA_REQUIRE_SRV」。
S6_SRV="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/check_srv_required_tests.py"
S6_BL="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/run_release_baseline.sh"
if [ -f "${S6_SRV}" ]; then
  /usr/bin/python3 "${S6_SRV}" --self-test >/dev/null 2>&1 || bad "[6] 需服务金标检查器自证失败"
  if S6_LINT="$(/usr/bin/python3 "${S6_SRV}" lint --tests "${REPO_ROOT}/Horosa-Web/astropy/tests" 2>&1)"; then
    ok "[6] ${S6_LINT}"
  else
    bad "[6] 需服务金标登记不一致:$(tr '\n' ' ' <<< "${S6_LINT}")"
  fi
  if grep -qE 'HOROSA_REQUIRE_SRV=1[^#]*-m pytest' "${S6_BL}" && grep -qE 'check_srv_required_tests\.py|SRV_TESTS_CHECK' "${S6_BL}" \
     && grep -qE '"\$\{SRV_TESTS_CHECK\}" junit' "${S6_BL}" && grep -qE '^if ! srv8899_gate; then|^  if ! srv8899_gate; then' "${S6_BL}"; then
    ok "[6] 基线 pytest 带 HOROSA_REQUIRE_SRV=1 + 服务门 + 逐文件核 0 skip"
  else
    bad "[6] 基线 pytest 没设 HOROSA_REQUIRE_SRV=1 / 没过服务门 / 没核需服务金标的 skip —— 服务不在线时整模块 skip 照样记绿"
  fi
else bad "[6] 缺 scripts/check_srv_required_tests.py(需服务金标检查器)"; fi
}

seg_28() {
# 28. 主 README 版本一致性 —— 教训:v2.5.1 首发漏更三主 README(仍停在 2.5.0,下载链接指向旧 pkg →
#     用户点了拿不到新版)。[1] 只校验 package.json/Cargo/tauri 等,不含 README,故漏网。这里补门禁。
echo "[28] 主 README 版本一致性(徽章 + 下载链接随 app 版本 lockstep)"
README_BAD=0
for rf in README.md README_EN.md README_ZH.md; do
  rp="${REPO_ROOT}/${rf}"
  if [ ! -f "${rp}" ]; then warn "[28] 缺 ${rf}"; continue; fi
  if ! grep -q "version-${VERSION}-" "${rp}"; then bad "[28] ${rf} 版本徽章不是 ${VERSION}(README 漏跟随 app 版本)"; README_BAD=1; fi
  if grep -oE "releases/download/v[0-9]+\.[0-9]+\.[0-9]+/" "${rp}" 2>/dev/null | pipe_has -v "releases/download/v${VERSION}/"; then bad "[28] ${rf} 有指向非 v${VERSION} 的下载链接(陈旧,用户会下到旧包)"; README_BAD=1; fi
done
[ "${README_BAD}" = "0" ] && ok "[28] 三主 README 版本徽章 + 下载链接均为 v${VERSION}"
}

seg_42() {
# [42] 发布脚本 config 交接必须 TAB 分隔 (appName 含空格时空格分词会整串右移,
#      RUNTIME_ASSET 变成名字后半截 → "missing runtime archive" 假报,打包中断)
echo "[42] 发布脚本 config 交接 TAB 安全"
S42_BAD=0
for S42_F in build_desktop_release.sh verify_github_release_end_to_end.sh verify_desktop_packaging.sh; do
  S42_P="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/${S42_F}"
  [ -f "${S42_P}" ] || continue
  grep -Eq "IFS=.+ read -r APP_NAME" "${S42_P}" || { bad "[42] ${S42_F} 的 APP_NAME read 缺 IFS 限定(空格 appName 会右移)"; S42_BAD=1; }
  grep -q "sep='\\\\t'" "${S42_P}" || { bad "[42] ${S42_F} 的 python 配置打印缺 sep='\\\\t'"; S42_BAD=1; }
done
[ "${S42_BAD}" = "0" ] && ok "[42] config 交接 TAB 分隔在位"
}

seg_50() {
# [50] 安装分发守卫 (2026-06-12): arm64-only + macOS 12+ gate + entitlements,缺一不可
#      (productbuild 默认 Distribution 允许 x86_64,Intel/旧 OS 用户装完即崩)。
echo "[50] 安装分发守卫"
S50_BAD=0
S50_DIST="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/distribution.xml.template"
[ -f "${S50_DIST}" ] || { bad "[50] distribution.xml.template 缺失"; S50_BAD=1; }
grep -q 'hostArchitectures="arm64"' "${S50_DIST}" 2>/dev/null || { bad "[50] Distribution 缺 arm64-only gate"; S50_BAD=1; }
grep -q 'os-version min="12.0"' "${S50_DIST}" 2>/dev/null || { bad "[50] Distribution 缺 macOS 12+ gate"; S50_BAD=1; }
grep -q -- "--distribution" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh" || { bad "[50] build 脚本未走 --distribution"; S50_BAD=1; }
grep -q 'uname -m' "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template" || { bad "[50] postinstall 缺 arch 兜底守卫"; S50_BAD=1; }
[ -f "${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/horosa.entitlements" ] || { bad "[50] entitlements 文件缺失"; S50_BAD=1; }
grep -q "horosa.entitlements" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh" || { bad "[50] build 脚本未默认挂 entitlements"; S50_BAD=1; }
[ "${S50_BAD}" = "0" ] && ok "[50] arm64+12.0 gate / postinstall 兜底 / entitlements 全在位"
}

seg_74() {
# ============================================================================
# seg_74 增量更新制度(部件切分/manifest v2/发布复用/客户端分支;边界三处 lockstep)
# ============================================================================
S74_BAD=0
S74_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S74_BUILD="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh"
S74_PUB="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh"
S74_MAIN="$(pf_shell_rs_prod)"
S74_LOCK="${REPO_ROOT}/Horosa_Desktop_Installer/dist/components/components-lock.json"
echo "[${PF_NO}] 增量更新制度(部件化 runtime)"
# 打包端:部件段结构 + 部件名单锚(改边界必须同步 SOP 文档与本哨兵)+ 内建校验 + lock 进全量 tar
grep -q "HOROSA_BUILD_COMPONENTS" "${S74_PKG}" 2>/dev/null || { bad "[${PF_NO}] 打包脚本缺部件切分段"; S74_BAD=1; }
for comp in "py-runtime" "jdk-runtime" "ephe-data" "xuanshi-data" "web-app" "java-lib" "java-app"; do
  grep -q "'${comp}'" "${S74_PKG}" 2>/dev/null || { bad "[${PF_NO}] 部件名单缺 ${comp}(边界漂移:脚本/SOP/哨兵三处须 lockstep)"; S74_BAD=1; }
done
grep -q "component split drift" "${S74_PKG}" 2>/dev/null || { bad "[${PF_NO}] 打包脚本缺零遗漏零重叠内建校验"; S74_BAD=1; }
grep -qF "(stage / 'components-lock.json').write_text(lock_text)" "${S74_PKG}" 2>/dev/null || { bad "[${PF_NO}] components-lock 未写入全量 tar(增量本地基准会缺失)"; S74_BAD=1; }
# 发布端:manifest v2 + asset 复用
grep -q "componentsLockUrl" "${S74_BUILD}" 2>/dev/null || { bad "[${PF_NO}] build 脚本缺 manifest v2 部件字段"; S74_BAD=1; }
grep -q "manifest_version = 2" "${S74_BUILD}" 2>/dev/null || { bad "[${PF_NO}] build 脚本缺 manifestVersion 2 升级"; S74_BAD=1; }
grep -q "PYCOMPREUSE" "${S74_PUB}" 2>/dev/null || { bad "[${PF_NO}] publish 脚本缺跨版本 asset 复用决策"; S74_BAD=1; }
# 客户端:diff/下载/应用/回退四件套 + kill-switch
for anchor in "plan_component_diff" "download_component_updates" "apply_component_updates" "HOROSA_UPDATE_FULL_ONLY" "staged_components"; do
  grep -q "${anchor}" "${S74_MAIN}" 2>/dev/null || { bad "[${PF_NO}] main.rs 缺增量客户端锚 ${anchor}"; S74_BAD=1; }
done
# 产物自洽(仅当本地已构建部件时;发版构建必产):lock 结构 + 部件文件在位 + sha 实测一致
if [ -f "${S74_LOCK}" ]; then
  S74_VERIFY="$(python3 - "${S74_LOCK}" 2>&1 <<'PY74'
import hashlib, json, pathlib, sys
lock_path = pathlib.Path(sys.argv[1])
lock = json.loads(lock_path.read_text())
names = sorted(c['name'] for c in lock['components'])
expect = sorted(['py-runtime', 'jdk-runtime', 'ephe-data', 'xuanshi-data', 'web-app', 'java-lib', 'java-app'])
if names != expect:
    raise SystemExit(f'部件集合漂移: {names}')
for c in lock['components']:
    f = lock_path.parent / c['file']
    if not f.is_file():
        raise SystemExit(f"部件文件缺失: {c['file']}")
    h = hashlib.sha256()
    with open(f, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    if h.hexdigest() != c['sha256']:
        raise SystemExit(f"部件 sha 不一致: {c['name']}(lock 与实物漂移,须重跑打包)")
    if c['type'] == 'tree' and not c.get('paths'):
        raise SystemExit(f"tree 部件缺 paths: {c['name']}")
    if c['type'] == 'files' and not c.get('files'):
        raise SystemExit(f"files 部件缺 files: {c['name']}")
print('OK')
PY74
)"
  if [ "${S74_VERIFY}" = "OK" ]; then
    ok "[${PF_NO}] 本地部件产物自洽(7 部件 sha 全核)"
  else
    bad "[${PF_NO}] 部件产物自检失败: ${S74_VERIFY}"; S74_BAD=1
  fi
fi
[ "${S74_BAD}" = "0" ] && ok "[${PF_NO}] 增量更新制度 全在位" || bad "[${PF_NO}] 增量更新制度 有缺失"
}

seg_75() {
# ============================================================================
# seg_75 法律文档与隐私声明一致性(协议说的必须就是代码做的)
# ============================================================================
S75_BAD=0
S75_LEGAL="${REPO_ROOT}/docs/legal"
S75_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
echo "[${PF_NO}] 法律文档随库完整 + 声明↔代码一致"
for doc in "最终用户许可协议与服务条款.md" "隐私政策.md" "安全说明.md" "网络与数据传输说明.md" "开源与第三方组件声明.md"; do
  [ -f "${S75_LEGAL}/${doc}" ] || { bad "[${PF_NO}] 缺法律文档 ${doc}"; S75_BAD=1; }
done
for doc in "Terms-of-Service-and-EULA.md" "Privacy-Policy.md" "Security-Statement.md" "Network-and-Data-Transmission-Statement.md" "Open-Source-and-Third-Party-Notices.md"; do
  [ -f "${S75_LEGAL}/en/${doc}" ] || { bad "[${PF_NO}] 缺英文法律文档 ${doc}"; S75_BAD=1; }
done
# 占位符必须清零(对外文档不得携带待填占位)
# 全树:扫的是法律文档目录(没有测试文件之说)
grep -rl "〔" "${S75_LEGAL}" --include='*.md' 2>/dev/null | grep -v "README.md" | while read -r f; do bad "[${PF_NO}] 法律文档残留占位符: ${f}"; done
# 全树:同上
[ "$(grep -rl '〔' "${S75_LEGAL}" --include='*.md' 2>/dev/null | grep -cv 'README.md')" = "0" ] || S75_BAD=1
# 关于对话框内嵌声明 + 官方链接接线
grep -q "aboutLegal" "${S75_UI}/components/homepage/PageHeader.js" 2>/dev/null || { bad "[${PF_NO}] 关于对话框缺法律声明区块"; S75_BAD=1; }
grep -q "HOROSA_OFFICIAL_REPO" "${S75_UI}/components/homepage/PageHeader.js" 2>/dev/null || { bad "[${PF_NO}] 关于对话框缺官方渠道链接常量"; S75_BAD=1; }
# 隐私声明↔代码一致性执行锚:
#   ① 在线地图须有一次性同意闸(隐私政策 5.3 的事实基础)
grep -q "hasMapConsent" "${S75_UI}/components/amap/MapV2.js" 2>/dev/null || { bad "[${PF_NO}] MapV2 缺地图加载同意闸(隐私政策 5.3 将失实)"; S75_BAD=1; }
#   ② 历史 3D 模型远端域名不得回流(网络说明「不连历史域名」的执行锚)
[ -n "$(pf_prod_hits -a "chart3d\.horosa\.com" "${S75_UI}")" ] && { bad "[${PF_NO}] 前端出现 chart3d 历史域名回流(网络说明将失实)"; S75_BAD=1; }
[ "${S75_BAD}" = "0" ] && ok "[${PF_NO}] 法律文档与一致性 全在位" || bad "[${PF_NO}] 法律文档与一致性 有缺失"
}

seg_79() {
# 79. 打包产物全路由冒烟已跑且绿(哈希绑定,防拿旧包结果充数)
echo "[79] 全路由真实冒烟 stamp(哈希绑定)"
S79_STAMP="${INSTALLER_ROOT}/build/runtime-smoke/last_smoke.json"
S79_ASSET="$(python3 -c "import json;print(json.load(open('${INSTALLER_ROOT}/config/release_config.json')).get('runtimeAssetName','horosa-runtime-macos-arm64.tar.gz'))" 2>/dev/null || echo horosa-runtime-macos-arm64.tar.gz)"
S79_ARCHIVE="${INSTALLER_ROOT}/dist/${S79_ASSET}"
if [ ! -f "${S79_ARCHIVE}" ]; then
  warn "[79] dist 无运行时归档(${S79_ASSET}),冒烟 stamp 校验跳过(构建后会强制)"
elif [ ! -f "${S79_STAMP}" ]; then
  bad "[79] 缺 build/runtime-smoke/last_smoke.json —— 先跑 scripts/verify_runtime_smoke.sh"
else
  S79_RES="$(python3 - "$S79_STAMP" "$S79_ARCHIVE" <<'PY'
import hashlib, json, sys
stamp = json.load(open(sys.argv[1], encoding="utf-8"))
sha = hashlib.sha256(open(sys.argv[2], "rb").read()).hexdigest()
if not stamp.get("pass"):
    print("stamp=FAIL")
elif stamp.get("runtimeSha256") != sha:
    print("sha-mismatch stamp=%s dist=%s" % (str(stamp.get("runtimeSha256"))[:16], sha[:16]))
else:
    print("ok")
PY
)"
  if [ "${S79_RES}" = "ok" ]; then
    ok "[79] 冒烟 stamp PASS 且 sha 与 dist 归档一致"
  else
    bad "[79] 冒烟 stamp 无效(${S79_RES}):对当前归档重跑 verify_runtime_smoke.sh"
  fi
fi
grep -q "runtime-smoke" "${INSTALLER_ROOT}/SELFCHECK_LOG.md" 2>/dev/null \
  && ok "[79] SELFCHECK_LOG 有冒烟留档行" \
  || warn "[79] SELFCHECK_LOG 尚无冒烟留档(首次构建后自动追加)"
}

seg_80() {
# 80. 路由挂载 ↔ 冒烟探针清单 漂移=0(挂载无探针/探针无挂载 皆 FAIL)
echo "[80] 路由挂载↔探针清单漂移"
if python3 "${INSTALLER_ROOT}/scripts/check_route_probe_drift.py" >/dev/null 2>&1; then
  ok "[80] 挂载↔探针 双向一致(含 kinastro importer 覆盖名单)"
else
  python3 "${INSTALLER_ROOT}/scripts/check_route_probe_drift.py" 2>&1 | sed 's/^/    /' >&2 || true
  bad "[80] 挂载↔探针漂移:新增技法漏配探针或僵尸探针(详见上)"
fi
}

seg_84() {
echo "[84] 更新验证基建(事件镜像+假release隔离)"
# (manifest 分离签名机制已整体移除;本节保留事件镜像与假 release 入口隔离锚,
#  并以反向锚确保签名代码不以「半拆」状态残留。)
S84_BAD=0
S84_MAIN="$(pf_shell_rs_prod)"
grep -q "fn log_updater_event" "${S84_MAIN}" 2>/dev/null || { bad "[84] updater 事件镜像 log_updater_event 缺位(用户更新出问题拿不到证据)"; S84_BAD=1; }
grep -q "updater-events.log" "${S84_MAIN}" 2>/dev/null || { bad "[84] 事件镜像日志文件锚缺位"; S84_BAD=1; }
grep -q 'feature = "update-url-override"' "${S84_MAIN}" 2>/dev/null || { bad "[84] URL override 未按 feature 隔离"; S84_BAD=1; }
if grep -q "update-url-override" "${INSTALLER_ROOT}/scripts/build_desktop_release.sh" 2>/dev/null; then
  bad "[84] 发布构建脚本出现 update-url-override(假 release 入口绝不可进发布二进制)"; S84_BAD=1
fi
grep -q "manifest_fetch_three_outcomes" "$(pf_shell_rs_tests)" 2>/dev/null || { bad "[84] manifest 获取三态回归测试缺位"; S84_BAD=1; }
# 反向锚:签名制度已取消,残留即「半拆」状态(比有或无都危险)
for zombie in "UPDATE_MANIFEST_PUBKEY_HEX" "verify_manifest_signature" "HOROSA_UPDATE_REQUIRE_SIG" "ed25519"; do
  if grep -qi "${zombie}" "${S84_MAIN}" 2>/dev/null; then
    bad "[84] 签名制度已取消但 main.rs 残留 ${zombie}(半拆状态,拆干净或整体恢复)"; S84_BAD=1
  fi
done
grep -q "horosa-update-manifest-sign" "${INSTALLER_ROOT}/scripts/build_desktop_release.sh" 2>/dev/null && { bad "[84] build 脚本残留签名段(制度已取消)"; S84_BAD=1; }
[ "${S84_BAD}" = "0" ] && ok "[84] 事件镜像+假release隔离 全在位(签名制度已取消且拆净)"
}

seg_86() {
# 86. 增量八不变量(WS-1e):I3 三方 sha/I5 全量回退字段/I7 尺寸真值/I8 kill-switch 矩阵
#     (I1 合成校验+I2 边界 lockstep+I6 lock 进 tar 由seg_74强制;I4 差分门在 publish 内)
echo "[86] 增量八不变量(I3/I5/I7/I8)"
S86_BAD=0
S86_MAIN="$(pf_shell_rs_prod)"
# I8:四个 kill-switch + I4 门锚静态在位
for anchor in "HOROSA_UPDATE_FULL_ONLY" "HOROSA_DOWNLOAD_NO_RESUME" "HOROSA_EXTRACT_NATIVE" "HOROSA_MENU_UPDATE_LEGACY"; do
  grep -q "${anchor}" "${S86_MAIN}" 2>/dev/null || { bad "[86·I8] kill-switch ${anchor} 缺位"; S86_BAD=1; }
done
grep -q "HOROSA_ALLOW_LARGE_DELTA" "${INSTALLER_ROOT}/scripts/publish_github_release.sh" 2>/dev/null || { bad "[86·I4] publish 缺差分效率门"; S86_BAD=1; }
grep -q "HOROSA_DELTA_BUDGET_MB" "${INSTALLER_ROOT}/scripts/publish_github_release.sh" 2>/dev/null || { bad "[86·I4] 差分门缺预算参数"; S86_BAD=1; }
# I3/I5/I7:dist manifest 已产时做真值核对(manifest↔lock 逐名 sha / v1 全字段 / 尺寸↔实物)
S86_MANIFEST="${INSTALLER_ROOT}/dist/horosa-latest.json"
if [ -f "${S86_MANIFEST}" ]; then
  S86_RES="$(python3 - "${S86_MANIFEST}" "${INSTALLER_ROOT}/dist" <<'PY86'
import json, pathlib, sys
manifest = json.loads(pathlib.Path(sys.argv[1]).read_text())
dist = pathlib.Path(sys.argv[2])
problems = []
for key, entry in (manifest.get('platforms') or {}).items():
    # I5:v2 必含 v1 全量回退字段(老壳/降级路径的生命线)
    for field in ('appUrl', 'appSha256', 'runtimeUrl', 'runtimeSha256', 'runtimeVersion'):
        if not entry.get(field):
            problems.append(f"I5:{key} 缺 {field}")
    # I7:尺寸字段完备且与 dist 实物一致(检查更新「要下多大」的真值)
    for field, fname in (
        ('appSizeBytes', entry.get('appUrl', '').rsplit('/', 1)[-1]),
        ('runtimeSizeBytes', entry.get('runtimeUrl', '').rsplit('/', 1)[-1]),
    ):
        declared = entry.get(field)
        if declared is None:
            problems.append(f"I7:{key} 缺 {field}")
            continue
        f = dist / fname
        if f.is_file() and f.stat().st_size != declared:
            problems.append(f"I7:{key} {field}={declared} 与实物 {f.stat().st_size} 不一致({fname})")
    # I3:manifest.components ↔ lock ↔ 实物 逐名 sha 三方核对
    comps = entry.get('components') or []
    if comps:
        lock_path = dist / 'components' / 'components-lock.json'
        if not lock_path.is_file():
            problems.append('I3:dist/components/components-lock.json 缺失')
        else:
            lock = json.loads(lock_path.read_text())
            lock_sha = {c['name']: c['sha256'] for c in lock.get('components') or []}
            man_sha = {c['name']: c['sha256'] for c in comps}
            if set(lock_sha) != set(man_sha):
                problems.append(f"I3:{key} manifest/lock 部件集合漂移")
            for name in set(lock_sha) & set(man_sha):
                if lock_sha[name] != man_sha[name]:
                    problems.append(f"I3:{key} 部件 {name} manifest/lock sha 漂移")
print('; '.join(problems) if problems else 'OK')
PY86
)"
  if [ "${S86_RES}" = "OK" ]; then
    ok "[86] dist manifest I3/I5/I7 真值核对通过"
  else
    bad "[86] 不变量违约: ${S86_RES}"; S86_BAD=1
  fi
else
  warn "[86] dist 未打包,跳过 I3/I5/I7 真值核对(I4/I8 静态锚已核)"
fi
[ "${S86_BAD}" = "0" ] && ok "[86] 增量八不变量 全在位"
}

seg_98() {
# ── [98] kill-atomic 对换(U-A):renamex_np 单点互换+启动撕裂探测 ──────────────
echo "[98] kill-atomic 对换"
S98_BAD=0
S98_MAIN="$(pf_shell_rs_prod)"
S98_TOML="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/Cargo.toml"
grep -q 'renamex_np' "${S98_MAIN}" || { bad "[98] 缺 renamex_np 系统调用"; S98_BAD=1; }
grep -q 'RENAME_SWAP' "${S98_MAIN}" || { bad "[98] 缺 RENAME_SWAP 旗标"; S98_BAD=1; }
grep -q 'fn atomic_swap_dirs' "${S98_MAIN}" || { bad "[98] 缺 atomic_swap_dirs"; S98_BAD=1; }
grep -q 'fn repair_torn_runtime_slots' "${S98_MAIN}" || { bad "[98] 缺启动撕裂探测 repair_torn_runtime_slots"; S98_BAD=1; }
grep -q 'HOROSA_SWAP_DISABLE' "${S98_MAIN}" || { bad "[98] 缺回退分支逃生阀 HOROSA_SWAP_DISABLE"; S98_BAD=1; }
grep -qE '^libc' "${S98_TOML}" || { bad "[98] Cargo.toml 缺 libc 依赖"; S98_BAD=1; }
# 两处对换必须都走 swap(全量 extracted↔current、增量 stage↔current);删 swap 只留两段 rename=静默回退,红
grep -q 'atomic_swap_dirs(&extracted_runtime, &final_runtime)' "${S98_MAIN}" || { bad "[98] 全量对换未走 swap"; S98_BAD=1; }
grep -q 'atomic_swap_dirs(&stage, &current)' "${S98_MAIN}" || { bad "[98] 增量对换未走 swap"; S98_BAD=1; }
grep -q 'repair_torn_runtime_slots(root)' "${S98_MAIN}" || { bad "[98] bootstrap 未接线撕裂探测"; S98_BAD=1; }
grep -q 'rust.torn_slot_repaired' "${S98_MAIN}" || { bad "[98] 缺撕裂修复账本段"; S98_BAD=1; }
grep -q 'atomic_swap_dirs_exchanges_trees_on_apfs' "$(pf_shell_rs_tests)" || { bad "[98] 缺 swap 回归测试"; S98_BAD=1; }
grep -q 'torn_slot_repair_promotes_complete_candidate' "$(pf_shell_rs_tests)" || { bad "[98] 缺撕裂修复回归测试"; S98_BAD=1; }
[ "${S98_BAD}" = "0" ] && ok "[98] kill-atomic 对换链在位(swap 双点+撕裂探测+回退阀)"
}

seg_102() {
# ── [102] 部件级重试(U-E):单部件先重试再整链降级 ──────────────────────────
echo "[102] 部件级重试"
S102_BAD=0
S102_MAIN="$(pf_shell_rs_prod)"
grep -q 'COMPONENT_RETRY_MAX' "${S102_MAIN}" || { bad "[102] 缺 COMPONENT_RETRY_MAX"; S102_BAD=1; }
grep -q 'fn download_component_with_retry' "${S102_MAIN}" || { bad "[102] 缺重试壳函数"; S102_BAD=1; }
grep -q 'download_component_with_retry(' "${S102_MAIN}" || { bad "[102] 逐部件循环未走重试壳"; S102_BAD=1; }
grep -q '次重试' "${S102_MAIN}" || { bad "[102] 缺重试可视事件文案"; S102_BAD=1; }
grep -q 'component_download_retry_then_success_and_exhaust' "$(pf_shell_rs_tests)" || { bad "[102] 缺重试回归测试"; S102_BAD=1; }
grep -qF '部件级重试后语义不变' "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_update_experience_local.sh" || { bad "[102] s2 剧本缺重试语义注记"; S102_BAD=1; }
[ "${S102_BAD}" = "0" ] && ok "[102] 部件级重试在位(sha 失配全新下/网络错续传接力)"
}

seg_99() {
# ── [99] .app helper 加固(U-B):stage-first+主二进制 swap 旗标+失败重开臂 ──
echo "[99] helper 加固"
S99_BAD=0
S99_MAIN="$(pf_shell_rs_prod)"
# swap 旗标两处各一条精确锚(按总数计会被注释 / 测试凑数):入口分派 + helper 模板里的调用
grep -qF 'args[1] == "--horosa-atomic-swap"' "${S99_MAIN}" || { bad "[99] 入口缺 --horosa-atomic-swap 分派"; S99_BAD=1; }
grep -qF -- '--horosa-atomic-swap \"${{STAGE_TARGET}}\" \"${{TARGET}}\"' "${S99_MAIN}" || { bad "[99] helper 模板不再经 --horosa-atomic-swap 对换主二进制"; S99_BAD=1; }
grep -q 'fn run_swap_cli' "${S99_MAIN}" || { bad "[99] 缺 swap CLI 本体"; S99_BAD=1; }
grep -q 'update-stage.app' "${S99_MAIN}" || { bad "[99] helper 缺 stage-first 暂存位"; S99_BAD=1; }
grep -q 'if ! install_app; then' "${S99_MAIN}" || { bad "[99] helper 缺 install 失败守卫臂"; S99_BAD=1; }
grep -q 'reopening previous app' "${S99_MAIN}" || { bad "[99] helper 失败臂缺重开旧 app"; S99_BAD=1; }
grep -q 'insufficient disk space' "${S99_MAIN}" || { bad "[99] helper 缺磁盘预检"; S99_BAD=1; }
# 反向锚:危险旧序(新版长时间 ditto 直写 TARGET)不得回潮
grep -q 'ditto \\"\${{SRC}}\\" \\"\${{TARGET}}\\"' "$(pf_shell_rs_prod_all)" && { bad "[99] helper 回潮 ditto 直写 TARGET(长窗口)"; S99_BAD=1; }
grep -q 'update_helper_script_stages_before_swap' "$(pf_shell_rs_tests)" || { bad "[99] 缺 helper 契约测试"; S99_BAD=1; }
grep -q 'atomic_swap_cli_flag_swaps_and_exits' "$(pf_shell_rs_tests)" || { bad "[99] 缺 swap CLI 测试"; S99_BAD=1; }
[ "${S99_BAD}" = "0" ] && ok "[99] helper 加固在位(stage-first+swap 旗标+失败重开+磁盘预检)"
}

seg_100() {
# ── [100] staged 持久化+断点恢复(U-C) ─────────────────────────────────────
echo "[100] staged 持久化"
S100_BAD=0
S100_MAIN="$(pf_shell_rs_prod)"
grep -q 'staged-update.json' "${S100_MAIN}" || { bad "[100] 缺暂存档文件"; S100_BAD=1; }
grep -q 'fn load_staged_update_file_at' "${S100_MAIN}" || { bad "[100] 缺读档函数"; S100_BAD=1; }
grep -q 'STAGED_UPDATE_MAX_AGE_MS' "${S100_MAIN}" || { bad "[100] 缺过期常量"; S100_BAD=1; }
grep -q 'rust.staged_update_restored' "${S100_MAIN}" || { bad "[100] 缺恢复账本段"; S100_BAD=1; }
grep -q '此前已下载完成' "${S100_MAIN}" || { bad "[100] 缺恢复 ready 独有文案(s5 锚)"; S100_BAD=1; }
# 读档必须逐资产 sha 重验(load 函数体内含 sha256_digest)
awk '/fn load_staged_update_file_at/,/^}/' "${S100_MAIN}" | pipe_has 'sha256_digest' || { bad "[100] 读档未逐资产重验 sha"; S100_BAD=1; }
# 写点+两清点+部件档清理都在
grep -q 'persist_staged_update_file(app, &staged)' "${S100_MAIN}" || { bad "[100] 下载完成未落盘"; S100_BAD=1; }
S100_CLEARS=$(grep -c 'clear_staged_update_file(app)' "${S100_MAIN}" 2>/dev/null || true)
[ "${S100_CLEARS}" -ge 2 ] || { bad "[100] 消费清点 ${S100_CLEARS} < 2(helper 交接+runtime-only 成功)"; S100_BAD=1; }
S100_CLEANUPS=$(grep -c 'cleanup_consumed_component_archives(&staged)' "${S100_MAIN}" 2>/dev/null || true)
[ "${S100_CLEANUPS}" -ge 2 ] || { bad "[100] 部件档清理点 ${S100_CLEANUPS} < 2(磁盘漏回潮)"; S100_BAD=1; }
grep -q 'staged_update_file_roundtrip_and_sha_gate' "$(pf_shell_rs_tests)" || { bad "[100] 缺往返/篡改回归测试"; S100_BAD=1; }
grep -q "'此前已下载完成'" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_update_experience_local.sh" || { bad "[100] 假 release 缺 s5 断言"; S100_BAD=1; }
[ "${S100_BAD}" = "0" ] && ok "[100] staged 持久化断点恢复在位(sha 门+过期门+双清点)"
}

seg_101() {
# ── [101] 更新链防降级(U-D):单调判定+双逃生阀+内联手抄零回潮 ──────────────
echo "[101] 更新防降级"
S101_BAD=0
S101_MAIN="$(pf_shell_rs_prod)"
grep -q 'fn compute_runtime_update_decision' "${S101_MAIN}" || { bad "[101] 缺单一判定函数 compute_runtime_update_decision"; S101_BAD=1; }
grep -q 'runtime_version_rank(remote)' "${S101_MAIN}" || { bad "[101] 判定未走 runtime_version_rank 单调比较"; S101_BAD=1; }
grep -q 'HOROSA_ALLOW_DOWNGRADE' "${S101_MAIN}" || { bad "[101] 缺 env 逃生阀 HOROSA_ALLOW_DOWNGRADE"; S101_BAD=1; }
grep -q 'allowDowngrade' "${S101_MAIN}" || { bad "[101] 缺 manifest 逃生阀字段 allowDowngrade"; S101_BAD=1; }
grep -q 'rust.update_downgrade_blocked' "${S101_MAIN}" || { bad "[101] 缺降级拦截账本段"; S101_BAD=1; }
# 反向锚:runtime 判定的「remote.trim() != local.trim()」内联手抄曾散在 3 处,回潮即红
S101_NEQ=$(grep -c 'remote.trim() != local.trim()' "${S101_MAIN}" 2>/dev/null || true)
[ "${S101_NEQ}" = "0" ] || { bad "[101] runtime 判定内联手抄回潮 ${S101_NEQ} 处(必须走统一入口)"; S101_BAD=1; }
# 消费面:菜单/静默检查/后台下载/自动检查 四处必须都走统一入口
S101_CALLS=$(grep -cE 'runtime_update_decision\(&?app' "${S101_MAIN}" 2>/dev/null || true)
[ "${S101_CALLS}" -ge 4 ] || { bad "[101] runtime_update_decision 消费点 ${S101_CALLS} < 4(有路径漏收口)"; S101_BAD=1; }
grep -q 'allowDowngrade' "${REPO_ROOT}/Horosa_Desktop_Installer/INCREMENTAL_UPDATE_SOP.md" || { bad "[101] SOP §4.3 缺 allowDowngrade 退版剧本"; S101_BAD=1; }
grep -q 'runtime_update_monotonic_gate' "$(pf_shell_rs_tests)" || { bad "[101] 缺单调判定回归测试"; S101_BAD=1; }
[ "${S101_BAD}" = "0" ] && ok "[101] 防降级链在位(单调判定+双逃生阀+手抄零回潮)"
}

seg_104() {
# ── [104] 耐久更新台账+轮转保代+诊断包导出(U-G) ───────────────────────────
echo "[104] 更新台账/诊断包"
S104_BAD=0
S104_MAIN="$(pf_shell_rs_prod)"
S104_DHTML="${REPO_ROOT}/Horosa_Desktop_Installer/web/diagnostics.html"
S104_DJS="${REPO_ROOT}/Horosa_Desktop_Installer/web/diagnostics.js"
grep -q 'update-history.jsonl' "${S104_MAIN}" || { bad "[104] 缺耐久台账文件"; S104_BAD=1; }
grep -q 'fn rotate_log_keep_one' "${S104_MAIN}" || { bad "[104] 缺轮转保代函数"; S104_BAD=1; }
# 写点覆盖:staged_ready/download_error/apply_begin/helper_handoff/apply_runtime_ok/
# apply_failed/install_confirmed/watchdog_rollback/downgrade_blocked/check_failed ≥10 调用
S104_WRITES=$(grep -c 'append_update_history(' "${S104_MAIN}" 2>/dev/null || true)
[ "${S104_WRITES}" -ge 10 ] || { bad "[104] 台账写点 ${S104_WRITES} < 10(事件面漏挂)"; S104_BAD=1; }
grep -q '"event": "install_confirmed"' "${S104_MAIN}" || { bad "[104] 缺 vX→vY 结果闭环行"; S104_BAD=1; }
# 反向锚:updater-events.log 的 File::create 截断毁证旧样式不得回潮(排除注释行——
# 函数内说明性注释提到旧样式字样不算回潮)
awk '/fn log_updater_event/,/^}/' "${S104_MAIN}" | grep -v '^[[:space:]]*//' | pipe_has 'File::create' && { bad "[104] events 日志截断毁证旧样式回潮"; S104_BAD=1; }
grep -q 'fn export_diagnostics_bundle' "${S104_MAIN}" || { bad "[104] 缺一键诊断包命令"; S104_BAD=1; }
awk '/generate_handler!\[/,/\]\)/' "${S104_MAIN}" | pipe_has 'export_diagnostics_bundle' || { bad "[104] 诊断包命令未注册"; S104_BAD=1; }
grep -q 'update_history_lines' "${S104_MAIN}" || { bad "[104] 诊断载荷缺台账尾部"; S104_BAD=1; }
grep -q 'updateHistoryOutput' "${S104_DHTML}" || { bad "[104] 诊断页缺更新历史卡"; S104_BAD=1; }
grep -q 'exportBundleBtn' "${S104_DHTML}" || { bad "[104] 诊断页缺导出按钮"; S104_BAD=1; }
grep -q 'export_diagnostics_bundle' "${S104_DJS}" || { bad "[104] 诊断页未接导出命令"; S104_BAD=1; }
grep -q 'update_history_append_and_rotation_keeps_tail' "$(pf_shell_rs_tests)" || { bad "[104] 缺台账回归测试"; S104_BAD=1; }
grep -q 'rotate_log_keep_one_generation' "$(pf_shell_rs_tests)" || { bad "[104] 缺轮转保代回归测试"; S104_BAD=1; }
# 壳自带三页(启动器 / 设置 / 诊断)的报错先换成一句中文再上屏(系统原文多是英文 + os error 码);诊断页另列原始信息、资产状态显示中文
if command -v node >/dev/null 2>&1; then
  node "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/test_shell_error_text.js" "${REPO_ROOT}" >/dev/null 2>&1 \
    || { bad "[104] 壳自带页面报错文字自检不过(node Horosa_Desktop_Installer/scripts/test_shell_error_text.js 看明细)"; S104_BAD=1; }
else
  bad "[104] 缺 node,跑不了壳自带页面报错文字自检"; S104_BAD=1
fi
[ "${S104_BAD}" = "0" ] && ok "[104] 更新台账/诊断包在位(写点 ${S104_WRITES}/轮转保代/一键导出)"
}

seg_105() {
# ── [105] 周期检查+节流+检查失败显式化(U-H) ──────────────────────────────
echo "[105] 更新检查节流/周期"
S105_BAD=0
S105_MAIN="$(pf_shell_rs_prod)"
S105_UN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/update/UpdateNotifier.js"
grep -q 'last-update-check.json' "${S105_MAIN}" || { bad "[105] 缺检查戳记文件"; S105_BAD=1; }
grep -q 'fn should_run_auto_check' "${S105_MAIN}" || { bad "[105] 缺节流纯函数"; S105_BAD=1; }
grep -q 'fn run_auto_update_check' "${S105_MAIN}" || { bad "[105] 缺自动检查本体函数"; S105_BAD=1; }
grep -q 'AUTO_CHECK_CYCLE_SECS' "${S105_MAIN}" || { bad "[105] 缺 24h 周期常量"; S105_BAD=1; }
grep -q 'HOROSA_UPDATE_CHECK_INTERVAL_SECS' "${S105_MAIN}" || { bad "[105] 缺 dev 周期覆盖 env"; S105_BAD=1; }
grep -q 'rust.update_check_failed' "${S105_MAIN}" || { bad "[105] 检查失败未落账本"; S105_BAD=1; }
grep -q '"check-failed"' "${S105_MAIN}" || { bad "[105] 检查失败未发显式事件"; S105_BAD=1; }
# 反向锚:检查失败只 eprintln 吞掉的旧样式(auto check skipped)不得回潮
grep -q 'auto check skipped' "$(pf_shell_rs_prod_all)" && { bad "[105] 检查失败静默吞掉旧样式回潮"; S105_BAD=1; }
# 手动检查两路径写戳记(菜单+前端 silent);消费点 ≥3(auto+2 手动)
S105_STAMPS=$(grep -c 'write_update_check_stamp(' "${S105_MAIN}" 2>/dev/null || true)
[ "${S105_STAMPS}" -ge 3 ] || { bad "[105] 检查戳记写点 ${S105_STAMPS} < 3(手动路径漏写)"; S105_BAD=1; }
grep -q "check-failed" "${S105_UN}" || { bad "[105] 前端缺 check-failed 低打扰处理"; S105_BAD=1; }
grep -q "downgrade-blocked" "${S105_UN}" || { bad "[105] 前端缺 downgrade-blocked 提示"; S105_BAD=1; }
grep -q 'auto_check_throttle_gate' "$(pf_shell_rs_tests)" || { bad "[105] 缺节流回归测试"; S105_BAD=1; }
[ "${S105_BAD}" = "0" ] && ok "[105] 检查节流/周期/失败显式化在位"
}

seg_106() {
# ── [106] 安装链收尾组合锚(U-I:编码钉死/CLT桩清零/降级门/六包门/缓存实物锚/本机直连钉/搬迁) ──
echo "[106] 安装链收尾"
S106_BAD=0
S106_MAIN="$(pf_shell_rs_prod)"
S106_START="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
S106_POST="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template"
# G1:三条 Java 启动路径都钉 file.encoding+sun.jnu.encoding;LANG 兜底(脚本+壳)
S106_ENC=$(grep -c 'Dfile.encoding=UTF-8' "${S106_START}" 2>/dev/null || true)
[ "${S106_ENC}" -ge 3 ] || { bad "[106] file.encoding 钉死 ${S106_ENC} < 3 条启动路径"; S106_BAD=1; }
S106_JNU=$(grep -c 'Dsun.jnu.encoding=UTF-8' "${S106_START}" 2>/dev/null || true)
[ "${S106_JNU}" -ge 3 ] || { bad "[106] sun.jnu.encoding 钉死 ${S106_JNU} < 3"; S106_BAD=1; }
grep -q 'export LANG=zh_CN.UTF-8' "${S106_START}" || { bad "[106] start 脚本缺 LANG 兜底"; S106_BAD=1; }
grep -q '"LANG"' "${S106_MAIN}" || { bad "[106] 壳 spawn 缺 LANG 兜底"; S106_BAD=1; }
# G2:postinstall 零 /usr/bin/python3 实调(注释里提及不算——查行首非注释调用)
grep -vE '^\s*#' "${S106_POST}" | pipe_has '/usr/bin/python3' && { bad "[106] postinstall 回潮 /usr/bin/python3(CLT 弹窗桩)"; S106_BAD=1; }
# G3:降级门
grep -q 'downgrade guard' "${S106_POST}" || { bad "[106] postinstall 缺 runtime 降级门"; S106_BAD=1; }
grep -q 'sort -V' "${S106_POST}" || { bad "[106] 降级门缺 sort -V 版本比较"; S106_BAD=1; }
# G4:可用门六包(壳+postinstall 两处)
grep -q "'cherrypy','jsonpickle','swisseph','cn2an','sxtwl','cnlunar'" "${S106_MAIN}" || { bad "[106] 壳可用门未对齐 6 包"; S106_BAD=1; }
grep -q 'cherrypy, jsonpickle, swisseph, cn2an, sxtwl, cnlunar' "${S106_POST}" || { bad "[106] postinstall 可用门未对齐 6 包"; S106_BAD=1; }
# G5:健康缓存实物锚
grep -q 'fn runtime_health_probe_files_present' "${S106_MAIN}" || { bad "[106] 缺健康缓存实物锚"; S106_BAD=1; }
grep -q 'runtime_health_probe_files_present(runtime_dir)' "${S106_MAIN}" || { bad "[106] 快路径未接实物锚"; S106_BAD=1; }
# G7:本机直连钉死(三条启动路径 + CDS 自训各带 HTTP 与 SOCKS 两种例外;代码层根修见 [27],这里是双保险)
S106_NPH=$(grep -c 'Dhttp.nonProxyHosts=localhost' "${S106_START}" 2>/dev/null || true)
[ "${S106_NPH}" -ge 4 ] || { bad "[106] http.nonProxyHosts 钉死 ${S106_NPH} < 4"; S106_BAD=1; }
S106_SNPH=$(grep -c 'DsocksNonProxyHosts=localhost' "${S106_START}" 2>/dev/null || true)
[ "${S106_SNPH}" -ge 4 ] || { bad "[106] socksNonProxyHosts 钉死 ${S106_SNPH} < 4"; S106_BAD=1; }
# 带 useSystemProxies 的每一行都必须同时带两种例外(新加启动路径漏带 = 红)
S106_USP_BARE=$(grep -a 'Djava.net.useSystemProxies=true' "${S106_START}" 2>/dev/null | grep -av '^[[:space:]]*#' | grep -av 'DsocksNonProxyHosts=localhost' | grep -c . || true)
[ "${S106_USP_BARE:-0}" = "0" ] || { bad "[106] ${S106_USP_BARE} 条带 useSystemProxies 的启动行缺 socksNonProxyHosts"; S106_BAD=1; }
# G8:Translocation 搬迁菜单
grep -q 'MENU_RELOCATE_APP' "${S106_MAIN}" || { bad "[106] 缺搬迁菜单"; S106_BAD=1; }
grep -q 'fn relocate_app_to_applications' "${S106_MAIN}" || { bad "[106] 缺搬迁实现"; S106_BAD=1; }
[ "${S106_BAD}" = "0" ] && ok "[106] 安装链收尾在位(编码×${S106_ENC}/降级门/六包门/实物锚/直连钉 HTTP×${S106_NPH} SOCKS×${S106_SNPH}/搬迁)"
}

seg_107() {
# ── seg_107 helper 全量 runtime 原子化(手术收进 TARGET 二进制/定义不执行/wait 后时序/
#     previous 保留/撕裂候选 _update/失败臂不写标记/孤儿清扫/旧危险序仅存于 _legacy 逃生阀) ──
echo "[${PF_NO}] helper 全量 runtime 原子化"
S107_BAD=0
S107_MAIN="$(pf_shell_rs_prod)"
# ① 新协议生成器:非 legacy 函数体必须经 --horosa-runtime-swap,且零两段 mv 危险序
S107_NEWBODY=$(awk '/^(pub\(crate\) )?fn build_single_runtime_update_command\(/{f=1} /^(pub\(crate\) )?fn build_single_runtime_update_command_legacy\(/{f=0} f{print}' "${S107_MAIN}")
printf '%s' "${S107_NEWBODY}" | pipe_has -- '--horosa-runtime-swap' || { bad "[${PF_NO}] 新协议生成器未经 TARGET 二进制对换"; S107_BAD=1; }
printf '%s' "${S107_NEWBODY}" | pipe_has -F 'mv \"${WORK_ROOT}/runtime-payload\"' && { bad "[${PF_NO}] 新协议生成器回潮两段 mv 危险序"; S107_BAD=1; }
# ② 逃生阀成对:legacy 函数 + 开关门都在(单删其一=半拆)
grep -q 'fn build_single_runtime_update_command_legacy' "${S107_MAIN}" || { bad "[${PF_NO}] 缺 legacy 逃生阀函数"; S107_BAD=1; }
grep -q 'fn helper_runtime_swap_enabled' "${S107_MAIN}" || { bad "[${PF_NO}] 缺 HOROSA_HELPER_RUNTIME_SWAP 开关门"; S107_BAD=1; }
# ③ CLI 钩 + 协议统一(CLI 必须走 extract_runtime_archive_with 同一协议 → previous 保留/版本闸/磁盘预检全继承)
grep -q 'fn run_runtime_swap_cli' "${S107_MAIN}" || { bad "[${PF_NO}] 缺 runtime-swap CLI 实现"; S107_BAD=1; }
awk '/^(pub\(crate\) )?fn run_runtime_swap_cli\(/{f=1} f&&/^}$/{exit} f{print}' "${S107_MAIN}" | pipe_has 'extract_runtime_archive_with' || { bad "[${PF_NO}] CLI 未复用进程内 extract 协议(previous 保留失守)"; S107_BAD=1; }
# ④ 模板时序:runtime 调用必须在 install_app 之后(sleep 1 之后)且失败臂 exit 73 在 mark 之前
grep -qF 'sleep 1\nif ! run_runtime_installs; then' "${S107_MAIN}" || { bad "[${PF_NO}] 模板时序失守(runtime 未在 install_app 之后)"; S107_BAD=1; }
grep -qF 'exit 73\nfi\nseal_shared_runtime || true\nmark_update_complete \"pending_manual\"' "${S107_MAIN}" || { bad "[${PF_NO}] 失败臂/完成标记相对序失守(铁律14)"; S107_BAD=1; }
# ⑤ 撕裂候选含旧协议暂存位 _update/runtime-payload
grep -qF 'root.join("_update").join("runtime-payload")' "${S107_MAIN}" || { bad "[${PF_NO}] 撕裂候选缺 _update(旧协议过渡跳撕裂成孤儿)"; S107_BAD=1; }
# ⑥ 孤儿清扫 + 账本段
grep -q 'fn sweep_stale_runtime_stage_dirs' "${S107_MAIN}" || { bad "[${PF_NO}] 缺孤儿暂存清扫"; S107_BAD=1; }
grep -q 'rust.stale_stage_swept' "${S107_MAIN}" || { bad "[${PF_NO}] 清扫缺账本段"; S107_BAD=1; }
# ⑦ helper_handoff 事件带协议指纹(排障时区分新旧协议)
grep -q '"helperProtocol"' "${S107_MAIN}" || { bad "[${PF_NO}] helper_handoff 缺协议指纹字段"; S107_BAD=1; }
# ⑧ 回归测试在位(契约钉住:时序/铁律14/开关闭环/版本闸/previous 保留/收养)
for t in update_helper_script_runtime_swap_after_wait_and_app update_helper_runtime_failure_arm_never_marks update_helper_legacy_killswitch_restores_old_template runtime_swap_cli_rejects_version_mismatch runtime_swap_cli_promotes_and_keeps_previous repair_torn_slots_adopts_legacy_update_dir; do
  grep -q "fn ${t}" "$(pf_shell_rs_tests)" || { bad "[${PF_NO}] 缺回归测试 ${t}"; S107_BAD=1; }
done
[ "${S107_BAD}" = "0" ] && ok "[${PF_NO}] helper 全量 runtime 原子化在位(CLI 协议统一/时序/previous 保留/撕裂候选/清扫/测试×6)"
}

seg_108() {
# ── seg_108 跨进程手术互斥锁(flock 五叶子/上层禁取反锚/多实例更新感知) ──
echo "[${PF_NO}] 跨进程手术互斥锁"
S108_BAD=0
S108_MAIN="$(pf_shell_rs_prod)"
S108_BANNER="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/common/ServiceStatusBanner.js"
# ① 锁原语三件:锁文件名常量 / flock 系调 / 开关门
grep -q '\.horosa-surgery\.lock' "${S108_MAIN}" || { bad "[${PF_NO}] 缺锁文件名常量"; S108_BAD=1; }
grep -q 'libc::flock(fd, libc::LOCK_EX | libc::LOCK_NB)' "${S108_MAIN}" || { bad "[${PF_NO}] 缺 flock 非阻塞轮询"; S108_BAD=1; }
grep -q 'HOROSA_SURGERY_LOCK_DISABLE' "${S108_MAIN}" || { bad "[${PF_NO}] 缺锁开关门"; S108_BAD=1; }
# ② 五叶各含锁调用(required×2 + optional×3),少一叶=写窗口裸奔
for leaf in extract_runtime_archive_with apply_component_updates_with; do
  awk "/^(pub\(crate\) )?fn ${leaf}\(/{f=1} f&&/^}\$/{exit} f{print}" "${S108_MAIN}" | pipe_has 'acquire_surgery_lock_required' || { bad "[${PF_NO}] ${leaf} 缺 required 锁"; S108_BAD=1; }
done
for leaf in rollback_runtime_to_previous repair_torn_runtime_slots cleanup_previous_slots; do
  awk "/^(pub\(crate\) )?fn ${leaf}\(/{f=1} f&&/^}\$/{exit} f{print}" "${S108_MAIN}" | pipe_has 'acquire_surgery_lock_optional' || { bad "[${PF_NO}] ${leaf} 缺 optional 锁"; S108_BAD=1; }
done
# ③ 反向锚:锁调用总数=5(五叶各一)+定义处;上层乱取=同进程 fd 互斥自死锁
S108_REQ=$(grep -c 'acquire_surgery_lock_required(' "${S108_MAIN}" || true)
S108_OPT=$(grep -c 'acquire_surgery_lock_optional(' "${S108_MAIN}" || true)
[ "${S108_REQ}" -eq 3 ] || { bad "[${PF_NO}] required 锁出现 ${S108_REQ} 次 ≠ 3(定义1+两叶;上层禁取)"; S108_BAD=1; }
[ "${S108_OPT}" -eq 4 ] || { bad "[${PF_NO}] optional 锁出现 ${S108_OPT} 次 ≠ 4(定义1+三叶;上层禁取)"; S108_BAD=1; }
# ④ 收养复核:repair 拿锁后必须复核 current(等锁期间对方可能已产出)
awk '/^(pub\(crate\) )?fn repair_torn_runtime_slots\(/{f=1} f&&/^}$/{exit} f{print}' "${S108_MAIN}" | pipe_has '拿锁后复核' || { bad "[${PF_NO}] repair 缺拿锁后复核"; S108_BAD=1; }
# ⑤ 多实例更新感知(V11):纯函数+supervisor 接线+账本+前端信息横幅
grep -q 'fn runtime_change_step' "${S108_MAIN}" || { bad "[${PF_NO}] 缺 runtime_change_step 纯函数"; S108_BAD=1; }
grep -q 'rust.runtime_updated_elsewhere' "${S108_MAIN}" || { bad "[${PF_NO}] 缺多实例更新账本段"; S108_BAD=1; }
grep -q 'runtime_updated_elsewhere' "${S108_BANNER}" || { bad "[${PF_NO}] 前端横幅未接多实例更新事件"; S108_BAD=1; }
# ⑥ 账本段 + 回归测试
grep -q 'rust.surgery_lock_timeout' "${S108_MAIN}" || { bad "[${PF_NO}] 缺锁超时账本段"; S108_BAD=1; }
for t in surgery_lock_blocks_second_acquire_same_process surgery_lock_cross_process_contention surgery_lock_released_on_sigkill surgery_lock_disable_env_bypasses torn_repair_skips_when_locked runtime_change_step_detects_version_drift; do
  grep -q "fn ${t}" "$(pf_shell_rs_tests)" || { bad "[${PF_NO}] 缺回归测试 ${t}"; S108_BAD=1; }
done
[ "${S108_BAD}" = "0" ] && ok "[${PF_NO}] 跨进程手术锁在位(五叶插桩/上层禁取反锚/复核/V11 感知/测试×6)"
}

seg_109() {
# ── seg_109 API 回退源 sha 闭环(manifest asset 取回 / 守门无条件 / notify-only 不触网) ──
echo "[${PF_NO}] API 回退源 sha 闭环"
S109_BAD=0
S109_MAIN="$(pf_shell_rs_prod)"
S109_NOTIFIER="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/update/UpdateNotifier.js"
# ① 反向锚(最重要):旧「按来源豁免 sha 守门」条件式零回潮——无 sha 绝不自动安装
grep -q 'plan.source == UpdateSource::Manifest' "$(pf_shell_rs_prod_all)" && { bad "[${PF_NO}] sha 守门回潮按来源豁免(GithubApi 回退将无 sha 自动安装)"; S109_BAD=1; }
# ② 守门无条件在位(两处消费点:菜单检查 + 后台下载)
S109_GUARD=$(grep -c 'plan.latest_version > current && plan.app_sha256.is_none()' "${S109_MAIN}" || true)
[ "${S109_GUARD}" -ge 2 ] || { bad "[${PF_NO}] 无条件 app sha 守门 ${S109_GUARD} < 2 处"; S109_BAD=1; }
S109_RTG=$(grep -c 'runtime_needs_update && plan.runtime_sha256.is_none()' "${S109_MAIN}" || true)
[ "${S109_RTG}" -ge 2 ] || { bad "[${PF_NO}] 无条件 runtime sha 守门 ${S109_RTG} < 2 处"; S109_BAD=1; }
# ③ 一级回退:经 API 定位 manifest asset 取回真 manifest(引用 update_manifest_name 配置)
grep -q 'fn fetch_manifest_via_release_asset' "${S109_MAIN}" || { bad "[${PF_NO}] 缺 manifest asset 取回"; S109_BAD=1; }
awk '/^(pub\(crate\) )?fn fetch_manifest_via_release_asset\(/{f=1} f&&/^}$/{exit} f{print}' "${S109_MAIN}" | pipe_has 'a.name == manifest_name' || { bad "[${PF_NO}] asset 取回未按 updateManifestName 匹配"; S109_BAD=1; }
grep -q 'UpdateSource::ManifestViaApi' "${S109_MAIN}" || { bad "[${PF_NO}] 缺 ManifestViaApi 来源变体"; S109_BAD=1; }
# ④ 纯映射单一真值(主通道与回退通道共用,防手抄分叉)
grep -q 'fn plan_from_manifest' "${S109_MAIN}" || { bad "[${PF_NO}] 缺 plan_from_manifest 纯映射"; S109_BAD=1; }
#   计数只数产品代码(测试里的调用不许替产品凑数):定义 1 + 主通道 1 + 回退 1;测试另锚
S109_PFM=$(grep -c 'plan_from_manifest(' "${S109_MAIN}" || true)
[ "${S109_PFM}" -ge 3 ] || { bad "[${PF_NO}] plan_from_manifest 产品代码里 ${S109_PFM} 处 < 3(定义1+主通道1+回退1)"; S109_BAD=1; }
[ "$(grep -c 'plan_from_manifest(' "$(pf_shell_rs_tests)" || true)" -ge 1 ] || { bad "[${PF_NO}] 缺 plan_from_manifest 测试"; S109_BAD=1; }
# ⑤ 二级降级 notify-only:plan 字段 + 三消费点短路 + 账本 + 台账
grep -q 'notify_only: bool' "${S109_MAIN}" || { bad "[${PF_NO}] UpdatePlan 缺 notify_only"; S109_BAD=1; }
grep -q 'rust.update_notify_only' "${S109_MAIN}" || { bad "[${PF_NO}] 缺 notify-only 账本段"; S109_BAD=1; }
grep -q 'rust.update_manifest_via_api' "${S109_MAIN}" || { bad "[${PF_NO}] 缺 asset 取回账本段"; S109_BAD=1; }
grep -q '"event": "notify_only"' "${S109_MAIN}" || { bad "[${PF_NO}] notify-only 未写耐久台账"; S109_BAD=1; }
grep -q '"phase": "notify-only"' "${S109_MAIN}" || { bad "[${PF_NO}] 缺 notify-only 事件"; S109_BAD=1; }
awk '/^(pub\(crate\) )?fn run_background_update_download\(/{f=1} f&&/^}$/{exit} f{print}' "${S109_MAIN}" | pipe_has 'if plan.notify_only' || { bad "[${PF_NO}] 后台下载未短路 notify-only(会触网无 sha 下载)"; S109_BAD=1; }
# ⑤b 早先安装包留下「别的账户所有、所有账户可写」的共享运行环境:App 里不提权,这一次只通知、引导完整安装包(postinstall 以 root 收权限)
grep -qF 'apply_shared_tree_policy(&mut plan, legacy_open_shared_tree());' "${S109_MAIN}" && grep -qF 'pub(crate) fn legacy_open_shared_tree_at(' "${S109_MAIN}" && grep -qF 'fn legacy_open_shared_tree_detected_and_forces_full_pkg' "$(pf_shell_rs_tests)" \
  || { bad "[${PF_NO}] 旧共享树权限:检测 / 强制完整安装包 / 回归测试缺失"; S109_BAD=1; }
# ⑤c 检测范围 = 安装器封权范围(共享根本身 / downloads / install-source.json 也探);检查只读(偏好 / 诊断页读它,不许顺手 chmod -R),
#    本账户名下的由用户在设置页确认后后台收紧;自愈用缓存归档前核权限与安装记录里的 sha256(postinstall 写进 install-source.json)
grep -qF 'const SHARED_ROOT_PROBES: &[&str] = &["", "downloads", "install-source.json"];' "${S109_MAIN}" \
  && ! awk '/^pub\(crate\) fn inspect_shared_tree_at\(/{f=1} f&&/^}$/{exit} f{print}' "${S109_MAIN}" | pipe_has 'seal_tree_permissions' \
  && grep -qF 'if let Err(why) = cached_archive_trust(archive) {' "${S109_MAIN}" && grep -qF 'pub(crate) async fn seal_shared_runtime_permissions_command(' "${S109_MAIN}" \
  && grep -qF "invoke('seal_shared_runtime_permissions_command')" "${INSTALLER_ROOT}/web/settings.js" \
  && grep -qF '"runtimeArchiveSha256": "%s"' "${INSTALLER_ROOT}/installer-scripts/postinstall.template" \
  && [ "$(grep -acE 'fn (legacy_open_shared_root_downloads_and_marker_detected|cached_runtime_archive_trust_checks_perms_and_sha)\(' "$(pf_shell_rs_tests)")" = "2" ] \
  || { bad "[${PF_NO}] 旧共享树:检测没覆盖共享根 / downloads / 安装记录,或检查顺手改权限,或自愈不核归档权限与 sha(回归测试缺)"; S109_BAD=1; }
# ⑥ 前端:notifyOnly 判空退化 + 「打开发布页」形态
grep -q 'payload.notifyOnly === true' "${S109_NOTIFIER}" || { bad "[${PF_NO}] 前端 notifyOnly 未判空退化(老壳不安全)"; S109_BAD=1; }
grep -q '打开发布页' "${S109_NOTIFIER}" || { bad "[${PF_NO}] 前端缺发布页出口"; S109_BAD=1; }
# ⑦ 开关(只允许「跳过 asset 取回」,不提供「恢复无 sha 安装」的回魂路)+ 回归测试
grep -q 'HOROSA_UPDATE_API_MANIFEST_FETCH' "${S109_MAIN}" || { bad "[${PF_NO}] 缺 asset 取回开关"; S109_BAD=1; }
for t in api_fallback_fetches_manifest_asset_and_keeps_sha api_fallback_manifest_asset_missing_yields_none api_fallback_manifest_asset_bad_json_yields_none api_manifest_fetch_killswitch_forces_notify_only_path plan_from_manifest_without_sha_leaves_none_for_guard; do
  grep -q "fn ${t}" "$(pf_shell_rs_tests)" || { bad "[${PF_NO}] 缺回归测试 ${t}"; S109_BAD=1; }
done
[ "${S109_BAD}" = "0" ] && ok "[${PF_NO}] API 回退源 sha 闭环在位(asset 取回/守门无条件×${S109_GUARD}/notify-only 不触网/前端退化/测试×5)"
}

seg_114() {
# 签名产物防误发():ad-hoc 构建落 UNSIGNED-DEV-BUILD.txt 标记+警告;
#      publish 上传前 stapler validate 硬门(逃生 HOROSA_ALLOW_UNSTAPLED=1 仅测试 release)。
#      堵「本地未签名误建版被 publish 流入公开 release、他机 Gatekeeper 拦装」这条路。
echo "[${PF_NO}] 签名产物防误发(build 标记 + publish 装订门)"
S114_BAD=0
S114_BUILD="${INSTALLER_ROOT}/scripts/build_desktop_release.sh"
S114_PUB="${INSTALLER_ROOT}/scripts/publish_github_release.sh"
grep -q 'UNSIGNED-DEV-BUILD.txt' "${S114_BUILD}" || { bad "[${PF_NO}] build 缺 ad-hoc 标记文件落点"; S114_BAD=1; }
grep -q 'ad-hoc 构建(未签名/未公证)' "${S114_BUILD}" || { bad "[${PF_NO}] build 缺 ad-hoc 显眼警告"; S114_BAD=1; }
awk '/UNSIGNED-DEV-BUILD.txt/{n++} END{exit !(n>=2)}' "${S114_BUILD}" || { bad "[${PF_NO}] build 标记须双臂(降档写入+签名档清除)"; S114_BAD=1; }
grep -q 'xcrun stapler validate "${DIST_ROOT}/${DESKTOP_OFFLINE_PKG}"' "${S114_PUB}" || { bad "[${PF_NO}] publish 缺 stapler validate 硬门(须验 offline pkg 本体)"; S114_BAD=1; }
grep -q 'HOROSA_ALLOW_UNSTAPLED' "${S114_PUB}" || { bad "[${PF_NO}] publish 装订门缺逃生阀(内网测试 release 需要)"; S114_BAD=1; }
grep -q 'UNSIGNED-DEV-BUILD.txt' "${S114_PUB}" || { bad "[${PF_NO}] publish 未检查 ad-hoc 标记文件"; S114_BAD=1; }
# 顺序锚:装订门必须先于上传(资产一旦上传,门就形同虚设)
S114_GATE_LN="$(grep -n 'xcrun stapler validate "${DIST_ROOT}' "${S114_PUB}" | head -1 | cut -d: -f1 || true)"
S114_UP_LN="$(grep -n '^upload_asset()' "${S114_PUB}" | head -1 | cut -d: -f1 || true)"
{ [ -n "${S114_GATE_LN}" ] && [ -n "${S114_UP_LN}" ] && [ "${S114_GATE_LN}" -lt "${S114_UP_LN}" ]; } || { bad "[${PF_NO}] 装订门(${S114_GATE_LN:-?})未先于上传函数(${S114_UP_LN:-?})"; S114_BAD=1; }
[ "${S114_BAD}" = "0" ] && ok "[${PF_NO}] 签名产物防误发在位(标记双臂/装订门/逃生阀/门先于上传)"
}

seg_182() {
echo "[182] 部件包可复现(内容不变 ⇒ sha 不变;否则增量复用恒 0)"
# 🔴 2026-08-01 实测抓出:增量更新的复用判据是「本地 lock 的部件 sha == 新 manifest 的部件 sha」
# (plan_component_diff)。打包若不可复现,内容一字未改的稳定部件也会 sha 漂移 → 判为「变了」
# → 每版每个用户全量重下,I4 不变量(稳定部件不得变)恒不成立。
# 实锤:上一版已装的 ephe-data 与本版新包逐文件内容完全一致(158 档同摘要),包 sha 却不同;
# 七部件无一复用,reusePct=0、downloadBytes=690MB。
# 两个与内容无关的漂移源:① gzip 头 MTIME=打包时刻;② 目录条目 mtime 被 staging 拷贝刷新。
S182_BAD=0
S182_PK="${INSTALLER_ROOT}/scripts/package_runtime_payload.sh"
# ① 实现在位:gzip -n(归零头时间戳)+ 目录 mtime 归一
grep -aq "'/usr/bin/gzip', '-n'" "${S182_PK}" 2>/dev/null \
  || { S182_BAD=1; bad "[182] 部件打包未走 gzip -n —— gzip 头会写入打包时刻,sha 每版必漂,增量复用恒 0"; }
grep -aq "def normalize_dir_mtimes" "${S182_PK}" 2>/dev/null \
  && grep -aq "normalize_dir_mtimes(stage)" "${S182_PK}" 2>/dev/null \
  || { S182_BAD=1; bad "[182] 部件打包前未归一目录 mtime —— staging 拷贝会刷新目录时间戳,sha 照样漂"; }
# ② 反向锚:旧写法(-czf 一步压)不得回潮
grep -aqE "'-czf', str\(out\)" "${S182_PK}" 2>/dev/null \
  && { S182_BAD=1; bad "[182] 部件打包又出现 -czf 一步压 —— 那正是把打包时刻写进 gzip 头的写法"; }
# ③ 终判据:直接扫**真产物**的 gzip 头 MTIME 字段,必须为 0(不信源码,只认产物)
S182_CD="${INSTALLER_ROOT}/dist/components"
if [ -d "${S182_CD}" ]; then
  S182_N=0
  for S182_F in "${S182_CD}"/horosa-comp-*.tar.gz; do
    [ -f "${S182_F}" ] || continue
    S182_N=$((S182_N+1))
    S182_MT="$(python3 -c "
import struct,sys
h=open(sys.argv[1],'rb').read(10)
print(struct.unpack('<I', h[4:8])[0] if len(h)>=8 else -1)
" "${S182_F}" 2>/dev/null || echo -1)"
    [ "${S182_MT}" = "0" ] || { S182_BAD=1; bad "[182] $(basename "${S182_F}") 的 gzip 头 MTIME=${S182_MT}(应为 0)—— 该包 sha 与内容无关地每版漂移"; }
  done
  [ "${S182_N}" -ge 7 ] || { S182_BAD=1; bad "[182] dist/components 只有 ${S182_N} 个部件包(应 ≥7)—— 判据没扫到东西,拒绝虚绿"; }
fi
[ "${S182_BAD}" = "0" ] && ok "[182] 部件包可复现(gzip -n + 目录 mtime 归一在位·旧写法未回潮·产物 gzip 头 MTIME 全 0)"
}

seg_193() {
# ── [193] 增量部件可复现性三资产(pyc/文件 mtime 归一 + CDS 豁免 + 签名缓存) ──
# 增量更新的复用判据是「本地部件 sha == 新 manifest 部件 sha」。打包一旦不可复现,内容
# 一字未改的部件也被判「变了」⇒ 每版每个用户全量重下(实测曾复用率仅 14%、白耗 167MB)。
# 三条修复缺一即回退到「白下载」,故逐条钉死;另钉可执行护栏脚本在位。
echo "== [193] 增量部件可复现性三资产 =="
S193_BAD=0
S193_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S193_SIGN="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/sign_payload_cached.py"
S193_VERIFY="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_component_reproducibility.sh"
S193_TEST="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/test_sign_payload_cached.py"
# 修一:文件 mtime 归一(且 .py 必须豁免——动它会让全量 pyc 失效、用户首启重编译)
grep -aq "def normalize_file_mtimes" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修一缺失:文件 mtime 归一函数不在(xuanshi/jdk 将每版重下)"; S193_BAD=1; }
grep -aqE "if fn\.endswith\('\.py'\):" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修一危险:.py 豁免不在——归一 .py 的 mtime 会让全量 pyc 失效"; S193_BAD=1; }
grep -aq "normalize_file_mtimes(stage)" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修一未接线:归一函数定义了但没调用"; S193_BAD=1; }
# 修二:base CDS archive 豁免出增量部件
grep -aq "JDK_CDS_REL = 'runtime/mac/java/lib/server/classes.jsa'" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修二缺失:classes.jsa 豁免锚不在"; S193_BAD=1; }
grep -aq "HOROSA_CDS_IN_COMPONENTS" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修二 kill-switch 缺失"; S193_BAD=1; }
# 修三:签名产物缓存(且缓存键必须排除 .jsa——它每次 dump 都不同,纳入键则缓存永不命中)
[ -f "${S193_SIGN}" ] || { bad "[193] 🔴 修三缺失:签名缓存层脚本不在"; S193_BAD=1; }
grep -aq "horosa_repro_sign_cache_v1" "${S193_SIGN}" 2>/dev/null || { bad "[193] 🔴 修三资产标记缺失"; S193_BAD=1; }
grep -aq 'KEY_EXCLUDE_SUFFIXES = (".jsa",)' "${S193_SIGN}" 2>/dev/null || { bad "[193] 🔴 修三键污染防线缺失:.jsa 未排出缓存键(实测踩过——键每次都变、缓存永不命中)"; S193_BAD=1; }
grep -aq "HOROSA_SIGN_CACHE" "${S193_SIGN}" 2>/dev/null || { bad "[193] 🔴 修三 kill-switch 缺失"; S193_BAD=1; }
grep -aq "sign_payload_cached.py" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修三未接线:打包脚本仍直呼原签名脚本(缓存不生效)"; S193_BAD=1; }
# 修四:单文件原生库签名按内容缓存(jar 内成员每版重签的时间戳漂移 ⇒ java-lib 298.7 MB 每版必变)
S193_SIGNER="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/sign_runtime_payload.py"
S193_NTEST="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/test_sign_runtime_payload_native_cache.py"
grep -aq "def sign_file_cached" "${S193_SIGNER}" 2>/dev/null || { bad "[193] 🔴 修四缺失:签名器没有单文件按内容缓存(sign_file_cached)"; S193_BAD=1; }
grep -aq "outcome = sign_file_cached(macho" "${S193_SIGNER}" 2>/dev/null || { bad "[193] 🔴 修四未接线:jar 内 Mach-O 成员仍直呼 sign_path"; S193_BAD=1; }
grep -aq "HOROSA_NATIVE_SIGN_CACHE" "${S193_PKG}" 2>/dev/null || { bad "[193] 🔴 修四未接线:打包脚本没给签名器传缓存目录(HOROSA_NATIVE_SIGN_CACHE)"; S193_BAD=1; }
[ -f "${S193_NTEST}" ] && python3 "${S193_NTEST}" >/dev/null 2>&1 || { bad "[193] 🔴 修四判别向量缺失或失败(test_sign_runtime_payload_native_cache.py)"; S193_BAD=1; }
# 护栏与金标在位
[ -x "${S193_VERIFY}" ] || { bad "[193] 🔴 可复现性护栏脚本缺失或不可执行"; S193_BAD=1; }
[ -f "${S193_TEST}" ] || { bad "[193] 🔴 签名缓存金标缺失"; S193_BAD=1; }
[ "${S193_BAD}" = "0" ] && ok "[193] 增量可复现四资产(mtime 归一+.py 豁免+CDS 豁免+签名缓存+键防污+原生库按内容缓存+护栏+金标)全在位"
}

seg_279() {
# ── seg_279 发布链顺序不变量:部件复用基线在建 release **之前**取 / 清单最后上传 / 新 release 以 draft 建、资产齐了才转正 ──
# 病症(v3.11.0 发布实测,从 v3.1.0 起就有):①脚本先建新 release(立刻成为 latest)再去 releases/latest 取「上一版」清单当基线
#   → 取到刚建好、还没有清单的新 release → 基线恒空 → 部件全量重传、差分效率门(I4)形同虚设;②资产顺序「安装包 → 桌面包 →
#   清单 → runtime → 部件」:清单一上线在线用户就拿到新版本号,去下 runtime / 部件却 404,当次更新失败(实测窗口 ≈80 s)。
# 现在:基线由 pick_release_baseline.py 经认证 API 挑「非本次 tag 的最新已发布版」;顺序不变量由同一文件 --lint 静态看守(判别向量在 --self-test)。
echo "[${PF_NO}] 发布链:基线先于建 release / 清单最后上传 / draft 转正"
S279_BAD=0
S279_PK="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/pick_release_baseline.py"
S279_PUB="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh"
if [ ! -f "${S279_PK}" ]; then
  bad "[${PF_NO}] 🔴 缺 pick_release_baseline.py(基线挑选 / 顺序自检单源件)"; S279_BAD=1
else
  python3 "${S279_PK}" --self-test >/dev/null 2>&1 || { bad "[${PF_NO}] 🔴 基线挑选 / 顺序不变量的判别向量失败"; S279_BAD=1; }
  S279_OUT="$(python3 "${S279_PK}" --lint "${S279_PUB}" 2>&1 || true)"
  case "${S279_OUT}" in
    *"LINT: OK"*) : ;;
    *) bad "[${PF_NO}] 🔴 发布脚本顺序不变量不成立:$(printf '%s' "${S279_OUT}" | grep -a 'LINT:' | grep -av 'LINT: OK' | head -3 | tr '\n' ' ')"; S279_BAD=1 ;;
  esac
fi
grep -qF 'HOROSA_ALLOW_NO_BASELINE' "${S279_PUB}" || { bad "[${PF_NO}] 🔴 基线取回失败的显式放行阀缺失(失败应拦、放行须显式)"; S279_BAD=1; }
grep -qF 'find_release_json_by_tag "${tag_name}"' "${S279_PUB}" || { bad "[${PF_NO}] 🔴 ensure_release 不再按 tag 找回上次中途留下的 draft(会重复建 release)"; S279_BAD=1; }
[ "${S279_BAD}" = "0" ] && ok "[${PF_NO}] 发布链顺序不变量 + 基线判别向量 全在位"
}

seg_280() {
# ── seg_280 安装器:同版本号 runtime 再比一层内容身份(components-lock sha)──
# 病症:postinstall 遇到已装 runtime 只比 runtime-manifest.json 的 version 串;同版本号重打的包一个字节也装不进去,
#   安装日志只有一句 keeping current runtime。现在同版本号再比内容身份,不同就按「版本不同」同一条路径替换;降级门原样不动。
#   四格 + 咬合判别向量:verify_postinstall_version_matrix.sh <offline.pkg>(真解压,发版轮跑一次)。
echo "[${PF_NO}] 安装器:同版本号 runtime 再比内容身份"
S280_BAD=0
S280_TPL="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template"
grep -qF 'runtime_content_identity() {' "${S280_TPL}" || { bad "[${PF_NO}] 🔴 模板缺 runtime_content_identity(同版本重打的包又会装不进去)"; S280_BAD=1; }
grep -qF 'PAYLOAD_IDENTITY="$(runtime_content_identity "${WORK_DIR}/runtime-payload")"' "${S280_TPL}" || { bad "[${PF_NO}] 🔴 同版本分支不再取包内内容身份"; S280_BAD=1; }
grep -qF '[ "${EXISTING_IDENTITY}" = "${PAYLOAD_IDENTITY}" ]' "${S280_TPL}" || { bad "[${PF_NO}] 🔴 同版本分支的内容比对被改掉"; S280_BAD=1; }
grep -qF 'different content' "${S280_TPL}" || { bad "[${PF_NO}] 🔴 「同版本不同内容」的替换日志缺失(真机排障靠它)"; S280_BAD=1; }
grep -qF 'downgrade guard' "${S280_TPL}" || { bad "[${PF_NO}] 🔴 降级门丢失"; S280_BAD=1; }
[ -f "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_postinstall_version_matrix.sh" ] || { bad "[${PF_NO}] 🔴 缺四格判别向量测试台 verify_postinstall_version_matrix.sh"; S280_BAD=1; }
/bin/bash -n "${S280_TPL}" 2>/dev/null || { bad "[${PF_NO}] 🔴 安装模板语法错"; S280_BAD=1; }
[ "${S280_BAD}" = "0" ] && ok "[${PF_NO}] 安装器同版本内容身份比对 在位"
}

seg_306() {
# ── seg_306 签名缓存加固 + 自动种子 + 稳定部件包内对拍 + sqlite 边车 + 交易日志不分大小写 + persistable 回退 + 温启页签 / 一次性上下文:
#   ① 签名器键输入显式化(codesign 参数模板 + 语义代次)/ 基名入键 / 命中 codesign --verify / 原子写 / 播种入口 + 反锚(参数不散写)
#   ② 域级缓存层:签名器盐 + 层代次 + 放回保留权限位 + manifest v2;反锚(不再掺脚本全文 sha)
#   ③ 打包脚本接线:prepare_sign_seed.py 自动种子(按 tar 头权限解)+ --seed-native-from + verify_stable_parts_headers.py + 边车剥离 + 部件 tar --no-xattrs --no-acls
#   ④ 引擎 immutable=1 只读(与边车剥离必须同时成立)⑤ Java 三处 ⑥ 前端两处 ⑦ 测试在位并通过 ⑧ 语义代次变了没种子只提醒
echo "[${PF_NO}] 签名缓存加固 / 自动种子 / 稳定部件包内对拍 / sqlite 边车 / 交易日志不分大小写 / persistable 回退 / 温启页签与一次性上下文"
S306_BAD=0; S306_SC="${REPO_ROOT}/Horosa_Desktop_Installer/scripts"; S306_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"; S306_SRV="${REPO_ROOT}/Horosa-Web/astrostudysrv"
for S306_KW in 'CODESIGN_ARGS_TEMPLATE = (' 'SIGNER_CACHE_EPOCH = "' 'def signer_cache_salt()' 'def native_cache_key(data: bytes, name: str)' 'def verify_signature(path' 'def write_cache_entry(dst' 'def seed_native_cache(' '"--seed-native-from"' 'cmd = list(CODESIGN_ARGS_TEMPLATE) + ["--sign", identity]'; do
  grep -qF -- "${S306_KW}" "${S306_SC}/sign_runtime_payload.py" 2>/dev/null || { bad "[${PF_NO}]① 签名器缺「${S306_KW}」"; S306_BAD=1; }
done
[ "$(grep -c '"--options",' "${S306_SC}/sign_runtime_payload.py" 2>/dev/null || true)" = "1" ] || { bad "[${PF_NO}]① codesign 参数在模板之外又散写了(模板是唯一来源)"; S306_BAD=1; }
for S306_KW in 'CACHE_LAYER_EPOCH = "' 'def signer_salt(signer_mod, signer_path' 'def _put_signed(src' 'horosa_repro_sign_cache_v2' 'signer_salt(signer_mod, signer)'; do
  grep -qF -- "${S306_KW}" "${S306_SC}/sign_payload_cached.py" 2>/dev/null || { bad "[${PF_NO}]② 域级缓存层缺「${S306_KW}」"; S306_BAD=1; }
done
grep -qF 'cache_key(keyed, identity, [signer, __file__])' "${S306_SC}/sign_payload_cached.py" 2>/dev/null && { bad "[${PF_NO}]② 域级缓存键仍掺脚本全文 sha(回潮)"; S306_BAD=1; }
for S306_KW in 'prepare_sign_seed.py' '--seed-native-from' 'verify_stable_parts_headers.py' 'sqlite-shm'; do
  grep -qF -- "${S306_KW}" "${S306_SC}/package_runtime_payload.sh" 2>/dev/null || { bad "[${PF_NO}]③ 打包脚本未接「${S306_KW}」"; S306_BAD=1; }
done
grep -qF -- "'/usr/bin/tar', '--disable-copyfile', '--no-xattrs', '--no-acls', '-cf', '-'" "${S306_SC}/package_runtime_payload.sh" 2>/dev/null || { bad "[${PF_NO}]③ 部件 tar 未带 --no-xattrs --no-acls(扩展属性随打包进程环境来去,写进头 = 稳定部件 sha 漂)"; S306_BAD=1; }
grep -qF 'filter="fully_trusted"' "${S306_SC}/prepare_sign_seed.py" 2>/dev/null || { bad "[${PF_NO}]③ 种子解包未按 tar 头权限(fully_trusted)"; S306_BAD=1; }
grep -qF 'def dump_prev_headers(' "${S306_SC}/prepare_sign_seed.py" 2>/dev/null || { bad "[${PF_NO}]③ 种子准备未留档上一版部件头部"; S306_BAD=1; }
grep -qF 'mode=ro&immutable=1' "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/xuanshi/db.py" 2>/dev/null || { bad "[${PF_NO}]④ 天象库未以 immutable=1 只读打开(剥了边车会打不开)"; S306_BAD=1; }
grep -qF 'TransLogRules.normalizeTransCodes(' "${S306_SRV}/boundless/src/main/java/boundless/spring/help/TransLogMongoHelper.java" 2>/dev/null \
  && grep -qF 'shouldSkipTransLog(path)' "${S306_SRV}/boundless/src/main/java/boundless/spring/help/TransLogMongoHelper.java" 2>/dev/null || { bad "[${PF_NO}]⑤ 交易日志排除表仍精确串匹配"; S306_BAD=1; }
grep -qF 'head = SecretRedactor.redactRecord(head, RemovedParams);' "${S306_SRV}/boundless/src/main/java/boundless/spring/help/interceptor/TransData.java" 2>/dev/null || { bad "[${PF_NO}]⑤ 交易日志请求头未经脱敏单源(名字不分大小写 / 下划线 / 连字符)"; S306_BAD=1; }
grep -qF 'ParamHashPersistPolicy.apply(obj, ParamHashCacheHelper::persistable)' "${S306_SRV}/astrostudy/src/main/java/spacex/astrostudy/helper/ParamHashCacheHelper.java" 2>/dev/null || { bad "[${PF_NO}]⑤ persistable 无回退开关"; S306_BAD=1; }
grep -qF "url.searchParams.delete('firstLaunch');" "${S306_UI}/utils/backendBootGate.js" 2>/dev/null || { bad "[${PF_NO}]⑥ 首启一次性上下文未从地址栏摘除"; S306_BAD=1; }
grep -qF '}, [currentTab, currentSubTab]);' "${S306_UI}/pages/index.js" 2>/dev/null || { bad "[${PF_NO}]⑥ 切页签不重落温启快照"; S306_BAD=1; }
for S306_T in test_sign_payload_cached.py test_sign_runtime_payload_native_cache.py test_prepare_sign_seed.py; do
  /usr/bin/python3 "${S306_SC}/${S306_T}" >/dev/null 2>&1 || { bad "[${PF_NO}]⑦ ${S306_T} 失败"; S306_BAD=1; }
done
/usr/bin/python3 "${S306_SC}/verify_stable_parts_headers.py" --self-test >/dev/null 2>&1 || { bad "[${PF_NO}]⑦ verify_stable_parts_headers 自证失败"; S306_BAD=1; }
[ -f "${REPO_ROOT}/Horosa-Web/astropy/tests/test_xuanshi_db_immutable_readonly.py" ] || { bad "[${PF_NO}]⑦ 缺 sqlite immutable 只读测试"; S306_BAD=1; }
[ -f "${S306_SRV}/boundless/src/test/java/boundless/spring/help/TransLogRulesTest.java" ] && [ -f "${S306_SRV}/astrostudy/src/test/java/spacex/astrostudy/helper/ParamHashPersistPolicyTest.java" ] || { bad "[${PF_NO}]⑦ 缺 JUnit(TransLogRulesTest / ParamHashPersistPolicyTest)"; S306_BAD=1; }
grep -qF '上下文读完即从地址栏摘掉 firstLaunch / boot' "${S306_UI}/utils/__tests__/backendBootGate.test.js" 2>/dev/null && grep -qF '温启快照的页签 = 上次停留' "${S306_UI}/utils/__tests__/bootChartRestore.test.js" 2>/dev/null || { bad "[${PF_NO}]⑦ 缺 jest(一次性上下文 / 切页签快照)"; S306_BAD=1; }
S306_TAG="$(git -C "${REPO_ROOT}" describe --tags --abbrev=0 --match 'v[0-9]*' --exclude '*-runtime*' HEAD 2>/dev/null || true)"
if [ -n "${S306_TAG}" ]; then
  S306_PREV_EPOCH="$(git -C "${REPO_ROOT}" show "${S306_TAG}:Horosa_Desktop_Installer/scripts/sign_runtime_payload.py" 2>/dev/null | sed -n 's/^SIGNER_CACHE_EPOCH = "\(.*\)"/\1/p' | head -1)"
  S306_CUR_EPOCH="$(sed -n 's/^SIGNER_CACHE_EPOCH = "\(.*\)"/\1/p' "${S306_SC}/sign_runtime_payload.py" | head -1)"
  if [ "${S306_PREV_EPOCH}" != "${S306_CUR_EPOCH}" ] && ! ls "${REPO_ROOT}/Horosa_Desktop_Installer/dist/components"/horosa-comp-py-runtime-*.tar.gz >/dev/null 2>&1 && [ -z "${HOROSA_SIGN_SEED_DIR:-}" ]; then
    warn "[${PF_NO}]⑧ 签名语义代次 ${S306_PREV_EPOCH:-无} → ${S306_CUR_EPOCH}(与 ${S306_TAG} 不同)且 dist/components 无上一版 py-runtime 部件可作种子:打包前放回上一版部件或显式设 HOROSA_SIGN_SEED_DIR,否则 py-runtime 整版重签重下"
  fi
fi
[ "${S306_BAD}" = "0" ] && ok "[${PF_NO}] 签名缓存加固 / 自动种子 / 稳定部件包内对拍 / sqlite 边车 / 交易日志不分大小写 / persistable 回退 / 温启页签与一次性上下文:代码 + 接线 + 测试全在位"
}

seg_308() {
echo "[${PF_NO}] 首启原生库预检 + 硬链接暂存槽 + 换完即预检 + 排盘服务分级门(装包 / 更新后第一次打开不再等十几秒)"
S308_BAD=0
S308_RS="$(pf_shell_rs_prod)"
S308_PI="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template"
S308_CFG="${REPO_ROOT}/Horosa_Desktop_Installer/config/native_prewarm_priority.json"
S308_PY="${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"
# ① 壳:子命令 + 就绪后补做 + 只做文件级校验(块内不许出现可执行映射 / 动态加载)
for S308_K in '"--horosa-native-prewarm"' 'fn run_native_prewarm_cli' 'fn spawn_native_prewarm_after_ready' 'NATIVE_PREWARM_F_CHECK_LV' 'NATIVE_PREWARM_F_ADDFILESIGS_RETURN' 'fn stage_dir_by_hardlink' 'fn stage_runtime_copy' 'stage_runtime_copy(&current, &stage, &say)?;' 'fn native_prewarm_after_runtime_update' '"update-incremental"' '"update-full"' '"first-install"' '"runtime-swap"'; do
  grep -aqF -- "${S308_K}" "${S308_RS}" 2>/dev/null || { bad "[${PF_NO}] 🔴 壳缺 ${S308_K}"; S308_BAD=1; }
done
for S308_K in 'fn native_prewarm_block_never_maps_or_loads_code' 'fn component_apply_keeps_inodes_of_untouched_files_and_isolates_root_files' 'fn stage_dir_by_hardlink_shares_inodes_but_copies_root_files'; do
  grep -aqF -- "${S308_K}" "$(pf_shell_rs_tests)" 2>/dev/null || { bad "[${PF_NO}] 🔴 壳缺用例 ${S308_K}"; S308_BAD=1; }
done
S308_BLK="$(awk '/\[首启原生库预检\] 装包 \/ 更新后第一次打开/{f=1} f{print} /\[首启原生库预检\] 块尾/{if(f){exit}}' "${S308_RS}" 2>/dev/null)"
[ -n "${S308_BLK}" ] || { bad "[${PF_NO}] 🔴 壳里找不到预检块(首尾标记)"; S308_BAD=1; }
for S308_K in 'mmap(' 'dlopen(' 'libloading' 'Command::new'; do
  printf '%s' "${S308_BLK}" | pipe_has -F -- "${S308_K}" && { bad "[${PF_NO}] 🔴 预检块里出现了 ${S308_K}(只许文件级校验调用)"; S308_BAD=1; }
done
# ①b 暂存槽用硬链接搭:外部 tar 回退必须先删条目再建(就地覆盖写会伤到与旧树共用 inode 的文件);树根两处改写先删条目
grep -aqF -- '.arg("-U")' "${S308_RS}" 2>/dev/null || { bad "[${PF_NO}] 🔴 外部 tar 回退缺 -U(硬链接槽里就地覆盖写会伤到正在跑的旧树)"; S308_BAD=1; }
grep -aqF -- 'let _ = fs::remove_file(stage.join("components-lock.json"));' "${S308_RS}" 2>/dev/null || { bad "[${PF_NO}] 🔴 手术改写部件锁前没先删条目"; S308_BAD=1; }
# ② 安装脚本:装完后台跑,且只在二进制认识该子命令时才调
grep -aqF -- '--horosa-native-prewarm "${CURRENT_DIR}"' "${S308_PI}" 2>/dev/null || { bad "[${PF_NO}] 🔴 postinstall 没接首启原生库预检"; S308_BAD=1; }
grep -aqF -- "grep -q -- '--horosa-native-prewarm' \"\${APP_BIN}\"" "${S308_PI}" 2>/dev/null || { bad "[${PF_NO}] 🔴 postinstall 预检缺「二进制认识该子命令」守卫(旧二进制会拉起界面)"; S308_BAD=1; }
# ③ 顺序表:合法 JSON,启动档数 ≤ 档数,配对哨兵在
python3 - "${S308_CFG}" <<'PY' 2>/dev/null || { bad "[${PF_NO}] 🔴 native_prewarm_priority.json 缺失 / 不合法 / 启动档数越界"; S308_BAD=1; }
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
t = d['tiers']; s = d['startupTiers']
assert isinstance(t, list) and len(t) >= 4 and 1 <= s <= len(t)
assert all(tier and all(isinstance(x, str) and x for x in tier) for tier in t)
PY
[ -f "${REPO_ROOT}/Horosa-Web/astropy/tests/test_native_prewarm_priority.py" ] || { bad "[${PF_NO}] 🔴 缺顺序表覆盖哨兵 test_native_prewarm_priority.py"; S308_BAD=1; }
# ④ 排盘服务分级门:核心门 / 卜类挂载点判定 / 总开关 / 宽限 / 金标
for S308_K in 'CORE_GATE = threading.Event()' 'def _request_targets_kentang' 'HOROSA_PY_TIERED_GATE' 'HOROSA_PY_CORE_GATE_GRACE_MS' 'py.gate_core_open'; do
  grep -aqF -- "${S308_K}" "${S308_PY}" 2>/dev/null || { bad "[${PF_NO}] 🔴 排盘服务缺 ${S308_K}"; S308_BAD=1; }
done
[ -f "${REPO_ROOT}/Horosa-Web/astropy/tests/test_startup_gate_tiers.py" ] || { bad "[${PF_NO}] 🔴 缺分级门金标 test_startup_gate_tiers.py"; S308_BAD=1; }
[ "${S308_BAD}" = "0" ] && ok "[${PF_NO}] 首启原生库预检(壳子命令 + 安装脚本后台跑 + 就绪后补做 + 顺序表哨兵)+ 硬链接暂存槽 / 换完即预检 / 外部 tar 先删后建 + 分级门金标全在位"
}

seg_309() {
echo "[${PF_NO}] 打包链单飞锁(release_lock.sh:内核文件锁随进程走 + 嵌套放行 + 不挂 EXIT trap)+ 签名产物权限位单一来源(prev_parts_modes:两层缓存同口径)"
S309_BAD=0; S309_SC="${REPO_ROOT}/Horosa_Desktop_Installer/scripts"
for S309_KW in 'horosa_release_lock()' 'horosa_release_lock_release()' 'fcntl.LOCK_EX | fcntl.LOCK_NB' 'os.kill(owner, 0)' 'return 75' 'HOROSA_RELEASE_LOCK_OWNER'; do
  grep -qF -- "${S309_KW}" "${S309_SC}/release_lock.sh" 2>/dev/null || { bad "[${PF_NO}]① 单飞锁缺「${S309_KW}」"; S309_BAD=1; }
done
# 锁随进程走(内核 flock + 守锁进程),绝不挂 EXIT trap:bash 3.2 下 set -euo pipefail 的脚本挂了 EXIT trap,未绑定变量的错误退出码会被吞成 0
for S309_F in release_lock.sh build_desktop_release.sh package_runtime_payload.sh; do
  [ "$(grep -cE -- '^[[:space:]]*trap .*EXIT' "${S309_SC}/${S309_F}" 2>/dev/null || true)" = "0" ] || { bad "[${PF_NO}]① ${S309_F} 挂了 EXIT trap(打包脚本出错会被报成功)"; S309_BAD=1; }
done
for S309_F in build_desktop_release.sh package_runtime_payload.sh; do
  grep -qF '. "${INSTALLER_ROOT}/scripts/release_lock.sh"' "${S309_SC}/${S309_F}" 2>/dev/null && grep -qF 'horosa_release_lock "' "${S309_SC}/${S309_F}" 2>/dev/null || { bad "[${PF_NO}]① ${S309_F} 未接单飞锁"; S309_BAD=1; }
  S309_LN="$(grep -n 'horosa_release_lock "' "${S309_SC}/${S309_F}" 2>/dev/null | head -n 1 | cut -d: -f1)"
  [ -n "${S309_LN}" ] && [ "${S309_LN}" -le 40 ] || { bad "[${PF_NO}]① ${S309_F} 取锁不在脚本开头(第 ${S309_LN:-?} 行;须先于任何构建步骤)"; S309_BAD=1; }
done
bash "${S309_SC}/test_release_lock.sh" >/dev/null 2>&1 || { bad "[${PF_NO}]② 单飞锁自证失败(并发拒 / 嵌套放行 / kill -9 后放开 / 退出放开 / 不吞退出码 / 十条同跑不重叠)"; S309_BAD=1; }
for S309_KW in 'def decide_mode(' 'def tar_name_of(' 'def apply_mode(' 'RECORD_ENV = "HOROSA_PREV_PARTS_HEADERS"' 'SWITCH_ENV = "HOROSA_PREV_PARTS_MODES"'; do
  grep -qF -- "${S309_KW}" "${S309_SC}/prev_parts_modes.py" 2>/dev/null || { bad "[${PF_NO}]③ 权限位单一来源缺「${S309_KW}」"; S309_BAD=1; }
done
grep -qF 'prev_parts_modes.apply_mode(dst, mode)' "${S309_SC}/sign_payload_cached.py" 2>/dev/null || { bad "[${PF_NO}]③ 域级缓存放回未走权限位单一来源"; S309_BAD=1; }
grep -qF 'prev_parts_modes.apply_mode(archive_path, staged_mode)' "${S309_SC}/sign_runtime_payload.py" 2>/dev/null || { bad "[${PF_NO}]③ jar 重建未走权限位单一来源(会落临时档的 0600)"; S309_BAD=1; }
grep -qF 'export HOROSA_PREV_PARTS_HEADERS=' "${S309_SC}/package_runtime_payload.sh" 2>/dev/null || { bad "[${PF_NO}]③ 打包脚本未导出上一版部件头部留档路径"; S309_BAD=1; }
/usr/bin/python3 "${S309_SC}/test_prev_parts_modes.py" >/dev/null 2>&1 || { bad "[${PF_NO}]④ 权限位单一来源自证失败(两层缓存口径 / 开关 / 留档缺失回退)"; S309_BAD=1; }
[ "${S309_BAD}" = "0" ] && ok "[${PF_NO}] 打包链单飞锁(内核文件锁 + 嵌套 + kill -9 / 退出即放 + 不吞退出码 + 并发不重叠,自证 6/6)+ 签名产物权限位单一来源(留档优先 / 暂存位回退 / 两层同口径,自证 ①–⑤)"
}

seg_323() {
echo "[${PF_NO}] 后端构建命令一律走聚合 pom(脚本 / 文档 / Eclipse 工程里的模块名 ⊆ <modules>、禁逐模块 install、-pl 必带 -am、一键部署两处构建函数干跑)"
S323_BAD=0; S323_PY="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/check_backend_build_commands.py"
# 后端是聚合 pom 管着的多模块工程:逐个模块进目录各装一遍,在新机器上缺父 pom 必失败、在旧机器上吃 ~/.m2 旧件;
#   脚本里手抄的模块清单在下架模块后会让源码一键部署整条中止。检查器自带判别力自证(坏样本必须报出来)。
if [ ! -f "${S323_PY}" ]; then
  bad "[${PF_NO}] 缺 check_backend_build_commands.py"; S323_BAD=1
else
  S323_OUT="$(python3 "${S323_PY}" --self-test 2>&1)" || { printf '%s\n' "${S323_OUT}" | tail -5 | sed 's/^/      /' >&2; bad "[${PF_NO}] 构建命令检查器自证失败(判别力丢了)"; S323_BAD=1; }
  S323_OUT="$(python3 "${S323_PY}" 2>&1)" || { printf '%s\n' "${S323_OUT}" | head -40 | sed 's/^/      /' >&2; bad "[${PF_NO}] 有构建命令没走聚合 pom / 写了聚合 pom 里没有的模块(见上;改成 mvn -f Horosa-Web/astrostudysrv/pom.xml …,只跑某几个模块用 -pl 模块 -am)"; S323_BAD=1; }
fi
[ "${S323_BAD}" = "0" ] && ok "[${PF_NO}] 后端构建命令全走聚合 pom($(printf '%s' "${S323_OUT}" | tail -n 1))"
}

seg_3() {
# 3. UPGRADE_LOG 有本版条目
echo "[3] UPGRADE_LOG 条目"
grep -qF "${VERSION}" "${REPO_ROOT}/UPGRADE_LOG.md" && ok "UPGRADE_LOG 提及 ${VERSION}" || bad "UPGRADE_LOG.md 没有 ${VERSION} 条目"
}

seg_1() {
# 1. 版本号 lockstep:所有该带版本号的文件都必须含当前 VERSION
echo "[1] 版本号一致性"
grep -q "\"version\": \"${VERSION}\"" "${INSTALLER_ROOT}/package.json"            && ok "package.json"        || bad "package.json version != ${VERSION}"
grep -q "^version = \"${VERSION}\"" "${INSTALLER_ROOT}/src-tauri/Cargo.toml"       && ok "Cargo.toml"          || bad "Cargo.toml version != ${VERSION}"
grep -q "\"version\": \"${VERSION}\"" "${INSTALLER_ROOT}/src-tauri/tauri.conf.json" && ok "tauri.conf.json"     || bad "tauri.conf.json version != ${VERSION}"
# CITATION.cff 须对版本（缺席即跳过，不误报）。
if [ -f "${REPO_ROOT}/CITATION.cff" ]; then
  grep -q "version: \"${VERSION}\"" "${REPO_ROOT}/CITATION.cff"                     && ok "CITATION.cff"        || bad "CITATION.cff version != ${VERSION}"
else
  ok "CITATION.cff(本仓无此文件，跳过)"
fi
grep -q "APP_VERSION = '${VERSION}'" "${INSTALLER_ROOT}/web/app.js"                 && ok "web/app.js"          || bad "web/app.js APP_VERSION != ${VERSION}"
# Cargo.lock: 本项目包的版本
if awk '/^name = "horosa-desktop-installer"$/{getline; print}' "${INSTALLER_ROOT}/src-tauri/Cargo.lock" | pipe_has "version = \"${VERSION}\""; then ok "Cargo.lock"; else bad "Cargo.lock horosa-desktop-installer version != ${VERSION}"; fi
# runtimeVersion 必须是 {VERSION}-runtimeN
case "${RUNTIME_VERSION}" in "${VERSION}-runtime"*) ok "release_config runtimeVersion (${RUNTIME_VERSION})";; *) bad "runtimeVersion '${RUNTIME_VERSION}' 不是 ${VERSION}-runtimeN";; esac
# 运行时版本闸字面量单源已迁 basecomm RuntimeWire(各控制器只引用不手抄);须与 runtimeVersion lockstep(改后须按聚合 pom 重编 mvn -f Horosa-Web/astrostudysrv/pom.xml clean install)
S1_RW="${REPO_ROOT}/Horosa-Web/astrostudysrv/basecomm/src/main/java/spacex/basecomm/constants/RuntimeWire.java"
grep -q "RUNTIME_VERSION = \"${RUNTIME_VERSION}\"" "${S1_RW}" 2>/dev/null && ok "RuntimeWire.RUNTIME_VERSION=${RUNTIME_VERSION}" || bad "RuntimeWire.RUNTIME_VERSION != ${RUNTIME_VERSION}(改后须按聚合 pom 重编 mvn -f Horosa-Web/astrostudysrv/pom.xml clean install)"
# verify_launcher_console_states.py 硬编码 launcher 的 "来源 pkg <VERSION>" 断言(launcher 用 APP_VERSION 渲染该行)——
# 每版必须同步,否则 verify_desktop_packaging 在「编译+签名+公证」之后才报 ready-state 失败(v2.1.8 复盘:白白跑完一次签名公证)。
grep -q "来源 pkg ${VERSION}" "${INSTALLER_ROOT}/scripts/verify_launcher_console_states.py" && ok "verify_launcher_console_states.py(launcher 版本断言)" || bad "verify_launcher_console_states.py 仍断言旧版本 —— 改 '来源 pkg ${VERSION}' 及注入 detail 的 '本机组件版本 ${VERSION}'"
# 同文件另有一处 offline_ready 夹具串「本机组件版本 <VERSION>」—— 历版皆随版本改,却一直靠人记得。
# 2026-08-12 v3.9.1 lockstep 时发现它是唯一没被守住的一处,补进本闸。
grep -q "本机组件版本 ${VERSION} 已可直接使用" "${INSTALLER_ROOT}/scripts/verify_launcher_console_states.py" && ok "verify_launcher_console_states.py(offline_ready 夹具版本)" || bad "verify_launcher_console_states.py 的 offline_ready 夹具版本 != ${VERSION}"
}

seg_22() {
# 22. 发布范围完整性（防漏合本地分支）—— **铁律**：判断「发布收敛哪些分支 / 哪些 ready」时,绝不凭记忆或部分列表,
#     必枚举所有本地分支并逐个查领先 main 的提交。v2.5.0 险些漏合 feature/ziwei-depth(紫微运限深化 + 六壬Phase4)→ 差点发出残缺版本。
echo "[22] 发布范围完整性(本地分支全枚举,防漏合)"
# 已并入主线、只是没删的旧分支登记在 superseded_branches.tsv(分支名 + 当时的 tip):tip 未变 = 放行;
# tip 变了(冒出新提交 = 真有新活)= 照常报。
SUPERSEDED_REG="${REPO_ROOT}/Horosa_Desktop_Installer/config/superseded_branches.tsv"
AHEAD_FEAT=""
ACK_FEAT=""
while read -r b; do
  [ -n "$b" ] || continue
  n="$(git -C "${REPO_ROOT}" rev-list --count "main..${b}" 2>/dev/null || true)"
  [ "${n:-0}" -gt 0 ] || continue
  cur="$(git -C "${REPO_ROOT}" rev-parse "${b}" 2>/dev/null || echo '')"
  reg="$(grep -E "^${b}[[:space:]]" "${SUPERSEDED_REG}" 2>/dev/null | head -1 | cut -f2)"
  if [ -n "${reg}" ] && [ "${reg}" = "${cur}" ]; then
    ACK_FEAT="${ACK_FEAT} ${b}"
  else
    AHEAD_FEAT="${AHEAD_FEAT} ${b}(+${n})"
  fi
done < <(git -C "${REPO_ROOT}" for-each-ref --format='%(refname:short)' refs/heads/ | grep -E '^feature/' || true)
if [ -n "${AHEAD_FEAT}" ]; then
  if [ "${HOROSA_KNOWN_UNMERGED:-}" = "1" ]; then
    warn "feature/* 领先 main,但已 HOROSA_KNOWN_UNMERGED=1 确认非本版:${AHEAD_FEAT}"
  else
    bad "feature/* 分支领先 main,可能漏入本版:${AHEAD_FEAT} —— 必逐个确认应否合并(漏 ziwei-depth 教训);未来版本 HOROSA_KNOWN_UNMERGED=1,已并入主线的旧分支登记 superseded_branches.tsv"
  fi
elif [ -n "${ACK_FEAT}" ]; then
  ok "[22] feature/* 无遗漏:${ACK_FEAT# } 已登记 superseded(tip 未变、在 main 里且更新)→ 放行;冒新提交自动复报"
else
  ok "无 feature/* 分支领先 main(本地 feature 分支均已纳入/合并)"
fi
}

seg_44() {
# [44] 远端隔离白名单 (2026-06-10): 本仓所有 git remote URL 只允许指向本仓自身,
#      杜绝接错远端互推;publish 的 runtime 内嵌前端一致性闸也必须在位。
echo "[44] 远端隔离白名单 + runtime 内嵌前端闸"
R44_BAD=0
# 本仓远端白名单(case 模式,逐个比)
R44_ALLOW=('*github.com[:/]Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS*')
while IFS= read -r R44_URL; do
  R44_HIT=0
  for R44_P in "${R44_ALLOW[@]}"; do
    # shellcheck disable=SC2254
    case "${R44_URL}" in ${R44_P}) R44_HIT=1 ;; esac
  done
  [ "${R44_HIT}" = "1" ] || { bad "[44] 远端 URL 不在本仓白名单: ${R44_URL}"; R44_BAD=1; }
done <<EOF44
$(git -C "${REPO_ROOT}" remote -v | awk '{print $2}' | sort -u)
EOF44
grep -q "runtime 包内嵌前端" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh" || { bad "[44] publish 缺 runtime 内嵌前端一致性闸"; R44_BAD=1; }
[ "${R44_BAD}" = "0" ] && ok "[44] 远端全在白名单 + runtime 前端闸在位"
}

seg_43() {
# [43] 更新通道隔离: 本仓 app 身份/更新源四件套必须自洽,且 publish 带产物身份硬闸。
#      防两类事故: ①壳层兜底配置漂移 → 装机用户的自动更新拉错源; ②误把别处构建的产物传进本仓 release。
echo "[43] 更新通道隔离(身份四件套 + publish 硬闸)"
U43_BAD=0
U43_TAURI="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/tauri.conf.json"
U43_RC="${REPO_ROOT}/Horosa_Desktop_Installer/config/release_config.json"
U43_MAIN="$(pf_shell_rs_prod)"
U43_PUBSH="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/publish_github_release.sh"
# 本仓身份期望值(identifier / 产品名 / 更新源仓名 / 共享安装根)
U43_W_ID="com.horacedong.horosa"; U43_W_NAME="星阙"; U43_W_REPO="Horosa-Web-App-comprehensively-improved-MacOS"; U43_W_SRN="Horosa"
U43_ID="$(python3 -c "import json;print(json.load(open('${U43_TAURI}'))['identifier'])" 2>/dev/null)"
U43_PN="$(python3 -c "import json;print(json.load(open('${U43_TAURI}'))['productName'])" 2>/dev/null)"
U43_AN="$(python3 -c "import json;print(json.load(open('${U43_RC}'))['appName'])" 2>/dev/null)"
U43_RN="$(python3 -c "import json;print(json.load(open('${U43_RC}'))['repoName'])" 2>/dev/null)"
[ "${U43_ID}" = "${U43_W_ID}" ] || { bad "[43] tauri identifier=${U43_ID} ≠ ${U43_W_ID}"; U43_BAD=1; }
[ "${U43_PN}" = "${U43_W_NAME}" ] || { bad "[43] tauri productName=${U43_PN} ≠ ${U43_W_NAME}"; U43_BAD=1; }
[ "${U43_AN}" = "${U43_W_NAME}" ] || { bad "[43] release_config appName=${U43_AN} ≠ ${U43_W_NAME}"; U43_BAD=1; }
[ "${U43_RN}" = "${U43_W_REPO}" ] || { bad "[43] release_config repoName=${U43_RN} ≠ ${U43_W_REPO}(更新会拉错源!)"; U43_BAD=1; }
grep -qF "const APP_NAME: &str = \"${U43_W_NAME}\"" "${U43_MAIN}" || { bad "[43] 壳层 APP_NAME 兜底 ≠ ${U43_W_NAME}(会碰另一版的安装位 / 更新路径)"; U43_BAD=1; }
grep -qF "const APP_IDENTIFIER: &str = \"${U43_W_ID}\"" "${U43_MAIN}" || { bad "[43] 壳层 APP_IDENTIFIER 兜底 ≠ ${U43_W_ID}(重置偏好会删到另一版的域)"; U43_BAD=1; }
grep -qF "const DEFAULT_REPO_NAME: &str = \"${U43_W_REPO}\"" "${U43_MAIN}" || { bad "[43] 壳层 DEFAULT_REPO_NAME 兜底漂移(配置缺失时更新会拉错源)"; U43_BAD=1; }
grep -q "更新通道隔离硬闸" "${U43_PUBSH}" || { bad "[43] publish_github_release.sh 缺产物身份硬闸"; U43_BAD=1; }
# 共享目录单源化:安装器与壳层必须同目录;runtime 须带 appName 身份戳并在安装时验明
U43_SRN="$(python3 -c "import json;print(json.load(open('${U43_RC}')).get('sharedRootName',''))" 2>/dev/null)"
[ "${U43_SRN}" = "${U43_W_SRN}" ] || { bad "[43] release_config sharedRootName=${U43_SRN} ≠ ${U43_W_SRN}(安装器会装错目录)"; U43_BAD=1; }
U43_TPL="${REPO_ROOT}/Horosa_Desktop_Installer/installer-scripts/postinstall.template"
grep -q "__SHARED_ROOT_NAME__" "${U43_TPL}" || { bad "[43] postinstall 模板缺 __SHARED_ROOT_NAME__ 占位(回退写死路径)"; U43_BAD=1; }
grep -q 'manifest_app.*APP_NAME' "${U43_TPL}" || { bad "[43] postinstall 缺 runtime 身份验明(别的版本的 runtime 会被误判可用)"; U43_BAD=1; }
grep -q "__SHARED_ROOT_NAME__" "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh" || { bad "[43] build 脚本未渲染 __SHARED_ROOT_NAME__"; U43_BAD=1; }
grep -q '"appName": "\${PAYLOAD_APP_NAME}"' "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh" || { bad "[43] runtime manifest 缺 appName 身份戳"; U43_BAD=1; }
grep -qF "\"/Users/Shared/${U43_W_SRN}/runtime/current\"" "${U43_MAIN}" || { bad "[43] 壳层共享目录字面量 /Users/Shared/${U43_W_SRN}/runtime/current 漂移"; U43_BAD=1; }
# 主限法方位法:前端白名单与 Python 注册表两端一致(不一致 = 下拉能选、后端不认)+ 核心法齐 + 不少于 6 项
U43_PD="$(python3 - "${REPO_ROOT}" <<'PY43'
import re, sys
src = open(sys.argv[1] + '/Horosa-Web/astrostudyui/src/utils/primaryDirectionSync.js', encoding='utf-8').read()
m = re.search(r'SUPPORTED_PD_METHODS\s*=\s*\[(.*?)\]', src, re.S)
methods = sorted(re.findall(r"'([a-z_]+)'", m.group(1))) if m else []
print(','.join(methods))
PY43
)"
U43_REG="$(cd "${REPO_ROOT}/Horosa-Web/astropy" && python3 -c "
import re
src = open('astrostudy/perpredict.py', encoding='utf-8').read()
m = re.search(r'_PD_METHOD_REGISTRY\s*=\s*\{(.*?)\n\}', src, re.S)
keys = sorted(set(re.findall(r\"'([a-z_]+)':\", m.group(1)))) if m else []
print(','.join(keys))" 2>/dev/null)"
if [ -z "${U43_PD}" ] || [ -z "${U43_REG}" ]; then
  bad "[43] 方位法集合取不到(JS='${U43_PD}' Py='${U43_REG}')—— 解析源或常量名变了"; U43_BAD=1
elif [ "${U43_PD}" != "${U43_REG}" ]; then
  bad "[43] 前端白名单与 Python _PD_METHOD_REGISTRY 不一致 —— 会出「能选但后端不认」: JS=${U43_PD} / Py=${U43_REG}"; U43_BAD=1
else
  U43_N="$(printf '%s' "${U43_PD}" | awk -F, '{print NF}')"
  [ "${U43_N}" -ge 6 ] || { bad "[43] 方位法集合只剩 ${U43_N} 项(<6)—— 疑误删: ${U43_PD}"; U43_BAD=1; }
  for _m in core_alchabitius meridian porphyry equal_ecliptic equal_hour_circle; do
    case ",${U43_PD}," in *",${_m},"*) : ;; *) bad "[43] 方位法集合缺核心法 '${_m}'"; U43_BAD=1 ;; esac
  done
fi
[ "${U43_BAD}" = "0" ] && ok "[43] 身份四件套(${U43_W_NAME})+ publish 硬闸 + 共享目录单源 + 方位法白名单(JS + Py 两端一致)在位"
}

seg_156() {
# ── [${PF_NO}] 离线安装链真装门(渲染占位符/内嵌档 gz/净化 PATH 可解/成品 pkg e2e stamp) ──
#   守 2026-07-20 双案:①模板占位符 __OFFLINE_RUNTIME_ASSET__ 渲染表漏键 → postinstall 找不到
#   内嵌档 → 降级 pending;②内嵌 .tar.zst 而 macOS 系统 tar(libarchive 无 zstd 滤器)在
#   PKInstallSandbox 净化 PATH 下无第三方 zstd 兜底 → 解压必败 → 降级;两案 App 首启都读到
#   旧版缓存报「版本不符」。全链自检此前只测「runtime 归档能启动」,从未测「成品 .pkg 的
#   postinstall 在安装沙盒等价环境下真装成功」—— 本哨兵 + build 内联断言 + e2e 门三层补死。
echo "[${PF_NO}] 离线安装链真装门"
S156_BAD=0
S156_BUILD="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/build_desktop_release.sh"
S156_RD="${REPO_ROOT}/Horosa_Desktop_Installer/build/installer-scripts-rendered-offline"
S156_STAMP="${REPO_ROOT}/Horosa_Desktop_Installer/build/offline-pkg-e2e.stamp"
# 离线 pkg 只许内嵌 gz:构建脚本里 zst 内嵌的口子是否已封
S156_GZ_OK=0
{ grep -qF 'OFFLINE_EMBED_ARCHIVE="${RUNTIME_ARCHIVE}"' "${S156_BUILD}" 2>/dev/null && ! grep -q 'HOROSA_OFFLINE_ZSTD' "${S156_BUILD}" 2>/dev/null; } && S156_GZ_OK=1
S156_GZ_MSG="build 离线 pkg 须只内嵌 gz(本壳不认 tar.zst 缓存,不得留内嵌 zst 的口子)"
[ "${S156_GZ_OK}" = "1" ] || { bad "[${PF_NO}] 🔴 ${S156_GZ_MSG}"; S156_BAD=1; }
grep -q 'env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin /usr/bin/tar -tf' "${S156_BUILD}" 2>/dev/null || { bad "[${PF_NO}] 🔴 build 缺净化 PATH 内嵌档探测"; S156_BAD=1; }
{ grep -qF "if grep -nE '__[A-Z_]+__' \"\${OFFLINE_SCRIPTS_RENDERED_DIR}/postinstall\"; then" "${S156_BUILD}" 2>/dev/null \
  && grep -qF '[ ! -s "${OFFLINE_SCRIPTS_RENDERED_DIR}/${RENDERED_ARCHIVE_NAME}" ]' "${S156_BUILD}" 2>/dev/null; } \
  || { bad "[${PF_NO}] 🔴 build 缺渲染后硬断言块(占位符/档在位/可解)"; S156_BAD=1; }
grep -q 'verify_offline_pkg_install_e2e.sh' "${S156_BUILD}" 2>/dev/null || { bad "[${PF_NO}] 🔴 build 未接离线 pkg 真装 e2e 门"; S156_BAD=1; }
[ -x "${REPO_ROOT}/Horosa_Desktop_Installer/scripts/verify_offline_pkg_install_e2e.sh" ] || { bad "[${PF_NO}] 缺 verify_offline_pkg_install_e2e.sh"; S156_BAD=1; }
if [ -f "${S156_RD}/postinstall" ]; then
  grep -qE '__[A-Z_]+__' "${S156_RD}/postinstall" && { bad "[${PF_NO}] 🔴 rendered postinstall 残留未替换占位符"; S156_BAD=1; }
  S156_AN="$(sed -n 's/^ARCHIVE_NAME="\(.*\)"$/\1/p' "${S156_RD}/postinstall" | head -n 1)"
  if [ -z "${S156_AN}" ] || [ ! -s "${S156_RD}/${S156_AN}" ]; then
    bad "[${PF_NO}] 🔴 rendered Scripts 缺内嵌档(${S156_AN:-<空>})"; S156_BAD=1
  elif ! env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin /usr/bin/tar -tf "${S156_RD}/${S156_AN}" >/dev/null 2>&1; then
    bad "[${PF_NO}] 🔴 rendered 内嵌档净化 PATH(≈PKInstallSandbox)不可解——系统 tar 无此压缩滤器"; S156_BAD=1
  fi
fi
S156_PKG_NAME="$(python3 -c "import json;print(json.load(open('${REPO_ROOT}/Horosa_Desktop_Installer/config/release_config.json'))['desktopOfflinePkgName'])" 2>/dev/null || true)"
S156_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/dist/${S156_PKG_NAME}"
if [ -n "${S156_PKG_NAME}" ] && [ -s "${S156_PKG}" ]; then
  if [ ! -f "${S156_STAMP}" ]; then
    bad "[${PF_NO}] 🔴 有离线 pkg 但缺真装 e2e stamp(HOROSA_SKIP_PKG_E2E 跳过未补跑?)"; S156_BAD=1
  else
    S156_SHA="$(shasum -a 256 "${S156_PKG}" | awk '{print $1}')"
    S156_MATCH="$(awk -F'\t' -v sha="${S156_SHA}" '$1=="OK" && $2==sha {print "MATCH"}' "${S156_STAMP}" | head -n 1)"
    [ "${S156_MATCH}" = "MATCH" ] || { bad "[${PF_NO}] 🔴 e2e stamp 非 OK 或与成品 pkg sha 不符——对当前 pkg 补跑 verify_offline_pkg_install_e2e.sh"; S156_BAD=1; }
  fi
fi
[ "${S156_BAD}" = "0" ] && ok "[${PF_NO}] 离线安装链真装门全在位(gz 默认/净化探测/渲染断言/e2e stamp 绑定成品)"
}
