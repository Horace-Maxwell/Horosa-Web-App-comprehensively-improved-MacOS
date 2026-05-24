"""
astro/sanshi/qimen.py — 奇門遁甲排盤模組 (Qi Men Dun Jia Divination Module)

奇門遁甲為古代三式之一，以九宮格配置天盤、地盤、八門、九星、八神，
共 1080 局，推斷吉凶方位。

此模組封裝 kinqimen 庫，提供 compute / render 介面。
"""

from __future__ import annotations

import streamlit as st

from astro.i18n import auto_cn

# 九宮排列順序（用於顯示）
GONG_ORDER = ["巽", "離", "坤", "震", "中", "兌", "艮", "坎", "乾"]
GONG_GRID = [
    ["巽", "離", "坤"],
    ["震", "中", "兌"],
    ["艮", "坎", "乾"],
]


def compute_qimen_chart(
    year: int, month: int, day: int,
    hour: int, minute: int,
    method: int = 1,
    timezone: float = 8.0,
    **kwargs,
) -> dict:
    """計算奇門遁甲排盤。

    Parameters
    ----------
    method : int
        1 = 拆補法, 2 = 置閏法
    """
    from kinqimen.kinqimen import Qimen

    q = Qimen(year, month, day, hour, minute)
    result = q.pan(method)
    return result


def render_qimen_chart(chart: dict, after_chart_hook=None):
    """在 Streamlit 中渲染奇門遁甲排盤結果。"""
    st.markdown(f"### 🚪 {auto_cn('奇門遁甲排盤')}")

    # ── 基本資訊 ──
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(auto_cn("排盤方式"), chart.get("排盤方式", ""))
        st.metric(auto_cn("節氣"), chart.get("節氣", ""))
    with col2:
        st.metric(auto_cn("干支"), chart.get("干支", ""))
        st.metric(auto_cn("排局"), chart.get("排局", ""))
    with col3:
        st.metric(auto_cn("局日"), chart.get("局日", ""))
        xunkong = chart.get("旬空", {})
        if xunkong:
            st.metric(auto_cn("旬空"), f"{xunkong.get('日空', '')} / {xunkong.get('時空', '')}")

    st.divider()

    # ── 值符值使 ──
    zhifu = chart.get("值符值使", {})
    if zhifu:
        st.markdown(f"#### {auto_cn('值符值使')}")
        zf_cols = st.columns(3)
        with zf_cols[0]:
            zfg = zhifu.get("值符天干", [])
            st.markdown(f"**{auto_cn('值符天干')}**：{'、'.join(zfg) if isinstance(zfg, list) else zfg}")
        with zf_cols[1]:
            zfx = zhifu.get("值符星宮", [])
            st.markdown(f"**{auto_cn('值符星宮')}**：{'、'.join(zfx) if isinstance(zfx, list) else zfx}")
        with zf_cols[2]:
            zsm = zhifu.get("值使門宮", [])
            st.markdown(f"**{auto_cn('值使門宮')}**：{'、'.join(zsm) if isinstance(zsm, list) else zsm}")

    st.divider()

    # ── 九宮盤（3×3 格局）──
    st.markdown(f"#### {auto_cn('九宮盤')}")

    tian_pan = chart.get("天盤", {})
    di_pan = chart.get("地盤", {})
    men = chart.get("門", {})
    xing = chart.get("星", {})
    shen = chart.get("神", {})

    # Build 3×3 grid
    for row in GONG_GRID:
        cols = st.columns(3)
        for ci, gong in enumerate(row):
            with cols[ci]:
                tp = tian_pan.get(gong, "")
                dp = di_pan.get(gong, "")
                m = men.get(gong, "")
                x = xing.get(gong, "")
                s = shen.get(gong, "")

                if gong == "中":
                    # 中宮
                    st.markdown(
                        f"<div style='border:2px solid #EAB308;border-radius:8px;"
                        f"padding:8px;text-align:center;background:rgba(234,179,8,0.1);'>"
                        f"<b>{auto_cn('中宮')}</b><br>"
                        f"{auto_cn('天乙')}：{chart.get('天乙', '')}<br>"
                        f"{auto_cn('地盤')}：{dp}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div style='border:1px solid #555;border-radius:8px;"
                        f"padding:8px;text-align:center;min-height:120px;'>"
                        f"<b>{gong}</b><br>"
                        f"<span style='color:#EAB308;'>{auto_cn('神')}：{s}</span><br>"
                        f"<span style='color:#A78BFA;'>{auto_cn('星')}：{x}</span><br>"
                        f"<span style='color:#60A5FA;'>{auto_cn('門')}：{m}</span><br>"
                        f"{auto_cn('天')}：{tp} / {auto_cn('地')}：{dp}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    st.divider()

    # ── 馬星 ──
    maxing = chart.get("馬星", {})
    if maxing:
        st.markdown(f"#### {auto_cn('馬星')}")
        mx_cols = st.columns(len(maxing))
        for i, (mk, mv) in enumerate(maxing.items()):
            with mx_cols[i]:
                st.metric(auto_cn(mk), mv)

    # ── 長生運（折疊）──
    cs_data = chart.get("長生運", {})
    if cs_data:
        with st.expander(auto_cn("長生運"), expanded=False):
            tp_cs = cs_data.get("天盤", {})
            for gong, inner in tp_cs.items():
                for stem, phase in inner.items():
                    st.markdown(f"**{gong}**（{stem}）：{phase}")

    if after_chart_hook:
        after_chart_hook()
