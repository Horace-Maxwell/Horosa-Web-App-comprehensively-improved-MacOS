// 策天页 · 按需加载的子面板(神数正传:引擎与秘数表随组件走独立 chunk,不点这条 rail 即零成本)
// 从 KinAstroMain.js 按职责拆出(门面保留原导入路径与对外导出;读源码的检查读「子模块 + 门面」全集,见 scripts/source-sets.json)。
import React from 'react';

// 神数正传:组件级 lazy —— 引擎与秘数表(~250KB)随组件走独立 chunk,不点这条 rail 即零成本。
// 条文库(465KB+598KB)另在引擎内动态 import,条文号先出、正文到达后填(见 zhengchuan*Local)。
export const ZhengChuanMain = React.lazy(() => import(/* webpackChunkName: "zhengchuan-main" */ '../../shusuan/ZhengChuanMain'));
