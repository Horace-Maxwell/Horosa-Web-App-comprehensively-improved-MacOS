# -*- coding: utf-8 -*-
"""streamlit 兼容桩 dunder 守卫哨兵(v3.2.0 太乙静默 404 事故的根因层回归)。

事故链:桩 __getattr__ 对一切属性返回 _noop 函数 → inspect.getmodule() 遍历
sys.modules 读各模块 __file__(期望 str)→ 拿到函数 → 真 astropy 导入期内省炸
AttributeError → kintaiyi 导入永久失败 → CherryPy dispatcher 把 AttributeError
当「无此路由」→ /taiyi/pan 整进程静默 404。

守卫语义(stub_dunder_guard_v1):dunder 探测一律按「属性不存在」拒答(raise
AttributeError),具名属性照旧 noop;子桩(components/v1)带显式 __horosa_slim_stub__
实例属性。本测试在「无真 streamlit」的独立子进程里验证桩本体行为。
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def _run_blocked(code):
    """meta_path 阻断 streamlit 的独立解释器里执行 code(沿用 test_runtime_deps_slim 模式)。"""
    wrapper = r'''
import sys
sys.path.insert(0, %r)

class _Blocker:
    def find_spec(self, name, path=None, target=None):
        if name.split('.')[0] == 'streamlit':
            raise ModuleNotFoundError('blocked-by-stub-guard-test: %%s' %% name)
        return None

sys.meta_path.insert(0, _Blocker())

# 探测面语义对齐(真实缺包 find_spec 返 None)
import importlib.util as _ilu
_orig_find_spec = _ilu.find_spec
def _blk_find_spec(name, package=None):
    if name.split('.')[0] == 'streamlit':
        return None
    return _orig_find_spec(name, package)
_ilu.find_spec = _blk_find_spec
%s
''' % (ROOT, code)
    return subprocess.run([sys.executable, '-c', wrapper],
                          capture_output=True, text=True, cwd=ROOT, timeout=180)


def test_stub_dunder_rejected_named_attrs_noop():
    """dunder 拒答(hasattr False)、具名属性 noop 可调、cache_data 透传装饰。"""
    code = r'''
import websrv.kentang.kinastro_common  # 触发桩注入
import streamlit as st

# 桩标记:显式实例属性,可读
assert st.__horosa_slim_stub__ is True
assert st.components.__horosa_slim_stub__ is True
assert st.components.v1.__horosa_slim_stub__ is True

# dunder 一律按不存在拒答(不返回函数)。注:__loader__/__spec__/__name__ 等由
# ModuleType 构造时写进实例字典(值为 None/名字),属实例属性、不经 __getattr__,
# 不在守卫射程内也无害(str/None 而非函数);只断言真正缺失的 dunder。
for name in ('__file__', '__path__', '__all__'):
    assert not hasattr(st, name), name
try:
    st.__file__
    raise SystemExit('dunder __file__ should raise AttributeError')
except AttributeError:
    pass

# 具名属性照旧 noop 函数
assert callable(st.warning)
assert st.warning('x') is None

# cache_data/resource 透传装饰器语义不变
def _fn(x):
    return x + 1
assert st.cache_data(_fn) is _fn
assert st.cache_data(ttl=60)(_fn) is _fn
assert st.cache_resource(_fn) is _fn
print('STUB_GUARD_OK')
'''
    proc = _run_blocked(code)
    assert proc.returncode == 0 and 'STUB_GUARD_OK' in proc.stdout, (
        'stdout=%s\nstderr=%s' % (proc.stdout[-2000:], proc.stderr[-4000:]))


def test_stub_survives_stdlib_introspection():
    """inspect/pkgutil 级 sys.modules 全量内省在桩在场时不抛(事故的直接触发面)。"""
    code = r'''
import websrv.kentang.kinastro_common  # 注桩
import inspect, sys

def _probe():
    return 0

# inspect.getmodule 会遍历 sys.modules 逐个读 __file__ —— 桩在场必须无害
mod = inspect.getmodule(_probe)
assert mod is not None

# 手工重放遍历(比 getmodule 更苛刻:显式逐模块读 __file__)
for name, m in list(sys.modules.items()):
    try:
        f = getattr(m, '__file__', None)
    except Exception as e:
        raise SystemExit('module %r __file__ raised %r' % (name, e))
    if f is not None and not isinstance(f, str):
        raise SystemExit('module %r __file__ is %r (non-str!)' % (name, type(f)))
print('INTROSPECT_OK')
'''
    proc = _run_blocked(code)
    assert proc.returncode == 0 and 'INTROSPECT_OK' in proc.stdout, (
        'stdout=%s\nstderr=%s' % (proc.stdout[-2000:], proc.stderr[-4000:]))
