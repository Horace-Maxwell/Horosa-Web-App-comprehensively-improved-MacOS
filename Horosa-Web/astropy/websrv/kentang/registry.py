"""Registry for kentang2017-backed calculation services.

This file is the only place the root CherryPy app should know about
Kentang-backed service mounts. Each concrete adapter remains in its own
one web service adapter module so the raw vendor library, Horosa normalization, and
HTTP route stay identifiable.
"""


KENTANG_SERVICE_SPECS = [
    {
        "key": "taiyi",
        "engine": "kintaiyi",
        "mount": "/taiyi",
        "module": "websrv.webtaiyisrv",
        "class_name": "TaiYiSrv",
    },
    {
        "key": "jinkou",
        "engine": "kinjinkou",
        "mount": "/jinkou",
        "module": "websrv.webjinkousrv",
        "class_name": "JinKouSrv",
    },
    {
        "key": "qimen",
        "engine": "kinqimen",
        "mount": "/qimen",
        "module": "websrv.webqimensrv",
        "class_name": "QiMenSrv",
    },
    {
        "key": "wangji",
        "engine": "kinwangji",
        "mount": "/wangji",
        "module": "websrv.webwangjisrv",
        "class_name": "WangJiSrv",
    },
    {
        "key": "wuzhao",
        "engine": "kinwuzhao",
        "mount": "/wuzhao",
        "module": "websrv.webwuzhaosrv",
        "class_name": "WuZhaoSrv",
    },
    {
        "key": "taixuan",
        "engine": "taixuanshifa",
        "mount": "/taixuan",
        "module": "websrv.webtaixuansrv",
        "class_name": "TaiXuanSrv",
    },
    {
        "key": "jingjue",
        "engine": "jingjue",
        "mount": "/jingjue",
        "module": "websrv.webjingjuesrv",
        "class_name": "JingJueSrv",
    },
    {
        "key": "shenyishu",
        "engine": "shenyishu",
        "mount": "/shenyishu",
        "module": "websrv.webshenyishusrv",
        "class_name": "ShenYiShuSrv",
    },
    {
        "key": "shaozi",
        "engine": "kinastro-shaozi",
        "mount": "/shaozi",
        "module": "websrv.webshaozisrv",
        "class_name": "ShaoZiSrv",
    },
    {
        "key": "tieban",
        "engine": "kinastro-tieban",
        "mount": "/tieban",
        "module": "websrv.webtiebansrv",
        "class_name": "TieBanSrv",
    },
    {
        "key": "fendjing",
        "engine": "kinastro-fendjing",
        "mount": "/fendjing",
        "module": "websrv.webfendjingsrv",
        "class_name": "FenDingJingSrv",
    },
    {
        "key": "beiji",
        "engine": "kinastro-beiji",
        "mount": "/beiji",
        "module": "websrv.webbeijisrv",
        "class_name": "BeiJiSrv",
    },
    {
        "key": "nanji",
        "engine": "kinastro-nanji",
        "mount": "/nanji",
        "module": "websrv.webnanjisrv",
        "class_name": "NanJiSrv",
    },
    {
        "key": "chunzi",
        "engine": "kinastro-chunzi",
        "mount": "/chunzi",
        "module": "websrv.webchunzisrv",
        "class_name": "ChunZiSrv",
    },
    {
        "key": "xianqin",
        "engine": "kinastro-xianqin",
        "mount": "/xianqin",
        "module": "websrv.webxianqinsrv",
        "class_name": "XianQinSrv",
    },
    {
        "key": "cetian",
        "engine": "kinastro-cetian",
        "mount": "/cetian",
        "module": "websrv.webcetiansrv",
        "class_name": "CeTianSrv",
    },
    {
        "key": "qizhengkin",
        "engine": "kinastro-qizheng",
        "mount": "/qizhengkin",
        "module": "websrv.webqizhengkinsrv",
        "class_name": "QiZhengKinSrv",
    },
]


def _load_service(spec):
    module = __import__(spec["module"], fromlist=[spec["class_name"]])
    service_cls = getattr(module, spec["class_name"])
    return service_cls()


def mount_kentang_services(cherrypy):
    for spec in KENTANG_SERVICE_SPECS:
        cherrypy.tree.mount(_load_service(spec), spec["mount"])
