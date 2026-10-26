#!/usr/bin/env bash
# 发布前自检 · 保密与投影
# 由 preflight/lib.sh 按登记表装载;只定义函数 seg_<id>(),不直接执行。段号用 ${PF_NO}(登记表第二列)。

seg_41() {
# [41] 已修缺陷模式负向门禁 (2026-06-10 算法/设置/渲染扫雷批)
# 这批模式都是实战修掉的 bug 形态,任何一处再现 = 回归(grep -a:部分源码含 emoji 会被 grep 误判二进制)。
echo "[41] 已修缺陷模式负向门禁"
R41_BAD=0
R41_UI="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
R41_PY="${REPO_ROOT}/Horosa-Web/astropy/astrostudy"
# 七类都是「产品代码里不许再出现」:只扫产品文件(pf_prod_hits 去掉测试目录 / 测试文件),给这些回归写行为测试时可以直接拿被禁写法当夹具
# ① antd 按钮直挂带参 handler:点击事件会被当首参串化成 "[object Object]" 发出
[ -n "$(pf_prod_hits -a "onClick={handleSend}" "${R41_UI}" js)" ] && { bad "[41] 发送按钮直挂 onClick={handleSend} 再现(事件对象会被当文本发出)"; R41_BAD=1; }
# ② 接口家族判定写死 'openai':预设实际值是 'openai-compatible',判定永假
[ -n "$(pf_prod_hits -a "protoFamily === 'openai'" "${R41_UI}" js)" ] && { bad "[41] protoFamily === 'openai' 死分支再现(应走 isOpenAiFamily)"; R41_BAD=1; }
# ③ 列表 key 用随机串(每次渲染重挂,丢焦点/白耗)。全仓存量待清(legacy 惯用法,百余处),
#    本门禁先钉「已修文件零回归」;新文件请直接用稳定 key。
for R41_F in components/calendar/NongLi.js components/calendar/NongLiMain.js components/ziwei/ZiWeiMain.js components/deeplearn/DLFeature.js components/germany/Midpoint.js components/dice/DiceMain.js; do
  grep -an "key={randomStr(" "${R41_UI}/${R41_F}" >/dev/null 2>&1 && { bad "[41] ${R41_F} 的 randomStr key 回归"; R41_BAD=1; }
done
# ④ SVG 属性拼写:stroke-dashanray 会被静默忽略
[ -n "$(pf_prod_hits -a "stroke-dashanray" "${R41_UI}" js)" ] && { bad "[41] stroke-dashanray 拼写再现(应为 stroke-dasharray)"; R41_BAD=1; }
# ⑤ 经纬度分换算公式回退:deg + 1.0/min(应为 min/60)
[ -n "$(pf_prod_hits -a "(1.0 / min)" "${R41_PY}" py)" ] && { bad "[41] 经纬度 deg+(1.0/min) 公式回退"; R41_BAD=1; }
# ⑥ 圆周距离常量回退:delta = 360 - 180
[ -n "$(pf_prod_hits -a "delta = 360 - 180" "${R41_UI}" js)" ] && { bad "[41] distanceInCircleAbs 360-180 常量回退"; R41_BAD=1; }
# ⑦ absDistance 第二窗口符号回退
[ -n "$(pf_prod_hits -a "360 - ang2 - ang1" "${R41_PY}" py)" ] && { bad "[41] absDistance 360-ang2-ang1 符号回退"; R41_BAD=1; }
[ "${R41_BAD}" = "0" ] && ok "[41] 7 类已修缺陷模式零再现"
}

seg_180() {
echo "[180] 构建产物路径脱敏(构建机用户名与仓目录名不得进 bundle)"
# 病灶(2026-08-01 v3.6.1 保密复查抓到,存量):umi 的插件注册把运行时文件的**绝对路径**
# 原样写进 bundle —— register({apply:a, path:"/Users/<用户名>/Desktop/<仓目录名>/.../runtime.tsx"}),
# 于是发布产物里同时躺着构建机用户名(PII)与本地仓目录名。禁词表扫源码扫不到它(产物不在源码树),
# 人工逐条读 diff 也看不见(产物不入 git),只有直接 grep 打包产物才现形。
S180_BAD=0
S180_UI="${REPO_ROOT}/Horosa-Web/astrostudyui"
[ -f "${S180_UI}/scripts/scrub-build-paths.js" ] || { S180_BAD=1; bad "[180] 缺脱敏脚本 scripts/scrub-build-paths.js"; }
# ① 两条构建链都必须接:漏一条 → 那个产物照样带路径
for S180_K in '"build":' '"build:file":'; do
  S180_LINE="$(grep -a "${S180_K}" "${S180_UI}/package.json" 2>/dev/null | head -1)"
  printf '%s' "${S180_LINE}" | pipe_has "scrub-build-paths" \
    || { S180_BAD=1; bad "[180] package.json ${S180_K} 未接脱敏步骤 —— 该产物会带构建机路径"; }
  # ② 顺序:必须在 write-build-info 之前(脱敏改文件内容,后写指纹才对得上产物)
  printf '%s' "${S180_LINE}" | awk '{ i=index($0,"scrub-build-paths"); j=index($0,"write-build-info"); exit !(i>0 && j>0 && i<j) }' \
    || { S180_BAD=1; bad "[180] ${S180_K} 脱敏步骤必须排在 write-build-info 之前(否则指纹与产物不符)"; }
done
# ③ 终判据:直接 grep 现有产物,残留即红(不信脚本"跑过了",只认产物本身)
for S180_D in dist dist-file; do
  if [ -d "${S180_UI}/${S180_D}" ]; then
    # 全树:扫的是构建产物目录(没有测试文件之说)
    if grep -rlaE '/(Users|home)/[A-Za-z0-9._-]+/' "${S180_UI}/${S180_D}" --include=*.js --include=*.css --include=*.html 2>/dev/null | pipe_has .; then
      S180_BAD=1; bad "[180] ${S180_D} 产物内仍有构建机绝对路径 —— 重跑 npm run build/build:file"
    fi
  fi
done
[ "${S180_BAD}" = "0" ] && ok "[180] 产物路径脱敏链完好(脚本在位·两链已接·顺序正确·产物零残留)"
}

seg_219() {
# ── [219] 源码文本文件禁裸控制字节(NUL):裸 \x00 会让 file(1) 判 data、BSD grep 判 binary
# 静默弃扫 —— 一切基于 grep 的护栏/审计/临时排查在该文件上失明(2026-08-17 实抓:
# KaTeX 占位哨兵写成裸字节,致该文件对无 -a 的 grep 完全不可见)。哨兵/分隔符一律写
# \x00 转义序列(运行时字节串等价),绝不落裸字节。──
echo "[219] 文本源码禁裸 NUL"
S219_HITS="$(cd "${REPO_ROOT}" && git ls-files -z -- '*.js' '*.jsx' '*.ts' '*.md' '*.less' '*.css' '*.json' '*.py' '*.java' '*.sh' '*.rs' '*.html' | python3 -c '
import sys
files = sys.stdin.buffer.read().split(b"\x00")
bad = []
for f in files:
    if not f:
        continue
    try:
        data = open(f, "rb").read()
    except Exception:
        continue
    if b"\x00" in data:
        bad.append(f.decode())
print("\n".join(bad))
')"
if [ -n "${S219_HITS}" ]; then
  bad "[219] 🔴 文本源码含裸 NUL 字节(grep 类护栏对其静默失明,改用 \\x00 转义): $(printf '%s' "${S219_HITS}" | tr '\n' ' ')"
else
  ok "[219] 文本源码零裸 NUL(grep 类护栏可信)"
fi
}

seg_324() {
echo "[${PF_NO}] 预检自身结构(段间不靠函数体变量传值 / 段号写错必非零退出 / 本轮临时目录 mktemp + trap / 登记表第三列与函数重名 / 测试被关掉守卫单源 / 全仓脚本出口)"
S324_BAD=0; S324_SC="${INSTALLER_ROOT}/scripts"; S324_PF="${S324_SC}/release_preflight.sh"
# ① 静态:每个段函数读到的变量都有来处(本段赋值 / 装载期常量 / 公共库 / 本段调的助手 / 带缺省值的展开)
S324_OUT="$(python3 "${S324_SC}/check_preflight_structure.py" --self-test 2>&1)" || { printf '%s\n' "${S324_OUT}" | tail -3 | sed 's/^/      /' >&2; bad "[${PF_NO}]① 段间依赖检查器自证失败"; S324_BAD=1; }
S324_OUT="$(python3 "${PF_DIR}/rs_split.py" --self-test 2>&1)" || { printf '%s\n' "${S324_OUT}" | tail -3 | sed 's/^/      /' >&2; bad "[${PF_NO}]① 壳源码产品 / 测试拆分器自证失败(preflight/rs_split.py)"; S324_BAD=1; }
S324_OUT="$(python3 "${S324_SC}/check_preflight_structure.py" 2>&1)" || { printf '%s\n' "${S324_OUT}" | head -20 | sed 's/^/      /' >&2; bad "[${PF_NO}]① 有段读「别的段函数体里赋的变量」(见上)—— --only / --from 单跑会 unbound variable"; S324_BAD=1; }
# ② 选段参数写错一律非零退出(一段没跑却报全绿 = 假绿;缺值不许退化成跑全量)。
#   子进程带 HOROSA_PF_ARGS_PROBE=1:参数一旦被放行就退 97、不跑任何段(否则校验坏掉时子进程会跑全量 / 递归调起本段)。
#   对照组:合法的本段号必须被放行(97),证明探针本身有效。
for S324_ARGS in "--only 999999" "--from 999999" "--only 999999,${PF_NO}" "--only" "--only=" "--from" "--only --from ${PF_NO}"; do
  # shellcheck disable=SC2086
  HOROSA_PF_ARGS_PROBE=1 bash "${S324_PF}" ${S324_ARGS} </dev/null >/dev/null 2>&1; S324_RC=$?
  [ "${S324_RC}" = "2" ] || { bad "[${PF_NO}]② release_preflight.sh ${S324_ARGS} 退出码 ${S324_RC}(应为 2:段号不在登记表 / 缺值必须报错)"; S324_BAD=1; }
done
HOROSA_PF_ARGS_PROBE=1 bash "${S324_PF}" --only "${PF_NO}" </dev/null >/dev/null 2>&1; S324_RC=$?
[ "${S324_RC}" = "97" ] || { bad "[${PF_NO}]② 对照组:合法段号 --only ${PF_NO} 应被放行(探针退 97),实得 ${S324_RC} —— 探针失效"; S324_BAD=1; }
#   合并段在输出里另打的子段号(登记表第四列)照输出里的号 --only 必须被放行(否则「照提示重跑一段」走不通)
S324_AL=""
for S324_X in $(printf '%s\n' "${PF_ALIASES[@]}" | tr ',' ' '); do S324_AL="${S324_X}"; break; done
if [ -n "${S324_AL}" ]; then
  HOROSA_PF_ARGS_PROBE=1 bash "${S324_PF}" --only "${S324_AL}" </dev/null >/dev/null 2>&1; S324_RC=$?
  [ "${S324_RC}" = "97" ] || { bad "[${PF_NO}]② 子段号 --only ${S324_AL}(登记表第四列)应映射到所在段并放行(探针退 97),实得 ${S324_RC}"; S324_BAD=1; }
fi
# ③ 静态:公共库不许按 $$ 拼临时文件名;本轮临时目录 mktemp -d + EXIT trap
S324_LIB="$(sed -E 's/#.*$//' "${PF_DIR}/lib.sh")"
[ "$(printf '%s\n' "${S324_LIB}" | grep -cF '$$' || true)" = "0" ] || { bad "[${PF_NO}]③ preflight/lib.sh 又按 \$\$ 拼临时文件名(中断的那轮留下的缓存会被撞号的另一轮复用)—— 一律放进 PF_TMP"; S324_BAD=1; }
for S324_KW in 'PF_TMP="$(mktemp -d ' 'trap pf_on_exit EXIT' '_pf_out="${PF_TMP}/shellrs.' '_pf_out="${PF_TMP}/srcset.' '_pf_f="${PF_TMP}/self"'; do
  [ "$(printf '%s\n' "${S324_LIB}" | grep -cF -- "${S324_KW}" || true)" != "0" ] || { bad "[${PF_NO}]③ preflight/lib.sh 缺「${S324_KW}」"; S324_BAD=1; }
done
# ④ 动态:按旧命名预置一份「死掉那轮」的假快照,本轮必须现拼(内容 = 源文件拼接);段内 unbound variable 中止 → 非零退出且临时目录清掉
S324_T="${PF_TMP}/s324"; mkdir -p "${S324_T}"
S324_RC=0
#   子进程用 set -euo pipefail:bash 3.2 在这种设定下 unbound variable 中止时 $? 是 0,EXIT trap 必须按「没走正常出口」改判 1。
TMPDIR="${S324_T}" bash -c '
  set -euo pipefail
  printf "fn main_STALE_SNAPSHOT_FROM_DEAD_RUN() {}\n" > "${TMPDIR}/horosa-preflight-shellrs.$$.$(printf "%s" "$(cd "$(dirname "$0")/../.." && pwd)" | cksum | cut -d" " -f1)"
  printf "stale\n" > "${TMPDIR}/horosa-preflight-self.$$"
  . "$(dirname "$0")/preflight/lib.sh"
  pf_load >/dev/null 2>&1
  _want="$(for f in ${PF_SHELL_RS_FILES}; do [ -f "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/$f" ] && cat "${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src/$f"; done | cksum)"
  [ "$(cksum < "$(pf_shell_rs)")" = "${_want}" ] || exit 41
  [ "$(cksum < "$(pf_shell_rs)")" = "${_want}" ] || exit 42
  _src="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src"
  _wantp="$(cd "${_src}" && python3 "${PF_RS_SPLIT}" prod ${PF_SHELL_RS_FILES} | cksum)"
  [ "$(cksum < "$(pf_shell_rs_prod)")" = "${_wantp}" ] || exit 44
  [ "$(cksum < "$(pf_shell_rs_prod)")" = "${_wantp}" ] || exit 44
  cmp -s "$(pf_self)" "${TMPDIR}/horosa-preflight-self.$$" && exit 43
  [ -s "$(pf_self)" ] || exit 43
  echo "${S324_UNSET_PROBE_VAR}"
  exit 0
' "${S324_PF}" </dev/null >/dev/null 2>&1 || S324_RC=$?
case "${S324_RC}" in
  41|42) bad "[${PF_NO}]④ pf_shell_rs 返回的不是现拼的壳源码(复用了旧快照)"; S324_BAD=1 ;;
  44) bad "[${PF_NO}]④ pf_shell_rs_prod 返回的不是现拼的产品代码(复用了旧快照,或与拆分器口径不一)"; S324_BAD=1 ;;
  43) bad "[${PF_NO}]④ pf_self 复用了旧快照"; S324_BAD=1 ;;
  0) bad "[${PF_NO}]④ 段内 unbound variable 中止却以 0 退出(假绿)"; S324_BAD=1 ;;
esac
[ "$(find "${S324_T}" -maxdepth 1 -name 'horosa-preflight.*' -type d 2>/dev/null | wc -l | tr -d ' ')" = "0" ] || { bad "[${PF_NO}]④ 中途中止后本轮临时目录没清掉(trap 失效)"; S324_BAD=1; }
# ⑤ 登记表闭合的两个缺口:第三列写错段文件 / 两个段文件定义同名函数(后装载的静默覆盖前一份)—— 在临时目录里构造坏样本
S324_D="${PF_TMP}/s324reg"; mkdir -p "${S324_D}/segments"
printf 'seg_x1() {\n:\n}\ns324_helper() { :; }\n' > "${S324_D}/segments/a.sh"
printf 's324_helper() { :; }\n' > "${S324_D}/segments/b.sh"
cp "${PF_DIR}/lib.sh" "${S324_D}/lib.sh"
S324_OUT="$( (PF_DIR="${S324_D}"; PF_REGISTRY="${S324_D}/registry.tsv"; PF_IDS=(x1); PF_NOS=(1); PF_FILES=(segments/b.sh); PF_LOADED=(segments/a.sh segments/b.sh); pf_check_registry) 2>&1 >/dev/null)"
[ "$(printf '%s\n' "${S324_OUT}" | grep -cF 'x1 在 preflight/segments/b.sh 里没有恰好一个定义' || true)" = "1" ] || { bad "[${PF_NO}]⑤ 登记表第三列指错段文件没报出来"; S324_BAD=1; }
[ "$(printf '%s\n' "${S324_OUT}" | grep -cF '函数 s324_helper 在 preflight/segments/a.sh 与 preflight/segments/b.sh 各定义一次' || true)" = "1" ] || { bad "[${PF_NO}]⑤ 两个段文件定义同名函数没报出来"; S324_BAD=1; }
# ⑥ 「测试被关掉」守卫单源 pf_test_disabled 的判别力:各形态必须报出、干净 / 注释 / 同名前缀不误报
S324_TD="${PF_TMP}/s324td"; mkdir -p "${S324_TD}"
printf "describe('a', ()=>{ it('b', ()=>{ const q = { skip: 1 }; }); test.each([1])('c', ()=>{}); });\nconst o = { skipTechniques: 1 }; o.onlyOnce = 2; latest({ only: 1 }); at.skip(1);\n// it.skip('注释里的不算')\n" > "${S324_TD}/clean.test.js"  # pf_test_disabled 判别向量
printf 'import pytest\n# @pytest.mark.skip 注释里的不算\n# pytestmark = require_srv_mark()\npytestmark = pytest.mark.slow\ndef test_a():\n    assert 1\n' > "${S324_TD}/clean_test.py"  # pf_test_disabled 判别向量
pf_test_disabled "${S324_TD}/clean.test.js" "${S324_TD}/clean_test.py" "${S324_TD}/absent.test.js" && { bad "[${PF_NO}]⑥ pf_test_disabled 把干净 / 注释 / 同名前缀 / 不存在的文件误判成被关掉"; S324_BAD=1; }
S324_TDN=0
for S324_V in "it.skip('x', ()=>{})" "test.only('x', ()=>{})" "describe.only.each([1])('x', ()=>{})" "it.concurrent.skip('x', ()=>{})" "test.todo('x')" "xit('x', ()=>{})" "xdescribe('x', ()=>{})" "fit('x', ()=>{})" "fdescribe('x', ()=>{})" "xtest('x', ()=>{})" "it('x', { skip: true }, ()=>{})" "test('x', {todo: 'later'})" "describe('x', { timeout: 5, only: true }, ()=>{})" "  t.skip('x')"; do  # pf_test_disabled 判别向量
  printf '%s\n' "${S324_V}" > "${S324_TD}/v.test.js"
  pf_test_disabled "${S324_TD}/v.test.js" || { bad "[${PF_NO}]⑥ pf_test_disabled 没认出「${S324_V}」"; S324_BAD=1; }
  S324_TDN=$((S324_TDN + 1))
done
for S324_V in "@pytest.mark.skip(reason='x')" "@pytest.mark.xfail" "    pytest.skip('x')" "@unittest.skip('x')" "pytestmark = pytest.mark.skipif(True, reason='x')" "pytestmark = [pytest.mark.xfail]" "np = pytest.importorskip('numpy')" "        self.skipTest('x')" "pytestmark = require_srv_mark()" "needs = pytest.mark.skipif(True, reason='x')" "@unittest.skipIf(True, 'x')" "    pytest.xfail('x')"; do  # pf_test_disabled 判别向量
  printf 'import pytest\n%s\ndef test_a():\n    pass\n' "${S324_V}" > "${S324_TD}/v_test.py"
  pf_test_disabled "${S324_TD}/v_test.py" || { bad "[${PF_NO}]⑥ pf_test_disabled 没认出「${S324_V}」"; S324_BAD=1; }
  S324_TDN=$((S324_TDN + 1))
done
[ "${S324_TDN}" = "26" ] || { bad "[${PF_NO}]⑥ pf_test_disabled 判别向量没跑全(${S324_TDN}/26)"; S324_BAD=1; }
# ⑦ 仓里全部 shell 脚本的出口(check_shell_exit_guard.py):set -u + EXIT trap 必带出口守卫(bash 3.2 下未赋值变量中止以 0 退出 = 失败报成成功)/
#    用了 mktemp 必挂 EXIT trap / pipefail 下不许「管道接 grep -q」(大输入假绿 / 假红)。自证含 /bin/bash 真跑守卫片段。
S324_OUT="$(python3 -B "${S324_SC}/check_shell_exit_guard.py" --self-test 2>&1)" || { printf '%s\n' "${S324_OUT}" | grep -v '^✅' | tail -4 | sed 's/^/      /' >&2; bad "[${PF_NO}]⑦ 脚本出口检查器自证失败"; S324_BAD=1; }
S324_OUT="$(python3 -B "${S324_SC}/check_shell_exit_guard.py" 2>&1)" || { printf '%s\n' "${S324_OUT}" | head -12 | sed 's/^/      /' >&2; bad "[${PF_NO}]⑦ 有脚本出口问题(见上:缺出口守卫 / mktemp 不收 / 管道接 grep -q)"; S324_BAD=1; }
[ "${S324_BAD}" = "0" ] && ok "[${PF_NO}] 预检自身结构:段间零隐式传值(含算术裸名)/ skip 守卫只走 pf_test_disabled / 段内 mktemp 在 PF_TMP 下 + 选段参数写错 7 向全退 2(+ 合法号对照放行) + 临时目录 mktemp/trap(旧快照不复用、中止必非零且清目录)+ 登记表第三列 / 函数重名可报 + pf_test_disabled 26 向判别 + 壳源码锚读面(产品锚不被测试满足 / 计数不靠测试凑 / 反锚不读测试夹具 / 拆分器自证)+ 全仓脚本出口(守卫 / mktemp 收尾 / 零管道接 grep -q)"
}

seg_326() {
echo "[${PF_NO}] 已跟踪文件的可执行位只给带 #! 的脚本"
# 没有 #! 的文件带 755(如前端页面源码、图片、参考资料):同步通道与打包都照搬文件模式,看不出原因的模式变更会一路带进发布物。
#   判据 = 索引里的模式(git ls-files -s),与工作树 chmod 无关;修法:chmod 644 后重新 add(或 git update-index --chmod=-x)。
S326_BAD=0
while IFS= read -r S326_F; do
  [ -n "${S326_F}" ] && [ -f "${REPO_ROOT}/${S326_F}" ] || continue
  [ "$(head -c 2 "${REPO_ROOT}/${S326_F}" 2>/dev/null)" = '#!' ] && continue
  bad "[${PF_NO}] ${S326_F} 带可执行位却没有 #!(chmod 644 后重新 add)"; S326_BAD=1
done < <(git -C "${REPO_ROOT}" -c core.quotepath=false ls-files -s | grep -a '^100755 ' | cut -f2-)
[ "${S326_BAD}" = "0" ] && ok "[${PF_NO}] 可执行位只在带 #! 的脚本上"
}

seg_210() {
# ── [210] pyc 不得嵌打包机绝对路径 ───────────────────────────────────────────
# 病症:compileall 不带 -s/-p 时,code object 的 co_filename 记的是打包机绝对路径,
# 于是 /Users/<用户名>/... 随每一个 pyc 进了已公证的 .pkg(实测 runtime tar 内数千个全带)。
# 构建机用户名属 PII。与 seg_180 前端 bundle 路径脱敏是同类病、不同表面 —— 那条只钉了
# 前端产物,pyc 这一面此前无人看守;它扫源码扫不到(产物不在源码树)、读 diff 也看不见
# (产物不入 git),只有拆产物 grep 才现形。
# 附带收益:脱敏后同源跨机编译的 pyc 字节恒等,增量部件不再因换目录名被判「变了」。
echo "[210] pyc 路径脱敏(co_filename 不得含构建机路径)"
S210_PKG="${REPO_ROOT}/Horosa_Desktop_Installer/scripts/package_runtime_payload.sh"
S210_BAD=0
[ -s "${S210_PKG}" ] || { bad "[210] 🔴 打包脚本缺失"; S210_BAD=1; }
if [ -s "${S210_PKG}" ]; then
  grep -qE '^\s*-s "\$\{STAGE_ROOT\}" -p "horosa-runtime" \\' "${S210_PKG}" \
    || { bad "[210] 🔴 compileall 未带 -s \${STAGE_ROOT} -p horosa-runtime —— pyc 会重新嵌构建机绝对路径"; S210_BAD=1; }
  grep -qF 'PYTHONHASHSEED=0 "${STAGE_PY_BIN}" -m compileall -q -j1 -f --invalidation-mode unchecked-hash' "${S210_PKG}" \
    || { bad "[210] 🔴 compileall 的种子/单进程/hash 失效模式三件套被改动(pyc 可复现性依赖它)"; S210_BAD=1; }
fi
# pip 的 console_scripts 把安装当时的 python 绝对路径写死进 shebang,同样要脱敏
grep -qF 'console_scripts shebang 脱敏' "${S210_PKG}" \
  || { bad "[210] 🔴 console_scripts shebang 脱敏段缺失 —— pip 入口脚本会带构建机绝对路径"; S210_BAD=1; }
# 终判据:直接扫已产出的**全部**部件,残留即红(不信脚本「跑过了」,只认产物本身)。
# 🔴 曾只扫一个部件 → 另一个部件里的残留照样漏过去;判据面窄 = 假绿。
S210_DIR="${REPO_ROOT}/Horosa_Desktop_Installer/dist/components"
if [ -d "${S210_DIR}" ]; then
  for S210_COMP in "${S210_DIR}"/horosa-comp-*.tar.gz; do
    [ -s "${S210_COMP}" ] || continue
    S210_HIT="$(tar -xzOf "${S210_COMP}" 2>/dev/null | LC_ALL=C grep -ac "/Users/${USER}/" || true)"
    [ "${S210_HIT:-0}" = "0" ] \
      || { bad "[210] 🔴 部件 $(basename "${S210_COMP}") 内仍有构建机路径(${S210_HIT} 处)——重跑 package_runtime_payload.sh"; S210_BAD=1; }
  done
fi
[ "${S210_BAD}" = "0" ] && ok "[210] compileall 带 -s/-p + 可复现三件套完整 + 产物零构建机路径"
}
