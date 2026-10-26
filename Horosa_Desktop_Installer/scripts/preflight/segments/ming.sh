#!/usr/bin/env bash
# 发布前自检 · 命(各技法与历法)
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。段号用 ${PF_NO}(登记表第二列)。

seg_11() {
echo "[11] 西占推运 + 宫制修复哨兵(v2.5.0)"
PERCHART="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py")"
ASTROCONST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/constants/AstroConst.js"
PERSIAN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroPersianDirected.js"
BALB="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/balbillus.js"
# A. 宫制数量前后端同步(后端 hsys[] vs 前端 HOUSE_SYSTEM_OPTIONS):改一处必改另一处,否则 index 错位读错宫制
if [ -f "${PERCHART}" ] && [ -f "${ASTROCONST}" ]; then
  HSYS_BE="$(python3 -c "import re;t=open('${PERCHART}').read();m=re.search(r'hsys=\[(.*?)\]',t,re.S);print(len([x for x in m.group(1).split(',') if x.strip()]) if m else -1)" 2>/dev/null || echo -2)"
  HSYS_FE="$(python3 -c "import re;t=open('${ASTROCONST}').read();m=re.search(r'HOUSE_SYSTEM_OPTIONS = \[(.*?)\];',t,re.S);print(len(re.findall(r'value:',m.group(1))) if m else -1)" 2>/dev/null || echo -3)"
  if [ "${HSYS_BE}" = "${HSYS_FE}" ] && [ "${HSYS_BE}" -gt 0 ] 2>/dev/null; then
    ok "A 宫制数量前后端同步(${HSYS_BE})"
  else
    bad "A 宫制数量不同步:后端 hsys[]=${HSYS_BE} vs 前端 HOUSE_SYSTEM_OPTIONS=${HSYS_FE} —— index 错位会读错宫制"
  fi
else
  warn "perchart.py / AstroConst.js 不存在,跳过宫制同步哨兵"
fi
# B. 福点整宫制:自定义整宫制宫头必须 house.hsys=const.HOUSES_WHOLE_SIGN,否则 flatlib inHouse 加 -5° 偏移致落宫差一宫
if [ -f "${PERCHART}" ] && grep -q "custHouse_Fortuna_Whole" "${PERCHART}"; then
  if grep -q "house.hsys = const.HOUSES_WHOLE_SIGN" "${PERCHART}" && ! grep -q "house.hsys = custHouse_Fortuna_Whole" "${PERCHART}"; then
    ok "B 福点整宫制宫头走 HOUSES_WHOLE_SIGN(inHouse 无 -5° 偏移)"
  else
    bad "B 福点整宫制宫头未设 const.HOUSES_WHOLE_SIGN(或回退自定义标记) —— inHouse -5° 偏移致落宫 off-by-one"
  fi
fi
# C. 双圈盘内圈本命冻结修复:AstroPersianDirected.requestData 每次从 props.value 重算 natalParams
if [ -f "${PERSIAN}" ]; then
  grep -q "natalParams(this.props.value)" "${PERSIAN}" \
    && ok "C 波斯向运 requestData 重算 natalParams(内圈本命不冻结)" \
    || bad "C AstroPersianDirected 未从 props.value 重算 natalParams —— 换盘后内圈本命会冻结成旧盘"
fi
# D. Balbillus 旺距削减公式 N×(1−d/360) + 七星小年表(独立引擎,勿退回 k 标度实验版)
if [ -f "${BALB}" ]; then
  grep -q "1 - d / 360" "${BALB}" && grep -q "BALBILLUS_YEARS" "${BALB}" \
    && ok "D Balbillus 旺距削减公式在位" \
    || bad "D balbillus.js 缺 N×(1−d/360) 削减公式 或 BALBILLUS_YEARS"
fi
}

seg_13() {
echo "[13] 时区/夏令时(DST)自动校正哨兵(v2.5.0)"
UI_SRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
UI_PKG="${REPO_ROOT}/Horosa-Web/astrostudyui/package.json"
TZUTIL="${UI_SRC}/utils/timezone.js"
DSTIND="${UI_SRC}/components/comp/DstZoneIndicator.js"
if [ -f "${UI_PKG}" ]; then
  grep -q '"tz-lookup"' "${UI_PKG}" \
    && ok "A package.json 含 tz-lookup 依赖(经纬度→IANA 时区,离线)" \
    || bad "A package.json 缺 tz-lookup —— DST 自动校正无法离线求时区"
fi
if [ -f "${TZUTIL}" ]; then
  grep -q "applyDstToFields" "${TZUTIL}" && grep -q "dstAwareZoneAt" "${TZUTIL}" && grep -q "longOffset" "${TZUTIL}" \
    && ok "B timezone.js 在位(applyDstToFields + dstAwareZoneAt + Intl longOffset)" \
    || bad "B timezone.js 缺 applyDstToFields/dstAwareZoneAt/longOffset —— DST 引擎不完整"
else
  bad "B timezone.js 不存在 —— DST 自动校正引擎缺失"
fi
[ -f "${DSTIND}" ] \
  && ok "C DstZoneIndicator.js 共享指示器组件在位" \
  || bad "C DstZoneIndicator.js 不存在 —— 三表单 DST 指示器缺失"
dst_forms_ok=1
for f in "components/comp/ChartFormData.js" "components/user/ChartData.js" "components/user/CaseData.js"; do
  fp="${UI_SRC}/${f}"
  if [ -f "${fp}" ]; then
    grep -q "applyDstToFields" "${fp}" && grep -q "DstZoneIndicator" "${fp}" && grep -q "zoneManual" "${fp}" \
      || { bad "D ${f} 未接 DST(applyDstToFields/DstZoneIndicator/zoneManual) —— 该表单时区不自动校正"; dst_forms_ok=0; }
  else
    bad "D ${f} 不存在"; dst_forms_ok=0
  fi
done
[ "${dst_forms_ok}" -eq 1 ] && ok "D 三表单(ChartFormData/ChartData/CaseData)均接 DST 自动校正"

# 14-19. 启动机制稳健化哨兵(端口被占/后端未启动 根治,详见 docs/启动机制稳健化-端口与就绪.md)。
:  # 14-19 段共用的路径常量 UISRC / WARMJS 在 preflight/lib.sh 顶层定义(装载期就有,单跑 --only 不依赖本段)
}

seg_20() {
# 20. 紫微 运限(ZiWeiLuck)/格局(ZiWeiPattern) 深度增强完整性(v2.5.8)
echo "[20] 紫微 运限/格局深度增强"
ZW_HELPER_DIR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/helper"
ZW_MODEL_DIR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model"
ZW_FAT_JAR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
ZW_MAIN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/ZiWeiMain.js"
zw_src_ok=1
for f in "${ZW_MODEL_DIR}/ZiWeiLuck.java" "${ZW_MODEL_DIR}/ZiWeiPattern.java" "${ZW_HELPER_DIR}/ziweige.json" "${ZW_HELPER_DIR}/ziweiliuchangqu.json"; do
  [ -f "$f" ] || { bad "[20] 缺文件 $(basename "$f")"; zw_src_ok=0; }
done
[ "$zw_src_ok" -eq 1 ] && ok "[20] ZiWeiLuck/ZiWeiPattern + ziweige/ziweiliuchangqu 源齐全"
if grep -q "startidx - idx" "${ZW_HELPER_DIR}/ZiWeiHelper.java" 2>/dev/null; then ok "[20] getSmallDirectioinHouse 女命分支已修正(startidx - idx)"; else bad "[20] getSmallDirectioinHouse 女命分支疑似未修正(应为 startidx - idx)"; fi
if grep -q "ZWLuckPanel" "${ZW_MAIN}" 2>/dev/null && grep -q "ZWPatternPanel" "${ZW_MAIN}" 2>/dev/null; then ok "[20] ZiWeiMain 已挂 ZWLuckPanel/ZWPatternPanel"; else bad "[20] ZiWeiMain 未挂 运限/格局 TabPane"; fi
if [ -f "${ZW_FAT_JAR}" ] && command -v unzip >/dev/null 2>&1; then
  zw_cn="$(unzip -Z1 "${ZW_FAT_JAR}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${zw_cn}" ]; then
    zw_list="$(cd "$(mktemp -d "${PF_TMP}/zw_list.XXXXXX")" && unzip -oq "${ZW_FAT_JAR}" "${zw_cn}" 2>/dev/null && unzip -Z1 "${zw_cn}" 2>/dev/null)"
    if echo "${zw_list}" | pipe_has "ZiWeiLuck.class" && echo "${zw_list}" | pipe_has "ZiWeiPattern.class" && echo "${zw_list}" | pipe_has "ziweige.json" && echo "${zw_list}" | pipe_has "ziweiliuchangqu.json"; then
      ok "[20] fat jar 已含 ZiWeiLuck/ZiWeiPattern + ziweige/ziweiliuchangqu(gotcha #10)"
    else
      bad "[20] fat jar 缺紫微运限/格局类或数据 —— 需 astrostudycn install + astrostudyboot clean package"
    fi
  else
    warn "[20] fat jar 内未找到 astrostudycn dep jar,跳过内容校验"
  fi
else
  warn "[20] 未找到 fat jar 或无 unzip,跳过 jar 内容校验"
fi
}

seg_20b() {
# 本段自己取(与前段同值;段与段之间不靠函数体里赋的变量传值,--only 单跑也成立)
ZW_MODEL_DIR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model"
ZW_FAT_JAR="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
# 20b. 紫微 全面增强 P0–P2(杂曜显示/流派四化表/格局详情/天伤天使) 完整性
echo "[20b] 紫微 全面增强 P0–P2"
ZW_HOUSE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/ZWHouse.js"
ZW_CONST_JS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/constants/ZWConst.js"
ZW_CHART_JAVA="${ZW_MODEL_DIR}/ZiWeiChart.java"
ZW_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/__tests__/ziweiEnhance.test.js"
zw2_ok=1
grep -q "drawSihuaSmallStars" "${ZW_HOUSE}" 2>/dev/null || { bad "[20b] ZWHouse 缺 drawSihuaSmallStars(十二神角格)"; zw2_ok=0; }
grep -q "starsOthersGood" "${ZW_HOUSE}" 2>/dev/null || { bad "[20b] ZWHouse 主四化盘未补显杂曜(starsOthersGood)"; zw2_ok=0; }
{ grep -q "SiHuaTables" "${ZW_CONST_JS}" && grep -q "getActiveSiHuaGan" "${ZW_CONST_JS}"; } 2>/dev/null || { bad "[20b] ZWConst 缺多流派四化表(SiHuaTables/getActiveSiHuaGan)"; zw2_ok=0; }
grep -q "setupStarsTianShangShi" "${ZW_CHART_JAVA}" 2>/dev/null || { bad "[20b] ZiWeiChart 缺天伤天使安星"; zw2_ok=0; }
{ grep -q "inOpp" "${ZW_PATTERN_JAVA:-${ZW_MODEL_DIR}/ZiWeiPattern.java}" && grep -q "sandwichHua" "${ZW_MODEL_DIR}/ZiWeiPattern.java"; } 2>/dev/null || { bad "[20b] ZiWeiPattern 缺新 op inOpp/sandwichHua"; zw2_ok=0; }
[ -f "${ZW_TEST}" ] || { bad "[20b] 缺自检 ziweiEnhance.test.js"; zw2_ok=0; }
[ "$zw2_ok" -eq 1 ] && ok "[20b] 杂曜显示/流派四化表/天伤天使/新op/自检 源齐全"
if grep -q "school: 'beipai'" "${ZW_CONST_JS}" 2>/dev/null; then ok "[20b] 四化流派默认 beipai(=现状零回归)"; else bad "[20b] 四化流派默认非 beipai —— 恐改动存量盘四化(回归风险)"; fi
if [ -f "${ZW_FAT_JAR}" ] && command -v unzip >/dev/null 2>&1; then
  zw2_cn="$(unzip -Z1 "${ZW_FAT_JAR}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${zw2_cn}" ]; then
    zw2_dir="$(mktemp -d "${PF_TMP}/zw2_dir.XXXXXX")"; ( cd "${zw2_dir}" && unzip -oq "${ZW_FAT_JAR}" "${zw2_cn}" 2>/dev/null )
    if unzip -p "${zw2_dir}/${zw2_cn}" spacex/astrostudycn/model/ZiWeiPattern.class 2>/dev/null | strings | pipe_has "inOpp"; then ok "[20b] fat jar ZiWeiPattern 含新 op(inOpp)"; else bad "[20b] fat jar 未含新 op —— 需 astrostudycn install + astrostudyboot clean package"; fi
    if unzip -p "${zw2_dir}/${zw2_cn}" spacex/astrostudycn/model/ZiWeiChart.class 2>/dev/null | pipe_has "setupStarsTianShangShi"; then ok "[20b] fat jar ZiWeiChart 含天伤天使"; else bad "[20b] fat jar 未含天伤天使 —— 需重编"; fi
  fi
fi
}

seg_25() {
# 本段自己取(与前段同值;段与段之间不靠函数体里赋的变量传值,--only 单跑也成立)
LR_AICTX="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js")"
# 25. 经纬度/时区 全半球转换 + 真太阳时/直接时间(用户验收追加)
echo "[25] 经纬度/时区转换 + timeAlg 哨兵"
ASTROHELPER_JS="${UISRC}/components/astro/AstroHelper.js"
GEO_TEST_JS="${UISRC}/components/astro/__tests__/AstroHelperGeo.test.js"
# 正向规范转换器:方向按【原始值符号】判(非 deg[0]>=0,否则 |值|<1 小负值如伦敦会判错向)
if grep -q "? 's' : 'n'" "${ASTROHELPER_JS}" 2>/dev/null && grep -q "? 'w' : 'e'" "${ASTROHELPER_JS}" 2>/dev/null; then ok "[25] convertLat/LonToStr 方向按原始值符号(修 (-1,0) 判向)"; else bad "[25] convertLat/LonToStr 方向疑似仍用 deg[0]>=0(小负值判向错)"; fi
# 反向解析:min/60(非 1.0/min)
if grep -q "min / 60" "${ASTROHELPER_JS}" 2>/dev/null; then ok "[25] convertLat/LonStrToDegree 用 min/60(修 1.0/min 致 gpsLat 偏)"; else bad "[25] 反向解析疑似仍 1.0/min(手输经纬度算出 gpsLat 偏、地图/时区偏)"; fi
# 6 手抄坐标转换无「分取负」畸形残留(西经/南纬 param error 源)
GEO_MANUAL_FILES="${UISRC}/components/user/ChartData.js ${UISRC}/components/user/CaseData.js ${UISRC}/components/comp/ChartFormData.js ${UISRC}/components/dice/DiceMain.js ${UISRC}/components/commtools/Azimuth.js ${UISRC}/components/astro/AstroDirectionForm.js"
geo_bad=""
for gf in ${GEO_MANUAL_FILES}; do grep -q "deg\[1\] = -" "$gf" 2>/dev/null && geo_bad="${geo_bad} $(basename "$gf")"; done
[ -z "${geo_bad}" ] && ok "[25] 6 手抄坐标转换无「分取负」畸形残留(西经/南纬不产 121w0-44)" || bad "[25] 仍有「分取负」畸形:${geo_bad}"
# 🔒 buildFieldObject 读 record.timeAlg(真太阳时=0/直接时间=1 不写死),否则八字快照对直接时间盘错用真太阳时校正
if grep -q "timeAlg: { value: (record.timeAlg" "${LR_AICTX}" 2>/dev/null; then ok "[25] 🔒 buildFieldObject 透传 record.timeAlg(直接时间盘不被强施真太阳时)"; else bad "[25] 🔒 buildFieldObject 疑似写死 timeAlg(canping/heluo 等对直接时间盘会错用真太阳时)"; fi
# 坐标转换自检测试存在
if [ -f "${GEO_TEST_JS}" ]; then ok "[25] AstroHelperGeo.test 全半球坐标自检在(回归门禁)"; else bad "[25] 缺 AstroHelperGeo.test"; fi
}

seg_29() {
# 29. 汉堡中点盘(双技法)哨兵 —— 字形/AI 同步/param error 护栏(2026-06-01 大改)。
echo "[29] 汉堡中点盘 双技法 + AI 段同步 + param error 护栏"
DIAL29_BAD=0
grep -q "AstroText.AstroMsg\[s.rep\]" "${UISRC}/components/germany/UranianDial.js" 2>/dev/null || { bad "[29] 折叠盘扇区字形未用 AstroMsg[名](会渲染成 emoji 彩块,须配 AstroChartFont)"; DIAL29_BAD=1; }
[ -f "${UISRC}/components/germany/UranianModulusDial.js" ] || { bad "[29] 缺 UranianModulusDial.js(多环模数盘技法丢失,用户要求两种盘并存)"; DIAL29_BAD=1; }
grep -q "'90°中点盘'" "$(pf_src_set "${UISRC}/utils/aiExport.js")" 2>/dev/null || { bad "[29] aiExport germany 预设缺 '90°中点盘' 段"; DIAL29_BAD=1; }
grep -q "\[90°中点盘\]" "${UISRC}/components/germany/AstroMidpoint.js" 2>/dev/null || { bad "[29] buildGermanySnapshotText 缺 [90°中点盘] 段(AI 挂载/导出/储存漏盘)"; DIAL29_BAD=1; }
grep -q "invalid_date" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py" 2>/dev/null || { bad "[29] webchartsrv 缺 NaN 日期护栏(invalid_date,param error 会复发)"; DIAL29_BAD=1; }
[ "${DIAL29_BAD}" = "0" ] && ok "[29] 中点盘双技法/字形 AstroMsg/AI 段同步/webchartsrv NaN 护栏 均在"
}

seg_32() {
# [32] 主限法方位+时间补全·铁律①守卫
#  - perpredict.py: _byZCoreKernel 函数指针仍在(纯公式 Alcabitius 主路径不被改名/重排)
#  - perpredict.py: CORE_PD_VIRTUAL_BODY_CORR_MODELS(ΔT 取数映射) + ΔT 注入 + 显示窗 + 宿命点闭式 在位
#  - perpredict.py: STATIC_TIME_KEY_SCALES['Ptolemy'] 严格 == 1.0(必须是数值字面量,不接受公式)
#  - perpredict.py: _PD_METHOD_REGISTRY 含 'core_alchabitius' 且默认 fallback 路径正确
#  - 540 case byte-perfect 测试存在并能跑通
echo "[32] 主限法方位+时间补全·铁律①守卫(Alcabitius+Ptolemy 字节级一致)"
PD32_BAD=0
PERPREDICT="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perpredict.py"
if [ -f "${PERPREDICT}" ]; then
  if ! grep -q "def getPrimaryDirectionByZCoreKernel" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 getPrimaryDirectionByZCoreKernel —— Alcabitius+Ptolemy 纯公式主路径被改名/移除(540 case 字节级将失效)"
    PD32_BAD=1
  fi
  if ! grep -q "CORE_PD_VIRTUAL_BODY_CORR_MODELS" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 CORE_PD_VIRTUAL_BODY_CORR_MODELS —— ΔT 校准批量取数映射表不在(_corePdDeltaTPointMap 依赖)"
    PD32_BAD=1
  fi
  if ! grep -q "_corePdDeltaTPointMap" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _corePdDeltaTPointMap —— 未来盘 ΔT 注入失效"
    PD32_BAD=1
  fi
  if ! grep -q "def _passesCoreDisplayWindow" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _passesCoreDisplayWindow —— 行星对显示窗(pre-norm 原值,|Δ|<107.5)被移除"
    PD32_BAD=1
  fi
  if ! grep -q "def _coreVertexArc" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _coreVertexArc —— 宿命点(Vertex)应星闭式被移除"
    PD32_BAD=1
  fi
  if ! grep -q "def _extendCorePdRecurrences" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _extendCorePdRecurrences —— 整圈复发/互补统一扩展被移除(180+ 互补与 3000 年多圈直达都走它)"
    PD32_BAD=1
  fi
  if ! grep -q "min(3000, int(round(float(data\['pdYears'\])))" "$(pf_src_set "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py")"; then
    bad "[32] perchart.py pdYears 上限不是 3000 —— 年数选择上限回退"
    PD32_BAD=1
  fi
  # 前端 pdYears clamp 必须四处全 3000(任一回落 360 → 选 3000 在该路径被截断,LIVE 实测真踩过):
  #   AstroPrimaryDirection.normalizePdYears(表格组件) / AstroDirectMain.normalizePdYears(主限tab容器·真fetch路径)
  #   / aiAnalysisContext.normalizePdYearsValue(AI挂载·buildFieldObject) / techniqueMountSettings pdYears max
  PD_CLAMP_360=$(grep -rIl "Math.min(360, n)" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js" "$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js")" 2>/dev/null | wc -l | tr -d ' ')
  PD_CLAMP_3000=$(grep -rl "Math.min(3000, n)" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/direction/AstroDirectMain.js" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroPrimaryDirection.js" 2>/dev/null | wc -l | tr -d ' ')
  if [ "${PD_CLAMP_360}" != "0" ] || [ "${PD_CLAMP_3000}" != "2" ]; then
    bad "[32] 前端 pdYears clamp 未全 3000(残留 Math.min(360,n)=${PD_CLAMP_360} 处 / 应为 0;3000 命中=${PD_CLAMP_3000} / 应为 2)—— LIVE 实测过:任一处回落会让 3000 年在该路径被截到 360"
    PD32_BAD=1
  fi
  if ! grep -q "Math.min(3000, n)" "$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js")"; then
    bad "[32] aiAnalysisContext.normalizePdYearsValue 上限不是 3000 —— AI 挂载路径会把 3000 截到 360"
    PD32_BAD=1
  fi
  # STATIC_TIME_KEY_SCALES['Ptolemy'] 必须严格 == 1.0 (数值字面量)
  if ! grep -qE "['\"]Ptolemy['\"]\s*:\s*1\.0" "${PERPREDICT}"; then
    bad "[32] STATIC_TIME_KEY_SCALES['Ptolemy'] 必须 == 1.0(数值字面量),不能写成公式或近似值;否则 Ptolemy 默认路径将失去字节级一致"
    PD32_BAD=1
  fi
  if ! grep -q "_PD_METHOD_REGISTRY" "${PERPREDICT}"; then
    bad "[32] perpredict.py 缺 _PD_METHOD_REGISTRY —— strategy 分发被回退(P0 方位法补全失效)"
    PD32_BAD=1
  fi
else
  bad "[32] 缺 perpredict.py"
  PD32_BAD=1
fi
# byte-perfect 测试存在
PD_BYTEPERFECT="${REPO_ROOT}/Horosa-Web/astropy/tests/test_pd_alcabitius_byteperfect.py"
# 金标语料现为 gzip 压缩(.ndjson.gz,test_pd_alcabitius_byteperfect.py 用 gzip.open 读);兼容旧未压缩名。
PD_GOLDEN_GZ="${REPO_ROOT}/Horosa-Web/astropy/tests/data/pd_calibration_corpus/golden_alcabitius_ptolemy_v266.ndjson.gz"
PD_GOLDEN_RAW="${REPO_ROOT}/Horosa-Web/astropy/tests/data/pd_calibration_corpus/golden_alcabitius_ptolemy_v266.ndjson"
if [ ! -f "${PD_BYTEPERFECT}" ]; then
  bad "[32] 缺 tests/test_pd_alcabitius_byteperfect.py —— byte-perfect 守卫缺失,540 case 回归无法跑"
  PD32_BAD=1
fi
if [ ! -f "${PD_GOLDEN_GZ}" ] && [ ! -f "${PD_GOLDEN_RAW}" ]; then
  bad "[32] 缺 tests/data/pd_calibration_corpus/golden_alcabitius_ptolemy_v266.ndjson(.gz) —— byte-perfect 基线缺失"
  PD32_BAD=1
fi
# 实跑 byte-perfect 子集 —— 「golden 与代码脱节(stale fixture)」事故的根因守卫。
# 仅做结构 grep 无法发现 golden 过期(v2.5.4 即因 golden 由中间态生成、从未与代码一致而带病发布,
# 且本门只查文件存在故未拦住);必须实跑确认 golden == 当前 Alcabitius+Ptolemy 输出。
# 默认前 12 case(~20s);HOROSA_PD_BYTEPERFECT_LIMIT 可调,HOROSA_PD_PREFLIGHT_SKIP_BP=1 跳过实跑。
if [ -f "${PD_BYTEPERFECT}" ] && [ "${HOROSA_PD_PREFLIGHT_SKIP_BP:-0}" != "1" ] && command -v python3 >/dev/null 2>&1; then
  PD_BP_LIMIT="${HOROSA_PD_BYTEPERFECT_LIMIT:-12}"
  PD_BP_OUT="$(cd "${REPO_ROOT}/Horosa-Web/astropy" 2>/dev/null && HOROSA_PD_BYTEPERFECT_LIMIT="${PD_BP_LIMIT}" PYTHONPATH="../flatlib-ctrad2:." python3 -m pytest tests/test_pd_alcabitius_byteperfect.py -q 2>&1)"
  if printf '%s\n' "${PD_BP_OUT}" | pipe_has -E "[0-9]+ passed"; then
    ok "[32] byte-perfect 实跑前 ${PD_BP_LIMIT} case 通过 —— golden 与当前代码字节级一致(防 stale fixture)"
  elif printf '%s\n' "${PD_BP_OUT}" | pipe_has -E "[0-9]+ failed|Error|Traceback"; then
    bad "[32] byte-perfect 实跑失败 —— Alcabitius+Ptolemy 与 golden 不一致(代码漂移或 golden 过期);末行:$(printf '%s\n' "${PD_BP_OUT}" | tail -1)"
    PD32_BAD=1
  else
    warn "[32] byte-perfect 实跑无法判定(python/依赖?),仅结构校验;末行:$(printf '%s\n' "${PD_BP_OUT}" | tail -1)"
  fi
fi
[ "${PD32_BAD}" = "0" ] && ok "[32] 铁律① Alcabitius+Ptolemy 字节级守卫 + byte-perfect 测试基线 + 子集实跑 均通过"
}

seg_34() {
# 本段自己取(与前段同值;段与段之间不靠函数体里赋的变量传值,--only 单跑也成立)
PERCHART="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py")"
# [34] 七政四余 二十八宿度·自有恒星案三制(回归今制活体距星 / 开禧+岁差 / 郑氏恒星基值)
#  - perchart.py: MOIRA_DISTAR_J2000 (28 距星) + _moira_distar_lon + _moira_ayanamsha 在
#  - perchart.py: setPlanetSu28 支持 byLon (黄道置宿)
#  - 回归今制不再直接用冻结 15.9 当今制(必经活体距星)
#  - 回归测试存在
echo "[34] 七政四余 二十八宿度·自有恒星案三制"
GUO34_BAD=0
if [ -f "${PERCHART}" ]; then
  grep -q "MOIRA_DISTAR_J2000" "${PERCHART}" || { bad "[34] perchart.py 缺 MOIRA_DISTAR_J2000(28 距星表)—— 回归今制活体距星失效"; GUO34_BAD=1; }
  grep -q "_moira_distar_lon" "${PERCHART}" || { bad "[34] perchart.py 缺 _moira_distar_lon(距星严格岁差投射)"; GUO34_BAD=1; }
  grep -q "_moira_ayanamsha" "${PERCHART}" || { bad "[34] perchart.py 缺 _moira_ayanamsha(开禧/恒星制基准)"; GUO34_BAD=1; }
  grep -q "byLon" "${PERCHART}" || { bad "[34] perchart.py setPlanetSu28 缺 byLon(自有恒星案三制须沿黄道置宿)"; GUO34_BAD=1; }
else
  bad "[34] 缺 perchart.py"; GUO34_BAD=1
fi
GUO_TEST="${REPO_ROOT}/Horosa-Web/astropy/tests/test_guolao_su28_moira.py"
[ -f "${GUO_TEST}" ] || { bad "[34] 缺 tests/test_guolao_su28_moira.py(七政四余宿度回归)"; GUO34_BAD=1; }
[ "${GUO34_BAD}" = "0" ] && ok "[34] 七政四余 28 距星表 + 严格岁差 + 黄道置宿 + 回归测试 均在"
}

seg_36() {
echo "[36] 城市搜索专业化(简体显示 + 拼音/首字母 + 繁简折叠;全技法经纬度共用 GeoCoordSelector)"
CITY_BAD=0
CM_JS="${UISRC}/components/amap/cityMatch.js"
CM_TEST="${UISRC}/components/amap/__tests__/cityMatch.test.js"
CITY_FULL="${UISRC}/data/citiesFull.json"
CITY_MAP="${UISRC}/data/cityTradSimpMap.json"
CITY_SEL="${UISRC}/components/amap/GeoCoordSelector.js"
[ -f "${CM_JS}" ] || { bad "[36] 缺 cityMatch.js(城市检索纯函数,简繁/拼音核心)"; CITY_BAD=1; }
[ -f "${CM_TEST}" ] || { bad "[36] 缺 cityMatch.test.js(城市检索自检)"; CITY_BAD=1; }
[ -f "${CITY_MAP}" ] || { bad "[36] 缺 cityTradSimpMap.json(繁→简折叠表;繁体查询会失效)"; CITY_BAD=1; }
{ [ -f "${CITY_SEL}" ] && grep -q "from './cityMatch'" "${CITY_SEL}"; } || { bad "[36] GeoCoordSelector 未委托 cityMatch(搜索退回旧逻辑)"; CITY_BAD=1; }
# citiesFull 必须带拼音字段 p(中国城市可拼音搜)且已转简体;抽查北京市 + 全表无残留繁体字。
if [ -f "${CITY_FULL}" ]; then
  node -e 'const a=require(process.argv[1]);const bj=a.find(c=>c.n==="北京市");if(!bj||!bj.p||bj.p.indexOf("bei jing")<0){console.error("NO_PINYIN");process.exit(2);}const trad=a.find(c=>/[門臺廣烏齊]/.test(c.n));if(trad){console.error("STILL_TRAD:"+trad.n);process.exit(3);}' "${CITY_FULL}" 2>/dev/null \
    || { bad "[36] citiesFull.json 缺拼音字段 p 或仍含繁体名(须 npm run build:cities 重建)"; CITY_BAD=1; }
else
  bad "[36] 缺 citiesFull.json"; CITY_BAD=1
fi
# 构建依赖只能在 devDependencies(不得进运行时 bundle)。
node -e 'const p=require(process.argv[1]);if((p.dependencies||{})["pinyin-pro"]||(p.dependencies||{})["opencc-js"]){console.error("IN_DEPS");process.exit(2);}if(!(p.devDependencies||{})["pinyin-pro"]||!(p.devDependencies||{})["opencc-js"]){console.error("MISSING_DEV");process.exit(3);}' "${UISRC}/../package.json" 2>/dev/null \
  || { bad "[36] pinyin-pro/opencc-js 必须在 devDependencies(build-only),不得进 dependencies/运行时"; CITY_BAD=1; }
[ "${CITY_BAD}" = "0" ] && ok "[36] cityMatch + 折叠表 + citiesFull(简体+拼音) + GeoCoordSelector 委托 + 构建依赖隔离 均在"
}

seg_37() {
# [37] 起课时间挂载 13 技法 + 5 builder opts 透传 + buildFieldObject divTime 兜底 (2026-06-08)
echo "[37] 起课时间挂载 13 技法 + builder opts 透传 + divTime 兜底"
T37_BAD=0
T37_AICTX="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js")"
T37_TMS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/techniqueMountSettings.js"
T37_TMS_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/techniqueMountSettings.test.js"
T37_AICTX_TEST="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/aiAnalysisContext.test.js"
T37_TAIXUAN="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/taixuan/TaiXuanMain.js"
T37_JINGJUE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/jingjue/JingJueMain.js"
T37_WUZHAO="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/wuzhao/WuZhaoMain.js"
T37_SHENYI="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/shenyishu/ShenYiShuMain.js"
if [ -f "${T37_AICTX}" ]; then
  for k in huangji taixuan jingjue wuzhao shenyishu; do
    awk '/TIMEPOINT_CASTABLE_SET =/' "${T37_AICTX}" | pipe_has "${k}" || { bad "[37] TIMEPOINT_CASTABLE_SET 缺 ${k}(下拉能选但显「缺失」)"; T37_BAD=1; }
  done
  grep -q "record.birth || record.divTime" "${T37_AICTX}" || { bad "[37] buildFieldObject 未兜底 record.divTime → timepoint 源 5 法时间出 NaN-undefined"; T37_BAD=1; }
  for k in huangji taixuan jingjue wuzhao shenyishu; do
    grep -qE "case '${k}':" "${T37_AICTX}" || { bad "[37] regenerateCaseTechniqueSnapshot 缺 case '${k}'(改 settings 不重算)"; T37_BAD=1; }
  done
fi
{ [ -f "${T37_TAIXUAN}" ] && grep -q "buildTaiXuanSnapshotForFields(fields, opts)" "${T37_TAIXUAN}"; } || { bad "[37] TaiXuanMain 缺 buildTaiXuanSnapshotForFields(fields, opts)"; T37_BAD=1; }
{ [ -f "${T37_JINGJUE}" ] && grep -q "buildJingJueSnapshotForFields(fields, opts)" "${T37_JINGJUE}"; } || { bad "[37] JingJueMain 缺 buildJingJueSnapshotForFields(fields, opts)"; T37_BAD=1; }
{ [ -f "${T37_WUZHAO}" ] && grep -q "buildWuZhaoSnapshotForFields(fields, opts)" "${T37_WUZHAO}"; } || { bad "[37] WuZhaoMain 缺 buildWuZhaoSnapshotForFields(fields, opts)"; T37_BAD=1; }
{ [ -f "${T37_SHENYI}" ] && grep -q "buildShenYiShuSnapshotForFields(fields, opts)" "${T37_SHENYI}"; } || { bad "[37] ShenYiShuMain 缺 buildShenYiShuSnapshotForFields(fields, opts)"; T37_BAD=1; }
if [ -f "${T37_TMS}" ]; then
  for k in taixuan jingjue wuzhao shenyishu; do
    grep -qE "${k}: \{ kind: 'payload'" "${T37_TMS}" || { bad "[37] techniqueMountSettings ${k} 必 kind:'payload'(sectionsOnly 不调 regenerate)"; T37_BAD=1; }
  done
fi
if [ -f "${T37_TMS_TEST}" ]; then
  awk '/SECTIONS_ONLY =/' "${T37_TMS_TEST}" | pipe_has "tongshefa" || { bad "[37] SECTIONS_ONLY 常量被改"; T37_BAD=1; }
fi
[ -f "${T37_AICTX_TEST}" ] && grep -q "timepoint) 必含全 13 项" "${T37_AICTX_TEST}" || { bad "[37] aiAnalysisContext.test.js 缺 13 项 timepoint 锁定断言"; T37_BAD=1; }
[ "${T37_BAD}" = "0" ] && ok "[37] timepoint 13 技法 + 4 builder opts + divTime 兜底 + 5 switch case + 4 payload schema + 测试锁 均到位"
}

seg_38() {
# [38] 合盘 (AstroRelative) 端点 :9999 + 子盘交互全链路 + 黄道 Select 局部定宽 (2026-06-08)
echo "[38] 合盘端点 + 子盘交互全链路 + 黄道 Select 定宽"
R38_BAD=0
R38_REL="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/astro/AstroRelative.js"
R38_LESS="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.less")"
R38_INDEX="${REPO_ROOT}/Horosa-Web/astrostudyui/src/pages/index.js"
if [ -f "${R38_REL}" ]; then
  grep -q "Constants.ServerRoot}/modern/relative" "${R38_REL}" || { bad "[38] AstroRelative 合盘端点必走 :9999 Java"; R38_BAD=1; }
  # 检查非注释行(忽略 // 开头的历史解释注释)
  grep -vE "^\s*//" "${R38_REL}" | pipe_has "resolveKentangServiceRoot" && { bad "[38] AstroRelative 残留 resolveKentangServiceRoot active 代码(:8899 不解密)"; R38_BAD=1; }
  grep -q "handleRelativeOnChange" "${R38_REL}" || { bad "[38] AstroRelative 缺 handleRelativeOnChange"; R38_BAD=1; }
  grep -q "ResizeObserver" "${R38_REL}" || { bad "[38] AstroRelative 缺 ResizeObserver(子盘下端空白真因)"; R38_BAD=1; }
fi
if [ -f "${R38_INDEX}" ]; then
  awk '/<AstroRelative/,/\/>/' "${R38_INDEX}" | pipe_has "chartStyle={chartStyle}" || { bad "[38] index.js AstroRelative 缺 chartStyle 透传"; R38_BAD=1; }
  awk '/<AstroRelative/,/\/>/' "${R38_INDEX}" | pipe_has "onChange={changeCond}" || { bad "[38] index.js AstroRelative 缺 onChange"; R38_BAD=1; }
fi
for f in AstroSynastry AstroMarks AstroComposite AstroTimeSpace relativeFields; do
  FP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/relative/${f}.js"
  [ -f "${FP}" ] || continue
  grep -q "hidezodiacal={1}" "${FP}" && { bad "[38] ${f} 仍有 hidezodiacal={1}(popover 空白)"; R38_BAD=1; }
  grep -q "hidehsys={1}" "${FP}" && { bad "[38] ${f} 仍有 hidehsys={1}"; R38_BAD=1; }
  awk '/function paramsToFields/,/^}/' "${FP}" | pipe_has "value: param.zodiacal" && { bad "[38] ${f} paramsToFields 仍覆盖 zodiacal(左栏改了显示不变)"; R38_BAD=1; }
done
if [ -f "${R38_LESS}" ]; then
  grep -q ".horosa-relative-page .horosa-field-block .ant-select-selector" "${R38_LESS}" || { bad "[38] app.less 缺合盘局部 Select CSS"; R38_BAD=1; }
fi
[ "${R38_BAD}" = "0" ] && ok "[38] 合盘 :9999 + 5 props 透传 + handleRelativeOnChange + ResizeObserver + paramsToFields 净化 + 黄道局部定宽 均到位"
}

seg_39() {
# [39] Python helper 接受数值 geo (地图选点存浮点) (2026-06-08)
echo "[39] Python helper 接受数值 geo"
GE39_BAD=0
GE39_HELP="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/helper.py"
GE39_REAL="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/jieqi/realsuntime.py"
if [ -f "${GE39_HELP}" ]; then
  grep -q "isinstance(lon," "${GE39_HELP}" || { bad "[39] helper.py 缺 isinstance(lon, ...)"; GE39_BAD=1; }
  grep -q "isinstance(lat," "${GE39_HELP}" || { bad "[39] helper.py 缺 isinstance(lat, ...)"; GE39_BAD=1; }
fi
if [ -f "${GE39_REAL}" ]; then
  grep -q "isinstance(zone," "${GE39_REAL}" || { bad "[39] realsuntime.py 缺 isinstance(zone, ...)"; GE39_BAD=1; }
fi
[ "${GE39_BAD}" = "0" ] && ok "[39] helper.py + realsuntime.py 数值 geo 容错 均在"
}

seg_195() {
# ── [195] 二十八宿相关六修(节气距离/宿度表/环长/锚点/死代码/天才双端) ─────────
# 全部经独立复核+史料查证落定,判据写在各自注释里;拆任一条即回到静默错值。
echo "== [195] 二十八宿六修资产 =="
S195_BAD=0
S195_JQ="${REPO_ROOT}/Horosa-Web/vendor/kintaiyi/src/kintaiyi/jieqi.py"
S195_CFG="${REPO_ROOT}/Horosa-Web/vendor/kintaiyi/src/kintaiyi/config.py"
S195_PC="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py")"
S195_ZJS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/ZiweiCalc.js"
S195_ZJV="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model/ZiWeiChart.java"
S195_T="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/ziwei/__tests__/ziweiTianCaiParity.test.js"
# ① distancejq 取当前节气(不得回潮 year-1)
grep -aq "get_jieqi_start_date(year, month, day, hour, minute)" "${S195_JQ}" 2>/dev/null || { bad "[195] 🔴 distancejq 未取当前节气起点"; S195_BAD=1; }
# 🔴 负锚必须只认【真代码形态】:文档字符串里引述旧写法时会误报(本哨兵初版即栽在这)。
# 旧代码独有形态 = 同一行里既有 `return int( Date(` 又有 `find_jq_date(year-1`。
grep -aE "return int\( *Date\(.*find_jq_date\(year-1," "${S195_JQ}" >/dev/null 2>&1 && { bad "[195] 🔴 distancejq 的 year-1 回潮(春分当天会返回 365)"; S195_BAD=1; }
# ①' 全年份域:distancejq 取 now 必须走 ephem.Date,不得用 datetime.datetime。
#     datetime 只支持公元 1..9999,而本函数经 starhouse 服务于太乙全年份域 ——
#     ①的首版改用 datetime 取 now,公元前 1 年/16798 年直接 ValueError 炸掉整个
#     taiyi/pan(极端年矩阵三例转红)。负锚只认 now 赋值这一真代码形态。
grep -aq "now = Date(" "${S195_JQ}" 2>/dev/null || { bad "[195] 🔴 distancejq 的 now 未走 ephem.Date(全年份域会炸)"; S195_BAD=1; }
grep -aE "^\s*now = datetime\.datetime\(year," "${S195_JQ}" >/dev/null 2>&1 && { bad "[195] 🔴 distancejq 回潮 datetime.datetime 取 now(公元前/远未来 ValueError,taiyi/pan 全炸)"; S195_BAD=1; }
S195_JQT="${REPO_ROOT}/Horosa-Web/astropy/tests/test_kintaiyi_jieqi_distance.py"
[ -f "${S195_JQT}" ] || { bad "[195] 🔴 节气距离金标缺失(纯单元,不依赖 :8899——极端年矩阵要服务在线,单靠它守不住离线自检)"; S195_BAD=1; }
# ② 虚宿距度(汉书10/授时9,原误作25)
grep -aq "numlist = \[13, 9, 16, 5, 5, 17, 10, 24, 7, 11, 10, 18," "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 虛宿距度非 10(汉书/授时两源皆远小于原值 25)"; S195_BAD=1; }
# ③ 环长按表长取模(不得写死 360)
grep -aq "zhoutian = len(gensulist)" "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 周天写死回潮(表长 363 与 360 不符即静默混叠)"; S195_BAD=1; }
grep -aqE "new_num = num -360" "${S195_CFG}" 2>/dev/null && { bad "[195] 🔴 旧 -360 环绕回潮"; S195_BAD=1; }
# ④ 三处节气锚点(判据=24 步间隔须 13~17)
grep -aq '\["井", 12\]' "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 夏至锚点非井12(原井1 致 4/26 度畸形步)"; S195_BAD=1; }
grep -aq '\["箕",4\]' "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 大雪锚点非箕4(原箕24 越出箕宿致岁末倒退)"; S195_BAD=1; }
grep -aq '\["氐", 2\],\["房",1\]' "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 霜降/立冬 氐房顺序回潮(原序为全环唯一逆行)"; S195_BAD=1; }
# ⑤ 节气名对不上须硬报错(不得静默取首宿)
grep -aq "starhouse: 节气" "${S195_CFG}" 2>/dev/null || { bad "[195] 🔴 锚点缺失时的硬报错缺失(会把错误伪装成宿名交出)"; S195_BAD=1; }
# ⑥ MOIRA 赤经死代码停用
grep -aq "_moira_distar_ra 已停用" "${S195_PC}" 2>/dev/null || { bad "[195] 🔴 _moira_distar_ra 停用守卫缺失(按赤经定宿会偏 10–44°)"; S195_BAD=1; }
# ⑦ 天才双端同式(JS/Java 必须同改,否则前后端分叉)
grep -aq "placeRec((lifeIdx + yearZiIdx) % 12, '天才', 3)" "${S195_ZJS}" 2>/dev/null || { bad "[195] 🔴 JS 天才落宫式回潮(宫名反查恒偏一位)"; S195_BAD=1; }
grep -aq "int caiIdx = (this.lifeHouseIndex + yearziIdx0 + 24) % 12;" "${S195_ZJV}" 2>/dev/null || { bad "[195] 🔴 Java 天才落宫式未同改(前后端分叉)"; S195_BAD=1; }
[ -f "${S195_T}" ] || { bad "[195] 🔴 天才/马星金标缺失"; S195_BAD=1; }
[ "${S195_BAD}" = "0" ] && ok "[195] 二十八宿六修(节气距离/虛10/环长/三锚点/硬报错/死代码/天才双端)全在位"
}

seg_196() {
# ── [196] 三式外圈随时间校正 + 遁甲/择日遮罩 + 六壬环角宫排版 ─────────────────
# 用户实测三轮才定位的一类**静默错值**:三式已起盘后按时间步进,中栏表头与奇门/太乙盘都跟着走,
# 唯独外圈星度(顶/升/金/日/月,唯一数据源 props.chartObj)冻在起盘那一刻;同一时辰内奇门局与
# 太乙局本就不变,于是整盘看上去「完全没动」。差分实证(同一时刻):点「确定」盘更新、按步进不更新。
# 三道判据缺一即复发,故逐条钉死。
echo "[196] 三式外圈随时间校正 + 遮罩 + 角宫排版"
S196_BAD=0
S196_SS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/SanShiUnitedMain.js"
S196_FLAGS="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/perfFlags.js"
S196_DJ="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/dunjia/DunJiaMain.js"
S196_LESS="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astrostudyui/src/layouts/app.less")"
S196_T="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/sanshi/__tests__/outerRingFollowsTime.test.js"
# ① chartObj 校正不得被 awaitingChartSync 闸死(实时传导路径下它恒为 false)
grep -aq "if(this.state.hasPlotted && chartChanged){" "${S196_SS}" 2>/dev/null || { bad "[196] 🔴 三式 chartObj 校正判据缺失(外圈会冻在起盘那一刻)"; S196_BAD=1; }
grep -aq "if(this.awaitingChartSync && this.state.hasPlotted && chartChanged)" "${S196_SS}" 2>/dev/null && { bad "[196] 🔴 awaitingChartSync 前置条件回潮(它恒 false,校正整个被跳过)"; S196_BAD=1; }
# ② outerChartKey 不得含随机 chartId(否则同刻重复回流也判「变了」,每次全量重算)
grep -aE "^\s+chartId,\s*$" "${S196_SS}" >/dev/null 2>&1 && { bad "[196] 🔴 getOuterChartKey 回潮纳入随机 chartId"; S196_BAD=1; }
# ③ /chart 主链 abort 必须默认关 —— 两个并发请求会互相残杀致 chartObj 永不更新
grep -aq "=== '1'" "${S196_FLAGS}" 2>/dev/null || { bad "[196] 🔴 mainChainAbort 未保持默认关(双杀致盘不跟时间走)"; S196_BAD=1; }
grep -aq "return flagEnabled('horosa.perf.mainChainAbort')" "${S196_FLAGS}" 2>/dev/null && { bad "[196] 🔴 mainChainAbort 回潮为默认开"; S196_BAD=1; }
# ④ 遁甲/择日全屏遮罩已撤为中栏小徽标(择日内嵌的正是 DunJiaMain,一处守两处)
grep -aq "<Spin spinning={this.state.loading}>" "${S196_DJ}" 2>/dev/null && { bad "[196] 🔴 遁甲全屏 Spin 遮罩回潮(用户明令只留中栏小徽标)"; S196_BAD=1; }
grep -aq "horosa-workspace-updating horosa-dunjia-updating" "${S196_DJ}" 2>/dev/null || { bad "[196] 🔴 遁甲中栏小徽标缺失"; S196_BAD=1; }
grep -aq "horosa-dunjia-updating" "${S196_LESS}" 2>/dev/null || { bad "[196] 🔴 遁甲徽标样式缺失(absolute 会飞到窗口角)"; S196_BAD=1; }
# ⑤ 六壬环角宫:落点回重心 + 外推调小(原 3.1 会把字压出外框)
grep -aq "巳: { left: '29.6%', top: '25.9%'" "${S196_SS}" 2>/dev/null || { bad "[196] 🔴 六壬环角宫落点非重心原值"; S196_BAD=1; }
grep -aq "const outerShift = 3.1;" "${S196_SS}" 2>/dev/null && { bad "[196] 🔴 角宫径向外推回潮 3.1(字会压出外框)"; S196_BAD=1; }
[ -f "${S196_T}" ] || { bad "[196] 🔴 外圈随时间校正金标缺失"; S196_BAD=1; }
[ "${S196_BAD}" = "0" ] && ok "[196] 外圈随时间校正(校正闸/键去随机/abort默认关)+遁甲择日小徽标+角宫排版 全在位"
}

seg_240() {
# seg_240 西占宫主口径单源锁(Windows #79):宫主/主宰=整宫制自上升起算(与后端 ruleHouses/快照 nR 同源),行星力量=当前分宫制;
#   两表派生只许一份实现(utils/wholeSignRulers.js),AI 快照与主页 AstroDispositor/AstroInfo 同函数(禁本地 SIGN_RULER 查表);
#   [分宫制宫神星表] 独立段:九个西占键 preset 紧随「主宰星链」+ v57 union(MIGRATION_VERSION 恒 44);旧格式快照按 payload 格式版本失效;三测在位。
echo "[${PF_NO}] 西占宫主口径单源(整宫制宫主表/分宫制宫神星表)锁"
S240_BAD=0
S240_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
[ -f "${S240_UI}/src/utils/wholeSignRulers.js" ] || { bad "[${PF_NO}] wholeSignRulers.js 缺失(宫主派生单源)"; S240_BAD=1; }
grep -aq "from './wholeSignRulers'" "${S240_UI}/src/utils/astroAiSnapshot.js" || { bad "[${PF_NO}] astroAiSnapshot.js 未引宫主单源"; S240_BAD=1; }
grep -aq "utils/wholeSignRulers'" "${S240_UI}/src/components/astro/AstroDispositor.js" || { bad "[${PF_NO}] AstroDispositor.js 未引宫主单源"; S240_BAD=1; }
grep -aq "utils/wholeSignRulers'" "${S240_UI}/src/components/astro/AstroInfo.js" || { bad "[${PF_NO}] AstroInfo.js 未引宫主单源(命主星)"; S240_BAD=1; }
S240_LOCAL="$(grep -anF "SIGN_RULER = {" "${S240_UI}/src/components/astro/AstroDispositor.js" "${S240_UI}/src/components/astro/AstroInfo.js" "${S240_UI}/src/utils/astroAiSnapshot.js" 2>/dev/null | grep -vE ":[0-9]+:\s*//" || true)"
[ -z "${S240_LOCAL}" ] || { bad "[${PF_NO}] 宫主查表又长回第二份本地实现(须走 wholeSignRulers.rulerOfSign):"; echo "${S240_LOCAL}" | head -3 | sed 's/^/      /'; S240_BAD=1; }
grep -aqF "'◆ 整宫制宫主表(wholeSignRulers)'" "${S240_UI}/src/utils/astroAiSnapshot.js" || { bad "[${PF_NO}] [主宰星链] 缺整宫制宫主表子块"; S240_BAD=1; }
grep -aqF "buildSectionText('分宫制宫神星表'" "${S240_UI}/src/utils/astroAiSnapshot.js" || { bad "[${PF_NO}] 快照缺 [分宫制宫神星表] 独立段"; S240_BAD=1; }
grep -aqF "'◆ 宫神星(houseRows)'" "${S240_UI}/src/utils/astroAiSnapshot.js" && { bad "[${PF_NO}] 旧「◆ 宫神星(houseRows)」子块回潮到 [主宰星链](分宫制表须独立成段并标宫制)"; S240_BAD=1; }
grep -aqF "export const ASTRO_SNAPSHOT_FORMAT_VERSION" "${S240_UI}/src/utils/astroAiSnapshot.js" || { bad "[${PF_NO}] astroAiSnapshot.js 缺快照格式版本常量"; S240_BAD=1; }
grep -aqF "ASTRO_SNAPSHOT_FORMAT_VERSION" "$(pf_src_set "${S240_UI}/src/utils/aiAnalysisContext.js")" || { bad "[${PF_NO}] aiAnalysisContext.js 缺旧格式快照守卫"; S240_BAD=1; }
S240_PRESET="$(grep -acF "'主宰星链', '分宫制宫神星表'" "$(pf_src_set "${S240_UI}/src/utils/aiExport.js")" || true)"
[ "${S240_PRESET:-0}" -ge 9 ] || { bad "[${PF_NO}] aiExport.js preset 含「主宰星链, 分宫制宫神星表」行数 ${S240_PRESET:-0} < 9(九个西占键必登记,否则该段被静默删)"; S240_BAD=1; }
grep -aq "AI_EXPORT_V57_SECTION_UNION" "$(pf_src_set "${S240_UI}/src/utils/aiExport.js")" || { bad "[${PF_NO}] aiExport.js 缺 v57 union"; S240_BAD=1; }
grep -aqF "AI_EXPORT_SECTION_MIGRATION_VERSION = 44;" "$(pf_src_set "${S240_UI}/src/utils/aiExport.js")" || { bad "[${PF_NO}] AI_EXPORT_SECTION_MIGRATION_VERSION 被动(须恒 44)"; S240_BAD=1; }
for f in wholeSignRulers.test.js astroV2FactEquivalence.test.js astroClassicalSnapshot.test.js; do
  [ -f "${S240_UI}/src/utils/__tests__/${f}" ] || { bad "[${PF_NO}] 测试缺失:${f}"; S240_BAD=1; }
done
grep -aqF "POST_BASELINE_HEADS" "${S240_UI}/src/utils/__tests__/astroV2FactEquivalence.test.js" || { bad "[${PF_NO}] 等价证明缺段头白名单守卫(基线只读,新段须白名单)"; S240_BAD=1; }
[ "${S240_BAD}" = "0" ] && ok "[${PF_NO}] 西占宫主口径:单源在位/零本地查表/两表两段/preset×9+v57/MIGRATION 44/格式版本守卫/三测在位"
}

seg_243() {
# seg_243 产品口径锁(中国大陆统一时区归并/地名中文别名与重音折叠/跨技法时间基准自声明)
echo "[${PF_NO}] 产品口径锁(中国大陆统一时区归并/地名中文别名与重音折叠/跨技法时间基准自声明)"
S243_BAD=0
S243_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
grep -aq "CN_UNIFIED_ZONE_SINCE" "${S243_UI}/src/utils/timezone.js" || { bad "[${PF_NO}] timezone.js 缺统一北京时间归并"; S243_BAD=1; }
[ "$(sed -E 's#//.*$##' "${S243_UI}/src/utils/timezone.js" | grep -ac "return '+08:00'")" = "0" ] || { bad "[${PF_NO}] timezone.js 出现写死 +08:00 返回(须按日期算偏移)"; S243_BAD=1; }
grep -aq "'horosa.tz.cnUnified'" "${S243_UI}/src/utils/storageKeyRegistry.js" || { bad "[${PF_NO}] horosa.tz.cnUnified 未登记注册表"; S243_BAD=1; }
grep -aq "cn-unified" "${S243_UI}/src/components/amap/GeoCoordSelector.js" || { bad "[${PF_NO}] 选点预览缺官方/当地惯用提示"; S243_BAD=1; }
grep -aq "world_cities_zh" "${S243_UI}/scripts/build-cities.js" || { bad "[${PF_NO}] build-cities 未合并中文别名种子"; S243_BAD=1; }
[ "$(python3 -c "import json;d=json.load(open('${S243_UI}/scripts/data/world_cities_zh.json'));print(len([k for k in d if k!='_doc']))" 2>/dev/null || echo 0)" -ge 300 ] || { bad "[${PF_NO}] 中文别名种子少于 300 条"; S243_BAD=1; }
grep -aq "雷克雅未克" "${S243_UI}/src/data/citiesFull.json" || { bad "[${PF_NO}] citiesFull.json 未含中文别名(需 npm run build:cities)"; S243_BAD=1; }
grep -aq "export function foldAscii" "${S243_UI}/src/components/amap/cityMatch.js" || { bad "[${PF_NO}] cityMatch 缺重音折叠"; S243_BAD=1; }
[ -f "${S243_UI}/src/utils/timeBasisLine.js" ] || { bad "[${PF_NO}] timeBasisLine.js 缺失"; S243_BAD=1; }
[ "$(grep -ac 'buildTimeBasisLine(' "$(pf_src_set "${S243_UI}/src/components/guolao/GuoLaoChartMain.js")")" -ge 2 ] || { bad "[${PF_NO}] 七政两处 [起盘信息] 未自声明时间基准"; S243_BAD=1; }
grep -aq "buildTimeBasisLine(" "${S243_UI}/src/components/cntradition/BaZi.js" || { bad "[${PF_NO}] 八字 [起盘信息] 未自声明时间基准"; S243_BAD=1; }
grep -aq "withTimeBasis: true" "${S243_UI}/src/utils/astroAiSnapshot.js" || { bad "[${PF_NO}] 星盘 [起盘信息] 未自声明时间基准"; S243_BAD=1; }
grep -aq "时间基准" "${S243_UI}/src/utils/aiAgent/protocol.js" || { bad "[${PF_NO}] AGENT_SYSTEM_RULES 缺跨技法时间基准条款"; S243_BAD=1; }
for t in timezone.cnRegion snapshotTimeBasis.contract; do [ -f "${S243_UI}/src/utils/__tests__/$t.test.js" ] || { bad "[${PF_NO}] 回归测试 $t.test.js 缺失"; S243_BAD=1; }; done
[ "${S243_BAD}" = "0" ] && ok "[${PF_NO}] 产品口径锁(中国大陆统一时区归并/地名中文别名与重音折叠/跨技法时间基准自声明)"
}

seg_301() {
echo "[${PF_NO}] 八字岁数 / 年份口径:回退 Java 的岁数对齐虚岁 + 旧版界面与快照随「年龄」档 + 跨公元纪元无 0 年"
S301_BAD=0
S301_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S301_CT="${S301_UI}/components/cntradition"
S301_CN="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn"
# ① 取数入口:/bazi/birth、/bazi/direct 两处回退结果都先对齐为虚岁(大运按天文年差,跨纪元不多算)
[ "$(grep -cF 'alignJavaBaziAges(data[Constants.ResultKey])' "${S301_CT}/BaZi.js" 2>/dev/null)" -ge 2 ] \
  && grep -qF 'd.age = displayYearDiff(birthYear, startYear) + 1;' "${S301_CT}/BaZi.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 八字页回退 Java 的结果未在取数入口对齐为虚岁(公元前 / 域外年份岁数小一岁)"; S301_BAD=1; }
# ② 岁数显示单源 + 旧版界面随「年龄」档
grep -qF "export function baziAgeText(age, ageStyle, legacySuffix = '周岁'){" "${S301_CT}/baziAgeText.js" 2>/dev/null \
  && grep -qF "return ageStyle === 'real' ? Math.max(0, n - 1) : n;" "${S301_CT}/baziAgeText.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 岁数显示单源 baziAgeText 缺失或换算被改"; S301_BAD=1; }
for s301_f in MDSDirect MDSYear SmallDirection MainDirection BaZiLegacyView; do
  grep -qF 'baziAgeText(' "${S301_CT}/${s301_f}.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 ${s301_f} 岁数未走 baziAgeText(虚岁数据标「周岁」大一岁)"; S301_BAD=1; }
done
if grep -qF '<span>{age}周岁</span>' "${S301_CT}/MDSDirect.js" 2>/dev/null || grep -qF "nowage + '周岁'" "${S301_CT}/MDSYear.js" 2>/dev/null \
  || grep -qF '{d.age !== undefined ? `${d.age}周岁`' "${S301_CT}/SmallDirection.js" 2>/dev/null || grep -qF '{age ? `${age}周岁` : ' "${S301_CT}/BaZiLegacyView.js" 2>/dev/null; then
  bad "[${PF_NO}] 🔴 旧版界面又出现把原值直接标「周岁」的写法"; S301_BAD=1
fi
[ "$(grep -cF 'ageStyle={ageStyle} />' "${S301_CT}/BaZiLegacyView.js" 2>/dev/null)" -ge 3 ] \
  && grep -qF "<BaZiLegacyInfoPanel value={bazi} fields={this.effFields()} height={tabHeight} ageStyle={(this.state.baziOpt && this.state.baziOpt.ageStyle) || 'nominal'} />" "${S301_CT}/BaZi.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 旧版界面三处岁数未下传「年龄」档"; S301_BAD=1; }
# ③ AI 快照「流年行运概略」起始年龄随档
grep -qF "const startAge = block && block.age !== undefined ? baziAgeText(block.age, overviewAgeStyle) : '';" "${S301_CT}/BaZi.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 快照起始年龄又恒写虚岁(与小运表口径不一)"; S301_BAD=1; }
# ④ 显示年算术(无公元 0 年):行运面板 / 细盘 / 旧版 / 快照
grep -qF 'export function addDisplayYears(year, n){' "${S301_UI}/utils/dateStrSafe.js" 2>/dev/null \
  && grep -qF 'export function displayYearDiff(a, b){' "${S301_UI}/utils/dateStrSafe.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 dateStrSafe 缺显示年算术"; S301_BAD=1; }
if grep -qF 'const year = luck.startYear + idx;' "${S301_CT}/BaZiLuckFlowPanel.js" 2>/dev/null || grep -qF 'const year = birthYear + idx;' "${S301_CT}/BaZiLuckFlowPanel.js" 2>/dev/null \
  || grep -qF 'return SixtyJiaZi[mod(year - 1984, 60)];' "${S301_CT}/BaZiLuckFlowPanel.js" 2>/dev/null \
  || grep -qF 'const index = Number(selection.year) - Number(block.startYear);' "${S301_CT}/BaZiFineChart.js" 2>/dev/null; then
  bad "[${PF_NO}] 🔴 行运面板 / 细盘又直接加减年份(跨公元纪元出 0 年、公元前年干支错一位)"; S301_BAD=1
fi
# ⑤ Java:大运起运岁、小运年份跨纪元
[ "$(grep -cF 'int age = historicalYearDiff(birthYear, dirYear);' "${S301_CN}/model/BaZiDirect.java" 2>/dev/null)" -eq 2 ] \
  && [ "$(grep -cF 'int age = historicalYearDiff(birthYear, dirYear);' "${S301_CN}/model/OnlyFourColumns.java" 2>/dev/null)" -eq 2 ] \
  && [ "$(grep -cF 'int y = addHistoricalYears(year, i);' "${S301_CN}/model/BaZiDirect.java" 2>/dev/null)" -eq 2 ] || { bad "[${PF_NO}] 🔴 Java 大运岁 / 小运年份又直接加减(公元前出生起运岁多一岁、小运出 0 年)"; S301_BAD=1; }
grep -qF 'bcBirthLuckStartingInAdDoesNotCountYearZero' "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/test/java/spacex/astrostudycn/model/BaZiEraBoundaryTest.java" 2>/dev/null \
  && grep -qF '旧版界面岁数随「年龄」档' "${S301_CT}/__tests__/baziAgeYearConvention.test.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 缺岁数 / 年份口径测试(前端 / Java)"; S301_BAD=1; }
S301_FAT="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
if [ -f "${S301_FAT}" ]; then
  s301_cn="$(unzip -Z1 "${S301_FAT}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${s301_cn}" ]; then
    s301_tmp="$(mktemp -d "${PF_TMP}/s301_tmp.XXXXXX")"; unzip -oq "${S301_FAT}" "${s301_cn}" -d "${s301_tmp}" 2>/dev/null
    unzip -p "${s301_tmp}/${s301_cn}" spacex/astrostudycn/model/BaZi.class 2>/dev/null | strings | pipe_has "historicalYearDiff" || { bad "[${PF_NO}] fat jar 未含 historicalYearDiff —— 需 astrostudycn install + astrostudyboot clean package"; S301_BAD=1; }
    rm -rf "${s301_tmp}"
  fi
fi
[ "${S301_BAD}" = "0" ] && ok "[${PF_NO}] 八字岁数 / 年份口径:取数入口对齐虚岁 / 旧版界面与快照随「年龄」档 / 显示年算术 / Java 跨纪元 / 测试 / 运行时 jar 在位"
}

seg_207() {
# ── [207] 盘面美术(wheel art)五档全链(2026-08-09) ────────────────────────────
# 病灶预防:①wheelArt 不进 AstroChart sCU 白名单=改档不重绘死开关;②app model globalSetup 白名单漏键=静默不存;
# ③重绘签名缺维度=方盘切回圆盘白屏;④中世纪坐标表(徽章=宫头线中点/星体=三角质心/宫号贴内方形)金标锁死。
echo "[207] 盘面美术五档全链"
S207_BAD=0
S207_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
grep -qF "'wheelArt'," "${S207_UI}/components/astro/AstroChart.js" \
  || { bad "[207] 🔴 wheelArt 不在 AstroChart sCU 白名单(改档不重绘=死开关)"; S207_BAD=1; }
grep -qF "'wheelArt'," "${S207_UI}/utils/globalSetupStore.js" \
  && grep -qF 'mergeGlobalSetupWrite(patch);' "${S207_UI}/models/app.js" \
  || { bad "[207] 🔴 全局设置落盘字段表缺 wheelArt / app model 未经落盘单源写(跨会话保存静默失效)"; S207_BAD=1; }
grep -qF 'export function normalizeWheelArt' "${S207_UI}/constants/AstroConst.js" \
  || { bad "[207] 🔴 wheelArt 归一函数缺失"; S207_BAD=1; }
grep -qF 'renderWheelStyleGrid' "${S207_UI}/components/astro/AstroChartMain.js" \
  || { bad "[207] 🔴 星盘样式双下拉单源方法被拆(外环样式+盘面美术)"; S207_BAD=1; }
[ -s "${S207_UI}/components/astro/__tests__/wheelArtChart.test.js" ] \
  || { bad "[207] 🔴 盘面美术金标缺失(中世纪几何校准规格失锁)"; S207_BAD=1; }
grep -qF '每个 <AstroChart 渲染点' "${S207_UI}/components/astro/__tests__/wheelArtChart.test.js" \
  || { bad "[207] 🔴 消费点完备性总锁被拆(新增 AstroChart 渲染点漏接 wheelArt 将无人拦截)"; S207_BAD=1; }
grep -qF '至少一个宿主渲染点传了 wheelArt' "${S207_UI}/components/astro/__tests__/wheelArtChart.test.js" \
  || { bad "[207] 🔴 宿主链断点总锁被拆(组件接了 props 宿主没传=选了无效死开关)"; S207_BAD=1; }
grep -qF 'wheelArt: this.props.wheelArt' "${S207_UI}/components/astro/AstroChart.js" \
  || { bad "[207] 🔴 重绘签名缺 wheelArt 维度(方盘切回圆盘白屏)"; S207_BAD=1; }
[ "${S207_BAD}" = "0" ] && ok "[207] 盘面美术 sCU键/持久化白名单/归一/双下拉/几何金标/双总锁/签名维度 全绿"
}

seg_296() {
# [${PF_NO}] 八字时间算法口径:「直接时间」不做任何时刻换算(年柱 / 月柱 / 交节距离也按所填钟表时刻,不沿用计算服务的卯时偏移
#       —— 否则交节后一段时间内节气窗越界报错);「春分定卯时」尚无独立换算,模型与四处控制器缓存键一律按「直接时间」算
#       (否则按平移后的时刻判换日,多数时辰日柱前错一天)。真太阳时 / 平太阳时结果不变。锚住防回潮(2026-09-27)。
echo "[${PF_NO}] 八字时间算法口径:直接时间零偏移 + 春分定卯时按直接时间"
S296_BAD=0
S296_CN="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn"
S296_T="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/test/java/spacex/astrostudycn/model/BaZiTimeAlgBasisTest.java"
grep -q "return this == SpringMao ? DirectTime : this;" "${S296_CN}/constants/TimeZiAlg.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 TimeZiAlg.calcBasis 缺失(春分定卯时未归直接时间)"; S296_BAD=1; }
grep -q "this.timeAlg = timeAlg == null ? null : timeAlg.calcBasis();" "${S296_CN}/model/BaZi.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 BaZi 构造未按 calcBasis 归一时间算法"; S296_BAD=1; }
grep -A5 "}else if(this.timeAlg == TimeZiAlg.DirectTime) {" "${S296_CN}/model/BaZi.java" 2>/dev/null | pipe_has "this.timeOffsetJDN = 0;" || { bad "[${PF_NO}] 🔴 直接时间未清零偏移(会沿用卯时偏移平移出生时刻)"; S296_BAD=1; }
for s296_c in BaZiBirthController PaiBaZiController LiuRengController JieQiController; do
  grep -q "TimeZiAlg.fromCode(time[A-Za-z]*).calcBasis()" "${S296_CN}/controller/${s296_c}.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 ${s296_c} 缓存键未按 calcBasis 归一"; S296_BAD=1; }
done
grep -q "springMaoOutputEqualsDirectTimeByteForByte" "${S296_T}" 2>/dev/null && grep -q "directTimeUsesClockTimeWithoutOffset" "${S296_T}" 2>/dev/null \
  && grep -q "solarTimeAlgorithmsKeepTheirOffsets" "${S296_T}" 2>/dev/null || { bad "[${PF_NO}] 🔴 测试缺「春分定卯时 = 直接时间逐字节」/「直接时间零偏移」/「真太阳时平太阳时照旧」"; S296_BAD=1; }
S296_FAT="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
if [ -f "${S296_FAT}" ]; then
  s296_cn="$(unzip -Z1 "${S296_FAT}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${s296_cn}" ]; then
    s296_tmp="$(mktemp -d "${PF_TMP}/s296_tmp.XXXXXX")"; unzip -oq "${S296_FAT}" "${s296_cn}" -d "${s296_tmp}" 2>/dev/null
    unzip -p "${s296_tmp}/${s296_cn}" spacex/astrostudycn/constants/TimeZiAlg.class 2>/dev/null | strings | pipe_has "calcBasis" || { bad "[${PF_NO}] fat jar 未含 calcBasis —— 需 astrostudycn install + astrostudyboot clean package"; S296_BAD=1; }
    rm -rf "${s296_tmp}"
  fi
fi
[ "${S296_BAD}" = "0" ] && ok "[${PF_NO}] 直接时间零偏移 + 春分定卯时按直接时间(模型 / 四处缓存键 / 测试 / 运行时 jar)在位"
}

seg_297() {
# [${PF_NO}] 年柱按立春本身判定 + 换算后跨出节气窗时重取窗口:一、二月出生与节气窗里的立春(ord == 0 的节)比较,不按固定下标
#       (节气窗会在生辰前补项以包住生辰,二月立春前出生时立春不在 [2]);不再「换算跨立春另进一年」(年柱已按换算后时刻判定);
#       真太阳时 / 平太阳时换算后跨回交节前、落出按钟表时刻取的节气窗时,按换算后时刻重取窗口,不再报错。锚住防回潮(2026-09-27)。
echo "[${PF_NO}] 年柱按立春本身判定 + 换算后跨出节气窗重取窗口"
S297_BAD=0
S297_H="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/helper/BaZiHelper.java"
S297_B="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/model/BaZi.java"
S297_J="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn/controller/JieQiController.java"
S297_T="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/test/java/spacex/astrostudycn/model/BaZiLichunWindowTest.java"
grep -q "static Map<String, Object> findLichun(Map<String, Object>\[\] jieqi, double birthJdn)" "${S297_H}" 2>/dev/null \
  && grep -q "if(m == Calendar.JANUARY || m == Calendar.FEBRUARY) {" "${S297_H}" 2>/dev/null \
  && grep -q "Map<String, Object> lichun = findLichun(jieqi, jdn);" "${S297_H}" 2>/dev/null || { bad "[${PF_NO}] 🔴 年柱未按窗口里的立春本身判定(一、二月)"; S297_BAD=1; }
grep -q "Map<String, Object> map = jieqi\[2\];" "${S297_H}" 2>/dev/null && { bad "[${PF_NO}] 🔴 年柱又按固定下标 jieqi[2] 取立春"; S297_BAD=1; }
grep -q "nextYear" "${S297_B}" 2>/dev/null && { bad "[${PF_NO}] 🔴 BaZi 又出现跨立春另进一年(年柱已按换算后时刻判定,再进 = 多算一年)"; S297_BAD=1; }
grep -q "private int locateBirthJie() {" "${S297_B}" 2>/dev/null \
  && grep -q "BaZiHelper.getJieQiInfo(this.ad, this.birth, this.zone, this.lon, this.lat, useLocalMao, byLon).get(\"jieqi\")" "${S297_B}" 2>/dev/null \
  && [ "$(grep -c "jieidx = this.locateBirthJie();" "${S297_B}" 2>/dev/null)" -ge 2 ] || { bad "[${PF_NO}] 🔴 换算后跨出节气窗未按换算后时刻重取窗口"; S297_BAD=1; }
s297_rev="$(grep -oE 'JieQiYearCacheRev = "jieqi_year_bazi_v[0-9]+"' "${S297_J}" 2>/dev/null | grep -oE '[0-9]+"$' | tr -d '"')"
[ "${s297_rev:-0}" -ge 6 ] 2>/dev/null || { bad "[${PF_NO}] 🔴 节气年表缓存代次低于 v6(旧年缓存 180 天返旧四柱)"; S297_BAD=1; }
for s297_m in februaryBeforeLichunIsPreviousYear julianEraLichunInLateJanuary solarTimeCrossingLichunAddsNoExtraYear shiftedBirthOutsideClockWindowRefetches; do
  grep -q "${s297_m}" "${S297_T}" 2>/dev/null || { bad "[${PF_NO}] 🔴 测试缺 ${s297_m}"; S297_BAD=1; }
done
S297_FAT="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
if [ -f "${S297_FAT}" ]; then
  s297_tmp="$(mktemp -d "${PF_TMP}/s297_tmp.XXXXXX")"
  s297_as="$(unzip -Z1 "${S297_FAT}" 'BOOT-INF/lib/astrostudy-1*.jar' 2>/dev/null | head -1)"
  s297_cn="$(unzip -Z1 "${S297_FAT}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${s297_as}" ] && [ -n "${s297_cn}" ]; then
    unzip -oq "${S297_FAT}" "${s297_as}" "${s297_cn}" -d "${s297_tmp}" 2>/dev/null
    unzip -p "${s297_tmp}/${s297_as}" spacex/astrostudy/helper/BaZiHelper.class 2>/dev/null | strings | pipe_has "findLichun" || { bad "[${PF_NO}] fat jar 未含 findLichun —— 需 astrostudy / astrostudycn install + astrostudyboot clean package"; S297_BAD=1; }
    unzip -p "${s297_tmp}/${s297_cn}" spacex/astrostudycn/model/BaZi.class 2>/dev/null | strings | pipe_has "locateBirthJie" || { bad "[${PF_NO}] fat jar 未含 locateBirthJie —— 需 astrostudycn install + astrostudyboot clean package"; S297_BAD=1; }
  fi
  rm -rf "${s297_tmp}"
fi
[ "${S297_BAD}" = "0" ] && ok "[${PF_NO}] 年柱按立春本身判定 / 不另进一年 / 跨出节气窗重取 / 年表缓存代次 / 测试 / 运行时 jar 在位"
}

seg_298() {
# [${PF_NO}] 经纬度串按「度 + 分 / 60」解析(真太阳时 / 平太阳时偏移随之正确)+ 日柱按换算后时刻取、不再另减一天
#       (偏移大的西部地点子时出生此前日柱前错一天)。锚住防回潮(2026-09-27)。
echo "[${PF_NO}] 经纬度串「度 + 分 / 60」+ 日柱不另减一天"
S298_BAD=0
S298_W="${REPO_ROOT}/Horosa-Web/astrostudysrv"
S298_P="${S298_W}/boundless/src/main/java/boundless/utility/PositionUtility.java"
S298_B="${S298_W}/astrostudycn/src/main/java/spacex/astrostudycn/model/BaZi.java"
grep -q "static double parseDegreeMinute(String degStr, String minStr){" "${S298_P}" 2>/dev/null \
  && grep -q "ConvertUtility.getValueAsDouble(minStr, 0) / 60.0" "${S298_P}" 2>/dev/null \
  && [ "$(grep -c "return parseDegreeMinute(parts\[0\], parts\[1\]) \* positive;" "${S298_P}" 2>/dev/null)" -ge 2 ] || { bad "[${PF_NO}] 🔴 经纬度串未按「度 + 分 / 60」解析(经度 / 纬度两处)"; S298_BAD=1; }
grep -q "(1.0 / min" "${S298_P}" 2>/dev/null && { bad "[${PF_NO}] 🔴 经纬度串又出现「度 + 1 / 分」"; S298_BAD=1; }
grep -Eq "prevDay|nextDay|offsetTimeZi" "${S298_B}" 2>/dev/null && { bad "[${PF_NO}] 🔴 BaZi 又出现日柱另减一天(日柱已按换算后时刻取)"; S298_BAD=1; }
s298_rev="$(grep -oE 'JieQiYearCacheRev = "jieqi_year_bazi_v[0-9]+"' "${S298_W}/astrostudycn/src/main/java/spacex/astrostudycn/controller/JieQiController.java" 2>/dev/null | grep -oE '[0-9]+"$' | tr -d '"')"
[ "${s298_rev:-0}" -ge 7 ] 2>/dev/null || { bad "[${PF_NO}] 🔴 节气年表缓存代次低于 v7"; S298_BAD=1; }
grep -q "public void roundTripWithFormatter()" "${S298_W}/boundless/src/test/java/boundless/utility/PositionUtilityDegreeMinuteTest.java" 2>/dev/null \
  && grep -q "longitudeMinutesAreSixtiethsOfDegree" "${S298_W}/astrostudy/src/test/java/spacex/astrostudy/model/RealSunTimeOffsetTest.java" 2>/dev/null \
  && grep -q "westernLateNightUsesDayOfConvertedTime" "${S298_W}/astrostudycn/src/test/java/spacex/astrostudycn/model/BaZiSolarDayPillarTest.java" 2>/dev/null \
  && grep -q "smallOffsetUnchanged" "${S298_W}/astrostudycn/src/test/java/spacex/astrostudycn/model/BaZiSolarDayPillarTest.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 测试缺解析 / 偏移 / 西部子时日柱 / 小偏移不变之一"; S298_BAD=1; }
S298_FAT="${S298_W}/astrostudyboot/target/astrostudyboot.jar"
if [ -f "${S298_FAT}" ]; then
  s298_tmp="$(mktemp -d "${PF_TMP}/s298_tmp.XXXXXX")"
  s298_bl="$(unzip -Z1 "${S298_FAT}" 'BOOT-INF/lib/boundless-*.jar' 2>/dev/null | head -1)"
  s298_cn="$(unzip -Z1 "${S298_FAT}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${s298_bl}" ] && [ -n "${s298_cn}" ]; then
    unzip -oq "${S298_FAT}" "${s298_bl}" "${s298_cn}" -d "${s298_tmp}" 2>/dev/null
    unzip -p "${s298_tmp}/${s298_bl}" boundless/utility/PositionUtility.class 2>/dev/null | strings | pipe_has "parseDegreeMinute" || { bad "[${PF_NO}] fat jar 未含 parseDegreeMinute —— 需 boundless / astrostudy / astrostudycn install + astrostudyboot clean package"; S298_BAD=1; }
    unzip -p "${s298_tmp}/${s298_cn}" spacex/astrostudycn/model/BaZi.class 2>/dev/null | strings | pipe_has "prevDay" && { bad "[${PF_NO}] fat jar 的 BaZi 仍含 prevDay —— 需 astrostudycn install + astrostudyboot clean package"; S298_BAD=1; }
  fi
  rm -rf "${s298_tmp}"
fi
[ "${S298_BAD}" = "0" ] && ok "[${PF_NO}] 经纬度串「度 + 分 / 60」/ 日柱不另减一天 / 年表缓存 v7 / 测试 / 运行时 jar 在位"
}

seg_300() {
# [${PF_NO}] 八字「南半球月令」设置:缺省不对冲(八字主盘现状),两个引擎都按它算(本地 flipMonthPillar / 后端 BaZi.southMonthFlip,
#       缺省 false);/bazi/birth、/bazi/direct 按请求参数;二十四节气页显式对冲,保持其帮助文档写明的南纬对调。锚住防回潮(2026-09-27)。
echo "[${PF_NO}] 南半球月令设置(两引擎同口径)"
S300_BAD=0
S300_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S300_CN="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/main/java/spacex/astrostudycn"
grep -q '<div className="horosa-field-label">南半球月令</div>' "${S300_UI}/components/cntradition/CnTraditionInput.js" 2>/dev/null \
  && grep -q "southMonth: (this.state.baziOpt && this.state.baziOpt.southMonth) || 'none'," "${S300_UI}/components/cntradition/BaZi.js" 2>/dev/null \
  && grep -q "(prev.southMonth || 'none') !== (opt.southMonth || 'none')" "${S300_UI}/components/cntradition/BaZi.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 八字页缺「南半球月令」控件 / 请求参数 / 改后重排"; S300_BAD=1; }
grep -q "{ name: 'southMonth', label: '南半球月令'" "${S300_UI}/utils/techniqueMountSettings.js" 2>/dev/null \
  && grep -q "southMonth: baziOptFromRecord(record, 'southMonth', 'none')," "$(pf_src_set "${S300_UI}/utils/aiAnalysisContext.js")" 2>/dev/null || { bad "[${PF_NO}] 🔴 AI 挂载缺南半球月令 / 取盘参数未转发"; S300_BAD=1; }
grep -q "function flipMonthPillar(hybrid, base){" "${S300_UI}/utils/baziLunarLocal.js" 2>/dev/null \
  && grep -q "export function isSouthLatitude(params){" "${S300_UI}/utils/baziLunarLocal.js" 2>/dev/null \
  && grep -q "'gender', 'southMonth'\];" "${S300_UI}/utils/baziLunarLocal.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 本地引擎缺对冲实现 / 南纬判定 / 核心缓存键未含 southMonth"; S300_BAD=1; }
grep -q "transient protected boolean southMonthFlip = false;" "${S300_CN}/model/BaZi.java" 2>/dev/null \
  && grep -q 'if(this.southMonthFlip && lat.toLowerCase().contains("s")) {' "${S300_CN}/model/BaZi.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 Java 南纬月柱又成无条件对冲(或缺开关)"; S300_BAD=1; }
for s300_c in BaZiBirthController PaiBaZiController; do
  grep -q 'bz.setSouthMonthFlip("chong".equals(params.get("southMonth")));' "${S300_CN}/controller/${s300_c}.java" 2>/dev/null \
    && grep -q 'map.put("southMonth", "chong".equals(TransData.getValueAsString("southMonth")) ? "chong" : "none");' "${S300_CN}/controller/${s300_c}.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 ${s300_c} 未按参数设南半球月令(或未进缓存键)"; S300_BAD=1; }
done
[ "$(grep -c "bz.setSouthMonthFlip(true);" "${S300_CN}/controller/JieQiController.java" 2>/dev/null)" -ge 2 ] || { bad "[${PF_NO}] 🔴 节气页未显式对冲(其帮助文档写明南纬月柱对调)"; S300_BAD=1; }
grep -q "AI 快照:南纬盘标明月令口径" "${S300_UI}/utils/__tests__/baziSouthMonth.test.js" 2>/dev/null \
  && grep -q "southFlipWhenRequested" "${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudycn/src/test/java/spacex/astrostudycn/model/BaZiSouthMonthTest.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 缺南半球月令测试(前端 / Java)"; S300_BAD=1; }
S300_FAT="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar"
if [ -f "${S300_FAT}" ]; then
  s300_cn="$(unzip -Z1 "${S300_FAT}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${s300_cn}" ]; then
    s300_tmp="$(mktemp -d "${PF_TMP}/s300_tmp.XXXXXX")"; unzip -oq "${S300_FAT}" "${s300_cn}" -d "${s300_tmp}" 2>/dev/null
    unzip -p "${s300_tmp}/${s300_cn}" spacex/astrostudycn/model/BaZi.class 2>/dev/null | strings | pipe_has "setSouthMonthFlip" || { bad "[${PF_NO}] fat jar 未含 setSouthMonthFlip —— 需 astrostudycn install + astrostudyboot clean package"; S300_BAD=1; }
    rm -rf "${s300_tmp}"
  fi
fi
[ "${S300_BAD}" = "0" ] && ok "[${PF_NO}] 南半球月令:界面 / 请求 / 挂载 / 本地引擎 / Java 缺省不对冲 / 节气页显式对冲 / 测试 / 运行时 jar 在位"
}

seg_72() {
# ============================================================================
# [${PF_NO}] 择日西方深化:五档流派轴 + 默认档零回归守卫 + golden 锚 + 数据完整性
#   默认(现代主流)输出与 golden 逐字一致;modern_main extraWeights 必须为空
#   (空表 = 新增分析模块不进默认总分,评分构成与既往字节不变)。
# ============================================================================
S72_BAD=0
S72_DIR="${REPO_ROOT}/Horosa-Web/astrostudyui/src/divination"
S72_WS="${S72_DIR}/election/westernSchools.js"
S72_SNAP="${S72_DIR}/election/__tests__/__snapshots__/electionGolden.test.js.snap"
echo "[${PF_NO}] 择日西方深化(流派轴·golden·28宿·交映)"
[ -f "${S72_WS}" ] || { bad "[${PF_NO}] 缺 westernSchools.js 流派真值源"; S72_BAD=1; }
for s72k in modern_main hellenistic persian renaissance modern_revival; do
	grep -q "${s72k}: {" "${S72_WS}" 2>/dev/null || { bad "[${PF_NO}] 流派档缺失: ${s72k}"; S72_BAD=1; }
done
awk '/modern_main: \{/,/\},/' "${S72_WS}" 2>/dev/null | pipe_has "extraWeights: {}," || { bad "[${PF_NO}] 🔴 modern_main extraWeights 非空(默认总分构成被改=零回归破坏)"; S72_BAD=1; }
awk '/modern_main: \{/,/\},/' "${S72_WS}" 2>/dev/null | pipe_has "hsys: null" || { bad "[${PF_NO}] modern_main 宫制联动未保持 null(默认不得改用户宫制)"; S72_BAD=1; }
[ -f "${S72_SNAP}" ] || { bad "[${PF_NO}] 缺 electionGolden 快照(默认输出法律)"; S72_BAD=1; }
[ -f "${S72_DIR}/election/__tests__/electionFixture.js" ] || { bad "[${PF_NO}] 缺 golden 固定盘 fixture"; S72_BAD=1; }
S72_MANSIONS=$(grep -c "{ n: " "${S72_DIR}/data/lunarMansions.js" 2>/dev/null || true)
[ "${S72_MANSIONS}" = "28" ] || { bad "[${PF_NO}] lunarMansions 应 28 条,实际 ${S72_MANSIONS}"; S72_BAD=1; }
grep -q "360 / 28" "${S72_DIR}/data/lunarMansions.js" 2>/dev/null || { bad "[${PF_NO}] 28 宿缺 Agrippa 均分锚"; S72_BAD=1; }
S72_EGY=$(grep -oE "\[[0-9]+, [0-9]+\]" "${S72_DIR}/data/egyptianDays.js" 2>/dev/null | wc -l | tr -d ' ')
[ "${S72_EGY}" = "12" ] || { bad "[${PF_NO}] 埃及凶日应 12 月×2 日,实际 ${S72_EGY} 组"; S72_BAD=1; }
grep -q "tanφ·tanδ" "${S72_DIR}/engine/paransLocal.js" 2>/dev/null || { bad "[${PF_NO}] paransLocal 缺公式口径注释"; S72_BAD=1; }
grep -q "riseHourAngle" "${S72_DIR}/engine/paransLocal.js" 2>/dev/null || { bad "[${PF_NO}] paransLocal 缺升落时角"; S72_BAD=1; }
grep -q "\['sun', 10\]" "${S72_DIR}/engine/timeLords.js" 2>/dev/null || { bad "[${PF_NO}] Firdaria 昼表缺日10"; S72_BAD=1; }
grep -q "capricorn: 27, aquarius: 30" "${S72_DIR}/engine/timeLords.js" 2>/dev/null || { bad "[${PF_NO}] ZR 小年表锚缺(摩羯27/水瓶30)"; S72_BAD=1; }
grep -q "§" "${S72_DIR}/election/electionSnapshot.js" 2>/dev/null && { bad "[${PF_NO}] 快照文本含 § 内部章节引用"; S72_BAD=1; }
[ "${S72_BAD}" = "0" ] && ok "[${PF_NO}] 择日西方深化 全在位" || bad "[${PF_NO}] 择日西方深化 有缺失"
}

seg_124() {
# ---- [124] 推运盘星体白名单防线(历史事故:
#      根因:星运页三个推运 TabPane 漏传 planetDisplay 等显示 props,
#      AstroDoubleChart/AstroChart 把「漏传(undefined)」当「空白名单」→ 双盘有框架无星体,
#      且 dev 源码恒正常(props 齐)——只有打包产物坏,preview 永远测不出。
#      判据:推运盘 svg texts=64(坏)/250(好)。防线两层:①三 TabPane 显式传 planetDisplay
#      ②两 chart 组件对漏传回落 DEFAULT_OBJECTS/DEFAULT_LOTS(漏传≠全空盘)。) ----
S124_BAD=0
S124_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
echo "[124] 推运盘星体白名单(漏传≠全空盘)"
S124_CNT=$({ grep -c "planetDisplay={this.props.planetDisplay}" "${S124_UI}/src/components/direction/AstroDirectMain.js" 2>/dev/null || echo 0; } | tail -1)
[ "${S124_CNT}" -ge 6 ] || { bad "[124] AstroDirectMain planetDisplay 透传少于 6 处(推运 TabPane 漏传回潮,现=${S124_CNT})"; S124_BAD=1; }
grep -q "DEFAULT_OBJECTS" "${S124_UI}/src/components/astro/AstroDoubleChart.js" 2>/dev/null || { bad "[124] AstroDoubleChart 缺 planetDisplay 漏传回落(空盘回潮)"; S124_BAD=1; }
grep -q "DEFAULT_OBJECTS" "${S124_UI}/src/components/astro/AstroChart.js" 2>/dev/null || { bad "[124] AstroChart 缺 planetDisplay 漏传回落(空盘回潮)"; S124_BAD=1; }
[ "${S124_BAD}" = "0" ] && ok "[124] 推运 TabPane 透传×${S124_CNT}+双 chart 组件漏传回落 全在位"
}

seg_179() {
# [${PF_NO}] 干支年基准 / 性别接线 / AI 输出预算键 三合一锁：
#   ①术数流年 base 必须是干支年(立春前出生者用公历年会整体错一年);
#   ②左栏性别下拉须宿主下发 + 组件 props 优先(曾恒读命盘性别=死开关);
#   ③AI 输出预算键走单源 maxTokensKeyForModel + 后端代际归一(gpt-5+ 不收 max_tokens)。
echo "[${PF_NO}] 干支年基准 + 性别接线 + AI 预算键代际(三合一)"
S179_BAD=0
S179_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S179_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"
[ -f "${S179_UI}/utils/ganzhiYearBase.js" ] || { S179_BAD=1; bad "[${PF_NO}]① 缺干支年基准单源 utils/ganzhiYearBase.js"; }
for F in components/shusuan/HeLuoMain.js components/shusuan/CanPingMain.js utils/aiAnalysisContext.js; do
    grep -aq "ganzhiYearBase(" "$(pf_src_set "${S179_UI}/${F}")" 2>/dev/null || { S179_BAD=1; bad "[${PF_NO}]① ${F} 未经 ganzhiYearBase(立春前出生者流年会整体错一年)"; }
done
grep -aq "gender={this.state.gender}" "${S179_UI}/components/kinastro/KinAstroMain.js" 2>/dev/null || { S179_BAD=1; bad "[${PF_NO}]② 宿主未下发 gender(左栏性别成死开关)"; }
for F in components/shusuan/CanPingMain.js components/shusuan/ZhengChuanMain.js components/shusuan/HeLuoMain.js; do
    grep -aq "this.props.gender !== undefined" "${S179_UI}/${F}" 2>/dev/null || { S179_BAD=1; bad "[${PF_NO}]② ${F} 未 props.gender 优先"; }
done
grep -aq "maxTokensKeyForModel" "${S179_UI}/utils/aiAnalysisProviders.js" 2>/dev/null || { S179_BAD=1; bad "[${PF_NO}]③ 缺 AI 预算键单源 maxTokensKeyForModel"; }
S179_TOKFILES="components/aianalysis/AIAnalysisMain.js"
for F in ${S179_TOKFILES}; do
    grep -aq "maxTokensKeyForModel(protoFamily, model)" "$(pf_src_set "${S179_UI}/${F}")" 2>/dev/null || { S179_BAD=1; bad "[${PF_NO}]③ ${F} 未走预算键单源(新代 OpenAI 会恒吃 400)"; }
done
grep -aq "normalizeOpenAIMaxTokensKey" "${S179_JAVA}" 2>/dev/null || { S179_BAD=1; bad "[${PF_NO}]③ Java 代理缺代际归一(providerOptions.max_tokens 会原样上线)"; }
[ -f "${S179_UI}/utils/__tests__/ganzhiYearBaseGuard.test.js" ] || { S179_BAD=1; bad "[${PF_NO}] 缺 jest 金标 ganzhiYearBaseGuard"; }
[ "${S179_BAD}" = "0" ] && ok "[${PF_NO}] 三合一锁全绿(干支年 base · 性别接线 · AI 预算键代际)"
}

seg_299() {
# [${PF_NO}] 八字本地引擎按出生绝对时刻取年柱 / 月柱 / 交节距离:lunar-javascript 节气表按北京时间,非东八区须把(真太阳时换算后的)
#       出生时刻折成北京时间去取年 / 月与交节,日柱 / 时柱仍按当地钟表;东八区原样(逐字节不变)。锚住防回潮(2026-09-27)。
echo "[${PF_NO}] 八字本地引擎按绝对时刻换月(非东八区)"
S299_BAD=0
S299_L="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/baziLunarLocal.js"
S299_T="${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/__tests__/baziAbsoluteTimeJie.test.js"
grep -q "function absoluteTimeLunar(localLunar, localSolar, zone" "${S299_L}" 2>/dev/null \
  && grep -qF "export function shiftSolarMinutes(solar, minutes){" "${REPO_ROOT}/Horosa-Web/astrostudyui/src/utils/beijingTimeShift.js" 2>/dev/null \
  && pf_imports "${S299_L}" "import { parseZoneHours, bjShiftMinutes, shiftSolarMinutes } from './beijingTimeShift';" \
  && pf_imports "${S299_L}" "import { Solar, LunarUtil, Lunar, LunarMonth, EightChar } from 'lunar-javascript';" || { bad "[${PF_NO}] 🔴 本地引擎缺按绝对时刻的农历(absoluteTimeLunar / shiftSolarMinutes / EightChar)"; S299_BAD=1; }
[ "$(grep -c "const baziLunar = absoluteTimeLunar(lunar, solar, params && params.zone" "${S299_L}" 2>/dev/null)" -ge 2 ] \
  && [ "$(grep -c "buildNongli(lunar, solar, solar, ziweiLunar, baziLunar)" "${S299_L}" 2>/dev/null)" -ge 2 ] \
  && grep -q "const prevJie = baziLunar.getPrevJie();" "${S299_L}" 2>/dev/null || { bad "[${PF_NO}] 🔴 完整版 / 奇门轻量版 / 节后天数 / 月律分野 未全部改走绝对时刻"; S299_BAD=1; }
grep -q "东八区不变(对照)" "${S299_T}" 2>/dev/null && grep -q "巴黎 / 纽约芒种后 2 时 14 分出生" "${S299_T}" 2>/dev/null \
  && grep -q "奇门扫描用轻量版同口径" "${S299_T}" 2>/dev/null || { bad "[${PF_NO}] 🔴 测试缺海外换月 / 东八区对照 / 轻量版同口径"; S299_BAD=1; }
[ "${S299_BAD}" = "0" ] && ok "[${PF_NO}] 八字本地引擎按绝对时刻换月(完整版 + 轻量版 + 节后天数 + 分野)+ 测试在位"
}

seg_302() {
echo "[${PF_NO}] 历法口径统一:时刻串秒进位 / 八字农历随时间算法 / 交节精确时刻 / 北京农历表 / 各模块按当地钟表比节气"
S302_BAD=0
S302_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S302_SRV="${REPO_ROOT}/Horosa-Web/astrostudysrv"
S302_PY="${REPO_ROOT}/Horosa-Web/astropy"
S302_DT="${S302_SRV}/boundless/src/main/java/boundless/utility/DateTimeUtility.java"
S302_NL="${S302_SRV}/astrostudy/src/main/java/spacex/astrostudy/helper/NongliHelper.java"
S302_CN="${S302_SRV}/astrostudycn/src/main/java/spacex/astrostudycn"
# ① 时刻串:秒四舍五入到 60 逐级进位,进到 24:00:00 日期同步进一天(不再出 xx:xx:60、整点时辰不再判早)
grep -qF 'if(s >= 60) {' "${S302_DT}" 2>/dev/null && grep -qF 'long[] dt = calDateFromJdn(tparts[0] > 0 ? locjdn + 1 : locjdn);' "${S302_DT}" 2>/dev/null \
  && grep -qF 'if(Math.abs(delta) > 0.5 / 86400.0 + 0.00000001) {' "${S302_DT}" 2>/dev/null || { bad "[${PF_NO}] 🔴 Java 时刻串秒数进位被改回(会再出 :60,整点时辰判早一个)"; S302_BAD=1; }
# ② 八字类农历日期 / 节后天数 / 人元司令随所选时间算法(真太阳时档不动;标为真太阳时的一行仍给真太阳时)
[ "$(grep -cF 'this.alignNongliWithTimeAlg(realSunBirth);' "${S302_CN}/model/BaZi.java" 2>/dev/null)" -eq 1 ] \
  && grep -qF 'map.put("birth", trueSolarBirth);' "${S302_CN}/model/BaZi.java" 2>/dev/null || { bad "[${PF_NO}] 🔴 八字农历又恒按真太阳时(或真太阳时一行被改)"; S302_BAD=1; }
# ③ 交节时刻:求解目标为节气黄经本身;节气时刻显示四舍五入到秒;缓存代次随之升级
for s302_f in BirthJieQi YearJieQi; do
  [ "$(grep -cF '+ 1/7200' "${S302_PY}/astrostudy/jieqi/${s302_f}.py" 2>/dev/null)" = "0" ] || { bad "[${PF_NO}] 🔴 ${s302_f} 交节求解又加了 1/7200°(交节晚约 12 秒)"; S302_BAD=1; }
done
grep -qF 'def cnTimeRounded(tm):' "${S302_PY}/astrostudy/jieqi/jieqiconst.py" 2>/dev/null \
  && [ "$(grep -cF 'jieqiconst.cnTimeRounded(newtm)' "${S302_PY}/astrostudy/jieqi/BirthJieQi.py" 2>/dev/null)" -ge 3 ] \
  && [ "$(grep -cF 'jieqiconst.cnTimeRounded(newtm)' "${S302_PY}/astrostudy/jieqi/YearJieQi.py" 2>/dev/null)" -ge 2 ] || { bad "[${PF_NO}] 🔴 节气时刻显示不再四舍五入到秒"; S302_BAD=1; }
[ "$(grep -cF 'params.put("_v", "w5");' "${S302_SRV}/astrostudy/src/main/java/spacex/astrostudy/helper/AstroHelper.java" 2>/dev/null)" -ge 2 ] \
  && grep -qF 'params.put("_v", "w6");' "${S302_SRV}/astrostudy/src/main/java/spacex/astrostudy/helper/AstroHelper.java" 2>/dev/null \
  && [ "$(grep -cF 'params.put("_v", "w5");' "${S302_SRV}/astrostudy/src/main/java/spacex/astrostudy/helper/BaZiHelper.java" 2>/dev/null)" -ge 2 ] \
  && [ "$(grep -cF 'w6", date, zone);' "${S302_SRV}/astrostudy/src/main/java/spacex/astrostudy/helper/AstroCacheHelper.java" 2>/dev/null)" -ge 2 ] || { bad "[${PF_NO}] 🔴 节气 / 农历请求缓存代次未升级(老缓存会返回晚 12 秒的交节)"; S302_BAD=1; }
# ④ 农历按北京时间编算的农历表、以出生地日期查;月末换月东八区原逻辑、其他时区只比日期;朔时刻标北京时间
[ "$(grep -cF 'getNongliMonths(year, NONGLI_TABLE_ZONE, ctx);' "${S302_NL}" 2>/dev/null)" = "1" ] \
  && grep -qF 'getNongliMonths(nexty + "", NONGLI_TABLE_ZONE, ctx);' "${S302_NL}" 2>/dev/null \
  && grep -qF 'if(isNongliTableZone(zone)) {' "${S302_NL}" 2>/dev/null \
  && [ "$(grep -cF 'dtNum = DateTimeUtility.getDateNum(dt+" 00:00:00", zone);' "${S302_NL}" 2>/dev/null)" -ge 2 ] \
  && grep -qF 'moonTime = moonTime + "（北京时间）";' "${S302_NL}" 2>/dev/null || { bad "[${PF_NO}] 🔴 农历又按出生地时区求朔(海外农历日差一天)或月末换月比较错位"; S302_BAD=1; }
# ⑤ 结果缓存键带历法口径代次(升级后不返回旧口径结果),且不发给排盘引擎
grep -qF 'public static final String CALENDAR_CACHE_REV' "${S302_NL}" 2>/dev/null \
  && [ "$(grep -cF 'NongliHelper.CALENDAR_CACHE_REV' "${S302_CN}/controller/LiuRengController.java" 2>/dev/null)" -eq 2 ] \
  && grep -qF 'NongliHelper.CALENDAR_CACHE_REV' "${S302_CN}/controller/BaZiBirthController.java" 2>/dev/null \
  && grep -qF 'NongliHelper.CALENDAR_CACHE_REV' "${S302_CN}/controller/PaiBaZiController.java" 2>/dev/null \
  && [ "$(grep -cF 'args.remove("_calRev");' "${S302_CN}/controller/ChartController.java" 2>/dev/null)" -eq 3 ] || { bad "[${PF_NO}] 🔴 八字 / 六壬 / 七政结果缓存缺历法口径代次(升级后一天内返回旧口径)"; S302_BAD=1; }
# ⑥ 前端各模块按当地钟表比节气(节气种子 / 奇门 / 节气页本地回退 / 河洛页与挂载同源)
grep -qF 'export function shiftSolarMinutes(solar, minutes){' "${S302_UI}/utils/beijingTimeShift.js" 2>/dev/null \
  && pf_imports "${S302_UI}/utils/baziLunarLocal.js" "import { parseZoneHours, bjShiftMinutes, shiftSolarMinutes } from './beijingTimeShift';" \
  && grep -qF 'const toLocal = -bjShiftMinutes(zone);' "${S302_UI}/utils/localNongliAdapter.js" 2>/dev/null \
  && grep -qF 'export function heluoSolarTermOfDate(dateStr, zone, quHuaGong) {' "${S302_UI}/utils/heluoLocal.js" 2>/dev/null \
  && grep -qF "return heluoSolarTermOfDate(dateStr, zone, this.props.quHuaGong || 'tuWangKunGen');" "${S302_UI}/components/shusuan/HeLuoMain.js" 2>/dev/null \
  && grep -qF 'return heluoSolarTermOfDate(dateStr, zone, quHuaGong);' "$(pf_src_set "${S302_UI}/utils/aiAnalysisContext.js")" 2>/dev/null || { bad "[${PF_NO}] 🔴 节气种子 / 河洛又拿当地钟表比北京时间节气(非东八区交节前后判错)"; S302_BAD=1; }
# ⑦ 测试在位(Java / Python / 前端)
[ -f "${S302_SRV}/boundless/src/test/java/boundless/utility/DateTimeUtilitySecondCarryTest.java" ] \
  && [ -f "${S302_SRV}/astrostudycn/src/test/java/spacex/astrostudycn/model/BaZiNongliTimeAlgTest.java" ] \
  && [ -f "${S302_SRV}/astrostudycn/src/test/java/spacex/astrostudycn/model/NongliBeijingTableTest.java" ] \
  && [ -f "${S302_PY}/tests/test_jieqi_exact_longitude.py" ] \
  && [ -f "${S302_UI}/utils/__tests__/beijingTimeJieqiCrossModule.test.js" ] || { bad "[${PF_NO}] 🔴 缺历法口径测试(Java / Python / 前端)"; S302_BAD=1; }
# 置闰:按日期定冬至所在月(不再「该月不是从 12 月起就后挪一个月」→ 2033 等年凭空闰秋月、与次年表前后矛盾)
grep -qF "prevdz0 = self.prevDongZi['tm'].calcZeroHourJd()" "${S302_PY}/astrostudy/jieqi/NongLi.py" 2>/dev/null \
  && [ "$(grep -cF "if dparts[1] != '12' and dparts[2] != '01':" "${S302_PY}/astrostudy/jieqi/NongLi.py" 2>/dev/null)" = "0" ] \
  && [ -f "${S302_PY}/tests/test_nongli_leap_month.py" ] || { bad "[${PF_NO}] 🔴 农历置闰又按「非 12 月起就后挪」定冬至所在月(2033 年误成闰七月)"; S302_BAD=1; }
# ⑧ 运行时 jar 在位
S302_FAT="${S302_SRV}/astrostudyboot/target/astrostudyboot.jar"
if [ -f "${S302_FAT}" ]; then
  s302_as="$(unzip -Z1 "${S302_FAT}" 'BOOT-INF/lib/astrostudy-*.jar' 2>/dev/null | head -1)"
  s302_cn="$(unzip -Z1 "${S302_FAT}" 'BOOT-INF/lib/astrostudycn-*.jar' 2>/dev/null | head -1)"
  if [ -n "${s302_as}" ] && [ -n "${s302_cn}" ]; then
    s302_tmp="$(mktemp -d "${PF_TMP}/s302_tmp.XXXXXX")"; unzip -oq "${S302_FAT}" "${s302_as}" "${s302_cn}" -d "${s302_tmp}" 2>/dev/null
    unzip -p "${s302_tmp}/${s302_as}" spacex/astrostudy/helper/NongliHelper.class 2>/dev/null | strings | pipe_has "isNongliTableZone" || { bad "[${PF_NO}] fat jar 未含 isNongliTableZone —— 需 astrostudy install + astrostudyboot clean package"; S302_BAD=1; }
    unzip -p "${s302_tmp}/${s302_cn}" spacex/astrostudycn/model/BaZi.class 2>/dev/null | strings | pipe_has "alignNongliWithTimeAlg" || { bad "[${PF_NO}] fat jar 未含 alignNongliWithTimeAlg —— 需 astrostudycn install + astrostudyboot clean package"; S302_BAD=1; }
    rm -rf "${s302_tmp}"
  fi
fi
[ "${S302_BAD}" = "0" ] && ok "[${PF_NO}] 历法口径统一:秒进位 / 农历随时间算法 / 交节精确 / 北京农历表 / 缓存代次 / 当地钟表比节气 / 测试 / 运行时 jar 在位"
}

seg_70() {
# [${PF_NO}] 占星地图(ACG)全流派:引擎 golden(validate_acg 对 swisseph 独立反验,退0)+
#      三层透传(Java AcgController 白名单是唯一闸门,漏登=前端参数静默丢)+ 前端接线。
#      默认全零回归(所有新参数 opt-in:mode/lsMode/geodetic/cuspLines/coord/ayanamsa/stars/ccg*/rel*)。
S70_BAD=0
S70_PY="${REPO_ROOT}/Horosa-Web/astropy"
S70_ENG="${S70_PY}/astrostudy/acg/ACGraph.py"
S70_VAL="${S70_PY}/astrostudy/acg/validate_acg.py"
S70_SRV="${S70_PY}/websrv/webacgsrv.py"
S70_JAVA="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/AcgController.java"
S70_FE="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/acg/AstroAcg.js"
S70_MAP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/acg/AcgD3Map.js"
echo "[${PF_NO}] 占星地图 ACG 全流派(口径/线型/坐标系/CCG/关系盘/固定星/寻宝图)"
for f in "${S70_ENG}" "${S70_VAL}" "${S70_SRV}" "${S70_JAVA}" "${S70_FE}" "${S70_MAP}"; do
  [ -f "${f}" ] || { bad "[${PF_NO}] 缺文件 ${f#${REPO_ROOT}/}"; S70_BAD=1; }
done
# 引擎能力面(方法在位)
for fn in "_aspectLines" "_eastWestLines" "_antisciaLines" "_vertexLines" "_cuspLines" "_lotsLines" "_midpointLines" "_geodeticLines" "_crossings" "_starLines" "_starParans" "_ccgLines" "findMundaneEvent" "_lsRhumb"; do
  grep -q "${fn}" "${S70_ENG}" 2>/dev/null || { bad "[${PF_NO}] ACGraph 缺 ${fn}"; S70_BAD=1; }
done
# Java 白名单(唯一闸门)—— 含全流派补齐 P0 天体集/口径底座新键
for p in "mode" "lsMode" "geodetic" "cuspLines" "coord" "ayanamsa" "stars" "ccgDate" "ccgMix" "relMode" "relDate" "asteroids" "nodeType" "lilithType" "posType" "horizon"; do
  grep -q "containsParam(\"${p}\")" "${S70_JAVA}" 2>/dev/null || { bad "[${PF_NO}] AcgController 白名单缺 ${p}"; S70_BAD=1; }
done
# P0 引擎能力面:小行星直算 + 交点/月孛切换 + 站心/真位置/J2000 读数 + 折射
for m in "ASTEROID_SWE" "nodeType" "lilithType" "posType" "horizon" "_j2000Lon" "FLG_TOPOCTR" "TRUE_NODE" "_minorKepler" "MINOR_ELEMENTS"; do
  grep -q "${m}" "${S70_ENG}" 2>/dev/null || { bad "[${PF_NO}] ACGraph 缺 P0 标记 ${m}"; S70_BAD=1; }
done
# P1 引擎能力面:龙黄道/谐波/振动线/自定义Lots/中点四线mundo/LS盘面/关系交叉
for m in "self.draconic" "self.harmonicH" "_vibrationLines" "_customLot" "midpointMode" "_lsAzAlt" "_relCrossings" "_crossParans"; do
  grep -q "${m}" "${S70_ENG}" 2>/dev/null || { bad "[${PF_NO}] ACGraph 缺 P1 标记 ${m}"; S70_BAD=1; }
done
# P3/P4 引擎能力面:geodeticZero 偏移 + 落点 8 敏感点
for m in "self.geodeticZero" "'sensitive'"; do
  grep -q "${m}" "${S70_ENG}" 2>/dev/null || { bad "[${PF_NO}] ACGraph 缺 P3/P4 标记 ${m}"; S70_BAD=1; }
done
# P4 含义多表(逐格 planet×角):interpretations.zh.js PLANET_ANGLE
S70_INTERP="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/acg/interpretations.zh.js"
grep -q "PLANET_ANGLE" "${S70_INTERP}" 2>/dev/null || { bad "[${PF_NO}] interpretations 缺 P4 逐格 PLANET_ANGLE"; S70_BAD=1; }
# P0/P1 golden 必在 validate 里(独立 swe/azalt 反验)
for c in "check_celestial" "check_p1"; do
  grep -q "${c}" "${S70_VAL}" 2>/dev/null || { bad "[${PF_NO}] validate_acg 缺 ${c}"; S70_BAD=1; }
done
grep -q '"/acgevent"' "${S70_JAVA}" 2>/dev/null || { bad "[${PF_NO}] AcgController 缺 /acgevent 端点"; S70_BAD=1; }
grep -q "def acgevent" "${S70_SRV}" 2>/dev/null || { bad "[${PF_NO}] webacgsrv 缺 acgevent 路由"; S70_BAD=1; }
# 前端接线(genParams 下发 + 地图渲染层)—— 含 P0/P1 新键
for p in "ayanamsa:" "coord:" "stars:" "ccgDate" "relMode" "posType:" "horizon:" "nodeType:" "lilithType:" "asteroids:" "draconic:" "harmonic:" "vibration:" "midpointMode:" "lotsCustom:" "relZone" "geodeticZero:"; do
  grep -q "${p}" "${S70_FE}" 2>/dev/null || { bad "[${PF_NO}] AstroAcg 缺参数接线 ${p}"; S70_BAD=1; }
done
# P1 地图渲染层:振动线 + 关系交叉;polish:影响带 + 正射投影
for m in "showVibration" "showRelCross" "showZones" "geoOrthographic"; do
  grep -q "${m}" "${S70_MAP}" 2>/dev/null || { bad "[${PF_NO}] AcgD3Map 缺渲染 ${m}"; S70_BAD=1; }
done
# polish:LS 罗盘盘面组件
S70_DIAL="${REPO_ROOT}/Horosa-Web/astrostudyui/src/components/acg/AcgCompassDial.js"
[ -f "${S70_DIAL}" ] || { bad "[${PF_NO}] 缺 LS 罗盘盘面 AcgCompassDial.js"; S70_BAD=1; }
grep -q "drawTreasure" "${S70_MAP}" 2>/dev/null || { bad "[${PF_NO}] AcgD3Map 缺寻宝图热力层 drawTreasure"; S70_BAD=1; }
grep -q "data.second" "${S70_MAP}" 2>/dev/null || { bad "[${PF_NO}] AcgD3Map 缺双人叠加层(data.second)"; S70_BAD=1; }
grep -q "data.ccg" "${S70_MAP}" 2>/dev/null || { bad "[${PF_NO}] AcgD3Map 缺 CCG 层(data.ccg)"; S70_BAD=1; }
# 🔴 核心可执行护栏:validate_acg 全量 golden(swisseph 独立反验)必须退 0
if [ "${S70_BAD}" = "0" ] && command -v python3 >/dev/null 2>&1 && [ "${HOROSA_ACG_PREFLIGHT_SKIP:-0}" != "1" ]; then
  S70_OUT="$(cd "${S70_PY}" 2>/dev/null && PYTHONPATH="../flatlib-ctrad2:." python3 astrostudy/acg/validate_acg.py 2>&1)" || {
    bad "[${PF_NO}] 🔴 validate_acg golden 未退0: $(printf '%s' "${S70_OUT}" | tail -2 | head -1)"; S70_BAD=1; }
  printf '%s' "${S70_OUT}" | pipe_has "ACG alignment PASS" || { bad "[${PF_NO}] validate_acg 输出无 PASS"; S70_BAD=1; }
fi
[ "${S70_BAD}" = "0" ] && ok "[${PF_NO}] 占星地图 引擎golden+白名单+前端接线 在位" || bad "[${PF_NO}] 占星地图 护栏 有缺失"
}

seg_33() {
# [33] 主限法方位+时间补全·strategy 分发完整性 + 前端选项扩 (含铺满/盘宫制/label 收口)
#  - perchart.py: pdMethod 白名单与本仓核验集一致 + pdDirect 解析
#  - 前端 primaryDirectionSync.js: PD_SYNC_REV = 'pd_method_sync_v15' + SUPPORTED_PD_METHODS(核验集)
#  - 后端 helper.py / webchartsrv.py: PD_SYNC_REV 对齐 v10(否则新盘恒误判重算)
#  - pd_engine.py: build_directions + solar_arc_for_years(真太阳弧动态钥匙逆函数)
#  - 表格工具栏单行(无 advanced 第二行,不遮表格);TabPane 名「主限法」
#  - AstroPrimaryDirectionChart.js getTablePdTimeKey 不再强制降级 Naibod
#  - aiAnalysisContext.js 主限法 case 不再硬编码覆盖 pdMethod/pdTimeKey
echo "[33] 主限法方位+时间补全·strategy 分发 + 前端选项扩 (v10+v11)"
PD33_BAD=0
PERCHART="$(pf_src_set "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perchart.py")"
PD_SYNC="${UISRC}/utils/primaryDirectionSync.js"
if [ -f "${PD_SYNC}" ]; then
  if ! grep -q "pd_method_sync_v15" "${PD_SYNC}"; then
    bad "[33] primaryDirectionSync.js PD_SYNC_REV 未升到 'pd_method_sync_v15' —— 旧缓存不重算,新 方位法/世俗/顺逆/真太阳弧 不生效"
    PD33_BAD=1
  fi
  if ! grep -q "SUPPORTED_PD_METHODS" "${PD_SYNC}"; then
    bad "[33] primaryDirectionSync.js 缺 SUPPORTED_PD_METHODS 白名单"
    PD33_BAD=1
  fi
  # 方位法(核验核集 + 象限四法)须在前端白名单(否则下拉选了被 normalize 回退默认)
  for m in meridian porphyry equal_ecliptic equal_hour_circle placidus regiomontanus campanus topocentric; do
    grep -q "'${m}'" "${PD_SYNC}" || { bad "[33] primaryDirectionSync.js SUPPORTED_PD_METHODS 缺 '${m}'"; PD33_BAD=1; }
  done
fi
# v10:后端 PD_SYNC_REV 必须与前端一致(均 v10),否则每张新盘首查都误判需重算
for f in "${REPO_ROOT}/Horosa-Web/astropy/astrostudy/helper.py" "${REPO_ROOT}/Horosa-Web/astropy/websrv/webchartsrv.py"; do
  [ -f "$f" ] && { grep -q "pd_method_sync_v15" "$f" || { bad "[33] 后端 $(basename $f) PD_SYNC_REV 未对齐到 v11(与前端不一致→新盘恒误判重算)"; PD33_BAD=1; }; }
done
# perchart 白名单含上面同一组方位法 + pdDirect 解析存在(顺逆同选)
if [ -f "${PERCHART}" ]; then
  for m in meridian porphyry equal_ecliptic equal_hour_circle placidus regiomontanus campanus topocentric; do
    grep -q "'${m}'" "${PERCHART}" || { bad "[33] perchart.py pdMethod 白名单缺 '${m}'"; PD33_BAD=1; }
  done
  grep -q "pdDirect" "${PERCHART}" || { bad "[33] perchart.py 缺 pdDirect 解析(顺向 direct,顺逆同选的前提)"; PD33_BAD=1; }
fi
# v10:pd_engine 必备(动态真太阳弧逆函数 solar_arc_for_years + 世俗数值法)
PD_ENGINE="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/pd_engine.py"
if [ -f "${PD_ENGINE}" ]; then
  grep -q "def solar_arc_for_years" "${PD_ENGINE}" || { bad "[33] pd_engine.py 缺 solar_arc_for_years(盘的真太阳弧动态钥匙,否则盘把 TrueSolarArc 当 Ptolemy)"; PD33_BAD=1; }
  grep -q "def build_directions" "${PD_ENGINE}" || { bad "[33] pd_engine.py 缺 build_directions"; PD33_BAD=1; }
else
  bad "[33] 缺 pd_engine.py —— 主限法时间钥匙引擎(真太阳弧/太阳弧动态钥匙)不存在"; PD33_BAD=1
fi
# v10:主限法表格工具栏须为单行(无第二行,否则遮挡表格);tab 名为「主限法」
PD_TABLE="${UISRC}/components/astro/AstroPrimaryDirection.js"
if [ -f "${PD_TABLE}" ]; then
  grep -q "horosa-primary-direction-toolbar-advanced" "${PD_TABLE}" && { bad "[33] AstroPrimaryDirection.js 仍有第二行工具栏(advanced)—— 会遮挡表格,须并回单行"; PD33_BAD=1; }
fi
DIRECT_MAIN="${UISRC}/components/direction/AstroDirectMain.js"
if [ -f "${DIRECT_MAIN}" ] && grep -q 'tab="主/界限法"' "${DIRECT_MAIN}"; then
  bad "[33] AstroDirectMain.js 主限法 TabPane 仍名「主/界限法」,应改为「主限法」"
  PD33_BAD=1
fi
# v10 真因守卫:Java getParams 必须透传 pdDirect/pdConverse/pdAntiscia/pdTerms,否则前端传了到不了 Python
#   (ParamHashCache 键=params,缺这些 → direct/converse 同哈希命中同缓存 → 「推运方向选了没用」)
PD_CTRL="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/controller/PredictiveController.java"
if [ -f "${PD_CTRL}" ]; then
  for p in pdDirect pdConverse pdAntiscia pdTerms; do
    grep -q "\"${p}\"" "${PD_CTRL}" || { bad "[33] PredictiveController.java getParams 未透传 '${p}' —— 前端选项到不了 Python(ParamHashCache 还会致顺逆同缓存,选了没用),须补 params.put + 重编 jar"; PD33_BAD=1; }
  done
  # 单源化后控制器不再含字面量:判「引用 PdWire.REV」且「PdWire 定义 = v15」(旧判据只认字面量→误红)
  if ! grep -q "PdWire.REV" "${PD_CTRL}"; then
    bad "[33] PredictiveController.java _wireRev 未引用 PdWire.REV(缓存盐单源破)"; PD33_BAD=1
  elif ! grep -q "pd_method_sync_v15" "${REPO_ROOT}/Horosa-Web/astrostudysrv/basecomm/src/main/java/spacex/basecomm/constants/PdWire.java"; then
    bad "[33] PdWire.REV 未升 v15 —— 旧 ParamHashCache 哈希不失效,新参可能读到旧缓存"; PD33_BAD=1
  fi
fi
PD_CHART="${UISRC}/components/astro/AstroPrimaryDirectionChart.js"
if [ -f "${PD_CHART}" ] && grep -qE "key === 'Naibod' \? DEFAULT_PD_TIME_KEY" "${PD_CHART}"; then
  bad "[33] AstroPrimaryDirectionChart.getTablePdTimeKey 仍强制把 Naibod 降级为 Ptolemy —— P0 起 Naibod 应直接进表格"
  PD33_BAD=1
fi
AIANALYSISCTX="$(pf_src_set "${UISRC}/utils/aiAnalysisContext.js")"
if [ -f "${AIANALYSISCTX}" ] && grep -qE "pdMethod: 'core_alchabitius'," "${AIANALYSISCTX}"; then
  bad "[33] aiAnalysisContext.js 主限法 case 仍硬编码 pdMethod='core_alchabitius' —— LLM 上下文永远显示 Alchabitius、与用户实选不符"
  PD33_BAD=1
fi
# v11:主限法盘宫制随方法(_PD_CHART_METHOD_HSYS)——盘的宫头随方位法变,缺则盘恒用本命宫制(方法选了盘不动)
PERPREDICT_V11="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/perpredict.py"
if [ -f "${PERPREDICT_V11}" ]; then
  grep -q "_PD_CHART_METHOD_HSYS" "${PERPREDICT_V11}" || { bad "[33] perpredict.py 缺 _PD_CHART_METHOD_HSYS —— 主限法盘宫头不随方位法变"; PD33_BAD=1; }
  grep -q "def _pdChartHouseSystem" "${PERPREDICT_V11}" || { bad "[33] perpredict.py 缺 _pdChartHouseSystem 解析器(盘宫制 fallback 本命制的入口)"; PD33_BAD=1; }
fi
# v11:方位法白名单与时间钥匙铺满——少一处下拉选了被 normalize 回退
if [ -f "${PD_SYNC}" ]; then
  for m in meridian porphyry equal_ecliptic equal_hour_circle; do
    grep -q "'${m}'" "${PD_SYNC}" || { bad "[33] primaryDirectionSync.js SUPPORTED_PD_METHODS 缺 v11 方位法 '${m}'"; PD33_BAD=1; }
  done
  for k in Naibod Cardano SelfMeasure; do
    grep -q "'${k}'" "${PD_SYNC}" || { bad "[33] primaryDirectionSync.js SUPPORTED_PD_TIME_KEYS 缺 v11 时间钥匙 '${k}'"; PD33_BAD=1; }
  done
fi
# 铁律:方位法以逐位核验白名单为准——前端两份白名单(同步层/方法下拉)与 Python 注册表
#   集合必须精确等于 seg_43 的核验集;pd_engine 只保留时间钥匙与共享量度原语。
PD_TABLE_OS="${UISRC}/components/astro/AstroPrimaryDirection.js"
PDENG_OS="${REPO_ROOT}/Horosa-Web/astropy/astrostudy/pd_engine.py"
PD33_TABLE="$(python3 - "${REPO_ROOT}" <<'PY33'
import re, sys
src = open(sys.argv[1] + '/Horosa-Web/astrostudyui/src/utils/primaryDirectionSync.js', encoding='utf-8').read()
m = re.search(r"SUPPORTED_PD_METHODS\s*=\s*\[(.*?)\]", src, re.S)
methods = sorted(re.findall(r"'([a-z_]+)'", m.group(1))) if m else []
print(','.join(methods))
PY33
)"
# 方位法白名单:不再硬编码期望串(主限法解禁后本仓法集会随上游增长,硬串每次都要手改)。
# 判据换成「核心必备法齐 + 非空」——真正会出的事故是误删/取不到,而不是"多了名字"。
if [ -z "${PD33_TABLE}" ]; then
  bad "[33] 取不到 SUPPORTED_PD_METHODS(解析源或常量名变了)"; PD33_BAD=1
else
  for _m in core_alchabitius meridian porphyry equal_ecliptic equal_hour_circle; do
    case ",${PD33_TABLE}," in *",${_m},"*) : ;; *) bad "[33] 方位法白名单缺核心法 '${_m}': ${PD33_TABLE}"; PD33_BAD=1 ;; esac
  done
fi
# 方位法全谱开放(2026-07-30):pd_engine 必须含闭式引擎函数(缺=功能残缺),断言随之反转。
[ -f "${PDENG_OS}" ] && ! grep -qE "^def arc_" "${PDENG_OS}" && { bad "[33] pd_engine.py 缺方位法闭式引擎函数(全谱开放后必须在位)"; PD33_BAD=1; }
# v11:AI 导出/挂载快照方法名必走共享 label 字典——AstroDirectMain 的 method/timeKey 文本函数不能再有 'Alchabitius' 字面回退
if [ -f "${DIRECT_MAIN}" ]; then
  grep -q "getPdMethodLabel" "${DIRECT_MAIN}" || { bad "[33] AstroDirectMain.js 未 import/使用 getPdMethodLabel —— 非默认方位法/钥匙的快照名会回退误标 Alchabitius"; PD33_BAD=1; }
  # 旧 bug 模式:primaryDirectionMethodText 内 `return 'Alchabitius'` 字面回退(非 label 字典)
  if grep -A3 "function primaryDirectionMethodText" "${DIRECT_MAIN}" | pipe_has "return 'Alchabitius'"; then
    bad "[33] AstroDirectMain.primaryDirectionMethodText 仍字面回退 'Alchabitius' —— 须 delegate 到 getPdMethodLabel(非默认选项导出/挂载会被误标)"
    PD33_BAD=1
  fi
fi
# v11:主限法盘宫制自检测试存在
PD_DIAL_TEST="${REPO_ROOT}/Horosa-Web/astropy/tests/test_pd_dial_house_system.py"
[ -f "${PD_DIAL_TEST}" ] || { bad "[33] 缺 tests/test_pd_dial_house_system.py —— 盘宫制随方法的自检守卫缺失"; PD33_BAD=1; }
[ "${PD33_BAD}" = "0" ] && ok "[33] strategy 分发 + 前端白名单精确集 + 盘宫制随方法 + 共享 label 字典 + AI 上下文实选透传 均到位"
}
