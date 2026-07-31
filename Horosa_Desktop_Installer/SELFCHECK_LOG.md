# SELFCHECK_LOG — 发布门自检留档(机器追加,倒查用)

每次「全路由真实冒烟门 / hostile 敌意环境门」运行由脚本自动追加一行;
preflight[79] 校验最近一次 runtime-smoke 为 PASS 且 sha 与当前 dist 归档一致。
不要手工编辑数据行。

| 时间 | git | 结果 | 门 | 产物 sha(前16) |
|---|---|---|---|---|
| 2026-07-05 03:08 | b60cd75 | PASS | runtime-smoke | da248ad2518b8c40… |
| 2026-07-05 14:09 | e451cef | FAIL | runtime-smoke | 373d354e8412c64c… |
| 2026-07-05 14:33 | e451cef | FAIL | runtime-smoke | 1326b13bdd61818e… |
| 2026-07-05 15:29 | e451cef | PASS | runtime-smoke | 7765ba251eb99446… |
| 2026-07-07 17:14 | 21d489e | FAIL | runtime-smoke | d66f3bda6a4df1af… |
| 2026-07-07 17:50 | 21d489e | PASS | runtime-smoke | 82de01c3b00bfa30… |
| 2026-07-07 22:35 | 21d489e | PASS | runtime-smoke | 15e95252beb329c9… |
| 2026-07-12 06:41 | c49b873 | PASS | runtime-smoke | fc33a7e54ff80f9d… |
| 2026-07-12 07:31 | 995d9ec | PASS | runtime-smoke | 33ad59cf77a857a4… |
| 2026-07-12 11:42 | 844511c | PASS | runtime-smoke | 9f5668b54d0ec4da… |
| 2026-07-12 14:33 | 3442fe9 | PASS | runtime-smoke | 031e6383da1a86e6… |
| 2026-07-13 12:15 | 50e8cc1 | PASS | runtime-smoke | 18372ee6813a66ca… |
| 2026-07-14 00:12 | b5362c7 | PASS | runtime-smoke | 8c0ba62d3ca0ba79… |
| 2026-07-14 01:27 | a56722d | PASS | runtime-smoke | 5ec3c19cabfe741e… |
| 2026-07-14 01:52 | 84febc2 | PASS | runtime-smoke | 6214f1fba19b8fe6… |
| 2026-07-14 02:48 | a829e36 | PASS | runtime-smoke | f0a968c7fe0e877b… |
| 2026-07-14 03:43 | 3a685f0 | PASS | runtime-smoke | 00f1501d12ffc048… |
| 2026-07-14 07:07 | bbc8de3 | PASS | runtime-smoke | e12df06370440465… |
| 2026-07-14 11:48 | 7669fe7 | PASS | runtime-smoke | 839d8ce2b023e6c8… |
| 2026-07-14 13:46 | ae456a8 | PASS | runtime-smoke | d802bb6ecf671871… |
| 2026-07-20 10:03 | 2a4516d | FAIL | runtime-smoke | da016bfc69d5875f… |
| 2026-07-20 13:08 | c110312 | PASS | runtime-smoke | 7c5ef0b9cd1f013a… |
| 2026-07-20 14:27 | 0a74983 | PASS | runtime-smoke | a436633d6ee1612f… |
| 2026-07-20 15:15 | f799ace | PASS | runtime-smoke | efb630e5598c5eb7… |
| 2026-07-21 19:45 | f52f75b | FAIL | runtime-smoke | 23114a546f806c07… |
| 2026-07-21 19:47 | f52f75b | PASS | runtime-smoke | 23114a546f806c07… |
| 2026-07-21 20:34 | f52f75b | PASS | runtime-smoke | 5082f263f699f88a… |
| 2026-07-21 21:24 | ba07628 | PASS | runtime-smoke | 658c179f060a50a9… |
| 2026-07-30 20:47 | faaa2c7 | PASS | runtime-smoke | dc4e20484cc9ce86… |
| 2026-07-30 22:41 | ea77850 | PASS | runtime-smoke | abac271f164bec32… |
| 2026-07-30 23:24 | 8256d56 | PASS | runtime-smoke | a1d61fb6ed87e593… |
