"""
i18n.py — Internationalisation strings for Kin Astro
Supports: 繁體中文 (zh), 簡體中文 (zh_cn), and English (en)
"""

TRANSLATIONS = {
    # ── App title / subtitle ────────────────────────────────────────────────
    "app_title": {
        "zh": "⭐ 堅占星 Kin Astro",
        "en": "⭐ Kin Astro",
    },
    "app_subtitle": {
        "zh": "✨ 輸入你的出生資料，一鍵了解你的命運走向",
        "en": "✨ Enter your birth info and discover your destiny in one click",
    },
    # ── Sidebar ─────────────────────────────────────────────────────────────
    "sidebar_header": {
        "zh": "📝 你的出生資料",
        "en": "📝 Your Birth Info",
    },
    "date_time": {
        "zh": "出生日期和時間",
        "en": "Birth Date & Time",
    },
    "birth_date": {
        "zh": "出生日期",
        "en": "Birth Date",
    },
    "birth_time": {
        "zh": "出生時間",
        "en": "Birth Time",
    },
    "birth_location": {
        "zh": "你在哪裡出生？",
        "en": "Where were you born?",
    },
    "city_preset": {
        "zh": "城市",
        "en": "City",
    },
    "latitude": {
        "zh": "緯度",
        "en": "Latitude",
    },
    "longitude": {
        "zh": "經度",
        "en": "Longitude",
    },
    "timezone": {
        "zh": "時區 (UTC)",
        "en": "Timezone (UTC)",
    },
    "custom": {
        "zh": "自訂",
        "en": "Custom",
    },
    "custom_location": {
        "zh": "自訂地點",
        "en": "Custom Location",
    },
    "region_label": {
        "zh": "地區",
        "en": "Region",
    },
    "birth_year": {
        "zh": "年",
        "en": "Year",
    },
    "birth_month": {
        "zh": "月",
        "en": "Month",
    },
    "birth_day": {
        "zh": "日",
        "en": "Day",
    },
    "birth_hour": {
        "zh": "時",
        "en": "Hour",
    },
    "birth_minute": {
        "zh": "分",
        "en": "Minute",
    },
    "region_hk_macau": {
        "zh": "港澳",
        "en": "HK / Macau",
    },
    "region_taiwan": {
        "zh": "台灣",
        "en": "Taiwan",
    },
    "region_mainland_south": {
        "zh": "華南",
        "en": "South China",
    },
    "region_mainland_east": {
        "zh": "華東",
        "en": "East China",
    },
    "region_mainland_north": {
        "zh": "華北 / 東北",
        "en": "North / Northeast China",
    },
    "region_mainland_central": {
        "zh": "華中",
        "en": "Central China",
    },
    "region_mainland_west": {
        "zh": "西部",
        "en": "West China",
    },
    "region_japan_korea": {
        "zh": "日本 / 韓國",
        "en": "Japan / Korea",
    },
    "region_southeast_asia": {
        "zh": "東南亞",
        "en": "Southeast Asia",
    },
    "region_south_asia": {
        "zh": "南亞",
        "en": "South Asia",
    },
    "region_middle_east": {
        "zh": "中東",
        "en": "Middle East",
    },
    "region_africa": {
        "zh": "非洲",
        "en": "Africa",
    },
    "region_europe": {
        "zh": "歐洲",
        "en": "Europe",
    },
    "region_north_america": {
        "zh": "北美洲",
        "en": "North America",
    },
    "region_south_america": {
        "zh": "南美洲",
        "en": "South America",
    },
    "region_oceania": {
        "zh": "大洋洲 / 太平洋",
        "en": "Oceania / Pacific",
    },
    "region_russia_central_asia": {
        "zh": "俄羅斯 / 中亞",
        "en": "Russia / Central Asia",
    },
    "region_custom": {
        "zh": "自訂",
        "en": "Custom",
    },
    "calculate_btn": {
        "zh": "🔮 開始排盤",
        "en": "🔮 Calculate Chart",
    },
    # ── Birth data form ──────────────────────────────────────────────────────
    "generate_chart_btn": {
        "zh": "🌟 生成命盤",
        "en": "🌟 Generate Chart",
    },
    "form_validation_date": {
        "zh": "⚠️ 請輸入有效的出生日期",
        "en": "⚠️ Please enter a valid birth date",
    },
    "form_validation_location": {
        "zh": "⚠️ 自訂地點：緯度需在 −90°~90°，經度需在 −180°~180°",
        "en": "⚠️ Custom location: latitude must be −90°~90°, longitude −180°~180°",
    },
    "form_hint_custom_coords": {
        "zh": "請填入自訂座標",
        "en": "Enter custom coordinates",
    },
    # ── Main navigation tabs ─────────────────────────────────────────────────
    "main_tab_natal": {
        "zh": "🌟 本命盤",
        "en": "🌟 Natal Chart",
    },
    "main_tab_transit": {
        "zh": "📅 流年 / 大運 / 過運",
        "en": "📅 Transits / Progressions",
    },
    "main_tab_ai": {
        "zh": "🤖 AI 深度解讀",
        "en": "🤖 AI Analysis",
    },
    "main_tab_compare": {
        "zh": "🔄 跨體系比較",
        "en": "🔄 Cross-system Comparison",
    },
    "main_tab_electional": {
        "zh": "📆 擇日工具",
        "en": "📆 Electional Tools",
    },
    "main_tab_relocation": {
        "zh": "🗺️ 地圖與 Relocation",
        "en": "🗺️ Map & Relocation",
    },
    # ── Transit quick-panel (main tab 2) ─────────────────────────────────────
    "transit_tab_hint": {
        "zh": "💡 過運（流年）功能已整合在各體系的子分頁中。請先從左側選擇體系，再切換至「流年過運」子頁籤。",
        "en": "💡 Transit features are available within each system's sub-tabs. Select a system from the sidebar, then switch to the 'Transits' sub-tab.",
    },
    "transit_quick_title": {
        "zh": "西洋占星快速過運查詢",
        "en": "Western Astrology Quick Transit Lookup",
    },
    # ── Cross-system comparison tab ──────────────────────────────────────────
    "compare_tab_hint": {
        "zh": "💡 請在左側側邊欄啟用「跨體系比較」開關，並選擇任意體系查看命盤。",
        "en": "💡 Enable the 'Cross-system Comparison' toggle in the sidebar, then select any system to view the multi-system synthesis.",
    },
    # ── Share chart ──────────────────────────────────────────────────────────
    "share_chart_btn": {
        "zh": "🔗 複製分享連結",
        "en": "🔗 Copy Share Link",
    },
    "share_chart_copied": {
        "zh": "✅ 分享連結已複製至剪貼簿！",
        "en": "✅ Share link copied to clipboard!",
    },
    "share_chart_hint": {
        "zh": "分享此連結可讓他人直接開啟你的命盤設定",
        "en": "Share this link to let others open your chart settings directly",
    },
    "share_chart_loaded": {
        "zh": "✅ 已從分享連結載入命盤資料",
        "en": "✅ Chart loaded from shared link",
    },
    "gender_header": {
        "zh": "性別",
        "en": "Gender",
    },
    "gender_label": {
        "zh": "你的性別",
        "en": "Your Gender",
    },
    "male": {
        "zh": "男命",
        "en": "Male",
    },
    "female": {
        "zh": "女命",
        "en": "Female",
    },
    # ── City names ───────────────────────────────────────────────────────────
    "city_beijing": {"zh": "北京", "en": "Beijing"},
    "city_shanghai": {"zh": "上海", "en": "Shanghai"},
    "city_hongkong": {"zh": "香港", "en": "Hong Kong"},
    "city_taipei": {"zh": "台北", "en": "Taipei"},
    "city_tokyo": {"zh": "東京", "en": "Tokyo"},
    "city_seoul": {"zh": "首爾", "en": "Seoul"},
    "city_singapore": {"zh": "新加坡", "en": "Singapore"},
    "city_london": {"zh": "倫敦", "en": "London"},
    "city_newyork": {"zh": "紐約", "en": "New York"},
    "city_yangon": {"zh": "仰光", "en": "Yangon"},
    "city_ulaanbaatar": {"zh": "烏蘭巴托", "en": "Ulaanbaatar"},
    # ── Tab labels ───────────────────────────────────────────────────────────
    "tab_chinese": {
        "zh": "🀄 七政四餘",
        "en": "🀄 Qi Zheng Si Yu (Chinese Astrology)",
    },
    "tab_ziwei": {
        "zh": "🌟 紫微斗數",
        "en": "🌟 Zi Wei Dou Shu",
    },
    "tab_western": {
        "zh": "🌍 西洋占星",
        "en": "🌍 Western Astrology",
    },
    "tab_indian": {
        "zh": "🙏 印度占星",
        "en": "🙏 Indian Astrology",
    },
    "tab_vastu": {
        "zh": "🪔 吠陀風水",
        "en": "🪔 Vastu Shastra",
    },
    "tab_sukkayodo": {
        "zh": "🈳 日本宿曜道",
        "en": "🈳 Sukkayodo",
    },
    "tab_thai": {
        "zh": "🐘 泰國占星",
        "en": "🐘 Thai Astrology",
    },
    "tab_laos": {
        "zh": "🇱🇦 老撾占星（ໄທຣາສາດລາວ）",
        "en": "🇱🇦 Laos Horasat",
    },
    "tab_kabbalistic": {
        "zh": "✡ 卡巴拉占星",
        "en": "✡ Kabbalistic Astrology",
    },
    "tab_arabic": {
        "zh": "☪ 阿拉伯占星",
        "en": "☪ Arabic Astrology",
    },
    "tab_maya": {
        "zh": "🏺 瑪雅占星",
        "en": "🏺 Maya Astrology",
    },
    "tab_dogon_sirius": {
        "zh": "🜂 多貢天狼星宇宙學",
        "en": "🜂 Dogon Sirius Cosmology",
    },
    "tab_aztec": {
        "zh": "🦅 阿茲特克占星",
        "en": "🦅 Aztec Astrology",
    },
    "tab_mahabote": {
        "zh": "🇲🇲 緬甸／撣族 Mahabote",
        "en": "🇲🇲 Burmese/Shan Mahabote",
    },
    "tab_wariga": {
        "zh": "🏝️ 巴厘 Wariga",
        "en": "🏝️ Balinese Wariga",
    },
    "tab_jawa_weton": {
        "zh": "🏺 爪哇 Weton / Primbon",
        "en": "🏺 Javanese Weton / Primbon",
    },
    "tab_bintang_duabelas": {
        "zh": "⭐ 馬來伊斯蘭占星（十二星）",
        "en": "⭐ Bintang Duabelas (Twelve Stars)",
    },
    "tab_kinketika": {
        "zh": "🌙 馬來七星五刻占卜",
        "en": "🌙 Kinketika (Malay Time Divination)",
    },
    "tab_polynesian": {
        "zh": "🌺 波利尼西亞／夏威夷星辰知識",
        "en": "🌺 Polynesian / Hawaiian Star Lore",
    },
    "tab_andean": {
        "zh": "⛰️ 印加／安地斯占星",
        "en": "⛰️ Inca / Andean Astrology",
    },
    "tab_decans": {
        "zh": "🏛️ 古埃及十度區間",
        "en": "🏛️ Egyptian Decans",
    },
    "tab_nadi": {
        "zh": "🔱 印度納迪占星",
        "en": "🔱 Nadi Jyotish",
    },
    "tab_zurkhai": {
        "zh": "🇲🇳 蒙古祖爾海",
        "en": "🇲🇳 Mongolian Zurkhai",
    },
    "tab_jaimini": {
        "zh": "🕉️ 闍彌尼占星",
        "en": "🕉️ Jaimini Astrology",
    },
    "tab_picatrix": {
        "zh": "📜 Picatrix 星體魔法",
        "en": "📜 Picatrix Stellar Magic",
    },
    "tab_shams": {
        "zh": "☪ 太陽知識大全",
        "en": "☪ Shams al-Maʻārif",
    },
    # ── Arabic sub-tab labels ─────────────────────────────────────────────────
    "arabic_subtab_chart": {
        "zh": "☪ 阿拉伯占星",
        "en": "☪ Arabic Astrology",
    },
    "arabic_subtab_lots": {
        "zh": "🧿 Al-Biruni 97 阿拉伯點",
        "en": "🧿 Al-Biruni 97 Lots",
    },
    "arabic_subtab_picatrix": {
        "zh": "📜 Picatrix 星體魔法",
        "en": "📜 Picatrix Stellar Magic",
    },
    "arabic_subtab_invocation": {
        "zh": "🕯️ 靈體召喚（Picatrix）",
        "en": "🕯️ Spirit Invocation (Picatrix)",
    },
    "arabic_subtab_shams": {
        "zh": "☪ 太陽知識大全",
        "en": "☪ Shams al-Maʻārif",
    },
    "arabic_subtab_reference": {"zh": "古籍知識庫", "en": "Reference Library"},
    "arabic_subtab_ms164": {"zh": "📜 MS.164 手稿", "en": "📜 MS.164 Manuscript"},
    # ── Chinese (七政四餘) sub-tab labels ──────────────────────────────────────
    "ch_subtab_natal": {
        "zh": "🎯 本命盤",
        "en": "🎯 Natal Chart",
    },
    "ch_subtab_shensha": {
        "zh": "🔮 神煞",
        "en": "🔮 Shen Sha",
    },
    "ch_subtab_dasha": {
        "zh": "📅 年限大運",
        "en": "📅 Planetary Periods",
    },
    "ch_subtab_transit": {
        "zh": "🔄 流時對盤",
        "en": "🔄 Transit Chart",
    },
    "ch_subtab_zhangguo": {
        "zh": "📜 張果星宗",
        "en": "📜 Zhang Guo Star Readings",
    },
    "show_transit_overlay": {
        "zh": "在圓盤上顯示流時星曜",
        "en": "Show transit planets on ring chart",
    },
    "transit_header": {
        "zh": "🔄 流時對盤",
        "en": "🔄 Transit Chart Comparison",
    },
    "transit_date": {
        "zh": "流時日期",
        "en": "Transit date",
    },
    "transit_time": {
        "zh": "流時時間",
        "en": "Transit time",
    },
    "transit_tz": {
        "zh": "流時時區",
        "en": "Transit TZ",
    },
    # ── Spinner messages ──────────────────────────────────────────────────────
    "spinner_indian": {
        "zh": "正在計算印度占星排盤...",
        "en": "Calculating Indian astrology chart...",
    },
    "spinner_jaimini": {
        "zh": "正在計算 Jaimini 占星排盤...",
        "en": "Calculating Jaimini astrology chart...",
    },
    "spinner_chinese": {
        "zh": "正在計算七政四餘位置...",
        "en": "Calculating Seven Governors chart...",
    },
    "spinner_ziwei": {
        "zh": "正在計算紫微斗數命盤...",
        "en": "Calculating Zi Wei Dou Shu chart...",
    },
    "spinner_western": {
        "zh": "正在計算西洋占星排盤...",
        "en": "Calculating Western astrology chart...",
    },
    "spinner_thai": {
        "zh": "正在計算泰國占星排盤...",
        "en": "Calculating Thai astrology chart...",
    },
    "spinner_laos": {
        "zh": "正在計算老撾占星排盤...",
        "en": "Calculating Laos Horasat chart...",
    },
    "spinner_kabbalistic": {
        "zh": "正在計算卡巴拉占星排盤...",
        "en": "Calculating Kabbalistic astrology chart...",
    },
    "spinner_arabic": {
        "zh": "正在計算阿拉伯占星排盤...",
        "en": "Calculating Arabic astrology chart...",
    },
    "spinner_arabic_lots": {
        "zh": "正在計算 Al-Biruni 97 阿拉伯點...",
        "en": "Calculating Al-Biruni 97 Arabic Lots...",
    },
    "spinner_maya": {
        "zh": "正在計算瑪雅占星排盤...",
        "en": "Calculating Maya astrology chart...",
    },
    "spinner_dogon_sirius": {
        "zh": "正在計算多貢天狼星宇宙學...",
        "en": "Calculating Dogon Sirius cosmology...",
    },
    "spinner_aztec": {
        "zh": "正在計算阿茲特克占星排盤...",
        "en": "Calculating Aztec astrology chart...",
    },
    "spinner_mahabote": {
        "zh": "正在計算緬甸 Mahabote 排盤...",
        "en": "Calculating Myanmar Mahabote chart...",
    },
    "spinner_wariga": {
        "zh": "正在計算巴厘 Wariga 日曆...",
        "en": "Calculating Balinese Wariga calendar...",
    },
    "spinner_jawa_weton": {
        "zh": "正在計算爪哇 Weton 排盤...",
        "en": "Calculating Javanese Weton chart...",
    },
    "spinner_bintang_duabelas": {
        "zh": "正在整理馬來伊斯蘭占星（Bintang Duabelas）工具...",
        "en": "Preparing Malay Islamic astrology (Bintang Duabelas) tools...",
    },
    "spinner_kinketika": {
        "zh": "正在計算馬來七星五刻占卜（Kinketika）...",
        "en": "Computing Kinketika (Malay Time Divination)...",
    },
    "spinner_polynesian": {
        "zh": "正在計算夏威夷星辰排盤...",
        "en": "Calculating Hawaiian Star Lore chart...",
    },
    "spinner_andean": {
        "zh": "正在計算印加天河暗星宿排盤...",
        "en": "Calculating Inca / Andean Mayu chart...",
    },
    "spinner_decans": {
        "zh": "正在計算古埃及十度區間排盤...",
        "en": "Calculating Egyptian Decans chart...",
    },
    "spinner_nadi": {
        "zh": "正在計算納迪占星排盤...",
        "en": "Calculating Nadi Jyotish chart...",
    },
    "spinner_zurkhai": {
        "zh": "正在計算蒙古祖爾海排盤...",
        "en": "Calculating Mongolian Zurkhai chart...",
    },
    # ── Sidereal checkbox ──────────────────────────────────────────────────
    "sidereal_label": {
        "zh": "🌟 使用恆星黃道 (Sidereal Zodiac / Lahiri Ayanamsa)",
        "en": "🌟 Use Sidereal Zodiac (Lahiri Ayanamsa)",
    },
    "sidereal_help": {
        "zh": "恆星黃道以實際星座位置計算，含歲差修正（印度占星用同一體系）",
        "en": "Sidereal zodiac calculates with actual star positions including precession correction (same system used in Indian astrology)",
    },
    # ── Sukkayodo subheader & info ────────────────────────────────────────
    "sukkayodo_subheader": {
        "zh": "🈳 日本宿曜道 (Yojōdō)",
        "en": "🈳 Japanese Sukkayodo (Yojōdō)",
    },
    "sukkayodo_info": {
        "zh": "宿曜道建基於印度占星排盤，請至「🙏 印度占星」分頁查看完整印度占星排盤。",
        "en": "Sukkayodo is based on Indian astrology. See the '🙏 Indian Astrology' tab for the full Vedic chart.",
    },
    # ── Thai sub-tab labels ────────────────────────────────────────────────
    "thai_subtab_chart": {
        "zh": "🐘 ผังดวงชาตา (占星排盤)",
        "en": "🐘 ผังดวงชาตา (Astrology Chart)",
    },
    "thai_subtab_nine": {
        "zh": "🔮 ตาราง 9 ช่อง & 九宮占卜 (9宮格數字學 · 九宮占卜)",
        "en": "🔮 9-Palace Grid & Divination (Numerology · Divination)",
    },
    "thai_subtab_brahma": {
        "zh": "📖 พรหมชาติ (泰國命理)",
        "en": "📖 Brahma Jati (Thai Fate Reading)",
    },
    "thai_nakshatra_title": {
        "zh": "🌙 นักษัตร — Moon Nakshatra (月亮宿)",
        "en": "🌙 นักษัตร — Moon Nakshatra",
    },
    "thai_omens_title": {
        "zh": "🔮 คำทำนายตามวันเกิด (日主星預兆)",
        "en": "🔮 Day Planet Omens (คำทำนายตามวันเกิด)",
    },
    "thai_mandala_title": {
        "zh": "🪷 ผังดวงมณฑลทอง (金色曼荼羅排盤)",
        "en": "🪷 Thai Gold Mandala Chart",
    },
    "thai_brahma_jati_color": {
        "zh": "📿 พรหมชาติ — 吉色與補救",
        "en": "📿 Brahma Jati — Lucky Colours & Remedies",
    },
    # ── Picatrix section ───────────────────────────────────────────────────
    "picatrix_subheader": {
        "zh": "📜 Picatrix 星體魔法 (Picatrix Stellar Magic)",
        "en": "📜 Picatrix Stellar Magic",
    },
    "picatrix_source": {
        "zh": (
            "資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim) — "
            "Greer & Warnock 2011 translation / Attrell & Porreca 2019"
        ),
        "en": (
            "Source: Picatrix (Ghayat al-Hakim) — "
            "Greer & Warnock 2011 translation / Attrell & Porreca 2019"
        ),
    },
    "picatrix_subtab_mansion": {
        "zh": "🌙 月宿查詢器",
        "en": "🌙 Mansion Lookup",
    },
    "picatrix_subtab_hours": {
        "zh": "⏰ 行星時計算器",
        "en": "⏰ Planetary Hours",
    },
    "picatrix_subtab_talisman": {
        "zh": "🔮 護符生成器",
        "en": "🔮 Talisman Generator",
    },
    "picatrix_subtab_browse": {
        "zh": "📚 Picatrix 參考總覽",
        "en": "📚 Picatrix Reference",
    },
    "picatrix_talisman_subheader": {
        "zh": "🔮 護符生成器（無需排盤）",
        "en": "🔮 Talisman Generator (no chart needed)",
    },
    # ── "Please calculate" info messages ───────────────────────────────────
    "info_decans_prompt": {
        "zh": (
            "👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕查看個人十度區間排盤。"
            "下方可先瀏覽古埃及 36 Decans 總覽。"
        ),
        "en": (
            "👈 Enter birth data on the left and click 'Calculate Chart' to view your personal Decans chart. "
            "Browse all 36 Egyptian Decans below."
        ),
    },
    "info_picatrix_prompt": {
        "zh": (
            "👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕查看個人月宿排盤。"
            "下方可先瀏覽 Picatrix 28 月宿完整參考。"
        ),
        "en": (
            "👈 Enter birth data on the left and click 'Calculate Chart' to view your personal Moon Mansion chart. "
            "Browse all 28 Picatrix Mansions below."
        ),
    },
    "shams_subheader": {
        "zh": "☪ 《太陽知識大全》 (Shams al-Maʻārif al-Kubrā)",
        "en": "☪ Shams al-Maʻārif al-Kubrā",
    },
    "shams_source": {
        "zh": "資料來源：《Shams al-Maʻārif al-Kubrā wa Laṭāʼif al-ʻAwārif》— 1927 McGill 版",
        "en": "Source: Shams al-Maʻārif al-Kubrā wa Laṭāʼif al-ʻAwārif — 1927 McGill edition",
    },
    # ── Tab description markdown ────────────────────────────────────────────
    "desc_chinese": {
        "zh": """
### 什麼是七政四餘？

**七政四餘**是中國傳統占星術的核心體系：

- **七政（日月五星）**：太陽、太陰（月亮）、水星、金星、火星、木星、土星
- **四餘（虛星）**：羅睺（北交點）、計都（南交點）、月孛（平均遠地點）、紫氣

本系統使用 **pyswisseph**（瑞士星曆表）進行精確的天文計算，
提供星曜的黃經位置、所在星次、二十八宿對應、十二宮位分布等資訊。
""",
        "en": """
### What are the Seven Governors (七政四餘)?

The **Seven Governors and Four Remainders** form the core of traditional Chinese astrology:

- **Seven Governors (Sun, Moon & Five Planets)**: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn
- **Four Remainders (Virtual Stars)**: Rāhu (North Node), Ketu (South Node), Moon Apogee, Purple Vapour

This system uses **pyswisseph** (Swiss Ephemeris) for precise astronomical calculations,
providing planetary longitudes, lunar mansion correspondences, and twelve-house distributions.
""",
    },
    "desc_ziwei": {
        "zh": """
### 什麼是紫微斗數？

**紫微斗數**是中國傳統命理學最重要的排盤體系之一，相傳由五代末宋初的
**陳希夷**（陳摶）整理創立：

- **十四主星**：紫微（帝王星）、天機、太陽、武曲、天同、廉貞（紫微六系）；
  天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍（天府八系）
- **十二宮位**：命宮、兄弟宮、夫妻宮、子女宮、財帛宮、疾厄宮、
  遷移宮、交友宮、官祿宮、田宅宮、福德宮、父母宮
- **五行局**：由命宮天干決定，分水二、木三、金四、土五、火六局，
  影響紫微星安星方式
- **農曆排盤**：以農曆生辰（年、月、日、時辰）為基礎
""",
        "en": """
### What is Zi Wei Dou Shu (紫微斗數)?

**Zi Wei Dou Shu** is one of the most important Chinese fortune-telling systems,
traditionally attributed to **Chen Xiyi** (Chen Tuan) of the late Five Dynasties / early Song period:

- **14 Major Stars**: Zi Wei (Emperor Star), Tian Ji, Tai Yang, Wu Qu, Tian Tong, Lian Zhen (Zi Wei group);
  Tian Fu, Tai Yin, Tan Lang, Ju Men, Tian Xiang, Tian Liang, Qi Sha, Po Jun (Tian Fu group)
- **12 Palaces**: Life, Siblings, Spouse, Children, Wealth, Health,
  Travel, Friends, Career, Property, Virtue, Parents
- **Five-Element Bureau**: Determined by the Life Palace heavenly stem; Water-2, Wood-3, Gold-4, Earth-5, Fire-6
- **Lunar Calendar**: Based on lunar birth year, month, day, and hour
""",
    },
    "desc_western": {
        "zh": """
### 什麼是西洋占星？

**西洋占星**使用回歸黃道（Tropical Zodiac）計算行星位置：

- **行星**：太陽、月亮、水星、金星、火星、木星、土星、天王星、海王星、冥王星
- **十二星座**：白羊座至雙魚座
- **宮位制**：Placidus 等分宮制
- **相位**：合、沖、刑、三合、六合等
""",
        "en": """
### What is Western Astrology?

**Western Astrology** uses the Tropical Zodiac to calculate planetary positions:

- **Planets**: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
- **12 Signs**: Aries through Pisces
- **House System**: Placidus equal house system
- **Aspects**: Conjunction, opposition, square, trine, sextile, etc.
""",
    },
    "desc_indian": {
        "zh": """
### 什麼是印度占星 (Jyotish)？

**印度占星**使用恆星黃道（Sidereal Zodiac）搭配 Lahiri 歲差：

- **九曜 (Navagraha)**：太陽、月亮、火星、水星、木星、金星、土星、羅睺、計都
- **十二星座 (Rashi)**：Mesha 至 Meena
- **二十七宿 (Nakshatra)**：Ashwini 至 Revati，每宿分四足 (Pada)
- **南印度式方盤 (South Indian Chart)**
- **七曜管宿**：每顆曜主管 3 個 Nakshatra，構成 27 宿體系

| 曜 | 主宿 |
|:--:|:-----|
| Sun | Krittika、Uttara Phalguni、Uttara Ashadha |
| Moon | Rohini、Hasta、Shravana |
| Mars | Mrigashira、Chitra、Dhanishta |
| Mercury | Ashlesha、Jyeshtha、Revati |
| Jupiter | Punarvasu、Vishakha、Purva Bhadrapada |
| Venus | Bharani、Purva Phalguni、Purva Ashadha |
| Saturn | Pushya、Anuradha、Uttara Bhadrapada |
| Rahu | Ardra、Swati、Shatabhisha |
| Ketu | Ashwini、Magha、Mula |
""",
        "en": """
### What is Indian Astrology (Jyotish)?

**Jyotish** uses the Sidereal Zodiac with the Lahiri ayanamsa:

- **Nine Planets (Navagraha)**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
- **12 Signs (Rashi)**: Mesha through Meena
- **27 Lunar Mansions (Nakshatra)**: Ashwini through Revati, each divided into 4 Padas
- **South Indian Chart** style
- **Planetary Rulerships**: Each planet rules 3 Nakshatras

| Planet | Ruled Nakshatras |
|:------:|:-----------------|
| Sun | Krittika, Uttara Phalguni, Uttara Ashadha |
| Moon | Rohini, Hasta, Shravana |
| Mars | Mrigashira, Chitra, Dhanishta |
| Mercury | Ashlesha, Jyeshtha, Revati |
| Jupiter | Punarvasu, Vishakha, Purva Bhadrapada |
| Venus | Bharani, Purva Phalguni, Purva Ashadha |
| Saturn | Pushya, Anuradha, Uttara Bhadrapada |
| Rahu | Ardra, Swati, Shatabhisha |
| Ketu | Ashwini, Magha, Mula |
""",
    },
    "desc_jaimini": {
        "zh": """
### 什麼是 Jaimini 占星？

**Jaimini 占星**源自古印度聖人 Jaimini 的《Jaimini Sutras》，與 Parashara 體系並列為印度 Jyotish 兩大核心流派：

- **Chara Karaka（可變徵象星）**：7 顆行星依度數高低動態分配角色（AK、AmK、BK、MK、PK、GK、DK）
- **Rashi Drishti（星座視線）**：整個星座之間的相互視線，活動座 ↔ 固定座互視，雙體座之間互視
- **Argala（介入）與 Virodhargala（阻擋）**：分析宮位間的干預效果
- **Arudha Pada（虛象宮）**：反映外在世界對命主的感知
- **Chara Dasha（可變大運）**：以星座為單位的獨特大運系統
- **Sthira Karaka（固定徵象星）**：每顆行星永遠代表固定的主題

| Karaka | 中文 | 代表意義 |
|:------:|:----:|:---------|
| AK | 靈魂徵象星 | 自我、靈魂目的 |
| AmK | 大臣徵象星 | 事業、職業 |
| BK | 兄弟徵象星 | 兄弟姐妹、勇氣 |
| MK | 母親徵象星 | 母親、不動產 |
| PK | 子女徵象星 | 子女、智慧 |
| GK | 敵人徵象星 | 疾病、障礙 |
| DK | 配偶徵象星 | 婚姻、伴侶 |
""",
        "en": """
### What is Jaimini Astrology?

**Jaimini Astrology** originates from the ancient Indian sage Jaimini's *Jaimini Sutras*, standing alongside the Parashara system as one of the two core Jyotish traditions:

- **Chara Karaka (Variable Significators)**: 7 planets dynamically assigned roles (AK, AmK, BK, MK, PK, GK, DK) based on degrees
- **Rashi Drishti (Sign Aspects)**: Whole-sign aspects — Cardinal ↔ Fixed signs aspect each other, Dual signs aspect each other
- **Argala & Virodhargala**: Intervention and obstruction analysis between houses
- **Arudha Pada**: Reflects how the external world perceives the native
- **Chara Dasha**: Unique sign-based dasha (timing) system
- **Sthira Karaka (Fixed Significators)**: Each planet permanently represents fixed themes

| Karaka | Full Name | Signification |
|:------:|:----------|:-------------|
| AK | Atmakaraka | Self, soul purpose |
| AmK | Amatyakaraka | Career, profession |
| BK | Bhratrukaraka | Siblings, courage |
| MK | Matrukaraka | Mother, property |
| PK | Putrakaraka | Children, wisdom |
| GK | Gnatikaraka | Disease, obstacles |
| DK | Darakaraka | Marriage, partner |
""",
    },
    "desc_sukkayodo": {
        "zh": """
### 什麼是宿曜道？

**宿曜道**由空海大師於 9 世紀自印度傳入日本，是融合佛密與道教的占星體系：

- **二十八宿 (Nakshatra)**：比印度 Jyotish 多出 **Abhijit（牛宿）**，共 28 宿
- **六曜 (Rokuyō)**：先勝・友引・先負・仏滅・大安・赤口，由 **Moon 所在宿** 決定
- **宿曜道方盤**：以 Moon 為中心，二十八宿沿圓環排列

宿曜道可用於擇日、占卜日常生活中各類事務的吉凶。
""",
        "en": """
### What is Sukkayodo (宿曜道)?

**Sukkayodo** was brought to Japan from India by Master Kukai in the 9th century,
blending Esoteric Buddhism and Taoist astrology:

- **28 Lunar Mansions (Nakshatra)**: Includes **Abhijit (牛宿)** not found in Indian Jyotish, totalling 28
- **Six Day Cycle (Rokuyō)**: Sensho, Tomobiki, Senbu, Butsumetsu, Taian, Shakko — determined by the Moon's mansion
- **Sukkayodo Wheel Chart**: Moon at centre, 28 mansions arranged in a ring

Sukkayodo is used for date selection and divination of auspiciousness in daily life matters.
""",
    },
    "desc_thai": {
        "zh": """
### 什麼是泰國占星？

**泰國占星**以印度 Jyotish 為基礎，融合泰國傳統文化：

- **九曜**：太陽、月亮、火星、水星、木星、金星、土星、羅睺、計都
- **十二星座 (ราศี)**：使用泰語命名的恆星黃道星座
- **日主星 (ดาวประจำวัน)**：根據出生星期判定守護星
- **泰式方盤 (ผังดวงชาตา)**
""",
        "en": """
### What is Thai Astrology?

**Thai Astrology** is based on Indian Jyotish, blended with Thai traditional culture:

- **Nine Planets**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
- **12 Signs (ราศี)**: Sidereal zodiac signs named in Thai
- **Day Ruler (ดาวประจำวัน)**: Guardian planet determined by day of birth
- **Thai Chart (ผังดวงชาตา)**
""",
    },
    "desc_laos": {
        "zh": """
### 什麼是老撾占星（ໄທຣາສາດລາວ）？

**老撾占星**承接南傳婆羅門—佛教曆法傳統，重視日期、時段與日常擇事：

- **老撾曆日期（ວັນ・ເດືອນ・ປີ）**
- **特殊年份（ປີອະທິກະ）**
- **ສັງຄົມ 吉凶擇日**
- **ສີກາດ 時段吉凶**
- **婆羅門占星輪（🌀）**
""",
        "en": """
### What is Laos Horasat (ໄທຣາສາດລາວ)?

**Laos Horasat** follows traditional Lao Brahmanic-Buddhist calendar astrology,
with emphasis on daily timing and practical electional guidance:

- Lao date system (day/month/year)
- Special year cycle analysis
- ສັງຄົມ auspiciousness tables
- ສີກາດ time-slot selection
- Brahman cosmic wheel (🌀)
""",
    },
    "desc_kabbalistic": {
        "zh": """
### 什麼是卡巴拉占星？

**卡巴拉占星**結合猶太神祕主義（Kabbalah）與占星術：

- **生命之樹 (Tree of Life)**：十個質點（Sephiroth）對應不同行星
- **希伯來字母**：22 個字母分別對應黃道星座與行星
- **塔羅對應**：每個星座對應一張塔羅大牌
- **回歸黃道 (Tropical Zodiac)**：使用西洋占星的回歸黃道系統
""",
        "en": """
### What is Kabbalistic Astrology?

**Kabbalistic Astrology** combines Jewish mysticism (Kabbalah) with astrology:

- **Tree of Life**: Ten Sephiroth corresponding to different planets
- **Hebrew Letters**: 22 letters corresponding to zodiac signs and planets
- **Tarot Correspondences**: Each sign corresponds to a Major Arcana card
- **Tropical Zodiac**: Uses the Western tropical zodiac system
""",
    },
    "desc_arabic": {
        "zh": """
### 什麼是阿拉伯占星？

**阿拉伯占星**源自中世紀伊斯蘭黃金時代，融合希臘與波斯天文傳統：

- **阿拉伯點 (Arabic Parts / Lots)**：透過上升點與行星經度加減運算，
  推導出幸運點、精神點、愛情點等各生活主題的敏感度數
- **日夜盤 (Sect)**：根據太陽位置區分日盤與夜盤，影響阿拉伯點公式
- **行星廟旺落陷 (Essential Dignities)**：入廟、入旺、落陷、入弱
- **回歸黃道 (Tropical Zodiac)**：使用 Placidus 宮位制
""",
        "en": """
### What is Arabic Astrology?

**Arabic Astrology** originated in the medieval Islamic Golden Age, blending Greek and Persian astronomical traditions:

- **Arabic Parts (Lots)**: Sensitive points derived by adding/subtracting the Ascendant and planetary longitudes —
  Fortune, Spirit, Love, and other life themes
- **Diurnal/Nocturnal Sect**: Whether Sun is above or below the horizon affects Arabic Part formulas
- **Essential Dignities**: Domicile, Exaltation, Fall, Detriment
- **Tropical Zodiac**: Uses Placidus house system
""",
    },
    "desc_arabic_lots": {
        "zh": """
### Al-Biruni 97 阿拉伯點（完整 Lots 引擎）

- 收錄 **97 個經典 Lots**：7 行星 Lots + 80 宮位 Lots + 10 專題 Lots  
- 核心公式：**Lot = Personal Point + Significator - Trigger**  
- 自動判斷 **日盤 / 夜盤（Sect）**，套用公式反轉  
- 支援 **Tropical / Sidereal** 雙黃道模式  
- 可依分類、關鍵字、宮位與優先級快速篩選
""",
        "en": """
### Al-Biruni 97 Arabic Lots (Complete Engine)

- Includes **97 classical Lots**: 7 planetary + 80 house-based + 10 special-topic lots  
- Core formula: **Lot = Personal Point + Significator - Trigger**  
- Automatic **day/night sect** detection with formula reversal  
- Supports both **Tropical and Sidereal** zodiac modes  
- Dashboard supports search, filtering, and priority-based sorting
""",
    },
    "arabic_lots_dashboard_title": {"zh": "Al-Biruni 97 阿拉伯點總覽", "en": "Al-Biruni 97 Lots Overview"},
    "arabic_lots_total_count": {"zh": "總數", "en": "Total"},
    "arabic_lots_sect": {"zh": "盤型", "en": "Sect"},
    "arabic_lots_day_chart": {"zh": "日盤", "en": "Day Chart"},
    "arabic_lots_night_chart": {"zh": "夜盤", "en": "Night Chart"},
    "arabic_lots_zodiac_mode": {"zh": "黃道模式", "en": "Zodiac Mode"},
    "arabic_lots_tropical": {"zh": "Tropical 回歸黃道", "en": "Tropical"},
    "arabic_lots_sidereal": {"zh": "Sidereal 恆星黃道", "en": "Sidereal"},
    "arabic_lots_search": {"zh": "搜尋 Lots", "en": "Search Lots"},
    "arabic_lots_search_placeholder": {
        "zh": "可搜尋中英阿文名稱、公式關鍵字",
        "en": "Search by Chinese/English/Arabic name or formula keyword",
    },
    "arabic_lots_filter_category": {"zh": "分類篩選", "en": "Category Filter"},
    "arabic_lots_category_planetary": {"zh": "行星 Lots", "en": "Planetary Lots"},
    "arabic_lots_category_houses": {"zh": "宮位 Lots", "en": "House Lots"},
    "arabic_lots_category_special": {"zh": "專題 Lots", "en": "Special Lots"},
    "arabic_lots_sort": {"zh": "排序", "en": "Sort"},
    "arabic_lots_sort_priority": {"zh": "依重要度", "en": "By Priority"},
    "arabic_lots_sort_longitude": {"zh": "依黃經", "en": "By Longitude"},
    "arabic_lots_sort_house": {"zh": "依宮位", "en": "By House"},
    "arabic_lots_sort_name": {"zh": "依名稱", "en": "By Name"},
    "arabic_lots_filtered_count": {"zh": "篩選後筆數", "en": "Filtered Rows"},
    "arabic_lots_col_name": {"zh": "Lot 名稱", "en": "Lot Name"},
    "arabic_lots_col_arabic": {"zh": "阿拉伯文", "en": "Arabic"},
    "arabic_lots_col_category": {"zh": "分類", "en": "Category"},
    "arabic_lots_col_formula": {"zh": "公式", "en": "Formula"},
    "arabic_lots_col_position": {"zh": "位置", "en": "Position"},
    "arabic_lots_col_house": {"zh": "宮位", "en": "House"},
    "arabic_lots_col_beneficence": {"zh": "吉凶", "en": "Beneficence"},
    "arabic_lots_col_priority": {"zh": "重要度", "en": "Priority"},
    "arabic_lots_top10_title": {"zh": "前 10 大重要 Lots", "en": "Top 10 Priority Lots"},
    "desc_maya": {
        "zh": """
### 什麼是瑪雅占星？

**瑪雅占星**源自瓜地馬拉瑪雅文明的天文與曆法傳統：

- **Long Count（長紀年）**：以 B'ak'tun、Ka'tun、Tu'n、Winal、K'in 計算天數
- **Tzolkin（神聖曆）**：260 天循環，13 數字 × 20 神明名
- **Haab（民用曆）**：365 天，18 月 × 20 日 + 5 Wayeb 無日
- **Calendar Round**：Tzolkin × Haab 同步循環，約 52 年一輪
- **行星疊加**：結合西方占星行星位置對應 Tzolkin 能量
""",
        "en": """
### What is Maya Astrology?

**Maya Astrology** draws from the astronomical and calendrical traditions of Guatemalan Maya civilisation:

- **Long Count**: Days counted in B'ak'tun, Ka'tun, Tu'n, Winal, K'in units
- **Tzolkin (Sacred Calendar)**: 260-day cycle — 13 numbers × 20 day signs
- **Haab (Civil Calendar)**: 365 days — 18 months × 20 days + 5 Wayeb nameless days
- **Calendar Round**: Tzolkin × Haab synchronised cycle, ~52 years per round
- **Planetary Overlay**: Western planetary positions mapped to Tzolkin energies
""",
    },
    "desc_andean": {
        "zh": """
### 什麼是印加／安地斯占星？

**安地斯占星**源自南美安第斯山脈前哥倫比亞文明（印加帝國 Tahuantinsuyu）與活態克丘亞語傳統。

#### 🌌 天河（Mayu）
銀河對安地斯人而言是神聖天河（Mayu / Hatun Mayu），連結三界：
- **Hanan Pacha**（上界 / 天界）
- **Kay Pacha**（此界 / 現世）
- **Uku Pacha**（下界 / 地底）

#### 🦙 暗星宿（Yana Phuyu / 陰雲星座）
安地斯「黃道」由銀河暗雲組成的動物靈魂構成，主要包括：
- **Qatachillay**（母駱馬與幼駱馬）—— 繁殖、雨季
- **Hamp'atu**（蟾蜍）—— 播種時機
- **Mach'aqway**（蛇）—— 轉化、三界通道
- **Atoq**（狐狸）—— 試煉、機智
- **Kuntur**（兀鷹）—— 祖靈、高瞻
- **Lluthu**（山鶉）—— 謙遜、日常勤勞
- **Michiq**（牧羊人）—— 秩序、守護

#### ⭐ 明星標記
- **Collca**（昴宿星團）—— 穀倉、農業新年
- **Chakana**（南十字座）—— 宇宙階梯、四方秩序
- **Orion 三星** —— 播種時機

#### 占星原則
無西方十二宮式出生盤；重視 **偕日出 / 偕日落**（heliacal rising/setting）、
天河位置、暗星宿可見性與季節農業預兆。
""",
        "en": """
### What is Inca / Andean Astrology?

**Andean Astrology** originates from the pre-Columbian civilisations of the South American Andes
(the Inca Empire, Tahuantinsuyu) and living Quechua oral traditions.

#### 🌌 Mayu (The Sacred Milky Way)
The Milky Way is a sacred river (Mayu / Hatun Mayu) connecting the three realms:
- **Hanan Pacha** (the upper / celestial world)
- **Kay Pacha** (this world / the present)
- **Uku Pacha** (the inner / lower world)

#### 🦙 Yana Phuyu (Dark Cloud Constellations)
The Andean "zodiac" is formed by living animal spirits in the dark-dust rifts of the Milky Way:
- **Qatachillay** (Llama & Baby Llama) — fertility, rainy season
- **Hamp'atu** (Toad) — sowing timing
- **Mach'aqway** (Serpent) — transformation, inter-world gateway
- **Atoq** (Fox) — trial, cunning
- **Kuntur** (Condor) — ancestral vision
- **Lluthu** (Partridge) — humility, daily labour
- **Michiq** (Shepherd) — order, guardianship

#### ⭐ Bright Markers
- **Collca** (Pleiades) — granary, agro-new-year marker
- **Chakana** (Southern Cross) — cosmic staircase, four-directional order
- **Orion's Belt** — sowing timing

#### Astrological Principles
No Western-style zodiac wheel; emphasis on **heliacal rising/setting**, Mayu position,
dark-cloud visibility, and seasonal agricultural omens.
""",
    },
    "desc_dogon_sirius": {
        "zh": """
### 什麼是多貢天狼星宇宙學？

**Dogon Sirius Cosmology** 以馬利多貢族口傳宇宙觀為核心，聚焦 Sirius（天狼星）相關傳統：

- **Sirius A / Sigu Tolo**：可見主星與儀式時間節律
- **Sirius B / Po Tolo**：高密度「種子」象徵
- **Sirius C / Emme Ya**：傳說性伴星，作為文化宇宙學敘事
- **Sigui 50 年週期**：對應社群更新與祖先記憶傳承節點
- **跨文化比較**：並列埃及、巴比倫、瑪雅等 Sirius 傳統

⚠️ 本模組將相關內容呈現為文化人類學語境（含學術爭議標註），
不主張其為現代天文學定論。
""",
        "en": """
### What is Dogon Sirius Cosmology?

**Dogon Sirius Cosmology** centers on Dogon (Mali) oral cosmic traditions around Sirius:

- **Sirius A / Sigu Tolo**: visible principal star and ritual timing anchor
- **Sirius B / Po Tolo**: dense “seed” symbol
- **Sirius C / Emme Ya**: lore-level companion in cosmological narrative
- **50-year Sigui cycle**: communal renewal and ancestral memory marker
- **Cross-cultural comparison**: parallels with Egyptian, Babylonian, and Maya Sirius emphasis

⚠️ This module presents the material as cultural anthropology (with contested claims clearly noted),
not as settled modern astronomical fact.
""",
    },
    "desc_aztec": {
        "zh": """
### 什麼是阿茲特克占星？

**阿茲特克占星**源自中美洲阿茲特克文明的天文與曆法傳統：

- **Tonalpohualli（神聖曆）**：260 天循環，13 數字 × 20 日徵（day signs）
- **Trecena（13天週期）**：每 13 天為一個能量週期，由第一天的日徵命名
- **守護神祇**：每個日徵對應特定的阿茲特克神祇
- **四方位與顏色**：東=紅、北=白、西=藍、南=黃
- **行星疊加**：結合西方占星行星位置對應 Tonalpohualli 能量

參考：https://www.azteccalendar.com/
""",
        "en": """
### What is Aztec Astrology?

**Aztec Astrology** draws from the astronomical and calendrical traditions of Mesoamerican Aztec civilisation:

- **Tonalpohualli (Sacred Calendar)**: 260-day cycle — 13 numbers × 20 day signs
- **Trecena (13-Day Period)**: Each 13-day period is named after its first day sign
- **Patron Deities**: Each day sign is associated with a specific Aztec deity
- **Four Directions & Colours**: East=Red, North=White, West=Blue, South=Yellow
- **Planetary Overlay**: Western planetary positions mapped to Tonalpohualli energies

Reference: https://www.azteccalendar.com/
""",
    },
    "desc_mahabote": {
        "zh": """
### 什麼是緬甸 Mahabote 占星？

**Mahabote** (မဟာဘုတ်) 是緬甸傳統占星術核心體系，意為「大創造」：

- **七曜行星 + 羅睺**：日、月、火、水、木、金、土 + 羅睺（星期三傍晚）
- **八方位輪盤**：NE、E、SE、S、SW、W、NW、N，每顆行星對應一個方位
- **八宮位**：本命、壽命、意識、身體、權勢、死亡、道德 + 業力（第八隱藏宮）
- **動物守護**：迦樓羅、虎、獅、象(有牙)、鼠、天竺鼠、龍/那伽、象(無牙)
- **行星大運 (Atar)**：七星循環共 96 年，主宰人生各階段
- **Sakka 曆計算**：Mahabote 值 = (Sakka 年 + 星期數) mod 8
- **傳統預兆**：每個方位含吉凶、事業、婚姻、健康解讀
""",
        "en": """
### What is Myanmar Mahabote Astrology?

**Mahabote** (မဟာဘုတ်) is the core traditional Myanmar astrology system, meaning "Great Creation":

- **Seven Planets + Rahu**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn + Rahu (Wednesday evening)
- **Eight-Direction Wheel**: NE, E, SE, S, SW, W, NW, N — each planet maps to a compass direction
- **Eight Houses**: Birth, Life, Mind, Body, Power, Death, Morality + Karma (8th hidden house)
- **Animal Guardians**: Garuda, Tiger, Lion, Tusked Elephant, Rat, Guinea Pig, Naga, Tuskless Elephant
- **Planetary Periods (Atar)**: Seven-planet cycle totalling 96 years
- **Sakka Calendar**: Mahabote value = (Sakka year + weekday number) mod 8
- **Traditional Omens**: Each direction includes fortune, career, marriage, and health readings
""",
    },
    "desc_wariga": {
        "zh": """
### 什麼是巴厘傳統 Wariga 占星？

**Wariga**（亦稱 Ala Ayuning Dewasa）是巴厘島印度教傳統曆法占卜體系，古法依據 *Lontar Wariga / Dasar Wariga*：

- **Wuku 週期**：共 30 個 Wuku，每個 7 天，形成 210 天的 Pawukon 大週期
- **Wewaran（十類星期）**：Eka～Dasa Wara，以各 Neptu/Urip 數值推算吉凶
- **Dewasa 吉凶**：Panca Wara + Sapta Wara Neptu 總和，對應 Pancasuda 五星判斷
- **Ingkel、Watek、Lintang**：動物分類、吉凶屬性、星宿守護
- **Sasih 月份**：對應巴厘傳統農曆月份與乾雨季劃分
- **Waluku (Orion) 參考**：用於季節驗證與農作時機判斷
""",
        "en": """
### What is Balinese Wariga Astrology?

**Wariga** (also known as Ala Ayuning Dewasa) is the traditional Balinese Hindu calendar divination system, based on *Lontar Wariga / Dasar Wariga*:

- **Wuku Cycle**: 30 Wuku, each 7 days, forming a 210-day Pawukon grand cycle
- **Wewaran (Ten Weekday Types)**: Eka~Dasa Wara, using Neptu/Urip values to assess auspiciousness
- **Dewasa (Auspiciousness)**: Panca Wara + Sapta Wara Neptu sum mapped to Pancasuda five-star judgment
- **Ingkel, Watek, Lintang**: Animal classification, auspice attributes, and stellar guardians
- **Sasih (Months)**: Corresponds to Balinese traditional lunar months and dry/wet season divisions
- **Waluku (Orion) Reference**: Used for seasonal verification and farming timing
""",
    },
    "desc_jawa_weton": {
        "zh": """
### 什麼是爪哇 Weton / Primbon？

**Weton**（韋東）是爪哇傳統命理體系 **Primbon** 的核心概念，
以 Saptawara（七日週期）× Pancawara（五日市集週期）= 35 種命理組合。

- **Saptawara**：對應七大行星能量（日、月、火、水、木、金、土）
- **Pancawara（Pasaran）**：純爪哇本土的五日市集週期（Legi、Pahing、Pon、Wage、Kliwon）
- **Neptu**：每個曆日的命理數值，用於合婚計算與擇日判斷
- **35 天 Weton 循環**：7 × 5 = 35 天完整週期，每人出生 Weton 主導命運特質
- **合婚計算**：兩人 Neptu 相加對照古典 Primbon，判斷婚配吉凶
""",
        "en": """
### What is Javanese Weton / Primbon?

**Weton** is the core concept of the Javanese **Primbon** tradition —
a combination of Saptawara (7-day week) × Pancawara (5-day market week) = 35 destiny types.

- **Saptawara**: 7 planetary weekdays (Sun through Sat)
- **Pancawara (Pasaran)**: Native Javanese 5-day market cycle (Legi, Pahing, Pon, Wage, Kliwon)
- **Neptu**: Numerological value used for marriage compatibility and electional purposes
- **35-day Weton cycle**: 7 × 5 = 35 unique Weton combinations repeating every 35 days
- **Marriage compatibility**: Sum of two Weton Neptus mapped to classical Primbon results
""",
    },
    "desc_bintang_duabelas": {
        "zh": """
### 什麼是 Bintang Duabelas？

**Bintang Duabelas（十二星）** 是馬來－伊斯蘭傳統的數理與十二宮工具箱，結合 **Abjad** 字母數值、
**Hisab Nama** 姓名餘數法、**十二星宮**、**行星時辰** 與 **Azimat** 實務。

- **Abjad / Jawi 姓名數值**：把阿拉伯字母或 Jawi 姓名換算成數值
- **Hisab Nama**：用模數餘數推算疾病來源、婚姻相合、胎兒占與失蹤占
- **十二星宮**：以本人與母名決定對應星宮與十二宮落點
- **行星時辰**：依星期與晝夜序列判斷吉時與凶時
- **Azimat**：依用途提供護符文字、製作時機與簡要指引
""",
        "en": """
### What is Bintang Duabelas?

**Bintang Duabelas (Twelve Stars)** is a Malay-Islamic practical toolkit combining **Abjad** letter values,
**Hisab Nama** remainder divination, the **twelve star houses**, **planetary hours**, and
recommended **Azimat** talisman recipes.

- **Abjad / Jawi name values**: Convert Arabic or Jawi names into numerical totals
- **Hisab Nama**: Use modular remainders for illness source, marriage compatibility, fetal, and missing-person readings
- **Twelve star houses**: Map the querent and mother-name total to a star sign and house
- **Planetary hours**: Read auspicious and difficult hours from weekday day/night sequences
- **Azimat**: Browse talisman texts, timing, and practical preparation notes
""",
    },
    "desc_kinketika": {
        "zh": """
### 什麼是 Kinketika（馬來七星五刻占卜）？

**Kinketika** 來自馬來群島（Nusantara）傳統時間占卜，整合兩種核心方法：

- **Ketika Lima（五時刻）**：依五時禮拜（Subuh、Zohor、Asar、Maghrib、Isyak）分時
- **Bintang Tujuh（七星時刻）**：依七曜（太陽、月亮、火星、水星、木星、金星、土星）分時
- **三類判斷**：Baik（吉）、Nahas（凶）、Sederhana（中平）
- **活動規劃器**：可依航海、婚姻、開業、動土等活動篩出推薦與禁忌時段

此工具用於文化學習與參考，重要決定請結合理性判斷，並尊重 Bomoh 與 Panrita 傳承。
""",
        "en": """
### What is Kinketika (Malay Time Divination)?

**Kinketika** is a Nusantara time-divination module that combines:

- **Ketika Lima**: five periods aligned with Islamic prayer-time structure
- **Bintang Tujuh**: seven periods mapped to the classical seven celestial bodies
- **Three judgments**: Baik (auspicious), Nahas (inauspicious), Sederhana (neutral)
- **Activity planner**: recommends or discourages periods for sailing, marriage, trade, building, and rituals

This tool is for cultural learning/reference. Important life decisions should be combined with rational judgement and respect for Bomoh/Panrita traditions.
""",
    },
    "desc_polynesian": {
        "zh": """
### 波利尼西亞／夏威夷星辰知識 Polynesian / Hawaiian Star Lore

**夏威夷星辰知識**是玻里尼西亞非儀器航海傳統的核心，由航海大師 **Nainoa Thompson** 重振，
透過 **Hōkūleʻa**（喜悅之星，即大角星）引航雙體獨木舟橫越太平洋。

- **32星屋羅盤**：將地平線分為32等份，用於識別星辰升起/落下的方位
- **主要星線**：Ka Iwikuamoʻo（脊椎星線）、Ke Ka o Makaliʻi（馬卡利伊的弦）
- **馬卡希基節**：當 Makaliʻi（昴星團）於日落時升起，標誌夏威夷新年
- **守護星屋**：你出生時 Hōkūleʻa 所在的星屋，象徵你的航海命運
""",
        "en": """
### Polynesian / Hawaiian Star Lore

**Hawaiian Star Lore** is the core of Polynesian non-instrument wayfinding, revived by master navigator
**Nainoa Thompson**, guiding the double-hulled canoe *Hōkūleʻa* across the Pacific by stars alone.

- **32-House Star Compass**: Divides the horizon into 32 houses for star rising/setting bearings
- **Star Lines**: Ka Iwikuamoʻo (The Backbone), Ke Ka o Makaliʻi (The Canoe Bailer)
- **Makahiki Season**: When Makaliʻi (Pleiades) rises at sunset, marking the Hawaiian New Year
- **Guardian House**: The compass house where Hōkūleʻa stood at your birth
""",
    },
    "desc_nadi": {
        "zh": """
### 什麼是納迪占星 (Nadi Jyotish)？

**納迪占星**源自南印度泰米爾那德邦數千年前的古代棕櫚葉手稿（Nadi Granthas）：

- **三大納迪脈輪**：每顆行星依其所在星宿歸屬三種脈輪能量
  - 🌬️ **Aadi Nadi（初脈）**：風型 (Vata)，主神經與思維
  - 🔥 **Madhya Nadi（中脈）**：火型 (Pitta)，主代謝與意志
  - 💧 **Antya Nadi（末脈）**：水型 (Kapha)，主免疫與耐力
- **命主納迪 (Janma Nadi)**：由出生月亮所在星宿決定，影響體質與性格
- **上升納迪 (Lagna Nadi)**：由上升點所在星宿決定，影響外在表現
- **納迪宮分 (Nadi Amsha)**：每宮 30° 分成 150 份（每份 12'），提供最精細分析
- **Nadi Dosha（脈衝衝突）**：婚配雙方若同屬一種納迪，傳統認為需特別注意
""",
        "en": """
### What is Nadi Jyotish?

**Nadi Jyotish** originates from ancient palm-leaf manuscripts (Nadi Granthas) from Tamil Nadu, South India:

- **Three Nadi Channels**: Each planet's Nakshatra belongs to one of three energy channels
  - 🌬️ **Aadi Nadi (First Pulse)**: Vata (Wind) — governs nerves and mind
  - 🔥 **Madhya Nadi (Middle Pulse)**: Pitta (Fire) — governs metabolism and will
  - 💧 **Antya Nadi (Last Pulse)**: Kapha (Water) — governs immunity and endurance
- **Birth Nadi (Janma Nadi)**: Determined by Moon's Nakshatra at birth — affects constitution and character
- **Ascendant Nadi (Lagna Nadi)**: Determined by Ascendant's Nakshatra — affects outer expression
- **Nadi Amsha**: Each 30° house divided into 150 parts (12' each) for the finest analysis
- **Nadi Dosha**: If both partners share the same Nadi, traditional teaching advises special attention
""",
    },
    "desc_zurkhai": {
        "zh": """
### 什麼是蒙古祖爾海 (Zurkhai)？

**祖爾海 (Зурхай / Zurkhai)** 是蒙古傳統占星術，源自藏傳佛教曆算體系：

- **12 生肖**：鼠（Hulgana）、牛（Ükher）、虎（Bar）、兔（Tuulai）、
  龍（Luu）、蛇（Mogoi）、馬（Mori）、羊（Honi）、猴（Bich）、
  雞（Tahia）、狗（Nokhoi）、豬（Gakhai）
- **五行 (元素)**：木（Mod）、火（Gal）、土（Shoroo）、
  金（Temür）、水（Us），各分陰陽
- **60 年循環**：12 生肖 × 5 元素的大循環
- **擇吉**：結婚、出行、建屋、醫療等活動的吉日計算
- **松巴堪布體系**：基於 Sumpa Khenpo Yeshe Peljor 的德古斯布揚圖祖爾海
""",
        "en": """
### What is Mongolian Zurkhai (蒙古祖爾海)?

**Zurkhai (Зурхай)** is traditional Mongolian astrology, rooted in the Tibetan Buddhist calendrical system:

- **12 Animal Signs**: Rat (Hulgana), Ox (Ükher), Tiger (Bar), Rabbit (Tuulai),
  Dragon (Luu), Snake (Mogoi), Horse (Mori), Sheep (Honi), Monkey (Bich),
  Rooster (Tahia), Dog (Nokhoi), Pig (Gakhai)
- **Five Elements**: Wood (Mod), Fire (Gal), Earth (Shoroo), Metal (Temür), Water (Us), each with Yin/Yang
- **60-Year Cycle**: 12 animals × 5 elements
- **Auspicious Date Selection**: Marriage, travel, construction, medicine, and other life events
- **Sumpa Khenpo System**: Based on Sumpa Khenpo Yeshe Peljor's Tegus Buyantu Zurkhai
""",
    },
    "desc_picatrix": {
        "zh": """
### 什麼是 Picatrix 星體魔法？

**Picatrix《賢者之目的》(Ghayat al-Hakim)** 是中世紀阿拉伯魔法占星學的
最重要典籍，約成書於 10-11 世紀：

- **28 阿拉伯月宿 (Manazil al-Qamar)**：以月亮所在度數確定月宿，
  每宿有其統治行星、魔法圖像、香料、金屬與咒語
- **行星時 (Planetary Hours)**：以迦勒底序輪轉，日間夜間各 12 時，
  每時辰由不同行星主導
- **護符魔法 (Talisman Magic)**：結合月宿、行星時、材質，
  製作針對特定意圖（愛情、財富、治病等）的護符

資料來源：Picatrix《賢者之目的》(Ghayat al-Hakim)
— Greer & Warnock 2011 translation / Attrell & Porreca 2019
""",
        "en": """
### What is Picatrix Stellar Magic?

**Picatrix (Ghayat al-Hakim, "The Goal of the Wise")** is the most important medieval Arabic magical-astrological
text, compiled around the 10th–11th century:

- **28 Arabic Lunar Mansions (Manazil al-Qamar)**: Determined by Moon's degree;
  each mansion has its ruling planet, magical image, incense, metal, and invocation
- **Planetary Hours**: Chaldean order rotates through day and night, 12 hours each,
  with a different planet ruling each hour
- **Talisman Magic**: Combining mansion, planetary hour, and materials to create
  talismans for specific intentions (love, wealth, healing, etc.)

Source: Picatrix (Ghayat al-Hakim) — Greer & Warnock 2011 / Attrell & Porreca 2019
""",
    },
    "desc_shams": {
        "zh": """
### 什麼是《太陽知識大全》(Shams al-Maʻārif)？

**《شمس المعارف الكبرى》(Shams al-Maʻārif al-Kubrā)**
是伊斯蘭神秘學最重要的經典之一，由 Aḥmad ibn ʿAlī al-Būnī（1225年卒）所著：

- **七大行星特性**：日、月、水、金、火、木、土的體質、元素、顏色與護符用途
- **十二星座徵兆**：各星座在護符與預言中的意義
- **方陣 (Wafq)**：3×3 至 9×9 魔方方陣，用於護符製作
- **九十九美名 (Asmāʼ al-Ḥusnā)**：每個美名對應行星、用途與時辰
- **修持法 (Riyāḍa)**：結合誦念、香料、齋戒的靈性修行
- **祈禱文 (Du'a)**：各種場景的咒語與祈禱

資料來源：《Shams al-Maʻārif al-Kubrā wa Laṭāʼif al-ʻAwārif》— 1927 McGill 版
""",
        "en": """
### What is Shams al-Maʻārif?

**Shams al-Maʻārif al-Kubrā (شمس المعارف الكبرى, "The Great Sun of Gnosis")**
is one of the most important texts in Islamic esoteric tradition, attributed to
Aḥmad ibn ʿAlī al-Būnī (d. 1225):

- **Seven Planetary Properties**: Temperaments, elements, colours, and talisman uses for each planet
- **Twelve Zodiac Sign Omens**: Significance of each sign in talismanic and divinatory contexts
- **Wafq (Magic Squares)**: 3×3 to 9×9 magic squares for talisman construction
- **99 Beautiful Names (Asmāʼ al-Ḥusnā)**: Each Name mapped to a planet, purpose, and timing
- **Riyāḍa (Spiritual Exercises)**: Practices combining recitation, incense, and fasting
- **Du'a (Invocations)**: Prayers and invocations for various purposes

Source: Shams al-Maʻārif al-Kubrā wa Laṭāʼif al-ʻAwārif — 1927 McGill edition
""",
    },

    # ── 萬化仙禽 (WanHua XianQin) ───────────────────────────
    "tab_chinstar": {"zh": "🐦 萬化仙禽", "en": "🐦 WanHua XianQin"},
    "desc_chinstar": {
        "zh": (
            "**萬化仙禽（新刻劉伯溫萬化仙禽）**\n\n"
            "依據明代古籍《新刻劉伯溫萬化仙禽》（朱國祥著）之演禽推算系統。\n"
            "涵蓋三元起宿、推胎宮、推胎星、推命宮（時加至卯）、推身宮、"
            "推命星、推身星、十二宮衍生星、吞啗合戰判斷、情性賦及格局分析。\n\n"
            "⚠️ 本系統以**農曆**年月日起盤，請在下方輸入農曆出生資料。"
        ),
        "en": (
            "**WanHua XianQin (萬化仙禽)**\n\n"
            "Star-Animal Divination based on the classical Ming-dynasty text "
            "«新刻劉伯溫萬化仙禽» by Zhu Guoxiang.\n"
            "Covers 三元起宿, Fetus Palace, Natal Star, Life Palace, Body Palace, "
            "12 Derived Stars, Swallow-Bite analysis, Personality verse and Chart Pattern.\n\n"
            "⚠️ This system uses the **Lunar Calendar**. Please enter your lunar birth date below."
        ),
    },
    "spinner_chinstar": {"zh": "計算萬化仙禽盤中...", "en": "Computing WanHua XianQin chart…"},
    "chinstar_lunar_input_header": {"zh": "🗓️ 農曆出生資料", "en": "🗓️ Lunar Birth Data"},
    "chinstar_lunar_year": {"zh": "農曆年（公曆年）", "en": "Lunar Year (solar year)"},
    "chinstar_lunar_month": {"zh": "農曆月", "en": "Lunar Month"},
    "chinstar_lunar_day": {"zh": "農曆日", "en": "Lunar Day"},
    "chinstar_use_auto": {"zh": "自動從公曆換算農曆", "en": "Auto-convert from solar date"},
    "chinstar_auto_result": {"zh": "換算結果：{year}年{month}月{day}日 {hour}時", "en": "Converted: {year}-{month}-{day} {hour} hour"},
    "chinstar_subtab_chart": {"zh": "起盤結果", "en": "Chart Result"},
    "chinstar_subtab_text": {"zh": "古籍全文", "en": "Classical Text"},
    "chinstar_subtab_xiangtai": {"zh": "相胎賦", "en": "Birth Combination Reading"},
    "chinstar_subtab_gui_jian": {"zh": "貴賤格", "en": "Noble/Ignoble Patterns"},
    "chinstar_leap_month": {"zh": "（閏月）", "en": " (Leap Month)"},
    "chinstar_auto_convert_failed": {"zh": "自動換算失敗，請手動輸入農曆日期：", "en": "Auto-conversion failed, please enter lunar date manually: "},
    "chinstar_no_swallow": {"zh": "無吞啗關係", "en": "No swallow/bite relationship"},
    "chinstar_text_not_found": {"zh": "古籍文本文件未找到", "en": "Classical text file not found"},
    "chinstar_birth_info": {"zh": "**出生**：{year}年{month}月{day}日 {hour}時　{gender}命　{day_night}　{season}季　**三元**：{san_yuan}", "en": "**Birth**: {year}-{month}-{day} {hour}h　{gender}　{day_night}　{season}　**Three Cycles**: {san_yuan}"},
    "chinstar_twelve_palaces_header": {"zh": "#### 十二宮排布（命宮起逆行）", "en": "#### Twelve Palaces (counter-clockwise from Life Palace)"},
    "chinstar_derived_stars_header": {"zh": "#### 衍生星", "en": "#### Derived Stars"},
    "chinstar_swallow_analysis_header": {"zh": "#### 吞啗 / 合戰分析", "en": "#### Swallow-Bite / Alliance-Battle Analysis"},
    "chinstar_personality_header": {"zh": "#### 情性賦", "en": "#### Personality Verse"},
    "chinstar_pattern_header": {"zh": "#### 格局：{grade}", "en": "#### Chart Pattern: {grade}"},
    "chinstar_full_text_expander": {"zh": "📄 完整文字輸出", "en": "📄 Full Text Output"},
    "chinstar_full_text_label": {"zh": "新刻劉伯溫萬化仙禽（全文）", "en": "WanHua XianQin Classical Text (Full)"},
    "chinstar_xiangtai_title": {"zh": "#### 相胎賦 — 主星胎星配合論斷", "en": "#### Birth Combination Reading — Main Star + Birth Star"},
    "chinstar_xiangtai_match": {"zh": "**命星 {zhu} × 胎星 {tai}** 配合斷語", "en": "**Life Star {zhu} × Birth Star {tai}** Combination Reading"},
    "chinstar_xiangtai_xingpin": {"zh": "形品", "en": "Appearance"},
    "chinstar_xiangtai_xiji": {"zh": "喜忌", "en": "Favored/Avoided"},
    "chinstar_xiangtai_desc": {"zh": "論斷", "en": "Reading"},
    "chinstar_xiangtai_poem": {"zh": "斷曰", "en": "Poem"},
    "chinstar_xiangtai_no_match": {"zh": "⚠️ 未找到命星與胎星的相胎賦配合", "en": "⚠️ No matching birth combination reading found"},
    "chinstar_xiangtai_ref": {"zh": "📖 相胎賦全覽（28組主胎配合）", "en": "📖 All 28 Birth Combination Readings"},
    "chinstar_gui_title": {"zh": "#### 貴格 — 吉利格局", "en": "#### Noble Patterns — Auspicious Configurations"},
    "chinstar_jian_title": {"zh": "#### 賤格 — 凶煞格局", "en": "#### Ignoble Patterns — Inauspicious Configurations"},
    "chinstar_fulu_title": {"zh": "#### 福祿上格", "en": "#### Auspicious High Rank Patterns"},
    "chinstar_pinjian_title": {"zh": "#### 貧賤下命", "en": "#### Inauspicious Low Rank Patterns"},
    "chinstar_gui_for_star": {"zh": "**{star}** 貴格", "en": "**{star}** Noble Patterns"},
    "chinstar_jian_for_star": {"zh": "**{star}** 賤格", "en": "**{star}** Ignoble Patterns"},
    "chinstar_no_gui": {"zh": "無貴格記錄", "en": "No noble patterns recorded"},
    "chinstar_no_jian": {"zh": "無賤格記錄", "en": "No ignoble patterns recorded"},

    # ── 策天十八飛星 (Ce Tian 18 Flying Stars) ─────────────────
    "tab_cetian_ziwei": {"zh": "🌠 策天飛星", "en": "🌠 Ce Tian Flying Stars"},
    "desc_cetian_ziwei": {
        "zh": """
### 什麼是策天十八飛星紫微斗數？

**策天十八飛星**是紫微斗數的古法前身與重要分支，源自明代《十八飛星策天紫微斗數全集》，
由**陳希夷**（希夷先生）傳承，後與標準紫微斗數合併。

- **十八飛星**：十一正曜（紫微、天虛、天貴、天印、天壽、天空、紅鸞、天庫、天貫、文昌、天福、天祿）
  + 七副曜（天杖、天異、旄頭、天刃、天刑、天姚、天哭）
- **無空宮**：每宮至少有正曜＋副曜
- **飛星技術**：星曜會由本宮飛入他宮，產生吉凶影響
- **單宮獨斷**：以單宮解讀為主，較少使用三方四會
- **節氣影響**：星曜落度受節氣影響
- **古法格局**：刑刃哭姚合會等特殊格局解讀
""",
        "en": """
### What is Ce Tian 18 Flying Stars Zi Wei Dou Shu?

**Ce Tian 18 Flying Stars** is the ancient predecessor and important branch of Zi Wei Dou Shu,
originating from the Ming dynasty text *"18 Flying Stars Ce Tian Zi Wei Dou Shu Complete Collection"*,
transmitted by **Chen Xiyi**.

- **18 Flying Stars**: 11 Main Stars (Zi Wei, Tian Xu, Tian Gui, etc.)
  + 7 Auxiliary Stars (Tian Zhang, Tian Yi, Mao Tou, etc.)
- **No Empty Palaces**: Each palace has at least one main + auxiliary star
- **Flying Star Technique**: Stars "fly" from their palace to influence other palaces
- **Single Palace Judgment**: Focus on individual palace reading
- **Solar Term Influence**: Star positions affected by solar terms
- **Classical Patterns**: Special pattern interpretations like Blade-Punishment, Crying-Peach Blossom
""",
    },
    "spinner_cetian_ziwei": {"zh": "正在計算策天十八飛星命盤...", "en": "Calculating Ce Tian 18 Flying Stars chart..."},

    # ── Hellenistic Astrology ───────────────────────────────
    "tab_hellenistic": {"zh": "🏛️ 希臘占星", "en": "🏛️ Hellenistic"},
    "desc_hellenistic": {
        "zh": "**希臘占星（Hellenistic Astrology）**\n\n源自古希臘-羅馬的占星傳統，包含希臘點、埃及界主、年限推進、黃道釋放、行星狀態評分等經典技法。",
        "en": "**Hellenistic Astrology**\n\nThe Greco-Roman tradition featuring Greek Lots, Egyptian Bounds, Annual Profections, Zodiacal Releasing, and Planetary Condition scoring.",
    },
    "spinner_hellenistic": {"zh": "計算希臘占星盤中...", "en": "Computing Hellenistic chart…"},
    "hellen_subtab_chart": {"zh": "星盤圖", "en": "Chart"},
    "hellen_subtab_natal": {"zh": "本命盤", "en": "Natal"},
    "hellen_subtab_profections": {"zh": "年限推進", "en": "Profections"},
    "hellen_subtab_zr": {"zh": "黃道釋放", "en": "Zodiacal Releasing"},
    "hellen_subtab_lots": {"zh": "希臘點", "en": "Lots"},
    "hellen_subtab_centiloquy": {"zh": "百論", "en": "Centiloquy"},

    # ── Western sub-tabs ────────────────────────────────────
    "western_subtab_natal": {"zh": "本命盤", "en": "Natal"},
    "western_subtab_transit": {"zh": "流年過運", "en": "Transits"},
    "western_subtab_return": {"zh": "返照盤", "en": "Solar Return"},
    "western_subtab_synastry": {"zh": "合盤", "en": "Synastry"},
    "western_subtab_dignity": {"zh": "行星尊卑", "en": "Dignities"},
    "western_subtab_harmonic": {
        "zh": "諧波盤",
        "zh_cn": "谐波盘",
        "en": "Harmonics",
    },
    "western_subtab_draconic": {
        "zh": "龍頭星盤",
        "zh_cn": "龙头星盘",
        "en": "Draconic",
    },
    "western_subtab_asteroids": {
        "zh": "小行星",
        "zh_cn": "小行星",
        "en": "Asteroids",
    },
    "western_subtab_fixed_stars": {
        "zh": "恆星",
        "zh_cn": "恒星",
        "en": "Fixed Stars",
    },
    "western_subtab_parans": {
        "zh": "並升星",
        "zh_cn": "并升星",
        "en": "Parans",
    },
    "western_subtab_heliacal": {
        "zh": "偕日升",
        "zh_cn": "偕日升",
        "en": "Heliacal",
    },
    "western_subtab_predictive": {
        "zh": "🔮 預測技術全套",
        "zh_cn": "🔮 预测技术全套",
        "en": "🔮 Predictive Suite",
    },
    # Sabian Symbols
    "sabian_symbols_title": {
        "zh": "🔮 薩比恩符號",
        "zh_cn": "🔮 萨比恩符号",
        "en": "🔮 Sabian Symbols",
    },
    "sabian_symbols_help": {
        "zh": "Marc Edmund Jones (1953) 原著的 360 個薩比恩符號，每個黃道度數對應一個象徵圖像。",
        "zh_cn": "Marc Edmund Jones (1953) 原著的 360 个萨比恩符号，每个黄道度数对应一个象征图像。",
        "en": "360 Sabian Symbols from Marc Edmund Jones (1953), one symbolical image per zodiac degree.",
    },
    "sabian_show_symbols": {
        "zh": "顯示薩比恩符號",
        "zh_cn": "显示萨比恩符号",
        "en": "Show Sabian Symbols",
    },
    "sabian_degree_label": {
        "zh": "度數",
        "zh_cn": "度数",
        "en": "Degree",
    },
    "sabian_symbol_label": {
        "zh": "象徵圖像",
        "zh_cn": "象征图像",
        "en": "Symbol",
    },
    "sabian_keyword_label": {
        "zh": "關鍵字",
        "zh_cn": "关键字",
        "en": "Keyword",
    },
    "sabian_formula_label": {
        "zh": "公式",
        "zh_cn": "公式",
        "en": "Formula",
    },
    "sabian_positive_label": {
        "zh": "正面表達",
        "zh_cn": "正面表达",
        "en": "Positive",
    },
    "sabian_negative_label": {
        "zh": "負面表達",
        "zh_cn": "负面表达",
        "en": "Negative",
    },
    "sabian_interpretation_label": {
        "zh": "心理詮釋",
        "zh_cn": "心理诠释",
        "en": "Interpretation",
    },
    "sabian_show_all": {
        "zh": "📜 查看所有 360 個符號",
        "zh_cn": "📜 查看所有 360 个符号",
        "en": "📜 View All 360 Symbols",
    },
    "sabian_scroll_hint": {
        "zh": "← 左右滑動查看所有行星 →",
        "zh_cn": "← 左右滑动查看所有行星 →",
        "en": "← Swipe to see all planets →",
    },
    "sabian_system_label": {
        "zh": "🔮 薩比恩符號",
        "zh_cn": "🔮 萨比恩符号",
        "en": "🔮 Sabian Symbols",
    },
    "sys_hint_sabian": {
        "zh": "Marc Edmund Jones (1953) 原著的 360 個薩比恩象徵，探索每個度數的心理原型。",
        "zh_cn": "Marc Edmund Jones (1953) 原著的 360 个萨比恩象征，探索每个度数的心理原型。",
        "en": "360 Sabian Symbols from Marc Edmund Jones (1953), exploring psychological archetypes per degree.",
    },
    "desc_sabian": {
        "zh": "🔮 **薩比恩符號**（Sabian Symbols）是由 Marc Edmund Jones 於 1953 年出版的占星象徵系統。每個黃道度數（共 360 度）都對應一個獨特的象徵圖像，揭示該度數的心理原型和生命主題。本模組嚴格採用 Jones 原著的 wording，不使用後世改寫版本。",
        "zh_cn": "🔮 **萨比恩符号**（Sabian Symbols）是由 Marc Edmund Jones 于 1953 年出版的占星象征系统。每个黄道度数（共 360 度）都对应一个独特的象征图像，揭示该度数的心理原型和生命主题。本模组严格采用 Jones 原著的 wording，不使用后世改写版本。",
        "en": "🔮 **Sabian Symbols** is an astrological symbol system published by Marc Edmund Jones in 1953. Each zodiac degree (360 total) corresponds to a unique symbolical image, revealing the psychological archetype and life theme of that degree. This module strictly uses Jones' original wording, not later reinterpretations.",
    },
    # Persian / Sassanian Astrology
    "tab_persian": {
        "zh": "🔯 波斯傳統占星",
        "zh_cn": "🔯 波斯传统占星",
        "en": "🔯 Persian Astrology",
    },
    "sys_hint_persian": {
        "zh": "古代波斯薩珊王朝（224–651 CE）占星技術，包含 Firdar 生命週期、Hyleg/Alcocoden 壽命推算。",
        "zh_cn": "古代波斯萨珊王朝（224–651 CE）占星技术，包含 Firdar 生命周期、Hyleg/Alcocoden 寿命推算。",
        "en": "Ancient Sassanian Persian astrology (224–651 CE), featuring Firdar time lords, Hyleg/Alcocoden longevity techniques.",
    },
    "sys_hint_kp": {
        "zh": "印度現代占星大師克里希納穆提創立的精確預測系統，使用宿度主星 (Sub Lord) 判斷事件發生時機。",
        "zh_cn": "印度现代占星大师克里希纳穆提创立的精确预测系统，使用宿度主星 (Sub Lord) 判断事件发生时机。",
        "en": "Modern Indian astrology system by K.S. Krishnamurti for precise event timing using Sub Lord analysis.",
    },
    "desc_kp": {
        "zh": "🔮 **KP Astrology (Krishnamurti Paddhati)** — 印度現代占星大師 K.S. Krishnamurti (1908-1972) 創立的精確預測系統。\\\\n\\\\n核心特點：\\\\n- **Rasi/Star/Sub Lord 系統**：每顆行星/宮頭都有三層主星，Sub Lord 決定事件「是否成立」\\\\n- **27 宿 × 9 Sub**：249 個精確區間，嚴格按照 Vimshottari Dasha 比例分割\\\\n- **Placidus 宮位制**：採用西洋宮位系統，不同於傳統 Vedic 的整宮制\\\\n- **Ruling Planets**：時辰主星用於問卜 (Horary) 與應期判斷\\\\n- **Significators 分析**：根據宮位守護、佔據、宿度關係判斷行星影響力\\\\n\\\\n適用於：精確預測事件發生時機、問卜占卜、擇日擇時。",
        "zh_cn": "🔮 **KP Astrology (Krishnamurti Paddhati)** — 印度现代占星大师 K.S. Krishnamurti (1908-1972) 创立的精确预测系统。\\\\n\\\\n核心特点：\\\\n- **Rasi/Star/Sub Lord 系统**：每颗行星/宫头都有三层主星，Sub Lord 决定事件「是否成立」\\\\n- **27 宿 × 9 Sub**：249 个精确区间，严格按照 Vimshottari Dasha 比例分割\\\\n- **Placidus 宫位制**：采用西洋宫位系统，不同于传统 Vedic 的整宫制\\\\n- **Ruling Planets**：时辰主星用于问卜 (Horary) 与应期判断\\\\n- **Significators 分析**：根据宫位守护、占据、宿度关系判断行星影响力\\\\n\\\\n适用于：精确预测事件发生时机、问卜占卜、择日择时。",
        "en": "🔮 **KP Astrology (Krishnamurti Paddhati)** — Modern Indian astrology system by K.S. Krishnamurti (1908-1972) for precise event timing.\\\\n\\\\nKey Features:\\\\n- **Rasi/Star/Sub Lord System**: Three-tier lordship for each planet/cusp; Sub Lord determines 'whether event happens'\\\\n- **27 Nakshatras × 9 Subs**: 249 precise divisions following Vimshottari Dasha proportions\\\\n- **Placidus House System**: Western house calculation, different from traditional Vedic Whole Sign\\\\n- **Ruling Planets**: For Horary astrology and timing predictions\\\\n- **Significators Analysis**: Planet strength based on ownership, occupation, and star relationships\\\\n\\\\nBest for: Precise event timing, Horary占卜, electional astrology.",
    },
    "spinner_kp": {
        "zh": "計算 KP 星盤...",
        "zh_cn": "计算 KP 星盘...",
        "en": "Computing KP chart...",
    },
    "desc_persian": {
        "zh": "🔯 **波斯薩珊王朝占星**（Sassanian Astrology）是古代波斯帝國（224–651 CE）的占星傳統，對中世紀伊斯蘭占星和歐洲占星有深遠影響。本模組實現薩珊占星的核心技術：\\n\\n- **Firdar / Firdaria**（行星生命週期）：薩珊占星最具特色的預測技法，將人生劃分為不同行星統治的時期\\n- **Hyleg & Alcocoden**（生命給予者與壽命給予者）：古典壽命推算技術，判斷生命力和壽命長短\\n- **波斯式年度主限**：基於度數的連續移動（每年 30°），不同於希臘占星的星座主限\\n- **Almuten Figuris**（最強行星/命主星）：根據薩珊尊嚴規則計算的命主星\\n- **四顆皇家恆星**：波斯傳統的畢宿五、軒轅十四、心宿二、北落師門\\n- **波斯敏感點**：特殊的阿拉伯點計算\\n\\n此技術與現有阿拉伯占星互補但有獨立體系。",
        "zh_cn": "🔯 **波斯萨珊王朝占星**（Sassanian Astrology）是古代波斯帝国（224–651 CE）的占星传统，对中世纪伊斯兰占星和欧洲占星有深远影响。本模组实现萨珊占星的核心技术：\\n\\n- **Firdar / Firdaria**（行星生命周期）：萨珊占星最具特色的预测技法，将人生划分为不同行星统治的时期\\n- **Hyleg & Alcocoden**（生命给予者与寿命给予者）：古典寿命推算技术，判断生命力和寿命长短\\n- **波斯式年度主限**：基于度数的连续移动（每年 30°），不同于希腊占星的星座主限\\n- **Almuten Figuris**（最强行星/命主星）：根据萨珊尊严规则计算的命主星\\n- **四颗皇家恒星**：波斯传统的毕宿五、轩辕十四、心宿二、北落师门\\n- **波斯敏感点**：特殊的阿拉伯点计算\\n\\n此技术与现有阿拉伯占星互补但有独立体系。",
        "en": "🔯 **Sassanian Astrology** is the ancient Persian Empire (224–651 CE) astrological tradition, profoundly influencing medieval Islamic and European astrology. This module implements core Sassanian techniques:\\n\\n- **Firdar / Firdaria** (Planetary Time Lords): The most characteristic Sassanian predictive technique, dividing life into periods ruled by different planets\\n- **Hyleg & Alcocoden** (Giver of Life & Giver of Years): Classical longevity techniques for judging vitality and lifespan\\n- **Persian Profections**: Degree-based continuous movement (30° per year), distinct from Hellenistic sign profections\\n- **Almuten Figuris** (Chart Ruler): The strongest planet calculated per Sassanian dignity rules\\n- **Four Royal Stars**: Aldebaran, Regulus, Antares, Fomalhaut in Persian tradition\\n- **Persian Lots**: Special Arabic Parts calculations\\n\\nThis system complements but is distinct from Arabic astrology.",
    },
    "persian_firdar_title": {"zh": "📅 Firdar 生命週期", "zh_cn": "📅 Firdar 生命周期", "en": "📅 Firdar Time Lords"},
    "persian_firdar_help": {"zh": "Firdar 是薩珊占星的核心預測技法，將人生劃分為主要行星統治的時期，每個主要時期再細分為子時期。", "zh_cn": "Firdar 是萨珊占星的核心预测技法，将人生划分为主要行星统治的时期，每个主要时期再细分为子时期。", "en": "Firdar is the core Sassanian predictive technique, dividing life into major periods ruled by planets, each subdivided into sub-periods."},
    "persian_hyleg_title": {"zh": "🌟 Hyleg & Alcocoden", "zh_cn": "🌟 Hyleg & Alcocoden", "en": "🌟 Hyleg & Alcocoden"},
    "persian_hyleg_help": {"zh": "Hyleg（生命給予者）判斷生命力來源，Alcocoden（壽命給予者）推算壽命長短。", "zh_cn": "Hyleg（生命给予者）判断生命力来源，Alcocoden（寿命给予者）推算寿命长短。", "en": "Hyleg (Giver of Life) identifies the source of vitality, Alcocoden (Giver of Years) estimates lifespan."},
    "persian_profections_title": {"zh": "🔄 年度主限", "zh_cn": "🔄 年度主限", "en": "🔄 Annual Profections"},
    "persian_almuten_title": {"zh": "👑 Almuten Figuris", "zh_cn": "👑 Almuten Figuris", "en": "👑 Almuten Figuris"},
    "persian_royal_stars_title": {"zh": "⭐ 皇家恆星", "zh_cn": "⭐ 皇家恒星", "en": "⭐ Royal Stars"},
    "persian_lots_title": {"zh": "📍 波斯敏感點", "zh_cn": "📍 波斯敏感点", "en": "📍 Persian Lots"},
    "persian_current_firdar": {"zh": "當前 Firdar", "zh_cn": "当前 Firdar", "en": "Current Firdar"},
    "persian_current_sub": {"zh": "當前子週期", "zh_cn": "当前子周期", "en": "Current Sub-Period"},
    "persian_hyleg_label": {"zh": "Hyleg", "zh_cn": "Hyleg", "en": "Hyleg"},
    "persian_alcocoden_label": {"zh": "Alcocoden", "zh_cn": "Alcocoden", "en": "Alcocoden"},
    "persian_planetary_years": {"zh": "行星年數", "zh_cn": "行星年数", "en": "Planetary Years"},
    "persian_modified_years": {"zh": "修正年數", "zh_cn": "修正年数", "en": "Modified Years"},
    "persian_aspects": {"zh": "相位影響", "zh_cn": "相位影响", "en": "Aspect Influences"},
    "persian_dignity_score": {"zh": "尊嚴分數", "zh_cn": "尊严分数", "en": "Dignity Score"},
    "persian_no_prominent_stars": {"zh": "無顯著皇家恆星合相（容許度 3°以內）", "zh_cn": "无显著皇家恒星合相（容许度 3°以内）", "en": "No prominent Royal Star conjunctions (within 3° orb)"},
    "spinner_persian": {"zh": "正在計算波斯薩珊占星星盤...", "zh_cn": "正在计算波斯萨珊占星星盘...", "en": "Computing Sassanian Persian chart..."},
    # Sassanian Traditional Star Chart
    "sassanian_chart_title": {
        "zh": "🏛️ 波斯薩珊傳統占星星盤",
        "zh_cn": "🏛️ 波斯萨珊传统占星星盘",
        "en": "🏛️ Sassanian Traditional Star Chart",
    },
    "sassanian_chart_toggle": {
        "zh": "啟用波斯傳統占星星盤（薩珊王朝古風）",
        "zh_cn": "启用波斯传统占星星盘（萨珊王朝古风）",
        "en": "Enable Sassanian Traditional Star Chart (Ancient Pahlavi Style)",
    },
    "sassanian_chart_disclaimer": {
        "zh": "此星盤依據薩珊王朝古文獻（Bundahishn、Dorotheus Pahlavi 譯本）與出土波斯銀盤、印章藝術風格重建，非現代圓形輪盤。",
        "zh_cn": "此星盘依据萨珊王朝古文献（Bundahishn、Dorotheus Pahlavi 译本）与出土波斯银盘、印章艺术风格重建，非现代圆形轮盘。",
        "en": "This chart is reconstructed based on Sassanian ancient texts (Bundahishn, Dorotheus Pahlavi translation) and excavated Persian silver plates and seals, not a modern circular wheel.",
    },
    "sassanian_tab_name": {
        "zh": "🏛️ 薩珊傳統星盤",
        "zh_cn": "🏛️ 萨珊传统星盘",
        "en": "🏛️ Sassanian Traditional Chart",
    },
    "sassanian_tab_help": {
        "zh": "基於薩珊王朝古文獻（3-7 世紀）與出土文物重建的方形/橫幅格式星盤，使用整宮制、薩珊 Ayanamsa 和四顆皇家恆星。",
        "zh_cn": "基于萨珊王朝古文献（3-7 世纪）与出土文物重建的方形/横幅格式星盘，使用整宫制、萨珊 Ayanamsa 和四颗皇家恒星。",
        "en": "Square/banner format chart reconstructed from Sassanian ancient texts (3rd-7th century) and artifacts, using Whole Sign Houses, Sassanian Ayanamsa, and Four Royal Stars.",
    },
    "sassanian_show_pahlavi": {
        "zh": "顯示 Pahlavi 文字",
        "zh_cn": "显示 Pahlavi 文字",
        "en": "Show Pahlavi Text",
    },
    "sassanian_show_royal_stars": {
        "zh": "顯示皇家恆星",
        "zh_cn": "显示皇家恒星",
        "en": "Show Royal Stars",
    },
    "sassanian_show_firdar": {
        "zh": "顯示 Firdar 時間線",
        "zh_cn": "显示 Firdar 时间线",
        "en": "Show Firdar Timeline",
    },
    "sassanian_royal_star_tascheter": {
        "zh": "Tascheter（畢宿五）- 春分點守護者",
        "zh_cn": "Tascheter（毕宿五）- 春分点守护者",
        "en": "Tascheter (Aldebaran) - Spring Equinox Guardian",
    },
    "sassanian_royal_star_vanand": {
        "zh": "Vanand（軒轅十四）- 夏分點守護者",
        "zh_cn": "Vanand（轩辕十四）- 夏分点守护者",
        "en": "Vanand (Regulus) - Summer Solstice Guardian",
    },
    "sassanian_royal_star_satevis": {
        "zh": "Satevis（心宿二）- 秋分點守護者",
        "zh_cn": "Satevis（心宿二）- 秋分点守护者",
        "en": "Satevis (Antares) - Autumn Equinox Guardian",
    },
    "sassanian_royal_star_hastorang": {
        "zh": "Hastorang（北落師門）- 冬至點守護者",
        "zh_cn": "Hastorang（北落师门）- 冬至点守护者",
        "en": "Hastorang (Fomalhaut) - Winter Solstice Guardian",
    },
    "sassanian_chart_format": {
        "zh": "星盤格式",
        "zh_cn": "星盘格式",
        "en": "Chart Format",
    },
    "sassanian_format_square": {
        "zh": "方形（薩珊傳統）",
        "zh_cn": "方形（萨珊传统）",
        "en": "Square (Sassanian Traditional)",
    },
    "sassanian_format_banner": {
        "zh": "橫幅（手稿風格）",
        "zh_cn": "横幅（手稿风格）",
        "en": "Banner (Manuscript Style)",
    },
    "sassanian_ayanamsa_label": {
        "zh": "薩珊 Ayanamsa",
        "zh_cn": "萨珊 Ayanamsa",
        "en": "Sassanian Ayanamsa",
    },
    "sassanian_whole_sign_houses": {
        "zh": "整宮制（薩珊標準）",
        "zh_cn": "整宫制（萨珊标准）",
        "en": "Whole Sign Houses (Sassanian Standard)",
    },
    "spinner_sassanian": {
        "zh": "正在渲染薩珊傳統星盤...",
        "zh_cn": "正在渲染萨珊传统星盘...",
        "en": "Rendering Sassanian traditional chart...",
    },
    # Advanced Sassanian / Persian Deep
    "tab_persian_deep": {
        "zh": "🏛️ 薩珊波斯・進階版",
        "zh_cn": "🏛️ 萨珊波斯・进阶版",
        "en": "🏛️ Sassanian Persia (Advanced)",
    },
    "sys_hint_persian_deep": {
        "zh": "深度波斯薩珊占星：Firdaria（正確序列）、Hyleg/Alcocoden、Almuten、月度主限、埃及界、多德卡特摩里亞、反射點、14 個阿拉伯點及 Dorotheus 解讀。",
        "zh_cn": "深度波斯萨珊占星：Firdaria（正确序列）、Hyleg/Alcocoden、Almuten、月度主限、埃及界、多德卡特摩里亚、反射点、14 个阿拉伯点及 Dorotheus 解读。",
        "en": "Deep Sassanian Persian astrology: corrected Firdaria, Hyleg/Alcocoden, Almuten, monthly profections, Egyptian bounds, Dodecatemoria, Antiscia, 14 Arabic parts, and Dorotheus interpretation.",
    },
    "spinner_persian_deep": {
        "zh": "正在計算進階波斯薩珊占星星盤...",
        "zh_cn": "正在计算进阶波斯萨珊占星星盘...",
        "en": "Computing advanced Sassanian Persian chart...",
    },
    "desc_persian_deep": {
        "zh": "🏛️ **薩珊波斯進階占星** — 深度實現波斯薩珊王朝（224–651 CE）占星傳統的高階技術，基於多羅修斯《卡門天文學》、馬沙阿拉、阿布·馬沙爾等波斯阿拉伯占星大師的原典。\n\n**核心特色**：正確 Firdaria 序列（日夜有別）、Hyleg/Alcocoden 壽命三範圍計算、整宮制、埃及界、三分守護星、多德卡特摩里亞（12份法）、反射點/對射點、14 個波斯阿拉伯點、波斯 Dorotheus 解讀引擎、四顆皇家恆星。",
        "zh_cn": "🏛️ **萨珊波斯进阶占星** — 深度实现波斯萨珊王朝（224–651 CE）占星传统的高阶技术。\n\n**核心特色**：正确 Firdaria 序列、Hyleg/Alcocoden 寿命三范围计算、整宫制、埃及界、三分守护星、多德卡特摩里亚、反射点、14 个波斯阿拉伯点、Dorotheus 解读引擎、四颗皇家恒星。",
        "en": "🏛️ **Advanced Sassanian Persian Astrology** — Deep implementation of Sassanian dynasty (224–651 CE) astrological tradition based on Dorotheus, Masha'allah, and Abu Ma'shar.\n\nFeatures: Corrected Firdaria sequences (day/night), three-range Hyleg/Alcocoden longevity, Whole Sign Houses, Egyptian bounds, triplicity lords, Dodecatemoria, Antiscia, 14 Arabic parts, Dorotheus interpretation engine, Royal Stars of Persia.",
    },
    "info_persian_deep_prompt": {
        "zh": "請輸入出生資料並點擊「計算」以查看薩珊波斯進階占星結果。",
        "zh_cn": "请输入出生资料并点击「计算」以查看萨珊波斯进阶占星结果。",
        "en": "Enter birth data and click 'Calculate' to view the advanced Sassanian Persian chart.",
    },
    # Transit / Return / Synastry
    "return_year_label": {"zh": "返照年份", "en": "Return Year"},
    "synastry_header": {"zh": "合盤比較", "en": "Synastry Comparison"},
    "synastry_person_b": {"zh": "對象 B 出生資料", "en": "Person B Birth Data"},

    # ── Vedic sub-tabs ──────────────────────────────────────
    "vedic_subtab_rashi": {"zh": "星盤 Rashi", "en": "Rashi Chart"},
    "vedic_subtab_navamsa": {"zh": "九分盤 D9", "en": "Navamsa D9"},
    "vedic_subtab_dasha": {"zh": "大運 Dasha", "en": "Dasha"},
    "vedic_subtab_ashtaka": {"zh": "八分力量", "en": "Ashtakavarga"},
    "vedic_subtab_yogas": {"zh": "瑜伽組合", "en": "Yogas"},
    "vedic_subtab_bphs": {"zh": "帕拉夏拉大占星經", "en": "BPHS Classic"},
    "vedic_subtab_varga": {"zh": "分盤 Varga", "en": "Divisional Charts"},
    "vedic_subtab_financial": {"zh": "💰 金融占星", "en": "💰 Financial Astrology"},
    # ── Jaimini sub-tab labels ────────────────────────────────────────────────
    "jaimini_subtab_chart": {"zh": "🕉️ Rashi Drishti 排盤", "en": "🕉️ Rashi Drishti Chart"},
    "jaimini_subtab_dasha": {"zh": "📅 Chara Dasha 大運", "en": "📅 Chara Dasha"},

    # ── Ziwei sub-tabs ──────────────────────────────────────
    "ziwei_subtab_natal": {"zh": "本命盤", "en": "Natal"},
    "ziwei_subtab_daxian": {"zh": "大限流年", "en": "Daxian / Liunian"},

    # ── Qizheng electional ──────────────────────────────────
    "ch_subtab_electional": {"zh": "擇日", "en": "Electional"},

    # ── Qizheng financial astrology ─────────────────────────
    "ch_subtab_financial": {"zh": "💰 金融占星", "en": "💰 Financial Astrology"},

    # ── Qizheng 28 mansions text panel ──────────────────────
    "ch_subtab_mansion": {"zh": "🌟 二十八宿", "en": "🌟 28 Mansions"},

    # ── Fixed stars & asteroids ─────────────────────────────
    "show_fixed_stars": {"zh": "顯示恆星合相", "en": "Show Fixed Star Conjunctions"},
    "show_asteroids": {"zh": "顯示小行星", "en": "Show Asteroids"},

    # ── Export ──────────────────────────────────────────────
    "export_header": {"zh": "匯出", "en": "Export"},
    # PDF keys removed — PDF generation has been removed

    # ── Natal summary / Interpretations ────────────────────
    "natal_summary_header": {"zh": "📝 命盤解讀 / Natal Summary", "en": "📝 Natal Summary"},
    "transit_readings_header": {"zh": "📖 流年解讀 / Transit Readings", "en": "📖 Transit Readings"},
    "synastry_readings_header": {"zh": "📖 合盤解讀 / Synastry Readings", "en": "📖 Synastry Readings"},
    "dasha_reading_header": {"zh": "📖 大限解讀", "en": "📖 Dasha Interpretation"},

    # ── Error boundary ─────────────────────────────────────
    "error_tab_compute": {
        "zh": "此體系計算時發生錯誤",
        "en": "An error occurred computing this system",
    },

    # ── Sidebar astrology selector ─────────────────────────
    "sidebar_system_home": {
        "zh": "🏠 首頁（世界地圖）",
        "en": "🏠 Home (World Map)",
    },

    # ── World map homepage ─────────────────────────────────
    "map_title": {
        "zh": "🗺️ 世界占星地圖 — 點選地區探索占星體系",
        "en": "🗺️ World Astrology Map — Click a region to explore",
    },
    "map_subtitle": {
        "zh": "將滑鼠移到地區上方可查看該地區的占星體系，點擊按鈕即可進入",
        "en": "Hover over a region to see its astrology systems, click a button to enter",
    },

    # ── AI Analysis (AI 分析) ──────────────────────────────────
    "ai_settings_header": {
        "zh": "🤖 AI 分析設置",
        "en": "🤖 AI Analysis Settings",
    },
    "ai_model_label": {
        "zh": "AI 模型",
        "en": "AI Model",
    },
    "ai_select_prompt": {
        "zh": "選擇系統提示",
        "en": "Select System Prompt",
    },
    "ai_select_prompt_help": {
        "zh": "選擇用於 AI 模型的系統提示，指導其分析排盤結果",
        "en": "Select a system prompt for the AI model to guide chart analysis",
    },
    "ai_edit_prompt": {
        "zh": "編輯提示內容",
        "en": "Edit Prompt Content",
    },
    "ai_edit_prompt_placeholder": {
        "zh": "在此編輯系統提示內容…",
        "en": "Edit the system prompt content here…",
    },
    "ai_update_prompt_btn": {
        "zh": "💾 更新提示",
        "en": "💾 Update Prompt",
    },
    "ai_delete_prompt_btn": {
        "zh": "🗑️ 刪除提示",
        "en": "🗑️ Delete Prompt",
    },
    "ai_add_prompt_expander": {
        "zh": "➕ 新增自訂提示",
        "en": "➕ Add Custom Prompt",
    },
    "ai_new_prompt_name": {
        "zh": "提示名稱",
        "en": "Prompt Name",
    },
    "ai_new_prompt_content": {
        "zh": "提示內容",
        "en": "Prompt Content",
    },
    "ai_new_prompt_placeholder": {
        "zh": "輸入 AI 分析指令…",
        "en": "Enter AI analysis instructions…",
    },
    "ai_save_new_prompt_btn": {
        "zh": "💾 儲存新提示",
        "en": "💾 Save New Prompt",
    },
    "ai_prompt_updated": {
        "zh": "✅ 已更新提示「{}」",
        "en": '✅ Prompt "{}" updated',
    },
    "ai_prompt_deleted": {
        "zh": "🗑️ 已刪除提示「{}」",
        "en": '🗑️ Prompt "{}" deleted',
    },
    "ai_prompt_saved": {
        "zh": "✅ 已新增提示「{}」",
        "en": '✅ Prompt "{}" saved',
    },
    "ai_max_tokens": {
        "zh": "最大回應長度",
        "en": "Max Response Tokens",
    },
    "ai_max_tokens_help": {
        "zh": "控制 AI 回應的最大長度",
        "en": "Control the maximum length of AI responses",
    },
    "ai_temperature": {
        "zh": "溫度 (Temperature)",
        "en": "Temperature",
    },
    "ai_temperature_help": {
        "zh": "較高的溫度會產生更有創意的回應，較低則更精確",
        "en": "Higher temperature produces more creative responses, lower is more precise",
    },
    "ai_analyze_btn": {
        "zh": "🔍 使用 AI 分析排盤結果",
        "en": "🔍 Analyze Chart with AI",
    },
    "ai_analyzing": {
        "zh": "AI 正在分析排盤結果…",
        "en": "AI is analyzing the chart…",
    },
    "ai_key_missing": {
        "zh": "⚠️ 未設置 Cerebras API Key。請在 Streamlit Secrets 或環境變數中設定 CEREBRAS_API_KEY。",
        "en": "⚠️ Cerebras API Key not found. Set CEREBRAS_API_KEY in Streamlit Secrets or environment variables.",
    },
    "ai_openai_key_missing": {
        "zh": "⚠️ 請在「AI 分析設置」中輸入您的 OpenAI API Key。",
        "en": "⚠️ Please enter your OpenAI API Key in the AI Analysis Settings.",
    },
    "ai_provider_label": {
        "zh": "AI 服務提供商",
        "en": "AI Provider",
    },
    "ai_provider_cerebras": {
        "zh": "Cerebras（免費）",
        "en": "Cerebras (Free)",
    },
    "ai_provider_openai": {
        "zh": "OpenAI（自帶密鑰）",
        "en": "OpenAI (Bring Your Own Key)",
    },
    "ai_openai_key_label": {
        "zh": "OpenAI API Key",
        "en": "OpenAI API Key",
    },
    "ai_openai_key_help": {
        "zh": "輸入您的 OpenAI API Key（以 sk- 開頭）。密鑰僅在本次會話中使用，不會被儲存。",
        "en": "Enter your OpenAI API Key (starts with sk-). The key is only used in this session and is never stored.",
    },
    "ai_provider_custom": {
        "zh": "第三方服務商",
        "en": "Custom Provider",
    },
    "ai_custom_name_label": {
        "zh": "名稱",
        "en": "Name",
    },
    "ai_custom_name_placeholder": {
        "zh": "例如：我的 LLM",
        "en": "e.g. My LLM",
    },
    "ai_custom_api_mode_label": {
        "zh": "API 模式",
        "en": "API Mode",
    },
    "ai_custom_api_mode_openai": {
        "zh": "OpenAI API 兼容",
        "en": "OpenAI API Compatible",
    },
    "ai_custom_key_label": {
        "zh": "API 密鑰",
        "en": "API Key",
    },
    "ai_custom_key_help": {
        "zh": "輸入第三方服務商的 API Key。密鑰僅在本次會話中使用，不會被儲存。",
        "en": "Enter the API key for your custom provider. The key is only used in this session and is never stored.",
    },
    "ai_custom_host_label": {
        "zh": "API 主機",
        "en": "API Host",
    },
    "ai_custom_path_label": {
        "zh": "API 路徑",
        "en": "API Path",
    },
    "ai_custom_url_preview": {
        "zh": "完整 URL：",
        "en": "Full URL: ",
    },
    "ai_custom_models_header": {
        "zh": "模型",
        "en": "Models",
    },
    "ai_custom_models_add": {
        "zh": "+ 新建",
        "en": "+ Add",
    },
    "ai_custom_models_reset": {
        "zh": "↺ 重置",
        "en": "↺ Reset",
    },
    "ai_custom_models_fetch": {
        "zh": "↻ 獲取",
        "en": "↻ Fetch",
    },
    "ai_custom_model_new_placeholder": {
        "zh": "輸入模型名稱",
        "en": "Enter model name",
    },
    "ai_custom_key_missing": {
        "zh": "⚠️ 請在「AI 分析設置」中輸入第三方服務商的 API Key。",
        "en": "⚠️ Please enter the custom provider API key in AI Analysis Settings.",
    },
    "ai_custom_host_missing": {
        "zh": "⚠️ 請在「AI 分析設置」中輸入 API 主機地址。",
        "en": "⚠️ Please enter the API host in AI Analysis Settings.",
    },
    "ai_custom_model_missing": {
        "zh": "⚠️ 請先添加至少一個模型。",
        "en": "⚠️ Please add at least one model first.",
    },
    "ai_custom_fetch_ok": {
        "zh": "✅ 成功獲取 {} 個模型。",
        "en": "✅ Successfully fetched {} models.",
    },
    "ai_custom_fetch_fail": {
        "zh": "❌ 獲取模型失敗：{}",
        "en": "❌ Failed to fetch models: {}",
    },
    "ai_error": {
        "zh": "❌ 調用 AI 時發生錯誤：{}",
        "en": "❌ Error calling AI: {}",
    },
    "ai_rate_limit": {
        "zh": "⏳ AI 服務目前流量過高，已自動重試但仍未成功。請稍後再試。",
        "en": "⏳ AI service is experiencing high traffic. Automatic retries were exhausted. Please try again shortly.",
    },
    "ai_result_header": {
        "zh": "AI 分析結果",
        "en": "AI Analysis Result",
    },
    "ai_no_chart": {
        "zh": "請先計算排盤後再進行 AI 分析。",
        "en": "Please compute a chart first before running AI analysis.",
    },
    "ai_chat_header": {
        "zh": "AI 占星助手",
        "en": "AI Astrology Assistant",
    },
    "ai_chat_placeholder": {
        "zh": "輸入問題與 AI 對話…",
        "en": "Ask the AI about this chart…",
    },
    "ai_chat_welcome": {
        "zh": "你好！我是 AI 占星助手。排盤數據已載入，你可以問我任何關於這個命盤的問題，例如：\n- 幫我分析整體命盤格局\n- 我的事業運如何？\n- 有什麼需要注意的？",
        "en": "Hello! I'm your AI astrology assistant. The chart data is loaded — you can ask me anything about this chart, such as:\n- Analyze the overall chart\n- How does my career look?\n- What should I watch out for?",
    },
    "ai_chat_clear": {
        "zh": "🗑️ 清除對話",
        "en": "🗑️ Clear Chat",
    },
    "tab_contact": {"zh": "📬 關於 / 聯繫", "en": "📬 About / Contact"},
    "tab_history": {"zh": "📜 占星歷史", "en": "📜 History of Astrology"},
    "tab_wiki": {"zh": "📚 占星知識庫", "en": "📚 Astrology Wiki"},
    "contact_title": {"zh": "開發者資訊", "en": "Developer Info"},
    "contact_wechat": {"zh": "微信公眾號：**探究三式**", "en": "WeChat Official Account: **探究三式**"},
    "contact_wechat_id": {
        "zh": "如有任何建議或合作事宜，可加本人微信聯繫，或搜 **gnatnek**（請註明是在 GitHub 加我的）",
        "en": "For suggestions or collaboration, add WeChat ID **gnatnek** (please mention you found me on GitHub)",
    },
    "contact_qq": {
        "zh": "或加入 QQ 群組「堅三式軟件交流群」（群號 **770621021**）",
        "en": "Or join QQ Group 「堅三式軟件交流群」 (Group ID **770621021**)",
    },
    "contact_other_apps": {"zh": "其他相關應用", "en": "Other Related Apps"},

    # ── GUI Optimization: System categories ─────────────────
    "cat_popular": {"zh": "最熱門", "en": "Most Popular"},
    "cat_chinese": {"zh": "中華傳統", "en": "Chinese Traditions"},
    "cat_western": {"zh": "西方體系", "en": "Western Systems"},
    "cat_indian": {"zh": "印度體系", "en": "Indian Systems"},
    "cat_asian": {"zh": "亞洲體系", "en": "Asian Systems"},
    "cat_middle_east": {"zh": "中東體系", "en": "Middle Eastern Systems"},
    "cat_africa": {"zh": "非洲體系", "en": "African Systems"},
    "cat_ancient": {"zh": "古文明", "en": "Ancient Civilizations"},
    "cat_obscure": {"zh": "隱祕與原民傳統", "en": "Obscure & Indigenous Traditions"},
    "cat_yi_zhan": {"zh": "醫占", "en": "Medical Astrology"},
    "cat_horary": {"zh": "傳統卜卦占星", "en": "Traditional Horary Astrology"},
    "cat_korean": {"zh": "韓國體系", "en": "Korean Systems"},
    "cat_khmer": {"zh": "高棉體系", "en": "Khmer Systems"},

    # ── GUI Optimization: Short beginner-friendly system descriptions ──
    "sys_hint_western": {"zh": "最廣為人知的星座運勢", "en": "The most well-known horoscope system"},
    "sys_hint_ziwei": {"zh": "中國最流行的命理系統", "en": "China's most popular destiny system"},
    "sys_hint_chinese": {"zh": "中國古代天文星象占卜", "en": "Ancient Chinese astronomical divination"},
    "sys_hint_indian": {"zh": "印度古老吠陀占星", "en": "Ancient Vedic astrology from India"},
    "sys_hint_thai": {"zh": "泰國傳統命理解讀", "en": "Traditional Thai fate reading"},
    "sys_hint_laos": {"zh": "老撾婆羅門占星與擇日", "en": "Traditional Lao Horasat and electional timing"},
    "sys_hint_kabbalistic": {"zh": "猶太神祕主義占星", "en": "Jewish mystical astrology"},
    "sys_hint_arabic": {"zh": "伊斯蘭黃金時代占星術", "en": "Islamic Golden Age astrology"},
    "sys_hint_maya": {"zh": "瑪雅 Tzolk'in 神聖曆、Long Count 長紀年、Calendar Round 52年循環", "en": "Maya Tzolk'in sacred calendar, Long Count, Calendar Round 52-year cycle"},
    "sys_hint_dogon_sirius": {"zh": "多貢天狼星傳統：Po Tolo、Nommo、Sigui 50 年週期", "en": "Dogon Sirius lore: Po Tolo, Nommo, and the 50-year Sigui cycle"},
    "sys_hint_aztec": {"zh": "阿茲特克文明神聖曆占卜", "en": "Aztec Tonalpohualli sacred calendar divination"},
    "sys_hint_mahabote": {"zh": "緬甸／撣族 Mahabote 深度排盤", "en": "Burmese/Shan Mahabote deep astrology"},
    "sys_hint_wariga": {"zh": "巴厘島傳統 Wuku 吉凶日曆", "en": "Balinese traditional Wuku auspiciousness calendar"},
    "sys_hint_jawa_weton": {"zh": "爪哇 Weton 命理 + 合婚計算", "en": "Javanese Weton destiny & marriage compatibility"},
    "sys_hint_bintang_duabelas": {
        "zh": "馬來伊斯蘭占星：Jawi Abjad、Hisab Nama、十二星宮、行星時辰與 Azimat",
        "en": "Malay Islamic astrology: Jawi Abjad, Hisab Nama, twelve houses, planetary hours, and Azimat",
    },
    "sys_hint_kinketika": {
        "zh": "馬來群島時間占卜：Ketika Lima 五時刻 + Bintang Tujuh 七星時刻",
        "en": "Nusantara time divination: Ketika Lima + Bintang Tujuh with activity planning",
    },
    "sys_hint_polynesian": {"zh": "夏威夷 / 玻里尼西亞星辰知識與航海星羅盤", "en": "Hawaiian / Polynesian Star Lore & Navigation Compass"},
    "sys_hint_andean": {
        "zh": "印加天河（Mayu）、暗星宿（Yana Phuyu）、南十字 Chakana、昴宿穀倉預兆",
        "en": "Inca Mayu sky-river, Yana Phuyu dark cloud animals, Chakana cross, Pleiades harvest omens",
    },
    "sys_hint_decans": {"zh": "古埃及十度區間預測", "en": "Ancient Egyptian decan predictions"},
    "sys_hint_nadi": {"zh": "南印度棕櫚葉手稿", "en": "South Indian palm-leaf readings"},
    "sys_hint_zurkhai": {"zh": "蒙古藏傳佛教占星", "en": "Mongolian Tibetan Buddhist astrology"},
    "sys_hint_hellenistic": {"zh": "古希臘羅馬占星傳統", "en": "Greco-Roman astrological tradition"},
    "sys_hint_sukkayodo": {"zh": "日本宿曜道擇日占卜", "en": "Japanese lunar mansion divination"},
    "sys_hint_chinstar": {"zh": "明代演禽命理推算", "en": "Ming dynasty bird-star divination"},
    "sys_hint_cetian_ziwei": {"zh": "古法十八飛星紫微斗數", "en": "Ancient 18 Flying Stars Zi Wei Dou Shu"},
    "sys_hint_jaimini": {"zh": "Jaimini Sutras 古法占星", "en": "Jaimini Sutras ancient Vedic astrology"},
    "sys_hint_twelve_ci": {"zh": "中國古代木星分野系統", "en": "Ancient Chinese Jupiter-station system"},
    "sys_hint_tojeong": {"zh": "朝鮮時代土亭子占數系統", "en": "Joseon Dynasty Tojeong numerology system"},
    "sys_hint_huangji_short": {"zh": "邵雍皇極經世・元會運世宏觀週期", "en": "Shao Yong's macro cosmic cycles (Yuan-Hui-Yun-Shi)"},
    "sys_hint_armenian_short": {"zh": "亞美尼亞黃道・Haykian 古曆・Arevakhach 象徵", "en": "Armenian zodiac, Haykian calendar & Arevakhach symbolism"},
    "sys_hint_sports_astrology_short": {"zh": "Frawley 運動卜卦・1/7宮勝負判斷", "en": "Frawley sports horary & event-chart win judgment"},

    # ── 十二星次 (Twelve Ci) ────────────────────────────────────
    "tab_twelve_ci": {"zh": "🌌 十二星次", "en": "🌌 Twelve Ci"},
    "desc_twelve_ci": {
        "zh": (
            "**十二星次（Twelve Ci / 十二次 / 木星分野）**\n\n"
            "中國古代最古老的木星分野系統，源自《左傳》《國語》《漢書・天文志》等經典。"
            "以冬至點為黃道 0° 起點，將黃道 360° 等分為十二次，每次 30°，"
            "依據木星（歲星）十二年繞天一周的運行規律，判定分野歸屬與吉凶。\n\n"
            "十二次與十二地支、二十八宿、九州分野一一對應，是古代天文預測與國運分析的核心工具。"
        ),
        "en": (
            "**Twelve Ci (十二星次 / Jupiter Station Astrology)**\n\n"
            "The most ancient Chinese Jupiter-station system, originating from classical texts "
            "such as Zuozhuan, Guoyu, and Han Shu (Book of Han — Treatise on Astronomy).\n\n"
            "Starting from the winter-solstice point as ecliptic 0°, the ecliptic is divided into "
            "twelve equal 30° sections (Ci).  Based on Jupiter's ~12-year orbital cycle, each Ci "
            "corresponds to an Earthly Branch, Lunar Mansions, and a territorial domain (Fenye)."
        ),
    },
    "spinner_twelve_ci": {"zh": "計算十二星次盤中…", "en": "Computing Twelve Ci chart…"},
    "twelve_ci_chart_title": {"zh": "🌌 十二星次排盤 / Twelve Ci Astrology", "en": "🌌 Twelve Ci Astrology"},
    "twelve_ci_natal_jupiter": {"zh": "本命木星星次", "en": "Natal Jupiter Ci"},
    "twelve_ci_ci_name": {"zh": "星次", "en": "Ci"},
    "twelve_ci_branch": {"zh": "地支", "en": "Branch"},
    "twelve_ci_mansions": {"zh": "二十八宿", "en": "Mansions"},
    "twelve_ci_fenye": {"zh": "分野", "en": "Fenye"},
    "twelve_ci_jupiter_degree": {"zh": "木星度數", "en": "Jupiter Degree"},
    "twelve_ci_planet_table": {"zh": "全部行星星次位置", "en": "All Planet Ci Positions"},
    "twelve_ci_col_planet": {"zh": "行星", "en": "Planet"},
    "twelve_ci_col_ci": {"zh": "星次", "en": "Ci"},
    "twelve_ci_col_branch": {"zh": "地支", "en": "Branch"},
    "twelve_ci_col_degree": {"zh": "度數", "en": "Degree"},
    "twelve_ci_col_mansions": {"zh": "宿", "en": "Mansions"},
    "twelve_ci_col_fenye": {"zh": "分野", "en": "Fenye"},
    "twelve_ci_col_range": {"zh": "範圍", "en": "Range"},
    "twelve_ci_col_solar": {"zh": "約陽曆", "en": "Solar Approx."},
    "twelve_ci_transit_title": {"zh": "流年木星（當前行運）", "en": "Transit Jupiter (Current)"},
    "twelve_ci_transit_ci": {"zh": "流年星次", "en": "Transit Ci"},
    "twelve_ci_transit_degree": {"zh": "流年度數", "en": "Transit Degree"},
    "twelve_ci_transit_branch": {"zh": "流年地支", "en": "Transit Branch"},
    "twelve_ci_reference_title": {"zh": "📚 十二星次總覽", "en": "📚 Twelve Ci Reference"},
    "twelve_ci_subtab_chart": {"zh": "🌌 星次輪盤", "en": "🌌 Ci Wheel"},
    "twelve_ci_subtab_detail": {"zh": "📋 排盤資料", "en": "📋 Chart Detail"},

    # ── GUI Optimization: Welcome / onboarding ─────────────
    "welcome_hero_title": {
        "zh": "歡迎來到堅占星 ⭐",
        "en": "Welcome to Kin Astro ⭐",
    },
    "welcome_hero_body": {
        "zh": "不用懂占星也能了解自己！只需 3 步，即可獲得你的專屬命理分析。",
        "en": "No astrology knowledge needed! Just 3 steps to get your personal destiny reading.",
    },
    "welcome_step1_title": {"zh": "填寫出生資料", "en": "Enter Birth Info"},
    "welcome_step1_body": {
        "zh": "在左邊欄填入出生日期、時間、地點",
        "en": "Fill in your birth date, time, and place in the sidebar",
    },
    "welcome_step2_title": {"zh": "選擇占星類型", "en": "Pick a System"},
    "welcome_step2_body": {
        "zh": "推薦從「西洋占星」或「紫微斗數」開始",
        "en": "Start with Western Astrology or Zi Wei Dou Shu",
    },
    "welcome_step3_title": {"zh": "AI 幫你解讀", "en": "AI Reads for You"},
    "welcome_step3_body": {
        "zh": "點擊 AI 分析按鈕，用白話文解讀你的命盤",
        "en": "Click AI Analysis to get a plain-language reading",
    },
    "welcome_quick_start": {
        "zh": "👈 先在左邊欄輸入你的出生資料，再選擇一個占星體系吧！",
        "en": "👈 Start by entering your birth info in the sidebar, then pick a system!",
    },
    "sidebar_system_label": {
        "zh": "選擇你想了解的命理",
        "en": "Pick Your Destiny Reading",
    },
    "lang_switcher_label": {
        "zh": "語言切換",
        "en": "Language",
    },
    "overview_dashboard_title": {
        "zh": "概覽 Dashboard",
        "en": "Overview Dashboard",
    },
    "overview_dashboard_open": {
        "zh": "查看詳細",
        "en": "Open Details",
    },
    "overview_dashboard_current": {
        "zh": "目前體系",
        "en": "Current System",
    },
    "overview_dashboard_loading": {
        "zh": "彙整多體系關鍵指標中…",
        "en": "Building multi-system overview…",
    },
    "status_chart_ready": {
        "zh": "命盤已更新，請從下方概覽快速切換體系深入查看。",
        "en": "Chart updated. Use the overview cards below to jump into any system.",
    },

    # ── GUI Optimization: Simplified info prompt ───────────
    "info_calc_prompt": {
        "zh": "👈 請在左邊欄填寫你的出生資料，然後點選你想了解的占星類型。",
        "en": "👈 Enter your birth info on the left, then pick the astrology system you want.",
    },
    "info_lao_prompt": {
        "zh": "👈 請先在左側輸入出生資料並點擊「開始排盤」，即可查看老撾曆、ສັງຄົມ、ສີກາດ與婆羅門占星輪。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart' to view Lao date info, ສັງຄົມ, ສີກາດ, and the Brahman wheel.",
    },

    # ── Babylonian Astrology (古巴比倫占星) ─────────────────
    "tab_babylonian": {"zh": "🏺 古巴比倫占星", "en": "🏺 Babylonian"},
    "desc_babylonian": {
        "zh": (
            "**古巴比倫占星（Babylonian / Chaldean Astrology）**\n\n"
            "美索不達米亞文明是所有西洋占星的直接源頭。核心文獻包括 MUL.APIN 星表（約公元前 1000 年）、"
            "Enūma Anu Enlil 預兆集（約 70 片泥板）以及 K.8538 尼尼微星盤（8 區間平面星圖）。\n\n"
            "本模組使用 sidereal 黃道計算行星位置，對應 12 宮 Akkadian 古名與七大行星神，"
            "並以 K.8538 泥板風格呈現視覺化星盤。"
        ),
        "en": (
            "**Babylonian / Chaldean Astrology**\n\n"
            "Mesopotamian civilisation is the direct ancestor of all Western astrology. "
            "Core sources include the MUL.APIN star catalogue (~1000 BCE), the Enūma Anu Enlil "
            "omen series (~70 tablets), and the K.8538 Nineveh planisphere (8-sector star map).\n\n"
            "This module uses a sidereal zodiac to compute planetary positions, maps them to the "
            "12 Akkadian sign names and the seven planetary deities, and renders a K.8538-style "
            "clay-tablet planisphere."
        ),
    },
    "spinner_babylonian": {"zh": "計算古巴比倫星盤中…", "en": "Computing Babylonian chart…"},
    "sys_hint_babylonian": {"zh": "美索不達米亞占星——西洋占星之源", "en": "Mesopotamian astrology — origin of Western horoscopy"},
    "cat_mesopotamia": {"zh": "🏺 美索不達米亞", "en": "🏺 Mesopotamia"},
    "babylonian_subtab_chart": {"zh": "泥板星圖", "en": "Planisphere"},
    "babylonian_subtab_natal": {"zh": "本命盤", "en": "Natal"},
    "babylonian_subtab_omens": {"zh": "預兆", "en": "Omens"},
    "babylonian_chart_title": {"zh": "𒀭 古巴比倫占星 / Babylonian Astrology", "en": "𒀭 Babylonian Astrology"},
    "babylonian_planet_positions": {"zh": "行星位置 (Sidereal)", "en": "Planet Positions (Sidereal)"},
    "babylonian_omens_title": {"zh": "Enūma Anu Enlil 預兆", "en": "Enūma Anu Enlil Omens"},
    "babylonian_aspects_title": {"zh": "行星相位", "en": "Aspects"},
    "babylonian_houses_title": {"zh": "宮位 (Sidereal)", "en": "Houses (Sidereal)"},
    "babylonian_col_planet": {"zh": "行星", "en": "Planet"},
    "babylonian_col_god": {"zh": "守護神", "en": "Deity"},
    "babylonian_col_akkadian": {"zh": "Akkadian 宮名", "en": "Akkadian Sign"},
    "babylonian_col_sign_cn": {"zh": "中文名", "en": "Chinese Name"},
    "babylonian_col_degree": {"zh": "度數", "en": "Degree"},
    "babylonian_col_house": {"zh": "宮位", "en": "House"},
    "babylonian_col_cusp": {"zh": "宮首", "en": "Cusp"},
    "babylonian_col_aspect": {"zh": "相位", "en": "Aspect"},
    "babylonian_col_angle": {"zh": "角度", "en": "Angle"},
    "babylonian_col_orb": {"zh": "容許度", "en": "Orb"},
    "babylonian_col_condition": {"zh": "狀態", "en": "Condition"},
    "babylonian_col_omen": {"zh": "預兆", "en": "Omen"},
    "babylonian_sector_title": {"zh": "K.8538 八區間", "en": "K.8538 Eight Sectors"},
    "babylonian_sector_direction": {"zh": "方位", "en": "Direction"},
    "babylonian_sector_constellation": {"zh": "星座", "en": "Constellation"},
    "babylonian_sector_planets": {"zh": "行星", "en": "Planets"},
    "babylonian_planisphere_title": {"zh": "K.8538 尼尼微泥板星圖", "en": "K.8538 Nineveh Planisphere"},
    # ── Tibetan Kalachakra 藏傳時輪金剛占星 ──────────────────────────────────
    "tab_tibetan": {
        "zh": "🏔️ 藏傳時輪金剛占星",
        "en": "🏔️ Tibetan Kalachakra",
    },
    "spinner_tibetan": {
        "zh": "正在計算藏傳時輪金剛排盤...",
        "en": "Calculating Tibetan Kalachakra chart...",
    },
    "sys_hint_tibetan": {
        "zh": "藏傳佛教時輪金剛占星體系",
        "en": "Tibetan Buddhist Kalachakra astrology system",
    },
    "desc_tibetan": {
        "zh": """
### 什麼是藏傳時輪金剛占星 (Kalachakra Astrology)？

**時輪金剛 (Kalachakra)** 是藏傳佛教最深奧的密續體系之一：

- **十二生肖 (lo-rtags)**：鼠 (Byi-ba)、牛 (Glang)、虎 (sTag)、兔 (Yos)、
  龍 (ḥBrug)、蛇 (sBrul)、馬 (rTa)、羊 (Lug)、猴 (sPre-hu)、
  鳥 (Bya)、狗 (Khyi)、豬 (Phag)
- **五行 (ḥByung-ba)**：木 (Shing)、火 (Me)、土 (Sa)、金 (Lcags)、水 (Chu)
- **九宮 Mewa (sMe-ba dgu)**：九個數字與顏色、方位對應
- **八卦 Parkha (sPar-kha brgyad)**：八方位系統
- **五力 (dBang-thang lnga)**：La（魂）、Sok（命）、Lu（身）、Wangthang（權勢）、Lungta（風馬）
- **九曜**：七星 + 羅睺 (Ra-hu) + 計都 (Khe-ta)
""",
        "en": """
### What is Tibetan Kalachakra Astrology?

**Kalachakra (Time Wheel)** is one of the most profound tantric systems in Tibetan Buddhism:

- **12 Animal Signs (lo-rtags)**: Rat (Byi-ba), Ox (Glang), Tiger (sTag), Rabbit (Yos),
  Dragon (ḥBrug), Snake (sBrul), Horse (rTa), Sheep (Lug), Monkey (sPre-hu),
  Bird (Bya), Dog (Khyi), Pig (Phag)
- **Five Elements (ḥByung-ba)**: Wood (Shing), Fire (Me), Earth (Sa), Metal (Lcags), Water (Chu)
- **Nine Mewa (sMe-ba dgu)**: Nine numbers with color and directional correspondences
- **Eight Parkha (sPar-kha brgyad)**: Eight directional trigram system
- **Five Forces (dBang-thang lnga)**: La (Soul), Sok (Life), Lu (Body), Wangthang (Power), Lungta (Wind Horse)
- **Nine Planets**: Seven planets + Rahu (Ra-hu) + Ketu (Khe-ta)
""",
    },
    # ── Yemeni Astrology (也門占星) ────────────────────────────
    "tab_yemeni": {"zh": "🕌 也門占星", "en": "🕌 Yemeni"},
    "desc_yemeni": {
        "zh": (
            "**也門占星（Yemeni / South Arabian / Rasulid Astrology）**\n\n"
            "也門占星源自公元前 8 世紀的示巴王國，在 13 世紀 Rasulid 王朝達到高峰。"
            "核心文獻為 al-Malik al-Ashraf ʿUmar ibn Yūsuf 的《Kitāb al-Tabṣira fī ʿIlm al-Nujūm》。\n\n"
            "本模組重點在「也門本土 Rasulid 月宿魔法傳統」，包括 28 月宿（Manazil）的護符魔法（Talismanic Magic）、"
            "醫療與農業擇時、Anwā' 天氣星宿預兆、附庸星傳統、阿拉伯點與 Firdaria 週期。"
        ),
        "en": (
            "**Yemeni / South Arabian / Rasulid Astrology**\n\n"
            "Yemeni astrology originates from the Kingdom of Saba' (8th century BCE) and peaked "
            "during the 13th-century Rasulid dynasty. The core text is al-Malik al-Ashraf ʿUmar ibn "
            "Yūsuf's *Kitāb al-Tabṣira fī ʿIlm al-Nujūm*.\n\n"
            "This module focuses on the uniquely Yemeni Rasulid lunar mansion magic tradition, including "
            "28 Manazil talismanic magic, medical and agricultural timing, Anwā' weather omens, "
            "affiliated planets, Arabic Parts, and Firdaria periods."
        ),
    },
    "spinner_yemeni": {"zh": "計算也門占星盤中…", "en": "Computing Yemeni chart…"},
    "sys_hint_yemeni": {"zh": "南阿拉伯 Rasulid 月宿魔法傳統", "en": "South Arabian Rasulid lunar mansion magic tradition"},
    "yemeni_subtab_mandala": {"zh": "☪ 月宿曼荼羅", "en": "☪ Manzil Mandala"},
    "yemeni_subtab_natal": {"zh": "📋 排盤資料", "en": "📋 Chart Info"},
    "yemeni_subtab_manazil": {"zh": "🌙 月宿詳表", "en": "🌙 Manazil Table"},
    "yemeni_subtab_omens": {"zh": "📜 預兆", "en": "📜 Omens"},
    "yemeni_chart_title": {"zh": "也門占星排盤 / Yemeni Astrology", "en": "Yemeni Astrology"},
    "yemeni_sect": {"zh": "盤型", "en": "Sect"},
    "yemeni_manazil_title": {"zh": "月宿 (Manazil)", "en": "Lunar Mansions (Manazil)"},
    "yemeni_birth_manzil": {"zh": "出生月宿", "en": "Birth Mansion"},
    "yemeni_stars": {"zh": "主要星宿", "en": "Principal Stars"},
    "yemeni_fortune": {"zh": "吉凶", "en": "Fortune"},
    "yemeni_affiliated_planet": {"zh": "附庸星", "en": "Affiliated Planet"},
    "yemeni_talisman_title": {"zh": "護符魔法 (Talismanic Magic)", "en": "Talismanic Magic"},
    "yemeni_anwa_title": {"zh": "Anwā' 天氣星宿預兆", "en": "Anwā' Weather Omens"},
    "yemeni_planet_positions": {"zh": "行星位置 (Sidereal)", "en": "Planet Positions (Sidereal)"},
    "yemeni_arabic_parts_title": {"zh": "阿拉伯點 (Arabic Parts)", "en": "Arabic Parts"},
    "yemeni_omens_title": {"zh": "al-Ashraf 預兆", "en": "al-Ashraf Omens"},
    "yemeni_firdaria_title": {"zh": "Firdaria 週期", "en": "Firdaria Periods"},
    "yemeni_houses_title": {"zh": "宮位 (Sidereal)", "en": "Houses (Sidereal)"},
    "yemeni_col_planet": {"zh": "行星", "en": "Planet"},
    "yemeni_col_sign": {"zh": "星座", "en": "Sign"},
    "yemeni_col_degree": {"zh": "度數", "en": "Degree"},
    "yemeni_col_house": {"zh": "宮位", "en": "House"},
    "yemeni_col_part_name": {"zh": "名稱", "en": "Name"},
    "yemeni_col_arabic": {"zh": "阿拉伯名", "en": "Arabic"},
    "yemeni_col_formula": {"zh": "公式", "en": "Formula"},
    "yemeni_col_years": {"zh": "年數", "en": "Years"},
    "yemeni_col_start": {"zh": "開始", "en": "Start"},
    "yemeni_col_end": {"zh": "結束", "en": "End"},
    "yemeni_col_cusp": {"zh": "宮首", "en": "Cusp"},

    "tibetan_subtab_mandala": {
        "zh": "☸️ 曼荼羅",
        "en": "☸️ Mandala",
    },
    "tibetan_subtab_natal": {
        "zh": "📋 排盤資料",
        "en": "📋 Chart Info",
    },
    "tibetan_subtab_mewa": {
        "zh": "🔮 九宮八卦",
        "en": "🔮 Mewa & Parkha",
    },
    "tibetan_subtab_forces": {
        "zh": "💪 五力",
        "en": "💪 Five Forces",
    },
    "tibetan_subtab_planets": {
        "zh": "🪐 九曜",
        "en": "🪐 Nine Graha",
    },

    # ── Jewish Mazzalot Astrology (猶太 Mazzalot 占星) ─────────
    "tab_mazzalot": {"zh": "✡ 猶太占星", "en": "✡ Jewish Astrology"},
    "desc_mazzalot": {
        "zh": (
            "**猶太 Mazzalot 占星（Jewish Mazzalot Astrology）**\n\n"
            "Mazzalot（מַזָּלוֹת）是猶太傳統中的黃道體系，源自 Talmud（塔木德）、"
            "Sefer Yetzirah（創造之書）與聖經星象解讀。\n\n"
            "- **12 個 Mazzalot**：對應十二支派（Twelve Tribes of Israel）\n"
            "- **Sefer Yetzirah 字母**：12 個簡單字母對應 12 個 Mazzalot\n"
            "- **靈性解讀**：基於 Talmud Shabbat 156a，強調「Ein Mazal l'Yisrael」\n"
            "- **Sidereal 黃道**：使用 Fagan-Bradley ayanamsa 計算"
        ),
        "en": (
            "**Jewish Mazzalot Astrology**\n\n"
            "Mazzalot (מַזָּלוֹת) is the zodiac system in Jewish tradition, rooted in the Talmud, "
            "Sefer Yetzirah (Book of Formation), and biblical star-lore.\n\n"
            "- **12 Mazzalot**: Corresponding to the Twelve Tribes of Israel\n"
            "- **Sefer Yetzirah Letters**: 12 simple letters mapped to 12 Mazzalot\n"
            "- **Spiritual Readings**: Based on Talmud Shabbat 156a, emphasizing 'Ein Mazal l'Yisrael'\n"
            "- **Sidereal Zodiac**: Computed with Fagan-Bradley ayanamsa"
        ),
    },
    "spinner_mazzalot": {"zh": "計算猶太 Mazzalot 星盤中…", "en": "Computing Jewish Mazzalot chart…"},
    "sys_hint_mazzalot": {"zh": "猶太傳統黃道占星——Talmud 與 Sefer Yetzirah", "en": "Jewish traditional zodiac — Talmud & Sefer Yetzirah"},
    "mazzalot_chart_title": {"zh": "✡ 猶太 Mazzalot 占星 / Jewish Mazzalot Astrology", "en": "✡ Jewish Mazzalot Astrology"},
    "mazzalot_planet_positions": {"zh": "行星位置 (Sidereal)", "en": "Planet Positions (Sidereal)"},
    "mazzalot_omens_title": {"zh": "Talmud 靈性解讀", "en": "Talmudic Spiritual Readings"},
    "mazzalot_aspects_title": {"zh": "行星相位", "en": "Aspects"},
    "mazzalot_houses_title": {"zh": "宮位 (Sidereal)", "en": "Houses (Sidereal)"},
    "mazzalot_ascendant": {"zh": "上升 Mazzalot", "en": "Ascendant Mazzalot"},
    "mazzalot_col_planet": {"zh": "行星", "en": "Planet"},
    "mazzalot_col_mazzalot": {"zh": "Mazzalot", "en": "Mazzalot"},
    "mazzalot_col_degree": {"zh": "度數", "en": "Degree"},
    "mazzalot_col_house": {"zh": "宮位", "en": "House"},
    "mazzalot_col_letter": {"zh": "希伯來字母", "en": "Hebrew Letter"},
    "mazzalot_col_tribe": {"zh": "支派", "en": "Tribe"},
    "mazzalot_col_month": {"zh": "希伯來月份", "en": "Hebrew Month"},
    "mazzalot_col_cusp": {"zh": "宮首", "en": "Cusp"},
    "mazzalot_col_aspect": {"zh": "相位", "en": "Aspect"},
    "mazzalot_col_angle": {"zh": "角度", "en": "Angle"},
    "mazzalot_col_orb": {"zh": "容許度", "en": "Orb"},
    "mazzalot_subtab_star": {"zh": "大衛之星輪盤", "en": "Star of David Wheel"},
    "mazzalot_subtab_natal": {"zh": "本命盤", "en": "Natal"},
    "mazzalot_subtab_omens": {"zh": "靈性解讀", "en": "Spiritual Readings"},


    # ── 滌器遺訣 (Di Qi Yi Jue) ───────────────────────────────────────
    "tab_diqiyijue": {
        "zh": "🌀 滌器遺訣",
        "en": "🌀 Di Qi Yi Jue",
    },
    "sys_hint_diqiyijue": {
        "zh": "邵子氣數古法——胎月、八宮、填空法與陰陽數合化",
        "en": "Shao Yong numerology with fetal month, eight palaces, void-filling, and yin-yang number synthesis",
    },
    "desc_diqiyijue": {
        "zh": (
            "**滌器遺訣（Di Qi Yi Jue / 邵子氣數）** — 以胎月、五條、八宮、本宮四位為骨架，"
            "結合填空法、觀空定卦、八卦體變、起胞法、合孕數與流籌法的古法命理系統。\n\n"
            "此模組會自動從輸入的公曆出生時間換算四柱，輸出胎月、元影數、八宮、命宮、大運與流年流籌等核心結果。"
        ),
        "en": (
            "**Di Qi Yi Jue (Shao Yong Qi Numerology)** — A classical numerological destiny method built around the fetal month, five lines, eight palaces, void filling, guankong divination, bagua transformation, qipao life-stage analysis, and flow-year procedures."
        ),
    },
    "spinner_diqiyijue": {"zh": "推算滌器遺訣中…", "en": "Computing Di Qi Yi Jue chart…"},
    "info_diqiyijue_prompt": {
        "zh": "👈 請在左側輸入出生年月日時及性別，點擊「開始排盤」進行滌器遺訣推演。",
        "en": "👈 Enter birth date/time and gender on the left, then click 'Calculate Chart' for Di Qi Yi Jue.",
    },
    "diqiyijue_chart_title": {"zh": "🌀 滌器遺訣 / 邵子氣數", "en": "🌀 Di Qi Yi Jue / Shao Yong Qi Numerology"},
    "diqiyijue_subtab_chart": {"zh": "八宮盤", "en": "Eight Palaces"},
    "diqiyijue_subtab_analysis": {"zh": "命局分析", "en": "Chart Analysis"},
    "diqiyijue_subtab_flow": {"zh": "流籌流年", "en": "Flow-Year"},
    "diqiyijue_subtab_classic": {"zh": "古法提要", "en": "Classical Notes"},
    "diqiyijue_birth_pillars": {"zh": "四柱", "en": "Four Pillars"},
    "diqiyijue_birth_gender": {"zh": "性別", "en": "Gender"},
    "diqiyijue_metric_tai": {"zh": "胎月", "en": "Fetal Month"},
    "diqiyijue_metric_guankong": {"zh": "觀空定卦", "en": "Guankong"},
    "diqiyijue_metric_tibian": {"zh": "八卦體變", "en": "Bagua Transformation"},
    "diqiyijue_metric_destiny": {"zh": "命宮", "en": "Destiny Palace"},
    "diqiyijue_section_five_lines": {"zh": "五條與納音", "en": "Five Lines & Na Yin"},
    "diqiyijue_section_core": {"zh": "核心數據", "en": "Core Numbers"},
    "diqiyijue_section_eight_palaces": {"zh": "八宮詳情", "en": "Eight Palaces Details"},
    "diqiyijue_section_qipao": {"zh": "起胞法", "en": "Qipao Life Stages"},
    "diqiyijue_qipao_bagong": {"zh": "八宮起胞", "en": "Eight-Palace Qipao"},
    "diqiyijue_qipao_bengong": {"zh": "本宮四位起胞", "en": "Core Four-Position Qipao"},
    "diqiyijue_section_relationships": {"zh": "合孕數與陰陽合化", "en": "Pregnancy Numbers & Yin-Yang Synthesis"},
    "diqiyijue_section_mingzhu": {"zh": "命主", "en": "Inner / Outer Lords"},
    "diqiyijue_section_patterns": {"zh": "格局與關殺", "en": "Patterns & Obstacles"},
    "diqiyijue_section_fate_cycles": {"zh": "大小運", "en": "Fortune Cycles"},
    "diqiyijue_section_flow_year": {"zh": "流籌卦", "en": "Flow-Year Chart"},
    "diqiyijue_section_biefa_flow": {"zh": "本宮別法流籌", "en": "Alternate Flow Method"},
    "diqiyijue_section_method_summary": {"zh": "方法摘要", "en": "Method Summary"},
    "diqiyijue_section_classic_points": {"zh": "古法要點", "en": "Classical Points"},
    "diqiyijue_row_yuan": {"zh": "元數", "en": "Yuan Numbers"},
    "diqiyijue_row_ying": {"zh": "影數", "en": "Ying Numbers"},
    "diqiyijue_row_bengong": {"zh": "本宮四位", "en": "Core Four Positions"},
    "diqiyijue_row_biefa": {"zh": "本宮別法", "en": "Alternate Four Positions"},
    "diqiyijue_row_shuwei": {"zh": "數尾", "en": "Tail Number"},
    "diqiyijue_label_guige": {"zh": "貴格", "en": "Auspicious Patterns"},
    "diqiyijue_label_xiongxing": {"zh": "凶星", "en": "Inauspicious Stars"},
    "diqiyijue_label_guansha": {"zh": "關殺", "en": "Obstacles / Sha"},
    "diqiyijue_none": {"zh": "無", "en": "None"},
    "diqiyijue_flow_age": {"zh": "行年歲數", "en": "Running Age"},
    "diqiyijue_flow_year_ganzhi": {"zh": "流年干支（選填）", "en": "Flow-Year Ganzhi (optional)"},
    "diqiyijue_method_1": {"zh": "以月柱進干一位、進支四位求胎月，形成五條起點。", "en": "Derive the fetal month by advancing the month stem by one and the branch by four steps."},
    "diqiyijue_method_2": {"zh": "由胎干、胎支分別順數到年月日時，得到元數與影數。", "en": "Count forward from the fetal stem and branch to derive yuan and ying numbers."},
    "diqiyijue_method_3": {"zh": "以鋪地錦乘法得八宮，再依填空法、觀空定卦與八卦體變分析命局。", "en": "Generate the eight palaces by multiplication, then analyse them through void filling, guankong, and bagua transformation."},
    "diqiyijue_method_4": {"zh": "結合命宮、起胞法、合孕數與流籌法，觀察人生階段與流年變化。", "en": "Combine the destiny palace, qipao method, pregnancy numbers, and flow-year procedures for timing analysis."},
    "diqiyijue_classic_point_1": {"zh": "胎月為全盤之始，後續元影數、八宮與本宮皆由此展開。", "en": "The fetal month is the starting pivot for the entire chart."},
    "diqiyijue_classic_point_2": {"zh": "八宮空位須依年、月、日、時納音與己宮五行填補，不能直接視為無。", "en": "Void palace positions must be filled according to Na Yin and Ji-palace rules rather than treated as empty."},
    "diqiyijue_classic_point_3": {"zh": "流籌與本宮別法常配合齒卦、八觀與賊星同看，以判行運吉凶。", "en": "Flow-year analysis is read together with tooth trigram, baguan relations, and thief stars."},

    # ── 達摩一掌經 (Damo One Palm Scripture) ────────────────────
    "tab_damo": {
        "zh": "🤚 達摩一掌經",
        "en": "🤚 Damo One Palm",
    },
    "sys_hint_damo": {
        "zh": "達摩祖師掌中推命——前世今生因果輪迴",
        "en": "Damo's palm-based past-life & destiny reading",
    },
    "desc_damo": {
        "zh": (
            "**達摩一掌經**（又名一掌金），相傳由菩提達摩祖師所創。\n\n"
            "以左手掌十二地支宮位為基礎，透過年、月、日、時四柱推算出對應的"
            "十二星與六道輪迴，藉此論斷前世今生與性格命運。\n\n"
            "十二星：天貴、天厄、天權、天破、天奸、天文、天福、天驛、天孤、天刃、天藝、天壽。\n\n"
            "六道：佛道、仙道、人道、修羅道、畜道、鬼道。"
        ),
        "en": (
            "**Damo One Palm Scripture** (Yi Zhang Jin), attributed to Bodhidharma.\n\n"
            "Based on 12 Earthly Branch positions on the left palm, it uses the Four Pillars "
            "(Year, Month, Day, Hour) to determine the corresponding 12 Stars and Six Realms, "
            "revealing past lives and present destiny."
        ),
    },
    "spinner_damo": {"zh": "推算達摩一掌經中…", "en": "Computing Damo One Palm chart…"},
    "damo_chart_title": {
        "zh": "🤚 達摩一掌經 / Damo One Palm Scripture",
        "en": "🤚 Damo One Palm Scripture",
    },
    "damo_subtab_chart": {"zh": "掌中星圖", "en": "Palm Chart"},
    "damo_subtab_detail": {"zh": "詳細解讀", "en": "Detailed Reading"},
    "damo_subtab_advice": {"zh": "改運建議", "en": "Remedy & Advice"},
    "damo_subtab_classic": {"zh": "掌經原文", "en": "Classic Text"},
    "damo_four_palaces": {"zh": "四宮速覽", "en": "Four Palaces Overview"},
    "damo_realm_analysis": {"zh": "六道綜合分析", "en": "Six Realms Analysis"},
    "damo_overall_summary": {"zh": "命格總論", "en": "Overall Destiny Summary"},
    "damo_life_stages": {"zh": "人生各階段建議", "en": "Life Stage Advice"},
    "damo_remedy": {"zh": "改運法門", "en": "Remedy Methods"},
    "damo_positive_ending": {
        "zh": (
            "🙏 **相由心生，命由己造。**\n\n"
            "一掌經揭示的是前世因果的參考，而非命定的枷鎖。"
            "了解自己的命格特質後，更應積極行善、廣結善緣、修心養性。"
            "每一個善念善行，都在為今生和來世種下美好的種子。"
            "改運的最佳方法，就是從此刻開始，做一個更好的自己。"
        ),
        "en": (
            "🙏 **Your destiny is shaped by your heart and actions.**\n\n"
            "The One Palm Scripture reveals past-life patterns as guidance, not shackles. "
            "Understanding your chart empowers you to cultivate virtue, form good connections, "
            "and refine your character. Every kind thought and deed plants beautiful seeds "
            "for this life and beyond. The best way to improve your destiny is to become "
            "a better version of yourself, starting right now."
        ),
    },
    # ── Astrocartography (地點占星 / 搬遷線) ──────────────────────────────────
    "tab_acg": {
        "zh": "🌍 地點占星 ACG",
        "en": "🌍 Astrocartography",
    },
    "sys_hint_acg": {
        "zh": "搬遷線地圖：找出最適合你的城市與方位",
        "en": "Relocation map: find your best cities & directions",
    },
    "desc_acg": {
        "zh": (
            "**Astrocartography（地點占星 / 搬遷線）**\n\n"
            "由 Jim Lewis 於 1976 年創立，顯示出生時刻各行星在地球上的角度力量。\n"
            "四條線代表：上升線 (AC)、中天線 (MC)、下降線 (DC)、底天線 (IC)。\n"
            "透過搬遷線地圖，找出最適合事業、愛情、健康的城市與地區。"
        ),
        "en": (
            "**Astrocartography (Relocation Astrology)**\n\n"
            "Created by Jim Lewis in 1976, showing where each planet is angular "
            "on Earth at the moment of birth.\n"
            "Four lines: Ascendant (AC), Midheaven (MC), Descendant (DC), Imum Coeli (IC).\n"
            "Find your best cities for career, love, health and growth."
        ),
    },
    # ── Uranian Astrology (天王星占星) ────────────────────────────────────────
    "tab_uranian": {
        "zh": "♅ 天王星占星",
        "en": "♅ Uranian Astrology",
    },
    "sys_hint_uranian": {
        "zh": "漢堡學派：以天王星虛點與和諧點進行精密分析",
        "en": "Hamburg School: midpoints & transneptunian planets for precision analysis",
    },
    "spinner_uranian": {
        "zh": "正在計算天王星（漢堡學派）命盤…",
        "en": "Computing Uranian (Hamburg School) chart…",
    },
    "desc_uranian": {
        "zh": (
            "**天王星占星（漢堡學派）** — 由 Alfred Witte 於 1920–1941 年創立。\n\n"
            "• 使用 90° 轉盤（Dial），將所有強相位（合、半刑、刑、倍半刑、沖）等同於合相處理。\n"
            "• 引入八顆超海王星虛點（TNPs）：Cupido、Hades、Zeus、Kronos、"
            "Apollon、Admetos、Vulkanus、Poseidon。\n"
            "• 核心公式：行星圖像 A + B − C = D（Regelwerk für Planetenbilder）。\n"
            "• 中點樹（Midpoint Tree）揭示行星能量的對稱匯聚點。\n\n"
            "請輸入出生資料後點擊計算。"
        ),
        "en": (
            "**Uranian Astrology (Hamburg School)** — Founded by Alfred Witte 1920–1941.\n\n"
            "• Uses the 90° Dial: all hard aspects (0°, 45°, 90°, 135°, 180°) "
            "are treated as conjunctions.\n"
            "• Introduces 8 Transneptunian Planets (TNPs): Cupido, Hades, Zeus, Kronos, "
            "Apollon, Admetos, Vulkanus, Poseidon.\n"
            "• Core law: Planetary Picture A + B − C = D "
            "(*Regelwerk für Planetenbilder*).\n"
            "• Midpoint Tree reveals symmetrical energy confluence points.\n\n"
            "Enter birth data and click Calculate."
        ),
    },
    "tab_cosmobiology": {
        "zh": "🔬 宇宙生物學",
        "en": "🔬 Cosmobiology (Ebertin)",
    },
    "sys_hint_cosmobiology": {
        "zh": "Ebertin 中點樹占星：COSI 原著行星組合詮釋 · 90° 轉盤",
        "en": "Ebertin midpoint astrology: COSI planetary combinations · 90° Dial",
    },
    "spinner_cosmobiology": {
        "zh": "正在計算 Ebertin 宇宙生物學命盤…",
        "en": "Computing Ebertin Cosmobiology chart…",
    },
    "desc_cosmobiology": {
        "zh": (
            "**宇宙生物學（Cosmobiology）** — Reinhold Ebertin 創立。\n\n"
            "• 嚴格依照《行星影響力的組合》（COSI，1972年英文版）原著。\n"
            "• 中點樹：M(A/B) = (A+B)/2，容許度最大 1.5°（COSI 第9頁）。\n"
            "• 90° 轉盤：所有強相位等同於合相。\n"
            "• 完整 COSI 行星組合資料庫：原則、正面表現、負面表現。\n"
            "• 支援本命分析、合盤及過境事件比對。\n\n"
            "本模組 100% 依照 Ebertin 原著，不添加任何後世詮釋。\n\n"
            "請輸入出生資料後點擊計算。"
        ),
        "en": (
            "**Cosmobiology** — Founded by Reinhold Ebertin.\n\n"
            "• Strictly follows *The Combination of Stellar Influences* (COSI, 1972 English ed.).\n"
            "• Midpoint Tree: M(A/B) = (A+B)/2, max orb 1.5° (COSI p. 9).\n"
            "• 90° Dial: all hard aspects treated as conjunctions.\n"
            "• Full COSI planetary combination database: principle, positive, negative.\n"
            "• Natal analysis, synastry, and transit/event comparison.\n\n"
            "This module is 100% faithful to Ebertin's original works. "
            "No modern interpretations have been added.\n\n"
            "Enter birth data and click Calculate."
        ),
    },
    "acg_title": {
        "zh": "🌍 Astrocartography 搬遷線地圖",
        "en": "🌍 Astrocartography Relocation Map",
    },
    "acg_subtab_map": {
        "zh": "🗺️ 互動地圖",
        "en": "🗺️ Interactive Map",
    },
    "acg_subtab_table": {
        "zh": "📊 行星線資料",
        "en": "📊 Planet Line Data",
    },
    "acg_subtab_transit": {
        "zh": "🔄 流年搬遷線",
        "en": "🔄 Transit Lines",
    },
    "acg_line_ac": {
        "zh": "上升線 (AC) — 紅",
        "en": "Ascendant (AC) — Red",
    },
    "acg_line_mc": {
        "zh": "中天線 (MC) — 藍",
        "en": "Midheaven (MC) — Blue",
    },
    "acg_line_ic": {
        "zh": "底天線 (IC) — 綠",
        "en": "Imum Coeli (IC) — Green",
    },
    "acg_line_dc": {
        "zh": "下降線 (DC) — 紫",
        "en": "Descendant (DC) — Purple",
    },
    "acg_planet_filter": {
        "zh": "選擇行星",
        "en": "Select Planets",
    },
    "acg_line_filter": {
        "zh": "選擇線型",
        "en": "Select Line Types",
    },
    "acg_paran_header": {
        "zh": "🔗 Paran 交叉點（多線交匯能量區）",
        "en": "🔗 Paran Crossings (Multi-line Power Zones)",
    },
    "acg_transit_date": {
        "zh": "流年日期",
        "en": "Transit Date",
    },
    "acg_transit_time": {
        "zh": "流年時間",
        "en": "Transit Time",
    },
    "acg_ai_btn": {
        "zh": "🤖 AI 地點占星解盤",
        "en": "🤖 AI Astrocartography Reading",
    },
    "spinner_acg": {
        "zh": "正在計算搬遷線…",
        "en": "Computing astrocartography lines…",
    },
    "acg_no_data": {
        "zh": "請先輸入出生資料並計算。",
        "en": "Please enter birth data and calculate first.",
    },

    # ── 三式 (Sanshi — Three Styles) ───────────────────────────
    # ── 大六壬 (Da Liu Ren) ────────────────────────────────────
    "tab_liuren": {
        "zh": "🔮 六壬祿命",
        "en": "🔮 Da Liu Ren",
    },
    "sys_hint_liuren": {
        "zh": "古代三式之一，以天地盤推演吉凶",
        "en": "One of the Three Styles — celestial/terrestrial plate divination",
    },
    "desc_liuren": {
        "zh": (
            "**大六壬**\n\n"
            "大六壬為中國古代三式（太乙、奇門、六壬）之一，"
            "以日干支及月將為基礎，排列天地盤、四課、三傳，推斷吉凶。\n\n"
            "六壬排盤包含：天地盤十二神將、四課上下、三傳（初傳、中傳、末傳）、"
            "格局判斷（賊尅、元首、重審等）及各類神煞。"
        ),
        "en": (
            "**Da Liu Ren (Six Ren Astrology)**\n\n"
            "One of China's ancient Three Styles (Taiyi, Qimen, Liuren). "
            "Based on the Day Stem-Branch and Monthly General, it constructs "
            "celestial and terrestrial plates, Four Courses, and Three Transmissions "
            "to predict fortune and misfortune."
        ),
    },
    "spinner_liuren": {"zh": "正在計算大六壬排盤…", "en": "Computing Da Liu Ren chart…"},

    # ── 鬼谷分定經 (Ghost Valley Fen Ding Jing) ─────────────────────────────
    "tab_fendjing": {
        "zh": "🔮 鬼谷分定經",
        "en": "🔮 Ghost Valley Fen Ding Jing",
    },
    "tab_tojeong": {
        "zh": "🔮 土亭數",
        "en": "🔮 Tojeong Shu",
    },
    "tab_khmer": {
        "zh": "🇰🇭 高棉占星",
        "en": "🇰🇭 Khmer Astrology",
    },
    "sys_hint_khmer": {
        "zh": "柬埔寨 Reamker 史詩占星系統",
        "en": "Cambodian Reamker epic astrology system",
    },
    "desc_khmer": {
        "zh": (
            "**高棉占星（Khmer Astrology / ហោរាសាស្ត្រ Reamker）**\n\n"
            "基於 François Bizot 2013 年論文《柬埔寨占星師遺失的星盤》與 Prochom Horasastra 高棉占星彙編，"
            "重建吳哥時期失傳的 Reamker（羅摩衍那高棉版）占星系統。\n\n"
            "包含：高棉 12 生肖、ដីណាំង 八大命主、32 格預言表、ព្រួញព្រះរាម 羅摩之箭，"
            "以及傳統 bè 祭壇化解儀式。"
        ),
        "en": (
            "**Khmer Astrology (ហោរាសាស្ត្រ Reamker)**\n\n"
            "Based on François Bizot's 2013 paper \"The Lost Astrological Charts of Cambodia\" "
            "and Prochom Horasastra, reconstructing the lost Reamker (Khmer Ramayana) astrology "
            "system from the Angkor period.\n\n"
            "Includes: Khmer 12 Zodiac,ដីណាំង Eight Great Influences, 32-cell prophecy table, "
            "ព្រួញព្រះរាម Rama Arrows, and traditional bè altar remedy rituals."
        ),
    },
    "spinner_khmer": {"zh": "正在計算高棉占星盤…", "en": "Computing Khmer astrology chart…"},
    "sys_hint_fendjing": {
        "zh": "又名兩頭鉗，以年時天干排盤推斷命運",
        "en": "Also known as Two-End Pincers — destiny analysis using year and hour stems",
    },
    "desc_fendjing": {
        "zh": (
            "**鬼谷分定經**\\n\\n"
            "鬼谷分定經，又名兩頭鉗，相傳為戰國時期鬼谷子所創。"
            "以出生年干與時干為「兩頭」排盤，配合十二宮與星曜，推斷一生命運。\\n\\n"
            "排盤包含：四柱干支、兩頭鉗組合、判斷、命格、基業、兄弟、行藏、婚姻、子息、收成等。"
        ),
        "en": (
            "**Ghost Valley Fen Ding Jing (Two-End Pincers)**\\n\\n"
            "Attributed to the Warring States period sage Ghost Valley (Guiguzi), "
            "also known as \\\"Two-End Pincers.\\\" Uses birth year and hour Heavenly Stems "
            "to arrange the chart with twelve palaces and stars for destiny analysis.\\n\\n"
            "Chart includes: Four Pillars, Two-End combination, judgments, life patterns, "
            "foundation, siblings, career, marriage, children, and harvest."
        ),
    },
    "spinner_fendjing": {"zh": "正在計算鬼谷分定經…", "en": "Computing Ghost Valley chart…"},

    # ── 奇門遁甲 (Qi Men Dun Jia) ─────────────────────────────
    "tab_qimen": {
        "zh": "🚪 奇門遁甲",
        "en": "🚪 Qi Men Dun Jia",
    },
    "sys_hint_qimen": {
        "zh": "古代三式之一，九宮配天地門星神推演",
        "en": "One of the Three Styles — Nine Palace energy mapping",
    },
    "desc_qimen": {
        "zh": (
            "**奇門遁甲**\n\n"
            "奇門遁甲為中國古代三式之一，以九宮格配置天盤、地盤、八門、九星、八神，"
            "共 1080 局，推斷吉凶方位。\n\n"
            "支援拆補法與置閏法兩種排盤方式。"
        ),
        "en": (
            "**Qi Men Dun Jia (Mysterious Door Escape)**\n\n"
            "One of China's ancient Three Styles, mapping cosmic energy "
            "onto a 3×3 Nine Palace grid with Heaven/Earth plates, "
            "Eight Doors, Nine Stars, and Eight Gods — 1,080 unique configurations."
        ),
    },
    "spinner_qimen": {"zh": "正在計算奇門遁甲排盤…", "en": "Computing Qi Men Dun Jia chart…"},
    "qimen_method_label": {"zh": "排盤方法", "en": "Chart Method"},
    "qimen_method_chaibu": {"zh": "拆補法", "en": "Chaibu Method"},
    "qimen_method_zhirun": {"zh": "置閏法", "en": "Zhirun Method"},

    # ── 太乙神數 (Taiyi Shen Shu) ─────────────────────────────
    "tab_taiyi": {
        "zh": "🌟 太乙命法",
        "en": "🌟 Taiyi Life Method",
    },
    "sys_hint_taiyi": {
        "zh": "古代三式之首，太乙命法推算個人命運",
        "en": "Chief of the Three Styles — Taiyi life destiny divination",
    },
    "desc_taiyi": {
        "zh": (
            "**太乙命法（太乙神數）**\n\n"
            "太乙神數為中國古代三式之首，傳為黃帝時代所創，"
            "主要用於推算天時國運及個人命運。\n\n"
            "本系統主要顯示「太乙命法」部分：以出生年月日時計算命宮、身宮、"
            "十二宮排列、卦象、陽九百六行限、太乙諸神等，推斷個人一生運勢。"
        ),
        "en": (
            "**Taiyi Life Method (Taiyi Shen Shu)**\n\n"
            "Taiyi Shen Shu is the chief of China's Three Styles, "
            "traditionally used for predicting celestial timing, national fortune, "
            "and personal destiny.\n\n"
            "This system focuses on the Life Destiny Method: calculating Life Palace, "
            "Body Palace, Twelve Palace arrangement, hexagrams, and life progressions."
        ),
    },
    "spinner_taiyi": {"zh": "正在計算太乙命法排盤…", "en": "Computing Taiyi life chart…"},

    # ── 奇門祿命 (Qimen Destiny) ──────────────────────────────
    "tab_qimen_luming": {
        "zh": "🔮 奇門祿命",
        "en": "🔮 Qimen Destiny",
    },
    "sys_hint_qimen_luming": {
        "zh": "以出生時辰奇門遁甲局推算一生命運吉凶",
        "en": "Qimen Dunjia destiny analysis based on birth chart",
    },
    "desc_qimen_luming": {
        "zh": (
            "**奇門祿命**\n\n"
            "推人命運，以本人生時奇門之局為主，然後於局中搜尋本人生年干支局，"
            "即其為人之本命。取其本命之局，以推其一生之窮通、壽夭、吉凶、禍福，"
            "妻財子祿，俱可知也。\n\n"
            "以年干五行為主，查看各宮奇儀之生克關係，分析六親（父母、兄弟、子孫、"
            "官祿、妻財、疾厄），結合八門、八神（八將）、格局等，"
            "推斷一生窮通壽夭吉凶禍福。"
        ),
        "en": (
            "**Qimen Destiny Analysis**\n\n"
            "This method uses the Qi Men Dun Jia chart cast at the time of birth "
            "to analyze one's destiny. The year stem's palace becomes the Life Palace, "
            "and the Five Elements relationships with other stems reveal the Six Relations "
            "(parents, siblings, children, career, spouse/wealth, health), combined with "
            "Eight Doors, Eight Gods, and pattern analysis for a comprehensive life reading."
        ),
    },
    "spinner_qimen_luming": {"zh": "正在計算奇門祿命…", "en": "Computing Qimen Destiny…"},

    # ── 三式分類 (Sanshi category) ─────────────────────────────
    "cat_sanshi": {
        "zh": "三式",
        "en": "Three Styles",
    },

    # ── BPHS 帕拉夏拉 section headers & labels ────────────────
    "bphs_section_dignity": {
        "zh": "### 🏅 行星品位 (Graha Dignity)",
        "en": "### 🏅 Graha Dignity",
    },
    "bphs_caption_dignity": {
        "zh": "根據 BPHS 第5章：行星高低點與基本三角",
        "en": "BPHS Ch.5: Planetary Exaltation, Debilitation & Moola-trikona",
    },
    "bphs_section_maitri": {
        "zh": "### 🤝 行星友敵關係 (Graha Maitri)",
        "en": "### 🤝 Graha Maitri (Planetary Friendships)",
    },
    "bphs_caption_maitri": {
        "zh": "根據 BPHS 第6章：行星友敵關係",
        "en": "BPHS Ch.6: Planetary Friendships & Enmities",
    },
    "bphs_section_avastha": {
        "zh": "### 🎭 行星阿瓦斯塔 (Graha Avastha)",
        "en": "### 🎭 Graha Avastha (Planetary States)",
    },
    "bphs_caption_avastha": {
        "zh": "根據 BPHS 第15章：行星狀態章 — 12種阿瓦斯塔決定行星實際表現",
        "en": "BPHS Ch.15: Graha Avasthas — 12 states determining actual planetary effects",
    },
    "bphs_section_raja": {
        "zh": "### 👑 王者瑜伽與特殊組合 (Raja Yoga & Special Yogas)",
        "en": "### 👑 Raja Yoga & Special Yogas",
    },
    "bphs_caption_raja": {
        "zh": "根據 BPHS 第14章：王者瑜伽與特殊瑜伽",
        "en": "BPHS Ch.14: Raja Yogas & Special Yogas",
    },
    "bphs_section_bhava": {
        "zh": "### 🏛️ 宮位果報 (Bhava Phala)",
        "en": "### 🏛️ Bhava Phala (House Readings)",
    },
    "bphs_caption_bhava": {
        "zh": "根據 BPHS 第13章：各宮位行星落入的具體果報",
        "en": "BPHS Ch.13: Specific planetary effects in each bhava (house)",
    },
    "bphs_section_varga": {
        "zh": "### 📊 十六分盤參考 (Shodasa Varga)",
        "en": "### 📊 Shodasa Varga (16 Divisional Charts)",
    },
    "bphs_caption_varga": {
        "zh": "根據 BPHS 第9章：16種分盤的用途與判斷標準",
        "en": "BPHS Ch.9: Purposes and assessment criteria of the 16 divisional charts",
    },
    "bphs_caption_varga_tab": {
        "zh": "根據 BPHS 第9章：Shodasa Varga 分盤系統 — 選擇分盤查看行星在各分盤中的位置",
        "en": "BPHS Ch.9: Shodasa Varga system — select a chart to view planetary positions",
    },
    "bphs_col_planet": {
        "zh": "行星",
        "en": "Planet",
    },
    "bphs_col_sign": {
        "zh": "星座",
        "en": "Sign",
    },
    "bphs_col_dignity": {
        "zh": "品位",
        "en": "Dignity",
    },
    "bphs_col_friends": {
        "zh": "友星 ✅",
        "en": "Friends ✅",
    },
    "bphs_col_neutral": {
        "zh": "中性 ⚖️",
        "en": "Neutral ⚖️",
    },
    "bphs_col_enemies": {
        "zh": "敵星 ❌",
        "en": "Enemies ❌",
    },
    "bphs_label_avastha": {
        "zh": "狀態 (Avastha)",
        "en": "State (Avastha)",
    },
    "bphs_label_strength": {
        "zh": "強度",
        "en": "Strength",
    },
    "bphs_label_effect": {
        "zh": "果報",
        "en": "Effect",
    },
    "bphs_label_description": {
        "zh": "說明",
        "en": "Description",
    },
    "bphs_label_judgment": {
        "zh": "判斷",
        "en": "Judgment",
    },
    "bphs_label_house_lord": {
        "zh": "宮主 (Lord)",
        "en": "House Lord",
    },
    "bphs_label_lord_reading": {
        "zh": "📖 宮主落宮解讀",
        "en": "📖 House Lord Placement",
    },
    "bphs_label_planets_in": {
        "zh": "**入宮行星解讀：**",
        "en": "**Planets in Bhava:**",
    },
    "bphs_label_special_yogas": {
        "zh": "**相關特殊瑜伽：**",
        "en": "**Related Special Yogas:**",
    },
    "bphs_label_house_num": {
        "zh": "第{n}宮",
        "en": "House {n}",
    },
    "bphs_label_lord_in_house": {
        "zh": "落在第 {n} 宮",
        "en": "in House {n}",
    },
    "bphs_col_varga_chart": {
        "zh": "分盤",
        "en": "Chart",
    },
    "bphs_col_varga_name": {
        "zh": "名稱",
        "en": "Name",
    },
    "bphs_col_varga_division": {
        "zh": "切割",
        "en": "Division",
    },
    "bphs_col_varga_use": {
        "zh": "用途",
        "en": "Use",
    },
    "bphs_col_varga_judgment": {
        "zh": "判斷",
        "en": "Judgment",
    },

    # ── Picatrix / Moon longitude ──────────────────────────────
    "picatrix_moon_lon_info": {
        "zh": "🌙 使用出生月亮黃經 (Birth Moon Longitude)：{lon:.2f}°",
        "en": "🌙 Using Birth Moon Longitude: {lon:.2f}°",
    },

    # ── Hellenistic sub-sections ──────────────────────────────
    "hellen_profections_header": {
        "zh": "🗓 年度守護星 (Annual Profections)",
        "en": "🗓 Annual Profections",
    },
    "hellen_zr_header": {
        "zh": "⚙ 黃道釋放 Zodiacal Releasing (L1/L2/L3)",
        "en": "⚙ Zodiacal Releasing (L1/L2/L3)",
    },
    "hellen_lots_header": {
        "zh": "希臘點 (Greek Lots)",
        "en": "Greek Lots",
    },
    "centiloquy_header": {
        "zh": "托勒密《百論》 / Ptolemy's Centiloquy",
        "en": "Ptolemy's Centiloquy",
    },
    "centiloquy_search_label": {
        "zh": "🔍 搜尋關鍵字",
        "en": "🔍 Search keyword",
    },
    "centiloquy_no_match": {
        "zh": "未找到匹配的格言",
        "en": "No matching aphorisms found.",
    },
    "centiloquy_aphorism_num": {
        "zh": "第 {n} 條",
        "en": "Aphorism {n}",
    },

    # ── Fixed stars / Asteroids headers ───────────────────────
    "fixed_star_conjunctions_header": {
        "zh": "#### ⭐ 恆星合相 (Fixed Star Conjunctions)",
        "en": "#### ⭐ Fixed Star Conjunctions",
    },
    "asteroids_header": {
        "zh": "#### ☄️ 小行星 (Asteroids)",
        "en": "#### ☄️ Asteroids",
    },


    # ── 日本九星氣學 (Japanese Nine Star Ki) ─────────────────────
    "tab_nine_star_ki": {
        "zh": "🌟 九星氣學",
        "en": "🌟 Nine Star Ki",
    },
    "spinner_nine_star_ki": {
        "zh": "正在計算九星氣學排盤...",
        "en": "Calculating Nine Star Ki chart...",
    },
    "sys_hint_nine_star_ki": {
        "zh": "日本九星氣學 — 洛書九宮飛星命理",
        "en": "Japanese Nine Star Ki — Lo Shu Flying Star astrology",
    },
    "desc_nine_star_ki": {
        "zh": """
### 什麼是九星氣學 (Kyūsei Kigaku)？

**九星氣學 (九星気学)** 是一種源自中國洛書、在日本廣泛發展的傳統命理體系：

- **九顆飛星**：一白水星、二黑土星、三碧木星、四綠木星、五黃土星、
  六白金星、七赤金星、八白土星、九紫火星
- **洛書九宮 (Lo Shu Square)**：九星按陰遁（逆時針）順序在九宮中飛移
- **立春 (Li Chun / Risshun)**：每年約2月4日為九星氣學新年的起點
- **三命星**：本命星（年）、月命星（月）、日命星（日）
- **五行與方位**：每星對應五行（水/木/火/土/金）及八方位

輸入出生資料即可計算您的三命星及流年流月飛星。
""",
        "en": """
### What is Nine Star Ki (Kyūsei Kigaku)?

**Nine Star Ki (九星気学)** is a traditional divination system originating from the
Chinese Lo Shu square, widely developed in Japan:

- **Nine Flying Stars**: One White Water, Two Black Earth, Three Jade Wood, Four Green Wood,
  Five Yellow Earth, Six White Metal, Seven Red Metal, Eight White Earth, Nine Purple Fire
- **Lo Shu Square (洛書)**: The nine stars fly counterclockwise (Yin cycle) through nine palaces
- **Li Chun (立春 / Risshun)**: ~Feb 4 each year marks the Nine Star Ki New Year
- **Three Stars**: Year Star (Honmeisei), Month Star (Tsukimeisei), Day Star (Himeisei)
- **Five Elements & Directions**: Each star corresponds to an element and cardinal direction

Enter your birth information to calculate your Three Stars and annual flying star cycles.
""",
    },
    # ── 凱爾特樹木曆法 (Celtic Tree Calendar — Robert Graves 1948) ────
    "tab_celtic_tree": {
        "zh": "🌳 凱爾特樹木曆",
        "en": "🌳 Celtic Tree Calendar",
    },
    "spinner_celtic_tree": {
        "zh": "正在計算凱爾特樹木曆法 (Graves 1948)...",
        "en": "Calculating Celtic Tree Calendar (Graves 1948)...",
    },
    "sys_hint_celtic_tree": {
        "zh": "Robert Graves 1948 年詩意重建的 Beth-Luis-Nion 樹木字母曆",
        "en": "Beth-Luis-Nion poetic tree-alphabet calendar reconstructed by Robert Graves (1948)",
    },
    "desc_celtic_tree": {
        "zh": """
### 凱爾特樹木曆法 (Celtic Tree Calendar — Robert Graves 1948)

**⚠️ 重要說明：此為 Robert Graves 1948 年《The White Goddess》所重建的現代樹木曆法，非古代凱爾特傳統。**

**Beth-Luis-Nion 體系**由英國詩人兼學者 Robert Graves（1895–1985）在其1948年著作
《The White Goddess: A Historical Grammar of Poetic Myth》中提出。

#### 曆法結構
- **13個月**，每月約28天，以13個歐甘字母（Ogham consonants）命名
- 每年始於**12月24日**（Beth月 / 樺樹月）
- **12月23日**為「創造之日」，遊離於13個月之外（如 Graves 所言）

輸入出生資料即可查閱您的樹木月份及對應詩意屬性。
""",
        "en": """
### Celtic Tree Calendar (Robert Graves 1948)

**⚠️ This is a modern poetic reconstruction by Robert Graves (1948) — not historical ancient Celtic astrology.**

The **Beth-Luis-Nion** system was devised by British poet and scholar Robert Graves (1895–1985)
in his 1948 work *The White Goddess: A Historical Grammar of Poetic Myth*.

#### Calendar Structure
- **13 months** of ~28 days each, named after 13 Ogham consonants
- The year begins on **December 24** (Beth / Birch month)
- **December 23** is the "Day of Creation" — outside the 13 months (per Graves)

Enter your birth information to look up your tree month and its poetic attributes.
""",
    },

    # ── Advanced bodies — new section ─────────────────────────
    "enable_cross_system": {
        "zh": "🔀 啟用跨系統交叉比對",
        "en": "🔀 Enable Cross-System Comparison",
    },
    "adv_bodies_header": {
        "zh": "🌑 進階天體選項",
        "en": "🌑 Advanced Bodies Options",
    },
    "adv_asteroids_toggle": {
        "zh": "包含小行星 & 半人馬天體",
        "en": "Include Asteroids & Centaurs",
    },
    "adv_asteroids_groups": {
        "zh": "選擇天體組",
        "en": "Select Body Groups",
    },
    "adv_asteroids_helio": {
        "zh": "日心坐標（非地心）",
        "en": "Heliocentric positions",
    },
    "adv_stars_toggle": {
        "zh": "包含恆星",
        "en": "Include Fixed Stars",
    },
    "adv_stars_count": {
        "zh": "顯示恆星數量",
        "en": "Stars to display",
    },
    "adv_parans_toggle": {
        "zh": "顯示旁點（偕升偕降）",
        "en": "Show Parans (Paranatellonta)",
    },
    "adv_parans_tooltip": {
        "zh": "旁點（Parans）：計算在出生時刻同時升起、中天、降落或天底的恆星與行星對，是古典占星的重要技法。",
        "en": "Parans (Paranatellonta): fixed stars and planets that simultaneously share the same horizon or meridian circle at birth — a key technique in classical astrology.",
    },
    "adv_heliacal_toggle": {
        "zh": "顯示偕日升沒現象",
        "en": "Show Heliacal Phenomena",
    },
    "adv_heliacal_tooltip": {
        "zh": "偕日升沒（Heliacal）：行星或恆星在太陽光輝中首次或最後可見的天象，是古代占星的重要觀測技法。",
        "en": "Heliacal phenomena: the first / last visibility of a planet or star in the solar glare — an important observational technique in ancient astrology.",
    },
    "adv_asteroid_aspects_toggle": {
        "zh": "顯示小行星相位",
        "en": "Show Asteroid Aspects",
    },

    # Tab labels
    "western_subtab_asteroids": {
        "zh": "小行星 & 半人馬",
        "en": "Asteroids & Centaurs",
    },
    "western_subtab_fixed_stars": {
        "zh": "恆星",
        "en": "Fixed Stars",
    },
    "western_subtab_parans": {
        "zh": "旁點",
        "en": "Parans",
    },
    "western_subtab_heliacal": {
        "zh": "偕日升沒",
        "en": "Heliacal",
    },

    # Column / table labels
    "adv_col_body": {
        "zh": "天體",
        "en": "Body",
    },
    "adv_col_sign": {
        "zh": "星座",
        "en": "Sign",
    },
    "adv_col_degree": {
        "zh": "度數",
        "en": "Degree",
    },
    "adv_col_lat": {
        "zh": "黃緯",
        "en": "Latitude",
    },
    "adv_col_speed": {
        "zh": "速度",
        "en": "Speed",
    },
    "adv_col_retro": {
        "zh": "逆行",
        "en": "Retro",
    },
    "adv_col_meaning": {
        "zh": "含義",
        "en": "Meaning",
    },
    "adv_col_magnitude": {
        "zh": "星等",
        "en": "Mag",
    },
    "adv_col_nature": {
        "zh": "性質",
        "en": "Nature",
    },
    "adv_col_constellation": {
        "zh": "星座（西）",
        "en": "Constellation",
    },
    "adv_col_cn_name": {
        "zh": "中文星名",
        "en": "CN Name",
    },
    "adv_col_star_event": {
        "zh": "恆星方位",
        "en": "Star Point",
    },
    "adv_col_planet_event": {
        "zh": "行星方位",
        "en": "Planet Point",
    },
    "adv_col_event_date": {
        "zh": "日期",
        "en": "Date",
    },
    "adv_col_event_type": {
        "zh": "天象類型",
        "en": "Event Type",
    },
    "adv_col_orb": {
        "zh": "容許度",
        "en": "Orb",
    },
    "adv_group_chiron_pholus": {
        "zh": "凱龍 & 福魯斯",
        "en": "Chiron & Pholus",
    },
    "adv_group_lilith": {
        "zh": "黑月麗莉絲",
        "en": "Black Moon Lilith",
    },
    "adv_group_main_belt": {
        "zh": "主帶小行星（穀/智/婚/灶/健康）",
        "en": "Main Belt (Ceres/Pallas/Juno/Vesta/Hygiea)",
    },
    "adv_group_centaurs": {
        "zh": "半人馬天體（涅索斯/卡莉克蘿）",
        "en": "Centaurs (Nessus/Chariklo)",
    },
    "adv_group_tnos": {
        "zh": "海外天體（伊/伐/夸/賽）",
        "en": "TNOs (Ixion/Varuna/Quaoar/Sedna)",
    },
    "adv_group_romance": {
        "zh": "愛慾星（愛神星/賽姬星）",
        "en": "Romance (Eros/Psyche)",
    },
    "adv_group_dwarf_planets": {
        "zh": "矮行星（鬩神星）",
        "en": "Dwarf Planets (Eris)",
    },
    "adv_no_results": {
        "zh": "未找到結果。",
        "en": "No results found.",
    },
    "adv_heliacal_unavail": {
        "zh": "⚠️ 偕日升沒計算需要精確的觀測地點，且部分 Swiss Ephemeris 版本可能不支援。",
        "en": "⚠️ Heliacal calculation requires precise observer location; may not be available in all Swiss Ephemeris builds.",
    },
    # ── KP Astrology (Krishnamurti Paddhati) ─────────────────────────────────
    "tab_lal_kitab": {
        "zh": "📕 紅皮書占星",
        "en": "📕 Lal Kitab",
    },
    "sys_hint_lal_kitab": {
        "zh": "印度紅皮書業力化解占星",
        "en": "Indian Red Book karma-remedy astrology",
    },
    "desc_lal_kitab": {
        "zh": (
            "**紅皮書（Lal Kitab）**\n\n"
            "印度占星師 Pt. Roop Chand Joshi 的傳奇占星系統，"
            "以固定的卡爾普拉什坤德里（白羊=第一宮）為基礎，"
            "強調業力化解（Upay）的實用方法。"
        ),
        "en": (
            "**Lal Kitab (Red Book)**\n\n"
            "The legendary Indian astrology system by Pt. Roop Chand Joshi, "
            "using the fixed Kal Purush Kundli (Aries = House 1) "
            "and renowned for its practical karma-dissolving Upay (remedies)."
        ),
    },
    "spinner_lal_kitab": {
        "zh": "🔮 計算紅皮書命盤中…",
        "en": "🔮 Computing Lal Kitab chart…",
    },
    "tab_kp": {
        "zh": "🔮 KP 占星",
        "en": "🔮 KP Astrology",
    },
    "kp_title": {
        "zh": "克里希納穆提占星術 (KP Astrology)",
        "en": "Krishnamurti Paddhati (KP Astrology)",
    },
    "kp_subtitle": {
        "zh": "精確預測事件發生時機的印度現代占星系統",
        "en": "Modern Indian astrology system for precise event timing",
    },
    "kp_horary_mode": {
        "zh": "問卜模式 (Horary)",
        "en": "Horary Mode",
    },
    "kp_natal_mode": {
        "zh": "本命模式 (Natal)",
        "en": "Natal Mode",
    },
    "kp_planet_table": {
        "zh": "🪐 行星位置 (Planetary Positions)",
        "en": "🪐 Planetary Positions",
    },
    "kp_cusp_table": {
        "zh": "🏠 宮頭 (House Cusps)",
        "en": "🏠 House Cusps",
    },
    "kp_ruling_planets": {
        "zh": "⏰ 時辰主星 (Ruling Planets)",
        "en": "⏰ Ruling Planets",
    },
    "kp_ayanamsa": {
        "zh": "📐 歲差 (Ayanamsa)",
        "en": "📐 Ayanamsa",
    },
    "kp_ayanamsa_label": {
        "zh": "KP New Ayanamsa",
        "en": "KP New Ayanamsa",
    },
    "kp_ayanamsa_help": {
        "zh": "克里希納穆提新歲差（與 Lahiri 相差約 0°00'10\"）",
        "en": "KP New Ayanamsa (differs from Lahiri by ~0°00'10\")",
    },
    "kp_significators": {
        "zh": "🎯 徵兆星分析 (Significators)",
        "en": "🎯 Significators Analysis",
    },
    "kp_select_house": {
        "zh": "選擇宮位",
        "en": "Select House",
    },
    "kp_very_strong": {
        "zh": "極強",
        "en": "Very Strong",
    },
    "kp_strong": {
        "zh": "強",
        "en": "Strong",
    },
    "kp_weak": {
        "zh": "弱",
        "en": "Weak",
    },
    "kp_very_weak": {
        "zh": "極弱",
        "en": "Very Weak",
    },
    "kp_lordship_system": {
        "zh": "📖 KP 主星系統說明",
        "en": "📖 KP Lordship System",
    },
    "kp_rasi_lord": {
        "zh": "星座主",
        "en": "Rasi Lord",
    },
    "kp_star_lord": {
        "zh": "宿度主",
        "en": "Star Lord",
    },
    "kp_sub_lord": {
        "zh": "分主",
        "en": "Sub Lord",
    },
    "kp_sub_sub_lord": {
        "zh": "細分主",
        "en": "Sub-Sub Lord",
    },
    "kp_rasi_lord_desc": {
        "zh": "決定事件的「性質」",
        "en": "Determines the 'nature' of the event",
    },
    "kp_star_lord_desc": {
        "zh": "顯示事件的「來源」",
        "en": "Shows the 'source' of the event",
    },
    "kp_sub_lord_desc": {
        "zh": "**最重要**：決定事件「是否成立」",
        "en": "**Most Important**: Determines 'whether the event happens'",
    },
    "kp_sub_sub_lord_desc": {
        "zh": "用於精確應期判斷",
        "en": "Used for precise timing prediction",
    },
    "kp_horary_title": {
        "zh": "🔮 KP 問卜 (Horary Astrology)",
        "en": "🔮 KP Horary Astrology",
    },
    "kp_horary_desc": {
        "zh": "通過提問時刻的星盤來解答問題",
        "en": "Answer questions using the chart of the moment",
    },
    "kp_horary_question": {
        "zh": "您的問題",
        "en": "Your Question",
    },
    "kp_horary_question_placeholder": {
        "zh": "請清晰、具體地提出您的問題...",
        "en": "Ask your question clearly and specifically...",
    },
    "kp_horary_question_help": {
        "zh": "問題越具體，答案越準確。避免假設性問題。",
        "en": "The more specific the question, the more accurate the answer. Avoid hypothetical questions.",
    },
    "kp_horary_submit": {
        "zh": "🔮 開始問卜",
        "en": "🔮 Start Horary",
    },
    "kp_question_date": {
        "zh": "提問日期",
        "en": "Question Date",
    },
    "kp_question_time": {
        "zh": "提問時間",
        "en": "Question Time",
    },
    "kp_question_city": {
        "zh": "提問城市（可選）",
        "en": "Question City (optional)",
    },
    "kp_day_lord": {
        "zh": "日主 (Day Lord)",
        "en": "Day Lord",
    },
    "kp_moon_star_lord": {
        "zh": "月亮宿度主",
        "en": "Moon Star Lord",
    },
    "kp_moon_sign_lord": {
        "zh": "月亮星座主",
        "en": "Moon Sign Lord",
    },
    "kp_lagna_star_lord": {
        "zh": "上升宿度主",
        "en": "Lagna Star Lord",
    },
    "kp_lagna_sign_lord": {
        "zh": "上升星座主",
        "en": "Lagna Sign Lord",
    },
    "kp_nakshatra": {
        "zh": "宿",
        "en": "Nakshatra",
    },
    "kp_pada": {
        "zh": "Padam",
        "en": "Pada",
    },
    "kp_placidus_note": {
        "zh": "KP 使用 Placidus 宮位系統（與傳統 Vedic 的整宮制不同）",
        "en": "KP uses Placidus house system (different from Vedic Whole Sign)",
    },
    "kp_chart_svg_unavailable": {
        "zh": "🚧 **KP 星盤圖 SVG 渲染器開發中**",
        "en": "🚧 **KP SVG Chart Renderer In Development**",
    },
    "kp_chart_svg_features": {
        "zh": "計劃功能：北半球式圓盤、Sub Lord 標註、宮頭線、Nakshatra 背景色塊、Ruling Planets 高亮",
        "en": "Planned features: North Indian style, Sub Lord labels, Cusp lines, Nakshatra backgrounds, Ruling Planets highlights",
    },
    # ── 鐵板神數 (Tie Ban Shen Shu) ─────────────────────────────────
    "tab_tieban": {
        "zh": "🔮 鐵板神數",
        "en": "🔮 Tie Ban Shen Shu",
    },
    "tieban_title": {
        "zh": "鐵板神數",
        "en": "Iron Plate Divine Numbers",
    },
    "tieban_subtitle": {
        "zh": "清刻足本 · 秘鈔密碼表 · 考刻分",
        "en": "Qing Edition · Secret Code Table · Ke Fen Calculation",
    },
    "desc_tieban": {
        "zh": "🔮 **鐵板神數** — 源自宋代邵雍《皇極經世》，清代发展为精密考刻分系統。每時分 8 刻、每刻 15 分（共 120 分），結合父母六親信息精確定位命運條文。號稱「鐵口直斷」，是中國傳統術數中最精密的查表法系統。",
        "en": "🔮 **Tie Ban Shen Shu** — Originating from Shao Yong's 'Huang Ji Jing Shi' (Song Dynasty), developed into a precise Ke Fen system in Qing Dynasty. Each hour divided into 8 Ke, each Ke into 15 Fen (120 Fen total). Combined with parents' and relatives' information to precisely locate destiny verses. Known as 'Iron Mouth Direct Judgment', it is the most precise lookup system in traditional Chinese metaphysics.",
    },
    "spinner_tieban": {
        "zh": "計算鐵板神數...",
        "en": "Calculating Tie Ban Shen Shu...",
    },
    "sys_hint_tieban": {
        "zh": "精密考刻分系統，需父母六親信息佐證",
        "en": "Precise Ke Fen system requiring parents and relatives information",
    },
    "tab_shaozi": {
        "zh": "🔯 邵子神數",
        "en": "🔯 Shao Zi Shen Shu",
    },
    "shaozi_title": {
        "zh": "邵子神數",
        "en": "Shao Zi Shen Shu",
    },
    "shaozi_subtitle": {
        "zh": "邵康節神數 · 洛陽派 · 洛書九宮起集",
        "en": "Shaozi Divine Numbers · Luoyang School · Lo Shu Palace System",
    },
    "desc_shaozi": {
        "zh": "🔯 **邵子神數** — 源自北宋邵雍（邵康節）易學，與鐵板神數同根。以洛書九宮配天干起集號（1–9），後天八卦配卦取月日時位（1–8），組成四位數條文號查詢命運詩讖。",
        "en": "🔯 **Shao Zi Shen Shu** — From Shao Yong (Song Dynasty), same root as Tie Ban Shen Shu. Uses Lo Shu Nine Palaces to assign year stem collection (1–9), and Post-Heaven Bagua to derive month/day/hour digits (1–8), forming a 4-digit verse number.",
    },
    "spinner_shaozi": {
        "zh": "計算邵子神數...",
        "en": "Calculating Shao Zi Shen Shu...",
    },
    "sys_hint_shaozi": {
        "zh": "邵康節洛陽派，洛書九宮配天干，四位數條文系統",
        "en": "Luoyang school, Lo Shu Nine Palaces, 4-digit verse system",
    },
    "tab_huangji": {
        "zh": "🏮 皇極經世",
        "en": "🏮 Huangji Jingshi",
    },
    "desc_huangji": {
        "zh": (
            "🏮 **皇極經世（Huangji Jingshi）**\n\n"
            "依邵雍《皇極經世》元會運世體系計算：\n"
            "- 一元 = 129,600 年（12會 × 30運 × 12世 × 30年）\n"
            "- 出生時間定位於 元/會/運/世 與先天四卦\n"
            "- 對照歷史朝代年表，並提供與西洋/紫微/吠陀的跨系統時間主對照\n"
            "- 節氣同時顯示 kinwangji 與 Swiss Ephemeris 驗證結果"
        ),
        "en": (
            "🏮 **Huangji Jingshi** based on Shao Yong's Yuan–Hui–Yun–Shi doctrine:\n"
            "- 1 Yuan = 129,600 years (12 Hui × 30 Yun × 12 Shi × 30 years)\n"
            "- Locates natal time in cosmic cycles and mapped hexagrams\n"
            "- Includes historical timeline context and cross-system time-lord comparison\n"
            "- Shows both kinwangji and Swiss Ephemeris solar-term references"
        ),
    },
    "spinner_huangji": {
        "zh": "推演皇極經世元會運世中…",
        "en": "Computing Huangji Yuan-Hui-Yun-Shi cycles…",
    },
    "sys_hint_huangji": {
        "zh": "邵雍《皇極經世》・元會運世・先天四卦・歷史年表・跨體系時間主",
        "en": "Shao Yong Huangji Jingshi · Yuan-Hui-Yun-Shi · four hexagrams · historical context · cross-system lords",
    },
    "info_huangji_prompt": {
        "zh": "✦ 輸入出生資料後，系統將顯示你的皇極元會運世定位、四卦、歷史對照與跨體系時間主解讀。",
        "en": "✦ Enter birth data to get Huangji cycle placement, four-hexagram mapping, historical context, and cross-system time-lord synthesis.",
    },
    "huangji_tab_basic": {"zh": "基本盤", "en": "Core Pan"},
    "huangji_tab_cycles": {"zh": "大週期", "en": "Macro Cycles"},
    "huangji_tab_cross": {"zh": "跨體系對照", "en": "Cross-System"},
    "huangji_tab_history": {"zh": "歷史年表", "en": "Historical Timeline"},
    "tieban_ming_palace": {
        "zh": "命宮",
        "en": "Life Palace",
    },
    "tieban_shen_palace": {
        "zh": "身宮",
        "en": "Body Palace",
    },
    "tieban_wuxing_ju": {
        "zh": "五行局",
        "en": "Five Elements Bureau",
    },
    "tieban_ke": {
        "zh": "刻",
        "en": "Ke",
    },
    "tieban_fen": {
        "zh": "分",
        "en": "Fen",
    },
    "tieban_he_luo": {
        "zh": "河洛數",
        "en": "He Luo Number",
    },
    "tieban_number": {
        "zh": "神數號碼",
        "en": "Divine Number",
    },
    "tieban_secret_code": {
        "zh": "密碼",
        "en": "Secret Code",
    },
    "tieban_verse": {
        "zh": "條文",
        "en": "Verse",
    },
    "tieban_parents_note": {
        "zh": "💡 **提示**：鐵板神數考刻分需要父母生卒年月日時及六親信息。完整版請在側邊欄輸入父母資料以獲得更精確的結果。",
        "en": "💡 **Note**: Tie Ban Shen Shu Ke Fen calculation requires parents' birth/death dates and relatives information. For more accurate results, please input parents' data in the sidebar.",
    },
    # 十二宮名稱 (Twelve Palaces)
    "palace_life": {
        "zh": "命宮",
        "en": "Life Palace",
    },
    "palace_siblings": {
        "zh": "兄弟宮",
        "en": "Siblings Palace",
    },
    "palace_spouse": {
        "zh": "夫妻宮",
        "en": "Spouse Palace",
    },
    "palace_children": {
        "zh": "子女宮",
        "en": "Children Palace",
    },
    "palace_wealth": {
        "zh": "財帛宮",
        "en": "Wealth Palace",
    },
    "palace_health": {
        "zh": "疾厄宮",
        "en": "Health Palace",
    },
    "palace_travel": {
        "zh": "遷移宮",
        "en": "Travel Palace",
    },
    "palace_friends": {
        "zh": "交友宮",
        "en": "Friends Palace",
    },
    "palace_career": {
        "zh": "官祿宮",
        "en": "Career Palace",
    },
    "palace_property": {
        "zh": "田宅宮",
        "en": "Property Palace",
    },
    "palace_fortune": {
        "zh": "福德宮",
        "en": "Fortune Palace",
    },
    "palace_parents": {
        "zh": "父母宮",
        "en": "Parents Palace",
    },
    # 條文分類 (Verse Categories)
    "category_general": {
        "zh": "綜合",
        "en": "General",
    },
    "category_parents": {
        "zh": "父母",
        "en": "Parents",
    },
    "category_siblings": {
        "zh": "兄弟",
        "en": "Siblings",
    },
    "category_spouse": {
        "zh": "夫妻",
        "en": "Spouse",
    },
    "category_children": {
        "zh": "子女",
        "en": "Children",
    },
    "category_wealth": {
        "zh": "財運",
        "en": "Wealth",
    },
    "category_career": {
        "zh": "事業",
        "en": "Career",
    },
    "category_health": {
        "zh": "健康",
        "en": "Health",
    },
    "category_disaster": {
        "zh": "災厄",
        "en": "Disaster",
    },
    "category_travel": {
        "zh": "遷移",
        "en": "Travel",
    },
    # UI 元素
    "tieban_main_verse": {
        "zh": "主條文（神數號碼）",
        "en": "Main Verse (Divine Number)",
    },
    "tieban_palace_verses": {
        "zh": "十二宮條文",
        "en": "Twelve Palaces Verses",
    },
    "tieban_view_palace_verses": {
        "zh": "查看十二宮詳細條文",
        "en": "View Twelve Palaces Verses",
    },
    "tieban_category": {
        "zh": "分類",
        "en": "Category",
    },

    # ── 太玄數占星 ──────────────────────────────────────────
    "tab_taixuan": {
        "zh": "☰ 太玄數占星",
        "en": "☰ Tai Xuan Shu",
    },
    "sys_hint_taixuan": {
        "zh": "揚雄《太玄》八十首，干支七政聯動",
        "en": "Yang Xiong's Tai Xuan Jing, 80 Shou linked to GanZhi & Seven Luminaries",
    },
    "desc_taixuan": {
        "zh": "☰ **太玄數占星** — 源自西漢揚雄《太玄經》，仿《易》三才三分取象，八十一首×九贊，配二十八宿、七政四餘，為中國最獨特的三進制宇宙哲學體系。支援本命排盤與即時問卜雙模式。",
        "en": "☰ **Tai Xuan Shu Astrology** — Based on Yang Xiong's Tai Xuan Jing (Han Dynasty), modeled after the I Ching with a ternary cosmological system. 81 Shou × 9 Zhan, aligned with 28 Mansions and Seven Luminaries. Supports natal charting and real-time divination.",
    },
    "spinner_taixuan": {
        "zh": "計算太玄命宮首……",
        "en": "Calculating Tai Xuan Shou…",
    },
    "taixuan_natal_tab": {
        "zh": "🌟 本命排盤",
        "en": "🌟 Natal Chart",
    },
    "taixuan_qigua_tab": {
        "zh": "🎴 即時問卜",
        "en": "🎴 Divination",
    },

    # ── 五運六氣 ────────────────────────────────────────────────
    "tab_wuyunliuqi": {
        "zh": "☯ 五運六氣",
        "en": "☯ Wu Yun Liu Qi",
    },
    "sys_hint_wuyunliuqi": {
        "zh": "《黃帝內經》運氣七篇，五運六氣大運主客推演",
        "en": "Yellow Emperor's Classic: Five Movements & Six Qi traditional system",
    },
    "desc_wuyunliuqi": {
        "zh": "☯ **五運六氣** — 源自《黃帝內經·素問》運氣七篇，涵蓋大運、主運、客運、司天之氣、在泉之氣、主氣、客氣、客主加臨、運氣同化（天符歲會）、勝復鬱發等完整古典推演體系。支援每分鐘精細計算，可生成任意時段運氣變化曲線。",
        "en": "☯ **Wu Yun Liu Qi** — From the Yellow Emperor's Classic (Huangdi Neijing, Seven Chapters on Qi Movement). Covers Annual Movement, Host/Guest Movements, Heavenly Domination Qi, Earth's Spring Qi, Host/Guest Qi, Guest-Host Interaction, Assimilation (Tianfu, Suihui), and Victory-Revenge patterns. Supports minute-level precision calculation.",
    },
    "spinner_wuyunliuqi": {
        "zh": "計算五運六氣……",
        "en": "Calculating Wu Yun Liu Qi…",
    },

    # ── Picatrix + Behenian 固定星 ──────────────────────────────
    "tab_picatrix_behenian": {
        "zh": "✦ Picatrix 占星魔法",
        "en": "✦ Picatrix Star Magic",
    },
    "sys_hint_picatrix_behenian": {
        "zh": "Picatrix 十五顆 Behenian 根源恆星魔法護符系統",
        "en": "Picatrix Behenian 15 fixed-stars talisman magic system",
    },
    "desc_picatrix_behenian": {
        "zh": "✦ **Picatrix 占星魔法 + Behenian 固定星** — 源自《賢者之目的》(Ghayat al-Hakim, c.10th CE) 及 Agrippa《神秘哲學三書》(1531)，涵蓋十五顆 Behenian 根源恆星的行星主星、寶石、草藥、護符圖像與召喚詞，可偵測星盤激活並推薦最佳護符製作時機。",
        "en": "✦ **Picatrix Star Magic + Behenian Fixed Stars** — Drawn from the Ghayat al-Hakim (Picatrix, c.10th CE) and Agrippa's Three Books of Occult Philosophy (1531). Features all 15 Behenian root stars with planetary rulers, gemstones, herbs, talisman images, and invocations. Detects chart activations and recommends optimal talisman-making windows.",
    },
    "spinner_picatrix_behenian": {
        "zh": "計算 Behenian 恆星激活……",
        "en": "Computing Behenian star activations…",
    },

    # ── 出生時間校正 Birth Chart Rectification ──────────────────
    "tab_rectification": {
        "zh": "🔮 出生時間校正",
        "en": "🔮 Rectification",
    },
    "sys_hint_rectification": {
        "zh": "多技術古典校正：初級方向 · 太陽弧 · 次進法 · 小限 · 黃道釋放",
        "en": "Multi-technique classical rectification: Primary Dirs · Solar Arcs · Progressions",
    },
    "desc_rectification": {
        "zh": (
            "🔮 **出生時間校正** — 結合初級方向（Primary Directions）、太陽弧（Solar Arcs）、"
            "次進法（Secondary Progressions）、流年小限（Annual Profections）、"
            "黃道釋放（Zodiacal Releasing）及行星過境（Transits）六大技術，"
            "以加權評分算法對候選出生時間進行排名。"
            "依據 Vettius Valens《Anthology》、William Lilly《Christian Astrology》等古典文獻。"
        ),
        "en": (
            "🔮 **Birth Chart Rectification** — Combines Primary Directions, Solar Arcs, "
            "Secondary Progressions, Annual Profections, Zodiacal Releasing, and Transits "
            "with weighted scoring to rank candidate birth times. "
            "Based on Vettius Valens' Anthology and Lilly's Christian Astrology."
        ),
    },
    "spinner_rectification": {
        "zh": "校正計算中，請稍候……",
        "en": "Running rectification, please wait…",
    },
    "tab_liuyao_lifetime": {
        "zh": "🔯 六爻終身卦",
        "en": "🔯 Lifetime Liu Yao",
    },
    "desc_liuyao_lifetime": {
        "zh": "🔯 **六爻終身卦** — 以出生年月日時的農曆干支數字演算，得出固定終身本命卦象。納甲排盤，六親六神，大限流年，合婚分析，與隨機占卜截然不同的本命終身推命系統。",
        "en": "🔯 **Lifetime Liu Yao** — A fixed lifetime hexagram derived from birth date/time via lunar Ganzhi numbers. Full Najia layout, Six Relatives, Six Spirits, life periods, and compatibility analysis. Distinct from random divination.",
    },
    "spinner_liuyao_lifetime": {
        "zh": "計算六爻終身卦…",
        "en": "Computing Lifetime Liu Yao hexagram…",
    },
    "sys_hint_liuyao_lifetime": {
        "zh": "以農曆干支起卦，納甲排盤，終身本命推命系統",
        "en": "Lunar Ganzhi hexagram, Najia layout, lifetime destiny system",
    },
    "tab_medical_astrology": {
        "zh": "⚕️ 醫學占星",
        "en": "⚕️ Medical Astrology",
    },
    "desc_medical_astrology": {
        "zh": "⚕️ **醫學占星（Iatromathematics）** — 希臘・阿拉伯・中世紀歐洲古典醫學占星體系。黃道人體質分析、四液質、埃及三十六旬星身體對照、療癒擇時、疾病危機日計算。源自托勒密《四書》、蓋倫、阿維森納及卡爾佩伯傳統。",
        "en": "⚕️ **Medical Astrology (Iatromathematics)** — Classical Greek, Arabic & Medieval European medical astrology. Zodiac Man temperament analysis, four humors, Egyptian 36-decan body mapping, electional timing, and critical day calculation. Sources: Ptolemy Tetrabiblos, Galen, Avicenna, Culpeper.",
    },
    "spinner_medical_astrology": {
        "zh": "計算醫學占星排盤…",
        "en": "Computing Medical Astrology chart…",
    },
    "sys_hint_medical_astrology": {
        "zh": "希臘阿拉伯中世紀醫學占星，黃道人體質，療癒擇時",
        "en": "Classical Iatromathematics, Zodiac Man, humoral temperament, electional timing",
    },
    "info_medical_astrology_prompt": {
        "zh": "👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕查看醫學占星分析。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart' to view your Medical Astrology analysis.",
    },
    "tab_byzantine_astrology": {
        "zh": "✚ 拜占庭占星",
        "en": "✚ Byzantine Astrology",
    },
    "desc_byzantine_astrology": {
        "zh": "✚ **拜占庭占星（Byzantine Astrology）** — 東羅馬帝國占星傳統（公元4–15世紀）。融合希臘化與阿拉伯技法，涵蓋政治星盤（皇帝、城市、宗教）、基督教-占星融合、地震占（地震占）、月行占（月相預兆）、雷鳴占（雷鳴預兆）。主要人物：赫費斯提翁、保羅·亞歷山大里亞、雷托里烏斯、埃德薩的塞奧菲盧斯、約翰·阿布拉米烏斯。",
        "en": "✚ **Byzantine Astrology** — Eastern Roman Empire astrological tradition (4th–15th century CE). Bridging Hellenistic and Arabic techniques, covering political horoscopes (emperors, cities, religions), Christian-astrological syncretism, Seismologia (earthquake omens), Selenodromia (moon phase omens), Vrontologia (thunder omens). Key figures: Hephaestion of Thebes, Paulus Alexandrinus, Rhetorius of Egypt, Theophilus of Edessa, John Abramius.",
    },
    "spinner_byzantine_astrology": {
        "zh": "計算拜占庭占星排盤…",
        "en": "Computing Byzantine Astrology chart…",
    },
    "sys_hint_byzantine_astrology": {
        "zh": "東羅馬帝國占星，政治星盤，地震月相雷鳴徵兆，基督教融合",
        "en": "Eastern Roman astrology, political horoscopes, omen tables, Christian syncretism",
    },
    "info_byzantine_astrology_prompt": {
        "zh": "👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕查看拜占庭占星分析。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart' to view your Byzantine Astrology analysis.",
    },
    "tab_amazigh": {
        "zh": "ⵣ 柏柏爾占星",
        "en": "ⵣ Amazigh Astrology",
    },
    "desc_amazigh": {
        "zh": "ⵣ **Amazigh（柏柏爾）占星** — 北非柏柏爾傳統啟發的星空方位占星。整合七曜位置、固定星、Lots（命運點）與方位季節象徵，呈現以方向與節令為核心的解讀框架。",
        "en": "ⵣ **Amazigh (Berber) Astrology** — A North African Berber-inspired directional sky system integrating seven planets, fixed stars, Lots, and seasonal-direction symbolism.",
    },
    "spinner_amazigh": {
        "zh": "計算柏柏爾占星盤…",
        "en": "Computing Amazigh chart…",
    },
    "sys_hint_amazigh": {
        "zh": "北非柏柏爾占星：七曜、固定星、Lots 與方位季節象徵",
        "en": "North African Amazigh astrology: planets, fixed stars, Lots, and directional seasons",
    },
    "info_amazigh_prompt": {
        "zh": "👈 請在左側輸入排盤資料，然後點擊「開始排盤」查看柏柏爾占星。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart' to view Amazigh astrology.",
    },
    "tab_bahre_hasab": {
        "zh": "⛪ 衣索比亞 Bahre Hasab",
        "en": "⛪ Ethiopian Bahre Hasab",
    },
    "desc_bahre_hasab": {
        "zh": (
            "⛪ **Bahre Hasab（ባሕረ ሐሳብ）** — 衣索比亞正教會傳統曆法與可移動節日推算系統。\\n\\n"
            "本模組以教會計算傳統為核心，呈現：\\n"
            "- Ethiopian ↔ Gregorian 日期轉換\\n"
            "- Fasika（ፋሲካ）與禁食週期（如 ዐቢይ ጾም）\\n"
            "- Amete Alem、Wenber、Abekte、Metqi 傳統年度指標\\n"
            "- Hasabe Kewakibit（ሐሳበ ከዋክብት）週期欄位\\n\\n"
            "所有結果均標註：依據傳統 Bahre Hasab 方法。"
        ),
        "en": (
            "⛪ **Bahre Hasab (ባሕረ ሐሳብ)** — Ethiopian Orthodox traditional computus for "
            "calendar conversion and movable feasts.\\n\\n"
            "This module presents:\\n"
            "- Ethiopian ↔ Gregorian conversion\\n"
            "- Fasika and major fasting cycles\\n"
            "- Amete Alem, Wenber, Abekte, and Metqi indicators\\n"
            "- Hasabe Kewakibit cycle fields\\n\\n"
            "All outputs are explicitly marked as based on traditional Bahre Hasab method."
        ),
    },
    "spinner_bahre_hasab": {
        "zh": "正在計算 Bahre Hasab 傳統曆法...",
        "en": "Computing traditional Bahre Hasab calendar...",
    },
    "sys_hint_bahre_hasab": {
        "zh": "衣索比亞正教 Bahre Hasab：Fasika、禁食週期、Ge'ez 曆法推算",
        "en": "Ethiopian Orthodox Bahre Hasab: Fasika, fasting cycles, and Ge'ez calendrics",
    },
    "info_bahre_hasab_prompt": {
        "zh": "👈 請在左側輸入出生資料並點擊「開始排盤」，即可進入 Bahre Hasab 曆法與節日推算。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart' to open Bahre Hasab calendrical and feast computation.",
    },
    "tab_shanghan_qianfa": {
        "zh": "🌿 傷寒鈐法",
        "en": "🌿 Shanghan Qianfa",
    },
    "desc_shanghan_qianfa": {
        "zh": "🌿 **傷寒鈐法** — 以張仲景《傷寒論》六經辨證為核心，結合干支鈐法推算，依出生年支與發病日支推定六經歸屬，推薦對應經方，計算傳經預後。源自普濟方（曹樂齋）及薛氏醫案傳統。",
        "en": "🌿 **Shanghan Qianfa** — Classical Chinese medical divination based on Zhang Zhongjing's Shang Han Lun (傷寒論). Uses stem-branch (干支) Qianfa computation to identify the Six-Channel (六經) pattern from birth year branch and onset day branch, recommending classical formulas (經方) and computing transmission prognosis. Sources: Puji Fang (普濟方) and Xue's Medical Cases (薛氏醫案).",
    },
    "spinner_shanghan_qianfa": {
        "zh": "計算傷寒鈐法…",
        "en": "Computing Shanghan Qianfa…",
    },
    "sys_hint_shanghan_qianfa": {
        "zh": "傷寒論六經辨證，干支鈐法推算，經方推薦",
        "en": "Shanghan Lun Six-Channel, stem-branch Qianfa, classical formulas",
    },
    "info_shanghan_qianfa_prompt": {
        "zh": "👈 請在左側輸入出生及發病日期，點擊「開始排盤」進行傷寒鈐法推算。",
        "en": "👈 Enter birth date and onset date on the left, then click 'Calculate Chart'.",
    },
    "tab_beiji": {
        "zh": "⭐ 北極神數",
        "en": "⭐ Beiji Shenshu",
    },
    "desc_beiji": {
        "zh": "⭐ **北極神數** — 宋代邵康節（邵雍）五大神數之一，以北斗七星（破軍星）為核心，結合奇門九星、六十四卦、二十八宿。特色「簡單、神奇、快而準」，僅需出生年月日時刻即可起盤，擅長區分相同八字不同命運，可論父母、婚姻、子息、財官、學業、牢獄、陰陽宅風水等。",
        "en": "⭐ **Beiji Shenshu (North Star Divine Numbers)** — One of the Five Divine Numbers Systems of Shao Kangjie (Shao Yong), Song Dynasty. Centered on the North Star (Breaking Army Star), integrating Qimen Nine Stars, 64 Hexagrams, and 28 Lunar Mansions. Known for being simple, accurate and fast — only birth year/month/day/hour/ke needed. Excellent at distinguishing people with identical Ba Zi but different fates.",
    },
    "spinner_beiji": {
        "zh": "計算北極神數…",
        "en": "Computing Beiji Shenshu…",
    },
    "sys_hint_beiji": {
        "zh": "邵康節五大神數，北斗七星，六十四卦，快準起盤",
        "en": "Shao Kangjie's divine numbers, North Star, 64 hexagrams, fast and accurate",
    },
    "info_beiji_prompt": {
        "zh": "👈 請在左側輸入出生年月日時，點擊「開始排盤」進行北極神數推算。",
        "en": "👈 Enter birth date and time on the left, then click 'Calculate Chart' for Beiji Shenshu.",
    },
    "tab_nanji": {
        "zh": "☰ 南極神數",
        "en": "☰ Nanji Shenshu",
    },
    "desc_nanji": {
        "zh": (
            "☰ **南極神數（Nanji Shenshu）** — 中國五大神數之一《家傳秘法手稿》完整 Python 實現。"
            "以四柱八字為基礎，結合二十八星宿、建除十二辰與十八幅星圖秘訣，"
            "透過 246 條高質量手稿條文進行推演解讀。"
            "手稿核心精神：「圖為體，條文為用」「圖不破則數難起」。"
        ),
        "en": (
            "☰ **Nanji Shenshu** — One of China's Five Great Divine Numbers. "
            "Based on the Four Pillars (Bazi), integrating 28 Lunar Mansions (Xiu), "
            "Jianchu 12 Spirits, and 18 Star Chart secrets, with 246 high-quality manuscript verses. "
            "Core principle: 'The chart is the body, the verse is the function.'"
        ),
    },
    "spinner_nanji": {
        "zh": "推演南極神數命盤…",
        "en": "Computing Nanji Shenshu chart…",
    },
    "sys_hint_nanji": {
        "zh": "南極神數，四柱八字，二十八宿，建除十二辰，246條手稿條文",
        "en": "Nanji Shenshu, Four Pillars, 28 Lunar Mansions, Jianchu, 246 manuscript verses",
    },
    "info_nanji_prompt": {
        "zh": "👈 請在左側輸入出生年月日時及性別，點擊「開始排盤」進行南極神數推演。",
        "en": "👈 Enter birth date/time and gender on the left, then click 'Calculate Chart' for Nanji Shenshu.",
    },
    "tab_bazi": {
        "zh": "🀄 子平八字",
        "en": "🀄 Ziping Bazi",
    },
    "desc_bazi": {
        "zh": "🀄 **子平八字（Ziping Bazi）** — 傳統子平正宗推命體系，源自徐子平《淵海子平》、沈孝瞻《子平真詮》、萬民英《三命通會》及《滴天髓》。以年月日時四柱干支為基礎，嚴格依古法判斷格局、取用神、排大運，並提供傳統水墨命盤 SVG 視覺化。",
        "en": "🀄 **Ziping Bazi** — Traditional Ziping destiny analysis. Sources: Yuanhai Ziping (淵海子平), Ziping Zhenquan (子平真詮), Sanming Tonghui (三命通會), Ditianshui (滴天髓). Full Four Pillars, Ten Gods, Day Master strength, classic Pattern determination, Use God selection, Great Fortune Cycles, and traditional ink-style chart SVG.",
    },
    "spinner_bazi": {
        "zh": "計算子平八字命盤…",
        "en": "Computing Ziping Bazi chart…",
    },
    "sys_hint_bazi": {
        "zh": "傳統子平正宗，四柱格局用神，大運流年，水墨命盤",
        "en": "Classical Ziping Bazi, Four Pillars, Pattern, Use God, Fortune Cycles, ink-style chart",
    },
    "info_bazi_prompt": {
        "zh": "👈 請在左側輸入出生年月日時及性別，點擊「開始排盤」進行子平八字推算。",
        "en": "👈 Enter birth date/time and gender on the left, then click 'Calculate Chart' for Ziping Bazi.",
    },
    # ── 蠢子數纏度 (ChunZiShu) ────────────────────────────────────────────────
    "tab_chunzi": {
        "zh": "☵ 蠢子數",
        "en": "☵ ChunZiShu",
    },
    "desc_chunzi": {
        "zh": (
            "☵ **蠢子數纏度（ChunZiShu）** — 以二十八宿 + 七政四餘 + 度數為核心的傳統詩詞命理系統。"
            "特別擅長女命婚姻、子息、父母、事業的交叉驗證。"
            "資料庫收錄 4574 筆詩詞，代碼格式：宿名 + 星曜 + 度數 + 地支，例如：室巨9未。"
        ),
        "en": (
            "☵ **ChunZiShu (Encampment Degree)** — A traditional Chinese verse-based divination system "
            "using 28 Lunar Mansions, Seven Governors (Seven Planets + Four Remainders), and degrees. "
            "Specialises in marriage, children, parents, and career cross-verification. "
            "Database contains 4,574 verses."
        ),
    },
    "spinner_chunzi": {
        "zh": "載入蠢子數資料庫…",
        "en": "Loading ChunZiShu database…",
    },
    "sys_hint_chunzi": {
        "zh": "蠢子數纏度，二十八宿，七政四餘，4574筆詩詞，女命推算",
        "en": "ChunZiShu, 28 Lunar Mansions, Seven Governors, 4574 verses, female destiny",
    },
    "info_chunzi_prompt": {
        "zh": "👈 蠢子數為詩詞查詢工具，可直接在右側輸入代碼或關鍵字查詢，無需先排盤。",
        "en": "👈 ChunZiShu is a verse lookup tool. Enter a code or keyword on the right to search directly.",
    },
    # ── 開元占經 (Kaiyuan Zhanjing) ───────────────────────────────────────────
    "tab_kaiyuan": {
        "zh": "📜 開元占經",
        "en": "📜 Kaiyuan Zhanjing",
    },
    "desc_kaiyuan": {
        "zh": (
            "📜 **開元占經（Kaiyuan Zhanjing）** — 唐代瞿曇悉達奉詔編撰，成書於開元年間（713–741 年），"
            "是中國現存規模最大的古代星占學百科全書。全書 120 卷，系統整理甘德、石申、巫咸三家及歷代天文占驗資料，"
            "涵蓋五星入二十八宿占、月犯五星、月犯二十八宿、日月食占、五音法等核心內容。"
        ),
        "en": (
            "📜 **Kaiyuan Zhanjing** — Compiled by Qutan Xida (瞿曇悉達) by imperial order during the Kaiyuan era "
            "(713–741 CE) of the Tang Dynasty. The largest surviving Chinese encyclopaedia of astral omen divination, "
            "comprising 120 volumes. Covers five-planet mansion omens, Moon vs. five planets, Moon vs. 28 lunar mansions, "
            "solar/lunar eclipse omens, and the Five-Sounds (Wu Yin) method."
        ),
    },
    "spinner_kaiyuan": {
        "zh": "載入開元占經資料庫…",
        "en": "Loading Kaiyuan Zhanjing database…",
    },
    "sys_hint_kaiyuan": {
        "zh": "開元占經，五星入宿，月占，日食占，五音法，唐代星占",
        "en": "Kaiyuan Zhanjing, five-planet mansion omens, moon omens, solar eclipse, Five Sounds, Tang Dynasty",
    },
    "info_kaiyuan_prompt": {
        "zh": "👈 開元占經為古典星占查詢工具，可直接在右側選擇查詢項目，無需先排盤。",
        "en": "👈 Kaiyuan Zhanjing is a classical omen lookup tool. Select a category on the right to search directly.",
    },
    # ── Sumerian / Mesopotamian Astrology (蘇美/美索不達米亞占星) ──────────────
    "tab_sumerian": {
        "zh": "𒀭 蘇美/美索不達米亞占星",
        "en": "𒀭 Sumerian / Mesopotamian",
    },
    "desc_sumerian": {
        "zh": (
            "**蘇美 / 美索不達米亞占星**\n\n"
            "人類最古老的占星傳統，源自公元前 3000 年的美索不達米亞文明。\n\n"
            "**核心文獻：**\n"
            "- **MUL.APIN 星表**（約公元前 1000 年）：66 顆恆星/星座的昏旦時間，12 宮黃道分割，"
            "三路天球分帶（恩利爾/安努/埃阿之路）\n"
            "- **Enūma Anu Enlil**（約 70 片泥板，公元前 2000–500 年）：史上最龐大天文預兆集，"
            "將行星運行與國家命運對應\n"
            "- **K.8538 尼尼微星盤**（約公元前 650 年）：已知最早的圓形星圖，8 區間楔形泥板\n\n"
            "七大行星神：Šamaš（太陽）、Sîn（月）、Ištar（金星）、Nabû（水星）、"
            "Nergal（火星）、Marduk（木星）、Ninurta（土星）"
        ),
        "en": (
            "**Sumerian / Mesopotamian Astrology**\n\n"
            "Humanity's oldest astrological tradition, originating in Mesopotamia c. 3000 BCE.\n\n"
            "**Core sources:**\n"
            "- **MUL.APIN** (~1000 BCE): 66 stars/constellations with heliacal risings, 12-sign sidereal "
            "zodiac, three sky paths (Enlil / Anu / Ea)\n"
            "- **Enūma Anu Enlil** (~70 tablets, 2000–500 BCE): the world's largest omen series, "
            "linking planetary phenomena to royal and national fate\n"
            "- **K.8538 Nineveh Planisphere** (~650 BCE): the oldest known circular star map, "
            "8-sector wedge-shaped clay tablet\n\n"
            "Seven planetary deities: Šamaš (Sun), Sîn (Moon), Ištar (Venus), Nabû (Mercury), "
            "Nergal (Mars), Marduk (Jupiter), Ninurta (Saturn)"
        ),
    },
    "spinner_sumerian": {
        "zh": "計算蘇美/美索不達米亞星盤中…",
        "en": "Computing Sumerian / Mesopotamian chart…",
    },
    "sys_hint_sumerian": {
        "zh": "MUL.APIN 星表，Enūma Anu Enlil 預兆，K.8538 尼尼微星盤，七大行星神",
        "en": "MUL.APIN star catalogue, Enūma Anu Enlil omens, K.8538 planisphere, seven planetary deities",
    },
    "info_sumerian_prompt": {
        "zh": "👈 請在左側輸入排盤資料，然後點擊「開始排盤」按鈕查看蘇美/美索不達米亞占星分析。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart' to view your Sumerian / Mesopotamian Astrology analysis.",
    },
    # ── Etruscan Astrology (伊特魯里亞占星) ─────────────────────────────────────
    "tab_etruscan": {
        "zh": "🏺 伊特魯里亞占星",
        "en": "🏺 Etruscan Astrology",
    },
    "desc_etruscan": {
        "zh": (
            "### 伊特魯里亞占星 — 皮亞琴察青銅肝臟\n\n"
            "**伊特魯里亞占星**源自公元前 7–1 世紀的義大利伊特魯里亞文明，"
            "是羅馬占星術的重要前身之一。其核心文獻是 **皮亞琴察青銅肝臟**（Fegato di Piacenza，"
            "約公元前 100 年），一枚銅製羊肝模型，外緣刻有 16 個「天宮區域」（Templum）。\n\n"
            "#### 🏺 宇宙模型：天宮十六區（Templum XVI）\n"
            "伊特魯里亞占星師（**haruspices**）面朝南方，"
            "將天空分為從正北起順時針每 22.5° 的 16 個區域，每區由一位或一組神靈主宰：\n"
            "- **Tin 廷尼亞（廷 / 朱庇特）** 掌管雷霆與天象（第 1–3 區）\n"
            "- **Uni / Juno** 守護婚姻與女性（第 4 區）\n"
            "- **Usil / 太陽神** 帶來光明與農業吉兆（第 6 區）\n"
            "- **Nethuns / 尼普頓** 主宰水域（第 7 區）\n"
            "- **Fufluns / 巴克斯** 代表歡宴與生命力（第 9 區）\n\n"
            "#### ⚡ 閃電占卜（Fulgural Divination）\n"
            "廷尼亞神持有 **九種雷霆**，每種雷霆從不同天宮區域降下，"
            "代表吉凶迥異的神意。依雷霆降落的方向判斷吉凶。\n\n"
            "#### 🔮 肝臟占卜（Haruspicy）\n"
            "動物（通常為羊）的肝臟被視為宇宙的縮影，"
            "其形狀、顏色、紋路與天宮方位對應，用於占卜國家大事。"
        ),
        "en": (
            "### Etruscan Astrology — The Piacenza Bronze Liver\n\n"
            "**Etruscan Astrology** originated in the Etruscan civilisation of Italy "
            "(c. 7th–1st century BCE) and is a significant precursor to Roman astrology. "
            "Its central artefact is the **Piacenza Bronze Liver** (*Fegato di Piacenza*, "
            "c. 100 BCE), a bronze sheep liver inscribed with 16 sky regions called *Templa*.\n\n"
            "#### 🏺 The Cosmic Model: Templum XVI\n"
            "Etruscan diviners (**haruspices**) faced south and divided the sky into "
            "16 sectors of 22.5° each, going clockwise from north. "
            "Each sector is governed by a deity:\n"
            "- **Tin / Tinia (Jupiter)** rules thunder and celestial signs (Regions 1–3)\n"
            "- **Uni / Juno** protects marriage and women (Region 4)\n"
            "- **Usil / the Sun God** brings light and agricultural omens (Region 6)\n"
            "- **Nethuns / Neptune** governs waters (Region 7)\n"
            "- **Fufluns / Bacchus** symbolises feasting and vital force (Region 9)\n\n"
            "#### ⚡ Lightning Divination (*Fulgural Divination*)\n"
            "Tinia wields **nine thunderbolts**, each descending from a different region "
            "and carrying distinct divine messages of fortune or misfortune.\n\n"
            "#### 🔮 Haruspicy\n"
            "A sacrificial animal's liver (usually sheep) is regarded as a microcosm of "
            "the cosmos, with its lobes, colours, and markings mapped to the Templum "
            "sky-regions for divination of state affairs."
        ),
    },
    "spinner_etruscan": {
        "zh": "正在計算伊特魯里亞天宮排盤…",
        "en": "Computing Etruscan Templum chart…",
    },
    "sys_hint_etruscan": {
        "zh": "皮亞琴察青銅肝臟，天宮16區，廷尼亞九雷，haruspicy，閃電占卜",
        "en": "Piacenza Bronze Liver, Templum XVI, Tinia's nine thunderbolts, haruspicy, lightning divination",
    },
    "sys_hint_armenian": {
        "zh": "亞美尼亞黃道、Haykian 古曆、Orion(Hayk) 連結、Arevakhach 象徵與古手稿美學",
        "en": "Armenian zodiac names, Haykian calendar mapping, Orion/Hayk linkage, Arevakhach symbolism and manuscript aesthetics",
    },
    "info_etruscan_prompt": {
        "zh": "👈 請在左側輸入排盤資料，點擊「開始排盤」以查看你的伊特魯里亞天宮排盤、皮亞琴察肝臟視覺化，以及閃電神諭解讀。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart' to view your Etruscan Templum chart, the interactive Piacenza Liver, and the lightning oracle reading.",
    },
    "tab_armenian": {
        "zh": "✶ 亞美尼亞占星",
        "en": "✶ Armenian Astrology",
    },
    "desc_armenian": {
        "zh": (
            "### Armenian Astrology（亞美尼亞占星）\n\n"
            "以 **Swiss Ephemeris** 為計算核心（預設 Tropical，可選 Sidereal），"
            "並將十二宮星座名稱完整映射為亞美尼亞語符號系統。\n\n"
            "- Armenian Zodiac 名稱（英語 + Հայերեն + transliteration）\n"
            "- Haykian Calendar 近似換算（MVP）\n"
            "- Orion / Hayk 可見度旗標\n"
            "- 祖靈／命運關鍵詞（luminary + angular house）\n"
            "- 支援 Natal、Transit、Secondary Progression、Solar Return"
        ),
        "en": (
            "### Armenian Astrology\n\n"
            "MVP built on Swiss Ephemeris computations (Tropical by default, optional Sidereal), "
            "with sign metadata remapped to Armenian naming and symbolic context.\n\n"
            "- Armenian zodiac names (EN + Armenian + transliteration)\n"
            "- Haykian calendar approximation\n"
            "- Orion/Hayk visibility marker\n"
            "- Ancestral keywords (luminaries + angular houses)\n"
            "- Natal, Transit, Secondary Progression, Solar Return"
        ),
    },
    "spinner_armenian": {
        "zh": "正在計算亞美尼亞星盤…",
        "en": "Computing Armenian chart…",
    },
    "info_armenian_prompt": {
        "zh": "👈 請在左側輸入出生資料，點擊「開始排盤」以查看 Armenian Zodiac 映射、Haykian 古曆與文化註記。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart' to view Armenian zodiac mapping, Haykian calendar markers, and cultural notes.",
    },
    "tab_horary": {
        "zh": "📜 傳統卜卦占星",
        "en": "📜 Traditional Horary",
    },
    "desc_horary": {
        "zh": (
            "📜 **傳統卜卦占星（Traditional Horary Astrology）** — "
            "融合西方 Lilly / Bonatti 傳統與吠陀《Prasna Marga》體系。"
            "西方面向嚴格遵循 William Lilly《Christian Astrology》（1647）與 Guido Bonatti《Liber Astronomiae》（~1277）規則："
            "Significators、本質尊貴與偶然尊貴、入相／離相相位、光之傳遞與聚合、虛空月、判斷障礙等。"
            "吠陀面向依《Prasna Marga》計算問卦命宮、阿魯達命宮（Arudha Lagna）及傳統問卦判斷法。"
        ),
        "en": (
            "📜 **Traditional Horary Astrology** — "
            "Combines Western Lilly/Bonatti tradition with Vedic Prasna Marga. "
            "Western horary strictly follows William Lilly's *Christian Astrology* (1647) and "
            "Guido Bonatti's *Liber Astronomiae* (~1277): Significators, Essential & Accidental Dignities, "
            "applying/separating aspects, Translation & Collection of Light, Void of Course Moon, "
            "and Strictures Against Judgment. "
            "Vedic Prashna follows *Prasna Marga* with Prasna Lagna, Arudha Lagna, and classical judgment rules."
        ),
    },
    "spinner_horary": {
        "zh": "計算傳統卜卦占星…",
        "en": "Computing Traditional Horary chart…",
    },
    "sys_hint_horary": {
        "zh": "Lilly/Bonatti 卜卦、虛空月、光之傳遞、吠陀問卦、Arudha Lagna",
        "en": "Lilly/Bonatti horary, VOC Moon, Translation of Light, Vedic Prashna, Arudha Lagna",
    },
    "info_horary_prompt": {
        "zh": "👈 請在左側輸入問卦時間與地點，點擊「開始排盤」後在卜卦占星頁面輸入問題進行判斷。",
        "en": "👈 Enter the time and location of the question on the left, then click 'Calculate Chart' and enter your question in the Horary tab.",
    },
    "tab_sports_astrology": {
        "zh": "🏟️ 運動占星",
        "en": "🏟️ Sports Astrology",
    },
    "desc_sports_astrology": {
        "zh": (
            "🏟️ **運動占星（Sports Astrology）** — 以 John Frawley 傳統問卜法為主軸，"
            "結合比賽開賽 Event Chart 與球隊/選手本命對照。"
            "核心判準含 1宮/7宮主星、尊貴、入相/離相、Reception、10宮勝利、"
            "6/12宮傷病風險、月亮流程與爆冷指標，輸出概率化勝負傾向。"
        ),
        "en": (
            "🏟️ **Sports Astrology** — centered on John Frawley's traditional horary method, "
            "combined with event-chart kickoff timing and team/player natal comparison. "
            "Core testimonies include 1st/7th lords, dignities, applying/separating aspects, "
            "reception, 10th-house victory indications, 6th/12th injury risk, lunar flow, "
            "and upset indicators with probabilistic output."
        ),
    },
    "spinner_sports_astrology": {
        "zh": "正在計算運動占星分析…",
        "en": "Computing sports astrology analysis…",
    },
    "sys_hint_sports_astrology": {
        "zh": "Frawley 運動占星、1/7宮勝負、Event Chart、球隊本命對照、爆冷指標",
        "en": "Frawley sports horary, 1st/7th win judgment, event chart, team natal comparison, upset indicators",
    },
    "info_sports_astrology_prompt": {
        "zh": "👈 請先輸入比賽與隊伍資訊，再執行運動占星分析以取得勝率傾向與關鍵證據。",
        "en": "👈 Enter match and team details, then run sports astrology analysis for win probabilities and key testimonies.",
    },
    "tab_esoteric": {
        "zh": "✨ 靈性占星（七道光線）",
        "en": "✨ Esoteric Astrology (Seven Rays)",
    },
    "sys_hint_esoteric": {
        "zh": "Alice Bailey 七道光線體系 · 靈魂光線 · 靈性統治星 · 靈性進化路徑",
        "en": "Alice Bailey Seven Rays · Soul Ray · Esoteric Rulers · Spiritual Evolution Path",
    },
    "spinner_esoteric": {
        "zh": "正在計算靈性占星七道光線命盤…",
        "en": "Computing Esoteric Astrology Seven Rays chart…",
    },
    "desc_esoteric": {
        "zh": (
            "**靈性占星（Esoteric Astrology）** — Alice A. Bailey 七道光線體系。\n\n"
            "• 嚴格依照《秘傳占星》（*Esoteric Astrology*，七道光線論文第三卷，1951年）。\n"
            "• 七道光線完整實作：意志/力量、愛-智慧、主動智性、和諧、具體科學、奉獻、典禮秩序。\n"
            "• 靈性統治星（Esoteric Rulers）：Bailey 定義的每個星座靈魂層次統治星。\n"
            "• 靈魂光線（Soul Ray）與人格光線（Personality Ray）傾向性指標分析。\n"
            "• 七道光線曼陀羅 SVG 視覺化：神聖幾何、七芒星、彩色光線效果。\n"
            "• 幻相（Glamours）識別與靈性服務方向分析。\n\n"
            "⚠️ 靈魂光線判斷具有解釋性質，非機械公式。最終確認需靈性洞察。\n\n"
            "請輸入出生資料後點擊計算。"
        ),
        "en": (
            "**Esoteric Astrology** — Alice A. Bailey's Seven Rays System.\n\n"
            "• Strictly follows *Esoteric Astrology* (A Treatise on the Seven Rays, Vol. III, 1951).\n"
            "• Full Seven Rays: Will/Power, Love-Wisdom, Active Intelligence, Harmony, "
            "Concrete Science, Devotion, Ceremonial Order.\n"
            "• Esoteric Rulers: Bailey's soul-level rulers for all 12 signs.\n"
            "• Soul Ray and Personality Ray tendency indicators.\n"
            "• Seven Rays Mandala SVG: sacred geometry, heptagram, ray beam effects.\n"
            "• Glamour identification and spiritual service direction analysis.\n\n"
            "⚠️ Soul Ray determination is indicative, not mechanical. "
            "Final confirmation requires spiritual insight.\n\n"
            "Enter birth data and click Calculate."
        ),
    },
    "info_esoteric_prompt": {
        "zh": "👈 請輸入出生資料後點擊「開始排盤」，進行靈性占星七道光線分析。",
        "en": "👈 Enter birth data and click 'Calculate Chart' to begin the Seven Rays Esoteric Astrology analysis.",
    },
    "info_maya_prompt": {
        "zh": "👈 請在左側輸入出生日期，點擊「開始排盤」以計算您的 Tzolk'in 日符號、Long Count 位置與完整瑪雅命盤。",
        "en": "👈 Enter your birth date on the left and click 'Calculate Chart' to discover your Tzolk'in day sign, Long Count position, and full Maya chart.",
    },
    "info_dogon_sirius_prompt": {
        "zh": "👈 請在左側輸入出生資料，點擊「開始排盤」以查看你與 Dogon 天狼星傳統（Po Tolo／Nommo／Sigui）的連結。",
        "en": "👈 Enter your birth data on the left and click 'Calculate Chart' to explore your connection with Dogon Sirius traditions (Po Tolo/Nommo/Sigui).",
    },
    "info_andean_prompt": {
        "zh": "👈 請在左側輸入出生資料，點擊「開始排盤」以查看你在印加天河（Mayu）中的暗星宿守護、出生動物靈，以及銀河占星解讀。",
        "en": "👈 Enter your birth data on the left and click 'Calculate Chart' to see your Andean Mayu sky map, dark-cloud constellation guardians, and birth animal spirit.",
    },
    "info_bintang_duabelas_prompt": {
        "zh": "👈 直接在頁面內輸入姓名、星期或時間，即可使用馬來伊斯蘭占星 Bintang Duabelas（十二星）的 Abjad、Hisab Nama、十二星宮、行星時辰與 Azimat 工具。",
        "en": "👈 Enter names, weekday, or time directly on the page to use the Malay Islamic astrology Bintang Duabelas (Twelve Stars) Abjad, Hisab Nama, twelve-house, planetary-hour, and Azimat tools.",
    },
    "info_kinketika_prompt": {
        "zh": "👈 可直接輸入日期時間，切換 Ketika Lima（五時刻）或 Bintang Tujuh（七星時刻），查看吉凶輪盤、活動規劃與每日吉凶總覽。",
        "en": "👈 Enter date/time, switch between Ketika Lima and Bintang Tujuh, and view the wheel, activity planner, and daily fortune overview.",
    },
    # ── Astronomical Geomancy (地占占星) ───────────────────────────────────
    "tab_astro_geomancy": {
        "zh": "🔮 地占占星",
        "en": "🔮 Astronomical Geomancy",
    },
    "desc_astro_geomancy": {
        "zh": (
            "### 地占占星 — Gerardus Cremonensis 地占占星\n\n"
            "**地占占星（Astronomical Geomancy / Geomantia Astronomica）**源自12世紀"
            "阿拉伯－拉丁學者 **Gerardus Cremonensis**（杰拉德·克雷莫納，約1114–1187年）"
            "的原典手稿。\n\n"
            "#### 核心機制\n"
            "傳統地占占卜結合古典占星的宮位系統：\n"
            "- 使用傳統幾何方式產生 **母親圖形**（4條隨機點線）\n"
            "- 第一個母親圖形決定**上升圖形**，對應 Gerard 原典的**上升星座**\n"
            "- 依序填滿 **12宮** 的星座（每宮 30°）\n"
            "- 7顆古典行星 + 龍頭（☊）+ 龍尾（☋）各以隨機點數法決定落宮\n\n"
            "#### 16個地占圖形\n"
            "每個圖形由4行點陣構成，奇數點為「•」，偶數點為「∶」：\n"
            "Acquisitio（白羊）、Laetitia（金牛）、Puer/Rubeus（雙子）、Albus（巨蟹）、"
            "Via（獅子）、Conjunctio/Caput（處女）、Puella（天秤）、Amissio/Tristitia（天蠍）、"
            "Cauda Draconis（射手）、Populus（摩羯）、Fortuna Major（水瓶）、Carcer（雙魚）\n\n"
            "#### 占卜應用\n"
            "此系統可解答生命、健康、財富、婚姻、事業、旅程等各類問題，"
            "依據行星落宮、星座性質與 Gerard 傳統判斷規則進行解讀。\n\n"
            "👈 請在左側選擇「地占占星」，點擊進入後輸入問題起卦。"
        ),
        "en": (
            "### Astronomical Geomancy — Gerardus Cremonensis\n\n"
            "**Astronomical Geomancy (Geomantia Astronomica)** originates from the 12th-century "
            "Arabic-Latin scholar **Gerardus Cremonensis** (Gerard of Cremona, c. 1114–1187).\n\n"
            "#### Core Mechanism\n"
            "Traditional geomantic divination combined with the classical astrological house system:\n"
            "- Generate **mother figures** using traditional random point counting (4 rows)\n"
            "- The first mother figure determines the **Ascendant figure**, mapped to a zodiac sign\n"
            "  per Gerard's authentic correspondence table\n"
            "- Fill the remaining **12 houses** sequentially through the zodiac (30° per house)\n"
            "- 7 classical planets + Caput Draconis (☊) + Cauda Draconis (☋) are each assigned "
            "  to a house via random remainder (mod 12) calculation\n\n"
            "#### 16 Geomantic Figures\n"
            "Each figure consists of 4 rows of dots — odd count = single (•), even = double (∶):\n"
            "Acquisitio (Aries), Laetitia (Taurus), Puer/Rubeus (Gemini), Albus (Cancer), "
            "Via (Leo), Conjunctio/Caput (Virgo), Puella (Libra), Amissio/Tristitia (Scorpio), "
            "Cauda Draconis (Sagittarius), Populus (Capricorn), Fortuna Major (Aquarius), "
            "Carcer (Pisces)\n\n"
            "#### Divination Applications\n"
            "This system addresses questions about life, health, wealth, marriage, career, and "
            "journeys, using planetary house placements, sign qualities, and Gerard's traditional "
            "interpretive rules.\n\n"
            "👈 Select 'Astronomical Geomancy' in the sidebar, then enter your question to cast the chart."
        ),
    },
    "spinner_astro_geomancy": {
        "zh": "正在起卦地占占星盤...",
        "en": "Casting Astronomical Geomancy chart...",
    },
    "sys_hint_astro_geomancy": {
        "zh": "Gerard Cremonensis 12世紀地占占星：16圖形 × 12宮 × 9行星",
        "en": "Gerard Cremonensis 12th-c. geomantic astrology: 16 figures × 12 houses × 9 planets",
    },
    "info_astro_geomancy_prompt": {
        "zh": (
            "🔮 請點擊左側「地占占星」進入系統，在頁面上方輸入你的問題並選擇問題類型，"
            "然後點擊「起卦占卜」產生地占占星盤。此系統不需要出生資料，以傳統隨機點數法起卦。"
        ),
        "en": (
            "🔮 Click 'Astronomical Geomancy' in the sidebar to enter the system. "
            "Enter your question and select a question type at the top of the page, "
            "then click 'Cast the Chart' to generate your geomantic wheel. "
            "This system requires no birth data — it casts the chart via traditional random point counting."
        ),
    },
    "tab_european_geomancy": {
        "zh": "🜃 歐洲地占",
        "en": "🜃 European Geomancy",
    },
    "desc_european_geomancy": {
        "zh": (
            "### 歐洲地占（European Geomancy）\n\n"
            "以文藝復興時期的歐洲地占傳統為核心：\n"
            "- 完整 16 圖形（拉丁名、元素、行星、星座對應）\n"
            "- 盾形圖（Shield Chart）完整鏈條：母親、女兒、姪輩、見證、判官、調解者\n"
            "- 十二宮圖（House Chart）結合占星宮位主題\n"
            "- 支援傳統點數、硬幣、隨機數與手動輸入起卦\n"
            "- 提供結構化解讀與占星連結解讀，可直接餵給 AI 進行深度報告"
        ),
        "en": (
            "### European Geomancy\n\n"
            "A Renaissance-oriented implementation of classical European geomancy:\n"
            "- Full 16 figures with Latin names and astrological correspondences\n"
            "- Complete Shield Chart chain (mothers, daughters, nieces, witnesses, judge, reconciler)\n"
            "- 12-house chart with astrological house topics\n"
            "- Casting modes: traditional dots, coins, random numbers, and manual input\n"
            "- Structured interpretation plus astrology bridge, ready for AI deep analysis"
        ),
    },
    "spinner_european_geomancy": {
        "zh": "正在生成歐洲地占圖表...",
        "en": "Generating European Geomancy charts...",
    },
    "sys_hint_european_geomancy": {
        "zh": "文藝復興歐洲地占：16圖形 × 盾形圖 × 十二宮圖",
        "en": "Renaissance European geomancy: 16 figures × Shield Chart × House Chart",
    },
    "info_european_geomancy_prompt": {
        "zh": "🜃 進入後可直接輸入問題起卦，不需要出生資料。",
        "en": "🜃 Enter your question directly to cast; no birth data required.",
    },
    "tab_electional": {
        "zh": "⏳ 擇日占星（Electional / Muhurta）",
        "en": "⏳ Electional Astrology / Muhurta",
    },
    "desc_electional": {
        "zh": (
            "⏳ **擇日占星（Electional Astrology & Vedic Muhurta）** — "
            "融合西方傳統擇日與印度吠陀擇時兩大古典體系。\n\n"
            "**西方傳統擇日（William Lilly / Guido Bonatti）：**\n"
            "• 行星時（Planetary Hours）— Chaldean 順序，Lilly CA p. 483\n"
            "• 月亮狀態：虛空月（Void of Course）、焦途（Via Combusta）、入相相位\n"
            "• 本質尊貴：入廟、入旺、失陷、落陷\n"
            "• 九種常見活動類型擇日規則：婚姻、開業、簽約、搬家、旅行、手術等\n"
            "• 支援「驗證特定時間」與「搜尋最佳時段」兩種模式\n\n"
            "**吠陀擇時（Muhurta Chintamani / Kalaprakashika / BPHS）：**\n"
            "• 五曆（Panchanga）：Tithi、Vara、Nakshatra、Yoga、Karana\n"
            "• Gandanta 點判斷（水象/火象星座交界）\n"
            "• Vishti Karana（毘濕提/凶刃）偵測\n"
            "• 婚姻擇日：木星/金星可見性、那舍特拉吉凶\n"
            "• 命宮（Lagna）吉凶判斷\n\n"
            "請輸入時間地點後點擊「開始排盤」，或使用搜尋模式尋找最佳吉時。"
        ),
        "en": (
            "⏳ **Electional Astrology & Vedic Muhurta** — "
            "Combines the Western Classical Electional tradition with the Vedic Muhurta system.\n\n"
            "**Western Electional (William Lilly / Guido Bonatti):**\n"
            "• Planetary Hours (Chaldean order, Lilly CA p. 483)\n"
            "• Moon state: Void of Course, Via Combusta, applying aspects, phase\n"
            "• Essential dignities: domicile, exaltation, detriment, fall, peregrine\n"
            "• Rules for 9 common activity types: marriage, business, contracts, relocation, "
            "travel, surgery, property, litigation, meetings\n"
            "• Two modes: validate a specific time or search for best windows\n\n"
            "**Vedic Muhurta (Muhurta Chintamani / Kalaprakashika / BPHS):**\n"
            "• Panchanga (5 limbs): Tithi, Vara, Nakshatra, Yoga, Karana\n"
            "• Gandanta detection (water/fire sign junctions)\n"
            "• Vishti Karana (Bhadra) detection\n"
            "• Vivaha Muhurta: Jupiter/Venus visibility, Nakshatra quality\n"
            "• Lagna (sidereal ascendant) auspiciousness\n\n"
            "Enter date/time/location and click Calculate, or use Search mode to find optimal windows."
        ),
    },
    "spinner_electional": {
        "zh": "計算擇日占星…",
        "en": "Computing Electional / Muhurta chart…",
    },
    "sys_hint_electional": {
        "zh": "西方擇日Lilly/Bonatti、行星時、吠陀五曆、婚姻擇日、Panchanga",
        "en": "Western Electional Lilly/Bonatti, Planetary Hours, Vedic Panchanga, Muhurta, Vivaha",
    },
    "info_electional_prompt": {
        "zh": "👈 請在左側輸入時間與地點，點擊「開始排盤」後選擇活動類型進行擇日分析，或使用搜尋模式找出最佳吉時。",
        "en": "👈 Enter date, time and location on the left, click 'Calculate Chart', then select an activity type for electional analysis or use Search mode to find optimal windows.",
    },
    "tab_harmonic": {
        "zh": "🎵 和諧占星",
        "zh_cn": "🎵 和谐占星",
        "en": "🎵 Harmonic Astrology",
    },
    "sys_hint_harmonic": {
        "zh": "John Addey 諧波體系，5H 才能，7H 靈性，9H 進化，神聖幾何曼陀羅",
        "zh_cn": "John Addey 谐波体系，5H 才能，7H 灵性，9H 进化，神圣几何曼陀罗",
        "en": "John Addey harmonics: H5 talent, H7 spirituality, H9 evolution, sacred geometry mandalas",
    },
    "spinner_harmonic": {
        "zh": "正在計算和諧占星盤…",
        "zh_cn": "正在计算和谐占星盘…",
        "en": "Computing Harmonic Astrology charts…",
    },
    "desc_harmonic": {
        "zh": (
            "🎵 **和諧占星（Harmonic Astrology）** — John Addey 創立。\n\n"
            "• 嚴格依照 John Addey《Harmonics in Astrology》（1976）及 David Hamblin《Harmonic Charts》（1983）。\n"
            "• 核心原理：第 N 諧波盤 = 所有行星經度 × N（mod 360°）。\n"
            "• 5H（五諧波）：天賦與創意表現的最重要指標。\n"
            "• 7H（七諧波）：靈性、神秘直覺與業力關係。\n"
            "• 9H（九諧波）：靈性進化與高層意識。\n"
            "• 支援 H1、H2、H3、H4、H5、H7、H9、H12 及自訂諧波。\n"
            "• 神聖幾何曼陀羅 SVG 視覺化（每個諧波獨特色彩主題）。\n"
            "• 多諧波綜合分析（Hamblin 行星重點識別法）。\n\n"
            "請輸入出生資料後點擊計算。"
        ),
        "en": (
            "🎵 **Harmonic Astrology** — Founded by John Addey.\n\n"
            "• Strictly follows John Addey's *Harmonics in Astrology* (1976) "
            "and David Hamblin's *Harmonic Charts* (1983).\n"
            "• Core principle: Nth Harmonic Chart = all longitudes × N (mod 360°).\n"
            "• H5 (5th Harmonic): the premier indicator of talent and creative expression.\n"
            "• H7 (7th Harmonic): spirituality, mystical intuition, karmic bonds.\n"
            "• H9 (9th Harmonic): spiritual evolution and elevated consciousness.\n"
            "• Supports H1, H2, H3, H4, H5, H7, H9, H12 and custom harmonics.\n"
            "• Sacred geometry Mandala SVG visuals (unique color theme per harmonic).\n"
            "• Multi-harmonic analysis (Hamblin planetary emphasis method).\n\n"
            "Enter birth data and click Calculate."
        ),
    },
    "info_harmonic_prompt": {
        "zh": "👈 請在左側輸入出生年月日時及地點，點擊「開始排盤」進行和諧占星分析。",
        "zh_cn": "👈 请在左侧输入出生年月日时及地点，点击「开始排盘」进行和谐占星分析。",
        "en": "👈 Enter birth date, time and location on the left, then click 'Calculate Chart' for Harmonic Astrology analysis.",
    },
    "tab_primary_directions": {
        "zh": "⚷ 古典主限推運",
        "zh_cn": "⚷ 古典主限推运",
        "en": "⚷ Primary Directions",
    },
    "sys_hint_primary_directions": {
        "zh": "Placidus 半弧世間主限 · Ptolemy 黃道主限 · 奈包德時間鍵 · 古典時機推算",
        "zh_cn": "Placidus 半弧世间主限 · Ptolemy 黄道主限 · 奈包德时间键 · 古典时机推算",
        "en": "Placidus Mundo Semi-Arc · Ptolemy Zodiacal · Naibod Key · Classical timing technique",
    },
    "spinner_primary_directions": {
        "zh": "正在計算古典主限推運…",
        "zh_cn": "正在计算古典主限推运…",
        "en": "Computing Classical Primary Directions…",
    },
    "desc_primary_directions": {
        "zh": (
            "⚷ **古典主限推運（Primary Directions）** — 西方古典占星最核心的時機推算體系。\n\n"
            "• 起源於 Claudius Ptolemy《占星四書》（約 150 CE），後由 Regiomontanus（1490）與 Placidus de Titis（1657）加以精算。\n"
            "• **世間主限（Mundo / Placidus 半弧法）**：最精準的傳統方法，依行星在晝弧中的比例位置計算推運弧。\n"
            "• **黃道主限（Zodiacal / Ptolemy 斜升法）**：以斜升度差計算推運弧，歷史最悠久的方法。\n"
            "• 支援五大相位：合相、六分、四分、三分、對分，以及赤緯平行。\n"
            "• 支援順向主限（Direct）與逆向主限（Converse）。\n"
            "• 時間鍵：奈包德鍵（0.9856°/年，最傳統）、托勒密鍵（1°/年）、太陽弧鍵。\n"
            "• 古典手稿風格 SVG 時間軸視覺化（仿文藝復興占星書籍設計）。\n\n"
            "請輸入出生資料後點擊計算。"
        ),
        "en": (
            "⚷ **Classical Primary Directions** — The most fundamental timing technique of Western classical astrology.\n\n"
            "• Originates with Claudius Ptolemy's *Tetrabiblos* (c. 150 CE); refined by Regiomontanus (1490) "
            "and Placidus de Titis (*Primum Mobile*, 1657).\n"
            "• **Mundo Directions (Placidus Semi-Arc)**: Most precise traditional method, using the "
            "proportional position within the Placidus diurnal semi-arc.\n"
            "• **Zodiacal Directions (Ptolemy Oblique Ascension)**: Uses oblique ascension differences; "
            "the oldest method.\n"
            "• Supports five major aspects: conjunction, sextile, square, trine, opposition, plus parallels.\n"
            "• Both Direct and Converse directions supported.\n"
            "• Time keys: Naibod (0.9856°/yr — most traditional), Ptolemy (1°/yr), Solar Arc.\n"
            "• Classical manuscript-style SVG timeline (Renaissance astronomical book aesthetic).\n\n"
            "Enter birth data and click Calculate."
        ),
    },
    "info_primary_directions_prompt": {
        "zh": "👈 請在左側輸入出生年月日時及地點，點擊「開始排盤」進行古典主限推運分析。",
        "zh_cn": "👈 请在左侧输入出生年月日时及地点，点击「开始排盘」进行古典主限推运分析。",
        "en": "👈 Enter birth date, time and location on the left, then click 'Calculate Chart' for Primary Directions analysis.",
    },
    "tab_trutine_of_hermes": {
        "zh": "☿ 赫密士前世盤",
        "en": "☿ Trutine of Hermes",
    },
    "sys_hint_trutine_of_hermes": {
        "zh": "赫密士出生前世盤，托勒密《百句箴言》，月亮↔上升點互換，靈魂入身印記",
        "en": "Prenatal Epoch, Ptolemy Centiloquium, Moon↔ASC/DSC reciprocity, soul incarnation imprint",
    },
    "desc_trutine_of_hermes": {
        "zh": (
            "☿ **赫密士出生前世盤（Trutine of Hermes / Prenatal Epoch）** — "
            "古典希臘化占星術中最深刻的靈魂層級技術。\n\n"
            "• **核心法則**（托勒密《百句箴言》第51條）：月亮在地平線上方→前世盤上升 = 本命月亮；"
            "月亮在地平線下方→前世盤下降 = 本命月亮。\n"
            "• **妊娠期回推**：從出生時刻回推約273天（9個太陰月），搜尋受孕星盤。\n"
            "• **靈魂層級解讀**：前世盤代表靈魂選擇化身時的天象印記，揭示此世的靈魂任務。\n"
            "• **校正驗證**：誤差 < 1° 可強力佐證出生時間準確性。\n"
            "• **雙圈天球圖**：前世盤（外環）× 本命盤（內環）可視化對照。\n"
            "• **跨盤相位**：前世盤與本命盤之間的相位揭示靈魂計劃與現實命運的對話。\n\n"
            "支援三種歷史方法：赫密士/托勒密經典法、貝利標準法（1916）、賽法利亞爾太陽紀元法。\n\n"
            "請輸入出生資料後點擊計算。"
        ),
        "en": (
            "☿ **Trutine of Hermes (Prenatal Epoch)** — "
            "The most profound soul-level technique in classical Hellenistic astrology.\n\n"
            "• **Core Rule** (Ptolemy Centiloquium Ap. 51): Moon above horizon → Epoch ASC = Natal Moon; "
            "Moon below → Epoch DSC = Natal Moon.\n"
            "• **Gestation Retrograde**: Searches ~273 days before birth for the Conception chart.\n"
            "• **Soul-Level Insights**: The Epoch represents the soul's celestial imprint at incarnation.\n"
            "• **Rectification Validation**: Orb < 1° strongly confirms birth time accuracy.\n"
            "• **Dual Zodiac Wheel**: Epoch (outer ring) × Natal (inner ring) visualisation.\n"
            "• **Cross-Chart Aspects**: Epoch-Natal aspects reveal the soul plan vs lived life dialogue.\n\n"
            "Supports three historical methods: Classical Hermes/Ptolemy, Bailey Standard (1916), "
            "Sepharial Solar Epoch.\n\n"
            "Enter birth data and click Calculate."
        ),
    },
    "spinner_trutine_of_hermes": {
        "zh": "計算前世盤中，請稍候…",
        "en": "Computing Prenatal Epoch chart, please wait…",
    },
    "info_trutine_of_hermes_prompt": {
        "zh": "👈 請在左側輸入出生資料，然後點擊「開始排盤」查看赫密士前世盤分析。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart' to view your Prenatal Epoch analysis.",
    },
    # ── Human Design 人間圖 ────────────────────────────────────────────────────
    "tab_human_design": {
        "zh": "☯ 人間圖（Human Design）",
        "en": "☯ Human Design",
    },
    "sys_hint_human_design": {
        "zh": "Ra Uru Hu · 類型/策略/權威 · 九大中心 · BodyGraph · 閘門/通道",
        "en": "Ra Uru Hu · Type/Strategy/Authority · Nine Centers · BodyGraph · Gates/Channels",
    },
    "spinner_human_design": {
        "zh": "正在計算人間圖命盤（包含設計日期太陽弧計算）…",
        "en": "Computing Human Design chart (including Solar Arc Design date)…",
    },
    "desc_human_design": {
        "zh": (
            "☯ **人間圖（Human Design）** — Ra Uru Hu 1987年創立，融合易經（I-Ching）、"
            "占星學、卡巴拉生命樹、印度脈輪系統與量子物理。\n\n"
            "**五大類型（Types）：**\n"
            "• 顯示者（Manifestor）~8% — 策略：告知；簽名：平靜\n"
            "• 生產者（Generator）~37% — 策略：回應；簽名：滿足\n"
            "• 顯示生產者（Manifesting Generator）~33% — 策略：回應後告知；簽名：滿足與平靜\n"
            "• 投射者（Projector）~21% — 策略：等待邀請；簽名：成功\n"
            "• 反映者（Reflector）~1% — 策略：等待月亮週期；簽名：驚喜\n\n"
            "**核心計算（pyswisseph 高精度）：**\n"
            "• 有意識命盤（Personality）= 出生時刻的行星位置\n"
            "• 無意識命盤（Design）= 太陽弧約88°前的行星位置（約88天）\n"
            "• Rave Mandala 64閘門映射，精確到六爻線位\n"
            "• 九大中心定義判斷、36通道分析、類型/策略/權威推算\n"
            "• 人生十字架（Incarnation Cross）四閘門確認\n\n"
            "請輸入出生資料後點擊計算。"
        ),
        "en": (
            "☯ **Human Design** — Founded by Ra Uru Hu in 1987, synthesizing "
            "the I-Ching, Astrology, Kabbalah Tree of Life, Hindu Chakra system, "
            "and Quantum Physics.\n\n"
            "**Five Types:**\n"
            "• Manifestor ~8% — Strategy: To Inform; Signature: Peace\n"
            "• Generator ~37% — Strategy: To Respond; Signature: Satisfaction\n"
            "• Manifesting Generator ~33% — Strategy: Respond + Inform; Signature: Satisfaction & Peace\n"
            "• Projector ~21% — Strategy: Wait for Invitation; Signature: Success\n"
            "• Reflector ~1% — Strategy: Wait & Reflect (lunar cycle); Signature: Surprise\n\n"
            "**Core Calculations (pyswisseph precision):**\n"
            "• Personality chart = planetary positions at exact birth time\n"
            "• Design chart = positions when Sun was ~88° Solar Arc before birth (~88 days)\n"
            "• Rave Mandala 64-gate mapping precise to hexagram line\n"
            "• Nine-center definition, 36 channels, Type/Strategy/Authority\n"
            "• Incarnation Cross (4 Sun/Earth gate activations)\n\n"
            "Enter birth data and click Calculate."
        ),
    },
    "info_human_design_prompt": {
        "zh": "👈 請在左側輸入出生資料，點擊「開始排盤」進行人間圖分析。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart' for your Human Design analysis.",
    },

    # ── Mundane Astrology 世俗占星 / 國家占星 ──────────────────────────────────
    "tab_mundane": {
        "zh": "🌍 世俗占星",
        "en": "🌍 Mundane Astrology",
    },
    "sys_hint_mundane": {
        "zh": "國家占星・入宮圖・日月食・木土大合相・時代脈動",
        "en": "National Astrology · Ingress Charts · Eclipses · Great Conjunctions · World Trends",
    },
    "desc_mundane": {
        "zh": (
            "🌍 **世俗占星（Mundane Astrology）** — 研究國家、時代與世界大事的占星分支。\n\n"
            "• **入宮圖（Ingress Chart）**：太陽進入基本星座（春分牡羊、夏至巨蟹、秋分天秤、冬至摩羯），"
            "預示國家與世界的季節性趨勢。\n"
            "• **日月食圖（Eclipse Chart）**：日食影響長達 6–12 個月，月食約 1 個月，"
            "揭示重大國家事件。\n"
            "• **木土大合相（Great Conjunctions）**：每約 20 年一次的木星-土星合相，"
            "標誌時代轉折。2020 年進入風象三角（寶瓶座），開啟資訊科技新紀元。\n"
            "• **國家運勢總覽**：選擇國家，結合外行星過運與入宮圖進行宏觀分析。\n\n"
            "融合西方 Mundane 傳統（Campion、Baigent、Lilly）與中國欽天監天象紀事傳統。\n"
            "AI 以欽天監星官人格，莊重詩意地解讀時代星象。"
        ),
        "en": (
            "🌍 **Mundane Astrology** — The branch of astrology studying nations, eras, and world events.\n\n"
            "• **Ingress Charts**: Sun's entry into cardinal signs (Aries/Cancer/Libra/Capricorn) "
            "forecasting seasonal national and world trends.\n"
            "• **Eclipse Charts**: Solar eclipses influence 6–12 months; lunar eclipses ~1 month, "
            "revealing major national events.\n"
            "• **Great Conjunctions**: Jupiter-Saturn conjunctions every ~20 years, marking historical "
            "turning points. The 2020 Aquarius conjunction opened the Air era of information and technology.\n"
            "• **National Overview**: Select any country for macro outer-planet transit analysis.\n\n"
            "Synthesises Western Mundane tradition (Campion, Baigent, Lilly) with "
            "Chinese Imperial Astronomical Bureau (欽天監) sky-omen records."
        ),
    },
    "spinner_mundane": {
        "zh": "計算世俗占星星盤中…",
        "en": "Computing Mundane Astrology chart…",
    },
    "info_mundane_prompt": {
        "zh": "👈 世俗占星不需出生資料，直接點擊左側頁面進行分析。",
        "en": "👈 Mundane Astrology does not require birth data. Use the controls within each tab.",
    },
    # ── 吠陀風水（Vastu Shastra）──────────────────────────────────────────────
    "spinner_vastu": {
        "zh": "正在計算個人化 Vastu Purusha Mandala…",
        "en": "Computing personalized Vastu Purusha Mandala…",
    },
    "desc_vastu": {
        "zh": (
            "### 🪔 吠陀風水（Vastu Shastra）\n\n"
            "**Vastu Shastra**（梵文：वास्तु शास्त्र）是源自印度吠陀時代的古典建築風水學，"
            "與吠陀占星（Jyotish）並列為「吠陀輔學（Vedāngas）」的重要支柱。\n\n"
            "**KinAstro Astro-Vastu 整合特色：**\n"
            "- **個人化 Vastu Purusha Mandala**：結合命盤 Lagna（上升星座）與九曜行星位置，"
            "高亮顯示最受影響的方位能量場\n"
            "- **9 宮格內部方位** + **32 外環天神位（Pada）**：完整 Paramasayika 9×9 曼荼羅\n"
            "- **房屋朝向診斷**：支援 8 方位選擇，分析居所朝向與命盤的相容性\n"
            "- **Vastu Compliance Score**：量化個人化吉祥指數（0–100）\n"
            "- **八大方位完整解讀**：含主宰神祇、五大元素、推薦顏色、房間配置與 Dosha 補救\n\n"
            "| 核心典籍 | 年代 | 內容 |\n"
            "|:---------|:-----|:-----|\n"
            "| Mayamata | 5–15 世紀 | 建築比例、方位能量、Pada 天神 |\n"
            "| Manasara | 梵文古典 | 建築規範、空間配置 |\n"
            "| Bṛhat Saṃhitā | Varāhamihira, 5 世紀 | 天文占星與建築結合 |\n\n"
            "🕉️ **Om Vastu Devaya Namah** — 願 Vastu 之神保佑您的居所平安吉祥"
        ),
        "en": (
            "### 🪔 Vastu Shastra — Vedic Architectural Science\n\n"
            "**Vastu Shastra** (Sanskrit: वास्तु शास्त्र) is the ancient Indian science of "
            "space, architecture, and environmental harmony — a sister discipline to Jyotish (Vedic Astrology).\n\n"
            "**KinAstro Astro-Vastu Integration Features:**\n"
            "- **Personalized Vastu Purusha Mandala**: Combines Lagna (Ascendant) and planetary "
            "positions to highlight key directional energy zones\n"
            "- **9 Inner Zones** + **32 Outer Padas (Guardian Deities)**\n"
            "- **House Facing Analysis**: 8-direction selector with natal chart compatibility\n"
            "- **Vastu Compliance Score**: Personalized auspiciousness index (0–100)\n"
            "- **Full 8-Direction Interpretations**: Deity, element, colors, rooms, Dosha remedies\n\n"
            "🕉️ **Om Vastu Devaya Namah** — May the Vastu Devata bless your dwelling"
        ),
    },
    "sys_hint_vastu": {
        "zh": "吠陀風水 Vastu Purusha Mandala · 個人化方位分析 · Compliance Score · 房間配置",
        "en": "Vastu Purusha Mandala · Personalized directional analysis · Compliance Score · Room placement",
    },
    "info_vastu_prompt": {
        "zh": "👈 請在左側輸入出生資料並點擊「開始排盤」，再選擇居所朝向，即可生成個人化 Vastu Purusha Mandala。",
        "en": "👈 Enter birth data on the left and click 'Calculate Chart', then select your house facing direction to generate a personalized Vastu Purusha Mandala.",
    },

    # ── 弗拉德命運輪盤（Fludd Rota Simulator）────────────────────────────────
    "tab_fludd_rota": {
        "zh": "⚙ 弗拉德命運輪盤",
        "en": "⚙ Fludd Rota Simulator",
    },
    "desc_fludd_rota": {
        "zh": (
            "### ⚙ 弗拉德命運輪盤（Fludd Rota Simulator）\n\n"
            "靈感來自 Robert Fludd（1574–1637）1617 年著作《Utriusque Cosmi Historia》"
            "（宇宙兩界史）中的占卜輪盤（Rota）。\n\n"
            "**四層輪盤結構：**\n\n"
            "| 層級 | 內容 | 控制行星 | 象徵 |\n"
            "|------|------|----------|------|\n"
            "| 第一層（最外）| 古典字母 + 符號 | ☉ 太陽 + ASC 上升點 | 宇宙語言、意識表達 |\n"
            "| 第二層 | 羅馬數字 I–XII | ☽ 月亮 | 命運之宮、情感週期 |\n"
            "| 第三層 | 七古典行星符號 | ☿ 水星 + ♀ 金星 | 溝通、美感、智識 |\n"
            "| 第四層（最內）| 十二星座命運區域 | ♂ 火星 + ♃ 木星 + ♄ 土星 | 宏觀命運走向 |\n\n"
            "月交點（☊ 北交點 / ☋ 南交點）作為解讀調節因子，影響吉凶傾向。\n\n"
            "輸入出生星盤行星度數後，系統自動旋轉各層輪盤至對應位置，並生成古典弗拉德風格解讀。"
            "各層亦支援滑鼠拖曳自由旋轉。"
        ),
        "en": (
            "### ⚙ Fludd Rota Simulator\n\n"
            "Inspired by Robert Fludd's (1574–1637) divination wheel (Rota) from "
            "*Utriusque Cosmi Historia* (1617).\n\n"
            "**Four-layer concentric wheel:**\n\n"
            "| Ring | Content | Controlling Planets | Symbolism |\n"
            "|------|---------|---------------------|-----------|\n"
            "| Ring 1 (outermost) | Classical letters + symbols | ☉ Sun + ASC | Cosmic language, consciousness |\n"
            "| Ring 2 | Roman numerals I–XII | ☽ Moon | Fate houses, emotional cycles |\n"
            "| Ring 3 | Seven classical planet glyphs | ☿ Mercury + ♀ Venus | Communication, beauty, intellect |\n"
            "| Ring 4 (innermost) | Twelve zodiac fate zones | ♂ ♃ ♄ | Macro destiny direction |\n\n"
            "Lunar Nodes (☊ North Node / ☋ South Node) act as interpretation modifiers "
            "affecting auspiciousness without directly controlling rotation.\n\n"
            "Enter natal chart planetary degrees; the system auto-rotates each ring to "
            "its chart-determined position and generates a classical Fludd-style reading. "
            "Each ring also supports free mouse-drag rotation."
        ),
    },
    "spinner_fludd_rota": {
        "zh": "正在旋轉弗拉德命運輪盤…",
        "en": "Spinning the Fludd Rota…",
    },
    "sys_hint_fludd_rota": {
        "zh": "Fludd 1617 · 四層輪盤 · 行星度數驅動 · 可拖曳旋轉 · 古典銅版雕刻風格",
        "en": "Fludd 1617 · 4-layer wheel · planet-driven rotation · drag-to-spin · classical engraving style",
    },
    "info_fludd_rota_prompt": {
        "zh": "✦ 輸入出生星盤行星度數，點擊「根據星盤設定輪盤並解讀」以啟動弗拉德命運輪盤占卜。",
        "en": "✦ Enter natal chart planetary degrees and click 'Set Wheel from Chart & Interpret' to activate the Fludd Rota divination.",
    },

    # ── 煉金占星 Alchemical Astrology ──────────────────────────────────────────
    "tab_alchemical_astrology": {
        "zh": "⚗️ 煉金占星",
        "en": "⚗️ Alchemical Astrology",
    },
    "desc_alchemical_astrology": {
        "zh": (
            "### ⚗️ 煉金占星（Alchemical Astrology）\n\n"
            "嚴格以 **帕拉塞爾蘇斯（Paracelsus, 1493–1541）** 傳統為基礎的煉金占星系統，"
            "涵蓋行星–金屬–草藥–礦物–人體對應關係（Signatures 符號論）及煉金過程與占星能量的整合。\n\n"
            "**主要文獻來源：**\n"
            "- Paracelsus《Coelum Philosophorum》\n"
            "- Paracelsus《Concerning the Spirits of the Planets》\n"
            "- Paracelsus《Astronomia Magna》\n"
            "- Cornelius Agrippa《Three Books of Occult Philosophy》\n\n"
            "**七大行星對應系統：**\n\n"
            "| 行星 | 金屬 | 代表草藥 | 人體部位 | 煉金階段 |\n"
            "|------|------|----------|----------|----------|\n"
            "| ☉ 太陽 Sol | 黃金 Gold | 聖約翰草、番紅花 | 心臟 | Citrinitas |\n"
            "| ☽ 月亮 Luna | 白銀 Silver | 艾草、月草 | 腦、體液 | Albedo |\n"
            "| ♂ 火星 Mars | 鐵 Iron | 苦艾草、大蒜 | 膽囊 | Nigredo |\n"
            "| ☿ 水星 Mercury | 汞 Quicksilver | 茴香、薰衣草 | 肺、神經 | — |\n"
            "| ♃ 木星 Jupiter | 錫 Tin | 龍牙草、鼠尾草 | 肝臟 | Rubedo |\n"
            "| ♀ 金星 Venus | 銅 Copper | 鐵線蕨、馬鞭草 | 腎臟 | Albedo |\n"
            "| ♄ 土星 Saturn | 鉛 Lead | 聚合草、問荊 | 脾臟、骨骼 | Nigredo |"
        ),
        "en": (
            "### ⚗️ Alchemical Astrology\n\n"
            "A rigorously document-based alchemical astrology system grounded in the "
            "**Paracelsian (1493–1541)** tradition, covering planet–metal–herb–mineral–body "
            "correspondences (Doctrine of Signatures) and the integration of alchemical "
            "processes with planetary energies.\n\n"
            "**Primary Sources:**\n"
            "- Paracelsus *Coelum Philosophorum*\n"
            "- Paracelsus *Concerning the Spirits of the Planets*\n"
            "- Paracelsus *Astronomia Magna*\n"
            "- Cornelius Agrippa *Three Books of Occult Philosophy*\n\n"
            "**Seven Planets Correspondence System:**\n\n"
            "| Planet | Metal | Key Herb | Body Part | Alch. Stage |\n"
            "|--------|-------|----------|-----------|-------------|\n"
            "| ☉ Sun Sol | Gold | St John's Wort, Saffron | Heart | Citrinitas |\n"
            "| ☽ Moon Luna | Silver | Mugwort, Moonwort | Brain, Humours | Albedo |\n"
            "| ♂ Mars | Iron | Wormwood, Garlic | Gallbladder | Nigredo |\n"
            "| ☿ Mercury | Quicksilver | Fennel, Lavender | Lungs, Nerves | — |\n"
            "| ♃ Jupiter | Tin | Agrimony, Sage | Liver | Rubedo |\n"
            "| ♀ Venus | Copper | Maidenhair Fern, Vervain | Kidneys | Albedo |\n"
            "| ♄ Saturn | Lead | Comfrey, Horsetail | Spleen, Bones | Nigredo |"
        ),
    },
    "spinner_alchemical_astrology": {
        "zh": "正在計算煉金行星對應…",
        "en": "Computing alchemical planetary correspondences…",
    },
    "sys_hint_alchemical_astrology": {
        "zh": "Paracelsus 傳統 · 行星–金屬–草藥對應 · Signatures 符號論 · 四大煉金階段 · 100% 文獻依據",
        "en": "Paracelsian tradition · Planet–Metal–Herb · Doctrine of Signatures · 4 Alchemical Stages · 100% documented",
    },
    "info_alchemical_astrology_prompt": {
        "zh": "✦ 輸入出生資料並計算星盤，系統將根據帕拉塞爾蘇斯傳統顯示你的行星煉金對應與個人化解讀。",
        "en": "✦ Enter birth data and compute the chart; the system will display your personal planetary alchemical correspondences based on the Paracelsian tradition.",
    },
}

def get_ui_lang() -> str:
    """Return the full UI language code: 'zh', 'zh_cn', or 'en'."""
    import streamlit as st
    return st.session_state.get("lang", "zh")


def get_lang() -> str:
    """Return normalised language code for content: 'zh' or 'en'.

    Simplified Chinese ('zh_cn') is normalised to 'zh' so that all
    existing ``lang == "zh"`` checks throughout the codebase continue
    to return Chinese content.
    """
    lang = get_ui_lang()
    if lang == "zh_cn":
        return "zh"
    return lang


try:
    from opencc import OpenCC as _OpenCC
    _T2S_CONVERTER = _OpenCC('t2s')
except Exception:
    _T2S_CONVERTER = None

from functools import lru_cache as _lru_cache


@_lru_cache(maxsize=4096)
def _t2s(text: str) -> str:
    """Convert Traditional Chinese text to Simplified Chinese using OpenCC."""
    if _T2S_CONVERTER is not None:
        return _T2S_CONVERTER.convert(text)
    return text


def auto_cn(text: str, en_text: str = "") -> str:
    """Return *text* in the appropriate language.

    When an *en_text* fallback is supplied the function acts as a bilingual
    selector: Chinese variants (``zh`` / ``zh_cn``) receive *text* and all
    other languages receive *en_text*.  For ``zh_cn``, *text* is additionally
    converted from Traditional to Simplified Chinese.

    When called with only *text* (no *en_text*), the original behaviour is
    preserved: *text* is returned as-is for non-Simplified UI languages, and
    converted to Simplified Chinese for ``zh_cn``.

    Use this helper to wrap any Chinese string that is **not** sourced from
    ``TRANSLATIONS`` (which is already handled by :func:`t`).
    """
    lang = get_ui_lang()
    if en_text and lang not in ("zh", "zh_cn"):
        return en_text
    if lang == "zh_cn":
        return _t2s(text)
    return text


def t(key: str) -> str:
    """Return the translated string for *key* in the current language.

    For zh_cn, falls back to zh (Traditional) if no explicit zh_cn entry
    exists, and automatically converts to Simplified Chinese.
    """
    lang = get_ui_lang()
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
