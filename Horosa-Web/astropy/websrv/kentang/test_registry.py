import unittest

from websrv.kentang.registry import KENTANG_SERVICE_SPECS


class KentangRegistryTest(unittest.TestCase):
    def test_service_specs_are_unique_and_complete(self):
        required = {"key", "engine", "mount", "module", "class_name"}
        keys = [spec["key"] for spec in KENTANG_SERVICE_SPECS]
        engines = [spec["engine"] for spec in KENTANG_SERVICE_SPECS]
        mounts = [spec["mount"] for spec in KENTANG_SERVICE_SPECS]

        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(engines), len(set(engines)))
        self.assertEqual(len(mounts), len(set(mounts)))

        for spec in KENTANG_SERVICE_SPECS:
            self.assertTrue(required.issubset(spec.keys()))
            self.assertTrue(spec["mount"].startswith("/"))
            self.assertTrue(spec["module"].startswith("websrv."))
            self.assertTrue(spec["class_name"].endswith("Srv"))

    def test_current_kentang_modules_are_registered(self):
        by_key = {spec["key"]: spec for spec in KENTANG_SERVICE_SPECS}

        self.assertEqual(by_key["taiyi"]["engine"], "kintaiyi")
        self.assertEqual(by_key["taiyi"]["mount"], "/taiyi")
        self.assertEqual(by_key["jinkou"]["engine"], "kinjinkou")
        self.assertEqual(by_key["jinkou"]["mount"], "/jinkou")
        self.assertEqual(by_key["qimen"]["engine"], "kinqimen")
        self.assertEqual(by_key["qimen"]["mount"], "/qimen")
        self.assertEqual(by_key["wangji"]["engine"], "kinwangji")
        self.assertEqual(by_key["wangji"]["mount"], "/wangji")
        self.assertEqual(by_key["wuzhao"]["engine"], "kinwuzhao")
        self.assertEqual(by_key["wuzhao"]["mount"], "/wuzhao")
        self.assertEqual(by_key["taixuan"]["engine"], "taixuanshifa")
        self.assertEqual(by_key["taixuan"]["mount"], "/taixuan")
        self.assertEqual(by_key["jingjue"]["engine"], "jingjue")
        self.assertEqual(by_key["jingjue"]["mount"], "/jingjue")
        self.assertEqual(by_key["shenyishu"]["engine"], "shenyishu")
        self.assertEqual(by_key["shenyishu"]["mount"], "/shenyishu")
        self.assertEqual(by_key["shaozi"]["engine"], "kinastro-shaozi")
        self.assertEqual(by_key["shaozi"]["mount"], "/shaozi")
        self.assertEqual(by_key["tieban"]["engine"], "kinastro-tieban")
        self.assertEqual(by_key["tieban"]["mount"], "/tieban")
        self.assertEqual(by_key["fendjing"]["engine"], "kinastro-fendjing")
        self.assertEqual(by_key["fendjing"]["mount"], "/fendjing")
        self.assertEqual(by_key["beiji"]["engine"], "kinastro-beiji")
        self.assertEqual(by_key["beiji"]["mount"], "/beiji")
        self.assertEqual(by_key["nanji"]["engine"], "kinastro-nanji")
        self.assertEqual(by_key["nanji"]["mount"], "/nanji")
        self.assertEqual(by_key["chunzi"]["engine"], "kinastro-chunzi")
        self.assertEqual(by_key["chunzi"]["mount"], "/chunzi")
        self.assertEqual(by_key["xianqin"]["engine"], "kinastro-xianqin")
        self.assertEqual(by_key["xianqin"]["mount"], "/xianqin")
        self.assertEqual(by_key["cetian"]["engine"], "kinastro-cetian")
        self.assertEqual(by_key["cetian"]["mount"], "/cetian")
        self.assertEqual(by_key["qizhengkin"]["engine"], "kinastro-qizheng")
        self.assertEqual(by_key["qizhengkin"]["mount"], "/qizhengkin")


if __name__ == "__main__":
    unittest.main()
