const fs = require('fs');
const path = require('path');

const TARGETS = [
	{
		file: 'node_modules/quill/blots/scroll.js',
		pattern: /\n\s*this\.domNode\.addEventListener\('DOMNodeInserted', function\(\) \{\}\);/g,
	},
	{
		file: 'node_modules/quill/dist/quill.js',
		pattern: /\n\s*_this\.domNode\.addEventListener\('DOMNodeInserted', function \(\) \{\}\);/g,
	},
	{
		file: 'node_modules/quill/dist/quill.core.js',
		pattern: /\n\s*_this\.domNode\.addEventListener\('DOMNodeInserted', function \(\) \{\}\);/g,
	},
];

function patchFile(target){
	const fullPath = path.resolve(__dirname, '..', target.file);
	if(!fs.existsSync(fullPath)){
		return { file: target.file, status: 'missing' };
	}
	const before = fs.readFileSync(fullPath, 'utf8');
	const after = before.replace(target.pattern, '');
	if(after === before){
		return { file: target.file, status: 'unchanged' };
	}
	fs.writeFileSync(fullPath, after, 'utf8');
	return { file: target.file, status: 'patched' };
}

const results = TARGETS.map(patchFile);
const changed = results.filter((item)=>item.status === 'patched').length;
const unchanged = results.filter((item)=>item.status === 'unchanged').length;
const missing = results.filter((item)=>item.status === 'missing').length;

console.log(`[patch-quill] patched=${changed} unchanged=${unchanged} missing=${missing}`);
