# -*- coding: utf-8 -*-
"""身份握手端点 /horosaIdentity 回归。

背景:本地服务地址(query/存储/端口推导)一旦指向被其它进程占用的端口,「毒 200」会被
前端误判成服务未就绪且重试死循环。前端自愈依赖本端点返回稳定的 app 标记 + 壳注入的
启动 nonce(HOROSA_LAUNCH_NONCE)——本测试钉死其响应契约:
  · app == 'horosa-chart'(与 Java 侧 'horosa-backend' 区分);
  · proto == 1;
  · nonce 原样回显且只允许 [A-Za-z0-9_-](其余字符过滤,无注入面);
  · 无 nonce 环境(浏览器直连 dev)回空串。
"""
import json


def _call_identity():
    import websrv.webchartsrv as srv
    return json.loads(srv.WebChartSrv().horosaIdentity())


def test_horosa_identity_marker_and_nonce_roundtrip(monkeypatch):
    monkeypatch.setenv('HOROSA_LAUNCH_NONCE', 'abc123-XY_z')
    data = _call_identity()
    assert data['app'] == 'horosa-chart'
    assert data['proto'] == 1
    assert data['nonce'] == 'abc123-XY_z'


def test_horosa_identity_filters_unsafe_nonce_chars(monkeypatch):
    monkeypatch.setenv('HOROSA_LAUNCH_NONCE', 'ab"c\\1<2>3&空 白')
    data = _call_identity()
    assert data['nonce'] == 'abc123'


def test_horosa_identity_without_nonce(monkeypatch):
    monkeypatch.delenv('HOROSA_LAUNCH_NONCE', raising=False)
    data = _call_identity()
    assert data['app'] == 'horosa-chart'
    assert data['nonce'] == ''
