import { buildQimenXiangTipObj } from '../QimenXiangDoc';

function joinTextBlocks(tipObj){
	if(!tipObj || !Array.isArray(tipObj.blocks)){
		return '';
	}
	return tipObj.blocks
		.filter((block)=>block && block.type === 'text')
		.map((block)=>`${block.text || ''}`)
		.join('\n');
}

describe('QimenXiangDoc 简体化', ()=>{
	test('八门条目正文应输出简体', ()=>{
		const tipObj = buildQimenXiangTipObj('door', '景门');
		expect(tipObj).toBeTruthy();
		expect(tipObj.title).toBe('景门');
		const content = joinTextBlocks(tipObj);
		expect(content).toContain('亮丽');
		expect(content).not.toContain('亮麗');
	});

	test('九星条目应转换洩等繁体字', ()=>{
		const tipObj = buildQimenXiangTipObj('star', '天冲');
		expect(tipObj).toBeTruthy();
		const content = joinTextBlocks(tipObj);
		expect(content).toContain('早泄');
		expect(content).not.toContain('早洩');
	});

	test('不应把乾误转为干', ()=>{
		const tipObj = buildQimenXiangTipObj('door', '开门');
		expect(tipObj).toBeTruthy();
		const content = joinTextBlocks(tipObj);
		expect(content).toContain('乾，亥，火墓');
		expect(content).not.toContain('干，亥，火墓');
	});
});
