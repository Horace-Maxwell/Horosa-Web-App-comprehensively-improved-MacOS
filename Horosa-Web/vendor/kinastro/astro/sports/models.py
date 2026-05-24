"""
資料模型 (Data Models)

定義比賽輸入、星盤資料、預測結果等資料結構。
"""

from dataclasses import dataclass, field
from typing import Optional
from typing import Literal, Optional
from .asian_handicap import HandicapAnalysis


@dataclass
class MatchInput:
    """比賽輸入資料"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    timezone: float  # UTC offset, e.g. +8.0
    latitude: float
    longitude: float
    home_team: str
    away_team: str
    location_name: str = ""
    favorite: Optional[str] = None  # "home" or "away" or None
    notes: str = ""
    analysis_mode: Literal["horary", "event"] = "horary"

    # 歐賠 (1X2 decimal odds) — 如輸入則啟用亞盤分析
    home_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    away_odds: Optional[float] = None


@dataclass
class PlanetInfo:
    """行星基礎資訊"""
    name: str
    longitude: float
    latitude: float
    sign_index: int  # 0=Aries..11=Pisces
    sign_name: str
    sign_degree: float
    house: int  # 1-12
    retrograde: bool
    speed: float = 0.0
    essential_dignity: str = ""  # domicile/exaltation/detriment/fall/peregrine


@dataclass
class HouseInfo:
    """宮位基礎資訊"""
    number: int  # 1-12
    cusp: float
    sign_index: int
    sign_name: str
    lord: str  # ruling planet name
    planets_in_house: list = field(default_factory=list)


@dataclass
class WesternChartData:
    """西洋占星盤資料 (Tropical, Regiomontanus)"""
    ascendant: float
    midheaven: float
    planets: list  # List[PlanetInfo]
    houses: list  # List[HouseInfo]
    julian_day: float
    lot_of_fortune: float = 0.0
    north_node_lon: float = 0.0
    south_node_lon: float = 0.0


@dataclass
class VedicPlanetInfo:
    """Vedic 行星資訊"""
    name: str
    longitude: float
    rashi_index: int  # 0=Mesha..11=Meena
    rashi_name: str
    rashi_lord: str
    sign_degree: float
    nakshatra: str
    nakshatra_pada: int
    house: int
    retrograde: bool


@dataclass
class VedicChartData:
    """Vedic 星盤資料 (Sidereal, Lahiri)"""
    ascendant: float
    asc_rashi_index: int
    planets: list  # List[VedicPlanetInfo]
    houses: list  # List[HouseInfo]
    navamsa_ascendant: float
    navamsa_asc_rashi_index: int
    navamsa_planets: list  # List[VedicPlanetInfo] - Navamsa positions
    julian_day: float
    ayanamsa: float


@dataclass
class TeamAssignment:
    """球隊宮位分配"""
    team_name: str
    primary_house: int  # 1 or 7
    supporting_house: int  # 10 or 4
    lord_planet: str  # Lord of primary house
    lord_info: Optional[PlanetInfo] = None


@dataclass
class FrawleyEvidence:
    """Frawley 方法的單條證據"""
    description: str
    favors: str  # "home", "away", "draw", "neutral"
    weight: float  # 1.0=normal, 2.0=strong, 3.0=decisive
    category: str  # "combustion", "house_placement", "aspect", etc.


@dataclass
class VedicEvidence:
    """Vedic 方法的單條證據"""
    description: str
    favors: str  # "home", "away", "draw", "neutral"
    tier: int  # 1, 2, or 3 (higher=stronger per Gambler's Dharma)
    points: float
    category: str  # "victory_house", "cuspal_strength", "navamsa", etc.


@dataclass
class PredictionResult:
    """最終預測結果"""
    home_team: str
    away_team: str
    home_win_pct: float
    away_win_pct: float
    draw_pct: float
    predicted_winner: str  # "home", "away", "draw"
    confidence: str  # "high", "medium", "low"
    score_trend: str  # e.g. "1-0", "2-1", "low scoring"
    frawley_evidences: list  # List[FrawleyEvidence]
    vedic_evidences: list  # List[VedicEvidence]
    frawley_summary: str
    vedic_summary: str
    combined_summary: str
    bet_recommendation: str  # betting suggestion
    western_chart: Optional[WesternChartData] = None
    vedic_chart: Optional[VedicChartData] = None
    handicap_analysis: Optional[HandicapAnalysis] = None
    sports_prediction: Optional["SportsPrediction"] = None


@dataclass
class SportsPrediction:
    """結構化運動占星輸出。"""
    mode: Literal["horary", "event"]
    winner_prob: dict[str, float]
    confidence: float  # 0~1
    key_factors: list[str] = field(default_factory=list)
    score_estimate: str = ""
    injury_risk: dict[str, float] = field(default_factory=dict)
    reversal_indicator: float = 0.0
    disclaimers: list[str] = field(default_factory=list)


@dataclass
class TeamProfile:
    """球隊/選手基礎資料。"""
    name: str
    sport: str
    country: str = ""
    founded_year: Optional[int] = None
    home_stadium: str = ""
    tags: list[str] = field(default_factory=list)
