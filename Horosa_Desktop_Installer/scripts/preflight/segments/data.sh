#!/usr/bin/env bash
# 发布前自检 · 数据管理与选项
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。段号用 ${PF_NO}(登记表第二列)。

seg_48() {
# [48] didMount 副作用必须有清理 (2026-06-12): 持续副作用(listener/interval/observer)无
#      willUnmount = SPA 反复挂卸的累积泄漏。负向门禁,新增即红。
echo "[48] 前端挂载副作用清理"
S48_HITS="$(python3 - "${REPO_ROOT}/Horosa-Web/astrostudyui/src" <<'PY48'
import os, re, sys
root = sys.argv[1]
bad = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in ('__tests__', 'node_modules')]
    for fn in filenames:
        if not fn.endswith('.js') or fn.endswith('.test.js'):
            continue
        path = os.path.join(dirpath, fn)
        try:
            src = open(path, encoding='utf-8').read()
        except Exception:
            continue
        m = re.search(r'componentDidMount\s*\(', src)
        if not m:
            continue
        # didMount 起到下一个同级方法名的粗块
        block = src[m.start():m.start() + 4000]
        nxt = re.search(r'\n\t(?:async )?[a-zA-Z_$][\w$]*\s*\(', block[20:])
        if nxt:
            block = block[:20 + nxt.start()]
        if re.search(r'addEventListener|setInterval|new (Resize|Mutation|Intersection)Observer', block):
            if 'componentWillUnmount' not in src:
                bad.append(os.path.relpath(path, root))
print('\n'.join(sorted(bad)))
PY48
)"
[ -z "${S48_HITS}" ] && ok "[48] didMount 持续副作用均有 willUnmount" || { bad "[48] 以下组件 didMount 注册持续副作用但无 willUnmount:"; printf '%s\n' "${S48_HITS}" >&2; }
}

seg_125() {
# ---- [125] 存储配额治理(FL 级「一个都没修好」终局根因:黄历缓存写满 localStorage
#      5MB origin 级配额 → 全 App 一切 setItem 抛 QuotaExceededError → 页页炸错误卡。
#      防线:①派生缓存迁 IndexedDB(字节预算+LRU,与 5MB 绝缘)+首启迁移清尸键
#      ②全站裸 localStorage.setItem 白名单制(新增裸写=红)③错误卡 quota 自愈按钮
#      ④quota 注错金标。) ----
S125_BAD=0
S125_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
echo "[125] 存储配额治理(缓存分层+裸写白名单+自愈)"
# ① 缓存分层:localCalcCache 走 IndexedDB 后端+迁移器
grep -q "idbCacheStore" "${S125_UI}/src/utils/localCalcCache.js" 2>/dev/null || { bad "[125] localCalcCache 未走 IndexedDB 后端(5MB 定时炸弹回潮)"; S125_BAD=1; }
grep -q "migrateLegacyLocalStorage" "${S125_UI}/src/utils/localCalcCache.js" 2>/dev/null || { bad "[125] 缺首启迁移器(老设备尸键不清)"; S125_BAD=1; }
grep -q "TOTAL_BUDGET_BYTES" "${S125_UI}/src/utils/idbCacheStore.js" 2>/dev/null || { bad "[125] idbCacheStore 缺字节预算(磁盘无限膨胀)"; S125_BAD=1; }
# ② 裸 setItem 白名单:只允许 safeStorage/deferredStorage(自带 quota 防线)出现裸写
S125_BARE=$(grep -rln "localStorage\.setItem" "${S125_UI}/src" --include="*.js" 2>/dev/null | grep -v "__tests__" | grep -v "safeStorage.js" | grep -v "deferredStorage.js" | head -5)
[ -z "${S125_BARE}" ] || { bad "[125] 发现白名单外裸 localStorage.setItem(须走 safeStorage): ${S125_BARE}"; S125_BAD=1; }
# ③ 错误卡 quota 自愈
grep -q "clearRecoverableCaches" "${S125_UI}/src/components/common/TechniqueErrorBoundary.js" 2>/dev/null || { bad "[125] 错误卡缺 quota 一键清理自愈"; S125_BAD=1; }
# ④ quota 注错金标
[ -f "${S125_UI}/src/utils/__tests__/storageQuotaGuard.test.js" ] || { bad "[125] 缺 quota 注错回归金标"; S125_BAD=1; }
[ "${S125_BAD}" = "0" ] && ok "[125] 缓存分层+迁移器+字节预算+裸写白名单+自愈+金标 全在位"
}

seg_126() {
# ---- [126] 盘面可见性重画+失败泊车(推运/恒星推运「表新盘旧」根治。
#      根因:antd Tabs 切换只切 CSS(children element 引用不变→React bail out,子树零 render);
#      隐藏期(svg 0×0,draw 尺寸早退)数据已更新的 d3 手绘盘切回后无任何重画触发 → 盘停旧数据、
#      右表已是新数据,永久不吻合。防线:①watchChartSvgResize(ResizeObserver,0→非0 必重画)
#      ②四个无自愈路径的 chart 组件挂接 ③load 失败绝不记 key 为已完成(失败泊车,窗口期后重试)
#      ④可见性重画+泊车金标。铁律:「隐藏期 0×0 不记签名」必须搭配变可见重画触发器。) ----
S126_BAD=0
S126_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
echo "[126] 盘面可见性重画+失败泊车(表盘严格吻合)"
# ① 共享工具在位
grep -q "export function watchChartSvgResize" "${S126_UI}/src/utils/chartDrawGuard.js" 2>/dev/null || { bad "[126] chartDrawGuard 缺 watchChartSvgResize(隐藏盘切回不重画回潮)"; S126_BAD=1; }
# ② 四个无自愈路径组件挂接(AstroDoubleChart/AstroChart=案发地;JinKouChart/GuaZhanChart=同病)
for S126_F in astro/AstroDoubleChart.js astro/AstroChart.js jinkou/JinKouChart.js guazhan/GuaZhanChart.js; do
	grep -q "watchChartSvgResize" "${S126_UI}/src/components/${S126_F}" 2>/dev/null || { bad "[126] ${S126_F} 未挂可见性重画"; S126_BAD=1; }
done
# ③ 推运面板+三容器 失败泊车(catch 记 key=表盘永久分叉)
grep -q "parkLoadFailure" "${S126_UI}/src/components/astro/AstroProgChart.js" 2>/dev/null || { bad "[126] ProgMethodPanel 缺失败泊车(load 失败吞更新回潮)"; S126_BAD=1; }
for S126_C in AstroProgressions AstroVedicProgressions AstroJaynesProgressions; do
	grep -q "parkLoadFailure" "${S126_UI}/src/components/astro/${S126_C}.js" 2>/dev/null || { bad "[126] ${S126_C} 缺失败泊车"; S126_BAD=1; }
done
# ④ 金标在位
[ -f "${S126_UI}/src/utils/__tests__/chartVisibilityRedraw.test.js" ] || { bad "[126] 缺可见性重画+泊车金标"; S126_BAD=1; }
[ "${S126_BAD}" = "0" ] && ok "[126] 可见性重画工具+4组件挂接+失败泊车×4+金标 全在位"
}

seg_258() {
# seg_258 前端源码零未声明标识符(Babel 作用域静态扫全 src;ReferenceError 机械网)
#   事故:手工维护的大文件里少了一行 `const xxxRef = React.useRef(null)`、别处还传着 xxxRef —— 语法合法、构建照过、
#   单测不渲染该组件照绿,只有真打开页面才整页白;另一处 `pdtype: DEFAULT_PD_TYPE` 漏 import 被 try/catch 吞成「段落恒降级」。
#   脚本内有存量棘轮表(只减不增)+ --self-test 判别向量(一红一绿)。
echo "[${PF_NO}] 前端源码零未声明标识符(ReferenceError 机械网)"
S258_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S258_JS="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/check_undefined_identifiers.js"
if [ ! -f "${S258_JS}" ]; then bad "[${PF_NO}] 缺 check_undefined_identifiers.js"
elif [ ! -d "${S258_UI}/node_modules/@babel/traverse" ]; then bad "[${PF_NO}] 缺 @babel/traverse(先在 astrostudyui 里 npm install)"
else
  S258_ST="$(node "${S258_JS}" "${S258_UI}" --self-test 2>&1)" || { echo "${S258_ST}" | sed 's/^/    /'; bad "[${PF_NO}] 静态扫描判别向量自证失败(网本身坏了)"; }
  S258_OUT="$(node "${S258_JS}" "${S258_UI}" . 2>&1)"; S258_RC=$?
  if [ "${S258_RC}" = "0" ]; then ok "[${PF_NO}] $(echo "${S258_OUT}" | tail -1 | sed 's/^✅ //')"
  else echo "${S258_OUT}" | tail -12 | sed 's/^/    /'; bad "[${PF_NO}] 前端源码有新增未声明标识符(整页 ReferenceError 白屏类;见上)"; fi
fi
}

seg_281() {
# ── seg_281 随盘键「新盘种子」(新命盘缺省 = 上次亲手设的值;载入记录不播;捕获按内建默认)──────────────────────
# 由来:占星黄道 / 宫制、时间算法、八字长生 / 神煞、宿法、印占选项、主限法口径写在 astro.fields,新盘 / 重开软件一律回出厂值(与「排盘设置
#   改了重开又回去」同一体感)。单源件 utils/newChartSeeds.js;四条语义由 newChartSeeds.test.js 逐条锁,本闸锁资产与接线在位。
echo "[${PF_NO}] 随盘键「新盘种子」:单源件 + 模型 / 还原接线 + 亲手改动入口 + 合同测试"
S281_BAD=0
S281_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
for S281_F in "${S281_UI}/utils/newChartSeeds.js" "${S281_UI}/utils/__tests__/newChartSeeds.test.js"; do
  [ -f "${S281_F}" ] || { bad "[${PF_NO}] 🔴 资产缺失:${S281_F#${REPO_ROOT}/}"; S281_BAD=1; }
done
grep -qF "...newChartSeedExtraEntries()," "${S281_UI}/models/astro.js" || { bad "[${PF_NO}] 🔴 newEmptyFields 不再展开种子(schema 没有的种子键回不到新盘)"; S281_BAD=1; }
S281_N="$(grep -c "value: newChartSeedValue('" "${S281_UI}/models/astro.js" 2>/dev/null || true)"
[ "${S281_N:-0}" -ge 16 ] || { bad "[${PF_NO}] 🔴 newEmptyFields 读种子的键少于 16(现 ${S281_N:-0}):有键退回写死初值"; S281_BAD=1; }
grep -qF "fields = resetNewChartSeedKeysToInternalDefaults(fields);" "${S281_UI}/utils/recordFieldsRestore.js" || { bad "[${PF_NO}] 🔴 载入记录不再复位种子键(记录会被种子污染)"; S281_BAD=1; }
grep -qF "isNewChartSeedKey(key) ? newChartSeedInternalDefault(key)" "${S281_UI}/utils/recordFieldsRestore.js" || { bad "[${PF_NO}] 🔴 捕获不再按内建默认判种子键(与种子同值的口径不落库 → 换机漂移)"; S281_BAD=1; }
for S281_A in "pages/index.js:seedNewCharts" "components/astro/AstroChartMain.js:if(this.props.seedNewCharts){ recordNewChartSeeds(patch); }" \
  "components/cntradition/BaZi.js:recordNewChartSeeds(" "components/ziwei/ZiWeiMain.js:!this.props.techniqueScope && patch.timeAlg !== undefined" \
  "components/sanshi/SanShiUnitedMain.js:if(this.usesSavedSettings()){ recordNewChartSeeds(" "components/suzhan/SuZhanInput.js:recordNewChartSeeds({ doubingSu28: val });" \
  "components/astro/IndiaChartMain.js:recordNewChartSeeds(patch);" "components/direction/AstroDirectMain.js:pdMethod, pdTimeKey, pdtype: normalizePdType(opt.pdtype)," \
  "components/homepage/PageHeader.js:时间算法（新命盘的缺省）"; do
  S281_F="${S281_UI}/${S281_A%%:*}"
  [ -f "${S281_F}" ] && grep -qF "${S281_A#*:}" "$(pf_src_set "${S281_F}")" || { bad "[${PF_NO}] 🔴 亲手改动入口没记种子:${S281_A%%:*}"; S281_BAD=1; }
done
grep -qF "'horosa.chart.newChartSeeds.v1'" "${S281_UI}/utils/storageKeyRegistry.js" || { bad "[${PF_NO}] 🔴 存储键未登记(备份面缺它 = 迁机即丢)"; S281_BAD=1; }
[ "${S281_BAD}" = "0" ] && ok "[${PF_NO}] 新盘种子:单源件 / 模型与还原接线 / 九处入口 / 存储键登记 全在位"
}

seg_282() {
echo "[${PF_NO}] 盘面随界面主题重画:单源订阅 + 宿主普查 + 合同锁"
S282_BAD=0
S282_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
S282_TEST="${S282_UI}/utils/__tests__/chartThemeFollow.contract.test.js"
for S282_F in "${S282_UI}/utils/appearance.js" "${S282_UI}/utils/chartDrawGuard.js" "${S282_TEST}"; do
  [ -f "${S282_F}" ] || { bad "[${PF_NO}] 🔴 资产缺失:${S282_F#${REPO_ROOT}/}"; S282_BAD=1; }
done
grep -qF "currentChartThemeKey()" "${S282_UI}/utils/chartDrawGuard.js" 2>/dev/null || { bad "[${PF_NO}] 🔴 绘制签名不含主题指纹 currentChartThemeKey()"; S282_BAD=1; }
if [ -f "${S282_TEST}" ]; then
  pf_test_disabled "${S282_TEST}" && { bad "[${PF_NO}] 🔴 合同测试有被跳过 / 被独占的用例(源码级三锁被整体关闭)"; S282_BAD=1; }
  for S282_T in "🔴 ① 每个宿主组件都挂 watchChartAppearance(" "🔴 ② 组件里零私自观察 data-horosa-appearance" "🔴 applyAppearanceToDocument:调色板先到位" "🔴 订阅:同帧多信号合并一次" "🔴 watchChartAppearance:重画回调在调色板切换之后" "🔴 ④ 组件树零模块级调色板烘焙" "🔴 ⑥ 零实例字段调色板烘焙" "🔴 ⑤ render 期读调色板的宿主,主题回调必须重渲染"; do
    grep -qF "${S282_T}" "${S282_TEST}" || { bad "[${PF_NO}] 🔴 合同测试缺锁:${S282_T}"; S282_BAD=1; }
  done
  # 浅色配色档(宣纸 / 经典白)也算主题:订阅与绘制签名都按主题指纹比(读 CSS 变量烘焙颜色的盘切档必重画)
  for S282_T in "🔴 浅色配色档(宣纸 ↔ 经典白)也算主题变化" "🔴 绘制签名含配色档"; do
    grep -qF "${S282_T}" "${S282_TEST}" || { bad "[${PF_NO}] 🔴 合同测试缺锁:${S282_T}"; S282_BAD=1; }
  done
  grep -qF "const HOST_RE = /AstroColor\\.|d3\\.select\\(|getContext\\('2d'\\)|new [A-Z]\\w*Chart\\(|new FengShuiEngine\\(/;" "${S282_TEST}" \
    || { bad "[${PF_NO}] 🔴 合同测试的宿主判据正则被改(与本闸普查不同文;改判据须两处同改)"; S282_BAD=1; }
fi
# 独立于 jest 的第二把锁:同一判据正则 + 同一豁免表(豁免必须两处同时写,且理由针仍在文件里)
S282_RES="$(python3 - "${S282_UI}" <<'PY'
import json, os, re, sys
src = sys.argv[1]; comp = os.path.join(src, 'components')
HOST_RE = re.compile(r"AstroColor\.|d3\.select\(|getContext\('2d'\)|new [A-Z]\w*Chart\(|new FengShuiEngine\(")
ALLOW = {
  'components/lrzhan/LiuRengMain.js': 'owner: null',
  'components/sanshi/SanShiUnitedMain.js': 'owner: null',
  'components/xuanshi/XuanShiPersons.js': 'var(--horosa',
  'components/fengshui/FengShuiMain.js': 'new FengShuiEngine(canvas',
}
# 拆成子模块的大文件按一个整体普查(登记表 astrostudyui/scripts/source-sets.json):子模块折回门面、门面按全集读,判据口径与拆分前同
try: SETS = json.load(open(os.path.join(src, '..', 'scripts', 'source-sets.json'), encoding='utf-8'))['sets']
except Exception: SETS = {}
PARTS = {'%s/%s' % (v['dir'], f) for v in SETS.values() for f in v['files']}
def read(p):
    rel = os.path.relpath(p, src).replace(os.sep, '/')
    files = [os.path.join(src, SETS[rel]['dir'], f) for f in SETS[rel]['files']] + [p] if rel in SETS else [p]
    try: return ''.join(open(x, encoding='utf-8').read() for x in files)
    except Exception: return ''
problems = []; hosts = 0
for root, dirs, files in os.walk(comp):
    dirs[:] = [d for d in dirs if d != '__tests__']
    for fn in files:
        if not fn.endswith('.js'): continue
        p = os.path.join(root, fn); rel = os.path.relpath(p, src)
        if rel.replace(os.sep, '/') in PARTS: continue
        s = read(p)
        if re.search(r"attributeFilter:\s*\[[^\]]*data-horosa-appearance", s): problems.append('私自观察外观属性:' + rel)
        if ('componentDidMount' in s or 'useEffect(' in s) and HOST_RE.search(s):
            hosts += 1
            if 'watchChartAppearance(' in s: continue
            if rel in ALLOW:
                if ALLOW[rel] not in s: problems.append('豁免理由已不成立:' + rel)
                continue
            problems.append('宿主未挂 watchChartAppearance(:' + rel)
for rel in ALLOW:
    p = os.path.join(src, rel)
    if os.path.isfile(p) and 'watchChartAppearance(' in read(p): problems.append('已接线却仍在豁免表:' + rel)
for root, dirs, files in os.walk(src):
    dirs[:] = [d for d in dirs if d not in ('__tests__', '.umi', '.umi-production')]
    for fn in files:
        if not fn.endswith('.js'): continue
        p = os.path.join(root, fn); rel = os.path.relpath(p, src)
        if rel in ('utils/appearance.js', 'constants/AstroConst.js') or rel.replace(os.sep, '/') in PARTS: continue
        if 'setColorTheme(' in read(p): problems.append('调色板在单源之外被切:' + rel)
for rel in ('layouts/app.js', 'pages/index.js'):
    if 'syncChartPalette(resolvedAppearance)' not in read(os.path.join(src, rel)): problems.append('render 站点不再同步调色板:' + rel)
ap = read(os.path.join(src, 'utils', 'appearance.js'))
i1 = ap.find('syncChartPalette(actual)'); i2 = ap.find("setAttribute('data-horosa-appearance'"); i3 = ap.find('dispatchEvent(new CustomEvent(APPEARANCE_APPLIED_EVENT')
if not (0 <= i1 < i2 < i3): problems.append('applyAppearanceToDocument 顺序不再是 调色板 → 根属性 → 广播')
if 'data-appearance-toggle="1"' not in read(os.path.join(src, 'components', 'homepage', 'PageHeader.js')): problems.append('主题钮审计锚缺失')
min_hosts = 15
if hosts < min_hosts: problems.append('宿主普查只数到 %d 个(判据失效或目录被挪)' % hosts)
print('; '.join(problems) if problems else 'ok:%d' % hosts)
PY
)"
case "${S282_RES}" in
  ok:*) [ "${S282_BAD}" = "0" ] && ok "[${PF_NO}] ${S282_RES#ok:} 个盘面宿主全挂单源订阅 / 调色板只在 utils/appearance.js 切 / 零私抄观察器 / 合同八锁在位" ;;
  *) bad "[${PF_NO}] 🔴 源码普查:${S282_RES}"; S282_BAD=1 ;;
esac
}

seg_261() {
# [${PF_NO}] 进阶页控件登记网(「写了键、没人读」一族):每个 data-* 控件必登记(锚/存储/消费方符号/端到端判据),检查器自证判别力;
#   D1-D5 负锚:短调用消费方禁再硬编码 'off' 思考档(槽参数死开关回潮)、目标自检按 judge 槽解析、外部客户端策略控件在位、细项档数不写死「八档」。
echo "[${PF_NO}] 进阶页控件登记表(锚↔登记↔消费方↔端到端判据)+ 死开关四修负锚"
S261_BAD=0
S261_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
S261_JS="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/check_adv_controls_registry.js"
[ -f "${S261_JS}" ] || { bad "[${PF_NO}] 缺 check_adv_controls_registry.js"; S261_BAD=1; }
[ -f "${S261_UI}/src/components/aianalysis/chat/advancedControls.registry.json" ] || { bad "[${PF_NO}] 缺进阶页控件登记表 advancedControls.registry.json"; S261_BAD=1; }
if [ "${S261_BAD}" = "0" ]; then
  S261_ST="$(node "${S261_JS}" "${S261_UI}" --self-test 2>&1)" || { echo "${S261_ST}" | tail -4 | sed 's/^/    /'; bad "[${PF_NO}] 登记表检查器判别向量自证失败(网本身坏了)"; S261_BAD=1; }
  S261_OUT="$(node "${S261_JS}" "${S261_UI}" 2>&1)"; S261_RC=$?
  [ "${S261_RC}" = "0" ] || { echo "${S261_OUT}" | tail -12 | sed 's/^/    /'; bad "[${PF_NO}] 进阶页控件登记表不合(源码锚未登记/消费方缺/端到端用例 id 缺/棘轮)"; S261_BAD=1; }
fi
S261_HOOKS=("${S261_UI}/src/components/aianalysis/chat/useChatBestOf.js" "${S261_UI}/src/components/aianalysis/chat/useChatReview.js" "${S261_UI}/src/components/aianalysis/chat/useChatOrchestrate.js" "${S261_UI}/src/utils/aiAgent/goalRunner.js")
S261_OFF=""; S261_SLOT=0
for S261_F in "${S261_HOOKS[@]}"; do
  S261_HIT="$(grep -nE "providerOptions \|\| \{\}\) \}, 'off'" "${S261_F}" 2>/dev/null | grep -vE ":[0-9]+:[[:space:]]*//" || true)"
  [ -z "${S261_HIT}" ] || S261_OFF="${S261_OFF}${S261_F}:${S261_HIT}
"
  S261_N="$(grep -c "providerOptionsForSlot(" "${S261_F}" 2>/dev/null || true)"; S261_SLOT=$(( S261_SLOT + ${S261_N:-0} ))
done
[ -z "${S261_OFF}" ] || { bad "[${PF_NO}] 短调用消费方又硬编码 'off' 思考档(判官/审阅/规划/子任务槽参数死开关回潮):"; echo "${S261_OFF}" | head -3 | sed 's/^/      /'; S261_BAD=1; }
[ "${S261_SLOT}" -ge 6 ] || { bad "[${PF_NO}] providerOptionsForSlot 调用 ${S261_SLOT} < 6(判官/合并/审阅/规划/子任务/目标自检 六处须走单源)"; S261_BAD=1; }
grep -aqF "resolveHeadlessSlot('judge'" "${S261_UI}/src/utils/aiAgent/goalRunner.js" || { bad "[${PF_NO}] 目标任务自检未按 judge 槽解析(说明书承诺落空)"; S261_BAD=1; }
[ "$(grep -acF 'data-external-policy-approval="1"' "${S261_UI}/src/components/aianalysis/ExternalAgentPanel.js")" = "1" ] || { bad "[${PF_NO}] 外部客户端策略控件锚 data-external-policy-approval 须恰一处"; S261_BAD=1; }
grep -aq "setExternalPolicy(" "${S261_UI}/src/components/aianalysis/ExternalAgentPanel.js" || { bad "[${PF_NO}] 外部客户端策略控件没有写入方(setExternalPolicy)"; S261_BAD=1; }
grep -aq "八档" "${S261_UI}/src/utils/aiChat/policyPanel.js" "${REPO_ROOT}/docs/AI_AGENT_RUNTIME.md" 2>/dev/null && { bad "[${PF_NO}] 「八档」写死回潮(细项档数只认 FIELD_SPECS.length)"; S261_BAD=1; }
[ -f "${S261_UI}/src/utils/__tests__/aiAdvancedControlsRegistry.test.js" ] || { bad "[${PF_NO}] 缺登记表 reveal 合同测试 aiAdvancedControlsRegistry.test.js"; S261_BAD=1; }
[ -f "${S261_UI}/src/utils/__tests__/externalPolicyPanel.test.js" ] || { bad "[${PF_NO}] 缺外部客户端策略控件测试"; S261_BAD=1; }
[ -f "${S261_UI}/src/utils/__tests__/aiModelRoutingSlotOptions.test.js" ] || { bad "[${PF_NO}] 缺槽参数单源测试"; S261_BAD=1; }
for S261_T in externalServersPanel aiAdvancedCrossWindow aiChatPolicyPanel; do [ -f "${S261_UI}/src/utils/__tests__/${S261_T}.test.js" ] || { bad "[${PF_NO}] 缺 ${S261_T}.test.js"; S261_BAD=1; }; done
# D7:槽输出上限必须经 maxTokensKeyForModel 落家族键(o 系 max_completion_tokens / gemini maxOutputTokens / ollama num_predict);裸 'o.max_tokens = s.maxTokens' 回潮 = 死格回潮
grep -aqF "maxTokensKeyForModel(getProviderProtocolFamily(providerType), model)] = s.maxTokens" "${S261_UI}/src/utils/aiModelRouting.js" || { bad "[${PF_NO}] applySlotParams 输出上限未经 maxTokensKeyForModel 单源(o 系/gemini/ollama 槽上限死格回潮)"; S261_BAD=1; }
grep -aqE "^\s*o\.max_tokens = s\.maxTokens" "${S261_UI}/src/utils/aiModelRouting.js" && { bad "[${PF_NO}] applySlotParams 又裸写 o.max_tokens = s.maxTokens"; S261_BAD=1; }
# D8:上下文策略卡「恢复现状」按「键存在」门控(不再按 preset==='legacy' 反判)
grep -aqF "disabled={!stored}" "${S261_UI}/src/components/aianalysis/chat/ChatContextPolicyPanel.js" || { bad "[${PF_NO}] 上下文策略「恢复现状」门控未按 hasStoredContextPolicy(缺省翻窗口后反判)"; S261_BAD=1; }
# D6/D9/D10(2026-09-07):跨窗口 storage 转发六处、invokeOptional 数组包 value、turn.end 有人发
S261_ST_N=$(grep -acF "window.addEventListener('storage', sh)" "${S261_UI}/src/utils/aiModelRouting.js" "${S261_UI}/src/utils/aiChat/persona.js" "${S261_UI}/src/utils/aiChat/personaLayers.js" "${S261_UI}/src/utils/aiChatHistory.js" 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}')
[ "${S261_ST_N:-0}" -ge 6 ] || { bad "[${PF_NO}] 进阶页六类订阅的跨窗口 storage 转发缺(${S261_ST_N:-0}/6;第二窗口卡片陈旧)"; S261_BAD=1; }
grep -aqF "!Array.isArray(r) ? r : { value: r }" "${S261_UI}/src/utils/aiAnalysisDesktop.js" || { bad "[${PF_NO}] invokeOptional 又把数组结果展开(外部服务器清单永远空表,D9)"; S261_BAD=1; }
grep -aqF "emitAutomationEvent('turn.end'" "$(pf_src_set "${S261_UI}/src/components/aianalysis/AIAnalysisMain.js")" || { bad "[${PF_NO}] 「一轮对话结束」事件没人发(自动规则 turn.end 死档,D10)"; S261_BAD=1; }
# D11(真模型磁带实抓):结构化短调用空正文第三级降级 —— 审阅/判官/规划与综合三处必须经 requestStructuredWithFallback(DeepSeek 把输出写进 reasoning_content、content 为空)
S261_SF_N=$(grep -acF "requestStructuredWithFallback(requestAIAnalysisChat" "${S261_UI}/src/components/aianalysis/chat/useChatReview.js" "${S261_UI}/src/components/aianalysis/chat/useChatBestOf.js" "${S261_UI}/src/components/aianalysis/chat/useChatOrchestrate.js" 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}')
[ "${S261_SF_N:-0}" -ge 3 ] || { bad "[${PF_NO}] 结构化短调用空正文降级缺(${S261_SF_N:-0}/3;/审阅 在 DeepSeek 上恒「没有返回合法 JSON」)"; S261_BAD=1; }
[ "${S261_BAD}" = "0" ] && ok "[${PF_NO}] 进阶页控件登记网:检查器自证/全锚登记/消费方在/D1-D10 负锚/六测在位"
}

seg_278() {
# ── [${PF_NO}] 技法页「排盘设置跨会话保留」制度(用户实报:排盘设置改了之后每次重开软件都要重设) ──────────
# 病症:各技法页的排盘口径历来只活在组件 state 里,关掉软件再开就回出厂值;而「这一页哪些选项该保留」从来没有一张表 ——
#   新页整页漏掉、老页加了新选项也没人想起来。另有两种更隐蔽的同族:① 改动时写了存储、首开却从不读回(七政四项);
#   ② 同一张卡里一个控件写全局、旁边那个只改本地 state(辅盘盘壳的外环样式)。
# 制度三件:单源件(声明 schema → load / save,校验严格、读端永不抛)· 登记表(每页保留哪些键 / 哪些键带理由不保留)·
#   合同测试(页面里每个用户可改键都已表态;登记表 ≡ 活 schema;候选值与缺省同类型)。本闸锁这三件在位、不被掏空。
echo "[${PF_NO}] 技法页排盘设置跨会话保留:单源件 + 登记表 + 合同测试"
S278_BAD=0
S278_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
for S278_F in \
  "${S278_UI}/utils/pageSettingsStore.js" "${S278_UI}/utils/pageSettingsRegistry.js" \
  "${S278_UI}/utils/divinationShellSettings.js" "${S278_UI}/utils/directionPageSettings.js" \
  "${S278_UI}/utils/__tests__/pageSettingsStore.test.js" "${S278_UI}/utils/__tests__/pageSettingsRegistry.contract.test.js" \
  "${S278_UI}/utils/__tests__/directionPageSettings.test.js"; do
  [ -f "${S278_F}" ] || { bad "[${PF_NO}] 🔴 制度资产缺失:${S278_F#${REPO_ROOT}/}"; S278_BAD=1; }
done
# 合同测试不许被掏空:四条要害断言的标题必须在
S278_CT="${S278_UI}/utils/__tests__/pageSettingsRegistry.contract.test.js"
if [ -f "${S278_CT}" ]; then
  for S278_A in "页面里用户可改的每个选项键都已表态" "登记表 fields 与页面 schema 的键逐个相同" "schema 自洽(活对象)" "落盘键已登记为 settings 且进备份面" "凡用盘壳的页,黄道 / 宫制的亲手改动都接到了落盘"; do
    grep -qF "${S278_A}" "${S278_CT}" || { bad "[${PF_NO}] 🔴 合同测试被掏空:缺「${S278_A}」"; S278_BAD=1; }
  done
fi
# 单源件的三条纪律:值形态严格(不做宽松转换)· 读端永不抛 · 稀疏覆盖层
S278_ST="${S278_UI}/utils/pageSettingsStore.js"
if [ -f "${S278_ST}" ]; then
  grep -qF "if(typeof value !== t){ return { ok: false }; }" "${S278_ST}" || { bad "[${PF_NO}] 🔴 单源件的严格类型校验被改(0 ≠ false、'1' ≠ 1 是死开关的防线)"; S278_BAD=1; }
  grep -qF "if(spec.sparse){" "${S278_ST}" || { bad "[${PF_NO}] 🔴 单源件的稀疏覆盖层分支丢失"; S278_BAD=1; }
  S278_N="$(grep -c "safeLocalStorage\(Get\|Set\|Remove\)" "${S278_ST}" 2>/dev/null || true)"
  [ "${S278_N:-0}" -ge 3 ] || { bad "[${PF_NO}] 🔴 单源件不再走 safeStorage(配额 / 登记闸全绕过)"; S278_BAD=1; }
fi
# 盘壳:黄道 / 宫制的亲手改动必须回调宿主;外环样式必须写全局(与同卡的盘面美术同律)
S278_SH="${S278_UI}/components/divination/DivinationChartShell.js"
if [ -f "${S278_SH}" ]; then
  S278_N="$(grep -c "this.notifyUserFieldChange(" "${S278_SH}" 2>/dev/null || true)"
  [ "${S278_N:-0}" -ge 2 ] || { bad "[${PF_NO}] 🔴 盘壳左栏的黄道 / 宫制不再回调 onUserFieldChange(宿主页的落盘就此断链)"; S278_BAD=1; }
  grep -qF "payload: { chartStyle }" "${S278_SH}" || { bad "[${PF_NO}] 🔴 盘壳的外环样式又只改本地 state(不写全局 → 重开即丢)"; S278_BAD=1; }
  grep -qF "props.chartStyle : readStoredChartStyle())" "${S278_SH}" || { bad "[${PF_NO}] 🔴 盘壳的外环样式缺「宿主没传就自己读全局」的兜底(天星择日这类宿主页改了写得进、重开读不回)"; S278_BAD=1; }
fi
# 七政:首开补空必须读回全部类 A 口径(此前只读回三项,其余四项「存而不读」)
S278_GL="$(pf_src_set "${S278_UI}/components/guolao/GuoLaoChartMain.js")"
if [ -f "${S278_GL}" ]; then
  for S278_A in "['guolaoTrueSolarTime', getStoredGuolaoTrueSolarTime]" "['guolaoNodeType', getStoredGuolaoNodeType]" "['guolaoLilithType', getStoredGuolaoLilithType]" "['guolaoBodyMode', getStoredGuolaoBodyMode]"; do
    grep -qF "${S278_A}" "${S278_GL}" || { bad "[${PF_NO}] 🔴 七政首开补空漏读:${S278_A}"; S278_BAD=1; }
  done
fi
# 一身多技法的大组件:用户入口统一走 setUserOpt(落盘 + setState);入口若被改回裸 setState,整族设置静默失效
S278_KA="${S278_UI}/components/kinastro/KinAstroMain.js"
if [ -f "${S278_KA}" ]; then
  S278_N="$(grep -c "this.setUserOpt(" "${S278_KA}" 2>/dev/null || true)"
  [ "${S278_N:-0}" -ge 100 ] || { bad "[${PF_NO}] 🔴 策天 / 数算族的用户入口只剩 ${S278_N:-0} 处走 setUserOpt(应 ≥100)"; S278_BAD=1; }
  grep -qF "KINASTRO_PAGE_SETTINGS.save(patch);" "${S278_KA}" || { bad "[${PF_NO}] 🔴 setUserOpt 不再落盘"; S278_BAD=1; }
fi
# 金口诀首帧:主盘未到位时宿主传下来的是空对象 {},画盘第一步取贵人读 nongli.dayGanZi 抛错,错误边界不自愈 → 整块面板停在「加载出错」
# (曾整页进不去,查下来是页面自己崩了)。
for S278_F in "${S278_UI}/components/jinkou/JinKouChart.js" "${S278_UI}/components/jinkou/JinKouPanChart.js"; do
  if [ -f "${S278_F}" ]; then
    grep -qF "nongli.dayGanZi){" "${S278_F}" || { bad "[${PF_NO}] 🔴 金口诀画盘前的「农历日柱未到位不画」守卫丢失:${S278_F##*/}"; S278_BAD=1; }
  fi
done
# 相交处五条:保存值本身留得住,出事的是它与「载入旧案 / 择日宿主 / 没有控件的兄弟页 / 离不开输入的起法 /
# 整张覆盖层落盘」相交的地方。语义由 jest(pageSettingsCaseAndHostSemantics)看守,这里锁住要害写法不被改回。
S278_SEM="${S278_UI}/utils/__tests__/pageSettingsCaseAndHostSemantics.test.js"
[ -f "${S278_SEM}" ] || { bad "[${PF_NO}] 🔴 相交处语义测试缺失:${S278_SEM#${REPO_ROOT}/}"; S278_BAD=1; }
if [ -f "${S278_ST}" ]; then
  grep -qF "function saveMapEntry(field, subKey, value){" "${S278_ST}" || { bad "[${PF_NO}] 🔴 单源件的 saveMapEntry 丢失(map 型字段又只能整张落盘 → 旧案的子项会被存成缺省)"; S278_BAD=1; }
  grep -qF "function fillMissing(obj){" "${S278_ST}" || { bad "[${PF_NO}] 🔴 单源件的 fillMissing 丢失(事盘还原缺键无处回出厂值)"; S278_BAD=1; }
fi
if [ -f "${S278_SH}" ]; then
  grep -qF "this.props.restoreBaseline" "${S278_SH}" || { bad "[${PF_NO}] 🔴 盘壳的事盘还原不再用还原基线(旧案缺键又会沿用本机保存的流派 / 宫制 / 判读参数)"; S278_BAD=1; }
fi
for S278_F in "${S278_UI}/components/horary/HoraryMain.js" "${S278_UI}/components/election/ElectionMain.js" "${S278_UI}/components/mundane/MundaneMain.js" "${S278_UI}/components/zeri/TianxingElectionMain.js"; do
  if [ -f "${S278_F}" ]; then
    grep -qF "restoreBaseline={this._" "${S278_F}" || { bad "[${PF_NO}] 🔴 盘壳宿主页没把还原基线传给壳:${S278_F##*/}"; S278_BAD=1; }
  fi
done
for S278_F in "${S278_UI}/components/lrzhan/LiuRengMain.js" "${S278_UI}/components/taiyi/TaiYiMain.js" "${S278_UI}/components/sanshi/SanShiUnitedMain.js"; do
  if [ -f "${S278_F}" ]; then
    grep -qF "usesSavedSettings(){" "$(pf_src_set "${S278_F}")" || { bad "[${PF_NO}] 🔴 择日内嵌实例的隔离丢失(内嵌盘又会继承独立页保存值 → 点选所见 ≠ 扫描所判):${S278_F##*/}"; S278_BAD=1; }
  fi
done
for S278_F in AstroGivenYear AstroLunarReturn AstroSolarReturn AstroPersianDirected; do
  if [ -f "${S278_UI}/components/astro/${S278_F}.js" ]; then
    S278_N="$(grep -c "load().nodeRetrograde" "${S278_UI}/components/astro/${S278_F}.js" 2>/dev/null || true)"
    [ "${S278_N:-0}" -eq 0 ] || { bad "[${PF_NO}] 🔴 ${S278_F} 没有「南北交逆移」控件却读了共享保存值(看不见的设置暗中改结果)"; S278_BAD=1; }
  fi
done
if [ -f "${S278_GL}" ]; then
  grep -qF "const recordLoaded = !!(fields.cid && fields.cid.value);" "${S278_GL}" || { bad "[${PF_NO}] 🔴 七政补空不再区分「载入了记录」(记录的缺省值会被全局仓值盖掉)"; S278_BAD=1; }
fi
for S278_A in "horary/HoraryMain.js:save({ horaryOverrides: next })" "election/ElectionMain.js:save({ electionParams: next })" "geomancy/GeomancyMain.js:save({ granular: next })"; do
  S278_F="${S278_UI}/components/${S278_A%%:*}"
  if [ -f "${S278_F}" ]; then
    S278_C="$(grep -cF "${S278_A#*:}" "${S278_F}" 2>/dev/null || true)"
    [ "${S278_C:-0}" -eq 0 ] || { bad "[${PF_NO}] 🔴 整张覆盖层落盘的写法回来了:${S278_A%%:*}"; S278_BAD=1; }
  fi
done
[ "${S278_BAD}" = "0" ] && ok "[${PF_NO}] 单源件 / 登记表 / 合同测试五要害 / 盘壳回调与写全局 / 七政读回四项 / 多技法组件入口 / 相交处五条要害写法 均在位"
}
