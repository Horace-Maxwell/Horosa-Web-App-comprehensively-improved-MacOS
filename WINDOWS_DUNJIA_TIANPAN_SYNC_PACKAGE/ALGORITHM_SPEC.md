# Algorithm Spec: Qimen Tianpan Heavenly Stems

## Scope

Only fix the Qimen/Dunjia Tianpan heavenly-stem layer.

Do not change:

- Earth pan.
- Doors.
- Stars.
- Gods, except existing alias normalization can stay as-is.
- Qimen ju selection.
- Calendar/Ganzhi calculation.
- Windows installer signing policy.

## Constants

Use existing project equivalents when available.

```js
const CNUMBER = '一二三四五六七八九'.split('');
const EIGHT_GUA = '坎坤震巽中乾兑艮离'.split('');
const CLOCKWISE_EIGHTGUA = '坎艮震巽离坤兑乾'.split('');

const JJ = {
  甲子: '戊',
  甲戌: '己',
  甲申: '庚',
  甲午: '辛',
  甲辰: '壬',
  甲寅: '癸',
};
```

The palace numbering must remain Horosa's current layout:

```text
1 巽 | 2 离 | 3 坤
4 震 | 5 中 | 6 兑
7 艮 | 8 坎 | 9 乾
```

## Earth Pan Reference

Keep current Earth pan semantics:

```js
function panEarth(qmju){
  const meta = parseQmju(qmju);
  const palaces = newList(CNUMBER, meta.kook).map((x)=>zipToMap(CNUMBER, EIGHT_GUA)[x]);
  const vals = meta.yy === '阳'
    ? '戊己庚辛壬癸丁丙乙'.split('')
    : '戊乙丙丁癸壬辛庚己'.split('');
  return zipToMap(palaces, vals);
}
```

For `阳遁九局`, Earth pan should be:

```json
{ "1": "壬", "2": "戊", "3": "庚", "4": "辛", "5": "癸", "6": "丙", "7": "乙", "8": "己", "9": "丁" }
```

## Correct Tianpan Rule

The Tianpan should not start from `值符星宫`.

Correct process:

1. Parse `qmju` to get Yang/Yin.
2. Build `earth = panEarth(qmju)`.
3. Invert Earth pan so stem maps to palace.
4. Get hour Xun head with `getXunHead(ganzhi.time)`.
5. Convert Xun head to hidden Liuyi with `JJ`.
6. `sourceGong = earthR[hiddenLiuyiStem]`.
7. `targetGong = earthR[currentHourGan]`.
8. If either palace is `中`, use `坤` for flying.
9. Yang uses `坎艮震巽离坤兑乾`; Yin uses reverse.
10. Rotate the Earth-pan stem sequence from `sourceGong`.
11. Write it onto palaces rotated from `targetGong`.
12. Preserve center stem separately.

## Reference Implementation

```js
function panSky(ganzhi, qmju){
  const meta = parseQmju(qmju);
  const rotate = meta.yy === '阳' ? CLOCKWISE_EIGHTGUA : [...CLOCKWISE_EIGHTGUA].reverse();
  const earth = panEarth(qmju);
  const earthR = invertMap(earth);
  const fuHead = JJ[getXunHead(ganzhi.time)] || '戊';
  const timeGan = getGanzhiGan(ganzhi.time);
  const normalizeTianpanGong = (gong)=>gong === '中' ? '坤' : gong;
  const sourceGong = normalizeTianpanGong(earthR[fuHead]);
  const targetGong = normalizeTianpanGong(earthR[timeGan]);
  const safeSourceGong = rotate.indexOf(sourceGong) >= 0 ? sourceGong : rotate[0];
  const safeTargetGong = rotate.indexOf(targetGong) >= 0 ? targetGong : safeSourceGong;
  const ganReorder = newList(rotate, safeSourceGong).map((g)=>earth[g]);
  const gongReorder = newList(rotate, safeTargetGong);
  const out = zipToMap(gongReorder, ganReorder);
  out.中 = earth.中;
  return out;
}
```

If Windows uses another language, implement identical semantics.

## Important Alias Note

Legacy response may show `勾/雀`, while current UI may normalize to `虎/玄`. Do not treat that as a Tianpan failure. This fix is specifically about Tianpan heavenly stems.

## Mistakes To Avoid

- Do not anchor Tianpan on Zhifu star palace.
- Do not hardcode the sample.
- Do not change Earth pan to make Tianpan pass.
- Do not alter Sanshi's independent logic if it already consumes shared Qimen output; wire it to the shared fixed result instead.
- Do not add Apple signing to Windows.
