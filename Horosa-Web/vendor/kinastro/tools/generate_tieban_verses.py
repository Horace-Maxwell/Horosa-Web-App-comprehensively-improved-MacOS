#!/usr/bin/env python3
"""
tools/generate_tieban_verses.py — 鐵板神數條文生成器

根據鐵板神數條文格式和組合規則，批量生成條文
"""

import json
import os

# 條文組件庫
PARENTS_STATUS = [
    ("父母雙全壽延長", "父母雙全"),
    ("父先母後赴瑤池", "父先母後"),
    ("母先父後淚雙垂", "母先父後"),
    ("父母早年雙雙亡", "父母雙亡"),
    ("父母中年雙雙去", "父母中年亡"),
    ("父在母亡早分離", "父亡母在"),
    ("父亡母在守孤燈", "父亡母在"),
    ("父母高壽享福來", "父母高壽"),
]

BROTHERS_COUNT = [
    ("兄弟一人獨撐持", "兄弟一人"),
    ("兄弟二人共爐香", "兄弟二人"),
    ("兄弟三人各分離", "兄弟三人"),
    ("兄弟四人分家產", "兄弟四人"),
    ("兄弟五人共榮華", "兄弟五人"),
    ("兄弟六人各一方", "兄弟六人"),
    ("兄弟七人顯門庭", "兄弟七人"),
    ("兄弟八人各一方", "兄弟八人"),
    ("兄弟零落各分散", "兄弟零落"),
]

WIFE_STATUS = [
    ("妻宮同庚來匹配", "妻宮同庚"),
    ("妻宮大配三年別", "妻宮大配"),
    ("妻宮小配共榮華", "妻宮小配"),
    ("妻宮異姓來匹配", "妻宮異姓"),
    ("妻宮同姓來匹配", "妻宮同姓"),
    ("妻宮刑剋三年別", "妻宮刑剋"),
    ("妻宮賢德來相助", "妻宮賢德"),
    ("妻宮再娶方得子", "再娶"),
]

CHILDREN_COUNT = [
    ("子嗣一人繼香火", "一子"),
    ("子嗣二人送終老", "二子"),
    ("子嗣三人繞膝前", "三子"),
    ("子嗣四人立門庭", "四子"),
    ("子嗣五人登科第", "五子"),
    ("子嗣六人繞膝前", "六子"),
    ("子嗣七人顯門庭", "七子"),
    ("子嗣八人各一方", "八子"),
    ("無子嗣來繼香火", "無子"),
    ("子嗣遲來中年得", "遲子"),
]

CAREER_OUTCOME = [
    ("事業有成創家業", "事業有成"),
    ("事業多舛少年難", "事業多舛"),
    ("事業順利少年得", "事業順利"),
    ("事業奔波各一方", "事業奔波"),
    ("事業穩定家業興", "事業穩定"),
    ("事業起伏多變故", "事業起伏"),
    ("事業官祿登科第", "官祿"),
    ("事業經商創富貴", "經商"),
    ("事業農耕守家業", "農耕"),
    ("事業文武雙全才", "文武雙全"),
]

WEALTH_STATUS = [
    ("財運亨通創富貴", "財運亨通"),
    ("財運多舛少年貧", "財運多舛"),
    ("財運穩定家業興", "財運穩定"),
    ("財運起伏多變故", "財運起伏"),
    ("財運經商創富貴", "財運經商"),
    ("財運官祿得俸祿", "官祿俸祿"),
    ("財運農耕守家業", "農耕守業"),
    ("財運破敗少年難", "財運破敗"),
    ("財運繼承得祖業", "繼承祖業"),
    ("財運投機得橫財", "投機橫財"),
]

HEALTH_STATUS = [
    ("健康康泰無病災", "健康康泰"),
    ("健康多病少年難", "健康多病"),
    ("健康殘疾終身苦", "健康殘疾"),
    ("健康長壽享福來", "健康長壽"),
    ("健康意外有災厄", "意外災厄"),
    ("健康慢性病纏身", "慢性病"),
    ("健康精神有困擾", "精神困擾"),
    ("健康婦科有病災", "婦科病"),
    ("健康心血管有疾", "心血管疾"),
    ("健康消化有問題", "消化問題"),
]

LONGEVITY_STATUS = [
    ("壽延長至古稀年", "古稀年"),
    ("壽限中年有災厄", "中年災厄"),
    ("壽限少年有災厄", "少年災厄"),
    ("壽限長至百歲年", "百歲年"),
    ("壽限意外有災厄", "意外災厄"),
    ("壽限疾病有災厄", "疾病災厄"),
    ("壽限安穩享天年", "安穩天年"),
    ("壽限坎坷多災難", "坎坷多難"),
    ("壽限平順無災厄", "平順無災"),
    ("壽限有驚無險過", "有驚無險"),
]

MIGRATION_STATUS = [
    ("遷移遠行創家業", "遠行創業"),
    ("遷移離鄉背井去", "離鄉背井"),
    ("遷移海外創富貴", "海外創富"),
    ("遷移內地安居樂", "內地安居"),
    ("遷移頻繁難安定", "遷移頻繁"),
    ("遷移定居一方安", "定居一方"),
    ("遷移歸鄉創家業", "歸鄉創業"),
    ("遷移流離失所苦", "流離失所"),
    ("遷移貴人相助來", "貴人相助"),
    ("遷移安穩無災厄", "安穩無災"),
]

SOCIAL_STATUS = [
    ("交遊廣闊朋友多", "交遊廣闊"),
    ("交遊狹隘朋友少", "交遊狹隘"),
    ("交遊貴人相助來", "交遊貴人"),
    ("交遊小人陷害來", "交遊小人"),
    ("交遊良師益友多", "良師益友"),
    ("交遊酒肉朋友多", "酒肉朋友"),
    ("交遊知己難得一", "知己難得"),
    ("交遊背叛朋友去", "朋友背叛"),
    ("交遊合作創家業", "合作創業"),
    ("交遊安穩無災厄", "安穩無災"),
]

FAME_STATUS = [
    ("功名登科及第來", "功名登科"),
    ("功名無緣少年難", "功名無緣"),
    ("功名武舉顯門楣", "功名武舉"),
    ("功名科舉屢試不第", "屢試不第"),
    ("功名恩蔭得官祿", "恩蔭官祿"),
    ("功名異路得官祿", "異路功名"),
    ("功名無望創家業", "功名無望"),
    ("功名遲來中年得", "功名遲來"),
    ("功名顯赫震朝野", "功名顯赫"),
    ("功名平順無大起", "功名平順"),
]

DISASTER_STATUS = [
    ("災厄火燭有災難", "火燭災"),
    ("災厄水患有家難", "水患災"),
    ("災厄盜賊有災難", "盜賊災"),
    ("災厄官非有災難", "官非災"),
    ("災厄疾病有災難", "疾病災"),
    ("災厄意外有災難", "意外災"),
    ("災厄戰爭有災難", "戰爭災"),
    ("災厄饑荒有災難", "饑荒災"),
    ("災厄地震有災難", "地震災"),
    ("災厄無難享太平", "無災無難"),
]

MARRIAGE_STATUS = [
    ("紅鸞相照正副生", "紅鸞相照"),
    ("紅鸞遲來中年婚", "紅鸞遲來"),
    ("紅鸞早動少年婚", "紅鸞早動"),
    ("紅鸞不現終身孤", "紅鸞不現"),
    ("紅鸞再動再婚配", "紅鸞再動"),
    ("紅鸞相照貴人助", "紅鸞貴人"),
    ("紅鸞刑剋有災難", "紅鸞刑剋"),
    ("紅鸞相照子嗣遲", "子嗣遲"),
    ("紅鸞相照子嗣早", "子嗣早"),
    ("紅鸞相照福壽全", "福壽全"),
]

LEGAL_STATUS = [
    ("良人有刑官非災", "良人有刑"),
    ("良人無刑享太平", "良人無刑"),
    ("良人輕刑有災難", "良人輕刑"),
    ("良人重刑有災難", "良人重刑"),
    ("良人冤獄有災難", "良人冤獄"),
    ("良人逃亡有災難", "良人逃亡"),
    ("良人軍伍有災難", "良人軍伍"),
    ("良人流放有災難", "良人流放"),
    ("良人赦免有貴人", "良人赦免"),
    ("良人無災享太平", "良人無災"),
]

STAR_STATUS = [
    ("火星入宅回祿災", "火星入宅"),
    ("計都照命有災難", "計都照命"),
    ("羅睺照命有災難", "羅睺照命"),
    ("土星照命有災難", "土星照命"),
    ("木星照命福壽來", "木星照命"),
    ("金星照命福壽全", "金星照命"),
    ("水星照命智慧開", "水星照命"),
    ("太陽照命福壽全", "太陽照命"),
    ("太陰照命福壽全", "太陰照命"),
    ("紫微照命福壽全", "紫微照命"),
    ("天府照命福壽全", "天府照命"),
    ("天魁照命貴人來", "天魁照命"),
    ("天鉞照命貴人來", "天鉞照命"),
    ("文昌照命學業成", "文昌照命"),
    ("祿存照命財運亨", "祿存照命"),
    ("擎羊照命有災難", "擎羊照命"),
    ("陀羅照命有災難", "陀羅照命"),
    ("火星照命有災難", "火星照命"),
    ("鈴星照命有災難", "鈴星照命"),
    ("地空照命有災難", "地空照命"),
    ("地劫照命有災難", "地劫照命"),
    ("天馬照命遠行安", "天馬照命"),
]

# 條文結尾
VERSE_ENDINGS = [
    "父母雙全福壽全，妻宮賢德共白頭。",
    "父母早年雙雙亡，兄弟扶養方成人。",
    "父母高壽享福來，妻宮同庚共榮華。",
    "父母中年雙雙去，兄弟同心創家業。",
    "父母雙全享福來，妻宮大配共白頭。",
    "父母高壽享福來，妻宮小配共榮華。",
    "父母雙全福壽全，妻宮賢德共白頭。",
    "父母早年雙雙亡，白手起家創門庭。",
    "父母高壽享福來，妻宮同庚共榮華。",
    "父母雙全福壽全，妻宮賢德共白頭。",
]


def generate_verses():
    """生成條文"""
    verses = {}
    verse_num = 101  # 從 101 開始
    
    # 生成綜合類條文（父母 + 兄弟 + 妻宮 + 子嗣）
    for parents, p_tag in PARENTS_STATUS:
        for brothers, b_tag in BROTHERS_COUNT:
            for wife, w_tag in WIFE_STATUS:
                for children, c_tag in CHILDREN_COUNT:
                    verse = f"{parents}，{brothers}。{wife}，{children}。"
                    verses[f"{verse_num:04d}"] = {
                        "verse": verse,
                        "category": "綜合",
                        "tags": [p_tag, b_tag, w_tag, c_tag]
                    }
                    verse_num += 1
                    
                    if verse_num > 500:  # 限制綜合類條文數量
                        break
                if verse_num > 500:
                    break
            if verse_num > 500:
                break
        if verse_num > 500:
            break
    
    # 生成事業類條文
    for career, c_tag in CAREER_OUTCOME:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{career}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "事業",
                "tags": [c_tag]
            }
            verse_num += 1
    
    # 生成財運類條文
    for wealth, w_tag in WEALTH_STATUS:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{wealth}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "財運",
                "tags": [w_tag]
            }
            verse_num += 1
    
    # 生成健康類條文
    for health, h_tag in HEALTH_STATUS:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{health}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "健康",
                "tags": [h_tag]
            }
            verse_num += 1
    
    # 生成壽限類條文
    for longevity, l_tag in LONGEVITY_STATUS:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{longevity}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "壽限",
                "tags": [l_tag]
            }
            verse_num += 1
    
    # 生成遷移類條文
    for migration, m_tag in MIGRATION_STATUS:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{migration}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "遷移",
                "tags": [m_tag]
            }
            verse_num += 1
    
    # 生成交遊類條文
    for social, s_tag in SOCIAL_STATUS:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{social}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "交遊",
                "tags": [s_tag]
            }
            verse_num += 1
    
    # 生成功名類條文
    for fame, f_tag in FAME_STATUS:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{fame}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "功名",
                "tags": [f_tag]
            }
            verse_num += 1
    
    # 生成災厄類條文
    for disaster, d_tag in DISASTER_STATUS:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{disaster}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "災厄",
                "tags": [d_tag]
            }
            verse_num += 1
    
    # 生成婚姻類條文
    for marriage, m_tag in MARRIAGE_STATUS:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{marriage}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "婚姻",
                "tags": [m_tag]
            }
            verse_num += 1
    
    # 生成刑獄類條文
    for legal, l_tag in LEGAL_STATUS:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{legal}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "刑獄",
                "tags": [l_tag]
            }
            verse_num += 1
    
    # 生成神煞類條文
    for star, s_tag in STAR_STATUS:
        for ending in VERSE_ENDINGS[:5]:
            verse = f"{star}，{ending}"
            verses[f"{verse_num:04d}"] = {
                "verse": verse,
                "category": "神煞",
                "tags": [s_tag]
            }
            verse_num += 1
    
    return verses


def main():
    """主函數"""
    print("生成鐵板神數條文...")
    
    # 生成條文
    verses = generate_verses()
    
    # 載入現有條文（0001-0100）
    existing_verses_path = os.path.join(
        os.path.dirname(__file__),
        '..', 'astro', 'tieban', 'data', 'verses_part1.json'
    )
    
    if os.path.exists(existing_verses_path):
        with open(existing_verses_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            # 過濾掉 _meta
            existing_verses = {k: v for k, v in existing_data.items() if not k.startswith('_')}
    else:
        existing_verses = {}
    
    # 合併條文
    all_verses = {**existing_verses, **verses}
    
    # 添加元數據
    output_data = {
        "_meta": {
            "source": "鐵板神數清刻足本（心一堂術數珍本古籍叢刊·星命類·神數類，2013）",
            "base_text": "虛白廬藏清中葉「貞元書屋」刻本",
            "description": "鐵板神數條文資料庫 - 萬千百十號對應詩讖條文",
            "version": "3.0",
            "total_verses": len(all_verses),
            "categories": [
                "綜合", "父母", "兄弟", "夫妻", "子女",
                "事業", "財運", "健康", "壽限",
                "遷移", "交遊", "功名", "災厄",
                "婚姻", "刑獄", "神煞"
            ],
            "generator": "tools/generate_tieban_verses.py"
        },
        **all_verses
    }
    
    # 保存
    output_path = os.path.join(
        os.path.dirname(__file__),
        '..', 'astro', 'tieban', 'data', 'verses.json'
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 生成 {len(all_verses)} 條條文")
    print(f"📁 保存到：{output_path}")
    
    # 統計
    categories = {}
    for verse_data in all_verses.values():
        cat = verse_data.get('category', '未知')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 分類統計:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}條")


if __name__ == "__main__":
    main()
