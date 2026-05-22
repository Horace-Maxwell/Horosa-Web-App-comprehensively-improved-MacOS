#!/usr/bin/env python3
"""Static integration checks for Horosa major modules and AI export wiring."""

from __future__ import annotations

import json
import re
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_contains(path: Path, needle: str) -> None:
    text = _read(path)
    if needle not in text:
        raise AssertionError(f"{path} missing expected text: {needle}")


def _assert_regex(path: Path, pattern: str) -> None:
    text = _read(path)
    if re.search(pattern, text, re.S) is None:
        raise AssertionError(f"{path} missing expected pattern: {pattern}")


def _assert_tab(path: Path, label: str, key: str) -> None:
    # Top-level tabs may use rich labels through mainTab('...'), while legacy
    # sub-tabs still use plain tab="...". Keep both shapes covered.
    _assert_regex(
        path,
        rf'<TabPane\b(?=[^>]*\bkey=["\']{re.escape(key)}["\'])(?=[^>]*(?:'
        rf'tab=["\']{re.escape(label)}["\']|tab=\{{mainTab\(["\']{re.escape(label)}["\']'
        rf'))',
    )


def main() -> None:
    root = _repo_root()

    index_js = root / "Horosa-Web" / "astrostudyui" / "src" / "pages" / "index.js"
    page_header = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "homepage" / "PageHeader.js"
    ai_export = root / "Horosa-Web" / "astrostudyui" / "src" / "utils" / "aiExport.js"
    astro_snapshot = root / "Horosa-Web" / "astrostudyui" / "src" / "utils" / "astroAiSnapshot.js"
    module_snapshot = root / "Horosa-Web" / "astrostudyui" / "src" / "utils" / "moduleAiSnapshot.js"
    precise_bridge = root / "Horosa-Web" / "astrostudyui" / "src" / "utils" / "preciseCalcBridge.js"
    astro_model = root / "Horosa-Web" / "astrostudyui" / "src" / "models" / "astro.js"
    ai_analysis_main = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "aianalysis" / "AIAnalysisMain.js"
    verify_sh = root / "Horosa-Web" / "verify_horosa_local.sh"

    cntrad_main = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "cntradition" / "CnTraditionMain.js"
    cnyibu_main = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "cnyibu" / "CnYiBuMain.js"
    direct_main = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "direction" / "AstroDirectMain.js"
    pd_table = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "AstroPrimaryDirection.js"
    hellen_main = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "hellenastro" / "HellenAstroMain.js"
    chart13 = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "hellenastro" / "AstroChart13.js"
    astro_chart_main = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "AstroChartMain.js"
    astro_chart_main3d = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro3d" / "AstroChartMain3D.js"
    astro_chart3d = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro3d" / "AstroChart3D.js"
    astro3d_core = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro3d" / "Astro3D.js"
    loc_main = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "loc" / "LocAstroMain.js"
    acg = root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "acg" / "AstroAcg.js"

    snapshot_expectations = {
        "bazi": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "cntradition" / "BaZi.js",
        "ziwei": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "ziwei" / "ZiWeiMain.js",
        "suzhan": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "suzhan" / "SuZhanMain.js",
        "guazhan": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "guazhan" / "GuaZhanMain.js",
        "liureng": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "lrzhan" / "LiuRengMain.js",
        "jinkou": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "jinkou" / "JinKouMain.js",
        "qimen": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "dunjia" / "DunJiaMain.js",
        "taiyi": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "taiyi" / "TaiYiMain.js",
        "tongshefa": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "tongshefa" / "TongSheFaMain.js",
        "sanshiunited": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "sanshi" / "SanShiUnitedMain.js",
        "jieqi": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "jieqi" / "JieQiChartsMain.js",
        "guolao": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "guolao" / "GuoLaoChartMain.js",
        "germany": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "germany" / "AstroMidpoint.js",
        "primarydirect": direct_main,
        "relative": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "AstroRelative.js",
        "indiachart": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "IndiaChart.js",
        "fengshui": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "fengshui" / "FengShuiMain.js",
        "otherbu": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "dice" / "DiceMain.js",
        "solararc": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "AstroSolarArc.js",
        "solarreturn": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "AstroSolarReturn.js",
        "lunarreturn": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "AstroLunarReturn.js",
        "givenyear": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "AstroGivenYear.js",
        "profection": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "AstroProfection.js",
        "zodialrelease": root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "AstroZR.js",
    }

    top_level_tabs = {
        "占星": "astrochart",
        "星运": "direction",
        "八字": "bazi",
        "紫微": "ziwei",
        "七政": "guolao",
        "印占": "indiachart",
        "辅盘": "auxchart",
        "合盘": "relativechart",
        "三式": "sanshiunited",
        "六壬": "liureng",
        "遁甲": "dunjia",
        "六爻": "guazhan",
        "太乙": "taiyi",
        "分至": "jieqichart",
        "风水": "fengshui",
        "其他": "cnyibu",
        "AI分析": "aianalysis",
        "3D": "astrochart3D",
        "黄历": "calendar",
        "辅助": "cntradition",
    }
    for label, key in top_level_tabs.items():
        _assert_tab(index_js, label, key)

    cntrad_tabs = {
        "八卦类象": "guasym",
        "十二串宫": "cuangong12",
        "八字规则": "pithy",
    }
    for label, key in cntrad_tabs.items():
        _assert_tab(cntrad_main, label, key)

    cnyibu_tabs = {
        "宿盘": "suzhan",
        "金口诀": "jinkou",
        "统摄法": "tongshefa",
    }
    for label, key in cnyibu_tabs.items():
        _assert_tab(cnyibu_main, label, key)

    _assert_contains(index_js, "type: 'astro/fetchByFields'")
    for key in [
        "'jieqichart'",
        "'guolao'",
        "'hellenastro'",
        "'indiachart'",
        "'locastro'",
        "'cnyibu'",
        "'cntradition'",
        "'sanshiunited'",
        "'germanytech'",
        "'astrochart'",
        "'astrochart3D'",
        "'fengshui'",
        "'aianalysis'",
    ]:
        _assert_contains(index_js, key)
    for hook_key in [
        "hook={predictHook.astrochart}",
        "hook={predictHook.astrochart3D}",
        "hook={predictHook.direction}",
        "hook={predictHook.bazi}",
        "hook={predictHook.ziwei}",
        "hook={predictHook.guolao}",
        "hook={predictHook.indiachart}",
        "hook={predictHook.auxchart}",
        "hook={predictHook.relativechart}",
        "hook={predictHook.sanshiunited}",
        "hook={predictHook.liureng}",
        "hook={predictHook.dunjia}",
        "hook={predictHook.guazhan}",
        "hook={predictHook.taiyi}",
        "hook={predictHook.jieqichart}",
        "hook={predictHook.cnyibu}",
        "hook={predictHook.aianalysis}",
        "hook={predictHook.cntradition}",
        "hook={predictHook.astrochart3D}",
        "hook={predictHook.planetarium}",
        "hook={predictHook.calendar}",
    ]:
        _assert_contains(index_js, hook_key)

    for needle in [
        "tabPosition=\"right\"",
        "本次分析模型",
        "案例选择（命盘 / 事盘）",
        "参考组合 / 资料（多选）",
        "发送分析",
        "历史",
        "资料",
        "模版",
        "设置",
    ]:
        _assert_contains(ai_analysis_main, needle)

    for needle in [
        "currentTab === 'aianalysis'",
        "aianalysis:{",
    ]:
        _assert_contains(astro_model, needle)

    _assert_contains(page_header, "runAIExport")
    _assert_contains(page_header, "loadAIExportSettings")
    _assert_contains(page_header, "saveAIExportSettings")
    _assert_contains(page_header, "listAIExportTechniqueSettings")
    _assert_contains(page_header, "getCurrentAIExportContext")
    _assert_contains(page_header, "<XQButton className={styles.astroHeaderCommand} size=\"small\" iconName=\"aiExport\">AI导出</XQButton>")
    _assert_contains(page_header, "AI导出设置")
    _assert_contains(page_header, "XQCheckList")
    _assert_contains(page_header, "XQCheckItem")
    _assert_contains(page_header, "message.success('AI导出设置已保存')")

    for needle in [
        "PlusMinusTime value={dt}",
        "GeoCoordModal",
        "<TabPane tab=\"信息\" key=\"1\">",
        "<TabPane tab=\"相位\" key=\"2\">",
        "<TabPane tab=\"行星\" key=\"3\">",
        "<div className=\"horosa-info-card-title\">希腊点</div>",
        "<TabPane tab=\"古典\" key=\"4\">",
        "<TabPane tab=\"可能性\" key=\"5\">",
        "<TabPane tab=\"格局\" key=\"6\">",
    ]:
        _assert_contains(astro_chart_main, needle)

    for needle in [
        "AstroChart3D",
        "needChart3D",
        "PlusMinusTime value={dt}",
        "GeoCoordModal",
        "<TabPane tab=\"信息\" key=\"1\">",
        "<TabPane tab=\"相位\" key=\"2\">",
        "<TabPane tab=\"行星\" key=\"3\">",
        "<TabPane tab=\"希腊点\" key=\"4\">",
    ]:
        _assert_contains(astro_chart_main3d, needle)

    _assert_contains(astro_chart3d, "new Astro3D(opt)")
    _assert_contains(astro_chart3d, "this.astro3d.init()")
    _assert_contains(astro3d_core, "const ChartOptKey = 'chart3dOpt';")
    _assert_contains(astro3d_core, "const ModelUnavailableAtKey = 'horosa3dModelUnavailableAt';")

    _assert_contains(hellen_main, "currentTab: \"Chart13\"")
    _assert_contains(hellen_main, "<AstroChart13")
    _assert_contains(hellen_main, "hook={this.state.hook.Chart13}")
    _assert_contains(chart13, "fetchChart13Cached")
    _assert_contains(chart13, "request(`${Constants.ServerRoot}/chart13`")

    _assert_contains(loc_main, "<AstroAcg")
    _assert_contains(loc_main, "hook={this.state.hook.Acg}")
    _assert_contains(acg, "request(`${Constants.ServerRoot}/location/acg`")

    for needle in [
        "currentTab: \"Natal\"",
        "currentFractal: 1",
        "Hora:{",
        "Drekkana:{",
        "Navamsa:{",
        "Dasamsa:{",
        "Shodasamsa:{",
        "Chaturvimsamsa:{",
        "value={this.state.currentTab}",
        "chartnum={currentHook.fractal}",
        "onClick={()=>this.changeTab('Natal')}",
        "<strong>D{item.fractal}</strong>",
        "saveModuleAISnapshot('indiachart_current'",
        "saveModuleAISnapshot(`indiachart_${fractal}`",
    ]:
        _assert_contains(snapshot_expectations["indiachart"], needle) if "saveModuleAISnapshot" in needle else _assert_contains(root / "Horosa-Web" / "astrostudyui" / "src" / "components" / "astro" / "IndiaChartMain.js", needle)

    for needle in [
        "currentTab: '二十四节气'",
        "saveModuleAISnapshot('jieqi'",
        "saveModuleAISnapshot('jieqi_current'",
        "<TabPane tab='二十四节气' key='二十四节气'>",
        "tab={title+'星盘'}",
        "tab={title+'宿盘'}",
        "tab={title+'3D盘'}",
        "AstroChartMain3D",
    ]:
        _assert_contains(snapshot_expectations["jieqi"], needle)

    for needle in [
        "<TabPane tab=\"主/界限法\" key=\"primarydirect\">",
        "<TabPane tab=\"黄道星释\" key=\"zodialrelease\">",
        "<TabPane tab=\"法达星限\" key=\"firdaria\">",
        "<TabPane tab=\"小限法\" key=\"profection\">",
        "<TabPane tab=\"太阳弧\" key=\"solararc\">",
        "<TabPane tab=\"太阳返照\" key=\"solarreturn\">",
        "<TabPane tab=\"月亮返照\" key=\"lunarreturn\">",
        "<TabPane tab=\"流年法\" key=\"givenyear\">",
        "<TabPane tab=\"十年大运\" key=\"decennials\">",
    ]:
        _assert_contains(direct_main, needle)

    _assert_contains(module_snapshot, "export function saveModuleAISnapshot")
    _assert_contains(module_snapshot, "export function loadModuleAISnapshot")
    _assert_contains(astro_snapshot, "export function saveAstroAISnapshot")
    _assert_contains(astro_snapshot, "export function loadAstroAISnapshot")
    _assert_contains(astro_snapshot, "export function getAstroAISnapshotForCurrent")
    _assert_contains(astro_model, "saveAstroAISnapshot(Result, values)")
    _assert_contains(astro_model, "saveAstroAISnapshot(Result, fields)")
    _assert_contains(astro_model, "saveAstroAISnapshot(Result, fieldValues)")

    for module_name, path in snapshot_expectations.items():
        _assert_contains(path, f"saveModuleAISnapshot('{module_name}'")

    for module_name in ["liureng", "jinkou", "qimen", "tongshefa", "guazhan"]:
        path = snapshot_expectations[module_name]
        _assert_contains(path, f"loadModuleAISnapshot('{module_name}')")

    _assert_contains(snapshot_expectations["jieqi"], "saveModuleAISnapshot('jieqi_current'")
    _assert_contains(snapshot_expectations["indiachart"], "saveModuleAISnapshot('indiachart_current'")
    _assert_contains(snapshot_expectations["indiachart"], "saveModuleAISnapshot(`indiachart_${fractal}`")

    _assert_contains(ai_export, "const AI_EXPORT_TECHNIQUES = [")
    _assert_contains(ai_export, "const AI_EXPORT_PRESET_SECTIONS = {")
    _assert_contains(ai_export, "export function listAIExportTechniqueSettings()")
    _assert_contains(ai_export, "export function getCurrentAIExportContext()")
    _assert_contains(ai_export, "export async function runAIExport(")

    ai_keys = [
        "astrochart",
        "indiachart",
        "astrochart_like",
        "relative",
        "primarydirect",
        "zodialrelease",
        "firdaria",
        "profection",
        "solararc",
        "solarreturn",
        "lunarreturn",
        "givenyear",
        "bazi",
        "ziwei",
        "suzhan",
        "sixyao",
        "tongshefa",
        "liureng",
        "jinkou",
        "qimen",
        "sanshiunited",
        "taiyi",
        "guolao",
        "germany",
        "jieqi",
        "otherbu",
        "fengshui",
    ]
    for key in ai_keys:
        _assert_contains(ai_export, f"key: '{key}'")
        _assert_contains(ai_export, f"{key}: [")

    for refresh_key in [
        "guazhan",
        "sixyao",
        "liureng",
        "jinkou",
        "qimen",
        "sanshiunited",
        "tongshefa",
        "taiyi",
        "germany",
        "jieqi_current",
        "jieqi",
        "primarydirect",
        "zodialrelease",
        "firdaria",
        "profection",
        "solararc",
        "solarreturn",
        "lunarreturn",
        "givenyear",
        "relative",
        "otherbu",
        "fengshui",
    ]:
        _assert_contains(ai_export, f"requestModuleSnapshotRefresh('{refresh_key}')")

    for extractor in [
        "extractPrimaryDirectContent",
        "extractJieQiContent",
        "extractGermanyContent",
        "extractSanShiUnitedContent",
        "extractQiMenContent",
        "extractLiuRengContent",
        "extractJinKouContent",
        "extractSixYaoContent",
        "extractTongSheFaContent",
        "extractRelativeContent",
        "extractSimpleModuleContent",
    ]:
        _assert_contains(ai_export, f"function {extractor}(")

    _assert_contains(ai_export, "return extractPrimaryDirectContent(context);")
    _assert_contains(ai_export, "return extractJieQiContent(context);")
    _assert_contains(ai_export, "return extractGermanyContent(context);")
    _assert_contains(ai_export, "return extractSanShiUnitedContent(context);")
    _assert_contains(ai_export, "return extractRelativeContent(context);")
    _assert_contains(ai_export, "return extractSimpleModuleContent('guolao');")
    _assert_contains(ai_export, "return extractSimpleModuleContent('bazi');")
    _assert_contains(ai_export, "return extractSimpleModuleContent('ziwei');")
    _assert_contains(ai_export, "return extractSimpleModuleContent('suzhan');")

    _assert_contains(precise_bridge, "export async function fetchPreciseNongli(params)")
    _assert_contains(precise_bridge, "export async function fetchPreciseJieqiYear(params)")
    _assert_contains(precise_bridge, "export async function fetchPreciseJieqiSeed(params)")
    _assert_contains(precise_bridge, "request(`${ServerRoot}/nongli/time`")
    _assert_contains(precise_bridge, "request(`${ServerRoot}/jieqi/year`")

    _assert_contains(chart13, "request(`${Constants.ServerRoot}/chart13`")
    _assert_contains(acg, "request(`${Constants.ServerRoot}/location/acg`")
    _assert_contains(hellen_main, "this.props.hook.fun = (fields)=>")
    _assert_contains(loc_main, "this.props.hook.fun = (fields)=>")
    _assert_contains(direct_main, "applyPrimaryDirectionConfig(pdMethod, pdTimeKey)")
    _assert_contains(pd_table, "const pdTypeOutOfSync = appliedPdState.pdtype !== DEFAULT_PD_TYPE;")
    _assert_contains(pd_table, "needsPdRecompute(){")
    _assert_contains(pd_table, "if(!this.needsPdRecompute())")
    _assert_contains(pd_table, "disabled={!needsPdRecompute}")
    _assert_contains(pd_table, "needsPdRecompute ? (isPdConfigDirty ? '重新计算' : '计算') : '已同步'")
    _assert_contains(direct_main, "includePrimaryDirection: true")
    _assert_contains(astro_model, "pdtype: fields.pdtype ? fields.pdtype.value : 0")

    _assert_contains(verify_sh, "verifyPrimaryDirectionRuntime.js")
    _assert_contains(verify_sh, "verifyHorosaRuntimeFull.js")
    _assert_contains(verify_sh, "check_primary_direction_astroapp_integration.py")
    _assert_contains(verify_sh, "check_horosa_full_integration.py")

    report = {
        "status": "ok",
        "top_level_tabs_checked": len(top_level_tabs),
        "cntradition_tabs_checked": len(cntrad_tabs),
        "cnyibu_tabs_checked": len(cnyibu_tabs),
        "snapshot_modules_checked": sorted(snapshot_expectations.keys()),
        "ai_export_keys_checked": ai_keys,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
