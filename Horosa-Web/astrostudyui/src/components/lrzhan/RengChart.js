import * as d3 from 'd3';
import * as AstroConst from '../../constants/AstroConst';
import {randomStr, formatDate, positionFloatingTooltip} from '../../utils/helper';
import { drawTextH, } from '../graph/GraphHelper';
import LRCircleChart from '../liureng/LRCircleChart';
import LRChart from '../liureng/LRChart';
import LRTextSquareChart from '../liureng/LRTextSquareChart';
import KeChart from '../liureng/KeChart';
import ChuangChart from '../liureng/ChuangChart';
import * as LRConst from '../liureng/LRConst';
import { getSignZi, LRChart_Circle, LRChart_Square, TaiSui} from '../liureng/LRConst';
import { ZSList, ZhangSheng, } from '../liureng/LRZhangSheng';
import { resolveLiuRengTwelvePanStyle } from '../liureng/LRPanStyle';
import { HourZi, } from '../gua/GuaConst';

function extractBranch(value){
	if(value === undefined || value === null){
		return '';
	}
	const txt = `${value}`;
	const match = txt.match(/[子丑寅卯辰巳午未申酉戌亥]/);
	return match ? match[0] : txt;
}

function isBranch(value){
	return LRConst.ZiList.indexOf(value) >= 0;
}

class RengChart {
	constructor(options){
		this.chartId = options.id;
		this.chartObj = options.chartObj;
		this.fields = options.fields;
		this.tooltipId = options.tooltipId;
		this.nongli = options.nongli;
		this.liureng = options.liureng;
		this.runyear = options.runyear;
		this.gender = options.gender;
		this.zhangshengElem = options.zhangshengElem;
		this.guireng = options.guireng;
		this.panStyleName = options.panStyleName || '';
		this.onMetaInfoClick = options.onMetaInfoClick;
		this.chartType = options.chartType !== undefined && options.chartType !== null ? options.chartType : LRChart_Square;

		this.margin = 20;
		this.svgTopgroup = null;
		this.svg = null;

		this.bgColor = 'var(--horosa-astro-panel, #090b0e)';
		this.color = 'var(--horosa-liureng-square-line, rgba(231, 189, 117, 0.18))';
		this.fontSize = 20;

		this.rengs = [];
		this.yue = null;
		if(this.chartObj){
			for(let i=0; i<this.chartObj.objects.length; i++){
				let obj = this.chartObj.objects[i];
				if(obj.id === AstroConst.SUN){
					this.yue = getSignZi(obj.sign);
					break;
				}
			}	
		}

		this.ke = null;

	}

	set chart(chartobj){
		this.chartObj = chartobj;
		for(let i=0; i<chartobj.objects.length; i++){
			let obj = chartobj.objects[i];
			if(obj.id === AstroConst.SUN){
				this.yue = getSignZi(obj.sign);
				break;
			}
		}
	}

	draw(){
		if(this.chartObj === undefined || this.chartObj === null){
			return null;
		}
		let svgdom = document.getElementById(this.chartId); 
		if(svgdom === undefined || svgdom === null){
			return null;
		}
		let width = svgdom.clientWidth;
		let height = svgdom.clientHeight;
		if(width === 0 || height === 0){
			return null;
		}

		let realW = width - this.margin * 2;
		let realH = height - this.margin * 2;

		this.hasDrawGua = false;
		let svgid = '#' + this.chartId;
		this.svg = d3.select(svgid);
		this.svg.html('');
		this.svg.attr('stroke', this.color).attr("stroke-width", 1);
	
		this.svgTopgroup = this.svg.append('g');
		this.svgTopgroup.append('rect')
			.attr('fill', this.bgColor)
			.attr('stroke', this.color)
			.attr('x', this.margin)
			.attr('y', this.margin)
			.attr('width', realW).attr('height', realH);

			let titleH = 0;
			let metaH = Math.min(58, Math.max(46, realH * 0.10));
			let h = realH - titleH - metaH;
			let cords = [];
			cords[0] = {x: this.margin, y: this.margin+titleH, w: realW, h: h};
			cords[2] = {x: this.margin, y: this.margin+titleH+h, w: realW, h: metaH};

			this.prepareLiuRengBase(cords[0]);
			this.drawSimpleBody(cords[0]);
			this.drawGua3(cords[2]);
		}

	prepareLiuRengBase(cord){
		let w = cord.w;
		let h = cord.h;
		let x = cord.x;
		let y = cord.y;

		let opt = {
			chartObj: this.chartObj,
			fields: this.fields,
			x: x,
			y: y,
			width: w,
			height: h,
			owner: this.svgTopgroup,
			divTooltip: this.tooltipId ? d3.select(`#${this.tooltipId}`) : null,
			yue: this.yue,
			nongli: this.nongli,
			guireng: this.guireng,
			panStyleName: this.panStyleName || this.getPanStyleName(),
		};

		let chartsvg = new LRTextSquareChart(opt);
		this.rengs[0] = chartsvg;	
		this.rengs[0].genYueJiangIndex();
		this.rengs[0].genHouseTianJiang();
		const panStyleName = this.panStyleName || this.getPanStyleName();
		if(this.rengs[0] && panStyleName){
			this.rengs[0].panStyleName = panStyleName;
		}

		this.ke = this.rengs[0].getKe();

	}

	getShortJiang(name){
		const map = {
			'贵人': '贵',
			'螣蛇': '蛇',
			'朱雀': '雀',
			'六合': '合',
			'勾陈': '勾',
			'青龙': '龙',
			'天空': '空',
			'白虎': '虎',
			'太常': '常',
			'玄武': '玄',
			'太阴': '阴',
			'天后': '后',
		};
		return map[name] || `${name || ''}`.substr(0, 1);
	}

	getXunGanMap(){
		const dayGanZi = this.nongli && this.nongli.dayGanZi ? this.nongli.dayGanZi : '';
		const gan = dayGanZi.substr(0, 1);
		const zi = dayGanZi.substr(1);
		const xun = LRConst.getXun(gan, zi);
		const map = {};
		for(let i=0; i<xun.length && i<LRConst.GanList.length; i++){
			map[xun[i]] = LRConst.GanList[i];
		}
		return map;
	}

	drawSimpleText(group, text, x, y, options = {}){
		const node = group.append('text')
			.attr('x', x)
			.attr('y', y)
			.attr('text-anchor', options.anchor || 'middle')
			.attr('dominant-baseline', 'middle')
			.attr('fill', options.fill || 'var(--horosa-liureng-square-main, #f0eee7)')
			.attr('font-size', options.size || 18)
			.attr('font-weight', options.weight || 520)
			.attr('font-family', options.family || '"Songti SC", "STSong", "Noto Serif CJK SC", serif')
			.text(text || '');
		this.bindSimpleTip(node, options);
		return node;
	}

	bindSimpleTip(target, options = {}){
		if(!target || !this.rengs[0]){
			return;
		}
		if(options.houseIndex !== undefined && options.houseIndex !== null){
			this.rengs[0].bindHouseTooltip(target, options.houseIndex);
			target.style('cursor', 'help');
			return;
		}
		if(options.branch){
			this.rengs[0].bindShenTooltip(target, options.branch);
			target.style('cursor', 'help');
		}
	}

	getHouseIndexByUpBranch(branch){
		const chart = this.rengs[0];
		if(!chart || !chart.upZi){
			return -1;
		}
		return chart.upZi.indexOf(extractBranch(branch));
	}

	drawSimpleBody(cord){
		if(!this.rengs[0]){
			return;
		}
		const chart = this.rengs[0];
		const opt1 = {
			chartObj: this.chartObj,
			x: cord.x,
			y: cord.y,
			width: cord.w,
			height: cord.h,
			owner: this.svgTopgroup,
			ke: this.ke,
			nongli: this.nongli,
			guireng: this.guireng,
			liuRengChart: chart,
			divTooltip: this.tooltipId ? d3.select(`#${this.tooltipId}`) : null,
		};
		const csvg = new ChuangChart(opt1);
		csvg.genCuangs();
		this.rengs[2] = csvg;
		if(chart){
			chart.cuangName = csvg.cuangs && csvg.cuangs.name ? csvg.cuangs.name : '';
		}

		const group = this.svgTopgroup.append('g').attr('class', 'liureng-simple-body');
		const left = {
			x: cord.x + 18,
			y: cord.y + 18,
			w: cord.w * 0.44 - 24,
			h: cord.h - 36,
		};
		const right = {
			x: cord.x + cord.w * 0.45,
			y: cord.y + 18,
			w: cord.w * 0.53 - 18,
			h: cord.h - 36,
		};
		this.drawSimpleTextPan(group, left, chart);
		this.drawSimpleKeChuan(group, right, csvg);
		this.drawCirclePreviewButton(group, {
			x: cord.x + cord.w - 92,
			y: cord.y + 12,
			w: 70,
			h: 30,
		});
	}

	getSimpleHouse(chart, diBranch){
		const idx = chart && chart.downZi ? chart.downZi.indexOf(diBranch) : -1;
		if(idx < 0){
			return {
				di: diBranch,
				up: '',
				gan: '◎',
				jiang: '',
			};
		}
		const up = chart.upZi[idx] || '';
		const map = this.getXunGanMap();
		return {
			idx,
			di: diBranch,
			up,
			gan: map[up] || '◎',
			jiang: this.getShortJiang(chart.houseTianJiang[idx] || ''),
		};
	}

	drawSimpleTextPan(group, cord, chart){
		const panGroup = group.append('g').attr('class', 'liureng-simple-pan');
		const gold = 'var(--horosa-liureng-square-jiang, #d8ad63)';
		const main = 'var(--horosa-liureng-square-main, #f0eee7)';
		const muted = 'var(--horosa-liureng-square-muted, #8f9694)';
		const size = Math.min(cord.w, cord.h);
		const branchSize = Math.max(18, size * 0.088);
		const jiangSize = Math.max(16, size * 0.080);
		const ganSize = Math.max(15, size * 0.073);
		const rowGap = Math.max(branchSize * 1.35, size * 0.138);
		const colGap = Math.max(branchSize * 1.28, cord.w * 0.074);
		const centerX = cord.x + cord.w * 0.54;
		const topY = cord.y + cord.h * 0.16;
		const branches = LRConst.ZiList;
		const house = branches.reduce((acc, branch)=>{
			acc[branch] = this.getSimpleHouse(chart, branch);
			return acc;
		}, {});
		const drawRow = (list, y, field, fill, fontSize, weight)=>{
			list.forEach((branch, idx)=>{
				const data = house[branch] || {};
				const tipOptions = field === 'jiang' ? { houseIndex: data.idx } : (field === 'up' ? { branch: data.up } : {});
				this.drawSimpleText(panGroup, data[field] || '', centerX + (idx - (list.length - 1) / 2) * colGap, y, {
					fill,
					size: fontSize,
					weight,
					...tipOptions,
				});
			});
		};
		drawRow(['巳', '午', '未', '申'], topY, 'jiang', gold, jiangSize, 760);
		drawRow(['巳', '午', '未', '申'], topY + rowGap, 'gan', muted, ganSize, 560);
		drawRow(['巳', '午', '未', '申'], topY + rowGap * 2, 'up', main, branchSize, 760);

		const middleY = topY + rowGap * 3.28;
		[
			{ branch: '辰', x: centerX - colGap * 2.24, y: middleY },
			{ branch: '卯', x: centerX - colGap * 2.24, y: middleY + rowGap },
		].forEach((item)=>{
			const data = house[item.branch] || {};
			this.drawSimpleText(panGroup, data.jiang, item.x - colGap * 0.74, item.y, { fill: gold, size: jiangSize, weight: 760, houseIndex: data.idx });
			this.drawSimpleText(panGroup, data.gan, item.x, item.y, { fill: muted, size: ganSize, weight: 560 });
			this.drawSimpleText(panGroup, data.up, item.x + colGap * 0.74, item.y, { fill: main, size: branchSize, weight: 760, branch: data.up });
		});
		[
			{ branch: '酉', x: centerX + colGap * 2.24, y: middleY },
			{ branch: '戌', x: centerX + colGap * 2.24, y: middleY + rowGap },
		].forEach((item)=>{
			const data = house[item.branch] || {};
			this.drawSimpleText(panGroup, data.up, item.x - colGap * 0.74, item.y, { fill: main, size: branchSize, weight: 760, branch: data.up });
			this.drawSimpleText(panGroup, data.gan, item.x, item.y, { fill: muted, size: ganSize, weight: 560 });
			this.drawSimpleText(panGroup, data.jiang, item.x + colGap * 0.74, item.y, { fill: gold, size: jiangSize, weight: 760, houseIndex: data.idx });
		});

		const bottomY = topY + rowGap * 5.7;
		drawRow(['寅', '丑', '子', '亥'], bottomY, 'up', main, branchSize, 760);
		drawRow(['寅', '丑', '子', '亥'], bottomY + rowGap, 'gan', muted, ganSize, 560);
		drawRow(['寅', '丑', '子', '亥'], bottomY + rowGap * 2, 'jiang', gold, jiangSize, 760);
	}

	formatChuanGanZi(gz){
		const txt = `${gz || ''}`;
		if(txt.indexOf('空') === 0 && txt.length > 1){
			return `${txt.substr(1)}空`;
		}
		return txt;
	}

	parseChuanGanZi(gz){
		const txt = `${gz || ''}`;
		const branch = extractBranch(txt);
		const isKong = txt.indexOf('空') >= 0;
		if(!branch){
			return {
				gan: '',
				branch: '',
				kong: isKong ? '空' : '',
			};
		}
		const gan = isKong ? '' : txt.replace(branch, '').replace(/空/g, '').substr(0, 1);
		return {
			gan,
			branch,
			kong: isKong ? '空' : '',
		};
	}

	drawSimpleKeChuan(group, cord, csvg){
		const rightGroup = group.append('g').attr('class', 'liureng-simple-ke-chuan');
		const gold = 'var(--horosa-liureng-square-jiang, #d8ad63)';
		const main = 'var(--horosa-liureng-square-main, #f0eee7)';
		const muted = 'var(--horosa-liureng-square-muted, #8f9694)';
		const size = Math.min(cord.w, cord.h);
		const big = Math.max(19, size * 0.096);
		const small = Math.max(13, size * 0.064);
		const keOrder = [3, 2, 1, 0];
		const keX = cord.x + cord.w * 0.02;
		const keY = cord.y + cord.h * 0.26;
		const keGap = Math.max(big * 1.16, cord.h * 0.13);
		const tokenGap = big * 0.92;
		const drawKeTokenRow = (rowIdx, y)=>{
			keOrder.forEach((keIdx, tokenIdx)=>{
				const ke = this.ke[keIdx] || [];
				let text = '';
				let options = {};
				if(rowIdx === 0){
					text = this.getShortJiang(ke[0]);
					options.houseIndex = this.getHouseIndexByUpBranch(ke[1]);
				}else if(rowIdx === 1){
					text = ke[1] || '';
					options.branch = extractBranch(text);
				}else{
					text = ke[2] || '';
					const branch = extractBranch(text);
					if(branch && isBranch(branch)){
						options.branch = branch;
					}
				}
				this.drawSimpleText(rightGroup, text, keX + tokenIdx * tokenGap, y, {
					anchor: 'start',
					fill: rowIdx === 0 ? gold : (rowIdx === 1 ? main : muted),
					size: rowIdx === 0 ? big : big * 0.96,
					weight: rowIdx === 0 ? 760 : 620,
					...options,
				});
			});
		};
		[0, 1, 2].forEach((idx)=>{
			drawKeTokenRow(idx, keY + idx * keGap);
		});

		const cuangs = csvg && csvg.cuangs ? csvg.cuangs : {};
		const startX = cord.x + cord.w * 0.60;
		const startY = keY;
		const rowGap = keGap;
		const chuanGanX = startX + Math.max(big * 1.02, cord.w * 0.058);
		const chuanBranchX = startX + Math.max(big * 1.78, cord.w * 0.118);
		const chuanJiangX = startX + Math.max(big * 2.58, cord.w * 0.176);
		for(let i=0; i<3; i++){
			const y = startY + i * rowGap;
			const liuqin = cuangs.liuQin && cuangs.liuQin[i] ? `${cuangs.liuQin[i]}`.substr(0, 1) : '';
			const chuanText = cuangs.cuang && cuangs.cuang[i] ? cuangs.cuang[i] : '';
			const parsedChuan = this.parseChuanGanZi(chuanText);
			this.drawSimpleText(rightGroup, liuqin, startX, y, {
				anchor: 'start',
				fill: muted,
					size: small,
					weight: 620,
				});
			this.drawSimpleText(rightGroup, parsedChuan.gan, chuanGanX, y, {
				anchor: 'middle',
				fill: muted,
				size: big * 0.78,
				weight: 560,
			});
			this.drawSimpleText(rightGroup, parsedChuan.branch, chuanBranchX, y, {
				anchor: 'middle',
				fill: main,
				size: big,
				weight: 760,
				branch: parsedChuan.branch,
			});
			this.drawSimpleText(rightGroup, this.getShortJiang(cuangs.tianJiang && cuangs.tianJiang[i] ? cuangs.tianJiang[i] : ''), chuanJiangX, y, {
				anchor: 'start',
				fill: gold,
				size: big,
				weight: 760,
				houseIndex: this.getHouseIndexByUpBranch(chuanText),
			});
		}
	}

	drawCirclePreviewButton(group, cord){
		if(!this.tooltipId){
			return;
		}
		const button = group.append('g')
			.attr('class', 'liureng-circle-preview-button')
			.style('cursor', 'help');
		button.append('rect')
			.attr('x', cord.x)
			.attr('y', cord.y)
			.attr('width', cord.w)
			.attr('height', cord.h)
			.attr('rx', 8)
			.attr('ry', 8)
			.attr('fill', 'rgba(231, 189, 117, 0.08)')
			.attr('stroke', 'rgba(231, 189, 117, 0.42)')
			.attr('stroke-width', 1);
		button.append('text')
			.attr('x', cord.x + cord.w / 2)
			.attr('y', cord.y + cord.h / 2)
			.attr('dominant-baseline', 'middle')
			.attr('text-anchor', 'middle')
			.attr('fill', 'var(--horosa-astro-gold, #e7bd75)')
			.attr('stroke', 'none')
			.attr('font-size', 12)
			.attr('font-weight', 700)
			.text('圆形盘');
		button.on('mouseover', (evt)=>{
			this.showCirclePreviewTooltip(evt, button);
		}).on('mousemove', (evt)=>{
			const divTooltip = d3.select(`#${this.tooltipId}`);
			positionFloatingTooltip(divTooltip, evt, {
				anchorNode: button.node(),
				offsetX: 12,
				offsetY: 10,
				viewportPadding: 14,
			});
		}).on('mouseout', ()=>{
			d3.select(`#${this.tooltipId}`).transition().duration(250).style('opacity', 0);
		});
	}

	showCirclePreviewTooltip(evt, anchor){
		const divTooltip = d3.select(`#${this.tooltipId}`);
		if(!divTooltip || !divTooltip.node || !divTooltip.node()){
			return;
		}
		const svgId = 'liureng-circle-preview-' + randomStr(8);
		divTooltip
			.style('opacity', 1)
			.html(`<div class="liureng-circle-preview-tooltip"><div class="liureng-circle-preview-title">圆形盘</div><svg id="${svgId}" width="330" height="330"></svg></div>`);
		positionFloatingTooltip(divTooltip, evt, {
			anchorNode: anchor.node(),
			offsetX: 12,
			offsetY: 10,
			viewportPadding: 14,
		});
		const previewSvg = d3.select(`#${svgId}`);
		const opt = {
			chartObj: this.chartObj,
			fields: this.fields,
			x: 12,
			y: 12,
			width: 306,
			height: 306,
			owner: previewSvg,
			divTooltip: null,
			yue: this.yue,
			nongli: this.nongli,
			guireng: this.guireng,
			panStyleName: this.panStyleName || this.getPanStyleName(),
		};
		const circle = new LRCircleChart(opt);
		circle.draw();
		if(this.rengs[2] && this.rengs[2].cuangs && this.rengs[2].cuangs.name){
			circle.cuangName = this.rengs[2].cuangs.name;
		}
	}

	getPanStyleName(){
		const timeBranch = this.nongli && this.nongli.time ? extractBranch(this.nongli.time) : '';
		const panStyle = resolveLiuRengTwelvePanStyle(this.yue, timeBranch);
		return panStyle && panStyle.name ? panStyle.name : '';
	}

	drawGua2(cord){
		let w = (cord.w - this.margin*2)*4/7;
		let h = cord.h - this.margin;
		let x = cord.x + this.margin/2;
		let y = cord.y + this.margin/2;

		if(this.rengs.length === 0 || this.rengs[0] === undefined || this.rengs[0] === null){
			return;
		}

		let opt = {
			chartObj: this.chartObj,
			x: x,
			y: y,
			width: w,
			height: h,
			owner: this.svgTopgroup,
			ke: this.ke,
			nongli: this.nongli,	
			guireng: this.guireng,
			liuRengChart: this.rengs[0],
			divTooltip: this.tooltipId ? d3.select(`#${this.tooltipId}`) : null,
		};
		let kesvg = new KeChart(opt);
		this.rengs[1] = kesvg;
		this.rengs[1].draw();

		let w1 = (cord.w - this.margin*2)*3/7;
		let h1 = h;
		let x1 = cord.x + w + this.margin;
		let y1 = y;
		let opt1 = {
			chartObj: this.chartObj,
			x: x1,
			y: y1,
			width: w1,
			height: h1,
			owner: this.svgTopgroup,
			ke: this.ke,
			nongli: this.nongli,
			guireng: this.guireng,
			liuRengChart: this.rengs[0],
			divTooltip: this.tooltipId ? d3.select(`#${this.tooltipId}`) : null,
		};
		let csvg = new ChuangChart(opt1);
		this.rengs[2] = csvg;
		this.rengs[2].draw();

	}

	drawGua3(cord){
		if(this.liureng === undefined || this.liureng === null){
			return;
		}

		const items = [
			['行年', this.getRunYear()],
			['旬日', this.getXun()],
			['旺衰', this.getData(this.liureng.season)],
			['基础神煞', this.getData(this.liureng.gods)],
			['干煞', this.getData(this.liureng.godsGan)],
			['月煞', this.getData(this.liureng.godsMonth)],
			['支煞', this.getData(this.liureng.godsZi)],
			['年煞', this.getYearGods()],
			[`${this.zhangshengElem}十二长生`, this.getZhangSheng()],
		];
		const gap = 8;
		const padX = this.margin / 2;
		const x = cord.x + padX;
		const y = cord.y + 6;
		const h = Math.max(38, cord.h - 12);
		const w = (cord.w - padX * 2 - gap * (items.length - 1)) / items.length;
		items.forEach((item, idx)=>{
			this.drawMetaButton({
				x: x + idx * (w + gap),
				y,
				width: w,
				height: h,
			}, item[0], item[1], false, true);
		});
	}

	drawGua4(cord){
		let w = (cord.w - this.margin) / 3;
		let h = (cord.h - this.margin*2) / 2;
		let x = cord.x + this.margin/2;
		let y = cord.y + this.margin/2;

		if(this.liureng === undefined || this.liureng === null){
			return;
		}

		let y1 = y;
		let x1 = x + w;
		let y2 = y1;
		let x2 = x1 + w;
		this.drawMetaButton({ x, y, width: w - this.margin/2, height: h * 2 - this.margin }, '支煞', this.getData(this.liureng.godsZi), true);
		this.drawMetaButton({ x: x1, y: y1, width: w - this.margin/2, height: h * 2 - this.margin }, '年煞', this.getYearGods(), true);
		this.drawMetaButton({ x: x2, y: y2, width: w - this.margin/2, height: h * 2 - this.margin }, this.zhangshengElem + '十二长生', this.getZhangSheng(), true);
	}

	getMetaSummary(gods){
		if(!gods || gods.length === 0){
			return '点击查看';
		}
		return `${gods.length}项信息`;
	}

	drawMetaButton(cord, title, gods, tall, compact){
		if(!this.svgTopgroup){
			return;
		}
		const rows = gods || [];
		const buttonW = compact ? Math.max(72, cord.width) : Math.max(92, Math.min(cord.width - 12, tall ? 132 : 118));
		const buttonH = compact ? Math.max(36, Math.min(cord.height, 42)) : (tall ? 70 : 56);
		const x = cord.x + cord.width / 2 - buttonW / 2;
		const y = cord.y + cord.height / 2 - buttonH / 2;
		const group = this.svgTopgroup.append('g')
			.attr('class', 'liureng-meta-button')
			.style('cursor', 'pointer')
			.attr('tabindex', 0)
			.on('click', ()=>{
				if(this.onMetaInfoClick){
					this.onMetaInfoClick({
						title,
						gods: rows,
					});
				}
			});
		group.append('rect')
			.attr('x', x)
			.attr('y', y)
			.attr('width', buttonW)
			.attr('height', buttonH)
			.attr('rx', 8)
			.attr('ry', 8)
			.attr('fill', 'var(--horosa-surface-solid, #fffdfa)')
			.attr('stroke', 'var(--horosa-astro-gold, #b8893f)')
			.attr('stroke-width', 1.2);
		group.append('text')
			.attr('x', x + buttonW / 2)
			.attr('y', y + (compact ? 16 : 23))
			.attr('text-anchor', 'middle')
			.attr('fill', 'var(--horosa-astro-gold, #b8893f)')
			.attr('font-size', compact ? 12 : (tall ? 16 : 15))
			.attr('font-weight', 700)
			.text(title);
		group.append('text')
			.attr('x', x + buttonW / 2)
			.attr('y', y + (compact ? 32 : 45))
			.attr('text-anchor', 'middle')
			.attr('fill', 'var(--horosa-astro-muted, #7f7a70)')
			.attr('font-size', compact ? 9 : 11)
			.text(this.getMetaSummary(rows));
		group.append('title').text(`${title}：点击查看完整信息`);
	}

	getZhangSheng(){
		let res = ZSList.map((item, idx)=>{
			let k = this.zhangshengElem + '_' + item;
			return {
				key: item,
				value: ZhangSheng.wxphase[k],
			};
		});
		return res;
	}

	getRunYear(){
		const runyear = this.runyear || {};
		const genderText = this.gender === 0 || this.gender === '0' ? '女' : '男';
		let res = [{
			key: '行年',
			value: runyear.year ? runyear.year : '—',
		},{
			key: '年龄',
			value: runyear.age !== undefined && runyear.age !== null ? (runyear.age + '岁') : '—',
		},{
			key: '性别',
			value: genderText,
		}];
		return res;
	}

	getYearGods(){
		let res = [];
		let taisui1 = this.liureng && this.liureng.godsYear ? this.liureng.godsYear.taisui1 : null;
		for(let i=0; i<TaiSui.length; i++){
			let k = TaiSui[i];
			let god = {
				key: k,
				value: taisui1 && taisui1[k] ? taisui1[k] : '—',
			};
			res.push(god);
		}
		return res;
	}

	getXun(){
		const dunDing = this.liureng.xun['遁丁'] || extractBranch(this.liureng.xun['旬丁']);
		let xuns = [{
			key: '旬空',
			value: this.liureng.xun['旬空'],
		},{
			key: '旬首',
			value: this.liureng.xun['旬首'],
		},{
			key: '旬尾',
			value: this.liureng.xun['旬尾'],
		},{
			key: '遁丁',
			value: dunDing,
		}];

		return xuns;
	}

	getData(obj){
		let res = [];
		for(let k in obj){
			let data = {
				key: k,
				value: obj[k],
			}
			let pidx = k.indexOf('(');
			if(pidx >= 0){
				let name = k.substr(0, pidx);
				data.key = name;
			}
			if(data.value instanceof Array){
				data.value = data.value.join('');
			}
			res.push(data);
		}
		return res;
	}

	drawTitle(cord){
		let txt = '';
		if(this.liureng){
			if(this.nongli){
				txt = '真太阳时:' + this.nongli.birth;
			}
			let fourcol = this.liureng.fourColumns;
			txt = txt + '； 八字:' 
				+ fourcol.year.ganzi + '年 ' + fourcol.month.ganzi + '月 ' 
				+ fourcol.day.ganzi + '日 '+ fourcol.time.ganzi + '时';
			if(this.nongli){
				let leap = this.nongli.leap ? '闰' : '';
				txt = txt + '（' + leap + this.nongli.month + this.nongli.day + '）';
			}

		}else if(this.nongli){
			let leap = this.nongli.leap ? '闰' : '';
			txt = '真太阳时:' + this.nongli.birth + '； 农历:' 
				+ this.nongli.year + '年 ' + this.nongli.monthGanZi + '月 ' 
				+ this.nongli.dayGanZi + '日 '+ this.nongli.time + '时'
				+ '（' + leap + this.nongli.month + this.nongli.day + '）';
				
		}else{
			let dt = new Date();
			let h = dt.getHours();
			let zi = HourZi[h];
			txt = '起卦时间：' + formatDate(dt) + ' ' + zi + '时';
		}
		
		let marg = 2;
		let fontsz = 15
		let len = (txt.length-9) * fontsz;
		if(len > cord.w){
			len = cord.w;
			fontsz = cord.w / (txt.length-9);
		}
		let h = fontsz + marg*2;
		let x = cord.x + cord.w/2 - len/2;
		let y = cord.y + cord.h/2;
		let data = [txt];
		drawTextH(this.svgTopgroup, data, x, y, len, h, marg, this.color);
	}

}

export default RengChart;
