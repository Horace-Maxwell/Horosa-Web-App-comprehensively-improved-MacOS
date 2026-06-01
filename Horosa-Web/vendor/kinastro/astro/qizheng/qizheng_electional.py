"""
astro/qizheng_electional.py — 擇日工具 (Electional Astrology)

Date selection based on heavenly stems/branches and divine stars.
"""
import swisseph as swe
from dataclasses import dataclass, field

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
WEEKDAY_CN = ["一", "二", "三", "四", "五", "六", "日"]

ACTIVITY_TYPES = {
    "marriage": {"cn": "嫁娶", "good_stars": ["天德", "月德", "天喜"], "bad_stars": ["天刑", "白虎"]},
    "travel": {"cn": "出行", "good_stars": ["驛馬", "天德"], "bad_stars": ["五鬼", "死門"]},
    "business": {"cn": "開市", "good_stars": ["天財", "祿神"], "bad_stars": ["劫煞", "歲破"]},
    "moving": {"cn": "搬遷", "good_stars": ["天德", "月德"], "bad_stars": ["五黃", "三煞"]},
    "general": {"cn": "通用", "good_stars": ["天德", "月德", "天喜", "祿神"], "bad_stars": ["天刑", "白虎", "五鬼"]},
}


@dataclass
class DateRating:
    date: str
    weekday: str
    stem_branch: str
    score: int
    auspicious_stars: list = field(default_factory=list)
    inauspicious_stars: list = field(default_factory=list)
    suitable_for: list = field(default_factory=list)
    avoid: list = field(default_factory=list)


@dataclass
class ElectionalResult:
    start_date: str
    end_date: str
    criteria: str
    rated_dates: list = field(default_factory=list)
    best_date: str = ""


def _day_stem_branch(jd):
    ref_jd = 2451911.0  # 2001-01-07 is 甲子 day
    day_num = int(jd + 0.5) - int(ref_jd + 0.5)
    stem = day_num % 10
    branch = day_num % 12
    return stem % 10, branch % 12


def find_auspicious_dates(start_year, start_month, start_day,
                          end_year, end_month, end_day,
                          timezone=8.0, criteria="general"):
    """Find and rate auspicious dates in a range (max 60 days)."""
    activity = ACTIVITY_TYPES.get(criteria, ACTIVITY_TYPES["general"])

    start_jd = swe.julday(start_year, start_month, start_day, 12.0 - timezone)
    end_jd = swe.julday(end_year, end_month, end_day, 12.0 - timezone)

    max_days = min(int(end_jd - start_jd) + 1, 60)
    rated = []

    for d in range(max_days):
        jd = start_jd + d
        stem_idx, branch_idx = _day_stem_branch(jd)
        y, m, day, h = swe.revjul(jd + timezone / 24.0)
        date_str = f"{int(y):04d}-{int(m):02d}-{int(day):02d}"
        wd_idx = int(jd + 1.5) % 7
        weekday = f"週{WEEKDAY_CN[wd_idx]}"
        sb = HEAVENLY_STEMS[stem_idx] + EARTHLY_BRANCHES[branch_idx]

        # Simple scoring based on stem/branch patterns
        score = 50
        good = []
        bad = []

        # 天德: stems 丙(2), 甲(0) in specific months
        if stem_idx in (0, 2, 4):
            score += 10
            good.append("天德")
        # 月德: branch 寅(2), 午(6), 戌(10) combos
        if branch_idx in (2, 6, 10):
            score += 10
            good.append("月德")
        # 天喜
        if (stem_idx + branch_idx) % 6 == 0:
            score += 5
            good.append("天喜")

        # Bad patterns
        if branch_idx in (3, 9):  # 卯/酉 can be 破日
            score -= 15
            bad.append("破日")
        if stem_idx == 6 and branch_idx == 7:  # 庚未
            score -= 10
            bad.append("天刑")

        score = max(0, min(100, score))

        suitable = []
        avoid_list = []
        if score >= 60:
            suitable.append(activity["cn"])
        if any(b in bad for b in activity["bad_stars"]):
            avoid_list.append(activity["cn"])

        rated.append(DateRating(
            date=date_str, weekday=weekday, stem_branch=sb,
            score=score, auspicious_stars=good, inauspicious_stars=bad,
            suitable_for=suitable, avoid=avoid_list,
        ))

    rated.sort(key=lambda r: r.score, reverse=True)
    best = rated[0].date if rated else ""

    return ElectionalResult(
        start_date=f"{start_year:04d}-{start_month:02d}-{start_day:02d}",
        end_date=f"{end_year:04d}-{end_month:02d}-{end_day:02d}",
        criteria=criteria, rated_dates=rated, best_date=best,
    )


def render_electional_tool(timezone=8.0):
    """Render electional date selection in Streamlit."""
    import streamlit as st
    from datetime import date, timedelta

    st.subheader("📅 擇日工具 / Date Selection")

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start / 起始", value=date.today(), key="elect_start")
    with col2:
        end = st.date_input("End / 結束", value=date.today() + timedelta(days=30), key="elect_end")

    criteria = st.selectbox("Purpose / 用途",
                           options=list(ACTIVITY_TYPES.keys()),
                           format_func=lambda k: f"{ACTIVITY_TYPES[k]['cn']} ({k})",
                           key="elect_criteria")

    if st.button("🔍 Search / 搜索", key="elect_search"):
        result = find_auspicious_dates(
            start.year, start.month, start.day,
            end.year, end.month, end.day,
            timezone=timezone, criteria=criteria,
        )
        st.success(f"Best date / 最佳日期: **{result.best_date}**")
        for dr in result.rated_dates[:10]:
            color = "🟢" if dr.score >= 70 else "🟡" if dr.score >= 50 else "🔴"
            with st.expander(f"{color} {dr.date} ({dr.weekday}) {dr.stem_branch} — Score: {dr.score}"):
                if dr.auspicious_stars:
                    st.write(f"✅ {', '.join(dr.auspicious_stars)}")
                if dr.inauspicious_stars:
                    st.write(f"❌ {', '.join(dr.inauspicious_stars)}")
