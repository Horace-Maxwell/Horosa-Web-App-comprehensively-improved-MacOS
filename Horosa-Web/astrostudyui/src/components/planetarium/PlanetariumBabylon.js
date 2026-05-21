import { Component, createRef } from 'react';
import DateTime from '../comp/DateTime';
import { fetchPlanetariumState } from '../../services/planetarium';

const BABYLON = typeof window !== 'undefined' ? window.BABYLON : null;

const SKY_RADIUS = 900;
const BODY_RADIUS = 820;
const STAR_RADIUS = 780;
const LINE_RADIUS = 760;

const BODY_LABELS = {
	Sun: '太阳',
	Moon: '月亮',
	Mercury: '水星',
	Venus: '金星',
	Mars: '火星',
	Jupiter: '木星',
	Saturn: '土星',
	Uranus: '天王星',
	Neptune: '海王星',
	Pluto: '冥王星',
	'North Node': '北交点',
	'South Node': '南交点',
};

const BODY_COLORS = {
	Sun: new BABYLON.Color3(1.0, 0.76, 0.25),
	Moon: new BABYLON.Color3(0.82, 0.9, 1.0),
	Mercury: new BABYLON.Color3(0.72, 0.72, 0.68),
	Venus: new BABYLON.Color3(0.98, 0.72, 0.48),
	Mars: new BABYLON.Color3(1.0, 0.34, 0.22),
	Jupiter: new BABYLON.Color3(0.95, 0.72, 0.48),
	Saturn: new BABYLON.Color3(0.92, 0.82, 0.56),
	Uranus: new BABYLON.Color3(0.44, 0.9, 0.96),
	Neptune: new BABYLON.Color3(0.38, 0.52, 1.0),
	Pluto: new BABYLON.Color3(0.78, 0.66, 0.58),
	'North Node': new BABYLON.Color3(0.75, 0.88, 1.0),
	'South Node': new BABYLON.Color3(0.7, 0.58, 0.96),
};

const DEFAULT_LAYERS = {
	stars: true,
	bodies: true,
	horizon: true,
	equator: true,
	ecliptic: true,
	zodiac: true,
	houses: true,
	su28: true,
	beidou: true,
	qizheng: true,
};

function degToRad(deg){
	return (Number(deg) || 0) * Math.PI / 180;
}

function normalizeAzimuth(azimuth){
	return ((Number(azimuth) || 0) + 180) % 360;
}

function clamp(value, min, max){
	return Math.max(min, Math.min(max, value));
}

function starTemperatureColor(star, brightness){
	const kelvin = Number(star && star.colorTemperature);
	if(!Number.isFinite(kelvin) || kelvin <= 0){
		return {
			r: 0.58 + brightness * 0.34,
			g: 0.66 + brightness * 0.22,
			b: 0.86 + brightness * 0.1,
		};
	}
	const t = clamp(kelvin, 2800, 14000);
	const warm = clamp((6500 - t) / 3700, 0, 1);
	const cool = clamp((t - 6500) / 7500, 0, 1);
	return {
		r: clamp(0.82 + warm * 0.18 - cool * 0.08, 0.52, 1),
		g: clamp(0.82 + warm * 0.06 + cool * 0.05, 0.52, 1),
		b: clamp(0.86 - warm * 0.34 + cool * 0.14, 0.48, 1),
	};
}

function toSkyVector(item, radius){
	const alt = Number(item.altitudeAppa !== undefined && item.altitudeAppa !== null ? item.altitudeAppa : item.altitudeTrue) || 0;
	const az = normalizeAzimuth(item.azimuth);
	const altRad = degToRad(alt);
	const azRad = degToRad(az);
	const r = radius * Math.cos(altRad);
	return new BABYLON.Vector3(
		r * Math.sin(azRad),
		radius * Math.sin(altRad),
		r * Math.cos(azRad),
	);
}

function formatDeg(val){
	if(val === undefined || val === null || Number.isNaN(Number(val))){
		return '--';
	}
	return `${Math.round(Number(val) * 1000) / 1000}°`;
}

function bodyName(item){
	return BODY_LABELS[item.id] || item.name || item.id || '天体';
}

function buildObservationTime(fields){
	const dt = fields && fields.time && fields.time.value && fields.time.value.clone
		? fields.time.value.clone()
		: new DateTime();
	if(fields && fields.date && fields.date.value){
		const d = fields.date.value;
		dt.year = d.year;
		dt.month = d.month;
		dt.date = d.date;
		dt.ad = d.ad;
	}
	if(fields && fields.zone){
		dt.zone = fields.zone.value;
	}
	dt.calcJdn();
	return dt;
}

function buildRequestParams(fields, time){
	return {
		date: time.format('YYYY/MM/DD'),
		time: time.format('HH:mm:ss'),
		ad: time.ad,
		zone: time.zone,
		lat: fields.lat.value,
		lon: fields.lon.value,
		gpsLat: fields.gpsLat.value,
		gpsLon: fields.gpsLon.value,
		name: fields.name ? fields.name.value : null,
		pos: fields.pos ? fields.pos.value : null,
		hsys: fields.hsys ? fields.hsys.value : 1,
		zodiacal: fields.zodiacal ? fields.zodiacal.value : 0,
		doubingSu28: fields.doubingSu28 ? fields.doubingSu28.value : 0,
		southchart: fields.southchart ? fields.southchart.value : 0,
		starLimit: 9000,
	};
}

class PlanetariumRenderer {
	constructor(canvas, onPick, onMetrics){
		this.canvas = canvas;
		this.onPick = onPick;
		this.onMetrics = onMetrics;
		this.engine = new BABYLON.Engine(canvas, true, {
			preserveDrawingBuffer: false,
			stencil: false,
			antialias: true,
			powerPreference: 'high-performance',
		});
		this.scene = new BABYLON.Scene(this.engine);
		this.scene.clearColor = new BABYLON.Color4(0.008, 0.012, 0.026, 1);
		this.scene.ambientColor = new BABYLON.Color3(0.12, 0.16, 0.3);
		this.groups = [];
		this.pickMeshes = [];
		this.layers = {...DEFAULT_LAYERS};
		this.initScene();
	}

	initScene(){
		this.camera = new BABYLON.ArcRotateCamera(
			'planetarium-camera',
			Math.PI * 1.25,
			Math.PI * 0.42,
			1120,
			BABYLON.Vector3.Zero(),
			this.scene,
		);
		this.camera.lowerRadiusLimit = 180;
		this.camera.upperRadiusLimit = 1400;
		this.camera.wheelPrecision = 45;
		this.camera.panningSensibility = 0;
		this.camera.attachControl(this.canvas, true);

		const light = new BABYLON.HemisphericLight('planetarium-light', new BABYLON.Vector3(0, 1, 0), this.scene);
		light.intensity = 0.38;

		const sky = BABYLON.MeshBuilder.CreateSphere('sky-shell', { diameter: SKY_RADIUS * 2, segments: 48, sideOrientation: BABYLON.Mesh.BACKSIDE }, this.scene);
		const skyMat = new BABYLON.StandardMaterial('sky-material', this.scene);
		skyMat.disableLighting = true;
		skyMat.emissiveColor = new BABYLON.Color3(0.006, 0.011, 0.032);
		skyMat.alpha = 1;
		sky.material = skyMat;

		const glow = new BABYLON.GlowLayer('planetarium-glow', this.scene);
		glow.intensity = 0.12;
		this.glow = glow;
		this.sky = sky;

		this.scene.onPointerObservable.add((pointerInfo)=>{
			if(pointerInfo.type !== BABYLON.PointerEventTypes.POINTERPICK){
				return;
			}
			const hit = pointerInfo.pickInfo && pointerInfo.pickInfo.pickedMesh;
			if(hit && hit.metadata && hit.metadata.body && this.onPick){
				this.onPick(hit.metadata.body);
			}
		});

		this.engine.runRenderLoop(()=>{
			if(this.scene){
				this.scene.render();
				if(this.onMetrics){
					this.onMetrics({
						fps: Math.round(this.engine.getFps()),
						meshes: this.scene.meshes.length,
					});
				}
			}
		});
		this.resizeHandler = ()=>{
			if(this.engine){
				this.engine.resize();
			}
		};
		window.addEventListener('resize', this.resizeHandler);
	}

	setLayers(layers){
		this.layers = {...this.layers, ...(layers || {})};
		this.applyLayerVisibility();
	}

	clearData(){
		this.pickMeshes = [];
		this.groups.forEach((group)=>{
			group.dispose(false, true);
		});
		this.groups = [];
	}

	makeGroup(name){
		const group = new BABYLON.TransformNode(name, this.scene);
		this.groups.push(group);
		return group;
	}

	material(name, color, alpha = 1){
		const mat = new BABYLON.StandardMaterial(name, this.scene);
		mat.disableLighting = true;
		mat.emissiveColor = color;
		mat.diffuseColor = color;
		mat.alpha = alpha;
		return mat;
	}

	updateData(data, layers){
		this.clearData();
		this.layers = {...DEFAULT_LAYERS, ...(layers || {})};
		if(!data){
			return;
		}
		this.createCardinals();
		this.createStars(data.stars && data.stars.catalog ? data.stars.catalog : []);
		this.createOverlayLines(data.overlays || {});
		this.createBodies(data.bodies || []);
		this.createTraditionalLayer('su28', data.traditions && data.traditions.su28 ? data.traditions.su28 : [], new BABYLON.Color3(0.9, 0.68, 0.36), 4.8);
		this.createTraditionalLayer('beidou', data.traditions && data.traditions.beidou ? data.traditions.beidou : [], new BABYLON.Color3(0.52, 0.82, 1), 6.2);
		this.applyLayerVisibility();
	}

	createCardinals(){
		const group = this.makeGroup('cardinals');
		[
			{ label: '南', azimuth: 0 },
			{ label: '西', azimuth: 90 },
			{ label: '北', azimuth: 180 },
			{ label: '东', azimuth: 270 },
		].forEach((item)=>{
			const plane = this.createTextPlane(item.label, 84, '#d7e9ff', 'rgba(8,16,34,0.1)');
			plane.position = toSkyVector({...item, altitudeAppa: 2}, LINE_RADIUS);
			plane.parent = group;
			plane.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;
		});
	}

	createTextPlane(text, size, color, bg){
		const texture = new BABYLON.DynamicTexture(`label-${text}-${Math.random()}`, { width: 256, height: 128 }, this.scene, true);
		texture.hasAlpha = true;
		const ctx = texture.getContext();
		ctx.clearRect(0, 0, 256, 128);
		ctx.fillStyle = bg || 'rgba(0,0,0,0)';
		ctx.fillRect(0, 0, 256, 128);
		texture.drawText(text, null, 78, `600 ${size || 48}px sans-serif`, color || '#fff', null, true, true);
		const mat = new BABYLON.StandardMaterial(`label-mat-${text}-${Math.random()}`, this.scene);
		mat.diffuseTexture = texture;
		mat.emissiveTexture = texture;
		mat.opacityTexture = texture;
		mat.disableLighting = true;
		mat.useAlphaFromDiffuseTexture = true;
		const plane = BABYLON.MeshBuilder.CreatePlane(`label-${text}`, { width: 58, height: 29 }, this.scene);
		plane.material = mat;
		plane.isPickable = false;
		return plane;
	}

	createStars(stars){
		if(!stars || !stars.length){
			return;
		}
		const group = this.makeGroup('stars-layer');
		const pcs = new BABYLON.PointsCloudSystem('star-point-cloud', 1.35, this.scene);
		pcs.addPoints(stars.length, (particle, idx)=>{
			const star = stars[idx];
			const mag = Number(star.mag || 5);
			particle.position = toSkyVector(star, STAR_RADIUS);
			const b = Math.max(0.18, Math.min(1.0, 1.18 - mag / 6.5));
			const c = starTemperatureColor(star, b);
			particle.color = new BABYLON.Color4(c.r, c.g, c.b, Math.max(0.18, b * 0.86));
		});
		pcs.buildMeshAsync().then((mesh)=>{
			mesh.parent = group;
			mesh.isPickable = false;
		});
	}

	createLine(name, points, color, alpha, parent, radius){
		if(!points || points.length < 2){
			return null;
		}
		const vectors = points.map((p)=>toSkyVector(p, radius || LINE_RADIUS));
		const line = BABYLON.MeshBuilder.CreateLines(name, { points: vectors }, this.scene);
		line.color = color;
		line.alpha = alpha === undefined ? 1 : alpha;
		line.parent = parent;
		line.isPickable = false;
		return line;
	}

	createOverlayLines(overlays){
		const group = this.makeGroup('overlay-layer');
		this.createLine('horizon', overlays.horizon && overlays.horizon.points, new BABYLON.Color3(0.42, 0.76, 0.96), 0.72, group, LINE_RADIUS);
		this.createLine('meridian', overlays.meridian && overlays.meridian.points, new BABYLON.Color3(0.78, 0.56, 0.94), 0.5, group, LINE_RADIUS);
		this.createLine('equator', overlays.equator && overlays.equator.points, new BABYLON.Color3(0.5, 0.62, 1.0), 0.42, group, LINE_RADIUS);
		this.createLine('ecliptic', overlays.ecliptic && overlays.ecliptic.points, new BABYLON.Color3(1.0, 0.72, 0.25), 0.66, group, LINE_RADIUS + 8);
		(overlays.zodiac || []).forEach((item)=>{
			this.createLine(`zodiac-${item.key}`, item.points, new BABYLON.Color3(0.72, 0.56, 0.94), 0.32, group, LINE_RADIUS + 12);
		});
		(overlays.houses || []).forEach((item)=>{
			const p1 = toSkyVector(item, LINE_RADIUS + 20);
			const p2 = BABYLON.Vector3.Zero();
			const line = BABYLON.MeshBuilder.CreateLines(`house-${item.id}`, { points: [p1, p2] }, this.scene);
			line.color = new BABYLON.Color3(0.5, 0.92, 0.75);
			line.alpha = 0.36;
			line.parent = group;
		});
	}

	createBodies(bodies){
		const group = this.makeGroup('body-layer');
		bodies.forEach((body)=>{
			const color = BODY_COLORS[body.id] || new BABYLON.Color3(0.9, 0.9, 1);
			const diameter = body.id === 'Sun' ? 21 : (body.id === 'Moon' ? 17 : 12);
			const mesh = BABYLON.MeshBuilder.CreateSphere(`body-${body.id}`, { diameter, segments: 18 }, this.scene);
			mesh.position = toSkyVector(body, BODY_RADIUS);
			mesh.material = this.material(`body-mat-${body.id}`, color, 1);
			mesh.parent = group;
			mesh.metadata = { body: { ...body, displayName: bodyName(body), layer: 'body' } };
			this.pickMeshes.push(mesh);

			if(body.id === 'Sun' || body.id === 'Moon' || body.id === 'Jupiter' || body.id === 'Saturn'){
				const label = this.createTextPlane(bodyName(body), 42, '#f4f7ff', 'rgba(0,0,0,0)');
				label.position = mesh.position.add(new BABYLON.Vector3(0, 24, 0));
				label.parent = group;
				label.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;
			}
		});
	}

	createTraditionalLayer(kind, items, color, diameter){
		const group = this.makeGroup(`${kind}-layer`);
		items.forEach((item)=>{
			const mesh = BABYLON.MeshBuilder.CreateSphere(`${kind}-${item.id || item.name}`, { diameter: diameter || 5, segments: 8 }, this.scene);
			mesh.position = toSkyVector(item, BODY_RADIUS - 28);
			mesh.material = this.material(`${kind}-mat-${item.id || item.name}`, color, 0.9);
			mesh.parent = group;
			mesh.metadata = { body: { ...item, displayName: item.name || item.id, layer: kind } };
			this.pickMeshes.push(mesh);
		});
		if(kind === 'beidou' && items.length > 1){
			this.createLine('beidou-line', items, color, 0.72, group, BODY_RADIUS - 28);
		}
	}

	applyLayerVisibility(){
		this.groups.forEach((group)=>{
			if(group.name.indexOf('stars-layer') === 0){
				group.setEnabled(!!this.layers.stars);
			}else if(group.name.indexOf('body-layer') === 0){
				group.setEnabled(!!this.layers.bodies);
			}else if(group.name.indexOf('overlay-layer') === 0){
				group.setEnabled(true);
				group.getChildMeshes().forEach((mesh)=>{
					if(mesh.name.indexOf('horizon') >= 0){ mesh.setEnabled(!!this.layers.horizon); }
					else if(mesh.name.indexOf('meridian') >= 0){ mesh.setEnabled(!!this.layers.horizon); }
					else if(mesh.name.indexOf('equator') >= 0){ mesh.setEnabled(!!this.layers.equator); }
					else if(mesh.name.indexOf('ecliptic') >= 0){ mesh.setEnabled(!!this.layers.ecliptic); }
					else if(mesh.name.indexOf('zodiac') >= 0){ mesh.setEnabled(!!this.layers.zodiac); }
					else if(mesh.name.indexOf('house') >= 0){ mesh.setEnabled(!!this.layers.houses); }
				});
			}else if(group.name.indexOf('su28-layer') === 0){
				group.setEnabled(!!this.layers.su28);
			}else if(group.name.indexOf('beidou-layer') === 0){
				group.setEnabled(!!this.layers.beidou);
			}
		});
	}

	dispose(){
		window.removeEventListener('resize', this.resizeHandler);
		this.clearData();
		if(this.sky){
			this.sky.dispose(false, true);
		}
		if(this.glow){
			this.glow.dispose();
		}
		if(this.scene){
			this.scene.dispose();
			this.scene = null;
		}
		if(this.engine){
			this.engine.stopRenderLoop();
			this.engine.dispose();
			this.engine = null;
		}
	}
}

class PlanetariumBabylon extends Component{
	constructor(props){
		super(props);
		const time = buildObservationTime(props.fields);
		this.state = {
			time,
			data: null,
			selected: null,
			loading: true,
			error: null,
			speed: 0,
			layers: {...DEFAULT_LAYERS},
			metrics: {
				fps: 0,
				meshes: 0,
				loadMs: 0,
				catalogCount: 0,
			},
		};
		this.canvasRef = createRef();
		this.renderer = null;
		this.reqSeq = 0;
		this.playTimer = null;
		this.metricTimer = null;
		this.requestState = this.requestState.bind(this);
		this.toggleLayer = this.toggleLayer.bind(this);
		this.changeSpeed = this.changeSpeed.bind(this);
		this.jumpNow = this.jumpNow.bind(this);
		this.toggleFullscreen = this.toggleFullscreen.bind(this);
	}

	componentDidMount(){
		this.renderer = new PlanetariumRenderer(
			this.canvasRef.current,
			(selected)=>this.setState({ selected }),
			(metrics)=>{
				if(!this.metricTimer){
					this.metricTimer = setTimeout(()=>{
						this.metricTimer = null;
						this.setState((prev)=>({
							metrics: {
								...prev.metrics,
								...metrics,
							},
						}));
					}, 500);
				}
			},
		);
		this.requestState();
	}

	componentDidUpdate(prevProps, prevState){
		if(prevState.layers !== this.state.layers && this.renderer){
			this.renderer.setLayers(this.state.layers);
		}
		if(prevState.speed !== this.state.speed){
			this.setupPlayback();
		}
		if(prevProps.fields !== this.props.fields){
			const time = buildObservationTime(this.props.fields);
			this.setState({ time }, this.requestState);
		}
	}

	componentWillUnmount(){
		if(this.playTimer){
			clearInterval(this.playTimer);
			this.playTimer = null;
		}
		if(this.metricTimer){
			clearTimeout(this.metricTimer);
			this.metricTimer = null;
		}
		if(this.renderer){
			this.renderer.dispose();
			this.renderer = null;
		}
	}

	setupPlayback(){
		if(this.playTimer){
			clearInterval(this.playTimer);
			this.playTimer = null;
		}
		const speed = Number(this.state.speed || 0);
		if(!speed){
			return;
		}
		this.playTimer = setInterval(()=>{
			this.setState((prev)=>{
				const next = prev.time.clone();
				if(speed === 86400){
					next.add(1, 'd');
				}else if(speed === 2592000){
					next.add(30, 'd');
				}else if(speed === 31536000){
					next.add(1, 'y');
				}else{
					next.addSecond(speed);
				}
				return { time: next };
			}, this.requestState);
		}, 1000);
	}

	async requestState(){
		const seq = ++this.reqSeq;
		const started = performance.now();
		this.setState({ loading: true, error: null });
		const params = buildRequestParams(this.props.fields, this.state.time);
		const rsp = await fetchPlanetariumState(params);
		if(seq !== this.reqSeq){
			return;
		}
		const data = rsp && rsp.Result ? rsp.Result : rsp;
		if(!data || data.err){
			this.setState({
				loading: false,
				error: data && data.err ? data.err : '天文馆数据载入失败',
			});
			return;
		}
		if(this.renderer){
			this.renderer.updateData(data, this.state.layers);
		}
		this.setState((prev)=>({
			data,
			loading: false,
			error: null,
			metrics: {
				...prev.metrics,
				loadMs: Math.round(performance.now() - started),
				catalogCount: data.meta ? data.meta.renderedCatalogCount : 0,
			},
		}));
	}

	toggleLayer(key){
		this.setState((prev)=>({
			layers: {
				...prev.layers,
				[key]: !prev.layers[key],
			},
		}));
	}

	changeSpeed(speed){
		this.setState({ speed });
	}

	jumpNow(){
		this.setState({
			time: buildObservationTime(this.props.fields),
			speed: 0,
		}, this.requestState);
	}

	toggleFullscreen(){
		const node = this.canvasRef.current && this.canvasRef.current.parentNode;
		if(!node){
			return;
		}
		if(document.fullscreenElement){
			document.exitFullscreen();
		}else if(node.requestFullscreen){
			node.requestFullscreen();
		}
	}

	renderLayerButton(key, label){
		return (
			<button
				type="button"
				className={`planetarium-chip ${this.state.layers[key] ? 'is-on' : ''}`}
				onClick={()=>this.toggleLayer(key)}
			>
				{label}
			</button>
		);
	}

	renderSelected(){
		const item = this.state.selected;
		if(!item){
			return <div className="planetarium-empty">点击太阳、月亮、行星、二十八宿或北斗星点查看详情</div>;
		}
		return (
			<div className="planetarium-detail">
				<h3>{item.displayName || bodyName(item)}</h3>
				<div><span>图层</span><strong>{item.layer || 'body'}</strong></div>
				<div><span>高度</span><strong>{formatDeg(item.altitudeAppa)}</strong></div>
				<div><span>方位</span><strong>{formatDeg(item.azimuth)}</strong></div>
				<div><span>赤经</span><strong>{formatDeg(item.ra)}</strong></div>
				<div><span>赤纬</span><strong>{formatDeg(item.decl)}</strong></div>
				<div><span>黄经</span><strong>{formatDeg(item.lon)}</strong></div>
				<div><span>黄纬</span><strong>{formatDeg(item.lat)}</strong></div>
				<div><span>星等</span><strong>{item.mag === undefined || item.mag === null ? '--' : item.mag}</strong></div>
				<div><span>星座/宿</span><strong>{item.sign || item.su28 || '--'}</strong></div>
				<div><span>宫位</span><strong>{item.house || '--'}</strong></div>
			</div>
		);
	}

	render(){
		const { metrics, data } = this.state;
		return (
			<div className="horosa-planetarium-page">
				<aside className="planetarium-side planetarium-left">
					<div className="planetarium-title">
						<small>地表观测天空</small>
						<h2>天文馆</h2>
					</div>
					<div className="planetarium-time">
						<div>{this.state.time.format('YYYY-MM-DD HH:mm:ss')}</div>
						<small>{this.state.time.zone} · {data && data.observer ? data.observer.locationName : '未命名地点'}</small>
					</div>
					<div className="planetarium-section">
						<div className="planetarium-section-title">时间播放</div>
						<div className="planetarium-speed-grid">
							<button type="button" className={this.state.speed === 0 ? 'is-active' : ''} onClick={()=>this.changeSpeed(0)}>暂停</button>
							<button type="button" className={this.state.speed === 1 ? 'is-active' : ''} onClick={()=>this.changeSpeed(1)}>1x</button>
							<button type="button" className={this.state.speed === 60 ? 'is-active' : ''} onClick={()=>this.changeSpeed(60)}>60x</button>
							<button type="button" className={this.state.speed === 86400 ? 'is-active' : ''} onClick={()=>this.changeSpeed(86400)}>日进</button>
							<button type="button" className={this.state.speed === 2592000 ? 'is-active' : ''} onClick={()=>this.changeSpeed(2592000)}>月进</button>
							<button type="button" className={this.state.speed === 31536000 ? 'is-active' : ''} onClick={()=>this.changeSpeed(31536000)}>年进</button>
						</div>
						<div className="planetarium-actions">
							<button type="button" onClick={this.jumpNow}>回到命盘时间</button>
							<button type="button" onClick={this.toggleFullscreen}>全屏</button>
						</div>
					</div>
					<div className="planetarium-section">
						<div className="planetarium-section-title">图层</div>
						<div className="planetarium-layer-grid">
							{this.renderLayerButton('stars', '恒星')}
							{this.renderLayerButton('bodies', '星体')}
							{this.renderLayerButton('horizon', '地平/子午')}
							{this.renderLayerButton('equator', '天赤道')}
							{this.renderLayerButton('ecliptic', '黄道')}
							{this.renderLayerButton('zodiac', '十二宫')}
							{this.renderLayerButton('houses', '宫位')}
							{this.renderLayerButton('su28', '二十八宿')}
							{this.renderLayerButton('beidou', '北斗')}
						</div>
					</div>
				</aside>
				<main className="planetarium-stage">
					<canvas ref={this.canvasRef} className="planetarium-canvas" />
					{this.state.loading ? <div className="planetarium-status">同步天空中...</div> : null}
					{this.state.error ? <div className="planetarium-status is-error">{this.state.error}</div> : null}
				</main>
				<aside className="planetarium-side planetarium-right">
					<div className="planetarium-section">
						<div className="planetarium-section-title">观测状态</div>
						<div className="planetarium-metrics">
							<div><span>FPS</span><strong>{metrics.fps}</strong></div>
							<div><span>网格</span><strong>{metrics.meshes}</strong></div>
							<div><span>载入</span><strong>{metrics.loadMs} ms</strong></div>
							<div><span>恒星</span><strong>{metrics.catalogCount}</strong></div>
						</div>
					</div>
					<div className="planetarium-section">
						<div className="planetarium-section-title">天体详情</div>
						{this.renderSelected()}
					</div>
				</aside>
			</div>
		);
	}
}

export default PlanetariumBabylon;
