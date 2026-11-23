// 天文馆 · Babylon 场景渲染器(类本体:构造与销毁;其余方法按职责拆在同目录 renderer*.js,类后 mixinMethods 挂回原型)。
// 只被 components/planetarium/PlanetariumBabylon.js 与同目录 babylon/ 下的兄弟模块引用。
import { pointerLocalRatio } from '../../../utils/zoomDomain';
import { BABYLON, STAR_MAG_LIMIT_MAX, DEFAULT_LAYERS } from './constants';
import { LabelUploadQueue } from './labelUploadQueue';
import { mixinMethods } from '../../../utils/mixinMethods';
import { rendererSceneMethods } from './rendererScene';
import { rendererViewMethods } from './rendererView';
import { rendererProjectionMethods } from './rendererProjection';
import { rendererStarMethods } from './rendererStars';
import { rendererGridMethods } from './rendererGrids';
import { rendererAsterismMethods } from './rendererAsterisms';
import { rendererInteractionMethods } from './rendererInteraction';

export class PlanetariumRenderer {
	constructor(canvas, onPick, onMetrics, onInteraction){
		this.canvas = canvas;
		this.onPick = onPick;
		this.onMetrics = onMetrics;
		this.onInteraction = onInteraction;
		this.engine = new BABYLON.Engine(canvas, true, {
			preserveDrawingBuffer: false,
			stencil: false,
			antialias: true,
			powerPreference: 'high-performance',
			adaptToDeviceRatio: true,
		});
		this.scene = new BABYLON.Scene(this.engine);
		// 引擎的指针坐标是「clientX − 画布 rect.left」(视觉域),而它自己的拾取(POINTERPICK 命中行星 / 亮星)与 createPickingRay 都按
		// 画布本地 CSS 坐标(布局域)解释 —— 壳缩放档下两者差 z 倍,点不中 / 点到别的天体(100% 档重合,看不出来)。
		// 在引擎更新指针位置之后立刻按「画布布局宽 ÷ rect 宽」折回;接口缺席(引擎升级改了内部结构)就退到 pickXY() 里只修本类自己的射线。
		this._pointerDomainPatched = false;
		try{
			const im = this.scene._inputManager;
			if(im && typeof im._updatePointerPosition === 'function'){
				const origUpdate = im._updatePointerPosition.bind(im);
				im._updatePointerPosition = (evt)=>{
					origUpdate(evt);
					const k = pointerLocalRatio(canvas);
					if(k.kx !== 1 || k.ky !== 1){
						im._pointerX *= k.kx;
						im._pointerY *= k.ky;
						im._unTranslatedPointerX = im._pointerX;
						im._unTranslatedPointerY = im._pointerY;
					}
				};
				this._pointerDomainPatched = true;
			}
		}catch(e){ this._pointerDomainPatched = false; }
		this.scene.clearColor = new BABYLON.Color4(0.008, 0.012, 0.026, 1);
		this.scene.ambientColor = new BABYLON.Color3(0.12, 0.16, 0.3);
		this.groups = [];
		this.pickMeshes = [];
		this.bodyMeshes = {};
		this.projectableMeshes = [];
		this.projectableLines = [];
		this.followMeshes = [];
		this.starPcs = null;
		this.starMesh = null;
		this.starCount = 0;
		this.starCatalog = [];
		this.starBuildPending = false;
		this.lastData = null;
		// 名牌纹理画完隔两帧再上传(见 labelUploadQueue.js);渲染循环每帧 tick
		this._labelUploads = new LabelUploadQueue();
		this._surfaceTextures = new Map();   // 日月行星表面贴图,跨全量重建留用(见 createSurfaceTexture)
		this._surfaceMats = [];              // 正挂着留用贴图的材质,清场前要先摘
		this.disposed = false;
		this._asterismBuildToken = 0;
		this._asterismBuildJob = null;
		this.viewMode = 'ground';
		this.layers = {...DEFAULT_LAYERS};
		// 星等过滤上限(默认 = 全 BSC5 上限,等价不过滤 → 零回归)。mag > magLimit 的恒星粒子 alpha=0 隐藏。
		this.magLimit = STAR_MAG_LIMIT_MAX;
		// 角距测量(默认关 → 零回归):开关 + 已记起点(单位方向向量)+ 连线/标记 mesh。
		this.measureMode = false;
		this.measureFirst = null;
		this.measureMeshes = [];
		this.onMeasure = null;
		this.onSkyReadout = null;
		this.initScene();
	}

	dispose(){
		this.disposed = true;
		window.removeEventListener('resize', this.resizeHandler);
		if(this.wheelHandler){
			this.canvas.removeEventListener('wheel', this.wheelHandler);
		}
		if(this.pointerDownHandler){
			this.canvas.removeEventListener('pointerdown', this.pointerDownHandler);
			this.canvas.removeEventListener('pointermove', this.pointerMoveHandler);
			this.canvas.removeEventListener('pointerup', this.pointerUpHandler);
			this.canvas.removeEventListener('pointercancel', this.pointerUpHandler);
		}
		this.clearMeasureMeshes();
		this.clearData();
		this.disposeSurfaceTextures();
		this._labelUploads.clear();
		if(this.sky){
			this.sky.dispose(false, true);
		}
		if(this.skyTexture){
			this.skyTexture.dispose();
			this.skyTexture = null;
		}
		if(this.horizonGlow){
			this.horizonGlow.dispose(false, true);
		}
		if(this.groundOccluder){
			this.groundOccluder.dispose(false, true);
		}
		if(this.horizonPanorama){
			this.horizonPanorama.dispose(false, true);
		}
		if(this.horizonMist){
			this.horizonMist.dispose(false, true);
		}
		if(this.horizonMistTexture){
			this.horizonMistTexture.dispose();
			this.horizonMistTexture = null;
		}
		(this.landscapeMeshes || []).forEach((mesh)=>mesh.dispose(false, true));
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
mixinMethods(PlanetariumRenderer, rendererSceneMethods, rendererViewMethods, rendererProjectionMethods, rendererStarMethods, rendererGridMethods, rendererAsterismMethods, rendererInteractionMethods);   // 方法按职责拆在同目录各文件里(见各文件头),挂回原型
