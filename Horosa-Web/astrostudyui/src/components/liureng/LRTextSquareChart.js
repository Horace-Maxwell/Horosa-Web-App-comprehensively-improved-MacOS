import * as AstroConst from '../../constants/AstroConst';
import * as LRConst from './LRConst';
import LRCommChart from './LRCommChart';
import {randomStr} from '../../utils/helper';

class LRTextSquareChart extends LRCommChart {
	constructor(option){
		super(option);
		this.cuangTitle = '';
		this.panStyleTitle = option.panStyleName || '';
		this.centerId = 'center' + randomStr(8);
	}

	set cuangName(name){
		this.cuangTitle = name || '';
		this.drawCenterPanel();
	}

	set panStyleName(name){
		this.panStyleTitle = name || '';
		this.drawCenterPanel();
	}

	draw(){
		super.draw();
		this.svg.append('rect')
			.attr('fill', 'transparent')
			.attr('x', this.x)
			.attr('y', this.y)
			.attr('width', this.width)
			.attr('height', this.height);
		this.drawHouses();
		this.drawCenterPanel();
	}

	getBoardRect(){
		const size = Math.min(this.width, this.height) * 0.92;
		return {
			x: this.x + (this.width - size) / 2,
			y: this.y + (this.height - size) / 2,
			size,
			cell: size / 4,
		};
	}

	getHouseXY(){
		const board = this.getBoardRect();
		const x = board.x;
		const y = board.y;
		const c = board.cell;
		return [
			{x:x+c*2, y:y+c*3, w:c, h:c},
			{x:x+c, y:y+c*3, w:c, h:c},
			{x:x, y:y+c*3, w:c, h:c},
			{x:x, y:y+c*2, w:c, h:c},
			{x:x, y:y+c, w:c, h:c},
			{x:x, y:y, w:c, h:c},
			{x:x+c, y:y, w:c, h:c},
			{x:x+c*2, y:y, w:c, h:c},
			{x:x+c*3, y:y, w:c, h:c},
			{x:x+c*3, y:y+c, w:c, h:c},
			{x:x+c*3, y:y+c*2, w:c, h:c},
			{x:x+c*3, y:y+c*3, w:c, h:c},
		];
	}

	drawText(group, text, x, y, opts){
		group.append('text')
			.attr('x', x)
			.attr('y', y)
			.attr('text-anchor', opts.anchor || 'middle')
			.attr('dominant-baseline', 'middle')
			.attr('fill', opts.fill)
			.attr('font-size', opts.size)
			.attr('font-weight', opts.weight || 500)
			.attr('font-family', AstroConst.NormalFont)
			.text(text || '');
	}

	drawHouse(ord, idx){
		const house = this.svg.append('g').attr('class', 'liureng-text-square-house');
		const downBranch = this.downZi[idx];
		const upBranch = this.upZi[idx];
		const jiang = this.houseTianJiang[idx];
		const cx = ord.x + ord.w / 2;
		const titleY = ord.y + ord.h * 0.23;
		const upY = ord.y + ord.h * 0.52;
		const downY = ord.y + ord.h * 0.78;
		const isTime = downBranch === this.timezi;
		const isMonth = upBranch === this.yue;
		const titleColor = 'var(--horosa-liureng-square-jiang, #d8a451)';
		const mainColor = isMonth ? 'var(--horosa-liureng-square-accent, #d8a451)' : 'var(--horosa-liureng-square-main, #f1eee7)';
		const downColor = isTime ? 'var(--horosa-liureng-square-accent, #d8a451)' : 'var(--horosa-liureng-square-muted, #9d968b)';

		if(isTime || isMonth){
			house.append('circle')
				.attr('cx', cx)
				.attr('cy', upY)
				.attr('r', Math.max(18, ord.w * 0.20))
				.attr('fill', 'var(--horosa-liureng-square-active-bg, rgba(231, 189, 117, 0.10))');
		}

		this.drawText(house, jiang, cx, titleY, {
			fill: titleColor,
			size: Math.max(15, ord.w * 0.22),
			weight: 720,
		});
		this.drawText(house, upBranch, cx, upY, {
			fill: mainColor,
			size: Math.max(22, ord.w * 0.40),
			weight: 760,
		});
		this.drawText(house, downBranch, cx, downY, {
			fill: downColor,
			size: Math.max(16, ord.w * 0.24),
			weight: 650,
		});

		this.bindHouseTooltip(house, idx);
	}

	drawHouses(){
		const houses = this.getHouseXY();
		for(let i=0; i<houses.length; i++){
			this.drawHouse(houses[i], i);
		}
	}

	drawCenterPanel(){
		if(!this.svg){
			return;
		}
		this.svg.select('#' + this.centerId).remove();
		const board = this.getBoardRect();
		const c = board.cell;
		const ord = {
			x: board.x + c,
			y: board.y + c,
			w: c * 2,
			h: c * 2,
		};
		const center = this.svg.append('g').attr('id', this.centerId).attr('class', 'liureng-text-square-center');

		const lines = [];
		if(this.nongli && this.nongli.dayGanZi){
			lines.push(`${this.nongli.dayGanZi}日`);
		}
		if(this.cuangTitle){
			lines.push(this.cuangTitle);
		}
		if(this.panStyleTitle){
			lines.push(this.panStyleTitle);
		}
		if(lines.length === 0){
			lines.push('六壬');
		}
		const lineH = Math.min(28, ord.h * 0.16);
		const startY = ord.y + ord.h / 2 - (lines.length - 1) * lineH / 2;
		lines.forEach((line, idx)=>{
			this.drawText(center, line, ord.x + ord.w / 2, startY + idx * lineH, {
				fill: idx === 1 ? 'var(--horosa-liureng-square-accent, #d8a451)' : 'var(--horosa-liureng-square-main, #f1eee7)',
				size: idx === 1 ? Math.max(15, lineH * 0.72) : Math.max(14, lineH * 0.68),
				weight: idx === 1 ? 760 : 650,
			});
		});
	}
}

export default LRTextSquareChart;
