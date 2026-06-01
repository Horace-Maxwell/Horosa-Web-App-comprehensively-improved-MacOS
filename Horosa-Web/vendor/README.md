# Vendor Libraries

This directory contains third-party source snapshots used by Horosa adapters.

Current kentang2017 engines:

- `kintaiyi` for 太乙
- `kinjinkou` for 金口诀
- `kinqimen` for 奇门遁甲
- `kinwangji` for 皇极经世
- `kinwuzhao` for 五兆
- `taixuanshifa` for 太玄筮法
- `jingjue` for 荆诀
- `shenyishu` for 神易数
- `kinastro` for 邵子神数、万化仙禽、策天飞星

Keep vendor code isolated. Horosa-specific behavior belongs in:

- Backend adapters: `Horosa-Web/astropy/websrv/web<module>srv.py`
- Backend registry: `Horosa-Web/astropy/websrv/kentang/registry.py`
- Frontend service routing: `Horosa-Web/astrostudyui/src/integrations/kentang/serviceRoot.js`
- Frontend UI: `Horosa-Web/astrostudyui/src/components/<module>/`

When adding or updating a vendor library, also update
`THIRD_PARTY_NOTICES.md`.
