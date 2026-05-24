from typing import List, Dict, Optional


class ShamsRiyada:
    """《Shams al-Maʻārif al-Kubrā》修持法 (Riyāḍa) 與香料配方完整資料庫"""

    RIYADA: List[Dict] = [
        {
            "name": "رياضة يا كريم يا رحيم (標準版)",
            "chapter": "第126頁",
            "description": "最常用修持法，用於求恩典、化解困難、招福",
            "arabic": "يا كريم يا رحيم (重複特定次數)",
            "steps": [
                "大淨後禮兩拜",
                "面向克爾白，誦『يا كريم يا رحيم』 1000 次",
                "每次誦念後吹氣於水中或紙上",
                "持續 7 天或 40 天"
            ],
            "incense": "乳香 + 白檀香 + 玫瑰",
            "use": "求財富、恩典、困難化解",
            "note": "書中稱此為最簡易有效的 Riyāḍa"
        },
        {
            "name": "رياضة يا كريم يا رحيم (另一版本)",
            "chapter": "第128頁",
            "description": "加強版，適合重大需求",
            "arabic": "يا كريم يا رحيم (配合誓詞)",
            "steps": [
                "大淨 + 禮兩拜",
                "誦『يا كريم يا رحيم』 313 次",
                "每次結束後念特定誓詞 (عزيمة)",
                "連續 11 天"
            ],
            "incense": "乳香 + 沒藥 + 龍腦香",
            "use": "重大需求、開啟運勢、化解極難之事",
            "note": "書中特別提及此版效果更強"
        },
        {
            "name": "رياضة جليلة (Grand Riyāḍa)",
            "chapter": "第130頁",
            "description": "莊嚴大修持，最強力版本",
            "arabic": "يا حافظ بالأبسط يا ودود يا مين",
            "steps": [
                "完全大淨 + 獨處",
                "面向克爾白，誦上述四名 1000 次",
                "每次誦念後默想所求之事",
                "持續 21 天或 40 天"
            ],
            "incense": "乳香 + 沉香 + 白檀 + 玫瑰",
            "use": "極大保護、化解危機、求至高恩典",
            "note": "書中稱此為『رياضة جليلة』，威力極強"
        },
        {
            "name": "رياضة الجلالة (Jalala Riyāḍa)",
            "chapter": "第131頁",
            "description": "威嚴修持法，用於提升地位與斬斷障礙",
            "arabic": "يا جليل يا قتالة",
            "steps": [
                "大淨後獨自修持",
                "誦『يا جليل يا قتالة』 313 次",
                "每次結束後念特定誓詞",
                "連續 7 天"
            ],
            "incense": "沉香 + 乳香 + 沒藥",
            "use": "提升威嚴、斬斷敵人與障礙",
            "note": "適合求權威與地位者"
        },
        {
            "name": "سورة الملك 修持法",
            "chapter": "第135頁",
            "description": "每日睡前修持",
            "arabic": "تبارك الذي بيده الملك...",
            "steps": ["睡前完整誦讀一次蘇萊曼章"],
            "incense": "乳香",
            "use": "保護、免墳墓刑罰、求王權",
            "note": "書中最簡單的每日 Riyāḍa"
        }
    ]

    INCENSE_FORMULAS: List[Dict] = [
        {
            "name": "標準 Riyāḍa 香料",
            "formula": "乳香 + 白檀香 + 玫瑰",
            "use": "一般修持、求恩典",
            "note": "最常用配方"
        },
        {
            "name": "重大需求香料",
            "formula": "乳香 + 沒藥 + 龍腦香",
            "use": "重大祈求、開運",
            "note": "第128頁特別記載"
        },
        {
            "name": "保護與威嚴香料",
            "formula": "沉香 + 乳香 + 沒藥",
            "use": "保護、提升威嚴",
            "note": "適合 Jalala Riyāḍa"
        },
        {
            "name": "蘇萊曼印章香料",
            "formula": "乳香 + 沉香 + 玫瑰",
            "use": "王權、召靈、智慧",
            "note": "第21章記載"
        }
    ]

    def list_all_riyada(self):
        return self.RIYADA

    def get_riyada(self, name: str):
        return next((r for r in self.RIYADA if name.lower() in r["name"].lower()), None)

    def list_all_incense(self):
        return self.INCENSE_FORMULAS

    def print_all(self):
        print("\n=== 《Shams al-Maʻārif》修持法與香料配方 ===")
        print("修持法：")
        for r in self.RIYADA:
            print(f"• {r['name']} ({r['chapter']})")
            print(f"  用途：{r['use']}")
            print(f"  香料：{r['incense']}")
            print(f"  步驟：{r['steps'][0]}...")
            print("---")
        print("\n香料配方：")
        for i in self.INCENSE_FORMULAS:
            print(f"• {i['name']} → {i['formula']} ({i['use']})")
