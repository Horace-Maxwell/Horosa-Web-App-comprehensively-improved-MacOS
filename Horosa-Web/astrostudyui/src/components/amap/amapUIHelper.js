function isLocalRuntime(){
	if(typeof window === 'undefined' || !window.location){
		return false;
	}
	const host = `${window.location.hostname || ''}`.toLowerCase();
	return window.location.protocol === 'file:'
		|| host === '127.0.0.1'
		|| host === 'localhost';
}

export function canUseAMapUI(){
	if(typeof window === 'undefined'){
		return false;
	}
	if(!window.AMapUI || typeof window.AMapUI.loadUI !== 'function'){
		return false;
	}
	if(isLocalRuntime()){
		return false;
	}
	return true;
}

export function safeLoadAMapUI(modules, onLoaded, onFallback){
	if(!canUseAMapUI()){
		if(onFallback){
			onFallback();
		}
		return false;
	}
	try{
		window.AMapUI.loadUI(modules, (...args)=>{
			if(onLoaded){
				onLoaded(...args);
			}
		});
		return true;
	}catch(e){
		console.warn('[AMapUI] loadUI failed, fallback applied.', e);
		if(onFallback){
			onFallback();
		}
		return false;
	}
}
