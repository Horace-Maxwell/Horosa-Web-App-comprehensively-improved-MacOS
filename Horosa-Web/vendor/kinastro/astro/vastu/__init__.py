"""
astro/vastu/ — 吠陀風水（Vastu Shastra）整合子套件

將 KinVastu 核心邏輯移植至 KinAstro，結合 VedicChart 命盤
與居所方位，生成個人化「Astro-Vastu 盤」。

主要匯出：
    VastuEngine       — 核心引擎，接收 VedicChart + 房屋朝向
    VastuResult       — 計算結果資料模型
    generate_vastu_disk — 便利函數
"""

from __future__ import annotations

from astro.vastu.engine import VastuEngine, VastuResult, generate_vastu_disk

__all__ = ["VastuEngine", "VastuResult", "generate_vastu_disk"]
