# ✶ Armenian Astrology（Հայկական Աստղագուշակություն）

## 概述
Armenian Astrology MVP 以 Swiss Ephemeris 計算行星位置（預設 Tropical，可切 Sidereal），再映射為亞美尼亞星座名稱、符號語義與文化詮釋。

## 核心特色
- Armenian Zodiac 12 signs（英文 + Armenian + transliteration）
- Haykian Calendar 近似換算（MVP）
- Orion/Hayk 可見度旗標
- 祖靈／命運關鍵詞（luminary + angular house 加權）
- 支援 Natal / Transit / Secondary Progression / Solar Return

## 文化來源註記
- TunApp: 12 Zodiac Signs, the Armenian Way
- Armeniapedia: Armenian Astrology
- Sevsar 山岩畫黃道地圖資料
- Ancient astronomy in Armenia (ArAS)
- Medieval Armenian astronomical diagram references
- Arevakhach / Armenian eternity sign

## AI 解讀模板（Cerebras / Ollama）
1. 僅採 Armenian cultural framing
2. 先本系統解讀，再跨系統比較（Zi Wei / Hellenistic）
3. 必須附文化脈絡與史料不確定性標註
4. Payload keys：`natal_summary`, `transit_hits`, `progression_hits`, `solar_return`, `haykian_date`, `ancestral_keywords`, `comparison_targets`
