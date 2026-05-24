# -*- coding: utf-8 -*-
"""
Created on Thu Jan  1 00:05:30 2026

@author: hooki
"""


# 球場資料
teamname = {
    "Afghanistan": (34.5, 67.7, "Asia/Kabul"),
    "Albania": (41.3, 19.8, "Europe/Tirane"),
    "Algeria": (28.0, 1.7, "Africa/Algiers"),
    "Andorra": (42.5, 1.6, "Europe/Andorra"),
    "Angola": (-11.2, 17.9, "Africa/Luanda"),
    "Antigua and Barbuda": (17.1, -61.8, "America/Antigua"),
    "Argentina": (-38.4, -63.6, "America/Argentina/Buenos_Aires"),
    "Armenia": (40.8, 44.5, "Asia/Yerevan"),
    "Australia": (-25.3, 133.8, "Australia/Adelaide"),
    "Austria": (47.3, 13.3, "Europe/Vienna"),
    "Azerbaijan": (40.5, 47.6, "Asia/Baku"),
    "Bahamas": (24.7, -76.0, "America/Nassau"),
    "Bahrain": (26.0, 50.6, "Asia/Bahrain"),
    "Bangladesh": (23.7, 90.4, "Asia/Dhaka"),
    "Barbados": (13.2, -59.5, "America/Barbados"),
    "Belarus": (53.9, 27.6, "Europe/Minsk"),
    "Belgium": (50.8, 4.4, "Europe/Brussels"),
    "Belize": (17.2, -88.7, "America/Belize"),
    "Benin": (9.3, 2.3, "Africa/Porto-Novo"),
    "Bhutan": (27.5, 90.7, "Asia/Thimphu"),
    "Bolivia": (-16.3, -63.6, "America/LaPaz"),
    "Bosnia and Herzegovina": (44.0, 18.0, "Europe/Sarajevo"),
    "Botswana": (-22.3, 24.6, "Africa/Gaborone"),
    "Brazil": (-14.2, -51.9, "America/Sao_Paulo"),
    "Brunei": (4.5, 114.7, "Asia/Brunei"),
    "Bulgaria": (42.7, 25.5, "Europe/Sofia"),
    "Burkina Faso": (12.4, -1.5, "Africa/Ouagadougou"),
    "Burundi": (-3.4, 29.9, "Africa/Bujumbura"),
    "Cabo Verde": (16.0, -24.0, "Atlantic/Cape_Verde"),
    "Cambodia": (12.5, 104.9, "Asia/PhnomPenh"),
    "Cameroon": (3.9, 12.0, "Africa/Douala"),
    "Canada": (56.9, -94.0, "America/Toronto"),
    "Central African Republic": (6.7, 20.5, "Africa/Bangui"),
    "Chad": (15.5, 18.8, "Africa/Ndjamena"),
    "Chile": (-35.7, -71.5, "America/Santiago"),
    "China": (35.9, 104.2, "Asia/Shanghai"),
    "Colombia": (4.6, -74.1, "America/Bogota"),
    "Comoros": (-11.7, 43.3, "Indian/Comoro"),
    "Congo (Congo-Brazzaville)": (-0.8, 11.9, "Africa/Brazzaville"),
    "Costa Rica": (9.9, -84.1, "America/CostaRica"),
    "Croatia": (45.2, 15.2, "Europe/Zagreb"),
    "Cuba": (21.5, -78.0, "America/Havana"),
    "Cyprus": (35.1, 33.4, "Asia/Nicosia"),
    "Czechia (Czech Republic)": (49.8, 15.5, "Europe/Prague"),
    "Denmark": (56.0, 9.5, "Europe/Copenhagen"),
    "Djibouti": (11.6, 42.6, "Africa/Djibouti"),
    "Dominica": (15.4, -61.4, "America/Dominica"),
    "Dominican Republic": (18.5, -69.9, "America/SantoDomingo"),
    "Ecuador": (-1.8, -78.2, "America/Guayaquil"),
    "Egypt": (26.8, 30.8, "Africa/Cairo"),
    "El Salvador": (13.7, -88.9, "America/ElSalvador"),
    "Equatorial Guinea": (1.6, 10.0, "Africa/Malabo"),
    "Eritrea": (15.3, 39.0, "Africa/Asmara"),
    "Estonia": (58.8, 25.7, "Europe/Tallinn"),
    "Eswatini (fmr. Swaziland)": (-26.5, 31.3, "Africa/Mbabane"),
    "Ethiopia": (9.0, 38.7, "Africa/AddisAbaba"),
    "Fiji": (-16.9, 179.4, "Pacific/Fiji"),
    "Finland": (64.0, 26.0, "Europe/Helsinki"),
    "France": (46.6, 1.9, "Europe/Paris"),
    "Gabon": (-0.4, 9.5, "Africa/Libreville"),
    "Gambia": (13.4, -16.6, "Africa/Banjul"),
    "Georgia": (42.0, 43.5, "Asia/Tbilisi"),
    "Germany": (51.2, 10.5, "Europe/Berlin"),
    "Ghana": (7.9, -1.0, "Africa/Accra"),
    "Greece": (39.1, 21.8, "Europe/Athens"),
    "Grenada": (12.1, -61.7, "America/Grenada"),
    "Guatemala": (15.8, -90.2, "America/Guatemala"),
    "Guinea": (9.6, -13.7, "Africa/Conakry"),
    "Guinea-Bissau": (11.9, -15.6, "Africa/Bissau"),
    "Guyana": (4.8, -58.9, "America/Guyana"),
    "Haiti": (18.5, -72.3, "America/Port-au-Prince"),
    "Honduras": (15.2, -86.2, "America/Tegucigalpa"),
    "Hungary": (47.0, 19.9, "Europe/Budapest"),
    "Iceland": (65.0, -18.0, "Atlantic/Reykjavik"),
    "India": (20.6, 78.5, "Asia/Kolkata"),
    "Indonesia": (-0.8, 113.9, "Asia/Jakarta"),
    "Iran": (32.4, 53.7, "Asia/Tehran"),
    "Iraq": (33.0, 44.4, "Asia/Baghdad"),
    "Ireland": (53.3, -8.0, "Europe/Dublin"),
    "Israel": (31.5, 34.8, "Asia/Jerusalem"),
    "Italy": (42.8, 12.8, "Europe/Rome"),
    "Ivory Coast": (8.0, -5.3, "Africa/Abidjan"),
    "Jamaica": (18.1, -77.3, "America/Jamaica"),
    "Japan": (36.2, 138.3, "Asia/Tokyo"),
    "Jordan": (31.2, 36.9, "Asia/Amman"),
    "Kazakhstan": (48.0, 66.9, "Asia/Almaty"),
    "Kenya": (-0.1, 37.9, "Africa/Nairobi"),
    "Kiribati": (1.4, 173.0, "Pacific/Tarawa"),
    "Kuwait": (29.3, 47.6, "Asia/Kuwait"),
    "Kyrgyzstan": (41.1, 74.6, "Asia/Bishkek"),
    "Laos": (19.9, 102.6, "Asia/Vientiane"),
    "Latvia": (56.9, 24.8, "Europe/Riga"),
    "Lebanon": (33.9, 35.9, "Asia/Beirut"),
    "Lesotho": (-29.6, 28.3, "Africa/Maseru"),
    "Liberia": (6.5, -9.4, "Africa/Monrovia"),
    "Libya": (26.8, 17.2, "Africa/Tripoli"),
    "Liechtenstein": (47.1, 9.5, "Europe/Vaduz"),
    "Lithuania": (55.3, 23.8, "Europe/Vilnius"),
    "Luxembourg": (49.6, 6.1, "Europe/Luxembourg"),
    "Madagascar": (-18.9, 46.7, "Indian/Antananarivo"),
    "Malawi": (-13.3, 34.0, "Africa/Blantyre"),
    "Malaysia": (4.2, 101.9, "Asia/KualaLumpur"),
    "Maldives": (3.3, 73.0, "Indian/Maldives"),
    "Mali": (17.0, -3.9, "Africa/Bamako"),
    "Malta": (35.9, 14.4, "Europe/Malta"),
    "Marshall Islands": (7.1, 171.4, "Pacific/Majuro"),
    "Mauritania": (21.0, -10.0, "Africa/Nouakchott"),
    "Mauritius": (-20.3, 57.6, "Indian/Mauritius"),
    "Mexico": (23.6, -102.5, "America/Mexico_City"),
    "Micronesia": (6.9, 158.2, "Pacific/Chuuk"),
    "Moldova": (47.0, 28.3, "Europe/Chisinau"),
    "Monaco": (43.7, 7.4, "Europe/Monaco"),
    "Mongolia": (46.9, 103.9, "Asia/Ulaanbaatar"),
    "Montenegro": (42.5, 19.3, "Europe/Podgorica"),
    "Morocco": (31.8, -7.0, "Africa/Casablanca"),
    "Mozambique": (-18.2, 35.0, "Africa/Maputo"),
    "Myanmar (formerly Burma)": (21.9, 95.9, "Asia/Yangon"),
    "Namibia": (-22.6, 17.1, "Africa/Windhoek"),
    "Nauru": (-0.5, 166.9, "Pacific/Nauru"),
    "Nepal": (28.2, 84.1, "Asia/Kathmandu"),
    "Netherlands": (52.2, 4.9, "Europe/Amsterdam"),
    "New Zealand": (-40.9, 174.9, "Pacific/Auckland"),
    "Nicaragua": (12.9, -85.6, "America/Managua"),
    "Niger": (17.0, 8.0, "Africa/Niamey"),
    "Nigeria": (9.1, 8.7, "Africa/Lagos"),
    "North Korea": (40.3, 127.5, "Asia/Pyongyang"),
    "North Macedonia": (41.6, 21.7, "Europe/Skopje"),
    "Norway": (60.4, 8.4, "Europe/Oslo"),
    "Oman": (21.5, 55.9, "Asia/Muscat"),
    "Pakistan": (30.4, 69.1, "Asia/Karachi"),
    "Palau": (7.5, 134.6, "Pacific/Palau"),
    "Palestine": (31.9, 35.2, "Asia/Gaza"),
    "Panama": (8.5, -80.0, "America/Panama"),
    "Papua New Guinea": (-6.3, 143.8, "Pacific/Port_Moresby"),
    "Paraguay": (-23.4, -58.4, "America/Asuncion"),
    "Peru": (-9.2, -74.2, "America/Lima"),
    "Philippines": (12.8, 121.8, "Asia/Manila"),
    "Poland": (51.9, 19.1, "Europe/Warsaw"),
    "Portugal": (39.5, -8.2, "Europe/Lisbon"),
    "Qatar": (25.3, 51.2, "Asia/Qatar"),
    "Romania": (45.9, 24.9, "Europe/Bucharest"),
    "Russia": (61.5, 105.3, "Asia/Moscow"),
    "Rwanda": (-1.9, 29.9, "Africa/Kigali"),
    "Saint Kitts and Nevis": (17.3, -62.8, "America/StKitts"),
    "Saint Lucia": (13.9, -60.9, "America/StLucia"),
    "Saint Vincent and the Grenadines": (13.2, -61.2, "America/StVincent"),
    "Samoa": (-13.8, -172.0, "Pacific/Apia"),
    "San Marino": (43.9, 12.4, "Europe/San_Marino"),
    "Sao Tome and Principe": (0.3, 6.7, "Africa/Sao_Tome"),
    "Saudi Arabia": (23.7, 45.0, "Asia/Riyadh"),
    "Senegal": (14.0, -14.0, "Africa/Dakar"),
    "Serbia": (44.2, 20.5, "Europe/Belgrade"),
    "Seychelles": (-4.6, 55.5, "Indian/Mahe"),
    "Sierra Leone": (8.5, -11.8, "Africa/Freetown"),
    "Singapore": (1.3, 103.8, "Asia/Singapore"),
    "Slovakia": (48.7, 19.5, "Europe/Bratislava"),
    "Slovenia": (46.1, 14.5, "Europe/Ljubljana"),
    "Solomon Islands": (-8.0, 159.0, "Pacific/Guadalcanal"),
    "Somalia": (2.0, 45.3, "Africa/Mogadishu"),
    "South Africa": (-30.6, 22.9, "Africa/Johannesburg"),
    "South Korea": (35.9, 127.7, "Asia/Seoul"),
    "South Sudan": (6.9, 31.3, "Africa/Juba"),
    "Spain": (40.0, -3.7, "Europe/Madrid"),
    "Sri Lanka": (7.9, 80.7, "Asia/Colombo"),
    "Sudan": (15.5, 32.5, "Africa/Khartoum"),
    "Suriname": (3.9, -56.0, "America/Paramaribo"),
    "Sweden": (60.1, 18.7, "Europe/Stockholm"),
    "Switzerland": (46.8, 8.2, "Europe/Zurich"),
    "Syria": (34.8, 38.0, "Asia/Damascus"),
    "Taiwan": (23.7, 121.0, "Asia/Taipei"),
    "Tajikistan": (38.6, 70.8, "Asia/Dushanbe"),
    "Tanzania": (-6.2, 34.9, "Africa/DaresSalaam"),
    "Thailand": (15.9, 100.9, "Asia/Bangkok"),
    "Timor-Leste": (-8.9, 125.6, "Asia/Dili"),
    "Togo": (8.6, 0.8, "Africa/Lome"),
    "Tonga": (-20.9, -175.2, "Pacific/Tongatapu"),
    "Trinidad and Tobago": (10.7, -61.2, "America/PortofSpain"),
    "Tunisia": (33.9, 9.5, "Africa/Tunis"),
    "Turkey": (38.9, 35.2, "Europe/Istanbul"),
    "Turkmenistan": (38.0, 59.0, "Asia/Ashgabat"),
    "Tuvalu": (-7.1, 177.7, "Pacific/Funafuti"),
    "Uganda": (1.4, 32.6, "Africa/Kampala"),
    "Ukraine": (48.4, 31.2, "Europe/Kyiv"),
    "United Arab Emirates": (23.4, 53.8, "Asia/Dubai"),
    "United Kingdom": (55.4, -3.4, "Europe/London"),
    "United States": (37.1, -95.7, "America/New_York"),
    "Uruguay": (-32.9, -55.8, "America/Montevideo"),
    "Uzbekistan": (41.4, 64.6, "Asia/Tashkent"),
    "Vanuatu": (-15.4, 166.9, "Pacific/Efate"),
    "Vatican City": (41.9, 12.5, "Europe/Vatican"),
    "Venezuela": (6.4, -66.0, "America/Caracas"),
    "Vietnam": (14.1, 108.3, "Asia/Ho_Chi_Minh"),
    "Yemen": (15.4, 48.0, "Asia/Aden"),
    "Zambia": (-13.6, 27.9, "Africa/Lusaka"),
    "Zimbabwe": (-19.0, 29.2, "Africa/Harare"),
    "阿富汗": (34.5, 67.7, "Asia/Kabul"),
    "阿爾巴尼亞": (41.3, 19.8, "Europe/Tirane"),
    "阿爾及利亞": (28.0, 1.7, "Africa/Algiers"),
    "安道爾": (42.5, 1.6, "Europe/Andorra"),
    "安哥拉": (-11.2, 17.9, "Africa/Luanda"),
    "安提瓜和巴布達": (17.1, -61.8, "America/Antigua"),
    "阿根廷": (-38.4, -63.6, "America/Argentina/Buenos_Aires"),
    "阿根廷女足": (-38.4, -63.6, "America/Argentina/Buenos_Aires"),
    "亞美尼亞": (40.8, 44.5, "Asia/Yerevan"),
    "澳洲": (-25.3, 133.8, "Australia/Adelaide"),
    "澳洲女足": (-25.3, 133.8, "Australia/Adelaide"),
    "奧地利": (47.3, 13.3, "Europe/Vienna"),
    "亞塞拜然": (40.5, 47.6, "Asia/Baku"),
    "巴哈馬": (24.7, -76.0, "America/Nassau"),
    "巴林": (26.0, 50.6, "Asia/Bahrain"),
    "孟加拉": (23.7, 90.4, "Asia/Dhaka"),
    "巴巴多斯": (13.2, -59.5, "America/Barbados"),
    "白俄羅斯": (53.9, 27.6, "Europe/Minsk"),
    "比利時": (50.8, 4.4, "Europe/Brussels"),
    "貝里斯": (17.2, -88.7, "America/Belize"),
    "貝寧": (9.3, 2.3, "Africa/Porto-Novo"),
    "不丹": (27.5, 90.7, "Asia/Thimphu"),
    "玻利維亞": (-16.3, -63.6, "America/LaPaz"),
    "波斯尼亞和黑塞哥維那": (44.0, 18.0, "Europe/Sarajevo"),
    "博茨瓦納": (-22.3, 24.6, "Africa/Gaborone"),
    "巴西": (-14.2, -51.9, "America/Sao_Paulo"),
    "巴西女足": (-14.2, -51.9, "America/Sao_Paulo"),
    "汶萊": (4.5, 114.7, "Asia/Brunei"),
    "保加利亞": (42.7, 25.5, "Europe/Sofia"),
    "布基納法索": (12.4, -1.5, "Africa/Ouagadougou"),
    "布隆迪": (-3.4, 29.9, "Africa/Bujumbura"),
    "維德角": (16.0, -24.0, "Atlantic/CapeVerde"),
    "柬埔寨": (12.5, 104.9, "Asia/PhnomPenh"),
    "喀麥隆": (3.9, 12.0, "Africa/Douala"),
    "加拿大": (56.9, -94.0, "America/Toronto"),
    "中非共和國": (6.7, 20.5, "Africa/Bangui"),
    "乍得": (15.5, 18.8, "Africa/Ndjamena"),
    "智利": (-35.7, -71.5, "America/Santiago"),
    "中國": (35.9, 104.2, "Asia/Shanghai"),
    "中國女足": (35.9, 104.2, "Asia/Shanghai"),
    "哥倫比亞": (4.6, -74.1, "America/Bogota"),
    "科摩羅": (-11.7, 43.3, "Indian/Comoro"),
    "剛果（布）": (-0.8, 11.9, "Africa/Brazzaville"),
    "哥斯達黎加": (9.9, -84.1, "America/CostaRica"),
    "克羅地亞": (45.2, 15.2, "Europe/Zagreb"),
    "古巴": (21.5, -78.0, "America/Havana"),
    "塞浦路斯": (35.1, 33.4, "Asia/Nicosia"),
    "捷克": (49.8, 15.5, "Europe/Prague"),
    "丹麥": (56.0, 9.5, "Europe/Copenhagen"),
    "吉布提": (11.6, 42.6, "Africa/Djibouti"),
    "多米尼克": (15.4, -61.4, "America/Dominica"),
    "多明尼加共和國": (18.5, -69.9, "America/Santo_Domingo"),
    "厄瓜多爾": (-1.8, -78.2, "America/Guayaquil"),
    "厄瓜多爾女足U20": (-1.8, -78.2, "America/Guayaquil"),
    "埃及": (26.8, 30.8, "Africa/Cairo"),
    "薩爾瓦多": (13.7, -88.9, "America/ElSalvador"),
    "赤道幾內亞": (1.6, 10.0, "Africa/Malabo"),
    "厄立特里亞": (15.3, 39.0, "Africa/Asmara"),
    "愛沙尼亞": (58.8, 25.7, "Europe/Tallinn"),
    "史瓦帝尼": (-26.5, 31.3, "Africa/Mbabane"),
    "埃塞俄比亞": (9.0, 38.7, "Africa/AddisAbaba"),
    "斐濟": (-16.9, 179.4, "Pacific/Fiji"),
    "芬蘭": (64.0, 26.0, "Europe/Helsinki"),
    "法國": (46.6, 1.9, "Europe/Paris"),
    "加蓬": (-0.4, 9.5, "Africa/Libreville"),
    "岡比亞": (13.4, -16.6, "Africa/Banjul"),
    "格魯吉亞": (42.0, 43.5, "Asia/Tbilisi"),
    "德國": (51.2, 10.5, "Europe/Berlin"),
    "加納": (7.9, -1.0, "Africa/Accra"),
    "希臘": (39.1, 21.8, "Europe/Athens"),
    "格林納達": (12.1, -61.7, "America/Grenada"),
    "危地馬拉": (15.8, -90.2, "America/Guatemala"),
    "幾內亞": (9.6, -13.7, "Africa/Conakry"),
    "幾內亞比索": (11.9, -15.6, "Africa/Bissau"),
    "圭亞那": (4.8, -58.9, "America/Guyana"),
    "海地": (18.5, -72.3, "America/Port-au-Prince"),
    "洪都拉斯": (15.2, -86.2, "America/Tegucigalpa"),
    "匈牙利": (47.0, 19.9, "Europe/Budapest"),
    "冰島": (65.0, -18.0, "Atlantic/Reykjavik"),
    "印度": (20.6, 78.5, "Asia/Kolkata"),
    "印度女足": (20.6, 78.5, "Asia/Kolkata"),
    "印尼": (-0.8, 113.9, "Asia/Jakarta"),
    "伊朗": (32.4, 53.7, "Asia/Tehran"),
    "伊拉克": (33.0, 44.4, "Asia/Baghdad"),
    "愛爾蘭": (53.3, -8.0, "Europe/Dublin"),
    "以色列": (31.5, 34.8, "Asia/Jerusalem"),
    "意大利": (42.8, 12.8, "Europe/Rome"),
    "象牙海岸": (8.0, -5.3, "Africa/Abidjan"),
    "牙買加": (18.1, -77.3, "America/Jamaica"),
    "日本": (36.2, 138.3, "Asia/Tokyo"),
    "日本女足": (36.2, 138.3, "Asia/Tokyo"),
    "約旦": (31.2, 36.9, "Asia/Amman"),
    "哈薩克": (48.0, 66.9, "Asia/Almaty"),
    "肯尼亞": (-0.1, 37.9, "Africa/Nairobi"),
    "基里巴斯": (1.4, 173.0, "Pacific/Tarawa"),
    "科威特": (29.3, 47.6, "Asia/Kuwait"),
    "吉爾吉斯": (41.1, 74.6, "Asia/Bishkek"),
    "老撾": (19.9, 102.6, "Asia/Vientiane"),
    "拉脫維亞": (56.9, 24.8, "Europe/Riga"),
    "黎巴嫩": (33.9, 35.9, "Asia/Beirut"),
    "萊索托": (-29.6, 28.3, "Africa/Maseru"),
    "利比里亞": (6.5, -9.4, "Africa/Monrovia"),
    "利比亞": (26.8, 17.2, "Africa/Tripoli"),
    "列支敦士登": (47.1, 9.5, "Europe/Vaduz"),
    "立陶宛": (55.3, 23.8, "Europe/Vilnius"),
    "盧森堡": (49.6, 6.1, "Europe/Luxembourg"),
    "盧森堡女足": (49.6, 6.1, "Europe/Luxembourg"),
    "馬達加斯加": (-18.9, 46.7, "Indian/Antananarivo"),
    "馬拉維": (-13.3, 34.0, "Africa/Blantyre"),
    "馬來西亞": (4.2, 101.9, "Asia/KualaLumpur"),
    "馬爾代夫": (3.3, 73.0, "Indian/Maldives"),
    "馬里": (17.0, -3.9, "Africa/Bamako"),
    "馬爾他": (35.9, 14.4, "Europe/Malta"),
    "馬紹爾群島": (7.1, 171.4, "Pacific/Majuro"),
    "茅利塔尼亞": (21.0, -10.0, "Africa/Nouakchott"),
    "模里西斯": (-20.3, 57.6, "Indian/Mauritius"),
    "墨西哥": (23.6, -102.5, "America/Mexico_City"),
    "密克羅尼西亞": (6.9, 158.2, "Pacific/Chuuk"),
    "摩爾多瓦": (47.0, 28.3, "Europe/Chisinau"),
    "蒙古": (46.9, 103.9, "Asia/Ulaanbaatar"),
    "黑山": (42.5, 19.3, "Europe/Podgorica"),
    "摩洛哥": (31.8, -7.0, "Africa/Casablanca"),
    "莫桑比克": (-18.2, 35.0, "Africa/Maputo"),
    "緬甸": (21.9, 95.9, "Asia/Yangon"),
    "納米比亞": (-22.6, 17.1, "Africa/Windhoek"),
    "諾魯": (-0.5, 166.9, "Pacific/Nauru"),
    "尼泊爾": (28.2, 84.1, "Asia/Kathmandu"),
    "荷蘭": (52.2, 4.9, "Europe/Amsterdam"),
    "紐西蘭": (-40.9, 174.9, "Pacific/Auckland"),
    "尼加拉瓜": (12.9, -85.6, "America/Managua"),
    "尼日": (17.0, 8.0, "Africa/Niamey"),
    "尼日利亞": (9.1, 8.7, "Africa/Lagos"),
    "北韓": (40.3, 127.5, "Asia/Pyongyang"),
    "北馬其頓": (41.6, 21.7, "Europe/Skopje"),
    "挪威": (60.4, 8.4, "Europe/Oslo"),
    "阿曼": (21.5, 55.9, "Asia/Muscat"),
    "巴基斯坦": (30.4, 69.1, "Asia/Karachi"),
    "帛琉": (7.5, 134.6, "Pacific/Palau"),
    "巴勒斯坦": (31.9, 35.2, "Asia/Gaza"),
    "巴拿馬": (8.5, -80.0, "America/Panama"),
    "巴布亞新幾內亞": (-6.3, 143.8, "Pacific/Port_Moresby"),
    "巴拉圭": (-23.4, -58.4, "America/Asuncion"),
    "秘魯": (-9.2, -74.2, "America/Lima"),
    "菲律賓": (12.8, 121.8, "Asia/Manila"),
    "菲律賓女足": (12.8, 121.8, "Asia/Manila"),
    "波蘭": (51.9, 19.1, "Europe/Warsaw"),
    "葡萄牙": (39.5, -8.2, "Europe/Lisbon"),
    "葡萄牙女足": (39.5, -8.2, "Europe/Lisbon"),
    "葡萄牙女足U23": (39.5, -8.2, "Europe/Lisbon"),
    "卡塔爾": (25.3, 51.2, "Asia/Qatar"),
    "羅馬尼亞": (45.9, 24.9, "Europe/Bucharest"),
    "俄羅斯": (61.5, 105.3, "Asia/Moscow"),
    "盧旺達": (-1.9, 29.9, "Africa/Kigali"),
    "聖基茨和尼維斯": (17.3, -62.8, "America/StKitts"),
    "聖露西亞": (13.9, -60.9, "America/StLucia"),
    "聖文森特和格林納丁斯": (13.2, -61.2, "America/StVincent"),
    "薩摩亞": (-13.8, -172.0, "Pacific/Apia"),
    "聖馬力諾": (43.9, 12.4, "Europe/SanMarino"),
    "聖多美普林西比": (0.3, 6.7, "Africa/SaoTome"),
    "沙地阿拉伯": (23.7, 45.0, "Asia/Riyadh"),
    "塞內加爾": (14.0, -14.0, "Africa/Dakar"),
    "塞爾維亞": (44.2, 20.5, "Europe/Belgrade"),
    "塞舌爾": (-4.6, 55.5, "Indian/Mahe"),
    "塞拉利昂": (8.5, -11.8, "Africa/Freetown"),
    "新加坡": (1.3, 103.8, "Asia/Singapore"),
    "斯洛伐克": (48.7, 19.5, "Europe/Bratislava"),
    "斯洛文尼亞": (46.1, 14.5, "Europe/Ljubljana"),
    "所羅門群島": (-8.0, 159.0, "Pacific/Guadalcanal"),
    "索馬里": (2.0, 45.3, "Africa/Mogadishu"),
    "南非": (-30.6, 22.9, "Africa/Johannesburg"),
    "南韓": (35.9, 127.7, "Asia/Seoul"),
    "南韓女足": (35.9, 127.7, "Asia/Seoul"),
    "南蘇丹": (6.9, 31.3, "Africa/Juba"),
    "西班牙": (40.0, -3.7, "Europe/Madrid"),
    "斯里蘭卡": (7.9, 80.7, "Asia/Colombo"),
    "蘇丹": (15.5, 32.5, "Africa/Khartoum"),
    "蘇里南": (3.9, -56.0, "America/Paramaribo"),
    "瑞典": (60.1, 18.7, "Europe/Stockholm"),
    "瑞士": (46.8, 8.2, "Europe/Zurich"),
    "敘利亞": (34.8, 38.0, "Asia/Damascus"),
    "台灣": (23.7, 121.0, "Asia/Taipei"),
    "塔吉克": (38.6, 70.8, "Asia/Dushanbe"),
    "坦桑尼亞": (-6.2, 34.9, "Africa/DaresSalaam"),
    "泰國": (15.9, 100.9, "Asia/Bangkok"),
    "東帝汶": (-8.9, 125.6, "Asia/Dili"),
    "多哥": (8.6, 0.8, "Africa/Lome"),
    "湯加": (-20.9, -175.2, "Pacific/Tongatapu"),
    "千里達及托巴哥": (10.7, -61.2, "America/PortofSpain"),
    "突尼西亞": (33.9, 9.5, "Africa/Tunis"),
    "土耳其": (38.9, 35.2, "Europe/Istanbul"),
    "土庫曼": (38.0, 59.0, "Asia/Ashgabat"),
    "圖瓦盧": (-7.1, 177.7, "Pacific/Funafuti"),
    "烏干達": (1.4, 32.6, "Africa/Kampala"),
    "烏克蘭": (48.4, 31.2, "Europe/Kyiv"),
    "阿拉伯聯合酋長國": (23.4, 53.8, "Asia/Dubai"),
    "英國": (55.4, -3.4, "Europe/London"),
    "美國": (37.1, -95.7, "America/New_York"),
    "烏拉圭": (-32.9, -55.8, "America/Montevideo"),
    "烏茲別克": (41.4, 64.6, "Asia/Tashkent"),
    "瓦努阿圖": (-15.4, 166.9, "Pacific/Efate"),
    "梵蒂岡": (41.9, 12.5, "Europe/Vatican"),
    "委內瑞拉": (6.4, -66.0, "America/Caracas"),
    "委內瑞拉女足U20": (6.4, -66.0, "America/Caracas"),
    "越南": (14.1, 108.3, "Asia/Ho_Chi_Minh"),
    "也門": (15.4, 48.0, "Asia/Aden"),
    "贊比亞": (-13.6, 27.9, "Africa/Lusaka"),
    "贊比亞女足": (-13.6, 27.9, "Africa/Lusaka"),
    "津巴布韋": (-19.0, 29.2, "Africa/Harare"),
    #英超
    "arsenal": (51.5549, -0.1088, "Europe/London"),  # Emirates Stadium
    "aston villa": (52.5091, -1.8848, "Europe/London"),  # Villa Park
    "bournemouth": (50.7353, -1.8383, "Europe/London"),  # Vitality Stadium
    "brentford": (51.4908, -0.2887, "Europe/London"),  # Gtech Community Stadium
    "brighton": (50.8616, -0.0837, "Europe/London"),  # American Express Stadium
    "burnley": (53.7890, -2.2303, "Europe/London"),  # Turf Moor
    "chelsea": (51.4818, -0.1910, "Europe/London"),  # Stamford Bridge
    "crystal palace": (51.3983, -0.0855, "Europe/London"),  # Selhurst Park
    "everton": (53.4390, -2.9650, "Europe/London"),  # Hill Dickinson Stadium (新球場)
    "fulham": (51.4750, -0.2216, "Europe/London"),  # Craven Cottage
    "leeds united": (53.7778, -1.5722, "Europe/London"),  # Elland Road
    "liverpool": (53.4308, -2.9608, "Europe/London"),  # Anfield
    "manchester city": (53.4831, -2.2004, "Europe/London"),  # Etihad Stadium
    "manchester united": (53.4631, -2.2913, "Europe/London"),  # Old Trafford
    "newcastle united": (54.9755, -1.6217, "Europe/London"),  # St James' Park
    "nottingham forest": (52.9399, -1.1329, "Europe/London"),  # City Ground
    "sunderland": (54.9144, -1.3882, "Europe/London"),  # Stadium of Light
    "tottenham hotspur": (51.6033, -0.0664, "Europe/London"),  # Tottenham Hotspur Stadium
    "west ham united": (51.5387, -0.0166, "Europe/London"),  # London Stadium
    "wolverhampton wanderers": (52.5902, -2.1303, "Europe/London"),  # Molineux Stadium
    "阿仙奴": (51.5549, -0.1088, "Europe/London"),  # Emirates Stadium
    "阿士東維拉": (52.5091, -1.8848, "Europe/London"),  # Villa Park
    "般尼茅夫": (50.7353, -1.8383, "Europe/London"),  # Vitality Stadium
    "賓福特": (51.4908, -0.2887, "Europe/London"),  # Gtech Community Stadium
    "白禮頓": (50.8616, -0.0837, "Europe/London"),  # American Express Stadium
    "般尼": (53.7890, -2.2303, "Europe/London"),  # Turf Moor
    "車路士": (51.4818, -0.1910, "Europe/London"),  # Stamford Bridge
    "水晶宮": (51.3983, -0.0855, "Europe/London"),  # Selhurst Park
    "愛華頓": (53.4390, -2.9650, "Europe/London"),  # Hill Dickinson Stadium (新球場)
    "富咸": (51.4750, -0.2216, "Europe/London"),  # Craven Cottage
    "列斯聯": (53.7778, -1.5722, "Europe/London"),  # Elland Road
    "利物浦": (53.4308, -2.9608, "Europe/London"),  # Anfield
    "曼城": (53.4831, -2.2004, "Europe/London"),  # Etihad Stadium
    "曼聯": (53.4631, -2.2913, "Europe/London"),  # Old Trafford
    "紐卡素": (54.9755, -1.6217, "Europe/London"),  # St James' Park
    "諾定咸森林": (52.9399, -1.1329, "Europe/London"),  # City Ground
    "新特蘭": (54.9144, -1.3882, "Europe/London"),  # Stadium of Light
    "熱刺": (51.6033, -0.0664, "Europe/London"),  # Tottenham Hotspur Stadium
    "韋斯咸": (51.5387, -0.0166, "Europe/London"),  # London Stadium
    "狼隊": (52.5902, -2.1303, "Europe/London"),  # Molineux Stadium
    # 英甲 EFL League One 2025/26 (主要球隊，涵蓋24隊)
    "luton town": (51.8840, -0.4317, "Europe/London"),  # Kenilworth Road
    "cardiff city": (51.4728, -3.2031, "Europe/London"),  # Cardiff City Stadium
    "bolton wanderers": (53.5806, -2.5356, "Europe/London"),  # Toughsheet Community Stadium
    "huddersfield town": (53.6543, -1.7683, "Europe/London"),  # John Smith's Stadium
    "plymouth argyle": (50.3878, -4.1508, "Europe/London"),  # Home Park
    "leyton orient": (51.5601, -0.0127, "Europe/London"),  # Brisbane Road
    "barnsley": (53.5523, -1.4676, "Europe/London"),  # Oakwell
    "blackpool": (53.8049, -3.0482, "Europe/London"),  # Bloomfield Road
    "wigan athletic": (53.5476, -2.6539, "Europe/London"),  # DW Stadium
    "reading": (51.4372, -0.9826, "Europe/London"),  # Select Car Leasing Stadium (Madejski)
    "peterborough united": (52.5653, -0.2405, "Europe/London"),  # London Road Stadium
    "wycombe wanderers": (51.6303, -0.8003, "Europe/London"),  # Adams Park
    "charlton athletic": (51.4863, 0.0364, "Europe/London"),  # The Valley
    "bristol rovers": (51.4861, -2.5831, "Europe/London"),  # Memorial Stadium
    "exeter city": (50.7314, -3.5128, "Europe/London"),  # St James Park
    "lincoln city": (53.2183, -0.5406, "Europe/London"),  # Sincil Bank
    "northampton town": (52.2353, -0.9336, "Europe/London"),  # Sixfields Stadium
    "oxford united": (51.7104, -1.2080, "Europe/London"),  # Kassam Stadium (若未升級調整)
    "stockport county": (53.4089, -2.1917, "Europe/London"),  # Edgeley Park
    "mansfield town": (53.1372, -1.1994, "Europe/London"),  # Field Mill
    "burton albion": (52.8222, -1.6269, "Europe/London"),  # Pirelli Stadium
    "crawley town": (51.0997, -0.1928, "Europe/London"),  # Broadfield Stadium
    "shrewsbury town": (52.6889, -2.7492, "Europe/London"),  # New Meadow
    "cambridge united": (52.2125, 0.1542, "Europe/London"),  # Abbey Stadium
    "stevenage": ( 51.8872331177, -0.18949757534,"Europe/London"),
    "rotherham united": (53.428101, -1.36172,"Europe/London"), 
    "哈特斯菲爾德": (53.6543, -1.7683, "Europe/London"),
    # 英乙 EFL League Two 2025/26
    "accrington stanley": (53.7653, -2.3710, "Europe/London"),  # Crown Ground / Wham Stadium
    "afc wimbledon": (51.4050, -0.2822, "Europe/London"),  # Plough Lane
    "barnet": (51.6028, -0.1922, "Europe/London"),  # The Hive Stadium
    "bradford city": (53.8043, -1.7590, "Europe/London"),  # Valley Parade (部分可能降級)
    "bromley": (51.3908, 0.0208, "Europe/London"),  # Hayes Lane
    "carlisle united": (54.8953, -2.9136, "Europe/London"),  # Brunton Park
    "cheltenham town": (51.9061, -2.0603, "Europe/London"),  # Completely-Suzuki Stadium
    "chesterfield": (53.2539, -1.4250, "Europe/London"),  # SMH Group Stadium
    "colchester united": (51.8867, -0.8967, "Europe/London"),  # JobServe Community Stadium
    "crewe alexandra": (53.0874, -2.4357, "Europe/London"),  # Gresty Road
    "doncaster rovers": (53.5078, -1.1128, "Europe/London"),  # Eco-Power Stadium
    "fleetwood town": (53.9161, -3.0250, "Europe/London"),  # Highbury Stadium
    "費列活特": (53.9161, -3.0250, "Europe/London"),  # Highbury Stadium
    "gillingham": (51.3842, 0.5606, "Europe/London"),  # Priestfield Stadium
    "基寧咸": (51.3842, 0.5606, "Europe/London"),  # Priestfield Stadium
    "grimsby town": (53.5703, -0.0949, "Europe/London"),  # Blundell Park
    "barrow": (54.1236, -3.2358, "Europe/London"),
    "巴羅": (54.1236, -3.2358, "Europe/London"),
    "甘士比": (53.5703, -0.0949, "Europe/London"),  # Blundell Park
    "harrogate town": (53.9921, -1.5148, "Europe/London"),  # Exercise Stadium
    "milton keynes dons": (52.0097, -0.7333, "Europe/London"),  # Stadium MK
    "morecambe": (54.0614, -2.8672, "Europe/London"),  # Mazuma Stadium
    "newport county": (51.5881, -2.9889, "Europe/London"),  # Rodney Parade
    "notts county": (52.9547, -1.1372, "Europe/London"),  # Meadow Lane
    "oldham athletic": (53.5528, -2.1286, "Europe/London"),  # Boundary Park
    "port vale": (53.0497, -2.1922, "Europe/London"),  # Vale Park
    "salford city": (53.5096, -2.3753, "Europe/London"),  # Peninsula Stadium
    "swindon town": (51.5644, -1.7706, "Europe/London"),  # County Ground
    "tranmere rovers": (53.3689, -3.0308, "Europe/London"),  # Prenton Park
    
    "盧頓": (51.8840, -0.4317, "Europe/London"),          # Luton Town - Kenilworth Road
    "卡迪夫城": (51.4728, -3.2031, "Europe/London"),        # Cardiff City - Cardiff City Stadium
    "博爾頓": (53.5806, -2.5356, "Europe/London"),          # Bolton Wanderers - Toughsheet Community Stadium
    "哈德斯菲爾德": (53.6543, -1.7683, "Europe/London"),    # Huddersfield Town - John Smith's Stadium
    "普利茅夫": (50.3878, -4.1508, "Europe/London"),        # Plymouth Argyle - Home Park
    "萊頓東方": (51.5601, -0.0127, "Europe/London"),        # Leyton Orient - Brisbane Road
    "班士利": (53.5523, -1.4676, "Europe/London"),          # Barnsley - Oakwell
    "黑池": (53.8049, -3.0482, "Europe/London"),            # Blackpool - Bloomfield Road
    "韋根": (53.5476, -2.6539, "Europe/London"),            # Wigan Athletic - DW Stadium
    "雷丁": (51.4372, -0.9826, "Europe/London"),            # Reading - Select Car Leasing Stadium (Madejski)
    "彼得堡聯": (52.5653, -0.2405, "Europe/London"),        # Peterborough United - London Road Stadium
    "韋甘比": (51.6303, -0.8003, "Europe/London"),          # Wycombe Wanderers - Adams Park
    "查爾頓": (51.4863, 0.0364, "Europe/London"),           # Charlton Athletic - The Valley
    "布里斯托流浪": (51.4861, -2.5831, "Europe/London"),    # Bristol Rovers - Memorial Stadium
    "艾克塞特城": (50.7314, -3.5128, "Europe/London"),      # Exeter City - St James Park
    "林肯城": (53.2183, -0.5406, "Europe/London"),          # Lincoln City - Sincil Bank
    "北安普頓": (52.2353, -0.9336, "Europe/London"),        # Northampton Town - Sixfields Stadium
    "牛津聯": (51.7104, -1.2080, "Europe/London"),          # Oxford United - Kassam Stadium
    "史托港郡": (53.4089, -2.1917, "Europe/London"),        # Stockport County - Edgeley Park
    "曼斯菲": (53.1372, -1.1994, "Europe/London"),          # Mansfield Town - Field Mill
    "博爾頓阿爾比恩": (52.8222, -1.6269, "Europe/London"),  # Burton Albion - Pirelli Stadium
    "克勞利鎮": (51.0997, -0.1928, "Europe/London"),        # Crawley Town - Broadfield Stadium
    "梳士巴利": (52.6889, -2.7492, "Europe/London"),        # Shrewsbury Town - New Meadow
    "劍橋聯": (52.2125, 0.1542, "Europe/London"),           # Cambridge United - Abbey Stadium
    "史蒂文納治": (51.8872, -0.1895, "Europe/London"),      # Stevenage - Lamex Stadium
    "羅瑟勒姆": (53.4281, -1.3617, "Europe/London"),        # Rotherham United - AESSEAL New York Stadium

    # 英乙 EFL League Two 2025/26
    "阿克靈頓斯坦利": (53.7653, -2.3710, "Europe/London"),  # Accrington Stanley - Crown Ground / Wham Stadium
    "AFC溫布頓": (51.4050, -0.2822, "Europe/London"),       # AFC Wimbledon - Plough Lane
    "巴尼特": (51.6028, -0.1922, "Europe/London"),          # Barnet - The Hive Stadium
    "巴拉福特城": (53.8043, -1.7590, "Europe/London"),      # Bradford City - Valley Parade
    "布羅姆利": (51.3908, 0.0208, "Europe/London"),         # Bromley - Hayes Lane
    "卡素爾聯": (54.8953, -2.9136, "Europe/London"),        # Carlisle United - Brunton Park
    "切爾滕漢姆": (51.9061, -2.0603, "Europe/London"),      # Cheltenham Town - Completely-Suzuki Stadium
    "切斯特菲爾德": (53.2539, -1.4250, "Europe/London"),    # Chesterfield - SMH Group Stadium
    "車士打菲特": (53.4281, -1.3617, "Europe/London"),
    "洛達咸": (53.4281, -1.3617, "Europe/London"),
    "高車士打聯": (51.8867, -0.8967, "Europe/London"),      # Colchester United - JobServe Community Stadium
    "克魯亞歷山德拉": (53.0874, -2.4357, "Europe/London"),  # Crewe Alexandra - Gresty Road
    "唐卡斯特": (53.5078, -1.1128, "Europe/London"),        # Doncaster Rovers - Eco-Power Stadium
    "弗利特伍德鎮": (53.9161, -3.0250, "Europe/London"),    # Fleetwood Town - Highbury Stadium
    "基寧漢姆": (51.3842, 0.5606, "Europe/London"),         # Gillingham - Priestfield Stadium
    "格林斯比鎮": (53.5703, -0.0949, "Europe/London"),      # Grimsby Town - Blundell Park
    "哈羅蓋特鎮": (53.9921, -1.5148, "Europe/London"),      # Harrogate Town - Exercise Stadium
    "米爾頓凱恩斯": (52.0097, -0.7333, "Europe/London"),    # Milton Keynes Dons - Stadium MK
    "摩甘比": (54.0614, -2.8672, "Europe/London"),          # Morecambe - Mazuma Stadium
    "紐波特郡": (51.5881, -2.9889, "Europe/London"),        # Newport County - Rodney Parade
    "諾茨郡": (52.9547, -1.1372, "Europe/London"),          # Notts County - Meadow Lane
    "奧咸": (53.5528, -2.1286, "Europe/London"),            # Oldham Athletic - Boundary Park
    "維爾港": (53.0497, -2.1922, "Europe/London"),        # Port Vale - Vale Park
    "薩福德城": (53.5096, -2.3753, "Europe/London"),        # Salford City - Peninsula Stadium
    "史雲頓鎮": (51.5644, -1.7706, "Europe/London"),        # Swindon Town - County Ground
    "彼德堡": (52.5653, -0.2405, "Europe/London"),
    "特蘭米亞": (53.3689, -3.0308, "Europe/London"),         # Tranmere Rovers - Prenton Park
    "諾咸頓": (52.2353, -0.9336, "Europe/London"),
    "保頓": (53.5806, -2.5356, "Europe/London"),
    #英冠
    "birmingham city": (52.4756, -1.8680, "Europe/London"),  # St Andrew's
    "blackburn rovers": (53.7286, -2.4892, "Europe/London"),  # Ewood Park
    "bristol city": (51.4401, -2.6203, "Europe/London"),  # Ashton Gate
    "coventry city": (52.4481, -1.4966, "Europe/London"),  # Coventry Building Society Arena
    "derby county": (52.9149, -1.4472, "Europe/London"),  # Pride Park
    "hull city": (53.7461, -0.3678, "Europe/London"),  # MKM Stadium
    "ipswich town": (52.0551, 1.1454, "Europe/London"),  # Portman Road
    "leicester city": (52.6204, -1.1423, "Europe/London"),  # King Power Stadium
    "middlesbrough": (54.5782, -1.2169, "Europe/London"),  # Riverside Stadium
    "millwall": (51.4860, -0.0509, "Europe/London"),  # The Den
    "norwich city": (52.6222, 1.3086, "Europe/London"),  # Carrow Road
    "portsmouth": (50.7965, -1.0639, "Europe/London"),  # Fratton Park
    "preston north end": (53.7722, -2.6882, "Europe/London"),  # Deepdale
    "queens park rangers": (51.5092, -0.2322, "Europe/London"),  # Loftus Road
    "sheffield united": (53.3703, -1.4707, "Europe/London"),  # Bramall Lane
    "sheffield wednesday": (53.4114, -1.5005, "Europe/London"),  # Hillsborough Stadium
    "southampton": (50.9058, -1.3910, "Europe/London"),  # St Mary's Stadium
    "stoke city": (52.9884, -2.1754, "Europe/London"),  # bet365 Stadium
    "swansea city": (51.6427, -3.9347, "Europe/London"),  # Swansea.com Stadium
    "watford": (51.6499, -0.4015, "Europe/London"),  # Vicarage Road
    "west bromwich albion": (52.5090, -1.9640, "Europe/London"),  # The Hawthorns
    "wrexham": (53.0520, -2.9935, "Europe/London"), # Racecourse Ground
    "walsall": (52.5656, -1.9910, "Europe/London"),  #
    "伯明翰": (52.4756, -1.8680, "Europe/London"),          # Birmingham City - St Andrew's
    "布力般流浪": (53.7286, -2.4892, "Europe/London"),
    "布里斯托城": (51.4401, -2.6203, "Europe/London"),       # Bristol City - Ashton Gate
    "高雲地利城": (52.4481, -1.4966, "Europe/London"),       # Coventry City - Coventry Building Society Arena
    "打比郡": (52.9149, -1.4472, "Europe/London"),           # Derby County - Pride Park
    "赫爾城": (53.7461, -0.3678, "Europe/London"),           # Hull City - MKM Stadium
    "葉士域治": (52.0551, 1.1454, "Europe/London"),          # Ipswich Town - Portman Road
    "李斯特城": (52.6204, -1.1423, "Europe/London"),         # Leicester City - King Power Stadium
    "錫周三": (53.4114, -1.5005, "Europe/London"),
    "史提芬納治": (54.9783, -1.6217, "Europe/London"),
    "埃克塞特": (50.7314, -3.5128, "Europe/London"),
    "唐卡士打": (53.5806, -2.5356, "Europe/London"),
    "米杜士堡": (54.5782, -1.2169, "Europe/London"),         # Middlesbrough - Riverside Stadium
    "米禾爾": (51.4860, -0.0509, "Europe/London"),           # Millwall - The Den
    "諾域治": (52.6222, 1.3086, "Europe/London"),            # Norwich City - Carrow Road
    "樸茨茅夫": (50.7965, -1.0639, "Europe/London"),         # Portsmouth - Fratton Park
    "普雷斯頓": (53.7722, -2.6882, "Europe/London"),         # Preston North End - Deepdale
    "昆士柏流浪": (51.5092, -0.2322, "Europe/London"),       # Queens Park Rangers - Loftus Road
    "錫菲聯": (53.3703, -1.4707, "Europe/London"),           # Sheffield United - Bramall Lane
    "錫菲星期三": (53.4114, -1.5005, "Europe/London"),       # Sheffield Wednesday - Hillsborough Stadium
    "修咸頓": (50.9058, -1.3910, "Europe/London"),           # Southampton - St Mary's Stadium
    "史篤城": (52.9884, -2.1754, "Europe/London"),           # Stoke City - bet365 Stadium
    "史雲斯城": (51.6427, -3.9347, "Europe/London"),         # Swansea City - Swansea.com Stadium
    "屈福特": (51.6499, -0.4015, "Europe/London"),           # Watford - Vicarage Road
    "西布朗": (52.5090, -1.9640, "Europe/London"),           # West Bromwich Albion - The Hawthorns
    "華素爾": (52.5656, -1.9910, "Europe/London"),            # Walsall - Bescot Stadium
    "域斯咸": (53.0520, -2.9935, "Europe/London"),
    "沙福特城": (53.4281, -1.3617, "Europe/London"),
    #Isthmian League Premier Division
    "aveley": (51.50339, 0.26083, "Europe/London"), # Parkside
    "billericaytown": (51.6287, 0.4196, "Europe/London"), # New Lodge
    "brentwoodtown": (51.63374, 0.29981, "Europe/London"), # The Brentwood Centre Arena
    "burgesshilltown": (50.9648, -0.1228, "Europe/London"), # Leylands Park
    "canveyisland": (51.5222, 0.5750, "Europe/London"), # Park Lane
    "carshaltonathletic": (51.367, -0.161, "Europe/London"), # War Memorial Sports Ground
    "chathamtown": (51.381, 0.528, "Europe/London"), # The Bauvill Stadium
    "cheshunt": (51.693492, -0.039286, "Europe/London"), # Theobalds Lane
    "chichestercity": (50.842986, -0.77726, "Europe/London"), # Oaklands Park
    "crayvalleypapermills": (51.4506149, 0.0348962, "Europe/London"), # Badgers Sports Ground
    "craywanderers": (51.429584, 0.081342, "Europe/London"), # Flamingo Park
    "dartford": (51.4356, 0.2251, "Europe/London"), # Princes Park
    "dulwichhamlet": (51.4616, -0.0849, "Europe/London"), # Champion Hill
    "folkestoneinvicta": (51.0853, 1.1557, "Europe/London"), # Cheriton Road
    "hashtagunited": (51.50339, 0.26083, "Europe/London"), # Parkside
    "lewes": (50.86902, 0.01229, "Europe/London"), # The Dripping Pan
    "pottersbartown": (51.688492, -0.246289, "Europe/London"), # Parkfield
    "ramsgate": (51.333616, 1.402976, "Europe/London"), # Southwood Stadium
    "stalbanscity": (51.75, -0.33333, "Europe/London"), # Clarence Park
    "wellingunited": (51.460375, 0.121482, "Europe/London"), # Park View Road
    "whitehawk": (50.827192, -0.112527, "Europe/London"), # The Enclosed Ground
    "wingateandfinchley": (51.75425, -0.32521, "Europe/London"), # The Maurice Rebak Stadium
    #英足南部聯賽
    "hungerford town fc": (51.40867, -1.515257,"Europe/London"),
    # 蘇超 Scottish Premiership 2025/26
    "aberdeen": (57.1599, -2.1052, "Europe/London"),  # Pittodrie Stadium
    "celtic": (55.8497, -4.2055, "Europe/London"),  # Celtic Park
    "dundee": (56.4753, -2.9690, "Europe/London"),  # Dens Park
    "dundee united": (56.4745, -2.9689, "Europe/London"),  # Tannadice Park
    "falkirk": (55.9986, -3.7589, "Europe/London"),  # Falkirk Stadium
    "hearts": (55.9393, -3.2323, "Europe/London"),  # Tynecastle Park
    "hibernian": (55.9617, -3.1652, "Europe/London"),  # Easter Road
    "kilmarnock": (55.6044, -4.4839, "Europe/London"),  # Rugby Park
    "livingston": (55.8867, -3.5228, "Europe/London"),  # Almondvale Stadium
    "motherwell": (55.7797, -3.9802, "Europe/London"),  # Fir Park
    "rangers": (55.8532, -4.3093, "Europe/London"),  # Ibrox Stadium
    "st mirren": (55.8506, -4.4437, "Europe/London"),  # St Mirren Park
    "鴨巴甸": (57.1599, -2.1052, "Europe/London"),          # Aberdeen - Pittodrie Stadium
    "些路迪": (55.8497, -4.2055, "Europe/London"),          # Celtic - Celtic Park
    "登地": (56.4753, -2.9690, "Europe/London"),            # Dundee - Dens Park
    "登地聯": (56.4745, -2.9689, "Europe/London"),          # Dundee United - Tannadice Park
    "福爾柯克": (55.9986, -3.7589, "Europe/London"),        # Falkirk - Falkirk Stadium
    "赫斯": (55.9393, -3.2323, "Europe/London"),            # Hearts - Tynecastle Park
    "喜伯年": (55.9617, -3.1652, "Europe/London"),          # Hibernian - Easter Road
    "基爾馬諾克": (55.6044, -4.4839, "Europe/London"),      # Kilmarnock - Rugby Park
    "利文斯頓": (55.8867, -3.5228, "Europe/London"),        # Livingston - Almondvale Stadium
    "馬瑟韋爾": (55.7797, -3.9802, "Europe/London"),        # Motherwell - Fir Park
    "格拉斯哥流浪": (55.8532, -4.3093, "Europe/London"),   # Rangers - Ibrox Stadium
    "聖美倫": (55.8506, -4.4437, "Europe/London"),           # St Mirren - St Mirren Park
    # 意甲 Serie A 2025/26
    "juventus": (45.1096, 7.6413, "Europe/Rome"),  # Allianz Stadium
    "inter milan": (45.4781, 9.1240, "Europe/Rome"),  # San Siro (Giuseppe Meazza)
    "ac milan": (45.4781, 9.1240, "Europe/Rome"),  # San Siro (共享)
    "napoli": (40.8280, 14.1930, "Europe/Rome"),  # Diego Armando Maradona
    "roma": (41.9339, 12.4547, "Europe/Rome"),  # Stadio Olimpico
    "lazio": (41.9339, 12.4547, "Europe/Rome"),  # Stadio Olimpico (共享)
    "atalanta": (45.705330512, 9.675163966, "Europe/Rome"),  # Gewiss Stadium
    "fiorentina": (43.7808, 11.2822, "Europe/Rome"),  # Stadio Artemio Franchi
    "bologna": (44.4922, 11.3097, "Europe/Rome"),  # Stadio Renato Dall'Ara
    "torino": (45.0417, 7.6500, "Europe/Rome"),  # Stadio Olimpico Grande Torino
    "udinese": (46.0817, 13.2000, "Europe/Rome"),  # Bluenergy Stadium (Friuli)
    "genoa": (44.4164, 8.9500, "Europe/Rome"),  # Stadio Luigi Ferraris
    "sampdoria": (44.4164, 8.9500, "Europe/Rome"),  # Stadio Luigi Ferraris (共享)
    "hellas verona": (45.4353, 10.9686, "Europe/Rome"),  # Stadio Marcantonio Bentegodi
    "parma": (44.7947, 10.3378, "Europe/Rome"),  # Stadio Ennio Tardini
    "lecce": (40.3653, 18.2089, "Europe/Rome"),  # Stadio Via del Mare
    "cagliari": (39.1992, 9.1350, "Europe/Rome"),  # Unipol Domus
    "sassuolo": (44.7147, 10.6489, "Europe/Rome"),  # Mapei Stadium – Città del Tricolore
    "cremonese": (45.1431, 10.0228, "Europe/Rome"),  # Stadio Giovanni Zini
    "pisa": (43.6831, 10.4006, "Europe/Rome"),  # Arena Garibaldi – Stadio Romeo Anconetani
    "como": (45.8083301, 9.06999972 , "Europe/Rome"),
    "祖雲達斯": (45.1096, 7.6413, "Europe/Rome"),          # Juventus - Allianz Stadium
    "國際米蘭": (45.4781, 9.1240, "Europe/Rome"),          # Inter Milan - San Siro (Giuseppe Meazza)
    "AC米蘭": (45.4781, 9.1240, "Europe/Rome"),            # AC Milan - San Siro (共享)
    "拿玻里": (40.8280, 14.1930, "Europe/Rome"),           # Napoli - Diego Armando Maradona
    "拿玻里女足": (40.8280, 14.1930, "Europe/Rome"),           # Napoli - Diego Armando Maradona
    "羅馬": (41.9339, 12.4547, "Europe/Rome"),             # Roma - Stadio Olimpico
    "拉素": (41.9339, 12.4547, "Europe/Rome"),             # Lazio - Stadio Olimpico (共享)
    "阿特蘭大": (45.705330512, 9.675163966, "Europe/Rome"), # Atalanta - Gewiss Stadium
    "費倫天拿": (43.7808, 11.2822, "Europe/Rome"),         # Fiorentina - Stadio Artemio Franchi
    "博洛尼亞": (44.4922, 11.3097, "Europe/Rome"),         # Bologna - Stadio Renato Dall'Ara
    "拖連奴": (45.0417, 7.6500, "Europe/Rome"),            # Torino - Stadio Olimpico Grande Torino
    "烏甸尼斯": (46.0817, 13.2000, "Europe/Rome"),         # Udinese - Bluenergy Stadium (Friuli)
    "熱拿亞": (44.4164, 8.9500, "Europe/Rome"),            # Genoa - Stadio Luigi Ferraris
    "熱拿亞女足": (44.4164, 8.9500, "Europe/Rome"),            # Genoa - Stadio Luigi Ferraris
    "森多利亞": (44.4164, 8.9500, "Europe/Rome"),          # Sampdoria - Stadio Luigi Ferraris (共享)
    "維羅納": (45.4353, 10.9686, "Europe/Rome"),           # Hellas Verona - Stadio Marcantonio Bentegodi
    "帕爾馬": (44.7947, 10.3378, "Europe/Rome"),           # Parma - Stadio Ennio Tardini
    "利察": (40.3653, 18.2089, "Europe/Rome"),             # Lecce - Stadio Via del Mare
    "卡利亞里": (39.1992, 9.1350, "Europe/Rome"),          # Cagliari - Unipol Domus
    "薩斯索羅": (44.7147, 10.6489, "Europe/Rome"),         # Sassuolo - Mapei Stadium – Città del Tricolore
    "克雷莫納": (45.1431, 10.0228, "Europe/Rome"),         # Cremonese - Stadio Giovanni Zini
    "比薩": (43.6831, 10.4006, "Europe/Rome"),             # Pisa - Arena Garibaldi – Stadio Romeo Anconetani
    "科木": (45.8083301, 9.06999972, "Europe/Rome"),        # Como - Stadio Giuseppe Sinigaglia,
    "萊切": (40.3519, 18.1725, "Europe/Rome"),
    # 日職聯 J1 League 2025
    "kashima antlers": (35.9917, 140.6392, "Asia/Tokyo"),  # Kashima Soccer Stadium
    "urawa red diamonds": (35.9031, 139.7175, "Asia/Tokyo"),  # Saitama Stadium 2002
    "yokohama f. marinos": (35.5100, 139.6064, "Asia/Tokyo"),  # Nissan Stadium
    "kawasaki frontale": (35.5860, 139.6500, "Asia/Tokyo"),  # Uvance Todoroki Stadium
    "fc tokyo": (35.6645, 139.5272, "Asia/Tokyo"),  # Ajinomoto Stadium
    "machida zelvia": (35.5436, 139.4386, "Asia/Tokyo"),  # Machida GION Stadium
    "tokyo verdy": (35.6645, 139.5272, "Asia/Tokyo"),  # Ajinomoto Stadium (共享)
    "albirex niigata": (37.8828, 139.0589, "Asia/Tokyo"),  # Denka Big Swan Stadium
    "sanfrecce hiroshima": (34.3928, 132.4556, "Asia/Tokyo"),  # EDION Peace Wing Hiroshima
    "gamba osaka": (34.8117, 135.5383, "Asia/Tokyo"),  # Panasonic Stadium Suita
    "cerezo osaka": (34.6147, 135.5164, "Asia/Tokyo"),  # Yodoko Sakura Stadium
    "vissel kobe": (34.6567, 135.1692, "Asia/Tokyo"),  # Noevir Stadium Kobe
    "kyoto sanga": (34.9944, 135.7153, "Asia/Tokyo"),  # Sanga Stadium by Kyocera
    "nagoya grampus": (35.0847, 137.1711, "Asia/Tokyo"),  # Toyota Stadium
    "avispa fukuoka": (33.5861, 130.4606, "Asia/Tokyo"),  # Best Denki Stadium
    "shimizu s-pulse": (35.0208, 138.4836, "Asia/Tokyo"),  # IAI Stadium Nihondaira
    "yokohama fc": (35.4672, 139.6033, "Asia/Tokyo"),  # NHK Spring Mitsuzawa Stadium
    "fagiano okayama": (34.6792, 133.9197, "Asia/Tokyo"),  # City Light Stadium
    "kashiwa reysol": (35.8483, 139.9750, "Asia/Tokyo"),  # Sankyo Frontier Kashiwa Stadium
    "shonan bellmare": (35.3433, 139.3417, "Asia/Tokyo"),  # Lemon Gas Stadium Hiratsuka
    # 日乙 J2 League 2025（部分常見球隊，包含降級與升級）
    "hokkaido consadole sapporo": (43.0150, 141.4097, "Asia/Tokyo"),  # Sapporo Dome
    "jubilo iwata": (34.7244, 137.8733, "Asia/Tokyo"),  # Yamaha Stadium
    "sagan tosu": (33.3717, 130.5208, "Asia/Tokyo"),  # Ekimae Real Estate Stadium
    "vegalta sendai": (38.3192, 140.8822, "Asia/Tokyo"),  # Yurtec Stadium Sendai
    "blaublitz akita": (39.7178, 140.1000, "Asia/Tokyo"),  # Soyu Stadium
    "montedio yamagata": (38.3347, 140.3672, "Asia/Tokyo"),  # ND Soft Stadium Yamagata
    "fukushima united": (37.7625, 140.3736, "Asia/Tokyo"),  # Toho Stadium
    "mito hollyhock": (36.3439, 140.3969, "Asia/Tokyo"),  # K's denki Stadium Mito
    "jef united chiba": (35.5781, 140.1233, "Asia/Tokyo"),  # Fukuda Denshi Arena
    "omiya ardija": (35.8967, 139.6339, "Asia/Tokyo"),  # NACK5 Stadium Omiya
    "ventforet kofu": (35.6250, 138.6064, "Asia/Tokyo"),  # JIT Recycle Ink Stadium
    "renofa yamaguchi": (34.0167, 131.4667, "Asia/Tokyo"),  # Ishin Me-Life Stadium
    "tokushima vortis": (34.0667, 134.6000, "Asia/Tokyo"),  # Pocarisweat Stadium
    "ehime fc": (33.7667, 132.7833, "Asia/Tokyo"),  # Ningineer Stadium
    "v-varen nagasaki": (32.7500, 129.8667, "Asia/Tokyo"),  # Transcosmos Stadium Nagasaki
    "roasso kumamoto": (32.8333, 130.8000, "Asia/Tokyo"),  # EGAO Kenko Stadium
    "oita trinita": (33.2000, 131.6500, "Asia/Tokyo"),  # Resonac Dome Oita
    "fujieda myfc": (34.8667, 138.2333, "Asia/Tokyo"),  # Fujieda Soccer Stadium
    "iwaki fc": (36.9667, 140.8833, "Asia/Tokyo"),  # Hawaiians Stadium Iwaki
    "thespakusatsu gunma": (36.4167, 139.0833, "Asia/Tokyo"),  # Shoda Shoyu Stadium Gunma
    "tochigi sc": (36.5667, 139.8333, "Asia/Tokyo"),  # Kanseki Stadium Tochigi
    "kagoshima united": (31.5667, 130.5500, "Asia/Tokyo"),  # Shiranami Stadium
    "kataller toyama": (36.625056, 137.195688, "Asia/Tokyo"),
    "鹿島鹿角": (35.9917, 140.6392, "Asia/Tokyo"),          # Kashima Antlers - Kashima Soccer Stadium
    "浦和紅鑽": (35.9031, 139.7175, "Asia/Tokyo"),          # Urawa Red Diamonds - Saitama Stadium 2002
    "橫濱水手": (35.5100, 139.6064, "Asia/Tokyo"),          # Yokohama F. Marinos - Nissan Stadium
    "川崎前鋒": (35.5860, 139.6500, "Asia/Tokyo"),          # Kawasaki Frontale - Uvance Todoroki Stadium
    "FC東京": (35.6645, 139.5272, "Asia/Tokyo"),            # FC Tokyo - Ajinomoto Stadium
    "町田澤維亞": (35.5436, 139.4386, "Asia/Tokyo"),        # Machida Zelvia - Machida GION Stadium
    "東京綠茵": (35.6645, 139.5272, "Asia/Tokyo"),          # Tokyo Verdy - Ajinomoto Stadium (共享)
    "東京綠茵女足": (35.6645, 139.5272, "Asia/Tokyo"),          # Tokyo Verdy - Ajinomoto Stadium (共享)
    "新潟天鵝": (37.8828, 139.0589, "Asia/Tokyo"),          # Albirex Niigata - Denka Big Swan Stadium
    "廣島三箭": (34.3928, 132.4556, "Asia/Tokyo"),          # Sanfrecce Hiroshima - EDION Peace Wing Hiroshima
    "廣島三箭女足": (34.3928, 132.4556, "Asia/Tokyo"),          # Sanfrecce Hiroshima - EDION Peace Wing Hiroshima
    "大阪飛腳": (34.8117, 135.5383, "Asia/Tokyo"),          # Gamba Osaka - Panasonic Stadium Suita
    "大阪櫻花": (34.6147, 135.5164, "Asia/Tokyo"),          # Cerezo Osaka - Yodoko Sakura Stadium
    "神戶勝利船": (34.6567, 135.1692, "Asia/Tokyo"),        # Vissel Kobe - Noevir Stadium Kobe
    "京都不死鳥": (34.9944, 135.7153, "Asia/Tokyo"),          # Kyoto Sanga - Sanga Stadium by Kyocera
    "名古屋鯨魚": (35.0847, 137.1711, "Asia/Tokyo"),        # Nagoya Grampus - Toyota Stadium
    "福岡黃蜂": (33.5861, 130.4606, "Asia/Tokyo"),          # Avispa Fukuoka - Best Denki Stadium
    "清水心跳": (35.0208, 138.4836, "Asia/Tokyo"),          # Shimizu S-Pulse - IAI Stadium Nihondaira
    "橫濱FC": (35.4672, 139.6033, "Asia/Tokyo"),            # Yokohama FC - NHK Spring Mitsuzawa Stadium
    "岡山雉雞": (34.6792, 133.9197, "Asia/Tokyo"),          # Fagiano Okayama - City Light Stadium
    "柏雷素爾": (35.8483, 139.9750, "Asia/Tokyo"),          # Kashiwa Reysol - Sankyo Frontier Kashiwa Stadium
    "湘南比馬": (35.3433, 139.3417, "Asia/Tokyo"),          # Shonan Bellmare - Lemon Gas Stadium Hiratsuka
    "仙台邁那比女足": (38.2569, 140.8792, "Asia/Tokyo"),
    # J2 League 部分常見球隊（日乙）
    "岡山綠雉": (34.7561, 133.9197, "Asia/Tokyo"),
    "北海道札幌岡薩多": (43.0150, 141.4097, "Asia/Tokyo"),        # Hokkaido Consadole Sapporo - Sapporo Dome
    "磐田山葉": (34.7244, 137.8733, "Asia/Tokyo"),          # Júbilo Iwata - Yamaha Stadium
    "鳥棲砂岩": (33.3717, 130.5208, "Asia/Tokyo"),          # Sagan Tosu - Ekimae Real Estate Stadium
    "仙台維加泰": (38.3192, 140.8822, "Asia/Tokyo"),        # Vegalta Sendai - Yurtec Stadium Sendai
    "秋田藍閃電": (39.7178, 140.1000, "Asia/Tokyo"),        # Blaublitz Akita - Soyu Stadium
    "山形山神": (38.3347, 140.3672, "Asia/Tokyo"),          # Montedio Yamagata - ND Soft Stadium Yamagata
    "福島聯": (37.7625, 140.3736, "Asia/Tokyo"),            # Fukushima United - Toho Stadium
    "水戶蜀葵": (36.3439, 140.3969, "Asia/Tokyo"),          # Mito Hollyhock - K's denki Stadium Mito
    "千葉市原": (35.5781, 140.1233, "Asia/Tokyo"),          # JEF United Chiba - Fukuda Denshi Arena
    "大宮松鼠": (35.8967, 139.6339, "Asia/Tokyo"),      # Omiya Ardija - NACK5 Stadium Omiya
    "大宮松鼠女足": (35.8967, 139.6339, "Asia/Tokyo"),      # Omiya Ardija - NACK5 Stadium Omiya
    "甲府風林": (35.6250, 138.6064, "Asia/Tokyo"),          # Ventforet Kofu - JIT Recycle Ink Stadium
    "山口雷法": (34.0167, 131.4667, "Asia/Tokyo"),          # Renofa Yamaguchi - Ishin Me-Life Stadium
    "德島漩渦": (34.0667, 134.6000, "Asia/Tokyo"),          # Tokushima Vortis - Pocarisweat Stadium
    "愛媛FC": (33.7667, 132.7833, "Asia/Tokyo"),            # Ehime FC - Ningineer Stadium
    "FC愛媛": (33.7667, 132.7833, "Asia/Tokyo"),            # Ehime FC - Ningineer Stadium
    "磐城FC": (37.0539, 140.8922, "Asia/Tokyo"),
    "長崎成功丸": (32.7500, 129.8667, "Asia/Tokyo"),        # V-Varen Nagasaki - Transcosmos Stadium Nagasaki
    "熊本深紅": (32.8333, 130.8000, "Asia/Tokyo"),          # Roasso Kumamoto - EGAO Kenko Stadium
    "大分三神": (33.2000, 131.6500, "Asia/Tokyo"),          # Oita Trinita - Resonac Dome Oita
    "藤枝MYFC": (34.8667, 138.2333, "Asia/Tokyo"),          # Fujieda MYFC - Fujieda Soccer Stadium
    "岩城FC": (36.9667, 140.8833, "Asia/Tokyo"),            # Iwaki FC - Hawaiians Stadium Iwaki
    "草津溫泉": (36.4167, 139.0833, "Asia/Tokyo"),          # Thespakusatsu Gunma - Shoda Shoyu Stadium Gunma
    "櫪木SC": (36.514444, 139.8575, "Asia/Tokyo"),            # Tochigi SC - Kanseki Stadium Tochigi
    "鹿兒島聯": (31.5667, 130.5500, "Asia/Tokyo"),          # Kagoshima United - Shiranami Stadium
    "富山勝利": (36.625056, 137.195688, "Asia/Tokyo"),       # Kataller Toyama - Toyama Athletic Stadium
    #日丙
    "宮崎棒牛鳥": (31.9167, 131.4167, "Asia/Tokyo"),
    "讚岐卡馬達馬尼": (34.3150, 134.0364, "Asia/Tokyo"),
    "熊本羅亞素": (32.8369, 130.8000, "Asia/Tokyo"),  # Egao Kenko Stadium
    "FC大阪": (34.6939, 135.4764, "Asia/Tokyo"),  # Hanazono Rugby Stadium
    "鹿兒島聯": (31.5667, 130.5500, "Asia/Tokyo"),  # Shiranami Stadium
    "金澤薩維根": (36.5542, 136.6567, "Asia/Tokyo"),  # Ishikawa Kanazawa Stadium
    "北九州向日葵": (33.8853, 130.8753, "Asia/Tokyo"),  # Mikuni World Stadium Kitakyushu
    "奈良俱樂部": (34.6853, 135.8328, "Asia/Tokyo"),  # Rohto Field Nara
    "鳥取飛翔": (35.4631, 133.3314, "Asia/Tokyo"),  # Axis Bird Stadium
    "SC相模原": (35.5775, 139.3708, "Asia/Tokyo"),  # Sagamihara Asamizo Park Stadium
    "FC岐阜": (35.4078, 136.7586, "Asia/Tokyo"),  # Gifu Memorial Center
    "群馬溫泉": (36.4050, 139.3300, "Asia/Tokyo"),  # Shoda Shoyu Stadium Gunma
    "松本山雅": (36.2339, 137.9667, "Asia/Tokyo"),  # Sunpro Alwin
    "FC琉球": (26.3158, 127.8225, "Asia/Tokyo"),  # Tapic Kenso Hiyagon 
    "琉球FC": (26.3158, 127.8225, "Asia/Tokyo"),  # Tapic Kenso Hiyagon Stadium
    "讚岐釜玉海": (34.3150, 134.0364, "Asia/Tokyo"),  # Pikara Stadium
    "高知聯": (33.5667, 133.6667, "Asia/Tokyo"),  # Kochi Haruno Athletic Stadium
    "AC長野拍檔": (36.1836, 138.1261, "Asia/Tokyo"),  # Nagano U Stadium
    "滋賀湖王": (35.0500, 136.0000, "Asia/Tokyo"),  # Nunobiki Green Stadium
    "櫪木城": (36.5650, 139.8833, "Asia/Tokyo"),
    "長野帕塞羅": (36.1836, 138.1261, "Asia/Tokyo"),
    "FC今治": (34.0667, 132.9833, "Asia/Tokyo"),
    "八戶雲羅里": (40.5122, 141.4886, "Asia/Tokyo"),
    # 法甲 Ligue 1 2025/26
    "paris saint-germain": (48.8414, 2.2530, "Europe/Paris"),  # Parc des Princes
    "olympique marseille": (43.2708, 5.3959, "Europe/Paris"),  # Stade Vélodrome
    "olympique lyonnais": (45.7653, 4.9820, "Europe/Paris"),  # Groupama Stadium
    "as monaco": (43.7052, 7.4159, "Europe/Paris"),  # Stade Louis II
    "lille": (50.6119, 3.1304, "Europe/Paris"),  # Stade Pierre-Mauroy
    "rc lens": (50.4328, 2.8149, "Europe/Paris"),  # Stade Bollaert-Delelis
    "nice": (43.7050, 7.1925, "Europe/Paris"),  # Allianz Riviera
    "rennes": (48.1075, -1.7128, "Europe/Paris"),  # Roazhon Park
    "brest": (48.4031, -4.4617, "Europe/Paris"),  # Stade Francis-Le Blé
    "nantes": (47.2561, -1.5242, "Europe/Paris"),  # Stade de la Beaujoire
    "strasbourg": (48.5600, 7.7550, "Europe/Paris"),  # Stade de la Meinau
    "auxerre": (47.7867, 3.5889, "Europe/Paris"),  # Stade de l'Abbé-Deschamps
    "le havre": (49.5039, 0.1678, "Europe/Paris"),  # Stade Océane
    "angers": (47.4603, -0.5311, "Europe/Paris"),  # Stade Raymond Kopa
    "toulouse": (43.5833, 1.4342, "Europe/Paris"),  # Stadium de Toulouse
    "lorient": (47.7489, -3.3689, "Europe/Paris"),  # Stade du Moustoir
    "paris fc": (48.8167, 2.4500, "Europe/Paris"),  # Stade Charléty (主場)
    "metz": (49.1100, 6.1592, "Europe/Paris"),  # Stade Saint-Symphorien
    # 法乙 Ligue 2 2025/26
    "montpellier": (43.6222, 3.8108, "Europe/Paris"),  # Stade de la Mosson
    "as saint-etienne": (45.4608, 4.3900, "Europe/Paris"),  # Stade Geoffroy-Guichard
    "stade de reims": (49.2469, 4.0250, "Europe/Paris"),  # Stade Auguste-Delaune
    "fc metz": (49.1100, 6.1592, "Europe/Paris"),  # Stade Saint-Symphorien (若重複，以最新為準)
    "guingamp": (48.5672, -3.1653, "Europe/Paris"),  # Stade de Roudourou
    "rodez af": (44.3500, 2.5667, "Europe/Paris"),  # Stade Paul-Lignon
    "caen": (49.1858, -0.3964, "Europe/Paris"),  # Stade Michel d'Ornano
    "amiens sc": (49.8900, 2.2631, "Europe/Paris"),  # Stade de la Licorne
    "pau fc": (43.3167, -0.3667, "Europe/Paris"),  # Nouste Camp
    "boulogne": (50.723742, 1.619411, "Europe/Paris"),
    "dunkerque": (51.0353, 2.3900, "Europe/Paris"),  # Stade Marcel-Tribut
    "lavallois": (48.1000, -0.7667, "Europe/Paris"),  # Stade Francis Le Basser
    "grenoble": (45.1883, 5.7167, "Europe/Paris"),  # Stade des Alpes
    "bordeaux": (44.8972, -0.5617, "Europe/Paris"),  # Matmut Atlantique (若仍在法乙)
    "annecy": (45.9167, 6.1167, "Europe/Paris"),  # Parc des Sports
    "martigues": (43.4167, 5.0500, "Europe/Paris"),  # Stade Francis Turcan
    "clermont foot": (45.8167, 3.1167, "Europe/Paris"),  # Stade Gabriel-Montpied
    "red star fc": (48.9278, 2.3611, "Europe/Paris"),  # Stade Bauer
    "bastia": (42.6500, 9.4500, "Europe/Paris"),  # Stade Armand Cesari
    "troyes": (48.3083, 4.0833, "Europe/Paris"),  # Stade de l'Aube
    "paris fc": (48.8167, 2.4500, "Europe/Paris"),  # Stade Charléty (若仍在法乙調整)
    "nimes": (43.815972, 4.359278, "Europe/Paris"),
    "克萊蒙特": (45.7772, 3.0867, "Europe/Paris"),
    "巴黎聖日耳門": (48.8414, 2.2530, "Europe/Paris"),          # Paris Saint-Germain - Parc des Princes
    "馬賽": (43.2708, 5.3959, "Europe/Paris"),                   # Olympique Marseille - Stade Vélodrome
    "里昂": (45.7653, 4.9820, "Europe/Paris"),                   # Olympique Lyonnais - Groupama Stadium
    "摩納哥": (43.7052, 7.4159, "Europe/Paris"),                 # AS Monaco - Stade Louis II
    "里爾": (50.6119, 3.1304, "Europe/Paris"),                   # Lille - Stade Pierre-Mauroy
    "朗斯": (50.4328, 2.8149, "Europe/Paris"),                   # RC Lens - Stade Bollaert-Delelis
    "尼斯": (43.7050, 7.1925, "Europe/Paris"),                   # Nice - Allianz Riviera
    "雷恩": (48.1075, -1.7128, "Europe/Paris"),                  # Rennes - Roazhon Park
    "布雷斯特": (48.4031, -4.4617, "Europe/Paris"),             # Brest - Stade Francis-Le Blé
    "南特": (47.2561, -1.5242, "Europe/Paris"),                  # Nantes - Stade de la Beaujoire
    "斯特拉斯堡": (48.5600, 7.7550, "Europe/Paris"),            # Strasbourg - Stade de la Meinau
    "歐塞爾": (47.7867, 3.5889, "Europe/Paris"),                 # Auxerre - Stade de l'Abbé-Deschamps
    "勒阿弗爾": (49.5039, 0.1678, "Europe/Paris"),               # Le Havre - Stade Océane
    "昂熱": (47.4603, -0.5311, "Europe/Paris"),                  # Angers - Stade Raymond Kopa
    "圖盧茲": (43.5833, 1.4342, "Europe/Paris"),                 # Toulouse - Stadium de Toulouse
    "洛里昂": (47.7489, -3.3689, "Europe/Paris"),                # Lorient - Stade du Moustoir
    "巴黎FC": (48.8167, 2.4500, "Europe/Paris"),                 # Paris FC - Stade Charléty
    "梅斯": (49.1100, 6.1592, "Europe/Paris"),                   # Metz - Stade Saint-Symphorien
    "FC安納西": (45.9200, 6.1667, "Europe/Paris"),
    "布羅尼": (46.2050, 5.2411, "Europe/Paris"),  # Bourg-en-Bresse 01 / Bourg-Péronnas - Stade Marcel-Verchère (Bourg-en-Bresse)
    "登卡基": (47.3333, 5.0333, "Europe/Paris"),   # Dijon FCO - Stade Gaston Gérard (Dijon)
    "比斯特": (47.3333, 5.0333, "Europe/Paris"),
    "羅德茲": (44.3528, 2.5750, "Europe/Paris"),
    # Ligue 2 (法乙)
    "拉瓦勒": (48.0733, -0.7667, "Europe/Paris"),
    "蒙彼利埃": (43.6222, 3.8108, "Europe/Paris"),               # Montpellier - Stade de la Mosson
    "聖伊天": (45.4608, 4.3900, "Europe/Paris"),                 # AS Saint-Étienne - Stade Geoffroy-Guichard
    "蘭斯": (49.2469, 4.0250, "Europe/Paris"),                   # Stade de Reims - Stade Auguste-Delaune
    "甘岡": (48.5672, -3.1653, "Europe/Paris"),                  # Guingamp - Stade de Roudourou
    "羅德斯": (44.3500, 2.5667, "Europe/Paris"),                 # Rodez AF - Stade Paul-Lignon
    "卡昂": (49.1858, -0.3964, "Europe/Paris"),                  # Caen - Stade Michel d'Ornano
    "亞眠": (49.8900, 2.2631, "Europe/Paris"),                   # Amiens SC - Stade de la Licorne
    "波城": (43.3167, -0.3667, "Europe/Paris"),                  # Pau FC - Nouste Camp
    "布洛涅": (50.723742, 1.619411, "Europe/Paris"),            # Boulogne - Stade de la Libération
    "敦刻爾克": (51.0353, 2.3900, "Europe/Paris"),              # Dunkerque - Stade Marcel-Tribut
    "拉瓦爾": (48.1000, -0.7667, "Europe/Paris"),                # Laval - Stade Francis Le Basser
    "格勒諾布爾": (45.1883, 5.7167, "Europe/Paris"),            # Grenoble - Stade des Alpes
    "波爾多": (44.8972, -0.5617, "Europe/Paris"),               # Bordeaux - Matmut Atlantique
    "安錫": (45.9167, 6.1167, "Europe/Paris"),                   # Annecy - Parc des Sports
    "馬蒂格": (43.4167, 5.0500, "Europe/Paris"),                 # Martigues - Stade Francis Turcan
    "克萊蒙": (45.8167, 3.1167, "Europe/Paris"),                 # Clermont Foot - Stade Gabriel-Montpied
    "紅星FC": (48.9278, 2.3611, "Europe/Paris"),                 # Red Star FC - Stade Bauer
    "巴斯蒂亞": (42.6500, 9.4500, "Europe/Paris"),              # Bastia - Stade Armand Cesari
    "特魯瓦": (48.3083, 4.0833, "Europe/Paris"),                 # Troyes - Stade de l'Aube
    "尼姆": (43.815972, 4.359278, "Europe/Paris"),                # Nîmes - Stade des Costières
    "南錫": (48.6889, 6.1833, "Europe/Paris"),
    "勒芒": (47.959, 0.2234, "Europe/Paris"),
    # 德甲 Bundesliga 2025/26
    "bayern munich": (48.2188, 11.6247, "Europe/Berlin"),  # Allianz Arena
    "borussia dortmund": (51.4926, 7.4518, "Europe/Berlin"),  # Signal Iduna Park
    "bayer leverkusen": (51.0381, 7.0022, "Europe/Berlin"),  # BayArena
    "rb leipzig": (51.3458, 12.3483, "Europe/Berlin"),  # Red Bull Arena
    "vfb stuttgart": (48.7923, 9.2320, "Europe/Berlin"),  # MHPArena
    "eintracht frankfurt": (50.0686, 8.6455, "Europe/Berlin"),  # Deutsche Bank Park
    "borussia monchengladbach": (51.1747, 6.3856, "Europe/Berlin"),  # Borussia-Park
    "wolfsburg": (52.4336, 10.8042, "Europe/Berlin"),  # Volkswagen Arena
    "union berlin": (52.4572, 13.5431, "Europe/Berlin"),  # Stadion An der Alten Försterei
    "freiburg": (48.0219, 7.8931, "Europe/Berlin"),  # Europa-Park Stadion
    "augsburg": (48.3231, 10.8858, "Europe/Berlin"),  # WWK Arena
    "hoffenheim": (49.2367, 8.8400, "Europe/Berlin"),  # PreZero Arena
    "werder bremen": (53.0664, 8.8375, "Europe/Berlin"),  # Weserstadion
    "mainz 05": (49.9842, 8.2236, "Europe/Berlin"),  # Mewa Arena
    "fc heidenheim": (48.6694, 10.1372, "Europe/Berlin"),  # Voith-Arena
    "fc st pauli": (53.5547, 9.9675, "Europe/Berlin"),  # Millerntor-Stadion
    "hamburger sv": (53.5872, 9.8986, "Europe/Berlin"),  # Volksparkstadion
    "1 fc koln": (50.9335, 6.8750, "Europe/Berlin"),  # RheinEnergieStadion
    # 德乙 2. Bundesliga 2025/26 (主要)
    "hertha bsc": (52.5147, 13.2397, "Europe/Berlin"),  # Olympiastadion Berlin
    "schalke 04": (51.5547, 7.0678, "Europe/Berlin"),  # Veltins-Arena
    "1 fc kaiserslautern": (49.4347, 7.7778, "Europe/Berlin"),  # Fritz-Walter-Stadion
    "fortuna dusseldorf": (51.2617, 6.7347, "Europe/Berlin"),  # Merkur Spiel-Arena
    "sc paderborn 07": (51.7311, 8.7089, "Europe/Berlin"),  # Home Deluxe Arena
    "karlsruher sc": (49.0200, 8.4131, "Europe/Berlin"),  # BBBank Wildpark
    "hannover 96": (52.3600, 9.7311, "Europe/Berlin"),  # Heinz von Heiden Arena
    "1 fc magdeburg": (52.1256, 11.6711, "Europe/Berlin"),  # MDCC-Arena
    "sv elversberg": (49.3167, 7.1667, "Europe/Berlin"),  # Waldstadion Kaiserlinde
    "1 fc nurnberg": (49.4264, 11.1256, "Europe/Berlin"),  # Max-Morlock-Stadion
    "eintracht braunschweig": (52.2900, 10.5217, "Europe/Berlin"),  # Eintracht-Stadion
    "holstein kiel": (54.3486, 10.1236, "Europe/Berlin"),  # Holstein-Stadion
    "vfl bochum": (51.4900, 7.2367, "Europe/Berlin"),  # Vonovia Ruhrstadion
    "hansa rostock": (54.0853, 12.0939, "Europe/Berlin"),  # Ostseestadion
    "greuther furth": (49.4869, 10.9986, "Europe/Berlin"),  # Sportpark Ronhof
    "sv darmstadt 98": (49.8578, 8.6722, "Europe/Berlin"),  # Merck-Stadion am Böllenfalltor
    "preussen munster": (51.9306, 7.6244, "Europe/Berlin"),  # Preußenstadion
    "1 fc saarbrucken": (49.2489, 7.0022, "Europe/Berlin"),  # Ludwigsparkstadion
    "tsv 1860 munich":(48.110833, 11.574444,"Europe/Berlin"),
    #德甲
    "拜仁慕尼黑": (48.2188, 11.6247, "Europe/Berlin"),          # Bayern Munich - Allianz Arena
    "多蒙特": (51.4926, 7.4518, "Europe/Berlin"),                # Borussia Dortmund - Signal Iduna Park
    "利華古遜": (51.0381, 7.0022, "Europe/Berlin"),              # Bayer Leverkusen - BayArena
    "RB萊比錫": (51.3458, 12.3483, "Europe/Berlin"),             # RB Leipzig - Red Bull Arena
    "史特加": (48.7923, 9.2320, "Europe/Berlin"),                # VfB Stuttgart - MHPArena
    "法蘭克福": (50.0686, 8.6455, "Europe/Berlin"),              # Eintracht Frankfurt - Deutsche Bank Park
    "慕遜加柏": (51.1747, 6.3856, "Europe/Berlin"),              # Borussia Mönchengladbach - Borussia-Park
    "禾夫斯堡": (52.4336, 10.8042, "Europe/Berlin"),             # Wolfsburg - Volkswagen Arena
    "柏林聯": (52.4572, 13.5431, "Europe/Berlin"),               # Union Berlin - Stadion An der Alten Försterei
    "弗賴堡": (48.0219, 7.8931, "Europe/Berlin"),                # Freiburg - Europa-Park Stadion
    "奧格斯堡": (48.3231, 10.8858, "Europe/Berlin"),             # Augsburg - WWK Arena
    "賀芬咸": (49.2367, 8.8400, "Europe/Berlin"),                # Hoffenheim - PreZero Arena
    "雲達不萊梅": (53.0664, 8.8375, "Europe/Berlin"),            # Werder Bremen - Weserstadion
    "緬恩斯": (49.9842, 8.2236, "Europe/Berlin"),                # Mainz 05 - Mewa Arena
    "海登咸": (48.6694, 10.1372, "Europe/Berlin"),               # FC Heidenheim - Voith-Arena
    "聖保利": (53.5547, 9.9675, "Europe/Berlin"),                # FC St. Pauli - Millerntor-Stadion
    "漢堡": (53.5872, 9.8986, "Europe/Berlin"),                  # Hamburger SV - Volksparkstadion
    "雷根斯堡": (49.0134, 12.1016, "Europe/Berlin"),
    # 德乙 2. Bundesliga 2025/26
    "哈化柏林": (52.5147, 13.2397, "Europe/Berlin"),             # Hertha BSC - Olympiastadion Berlin
    "史浩克04": (51.5547, 7.0678, "Europe/Berlin"),              # Schalke 04 - Veltins-Arena
    "凱沙勞頓": (49.4347, 7.7778, "Europe/Berlin"),              # 1. FC Kaiserslautern - Fritz-Walter-Stadion
    "杜塞爾多夫": (51.2617, 6.7347, "Europe/Berlin"),           # Fortuna Düsseldorf - Merkur Spiel-Arena
    "柏達邦": (51.7311, 8.7089, "Europe/Berlin"),                # SC Paderborn 07 - Home Deluxe Arena
    "卡爾斯魯厄": (49.0200, 8.4131, "Europe/Berlin"),            # Karlsruher SC - BBBank Wildpark
    "漢諾威96": (52.3600, 9.7311, "Europe/Berlin"),              # Hannover 96 - Heinz von Heiden Arena
    "馬格德堡": (52.1256, 11.6711, "Europe/Berlin"),             # 1. FC Magdeburg - MDCC-Arena
    "艾華斯堡": (49.3167, 7.1667, "Europe/Berlin"),              # SV Elversberg - Waldstadion Kaiserlinde
    "紐倫堡": (49.4264, 11.1256, "Europe/Berlin"),               # 1. FC Nürnberg - Max-Morlock-Stadion
    "布倫瑞克": (52.2900, 10.5217, "Europe/Berlin"),             # Eintracht Braunschweig - Eintracht-Stadion
    "基爾": (54.3486, 10.1236, "Europe/Berlin"),                 # Holstein Kiel - Holstein-Stadion
    "波琴": (51.4900, 7.2367, "Europe/Berlin"),                  # VfL Bochum - Vonovia Ruhrstadion
    "羅斯托克": (54.0853, 12.0939, "Europe/Berlin"),             # Hansa Rostock - Ostseestadion
    "格雷特霍夫": (49.4869, 10.9986, "Europe/Berlin"),               # Greuther Fürth - Sportpark Ronhof
    "達姆施塔特": (49.8578, 8.6722, "Europe/Berlin"),            # SV Darmstadt 98 - Merck-Stadion am Böllenfalltor
    "普魯士明斯特": (51.9306, 7.6244, "Europe/Berlin"),          # Preußen Münster - Preußenstadion
    "薩爾布呂肯": (49.2489, 7.0022, "Europe/Berlin"),            # 1. FC Saarbrücken - Ludwigsparkstadion
    "慕尼黑1860": (48.110833, 11.574444, "Europe/Berlin"),        # TSV 1860 Munich - Grünwalder Stadion
    #厄瓜多爾聯賽
    "基多利加大學": (-0.1803, -78.4678, "America/Guayaquil"),  # LDU Quito - Estadio Rodrigo Paz Delgado (Casa Blanca, Quito)
    "獨立谷": (-0.1833, -78.4833, "America/Guayaquil"),  # Independiente del Valle - Estadio Banco Guayaquil (Sangolquí)
    "SC巴斯隆拿": (-2.1833, -79.8833, "America/Guayaquil"),  # Barcelona SC - Estadio Monumental Banco Pichincha (Guayaquil)
    "艾梅卡斯": (-2.1833, -79.8833, "America/Guayaquil"),  # Emelec - Estadio George Capwell (Guayaquil)
    "奧爾梅多": (-1.4000, -78.7833, "America/Guayaquil"),  # C.D. Olmedo - Estadio Olímpico Ciudad de Riobamba (Riobamba)
    "德爾芬": (-1.0333, -79.4667, "America/Guayaquil"),  # Delfín S.C. - Estadio Jocay (Manta)
    "奧卡斯": (-2.1833, -79.8833, "America/Guayaquil"),  # Delfín S.C. - Estadio Jocay (Manta, shared)
    "馬卡拉": (-0.9667, -80.7167, "America/Guayaquil"),  # Macará - Estadio Bellavista (Ambato)
    "德波帝沃庫恩卡": (-2.9000, -79.0000, "America/Guayaquil"),  # Deportivo Cuenca - Estadio Alejandro Serrano Aguilar (Cuenca)
    "穆薩克魯斯": (-2.1833, -79.8833, "America/Guayaquil"),  # Mushuc Runa - COAC Mushuc Runa Stadium (Ambato)

    #俄甲
    "莫斯科火車頭": (55.7894, 37.5872, "Europe/Moscow"),
    "莫斯科斯巴達": (55.8178, 37.4408, "Europe/Moscow"),
    "莫斯科斯巴達克-2": (55.8178, 37.4408, "Europe/Moscow"),  # Spartak Moscow-2 - Spartak Academy (Moscow)
    "莫斯科迪納摩-2": (55.7911, 37.5875, "Europe/Moscow"),  # Dynamo Moscow-2 - Dynamo Stadium (Moscow)
    "葉尼塞": (56.0108, 92.8522, "Europe/Moscow"),  # FC Yenisey Krasnoyarsk - Central Stadium (Krasnoyarsk)
    "阿克隆托利亞蒂": (53.5167, 49.4167, "Europe/Moscow"),  # Akron Tolyatti - Akron Arena (Tolyatti)
    "羅托爾伏爾加格勒": (48.7344, 44.5486, "Europe/Moscow"),  # Rotor Volgograd - Central Stadium (Volgograd)
    "阿爾塞納爾圖拉": (54.1833, 37.6167, "Europe/Moscow"),  # Arsenal Tula - Arsenal Stadium (Tula)
    "索契": (43.5858, 39.7233, "Europe/Moscow"),  # FC Sochi - Fisht Olympic Stadium (Sochi)
    "卡馬斯納別列奇尼": (55.8333, 52.0667, "Europe/Moscow"),  # Kamaz Naberezhnye Chelny - Kamaz Stadium (Naberezhnye Chelny)
    "沙姆盧克別爾江": (54.7333, 55.9667, "Europe/Moscow"),  # Shinnik Yaroslavl - Shinnik Stadium (Yaroslavl)
    "涅夫特赫尼克下卡姆斯克": (55.6333, 51.8167, "Europe/Moscow"),  # Neftekhimik Nizhnekamsk - Neftekhimik Stadium (Nizhnekamsk)
    "烏法": (54.7333, 55.9667, "Europe/Moscow"),  # FC Ufa - Neftyanik Stadium (Ufa)
    "阿蘭尼亞弗拉基高加索": (43.0167, 44.6833, "Europe/Moscow"),  # Alania Vladikavkaz - Spartak Stadium (Vladikavkaz)
    "托爾佩多莫斯科": (55.7667, 37.6500, "Europe/Moscow"),  # Torpedo Moscow - Eduard Streltsov Stadium (Moscow)
    "斯卡羅斯托夫": (55.7558, 37.6173, "Europe/Moscow"),  # SKA-Khabarovsk - Lenin Stadium (Khabarovsk)
    "秋明": (57.1522, 65.5272, "Europe/Yekaterinburg"),  # FC Tyumen - Geolog Stadium (Tyumen)
    "切爾特科沃": (50.6000, 36.6000, "Europe/Moscow"),  # Chernomorets Novorossiysk - Central Stadium (Novorossiysk)
    "羅迪納莫斯科": (55.7667, 37.6500, "Europe/Moscow"),  # Rodina Moscow - Sapsan Arena (Moscow)
    "托爾佩多弗拉基米爾": (56.1333, 40.4167, "Europe/Moscow"),  # Torpedo Vladimir - Torpedo Stadium (Vladimir)
    "森馬拉": (47.2225, 39.7203, "Europe/Moscow"),
    "魯賓卡山": (55.7894, 37.5872, "Europe/Moscow"),
    # 韓職 K League 1 2025
    "ulsan hd": (35.5354, 129.3489, "Asia/Seoul"),  # Ulsan Munsu Football Stadium
    "pohang steelers": (36.0089, 129.3847, "Asia/Seoul"),  # Pohang Steel Yard
    "gimcheon sangmu": (36.1433, 128.0889, "Asia/Seoul"),  # Gimcheon Stadium
    "gangwon fc": (37.8800, 127.7300, "Asia/Seoul"),  # Chuncheon Songam Sports Town / Gangneung Stadium
    "fc seoul": (37.5683, 126.8972, "Asia/Seoul"),  # Seoul World Cup Stadium
    "jeonbuk hyundai motors": (35.8683, 127.0644, "Asia/Seoul"),  # Jeonju World Cup Stadium
    "daegu fc": (35.8814, 128.5883, "Asia/Seoul"),  # DGB Daegu Bank Park
    "daejeon hana citizen": (36.3650, 127.3250, "Asia/Seoul"),  # Daejeon World Cup Stadium
    "gwangju fc": (35.1333, 126.8750, "Asia/Seoul"),  # Gwangju Football Stadium
    "jeju united": (33.2461, 126.5094, "Asia/Seoul"),  # Jeju World Cup Stadium
    "suwon fc": (37.2858, 127.0389, "Asia/Seoul"),  # Suwon Sports Complex / Suwon Stadium
    "fc anyang": (37.4028, 126.9472, "Asia/Seoul"),  # Anyang Stadium (新升級球隊)
    # 韓職二級 K League 2 2025
    "incheon united": (37.4650, 126.6431, "Asia/Seoul"),  # Incheon Football Stadium (降級新軍)
    "hwaseong fc": (37.1400, 126.9400, "Asia/Seoul"),  # Hwaseong Stadium (新升級球隊)
    "suwon samsung bluewings": (37.2858, 127.0389, "Asia/Seoul"),  # Suwon World Cup Stadium
    "seongnam fc": (37.4100, 127.1283, "Asia/Seoul"),  # Tancheon Stadium
    "bucheon fc 1995": (37.4983, 126.7928, "Asia/Seoul"),  # Bucheon Stadium
    "seoul e-land fc": (37.5197, 126.8889, "Asia/Seoul"),  # Mokdong Stadium
    "busan ipark": (35.1900, 129.0600, "Asia/Seoul"),  # Busan Asiad Main Stadium
    "jeonnam dragons": (34.8500, 127.1333, "Asia/Seoul"),  # Gwangyang Football Stadium
    "chungnam asan fc": (36.8167, 127.0833, "Asia/Seoul"),  # Yi Sun-sin Stadium
    "gyeongnam fc": (35.1833, 128.7000, "Asia/Seoul"),  # Changwon Football Center
    "ansan greeners fc": (37.3189, 126.8347, "Asia/Seoul"),  # Ansan Wa~ Stadium
    "chungbuk cheongju fc": (36.6500, 127.4833, "Asia/Seoul"),  # Cheongju Stadium
    "gimpo fc": (37.6200, 126.7200, "Asia/Seoul"),  # Gimpo Solteo Stadium
    "cheonan city fc": (36.8189, 127.1500, "Asia/Seoul"),  # Cheonan Stadium
    # 韓職 K League 1 2025
    "蔚山現代": (35.5354, 129.3489, "Asia/Seoul"),              # Ulsan HD - Ulsan Munsu Football Stadium
    "浦項制鐵": (36.0089, 129.3847, "Asia/Seoul"),              # Pohang Steelers - Pohang Steel Yard
    "金泉尚武": (36.1433, 128.0889, "Asia/Seoul"),              # Gimcheon Sangmu - Gimcheon Stadium
    "江原FC": (37.8800, 127.7300, "Asia/Seoul"),                # Gangwon FC - Chuncheon Songam Sports Town / Gangneung Stadium
    "首爾FC": (37.5683, 126.8972, "Asia/Seoul"),                # FC Seoul - Seoul World Cup Stadium
    "FC首爾": (37.5683, 126.8972, "Asia/Seoul"),                # FC Seoul - Seoul World Cup Stadium
    "全北汽車": (35.8683, 127.0644, "Asia/Seoul"),          # Jeonbuk Hyundai Motors - Jeonju World Cup Stadium
    "大邱FC": (35.8814, 128.5883, "Asia/Seoul"),                # Daegu FC - DGB Daegu Bank Park
    "大田市民": (36.3650, 127.3250, "Asia/Seoul"),              # Daejeon Hana Citizen - Daejeon World Cup Stadium
    "光州FC": (35.1333, 126.8750, "Asia/Seoul"),                # Gwangju FC - Gwangju Football Stadium
    "濟州聯": (33.2461, 126.5094, "Asia/Seoul"),                # Jeju United - Jeju World Cup Stadium
    "水原FC": (37.2858, 127.0389, "Asia/Seoul"),                # Suwon FC - Suwon Sports Complex / Suwon Stadium
    "安養FC": (37.4028, 126.9472, "Asia/Seoul"),                # FC Anyang - Anyang Stadium (新升級球隊)
    "FC安養": (37.4028, 126.9472, "Asia/Seoul"),                # FC Anyang - Anyang Stadium (新升級球隊)
    # 韓職二級 K League 2 2025
    "仁川聯": (37.4650, 126.6431, "Asia/Seoul"),              # Incheon United - Incheon Football Stadium (降級新軍)
    "華城FC": (37.1400, 126.9400, "Asia/Seoul"),                # Hwaseong FC - Hwaseong Stadium (新升級球隊)
    "水原三星": (37.2858, 127.0389, "Asia/Seoul"),          # Suwon Samsung Bluewings - Suwon World Cup Stadium
    "城南FC": (37.4100, 127.1283, "Asia/Seoul"),                # Seongnam FC - Tancheon Stadium
    "富川FC": (37.4983, 126.7928, "Asia/Seoul"),           # Bucheon FC 1995 - Bucheon Stadium
    "首爾E-Land": (37.5197, 126.8889, "Asia/Seoul"),            # Seoul E-Land FC - Mokdong Stadium
    "釜山偶像": (35.1900, 129.0600, "Asia/Seoul"),              # Busan IPark - Busan Asiad Main Stadium
    "全南天龍": (34.8500, 127.1333, "Asia/Seoul"),              # Jeonnam Dragons - Gwangyang Football Stadium
    "忠南牙山": (36.8167, 127.0833, "Asia/Seoul"),              # Chungnam Asan FC - Yi Sun-sin Stadium
    "慶南FC": (35.1833, 128.7000, "Asia/Seoul"),                # Gyeongnam FC - Changwon Football Center
    "安山綠人": (37.3189, 126.8347, "Asia/Seoul"),              # Ansan Greeners FC - Ansan Wa~ Stadium
    "清州FC": (36.6500, 127.4833, "Asia/Seoul"),                # Chungbuk Cheongju FC - Cheongju Stadium
    "金浦FC": (37.6200, 126.7200, "Asia/Seoul"),                # Gimpo FC - Gimpo Solteo Stadium
    "天安市民": (36.8189, 127.1500, "Asia/Seoul"),               # Cheonan City FC - Cheonan Stadium
    "坡州前線": (37.8667, 126.7833, "Asia/Seoul"),
    "FC華城": (37.1997, 127.0950, "Asia/Seoul"),
    #韓職三級 K League 3
    "龍仁FC": (37.2414, 127.1786, "Asia/Seoul"),
    "金海市廳": (35.2583, 128.8786, "Asia/Seoul"),          # Gimhae City FC - Gimhae Stadium
    "昌原市廳": (35.2708, 128.6633, "Asia/Seoul"),          # Changwon FC - Changwon Football Center
    "蔚山公民": (35.5700, 129.3500, "Asia/Seoul"),          # Ulsan Citizen FC - Ulsan Stadium
    "春川市民": (37.8667, 127.7333, "Asia/Seoul"),          # Chuncheon Citizen FC - Chuncheon Songam Sports Town
    "大邱FC二隊": (35.8400, 128.4800, "Asia/Seoul"),        # Daegu FC II - DGB Daegu Bank Park (training/reserve)
    "安養市民": (37.4000, 126.9500, "Asia/Seoul"),          # Anyang Citizen FC - Anyang Sports Complex
    "抱川市民": (38.0667, 127.0667, "Asia/Seoul"),          # Pocheon Citizen FC - Pocheon Stadium
    "陽州市民": (37.8333, 127.1833, "Asia/Seoul"),          # Yangju Citizen FC - Yangju Stadium
    "牙山木槿": (36.7833, 127.0000, "Asia/Seoul"),          # Asan Mugunghwa FC - Yishunsin Stadium (Asan)
    "慶州韓水": (35.8333, 129.2167, "Asia/Seoul"),          # Gyeongju HNP - Gyeongju Citizen Stadium
    "江陵市民": (37.7500, 128.9000, "Asia/Seoul"),          # Gangneung Citizen FC - Gangneung Stadium
    "忠北清州FC": (36.6333, 127.4833, "Asia/Seoul"),        # Chungbuk Cheongju FC - Cheongju Stadium
    "富川1995": (37.4833, 126.7833, "Asia/Seoul"),          # Bucheon 1995 - Bucheon Stadium
    "水原FC二隊": (37.2667, 127.0333, "Asia/Seoul"),        # Suwon FC II - Suwon Sports Complex
    "天安城": (36.8150, 127.1167, "Asia/Seoul"),           # Cheonan City FC - Cheonan Baekseok Stadium
    # 美職聯 MLS 2025 (30隊)
    "atlanta united": (33.7554, -84.4012, "America/New_York"),  # Mercedes-Benz Stadium
    "austin fc": (30.3875, -97.7181, "America/Chicago"),  # Q2 Stadium
    "charlotte fc": (35.2258, -80.8528, "America/New_York"),  # Bank of America Stadium
    "chicago fire": (41.8623, -87.6167, "America/Chicago"),  # Soldier Field
    "fc cincinnati": (39.1114, -84.5222, "America/New_York"),  # TQL Stadium
    "columbus crew": (39.9692, -83.0111, "America/New_York"),  # Lower.com Field
    "dc united": (38.8681, -77.0114, "America/New_York"),  # Audi Field
    "fc dallas": (33.1544, -96.8353, "America/Chicago"),  # Toyota Stadium
    "houston dynamo": (29.7522, -95.3522, "America/Chicago"),  # Shell Energy Stadium
    "sporting kansas city": (39.1217, -94.8233, "America/Chicago"),  # Children's Mercy Park
    "la galaxy": (33.8643, -118.2611, "America/Los_Angeles"),  # Dignity Health Sports Park
    "lafc": (34.0128, -118.2855, "America/Los_Angeles"),  # BMO Stadium
    "inter miami": (26.1929, -80.1611, "America/New_York"),  # Chase Stadium
    "minnesota united": (44.9528, -93.1650, "America/Chicago"),  # Allianz Field
    "cf montreal": (45.5631, -73.5522, "America/Toronto"),  # Saputo Stadium
    "nashville sc": (36.1300, -86.7656, "America/Chicago"),  # GEODIS Park
    "new england revolution": (42.0909, -71.2643, "America/New_York"),  # Gillette Stadium
    "new york city fc": (40.8296, -73.9262, "America/New_York"),  # Yankee Stadium (臨時)
    "new york red bulls": (40.7367, -74.1503, "America/New_York"),  # Red Bull Arena
    "orlando city": (28.5411, -81.3892, "America/New_York"),  # Exploria Stadium
    "philadelphia union": (39.8322, -75.3789, "America/New_York"),  # Subaru Park
    "portland timbers": (45.5217, -122.5986, "America/Los_Angeles"),  # Providence Park
    "real salt lake": (40.5828, -111.8933, "America/Denver"),  # America First Field
    "san diego fc": (32.7831, -117.1195, "America/Los_Angeles"),  # Snapdragon Stadium
    "san jose earthquakes": (37.3514, -121.9250, "America/Los_Angeles"),  # PayPal Park
    "seattle sounders": (47.5952, -122.3316, "America/Los_Angeles"),  # Lumen Field
    "st louis city sc": (38.6314, -90.2106, "America/Chicago"),  # CITYPARK
    "toronto fc": (43.6328, -79.4186, "America/Toronto"),  # BMO Field
    "vancouver whitecaps": (49.2767, -123.1119, "America/Vancouver"),  # BC Place
    # 美職聯 MLS 2025 (30隊)
    "亞特蘭大聯": (33.7554, -84.4012, "America/New_York"),          # Atlanta United - Mercedes-Benz Stadium
    "奧斯汀FC": (30.3875, -97.7181, "America/Chicago"),              # Austin FC - Q2 Stadium
    "FC奧斯汀": (30.3875, -97.7181, "America/Chicago"),              # Austin FC - Q2 Stadium
    "夏洛特FC": (35.2258, -80.8528, "America/New_York"),             # Charlotte FC - Bank of America Stadium
    "芝加哥火焰": (41.8623, -87.6167, "America/Chicago"),            # Chicago Fire - Soldier Field
    "辛辛那提FC": (39.1114, -84.5222, "America/New_York"),           # FC Cincinnati - TQL Stadium
    "FC辛辛那提": (39.1114, -84.5222, "America/New_York"),           # FC Cincinnati - TQL Stadium
    "哥倫布機員": (39.9692, -83.0111, "America/New_York"),           # Columbus Crew - Lower.com Field
    "華盛頓聯隊": (38.8681, -77.0114, "America/New_York"),         # DC United - Audi Field
    "達拉斯FC": (33.1544, -96.8353, "America/Chicago"),              # FC Dallas - Toyota Stadium
    "侯斯頓戴拿模": (29.7522, -95.3522, "America/Chicago"),          # Houston Dynamo - Shell Energy Stadium
    "堪薩斯城體育會": (39.1217, -94.8233, "America/Chicago"),       # Sporting Kansas City - Children's Mercy Park
    "洛杉磯銀河": (33.8643, -118.2611, "America/Los_Angeles"),       # LA Galaxy - Dignity Health Sports Park
    "洛杉磯FC": (34.0128, -118.2855, "America/Los_Angeles"),         # LAFC - BMO Stadium
    "國際邁阿密": (26.1929, -80.1611, "America/New_York"),           # Inter Miami - Chase Stadium
    "明尼蘇達聯": (44.9528, -93.1650, "America/Chicago"),            # Minnesota United - Allianz Field
    "蒙特利爾衝擊": (45.5631, -73.5522, "America/Toronto"),          # CF Montréal - Saputo Stadium
    "納什維爾SC": (36.1300, -86.7656, "America/Chicago"),            # Nashville SC - GEODIS Park
    "新英格蘭革命": (42.0909, -71.2643, "America/New_York"),         # New England Revolution - Gillette Stadium
    "紐約城": (40.8296, -73.9262, "America/New_York"),             # New York City FC - Yankee Stadium (臨時)
    "紐約紅牛": (40.7367, -74.1503, "America/New_York"),             # New York Red Bulls - Red Bull Arena
    "奧蘭多城": (28.5411, -81.3892, "America/New_York"),             # Orlando City - Exploria Stadium
    "費城聯": (39.8322, -75.3789, "America/New_York"),             # Philadelphia Union - Subaru Park
    "波特蘭伐木者": (45.5217, -122.5986, "America/Los_Angeles"),       # Portland Timbers - Providence Park
    "皇家鹽湖城": (40.5829, -111.8934, "America/Denver"),            # Real Salt Lake - America First Field
    "聖地牙哥FC": (32.7831, -117.1195, "America/Los_Angeles"),       # San Diego FC - Snapdragon Stadium
    "聖地亞哥FC": (32.7833, -117.1167, "America/Los_Angeles"),
    "聖荷西地震": (37.3514, -121.9250, "America/Los_Angeles"),       # San Jose Earthquakes - PayPal Park
    "西雅圖海灣人": (47.5952, -122.3316, "America/Los_Angeles"),     # Seattle Sounders - Lumen Field
    "聖路易斯城SC": (38.6314, -90.2106, "America/Chicago"),          # St. Louis City SC - CITYPARK
    "多倫多FC": (43.6328, -79.4186, "America/Toronto"),              # Toronto FC - BMO Field
    "溫哥華白帽": (49.2767, -123.1119, "America/Vancouver"),          # Vancouver Whitecaps - BC Place
    "科羅拉多急流": (39.8056, -104.8919, "America/Denver"),
    #美國冠軍聯賽
    "伯明翰軍團": (33.5207, -86.8095, "America/Chicago"),  # Birmingham Legion FC - Protective Stadium (Birmingham, Alabama)
    "布魯克林FC": (40.6525, -73.9497, "America/New_York"),  # Brooklyn FC - MCU Park (Brooklyn, New York)
    "查爾斯頓炮台": (32.7904, -79.9370, "America/New_York"),  # Charleston Battery - Patriots Point Soccer Complex (Mount Pleasant, South Carolina)
    "科羅拉多泉坡路": (38.8333, -104.8333, "America/Denver"),  # Colorado Springs Switchbacks FC - Weidner Field (Colorado Springs, Colorado)
    "底特律城": (42.3390, -83.0490, "America/Detroit"),  # Detroit City FC - Keyworth Stadium (Hamtramck, Michigan)
    "艾爾帕索火車頭": (31.7613, -106.4850, "America/Denver"),  # El Paso Locomotive FC - Southwest University Park (El Paso, Texas)
    "FC塔爾薩": (36.1314, -95.9928, "America/Chicago"),
    "哈特福體育": (41.7637, -72.6740, "America/New_York"),  # Hartford Athletic - Trinity Health Stadium (Hartford, Connecticut)
    "印第安納十一": (39.7600, -86.1633, "America/Indiana/Indianapolis"),  # Indy Eleven - Carroll Stadium (Indianapolis, Indiana)
    "拉斯維加斯燈火": (36.0908, -115.1839, "America/Los_Angeles"),  # Las Vegas Lights FC - Cashman Field (Las Vegas, Nevada)
    "列星頓FC": (38.0406, -84.5037, "America/New_York"),
    "勞頓聯": (39.0989, -77.5072, "America/New_York"),
    "路易斯維爾城": (38.2025, -85.7586, "America/New_York"),
    "邁阿密FC": (25.9583, -80.2389, "America/New_York"),  # Miami FC - FIU Stadium (Miami, Florida)
    "蒙特雷灣": (36.6000, -121.8947, "America/Los_Angeles"),
    "新墨西哥聯": (35.0833, -106.6500, "America/Denver"),  # New Mexico United - Rio Grande Credit Union Field at Isotopes Park (Albuquerque, New Mexico)
    "奧克蘭根源": (37.7833, -122.2000, "America/Los_Angeles"),  # Oakland Roots SC - Laney College Football Field (Oakland, California)
    "SC奧蘭治郡": (33.6922, -117.8231, "America/Los_Angeles"),
    "鳳凰城復活": (33.4500, -112.0667, "America/Phoenix"),  # Phoenix Rising FC - Phoenix Rising Soccer Stadium (Phoenix, Arizona)
    "匹茲堡獵犬": (40.4469, -80.0058, "America/New_York"),  # Pittsburgh Riverhounds SC - Highmark Stadium (Pittsburgh, Pennsylvania)
    "羅德島FC": (41.7333, -71.4333, "America/New_York"),  # Rhode Island FC - Beirne Stadium (Smithfield, Rhode Island)
    "薩克拉門托共和": (38.5800, -121.5000, "America/Los_Angeles"),  # Sacramento Republic FC - Heart Health Park (Sacramento, California)
    "FC聖安東尼奧": (29.4167, -98.5000, "America/Chicago"),  # San Antonio FC - Toyota Field (San Antonio, Texas)
    "傑克遜維爾體育會": (30.3239, -81.6375, "America/New_York"),
    "譚伯灣暴徒": (27.9500, -82.4667, "America/New_York"),
    
    # 墨西哥職業聯賽 Liga MX 2025/26
    "club america": (19.3833, -99.1786, "America/Mexico_City"),  # 暫用 Estadio Ciudad de los Deportes (Azteca 翻新中)
    "cruz azul": (19.3031, -99.1506, "America/Mexico_City"),  # Estadio Azteca (或暫用其他)
    "chivas guadalajara": (20.6814, -103.4628, "America/Mexico_City"),  # Estadio Akron
    "tigres uanl": (25.7225, -100.3117, "America/Mexico_City"),  # Estadio Universitario
    "cf monterrey": (25.6692, -100.2446, "America/Mexico_City"),  # Estadio BBVA
    "pumas unam": (19.3328, -99.1919, "America/Mexico_City"),  # Estadio Olímpico Universitario
    "deportivo toluca": (19.2883, -99.6669, "America/Mexico_City"),  # Estadio Nemesio Díez
    "pachuca": (20.1050, -98.7561, "America/Mexico_City"),  # Estadio Hidalgo
    "santos laguna": (25.6458, -103.3814, "America/Mexico_City"),  # Estadio Corona
    "leon": (21.1158, -101.6581, "America/Mexico_City"),  # Estadio León
    "atlas": (20.6636, -103.3278, "America/Mexico_City"),  # Estadio Jalisco
    "queretaro": (20.5772, -100.3653, "America/Mexico_City"),  # Estadio Corregidora
    "puebla": (19.0783, -98.1650, "America/Mexico_City"),  # Estadio Cuauhtémoc
    "mazatlan": (23.2583, -106.3958, "America/Mexico_City"),  # Estadio Mazatlán
    "juarez": (31.7528, -106.4422, "America/Mexico_City"),  # Estadio Olímpico Benito Juárez
    "tijuana": (32.5061, -116.9931, "America/Mexico_City"),  # Estadio Caliente
    "necaxa": (21.8822, -102.2850, "America/Mexico_City"),  # Estadio Victoria
    "atletico san luis": (22.1389, -100.9608, "America/Mexico_City"),  # Estadio Alfonso Lastras
    # 墨西哥擴張聯賽 Liga de Expansión MX 2025/26
    "alebrijes de oaxaca": (17.0900, -96.7167, "America/Mexico_City"),  # Estadio Tecnológico de Oaxaca
    "atlante": (18.9333, -99.2333, "America/Mexico_City"),  # Estadio Agustín Coruco Díaz (Zacatepec)
    "atletico morelia": (19.7203, -101.1917, "America/Mexico_City"),  # Estadio Morelos
    "atletico la paz": (24.1422, -110.3167, "America/Mexico_City"),  # Estadio Guaycura
    "cancun fc": (21.1500, -86.8500, "America/Mexico_City"),  # Estadio Andrés Quintana Roo
    "correcaminos uat": (23.7333, -99.1500, "America/Mexico_City"),  # Estadio Marte R. Gómez
    "dorados de sinaloa": (32.5061, -116.9931, "America/Mexico_City"),  # Estadio Caliente (暫用，Tijuana)
    "jaiba brava": (22.2667, -97.8667, "America/Mexico_City"),  # Estadio Tamaulipas (Tampico Madero)
    "leones negros udeg": (20.6667, -103.3500, "America/Mexico_City"),  # Estadio Jalisco
    "mineros de zacatecas": (22.7667, -102.5833, "America/Mexico_City"),  # Estadio Carlos Vega Villalba
    "tampico madero": (22.2667, -97.8667, "America/Mexico_City"),  # Estadio Tamaulipas (同Jaiba Brava)
    "tapatio": (20.6667, -103.3500, "America/Mexico_City"),  # Estadio Akron (或訓練場，共享Chivas)
    "tepatitlan": (20.8167, -102.7667, "America/Mexico_City"),  # Estadio Gregorio "Tepa" Gómez
    "tlaxcala fc": (19.3167, -98.2333, "America/Mexico_City"),  # Estadio Tlahuicole
    "venados fc": (20.9333, -89.6000, "America/Mexico_City"),  # Estadio Carlos Iturralde
    
    # 墨西哥職業聯賽 Liga MX 2025/26
    "CF阿美利加": (19.3833, -99.1786, "America/Mexico_City"),          # Club América - Estadio Ciudad de los Deportes (Azteca 翻新中)
    "藍十字": (19.3031, -99.1506, "America/Mexico_City"),         # Cruz Azul - Estadio Azteca (或暫用其他)
    "瓜達拉哈拉": (20.6814, -103.4628, "America/Mexico_City"),        # Chivas Guadalajara - Estadio Akron
    "瓜達拉哈拉女足": (20.6814, -103.4628, "America/Mexico_City"),        # Chivas Guadalajara - Estadio Akron
    "堤格雷斯": (25.7225, -100.3117, "America/Mexico_City"),          # Tigres UANL - Estadio Universitario
    "蒙特雷": (25.6692, -100.2446, "America/Mexico_City"),        # CF Monterrey - Estadio BBVA
    "蒙特雷女足": (25.6692, -100.2446, "America/Mexico_City"),        # CF Monterrey - Estadio BBVA
    "普馬斯": (19.3328, -99.1919, "America/Mexico_City"),       # Pumas UNAM - Estadio Olímpico Universitario
    "普馬斯女足": (19.3328, -99.1919, "America/Mexico_City"),       # Pumas UNAM - Estadio Olímpico Universitario
    "托盧卡": (19.2883, -99.6669, "America/Mexico_City"),         # Deportivo Toluca - Estadio Nemesio Díez
    "帕丘卡": (20.1050, -98.7561, "America/Mexico_City"),         # Pachuca - Estadio Hidalgo
    "拿根亞": (25.6458, -103.3814, "America/Mexico_City"),  # Santos Laguna - Estadio Corona
    "拿根亞女足": (25.6458, -103.3814, "America/Mexico_City"),  # Santos Laguna - Estadio Corona
    "利昂": (21.1158, -101.6581, "America/Mexico_City"),          # León - Estadio León
    "利昂女足": (21.1158, -101.6581, "America/Mexico_City"),          # León - Estadio León
    "阿特拿斯": (20.6636, -103.3278, "America/Mexico_City"),      # Atlas - Estadio Jalisco
    "阿特拿斯女足": (20.6636, -103.3278, "America/Mexico_City"),      # Atlas - Estadio Jalisco
    "克雷塔羅": (20.5772, -100.3653, "America/Mexico_City"),      # Querétaro - Estadio Corregidora
    "普埃布拉": (19.0783, -98.1650, "America/Mexico_City"),       # Puebla - Estadio Cuauhtémoc
    "普埃布拉女足": (19.0783, -98.1650, "America/Mexico_City"),       # Puebla - Estadio Cuauhtémoc
    "FC馬薩特蘭": (23.2583, -106.3958, "America/Mexico_City"),      # Mazatlán - Estadio Mazatlán
    "FC馬薩特蘭女足": (23.2583, -106.3958, "America/Mexico_City"),      # Mazatlán - Estadio Mazatlán
    "祖亞雷斯": (31.7528, -106.4422, "America/Mexico_City"),        # Juárez - Estadio Olímpico Benito Juárez
    "迪祖亞拿": (32.5061, -116.9931, "America/Mexico_City"),        # Tijuana - Estadio Caliente
    "迪祖亞拿女足": (32.5061, -116.9931, "America/Mexico_City"),        # Tijuana - Estadio Caliente
    "尼卡沙": (21.8822, -102.2850, "America/Mexico_City"),        # Necaxa - Estadio Victoria
    "尼卡沙女足": (21.8822, -102.2850, "America/Mexico_City"),        # Necaxa - Estadio Victoria
    "聖路易斯體育會": (22.1389, -100.9608, "America/Mexico_City"),      # Atlético San Luis - Estadio Alfonso Lastras
    "聖路易斯體育會女足": (22.1389, -100.9608, "America/Mexico_City"),      # Atlético San Luis - Estadio Alfonso Lastras
    "阿坎巴羅": (20.0302, -100.7225, "America/Mexico_City"),  # Acámbaro FC
    "阿瓜卡特羅斯烏魯阿潘": (19.4192, -102.0577, "America/Mexico_City"),  # Aguacateros CDU
    "阿特薩諾斯梅特佩克": (19.2511, -99.6047, "America/Mexico_City"),  # Artesanos Metepec
    "阿延塞": (20.3333, -102.2500, "America/Mexico_City"),  # Ayense
    "卡哈奧布拉托斯": (20.6597, -103.3496, "America/Mexico_City"),  # Caja Oblatos
    "CDM": (16.7528, -93.1167, "America/Mexico_City"),  # CDM (Chiapas Deportivo Módulo)
    "西爾沃斯": (19.2617, -98.8978, "America/Mexico_City"),  # Ciervos
    "德波爾蒂沃東古": (19.6722, -99.1806, "America/Mexico_City"),  # Deportivo Dongu
    "奧阿哈卡龍": (17.0606, -96.7253, "America/Mexico_City"),  # Dragones de Oaxaca
    "胡阿納卡特蘭大猩猩": (20.5000, -103.1667, "America/Mexico_City"),  # Gorilas de Juanacatlán
    "雲拿度斯": (20.9333, -89.6000, "America/Mexico_City"),  # Estadio Carlos Iturralde
    "莫雷利亞體育會": (19.6886, -101.2183, "America/Mexico_City"),
    "阿蘭特": (17.0606, -96.7253, "America/Mexico_City"),
    "特帕蒂特蘭": (-33.3939, -70.6181, "America/Santiago"),
    "查巴巴華": (19.6886, -101.2183, "America/Mexico_City"),
    #挪威聯賽
    "維京": (58.9700, 5.7333, "Europe/Oslo"),  # Viking FK - Stavanger
    "波杜基林特": (67.2800, 14.4050, "Europe/Oslo"),  # FK Bodø/Glimt - Bodø
    "特羅姆瑟": (69.6496, 18.9570, "Europe/Oslo"),  # Tromsø IL - Tromsø
    "班蘭": (60.3928, 5.3242, "Europe/Oslo"),  # SK Brann - Bergen
    "山達費奧德": (59.1311, 10.2167, "Europe/Oslo"),  # Sandefjord Fotball - Sandefjord
    "華拿倫加": (59.9178, 10.7844, "Europe/Oslo"),  # Vålerenga Fotball - Oslo
    "洛辛堡": (63.4111, 10.4022, "Europe/Oslo"),  # Rosenborg BK - Trondheim
    "費德列斯達": (59.2133, 10.9298, "Europe/Oslo"),  # Fredrikstad FK - Fredrikstad
    "薩普斯堡08": (59.2844, 11.0986, "Europe/Oslo"),  # Sarpsborg 08 FF - Sarpsborg
    "莫迪": (62.7333, 7.1597, "Europe/Oslo"),  # Molde FK - Molde
    "咸卡姆": (60.7947, 11.0981, "Europe/Oslo"),  # Hamarkameratene - Hamar
    "KFUM奧斯陸": (59.9000, 10.8000, "Europe/Oslo"),  # KFUM-Kameratene Oslo - Oslo
    "基斯迪辛松": (63.1167, 7.7333, "Europe/Oslo"),  # Kristiansund BK - Kristiansund
    "拜尼": (58.8167, 5.7333, "Europe/Oslo"),  # Bryne FK - Bryne
    "利勒斯特羅姆": (59.9558, 11.0492, "Europe/Oslo"),  # Lillestrøm SK - Lillestrøm
    "克里斯蒂安松": (58.1469, 8.1119, "Europe/Oslo"),  # IK Start - Kristiansand
    "利尼史特朗": (59.9558, 11.0492, "Europe/Oslo"),
    "史達": (58.1469, 8.1119, "Europe/Oslo"),
    "艾格辛特": (58.7333, 5.6500, "Europe/Oslo"),
    "莫達倫": (59.1275, 10.2553, "Europe/Oslo"),
    #土耳其
    "alanyaspor": (36.5626, 32.0792, "Europe/Istanbul"), # Alanya Oba Stadium
    "antalyaspor": (36.888278, 30.668444, "Europe/Istanbul"), # Corendon Airlines Park
    "basaksehir": (41.12278, 28.80861, "Europe/Istanbul"), # Fatih Terim Stadium
    "besiktas": (41.03917, 28.99472, "Europe/Istanbul"), # Tüpraş Stadium
    "eyupspor": (40.879848, 29.257639, "Europe/Istanbul"), # Pendik Stadium
    "fatihkaragumruk": (41.07444, 28.76583, "Europe/Istanbul"), # Atatürk Olympic Stadium
    "fenerbahce": (40.987720, 29.036779, "Europe/Istanbul"), # Şükrü Saracoğlu Stadium
    "galatasaray": (41.10278, 28.99056, "Europe/Istanbul"), # Rams Park
    "gaziantep": (37.12389, 37.38250, "Europe/Istanbul"), # Gaziantep Stadium
    "genclerbirligi": (39.98028, 32.61389, "Europe/Istanbul"), # Eryaman Stadium
    "goztepe": (38.396821, 27.075950, "Europe/Istanbul"), # Gürsel Aksel Stadium
    "kasimpasa": (41.03278, 28.97250, "Europe/Istanbul"), # Recep Tayyip Erdoğan Stadium
    "kayserispor": (38.73722, 35.42306, "Europe/Istanbul"), # RHG Enertürk Enerji Stadium
    "kocaelispor": (40.77472, 30.01750, "Europe/Istanbul"), # Kocaeli Stadium
    "konyaspor": (37.946, 32.488, "Europe/Istanbul"), # Konya Metropolitan Municipality Stadium
    "rizespor": (41.04202, 40.5733, "Europe/Istanbul"), # Rize City Stadium
    "samsunspor": (41.22778, 36.45750, "Europe/Istanbul"), # Samsun 19 Mayıs Stadium
    "trabzonspor": (40.99917, 39.64583, "Europe/Istanbul"), # Papara Park
    # 巴甲 Brasileirão Série A 2025
    "flamengo": (-22.9122, -43.2300, "America/Sao_Paulo"),  # Maracanã
    "法林明高": (-22.9122, -43.2300, "America/Sao_Paulo"),  # Maracanã
    "palmeiras": (-23.5480, -46.6790, "America/Sao_Paulo"),  # Allianz Parque
    "彭美拉斯": (-23.5480, -46.6790, "America/Sao_Paulo"),  # Allianz Parque
    "彭美拉斯女足": (-23.5480, -46.6790, "America/Sao_Paulo"),  # Allianz Parque
    "corinthians": (-23.5453, -46.4744, "America/Sao_Paulo"),  # Neo Química Arena
    "哥連泰斯": (-23.5453, -46.4744, "America/Sao_Paulo"),  # Neo Química Arena
    "sao paulo": (-23.6000, -46.7200, "America/Sao_Paulo"),  # Morumbi
    "聖保羅": (-23.6000, -46.7200, "America/Sao_Paulo"),  # Morumbi
    "聖保羅女足": (-23.6000, -46.7200, "America/Sao_Paulo"),  # Morumbi
    "botafogo": (-22.9122, -43.2300, "America/Sao_Paulo"),  # Estádio Olímpico Nilton Santos (Engenhão)
    "保地花高": (-22.9122, -43.2300, "America/Sao_Paulo"),  # Estádio Olímpico Nilton Santos (Engenhão)
    "fluminense": (-22.9122, -43.2300, "America/Sao_Paulo"),  # Maracanã (共享)
    "富明尼斯": (-22.9122, -43.2300, "America/Sao_Paulo"),  # Maracanã (共享)
    "vasco da gama": (-22.8911, -43.2286, "America/Sao_Paulo"),  # São Januário
    "華斯高": (-22.8911, -43.2286, "America/Sao_Paulo"),  # São Januário    
    "cruzeiro": (-19.8658, -43.9711, "America/Sao_Paulo"),  # Mineirão
    "高士路": (-19.8658, -43.9711, "America/Sao_Paulo"),  # Mineirão
    "atletico mineiro": (-19.9039, -43.9178, "America/Sao_Paulo"),  # Arena MRV
    "明尼路": (-19.9039, -43.9178, "America/Sao_Paulo"),  # Arena MRV
    "gremio": (-30.0656, -51.2350, "America/Sao_Paulo"),  # Arena do Grêmio
    "甘美奧": (-30.0656, -51.2350, "America/Sao_Paulo"),  # Arena do Grêmio
    "甘美奧女足": (-30.0656, -51.2350, "America/Sao_Paulo"),  # Arena do Grêmio
    "internacional": (-30.0656, -51.2350, "America/Sao_Paulo"),  # Beira-Rio
    "國際體育會": (-30.0656, -51.2350, "America/Sao_Paulo"),  # Beira-Rio
    "國際體育會女足": (-30.0656, -51.2350, "America/Sao_Paulo"),  # Beira-Rio
    "bahia": (-12.9789, -38.5044, "America/Sao_Paulo"),  # Arena Fonte Nova
    "巴希亞": (-12.9789, -38.5044, "America/Sao_Paulo"),  # Arena Fonte Nova
    "vitoria": (-12.9392, -38.4342, "America/Sao_Paulo"),  # Barradão
    "維多利亞": (-12.9392, -38.4342, "America/Sao_Paulo"),  # Barradão
    "fortaleza": (-3.8072, -38.5225, "America/Sao_Paulo"),  # Castelão
    "福塔雷薩": (-3.8072, -38.5225, "America/Sao_Paulo"),          # Fortaleza - Castelão
    "sport recife": (-8.0267, -34.8911, "America/Sao_Paulo"),  # Ilha do Retiro
    "利斯菲體育會": (-8.0267, -34.8911, "America/Sao_Paulo"),  # Ilha do Retiro
    "哥列迪巴": (-25.421111, -49.2595, "America/Sao_Paulo"),  # Ilha do Retiro
    "ceara": (-3.8072, -38.5225, "America/Sao_Paulo"),  # Castelão (共享)
    "施亞拉": (-3.8072, -38.5225, "America/Sao_Paulo"),  # Castelão (共享)
    "santos": (-23.9600, -46.3389, "America/Sao_Paulo"),  # Vila Belmiro
    "山度士": (-23.9600, -46.3389, "America/Sao_Paulo"),  # Vila Belmiro
    "山度士女足": (-23.9600, -46.3389, "America/Sao_Paulo"),  # Vila Belmiro
    "mirassol": (-20.8167, -49.9500, "America/Sao_Paulo"),  # Estádio José Maria de Campos Maia
    "米拉索": (-20.8167, -49.9500, "America/Sao_Paulo"),  # Estádio José Maria de Campos Maia
    "bragantino": (-23.0000, -46.5333, "America/Sao_Paulo"),  # Nabi Abi Chedid / Arena Nico
    "巴拉干天奴紅牛": (-23.0000, -46.5333, "America/Sao_Paulo"),  # Nabi Abi Chedid / Arena Nico
    "juventude": (-29.1667, -51.1667, "America/Sao_Paulo"),  # Alfredo Jaconi
    "查比高恩斯":(-27.104139, -52.607,"America/Sao_Paulo"),
    "帕拉尼恩斯": (-25.448333, -49.276944,"America/Sao_Paulo"),
    #巴西乙級
    "雷莫": (-1.4558, -48.4903, "America/Belem"),
    "戈亞尼恩斯": (-16.6869, -49.2644, "America/Sao_Paulo"),  # Atlético Clube Goianiense - Estádio Antônio Accioly (Goiânia)
    "艾華爾": (-27.5958, -48.5186, "America/Sao_Paulo"),  # Avaí FC - Estádio da Ressacada (Florianópolis)
    "青年人": (-29.1667, -51.1833, "America/Sao_Paulo"),  # Esporte Clube Juventude - Estádio Alfredo Jaconi (Caxias do Sul)
    "森柏奧哥利亞": (-2.5311, -44.3028, "America/Fortaleza"),  # Sampaio Corrêa Futebol Clube - Estádio Castelão (São Luís)
    "伊圖諾": (-23.2667, -47.3000, "America/Sao_Paulo"),  # Ituano FC - Estádio Municipal Doutor Novelli Júnior (Itu)
    "基斯奧馬": (-28.6778, -49.3722, "America/Sao_Paulo"),  # Criciúma Esporte Clube - Estádio Heriberto Hülse (Criciúma)
    "隆德里納": (-23.3100, -51.1628, "America/Sao_Paulo"),  # Londrina Esporte Clube - Estádio do Café (Londrina)
    "古蘭尼": (-22.9000, -47.0667, "America/Sao_Paulo"),  # Guarani FC - Estádio Brinco de Ouro (Campinas)
    "雷加塔斯": (-9.6667, -35.7353, "America/Maceio"),  # Clube de Regatas Brasil - Estádio Rei Pelé (Maceió)
    "邦迪比達": (-22.9000, -47.0667, "America/Sao_Paulo"),  # Associação Atlética Ponte Preta - Estádio Moisés Lucarelli (Campinas)
    "維拉諾瓦": (-16.6869, -49.2644, "America/Sao_Paulo"),  # Vila Nova Futebol Clube - Estádio Onésio Brasileiro Alvarenga (Goiânia)
    "托姆本斯": (-19.9167, -43.9333, "America/Sao_Paulo"),  # Tombense Futebol Clube - Estádio Soares de Azevedo (Muriaé) 或 Estádio Antônio Guimarães de Carvalho (Tombos)
    "路禾利桑天奴": (-21.2333, -49.6333, "America/Sao_Paulo"),  # Grêmio Novorizontino - Estádio Jorge Ismael de Biasi (Novo Horizonte)
    "ABC納泰": (-5.7833, -35.2000, "America/Fortaleza"),  # ABC Futebol Clube - Estádio Frasqueirão Novo (Natal)
    "保地花高SP": (-21.1833, -47.8100, "America/Sao_Paulo"),  # Botafogo Futebol Clube (SP) - Estádio Santa Cruz (Ribeirão Preto)

    # 巴西聖保羅省聯賽 Paulistão 2025
    "卡比華蘭奴": (-22.99391, -47.51438, "America/Sao_Paulo"),
    "諾羅斯特": (-22.3147, -49.0607, "America/Sao_Paulo"),
    "ponte preta": (-22.9142, -47.0528, "America/Sao_Paulo"),  # Moisés Lucarelli (Campinas)
    "guarani": (-22.9083, -47.0444, "America/Sao_Paulo"),  # Brinco de Ouro da Princesa
    "inter de limeira": (-22.5667, -47.4000, "America/Sao_Paulo"),  # Limeirão
    "novorizontino": (-21.2167, -49.0167, "America/Sao_Paulo"),  # Jorge Ismael de Biasi
    "santo andre": (-23.6667, -46.5333, "America/Sao_Paulo"),  # Bruno José Daniel
    "portuguesa": (-23.5306, -46.6333, "America/Sao_Paulo"),  # Canindé
    "agua santa": (-23.6667, -46.7833, "America/Sao_Paulo"),  # Distrital do Inamar (Diadema)
    "sao bernardo": (-23.7000, -46.5500, "America/Sao_Paulo"),  # 1º de Maio
    "velo clube": (-22.3667, -47.3833, "America/Sao_Paulo"),  # Benito Agnelo Castellano (Rio Claro)
    "noroeste": (-21.9833, -49.8667, "America/Sao_Paulo"),  # Alfredão (Alfredo de Castilho, Bauru)
    "capivariano": (22.993523, -47.51441, "America/Sao_Paulo"),
    # 瑞超 Allsvenskan 2025
    "aik": (59.3456, 18.0900, "Europe/Stockholm"),  # Strawberry Arena (Friends Arena)
    "brommapojkarna": (59.3456, 18.0900, "Europe/Stockholm"),  # Grimsta IP (或共享)
    "degerfors if": (59.2333, 14.4500, "Europe/Stockholm"),  # Stora Valla
    "djurgardens if": (59.3061, 18.0819, "Europe/Stockholm"),  # Tele2 Arena
    "gais": (57.7061, 11.9817, "Europe/Stockholm"),  # Gamla Ullevi (共享)
    "hammarby if": (59.3061, 18.0819, "Europe/Stockholm"),  # Tele2 Arena (共享)
    "halmstads bk": (56.6833, 12.8667, "Europe/Stockholm"),  # Örjans Vall
    "ifk goteborg": (57.7061, 11.9817, "Europe/Stockholm"),  # Gamla Ullevi
    "if elfsborg": (57.7333, 12.9333, "Europe/Stockholm"),  # Borås Arena
    "ifk varnamo": (57.1833, 14.0500, "Europe/Stockholm"),  # Finnvedsvallen
    "ik sirius": (59.9167, 17.6500, "Europe/Stockholm"),  # Studenternas IP
    "mjallby aif": (56.0500, 14.8500, "Europe/Stockholm"),  # Strandvallen
    "osters if": (57.0000, 14.8000, "Europe/Stockholm"),  # Visma Arena (Växjö)
    "häcken": (57.7333, 11.9333, "Europe/Stockholm"),  # Bravida Arena
    "malmö ff": (55.5839, 12.9889, "Europe/Stockholm"),  # Eleda Stadion
    "ifk norrköping": (58.5833, 16.1833, "Europe/Stockholm"),  # PlatinumCars Arena
    "st gallen": (47.408333, 9.306389,"Europe/Stockholm"),
    "馬模": (55.5819, 12.9989, "Europe/Stockholm"),  # Malmö FF - Eleda Stadion
    "佐加頓斯": (59.3289, 18.0653, "Europe/Stockholm"),  # Djurgårdens IF - Tele2 Arena
    "夏拿佐普": (57.7353, 12.0067, "Europe/Stockholm"),  # BK Häcken - Bravida Arena
    "哥登堡": (57.7311, 11.9358, "Europe/Stockholm"),  # IFK Göteborg - Gamla Ullevi
    "艾夫斯堡": (57.7350, 12.9783, "Europe/Stockholm"),  # IF Elfsborg - Borås Arena
    "咸史達斯": (56.6750, 12.8639, "Europe/Stockholm"),  # Halmstads BK - Örjans Vall
    "諾高平": (58.5833, 16.1833, "Europe/Stockholm"),  # IFK Norrköping - PlatinumCars Arena
    "華美爾比": (57.1167, 15.8667, "Europe/Stockholm"),  # Kalmar FF - Guldfågeln Arena
    "米贊比": (55.6167, 13.0000, "Europe/Stockholm"),  # Mjällby AIF - Strandvallen
    "布羅馬波卡納": (59.3333, 17.9167, "Europe/Stockholm"),  # Brommapojkarna - Grimsta Arena
    "天狼星": (59.9167, 17.6333, "Europe/Stockholm"),  # IK Sirius - Studenternas IP
    "瓦爾貝加": (58.3833, 13.8667, "Europe/Stockholm"),  # Värnamo IF - Finnvedsvallen
    "賀斯達": (56.0333, 12.7000, "Europe/Stockholm"),  # Hammarby IF - Tele2 Arena
    "哥斯達": (57.7333, 12.0000, "Europe/Stockholm"),  # GAIS - Gamla Ullevi
    "哈馬比": (59.3061, 18.0819, "Europe/Stockholm"),  # Tele2 Arena (共享)
    "奧斯達": (57.7089, 11.9744, "Europe/Stockholm"), 
    "加爾斯": (57.7089, 11.9744, "Europe/Stockholm"),
    "AIK蘇納": (59.3544, 18.0000, "Europe/Stockholm"),
    # 阿根廷職業聯賽 Liga Profesional Argentina 2025
    "river plate": (-34.5453, -58.4497, "America/Argentina/Buenos_Aires"),  # Estadio Monumental Antonio Vespucio Liberti
    "boca juniors": (-34.6356, -58.3647, "America/Argentina/Buenos_Aires"),  # La Bombonera
    "racing club": (-34.6675, -58.3686, "America/Argentina/Buenos_Aires"),  # El Cilindro (Presidente Perón)
    "independiente": (-34.6703, -58.3711, "America/Argentina/Buenos_Aires"),  # Libertadores de América
    "san lorenzo": (-34.6522, -58.4400, "America/Argentina/Buenos_Aires"),  # Nuevo Gasómetro (Pedro Bidegain)
    "velez sarsfield": (-34.6350, -58.5208, "America/Argentina/Buenos_Aires"),  # José Amalfitani
    "estudiantes lp": (-34.9117, -57.9322, "America/Argentina/Buenos_Aires"),  # Jorge Luis Hirschi
    "gimnasia lp": (-34.9111, -57.9458, "America/Argentina/Buenos_Aires"),  # Juan Carmelo Zerillo
    "rosario central": (-32.9139, -60.6744, "America/Argentina/Buenos_Aires"),  # Gigante de Arroyito
    "newell's old boys": (-32.9558, -60.6614, "America/Argentina/Buenos_Aires"),  # Marcelo Bielsa (El Coloso del Parque)
    "lanus": (-34.7178, -58.3839, "America/Argentina/Buenos_Aires"),  # Ciudad de Lanús (Néstor Díaz Pérez)
    "banfield": (-34.7506, -58.3878, "America/Argentina/Buenos_Aires"),  # Florencio Sola
    "argentinos juniors": (-34.6097, -58.4714, "America/Argentina/Buenos_Aires"),  # Diego Armando Maradona
    "huracan": (-34.6436, -58.3967, "America/Argentina/Buenos_Aires"),  # Tomás Adolfo Ducó
    "talleres cordoba": (-31.3689, -64.2461, "America/Argentina/Buenos_Aires"),  # Mario Alberto Kempes (主要)
    "belgrano": (-31.3689, -64.2461, "America/Argentina/Buenos_Aires"),  # Julio César Villagra (Gigante de Alberdi)
    "instituto": (-31.3833, -64.1833, "America/Argentina/Buenos_Aires"),  # Juan Domingo Perón
    "godoy cruz": (-32.9189, -68.8769, "America/Argentina/Buenos_Aires"),  # Malvinas Argentinas
    "defensa y justicia": (-34.7922, -58.2917, "America/Argentina/Buenos_Aires"),  # Norberto Tomaghello
    "central cordoba sde": (-27.7833, -64.2667, "America/Argentina/Buenos_Aires"),  # Único Madre de Ciudades
    "atletico tucuman": (-26.8172, -65.2167, "America/Argentina/Buenos_Aires"),  # Monumental José Fierro
    "union santa fe": (-31.6333, -60.7167, "America/Argentina/Buenos_Aires"),  # 15 de Abril
    "platense": (-34.5389, -58.4667, "America/Argentina/Buenos_Aires"),  # Ciudad de Vicente López
    "barracas central": (-34.6417, -58.3819, "America/Argentina/Buenos_Aires"),  # Claudio Fabián Tapia
    "sarmiento junin": (-34.6083, -60.9500, "America/Argentina/Buenos_Aires"),  # Eva Perón
    "tigre": (-34.4489, -58.5922, "America/Argentina/Buenos_Aires"),  # José Dellagiovanna
    "deportivo riestra": (-34.6583, -58.4667, "America/Argentina/Buenos_Aires"),  # Guillermo Laza
    "independiente rivadavia": (-32.9167, -68.8667, "America/Argentina/Buenos_Aires"),  # Bautista Gargantini
    "河床": (-34.5453, -58.4497, "America/Argentina/Buenos_Aires"),  # Estadio Monumental Antonio Vespucio Liberti
    "小保加": (-34.6356, -58.3647, "America/Argentina/Buenos_Aires"),  # La Bombonera
    "競賽會": (-34.6675, -58.3686, "America/Argentina/Buenos_Aires"),  # El Cilindro (Presidente Perón)
    "獨立隊": (-34.6703, -58.3711, "America/Argentina/Buenos_Aires"),  # Libertadores de América
    "阿度斯維": (-38.0333, -57.5333, "America/Argentina/Buenos_Aires"),
    "聖羅倫素": (-34.6522, -58.4400, "America/Argentina/Buenos_Aires"),  # Nuevo Gasómetro (Pedro Bidegain)
    "沙士菲": (-34.6350, -58.5208, "America/Argentina/Buenos_Aires"),  # José Amalfitani
    "里奧古亞圖學生隊": (-34.9117, -57.9322, "America/Argentina/Buenos_Aires"),  # Jorge Luis Hirschi
    "甘拿斯亞": (-34.9111, -57.9458, "America/Argentina/Buenos_Aires"),  # Juan Carmelo Zerillo
    "羅沙里奧中央": (-32.9139, -60.6744, "America/Argentina/Buenos_Aires"),  # Gigante de Arroyito
    "紐維爾舊生": (-32.9558, -60.6614, "America/Argentina/Buenos_Aires"),  # Marcelo Bielsa (El Coloso del Parque)
    "拉魯斯": (-34.7178, -58.3839, "America/Argentina/Buenos_Aires"),  # Ciudad de Lanús (Néstor Díaz Pérez)
    "班菲特": (-34.7506, -58.3878, "America/Argentina/Buenos_Aires"),  # Florencio Sola
    "小阿根廷人": (-34.6097, -58.4714, "America/Argentina/Buenos_Aires"),  # Diego Armando Maradona
    "颶風隊": (-34.6436, -58.3967, "America/Argentina/Buenos_Aires"),  # Tomás Adolfo Ducó
    "泰拿尼斯": (-31.3689, -64.2461, "America/Argentina/Buenos_Aires"),  # Mario Alberto Kempes (主要)
    "貝格拉諾": (-31.3689, -64.2461, "America/Argentina/Buenos_Aires"),  # Julio César Villagra (Gigante de Alberdi)
    "科爾多瓦學院": (-31.3833, -64.1833, "America/Argentina/Buenos_Aires"),  # Juan Domingo Perón
    "葛度爾古斯": (-32.9189, -68.8769, "America/Argentina/Buenos_Aires"),  # Malvinas Argentinas
    "防衛者": (-34.7922, -58.2917, "America/Argentina/Buenos_Aires"),  # Norberto Tomaghello
    "CA科爾多瓦中央": (-27.7833, -64.2667, "America/Argentina/Buenos_Aires"),  # Único Madre de Ciudades
    "圖庫曼體育會": (-26.8172, -65.2167, "America/Argentina/Buenos_Aires"),  # Monumental José Fierro
    "聖達菲聯": (-31.6333, -60.7167, "America/Argentina/Buenos_Aires"),  # 15 de Abril
    "CA普拉坦斯": (-34.5389, -58.4667, "America/Argentina/Buenos_Aires"),  # Ciudad de Vicente López
    "巴拉卡斯中央": (-34.6417, -58.3819, "America/Argentina/Buenos_Aires"),  # Claudio Fabián Tapia
    "沙米恩圖": (-34.6083, -60.9500, "America/Argentina/Buenos_Aires"),  # Eva Perón
    "提格雷": (-34.4489, -58.5922, "America/Argentina/Buenos_Aires"),  # José Dellagiovanna
    "堤格雷": (-34.4489, -58.5922, "America/Argentina/Buenos_Aires"),  # José Dellagiovanna
    "萊斯查": (-34.6583, -58.4667, "America/Argentina/Buenos_Aires"),  # Guillermo Laza
    "利華達維亞獨立": (-32.9167, -68.8667, "America/Argentina/Buenos_Aires"),  # Bautista Gargantini
    "甘拿斯亞文度沙": (-32.8897, -68.8803, "America/Argentina/Mendoza"),
    "學生隊": (-34.6353, -58.3648, "America/Argentina/Buenos_Aires"),
    # 秘魯甲級聯賽 Liga 1 Perú 2025
    "利馬聯": (-12.0681, -77.0333, "America/Lima"),  # Estadio Alejandro Villanueva (Matute)
    "alianza lima": (-12.0681, -77.0333, "America/Lima"),  # Estadio Alejandro Villanueva (Matute)
    "universitario de deportes": (-12.0672, -77.0339, "America/Lima"),  # Estadio Monumental "U"
    "sporting cristal": (-12.0564, -77.0317, "America/Lima"),  # Estadio Alberto Gallardo (或 Nacional 共享)
    "alianza atletico": (-4.9067, -80.7067, "America/Lima"),  # Estadio Campeones del 36 (Sullana)
    "atletico grau": (-4.9067, -80.7067, "America/Lima"),  # Estadio Campeones del 36 (或 Bernal)
    "cienciano": (-13.5242, -71.9667, "America/Lima"),  # Estadio Inca Garcilaso de la Vega (Cusco)
    "cusco fc": (-13.5242, -71.9667, "America/Lima"),  # Estadio Inca Garcilaso de la Vega (共享)
    "deportivo garcilaso": (-13.5242, -71.9667, "America/Lima"),  # Estadio Inca Garcilaso de la Vega (共享)
    "fbc melgar": (-16.3992, -71.5361, "America/Lima"),  # Estadio Monumental UNSA (Arequipa)
    "sport huancayo": (-12.0667, -75.2167, "America/Lima"),  # Estadio Huancayo
    "utc cajamarca": (-7.1667, -78.5167, "America/Lima"),  # Estadio Héroes de San Ramón (Cajamarca)
    "comerciantes unidos": (-6.2333, -77.8667, "America/Lima"),  # Estadio Juan Maldonado Gamarra (Cutervo)
    "los chankas": (-13.6333, -72.8833, "America/Lima"),  # Estadio Los Chankas (Andahuaylas)
    "deportivo binacional": (-15.8333, -70.0167, "America/Lima"),  # Estadio Guillermo Briceño Rosamedina (Juliaca)
    "ayacucho fc": (-13.1589, -74.2256, "America/Lima"),  # Estadio Ciudad de Cumaná (Ayacucho)
    "adt tarma": (-11.4189, -75.6833, "America/Lima"),  # Estadio Unión Tarma
    "sport boys": (-12.0678, -77.1167, "America/Lima"),  # Estadio Miguel Grau (Callao)
    "alianza universidad": (-9.9333, -76.2500, "America/Lima"),  # Estadio Heraclio Tapia (Huánuco)
    "juan pablo ii college": (-5.1833, -80.6333, "America/Lima"),  # Estadio César Flores Marigorda (Lambayeque)
    # 挪超 Eliteserien 2025
    "bodo/glimt": (67.2789, 14.4078, "Europe/Oslo"),  # Aspmyra Stadion
    "molde": (62.7340, 7.1580, "Europe/Oslo"),  # Aker Stadion
    "viking fk": (58.9150, 5.7320, "Europe/Oslo"),  # SR-Bank Arena (Viking Stadion)
    "rosenborg": (63.4300, 10.4020, "Europe/Oslo"),  # Lerkendal Stadion
    "brann": (60.3672, 5.3572, "Europe/Oslo"),  # Brann Stadion
    "lillestrom": (59.9600, 11.0650, "Europe/Oslo"),  # Åråsen Stadion
    "valerenga": (59.9431, 10.7239, "Europe/Oslo"),  # Intility Arena
    "sarpsborg 08": (59.2981, 11.1089, "Europe/Oslo"),  # Sarpsborg Stadion
    "hamkam": (60.7939, 11.0761, "Europe/Oslo"),  # Briskeby Arena
    "tromso": (69.6489, 18.9550, "Europe/Oslo"),  # Alfheim Stadion
    "fredrikstad": (59.2128, 10.9300, "Europe/Oslo"),  # Fredrikstad Stadion
    "kristiansund": (63.1117, 7.7322, "Europe/Oslo"),  # Kristiansund Stadion
    "sandefjord": (59.1306, 10.1850, "Europe/Oslo"),  # Jotun Arena (Sandefjord Arena)
    "odd": (59.3850, 9.3600, "Europe/Oslo"),  # Skagerak Arena
    "stromsgodset": (59.7333, 10.1667, "Europe/Oslo"),  # Marienlyst Stadion
    "kfum oslo": (59.9172, 10.8069, "Europe/Oslo"),  # KFUM Arena (Ekeberg)
    # 西甲 La Liga 2025/26
    "real madrid": (40.4530, -3.6883, "Europe/Madrid"),  # Santiago Bernabéu
    "barcelona": (41.3809, 2.1228, "Europe/Madrid"),  # Camp Nou / Spotify Camp Nou (2025/26 已部分回歸)
    "atletico madrid": (40.4362, -3.5994, "Europe/Madrid"),  # Cívitas Metropolitano
    "valencia": (39.4747, -0.3983, "Europe/Madrid"),  # Mestalla
    "real betis": (37.3564, -5.9817, "Europe/Madrid"),  # Benito Villamarín (或臨時 La Cartuja)
    "athletic bilbao": (43.2640, -2.9491, "Europe/Madrid"),  # San Mamés
    "real sociedad": (43.3014, -1.9733, "Europe/Madrid"),  # Reale Arena
    "sevilla": (37.3839, -5.9706, "Europe/Madrid"),  # Ramón Sánchez-Pizjuán
    "villarreal": (39.9442, -0.1036, "Europe/Madrid"),  # Estadio de la Cerámica
    "celta vigo": (42.2117, -8.7394, "Europe/Madrid"),  # Balaídos
    "getafe": (40.3256, -3.7147, "Europe/Madrid"),  # Coliseum Alfonso Pérez
    "rayo vallecano": (40.3919, -3.6589, "Europe/Madrid"),  # Estadio de Vallecas
    "osasuna": (42.7964, -1.6367, "Europe/Madrid"),  # El Sadar
    "mallorca": (39.5897, 2.6303, "Europe/Madrid"),  # Son Moix
    "levante": (39.4947, -0.3636, "Europe/Madrid"),  # Ciutat de València
    "elche": (38.2672, -0.6628, "Europe/Madrid"),  # Martínez Valero
    "real oviedo": (43.3608, -5.8706, "Europe/Madrid"),  # Carlos Tartiere
    "espanyol": (41.3478, 2.0756, "Europe/Madrid"),  # RCDE Stadium
    "alaves": (42.8372, -2.6878, "Europe/Madrid"),  # Mendizorrotza
    "las palmas": (28.1003, -15.4572, "Europe/Madrid"),  # Estadio Gran Canaria (若未降級調整)
    #西乙 Segunda División 2025/26
    "real valladolid": (41.6444, -4.7611, "Europe/Madrid"),  # José Zorrilla
    "ud las palmas": (28.1003, -15.4572, "Europe/Madrid"),  # Gran Canaria
    "leganes": (40.3403, -3.7606, "Europe/Madrid"),  # Butarque
    "cd tenerife": (28.4631, -16.2620, "Europe/Madrid"),  # Heliodoro Rodríguez López
    "cd mirandes": (42.6833, -2.9500, "Europe/Madrid"),  # Anduva (Municipal de Anduva)
    "sd huesca": (42.1319, -0.4250, "Europe/Madrid"),  # El Alcoraz
    "granada": (37.1528, -3.5958, "Europe/Madrid"),  # Nuevo Los Cármenes
    "cadiz": (36.5022, -6.2739, "Europe/Madrid"),  # Nuevo Mirandilla
    "malaga": (36.7342, -4.4547, "Europe/Madrid"),  # La Rosaleda
    "sporting gijon": (43.5361, -5.6372, "Europe/Madrid"),  # El Molinón
    "real zaragoza": (41.6364, -0.9017, "Europe/Madrid"),  # La Romareda
    "almeria": (36.8397, -2.4361, "Europe/Madrid"),  # Power Horse Stadium (Juegos Mediterráneos)
    "deportivo la coruna": (43.3689, -8.4175, "Europe/Madrid"),  # Riazor
    "racing santander": (43.4631, -3.8350, "Europe/Madrid"),  # El Sardinero
    "burgos": (42.3442, -3.6806, "Europe/Madrid"),  # El Plantío
    "cartagena": (37.6100, -0.9958, "Europe/Madrid"),  # Cartagonova
    "cordoba": (37.8739, -4.7647, "Europe/Madrid"),  # Nuevo Arcángel
    "castellon": (39.9958, -0.0375, "Europe/Madrid"),  # Castalia
    "eibar": (43.1814, -2.4750, "Europe/Madrid"),  # Ipurua
    "eldense": (38.3500, -0.7833, "Europe/Madrid"),  # Nuevo Pepico Amat
    "oviedo": (43.3608, -5.8706, "Europe/Madrid"),  # Carlos Tartiere (部分可能已升級，但保留)
    "albacete": (38.9833, -1.8531, "Europe/Madrid"),  # Carlos Belmonte

    # 西甲 La Liga 2025/26
    "基達菲": (40.3256, -3.7147, "Europe/Madrid"),
    "皇家馬德里": (40.4530, -3.6883, "Europe/Madrid"),  # Real Madrid - Santiago Bernabéu
    "巴塞隆拿": (41.3809, 2.1228, "Europe/Madrid"),  # Barcelona - Camp Nou / Spotify Camp Nou (2025/26 已部分回歸)
    "馬德里體育會": (40.4362, -3.5994, "Europe/Madrid"),  # Atlético Madrid - Cívitas Metropolitano
    "華倫西亞": (39.4747, -0.3983, "Europe/Madrid"),  # Valencia - Mestalla
    "貝迪斯": (37.3564, -5.9817, "Europe/Madrid"),  # Real Betis - Benito Villamarín (或臨時 La Cartuja)
    "畢爾包": (43.2640, -2.9491, "Europe/Madrid"),  # Athletic Bilbao - San Mamés
    "皇家蘇斯達": (43.3014, -1.9733, "Europe/Madrid"),  # Real Sociedad - Reale Arena
    "皇家蘇斯達B隊": (43.3014, -1.9736, "Europe/Madrid"),
    "西維爾": (37.3839, -5.9706, "Europe/Madrid"),  # Sevilla - Ramón Sánchez-Pizjuán
    "維拉利爾": (39.9442, -0.1036, "Europe/Madrid"),  # Villarreal - Estadio de la Cerámica
    "塞爾塔": (42.2117, -8.7394, "Europe/Madrid"),  # Celta Vigo - Balaídos
    "赫塔菲": (40.3256, -3.7147, "Europe/Madrid"),  # Getafe - Coliseum Alfonso Pérez
    "華列卡諾": (40.3919, -3.6589, "Europe/Madrid"),  # Rayo Vallecano - Estadio de Vallecas
    "奧沙辛拿": (42.7964, -1.6367, "Europe/Madrid"),  # Osasuna - El Sadar
    "馬略卡": (39.5897, 2.6303, "Europe/Madrid"),  # Mallorca - Son Moix
    "利雲特": (39.4947, -0.3636, "Europe/Madrid"),  # Levante - Ciutat de València
    "艾爾切": (38.2672, -0.6628, "Europe/Madrid"),  # Elche - Martínez Valero
    "奧維多": (43.3608, -5.8706, "Europe/Madrid"),  # Real Oviedo - Carlos Tartiere
    "愛斯賓奴": (41.3478, 2.0756, "Europe/Madrid"),  # Espanyol - RCDE Stadium
    "艾拉維斯": (42.8372, -2.6878, "Europe/Madrid"),  # Alavés - Mendizorrotza
    "基羅納": (41.961389, 2.828611, "Europe/Madrid"),  #girona
    "赫羅納": (41.961389, 2.828611, "Europe/Madrid"),  #girona
    "希杭": (43.5361, -5.6372, "Europe/Madrid"),
    # 西乙 Segunda División 2025/26
    "華拉多利": (41.6444, -4.7611, "Europe/Madrid"),  # Real Valladolid - José Zorrilla
    "FC安道爾": (42.5044, 1.5347, "Europe/Andorra"),
    "拉斯彭馬斯": (28.1003, -15.4572, "Europe/Madrid"),  # UD Las Palmas - Gran Canaria
    "萊加內斯": (40.3403, -3.7606, "Europe/Madrid"),  # Leganés - Butarque
    "特內里費": (28.4631, -16.2620, "Europe/Madrid"),  # CD Tenerife - Heliodoro Rodríguez López
    "米蘭德斯": (42.6833, -2.9500, "Europe/Madrid"),  # CD Mirandés - Anduva (Municipal de Anduva)
    "韋斯卡": (42.1319, -0.4250, "Europe/Madrid"),  # SD Huesca - El Alcoraz
    "格蘭納達": (37.1528, -3.5958, "Europe/Madrid"),  # Granada - Nuevo Los Cármenes
    "加迪斯": (36.5022, -6.2739, "Europe/Madrid"),  # Cádiz - Nuevo Mirandilla
    "馬拉加": (36.7342, -4.4547, "Europe/Madrid"),  # Málaga - La Rosaleda
    "希洪體育": (43.5361, -5.6372, "Europe/Madrid"),  # Sporting Gijón - El Molinón
    "薩拉戈薩": (41.6364, -0.9017, "Europe/Madrid"),  # Real Zaragoza - La Romareda
    "艾美利亞": (36.8397, -2.4361, "Europe/Madrid"),  # Almería - Power Horse Stadium (Juegos Mediterráneos)
    "拉科魯尼亞": (43.3689, -8.4175, "Europe/Madrid"),  # Deportivo La Coruña - Riazor
    "桑坦德競技": (43.4631, -3.8350, "Europe/Madrid"),  # Racing Santander - El Sardinero
    "布爾戈斯": (42.3442, -3.6806, "Europe/Madrid"),  # Burgos - El Plantío
    "卡塔赫納": (37.6100, -0.9958, "Europe/Madrid"),  # Cartagena - Cartagonova
    "科爾多瓦": (37.8739, -4.7647, "Europe/Madrid"),  # Córdoba - Nuevo Arcángel
    "卡斯特利翁": (39.9958, -0.0375, "Europe/Madrid"),  # Castellón - Castalia
    "伊巴": (43.1814, -2.4750, "Europe/Madrid"),
    "伊巴女足": (43.1814, -2.4750, "Europe/Madrid"),
    "艾爾登斯": (38.3500, -0.7833, "Europe/Madrid"),  # Eldense - Nuevo Pepico Amat
    "阿爾巴塞特": (38.9833, -1.8531, "Europe/Madrid"),  # Albacete - Carlos Belmonte
    "施奧達": (43.2640, -2.9491, "Europe/Madrid"),
    "侯爾斯卡": (43.5333, -5.6372, "Europe/Madrid"),
    "卡迪斯": (36.5022, -6.2739, "Europe/Madrid"),
    "華歷簡奴": (40.4530, -3.6883, "Europe/Madrid"),
    "桑坦德": (43.4631, -3.8350, "Europe/Madrid"),
    # 荷甲 Eredivisie 2025/26 (主要)
    "ajax": (52.3142, 4.9419, "Europe/Amsterdam"),  # Johan Cruyff Arena
    "psv eindhoven": (51.4417, 5.4678, "Europe/Amsterdam"),  # Philips Stadion
    "feyenoord": (51.9219, 4.5233, "Europe/Amsterdam"),  # Stadion Feijenoord (De Kuip)
    "az alkmaar": (52.6128, 4.7422, "Europe/Amsterdam"),  # AFAS Stadion
    "fc twente": (52.2367, 6.8372, "Europe/Amsterdam"),  # De Grolsch Veste
    "fc utrecht": (52.0781, 5.1456, "Europe/Amsterdam"),  # Stadion Galgenwaard
    "go ahead eagles": (52.2206, 6.0011, "Europe/Amsterdam"),  # De Adelaarshorst
    "伊高斯": (52.2206, 6.0011, "Europe/Amsterdam"),  # De Adelaarshorst
    "heracles almelo": (52.3389, 6.6511, "Europe/Amsterdam"),  # Erve Asito
    "pec zwolle": (52.5158, 6.1194, "Europe/Amsterdam"),  # MAC³PARK Stadion
    "fortuna sittard": (50.9978, 5.8447, "Europe/Amsterdam"),  # Fortuna Sittard Stadion
    "nec nijmegen": (51.8239, 5.8347, "Europe/Amsterdam"),  # Goffertstadion
    "sc heerenveen": (52.9583, 5.9342, "Europe/Amsterdam"),  # Abe Lenstra Stadion
    "sparta rotterdam": (51.9194, 4.4344, "Europe/Amsterdam"),  # Het Kasteel (Sparta Stadion)
    "fc groningen": (53.2061, 6.5914, "Europe/Amsterdam"),  # Euroborg
    "willem ii": (51.5419, 5.0672, "Europe/Amsterdam"),  # Koning Willem II Stadion
    "nac breda": (51.5944, 4.7692, "Europe/Amsterdam"),  # Rat Verlegh Stadion
    "almere city fc": (52.3939, 5.2389, "Europe/Amsterdam"),  # Yanmar Stadion
    "rkc waalwijk": (51.6853, 5.0917, "Europe/Amsterdam"),  # Mandemakers Stadion
    # 荷乙 Eerste Divisie 2025/26 (主要示例)
    "ado den haag": (52.0628, 4.3831, "Europe/Amsterdam"),  # Bingoal Stadion (Cars Jeans Stadion)
    "almere city fc": (52.3939, 5.2389, "Europe/Amsterdam"),  # Yanmar Stadion
    "sc cambuur": (53.2053, 5.8139, "Europe/Amsterdam"),  # Kooi Stadion (新球場)
    "de graafschap": (51.9589, 6.3117, "Europe/Amsterdam"),  # De Vijverberg
    "fc den bosch": (51.7108, 5.3031, "Europe/Amsterdam"),  # De Vliert
    "fc dordrecht": (51.8089, 4.6889, "Europe/Amsterdam"),  # Matchoholic Stadion (Riwal Hoogwerkers Stadion)
    "fc eindhoven": (51.4417, 5.4789, "Europe/Amsterdam"),  # Jan Louwers Stadion
    "fc emmen": (52.7694, 6.9464, "Europe/Amsterdam"),  # De Oude Meerdijk
    "helmond sport": (51.4711, 5.6686, "Europe/Amsterdam"),  # SolarUnie Stadion
    "jong ajax": (52.3142, 4.9419, "Europe/Amsterdam"),  # Johan Cruyff Arena (或 Sportpark De Toekomst)
    "jong az alkmaar": (52.6128, 4.7422, "Europe/Amsterdam"),  # AFAS Trainingscomplex
    "jong psv": (51.4417, 5.4678, "Europe/Amsterdam"),  # PSV Campus De Herdgang
    "jong fc utrecht": (52.0814, 5.1458, "Europe/Amsterdam"),  # Sportcomplex Zoudenbalch
    "mvvm maastricht": (50.8594, 5.6869, "Europe/Amsterdam"),  # De Geusselt
    "roda jc kerkrade": (50.8572, 6.0939, "Europe/Amsterdam"),  # Parkstad Limburg Stadion
    "rkc waalwijk": (51.6853, 5.0917, "Europe/Amsterdam"),  # Mandemakers Stadion
    "top oss": (51.7650, 5.5289, "Europe/Amsterdam"),  # Frans Heesen Stadion
    "vvv-venlo": (51.3500, 6.1792, "Europe/Amsterdam"),  # Covebo Stadion - De Koel
    "vitesse": (51.9625, 5.8928, "Europe/Amsterdam"),  # GelreDome
    "willem ii": (51.5419, 5.0672, "Europe/Amsterdam"),  # Koning Willem II Stadion
    
    # 荷甲 Eredivisie 2025/26
    "阿積士": (52.3142, 4.9419, "Europe/Amsterdam"),            # Ajax - Johan Cruyff Arena
    "PSV燕豪芬": (51.4417, 5.4678, "Europe/Amsterdam"),          # PSV Eindhoven - Philips Stadion
    "飛燕諾": (51.9219, 4.5233, "Europe/Amsterdam"),             # Feyenoord - Stadion Feijenoord (De Kuip)
    "阿爾克馬爾": (52.6128, 4.7422, "Europe/Amsterdam"),         # AZ Alkmaar - AFAS Stadion
    "阿爾克馬爾女足": (52.6128, 4.7422, "Europe/Amsterdam"),         # AZ Alkmaar - AFAS Stadion
    "特溫特": (52.2367, 6.8372, "Europe/Amsterdam"),             # FC Twente - De Grolsch Veste
    "烏德勒支": (52.0781, 5.1456, "Europe/Amsterdam"),           # FC Utrecht - Stadion Galgenwaard
    "前進之鷹": (52.2206, 6.0011, "Europe/Amsterdam"),           # Go Ahead Eagles - De Adelaarshorst
    "赫拉克勒斯": (52.3389, 6.6511, "Europe/Amsterdam"),         # Heracles Almelo - Erve Asito
    "茲沃勒": (52.5158, 6.1194, "Europe/Amsterdam"),             # PEC Zwolle - MAC³PARK Stadion
    "施禾利": (52.5125, 6.0944, "Europe/Amsterdam"),
    "幸運薛達": (50.9978, 5.8447, "Europe/Amsterdam"),         # Fortuna Sittard - Fortuna Sittard Stadion
    "尼美根": (51.8239, 5.8347, "Europe/Amsterdam"),             # NEC Nijmegen - Goffertstadion
    "奈梅亨": (51.8239, 5.8347, "Europe/Amsterdam"),             # NEC Nijmegen - Goffertstadion
    "海倫芬": (52.9583, 5.9342, "Europe/Amsterdam"),             # SC Heerenveen - Abe Lenstra Stadion
    "鹿特丹斯巴達": (51.9194, 4.4344, "Europe/Amsterdam"),       # Sparta Rotterdam - Het Kasteel (Sparta Stadion)
    "格羅寧根": (53.2061, 6.5914, "Europe/Amsterdam"),           # FC Groningen - Euroborg
    "威廉二世": (51.5419, 5.0672, "Europe/Amsterdam"),           # Willem II - Koning Willem II Stadion
    "NAC": (51.5944, 4.7692, "Europe/Amsterdam"),            # NAC Breda - Rat Verlegh Stadion
    "阿爾梅勒": (52.3939, 5.2389, "Europe/Amsterdam"),         # Almere City FC - Yanmar Stadion
    "阿梅爾城": (52.3939, 5.2389, "Europe/Amsterdam"),         # Almere City FC - Yanmar Stadion
    "瓦爾韋克": (51.6853, 5.0917, "Europe/Amsterdam"),           # RKC Waalwijk - Mandemakers Stadion
    "荷華高斯": (52.0705, 4.3007, "Europe/Amsterdam"),
    "川迪": (52.2394, 6.8378, "Europe/Amsterdam"),
    # 荷乙 Eerste Divisie 2025/26
    "海牙ADO": (52.0628, 4.3831, "Europe/Amsterdam"),            # ADO Den Haag - Bingoal Stadion (Cars Jeans Stadion)
    "甘堡爾": (53.2053, 5.8139, "Europe/Amsterdam"),             # SC Cambuur - Kooi Stadion (新球場)
    "德格拉夫夏普": (51.9589, 6.3117, "Europe/Amsterdam"),       # De Graafschap - De Vijverberg
    "丹保殊": (51.7108, 5.3031, "Europe/Amsterdam"),           # FC Den Bosch - De Vliert
    "多德勒支": (51.8089, 4.6889, "Europe/Amsterdam"),         # FC Dordrecht - Matchoholic Stadion (Riwal Hoogwerkers Stadion)
    "燕豪芬FC": (51.4417, 5.4789, "Europe/Amsterdam"),           # FC Eindhoven - Jan Louwers Stadion
    "恩門": (52.7694, 6.9464, "Europe/Amsterdam"),               # FC Emmen - De Oude Meerdijk
    "赫爾蒙德體育": (51.4711, 5.6686, "Europe/Amsterdam"),       # Helmond Sport - SolarUnie Stadion
    "阿積士青年隊": (52.3142, 4.9419, "Europe/Amsterdam"),       # Jong Ajax - Johan Cruyff Arena (或 Sportpark De Toekomst)
    "阿爾克馬爾青年隊": (52.6128, 4.7422, "Europe/Amsterdam"),   # Jong AZ Alkmaar - AFAS Trainingscomplex
    "PSV青年隊": (51.4417, 5.4678, "Europe/Amsterdam"),          # Jong PSV - PSV Campus De Herdgang
    "烏德勒支青年隊": (52.0814, 5.1458, "Europe/Amsterdam"),     # Jong FC Utrecht - Sportcomplex Zoudenbalch
    "馬斯特里赫特MVV": (50.8594, 5.6869, "Europe/Amsterdam"),    # MVV Maastricht - De Geusselt
    "洛達": (50.8572, 6.0939, "Europe/Amsterdam"),             # Roda JC Kerkrade - Parkstad Limburg Stadion
    "瓦爾韋克": (51.6853, 5.0917, "Europe/Amsterdam"),           # RKC Waalwijk - Mandemakers Stadion
    "奧斯": (51.7650, 5.5289, "Europe/Amsterdam"),               # TOP Oss - Frans Heesen Stadion
    "芬洛": (51.3500, 6.1792, "Europe/Amsterdam"),            # VVV-Venlo - Covebo Stadion - De Koel
    "維迪斯": (51.9625, 5.8928, "Europe/Amsterdam"),             # Vitesse - GelreDome
    "威廉二世": (51.5419, 5.0672, "Europe/Amsterdam"),            # Willem II - Koning Willem II Stadion
    "迪加史卓普": (51.9597, 6.2889, "Europe/Amsterdam"),
    "靴蒙特": (51.4711, 5.6686, "Europe/Amsterdam"),  # SolarUnie Stadion
    "SC坎布爾": (53.2058, 5.8075, "Europe/Amsterdam"),
    # 荷丙
    "hhc hardenberg": (52.5672725, 6.5882764,"Europe/Amsterdam" ), 
    # 瑞士
    "etoile carouge": (46.1855, 6.1496, "Europe/Zurich"),
    
    # 比甲 Belgian Pro League 2025/26
    "rsc anderlecht": (50.8342, 4.2983, "Europe/Brussels"),  # Lotto Park
    "Sportvereniging Zulte Waregem": (50.883056, 3.428889, "Europe/Brussels"),  # Lotto Park
    "royal antwerp fc": (51.2328, 4.4522, "Europe/Brussels"),  # Bosuilstadion
    "cercle brugge": (51.193272, 3.180583, "Europe/Brussels"),  # Jan Breydel Stadium (共享)
    "club brugge": (51.1947, 3.1822, "Europe/Brussels"),  # Jan Breydel Stadium
    "kv kortrijk": (50.8292, 3.2528, "Europe/Brussels"),  # Guldensporen Stadion
    "krc genk": (50.9606, 5.5036, "Europe/Brussels"),  # Cegeka Arena
    "kaa gent": (51.0167, 3.7339, "Europe/Brussels"),  # KAA Gent Arena (Ghelamco)
    "kv mechelen": (51.0372, 4.4867, "Europe/Brussels"),  # AFAS Stadion
    "oudergem union saint-gilloise": (50.8339, 4.3950, "Europe/Brussels"),  # Stade Joseph Mariën
    "royal charleroi sc": (50.4142, 4.4444, "Europe/Brussels"),  # Stade du Pays de Charleroi
    "standard liege": (50.6100, 5.5431, "Europe/Brussels"),  # Stade Maurice Dufrasne
    "kvc westerlo": (51.0856, 4.9283, "Europe/Brussels"),  # Het Kuipje
    "oh leuven": (50.8681, 4.6950, "Europe/Brussels"),  # Den Dreef
    "kv oostende": (51.2122, 2.8869, "Europe/Brussels"),  # Diaz Arena
    "dender": (50.9642, 4.0269, "Europe/Brussels"),  # Dender Football Complex (或 Van Roy)
    "sint-truidense vv": (50.8150, 5.1669, "Europe/Brussels"),  # Stayen
    # 比甲 Belgian Pro League 2025/26
    "安德列治": (50.8342, 4.2983, "Europe/Brussels"),           # RSC Anderlecht - Lotto Park
    "華雷根": (50.8500, 4.3500, "Europe/Brussels"), # Sportvereniging Zulte Waregem - Regenboogstadion (或 Lotto Park 臨時)
    "安特衛普": (51.2328, 4.4522, "Europe/Brussels"),       # Royal Antwerp FC - Bosuilstadion
    "布魯日舒高": (51.193272, 3.180583, "Europe/Brussels"),       # Cercle Brugge - Jan Breydel Stadium (共享)
    "布魯日": (51.1947, 3.1822, "Europe/Brussels"),             # Club Brugge - Jan Breydel Stadium
    "科特賴克": (50.8292, 3.2528, "Europe/Brussels"),           # KV Kortrijk - Guldensporen Stadion
    "亨克": (50.9606, 5.5036, "Europe/Brussels"),               # KRC Genk - Cegeka Arena
    "真特": (51.0167, 3.7339, "Europe/Brussels"),               # KAA Gent - KAA Gent Arena (Ghelamco)
    "梅赫倫": (51.0372, 4.4867, "Europe/Brussels"),             # KV Mechelen - AFAS Stadion
    "聖基萊斯聯": (50.8339, 4.3950, "Europe/Brussels"),       # Oudergem Union Saint-Gilloise - Stade Joseph Mariën
    "查內爾": (50.4142, 4.4444, "Europe/Brussels"),           # Royal Charleroi SC - Stade du Pays de Charleroi
    "標準列治": (50.6100, 5.5431, "Europe/Brussels"),           # Standard Liège - Stade Maurice Dufrasne
    "韋斯達路": (51.0856, 4.9283, "Europe/Brussels"),           # KVC Westerlo - Het Kuipje
    "奧特海維利": (50.8681, 4.6950, "Europe/Brussels"),      # OH Leuven - Den Dreef
    "奧斯滕德": (51.2122, 2.8869, "Europe/Brussels"),           # KV Oostende - Diaz Arena
    "登達": (50.9642, 4.0269, "Europe/Brussels"),             # Dender - Dender Football Complex (或 Van Roy)
    "聖圖爾登": (50.8150, 5.1669, "Europe/Brussels"),          # Sint-Truidense VV - Stayen
    "拉路維爾": (50.477503, 4.201314, "Europe/Brussels"),          # Sint-Truidense VV - Stayen

    
    
    # 澳職聯 A-League Men 2025/26
    "adelaide united": (-34.9229, 138.6370, "Australia/Sydney"),  # Coopers Stadium
    "阿德萊德聯": (-34.9229, 138.6370, "Australia/Sydney"),  # Coopers Stadium
    "auckland fc": (-36.9187, 174.8120, "Pacific/Auckland"),  # Go Media Stadium (Mt Smart)
    "奧克蘭FC": (-36.9187, 174.8120, "Pacific/Auckland"),  # Go Media Stadium (Mt Smart)
    "brisbane roar": (-27.4650, 153.0090, "Australia/Sydney"),  # Suncorp Stadium (Lang Park)
    "布里斯本獅吼": (-27.4650, 153.0090, "Australia/Sydney"),  # Suncorp Stadium (Lang Park)
    "布里斯班獅吼": (-27.4650, 153.0090, "Australia/Sydney"),  # Suncorp Stadium (Lang Park)
    "central coast mariners": (-33.4286, 151.3417, "Australia/Sydney"),  # Industree Group Stadium (Gosford)
    "中岸水手": (-33.4286, 151.3417, "Australia/Sydney"),  # Industree Group Stadium (Gosford)
    "中岸水手女足": (-33.4286, 151.3417, "Australia/Sydney"),  # Industree Group Stadium (Gosford)
    "macarthur fc": (-34.0389, 150.8033, "Australia/Sydney"),  # Campbelltown Stadium
    "麥克阿瑟FC": (-34.0389, 150.8033, "Australia/Sydney"),  # Campbelltown Stadium
    "melbourne city": (-37.8250, 144.9837, "Australia/Sydney"),  # AAMI Park
    "墨爾本城": (-37.8250, 144.9837, "Australia/Sydney"),  # AAMI Park (共享)
    "melbourne victory": (-37.8250, 144.9837, "Australia/Sydney"),  # AAMI Park (共享)
    "墨爾本勝利": (-37.8250, 144.9837, "Australia/Sydney"),  # AAMI Park (共享)
    "墨爾本勝利女足": (-37.8250, 144.9837, "Australia/Sydney"),  # AAMI Park (共享)
    "newcastle jets": (-32.9189, 151.7267, "Australia/Sydney"),  # McDonald Jones Stadium
    "紐卡素噴射機": (-32.9189, 151.7267, "Australia/Sydney"),  # McDonald Jones Stadium
    "紐卡素噴射機女足": (-32.9189, 151.7267, "Australia/Sydney"),  # McDonald Jones Stadium
    "perth glory": (-31.9458, 115.8697, "Australia/Perth"),  # HBF Park (Perth Rectangular Stadium)
    "珀斯光輝": (-31.9458, 115.8697, "Australia/Perth"),  # HBF Park (Perth Rectangular Stadium)
    "sydney fc": (-33.8892, 151.2253, "Australia/Sydney"),  # Allianz Stadium (Sydney Football Stadium)
    "悉尼FC": (-33.8892, 151.2253, "Australia/Sydney"),  # Allianz Stadium (Sydney Football Stadium)
    "FC悉尼": (-33.8892, 151.2253, "Australia/Sydney"),  # Allianz Stadium (Sydney Football Stadium)
    "wellington phoenix": (-41.2730, 174.7850, "Pacific/Auckland"),  # Sky Stadium
    "威靈頓鳳凰": (-41.2730, 174.7850, "Pacific/Auckland"),  # Sky Stadium
    "威靈頓鳳凰女足": (-41.2730, 174.7850, "Pacific/Auckland"),  # Sky Stadium
    "western sydney wanderers": (-33.8078, 150.9944, "Australia/Sydney"),  # CommBank Stadium
    "西悉尼流浪者": (-33.8078, 150.9944, "Australia/Sydney"),  # CommBank Stadium
    # 葡超 Primeira Liga 2025/26
    "fc porto": (41.1618, -8.5839, "Europe/Lisbon"),  # Estádio do Dragão
    "sl benfica": (38.7527, -9.1847, "Europe/Lisbon"),  # Estádio da Luz
    "sporting cp": (38.7612, -9.1608, "Europe/Lisbon"),  # Estádio José Alvalade
    "sc braga": (41.5625, -8.3972, "Europe/Lisbon"),  # Estádio Municipal de Braga
    "vitoria guimaraes": (41.4458, -8.2992, "Europe/Lisbon"),  # Estádio D. Afonso Henriques
    "fc famalicao": (41.4019, -8.5228, "Europe/Lisbon"),  # Estádio Municipal 22 de Junho
    "rio ave": (41.3617, -8.7394, "Europe/Lisbon"),  # Estádio dos Arcos
    "cd santa clara": (37.7667, -25.6667, "Europe/Lisbon"),  # Estádio de São Miguel (亞速爾群島)
    "gil vicente": (41.5472, -8.6167, "Europe/Lisbon"),  # Estádio Cidade de Barcelos
    "moreirense": (41.3736, -8.3833, "Europe/Lisbon"),  # Estádio Comendador Joaquim de Almeida Freitas
    "boavista": (41.1619, -8.6428, "Europe/Lisbon"),  # Estádio do Bessa
    "estrela amadora": (38.7514, -9.2311, "Europe/Lisbon"),  # Estádio José Gomes
    "casa pia": (39.0833, -9.3333, "Europe/Lisbon"),  # Estádio Municipal de Rio Maior (臨時主場)
    "avc aves": (41.3667, -8.4167, "Europe/Lisbon"),  # Estádio do CD Aves (或類似)
    "gd chaves": (41.7556, -7.4667, "Europe/Lisbon"),  # Estádio Municipal Eng. Manuel Branco Teixeira
    "fc arouca": (40.9306, -8.4667, "Europe/Lisbon"),  # Estádio Municipal de Arouca
    "estoril praia": (38.7508, -9.4075, "Europe/Lisbon"),  # Estádio António Coimbra da Mota
    "nacional": (32.6667, -16.9333, "Europe/Lisbon"),  # Estádio da Madeira (馬德拉島)
    # 葡超 Primeira Liga 2025/26
    "法倫斯": (41.1333, -8.6167, "Europe/Lisbon"),
    "波圖": (41.1618, -8.5839, "Europe/Lisbon"),               # FC Porto - Estádio do Dragão
    "賓菲加": (38.7527, -9.1847, "Europe/Lisbon"),             # SL Benfica - Estádio da Luz
    "士砵亭": (38.7612, -9.1608, "Europe/Lisbon"),             # Sporting CP - Estádio José Alvalade
    "艾華卡": (38.7544, -9.2322, "Europe/Lisbon"),
    "布拉加": (41.5625, -8.3972, "Europe/Lisbon"),             # SC Braga - Estádio Municipal de Braga
    "甘馬雷斯": (41.4458, -8.2992, "Europe/Lisbon"),   # Vitória Guimarães - Estádio D. Afonso Henriques
    "法馬利卡奧": (41.4019, -8.5228, "Europe/Lisbon"),           # FC Famalicão - Estádio Municipal 22 de Junho
    "里奧艾維": (41.3617, -8.7394, "Europe/Lisbon"),           # Rio Ave - Estádio dos Arcos
    "辛達卡拉": (37.7667, -25.6667, "Europe/Lisbon"),          # CD Santa Clara - Estádio de São Miguel (亞速爾群島)
    "基維辛迪": (41.5472, -8.6167, "Europe/Lisbon"),         # Gil Vicente - Estádio Cidade de Barcelos
    "摩里倫斯": (41.3736, -8.3833, "Europe/Lisbon"),           # Moreirense - Estádio Comendador Joaquim de Almeida Freitas
    "博阿維斯塔": (41.1619, -8.6428, "Europe/Lisbon"),         # Boavista - Estádio do Bessa
    "艾馬多拉": (38.7514, -9.2311, "Europe/Lisbon"),       # Estrela Amadora - Estádio José Gomes
    "卡薩比亞": (39.0833, -9.3333, "Europe/Lisbon"),           # Casa Pia - Estádio Municipal de Rio Maior (臨時主場)
    "AVS": (41.3667, -8.4167, "Europe/Lisbon"),             # AVC Aves - Estádio do CD Aves (或類似)
    "查維斯": (41.7556, -7.4667, "Europe/Lisbon"),             # GD Chaves - Estádio Municipal Eng. Manuel Branco Teixeira
    "阿羅卡": (40.9306, -8.4667, "Europe/Lisbon"),             # FC Arouca - Estádio Municipal de Arouca
    "艾斯杜尼": (38.7508, -9.4075, "Europe/Lisbon"),         # Estoril Praia - Estádio António Coimbra da Mota
    "國民隊": (32.6667, -16.9333, "Europe/Lisbon"),               # Nacional - Estádio da Madeira (馬德拉島)
    
    # 俄羅斯超級聯賽 Russian Premier League 2025/26
    "巴爾迪卡": (54.7167, 20.5167, "Europe/Kaliningrad"),
    "阿克隆陶爾亞蒂": (53.5167, 49.4167, "Europe/Samara"),
    "莫斯科火車頭": (55.7894, 37.5872, "Europe/Moscow"),
    "FC奧倫堡": (51.7667, 55.1000, "Europe/Samara"),
    "羅斯托夫": (47.2225, 39.7203, "Europe/Moscow"),
    "馬哈奇卡拉戴拿模": (42.9667, 47.5126, "Europe/Moscow"),
    "圖拉兵工廠": (54.1833, 37.6167, "Europe/Moscow"),
    "辛尼特": (59.9730, 30.2215, "Europe/Moscow"),  # Gazprom Arena
    "spartak moscow": (55.8181, 37.4408, "Europe/Moscow"),  # Otkritie Arena (Spartak Stadium)
    "lokomotiv moscow": (55.8039, 37.7414, "Europe/Moscow"),  # RZD Arena
    "莫斯科中央陸軍": (55.7920, 37.5160, "Europe/Moscow"),  # VEB Arena
    "莫斯科戴拿模": (55.7920, 37.5600, "Europe/Moscow"),  # VTB Arena
    "卡斯洛達": (45.0436, 39.0292, "Europe/Moscow"),  # Krasnodar Stadium
    "fc rostov": (47.2089, 39.7389, "Europe/Moscow"),  # Rostov Arena
    "akhmat grozny": (43.3236, 45.7433, "Europe/Moscow"),  # Akhmat Arena
    "krylia sovetov samara": (53.2100, 50.1500, "Europe/Moscow"),  # Solidarnost Arena
    "orenburg": (51.7722, 55.1056, "Europe/Moscow"),  # Gazovik Stadium
    "fakel voronezh": (51.6611, 39.2417, "Europe/Moscow"),  # Tsentralnyi Profsoyuz Stadion
    "pari nizhny novgorod": (56.3247, 43.9389, "Europe/Moscow"),  # Nizhny Novgorod Stadium
    "akron tolyatti": (53.5028, 49.4439, "Europe/Moscow"),  # Kristall Stadium (或 Solidarnost 共享)
    "rubin kazan": (55.8211, 49.1606, "Europe/Moscow"),  # Ak Bars Arena
    "fc orenburg": (51.7722, 55.1056, "Europe/Moscow"),  # Gazovik Stadium (重複保留最新)
    "fc sochi": (43.4028, 39.9556, "Europe/Moscow"),  # Fisht Olympic Stadium
    # 沙特職業聯賽 Saudi Pro League 2025/26
    "al hilal": (24.7136, 46.6864, "Asia/Riyadh"),  # Kingdom Arena (主要主場)
    "al nassr": (24.6627, 46.7390, "Asia/Riyadh"),  # Al-Awwal Park
    "al ahli": (21.5493, 39.1939, "Asia/Riyadh"),  # King Abdullah Sports City (共享)
    "al taawoun": (26.3789, 43.9450, "Asia/Riyadh"),  # King Abdullah Sport City Stadium (Buraidah)
    "al ettifaq": (26.4089, 50.0939, "Asia/Riyadh"),  # Prince Mohamed bin Fahd Stadium (Dammam)
    "al fateh": (26.3789, 49.9700, "Asia/Riyadh"),  # Al-Fateh Club Stadium (Al-Hasa)
    "al shabab": (24.7136, 46.6864, "Asia/Riyadh"),  # Kingdom Arena (或 Prince Faisal bin Fahd)
    "al faisaly": (24.4667, 39.6167, "Asia/Riyadh"),  # Al Majma'ah Sports City (Harmah)
    "al qadsiah": (26.3789, 50.0939, "Asia/Riyadh"),  # Prince Saud bin Jalawi Stadium (Khobar)
    "al riyadh": (24.7136, 46.6864, "Asia/Riyadh"),  # Prince Faisal bin Fahd Stadium (Riyadh)
    "damac": (18.2833, 42.5667, "Asia/Riyadh"),  # Damac Club Stadium (Khamis Mushait)
    "al khaleej": (27.5167, 49.5667, "Asia/Riyadh"),  # Al-Khaleej Club Stadium (Saihat)
    "al orobah": (18.2833, 42.5667, "Asia/Riyadh"),  # Al-Orobah Club Stadium (Sakakah)
    "al akhdoud": (17.5667, 44.2167, "Asia/Riyadh"),  # Prince Hathloul Stadium (Najran)
    "al najma": (24.4667, 39.6167, "Asia/Riyadh"),  # Al-Najma Club Stadium (Unaizah)
    "neom": (28.3167, 34.8333, "Asia/Riyadh"),  # NEOM Stadium (新球場，預計座標)
    "al hazem": (25.8667, 43.4833, "Asia/Riyadh"),  # Al-Hazem Club Stadium (Ar Rass)

    # 沙特職業聯賽 Saudi Pro League 2025/26
    "希拉爾": (24.7136, 46.6864, "Asia/Riyadh"),              # Al Hilal - Kingdom Arena (主要主場)
    "納斯爾": (24.6627, 46.7390, "Asia/Riyadh"),              # Al Nassr - Al-Awwal Park
    "塔雲": (26.3789, 43.9450, "Asia/Riyadh"),                 # Al Taawoun - King Abdullah Sport City Stadium (Buraidah)
    "伊蒂法克": (26.4089, 50.0939, "Asia/Riyadh"),             # Al Ettifaq - Prince Mohamed bin Fahd Stadium (Dammam)
    "法特赫": (26.3789, 49.9700, "Asia/Riyadh"),               # Al Fateh - Al-Fateh Club Stadium (Al-Hasa)
    "艾沙比": (24.7136, 46.6864, "Asia/Riyadh"),               # Al Shabab - Kingdom Arena (或 Prince Faisal bin Fahd)
    "費薩利": (24.4667, 39.6167, "Asia/Riyadh"),               # Al Faisaly - Al Majma'ah Sports City (Harmah)
    "艾卡迪沙": (26.3789, 50.0939, "Asia/Riyadh"),               # Al Qadsiah - Prince Saud bin Jalawi Stadium (Khobar)
    "利雅得": (24.7136, 46.6864, "Asia/Riyadh"),               # Al Riyadh - Prince Faisal bin Fahd Stadium (Riyadh)
    "達馬克FC": (18.2833, 42.5667, "Asia/Riyadh"),               # Damac - Damac Club Stadium (Khamis Mushait)
    "卡赫利": (27.5167, 49.5667, "Asia/Riyadh"),               # Al Khaleej - Al-Khaleej Club Stadium (Saihat)
    "奧魯巴": (18.2833, 42.5667, "Asia/Riyadh"),               # Al Orobah - Al-Orobah Club Stadium (Sakakah)
    "阿赫杜德": (17.5667, 44.2167, "Asia/Riyadh"),             # Al Akhdoud - Prince Hathloul Stadium (Najran)
    "納吉馬": (24.4667, 39.6167, "Asia/Riyadh"),               # Al Najma - Al-Najma Club Stadium (Unaizah)
    "尼奧姆": (28.3167, 34.8333, "Asia/Riyadh"),               # Neom - NEOM Stadium (新球場，預計座標)
    "艾哈森": (25.8667, 43.4833, "Asia/Riyadh"),                # Al Hazem - Al-Hazem Club Stadium (Ar Rass)
    "艾拿積馬": (24.7136, 46.6864, "Asia/Riyadh"),
    "艾科魯特":(25.862222, 43.502361, "Asia/Riyadh"),
    "阿爾華達": (21.5493, 39.1939, "Asia/Riyadh"),
    # 阿聯酋職業聯賽 UAE Pro League 2025/26
    "shabab al ahli": (25.2747, 55.3486, "Asia/Dubai"),  # Rashid Stadium
    "al wasl": (25.2142, 55.3178, "Asia/Dubai"),  # Zabeel Stadium
    "al ain": (24.2458, 55.7167, "Asia/Dubai"),  # Hazza bin Zayed Stadium
    "艾阿恩":(24.2458, 55.7167, "Asia/Dubai"),  # Hazza bin Zayed Stadium
    "al jazira": (24.4522, 54.3922, "Asia/Dubai"),  # Mohammed bin Zayed Stadium
    "al wahda": (24.4711, 54.3706, "Asia/Dubai"),  # Al Nahyan Stadium
    "sharjah": (25.3332, 55.4196, "Asia/Dubai"),  # Sharjah Stadium
    "ajman": (25.4047, 55.4444, "Asia/Dubai"),  # Rashid bin Saeed Stadium
    "baniyas": (24.3417, 54.5333, "Asia/Dubai"),  # Baniyas Stadium
    "khor fakkan": (25.3333, 56.3500, "Asia/Dubai"),  # Saqr bin Mohammed Al Qasimi Stadium
    "al bataeh": (25.3333, 55.6333, "Asia/Dubai"),  # Al Bataeh Stadium
    "al nasr": (25.2700, 55.3200, "Asia/Dubai"),  # Al Maktoum Stadium
    "ittihad kalba": (25.0000, 56.3500, "Asia/Dubai"),  # Ittihad Kalba Stadium
    "al orooba": (25.6667, 55.7833, "Asia/Dubai"),  # Al Orooba Stadium
    "al dhafra": (23.7167, 53.7167, "Asia/Dubai"),  # Al Dhafra Stadium (若適用)
    "艾迪哈夫拉": (24.4711, 54.3706, "Asia/Dubai"),    
    "艾因": (24.2458, 55.7167, "Asia/Dubai"),  # Al Ain - Hazza bin Zayed Stadium
    "艾華斯爾": (25.2142, 55.3178, "Asia/Dubai"),  # Al Wasl - Zabeel Stadium
    "艾納斯爾": (25.2700, 55.3200, "Asia/Dubai"),  # Al Nasr - Al Maktoum Stadium
    "艾爾華達": (24.4711, 54.3706, "Asia/Dubai"),  # Al Wahda - Al Nahyan Stadium
    "艾積澤拉": (24.4522, 54.3922, "Asia/Dubai"),  # Al Jazira - Mohammed bin Zayed Stadium
    "沙迦": (25.3332, 55.4196, "Asia/Dubai"),  # Sharjah - Sharjah Stadium
    "賓尼耶斯": (24.3417, 54.5333, "Asia/Dubai"),  # Baniyas Stadium
    "阿治曼": (25.4047, 55.4444, "Asia/Dubai"),  # Ajman - Rashid bin Saeed Stadium
    "班尼亞斯": (24.3417, 54.5333, "Asia/Dubai"),  # Baniyas - Baniyas Stadium
    "哈塔": (24.8333, 56.1333, "Asia/Dubai"),  # Hatta - Hamdan bin Rashid Stadium
    "卡爾巴": (25.0000, 56.3500, "Asia/Dubai"),  # Ittihad Kalba - Ittihad Kalba Stadium
    "迪拜城": (25.2048, 55.2708, "Asia/Dubai"),  # Dibba Al Fujairah (或 Dibba Al Hisn) - Dibba Al Fujairah Club Stadium
    "艾奧羅巴": (25.6667, 55.7833, "Asia/Dubai"),  # Al Orooba - Al Orooba Stadium
    "艾巴泰": (25.3333, 55.6333, "Asia/Dubai"),  # Al Bataeh - Al Bataeh Stadium
    "艾查捷拉": (24.4522, 54.3922, "Asia/Dubai"),
    
    # 泰國職業聯賽 Thai League 1 2025/26
    "bangkok united": (14.0520, 100.5990, "Asia/Bangkok"),  # Thammasat Stadium (Pathum Thani)
    "曼谷聯": (14.0520, 100.5990, "Asia/Bangkok"),  # Thammasat Stadium (Pathum Thani)
    "buriram united": (14.9520, 103.1020, "Asia/Bangkok"),  # Chang Arena
    "武里南聯": (14.9520, 103.1020, "Asia/Bangkok"),  # Chang Arena
    "port fc": (13.7150, 100.5580, "Asia/Bangkok"),  # PAT Stadium
    "泰港": (13.7150, 100.5580, "Asia/Bangkok"),  # PAT Stadium
    "bg pathum united": (13.9810, 100.5360, "Asia/Bangkok"),  # BG Stadium (True BG Stadium)
    "巴吞聯": (13.9810, 100.5360, "Asia/Bangkok"),  # BG Stadium (True BG Stadium)
    "muangthong united": (13.9170, 100.5470, "Asia/Bangkok"),  # Thunderdome Stadium (SCG Stadium)
    "蒙通聯": (13.9170, 100.5470, "Asia/Bangkok"),  # Thunderdome Stadium (SCG Stadium)
    "chiangrai united": (19.9560, 99.8750, "Asia/Bangkok"),  # Singha Chiangrai Stadium
    "清萊聯": (19.9560, 99.8750, "Asia/Bangkok"),  # Singha Chiangrai Stadium
    "chonburi": (13.3980, 100.9930, "Asia/Bangkok"),  # Chonburi Stadium
    "春武里": (13.3980, 100.9930, "Asia/Bangkok"),  # Chonburi Stadium
    "lamphun warrior": (18.5700, 99.0100, "Asia/Bangkok"),  # Mae Guang Stadium
    "南奔勇士": (18.5700, 99.0100, "Asia/Bangkok"),  # Mae Guang Stadium
    "nakhon ratchasima": (14.9300, 102.0700, "Asia/Bangkok"),  # 80th Birthday Stadium
    "那空拉查斯馬": (14.9300, 102.0700, "Asia/Bangkok"),  # 80th Birthday Stadium
    "prachuap": (11.8180, 99.7900, "Asia/Bangkok"),  # Sam Ao Stadium
    "巴蜀": (11.8180, 99.7900, "Asia/Bangkok"),  # Sam Ao Stadium
    "ratchaburi": (13.6360, 99.8200, "Asia/Bangkok"),  # Dragon Solar Park
    "拉查布里": (13.6360, 99.8200, "Asia/Bangkok"),  # Dragon Solar Park
    "rayong": (12.6780, 101.2800, "Asia/Bangkok"),  # Rayong Provincial Stadium
    "羅勇": (12.6780, 101.2800, "Asia/Bangkok"),  # Rayong Provincial Stadium
    "sukhothai": (17.0100, 99.8200, "Asia/Bangkok"),  # Thung Thalay Luang Stadium
    "素可泰": (17.0100, 99.8200, "Asia/Bangkok"),  # Thung Thalay Luang Stadium
    "uthai thani": (15.3800, 100.0300, "Asia/Bangkok"),  # Uthai Thani Provincial Stadium
    "烏泰他尼": (15.3800, 100.0300, "Asia/Bangkok"),  # Uthai Thani Provincial Stadium
    "ayutthaya united": (14.3500, 100.6000, "Asia/Bangkok"),  # Ayutthaya Provincial Stadium
    "大城聯": (14.3500, 100.6000, "Asia/Bangkok"),  # Ayutthaya Provincial Stadium
    "kanchanaburi": (14.0200, 99.5300, "Asia/Bangkok"),  # Kanchanaburi Stadium
    "北碧府動力": (14.0200, 99.5300, "Asia/Bangkok"),  # Kanchanaburi Stadium
    "Thonburi United": (13.724254, 100.344909 , "Asia/Bangkok"),
    "那拉聯": (6.4333, 101.8167, "Asia/Bangkok"), # Nara United - Narathiwat PAO Stadium
    "沙敦": (6.6333, 101.2500, "Asia/Bangkok"), # Satun - Satun PAO Stadium
    "也拉FC": (6.5333, 101.2833, "Asia/Bangkok"), # Yala FC - Yala Provincial Stadium
    "薩穆聯": (9.5333, 99.9333, "Asia/Bangkok"), # Samui United - Samui Stadium
    "普吉安達曼": (7.8833, 98.4000, "Asia/Bangkok"), # Phuket Andaman - Surakul Stadium
    "宋卡聯": (7.2000, 100.6000, "Asia/Bangkok"), # Songkhla United - Tinsulanon Stadium
    "三育松幹城": (13.5333, 100.2667, "Asia/Bangkok"), # Samut Sakhon City - Samut Sakhon Provincial Stadium
    "通布里聯": (13.7333, 100.4833, "Asia/Bangkok"), # Thonburi United - Thonburi University Stadium
    "阿森普遜聯": (13.7500, 100.5167, "Asia/Bangkok"), # Assumption United - Assumption Thonburi University Stadium
    "三育松幹宋堪": (13.5333, 100.2667, "Asia/Bangkok"), # Samut Songkhram City - Samut Songkhram PAO Stadium
    "素攀武里": (14.5667, 100.6167, "Asia/Bangkok"), # Suphanburi - Suphan Buri Provincial Stadium
    "塔普魯昂聯": (13.9667, 99.5333, "Asia/Bangkok"), # Thap Luang United - Kanchanaburi Provincial Stadium
    "布拉帕聯": (13.1167, 100.9167, "Asia/Bangkok"), # Burapha United - Burapha University Stadium
    "海軍": (12.6667, 100.9333, "Asia/Bangkok"), # Navy - Sattahip Navy Stadium
    "班凱聯": (13.0833, 101.0000, "Asia/Bangkok"), # Bankhai United - Ban Khai District Stadium
    "關稅聯": (12.6667, 100.9333, "Asia/Bangkok"), # Customs United - Lad Krabang 54 Stadium
    "普魯克登聯": (13.0000, 101.2167, "Asia/Bangkok"), # Pluakdaeng United - Pluak Daeng Stadium
    "查喬恩紹高新科技": (13.4167, 101.0667, "Asia/Bangkok"), # Chachoengsao Hi-Tek - Chachoengsao Municipality Stadium
    "烏隆聯": (17.4167, 102.7833, "Asia/Bangkok"), # Udon United - Udon Thani Rajabhat University Stadium
    "美隆聯": (17.2000, 102.7833, "Asia/Bangkok"), # Muang Loei United - Loei Provincial Stadium
    "孔敬": (16.4167, 102.8333, "Asia/Bangkok"), # Khon Kaen - Khon Kaen Provincial Stadium
    "羅逸PB聯": (16.0667, 103.6500, "Asia/Bangkok"), # Roi Et PB United - Roi Et Provincial Stadium
    "烏隆班詹聯": (17.4167, 102.7833, "Asia/Bangkok"), # Udon Banjan United - Udon Thani Provincial Stadium
    "雅索通": (15.8000, 104.1500, "Asia/Bangkok"), # Yasothon - Yasothon Provincial Stadium
    "清邁FC": (18.7800, 98.9850, "Asia/Bangkok"), # Chiangmai - Chiang Mai Municipal Stadium
    "烏達拉迪": (17.6167, 100.1000, "Asia/Bangkok"), # Uttaradit - Uttaradit Provincial Stadium
    "披集聯": (16.8167, 100.2667, "Asia/Bangkok"), # Phichit United - Phichit Provincial Stadium
    "美曹聯": (18.8333, 98.9833, "Asia/Bangkok"), # Maejo United - Maejo University Stadium
    "那空美索聯": (16.8667, 99.1333, "Asia/Bangkok"), # Nakhon Mae Sot United - Nakhon Mae Sot Stadium
    "披實奴洛": (16.8167, 100.2667, "Asia/Bangkok"), # Phitsanulok - Phitsanulok Provincial Stadium
    "阿瑜陀耶聯": (14.3550, 100.5875, "Asia/Bangkok"), # Ayutthaya United - Ayutthaya Provincial Stadium
    "曼谷FC": (13.6750, 100.4722, "Asia/Bangkok"), # Bangkok - 72nd Anniversary Stadium
    "猜納犀鳥": (15.2333, 100.0500, "Asia/Bangkok"), # Chainat Hornbill - Khao Plong Stadium
    "占他武里FC": (12.6000, 102.1167, "Asia/Bangkok"), # Chanthaburi - Chanthaburi Province Stadium
    "清邁聯": (18.8061, 98.9833, "Asia/Bangkok"), # Chiangmai United - Chiang Mai Rajabhat University Stadium
    "卡塞薩特FC": (13.8000, 100.3167, "Asia/Bangkok"), # Kasetsart - Insee Chantarasatit Stadium
    "孔敬聯": (16.4167, 102.8333, "Asia/Bangkok"), # Khonkaen United - Khon Kaen PAO Stadium
    "馬哈薩拉坎FC": (16.1833, 103.3000, "Asia/Bangkok"), # Mahasarakham - Maha Sarakham Province Stadium
    "那空巴統聯": (13.8000, 100.0500, "Asia/Bangkok"), # Nakhon Pathom United - Nakhon Pathom Municipality Sport School Stadium
    "那空是聯": (8.4000, 99.9667, "Asia/Bangkok"), # Nakhon Si United - Nakhon Si Thammarat PAO Stadium
    "農武碧差亞FC": (17.1600, 100.0833, "Asia/Bangkok"), # Nongbua Pitchaya - Pitchaya Stadium
    "帕塔尼FC": (6.7000, 101.2500, "Asia/Bangkok"), # Pattani - Rainbow Stadium
    "芭堤雅聯": (12.9236, 100.9344, "Asia/Bangkok"), # Pattaya United - Nong Prue Stadium
    "帕瑞聯": (18.2000, 100.1500, "Asia/Bangkok"), # Phrae United - Huayma Stadium
    "警察特羅FC": (13.9167, 100.5833, "Asia/Bangkok"), # Police Tero - NT Stadium
    "拉西薩萊聯": (15.1167, 104.3333, "Asia/Bangkok"), # Rasisalai United - Sisaket Provincial Stadium
    "西薩格聯": (15.1167, 104.3333, "Asia/Bangkok"), # Sisaket United - Sri Nakhon Lamduan Stadium
    "宋卡FC": (7.0167, 100.4833, "Asia/Bangkok"), # Songkhla - Tinsulanonda Stadium
    "素攀武里FC": (14.5667, 100.6167, "Asia/Bangkok"), # Suphanburi - Suphan Buri Provincial Stadium
    "特拉特FC": (12.4000, 102.5167, "Asia/Bangkok"), # Trat - Trat Provincial Stadium
    "曼谷聯": (13.7563, 100.5018, "Asia/Bangkok"), # Bangkok - Various stadiums in Bangkok
    "北曼谷大學": (13.8675, 100.5833, "Asia/Bangkok"), # North Bangkok University - North Bangkok University Stadium
    "PTU巴吞他尼": (13.9167, 100.5333, "Asia/Bangkok"), # PTU Pathum Thani - Pathum Thani University Stadium
    "皇家空軍": (13.7833, 100.6167, "Asia/Bangkok"), # Royal Thai Air Force - Thupatemi Stadium
    "卡塞姆邦迪大學": (13.8167, 100.6667, "Asia/Bangkok"), # Kasem Bundit University - Kasem Bundit University Stadium
    "洛比里城": (14.8000, 100.6167, "Asia/Bangkok"), # Lopburi City - Lop Buri Stadium

    # 卡塔爾星級聯賽 Qatar Stars League 2025/26
    "al shahaniya": (25.2587, 51.5205, "Asia/Qatar"),  # Grand Hamad Stadium (常共用或臨時主場)
    "al sadd": (25.2672, 51.4842, "Asia/Doha"),  # Jassim bin Hamad Stadium
    "al duhail": (25.3728, 51.4750, "Asia/Doha"),  # Abdullah bin Khalifa Stadium
    "al rayyan": (25.3297, 51.3431, "Asia/Doha"),  # Ahmad bin Ali Stadium
    "al gharafa": (25.3469, 51.4419, "Asia/Doha"),  # Thani bin Jassim Stadium
    "al arabi": (25.3292, 51.4989, "Asia/Doha"),  # Grand Hamad Stadium
    "al wakrah": (25.1797, 51.5758, "Asia/Doha"),  # Al Janoub Stadium
    "al shamal": (25.9167, 51.3667, "Asia/Doha"),  # Al Shamal SC Stadium
    "al shahania": (25.3833, 51.2167, "Asia/Doha"),  # Al Shahania Stadium (或共享)
    "qatar sc": (25.2672, 51.4842, "Asia/Doha"),  # Suheim bin Hamad Stadium (或 Jassim bin Hamad)
    "umm salal": (25.4167, 51.4000, "Asia/Doha"),  # Umm Salal Stadium
    "al khor": (25.6833, 51.5167, "Asia/Doha"),  # Al Khor Stadium
    "al sailiya": (25.2667, 51.5167, "Asia/Doha"),  # Al Sailiya Stadium (或共享 Ahmed bin Ali)
    "Al Markhiya": (25.33225, 51.494278 ,"Asia/Doha"),
    "Al Bidda": (25.317155, 51.512366 ,"Asia/Doha"),
    "艾薩德": (25.2672, 51.4842, "Asia/Doha"), 
    "艾華卡拉": (25.1797, 51.5758, "Asia/Doha"),  # Al Janoub Stadium
    "艾比達": (25.317155, 51.512366 ,"Asia/Doha"),
    "艾沙哈尼亞": (25.3833, 51.2167, "Asia/Doha"),  # Al Shahania Stadium (或共享)
    "艾沙瑪": (25.9167, 51.3667, "Asia/Doha"),  # Al Shamal SC Stadium
    "艾科爾": (25.6833, 51.5167, "Asia/Doha"),  # Al Khor Stadium
    "艾馬希亞": (25.33225, 51.494278 ,"Asia/Doha"),
    "艾塞利亞": (25.2667, 51.5167, "Asia/Doha"),  # Al Sailiya Stadium (或共享 Ahmed bin Ali)
    "艾杜哈尼": (24.4711, 54.3706, "Asia/Qatar"),
    # 智利甲級聯賽 Primera División Chile 2025
    "colo colo": (-33.5064, -70.6056, "America/Santiago"),  # Estadio Monumental David Arellano
    "universidad de chile": (-33.4489, -70.6440, "America/Santiago"),  # Estadio Nacional Julio Martínez Prádanos (主要)
    "universidad catolica": (-33.3983, -70.6328, "America/Santiago"),  # Claro Arena (ex San Carlos de Apoquindo)
    "coquimbo unido": (-29.9628, -71.2542, "America/Santiago"),  # Estadio Francisco Sánchez Rumoroso
    "palestino": (-33.4933, -70.6100, "America/Santiago"),  # Estadio Municipal de La Cisterna
    "union espanola": (-33.3939, -70.6181, "America/Santiago"),  # Estadio Santa Laura-Universidad SEK
    "everton vina del mar": (-33.0089, -71.5400, "America/Santiago"),  # Estadio Sausalito
    "huachipato": (-36.7450, -73.1069, "America/Santiago"),  # Estadio Huachipato-CAP Acero
    "cobresal": (-26.2389, -69.6261, "America/Santiago"),  # Estadio El Cobre (El Salvador)
    "audax italiano": (-33.5083, -70.5833, "America/Santiago"),  # Estadio Bicentenario Municipal de La Florida
    "o'higgins": (-34.1789, -70.7269, "America/Santiago"),  # Estadio El Teniente (Rancagua)
    "nublense": (-36.6239, -72.1039, "America/Santiago"),  # Estadio Municipal Nelson Oyarzún Arenas (Chillán)
    "deportes iquique": (-20.2489, -70.1300, "America/Santiago"),  # Estadio Tierra de Campeones
    "union la calera": (-32.7833, -71.1833, "America/Santiago"),  # Estadio Municipal Nicolás Chahuán Nazar
    "deportes la serena": (-29.9089, -71.2511, "America/Santiago"),  # Estadio La Portada
    "deportes limache": (-32.7833, -71.1833, "America/Santiago"),  # Estadio Municipal Nicolás Chahuán Nazar (La Calera, 暫用)
    # 智利甲級聯賽 Primera División Chile 2025
    "柏利斯天奴": (-33.3939, -70.6181, "America/Santiago"),
    "高路高路": (-33.5064, -70.6056, "America/Santiago"),          # Colo-Colo - Estadio Monumental David Arellano
    "智利大學": (-33.4489, -70.6440, "America/Santiago"),           # Universidad de Chile - Estadio Nacional Julio Martínez Prádanos (主要)
    "天主教大學": (-33.3983, -70.6328, "America/Santiago"),         # Universidad Católica - Claro Arena (ex San Carlos de Apoquindo)
    "科金博": (-29.9628, -71.2542, "America/Santiago"),           # Coquimbo Unido - Estadio Francisco Sánchez Rumoroso
    "紐柏萊斯": (-33.4933, -70.6100, "America/Santiago"),           # Palestino - Estadio Municipal de La Cisterna
    "西班牙聯盟": (-33.3939, -70.6181, "America/Santiago"),         # Unión Española - Estadio Santa Laura-Universidad SEK
    "瓦爾帕萊索埃弗頓": (-33.0089, -71.5400, "America/Santiago"),   # Everton Viña del Mar - Estadio Sausalito
    "瓦奇帕托": (-36.7450, -73.1069, "America/Santiago"),           # Huachipato - Estadio Huachipato-CAP Acero
    "科布雷薩爾": (-26.2389, -69.6261, "America/Santiago"),         # Cobresal - Estadio El Cobre (El Salvador)
    "奧達克斯意大利": (-33.5083, -70.5833, "America/Santiago"),     # Audax Italiano - Estadio Bicentenario Municipal de La Florida
    "奧希金斯": (-34.1789, -70.7269, "America/Santiago"),           # O'Higgins - Estadio El Teniente (Rancagua)
    "紐布蘭斯": (-36.6239, -72.1039, "America/Santiago"),           # Ñublense - Estadio Municipal Nelson Oyarzún Arenas (Chillán)
    "伊基克": (-20.2489, -70.1300, "America/Santiago"),         # Deportes Iquique - Estadio Tierra de Campeones
    "拉卡萊拉聯盟": (-32.7833, -71.1833, "America/Santiago"),       # Unión La Calera - Estadio Municipal Nicolás Chahuán Nazar
    "拉塞雷納體育": (-29.9089, -71.2511, "America/Santiago"),       # Deportes La Serena - Estadio La Portada
    "利馬切": (-32.7833, -71.1833, "America/Santiago"),          # Deportes Limache - Estadio Municipal Nicolás Chahuán Nazar (La Calera, 暫用)
    "康塞普森體育": (-36.815278, -73.023333, "America/Santiago"),
    "卡拉雷聯": (-33.3939, -70.6181, "America/Santiago"),
    "科布雷素": (-26.2389, -69.6261, "America/Santiago"),
    "奧達斯": (-33.3939, -70.6181, "America/Santiago"),
    "拿沙連拿": (-33.5064, -70.6056, "America/Santiago"),
    # 芬超 Veikkausliiga 2025
    "hjk": (60.1903, 24.9639, "Europe/Helsinki"),  # Bolt Arena (Helsinki)
    "kups": (62.9814, 27.6672, "Europe/Helsinki"),  # Magnum Areena (Kuopio)
    "sjk": (62.7850, 22.8417, "Europe/Helsinki"),  # OmaSP Stadion (Seinäjoki)
    "ilves": (61.4997, 23.7892, "Europe/Helsinki"),  # Tammela Stadion (Tampere)
    "haka": (61.2750, 24.0333, "Europe/Helsinki"),  # Tehtaan kenttä (Valkeakoski)
    "vps": (63.0958, 21.6347, "Europe/Helsinki"),  # Elisa Stadion (Vaasa)
    "inter turku": (60.4361, 22.2208, "Europe/Helsinki"),  # Veritas Stadion (Turku)
    "mariehamn": (60.0997, 19.9361, "Europe/Helsinki"),  # Wiklöf Holding Arena (Mariehamn, Åland)
    "oulun": (65.0042, 25.4958, "Europe/Helsinki"),  # Raatti Stadion (Oulu)
    "gnistan": (60.2036, 24.9442, "Europe/Helsinki"),  # Mustapekka Areena (Helsinki)
    "ktp": (60.4500, 26.9333, "Europe/Helsinki"),  # Arto Tolsa Areena (Kotka)
    "jaro": (63.8333, 23.0333, "Europe/Helsinki"),  # Jakobstads Centralplan (Pietarsaari)

    # 芬超 Veikkausliiga 2025
    "HJK": (60.1903, 24.9639, "Europe/Helsinki"),               # HJK - Bolt Arena (Helsinki)
    "古比斯": (62.9814, 27.6672, "Europe/Helsinki"),             # KuPS - Magnum Areena (Kuopio)
    "施拿祖基": (62.7850, 22.8417, "Europe/Helsinki"),        # SJK - OmaSP Stadion (Seinäjoki)
    "伊爾韋斯": (61.4997, 23.7892, "Europe/Helsinki"),          # Ilves - Tammela Stadion (Tampere)
    "哈卡": (61.2750, 24.0333, "Europe/Helsinki"),               # Haka - Tehtaan kenttä (Valkeakoski)
    "瓦薩": (63.0958, 21.6347, "Europe/Helsinki"),               # VPS - Elisa Stadion (Vaasa)
    "英特杜古": (60.4361, 22.2208, "Europe/Helsinki"),        # Inter Turku - Veritas Stadion (Turku)
    "國際杜古": (60.4361, 22.2208, "Europe/Helsinki"),        # Inter Turku - Veritas Stadion (Turku)
    "馬利漢": (60.0997, 19.9361, "Europe/Helsinki"),             # Mariehamn - Wiklöf Holding Arena (Mariehamn, Åland)
    "奧盧": (65.0042, 25.4958, "Europe/Helsinki"),               # Oulu - Raatti Stadion (Oulu)
    "格尼斯坦": (60.2036, 24.9442, "Europe/Helsinki"),             # Gnistan - Mustapekka Areena (Helsinki)
    "科特卡": (60.4500, 26.9333, "Europe/Helsinki"),             # KTP - Arto Tolsa Areena (Kotka)
    "雅羅": (63.8333, 23.0333, "Europe/Helsinki"),               # Jaro - Jakobstads Centralplan (Pietarsaari)
    "赫爾辛基": (60.1903, 24.9639, "Europe/Helsinki"),
    "伊斯韋斯": (60.2214, 24.9417, "Europe/Helsinki"),
    #芬蘭甲級
    "埃克奈斯": (59.9733, 23.6614, "Europe/Helsinki"),  # Ekenäs IF - Ekenäs Centrumplan (Ekenäs/Raseborg)
    "拉赫蒂": (60.9833, 25.6667, "Europe/Helsinki"),  # FC Lahti - Lahden Kisapuisto (Lahti)
    "赫爾辛基04": (60.1903, 24.9639, "Europe/Helsinki"),  # HJK Klubi 04 - Bolt Arena / Helsinki Olympic Stadium (Helsinki)
    "約恩蘇快樂遊戲男孩": (62.6000, 29.7667, "Europe/Helsinki"),  # JIPPO - Mehtimäki (Joensuu)
    "耶爾文佩": (60.3833, 25.0833, "Europe/Helsinki"),  # JäPS - Järvenpään keskuskenttä (Järvenpää)
    "PK-35": (60.2214, 24.9417, "Europe/Helsinki"),  # PK-35 - Mustapekka Areena (Helsinki)
    "薩爾帕": (60.3833, 23.1333, "Europe/Helsinki"),  # SalPa - Salon Urheilupuisto (Salo)
    "TPS圖爾庫": (60.4361, 22.2208, "Europe/Helsinki"),  # Turun Palloseura (TPS) - Veritas Stadion (Turku)
    "KTP科特卡": (60.4667, 26.9333, "Europe/Helsinki"),  # KTP Kotka - Arto Tolsa Areena (Kotka)
    "JJK": (62.2333, 25.7333, "Europe/Helsinki"),  # JJK Jyväskylä - Harjun stadion (Jyväskylä)
    #印尼職業
    "Arema": (-7.9797, 112.6304, "Asia/Jakarta"),
    "Bali United": (-8.5435, 115.327, "Asia/Makassar"),
    "Bhayangkara Presisi Lampung": (-5.42917, 105.26111, "Asia/Jakarta"),
    "Borneo Samarinda": (-0.48585, 117.1466, "Asia/Makassar"),
    "Dewa United Banten": (-6.1149, 106.15, "Asia/Jakarta"),
    "Madura United": (-7.1568, 113.4746, "Asia/Jakarta"),
    "Malut United": (0.79065, 127.384, "Asia/Jayapura"),
    "Persebaya": (-7.25747, 112.75209, "Asia/Jakarta"),
    "Persib": (-6.914744, 107.60981, "Asia/Jakarta"),
    "Persija": (-6.17444, 106.82944, "Asia/Jakarta"),
    "Persijap": (-6.551382, 110.681076, "Asia/Jakarta"),
    "Persik": (-7.81667, 112.017, "Asia/Jakarta"),
    "Persis": (-7.57549, 110.82433, "Asia/Jakarta"),
    "Persita": (-6.17806, 106.63, "Asia/Jakarta"),
    "PSBS": (-1.16667, 136.1, "Asia/Jayapura"),
    "PSIM": (-7.79707, 110.37053, "Asia/Jakarta"),
    "PSM": (-5.14861, 119.432, "Asia/Makassar"),
    "Semen Padang": (-0.95, 100.35, "Asia/Jakarta"),
    "Adhyaksa Banten": (-6.1149, 106.15, "Asia/Jakarta"),
    "Barito Putera": (-3.31987, 114.591, "Asia/Makassar"),
    "Bekasi City": (-6.2349, 106.99, "Asia/Jakarta"),
    "Deltras": (-7.4478, 112.7183, "Asia/Jakarta"),
    "Garudayaksa": (-6.2349, 106.99, "Asia/Jakarta"),
    "Kendal Tornado": (-6.9333, 110.2333, "Asia/Jakarta"),
    "Persekat": (-6.8694, 109.14, "Asia/Jakarta"),
    "Persela": (-7.11667, 112.417, "Asia/Jakarta"),
    "Persiba": (-1.23793, 116.85285, "Asia/Makassar"),
    "Persikad": (-6.4, 106.81861, "Asia/Jakarta"),
    "Persiku kudus": (-6.8048, 110.8405, "Asia/Jakarta"),
    "Persipal palu": (-0.8917, 119.8707, "Asia/Makassar"),
    "Persipura": (-2.53371, 140.718, "Asia/Jayapura"),
    "Persiraja": (5.54167, 95.3333, "Asia/Jakarta"),
    "PSIS": (-6.99306, 110.421, "Asia/Jakarta"),
    "PSMS": (3.58333, 98.6667, "Asia/Jakarta"),
    "PSPS": (0.51667, 101.44167, "Asia/Jakarta"),
    "PSS": (-7.71556, 110.356, "Asia/Jakarta"),
    "Sriwijaya": (-2.97607, 104.77543, "Asia/Jakarta"),
    "Sumsel United": (-2.97607, 104.77543, "Asia/Jakarta"),
    "Tri Brata Rafflesia": (-3.8004, 102.2655, "Asia/Jakarta"),
    "Persitara Jakarta Utara": (-6.1744, 106.8294, "Asia/Jakarta"),
    "Batavia FC": (-6.1744, 106.8294, "Asia/Jakarta"),
    "Persika Karanganyar": (-7.5978, 110.9406, "Asia/Jakarta"),
    "Persebata Lembata": (-8.413, 123.4758, "Asia/Makassar"),
    "Sang Maestro FC": (-7.2504, 112.7688, "Asia/Jakarta"),
    "Pekanbaru FC": (-0.5333, 101.45, "Asia/Jakarta"),
    "Perseden Denpasar": (-8.65, 115.2167, "Asia/Makassar"),
    "PSGC Ciamis": (-7.3257, 108.3534, "Asia/Jakarta"),
    "Persekabpas Pasuruan": (-7.65, 112.9, "Asia/Jakarta"),
    "NZR Sumbersari": (-7.98, 112.63, "Asia/Jakarta"),
    "Persiba Bantul": (-7.8847, 110.3289, "Asia/Jakarta"),
    "PSDS Deli Serdang": (3.4202, 98.7041, "Asia/Jakarta"),
    "Waanal Brothers": (-4.5423, 136.8895, "Asia/Jayapura"),
    "Perserang Serang": (-6.1153, 106.1502, "Asia/Jakarta"),
    "Persibo Bojonegoro": (-7.1502, 111.8817, "Asia/Jakarta"),
    "Nusantara United": (-6.5944, 106.7892, "Asia/Jakarta"),
    "Persikota Tangerang": (-6.178, 106.63, "Asia/Jakarta"),
    "Dejan FC": (-6.4, 106.8186, "Asia/Jakarta"),
    "Persikabo 1973": (-6.5944, 106.7892, "Asia/Jakarta"),
    "Gresik United": (-7.1539, 112.6561, "Asia/Jakarta"),
    "Persewar Waropen": (-2.8, 136.7, "Asia/Jayapura"),
    "Persipa Pati": (-6.7536, 111.0385, "Asia/Jakarta"),
    "RANS Nusantara FC": (-6.1744, 106.8294, "Asia/Jakarta"),
    "Kalteng Putra": (-2.2136, 113.9108, "Asia/Jakarta"),
    "bintang ampenan": ( -8.581824, 116.106832, "Asia/Jakarta"),
    "Sulut United": (-1.4852, 124.8409, "Asia/Makassar"),
    "Persipani": (-3.9, 136.35, "Asia/Jayapura"),
    "757 Kepri Jaya": (1.0456, 104.0305, "Asia/Jakarta"),
    "Persikab": (-6.9147, 107.6098, "Asia/Jakarta"),
    "Persipasi": (-6.2349, 106.9896, "Asia/Jakarta"),
    "PSCS": (-7.7255, 109.0094, "Asia/Jakarta"),
    "PSM Madiun": (-7.63, 111.52, "Asia/Jakarta"),
    "Riverside Forest": (-6.9147, 107.6098, "Asia/Jakarta"),
    "Diklat Sepakbola Kuningan": (-6.975, 108.483, "Asia/Jakarta"),
    "Pelita Yudha Purwakarta": (-6.5569, 107.4433, "Asia/Jakarta"),
    "Bhatara United": (-6.8586, 107.9164, "Asia/Jakarta"),
    "PS Putra Jaya": (-7.65, 112.9, "Asia/Jakarta"),
    "Donggala": (-0.6615, 119.7459, "Asia/Makassar"),
    "Parigi Moutong": (-0.8186, 120.1758, "Asia/Makassar"),
    "Sigi": (-1.385, 119.967, "Asia/Makassar"),
    "Persikotas Tasikmalaya": (-7.3273, 108.2207, "Asia/Jakarta"),
    "Persika 1951": (-6.3075, 107.2907, "Asia/Jakarta"),
    "Pesik Kuningan": (-6.975, 108.483, "Asia/Jakarta"),
    "Cimahi United": (-6.8722, 107.5425, "Asia/Jakarta"),
    "Persindra Indramayu": (-6.3264, 108.324, "Asia/Jakarta"),
    "Persigar Garut": (-7.2167, 107.9, "Asia/Jakarta"),
    "PSN Ngada": (-8.805, 120.956, "Asia/Makassar"),
    "Persena Nagekeo": (-8.8727, 121.2096, "Asia/Makassar"),
    "Persada Southwest Sumba": (-9.445, 119.241, "Asia/Makassar"),
    #荷乙
    "ADO Den Haag": (52.0628, 4.3831, "Europe/Amsterdam"),
    "SC Cambuur": (53.2005, 5.7684, "Europe/Amsterdam"),
    "FC Den Bosch": (51.7016, 5.3298, "Europe/Amsterdam"),
    "FC Dordrecht": (51.8024, 4.6900, "Europe/Amsterdam"),
    "FC Eindhoven": (51.4408, 5.4778, "Europe/Amsterdam"),
    "FC Emmen": (52.7747, 6.9456, "Europe/Amsterdam"),
    "Excelsior Rotterdam": (51.9225, 4.4792, "Europe/Amsterdam"),
    "精英隊": (51.9225, 4.4792, "Europe/Amsterdam"),
    "De Graafschap": (51.9558, 6.3094, "Europe/Amsterdam"),
    "Helmond Sport": (51.4856, 5.6755, "Europe/Amsterdam"),
    "Jong Ajax": (52.3125, 4.9295, "Europe/Amsterdam"),
    "Jong AZ": (52.6077, 4.7387, "Europe/Amsterdam"),
    "Jong PSV Eindhoven": (51.4833, 5.4667, "Europe/Amsterdam"),
    "Jong FC Utrecht": (52.0929, 5.1045, "Europe/Amsterdam"),
    "MVV Maastricht": (50.8575, 5.7177, "Europe/Amsterdam"),
    "Roda JC Kerkrade": (50.8575, 6.0054, "Europe/Amsterdam"),
    "Telstar": (52.4552, 4.6350, "Europe/Amsterdam"),
    "TOP Oss": (51.7550, 5.5279, "Europe/Amsterdam"),
    "SBV Vitesse": (51.9628, 5.8929, "Europe/Amsterdam"),
    "VVV-Venlo": (51.3520, 6.1728, "Europe/Amsterdam"),
    "FC Volendam": (52.4944, 5.0663, "Europe/Amsterdam"),
    
    
    #港超聯
    "eastern": (22.3261, 114.1729, "Asia/HongKong"),  # Mong Kok Stadium
    "eastern district": (22.267473, 114.249058, "Asia/HongKong"),  # Siu Sai Wan Sports Ground
    "hkfc": (22.274425, 114.181677, "Asia/HongKong"),  # HKFC Stadium
    "kitchee": (22.3261, 114.1729, "Asia/HongKong"),  # Mong Kok Stadium (primary)
    "kowloon city": (22.3371, 114.1521, "Asia/HongKong"),  # Sham Shui Po Sports Ground
    "lee man": (22.3261, 114.1729, "Asia/HongKong"),  # Mong Kok Stadium
    "northdistrict": (22.50383, 114.125, "Asia/HongKong"),  # North District Sports Ground
    "biu chun rangers": (22.356139, 114.107479, "Asia/HongKong"),  # Tsing Yi Sports Ground
    "southern": (22.250087, 114.172398, "Asia/HongKong"),  # Aberdeen Sports Ground
    "tai po": (22.4554, 114.1667, "Asia/HongKong"),  # Tai Po Sports Ground
    
    "公民": (22.3344, 114.1986, "Asia/Hong_Kong"),  # Po Kong Village Road Park
    "中西區": (22.2747, 114.1842, "Asia/Hong_Kong"),  # Happy Valley Recreation Ground
    "海景": (22.3417, 114.2014, "Asia/Hong_Kong"),  # Hammer Hill Road Sports Ground
    "三勝": (22.3244, 114.2056, "Asia/Hong_Kong"),  # Kowloon Bay Park
    "元朗": (22.4417, 114.0225, "Asia/Hong_Kong"),  # Yuen Long Stadium
    "南華": (22.3261, 114.1729, "Asia/Hong_Kong"),  # Mong Kok Stadium
    "東昇": (22.3133, 114.2233, "Asia/Hong_Kong"),  # Kwun Tong Recreation Ground
    "至尊": (22.3344, 114.1986, "Asia/Hong_Kong"),  # Po Kong Village Road Park
    "觀塘": (22.3133, 114.2233, "Asia/Hong_Kong"),  # Kwun Tong Recreation Ground
    "幸運一哩": (22.3417, 114.2014, "Asia/Hong_Kong"),  # Hammer Hill Road Sports Ground
    "亮藍": (22.3317, 114.2033, "Asia/Hong_Kong"),  # Wu Shan Recreation Playground
    
    #中超
    "shanghai port": (31.1833, 121.4375, "Asia/Shanghai"),  # Shanghai Stadium
    "shanghai shenhua": (31.1833, 121.4375, "Asia/Shanghai"),  # Shanghai Stadium
    "chengdu rongcheng": (30.6564, 104.0667, "Asia/Shanghai"),  # Phoenix Hill Football Stadium
    "beijing guoan": (39.9294, 116.4394, "Asia/Shanghai"),  # Workers' Stadium
    "shandong taishan": (36.6569, 117.1106, "Asia/Shanghai"),  # Jinan Olympic Sports Center Stadium
    "tianjin jinmentiger": (39.0736, 117.1694, "Asia/Shanghai"),  # Tianjin Olympic Centre Stadium
    "zhejiang": (30.2681, 120.1492, "Asia/Shanghai"),  # Huanglong Sports Centre Stadium
    "henan": (34.7150, 113.7264, "Asia/Shanghai"),  # Zhengzhou Hanghai Stadium
    "wuhan three towns": (30.5431, 114.3092, "Asia/Shanghai"),  # Wuhan Sports Center
    "changchun yatai": (43.8381, 125.3153, "Asia/Shanghai"),  # Changchun Stadium
    "qingdao hainiu": (36.0656, 120.3461, "Asia/Shanghai"),  # Qingdao Youth Football Stadium
    "cangzhou mighty lions": (38.3067, 116.8361, "Asia/Shanghai"),  # Cangzhou Stadium
    "shenzhen peng city": (22.5644, 113.8794, "Asia/Shanghai"),  # Bao'an Stadium
    "qingdao west coast": (35.9236, 120.0017, "Asia/Shanghai"),  # Guzhenkou University City Sports Center
    "nantong zhiyun": (32.3811, 120.5728, "Asia/Shanghai"),  # Rugao Olympic Sports Center
    "meizhou hakka": (23.9231, 115.7769, "Asia/Shanghai"),  # Wuhua County Olympic Sports Centre
    "dalian yingbo": (38.9175, 121.6344, "Asia/Shanghai"),  # Dalian Suoyuwan Football Stadium
    #越南
    "becamex binh duong": (10.9700, 106.6700, "Asia/Ho_Chi_Minh"),  # Go Dau Stadium
    "binh dinh": (13.7700, 109.2300, "Asia/Ho_Chi_Minh"),  # Quy Nhon Stadium
    "cong an hanoi": (21.0206, 105.7639, "Asia/Ho_Chi_Minh"),  # My Dinh National Stadium
    "dong a thanh hoa": (19.8000, 105.7667, "Asia/Ho_Chi_Minh"),  # Thanh Hoa Stadium
    "hai phong": (20.8500, 106.6833, "Asia/Ho_Chi_Minh"),  # Lach Tray Stadium
    "hanoi fc": (21.0281, 105.8336, "Asia/Ho_Chi_Minh"),  # Hang Day Stadium
    "ho chi minh city": (10.7625, 106.6617, "Asia/Ho_Chi_Minh"),  # Thong Nhat Stadium
    "hoang anh gia lai": (13.9833, 108.0000, "Asia/Ho_Chi_Minh"),  # Pleiku Stadium
    "hong linh ha tinh": (18.3333, 105.9000, "Asia/Ho_Chi_Minh"),  # Ha Tinh Stadium
    "nam dinh": (20.4333, 106.1667, "Asia/Ho_Chi_Minh"),  # Thien Truong Stadium
    "quang nam": (15.5667, 108.4833, "Asia/Ho_Chi_Minh"),  # Tam Ky Stadium
    "shb da nang": (16.0667, 108.2167, "Asia/Ho_Chi_Minh"),  # Hoa Xuan Stadium
    "song lam nghe an": (18.6667, 105.6667, "Asia/Ho_Chi_Minh"),  # Vinh Stadium
    "viettel": (21.0206, 105.7639, "Asia/Ho_Chi_Minh"),  # My Dinh National Stadium
    # 港超聯 Hong Kong Premier League
    "東方": (22.3261, 114.1729, "Asia/Hong_Kong"),              # Eastern - Mong Kok Stadium
    "東區": (22.267473, 114.249058, "Asia/Hong_Kong"),          # Eastern District - Siu Sai Wan Sports Ground
    "港會": (22.274425, 114.181677, "Asia/Hong_Kong"),          # HKFC - HKFC Stadium
    "傑志": (22.3261, 114.1729, "Asia/Hong_Kong"),               # Kitchee - Mong Kok Stadium (主要主場)
    "九龍城": (22.3371, 114.1521, "Asia/Hong_Kong"),             # Kowloon City - Sham Shui Po Sports Ground
    "理文": (22.3261, 114.1729, "Asia/Hong_Kong"),               # Lee Man - Mong Kok Stadium
    "北區": (22.50383, 114.125, "Asia/Hong_Kong"),               # North District - North District Sports Ground
    "標準流浪": (22.356139, 114.107479, "Asia/Hong_Kong"),       # Biu Chun Rangers - Tsing Yi Sports Ground
    "南區": (22.250087, 114.172398, "Asia/Hong_Kong"),           # Southern - Aberdeen Sports Ground
    "大埔": (22.4554, 114.1667, "Asia/Hong_Kong"),               # Tai Po - Tai Po Sports Ground
    
    # 中超 Chinese Super League
    "上海海港": (31.1833, 121.4375, "Asia/Shanghai"),            # Shanghai Port - Shanghai Stadium
    "上海申花": (31.1833, 121.4375, "Asia/Shanghai"),            # Shanghai Shenhua - Shanghai Stadium
    "成都蓉城": (30.6564, 104.0667, "Asia/Shanghai"),            # Chengdu Rongcheng - Phoenix Hill Football Stadium
    "北京國安": (39.9294, 116.4394, "Asia/Shanghai"),            # Beijing Guoan - Workers' Stadium
    "山東泰山": (36.6569, 117.1106, "Asia/Shanghai"),            # Shandong Taishan - Jinan Olympic Sports Center Stadium
    "天津津門虎": (39.0736, 117.1694, "Asia/Shanghai"),          # Tianjin Jinmen Tiger - Tianjin Olympic Centre Stadium
    "浙江": (30.2681, 120.1492, "Asia/Shanghai"),                # Zhejiang - Huanglong Sports Centre Stadium
    "河南": (34.7150, 113.7264, "Asia/Shanghai"),                # Henan - Zhengzhou Hanghai Stadium
    "武漢三鎮": (30.5431, 114.3092, "Asia/Shanghai"),            # Wuhan Three Towns - Wuhan Sports Center
    "長春亞泰": (43.8381, 125.3153, "Asia/Shanghai"),            # Changchun Yatai - Changchun Stadium
    "青島海牛": (36.0656, 120.3461, "Asia/Shanghai"),            # Qingdao Hainiu - Qingdao Youth Football Stadium
    "滄州雄獅": (38.3067, 116.8361, "Asia/Shanghai"),            # Cangzhou Mighty Lions - Cangzhou Stadium
    "深圳鵬城": (22.5644, 113.8794, "Asia/Shanghai"),            # Shenzhen Peng City - Bao'an Stadium
    "青島西海岸": (35.9236, 120.0017, "Asia/Shanghai"),          # Qingdao West Coast - Guzhenkou University City Sports Center
    "南通支雲": (32.3811, 120.5728, "Asia/Shanghai"),            # Nantong Zhiyun - Rugao Olympic Sports Center
    "梅州客家": (23.9231, 115.7769, "Asia/Shanghai"),            # Meizhou Hakka - Wuhua County Olympic Sports Centre
    "大連英博": (38.9175, 121.6344, "Asia/Shanghai"),            # Dalian Yingbo - Dalian Suoyuwan Football Stadium
    
    # 越南職業聯賽 V.League 1
    "平陽比加麥": (10.9700, 106.6700, "Asia/Ho_Chi_Minh"),      # Becamex Binh Duong - Go Dau Stadium
    "平定": (13.7700, 109.2300, "Asia/Ho_Chi_Minh"),             # Binh Dinh - Quy Nhon Stadium
    "河內公安": (21.0206, 105.7639, "Asia/Ho_Chi_Minh"),         # Cong An Hanoi - My Dinh National Stadium
    "東亞清化": (19.8000, 105.7667, "Asia/Ho_Chi_Minh"),         # Dong A Thanh Hoa - Thanh Hoa Stadium
    "海防": (20.8500, 106.6833, "Asia/Ho_Chi_Minh"),             # Hai Phong - Lach Tray Stadium
    "河內FC": (21.0281, 105.8336, "Asia/Ho_Chi_Minh"),           # Hanoi FC - Hang Day Stadium
    "胡志明市": (10.7625, 106.6617, "Asia/Ho_Chi_Minh"),         # Ho Chi Minh City - Thong Nhat Stadium
    "黃英嘉萊": (13.9833, 108.0000, "Asia/Ho_Chi_Minh"),         # Hoang Anh Gia Lai - Pleiku Stadium
    "鴻林河靜": (18.3333, 105.9000, "Asia/Ho_Chi_Minh"),         # Hong Linh Ha Tinh - Ha Tinh Stadium
    "南定": (20.4333, 106.1667, "Asia/Ho_Chi_Minh"),             # Nam Dinh - Thien Truong Stadium
    "廣南": (15.5667, 108.4833, "Asia/Ho_Chi_Minh"),             # Quang Nam - Tam Ky Stadium
    "SHB峴港": (16.0667, 108.2167, "Asia/Ho_Chi_Minh"),          # SHB Da Nang - Hoa Xuan Stadium
    "宋藍義安": (18.6667, 105.6667, "Asia/Ho_Chi_Minh"),         # Song Lam Nghe An - Vinh Stadium
    "越南電信": (21.0206, 105.7639, "Asia/Ho_Chi_Minh"),         # Viettel - My Dinh National Stadium
    #奧地利
    "austria wien": (48.2075, 16.4189, "Europe/Vienna"),  # Generali Arena
    "rapid wien": (48.1975, 16.2653, "Europe/Vienna"),  # Allianz Stadion
    "red bull salzburg": (47.8164, 13.0794, "Europe/Vienna"),  # Red Bull Arena
    "sturm graz": (47.0464, 15.4542, "Europe/Vienna"),  # Merkur-Arena
    "lask": (48.2933, 14.2750, "Europe/Vienna"),  # Raiffeisen Arena
    "wolfsberger ac": (46.8250, 14.8500, "Europe/Vienna"),  # Lavanttal-Arena
    "austria klagenfurt": (46.6089, 14.2781, "Europe/Vienna"),  # Wörthersee Stadion
    "hartberg": (47.1047, 15.9700, "Europe/Vienna"),  # Profertil Arena Hartberg
    "austria lustenau": (47.4208, 9.6586, "Europe/Vienna"),  # Reichshofstadion
    "blau weiss linz": (48.2936, 14.2753, "Europe/Vienna"),  # Hofmann Personal Stadion
    "wsg tirol": (47.2631, 11.4094, "Europe/Vienna"),  # Tivoli Stadion Tirol
    "altach": (47.3536, 9.6389, "Europe/Vienna"),  # Cashpoint Arena
    "brisbanestrikers": (-27.4450, 153.0330, "Australia/Brisbane"),  # Perry Park
    #Football Queensland Premier League
    "broadbeach united": (-28.0290, 153.4280, "Australia/Brisbane"),  # Nikiforides Family Park
    "caboolture": (-27.1580, 152.9720, "Australia/Brisbane"),  # Moreton Bay Central Sports Complex
    "capalaba": (-27.5330, 153.1920, "Australia/Brisbane"),  # John Fredericks Park
    "eastern suburbs": (-27.4870, 153.0470, "Australia/Brisbane"),  # Heath Park
    "ipswich fc": (-27.6240, 152.7460, "Australia/Brisbane"),  # Briggs Road Sporting Complex
    "logan lightning": (-27.6610, 153.2080, "Australia/Brisbane"),  # Cornubia Park
    "moreton city excelsior": (-27.3580, 152.9700, "Australia/Brisbane"),  # Wolter Park
    "peninsula power": (-27.2260, 153.0880, "Australia/Brisbane"),  # A.J. Kelly Park
    "southside comets": (-27.4880, 153.1880, "Australia/Brisbane"),  # Wakerley Park
    "swq thunder": (-27.5580, 151.9670, "Australia/Brisbane"),  # Clive Berghofer Stadium
    "wdsc wolves": (-27.4780, 153.1170, "Australia/Brisbane"),  # Carmichael Park
    #Latvia league
    "auda": (56.8264, 24.2322, "Europe/Riga"),  # Audas Stadions
    "bfc daugavpils": (55.8714, 26.5333, "Europe/Riga"),  # Celtnieks Stadium
    "fs jelgava": (56.6533, 23.7283, "Europe/Riga"),  # Zemgale Olympic Center
    "grobinassc": (56.5042, 21.0106, "Europe/Riga"),  # Daugava Stadium (Liepāja)
    "fk liepaja": (56.5042, 21.0106, "Europe/Riga"),  # Daugava Stadium (Liepāja)
    "fk metta": (56.9614, 24.1167, "Europe/Riga"),  # Daugava Stadium (Riga)
    "riga fc": (56.9613, 24.1161, "Europe/Riga"),  # Skonto Stadium
    "rfs": (56.9042, 24.1722, "Europe/Riga"),  # LNK Sporta Parks
    "tukums 2000": (56.9725, 23.1556, "Europe/Riga"),  # Tukuma Pilsētas Stadions
    "valmiera fc": (57.5417, 25.4250, "Europe/Riga"),  # Jānis Daliņš Stadions
    #Egyptian Premier League
    "al ahly": (30.0694, 31.3122, "Africa/Cairo"),  # Cairo International Stadium
    "al mokawloon al arab sc": (30.1333, 31.3786, "Africa/Cairo"),  # Osman Ahmed Osman Stadium
    "ceramica cleopatra": (30.1333, 31.3786, "Africa/Cairo"),  # Osman Ahmed Osman Stadium
    "enppi": (30.0250, 31.3736, "Africa/Cairo"),  # Petrosport Stadium
    "ghazl el mahalla": (30.9563, 31.1703, "Africa/Cairo"),  # Ghazl El Mahalla Stadium
    "el gouna": (27.0717, 33.8389, "Africa/Cairo"),  # Khaled Bichara Stadium
    "haras el hodoud": (31.3811, 29.9744, "Africa/Cairo"),  # Haras El Hodoud Stadium
    "ismaily": (30.5992, 32.2733, "Africa/Cairo"),  # Ismailia Stadium
    "kahraba ismailia sc": (30.5992, 32.2733, "Africa/Cairo"),  # Kahraba Ismailia Stadium (approx Ismailia)
    "al ittihad": (31.1972, 29.9153, "Africa/Cairo"),  # Alexandria Stadium
    "al masry": (29.9569, 32.5492, "Africa/Cairo"),  # Suez Stadium
    "modern sport": (30.0694, 31.3122, "Africa/Cairo"),  # Cairo International Stadium
    "nationalbankofegypt": (30.0694, 31.3122, "Africa/Cairo"),  # Cairo International Stadium
    "petrojet": (30.0625, 31.3667, "Africa/Cairo"),  # Cairo Military Academy Stadium
    "pharco": (31.3811, 29.9744, "Africa/Cairo"),  # Haras El Hodoud Stadium
    "pyramids": (30.0625, 31.3667, "Africa/Cairo"),  # 30 June Stadium
    "smouha": (30.9989, 29.7264, "Africa/Cairo"),  # Borg El Arab Stadium
    "talaea el gaish": (30.0533, 31.3000, "Africa/Cairo"),  # Gehaz El Reyada Stadium
    "wadi degla sc": (30.0250, 31.3736, "Africa/Cairo"),  # Petrosport Stadium
    "zamalek": (30.0694, 31.3122, "Africa/Cairo"),  # Cairo International Stadium
    "zed": (30.0694, 31.3122, "Africa/Cairo"),  # Cairo International Stadium
    "伊蒂哈德": (31.1972, 29.9153, "Africa/Cairo"),  # Alexandria Stadium
    #NIFL Premiership
    "ballymena united": (54.8658, -6.2761, "Europe/Belfast"),  # Ballymena Showgrounds
    "bangor": (54.6453, -5.6958, "Europe/Belfast"),  # Clandeboye Park
    "carrick rangers": (54.7286, -5.7944, "Europe/Belfast"),  # Taylors Avenue
    "cliftonville": (54.6189, -5.9500, "Europe/Belfast"),  # Solitude
    "coleraine": (55.1325, -6.6669, "Europe/Belfast"),  # The Showgrounds
    "crusaders": (54.6208, -5.9517, "Europe/Belfast"),  # Seaview
    "dungannon swifts": (54.4519, -6.7811, "Europe/Belfast"),  # Stangmore Park
    "glenavon": (54.4542, -6.3347, "Europe/Belfast"),  # Mourneview Park
    "glentoran": (54.6025, -5.8922, "Europe/Belfast"),  # The Oval
    "larne": (54.8533, -5.8356, "Europe/Belfast"),  # Inver Park
    "linfield": (54.5825, -5.9550, "Europe/Belfast"),  # Windsor Park
    "portadown": (54.3511, -6.6447, "Europe/Belfast"),  # Shamrock Park
    #波蘭甲組
    "cracovia": (50.0614, 19.9236, "Europe/Warsaw"),  # Stadion Cracovii
    "gks katowice": (50.2658, 19.0275, "Europe/Warsaw"),  # Stadion GKS Katowice
    "gornik zabrze": (50.2961, 18.7689, "Europe/Warsaw"),  # Stadion im. Ernesta Pohla
    "jagiellonia bialystok": (53.1317, 23.1461, "Europe/Warsaw"),  # Stadion Miejski (Białystok)
    "korona kielce": (50.8633, 20.6117, "Europe/Warsaw"),  # Suzuki Arena
    "lech poznan": (52.3975, 16.8578, "Europe/Warsaw"),  # Stadion Poznań
    "lechia gdansk": (54.3914, 18.5306, "Europe/Warsaw"),  # Polsat Plus Arena Gdańsk
    "legia warsaw": (52.2206, 21.0408, "Europe/Warsaw"),  # Stadion Wojska Polskiego
    "motor lublin": (51.2325, 22.5608, "Europe/Warsaw"),  # Arena Lublin
    "piast gliwice": (50.3064, 18.6956, "Europe/Warsaw"),  # Stadion Miejski (Gliwice)
    "pogon szczecin": (53.4353, 14.5214, "Europe/Warsaw"),  # Stadion Miejski (Szczecin)
    "puszcza niepolomice": (50.0100, 20.1700, "Europe/Warsaw"),  # Stadion Miejski (Niepołomice)
    "radomiak radom": (51.3933, 21.1583, "Europe/Warsaw"),  # Stadion im. Braci Czachorów
    "rakow czestochowa": (50.7725, 19.1389, "Europe/Warsaw"),  # Stadion Rakowa
    "slask wroclaw": (51.1411, 16.9436, "Europe/Warsaw"),  # Stadion Wrocław
    "stal mielec": (50.2978, 21.4339, "Europe/Warsaw"),  # Stadion Miejski (Mielec)
    "widzew lodz": (51.7647, 19.5122, "Europe/Warsaw"),  # Stadion Widzewa Łódź
    "zaglebie lubin": (51.4139, 16.2017, "Europe/Warsaw"),  # Stadion Zagłębia Lubin
    #波蘭乙組
    "arka gdynia": (54.4928, 18.5311, "Europe/Warsaw"),  # Stadion Miejski (Gdynia)
    "bruk bet termalica nieciecza": (50.1600, 20.9400, "Europe/Warsaw"),  # Stadion Bruk-Bet
    "chrobry glogow": (51.6622, 16.0883, "Europe/Warsaw"),  # Stadion Chrobrego Głogów
    "gks tychy": (50.1250, 18.9861, "Europe/Warsaw"),  # Stadion Miejski (Tychy)
    "gornik leczna": (51.3011, 22.8811, "Europe/Warsaw"),  # Stadion Górnika Łęczna
    "kotwica kolobrzeg": (54.1833, 15.5833, "Europe/Warsaw"),  # Stadion Miejski (Kołobrzeg)
    "lks lodz": (51.7575, 19.4217, "Europe/Warsaw"),  # Stadion Miejski (Łódź)
    "miedz legnica": (51.2072, 16.1686, "Europe/Warsaw"),  # Stadion Miejski (Legnica)
    "odra opole": (50.6750, 17.9250, "Europe/Warsaw"),  # Stadion Odry Opole
    "polonia warszawa": (52.2528, 21.0239, "Europe/Warsaw"),  # Stadion Polonii Warszawa
    "ruch chorzow": (50.2819, 18.9514, "Europe/Warsaw"),  # Stadion Ruchu Chorzów
    "stal rzeszow": (50.0342, 22.0000, "Europe/Warsaw"),  # Stadion Miejski (Rzeszów)
    "stal stalowa wola": (50.5650, 22.0533, "Europe/Warsaw"),  # Stadion MOSiR (Stalowa Wola)
    "wisla krakow": (50.0639, 19.9111, "Europe/Warsaw"),  # Stadion Miejski (Kraków)
    "wisla plock": (52.5625, 19.6850, "Europe/Warsaw"),  # Stadion im. Kazimierza Górskiego
    "znicz pruszkow": (52.1700, 20.8100, "Europe/Warsaw"),  # Stadion MZOS Znicz
    #Segunda División Profesional de Chile
    "santiago morning": (-33.4100, -70.6325, "America/Santiago"),  # Chacabuco Stadium
    "deportes melipilla": (-33.6897, -71.3800, "America/Santiago"),  # Estadio Municipal Roberto Bravo Santibáñez
    "provincial osorno": (-40.5761, -73.1353, "America/Santiago"),  # Estadio Rubén Marcos Peralta
    "deportes rengo": (-34.4025, -70.8583, "America/Santiago"),  # Estadio Municipal Guillermo Guzmán Díaz
    "colchagua cd": (-34.6225, -70.9875, "America/Santiago"),  # Estadio Municipal Jorge Silva Valenzuela
    "concon national": (-32.9236, -71.5181, "America/Santiago"),  # Estadio Atlético Municipal
    "deportes linares": (-35.8461, -71.5972, "America/Santiago"),  # Estadio Fiscal de Linares
    "general velasquez": (-34.4389, -71.0811, "America/Santiago"),  # Estadio Municipal Augusto Rodríguez
    "real san joaquin": (-33.5025, -70.6236, "America/Santiago"),  # Estadio Municipal de San Joaquín
    "san antoniounido": (-33.5975, -71.6114, "America/Santiago"),  # Estadio Municipal Doctor Olegario Henríquez Escalante
    "trasandino": (-32.8333, -70.6000, "America/Santiago"),  # Estadio Regional de Los Andes
    "provincial ovalle": (-30.6011, -71.1994, "America/Santiago"),  # Estadio Diaguita
    "atletico colina": (-33.1986, -70.6700, "America/Santiago"),  # Estadio Municipal Manuel Rojas
    "brujas de salamanca": (-31.7800, -70.9750, "America/Santiago"), # Estadio Municipal de Salamanca
    "club de deportes naval de talcahuano":(-38.017, -71.900,"America/Santiago"),
    #National Premier Leagues Victoria
    "altona magic": (-37.8450, 144.8130, "Australia/Melbourne"),  # ABD Stadium
    "avondale": (-37.7600, 144.9200, "Australia/Melbourne"),  # Avondale Heights Reserve
    "dandenong city": (-37.9667, 145.2167, "Australia/Melbourne"),  # Frank Holohan Soccer Complex
    "dandenong thunder": (-37.9683, 145.1883, "Australia/Melbourne"),  # George Andrews Reserve
    "green gully": (-37.7133, 144.8233, "Australia/Melbourne"),  # Green Gully Reserve
    "heidelberg united": (-37.7250, 145.0389, "Australia/Melbourne"),  # Olympic Village
    "hume city": (-37.7033, 144.9542, "Australia/Melbourne"),  # John Ilhan Memorial Reserve
    "manningham united blues": (-37.7767, 145.1142, "Australia/Melbourne"),  # Pettys Reserve
    "melbourne knights": (-37.8175, 144.8825, "Australia/Melbourne"),  # Knights Stadium
    "oakleigh cannons": (-37.9183, 145.0983, "Australia/Melbourne"),  # Jack Edwards Reserve
    "port melbourne sharks": (-37.8325, 144.9433, "Australia/Melbourne"),  # SS Anderson Reserve
    "south melbourne": (-37.8350, 144.9600, "Australia/Melbourne"),  # Lakeside Stadium
    "st albans saints": (-37.7450, 144.8050, "Australia/Melbourne"),  # Churchill Reserve
    #其他
    "帕福斯":(34.769186, 32.440144,"Europe/Nicosia" ),
    "CD奧林比亞": (14.098333, -87.203889, "Tegucigalpa/Honduras"),
    
    #巴拉圭甲組
    "特立尼登斯": (-25.3000, -57.6333, "America/Asuncion"),
    "奧林比亞": (-25.3000, -57.6333, "America/Asuncion"),  # Club Olimpia - Estadio Osvaldo Domínguez Dibb / Para Uno (Asunción)
    "塞羅波特尼奧": (-25.3000, -57.6333, "America/Asuncion"),  # Cerro Porteño - Estadio General Pablo Rojas / La Olla (Asunción)
    "國民會": (-25.3000, -57.6333, "America/Asuncion"),  # Club Nacional - Estadio Arsenio Erico (Asunción)
    "瓜拉尼": (-25.3000, -57.6333, "America/Asuncion"),  # Club Guaraní - Estadio Rogelio Livieres (Asunción)
    "利伯塔德": (-25.3000, -57.6333, "America/Asuncion"),  # Club Libertad - Estadio Tigo La Huerta (Asunción)
    "斯波爾蒂沃盧克尼奧": (-25.2667, -57.5333, "America/Asuncion"),  # Sportivo Luqueño - Estadio Feliciano Cáceres (Luque)
    "斯波爾蒂沃阿梅利亞諾": (-25.3000, -57.6333, "America/Asuncion"),  # Sportivo Ameliano - Estadio José Tomás Silva (Asunción)
    "赫內拉爾卡瓦列羅": (-25.3667, -57.4333, "America/Asuncion"),  # General Caballero JLM - Estadio Ka'arendy (Juan León Mallorquín)
    "三鎮體育": (-25.3000, -57.6333, "America/Asuncion"),  # Sportivo Trinidense - Estadio Martín Torres (Asunción)
    "坦博雷亞": (-25.3000, -57.6333, "America/Asuncion"),  # Tacuary - Estadio Luis Alfonso Giagni (Asunción)
    "索爾德亞美利加": (-25.3000, -57.6333, "America/Asuncion"),  # Sol de América - Estadio Luis Alfonso Giagni (Asunción)
    "五月二日": (22.5333, -57.0833, "America/Asuncion"),  # Sportivo 2 de Mayo - Estadio Río Parapití (Pedro Juan Caballero)
    "波士頓河": (-34.8959, -56.1597, "America/Montevideo"),  # Boston River - Estadio Parque Central (Montevideo, shared)
    "西班牙人中央": (-34.7264, -56.2208, "America/Asuncion"),  # Club Central Español - Estadio Parque Central (Montevideo, shared)
    #巴拉圭乙組
    "艾特班": (-34.7917, -55.8333, "America/Montevideo"),  # Atenas de San Carlos - Estadio Parque Artigas (San Carlos)
    "拉努斯": (-34.7264, -56.2208, "America/Montevideo"),  # Rampla Juniors - Estadio Olímpico (Montevideo)
    "蒙特維多競賽會二隊": (-34.8847, -56.1528, "America/Montevideo"),  # Nacional B - Gran Parque Central (Montevideo, reserve)
    "達努比奧二隊": (-34.8011, -56.1997, "America/Montevideo"),  # Danubio B - Jardines del Hipódromo (Montevideo, reserve)
    "普羅格雷索": (-34.8667, -56.2333, "America/Montevideo"),  # C.A. Progreso - Estadio Abraham Paladino (Montevideo)
    "森特拉爾埃斯帕尼奧爾": (-34.7264, -56.2208, "America/Montevideo"),  # Central Español - Estadio Parque Central (Montevideo)
    "蒙特維多城托基": (-34.8500, -56.2133, "America/Montevideo"),  # Montevideo City Torque - Estadio Centenario (Montevideo)
    "米拉馬米斯奧尼斯": (-34.8667, -56.1833, "America/Montevideo"),  # Miramar Misiones - Estadio Luis Méndez Piana (Montevideo)
    "普拉薩科洛尼亞": (-34.4667, -57.8333, "America/Montevideo"),  # Plaza Colonia - Estadio Parque Sur (Colonia del Sacramento)
    "拉斯特雷斯": (-34.7264, -56.2208, "America/Montevideo"),  # Racing Club de Montevideo - Estadio Osvaldo Roberto (Montevideo)
    "艾斯特雷拉": (-34.7264, -56.2208, "America/Montevideo"),  # Sud América - Estadio Parque Luis Méndez Piana (Montevideo)
    "蒙特維多流浪者二隊": (-34.8606, -56.1667, "America/Montevideo"),  # Wanderers B - Estadio Alfredo Víctor Viera (Montevideo, reserve)
    "蒙特維多流浪者": (-34.8606, -56.1667, "America/Montevideo"),  # Wanderers B - Estadio Alfredo Víctor Viera (Montevideo, reserve)
    #星加坡
    "新加坡新潟天鵝": (1.3344, 103.7428, "Asia/Singapore"),  # 新加坡新潟天鵝（或丹戎巴葛新潟天鵝，Jurong East Stadium）
    "馬里士他卡沙": (1.3667, 103.8333, "Asia/Singapore"),  # 馬里士他卡沙（Toa Payoh Stadium）
    "淡濱尼流浪": (1.3539, 103.9419, "Asia/Singapore"),  # BG淡濱尼流浪（Our Tampines Hub）
    "芽籠國際": (1.3181, 103.8719, "Asia/Singapore"),  # 芽籠國際（Bedok Stadium）
    "後港聯": (1.3708, 103.8900, "Asia/Singapore"),  # 后港聯（Hougang Stadium）
    "獅城水手": (1.3547, 103.8501, "Asia/Singapore"),  # 獅城水手（Jalan Besar Stadium 或 Bishan Stadium）
    "丹戎巴葛": (1.3347, 103.7425, "Asia/Singapore"),  # 丹戎巴葛聯（Jurong East Stadium）
    "幼獅隊": (1.3000, 103.8500, "Asia/Singapore"),  # 幼獅隊（Jalan Besar Stadium）
    #瓜地馬拉國家足球聯賽球隊
    "阿丘阿帕": (14.2000, -89.7667, "America/Guatemala"),  # C.D. Achuapa - Estadio Winston Pineda (El Progreso, Jutiapa)
    "安蒂瓜": (14.5564, -90.7333, "America/Guatemala"),  # Antigua GFC - Estadio Pensativo (Antigua Guatemala)
    "奧羅拉": (14.4875, -90.6150, "America/Guatemala"),  # Aurora F.C. - Estadio Guillermo Slowing (Amatitlán)
    "科班帝國": (15.4711, -90.3167, "America/Guatemala"),  # Cobán Imperial - Estadio Verapaz (Cobán)
    "通訊": (14.6231, -90.5153, "America/Guatemala"),  # Comunicaciones F.C. - Estadio Cementos Progreso (Guatemala City)
    "瓜斯塔托亞": (14.8542, -89.8708, "America/Guatemala"),  # C.D. Guastatoya - Estadio David Cordón Hichos (Guastatoya)
    "馬拉卡特科": (14.5308, -91.8675, "America/Guatemala"),  # C.D. Malacateco - Estadio Santa Lucía (Malacatán)
    "馬肯塞": (14.9667, -91.8000, "America/Guatemala"),  # C.D. Marquense - Estadio Marquesa de la Ensenada (San Marcos)
    "米克特蘭": (14.3333, -89.7167, "America/Guatemala"),  # Atlético Mictlán - Estadio La Asunción (Asunción Mita)
    "米斯科": (14.5328, -90.5000, "America/Guatemala"),  # Deportivo Mixco - Estadio Santo Domingo de Guzmán (Mixco)
    "市政": (14.6169, -90.5347, "America/Guatemala"),  # C.S.D. Municipal - Estadio Manuel Felipe Carrera (El Trébol, Guatemala City)
    "夏拉祖": (14.8419, -91.5172, "America/Guatemala"),  # C.S.D. Xelajú MC - Estadio Mario Camposeco (Quetzaltenango)
    #加拿大聯業球隊
    "渥太華體育會": (45.3986, -75.6833, "America/Toronto"),  # Atlético Ottawa - TD Place Stadium (Ottawa, Ontario)
    "卡瓦利": (50.8850, -114.1006, "America/Edmonton"),  # Cavalry FC - ATCO Field (Foothills County, Alberta, near Calgary)
    "漢密爾頓鍛造": (43.2526, -79.8302, "America/Toronto"),  # Forge FC - Tim Hortons Field (Hamilton, Ontario)
    "太平洋": (48.4342, -123.4250, "America/Vancouver"),  # Pacific FC - Starlight Stadium (Langford, British Columbia, near Victoria)
    "哈利法克斯流浪者": (44.6614, -63.6114, "America/Halifax"),  # HFX Wanderers FC - Wanderers Grounds (Halifax, Nova Scotia)
    "約克聯": (43.7725, -79.5039, "America/Toronto"),  # York United FC - York Lions Stadium (Toronto, Ontario)
    "溫哥華FC": (49.1650, -122.6500, "America/Vancouver"),  # Vancouver FC - Willoughby Community Park Stadium (Langley, British Columbia)
    "瓦盧爾": (49.8078, -97.1431, "America/Winnipeg"), # Valour FC - Princess Auto Stadium (Winnipeg, Manitoba)
    #哥倫比亞
    "杜利馬": (-4.4295, -75.2183, "America/Bogota"),  # Deportes Tolima - Estadio Manuel Murillo Toro (Ibagué)
    "麥德林獨立": (6.2447, -75.5897, "America/Bogota"),  # Independiente Medellín - Estadio Atanasio Girardot (Medellín)
    "青年體育會": (10.9272, -74.7997, "America/Bogota"),  # Junior F.C. - Estadio Metropolitano Roberto Meléndez (Barranquilla)
    "國民體育會": (6.2447, -75.5897, "America/Bogota"),  # Atlético Nacional - Estadio Atanasio Girardot (Medellín)
    "聖達菲": (4.6461, -74.0775, "America/Bogota"),  # Independiente Santa Fe - Estadio Nemesio Camacho El Campín (Bogotá)
    "卡利阿美利加": (3.4299, -76.5411, "America/Bogota"),  # América de Cali - Estadio Olímpico Pascual Guerrero (Cali)
    "布卡拉曼格體育會": (7.0520, -73.0809, "America/Bogota"),  # Atlético Bucaramanga - Estadio Álvaro Gómez Hurtado (Floridablanca)
    "米倫拿列奧": (4.6461, -74.0775, "America/Bogota"),  # Millonarios F.C. - Estadio Nemesio Camacho El Campín (Bogotá)
    "卡達斯": (5.0562, -75.4898, "America/Bogota"),  # Once Caldas - Estadio Palogrande (Manizales)
    "巴耶杜帕爾聯": (10.4636, -73.2536, "America/Bogota"),  # Alianza Valledupar F.C. - Estadio Armando Maestre Pavajeau (Valledupar)
    "福塔雷薩FC": (4.6097, -74.0811, "America/Bogota"),  # Fortaleza F.C. - Estadio Metropolitano de Techo (Bogotá)
    "阿古拿斯": (6.1553, -75.4267, "America/Bogota"),  # Águilas Doradas - Estadio Alberto Grisales (Rionegro)
    "帕斯度": (1.2136, -77.2811, "America/Bogota"),  # Deportivo Pasto - Estadio Departamental Libertad (Pasto)
    "佩雷拉": (4.8133, -75.6944, "America/Bogota"),  # Deportivo Pereira - Estadio Hernán Ramírez Villegas (Pereira)
    "卡利": (3.4299, -76.5411, "America/Bogota"),  # Deportivo Cali - Estadio Deportivo Cali (Palmira, near Cali)
    "蘭尼羅斯": (4.1500, -73.6333, "America/Bogota"),  # Llaneros F.C. - Estadio Manuel Calle Lombana (Villavicencio)
    "恩維加多": (6.1758, -75.5917, "America/Bogota"),  # Envigado F.C. - Estadio Polideportivo Sur (Envigado)
    "博亞卡捷高": (5.0689, -73.6167, "America/Bogota"),  # Boyacá Chicó F.C. - Estadio La Independencia (Tunja)
    "曼達朗拿": (11.2404, -74.2110, "America/Bogota"),  # Unión Magdalena - Estadio Sierra Nevada (Santa Marta)
    "伊基達": (4.6235, -74.1356, "America/Bogota"),   # La Equidad - Estadio Metropolitano de Techo (Bogotá)
    #NPL Victoria (維多利亞州)
    "南墨爾本": (-37.8350, 144.9600, "Australia/Melbourne"),  # South Melbourne - Lakeside Stadium (Albert Park, Melbourne)
    "海德堡聯": (-37.7250, 145.0389, "Australia/Melbourne"),  # Heidelberg United - Olympic Village (Heidelberg West)
    "侯城": (-37.8409, 144.9465, "Australia/Melbourne"),  # Hume City - John Ilhan Memorial Reserve (Broadmeadows)
    "丹德農城": (-37.9667, 145.2167, "Australia/Melbourne"),  # Dandenong City - Frank Holohan Soccer Complex (Dandenong)

    
    #NPL NSW (新南威爾士州)
    "馬科尼斯塔利昂": (-33.8500, 150.8833, "Australia/Sydney"),
    "悉尼聯58": (-33.9167, 151.0333, "Australia/Sydney"),
    "伍倫貢狼": (-34.4333, 150.8667, "Australia/Sydney"),
    "洛克代爾伊林登": (-33.9500, 151.1333, "Australia/Sydney"),
    "悉尼奧林匹克": (-33.8500, 151.0500, "Australia/Sydney"),
    "聖喬治城": (-33.9667, 151.1167, "Australia/Sydney"),
    "薩瑟蘭鯊魚": (-34.0333, 151.0667, "Australia/Sydney"),
    #NPL Queensland (昆士蘭州)
    "獅子": (-27.4500, 153.0500, "Australia/Brisbane"),

    "半島力量": (-27.2260, 153.0880, "Australia/Brisbane"),
    "莫頓城卓越": (-27.3580, 152.9700, "Australia/Brisbane"),
    "陽光海岸流浪者": (-26.6500, 153.0667, "Australia/Brisbane"),
    "布里斯班城": (-27.4667, 153.0167, "Australia/Brisbane"),
    "羅奇代爾漫遊者": (-27.5833, 153.1167, "Australia/Brisbane"),
    "布里斯班獅吼B隊": (-27.5833, 153.0500, "Australia/Brisbane"),  # Brisbane Roar Youth / Brisbane Roar U23 - Underwood Park / Ballymore Stadium (Brisbane area)
    "布里斯班東區": (-27.4870, 153.0470, "Australia/Brisbane"),  # Eastern Suburbs - Heath Park (Brisbane)
    "黃金海岸騎士": (-28.0167, 153.4000, "Australia/Brisbane"),  # Gold Coast Knights - Croatian Sports Centre / Knights Sports Complex (Gold Coast)
    "FC獅子": (-27.4500, 153.0500, "Australia/Brisbane"),  # FC Lions - Lions Stadium (Brisbane)
    "魔術聯": (-37.8450, 144.8130, "Australia/Brisbane"),  # Magic United - Magic United Field (Gold Coast, but wait: Magic United is Gold Coast based)
    "半島電力": (-27.2260, 153.0880, "Australia/Brisbane"),  # Peninsula Power - A.J. Kelly Park (Redcliffe)
    "羅奇代爾流浪": (-27.5833, 153.1167, "Australia/Brisbane"),  # Rochedale Rovers - Underwood Park (Rochedale)
    "溫納姆狼隊": (-27.4780, 153.1170, "Australia/Brisbane"),  # Wynnum Wolves - Carmichael Park (Wynnum)
    
    #NPL South Australia (南澳洲)
    "阿德萊德城": (-34.9333, 138.5833, "Australia/Adelaide"),
    "坎貝爾敦城": (-34.9500, 138.6667, "Australia/Adelaide"),
    "東北都會星": (-34.8667, 138.6667, "Australia/Adelaide"),
    "克羅伊登國王": (-34.9000, 138.5667, "Australia/Adelaide"),
    "莫德伯里噴射機": (-34.8333, 138.7000, "Australia/Adelaide"),
    "白城": (-34.9167, 138.5833, "Australia/Adelaide"),
    "阿德萊德奧林匹克": (-34.9500, 138.6000, "Australia/Adelaide"),
    "萊卡特": (-33.9667, 151.1167, "Australia/Sydney"),
    "格連古利": (-33.7667, 150.9167, "Australia/Sydney"),
    "卡羅琳泉佐治十字": (-37.7167, 144.7500, "Australia/Melbourne"),
    
    #NPL Western Australia (西澳洲)
    "珀斯紅星": (-31.9500, 115.8500, "Australia/Perth"),
    "弗洛里亞特雅典娜": (-31.9333, 115.8000, "Australia/Perth"),
    "斯特靈馬其頓": (-31.8833, 115.8333, "Australia/Perth"),
    "貝斯沃特城": (-31.9167, 115.9167, "Australia/Perth"),
    "奧林匹克金斯威": (-31.9500, 115.8500, "Australia/Perth"),
    "阿馬代爾": (-32.1500, 116.0167, "Australia/Perth"),
    "珀斯SC": (-31.9500, 115.8500, "Australia/Perth"),
    #NPL Tasmania (塔斯馬尼亞州)
    "南霍巴特": (-42.8833, 147.3333, "Australia/Hobart"),
    "格倫奧奇騎士": (-42.8333, 147.2833, "Australia/Hobart"),
    "金堡獅": (-42.9667, 147.3167, "Australia/Hobart"),
    "朗塞斯頓城": (-41.4333, 147.1500, "Australia/Hobart"),
    "克拉倫斯斑馬": (-42.8667, 147.3667, "Australia/Hobart"),
    #
    "蘭頓賈法斯": (-32.9167, 151.7333, "Australia/Sydney"),
    "埃奇沃思老鷹": (-32.9167, 151.7333, "Australia/Sydney"),
    "梅特蘭": (-32.7333, 151.5500, "Australia/Sydney"),
    "布羅德梅多魔法": (-32.9167, 151.7333, "Australia/Sydney"),
    "紐卡斯爾奧林匹克": (-32.9167, 151.7333, "Australia/Sydney"),
    "堪培拉克羅埃西亞": (-35.2833, 149.1333, "Australia/Sydney"),
    #
    "貢加林聯": (-35.1833, 149.1333, "Australia/Sydney"),
    "老虎FC": (-35.2500, 149.0833, "Australia/Sydney"),
    "莫納羅黑豹": (-35.3667, 149.2333, "Australia/Sydney"),
    "奧康納騎士": (-35.2667, 149.1167, "Australia/Sydney"),
    "東方獅子": (-37.8528, 145.1028, "Australia/Melbourne"),  # Eastern Lions SC - Gardiners Reserve, Burwood East, Victoria
    
    "西堪培拉流浪者": (-35.3167, 149.0833, "Australia/Sydney"),  # West Canberra Wanderers - Melrose Synthetic
    "堪培拉奧林匹克": (-35.3000, 149.1333, "Australia/Sydney"),  # Canberra Olympic - O'Connor Enclosed Oval (shared)
    "亞當斯頓羅斯巴德": (-32.9167, 151.7333, "Australia/Sydney"),  # Adamstown Rosebud - Adamstown Oval

    "查爾斯頓藍軍": (-32.9167, 151.6667, "Australia/Sydney"),  # Charlestown Azzurri - Lisle Carr Oval
    "庫克斯希爾聯": (-32.8333, 151.6667, "Australia/Sydney"),  # Cooks Hill United - Fearnley Dawes Athletic Centre
    "紐蘭姆頓": (-32.9167, 151.7333, "Australia/Sydney"),  # New Lambton - Alder Park
    "瓦倫丁鳳凰": (-32.9167, 151.6667, "Australia/Sydney"),  # Valentine Phoenix - Cahill Oval
    "韋斯頓工人熊": (-32.8167, 151.6667, "Australia/Sydney"),  # Weston Workers Bears - Rockwell Automation Park
    "萊克麥覺利聯": (-32.9167, 151.7333, "Australia/Sydney"),  # Lake Macquarie City - Macquarie Field
    "戴文波特城": (-41.0500, 146.3667, "Australia/Hobart"),  # Devonport City - Valley Road Ground
    "霍巴特斑馬": (-42.8667, 147.3667, "Australia/Hobart"),  # Hobart Zebras - Wentworth Park (shared)

    "河邊奧林匹克": (-41.0500, 147.1333, "Australia/Hobart"),  # Riverside Olympic - Windsor Park
    "弗里曼特爾城": (-32.0667, 115.7667, "Australia/Perth"),  # Fremantle City - Hilton Park
    "因格爾伍德聯": (-31.9167, 115.8833, "Australia/Perth"),  # Inglewood United - Inglewood Stadium

    "西部騎士": (-31.9000, 115.8333, "Australia/Perth"),  # Western Knights - Nash Field
    "珀斯光榮青年隊": (-31.9500, 115.8500, "Australia/Perth"),  # Perth Glory Youth - Dorrien Gardens (shared)
    "巴爾卡塔": (-31.8667, 115.8333, "Australia/Perth"),  # Balcatta Etna - Grindleford Reserve
    "阿德萊德彗星": (-34.9167, 138.6167, "Australia/Adelaide"),  # Adelaide Comets - SA Athletics Stadium
    "阿德萊德藍鷹": (-34.8833, 138.5667, "Australia/Adelaide"),  # Adelaide Blue Eagles - Marden Sports Complex
    "阿德萊德雷德斯": (-34.9167, 138.6000, "Australia/Adelaide"),  # Adelaide Raiders - Croatian Sports Centre
    "南阿德萊德黑豹": (-34.9833, 138.5333, "Australia/Adelaide"),  # South Adelaide Panthers - O'Sullivan Beach Sports Complex
    "西托倫斯比卡拉": (-34.9500, 138.5500, "Australia/Adelaide"),  # West Torrens Birkalla - Jack Smith Park
    "阿德萊德維克托": (-34.9167, 138.5333, "Australia/Adelaide"),  # West Adelaide - Adelaide Shores Football Centre
    "布里斯班獅吼青年隊": (-27.5833, 153.0500, "Australia/Brisbane"),  # Brisbane Roar Youth - Underwood Park
    "布里斯班獅吼女足": (-27.5833, 153.0500, "Australia/Brisbane"),  # Brisbane Roar Youth - Underwood Park
    "布里斯班前鋒": (-27.4450, 153.0330, "Australia/Brisbane"),  # Brisbane Strikers - Perry Park
    "黃金海岸聯": (-28.0667, 153.4167, "Australia/Brisbane"),  # Gold Coast United - Coplick Family Sports Park
    "獅吼": (-27.4667, 153.0167, "Australia/Brisbane"),  # Lions FC - Lions Stadium
    "奧林匹克FC": (-27.4667, 153.0167, "Australia/Brisbane"),  # Olympic FC - Goodwin Park
    "紅地流浪者": (-27.2300, 153.0333, "Australia/Brisbane"),  # Redlands United - Cleveland Showgrounds
    "伍爾夫斯FC": (-27.4780, 153.1170, "Australia/Brisbane"),  # WDSC Wolves - Carmichael Park
    "中央海岸水手學院": (-33.3819, 151.3708, "Australia/Sydney"),  # Central Coast Mariners Academy - Pluim Park
    "杜魯伊特鎮流浪者": (-33.7700, 150.8183, "Australia/Sydney"),  # Mount Druitt Town Rangers - Popondetta Park
    "聖喬治FC": (-33.9578, 151.0333, "Australia/Sydney"),  # St George FC - Penshurst Park
    "悉尼FC青年隊": (-33.9639, 151.1444, "Australia/Sydney"),  # Sydney FC Youth - Ilinden Sports Centre (shared)
    "西悉尼流浪者青年隊": (-33.7819, 150.8556, "Australia/Sydney"),  # Western Sydney Wanderers Youth - Wanderers Football Park
    "西悉尼流浪者B隊": (-33.7819, 150.8556, "Australia/Sydney"), 
    "西悉尼流浪者女足": (-33.7819, 150.8556, "Australia/Sydney"), 
    "西部狂怒": (-33.8250, 151.0125, "Australia/Sydney"), # Western Rage / Granville Rage - Garside Park
    "騎警流浪": (-33.8949, 150.8985, "Australia/Sydney"),
    "臥龍崗狼隊": (-34.4250, 150.8931, "Australia/Sydney"),
    "新南威爾斯大學FC": (-33.9173, 151.2253, "Australia/Sydney"),  # UNSW FC / New South Wales University FC - The Village Green (UNSW Kensington Campus, Sydney)
    "丹德農雷霆": (-37.9875, 145.2149, "Australia/Melbourne"),  # Dandenong Thunder - George Andrews Reserve (Dandenong, Victoria)
    "墨爾本城B隊": (-37.8409, 144.9465, "Australia/Melbourne"),  # Melbourne City FC Youth / B隊 - Various (often AAMI Park or training grounds in Melbourne)
    "奧克萊加農炮": (-37.9061, 145.0989, "Australia/Melbourne"),  # Oakleigh Cannons - Jack Edwards Reserve (Oakleigh, Victoria)
    "普雷斯頓雄獅": (-37.7583, 144.9986, "Australia/Melbourne"),  # Preston Lions FC - B.T. Connor Reserve (Preston, Victoria)
    "洛克達爾以利亞日": (-33.9639, 151.1444, "Australia/Sydney"),
    "艾東拿魔術": (-37.8617, 144.8127, "Australia/Melbourne"),
    "摩頓城精英隊": (-27.3580, 152.9700, "Australia/Brisbane"),
    "聖奧爾本斯戴拿模": (-37.7450, 144.8050, "Australia/Melbourne"),
    #澳洲南威爾斯州
    "悉尼聯": (-33.8736, 150.8664, "Australia/Sydney"),  # Sydney United - Sydney United Sports Centre (Edensor Park)
    "馬可尼斯塔利昂": (-33.8597, 150.8836, "Australia/Sydney"),  # Marconi Stallions - Marconi Stadium (Bossley Park)
    "聖佐治城": (-33.9625, 151.0889, "Australia/Sydney"),  # St George City - Ilinden Sports Centre (Rockdale)
    "黑鎮城": (-33.7708, 150.9125, "Australia/Sydney"),  # Blacktown City - Gabbie Stadium (Seven Hills)
    "曼利聯": (-33.7306, 151.2958, "Australia/Sydney"),  # Manly United - Cromer Park (Dee Why)
    "NWS精神": (-33.7875, 151.1189, "Australia/Sydney"),  # NWS Spirit - Christie Park (North Ryde)
    "悉尼FC B隊": (-33.9639, 151.1444, "Australia/Sydney"),  # Sydney FC Youth - Ilinden Sports Centre (shared) or Jubilee Stadium (Kogarah)
    "聖佐治FC": (-33.9578, 151.0333, "Australia/Sydney"),  # St George FC - Penshurst Park (Penshurst)
    "APIA利奇哈特": (-33.8778, 151.1550, "Australia/Sydney"),  # APIA Leichhardt - Lambert Park (Leichhardt)
    "賓特利綠軍": (-37.7450, 144.8050, "Australia/Melbourne"),  # Green Gully - Green Gully Reserve (Keilor Downs)  # 注意：表格中「賓特利綠軍」屬維州NPL，但若跨州誤列，請確認
    "南區奇兵": (-33.9235, 150.9478, "Australia/Sydney"),  # Southern Districts Raiders - Ernie Smith Reserve (Moorebank)
    #澳職女足
    "坎培拉聯女足": (-35.2833, 149.1333, "Australia/Sydney"),
    #烏拉圭甲組聯賽
    "馬爾多納多": (-34.9111, -54.9500, "America/Montevideo"),  # Club Atlético Maldonado - Estadio Domingo Burgueño (Maldonado)
    "達奴比奧": (-34.7264, -56.2208, "America/Montevideo"),  # Danubio FC - Jardines del Hipódromo (Montevideo)
    "迪芬沙士砵亭": (-34.9167, -56.1667, "America/Montevideo"),  # Defensor Sporting - Estadio Luis Franzini (Montevideo)
    "蒙特維多流浪": (-34.8606, -56.1667, "America/Montevideo"),  # Montevideo Wanderers - Estadio Alfredo Víctor Viera (Montevideo)
    "蒙特維多國民隊": (-34.8847, -56.1528, "America/Montevideo"),  # Club Nacional de Football - Gran Parque Central (Montevideo)
    "艾比安FC": (-34.7264, -56.2208, "America/Montevideo"),
    "彭拿路": (-34.9011, -56.1883, "America/Montevideo"),  # C.A. Peñarol - Estadio Campeón del Siglo (Montevideo)
    "蒙特維多利物浦": (-34.7264, -56.2208, "America/Montevideo"),  # Montevideo City Torque - Estadio Centenario (Montevideo)
    "切洛拉高": (-31.3833, -54.2833, "America/Montevideo"),  # Cerro Largo FC - Estadio Antonio Ubilla (Melo)
    "拿斯派達斯青年": (-34.7333, -56.4667, "America/Montevideo"),  # Juventud de Las Piedras - Estadio Parque Artigas (Las Piedras)
    "蒙特維多多托基": (-34.8500, -56.2133, "America/Montevideo"),  # Montevideo City Torque - Estadio Centenario (Montevideo, shared)
    "蒙特維多競賽會": (-34.8847, -56.1528, "America/Montevideo"),
    "切洛": (-34.8833, -56.2333, "America/Montevideo"),
    "CA格雷克雷": (-34.7264, -56.2208, "America/Montevideo"),  # CA River Plate - Estadio Federico Saroldi (Montevideo)
    "尤文提度": (-34.7264, -56.2208, "America/Montevideo"),

    
    #希臘超級聯賽
    "奧林比亞高斯": (37.9461, 23.6644, "Europe/Athens"), # Olympiacos - Karaiskakis Stadium
    "彭拿典奈高斯": (37.9872, 23.7542, "Europe/Athens"), # Panathinaikos - Leoforos Alexandras Stadium
    "PAOK薩隆尼卡": (40.6139, 22.9725, "Europe/Athens"), # PAOK - Toumba Stadium
    "AEK雅典": (38.0364, 23.7425, "Europe/Athens"), # AEK Athens - Agia Sophia Stadium
    "雅典AEK": (38.0364, 23.7425, "Europe/Athens"), # AEK Athens - Agia Sophia Stadium
    "阿里斯": (40.6000, 22.9692, "Europe/Athens"), # Aris - Kleanthis Vikelidis Stadium
    "特里波利星": (37.5100, 22.3725, "Europe/Athens"), # Asteras Tripolis - Theodoros Kolokotronis Stadium
    "阿特羅米托斯": (38.0056, 23.7167, "Europe/Athens"), # Atromitos - Peristeri Stadium
    "利瓦迪亞科斯": (38.4361, 22.8733, "Europe/Athens"), # Levadiakos - Levadia Municipal Stadium
    "OFI克里特": (35.3375, 25.1061, "Europe/Athens"), # OFI - Pankritio Stadium
    "潘尼杜列高斯": (38.6231, 21.4083, "Europe/Athens"), # Panetolikos - Panetolikos Stadium
    "潘塞萊科斯": (41.0889, 23.5486, "Europe/Athens"), # Panserraikos - Serres Municipal Stadium
    "沃洛斯": (39.3783, 22.9308, "Europe/Athens"), # Volos - Panthessaliko Stadium
    "基菲西亞": (38.0739, 23.7778, "Europe/Athens"), # A.E. Kifisia - Michalis Kritikopoulos Stadium
    "拉里薩": (39.6222, 22.4194, "Europe/Athens"), # AEL - AEL FC Arena
    #冰島超級聯賽
    "布雷達比歷克": (64.0986, -21.9672, "Atlantic/Reykjavik"), # Breiðablik - Kópavogsvöllur, Kópavogur
    "FH哈夫納費奧德": (64.0672, -21.9328, "Atlantic/Reykjavik"), # FH - Kaplakrikavöllur, Hafnarfjörður
    "弗拉姆": (64.1333, -21.9333, "Atlantic/Reykjavik"), # Fram - Laugardalsvöllur, Reykjavík
    "費基爾": (64.1125, -21.9125, "Atlantic/Reykjavik"), # Fylkir - Fylkisvöllur, Reykjavík
    "HK科帕沃古爾": (64.1125, -21.9125, "Atlantic/Reykjavik"), # HK - Kórinn, Kópavogur
    "阿克拉內斯": (64.3214, -22.0714, "Atlantic/Reykjavik"), # ÍA - Akranesvöllur, Akranes
    "KA阿克雷里": (65.6839, -18.0878, "Atlantic/Reykjavik"), # KA - Akureyrarvöllur, Akureyri
    "KR雷克雅未克": (64.1355, -21.8954, "Atlantic/Reykjavik"), # KR - KR-völlur, Reykjavík
    "史達南": (64.0889, -21.9222, "Atlantic/Reykjavik"), # Stjarnan - Samsungvöllur, Garðabær
    "華路爾": (64.1355, -21.8954, "Atlantic/Reykjavik"), # Valur - Hlíðarendi, Reykjavík
    "韋斯特里": (66.0722, -23.1194, "Atlantic/Reykjavik"), # Vestri - Olísvöllurinn, Ísafjörður
    "維京古爾雷克雅維克": (64.1355, -21.8954, "Atlantic/Reykjavik"), # Víkingur Reykjavík - Víkingsvöllur, Reykjavík
    #其他
    "伊斯坦布爾": (41.01, 28.95, "Europe/Istanbul"),
    "艾祖拉": (33.3153, 44.3661, "Asia/Baghdad"),
    "阿卡達": (38.0601, 58.081, "Asia/Ashgabat"),
    "布拉格斯巴達女足": (50.0675, 14.4158, "Europe/Prague"),
    "沙巴罕": (32.6535, 51.6660, "Asia/Tehran"),
    "卡爾斯耶拿女足": (50.9297, 11.5906, "Europe/Berlin"),
    "法蘭克福女足": (50.0686, 8.6455, "Europe/Berlin"),
    "赫根女足": (57.7192, 11.9306, "Europe/Stockholm"), # BK Häcken FF Women - Bravida Arena, Gothenburg
    "奧特海維利女足": (56.8769, 14.8092, "Europe/Stockholm"), # Östers IF Women - Värendsvallen, Växjö
    "巴黎FC女足": (48.8186, 2.3467, "Europe/Paris"), # Paris FC Women - Stade Sébastien Charléty, Paris
    #伊朗
    "拖拉機": (38.0275, 46.2950, "Asia/Tehran"),  # Tractor - Sahand Stadium (Tabriz)
    "柏斯波里斯": (35.7247, 51.2756, "Asia/Tehran"),  # Persepolis - Azadi Stadium (Tehran)
    "塞帕漢": (32.7522, 51.6781, "Asia/Tehran"),  # Sepahan - Naghsh-e Jahan Stadium (Isfahan)
    "艾斯迪格拿": (35.7247, 51.2756, "Asia/Tehran"),  # Esteghlal - Azadi Stadium (Tehran)
    "富拉德": (31.3203, 48.6706, "Asia/Tehran"),  # Foolad - Foolad Arena (Ahvaz)
    "馬拉萬": (37.4758, 49.4625, "Asia/Tehran"),  # Malavan - Sirous Ghanbari Stadium (Bandar-e Anzali)
    "戈爾戈哈爾": (29.1392, 55.6725, "Asia/Tehran"),  # Gol Gohar - Gol Gohar Sport Complex (Sirjan)
    "沙姆斯阿扎爾": (36.2667, 48.4833, "Asia/Tehran"),  # Shams Azar - Sardar Jangal Stadium (Qazvin)
    "胡齊斯坦獨立": (31.3203, 48.6706, "Asia/Tehran"),  # Esteghlal Khuzestan - Ghadir Stadium (Ahvaz)
    "查多馬魯": (31.9667, 54.3667, "Asia/Tehran"),  # Chadormalu - Nasiri Stadium (Yazd)
    "凱巴爾霍拉馬巴德": (33.5342, 48.3528, "Asia/Tehran"),  # Kheybar Khorramabad - Takhti Stadium (Khorramabad)
    "哈瓦達爾": (35.6892, 51.4097, "Asia/Tehran"),  # Havadar - Dastgerdi Stadium (Tehran)
    "馬贊德蘭納薩吉": (36.4667, 51.5000, "Asia/Tehran"),  # Nassaji Mazandaran - Vatani Stadium (Qaem Shahr)
    "阿拉克鋁": (34.0942, 49.7025, "Asia/Tehran"),  # Aluminium Arak - Imam Khomeini Stadium (Arak)
    "拉夫桑詹銅": (31.1167, 55.9833, "Asia/Tehran"),  # Mes Rafsanjan - Shohadaye Mes Stadium (Rafsanjan)
    "佐布阿漢": (32.7522, 51.6781, "Asia/Tehran"),  # Zob Ahan - Foolad Shahr Stadium (Isfahan)
    #波蘭超級聯賽
    "華沙軍團": (52.2206, 21.0408, "Europe/Warsaw"),  # Legia Warszawa - Stadion Wojska Polskiego
    "拉科夫": (50.7725, 19.1389, "Europe/Warsaw"),  # Raków Częstochowa - Stadion Rakowa
    "波茲南萊赫": (52.3975, 16.8578, "Europe/Warsaw"),  # Lech Poznań - Stadion Poznań
    "雅蓋隆尼亞": (53.1317, 23.1461, "Europe/Warsaw"),  # Jagiellonia Białystok - Stadion Miejski w Białymstoku
    "斯拉希亞": (51.1411, 16.9436, "Europe/Warsaw"),  # Śląsk Wrocław - Stadion Wrocław
    "普沃茨克維斯瓦": (52.5625, 19.6850, "Europe/Warsaw"),  # Wisła Płock - Stadion im. Kazimierza Górskiego
    "哥爾尼克扎布熱": (50.2961, 18.7689, "Europe/Warsaw"),  # Górnik Zabrze - Stadion im. Ernesta Pohla
    "克拉科夫維斯瓦": (50.0639, 19.9111, "Europe/Warsaw"),  # Wisła Kraków - Stadion Miejski im. Henryka Reymana
    "波戈尼斯什切青": (53.4353, 14.5214, "Europe/Warsaw"),  # Pogoń Szczecin - Stadion Miejski im. Floriana Krygiera
    "克拉科維亞": (50.0614, 19.9236, "Europe/Warsaw"),  # Cracovia - Stadion Cracovii im. Józefa Piłsudskiego
    "皮亞斯特格利維采": (50.3064, 18.6956, "Europe/Warsaw"),  # Piast Gliwice - Stadion Miejski w Gliwicach
    "扎布熱戈爾尼克": (50.2961, 18.7689, "Europe/Warsaw"),  # Górnik Zabrze - Stadion im. Ernesta Pohla (重複球隊，共用主場)
    "格但斯克萊希亞": (54.3914, 18.5306, "Europe/Warsaw"),  # Lechia Gdańsk - Polsat Plus Arena Gdańsk
    "拉德米亞克拉多姆": (51.3933, 21.1583, "Europe/Warsaw"),  # Radomiak Radom - Stadion im. Braci Czachorów
    "普斯查涅波沃米采": (50.0100, 20.1700, "Europe/Warsaw"),  # Puszcza Niepołomice - Stadion Miejski w Niepołomicach
    "格羅德茲斯卡": (52.2333, 21.0167, "Europe/Warsaw"),  # GKS Katowice - Stadion GKS Katowice
    "貝爾哈圖": (50.2978, 18.6767, "Europe/Warsaw"),
    #西甲女足
    "畢爾包女足": (43.2642, -2.9494, "Europe/Madrid"),  # Athletic Bilbao Femenino - San Mamés Stadium (Bilbao, Spain)
    "皇家蘇斯達女足": (43.3014, -1.9736, "Europe/Madrid"),  # Real Sociedad Femenino - Reale Arena / Anoeta (San Sebastián, Spain) 或 Zubieta facilities
    "阿拉馬女足": (37.8542, -1.4269, "Europe/Madrid"),  # Alhama CF El Pozo - Complejo Deportivo Guadalentín (Alhama de Murcia, Spain)
    "皇家馬德里女足": (40.4769, -3.6143, "Europe/Madrid"),  # Real Madrid Femenino - Alfredo Di Stéfano Stadium (Valdebebas, Madrid)
    "海牙女足": (52.0628, 4.3831, "Europe/Amsterdam"),  # ADO Den Haag Vrouwen - Bingoal Stadion / WerkTalent Stadion (The Hague, Netherlands)
    "飛燕諾女足": (51.8913, 4.5250, "Europe/Amsterdam"),  # Feyenoord Vrouwen - Sportcomplex Varkenoord (Rotterdam, Netherlands)
    "帕爾馬女足": (44.7950, 10.3383, "Europe/Rome"),  # Parma Calcio 1913 Women - Stadio Ennio Tardini (Parma, Italy)
    "國際米蘭女足": (45.4758, 9.1792, "Europe/Rome"),   # Inter Milan Women - Arena Civica (Milan, Italy)
    #馬來西亞
    "柔佛DT": (1.4925, 103.7603, "Asia/Kuala_Lumpur"),  # Johor Darul Ta'zim - Sultan Ibrahim Stadium (Iskandar Puteri, Johor)
    "雪蘭莪": (3.0760, 101.5403, "Asia/Kuala_Lumpur"),  # Selangor FC - Petaling Jaya Stadium / MBPJ Stadium (Petaling Jaya)
    "登嘉樓": (5.3333, 103.1500, "Asia/Kuala_Lumpur"),  # Terengganu FC - Sultan Ismail Nasiruddin Shah Stadium (Kuala Terengganu)
    "吉隆坡城": (3.1357, 101.6880, "Asia/Kuala_Lumpur"),  # Kuala Lumpur City FC - KLFA Stadium / Petaling Jaya Stadium (shared)
    "沙巴": (5.9800, 116.0733, "Asia/Kuala_Lumpur"),  # Sabah FC - Likas Stadium (Kota Kinabalu)
    "霹靂": (4.8500, 100.7333, "Asia/Kuala_Lumpur"),  # Perak FC - Perak Stadium (Ipoh)
    "彭亨": (3.8167, 103.3333, "Asia/Kuala_Lumpur"),  # Pahang FC - Darul Makmur Stadium (Kuantan)
    "檳城": (5.4141, 100.3288, "Asia/Kuala_Lumpur"),  # Penang FC - City Stadium (George Town)
    "PDRM": (3.0833, 101.6833, "Asia/Kuala_Lumpur"),  # PDRM FC - Selayang Stadium (Selangor)
    "吉打": (6.1167, 100.3667, "Asia/Kuala_Lumpur"),  # Kedah Darul Aman FC - Darul Aman Stadium (Alor Setar)
    "森美蘭": (2.7333, 101.9500, "Asia/Kuala_Lumpur"),  # Negeri Sembilan FC - Tuanku Abdul Rahman Stadium (Seremban)
    "馬六甲": (2.2000, 102.2500, "Asia/Kuala_Lumpur"),  # Melaka United - Hang Tuah Stadium (Melaka)
    "雪蘭莪2": (3.0760, 101.5403, "Asia/Kuala_Lumpur"),  # Selangor 2 / Selangor II - UiTM Stadium (Shah Alam, reserve team)
    "吉隆坡聯": (3.1357, 101.6880, "Asia/Kuala_Lumpur"),  # Kuching City FC - Sarawak Stadium (Kuching, Sarawak - 但聯賽中常駐吉隆坡或共享)
    #以色列
    "馬卡比海法": (32.8186, 35.0000, "Asia/Jerusalem"),  # Maccabi Haifa - Sammy Ofer Stadium (Haifa)
    "貝爾謝巴夏普爾": (31.2667, 34.7833, "Asia/Jerusalem"),  # Hapoel Be'er Sheva - Toto Turner Stadium (Be'er Sheva)
    "耶路撒冷貝塔爾": (31.8000, 35.2167, "Asia/Jerusalem"),  # Beitar Jerusalem - Teddy Stadium (Jerusalem)
    "特拉維夫馬卡比": (32.0478, 34.7800, "Asia/Jerusalem"),  # Maccabi Tel Aviv - Bloomfield Stadium (Tel Aviv)
    "特拉維夫夏普爾": (32.0478, 34.7800, "Asia/Jerusalem"),  # Hapoel Tel Aviv - Bloomfield Stadium (shared)
    "海法夏普爾": (32.8186, 35.0000, "Asia/Jerusalem"),  # Hapoel Haifa - Sammy Ofer Stadium (shared)
    "內坦亞馬卡比": (32.3167, 34.8500, "Asia/Jerusalem"),  # Maccabi Netanya - Netanya Stadium (Netanya)
    "阿什杜德": (31.8000, 34.6500, "Asia/Jerusalem"),  # F.C. Ashdod - Yud-Alef Stadium (Ashdod)
    "基里亞特施莫納": (33.2167, 35.5667, "Asia/Jerusalem"),  # Hapoel Kiryat Shmona - Kiryat Shmona Municipal Stadium
    "貝內耶胡達": (32.0478, 34.7800, "Asia/Jerusalem"),  # Bnei Yehuda Tel Aviv - Bloomfield Stadium (shared)
    "佩塔提克瓦夏普爾": (32.0833, 34.8833, "Asia/Jerusalem"),  # Hapoel Petah Tikva - HaMoshava Stadium (Petah Tikva)
    "佩塔提克瓦馬卡比": (32.0833, 34.8833, "Asia/Jerusalem"),  # Maccabi Petah Tikva - HaMoshava Stadium (shared)
    "拉馬特甘哈波爾": (32.0667, 34.8167, "Asia/Jerusalem"),  # Hapoel Ramat Gan - Winter Stadium (Ramat Gan)
    "特拉維夫鐵錘": (32.0478, 34.7800, "Asia/Jerusalem"),  # Hapoel Ironi Tel Aviv / Ironi Ramat HaSharon - Various (shared)
    #哥斯達黎加甲級聯賽
    "薩普里沙": (9.9654, -84.0755, "America/Costa_Rica"),  # Deportivo Saprissa - Estadio Ricardo Saprissa Aymá (San Juan de Tibás)
    "希雷迪亞洛": (9.9986, -84.1231, "America/Costa_Rica"),  # Club Sport Herediano - Estadio Eladio Rosabal Cordero (Heredia)
    "阿拉祖蘭斯": (10.0200, -84.2111, "America/Costa_Rica"),  # Liga Deportiva Alajuelense - Estadio Alejandro Morera Soto (Alajuela)
    "聖卡洛斯": (10.3500, -84.4333, "America/Costa_Rica"),  # A.D. San Carlos - Estadio Carlos Ugalde Álvarez (Ciudad Quesada)
    "利比里亚": (10.6333, -85.4500, "America/Costa_Rica"),  # A.D. Municipal Liberia - Estadio Edgardo Baltodano Briceño (Liberia)
    "聖荷西體育會": (9.9281, -84.0900, "America/Costa_Rica"),  # Sporting F.C. - Estadio Nacional (San José)
    "瓜纳卡斯特": (10.0167, -85.4500, "America/Costa_Rica"),  # A.D. Guanacasteca - Estadio Chorotega (Nicoya)
    "佩雷斯薛尼當": (9.3667, -83.7000, "America/Costa_Rica"),  # Municipal Pérez Zeledón - Estadio Municipal de Pérez Zeledón (San Isidro)
    "卡達真尼斯": (9.8585, -83.9187, "America/Costa_Rica"),  # C.S. Cartaginés - Estadio José Rafael "Fello" Meza (Cartago)
    "普恩塔雷納斯": (9.9833, -84.8333, "America/Costa_Rica"),  # Puntarenas F.C. - Estadio Municipal de Puntarenas (Puntarenas)
    "格雷西亞": (10.0667, -84.3167, "America/Costa_Rica"),  # Municipal Grecia - Estadio Allen Riggioni (Grecia)
    "聖安娜": (9.9333, -84.1833, "America/Costa_Rica"),  # A.D. Municipal Santa Ana - Estadio Municipal de Santa Ana (Santa Ana)
    #多米尼加共和國足球甲級聯賽
    "錫寶": (19.4517, -70.6978, "America/Santo_Domingo"),  # Cibao FC - Estadio Cibao FC (Santiago de los Caballeros)
    "潘托哈競技": (18.4801, -69.9195, "America/Santo_Domingo"),  # Atlético Pantoja - Estadio Olímpico Félix Sánchez (Santo Domingo)
    "奧安德梅": (18.4801, -69.9195, "America/Santo_Domingo"),  # Universidad O&M - Estadio Olímpico Félix Sánchez (Santo Domingo, shared)
    "莫卡": (19.3933, -70.5250, "America/Santo_Domingo"),  # Moca FC - Estadio Complejo Deportivo Moca 86 (Moca)
    "維加皇家競技": (19.2210, -70.5290, "America/Santo_Domingo"),  # Atlético Vega Real - Estadio Olímpico (La Vega)
    "東部海豚": (18.4833, -69.8833, "America/Santo_Domingo"),  # Delfines Del Este - Estadio Félix Sánchez (Santo Domingo, shared)
    "大西洋": (19.7833, -70.6833, "America/Santo_Domingo"),  # Atlántico FC - Estadio Leonel Plácido (Puerto Plata)
    "聖克里斯托瓦爾競技": (18.4167, -70.1167, "America/Santo_Domingo"),  # Atlético San Cristóbal - Estadio Panamericano (San Cristóbal)
    "巴塞羅那": (18.4801, -69.9195, "America/Santo_Domingo"),  # Barcelona Atlético - Estadio Olímpico Félix Sánchez (Santo Domingo)
    "哈拉巴科阿": (19.1167, -70.6167, "America/Santo_Domingo"),  # Jarabacoa FC - Estadio Municipal de Jarabacoa (Jarabacoa)
    "薩爾塞多": (19.3778, -70.4167, "America/Santo_Domingo"),  # Salcedo FC - Estadio Domínguez (Salcedo)
    "聖塔菲": (18.4801, -69.9195, "America/Santo_Domingo"),  # Santa Fe - Estadio Olímpico Félix Sánchez (Santo Domingo, shared)
    #玻利維亞足球甲級聯賽
    "強者": (-16.5000, -68.1333, "America/La_Paz"),  # Club The Strongest - Estadio Hernando Siles (La Paz)
    "玻利瓦爾": (-16.5000, -68.1333, "America/La_Paz"),  # Club Bolívar - Estadio Hernando Siles (La Paz)
    "阿爾韋斯列迪": (-16.5000, -68.1333, "America/La_Paz"),  # Club Always Ready - Estadio Hernando Siles (La Paz, shared)
    "國民普托斯": (-19.5833, -65.7500, "America/La_Paz"),  # Nacional Potosí - Estadio Víctor Agustín Ugarte (Potosí)
    "極光球會": (-17.3833, -66.1500, "America/La_Paz"),  # Club Aurora - Estadio Félix Capriles (Cochabamba)
    "皇家杜馬耶保": (-21.5333, -64.7333, "America/La_Paz"),  # C.D. Real Tomayapo - Estadio IV Centenario (Tarija)
    "皇家聖克魯斯": (-17.8000, -63.1833, "America/La_Paz"),  # Real Santa Cruz - Estadio Ramón Tahuichi Aguilera (Santa Cruz)
    "威斯特曼": (-17.3833, -66.1500, "America/La_Paz"),  # Club Jorge Wilstermann - Estadio Félix Capriles (Cochabamba)
    "奧利恩特": (-17.8000, -63.1833, "America/La_Paz"),  # C.D. Oriente Petrolero - Estadio Ramón Tahuichi Aguilera (Santa Cruz)
    "賓托大學": (-17.3833, -66.1500, "America/La_Paz"),  # F.C. Universitario de Vinto - Estadio Municipal de Vinto (Vinto, Cochabamba)
    "帕爾米拉獨立隊": (-19.0333, -65.2667, "America/La_Paz"),  # Club Independiente Petrolero - Estadio Olímpico Patria (Sucre)
    "皇家帕里": (-17.8000, -63.1833, "America/La_Paz"),  # Royal Pari FC - Estadio Ramón Tahuichi Aguilera (Santa Cruz)
    "瓜比拉": (-17.3833, -63.2500, "America/La_Paz"),  # Club Deportivo Guabirá - Estadio Gilberto Parada (Montero)
    "邦明": (-17.8000, -63.1833, "America/La_Paz"),  # Club Blooming - Estadio Ramón Tahuichi Aguilera (Santa Cruz)
    "GV聖荷西": (-17.9667, -67.1167, "America/La_Paz"),  # GV San José - Estadio Víctor Agustín Ugarte (Oruro)
    "聖安東尼奧保布洛布洛": (-17.3833, -63.2500, "America/La_Paz"),  # C.D. San Antonio Bulo Bulo - Estadio Municipal de Entre Ríos (Entre Ríos)
    #千里達球隊
    "中央FC": (10.6525, -61.5000, "America/Port_of_Spain"),  # Central FC - Ato Boldon Stadium (Couva) 或 Hasely Crawford Stadium (Port of Spain)
    "警察FC": (10.6525, -61.5000, "America/Port_of_Spain"),  # Police FC - Various (often Hasely Crawford Stadium or Police Sports Club Ground)
    "國防部": (10.6525, -61.5000, "America/Port_of_Spain"),  # Defence Force - Hasely Crawford Stadium (Port of Spain)
    "莫克瓦": (10.6333, -61.4167, "America/Port_of_Spain"),  # Morvant Caledonia United - Morvant Recreation Ground (Morvant)
    "北東聯": (10.6525, -61.5000, "America/Port_of_Spain"),  # North East Stars - Various (often Arima Velodrome or Hasely Crawford)
    "點克魯斯": (10.2667, -61.4167, "America/Port_of_Spain"),  # Point Fortin Civic - Mahaica Sports Complex (Point Fortin)
    "俱樂部桑多斯": (10.6525, -61.5000, "America/Port_of_Spain"),  # Club Sando - Ato Boldon Stadium (Couva)
    "聖安東尼奧斯": (10.6525, -61.5000, "America/Port_of_Spain"),  # St. Ann's Rangers - Various (often Hasely Crawford Stadium)
    "拉芬加聯": (10.6333, -61.4333, "America/Port_of_Spain"),  # La Horquetta Rangers - La Horquetta Recreation Ground
    "終結者": (10.6525, -61.5000, "America/Port_of_Spain"),  # Terminix La Horquetta Rangers - La Horquetta Recreation Ground
    "刑事調查": (10.6525, -61.5000, "America/Port_of_Spain"),  # Police FC (重複或變體，共用主場)
    "俱樂部桑多": (10.6525, -61.5000, "America/Port_of_Spain"),  # Club Sando - Ato Boldon Stadium (Couva)
    #捷甲
    "布拉格斯拉維亞": (50.0678, 14.4711, "Europe/Prague"),  # SK Slavia Prague - Fortuna Arena / Sinobo Stadium (Prague)
    "柏辛域陀尼亞": (49.7478, 13.3775, "Europe/Prague"),  # FC Viktoria Plzeň - Doosan Arena (Plzeň)
    "奧斯泰華": (49.8039, 18.2669, "Europe/Prague"),  # FC Baník Ostrava - Městský stadion (Ostrava)
    "布拉格斯巴達": (50.1011, 14.4128, "Europe/Prague"),  # AC Sparta Prague - epet ARENA (Prague)
    "積布尼克": (50.7167, 15.1667, "Europe/Prague"),  # FK Jablonec - Stadion Střelnice (Jablonec nad Nisou)
    "奧洛慕克": (49.6000, 17.2500, "Europe/Prague"),  # SK Sigma Olomouc - Andrův stadion (Olomouc)
    "賀拉戴克": (50.2167, 15.8333, "Europe/Prague"),  # FC Hradec Králové - Lokotrans Aréna (Hradec Králové)
    "波希美恩斯1905": (50.1000, 14.4667, "Europe/Prague"),  # Bohemians 1905 - Ďolíček Stadium (Prague)
    "利巴域": (50.7667, 15.0500, "Europe/Prague"),  # FC Slovan Liberec - Stadion u Nisy (Liberec)
    "卡爾維納": (49.8333, 18.2833, "Europe/Prague"),  # MFK Karviná - Stadion města Karviná (Karviná)
    "塔比歷斯": (50.6500, 13.8333, "Europe/Prague"),  # FK Teplice - Na Stínadlech (Teplice)
    "波利斯拉夫": (50.4167, 14.9000, "Europe/Prague"),  # FK Mladá Boleslav - Stadion Mladá Boleslav (Mladá Boleslav)
    "斯洛華高": (49.0667, 17.4667, "Europe/Prague"),  # 1. FC Slovácko - Městský fotbalový stadion Miroslava Valenty (Uherské Hradiště)
    "杜克拉布拉格": (50.1167, 14.5000, "Europe/Prague"),  # FK Dukla Prague - Juliska Stadium (Prague)
    "帕爾杜比斯": (50.0417, 15.7767, "Europe/Prague"),  # FK Pardubice - Pod Vinicí (Pardubice)
    "施連": (49.2167, 17.6667, "Europe/Prague"),  # FC Zlín - Letná Stadion (Zlín)
    "特普利采": (50.6500, 13.8333, "Europe/Prague"),
    #丹麥超級聯賽
    "哥本哈根": (55.7027, 12.5716, "Europe/Copenhagen"),  # F.C. Copenhagen - Parken Stadium
    "米迪蘭特": (56.1169, 8.9517, "Europe/Copenhagen"),  # FC Midtjylland - MCH Arena (Herning)
    "北西蘭": (55.8158, 12.3533, "Europe/Copenhagen"),  # FC Nordsjælland - Right to Dream Park (Farum)
    "奧胡斯": (56.2000, 10.2167, "Europe/Copenhagen"),  # AGF Aarhus - Ceres Park (Aarhus)
    "布隆比": (55.6489, 12.4186, "Europe/Copenhagen"),  # Brøndby IF - Brøndby Stadium
    "蘭德斯": (56.4528, 10.0122, "Europe/Copenhagen"),  # Randers FC - Cepheus Park Randers
    "維堡": (56.4569, 9.4000, "Europe/Copenhagen"),  # Viborg FF - Energi Viborg Arena
    "錫爾克堡": (56.1842, 9.5751, "Europe/Copenhagen"),  # Silkeborg IF - JYSK Park
    "歐登塞": (55.3978, 10.3501, "Europe/Copenhagen"),  # Odense Boldklub - Nature Energy Park
    "松德比約斯克": (55.0236, 9.4911, "Europe/Copenhagen"),  # Sønderjyske - Sydbank Park (Haderslev)
    "韋勒": (55.7139, 9.5583, "Europe/Copenhagen"),  # Vejle Boldklub - Vejle Stadion
    "弗雷德里西亞": (55.5736, 9.7238, "Europe/Copenhagen"),  # FC Fredericia - Monjasa Park
    "奧爾堡": (57.0480, 9.9217, "Europe/Copenhagen"),
    #丹麥甲級
    "弗雷德里西亞": (55.5736, 9.7238, "Europe/Copenhagen"),  # FC Fredericia - Monjasa Park
    "韋勒": (55.7139, 9.5583, "Europe/Copenhagen"),  # Vejle Boldklub - Vejle Stadion
    "松德比約斯克": (55.0236, 9.4911, "Europe/Copenhagen"),  # Sønderjyske - Sydbank Park
    "霍爾森斯": (55.8667, 9.8500, "Europe/Copenhagen"),  # AC Horsens - CASA Arena Horsens
    "基爾斯霍爾姆": (55.6667, 9.1667, "Europe/Copenhagen"),  # Kolding IF - Kolding Stadium
    "弗雷姆阿馬格": (55.6333, 12.5833, "Europe/Copenhagen"),  # Fremad Amager - Valby Idrætspark
    "比靈布羅": (56.3667, 9.2167, "Europe/Copenhagen"),  # FC Helsingør - Helsingør Stadion
    "比靈布羅": (56.3667, 9.2167, "Europe/Copenhagen"),  # B93 Copenhagen - Østerbro Stadion
    "霍爾貝克": (55.7167, 11.7167, "Europe/Copenhagen"),  # Holbæk B&I - Holbæk Stadion
    "尼克賓": (55.7167, 11.7167, "Europe/Copenhagen"),  # Nykøbing FC - Nykøbing Falster Idrætspark
    "希爾勒勒": (55.9333, 12.3000, "Europe/Copenhagen"),  # Hillerød Fodbold - Hillerød Stadion
    "埃斯比約": (55.4667, 8.4500, "Europe/Copenhagen"),  # Esbjerg fB - Blue Water Arena
    #捷甲
    "布拉格斯拉維亞": (50.0678, 14.4711, "Europe/Prague"),  # SK Slavia Prague - Fortuna Arena / Sinobo Stadium (Prague)
    "柏辛域陀尼亞": (49.7478, 13.3775, "Europe/Prague"),  # FC Viktoria Plzeň - Doosan Arena (Plzeň)
    "奧斯泰華": (49.8039, 18.2669, "Europe/Prague"),  # FC Baník Ostrava - Městský stadion (Ostrava)
    "布拉格斯巴達": (50.1011, 14.4128, "Europe/Prague"),  # AC Sparta Prague - epet ARENA (Prague)
    "積布尼克": (50.7167, 15.1667, "Europe/Prague"),  # FK Jablonec - Stadion Střelnice (Jablonec nad Nisou)
    "奧洛慕克": (49.6000, 17.2500, "Europe/Prague"),  # SK Sigma Olomouc - Andrův stadion (Olomouc)
    "賀拉戴克": (50.2167, 15.8333, "Europe/Prague"),  # FC Hradec Králové - Lokotrans Aréna (Hradec Králové)
    "波希美恩斯1905": (50.1000, 14.4667, "Europe/Prague"),  # Bohemians 1905 - Ďolíček Stadium (Prague)
    "利巴域": (50.7667, 15.0500, "Europe/Prague"),  # FC Slovan Liberec - Stadion u Nisy (Liberec)
    "卡爾維納": (49.8333, 18.2833, "Europe/Prague"),  # MFK Karviná - Stadion města Karviná (Karviná)
    "塔比歷斯": (50.6500, 13.8333, "Europe/Prague"),  # FK Teplice - Na Stínadlech (Teplice)
    "波利斯拉夫": (50.4167, 14.9000, "Europe/Prague"),  # FK Mladá Boleslav - Stadion Mladá Boleslav (Mladá Boleslav)
    "斯洛華高": (49.0667, 17.4667, "Europe/Prague"),  # 1. FC Slovácko - Městský fotbalový stadion Miroslava Valenty (Uherské Hradiště)
    "杜克拉布拉格": (50.1167, 14.5000, "Europe/Prague"),  # FK Dukla Prague - Juliska Stadium (Prague)
    "帕爾杜比斯": (50.0417, 15.7767, "Europe/Prague"),  # FK Pardubice - Pod Vinicí (Pardubice)
    "施連": (49.2167, 17.6667, "Europe/Prague"),  # FC Zlín - Letná Stadion (Zlín)
    #波斯尼亞和黑塞哥維那超級足球聯賽
    "薩拉熱窩": (43.8563, 18.4132, "Europe/Sarajevo"),  # FK Sarajevo - Asim Ferhatović Hase Stadium (Sarajevo)
    "博拉茨班盧卡": (44.7667, 17.1833, "Europe/Sarajevo"),  # FK Borac Banja Luka - Gradski Stadion Banja Luka (Banja Luka)
    "澤列茲尼察": (44.7667, 17.1833, "Europe/Sarajevo"),  # FK Borac Banja Luka - Gradski Stadion (Banja Luka)
    "茲林斯基": (43.3333, 17.8000, "Europe/Sarajevo"),  # HŠK Zrinjski Mostar - Stadion pod Bijelim Brijegom (Mostar)
    "斯拉沃尼亞": (44.7667, 17.1833, "Europe/Sarajevo"),  # FK Slavija Sarajevo - Gradski Stadion (Istočno Sarajevo)
    "維列茲": (43.3333, 17.8000, "Europe/Sarajevo"),  # FK Velež Mostar - Stadion pod Bijelim Brijegom (Mostar, shared)
    "圖茲拉城": (44.5333, 18.6833, "Europe/Sarajevo"),  # FK Tuzla City - Stadion Tušanj (Tuzla)
    "戈斯皮奇": (44.8667, 17.2500, "Europe/Sarajevo"),  # FK Igman Konjic - Gradski stadion Igman (Konjic)
    "波薩維納": (44.9833, 18.1833, "Europe/Sarajevo"),  # HNK Posušje - Stadion Mokri Dolac (Posušje)
    "伊格曼": (43.6500, 17.9667, "Europe/Sarajevo"),  # FK Igman Konjic - Stadion Igman (Konjic)
    "斯拉維亞": (43.8563, 18.4132, "Europe/Sarajevo"),  # FK Slavija Sarajevo - Gradski Stadion (Istočno Sarajevo)
    #委內瑞拉超級足球聯賽
    "塔奇拉": (7.8167, -72.2333, "America/Caracas"),  # Deportivo Táchira - Estadio Polideportivo de Pueblo Nuevo (San Cristóbal)
    "卡拉卡斯": (10.4806, -66.9036, "America/Caracas"),  # Caracas FC - Estadio Olímpico de la UCV (Caracas)
    "卡拉保保": (10.1833, -68.0000, "America/Caracas"),  # Carabobo FC - Polideportivo Misael Delgado (Valencia)
    "米拿羅斯": (8.3333, -62.6667, "America/Caracas"),  # Mineros de Guayana - CTE Cachamay (Ciudad Guayana)
    "阿拉瓜": (10.1833, -67.5833, "America/Caracas"),  # Aragua FC - Estadio Hermanos Ghersi Páez (Maracay)
    "拉瓜爾拉": (10.5000, -66.9500, "America/Caracas"),  # Deportivo La Guaira - Estadio Olímpico de la UCV (Caracas, shared)
    "大都會FC": (10.4806, -66.9036, "America/Caracas"),  # Metropolitanos F.C. - Estadio Olímpico de la UCV (Caracas, shared)
    "梅里達學生隊": (8.6000, -71.1500, "America/Caracas"),  # Estudiantes de Mérida F.C. - Estadio Metropolitano de Mérida (Mérida)
    "FC薩莫拿": (8.0667, -68.7500, "America/Caracas"),  # Zamora FC - Estadio Agustín Tovar (Barinas)
    "拿拉體育會": (10.0667, -69.3333, "America/Caracas"),  # Deportivo Lara - Estadio Metropolitano de Barquisimeto (Barquisimeto)
    "蘇利亞": (10.6667, -71.6167, "America/Caracas"),  # Zulia FC - Estadio José Encarnación "Pachencho" Romero (Maracaibo)
    "卡貝略港大學": (10.1833, -67.9167, "America/Caracas"),  # Academia Puerto Cabello - Estadio Polideportivo Misael Delgado (Puerto Cabello)
    "委內瑞拉體育俱樂部": (10.4806, -66.9036, "America/Caracas"),  # Atlético Venezuela - Estadio Olímpico de la UCV (Caracas, shared)
    "莫納加斯": (9.7500, -63.1833, "America/Caracas"),  # Monagas Sport Club - Estadio Monumental de Maturín (Maturín)
    "波圖加沙": (9.5500, -69.2167, "America/Caracas"),  # Portuguesa FC - Estadio General José Antonio Páez (Acarigua)
    "拉尼洛斯": (9.9167, -67.9333, "America/Caracas"),  # Llaneros Escuela de Fútbol - Estadio Metropolitano de Cabudare (Cabudare)
    "圖積蘭奴斯": (9.3667, -70.4333, "America/Caracas"),  # Trujillanos FC - Estadio José Alberto Pérez (Valera)
    "拿拉FC": (10.4806, -66.9036, "America/Caracas"),  # LALA FC - Estadio Olímpico de la UCV (Caracas, shared)
    "雅拉古恩奴斯": (10.3500, -68.7333, "America/Caracas"),  # Yaracuyanos F.C. - Estadio Independencia (San Felipe)
    "馬拉奇": (10.1833, -67.5833, "America/Caracas"),  # Gran Valencia Maracay F.C. - Estadio Hermanos Ghersi Páez (Maracay)
    #巴拿馬足球聯賽
    "阿拉貝": (8.9833, -79.5167, "America/Panama"),  # Árabe Unido - Estadio Armando Dely Valdés (Colón)
    "卡利多尼亞": (8.9833, -79.5167, "America/Panama"),  # CAI / Club Atlético Independiente - Estadio Agustín Sánchez (La Chorrera)
    "奇里基": (8.4333, -82.4333, "America/Panama"),  # Chiriquí FC - Estadio San Cristóbal (David)
    "奇里基中央": (8.4333, -82.4333, "America/Panama"),  # Atlético Chiriquí - Estadio San Cristóbal (David)
    "科隆": (9.3500, -79.9000, "America/Panama"),  # CD Colón - Estadio Armando Dely Valdés (Colón)
    "達里恩": (8.9833, -79.5167, "America/Panama"),  # CD Universitario - Estadio Universitario (Penonomé)
    "馬里亞托": (7.7000, -81.0833, "America/Panama"),  # Mariato FC - Estadio Omar Torrijos (Santiago de Veraguas, shared)
    "奧林匹克": (8.9833, -79.5167, "America/Panama"),  # Sporting San Miguelito - Estadio Luis Ernesto "Cascarita" Tapia (Panama City)
    "巴拿馬城": (8.9833, -79.5167, "America/Panama"),  # Plaza Amador - Estadio Luis Ernesto "Cascarita" Tapia (Panama City)
    "聖米格利托體育會": (8.9833, -79.5167, "America/Panama"),  # Sporting San Miguelito - Estadio Luis Ernesto "Cascarita" Tapia (Panama City)
    "塔沃加": (8.9833, -79.5167, "America/Panama"),  # Tauro FC - Estadio Luis Ernesto "Cascarita" Tapia (Panama City)
    "烏尼多斯": (8.9833, -79.5167, "America/Panama"),  # Alianza FC - Estadio Luis Ernesto "Cascarita" Tapia (Panama City)
    "維拉古埃拉": (8.9833, -79.5167, "America/Panama"),  # Veraguas United - Estadio Omar Torrijos (Santiago de Veraguas)
    "阿爾卡薩": (8.9833, -79.5167, "America/Panama"),  # Alcajá FC - Various (Panama City area)
    "科科萊": (9.0167, -79.5500, "America/Panama"),  # Coclé - Estadio Omar Torrijos (Santiago de Veraguas, shared)
    #埃及聯賽
    "阿赫利": (30.0694, 31.3122, "Africa/Cairo"),  # Al Ahly SC - Cairo International Stadium (Cairo)
    "扎馬雷克": (30.0694, 31.3122, "Africa/Cairo"),  # Zamalek SC - Cairo International Stadium (Cairo, shared)
    "皮拉米德斯": (30.0694, 31.3122, "Africa/Cairo"),  # Pyramids FC - 30 June Stadium (Cairo)
    "陶瓷克萊奧帕特拉": (30.0694, 31.3122, "Africa/Cairo"),  # Ceramica Cleopatra - Gezirah Youth Center (Cairo)
    "馬斯里": (31.2560, 32.3011, "Africa/Cairo"),  # Al Masry SC - New Suez Stadium (Suez) / Borg El Arab (Alexandria)
    "伊斯梅利": (30.5992, 32.2733, "Africa/Cairo"),  # Ismaily SC - Ismailia Stadium (Ismailia)
    "伊蒂哈德亞歷山大": (31.1972, 29.9153, "Africa/Cairo"),  # Al Ittihad Alexandria - Alexandria Stadium (Alexandria)
    "法爾科": (31.2560, 32.3011, "Africa/Cairo"),  # Pharco FC - Alexandria Stadium (Alexandria)
    "恩皮": (30.0250, 31.3736, "Africa/Cairo"),  # ENPPI SC - Petrosport Stadium (Cairo)
    "莫哈拉紡織": (30.9563, 31.1703, "Africa/Cairo"),  # Ghazl El Mahalla SC - Ghazl El Mahalla Stadium (El Mahalla El Kubra)
    "戈納": (27.0717, 33.8389, "Africa/Cairo"),  # El Gouna FC - Khaled Bichara Stadium (El Gouna)
    "哈拉斯奧德": (31.3811, 29.9744, "Africa/Cairo"),  # Haras El Hodoud SC - Haras El Hodoud Stadium (Alexandria)
    "澤德": (30.0694, 31.3122, "Africa/Cairo"),  # ZED FC - Cairo International Stadium (Cairo)
    "現代未來": (30.0694, 31.3122, "Africa/Cairo"),  # Modern Future FC - Cairo International Stadium (Cairo)
    "國民銀行": (30.0694, 31.3122, "Africa/Cairo"),  # National Bank of Egypt SC - Cairo International Stadium (Cairo)
    "伊蒂哈德曼蘇拉": (31.0400, 31.3800, "Africa/Cairo"),  # Ittihad El Shorta - Police Academy Stadium (Cairo)
    "伊蒂哈德伊斯梅利亞": (30.5992, 32.2733, "Africa/Cairo"),  # Ittihad El Iskandariya - Alexandria Stadium (Alexandria)
    "石油": (30.0694, 31.3122, "Africa/Cairo"),  # Petrojet - Suez Stadium (Suez)
    "斯穆哈": (31.2560, 32.3011, "Africa/Cairo"),  # Smouha SC - Alexandria Stadium (Alexandria)
    "塔拉埃爾賈伊什": (30.0533, 31.3000, "Africa/Cairo"),  # Tala'ea El Gaish - Gehaz El Reyada Stadium (Cairo)
    "瓦迪德格拉": (30.0250, 31.3736, "Africa/Cairo"),  # Wadi Degla SC - Petrosport Stadium (Cairo)
    #摩洛哥
    "奧林匹克薩菲": (32.3000, -9.2333, "Africa/Casablanca"),  # Olympique de Safi - Stade El Massira (Safi)
    "穆勒迪亞": (33.5833, -7.6167, "Africa/Casablanca"),  # Moghreb de Tétouan - Stade Saniat Rmel (Tétouan)
    "肯尼特拉": (34.2610, -6.5802, "Africa/Casablanca"),  # Ittihad de Tanger - Stade Ibn Batouta (Tangier)
    "馬格里布丹達迪斯": (34.0333, -5.0000, "Africa/Casablanca"),  # Maghreb de Fès - Complexe Sportif de Fès (Fès)
    #南非
    "馬梅洛迪日落": (-25.7511, 28.2228, "Africa/Johannesburg"),  # Mamelodi Sundowns - Lucas Masterpieces Moripe Stadium (Atteridgeville, Pretoria)
    "凱澤酋長": (-26.2342, 28.0583, "Africa/Johannesburg"),  # Kaizer Chiefs - FNB Stadium / Soccer City (Nasrec, Johannesburg)
    "奧蘭多海盜": (-26.2342, 28.0583, "Africa/Johannesburg"),  # Orlando Pirates - Orlando Stadium (Soweto, Johannesburg)
    "超級運動聯盟": (-25.8644, 28.1944, "Africa/Johannesburg"),  # SuperSport United - Lucas Masterpieces Moripe Stadium (Atteridgeville, Pretoria, shared)
    "阿瑪祖盧": (-29.8583, 31.0217, "Africa/Johannesburg"),  # AmaZulu FC - Moses Mabhida Stadium (Durban) 或 King Zwelithini Stadium
    "奇帕聯": (-33.0167, 27.9167, "Africa/Johannesburg"),  # Chippa United - Nelson Mandela Bay Stadium (Port Elizabeth) 或 Buffalo City Stadium (East London)
    "金箭": (-29.8583, 31.0217, "Africa/Johannesburg"),  # Golden Arrows - Princess Magogo Stadium (Durban)
    "斯泰倫博斯": (-33.9333, 18.8667, "Africa/Johannesburg"),  # Stellenbosch FC - Danie Craven Stadium (Stellenbosch) 或 Athlone Stadium (Cape Town)
    "理查茲灣": (-28.7833, 32.0667, "Africa/Johannesburg"),  # Richards Bay FC - Richards Bay Stadium (Richards Bay)
    "塞庫庫內聯": (-23.9167, 29.4667, "Africa/Johannesburg"),  # Sekhukhune United - Peter Mokaba Stadium (Polokwane)
    "皇家AM": (-29.8583, 31.0217, "Africa/Johannesburg"),  # Royal AM - Chatsworth Stadium (Durban)
    "開普敦城": (-33.9167, 18.4167, "Africa/Johannesburg"),  # Cape Town City FC - Cape Town Stadium (Cape Town)
    "斯沃普公園": (-26.2342, 28.0583, "Africa/Johannesburg"),  # TS Galaxy - Mbombela Stadium (Mbombela/Nelspruit)
    "馬魯莫加蘭茨": (-24.1833, 29.6333, "Africa/Johannesburg"),  # Marumo Gallants - Old Peter Mokaba Stadium (Polokwane)
    "奧比特學院": (-26.5000, 29.4667, "Africa/Johannesburg"),  # Orbit College - Peter Mokaba Stadium (Polokwane, shared)
    "曼德拉聯": (-33.0167, 27.9167, "Africa/Johannesburg"),  # Durban City FC - Moses Mabhida Stadium (Durban)
    #阿爾及尼亞
    "MC阿爾及爾": (36.7250, 3.1750, "Africa/Algiers"),  # MC Alger - Stade du 5 Juillet 1962 (Algiers)
    "USM阿爾及爾": (36.7250, 3.1750, "Africa/Algiers"),  # USM Alger - Stade Omar Hamadi (Algiers)
    "康斯坦丁": (36.3650, 6.6147, "Africa/Algiers"),  # CS Constantine - Stade Mohamed Hamlaoui (Constantine)
    "塞提夫": (36.1833, 5.4167, "Africa/Algiers"),  # ES Sétif - Stade du 8 Mai 1945 (Sétif)
    "貝賈亞": (36.7500, 5.0667, "Africa/Algiers"),  # JS Kabylie - Stade du 1er Novembre 1954 (Tizi Ouzou)
    "奧蘭": (35.6971, -0.6308, "Africa/Algiers"),  # MC Oran - Stade Ahmed Zabana (Oran)
    "帕拉德": (36.7500, 3.0500, "Africa/Algiers"),  # Paradou AC - Stade Omar Hamadi (Algiers, shared)
    "比斯克拉": (34.8500, 5.7333, "Africa/Algiers"),  # US Biskra - Stade 18 Février (Biskra)
    "馬格拉": (35.8667, 2.7500, "Africa/Algiers"),  # ASO Chlef - Stade Mohamed Boumezrag (Chlef)
    "卡比利亞青年": (36.7167, 4.0500, "Africa/Algiers"),  # JS Kabylie - Stade du 1er Novembre 1954 (Tizi Ouzou)
    "巴爾迪": (36.7525, 3.0428, "Africa/Algiers"),  # CR Belouizdad - Stade du 20 Août 1955 (Algiers)
    "什勒夫": (36.1667, 1.3333, "Africa/Algiers"),  # ASO Chlef - Stade Mohamed Boumezrag (Chlef)
    "卡比利亞青年": (36.7167, 4.0500, "Africa/Algiers"),  # JS Kabylie - Stade du 1er Novembre 1954 (Tizi Ouzou)
    "馬格拉": (35.8667, 2.7500, "Africa/Algiers"),  # ASO Chlef - Stade Mohamed Boumezrag (Chlef)
    "埃爾哈德": (36.7250, 3.1750, "Africa/Algiers"),  # ES Sétif - Stade du 8 Mai 1945 (Sétif)
    "康斯坦丁": (36.3650, 6.6147, "Africa/Algiers"),  # CS Constantine - Stade Mohamed Hamlaoui (Constantine)
    #其他
    "艾侯賽因伊比": (32.6535, 51.6660, "Asia/Tehran"),
    "皇家伊斯柏納": (15.5042, -88.0347, "America/Tegucigalpa"),
    "萬隆": (-6.9147, 107.6098, "Asia/Jakarta"),  # Persib Bandung - Gelora Bandung Lautan Api (Bandung)
    "阿里安沙體育會": (14.0911, -87.2061, "America/Tegucigalpa"),
    "拉巴斯體育會": (-16.5000, -68.1333, "America/La_Paz"),
}













