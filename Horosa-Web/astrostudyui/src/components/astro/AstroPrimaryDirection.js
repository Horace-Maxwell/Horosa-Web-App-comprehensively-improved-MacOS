import { Component } from 'react';
import { Row, Col, Table, Input, Button, Select,  } from 'antd';
import { SearchOutlined, } from '@ant-design/icons';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import * as AstroHelper from './AstroHelper';
import { appendPlanetHouseInfoById, splitPlanetHouseInfoText, } from '../../utils/planetHouseInfo';
import { buildMeaningTipByCategory, } from './AstroMeaningData';
import { isMeaningEnabled, wrapWithMeaning, } from './AstroMeaningPopover';
import {TableOddRowBgColor} from '../../utils/constants'
import styles from '../../css/styles.less';

const Option = Select.Option;

class AstroPrimaryDirection extends Component{

	constructor(props) {
		super(props);

		this.state = {
			searchYear: '',
			pdMethodValue: props.pdMethod ? props.pdMethod : 'astroapp_alchabitius',
			pdTimeKeyValue: props.pdTimeKey ? props.pdTimeKey : 'Ptolemy',
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

		this.genDateFilterDropdownDom = this.genDateFilterDropdownDom.bind(this);
		this.genDateColFilter = this.genDateColFilter.bind(this);
			this.genStarColFilter = this.genStarColFilter.bind(this);
			this.handleSearch = this.handleSearch.bind(this);
			this.handleReset = this.handleReset.bind(this);
			this.showMeaning = this.showMeaning.bind(this);
			this.handlePdMethodChange = this.handlePdMethodChange.bind(this);
			this.handlePdTimeKeyChange = this.handlePdTimeKeyChange.bind(this);
			this.handlePdCalculate = this.handlePdCalculate.bind(this);

			this.objs = AstroConst.LIST_OBJECTS.slice(0);
			this.objs.push(AstroConst.ASC);
			this.objs.push(AstroConst.MC);

		}

	componentDidUpdate(prevProps){
		const nextMethod = this.props.pdMethod ? this.props.pdMethod : 'astroapp_alchabitius';
		const nextTimeKey = this.props.pdTimeKey ? this.props.pdTimeKey : 'Ptolemy';
		if(prevProps.pdMethod !== nextMethod || prevProps.pdTimeKey !== nextTimeKey){
			this.setState({
				pdMethodValue: nextMethod,
				pdTimeKeyValue: nextTimeKey,
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
					<SearchOutlined style={{ color: filtered ? '#1890ff' : undefined }} />
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
					icon={<SearchOutlined />}
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

	handlePdCalculate(){
		if(this.props.onPdConfigApply){
			this.props.onPdConfigApply(
				this.state.pdMethodValue,
				this.state.pdTimeKeyValue
			);
		}
	}


	convertToDataSource(pds){
		let filterKeys = new Set();
		const showPdBounds = !(this.props.showPdBounds === 0 || this.props.showPdBounds === false);
		const appliedPdMethod = this.props.pdMethod ? this.props.pdMethod : 'astroapp_alchabitius';
		const hideAntisciaRows = appliedPdMethod === 'astroapp_alchabitius';
		if(pds === undefined || pds === null){
			return {
				ds: [],
				filterKeys: filterKeys,
			};
		}
		let res = [];
		for(let i=0; i<pds.length; i++){
			let pd = pds[i];
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

			let parts = data.Promittor.split('_');
			filterKeys.add(parts[1]);
			parts = data.Significator.split('_');
			filterKeys.add(parts[1]);
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
		const appliedPdMethod = this.props.pdMethod ? this.props.pdMethod : 'astroapp_alchabitius';
		const isHorosaLegacy = appliedPdMethod === 'horosa_legacy';

		let height = this.props.height ? this.props.height : document.documentElement.clientHeight - 50;
		const controlHeight = 54;
		const controlBottom = 10;
		const tableReserve = controlHeight + controlBottom + 126;
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
		const isPdConfigDirty = (
			(this.state.pdMethodValue ? this.state.pdMethodValue : 'astroapp_alchabitius') !== (this.props.pdMethod ? this.props.pdMethod : 'astroapp_alchabitius')
			|| (this.state.pdTimeKeyValue ? this.state.pdTimeKeyValue : 'Ptolemy') !== (this.props.pdTimeKey ? this.props.pdTimeKey : 'Ptolemy')
		);
		const controlBoxStyle = {
			border: '1px solid #d9d9d9',
			borderRadius: 4,
			backgroundColor: '#fff',
			padding: '6px 10px',
			height: controlHeight,
			display: 'flex',
			alignItems: 'center',
			gap: 8,
		};
		const labelStyle = {
			whiteSpace: 'nowrap',
			color: '#333',
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
			<div className={styles.scrollbar} style={style}>
				<Row gutter={8} style={{marginBottom: controlBottom, flex: '0 0 auto'}}>
					<Col span={8}>
						<div style={controlBoxStyle}>
							<span style={labelStyle}>推运方法</span>
							<Select
								size='small'
								style={{flex: 1}}
								value={this.state.pdMethodValue ? this.state.pdMethodValue : 'astroapp_alchabitius'}
								onChange={this.handlePdMethodChange}
							>
								<Option value='horosa_legacy'>Horosa原方法</Option>
								<Option value='astroapp_alchabitius'>AstroAPP-Alchabitius</Option>
							</Select>
						</div>
					</Col>
					<Col span={6}>
						<div style={controlBoxStyle}>
							<span style={labelStyle}>度数换算</span>
							<Select
								size='small'
								style={{flex: 1}}
								value={this.state.pdTimeKeyValue ? this.state.pdTimeKeyValue : 'Ptolemy'}
								onChange={this.handlePdTimeKeyChange}
							>
								<Option value='Ptolemy'>Ptolemy</Option>
							</Select>
						</div>
					</Col>
					<Col span={10} style={{textAlign: 'right'}}>
						<Button
							type='primary'
							size='small'
							style={{minWidth: 96, marginTop: 11}}
							onClick={this.handlePdCalculate}
							disabled={!isPdConfigDirty}
						>
							计算
						</Button>
					</Col>
				</Row>
				<div style={tableWrapStyle}>
					<Table
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
