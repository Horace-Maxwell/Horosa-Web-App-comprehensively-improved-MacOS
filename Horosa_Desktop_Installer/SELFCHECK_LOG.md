# SELFCHECK_LOG — 发布门自检留档(机器追加,倒查用)

每次「全路由真实冒烟门 / hostile 敌意环境门」运行由脚本自动追加一行;
preflight[79] 校验最近一次 runtime-smoke 为 PASS 且 sha 与当前 dist 归档一致。
不要手工编辑数据行。

| 时间 | git | 结果 | 门 | 产物 sha(前16) |
|---|---|---|---|---|
