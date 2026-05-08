# Complete Prompt For Windows-Side Codex

Copy everything inside the block below into the Windows-side Codex session.

```text
你现在要把 macOS/web 侧已经修复并验证通过的 Horosa/星阙 v1.3.4 遁甲天盘奇仪 bug 完整同步到 Windows 版本。

硬性边界：
- 这是 Windows 端任务，不要执行 Apple 签名。
- 不要执行 Apple notarization。
- 不要使用 Developer ID、notarytool、stapler、pkg、macOS .app、公证票据或 Gatekeeper 检查。
- 不要把 macOS 发布脚本、pkg 资产或 Apple 证书流程带进 Windows。
- Windows 只使用 Windows 仓库现有的安装器、打包、测试、GitHub release 流程。
- 不要破坏其他已经稳定的术数功能。

背景：
当前 bug 是遁甲/奇门盘中的天盘天干不随时间正确变化。macOS/web 侧已确认并修复根因：旧实现错误地把值符星宫当作天盘起点；正确逻辑是按时辰旬首六仪与当前时干在地盘中的位置进行飞布。

你需要先在 Windows 仓库中定位这些等价入口：
- 遁甲核心计算文件，等价于 macOS/web 的 `DunJiaCalc.js`
- 遁甲单页 UI/状态入口，等价于 `DunJiaMain.js`
- 三式合一入口，等价于 `SanShiUnitedMain.js`
- AI 导出 / AI 分析 snapshot 中序列化遁甲或三式合一结果的位置
- Windows 版本号、README、release notes、打包配置

必须同步影响：
1. 遁甲/奇门单页。
2. 三式合一盘里的遁甲部分。
3. AI 导出 / AI 分析中涉及遁甲或三式合一的输出。
4. Windows 测试。
5. 如果要发布 Windows 新版，更新 Windows 版本号、README、release notes、GitHub main 和 release，但不要签名。

算法要求：
只修天盘奇仪。保留现有地盘、门、星、神、起局、历法、干支计算逻辑。

关键常量：
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

九宫编号必须保持：
1 巽 | 2 离 | 3 坤
4 震 | 5 中 | 6 兑
7 艮 | 8 坎 | 9 乾

核心逻辑：
function panSky(ganzhi, qmju){
  const meta = parseQmju(qmju);
  const rotate = meta.yy === '阳'
    ? CLOCKWISE_EIGHTGUA
    : [...CLOCKWISE_EIGHTGUA].reverse();
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

如果 Windows 不是 JS，请实现完全等价语义：
- parseQmju 得到阴/阳和局数。
- panEarth 得到卦宫 -> 地盘天干。
- invertMap 得到天干 -> 卦宫。
- getXunHead(ganzhi.time) 得到时干支旬首。
- JJ[旬首] 得到旬首六仪。
- sourceGong = 旬首六仪在地盘中的宫。
- targetGong = 当前时干在地盘中的宫。
- 中宫参与飞布时按坤宫处理。
- 阳遁使用 `坎艮震巽离坤兑乾`；阴遁使用反向顺序。
- 从 sourceGong 旋转地盘天干序列，写入从 targetGong 旋转的宫位序列。
- 最后保留中心宫地盘干。

不要这样做：
- 不要使用值符星宫作为天盘起点。
- 不要硬编码样本。
- 不要修改地盘、门、星、神来凑结果。
- 不要让三式合一保留自己的旧缓存或旧算法；它必须使用修复后的共享遁甲结果。
- 不要引入 Apple 签名/公证。

黄金样本：
date = 1998-02-20
time = 20:48:00
longitude = 119e19
latitude = 26n04
nongli:
  yearJieqi = 戊寅
  year = 戊寅
  monthGanZi = 甲寅
  dayGanZi = 戊戌
  time = 壬戌
  jieqi = 雨水
  jiedelta = 雨水后第1天
  birth = 1998-02-20 20:48:00
  month = 正月
  day = 廿四
  leap = false
options:
  paiPanType = 3
  qijuMethod = chaibu
  timeAlg = 1
  shiftPalace = 0

期望：
juText = 阳遁九局上元
tianGan:
  1: 庚
  2: 丙
  3: 丁
  4: 戊
  6: 己
  7: 壬
  8: 辛
  9: 乙
diPan:
  1: 壬
  2: 戊
  3: 庚
  4: 辛
  5: 癸
  6: 丙
  7: 乙
  8: 己
  9: 丁
renPan:
  1: 死
  2: 惊
  3: 开
  4: 景
  6: 休
  7: 杜
  8: 伤
  9: 生
zhiFu = 天禽
zhiShi = 死门

同日不同时辰必须变化：
1998-02-20 18:48 期望天盘：
  1: 丙
  2: 丁
  3: 己
  4: 庚
  6: 乙
  7: 戊
  8: 壬
  9: 辛

测试要求：
1. 给遁甲核心新增单元测试，至少覆盖 1998-02-20 20:48。
2. 给三式合一新增回归测试，确认它使用共享遁甲结果。
3. 检查 AI 导出 / AI 分析 snapshot 是否从同一个修复后的 pan 取值；如有单独构造天盘字段，同步修复。
4. 自动或手动跑至少 48 个样本：1998-02-20、1999-06-18、2001-11-07、2004-02-29，每天取 00/02/04/06/08/10/12/14/16/18/20/22。
5. 如果神盘出现 `勾/雀` 与 `虎/玄` 差异，不要当作本次失败。本次只锁定天盘天干。

Windows 发布要求：
- 测试通过后再构建 Windows 安装包。
- 如果发布新版，按 Windows 仓库版本策略更新版本号、README、release notes。
- release 文案写“修复遁甲/三式合一中天盘奇仪随时辰飞布的问题”。
- 不要写 Apple 签名、公证、Developer ID、notarytool、stapler。
- GitHub release 只上传 Windows 应有资产，不上传 macOS pkg/app zip。

完成后请输出：
- 修改文件列表。
- 核心算法说明。
- 遁甲单页、三式合一、AI 导出是否都已同步。
- 测试结果。
- Windows 安装包构建结果。
- GitHub main/release 更新结果。
- 明确说明没有执行 Apple 签名/公证。
```
