export function filterTechniqueKeysBySource(activeSource, techniqueOptions, selectedTechniqueKeys){
	if(!activeSource){
		return [];
	}
	const allowed = new Set((techniqueOptions || []).map((item)=>item && item.value).filter(Boolean));
	return (selectedTechniqueKeys || []).filter((item)=>allowed.has(item));
}

export function getTechniqueContextMode(selectedTechniqueKeys){
	return (selectedTechniqueKeys || []).length ? 'meta' : 'full';
}
