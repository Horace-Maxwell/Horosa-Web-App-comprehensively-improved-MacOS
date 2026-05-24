# Kentang Integrations

Horosa keeps kentang2017 libraries isolated behind thin adapters. The goal is
to make each external engine easy to identify, replace, upgrade, or remove.

## Current Modules

| Horosa module | Vendor engine | Vendor location | Backend mount | Frontend module |
| --- | --- | --- | --- | --- |
| 太乙 | kintaiyi | `Horosa-Web/vendor/kintaiyi` | `/taiyi` | `src/components/taiyi` |
| 金口诀 | kinjinkou | `Horosa-Web/vendor/kinjinkou` | `/jinkou` | `src/components/jinkou` |
| 奇门遁甲 | kinqimen | `Horosa-Web/vendor/kinqimen` | `/qimen` | `src/components/dunjia` |
| 皇极经世 | kinwangji | `Horosa-Web/vendor/kinwangji` | `/wangji` | `src/components/huangji` |
| 五兆 | kinwuzhao | `Horosa-Web/vendor/kinwuzhao` | `/wuzhao` | `src/components/wuzhao` |
| 太玄筮法 | taixuanshifa | `Horosa-Web/vendor/taixuanshifa` | `/taixuan` | `src/components/taixuan` |
| 荆诀 | jingjue | `Horosa-Web/vendor/jingjue` | `/jingjue` | `src/components/jingjue` |
| 神易数 | shenyishu | `Horosa-Web/vendor/shenyishu` | `/shenyishu` | `src/components/shenyishu` |
| 邵子神数 | kinastro | `Horosa-Web/vendor/kinastro` | `/shaozi` | `src/components/shusuan` |
| 铁板神数 | kinastro | `Horosa-Web/vendor/kinastro` | `/tieban` | `src/components/shusuan` |
| 鬼谷分定经 | kinastro | `Horosa-Web/vendor/kinastro` | `/fendjing` | `src/components/shusuan` |
| 北极神数 | kinastro | `Horosa-Web/vendor/kinastro` | `/beiji` | `src/components/shusuan` |
| 南极神数 | kinastro | `Horosa-Web/vendor/kinastro` | `/nanji` | `src/components/shusuan` |
| 蠢子数 | kinastro | `Horosa-Web/vendor/kinastro` | `/chunzi` | `src/components/shusuan` |
| 万化仙禽 | kinastro | `Horosa-Web/vendor/kinastro` | `/xianqin` | `src/components/yanqin` |
| 策天飞星 | kinastro | `Horosa-Web/vendor/kinastro` | `/cetian` | `src/components/mingother` |
| 七政四余 | kinastro | `Horosa-Web/vendor/kinastro` | `/qizhengkin` | `src/components/guolao` |

## Boundaries

Vendor code lives under `Horosa-Web/vendor/<engine>` and should remain as close
to upstream as possible. Avoid changing vendor files unless the change is a
documented compatibility patch.

Backend adapter code lives under `Horosa-Web/astropy/websrv/web<module>srv.py`.
Adapters may import vendor libraries, normalize raw outputs into Horosa data
contracts, sanitize display-sensitive fields, and expose CherryPy endpoints.
The root server imports only `websrv.kentang.registry.mount_kentang_services`.

Frontend service discovery lives under
`Horosa-Web/astrostudyui/src/integrations/kentang/serviceRoot.js`. UI modules
should call `buildKentangEndpoint(moduleKey, action)` instead of manually
reading URL params or guessing sibling module servers.

Frontend UI remains in the regular Horosa component folders. Kentang output is
treated as calculation data only; chart layout, labels, sidebars, tabs, and
display choices stay in Horosa components.

## Service URL Rules

Module-specific query params have highest priority:

- `taiyiSrv` or `kintaiyiSrv`
- `jinkouSrv` or `kinjinkouSrv`
- `qimenSrv` or `kinqimenSrv`
- `wangjiSrv`, `huangjiSrv`, or `kinwangjiSrv`
- `wuzhaoSrv` or `kinwuzhaoSrv`
- `taixuanSrv` or `taixuanshifaSrv`
- `jingjueSrv`
- `shenyishuSrv`
- `shaoziSrv`, `shusuanSrv`, or `kinastroSrv`
- `tiebanSrv`, `shusuanSrv`, or `kinastroSrv`
- `fendjingSrv`, `guiguSrv`, `shusuanSrv`, or `kinastroSrv`
- `beijiSrv`, `shusuanSrv`, or `kinastroSrv`
- `nanjiSrv`, `shusuanSrv`, or `kinastroSrv`
- `chunziSrv`, `shusuanSrv`, or `kinastroSrv`
- `xianqinSrv`, `yanqinSrv`, or `kinastroSrv`
- `cetianSrv`, `mingOtherSrv`, or `kinastroSrv`
- `qizhengKinSrv`, `qizhengSrv`, or `kinastroSrv`

Shared fallback params are `kentangSrv` and `kinSrv`. These are useful when one
local CherryPy process serves all kentang routes.

When no query param is provided and `ServerRoot` points at local port `9999`,
the frontend derives module-specific local ports. Shared 三式 services default
to `8898`; newer isolated services use their own ports, including `8895`
for 太玄筮法, `8894` for 荆诀, `8893` for 神易数, and `8892` for kinastro
命部技法与七政四余.

## Adding Another Kentang Engine

1. Put the upstream repo in `Horosa-Web/vendor/<engine>`.
2. Add a backend adapter in `Horosa-Web/astropy/websrv/web<module>srv.py`.
3. Register it in `Horosa-Web/astropy/websrv/kentang/registry.py`.
4. Add frontend service config in
   `Horosa-Web/astrostudyui/src/integrations/kentang/serviceRoot.js`.
5. Keep UI-specific rendering inside the Horosa component folder for that page.
6. Update `THIRD_PARTY_NOTICES.md` with the upstream license and attribution.

## Stability Checks

Run these after adding or changing a kentang integration:

```bash
cd Horosa-Web/astrostudyui
npx umi-test src/integrations/kentang/__tests__/serviceRoot.test.js --runInBand
npm run build:file -- --file src/pages/index.js
```

```bash
cd Horosa-Web/astropy
PYTHONPATH=. python3 -m unittest websrv.kentang.test_registry
python3 -m py_compile websrv/webchartsrv.py websrv/kentang/registry.py websrv/kentang/kinastro_common.py websrv/webtaiyisrv.py websrv/webjinkousrv.py websrv/webqimensrv.py websrv/webwuzhaosrv.py websrv/webtaixuansrv.py websrv/webjingjuesrv.py websrv/webshenyishusrv.py websrv/webshaozisrv.py websrv/webtiebansrv.py websrv/webfendjingsrv.py websrv/webbeijisrv.py websrv/webnanjisrv.py websrv/webchunzisrv.py websrv/webxianqinsrv.py websrv/webcetiansrv.py websrv/webqizhengkinsrv.py
```

The service-root test protects frontend URL isolation. The registry test
protects backend mount uniqueness and makes missing registration obvious.
