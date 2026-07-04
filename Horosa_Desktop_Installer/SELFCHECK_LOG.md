# SELFCHECK_LOG — 发布门自检留档(机器追加,倒查用)

每次「全路由真实冒烟门 / hostile 敌意环境门」运行由脚本自动追加一行;
preflight 校验最近一次 runtime-smoke 为 PASS 且 sha 与当前 dist 归档一致。

| 时间 | 门 | 结果 | 归档 sha256(前12) | 明细 |
|---|---|---|---|---|
| 2026-07-04 10:34 | a165b2f | PASS | runtime-smoke | cb149c8fe30e274c… |
