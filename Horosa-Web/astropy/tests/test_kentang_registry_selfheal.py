# -*- coding: utf-8 -*-
"""registry 加载守卫哨兵:sys.modules 污染自愈 + 失败类型永不落入静默 404 路径。

对应 registry.KENTANG_LAZY_MOUNT_SELF_HEAL 守卫:
  1) 半截缓存(模块在 sys.modules 但服务类缺失)→ purge(含引擎前缀)→ 重导成功;
  2) 重导仍失败 → raise KentangServiceLoadError(RuntimeError 而非 AttributeError:
     CherryPy dispatcher 用 getattr 吞 AttributeError 成永久 404,类型隔离是底线);
  3) purge 保护白名单:engine 命中公共包前缀(astropy 等)绝不被误清。
用临时目录里的合成 adapter 模块做靶,不碰真 vendor(轻、稳、无环境依赖)。
"""
import os
import sys
import types

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from websrv.kentang import registry  # noqa: E402


@pytest.fixture()
def synth_adapter(tmp_path):
    """磁盘上真实存在的合成 adapter:fake_selfheal_adapter.FakeSrv。"""
    mod_path = tmp_path / "fake_selfheal_adapter.py"
    mod_path.write_text(
        "class FakeSrv:\n"
        "    def __init__(self):\n"
        "        self.ok = True\n",
        encoding="utf-8",
    )
    sys.path.insert(0, str(tmp_path))
    try:
        yield {
            "key": "fake",
            "engine": "fake_engine_pkg",
            "mount": "/fake",
            "module": "fake_selfheal_adapter",
            "class_name": "FakeSrv",
        }
    finally:
        sys.path.remove(str(tmp_path))
        for k in list(sys.modules):
            if k.startswith("fake_selfheal_adapter") or k.startswith("fake_engine_pkg"):
                sys.modules.pop(k, None)


def test_poisoned_partial_module_self_heals(synth_adapter):
    """sys.modules 里塞「无服务类的半截模块」→ 守卫 purge 后从磁盘重导成功。"""
    poisoned = types.ModuleType("fake_selfheal_adapter")  # 没有 FakeSrv
    sys.modules["fake_selfheal_adapter"] = poisoned
    # 引擎前缀残骸也应一并被清
    sys.modules["fake_engine_pkg"] = types.ModuleType("fake_engine_pkg")
    sys.modules["fake_engine_pkg.sub"] = types.ModuleType("fake_engine_pkg.sub")

    module = registry._import_kentang_service_module(synth_adapter)
    assert getattr(module, "FakeSrv", None) is not None
    assert module is not poisoned, "应从干净状态重导,而非沿用半截缓存"
    assert "fake_engine_pkg" not in sys.modules
    assert "fake_engine_pkg.sub" not in sys.modules
    svc = registry._load_service(synth_adapter)
    assert svc.ok is True


def test_still_broken_raises_loaderror_not_attributeerror(tmp_path):
    """磁盘上根本没有服务类 → KentangServiceLoadError(绝非 AttributeError)。"""
    mod_path = tmp_path / "fake_classless_adapter.py"
    mod_path.write_text("VALUE = 1\n", encoding="utf-8")
    sys.path.insert(0, str(tmp_path))
    spec = {
        "key": "classless",
        "engine": "classless_engine",
        "mount": "/classless",
        "module": "fake_classless_adapter",
        "class_name": "MissingSrv",
    }
    try:
        with pytest.raises(registry.KentangServiceLoadError) as exc_info:
            registry._import_kentang_service_module(spec)
        assert not isinstance(exc_info.value, AttributeError)
        assert isinstance(exc_info.value, RuntimeError)
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("fake_classless_adapter", None)


def test_import_crash_raises_loaderror(tmp_path):
    """import 本身抛错(且重试仍抛)→ KentangServiceLoadError,响亮而非静默。"""
    mod_path = tmp_path / "fake_crash_adapter.py"
    mod_path.write_text("raise ValueError('boom-on-import')\n", encoding="utf-8")
    sys.path.insert(0, str(tmp_path))
    spec = {
        "key": "crash",
        "engine": "crash_engine",
        "mount": "/crash",
        "module": "fake_crash_adapter",
        "class_name": "CrashSrv",
    }
    try:
        with pytest.raises(registry.KentangServiceLoadError):
            registry._import_kentang_service_module(spec)
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("fake_crash_adapter", None)


def test_purge_protect_whitelist_spares_common_packages(synth_adapter):
    """engine 前缀命中公共包(白名单)时绝不误清:sys 顶层公共包对象保持同一身份。"""
    spec = dict(synth_adapter)
    spec["engine"] = "astropy"  # 恶意/误配 engine 指向公共包前缀
    poisoned = types.ModuleType("fake_selfheal_adapter")
    sys.modules["fake_selfheal_adapter"] = poisoned
    marker = types.ModuleType("astropy.fake_probe_submodule")
    sys.modules["astropy.fake_probe_submodule"] = marker
    before = sys.modules.get("astropy")
    try:
        module = registry._import_kentang_service_module(spec)
        assert getattr(module, "FakeSrv", None) is not None
        assert sys.modules.get("astropy") is before, "白名单公共包不得被 purge"
        assert sys.modules.get("astropy.fake_probe_submodule") is marker
    finally:
        sys.modules.pop("astropy.fake_probe_submodule", None)
