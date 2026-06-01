"""
astro/chart_theme.py — 全域圖表主題 (Global Chart Theme)

統一各體系的顏色常量、字型、網格風格，並提供行動裝置適配 CSS。
"""

# ── Primary UI colours (KinAstro Design System) ────────────────
PRIMARY_COLOR = "#a78bfa"
SECONDARY_COLOR = "#EAB308"          # stardust gold
ACCENT_PURPLE = "#7C3AED"           # soft purple mist
BG_LIGHT = "#1e1b4b"
BG_DARK = "#0F172A"                 # deep indigo
BG_DEEPSPACE = "#020617"            # deep space black
TEXT_PRIMARY = "#e0e0ff"
TEXT_SECONDARY = "#b0b0d0"

# ── Zodiac sign colours (by element) ───────────────────────────
ELEMENT_COLORS = {
    "Fire": "#e25822",
    "Earth": "#8b7355",
    "Air": "#87ceeb",
    "Water": "#4682b4",
}

ZODIAC_COLORS = {
    "Aries": "#e25822", "Leo": "#e25822", "Sagittarius": "#e25822",
    "Taurus": "#8b7355", "Virgo": "#8b7355", "Capricorn": "#8b7355",
    "Gemini": "#87ceeb", "Libra": "#87ceeb", "Aquarius": "#87ceeb",
    "Cancer": "#4682b4", "Scorpio": "#4682b4", "Pisces": "#4682b4",
}

# ── Universal planet colours (canonical key → hex) ─────────────
PLANET_COLORS = {
    "Sun": "#FF8C00",
    "Moon": "#C0C0C0",
    "Mercury": "#4169E1",
    "Venus": "#FF69B4",
    "Mars": "#DC143C",
    "Jupiter": "#228B22",
    "Saturn": "#8B4513",
    "Uranus": "#00CED1",
    "Neptune": "#7B68EE",
    "Pluto": "#800080",
    "Rahu": "#556B2F",
    "Ketu": "#4B0082",
    "MoonApogee": "#2F4F4F",
    "PurpleQi": "#9400D3",
}

# ── Aspect colours ──────────────────────────────────────────────
ASPECT_COLORS = {
    "Conjunction": "#FFD700",
    "Opposition": "#FF0000",
    "Trine": "#00AA00",
    "Square": "#FF4500",
    "Sextile": "#4169E1",
}

# ── SVG / Chart drawing defaults ────────────────────────────────
CHART_BG = "#0F172A"
CHART_RING_STROKE = "#5a5a9a"
CHART_GRID_LINE = "#2a2a5a"
CHART_TEXT_COLOR = "#e0e0ff"
FONT_FAMILY = "'Space Grotesk', 'Inter', 'Noto Sans TC', Arial, Helvetica, sans-serif"

# ── Mobile responsive CSS ───────────────────────────────────────
MOBILE_CSS = """<style>
/* ── Google Fonts ────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700;900&family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

/* ── Sidebar toggle button (Grok-style) ── */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    z-index: 999 !important;
}
[data-testid="collapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] button {
    background: rgba(30, 27, 75, 0.85) !important;
    border: 1px solid rgba(124, 58, 237, 0.3) !important;
    border-radius: 8px !important;
    color: #A78BFA !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    transition: all 0.25s ease !important;
}
[data-testid="collapsedControl"] button:hover,
[data-testid="stSidebarCollapsedControl"] button:hover {
    background: rgba(124, 58, 237, 0.25) !important;
    border-color: rgba(234, 179, 8, 0.4) !important;
    color: #EAB308 !important;
    box-shadow: 0 0 12px rgba(234, 179, 8, 0.15) !important;
}

/* ── Sidebar transitions ── */
section[data-testid="stSidebar"] {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                visibility 0.3s ease !important;
}
/* Close (X) button inside sidebar */
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] {
    color: #A78BFA !important;
    transition: all 0.25s ease !important;
}
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"]:hover {
    color: #EAB308 !important;
}

/* ── Global: prevent horizontal scroll ──────────────── */
.stMainBlockContainer, .stMain, [data-testid="stAppViewBlockContainer"] {
    max-width: 100vw;
    overflow-x: hidden;
}

/* ── Cosmic background ──────────────────────────────── */
.stApp {
    background:
        radial-gradient(ellipse at 20% 50%, rgba(88, 28, 135, 0.18) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(30, 27, 75, 0.45) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 80%, rgba(59, 7, 100, 0.15) 0%, transparent 50%),
        linear-gradient(180deg, #0F172A 0%, #0d0d35 50%, #020617 100%);
    background-attachment: fixed;
}

/* ── Typography ──────────────────────────────────────── */
h1, h2, h3 {
    font-family: 'Cinzel', 'Noto Sans TC', serif !important;
    letter-spacing: 1px;
}
h1 {
    background: linear-gradient(135deg, #a78bfa 0%, #EAB308 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
body, p, span, div, li, td, th, label, input, select, textarea, button {
    font-family: 'Space Grotesk', 'Inter', 'Noto Sans TC', sans-serif !important;
}
/* Preserve Material Symbols font for Streamlit UI icons (expander toggle, sidebar toggle, etc.) */
.material-symbols-rounded,
[class*="material-symbols"],
[data-testid="stIconMaterial"],
[data-testid="stExpanderToggleIcon"],
[data-testid="stExpanderToggleIcon"] span,
[data-testid="stExpander"] summary svg,
[data-testid="stExpander"] summary span[kind],
[data-testid="stBaseButton-headerNoPadding"] span,
[data-testid="collapsedControl"] span,
[data-testid="stSidebarCollapsedControl"] span,
[data-testid="stSidebarCollapsedControl"] button,
.stSidebarCollapsedControl span,
[data-testid="stHeader"] button span,
[data-testid="stHeader"] span[data-icon] {
    font-family: 'Material Symbols Rounded' !important;
}

/* ── Glassmorphism cards ─────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(30, 27, 75, 0.5) !important;
    border: 1px solid rgba(167, 139, 250, 0.15) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
}

/* ── Tabs styling ────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(30, 27, 75, 0.4);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: #b0b0d0 !important;
    font-weight: 500;
    transition: all 0.3s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(167, 139, 250, 0.15) !important;
    color: #e0e0ff !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: rgba(167, 139, 250, 0.25) !important;
    color: #a78bfa !important;
    font-weight: 600;
}
/* Tab highlight bar */
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #a78bfa !important;
}

/* ── Buttons ─────────────────────────────────────────── */
.stButton > button {
    border-radius: 20px !important;
    font-weight: 500;
    letter-spacing: 0.5px;
    transition: all 0.3s ease !important;
    border: 1px solid rgba(167, 139, 250, 0.3) !important;
}
.stButton > button:hover {
    transform: scale(1.03) translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(167, 139, 250, 0.3) !important;
}
.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%) !important;
    border: none !important;
    color: #fff !important;
}
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 4px 24px rgba(124, 58, 237, 0.5) !important;
}
.stButton > button[data-testid="stBaseButton-secondary"] {
    background: rgba(30, 27, 75, 0.6) !important;
    color: #e0e0ff !important;
}

/* ── DataFrames ──────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* ── Metrics ─────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(30, 27, 75, 0.5);
    border: 1px solid rgba(167, 139, 250, 0.15);
    border-radius: 16px;
    padding: 16px !important;
    backdrop-filter: blur(8px);
}
[data-testid="stMetricValue"] {
    color: #EAB308 !important;
    font-family: 'Cinzel', serif !important;
}

/* ── Dividers ────────────────────────────────────────── */
hr {
    border-color: rgba(167, 139, 250, 0.12) !important;
}

/* ── Info / Warning / Error boxes ────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    backdrop-filter: blur(8px);
}

/* ── Markdown tables: horizontal scroll on overflow ── */
[data-testid="stMarkdownContainer"] {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    max-width: 100%;
}

/* ── App subtitle ─────────────────────────────────── */
.app-subtitle {
    font-size: 1.05rem;
    color: #b0b0d0;
    margin-top: -8px;
    margin-bottom: 20px;
}

/* ── Welcome hero card ─────────────────────────────── */
.welcome-hero {
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(88, 28, 135, 0.6) 50%, rgba(30, 27, 75, 0.8) 100%);
    border: 1px solid rgba(167, 139, 250, 0.2);
    border-radius: 20px;
    padding: 40px 32px;
    margin-bottom: 28px;
    color: #fff;
    text-align: center;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px rgba(88, 28, 135, 0.3);
    position: relative;
    overflow: hidden;
}
.welcome-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(167, 139, 250, 0.06) 1px, transparent 1px);
    background-size: 30px 30px;
    animation: starfield 60s linear infinite;
    pointer-events: none;
    will-change: transform;
}
@keyframes starfield {
    0% { transform: translate(0, 0); }
    100% { transform: translate(30px, 30px); }
}
.welcome-hero h2 {
    color: #fff !important;
    font-size: 1.8rem !important;
    margin-bottom: 12px;
    font-family: 'Cinzel', serif !important;
    position: relative;
}
.welcome-hero p {
    color: rgba(224, 224, 255, 0.9);
    font-size: 1.05rem;
    margin-bottom: 0;
    line-height: 1.8;
    position: relative;
}

/* ── Step cards (onboarding) ───────────────────────── */
.step-row {
    display: flex;
    gap: 16px;
    justify-content: center;
}
.step-row .step-card {
    flex: 1 1 0;
    min-width: 0;
}
.step-card {
    background: rgba(30, 27, 75, 0.5);
    border: 1px solid rgba(167, 139, 250, 0.15);
    border-radius: 16px;
    padding: 24px 16px;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}
.step-card:hover {
    box-shadow: 0 8px 24px rgba(167, 139, 250, 0.2);
    transform: translateY(-3px);
    border-color: rgba(167, 139, 250, 0.3);
}
.step-num {
    display: inline-block;
    background: linear-gradient(135deg, #7c3aed, #a78bfa);
    color: #fff;
    width: 36px; height: 36px;
    border-radius: 50%;
    line-height: 36px;
    font-weight: bold;
    font-size: 0.95rem;
    margin-bottom: 10px;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.4);
}
.step-card h4 { margin: 8px 0 6px 0; font-size: 1rem; color: #a78bfa; }
.step-card p { color: #b0b0d0; font-size: 0.88rem; margin: 0; line-height: 1.5; }

/* ── Category header in sidebar ────────────────────── */
.sidebar-system-title {
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
    color: #e0e0ff;
}
.sidebar-cat {
    font-size: 0.7rem;
    color: #EAB308;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    margin: 18px 0 6px 2px;
    padding: 4px 0 4px 0;
    font-weight: 700;
    border-bottom: 1px solid rgba(234, 179, 8, 0.15);
}

/* ── System button descriptions ────────────────────── */
.sys-desc {
    font-size: 0.7rem;
    color: #8888bb;
    margin: -4px 0 8px 4px;
    line-height: 1.4;
    opacity: 0.85;
}

/* ── Beginner badge ────────────────────────────────── */
.beginner-badge {
    display: inline-block;
    background: linear-gradient(135deg, #7c3aed, #a78bfa);
    color: #fff;
    font-size: 0.6rem;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: 6px;
    font-weight: 700;
    vertical-align: middle;
    letter-spacing: 0.3px;
    box-shadow: 0 1px 6px rgba(124, 58, 237, 0.4);
}

/* ── Sidebar overall tweaks ────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1e1b4b 100%) !important;
    border-right: 1px solid rgba(234, 179, 8, 0.1) !important;
}
section[data-testid="stSidebar"] .stButton > button {
    font-size: 0.88rem;
    border-radius: 12px;
    transition: all 0.3s ease;
    letter-spacing: 0.3px;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(167, 139, 250, 0.2);
}

/* ── Spinner: Astrology symbol animation ─────────── */
.stSpinner > div {
    border-color: #a78bfa transparent #EAB308 transparent !important;
}

/* ── Scrollbar styling ───────────────────────────────── */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(10, 10, 42, 0.5);
}
::-webkit-scrollbar-thumb {
    background: rgba(167, 139, 250, 0.3);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(167, 139, 250, 0.5);
}

/* ── Mobile ─────────────────────────────────────────── */
@media (max-width: 768px) {
    /* Tabs: wrap onto multiple lines */
    .stTabs [data-baseweb="tab-list"] { flex-wrap: wrap; gap: 2px; }
    .stTabs [data-baseweb="tab"] { font-size: 0.8rem; padding: 3px 6px; min-height: 32px; }

    /* Columns: stack vertically on mobile */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    /* DataFrames: allow horizontal scroll within container */
    .stDataFrame { font-size: 0.78rem; overflow-x: auto; }
    .stMetric { padding: 6px 8px !important; }
    .stExpander summary { font-size: 0.85rem; }

    /* Headings */
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.15rem !important; }
    h3 { font-size: 1.0rem !important; }

    /* Scrollable wrapper for wide astrology tables */
    .scroll-table-wrap {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        max-width: 100%;
        margin: 8px 0;
    }

    /* All tables: compact font, horizontal scroll via parent div */
    [data-testid="stMarkdownContainer"] table {
        font-size: 0.75rem;
    }
    [data-testid="stMarkdownContainer"] table th,
    [data-testid="stMarkdownContainer"] table td {
        padding: 4px 6px !important;
        white-space: nowrap !important;
    }

    /* HTML tables rendered via unsafe_allow_html */
    table {
        font-size: 0.75rem;
    }
    table td, table th {
        white-space: nowrap !important;
        font-size: 0.75rem;
    }

    /* SVG charts: fit within viewport */
    svg {
        max-width: 100% !important;
        height: auto !important;
    }

    /* Palace grid: shrink for small screens */
    .palace-grid td {
        width: 70px !important;
        height: 65px !important;
        font-size: 0.7rem !important;
        white-space: normal !important;
    }

    /* Plotly charts: force full-width */
    .js-plotly-plot { width: 100% !important; }

    /* Welcome hero: compact on mobile */
    .welcome-hero { padding: 24px 16px; border-radius: 16px; }
    .welcome-hero h2 { font-size: 1.3rem !important; }
    .welcome-hero p { font-size: 0.9rem; }

    /* Step cards: stay in a row on mobile, compact */
    .step-row { gap: 8px; }
    .step-card { padding: 14px 8px; border-radius: 12px; }
    .step-num { width: 28px; height: 28px; line-height: 28px; font-size: 0.8rem; margin-bottom: 6px; }
    .step-card h4 { font-size: 0.78rem; }
    .step-card p { font-size: 0.72rem; }
}
/* ── Tablet ─────────────────────────────────────────── */
@media (min-width: 769px) and (max-width: 1024px) {
    .stTabs [data-baseweb="tab"] { font-size: 0.82rem; padding: 5px 10px; }
}
/* ── General ────────────────────────────────────────── */
svg.chart-wheel { max-width: 100%; height: auto; }
.export-btn-row .stDownloadButton { margin-bottom: 4px; }

/* ── Astro table styling (all screen sizes) ────────── */
[data-testid="stMarkdownContainer"] table {
    border-collapse: collapse;
    width: max-content;
    min-width: 100%;
}
[data-testid="stMarkdownContainer"] table th,
[data-testid="stMarkdownContainer"] table td {
    padding: 8px 12px;
    white-space: nowrap;
    text-align: center;
    vertical-align: middle;
}
[data-testid="stMarkdownContainer"] table th {
    background: rgba(167, 139, 250, 0.1);
    font-weight: 600;
    color: #a78bfa;
}
[data-testid="stMarkdownContainer"] table tbody tr:hover td {
    background: rgba(167, 139, 250, 0.06);
}

/* ── Palace grid (unified CSS for 天盤 / 宮位表) ──── */
.palace-grid {
    border-collapse: separate;
    border-spacing: 4px;
    margin: 10px auto;
    font-family: 'Noto Sans TC', sans-serif;
}
.palace-grid td {
    width: 100px;
    height: 88px;
    text-align: center;
    vertical-align: middle;
    border: 2px solid rgba(167, 139, 250, 0.3);
    padding: 4px 2px;
    border-radius: 8px;
    white-space: normal !important;
    word-break: break-word;
    background: rgba(30, 27, 75, 0.4);
    color: #e0e0ff;
}
.palace-grid .center-cell {
    background: rgba(30, 27, 75, 0.6);
    padding: 10px 8px;
    line-height: 1.6;
    color: #e0e0ff;
}
/* 五行配色 (Chinese five-element colours for palace cells) — dark mode */
.palace-grid .elem-wood  { background: rgba(56, 142, 60, 0.2); border-color: rgba(56, 142, 60, 0.5); }
.palace-grid .elem-fire  { background: rgba(198, 40, 40, 0.2); border-color: rgba(198, 40, 40, 0.5); }
.palace-grid .elem-earth { background: rgba(245, 127, 23, 0.2); border-color: rgba(245, 127, 23, 0.5); }
.palace-grid .elem-metal { background: rgba(158, 158, 158, 0.2); border-color: rgba(158, 158, 158, 0.5); }
.palace-grid .elem-water { background: rgba(21, 101, 192, 0.2); border-color: rgba(21, 101, 192, 0.5); }

/* ── Star particles background ─────────────────────── */
.star-particles {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.star-particles .particle {
    position: absolute;
    width: 2px;
    height: 2px;
    background: #EAB308;
    border-radius: 50%;
    animation: twinkle var(--duration, 3s) ease-in-out infinite var(--delay, 0s);
    opacity: 0;
}
@keyframes twinkle {
    0%, 100% { opacity: 0; transform: scale(0.5); }
    50% { opacity: var(--max-opacity, 0.7); transform: scale(1); }
}

/* ── Chart hover glow & rotation ───────────────────── */
.chart-glow-wrap {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 16px;
}
.chart-glow-wrap:hover {
    box-shadow: 0 0 30px rgba(234, 179, 8, 0.2), 0 0 60px rgba(124, 58, 237, 0.12);
    transform: rotate(0.5deg) scale(1.005);
}
.chart-glow-wrap:hover svg {
    filter: drop-shadow(0 0 8px rgba(234, 179, 8, 0.25));
}

/* ── Cosmic chart outer border ring ────────────────── */
.cosmic-ring {
    position: relative;
    display: inline-block;
}
.cosmic-ring::after {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: conic-gradient(
        from 0deg,
        rgba(234, 179, 8, 0.5),
        rgba(124, 58, 237, 0.3),
        rgba(167, 139, 250, 0.2),
        rgba(234, 179, 8, 0.5)
    );
    z-index: -1;
    animation: cosmicSpin 25s linear infinite;
    pointer-events: none;
}
@keyframes cosmicSpin {
    to { transform: rotate(360deg); }
}

/* ── Cosmic transition flash ───────────────────────── */
.cosmic-transition-flash {
    position: fixed;
    inset: 0;
    background: radial-gradient(ellipse at center, rgba(124, 58, 237, 0.25) 0%, transparent 70%);
    pointer-events: none;
    z-index: 9999;
    animation: flashFade 0.5s ease-out forwards;
}
@keyframes flashFade {
    0% { opacity: 0.7; }
    100% { opacity: 0; }
}

/* ── Sidebar search styling ────────────────────────── */
section[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(124, 58, 237, 0.25) !important;
    border-radius: 12px !important;
    font-size: 0.85rem !important;
}
section[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
    border-color: rgba(234, 179, 8, 0.5) !important;
    box-shadow: 0 0 12px rgba(234, 179, 8, 0.12) !important;
}

/* ── Share card button ─────────────────────────────── */
.share-card-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, rgba(234, 179, 8, 0.12), rgba(124, 58, 237, 0.12));
    border: 1px solid rgba(234, 179, 8, 0.25);
    border-radius: 12px;
    color: #EAB308;
    padding: 8px 16px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.3s ease;
}
.share-card-btn:hover {
    background: linear-gradient(135deg, rgba(234, 179, 8, 0.22), rgba(124, 58, 237, 0.22));
    box-shadow: 0 0 20px rgba(234, 179, 8, 0.18);
    transform: translateY(-1px);
}

/* ── Enhanced sidebar active button ────────────────── */
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #7C3AED 0%, #EAB308 100%) !important;
    border: none !important;
    color: #fff !important;
    box-shadow: 0 2px 12px rgba(234, 179, 8, 0.2) !important;
}
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 4px 24px rgba(234, 179, 8, 0.35) !important;
}
</style>"""

# ── Planet name → canonical key mapping ─────────────────────────
_PLANET_ALIASES: dict[str, str] = {
    # Chinese
    "太陽": "Sun", "太陰": "Moon", "水星": "Mercury", "金星": "Venus",
    "火星": "Mars", "木星": "Jupiter", "土星": "Saturn", "天王星": "Uranus",
    "海王星": "Neptune", "冥王星": "Pluto", "羅睺": "Rahu", "計都": "Ketu",
    "月孛": "MoonApogee", "紫氣": "PurpleQi",
    # Sanskrit / Vedic
    "Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars", "Budha": "Mercury",
    "Guru": "Jupiter", "Shukra": "Venus", "Shani": "Saturn",
    # Western with glyph
    "Sun ☉": "Sun", "Moon ☽": "Moon", "Mercury ☿": "Mercury",
    "Venus ♀": "Venus", "Mars ♂": "Mars", "Jupiter ♃": "Jupiter",
    "Saturn ♄": "Saturn", "Uranus ♅": "Uranus", "Neptune ♆": "Neptune",
    "Pluto ♇": "Pluto",
}


def get_planet_color(name: str) -> str:
    """Return hex colour for *name*, resolving aliases. Falls back to grey."""
    # Direct canonical match
    if name in PLANET_COLORS:
        return PLANET_COLORS[name]
    # Alias match
    canonical = _PLANET_ALIASES.get(name)
    if canonical:
        return PLANET_COLORS.get(canonical, "#666666")
    # Substring search (e.g. "Surya (太陽)")
    for alias, key in _PLANET_ALIASES.items():
        if alias in name:
            return PLANET_COLORS.get(key, "#666666")
    return "#666666"


# ── Plotly unified theme ────────────────────────────────────────

def get_plotly_theme() -> dict:
    """Return a unified Plotly layout theme dict for all chart modules."""
    return dict(
        paper_bgcolor="rgba(15, 23, 42, 0.8)",
        plot_bgcolor="rgba(30, 27, 75, 0.4)",
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY, size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        colorway=[
            "#EAB308",    # Sun – stardust gold
            "#c0c0c0",    # Moon – silver
            "#60a5fa",    # Mercury – sky blue
            "#f472b6",    # Venus – pink
            "#ef4444",    # Mars – red
            "#34d399",    # Jupiter – emerald
            "#a78bfa",    # Saturn – purple
        ],
        xaxis=dict(gridcolor="rgba(167, 139, 250, 0.1)", zerolinecolor="rgba(167, 139, 250, 0.2)"),
        yaxis=dict(gridcolor="rgba(167, 139, 250, 0.1)", zerolinecolor="rgba(167, 139, 250, 0.2)"),
    )


def apply_chart_theme(fig) -> None:
    """Apply the unified plotly theme to a plotly Figure *in place*."""
    fig.update_layout(**get_plotly_theme())


# ── SVG helpers ─────────────────────────────────────────────────

def svg_header(width: int = 600, height: int = 600, title: str = "") -> str:
    """Return a standardised SVG opening tag with consistent styling."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'class="chart-wheel" viewBox="0 0 {width} {height}" '
        f'style="background:{CHART_BG}; font-family:{FONT_FAMILY}; '
        f'border-radius:12px; border:1px solid rgba(167,139,250,0.15);">'
        f'<title>{title}</title>'
    )


def svg_footer() -> str:
    """Return the SVG closing tag."""
    return '</svg>'
