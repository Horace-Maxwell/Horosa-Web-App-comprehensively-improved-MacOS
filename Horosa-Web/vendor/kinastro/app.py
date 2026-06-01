"""
堅占星 (Kin Astro) - 多體系占星排盤系統
Multi-System Astrology Chart Application

支援七政四餘（中國）、紫微斗數、策天飛星、十二星次、達摩一掌經、太玄數占星、五運六氣、
萬化仙禽、鐵板神數、邵子神數、鬼谷分定經、大六壬、奇門祿命、太乙命法、
西洋占星、Sabian 符號、希臘（Hellenistic）、Astrocartography、天王星漢堡學派、凱爾特樹木曆、
印度占星（Vedic）、Jaimini、納迪（Nadi）、KP 克里希納穆提、紅皮書（Lal Kitab）、
宿曜道、泰國占星、緬甸（Mahabote）、巴厘 Wariga、爪哇 Weton、蒙古祖爾海（Zurkhai）、
藏傳時輪金剛、九星氣學、土亭數、高棉占星、波利尼西亞／夏威夷、
卡巴拉、猶太 Mazzalot、薩珊波斯、阿拉伯占星、也門占星、Picatrix 占星魔法、
瑪雅、阿茲特克、古埃及十度區間（Decans）、巴比倫占星
共四十九種體系，使用 pyswisseph 進行天文計算。
"""

import contextlib
import json
import os
import random
import textwrap
from pathlib import Path
import streamlit as st
from datetime import datetime, date, time
from typing import Any

from astro.i18n import TRANSLATIONS, get_lang, auto_cn, _t2s
from astro.chart_theme import MOBILE_CSS
from astro.qizheng.calculator import compute_chart
from astro.qizheng.chart_renderer import (
    render_chart_info,
    render_planet_table,
    render_house_table,
    render_aspect_summary,
    render_mansion_ring,
    render_full_chart,
    render_chart_info_panel,
    render_bazi,
    render_shensha,
    render_dasha,
    render_transit_comparison,
    render_zhangguo,
    render_ming_gong_interpretations,
    render_mansion_text_panel,
)
from astro.qizheng.shensha import compute_shensha
from astro.qizheng.qizheng_dasha import compute_dasha
from astro.qizheng.qizheng_transit import compute_transit, compute_transit_now
from astro.qizheng.zhangguo import compute_zhangguo
from astro.qizheng.qizheng_electional import render_electional_tool
from astro.qizheng.qizheng_financial import render_financial_tab
from astro.western.western import compute_western_chart, render_western_chart
from astro.western.western_transit import compute_western_transits
from astro.western.western_return import compute_solar_return
from astro.western.harmonic import render_harmonic_chart
from astro.western.draconic import render_draconic_chart
from astro.western.western_synastry import compute_synastry
from astro.vedic.indian import compute_vedic_chart, render_vedic_chart
from astro.vedic.financial import render_vedic_financial_tab
from astro.lal_kitab import compute_lal_kitab_chart, render_lal_kitab_chart, render_lal_kitab_1952_page
from astro.jaimini import compute_jaimini_chart, render_jaimini_chart, render_jaimini_dasha
from astro.vedic.vedic_dasha import compute_vimshottari, compute_yogini
from astro.vedic.ashtakavarga import compute_ashtakavarga
from astro.vedic.vedic_yogas import compute_yogas
from astro.vedic.bphs_engine import compute_bphs
from astro.vedic.varga import compute_varga_chart, VARGA_KEYS, VARGA_INFO, render_single_varga
from astro.sukkayodo import render_sukkayodo_chart
from astro.thai import (
    compute_thai_chart, render_thai_chart,
    calculate_thai_nine_grid, render_nine_grid,
    calculate_nine_palace_divination, render_nine_palace_divination,
    build_thai_mandala_svg, THAI_NAKSHATRAS,
)
from astro.laos import compute_lao_chart, render_lao_horasat
from astro.brahma_jati import (
    compute_brahma_jati, render_brahma_jati, render_brahma_jati_browse,
)
from astro.kabbalistic import compute_kabbalistic_chart, render_kabbalistic_chart
from astro.jewish_mazzalot import compute_mazzalot_chart, render_mazzalot_chart, build_mazzalot_star_of_david_svg
from astro.arabic.arabic import compute_arabic_chart, render_arabic_chart
from astro.arabic_lots import compute_albiruni_lots
from astro.tieban import TieBanShenShu, TieBanBirthData, render_tieban_chart_svg
from astro.maya import compute_maya_chart, render_maya_chart
from astro.dogon import compute_dogon_sirius_chart, render_dogon_sirius_chart
from astro.amazigh import compute_amazigh_chart, render_amazigh_chart, render_amazigh_sky_svg
from astro.bahre_hasab import analyze_bahre_hasab_date
from astro.aztec import compute_aztec_chart, render_aztec_chart
from astro.ziwei import compute_ziwei_chart, render_ziwei_chart
from astro.damo import compute_damo_chart, render_damo_chart
from astro.diqiyijue import compute_diqiyijue_chart, render_diqiyijue_chart
from astro.cetian_ziwei import compute_cetian_ziwei_chart, render_cetian_ziwei_chart
from astro.burmese_mahabote import compute_mahabote_chart, render_mahabote_chart
from astro.wariga.calculator import WarigaCalculator, compute_wariga
from astro.wariga.renderer import render_streamlit as render_wariga_chart
from astro.jawa_weton.calculator import WetonCalculator, compute_weton
from astro.jawa_weton.renderer import render_streamlit as render_jawa_weton_chart
from astro.bintang_duabelas.renderer import render_streamlit as render_bintang_duabelas_chart
from astro.kinketika import render_streamlit as render_kinketika_chart
from astro.liuyao_lifetime.calculator import compute_lifetime_hexagram
from astro.liuyao_lifetime.renderer import render_streamlit as render_liuyao_lifetime_chart
from astro.medical_astrology.calculator import compute_medical_chart
from astro.medical_astrology.renderer import render_streamlit as render_medical_astrology_chart
from astro.byzantine_astrology.calculator import compute_byzantine_chart
from astro.byzantine_astrology.renderer import render_streamlit as render_byzantine_astrology_chart
from astro.shanghan_qianfa.calculator import compute_shanghan_qianfa
from astro.shanghan_qianfa.renderer import render_streamlit as render_shanghan_qianfa_chart
from astro.beiji.renderer import render_streamlit as render_beiji_chart
from astro.nanji.renderer import render_streamlit as render_nanji_chart
from astro.chunzi.renderer import render_streamlit as render_chunzi_chart
from astro.kaiyuan.renderer import render_streamlit as render_kaiyuan_chart
from astro.sumerian.calculator import compute_sumerian_chart
from wiki_renderer import render_wiki
from astro.sumerian.renderer import render_streamlit as render_sumerian_chart
from astro.horary import render_streamlit as render_horary_chart
from astro.sports import render_streamlit as render_sports_astrology_chart
from astro.electional import render_streamlit as render_electional_chart
from astro.wuyunliuqi.calculator import WuYunLiuQiCalculator, compute_wuyunliuqi
from astro.wuyunliuqi.renderer import render_streamlit as render_wuyunliuqi_chart, render_wuyunliuqi_intro
from astro.polynesian_hawaiian.calculator import compute_polynesian_chart
from astro.polynesian_hawaiian.renderer import render_streamlit as render_polynesian_chart_ui
from astro.andean import compute_andean_chart as _compute_andean_chart_fn
from astro.andean import render_streamlit as render_andean_chart_ui
from astro.systems.obscure import compute_armenian_chart as _compute_armenian_chart_fn
from astro.systems.obscure import render_streamlit as render_armenian_chart_ui
from astro.etruscan import compute_etruscan_chart as _compute_etruscan_chart_fn
from astro.etruscan import render_streamlit as render_etruscan_chart_ui
from astro.astronomical_geomancy import (
    compute_geomancy_chart as _compute_geomancy_chart,
    format_geomancy_for_prompt as _format_geomancy_for_prompt,
    render_streamlit as _render_geomancy_ui,
    render_input_panel as _render_geomancy_input,
)
from astro.persian.renderer import render_streamlit as render_deep_sassanian_chart
from astro.egyptian.decans import compute_decan_chart, render_decan_chart, render_decan_browse
from astro.vedic.nadi import compute_nadi_chart, render_nadi_chart
from astro.zurkhai import compute_zurkhai_chart, render_zurkhai_chart
from astro.tibetan import compute_tibetan_chart, render_tibetan_chart, build_kalachakra_mandala_svg
from astro.western.hellenistic import (compute_hellenistic_chart, render_hellenistic_chart, build_greek_horoscope_svg,
                                      compute_hellenistic_extended, render_extended_lots, render_valens_combinations)
from frontend.hellenistic_enhanced_renderer import (render_annual_profections, render_zodiacal_releasing)
from astro.babylonian import compute_babylonian_chart, render_babylonian_chart, build_babylonian_planisphere_svg, build_k8538_planisphere_svg
from astro.yemeni import compute_yemeni_chart, render_yemeni_chart, build_yemeni_manzil_mandala_svg
from astro.western.ptolemy_dignities import PtolemyDignityCalculator, Planet as PtolPlanet, DignityType, dignity_to_chinese, SIGN_NAMES
from astro.western.fixed_stars import compute_fixed_star_positions, find_conjunctions, STAR_CATALOG_ALL
from astro.western.asteroids import compute_asteroids, ASTEROID_GROUPS
from astro.western.advanced_bodies import (
    calculate_parans, calculate_heliacal, get_asteroid_aspects,
)
from astro.western.uranian import compute_uranian_chart, render_uranian_chart
from astro.cosmobiology import compute_cosmobiology_chart, render_cosmobiology
from astro.harmonic import compute_multi_harmonic, render_harmonic
from astro.primary_directions import compute_primary_directions, render_primary_directions
from astro.esoteric import compute_esoteric_chart
from astro.esoteric.renderer import render_streamlit as render_esoteric_chart
from astro.human_design import compute_human_design_chart
from astro.human_design.renderer import render_streamlit as render_human_design_chart
from astro.western.predictive_ui import render_predictive_suite
from astro.export import western_chart_to_dict, vedic_chart_to_dict, chinese_chart_to_dict, generic_chart_to_dict
from astro.natal_summary import generate_natal_summary
from astro.interpretations import (
    get_transit_reading, get_synastry_reading, get_dasha_reading,
    get_yogini_reading, get_qizheng_dasha_reading,
)
from astro.ai_analysis import (
    CerebrasClient,
    OpenAIClient,
    CustomProviderClient,
    RateLimitError,
    CEREBRAS_MODEL_OPTIONS,
    CEREBRAS_MODEL_DESCRIPTIONS,
    OPENAI_MODEL_OPTIONS,
    OPENAI_MODEL_DESCRIPTIONS,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_SYSTEM_PROMPT_EN,
    detect_language,
    format_chart_for_prompt,
)

from astro.arabic.picatrix_mansions import (
    render_mansion_lookup,
    render_planetary_hours_tool,
    render_talisman_generator,
    render_picatrix_browse,
    get_mansion_index,
    compute_moon_longitude,
)
from astro.arabic.picatrix_invocations import render_picatrix_invocations
from astro.arabic.shams_maarif import render_shams_browse, render_shams_chart
from astro.arabic.ms164_browser import render_ms164_browse
from astro.picatrix_behenian import render_streamlit as render_picatrix_behenian
from astro.chinstar.chinstar import WanHuaXianQin
from astro.twelve_ci import compute_twelve_ci_chart, render_twelve_ci_chart, build_twelve_ci_svg
from astro.sanshi.liuren import compute_liuren_chart, render_liuren_chart, compute_lunming, render_lunming_report
from astro.sanshi.taiyi import compute_taiyi_chart, render_taiyi_chart
from astro.sanshi.qimen_luming import compute_qimen_luming, render_qimen_luming
from astro.astrocartography import (
    compute_astrocartography,
    compute_astrocartography_transit,
    format_acg_for_prompt,
    PLANET_GLYPHS,
    PLANET_COLORS as ACG_PLANET_COLORS,
    LINE_COLORS as ACG_LINE_COLORS,
    ACG_PLANETS,
)
from astro.nine_star_ki import compute_nine_star_ki_chart, render_nine_star_ki_chart
from astro.celtic import compute_celtic_tree_chart, render_celtic_tree_chart
from astro.chinese.taixuan import TaiXuanCalculator
from astro.chinese.taixuan.taixuan_renderer import (
    render_taixuan_chart,
    render_taixuan_intro,
    render_qigua_ui,
)
from astro.rectification.renderer import render_streamlit as render_rectification_page
from astro.trutine_of_hermes.renderer import render_streamlit as render_trutine_chart
from astro.bazi import compute_bazi as compute_bazi_chart, render_streamlit as render_bazi_chart
from astro.mundane import render_streamlit as render_mundane_chart
from astro.system_registry import get_system

from ui.state import SessionKeys, init_session_state_defaults
from ui.components.birth_form import BirthChartParams, build_birth_params
from ui.components.system_selector import render_system_selector
from ui.components.overview_dashboard import render_overview_dashboard
from ui.system_engine import EXECUTION_REGISTRY
from ui.system_handlers.phase1_handlers import build_ziwei_handler
from frontend.arabic_lots_dashboard import render_arabic_lots_dashboard
from frontend.european_geomancy_renderer import render_european_geomancy
from frontend.fludd_rota_renderer import render_fludd_rota
from astro.fludd_rota import config_from_dict as _fludd_config_from_dict
from frontend.alchemical_renderer import render_alchemical_tab
from frontend.bahre_hasab_renderer import render_bahre_hasab_tab


# ============================================================
# Homepage Landing Page (當未選擇體系時顯示)
# ============================================================
def render_homepage():
    """Render the aesthetic homepage landing page."""
    _lang = st.session_state.get("lang", "zh")

    _categories = [
        ("☯️", "三式神機", "San Shi Divination",
         ["大六壬", "太乙神數", "奇門祿命"],
         "#C9A84C", "rgba(201,168,76,0.12)", "rgba(201,168,76,0.28)"),
        ("🏮", "中式占星", "Chinese Systems",
         ["紫微斗數", "七政四餘", "萬化仙禽", "十二星次", "策天飛星", "達摩一掌經", "鐵板神數", "邵子神數", "皇極經世",
          "鬼谷分定經", "滌器遺訣", "太玄數占星", "開元占經", "五運六氣", "六爻終身卦", "北極神數", "南極神數", "子平八字", "蠢子數"],
         "#C9A84C", "rgba(201,168,76,0.10)", "rgba(201,168,76,0.22)"),
        ("🏛️", "西洋占星", "Western Astrology",
         ["西洋占星", "薩比安符號", "希臘化占星", "星移地圖", "天王星漢堡", "宇宙生物學", "和諧占星",
          "古典主限推運", "凱爾特樹", "出生時間校正", "赫密士前世盤", "靈性占星", "拜占庭占星", "人間圖", "世俗占星", "弗拉德命運輪盤", "煉金占星"],
         "#7B9ED9", "rgba(123,158,217,0.1)", "rgba(123,158,217,0.22)"),
        ("🪷", "印度占星", "Vedic Jyotish",
         ["Jyotish", "紅皮書 Lal Kitab", "納迪占星", "Jaimini", "KP 占星", "吠陀風水"],
         "#FF9933", "rgba(255,153,51,0.1)", "rgba(255,153,51,0.22)"),
        ("🌏", "亞洲體系", "Asian Systems",
         ["土亭數", "宿曜道", "泰國占星", "老撾占星", "緬甸 Mahabote", "峇里 Wariga", "爪哇 Weton", "馬來伊斯蘭占星（十二星）", "馬來七星五刻占卜", "祖爾海", "藏傳時輪金剛",
             "九星氣學", "高棉占星", "波利尼西亞"],
            "#E0A526", "rgba(224,165,38,0.1)", "rgba(224,165,38,0.22)"),
        ("🕌", "中東體系", "Middle East Systems",
         ["卡巴拉", "猶太占星", "薩珊波斯", "薩珊波斯進階版", "阿拉伯占星", "也門占星", "Picatrix 占星魔法", "柏柏爾占星", "地占占星"],
           "#3AB09E", "rgba(58,176,158,0.1)", "rgba(58,176,158,0.22)"),
        ("🌍", "非洲體系", "African Systems",
         ["衣索比亞 Bahre Hasab", "多貢天狼星宇宙學"],
         "#B07D42", "rgba(176,125,66,0.1)", "rgba(176,125,66,0.22)"),
        ("🜁", "隱祕與原民傳統", "Obscure & Indigenous",
         ["亞美尼亞占星"],
         "#A06C3B", "rgba(160,108,59,0.1)", "rgba(160,108,59,0.22)"),
        ("🏺", "古代文明", "Ancient Civilizations",
         ["瑪雅占星", "印加／安地斯占星", "阿茲特克", "古埃及十度", "巴比倫占星", "蘇美/美索不達米亞", "伊特魯里亞占星"],
         "#D4A04A", "rgba(212,160,74,0.1)", "rgba(212,160,74,0.22)"),
        ("⚕️", "醫占", "Medical Astrology",
         ["醫學占星", "傷寒鈐法"],
         "#2ECC71", "rgba(46,204,113,0.1)", "rgba(46,204,113,0.22)"),
        ("📜", "傳統卜卦占星", "Traditional Horary",
         ["傳統卜卦占星", "運動占星", "擇日占星", "歐洲地占"],
           "#7B4EBE", "rgba(123,78,190,0.1)", "rgba(123,78,190,0.25)"),
    ]
    _total_systems = sum(len(systems) for _, _, _, systems, *_ in _categories)

    # ── Language-aware text ───────────────────────────────────
    _hp_subtitle = auto_cn(
        f"{_total_systems} 體系占星排盤平台",
        f"{_total_systems}-System Astrology Platform",
    )
    _hp_badge = auto_cn(
        "線上免費使用 · Open Source · MIT License",
        "Free Online · Open Source · MIT License",
    )
    _hp_desc = auto_cn(
        f'從七政四餘到西洋占星、從紫微斗數到印度 Jyotish、<br/>'
        f'從三式（六壬、太乙、奇門）到 Astrocartography、凱爾特樹木曆、太玄數占星、<br/>'
        f'紅皮書 Lal Kitab、薩珊波斯占星、<strong style="color:#A78BFA;">皇極經世（Huangji Jingshi）</strong>、<strong style="color:#A78BFA;">馬來伊斯蘭占星（Bintang Duabelas）</strong>、<strong style="color:#A78BFA;">馬來七星五刻占卜（Kinketika）</strong>、<strong style="color:#A78BFA;">柏柏爾占星</strong>、<strong style="color:#A78BFA;">衣索比亞 Bahre Hasab</strong>、瑪雅曆法到巴比倫星表、<strong style="color:#A78BFA;">世俗占星</strong>、<strong style="color:#A78BFA;">拜占庭占星</strong>、醫學占星、傷寒鈐法、<br/>'
        f'傳統卜卦占星、<strong style="color:#A78BFA;">運動占星（Sports Astrology）</strong>、擇日占星、蠢子數、<strong style="color:#A78BFA;">亞美尼亞占星</strong>、<strong style="color:#A78BFA;">地占占星</strong>、<strong style="color:#A78BFA;">伊特魯里亞占星</strong>、<strong style="color:#A78BFA;">煉金占星</strong>——堅占星將<strong style="color:#EAB308;font-weight:600;">全球 {_total_systems} 種占星體系</strong>融合為一，讓千年星學智慧觸手可及。',
        f'From Seven Luminaries to Western Astrology, from Zi Wei Dou Shu to Indian Jyotish,<br/>'
        f'from San Shi (Liu Ren, Tai Yi, Qi Men) to Astrocartography, Celtic Tree Calendar, Tai Xuan Shu,<br/>'
        f'Lal Kitab, Sassanid Persian Astrology, <strong style="color:#A78BFA;">Huangji Jingshi</strong>, <strong style="color:#A78BFA;">Malay Islamic Astrology (Bintang Duabelas)</strong>, <strong style="color:#A78BFA;">Malay Time Divination (Kinketika)</strong>, <strong style="color:#A78BFA;">Berber Astrology</strong>, <strong style="color:#A78BFA;">Ethiopian Bahre Hasab</strong>, Mayan Calendar to Babylonian Star Catalogue, <strong style="color:#A78BFA;">Mundane Astrology</strong>, <strong style="color:#A78BFA;">Byzantine Astrology</strong>, Medical Astrology, Shang Han Method,<br/>'
        f'Traditional Horary, <strong style="color:#A78BFA;">Sports Astrology (Frawley)</strong>, Electional Astrology, Chun Zi Shu, <strong style="color:#A78BFA;">Armenian Astrology</strong>, <strong style="color:#A78BFA;">Geomantic Astrology</strong>, <strong style="color:#A78BFA;">Etruscan Astrology</strong>, <strong style="color:#A78BFA;">Alchemical Astrology</strong> — KinAstro unifies <strong style="color:#EAB308;font-weight:600;">{_total_systems} astrology systems</strong> worldwide, bringing millennia of stellar wisdom to your fingertips.',
    )
    _hp_stat_systems = auto_cn("占星體系 Systems", "Astrology Systems")
    _hp_stat_subtabs = auto_cn("子功能分頁 Sub-tabs", "Sub-tabs")
    _hp_stat_free = auto_cn("免費開源 Free &amp; Open", "Free &amp; Open Source")
    _hp_cta_hint = auto_cn(
        "← 請從左側側邊欄選擇占星體系開始排盤",
        "← Select a system from the left sidebar to begin",
    )
    _hp_sec_systems = auto_cn("占星體系總覽", "System Overview")
    _hp_sec_features = auto_cn("核心特色", "Key Features")
    _hp_cta_title = auto_cn("開始您的星象之旅", "Begin Your Stellar Journey")
    _hp_cta_body = auto_cn(
        "在左側側邊欄輸入出生日期、時間與地點，<br/>"
        "然後選擇您想探索的占星體系，即可立即排盤。",
        "Enter your birth date, time and location in the left sidebar,<br/>"
        "then select the astrology system you'd like to explore — your chart will be generated instantly.",
    )
    _hp_cta_tip = auto_cn(
        "💡 初學者推薦從「西洋占星」或「紫微斗數」開始",
        "💡 Beginners are recommended to start with 'Western Astrology' or 'Zi Wei Dou Shu'",
    )

    # ── Hero Section ──────────────────────────────────────────
    st.markdown(textwrap.dedent(f"""
    <div class="hp-hero">
      <div class="hp-constellation">
        <svg width="100%" height="100%" viewBox="0 0 900 420"
             preserveAspectRatio="xMidYMid slice" aria-hidden="true"
             style="position:absolute;inset:0;width:100%;height:100%;">
          <circle cx="80"  cy="60"  r="1.8" fill="#EAB308" opacity="0.75"/>
          <circle cx="140" cy="110" r="1.2" fill="#A78BFA" opacity="0.6"/>
          <circle cx="210" cy="45"  r="2.2" fill="#EAB308" opacity="0.8"/>
          <circle cx="270" cy="140" r="1.0" fill="#E0E0FF" opacity="0.5"/>
          <circle cx="340" cy="80"  r="1.8" fill="#A78BFA" opacity="0.7"/>
          <circle cx="400" cy="165" r="1.4" fill="#EAB308" opacity="0.65"/>
          <circle cx="460" cy="55"  r="2.6" fill="#EAB308" opacity="0.85"/>
          <circle cx="530" cy="130" r="1.0" fill="#E0E0FF" opacity="0.5"/>
          <circle cx="590" cy="85"  r="1.8" fill="#A78BFA" opacity="0.7"/>
          <circle cx="660" cy="40"  r="1.4" fill="#EAB308" opacity="0.6"/>
          <circle cx="720" cy="150" r="2.2" fill="#A78BFA" opacity="0.75"/>
          <circle cx="790" cy="70"  r="1.2" fill="#E0E0FF" opacity="0.55"/>
          <circle cx="840" cy="120" r="1.8" fill="#EAB308" opacity="0.7"/>
          <circle cx="50"  cy="200" r="1.0" fill="#A78BFA" opacity="0.4"/>
          <circle cx="180" cy="280" r="1.4" fill="#EAB308" opacity="0.5"/>
          <circle cx="320" cy="310" r="1.0" fill="#E0E0FF" opacity="0.35"/>
          <circle cx="500" cy="290" r="1.6" fill="#A78BFA" opacity="0.5"/>
          <circle cx="700" cy="270" r="1.2" fill="#EAB308" opacity="0.45"/>
          <circle cx="860" cy="250" r="1.0" fill="#E0E0FF" opacity="0.4"/>
          <line x1="80"  y1="60"  x2="140" y2="110" stroke="#A78BFA" stroke-width="0.5" opacity="0.35"/>
          <line x1="140" y1="110" x2="210" y2="45"  stroke="#A78BFA" stroke-width="0.5" opacity="0.35"/>
          <line x1="340" y1="80"  x2="400" y2="165" stroke="#EAB308" stroke-width="0.5" opacity="0.3"/>
          <line x1="460" y1="55"  x2="530" y2="130" stroke="#A78BFA" stroke-width="0.5" opacity="0.35"/>
          <line x1="590" y1="85"  x2="660" y2="40"  stroke="#EAB308" stroke-width="0.5" opacity="0.3"/>
          <line x1="720" y1="150" x2="790" y2="70"  stroke="#A78BFA" stroke-width="0.5" opacity="0.35"/>
          <line x1="790" y1="70"  x2="840" y2="120" stroke="#A78BFA" stroke-width="0.5" opacity="0.3"/>
          <circle cx="450" cy="210" r="130" fill="none" stroke="rgba(167,139,250,0.08)" stroke-width="1"/>
          <circle cx="450" cy="210" r="105" fill="none" stroke="rgba(234,179,8,0.06)"   stroke-width="1" stroke-dasharray="5,8"/>
          <circle cx="450" cy="210" r="78"  fill="none" stroke="rgba(167,139,250,0.05)" stroke-width="1"/>
          <line x1="450" y1="80"  x2="450" y2="340" stroke="rgba(167,139,250,0.06)" stroke-width="0.6"/>
          <line x1="320" y1="210" x2="580" y2="210" stroke="rgba(167,139,250,0.06)" stroke-width="0.6"/>
          <line x1="337" y1="127" x2="563" y2="293" stroke="rgba(167,139,250,0.05)" stroke-width="0.5"/>
          <line x1="563" y1="127" x2="337" y2="293" stroke="rgba(167,139,250,0.05)" stroke-width="0.5"/>
          <line x1="370" y1="98"  x2="530" y2="322" stroke="rgba(167,139,250,0.04)" stroke-width="0.5"/>
          <line x1="530" y1="98"  x2="370" y2="322" stroke="rgba(167,139,250,0.04)" stroke-width="0.5"/>
          <text x="450" y="218" text-anchor="middle" font-size="22"
                fill="rgba(234,179,8,0.2)" font-family="serif">&#9789;</text>
        </svg>
      </div>
      <div class="hp-hero-content">
        <div class="hp-badge">
          <span class="hp-badge-dot"></span>
          <span>{_hp_badge}</span>
        </div>
        <h1 class="hp-title">
          <span class="hp-title-line1">堅占星</span>
          <span class="hp-title-line2">KinAstro</span>
          <span class="hp-title-sub">{_hp_subtitle}</span>
        </h1>
         <p class="hp-desc">
           {_hp_desc}
         </p>
        <div class="hp-stats">
          <div class="hp-stat">
            <div class="hp-stat-num">{_total_systems}</div>
            <div class="hp-stat-label">{_hp_stat_systems}</div>
          </div>
          <div class="hp-stat-sep">✦</div>
          <div class="hp-stat">
            <div class="hp-stat-num">95<span style="font-size:1.1rem">+</span></div>
            <div class="hp-stat-label">{_hp_stat_subtabs}</div>
          </div>
          <div class="hp-stat-sep">✦</div>
          <div class="hp-stat">
            <div class="hp-stat-num">100<span style="font-size:1.1rem">%</span></div>
            <div class="hp-stat-label">{_hp_stat_free}</div>
          </div>
        </div>
        <div class="hp-cta-hint">{_hp_cta_hint}</div>
      </div>
    </div>
    """), unsafe_allow_html=True)

    # ── System Categories Showcase ────────────────────────────
    st.markdown(f'<div class="hp-section-title">{_hp_sec_systems}</div>', unsafe_allow_html=True)

    _cat_html = '<div class="hp-cat-grid">'
    for icon, title_zh, title_en, systems, accent, bg, border_col in _categories:
        _pills = "".join(f'<span class="hp-sys-pill">{s}</span>' for s in systems[:4])
        if len(systems) > 4:
            _pills += f'<span class="hp-sys-pill hp-sys-pill-more">+{len(systems) - 4}</span>'
        _cat_main = title_en if _lang == "en" else auto_cn(title_zh)
        _cat_sub = title_zh if _lang == "en" else title_en
        _cat_html += (
            f'<div class="hp-cat-card" style="'
            f'--cat-accent:{accent};--cat-bg:{bg};--cat-border:{border_col};">'
            f'<div class="hp-cat-icon">{icon}</div>'
            f'<div class="hp-cat-title">{_cat_main}</div>'
            f'<div class="hp-cat-en">{_cat_sub}</div>'
            f'<div class="hp-cat-pills">{_pills}</div>'
            f'</div>'
        )
    _cat_html += '</div>'
    st.markdown(_cat_html, unsafe_allow_html=True)

    # ── Feature Cards ─────────────────────────────────────────
    st.markdown(f'<div class="hp-section-title">{_hp_sec_features}</div>', unsafe_allow_html=True)

    _features = [
        ("🔮",
         auto_cn(f"{_total_systems} 體系合一", f"{_total_systems} Systems in One"),
         auto_cn(f"在同一介面中切換中國、西洋、印度、阿拉伯、瑪雅等全球 {_total_systems} 種占星體系",
                 f"Switch between {_total_systems} global astrology traditions — Chinese, Western, Indian, Arabic, Mayan and more — all in a single interface")),
        ("🪐",
         auto_cn("精密天文計算", "Precision Astronomy"),
         auto_cn("使用瑞士星曆表 (Swiss Ephemeris) pyswisseph 進行高精度天文運算",
                 "High-precision astronomical calculations powered by Swiss Ephemeris (pyswisseph)")),
        ("🤖",
         auto_cn("AI 智慧分析", "AI-Powered Analysis"),
         auto_cn("整合 Cerebras / OpenAI，提供專業命理解讀，支援中英雙語互動問答",
                 "Integrated with Cerebras / OpenAI for professional chart readings with bilingual Q&A")),
        ("📊",
         auto_cn("精美 SVG 圖表", "Beautiful SVG Charts"),
         auto_cn("純 SVG 渲染，清晰美觀，支援響應式設計，手機平板完美顯示",
                 "Pure SVG rendering — crisp, responsive, and perfect on mobile and tablet")),
        ("🌍",
         auto_cn("三語介面", "Trilingual Interface"),
         auto_cn("繁體中文、簡體中文、English 即時切換，無需重新載入",
                 "Switch instantly between Traditional Chinese, Simplified Chinese, and English — no reload required")),
        ("🆓",
         auto_cn("完全免費開源", "Free & Open Source"),
         auto_cn("MIT License，永久免費，無任何隱藏費用，歡迎 Fork 與貢獻",
                 "MIT License — free forever, no hidden fees. Fork and contribute welcome")),
    ]

    _feat_html = '<div class="hp-feat-grid">'
    for icon, title, desc in _features:
        _feat_html += (
            f'<div class="hp-feat-card glass-card">'
            f'<div class="hp-feat-icon">{icon}</div>'
            f'<div class="hp-feat-title">{title}</div>'
            f'<div class="hp-feat-desc">{desc}</div>'
            f'</div>'
        )
    _feat_html += '</div>'
    st.markdown(_feat_html, unsafe_allow_html=True)

    # ── Getting Started CTA ───────────────────────────────────
    st.markdown(textwrap.dedent(f"""
    <div class="hp-cta-box">
      <div class="hp-cta-stars">✦ ✧ ✦ ✧ ✦</div>
      <h3 class="hp-cta-title">{_hp_cta_title}</h3>
      <p class="hp-cta-body">
        {_hp_cta_body}
      </p>
      <div class="hp-cta-tips">
        <span class="hp-tip">{_hp_cta_tip}</span>
      </div>
    </div>
    """), unsafe_allow_html=True)




# ============================================================
# 頁面設定
# ============================================================
st.set_page_config(
    page_title="堅占星 KinAstro | 世界占星",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def _load_custom_css() -> str:
    """Load custom.css from disk (cached so the file is only read once)."""
    _css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
    if os.path.exists(_css_path):
        with open(_css_path, "r", encoding="utf-8") as _f:
            return _f.read()
    return ""


def inject_custom_css():
    """Inject all custom CSS (mobile + custom.css) into the page."""
    # Google Fonts — loaded once at the top of every page
    st.markdown(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Cinzel:wght@400;600;700;900'
        '&family=Noto+Serif+TC:wght@300;400;700;900'
        '&family=Space+Grotesk:wght@300;400;500;600;700'
        '&family=Noto+Sans+TC:wght@300;400;500;700'
        '&family=Inter:wght@300;400;500;600'
        '&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
    _custom = _load_custom_css()
    if _custom:
        st.markdown(f"<style>{_custom}</style>", unsafe_allow_html=True)

    # Apply theme data attribute via JS
    _theme = st.session_state.get("_ka_theme", "modern")
    _valid_themes = {"modern", "classic", "mystic"}
    if _theme not in _valid_themes:
        _theme = "modern"
    st.markdown(
        f"""<script>
        (function() {{
            var app = window.parent.document.querySelector('.stApp');
            if (app) app.setAttribute('data-ka-theme', '{_theme}');
        }})();
        </script>""",
        unsafe_allow_html=True,
    )


inject_custom_css()
init_session_state_defaults(st)


def _build_star_particles_html() -> str:
    """Build CSS-based star particle background HTML (60 particles)."""
    parts = []
    for _ in range(60):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        dur = random.uniform(2.5, 6.0)
        delay = random.uniform(0, 5.0)
        opacity = random.uniform(0.3, 0.8)
        size = random.choices([1, 2, 3], weights=[1, 2, 1], k=1)[0]
        color = random.choices(["#EAB308", "#A78BFA", "#E0E0FF"], weights=[3, 1, 1], k=1)[0]
        parts.append(
            f'<div class="particle" style="'
            f"left:{x:.1f}%;top:{y:.1f}%;"
            f"width:{size}px;height:{size}px;"
            f"background:{color};"
            f"--duration:{dur:.1f}s;--delay:{delay:.1f}s;"
            f'--max-opacity:{opacity:.2f};"></div>'
        )
    return '<div class="star-particles">' + "".join(parts) + "</div>"


def _inject_star_particles():
    """Inject CSS-based star particle background (cached per session)."""
    if "_star_particles_html" not in st.session_state:
        st.session_state["_star_particles_html"] = _build_star_particles_html()
    st.markdown(st.session_state["_star_particles_html"], unsafe_allow_html=True)


# Inject star particles if toggle is on (default: on for first visit)
if st.session_state.get("_star_particles", True):
    _inject_star_particles()

# ── Initialise language from the persisted selectbox widget value ────────────
# Language switcher uses a dropdown (selectbox). We check for the
# "_lang_select" session_state key that is set by the dropdown.
_LANG_MAP = {"繁體中文": "zh", "简体中文": "zh_cn", "English": "en"}
_LANG_LABEL_MAP = {v: k for k, v in _LANG_MAP.items()}
_DEFAULT_LANG_LABEL = "繁體中文"


def _sync_lang_from_selectbox() -> None:
    _sel = st.session_state.get("_lang_select", _DEFAULT_LANG_LABEL)
    st.session_state["lang"] = _LANG_MAP.get(_sel, "zh")

if "_lang_select" in st.session_state:
    _sync_lang_from_selectbox()
else:
    if "lang" not in st.session_state:
        st.session_state["lang"] = "zh"
    st.session_state["_lang_select"] = _LANG_LABEL_MAP.get(
        st.session_state.get("lang", "zh"),
        _DEFAULT_LANG_LABEL,
    )


# ── Restore birth data + system from URL query params (share feature) ─────────
def _load_from_query_params() -> bool:
    """Attempt to restore chart state from ``st.query_params``.

    Expected params: ``sys``, ``y``, ``mo``, ``d``, ``h``, ``mi``,
    ``tz``, ``lat``, ``lon``.

    Returns *True* if params were loaded, *False* otherwise.
    """
    qp = st.query_params
    if "sys" not in qp:
        return False
    try:
        sys_key = qp.get("sys", "")
        y   = int(qp.get("y",   1990))
        mo  = int(qp.get("mo",  1))
        d   = int(qp.get("d",   1))
        h   = int(qp.get("h",   12))
        mi  = int(qp.get("mi",  0))
        tz  = float(qp.get("tz",  8.0))
        lat = float(qp.get("lat", 22.3193))
        lon = float(qp.get("lon", 114.1694))
    except (ValueError, TypeError):
        return False

    # Only restore once per session to avoid overwriting user edits
    if st.session_state.get("_qp_loaded"):
        return True

    st.session_state["_system_select"] = sys_key
    st.session_state["birth_date_input"] = date(
        max(1, min(y, date.today().year)), max(1, min(mo, 12)), max(1, min(d, 31))
    )
    st.session_state["birth_time_input"] = time(
        max(0, min(h, 23)), max(0, min(mi, 59))
    )
    st.session_state["_custom_lat"] = lat
    st.session_state["_custom_lon"] = lon
    st.session_state["_custom_tz"]  = tz
    # Confirm so chart is rendered immediately
    st.session_state["_birth_confirmed"] = True
    st.session_state["_confirmed_params"] = dict(
        year=y, month=mo, day=d, hour=h, minute=mi,
        timezone=tz, latitude=lat, longitude=lon, location_name="",
    )
    st.session_state["_confirmed_gender"] = "male"
    st.session_state["_qp_loaded"] = True
    return True


_qp_restored = _load_from_query_params()


def _build_share_url(system_key: str, params: dict, base_url: str = "") -> str:
    """Build a shareable URL string from chart params.

    Parameters
    ----------
    system_key : str
        The selected system tab key.
    params : dict
        The ``_calc_params`` dict (year, month, day, hour, minute,
        timezone, latitude, longitude).
    base_url : str
        Base URL prefix (unused when running in Streamlit Cloud — the
        current page URL is used instead).
    """
    from urllib.parse import urlencode
    qd = {
        "sys": system_key,
        "y":   params.get("year", 1990),
        "mo":  params.get("month", 1),
        "d":   params.get("day", 1),
        "h":   params.get("hour", 12),
        "mi":  params.get("minute", 0),
        "tz":  params.get("timezone", 8.0),
        "lat": params.get("latitude", 22.3193),
        "lon": params.get("longitude", 114.1694),
    }
    return "?" + urlencode(qd)


def t(key: str) -> str:
    """Return the translated string for *key* in the current UI language.

    For zh_cn (Simplified Chinese), falls back to zh (Traditional) if no
    explicit zh_cn entry exists, and automatically converts to Simplified
    Chinese.
    """
    lang = st.session_state.get("lang", "zh")
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    if lang == "zh_cn":
        val = entry.get("zh_cn")
        if val is not None:
            return val
        # Fallback: convert Traditional Chinese to Simplified
        return _t2s(entry.get("zh", key))
    return entry.get(lang, entry.get("zh", key))


def _render_reference_library():
    """Render the Arabic astrology reference library sub-tab content."""
    import os
    _ref_dir = os.path.join(os.path.dirname(__file__), "astro", "reference")
    _ref_files = [
        ("astrology_fortune.md", "占星與財富 / Astrology & Fortune"),
        ("astrology_magic.md", "占星魔法 / Astrological Magic"),
        ("astrology_military.md", "軍事占星 / Military Astrology"),
    ]
    for _fname, _title in _ref_files:
        _fpath = os.path.join(_ref_dir, _fname)
        if os.path.exists(_fpath):
            with open(_fpath, "r", encoding="utf-8") as _f:
                _content = _f.read()
            with st.expander(_title, expanded=False):
                st.markdown(_content)


def _render_bphs_result(bphs_result):
    """Render BPHS interpretation result in Streamlit."""
    import pandas as pd

    # ── 1. 行星品位 (Dignity) ──
    st.markdown(t("bphs_section_dignity"))
    st.caption(t("bphs_caption_dignity"))
    _dignity_rows = []
    for d in bphs_result.dignities:
        status_icon = ""
        if d.uccha:
            status_icon = "⬆️"
        elif d.neecha:
            status_icon = "⬇️"
        elif d.moola_trikona:
            status_icon = "🔺"
        elif d.own_sign:
            status_icon = "🏠"
        _dignity_rows.append({
            "": status_icon,
            t("bphs_col_planet"): f"{auto_cn(d.planet_zh)} ({d.planet})",
            t("bphs_col_sign"): f"{auto_cn(d.rashi_zh)} ({d.rashi_en})",
            t("bphs_col_dignity"): auto_cn(d.status_zh),
        })
    if _dignity_rows:
        st.dataframe(pd.DataFrame(_dignity_rows), hide_index=True, width='stretch')

    st.divider()

    # ── 2. 行星友敵關係 (Graha Maitri) ──
    st.markdown(t("bphs_section_maitri"))
    st.caption(t("bphs_caption_maitri"))
    _maitri_rows = []
    for m in bphs_result.graha_maitri:
        _maitri_rows.append({
            t("bphs_col_planet"): f"{auto_cn(m.planet_zh)} ({m.planet})",
            t("bphs_col_friends"): auto_cn(m.friends_zh),
            t("bphs_col_neutral"): auto_cn(m.neutral_zh),
            t("bphs_col_enemies"): auto_cn(m.enemies_zh),
        })
    if _maitri_rows:
        st.dataframe(pd.DataFrame(_maitri_rows), hide_index=True, width='stretch')

    st.divider()

    # ── 3. 行星阿瓦斯塔 (Graha Avastha) ──
    st.markdown(t("bphs_section_avastha"))
    st.caption(t("bphs_caption_avastha"))
    _strength_icon_map = {"強": "💪", "中": "⚖️", "弱": "⚠️"}
    for av in bphs_result.avasthas:
        _av_strength = auto_cn(av.strength)
        strength_icon = _strength_icon_map.get(av.strength, "❓")
        with st.expander(f"{strength_icon} {auto_cn(av.planet_zh)} ({av.planet}) — {auto_cn(av.avastha_name)} [{_av_strength}]"):
            st.markdown(f"**{t('bphs_label_avastha')}:** {auto_cn(av.avastha_name)}")
            st.markdown(f"**{t('bphs_label_strength')}:** {_av_strength}")
            st.markdown(f"**{t('bphs_label_effect')}:** {auto_cn(av.reading_zh)}")

    st.divider()

    # ── 4. 王者瑜伽 (Raja Yoga) ──
    st.markdown(t("bphs_section_raja"))
    st.caption(t("bphs_caption_raja"))
    for ry in bphs_result.raja_yogas:
        icon = "✅" if ry.is_present else "⬜"
        with st.expander(f"{icon} {auto_cn(ry.name)}"):
            st.markdown(f"**{t('bphs_label_description')}:** {auto_cn(ry.description_zh)}")
            st.markdown(f"**{t('bphs_label_judgment')}:** {auto_cn(ry.reason_zh)}")

    st.divider()

    # ── 5. 宮位果報 (Bhava Phala) ──
    st.markdown(t("bphs_section_bhava"))
    st.caption(t("bphs_caption_bhava"))
    for br in bphs_result.bhava_readings:
        _house_label = t("bphs_label_house_num").format(n=br.bhava)
        label_parts = [f"{_house_label} {auto_cn(br.bhava_zh)}"]
        if br.signification:
            label_parts.append(f"— {br.signification}")
        label = " ".join(label_parts)
        with st.expander(label):
            _lord_in = t("bphs_label_lord_in_house").format(n=br.lord_house)
            st.markdown(f"**{t('bphs_label_house_lord')}:** {auto_cn(br.lord_zh)} ({br.lord_key}) — {_lord_in}")
            if br.lord_placement_zh:
                st.info(f"{t('bphs_label_lord_reading')}：{auto_cn(br.lord_placement_zh)}")
            if br.planets_in_bhava:
                st.markdown(t("bphs_label_planets_in"))
                for pk, pk_zh, reading, level in br.planets_in_bhava:
                    level_str = f" [{auto_cn(level)}]" if level else ""
                    st.markdown(f"- **{auto_cn(pk_zh)}** ({pk}){level_str}：{auto_cn(reading)}")
            if br.special_yogas:
                st.markdown(t("bphs_label_special_yogas"))
                for sy in br.special_yogas:
                    st.markdown(f"- **{auto_cn(sy.get('name', ''))}**：{auto_cn(sy.get('zh', ''))}")
            if br.note_zh:
                st.caption(f"💡 {auto_cn(br.note_zh)}")

    st.divider()

    # ── 6. 16分盤簡表 (Shodasa Varga Reference) ──
    st.markdown(t("bphs_section_varga"))
    st.caption(t("bphs_caption_varga"))
    _varga_rows = []
    for key, val in bphs_result.varga_info.get("vargas", {}).items():
        _varga_rows.append({
            t("bphs_col_varga_chart"): key,
            t("bphs_col_varga_name"): auto_cn(val.get("zh", "")),
            t("bphs_col_varga_division"): val.get("division", ""),
            t("bphs_col_varga_use"): auto_cn(val.get("use", "")),
            t("bphs_col_varga_judgment"): auto_cn(val.get("judgment", "")),
        })
    if _varga_rows:
        st.dataframe(pd.DataFrame(_varga_rows), hide_index=True, width='stretch')
    note = bphs_result.varga_info.get("general_note_zh", "")
    if note:
        st.caption(f"💡 {auto_cn(note)}")


# ── Language switcher (top-right corner) ───────────────────
_cur_lang = st.session_state.get("lang", "zh")
_lang_labels = ["繁體中文", "简体中文", "English"]
_lang_codes = ["zh", "zh_cn", "en"]

_lang_spacer, _lang_col = st.columns([4, 1])
with _lang_col:
    st.markdown('<div class="ka-lang-switcher">🌐 ' + t("lang_switcher_label") + "</div>", unsafe_allow_html=True)
    _sel_lang = st.selectbox(
        t("lang_switcher_label"),
        options=_lang_labels,
        key="_lang_select",
        on_change=_sync_lang_from_selectbox,
        label_visibility="collapsed",
    )

# Only show title/subtitle on chart pages; homepage has its own hero section
if "_system_select" in st.session_state:
    st.title(t("app_title"))
    st.markdown(
        '<p class="app-subtitle">' + t("app_subtitle") + "</p>",
        unsafe_allow_html=True,
    )

# ============================================================
# 世界城市資料 (城市, 緯度, 經度, 時區)
# ============================================================
_CITY_DATA_DIR = Path(__file__).resolve().parent / "tools" / "cities"
_CITY_WORLD_LIMIT = 3000
_CHINA_REGION_TZ = 8.0
# Default custom coordinates/timezone start from Hong Kong.
_DEFAULT_LAT = 22.3193
_DEFAULT_LON = 114.1694
_DEFAULT_TZ = 8.0
_CITY_CUSTOM_LABEL = "自訂"


def _normalize_tz_from_lon(lon: float) -> float:
    # Approximate timezone using 15° longitude per hour, rounded to nearest 0.5.
    tz = round((float(lon) / 15.0) * 2) / 2
    return max(-12.0, min(14.0, tz))


def _coerce_float_in_range(
    value: Any,
    *,
    default: float,
    min_value: float,
    max_value: float,
) -> float:
    try:
        _num = float(value)
    except (TypeError, ValueError):
        _num = default
    return max(min_value, min(max_value, _num))


def _safe_pop(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


@st.cache_data(show_spinner=False)
def _build_city_presets() -> tuple[
    dict[str, tuple[float, float, float]],
    list[str],
]:
    city_presets: dict[str, tuple[float, float, float]] = {}

    def _add_city(city_name: str, lat: float, lon: float, tz: float) -> None:
        if city_name not in city_presets:
            city_presets[city_name] = (lat, lon, tz)

    # China hierarchical dataset: province/city -> district
    china_file = _CITY_DATA_DIR / "china_cities.json"
    if china_file.exists():
        china_data = json.loads(china_file.read_text(encoding="utf-8"))

        def _collect_china_city(city_node: dict) -> None:
            city_name = (city_node.get("name") or "").strip()
            center = city_node.get("center") or {}
            if not city_name or "latitude" not in center or "longitude" not in center:
                return

            lat = float(center["latitude"])
            lon = float(center["longitude"])
            tz = _CHINA_REGION_TZ
            _add_city(city_name, lat, lon, tz)

        for province in china_data.get("districts", []) or []:
            province_name = province.get("name")
            province_center = province.get("center") or {}
            province_tz = _CHINA_REGION_TZ

            city_children = [
                c for c in (province.get("districts", []) or [])
                if c.get("level") == "city"
            ]
            if city_children:
                for city_node in city_children:
                    _collect_china_city(city_node)
            elif province_name and "latitude" in province_center and "longitude" in province_center:
                # Direct-controlled municipalities / SAR fallback
                _add_city(
                    province_name,
                    float(province_center["latitude"]),
                    float(province_center["longitude"]),
                    province_tz,
                )

    # World flat dataset: city + admin fields
    world_file = _CITY_DATA_DIR / "cities.json"
    if world_file.exists():
        world_rows = json.loads(world_file.read_text(encoding="utf-8"))
        world_rows.sort(key=lambda r: _safe_pop(r.get("pop")), reverse=True)

        for row in world_rows[:_CITY_WORLD_LIMIT]:
            name = (row.get("name") or "").strip()
            country = (row.get("country") or "").strip()
            if not name or "lat" not in row or "lon" not in row:
                continue

            city_label = f"{name} ({country})" if country else name
            lat = float(row["lat"])
            lon = float(row["lon"])
            tz = _CHINA_REGION_TZ if country in {"CN", "HK", "MO", "TW"} else _normalize_tz_from_lon(lon)
            _add_city(city_label, lat, lon, tz)

    # Custom fallback
    city_presets[_CITY_CUSTOM_LABEL] = (0.0, 0.0, 0.0)

    city_options = sorted([c for c in city_presets if c != _CITY_CUSTOM_LABEL]) + [_CITY_CUSTOM_LABEL]
    return city_presets, city_options


CITY_PRESETS, CITY_OPTIONS = _build_city_presets()


# ============================================================
# 側邊欄 - 輸入排盤資料
# ============================================================
with st.sidebar:
    st.header(t("sidebar_header"))

    # ── "Now" button outside the form so it can trigger a rerun ──
    _dt_col, _now_col = st.columns([3, 1])
    _dt_col.subheader(t("date_time"))
    if _now_col.button(
        auto_cn("現時", "Now"),
        key="now_btn",
        width="stretch",
        help=auto_cn("填入現在的日期和時間", "Fill in the current date and time"),
    ):
        _now = datetime.now()
        st.session_state["birth_date_input"] = _now.date()
        st.session_state["birth_time_input"] = _now.time().replace(second=0, microsecond=0)
        st.rerun()

    # ── Birth data form — all inputs wrapped so only submit triggers rerun ──
    # Initialise session-state defaults once so widgets can use key= without value=
    if "birth_date_input" not in st.session_state:
        st.session_state["birth_date_input"] = date(1990, 1, 1)
    if "birth_time_input" not in st.session_state:
        st.session_state["birth_time_input"] = time(12, 0)
    if "_lat_input" not in st.session_state:
        st.session_state["_lat_input"] = _DEFAULT_LAT
    if "_lon_input" not in st.session_state:
        st.session_state["_lon_input"] = _DEFAULT_LON
    if "_tz_input" not in st.session_state:
        st.session_state["_tz_input"] = _DEFAULT_TZ
    # Place city selector outside the form so switching city reruns immediately
    # and can sync lat/lon/timezone fields.
    st.subheader(t("birth_location"))
    city = st.selectbox(
        t("city_preset"),
        options=CITY_OPTIONS,
        key="city_sel",
    )

    _prev_city = st.session_state.get("_prev_city_sel")
    if _prev_city == _CITY_CUSTOM_LABEL and city != _CITY_CUSTOM_LABEL:
        # Persist current custom edits before switching to a preset city;
        # they will be restored when user switches back to custom mode.
        st.session_state["_custom_lat"] = st.session_state.get("_lat_input", _DEFAULT_LAT)
        st.session_state["_custom_lon"] = st.session_state.get("_lon_input", _DEFAULT_LON)
        st.session_state["_custom_tz"] = st.session_state.get("_tz_input", _DEFAULT_TZ)
    st.session_state["_prev_city_sel"] = city

    with st.form("birth_data_form", border=False):
        birth_date = st.date_input(
            t("birth_date"),
            min_value=date(1, 1, 1),
            max_value=date(date.today().year, 12, 31),
            key="birth_date_input",
        )
        birth_time = st.time_input(
            t("birth_time"),
            key="birth_time_input",
        )

        # Always show lat/lon/tz so values are visible inside the form.
        # When a preset city is selected the fields are pre-populated and
        # disabled; for 自訂 (custom) they are editable.
        _is_custom = city == _CITY_CUSTOM_LABEL
        if not _is_custom:
            _preset_lat, _preset_lon, _preset_tz = CITY_PRESETS.get(
                city,
                (_DEFAULT_LAT, _DEFAULT_LON, _DEFAULT_TZ),
            )
            st.session_state["_lat_input"] = _preset_lat
            st.session_state["_lon_input"] = _preset_lon
            st.session_state["_tz_input"] = _preset_tz
        else:
            _preset_lat = _coerce_float_in_range(
                st.session_state.get("_custom_lat", _DEFAULT_LAT),
                default=_DEFAULT_LAT,
                min_value=-90.0,
                max_value=90.0,
            )
            _preset_lon = _coerce_float_in_range(
                st.session_state.get("_custom_lon", _DEFAULT_LON),
                default=_DEFAULT_LON,
                min_value=-180.0,
                max_value=180.0,
            )
            _preset_tz = _coerce_float_in_range(
                st.session_state.get("_custom_tz", _DEFAULT_TZ),
                default=_DEFAULT_TZ,
                min_value=-12.0,
                max_value=14.0,
            )
            if _prev_city != _CITY_CUSTOM_LABEL:
                st.session_state["_lat_input"] = _preset_lat
                st.session_state["_lon_input"] = _preset_lon
                st.session_state["_tz_input"] = _preset_tz

        # Keep custom-mode state resilient against stale / out-of-range values.
        if _is_custom and _prev_city == _CITY_CUSTOM_LABEL:
            st.session_state["_lat_input"] = _coerce_float_in_range(
                st.session_state.get("_lat_input", _DEFAULT_LAT),
                default=_DEFAULT_LAT,
                min_value=-90.0,
                max_value=90.0,
            )
            st.session_state["_lon_input"] = _coerce_float_in_range(
                st.session_state.get("_lon_input", _DEFAULT_LON),
                default=_DEFAULT_LON,
                min_value=-180.0,
                max_value=180.0,
            )
            st.session_state["_tz_input"] = _coerce_float_in_range(
                st.session_state.get("_tz_input", _DEFAULT_TZ),
                default=_DEFAULT_TZ,
                min_value=-12.0,
                max_value=14.0,
            )

        _coord_col1, _coord_col2 = st.columns(2)
        with _coord_col1:
            input_lat = st.number_input(
                t("latitude"),
                format="%.4f",
                min_value=-90.0,
                max_value=90.0,
                disabled=not _is_custom,
                key="_lat_input",
            )
        with _coord_col2:
            input_lon = st.number_input(
                t("longitude"),
                format="%.4f",
                min_value=-180.0,
                max_value=180.0,
                disabled=not _is_custom,
                key="_lon_input",
            )
        input_tz = st.number_input(
            t("timezone"),
            format="%.1f",
            min_value=-12.0,
            max_value=14.0,
            step=0.5,
            disabled=not _is_custom,
            key="_tz_input",
        )
        if _is_custom:
            if not (-90.0 <= input_lat <= 90.0) or not (-180.0 <= input_lon <= 180.0):
                st.warning(t("form_validation_location"))

        if _is_custom:
            location_name = t("custom_location")
        else:
            location_name = city

        # 性別（用於七政四餘宮位方向）
        st.subheader(t("gender_header"))
        _male_label = t("male")
        _female_label = t("female")
        gender_choice = st.radio(
            t("gender_label"),
            options=[_male_label, _female_label],
            index=0,
            horizontal=True,
        )
        gender = "male" if gender_choice == _male_label else "female"

        # Submit button — chart computation triggered only on click
        _form_submitted = st.form_submit_button(
            t("generate_chart_btn"),
            width="stretch",
            type="primary",
        )
        if _form_submitted:
            # Persist custom coords for next session
            if _is_custom:
                st.session_state["_custom_lat"] = input_lat
                st.session_state["_custom_lon"] = input_lon
                st.session_state["_custom_tz"]  = input_tz
            # Mark that the user has confirmed the birth data
            st.session_state["_calc_success_flash"] = True
            st.session_state["_birth_confirmed"] = True
            st.session_state["_confirmed_params"] = dict(
                year=birth_date.year, month=birth_date.month, day=birth_date.day,
                hour=birth_time.hour, minute=birth_time.minute,
                timezone=input_tz, latitude=input_lat, longitude=input_lon,
                location_name=location_name,
            )
            st.session_state["_confirmed_gender"] = gender

    # ── Astrology system selector (categorised accordion with search) ──
    st.divider()
    st.markdown(
        f'<div class="sidebar-system-title">🌐 {t("sidebar_system_label")}</div>',
        unsafe_allow_html=True,
    )

    # ── System search box ──────────────────────────────────────
    _search_placeholder = auto_cn("搜尋占星體系...") if st.session_state.get("lang", "zh") in ("zh", "zh_cn") else "Search systems..."
    _system_search = st.text_input(
        "🔍",
        placeholder=_search_placeholder,
        key="_system_search",
        label_visibility="collapsed",
    )

    _selected_system = st.session_state.get(SessionKeys.SYSTEM_SELECT, None)
    _selected_system = render_system_selector(
        st_module=st,
        t=t,
        search_query=_system_search,
        current_system=_selected_system,
    )

    # ── History of Astrology link ─────────────────────────────
    if st.button(
        t("tab_history"),
        key="_btn_history",
        width="stretch",
        type="secondary",
    ):
        st.session_state["_system_select"] = "tab_history"
        st.rerun()

    # ── Astrology Wiki link ────────────────────────────────────
    if st.button(
        t("tab_wiki"),
        key="_btn_wiki",
        width="stretch",
        type="secondary",
    ):
        st.session_state["_system_select"] = "tab_wiki"
        st.rerun()

    # ── Star particles toggle ──────────────────────────────────
    st.divider()
    _particles_on = st.toggle(
        "✨ " + ("星空粒子背景" if _cur_lang in ("zh", "zh_cn") else "Star Particles"),
        value=st.session_state.get("_star_particles", True),
        key="_star_particles_toggle",
    )
    if _particles_on != st.session_state.get("_star_particles", True):
        st.session_state["_star_particles"] = _particles_on
        st.rerun()

    # ── Cross-system comparison toggle ────────────────────────
    _cross_system_on = st.toggle(
        t("enable_cross_system"),
        value=st.session_state.get("_cross_system_enabled", False),
        key="_cross_system_toggle",
        help=(
            "同時計算西洋、印度、七政四餘、紫微、希臘占星並進行 AI 交叉比對解讀"
            if _cur_lang in ("zh", "zh_cn") else
            "Compute Western, Vedic, Chinese, Zi Wei, and Hellenistic charts "
            "together for AI cross-system synthesis"
        ),
    )
    if _cross_system_on != st.session_state.get("_cross_system_enabled", False):
        st.session_state["_cross_system_enabled"] = _cross_system_on
        st.rerun()

    # ── Advanced Bodies settings ───────────────────────────────
    st.divider()
    with st.expander(t("adv_bodies_header"), expanded=False):
        _adv_ast = st.toggle(
            t("adv_asteroids_toggle"),
            value=st.session_state.get("_adv_asteroids", True),
            key="_adv_asteroids",
        )
        if _adv_ast:
            _group_options = {
                t("adv_group_chiron_pholus"): "chiron_pholus",
                t("adv_group_lilith"):        "lilith",
                t("adv_group_main_belt"):     "main_belt",
                t("adv_group_romance"):       "romance",
                t("adv_group_centaurs"):      "centaurs",
                t("adv_group_tnos"):          "tnos",
                t("adv_group_dwarf_planets"): "dwarf_planets",
            }
            _selected_groups = st.multiselect(
                t("adv_asteroids_groups"),
                options=list(_group_options.keys()),
                default=list(_group_options.keys())[:3],
                key="_adv_ast_groups",
            )
            st.session_state["_adv_ast_group_keys"] = [
                _group_options[g] for g in _selected_groups
            ]
            st.toggle(
                t("adv_asteroids_helio"),
                value=False,
                key="_adv_helio",
            )
            st.toggle(
                t("adv_asteroid_aspects_toggle"),
                value=True,
                key="_adv_ast_aspects",
            )

        _adv_stars = st.toggle(
            t("adv_stars_toggle"),
            value=st.session_state.get("_adv_fixed_stars", False),
            key="_adv_fixed_stars",
        )
        if _adv_stars:
            st.select_slider(
                t("adv_stars_count"),
                options=[10, 30, 50, STAR_CATALOG_ALL],
                value=30,
                key="_adv_stars_count",
                format_func=lambda v: ("全部 / All" if v == STAR_CATALOG_ALL else str(v)),
            )

        _adv_parans = st.toggle(
            t("adv_parans_toggle"),
            value=st.session_state.get("_adv_parans", False),
            key="_adv_parans",
            help=t("adv_parans_tooltip"),
        )

        _adv_heliacal = st.toggle(
            t("adv_heliacal_toggle"),
            value=st.session_state.get("_adv_heliacal", False),
            key="_adv_heliacal",
            help=t("adv_heliacal_tooltip"),
        )

    # ── AI Analysis settings ──────────────────────────────────
    st.divider()
    with st.expander(t("ai_settings_header"), expanded=False):

        # Provider selector
        def _fmt_provider(x):
            if x == "cerebras":
                return t("ai_provider_cerebras")
            if x == "openai":
                return t("ai_provider_openai")
            return t("ai_provider_custom")

        _ai_provider = st.radio(
            t("ai_provider_label"),
            options=["cerebras", "openai", "custom"],
            format_func=_fmt_provider,
            key="_ai_provider",
            horizontal=True,
        )

        # Model selector — options change depending on provider
        if _ai_provider == "openai":
            _ai_model = st.selectbox(
                t("ai_model_label"),
                options=OPENAI_MODEL_OPTIONS,
                index=0,
                key="_ai_model_select",
                help="\n".join(f"• {k}: {v}" for k, v in OPENAI_MODEL_DESCRIPTIONS.items()),
            )
            # OpenAI API key input
            st.text_input(
                t("ai_openai_key_label"),
                type="password",
                key="_ai_openai_key",
                help=t("ai_openai_key_help"),
                placeholder="sk-...",
            )
        elif _ai_provider == "custom":
            # ── Custom / Third-party provider form ──────────────
            st.text_input(
                t("ai_custom_name_label"),
                key="_ai_custom_name",
                placeholder=t("ai_custom_name_placeholder"),
            )
            st.selectbox(
                t("ai_custom_api_mode_label"),
                options=["openai_compat"],
                format_func=lambda x: t("ai_custom_api_mode_openai"),
                key="_ai_custom_api_mode",
            )
            st.text_input(
                t("ai_custom_key_label"),
                type="password",
                key="_ai_custom_key",
                help=t("ai_custom_key_help"),
            )
            _host_col, _path_col = st.columns(2)
            with _host_col:
                st.text_input(
                    t("ai_custom_host_label"),
                    key="_ai_custom_host",
                    placeholder="https://api.example.com/v1",
                )
            with _path_col:
                st.text_input(
                    t("ai_custom_path_label"),
                    key="_ai_custom_path",
                    placeholder="/chat/completions",
                    value=st.session_state.get("_ai_custom_path", "/chat/completions"),
                )
            _host_val = st.session_state.get("_ai_custom_host", "").rstrip("/")
            _path_val = st.session_state.get("_ai_custom_path", "/chat/completions")
            if _host_val:
                st.caption(f"{t('ai_custom_url_preview')}{_host_val}{_path_val}")

            # Models management
            if "_ai_custom_models" not in st.session_state:
                st.session_state["_ai_custom_models"] = []

            _m_label_col, _m_add_col, _m_reset_col, _m_fetch_col = st.columns([2, 1, 1, 1])
            with _m_label_col:
                st.markdown(f"**{t('ai_custom_models_header')}**")
            with _m_add_col:
                if st.button(t("ai_custom_models_add"), key="_btn_custom_add"):
                    st.session_state["_ai_custom_model_adding"] = True
            with _m_reset_col:
                if st.button(t("ai_custom_models_reset"), key="_btn_custom_reset"):
                    st.session_state["_ai_custom_models"] = []
                    st.session_state.pop("_ai_custom_model_adding", None)
            with _m_fetch_col:
                if st.button(t("ai_custom_models_fetch"), key="_btn_custom_fetch"):
                    _fetch_host = st.session_state.get("_ai_custom_host", "").rstrip("/")
                    _fetch_key = st.session_state.get("_ai_custom_key", "").strip()
                    if _fetch_host and _fetch_key:
                        try:
                            import openai as _oa
                            _fc = _oa.OpenAI(api_key=_fetch_key, base_url=_fetch_host)
                            _models_resp = _fc.models.list()
                            _fetched = sorted([m.id for m in _models_resp.data])
                            st.session_state["_ai_custom_models"] = _fetched
                            st.success(t("ai_custom_fetch_ok").format(len(_fetched)))
                        except Exception as _fe:
                            st.error(t("ai_custom_fetch_fail").format(str(_fe)))

            # Input row for adding a new model
            if st.session_state.get("_ai_custom_model_adding"):
                _new_model = st.text_input(
                    "",
                    key="_ai_custom_new_model_input",
                    placeholder=t("ai_custom_model_new_placeholder"),
                    label_visibility="collapsed",
                )
                _confirm_col, _cancel_col = st.columns(2)
                with _confirm_col:
                    if st.button("✔", key="_btn_custom_confirm"):
                        _nm = st.session_state.get("_ai_custom_new_model_input", "").strip()
                        if _nm and _nm not in st.session_state["_ai_custom_models"]:
                            st.session_state["_ai_custom_models"].append(_nm)
                        st.session_state.pop("_ai_custom_model_adding", None)
                        st.rerun()
                with _cancel_col:
                    if st.button("✘", key="_btn_custom_cancel"):
                        st.session_state.pop("_ai_custom_model_adding", None)
                        st.rerun()

            # Render model list
            _custom_models = st.session_state.get("_ai_custom_models", [])
            for _mi, _mname in enumerate(_custom_models):
                _mrow_cols = st.columns([4, 1])
                with _mrow_cols[0]:
                    st.text(_mname)
                with _mrow_cols[1]:
                    if st.button("⊖", key=f"_btn_del_model_{_mi}"):
                        st.session_state["_ai_custom_models"].pop(_mi)
                        st.rerun()

            # Model selector for active custom model
            if _custom_models:
                _ai_model = st.selectbox(
                    t("ai_model_label"),
                    options=_custom_models,
                    key="_ai_model_select",
                )
            else:
                _ai_model = ""
                st.session_state["_ai_model_select"] = ""
        else:
            _ai_model = st.selectbox(
                t("ai_model_label"),
                options=CEREBRAS_MODEL_OPTIONS,
                index=0,
                key="_ai_model_select",
                help="\n".join(f"• {k}: {v}" for k, v in CEREBRAS_MODEL_DESCRIPTIONS.items()),
            )

        # Use the hardcoded default system prompt (no user editing)
        st.session_state.ai_system_prompt = DEFAULT_SYSTEM_PROMPT

        # Max tokens & temperature
        _ai_max_tokens = st.slider(
            t("ai_max_tokens"), min_value=256, max_value=32768, value=8192, step=256,
            key="_ai_max_tokens",
            help=t("ai_max_tokens_help"),
        )
        _ai_temperature = st.slider(
            t("ai_temperature"), min_value=0.0, max_value=2.0, value=0.7, step=0.1,
            key="_ai_temperature",
            help=t("ai_temperature_help"),
        )

    # ── About / Contact section (always visible at sidebar bottom) ──
    st.divider()
    with st.expander(t("tab_contact"), expanded=False):
        st.subheader(t("contact_title"))
        st.markdown(t("contact_wechat"))
        st.markdown(t("contact_wechat_id"))
        st.markdown(t("contact_qq"))
        st.subheader(t("contact_other_apps"))
        _contact_apps = [
            ("https://iching.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/ichingshifa/master/pic/iching.png"),
            ("https://kintaiyi.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kintaiyi/master/pic/Untitled-1.png"),
            ("https://kinliuren.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinliuren/master/pic/Untitled-33.png"),
            ("https://kinwuzhao.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinwuzhao/refs/heads/main/pic/wuzhao.png"),
            ("https://kintaixuan.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/taixuanshifa/master/pic/taixuan.png"),
            ("https://kinwangji.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinwangji/refs/heads/main/pic/kwj.png"),
            ("https://jingjue.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/jingjue/master/pic/jingjue.png"),
            ("https://liangtouqian.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/liangtouqian/main/pic/Untitled-44.png"),
        ]
        _contact_cols = st.columns(3)
        for _ci, (_curl, _cimg) in enumerate(_contact_apps):
            with _contact_cols[_ci % 3]:
                st.markdown(
                    f'<a href="{_curl}" target="_blank"><img src="{_cimg}" style="max-width:100%;height:auto;margin-bottom:8px;"></a>',
                    unsafe_allow_html=True,
                )
        st.image(
            "https://raw.githubusercontent.com/kentang2017/kintaiyi/master/pic/20231205113526.jpg",
            width='stretch',
        )

# ============================================================
# AI Analysis helper — reusable across all system tabs
# ============================================================

def _render_ai_chat(system_key: str, chart_obj, btn_key: str = "",
                    page_content: str = ""):
    """Store chart data for the global fixed AI chat panel.

    This function no longer renders inline — it saves the chart context
    into ``st.session_state`` so the single fixed-bottom chat panel
    (rendered at the end of the page) can use it.

    Parameters
    ----------
    system_key : str
        The system tab key (e.g. ``"tab_western"``).
    chart_obj : object
        The chart object produced by the compute function.
    btn_key : str
        Optional unique key suffix (kept for API compatibility).
    page_content : str
        Optional extra text content rendered on the page that should also
        be included in the AI analysis prompt.
    """
    # Only one system tab is visible at a time, so the last call wins
    # intentionally.  Within a tab with multiple subtabs the most recent
    # chart context is the correct one for the global chat.
    st.session_state["_global_chat_system"] = system_key
    st.session_state["_global_chat_chart"] = chart_obj
    st.session_state["_global_chat_page_content"] = page_content


# Backward-compatible alias so existing call sites keep working
_render_ai_button = _render_ai_chat


def _init_execution_registry_once() -> None:
    """Register Phase 1 executable handlers once per app run."""
    if EXECUTION_REGISTRY.has_handler("tab_ziwei"):
        return
    EXECUTION_REGISTRY.register(
        build_ziwei_handler(
            compute_ziwei_chart=compute_ziwei_chart,
            render_ziwei_chart=render_ziwei_chart,
            ai_button_sink=_render_ai_button,
        )
    )


def _resolve_birth_params(
    *,
    confirmed_params: dict[str, Any] | None,
    confirmed_gender: str,
    birth_date_val: date,
    birth_time_val: time,
    timezone_val: float,
    latitude_val: float,
    longitude_val: float,
    location_name_val: str,
    fallback_gender: str,
) -> BirthChartParams:
    """Resolve unified birth parameters from confirmed/session/live widget values."""
    if confirmed_params:
        return BirthChartParams.from_dict(
            confirmed_params,
            gender=confirmed_gender or fallback_gender,
        )
    return build_birth_params(
        birth_date=birth_date_val,
        birth_time=birth_time_val,
        timezone=timezone_val,
        latitude=latitude_val,
        longitude=longitude_val,
        location_name=location_name_val,
        gender=fallback_gender,
    )


@st.cache_data(show_spinner=False)
def _cached_overview_snapshot(params_payload: dict[str, Any], gender: str) -> dict[str, dict[str, str]]:
    """Compute lightweight dashboard metrics for popular systems."""
    out: dict[str, dict[str, str]] = {}

    try:
        west = compute_western_chart(**params_payload)
        sun = next((p for p in getattr(west, "planets", []) if "Sun" in getattr(p, "name", "")), None)
        sun_sign = getattr(sun, "sign_chinese", "") or getattr(sun, "sign", "") or "-"
        out["tab_western"] = {
            "main": f"☉ {sun_sign}",
            "sub": f"P:{len(getattr(west, 'planets', []))} · A:{len(getattr(west, 'aspects', []))}",
        }
    except Exception:
        pass

    try:
        ziwei = compute_ziwei_chart(**params_payload, gender=gender)
        out["tab_ziwei"] = {
            "main": f"{getattr(ziwei, 'ming_zhu', '-')}",
            "sub": f"宮:{len(getattr(ziwei, 'palaces', []))} · 局:{getattr(ziwei, 'wu_xing_ju', '-')}",
        }
    except Exception:
        pass

    try:
        chinese = compute_chart(**params_payload, gender=gender)
        out["tab_chinese"] = {
            "main": f"{getattr(chinese, 'solar_month', '-')}",
            "sub": f"P:{len(getattr(chinese, 'planets', []))} · H:{len(getattr(chinese, 'houses', []))}",
        }
    except Exception:
        pass

    try:
        vedic = compute_vedic_chart(**params_payload)
        moon = next((p for p in getattr(vedic, "planets", []) if "Chandra" in getattr(p, "name", "")), None)
        nak = getattr(moon, "nakshatra", "-")
        out["tab_indian"] = {
            "main": f"☾ {nak}",
            "sub": f"P:{len(getattr(vedic, 'planets', []))} · H:{len(getattr(vedic, 'houses', []))}",
        }
    except Exception:
        pass

    return out


def _build_overview_items(params_payload: dict[str, Any], gender: str) -> list[dict[str, str]]:
    """Build rendered overview item cards in fixed priority order."""
    snapshot = _cached_overview_snapshot(params_payload, gender)
    ordered = ["tab_western", "tab_ziwei", "tab_chinese", "tab_indian"]
    items: list[dict[str, str]] = []
    for sys_id in ordered:
        meta = get_system(sys_id)
        metric = snapshot.get(sys_id)
        if not meta or not metric:
            continue
        items.append(
            {
                "system_id": sys_id,
                "icon": meta.icon,
                "title": t(meta.tab_key),
                "metric_main": metric.get("main", "-"),
                "metric_sub": metric.get("sub", "-"),
                "accent": meta.accent_color,
            }
        )
    return items


def _render_interactive_html(*, html: str, height: int, key: str) -> None:
    """Render embedded HTML/SVG with lightweight hover + click zoom tooltip UX."""
    component = f"""
    <div id="{key}" class="ka-interactive-frame">
      {html}
      <div class="ka-svg-tip" id="{key}-tip"></div>
    </div>
    <script>
    (function(){{
      const root = document.getElementById("{key}");
      if (!root) return;
      const tip = document.getElementById("{key}-tip");
      const svg = root.querySelector("svg");
      if (!svg) return;
      root.classList.add("ka-interactive-ready");
      let zoomed = false;
      svg.style.cursor = "zoom-in";
      svg.addEventListener("click", function(){{
        zoomed = !zoomed;
        svg.style.transition = "transform .25s ease";
        svg.style.transformOrigin = "50% 50%";
        svg.style.transform = zoomed ? "scale(1.22)" : "scale(1)";
      }});
      svg.addEventListener("mousemove", function(e){{
        const el = e.target;
        const txt = (el.getAttribute("aria-label") || el.getAttribute("title") || el.textContent || "").trim();
        if (!txt || txt.length < 2) {{
          tip.style.opacity = "0";
          return;
        }}
        tip.textContent = txt.slice(0, 52);
        tip.style.left = (e.clientX + 12) + "px";
        tip.style.top = (e.clientY + 12) + "px";
        tip.style.opacity = "1";
      }});
      svg.addEventListener("mouseleave", function(){{ tip.style.opacity = "0"; }});
    }})();
    </script>
    """
    st.components.v1.html(component, height=height, scrolling=False)


def _render_global_ai_chat():
    """Render the fixed-bottom AI chat panel using stored chart context.

    Called once at the very end of the page so the chat always appears
    at a consistent fixed position regardless of which system tab is active.
    """
    _system_key = st.session_state.get("_global_chat_system", "")
    _chart_obj = st.session_state.get("_global_chat_chart")
    _page_content = st.session_state.get("_global_chat_page_content", "")

    # Fallback: use the currently selected system so the chatbox always
    # appears even on pages that don't call _render_ai_button explicitly.
    if not _system_key:
        _system_key = st.session_state.get("_system_select", "")

    if not _system_key:
        return

    # User avatar based on sidebar gender selection
    _user_avatar = "👦" if st.session_state.get("_calc_gender") == "male" else "👧"

    _ck = f"_ai_chat_global_{_system_key}"

    # Initialize per-system chat history
    if _ck not in st.session_state:
        st.session_state[_ck] = []

    st.divider()

    # ── Fixed-bottom chat panel ───────────────────────────────
    st.markdown(
        '<div class="ai-chat-fixed-panel">',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="ai-chat-header">{t("ai_chat_header")}</div>',
        unsafe_allow_html=True,
    )

    # Clear-chat button
    _clear_key = f"{_ck}_clear"
    if st.button(t("ai_chat_clear"), key=_clear_key, type="secondary"):
        st.session_state[_ck] = []
        st.rerun()

    # Scrollable message area
    _chat_box = st.container(height=400)

    # Welcome message when history is empty
    _history = st.session_state[_ck]
    if not _history:
        with _chat_box.chat_message("assistant", avatar="🧙"):
            st.markdown(t("ai_chat_welcome"))

    # Render existing chat messages
    for _msg in _history:
        with _chat_box.chat_message(_msg["role"], avatar="🧙" if _msg["role"] == "assistant" else _user_avatar):
            st.markdown(_msg["content"])

    # Chat input
    _input_key = f"{_ck}_input"
    _user_input = st.chat_input(t("ai_chat_placeholder"), key=_input_key)

    st.markdown('</div>', unsafe_allow_html=True)

    if _user_input:
        # Show user message immediately
        _history.append({"role": "user", "content": _user_input})
        with _chat_box.chat_message("user", avatar=_user_avatar):
            st.markdown(_user_input)

        # Determine provider and resolve API key
        _provider = st.session_state.get("_ai_provider", "cerebras")

        if _provider == "openai":
            _api_key = st.session_state.get("_ai_openai_key", "").strip()
            if not _api_key:
                st.error(t("ai_openai_key_missing"))
                return
        elif _provider == "custom":
            _api_key = st.session_state.get("_ai_custom_key", "").strip()
            if not _api_key:
                st.error(t("ai_custom_key_missing"))
                return
            _custom_host = st.session_state.get("_ai_custom_host", "").strip().rstrip("/")
            if not _custom_host:
                st.error(t("ai_custom_host_missing"))
                return
            _custom_base_url = _custom_host
            if not st.session_state.get("_ai_custom_models"):
                st.error(t("ai_custom_model_missing"))
                return
        else:
            # Cerebras: try secrets then environment
            _api_key = ""
            try:
                _api_key = st.secrets.get("CEREBRAS_API_KEY", "")
            except (FileNotFoundError, KeyError, AttributeError):
                pass
            if not _api_key:
                _api_key = os.environ.get("CEREBRAS_API_KEY", "")
            if not _api_key:
                st.error(t("ai_key_missing"))
                return

        # Build messages list for the API
        if _chart_obj is not None:
            chart_prompt = format_chart_for_prompt(
                _system_key, _chart_obj, page_content=_page_content,
            )
        else:
            chart_prompt = t("ai_no_chart")
        # Detect the language of the latest user message and choose the
        # matching system prompt so the AI responds in the same language.
        _user_lang = detect_language(_user_input)
        if _user_lang == "en":
            _sys_prompt = DEFAULT_SYSTEM_PROMPT_EN
        else:
            _sys_prompt = st.session_state.get("ai_system_prompt", DEFAULT_SYSTEM_PROMPT)
        _api_messages = [
            {"role": "system", "content": _sys_prompt},
            # Provide chart data as initial context
            {"role": "user", "content": chart_prompt},
            {"role": "assistant", "content": t("ai_chat_welcome")},
        ]

        # Append full conversation history
        for _msg in _history:
            _api_messages.append({"role": _msg["role"], "content": _msg["content"]})

        with _chat_box.chat_message("assistant", avatar="🧙"):
            with st.spinner(t("ai_analyzing")):
                try:
                    if _provider == "openai":
                        client = OpenAIClient(api_key=_api_key)
                    elif _provider == "custom":
                        client = CustomProviderClient(api_key=_api_key, base_url=_custom_base_url)
                    else:
                        client = CerebrasClient(api_key=_api_key)
                    result = client.chat(
                        messages=_api_messages,
                        model=st.session_state.get("_ai_model_select", CEREBRAS_MODEL_OPTIONS[0]),
                        max_tokens=st.session_state.get("_ai_max_tokens", 8192),
                        temperature=st.session_state.get("_ai_temperature", 0.7),
                    )
                    st.markdown(result)
                    _history.append({"role": "assistant", "content": result})
                except RateLimitError:
                    st.warning(t("ai_rate_limit"))
                except Exception as e:
                    st.error(t("ai_error").format(str(e)))

        st.session_state[_ck] = _history

# ============================================================
# Welcome / Onboarding Section for Beginners
# 歡迎頁面 — 為初學者提供引導
# ============================================================

def _render_welcome():
    """Render a welcoming onboarding section for new users."""
    st.markdown(
        f'<div class="welcome-hero">'
        f'<h2>{t("welcome_hero_title")}</h2>'
        f'<p>{t("welcome_hero_body")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    _steps = [
        ("1️⃣", t("welcome_step1_title"), t("welcome_step1_body")),
        ("2️⃣", t("welcome_step2_title"), t("welcome_step2_body")),
        ("3️⃣", t("welcome_step3_title"), t("welcome_step3_body")),
    ]
    _cards_html = '<div class="step-row">'
    for _i, (_icon, _title, _body) in enumerate(_steps):
        _cards_html += (
            f'<div class="step-card">'
            f'<div class="step-num">{_i + 1}</div>'
            f'<h4>{_icon} {_title}</h4>'
            f'<p>{_body}</p>'
            f'</div>'
        )
    _cards_html += '</div>'
    st.markdown(_cards_html, unsafe_allow_html=True)

    st.info(t("welcome_quick_start"))


# ============================================================
# Homepage Check - 如果未選擇體系，顯示首頁
# ============================================================
if "_system_select" not in st.session_state:
    render_homepage()
    st.stop()  # Stop rendering main area when showing homepage

# ============================================================
# Main Area — Render the selected astrology system
# 主區域 — 根據側邊欄選擇顯示對應占星體系
# ============================================================

# Use confirmed params (submitted via form) when available, else fall back to
# current widget values so the chart still renders on first load.
_confirmed = st.session_state.get("_confirmed_params")
_birth_params = _resolve_birth_params(
    confirmed_params=_confirmed,
    confirmed_gender=st.session_state.get(SessionKeys.CONFIRMED_GENDER, gender),
    birth_date_val=birth_date,
    birth_time_val=birth_time,
    timezone_val=input_tz,
    latitude_val=input_lat,
    longitude_val=input_lon,
    location_name_val=location_name,
    fallback_gender=gender,
)
_params = _birth_params.to_dict()
gender = _birth_params.gender
birth_date = date(_birth_params.year, _birth_params.month, _birth_params.day)
birth_time = time(_birth_params.hour, _birth_params.minute)
input_tz = _birth_params.timezone
input_lat = _birth_params.latitude
input_lon = _birth_params.longitude
location_name = _birth_params.location_name

# Store params in session_state for lazy per-tab computation
st.session_state[SessionKeys.CALC_PARAMS] = _params
st.session_state[SessionKeys.CALC_GENDER] = gender
st.session_state[SessionKeys.CALCULATED] = True

_is_calculated = True

# Success flash banner after each new calculation submission
if st.session_state.get("_calc_success_flash"):
    st.markdown(
        f'<div class="ka-status-success">✅ {t("status_chart_ready")}</div>',
        unsafe_allow_html=True,
    )
    st.session_state["_calc_success_flash"] = False

# Show "loaded from share link" notice once
if _qp_restored and not st.session_state.get("_qp_notice_shown"):
    st.success(t("share_chart_loaded"))
    st.session_state["_qp_notice_shown"] = True

# Overview dashboard with popular-system key indicators
# Only show when no specific system is selected
if not _selected_system:
    with st.spinner(t("overview_dashboard_loading")):
        _overview_items = _build_overview_items(_params, gender)
    render_overview_dashboard(
        st_module=st,
        t=t,
        items=_overview_items,
        current_system=_selected_system,
    )


# No top-level tab navigation — every system renders directly on the page.
# contextlib.nullcontext() is used as a compatibility shim so the existing
# `with _natal_tab:` blocks work without modification.
_natal_tab = contextlib.nullcontext()

# ── Share-chart button (shown in main area when a system is active) ───────
with _natal_tab:
    _share_col1, _share_col2 = st.columns([4, 1])
    with _share_col2:
        _share_qs = _build_share_url(_selected_system, _params)
        _copy_js = f"""
<button onclick="navigator.clipboard.writeText(window.location.origin
  + window.location.pathname + '{_share_qs}')
  .then(()=>this.textContent='✅ Copied!')
  .catch(()=>this.textContent='⚠️ Failed');"
  style="background:rgba(167,139,250,0.18);border:1px solid rgba(167,139,250,0.35);
         color:#e0e0ff;border-radius:8px;padding:6px 14px;cursor:pointer;
         font-size:0.82rem;white-space:nowrap;">
  {t('share_chart_btn')}
</button>"""
        st.html(_copy_js)

with _natal_tab:
    _init_execution_registry_once()
    _engine_options: dict[str, Any] = {}
    if _selected_system == "tab_ziwei":
        _ziwei_col1, _ziwei_col2 = st.columns([3, 1])
        with _ziwei_col2:
            _vietnam_mode = st.toggle(
                "🇻🇳 越南 Tử Vi 模式",
                value=st.session_state.get("_ziwei_vietnam_mode", False),
                help="啟用越南 Tử Vi Đẩu Số 模式：以貓代兔、融入越南佛教與農耕文化詮釋",
                key="_ziwei_vietnam_toggle",
            )
            st.session_state["_ziwei_vietnam_mode"] = _vietnam_mode
            _engine_options["vietnam_mode"] = _vietnam_mode
        with _ziwei_col1:
            if _vietnam_mode:
                st.markdown(
                    '<span style="background:#DA251D;color:#FFCD00;'
                    'font-weight:bold;padding:4px 10px;border-radius:6px;font-size:13px">'
                    '🇻🇳 越南 Tử Vi Đẩu Số 模式已啟用</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span style="background:#1a1a2e;color:#c8a96e;'
                    'font-weight:bold;padding:4px 10px;border-radius:6px;font-size:13px">'
                    '🌟 中國紫微斗數模式</span>',
                    unsafe_allow_html=True,
                )

    _meta = get_system(_selected_system or "")
    _spinner_key = _meta.spinner_key if _meta else "info_calc_prompt"
    def _engine_error_handler(err: Exception) -> None:
        st.error(f"{t('error_tab_compute')}：{err}")
        st.exception(err)
    _engine_handled = _is_calculated and EXECUTION_REGISTRY.run_system(
        system_id=_selected_system or "",
        params=_birth_params,
        options=_engine_options,
        spinner_text=t(_spinner_key),
        st_module=st,
        on_error=_engine_error_handler,
    )

if not _engine_handled:
    # --- 七政四餘（中國） ---
    if _selected_system == "tab_chinese":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                _g = st.session_state["_calc_gender"]
                with st.spinner(t("spinner_chinese")):
                    chart = compute_chart(**_p, gender=_g)

                # 子 tabs for the Chinese chart
                _ch_tab_natal, _ch_tab_shensha, _ch_tab_dasha, _ch_tab_transit, _ch_tab_zhangguo, _ch_tab_elect, _ch_tab_financial, _ch_tab_mansion = st.tabs([
                    t("ch_subtab_natal"),
                    t("ch_subtab_shensha"),
                    t("ch_subtab_dasha"),
                    t("ch_subtab_transit"),
                    t("ch_subtab_zhangguo"),
                    t("ch_subtab_electional"),
                    t("ch_subtab_financial"),
                    t("ch_subtab_mansion"),
                ])

                with _ch_tab_natal:
                    # 計算流時盤 for overlay
                    _transit_now = compute_transit_now(timezone=input_tz)

                    # 選擇是否顯示流時對盤
                    _show_transit_overlay = st.checkbox(
                        t("show_transit_overlay"), value=False,
                    )
                    _transit_for_ring = _transit_now if _show_transit_overlay else None

                    # Full chart: circle + info panel side by side
                    render_full_chart(chart, transit=_transit_for_ring)
                    _render_ai_button("tab_chinese", chart, btn_key="chinese")
                    st.divider()
                    render_chart_info(chart)
                    st.divider()
                    render_bazi(chart)
                    st.divider()
                    render_planet_table(chart)
                    st.divider()
                    render_house_table(chart)
                    st.divider()
                    render_aspect_summary(chart)
                    st.divider()
                    render_ming_gong_interpretations(chart)

                with _ch_tab_shensha:
                    _shensha = compute_shensha(
                        year=chart.year,
                        solar_month=chart.solar_month,
                        julian_day=chart.julian_day,
                        hour_branch=chart.hour_branch,
                        timezone=chart.timezone,
                        ming_gong_branch=chart.ming_gong_branch,
                    )
                    render_shensha(chart, _shensha)

                with _ch_tab_dasha:
                    from datetime import datetime as _dt
                    _current_year = _dt.now().year
                    _dasha = compute_dasha(
                        birth_year=chart.year,
                        ming_gong_branch=chart.ming_gong_branch,
                        gender=_g,
                        houses=chart.houses,
                        current_year=_current_year,
                    )
                    render_dasha(chart, _dasha)
                    # Dasha interpretation
                    if _dasha.current_period_idx >= 0:
                        _cur_period = _dasha.periods[_dasha.current_period_idx]
                        _reading = get_qizheng_dasha_reading(_cur_period.lord, get_lang())
                        if _reading:
                            st.divider()
                            st.subheader(t("dasha_reading_header"))
                            st.info(f"**{_cur_period.lord}** — {_reading}")

                with _ch_tab_transit:
                    st.subheader(t("transit_header"))
                    _t_col1, _t_col2, _t_col3 = st.columns(3)
                    with _t_col1:
                        _t_date = st.date_input(
                            t("transit_date"),
                            value=datetime.now().date(),
                            key="transit_date_input",
                        )
                    with _t_col2:
                        _t_time = st.time_input(
                            t("transit_time"),
                            value=datetime.now().time(),
                            key="transit_time_input",
                        )
                    with _t_col3:
                        _t_tz = st.number_input(
                            t("transit_tz"),
                            value=input_tz,
                            format="%.1f",
                            min_value=-12.0, max_value=14.0, step=0.5,
                            key="transit_tz_input",
                        )

                    _transit_custom = compute_transit(
                        year=_t_date.year, month=_t_date.month, day=_t_date.day,
                        hour=_t_time.hour, minute=_t_time.minute,
                        timezone=_t_tz,
                    )
                    render_transit_comparison(chart, _transit_custom)

                with _ch_tab_zhangguo:
                    _zhangguo = compute_zhangguo(
                        planets=chart.planets,
                        houses=chart.houses,
                        gender=_g,
                    )
                    render_zhangguo(chart, _zhangguo)

                with _ch_tab_elect:
                    render_electional_tool(timezone=input_tz)

                with _ch_tab_financial:
                    render_financial_tab(
                        chart=chart,
                        params=_p,
                        input_tz=input_tz,
                    )

                with _ch_tab_mansion:
                    render_mansion_text_panel(chart)

            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_chinese"))

    # --- 紫微斗數 ---
    elif _selected_system == "tab_ziwei":
        # 越南 Tử Vi 模式切換
        _ziwei_col1, _ziwei_col2 = st.columns([3, 1])
        with _ziwei_col2:
            _vietnam_mode = st.toggle(
                "🇻🇳 越南 Tử Vi 模式",
                value=st.session_state.get("_ziwei_vietnam_mode", False),
                help="啟用越南 Tử Vi Đẩu Số 模式：以貓代兔、融入越南佛教與農耕文化詮釋",
                key="_ziwei_vietnam_toggle",
            )
            st.session_state["_ziwei_vietnam_mode"] = _vietnam_mode
        with _ziwei_col1:
            if _vietnam_mode:
                st.markdown(
                    '<span style="background:#DA251D;color:#FFCD00;'
                    'font-weight:bold;padding:4px 10px;border-radius:6px;font-size:13px">'
                    '🇻🇳 越南 Tử Vi Đẩu Số 模式已啟用</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span style="background:#1a1a2e;color:#c8a96e;'
                    'font-weight:bold;padding:4px 10px;border-radius:6px;font-size:13px">'
                    '🌟 中國紫微斗數模式</span>',
                    unsafe_allow_html=True,
                )
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                _gender = st.session_state.get("_calc_gender", "男")
                with st.spinner(t("spinner_ziwei")):
                    zw_chart = compute_ziwei_chart(**_p, gender=_gender, vietnam_mode=_vietnam_mode)
                render_ziwei_chart(zw_chart, after_chart_hook=lambda: _render_ai_button("tab_ziwei", zw_chart, btn_key="ziwei"))
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_ziwei"))

    # --- 策天十八飛星 ---
    elif _selected_system == "tab_cetian_ziwei":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                _gender = st.session_state.get("_calc_gender", "男")
                with st.spinner(t("spinner_cetian_ziwei")):
                    ct_chart = compute_cetian_ziwei_chart(**_p, gender=_gender)
                render_cetian_ziwei_chart(ct_chart, after_chart_hook=lambda: _render_ai_button("tab_cetian_ziwei", ct_chart, btn_key="cetian_ziwei"))
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_cetian_ziwei"))

    # --- 西洋占星 ---
    elif _selected_system == "tab_western":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                sidereal_mode = st.checkbox(
                    t("sidereal_label"),
                    value=False,
                    help=t("sidereal_help"),
                )
                with st.spinner(t("spinner_western")):
                    w_params = dict(**_p, sidereal=sidereal_mode)
                    w_chart = compute_western_chart(**w_params)

                _w_tab_natal, _w_tab_transit, _w_tab_return, _w_tab_synastry, _w_tab_dignity, _w_tab_harmonic, _w_tab_draconic, _w_tab_asteroids, _w_tab_stars, _w_tab_parans, _w_tab_heliacal, _w_tab_predictive = st.tabs([
                    t("western_subtab_natal"),
                    t("western_subtab_transit"),
                    t("western_subtab_return"),
                    t("western_subtab_synastry"),
                    t("western_subtab_dignity"),
                    t("western_subtab_harmonic"),
                    t("western_subtab_draconic"),
                    t("western_subtab_asteroids"),
                    t("western_subtab_fixed_stars"),
                    t("western_subtab_parans"),
                    t("western_subtab_heliacal"),
                    t("western_subtab_predictive"),
                ])

                with _w_tab_natal:
                    _w_gender = st.session_state.get("_calc_gender")
                    # Pre-compute natal summary so it can be included in AI analysis
                    _summary = generate_natal_summary(
                        w_chart.planets, w_chart.houses,
                        getattr(w_chart, 'asc_sign', ''),
                        lang=get_lang(),
                    )
                    render_western_chart(
                        w_chart,
                        after_chart_hook=lambda: _render_ai_button(
                            "tab_western", w_chart,
                            btn_key="western", page_content=_summary,
                        ),
                        gender=_w_gender,
                    )
                    # Natal summary
                    with st.expander(t("natal_summary_header"), expanded=True):
                        st.markdown(_summary)

                with _w_tab_transit:
                    st.subheader(t("western_subtab_transit"))
                    _wt_col1, _wt_col2 = st.columns(2)
                    with _wt_col1:
                        _wt_date = st.date_input(t("transit_target_date"),
                                                 value=datetime.now().date(),
                                                 key="wt_date")
                    with _wt_col2:
                        _wt_time = st.time_input("Time", value=datetime.now().time(),
                                                 key="wt_time")
                    w_transits = compute_western_transits(
                        w_chart, _wt_date.year, _wt_date.month, _wt_date.day,
                        _wt_time.hour, _wt_time.minute, input_tz,
                    )
                    if w_transits.aspects_to_natal:
                        st.dataframe([{"Transit": a.transit_planet, "Natal": a.natal_planet,
                                       "Aspect": a.aspect_name, "Orb": f"{a.orb:.1f}°",
                                       "Applying": "→" if a.is_applying else "←"}
                                      for a in w_transits.aspects_to_natal[:20]],
                                     width="stretch")
                        # Transit readings
                        st.subheader(t("transit_readings_header"))
                        _lang = get_lang()
                        for _ta in w_transits.aspects_to_natal[:5]:
                            _reading = _ta.interpretation_cn if _lang in ("zh", "zh_cn") else _ta.interpretation_en
                            _reading = auto_cn(_reading) if _reading else _reading
                            st.info(f"**{_ta.transit_planet} {_ta.aspect_symbol} {_ta.natal_planet}** (orb {_ta.orb}°)\n\n{_reading}")
                    else:
                        st.info("No transit aspects found.")

                with _w_tab_return:
                    st.subheader(t("western_subtab_return"))
                    _return_year = st.number_input(t("return_year_label"),
                                                   value=datetime.now().year,
                                                   min_value=1900, max_value=2100,
                                                   key="return_year")
                    sun_planet = next((p for p in w_chart.planets if p.name.startswith("Sun")), None)
                    if sun_planet:
                        sr = compute_solar_return(
                            sun_planet.longitude, _return_year,
                            input_lat, input_lon, input_tz, location_name,
                        )
                        st.success(f"Solar Return: **{sr.return_date}**")
                        render_western_chart(sr.return_chart)
                    else:
                        st.warning("Sun position not found in natal chart.")

                with _w_tab_synastry:
                    st.subheader(t("synastry_header"))
                    st.markdown(t("synastry_person_b"))
                    _s_col1, _s_col2, _s_col3 = st.columns(3)
                    with _s_col1:
                        _s_date = st.date_input("Date B", value=date(1990, 6, 15), key="syn_date")
                    with _s_col2:
                        _s_time = st.time_input("Time B", value=time(12, 0), key="syn_time")
                    with _s_col3:
                        _s_tz = st.number_input("TZ B", value=input_tz, key="syn_tz",
                                                min_value=-12.0, max_value=14.0, step=0.5)
                    if st.button("Calculate Synastry / 計算合盤", key="syn_btn"):
                        w_b = compute_western_chart(
                            year=_s_date.year, month=_s_date.month, day=_s_date.day,
                            hour=_s_time.hour, minute=_s_time.minute,
                            timezone=_s_tz, latitude=input_lat, longitude=input_lon,
                            location_name=location_name,
                        )
                        syn = compute_synastry(w_chart, w_b, "Person A", "Person B")
                        st.metric("Harmony Score", f"{syn.harmony_summary:.3f}")
                        st.info(auto_cn(syn.summary_cn) if get_lang() in ("zh", "zh_cn") else syn.summary_en)
                        if syn.element_compatibility:
                            st.write(f"🔮 {syn.element_compatibility}")
                        if syn.inter_aspects:
                            st.dataframe([{"A": a.planet_a, "B": a.planet_b,
                                           "Aspect": a.aspect_name, "Orb": f"{a.orb:.1f}°",
                                           "Score": f"{a.harmony_score:+.3f}"}
                                          for a in syn.inter_aspects[:20]],
                                         width="stretch")
                            # Synastry readings (top 5)
                            st.subheader(t("synastry_readings_header"))
                            _lang = get_lang()
                            for _sa in syn.inter_aspects[:5]:
                                _reading = _sa.interpretation_cn if _lang in ("zh", "zh_cn") else _sa.interpretation_en
                                _reading = auto_cn(_reading) if _reading else _reading
                                st.info(f"**{_sa.planet_a} {_sa.aspect_symbol} {_sa.planet_b}** (orb {_sa.orb}°)\n\n{_reading}")

                with _w_tab_dignity:
                    st.subheader(t("western_subtab_dignity"))
                    _calc = PtolemyDignityCalculator()
                    _PLANET_MAP = {"Sun": PtolPlanet.SUN, "Moon": PtolPlanet.MOON, "Mercury": PtolPlanet.MERCURY,
                                   "Venus": PtolPlanet.VENUS, "Mars": PtolPlanet.MARS, "Jupiter": PtolPlanet.JUPITER, "Saturn": PtolPlanet.SATURN}
                    _dignity_rows = []
                    for p in w_chart.planets:
                        _pname = p.name.split("(")[0].strip().split()[0]
                        _ptol = _PLANET_MAP.get(_pname)
                        if _ptol:
                            _sign = getattr(p, 'sign', '') or ''
                            _sign_key = _sign.split()[0] if _sign else ''
                            _degree = getattr(p, 'sign_degree', p.longitude % 30)
                            _digs = _calc.get_dignities(_ptol, _sign_key, _degree, is_day_chart=True)
                            _score = _calc.calculate_total_score(_digs)
                            _dignity_rows.append({
                                "Planet": f"{_pname} ({_ptol.value})",
                                "Sign": f"{_sign_key} ({SIGN_NAMES.get(_sign_key, '')})",
                                "Degree": f"{_degree:.2f}°",
                                "Dignities": dignity_to_chinese(_digs),
                                "Score": _score,
                            })
                    if _dignity_rows:
                        st.dataframe(_dignity_rows, width="stretch")
                    else:
                        st.info("No traditional planet dignity data available.")

                with _w_tab_harmonic:
                    render_harmonic_chart(w_chart, lang=get_lang())

                with _w_tab_draconic:
                    render_draconic_chart(w_chart, lang=get_lang())

                # ── Asteroids & Centaurs tab ──────────────────────────
                with _w_tab_asteroids:
                    st.markdown(t("asteroids_header"))
                    _use_adv_ast = st.session_state.get("_adv_asteroids", True)
                    if _use_adv_ast:
                        _helio = st.session_state.get("_adv_helio", False)
                        _grp_keys = st.session_state.get("_adv_ast_group_keys") or list(ASTEROID_GROUPS.keys())[:3]
                        with st.spinner("Calculating asteroid positions…"):

                            @st.cache_data(show_spinner=False)
                            def _cached_asteroids(jd, helio, groups_tuple):
                                return compute_asteroids(jd, heliocentric=helio,
                                                         include_groups=list(groups_tuple))

                            _asts = _cached_asteroids(
                                w_chart.julian_day, _helio, tuple(_grp_keys),
                            )
                        if _asts:
                            _ast_rows = []
                            for _a in _asts:
                                _ast_rows.append({
                                    t("adv_col_body"):    f"{_a.symbol} {_a.name} ({_a.name_cn})",
                                    t("adv_col_sign"):    _a.sign,
                                    t("adv_col_degree"):  f"{_a.sign_degree:.2f}°",
                                    t("adv_col_lat"):     f"{_a.latitude:.2f}°",
                                    t("adv_col_speed"):   f"{_a.speed:+.4f}°/d",
                                    t("adv_col_retro"):   "℞" if _a.retrograde else "",
                                    t("adv_col_meaning"): auto_cn(_a.meaning_cn),
                                })
                            st.dataframe(_ast_rows, width="stretch")

                            # Aspects with traditional planets
                            if st.session_state.get("_adv_ast_aspects", True):
                                _p_lons = {p.name: p.longitude for p in w_chart.planets}
                                _ast_aspects = get_asteroid_aspects(_asts, _p_lons)
                                if _ast_aspects:
                                    st.markdown("##### Asteroid Aspects / 小行星相位")
                                    st.dataframe([{
                                        t("adv_col_body"):   _aa.asteroid_name,
                                        "Aspect":            f"{_aa.aspect_symbol} {_aa.aspect_name}",
                                        "Planet":            _aa.planet_name,
                                        t("adv_col_orb"):    f"{_aa.orb:.2f}°",
                                    } for _aa in _ast_aspects[:30]], width="stretch")
                        else:
                            st.info(t("adv_no_results"))
                    else:
                        st.info("Enable 'Include Asteroids & Centaurs' in the sidebar.")

                # ── Fixed Stars tab ───────────────────────────────────
                with _w_tab_stars:
                    st.markdown(t("fixed_star_conjunctions_header"))
                    _use_adv_stars = st.session_state.get("_adv_fixed_stars", False)
                    if _use_adv_stars:
                        _star_limit = st.session_state.get("_adv_stars_count", 30)
                        if _star_limit == STAR_CATALOG_ALL:
                            _star_limit = None  # all

                        with st.spinner("Computing fixed star positions…"):

                            @st.cache_data(show_spinner=False)
                            def _cached_stars(jd, lim):
                                return compute_fixed_star_positions(jd, limit=lim)

                            _stars = _cached_stars(w_chart.julian_day, _star_limit)

                        _p_lons = {p.name: p.longitude for p in w_chart.planets}
                        _conjs = find_conjunctions(_stars, _p_lons)

                        st.markdown(f"**{len(_stars)}** stars computed · **{len(_conjs)}** conjunctions (orb ≤ 1.5°)")

                        if _conjs:
                            st.dataframe([{
                                t("adv_col_body"):         f"⭐ {c.star_name} ({c.star_cn})",
                                "Planet":                  c.planet_name,
                                t("adv_col_orb"):          f"{c.orb:.2f}°",
                                t("adv_col_nature"):       c.nature,
                                t("adv_col_meaning"):      auto_cn(c.meaning_cn),
                            } for c in _conjs], width="stretch")

                        with st.expander("All Stars / 全部恆星", expanded=False):
                            st.dataframe([{
                                t("adv_col_body"):          f"{s.name}",
                                t("adv_col_cn_name"):       s.cn_name,
                                t("adv_col_constellation"): s.constellation,
                                t("adv_col_sign"):          s.sign,
                                t("adv_col_degree"):        f"{s.sign_degree:.2f}°",
                                t("adv_col_lat"):           f"{s.latitude:.2f}°",
                                t("adv_col_magnitude"):     s.magnitude,
                                t("adv_col_nature"):        s.nature,
                                t("adv_col_meaning"):       auto_cn(s.meaning_cn),
                            } for s in _stars], width="stretch")
                    else:
                        st.info("Enable 'Include Fixed Stars' in the sidebar.")

                # ── Parans tab ────────────────────────────────────────
                with _w_tab_parans:
                    st.markdown("#### 🔱 " + t("western_subtab_parans"))
                    st.caption(t("adv_parans_tooltip"))
                    _use_parans = st.session_state.get("_adv_parans", False)
                    if _use_parans:
                        _star_limit_p = st.session_state.get("_adv_stars_count", 30)
                        if _star_limit_p == STAR_CATALOG_ALL:
                            _star_limit_p = None

                        with st.spinner("Calculating parans…"):

                            @st.cache_data(show_spinner=False)
                            def _cached_parans(jd, lat, lon, lim):
                                _s = compute_fixed_star_positions(jd, limit=lim)
                                return calculate_parans(jd, lat, lon, _s)

                            _parans = _cached_parans(
                                w_chart.julian_day,
                                getattr(w_chart, "latitude", 0.0),
                                getattr(w_chart, "longitude", 0.0),
                                _star_limit_p,
                            )

                        if _parans:
                            st.dataframe([{
                                "Star / 恆星":           f"⭐ {p.star_name} ({p.star_cn})",
                                t("adv_col_star_event"): p.star_event_cn,
                                "Planet / 行星":         p.planet_name,
                                t("adv_col_planet_event"): p.planet_event_cn,
                                t("adv_col_orb"):        f"{p.orb:.2f}°",
                                t("adv_col_nature"):     p.star_nature,
                                t("adv_col_meaning"):    auto_cn(p.star_meaning_cn),
                            } for p in _parans[:50]], width="stretch")
                        else:
                            st.info(t("adv_no_results"))
                    else:
                        st.info("Enable 'Show Parans' in the sidebar.")

                # ── Heliacal tab ──────────────────────────────────────
                with _w_tab_heliacal:
                    st.markdown("#### 🌅 " + t("western_subtab_heliacal"))
                    st.caption(t("adv_heliacal_tooltip"))
                    _use_heliacal = st.session_state.get("_adv_heliacal", False)
                    if _use_heliacal:
                        _star_limit_h = st.session_state.get("_adv_stars_count", 30)
                        _heliacal_star_cap = 30  # heliacal_ut is computationally expensive
                        if _star_limit_h == STAR_CATALOG_ALL or _star_limit_h > _heliacal_star_cap:
                            _star_limit_h = _heliacal_star_cap
                            st.caption(
                                "ℹ️ Heliacal star search capped at 30 stars for performance. "
                                "/ 偕日升沒恆星計算限於30顆以確保效能。"
                            )

                        with st.spinner("Calculating heliacal phenomena…"):
                            try:
                                @st.cache_data(show_spinner=False)
                                def _cached_heliacal(jd, lat, lon, alt, lim):
                                    _s = compute_fixed_star_positions(jd, limit=lim)
                                    return calculate_heliacal(jd, lat, lon, alt, _s)

                                _hels = _cached_heliacal(
                                    w_chart.julian_day,
                                    getattr(w_chart, "latitude", 0.0),
                                    getattr(w_chart, "longitude", 0.0),
                                    0.0,
                                    _star_limit_h,
                                )
                            except Exception as _he:
                                _hels = []
                                st.warning(t("adv_heliacal_unavail"))
                                st.caption(str(_he))

                        if _hels:
                            st.dataframe([{
                                t("adv_col_body"):       f"{'⭐' if h.is_star else '🪐'} {h.body_name} ({h.body_cn})",
                                t("adv_col_event_type"): auto_cn(h.event_name_cn),
                                t("adv_col_event_date"): h.event_date,
                            } for h in _hels[:50]], width="stretch")
                        else:
                            st.info(t("adv_no_results"))
                    else:
                        st.info("Enable 'Show Heliacal Phenomena' in the sidebar.")

                # ── Predictive Suite tab ──────────────────────────────────
                with _w_tab_predictive:
                    try:
                        def _w_predictive_ai_callback(prompt_text: str):
                            """將預測技術 AI 提示傳給現有 AI 分析框架"""
                            _render_ai_button(
                                "tab_western", w_chart,
                                btn_key="western_predictive",
                                page_content=prompt_text,
                            )
                        render_predictive_suite(
                            w_chart,
                            lang=get_lang(),
                            ai_callback=_w_predictive_ai_callback,
                        )
                    except Exception as _pred_e:
                        st.error(f"預測技術計算錯誤 / Predictive error: {_pred_e}")
                        st.exception(_pred_e)

            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_western"))

    # --- 薩比恩符號 ---
    elif _selected_system == "tab_sabian":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                sidereal_mode = st.checkbox(
                    t("sidereal_label"),
                    value=False,
                    help=t("sidereal_help"),
                )
                with st.spinner(t("spinner_western")):
                    w_params = dict(**_p, sidereal=sidereal_mode)
                    w_chart = compute_western_chart(**w_params)
                
                st.header(t("sabian_system_label"))
                st.caption(t("sabian_symbols_help"))
                
                try:
                    from astro.sabian import get_sabian_for_planet, render_sabian_svg, load_sabian_symbols
                    
                    # Major planets list
                    _sabian_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                                       "Jupiter", "Saturn", "Ascendant", "Midheaven"]
                    
                    # Pass full chart data including ascendant and midheaven
                    _chart_data = {
                        "planets": w_chart.planets,
                        "ascendant": w_chart.ascendant,
                        "midheaven": w_chart.midheaven,
                    }
                    
                    # Pre-fetch all Sabian data
                    _sabian_lang = st.session_state.get("lang", "zh")
                    _sabian_data_list = []
                    for _pname in _sabian_planets:
                        try:
                            _sabian = get_sabian_for_planet(_chart_data, _pname)
                            if _sabian:
                                _sabian_data_list.append((_pname, _sabian))
                        except Exception:
                            pass

                    # Build a horizontal-scroll card strip at the top
                    _planet_glyphs = {
                        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
                        "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
                        "Ascendant": "AC", "Midheaven": "MC",
                    }
                    _cards_html = ""
                    for _pname, _sabian in _sabian_data_list:
                        _svg = render_sabian_svg(
                            _sabian['planet_longitude'],
                            size=220,
                            language=_sabian_lang,
                        )
                        _glyph = _planet_glyphs.get(_pname, _pname[:2])
                        _cards_html += f"""
                        <div style="
                            display:inline-block;
                            vertical-align:top;
                            width:220px;
                            margin-right:12px;
                            flex-shrink:0;
                        ">
                            <div style="text-align:center;font-size:11px;font-weight:600;
                                        margin-bottom:4px;opacity:0.7;">{_glyph} {_pname}</div>
                            {_svg}
                        </div>"""

                    _scroll_component = f"""
                    <div style="
                        overflow-x: auto;
                        -webkit-overflow-scrolling: touch;
                        white-space: nowrap;
                        padding: 8px 4px 12px 4px;
                        scroll-snap-type: x mandatory;
                    ">
                        {_cards_html}
                    </div>
                    <p style="text-align:center;font-size:10px;opacity:0.5;margin-top:2px;">
                        {t('sabian_scroll_hint')}
                    </p>
                    """
                    _render_interactive_html(
                        html=_scroll_component,
                        height=360,
                        key="sabian-scroll-strip",
                    )

                    st.divider()

                    # Detail section: use tabs for each planet (compact vertical space)
                    _tab_labels = [f"{_planet_glyphs.get(n, '')} {n}" for n, _ in _sabian_data_list]
                    _tabs = st.tabs(_tab_labels)
                    for _idx, (_tab, (_pname, _sabian)) in enumerate(zip(_tabs, _sabian_data_list)):
                        with _tab:
                            _svg = render_sabian_svg(
                                _sabian['planet_longitude'],
                                size=300,
                                language=_sabian_lang,
                            )
                            _render_interactive_html(
                                html=f'<div style="width:100%;max-width:320px;margin:0 auto">{_svg}</div>',
                                height=380,
                                key=f"sabian-detail-{_idx}",
                            )
                            st.markdown(f"*{t('sabian_formula_label')}:* {_sabian['formula']}")
                            st.markdown(f"*{t('sabian_positive_label')}:* {_sabian['positive']}")
                            st.markdown(f"*{t('sabian_negative_label')}:* {_sabian['negative']}")
                            st.markdown(f"*{t('sabian_interpretation_label')}:* {_sabian['interpretation']}")
                    
                    # Optional: Show all 360 symbols in an expander
                    with st.expander(t("sabian_show_all")):
                        st.caption("360 Sabian Symbols (Marc Edmund Jones, 1953)")
                        _all_symbols = load_sabian_symbols()
                        for _sym in _all_symbols[:360]:
                            st.markdown(f"**{_sym['degree']}° {_sym['sign']}:** {_sym['symbol']}")
                            
                except ImportError as _ie:
                    st.error("Sabian Symbols module not available.")
                    st.exception(_ie)
                except Exception as _se:
                    st.error(f"Error loading Sabian Symbols: {_se}")
                    st.exception(_se)
                    
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_sabian") if hasattr(t, "desc_sabian") else "🔮 薩比恩符號：Marc Edmund Jones (1953) 原著的 360 個象徵圖像，每個黃道度數對應一個獨特的心理原型。")

    # --- 波斯薩珊占星 ---
    elif _selected_system == "tab_persian":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_persian")):
                    from astro.persian import compute_sassanian_chart
                    
                    p_chart = compute_sassanian_chart(
                        year=_p["year"], month=_p["month"], day=_p["day"],
                        hour=_p["hour"], minute=_p["minute"],
                        latitude=_p.get("lat", 0.0), longitude=_p.get("lon", 0.0),
                        timezone=_p.get("tz", 0.0),
                        language=get_lang()
                    )
                
                # 波斯傳統占星 - 直接顯示星盤圖案（緊湊佈局）
                
                # 薩珊傳統星盤圖（方形格式，純 SVG）
                try:
                    from astro.persian.sassanian_chart_renderer import generate_sassanian_svg
                    
                    chart_data = {
                        "year": _p["year"], "month": _p["month"], "day": _p["day"],
                        "hour": _p["hour"], "minute": _p["minute"],
                        "longitude": _p.get("lon", 0.0),
                        "latitude": _p.get("lat", 0.0),
                        "timezone": _p.get("tz", 0.0),
                    }
                    
                    # 生成 SVG 並直接顯示（響應式設計，PC/手機皆 100% 顯示）
                    svg_content = generate_sassanian_svg(
                        chart_data=chart_data,
                        width=500,
                        height=650,
                        show_pahlavi=False,
                        show_royal_stars=True,
                        show_firdar=True,
                    )
                    
                    # 使用 st.components.v1.html 顯示 SVG（響應式高度）
                    # viewBox 500x650，使用 width: 100% 確保 PC/手機皆完整顯示
                    _render_interactive_html(
                        html=f'''<div style="width: 100%; max-width: 600px; margin: 0 auto;">
                            {svg_content}
                        </div>''',
                        height=720,
                        key="sassanian-main-svg",
                    )
                    
                except Exception as e:
                    st.error(f"星盤渲染失敗：{str(e)}")
                
                # Basic chart info（緊貼星盤下方）
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**{t('persian_current_firdar')}:** {p_chart.current_firdar.lord} ({p_chart.current_firdar.lord_cn})" if p_chart.current_firdar else "當前 Firdar: N/A")
                with col2:
                    st.info(f"**{t('persian_current_sub')}:** {p_chart.current_sub_period.lord} ({p_chart.current_sub_period.lord_cn})" if p_chart.current_sub_period else "當前子週期：N/A")
                
                # Main tabs for Persian astrology
                _p_tab_intro, _p_tab_firdar, _p_tab_hyleg, _p_tab_profections, _p_tab_almuten, _p_tab_stars, _p_tab_lots = st.tabs([
                    t("western_subtab_natal"),
                    t("persian_firdar_title"),
                    t("persian_hyleg_title"),
                    t("persian_profections_title"),
                    t("persian_almuten_title"),
                    t("persian_royal_stars_title"),
                    t("persian_lots_title"),
                ])
                
                with _p_tab_intro:
                    st.header(t("tab_persian"))
                    st.caption(t("desc_persian"))
                    
                    # Planet positions table
                    st.subheader("行星位置")
                    planet_data = []
                    for planet in p_chart.planets:
                        planet_data.append({
                            "行星": f"{planet.name} ({planet.name_cn})",
                            "經度": f"{planet.longitude:.2f}°",
                            "星座": f"{planet.sign_cn} {planet.sign_degree:.1f}°",
                            "宮位": f"第{planet.house}宮",
                            "尊嚴": planet.essential_dignity,
                            "逆行": "✓" if planet.retrograde else "",
                        })
                    st.dataframe(planet_data, width="stretch")
                    
                    # AI Analysis button
                    _render_ai_button("tab_persian", p_chart, btn_key="persian")
                
                with _p_tab_firdar:
                    st.header(t("persian_firdar_title"))
                    st.caption(t("persian_firdar_help"))
                    
                    # Timeline visualization
                    st.subheader("Firdar 生命週期時間軸")
                    
                    for i, firdar_period in enumerate(p_chart.firdar):
                        is_current = (p_chart.current_firdar and firdar_period.lord == p_chart.current_firdar.lord)
                        expander_label = f"**{i+1}. {firdar_period.lord} ({firdar_period.lord_cn})** — {firdar_period.start_date} 至 {firdar_period.end_date} ({firdar_period.duration_years:.1f}年)"
                        if is_current:
                            expander_label = f"🔮 {expander_label} **(當前)**"
                        
                        with st.expander(expander_label, expanded=is_current):
                            # Sub-periods table
                            sub_data = []
                            for sp in firdar_period.sub_periods:
                                is_current_sub = (p_chart.current_sub_period and sp.lord == p_chart.current_sub_period.lord and sp.start_date == p_chart.current_sub_period.start_date)
                                sub_data.append({
                                    "子週期": f"{'🔮 ' if is_current_sub else ''}{sp.lord} ({sp.lord_cn})",
                                    "起始": sp.start_date,
                                    "結束": sp.end_date,
                                    "年數": f"{sp.duration_years:.2f}",
                                })
                            st.dataframe(sub_data, width="stretch")
                
                with _p_tab_hyleg:
                    st.header(t("persian_hyleg_title"))
                    st.caption(t("persian_hyleg_help"))
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader(t("persian_hyleg_label"))
                        if p_chart.hyleg:
                            st.info(f"**類型:** {p_chart.hyleg.hyleg_type} ({p_chart.hyleg.hyleg_name_cn})\\n\\n"
                                   f"**位置:** {p_chart.hyleg.sign} {p_chart.hyleg.degree:.1f}°\\n\\n"
                                   f"**宮位:** 第{p_chart.hyleg.house}宮\\n\\n"
                                   f"**原因:** {p_chart.hyleg.reason}")
                        else:
                            st.warning("無法計算 Hyleg")
                    
                    with col2:
                        st.subheader(t("persian_alcocoden_label"))
                        if p_chart.alcocoden:
                            st.info(f"**守護星:** {p_chart.alcocoden.alcocoden_lord} ({p_chart.alcocoden.alcocoden_lord_cn})\\n\\n"
                                   f"**{t('persian_planetary_years')}:** {p_chart.alcocoden.planetary_years}年\\n\\n"
                                   f"**{t('persian_modified_years')}:** {p_chart.alcocoden.modified_years:.1f}年\\n\\n"
                                   f"**{t('persian_aspects')}:** {', '.join(p_chart.alcocoden.aspects) if p_chart.alcocoden.aspects else '無'}\\n\\n"
                                   f"**說明:** {p_chart.alcocoden.reason}")
                        else:
                            st.warning("無法計算 Alcocoden")
                
                with _p_tab_profections:
                    st.header(t("persian_profections_title"))
                    st.caption("波斯式年度主限：每年移動 30°，從上升點開始連續計算。")
                    
                    # Show first 30 years
                    prof_data = []
                    for prof in p_chart.profections[:30]:
                        prof_data.append({
                            "年齡": prof.age,
                            "主限星座": f"{prof.profection_sign_cn} {prof.profection_degree:.1f}°",
                            "年度守護星": f"{prof.lord_of_year} ({prof.lord_of_year_cn})",
                            "起始": prof.start_date,
                            "結束": prof.end_date,
                        })
                    st.dataframe(prof_data, width="stretch")
                
                with _p_tab_almuten:
                    st.header(t("persian_almuten_title"))
                    st.caption("Almuten Figuris 是根據薩珊尊嚴規則計算的最強行星，代表命主星。")
                    
                    if p_chart.almuten_figuris:
                        st.info(f"**最強行星:** {p_chart.almuten_figuris.planet} ({p_chart.almuten_figuris.planet_cn})\\n\\n"
                               f"**{t('persian_dignity_score')}:** {p_chart.almuten_figuris.total_score}\\n\\n"
                               f"**說明:** {p_chart.almuten_figuris.reason}")
                        
                        # Dignity breakdown
                        if p_chart.almuten_figuris.dignity_scores:
                            st.subheader("尊嚴分數細項")
                            score_data = []
                            for key, score in p_chart.almuten_figuris.dignity_scores.items():
                                score_data.append({"關鍵點": key, "分數": score})
                            st.dataframe(score_data, width="stretch")
                    else:
                        st.warning("無法計算 Almuten Figuris")
                
                with _p_tab_stars:
                    st.header(t("persian_royal_stars_title"))
                    st.caption("四顆皇家恆星是波斯傳統的重要恆星，與行星合相時具有特殊意義。")
                    
                    prominent_stars = [rs for rs in p_chart.royal_stars if rs.is_prominent]
                    
                    if prominent_stars:
                        st.success(f"找到 {len(prominent_stars)} 顆顯著的皇家恆星：")
                        for rs in prominent_stars:
                            st.info(f"**{rs.star_name} ({rs.star_name_cn})**\\n\\n"
                                   f"**合相行星:** {rs.conjunction_planet} ({rs.conjunction_planet_cn})\\n\\n"
                                   f"**容許度:** {rs.orb}°\\n\\n"
                                   f"**意義:** {rs.meaning_cn}")
                    else:
                        st.info(t("persian_no_prominent_stars"))
                    
                    # Show all royal stars
                    st.subheader("所有皇家恆星")
                    star_data = []
                    for rs in p_chart.royal_stars:
                        star_data.append({
                            "恆星": f"{rs.star_name} ({rs.star_name_cn})",
                            "經度": f"{rs.star_longitude:.1f}°",
                            "合相": f"{rs.conjunction_planet} ({rs.conjunction_planet_cn})" if rs.conjunction_planet else "無",
                            "容許度": f"{rs.orb}°" if rs.orb > 0 else "—",
                            "顯著": "✓" if rs.is_prominent else "",
                        })
                    st.dataframe(star_data, width="stretch")
                
                with _p_tab_lots:
                    st.header(t("persian_lots_title"))
                    st.caption("波斯敏感點（Lots）是根據上升點、太陽、月亮計算的敏感點位。")
                    
                    lots_data = []
                    for lot in p_chart.persian_lots:
                        lots_data.append({
                            "名稱": f"{lot.name_en}\\n({lot.name_cn})",
                            "阿拉伯名": lot.name_arabic,
                            "經度": f"{lot.longitude:.2f}°",
                            "星座": f"{lot.sign_cn} {lot.degree:.1f}°",
                            "宮位": f"第{lot.house}宮",
                        })
                    st.dataframe(lots_data, width="stretch")
                    
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_persian"))

    # --- 薩珊波斯 進階版 Advanced Sassanian Persian Astrology ---
    elif _selected_system == "tab_persian_deep":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_persian_deep")):
                    render_deep_sassanian_chart(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p.get("minute", 0),
                        timezone=_p.get("tz", 0.0),
                        latitude=_p.get("lat", 0.0),
                        longitude=_p.get("lon", 0.0),
                        location_name=_p.get("location_name", ""),
                    )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_persian_deep_prompt"))
            st.markdown(t("desc_persian_deep"))

    # --- KP Astrology (Krishnamurti Paddhati) ---
    elif _selected_system == "tab_kp":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_kp") if hasattr(t, "spinner_kp") else "計算 KP 星盤..."):
                    from astro.kp import compute_kp_chart, render_kp_chart
                    
                    kp_chart = compute_kp_chart(
                        year=_p["year"], month=_p["month"], day=_p["day"],
                        hour=_p["hour"], minute=_p["minute"],
                        latitude=_p.get("lat", 0.0), longitude=_p.get("lon", 0.0),
                        timezone=_p.get("tz", 0.0),
                        language=get_lang()
                    )
                
                # KP Astrology main layout
                st.header(t("kp_title"))
                st.caption(t("kp_subtitle"))
                
                # KP vs Vedic note
                st.info(t("kp_placidus_note"))
                
                # Render KP chart (tables + SVG chart)
                render_kp_chart(kp_chart, language=get_lang())
                
                # AI Analysis button
                _render_ai_button("tab_kp", kp_chart, btn_key="kp")
                
            except ImportError as _ie:
                st.error("KP Astrology module not available.")
                st.exception(_ie)
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                import traceback
                st.code(traceback.format_exc())
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_kp") if hasattr(t, "desc_kp") else "🔮 **KP Astrology (Krishnamurti Paddhati)** — 印度現代占星大師 K.S. Krishnamurti 創立的精確預測系統，使用宿度主星 (Sub Lord) 和時辰主星 (Ruling Planets) 判斷事件發生時機。")

    # --- 鐵板神數 (Tie Ban Shen Shu) ---
    elif _selected_system == "tab_tieban":
        _tb_tab_main, _tb_tab_tiaowen, _tb_tab_kunji = st.tabs([
            auto_cn("🔮 命盤"), auto_cn("📚 完整條文庫"), auto_cn("🔑 坤集扣入法"),
        ])
        with _tb_tab_main:
            if _is_calculated:
                try:
                    _p = st.session_state["_calc_params"]
                    with st.spinner(t("spinner_tieban") if hasattr(t, "spinner_tieban") else "計算鐵板神數..."):
                        # 鐵板神數需要父母信息，此處為簡化示例
                        from astro.tieban import TieBanShenShu, TieBanBirthData, render_tieban_chart_svg
                        from astro.tieban.tieban_calculator import Ganzhi
                        
                        # 計算干支
                        tbss = TieBanShenShu()
                        ganzhi = tbss.calculate_ganzhi(
                            datetime(
                                _p["year"], _p["month"], _p["day"],
                                _p["hour"], _p["minute"]
                            )
                        )
                        
                        # 創建出生資料（完整版需用戶輸入父母信息）
                        birth_data = TieBanBirthData(
                            birth_dt=datetime(_p["year"], _p["month"], _p["day"], _p["hour"], _p["minute"]),
                            year_gz=ganzhi['year'],
                            month_gz=ganzhi['month'],
                            day_gz=ganzhi['day'],
                            hour_gz=ganzhi['hour'],
                            gender=st.session_state.get("_calc_gender", "男"),
                        )
                        
                        # 計算
                        tb_result = tbss.calculate(birth_data)
                    
                    # ── 鐵板神數主界面（先圖後字，手機優先）──────────────
                    # ① 圖：SVG 星盤（響應式，已用 components.v1.html 渲染）
                    svg_chart = render_tieban_chart_svg(tb_result, language=get_lang())
                    _render_interactive_html(
                        html=svg_chart,
                        height=760,
                        key="tieban-main-svg",
                    )

                    # ② 核心數字卡片（HTML，手機單列）
                    _tb_lang = get_lang()
                    _tb_num_label   = "神數號碼"   if _tb_lang != "en" else "Divine Number"
                    _tb_ke_label    = "刻"         if _tb_lang != "en" else "Ke"
                    _tb_fen_label   = "分"         if _tb_lang != "en" else "Fen"
                    _tb_helo_label  = "河洛數"     if _tb_lang != "en" else "He Luo"
                    _tb_ming_label  = "命宮"       if _tb_lang != "en" else "Life Palace"
                    _tb_shen_label  = "身宮"       if _tb_lang != "en" else "Body Palace"
                    _tb_wx_label    = "五行局"     if _tb_lang != "en" else "Element Cycle"
                    _tb_code_label  = "密碼"       if _tb_lang != "en" else "Secret Code"
                    st.markdown(f"""
        <div style="
            display:flex;flex-wrap:wrap;gap:8px;
            margin:0 0 16px 0;
        ">
          <div style="flex:1 1 140px;min-width:140px;
              background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.4);
              border-radius:12px;padding:12px 14px;text-align:center;">
            <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_num_label}</div>
            <div style="font-size:26px;font-weight:700;color:#FF6B35;letter-spacing:3px;">{tb_result.tieban_number}</div>
          </div>
          <div style="flex:1 1 80px;min-width:80px;
              background:rgba(255,217,61,0.08);border:1px solid rgba(255,217,61,0.25);
              border-radius:12px;padding:12px 14px;text-align:center;">
            <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_ke_label}</div>
            <div style="font-size:22px;font-weight:700;color:#FFD93D;">{tb_result.ke}</div>
          </div>
          <div style="flex:1 1 80px;min-width:80px;
              background:rgba(255,217,61,0.08);border:1px solid rgba(255,217,61,0.25);
              border-radius:12px;padding:12px 14px;text-align:center;">
            <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_fen_label}</div>
            <div style="font-size:22px;font-weight:700;color:#FFD93D;">{tb_result.fen}</div>
          </div>
          <div style="flex:1 1 80px;min-width:80px;
              background:rgba(107,203,119,0.08);border:1px solid rgba(107,203,119,0.25);
              border-radius:12px;padding:12px 14px;text-align:center;">
            <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_helo_label}</div>
            <div style="font-size:22px;font-weight:700;color:#6BCB77;">{tb_result.he_luo_number}</div>
          </div>
          <div style="flex:1 1 100px;min-width:100px;
              background:rgba(107,203,119,0.08);border:1px solid rgba(107,203,119,0.25);
              border-radius:12px;padding:12px 14px;text-align:center;">
            <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_ming_label}</div>
            <div style="font-size:18px;font-weight:700;color:#6BCB77;">{tb_result.ming_palace}</div>
          </div>
          <div style="flex:1 1 100px;min-width:100px;
              background:rgba(107,203,119,0.08);border:1px solid rgba(107,203,119,0.25);
              border-radius:12px;padding:12px 14px;text-align:center;">
            <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_shen_label}</div>
            <div style="font-size:18px;font-weight:700;color:#6BCB77;">{tb_result.shen_palace}</div>
          </div>
          <div style="flex:1 1 100px;min-width:100px;
              background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.25);
              border-radius:12px;padding:12px 14px;text-align:center;">
            <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_wx_label}</div>
            <div style="font-size:15px;font-weight:700;color:#C9A84C;">{tb_result.wuxing_ju}</div>
          </div>
          <div style="flex:1 1 100px;min-width:100px;
              background:rgba(233,69,96,0.08);border:1px solid rgba(233,69,96,0.25);
              border-radius:12px;padding:12px 14px;text-align:center;">
            <div style="font-size:11px;color:#9090b0;margin-bottom:4px;">{_tb_code_label}</div>
            <div style="font-size:15px;font-weight:700;color:#E94560;">{tb_result.secret_code}</div>
          </div>
        </div>""", unsafe_allow_html=True)

                    # ③ 字：坤集條文（tiaowen_full_12000.json 主條文）
                    st.divider()
                    _tb_kunji_title = auto_cn("🔑 坤集條文")
                    st.subheader(_tb_kunji_title)

                    # 坤集扣入法天干序列 + 條文編號
                    if tb_result.kunji_tiangan:
                        _tg_str = "　".join(tb_result.kunji_tiangan)
                        _tiaowen_num_label = auto_cn("坤集編號") + f" {tb_result.tiaowen_number}"
                        _ke_lbl = tb_result.ke_label or str(tb_result.ke)
                        st.markdown(
                            f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;">'
                            f'<span style="background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.35);'
                            f'border-radius:8px;padding:4px 10px;font-size:12px;color:#FF9966;">'
                            f'#{_tiaowen_num_label}</span>'
                            f'<span style="background:rgba(255,217,61,0.10);border:1px solid rgba(255,217,61,0.3);'
                            f'border-radius:8px;padding:4px 10px;font-size:12px;color:#FFD93D;">'
                            f'{auto_cn("扣入天干")}：{_tg_str}</span>'
                            f'<span style="background:rgba(107,203,119,0.10);border:1px solid rgba(107,203,119,0.25);'
                            f'border-radius:8px;padding:4px 10px;font-size:12px;color:#6BCB77;">'
                            f'{auto_cn("刻")}：{_ke_lbl}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                    # 坤集主條文（tiaowen_full_12000.json）
                    _tw = tb_result.tiaowen_data
                    if _tw and _tw.get("text"):
                        st.markdown(
                            f'<div style="background:rgba(255,107,53,0.08);border-left:4px solid #FF6B35;'
                            f'border-radius:0 12px 12px 0;padding:14px 18px;font-size:15px;'
                            f'color:#f0d9c8;line-height:1.9;letter-spacing:0.5px;">'
                            f'{_tw["text"]}</div>',
                            unsafe_allow_html=True,
                        )
                        if _tw.get("note") and _tw["note"].strip() not in ("", "0 0"):
                            st.caption(auto_cn(f"備注：{_tw['note']}"))
                    else:
                        # 如坤集無此條，退而顯示 verses.json 條文
                        st.info(tb_result.verse)

                    # 算盤打數條文（suanpan_tiaowen_full.json）
                    st.divider()
                    st.subheader(auto_cn("🧮 算盤打數條文"))
                    st.caption(auto_cn("曹展碩實務版 · 金鎖銀匙歌 · 算盤打數五部條文"))
                    from astro.tieban.suanpan_full_structure import (
                        suanpan_calculate,
                        SuanpanTiaowenDatabase,
                    )
                    _sp_calc = suanpan_calculate(
                        year_gz=str(ganzhi["year"]),
                        month_gz=str(ganzhi["month"]),
                        day_gz=str(ganzhi["day"]),
                        hour_gz=str(ganzhi["hour"]),
                        gender=st.session_state.get("_calc_gender", "男"),
                    )
                    _sp_db = SuanpanTiaowenDatabase()
                    _sp_tiaowen = _sp_db.get_by_result(_sp_calc)

                    # 基本定部資訊卡
                    _sp_nayin_label = auto_cn("納音")
                    _sp_dept_label  = auto_cn("五行部")
                    _sp_num_label   = auto_cn("算盤總數")
                    _sp_key_label   = auto_cn("條文鍵")
                    st.markdown(
                        f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;">'
                        f'<span style="background:rgba(107,203,119,0.10);border:1px solid rgba(107,203,119,0.3);'
                        f'border-radius:8px;padding:4px 10px;font-size:12px;color:#6BCB77;">'
                        f'{_sp_nayin_label}：{_sp_calc.nayin or "未知"}</span>'
                        f'<span style="background:rgba(107,203,119,0.10);border:1px solid rgba(107,203,119,0.3);'
                        f'border-radius:8px;padding:4px 10px;font-size:12px;color:#6BCB77;">'
                        f'{_sp_dept_label}：{_sp_calc.department or "未知"}部</span>'
                        f'<span style="background:rgba(255,217,61,0.10);border:1px solid rgba(255,217,61,0.3);'
                        f'border-radius:8px;padding:4px 10px;font-size:12px;color:#FFD93D;">'
                        f'{_sp_num_label}：{_sp_calc.total_number}</span>'
                        f'<span style="background:rgba(255,107,53,0.10);border:1px solid rgba(255,107,53,0.3);'
                        f'border-radius:8px;padding:4px 10px;font-size:12px;color:#FF9966;">'
                        f'{_sp_key_label}：{_sp_calc.tiaowen_key}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    # 算盤打數條文內文
                    if _sp_tiaowen and _sp_tiaowen.get("text"):
                        _sp_raw = _sp_tiaowen.get("raw_key", "")
                        _sp_raw_badge = (
                            f'<span style="font-size:11px;color:#9090b0;margin-left:8px;">'
                            f'（{_sp_raw}）</span>'
                        ) if _sp_raw else ""
                        st.markdown(
                            f'<div style="background:rgba(107,203,119,0.06);border-left:4px solid #6BCB77;'
                            f'border-radius:0 12px 12px 0;padding:14px 18px;font-size:15px;'
                            f'color:#d4f0d8;line-height:1.9;letter-spacing:0.5px;">'
                            f'{_sp_tiaowen["text"]}{_sp_raw_badge}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.info(auto_cn(f"（算盤打數條文鍵 {_sp_calc.tiaowen_key} 暫無資料）"))

                    # 歲運條文（流年歲運）
                    _sp_suiyun = _sp_db.get_suiyun_by_result(_sp_calc)
                    if _sp_suiyun and _sp_suiyun.get("text"):
                        st.markdown(f"**{auto_cn('🌀 歲運條文')}**")
                        _sp_sy_raw = _sp_suiyun.get("raw_key", "")
                        _sp_sy_raw_badge = (
                            f'<span style="font-size:11px;color:#9090b0;margin-left:8px;">'
                            f'（{_sp_sy_raw}）</span>'
                        ) if _sp_sy_raw else ""
                        st.markdown(
                            f'<div style="background:rgba(201,168,76,0.06);border-left:4px solid #C9A84C;'
                            f'border-radius:0 12px 12px 0;padding:14px 18px;font-size:15px;'
                            f'color:#f0e8c0;line-height:1.9;letter-spacing:0.5px;">'
                            f'{_sp_suiyun["text"]}{_sp_sy_raw_badge}</div>',
                            unsafe_allow_html=True,
                        )

                    # 計算步驟展開
                    with st.expander(auto_cn("查看算盤打數計算步驟"), expanded=False):
                        for _step in _sp_calc.calculation_steps:
                            st.markdown(f"- {_step}")

                    # 九十六刻表 & 六親刻分圖查詢結果
                    _bake = tb_result.bake_fuqin_info
                    _six = tb_result.six_qin_qizi_info
                    if _bake or _six:
                        st.divider()
                        st.markdown(f"**{auto_cn('⏰ 刻分六親')}**")
                        _kf_cards = ""
                        if _bake:
                            _kf_cards += (
                                f'<div style="border-left:3px solid rgba(255,217,61,0.5);'
                                f'padding:8px 12px;margin-bottom:8px;'
                                f'background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;">'
                                f'<div style="font-size:11px;color:#9090b0;margin-bottom:2px;">'
                                f'{auto_cn("父母兄弟（九十六刻）")}</div>'
                                f'<div style="font-size:13px;color:#FFD93D;">{_bake}</div></div>'
                            )
                        if _six:
                            _kf_cards += (
                                f'<div style="border-left:3px solid rgba(107,203,119,0.5);'
                                f'padding:8px 12px;margin-bottom:8px;'
                                f'background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;">'
                                f'<div style="font-size:11px;color:#9090b0;margin-bottom:2px;">'
                                f'{auto_cn("妻子（六親刻分）")}</div>'
                                f'<div style="font-size:13px;color:#6BCB77;">{_six}</div></div>'
                            )
                        st.markdown(f'<div style="width:100%;">{_kf_cards}</div>', unsafe_allow_html=True)

                    # 十二宮條文詳情
                    st.divider()
                    st.markdown("**🏛️ " + (t("tieban_palace_verses") if hasattr(t, "tieban_palace_verses") else auto_cn("十二宮條文")) + "**")

                    expander_label = t("tieban_view_palace_verses") if hasattr(t, "tieban_view_palace_verses") else auto_cn("查看十二宮詳細條文")
                    with st.expander(expander_label, expanded=False):
                        palace_order = ["命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
                                       "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮"]
                        palace_names_en = {
                            "命宮": "Life", "兄弟宮": "Siblings", "夫妻宮": "Spouse",
                            "子女宮": "Children", "財帛宮": "Wealth", "疾厄宮": "Health",
                            "遷移宮": "Travel", "交友宮": "Friends", "官祿宮": "Career",
                            "田宅宮": "Property", "福德宮": "Fortune", "父母宮": "Parents",
                        }
                        category_trans = {
                            "綜合": "General", "父母": "Parents", "兄弟": "Siblings",
                            "夫妻": "Spouse", "子女": "Children", "財運": "Wealth",
                            "事業": "Career", "健康": "Health", "災厄": "Disaster",
                            "遷移": "Travel",
                        }
                        # 手機友好：以 HTML 卡片列表代替三列
                        _palace_cards = ""
                        for palace_name in palace_order:
                            palace_info = tb_result.palace_verses.get(palace_name, {})
                            verse = palace_info.get("verse", t("no_verse") if hasattr(t, "no_verse") else auto_cn("暫無條文"))
                            category = palace_info.get("category", "")
                            branch = palace_info.get("branch", "")
                            display_name = palace_names_en.get(palace_name, palace_name) if get_lang() == "en" else palace_name
                            display_category = category_trans.get(category, category) if get_lang() == "en" else category
                            cat_badge = (
                                f'<span style="font-size:10px;color:#FF6B35;margin-left:6px;">'
                                f'【{display_category}】</span>'
                            ) if display_category else ""
                            _palace_cards += f"""
        <div style="border-left:3px solid rgba(255,107,53,0.5);
             padding:10px 12px;margin-bottom:10px;
             background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;">
          <div style="font-size:13px;font-weight:700;color:#FFD93D;margin-bottom:4px;">
            {display_name}
            <span style="font-size:11px;color:#9090b0;font-weight:400;margin-left:4px;">({branch})</span>
            {cat_badge}
          </div>
          <div style="font-size:13px;color:#c8c8e8;line-height:1.6;">{verse}</div>
        </div>"""
                        st.markdown(f'<div style="width:100%;">{_palace_cards}</div>', unsafe_allow_html=True)

                    # AI 分析按鈕
                    _render_ai_button("tab_tieban", {"result": tb_result}, btn_key="tieban")

                except Exception as _e:
                    st.error(f"{t('error_tab_compute')}：{_e}")
                    import traceback
                    st.code(traceback.format_exc())
            else:
                st.markdown("""
        <div style="
            background:linear-gradient(135deg,#1a0828 0%,#0f1e35 100%);
            border:1px solid rgba(255,107,53,0.35);
            border-radius:16px;
            padding:28px 24px 24px 24px;
            margin-bottom:20px;
            text-align:center;
        ">
          <div style="font-size:52px;margin-bottom:12px;">🔮</div>
          <div style="font-size:22px;font-weight:700;color:#FF6B35;letter-spacing:2px;margin-bottom:6px;">
            鐵板神數
          </div>
          <div style="font-size:12px;color:#9090b0;margin-bottom:14px;letter-spacing:1px;">
            Tie Ban Shen Shu &middot; Iron Plate Divine Numbers
          </div>
          <div style="font-size:13px;color:#8888aa;line-height:1.8;max-width:380px;margin:0 auto 18px auto;">
            源自宋代邵雍《皇極經世》，清代發展為精密考刻分系統<br>
            每時分 8 刻、每刻 15 分（共 120 分）<br>
            號稱「鐵口直斷」，中國傳統術數中最精密的查表法系統
          </div>
          <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-bottom:18px;">
            <div style="background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.35);
                 border-radius:8px;padding:7px 13px;font-size:12px;color:#FF9966;">
              📅 輸入出生年月日時
            </div>
            <div style="background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.35);
                 border-radius:8px;padding:7px 13px;font-size:12px;color:#FF9966;">
              ⚡ 一鍵推算神數
            </div>
            <div style="background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.35);
                 border-radius:8px;padding:7px 13px;font-size:12px;color:#FF9966;">
              📜 查閱十二宮條文
            </div>
          </div>
          <div style="
            display:inline-block;
            background:rgba(205,46,58,0.15);
            border:1px solid rgba(205,46,58,0.4);
            border-radius:8px;
            padding:8px 20px;
            font-size:13px;
            color:#f87171;
          ">👈 請在左側填寫出生年月日時，即可起盤</div>
        </div>""", unsafe_allow_html=True)

        with _tb_tab_tiaowen:
            from astro.tieban.tieban_browser import (
                render_tiaowen_full_browser_inline,
                render_suanpan_tiaowen_browser_inline,
            )
            _tiaowen_db_choice = st.radio(
                auto_cn("條文庫"),
                [auto_cn("📚 坤集扣入法（12000 條）"), auto_cn("🧮 算盤打數五部條文")],
                horizontal=True,
                label_visibility="collapsed",
                key="tb_tiaowen_db_choice",
            )
            st.divider()
            if _tiaowen_db_choice == auto_cn("📚 坤集扣入法（12000 條）"):
                render_tiaowen_full_browser_inline()
            else:
                render_suanpan_tiaowen_browser_inline()

        with _tb_tab_kunji:
            from astro.tieban.kunji_full_structure import (
                KUNJI_TIANGAN_CODE, BAKE_96_KE, SIX_QIN_KE_FEN,
                kou_ru_fa, advanced_kou_ru_fa,
            )
            st.subheader("🔑 坤集密碼表")
            st.caption("天干扣入法核心：各天干對應數字，用於萬千百十條文編號解碼")
            _code_rows = [{"天干": k, "密碼數": v} for k, v in KUNJI_TIANGAN_CODE.items()]
            st.dataframe(_code_rows, width="stretch", hide_index=True)

            st.divider()
            st.subheader("🔢 扣入法查詢")
            _kunji_num = st.number_input(
                "輸入條文編號（1001–13000）",
                min_value=1001, max_value=13000, value=1001, step=1,
                key="kunji_num_input",
            )
            if st.button("解碼天干序列", key="kunji_decode_btn"):
                _seq = kou_ru_fa(int(_kunji_num))
                st.success(f"條文 {int(_kunji_num)} → 扣入天干序列：{'  '.join(_seq)}")
                _adv = advanced_kou_ru_fa(int(_kunji_num))
                st.info(f"基礎天干：{'  '.join(_adv['base_tiangan'])}")

            st.divider()
            st.subheader("⏰ 九十六刻天干數表")
            st.caption("各時辰（父母兄弟 / 妻子）刻分對應坤集天干")
            _ke_hour = st.selectbox(
                "選擇時辰",
                options=list(BAKE_96_KE.keys()),
                key="kunji_ke_hour",
            )
            _ke_data = BAKE_96_KE.get(_ke_hour, {})
            for _rel, _kes in _ke_data.items():
                st.markdown(f"**{_rel}**")
                _ke_rows = [{"刻/分": k, "天干結果": v} for k, v in _kes.items()]
                st.dataframe(_ke_rows, width="stretch", hide_index=True)

            st.divider()
            st.subheader("👨\u200d👩\u200d👧 六親刻分圖")
            st.caption("各時辰六親（父母兄弟 / 妻子）刻分對應")
            _qin_hour = st.selectbox(
                "選擇時辰",
                options=list(SIX_QIN_KE_FEN.keys()),
                key="kunji_qin_hour",
            )
            _qin_data = SIX_QIN_KE_FEN.get(_qin_hour, {})
            for _rel, _fens in _qin_data.items():
                st.markdown(f"**{_rel}**")
                _qin_rows = [{"刻/分": k, "六親結果": v} for k, v in _fens.items()]
                st.dataframe(_qin_rows, width="stretch", hide_index=True)

    # --- 邵子神數 ---
    elif _selected_system == "tab_shaozi":
        _sz_tab_main, _sz_tab_64keys, _sz_tab_tiaowen = st.tabs([
            auto_cn("🔯 命盤"), auto_cn("🗝️ 64鑰匙"), auto_cn("📚 條文庫"),
        ])
        with _sz_tab_main:
            if _is_calculated:
                try:
                    from astro.shaozi import ShaoziShenShu, ShaoziBirthData
                    from astro.shaozi.renderer import render_shaozi_result

                    _p = st.session_state["_calc_params"]
                    with st.spinner(t("spinner_shaozi")):
                        _sz_engine = ShaoziShenShu()
                        _sz_birth = ShaoziBirthData(
                            birth_dt=datetime(
                                _p["year"], _p["month"], _p["day"],
                                _p["hour"], _p.get("minute", 0),
                            ),
                            gender=st.session_state.get("_calc_gender", "男"),
                        )
                        _sz_result = _sz_engine.calculate(_sz_birth)

                    render_shaozi_result(_sz_result)
                    _render_ai_button(
                        "tab_shaozi",
                        {
                            "tiaowen_id": _sz_result.tiaowen_id,
                            "gua": _sz_result.gua_name,
                            "tiaowen": _sz_result.tiaowen_text,
                            "year_gz": _sz_result.year_gz,
                            "day_gz": _sz_result.day_gz,
                        },
                        btn_key="shaozi",
                    )
                except Exception as _e:
                    st.error(f"{t('error_tab_compute')}：{_e}")
                    import traceback
                    st.code(traceback.format_exc())
            else:
                from astro.shaozi.renderer import render_shaozi_placeholder
                render_shaozi_placeholder()

        with _sz_tab_64keys:
            if _is_calculated:
                try:
                    from astro.shaozi import ShaoziShenShu as _SzMain, ShaoziBirthData
                    from astro.shaozi.shaozi_full_structure import ShaoziFullShenShu as _SzFull
                    from astro.shaozi.renderer import render_shaozi_64key_section

                    _p = st.session_state["_calc_params"]
                    with st.spinner(t("spinner_shaozi")):
                        # 取得四柱干支（復用主盤計算結果或重新推算）
                        _sz_main_engine = _SzMain()
                        _sz_birth = ShaoziBirthData(
                            birth_dt=datetime(
                                _p["year"], _p["month"], _p["day"],
                                _p["hour"], _p.get("minute", 0),
                            ),
                            gender=st.session_state.get("_calc_gender", "男"),
                        )
                        _sz_base = _sz_main_engine.calculate(_sz_birth)

                        # 使用 shaozi_full_structure 進行64鑰匙起盤
                        _sz_full_engine = _SzFull()
                        _sz_full_result = _sz_full_engine.cast_plate(
                            year_gz=_sz_base.year_gz,
                            month_gz=_sz_base.month_gz,
                            day_gz=_sz_base.day_gz,
                            hour_gz=_sz_base.hour_gz,
                        )

                    render_shaozi_64key_section(_sz_full_result)
                except Exception as _e:
                    st.error(f"{t('error_tab_compute')}：{_e}")
                    import traceback
                    st.code(traceback.format_exc())
            else:
                from astro.shaozi.renderer import render_shaozi_placeholder
                render_shaozi_placeholder()

        with _sz_tab_tiaowen:
            from astro.shaozi.renderer import render_shaozi_tiaowen_browser
            render_shaozi_tiaowen_browser()

    # --- 皇極經世 ---
    elif _selected_system == "tab_huangji":
        if _is_calculated:
            try:
                from astro.huangji import compute_huangji_pan, render_streamlit as render_huangji_chart

                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_huangji")):
                    _huangji_chart = compute_huangji_pan(
                        **_p,
                        reference_year=datetime.now().year,
                        include_cross_system=True,
                        gender=st.session_state.get("_calc_gender", "男"),
                    )
                render_huangji_chart(
                    _huangji_chart,
                    lang=get_lang(),
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_huangji",
                        _huangji_chart,
                        btn_key="huangji",
                    ),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_huangji"))

    # --- 太玄數占星 ---
    elif _selected_system == "tab_taixuan":
        # 子頁籤：本命排盤 / 即時問卜
        _tx_natal_label = t("taixuan_natal_tab")
        _tx_qigua_label = t("taixuan_qigua_tab")
        _tx_tab_natal, _tx_tab_qigua = st.tabs([_tx_natal_label, _tx_qigua_label])

        with _tx_tab_natal:
            if _is_calculated:
                try:
                    _p = st.session_state["_calc_params"]
                    with st.spinner(t("spinner_taixuan")):
                        _tx_calc = TaiXuanCalculator(
                            year=_p["year"],
                            month=_p["month"],
                            day=_p["day"],
                            hour=_p["hour"],
                            mode="natal",
                        )
                        _tx_result = _tx_calc.calculate()
                    render_taixuan_chart(
                        _tx_result,
                        after_chart_hook=lambda: _render_ai_button(
                            "tab_taixuan",
                            {
                                "shou_name": _tx_result.shou.name,
                                "gua_title": _tx_result.shou.gua_title,
                                "gua_text": _tx_result.shou.gua_text,
                                "zhan_name": _tx_result.shou.zhan_name,
                                "zhan_text": _tx_result.shou.zhan_text,
                                "year_gz": _tx_result.year_gz,
                                "day_gz": _tx_result.day_gz,
                                "sishi": _tx_result.sishi,
                                "mansion": _tx_result.shou.mansion,
                                "planet": _tx_result.shou.planet,
                            },
                            btn_key="taixuan_natal",
                        ),
                    )
                except Exception as _e:
                    st.error(f"{t('error_tab_compute')}：{_e}")
                    import traceback
                    st.code(traceback.format_exc())
            else:
                render_taixuan_intro()

        with _tx_tab_qigua:
            render_qigua_ui(
                after_chart_hook=lambda: _render_ai_button(
                    "tab_taixuan",
                    {"mode": "qigua"},
                    btn_key="taixuan_qigua",
                )
            )

    # --- 五運六氣 ---
    elif _selected_system == "tab_wuyunliuqi":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_wuyunliuqi")):
                    _wylq_result = compute_wuyunliuqi(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p.get("minute", 0),
                    )
                render_wuyunliuqi_chart(_wylq_result)
                _render_ai_button("tab_wuyunliuqi", {
                    "ganzhi": _wylq_result.ganzhi,
                    "dayun": _wylq_result.dayun.taishao,
                    "sitian": _wylq_result.sitian,
                    "zaiquan": _wylq_result.zaiquan,
                    "tonghua": _wylq_result.tonghua.categories,
                }, btn_key="wuyunliuqi")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                import traceback
                st.code(traceback.format_exc())
        else:
            render_wuyunliuqi_intro()
            st.markdown(t("desc_wuyunliuqi"))

    # --- History of Astrology ---
    elif _selected_system == "tab_history":
        st.header("📜 " + t("tab_history"))
        st.caption("占星術是人類最古老的知識體系之一，跨越五千年文明，連結天上與地下。" if _cur_lang in ("zh", "zh_cn") else "Astrology is one of humanity's oldest knowledge systems, spanning five millennia of civilization.")
        
        st.divider()
        
        # Load and render markdown file
        try:
            with open("docs/astrology_history.md", "r", encoding="utf-8") as f:
                history_md = f.read()
            st.markdown(history_md)
        except FileNotFoundError:
            st.error("占星歷史文件尚未建立 / Astrology history file not found: `docs/astrology_history.md`")
            st.info("請先建立文件 / Please create the document first.")
        
        _render_ai_button("tab_history", {"system": "astrology_history"}, btn_key="history")

    # --- Astrology Wiki ---
    elif _selected_system == "tab_wiki":
        render_wiki(lang=_cur_lang)

    # --- 印度占星 ---
    elif _selected_system == "tab_indian":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_indian")):
                    v_chart = compute_vedic_chart(**_p)

                _v_tab_rashi, _v_tab_dasha, _v_tab_ashtaka, _v_tab_yogas, _v_tab_bphs, _v_tab_varga, _v_tab_financial = st.tabs([
                    t("vedic_subtab_rashi"),
                    t("vedic_subtab_dasha"),
                    t("vedic_subtab_ashtaka"),
                    t("vedic_subtab_yogas"),
                    t("vedic_subtab_bphs"),
                    t("vedic_subtab_varga"),
                    t("vedic_subtab_financial"),
                ])

                with _v_tab_rashi:
                    render_vedic_chart(v_chart, after_chart_hook=lambda: _render_ai_button("tab_indian", v_chart, btn_key="vedic"))

                with _v_tab_dasha:
                    st.subheader(t("vedic_subtab_dasha"))
                    moon_p = next((p for p in v_chart.planets if "Chandra" in p.name or "Moon" in p.name), None)
                    if moon_p:
                        vim = compute_vimshottari(moon_p.longitude, v_chart.julian_day)
                        st.info(f"Moon Nakshatra: **{vim.moon_nakshatra}** | Lord: **{vim.moon_nakshatra_lord}** | Balance: {vim.balance_years:.2f} yrs")
                        for md in vim.mahadasha_periods:
                            _dasha_reading = get_dasha_reading(md.lord, get_lang())
                            with st.expander(f"**{md.lord}** ({md.lord_cn}) — {md.start_date} to {md.end_date} ({md.years:.1f} yrs)"):
                                if _dasha_reading:
                                    st.markdown(f"📖 {_dasha_reading}")
                                if md.sub_periods:
                                    st.dataframe([{"Lord": s.lord, "CN": s.lord_cn,
                                                  "Start": s.start_date, "End": s.end_date,
                                                  "Years": f"{s.years:.2f}"}
                                                 for s in md.sub_periods],
                                                 width="stretch")
                        st.divider()
                        st.markdown("##### Yogini Dasha (36-year cycle)")
                        yog = compute_yogini(moon_p.longitude, v_chart.julian_day)
                        st.dataframe([{"Yogini": p.lord, "CN": p.lord_cn,
                                      "Start": p.start_date, "End": p.end_date,
                                      "Years": f"{p.years:.2f}"}
                                     for p in yog.periods], width="stretch")
                        # Yogini reading for current period
                        if yog.periods:
                            _yog_reading = get_yogini_reading(yog.periods[0].lord, get_lang())
                            if _yog_reading:
                                st.info(f"📖 Current: {_yog_reading}")
                    else:
                        st.warning("Moon position not found.")
                    _render_ai_button("tab_indian", v_chart, btn_key="vedic_dasha")

                with _v_tab_ashtaka:
                    st.subheader(t("vedic_subtab_ashtaka"))
                    p_lons = {}
                    for p in v_chart.planets:
                        key = p.name.split("(")[0].strip().split()[0]
                        _MAP = {"Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars",
                                "Budha": "Mercury", "Guru": "Jupiter", "Shukra": "Venus", "Shani": "Saturn"}
                        canonical = _MAP.get(key, key)
                        p_lons[canonical] = p.longitude
                    asc_lon = getattr(v_chart, 'ascendant', 0.0) if hasattr(v_chart, 'ascendant') else 0.0
                    if len(p_lons) >= 7:
                        av = compute_ashtakavarga(p_lons, asc_lon)
                        st.info(f"Sarvashtakavarga Total: **{av.sarva_total}**")
                        import pandas as pd
                        signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                                 "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
                        rows = []
                        for bav in av.bav:
                            row = {"Planet": f"{bav.planet} ({bav.planet_cn})"}
                            for i, s in enumerate(signs):
                                row[s] = bav.bindus[i]
                            row["Total"] = bav.total
                            rows.append(row)
                        sarva_row = {"Planet": "SARVA"}
                        for i, s in enumerate(signs):
                            sarva_row[s] = av.sarva[i]
                        sarva_row["Total"] = av.sarva_total
                        rows.append(sarva_row)
                        st.dataframe(pd.DataFrame(rows), width="stretch")
                    else:
                        st.warning("Insufficient planet data for Ashtakavarga.")
                    _render_ai_button("tab_indian", v_chart, btn_key="vedic_ashtaka")

                with _v_tab_yogas:
                    st.subheader(t("vedic_subtab_yogas"))
                    p_lons_y = {}
                    for p in v_chart.planets:
                        key = p.name.split("(")[0].strip().split()[0]
                        _MAP2 = {"Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars",
                                 "Budha": "Mercury", "Guru": "Jupiter", "Shukra": "Venus",
                                 "Shani": "Saturn", "Rahu": "Rahu", "Ketu": "Ketu"}
                        canonical = _MAP2.get(key, key)
                        p_lons_y[canonical] = p.longitude
                    asc_lon_y = getattr(v_chart, 'ascendant', 0.0) if hasattr(v_chart, 'ascendant') else 0.0
                    yogas = compute_yogas(p_lons_y, asc_lon_y)
                    for yg in yogas:
                        icon = "✅" if yg.is_present else "⬜"
                        with st.expander(f"{icon} {yg.name} ({auto_cn(yg.name_cn)}) — {yg.strength}"):
                            _yg_text = yg.description_cn if get_lang() in ("zh", "zh_cn") else yg.description
                            st.write(auto_cn(_yg_text))
                    _render_ai_button("tab_indian", v_chart, btn_key="vedic_yogas")

                with _v_tab_bphs:
                    st.subheader("📜 " + t("vedic_subtab_bphs"))
                    bphs_result = compute_bphs(v_chart.planets, v_chart.houses, v_chart.ascendant)
                    _render_bphs_result(bphs_result)
                    _render_ai_button("tab_indian", v_chart, btn_key="vedic_bphs")

                with _v_tab_varga:
                    st.subheader("📊 " + t("vedic_subtab_varga"))
                    st.caption(t("bphs_caption_varga_tab"))
                    _varga_tab_labels = [f"{k} {VARGA_INFO[k]['zh']}" for k in VARGA_KEYS]
                    _varga_tabs = st.tabs(_varga_tab_labels)
                    for _vi, _vk in enumerate(VARGA_KEYS):
                        with _varga_tabs[_vi]:
                            _vc = compute_varga_chart(_vk, v_chart.planets, v_chart.ascendant)
                            render_single_varga(_vc)
                    _render_ai_button("tab_indian", v_chart, btn_key="vedic_varga")

                with _v_tab_financial:
                    render_vedic_financial_tab(input_tz=float(_p.get("timezone", 8.0)))

            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_indian"))

    # --- 吠陀風水（Vastu Shastra）---
    elif _selected_system == "tab_vastu":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_vastu")):
                    _vastu_vchart = compute_vedic_chart(**_p)
                from frontend.vastu_renderer import render_vastu_tab
                render_vastu_tab(
                    v_chart=_vastu_vchart,
                    after_chart_hook=lambda: _render_ai_button("tab_vastu", _vastu_vchart, btn_key="vastu"),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_vastu_prompt"))
            st.markdown(t("desc_vastu"))

    # --- 宿曜道 ---
    elif _selected_system == "tab_lal_kitab":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_lal_kitab")):
                    _lk_chart = compute_lal_kitab_chart(**_p)
                _lk_lang = st.session_state.get("lang", "zh")
                render_lal_kitab_1952_page(
                    _lk_chart,
                    lang=_lk_lang,
                    after_chart_hook=lambda: _render_ai_button("tab_lal_kitab", _lk_chart, btn_key="lal_kitab"),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_lal_kitab"))

    # --- 宿曜道 ---
    elif _selected_system == "tab_sukkayodo":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_indian")):
                    _v_chart_sukka = compute_vedic_chart(**_p)
                render_sukkayodo_chart(_v_chart_sukka, after_chart_hook=lambda: _render_ai_button("tab_sukkayodo", _v_chart_sukka, btn_key="sukkayodo"))
                st.subheader(t("sukkayodo_subheader"))
                st.info(t("sukkayodo_info"))
                st.markdown(t("desc_sukkayodo"))
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_sukkayodo"))

    # --- 泰國占星 ---
    elif _selected_system == "tab_thai":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_thai")):
                    t_chart = compute_thai_chart(**_p)
                thai_tab_chart, thai_tab_nine, thai_tab_brahma = st.tabs(
                    [t("thai_subtab_chart"), t("thai_subtab_nine"), t("thai_subtab_brahma")]
                )
                with thai_tab_chart:
                    render_thai_chart(t_chart, after_chart_hook=lambda: _render_ai_button("tab_thai", t_chart, btn_key="thai"))
                with thai_tab_nine:
                    nine_grid_result = calculate_thai_nine_grid(
                        birth_date.day, birth_date.month, birth_date.year
                    )
                    render_nine_grid(nine_grid_result)
                    st.markdown("---")
                    divination_result = calculate_nine_palace_divination(t_chart)
                    render_nine_palace_divination(divination_result)
                with thai_tab_brahma:
                    from datetime import date as _date_cls
                    _bj_bd = _date_cls(birth_date.year, birth_date.month, birth_date.day)
                    _bj_weekday = _bj_bd.weekday()  # 0=Mon … 6=Sun
                    _bj_age = None
                    _bj_gender = None
                    _bj_age_col, _bj_gender_col = st.columns(2)
                    with _bj_age_col:
                        _bj_age = st.number_input(
                            "年齡 (Age)", min_value=1, max_value=120,
                            value=max(1, _date_cls.today().year - birth_date.year),
                            key="brahma_jati_age",
                        )
                    with _bj_gender_col:
                        _bj_gender = st.selectbox(
                            "性別 (Gender)",
                            options=["male", "female"],
                            format_func=lambda x: "男 Male" if x == "male" else "女 Female",
                            key="brahma_jati_gender",
                        )
                    _bj_reading = compute_brahma_jati(
                        ce_year=birth_date.year,
                        month=birth_date.month,
                        weekday=_bj_weekday,
                        age=_bj_age,
                        gender=_bj_gender,
                    )
                    render_brahma_jati(_bj_reading)
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_thai"))
            render_brahma_jati_browse()

    # --- 老撾占星 ---
    elif _selected_system == "tab_laos":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_laos")):
                    lao_chart = compute_lao_chart(**_p)
                render_lao_horasat(
                    lao_chart,
                    lang=get_lang(),
                    after_chart_hook=lambda: _render_ai_button("tab_laos", lao_chart, btn_key="tab_laos"),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_lao_prompt"))
            st.markdown(t("desc_laos"))

    # --- 卡巴拉占星 ---
    elif _selected_system == "tab_kabbalistic":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_kabbalistic")):
                    k_chart = compute_kabbalistic_chart(**_p)
                render_kabbalistic_chart(k_chart, after_chart_hook=lambda: _render_ai_button("tab_kabbalistic", k_chart, btn_key="kabbalistic"))
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_kabbalistic"))

    # --- 猶太 Mazzalot 占星 ---
    elif _selected_system == "tab_mazzalot":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_mazzalot")):
                    _mz_chart = compute_mazzalot_chart(
                        year=_p["year"], month=_p["month"], day=_p["day"],
                        hour=_p["hour"], minute=_p["minute"],
                        timezone=_p["timezone"],
                        lat=_p["latitude"], lon=_p["longitude"],
                    )
                _mz_tab_star, _mz_tab_natal, _mz_tab_omens = st.tabs([
                    t("mazzalot_subtab_star"),
                    t("mazzalot_subtab_natal"),
                    t("mazzalot_subtab_omens"),
                ])
                with _mz_tab_star:
                    _mz_svg = build_mazzalot_star_of_david_svg(
                        _mz_chart,
                        year=birth_date.year,
                        month=birth_date.month,
                        day=birth_date.day,
                        hour=birth_time.hour,
                        minute=birth_time.minute,
                        tz=input_tz,
                        location=location_name,
                    )
                    st.markdown(_mz_svg, unsafe_allow_html=True)
                    st.caption(
                        '<p style="text-align:center; color:#888; font-size:11px;">'
                        'Star of David Wheel (Magen David) — Sidereal zodiac · '
                        '12 Mazzalot · Sefer Yetzirah letters · Twelve Tribes'
                        '</p>',
                        unsafe_allow_html=True,
                    )
                    _render_ai_button("tab_mazzalot", _mz_chart, btn_key="mazzalot")
                with _mz_tab_natal:
                    render_mazzalot_chart(_mz_chart)
                with _mz_tab_omens:
                    st.subheader("📜 " + t("mazzalot_omens_title"))
                    for _omen in _mz_chart.omens:
                        _omen_icon = "🌟" if _omen.condition == "strong" else "⚠️"
                        _en_part = f"  \n_{_omen.text_en}_" if _omen.text_en else ""
                        st.markdown(
                            f"{_omen_icon} **{_omen.planet}** — "
                            f"*{_omen.condition.upper()}*: {_omen.text}{_en_part}"
                        )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_mazzalot"))

    # --- 阿拉伯占星 ---
    elif _selected_system == "tab_arabic":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                arabic_subtab_chart, arabic_subtab_lots, arabic_subtab_picatrix, arabic_subtab_invocation, arabic_subtab_shams, arabic_subtab_ref, arabic_subtab_ms164 = st.tabs([
                    t("arabic_subtab_chart"),
                    t("arabic_subtab_lots"),
                    t("arabic_subtab_picatrix"),
                    t("arabic_subtab_invocation"),
                    t("arabic_subtab_shams"),
                    t("arabic_subtab_reference"),
                    t("arabic_subtab_ms164"),
                ])

                with arabic_subtab_chart:
                    with st.spinner(t("spinner_arabic")):
                        a_chart = compute_arabic_chart(**_p)
                    render_arabic_chart(a_chart, after_chart_hook=lambda: _render_ai_button("tab_arabic", a_chart, btn_key="arabic"))

                with arabic_subtab_lots:
                    _lots_mode_options = {
                        "tropical": t("arabic_lots_tropical"),
                        "sidereal": t("arabic_lots_sidereal"),
                    }
                    _lots_mode = st.selectbox(
                        t("arabic_lots_zodiac_mode"),
                        options=list(_lots_mode_options.keys()),
                        format_func=lambda _mode: _lots_mode_options[_mode],
                        index=0,
                        key="arabic_lots_mode",
                    )
                    with st.spinner(t("spinner_arabic_lots")):
                        _lots_result = compute_albiruni_lots(
                            year=_p["year"],
                            month=_p["month"],
                            day=_p["day"],
                            hour=_p["hour"],
                            minute=_p["minute"],
                            timezone=_p["timezone"],
                            latitude=_p["latitude"],
                            longitude=_p["longitude"],
                            zodiac_mode=_lots_mode,
                        )
                    render_arabic_lots_dashboard(_lots_result, t)

                # --- Picatrix 星體魔法 ---
                with arabic_subtab_picatrix:
                    st.subheader(t("picatrix_subheader"))
                    st.caption(t("picatrix_source"))

                    _birth_moon_lon: float | None = compute_moon_longitude(
                        year=birth_date.year,
                        month=birth_date.month,
                        day=birth_date.day,
                        hour=birth_time.hour,
                        minute=birth_time.minute,
                        timezone=input_tz,
                    )

                    ptab_browse, ptab_mansions, ptab_hours, ptab_talisman = st.tabs([
                        t("picatrix_subtab_browse"),
                        t("picatrix_subtab_mansion"),
                        t("picatrix_subtab_hours"),
                        t("picatrix_subtab_talisman"),
                    ])

                    with ptab_browse:
                        render_picatrix_browse()

                    with ptab_mansions:
                        st.info(t("picatrix_moon_lon_info").format(lon=_birth_moon_lon))
                        render_mansion_lookup(moon_lon=_birth_moon_lon)

                    with ptab_hours:
                        render_planetary_hours_tool(
                            year=birth_date.year,
                            month=birth_date.month,
                            day=birth_date.day,
                            timezone=input_tz,
                            latitude=input_lat,
                            longitude=input_lon,
                        )

                    with ptab_talisman:
                        render_talisman_generator()

                with arabic_subtab_invocation:
                    render_picatrix_invocations()

                # --- 太陽知識大全 (Shams al-Maʻārif) ---
                with arabic_subtab_shams:
                    st.subheader(t("shams_subheader"))
                    st.caption(t("shams_source"))

                    # Compute Arabic chart if not already done
                    try:
                        _a_chart_for_shams = a_chart
                    except NameError:
                        with st.spinner(t("spinner_arabic")):
                            _a_chart_for_shams = compute_arabic_chart(**_p)
                    _shams_planets = {
                        p.name.split("(")[0].strip().split()[-1]: p.longitude
                        for p in _a_chart_for_shams.planets
                    }
                    _shams_sun_idx: int | None = None
                    for p in _a_chart_for_shams.planets:
                        if "Sun" in p.name:
                            _shams_sun_idx = int(p.longitude / 30.0)
                            break
                    render_shams_chart(chart_planets=_shams_planets,
                                       birth_sign_idx=_shams_sun_idx)

                with arabic_subtab_ref:
                    st.subheader(t("arabic_subtab_reference"))
                    _render_reference_library()

                with arabic_subtab_ms164:
                    render_ms164_browse()

            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            arabic_subtab_chart, arabic_subtab_lots, arabic_subtab_picatrix, arabic_subtab_invocation, arabic_subtab_shams, arabic_subtab_ref, arabic_subtab_ms164 = st.tabs([
                t("arabic_subtab_chart"),
                t("arabic_subtab_lots"),
                t("arabic_subtab_picatrix"),
                t("arabic_subtab_invocation"),
                t("arabic_subtab_shams"),
                t("arabic_subtab_reference"),
                t("arabic_subtab_ms164"),
            ])

            with arabic_subtab_chart:
                st.info(t("info_calc_prompt"))
                st.markdown(t("desc_arabic"))

            with arabic_subtab_lots:
                st.info(t("info_calc_prompt"))
                st.markdown(t("desc_arabic_lots"))

            with arabic_subtab_picatrix:
                st.subheader(t("picatrix_subheader"))
                st.caption(t("picatrix_source"))

                ptab_browse, ptab_mansions, ptab_hours, ptab_talisman = st.tabs([
                    t("picatrix_subtab_browse"),
                    t("picatrix_subtab_mansion"),
                    t("picatrix_subtab_hours"),
                    t("picatrix_subtab_talisman"),
                ])

                with ptab_browse:
                    render_picatrix_browse()

                with ptab_mansions:
                    render_mansion_lookup(moon_lon=None)

                with ptab_hours:
                    render_planetary_hours_tool(
                        timezone=input_tz,
                        latitude=input_lat,
                        longitude=input_lon,
                    )

                with ptab_talisman:
                    render_talisman_generator()

            with arabic_subtab_invocation:
                render_picatrix_invocations()

            with arabic_subtab_shams:
                st.subheader(t("shams_subheader"))
                st.caption(t("shams_source"))
                st.markdown(t("desc_shams"))
                render_shams_browse()

            with arabic_subtab_ref:
                st.subheader(t("arabic_subtab_reference"))
                _render_reference_library()

            with arabic_subtab_ms164:
                render_ms164_browse()

    # --- 也門占星 (Yemeni) ---
    elif _selected_system == "tab_yemeni":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_yemeni")):
                    _yemeni_chart = compute_yemeni_chart(
                        year=_p["year"], month=_p["month"], day=_p["day"],
                        hour=_p["hour"], minute=_p["minute"],
                        timezone=_p["timezone"],
                        latitude=_p["latitude"], longitude=_p["longitude"],
                        location_name=location_name,
                    )
                _y_tab_mandala, _y_tab_natal, _y_tab_omens = st.tabs([
                    t("yemeni_subtab_mandala"),
                    t("yemeni_subtab_natal"),
                    t("yemeni_subtab_omens"),
                ])
                with _y_tab_mandala:
                    _yemeni_svg = build_yemeni_manzil_mandala_svg(
                        _yemeni_chart,
                        year=birth_date.year,
                        month=birth_date.month,
                        day=birth_date.day,
                        hour=birth_time.hour,
                        minute=birth_time.minute,
                        tz=input_tz,
                        location=location_name,
                    )
                    st.markdown(_yemeni_svg, unsafe_allow_html=True)
                    st.caption(
                        '<p style="text-align:center; color:#888; font-size:11px;">'
                        'Yemeni Manzil Mandala — 28-mansion disc · '
                        'Rasulid manuscript style · Sidereal zodiac'
                        '</p>',
                        unsafe_allow_html=True,
                    )
                    _render_ai_button("tab_yemeni", _yemeni_chart, btn_key="yemeni")
                with _y_tab_natal:
                    render_yemeni_chart(_yemeni_chart)
                with _y_tab_omens:
                    st.subheader("📜 al-Ashraf " + t("yemeni_subtab_omens"))
                    for _omen in _yemeni_chart.omens:
                        _omen_icon = "🌟" if _omen.condition == "strong" else "⚠️"
                        st.markdown(
                            f"{_omen_icon} **{_omen.planet}** ({_omen.planet_cn}) — "
                            f"*{_omen.condition.upper()}*: {_omen.text} / {_omen.text_en}"
                        )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_yemeni"))

    # --- Picatrix 占星魔法 + Behenian 固定星 ---
    elif _selected_system == "tab_picatrix_behenian":
        _p = st.session_state.get("_calc_params", {})
        if _is_calculated and _p:
            try:
                from astro.western.western import compute_western_chart as _cwc
                with st.spinner(t("spinner_picatrix_behenian")):
                    _pb_chart = _cwc(**_p)
                render_picatrix_behenian(
                    chart=_pb_chart,
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p["minute"],
                    timezone_offset=_p["timezone"],
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_picatrix_behenian"))
            # Show compendium even without a chart
            try:
                from astro.picatrix_behenian.renderer import _render_compendium_tab
                _render_compendium_tab()
            except Exception:
                pass

    # --- 瑪雅占星 ---
    elif _selected_system == "tab_maya":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_maya")):
                    m_chart = compute_maya_chart(**_p)
                render_maya_chart(m_chart, after_chart_hook=lambda: _render_ai_button("tab_maya", m_chart, btn_key="maya"))
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_maya_prompt"))
            st.markdown(t("desc_maya"))

    # --- Armenian Astrology ---
    elif _selected_system == "tab_armenian":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_armenian")):
                    _armenian_chart = _compute_armenian_chart_fn(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p["minute"],
                        timezone=_p["timezone"],
                        latitude=_p["latitude"],
                        longitude=_p["longitude"],
                        location_name=_p.get("location_name", ""),
                    )
                render_armenian_chart_ui(
                    _armenian_chart,
                    after_chart_hook=lambda: _render_ai_button("tab_armenian", _armenian_chart, btn_key="armenian"),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_armenian_prompt"))
            st.markdown(t("desc_armenian"))

    # --- 印加 / 安地斯占星 ---
    elif _selected_system == "tab_andean":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_andean")):
                    _andean_chart = _compute_andean_chart_fn(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p["minute"],
                        timezone=_p["timezone"],
                        latitude=_p["latitude"],
                        longitude=_p["longitude"],
                        location_name=_p.get("location_name", ""),
                    )
                render_andean_chart_ui(
                    _andean_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_andean", _andean_chart, btn_key="andean"
                    ),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_andean_prompt"))
            st.markdown(t("desc_andean"))

    # --- 伊特魯里亞占星 (Etruscan Astrology) ---
    elif _selected_system == "tab_etruscan":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_etruscan")):
                    _etruscan_chart = _compute_etruscan_chart_fn(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p["minute"],
                        timezone=_p["timezone"],
                        latitude=_p["latitude"],
                        longitude=_p["longitude"],
                        location_name=_p.get("location_name", ""),
                    )
                render_etruscan_chart_ui(
                    _etruscan_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_etruscan", _etruscan_chart, btn_key="etruscan"
                    ),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_etruscan_prompt"))
            st.markdown(t("desc_etruscan"))

    # --- Dogon Sirius Cosmology ---
    elif _selected_system == "tab_dogon_sirius":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_dogon_sirius")):
                    _dogon_chart = compute_dogon_sirius_chart(**_p)
                render_dogon_sirius_chart(
                    _dogon_chart,
                    after_chart_hook=lambda: _render_ai_button("tab_dogon_sirius", _dogon_chart, btn_key="dogon_sirius"),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_dogon_sirius_prompt"))
            st.markdown(t("desc_dogon_sirius"))

    # --- Amazigh (Berber) 北非柏柏爾占星 ---
    elif _selected_system == "tab_amazigh":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_amazigh")):
                    _amazigh_chart = compute_amazigh_chart(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p["minute"],
                        timezone=_p["timezone"],
                        latitude=_p["latitude"],
                        longitude=_p["longitude"],
                        location_name=_p.get("location_name", ""),
                    )
                _amz_tab_sky, _amz_tab_chart = st.tabs([
                    "ⵣ 星空圖 Sky Chart",
                    "📊 占星資料 Chart Data",
                ])
                with _amz_tab_sky:
                    st.markdown(render_amazigh_sky_svg(_amazigh_chart), unsafe_allow_html=True)
                    if _amazigh_chart.direction:
                        st.caption(
                            f"{_amazigh_chart.direction.name_zh} / {_amazigh_chart.direction.name_en} · "
                            f"{_amazigh_chart.direction.season_zh} / {_amazigh_chart.direction.season_en}"
                        )
                    _render_ai_button("tab_amazigh", _amazigh_chart, btn_key="amazigh_sky")
                with _amz_tab_chart:
                    render_amazigh_chart(
                        _amazigh_chart,
                        after_chart_hook=lambda: _render_ai_button("tab_amazigh", _amazigh_chart, btn_key="amazigh_chart"),
                    )
                    st.markdown(t("desc_amazigh"))
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_amazigh_prompt"))
            st.markdown(t("desc_amazigh"))

    # --- Ethiopian Bahre Hasab ---
    elif _selected_system == "tab_bahre_hasab":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                _probe = analyze_bahre_hasab_date(date(_p["year"], _p["month"], _p["day"]))
                with st.spinner(t("spinner_bahre_hasab")):
                    render_bahre_hasab_tab(
                        calc_params=_p,
                        after_chart_hook=lambda: _render_ai_button("tab_bahre_hasab", _probe, btn_key="bahre_hasab"),
                    )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_bahre_hasab_prompt"))
            st.markdown(t("desc_bahre_hasab"))

    # --- 阿茲特克占星 ---
    elif _selected_system == "tab_aztec":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_aztec")):
                    az_chart = compute_aztec_chart(**_p)
                render_aztec_chart(az_chart, after_chart_hook=lambda: _render_ai_button("tab_aztec", az_chart, btn_key="aztec"))
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_aztec"))

    # --- 緬甸占星 (Mahabote) ---
    elif _selected_system == "tab_mahabote":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_mahabote")):
                    mb_chart = compute_mahabote_chart(**_p)
                render_mahabote_chart(mb_chart, after_chart_hook=lambda: _render_ai_button("tab_mahabote", mb_chart, btn_key="mahabote"))
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_mahabote"))

    # --- 古埃及十度區間 (Decans) ---
    elif _selected_system == "tab_decans":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_decans")):
                    dc_chart = compute_decan_chart(**_p)
                render_decan_chart(dc_chart)
                _render_ai_button("tab_decans", dc_chart, btn_key="decans")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_decans_prompt"))
            render_decan_browse()

    # --- 納迪占星 (Nadi Jyotish) ---
    elif _selected_system == "tab_nadi":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_nadi")):
                    nadi_chart = compute_nadi_chart(**_p)
                render_nadi_chart(nadi_chart, after_chart_hook=lambda: _render_ai_button("tab_nadi", nadi_chart, btn_key="nadi"))
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_nadi"))

    # --- Jaimini 占星 (Jaimini Astrology) ---
    elif _selected_system == "tab_jaimini":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_jaimini")):
                    jm_chart = compute_jaimini_chart(**_p)

                _jm_tab_chart, _jm_tab_dasha = st.tabs([
                    t("jaimini_subtab_chart"),
                    t("jaimini_subtab_dasha"),
                ])

                with _jm_tab_chart:
                    render_jaimini_chart(jm_chart, after_chart_hook=lambda: _render_ai_button("tab_jaimini", jm_chart, btn_key="jaimini"))

                with _jm_tab_dasha:
                    render_jaimini_dasha(jm_chart)
                    _render_ai_button("tab_jaimini", jm_chart, btn_key="jaimini_dasha")

            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_jaimini"))

    # --- 蒙古祖爾海 (Zurkhai) ---
    elif _selected_system == "tab_zurkhai":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_zurkhai")):
                    zk_chart = compute_zurkhai_chart(**_p)
                render_zurkhai_chart(zk_chart, after_chart_hook=lambda: _render_ai_button("tab_zurkhai", zk_chart, btn_key="zurkhai"))
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_zurkhai"))

    # --- 藏傳時輪金剛占星 (Tibetan Kalachakra) ---
    elif _selected_system == "tab_tibetan":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                _g = st.session_state["_calc_gender"]
                with st.spinner(t("spinner_tibetan")):
                    _tib_chart = compute_tibetan_chart(**_p, gender=_g)
                _t_tab_mandala, _t_tab_natal, _t_tab_mewa, _t_tab_forces, _t_tab_planets = st.tabs([
                    t("tibetan_subtab_mandala"),
                    t("tibetan_subtab_natal"),
                    t("tibetan_subtab_mewa"),
                    t("tibetan_subtab_forces"),
                    t("tibetan_subtab_planets"),
                ])
                with _t_tab_mandala:
                    _tib_svg = build_kalachakra_mandala_svg(
                        _tib_chart,
                        year=birth_date.year,
                        month=birth_date.month,
                        day=birth_date.day,
                        hour=birth_time.hour,
                        minute=birth_time.minute,
                        tz=input_tz,
                        location=location_name,
                    )
                    st.markdown(_tib_svg, unsafe_allow_html=True)
                    st.caption(
                        '<p style="text-align:center;color:#888;font-size:11px;">'
                        'Kalachakra Mandala · 時輪金剛曼荼羅 · '
                        'Outer: 12 Animals · Middle: 8 Parkha · Inner: 9 Mewa'
                        '</p>',
                        unsafe_allow_html=True,
                    )
                    _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_mandala")
                with _t_tab_natal:
                    render_tibetan_chart(_tib_chart, after_chart_hook=lambda: _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_natal"))
                with _t_tab_mewa:
                    from astro.tibetan import _render_mewa_parkha
                    _render_mewa_parkha(_tib_chart)
                    _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_mewa")
                with _t_tab_forces:
                    from astro.tibetan import _render_five_forces
                    _render_five_forces(_tib_chart)
                    _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_forces")
                with _t_tab_planets:
                    from astro.tibetan import _render_planets
                    _render_planets(_tib_chart)
                    _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_planets")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_tibetan"))

    # --- 日本九星氣學 (Japanese Nine Star Ki) ---
    elif _selected_system == "tab_nine_star_ki":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_nine_star_ki")):
                    _nsk_chart = compute_nine_star_ki_chart(**_p)
                render_nine_star_ki_chart(
                    _nsk_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_nine_star_ki", _nsk_chart, btn_key="nine_star_ki"
                    ),
                    lang=get_lang(),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_nine_star_ki"))

    # --- 凱爾特樹木曆法 (Celtic Tree Calendar — Robert Graves 1948) ---
    elif _selected_system == "tab_celtic_tree":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_celtic_tree")):
                    _celtic_chart = compute_celtic_tree_chart(**_p)
                render_celtic_tree_chart(
                    _celtic_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_celtic_tree", _celtic_chart, btn_key="celtic_tree"
                    ),
                    lang=get_lang(),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_celtic_tree"))

    # --- 希臘占星 (Hellenistic) ---
    elif _selected_system == "tab_hellenistic":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                # Hellenistic needs a western chart first
                with st.spinner(t("spinner_western")):
                    _hellen_w = compute_western_chart(**_p)
                with st.spinner(t("spinner_hellenistic")):
                    _hellen_chart = compute_hellenistic_chart(
                        _hellen_w,
                        birth_year=birth_date.year,
                        current_year=datetime.now().year,
                    )
                    _hellen_ext = compute_hellenistic_extended(_hellen_w, _hellen_chart)
                _h_tab_chart, _h_tab_natal, _h_tab_prof, _h_tab_zr, _h_tab_lots, _h_tab_ext_lots, _h_tab_synkrasis, _h_tab_centiloquy = st.tabs([
                    t("hellen_subtab_chart"),
                    t("hellen_subtab_natal"),
                    t("hellen_subtab_profections"),
                    t("hellen_subtab_zr"),
                    t("hellen_subtab_lots"),
                    "📜 Extended Lots / 擴充 Lots",
                    "⚗️ Valens Synkrasis / 行星組合",
                    t("hellen_subtab_centiloquy"),
                ])
                with _h_tab_chart:
                    _greek_svg = build_greek_horoscope_svg(
                        _hellen_chart,
                        year=birth_date.year,
                        month=birth_date.month,
                        day=birth_date.day,
                        hour=birth_time.hour,
                        minute=birth_time.minute,
                        tz=input_tz,
                        location=location_name,
                    )
                    st.markdown(_greek_svg, unsafe_allow_html=True)
                    st.caption(
                        '<p style="text-align:center; color:#888; font-size:11px;">'
                        'Greek Horoscope (θέμα) — Square chart form after L 497 · '
                        'Whole-sign houses · ASC at left, MC at top'
                        '</p>',
                        unsafe_allow_html=True,
                    )
                    _render_ai_button("tab_hellenistic", _hellen_chart, btn_key="hellenistic")
                with _h_tab_natal:
                    render_hellenistic_chart(_hellen_chart)
                with _h_tab_prof:
                    render_annual_profections(
                        asc_lon=_hellen_chart.ascendant,
                        birth_year=birth_date.year,
                        num_years=24,
                        lang=get_lang(),
                    )
                with _h_tab_zr:
                    # Retrieve Lot of Fortune and Lot of Spirit longitudes
                    _zr_fortune_lon = next(
                        (l.longitude for l in _hellen_chart.lots if "Fortune" in l.name), 0.0
                    )
                    _zr_spirit_lon = next(
                        (l.longitude for l in _hellen_chart.lots if "Spirit" in l.name), 0.0
                    )
                    render_zodiacal_releasing(
                        fortune_lon=_zr_fortune_lon,
                        spirit_lon=_zr_spirit_lon,
                        birth_jd=_hellen_w.julian_day,
                        target_jd=_hellen_w.julian_day + (datetime.now().year - birth_date.year) * 365.25,
                        lang=get_lang(),
                    )
                with _h_tab_lots:
                    if _hellen_chart.lots:
                        st.subheader(t("hellen_lots_header"))
                        st.dataframe([{"Name": f"{l.name} ({auto_cn(l.name_cn)})",
                                       "Sign": l.sign, "Degree": f"{l.sign_degree:.2f}°",
                                       "House": l.house, "Formula": l.formula_en,
                                       "Meaning": auto_cn(l.meaning_cn)}
                                      for l in _hellen_chart.lots],
                                     width="stretch")

                with _h_tab_ext_lots:
                    if _hellen_ext.extended_lots:
                        render_extended_lots(_hellen_ext.extended_lots)
                with _h_tab_synkrasis:
                    if _hellen_ext.synkrasis:
                        render_valens_combinations(_hellen_ext.synkrasis)

                with _h_tab_centiloquy:
                    st.subheader(t("centiloquy_header"))
                    from astro.classic.ptolemy_centiloquy import get_random_aphorism, search_aphorism, get_all_aphorisms, format_aphorism
                    # Daily aphorism
                    st.info(format_aphorism(get_random_aphorism()))
                    # Search
                    _cent_query = st.text_input(t("centiloquy_search_label"), key="centiloquy_search")
                    if _cent_query:
                        _results = search_aphorism(_cent_query)
                        if _results:
                            for _r in _results:
                                st.markdown(format_aphorism(_r))
                        else:
                            st.warning(t("centiloquy_no_match"))
                    else:
                        for _a in get_all_aphorisms():
                            with st.expander(t("centiloquy_aphorism_num").format(n=_a['id'])):
                                st.markdown(_a["text"])

            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_hellenistic"))

    # --- 古巴比倫占星 (Babylonian) ---
    elif _selected_system == "tab_babylonian":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_babylonian")):
                    _bab_chart = compute_babylonian_chart(
                        year=_p["year"], month=_p["month"], day=_p["day"],
                        hour=_p["hour"], minute=_p["minute"],
                        timezone=_p["timezone"],
                        lat=_p["latitude"], lon=_p["longitude"],
                    )
                _bab_tab_chart, _bab_tab_natal, _bab_tab_omens = st.tabs([
                    t("babylonian_subtab_chart"),
                    t("babylonian_subtab_natal"),
                    t("babylonian_subtab_omens"),
                ])
                with _bab_tab_chart:
                    _bab_svg = build_babylonian_planisphere_svg(
                        _bab_chart,
                        year=birth_date.year,
                        month=birth_date.month,
                        day=birth_date.day,
                        hour=birth_time.hour,
                        minute=birth_time.minute,
                        tz=input_tz,
                        location=location_name,
                    )
                    st.markdown(_bab_svg, unsafe_allow_html=True)
                    st.caption(
                        '<p style="text-align:center; color:#888; font-size:11px;">'
                        'Babylonian Planisphere (K.8538 style) — 8-sector clay disc · '
                        'Sidereal zodiac · MUL.APIN sign names'
                        '</p>',
                        unsafe_allow_html=True,
                    )
                    _render_ai_button("tab_babylonian", _bab_chart, btn_key="babylonian")
                with _bab_tab_natal:
                    render_babylonian_chart(_bab_chart)
                with _bab_tab_omens:
                    st.subheader("📜 Enūma Anu Enlil " + t("babylonian_subtab_omens"))
                    for _omen in _bab_chart.omens:
                        _omen_icon = "🌟" if _omen.condition == "strong" else "⚠️"
                        st.markdown(
                            f"{_omen_icon} **{_omen.planet}** ({_omen.god_name}) — "
                            f"*{_omen.condition.upper()}*: {_omen.text}"
                        )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_babylonian"))

    # --- 蘇美/美索不達米亞占星 (Sumerian / Mesopotamian Astrology) ---
    elif _selected_system == "tab_sumerian":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                render_sumerian_chart(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p.get("minute", 0),
                    timezone=_p.get("timezone", 0.0),
                    latitude=_p.get("latitude", 32.542),
                    longitude=_p.get("longitude", 44.421),
                    location_name=_p.get("location_name", ""),
                )
                _sumerian_chart = compute_sumerian_chart(
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p.get("minute", 0),
                    timezone=_p.get("timezone", 0.0),
                    lat=_p.get("latitude", 32.542),
                    lon=_p.get("longitude", 44.421),
                    location_name=_p.get("location_name", ""),
                )
                _render_ai_button("tab_sumerian", _sumerian_chart, btn_key="sumerian")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_sumerian_prompt"))
            st.markdown(t("desc_sumerian"))

    # --- 達摩一掌經 (Damo One Palm Scripture) ---
    elif _selected_system == "tab_damo":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                _damo_params = dict(_p)
                _damo_params["gender"] = gender
                with st.spinner(t("spinner_damo")):
                    _damo_chart = compute_damo_chart(**_damo_params)
                render_damo_chart(
                    _damo_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_damo", _damo_chart, btn_key="damo"
                    ),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_damo"))

    # --- 滌器遺訣 Di Qi Yi Jue ---
    elif _selected_system == "tab_diqiyijue":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                _diqiyijue_params = dict(_p)
                _diqiyijue_params["gender"] = gender
                with st.spinner(t("spinner_diqiyijue")):
                    _diqiyijue_chart = compute_diqiyijue_chart(**_diqiyijue_params)
                render_diqiyijue_chart(
                    _diqiyijue_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_diqiyijue", _diqiyijue_chart, btn_key="diqiyijue"
                    ),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_diqiyijue_prompt"))
            st.markdown(t("desc_diqiyijue"))

    # --- 十二星次 (Twelve Ci) ---
    elif _selected_system == "tab_twelve_ci":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_twelve_ci")):
                    _ci_chart = compute_twelve_ci_chart(**_p)

                _ci_tab_wheel, _ci_tab_detail = st.tabs([
                    t("twelve_ci_subtab_chart"),
                    t("twelve_ci_subtab_detail"),
                ])

                with _ci_tab_wheel:
                    _ci_svg = build_twelve_ci_svg(
                        _ci_chart,
                        year=birth_date.year,
                        month=birth_date.month,
                        day=birth_date.day,
                        hour=birth_time.hour,
                        minute=birth_time.minute,
                        tz=input_tz,
                        location=location_name,
                    )
                    st.markdown(_ci_svg, unsafe_allow_html=True)
                    _render_ai_button("tab_twelve_ci", _ci_chart, btn_key="twelve_ci")

                with _ci_tab_detail:
                    render_twelve_ci_chart(
                        _ci_chart,
                        after_chart_hook=lambda: _render_ai_button(
                            "tab_twelve_ci", _ci_chart, btn_key="twelve_ci_detail"
                        ),
                    )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_twelve_ci"))

    # --- 萬化仙禽 (WanHua XianQin) ---
    elif _selected_system == "tab_chinstar":

        # ── Lunar date conversion (hidden) ──────────────────────────
        _chinstar_year = birth_date.year
        _chinstar_month = birth_date.month
        _chinstar_day = birth_date.day
        _chinstar_hour = birth_time.hour
        _auto_ok = False

        if _is_calculated:
            try:
                import swisseph as _swe_cs
                from astro.ziwei import _solar_to_lunar as _cs_solar_to_lunar
                _p = st.session_state["_calc_params"]
                _cs_jd = _swe_cs.julday(
                    _p["year"], _p["month"], _p["day"],
                    _p["hour"] + _p["minute"] / 60.0 - _p["timezone"],
                )
                _cs_ly, _cs_lm, _cs_ld, _cs_leap = _cs_solar_to_lunar(_cs_jd)
                _chinstar_year = _cs_ly
                _chinstar_month = _cs_lm
                _chinstar_day = _cs_ld
                _chinstar_hour = _p["hour"]
                _auto_ok = True
            except Exception:
                pass

        _cs_gender = "M" if gender == "male" else "F"

        if _auto_ok:
            try:
                with st.spinner(t("spinner_chinstar")):
                    _cs_tool = WanHuaXianQin()
                    _cs_chart = _cs_tool.build_chart(
                        year=int(_chinstar_year),
                        month=int(_chinstar_month),
                        day=int(_chinstar_day),
                        hour=int(_chinstar_hour),
                        gender=_cs_gender,
                    )

                _cs_tab_chart, _cs_tab_xiangtai, _cs_tab_gui_jian = st.tabs([
                    t("chinstar_subtab_chart"),
                    t("chinstar_subtab_xiangtai"),
                    t("chinstar_subtab_gui_jian"),
                ])

                with _cs_tab_chart:
                    from astro.chinstar.chinstar import BRANCHES as _cs_branches, QIN_ELEMENT as _cs_qin_elem

                    bi = _cs_chart["basic_info"]
                    p = _cs_chart["palaces"]
                    s = _cs_chart["stars"]
                    pat = _cs_chart["pattern"]

                    # ── 宮位→禽 映射 ──────────────────────────────
                    _cs_palace_bird = {
                        "命宮":   s["ming_xing"],
                        "財帛宮": s["derived"].get("財帛星", ""),
                        "兄弟宮": s["derived"].get("兄弟星", ""),
                        "田宅宮": s["derived"].get("田宅星", ""),
                        "子女宮": s["derived"].get("子息星", ""),
                        "奴僕宮": s["derived"].get("奴僕星", ""),
                        "夫妻宮": s["derived"].get("妻妾星", ""),
                        "疾厄宮": s["derived"].get("疾厄星", ""),
                        "遷移宮": s["derived"].get("遷移星", ""),
                        "官祿宮": s["derived"].get("官祿星", ""),
                        "福德宮": s["derived"].get("福德星", ""),
                        "相貌宮": s["derived"].get("相貌星", ""),
                    }
                    # 地支→宮名（反查）
                    _cs_branch_to_palace = {v: k for k, v in p["twelve"].items()}

                    # 特殊宮位地支（命/身/胎）
                    _cs_ming_br = p["ming_gong"]["branch"]
                    _cs_shen_br = p["shen_gong"]["branch"]
                    _cs_tai_br  = p["tai_gong"]["branch"]

                    # 五行色彩 (dark theme)
                    _cs_elem_bg = {
                        "木": "rgba(56,142,60,0.15)", "火": "rgba(198,40,40,0.15)",
                        "土": "rgba(245,127,23,0.15)", "金": "rgba(158,158,158,0.15)", "水": "rgba(21,101,192,0.15)",
                    }
                    _cs_elem_bd = {
                        "木": "rgba(56,142,60,0.4)", "火": "rgba(198,40,40,0.4)",
                        "土": "rgba(245,127,23,0.4)", "金": "rgba(158,158,158,0.4)", "水": "rgba(21,101,192,0.4)",
                    }

                    def _cs_cell(branch_char: str) -> str:
                        palace = _cs_branch_to_palace.get(branch_char, "")
                        bird   = _cs_palace_bird.get(palace, "")
                        elem   = _cs_qin_elem.get(bird, "")
                        bg     = _cs_elem_bg.get(elem, "rgba(30,27,75,0.4)")
                        bd     = _cs_elem_bd.get(elem, "rgba(167,139,250,0.3)")
                        badge  = ""
                        if branch_char == _cs_ming_br:
                            badge = '<span style="color:#ef4444;font-size:10px;">★命</span> '
                            bd    = "rgba(239,68,68,0.5)"
                            bg    = "rgba(239,68,68,0.1)"
                        elif branch_char == _cs_shen_br:
                            badge = '<span style="color:#a78bfa;font-size:10px;">☆身</span> '
                            bd    = "rgba(167,139,250,0.5)"
                            bg    = "rgba(167,139,250,0.1)"
                        elif branch_char == _cs_tai_br:
                            badge = '<span style="color:#facc15;font-size:10px;">◎胎</span> '
                            bd    = "rgba(250,204,21,0.5)"
                            bg    = "rgba(250,204,21,0.1)"
                        return (
                            f'<td style="width:25%;min-width:70px;height:88px;text-align:center;'
                            f'vertical-align:middle;border:2px solid {bd};'
                            f'background:{bg};padding:4px 2px;border-radius:8px;">'
                            f'<div style="font-size:11px;color:#b0b0d0;font-weight:bold;">'
                            f'{badge}{branch_char}宮</div>'
                            f'<div style="font-size:11px;color:#e0e0ff;margin-top:2px;">{palace}</div>'
                            f'<div style="font-size:14px;color:#a78bfa;font-weight:bold;'
                            f'margin-top:3px;">{bird}</div>'
                            f'</td>'
                        )

                    # 中央格（基本資料 + 三主星 + 格局）
                    _cs_center_td = (
                        '<td colspan="2" rowspan="2" style="text-align:center;'
                        'vertical-align:middle;border:2px solid rgba(167,139,250,0.3);'
                        'background:rgba(30,27,75,0.6);padding:10px 8px;border-radius:8px;'
                        'line-height:1.6;">'
                        '<div style="font-size:15px;font-weight:bold;color:#a78bfa;'
                        'letter-spacing:2px;">萬化仙禽</div>'
                        f'<div style="font-size:11px;color:#e0e0ff;margin-top:6px;">'
                        f'{bi["year"]}年{bi["month"]}月{bi["day"]}日 {bi["hour"]}時</div>'
                        f'<div style="font-size:11px;color:#e0e0ff;">{bi["gender"]}命 {bi["day_night"]}</div>'
                        f'<div style="font-size:11px;color:#e0e0ff;">{bi["season"]}季 · {bi["san_yuan"]}</div>'
                        '<hr style="margin:6px 0;border-color:rgba(167,139,250,0.2);">'
                        f'<div style="font-size:11px;color:#e0e0ff;"><b>胎星</b>：{s["tai_xing"]}</div>'
                        f'<div style="font-size:11px;color:#e0e0ff;"><b>命星</b>：{s["ming_xing"]}</div>'
                        f'<div style="font-size:11px;color:#e0e0ff;"><b>身星</b>：{s["shen_xing"]}</div>'
                        '<hr style="margin:6px 0;border-color:rgba(167,139,250,0.2);">'
                        f'<div style="font-size:11px;color:#e0e0ff;">'
                        f'<b>格局</b>：{pat["grade"]}</div>'
                        '</td>'
                    )

                    # 大六壬式四列排盤
                    # Row 0: 巳(5)  午(6)  未(7)  申(8)
                    # Row 1: 辰(4)  [CENTER]       酉(9)
                    # Row 2: 卯(3)  [CENTER]       戌(10)
                    # Row 3: 寅(2)  丑(1)  子(0)  亥(11)
                    _cs_br = _cs_branches
                    _cs_grid = (
                        '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
                        '<table style="border-collapse:separate;border-spacing:4px;'
                        'margin:10px auto;width:100%;table-layout:fixed;font-family:\'Noto Sans TC\',serif;">'
                        "<tr>"
                        + _cs_cell(_cs_br[5])  + _cs_cell(_cs_br[6])
                        + _cs_cell(_cs_br[7])  + _cs_cell(_cs_br[8])
                        + "</tr><tr>"
                        + _cs_cell(_cs_br[4])  + _cs_center_td + _cs_cell(_cs_br[9])
                        + "</tr><tr>"
                        + _cs_cell(_cs_br[3])  + _cs_cell(_cs_br[10])
                        + "</tr><tr>"
                        + _cs_cell(_cs_br[2])  + _cs_cell(_cs_br[1])
                        + _cs_cell(_cs_br[0])  + _cs_cell(_cs_br[11])
                        + "</tr></table></div>"
                    )
                    st.markdown(_cs_grid, unsafe_allow_html=True)
                    _render_ai_button("tab_chinstar", _cs_chart, btn_key="chinstar")
                    st.divider()

                    # ── 吞啗分析 ──────────────────────────────
                    st.markdown(t("chinstar_swallow_analysis_header"))
                    _sw = _cs_chart["swallow_analysis"]
                    if _sw:
                        _sw_rows = [{"對照": k, "判斷": v} for k, v in _sw.items()]
                        st.dataframe(_sw_rows, width='stretch', hide_index=True)
                    else:
                        st.info(t("chinstar_no_swallow"))
                    st.divider()

                    # ── 情性賦 ──────────────────────────────
                    st.markdown(t("chinstar_personality_header"))
                    for _label, text in _cs_chart["personality"].items():
                        st.info(text)
                    st.divider()

                    # ── 格局 ──────────────────────────────
                    st.markdown(t("chinstar_pattern_header").format(grade=pat["grade"]))
                    st.write(pat["reason"])

                    # ── 完整文字輸出（可複製） ──────────────────────
                    with st.expander(t("chinstar_full_text_expander")):
                        st.code(WanHuaXianQin.format_chart(_cs_chart), language="")

                with _cs_tab_xiangtai:
                    from astro.chinstar.chinstar import lookup_xiangtai, _get_xiangtai_fu

                    st.markdown(t("chinstar_xiangtai_title"))

                    # 查找匹配的相胎賦
                    _xt_match = lookup_xiangtai(s["ming_xing"], s["tai_xing"])
                    if _xt_match:
                        st.markdown(t("chinstar_xiangtai_match").format(
                            zhu=s["ming_xing"], tai=s["tai_xing"],
                        ))
                        _xt_cols = st.columns(2)
                        with _xt_cols[0]:
                            st.metric(t("chinstar_xiangtai_xingpin"), _xt_match["xing_pin"])
                        with _xt_cols[1]:
                            st.metric(t("chinstar_xiangtai_xiji"), _xt_match["xi_ji"])
                        st.info(f'**{t("chinstar_xiangtai_desc")}**：{_xt_match["desc"]}')
                        st.success(f'**{t("chinstar_xiangtai_poem")}**：\n\n{_xt_match["poem"]}')
                    else:
                        st.warning(t("chinstar_xiangtai_no_match"))

                    st.divider()

                    # 顯示相胎賦全覽
                    with st.expander(t("chinstar_xiangtai_ref")):
                        _xt_all = _get_xiangtai_fu()
                        _xt_rows = []
                        for _xt_e in _xt_all:
                            _xt_rows.append({
                                "主星": _xt_e["zhu"],
                                "胎星": _xt_e["tai"],
                                "形品": _xt_e["xing_pin"],
                                "喜忌": _xt_e["xi_ji"],
                                "論斷": _xt_e["desc"][:50] + "…" if len(_xt_e["desc"]) > 50 else _xt_e["desc"],
                            })
                        st.dataframe(_xt_rows, width='stretch', hide_index=True)

                with _cs_tab_gui_jian:
                    from astro.chinstar.chinstar import (
                        lookup_gui_ge, lookup_jian_ge,
                        lookup_fulu_patterns, lookup_pinjian_patterns,
                    )

                    # 取主要禽星（胎星、命星）
                    _gj_stars = [s["tai_xing"], s["ming_xing"]]
                    if s["shen_xing"] not in _gj_stars:
                        _gj_stars.append(s["shen_xing"])

                    # ── 福祿上格 ──
                    st.markdown(t("chinstar_fulu_title"))
                    _fulu_found = False
                    for _gj_star in _gj_stars:
                        _fl = lookup_fulu_patterns(_gj_star)
                        if _fl:
                            _fulu_found = True
                            for _fl_e in _fl:
                                st.success(f'**{_fl_e["name"]}**（{_fl_e["stars"]}）— {_fl_e["condition"]}')
                    if not _fulu_found:
                        st.info("—")
                    st.divider()

                    # ── 貧賤下命 ──
                    st.markdown(t("chinstar_pinjian_title"))
                    _pj_found = False
                    for _gj_star in _gj_stars:
                        _pj = lookup_pinjian_patterns(_gj_star)
                        if _pj:
                            _pj_found = True
                            for _pj_e in _pj:
                                st.error(f'**{_pj_e["name"]}**（{_pj_e["stars"]}）— {_pj_e["condition"]}')
                    if not _pj_found:
                        st.info("—")
                    st.divider()

                    # ── 各星貴格 / 賤格 ──
                    for _gj_star in _gj_stars:
                        st.markdown(t("chinstar_gui_for_star").format(star=_gj_star))
                        _gui = lookup_gui_ge(_gj_star)
                        if _gui:
                            _gui_rows = [{"格局": g["name"], "干支": g["ganzhi"]} for g in _gui]
                            st.dataframe(_gui_rows, width='stretch', hide_index=True)
                        else:
                            st.info(t("chinstar_no_gui"))

                        st.markdown(t("chinstar_jian_for_star").format(star=_gj_star))
                        _jian = lookup_jian_ge(_gj_star)
                        if _jian:
                            _jian_rows = [{"格局": j["name"], "干支": j["ganzhi"]} for j in _jian]
                            st.dataframe(_jian_rows, width='stretch', hide_index=True)
                        else:
                            st.info(t("chinstar_no_jian"))
                        st.divider()

            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            # Manual input fallback or not calculated
            st.markdown(t("desc_chinstar"))
            if not _is_calculated:
                st.info(t("info_calc_prompt"))
            else:
                st.subheader(t("chinstar_lunar_input_header"))
                _cs_col1, _cs_col2, _cs_col3 = st.columns(3)
                with _cs_col1:
                    _chinstar_year = st.number_input(
                        t("chinstar_lunar_year"), value=int(_chinstar_year),
                        min_value=1, max_value=2200, key="cs_year",
                    )
                with _cs_col2:
                    _chinstar_month = st.number_input(
                        t("chinstar_lunar_month"), value=int(_chinstar_month),
                        min_value=1, max_value=12, key="cs_month",
                    )
                with _cs_col3:
                    _chinstar_day = st.number_input(
                        t("chinstar_lunar_day"), value=int(_chinstar_day),
                        min_value=1, max_value=30, key="cs_day",
                    )
                if st.button(t("calculate_btn"), key="chinstar_calc_btn"):
                    try:
                        with st.spinner(t("spinner_chinstar")):
                            _cs_tool = WanHuaXianQin()
                            _cs_chart = _cs_tool.build_chart(
                                year=int(_chinstar_year),
                                month=int(_chinstar_month),
                                day=int(_chinstar_day),
                                hour=int(_chinstar_hour),
                                gender=_cs_gender,
                            )

                        _cs_tab_chart, _cs_tab_xiangtai, _cs_tab_gui_jian = st.tabs([
                            t("chinstar_subtab_chart"),
                            t("chinstar_subtab_xiangtai"),
                            t("chinstar_subtab_gui_jian"),
                        ])

                        with _cs_tab_chart:
                            from astro.chinstar.chinstar import BRANCHES as _cs_branches, QIN_ELEMENT as _cs_qin_elem
                            st.code(WanHuaXianQin.format_chart(_cs_chart), language="")
                    except Exception as _e:
                        st.error(f"{t('error_tab_compute')}：{_e}")
                        st.exception(_e)

    # --- 大六壬 (Da Liu Ren) ---
    elif _selected_system == "tab_liuren":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_liuren")):
                    _liuren_chart = compute_liuren_chart(**_p)
                # 從生年推算本命地支（年支）
                import sxtwl as _sxtwl_lr
                _lr_day = _sxtwl_lr.fromSolar(_p["year"], _p["month"], _p["day"])
                _lr_year_gz = _lr_day.getYearGZ()
                _lr_benming = list("子丑寅卯辰巳午未申酉戌亥")[_lr_year_gz.dz]
                render_liuren_chart(
                    _liuren_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_liuren", _liuren_chart, btn_key="liuren"
                    ),
                    benming_zhi=_lr_benming,
                )
                # ── 論命分析 ──
                st.divider()
                # 本命與流年均取自排盤年份的年支
                _lunming_report = compute_lunming(
                    _liuren_chart, _lr_benming, liunian_zhi=_lr_benming,
                )
                render_lunming_report(_lunming_report)
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_liuren"))

    # --- 鬼谷分定經 (Ghost Valley Fen Ding Jing) ---
    elif _selected_system == "tab_fendjing":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_fendjing") if hasattr(t, "spinner_fendjing") else "計算鬼谷分定經..."):
                    from astro.fendjing import compute_fendjing_chart, render_fendjing_chart
                    _fendjing_chart = compute_fendjing_chart(**_p)
                render_fendjing_chart(
                    _fendjing_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_fendjing", _fendjing_chart, btn_key="fendjing"
                    ),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_fendjing") if hasattr(t, "desc_fendjing") else "🔮 **鬼谷分定經** — 相傳為戰國時期鬼谷子所創，又名兩頭鉗，以出生年時天干排盤，配合十二宮與星曜，推斷一生命運的古典命理系統。")

    # --- 土亭數 (Tojeong Shu) ---
    elif _selected_system == "tab_tojeong":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                _g = st.session_state["_calc_gender"]
                _tojeong_gender = "male" if _g in ("male", "男", "M") else "female"
                # compute_tojeong_chart only accepts: year, month, day, hour, gender, solar_term
                _tojeong_params = {k: v for k, v in _p.items() if k in ("year", "month", "day", "hour")}
                with st.spinner(t("spinner_tojeong") if hasattr(t, "spinner_tojeong") else "計算土亭數..."):
                    from astro.tojeong import compute_tojeong_chart, render_tojeong_chart
                    _tojeong_chart = compute_tojeong_chart(**_tojeong_params, gender=_tojeong_gender)
                render_tojeong_chart(
                    _tojeong_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_tojeong", _tojeong_chart, btn_key="tojeong"
                    ),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.markdown("""
    <div style="
        background:linear-gradient(135deg,#0f1e35 0%,#1a0d28 100%);
        border:1px solid rgba(201,168,76,0.35);
        border-radius:16px;
        padding:28px 24px 24px 24px;
        margin-bottom:20px;
        text-align:center;
    ">
      <div role="img" aria-label="韓國國旗" style="font-size:52px;margin-bottom:10px;">🇰🇷</div>
      <div style="font-size:22px;font-weight:700;color:#C9A84C;letter-spacing:2px;margin-bottom:8px;">
        土亭數命盤
      </div>
      <div style="font-size:13px;color:#8888aa;line-height:1.7;max-width:380px;margin:0 auto 18px auto;">
        朝鮮時代土亭李先生所創的占數系統<br>
        以先天數、後天數計算格局代碼<br>
        查 129 格局斷語推斷吉凶
      </div>
      <div style="
        display:inline-block;
        background:rgba(205,46,58,0.15);
        border:1px solid rgba(205,46,58,0.4);
        border-radius:8px;
        padding:8px 20px;
        font-size:13px;
        color:#f87171;
      ">👈 請在左側填寫出生年月日時，即可起盤</div>
    </div>""", unsafe_allow_html=True)

    # --- 高棉占星 (Khmer Astrology / Reamker) ---
    elif _selected_system == "tab_khmer":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                _g = st.session_state["_calc_gender"]
                _khmer_gender = "male" if _g in ("male", "男", "M") else "female"
                _age = _p.get("age", 2026 - _p.get("year", 1995))
                with st.spinner(t("spinner_khmer") if hasattr(t, "spinner_khmer") else "計算高棉占星盤..."):
                    from astro.khmer import ReamkerAstrology, render_khmer_chart
                    astro = ReamkerAstrology()
                    _khmer_chart = astro.full_reading(
                        birth_year=_p.get("year", 1995),
                        gender=_khmer_gender,
                        current_age=_age,
                        language=st.session_state.get("lang", "zh")
                    )
                # Render chart via components.v1.html for full CSS/flexbox support
                _khmer_lang = st.session_state.get("lang", "zh")
                _khmer_html = render_khmer_chart(_khmer_chart, language=_khmer_lang)
                _render_interactive_html(
                    html=f'<div style="width:100%;font-family:\'Noto Sans\',\'Khmer OS\',Arial,sans-serif">{_khmer_html}</div>',
                    height=1050,
                    key="khmer-main-svg",
                )
                # AI interpretation button
                _render_ai_button("tab_khmer", _khmer_chart, btn_key="khmer")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_khmer") if hasattr(t, "desc_khmer") else "🇰🇭 **高棉占星** — 基於 François Bizot 2013 年論文與 Prochom Horasastra，重建吳哥時期失傳的 Reamker 占星系統。")

    # --- 太乙命法 (Taiyi Life Method) ---
    elif _selected_system == "tab_taiyi":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                _g = st.session_state["_calc_gender"]
                _taiyi_gender = "male" if _g in ("male", "男", "M") else "female"
                with st.spinner(t("spinner_taiyi")):
                    _taiyi_chart = compute_taiyi_chart(**_p, gender=_taiyi_gender)
                render_taiyi_chart(
                    _taiyi_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_taiyi", _taiyi_chart, btn_key="taiyi"
                    ),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_taiyi"))

    # --- 奇門祿命 (Qi Men Destiny Analysis) ---
    elif _selected_system == "tab_qimen_luming":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_qimen_luming")):
                    _qm_luming = compute_qimen_luming(**_p)
                render_qimen_luming(
                    _qm_luming,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_qimen_luming", _qm_luming, btn_key="qimen_luming"
                    ),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_qimen_luming"))
    elif _selected_system == "tab_acg":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_acg")):
                    _acg_result = compute_astrocartography(**_p)

                st.markdown(f"### {t('acg_title')}")

                _acg_tab_map, _acg_tab_table, _acg_tab_transit = st.tabs([
                    t("acg_subtab_map"),
                    t("acg_subtab_table"),
                    t("acg_subtab_transit"),
                ])

                # ── Sub-tab 1: 互動地圖 Interactive Map ──
                with _acg_tab_map:
                    import plotly.graph_objects as go

                    # Planet & line type filters
                    _acg_col1, _acg_col2 = st.columns(2)
                    with _acg_col1:
                        _acg_planets = st.multiselect(
                            t("acg_planet_filter"),
                            options=list(ACG_PLANETS.keys()),
                            default=["Sun", "Moon", "Venus", "Mars", "Jupiter"],
                            key="acg_planet_sel",
                        )
                    with _acg_col2:
                        _acg_lines = st.multiselect(
                            t("acg_line_filter"),
                            options=["AC", "MC", "IC", "DC"],
                            default=["AC", "MC", "IC", "DC"],
                            key="acg_line_sel",
                        )

                    # Build Plotly map
                    _acg_fig = go.Figure()

                    # Line dash patterns for each line type
                    _acg_dashes = {"AC": "solid", "MC": "dash", "IC": "dot", "DC": "dashdot"}

                    for _planet in _acg_planets:
                        _planet_data = _acg_result.lines.get(_planet, {})
                        _glyph = PLANET_GLYPHS.get(_planet, "")
                        _p_color = ACG_PLANET_COLORS.get(_planet, "#888")

                        for _lt in _acg_lines:
                            _pts = _planet_data.get(_lt, [])
                            if not _pts:
                                continue

                            _lons = [p[0] for p in _pts]
                            _lats = [p[1] for p in _pts]

                            # Get meaning for hover
                            _meaning = _acg_result.meanings.get(_planet, {}).get(_lt, "")

                            _acg_fig.add_trace(go.Scattergeo(
                                lon=_lons,
                                lat=_lats,
                                mode="lines",
                                line=dict(
                                    color=_p_color,
                                    width=2,
                                    dash=_acg_dashes.get(_lt, "solid"),
                                ),
                                name=f"{_planet} {_glyph} {_lt}",
                                hovertemplate=(
                                    f"<b>{_planet} {_glyph} {_lt}</b><br>"
                                    f"經度: %{{lon:.1f}}°<br>"
                                    f"緯度: %{{lat:.1f}}°<br>"
                                    f"<i>{_meaning[:40]}</i>"
                                    "<extra></extra>"
                                ),
                            ))

                    # Add Paran points as markers
                    if _acg_result.parans:
                        _paran_lons = [p.longitude for p in _acg_result.parans[:50]]
                        _paran_lats = [p.latitude for p in _acg_result.parans[:50]]
                        _paran_texts = [
                            f"{p.planet1} {p.line_type1} × {p.planet2} {p.line_type2}"
                            for p in _acg_result.parans[:50]
                        ]

                        _acg_fig.add_trace(go.Scattergeo(
                            lon=_paran_lons,
                            lat=_paran_lats,
                            mode="markers",
                            marker=dict(
                                size=8,
                                color="#FFD700",
                                symbol="star",
                                line=dict(width=1, color="#333"),
                            ),
                            text=_paran_texts,
                            name="Paran ✦",
                            hovertemplate=(
                                "<b>Paran 交叉點</b><br>"
                                "%{text}<br>"
                                "經度: %{lon:.1f}°, 緯度: %{lat:.1f}°"
                                "<extra></extra>"
                            ),
                        ))

                    # Add birth location marker
                    _acg_fig.add_trace(go.Scattergeo(
                        lon=[_p["longitude"]],
                        lat=[_p["latitude"]],
                        mode="markers+text",
                        marker=dict(size=12, color="#e74c3c", symbol="diamond"),
                        text=[_p.get("location_name", "Birth")],
                        textposition="top center",
                        name="出生地 Birth",
                        hovertemplate=(
                            "<b>出生地</b><br>"
                            f"{_p.get('location_name', '')}<br>"
                            f"經度: {_p['longitude']:.2f}°, 緯度: {_p['latitude']:.2f}°"
                            "<extra></extra>"
                        ),
                    ))

                    _acg_fig.update_geos(
                        showcountries=True,
                        countrycolor="rgba(100,100,100,0.3)",
                        showcoastlines=True,
                        coastlinecolor="rgba(150,150,150,0.4)",
                        showland=True,
                        landcolor="rgba(30,30,50,0.8)",
                        showocean=True,
                        oceancolor="rgba(20,20,40,0.9)",
                        showlakes=False,
                        projection_type="natural earth",
                        bgcolor="rgba(0,0,0,0)",
                    )

                    _acg_fig.update_layout(
                        height=550,
                        margin=dict(l=0, r=0, t=30, b=0),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=10),
                        ),
                        geo=dict(bgcolor="rgba(0,0,0,0)"),
                    )

                    st.plotly_chart(_acg_fig, width="stretch")

                    # Legend
                    _legend_cols = st.columns(4)
                    _legend_items = [
                        ("acg_line_ac", ACG_LINE_COLORS["AC"], "solid"),
                        ("acg_line_mc", ACG_LINE_COLORS["MC"], "dashed"),
                        ("acg_line_ic", ACG_LINE_COLORS["IC"], "dotted"),
                        ("acg_line_dc", ACG_LINE_COLORS["DC"], "dashdot"),
                    ]
                    for _col, (_key, _color, _style) in zip(_legend_cols, _legend_items):
                        with _col:
                            st.markdown(
                                f'<div style="display:flex;align-items:center;gap:6px;">'
                                f'<div style="width:24px;height:3px;background:{_color};'
                                f'border-style:{_style};"></div>'
                                f'<span style="font-size:12px;">{t(_key)}</span></div>',
                                unsafe_allow_html=True,
                            )

                    # Paran section
                    if _acg_result.parans:
                        with st.expander(t("acg_paran_header"), expanded=False):
                            import pandas as pd
                            _paran_rows = []
                            for _pr in _acg_result.parans[:30]:
                                _paran_rows.append({
                                    "行星1": f"{_pr.planet1} {PLANET_GLYPHS.get(_pr.planet1, '')}",
                                    "線型1": _pr.line_type1,
                                    "行星2": f"{_pr.planet2} {PLANET_GLYPHS.get(_pr.planet2, '')}",
                                    "線型2": _pr.line_type2,
                                    "緯度": f"{_pr.latitude:.1f}°",
                                    "經度": f"{_pr.longitude:.1f}°",
                                })
                            if _paran_rows:
                                st.dataframe(pd.DataFrame(_paran_rows), hide_index=True, width="stretch")

                    # AI button
                    _render_ai_button("tab_acg", _acg_result, btn_key="acg_map",
                                      page_content=format_acg_for_prompt(_acg_result))

                # ── Sub-tab 2: 行星線資料表 Planet Line Data Table ──
                with _acg_tab_table:
                    import pandas as pd
                    st.subheader(t("acg_subtab_table"))

                    _table_rows = []
                    for _planet_name, _line_dict in _acg_result.lines.items():
                        _glyph = PLANET_GLYPHS.get(_planet_name, "")
                        for _lt in ("AC", "MC", "IC", "DC"):
                            _pts = _line_dict.get(_lt, [])
                            _meaning = _acg_result.meanings.get(_planet_name, {}).get(_lt, "")
                            if _pts:
                                _mid = len(_pts) // 2
                                _table_rows.append({
                                    "行星 Planet": f"{_planet_name} {_glyph}",
                                    "線型 Type": _lt,
                                    "黃經 Lon": f"{_acg_result.planet_longitudes.get(_planet_name, 0):.2f}°",
                                    "代表經度 Geo Lon": f"{_pts[_mid][0]:.1f}°",
                                    "點數 Points": len(_pts),
                                    "解釋 Meaning": _meaning,
                                })
                    if _table_rows:
                        st.dataframe(pd.DataFrame(_table_rows), hide_index=True, width="stretch")

                    _render_ai_button("tab_acg", _acg_result, btn_key="acg_table",
                                      page_content=format_acg_for_prompt(_acg_result))

                # ── Sub-tab 3: 流年搬遷線 Transit ACG ──
                with _acg_tab_transit:
                    st.subheader(t("acg_subtab_transit"))

                    _tr_col1, _tr_col2 = st.columns(2)
                    with _tr_col1:
                        _tr_date = st.date_input(
                            t("acg_transit_date"),
                            value=datetime.now().date(),
                            key="acg_tr_date",
                        )
                    with _tr_col2:
                        _tr_time = st.time_input(
                            t("acg_transit_time"),
                            value=time(12, 0),
                            key="acg_tr_time",
                        )

                    # Year slider for quick navigation
                    _tr_year_slider = st.slider(
                        "Year / 年份",
                        min_value=1950,
                        max_value=2050,
                        value=_tr_date.year,
                        key="acg_tr_year_slider",
                    )

                    # Compute transit ACG
                    with st.spinner(t("spinner_acg")):
                        _tr_acg = compute_astrocartography_transit(
                            natal_year=_p["year"], natal_month=_p["month"],
                            natal_day=_p["day"], natal_hour=_p["hour"],
                            natal_minute=_p["minute"], natal_timezone=_p["timezone"],
                            transit_year=_tr_year_slider,
                            transit_month=_tr_date.month,
                            transit_day=_tr_date.day,
                            transit_hour=_tr_time.hour,
                            transit_minute=_tr_time.minute,
                            transit_timezone=_p["timezone"],
                        )

                    # Transit map
                    import plotly.graph_objects as go
                    _tr_fig = go.Figure()

                    _tr_planets_sel = st.multiselect(
                        t("acg_planet_filter"),
                        options=list(ACG_PLANETS.keys()),
                        default=["Sun", "Moon", "Jupiter", "Saturn"],
                        key="acg_tr_planet_sel",
                    )
                    _tr_dashes = {"AC": "solid", "MC": "dash", "IC": "dot", "DC": "dashdot"}

                    for _planet in _tr_planets_sel:
                        _planet_data = _tr_acg.lines.get(_planet, {})
                        _glyph = PLANET_GLYPHS.get(_planet, "")
                        _p_color = ACG_PLANET_COLORS.get(_planet, "#888")

                        for _lt in ("AC", "MC", "IC", "DC"):
                            _pts = _planet_data.get(_lt, [])
                            if not _pts:
                                continue
                            _lons = [p[0] for p in _pts]
                            _lats = [p[1] for p in _pts]

                            _tr_fig.add_trace(go.Scattergeo(
                                lon=_lons,
                                lat=_lats,
                                mode="lines",
                                line=dict(color=_p_color, width=2,
                                          dash=_tr_dashes.get(_lt, "solid")),
                                name=f"{_planet} {_glyph} {_lt} (Transit)",
                            ))

                    _tr_fig.update_geos(
                        showcountries=True,
                        countrycolor="rgba(100,100,100,0.3)",
                        showcoastlines=True,
                        coastlinecolor="rgba(150,150,150,0.4)",
                        showland=True,
                        landcolor="rgba(30,30,50,0.8)",
                        showocean=True,
                        oceancolor="rgba(20,20,40,0.9)",
                        projection_type="natural earth",
                        bgcolor="rgba(0,0,0,0)",
                    )
                    _tr_fig.update_layout(
                        height=500,
                        margin=dict(l=0, r=0, t=30, b=0),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                                    xanchor="center", x=0.5, font=dict(size=10)),
                        geo=dict(bgcolor="rgba(0,0,0,0)"),
                    )

                    st.plotly_chart(_tr_fig, width="stretch")

                    _render_ai_button("tab_acg", _tr_acg, btn_key="acg_transit",
                                      page_content=format_acg_for_prompt(_tr_acg))

            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_acg"))

    # --- 天王星派占星 (Uranian / Hamburg School) ---
    elif _selected_system == "tab_uranian":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_uranian")):
                    _uranian_result = compute_uranian_chart(**_p)
                render_uranian_chart(_uranian_result)
                _render_ai_button("tab_uranian", _uranian_result, btn_key="uranian")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_uranian"))
    elif _selected_system == "tab_cosmobiology":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_cosmobiology")):
                    _cosmo_result = compute_cosmobiology_chart(**_p)
                render_cosmobiology(_cosmo_result)
                _render_ai_button("tab_cosmobiology", _cosmo_result, btn_key="cosmobiology")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_cosmobiology"))
    elif _selected_system == "tab_harmonic":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_harmonic")):
                    _harmonic_result = compute_multi_harmonic(**_p)
                render_harmonic(_harmonic_result)
                _render_ai_button("tab_harmonic", _harmonic_result, btn_key="harmonic")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_harmonic"))
    elif _selected_system == "tab_primary_directions":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_primary_directions")):
                    _pd_result = compute_primary_directions(**_p)
                render_primary_directions(_pd_result)
                _render_ai_button("tab_primary_directions", _pd_result, btn_key="primary_directions")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_primary_directions_prompt"))
            st.markdown(t("desc_primary_directions"))
    elif _selected_system == "tab_wariga":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_wariga")):
                    _wariga_result = compute_wariga(
                        year=_p["year"], month=_p["month"], day=_p["day"],
                        hour=_p["hour"], minute=_p["minute"],
                        lat=_p["latitude"], lon=_p["longitude"],
                    )
                render_wariga_chart(_wariga_result)
                _render_ai_button("tab_wariga", _wariga_result, btn_key="wariga")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_wariga"))

    elif _selected_system == "tab_jawa_weton":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_jawa_weton")):
                    _jawa_result = compute_weton(
                        year=_p["year"], month=_p["month"], day=_p["day"],
                        hour=_p["hour"], minute=_p["minute"],
                        location_name=_p.get("location_name", ""),
                        timezone=_p.get("timezone", 7.0),
                    )
                render_jawa_weton_chart(_jawa_result)
                _render_ai_button("tab_jawa_weton", _jawa_result, btn_key="jawa_weton")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_jawa_weton"))

    elif _selected_system == "tab_bintang_duabelas":
        try:
            _default_birth_datetime = None
            if _is_calculated:
                _p = st.session_state["_calc_params"]
                _default_birth_datetime = datetime(
                    _p["year"],
                    _p["month"],
                    _p["day"],
                    _p["hour"],
                    _p["minute"],
                )
            st.info(t("info_bintang_duabelas_prompt"))
            with st.spinner(t("spinner_bintang_duabelas")):
                render_bintang_duabelas_chart(_default_birth_datetime)
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

    elif _selected_system == "tab_kinketika":
        try:
            _default_birth_datetime = None
            if _is_calculated:
                _p = st.session_state["_calc_params"]
                _default_birth_datetime = datetime(
                    _p["year"],
                    _p["month"],
                    _p["day"],
                    _p["hour"],
                    _p["minute"],
                )
            st.info(t("info_kinketika_prompt"))
            with st.spinner(t("spinner_kinketika")):
                _kinketika_report = render_kinketika_chart(_default_birth_datetime)
            _render_ai_button("tab_kinketika", _kinketika_report, btn_key="kinketika")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

    elif _selected_system == "tab_polynesian":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_polynesian")):
                    _poly_result = compute_polynesian_chart(
                        year=_p["year"], month=_p["month"], day=_p["day"],
                        hour=_p["hour"], minute=_p["minute"],
                        lat=_p.get("latitude", 21.3),
                        lon=_p.get("longitude", -157.8),
                        timezone_offset=_p.get("timezone", 0.0),
                        location_name=_p.get("location_name", ""),
                    )
                render_polynesian_chart_ui(_poly_result)
                _render_ai_button("tab_polynesian", _poly_result, btn_key="polynesian")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_polynesian"))

    # --- 出生時間校正 Birth Chart Rectification ---
    elif _selected_system == "tab_rectification":
        _p = st.session_state.get("_calc_params", {})
        render_rectification_page(
            default_date=(
                date(_p["year"], _p["month"], _p["day"])
                if _p else None
            ),
            default_lat=_p.get("latitude", 22.3193),
            default_lon=_p.get("longitude", 114.1694),
            default_tz=_p.get("timezone", 8.0),
        )

    # --- 赫密士出生前世盤 Trutine of Hermes / Prenatal Epoch ---
    elif _selected_system == "tab_trutine_of_hermes":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                render_trutine_chart(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p.get("minute", 0),
                    timezone=_p.get("timezone", 0.0),
                    latitude=_p.get("latitude", 25.033),
                    longitude=_p.get("longitude", 121.565),
                    location_name=_p.get("location_name", ""),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_trutine_of_hermes_prompt"))
            st.markdown(t("desc_trutine_of_hermes"))

    # --- 六爻終身卦 Lifetime Liu Yao Hexagram ---
    elif _selected_system == "tab_liuyao_lifetime":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_liuyao_lifetime")):
                    _liuyao_result = compute_lifetime_hexagram(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p["minute"],
                        location_name=_p.get("location_name", ""),
                    )
                render_liuyao_lifetime_chart(_liuyao_result)
                _render_ai_button("tab_liuyao_lifetime", _liuyao_result, btn_key="liuyao_lifetime")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_liuyao_lifetime"))

    # --- 拜占庭占星 Byzantine Astrology ---
    elif _selected_system == "tab_byzantine_astrology":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                render_byzantine_astrology_chart(
                    year=_p["year"],
                    month=_p["month"],
                    day=_p["day"],
                    hour=_p["hour"],
                    minute=_p.get("minute", 0),
                    timezone=_p.get("timezone", 0.0),
                    latitude=_p.get("latitude", 41.016),
                    longitude=_p.get("longitude", 28.977),
                    location_name=_p.get("location_name", ""),
                )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_byzantine_astrology_prompt"))
            st.markdown(t("desc_byzantine_astrology"))

    # --- 醫學占星 Medical Astrology (Iatromathematics) ---
    elif _selected_system == "tab_medical_astrology":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_medical_astrology")):
                    _medical_result = compute_medical_chart(**_p)
                render_medical_astrology_chart(_medical_result)
                _render_ai_button("tab_medical_astrology", _medical_result, btn_key="medical_astrology")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_medical_astrology_prompt"))
            st.markdown(t("desc_medical_astrology"))

    elif _selected_system == "tab_shanghan_qianfa":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_shanghan_qianfa")):
                    _shanghan_result = compute_shanghan_qianfa(**_p)
                render_shanghan_qianfa_chart(_shanghan_result)
                _render_ai_button("tab_shanghan_qianfa", _shanghan_result, btn_key="shanghan_qianfa")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_shanghan_qianfa_prompt"))
            st.markdown(t("desc_shanghan_qianfa"))

    # --- 北極神數 (Beiji Shenshu) ---
    elif _selected_system == "tab_beiji":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_beiji")):
                    render_beiji_chart(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p["minute"],
                        gender=st.session_state.get("_calc_gender", "男"),
                    )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_beiji_prompt"))
            st.markdown(t("desc_beiji"))

    # --- 南極神數 Nanji Shenshu ---
    elif _selected_system == "tab_nanji":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_nanji")):
                    render_nanji_chart(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p.get("minute", 0),
                        gender=st.session_state.get("_calc_gender", "男"),
                    )
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_nanji_prompt"))
            st.markdown(t("desc_nanji"))

    # --- 子平八字 Ziping Bazi ---
    elif _selected_system == "tab_bazi":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_bazi")):
                    _bazi_result = compute_bazi_chart(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p["minute"],
                        gender=st.session_state.get("_calc_gender", "男"),
                        timezone=_p.get("timezone", 8.0),
                        latitude=_p.get("latitude", 25.033),
                        longitude=_p.get("longitude", 121.565),
                        location_name=_p.get("location_name", ""),
                    )
                render_bazi_chart(_bazi_result)
                _render_ai_button("tab_bazi", _bazi_result, btn_key="bazi")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_bazi_prompt"))
            st.markdown(t("desc_bazi"))

    # --- 蠢子數纏度 ChunZiShu ---
    elif _selected_system == "tab_chunzi":
        try:
            with st.spinner(t("spinner_chunzi")):
                render_chunzi_chart()
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

    # --- 開元占經 Kaiyuan Zhanjing ---
    elif _selected_system == "tab_kaiyuan":
        try:
            with st.spinner(t("spinner_kaiyuan")):
                render_kaiyuan_chart()
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

    # ============================================================
    # --- 傳統卜卦占星 Traditional Horary Astrology ---
    elif _selected_system == "tab_horary":
        _p = st.session_state.get("_calc_params", {})
        try:
            render_horary_chart(
                year=_p.get("year", 2024),
                month=_p.get("month", 1),
                day=_p.get("day", 1),
                hour=_p.get("hour", 12),
                minute=_p.get("minute", 0),
                timezone=_p.get("tz", 0.0),
                latitude=_p.get("lat", 25.033),
                longitude=_p.get("lon", 121.565),
                location_name=_p.get("location_name", ""),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    elif _selected_system == "tab_sports_astrology":
        _p = st.session_state.get("_calc_params", {})
        try:
            render_sports_astrology_chart(
                year=_p.get("year", 2024),
                month=_p.get("month", 1),
                day=_p.get("day", 1),
                hour=_p.get("hour", 12),
                minute=_p.get("minute", 0),
                timezone=_p.get("tz", 0.0),
                latitude=_p.get("lat", 25.033),
                longitude=_p.get("lon", 121.565),
                location_name=_p.get("location_name", ""),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    elif _selected_system == "tab_esoteric":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_esoteric")):
                    _esoteric_result = compute_esoteric_chart(**_p)
                render_esoteric_chart(_esoteric_result)
                _render_ai_button("tab_esoteric", _esoteric_result, btn_key="esoteric")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_esoteric_prompt"))
            st.markdown(t("desc_esoteric"))

    # ============================================================
    # --- 人間圖 Human Design ---
    elif _selected_system == "tab_human_design":
        if _is_calculated:
            try:
                _p = st.session_state["_calc_params"]
                with st.spinner(t("spinner_human_design")):
                    _hd_result = compute_human_design_chart(
                        year=_p["year"],
                        month=_p["month"],
                        day=_p["day"],
                        hour=_p["hour"],
                        minute=_p["minute"],
                        timezone=_p.get("timezone", 8.0),
                        latitude=_p.get("latitude", 25.033),
                        longitude=_p.get("longitude", 121.565),
                        location_name=_p.get("location_name", ""),
                    )
                render_human_design_chart(_hd_result)
                _render_ai_button("tab_human_design", _hd_result, btn_key="human_design")
            except Exception as _e:
                st.error(f"{t('error_tab_compute')}：{_e}")
                st.exception(_e)
        else:
            st.info(t("info_human_design_prompt"))
            st.markdown(t("desc_human_design"))

    # ============================================================
    # --- 擇日占星 Electional Astrology / Vedic Muhurta ---
    elif _selected_system == "tab_electional":
        _p = st.session_state.get("_calc_params", {})
        try:
            render_electional_chart(
                year=_p.get("year", 2024),
                month=_p.get("month", 1),
                day=_p.get("day", 1),
                hour=_p.get("hour", 12),
                minute=_p.get("minute", 0),
                timezone=_p.get("tz", 0.0),
                latitude=_p.get("lat", 25.033),
                longitude=_p.get("lon", 121.565),
                location_name=_p.get("location_name", ""),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

    # ============================================================
    # --- 世俗占星 Mundane Astrology ---
    elif _selected_system == "tab_mundane":
        try:
            _p = st.session_state.get("_calc_params", {})
            render_mundane_chart(
                year=_p.get("year"),
                month=_p.get("month"),
                day=_p.get("day"),
                hour=_p.get("hour"),
                minute=_p.get("minute"),
                timezone=_p.get("timezone"),
                latitude=_p.get("latitude"),
                longitude=_p.get("longitude"),
                location_name=_p.get("location_name", ""),
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

    # ============================================================
    # --- 地占占星 Astronomical Geomancy ---
    elif _selected_system == "tab_astro_geomancy":
        try:
            _geo_key = "geo_chart_result"
            _geo_input = _render_geomancy_input()
            if _geo_input is not None:
                # User submitted a new question — recompute
                with st.spinner(t("spinner_astro_geomancy")):
                    _geo_chart = _compute_geomancy_chart(
                        question=_geo_input["question"],
                        question_type=_geo_input["question_type"],
                        seed_mode=_geo_input["seed_mode"],
                        mode=_geo_input.get("mode", "horary"),
                        layout=_geo_input.get("layout", "square"),
                    )
                st.session_state[_geo_key] = _geo_chart
            if _geo_key in st.session_state:
                _geo_chart = st.session_state[_geo_key]
                _render_geomancy_ui(
                    _geo_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_astro_geomancy", _geo_chart, btn_key="astro_geomancy"
                    ),
                )
            else:
                st.info(t("info_astro_geomancy_prompt"))
                st.markdown(t("desc_astro_geomancy"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

    elif _selected_system == "tab_european_geomancy":
        try:
            with st.spinner(t("spinner_european_geomancy")):
                render_european_geomancy(
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_european_geomancy",
                        st.session_state.get("_eg_reading"),
                        btn_key="european_geomancy",
                    )
                )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

    # ── 弗拉德命運輪盤 ──
    elif _selected_system == "tab_fludd_rota":
        try:
            _fludd_auto_cfg = None
            if _is_calculated:
                try:
                    _p = st.session_state["_calc_params"]
                    with st.spinner(t("spinner_fludd_rota")):
                        _fw = compute_western_chart(**_p)
                    def _planet_lon(_name_prefix: str) -> float | None:
                        for _pl in _fw.planets:
                            if _pl.name.startswith(_name_prefix):
                                return _pl.longitude
                        return None
                    _lons = {
                        k: _planet_lon(v)
                        for k, v in [
                            ("sun", "Sun"), ("moon", "Moon"),
                            ("mercury", "Mercury"), ("venus", "Venus"),
                            ("mars", "Mars"), ("jupiter", "Jupiter"),
                            ("saturn", "Saturn"),
                        ]
                    }
                    _nn_lon = _planet_lon("North Node")
                    # Only build auto_config when all required planets are present
                    if all(v is not None for v in _lons.values()) and _nn_lon is not None:
                        _fludd_auto_cfg = _fludd_config_from_dict({
                            **_lons,
                            "ascendant": _fw.ascendant,
                            "north_node": _nn_lon,
                            "south_node": (_nn_lon + 180.0) % 360.0,
                        })
                except Exception as _fludd_err:
                    import logging as _logging
                    _logging.getLogger(__name__).warning(
                        "Fludd Rota auto-config failed: %s", _fludd_err
                    )
            render_fludd_rota(
                auto_config=_fludd_auto_cfg,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_fludd_rota",
                    st.session_state.get("fludd_rota_reading"),
                    btn_key="fludd_rota",
                )
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

    # ============================================================
    # --- 煉金占星 Alchemical Astrology (Paracelsus tradition) ---
    elif _selected_system == "tab_alchemical_astrology":
        try:
            _alch_lons: dict | None = None
            if _is_calculated:
                with st.spinner(t("spinner_alchemical_astrology")):
                    _alch_fw = compute_western_chart(**st.session_state["_calc_params"])
                # pl.name format in WesternChart is "<PlanetName> [retrograde]"
                # split()[0] extracts the planet name reliably (e.g. "Sun", "Moon")
                _alch_lons = {
                    pl.name.split()[0].lower(): pl.longitude
                    for pl in _alch_fw.planets
                    if pl.name.split()[0] in {
                        "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"
                    }
                }
            render_alchemical_tab(
                planet_longitudes=_alch_lons,
                after_chart_hook=lambda: _render_ai_button(
                    "tab_alchemical_astrology",
                    st.session_state.get("alchemical_reading"),
                    btn_key="alchemical_astrology",
                ) if _is_calculated else None,
            )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)

# ── Global AI chatbox — fixed at the bottom of every page ──────────────────
_render_global_ai_chat()
