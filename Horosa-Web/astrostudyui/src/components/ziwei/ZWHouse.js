import * as d3 from 'd3';
import * as AstroConst from '../../constants/AstroConst';
import * as ZWCont from '../../constants/ZWConst';
import * as ZiWeiHelper from './ZiWeiHelper';
import * as GraphHelper from '../graph/GraphHelper';
import ZWCommHouse from './ZWCommHouse';
import D3Arrow from '../graph/D3Arrow';
import {randomStr,} from '../../utils/helper';

class ZWHouse extends ZWCommHouse {
	constructor(option){
		super(option);
	}

	bindClick(){
		if(this.svg === undefined || this.svg === null){
			return;
		}
		this.svg.on('click', ()=>{ this.clickHouse(); });
	}

	clickHouse(){
		if(this.zwchart && this.zwchart.clickHouse){
			this.zwchart.clickHouse(this.houseObj);
		}
	}

	draw(){
		if(this.flyGanzi && this.flyGanzi === this.houseObj.ganzi){
			this.houseBG = ZWCont.ZWColor.SelectedBG;
		}
		this.owner.select('#' + this.id).remove();
		let container = this.owner.append('g').attr('id', this.id);
		container.append('rect')
				.attr('fill', this.houseBG)
				.attr('stroke', ZWCont.ZWColor.HouseLineStroke)
				.attr('x', this.x).attr('y', this.y)
				.attr('width', this.width).attr('height', this.height);
		this.svg = container;
		this.bindClick();

		if(ZWCont.ZWChart.chart === ZWCont.ZWChart_FeiXing){
			this.drawFeixing();
		}else if(ZWCont.ZWChart.chart === ZWCont.ZWChart_SangHe){
			this.drawSanghe();
		}else if(ZWCont.ZWChart.chart === ZWCont.ZWChart_SiHua){
			this.drawSihua();
		}

		this.drawLaiYing();
	}

	drawSihuaTitle(){
		let h = this.height / 4;
		let w = this.width / 4;
		let x = this.x;
		let y = this.y + this.height * 3 / 4;

		let container = this.svg.append('g');
		container.append('rect')
				.attr('fill', this.houseBG)
				.attr('stroke', ZWCont.ZWColor.HouseLineStroke)
				.attr('x', x).attr('y', y)
				.attr('width', w).attr('height', h);
		this.drawKinastroCornerMark(container, x, y, w, h);
		let data = [];
		let gzsvg = container.append('g');
		let gztip = ZWCont.NaYin[this.houseObj.ganzi];
		if(gztip){
			let tipobj = {
				title: this.houseObj.ganzi,
				tips: '纳音五行：' + gztip,
			};
			this.genTooltip(gzsvg, tipobj, this.houseObj.name)
		}

		let dirX = x + w;
		let dirY = y;
		let dirW = this.width / 2;
		let dirH = h;
		container.append('rect')
				.attr('fill', this.houseBG)
				.attr('stroke', ZWCont.ZWColor.HouseLineStroke)
				.attr('x', dirX).attr('y', dirY)
				.attr('width', dirW).attr('height', dirH);
		if(this.dirname !== undefined && this.dirname !== null && this.dirname.length){
			let dirData = [];
			dirData[0] = '运';
			dirData[1] = this.dirname.substr(0, 1);
			if(dirData[1] == '交' ){
				dirData[1] = '友';
			}
			GraphHelper.drawTextH(container.append('g'), dirData, dirX, dirY, dirW, dirH / 2, this.margin, ZWCont.ZWColor.HouseBranchStroke, 240);
		}

		if(this.yearText){
			let parts = this.yearText.split('年');
			let ageparts = parts[1].split('岁');
			let ydata = [];
			ydata[0] = parts[0].substr(0, 2);
			ydata[1] = parts[0].substr(2, 2);
			ydata[2] = '年';
			ydata[3] = ageparts[0];
			ydata[4] = '岁';
			let yearH = 12;
			let yearW = yearH * ydata.length;
			let yearX = this.x + (this.width - yearW) / 2;
			GraphHelper.drawTextH(container.append('g'), ydata, yearX, dirY-yearH - 0.5*yearH, yearW, yearH, 1, ZWCont.ZWColor.HouseAgeStroke);
		}

		let dirSubX1 = dirX;
		let dirSubY1 = dirY + dirH / 2;
		let dirSubX2 = dirX + dirW;
		let dirSubY2 = dirSubY1;
		container.append('line')
				.attr('x1', dirSubX1)
				.attr('y1', dirSubY1)
				.attr('x2', dirSubX2)
				.attr('y2', dirSubY2)
				.attr('stroke', ZWCont.ZWColor.HouseLineStroke);

		let dirData = [];
		dirData[0] = this.houseObj.direction[0] + '';
		dirData[1] = '~';
		dirData[2] = this.houseObj.direction[1] + '';
		GraphHelper.drawTextH(container.append('g'), dirData, dirSubX1, dirSubY2, dirW, dirH / 2, this.margin, ZWCont.ZWColor.HouseAgeStroke, 140);

		let titleX = dirX + dirW;
		let titleY = y;
		let titleW = this.width - w - dirW;
		let titleH = h;
		container.append('rect')
				.attr('fill', this.houseBG)
				.attr('stroke', ZWCont.ZWColor.HouseLineStroke)
				.attr('x', titleX).attr('y', titleY)
				.attr('width', titleW).attr('height', titleH);
		let housesvg = this.drawHouseTitleText(container.append('g'), {
			x: titleX,
			y: titleY,
			w: titleW,
			h: titleH,
		});
		let tip = this.ZWRules.RuleHouses[this.houseObj.name];
		if(tip){
			let tipobj = {
				title: this.houseObj.name,
				tips: tip,
			};
			this.genTooltip(housesvg, tipobj, this.houseObj.name)
		}
		
	}

	drawKinastroCornerMark(group, x, y, w, h){
		if(!this.kinastroBorrowed || !this.houseObj || !this.houseObj.kinastroCornerMark){
			return;
		}
		const sz = Math.max(14, Math.min(w * 0.42, h * 0.58));
		group.append('text')
			.attr('class', 'horosa-ziwei-kinastro-corner-mark')
			.attr('x', x + w / 2)
			.attr('y', y + h / 2)
			.attr('dominant-baseline', 'middle')
			.attr('text-anchor', 'middle')
			.attr('fill', 'var(--horosa-ziwei-house-title, var(--horosa-ziwei-house-name, #f3d18b))')
			.attr('stroke', 'none')
			.attr('font-size', `${sz}px`)
			.attr('font-weight', 800)
			.attr('font-family', AstroConst.NormalFont)
			.text(this.houseObj.kinastroCornerMark);
	}

	drawHouseTitleText(group, ord){
		const name = `${this.houseObj.name || ''}`.replace(/[宫宮]$/, '');
		const ganzi = this.houseObj.ganzi || '';
		const nameSize = Math.max(14, Math.min(ord.w * 0.46, ord.h * 0.54));
		const ganziSize = Math.max(9, Math.min(ord.w * 0.30, ord.h * 0.28));
		const cx = ord.x + ord.w / 2;
		const nameY = ord.y + ord.h * 0.36;
		const ganziY = ord.y + ord.h * 0.72;
		group.append('text')
			.attr('class', 'horosa-ziwei-house-name-hit')
			.attr('x', cx)
			.attr('y', nameY)
			.attr('dominant-baseline', 'middle')
			.attr('text-anchor', 'middle')
			.attr('fill', 'var(--horosa-ziwei-house-title, var(--horosa-ziwei-house-name, #f3d18b))')
			.attr('stroke', 'none')
			.attr('font-size', `${nameSize}px`)
			.attr('font-weight', 800)
			.attr('font-family', AstroConst.NormalFont)
			.text(name);
		group.append('text')
			.attr('class', 'horosa-ziwei-house-ganzi-hit')
			.attr('x', cx)
			.attr('y', ganziY)
			.attr('dominant-baseline', 'middle')
			.attr('text-anchor', 'middle')
			.attr('fill', ZWCont.ZWColor.HouseAgeStroke)
			.attr('stroke', 'none')
			.attr('font-size', `${ganziSize}px`)
			.attr('font-weight', 620)
			.attr('font-family', AstroConst.NormalFont)
			.text(ganzi);
		return group;
	}

	drawSihuaStars(){
		let starsCount = this.houseObj.starsMain.length + this.houseObj.starsAssist.length + this.houseObj.starsEvil.length;
		if(!starsCount){
			return;
		}
		let avgsz = (this.width - this.margin*starsCount) / starsCount;
		let baseStarSize = this.starFontSize || this.fontSize;
		let sz = baseStarSize < avgsz ? baseStarSize : avgsz;

		let x = this.x;
		let y = this.y;
		let w = sz + this.margin/2;
		let h = this.kinastroBorrowed ? sz*4 + this.margin*4 : sz*2 + this.margin*2;
		for(let i=0; i<this.houseObj.starsMain.length; i++){
			let star = this.houseObj.starsMain[i];
			let sx = x + i*w;
			this.drawStar(star, sx, y, w, h, ZWCont.ZWColor.StarMainStroke, 760, 1.16);
		}
		x = x + this.houseObj.starsMain.length * w;

		for(let i=0; i<this.houseObj.starsAssist.length; i++){
			let star = this.houseObj.starsAssist[i];
			let sx = x + i*w;
			this.drawStar(star, sx, y, w, h, ZWCont.ZWColor.StarAssistStroke, 560);
		}
		x = x + this.houseObj.starsAssist.length * w;

		for(let i=0; i<this.houseObj.starsEvil.length; i++){
			let star = this.houseObj.starsEvil[i];
			let sx = x + i*w;
			this.drawStar(star, sx, y, w, h, ZWCont.ZWColor.StarEvilStroke, 560);
		}
	}

	drawSihua(){
		this.drawSihuaTitle();
		this.drawSihuaStars();
	}

	shouldShowStarLight(){
		return ZWCont.ZWChart.chart !== ZWCont.ZWChart_SiHua;
	}



	drawSanghe(){

	}
	


	drawFeixing(){

	}

	drawStar(star, x, y, w, h, color, nameWeight = 100, sizeScale = 1){
		if(!star || !star.name){
			return;
		}
		if(this.kinastroBorrowed){
			this.drawKinastroStar(star, x, y, w, h, color, nameWeight, sizeScale);
			return;
		}
		let yearGan = this.chartObj.yearGan;
		let txt = [];
		for(let i=0; i<star.name.length; i++){
			txt[i] = star.name.charAt(i) + '';
		}
		let textW = w * sizeScale;
		let textH = h * sizeScale;
		let textX = x + (w - textW) / 2;
		let textY = y + (h - textH) / 2;
		let flyhua = null;
		if(this.flyGanzi && !this.kinastroBorrowed){
			let gan = this.flyGanzi.charAt(0) + '';
			flyhua = ZiWeiHelper.getSiHua(star.name, gan);
		}
		let starsvg = null;
		if(flyhua){
			let coloropt = ZWCont.ZWColor[flyhua];
			starsvg = GraphHelper.drawTextV(this.svg.append('g'), txt, textX, textY, textW, textH, 2, 
				coloropt.color, nameWeight, coloropt.bg);
			starsvg.selectAll('text').attr('fill', coloropt.color).attr('stroke', 'none');
		}else{
			starsvg = GraphHelper.drawTextV(this.svg.append('g'), txt, textX, textY, textW, textH, 2, color, nameWeight);
			starsvg.selectAll('text').attr('fill', color).attr('stroke', 'none');
		}
		let tip = this.ZWRules.RuleStars[star.name];
		if(tip){
			let tipobj = {
				title: star.name,
				tips: tip,
			};
			this.genTooltip(starsvg, tipobj, star.name)
		}
		const metaText = [this.shouldShowStarLight() ? star.starlight : '', star.flyTo ? `→${star.flyTo}` : ''].filter(Boolean).join(' ');
		if(metaText){
			this.svg.append('text')
				.attr('x', x + w / 2)
				.attr('y', y + h - 2)
				.attr('dominant-baseline', 'auto')
				.attr('text-anchor', 'middle')
				.attr('fill', star.flyTo ? '#cda24d' : 'var(--horosa-muted, #8a8f95)')
				.attr('stroke', 'none')
				.attr('font-size', `${Math.max(7, Math.min(9, Math.round(w * 0.42)))}px`)
				.attr('font-weight', 620)
				.attr('font-family', AstroConst.NormalFont)
				.text(metaText);
		}

		let dim = {
			x: x,
			y: y,
			w: w,
			h: h
		};
		let hua = star.hua || (!this.kinastroBorrowed ? ZiWeiHelper.getSiHua(star.name, yearGan) : '');
		if(hua === '祿'){
			hua = '禄';
		}
		if(hua){
			let coloropt = ZWCont.ZWColor[hua];
			if(!coloropt){
				coloropt = ZWCont.ZWColor.StarMainStroke;
			}
			let huaScale = Math.max(sizeScale, 1.12);
			let huaw = (w - 4) * huaScale;
			let huah = w * huaScale;
			let huax = x + (w - huaw) / 2;
			let huay = y + h;
			let huatxt = [hua];
			let huasvg = GraphHelper.drawTextV(this.svg.append('g'), 
				huatxt, huax, huay, huaw, huah, 2, 
				coloropt.color || '#ffffff', 850, coloropt.bg || ZWCont.ZWColor.StarMainStroke);
			huasvg.selectAll('text')
				.attr('fill', coloropt.color || '#ffffff')
				.attr('stroke', 'rgba(0, 0, 0, 0.34)')
				.attr('stroke-width', 0.55)
				.attr('paint-order', 'stroke')
				.attr('font-weight', 850);
				
			let huatip = this.ZWRules && this.ZWRules.RuleSihua && this.ZWRules.RuleSihua[hua] ? this.ZWRules.RuleSihua[hua].slice(0) : [];
			let huahouse = this.ZWRuleSihua && this.ZWRuleSihua.HuaInHouse ? this.ZWRuleSihua.HuaInHouse[hua] : null;
			let huahousetip = huahouse && huahouse[this.houseObj.name] ? huahouse[this.houseObj.name].slice(0) : [];
			let hasflag = false;
			for(let val of huatip){
				if(val === '=='){
					hasflag = true;
					break;
				}
			}
			if(!hasflag){
				huatip.push('==');
				huatip.push(`${hua}在${this.houseObj.name}`);
				huatip.push(huahousetip);	
			}
			if(huatip){
				let tipobj = {
					title: hua,
					tips: huatip,
				};
				this.genTooltip(huasvg, tipobj, hua)
			}
					
			dim.h = dim.h + huah; 
		}

		let housegan = this.houseObj.ganzi.charAt(0);
		let ganhua = !this.kinastroBorrowed ? ZiWeiHelper.getSiHua(star.name, housegan) : null;
		if(ganhua){
			let coloropt = ZWCont.ZWColor[ganhua];
			let huaScale = Math.max(sizeScale, 1.12);
			let huaw = (w - 4) * huaScale;
			let huah = w * huaScale;
			let huax = x + (w - huaw) / 2;
			let huay = y + dim.h;
			let huatxt = [ganhua];
			if(hua){
				huay = huay + 2;
			}
			GraphHelper.drawTextV(this.svg.append('g'), 
				huatxt, huax, huay, huaw, huah, 2, 
				coloropt.bg, null, null, coloropt.bg);
			
			dim.h = dim.h + huah; 

			let opt = {
				owner: this.svg.append('g'),
				x2: huax + huaw/2,
				y2: huay + huah,
				x1: huax + huaw/2,
				y1: huay,
				color: coloropt.bg,
			};
			let arrow = new D3Arrow(opt);
			arrow.draw();
		}
/*
		if(this.dirIndex !== undefined && this.dirIndex !== null){
			let dirhouse = this.chartObj.houses[this.dirIndex];
			let dirgan = dirhouse.ganzi.charAt(0);
			let dirhua = ZiWeiHelper.getSiHua(star.name, dirgan);
			if(dirhua){
				let coloropt = ZWCont.ZWColor[dirhua];
				let huax = x + 2;
				let huay = y + dim.h + 4;
				let huaw = w - 4;
				let huah = w;
				let huatxt = [dirhua];
				GraphHelper.drawTextV(this.svg.append('g'), 
					huatxt, huax, huay, huaw, huah, 2, 
					coloropt.bg, null, null, coloropt.bg, 30);
				
				dim.h = dim.h + huah + 4; 
			}	
		}
*/
		this.stars.set(star.name, dim);
	}

	drawKinastroStar(star, x, y, w, h, color, nameWeight = 760, sizeScale = 1){
		const txt = [];
		for(let i=0; i<star.name.length; i++){
			txt[i] = star.name.charAt(i) + '';
		}
		const group = this.svg.append('g').attr('class', 'horosa-ziwei-kinastro-star-stack');
		const fontSize = Math.max(16, Math.min(22, Math.round((w - 3) * sizeScale)));
		const nameW = Math.max(fontSize + 3, Math.min(w * sizeScale, w + 2));
		const nameH = Math.max(fontSize * txt.length + txt.length + 2, fontSize + 4);
		const nameX = x + (w - nameW) / 2;
		let cursorY = y + 1;
		let starsvg = GraphHelper.drawTextV(group, txt, nameX, cursorY, nameW, nameH, 1, color, nameWeight || 760);
		starsvg.selectAll('text')
			.attr('fill', color)
			.attr('stroke', 'none')
			.attr('font-weight', nameWeight || 760);
		cursorY += nameH + 1;

		if(this.shouldShowStarLight() && star.starlight){
			group.append('text')
				.attr('class', 'horosa-ziwei-kinastro-star-light')
				.attr('x', x + w / 2)
				.attr('y', cursorY + 6)
				.attr('dominant-baseline', 'middle')
				.attr('text-anchor', 'middle')
				.attr('fill', 'var(--horosa-ziwei-house-age, #8794a8)')
				.attr('stroke', 'none')
				.attr('font-size', `${Math.max(10, Math.min(12, Math.round(w * 0.46)))}px`)
				.attr('font-weight', 680)
				.attr('font-family', AstroConst.NormalFont)
				.text(star.starlight);
			cursorY += 14;
		}

		let hua = star.hua;
		if(hua === '祿'){
			hua = '禄';
		}
		if(hua){
			let coloropt = ZWCont.ZWColor[hua] || ZWCont.ZWColor.StarMainStroke;
			const badgeSize = Math.max(16, Math.min(21, w + 1));
			const badgeX = x + (w - badgeSize) / 2;
			let huasvg = GraphHelper.drawTextV(group, [hua], badgeX, cursorY, badgeSize, badgeSize, 1,
				coloropt.color || '#ffffff', 850, coloropt.bg || ZWCont.ZWColor.StarMainStroke);
			huasvg.selectAll('text')
				.attr('fill', coloropt.color || '#ffffff')
				.attr('stroke', 'rgba(0, 0, 0, 0.34)')
				.attr('stroke-width', 0.55)
				.attr('paint-order', 'stroke')
				.attr('font-weight', 850);
			cursorY += badgeSize + 2;
		}

		if(star.flyTo){
			const flyBranch = `${star.flyTo}`.replace(/[宫宮]$/, '').slice(-1);
			const flyW = Math.max(20, Math.min(25, w + 3));
			const flyH = Math.max(21, Math.min(26, flyW));
			const tipH = Math.max(4, Math.round(flyH * 0.22));
			const flyX = x + (w - flyW) / 2;
			const flyY = cursorY;
			const flyMidX = flyX + flyW / 2;
			const flyBottom = flyY + flyH;
			group.append('rect')
				.attr('class', 'horosa-ziwei-kinastro-fly-badge')
				.attr('x', flyX)
				.attr('y', flyY)
				.attr('width', flyW)
				.attr('height', flyH)
				.attr('rx', 3)
				.attr('ry', 3)
				.attr('fill', 'rgba(205, 162, 77, 0.14)')
				.attr('stroke', '#cda24d')
				.attr('stroke-width', 1.25);
			group.append('path')
				.attr('class', 'horosa-ziwei-kinastro-fly-tip')
				.attr('d', `M${flyMidX - tipH},${flyBottom - 1} L${flyMidX + tipH},${flyBottom - 1} L${flyMidX},${flyBottom + tipH} Z`)
				.attr('fill', 'rgba(205, 162, 77, 0.14)')
				.attr('stroke', '#cda24d')
				.attr('stroke-width', 1.25)
				.attr('stroke-linejoin', 'round');
			const flyFont = Math.max(14, Math.min(17, Math.round(flyW * 0.72)));
			group.append('text')
				.attr('class', 'horosa-ziwei-kinastro-fly-text')
				.attr('x', flyMidX)
				.attr('y', flyY + flyH / 2 + 0.5)
				.attr('dominant-baseline', 'middle')
				.attr('text-anchor', 'middle')
				.attr('fill', '#f3d18b')
				.attr('stroke', 'rgba(0, 0, 0, 0.32)')
				.attr('stroke-width', 0.45)
				.attr('paint-order', 'stroke')
				.attr('font-size', `${flyFont}px`)
				.attr('font-weight', 850)
				.attr('font-family', AstroConst.NormalFont)
				.text(flyBranch);
			cursorY += flyH + tipH + 3;
		}

		let tip = this.ZWRules && this.ZWRules.RuleStars ? this.ZWRules.RuleStars[star.name] : null;
		if(tip){
			this.genTooltip(group, {
				title: star.name,
				tips: tip,
			}, star.name);
		}
		this.stars.set(star.name, {
			x,
			y,
			w,
			h: Math.min(h, cursorY - y),
		});
	}

	drawLaiYing(){
		let hgan = this.houseObj.ganzi.charAt(0) + '';
		let hzi = this.houseObj.ganzi.charAt(1) + '';
		if(hgan !== this.chartObj.yearGan || hzi === '子' || hzi === '丑'){
			return;
		}

		let hw = this.fontSize;
		let hh = hw * 2 + this.margin;
		let hx = this.x + this.width - 25;
		let hy = this.y + this.height - this.height/4 - hh - 10;
		let txt = ['来', '因'];
		let color = AstroConst.AstroColor.Stroke;
		GraphHelper.drawTextV(this.svg.append('g'), txt, hx, hy, hw, hh, 2, 
			color, null, null, color);

	}
	
}

export default ZWHouse;
