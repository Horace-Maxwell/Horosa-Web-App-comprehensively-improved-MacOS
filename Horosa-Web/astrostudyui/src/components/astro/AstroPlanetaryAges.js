import { Component } from 'react';
import { Row, Col, Divider } from 'antd';
import AstroChart from './AstroChart';
import { symbolWithMeaning } from './AstroExtraCommon';
import * as AstroConst from '../../constants/AstroConst';
import * as AstroText from '../../constants/AstroText';
import { saveModuleAISnapshot, } from '../../utils/moduleAiSnapshot';
import { buildPlanetaryAges, buildPlanetaryAgesSnapshotText, } from '../../utils/planetaryAges';
import styles from '../../css/styles.less';

class AstroPlanetaryAges extends Component{
	constructor(props){
		super(props);
		this.saveAISnapshot = this.saveAISnapshot.bind(this);
		this.handleSnapshotRefreshRequest = this.handleSnapshotRefreshRequest.bind(this);
	}

	componentDidMount(){
		this.saveAISnapshot();
		if(typeof window !== 'undefined'){
			window.addEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
	}

	componentDidUpdate(prevProps){
		if(prevProps.value !== this.props.value){
			this.saveAISnapshot();
		}
	}

	componentWillUnmount(){
		if(typeof window !== 'undefined'){
			window.removeEventListener('horosa:refresh-module-snapshot', this.handleSnapshotRefreshRequest);
		}
	}

	saveAISnapshot(){
		const txt = buildPlanetaryAgesSnapshotText(this.props.value);
		saveModuleAISnapshot('planetaryages', txt, { tab: 'planetaryages' });
		return txt;
	}

	handleSnapshotRefreshRequest(evt){
		if(!evt || !evt.detail || evt.detail.module !== 'planetaryages'){
			return;
		}
		const txt = this.saveAISnapshot();
		if(txt){
			evt.detail.snapshotText = txt;
		}
	}

	render(){
		const height = this.props.height ? this.props.height : 760;
		const style = { height: `${height - 20}px`, overflowY: 'auto', overflowX: 'hidden' };
		const { bands, curAge } = buildPlanetaryAges(this.props.value);
		const glyph = (id) => AstroText.AstroMsg[id] || id;
		const cn = (id) => (id ? (AstroText.AstroTxtMsg[id] || id) : '');
		return (
			<div>
				<Row gutter={6}>
					<Col span={16}>
						<AstroChart
							value={this.props.value}
							chartDisplay={this.props.chartDisplay}
							planetDisplay={this.props.planetDisplay}
							lotsDisplay={this.props.lotsDisplay}
							showAstroMeaning={this.props.showAstroMeaning}
							height={height}
						/>
					</Col>
					<Col span={8}>
						<div className={styles.scrollbar} style={style}>
							<Divider orientation="left">行星年龄（托勒密人生七阶）</Divider>
							{curAge !== null ? (
								<div style={{ marginBottom: 8, color: 'var(--horosa-muted, #666)' }}>当前年龄：约 {Math.floor(curAge)} 岁</div>
							) : null}
							{bands.map((b, i) => {
								const range = b.to === Infinity ? `${b.from}+ 岁` : `${b.from}–${b.to} 岁`;
								const pos = b.sign ? `${cn(b.sign)}${(b.signlon !== null) ? (' ' + Math.floor(b.signlon) + '°') : ''}` : '';
								return (
									<div key={i} className={`horosa-age-band${b.active ? ' horosa-age-band--active' : ''}`}>
										<span className="horosa-age-range" style={{ fontFamily: AstroConst.NormalFont }}>{range}</span>
										<span className="horosa-age-glyph">{symbolWithMeaning(b.planet, this.props.showAstroMeaning)}</span>
										<span style={{ fontFamily: AstroConst.NormalFont }}>{cn(b.planet)}{b.active ? ' · 当前' : ''}</span>
										{pos ? <span className="horosa-age-pos" style={{ fontFamily: AstroConst.NormalFont }}>本命 {pos}</span> : null}
									</div>
								);
							})}
						</div>
					</Col>
				</Row>
			</div>
		);
	}
}

export default AstroPlanetaryAges;
