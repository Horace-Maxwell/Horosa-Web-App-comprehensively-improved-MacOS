// 浮层几何判据体(单源):由 headless 双引擎闸 audit_popup_geometry.py 注入页面执行。
// 占位符:__KEY__ 页面 key;__RTZ__ 运行时换档目标('' = 不换,沿用加载定档);__SCROLLS__ 左栏滚动分位('0,0.5,1');
//        __LIMIT__ 每个滚动位最多测几个控件;__CAST__ '1' = 进页先起盘。
// 方法学(每条都对应一类假报):
//   ① 触发器与浮层必须**开后同一拍**量 —— 聚焦会让浏览器把输入框滚进视野,开前量的触发器位置是陈旧的;
//   ② 只测**真能点中**的触发器(elementFromPoint 命中自身),被滚动容器裁掉的不算;
//   ③ 量之前必须「恰 1 个可见浮层且进场动画已结束」(slide-up 动画期间 scaleY 会改 rect);
//   ④ 关闭用 mousedown(rc-select 监听的是 window mousedown,click 关不掉 → 残留浮层被下一拍误量);
//   ⑤ 关不干净 = dirty,该行作废不计入结论;
//   ⑥ 合法落点三态:正下 / 翻转到正上 / 两边都放不下时夹在视口内。其余一律 MISALIGNED;贴着触发器却伸出视口、而另一侧放得下 = OVERFLOW-NOFLIP。
const KEY='__KEY__', RTZ='__RTZ__', SCROLLS='__SCROLLS__', LIMIT=parseInt('__LIMIT__',10)||8, CAST='__CAST__';
const sleep=(ms)=>new Promise(r=>setTimeout(r,ms));
const raf2=()=>new Promise(r=>{ let done=false; const fin=()=>{ if(!done){ done=true; r(); } }; requestAnimationFrame(()=>requestAnimationFrame(fin)); setTimeout(fin,400); });
// 裁判不能被引擎模型骗:双引擎闸的 E2 shim 改写的是**页面看到的** getBoundingClientRect,判据自身走 window.__REAL_GBCR
// (shim 前保存的原始函数)取真实渲染坐标;该全局缺席时退回原生读数。
const GB=(el)=>(typeof window.__REAL_GBCR==='function'?window.__REAL_GBCR.call(el):el.getBoundingClientRect());
const R=(el)=>{ const r=GB(el); return {l:+r.left.toFixed(1),t:+r.top.toFixed(1),r:+r.right.toFixed(1),b:+r.bottom.toFixed(1),w:+r.width.toFixed(1),h:+r.height.toFixed(1)}; };
for(let i=0;i<80&&!document.querySelector('#mainContent');i++) await sleep(500);
window.dispatchEvent(new CustomEvent('horosa:navigate',{detail:{key:KEY}}));
await sleep(5500);
if(CAST==='1'){ const b=[...document.querySelectorAll('button')].find(x=>/^(起\s*盘|起\s*课|起\s*卦|起\s*局|排\s*盘)$/.test((x.textContent||'').trim())); if(b){ b.click(); await sleep(6000); } }
const out={key:KEY, loadZoom:document.documentElement.style.zoom||'1', rtz:RTZ, rows:[], rafAlive:null};
{ let n=0; const t0=performance.now(); await new Promise(res=>{ const tick=()=>{ n++; if(performance.now()-t0<300) requestAnimationFrame(tick); }; requestAnimationFrame(tick); setTimeout(res,380); }); out.rafAlive=n; }
if(RTZ){ if(typeof window.__HOROSA_APPLY_SHELL_ZOOM==='function'){ window.__HOROSA_APPLY_SHELL_ZOOM(parseFloat(RTZ)); out.rtApplied='shellFn'; } else { document.documentElement.style.zoom=RTZ; window.dispatchEvent(new Event('resize')); out.rtApplied='styleOnly'; } await sleep(2500); }
const z=parseFloat(document.documentElement.style.zoom)||1; out.z=z;
out.diag=(typeof window.__HOROSA_ALIGN_DIAG__==='function')?window.__HOROSA_ALIGN_DIAG__():null;
out.vp={iw:innerWidth, ih:innerHeight, cw:document.documentElement.clientWidth, ch:document.documentElement.clientHeight};
const visibleDropdowns=()=>[...document.querySelectorAll('.ant-select-dropdown')].filter(d=>{ if(d.classList.contains('ant-select-dropdown-hidden')) return false; const r=GB(d); if(r.height<=4||r.width<=4) return false; return true; });
const animating=(d)=>/-(enter|appear|leave)(-|$| )/.test(d.className)&&/-active/.test(d.className) || /ant-slide-up-(enter|appear|leave)/.test(d.className);
async function closeAll(){
  for(let k=0;k<3;k++){
    const tgt=document.querySelector('.ant-layout-header')||document.body;
    tgt.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,cancelable:true,view:window,button:0}));
    tgt.dispatchEvent(new MouseEvent('mouseup',{bubbles:true,cancelable:true,view:window,button:0}));
    let waited=0; while(waited<1500){ if(visibleDropdowns().length===0) return true; await sleep(100); waited+=100; }
  }
  return visibleDropdowns().length===0;
}
const hittable=(sel)=>{ const host=sel.closest('.ant-select'); if(!host||host.classList.contains('ant-select-disabled')) return false; const r=GB(sel); if(r.width<40||r.height<8) return false; if(r.top<0||r.bottom>innerHeight||r.left<0||r.right>innerWidth) return false; const el=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); return !!el&&host.contains(el); };
const scrollerOf=(el)=>{ let p=el.parentElement; while(p&&p!==document.body){ const cs=getComputedStyle(p); if(/(auto|scroll)/.test(cs.overflowY)&&p.scrollHeight>p.clientHeight+20) return p; p=p.parentElement; } return null; };
const ancestorsScroll=(el)=>{ const m=[]; let p=el; while(p){ m.push([p, p.scrollTop||0, p.scrollLeft||0]); p=p.parentElement; } m.push([document.scrollingElement||document.documentElement, (document.scrollingElement||document.documentElement).scrollTop, 0]); return m; };
const first=[...document.querySelectorAll('.ant-select-selector')].find(s=>scrollerOf(s));
const scroller=first?scrollerOf(first):null;
out.scroller=scroller?{cls:(scroller.className||'').toString().slice(0,48), ch:scroller.clientHeight, sh:scroller.scrollHeight}:null;
const fracs=SCROLLS.split(',').map(Number).filter(x=>isFinite(x));
const tol=Math.max(3, 3*z);
for(const f of (fracs.length?fracs:[0])){
  if(scroller){ scroller.scrollTop=Math.round(f*(scroller.scrollHeight-scroller.clientHeight)); await sleep(350); }
  let sels=[...document.querySelectorAll('.ant-select-selector')].filter(hittable);
  if(sels.length>LIMIT){ const step=sels.length/LIMIT; sels=Array.from({length:LIMIT},(_,i)=>sels[Math.floor(i*step)]); }
  for(const sel of sels){
    const row={f, label:''};
    const okClosed=await closeAll(); row.dirtyBefore=!okClosed; if(!okClosed){ row.verdict='DIRTY'; out.rows.push(row); continue; }
    if(!hittable(sel)){ row.verdict='SKIP-not-hittable'; out.rows.push(row); continue; }
    const host=sel.closest('.ant-select'); row.label=(host.textContent||'').trim().slice(0,14);
    const pre=R(host); const scPre=ancestorsScroll(host);
    sel.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,cancelable:true,view:window,button:0}));
    sel.dispatchEvent(new MouseEvent('mouseup',{bubbles:true,cancelable:true,view:window,button:0}));
    sel.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window,button:0}));
    let dd=null, waited=0;
    while(waited<2200){ await sleep(120); waited+=120; const v=visibleDropdowns(); if(v.length===1&&!animating(v[0])){ dd=v[0]; break; } }
    await raf2();
    const v=visibleDropdowns(); row.visCount=v.length;
    if(v.length!==1){ row.verdict=(v.length===0?'NO-POPUP':'DIRTY'); out.rows.push(row); continue; }
    dd=v[0];
    const T=R(host), D=R(dd);                       // ① 同一拍
    row.trigPre=pre; row.trig=T; row.dd=D; row.styleLeft=dd.style.left; row.styleTop=dd.style.top; row.ddParent=(dd.parentElement&&dd.parentElement.parentElement===document.body)?'body':((dd.parentElement&&(dd.parentElement.className||'').toString().slice(0,30))||'?');
    row.trigMoved=[+(T.l-pre.l).toFixed(1), +(T.t-pre.t).toFixed(1)];
    row.scrollDelta=scPre.map(([p,st,sl])=>({p, dt:(p.scrollTop||0)-st, dl:(p.scrollLeft||0)-sl})).filter(o=>o.dt||o.dl).map(o=>({cls:(o.p.className||o.p.tagName||'').toString().slice(0,40), dt:o.dt, dl:o.dl}));
    const gap=4*z;
    const dx=D.l-T.l, dyB=D.t-T.b, dyA=T.t-D.b;
    row.dx=+dx.toFixed(1); row.dyBelow=+dyB.toFixed(1); row.dyAbove=+dyA.toFixed(1);
    const xOk=Math.abs(dx)<=tol || (D.r<=innerWidth+1 && Math.abs(D.r-innerWidth)<=tol+8*z && dx<0);   // adjustX 把右缘贴回视口也合法
    const below=Math.abs(dyB-gap)<=tol, above=Math.abs(dyA-gap)<=tol;
    const fitsBelow=T.b+gap+D.h<=innerHeight, fitsAbove=T.t-gap-D.h>=0;
    const inView=D.t>=-1&&D.b<=innerHeight+1;
    row.fits={below:fitsBelow, above:fitsAbove};
    // 落点贴着触发器还不够:伸出视口而另一侧放得下 = 翻转逻辑没生效(放大档下滚动祖先可视区被算矮时的病),选项被窗口边切掉、够不着。
    if(xOk&&below) row.verdict=(D.b-innerHeight>2&&fitsAbove)?'OVERFLOW-NOFLIP':'OK-below';
    else if(xOk&&above) row.verdict=(D.t<-2&&fitsBelow)?'OVERFLOW-NOFLIP':'OK-above';
    else if(xOk&&!fitsBelow&&!fitsAbove&&inView) row.verdict='OK-clamped';
    else row.verdict='MISALIGNED';
    out.rows.push(row);
  }
}
await closeAll();
// ── 气泡类(Popover):左栏时间字段(单击弹出整块日期时间选择器,placement=rightTop)。判据 = 与触发器**相邻**:
//    水平间隙 ≤ 24·z 且纵向有交叠(或被夹在视口内);飘到盘面中间 = 既不相邻也不交叠。
{
  if(scroller){ scroller.scrollTop=0; await sleep(300); }
  const visiblePopovers=()=>[...document.querySelectorAll('.ant-popover')].filter(d=>{ if(d.classList.contains('ant-popover-hidden')) return false; const r=GB(d); return r.width>20&&r.height>20; });
  const trigs=[...document.querySelectorAll('[data-quick-time-trigger="1"]')].filter(t=>{ const r=GB(t); if(r.width<40||r.top<0||r.bottom>innerHeight) return false; const el=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); return !!el&&t.contains(el); }).slice(0,2);
  for(const t of trigs){
    const row={f:0, kind:'popover', label:'时间:'+(t.textContent||'').trim().slice(0,10)};
    t.click();
    let waited=0, pv=[]; while(waited<2500){ await sleep(150); waited+=150; pv=visiblePopovers(); if(pv.length===1&&!/-(enter|appear)/.test(pv[0].className)) break; }
    await raf2(); pv=visiblePopovers(); row.visCount=pv.length;
    if(pv.length!==1){ row.verdict=pv.length?'DIRTY':'NO-POPUP'; out.rows.push(row); document.body.dispatchEvent(new MouseEvent('mousedown',{bubbles:true})); document.body.click(); await sleep(600); continue; }
    const inner=pv[0].querySelector('.ant-popover-inner')||pv[0];
    const T=R(t), D=R(inner); row.trig=T; row.dd=D; row.trigPre=T; row.trigMoved=[0,0]; row.scrollDelta=[];
    const gapX=Math.max(0, D.l-T.r, T.l-D.r), gapY=Math.max(0, D.t-T.b, T.t-D.b);
    const overlapY=Math.min(T.b,D.b)-Math.max(T.t,D.t), overlapX=Math.min(T.r,D.r)-Math.max(T.l,D.l);
    row.dx=+gapX.toFixed(1); row.dyBelow=+gapY.toFixed(1); row.dyAbove=+overlapY.toFixed(1);
    const inView=D.t>=-1&&D.b<=innerHeight+1&&D.l>=-1&&D.r<=innerWidth+1;
    const lim=24*Math.max(1,z)+4;
    const adjacentH=gapX<=lim&&(overlapY>0||(inView&&(Math.abs(D.b-innerHeight)<=8*z||Math.abs(D.t)<=8*z)));
    const adjacentV=gapY<=lim&&(overlapX>0||inView);
    row.verdict=(adjacentH||adjacentV)?'OK-adjacent':'MISALIGNED';
    out.rows.push(row);
    const hdr=document.querySelector('.ant-layout-header')||document.body; hdr.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,cancelable:true,view:window})); hdr.dispatchEvent(new MouseEvent('mouseup',{bubbles:true,cancelable:true,view:window})); hdr.click(); await sleep(700);
  }
}
out.summary=out.rows.reduce((m,r)=>{ m[r.verdict]=(m[r.verdict]||0)+1; return m; },{});
return JSON.stringify(out);
