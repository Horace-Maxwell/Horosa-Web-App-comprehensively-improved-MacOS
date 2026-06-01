# -*- coding: utf-8 -*-
import drawsvg as draw
import math

# ======================  共用顏色設定  ======================
BRANCH_COLORS = {
    '子': 'blue',  '亥': 'blue',
    '丑': 'brown', '未': 'brown', '辰': 'brown', '戌': 'brown',
    '寅': 'green', '卯': 'green',
    '巳': 'red',   '午': 'red',
    '申': 'gold',  '酉': 'gold',
    '乾': 'gold',  '坤': 'brown', '艮': 'brown', '巽': 'green',
}

CONSTELLATION_COLORS = {
    '角': 'green', '斗': 'green', '奎': 'green', '井': 'green',
    '尾': 'red',   '室': 'red', '觜': 'red', '翼': 'red',
    '亢': 'gold',  '牛': 'gold', '婁': 'gold', '鬼': 'gold',
    '箕': 'blue',  '壁': 'blue', '參': 'blue', '軫': 'blue',
    '氐': 'brown', '女': 'brown', '胃': 'brown', '柳': 'brown',
    '房': 'orange','虛': 'orange','昴': 'orange','星': 'orange',
    '心': 'silver','危': 'silver','畢': 'silver','張': 'silver',
}

GATE_TO_BRANCH = {
    '休': '子', '生': '丑', '傷': '寅', '杜': '卯',
    '景': '巳', '死': '未', '驚': '申', '開': '酉',
}

TEXT_COLORS = {
    'blue':  'white', 'brown': 'white', 'green': 'white',
    'red':   'white', 'gold':  'black', 'orange':'black',
    'silver':'black', 'black': 'white', 'gray':  'white',
}
# =========================================================

def _format_label(raw):
    if isinstance(raw, list):
        return '\n'.join(str(x) for x in raw)
    return str(raw)

def _get_branch_key(raw_label):
    """取出第一個屬於 BRANCH_COLORS 的字元（地支/八卦）"""
    s = _format_label(raw_label)
    for c in s:
        if c in BRANCH_COLORS:
            return c
    return ''

def _draw_sector(group, start, end, inner, outer, raw_label,
                 is_16_palace=False, is_28_layer=False,
                 is_second_layer=False, is_third_layer=False):
    """共用繪製扇形 + 標籤（支援第 3 層）"""
    # ---- 座標 ----
    sox = outer * math.cos(math.radians(start))
    soy = outer * math.sin(math.radians(start))
    eox = outer * math.cos(math.radians(end))
    eoy = outer * math.sin(math.radians(end))
    six = inner * math.cos(math.radians(start))
    siy = inner * math.sin(math.radians(start))
    eix = inner * math.cos(math.radians(end))
    eiy = inner * math.sin(math.radians(end))

    # ---- 顏色邏輯（優先順序：第 2 層 > 第 3 層 > 16宮 > 28宿）----
    fill = 'black'   # 預設
    if is_second_layer:                     # 八門 → 五行
        text = _format_label(raw_label)
        key = next((c for c in text if c in GATE_TO_BRANCH), None)
        if key:
            fill = BRANCH_COLORS.get(GATE_TO_BRANCH[key], 'gray')
        else:
            fill = 'gray'
    elif is_third_layer:                    # 第 3 層 → 地支五行
        key = _get_branch_key(raw_label)
        fill = BRANCH_COLORS.get(key, 'gray')
    elif is_16_palace:                      # 16 宮 → 地支五行
        key = _get_branch_key(raw_label)
        fill = BRANCH_COLORS.get(key, 'gray')
    elif is_28_layer:                       # 28 宿 → 宿名
        key = raw_label[0] if isinstance(raw_label, list) and raw_label else str(raw_label)
        fill = CONSTELLATION_COLORS.get(key, 'gray')

    text_fill = TEXT_COLORS.get(fill, 'white')

    # ---- 路徑 ----
    p = draw.Path(stroke='white', stroke_width=1.8, fill=fill)
    p.M(six, siy)
    p.L(sox, soy)
    p.A(outer, outer, 0, 0, 1, eox, eoy)
    p.L(eix, eiy)
    p.A(inner, inner, 0, 0, 0, six, siy)
    p.Z()
    group.append(p)

    # ---- 標籤 ----
    label_str = _format_label(raw_label)
    mid = (start + end) / 2
    tx = (inner + outer) / 2 * math.cos(math.radians(mid))
    ty = (inner + outer) / 2 * math.sin(math.radians(mid))
    t = draw.Text(label_str, 9, tx, ty, center=1, fill=text_fill,
                  font_family='sans-serif', font_weight='bold')
    group.append(t)


# ====================  gen_chart  ====================
def gen_chart(first_layer, second_layer, sixth_layer, sevenstars):
    d = draw.Drawing(500, 500, origin="center")
    inner_radius = 13
    layer_gap = 45
    num_divisions = [1, 8, 16, 16, 12]
    rotation_angle = 248

    data = [
        [first_layer],
        second_layer,
        [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'],
         ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'],
         ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'],
         ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        sixth_layer,
        sevenstars
    ]

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 2),
                         is_second_layer=(layer_idx == 1))
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-4.86988571440686,-12.053390109368236 L-21.72718241812291,-53.776663564873665 A58,58,0,0,1,-21.727182418122876,-53.77666356487368 L-4.869885714406852,-12.053390109368237 A13,13,0,0,0,-4.86988571440686,-12.053390109368236 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")


# ====================  gen_chart_life  ====================
def gen_chart_life(second_layer, twelve, sixth_layer, sevenstars):
    d = draw.Drawing(450, 450, origin="center")
    inner_radius = 12
    layer_gap = 35
    num_divisions = [1, 12, 12, 12, 12]          # 第 3 層 = index 2
    rotation_angle = 248

    data = [
        [second_layer],
        twelve,                              # 第 2 層
        ['巳','午','未','申','酉','戌','亥','子','丑','寅','卯','辰'],  # 第 3 層（地支）
        sixth_layer,
        sevenstars
    ]

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 2),   # 第 4 層（index 3）是 16 宮
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2)) # 第 3 層
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-4.495279120990947,-11.126206254801447 L-17.606509890547876,-43.577641164639005 A47,47,0,0,1,-17.606509890547848,-43.57764116463901 L-4.49527912099094,-11.12620625480145 A12,12,0,0,0,-4.495279120990947,-11.126206254801447 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")


# ====================  gen_chart_day  ====================
def gen_chart_day(first_layer, second_layer, golden, sixth_layer, seven_stars):
    d = draw.Drawing(500, 500, origin="center")
    inner_radius = 3
    layer_gap = 31.5
    num_divisions = [1, 8, 8, 16, 16, 12]          # 第 3 層 = index 2
    rotation_angle = 248

    data = [
        [first_layer],
        second_layer,
        golden,                               # 第 3 層（可放地支或文字）
        [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'],
         ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'],
         ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'],
         ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        sixth_layer, 
        seven_stars
    ]

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 3),
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2))   # 第 3 層
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-1.1238197802477368,-2.781551563700362 L-12.923927472848973,-31.987842982554163 A34.5,34.5,0,0,1,-12.923927472848954,-31.98784298255417 L-1.123819780247735,-2.7815515637003627 A3.0,3.0,0,0,0,-1.1238197802477368,-2.781551563700362 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")


# ====================  gen_chart_hour（支援 rotate_28） ====================
def gen_chart_hour(first_layer, second_layer, skygeneral, sixth_layer,
                   twentyeight, seven_stars, degrees, rotate_28=0):
    """
    rotate_28: 28宿旋轉角度（度）
               正數 → 逆時針（擰後）
               負數 → 順時針（擰前）
    """
    d = draw.Drawing(500, 500, origin="center")
    inner_radius = 3
    layer_gap = 31.5
    num_divisions = [1, 8, 16, 16, 16, 28, 12]   # 第 3 層 = index 2
    rotation_angle = 248

    data = [
        [first_layer],
        second_layer,
        skygeneral,                           # 第 3 層（可放地支）
        [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'],
         ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'],
         ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'],
         ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        sixth_layer,
        twentyeight,
        seven_stars
    ]

    cumulative = [0]
    for deg in degrees:
        cumulative.append(cumulative[-1] + deg)

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            if layer_idx == 5:   # 28 宿
                start = cumulative[div] + rotation_angle + rotate_28
                end   = cumulative[div + 1] + rotation_angle + rotate_28
            else:
                start = (360 / divs) * div + rotation_angle
                end   = (360 / divs) * (div + 1) + rotation_angle

            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 3),
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2),   # 第 3 層
                         is_28_layer=(layer_idx == 5))
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-1.1238197802477368,-2.781551563700362 L-12.923927472848973,-31.987842982554163 A34.5,34.5,0,0,1,-12.923927472848954,-31.98784298255417 L-1.123819780247735,-2.7815515637003627 A3.0,3.0,0,0,0,-1.1238197802477368,-2.781551563700362 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")


# ====================  完整測試範例 ====================
if __name__ == "__main__":
    constellations = [
        '角','亢','氐','房','心','尾','箕','斗','牛','女','虛','危',
        '室','壁','奎','婁','胃','昴','畢','觜','參','井','鬼','柳',
        '星','張','翼','軫'
    ]

    # ---------- 測試 gen_chart_hour（第 3 層放地支） ----------
    svg_hour = gen_chart_hour(
        first_layer="太乙",
        second_layer=['休門','生門','傷門','杜門','景門','死門','驚門','開門'],
        skygeneral=['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑','寅','卯'],  # 16 個地支（可自行調整）
        sixth_layer=[['巳','大神','楚']]*16,
        twentyeight=constellations,
        degrees=[360/28]*28,
        rotate_28=-6
    )
    with open("test_hour_third_layer.svg", "w", encoding="utf-8") as f:
        f.write(svg_hour)
    print("已產生 test_hour_third_layer.svg（第 3 層已按地支五行上色）")

    # ---------- 測試 gen_chart_life ----------
    svg_life = gen_chart_life(
        second_layer="中宮",
        twelve=['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑'],
        sixth_layer=['休門','生門','傷門','杜門','景門','死門','驚門','開門'] + ['其他']*4
    )
    with open("test_life_third_layer.svg", "w", encoding="utf-8") as f:
        f.write(svg_life)
    print("已產生 test_life_third_layer.svg（第 3 層為地支，已上色）")






