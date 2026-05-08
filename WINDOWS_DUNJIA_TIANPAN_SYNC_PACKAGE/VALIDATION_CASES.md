# Validation Cases

## Golden Sample

Input:

```json
{
  "date": "1998-02-20",
  "time": "20:48:00",
  "longitude": "119e19",
  "latitude": "26n04",
  "nongli": {
    "yearJieqi": "戊寅",
    "year": "戊寅",
    "monthGanZi": "甲寅",
    "dayGanZi": "戊戌",
    "time": "壬戌",
    "jieqi": "雨水",
    "jiedelta": "雨水后第1天",
    "birth": "1998-02-20 20:48:00",
    "month": "正月",
    "day": "廿四",
    "leap": false
  },
  "options": {
    "paiPanType": 3,
    "qijuMethod": "chaibu",
    "timeAlg": 1,
    "shiftPalace": 0
  }
}
```

Expected:

```json
{
  "juText": "阳遁九局上元",
  "tianGan": {
    "1": "庚",
    "2": "丙",
    "3": "丁",
    "4": "戊",
    "6": "己",
    "7": "壬",
    "8": "辛",
    "9": "乙"
  },
  "diPan": {
    "1": "壬",
    "2": "戊",
    "3": "庚",
    "4": "辛",
    "5": "癸",
    "6": "丙",
    "7": "乙",
    "8": "己",
    "9": "丁"
  },
  "renPan": {
    "1": "死",
    "2": "惊",
    "3": "开",
    "4": "景",
    "6": "休",
    "7": "杜",
    "8": "伤",
    "9": "生"
  },
  "zhiFu": "天禽",
  "zhiShi": "死门"
}
```

## Same Day Different Hours

All are for `1998-02-20`, minute `48`, `paiju = 阳遁九局上元`.

```json
[
  { "time": "00:48", "hourGanzhi": "壬子", "tianGan": { "1": "壬", "2": "戊", "3": "庚", "4": "辛", "6": "丙", "7": "乙", "8": "己", "9": "丁" } },
  { "time": "02:48", "hourGanzhi": "癸丑", "tianGan": { "1": "乙", "2": "辛", "3": "壬", "4": "己", "6": "戊", "7": "丁", "8": "丙", "9": "庚" } },
  { "time": "04:48", "hourGanzhi": "甲寅", "tianGan": { "1": "壬", "2": "戊", "3": "庚", "4": "辛", "6": "丙", "7": "乙", "8": "己", "9": "丁" } },
  { "time": "06:48", "hourGanzhi": "乙卯", "tianGan": { "1": "丁", "2": "己", "3": "乙", "4": "丙", "6": "辛", "7": "庚", "8": "戊", "9": "壬" } },
  { "time": "08:48", "hourGanzhi": "丙辰", "tianGan": { "1": "辛", "2": "壬", "3": "戊", "4": "乙", "6": "庚", "7": "己", "8": "丁", "9": "丙" } },
  { "time": "10:48", "hourGanzhi": "丁巳", "tianGan": { "1": "乙", "2": "辛", "3": "壬", "4": "己", "6": "戊", "7": "丁", "8": "丙", "9": "庚" } },
  { "time": "12:48", "hourGanzhi": "戊午", "tianGan": { "1": "戊", "2": "庚", "3": "丙", "4": "壬", "6": "丁", "7": "辛", "8": "乙", "9": "己" } },
  { "time": "14:48", "hourGanzhi": "己未", "tianGan": { "1": "己", "2": "乙", "3": "辛", "4": "丁", "6": "壬", "7": "丙", "8": "庚", "9": "戊" } },
  { "time": "16:48", "hourGanzhi": "庚申", "tianGan": { "1": "壬", "2": "戊", "3": "庚", "4": "辛", "6": "丙", "7": "乙", "8": "己", "9": "丁" } },
  { "time": "18:48", "hourGanzhi": "辛酉", "tianGan": { "1": "丙", "2": "丁", "3": "己", "4": "庚", "6": "乙", "7": "戊", "8": "壬", "9": "辛" } },
  { "time": "20:48", "hourGanzhi": "壬戌", "tianGan": { "1": "庚", "2": "丙", "3": "丁", "4": "戊", "6": "己", "7": "壬", "8": "辛", "9": "乙" } },
  { "time": "22:48", "hourGanzhi": "癸亥", "tianGan": { "1": "壬", "2": "戊", "3": "庚", "4": "辛", "6": "丙", "7": "乙", "8": "己", "9": "丁" } }
]
```

## Batch Plan

Before Windows release, test at least these 48 cases:

```text
1998-02-20: 00,02,04,06,08,10,12,14,16,18,20,22
1999-06-18: 00,02,04,06,08,10,12,14,16,18,20,22
2001-11-07: 00,02,04,06,08,10,12,14,16,18,20,22
2004-02-29: 00,02,04,06,08,10,12,14,16,18,20,22
```

The macOS/web implementation passed `48/48` against the legacy Horosa Qimen output.

## Manual Smoke

1. Open Qimen/Dunjia.
2. Plot `1998-02-20 20:48`.
3. Confirm Tianpan `1庚 2丙 3丁 4戊 6己 7壬 8辛 9乙`.
4. Change only the time to `18:48`.
5. Confirm Tianpan changes to `1丙 2丁 3己 4庚 6乙 7戊 8壬 9辛`.
6. Open Sanshi United and confirm its Qimen section matches standalone Qimen.
7. Run AI export / AI analysis snapshot and confirm the serialized Qimen/Sanshi text uses the same Tianpan stems.
