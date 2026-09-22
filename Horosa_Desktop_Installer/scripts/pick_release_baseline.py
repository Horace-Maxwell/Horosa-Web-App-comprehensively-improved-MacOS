#!/usr/bin/env python3
"""发布链·增量部件复用基线的挑选 / 校验 / 顺序自检(publish_github_release.sh 的纯函数部分,可单测)。

背景:发布脚本从 v3.1.0 起「先建新 release(立刻成为 latest)→ 再去 releases/latest 取上一版清单当基线」,
取到的恒是刚建好、还没有清单的新 release → 基线恒空 → 部件全量重传、差分效率门形同虚设;仓库不公开时匿名
download 地址还恒 404。现在改为:建 release **之前**,经认证 API 列 releases,挑「非本次 tag / 非 runtime tag /
非 draft / 带清单资产(发正式版时还要非预发布)」里最新的一版,再经资产 API 下载它的清单。

四种子命令(输出一律单行 JSON 或纯文本,给 bash 用):
  --pick            stdin 或 --releases-file 给 releases 列表 JSON → {"state","tag","asset_url","published_at","reason"}
                    state ∈ ok | first(仓里没有任何别的 release = 真首发)| none_eligible(有别的 release 但都没清单资产)
                          | fetch_failed(列表拿不到 / 不是 JSON)
  --verify-manifest stdin 给下载到的清单 → 纯文本 ok | self(取到的是本次自己的清单 = 挑选逻辑有误)
                    | no_v2(没有 components 段 = 旧格式)| unparsable
  --lint <script>   静态核对发布脚本的顺序不变量(基线在建 release 之前取 / 清单最后上传 / 转正在清单之后 / 旧写法零残留)
  --self-test       全部判别向量(含「顺序不变量对被改坏的脚本必红」)
"""
import argparse
import json
import sys


def _load_releases(text):
    try:
        data = json.loads(text or '')
    except Exception:
        return None
    return data if isinstance(data, list) else None


def pick(releases, tag, runtime_tag, manifest_name, prerelease):
    """挑基线。releases 为 GitHub /releases 列表(任意顺序);返回 dict。"""
    if releases is None:
        return {'state': 'fetch_failed', 'tag': '', 'asset_url': '', 'published_at': '', 'reason': 'releases 列表拿不到或不是 JSON'}
    own = {tag, runtime_tag}
    others = [r for r in releases if isinstance(r, dict) and not r.get('draft') and r.get('tag_name') and r.get('tag_name') not in own]
    if not others:
        return {'state': 'first', 'tag': '', 'asset_url': '', 'published_at': '', 'reason': '仓里没有别的已发布 release'}
    want_stable = str(prerelease).lower() != 'true'
    eligible = []
    for r in others:
        if want_stable and r.get('prerelease'):
            continue
        asset = next((a for a in (r.get('assets') or []) if isinstance(a, dict) and a.get('name') == manifest_name), None)
        if not asset or not asset.get('url'):
            continue
        eligible.append((str(r.get('published_at') or r.get('created_at') or ''), r.get('tag_name'), asset.get('url')))
    if not eligible:
        return {'state': 'none_eligible', 'tag': '', 'asset_url': '', 'published_at': '',
                'reason': '别的 release 都没有清单资产' + ('(或都是预发布)' if want_stable else '')}
    eligible.sort(reverse=True)
    published_at, best_tag, url = eligible[0]
    return {'state': 'ok', 'tag': best_tag, 'asset_url': url, 'published_at': published_at, 'reason': ''}


def verify_manifest(text, tag, version):
    try:
        m = json.loads(text or '')
    except Exception:
        return 'unparsable'
    if not isinstance(m, dict):
        return 'unparsable'
    if m.get('tag') == tag or m.get('version') == version:
        return 'self'
    has_comps = any(isinstance(e, dict) and e.get('components') for e in (m.get('platforms') or {}).values())
    return 'ok' if has_comps else 'no_v2'


# ── 发布脚本顺序不变量(锚是脚本里的字面行;改了脚本要同步改这里,preflight 每次都跑) ──
BASELINE_LINE = 'BASELINE_STATE="$('
ENSURE_APP_LINE = 'ensure_release "${TAG_NAME}"'
OLD_BASELINE_CURL = 'PREV_MANIFEST_JSON="$(curl -fsSL -H \'Cache-Control: no-cache\' "https://github.com/'
COMPONENTS_DONE_LINE = 'components uploaded (incremental set)'
MANIFEST_UPLOAD_LINE = 'replace_asset "${APP_RELEASE_ID}" "${APP_UPLOAD_URL}" "${DIST_ROOT}/${UPDATE_MANIFEST_NAME}"'
PUBLISH_LINE = 'publish_release "${APP_RELEASE_ID}"'
DRAFT_CREATE_LINE = "'draft': os.environ['DRAFT_ENV'] == 'true'"
SELF_GUARD_LINE = 'self) echo "❌ 部件复用基线取到了本次发布自己'
OFFLINE_UPLOAD_LINE = 'replace_asset "${APP_RELEASE_ID}" "${APP_UPLOAD_URL}" "${DIST_ROOT}/${DESKTOP_OFFLINE_PKG}"'


def lint(text):
    """回 [] = 全部不变量成立;否则每条一句话。"""
    problems = []

    def first(needle):
        i = text.find(needle)
        return i if i >= 0 else None

    b, e = first(BASELINE_LINE), first(ENSURE_APP_LINE)
    if b is None:
        problems.append('缺基线取回段(BASELINE_STATE=)')
    if e is None:
        problems.append('缺 ensure_release "${TAG_NAME}" 调用')
    if b is not None and e is not None and not b < e:
        problems.append('基线必须在 ensure_release "${TAG_NAME}" 之前取(现在在之后 → 取到的是新 release 自己)')
    if first(OLD_BASELINE_CURL) is not None:
        problems.append('旧写法残留:PREV_MANIFEST_JSON 直接 curl releases/latest/download(仓库不公开时恒 404、新版已成 latest 后恒空)')
    c, m, p = first(COMPONENTS_DONE_LINE), first(MANIFEST_UPLOAD_LINE), first(PUBLISH_LINE)
    if m is None:
        problems.append('缺清单上传行(replace_asset … UPDATE_MANIFEST_NAME)')
    if c is None:
        problems.append('缺部件上传完成标记')
    if c is not None and m is not None and not c < m:
        problems.append('清单必须在增量部件之后上传(清单一上线在线用户就会去下部件)')
    o = first(OFFLINE_UPLOAD_LINE)
    if o is not None and m is not None and not o < m:
        problems.append('清单必须在安装包之后上传')
    if p is None:
        problems.append('缺 publish_release(draft 转正)')
    if p is not None and m is not None and not m < p:
        problems.append('转正(publish_release)必须在清单上传之后')
    if first(DRAFT_CREATE_LINE) is None:
        problems.append('ensure_release 不再支持以 draft 建 release')
    if first(SELF_GUARD_LINE) is None:
        problems.append('缺「基线取到自己」硬拒分支')
    return problems


# ── 自检 ─────────────────────────────────────────────────────────────────────
def _rel(tag, published, assets=(), draft=False, prerelease=False):
    return {'tag_name': tag, 'published_at': published, 'draft': draft, 'prerelease': prerelease,
            'assets': [{'name': n, 'url': f'https://api.example/assets/{tag}/{n}'} for n in assets]}


GOOD_SCRIPT = '\n'.join([
    'x=1',
    'BASELINE_STATE="$(pick)"',
    'self) echo "❌ 部件复用基线取到了本次发布自己" >&2; exit 1 ;;',
    'ensure_release "${TAG_NAME}" a b c d "true"',
    "  'draft': os.environ['DRAFT_ENV'] == 'true',",
    'echo "components uploaded (incremental set)"',
    'replace_asset "${APP_RELEASE_ID}" "${APP_UPLOAD_URL}" "${DIST_ROOT}/${DESKTOP_OFFLINE_PKG}"',
    'replace_asset "${APP_RELEASE_ID}" "${APP_UPLOAD_URL}" "${DIST_ROOT}/${UPDATE_MANIFEST_NAME}"',
    'publish_release "${APP_RELEASE_ID}" "${APP_MAKE_LATEST}" "${RELEASE_PRERELEASE}"',
])


def self_test():
    M = 'horosa-latest.json'
    # 1. 正常:最新一版(非本 tag)带清单 → ok,且挑的是 published_at 最新的,不是列表第一个
    rels = [
        _rel('v3.11.0', '2026-09-21T20:21:00Z', [M]),            # 本次自己(已存在的同 tag 重发场景)
        _rel('v3.11.0-runtime1', '2026-09-21T20:20:00Z', ['x.tar.gz']),
        _rel('v3.9.4', '2026-08-20T00:00:00Z', [M]),
        _rel('v3.10.0', '2026-09-01T00:00:00Z', [M]),
        _rel('v3.10.0-runtime1', '2026-09-01T00:00:00Z', ['comp.tar.gz']),
    ]
    r = pick(rels, 'v3.11.0', 'v3.11.0-runtime1', M, 'false')
    assert r['state'] == 'ok' and r['tag'] == 'v3.10.0' and r['asset_url'].endswith('/v3.10.0/' + M), r
    # 2. 本次 tag 若是列表里唯一带清单的 → 不能选自己:别的 release 存在但无清单 → none_eligible
    r = pick([_rel('v3.11.0', '2026-09-21T20:21:00Z', [M]), _rel('v3.11.0-runtime1', '2026-09-21', ['a'])], 'v3.11.0', 'v3.11.0-runtime1', M, 'false')
    assert r['state'] == 'first', r
    r = pick([_rel('v3.11.0', '2026-09-21T20:21:00Z', [M]), _rel('v3.10.0', '2026-09-01', ['only-runtime.tar.gz'])], 'v3.11.0', 'v3.11.0-runtime1', M, 'false')
    assert r['state'] == 'none_eligible', r
    # 3. 空列表 / 非 JSON → first / fetch_failed
    assert pick([], 'v1', 'v1-runtime1', M, 'false')['state'] == 'first'
    assert pick(None, 'v1', 'v1-runtime1', M, 'false')['state'] == 'fetch_failed'
    assert _load_releases('not json') is None and _load_releases('{"a":1}') is None and _load_releases('[]') == []
    # 4. draft 一律跳过(上次中途失败留下的 draft 没有 tag、没有完整资产)
    r = pick([_rel('v3.10.0', '2026-09-01', [M], draft=True), _rel('v3.9.4', '2026-08-20', [M])], 'v3.11.0', 'v3.11.0-runtime1', M, 'false')
    assert r['state'] == 'ok' and r['tag'] == 'v3.9.4', r
    # 5. 发正式版:预发布不作基线;发预发布:可以拿预发布当基线
    r = pick([_rel('v3.10.1-beta', '2026-09-10', [M], prerelease=True), _rel('v3.10.0', '2026-09-01', [M])], 'v3.11.0', 'v3.11.0-runtime1', M, 'false')
    assert r['tag'] == 'v3.10.0', r
    r = pick([_rel('v3.10.1-beta', '2026-09-10', [M], prerelease=True), _rel('v3.10.0', '2026-09-01', [M])], 'v3.11.0', 'v3.11.0-runtime1', M, 'true')
    assert r['tag'] == 'v3.10.1-beta', r
    # 6. 清单校验:自己 / 旧格式 / 正常 / 坏文本
    comps = {'platforms': {'macos-arm64': {'components': [{'name': 'a', 'sha256': 'x'}]}}}
    assert verify_manifest(json.dumps({'version': '3.11.0', 'tag': 'v3.11.0', **comps}), 'v3.11.0', '3.11.0') == 'self'
    assert verify_manifest(json.dumps({'version': '3.10.0', 'tag': 'v3.10.0', 'platforms': {'macos-arm64': {}}}), 'v3.11.0', '3.11.0') == 'no_v2'
    assert verify_manifest(json.dumps({'version': '3.10.0', 'tag': 'v3.10.0', **comps}), 'v3.11.0', '3.11.0') == 'ok'
    assert verify_manifest('<html>404', 'v3.11.0', '3.11.0') == 'unparsable'
    assert verify_manifest('[1,2]', 'v3.11.0', '3.11.0') == 'unparsable'
    # 7. 顺序不变量:好脚本零问题;每一种改坏都必红
    assert lint(GOOD_SCRIPT) == [], lint(GOOD_SCRIPT)
    lines = GOOD_SCRIPT.split('\n')
    def swap(a, b):
        ls = lines[:]
        ls[a], ls[b] = ls[b], ls[a]
        return '\n'.join(ls)
    assert any('之前取' in p for p in lint(swap(1, 3))), '基线挪到 ensure_release 之后必须判红'
    assert any('旧写法残留' in p for p in lint(GOOD_SCRIPT + '\nPREV_MANIFEST_JSON="$(curl -fsSL -H \'Cache-Control: no-cache\' "https://github.com/o/r/releases/latest/download/m.json" 2>/dev/null || true)"')), '旧 curl 回潮必须判红'
    assert any('增量部件之后' in p for p in lint(swap(5, 7))), '清单先于部件必须判红'
    assert any('安装包之后' in p for p in lint(swap(6, 7))), '清单先于安装包必须判红'
    assert any('清单上传之后' in p for p in lint(swap(7, 8))), '转正先于清单必须判红'
    assert any('draft' in p for p in lint(GOOD_SCRIPT.replace(DRAFT_CREATE_LINE, ''))), '去掉 draft 建法必须判红'
    assert any('硬拒' in p for p in lint(GOOD_SCRIPT.replace('self) echo "❌ 部件复用基线取到了本次发布自己', 'self) :'))), '去掉自取硬拒必须判红'
    assert any('缺清单上传行' in p for p in lint(GOOD_SCRIPT.replace(MANIFEST_UPLOAD_LINE, ''))), '删掉清单上传必须判红'
    print('pick_release_baseline self-test: OK (7 组判别向量)')


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pick', action='store_true')
    ap.add_argument('--verify-manifest', action='store_true')
    ap.add_argument('--lint', metavar='SCRIPT')
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--releases-file')
    ap.add_argument('--tag', default='')
    ap.add_argument('--runtime-tag', default='')
    ap.add_argument('--version', default='')
    ap.add_argument('--manifest-name', default='horosa-latest.json')
    ap.add_argument('--prerelease', default='false')
    a = ap.parse_args(argv)
    if a.self_test:
        self_test()
        return 0
    if a.lint:
        with open(a.lint, encoding='utf-8') as fh:
            problems = lint(fh.read())
        for p in problems:
            print('LINT: ' + p)
        print('LINT: OK' if not problems else f'LINT: {len(problems)} 处不合')
        return 0 if not problems else 1
    if a.pick:
        if a.releases_file:
            with open(a.releases_file, encoding='utf-8') as fh:
                text = fh.read()
        else:
            text = sys.stdin.read()
        print(json.dumps(pick(_load_releases(text), a.tag, a.runtime_tag, a.manifest_name, a.prerelease), ensure_ascii=False))
        return 0
    if a.verify_manifest:
        print(verify_manifest(sys.stdin.read(), a.tag, a.version))
        return 0
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
