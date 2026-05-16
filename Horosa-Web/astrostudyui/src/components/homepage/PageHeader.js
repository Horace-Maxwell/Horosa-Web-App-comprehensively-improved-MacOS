import React from 'react';
import { Avatar, Dropdown, message, Tooltip } from 'antd';
import {
	UserOutlined,
	LogoutOutlined,
} from '@ant-design/icons';
import blogo from '../../assets/blogo.jpg';
import {
	APPEARANCE_DARK,
	APPEARANCE_LIGHT,
	APPEARANCE_SYSTEM,
	getAppearanceLabel,
	getNextAppearanceMode,
	normalizeAppearanceMode,
} from '../../utils/appearance';
import {
	runAIExport,
	loadAIExportSettings,
	saveAIExportSettings,
	listAIExportTechniqueSettings,
	getCurrentAIExportContext,
	AI_EXPORT_SETTINGS_VERSION,
} from '../../utils/aiExport';
import {
	XQButton,
	XQCheckItem,
	XQCheckList,
	XQIconButton,
	XQInput,
	XQModal,
	XQSectionTitle,
	XQSelect,
	XQToolbar,
} from '../xq-ui';
import XQIcon from '../xq-icons';
import styles from './PageHeader.less';

const Option = XQSelect.Option;

function PageHeader(props){
	const [aiSettingVisible, setAiSettingVisible] = React.useState(false);
	const [aiSettingData, setAiSettingData] = React.useState(loadAIExportSettings());
	const aiSettingDataRef = React.useRef(aiSettingData);
	const [aiSettingTechs, setAiSettingTechs] = React.useState(listAIExportTechniqueSettings());
	const [aiSettingKey, setAiSettingKey] = React.useState('astrochart');

	const currentSettingTech = aiSettingTechs.find((item)=>item.key === aiSettingKey) || null;
	const currentSettingOptions = currentSettingTech && currentSettingTech.options ? currentSettingTech.options : [];
	const currentSettingSupportsPlanetInfo = !!(currentSettingTech && currentSettingTech.supportsPlanetInfo);
	const currentSettingSupportsAstroMeaning = !!(currentSettingTech && currentSettingTech.supportsAstroMeaning);
	const currentSettingMeaningTitle = currentSettingTech && currentSettingTech.astroMeaningTitle
		? currentSettingTech.astroMeaningTitle
		: '占星注释（仅AI导出）：';
	const currentSettingMeaningCheckbox = currentSettingTech && currentSettingTech.astroMeaningCheckbox
		? currentSettingTech.astroMeaningCheckbox
		: '在对应分段输出星/宫/座/相/希腊点释义';
	const currentSettingSelected = (()=>{
		const sections = aiSettingData && aiSettingData.sections ? aiSettingData.sections : {};
		if(Array.isArray(sections[aiSettingKey])){
			return sections[aiSettingKey];
		}
		return currentSettingOptions.slice(0);
	})();
	const currentSettingPlanetInfo = (()=>{
		const map = aiSettingData && aiSettingData.planetInfo ? aiSettingData.planetInfo : {};
		const one = map && map[aiSettingKey] ? map[aiSettingKey] : null;
		if(!one){
			return {
				showHouse: 1,
				showRuler: 1,
			};
		}
		return {
			showHouse: one && (one.showHouse === 1 || one.showHouse === true) ? 1 : 0,
			showRuler: one && (one.showRuler === 1 || one.showRuler === true) ? 1 : 0,
		};
	})();
	const currentSettingAstroMeaning = (()=>{
		const map = aiSettingData && aiSettingData.astroMeaning ? aiSettingData.astroMeaning : {};
		const one = map && map[aiSettingKey] ? map[aiSettingKey] : null;
		return {
			enabled: one && (one.enabled === 1 || one.enabled === true) ? 1 : 0,
		};
	})();

	function changeAppearanceMode(mode){
		if(props.dispatch){
			props.dispatch({
				type: 'app/save',
				payload:{
					appearanceMode: normalizeAppearanceMode(mode),
				},
			});		
		}
	}

	function cycleAppearanceMode(){
		changeAppearanceMode(getNextAppearanceMode(props.appearanceMode));
	}

    function openDrawer(key){
		if(props.dispatch){
			props.dispatch({
				type: 'astro/openDrawer',
				payload:{ 
					key: key,
				},
			});		
		}
	}
	
	function newChart(){
		if(props.dispatch){
			props.dispatch({
				type: 'astro/nowChart',
				payload:{ },
			});		
		}
	}

	async function onAIExportClick({key}){
		try{
			const ret = await runAIExport(key);
			if(ret && ret.ok){
				message.success(ret.message);
			}else{
				message.error(ret && ret.message ? ret.message : 'AI导出失败，请重试。');
			}
		}catch(e){
			const msg = e && e.message ? e.message : 'AI导出异常';
			message.error(msg);
		}
	}

	function openAIExportSettings(){
		const settings = loadAIExportSettings();
		const techs = listAIExportTechniqueSettings();
		const current = getCurrentAIExportContext();
		let key = techs.length ? techs[0].key : 'astrochart';
		if(current && current.key){
			const found = techs.find((item)=>item.key === current.key);
			if(found){
				key = found.key;
			}
		}
		setAiSettingData(settings);
		setAiSettingTechs(techs);
		setAiSettingKey(key);
		setAiSettingVisible(true);
	}

	function onAISettingSave(){
		const saved = saveAIExportSettings(aiSettingDataRef.current);
		aiSettingDataRef.current = saved;
		setAiSettingData(saved);
		setAiSettingVisible(false);
		message.success('AI导出设置已保存');
	}

	function onAISettingOptionsChange(vals){
		const arr = Array.isArray(vals) ? vals.map((item)=>`${item}`) : [];
		setAiSettingData((prev)=>{
			const sections = {
				...(prev && prev.sections ? prev.sections : {}),
				[aiSettingKey]: arr,
			};
			const next = {
				...(prev || {}),
				version: AI_EXPORT_SETTINGS_VERSION,
				sections,
			};
			aiSettingDataRef.current = next;
			return next;
		});
	}

	function onAISettingToggleOption(item){
		const key = `${item}`;
		const selected = currentSettingSelected.indexOf(key) >= 0;
		const next = selected
			? currentSettingSelected.filter((rec)=>rec !== key)
			: currentSettingSelected.concat([key]);
		onAISettingOptionsChange(next);
	}

	function onAISettingSelectAll(){
		onAISettingOptionsChange(currentSettingOptions.slice(0));
	}

	function onAISettingClear(){
		onAISettingOptionsChange([]);
	}

	function onAISettingResetDefault(){
		setAiSettingData((prev)=>{
			const sections = {
				...(prev && prev.sections ? prev.sections : {}),
			};
			const planetInfo = {
				...(prev && prev.planetInfo ? prev.planetInfo : {}),
			};
			const astroMeaning = {
				...(prev && prev.astroMeaning ? prev.astroMeaning : {}),
			};
			delete sections[aiSettingKey];
			delete planetInfo[aiSettingKey];
			delete astroMeaning[aiSettingKey];
			const next = {
				...(prev || {}),
				version: AI_EXPORT_SETTINGS_VERSION,
				sections,
				planetInfo,
				astroMeaning,
			};
			aiSettingDataRef.current = next;
			return next;
		});
	}

	function onAISettingPlanetInfoChange(field, checked){
		setAiSettingData((prev)=>{
			const current = prev && prev.planetInfo && prev.planetInfo[aiSettingKey]
				? prev.planetInfo[aiSettingKey]
				: { showHouse: 1, showRuler: 1 };
			const nextOne = {
				showHouse: current.showHouse === 1 || current.showHouse === true ? 1 : 0,
				showRuler: current.showRuler === 1 || current.showRuler === true ? 1 : 0,
			};
			nextOne[field] = checked ? 1 : 0;
			const next = {
				...(prev || {}),
				version: AI_EXPORT_SETTINGS_VERSION,
				sections: {
					...(prev && prev.sections ? prev.sections : {}),
				},
				planetInfo: {
					...(prev && prev.planetInfo ? prev.planetInfo : {}),
					[aiSettingKey]: nextOne,
				},
				astroMeaning: {
					...(prev && prev.astroMeaning ? prev.astroMeaning : {}),
				},
			};
			aiSettingDataRef.current = next;
			return next;
		});
	}

	function onAISettingAstroMeaningChange(checked){
		setAiSettingData((prev)=>{
			const next = {
				...(prev || {}),
				version: AI_EXPORT_SETTINGS_VERSION,
				sections: {
					...(prev && prev.sections ? prev.sections : {}),
				},
				planetInfo: {
					...(prev && prev.planetInfo ? prev.planetInfo : {}),
				},
				astroMeaning: {
					...(prev && prev.astroMeaning ? prev.astroMeaning : {}),
					[aiSettingKey]: {
						enabled: checked ? 1 : 0,
					},
				},
			};
			aiSettingDataRef.current = next;
			return next;
		});
	}

	React.useEffect(()=>{
		aiSettingDataRef.current = aiSettingData;
	}, [aiSettingData]);

	React.useEffect(()=>{
		if(!aiSettingVisible){
			return;
		}
		saveAIExportSettings(aiSettingData);
	}, [aiSettingData, aiSettingVisible]);

	function hasDesktopBridge(){
		return typeof window !== 'undefined'
			&& window.horosaDesktop
			&& typeof window.horosaDesktop.exportDiagnostics === 'function';
	}

	function collectSnapshotPayload(){
		const payload = {
			url: typeof window !== 'undefined' ? window.location.href : '',
			userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
			timestamp: new Date().toISOString(),
			snapshots: {},
			localKeys: [],
		};
		if(typeof window === 'undefined' || !window.localStorage){
			return payload;
		}
		for(let i=0; i<window.localStorage.length; i++){
			const key = window.localStorage.key(i);
			if(!key){
				continue;
			}
			payload.localKeys.push(key);
			if(key.indexOf('horosa.ai.snapshot.module.v1.') === 0){
				payload.snapshots[key] = window.localStorage.getItem(key);
			}
		}
		return payload;
	}

	async function onExportDiagnosticsClick(){
		if(!hasDesktopBridge()){
			message.warning('当前不是桌面 App 环境，无法导出诊断报告。');
			return;
		}
		const ret = await window.horosaDesktop.exportDiagnostics(collectSnapshotPayload());
		if(ret && ret.ok){
			message.success(ret.message || '诊断报告导出成功');
		}else if(ret && ret.canceled){
			message.info('已取消导出诊断报告');
		}else{
			message.error((ret && ret.message) ? ret.message : '诊断报告导出失败');
		}
	}
	
	let pubmenu = [{
		key: 'chartlist',
		label: (<div><UserOutlined />&nbsp;管理命盘</div>)
	},{
		key: 'caselist',
		label: (<div><UserOutlined />&nbsp;管理事盘</div>)
	},{
		key: 'chartadd',
		label: (<div><UserOutlined />&nbsp;新增命盘</div>)
	}];

	let usermenu = [{
		key: 'chartlist',
		label: (<div><UserOutlined />&nbsp;我的星盘列表</div>)
	},{
		key: 'caselist',
		label: (<div><UserOutlined />&nbsp;管理事盘</div>)
	},{
		key: 'chartsgps',
		label: (<div><UserOutlined />&nbsp;我的星盘分布</div>)
	},{
		key: 'chartadd',
		label: (<div><UserOutlined />&nbsp;新增星盘数据</div>)
	},{
		key: 'changeparams',
		label: (<div><UserOutlined />&nbsp;星盘参数修改</div>)
	},{
		key: 'changepwd',
		label: (<div><UserOutlined />&nbsp;密码修改</div>)
	},{
		key: 'divider',
		label: (<hr />),
		disabled: true
	},{
		key: 'logout',
		label: (<div><LogoutOutlined />&nbsp;退出登录</div>)
	}];

	let menu = pubmenu;
	let username = '管理';
	if(props.userInfo){
		menu = usermenu;
		username = props.userInfo.uid;
	}

	let avatarcomp = null;
	if(props.avatar){
		avatarcomp = (<Avatar size="small" className={styles.avatar} src={props.avatar} />);
	}else{
		avatarcomp = (<Avatar size="small" className={styles.avatar} icon={<XQIcon name="user" />} />);
	}

	const appearanceMode = normalizeAppearanceMode(props.appearanceMode);
	const appearanceLabel = getAppearanceLabel(appearanceMode, props.resolvedAppearance);
	const appearanceIcon = appearanceMode === APPEARANCE_SYSTEM
		? <XQIcon name="theme" />
		: (appearanceMode === APPEARANCE_DARK ? <XQIcon name="theme" /> : <XQIcon name="theme" />);

	const horosaqr = [{
		key: '1',
		label: (<img src={blogo} alt='星阙公众号' style={{width: 200, height:200}} />)
	}];
	const aiExportMenu = [{
		key: 'all',
		label: (<div>一键复制+导出全部</div>),
	},{
		key: 'copy',
		label: (<div>复制AI纯文字</div>),
	},{
		key: 'txt',
		label: (<div>导出TXT</div>),
	},{
		key: 'word',
		label: (<div>导出Word</div>),
	},{
		key: 'pdf',
		label: (<div>导出PDF</div>),
	}];

		return (
			<div className={styles.userbox}>
				<div className={styles.brand}>
					<Dropdown menu={{items: horosaqr}} placement="bottomLeft" trigger={['click', 'hover']}>
						<button className={styles.brandButton} type="button">
							<span className={styles.brandMark}><XQIcon name="astro" /></span>
							<span className={styles.brandText}>星阙</span>
						</button>
					</Dropdown>
				</div>
				<div className={styles.commandBar}>
					<span className={styles.commandGroup}>
						<Tooltip title="导航">
							<XQButton className={styles.compactCommand} size='small' iconName="navigation" onClick={()=>{openDrawer('homepage')}}>导航</XQButton>
						</Tooltip>
						<Tooltip title="批注">
							<XQButton className={styles.compactCommand} size='small' iconName="note" onClick={()=>{openDrawer('memo')}}>批注</XQButton>
						</Tooltip>
					</span>
					<span className={styles.commandGroup}>
						<Tooltip title="小工具">
							<XQButton className={styles.compactCommand} size='small' iconName="tools" onClick={()=>{openDrawer('commtools')}}>小工具</XQButton>
						</Tooltip>
					</span>
					<span className={styles.commandGroup}>
						<XQButton className={styles.primaryCommand} variant="primary" size='small' iconName="newChart" onClick={newChart}>新命盘</XQButton>
						<Dropdown menu={{items: aiExportMenu, onClick: onAIExportClick}} placement="bottom" trigger={['click']}>
							<XQButton className={styles.compactCommand} size='small' iconName="aiExport">AI导出</XQButton>
						</Dropdown>
						<XQButton className={styles.compactCommand} size='small' iconName="aiSettings" onClick={openAIExportSettings}>AI导出设置</XQButton>
						{hasDesktopBridge() ? (
							<XQButton className={styles.compactCommand} size='small' iconName="diagnostics" onClick={onExportDiagnosticsClick}>诊断</XQButton>
						) : null}
					</span>
				</div>
				<div className={styles.utilityBar}>
					<XQInput
						className={styles.searchInput}
						size="small"
						prefix={<XQIcon name="search" />}
						placeholder="搜索功能 / 命盘 / 笔记"
						readOnly
						onClick={()=>{openDrawer('query')}}
					/>
					<Tooltip title={`主题：${appearanceLabel}。点击切换昼夜模式。`}>
						<XQButton
							size="small"
							className={styles.appearanceButton}
							icon={appearanceIcon}
							onClick={cycleAppearanceMode}
						>
							{appearanceLabel}
						</XQButton>
					</Tooltip>
					<Dropdown
						menu={{
							items: [
								{ key: APPEARANCE_SYSTEM, label: '跟随系统' },
								{ key: APPEARANCE_LIGHT, label: '昼间' },
								{ key: APPEARANCE_DARK, label: '暗夜' },
							],
							onClick: ({key})=>changeAppearanceMode(key),
						}}
						trigger={['click']}
					>
						<XQIconButton size="small" iconName="theme" />
					</Dropdown>
					<Dropdown menu={{
							items: menu,
							onClick: props.onMenuClick}}
					>
						<span className={`${styles.account}`}>
							{avatarcomp}
							<span className={styles.name}>{username}</span>
						</span>
					</Dropdown>
				</div>
			<XQModal
				title="AI导出设置"
				open={aiSettingVisible}
				onCancel={()=>setAiSettingVisible(false)}
				width={640}
				footer={(
					<XQToolbar className={styles.aiSettingFooter}>
						<XQButton size="small" onClick={()=>setAiSettingVisible(false)}>取消</XQButton>
						<XQButton size="small" variant="primary" onClick={onAISettingSave}>保存设置</XQButton>
					</XQToolbar>
				)}
			>
				<div className={styles.aiSettingModal}>
					<XQSectionTitle>选择技法</XQSectionTitle>
					<XQSelect
					size='small'
					style={{width: '100%'}}
					value={aiSettingKey}
					onChange={(val)=>setAiSettingKey(val)}
					>
						{aiSettingTechs.map((item)=>(
							<Option key={item.key} value={item.key}>{item.label}</Option>
						))}
					</XQSelect>
					<XQToolbar compact className={styles.aiSettingActions}>
						<XQButton size='small' onClick={onAISettingSelectAll}>全选</XQButton>
						<XQButton size='small' onClick={onAISettingClear}>清空</XQButton>
						<XQButton size='small' onClick={onAISettingResetDefault}>恢复默认</XQButton>
					</XQToolbar>
					<XQSectionTitle>导出分段</XQSectionTitle>
					{currentSettingOptions.length ? (
						<XQCheckList columns={2} className={styles.aiSettingChecks}>
							{currentSettingOptions.map((item)=>(
								<XQCheckItem
									key={item}
									compact
									checked={currentSettingSelected.indexOf(item) >= 0}
									onClick={()=>onAISettingToggleOption(item)}
								>
									{item}
								</XQCheckItem>
							))}
						</XQCheckList>
					) : (
						<div className={styles.aiSettingEmpty}>当前技法暂未检测到可选分段，请先在该技法完成一次排盘后再设置。</div>
					)}
					{currentSettingSupportsPlanetInfo ? (
						<div>
							<XQSectionTitle>星曜后天信息</XQSectionTitle>
							<XQCheckList columns={2}>
								<XQCheckItem
									compact
									checked={currentSettingPlanetInfo.showHouse === 1}
									onClick={()=>onAISettingPlanetInfoChange('showHouse', currentSettingPlanetInfo.showHouse !== 1)}
								>
									显示星曜宫位
								</XQCheckItem>
								<XQCheckItem
									compact
									checked={currentSettingPlanetInfo.showRuler === 1}
									onClick={()=>onAISettingPlanetInfoChange('showRuler', currentSettingPlanetInfo.showRuler !== 1)}
								>
									显示星曜主宰宫
								</XQCheckItem>
							</XQCheckList>
						</div>
					) : null}
					{currentSettingSupportsAstroMeaning ? (
						<div>
							<XQSectionTitle>{currentSettingMeaningTitle}</XQSectionTitle>
							<XQCheckItem
								compact
								checked={currentSettingAstroMeaning.enabled === 1}
								onClick={()=>onAISettingAstroMeaningChange(currentSettingAstroMeaning.enabled !== 1)}
							>
								{currentSettingMeaningCheckbox}
							</XQCheckItem>
						</div>
					) : null}
				</div>
			</XQModal>
		</div>
	);
}

export default PageHeader;
