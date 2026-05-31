import * as d3 from 'd3';
import { Component } from 'react';
import { Modal } from 'antd';
import {randomStr, setupFloatingTooltip} from '../../utils/helper';
import * as AstroConst from '../../constants/AstroConst';
import RengChart from './RengChart';

class LiuRengChart extends Component{
	constructor(props) {
		super(props);
		let svgid = this.props.id ? 'svg' + this.props.id : 'svg' + randomStr(8);
		this.state = {
			chartid: svgid,
			ox: 0,
			oy: 0,
			radius: 0,
			tooltipId: 'div' + randomStr(8),
			metaDialog: null,
		};

		this.openMetaDialog = this.openMetaDialog.bind(this);
		this.closeMetaDialog = this.closeMetaDialog.bind(this);

		let opt = {
			id: svgid,
			fields: this.props.fields,
			tooltipId: this.state.tooltipId,
			chartObj: null,
			nongli: this.props.nongli,
			liureng: this.props.liureng,
			runyear: this.props.runyear,
			gender: this.props.gender,
			zhangshengElem: this.props.zhangshengElem,
			guireng: this.props.guireng,
			castOverride: this.props.castOverride,
			panStyleName: this.props.panStyleName,
			onMetaInfoClick: this.openMetaDialog,
			chartType: this.props.chartType,
			compactPreview: this.props.compactPreview,
		};
		this.rengchart = new RengChart(opt);

		this.drawChart = this.drawChart.bind(this);
		this.safeDrawChart = this.safeDrawChart.bind(this);
		this.handleResize = this.handleResize.bind(this);
		this.setupToolTip = this.setupToolTip.bind(this);
	}

	openMetaDialog(payload){
		this.setState({
			metaDialog: payload,
		});
	}

	closeMetaDialog(){
		this.setState({
			metaDialog: null,
		});
	}

	handleResize(){
		let svgdom = document.getElementById(this.state.chartid);
		if(svgdom === undefined || svgdom === null){
			return;
		}
		let w = svgdom.clientWidth;
		let h = svgdom.clientHeight;
		if(h < 560 || w < 560){
			return;
		}
	
		let orgx = w / 2;
		let orgy = h / 2;
		let delta = 30;
		let chartR = Math.min(w, h) / 2 - delta;
		this.setState({
			ox: orgx,
			oy: orgy,
			radius: chartR,
		}, this.safeDrawChart);
	}

	drawChart(){
		let chartobj = this.props.value;
		if(chartobj === undefined || chartobj === null){
			return;
		}
		
		this.rengchart.fields = this.props.fields;
		this.rengchart.chart = chartobj;
		this.rengchart.nongli = chartobj.nongli;
		this.rengchart.liureng = this.props.liureng;
		this.rengchart.runyear = this.props.runyear;
		this.rengchart.gender = this.props.gender;
		this.rengchart.zhangshengElem = this.props.zhangshengElem;
		this.rengchart.guireng = this.props.guireng;
		this.rengchart.castOverride = this.props.castOverride;
		this.rengchart.panStyleName = this.props.panStyleName || '';
		this.rengchart.onMetaInfoClick = this.openMetaDialog;
		this.rengchart.chartType = this.props.chartType;
		this.rengchart.compactPreview = !!this.props.compactPreview;

		this.rengchart.draw();
	}

	safeDrawChart(){
		try{
			this.drawChart();
		}catch(e){
			if(typeof console !== 'undefined' && console.error){
				console.error('[LiuRengChart] draw failed', e);
			}
		}
	}

	componentDidMount(){
		window.addEventListener('resize', this.handleResize)
		d3.select('body').append('div').attr('id', this.state.tooltipId);
		const tip = d3.select('#' + this.state.tooltipId);
		this.setupToolTip(tip);
		this.safeDrawChart();
	}

	componentDidUpdate(prevProps){
		if(prevProps.value !== this.props.value
			|| prevProps.liureng !== this.props.liureng
			|| prevProps.runyear !== this.props.runyear
			|| prevProps.gender !== this.props.gender
			|| prevProps.zhangshengElem !== this.props.zhangshengElem
			|| prevProps.guireng !== this.props.guireng
			|| prevProps.castOverride !== this.props.castOverride
			|| prevProps.panStyleName !== this.props.panStyleName
			|| prevProps.chartType !== this.props.chartType
			|| prevProps.compactPreview !== this.props.compactPreview){
			this.safeDrawChart();
		}
	}

	componentWillUnmount() {
		window.removeEventListener('resize', this.handleResize)
		d3.select('#' + this.state.tooltipId).remove();
	}

	setupToolTip(divTooltip){
		if(divTooltip){
			setupFloatingTooltip(divTooltip, {
				width: 'auto',
				'max-width': '560px',
				'min-width': '220px',
				'max-height': '62vh',
				'overflow-y': 'auto',
				padding: '8px 10px',
				font: '13px sans-serif',
				background: 'var(--horosa-surface-raised, #ffffff)',
				color: 'var(--horosa-text, #262626)',
				border: '1px solid var(--horosa-border, #e8e8e8)',
				'border-radius': '8px',
				'box-shadow': '0 6px 18px rgba(0,0,0,0.16)',
			});
		}
	}

	render(){
		let chartstyle = {
			width: this.props.width ? this.props.width : '100%',
			height: this.props.height ? this.props.height : '100%',
			backgroundColor: 'var(--horosa-astro-panel, #090b0e)',
		};

		if(this.props.style){
			chartstyle = this.props.style;
		}

		const metaDialog = this.state.metaDialog;
		const metaRows = metaDialog && Array.isArray(metaDialog.gods) ? metaDialog.gods : [];

		return (
			<>
				<svg id={this.state.chartid} style={chartstyle}>
				</svg>
				<Modal
					visible={!!metaDialog}
					title={metaDialog ? metaDialog.title : ''}
					footer={null}
					onCancel={this.closeMetaDialog}
					width={420}
					className="horosa-liureng-meta-modal"
					destroyOnClose
				>
					<div className="horosa-liureng-meta-list">
						{metaRows.length ? metaRows.map((item, idx)=>(
							<div className="horosa-liureng-meta-row" key={`${item.key}_${idx}`}>
								<span>{item.key}</span>
								<strong>{item.value}</strong>
							</div>
						)) : (
							<div className="horosa-liureng-meta-empty">暂无信息</div>
						)}
					</div>
				</Modal>
			</>
		)
	}
}

export default LiuRengChart;
