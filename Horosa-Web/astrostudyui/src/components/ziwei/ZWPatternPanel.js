import { Component } from 'react';

const CAT_ORDER = ['富贵', '文贵', '武贵', '破格'];
const CAT_CLASS = { 富贵: 'fugui', 文贵: 'wengui', 武贵: 'wugui', 破格: 'poge' };

class ZWPatternPanel extends Component {
	render() {
		const patterns = this.props.patterns || [];
		if (!patterns.length) {
			return <div className="horosa-empty-hint">起盘后显示命中格局；本盘暂未命中所收录格局。</div>;
		}
		const sorted = patterns.slice().sort((a, b) => {
			const ca = CAT_ORDER.indexOf(a.category);
			const cb = CAT_ORDER.indexOf(b.category);
			return (ca < 0 ? 99 : ca) - (cb < 0 ? 99 : cb);
		});
		return (
			<div className="horosa-ziwei-pattern-scroll">
				<div className="horosa-ziwei-pattern-count">命中格局 · {patterns.length}</div>
				<div className="horosa-ziwei-pattern-list">
					{sorted.map((p) => {
						const cls = CAT_CLASS[p.category] || 'fugui';
						return (
							<div className={`horosa-ziwei-pattern-item cat-${cls}`} key={p.name}>
								<div className="horosa-ziwei-pattern-head">
									<span className="horosa-ziwei-pattern-name">{p.name}</span>
									<span className={`horosa-ziwei-pattern-cat cat-${cls}`}>{p.category}</span>
									{p.broken && <span className="horosa-ziwei-pattern-broken">破格</span>}
								</div>
								<div className="horosa-ziwei-pattern-duanyi">{p.duanyi}</div>
								{p.source_ref && <div className="horosa-ziwei-pattern-src">— {p.source_ref}</div>}
							</div>
						);
					})}
				</div>
			</div>
		);
	}
}

export default ZWPatternPanel;
