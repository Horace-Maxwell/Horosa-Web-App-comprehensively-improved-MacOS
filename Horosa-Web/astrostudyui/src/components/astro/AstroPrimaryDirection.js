import { Component } from 'react';
import { Row, Col } from 'antd';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import * as AstroHelper from './AstroHelper';
import { appendPlanetHouseInfoById, splitPlanetHouseInfoText, } from '../../utils/planetHouseInfo';
import { buildMeaningTipByCategory, } from './AstroMeaningData';
import { isMeaningEnabled, wrapWithMeaning, } from './AstroMeaningPopover';
import {TableOddRowBgColor} from '../../utils/constants'
import styles from '../../css/styles.less';
import { XQButton as Button, XQInput as Input, XQInputNumber as InputNumber, XQSelect as Select, XQTable as Table } from '../xq-ui';
import XQIcon from '../xq-icons';

const Option = Select.Option;
const PD_SYNC_REV = 'pd_method_sync_v8';
const DEFAULT_PD_METHOD = 'core_alchabitius';
const DEFAULT_PD_TIME_KEY = 'Ptolemy';
const DEFAULT_PD_TYPE = 0;
const CORE_PD_SUPPORTED_BASE_IDS = new Set([
	AstroConst.SUN,
	AstroConst.MOON,
	AstroConst.MERCURY,
	AstroConst.VENUS,
	AstroConst.MARS,
	AstroConst.JUPITER,
	AstroConst.SATURN,
	AstroConst.URANUS,
	AstroConst.NEPTUNE,
	AstroConst.PLUTO,
	AstroConst.NORTH_NODE,
	AstroConst.PARS_FORTUNA,
	AstroConst.ASC,
	AstroConst.MC,
]);

class AstroPrimaryDirection extends Component{

	constructor(props) {
		super(props);

		this.state = {
			searchYear: '',
			pdMethodValue: props.pdMethod ? props.pdMethod : 'core_alchabitius',
			pdTimeKeyValue: props.pdTimeKey ? props.pdTimeKey : 'Ptolemy',
			pdYearsValue: props.pdYears ? props.pdYears : 100,
		}

		this.searchInput = null;

		this.convertToDataSource = this.convertToDataSource.bind(this);
		this.convertText = this.convertText.bind(this);
		this.planetText = this.planetText.bind(this);
		this.T = this.T.bind(this);
		this.A = this.A.bind(this);
		this.C = this.C.bind(this);
		this.D = this.D.bind(this);
		this.S = this.S.bind(this);
		this.N = this.N.bind(this);
		this.baseDirectionObjectId = this.baseDirectionObjectId.bind(this);
		this.isCoreUnsupportedRow = this.isCoreUnsupportedRow.bind(this);

		this.genDateFilterDropdownDom = this.genDateFilterDropdownDom.bind(this);
		this.genDateColFilter = this.genDateColFilter.bind(this);
			this.genStarColFilter = this.genStarColFilter.bind(this);
			this.handleSearch = this.handleSearch.bind(this);
			this.handleReset = this.handleReset.bind(this);
			this.showMeaning = this.showMeaning.bind(this);
		this.handlePdMethodChange = this.handlePdMethodChange.bind(this);
		this.handlePdTimeKeyChange = this.handlePdTimeKeyChange.bind(this);
		this.handlePdCalculate = this.handlePdCalculate.bind(this);
		this.normalizePdMethod = this.normalizePdMethod.bind(this);
		this.normalizePdTimeKey = this.normalizePdTimeKey.bind(this);
		this.normalizePdType = this.normalizePdType.bind(this);
		this.getSelectedPdMethod = this.getSelectedPdMethod.bind(this);
		this.getSelectedPdTimeKey = this.getSelectedPdTimeKey.bind(this);
		this.getAppliedPdState = this.getAppliedPdState.bind(this);
		this.handlePdYearsChange = this.handlePdYearsChange.bind(this);
		this.normalizePdYears = this.normalizePdYears.bind(this);
		this.getSelectedPdYears = this.getSelectedPdYears.bind(this);

			this.objs = AstroConst.LIST_OBJECTS.slice(0);
			this.objs.push(AstroConst.ASC);
			this.objs.push(AstroConst.MC);

		}

	componentDidUpdate(prevProps){
		// 仅当 props 真正变化时才从 props 同步本地 state（镜像 AstroPrimaryDirectionChart 的口径）。
		// 旧逻辑「state≠normalize(props) 就 setState」会把用户对 度数换算/推运方法 的本地改选（如选 Naibod）
		// 立刻反弹回全局旧值，导致表格上方的选项形同只读。改为 prevProps 守卫后：props 稳定→不同步（本地改选保留），
		// 用户点「计算」经 onPdConfigApply 落全局后 props 才变、再同步。仍比旧 state-diff 守卫更严格，绝不重新引入
		// 「旧存盘 pdMethod 规范化≠原 prop → 无限 setState 白屏」（内层 state-diff 守卫亦保留作双保险）。
		if(prevProps.pdMethod === this.props.pdMethod
			&& prevProps.pdTimeKey === this.props.pdTimeKey
			&& prevProps.pdYears === this.props.pdYears){
			return;
		}
		const nextMethod = this.normalizePdMethod(this.props.pdMethod);
		const nextTimeKey = this.normalizePdTimeKey(this.props.pdTimeKey);
		const nextYears = this.normalizePdYears(this.props.pdYears);
		if(this.state.pdMethodValue !== nextMethod || this.state.pdTimeKeyValue !== nextTimeKey || this.state.pdYearsValue !== nextYears){
			this.setState({
				pdMethodValue: nextMethod,
				pdTimeKeyValue: nextTimeKey,
				pdYearsValue: nextYears,
			});
		}
	}

	showMeaning(){
		return isMeaningEnabled(this.props.showAstroMeaning);
	}

	planetText(id){
		const base = AstroText.AstroMsg[id] ? AstroText.AstroMsg[id] : `${id || ''}`;
		const text = appendPlanetHouseInfoById(
			base,
			this.props.value,
			id,
			this.props.showPlanetHouseInfo
		);
		const one = splitPlanetHouseInfoText(text);
		const labelNode = (
			<span>
				<span style={{fontFamily: AstroConst.AstroFont}}>{one.label}</span>
				{one.info ? <span style={{fontFamily: AstroConst.NormalFont}}>{`(${one.info})`}</span> : null}
			</span>
		);
		return wrapWithMeaning(labelNode, this.showMeaning(), buildMeaningTipByCategory('planet', id));
	}

	isBoundRow(pd){
		if(!pd || !pd.length){
			return false;
		}
		const promittor = pd[1] ? `${pd[1]}` : '';
		const significator = pd[2] ? `${pd[2]}` : '';
		return promittor.indexOf('T_') === 0 || significator.indexOf('T_') === 0;
	}

	isAntisciaRow(pd){
		if(!pd || !pd.length){
			return false;
		}
		const promittor = pd[1] ? `${pd[1]}` : '';
		const significator = pd[2] ? `${pd[2]}` : '';
		return (
			promittor.indexOf('A_') === 0 || promittor.indexOf('C_') === 0 ||
			significator.indexOf('A_') === 0 || significator.indexOf('C_') === 0
		);
	}

	baseDirectionObjectId(text){
		const parts = `${text || ''}`.split('_');
		if(parts.length < 3){
			return `${text || ''}`;
		}
		return parts.slice(1, parts.length - 1).join('_').trim();
	}

	isCoreUnsupportedRow(pd){
		if(!pd || !pd.length){
			return false;
		}
		if(this.isBoundRow(pd)){
			return true;
		}
		const promBase = this.baseDirectionObjectId(pd[1]);
		const sigBase = this.baseDirectionObjectId(pd[2]);
		return !CORE_PD_SUPPORTED_BASE_IDS.has(promBase) || !CORE_PD_SUPPORTED_BASE_IDS.has(sigBase);
	}

	genStarColFilter(dataIndex, filterKeys){
		let filters = [];

		for(let i=0; i<this.objs.length; i++){
			let planet = this.objs[i];
			if(!filterKeys.has(planet)){
				continue;
			}
			let obj = {
				text: this.planetText(planet),
				value: planet,
			}
			filters.push(obj);
		}

		let res = {
			filters: filters,
			onFilter: (value, record)=>{
				if(record[dataIndex]){
					return record[dataIndex].indexOf(value) >= 0;
				}
				return false;
			},

		};
		return res;
	}

	genDateColFilter(dataIndex){
		let res = {
			filterDropdown: (option)=>{
				return this.genDateFilterDropdownDom(option)
			},
			onFilterDropdownVisibleChange: (visible)=>{
				if(visible && this.searchInput){
					setTimeout(()=>{ this.searchInput.select()});
				}
			},
			filterIcon: (filtered)=>{
				let dom = (
					<XQIcon name="search" style={{ color: filtered ? 'var(--horosa-accent, #e7bd75)' : undefined }} />
				);
				return dom;
			},
			onFilter: (value, record)=>{
				if(record[dataIndex]){
					let txt = record[dataIndex].toString().toLowerCase();
					return txt.includes(value.toLowerCase());	
				}
				return false;
			},
		};

		return res;
	}

	genDateFilterDropdownDom(option){
		let { setSelectedKeys, selectedKeys, confirm, clearFilters } = option;
		let dom = (
			<div style={{ padding: 8 }}>
				<Input
					ref={node => {
						this.searchInput = node;
					}}
					placeholder={`输入年份`}
					value={selectedKeys[0]}
					onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
					onPressEnter={() => this.handleSearch(selectedKeys, confirm)}
					style={{ width: 188, marginBottom: 8, display: 'block' }}
				/>
				<Button
					type="primary"
					onClick={() => this.handleSearch(selectedKeys, confirm)}
					icon={<XQIcon name="search" />}
					size="small"
					style={{ width: 90, marginRight: 8 }}
				>
					搜索
				</Button>
				<Button onClick={() => this.handleReset(clearFilters)} size="small" style={{ width: 90 }}>
					重置
				</Button>
			</div>
		);

		return dom;
	}

	handleSearch(selectedKeys, confirm){
		confirm();
		this.setState({ searchYear: selectedKeys[0] });	
	}

	handleReset(clearFilters){
		clearFilters();
    	this.setState({ searchYear: '' });
	}

	handlePdMethodChange(value){
		this.setState({
			pdMethodValue: value,
		});
	}

	handlePdTimeKeyChange(value){
		this.setState({
			pdTimeKeyValue: value,
		});
	}

	handlePdYearsChange(value){
		this.setState({
			pdYearsValue: this.normalizePdYears(value),
		});
	}

	handlePdCalculate(){
		if(!this.needsPdRecompute()){
			return;
		}
		if(this.props.onPdConfigApply){
			this.props.onPdConfigApply(
				this.state.pdMethodValue,
				this.state.pdTimeKeyValue,
				this.getSelectedPdYears()
			);
		}
	}

	normalizePdMethod(value){
		if(value === 'horosa_legacy' || value === 'core_alchabitius'){
			return value;
		}
		return DEFAULT_PD_METHOD;
	}

	normalizePdTimeKey(value){
		if(value === 'Ptolemy' || value === 'Naibod'){
			return value;
		}
		return DEFAULT_PD_TIME_KEY;
	}

	normalizePdType(value){
		const num = Number(value);
		if(Number.isNaN(num)){
			return DEFAULT_PD_TYPE;
		}
		return num;
	}

	getSelectedPdMethod(){
		return this.normalizePdMethod(this.state.pdMethodValue);
	}

	getSelectedPdTimeKey(){
		return this.normalizePdTimeKey(this.state.pdTimeKeyValue);
	}

	normalizePdYears(value){
		const n = Math.round(Number(value));
		if(!Number.isFinite(n)){
			return 100;
		}
		return Math.max(1, Math.min(180, n));
	}

	getSelectedPdYears(){
		return this.normalizePdYears(this.state.pdYearsValue);
	}

	getAppliedPdState(){
		const chart = this.props.value ? this.props.value : {};
		const params = chart && chart.params ? chart.params : {};
		const hasMethod = params.pdMethod !== undefined && params.pdMethod !== null && `${params.pdMethod}` !== '';
		const hasTimeKey = params.pdTimeKey !== undefined && params.pdTimeKey !== null && `${params.pdTimeKey}` !== '';
		const hasPdType = params.pdtype !== undefined && params.pdtype !== null && `${params.pdtype}` !== '';
		const syncRev = params.pdSyncRev ? `${params.pdSyncRev}` : '';
		const hasCompleteParams = hasMethod && hasTimeKey && hasPdType && syncRev === PD_SYNC_REV;
		return {
			hasCompleteParams,
			pdMethod: this.normalizePdMethod(hasMethod ? params.pdMethod : this.props.pdMethod),
			pdTimeKey: this.normalizePdTimeKey(hasTimeKey ? params.pdTimeKey : this.props.pdTimeKey),
			pdtype: this.normalizePdType(hasPdType ? params.pdtype : DEFAULT_PD_TYPE),
			pdYears: this.normalizePdYears(params.pdYears !== undefined && params.pdYears !== null ? params.pdYears : this.props.pdYears),
			syncRev,
		};
	}

	needsPdRecompute(){
		let chart = this.props.value ? this.props.value : {};
		let predictives = chart.predictives ? chart.predictives : {};
		let pds = predictives.primaryDirection ? predictives.primaryDirection : [];
		const appliedPdState = this.getAppliedPdState();
		const selectedPdMethod = this.getSelectedPdMethod();
		const selectedPdTimeKey = this.getSelectedPdTimeKey();
		const appliedPdMethod = appliedPdState.pdMethod;
		const appliedPdTimeKey = appliedPdState.pdTimeKey;
		if(selectedPdMethod !== appliedPdMethod || selectedPdTimeKey !== appliedPdTimeKey){
			return true;
		}
		if(this.getSelectedPdYears() !== appliedPdState.pdYears){
			return true;
		}
		if(!appliedPdState.hasCompleteParams){
			return true;
		}
		if(appliedPdState.pdtype !== DEFAULT_PD_TYPE){
			return true;
		}
		return !(Array.isArray(pds) && pds.length > 0);
	}


	convertToDataSource(pds){
		let filterKeys = new Set();
		const showPdBounds = !(this.props.showPdBounds === 0 || this.props.showPdBounds === false);
		const appliedPdMethod = this.props.pdMethod ? this.props.pdMethod : 'core_alchabitius';
		const hideAntisciaRows = appliedPdMethod === 'core_alchabitius';
		const hideUnsupportedCoreRows = appliedPdMethod === 'core_alchabitius';
		if(pds === undefined || pds === null){
			return {
				ds: [],
				filterKeys: filterKeys,
			};
		}
		let res = [];
		for(let i=0; i<pds.length; i++){
			let pd = pds[i];
			if(hideUnsupportedCoreRows && this.isCoreUnsupportedRow(pd)){
				continue;
			}
			if(!showPdBounds && this.isBoundRow(pd)){
				continue;
			}
			if(hideAntisciaRows && this.isAntisciaRow(pd)){
				continue;
			}

			let data = {
				Seq: i,
				Degree: pd[0],
				Promittor: pd[1],
				Significator: pd[2],
				Date: pd[4],
			}
			res.push(data);

			const promBase = this.baseDirectionObjectId(data.Promittor);
			const sigBase = this.baseDirectionObjectId(data.Significator);
			if(promBase){
				filterKeys.add(promBase);
			}
			if(sigBase){
				filterKeys.add(sigBase);
			}
		}
		return {
			ds: res,
			filterKeys: filterKeys
		};
	}

	T(parts){
		let dom = (
			<div>
				{this.planetText(parts[2])}&nbsp;的&nbsp;
				{this.planetText(parts[1])}&nbsp;界
			</div>
		);
		return dom;
	}

	A(parts){
		let dom = (
			<div>
				{this.planetText(parts[1])}&nbsp;的映点
			</div>
		);
		return dom;
	}
	C(parts){
		let dom = (
			<div>
				{this.planetText(parts[1])}&nbsp;的反映点
			</div>
		);
		return dom;
	}

	D(parts){
		let dom = (
			<div>
				{this.planetText(parts[1])}&nbsp;的&nbsp;
				<span style={{fontFamily: AstroConst.NormalFont}}>{parts[2]}</span>&nbsp;度右相位处
			</div>
		);
		return dom;
	}
	S(parts){
		let dom = (
			<div>
				{this.planetText(parts[1])}&nbsp;的&nbsp;
				<span style={{fontFamily: AstroConst.NormalFont}}>{parts[2]}</span>&nbsp;度左相位处
			</div>
		);
		return dom;
	}
	N(parts){
		let dom = (
			<div>
				{this.planetText(parts[1])}&nbsp;
			</div>
		);
		if(parts[2] !== '0'){
			dom = (
				<div>
					{this.planetText(parts[1])}&nbsp;的&nbsp;
					<span style={{fontFamily: AstroConst.NormalFont}}>{parts[2]}</span>&nbsp;度相位处
				</div>
			); 
		}
		return dom;
	}

	convertText(text){
		let parts = text.split('_');
		let txt = text;
		if(parts[0] === 'T'){
			txt = this.T(parts);
		}else if(parts[0] === 'A'){
			txt = this.A(parts);
		}else if(parts[0] === 'C'){
			txt = this.C(parts);
		}else if(parts[0] === 'D'){
			txt = this.D(parts);
		}else if(parts[0] === 'S'){
			txt = this.S(parts);
		}else if(parts[0] === 'N'){
			txt = this.N(parts);
		}
		return txt;
	}

	render(){
		let chart = this.props.value ? this.props.value : {};
		let predictives = chart.predictives ? chart.predictives : {};
		let pds = predictives.primaryDirection ? predictives.primaryDirection : [];
		const appliedPdMethod = this.props.pdMethod ? this.props.pdMethod : 'core_alchabitius';
		const isHorosaLegacy = appliedPdMethod === 'horosa_legacy';
		const viewportWidth = typeof document !== 'undefined' && document.documentElement
			? document.documentElement.clientWidth
			: 1440;
		const compactControls = viewportWidth < 1280;
		const stackedControls = viewportWidth < 920;

		let height = this.props.height ? this.props.height : document.documentElement.clientHeight - 50;
		const controlHeight = stackedControls ? 110 : (compactControls ? 82 : 54);
		const controlBottom = 10;
		const bottomSafeReserve = 18;
		const tableReserve = controlHeight + controlBottom + 60 + bottomSafeReserve;
		let tblY = height - tableReserve;
		if(tblY < 200){
			tblY = 200;
		}

		let style = {
			height: height,
			overflow: 'hidden',
			display: 'flex',
			flexDirection: 'column',
		};
		let tableWrapStyle = {
			flex: '1 1 auto',
			minHeight: 0,
		};

		let dsres = this.convertToDataSource(pds);
		let ds = dsres.ds;
		let filterKeys = dsres.filterKeys;
		const appliedPdState = this.getAppliedPdState();
		const appliedPdTimeKey = appliedPdState.pdTimeKey;
		const tableKey = `${chart.chartId ? chart.chartId : 'pd'}:${appliedPdMethod}:${appliedPdTimeKey}:${this.props.showPdBounds === 0 || this.props.showPdBounds === false ? 0 : 1}:${appliedPdState.syncRev || 'nosync'}`;
		const pdTypeOutOfSync = appliedPdState.pdtype !== DEFAULT_PD_TYPE;
		const isPdConfigDirty = (
			this.getSelectedPdMethod() !== appliedPdState.pdMethod
			|| this.getSelectedPdTimeKey() !== appliedPdState.pdTimeKey
			|| this.getSelectedPdYears() !== appliedPdState.pdYears
			|| pdTypeOutOfSync
			|| !appliedPdState.hasCompleteParams
		);
		const needsPdRecompute = this.needsPdRecompute();
		const controlBoxStyle = {
			border: '1px solid var(--horosa-border, #d9d9d9)',
			borderRadius: 4,
			backgroundColor: 'var(--horosa-panel-bg, #fff)',
			padding: compactControls ? '8px 10px' : '6px 10px',
			minHeight: stackedControls ? 48 : 40,
			display: 'flex',
			alignItems: 'center',
			flexWrap: compactControls ? 'wrap' : 'nowrap',
			gap: 8,
			height: '100%',
		};
		const labelStyle = {
			whiteSpace: 'nowrap',
			color: 'var(--horosa-text, #333)',
			flex: '0 0 auto',
		};
		const selectStyle = {
			flex: '1 1 180px',
			minWidth: stackedControls ? '100%' : 0,
		};
		const buttonWrapStyle = {
			height: '100%',
			display: 'flex',
			alignItems: stackedControls ? 'stretch' : 'center',
			justifyContent: stackedControls ? 'stretch' : 'flex-end',
		};
		const buttonStyle = {
			minWidth: 96,
			width: stackedControls ? '100%' : 'auto',
			height: compactControls ? 36 : 32,
		};
		
		let columns = [{
			title: isHorosaLegacy ? '赤经' : 'Arc',
			dataIndex: 'Degree',
			key: 'Degree',
			width: '25%',
			render: (text, record)=>{
				if(isHorosaLegacy){
					let deg = AstroHelper.splitDegree(text);
					return deg[0] + '度' + deg[1] + '分';
				}
				const num = Number(text);
				if(!Number.isNaN(num)){
					const sign = num < 0 ? '-' : '';
					const abs = Math.abs(num);
					let deg = Math.floor(abs);
					let min = Math.round((abs - deg) * 60);
					if(min >= 60){
						deg += 1;
						min = 0;
					}
					return `${sign}${deg}度${min}分`;
				}
				let deg = AstroHelper.splitDegree(text);
				return deg[0] + '度' + deg[1] + '分';
			},
		},{
			title: '迫星',
			dataIndex: 'Promittor',
			key: 'Promittor',
			width: '25%',
			render: (text, record)=>{
				return this.convertText(text);
			},
			...this.genStarColFilter('Promittor', filterKeys)
		},{
			title: '应星',
			dataIndex: 'Significator',
			key: 'Significator',
			width: '25%',
			render: (text, record)=>{
				return this.convertText(text);
			},
			...this.genStarColFilter('Significator', filterKeys)
		},{
			title: '日期',
			dataIndex: 'Date',
			key: 'Date',
			width: '25%',
			render: (text, record)=>{
				return text;
			},
			...this.genDateColFilter('Date')
		}];


		
		return (
			<div className={`${styles.scrollbar} horosa-primary-direction-page`} style={style}>
				<Row className='horosa-primary-direction-toolbar' gutter={[8, 8]} style={{marginBottom: controlBottom, flex: '0 0 auto'}}>
					<Col xs={24} md={12} lg={7}>
						<div style={controlBoxStyle}>
							<span style={labelStyle}>推运方法</span>
							<Select
								size='small'
								style={selectStyle}
								value={this.getSelectedPdMethod()}
								onChange={this.handlePdMethodChange}
							>
								<Option value='horosa_legacy'>Horosa原方法</Option>
								<Option value='core_alchabitius'>Alchabitius</Option>
							</Select>
						</div>
					</Col>
					<Col xs={24} sm={12} md={8} lg={5}>
						<div style={controlBoxStyle}>
							<span style={labelStyle}>度数换算</span>
							<Select
								size='small'
								style={selectStyle}
								value={this.getSelectedPdTimeKey()}
								onChange={this.handlePdTimeKeyChange}
							>
								<Option value='Ptolemy'>Ptolemy</Option>
								<Option value='Naibod'>Naibod</Option>
							</Select>
						</div>
					</Col>
					<Col xs={24} sm={12} md={8} lg={5}>
						<div style={controlBoxStyle}>
							<span style={labelStyle}>推运年数</span>
							<InputNumber
								size='small'
								min={1}
								max={180}
								step={1}
								precision={0}
								style={selectStyle}
								value={this.getSelectedPdYears()}
								onChange={this.handlePdYearsChange}
							/>
						</div>
					</Col>
					<Col xs={24} sm={12} md={4} lg={7} style={buttonWrapStyle}>
						<Button
							type='primary'
							size='small'
							style={buttonStyle}
							onClick={this.handlePdCalculate}
							disabled={!needsPdRecompute}
						>
							{needsPdRecompute ? (isPdConfigDirty ? '重新计算' : '计算') : '已同步'}
						</Button>
					</Col>
				</Row>
				<div style={tableWrapStyle}>
					<Table
						className='horosa-primary-direction-table'
						key={tableKey}
						dataSource={ds} columns={columns} 
						rowKey='Seq'  
						pagination={{pageSize: 50}}
						bordered size='small'
						scroll={{x: '100%', y: tblY }}
						onRow={(record, index)=>{
							let rowstyle = {};
							if(index % 2 === 1){
								rowstyle = {
									style: { backgroundColor: TableOddRowBgColor, },
								};
							}
							return {
								...rowstyle,
							}
						}}
					/>		
				</div>
			</div>
		);
	}
}

export default AstroPrimaryDirection;
