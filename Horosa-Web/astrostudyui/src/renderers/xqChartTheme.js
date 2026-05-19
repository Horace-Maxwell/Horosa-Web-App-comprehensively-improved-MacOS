export const XQ_CHART_CLASS = 'xq-chart-renderer';
export const XQ_ASTRO_CHART_CLASS = 'xq-chart-renderer-astro';
export const XQ_INDIA_CHART_CLASS = 'xq-chart-renderer-india';

export function getChartRendererClass(kind){
	if(kind === 'india'){
		return `${XQ_CHART_CLASS} ${XQ_INDIA_CHART_CLASS}`;
	}
	return `${XQ_CHART_CLASS} ${XQ_ASTRO_CHART_CLASS}`;
}
