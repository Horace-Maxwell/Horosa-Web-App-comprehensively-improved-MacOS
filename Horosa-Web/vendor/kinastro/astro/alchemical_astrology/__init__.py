"""Public API for the Alchemical Astrology module.

煉金占星學（Alchemical Astrology / 煉金占星）模組公開介面
基於帕拉塞爾蘇斯（Paracelsus）Coelum Philosophorum 及 Astronomia Magna 傳統。
"""

from .correspondences import (
    ALCHEMICAL_STAGES,
    DIGNITY_SCORES,
    PLANET_CORRESPONDENCES,
    PLANET_KEYS,
    AlchemicalStageInfo,
    PlanetCorrespondence,
    longitude_to_sign_index,
)
from .engine import (
    AlchemicalEngine,
    AlchemicalReading,
    PlanetProfile,
    compute_reading,
)
from .interpretations import (
    PLANET_READING,
    STAGE_READING,
    get_planet_reading,
    get_stage_reading,
)
from .signatures import (
    PLANET_SIGNATURES,
    PlanetSignature,
    get_planet_signature,
    get_signature_text_zh,
)

__all__ = [
    # correspondences
    "PLANET_CORRESPONDENCES",
    "ALCHEMICAL_STAGES",
    "DIGNITY_SCORES",
    "PLANET_KEYS",
    "PlanetCorrespondence",
    "AlchemicalStageInfo",
    "longitude_to_sign_index",
    # engine
    "AlchemicalEngine",
    "AlchemicalReading",
    "PlanetProfile",
    "compute_reading",
    # interpretations
    "PLANET_READING",
    "STAGE_READING",
    "get_planet_reading",
    "get_stage_reading",
    # signatures
    "PLANET_SIGNATURES",
    "PlanetSignature",
    "get_planet_signature",
    "get_signature_text_zh",
]
