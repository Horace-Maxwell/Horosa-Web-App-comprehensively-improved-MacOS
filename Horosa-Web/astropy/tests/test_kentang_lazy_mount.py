# -*- coding: utf-8 -*-
"""kentang 懒挂载(WS-3d)回归:代理转发/单次加载/dunder 拒答/失败响亮/开关/预热。

太乙静默 404 事故(2026-07-04 事故复盘)的机制课在此延续:懒代理的任何失败都必须是
KentangServiceLoadError(CherryPy dispatcher 不吞)而绝不是 AttributeError(会被吞成 404)。
"""
import sys
import types

import pytest

from websrv.kentang import registry
from websrv.kentang.registry import (
    KentangServiceLoadError,
    _LazyMountedService,
    _kentang_lazy_enabled,
    mount_kentang_services,
    prewarm_kentang_services,
)


def _install_fake_module(monkeypatch, module_name, class_name, ctor_calls):
    mod = types.ModuleType(module_name)

    class FakeSrv(object):
        def __init__(self):
            ctor_calls.append(module_name)

        def pan(self, **kwargs):
            return {"ok": True}

        pan.exposed = True

    setattr(mod, class_name, FakeSrv)
    monkeypatch.setitem(sys.modules, module_name, mod)
    return mod


def test_lazy_proxy_loads_once_and_forwards(monkeypatch):
    calls = []
    _install_fake_module(monkeypatch, "tests_fake_lazy_srv", "FakeSrv", calls)
    spec = {"key": "fake", "engine": "fake-engine", "module": "tests_fake_lazy_srv", "class_name": "FakeSrv"}
    proxy = _LazyMountedService(spec)
    assert calls == [], "挂载(构造代理)阶段必须零导入零实例化"
    handler = proxy.pan
    assert handler() == {"ok": True}
    assert getattr(proxy.pan, "exposed", False) is True
    proxy.pan  # 第二次属性访问
    assert calls == ["tests_fake_lazy_srv"], "真服务必须只实例化一次"


def test_lazy_proxy_rejects_dunder_without_loading(monkeypatch):
    calls = []
    _install_fake_module(monkeypatch, "tests_fake_lazy_srv2", "FakeSrv", calls)
    spec = {"key": "fake2", "engine": None, "module": "tests_fake_lazy_srv2", "class_name": "FakeSrv"}
    proxy = _LazyMountedService(spec)
    with pytest.raises(AttributeError):
        proxy.__file__  # noqa: B018 —— inspect 内省场景
    with pytest.raises(AttributeError):
        proxy.__wrapped__  # noqa: B018
    assert calls == [], "dunder 内省绝不触发真加载"


def test_lazy_proxy_load_failure_is_loud_not_404(monkeypatch):
    spec = {"key": "ghost", "engine": None, "module": "tests_no_such_module_xyz", "class_name": "Nope"}
    proxy = _LazyMountedService(spec)
    with pytest.raises(KentangServiceLoadError) as exc_info:
        proxy.pan  # noqa: B018
    assert not isinstance(exc_info.value, AttributeError), (
        "加载失败绝不能是 AttributeError——dispatcher 会吞成永久静默 404(v3.2.0 太乙事故)"
    )
    # 失败不粘死:模块补齐后同一代理可恢复(下个请求重试加载)
    calls = []
    _install_fake_module(monkeypatch, "tests_no_such_module_xyz", "Nope", calls)
    assert proxy.pan() == {"ok": True}


class _FakeTree(object):
    def __init__(self):
        self.mounted = {}
        self.apps = {}

    def mount(self, root, mount):
        self.mounted[mount] = root
        self.apps[mount] = types.SimpleNamespace(root=root)


class _FakeCherrypy(object):
    def __init__(self):
        self.tree = _FakeTree()


def test_mount_lazy_by_default_and_eager_on_killswitch(monkeypatch):
    # 默认(未设 env):懒代理
    monkeypatch.delenv("HOROSA_KENTANG_LAZY", raising=False)
    assert _kentang_lazy_enabled() is True
    fake = _FakeCherrypy()
    mount_kentang_services(fake)
    assert len(fake.tree.mounted) == len(registry.KENTANG_SERVICE_SPECS)
    assert all(isinstance(v, _LazyMountedService) for v in fake.tree.mounted.values())

    # kill-switch:饿加载(逐个真加载——用假加载器避免真拉 18 个 vendor 引擎)
    monkeypatch.setenv("HOROSA_KENTANG_LAZY", "0")
    assert _kentang_lazy_enabled() is False
    loaded = []
    monkeypatch.setattr(registry, "_load_service", lambda spec: loaded.append(spec["key"]) or object())
    fake2 = _FakeCherrypy()
    mount_kentang_services(fake2)
    assert len(loaded) == len(registry.KENTANG_SERVICE_SPECS)
    assert not any(isinstance(v, _LazyMountedService) for v in fake2.tree.mounted.values())


def test_prewarm_loads_all_lazy_roots(monkeypatch):
    calls = []
    _install_fake_module(monkeypatch, "tests_fake_prewarm_srv", "FakeSrv", calls)
    fake = _FakeCherrypy()
    # prewarm 按 KENTANG_SERVICE_SPECS 的 mount 路径查 tree.apps:
    # 前两个挂懒根(用假模块 spec),其余挂真实例(应跳过)。
    specs = registry.KENTANG_SERVICE_SPECS
    for i, spec in enumerate(specs):
        if i < 2:
            fake_spec = dict(spec, module="tests_fake_prewarm_srv", class_name="FakeSrv", engine=None)
            fake.tree.mount(_LazyMountedService(fake_spec), spec["mount"])
        else:
            fake.tree.mount(object(), spec["mount"])
    # prewarm 内部 `import cherrypy` → 注入假模块接管
    monkeypatch.setitem(sys.modules, "cherrypy", fake)
    loaded, failed = prewarm_kentang_services()
    assert loaded == 2, "两个懒根必须被预热成真服务"
    assert failed == 0
    assert calls == ["tests_fake_prewarm_srv", "tests_fake_prewarm_srv"]
    for i, spec in enumerate(specs[:2]):
        root = fake.tree.apps[spec["mount"]].root
        assert object.__getattribute__(root, "_horosa_real") is not None
