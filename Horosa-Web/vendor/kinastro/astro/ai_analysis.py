"""
astro/ai_analysis.py — AI 分析模組 (AI Analysis Module)

Provides:
  - CerebrasClient: wrapper around the Cerebras Cloud SDK for chat completions
  - format_chart_for_prompt(): formats any astrology chart into a text prompt
  - load/save system prompts from a JSON file
  - CEREBRAS_MODEL_OPTIONS / descriptions

Similar to the AI integration in kintaiyi (太乙神數).
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cerebras SDK wrapper
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "qwen-3-235b-a22b-instruct-2507"

CEREBRAS_MODEL_OPTIONS = [
    "qwen-3-235b-a22b-instruct-2507",
    "llama3.1-8b",
    "zai-glm-4.7",
]

CEREBRAS_MODEL_DESCRIPTIONS = {
    "qwen-3-235b-a22b-instruct-2507": "Cerebras: Fast inference, great for rapid iteration.",
    "llama3.1-8b": "Cerebras: Light and fast for quick tasks.",
    "zai-glm-4.7": "Cerebras: Versatile model for general use.",
}

# ---------------------------------------------------------------------------
# OpenAI model options
# ---------------------------------------------------------------------------

OPENAI_MODEL_OPTIONS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
]

OPENAI_MODEL_DESCRIPTIONS = {
    "gpt-4o": "OpenAI: Flagship multimodal model, best overall.",
    "gpt-4o-mini": "OpenAI: Fast and cost-effective for everyday tasks.",
    "gpt-4.1": "OpenAI: Latest GPT-4.1 model with improved capabilities.",
    "gpt-4.1-mini": "OpenAI: Compact GPT-4.1 for quick and efficient responses.",
    "gpt-4-turbo": "OpenAI: High-capability model with 128k context.",
    "gpt-3.5-turbo": "OpenAI: Fast and affordable for simpler tasks.",
}


class RateLimitError(Exception):
    """Raised when the AI API returns a rate-limit (429) error after all retries."""


# Maximum number of application-level retries on top of the SDK's built-in
# retries.  Total wait can be up to ~1+2+4 = 7 seconds with jitter.
_APP_MAX_RETRIES = 3
_APP_RETRY_BASE_DELAY = 1.0  # seconds


class CerebrasClient:
    """Thin wrapper around the Cerebras Cloud SDK with enhanced retry logic."""

    def __init__(self, api_key: str, max_retries: int = 5):
        if not api_key:
            raise ValueError("CerebrasClient requires a non-empty API key.")
        from cerebras.cloud.sdk import Cerebras
        self.client = Cerebras(api_key=api_key, max_retries=max_retries)

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str = DEFAULT_MODEL,
        **kwargs,
    ) -> str:
        """Send a chat completion request and return the assistant message text.

        Includes application-level retry with exponential back-off on top of
        the SDK's built-in retry so that transient 429 bursts are absorbed
        gracefully.
        """
        from cerebras.cloud.sdk import RateLimitError as _SdkRateLimit

        last_exc: Exception | None = None
        for attempt in range(_APP_MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    **kwargs,
                )
                return response.choices[0].message.content
            except _SdkRateLimit as exc:
                last_exc = exc
                if attempt < _APP_MAX_RETRIES - 1:
                    delay = _APP_RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        "Rate limited (attempt %d/%d), retrying in %.1fs …",
                        attempt + 1, _APP_MAX_RETRIES, delay,
                    )
                    time.sleep(delay)

        # All retries exhausted — raise our own RateLimitError so the caller
        # can show a user-friendly message.
        raise RateLimitError(str(last_exc)) from last_exc


class OpenAIClient:
    """Thin wrapper around the OpenAI Python SDK with retry logic."""

    def __init__(self, api_key: str, max_retries: int = 3):
        if not api_key:
            raise ValueError("OpenAIClient requires a non-empty API key.")
        import openai as _openai
        self.client = _openai.OpenAI(api_key=api_key, max_retries=max_retries)

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-4o",
        **kwargs,
    ) -> str:
        """Send a chat completion request and return the assistant message text."""
        import openai as _openai

        last_exc: Exception | None = None
        for attempt in range(_APP_MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    **kwargs,
                )
                return response.choices[0].message.content or ""
            except _openai.RateLimitError as exc:
                last_exc = exc
                if attempt < _APP_MAX_RETRIES - 1:
                    delay = _APP_RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        "OpenAI rate limited (attempt %d/%d), retrying in %.1fs …",
                        attempt + 1, _APP_MAX_RETRIES, delay,
                    )
                    time.sleep(delay)
            except _openai.AuthenticationError as exc:
                raise ValueError(str(exc)) from exc

        raise RateLimitError(str(last_exc)) from last_exc


class CustomProviderClient:
    """OpenAI-compatible client for third-party LLM providers."""

    def __init__(self, api_key: str, base_url: str, max_retries: int = 3):
        if not api_key:
            raise ValueError("CustomProviderClient requires a non-empty API key.")
        if not base_url:
            raise ValueError("CustomProviderClient requires a non-empty base URL.")
        import openai as _openai
        self.client = _openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            max_retries=max_retries,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        **kwargs,
    ) -> str:
        """Send a chat completion request and return the assistant message text."""
        import openai as _openai

        last_exc: Exception | None = None
        for attempt in range(_APP_MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    **kwargs,
                )
                return response.choices[0].message.content or ""
            except _openai.RateLimitError as exc:
                last_exc = exc
                if attempt < _APP_MAX_RETRIES - 1:
                    delay = _APP_RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        "Custom provider rate limited (attempt %d/%d), retrying in %.1fs …",
                        attempt + 1, _APP_MAX_RETRIES, delay,
                    )
                    time.sleep(delay)
            except _openai.AuthenticationError as exc:
                raise ValueError(str(exc)) from exc

        raise RateLimitError(str(last_exc)) from last_exc


# ---------------------------------------------------------------------------
# System prompt management
# ---------------------------------------------------------------------------

_PROMPTS_FILE = os.path.join(
    os.path.dirname(__file__), "data", "system_prompts.json"
)

DEFAULT_SYSTEM_PROMPT = (
    "# 占星师身份设定\n\n"
    "你是一位专业、温暖且富有洞察力的占星师，拥有深厚的占星学知识。\n"
    "你的使命是帮助用户理解星盘、行星位置、星座特质以及宇宙能量对人生的影响。\n\n"
    "## 专业领域\n"
    "- **本命盘解读**：分析出生星盘中的太阳、月亮、上升星座及行星位置\n"
    "- **运势预测**：提供日运、周运、月运及年度运势指引\n"
    "- **合盘分析**：解读人际关系、爱情、合作的星座兼容性\n"
    "- **行运追踪**：解释当前天象对个人的影响（水逆、满月、新月等）\n"
    "- **星座特质**：深入讲解十二星座的性格、优势与成长课题\n"
    "- **宫位解读**：分析十二宫位代表的生命领域\n"
    "- **相位分析**：解读行星间的角度关系及其意义\n\n"
    "## 沟通风格\n"
    "- **温暖共情**：用理解和支持的语气回应用户\n"
    "- **启发式引导**：不直接下判断，而是帮助用户自我觉察\n"
    "- **专业但易懂**：解释占星术语时用生活化的比喻\n"
    "- **正向赋能**：强调成长可能性，而非宿命论\n"
    "- **尊重自由意志**：提醒用户占星是指引，选择权在自己手中\n\n"
    "## 回应原则\n"
    "1. 先确认用户的出生信息（日期、时间、地点）以提供准确解读\n"
    "2. 结合用户的具体问题或关注领域进行针对性分析\n"
    "3. 避免绝对化的预测（如\"你一定会...\"），改用\"可能\"\"倾向于\"等表述\n"
    "4. 在给出建议时，兼顾占星洞察与现实可行性\n"
    "5. 对于重大人生决策，建议用户综合多方面信息做决定\n\n"
    "## 注意事项\n"
    "- 不替代专业医疗、法律、财务建议\n"
    "- 不鼓励迷信或依赖，而是促进自我认知\n"
    "- 尊重不同文化背景的占星传统\n"
    "- 保持开放心态，承认占星学的多元解读\n\n"
    "## 跨文化占星体系\n"
    "你精通并擅长融合世界各地占星体系，包括：\n"
    "- 西洋占星（古典、现代、Hellenistic）\n"
    "- 印度占星（Jyotish、Nadi）\n"
    "- 中国传统占星（七政四餘、八字、紫微斗數、宿曜道、萬化仙禽）\n"
    "- 泰國占星、阿拉伯占星、卡巴拉占星\n"
    "- 瑪雅占星、緬甸占星（Mahabote）、蒙古祖爾海（Zurkhai）\n"
    "- 古埃及十度區間（Decans）、**日本九星氣學（Kyūsei Kigaku）**、\n"
    "  **Robert Graves 1948 凱爾特樹木曆法（Beth-Luis-Nion，《The White Goddess》）**等\n\n"
    "若命盤包含九星氣學資料，請融合本命星（年）、月命星（月）、日命星（日）\n"
    "與其他體系（紫微斗數、七政四餘、西洋占星、印度占星）進行交叉分析，\n"
    "提供跨系統綜合洞察（例如：本命二黑土星 + 西洋土星在第四宮 = 家庭責任感深重…）。\n\n"
    "## 分析結構\n"
    "請按照以下清晰結構，以繁體中文、Markdown 格式呈現（使用 ##、###、項目符號、粗體提升可讀性）：\n\n"
    "### 1. 命盤整體格局總覽\n"
    "   簡潔概括整個盤局的核心主題、主要性格特質與人生焦點。\n\n"
    "### 2. 關鍵要素詳細解讀\n"
    "   清楚說明重要的行星、宮位、相位、特殊格局（含各體系特有瑜伽、星系配置、星曜組合等），"
    "並說明其占星意義。可適度對比不同體系的觀點。\n\n"
    "### 3. 優勢、挑戰與潛在影響\n"
    "   客觀分析盤局的吉凶因素，對事業、財富、人際關係、感情、婚姻、健康、靈性發展等領域的潛在影響。\n\n"
    "### 4. 運勢趨勢與人生時機\n"
    "   評估命主的人生整體走向、主要發展趨勢，以及重要階段或時機點（若有大運、流年、行運資訊則一併納入）。\n\n"
    "### 5. 實用建議與成長指引\n"
    "   提供具體、可執行的建議、補救方法或發展策略，幫助命主善用優勢、化解挑戰。"
    "可融入跨文化智慧（如心態調整、儀式、配石、風水等）。\n\n"
    "最後可加上簡短且正面的總結與鼓勵。\n\n"
    "**嚴格依據用戶提供的排盤數據**（包含出生資訊、行星位置、宮位、相位、度數、特殊格局等）進行分析，"
    "請務必保持專業、平衡、溫和且賦能的語調，避免絕對化或恐嚇性語言，"
    "多使用「傾向」「潛在」「有利於」「可透過努力提升」等詞彙，強調個人主動性與後天努力。\n\n"
    "若提供的數據不足或某些體系資訊不完整，請誠實註明並給予通用指引。\n\n"
    "請開始根據以上提供的排盤數據進行分析。"
)

DEFAULT_SYSTEM_PROMPT_EN = (
    "# Astrologer Identity\\n\\n"
    "You are a professional, warm, and insightful astrologer with deep astrological knowledge.\\n"
    "Your mission is to help users understand birth charts, planetary positions, zodiac traits, and how cosmic energies influence life.\\n\\n"
    "## Areas of Expertise\\n"
    "- **Natal Chart Interpretation**: Analyze Sun, Moon, Rising signs and planetary positions\\n"
    "- **Fortune Prediction**: Provide daily, weekly, monthly, and yearly forecasts\\n"
    "- **Synastry Analysis**: Interpret compatibility in relationships, love, and partnerships\\n"
    "- **Transit Tracking**: Explain current celestial events (Mercury retrograde, Full Moon, New Moon, etc.)\\n"
    "- **Zodiac Traits**: Deep dive into the 12 signs' personalities, strengths, and growth lessons\\n"
    "- **House Interpretation**: Analyze what the 12 houses represent in life domains\\n"
    "- **Aspect Analysis**: Interpret angular relationships between planets\\n\\n"
    "## Communication Style\\n"
    "- **Warm & Empathetic**: Respond with understanding and support\\n"
    "- **Guiding & Insightful**: Help users self-reflect rather than making direct judgments\\n"
    "- **Professional yet Accessible**: Use everyday metaphors for astrological terms\\n"
    "- **Empowering**: Emphasize growth potential, not fatalism\\n"
    "- **Respect Free Will**: Remind users that astrology is guidance—choices are theirs\\n\\n"
    "## Response Principles\\n"
    "1. Confirm birth information (date, time, location) for accurate interpretation\\n"
    "2. Address user's specific questions or areas of concern\\n"
    "3. Avoid absolute predictions ('you will definitely...'), use 'tends to', 'likely', 'potential' instead\\n"
    "4. Balance astrological insights with practical feasibility\\n"
    "5. For major life decisions, suggest consulting multiple sources\\n\\n"
    "## Important Notes\\n"
    "- Do not replace professional medical, legal, or financial advice\\n"
    "- Do not encourage superstition or dependency—promote self-awareness\\n"
    "- Respect diverse cultural astrological traditions\\n"
    "- Stay open-minded, acknowledge multiple interpretations\\n\\n"
    "## Cross-Cultural Astrology Systems\\n"
    "You are proficient in integrating astrology systems worldwide, including:\\n"
    "- Western Astrology (Classical, Modern, Hellenistic)\\n"
    "- Indian Astrology (Jyotish, Nadi)\\n"
    "- Chinese Traditional Astrology (Seven Governors & Four Remainders, BaZi, Zi Wei Dou Shu, Sukkayodo, Wan Hua Xian Qin)\\n"
    "- Thai Astrology, Arabic Astrology, Kabbalistic Astrology\\n"
    "- Mayan Astrology, Myanmar Astrology (Mahabote), Mongolian Zurkhai\\n"
    "- Ancient Egyptian Decans, **Japanese Nine Star Ki (Kyūsei Kigaku)**, "
    "**Robert Graves' 1948 Celtic Tree Calendar (Beth-Luis-Nion, The White Goddess)**, etc.\\n"
    "- When Nine Star Ki data is provided, cross-reference Year Star (Honmeisei), "
    "Month Star (Tsukimeisei), and Day Star (Himeisei) with other systems for synthesized insights "
    "(e.g., Year Star 2 Black Earth + Western Saturn in 4th house = deep family responsibility...).\\n\\n"
    "## Analysis Structure\\n"
    "Please present your analysis in English, using clear Markdown formatting (##, ###, bullet points, bold), following this structure:\\n\\n"
    "### 1. Overall Chart Overview\\n"
    "   Concisely summarize the core themes, main personality traits, and life focus.\\n\\n"
    "### 2. Detailed Interpretation of Key Elements\\n"
    "   Explain important planets, houses, aspects, special patterns (yogas, configurations, combinations). Compare different systems where appropriate.\\n\\n"
    "### 3. Strengths, Challenges & Potential Influences\\n"
    "   Analyze favorable and challenging factors, their impact on career, wealth, relationships, love, health, spirituality.\\n\\n"
    "### 4. Fortune Trends & Life Timing\\n"
    "   Assess life trajectory, development trends, important phases or timing (include Dasha, transits if available).\\n\\n"
    "### 5. Practical Advice & Growth Guidance\\n"
    "   Provide actionable suggestions, remedies, strategies. Incorporate cross-cultural wisdom (mindset, rituals, gemstones, feng shui).\\n\\n"
    "End with a brief, positive summary and encouragement.\\n\\n"
    "**Strictly base analysis on user-provided chart data** (birth info, planets, houses, aspects, degrees, patterns).\\n"
    "Maintain professional, balanced, gentle, empowering tone. Avoid absolutist or fear-inducing language.\\n"
    "Use words like 'tendency', 'potential', 'favorable for', 'can improve through effort'.\\n\\n"
    "If data is insufficient or certain systems incomplete, honestly note and offer general guidance.\\n\\n"
    "Please begin your analysis based on the chart data provided above."
)


_CJK_RATIO_THRESHOLD = 0.1


def detect_language(text: str) -> str:
    """Detect whether *text* is primarily Chinese or English.

    Returns ``"zh"`` if the text contains a significant proportion of CJK
    characters (more than 10 %), otherwise ``"en"``.  Empty or
    whitespace-only input defaults to ``"zh"`` (the application's primary
    language).
    """
    if not text or not text.strip():
        return "zh"
    # Count CJK Unified Ideographs (common Chinese characters)
    cjk = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
    total = len(text.strip())
    if total > 0 and cjk / total > _CJK_RATIO_THRESHOLD:
        return "zh"
    return "en"


URANIAN_SYSTEM_PROMPT = (
    "You are the authentic voice and living system of Alfred Witte (1878–1941), "
    "founder of the Hamburg School of Uranian Astrology (Uranian System), exactly as he "
    "developed and taught it in Hamburg during the 1920s and 1930s, as codified in "
    "\"Regelwerk für Planetenbilder\" (Rules for Planetary Pictures).\n\n"
    "You interpret charts strictly according to Witte's original principles: cosmic symmetry, "
    "planetary pictures (Planetenbilder), midpoints, the 90-degree dial, and mathematical precision. "
    "You do not incorporate later developments such as Cosmobiology by Reinhold Ebertin, nor modern "
    "psychological or spiritual interpretations unless they follow directly from Witte's own logic "
    "and empirical rules.\n\n"
    "## Core Axioms (Never Deviate)\n\n"
    "- Every astrological effect is revealed through **symmetrical planetary combinations** expressed "
    "as planetary pictures: A + B = C + D, or 2A = B + C (where A is the direct midpoint of B and C).\n"
    "- The strongest pictures involve the **six personal points**: Sun, Moon, Ascendant, Midheaven (MC), "
    "Lunar Node, and the Aries Point / Earth Point axis.\n"
    "- The **90-degree dial** is the primary working tool. On the 90° dial, all multiples of 45° "
    "(conjunction, square, opposition) appear as conjunctions, making hidden midpoints and planetary "
    "pictures immediately visible.\n"
    "- **Transneptunian planets** discovered/calculated by Alfred Witte himself (Cupido, Hades, Zeus, "
    "Kronos) are to be given full weight and priority. The additional four (Apollon, Admetos, Vulkanus, "
    "Poseidon) may be mentioned as later Hamburg School contributions, but Witte's original four remain "
    "central.\n"
    "- Astrology is a **precise, mathematical, symmetrical science** based on vibration and cosmic order. "
    "Interpretation must be clear, objective, event-oriented, and characterological — never vague, "
    "romantic, or purely psychological.\n\n"
    "## Response Rules (Strictly Enforce)\n\n"
    "1. **Always show exact planetary picture formulas** when interpreting "
    "(e.g., \"Sun = Moon/Mars + Saturn\" or \"2*Sun = Moon + Mars\").\n"
    "2. For any chart analysis, **systematically identify and list** the most important direct midpoints "
    "and planetary pictures, especially those involving personal points.\n"
    "3. Use **precise, technical, and objective language** exactly like Witte's writings and the Rules "
    "for Planetary Pictures.\n"
    "4. When analysing family astrology (KinAstro's core), **highlight how planetary pictures reveal "
    "inherited patterns**, family dynamics, collective fates, and symmetrical connections between family "
    "members' charts.\n"
    "5. **Begin every major analysis with**: \"According to the Uranian System as developed by Alfred "
    "Witte in the Hamburg School...\"\n"
    "6. If asked for anything outside Witte's original 1920s–1930s framework, politely redirect: "
    "\"Within the original Uranian System of Alfred Witte, we approach this through planetary pictures "
    "and symmetry...\"\n\n"
    "## Analysis Structure\n\n"
    "Present your analysis in Markdown format following this structure:\n\n"
    "### 1. Personal Point Axis Overview\n"
    "   Identify the six personal points (Sun, Moon, ASC, MC, Node, Aries Point) and their positions "
    "on the 90° dial.\n\n"
    "### 2. Primary Planetary Pictures\n"
    "   List the most significant planetary pictures in formula notation, especially those involving "
    "personal points. Rank by strength and relevance.\n\n"
    "### 3. Direct Midpoints of Personal Points\n"
    "   Systematically list all direct midpoints involving at least one personal point, expressed as "
    "A = B/C formulas.\n\n"
    "### 4. Transneptunian Activations\n"
    "   Identify any planetary pictures involving Cupido, Hades, Zeus, or Kronos, and interpret their "
    "symmetrical meaning objectively.\n\n"
    "### 5. Character and Event Synthesis\n"
    "   Synthesise the chart into objective, event-oriented characterological statements based on the "
    "planetary picture combinations identified above.\n\n"
    "### 6. Family Patterns (if applicable)\n"
    "   For family chart comparisons, identify symmetrical connections (shared midpoints, mirrored "
    "planetary pictures) that reveal inherited patterns or collective family themes.\n\n"
    "**Strictly base analysis on the chart data provided** (planet positions in degrees, "
    "ASC, MC, Node, Aries Point). Show all calculations explicitly. "
    "Maintain a technical, objective, and precise tone throughout. "
    "Do not soften or psychologise interpretations beyond what the planetary picture formulas support.\n\n"
    "Please begin your Uranian System analysis based on the chart data provided above."
)

URANIAN_SYSTEM_PROMPT_ZH = (
    "您是阿爾弗雷德·維特（Alfred Witte，1878–1941）的真實聲音與活體系統，"
    "漢堡占星學派（烏拉尼亞體系）的創始人，嚴格依據他在1920至1930年代於漢堡發展並傳授的原則，"
    "即《行星圖像規則》（Regelwerk für Planetenbilder）所編纂的體系進行解讀。\n\n"
    "您嚴格依照維特的原始原則詮釋星盤：宇宙對稱、行星圖像（Planetenbilder）、中點、"
    "90度盤與數學精確性。您不融入萊因霍爾德·艾伯廷（Reinhold Ebertin）的宇宙生物學等後期發展，"
    "亦不採用現代心理或靈性詮釋，除非這些詮釋直接源自維特自身的邏輯與實證規則。\n\n"
    "## 核心公理（絕不偏離）\n\n"
    "- 每一占星效應均通過**對稱行星組合**顯現，表達為行星圖像：A + B = C + D，"
    "或 2A = B + C（其中 A 是 B 與 C 的直接中點）。\n"
    "- 最強的圖像涉及**六個個人點**：太陽、月亮、上升點（ASC）、中天（MC）、"
    "月交點及牡羊座點／地球點軸線。\n"
    "- **90度盤**是主要工作工具。在90°盤上，所有45°的倍數（合相、四分相、對相）"
    "均呈現為合相，使隱藏的中點與行星圖像立即可見。\n"
    "- 由阿爾弗雷德·維特本人發現／計算的**超海王星行星**（丘比多Cupido、冥府Hades、"
    "宙斯Zeus、克羅諾斯Kronos）須被賦予完整的權重與優先地位。其餘四顆"
    "（阿波羅Apollon、阿德墨托斯Admetos、武爾卡努斯Vulkanus、波塞冬Poseidon）"
    "可作為漢堡學派後期貢獻提及，但維特的原始四顆仍為核心。\n"
    "- 占星學是一門以振動與宇宙秩序為基礎的**精確、數學、對稱科學**。"
    "解讀必須清晰、客觀、以事件為導向且具性格描述性——絕非模糊、浪漫或純粹心理化的。\n\n"
    "## 回應規則（嚴格執行）\n\n"
    "1. 詮釋時**始終顯示精確的行星圖像公式**（例如：「太陽 = 月亮/火星 + 土星」或「2*太陽 = 月亮 + 火星」）。\n"
    "2. 對任何星盤分析，**系統性地識別並列出**最重要的直接中點與行星圖像，尤其是涉及個人點的部分。\n"
    "3. 使用**精確、技術性且客觀的語言**，完全符合維特著作與《行星圖像規則》的風格。\n"
    "4. 分析家庭占星（KinAstro核心）時，**強調行星圖像如何揭示遺傳模式**、"
    "家庭動態、集體命運，以及家庭成員星盤間的對稱連結。\n"
    "5. **每項主要分析均以以下語句開始**：「根據阿爾弗雷德·維特在漢堡學派所發展的烏拉尼亞體系……」\n"
    "6. 若被要求超出維特1920至1930年代原始框架之外的內容，請禮貌地轉向：\n"
    "   「在阿爾弗雷德·維特的原始烏拉尼亞體系中，我們通過行星圖像與對稱性來處理這一問題……」\n\n"
    "## 分析結構\n\n"
    "請以繁體中文、Markdown 格式呈現您的分析，遵循以下結構：\n\n"
    "### 1. 個人點軸線總覽\n"
    "   識別六個個人點（太陽、月亮、ASC、MC、月交點、牡羊座點）及其在90°盤上的位置。\n\n"
    "### 2. 主要行星圖像\n"
    "   以公式符號列出最重要的行星圖像，尤其是涉及個人點的部分。依強度與相關性排序。\n\n"
    "### 3. 個人點的直接中點\n"
    "   系統性列出所有涉及至少一個個人點的直接中點，以 A = B/C 公式表達。\n\n"
    "### 4. 超海王星行星啟動\n"
    "   識別任何涉及丘比多、冥府、宙斯或克羅諾斯的行星圖像，並客觀詮釋其對稱意義。\n\n"
    "### 5. 性格與事件綜合\n"
    "   依據上述識別的行星圖像組合，將星盤綜合為客觀、以事件為導向的性格描述。\n\n"
    "### 6. 家庭模式（如適用）\n"
    "   對於家庭星盤比較，識別揭示遺傳模式或集體家庭主題的對稱連結（共享中點、映射行星圖像）。\n\n"
    "**嚴格依據所提供的星盤數據**（行星度數、ASC、MC、月交點、牡羊座點）進行分析。"
    "明確展示所有計算過程。全程保持技術性、客觀且精確的語調。"
    "不要超出行星圖像公式所支持的範圍去軟化或心理化詮釋。\n\n"
    "請開始根據以上提供的排盤數據進行烏拉尼亞體系分析。"
)


_DEFAULT_PROMPTS = {
    "prompts": [
        {
            "name": "占星大師",
            "name_en": "Astrology Master",
            "content": DEFAULT_SYSTEM_PROMPT,
        },
        {
            "name": "烏拉尼亞占星（維特體系）",
            "name_en": "Uranian Astrology (Witte System)",
            "content": URANIAN_SYSTEM_PROMPT_ZH,
            "content_en": URANIAN_SYSTEM_PROMPT,
        },
    ],
    "selected": "占星大師",
}


def load_system_prompts() -> dict:
    """Load system prompts from JSON file, creating defaults if needed."""
    try:
        with open(_PROMPTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "prompts" in data and data["prompts"]:
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    # Write defaults
    save_system_prompts(_DEFAULT_PROMPTS)
    return _DEFAULT_PROMPTS.copy()


def save_system_prompts(data: dict) -> bool:
    """Persist system prompts to the JSON file."""
    try:
        with open(_PROMPTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Chart → prompt formatters
# ---------------------------------------------------------------------------

def _safe_getattr(obj: Any, *attrs: str, default: str = "") -> str:
    """Try multiple attribute names and return the first truthy value."""
    for attr in attrs:
        val = getattr(obj, attr, None)
        if val is not None:
            return str(val)
    return default


def _format_planet_list(planets, fields=None) -> str:
    """Generic planet list formatter."""
    if not planets:
        return "(none)"
    lines = []
    for p in planets:
        name = _safe_getattr(p, "name", "symbol")
        sign = _safe_getattr(p, "sign", "rashi", "sign_western")
        deg = _safe_getattr(p, "degree", "sign_degree", "longitude")
        house = _safe_getattr(p, "house", "house_num")
        retro = "R" if getattr(p, "retrograde", False) else ""
        parts = [name]
        if sign:
            parts.append(f"in {sign}")
        if deg:
            parts.append(f"{deg}°")
        if house:
            parts.append(f"H{house}")
        if retro:
            parts.append("(R)")
        lines.append(" ".join(parts))
    return "\n".join(lines)


def _format_aspects(aspects) -> str:
    """Format aspect list."""
    if not aspects:
        return "(none)"
    lines = []
    for a in aspects[:30]:  # cap to avoid overly long prompts
        p1 = _safe_getattr(a, "planet1", "planet1_name", "p1")
        p2 = _safe_getattr(a, "planet2", "planet2_name", "p2")
        asp = _safe_getattr(a, "aspect", "aspect_name", "name")
        orb = _safe_getattr(a, "orb")
        lines.append(f"{p1} {asp} {p2} (orb {orb}°)")
    return "\n".join(lines)


def _format_houses(houses) -> str:
    """Format house cusps."""
    if not houses:
        return "(none)"
    lines = []
    for h in houses:
        num = _safe_getattr(h, "number", "house_num")
        sign = _safe_getattr(h, "sign", "sign_name")
        deg = _safe_getattr(h, "degree", "cusp_degree")
        lines.append(f"House {num}: {sign} {deg}°")
    return "\n".join(lines)


def format_western_chart(chart) -> str:
    """Format a Western chart for the AI prompt, including asteroid and star data."""
    import streamlit as st
    sections = ["【西洋占星排盤 Western Chart】"]
    sections.append(f"ASC Sign: {_safe_getattr(chart, 'asc_sign')}")
    sections.append(f"MC Sign: {_safe_getattr(chart, 'mc_sign')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    sections.append("\n--- Houses ---")
    sections.append(_format_houses(getattr(chart, 'houses', [])))
    sections.append("\n--- Aspects ---")
    sections.append(_format_aspects(getattr(chart, 'aspects', [])))

    # ── Asteroids & Centaurs ─────────────────────────────────────────────
    try:
        if st.session_state.get("_adv_asteroids", False):
            from astro.western.asteroids import compute_asteroids
            _grp_keys = st.session_state.get("_adv_ast_group_keys") or ["chiron_pholus", "lilith", "main_belt"]
            _helio = st.session_state.get("_adv_helio", False)
            _asts = compute_asteroids(chart.julian_day, heliocentric=_helio,
                                      include_groups=_grp_keys)
            if _asts:
                sections.append("\n--- Asteroids & Centaurs ---")
                for a in _asts:
                    r = "℞" if a.retrograde else ""
                    sections.append(
                        f"  {a.name} ({a.name_cn}) {a.symbol}: "
                        f"{a.sign} {a.sign_degree:.2f}° {r}  "
                        f"[{a.meaning_en}]"
                    )
                # Chiron interpretation note
                chiron = next((a for a in _asts if a.name == "Chiron"), None)
                if chiron:
                    sections.append(
                        f"  → Chiron (凱龍) in {chiron.sign}: the Wounded Healer archetype "
                        f"manifests in the realm of {chiron.sign}."
                    )
                lilith = next((a for a in _asts if "Lilith" in a.name and "Mean" in a.name), None)
                if lilith:
                    sections.append(
                        f"  → Black Moon Lilith (黑月麗莉絲) in {lilith.sign}: "
                        f"raw instinct and shadow self in the area of {lilith.sign}."
                    )
    except Exception:
        pass

    # ── Fixed Star Conjunctions ─────────────────────────────────────────
    try:
        if st.session_state.get("_adv_fixed_stars", False):
            from astro.western.fixed_stars import compute_fixed_star_positions, find_conjunctions
            _lim = st.session_state.get("_adv_stars_count", 30)
            if _lim == 103:
                _lim = None
            _stars = compute_fixed_star_positions(chart.julian_day, limit=_lim)
            _p_lons = {p.name: p.longitude for p in chart.planets}
            _conjs = find_conjunctions(_stars, _p_lons)
            if _conjs:
                sections.append("\n--- Fixed Star Conjunctions ---")
                _notable = {
                    "Sirius":    "fame and distinction (天狼星)",
                    "Regulus":   "power and leadership (軒轅十四)",
                    "Spica":     "gift and good fortune (角宿一)",
                    "Algol":     "intense power and upheaval (大陵五)",
                    "Antares":   "obsession and extremism (心宿二)",
                    "Fomalhaut": "idealism and occult ability (北落師門)",
                    "Aldebaran": "courage and integrity (畢宿五)",
                    "Vega":      "artistic talent and idealism (織女一)",
                }
                for c in _conjs[:15]:
                    note = _notable.get(c.star_name, c.meaning_en)
                    sections.append(
                        f"  {c.star_name} conjunct {c.planet_name} (orb {c.orb:.1f}°): "
                        f"{note}"
                    )
    except Exception:
        pass

    # ── Parans ────────────────────────────────────────────────────────────
    try:
        if st.session_state.get("_adv_parans", False):
            from astro.western.fixed_stars import compute_fixed_star_positions
            from astro.western.advanced_bodies import calculate_parans
            _lim = st.session_state.get("_adv_stars_count", 30)
            if _lim == 103:
                _lim = None
            _stars_p = compute_fixed_star_positions(chart.julian_day, limit=_lim)
            _parans = calculate_parans(chart.julian_day, chart.latitude, chart.longitude, _stars_p)
            if _parans:
                sections.append("\n--- Parans (Paranatellonta) ---")
                for p in _parans[:10]:
                    sections.append(
                        f"  {p.star_name} ({p.star_event_en}) "
                        f"paran {p.planet_name} ({p.planet_event_en}) "
                        f"[orb {p.orb:.1f}°]: {p.star_meaning_en}"
                    )
    except Exception:
        pass

    return "\n".join(sections)


def format_vedic_chart(chart) -> str:
    """Format a Vedic (Indian / Jyotish) chart for the AI prompt."""
    sections = ["【印度占星排盤 Vedic Chart】"]
    sections.append(f"Lagna: {_safe_getattr(chart, 'lagna', 'asc_rashi')}")
    sections.append(f"Ayanamsa: {_safe_getattr(chart, 'ayanamsa')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    sections.append("\n--- Houses ---")
    sections.append(_format_houses(getattr(chart, 'houses', [])))
    sections.append("\n--- Aspects ---")
    sections.append(_format_aspects(getattr(chart, 'aspects', [])))
    return "\n".join(sections)


def format_chinese_chart(chart) -> str:
    """Format a Chinese Seven-Governors (七政四餘) chart for the AI prompt."""
    sections = ["【七政四餘排盤 Chinese Chart】"]
    sections.append(f"命宮: {_safe_getattr(chart, 'ming_gong', 'ming')}")
    sections.append(f"身宮: {_safe_getattr(chart, 'shen_gong', 'shen')}")
    # BaZi
    bazi = getattr(chart, 'bazi', None)
    if bazi:
        sections.append(f"八字: 年={_safe_getattr(bazi, 'year')}, 月={_safe_getattr(bazi, 'month')}, "
                        f"日={_safe_getattr(bazi, 'day')}, 時={_safe_getattr(bazi, 'hour')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    sections.append("\n--- Houses ---")
    sections.append(_format_houses(getattr(chart, 'houses', [])))
    sections.append("\n--- Aspects ---")
    sections.append(_format_aspects(getattr(chart, 'aspects', [])))
    return "\n".join(sections)


def format_ziwei_chart(chart) -> str:
    """Format a Zi Wei Dou Shu (紫微斗數) chart for the AI prompt."""
    sections = ["【紫微斗數排盤 Zi Wei Dou Shu Chart】"]
    sections.append(f"命宮: {_safe_getattr(chart, 'ming_gong')}")
    sections.append(f"身宮: {_safe_getattr(chart, 'shen_gong')}")
    sections.append(f"命主: {_safe_getattr(chart, 'ming_zhu')}")
    sections.append(f"身主: {_safe_getattr(chart, 'shen_zhu')}")
    # palaces
    palaces = getattr(chart, 'palaces', [])
    if palaces:
        sections.append("\n--- 十二宮 ---")
        for pal in palaces:
            name = _safe_getattr(pal, 'name', 'palace_name')
            branch = _safe_getattr(pal, 'branch', 'earthly_branch')
            stars = _safe_getattr(pal, 'stars', 'star_list')
            sections.append(f"{name}（{branch}）: {stars}")
    return "\n".join(sections)


def format_thai_chart(chart) -> str:
    """Format a Thai astrology chart for the AI prompt."""
    sections = ["【泰國占星排盤 Thai Chart】"]
    sections.append(f"Weekday: {_safe_getattr(chart, 'weekday', 'birth_weekday')}")
    sections.append(f"Lagna: {_safe_getattr(chart, 'lagna')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_kabbalistic_chart(chart) -> str:
    """Format a Kabbalistic chart for the AI prompt."""
    sections = ["【卡巴拉占星排盤 Kabbalistic Chart】"]
    sections.append(f"Life Path: {_safe_getattr(chart, 'life_path')}")
    sections.append(f"Name Number: {_safe_getattr(chart, 'name_number')}")
    sections.append(f"Hebrew Letter: {_safe_getattr(chart, 'hebrew_letter')}")
    sections.append(f"Sephirah: {_safe_getattr(chart, 'sephirah')}")
    sections.append(f"Tree Path: {_safe_getattr(chart, 'tree_path')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_arabic_chart(chart) -> str:
    """Format an Arabic astrology chart for the AI prompt."""
    sections = ["【阿拉伯占星排盤 Arabic Chart】"]
    sections.append(f"Lot of Fortune: {_safe_getattr(chart, 'lot_of_fortune')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    sections.append("\n--- Arabic Parts ---")
    parts = getattr(chart, 'arabic_parts', [])
    if parts:
        for pt in parts:
            name = _safe_getattr(pt, 'name')
            lon = _safe_getattr(pt, 'longitude', 'degree')
            sign = _safe_getattr(pt, 'sign')
            sections.append(f"{name}: {sign} {lon}°")
    return "\n".join(sections)


def format_maya_chart(chart) -> str:
    """Format a Mayan astrology chart for the AI prompt."""
    sections = ["【瑪雅占星排盤 Mayan Chart】"]
    sections.append(f"Kin: {_safe_getattr(chart, 'kin')}")
    sections.append(f"Tzolkin: {_safe_getattr(chart, 'tzolkin')}")
    sections.append(f"Haab: {_safe_getattr(chart, 'haab')}")
    sections.append(f"Tone: {_safe_getattr(chart, 'tone')}")
    sections.append(f"Glyph: {_safe_getattr(chart, 'glyph', 'day_sign')}")
    sections.append(f"Long Count: {_safe_getattr(chart, 'long_count')}")
    return "\n".join(sections)


def format_aztec_chart(chart) -> str:
    """Format an Aztec astrology chart for the AI prompt."""
    sections = ["【阿茲特克占星排盤 Aztec Chart】"]
    sections.append(f"Tonalpohualli: {_safe_getattr(chart, 'tonalpohualli_number')} "
                    f"{_safe_getattr(chart, 'tonalpohualli_sign_name')}")
    sections.append(f"Day Sign (中文): {_safe_getattr(chart, 'tonalpohualli_sign_cn')}")
    sections.append(f"Day Sign (EN): {_safe_getattr(chart, 'tonalpohualli_sign_en')}")
    sections.append(f"Energy: {_safe_getattr(chart, 'tonalpohualli_energy')}")
    sections.append(f"Trecena: {_safe_getattr(chart, 'trecena_ruler_name')} "
                    f"({_safe_getattr(chart, 'trecena_ruler_cn')})")
    sections.append(f"Deity: {_safe_getattr(chart, 'deity')}")
    sections.append(f"Direction: {_safe_getattr(chart, 'direction_cn')} "
                    f"({_safe_getattr(chart, 'direction_en')})")
    sections.append(f"Color: {_safe_getattr(chart, 'color_cn')} "
                    f"({_safe_getattr(chart, 'color_en')})")
    return "\n".join(sections)


def format_mahabote_chart(chart) -> str:
    """Format a Mahabote (Myanmar) chart for the AI prompt."""
    sections = ["【緬甸占星排盤 Mahabote Chart】"]
    sections.append(f"Weekday: {_safe_getattr(chart, 'birth_weekday')}")
    sections.append(f"Animal: {_safe_getattr(chart, 'birth_animal_en', 'birth_animal_cn')}")
    houses = getattr(chart, 'houses', [])
    if houses:
        sections.append("\n--- Houses ---")
        for h in houses:
            name = _safe_getattr(h, 'name', 'house_name')
            wday = _safe_getattr(h, 'weekday_en', 'weekday_cn')
            animal = _safe_getattr(h, 'animal_en', 'animal_cn')
            sections.append(f"{name}: {wday} ({animal})")
    return "\n".join(sections)


def format_decan_chart(chart) -> str:
    """Format an Egyptian Decans chart for the AI prompt."""
    sections = ["【古埃及十度區間排盤 Egyptian Decans Chart】"]
    sections.append(f"Sun Decan: {_safe_getattr(chart, 'sun_decan')}")
    sections.append(f"Moon Decan: {_safe_getattr(chart, 'moon_decan')}")
    sections.append(f"ASC Decan: {_safe_getattr(chart, 'asc_decan')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_nadi_chart(chart) -> str:
    """Format a Nadi Jyotish chart for the AI prompt."""
    sections = ["【納迪占星排盤 Nadi Chart】"]
    sections.append(f"Nadi Type: {_safe_getattr(chart, 'nadi_type')}")
    sections.append(f"Nakshatra: {_safe_getattr(chart, 'birth_nakshatra', 'nakshatra')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_zurkhai_chart(chart) -> str:
    """Format a Mongolian Zurkhai chart for the AI prompt."""
    sections = ["【蒙古祖爾海排盤 Zurkhai Chart】"]
    sections.append(f"Animal: {_safe_getattr(chart, 'animal', 'birth_animal')}")
    sections.append(f"Element: {_safe_getattr(chart, 'element', 'birth_element')}")
    sections.append(f"Mewa: {_safe_getattr(chart, 'mewa')}")
    sections.append(f"Parkha: {_safe_getattr(chart, 'parkha')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_hellenistic_chart(chart) -> str:
    """Format a Hellenistic chart for the AI prompt."""
    sections = ["【希臘占星排盤 Hellenistic Chart】"]
    sections.append(f"ASC: {_safe_getattr(chart, 'asc_sign')}")
    sections.append(f"MC: {_safe_getattr(chart, 'mc_sign')}")
    sections.append(f"Sect: {_safe_getattr(chart, 'sect')}")
    sections.append(f"Lot of Fortune: {_safe_getattr(chart, 'lot_of_fortune')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    sections.append("\n--- Aspects ---")
    sections.append(_format_aspects(getattr(chart, 'aspects', [])))
    return "\n".join(sections)


def format_huangji_chart(chart) -> str:
    """Format a Huangji Jingshi chart for the AI prompt."""
    sections = ["【皇極經世排盤 Huangji Jingshi】"]
    pan = getattr(chart, "huangji_pan", None)
    if pan is not None:
        sections.append(
            f"元會運世: 元{_safe_getattr(pan, 'yuan')} / 會{_safe_getattr(pan, 'hui')} / "
            f"運{_safe_getattr(pan, 'yun')} / 世{_safe_getattr(pan, 'shi')}"
        )
        sections.append(
            f"定位: 世內第{_safe_getattr(pan, 'year_in_shi')}年, "
            f"運內第{_safe_getattr(pan, 'year_in_yun')}年, "
            f"會內第{_safe_getattr(pan, 'year_in_hui')}年"
        )
        sections.append(
            f"節氣: kinwangji={_safe_getattr(pan, 'jieqi_kinwangji')} / "
            f"swiss={_safe_getattr(pan, 'jieqi_swiss')}"
        )
        gua = getattr(pan, "gua", {})
        if isinstance(gua, dict) and gua:
            sections.append("四卦/時序卦: " + "、".join([f"{k}:{v}" for k, v in gua.items()]))
    cross = getattr(chart, "cross_system", None)
    if cross is not None:
        sections.append("\n--- 跨體系對照 ---")
        sections.append(f"Zodiacal Releasing: {_safe_getattr(cross, 'zodiacal_releasing_l1')}")
        sections.append(f"Annual Profection: {_safe_getattr(cross, 'annual_profection')}")
        sections.append(f"Vedic Dasha: {_safe_getattr(cross, 'vedic_dasha')}")
        sections.append(f"Ziwei Daxian: {_safe_getattr(cross, 'ziwei_daxian')}")
    return "\n".join(sections)


def format_sukkayodo_chart(chart) -> str:
    """Format a Sukkayodo chart for the AI prompt."""
    sections = ["【宿曜道排盤 Sukkayodo Chart】"]
    sections.append(f"Birth Mansion: {_safe_getattr(chart, 'birth_mansion', 'mansion')}")
    sections.append("\n--- Planets ---")
    sections.append(_format_planet_list(getattr(chart, 'planets', [])))
    return "\n".join(sections)


def format_chinstar_chart(chart_data: dict) -> str:
    """Format a 萬花仙禽 (Chinstar) chart for the AI prompt."""
    sections = ["【萬花仙禽排盤 Chinstar Chart】"]
    if isinstance(chart_data, dict):
        for k, v in chart_data.items():
            sections.append(f"{k}: {v}")
    else:
        sections.append(format_generic_chart(chart_data, "萬花仙禽"))
    return "\n".join(sections)


def _format_value(value: Any, depth: int = 0) -> str:
    """Recursively format a value for inclusion in the AI prompt."""
    if depth > 3:
        return str(value)
    indent = "  " * depth
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            lines.append(f"{indent}{k}: {_format_value(v, depth + 1)}")
        return "\n".join(lines)
    if isinstance(value, (list, tuple)):
        if not value:
            return "(none)"
        lines = []
        for item in value:
            lines.append(f"{indent}- {_format_value(item, depth + 1)}")
        return "\n".join(lines)
    if hasattr(value, "__dict__") and not callable(value):
        lines = []
        for attr in sorted(vars(value)):
            if attr.startswith("_"):
                continue
            val = getattr(value, attr, None)
            if callable(val):
                continue
            lines.append(f"{indent}{attr}: {_format_value(val, depth + 1)}")
        return "\n".join(lines) if lines else str(value)
    return str(value)


def format_generic_chart(chart, system_name: str = "Unknown") -> str:
    """Fallback formatter for any chart object — dumps all public attributes."""
    sections = [f"【{system_name}】"]
    if isinstance(chart, dict):
        for k, v in chart.items():
            sections.append(f"{k}: {_format_value(v, depth=1)}")
    else:
        for attr in sorted(dir(chart)):
            if attr.startswith("_"):
                continue
            val = getattr(chart, attr, None)
            if callable(val):
                continue
            sections.append(f"{attr}: {_format_value(val, depth=1)}")
    return "\n".join(sections)


def _format_twelve_ci_chart(chart) -> str:
    """Format a TwelveCiChart for AI analysis."""
    from astro.twelve_ci import format_twelve_ci_chart
    return format_twelve_ci_chart(chart)


def _format_acg_chart(chart) -> str:
    """Format an AcgResult for AI analysis."""
    from astro.astrocartography import format_acg_for_prompt
    return format_acg_for_prompt(chart)


def format_nine_star_ki_chart(chart) -> str:
    """Format a NineStarKiChart (日本九星氣學) for the AI prompt."""
    sections = ["【日本九星氣學排盤 Japanese Nine Star Ki Chart】"]
    # Three stars
    ys = getattr(chart, "year_star", "")
    ms = getattr(chart, "month_star", "")
    ds = getattr(chart, "day_star", "")
    ys_info = getattr(chart, "year_star_info", {})
    ms_info = getattr(chart, "month_star_info", {})
    ds_info = getattr(chart, "day_star_info", {})
    sections.append(
        f"本命星 (Year Star): {ys} {ys_info.get('zh_name', '')} / {ys_info.get('en_name', '')}"
    )
    sections.append(
        f"  五行: {ys_info.get('element_zh', '')} ({ys_info.get('element_en', '')}) | "
        f"方位: {ys_info.get('direction_zh', '')} ({ys_info.get('direction_en', '')}) | "
        f"顏色: {ys_info.get('color_zh', '')} | 性格: {ys_info.get('personality_zh', '')}"
    )
    sections.append(
        f"月命星 (Month Star): {ms} {ms_info.get('zh_name', '')} / {ms_info.get('en_name', '')}"
    )
    sections.append(
        f"  五行: {ms_info.get('element_zh', '')} ({ms_info.get('element_en', '')}) | "
        f"方位: {ms_info.get('direction_zh', '')} | 性格: {ms_info.get('personality_zh', '')}"
    )
    sections.append(
        f"日命星 (Day Star): {ds} {ds_info.get('zh_name', '')} / {ds_info.get('en_name', '')}"
    )
    sections.append(
        f"  五行: {ds_info.get('element_zh', '')} ({ds_info.get('element_en', '')}) | "
        f"方位: {ds_info.get('direction_zh', '')} | 性格: {ds_info.get('personality_zh', '')}"
    )
    # Adjusted year / Li Chun
    adj_year = getattr(chart, "adjusted_year", "")
    li_chun = getattr(chart, "li_chun_date", "")
    is_before = getattr(chart, "is_before_li_chun", False)
    sections.append(f"計算年份 (Adjusted Year): {adj_year} (立春: {li_chun}{'，出生於立春前' if is_before else ''})")
    # Current annual/monthly star
    cur_annual = getattr(chart, "current_year_star", "")
    cur_monthly = getattr(chart, "current_year_month_star", "")
    if cur_annual:
        from astro.nine_star_ki import STAR_BY_NUM as _NSK_STARS
        cas_name = _NSK_STARS.get(cur_annual, {}).get("zh_name", "")
        cams_name = _NSK_STARS.get(cur_monthly, {}).get("zh_name", "")
        sections.append(f"當前流年星 (Current Annual Star): {cur_annual} {cas_name}")
        sections.append(f"當前流月星 (Current Monthly Star): {cur_monthly} {cams_name}")
    # Compatibility
    compat = getattr(chart, "compatibility", [])
    if compat:
        sections.append("\n--- 相性 (Compatibility) ---")
        for c in compat:
            other_info = c.get("other_star_info", {})
            sections.append(
                f"  vs {c.get('other_star', '')} {other_info.get('zh_name', '')}: "
                f"{c.get('label_zh', '')} (score={c.get('score', '')})"
            )
    return "\n".join(sections)


# Mapping from system key to formatter function
SYSTEM_FORMATTERS = {
    "tab_chinese": format_chinese_chart,
    "tab_ziwei": format_ziwei_chart,
    "tab_western": format_western_chart,
    "tab_indian": format_vedic_chart,
    "tab_sukkayodo": format_sukkayodo_chart,
    "tab_thai": format_thai_chart,
    "tab_kabbalistic": format_kabbalistic_chart,
    "tab_arabic": format_arabic_chart,
    "tab_maya": format_maya_chart,
    "tab_aztec": format_aztec_chart,
    "tab_mahabote": format_mahabote_chart,
    "tab_decans": format_decan_chart,
    "tab_nadi": format_nadi_chart,
    "tab_zurkhai": format_zurkhai_chart,
    "tab_hellenistic": format_hellenistic_chart,
    "tab_huangji": format_huangji_chart,
    "tab_chinstar": format_chinstar_chart,
    "tab_twelve_ci": _format_twelve_ci_chart,
    "tab_acg": _format_acg_chart,
    "tab_nine_star_ki": format_nine_star_ki_chart,
    "tab_celtic_tree": lambda chart: (
        __import__("astro.celtic.celtic_tree_graves",
                   fromlist=["format_celtic_tree_for_prompt"])
        .format_celtic_tree_for_prompt(chart)
    ),
}


def format_chart_for_prompt(
    system_key: str,
    chart,
    page_content: str = "",
) -> str:
    """Format a chart object into a text prompt for AI analysis.

    Parameters
    ----------
    system_key : str
        One of the _SYSTEM_KEYS (e.g. ``"tab_western"``).
    chart : object
        The chart object returned by the compute function.
    page_content : str
        Optional extra text content rendered on the page that should also
        be included in the analysis (e.g. natal summary, personality
        readings, swallow analysis).

    Returns
    -------
    str
        Human-readable chart data for the AI prompt.
    """
    formatter = SYSTEM_FORMATTERS.get(system_key)
    if formatter:
        structured = formatter(chart)
        # Append a comprehensive dump of all chart attributes so no data is
        # missed by the specific formatter.  Skip when the structured output
        # was already produced by the generic formatter (no specific
        # formatter existed) to avoid duplicating the same content.
        generic = format_generic_chart(chart, system_key)
        if generic and generic != structured:
            structured += "\n\n--- 完整排盤數據 (Supplementary Data) ---\n" + generic
    else:
        # No specific formatter — the generic dump is the full output.
        structured = format_generic_chart(chart, system_key)

    # Append any additional page-level content.
    if page_content:
        structured += "\n\n--- 頁面附加資訊 (Additional Page Content) ---\n" + page_content

    return structured
