# -*- coding: utf-8 -*-
"""
神易數兵占系統 - Streamlit App
講武全書兵占卷之十六 明州玄谷蔡時宜撰

參考 https://github.com/kentang2017/kinliuren 起盤設計顯示
"""

import streamlit as st
import pendulum as pdlm
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from shenyishu import Shenyishu

@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write
        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret
        stdout.write = new_write
        yield

st.set_page_config(
    layout="wide",
    page_title="神易數 - 兵占排盤",
    page_icon="⚔️"
)

# ── Sidebar: Date & Time Selection ──────────────────────────────
with st.sidebar:
    st.header("日期與時間選擇")

    default_datetime = pdlm.now(tz='Asia/Hong_Kong')

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        y = st.number_input(
            "年",
            min_value=1900,
            max_value=2100,
            value=default_datetime.year,
            step=1,
            help="輸入年份 (1900-2100)"
        )
    with col2:
        m = st.number_input(
            "月",
            min_value=1,
            max_value=12,
            value=default_datetime.month,
            step=1,
            help="輸入月份 (1-12)"
        )
    with col3:
        d = st.number_input(
            "日",
            min_value=1,
            max_value=31,
            value=default_datetime.day,
            step=1,
            help="輸入日期 (1-31)"
        )

    h = st.number_input(
        "時",
        min_value=0,
        max_value=23,
        value=default_datetime.hour,
        step=1,
        help="輸入小時 (0-23)"
    )

    st.subheader("快速選擇")
    if st.button("現在"):
        now = pdlm.now(tz='Asia/Hong_Kong')
        y = now.year
        m = now.month
        d = now.day
        h = now.hour

    try:
        selected_datetime = pdlm.datetime(y, m, d, h, tz='Asia/Hong_Kong')
        st.write(f"已選擇: {y}年{m}月{d}日 {h:02d}時")
    except ValueError:
        st.error("請輸入有效的日期和時間！")

    st.caption("時區: Asia/Hong_Kong")

# ── Tabs ────────────────────────────────────────────────────────
plate_lines = None
pan, plate_tab, readme_tab = st.tabs([' 🧮排盤 ', ' 📄排盤文字 ', ' 📖說明 '])

# ── 排盤 Tab ────────────────────────────────────────────────────
with pan:
    st.header('神易數兵占')
    st.caption('講武全書兵占卷之十六 · 明州玄谷蔡時宜撰')

    try:
        ss = Shenyishu(y, m, d, h)
        result = ss.get_bingzhan_result()

        # ── Text-based plate display (code block) ───────────────
        gz = result["干支"]
        wx = result["五行"]
        total = result["總數"]
        zs = result["總數分析"]
        zk = result["主客判斷"]
        shensha = result["神煞"]
        changsheng = result["長生"]
        jx = result["吉凶"]

        plate_lines = []
        plate_lines.append("=" * 52)
        plate_lines.append("           神 易 數 兵 佔 系 統")
        plate_lines.append("        講武全書兵占卷之十六")
        plate_lines.append("=" * 52)
        plate_lines.append("")
        plate_lines.append(f"  日期︰{result['生辰']}")
        plate_lines.append(f"  干支︰{gz['年']}年  {gz['月']}月  {gz['日']}日  {gz['時']}時")
        plate_lines.append(f"  五行︰{wx['年']}    {wx['月']}    {wx['日']}    {wx['時']}")
        plate_lines.append("")
        plate_lines.append(f"  總數︰{total}")
        plate_lines.append(f"  連山卦︰{result['連山卦']}    歸藏卦︰{result['歸藏卦']}")
        plate_lines.append(f"  八卦︰{'  '.join(result['八卦'])}")
        plate_lines.append("")
        plate_lines.append("  ─────── 兵占 ───────")
        plate_lines.append(f"  百位(主將)︰{zs['百位']['數']} → {zs['百位']['卦']}  {zs['百位']['陰陽']}數")
        plate_lines.append(f"  十位(我兵)︰{zs['十位']['數']} → {zs['十位']['卦']}  {zs['十位']['陰陽']}數")
        plate_lines.append(f"  個位(賊寇)︰{zs['個位']['數']} → {zs['個位']['卦']}  {zs['個位']['陰陽']}數")
        plate_lines.append("")
        plate_lines.append("  ─────── 主客判斷 ───────")
        plate_lines.append(f"  結論︰{zk['結論']}")
        for a in zk["分析"]:
            plate_lines.append(f"    ● {a}")
        plate_lines.append("")
        plate_lines.append("  ─────── 神煞 ───────")
        plate_lines.append(f"  年干︰{shensha['年干']}")
        plate_lines.append(f"  貴人︰{shensha['貴人']}    驛馬︰{shensha['驛馬']}    天財︰{shensha['天財']}")
        plate_lines.append(f"  魁元︰{shensha['魁元']}    羊刃︰{shensha['羊刃']}    正祿︰{shensha['正祿']}")
        plate_lines.append(f"  血光︰{shensha['血光']}    白虎︰{shensha['白虎']}    破碎︰{shensha['破碎']}")
        plate_lines.append(f"  劫殺︰{shensha['劫殺']}    馬帶刀︰{shensha['馬帶刀']}  寶馬︰{shensha['寶馬']}")
        plate_lines.append("")
        plate_lines.append("  ─────── 長生 ───────")
        for k, v in changsheng.items():
            plate_lines.append(f"  {k}︰{'  '.join(v)}")
        plate_lines.append("")
        plate_lines.append("  ─────── 吉凶判斷 ───────")
        plate_lines.append(f"  等級︰{jx['level']}    評分︰{jx['score']}")
        plate_lines.append(f"  結論︰{jx['detail']}")
        if jx["reasons"]:
            plate_lines.append("  理由︰")
            for r in jx["reasons"]:
                plate_lines.append(f"    ● {r}")
        plate_lines.append("")
        plate_lines.append("=" * 52)

        # ── Structured display ───────────────────────────────

        # 干支 & 五行
        st.subheader("干支資訊")
        cols = st.columns(4)
        for idx, (k, v) in enumerate(gz.items()):
            with cols[idx]:
                st.metric(label=f"{k}支", value=v, delta=wx[k])

        # 神卦 display
        st.subheader("神卦")
        col_ls, col_gc = st.columns(2)
        with col_ls:
            st.markdown(
                f"<div style='text-align:center;'>"
                f"<div style='display:inline-block;width:100px;height:100px;"
                f"border:2px solid #d4af37;border-radius:50%;line-height:100px;"
                f"font-size:2.5em;color:#d4af37;'>{result['連山卦']}</div>"
                f"<p style='color:#888;margin-top:8px;'>連山卦</p></div>",
                unsafe_allow_html=True
            )
        with col_gc:
            st.markdown(
                f"<div style='text-align:center;'>"
                f"<div style='display:inline-block;width:100px;height:100px;"
                f"border:2px solid #d4af37;border-radius:50%;line-height:100px;"
                f"font-size:2.5em;color:#d4af37;'>{result['歸藏卦']}</div>"
                f"<p style='color:#888;margin-top:8px;'>歸藏卦</p></div>",
                unsafe_allow_html=True
            )

        # 總數分析
        st.subheader("總數分析 — 兵占")
        st.write(f"**總數: {total}**")
        cols_zs = st.columns(3)
        pos_labels = {"百位": "主將", "十位": "我兵", "個位": "賊寇"}
        for idx, pos in enumerate(["百位", "十位", "個位"]):
            with cols_zs[idx]:
                p = zs[pos]
                st.metric(
                    label=f"{pos} ({pos_labels[pos]})",
                    value=f"{p['數']} → {p['卦']}",
                    delta=f"{p['陰陽']}數"
                )

        # 主客判斷
        st.subheader("主客判斷")
        st.info(f"**{zk['結論']}**")
        for a in zk["分析"]:
            st.write(f"- {a}")

        # 神煞
        st.subheader("神煞")
        cols_ss = st.columns(4)
        shensha_display = {k: v for k, v in shensha.items() if k != "年干"}
        for idx, (k, v) in enumerate(shensha_display.items()):
            with cols_ss[idx % 4]:
                st.markdown(
                    f"<div style='background:rgba(0,0,0,0.2);padding:10px;border-radius:6px;"
                    f"border-left:3px solid #d4af37;margin-bottom:10px;'>"
                    f"<span style='color:#888;font-size:0.9em;'>{k}</span><br>"
                    f"<span style='color:#e8e8e8;font-size:1.1em;font-weight:bold;'>{v}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        # 吉凶判斷
        st.subheader("吉凶判斷")
        level = jx["level"]
        color_map = {
            "大吉": ("#228b22", "🟢"),
            "吉": ("#90ee90", "🟢"),
            "平": ("#ffa500", "🟡"),
            "凶": ("#ff6347", "🔴"),
            "大凶": ("#dc143c", "🔴")
        }
        color, icon = color_map.get(level, ("#ffa500", "🟡"))
        st.markdown(
            f"<div style='text-align:center;padding:20px;border:2px solid {color};"
            f"border-radius:8px;background:rgba(0,0,0,0.2);'>"
            f"<div style='font-size:2.5em;color:{color};'>{icon} {level}</div>"
            f"<div style='color:#888;margin:10px 0;'>評分: {jx['score']}</div>"
            f"<div style='font-size:1.2em;color:#e8e8e8;'>{jx['detail']}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        if jx["reasons"]:
            st.markdown("**理由:**")
            for r in jx["reasons"]:
                if "+" in r:
                    st.markdown(f"- :green[{r}]")
                else:
                    st.markdown(f"- :red[{r}]")

        # Raw data expander
        expander = st.expander("原始資料 (JSON)")
        expander.json(result)

    except Exception as e:
        st.error(f"起盤錯誤: {e}")

# ── 排盤文字 Tab ─────────────────────────────────────────────────
with plate_tab:
    st.header('排盤文字')
    st.caption('講武全書兵占卷之十六 · 明州玄谷蔡時宜撰')
    if plate_lines:
        output = st.empty()
        with st_capture(output.code):
            print("\n".join(plate_lines))
    else:
        st.info("請先完成排盤設定")

# ── 說明 Tab ────────────────────────────────────────────────────
with readme_tab:
    st.header('說明')
    st.markdown("""

### 神易數兵占系統

**神易數**是一套基於《講武全書》卷十六的古代兵占推演系統。本系統運用天干地支、八卦、五行、神煞等傳統易學理論，
對指定時間進行軍事吉凶推演，為研究中國古代兵學與易學的交叉領域提供工具。

#### 功能特色

- 🔮 **干支推演** — 自動計算年、月、日、時四柱干支
- ☯️ **八卦與五行** — 連山卦、歸藏卦、八卦及五行分析
- ⚔️ **兵占** — 總數分析（主將、我兵、賊寇三方對比）
- 🏯 **主客判斷** — 陰陽數理判定主客形勢
- 🌟 **神煞系統** — 貴人、驛馬、天財、魁元、羊刃、正祿、白虎、血光、破碎、劫殺等
- 📊 **吉凶評分** — 綜合評分與等級（大吉、吉、平、凶、大凶）

#### 使用方式

在左側欄選擇日期與時間，排盤結果會自動更新顯示。

#### 參考

- 《講武全書》卷十六 · 明州玄谷蔡時宜撰
- [sxtwl](https://pypi.org/project/sxtwl/) — 壽星天文曆
""")
    st.caption("此項目僅供學術研究與文化傳承之用。")
