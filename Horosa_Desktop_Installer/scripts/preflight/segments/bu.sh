#!/usr/bin/env bash
# 发布前自检 · 卜与择日
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。段号用 ${PF_NO}(登记表第二列)。

seg_21() {
# 21. 六壬 起课法/换将/分昼夜(纯前端 castOverride 机制,不动 Java)
echo "[21] 六壬 起课法/换将/分昼夜哨兵"
LR_MAIN="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/lrzhan/LiuRengMain.js")"
LR_COMM="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js"
LR_AICTX="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js")"
LR_CONST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRConst.js"
if grep -q "buildLiuRengCastOverride" "${LR_MAIN}" 2>/dev/null && grep -q "function computeQiXY" "${LR_MAIN}" 2>/dev/null; then ok "[21] LiuRengMain 含起课法引擎(buildLiuRengCastOverride/computeQiXY)"; else bad "[21] LiuRengMain 缺起课法引擎"; fi
if grep -q "castOverride" "${LR_COMM}" 2>/dev/null; then ok "[21] LRCommChart 渲染侧读 castOverride(中心盘随起课法,与右栏断辞同源)"; else bad "[21] LRCommChart 未读 castOverride —— 中心盘不随起课法变,会与右栏断辞不一致"; fi
if grep -q "isDiurnalOverride" "${LR_CONST}" 2>/dev/null; then ok "[21] LRConst.getGuiZi 接受昼夜覆盖(分昼夜法)"; else bad "[21] LRConst.getGuiZi 缺昼夜覆盖参 —— 分昼夜法失效"; fi
if grep -q "castMethod: this.state.castMethod" "${LR_MAIN}" 2>/dev/null && grep -q "fenZhouYe: this.state.fenZhouYe" "${LR_MAIN}" 2>/dev/null; then ok "[21] 占案 payload 含起课法/换将/分昼夜(储存可复现)"; else bad "[21] 占案 payload 缺起课法字段 —— 存档不可复现"; fi
if grep -q "yueJiangMethod: payload.yueJiangMethod" "${LR_AICTX}" 2>/dev/null; then ok "[21] AI挂载 事盘重建透传 castOpts(挂载与显示一致)"; else bad "[21] AI挂载 六壬事盘未透传 castOpts —— 八客/选时案例会挂成默认正时正将"; fi
if grep -q "'xuanshi'" "${LR_MAIN}" 2>/dev/null && grep -q "'yanshu'" "${LR_MAIN}" 2>/dev/null && grep -q "'alnr'" "${LR_MAIN}" 2>/dev/null; then ok "[21] 起课法含 选时/演数/四柱对齐"; else bad "[21] 起课法缺 选时/演数/对齐 选项"; fi
# 次客=筹支加时(重排天地盘),勿退回只改三传;月将高亮认真实月将 actualYue;ChuangChart 必无 applyCiChou。
LR_CHUANG="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.js"
if grep -q "function liurengChouBranch" "${LR_MAIN}" 2>/dev/null && grep -q "case 'cike3':" "${LR_MAIN}" 2>/dev/null; then ok "[21] 次客=筹支加时(liurengChouBranch + computeQiXY cike 分支,重排天地盘)"; else bad "[21] 次客缺筹支加时引擎 —— 退回了「只改三传」的错误实现"; fi
if grep -q "actualYue" "${LR_MAIN}" 2>/dev/null; then ok "[21] 月将/盘式高亮认真实月将 actualYue(非起课法天盘起支 X)"; else bad "[21] 缺 actualYue —— 加时/次客法的月将高亮会错显为起课法 X"; fi
if grep -q "applyCiChou" "${LR_CHUANG}" 2>/dev/null; then bad "[21] ChuangChart 残留 applyCiChou —— 次客退回「只改三传」错误实现,必删"; else ok "[21] ChuangChart 无 applyCiChou(次客在新天盘正常发用三传)"; fi
# 天地盘月将/时辰可视高亮:必须认 actualYue/realTimeBranch,不能用起课法的 X(this.yue)/Y(this.timezi) 对齐支。
LR_COMM2="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRCommChart.js"
LR_CIRCLE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRCircleChart.js"
LR_SQUARE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/LRTextSquareChart.js"
if grep -q "this.actualYue" "${LR_COMM2}" 2>/dev/null && grep -q "this.realTimeBranch" "${LR_COMM2}" 2>/dev/null; then ok "[21] LRCommChart 暴露 actualYue/realTimeBranch(高亮真源)"; else bad "[21] LRCommChart 缺 actualYue/realTimeBranch —— 月将/时辰高亮会落到起课法对齐支"; fi
if grep -q "highLightData: \[this.actualYue\]" "${LR_CIRCLE}" 2>/dev/null && grep -q "highLightData: \[this.realTimeBranch\]" "${LR_CIRCLE}" 2>/dev/null; then ok "[21] 圆盘高亮=真实月将(天盘)+真实时支(地盘)"; else bad "[21] 圆盘高亮仍用 this.yue(X) —— 会高亮起课法对齐的两格而非月将/时辰"; fi
{ grep -q "upBranch === this.actualYue" "${LR_SQUARE}" 2>/dev/null && grep -q "downBranch === this.realTimeBranch" "${LR_SQUARE}" 2>/dev/null; } || { bad "[21] 方盘 drawHouse 高亮仍用 this.yue/this.timezi —— 应改 actualYue/realTimeBranch"; }
# 中间盘小屏可下滑:RengChart.draw 设模式最小高度 + inline !important 撑高 svg + 读 host 视口高度。
LR_RENG="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/lrzhan/RengChart.js"
if grep -q "minChartH" "${LR_RENG}" 2>/dev/null && grep -q "setProperty('height'" "${LR_RENG}" 2>/dev/null; then ok "[21] 中间盘按模式最小高度绘制 + 撑高 svg(小屏 overflow-y 可下滑)"; else bad "[21] RengChart 缺 minChartH/撑高 svg —— 小屏方盘会裁切且无法下滑"; fi
}

seg_26() {
# 本段自己取(与前段同值;段与段之间不靠函数体里赋的变量传值,--only 单跑也成立)
AIEXPORT_JS="$(pf_src_set "${UISRC}/utils/aiExport.js")"
# 26. 奇门法奇门叠加层(荀爽:化解/用神/取象;纯前端,无 jar)四同步 + 引擎自检
echo "[26] 奇门法奇门叠加层(化解/用神/取象)"
DUNJIA_FACALC="${UISRC}/components/dunjia/DunJiaFaCalc.js"
DUNJIA_FADOC="${UISRC}/components/dunjia/DunJiaFaDoc.js"
DUNJIA_CALC_JS="${UISRC}/components/dunjia/DunJiaCalc.js"
if [ -f "${DUNJIA_FACALC}" ] && [ -f "${DUNJIA_FADOC}" ]; then ok "[26] DunJiaFaCalc/DunJiaFaDoc 在"; else bad "[26] 法奇门叠加层文件缺失"; fi
# 快照 8 段必须在(漏接=AI 导出/挂载/储存看不到化解·用神)
if grep -q "\[六害总览\]" "${DUNJIA_CALC_JS}" 2>/dev/null && grep -q "\[化解方案\]" "${DUNJIA_CALC_JS}" 2>/dev/null && grep -q "\[用神分论\]" "${DUNJIA_CALC_JS}" 2>/dev/null; then ok "[26] buildDunJiaSnapshotText 含法奇门段(六害/化解/用神)"; else bad "[26] 快照漏法奇门段(AI 四同步看不到化解·用神)"; fi
# 导出段表同步(漏=导出设置隐身)
if grep -q "'六害总览', '化解方案'" "${AIEXPORT_JS}" 2>/dev/null; then ok "[26] aiExport.qimen 段表含法奇门段"; else bad "[26] aiExport.qimen 段表漏法奇门段(导出设置隐身)"; fi
# 八神勾雀→虎玄归一(白虎检测两遁通用)必在
if grep -q "replace(/勾/g" "${DUNJIA_CALC_JS}" 2>/dev/null; then ok "[26] 八神勾雀→虎玄归一在(白虎检测两遁通用)"; else bad "[26] 缺勾雀→虎玄归一(阳遁白虎检测会失效)"; fi
# 神煞判语全覆盖自检 + 法奇门引擎单测在
if grep -q "神煞判语全覆盖" "${UISRC}/components/dunjia/__tests__/DunJiaFaDoc.test.js" 2>/dev/null; then ok "[26] 神煞判语全覆盖自检在"; else bad "[26] 缺神煞判语全覆盖自检"; fi
# 相关人员→生年干→八门化气大阵(命盘库选人,捕获各人生年干喂保护清单;未选则不显示该类)
if grep -q "export function birthToYearGan" "${DUNJIA_CALC_JS}" 2>/dev/null && grep -q "CHART_CATEGORY_OPTIONS" "${DUNJIA_CALC_JS}" 2>/dev/null; then ok "[26] DunJiaCalc 含 birthToYearGan(生年干)+CHART_CATEGORY_OPTIONS(命盘/事盘)"; else bad "[26] 缺 birthToYearGan/CHART_CATEGORY_OPTIONS"; fi
if grep -q "faRelatedPeople" "${DUNJIA_FACALC}" 2>/dev/null && ! grep -q "示本盘年干" "${DUNJIA_FACALC}" 2>/dev/null; then ok "[26] computeProtect 生年干来自相关人员(占位『示本盘年干』已移除)"; else bad "[26] computeProtect 仍用本盘年干占位/未读 faRelatedPeople"; fi
if grep -q "onRelatedPeopleChange" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null && grep -q "applyFaRelatedToPan" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 相关人员多选已接线(stamp pan.faRelatedPeople→AI 四同步单源)"; else bad "[26] 相关人员多选未接线/未 stamp pan"; fi
# 命盘/事盘双库:命盘复用命盘库(localCharts)、跨技法自用,奇门设置存 payload.qimen;新增命盘表单须透传 payload(否则丢)
if grep -q "saveAsMingChart" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null && grep -q "qimen: qimenSettings" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 命盘存 payload.qimen(复用命盘库,跨技法可用)"; else bad "[26] 命盘保存未走 payload.qimen"; fi
if grep -q "this.props.fields.payload" "${UISRC}/components/user/ChartAddFormComp.js" 2>/dev/null; then ok "[26] ChartAddFormComp 新增命盘透传 payload(修『新增命盘丢 payload』漏洞)"; else bad "[26] ChartAddFormComp 未透传 payload(奇门命盘设置会丢)"; fi
# 命盘信息完整(命盘管理完整显示):注入性别/经纬度+newCurrentChart honor;命盘保存恒弹新增抽屉(不静默原地更新)
if grep -q "gender: this.state.options" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null && grep -q "values.gender" "${UISRC}/models/user.js" 2>/dev/null; then ok "[26] 奇门命盘信息完整(注入性别/经纬度+newCurrentChart honor)"; else bad "[26] 奇门命盘信息不全(命盘管理缺性别等)"; fi
if ! grep -q "已更新该命盘的奇门设置" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 命盘保存恒弹新增星盘抽屉(无 cid 静默原地更新)"; else bad "[26] 命盘保存仍有 cid 静默原地更新(应恒弹新增抽屉)"; fi
# AI 四同步挂载无遗漏:重算 pan 路径补 faRelatedPeople(regenerate)+computeProtect 全局兜底
if grep -q "qs.faRelatedPeople" "$(pf_src_set "${UISRC}/utils/aiAnalysisContext.js")" 2>/dev/null; then ok "[26] AI 挂载 regenerateQimenSnapshot 补 faRelatedPeople(四同步无遗漏)"; else bad "[26] AI 挂载重算 pan 漏 faRelatedPeople(相关人员挂载缺失)"; fi
if grep -q "__horosa_qimen_related_people" "${DUNJIA_FACALC}" 2>/dev/null; then ok "[26] computeProtect 全局兜底相关人员(覆盖未 stamp 的重算路径)"; else bad "[26] computeProtect 缺全局兜底(部分挂载路径漏相关人员)"; fi
}

seg_26_2() {
# 26. 占卜/星盘各页 changeGeo 选地点 → 时区自动校正(resolveGeoZone 单一真源,11 时刻敏感页全接入)
echo "[26] 占卜/星盘选地点时区自动校正哨兵(resolveGeoZone)"
TZUTIL_JS="${UISRC}/utils/timezone.js"
RGZ_TEST_JS="${UISRC}/utils/__tests__/timezone.resolveGeoZone.test.js"
if grep -q "export function resolveGeoZone" "${TZUTIL_JS}" 2>/dev/null; then ok "[26] timezone.js 导出 resolveGeoZone(单一真源:手改优先/坐标推断/缺日期兜底今天)"; else bad "[26] timezone.js 缺 resolveGeoZone 导出"; fi
RGZ_PAGES="components/lrzhan/LiuRengInput.js components/lrzhan/LiuRengBirthInput.js components/suzhan/SuZhanInput.js components/guazhan/GuaZhanInput.js components/dunjia/DunJiaMain.js components/taiyi/TaiYiMain.js components/sanshi/SanShiUnitedMain.js components/divination/DivinationChartShell.js components/astro/IndiaChartMain.js components/astro3d/AstroChartMain3D.js components/dice/DiceMain.js"
rgz_miss=""
for pg in ${RGZ_PAGES}; do
  f="$(pf_src_set "${UISRC}/${pg}")"
  grep -q "resolveGeoZone" "$f" 2>/dev/null || rgz_miss="${rgz_miss} $(basename "$pg")"
done
[ -z "${rgz_miss}" ] && ok "[26] 11 时刻敏感页 changeGeo 均接入 resolveGeoZone(六壬/六壬命课/宿占/六爻/奇门/太乙/三式/卜卦择日/印度/3D/骰子)" || bad "[26] 以下页未接入 resolveGeoZone(选地点时区不校正):${rgz_miss}"
if [ -f "${RGZ_TEST_JS}" ]; then ok "[26] resolveGeoZone 全半球自检在(回归门禁)"; else bad "[26] 缺 timezone.resolveGeoZone.test"; fi
# 重锚 date/time:占卜 changeGeo 须 clone+setZone(z) 重锚(否则改时区只动字段、瞬时仍按旧时区→真太阳时/四柱错)
REANCHOR_PAGES="components/lrzhan/LiuRengInput.js components/suzhan/SuZhanInput.js components/guazhan/GuaZhanInput.js components/lrzhan/LiuRengBirthInput.js components/taiyi/TaiYiMain.js components/dunjia/DunJiaMain.js components/sanshi/SanShiUnitedMain.js components/kinastro/KinAstroMain.js"
reanchor_miss=""
for pg in ${REANCHOR_PAGES}; do
  grep -q "setZone(z)" "${UISRC}/${pg}" 2>/dev/null || reanchor_miss="${reanchor_miss} $(basename "$pg")"
done
[ -z "${reanchor_miss}" ] && ok "[26] 占卜各页 changeGeo 重锚 date/time(setZone(z)),改时区瞬时随之偏移、实时重算正确" || bad "[26] 以下页 changeGeo 未重锚 date/time(改时区真太阳时/四柱会错):${reanchor_miss}"
# 策天 KinAstroMain(cetian)选地点已接线(原 showLocation 但无 onGeoChange→选点失效)
if grep -q "onGeoChange={this.changeGeo}" "${UISRC}/components/kinastro/KinAstroMain.js" 2>/dev/null; then ok "[26] 策天 KinAstroMain 已接 onGeoChange+changeGeo(cetian 选点生效)"; else bad "[26] 策天 KinAstroMain 缺 onGeoChange(选地点失效)"; fi
# 奇门 changeGeo 延后 requestNongli 重排(避 hook 预取竞态以旧盘覆盖)
if grep -q "_geoRecalcTimer" "${UISRC}/components/dunjia/DunJiaMain.js" 2>/dev/null; then ok "[26] 奇门 changeGeo 延后强制重排(避竞态、改地点实时重算)在"; else bad "[26] 奇门 changeGeo 缺延后重排(改地点不重算风险)"; fi
# 六壬中间盘头部默认显真太阳时(非公历钟表时)
if grep -q "formatTrueSolarTime" "${UISRC}/components/lrzhan/RengChart.js" 2>/dev/null; then ok "[26] 六壬头部显真太阳时(formatTrueSolarTime)在"; else bad "[26] 六壬头部缺真太阳时显示(应默认显真太阳时)"; fi
}

seg_81() {
# 81. 太乙静默404三层守卫在位(2026-07-04 事故复盘;grep 特征串,不用文件存在性)
echo "[81] 太乙静默404三层守卫"
S81_BAD=0
S81_PY="${REPO_ROOT}/Horosa-Web/astropy"
grep -q "stub_dunder_guard_v1" "${S81_PY}/websrv/kentang/kinastro_common.py" 2>/dev/null || { bad "[81] 桩 dunder 守卫(stub_dunder_guard_v1)缺位"; S81_BAD=1; }
grep -q 'raise AttributeError(_name)' "${S81_PY}/websrv/kentang/kinastro_common.py" 2>/dev/null || { bad "[81] 桩 dunder 拒答语句缺位"; S81_BAD=1; }
[ "$(grep -c "__horosa_slim_stub__ = True" "${S81_PY}/websrv/kentang/kinastro_common.py" 2>/dev/null)" -ge 3 ] || { bad "[81] 子桩哨兵标记不足三处(顶桩+components+v1)"; S81_BAD=1; }
grep -q "class KentangServiceLoadError" "${S81_PY}/websrv/kentang/registry.py" 2>/dev/null || { bad "[81] registry 缺 KentangServiceLoadError 响亮失败类型"; S81_BAD=1; }
grep -q "KENTANG_LAZY_MOUNT_SELF_HEAL" "${S81_PY}/websrv/kentang/registry.py" 2>/dev/null || { bad "[81] registry 缺 sys.modules 自愈净化守卫"; S81_BAD=1; }
grep -q "_warm_real_astropy" "${S81_PY}/websrv/webchartsrv.py" 2>/dev/null || { bad "[81] webchartsrv 缺真 astropy 预热(顺序免疫层)"; S81_BAD=1; }
grep -q "stub_first" "${S81_PY}/tests/test_kentang_import_order.py" 2>/dev/null || { bad "[81] 双向导入门测试缺位/缺 stub_first 方向"; S81_BAD=1; }
[ "${S81_BAD}" = "0" ] && ok "[81] 三层守卫+双向导入门 全在位"
}

seg_184() {
# ── [184] 天星择日征象搜索:条件类型注册表 前↔后端 双向差空 ──
# 前端多键=用户可选而后端 invalid_conditions(死开关);后端多键=功能藏而不露。
# 键抓取契约:py 一键一行 '键': {...} / js 一键一行 \t键: {(两侧文件头均有注记);
# jest 哨兵(conditionTypesSync.test.js)带注错自证,此处再做 bash 轻量双向差(零依赖秒级)。
echo "== [184] 择日征象条件类型 前↔后端一致性 =="
S184_BAD=0
S184_PY="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/election_scan.py"
S184_JS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/divination/zeri/conditionTypes.js"
S184_JEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/divination/zeri/__tests__/conditionTypesSync.test.js"
# R4 对齐制度化:tab 对拍资产(页签↔扫描引擎双端锁)与 explain 全类契约不许缺席/缩水:
# 「选了什么→搜出来→点开右栏严密符合」的机械保证。
S184_PARITY="${REPO_ROOT}/Horosa-Web/astropy/tests/test_election_scan_tab_parity.py"
S184_ENDP="${REPO_ROOT}/Horosa-Web/astropy/tests/test_election_scan_endpoint.py"
for f in "${S184_PY}" "${S184_JS}" "${S184_JEST}" "${S184_PARITY}" "${S184_ENDP}"; do
  [ -f "${f}" ] || { bad "[184] 🔴 缺真值源/哨兵文件:${f}"; S184_BAD=1; }
done
if [ -f "${S184_PARITY}" ]; then
  S184_NPAR=$(grep -ac "^def test_" "${S184_PARITY}" || true)
  [ "${S184_NPAR}" -ge 9 ] || { bad "[184] 🔴 tab 对拍资产缩水(${S184_NPAR}<9)——对齐护栏被删?"; S184_BAD=1; }
fi
if [ -f "${S184_ENDP}" ]; then
  grep -aq "test_explain_contract_all_types_and_scan_agreement" "${S184_ENDP}"     || { bad "[184] 🔴 explain 全类契约测试缺席(新类可无实测文本=详情面板哑)"; S184_BAD=1; }
fi
if [ "${S184_BAD}" = "0" ]; then
  S184_PYKEYS=$(sed -n "/^CONDITION_TYPES = {/,/^}/p" "${S184_PY}" | grep -aoE "^    '[a-z_]+':" | tr -d " ':" | sort)
  S184_JSKEYS=$(sed -n "/^export const CONDITION_TYPES = {/,/^};/p" "${S184_JS}" | grep -aoE $'^\t[a-z_]+:' | tr -d $'\t:' | sort)
  S184_NPY=$(printf '%s\n' "${S184_PYKEYS}" | grep -ac . || true)
  S184_NJS=$(printf '%s\n' "${S184_JSKEYS}" | grep -ac . || true)
  if [ "${S184_NPY}" -lt 10 ] || [ "${S184_NJS}" -lt 10 ]; then
    bad "[184] 🔴 键抓取塌缩(py=${S184_NPY}/js=${S184_NJS} <10)——一键一行格式契约被破或 regex 失配"; S184_BAD=1;
  elif [ "${S184_PYKEYS}" != "${S184_JSKEYS}" ]; then
    bad "[184] 🔴 条件类型键集不一致(前端死开关或后端藏功能):"; S184_BAD=1;
    diff <(printf '%s\n' "${S184_PYKEYS}") <(printf '%s\n' "${S184_JSKEYS}") | sed 's/^/[184]   /' >&2 || true
  fi
  grep -aq "注错自证" "${S184_JEST}" 2>/dev/null || { bad "[184] 🔴 jest 哨兵缺注错自证断言(哨兵可能已死)"; S184_BAD=1; }
fi
[ "${S184_BAD}" = "0" ] && ok "[184] 择日条件类型前后端恒等(py=${S184_NPY} 键)+jest 哨兵自证在位"
}

seg_185() {
# ── [185] 六壬伏吟子卯互刑末传取冲(#62) ──
# 病史:伏吟中末传沿刑链取(中=初刑,末=中刑,唯中传自刑取冲),而刑表子↔卯为唯一二环——
# 中传所刑还回初传时旧码照取,丁卯/己卯/辛卯日伏吟排出「卯子卯」(#62 实报,应卯子午)。
# 勘正:初中两传恰为子卯互刑(传行杜塞)→ 末传取中传所冲;明令仅此一对,不作更泛抽象。
# 🔴 seg_160 型「对拍在位」哨兵抓不到本类病:720 对拍 oracle 的伏吟段曾与引擎同盲区(对拍恒绿)。
# 故本哨兵直接锁:引擎守卫+三分支接线+oracle 同口径+用户实报课式金标锚+反越界锚。
echo "== [185] 六壬伏吟子卯互刑末传取冲(#62) =="
S185_BAD=0
S185_ENG="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/ChuangChart.js"
S185_ORACLE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/__tests__/liurengNineMethodOracle.test.js"
S185_GOLD="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/liureng/__tests__/liurengSanChuanGolden.test.js"
grep -aq "getFuYinLastCuang(cuang0, cuang1){" "${S185_ENG}" 2>/dev/null || { bad "[185] 🔴 引擎伏吟末传守卫函数缺失(getFuYinLastCuang)"; S185_BAD=1; }
grep -aq "cuang0 === '子' && cuang1 === '卯'" "${S185_ENG}" 2>/dev/null || { bad "[185] 🔴 引擎子卯互刑字面守卫缺失(或被泛化改写)"; S185_BAD=1; }
S185_WIRE=$(grep -ac "this.getFuYinLastCuang(cuang0, cuang1)" "${S185_ENG}" 2>/dev/null)
S185_WIRE=${S185_WIRE:-0}
[ "${S185_WIRE}" -ge 3 ] || { bad "[185] 🔴 伏吟三分支(不虞/自任·杜传/自信·杜传)末传接线不足(需≥3,现 ${S185_WIRE})"; S185_BAD=1; }
grep -aqF "(x1.selfX || ziMaoLoop)" "${S185_ORACLE}" 2>/dev/null || { bad "[185] 🔴 720 对拍 oracle 未同步子卯口径(半截修复:引擎与 oracle 将再度同盲或互红)"; S185_BAD=1; }
grep -aq "#62" "${S185_GOLD}" 2>/dev/null || { bad "[185] 🔴 金标缺 #62 勘正区块标记"; S185_BAD=1; }
grep -aq "'卯', '子', '午'" "${S185_GOLD}" 2>/dev/null || { bad "[185] 🔴 金标缺 #62 实报课式锚(丁卯/己卯/辛卯伏吟→卯子午)"; S185_BAD=1; }
grep -aq "'辰', '卯', '子'" "${S185_GOLD}" 2>/dev/null || { bad "[185] 🔴 金标缺反越界锚(乙卯不虞辰卯子:守卫只认初中互刑环)"; S185_BAD=1; }
grep -aq "'亥', '子', '卯'" "${S185_GOLD}" 2>/dev/null || { bad "[185] 🔴 金标缺反越界锚(壬子杜传亥子卯:中末子卯相邻不得改写)"; S185_BAD=1; }
pf_test_disabled "${S185_GOLD}" && { bad "[185] 🔴 金标文件被 skip / only 旁路"; S185_BAD=1; }
[ "${S185_BAD}" = "0" ] && ok "[185] 六壬伏吟子卯守卫(引擎+三分支接线+oracle 同口径+金标/反越界锚)全在位"
}

seg_260() {
# seg_260 快捷数字时间录入(左栏双击键入 / 表单「快捷输入」)接线锁:解析单源 + 共享触发件 + 五站点 + 三表单 + 起课标签 + 帮助文档 + 回归锁
echo "[${PF_NO}] 快捷数字时间录入接线锁"
S260_BAD=0
S260_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
pf_need "${S260_UI}/utils/quickDateTimeDigits.js" "export function applyQuickDigits(" "解析单源缺 applyQuickDigits"
pf_need "${S260_UI}/utils/quickDateTimeDigits.js" "if(month === 0){ month = 1; }" "补零月份未按 01 处理"
pf_need "${S260_UI}/components/comp/QuickTimeField.js" "export class TimeFieldTrigger" "共享触发件缺失"
pf_need "${S260_UI}/components/comp/QuickTimeField.js" "export class QuickTimeInput" "表单快捷输入件缺失"
pf_need "${S260_UI}/components/comp/QuickTimeField.js" "onDoubleClick={this.startEdit}" "双击进入键入态的接线缺失"
pf_none "${S260_UI}/components/comp/QuickTimeField.js" "maxLength" "输入框不得设 maxLength(粘贴带分隔符时间会先被截断)"
for f in comp/SpaceTimePanel.js astro/AstroChartMain.js divination/DivinationChartShell.js horary/HoraryMain.js mundane/MundaneMain.js; do
  pf_need "${S260_UI}/components/${f}" "<TimeFieldTrigger" "${f} 未走共享触发件"
  pf_none "${S260_UI}/components/${f}" "content={timeEditor}" "${f} 仍有手抄 Popover 时间块"
done
for f in user/ChartData.js user/CaseData.js comp/ChartFormData.js; do pf_need "${S260_UI}/components/${f}" "<QuickTimeInput" "${f} 缺快捷输入行"; done
pf_need "${S260_UI}/components/user/CaseData.js" "起课时间：" "起课表单标签未改名"
pf_none "${S260_UI}/components/user/CaseData.js" "起课事件：" "起课表单旧标签残留"
pf_need "${S260_UI}/components/help/AstroHelpDoc.js" "双击" "占星帮助未写快输"
pf_need "${S260_UI}/components/comp/QuickTimeField.js" "export class QuickTimeText" "单行时间文本共享件缺 QuickTimeText"
pf_need "${S260_UI}/components/planetarium/PlanetariumBabylon.js" "<QuickTimeText" "天文馆时间行未接 QuickTimeText"
pf_none "${S260_UI}/components/planetarium/PlanetariumBabylon.js" "<div ref={this._timeDisplayRef}" "天文馆仍有手写时间行"
pf_need "${S260_UI}/components/xq-ui/index.js" "export function QuickDigitsHost" "xq-ui 缺数字快输宿主"
pf_need "${S260_UI}/components/xq-ui/index.js" "export function XQTimePicker" "xq-ui 缺 XQTimePicker"
pf_need "${S260_UI}/utils/quickDateTimeDigits.js" "export function parseQuickDigitsForFormat(" "解析单源缺按 format 切位"
S260_RAW="$(grep -rlE --include='*.js' "import[[:space:]]*\{[^}]*(DatePicker|TimePicker)[^}]*\}[[:space:]]*from[[:space:]]*'antd'" "${S260_UI}/components" 2>/dev/null | grep -v "xq-ui/index.js" | grep -v "__tests__" || true)"
[ -z "${S260_RAW}" ] || { bad "[${PF_NO}] 组件层仍直接引 antd DatePicker/TimePicker(绕过数字快输宿主): ${S260_RAW}"; S260_BAD=1; }
pf_need "${S260_UI}/components/help/PlanetariumHelpDoc.js" "双击" "天文馆帮助未写快输"
for f in utils/__tests__/quickDateTimeDigits components/comp/__tests__/quickTimeFieldTrigger components/comp/__tests__/spaceTimePanelQuickEntry utils/__tests__/recordFormsQuickTime components/comp/__tests__/quickTimeFieldWiring components/comp/__tests__/quickTimeText components/xq-ui/__tests__/xqPickerQuickDigits; do
  [ -f "${S260_UI}/${f}.test.js" ] || { bad "[${PF_NO}] 回归锁 ${f}.test.js 缺失"; S260_BAD=1; }
done
[ "${S260_BAD}" = "0" ] && ok "[${PF_NO}] 快捷数字时间录入接线锁"
}

seg_286() {
echo "[${PF_NO}] 加载态收敛:玄学史序号各守各的 · 神数正传条文库按派归属 · 双触发收敛通用件接线(2026-09-26)"
S286_BAD=0
S286_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
for S286_F in "components/xuanshi/__tests__/xuanshiLoaderSeq.test.js" "components/shusuan/__tests__/zhengchuanVersesLoad.test.js" "utils/__tests__/singleTrigger.test.js" "utils/singleTrigger.js"; do
  [ -s "${S286_UI}/${S286_F}" ] || { bad "[${PF_NO}] 🔴 缺 ${S286_F}"; S286_BAD=1; }
done
grep -q "this._dynSeq" "${S286_UI}/components/xuanshi/XuanShiStories.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 故事专题朝代选项未用独立序号(与列表共用 = 首开永远「载入…」)"; S286_BAD=1; }
grep -q "this._microSeq" "${S286_UI}/components/xuanshi/XuanShiCelestial.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 星象大典年代明细未用独立序号"; S286_BAD=1; }
grep -q "currentVerses()" "${S286_UI}/components/shusuan/ZhengChuanMain.js" 2>/dev/null && grep -q "versesFor" "${S286_UI}/components/shusuan/ZhengChuanMain.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 神数正传条文库未按派归属管理"; S286_BAD=1; }
S286_N=0
for S286_C in guolao/GuoLaoChartMain taiyi/TaiYiMain babylon/BabylonMain astro/AstroDecennials germany/UranianDialMain germany/UranianGraphicEphemeris germany/UranianHouseFrames huangji/HuangJiMain jingjue/JingJueMain shenyishu/ShenYiShuMain taixuan/TaiXuanMain wuzhao/WuZhaoMain kinastro/KinAstroMain; do
  if grep -q "claimTrigger(this, '" "$(pf_src_set "${S286_UI}/components/${S286_C}.js")" 2>/dev/null; then S286_N=$((S286_N + 1)); else bad "[${PF_NO}] 🔴 ${S286_C} 未接双触发收敛(挂钩与更新钩子同参各算一遍)"; S286_BAD=1; fi
done
[ "${S286_BAD}" = "0" ] && ok "[${PF_NO}] 玄学史两组件序号独立 + 神数正传条文库按派归属 + 双触发收敛接线 ${S286_N} 处 + 回归测试在场"
}

seg_61() {
# [61] 风水 十三派:理气六派(八宅/玄空/三合/金锁/乾坤/紫白)+水法(辅星/净阴净阳)+玄空大卦+形势+择日 纯计算引擎 + 流派UI + 户型图两法零回归
S61_BAD=0
echo "[61] 风水 十三派 引擎+流派UI+玄空进阶+深化(黄泉/拨砂/线法/九水位/门主灶/年神)+零回归"
S61_FS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/fengshui"
for f in fengshuiData.js liqiCore.js xuankong.js sanhe.js zibai.js qiankun.js bazhai.js jinsuo.js LiqiWorkspace.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水理气 ${f}"; S61_BAD=1; }
done
# 新增五派引擎(辅星/净阴净阳/玄空大卦/形势/择日)
for f in fuxing.js jingyin.js dagua.js xingshi.js zeri.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水新派 ${f}"; S61_BAD=1; }
done
for f in charts/LuoshuGrid.js charts/TwentyFourShanRing.js charts/EightPalaceDisk.js charts/SixtyFourGuaRing.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水盘面 ${f}"; S61_BAD=1; }
done
# 六派深化 + 新派核心纯函数
grep -qE "export function sanheXiangFaAll" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺三合十二向 sanheXiangFaAll(5.9)"; S61_BAD=1; }
grep -qE "export function boshaWuGe" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺拨砂五格 boshaWuGe(5.11)"; S61_BAD=1; }
grep -qE "export function huangquanBaYao" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺黄泉八煞 huangquanBaYao(5.5)"; S61_BAD=1; }
grep -qE "export function (chuanshanAt|toudiAt|fenjinAt)" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺线法穿山透地分金(5.12-14)"; S61_BAD=1; }
grep -qE "export function qkgbFullPositions" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺乾坤九水位 qkgbFullPositions(7.B)"; S61_BAD=1; }
grep -qE "export function jianXiangByDeg" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺玄空兼向度数判别 jianXiangByDeg(4.5)"; S61_BAD=1; }
grep -qE "export function gua64Of" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺玄空大卦识卦 gua64Of(6.7)"; S61_BAD=1; }
grep -qE "export function guaRelation" "${S61_FS}/bazhai.js" 2>/dev/null || { bad "[61] 缺八宅门主灶 guaRelation(3.9)"; S61_BAD=1; }
grep -qE "export function dayCenter" "${S61_FS}/zibai.js" 2>/dev/null || { bad "[61] 缺日紫白 dayCenter(8.1.3)"; S61_BAD=1; }
grep -qE "export function yearGods" "${S61_FS}/zeri.js" 2>/dev/null || { bad "[61] 缺择日年神 yearGods(9.1)"; S61_BAD=1; }
# 新数据底座(纳甲/纳音/64卦/黄泉/三煞)
grep -qE "NAJIA_GUA|NAYIN_60|GUA64_TABLE|BA_YAO_SHA|SANSHA_BY_JU" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 缺新数据底座(纳甲/纳音/64卦/黄泉/三煞)"; S61_BAD=1; }
# 玄空进阶:替卦(4.12)/替星(4.5)/城门(4.14)/七星打劫(4.13)
grep -qE "export function flyChartTi" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺替卦 flyChartTi(4.12)"; S61_BAD=1; }
grep -qE "export function tixingOf" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺替星 tixingOf(4.5)"; S61_BAD=1; }
grep -qE "TIXING_VARIANTS" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 缺替星3方案"; S61_BAD=1; }
grep -qE "function cityGate" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] 缺城门诀 cityGate(4.14)"; S61_BAD=1; }
grep -qE "function sevenStarRob" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] 缺七星打劫 sevenStarRob(4.13)"; S61_BAD=1; }
# 下卦默认零回归:替卦必须 opt-in(默认走 flyChart 非 flyChartTi)
grep -qE "jian \? flyChartTi" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] xuankong 替卦未 opt-in(下卦零回归风险)"; S61_BAD=1; }
# FengShuiMain:流派选择器 + 户型图两法画布引擎保持挂载(理气派 display:none 零回归)
grep -qE "import FengShuiEngine" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain 丢画布引擎(户型图两法回归)"; S61_BAD=1; }
grep -qE "LIQI_SET|SCHOOL_GROUPS" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain 缺流派选择器"; S61_BAD=1; }
grep -qE "canvas-body" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain 缺 canvas 保活(零回归)"; S61_BAD=1; }
# onVm 守:理气/新派激活时画布引擎 vm 不得覆盖当前流派快照(否则 AI 导出取到纳气盘)
grep -qE "snapshotText && !LIQI_SET.has" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain onVm 缺理气快照防覆盖守(AI导出会取错派)"; S61_BAD=1; }
# golden + 压测测试在位(下卦 byte 守 out_grid/sanhe/zibai/qkgb + 替卦同卦不变性 + 深化/新派锚)
for t in liqiCore.test.js xuankong.test.js schools.test.js xuankongAdvanced.test.js charts.test.js fengshuiOptionMatrix.test.js fengshuiQaRound2.test.js fengshuiManualAnchor.test.js \
         sanheAugment.test.js qiankunAugment.test.js bazhaiAugment.test.js xuankongAugment.test.js zibaiAugment.test.js newSchools.test.js fengshuiStress.test.js; do
  [ -f "${S61_FS}/__tests__/${t}" ] || { bad "[61] 缺风水测试 ${t}"; S61_BAD=1; }
done
# nav 可发现十三派(理气六派 + 新派关键词)
grep -qE "key: 'fengshui'.*金锁玉关.*乾坤国宝" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js" 2>/dev/null || { bad "[61] nav 缺理气六派关键词"; S61_BAD=1; }
grep -qE "key: 'fengshui'.*玄空大卦.*形势.*择日" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js" 2>/dev/null || { bad "[61] nav 缺新派关键词(大卦/形势/择日)"; S61_BAD=1; }
# ── 补齐（十六项）：综合罗经13层三针 / 玄空门派度界分运 / 玄空六法 / 命理派 / 形体图库 / 落卦 / 应期 / 造命四纲 ──
for f in xuankongLiufa.js mingli.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水新派 ${f}"; S61_BAD=1; }
done
for f in charts/LuopanDial.js charts/XianfaRing.js charts/SixtyFourGuaCircle.js charts/XingshiFormGallery.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺风水盘面 ${f}"; S61_BAD=1; }
done
grep -qE "export function xuankongLiufa" "${S61_FS}/xuankongLiufa.js" 2>/dev/null || { bad "[61] 缺玄空六法 xuankongLiufa(8.6)"; S61_BAD=1; }
grep -qE "export function mingli" "${S61_FS}/mingli.js" 2>/dev/null || { bad "[61] 缺命理派 mingli(8.4)"; S61_BAD=1; }
grep -qE "export function gua64AtDeg" "${S61_FS}/liqiCore.js" 2>/dev/null || { bad "[61] 缺六十四卦圆图落卦 gua64AtDeg(6.1)"; S61_BAD=1; }
# 数据底座：罗盘13层 + 三针偏移 + 门派表 + 六法 + 圆图 + 形体图
grep -qE "export const LUOPAN_LAYERS" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 缺罗盘层序表 LUOPAN_LAYERS(10.7)"; S61_BAD=1; }
grep -qE "NEEDLE_OFFSET = \{ zheng: 0, ren: -7\.5, feng: 7\.5 \}" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 三针偏移非 正0/中-7.5/缝+7.5(0.4)"; S61_BAD=1; }
for k in XUANKONG_SCHOOLS LIUFA_ITEMS GUA64_CIRCLE XINGSHI_SHAPES XIU28_RING; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 缺数据底座 ${k}"; S61_BAD=1; }
done
# 🔴 玄空门派：唯「中州 ⇒ 五黄两元八运」一条自动联动；严禁门派→替星表/度界的臆造映射
S61_AUTO=$(grep -cE "auto: \{ wuHuangSplit: 'liangyuan' \}" "${S61_FS}/fengshuiData.js" 2>/dev/null || true)
[ "${S61_AUTO}" = "1" ] || { bad "[61] 玄空门派自动联动应恰 1 条(中州=>五黄两元八运),实得 ${S61_AUTO}"; S61_BAD=1; }
if grep -qE "auto: \{ (tiVariant|jianBoundary)" "${S61_FS}/fengshuiData.js" 2>/dev/null; then bad "[61] 门派携带替星表/兼向度界联动=臆造映射(古籍未指名归派)"; S61_BAD=1; fi
# 度界参数化真接线（此前 jianXiangByDeg 只传 deg、吃默认 3）
grep -qE "jianXiangByDeg\(opts\.deg, jianBoundary\)" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] 玄空兼向度界未接线(jianBoundary 死开关)"; S61_BAD=1; }
# 🔴 真/假打劫不得压平（曾写成三元表达式两分支同值，把坎宫假打劫吞成 good）
if grep -qE "nature: r\.nature === 'good' \? 'good' : 'good'" "${S61_FS}/xuankong.js" 2>/dev/null; then bad "[61] 七星打劫真假被压平(坎宫假打劫会被吞成真)"; S61_BAD=1; fi
grep -qE "nature: 'mild'" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] ROB_GROUPS 丢假打劫 mild 档"; S61_BAD=1; }
# 造命四纲：补龙/相主入参 + 纲分组
# 锚在签名首段而非其尾：尾部会随 additive 入参增长而漂移，锚在尾＝每加一个参就假红。
grep -qF "export function zaoMing({ zuoShan = '子', y, m, d, laiLong, zhuMing," "${S61_FS}/zeri.js" 2>/dev/null || { bad "[61] 择日造命缺补龙/相主入参(9.5 四纲)"; S61_BAD=1; }
grep -qE "gang: '补龙'" "${S61_FS}/zeri.js" \
  && grep -qE "gang: '相主'" "${S61_FS}/zeri.js" \
  && grep -qE "gang: '避煞'" "${S61_FS}/zeri.js" 2>/dev/null || { bad "[61] 造命 items 缺纲分组"; S61_BAD=1; }
# 金锁应期 + 形势定穴九法
grep -qE "p\.yingqi = \{" "${S61_FS}/jinsuo.js" 2>/dev/null || { bad "[61] 金锁玉关缺应期(7.A.7)"; S61_BAD=1; }
grep -qE "s\.dingXue \? 1 : 0" "${S61_FS}/xingshi.js" 2>/dev/null || { bad "[61] 形势定穴九法未入穴分(2.9)"; S61_BAD=1; }
# 三新派必须进 LIQI_SET，否则 onVm 守失效、画布快照覆盖本派快照（既有事故模式）
grep -qE "'liufa', 'mingli', 'luopan'" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] 三新派未进 LIQI_SCHOOLS(画布快照会覆盖=AI导出取错盘)"; S61_BAD=1; }
grep -qE "liufa: '玄空六法'" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] SCHOOL_CN 缺三新派(buildSnapshot 头部依赖)"; S61_BAD=1; }
# 中栏多件必须走竖排容器（本身是 row flex，漏套会挤成两栏）
grep -qE "horosa-fengshui-chart-stack[^A-Za-z0-9_-]" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] 中栏多件缺竖排容器(主盘与副图会并排)"; S61_BAD=1; }
grep -qE "\.horosa-fengshui-chart-stack[^A-Za-z0-9_-]" "$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.less")" 2>/dev/null || { bad "[61] app.less 缺竖排容器样式"; S61_BAD=1; }
# aiExport 三新段登记 + 键内 union 迁移（不升 MIGRATION_VERSION，避免破 v45「取消=真取消」）
S61_AIX="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiExport.js")"
# 三段行尾不钉 `],`(其后还可能接别的段,行尾会变逗号),三段本身与先后仍钉死
grep -qE "^[[:space:]]+'风水·玄空六法', '风水·命理派', '风水·综合罗经'," "${S61_AIX}" 2>/dev/null || { bad "[61] aiExport 缺风水三新导出段"; S61_BAD=1; }
grep -qE "AI_EXPORT_V49_SECTION_UNION[^A-Za-z0-9_]" "${S61_AIX}" 2>/dev/null || { bad "[61] aiExport 缺三新段 union 迁移(老用户自定义会静默丢新段)"; S61_BAD=1; }
# 测试在册
for t in xuankongSchools.test.js zeriAugment.test.js newSchools2.test.js gua64Circle.test.js; do
  [ -f "${S61_FS}/__tests__/${t}" ] || { bad "[61] 缺风水测试 ${t}"; S61_BAD=1; }
done
grep -qE "LuopanDial[^A-Za-z0-9_]" "${S61_FS}/__tests__/charts.test.js" 2>/dev/null || { bad "[61] charts.test 未覆盖盘面"; S61_BAD=1; }
grep -qE "xuankongLiufa[^A-Za-z0-9_]" "${S61_FS}/__tests__/fengshuiStress.test.js" 2>/dev/null || { bad "[61] 压测未覆盖新派"; S61_BAD=1; }
# nav 可发现
grep -qE "key: 'fengshui'.*玄空六法.*罗经.*补龙" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js" 2>/dev/null || { bad "[61] nav 缺关键词(六法/罗经/补龙)"; S61_BAD=1; }
# 🔴 显示层零来源泄漏：帮助文档与理气工作区不得出现章节号/书名
# ── （十七项）：大玄空(单盘挨星) + registry 新派机制 ──────────────────
# registry：新派走注册表（旧十四派 legacy switch 不迁移）；契约六成员齐备才算落成。
for f in daxuankong.js fengshuiLiqiDeepData.js liqi/registry.js liqi/daxuankongSchool.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺大玄空/registry ${f}"; S61_BAD=1; }
done
grep -qE "export function daxuankong" "${S61_FS}/daxuankong.js" 2>/dev/null || { bad "[61] 缺大玄空主入口 daxuankong"; S61_BAD=1; }
grep -qE "export function (yuanOf|starNature|palaceStar)" "${S61_FS}/daxuankong.js" 2>/dev/null || { bad "[61] 缺大玄空核心纯函数(元属/正零/宫星)"; S61_BAD=1; }
for k in DAXUANKONG_YANG_JUE DAXUANKONG_AISTAR_YANG DAXUANKONG_AISTAR_YIN DAXUANKONG_ZHENGLING DAXUANKONG_DUANYING; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiLiqiDeepData.js" 2>/dev/null || { bad "[61] 缺大玄空数据 ${k}"; S61_BAD=1; }
done
grep -qE "export const LIQI_SCHOOL_IMPL" "${S61_FS}/liqi/registry.js" 2>/dev/null || { bad "[61] registry 缺 LIQI_SCHOOL_IMPL"; S61_BAD=1; }
for m in defaults compute Params Chart Panel snapshotLines; do
  grep -qE "export (function |const )${m}" "${S61_FS}/liqi/daxuankongSchool.js" 2>/dev/null || { bad "[61] registry 派缺契约成员 ${m}"; S61_BAD=1; }
done
# 🔴 registry 派的 snapshotLines 绝不自带段头（自带＝双段头，导出段过滤器会切坏）
#    只咬「字符串字面量里的段头」——注释里写明该纪律是允许的，故锚 push/return 后紧跟引号的形态。
if grep -nE "(push|return)[[:space:]]*\([[:space:]]*[\`'\"]【风水·" "${S61_FS}/liqi/"*.js 2>/dev/null | pipe_has .; then bad "[61] registry 派 snapshotLines 自带段头(会产双段头切坏导出)"; S61_BAD=1; fi
grep -qE "if \(impl\) \{ return L\.concat" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] buildSnapshot 未单点统一冠段头(registry 派快照无头)"; S61_BAD=1; }
# 五处齐动：白名单/流派表/导出段/union 迁移
grep -qE "'luopan', 'daxuankong'" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] 大玄空未进 LIQI_SCHOOLS(画布快照会覆盖=AI导出取错盘)"; S61_BAD=1; }
grep -qE "daxuankong: '大玄空'" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] SCHOOL_CN 缺大玄空(buildSnapshot 头部依赖)"; S61_BAD=1; }
grep -qE "'风水·综合罗经', '风水·大玄空'," "${S61_AIX}" 2>/dev/null || { bad "[61] aiExport 缺风水·大玄空导出段"; S61_BAD=1; }
grep -qE "AI_EXPORT_V52_SECTION_UNION[^A-Za-z0-9_]" "${S61_AIX}" 2>/dev/null || { bad "[61] aiExport 缺 v52 union 迁移(老用户自定义会静默丢大玄空段)"; S61_BAD=1; }
# 🔴 MIGRATION_VERSION 不得因新派上升（升了会令 v45+ 存档重走全 preset union、破「取消=真取消」）
grep -qE "^(export )?const AI_EXPORT_SECTION_MIGRATION_VERSION = 44;" "${S61_AIX}" 2>/dev/null || { bad "[61] MIGRATION_VERSION 被改动(v45 取消=真取消 铁律)"; S61_BAD=1; }
# 大玄空 golden 在册（书中四算例逐宫对拍）
[ -f "${S61_FS}/__tests__/daxuankong.test.js" ] || { bad "[61] 缺大玄空 golden 测试"; S61_BAD=1; }
grep -qE "账⑤" "${S61_FS}/__tests__/fengshuiFourLedgers.test.js" 2>/dev/null || { bad "[61] 四本账缺 LIQI_SCHOOLS 白名单恒等哨兵"; S61_BAD=1; }
# ── 形势九纲深化────────────────────────────────────────
[ -f "${S61_FS}/fengshuiXingshiData.js" ] || { bad "[61] 缺形势深化数据 fengshuiXingshiData.js"; S61_BAD=1; }
for k in DINGXUE_13 ZHENGXUE_13 JIUXING_BIANXUE_8 MINGTANG_JI_9 MINGTANG_XIONG_9 LONGHU_DUAN_15 SHUIKOU_5SHA GUAIXUE_8 ZIRAN_SHUIFA SHANXUE_4JI HEXING_41; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiXingshiData.js" 2>/dev/null || { bad "[61] 缺形势九纲数据 ${k}"; S61_BAD=1; }
done
# 🔴 并存不合并：古籍十三法与既有九法/十证必须各自独立存在（合表＝造出典籍没有的第三套）
grep -qE "export const DINGXUE_9" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 既有定穴九法被删(应与十三法并存)"; S61_BAD=1; }
grep -qE "export const ZHENGXUE_10" "${S61_FS}/fengshuiData.js" 2>/dev/null || { bad "[61] 既有证穴十证被删(应与十三法并存)"; S61_BAD=1; }
# 🔴 九纲必须 opt-in：缺省口径逐字节零回归（图判工作台喂的就是缺省档）
grep -qE "if \(s\.scoreMode !== 'nine'\)" "${S61_FS}/xingshi.js" 2>/dev/null || { bad "[61] 形势九纲未 opt-in(缺省口径零回归风险)"; S61_BAD=1; }
grep -qE "function nineGang" "${S61_FS}/xingshi.js" 2>/dev/null || { bad "[61] 缺形势九纲实现 nineGang"; S61_BAD=1; }
# 三条古籍权重调制（非线性）必须在位
for m in jiaLong shaByLong wuAnChao; do
  grep -qE "key: '${m}'" "${S61_FS}/xingshi.js" 2>/dev/null || { bad "[61] 形势缺权重调制 ${m}"; S61_BAD=1; }
done
[ -f "${S61_FS}/__tests__/xingshiNineGang.test.js" ] || { bad "[61] 缺形势九纲测试"; S61_BAD=1; }
# ── 水龙(平洋)新派 —— 与山龙并行两路，多处口径相反不可套用 ──────────
for f in shuilong.js fengshuiShuilongData.js liqi/shuilongSchool.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺水龙 ${f}"; S61_BAD=1; }
done
grep -qE "export function shuilong" "${S61_FS}/shuilong.js" 2>/dev/null || { bad "[61] 缺水龙主入口"; S61_BAD=1; }
grep -qE "export function fenPai" "${S61_FS}/shuilong.js" 2>/dev/null || { bad "[61] 缺水龙地形分派 fenPai"; S61_BAD=1; }
for k in SHUILONG_4JI SHUI_8JI_ZI SHUI_8XIONG_ZI SHUILONG_XUE_6 SHUILONG_3GE XIDAO_LOUDAO SHUILONG_JIGE SHUILONG_XIONGGE SHUILONG_WUXING; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiShuilongData.js" 2>/dev/null || { bad "[61] 缺水龙数据 ${k}"; S61_BAD=1; }
done
# 🔴 与山龙相反的三处口径必须显式标注（混用即错）
grep -qE "与山龙相反" "${S61_FS}/fengshuiShuilongData.js" 2>/dev/null || { bad "[61] 水龙未标注与山龙相反口径(五星/穴后高低)"; S61_BAD=1; }
grep -qE "水穴后高绝无踪" "${S61_FS}/fengshuiShuilongData.js" 2>/dev/null || { bad "[61] 水龙缺穴后高低口径"; S61_BAD=1; }
grep -qE "maxDepthM: 2" "${S61_FS}/fengshuiShuilongData.js" 2>/dev/null || { bad "[61] 水龙缺葬深 2 米硬上限"; S61_BAD=1; }
grep -qE "'luopan', 'daxuankong', 'shuilong'" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] 水龙未进 LIQI_SCHOOLS"; S61_BAD=1; }
grep -qE "shuilong: '水龙平洋'" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] SCHOOL_CN 缺水龙"; S61_BAD=1; }
grep -qE "'风水·大玄空', '风水·水龙平洋'," "${S61_AIX}" 2>/dev/null || { bad "[61] aiExport 缺风水·水龙平洋段"; S61_BAD=1; }
grep -qE "AI_EXPORT_V53_SECTION_UNION[^A-Za-z0-9_]" "${S61_AIX}" 2>/dev/null || { bad "[61] aiExport 缺 v53 union 迁移"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/shuilong.test.js" ] || { bad "[61] 缺水龙测试"; S61_BAD=1; }
# ── 理气深化 —— 三合赖公拨砂/格龙 · 八宅法脉三档/三元阳宅 · 玄空收山出煞 ──
#   三者一律 additive：缺省档逐字节零回归(既有 golden/图判工作台喂的都是缺省档)。
for k in LAIGONG_BOSHA_WUXING LAIGONG_BOSHA_SUBLABEL LAIGONG_BOSHA_NOTE; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiLiqiDeepData.js" 2>/dev/null || { bad "[61] 缺赖公拨砂数据 ${k}"; S61_BAD=1; }
done
# 🔴 赖公拨砂走**人盘中针**(退半山=+7.5°)，与双山三合五行不同源，两档结论允许相反、不可互校。
grep -qE "shanAtDeg\(SHAN_CENTER_DEG\[zuoShanForBosha\] \+ 7\.5\)" "${S61_FS}/sanhe.js" 2>/dev/null || { bad "[61] 赖公拨砂未走人盘中针(退半山 +7.5°)"; S61_BAD=1; }
# 🔴 回落必须如实标注实际所用档(否则右栏渲染出「·undefined山中针」的假标签 —— 实测踩过)
grep -qE "const effVariant = boshaVariant === 'zuo' \? 'zuo' : 'shuangshan';" "${S61_FS}/sanhe.js" 2>/dev/null || { bad "[61] 赖公档缺坐山未如实回落标注(会出 undefined 山假标签)"; S61_BAD=1; }
grep -qE "note: '三合以四大局起长生：左旋顺起论水" "${S61_FS}/sanhe.js" 2>/dev/null || { bad "[61] 三合格龙缺龙水两向告诫"; S61_BAD=1; }
# 八宅法脉三档：坐山起伏位(缺省) / 门上起伏位 / 三元阳宅
grep -qE "faMai = 'zuoshan'" "${S61_FS}/bazhai.js" 2>/dev/null || { bad "[61] 八宅法脉缺省档非坐山起伏位(零回归风险)"; S61_BAD=1; }
grep -qE "faMai === 'menshang'" "${S61_FS}/bazhai.js" 2>/dev/null || { bad "[61] 八宅缺门上起伏位档"; S61_BAD=1; }
grep -qE "\? '宅运兴时：纵游年落鬼绝，亦「逢兴鬼绝更昌隆」'" "${S61_FS}/bazhai.js" 2>/dev/null || { bad "[61] 八宅三元阳宅缺兴替反转口径"; S61_BAD=1; }
grep -qE "if \(lunMing !== false && ming && ming\.year\)" "${S61_FS}/bazhai.js" 2>/dev/null || { bad "[61] 八宅缺「只论宅不论命」开关"; S61_BAD=1; }
# 玄空收山出煞：只作形势理气合参之独立结论，**绝不改 ge 的本判**(古籍两说并陈)
grep -qE "opts\.shousha && typeof opts\.shousha === 'object'" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] 玄空缺收山出煞层"; S61_BAD=1; }
grep -qE "\['shan', 'gao', 'shui', 'kong'\]\.indexOf\(env\) < 0" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] 收山出煞未白名单 env(杂值会凭空造「全违」凶断)"; S61_BAD=1; }
grep -qE "note: '古籍另说：能收山出煞者虽上山下水亦吉" "${S61_FS}/xuankong.js" 2>/dev/null || { bad "[61] 收山出煞缺两说并陈之说明"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/liqiDeepening.test.js" ] || { bad "[61] 缺理气深化测试"; S61_BAD=1; }
# ── 三合十三水法全表 + 金锁玉关断诀全库──────────────
[ -f "${S61_FS}/fengshuiSanheShuifa.js" ] || { bad "[61] 缺三合十三水法 fengshuiSanheShuifa.js"; S61_BAD=1; }
# 🔴 十三条是结构键(阶+水流)驱动的模板；火局渲染须与传本逐字相同 → 条数与关键用语钉死。
S61_SF13="$(grep -c "no: [0-9]" "${S61_FS}/fengshuiSanheShuifa.js" 2>/dev/null || echo 0)"
[ "${S61_SF13}" = "13" ] || { bad "[61] 十三水法模板不是 13 条(实为 ${S61_SF13})"; S61_BAD=1; }
for k in 三合联珠 禄存流尽佩金鱼 杀人大黄泉 颜回夭寿水 短命寡宿水 旺去冲生 生来破旺; do
  grep -q "${k}" "${FS_SF13:-${S61_FS}/fengshuiSanheShuifa.js}" 2>/dev/null || { bad "[61] 十三水法缺「${k}」"; S61_BAD=1; }
done
# 🔴 帝旺按水流方向二分（第12出煞 / 第13生来破旺）—— 合并即错判
grep -qE "stage: '帝旺', flow: 'rightToLeft'" "${S61_FS}/fengshuiSanheShuifa.js" 2>/dev/null || { bad "[61] 十三水法帝旺未按水流二分(右倒左·出煞)"; S61_BAD=1; }
grep -qE "stage: '帝旺', flow: 'leftToRight'" "${S61_FS}/fengshuiSanheShuifa.js" 2>/dev/null || { bad "[61] 十三水法帝旺未按水流二分(左倒右·生来破旺)"; S61_BAD=1; }
# 🔴 向法限制必须随表标出（传本只载正旺向一路，他向法不臆造）
grep -qE "SHUIFA_13_XIANGFA_NOTE = '本表为「向＝帝旺（正旺向一路）」" "${S61_FS}/fengshuiSanheShuifa.js" 2>/dev/null || { bad "[61] 十三水法缺向法限制标注(会被误读为通用表)"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/sanheShuifa13.test.js" ] || { bad "[61] 缺十三水法 golden"; S61_BAD=1; }
# 金锁断诀全库：24 山 ×{水,砂}＝48 条 + 宫全 + 跨宫 + 形态
[ -f "${S61_FS}/fengshuiJinsuoDuanjue.js" ] || { bad "[61] 缺金锁断诀库 fengshuiJinsuoDuanjue.js"; S61_BAD=1; }
for k in JINSUO_SHAN_DUAN JINSUO_GONG_QUAN JINSUO_KUA_GONG JINSUO_XING JINSUO_DUIGONG; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiJinsuoDuanjue.js" 2>/dev/null || { bad "[61] 缺金锁断诀数据 ${k}"; S61_BAD=1; }
done
S61_JS24="$(grep -cE "^\t(壬|子|癸|未|坤|申|甲|卯|乙|辰|巽|巳|戌|乾|亥|庚|酉|辛|丑|艮|寅|丙|午|丁): \{" "${S61_FS}/fengshuiJinsuoDuanjue.js" 2>/dev/null || echo 0)"
[ "${S61_JS24}" = "24" ] || { bad "[61] 金锁断诀不是 24 山(实为 ${S61_JS24})"; S61_BAD=1; }
# 🔴 每条对照条件都必须带机器可判的 req，否则只能读文本猜 → 静默失效
S61_ZHAO="$(grep -c "kind: 'zhao'" "${S61_FS}/fengshuiJinsuoDuanjue.js" 2>/dev/null || echo 0)"
S61_ZREQ="$(grep -c "kind: 'zhao', req:" "${S61_FS}/fengshuiJinsuoDuanjue.js" 2>/dev/null || echo 0)"
[ "${S61_ZHAO}" = "${S61_ZREQ}" ] || { bad "[61] 金锁对照条件有 $((S61_ZHAO-S61_ZREQ)) 条缺 req(必静默不命中)"; S61_BAD=1; }
# 🔴 24 山细式必须 additive：不给 shans 时零回归；且八方档遗留 flat 不得吞掉细式（死开关闸）
grep -qE "const hasShan = !!shans" "${S61_FS}/jinsuo.js" 2>/dev/null || { bad "[61] 金锁 24 山细式未 opt-in(八方档零回归风险)"; S61_BAD=1; }
grep -qE "if \(!nonFlat\.length\) \{ out\[gua\] = \(sectors && sectors\[gua\]\) \|\| 'flat'; return; \}" "${S61_FS}/jinsuo.js" 2>/dev/null || { bad "[61] 金锁细式被八方档 flat 吞掉(死开关)"; S61_BAD=1; }
# 🔴 「全是砂/都是水」须三山录满才算（不足而断＝造假阳）
grep -qE "if \(vals\.every\(\(v\)=>v === want\)\) \{ return true; \}" "${S61_FS}/jinsuo.js" 2>/dev/null || { bad "[61] 金锁宫全判定未要求三山录满(会造假阳)"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/jinsuoDuanjue.test.js" ] || { bad "[61] 缺金锁断诀 golden"; S61_BAD=1; }
# ── 玄空大卦深化（二元八运/四数/两卦相见四档/五种交通/些子法）────────
[ -f "${S61_FS}/fengshuiDaguaDeepData.js" ] || { bad "[61] 缺大卦深化数据 fengshuiDaguaDeepData.js"; S61_BAD=1; }
for k in ERYUAN_8YUN XINGYUN_MAP HOUTIAN_WEI XIANGJIAN_4 QIXING_DAJIE_28 JIAOTONG_5; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiDaguaDeepData.js" 2>/dev/null || { bad "[61] 缺大卦深化数据 ${k}"; S61_BAD=1; }
done
# 🔴 二元八运八运齐（无五运），起讫年逐运钉死
# 一行内多条，须按「匹配数」而非「行数」计（grep -c 数的是行 —— 此处踩过一次）；
# 且正则**只用 ASCII**：多字节字符类在 preflight 的 shell/locale 下匹配为 0，会假报缺失（亦踩过）。
S61_EY="$(grep -oE "yun: [0-9], from: [0-9]{4} \}" "${S61_FS}/fengshuiDaguaDeepData.js" 2>/dev/null | wc -l | tr -d ' ')"
[ "${S61_EY}" = "8" ] || { bad "[61] 二元八运不是 8 运(实为 ${S61_EY})"; S61_BAD=1; }
grep -qE "\{ gua: '坤', yun: 1, from: 1864 \}" "${S61_FS}/fengshuiDaguaDeepData.js" 2>/dev/null || { bad "[61] 二元八运起运非坤1运1864"; S61_BAD=1; }
grep -qE "\{ gua: '乾', yun: 9, from: 2017 \}" "${S61_FS}/fengshuiDaguaDeepData.js" 2>/dev/null || { bad "[61] 二元八运末运非乾9运2017"; S61_BAD=1; }
grep -qE "yang \* 9 \+ yin \* 6" "${S61_FS}/fengshuiDaguaDeepData.js" 2>/dev/null || { bad "[61] 二元八运缺「阳爻9年阴爻6年」年数推法"; S61_BAD=1; }
# 🔴 星运生成规则：父卦一运 / 母卦九运 / 江东八七六 / 江西二三四（缺一即八运计数破）
for y in "1, '父卦'" "9, '母卦'" "\[0, 8, '初'\]" "\[1, 7, '二'\]" "\[2, 6, '三'\]" "\[0, 2, '初'\]" "\[1, 3, '二'\]" "\[2, 4, '三'\]"; do
  grep -qE "${y}" "${S61_FS}/fengshuiDaguaDeepData.js" 2>/dev/null || { bad "[61] 大卦星运生成规则缺 ${y}"; S61_BAD=1; }
done
# 🔴 两卦相见四档 + 阴阳相乘；纯阳纯阴集合不可写反
grep -qE "WEI_YANG = new Set\(\[6, 1, 8, 3\]\)" "${S61_FS}/fengshuiDaguaDeepData.js" 2>/dev/null || { bad "[61] 后天卦位纯阳集有误(应为6/1/8/3)"; S61_BAD=1; }
grep -qE "WEI_YIN = new Set\(\[4, 9, 2, 7\]\)" "${S61_FS}/fengshuiDaguaDeepData.js" 2>/dev/null || { bad "[61] 后天卦位纯阴集有误(应为4/9/2/7)"; S61_BAD=1; }
grep -qE "pairs: \[\[6, 2\], \[3, 4\], \[9, 1\], \[8, 7\]\]" "${S61_FS}/fengshuiDaguaDeepData.js" 2>/dev/null || { bad "[61] 夫妇正配四对有误"; S61_BAD=1; }
# 🔴「合相通」传本未给判据 → 必须据实标注，不得自造规则
grep -qE "HEXIANGTONG_UNDEFINED = '传本列「合相通」" "${S61_FS}/fengshuiDaguaDeepData.js" 2>/dev/null || { bad "[61] 合相通未据实标为未给判据(自造规则风险)"; S61_BAD=1; }
# 🔴 些子法：深化层 opt-in（不开时 deep 为 null，逐字段零回归）+ 爻序差异据实标注
grep -qE "if \(showDeep\) \{" "${S61_FS}/dagua.js" 2>/dev/null || { bad "[61] 大卦深化层未 opt-in(零回归风险)"; S61_BAD=1; }
grep -qE "yaoXuNote: '爻序约定：本器「抽第 n 爻」" "${S61_FS}/dagua.js" 2>/dev/null || { bad "[61] 些子法缺爻序称法差异之据实标注"; S61_BAD=1; }
grep -qE "罗盘内容不可尽信" "${S61_FS}/dagua.js" 2>/dev/null || { bad "[61] 些子法缺「罗盘不可尽信」告诫"; S61_BAD=1; }
for t in daguaDeep.test.js daguaXiezi.test.js; do
  [ -f "${S61_FS}/__tests__/${t}" ] || { bad "[61] 缺大卦深化测试 ${t}"; S61_BAD=1; }
done
# ── 改造化煞新派（形煞二十 / 气煞二十三 / 补偏救弊五法 / 化解用品三十）────
for f in huasha.js fengshuiHuashaData.js liqi/huashaSchool.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺化煞 ${f}"; S61_BAD=1; }
done
for k in BUPIAN_5 XINGSHA_20 QISHA_RIKE QISHA_LIQI LINGXING_SHA HUAJIE_WUPIN QISHA_TRIGGER; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiHuashaData.js" 2>/dev/null || { bad "[61] 缺化煞数据 ${k}"; S61_BAD=1; }
done
# 条数按「匹配数」计（一行内可能多条；grep -c 数行会假绿），且正则只用 ASCII（多字节字符类在本 shell/locale 下恒 0）
S61_XS="$(grep -oE "^\t\{ key: '[a-z]+', name: '" "${S61_FS}/fengshuiHuashaData.js" 2>/dev/null | wc -l | tr -d ' ')"
[ "${S61_XS}" -ge "20" ] 2>/dev/null || { bad "[61] 形煞条目不足 20(实为 ${S61_XS})"; S61_BAD=1; }
# 🔴 动静闸：气煞所临之方安静无动象一般不出灾 —— 缺此闸即把静方也报成灾
S61_HSG="$(grep -oE "\['dong', 'eshan'\]\.indexOf" "${S61_FS}/huasha.js" 2>/dev/null | wc -l | tr -d ' ')"
[ "${S61_HSG}" = "2" ] || { bad "[61] 化煞「动象/恶山恶水」发灾闸不足两处(日课+理气各一;实为 ${S61_HSG})"; S61_BAD=1; }
# 🔴 传本未给判据者只在用户登记宫位时才判，绝不自造规则
grep -qE "传本未给表|传本未载" "${S61_FS}/fengshuiHuashaData.js" 2>/dev/null || { bad "[61] 力士/戊己都天/暗建煞未据实标为传本未给判据"; S61_BAD=1; }
grep -qE "needsInput: '力士所临之宫'" "${S61_FS}/fengshuiHuashaData.js" 2>/dev/null || { bad "[61] 力士未走用户登记(自造规则风险)"; S61_BAD=1; }
# 🔴 阴神满地按相异阴星计（同一颗星重复不作两颗 —— 真机误报过）
grep -qE "new Set\(stars\.filter\(\(n\)=>YIN_STARS\.indexOf\(n\) >= 0\)\)\.size >= 2" "${S61_FS}/huasha.js" 2>/dev/null || { bad "[61] 阴神满地未按相异阴星计(同星重复会误报)"; S61_BAD=1; }
# 🔴 259 合局煞：传本标题与释义不一致，判据取释义正文并存疑标注
grep -qE "combo: \[2, 5, 9\]" "${S61_FS}/fengshuiHuashaData.js" 2>/dev/null || { bad "[61] 259 合局煞判据未取释义正文 2/5/9"; S61_BAD=1; }
grep -qE "conflict: '此条传本标题作「257 合局煞」" "${S61_FS}/fengshuiHuashaData.js" 2>/dev/null || { bad "[61] 259 合局煞缺标题/释义不一致之存疑标注"; S61_BAD=1; }
# 🔴 同名异实两存：形煞穿心煞 与 气煞穿心煞
grep -qE "name: '穿心煞（形煞）'" "${S61_FS}/fengshuiHuashaData.js" 2>/dev/null || { bad "[61] 形煞穿心煞未标注区分"; S61_BAD=1; }
grep -qE "name: '穿心煞（气煞）'" "${S61_FS}/fengshuiHuashaData.js" 2>/dev/null || { bad "[61] 气煞穿心煞未标注区分"; S61_BAD=1; }
# 新派五处齐动
grep -qE "^\thuasha: huashaSchool,$" "${S61_FS}/liqi/registry.js" 2>/dev/null || { bad "[61] 化煞未进 registry"; S61_BAD=1; }
grep -qE "'daxuankong', 'shuilong', 'huasha'" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] 化煞未进 LIQI_SCHOOLS"; S61_BAD=1; }
grep -qE "huasha: '改造化煞'" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] SCHOOL_CN 缺化煞"; S61_BAD=1; }
grep -qE "'风水·水龙平洋', '风水·改造化煞'," "${S61_AIX}" 2>/dev/null || { bad "[61] aiExport 缺风水·改造化煞段"; S61_BAD=1; }
grep -qE "AI_EXPORT_V54_SECTION_UNION[^A-Za-z0-9_]" "${S61_AIX}" 2>/dev/null || { bad "[61] aiExport 缺 v54 union 迁移"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/huasha.test.js" ] || { bad "[61] 缺化煞 golden"; S61_BAD=1; }
# ── 阳宅判断新派（峦头断/理气断内外局/客星断含飞太岁/选宅五原则/室内凶局）────
for f in zhaiduan.js fengshuiZhaiduanData.js liqi/zhaiduanSchool.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺宅断 ${f}"; S61_BAD=1; }
done
for k in WAI_LIUSHI_YAO ZHAI_XING_8 XIONGGE_10 WAI_JU_6 NEI_JU_5 NEIWAI_4 DUAN_3 XUANZHAI_5 BIKAI_CHANGSUO_10 NEIJU_XINGXING_10 NEIJU_LIQI_2 KEXING_JUE; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiZhaiduanData.js" 2>/dev/null || { bad "[61] 缺宅断数据 ${k}"; S61_BAD=1; }
done
# 🔴 飞太岁：以流年地支所对之宫为数、取该数在流年紫白盘所飞之宫（三算例 2013→巽/2014→坎/2015→巽 为 golden）
grep -qE "export function feiTaiSui" "${S61_FS}/zhaiduan.js" 2>/dev/null || { bad "[61] 缺飞太岁求法"; S61_BAD=1; }
grep -qE "if \(pan\[g\] === num\)" "${S61_FS}/zhaiduan.js" 2>/dev/null || { bad "[61] 飞太岁未按「该数所飞之宫」取(算法被改)"; S61_BAD=1; }
# 🔴 峤星回风返气强化的是**对宫**之气（宫与对宫弄反即整条判反）
grep -qE "const there = at\(OPP\[qg\]\);" "${S61_FS}/zhaiduan.js" 2>/dev/null || { bad "[61] 峤星未取对宫向星(回风返气判反)"; S61_BAD=1; }
# 🔴 形气为主、客星为用 —— 客星段恒带此告诫
grep -qE "KEXING_ZHUCI = '形、气为主，客星为用" "${S61_FS}/fengshuiZhaiduanData.js" 2>/dev/null || { bad "[61] 客星断缺「形气为主客星为用」告诫"; S61_BAD=1; }
grep -qE "zhuCi: KEXING_ZHUCI," "${S61_FS}/zhaiduan.js" 2>/dev/null || { bad "[61] 客星段未随判带出该告诫"; S61_BAD=1; }
# 🔴 线位合法原则须明写以磁子午线为准（用真子午线立向是明确的错法）
grep -qE "而非真子午线" "${S61_FS}/fengshuiZhaiduanData.js" 2>/dev/null || { bad "[61] 选宅线位原则缺「磁子午线而非真子午线」"; S61_BAD=1; }
# 室内凶局原子项须够细（宅形不利十 + 理气不合二，合计 ≥40 项）
S61_ZDA="$(grep -oE "atoms: \[" "${S61_FS}/fengshuiZhaiduanData.js" 2>/dev/null | wc -l | tr -d ' ')"
[ "${S61_ZDA}" = "12" ] || { bad "[61] 室内凶局条目不是 12 条(宅形10+理气2;实为 ${S61_ZDA})"; S61_BAD=1; }
# 新派五处齐动
grep -qE "^\tzhaiduan: zhaiduanSchool,$" "${S61_FS}/liqi/registry.js" 2>/dev/null || { bad "[61] 宅断未进 registry"; S61_BAD=1; }
grep -qE "'daxuankong', 'shuilong', 'huasha', 'zhaiduan'" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] 宅断未进 LIQI_SCHOOLS"; S61_BAD=1; }
grep -qE "zhaiduan: '阳宅判断'" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] SCHOOL_CN 缺宅断"; S61_BAD=1; }
grep -qE "'风水·改造化煞', '风水·阳宅判断'," "${S61_AIX}" 2>/dev/null || { bad "[61] aiExport 缺风水·阳宅判断段"; S61_BAD=1; }
grep -qE "AI_EXPORT_V55_SECTION_UNION[^A-Za-z0-9_]" "${S61_AIX}" 2>/dev/null || { bad "[61] aiExport 缺 v55 union 迁移"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/zhaiduan.test.js" ] || { bad "[61] 缺宅断 golden"; S61_BAD=1; }
# ── 择日深化（用事十四事/紫白法全套/三步选课/斗首法）· 全 additive ────
for f in zeriDeep.js fengshuiZeriDeepData.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺择日深化 ${f}"; S61_BAD=1; }
done
for k in YONGSHI_JIANZAO_8 YONGSHI_SANGZANG_6 ZIBAI_JUE_4 ZIBAI_COMBO ZIBAI_SHIJIAN ZIBAI_KONGJIAN YONGSHI_GONG_4 HUASHA_XUANXING SANBU_2_GANZHI SANBU_3_GOUTONG DOUSHOU_SHAN_WUXING DOUSHOU_GAN_HUAQI DOUSHOU_LIUQIN; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiZeriDeepData.js" 2>/dev/null || { bad "[61] 缺择日深化数据 ${k}"; S61_BAD=1; }
done
# 🔴 择日深化必须 opt-in：不开 showDeep 时 zaoMing 输出逐字段零回归
grep -qE "deep: showDeep \? zeriDeep\(\{" "${S61_FS}/zeri.js" 2>/dev/null || { bad "[61] 择日深化未 opt-in(造命缺省路零回归风险)"; S61_BAD=1; }
# 🔴 阳宅动土 / 阴宅破土 不可混淆（此告诫是用事分类之要害）
grep -qE "阳宅开工为「动土」、阴宅开工为「破土」，两者不能混淆" "${S61_FS}/fengshuiZeriDeepData.js" 2>/dev/null || { bad "[61] 用事缺「动土/破土不可混淆」告诫"; S61_BAD=1; }
# 🔴 75/57 只有五运可组合（漏此闸会把五运的可用组合一律判凶）
grep -qE "wuYunOnly: \['75', '57'\]" "${S61_FS}/fengshuiZeriDeepData.js" 2>/dev/null || { bad "[61] 紫白缺「75/57 只五运可组合」之闸"; S61_BAD=1; }
grep -qE "Number\(yun\) === 5" "${S61_FS}/zeriDeep.js" 2>/dev/null || { bad "[61] 紫白组合未按运判 75/57"; S61_BAD=1; }
# 🔴 传本未列之组合据实标「不臆断」
grep -qE "传本未列此组，不臆断" "${S61_FS}/zeriDeep.js" 2>/dev/null || { bad "[61] 紫白未列组合未据实标注(会被硬判)"; S61_BAD=1; }
# 🔴 两说并陈（《宗镜》vs《诹吉述正》）不判孰是
grep -qE "两说并陈，本页不判孰是" "${S61_FS}/fengshuiZeriDeepData.js" 2>/dev/null || { bad "[61] 紫白两说未并陈标注"; S61_BAD=1; }
# 🔴 斗首三套五行口诀逐条在册；六亲关系不可错位
for j in "壬子巽巳辛戌土" "甲己化土乙庚金" "亥壬子癸大江水"; do
  grep -q "${j}" "${S61_FS}/fengshuiZeriDeepData.js" 2>/dev/null || { bad "[61] 斗首缺口诀「${j}」"; S61_BAD=1; }
done
grep -qE "rel: '比和', want: '当令为吉'" "${S61_FS}/fengshuiZeriDeepData.js" 2>/dev/null || { bad "[61] 斗首元辰关系有误(应为比和)"; S61_BAD=1; }
grep -qE "if \(WX_KE\[my\] === other\) \{ return 'wucai'; \}" "${S61_FS}/zeriDeep.js" 2>/dev/null || { bad "[61] 斗首武财关系有误(应为我克)"; S61_BAD=1; }
# 半三合/半三会须有中神方计
grep -qE "got\.indexOf\(SANHE_MID\[k\]\) >= 0" "${S61_FS}/zeriDeep.js" 2>/dev/null || { bad "[61] 干支检测半三合未要求有中神"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/zeriDeep.test.js" ] || { bad "[61] 缺择日深化 golden"; S61_BAD=1; }
# ── （终局）：流派立场对照制度化 ────────────────────────────────────
#   这张表不是文案而是**制度**：登记「谁与谁分歧、分歧在哪、本模块怎么落地」，
#   并由 golden 把「表里登记的」与「代码里实际做到的」逐条对拍（防止表说并陈、代码却合并了）。
[ -f "${S61_FS}/fengshuiStanceData.js" ] || { bad "[61] 缺流派立场对照表 fengshuiStanceData.js"; S61_BAD=1; }
for k in STANCE_ROWS STANCE_LAWS STANCE_NOTE; do
  grep -qE "export const ${k}" "${S61_FS}/fengshuiStanceData.js" 2>/dev/null || { bad "[61] 立场表缺 ${k}"; S61_BAD=1; }
done
S61_STN="$(grep -oE "^\t\tkey: '[A-Za-z0-9]+'," "${S61_FS}/fengshuiStanceData.js" 2>/dev/null | wc -l | tr -d ' ')"
[ "${S61_STN}" -ge "13" ] 2>/dev/null || { bad "[61] 立场表条目不足 13(实为 ${S61_STN})"; S61_BAD=1; }
# 🔴 四条铁律逐条在册（少一条即制度被架空）
grep -qE "^\t'只述分歧，不判对错" "${S61_FS}/fengshuiStanceData.js" 2>/dev/null || { bad "[61] 立场表缺「只述分歧不判对错」铁律"; S61_BAD=1; }
grep -qE "^\t'既有实现零改" "${S61_FS}/fengshuiStanceData.js" 2>/dev/null || { bad "[61] 立场表缺「既有实现零改」铁律"; S61_BAD=1; }
grep -qE "^\t'传本未给判据者不自造规则" "${S61_FS}/fengshuiStanceData.js" 2>/dev/null || { bad "[61] 立场表缺「不自造规则」铁律"; S61_BAD=1; }
# 🔴 立场表须进帮助页（只放在代码里等于没对用户说）
grep -qE "\{STANCE_ROWS\.map\(\(r\)=>kv\(" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/help/FengshuiHelpDoc.js" 2>/dev/null || { bad "[61] 立场对照表未进帮助页"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/fengshuiStance.test.js" ] || { bad "[61] 缺立场表与实现对拍 golden"; S61_BAD=1; }
# ── 罗盘升级（三盘式/新层/磁偏角358城/分金择优/立向判向向导）────────
for f in fengshuiLuopanData.js fengshuiDeclinationData.js luopanTools.js; do
  [ -f "${S61_FS}/${f}" ] || { bad "[61] 缺罗盘升级 ${f}"; S61_BAD=1; }
done
# 🔴 三元盘（蒋盘）明载无人盘中针/天盘缝针廿四山、无七十二龙/一百二十龙/六十龙分金
grep -qE "not: \['renpan', 'tianpan', 'chuanshan', 'toudi', 'fenjin'" "${S61_FS}/fengshuiLuopanData.js" 2>/dev/null || { bad "[61] 三元盘层集未排除三针余两针与三龙分金"; S61_BAD=1; }
# 🔴 盘式过滤须真作用到中栏（只换标题＝假切档）
grep -qE "layers=\{result\.effLayers\}" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] 罗盘中栏未吃盘式过滤后的层集(切盘式只换标题)"; S61_BAD=1; }
grep -qE "effLayers: \(\(\)=>\{" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] 缺盘式层集过滤 effLayers"; S61_BAD=1; }
# 🔴 磁偏角符号：本表西偏为正，WMM/IGRF 东偏为正须取负（弄反则整盘反向偏）
grep -qE "source === 'wmm' \? -d : d" "${S61_FS}/fengshuiDeclinationData.js" 2>/dev/null || { bad "[61] 磁偏角换源未取负(WMM 东偏为正，符号相反)"; S61_BAD=1; }
grep -qE "DECLINATION_EPOCH = '2013-06'" "${S61_FS}/fengshuiDeclinationData.js" 2>/dev/null || { bad "[61] 磁偏角未标数据时点"; S61_BAD=1; }
S61_DEC="$(grep -oE "\['[^']+', -?[0-9]+\.[0-9]+\]" "${S61_FS}/fengshuiDeclinationData.js" 2>/dev/null | wc -l | tr -d ' ')"
[ "${S61_DEC}" = "358" ] || { bad "[61] 磁偏角城市数不是 358(实为 ${S61_DEC})"; S61_BAD=1; }
# 🔴 分金择优：可用纳甲丙丁庚辛；起点从本册「甲子始于子方」自算，不复用线法层(壬山初)之干支
grep -qE "FENJIN_USABLE_GAN = \['丙', '丁', '庚', '辛'\]" "${S61_FS}/luopanTools.js" 2>/dev/null || { bad "[61] 分金可用纳甲有误(应为丙丁庚辛)"; S61_BAD=1; }
grep -qE "CHUANSHAN_ORIGIN = 352\.5" "${S61_FS}/luopanTools.js" 2>/dev/null || { bad "[61] 穿山择优起点未按本册(壬子交界 352.5°)"; S61_BAD=1; }
grep -qE "export const SHAN_FENJIN_ZHI" "${S61_FS}/luopanTools.js" 2>/dev/null || { bad "[61] 缺分金山→支映射(48 线位自洽之据)"; S61_BAD=1; }
# 🔴 SHAN_ORDER 自壬起、壬在 345°：索引/中心度基准弄错会整环偏一山（本轮踩过两次）
grep -qE "norm360\(d - 345 \+ 7\.5\) / 15" "${S61_FS}/luopanTools.js" 2>/dev/null || { bad "[61] degToShan 索引基准未减 345(整体偏一山)"; S61_BAD=1; }
grep -qE "norm360\(345 \+ idx \* 15\)" "${S61_FS}/fengshuiLuopanData.js" 2>/dev/null || { bad "[61] 节气环中心度基准未加 345(整环偏一山)"; S61_BAD=1; }
# 🔴 书未给表者不臆造：天星逐山星名、地母翻卦逐山配星
grep -qE "逐山星名须按所宗罗盘自校" "${S61_FS}/fengshuiLuopanData.js" 2>/dev/null || { bad "[61] 廿四天星逐山星名未标「须按所宗盘」(臆造风险)"; S61_BAD=1; }
grep -qE "不臆造映射" "${S61_FS}/fengshuiLuopanData.js" 2>/dev/null || { bad "[61] 地母翻卦逐山配星未标不臆造"; S61_BAD=1; }
# 🔴 钢混结构绝不能室内打盘（安全性告诫）
grep -qE "绝对不能在室内打盘" "${S61_FS}/fengshuiLuopanData.js" 2>/dev/null || { bad "[61] 缺「钢混结构绝不能室内打盘」之诫"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/luopanTools.test.js" ] || { bad "[61] 缺罗盘升级 golden"; S61_BAD=1; }
# ── 玄空断语库（两赋全文 79 条）+ 阳宅三十则 ──────────────────────
[ -f "${S61_FS}/fengshuiDuanyuData.js" ] || { bad "[61] 缺断语库 fengshuiDuanyuData.js"; S61_BAD=1; }
S61_DY="$(grep -oE "^\tI src: '" "${S61_FS}/fengshuiDuanyuData.js" 2>/dev/null | wc -l | tr -d ' ')"
S61_DY="$(grep -oE "src: '(玄机赋|玄空秘旨)', no: " "${S61_FS}/fengshuiDuanyuData.js" 2>/dev/null | wc -l | tr -d ' ')"
[ "${S61_DY}" = "79" ] || { bad "[61] 玄空断语不是 79 条(实为 ${S61_DY})"; S61_BAD=1; }
S61_YZ="$(grep -oE "^\t\{ no: [0-9]+, title: '" "${S61_FS}/fengshuiDuanyuData.js" 2>/dev/null | wc -l | tr -d ' ')"
[ "${S61_YZ}" = "30" ] || { bad "[61] 阳宅三十则不是 30 条(实为 ${S61_YZ})"; S61_BAD=1; }
# 🔴《飞星赋》本册未收全文 → 不得混入他处版本
grep -qE "\+ '本册只述其名而未收全文，故本库不含《飞星赋》" "${S61_FS}/fengshuiDuanyuData.js" 2>/dev/null || { bad "[61] 未据实说明《飞星赋》未收全文"; S61_BAD=1; }
if grep -qE "src: '飞星赋'" "${S61_FS}/fengshuiDuanyuData.js" 2>/dev/null; then bad "[61] 断语库混入《飞星赋》(本册未收全文)"; S61_BAD=1; fi
# 🔴 三处防假阳性之限（首版全踩过）：单字辅不认星、卦名须紧邻方位词、空邻字不得恒真
grep -qE "单字「辅」多为「辅佐」之义" "${S61_FS}/fengshuiDuanyuData.js" 2>/dev/null || { bad "[61] 断语索引未记「单字辅不认星」之限"; S61_BAD=1; }
grep -qE "「离乡砂」之「离」" "${S61_FS}/fengshuiDuanyuData.js" 2>/dev/null || { bad "[61] 断语索引未记卦名须紧邻方位词之限"; S61_BAD=1; }
grep -qE "Array\.isArray\(stars\) \? stars : \[\]" "${S61_FS}/fengshuiDuanyuData.js" 2>/dev/null || { bad "[61] 断语检索入参未归一(非数组会抛)"; S61_BAD=1; }
# 🔴 阳宅三十则原书编号有讹，须记录原印之号与自证依据
grep -qE "ocrNum: '1122'" "${S61_FS}/fengshuiDuanyuData.js" 2>/dev/null || { bad "[61] 阳宅三十则未保留原印讹号(自证依据丢失)"; S61_BAD=1; }
grep -qE "条数恰三十与篇名相符" "${S61_FS}/fengshuiDuanyuData.js" 2>/dev/null || { bad "[61] 阳宅三十则编号法缺自证说明"; S61_BAD=1; }
# 接线：玄空右栏按盘检索、宅断右栏三十则
grep -qE "duanyuByPan\(result\.palaces\)" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] 玄空右栏未按盘检索断语"; S61_BAD=1; }
grep -qE "YANGZHAI_30\.map" "${S61_FS}/liqi/zhaiduanSchool.js" 2>/dev/null || { bad "[61] 宅断右栏未列阳宅三十则"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/fengshuiDuanyu.test.js" ] || { bad "[61] 缺断语库 golden"; S61_BAD=1; }
# ── 室内凶局 · 几何自动检测（户型图 → 建议，不代人下判）──────────────
[ -f "${S61_FS}/neijuGeometry.js" ] || { bad "[61] 缺几何检测 neijuGeometry.js"; S61_BAD=1; }
[ -f "${S61_FS}/__tests__/neijuGeometry.test.js" ] || { bad "[61] 缺几何检测 golden"; S61_BAD=1; }
# 🔴 三层诚实防线（缺一即退化成「机器说没有＝真没有」）
grep -qE "「未检出」不等于「无此凶局」" "${S61_FS}/neijuGeometry.js" 2>/dev/null || { bad "[61] 几何检测缺「未检出≠无此凶局」之明示"; S61_BAD=1; }
grep -qE "不覆盖人工勾选" "${S61_FS}/neijuGeometry.js" 2>/dev/null || { bad "[61] 几何检测未声明只作建议(不覆盖人工勾选)"; S61_BAD=1; }
grep -qE "skipped\.push\(\{ name, missing: what \}\)" "${S61_FS}/neijuGeometry.js" 2>/dev/null || { bad "[61] 几何检测缺「未判之项须写明缺什么」之落地"; S61_BAD=1; }
# 🔴 方位绝不在检测侧自铺：必须走宿主传入的 gongAt（唯一真值源 = 画布 getSectorForPoint，含盘面旋转）
grep -qE "typeof gongAt === 'function'" "${S61_FS}/neijuGeometry.js" 2>/dev/null || { bad "[61] 几何检测缺角未走 gongAt(自铺九宫必与画布错位)"; S61_BAD=1; }
if grep -qE "\[\[4, ?9, ?2\]|\[\[6, ?1, ?8\]" "${S61_FS}/neijuGeometry.js" 2>/dev/null; then bad "[61] 🔴 几何检测里写死了九宫方位表(画布可任意旋转,必错宫)"; S61_BAD=1; fi
grep -qE "buildNeijuGeoInput\(\)" "${S61_FS}/fengshuiEngine.js" 2>/dev/null || { bad "[61] 画布引擎缺 buildNeijuGeoInput 供给口"; S61_BAD=1; }
# 🔴 中宫可达性：SECTORS 只有外八方，供给口不补中宫则「卫生间在中宫」是死判据（真机才看得出）
grep -qE "inCenterPalace\(pt\)" "${S61_FS}/fengshuiEngine.js" 2>/dev/null || { bad "[61] 缺 inCenterPalace(中宫判据将永不命中)"; S61_BAD=1; }
grep -qE "if \(this\.inCenterPalace\(pt\)\) \{ return 5; \}" "${S61_FS}/fengshuiEngine.js" 2>/dev/null || { bad "[61] geo 供给口未接中宫(卫生间在中宫成死开关)"; S61_BAD=1; }
grep -qE "rotatePoint\(pt, center, -this\.rect\.rotation\)" "${S61_FS}/fengshuiEngine.js" 2>/dev/null || { bad "[61] 中宫未按房屋框本地坐标算(框一转即错)"; S61_BAD=1; }
# 🔴 机器建议绝不并入 neiXiong、绝不计入 neiBad（并入即「机器代人下判」）
grep -qE "绝不并入 neiXiong、绝不计入 neiBad、绝不动总断" "${S61_FS}/zhaiduan.js" 2>/dev/null || { bad "[61] zhaiduan 未声明几何建议不入判词"; S61_BAD=1; }
if grep -qE "nx\[[^]]*\] *= *\(?nx\[|Object\.keys\(d\.suggested\)\.forEach" "${S61_FS}/zhaiduan.js" 2>/dev/null; then bad "[61] 🔴 zhaiduan 把几何建议并进了人工勾选(机器代人下判)"; S61_BAD=1; fi
# 接线：右栏出建议+凭据+采纳按钮；类名必须真有 CSS 定义
grep -qE "r\.geoScan \? card\(" "${S61_FS}/liqi/zhaiduanSchool.js" 2>/dev/null || { bad "[61] 宅断右栏未出几何检测卡"; S61_BAD=1; }
grep -qE "horosa-fengshui-liqi-adopt" "${S61_FS}/liqi/zhaiduanSchool.js" 2>/dev/null || { bad "[61] 缺「采纳此条」控件"; S61_BAD=1; }
grep -qE "^\.horosa-fengshui-liqi-adopt \{" "$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.less")" 2>/dev/null || { bad "[61] 采纳控件类名无 CSS 定义(裸文本)"; S61_BAD=1; }
grep -qE "impl\.Panel result=\{result\} ui=\{\{ card, row \}\} p=\{regP\} patch=\{regPatch\}" "${S61_FS}/LiqiWorkspace.js" 2>/dev/null || { bad "[61] 右栏未拿到 p/patch(采纳按钮成死按钮)"; S61_BAD=1; }
grep -qE "geo=\{this\.engine \? this\.engine\.buildNeijuGeoInput\(\) : null\}" "${S61_FS}/FengShuiMain.js" 2>/dev/null || { bad "[61] FengShuiMain 未把画布几何传给理气工作区"; S61_BAD=1; }
# 🔴 AI 快照必须把「待核」与已确认分行并标未经人工确认，否则报告会当成已定之事
grep -qE "未经人工确认，不可作已定之事" "${S61_FS}/liqi/zhaiduanSchool.js" 2>/dev/null || { bad "[61] AI 快照未标机器建议为待核(会被写成已定之事)"; S61_BAD=1; }
# 🔴 保密：立场表与本轮新增诸数据文件里不得出现现代书名/作者/册次/页码之痕迹
for f in fengshuiStanceData.js fengshuiHuashaData.js fengshuiZhaiduanData.js fengshuiZeriDeepData.js fengshuiJinsuoDuanjue.js fengshuiSanheShuifa.js fengshuiDaguaDeepData.js neijuGeometry.js; do
  if grep -qE "第[0-9]+页|和谐家居|居住时空|编著|主编" "${S61_FS}/${f}" 2>/dev/null; then bad "[61] ${f} 出现来源痕迹(书名/册次/页码)"; S61_BAD=1; fi
done
[ "${S61_BAD}" = "0" ] && ok "[61] 风水 二十项 引擎+玄空进阶(替卦/城门/真假打劫)+深化(黄泉/拨砂/线法/九水位/门主灶/日时紫白)+新派(辅星/净阴净阳/大卦/形势/择日/六法/命理/罗经/大玄空/水龙)+registry机制+形势九纲+理气深化(赖公拨砂/格龙/法脉三档/三元阳宅/收山出煞/十三水法全表/金锁断诀48条)+大卦深化(二元八运/四数/相见四档/五交通/些子法)+改造化煞(形煞20/气煞23/补偏救弊5/用品30)+阳宅判断(峦头/内外局/客星飞太岁/选宅五原则/室内凶局)+择日深化(用事14事/紫白全套/三步选课/斗首法)+流派立场对照制度化+罗盘升级(三盘式/磁偏角358城/分金择优/立向判向向导)+玄空断语库79条+阳宅三十则+室内凶局几何自动检测(只出建议/方位走gongAt/未判如实列缺)+罗盘13层三针+圆图落卦+形体图库+造命四纲+应期+盘面+golden+户型图两法零回归 在位" || bad "[61] 风水 有缺失"
}

seg_97() {
# ── [97] 七政天星择日双轮(Moira 对照)链完整性 ──────────────────────────────
echo "[97] 七政择日双轮链"
S97_BAD=0
S97_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S97_PY="${REPO_ROOT}/Horosa-Web/astropy"
for S97_F in \
  "${S97_UI}/components/guolao/electionGeomag.js" \
  "${S97_UI}/components/guolao/electionCore.js" \
  "${S97_UI}/components/guolao/moiraWheelLayout.js" \
  "${S97_UI}/components/guolao/guolaoMoiraTables.js" \
  "${S97_UI}/components/guolao/guolaoStarNotes.js" \
  "${S97_UI}/components/guolao/GuoLaoElectionTable.js" \
  "${S97_UI}/components/guolao/GuoLaoWheelCaptions.js" \
  "${S97_UI}/components/common/QuickDockBar.js" \
  "${S97_PY}/websrv/webqizhengelectionsrv.py"; do
  [ -f "${S97_F}" ] || { bad "[97] 缺文件: ${S97_F#"${REPO_ROOT}"/}"; S97_BAD=1; }
done
# WMM 系数完整性:两套历元且每套 90 行系数(截断即红)
S97_WMM_EPOCHS=$(grep -c 'epoch: 20' "${S97_UI}/components/guolao/electionGeomag.js" 2>/dev/null || true)
[ "${S97_WMM_EPOCHS}" -ge 2 ] || { bad "[97] WMM 历元数 ${S97_WMM_EPOCHS} < 2"; S97_BAD=1; }
S97_WMM_ROWS=$(grep -cE '^\s*\[(1[0-2]|[1-9]), ' "${S97_UI}/components/guolao/electionGeomag.js" 2>/dev/null || true)
[ "${S97_WMM_ROWS}" -ge 180 ] || { bad "[97] WMM 系数行 ${S97_WMM_ROWS} < 180(截断?)"; S97_BAD=1; }
# 端点挂载在位
grep -q "qizhengelection" "${S97_PY}/websrv/webchartsrv.py" || { bad "[97] webchartsrv 未挂载 /qizhengelection"; S97_BAD=1; }
# 快捷栏契约测试在位(信息不进栏/禁复现守卫)
[ -f "${S97_UI}/components/common/__tests__/quickDockContract.test.js" ] || { bad "[97] 缺 quickDockContract 契约测试"; S97_BAD=1; }
[ "${S97_BAD}" = "0" ] && ok "[97] 择日双轮链完整(WMM ${S97_WMM_EPOCHS} 历元/${S97_WMM_ROWS} 行系数)"
}

seg_186() {
# ── [186] 奇门择日(zeri 子技法)全链完整性 ──
# 择日页「奇门择日」= scope 化复用 DunJiaMain + 纯本地找局引擎。本哨兵锁四类静默退化:
# ①资产在位+新测试零 skip ②条件注册表一键一行契约(Tab 缩进抓键,塌缩判红)+格局清单加性导出
#   (zeri 侧零手抄的根,机械同源 jest 含注错自证) ③对偶锁:SubTabRegistry⇔ZeriMain TabPane
#   (缺一=切走切回被打回首档)、aiExport preset 追加三段⇔快照 builder 三段头(逐字成对)
# ④DunJiaMain scope 化回归锚(硬编码 qimen 槽回潮=keep-alive 双实例竞写复发)+aiExport
#   「择日」子串启发式次序锚(奇门择日<天星择日<裸择日,乱序=zeri 页导出串成辅盘择日盘)。
S186_BAD=0
echo "== [186] 奇门择日全链完整性 =="
S186_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S186_REG="${S186_UI}/src/divination/zeri/qimenConditionTypes.js"
S186_T1="${S186_UI}/src/divination/zeri/__tests__/qimenConditionTypes.test.js"
S186_T2="${S186_UI}/src/divination/zeri/__tests__/qimenScanEngine.test.js"
S186_T3="${S186_UI}/src/divination/zeri/__tests__/qimenZeriFourLedger.test.js"
S186_T5="${S186_UI}/src/components/dunjia/__tests__/dunjiaMainScopeContract.test.js"
for f in \
	"${S186_REG}" \
	"${S186_UI}/src/divination/zeri/qimenScanEngine.js" \
	"${S186_UI}/src/divination/zeri/qimenZeriSnapshot.js" \
	"${S186_UI}/src/components/zeri/QimenZeriMain.js" \
	"${S186_UI}/src/components/zeri/QimenZeriWorkbench.js" \
	"${S186_UI}/src/components/zeri/QimenMiniBoardPopup.js" \
	"${S186_UI}/src/components/help/ZeriHelpDoc.js" \
	"${S186_T1}" "${S186_T2}" "${S186_T3}" "${S186_T5}"; do
	[ -f "${f}" ] || { bad "[186] 🔴 奇门择日资产缺失: ${f#${REPO_ROOT}/}"; S186_BAD=1; }
done
for f in "${S186_T1}" "${S186_T2}" "${S186_T3}" "${S186_T5}"; do
	pf_test_disabled "${f}" && { bad "[186] 🔴 奇门择日测试被 skip / only 旁路: $(basename "${f}")"; S186_BAD=1; }
done
grep -aq "注错自证" "${S186_T1}" 2>/dev/null || { bad "[186] 🔴 格局机械同源哨兵缺注错自证(T1 可能已死)"; S186_BAD=1; }
S186_NKEYS=$(grep -acE $'^\t[a-z_]+: \{' "${S186_REG}" 2>/dev/null || true)
[ "${S186_NKEYS}" -ge 19 ] || { bad "[186] 🔴 奇门条件注册表键抓取塌缩(现 ${S186_NKEYS},需≥19;一键一行 Tab 缩进契约被破?)"; S186_BAD=1; }
grep -aq "^export const QIMEN_JI_PATTERN_NAMES" "${S186_UI}/src/components/dunjia/DunJiaBaGongRules.js" 2>/dev/null || { bad "[186] 🔴 吉格清单加性导出缺失(DunJiaBaGongRules)"; S186_BAD=1; }
grep -aq "^export const QIMEN_XIONG_PATTERN_NAMES" "${S186_UI}/src/components/dunjia/DunJiaBaGongRules.js" 2>/dev/null || { bad "[186] 🔴 凶格清单加性导出缺失(DunJiaBaGongRules)"; S186_BAD=1; }
grep -aq "'qimenzeri'" "${S186_UI}/src/constants/SubTabRegistry.js" 2>/dev/null || { bad "[186] 🔴 ZERI_SUBTABS 缺 qimenzeri(切走切回被打回首档)"; S186_BAD=1; }
grep -aq 'key="qimenzeri"' "${S186_UI}/src/components/zeri/ZeriMain.js" 2>/dev/null || { bad "[186] 🔴 ZeriMain 缺 qimenzeri TabPane"; S186_BAD=1; }
grep -aq "AI_EXPORT_PRESET_SECTIONS.qimenzeri = \[\.\.\.AI_EXPORT_PRESET_SECTIONS.qimen, '择日搜索配置', '择日条件', '命中时辰'\]" "$(pf_src_set "${S186_UI}/src/utils/aiExport.js")" 2>/dev/null || { bad "[186] 🔴 qimenzeri preset 段表缺失或改形(须=qimen 全段+择日三段)"; S186_BAD=1; }
for s in '\[择日搜索配置\]' '\[择日条件\]' '\[命中时辰\]'; do
	grep -aq "${s}" "${S186_UI}/src/divination/zeri/qimenZeriSnapshot.js" 2>/dev/null || { bad "[186] 🔴 奇门择日快照缺段头 ${s}"; S186_BAD=1; }
done
S186_L1=$(grep -an "topInfo.includes('奇门择日')" "$(pf_src_set "${S186_UI}/src/utils/aiExport.js")" 2>/dev/null | head -1 | cut -d: -f1)
S186_L2=$(grep -an "topInfo.includes('天星择日')" "$(pf_src_set "${S186_UI}/src/utils/aiExport.js")" 2>/dev/null | head -1 | cut -d: -f1)
S186_L3=$(grep -an "topInfo.includes('择日')" "$(pf_src_set "${S186_UI}/src/utils/aiExport.js")" 2>/dev/null | head -1 | cut -d: -f1)
{ [ -n "${S186_L1}" ] && [ -n "${S186_L2}" ] && [ -n "${S186_L3}" ] && [ "${S186_L1}" -lt "${S186_L2}" ] && [ "${S186_L2}" -lt "${S186_L3}" ]; } || { bad "[186] 🔴 aiExport 择日子串启发式次序被破(奇门择日=${S186_L1:-缺} 天星=${S186_L2:-缺} 裸择日=${S186_L3:-缺};乱序=zeri 页导出串盘)"; S186_BAD=1; }
grep -aq "case 'zeri':" "$(pf_src_set "${S186_UI}/src/utils/aiExport.js")" 2>/dev/null || { bad "[186] 🔴 resolveContextByAstroState 缺 zeri 分流(store 兜底根治缺位)"; S186_BAD=1; }
grep -aq "this.scope = props.techniqueScope || 'qimen';" "${S186_UI}/src/components/dunjia/DunJiaMain.js" 2>/dev/null || { bad "[186] 🔴 DunJiaMain techniqueScope 默认锚缺失"; S186_BAD=1; }
S186_HARD=$(grep -ac "saveModuleAISnapshot('qimen'" "${S186_UI}/src/components/dunjia/DunJiaMain.js" 2>/dev/null || true)
[ "${S186_HARD}" = "0" ] || { bad "[186] 🔴 DunJiaMain 出现硬编码 qimen 快照槽(${S186_HARD} 处;scope 化被回潮=双实例竞写复发)"; S186_BAD=1; }
grep -aq "horosa-zeri-host .horosa-dunjia-redesign" "$(pf_src_set "${S186_UI}/src/layouts/app.less")" 2>/dev/null || { bad "[186] 🔴 zeri 页 dunjia dock 行样式条缺失(底部 64px 空带回归)"; S186_BAD=1; }
# 通用扫描外壳「同四柱直算」铁律字面哨兵:红字注释被删 = 有人可能引 memo 优化
grep -q "不做「按四柱/时辰 memo 求值」" "${S186_UI}/src/divination/zeri/hourlyScanEngine.js" 2>/dev/null \
  || { bad "[186] 🔴 通用扫描外壳「同四柱直算」铁律注释被删(memo 优化回潮风险)"; S186_BAD=1; }
# 择日完备性闸装置在位(能算出来的都可搜索):登记表 + 哨兵缺任一 = 「主技法新增快照段 → 择日强制表态」制度失守。
[ -s "${S186_UI}/src/divination/zeri/zeriCoverageMap.js" ] \
  || { bad "[186] 🔴 择日完备性登记表 zeriCoverageMap.js 缺失"; S186_BAD=1; }
[ -s "${S186_UI}/src/divination/zeri/__tests__/zeriCoverageMap.test.js" ] \
  || { bad "[186] 🔴 完备性闸哨兵 zeriCoverageMap.test.js 缺失"; S186_BAD=1; }
[ "${S186_BAD}" = "0" ] && ok "[186] 奇门择日全链(资产11+注册表${S186_NKEYS}键+格局同源导出+对偶锁+scope回归锚+启发式次序锚+完备性闸)在位"
}

seg_303() {
echo "[${PF_NO}] 六爻间爻按世应位置取(世应中间两爻,不再写死三、四爻)"
S303_BAD=0
S303_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S303_CONST="${S303_UI}/components/gua/LiuYaoConst.js"
S303_FACADE="${S303_UI}/components/gua/liuyaoFacade.js"
# ① 单源:间爻爻位只由 jianYaoPositions(世, 应) 给出;门面按世应取,不得再写死三、四爻
grep -qF 'export function jianYaoPositions(shi, ying){' "${S303_CONST}" 2>/dev/null \
  && [ "$(grep -cF 'jianYaoPositions(shiPos, yingPos)' "${S303_FACADE}" 2>/dev/null)" = "1" ] \
  && [ "$(grep -cE 'jianYao[[:space:]]*=[[:space:]]*\[[[:space:]]*3[[:space:]]*,[[:space:]]*4[[:space:]]*\]' "${S303_FACADE}" 2>/dev/null)" = "0" ] || { bad "[${PF_NO}] 🔴 六爻间爻又写死三、四爻(64 卦中 48 卦会把世爻或应爻本身算进间爻)"; S303_BAD=1; }
# ② 概览卡片与 AI 快照同源:两处都按世应位置出「世某应某之间」
grep -qF 'jianYaoSpanText(pt.shi, pt.ying)' "${S303_UI}/components/guazhan/LiuYaoBoard.js" 2>/dev/null \
  && grep -qF 'jianYaoSpanText(pt.shi, pt.ying)' "${S303_UI}/components/guazhan/liuyaoSnapshotEx.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 间爻的概览卡片 / AI 快照未走同一取位函数"; S303_BAD=1; }
# ③ 帮助文档不再写「三四间爻」,装卦结构卡有「间爻」一条
[ "$(grep -cF '三四间爻' "${S303_UI}/components/help/GuazhanHelpDoc.js" 2>/dev/null)" = "0" ] \
  && grep -qF "{kv('间爻'," "${S303_UI}/components/help/GuazhanHelpDoc.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 六爻帮助文档的间爻口径回退"; S303_BAD=1; }
# ④ 测试在位(全 64 卦逐一核:间爻恰在世应之间、从不含世应本身)
grep -qF '全 64 卦:间爻恰为世应之间两爻' "${S303_UI}/components/guazhan/__tests__/liuyaoJianYao.test.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 缺六爻间爻测试"; S303_BAD=1; }
[ "${S303_BAD}" = "0" ] && ok "[${PF_NO}] 六爻间爻:按世应位置单源取位 / 概览卡片与 AI 快照同源 / 帮助文档 / 测试在位"
}

seg_211() {
# ── [211] 天文地占:改设置/改时地必须实时重排,且重排绝不换卦 ────────────────
# 病症一:改设置或换地点后盘面纹丝不动,非得再点一次「起盘」—— 而再点起盘就是重新揲卦,
#   手上那一卦当场就没了。根因:时地接入计算之后,无人在时地变化时重新请求判读。
# 病症二:用报数起卦的盘,切一次流派就被重新揲一次(母图全变,等于换了一卦)——
#   重排时只带种子、不带那十六个数,计算端遂改由随机数重揲。八种起卦法逐一实测,唯此档失败;
#   时间档另有隐患:它只认时间种子,钉成普通种子即退化成真随机。
# 病症三:「据所选时地起真实上升」「真实星历落星」两档从未生效 —— 界面送出的是度分记法的经纬
#   (如 119e19),计算端按十进制度解读:'26n04' 解不出;'119e19' 更隐蔽,会被当成科学记数法的
#   合法浮点(1.19e21),过了数值转换却卡在经度范围检查上,于是整体静默回落成「无真实盘」。
# 判据两层:jest/pytest 立行为判据 + 此处钉住关键接线与判据文件不被摘掉。
echo "[211] 天文地占实时重排 + 重排不换卦"
S211_SRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/geomancy/GeomancyMain.js"
S211_T="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/geomancy/__tests__/geomancyLiveRecast.test.js"
S211_PY="${REPO_ROOT}/Horosa-Web/astropy/websrv/webgeomancysrv.py"
S211_PT="${REPO_ROOT}/Horosa-Web/astropy/tests/test_geomancy_kernel.py"
S211_BAD=0
[ -s "${S211_SRC}" ] || { bad "[211] 🔴 GeomancyMain.js 缺失"; S211_BAD=1; }
[ -s "${S211_T}" ]   || { bad "[211] 🔴 判据文件 geomancyLiveRecast.test.js 缺失(行为判据没了=无人看守)"; S211_BAD=1; }
if [ -s "${S211_SRC}" ]; then
  # ① 时地判据须取「真正送进请求体的值」,而非 fields 引用 —— 按引用判会因无关状态更新白打后端
  grep -qF 'castParamSig(){' "${S211_SRC}" \
    || { bad "[211] 🔴 castParamSig 缺失 —— 时地变化判据回落引用比较"; S211_BAD=1; }
  # ② 载入存档那一拍不得重排(否则存档盘被覆盖),且签名照样同步(否则下一拍误触发)
  grep -qF 'if(changed && !restored && !this._suppressRecast){ this.scheduleRecastPinned(); }' "${S211_SRC}" \
    || { bad "[211] 🔴 didUpdate 的「变了才算 + 载档不算」守卫被改动"; S211_BAD=1; }
  # ③ 载档抑制窗口:状态更新是异步的,清本地时地草稿要到下一拍才生效,届时「刚载过档」的标志
  #    已复位而签名已变 —— 无此窗口则刚载入的存档盘会被重排覆盖。
  grep -qF 'this._suppressRecast = true;' "${S211_SRC}" \
    || { bad "[211] 🔴 载档抑制窗口缺失 —— 存档盘会在下一拍被重排覆盖"; S211_BAD=1; }
  # ④ 重排须回带该盘自己的起卦源(报数十六数),否则报数盘一改设置就被重新揲卦
  grep -qF "fzMethod === 'numbers' && Array.isArray(fz.cast_numbers)" "${S211_SRC}" \
    || { bad "[211] 🔴 重排未回带十六数 —— 报数盘改设置即被重新揲卦"; S211_BAD=1; }
  # ⑤ 时间档只认时间种子
  grep -qF "if(fzMethod === 'time'){ payload.castMethod = 'time'; payload.timeSeed = pinned; }" "${S211_SRC}" \
    || { bad "[211] 🔴 时间档未走 timeSeed —— 钉成普通种子即退化真随机"; S211_BAD=1; }
  # ⑥ 会改判读的左栏控件须全汇到同一入口(曾散着四份各自钉种子的重复实现)
  S211_N="$(grep -c 'this.recastPinned()' "${S211_SRC}" || true)"
  [ "${S211_N:-0}" -ge 7 ] \
    || { bad "[211] 🔴 recastPinned 调用点仅 ${S211_N} 处(应 ≥7:流派/传本/行星盘/问类/所问宫/转宫/问题+时地)"; S211_BAD=1; }
fi
# ⑦-⑨ 服务层时地解析:经纬是度分记法、时区是偏移串,直接数值转换会让两档成为死开关
if [ -s "${S211_PY}" ]; then
  grep -qF 'lon = _parse_geo(data.get("lon"))' "${S211_PY}" \
    || { bad "[211] 🔴 地占服务未走 _parse_geo —— 真实上升/真实星历落星回落成死开关"; S211_BAD=1; }
  grep -qF 'zone = _parse_zone(data.get("zone"))' "${S211_PY}" \
    || { bad "[211] 🔴 地占服务未按偏移串解析时区 —— 非东八区的真实盘时刻整体偏"; S211_BAD=1; }
  grep -qF 'from websrv.horosa_engine_common import coord_to_float' "${S211_PY}" \
    || { bad "[211] 🔴 未复用既有 coord_to_float(度分解析口径会分叉)"; S211_BAD=1; }
else
  bad "[211] 🔴 webgeomancysrv.py 缺失"; S211_BAD=1
fi
# ⑩ 判据文件里的关键断言不得被摘:每条都对应上述三项修复中的一个具体失效形态
if [ -s "${S211_T}" ]; then
  for S211_A in \
    '报数盘:重算必带回那十六个数' \
    '时间档只认 timeSeed' \
    '载档那一拍不许重算' \
    '时地无关的重渲染'
  do
    grep -qF "${S211_A}" "${S211_T}" \
      || { bad "[211] 🔴 判据文件缺关键断言:${S211_A}"; S211_BAD=1; }
  done
fi
grep -qF 'def test_time_place_reaches_real_chart_with_frontend_payload' "${S211_PT}" 2>/dev/null \
  || { bad "[211] 🔴 pytest 缺「按界面原样请求体须起得出真实盘」判据"; S211_BAD=1; }
grep -qF 'def test_real_chart_switch_off_means_time_place_never_matters' "${S211_PT}" 2>/dev/null \
  || { bad "[211] 🔴 pytest 缺零回归判据(未选真实盘档时喂不喂时地必恒等)"; S211_BAD=1; }
if [ -s "${S211_PY}" ]; then
  grep -qF 'from websrv.horosa_engine_common import coord_to_float' "${S211_PY}" \
    || { bad "[211] 🔴 未复用 websrv 层既有 coord_to_float(度分解析口径会分叉)"; S211_BAD=1; }
  grep -qF 'zone = _parse_zone(data.get("zone"))' "${S211_PY}" \
    || { bad "[211] 🔴 地占服务未按偏移串解析时区 —— 非东八区的真实盘时刻整体偏"; S211_BAD=1; }
  grep -qF 'def _parse_geo(v):' "${S211_PY}" || { bad "[211] 🔴 _parse_geo 缺失"; S211_BAD=1; }
else
  bad "[211] 🔴 webgeomancysrv.py 缺失"; S211_BAD=1
fi
[ "${S211_BAD}" = "0" ] && ok "[211] 时地/设置改动即重排 + 八档起卦源原样回带 + 载档不被覆盖"
}
