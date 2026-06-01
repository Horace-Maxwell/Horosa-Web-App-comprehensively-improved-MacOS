"""
astro/medical_astrology — 醫學占星 / Iatromathematics

Classical Medical Astrology module combining:
- Zodiac Man (Homo Signorum) body-part correspondences
- Humoral theory (four humors / four temperaments)
- Egyptian Decan body-zone mapping
- Planetary hour electional rules for medical procedures
- Critical-day (crisis period) analysis for acute illness

Sources:
- Hippocrates, "Airs, Waters, Places"
- Galen, "On the Usefulness of the Parts"
- Ptolemy, "Tetrabiblos" Book III
- Avicenna, "Canon of Medicine" (Kitāb al-Qānūn fī al-Ṭibb)
- Picatrix (Ghāyat al-Ḥakīm)
- Medieval "Zodiac Man" manuscripts (Très Riches Heures du Duc de Berry)
- William Culpeper, "Astrological Judgement of Diseases"
"""

from .calculator import compute_medical_chart, MedicalChart
from .renderer import render_streamlit

__all__ = ["compute_medical_chart", "MedicalChart", "render_streamlit"]
