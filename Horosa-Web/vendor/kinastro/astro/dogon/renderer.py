"""Streamlit renderer for Dogon Sirius Cosmology."""

from __future__ import annotations

import json
import math
from pathlib import Path

from astro.chart_theme import apply_chart_theme, svg_header, svg_footer, FONT_FAMILY
from astro.i18n import auto_cn, get_lang

from .calculator import DogonSiriusChart


def _load_constants_cached():
    import streamlit as st

    @st.cache_data(show_spinner=False)
    def _load() -> dict:
        p = Path(__file__).parent / "data" / "constants.json"
        return json.loads(p.read_text(encoding="utf-8"))

    return _load()


# ---------------------------------------------------------------------------
# Nommo totem SVG paths (simplified West-African mask geometry)
# ---------------------------------------------------------------------------

def _nommo_totem_svg(cx: float, cy: float, size: float, color: str) -> str:
    """Return SVG markup for a simplified Nommo totem icon centred at (cx, cy)."""
    h = size
    w = size * 0.4
    # Oval head
    head = f'<ellipse cx="{cx:.1f}" cy="{cy - h * 0.35:.1f}" rx="{w * 0.55:.1f}" ry="{h * 0.28:.1f}" fill="none" stroke="{color}" stroke-width="1.4" opacity="0.72"/>'
    # Body line
    body = f'<line x1="{cx:.1f}" y1="{cy - h * 0.07:.1f}" x2="{cx:.1f}" y2="{cy + h * 0.35:.1f}" stroke="{color}" stroke-width="1.6" opacity="0.72"/>'
    # Arms
    arm_l = f'<line x1="{cx:.1f}" y1="{cy + h * 0.05:.1f}" x2="{cx - w:.1f}" y2="{cy + h * 0.18:.1f}" stroke="{color}" stroke-width="1.2" opacity="0.65"/>'
    arm_r = f'<line x1="{cx:.1f}" y1="{cy + h * 0.05:.1f}" x2="{cx + w:.1f}" y2="{cy + h * 0.18:.1f}" stroke="{color}" stroke-width="1.2" opacity="0.65"/>'
    # Mask scarification lines (horizontal)
    scar1 = f'<line x1="{cx - w * 0.4:.1f}" y1="{cy - h * 0.32:.1f}" x2="{cx + w * 0.4:.1f}" y2="{cy - h * 0.32:.1f}" stroke="{color}" stroke-width="0.7" opacity="0.5"/>'
    scar2 = f'<line x1="{cx - w * 0.3:.1f}" y1="{cy - h * 0.22:.1f}" x2="{cx + w * 0.3:.1f}" y2="{cy - h * 0.22:.1f}" stroke="{color}" stroke-width="0.7" opacity="0.5"/>'
    return head + body + arm_l + arm_r + scar1 + scar2


def _african_weave_pattern(size: int, ochre: str, indigo: str) -> str:
    """Generate an SVG kente/African weave border pattern."""
    lines = []
    step = 18
    n = size // step
    for i in range(n + 1):
        x = i * step
        # Vertical dash
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{size}" stroke="{ochre}" stroke-width="0.5" stroke-dasharray="4 14" opacity="0.22"/>')
        lines.append(f'<line x1="0" y1="{x}" x2="{size}" y2="{x}" stroke="{indigo}" stroke-width="0.5" stroke-dasharray="4 14" opacity="0.18"/>')
    # Corner diamond motifs
    for cx, cy in [(0, 0), (size, 0), (0, size), (size, size)]:
        lines.append(f'<polygon points="{cx},{cy+12} {cx+12},{cy} {cx+24},{cy+12} {cx+12},{cy+24}" fill="none" stroke="{ochre}" stroke-width="1" opacity="0.3"/>')
    return "".join(lines)


def _build_svg_fallback(chart: DogonSiriusChart, constants: dict) -> str:
    colors = constants["palette"]
    size = 680
    cx = cy = size / 2
    r0 = 210

    body_cfg = constants["bodies"]

    def pos(lon: float, radius: float) -> tuple[float, float]:
        a = math.radians((lon - 90.0) % 360)
        return cx + radius * math.cos(a), cy + radius * math.sin(a)

    lines = [
        svg_header(size, size, "Dogon Sirius Cosmology"),
        # Deep-night-sky radial gradient
        f'<defs>'
        f'<radialGradient id="dogonbg" cx="50%" cy="50%" r="55%">'
        f'<stop offset="0%" stop-color="{colors["indigo"]}"/>'
        f'<stop offset="70%" stop-color="#0a0f1e"/>'
        f'<stop offset="100%" stop-color="{colors["black"]}"/>'
        f'</radialGradient>'
        f'<radialGradient id="sirius_glow" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="#ffffff" stop-opacity="0.9"/>'
        f'<stop offset="100%" stop-color="{colors["stardust"]}" stop-opacity="0"/>'
        f'</radialGradient>'
        f'</defs>',
        f'<rect x="0" y="0" width="{size}" height="{size}" fill="url(#dogonbg)"/>',
        # African weave border
        _african_weave_pattern(size, colors["ochre"], colors["indigo"]),
        # Mask frame: outer octagonal frame
        f'<polygon points="{cx},{cy - r0 - 38} {cx + r0 + 38},{cy} {cx},{cy + r0 + 38} {cx - r0 - 38},{cy}" '
        f'fill="none" stroke="{colors["ochre"]}" stroke-width="2.2" opacity="0.55" stroke-dasharray="8 4"/>',
        # Orbit rings
        f'<circle cx="{cx}" cy="{cy}" r="{r0}" fill="none" stroke="{colors["earth"]}" stroke-width="1.5" stroke-dasharray="3 5" opacity="0.7"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r0 * 0.66}" fill="none" stroke="{colors["stardust"]}" stroke-width="0.9" opacity="0.45"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r0 * 0.46}" fill="none" stroke="{colors["nommo"]}" stroke-width="0.7" opacity="0.35"/>',
    ]

    # Particle stars (static seed-based positions)
    import hashlib
    for si in range(60):
        hx = int(hashlib.md5(f"star{si}".encode()).hexdigest()[:6], 16)
        sx = (hx % size) * 1.0
        hx2 = int(hashlib.md5(f"star{si}y".encode()).hexdigest()[:6], 16)
        sy = (hx2 % size) * 1.0
        sr = 0.6 + (si % 3) * 0.4
        so = 0.2 + (si % 5) * 0.1
        lines.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{sr}" fill="{colors["stardust"]}" opacity="{so:.2f}"/>')

    radius_map = {"sirius_a": r0, "sirius_b": r0 * 0.66, "sirius_c": r0 * 0.46}
    body_colors = {
        "sirius_a": colors["stardust"],
        "sirius_b": "#D0D7F2",
        "sirius_c": colors["nommo"],
    }

    for body in chart.bodies:
        cfg = body_cfg[body.key]
        px, py = pos(body.longitude, radius_map.get(body.key, r0 * 0.46))
        bcol = body_colors.get(body.key, colors["stardust"])
        br = int(cfg["radius"])
        # Glow halo
        lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{br + 6}" fill="{bcol}" opacity="0.18"/>')
        # Body dot
        lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{br}" fill="{bcol}" opacity="0.95"/>')
        lines.append(
            f'<text x="{px + 14:.1f}" y="{py - 10:.1f}" font-family="{FONT_FAMILY}" font-size="11" fill="{colors["stardust"]}">'
            f'{body.label} · {body.dogon_name}</text>'
        )
        # Sirius B: show separation
        if body.key == "sirius_b" and body.separation_arcsec > 0:
            lines.append(
                f'<text x="{px + 14:.1f}" y="{py + 4:.1f}" font-family="{FONT_FAMILY}" font-size="9" fill="{colors["earth"]}" opacity="0.8">'
                f'sep {body.separation_arcsec:.1f}"</text>'
            )

    # Nommo totems (left and right flanking)
    lines.append(_nommo_totem_svg(cx - r0 - 50, cy, 58, colors["nommo"]))
    lines.append(_nommo_totem_svg(cx + r0 + 50, cy, 58, colors["nommo"]))

    # Footer text
    lines.append(
        f'<text x="18" y="{size - 44}" font-family="{FONT_FAMILY}" font-size="12" fill="{colors["stardust"]}">'
        f'Sigui {chart.sigui.previous_year} → {chart.sigui.next_year} · Phase {chart.sigui.life_phase}</text>'
    )
    lines.append(
        f'<text x="18" y="{size - 26}" font-family="{FONT_FAMILY}" font-size="11" fill="{colors["earth"]}">'
        f'Zone: {chart.zone_result.label} · {chart.location_name}</text>'
    )
    if chart.heliacal_rising:
        lines.append(
            f'<text x="18" y="{size - 10}" font-family="{FONT_FAMILY}" font-size="10" fill="{colors["nommo"]}" opacity="0.85">'
            f'Heliacal Rising: {chart.heliacal_rising.date_str}</text>'
        )
    lines.append(svg_footer())
    return "".join(lines)


def _render_sigui_timeline(chart: DogonSiriusChart, constants: dict, is_zh: bool) -> None:
    """Render the Sigui cycle life-phase timeline widget."""
    import streamlit as st

    try:
        import plotly.graph_objects as go
    except ImportError:
        st.caption(auto_cn(
            f"Sigui 生命階段 {chart.sigui.life_phase}：{chart.sigui.life_phase_label_zh}",
            f"Sigui Life Phase {chart.sigui.life_phase}: {chart.sigui.life_phase_label_en}",
        ))
        return

    colors = constants["palette"]
    phases = constants.get("sigui_life_phases", [])
    cycle = chart.sigui.cycle_years
    years_since = chart.sigui.years_since_previous
    prev_year = chart.sigui.previous_year

    # Build a horizontal timeline bar chart
    phase_labels = [p["label_zh"] if is_zh else p["label_en"] for p in phases]
    phase_ranges = [p["range_years"] for p in phases]
    phase_widths = [r[1] - r[0] for r in phase_ranges]
    phase_starts = [r[0] for r in phase_ranges]

    bar_colors = [
        colors["indigo"], colors["nommo"], colors["earth"],
        colors["ochre"], colors["stardust"],
    ]

    fig = go.Figure()
    for i, (label, start, width) in enumerate(zip(phase_labels, phase_starts, phase_widths)):
        fig.add_trace(go.Bar(
            x=[width],
            y=["Sigui"],
            base=[start],
            orientation="h",
            marker_color=bar_colors[i % len(bar_colors)],
            opacity=0.72,
            name=label,
            hovertemplate=f"{label}<extra></extra>",
        ))

    # Current position marker
    fig.add_vline(
        x=years_since,
        line_color=colors["stardust"],
        line_width=2.5,
        annotation_text=f"◀ {prev_year + int(years_since):.0f}",
        annotation_font_color=colors["stardust"],
    )

    fig.update_layout(
        barmode="stack",
        height=90,
        margin=dict(l=0, r=0, t=22, b=0),
        xaxis=dict(
            range=[0, cycle],
            showgrid=False,
            title=dict(text=auto_cn("距上次 Sigui（年）", "Years since last Sigui"), font=dict(size=11)),
        ),
        yaxis=dict(visible=False),
        showlegend=True,
        legend=dict(orientation="h", y=-0.8, font=dict(size=10)),
        title=dict(
            text=auto_cn(f"Sigui {cycle}年週期生命階段", f"Sigui {cycle}-Year Life Phases"),
            font=dict(size=13, color=colors["stardust"]),
        ),
    )
    apply_chart_theme(fig)
    st.plotly_chart(fig, width="stretch")


def render_dogon_sirius_chart(chart: DogonSiriusChart, after_chart_hook=None) -> None:
    import streamlit as st

    constants = _load_constants_cached()
    colors = constants["palette"]
    lang = get_lang()
    is_zh = lang in ("zh", "zh_cn")

    st.markdown(
        f"""
<div style="padding:18px 20px;border-radius:14px;
border:1.5px solid {colors['ochre']};
background:linear-gradient(135deg,{colors['black']} 0%,{colors['indigo']} 100%);
margin-bottom:12px;">
  <div style="font-size:1.25rem;color:{colors['stardust']};font-weight:700;letter-spacing:.04em;">
    🜂 Dogon Sirius Cosmology · Po Tolo · Nommo · Sigui
  </div>
  <div style="font-size:.93rem;color:{colors['earth']};margin-top:6px;">
    {chart.location_name} · {chart.year:04d}-{chart.month:02d}-{chart.day:02d} {chart.hour:02d}:{chart.minute:02d} (UTC{chart.timezone:+.1f})
  </div>
  <div style="font-size:.82rem;color:{colors['nommo']};margin-top:4px;font-style:italic;">
    {auto_cn("基於人類學與天文重建", "Based on anthropological & astronomical reconstruction")}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # ── Interactive Plotly chart ───────────────────────────────────────────
    fig_ok = False
    try:
        import plotly.graph_objects as go

        traces = []

        # Orbit rings as background scatter
        for ring_r, ring_color, ring_dash in [
            (1.0, colors["earth"], "dash"),
            (0.66, colors["stardust"], "dot"),
            (0.46, colors["nommo"], "dot"),
        ]:
            thetas = list(range(0, 361, 3))
            traces.append(go.Scatterpolar(
                r=[ring_r] * len(thetas),
                theta=thetas,
                mode="lines",
                line=dict(color=ring_color, width=0.8, dash=ring_dash),
                opacity=0.35,
                showlegend=False,
                hoverinfo="skip",
            ))

        # Particle stars
        import hashlib
        star_r, star_t = [], []
        for si in range(80):
            hv = int(hashlib.md5(f"st{si}".encode()).hexdigest()[:8], 16)
            star_r.append(0.05 + (hv % 1000) / 1000.0 * 1.1)
            star_t.append(hv % 360)
        traces.append(go.Scatterpolar(
            r=star_r, theta=star_t,
            mode="markers",
            marker=dict(size=1.8, color=colors["stardust"], opacity=0.3),
            showlegend=False, hoverinfo="skip",
        ))

        # Bodies
        r_map = {"sirius_a": 1.0, "sirius_b": 0.66, "sirius_c": 0.46}
        bc_map = {
            "sirius_a": colors["stardust"],
            "sirius_b": "#D0D7F2",
            "sirius_c": colors["nommo"],
        }
        bs_map = {"sirius_a": 16, "sirius_b": 11, "sirius_c": 9}

        for body in chart.bodies:
            note = body.cultural_note_zh if is_zh else body.cultural_note_en
            extra_tip = ""
            if body.key == "sirius_b" and body.separation_arcsec > 0:
                extra_tip = f"<br>Sep: {body.separation_arcsec:.2f}\" | Phase: {body.orbit_phase:.3f}"
            traces.append(go.Scatterpolar(
                r=[r_map.get(body.key, 0.5)],
                theta=[body.longitude],
                mode="markers+text",
                text=[f"{body.label}<br><span style='font-size:10px'>{body.dogon_name}</span>"],
                textposition="top center",
                marker=dict(
                    size=bs_map.get(body.key, 9),
                    color=bc_map.get(body.key, colors["stardust"]),
                    line=dict(color=colors["ochre"], width=1),
                ),
                customdata=[[note, extra_tip]],
                hovertemplate="%{text}<br>lon %{theta:.1f}°%{customdata[1]}<br>%{customdata[0]}<extra></extra>",
                name=f"{body.label} ({body.dogon_name})",
            ))

        # Birth aspects arcs
        for asp in chart.birth_aspects:
            arc_color = "#FFD700" if asp.aspect_name == "Conjunction" else (
                colors["nommo"] if asp.nommo_resonance else colors["ochre"]
            )
            traces.append(go.Scatterpolar(
                r=[0.85, 0.85],
                theta=[asp.sirius_longitude, asp.planet_longitude],
                mode="lines",
                line=dict(color=arc_color, width=1.4, dash="dot"),
                opacity=0.55,
                showlegend=False,
                hoverinfo="skip",
            ))

        # Sigui timeline spiral overlay
        timeline_years = list(range(chart.sigui.previous_year, chart.sigui.next_year + 1, 4))
        cycle = chart.sigui.cycle_years
        prev = chart.sigui.previous_year
        t_r = [0.1 + 0.55 * ((y - prev) / max(1, cycle)) for y in timeline_years]
        t_theta = [(360 * ((y - prev) / max(1, cycle))) for y in timeline_years]
        traces.append(go.Scatterpolar(
            r=t_r, theta=t_theta,
            mode="lines+markers",
            line=dict(color=colors["ochre"], width=1.2, dash="dot"),
            marker=dict(size=4, color=colors["stardust"]),
            name=auto_cn("Sigui 時間軸", "Sigui Timeline"),
            hovertext=[str(y) for y in timeline_years],
            hoverinfo="text+name",
        ))
        # Current position on Sigui spiral
        yrs_since = chart.sigui.years_since_previous
        cur_r = 0.1 + 0.55 * (yrs_since / max(1, cycle))
        cur_theta = 360 * (yrs_since / max(1, cycle))
        traces.append(go.Scatterpolar(
            r=[cur_r], theta=[cur_theta],
            mode="markers",
            marker=dict(size=10, color=colors["stardust"], symbol="star", line=dict(color=colors["ochre"], width=1.5)),
            name=auto_cn("現在位置", "Current Sigui Position"),
            hovertext=[f"{chart.year} · Phase {chart.sigui.life_phase}"],
            hoverinfo="text",
        ))

        fig = go.Figure(data=traces)
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, showticklabels=False, gridcolor="rgba(217,191,139,0.1)"),
                angularaxis=dict(direction="clockwise", rotation=90, gridcolor="rgba(217,191,139,0.08)"),
            ),
            title=dict(
                text=auto_cn("多貢天狼星宇宙觀 · Nommo 水靈視角", "Dogon Sirius Cosmology · Nommo Water-Spirit View"),
                font=dict(color=colors["stardust"], size=14),
            ),
            showlegend=True,
            legend=dict(font=dict(size=11, color=colors["stardust"]), bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor=colors["black"],
            height=560,
        )
        apply_chart_theme(fig)
        st.plotly_chart(fig, width="stretch")
        fig_ok = True
    except Exception:
        pass

    if not fig_ok:
        st.markdown(_build_svg_fallback(chart, constants), unsafe_allow_html=True)

    # ── Metrics row ────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(auto_cn("Sirius 赤緯", "Sirius Declination"), f"{chart.sirius_declination:.2f}°")
    c2.metric(auto_cn("距下次 Sigui", "To Next Sigui"), f"{chart.sigui.years_until_next:.1f}y")
    c3.metric(auto_cn("星象區域", "Lore Zone"), chart.zone_result.label)
    c4.metric(auto_cn("生命階段", "Life Phase"), f"#{chart.sigui.life_phase}")

    # ── Sirius B orbital data ───────────────────────────────────────────────
    b_body = next((b for b in chart.bodies if b.key == "sirius_b"), None)
    if b_body and b_body.separation_arcsec > 0:
        st.caption(
            auto_cn(
                f"Po Tolo（Sirius B）軌道相位：{b_body.orbit_phase:.3f}，角距 {b_body.separation_arcsec:.2f}\"",
                f"Po Tolo (Sirius B) orbital phase: {b_body.orbit_phase:.3f}, angular separation {b_body.separation_arcsec:.2f}\"",
            )
        )

    # ── Heliacal rising ────────────────────────────────────────────────────
    if chart.heliacal_rising:
        hr = chart.heliacal_rising
        st.info(auto_cn(
            f"🌅 天狼星偕日升（Heliacal Rising）：{hr.date_str}（距今 {hr.days_until:.0f} 天）",
            f"🌅 Sirius Heliacal Rising: {hr.date_str} ({hr.days_until:.0f} days away)",
        ))

    st.caption(auto_cn(chart.disclaimer_zh, chart.disclaimer_en))

    # ── Sigui life-phase timeline ──────────────────────────────────────────
    st.subheader(auto_cn("Sigui 生命週期時間軸", "Sigui Life-Cycle Timeline"))
    _render_sigui_timeline(chart, constants, is_zh)
    with st.expander(auto_cn(
        f"階段 {chart.sigui.life_phase}：{chart.sigui.life_phase_label_zh}",
        f"Phase {chart.sigui.life_phase}: {chart.sigui.life_phase_label_en}",
    ), expanded=True):
        st.markdown(chart.sigui.life_phase_desc_zh if is_zh else chart.sigui.life_phase_desc_en)

    # ── Personal influence ─────────────────────────────────────────────────
    st.subheader(auto_cn("Dogon 個人影響（長老詩意語調）", "Dogon Personal Influence (Elder Poetic Voice)"))
    st.info(chart.personal_influence_zh if is_zh else chart.personal_influence_en)

    # ── Birth aspects ──────────────────────────────────────────────────────
    if chart.birth_aspects:
        st.subheader(auto_cn("Sirius 與出生圖相位", "Sirius–Natal Aspects"))
        for asp in chart.birth_aspects:
            nommo_badge = " 🌊" if asp.nommo_resonance else ""
            st.markdown(
                f"**{asp.aspect_name}** {asp.planet}{nommo_badge} "
                f"(orb {asp.orb}°) — {asp.meaning_zh if is_zh else asp.meaning_en}"
            )

    # ── Cultural cosmology ─────────────────────────────────────────────────
    st.subheader(auto_cn("文化宇宙學與教育內容", "Cultural Cosmology & Learning"))
    st.markdown(
        auto_cn(
            "- **Nommo**：祖先靈與秩序修復象徵；雙生水靈賦予宇宙創生之力\n"
            "- **Po Tolo**：高密度『種子星』（白矮星）隱喻，50 年橢圓軌道\n"
            "- **Emme Ya Tolo**：女性太陽，Nommo 雙生之一的象徵\n"
            "- **Sigui**：約 60 年社群更新節律，伴隨面具舞蹈與口傳傳承\n"
            "- **提示**：此頁內容以文化人類學脈絡呈現，不作自然科學定論。",
            "- **Nommo**: ancestor-spirit motif of order restoration; twin water-beings giving cosmic generative power\n"
            "- **Po Tolo**: dense 'seed-star' (white dwarf) metaphor, 50-yr elliptical orbit\n"
            "- **Emme Ya Tolo**: 'Female Sun', symbol of one Nommo twin\n"
            "- **Sigui**: ~60-year communal renewal rhythm, with mask dances and oral transmission\n"
            "- **Note**: presented as cultural anthropology, not hard-science proof."
        )
    )

    # ── Cross-cultural comparison ──────────────────────────────────────────
    st.subheader(auto_cn("跨文化比較（Sirius 多元視野）", "Cross-Cultural Sirius Perspectives"))
    for row in chart.cross_cultural:
        st.markdown(f"- **{row['system']}** · {row['zh'] if is_zh else row['en']}")

    # ── References ─────────────────────────────────────────────────────────
    with st.expander(auto_cn("來源與爭議說明", "Sources & Contested Points"), expanded=False):
        for ref in chart.references:
            st.markdown(f"- {ref}")

    # ── Export ─────────────────────────────────────────────────────────────
    report_parts = [
        chart.personal_influence_zh if is_zh else chart.personal_influence_en,
        "",
        f"Sigui Phase {chart.sigui.life_phase}: {chart.sigui.life_phase_label_zh if is_zh else chart.sigui.life_phase_label_en}",
    ]
    if chart.heliacal_rising:
        report_parts.append(f"Heliacal Rising: {chart.heliacal_rising.date_str}")
    if chart.birth_aspects:
        report_parts.append("\nNatal Aspects:")
        for asp in chart.birth_aspects:
            report_parts.append(f"  {asp.aspect_name} {asp.planet} orb {asp.orb}°")
    report_parts += ["", chart.disclaimer_zh if is_zh else chart.disclaimer_en]
    report_txt = "\n".join(report_parts)

    st.download_button(
        auto_cn("⬇ 匯出 Dogon 解讀（TXT）", "⬇ Export Dogon Reading (TXT)"),
        data=report_txt,
        file_name=f"dogon_sirius_{chart.year:04d}{chart.month:02d}{chart.day:02d}.txt",
        mime="text/plain",
    )

    if after_chart_hook:
        after_chart_hook()
