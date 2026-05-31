import * as AstroText from '../../constants/AstroText';
import * as AstroConst from '../../constants/AstroConst';
import { buildMeaningTipByCategory } from './AstroMeaningData';
import { isMeaningEnabled, wrapWithMeaning } from './AstroMeaningPopover';

export function unwrapResult(data){
	return data && data.Result ? data.Result : data;
}

// 字形 + 富「悬浮释义」弹窗（gated showAstroMeaning），供新推运技法与既有技法同步 hover 释义。
export function symbolWithMeaning(id, showAstroMeaning, category = 'planet'){
	return wrapWithMeaning(astroSymbol(id), isMeaningEnabled(showAstroMeaning), buildMeaningTipByCategory(category, id));
}

export function planetName(id){
	return (AstroText.AstroMsg && AstroText.AstroMsg[id]) || (AstroText.AstroTxtMsg && AstroText.AstroTxtMsg[id]) || id || '-';
}

export const astroSymbolStyle = {
	fontFamily: AstroConst.AstroFont,
	fontSize: '1.1em',
	lineHeight: 1,
	display: 'inline-block',
};

function isGlyphCode(value){
	if(value === undefined || value === null){
		return false;
	}
	const text = `${value}`;
	if(text.length !== 1){
		return false;
	}
	return /^[A-Za-z0-9{}$]$/.test(text);
}

export function astroSymbol(id){
	const glyph = (AstroText.AstroMsg && AstroText.AstroMsg[id]) || (isGlyphCode(id) ? `${id}` : '');
	const title = (AstroText.AstroTxtMsg && AstroText.AstroTxtMsg[id]) || (AstroText.AstroMsgCN && AstroText.AstroMsgCN[id]) || `${id || ''}`;
	if(!glyph){
		return title || '-';
	}
	return <span style={astroSymbolStyle} title={title}>{glyph}</span>;
}

export function astroSymbolList(ids, separator = ' / '){
	const items = ids || [];
	if(!items.length){
		return '-';
	}
	const parts = [];
	items.forEach((id, idx)=>{
		if(idx > 0){
			parts.push(<span key={`sep-${idx}`}>{separator}</span>);
		}
		parts.push(<span key={`${id}-${idx}`}>{astroSymbol(id)}</span>);
	});
	return parts;
}

export function signName(id){
	return (AstroText.AstroTxtMsg && AstroText.AstroTxtMsg[id]) || (AstroText.AstroMsg && AstroText.AstroMsg[id]) || id || '-';
}

export function fmtNum(value, digits = 2){
	const num = Number(value);
	if(!Number.isFinite(num)){
		return '-';
	}
	return num.toFixed(digits);
}

export function fmtDegree(item){
	if(!item){
		return '-';
	}
	const sign = signName(item.sign);
	const signlon = item.signlon !== undefined ? item.signlon : (Number(item.lon) % 30);
	return `${sign} ${fmtNum(signlon, 2)}°`;
}

export function chartParams(chartObj){
	const params = chartObj && chartObj.params ? chartObj.params : {};
	const birth = params.birth || '';
	const parts = birth.split(' ');
	return {
		date: params.date || parts[0],
		time: params.time || parts[1] || '12:00:00',
		ad: params.ad || 1,
		zone: params.zone || '+00:00',
		lat: params.lat || '0n00',
		lon: params.lon || '0e00',
		hsys: params.hsys !== undefined ? params.hsys : 0,
		zodiacal: params.zodiacal !== undefined ? params.zodiacal : 0,
		tradition: false,
		predictive: false,
		orbs: params.orbs,
		orbScale: params.orbScale,
	};
}

export function chartRequestKey(chartObj, extra = ''){
	if(!chartObj){
		return '';
	}
	const params = chartObj.params || {};
	const parts = [
		params.birth || '',
		params.date || '',
		params.time || '',
		params.zone || '',
		params.lat || '',
		params.lon || '',
		params.hsys !== undefined ? params.hsys : '',
		params.zodiacal !== undefined ? params.zodiacal : '',
		params.orbScale !== undefined ? params.orbScale : '',
		params.orbs ? JSON.stringify(params.orbs) : '',
		extra,
	];
	return parts.join('|');
}

export function paramsRequestKey(params){
	if(!params){
		return '';
	}
	try{
		return JSON.stringify(params);
	}catch(e){
		return `${params}`;
	}
}

export const cardStyle = {
	border: '1px solid var(--horosa-border-soft, rgba(148, 163, 184, .28))',
	borderRadius: 8,
	padding: 12,
	marginBottom: 12,
	background: 'var(--horosa-surface, rgba(255,255,255,.72))',
};

export const gridStyle = {
	display: 'grid',
	gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
	gap: 8,
};

export function SmallTable({columns, rows, rowKey}){
	return (
		<table style={{width: '100%', borderCollapse: 'collapse', fontSize: 12}}>
			<thead>
				<tr>
					{columns.map((col)=>(
						<th key={col.key} style={{textAlign: 'left', borderBottom: '1px solid rgba(148,163,184,.35)', padding: '6px 4px'}}>
							{col.title}
						</th>
					))}
				</tr>
			</thead>
			<tbody>
				{(rows || []).map((row, idx)=>(
					<tr key={rowKey ? rowKey(row, idx) : idx}>
						{columns.map((col)=>(
							<td key={col.key} style={{borderBottom: '1px solid rgba(148,163,184,.16)', padding: '6px 4px', verticalAlign: 'top'}}>
								{col.render ? col.render(row[col.key], row, idx) : row[col.key]}
							</td>
						))}
					</tr>
				))}
			</tbody>
		</table>
	);
}
