// 占星地图 · 落点解读(自备简体中文,基于公版占星含义原创撰写)。
// 键:行星 const 值;角:Asc/Desc/MC/IC。

const PLANET_THEME = {
	Sun: '自我、活力与“被看见”的渴望',
	Moon: '情绪、归属感与内在的安全需求',
	Mercury: '思考、表达、学习与人际往来',
	Venus: '情感、审美、愉悦与人缘财禄',
	Mars: '行动力、竞争心、勇气与冲劲',
	Jupiter: '扩张、机遇、信念与顺势成长',
	Saturn: '责任、磨练、结构与现实限制',
	Uranus: '变动、自由、突破与意外转折',
	Neptune: '梦想、灵性、慈悲与界线消融',
	Pluto: '权力、深度、危机与彻底蜕变',
	'North Node': '需要去成长的方向与命运课题',
	'South Node': '熟悉的旧习惯与天生的惯性',
	Chiron: '旧伤的触动与疗愈转化的契机',
	'Dark Moon': '阴影、深层欲望与未被驯服的部分',
	'Purple Clouds': '隐微的福泽与精神层面的气运',
};

const ANGLE_THEME = {
	MC: '这股能量会投向事业、名声与人生方向,在公众与外界面前格外鲜明',
	IC: '这股能量沉入家庭、根基与内心私域,影响你的安顿、归属与晚年',
	Asc: '这股能量融入你的自我呈现、身体状态与第一印象,在此地你活得更像“这颗星”',
	Desc: '这股能量集中在关系、伴侣与合作上,往往通过身边的人映照出来',
};

const ANGLE_NAME = { MC: '中天线', IC: '天底线', Asc: '上升线', Desc: '下降线' };

export function getInterp(planet, angleConst) {
	const p = PLANET_THEME[planet];
	const a = ANGLE_THEME[angleConst];
	if (!p || !a) return '';
	return `在此地的${ANGLE_NAME[angleConst] || ''}上,${a};主题关乎${p}。`;
}

export { PLANET_THEME, ANGLE_THEME, ANGLE_NAME };
