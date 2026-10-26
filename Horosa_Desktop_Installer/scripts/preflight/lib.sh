# shellcheck shell=bash
# 发布前自检 · 公共库:由 release_preflight.sh 装载。这里只定义公共变量与函数,不直接执行检查。
#
#   段 = 一个函数 seg_<id>(),住在 preflight/segments/<域>.sh;执行顺序与输出里的段号只由登记表决定:
#     登记表一行一段「id<TAB>段号<TAB>段文件(相对 preflight/)[<TAB>子段号,…]」,按执行顺序排列,# 开头为注释。
#     第四列(可选)= 合并过的段在输出里另打的子段号:`--only` / `--from` 写子段号 = 选中本段(连同本段其它子段一起跑)。
#     段体打印的「[N]」开头只许是本段段号 / ${PF_NO} / 第四列登记的子段号(check_preflight_structure.py ⑬ 机检)。
#     id 是函数名后缀,永久不变;段号是输出里打印的号。段内文字用 ${PF_NO} 引用本段段号,
#     段内变量名沿用 S<id>_ 前缀(id 与段号可以不同)。
#   preflight/extra/ 在场时用 extra/registry.tsv(整套执行顺序,可引用 segments/ 与 extra/ 下的段文件),
#   否则用 preflight/registry.tsv。只装载所用登记表引用到的段文件。
#   登记表闭合(装载后核):登记了却没定义 / 定义了却没登记 / 同一 id 登记两次,都报红。
INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "${INSTALLER_ROOT}/.." && pwd)"
fail=0
# ── 本轮临时目录 ──
#   本预检自己拼的缓存(壳源码全集 / 前端源码全集 / 本预检全文)一律放进本轮独占的 mktemp 目录,退出时(正常结束、
#   段内 set -u 中止、Ctrl-C、被杀)由 trap 整个删掉。不许再按 $$ 拼名放在 $TMPDIR 下:中断的那一轮留下的缓存,
#   会被日后碰巧拿到同一个 PID 的另一轮当成「本轮已拼好」直接复用 —— 读壳源码的检查就判在旧代码上(假绿)。
#   退出码:EXIT trap 里先取 $?,收尾后原样 exit;没走到入口的正常出口(pf_exit)却以 0 退出 = 中途意外终止,按 1 计
#   (bash 3.2 在 set -e 下 unbound variable 中止时 $? 会是 0,实测如此)。
PF_TMP="$(mktemp -d "${TMPDIR:-/tmp}/horosa-preflight.XXXXXX")" || { echo "preflight: 建不了临时目录" >&2; exit 2; }
PF_EXITED=0
pf_cleanup(){ [ -n "${PF_TMP:-}" ] && [ -d "${PF_TMP}" ] && rm -rf "${PF_TMP}"; return 0; }
pf_exit(){ PF_EXITED=1; exit "$1"; }
pf_on_exit(){ local _pf_rc=$?; pf_cleanup; if [ "${PF_EXITED}" != "1" ] && [ "${_pf_rc}" = "0" ]; then _pf_rc=1; fi; exit "${_pf_rc}"; }
trap pf_on_exit EXIT
trap 'pf_cleanup; trap - EXIT; exit 130' INT
trap 'pf_cleanup; trap - EXIT; exit 143' TERM
ok()   { printf '  \033[32m✅\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m❌\033[0m %s\n' "$1" >&2; fail=1; }
warn() { printf '  \033[33m⚠️\033[0m  %s\n' "$1"; }
# pipe_has <grep 参数…> —— 「管道接 grep -q」的等价替身:从标准输入读,命中返回 0;参数与 grep 同形(去掉 q)。
#   本脚本开着 pipefail。`… | grep -q` 命中即退,上游若还有超过管道缓冲(64KB)的内容没写完就吃 SIGPIPE,整条管道按失败计:
#   「命中 → 报红」的缺席型检查因此**假绿**(旧坏形态回潮却判通过),「未命中 → 报红」的存在型检查因此假红。
#   计数式必须读完全部输入,上游不会被掐断。本脚本的代码行里不许再出现「管道接 grep -q」(由文末哨兵机械锁)。
pipe_has(){ local n; n="$(grep -ac "$@" 2>/dev/null || true)"; [ "${n:-0}" -gt 0 ] 2>/dev/null; }
# pf_test_disabled <文件…> —— 「测试被关掉」守卫的单一来源:任一文件里有被跳过 / 被独占 / 占位的用例就返回 0(真)。
#   JS(jest):it / test / describe 后接 .skip / .only / .todo(含 .concurrent / .each / .failing 链,如 it.concurrent.skip、
#   describe.only.each)与 xit / xtest / xdescribe / fit / fdescribe / ftest。.only 同样算:同文件里只要有一条 .only,其余用例就全不跑。
#   node:test:选项式 skip —— it / test / describe / suite 调用行里的选项对象带 skip: / todo: / only:(如 it('x', { skip: true }, fn)),
#   以及上下文对象的 t.skip( / t.todo(。
#   Python(pytest / unittest):pytest.mark.skip / skipif / xfail(装饰器、`pytestmark = …` 整模块、先赋给变量再装饰都算)、
#   pytest.skip( / pytest.xfail( / pytest.importorskip(、@unittest.skip(含 skipIf / skipUnless)、self.skipTest(、SkipTest,
#   以及 `pytestmark = require_srv_mark()`(需服务的整模块条件跳过,与 skipif 同类)。
#   行注释里的写法不算(JS 去 // 之后、Python 去 # 之后再判)。文件不存在 = 不算(存在性由各段自己核)。
#   各段一律写 `pf_test_disabled "<文件>" && { bad …; }`,不许再各写一份正则(口径曾分两种、且都漏 .only;check_preflight_structure 机检)。
PF_TEST_DISABLED_JS_RE='(^|[^A-Za-z0-9_$.])(it|test|describe)([[:space:]]*\.[[:space:]]*(concurrent|each|failing))*[[:space:]]*\.[[:space:]]*(skip|only|todo)([^A-Za-z0-9_$]|$)|(^|[^A-Za-z0-9_$.])(xit|xtest|xdescribe|fit|fdescribe|ftest)[[:space:]]*[(.]|(^|[^A-Za-z0-9_$.])(it|test|describe|suite)[[:space:]]*\([^)]*\{([^}]*[^A-Za-z0-9_$])?(skip|todo|only)[[:space:]]*:|(^|[^A-Za-z0-9_$.])t[[:space:]]*\.[[:space:]]*(skip|todo)[[:space:]]*\('
PF_TEST_DISABLED_PY_RE='pytest\.mark\.(skip|skipif|xfail)([^A-Za-z0-9_]|$)|pytest\.(skip|xfail|importorskip)[[:space:]]*\(|@unittest\.skip|\.skipTest[[:space:]]*\(|SkipTest|(^|[^A-Za-z0-9_])pytestmark[[:space:]]*=.*require_srv_mark'
pf_test_disabled(){
  local _pf_f _pf_n=0 _pf_c
  for _pf_f in "$@"; do
    [ -f "${_pf_f}" ] || continue
    case "${_pf_f}" in
      *.py) _pf_c="$(sed -E 's/#.*$//' "${_pf_f}" | grep -acE -- "${PF_TEST_DISABLED_PY_RE}" || true)" ;;
      *) _pf_c="$(sed -E 's#//.*$##' "${_pf_f}" | grep -acE -- "${PF_TEST_DISABLED_JS_RE}" || true)" ;;
    esac
    _pf_n=$(( _pf_n + ${_pf_c:-0} ))
  done
  [ "${_pf_n}" -gt 0 ]
}
# 前端源面清单(单源 = astrostudyui/scripts/fe-source-paths.txt):构建时判脏(write-build-info.js)、本脚本两处构建指纹判定、
#   打包产物前端冒烟(verify_packaged_frontend.sh)同读这一份。读不到或为空 = 无从判定产物与源码是否对应 → [122] fail-closed 报红。
FE_SRC_LIST_FILE="${REPO_ROOT}/Horosa-Web/astrostudyui/scripts/fe-source-paths.txt"
FE_SRC_PATHS="$(grep -avE '^[[:space:]]*(#|$)' "${FE_SRC_LIST_FILE}" 2>/dev/null | sed -e 's/[[:space:]]*$//' -e 's#^#Horosa-Web/astrostudyui/#' | tr '\n' ' ')"

# keg-only node@22 不在默认 PATH 的终端会让 node -e 检查假阳性失败、误拦 pre-push;缺 node 则自动补常见位置的 node。
if ! command -v node >/dev/null 2>&1; then
	for _nd in /opt/homebrew/opt/node@22/bin /opt/homebrew/opt/node@20/bin /opt/homebrew/opt/node@18/bin /opt/homebrew/bin /usr/local/opt/node@22/bin /usr/local/opt/node@18/bin /usr/local/bin; do
		[ -x "${_nd}/node" ] && { PATH="${_nd}:${PATH}"; export PATH; break; }
	done
fi

# ── 段间共用的路径常量(装载期就定好)──
#   段与段之间不许靠「别的段函数体里赋的变量」传值:全量按序跑看不出毛病,`--only` / `--from` 跳过赋值那段就 set -u 中止
#   (unbound variable,一段没跑完也没有汇总行)。几段共用的路径写在这里;只给一两段用的,由读它的段自己取。
#   机检:check_preflight_structure.py(静态核每个段函数读到的变量都有来处),由预检段每轮跑。
UISRC="${REPO_ROOT}/Horosa-Web/astrostudyui/src"
WARMJS="${REPO_ROOT}/Horosa-Web/astrostudyui/scripts/warmHorosaRuntime.js"
STARTSH="${REPO_ROOT}/Horosa-Web/start_horosa_local.sh"
AIPROXY="${REPO_ROOT}/Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysisProxyService.java"

VERSION="$(python3 -c "import json,os;print(json.load(open(os.path.join('${INSTALLER_ROOT}','package.json')))['version'])" 2>/dev/null || echo "")"
RUNTIME_VERSION="$(python3 -c "import json,os;print(json.load(open(os.path.join('${INSTALLER_ROOT}','config','release_config.json'))).get('runtimeVersion',''))" 2>/dev/null || echo "")"

# ── 公共助手 ──
# 私有块剥离 awk 程序(与同步通道同一口径:开始标记行起到 end 标记行止整段删掉,标记行本身也删)。
#   标记字面在这里拼出来,本文件自身不含完整标记。
_PF_MK='@horosa-''private'
PF_STRIP_PRIVATE="f{if(/${_PF_MK}:end/)f=0; next} /${_PF_MK}:/{f=1; next} 1"
unset _PF_MK

# ── 壳层 Rust 源全集 ──
# 桌面壳 src-tauri/src 下:main.rs(入口 / 模块声明 / Builder 装配与命令注册)+ 按职责拆出的模块 + 三个测试文件,原先全在 main.rs 一份里。
#   按下面的固定顺序拼成一份临时文件;原先 grep main.rs 的检查改读这一份,判定口径不变(内容就是原先 main.rs 的内容)。
#   另外五个独立子模块(终端命令 / 本机服务三件 / REST)向来各自成文件、由检查直接点名读,不在其中。
PF_SHELL_RS_FILES="main.rs edition.rs config.rs app_state.rs shell_init.rs ui_launcher.rs ui_windows.rs ui_menu.rs shell_text.rs notify.rs diagnostics.rs agent_bridge.rs asset_review.rs storage.rs desktop_io.rs ai_files.rs runtime_paths.rs runtime_health.rs runtime_prewarm.rs runtime_slots.rs runtime_archive.rs runtime_components.rs runtime_install.rs updater_manifest.rs updater_download.rs updater_events.rs updater_check.rs updater_staged.rs updater_helper.rs static_server.rs services.rs bootstrap.rs ledger.rs bridge_acl_tests.rs tests.rs shell_guard_tests.rs"
PF_SHELL_RS_STANDALONE="horosa_cli.rs mcp_client.rs mcp_server.rs mcp_stdio.rs rest_api.rs"
# pf_shell_rs [仓根]:打印拼好的临时文件路径(缺省本仓)。本仓那份本轮只拼一次(放在本轮独占的 PF_TMP 里,旁边记着它拼自哪个根,
#   复用前核对);别的根(另一仓、判别力自证的临时根)每次现拼。
#   该根下没有 main.rs 时打印一个不存在的路径:各检查原先「文件不在 → 跳过 / 报缺」的口径不变。
#   这是「整份源码」口径(拼接新鲜度自证、跨仓对拍);段里的锚不许拿它当读面(含测试 → 测试替产品作证 / 夹具误红),
#   按语义改读下面的 pf_shell_rs_prod / pf_shell_rs_prod_all / pf_shell_rs_tests(check_preflight_structure.py ⑪ R4)。
pf_shell_rs(){
  local _pf_root="${1:-${REPO_ROOT}}" _pf_src _pf_out _pf_f
  _pf_src="${_pf_root}/Horosa_Desktop_Installer/src-tauri/src"
  if [ ! -f "${_pf_src}/main.rs" ]; then printf '%s' "${_pf_src}/main.rs"; return 0; fi
  _pf_out="${PF_TMP}/shellrs.$(printf '%s' "${_pf_root}" | cksum | cut -d' ' -f1)"
  if [ "${_pf_root}" != "${REPO_ROOT}" ] || [ ! -s "${_pf_out}" ] || [ "$(cat "${_pf_out}.root" 2>/dev/null)" != "${_pf_root}" ]; then
    printf '%s' "${_pf_root}" > "${_pf_out}.root"
    for _pf_f in ${PF_SHELL_RS_FILES}; do
      [ -f "${_pf_src}/${_pf_f}" ] && cat "${_pf_src}/${_pf_f}"
    done > "${_pf_out}"
  fi
  printf '%s' "${_pf_out}"
}
# ── 壳层 Rust 源:产品 / 测试分开读(单一口径 = preflight/rs_split.py,按 Rust 词法拆)──
#   「测试」= 文件名以 tests.rs 结尾的整份 + 各文件里紧跟 #[cfg(test)] 的那一项(`mod 名 { … }` 整块 / `mod 名;` / `fn …{ … }`)。
#   字符串、字符字面量、注释里的花括号与 #[cfg(test)] 都不算(词法走,不是按行 grep)。
#   读法(段里写哪一个,check_preflight_structure.py ⑪ 每轮机检):
#     · 产品语义的正锚(「源码里必须有 Y」)与计数阈值 → pf_shell_rs_prod:测试里的同名调用 / 夹具满足不了它,
#       删掉产品那一处必红(读全集时测试替产品「作证」= 假绿);
#     · 「产品代码里不许出现 X」的反锚 → pf_shell_rs_prod_all(壳层模块 + 五个独立子模块的产品代码):
#       测试为验证检测器会故意造这类夹具,不算产品回归;独立子模块同样会写令牌 / 配置文件,不许漏扫;
#     · 「某条测试必须在位」的锚 → pf_shell_rs_tests(全部测试:三个测试文件 + 各文件的同文件测试项,含独立子模块);
#     · 只读一个独立子模块的产品代码 → pf_rs_prod <文件>。
#   pf_shell_rs(全集)只留给「整份源码」口径的用途(拼接新鲜度自证、跨仓对拍),段里不许拿它当锚的读面。
#   产品输出里测试项所在的行换成空行,行数与原文相同(按行号比先后的检查照常)。
PF_RS_SPLIT="${INSTALLER_ROOT}/scripts/preflight/rs_split.py"
# 拆分失败 = 失败关闭:拆分器退非 0(python3 不在 / 拆分器自身回归 / 文件读不了)时,不写缓存、返回一个不存在的路径
#   (正锚因此读不到 → 红),并往 PF_RS_SPLIT_FAIL 记一笔;pf_run 每跑完一段查它,有记录就把这一段判红(反锚读不存在的文件
#   照样「零命中」,只靠返回路径兜不住)。这几个助手都在 $( … ) 子进程里被调,bad 打不进本进程的 fail,所以经文件传。
#   以前写成「失败就写空文件」:产品读面成了空面,所有「产品代码里不许出现 X」的反锚整类判绿,而且空文件整轮被复用。
PF_RS_SPLIT_FAIL="${PF_TMP}/rs_split.failed"
# _pf_rs_split_to <输出> <prod|tests> <文件…>:成功 → 0 且写好输出;失败 → 非 0、输出不存在、记一笔失败
_pf_rs_split_to(){
  local _pf_dst="$1" _pf_m="$2"
  shift 2
  if python3 "${PF_RS_SPLIT}" "${_pf_m}" "$@" > "${_pf_dst}.part" 2>"${_pf_dst}.err"; then
    mv -f "${_pf_dst}.part" "${_pf_dst}"; rm -f "${_pf_dst}.err"; return 0
  fi
  printf 'rs_split %s 失败(退出码非 0,读 %d 个文件;%s)\n' "${_pf_m}" "$#" "$(head -1 "${_pf_dst}.err" 2>/dev/null | cut -c1-200)" >> "${PF_RS_SPLIT_FAIL}"
  rm -f "${_pf_dst}.part" "${_pf_dst}.err" "${_pf_dst}"
  return 1
}
# pf_rs_split_check:pf_run 每跑完一段调一次;本段里有过拆分失败 → 判红(并清掉记录,下一段重新记)
pf_rs_split_check(){
  [ -s "${PF_RS_SPLIT_FAIL}" ] || return 0
  bad "[${PF_NO:-壳层源码}] 壳源码产品 / 测试拆分失败(preflight/rs_split.py):本段读壳源码的检查不作数 —— $(head -1 "${PF_RS_SPLIT_FAIL}")"
  [ -n "${PF_ID:-}" ] && eval "S${PF_ID}_BAD=1"
  : > "${PF_RS_SPLIT_FAIL}"
}
# _pf_shell_rs_part <仓根> <prod|tests> <缓存名> <文件清单>:本仓那份本轮只拼一次(旁边记着根,复用前核对),别的根每次现拼。
_pf_shell_rs_part(){
  local _pf_root="$1" _pf_mode="$2" _pf_tag="$3" _pf_list="$4" _pf_src _pf_out _pf_f _pf_paths=""
  _pf_src="${_pf_root}/Horosa_Desktop_Installer/src-tauri/src"
  if [ ! -f "${_pf_src}/main.rs" ]; then printf '%s' "${_pf_src}/main.rs"; return 0; fi
  _pf_out="${PF_TMP}/${_pf_tag}.$(printf '%s' "${_pf_root}" | cksum | cut -d' ' -f1)"
  if [ "${_pf_root}" != "${REPO_ROOT}" ] || [ ! -f "${_pf_out}" ] || [ "$(cat "${_pf_out}.root" 2>/dev/null)" != "${_pf_root}" ]; then
    for _pf_f in ${_pf_list}; do
      [ -f "${_pf_src}/${_pf_f}" ] && _pf_paths="${_pf_paths} ${_pf_src}/${_pf_f}"
    done
    # shellcheck disable=SC2086
    if ! _pf_rs_split_to "${_pf_out}" "${_pf_mode}" ${_pf_paths}; then
      rm -f "${_pf_out}.root"; printf '%s' "${_pf_out}.rs-split-failed"; return 0
    fi
    printf '%s' "${_pf_root}" > "${_pf_out}.root"
  fi
  printf '%s' "${_pf_out}"
}
pf_shell_rs_prod(){ _pf_shell_rs_part "${1:-${REPO_ROOT}}" prod shellrs_prod "${PF_SHELL_RS_FILES}"; }
pf_shell_rs_prod_all(){ _pf_shell_rs_part "${1:-${REPO_ROOT}}" prod shellrs_prodall "${PF_SHELL_RS_FILES} ${PF_SHELL_RS_STANDALONE}"; }
pf_shell_rs_tests(){ _pf_shell_rs_part "${1:-${REPO_ROOT}}" tests shellrs_tests "${PF_SHELL_RS_FILES} ${PF_SHELL_RS_STANDALONE}"; }
# pf_rs_prod <文件>:单个 .rs 的产品代码(同文件测试项换成空行;文件不在 → 打印原路径,「文件不在 → 跳过 / 报缺」口径不变)。
#   缓存键 = 路径 + 内容摘要(判别力自证改了临时副本 → 摘要变 → 现拼)。
pf_rs_prod(){
  local _pf_out
  [ -f "$1" ] || { printf '%s' "$1"; return 0; }
  _pf_out="${PF_TMP}/rsprod.$( { printf '%s\n' "$1"; cat "$1"; } | cksum | tr ' ' '.')"
  [ -f "${_pf_out}" ] || _pf_rs_split_to "${_pf_out}" prod "$1" || { printf '%s' "${_pf_out}.rs-split-failed"; return 0; }
  printf '%s' "${_pf_out}"
}
# 「测试在位」形状的字面(fn 名 / mod …tests / #[test]):表格里这类行读整份文件(测试就在文件里),其余 .rs 行只读产品代码。
PF_RS_TEST_SHAPE_RE='^(fn [A-Za-z0-9_]+(\(\)?)?|mod [A-Za-z0-9_]*tests|#\[test\])$'
# ── 前端 / Python 源码树:只扫产品文件(「不许出现」类递归反锚用)──
# pf_prod_tree <根> [扩展名…]:根下的产品源文件(每行一个)。去掉测试目录(__tests__ / tests / test / __mocks__ / __fixtures__ /
#   fixtures / __snapshots__)、测试文件(*.test.* / *.spec.* / test_*.py / *_test.py / conftest.py)与 node_modules / dist / dist-file /
#   __pycache__。扩展名不写 = 全部文件。根是单个文件时原样打印它。
#   为什么:「产品代码里不许再出现 X」的反锚递归扫整树时,谁给这条回归写行为测试、把被禁字面当夹具写进测试,预检就假红
#   (以往的处理是测试改写法躲,测试越来越难读)。保密类(私有名 / 标记 / 密钥字面)的反锚测试也会同步出去,照旧扫整树,
#   在行上或上一行写「# 全树:<理由>」(check_preflight_structure.py ⑫ 机检:递归反锚既不排除测试、又没写理由 = 红)。
pf_prod_tree(){
  local _pf_root="$1" _pf_e
  local _pf_names=()
  shift
  if [ -f "${_pf_root}" ]; then printf '%s\n' "${_pf_root}"; return 0; fi
  [ -d "${_pf_root}" ] || return 0
  for _pf_e in "$@"; do
    [ "${#_pf_names[@]}" -gt 0 ] && _pf_names+=(-o)
    _pf_names+=(-name "*.${_pf_e}")
  done
  [ "${#_pf_names[@]}" -gt 0 ] || _pf_names=(-name '*')
  find "${_pf_root}" \( -name __tests__ -o -name tests -o -name test -o -name __mocks__ -o -name __fixtures__ -o -name fixtures -o -name __snapshots__ \
      -o -name node_modules -o -name dist -o -name dist-file -o -name __pycache__ \) -prune -o -type f \
      ! -name '*.test.*' ! -name '*.spec.*' ! -name 'test_*.py' ! -name '*_test.py' ! -name conftest.py \
      \( "${_pf_names[@]}" \) -print 2>/dev/null | LC_ALL=C sort
}
# pf_prod_hits <grep 选项> <模式> <根> [扩展名…]:产品文件里命中模式的文件(每行一个;选项同 grep,不含 -r / -l / -q,至少写一个如 -a)。
#   反锚写 `[ -n "$(pf_prod_hits -a '<模式>' "<根>" js)" ] && { bad …; }`。
pf_prod_hits(){
  local _pf_o="$1" _pf_p="$2" _pf_r="$3"
  shift 3
  # shellcheck disable=SC2086
  pf_prod_tree "${_pf_r}" "$@" | tr '\n' '\0' | xargs -0 grep -l ${_pf_o} -- "${_pf_p}" /dev/null 2>/dev/null || true
}
# pf_prod_grep <grep 选项> <模式> <根> [扩展名…]:同上,但打印 grep 原样的命中行(选项里写 -n 带行号;要列出命中处给人看时用)。
#   计数(「至少 N 个文件接了线」)也走 pf_prod_hits … | wc -l:测试文件替产品凑数 = 删掉产品接线照样绿。
pf_prod_grep(){
  local _pf_o="$1" _pf_p="$2" _pf_r="$3"
  shift 3
  # shellcheck disable=SC2086
  pf_prod_tree "${_pf_r}" "$@" | tr '\n' '\0' | xargs -0 grep -H ${_pf_o} -- "${_pf_p}" /dev/null 2>/dev/null || true
}
# pf_shell_rs_check:源全集闭合(pf_run 跑段之前调一次,全过时不出声):src 下每个 .rs 都在两张清单之一、清单里的文件都在。
#   否则新加的模块文件里的代码会逃出全部「读壳源码」的检查(读不到 → 判缺席 → 假绿)。
pf_shell_rs_check(){
  local _pf_src="${REPO_ROOT}/Horosa_Desktop_Installer/src-tauri/src" _pf_f _pf_b
  for _pf_f in ${PF_SHELL_RS_FILES} ${PF_SHELL_RS_STANDALONE}; do
    [ -f "${_pf_src}/${_pf_f}" ] || bad "[壳层源码] 清单里的 src-tauri/src/${_pf_f} 不存在(preflight/lib.sh 的 PF_SHELL_RS_FILES / PF_SHELL_RS_STANDALONE)"
  done
  for _pf_f in "${_pf_src}"/*.rs; do
    _pf_b="${_pf_f##*/}"
    case " ${PF_SHELL_RS_FILES} ${PF_SHELL_RS_STANDALONE} " in *" ${_pf_b} "*) ;; *) bad "[壳层源码] src-tauri/src/${_pf_b} 不在任何清单里:登记进 preflight/lib.sh 的 PF_SHELL_RS_FILES(壳层模块)或 PF_SHELL_RS_STANDALONE(独立子模块)" ;; esac
  done
}

# ── 前端拆成子模块的大文件:源码全集 ──
# AIAnalysisMain.js / aiExport.js / aiAnalysisContext.js / LiuRengMain.js / PlanetariumBabylon.js / IndiaChartMain.js / GuoLaoChartMain.js 原先各是一份大文件,
#   现按职责拆成子目录下的子模块,原路径留作门面(对外导入路径不变);全站样式 layouts/app.less 按区段拆成 layouts/app/*.less,app.less 按原顺序 @import。
#   登记表单源 = Horosa-Web/astrostudyui/scripts/source-sets.json(jest 的 helpers/sourceSet.js、各检查器读同一份):
#   每个门面 → 子模块目录 + 子模块文件的先后次序。拼法:子模块按登记次序在前、门面在最后,首尾相接成一份(内容即拆分前那份文件的全部代码)。
#   原先 grep 这些文件的检查改读拼好的这一份,判定口径不变;下面的 pf_code / pf_has / pf_need / pf_none / pf_once / pf_scan_table 已自动按全集读。
#   Python 计算引擎的 perchart.py / india/jyotish_engine.py / astroextra.py 同样拆成同级 *_parts 子包里的子模块(登记表 pySets,路径相对 Horosa-Web/astropy),
#   读法相同(子模块在前、门面在最后首尾相接);子包里只有文档串的 __init__.py 不登记。
PF_SRC_SETS_JSON="${REPO_ROOT}/Horosa-Web/astrostudyui/scripts/source-sets.json"
# 一行一个门面:「门面路径(相对根)<TAB>子模块目录<TAB>空格分隔的子模块文件<TAB>根(src = astrostudyui/src,astropy = Horosa-Web/astropy)」(装载时读一次)
PF_SRC_SETS="$(python3 -c '
import json, sys
try:
    m = json.load(open(sys.argv[1], encoding="utf-8"))
    groups = ((m["sets"], "src"), (m.get("pySets") or {}, "astropy"))
except Exception:
    sys.exit(0)
for sets, base in groups:
    for rel, v in sets.items():
        print("%s\t%s\t%s\t%s" % (rel, v["dir"], " ".join(v["files"]), base))
' "${PF_SRC_SETS_JSON}" 2>/dev/null)"
# pf_src_set_files <文件路径>:全集文件清单(每行一个,子模块在前、门面在后)。路径尾部不是登记过的门面(…/src/<门面> 或 …/astropy/<门面>),
#   或该根下门面 / 任一子模块不在(例:判别力自证只拷了一份拼好的全集当门面)→ 只打印它自己。
pf_src_set_files(){
  local _pf_p="$1" _pf_rel _pf_dir _pf_files _pf_base _pf_root _pf_f _pf_out=""
  while IFS="$(printf '\t')" read -r _pf_rel _pf_dir _pf_files _pf_base; do
    [ -n "${_pf_rel}" ] || continue
    case "${_pf_p}" in
      */"${_pf_base}"/"${_pf_rel}")
        _pf_root="${_pf_p%"${_pf_rel}"}"
        [ -f "${_pf_p}" ] || break
        for _pf_f in ${_pf_files}; do
          [ -f "${_pf_root}${_pf_dir}/${_pf_f}" ] || { _pf_out=""; break 2; }
          _pf_out="${_pf_out}${_pf_root}${_pf_dir}/${_pf_f}
"
        done
        printf '%s%s\n' "${_pf_out}" "${_pf_p}"
        return 0 ;;
    esac
  done <<PF_SRC_SETS_EOF
${PF_SRC_SETS}
PF_SRC_SETS_EOF
  printf '%s\n' "${_pf_p}"
}
# pf_src_set <文件路径>:登记过的门面 → 打印拼好的临时文件路径;其余原样打印(调用方不用区分)。每次现拼(判别力自证会改临时副本)。
#   .js 门面 = 子模块(登记次序)+ 门面首尾相接;样式门面 layouts/app.less = 门面里的区段 @import 原位展开(= 拆分前的整份样式)。
pf_src_set(){
  local _pf_list _pf_out _pf_f
  _pf_list="$(pf_src_set_files "$1")"
  if [ "${_pf_list}" = "$1" ]; then printf '%s' "$1"; return 0; fi
  _pf_out="${PF_TMP}/srcset.$(printf '%s' "$1" | cksum | cut -d' ' -f1)"
  case "$1" in
    *.less)
      # 样式门面:门面里指向登记区段的 `@import './…';` 行原位换成区段全文(= 拆分前的整份样式,规则次序与 :global 嵌套都原样)
      printf '%s\n' "${_pf_list}" | python3 -c '
import os, re, sys
files = [l for l in sys.stdin.read().split("\n") if l]
facade, parts = files[-1], set(files[:-1])
out = []
for ln in open(facade, encoding="utf-8").read().split("\n"):
    m = re.match(r"^@import \x27(\./[^\x27]+\.less)\x27;\s*$", ln)
    p = os.path.normpath(os.path.join(os.path.dirname(facade), m.group(1))) if m else None
    out.append(open(p, encoding="utf-8").read()[:-1] if p in parts else ln)
sys.stdout.write("\n".join(out))
' > "${_pf_out}" ;;
    *)
      while IFS= read -r _pf_f; do cat "${_pf_f}"; done <<PF_SRC_SET_EOF > "${_pf_out}"
${_pf_list}
PF_SRC_SET_EOF
      ;;
  esac
  printf '%s' "${_pf_out}"
}
# pf_src_set_owner <门面路径> <字面>:全集里第一个含该字面(grep -F)的文件(判别力自证改临时副本时定位要改的那份);没有则打印门面路径。
pf_src_set_owner(){
  local _pf_f
  while IFS= read -r _pf_f; do
    grep -qF -- "$2" "${_pf_f}" 2>/dev/null && { printf '%s' "${_pf_f}"; return 0; }
  done <<PF_SRC_OWNER_EOF
$(pf_src_set_files "$1")
PF_SRC_OWNER_EOF
  printf '%s' "$1"
}
# pf_src_set_check:全集闭合(pf_run 跑段之前调一次,全过时不出声):登记表读得出、登记的门面与子模块都在、子模块目录里每个与门面同扩展名的文件
#   (.js 门面收 .js、样式门面 layouts/app.less 收 .less、Python 门面收 .py —— 子包里只有文档串的 __init__.py 除外)都登记了。
#   否则新加的子模块文件里的代码会逃出全部「读源码」的检查(读不到 → 判缺席 → 假绿)。
pf_src_set_check(){
  local _pf_ui _pf_rel _pf_dir _pf_files _pf_base _pf_f _pf_b _pf_lbl
  [ -n "${PF_SRC_SETS}" ] || { bad "[前端源码全集] 登记表读不出(Horosa-Web/astrostudyui/scripts/source-sets.json)"; return 0; }
  while IFS="$(printf '\t')" read -r _pf_rel _pf_dir _pf_files _pf_base; do
    [ -n "${_pf_rel}" ] || continue
    if [ "${_pf_base}" = "astropy" ]; then _pf_ui="${REPO_ROOT}/Horosa-Web/astropy"; _pf_lbl="[Python 源码全集]"
    else _pf_ui="${REPO_ROOT}/Horosa-Web/astrostudyui/src"; _pf_lbl="[前端源码全集]"; fi
    [ -f "${_pf_ui}/${_pf_rel}" ] || bad "${_pf_lbl} 登记的门面 ${_pf_base}/${_pf_rel} 不存在(scripts/source-sets.json)"
    for _pf_f in ${_pf_files}; do
      [ -f "${_pf_ui}/${_pf_dir}/${_pf_f}" ] || bad "${_pf_lbl} 登记的子模块 ${_pf_base}/${_pf_dir}/${_pf_f} 不存在(scripts/source-sets.json)"
    done
    for _pf_f in "${_pf_ui}/${_pf_dir}"/*."${_pf_rel##*.}"; do
      [ -f "${_pf_f}" ] || continue
      _pf_b="${_pf_f##*/}"
      [ "${_pf_base}/${_pf_b}" = "astropy/__init__.py" ] && continue
      case " ${_pf_files} " in *" ${_pf_b} "*) ;; *) bad "${_pf_lbl} ${_pf_base}/${_pf_dir}/${_pf_b} 没登记:按原文件里的先后次序登记进 Horosa-Web/astrostudyui/scripts/source-sets.json" ;; esac
    done
  done <<PF_SRC_CHECK_EOF
${PF_SRC_SETS}
PF_SRC_CHECK_EOF
}

# ── 段登记与装载 ──
PF_DIR="${INSTALLER_ROOT}/scripts/preflight"
PF_REGISTRY="${PF_DIR}/registry.tsv"
[ -f "${PF_DIR}/extra/registry.tsv" ] && PF_REGISTRY="${PF_DIR}/extra/registry.tsv"
PF_IDS=(); PF_NOS=(); PF_FILES=(); PF_ALIASES=(); PF_LOADED=(); PF_SELF_FILES=()
PF_MODE=run; PF_ONLY=""; PF_FROM=""; PF_RAN=0
PF_NO=""; PF_ID=""

pf_usage(){
  echo "用法: release_preflight.sh [--list] [--only 段号[,段号…]] [--from 段号]"
  echo "  --list        列出本仓登记表(段号 / id / 段文件),不执行"
  echo "  --only 段号…  只跑这些段(逗号分隔,段号按输出里的号;每个号都必须在登记表里 —— 合并段的子段号见 --list 第四列,写子段号 = 跑它所在的整段)"
  echo "  --from 段号   从这一段起跑到最后(号必须在登记表里;子段号 = 从它所在的整段起)"
  echo "  段号写错 / 缺值 / 一段都没选中 = 退出码 2(不会「一段没跑却报全绿」)"
}

# pf_arg_val <选项> <值>:选项值不许为空、不许是另一个选项(`--only --from 3` 这类漏写值)
pf_arg_val(){
  case "$2" in
    ''|-*) echo "参数 $1 缺值(要跟段号,例 $1 26)" >&2; pf_usage >&2; return 1 ;;
  esac
  return 0
}

pf_parse_args(){
  while [ $# -gt 0 ]; do
    case "$1" in
      --list) PF_MODE=list ;;
      --only) pf_arg_val --only "${2:-}" || return 1; PF_ONLY="$2"; shift ;;
      --only=*) PF_ONLY="${1#--only=}"; pf_arg_val --only "${PF_ONLY}" || return 1 ;;
      --from) pf_arg_val --from "${2:-}" || return 1; PF_FROM="$2"; shift ;;
      --from=*) PF_FROM="${1#--from=}"; pf_arg_val --from "${PF_FROM}" || return 1 ;;
      -h|--help) pf_usage; pf_exit 0 ;;
      *) echo "未知参数: $1" >&2; pf_usage >&2; return 1 ;;
    esac
    shift
  done
  return 0
}

# pf_check_selection:--only 的每个号、--from 的号都必须在本仓登记表(第二列)里;否则打印未知号并返回 1。
#   (段号写错时「一段都没跑、照样打印全部通过、exit 0」= 假绿;--list 看本仓有哪些号)
# pf_parent_no <号>:段号原样打印;登记表第四列里的子段号 → 打印它所在段的段号;都不是 → 返回 1。
pf_parent_no(){
  local _pf_i=0 _pf_n=${#PF_IDS[@]}
  while [ "${_pf_i}" -lt "${_pf_n}" ]; do
    [ "${PF_NOS[${_pf_i}]}" = "$1" ] && { printf '%s' "$1"; return 0; }
    _pf_i=$((_pf_i + 1))
  done
  _pf_i=0
  while [ "${_pf_i}" -lt "${_pf_n}" ]; do
    case ",${PF_ALIASES[${_pf_i}]}," in *",$1,"*) printf '%s' "${PF_NOS[${_pf_i}]}"; return 0 ;; esac
    _pf_i=$((_pf_i + 1))
  done
  return 1
}
pf_check_selection(){
  local _pf_x _pf_p _pf_bad="" _pf_only=""
  if [ -n "${PF_ONLY}" ]; then
    for _pf_x in $(printf '%s' "${PF_ONLY}" | tr ',' ' '); do
      if _pf_p="$(pf_parent_no "${_pf_x}")"; then
        [ "${_pf_p}" = "${_pf_x}" ] || echo "(子段号 ${_pf_x} 属于段 [${_pf_p}]:跑整段)" >&2
        _pf_only="${_pf_only}${_pf_only:+,}${_pf_p}"
      else
        _pf_bad="${_pf_bad} ${_pf_x}"
      fi
    done
    [ -n "$(printf '%s' "${PF_ONLY}" | tr -d ', ')" ] || _pf_bad="${_pf_bad} (空)"
  fi
  if [ -n "${PF_FROM}" ]; then
    if _pf_p="$(pf_parent_no "${PF_FROM}")"; then
      [ "${_pf_p}" = "${PF_FROM}" ] || echo "(子段号 ${PF_FROM} 属于段 [${_pf_p}]:从整段起)" >&2
      PF_FROM="${_pf_p}"
    else
      _pf_bad="${_pf_bad} ${PF_FROM}"
    fi
  fi
  if [ -n "${_pf_bad}" ]; then
    echo "本仓登记表($(printf '%s' "${PF_REGISTRY}" | sed "s#^${INSTALLER_ROOT}/scripts/##"))里没有这些段号:${_pf_bad} —— 用 --list 看本仓的段号(第四列是合并段的子段号)" >&2
    return 1
  fi
  [ -n "${PF_ONLY}" ] && PF_ONLY="${_pf_only}"
  return 0
}

# 读登记表 → 装载段文件(每个文件只 source 一次;source 会把整份读进内存再执行,本轮跑的就是装载那一刻的快照)
pf_load(){
  local _pf_id _pf_no _pf_rel _pf_al _pf_seen=" "
  while IFS="$(printf '\t')" read -r _pf_id _pf_no _pf_rel _pf_al; do
    case "${_pf_id}" in ''|'#'*) continue ;; esac
    PF_IDS+=("${_pf_id}"); PF_NOS+=("${_pf_no}"); PF_FILES+=("${_pf_rel}"); PF_ALIASES+=("${_pf_al}")
  done < "${PF_REGISTRY}"
  PF_SELF_FILES=("${INSTALLER_ROOT}/scripts/release_preflight.sh" "${PF_DIR}/lib.sh" "${PF_REGISTRY}")
  for _pf_rel in "${PF_FILES[@]}"; do
    case "${_pf_seen}" in *" ${_pf_rel} "*) continue ;; esac
    _pf_seen="${_pf_seen}${_pf_rel} "
    if [ -f "${PF_DIR}/${_pf_rel}" ]; then
      PF_LOADED+=("${_pf_rel}"); PF_SELF_FILES+=("${PF_DIR}/${_pf_rel}")
      # shellcheck disable=SC1090
      . "${PF_DIR}/${_pf_rel}"
    else
      bad "[登记表] 段文件不存在: preflight/${_pf_rel}"
    fi
  done
}

# 登记表闭合:登记了却没定义 / 定义了却没登记 / 重复登记。另核 registry.tsv(用 extra 时它不执行,但要保持可用):
#   每行的函数确在所写的段文件里定义;segments/ 下非 .public.sh 文件里的每个段函数都在 registry.tsv 里登记。
pf_check_registry(){
  local _pf_i=0 _pf_n=${#PF_IDS[@]} _pf_ids=" " _pf_f _pf_line _pf_id _pf_no _pf_rel _pf_x
  while [ "${_pf_i}" -lt "${_pf_n}" ]; do
    _pf_id="${PF_IDS[${_pf_i}]}"
    case "${_pf_ids}" in *" ${_pf_id} "*) bad "[登记表] id ${_pf_id} 登记了两次" ;; esac
    _pf_ids="${_pf_ids}${_pf_id} "
    declare -F "seg_${_pf_id}" >/dev/null 2>&1 || bad "[登记表] seg_${_pf_id} 登记了却没定义(preflight/${PF_FILES[${_pf_i}]})"
    _pf_i=$((_pf_i + 1))
  done
  # 子段号(第四列):纯数字、不与本表任何段号 / 别的子段号重复(重了 --only 就有两种解释)
  _pf_line=" ${PF_NOS[*]} "
  for _pf_f in $(printf '%s\n' "${PF_ALIASES[@]}" | tr ',' ' '); do
    case "${_pf_f}" in *[!0-9]*) bad "[登记表] 子段号「${_pf_f}」不是纯数字"; continue ;; esac
    case "${_pf_line}" in *" ${_pf_f} "*) bad "[登记表] 子段号 ${_pf_f} 与本表的段号 / 别的子段号重复" ;; esac
    _pf_line="${_pf_line}${_pf_f} "
  done
  for _pf_f in $(declare -F | awk '$3 ~ /^seg_/ {print $3}'); do
    case "${_pf_ids}" in *" ${_pf_f#seg_} "*) ;; *) bad "[登记表] ${_pf_f} 定义了却没登记(不会执行)" ;; esac
  done
  # 执行用登记表的第三列也要对得上:该段函数在它写的那个段文件里恰好定义一处,且在本轮装载的全部文件里合计恰好一处
  #   (两个段文件定义同名 seg_X 时,后装载的那份静默盖掉前一份,登记表第三列形同虚设)。
  _pf_i=0
  while [ "${_pf_i}" -lt "${_pf_n}" ]; do
    _pf_id="${PF_IDS[${_pf_i}]}"; _pf_rel="${PF_FILES[${_pf_i}]}"
    [ "$(grep -c "^seg_${_pf_id}() {" "${PF_DIR}/${_pf_rel}" 2>/dev/null || true)" = "1" ] \
      || bad "[登记表] ${PF_REGISTRY##*/preflight/} 的 ${_pf_id} 在 preflight/${_pf_rel} 里没有恰好一个定义"
    _pf_i=$((_pf_i + 1))
  done
  # 函数名(段函数与段内助手)在本轮装载的文件(公共库 + 段文件)里不许重名:重名 = 后装载的静默覆盖前一份
  _pf_line="$(cd "${PF_DIR}" && for _pf_f in lib.sh "${PF_LOADED[@]}"; do sed -n -E "s#^(function[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*\(\)[[:space:]]*\{.*#\2 ${_pf_f}#p" "${_pf_f}"; done | sort | awk '$1 == p { print p " " pf " " $2 } { p = $1; pf = $2 }')"
  if [ -n "${_pf_line}" ]; then
    while IFS=' ' read -r _pf_f _pf_id _pf_rel; do
      bad "[登记表] 函数 ${_pf_f} 在 preflight/${_pf_id} 与 preflight/${_pf_rel} 各定义一次(后装载的静默覆盖前一份):改名或合并"
    done <<PF_DUPFN_EOF
${_pf_line}
PF_DUPFN_EOF
  fi
  if [ "${PF_REGISTRY}" != "${PF_DIR}/registry.tsv" ] && [ -f "${PF_DIR}/registry.tsv" ]; then
    _pf_ids=" "
    while IFS="$(printf '\t')" read -r _pf_id _pf_no _pf_rel _pf_x; do
      case "${_pf_id}" in ''|'#'*) continue ;; esac
      _pf_ids="${_pf_ids}${_pf_id} "
      [ "$(grep -c "^seg_${_pf_id}() {" "${PF_DIR}/${_pf_rel}" 2>/dev/null || true)" = "1" ] \
        || bad "[登记表] registry.tsv 的 ${_pf_id} 在 preflight/${_pf_rel} 里没有恰好一个定义"
    done < "${PF_DIR}/registry.tsv"
    for _pf_f in "${PF_DIR}"/segments/*.sh; do
      case "${_pf_f}" in *.public.sh) continue ;; esac
      for _pf_line in $(sed -n 's/^seg_\([A-Za-z0-9_]*\)() {$/\1/p' "${_pf_f}"); do
        case "${_pf_ids}" in *" ${_pf_line} "*) ;; *) bad "[登记表] seg_${_pf_line}(${_pf_f##*/preflight/})未在 registry.tsv 登记" ;; esac
      done
    done
  fi
}

pf_list(){
  pf_load
  local _pf_i=0 _pf_n=${#PF_IDS[@]}
  while [ "${_pf_i}" -lt "${_pf_n}" ]; do
    printf '%s\t%s\t%s\t%s\n' "${PF_NOS[${_pf_i}]}" "${PF_IDS[${_pf_i}]}" "${PF_FILES[${_pf_i}]}" "${PF_ALIASES[${_pf_i}]}"
    _pf_i=$((_pf_i + 1))
  done
}

# 按登记表顺序执行(--only / --from 只是筛选,不改顺序)。段函数不带参数调用;本函数的局部变量都带 _pf_ 前缀,
#   段代码里的同名全局变量不会和循环计数打架(bash 是动态作用域)。
#   --only / --from 的号不在登记表里 → 返回 2(一段不跑);选中零段同样返回 2。PF_RAN = 本轮实际跑了几段。
pf_run(){
  pf_load
  pf_check_selection || return 2
  # 选段参数的反向自证([预检自身结构] 段)用:子进程只验参数、不跑任何段(防自证递归调起整轮预检);正常运行从不设它
  if [ "${HOROSA_PF_ARGS_PROBE:-}" = "1" ]; then echo "选段参数已通过校验(自证子进程,不跑段)"; pf_exit 97; fi
  pf_check_registry
  pf_shell_rs_check
  pf_src_set_check
  local _pf_i=0 _pf_n=${#PF_IDS[@]} _pf_on=1
  [ -n "${PF_FROM}" ] && _pf_on=0
  PF_RAN=0
  while [ "${_pf_i}" -lt "${_pf_n}" ]; do
    PF_ID="${PF_IDS[${_pf_i}]}"; PF_NO="${PF_NOS[${_pf_i}]}"
    _pf_i=$((_pf_i + 1))
    [ "${PF_NO}" = "${PF_FROM}" ] && _pf_on=1
    [ "${_pf_on}" = "1" ] || continue
    if [ -n "${PF_ONLY}" ]; then
      case ",${PF_ONLY}," in *",${PF_NO},"*) ;; *) continue ;; esac
    fi
    PF_RAN=$((PF_RAN + 1))
    "seg_${PF_ID}"
    pf_rs_split_check
  done
  PF_ID=""; PF_NO=""
  [ "${PF_RAN}" -gt 0 ] || { echo "一段都没选中(--only / --from 与登记表对不上)" >&2; return 2; }
  return 0
}

# 本预检自身全文(入口 + 公共库 + 所用登记表 + 本轮装载的全部段文件,再加一张「# [段号]」清单):
#   给「读本预检自身」的段用(台账引用的段号是否存在、开关读点、自身代码行扫描)。本轮只拼一次(PF_TMP 里),退出时随目录删掉。
pf_self(){
  local _pf_f="${PF_TMP}/self" _pf_x
  if [ ! -s "${_pf_f}" ]; then
    {
      [ "${#PF_SELF_FILES[@]}" -gt 0 ] && cat "${PF_SELF_FILES[@]}" 2>/dev/null </dev/null
      for _pf_x in "${PF_NOS[@]}"; do printf '# [%s]\n' "${_pf_x}"; done
      for _pf_x in $(printf '%s\n' "${PF_ALIASES[@]}" | tr ',' ' '); do printf '# [%s]\n' "${_pf_x}"; done
    } > "${_pf_f}"
  fi
  printf '%s' "${_pf_f}"
}

# ── 段内常用判据(各段原先各抄一份,收拢到这里;报错文案带本段段号 ${PF_NO},并置本段 S<id>_BAD=1)──
# pf_code [-q | --fullline] <文件>:剥掉 // 注释后的代码文本(拆成子模块的门面按全集读,见 pf_src_set)。缺省剥行尾 // 起的部分;-q 同上且文件不在时不报错;
#   --fullline 只剥整行 // 注释(行内的 // 保留,适合含 URL 的文件)。
pf_code(){
  case "$1" in
    -q) sed -E 's#//.*$##' "$(pf_src_set "$2")" 2>/dev/null ;;
    --fullline) sed -E 's#^[[:space:]]*//.*$##' "$(pf_src_set "$2")" ;;
    *) sed -E 's#//.*$##' "$(pf_src_set "$1")" ;;
  esac
}
# pf_has <文件> <字面>:剥注释后含该字面(grep -F)。pf_need / pf_none / pf_once <文件> <字面> <消息>:
#   必须含 / 必须不含 / 必须恰好一处,否则 bad "[段号] 消息"。
pf_has(){ [ "$(pf_code -q "$1" | grep -acF -- "$2")" != "0" ]; }
pf_seg_bad(){ bad "[${PF_NO}] $1"; eval "S${PF_ID}_BAD=1"; }
pf_need(){ pf_has "$1" "$2" || pf_seg_bad "$3"; }
pf_none(){ [ "$(pf_code -q "$1" | grep -acF -- "$2")" = "0" ] || pf_seg_bad "$3"; }
pf_once(){ [ "$(pf_code -q "$1" | grep -acF -- "$2")" = "1" ] || pf_seg_bad "$3"; }
# pf_imports <文件> <import 语句>:按 AST 判该文件(门面按全集逐文件)从语句里写的来源导入了语句里的每个名字(本地名相同)——
#   与同一条里还有哪些名字、先后、换行、注释都无关(整行字面锚往同一条 import 里加一个名字就假红,写在注释里又假绿)。
#   解析与 jest 同一份助手(preflight/import_specs.js → astrostudyui/src/utils/__tests__/helpers/importSpecs.js)。缺 → 退出非 0。
#   静态检查 check_preflight_structure.py ⑩:段里拿 grep / pf_has 一类按字面认 import 语句 = 红,一律改调它。
PF_IMPORT_SPECS_JS="${PF_DIR}/import_specs.js"
pf_imports(){ node "${PF_IMPORT_SPECS_JS}" "${REPO_ROOT}/Horosa-Web/astrostudyui" "$1" "$2" >/dev/null 2>&1; }
# pf_scan_table <根目录>:从标准输入读「相对路径|必含字面量」表(空行跳过),逐行 grep -F(门面按全集读);缺的打印「路径「字面」」。
#   字面量是一条 import 语句(以 import 开头)的,改按 pf_imports 判(只认来源 + 名字)。
#   路径是 .rs 的:只认该文件的产品代码(pf_rs_prod),字面是「测试在位」形状(PF_RS_TEST_SHAPE_RE)的才读整份。
pf_scan_table(){
  local _pf_rel _pf_kw
  while IFS='|' read -r _pf_rel _pf_kw; do
    [ -n "${_pf_rel}" ] || continue
    case "${_pf_kw}" in
      'import '*) pf_imports "$1/${_pf_rel}" "${_pf_kw}" || printf '%s「%s」\n' "${_pf_rel}" "${_pf_kw}" ;;
      *)
        # 壳 Rust 源:产品锚只认产品代码(同文件测试模块里的同名字面不替产品作证);测试在位形状读整份
        if [ "${_pf_rel%.rs}" != "${_pf_rel}" ] && ! [[ "${_pf_kw}" =~ ${PF_RS_TEST_SHAPE_RE} ]]; then
          grep -qF -- "${_pf_kw}" "$(pf_rs_prod "$1/${_pf_rel}")" 2>/dev/null || printf '%s「%s」\n' "${_pf_rel}" "${_pf_kw}"
        else
          grep -qF -- "${_pf_kw}" "$(pf_src_set "$1/${_pf_rel}")" 2>/dev/null || printf '%s「%s」\n' "${_pf_rel}" "${_pf_kw}"
        fi ;;
    esac
  done
}
# pf_private_pair_awk <块名>:私有块配对检查的 awk 程序(只数这个块名的开 / 闭;块内又开别的块 = INTERLEAVE;
#   没收尾 = UNCLOSED;开闭数不等 = UNBALANCED;都对 = OK)。end 规则排在「任意块名」规则之前,否则 end 会被当成块名吞掉。
pf_private_pair_awk(){
  local _pf_mk='@horosa-''private'
  printf '%s' "/${_pf_mk}:$1/{if(open){print \"INTERLEAVE\";exit}open=1;oc++;next} /${_pf_mk}:end/{if(open){open=0;ec++}next} /${_pf_mk}:[a-z]/{if(open){print \"INTERLEAVE\";exit}next} END{if(open)print \"UNCLOSED\"; else if(oc!=ec)print \"UNBALANCED oc=\"oc\" ec=\"ec; else print \"OK\"}"
}
