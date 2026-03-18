import { cloneElement, isValidElement, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, } from 'react';
import { createPortal } from 'react-dom';

const VIEWPORT_PADDING = 12;
const FLOAT_OFFSET = 14;

function clamp(num, min, max){
	return Math.min(Math.max(num, min), max);
}

function getViewportSize(){
	if(typeof window === 'undefined'){
		return {
			width: 1440,
			height: 900,
		};
	}
	return {
		width: window.innerWidth || 1440,
		height: window.innerHeight || 900,
	};
}

function getAnchorFromEvent(evt, currentTarget){
	if(evt && Number.isFinite(evt.clientX) && Number.isFinite(evt.clientY)){
		return {
			x: evt.clientX,
			y: evt.clientY,
		};
	}
	if(currentTarget && currentTarget.getBoundingClientRect){
		const rect = currentTarget.getBoundingClientRect();
		return {
			x: rect.left + rect.width / 2,
			y: rect.top + rect.height / 2,
		};
	}
	const viewport = getViewportSize();
	return {
		x: viewport.width / 2,
		y: viewport.height / 2,
	};
}

function calcOverlayPosition(anchor, overlaySize){
	const viewport = getViewportSize();
	const width = overlaySize.width || 0;
	const height = overlaySize.height || 0;
	const maxLeft = Math.max(VIEWPORT_PADDING, viewport.width - width - VIEWPORT_PADDING);
	const maxTop = Math.max(VIEWPORT_PADDING, viewport.height - height - VIEWPORT_PADDING);
	const preferredLeft = anchor.x - width / 2;
	const canPlaceAbove = anchor.y - FLOAT_OFFSET - height >= VIEWPORT_PADDING;
	const preferredTop = canPlaceAbove
		? anchor.y - FLOAT_OFFSET - height
		: anchor.y + FLOAT_OFFSET;
	return {
		left: clamp(preferredLeft, VIEWPORT_PADDING, maxLeft),
		top: clamp(preferredTop, VIEWPORT_PADDING, maxTop),
	};
}

function mergeHandler(originalHandler, nextHandler){
	return (evt)=>{
		if(typeof originalHandler === 'function'){
			originalHandler(evt);
		}
		if(typeof nextHandler === 'function'){
			nextHandler(evt);
		}
	};
}

function normalizeTip(tip){
	if(!tip){
		return null;
	}
	if(typeof tip === 'string'){
		return {
			title: '',
			tips: `${tip}`.split(/\r?\n/),
		};
	}
	if(Array.isArray(tip)){
		return {
			title: '',
			tips: tip.map((item)=>`${item}`),
		};
	}
	if(typeof tip === 'object'){
		const title = tip.title ? `${tip.title}` : '';
		const tips = Array.isArray(tip.tips)
			? tip.tips.map((item)=>`${item}`)
			: (tip.tips !== undefined && tip.tips !== null && tip.tips !== ''
				? [`${tip.tips}`]
				: []);
		return {
			...tip,
			title,
			tips,
		};
	}
	return null;
}

export function isMeaningEnabled(flag){
	return flag === 1 || flag === true;
}

function stripHeadingText(line){
	return `${line || ''}`
		.replace(/^#+\s*/, '')
		.replace(/^\*\*(.*)\*\*$/, '$1')
		.trim();
}

function isHeadingLine(line){
	return /^#+\s+/.test(`${line || ''}`.trim());
}

function renderInlineBold(text, keyPrefix = 'txt'){
	const str = `${text || ''}`;
	const parts = str.split(/(\*\*[^*]+\*\*)/g);
	return parts.filter((item)=>item !== '').map((part, idx)=>{
		if(/^\*\*[^*]+\*\*$/.test(part)){
			return (
				<strong key={`${keyPrefix}_b_${idx}`}>
					{part.substring(2, part.length - 2)}
				</strong>
			);
		}
		return <span key={`${keyPrefix}_t_${idx}`}>{part}</span>;
	});
}

export function renderMeaningContent(tip){
	const normalizedTip = normalizeTip(tip);
	if(!normalizedTip){
		return null;
	}
	const lines = [];
	if(normalizedTip.title){
		lines.push((
			<div key="title" style={{fontSize: 17, lineHeight: '24px', fontWeight: 700, color: '#1f1f1f'}}>
				{normalizedTip.title}
			</div>
		));
		lines.push((
			<div key="title_sep" style={{borderTop: '1px solid #d9d9d9', margin: '6px 0 8px'}} />
		));
	}
	const tipLines = normalizedTip.tips;
	tipLines.forEach((line, idx)=>{
		const oneLine = `${line || ''}`;
		const trimmed = oneLine.trim();
		if(trimmed === '=='){
			lines.push((
				<div key={`sep_${idx}`} style={{borderTop: '1px solid #e8e8e8', margin: '6px 0'}} />
			));
			return;
		}
		if(trimmed === ''){
			lines.push(<div key={`blank_${idx}`} style={{height: 4}} />);
			return;
		}
		if(isHeadingLine(trimmed)){
			lines.push((
				<div key={`heading_wrap_${idx}`} style={{marginTop: 4, marginBottom: 6}}>
					<div style={{fontSize: 14, lineHeight: '20px', fontWeight: 700, color: '#262626'}}>
						{renderInlineBold(stripHeadingText(trimmed), `heading_${idx}`)}
					</div>
					<div style={{borderTop: '1px solid #efefef', marginTop: 4}} />
				</div>
			));
			return;
		}
		lines.push((
			<div
				key={`line_${idx}`}
				style={{marginBottom: 3, fontSize: 13, lineHeight: '21px', color: '#262626', whiteSpace: 'pre-wrap'}}
			>
				{renderInlineBold(oneLine, `line_${idx}`)}
			</div>
		));
	});
	if(lines.length === 0){
		return null;
	}
	return (
		<div
			style={{
				width: 'min(560px, calc(100vw - 28px))',
				maxWidth: 'min(560px, calc(100vw - 28px))',
				maxHeight: 'min(62vh, calc(100vh - 28px))',
				overflowY: 'auto',
				overflowX: 'hidden',
				whiteSpace: 'normal',
			}}
		>
			{lines}
		</div>
	);
}

function MeaningOverlayTrigger({ node, content, }){
	const overlayRef = useRef(null);
	const hideTimerRef = useRef(null);
	const [visible, setVisible] = useState(false);
	const [anchor, setAnchor] = useState({x: 0, y: 0});
	const [overlayPosition, setOverlayPosition] = useState({
		left: VIEWPORT_PADDING,
		top: VIEWPORT_PADDING,
	});

	const clearHideTimer = useCallback(()=>{
		if(hideTimerRef.current){
			clearTimeout(hideTimerRef.current);
			hideTimerRef.current = null;
		}
	}, []);

	const showOverlay = useCallback((evt)=>{
		clearHideTimer();
		setAnchor(getAnchorFromEvent(evt, evt && evt.currentTarget));
		setVisible(true);
	}, [clearHideTimer]);

	const moveOverlay = useCallback((evt)=>{
		if(!visible){
			return;
		}
		setAnchor(getAnchorFromEvent(evt, evt && evt.currentTarget));
	}, [visible]);

	const hideOverlaySoon = useCallback(()=>{
		clearHideTimer();
		hideTimerRef.current = setTimeout(()=>{
			setVisible(false);
		}, 100);
	}, [clearHideTimer]);

	useLayoutEffect(()=>{
		if(!visible || !overlayRef.current){
			return;
		}
		const rect = overlayRef.current.getBoundingClientRect();
		setOverlayPosition(calcOverlayPosition(anchor, {
			width: rect.width,
			height: rect.height,
		}));
	}, [anchor, content, visible]);

	useEffect(()=>{
		return ()=>{
			clearHideTimer();
		};
	}, [clearHideTimer]);

	const triggerNode = useMemo(()=>{
		const injectProps = {
			onMouseEnter: showOverlay,
			onMouseMove: moveOverlay,
			onMouseLeave: hideOverlaySoon,
			onFocus: showOverlay,
			onBlur: hideOverlaySoon,
			style: {
				...(node && node.props && node.props.style ? node.props.style : {}),
				cursor: 'help',
			},
		};
		if(isValidElement(node)){
			return cloneElement(node, {
				...injectProps,
				onMouseEnter: mergeHandler(node.props && node.props.onMouseEnter, showOverlay),
				onMouseMove: mergeHandler(node.props && node.props.onMouseMove, moveOverlay),
				onMouseLeave: mergeHandler(node.props && node.props.onMouseLeave, hideOverlaySoon),
				onFocus: mergeHandler(node.props && node.props.onFocus, showOverlay),
				onBlur: mergeHandler(node.props && node.props.onBlur, hideOverlaySoon),
			});
		}
		return (
			<span
				onMouseEnter={showOverlay}
				onMouseMove={moveOverlay}
				onMouseLeave={hideOverlaySoon}
				onFocus={showOverlay}
				onBlur={hideOverlaySoon}
				style={{cursor: 'help'}}
			>
				{node}
			</span>
		);
	}, [hideOverlaySoon, moveOverlay, node, showOverlay]);

	const overlayNode = visible && typeof document !== 'undefined'
		? createPortal(
			<div
				ref={overlayRef}
				onMouseEnter={clearHideTimer}
				onMouseLeave={hideOverlaySoon}
				style={{
					position: 'fixed',
					left: overlayPosition.left,
					top: overlayPosition.top,
					zIndex: 5000,
					background: '#fff',
					border: '1px solid rgba(0, 0, 0, 0.08)',
					borderRadius: 10,
					boxShadow: '0 10px 34px rgba(0, 0, 0, 0.18)',
					padding: '12px 14px',
					pointerEvents: 'auto',
					boxSizing: 'border-box',
				}}
			>
				{content}
			</div>,
			document.body,
		)
		: null;

	return (
		<>
			{triggerNode}
			{overlayNode}
		</>
	);
}

export function wrapWithMeaning(node, enabled, tip){
	if(!enabled || !tip){
		return node;
	}
	const content = renderMeaningContent(tip);
	if(!content){
		return node;
	}
	return <MeaningOverlayTrigger node={node} content={content} />;
}
