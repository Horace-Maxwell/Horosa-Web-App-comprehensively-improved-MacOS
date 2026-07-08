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
