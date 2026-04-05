import React from 'react';
import loader from '@monaco-editor/loader';

const DEFAULT_OPTIONS = {
	automaticLayout: true,
	minimap: {
		enabled: false,
	},
	scrollBeyondLastLine: false,
	fontSize: 13,
};

function MonacoField(props){
	const {
		value,
		onChange,
		defaultLanguage = 'plaintext',
		language,
		height = '200px',
		options = {},
		beforeMount,
		loading = '编辑器加载中...',
	} = props || {};
	const containerRef = React.useRef(null);
	const editorRef = React.useRef(null);
	const monacoRef = React.useRef(null);
	const subscriptionRef = React.useRef(null);

	React.useEffect(()=>{
		let disposed = false;
		loader.init().then((monaco)=>{
			if(disposed || !containerRef.current){
				return;
			}
			monacoRef.current = monaco;
			if(typeof beforeMount === 'function'){
				beforeMount(monaco);
			}
			editorRef.current = monaco.editor.create(containerRef.current, {
				value: value == null ? '' : `${value}`,
				language: language || defaultLanguage,
				...DEFAULT_OPTIONS,
				...(options || {}),
			});
			subscriptionRef.current = editorRef.current.onDidChangeModelContent(()=>{
				if(typeof onChange === 'function'){
					onChange(editorRef.current.getValue());
				}
			});
		}).catch((err)=>{
			if(!disposed){
				console.error('monaco.init.failed', err);
			}
		});
		return ()=>{
			disposed = true;
			if(subscriptionRef.current){
				subscriptionRef.current.dispose();
				subscriptionRef.current = null;
			}
			if(editorRef.current){
				editorRef.current.dispose();
				editorRef.current = null;
			}
		};
	}, []);

	React.useEffect(()=>{
		if(!editorRef.current){
			return;
		}
		const nextValue = value == null ? '' : `${value}`;
		if(editorRef.current.getValue() !== nextValue){
			editorRef.current.setValue(nextValue);
		}
	}, [value]);

	React.useEffect(()=>{
		if(!editorRef.current || !monacoRef.current){
			return;
		}
		const model = editorRef.current.getModel();
		if(model && (language || defaultLanguage)){
			monacoRef.current.editor.setModelLanguage(model, language || defaultLanguage);
		}
	}, [language, defaultLanguage]);

	React.useEffect(()=>{
		if(editorRef.current){
			editorRef.current.updateOptions({
				...DEFAULT_OPTIONS,
				...(options || {}),
			});
		}
	}, [options]);

	return (
		<div style={{ position: 'relative', minHeight: height }}>
			<div ref={containerRef} style={{ height, width: '100%' }} />
			{!editorRef.current ? (
				<div style={{
					position: 'absolute',
					inset: 0,
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'center',
					color: '#7d7d7d',
					fontSize: 12,
					pointerEvents: 'none',
					background: '#fafafa',
					border: '1px solid #f0f0f0',
				}}
				>
					{loading}
				</div>
			) : null}
		</div>
	);
}

export default MonacoField;
