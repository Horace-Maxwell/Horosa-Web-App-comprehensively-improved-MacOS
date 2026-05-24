"""
wiki_renderer.py — 占星知識庫 Wiki 渲染器
Astrology Wiki renderer with search, tabs, Plotly timeline, and custom CSS.
"""

from __future__ import annotations

import csv
import difflib
from pathlib import Path
from typing import Any

import streamlit as st

# ── Paths ────────────────────────────────────────────────────────────────────

_WIKI_DIR = Path(__file__).parent / "wiki" / "systems"

# ── CSS ──────────────────────────────────────────────────────────────────────

_WIKI_CSS = """
<style>
/* ── Wiki container ──────────────────────────── */
.wiki-container {
    max-width: 860px;
    margin: 0 auto;
    font-family: "Georgia", "Noto Serif TC", "Source Han Serif", serif;
}

/* ── Section header ──────────────────────────── */
.wiki-header {
    border-left: 4px solid #c8a96e;
    padding: 0.5rem 1rem;
    margin-bottom: 1.2rem;
    background: linear-gradient(90deg, rgba(200,169,110,0.1) 0%, transparent 100%);
}
.wiki-header h1, .wiki-header h2 {
    color: #c8a96e;
    font-weight: 600;
    letter-spacing: 0.04em;
}

/* ── Tag badges ──────────────────────────────── */
.wiki-tag {
    display: inline-block;
    background: rgba(200,169,110,0.15);
    color: #c8a96e;
    border: 1px solid rgba(200,169,110,0.4);
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.78rem;
    margin: 2px 3px;
    font-family: monospace;
}

/* ── Article body ────────────────────────────── */
.wiki-article {
    line-height: 1.85;
    color: #e8e0d0;
}
.wiki-article h2 {
    color: #c8a96e;
    border-bottom: 1px solid rgba(200,169,110,0.3);
    padding-bottom: 0.3rem;
    margin-top: 1.6rem;
}
.wiki-article h3 {
    color: #b0c4a0;
    margin-top: 1.2rem;
}
.wiki-article table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    margin: 0.8rem 0;
}
.wiki-article th {
    background: rgba(200,169,110,0.2);
    color: #c8a96e;
    padding: 6px 10px;
    text-align: left;
    font-weight: 600;
}
.wiki-article td {
    padding: 5px 10px;
    border-bottom: 1px solid rgba(200,169,110,0.15);
}
.wiki-article tr:hover td {
    background: rgba(200,169,110,0.07);
}
.wiki-article blockquote {
    border-left: 3px solid #c8a96e;
    padding: 0.3rem 1rem;
    margin: 0.8rem 0;
    color: #b0a080;
    font-style: italic;
    background: rgba(200,169,110,0.06);
}
.wiki-article code {
    background: rgba(0,0,0,0.3);
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 0.85em;
}
.wiki-article hr {
    border: none;
    border-top: 1px solid rgba(200,169,110,0.25);
    margin: 1.5rem 0;
}

/* ── System card grid ────────────────────────── */
.wiki-card {
    background: rgba(200,169,110,0.07);
    border: 1px solid rgba(200,169,110,0.25);
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
    cursor: pointer;
    transition: border-color 0.2s;
}
.wiki-card:hover {
    border-color: #c8a96e;
}
.wiki-card-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #c8a96e;
}
.wiki-card-subtitle {
    font-size: 0.85rem;
    color: #888;
}
</style>
"""


# ── Data loading (cached) ─────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _load_index() -> list[dict[str, str]]:
    """Load wiki/systems/index.csv and return list of system dicts."""
    idx_path = _WIKI_DIR / "index.csv"
    systems: list[dict[str, str]] = []
    if not idx_path.exists():
        return systems
    with idx_path.open(encoding="utf-8") as f:
        for row in csv.reader(f):
            row = [c.strip() for c in row]
            if not row or row[0].startswith("#") or len(row) < 5:
                continue
            systems.append(
                {
                    "file": row[0],
                    "name_zh": row[1],
                    "name_en": row[2],
                    "category": row[3],
                    "tags": row[4],
                }
            )
    return systems


@st.cache_data(show_spinner=False)
def _load_md(filename: str) -> str:
    """Load and return Markdown content for a given system file (no .md suffix)."""
    path = _WIKI_DIR / f"{filename}.md"
    if not path.exists():
        return f"# ⚠️ 找不到文件 | File not found\n\n`{path}`"
    return path.read_text(encoding="utf-8")


# ── Search ────────────────────────────────────────────────────────────────────

def _search_systems(
    query: str, systems: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Return systems whose name/tags fuzzy-match the query (using difflib)."""
    if not query:
        return systems
    q = query.lower()
    scored: list[tuple[float, dict[str, str]]] = []
    for s in systems:
        haystack = " ".join([s["name_zh"], s["name_en"], s["tags"]]).lower()
        # Direct substring match gets top priority
        if q in haystack:
            scored.append((1.0, s))
            continue
        ratio = difflib.SequenceMatcher(None, q, haystack).ratio()
        scored.append((ratio, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    # Keep any with ratio >= 0.25 or that contain the substring
    return [s for r, s in scored if r >= 0.25]


# ── Category labels ───────────────────────────────────────────────────────────

_CATEGORY_LABELS: dict[str, tuple[str, str]] = {
    "ancient":    ("🏺 古代文明", "🏺 Ancient"),
    "western":    ("🏛️ 西方體系", "🏛️ Western"),
    "indian":     ("🪷 印度體系", "🪷 Indian"),
    "chinese":    ("🏮 中國體系", "🏮 Chinese"),
    "asian":      ("🌏 亞洲體系", "🌏 Asian"),
    "african":    ("🌍 非洲體系", "🌍 African"),
    "indigenous": ("🌿 原住民體系", "🌿 Indigenous"),
    "obscure":   ("🜁 隱祕與原民傳統", "🜁 Obscure & Indigenous"),
    "middle_east":("🕌 中東體系", "🕌 Middle Eastern"),
}


def _cat_label(cat: str, lang: str) -> str:
    label = _CATEGORY_LABELS.get(cat, (cat, cat))
    return label[0] if lang in ("zh", "zh_cn") else label[1]


# ── Timeline data ─────────────────────────────────────────────────────────────

_TIMELINE_EVENTS = [
    # (year, label_zh, label_en, category)
    (-3000, "蘇美爾天文記錄", "Sumerian astronomical records", "ancient"),
    (-1800, "巴比倫占星形成", "Babylonian astrology develops", "ancient"),
    (-1200, "甲骨文天象記錄", "Oracle bone celestial records", "chinese"),
    (-1000, "MUL.APIN 泥板", "MUL.APIN tablets compiled", "ancient"),
    (-500,  "吠陀占星雛形", "Early Vedic astrology (Nakshatras)", "indian"),
    (-334,  "亞歷山大東征", "Alexander's conquests", "western"),
    (-100,  "史記·天官書", "Sima Qian: Treatise on Celestial Offices", "chinese"),
    (150,   "托勒密《四書》", "Ptolemy's Tetrabiblos", "western"),
    (269,   "Yavanajātaka（梵文）", "Yavanajātaka (Sanskrit)", "indian"),
    (618,   "七政四餘成熟（唐）", "Qizheng Siyu matures (Tang Dynasty)", "chinese"),
    (641,   "文成公主入藏", "Princess Wencheng enters Tibet", "asian"),
    (830,   "巴格達智慧之家", "Baghdad House of Wisdom", "western"),
    (1000,  "Picatrix 成書", "Picatrix compiled", "western"),
    (1027,  "時輪金剛傳藏", "Kalachakra transmitted to Tibet", "asian"),
    (1300,  "Rasulid 也門手稿", "Rasulid Hexaglot (Yemen)", "western"),
    (1438,  "印加帝國天文", "Inca imperial astronomy", "indigenous"),
    (1500,  "紫微斗數形成（明）", "Zi Wei Dou Shu forms (Ming)", "chinese"),
    (1647,  "Lilly《基督教占星學》", "Lilly's Christian Astrology", "western"),
    (1860,  "艾倫·利奧現代占星", "Alan Leo: modern astrology", "western"),
    (1925,  "Sabian 符號（Jones）", "Sabian Symbols (Jones/Wheeler)", "western"),
    (1970,  "KP 占星體系", "KP Astrology system", "indian"),
    (1975,  "Jim Lewis 地點占星", "Jim Lewis Astrocartography", "western"),
    (1987,  "Project Hindsight 希臘復興", "Project Hindsight: Hellenistic revival", "western"),
    (2000,  "數位排盤普及", "Digital chart software widespread", "western"),
    (2020,  "AI 整合占星", "AI-integrated astrology platforms", "western"),
]

_CAT_COLORS = {
    "ancient":    "#e8c56e",
    "western":    "#6ea8e8",
    "indian":     "#e88f6e",
    "chinese":    "#e86ea8",
    "asian":      "#6ee8c5",
    "african":    "#a8e86e",
    "indigenous": "#c56ee8",
    "obscure":   "#a67c52",
    "middle_east":"#e8a86e",
}


@st.cache_data(ttl=3600, show_spinner=False)
def _build_timeline_figure(lang: str) -> Any:
    """Build and return a Plotly scatter figure for the timeline."""
    import plotly.graph_objects as go  # lazy import

    years   = [e[0] for e in _TIMELINE_EVENTS]
    labels  = [e[1] if lang in ("zh", "zh_cn") else e[2] for e in _TIMELINE_EVENTS]
    cats    = [e[3] for e in _TIMELINE_EVENTS]
    colors  = [_CAT_COLORS.get(c, "#888") for c in cats]
    hover   = [
        f"<b>{lbl}</b><br>{'年份' if lang in ('zh','zh_cn') else 'Year'}: "
        f"{'公元前 ' if y < 0 else ''}{abs(y)}{'年' if lang in ('zh','zh_cn') else ' CE' if y >= 0 else ' BCE'}"
        for y, lbl in zip(years, labels)
    ]

    y_jitter = [0.0] * len(years)  # flat line, dots hover for labels

    fig = go.Figure()

    # Base timeline line
    fig.add_trace(go.Scatter(
        x=[-3200, 2100], y=[0, 0],
        mode="lines",
        line=dict(color="rgba(200,169,110,0.3)", width=2),
        hoverinfo="skip",
        showlegend=False,
    ))

    # Events
    fig.add_trace(go.Scatter(
        x=years, y=y_jitter,
        mode="markers+text",
        marker=dict(size=10, color=colors, line=dict(width=1, color="#fff")),
        text=labels,
        textposition="top center",
        textfont=dict(size=9),
        customdata=cats,
        hovertemplate="%{hovertext}<extra></extra>",
        hovertext=hover,
        showlegend=False,
    ))

    # Category legend (manual traces)
    shown_cats: set[str] = set()
    for cat, col in _CAT_COLORS.items():
        if cat in set(cats):
            label_zh, label_en = _CATEGORY_LABELS.get(cat, (cat, cat))
            legend_label = label_zh if lang in ("zh", "zh_cn") else label_en
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="markers",
                marker=dict(size=8, color=col),
                name=legend_label,
                showlegend=True,
            ))
            shown_cats.add(cat)

    x_label = "年份（公元前為負數）" if lang in ("zh", "zh_cn") else "Year (negative = BCE)"
    title_text = "📜 占星歷史大事記" if lang in ("zh", "zh_cn") else "📜 Astrology Historical Timeline"

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=15, color="#c8a96e")),
        xaxis=dict(
            title=x_label,
            gridcolor="rgba(200,169,110,0.1)",
            zeroline=True,
            zerolinecolor="rgba(200,169,110,0.4)",
            tickfont=dict(size=10),
        ),
        yaxis=dict(visible=False, range=[-0.8, 2.0]),
        height=300,
        margin=dict(l=20, r=20, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
        ),
    )
    return fig


# ── Main renderer ─────────────────────────────────────────────────────────────

def render_wiki(lang: str = "zh") -> None:
    """
    Main entry point.  Call this from app.py when the user navigates to Wiki.
    
    Parameters
    ----------
    lang : str
        Current language key ("zh", "zh_cn", or "en").
    """
    st.markdown(_WIKI_CSS, unsafe_allow_html=True)

    is_zh = lang in ("zh", "zh_cn")

    # ── Page title
    st.markdown(
        '<div class="wiki-header"><h1>'
        + ("📚 占星知識庫 Wiki" if is_zh else "📚 Astrology Knowledge Wiki")
        + "</h1></div>",
        unsafe_allow_html=True,
    )
    if is_zh:
        st.caption("深入各占星體系的歷史、原理、計算與文化意義")
    else:
        st.caption("Deep dive into the history, principles, calculations, and cultural significance of each system")

    # ── Search bar
    search_placeholder = "🔍 搜尋體系、標籤、關鍵字..." if is_zh else "🔍 Search systems, tags, keywords..."
    search_query = st.text_input(
        "wiki_search",
        placeholder=search_placeholder,
        label_visibility="collapsed",
        key="_wiki_search",
    )

    systems = _load_index()
    filtered = _search_systems(search_query, systems)

    # ── Two main tabs: Systems | Timeline
    tab_systems_label = "🌐 體系列表" if is_zh else "🌐 Systems"
    tab_timeline_label = "📜 歷史時間軸" if is_zh else "📜 Historical Timeline"
    tab_systems, tab_timeline = st.tabs([tab_systems_label, tab_timeline_label])

    with tab_systems:
        _render_systems_tab(filtered, lang, is_zh)

    with tab_timeline:
        _render_timeline_tab(lang, is_zh)


def _render_systems_tab(
    systems: list[dict[str, str]], lang: str, is_zh: bool
) -> None:
    """Render the categorized system list with article viewer."""
    if not systems:
        msg = "⚠️ 找不到相關體系" if is_zh else "⚠️ No matching systems found"
        st.info(msg)
        return

    # Group by category
    cats: dict[str, list[dict[str, str]]] = {}
    for s in systems:
        cats.setdefault(s["category"], []).append(s)

    # Sidebar-style selection via st.session_state
    selected_key = "_wiki_selected_system"
    if selected_key not in st.session_state:
        st.session_state[selected_key] = systems[0]["file"] if systems else None

    col_list, col_article = st.columns([1, 2], gap="medium")

    with col_list:
        for cat, cat_systems in cats.items():
            with st.expander(_cat_label(cat, lang), expanded=True):
                for s in cat_systems:
                    btn_label = s["name_zh"] if is_zh else s["name_en"]
                    is_active = st.session_state.get(selected_key) == s["file"]
                    btn_type = "primary" if is_active else "secondary"
                    if st.button(
                        btn_label,
                        key=f"_wiki_btn_{s['file']}",
                        type=btn_type,
                        width="stretch",
                    ):
                        st.session_state[selected_key] = s["file"]
                        st.rerun()

    with col_article:
        sel = st.session_state.get(selected_key)
        if sel:
            _render_article(sel, is_zh)


def _render_article(filename: str, is_zh: bool) -> None:
    """Render a single wiki article from its Markdown file."""
    md = _load_md(filename)

    # Extract front-matter tags (lines starting with > **tags:**)
    tag_line = ""
    for line in md.splitlines():
        if line.strip().startswith("> **tags:**"):
            tag_line = line.strip().replace("> **tags:**", "").strip()
            break

    # Render tag badges
    if tag_line:
        badges = "".join(
            f'<span class="wiki-tag">{t.strip()}</span>'
            for t in tag_line.split(",")
            if t.strip()
        )
        st.markdown(f'<div style="margin-bottom:0.6rem">{badges}</div>', unsafe_allow_html=True)

    # Render Markdown body
    st.markdown(
        f'<div class="wiki-article">{_md_to_html(md)}</div>',
        unsafe_allow_html=True,
    )


def _md_to_html(md: str) -> str:
    """
    Convert Markdown to HTML for st.markdown unsafe rendering.
    Uses Python's markdown library if available, otherwise falls back to
    Streamlit's native markdown rendering path (plain text in a pre block).
    """
    try:
        import markdown as md_lib  # type: ignore
        return md_lib.markdown(
            md,
            extensions=["tables", "fenced_code", "nl2br"],
        )
    except ImportError:
        # markdown library not installed — surface a notice to the developer
        st.warning(
            "⚠️ Python `markdown` package not installed. "
            "Content is shown as plain text. Run `pip install markdown` for rich rendering."
        )
        return f"<pre style='white-space:pre-wrap'>{md}</pre>"


def _render_timeline_tab(lang: str, is_zh: bool) -> None:
    """Render the Plotly historical timeline."""
    try:
        import plotly.graph_objects as go  # noqa: F401
    except ImportError:
        msg = (
            "⚠️ Plotly 未安裝，無法顯示時間軸。請執行 `pip install plotly`。"
            if is_zh else
            "⚠️ Plotly is not installed. Cannot display timeline. Run `pip install plotly`."
        )
        st.error(msg)
        return

    fig = _build_timeline_figure(lang)
    st.plotly_chart(fig, width="stretch")

    # Instruction note
    note = (
        "💡 將滑鼠移到事件點可查看詳情。各色代表不同體系分類。"
        if is_zh else
        "💡 Hover over event dots for details. Colors represent different system categories."
    )
    st.caption(note)
