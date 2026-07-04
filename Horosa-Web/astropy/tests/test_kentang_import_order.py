# -*- coding: utf-8 -*-
"""kentang 双向导入门(两个导入顺序都必须无损;v3.2.0 太乙静默 404 顺序面回归)。

两个方向各在「无真 streamlit」的独立子进程里跑:
  - taiyi_first:今日打包实序(taiyi 排 registry 第 1,真 astropy 先装入)——历史侥幸序;
  - stub_first :事故序(先 import 注桩 adapter,再 import webtaiyisrv 触发真
    astropy 导入)——桩无 dunder 守卫时此序必炸(改前红/改后绿的对赌证据)。

断言三层:全部 adapter 可导入且服务类在位;真 astropy 已装入且非桩;sys.modules
卫生(桩 dunder 拒答生效、无「有模块无服务类」的半截残骸)。
adapter 清单从 registry 推导,不手抄(消 KENTANG_ADAPTERS 类漂移根因)。
"""
import os
import subprocess
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from websrv.kentang.registry import KENTANG_SERVICE_SPECS  # noqa: E402

# 全量 adapter(module, class_name),由 registry 推导
ADAPTERS = [(s["module"], s["class_name"]) for s in KENTANG_SERVICE_SPECS]
# 注桩者:任何 import kinastro_common 的 adapter 都会注桩;用 qizhengkin(kinastro 系)作代表
STUB_INJECTOR = "websrv.webqizhengkinsrv"
ASTROPY_CONSUMER = "websrv.webtaiyisrv"


def _run_order(first_imports):
    code = r'''
import sys
sys.path.insert(0, %r)

class _Blocker:
    def find_spec(self, name, path=None, target=None):
        if name.split('.')[0] == 'streamlit':
            raise ModuleNotFoundError('blocked-by-import-order-test: %%s' %% name)
        return None

sys.meta_path.insert(0, _Blocker())

# 探测面语义对齐(真实缺包 find_spec 返 None,防误伤 optional-deps 探测)
import importlib.util as _ilu
_orig_find_spec = _ilu.find_spec
def _blk_find_spec(name, package=None):
    if name.split('.')[0] == 'streamlit':
        return None
    return _orig_find_spec(name, package)
_ilu.find_spec = _blk_find_spec

ADAPTERS = %r
FIRST = %r

for mod in FIRST:
    __import__(mod)

failures = []
for mod, cls in ADAPTERS:
    try:
        m = __import__(mod, fromlist=[cls])
        if getattr(m, cls, None) is None:
            failures.append('%%s: class %%s missing' %% (mod, cls))
    except Exception as e:
        failures.append('%%s: %%r' %% (mod, e))
assert not failures, 'adapter import failures:\n' + '\n'.join(failures)

# 真 astropy 必须已装入且不是桩
import sys as _s
ap = _s.modules.get('astropy')
assert ap is not None, 'astropy not loaded after webtaiyisrv import'
assert not getattr(ap, '__horosa_slim_stub__', False), 'astropy must be the real package'

# 桩卫生:streamlit 是桩且 dunder 拒答
st = _s.modules.get('streamlit')
assert st is not None and getattr(st, '__horosa_slim_stub__', False)
assert not hasattr(st, '__file__')

# 无半截残骸:registry 各 spec 模块若在 sys.modules 则服务类必在
for mod, cls in ADAPTERS:
    m = _s.modules.get(mod)
    if m is not None:
        assert getattr(m, cls, None) is not None, 'partial module: %%s' %% mod
print('ORDER_OK')
''' % (ROOT, ADAPTERS, first_imports)
    return subprocess.run([sys.executable, '-c', code],
                          capture_output=True, text=True, cwd=ROOT, timeout=600)


@pytest.mark.parametrize('order,first', [
    ('taiyi_first', [ASTROPY_CONSUMER]),
    ('stub_first', [STUB_INJECTOR, ASTROPY_CONSUMER]),
])
def test_kentang_import_order(order, first):
    proc = _run_order(first)
    assert proc.returncode == 0 and 'ORDER_OK' in proc.stdout, (
        '[%s] stdout=%s\nstderr=%s' % (order, proc.stdout[-2000:], proc.stderr[-6000:]))
