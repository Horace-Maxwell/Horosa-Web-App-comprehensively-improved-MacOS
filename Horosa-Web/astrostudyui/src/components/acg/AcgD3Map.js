import { Component } from 'react';
import * as d3 from 'd3';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import world from './world.geo.json';

// Two appearance themes (follow the app's data-horosa-appearance). Planet colours stay
// recognisable but are deepened in light mode; the casing/label-chip flip so lines and
// labels read on either basemap.
const THEMES = {
	dark: {
		ocean: '#0e1521', land: '#1d2735', border: '#33445a', grid: '#2a384d', gridOpacity: 0.55,
		casing: 'rgba(7,11,18,0.62)',
		chipBg: '#0f141c', chipBorder: 'rgba(222,228,238,0.9)',
		geo: { equator: '#7f8a99', ecliptic: '#c9a227', tropic: '#6f7a8a', paran: '#9aa6cc' },
		markerFill: '#ffffff', markerStroke: 'rgba(7,11,18,0.7)',
		tipBg: 'rgba(16,20,28,0.95)', tipFg: '#f0f3f8', tipBorder: 'rgba(255,255,255,0.12)',
		colors: {
			Sun: '#F2A93B', Moon: '#9FB2C9', Mercury: '#39B5A6', Venus: '#E07AB0', Mars: '#E2493B',
			Jupiter: '#8C82F0', Saturn: '#C79A5E', Uranus: '#34C5D6', Neptune: '#6E90F2', Pluto: '#AEB4BD',
			'North Node': '#D98C4A', 'South Node': '#C9B07A', Chiron: '#5DAE54',
			'Dark Moon': '#B188DA', 'Purple Clouds': '#CB8BD9',
		},
	},
	light: {
		ocean: '#e9eff6', land: '#f4f2ea', border: '#c6ccd5', grid: '#d4dbe3', gridOpacity: 0.85,
		casing: 'rgba(255,255,255,0.92)',
		chipBg: '#ffffff', chipBorder: 'rgba(40,46,58,0.88)',
		geo: { equator: '#7d8896', ecliptic: '#b07d14', tropic: '#9aa3af', paran: '#5b6b86' },
		markerFill: '#222831', markerStroke: 'rgba(255,255,255,0.92)',
		tipBg: 'rgba(28,33,42,0.96)', tipFg: '#f4f6fa', tipBorder: 'rgba(0,0,0,0.18)',
		colors: {
			Sun: '#DD8E12', Moon: '#4F6F9C', Mercury: '#1C9A8C', Venus: '#CF4F92', Mars: '#CC382B',
			Jupiter: '#5A4BC0', Saturn: '#866428', Uranus: '#108EA0', Neptune: '#3357C4', Pluto: '#565C66',
			'North Node': '#BC6A28', 'South Node': '#937B3F', Chiron: '#358230',
			'Dark Moon': '#7E52B6', 'Purple Clouds': '#9A55AE',
		},
	},
};
const AstroColor = THEMES.dark.colors;

// Basemap style presets (original designs; orthogonal to light/dark). Each only
// overrides terrain tones — geo/planet colours come from the theme.
const STYLES = {
	classic: { name: '标准', light: {}, dark: {} },
	minimal: {
		name: '简约',
		light: { land: '#eef0ed', border: '#dde0e1', grid: '#e7eaed', gridOpacity: 0.3 },
		dark: { land: '#161c26', border: '#212a38', grid: '#1b2430', gridOpacity: 0.28 },
	},
	atlas: {
		name: '政区',
		light: { ocean: '#cfe1ef', land: '#ece4d2', border: '#b6a888', grid: '#bcc8d4', gridOpacity: 0.55 },
		dark: { ocean: '#0a121f', land: '#27313f', border: '#48586f', grid: '#30404f', gridOpacity: 0.6 },
	},
	noir: {
		name: '单色',
		light: { ocean: '#ebebec', land: '#d8d8da', border: '#bcbcbf', grid: '#dedee0', gridOpacity: 0.45 },
		dark: { ocean: '#0c0c0e', land: '#1c1c20', border: '#35353b', grid: '#212125', gridOpacity: 0.45 },
	},
};

const PLANET_CN = {
	[AstroConst.SUN]: '太阳', [AstroConst.MOON]: '月亮', [AstroConst.MERCURY]: '水星',
	[AstroConst.VENUS]: '金星', [AstroConst.MARS]: '火星', [AstroConst.JUPITER]: '木星',
	[AstroConst.SATURN]: '土星', [AstroConst.URANUS]: '天王星', [AstroConst.NEPTUNE]: '海王星',
	[AstroConst.PLUTO]: '冥王星', [AstroConst.NORTH_NODE]: '北交点', [AstroConst.SOUTH_NODE]: '南交点',
	[AstroConst.CHIRON]: '凯龙星', [AstroConst.DARKMOON]: '莉莉丝', [AstroConst.PURPLE_CLOUDS]: '紫炁',
};
const ANGLE_CN = { asc: '上升', desc: '下降', mc: '中天', ic: '天底' };
const ANGLE_CONST = { asc: AstroConst.ASC, desc: AstroConst.DESC, mc: AstroConst.MC, ic: AstroConst.IC };
const ANGLE_WIDTH = { mc: 1.7, ic: 1.4, asc: 1.6, desc: 1.4 };
const GEO_META = {
	equator: { gkey: 'equator', dash: null, width: 1, label: '赤道' },
	ecliptic: { gkey: 'ecliptic', dash: '5,5', width: 1, label: '黄道' },
	tropicN: { gkey: 'tropic', dash: '2,5', width: 0.8, label: '北回归线' },
	tropicS: { gkey: 'tropic', dash: '2,5', width: 0.8, label: '南回归线' },
};

function readAppearance() {
	if (typeof document !== 'undefined') {
		const a = document.documentElement.getAttribute('data-horosa-appearance');
		if (a === 'dark' || a === 'light') return a;
	}
	if (typeof window !== 'undefined' && window.matchMedia) {
		return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
	}
	return 'light';
}

// Split a lat/lon polyline at the antimeridian, INTERPOLATING the crossing so each
// segment reaches the ±180 edge — lines flow off one edge and back on the other with
// no visible gap. Returns arrays of [lon,lat].
function splitAtDateline(points) {
	const segs = [];
	let cur = [];
	let prev = null;
	for (let i = 0; i < points.length; i++) {
		const p = points[i];
		if (prev !== null && Math.abs(p.lon - prev.lon) > 180) {
			let pU = p.lon;
			if (p.lon - prev.lon > 180) pU = p.lon - 360;
			else if (p.lon - prev.lon < -180) pU = p.lon + 360;
			const edge = pU > prev.lon ? 180 : -180;
			const t = (edge - prev.lon) / (pU - prev.lon);
			const latCross = prev.lat + t * (p.lat - prev.lat);
			cur.push([edge, latCross]);
			if (cur.length > 1) segs.push(cur);
			cur = [[-edge, latCross]];
		}
		cur.push([p.lon, p.lat]);
		prev = p;
	}
	if (cur.length > 1) segs.push(cur);
	return segs;
}

function glyph(key) { return (AstroText.AstroMsg && AstroText.AstroMsg[key]) || ''; }
function planetCN(key) { return PLANET_CN[key] || key; }

class AcgD3Map extends Component {
	constructor(props) {
		super(props);
		this.state = { tip: null, themeName: readAppearance() };
		this.svgRef = { current: null };
		this.hostRef = { current: null };
		this.projection = null;
		this.path = null;
		this.size = { w: 0, h: 0 };
		this.theme = this.computeTheme();
		this.onResize = this.onResize.bind(this);
		this.onAppearance = this.onAppearance.bind(this);
	}

	computeTheme() {
		const base = THEMES[this.state.themeName] || THEMES.light;
		const style = STYLES[this.props.mapStyle] || STYLES.classic;
		const ov = (style[this.state.themeName]) || {};
		return Object.assign({}, base, ov);
	}

	componentDidMount() {
		this.ro = new ResizeObserver(this.onResize);
		if (this.hostRef.current) this.ro.observe(this.hostRef.current);
		if (typeof MutationObserver !== 'undefined') {
			this.mo = new MutationObserver(this.onAppearance);
			this.mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-horosa-appearance'] });
		}
		this.rebuild();
	}

	componentDidUpdate(prevProps, prevState) {
		if (prevState.themeName !== this.state.themeName || prevProps.projection !== this.props.projection || prevProps.mapStyle !== this.props.mapStyle) {
			this.rebuild();
		} else if (
			prevProps.value !== this.props.value || prevProps.lines !== this.props.lines ||
			prevProps.showGeo !== this.props.showGeo || prevProps.showLS !== this.props.showLS ||
			prevProps.showParans !== this.props.showParans || prevProps.showLabels !== this.props.showLabels ||
			prevProps.clickMarker !== this.props.clickMarker
		) {
			this.drawAll();
		}
	}

	componentWillUnmount() {
		if (this.ro) this.ro.disconnect();
		if (this.mo) this.mo.disconnect();
	}

	onAppearance() {
		const n = readAppearance();
		if (n !== this.state.themeName) this.setState({ themeName: n });
	}

	onResize() {
		const host = this.hostRef.current;
		if (!host) return;
		if (host.clientWidth === this.size.w && host.clientHeight === this.size.h) return;
		this.rebuild();
	}

	makeProjection(w, h) {
		const sphere = { type: 'Sphere' };
		const proj = this.props.projection === 'mercator'
			? d3.geoMercator().clipExtent([[0, 0], [w, h]])
			: d3.geoEquirectangular();
		proj.fitSize([w, h], sphere);
		return proj;
	}

	rebuild() {
		const host = this.hostRef.current;
		const svg = this.svgRef.current;
		if (!host || !svg) return;
		this.theme = this.computeTheme();
		const th = this.theme;
		const w = host.clientWidth || 960;
		const h = host.clientHeight || 480;
		this.size = { w, h };
		this.projection = this.makeProjection(w, h);
		this.path = d3.geoPath(this.projection);

		const sel = d3.select(svg);
		sel.selectAll('*').remove();
		sel.attr('width', w).attr('height', h).attr('viewBox', `0 0 ${w} ${h}`);

		const root = sel.append('g').attr('class', 'acg-zoom');
		this.root = root;

		root.append('path').datum({ type: 'Sphere' }).attr('d', this.path).attr('fill', th.ocean).attr('stroke', 'none');
		root.append('path').datum(d3.geoGraticule10()).attr('d', this.path).attr('fill', 'none')
			.attr('stroke', th.grid).attr('stroke-width', 0.4).attr('opacity', th.gridOpacity);
		root.append('g').selectAll('path').data(world.features).enter().append('path')
			.attr('d', this.path).attr('fill', th.land).attr('stroke', th.border).attr('stroke-width', 0.4);

		this.geoG = root.append('g').attr('class', 'acg-geo');
		this.paranG = root.append('g').attr('class', 'acg-paran');
		this.lsG = root.append('g').attr('class', 'acg-ls');
		this.lineG = root.append('g').attr('class', 'acg-lines');
		this.labelG = root.append('g').attr('class', 'acg-labels').style('pointer-events', 'none');
		this.markerG = root.append('g').attr('class', 'acg-markers').style('pointer-events', 'none');

		this.zoomBehavior = d3.zoom().scaleExtent([1, 14]).on('zoom', (ev) => root.attr('transform', ev.transform));
		sel.call(this.zoomBehavior);

		sel.on('click', (ev) => {
			if (!this.props.onMapClick || !this.projection) return;
			const [mx, my] = d3.pointer(ev, svg);
			const t = d3.zoomTransform(svg);
			const inv = this.projection.invert([(mx - t.x) / t.k, (my - t.y) / t.k]);
			if (inv && isFinite(inv[0]) && isFinite(inv[1])) this.props.onMapClick(inv[1], inv[0]);
		});

		this.drawAll();
	}

	showTip(ev, g, t) {
		const host = this.hostRef.current;
		if (!host) return;
		const r = host.getBoundingClientRect();
		this.setState({ tip: { x: ev.clientX - r.left + 14, y: ev.clientY - r.top + 14, g, t } });
	}
	hideTip() { this.setState({ tip: null }); }

	stroke(group, d, { color, width, dash, g, t, casing = true }) {
		if (casing) {
			group.append('path').attr('d', d).attr('fill', 'none')
				.attr('stroke', this.theme.casing).attr('stroke-width', width + 1.8)
				.attr('stroke-linecap', 'round').attr('stroke-linejoin', 'round');
		}
		const line = group.append('path').attr('d', d).attr('fill', 'none')
			.attr('stroke', color).attr('stroke-width', width).attr('stroke-dasharray', dash || null)
			.attr('stroke-linecap', 'round').attr('stroke-linejoin', 'round');
		if (t || g) {
			line.style('cursor', 'pointer')
				.on('mouseover', (ev) => { line.attr('stroke-width', width + 1.4); this.showTip(ev, g, t); })
				.on('mousemove', (ev) => this.showTip(ev, g, t))
				.on('mouseout', () => { line.attr('stroke-width', width); this.hideTip(); });
		}
		return line;
	}

	// label as a small chip: rounded rect (theme bg + frame) with the glyph inside.
	label(lonlat, glyphText, color) {
		const xy = this.projection(lonlat);
		if (!xy || !isFinite(xy[0]) || !isFinite(xy[1])) return;
		const th = this.theme;
		const g = this.labelG.append('g').attr('transform', `translate(${xy[0].toFixed(1)},${xy[1].toFixed(1)})`);
		const text = g.append('text').attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
			.attr('font-family', AstroConst.AstroFont).attr('font-size', 12).attr('fill', color)
			// inline style beats the global `text { stroke }` rule that otherwise outlines the glyph
			.style('stroke', 'none').style('paint-order', 'fill').text(glyphText);
		let bb;
		try { bb = text.node().getBBox(); } catch (e) { bb = { x: -9, y: -7, width: 18, height: 14 }; }
		const px = 3.5, py = 2;
		g.insert('rect', 'text')
			.attr('x', (bb.x - px).toFixed(1)).attr('y', (bb.y - py).toFixed(1))
			.attr('width', (bb.width + 2 * px).toFixed(1)).attr('height', (bb.height + 2 * py).toFixed(1))
			.attr('rx', 3).attr('ry', 3)
			.attr('fill', th.chipBg).attr('stroke', th.chipBorder).attr('stroke-width', 0.9).attr('opacity', 0.97);
	}

	lineVisible(planetKey, field) {
		const lines = this.props.lines;
		if (!lines) return true;
		return lines.has(`${planetKey}:${ANGLE_CONST[field]}`);
	}

	drawAll() {
		if (!this.root || !this.path) return;
		[this.geoG, this.paranG, this.lsG, this.lineG, this.labelG, this.markerG].forEach((g) => g && g.selectAll('*').remove());
		const data = this.props.value;
		const th = this.theme;
		const showLabels = this.props.showLabels !== false;

		if (this.props.showGeo && data && data.geo) {
			Object.keys(GEO_META).forEach((key) => {
				const pts = data.geo[key];
				if (!pts || !pts.length) return;
				const m = GEO_META[key];
				splitAtDateline(pts).forEach((seg) => {
					this.stroke(this.geoG, this.path({ type: 'LineString', coordinates: seg }),
						{ color: th.geo[m.gkey], width: m.width, dash: m.dash, t: m.label });
				});
			});
		}

		// parans: thin, BRIGHT, dashed latitude lines — no casing so they actually show.
		if (this.props.showParans && data && data.parans && data.parans.length) {
			const isLum = (p) => p.a === AstroConst.SUN || p.b === AstroConst.SUN || p.a === AstroConst.MOON || p.b === AstroConst.MOON;
			const list = this.props.paranAll ? data.parans : data.parans.filter(isLum);
			const seen = new Set();
			list.forEach((p) => {
				const k = Math.round(p.lat);   // dedupe overlapping latitudes (1°) — keep it readable
				if (seen.has(k)) return;
				seen.add(k);
				const coords = [];
				for (let lon = -179; lon <= 179; lon += 20) coords.push([lon, p.lat]);
				coords.push([179, p.lat]);
				const line = this.stroke(this.paranG, this.path({ type: 'LineString', coordinates: coords }), {
					color: th.geo.paran, width: 0.8, dash: '4,8', casing: false,
					g: glyph(p.a) + glyph(p.b), t: `${planetCN(p.a)}/${planetCN(p.b)} 交映`,
				});
				line.attr('opacity', 0.55);
			});
		}

		if (!data || !data.planets) { this.drawMarkers(); return; }

		if (this.props.showLS) {
			Object.keys(data.planets).forEach((pk) => {
				const ls = data.planets[pk].lines && data.planets[pk].lines.ls;
				if (!ls || !ls.length) return;
				const color = th.colors[pk] || '#888';
				splitAtDateline(ls).forEach((seg) => {
					this.stroke(this.lsG, this.path({ type: 'LineString', coordinates: seg }),
						{ color, width: 1.1, dash: '2,4', g: glyph(pk), t: `${planetCN(pk)} 本地空间` });
				});
			});
		}

		Object.keys(data.planets).forEach((pk) => {
			const lines = data.planets[pk].lines || {};
			const color = th.colors[pk] || '#888';
			['mc', 'ic', 'asc', 'desc'].forEach((field) => {
				if (!this.lineVisible(pk, field)) return;
				const g = glyph(pk) + glyph(ANGLE_CONST[field]);
				const t = `${planetCN(pk)} ${ANGLE_CN[field]}`;
				if (field === 'mc' || field === 'ic') {
					const lon = lines[field] && lines[field].lon;
					if (lon === undefined || lon === null) return;
					const d = this.path({ type: 'LineString', coordinates: [[lon, -85], [lon, 85]] });
					this.stroke(this.lineG, d, { color, width: ANGLE_WIDTH[field], g, t });
					if (showLabels) this.label([lon, field === 'mc' ? 83 : -83], g, color);
				} else {
					const pts = lines[field];
					if (!pts || !pts.length) return;
					splitAtDateline(pts).forEach((seg) => {
						this.stroke(this.lineG, this.path({ type: 'LineString', coordinates: seg }),
							{ color, width: ANGLE_WIDTH[field], g, t });
					});
					if (showLabels) {
						let anchor = pts[0];
						for (let i = 0; i < pts.length; i++) if (Math.abs(pts[i].lat) < Math.abs(anchor.lat)) anchor = pts[i];
						this.label([anchor.lon, anchor.lat], g, color);
					}
				}
			});
		});

		this.drawMarkers();
	}

	drawMarkers() {
		if (!this.markerG) return;
		const data = this.props.value;
		const th = this.theme;
		if (data && data.meta && data.meta.birth) {
			const b = data.meta.birth;
			const xy = this.projection([b.lon, b.lat]);
			if (xy && isFinite(xy[0])) {
				this.markerG.append('circle').attr('cx', xy[0]).attr('cy', xy[1]).attr('r', 4)
					.attr('fill', th.markerFill).attr('stroke', th.markerStroke).attr('stroke-width', 2);
			}
		}
		const m = this.props.clickMarker;
		if (m && typeof m.lat === 'number') {
			const xy = this.projection([m.lon, m.lat]);
			if (xy && isFinite(xy[0])) {
				const g = this.markerG.append('g');
				g.append('circle').attr('cx', xy[0]).attr('cy', xy[1]).attr('r', 6)
					.attr('fill', 'none').attr('stroke', '#ff5d5d').attr('stroke-width', 2.4);
				g.append('line').attr('x1', xy[0] - 9).attr('y1', xy[1]).attr('x2', xy[0] + 9).attr('y2', xy[1])
					.attr('stroke', '#ff5d5d').attr('stroke-width', 1.4);
				g.append('line').attr('x1', xy[0]).attr('y1', xy[1] - 9).attr('x2', xy[0]).attr('y2', xy[1] + 9)
					.attr('stroke', '#ff5d5d').attr('stroke-width', 1.4);
			}
		}
	}

	render() {
		const height = this.props.height || 600;
		const tip = this.state.tip;
		const th = THEMES[this.state.themeName] || THEMES.light;
		return (
			<div className="horosa-acg-d3-map"
				ref={(el) => { this.hostRef.current = el; }}
				style={{ position: 'relative', width: '100%', height, overflow: 'hidden', background: th.ocean }}
			>
				<svg ref={(el) => { this.svgRef.current = el; }} style={{ display: 'block', width: '100%', height: '100%' }} />
				{tip ? (
					<div style={{
						position: 'absolute', left: tip.x, top: tip.y, pointerEvents: 'none',
						background: th.tipBg, color: th.tipFg, padding: '3px 9px', borderRadius: 5,
						whiteSpace: 'nowrap', zIndex: 5, border: `1px solid ${th.tipBorder}`,
						display: 'flex', alignItems: 'center', gap: 6, fontSize: 13,
					}}>
						{tip.g ? <span style={{ fontFamily: AstroConst.AstroFont, fontSize: 15 }}>{tip.g}</span> : null}
						{tip.t ? <span>{tip.t}</span> : null}
					</div>
				) : null}
			</div>
		);
	}
}

export default AcgD3Map;
export { AstroColor, STYLES };
