import { Component } from 'react';
import KinAstroMain from '../kinastro/KinAstroMain';

const MING_OTHER_TECHNIQUE_TABS = [
	{ key: 'cetian', label: '策天飞星' },
	{ key: 'xianqin', label: '演禽' },
];

export default class MingOtherMain extends Component{
	constructor(props){
		super(props);
		this.state = {
			technique: 'cetian',
		};
		this.onTechniqueChange = this.onTechniqueChange.bind(this);
	}

	onTechniqueChange(technique){
		this.setState({
			technique: technique === 'xianqin' ? 'xianqin' : 'cetian',
		});
	}

	render(){
		return (
			<KinAstroMain
				{...this.props}
				technique={this.state.technique}
				activeTechnique={this.state.technique}
				techniqueTabs={MING_OTHER_TECHNIQUE_TABS}
				onTechniqueChange={this.onTechniqueChange}
			/>
		);
	}
}
