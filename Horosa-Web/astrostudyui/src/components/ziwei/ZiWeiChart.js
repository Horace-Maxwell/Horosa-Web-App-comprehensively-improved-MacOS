import * as d3 from 'd3';
import { Component } from 'react';
import {randomStr, setupFloatingTooltip} from '../../utils/helper';
import * as AstroConst from '../../constants/AstroConst';
import ZWChart from './ZWChart';
import DateTime from '../comp/DateTime';

class ZiWeiChart extends Component{
	constructor(props) {
		super(props);
		let svgid = this.props.id ? 'svg' + this.props.id : 'svg' + randomStr(8);
		this.state = {
			chartid: svgid,
			ox: 0,
			oy: 0,
			radius: 0,
			tooltipId: 'div' + randomStr(8),
		};

		this.zwchart = new ZWChart(svgid, null, this.props.fields, this.state.tooltipId, this.props.onTipClick, this.props.onCenterInfoClick);

		this.drawChart = this.drawChart.bind(this);
		this.handleResize = this.handleResize.bind(this);
		this.scheduleDrawChart = this.scheduleDrawChart.bind(this);
		this.setupToolTip = this.setupToolTip.bind(this);
		this.drawFrame = null;
		this.resizeObserver = null;

		if(this.props.indicate){
			this.props.indicate(this.zwchart.zwindicator);
		}
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
	
		this.scheduleDrawChart();
	}

	scheduleDrawChart(){
		if(this.drawFrame){
			cancelAnimationFrame(this.drawFrame);
		}
		this.drawFrame = requestAnimationFrame(()=>{
			this.drawFrame = requestAnimationFrame(()=>{
				this.drawFrame = null;
				this.drawChart();
			});
		});
	}

	drawChart(){
		let chartobj = this.props.value;
		if(chartobj === undefined || chartobj === null 
			|| chartobj.houses === undefined || chartobj.houses === null){
			return;
		}
		
		this.zwchart.fileds = this.props.fields;
		this.zwchart.fields = this.props.fields;
		this.zwchart.onCenterInfoClick = this.props.onCenterInfoClick;
		this.zwchart.chart = chartobj;
		if(this.props.dirIndex !== undefined && this.props.dirIndex !== null){
			this.zwchart.dirHouseIndex = this.props.dirIndex;
		}else{
			let now = new DateTime();
			let y = now.format('YYYY');
			let year = parseInt(y);
			let birth = parseInt(chartobj.birth.substr(0,4));
			let age = year - birth;
			for(let i = 0; i<12; i++){
				let house = chartobj.houses[i];
				if(house.direction[0]<= age && age<=house.direction[1]){
					this.zwchart.dirHouseIndex = i;
					break;
				}
			}
		}

		this.zwchart.draw();
	}

	setupToolTip(divTooltip){
		if(divTooltip){
			setupFloatingTooltip(divTooltip, {
				width: '460px',
				padding: '8px 10px',
				font: '13px sans-serif',
				background: 'var(--horosa-surface-raised, lightsteelblue)',
				color: 'var(--horosa-text, #182235)',
				border: '1px solid var(--horosa-border, transparent)',
				'border-radius': '8px',
				'box-shadow': '0 10px 28px rgba(0,0,0,0.18)',
			});
		}
	}

	componentDidMount(){
		window.addEventListener('resize', this.handleResize);
		d3.select('body').append('div').attr('id', this.state.tooltipId);
		let divtip = d3.select('#' + this.state.tooltipId);
		this.setupToolTip(divtip);
		const svgdom = document.getElementById(this.state.chartid);
		if(svgdom && typeof ResizeObserver !== 'undefined'){
			this.resizeObserver = new ResizeObserver(()=>{
				this.scheduleDrawChart();
			});
			this.resizeObserver.observe(svgdom);
			if(svgdom.parentElement){
				this.resizeObserver.observe(svgdom.parentElement);
			}
		}
		this.scheduleDrawChart();
	}

	componentDidUpdate(){
		this.scheduleDrawChart();
	}

	componentWillUnmount() {
		window.removeEventListener('resize', this.handleResize);
		if(this.drawFrame){
			cancelAnimationFrame(this.drawFrame);
			this.drawFrame = null;
		}
		if(this.resizeObserver){
			this.resizeObserver.disconnect();
			this.resizeObserver = null;
		}
		d3.select('#' + this.state.tooltipId).remove();
	}

	render(){
		let chartstyle = {
			width: this.props.width ? this.props.width : '100%',
			height: this.props.height ? this.props.height : '100%',
			backgroundColor: AstroConst.AstroColor.ChartBackgroud,
		};

		if(this.props.style){
			chartstyle = this.props.style;
		}

		this.zwchart.rules = this.props.rules;

		return (
			<svg id={this.state.chartid} style={chartstyle}>
			</svg>
		)
	}
}

export default ZiWeiChart;
