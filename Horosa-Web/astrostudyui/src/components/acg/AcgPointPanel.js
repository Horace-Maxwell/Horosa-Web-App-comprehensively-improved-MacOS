import { Component } from 'react';
import { Spin, Empty } from 'antd';
import { XQDrawer } from '../xq-ui';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import { getInterp } from './interpretations.zh';

const PLANET_CN = {
	[AstroConst.SUN]: '太阳', [AstroConst.MOON]: '月亮', [AstroConst.MERCURY]: '水星',
	[AstroConst.VENUS]: '金星', [AstroConst.MARS]: '火星', [AstroConst.JUPITER]: '木星',
	[AstroConst.SATURN]: '土星', [AstroConst.URANUS]: '天王星', [AstroConst.NEPTUNE]: '海王星',
	[AstroConst.PLUTO]: '冥王星', [AstroConst.NORTH_NODE]: '北交点', [AstroConst.SOUTH_NODE]: '南交点',
	[AstroConst.CHIRON]: '凯龙星', [AstroConst.DARKMOON]: '莉莉丝', [AstroConst.PURPLE_CLOUDS]: '紫炁',
};
const ANGLE_CN = { [AstroConst.ASC]: '上升', [AstroConst.DESC]: '下降', [AstroConst.MC]: '中天', [AstroConst.IC]: '天底' };
const SIGN_CN = ['白羊', '金牛', '双子', '巨蟹', '狮子', '处女', '天秤', '天蝎', '射手', '摩羯', '水瓶', '双鱼'];

function glyph(k) { return (AstroText.AstroMsg && AstroText.AstroMsg[k]) || ''; }
function fmtLat(v) { return `${Math.abs(v).toFixed(2)}°${v >= 0 ? 'N' : 'S'}`; }
function fmtLon(v) { return `${Math.abs(v).toFixed(2)}°${v >= 0 ? 'E' : 'W'}`; }
function signDeg(lon) {
	let l = ((lon % 360) + 360) % 360;
	const idx = Math.floor(l / 30);
	return `${SIGN_CN[idx]} ${(l % 30).toFixed(1)}°`;
}

const GLYPH = { fontFamily: AstroConst.AstroFont };

class AcgPointPanel extends Component {
	render() {
		const { open, onClose, loading, report } = this.props;
		const hits = (report && report.hits) || [];
		const ra = (report && report.relocAngles) || null;
		const ANGLE_ORDER = [AstroConst.ASC, AstroConst.MC, AstroConst.DESC, AstroConst.IC];

		return (
			<XQDrawer
				title="落点分析"
				width={420}
				placement="right"
				onClose={onClose}
				maskClosable={true}
				open={open}
				style={{ overflow: 'auto', paddingBottom: 40, backgroundColor: 'transparent' }}
			>
				{loading ? (
					<div style={{ textAlign: 'center', padding: 40 }}><Spin /></div>
				) : !report ? (
					<Empty description="点击地图任意位置查看落点" />
				) : (
					<div className="horosa-acg-point">
						<div style={{ marginBottom: 12, fontSize: 13, opacity: 0.8 }}>
							所选地点 · {fmtLat(report.lat)} {fmtLon(report.lon)}（orb {report.orb}°）
						</div>

						<div style={{ fontWeight: 600, margin: '6px 0' }}>此地落在以下行星线内</div>
						{hits.length === 0 ? (
							<div style={{ opacity: 0.65, fontSize: 13, padding: '6px 0' }}>
								该 orb 范围内没有行星-轴线经过此地。
							</div>
						) : (
							hits.map((h, i) => (
								<div key={i} style={{ padding: '8px 0', borderBottom: '1px solid rgba(128,128,128,0.18)' }}>
									<div style={{ marginBottom: 3 }}>
										<span style={{ ...GLYPH, fontSize: 16, marginRight: 6 }}>{glyph(h.planet)}{glyph(h.angle)}</span>
										<span style={{ fontWeight: 600 }}>{PLANET_CN[h.planet] || h.planet} {ANGLE_CN[h.angle] || h.angle}线</span>
										<span style={{ float: 'right', opacity: 0.6, fontSize: 12 }}>偏差 {h.orb}°</span>
									</div>
									<div style={{ fontSize: 12.5, lineHeight: 1.6, opacity: 0.85 }}>{getInterp(h.planet, h.angle)}</div>
								</div>
							))
						)}

						{ra ? (
							<div style={{ marginTop: 16 }}>
								<div style={{ fontWeight: 600, margin: '6px 0' }}>迁移四轴（此地起盘）</div>
								{ANGLE_ORDER.map((a) => (
									<div key={a} style={{ fontSize: 13, padding: '3px 0', display: 'flex', justifyContent: 'space-between' }}>
										<span><span style={{ ...GLYPH, marginRight: 6 }}>{glyph(a)}</span>{ANGLE_CN[a]}</span>
										<span>{ra[a] !== undefined ? signDeg(ra[a]) : '—'}</span>
									</div>
								))}
							</div>
						) : null}
					</div>
				)}
			</XQDrawer>
		);
	}
}

export default AcgPointPanel;
