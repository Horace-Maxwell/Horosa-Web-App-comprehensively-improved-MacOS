import { Component } from 'react';
import AstroChart13 from './AstroChart13';

class HellenAstroMain extends Component{

	constructor(props) {
		super(props);
		this.state = {
			currentTab: "Chart13",
			hook: {
				Chart13:{
					fun: null
				},
			},
		};

		this.changeTab = this.changeTab.bind(this);
		this.onFieldsChange = this.onFieldsChange.bind(this);

		if(this.props.hook){
			this.props.hook.fun = (fields)=>{
				let hook = this.state.hook;
				if(hook[this.state.currentTab].fun){
					let fld = {
						...fields,
					}
					hook[this.state.currentTab].fun(fld)
				}
			};
		}

	}


	changeTab(key){
		let hook = this.state.hook;
		this.setState({
			currentTab: key,
		}, ()=>{
			if(this.state.hook[key] && this.state.hook[key].fun){
				this.state.hook[key].fun();
			}
			if(this.props.dispatch){
				this.props.dispatch({
					type: 'astro/save',
					payload: {
						currentSubTab: key,
					}
				});
			}
		});
	}

	onFieldsChange(values){
		if(this.props.onChange){
			let flds = this.props.onChange(values);
			let hook = this.state.hook[this.state.currentTab];
			if(hook.fun){
				hook.fun(flds);
			}
		}
	}

	componentDidMount(){
		let hook = this.state.hook;
		if(hook[this.state.currentTab].fun){
			hook[this.state.currentTab].fun()
		}
	}

	render(){
		let fields = this.props.fields;
		let height = this.props.height ? this.props.height : 760;


		return (
			<div className="horosa-aux-module-page xq-chart-renderer xq-chart-renderer-hellen">
				<AstroChart13
					onChange={this.onFieldsChange}
					fields={fields}
					height={height}
					chartDisplay={this.props.chartDisplay}
					planetDisplay={this.props.planetDisplay}
					lotsDisplay={this.props.lotsDisplay}
					showPlanetHouseInfo={this.props.showPlanetHouseInfo}
					showAstroMeaning={this.props.showAstroMeaning}
					hook={this.state.hook.Chart13}
				/>
			</div>
		);
	}
}

export default HellenAstroMain;
