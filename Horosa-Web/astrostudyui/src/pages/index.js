import { connect  } from 'dva';
import { Drawer, Tabs, Spin, } from 'antd';
import {
    AimOutlined,
    ApartmentOutlined,
    ApiOutlined,
    AppstoreOutlined,
    BarChartOutlined,
    BookOutlined,
    BorderOuterOutlined,
    BranchesOutlined,
    BuildOutlined,
    CalendarOutlined,
    CompassOutlined,
    DeploymentUnitOutlined,
    ExperimentOutlined,
    FieldTimeOutlined,
    GlobalOutlined,
    HeartOutlined,
    PlayCircleOutlined,
    RadarChartOutlined,
    RiseOutlined,
    StarOutlined,
    ThunderboltOutlined,
    ToolOutlined,
} from '@ant-design/icons';
import DateTime from '../components/comp/DateTime';
import LoginForm from '../components/user/LoginForm';
import RegisterForm from '../components/user/RegisterForm';
import ResetPwdForm from '../components/user/ResetPwdForm';
import ChangePwdForm from '../components/user/ChangePwdForm';
import ChangeParamsFormComp from '../components/user/ChangeParamsFormComp';
import ChartAddFormComp from '../components/user/ChartAddFormComp';
import ChartEditFormComp from '../components/user/ChartEditFormComp';
import ChartList from '../components/user/ChartList';
import CaseAddFormComp from '../components/user/CaseAddFormComp';
import CaseEditFormComp from '../components/user/CaseEditFormComp';
import CaseList from '../components/user/CaseList';
import AstroFormComp from '../components/astro/AstroFormComp';
import AstroChartMain from '../components/astro/AstroChartMain';
import AstroChartMain3D from '../components/astro3d/AstroChartMain3D';
import AuxChartMain from '../components/auxchart/AuxChartMain';
import IndiaChartMain from '../components/astro/IndiaChartMain';
import AstroRelative from '../components/astro/AstroRelative';
import AstroDirectMain from '../components/direction/AstroDirectMain';
import AspSelector from '../components/astro/AspSelector';
import PlanetSelector from '../components/astro/PlanetSelector';
import ChartDisplaySelector from '../components/astro/ChartDisplaySelector';
import ChartsGps from '../components/user/ChartsGps';
import ChartMemo from '../components/comp/ChartMemo';
import JieQiChartsMain from '../components/jieqi/JieQiChartsMain';
import CnTraditionMain from '../components/cntradition/CnTraditionMain';
import CnYiBuMain from '../components/cnyibu/CnYiBuMain';
import CalendarMain from '../components/calendar/CalendarMain';
import FengShuiMain from '../components/fengshui/FengShuiMain';
import SanShiUnitedMain from '../components/sanshi/SanShiUnitedMain';
import AIAnalysisMain from '../components/aianalysis/AIAnalysisMain';
import BookMain from '../components/reader/BookMain';
import MediaMain from '../components/multimedia/MediaMain';
import AdminToolsMain from '../components/admintools/AdminToolsMain';
import GuoLaoChartMain from '../components/guolao/GuoLaoChartMain';
import CommToolsMain from '../components/commtools/CommToolsMain';
import DLFeature from '../components/deeplearn/DLFeature';
import HomePageSetup from '../components/HomePageSetup';
import BaZi from '../components/cntradition/BaZi';
import ZiWeiMain from '../components/ziwei/ZiWeiMain';
import GuaZhanMain from '../components/guazhan/GuaZhanMain';
import LiuRengMain from '../components/lrzhan/LiuRengMain';
import DunJiaMain from '../components/dunjia/DunJiaMain';
import TaiYiMain from '../components/taiyi/TaiYiMain';
import * as AstroConst from '../constants/AstroConst';
import {convertToArray} from '../utils/helper';
import { APPEARANCE_DARK } from '../utils/appearance';

const TabPane = Tabs.TabPane;
let fetchByFieldsTimer = null;

const mainTabIcons = {
    占星: <StarOutlined />,
    星盘: <StarOutlined />,
    星运: <RiseOutlined />,
    八字: <BorderOuterOutlined />,
    紫微: <AimOutlined />,
    '3D': <AppstoreOutlined />,
    三维盘: <AppstoreOutlined />,
    七政: <CompassOutlined />,
    印占: <GlobalOutlined />,
    辅盘: <BarChartOutlined />,
    合盘: <HeartOutlined />,
    七政四余: <CompassOutlined />,
    印度占星: <GlobalOutlined />,
    三式: <ApiOutlined />,
    三式合一: <ApiOutlined />,
    六壬: <DeploymentUnitOutlined />,
    遁甲: <ThunderboltOutlined />,
    六爻: <BranchesOutlined />,
    太乙: <RadarChartOutlined />,
    分至: <FieldTimeOutlined />,
    节气盘: <FieldTimeOutlined />,
    风水: <CompassOutlined />,
    其他: <ApartmentOutlined />,
    其他术数: <ApartmentOutlined />,
    AI分析: <ExperimentOutlined />,
    黄历: <CalendarOutlined />,
    辅助: <BuildOutlined />,
    书籍阅读: <BookOutlined />,
    星阙直播: <PlayCircleOutlined />,
    管理工具: <ToolOutlined />,
};

const navigationPages = [
    { label: '占星', key: 'astrochart' },
    { label: '星运', key: 'direction' },
    { label: '八字', key: 'bazi' },
    { label: '紫微', key: 'ziwei' },
    { label: '七政', key: 'guolao' },
    { label: '印占', key: 'indiachart' },
    { label: '辅盘', key: 'auxchart' },
    { label: '合盘', key: 'relativechart' },
    { label: '三式', key: 'sanshiunited' },
    { label: '六壬', key: 'liureng' },
    { label: '遁甲', key: 'dunjia' },
    { label: '六爻', key: 'guazhan' },
    { label: '太乙', key: 'taiyi' },
    { label: '分至', key: 'jieqichart' },
    { label: '风水', key: 'fengshui' },
    { label: '其他', key: 'cnyibu' },
    { label: 'AI分析', key: 'aianalysis' },
    { label: '3D', key: 'astrochart3D' },
    { label: '黄历', key: 'calendar' },
    { label: '辅助', key: 'cntradition' },
];

function mainTab(label, group, options = {}){
    const icon = mainTabIcons[label] || <StarOutlined />;
    return (
        <span
            className={`horosa-main-tab-label${options.hidden ? ' horosa-main-tab-hidden' : ''}`}
            title={label}
            aria-label={label}
        >
            <span className="horosa-main-tab-icon">{icon}</span>
            <span className="horosa-main-tab-copy">
                {group ? <span className="horosa-main-tab-group">{group}</span> : null}
                <span className="horosa-main-tab-text">{label}</span>
            </span>
        </span>
    );
}

function AstroIndex({dispatch, astro, app, user, rules, }){
    const { tokenImg, registerFields, loginFields, loading, loadingText, refresh, chartDisplay, chartStyle, indiaChartStyle, aspects, planetDisplay, lotsDisplay, resolvedAppearance, showPdBounds, showPlanetHouseInfo, showAstroMeaning, showOnlyRulExaltReception} = app;
    const {
        pwdFields,
        userInfo,
        charts,
        currentChart,
        admin,
        pageSize,
        pageIndex,
        total,
        cases,
        currentCase,
        casePageSize,
        casePageIndex,
        caseTotal,
    } = user;
 	const { height, fields, chartObj, drawerVisible, predictHook, memo, memoType, currentTab, currentSubTab, deeplearn} = astro;
    const { ziwei, } = rules; 

    
    function closeDrawer(){
        dispatch({
            type: 'astro/closeDrawer',
            payload:{},
        });
    }

    function changeTab(key){
        if(predictHook[key] && predictHook[key].fun){
            if(key === 'indiachart' || key === 'cntradition' || key === 'jieqichart'
                || key === 'otherbu' || key === 'cnyibu' || key === 'germanytech'
                || key === 'guolao' || key === 'hellenastro'  || key === 'astrochart'
                || key === 'locastro' || key === 'admintools' || key === 'astrochart3D'
                || key === 'fengshui' || key === 'sanshiunited' || key === 'aianalysis'
                || key === 'bazi' || key === 'ziwei' || key === 'guazhan'
                || key === 'liureng' || key === 'dunjia' || key === 'taiyi'
                || key === 'auxchart'){
                predictHook[key].fun(fields);
            }else if(key === 'astroreader'){
                predictHook[key].fun();
            }else{
                predictHook[key].fun(chartObj);
            }
        }

        const cnTraditionTabs = ['guasym', 'cuangong12', 'pithy'];
        const cnYiBuTabs = ['suzhan', 'jinkou', 'tongshefa'];
        const auxChartTabs = ['germanytech', 'hellenastro', 'locastro', 'otherbu'];
        let nextSubTab = null;
        if(key === 'cntradition'){
            nextSubTab = cnTraditionTabs.indexOf(currentSubTab) >= 0 ? currentSubTab : 'guasym';
        }else if(key === 'cnyibu'){
            nextSubTab = cnYiBuTabs.indexOf(currentSubTab) >= 0 ? currentSubTab : 'suzhan';
        }else if(key === 'auxchart'){
            nextSubTab = auxChartTabs.indexOf(currentSubTab) >= 0 ? currentSubTab : 'germanytech';
        }else if(key === 'direction' || key === 'relativechart'){
            nextSubTab = currentSubTab;
        }
        
        dispatch({
            type: 'astro/save',
            payload:{ 
                chartObj: chartObj,
                currentTab: key,
                currentSubTab: nextSubTab,
            },
        });    

    }

    function changeCond(values){
        let flds = {
            ...fields,
        };  
        if(values.nohook){
            flds.nohook = true;
        }  

        if(values.tm !== undefined && values.tm != null){
            let birth = values.tm;
            flds.date.value = birth.clone();
            flds.time.value = birth.clone();
            flds.ad.value = birth.ad;
            flds.zone.value = birth.zone
        }

        if(values.hsys !== undefined && values.hsys !== null){
            flds.hsys.value = values.hsys;
        }
        if(values.zodiacal !== undefined && values.zodiacal !== null){
            flds.zodiacal.value = values.zodiacal;
        }
        if(values.lon !== undefined && values.lon !== null){
            flds.lon.value = values.lon;
            flds.lat.value = values.lat;
            flds.gpsLon.value = values.gpsLon;
            flds.gpsLat.value = values.gpsLat;
        }
        if(values.southchart !== undefined && values.southchart !== null){
            flds.southchart.value = values.southchart;
        }
        if(flds.lat.value >= 0){
            let lat = flds.lat.value;
            if(lat.toLowerCase().indexOf('n') >= 0){
                flds.southchart.value = 0;
            }
        }

        const isUnconfirmedTime = values && values.tm !== undefined && values.tm !== null && values.confirmed === false;
        if(isUnconfirmedTime){
            if(fetchByFieldsTimer){
                clearTimeout(fetchByFieldsTimer);
            }
            const queuedPayload = {
                ...flds,
                __requestOptions: {
                    silent: true,
                },
            };
            fetchByFieldsTimer = setTimeout(()=>{
                dispatch({
                    type: 'astro/fetchByFields',
                    payload: queuedPayload,
                });
                fetchByFieldsTimer = null;
            }, 180);
            return flds;
        }

        if(fetchByFieldsTimer){
            clearTimeout(fetchByFieldsTimer);
            fetchByFieldsTimer = null;
        }

        dispatch({
            type: 'astro/fetchByFields',
            payload: flds,
        });

        return flds;
    }

    function endRefresh(){
        setTimeout(()=>{
            dispatch({
                type: 'app/endRefresh',
                payload: {},
            });               
        }, 1000);
    }
    
    AstroConst.setColorTheme(resolvedAppearance === APPEARANCE_DARK ? 8 : AstroConst.DefaultColorTheme);
    
    let idxstyle = {
        backgroundColor: 'var(--horosa-bg)',
        height: height,
    };

    if(refresh){
        endRefresh();
    }

    let tip = '载入中...';
    if(loadingText){
        tip = loadingText;
    }

    let aryfields = convertToArray(fields);
    let arychartflds = convertToArray(currentChart);
    let arycaseflds = convertToArray(currentCase);
    let aryregflds = convertToArray(registerFields);
    let aryloginflds = convertToArray(loginFields);
    const drawerNavigationPages = navigationPages.concat(
        userInfo ? [{ label: '书籍阅读', key: 'astroreader' }, { label: '星阙直播', key: 'liveplayer' }] : [],
        admin ? [{ label: '管理工具', key: 'admintools' }] : []
    );

	return (
		<div style={idxstyle}>
        <Spin spinning={loading} size="large" tip={tip}>
            <Tabs 
                defaultActiveKey="astrochart" tabPosition='left' onChange={changeTab}
                activeKey={currentTab}
                className='mainRootTabs horosa-nav-in-drawer'
                style={{ height: height }}
            >
                <TabPane tab={mainTab('占星', '命')} key="astrochart">
	                    <AstroChartMain 
	                        value={chartObj} 
                        onChange={changeCond}
                        fields={fields} 
                        fieldsAry={aryfields}
                        height={height} 
                        chartDisplay={chartDisplay}
                        chartStyle={chartStyle}
                        planetDisplay={planetDisplay}
	                        lotsDisplay={lotsDisplay}
	                        showPlanetHouseInfo={showPlanetHouseInfo}
	                        showAstroMeaning={showAstroMeaning}
	                        memo={memo}
	                        dispatch={dispatch}
	                        hook={predictHook.astrochart}
                            onNavigate={changeTab}
                            showQuickActions={true}
                            featureLinks={[
                                { label: '星运', key: 'direction', desc: '推运、返照与时序' },
                                { label: '辅盘', key: 'auxchart', desc: '量化、十三分与地图' },
                                { label: '合盘', key: 'relativechart', desc: '关系与组合分析' },
                                { label: '分至', key: 'jieqichart', desc: '节气与太阳时点' },
                            ]}
	                    />
                </TabPane>

                <TabPane tab={mainTab('星运', null, { hidden: true })} key="direction">
	                    <AstroDirectMain
                        height={height} 
                        fields={fields}
                        fieldsAry={aryfields}
                        chartObj={chartObj}
                        chartDisplay={chartDisplay}
                        planetDisplay={planetDisplay}
	                        lotsDisplay={lotsDisplay}
	                        showPlanetHouseInfo={showPlanetHouseInfo}
	                        showAstroMeaning={showAstroMeaning}
	                        hook={predictHook.direction}
	                        dispatch={dispatch}
	                        currentSubTab={currentSubTab}
                    />
                </TabPane>

                <TabPane tab={mainTab('八字')} key="bazi">
                    <BaZi
                        height={height}
                        fields={fields}
                        hook={predictHook.bazi}
                        dispatch={dispatch}
                    />
                </TabPane>

                <TabPane tab={mainTab('紫微')} key="ziwei">
                    <ZiWeiMain
                        height={height}
                        fields={fields}
                        hook={predictHook.ziwei}
                        dispatch={dispatch}
                    />
                </TabPane>

                <TabPane tab={mainTab('七政')} key="guolao">
                    <GuoLaoChartMain 
                        value={chartObj} 
                        onChange={changeCond}
                        fields={fields} 
                        fieldsAry={aryfields}
                        height={height} 
                        chartDisplay={chartDisplay}
                        indiaChartStyle={indiaChartStyle}
                        planetDisplay={planetDisplay}
                        lotsDisplay={lotsDisplay}
                        hook={predictHook.guolao}
                        dispatch={dispatch}
                    />
                </TabPane>

                <TabPane tab={mainTab('印占')} key="indiachart">
	                    <IndiaChartMain
                        onChange={changeCond}
                        fields={fields} 
                        fieldsAry={aryfields}
                        height={height} 
                        chartDisplay={chartDisplay}
                        indiaChartStyle={indiaChartStyle}
                        planetDisplay={planetDisplay}
	                        lotsDisplay={lotsDisplay}
	                        showPlanetHouseInfo={showPlanetHouseInfo}
	                        showAstroMeaning={showAstroMeaning}
	                        hook={predictHook.indiachart}
	                        dispatch={dispatch}
	                    />
                </TabPane>

                <TabPane tab={mainTab('辅盘', null, { hidden: true })} key="auxchart">
                    <AuxChartMain
                        chart={chartObj}
                        onChange={changeCond}
                        height={height}
                        fields={fields}
                        fieldsAry={aryfields}
                        chartDisplay={chartDisplay}
                        planetDisplay={planetDisplay}
                        lotsDisplay={lotsDisplay}
                        showPlanetHouseInfo={showPlanetHouseInfo}
                        showAstroMeaning={showAstroMeaning}
                        hook={predictHook.auxchart}
                        dispatch={dispatch}
                        currentSubTab={currentSubTab}
                    />
                </TabPane>

                <TabPane tab={mainTab('合盘', null, { hidden: true })} key="relativechart">
	                    <AstroRelative
                        fields={fields} 
                        fieldsAry={aryfields}
                        height={height} 
                        chartDisplay={chartDisplay}
                        planetDisplay={planetDisplay}
	                        lotsDisplay={lotsDisplay}
	                        showPlanetHouseInfo={showPlanetHouseInfo}
	                        showAstroMeaning={showAstroMeaning}
	                        hook={predictHook.relativechart}
	                        dispatch={dispatch}
	                        currentSubTab={currentSubTab}
                    />
                </TabPane>

                <TabPane tab={mainTab('三式', '卜')} key="sanshiunited">
	                    <SanShiUnitedMain
	                        height={height}
                        fields={fields}
                        fieldsAry={aryfields}
	                        chartObj={chartObj}
	                        showPlanetHouseInfo={showPlanetHouseInfo}
	                        showAstroMeaning={showAstroMeaning}
	                        dispatch={dispatch}
	                        hook={predictHook.sanshiunited}
	                    />
                </TabPane>

                <TabPane tab={mainTab('六壬')} key="liureng">
                    <LiuRengMain
                        value={chartObj}
                        height={height}
                        fields={fields}
                        hook={predictHook.liureng}
                        dispatch={dispatch}
                    />
                </TabPane>

                <TabPane tab={mainTab('遁甲')} key="dunjia">
                    <DunJiaMain
                        value={chartObj}
                        height={height}
                        fields={fields}
                        hook={predictHook.dunjia}
                        dispatch={dispatch}
                    />
                </TabPane>

                <TabPane tab={mainTab('六爻')} key="guazhan">
                    <GuaZhanMain
                        value={chartObj}
                        height={height}
                        fields={fields}
                        hook={predictHook.guazhan}
                        dispatch={dispatch}
                    />
                </TabPane>

                <TabPane tab={mainTab('太乙')} key="taiyi">
                    <TaiYiMain
                        value={chartObj}
                        height={height}
                        fields={fields}
                        hook={predictHook.taiyi}
                        dispatch={dispatch}
                    />
                </TabPane>

                <TabPane tab={mainTab('分至', null, { hidden: true })} key="jieqichart">
	                    <JieQiChartsMain
                        height={height} 
                        fields={fields}
                        fieldsAry={aryfields}
                        chartDisplay={chartDisplay}
                        planetDisplay={planetDisplay}
	                        lotsDisplay={lotsDisplay}
	                        showPlanetHouseInfo={showPlanetHouseInfo}
	                        showAstroMeaning={showAstroMeaning}
	                        hook={predictHook.jieqichart}
	                        dispatch={dispatch}
	                    />
                </TabPane>

                <TabPane tab={mainTab('风水')} key="fengshui">
                    <FengShuiMain
                        height={height}
                        fields={fields}
                        fieldsAry={aryfields}
                        dispatch={dispatch}
                    />
                </TabPane>

                <TabPane tab={mainTab('其他')} key="cnyibu">
                    <CnYiBuMain
                        chart={chartObj}
                        height={height}
                        fields={fields}
                        fieldsAry={aryfields}
                        chartDisplay={chartDisplay}
                        planetDisplay={planetDisplay}
                        hook={predictHook.cnyibu}
                        dispatch={dispatch}
                        currentSubTab={currentSubTab}
                    />
                </TabPane>

                <TabPane tab={mainTab('AI分析', '工具')} key="aianalysis">
                    <AIAnalysisMain
                        height={height}
                        fields={fields}
                        fieldsAry={aryfields}
                        chartObj={chartObj}
                        dispatch={dispatch}
                        hook={predictHook.aianalysis}
                    />
                </TabPane>

                {
                    true && (
                    <TabPane tab={mainTab('3D')} key="astrochart3D">
	                        <AstroChartMain3D 
                            value={chartObj} 
                            onChange={changeCond}
                            fields={fields} 
                            fieldsAry={aryfields}
                            height={height} 
                            currentTab={currentTab}
                            chartDisplay={chartDisplay}
                            planetDisplay={planetDisplay}
	                            lotsDisplay={lotsDisplay}
	                            showPlanetHouseInfo={showPlanetHouseInfo}
	                            showAstroMeaning={showAstroMeaning}
	                            dispatch={dispatch}
	                            hook={predictHook.astrochart3D}
	                        />
                    </TabPane>   
                    )
                }

                <TabPane tab={mainTab('黄历')} key="calendar">
                    <CalendarMain
                        height={height} 
                        fields={fields}
                        fieldsAry={aryfields}
                        hook={predictHook.calendar}
                        dispatch={dispatch}
                    />
                </TabPane>

                <TabPane tab={mainTab('辅助')} key="cntradition">
                    <CnTraditionMain
                        chart={chartObj}
                        height={height}
                        fields={fields}
                        fieldsAry={aryfields}
                        chartDisplay={chartDisplay}
                        planetDisplay={planetDisplay}
                        hook={predictHook.cntradition}
                        dispatch={dispatch}
                        currentSubTab={currentSubTab}
                    />
                </TabPane>

                {
                    userInfo && (
                        <TabPane tab={mainTab('书籍阅读', '内容与管理')} key="astroreader">
                            <BookMain 
                                height={height}
                                userInfo={userInfo}
                                dispatch={dispatch}
                                hook={predictHook.astroreader}
                            />
                        </TabPane>
                    )
                }

                {
                    userInfo && (
                        <TabPane tab={mainTab('星阙直播')} key="liveplayer">
                            <MediaMain 
                                height={height}
                                dispatch={dispatch}
                                userInfo={userInfo}
                                currentSubTab={currentSubTab}
                                admin={admin}
                            />
                        </TabPane>
                    )
                }

                {
                    admin && (
                        <TabPane tab={mainTab('管理工具')} key="admintools">
                            <AdminToolsMain />
                        </TabPane>
                    )
                }

            </Tabs>

            <Drawer
                title='星盘配置'
                width={720}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.query}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <AstroFormComp 
                    { ...fields }
                    fields={fields}
                    fieldsAry={aryfields}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='注册'
                width={300}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.register}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <RegisterForm 
                    {...registerFields}
                    tokenImg={tokenImg}
                    fields={registerFields}
                    fieldsAry={aryregflds}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='登录'
                width={300}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.login}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <LoginForm 
                    {...loginFields}
                    fields={loginFields}
                    fieldsAry={aryloginflds}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='忘记密码'
                width={300}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.resetpwd}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <ResetPwdForm 
                    {...registerFields}
                    tokenImg={tokenImg}
                    fields={registerFields}
                    fieldsAry={aryregflds}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='修改密码'
                width={300}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.changepwd}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <ChangePwdForm 
                    {...pwdFields}
                    fields={pwdFields}
                    fieldsAry={convertToArray(pwdFields)}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='修改参数'
                width={700}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.changeparams}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <ChangeParamsFormComp 
                    {...fields}
                    fields={fields}
                    fieldsAry={aryfields}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='添加星盘'
                width={700}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.chartadd}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <ChartAddFormComp 
                    {...currentChart}
                    fields={currentChart}
                    fieldsAry={arychartflds}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='编辑星盘'
                width={700}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.chartedit}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <ChartEditFormComp 
                    {...currentChart}
                    fields={currentChart}
                    fieldsAry={arychartflds}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='星盘列表'
                width={950}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={false}
                open={drawerVisible.chartlist}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <ChartList
                    height={height} 
                    userInfo={userInfo}
                    charts={charts}
                    pageSize={pageSize}
                    pageIndex={pageIndex}
                    total={total}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='添加起课'
                width={700}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.caseadd}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}
            >
                <CaseAddFormComp
                    {...currentCase}
                    fields={currentCase}
                    fieldsAry={arycaseflds}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='编辑起课'
                width={700}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.caseedit}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}
            >
                <CaseEditFormComp
                    {...currentCase}
                    fields={currentCase}
                    fieldsAry={arycaseflds}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='起课列表'
                width={950}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={false}
                open={drawerVisible.caselist}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}
            >
                <CaseList
                    height={height}
                    userInfo={userInfo}
                    cases={cases}
                    casePageSize={casePageSize}
                    casePageIndex={casePageIndex}
                    caseTotal={caseTotal}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='相位选择'
                width={250}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.selectasp}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <AspSelector
                    value={aspects}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='行星选择'
                width={250}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.selectplanet}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <PlanetSelector
                    value={planetDisplay}
                    lots={lotsDisplay}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='星盘组件'
                width={300}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.selectchartdisplay}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <ChartDisplaySelector
                    value={chartDisplay}
                    showPdBounds={fields && fields.showPdBounds ? fields.showPdBounds.value : showPdBounds}
                    showPlanetHouseInfo={showPlanetHouseInfo}
                    showAstroMeaning={showAstroMeaning}
                    showOnlyRulExaltReception={showOnlyRulExaltReception}
                    fields={fields}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='我的星盘分布'
                width={900}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={true}
                open={drawerVisible.chartsgps}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <ChartsGps
                    height={height} 
                    charts={charts}
                    userInfo={userInfo}
                    dispatch={dispatch}
                />
            </Drawer>

            <Drawer
                title='命盘批注'
                width={500}
                placement="right"
                destroyOnClose={true}
                onClose={closeDrawer}
                maskClosable={true}
                open={drawerVisible.memo}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <ChartMemo
                    memoType={memoType}
                    memo={memo}
                    currentSubTab={currentSubTab}
                    currentTab={currentTab}
                    userInfo={userInfo}
                    currentChart={currentChart}
                    dispatch={dispatch}
                    loading={loading}
                />
            </Drawer>

            <Drawer
                title='小工具'
                width={960}
                placement="left"
                destroyOnClose={true}
                onClose={closeDrawer}
                maskClosable={true}
                open={drawerVisible.commtools}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <CommToolsMain
                    fields={fields}
                    dispatch={dispatch}
                    loading={loading}
                />
            </Drawer>

            <Drawer
                title='人生事件设置'
                width={1000}
                placement="left"
                onClose={closeDrawer}
                maskClosable={true}
                destroyOnClose={false}
                open={drawerVisible.chartdeeplearn}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <DLFeature
                    {...currentChart}
                    fields={currentChart}
                    fieldsAry={arychartflds}
                    deeplearn={deeplearn}
                    height={height} 
                    dispatch={dispatch}
                    loading={loading}
                />
            </Drawer>

            <Drawer
                title='导航'
                width={200}
                placement="left"
                destroyOnClose={true}
                onClose={closeDrawer}
                maskClosable={true}
                open={drawerVisible.homepage}
                style={{
                    height: 'calc(100% - 0px)',
                    overflow: 'auto',
                    paddingBottom: 53,
                    backgroundColor: 'transparent',
                }}        
            >
                <HomePageSetup
                    dispatch={dispatch}
                    loading={loading}
                    pages={drawerNavigationPages}
                    currentKey={currentTab}
                    onNavigate={changeTab}
                    onClose={closeDrawer}
                />
            </Drawer>

        </Spin>
		</div>
	);
}

function mapStateToProps(state){
    const { astro, app, user, rules, } = state;

    return {
		astro: astro,
        app: app,
        user: user,
        rules: rules,
    };
}

export default connect(mapStateToProps)(AstroIndex);
