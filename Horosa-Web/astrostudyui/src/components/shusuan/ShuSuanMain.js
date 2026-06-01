import { Component } from 'react';
import KinAstroMain from '../kinastro/KinAstroMain';

export default class ShuSuanMain extends Component{
	constructor(props){
		super(props);
		this.state = { technique: 'shaozi' };
		this.setTechnique = this.setTechnique.bind(this);
	}

	setTechnique(technique){
		this.setState({ technique });
	}

	render(){
		return (
			<KinAstroMain
				{...this.props}
				technique={this.state.technique}
				onTechniqueChange={this.setTechnique}
			/>
		);
	}
}
