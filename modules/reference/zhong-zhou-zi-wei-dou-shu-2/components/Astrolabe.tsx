
import React, { useState, useMemo, useEffect } from 'react';
import { ChartData, HEAVENLY_STEMS, AppSettings } from '../types';
import PalaceCard, { LayoutType } from './PalaceCard';
import { getSiHua, getFlowState, calculateFlowStars, STEMS, getElementColor } from '../services/ziweiMath';
import { ChevronLeft, ChevronRight, Settings, RotateCcw, LayoutGrid, Star } from 'lucide-react';

interface AstrolabeProps {
  data: ChartData;
  onReset: () => void;
  onTimeTravel: (dayDelta: number, hourDelta: number) => void;
  onOpenSettings: () => void;
  settings: AppSettings;
}

type ViewLevel = 'birth' | 'daxian' | 'year' | 'month' | 'day' | 'hour';
export type ViewMode = 'sanhe' | 'feixing';

const Astrolabe: React.FC<AstrolabeProps> = ({ data, onReset, onTimeTravel, onOpenSettings, settings }) => {
  const [viewMode, setViewMode] = useState<ViewMode>('sanhe');
  const [flowDate, setFlowDate] = useState(new Date());
  const [flowTimeIdx, setFlowTimeIdx] = useState(0); 
  const [focusedPalaceIndex, setFocusedPalaceIndex] = useState<number | null>(null);
  const [activeLevel, setActiveLevel] = useState<ViewLevel>('birth');

  const birthYear = parseInt(data.solarDateStr.match(/\d{4}/)?.[0] || new Date().getFullYear().toString());
  const birthDate = new Date(birthYear, 0, 1); 

  // Reset active level when switching modes if the current level is not allowed
  useEffect(() => {
      if (viewMode === 'feixing') {
          if (['month', 'day', 'hour'].includes(activeLevel)) {
              setActiveLevel('year'); // Default to Year or Birth if filtered out
          }
      }
  }, [viewMode, activeLevel]);

  // Calculate Flow State
  const flowState = useMemo(() => {
     return getFlowState(data, flowDate, birthDate, flowTimeIdx, settings);
  }, [data, flowDate, flowTimeIdx, birthYear, settings]);

  // Calculate Flow Stars (New)
  const flowStarsMap = useMemo(() => {
      return calculateFlowStars(data, flowState, settings, activeLevel);
  }, [data, flowState, settings, activeLevel]);

  // Si Hua Layers Calculation
  const siHuaLayers = useMemo(() => {
      return {
          birth: getSiHua(data.yearStemIndex, settings),
          daxian: getSiHua(flowState.stems.daxian, settings),
          liunian: getSiHua(flowState.stems.liunian, settings),
          liuyue: getSiHua(flowState.stems.liuyue, settings),
          liuri: getSiHua(flowState.stems.liuri, settings),
          liushi: getSiHua(flowState.stems.liushi, settings)
      };
  }, [data.yearStemIndex, flowState.stems, settings]);

  // Calculate Ming Palace Si Hua (Specifically for Flying Star Mode)
  const mingSiHua = useMemo(() => {
      const mingPalace = data.palaces.find(p => p.index === data.mingPalaceIndex);
      if (!mingPalace) return {};
      const stemIdx = STEMS.indexOf(mingPalace.heavenlyStem);
      return getSiHua(stemIdx, settings);
  }, [data.palaces, data.mingPalaceIndex, settings]);

  // Calculated Flying Si Hua based on selected palace (San He usage mainly)
  const flyingSiHua = useMemo(() => {
      if (focusedPalaceIndex === null) return undefined;
      const p = data.palaces.find(x => x.index === focusedPalaceIndex);
      if (!p) return undefined;
      const stemIdx = STEMS.indexOf(p.heavenlyStem);
      if (stemIdx === -1) return undefined;
      return getSiHua(stemIdx, settings);
  }, [focusedPalaceIndex, data.palaces, settings]);

  // Hierarchy
  const LEVELS: ViewLevel[] = ['birth', 'daxian', 'year', 'month', 'day', 'hour'];
  const currentLevelIdx = LEVELS.indexOf(activeLevel);

  // Handlers
  const handleLevelSelect = (level: ViewLevel) => {
      const idx = LEVELS.indexOf(level);
      // Can only select levels up to current + 1
      if (idx > currentLevelIdx + 1) return;
      setActiveLevel(level);
  };

  const handleArrowClick = (delta: number) => {
      if (activeLevel === 'birth') return;
      
      const newDate = new Date(flowDate);
      switch(activeLevel) {
          case 'daxian': newDate.setFullYear(newDate.getFullYear() + (delta * 10)); break;
          case 'year': newDate.setFullYear(newDate.getFullYear() + delta); break;
          case 'month': newDate.setMonth(newDate.getMonth() + delta); break;
          case 'day': newDate.setDate(newDate.getDate() + delta); break;
          case 'hour':
              let newT = flowTimeIdx + delta;
              if (newT > 11) { newT = 0; newDate.setDate(newDate.getDate() + 1); }
              else if (newT < 0) { newT = 11; newDate.setDate(newDate.getDate() - 1); }
              setFlowTimeIdx(newT);
              setFlowDate(newDate);
              return; 
      }
      setFlowDate(newDate);
  };

  const getPalace = (idx: number) => data.palaces.find(p => p.index === idx)!;
  
  // Helper to determine markers for a palace
  const getMarkers = (idx: number) => ({
      isDaXian: idx === flowState.daXianIndex,
      isLiuNian: idx === flowState.liuNianIndex,
      isLiuYue: idx === flowState.liuYueIndex,
      isLiuRi: idx === flowState.liuRiIndex,
      isLiuShi: idx === flowState.liuShiIndex,
  });

  const handleReset = () => {
      setFocusedPalaceIndex(null);
      setActiveLevel('birth');
      onReset();
  };

  // Helper to calculate flying arrows (Zi Hua and Xiang Xin Li)
  const getFlyingArrows = (palaceIdx: number) => {
      const p = getPalace(palaceIdx);
      const stemIdx = STEMS.indexOf(p.heavenlyStem);
      const siHua = getSiHua(stemIdx, settings); // { 'StarName': '禄'|'忌'... }
      
      const ziHua: ('禄'|'权'|'科'|'忌')[] = [];
      const xiangXin: ('禄'|'权'|'科'|'忌')[] = [];

      // 1. Zi Hua (Self Transformation) - Check stars in CURRENT palace
      const selfStars = [...p.majorStars, ...p.auxStars, ...p.badStars]; // Include relevant stars
      selfStars.forEach(star => {
          if (siHua[star.name]) {
              ziHua.push(siHua[star.name]);
          }
      });

      // 2. Xiang Xin (Transformation to Opposite) - Check stars in OPPOSITE palace
      const oppIdx = (palaceIdx + 6) % 12;
      const oppPalace = getPalace(oppIdx);
      const oppStars = [...oppPalace.majorStars, ...oppPalace.auxStars, ...oppPalace.badStars];
      oppStars.forEach(star => {
          if (siHua[star.name]) {
              xiangXin.push(siHua[star.name]);
          }
      });
      
      // Sort to ensure consistent order (Lu -> Quan -> Ke -> Ji)
      const order = { '禄': 1, '权': 2, '科': 3, '忌': 4 };
      ziHua.sort((a, b) => order[a] - order[b]);
      xiangXin.sort((a, b) => order[a] - order[b]);

      return { ziHua, xiangXin };
  };

  // Helper to determine specific layout type (Corners vs Edges)
  const getLayoutType = (idx: number): LayoutType => {
      if (idx === 5) return 'corner-tl'; // Si (Top Left)
      if (idx === 6 || idx === 7) return 'top'; // Wu, Wei
      if (idx === 8) return 'corner-tr'; // Shen (Top Right)
      if (idx === 9 || idx === 10) return 'right'; // You, Xu
      if (idx === 11) return 'corner-br'; // Hai (Bottom Right)
      if (idx === 0 || idx === 1) return 'bottom'; // Zi, Chou
      if (idx === 2) return 'corner-bl'; // Yin (Bottom Left)
      return 'left'; // Mao, Chen
  };

  const renderPalace = (gridIndex: number) => {
      const p = getPalace(gridIndex);
      // Inject Flow Stars
      const pWithFlow = {
          ...p,
          flowStars: flowStarsMap[p.index] || []
      };

      const { ziHua, xiangXin } = getFlyingArrows(p.index);
      const layoutType = getLayoutType(p.index);

      return (
          <PalaceCard 
             data={pWithFlow} 
             viewMode={viewMode}
             flowMarkers={getMarkers(p.index)} 
             siHuaLayers={siHuaLayers}
             mingSiHua={mingSiHua}
             flowIndices={{
                 daXianMingIdx: flowState.daXianIndex,
                 liuNianMingIdx: flowState.liuNianIndex,
                 liuYueMingIdx: flowState.liuYueIndex,
                 liuRiMingIdx: flowState.liuRiIndex,
                 liuShiMingIdx: flowState.liuShiIndex,
                 flowYearStem: flowState.stems.liunian
             }}
             isSelected={focusedPalaceIndex === p.index}
             onClick={() => setFocusedPalaceIndex(prev => prev === p.index ? null : p.index)}
             highlightedSiHua={flyingSiHua}
             activeLevel={activeLevel}
             displaySettings={settings.display}
             // Flying Star Props - Passed in both modes
             flyingArrows={{ ziHua, xiangXin }}
             layoutType={layoutType}
          />
      );
  };

  // SVG Line Generation
  const getInnerAnchor = (idx: number): string => {
      const anchors: Record<number, string> = {
          5:  "25% 25%",     // Top-Left Corner Inner
          6:  "37.5% 25%",   // Top Edge Inner
          7:  "62.5% 25%",   // Top Edge Inner
          8:  "75% 25%",     // Top-Right Corner Inner
          
          9:  "75% 37.5%",   // Right Edge Inner
          10: "75% 62.5%",   // Right Edge Inner
          11: "75% 75%",     // Bottom-Right Corner Inner
          
          0:  "62.5% 75%",   // Bottom Edge Inner
          1:  "37.5% 75%",   // Bottom Edge Inner
          2:  "25% 75%",     // Bottom-Left Corner Inner
          
          3:  "25% 62.5%",   // Left Edge Inner
          4:  "25% 37.5%"    // Left Edge Inner
      };
      return anchors[idx];
  };

  const renderLines = () => {
      if (focusedPalaceIndex === null || !settings.display.showArrows) return null;
      if (viewMode === 'feixing') return null; // Hide relationship arrows in Fei Xing mode for clarity

      const selfIdx = focusedPalaceIndex;
      const oppIdx = (selfIdx + 6) % 12;
      const triIdx1 = (selfIdx + 4) % 12;
      const triIdx2 = (selfIdx + 8) % 12;

      // Points
      const p1 = getInnerAnchor(selfIdx);
      const p2 = getInnerAnchor(triIdx1);
      const p3 = getInnerAnchor(triIdx2);
      const pOpp = getInnerAnchor(oppIdx);

      // Parse percentages
      const parse = (s: string) => {
          const [x, y] = s.split(' ').map(v => v.replace('%', ''));
          return { x: `${x}%`, y: `${y}%` };
      }
      const c1 = parse(p1);
      const c2 = parse(p2);
      const c3 = parse(p3);
      const cOpp = parse(pOpp);

      return (
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-20 overflow-visible">
              <defs>
                  {/* Arrow Marker */}
                  <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#9ca3af" />
                  </marker>
              </defs>
              
              {/* Line to Opposite (Si Zheng) */}
              <line 
                 x1={c1.x} y1={c1.y} 
                 x2={cOpp.x} y2={cOpp.y} 
                 stroke="#9ca3af" 
                 strokeWidth="1.5" 
                 strokeDasharray="4 4"
                 strokeOpacity="0.8"
                 markerEnd="url(#arrow)"
              />
              
              {/* Line to Triangle 1 (San Fang) */}
               <line 
                 x1={c1.x} y1={c1.y} 
                 x2={c2.x} y2={c2.y} 
                 stroke="#9ca3af" 
                 strokeWidth="1.5" 
                 strokeDasharray="4 4"
                 strokeOpacity="0.8"
                 markerEnd="url(#arrow)"
              />

              {/* Line to Triangle 2 (San Fang) */}
               <line 
                 x1={c1.x} y1={c1.y} 
                 x2={c3.x} y2={c3.y} 
                 stroke="#9ca3af" 
                 strokeWidth="1.5" 
                 strokeDasharray="4 4"
                 strokeOpacity="0.8"
                 markerEnd="url(#arrow)"
              />
          </svg>
      );
  };

  const renderBaZi = (label: string, value: string) => {
      const stem = value.split('')[0];
      const branch = value.split('')[1];
      return (
          <div className="flex flex-col items-center">
              <span className="text-[10px] text-gray-400">{label}</span>
              <span className={`text-lg font-bold font-serif leading-none mt-1 ${getElementColor(stem)}`}>{stem}</span>
              <span className={`text-lg font-bold font-serif leading-none ${getElementColor(branch)}`}>{branch}</span>
          </div>
      );
  };

  // Define Bottom Bar Items
  const controlItems = [
     { id: 'daxian', label: flowState.labels.daxian, show: true },
     { id: 'year', label: flowState.labels.year, show: true },
     { id: 'month', label: flowState.labels.month, show: viewMode === 'sanhe' },
     { id: 'day', label: flowState.labels.day, show: viewMode === 'sanhe' },
     { id: 'hour', label: flowState.labels.hour, show: viewMode === 'sanhe' },
  ];

  return (
    <div className="w-full h-screen flex flex-col bg-gray-50 overflow-hidden">
       {/* Top Bar */}
       <div className="relative flex justify-between items-center px-4 py-2 bg-white shadow-sm shrink-0 border-b border-gray-200">
         
         {/* Left Side: Buttons */}
         <div className="flex items-center z-10">
            {/* View Mode Switcher */}
            <div className="flex bg-gray-100 p-0.5 rounded-lg border border-gray-200">
                <button 
                  onClick={() => setViewMode('sanhe')}
                  className={`flex items-center gap-1.5 px-3 py-1 text-xs font-bold rounded-md transition-all ${viewMode === 'sanhe' ? 'bg-white text-ziwei-blue shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                >
                    <LayoutGrid size={14} /> 三合
                </button>
                <button 
                  onClick={() => setViewMode('feixing')}
                  className={`flex items-center gap-1.5 px-3 py-1 text-xs font-bold rounded-md transition-all ${viewMode === 'feixing' ? 'bg-white text-ziwei-purple shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                >
                    <Star size={14} /> 飞星
                </button>
            </div>
         </div>

         {/* Center: Title */}
         <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <h2 className="text-lg text-ziwei-text font-bold tracking-widest">紫微斗数</h2>
         </div>

         {/* Right Side: Settings */}
         <div className="flex gap-3 z-10">
            <button onClick={onOpenSettings} className="flex items-center gap-1 text-sm text-ziwei-blue hover:text-blue-700">
                <Settings size={16} /> <span className="hidden sm:inline">设定</span>
            </button>
         </div>
       </div>

       {/* Grid Container with increased margin */}
       <div className="flex-1 grid grid-cols-4 grid-rows-4 gap-0 p-0.5 bg-ziwei-grid m-5 sm:m-8 rounded-sm border border-ziwei-grid relative shadow-lg">
          
          {/* Overlay Lines */}
          {renderLines()}

          {renderPalace(5)}
          {renderPalace(6)}
          {renderPalace(7)}
          {renderPalace(8)}

          {renderPalace(4)}
          
          <div className="col-span-2 row-span-2 bg-white flex flex-col relative p-2 overflow-hidden border-r border-b border-ziwei-grid">
             <div className="flex-1 flex flex-col justify-start z-10 gap-2">
                <div className="text-center pt-2">
                    <h1 className="text-2xl font-bold text-gray-800 tracking-[0.2em]">{data.name || '无名氏'}</h1>
                    <div className="flex justify-center gap-4 text-sm mt-2 font-medium text-ziwei-gold">
                        <span>{data.yinYang}{data.gender}</span>
                        <span>{data.bureau}</span>
                        <span>命主: {data.mingZhu}</span>
                        <span>身主: {data.shenZhu}</span>
                        <span>子斗: {data.ziDou}</span>
                    </div>
                </div>
                
                {/* Dates Section */}
                <div className="text-center space-y-1">
                   <p className="text-sm font-medium text-ziwei-purple font-serif">{data.lunarDateStr}</p>
                   <p className="text-sm font-medium text-gray-600 font-mono">{data.solarDateStr}</p>
                   {data.trueSolarDateStr && (
                       <p className="text-xs font-bold text-amber-600 font-mono">{data.trueSolarDateStr}</p>
                   )}
                </div>

                {/* Fei Xing Legend (Visible only in Fei Xing Mode) */}
                {viewMode === 'feixing' && (
                    <div className="flex justify-center gap-4 text-[11px] font-bold mt-2">
                        <div className="flex items-center gap-1">
                            <span className="text-ziwei-green">禄</span> <span className="text-ziwei-red">忌</span> <span className="text-ziwei-blue">科</span> <span className="text-ziwei-purple">权</span>
                        </div>
                    </div>
                )}
                
                <div className="flex-1"></div>

                {/* BaZi Section */}
                <div className="flex justify-around items-center border-y border-gray-100 py-2 bg-gray-50 mx-4 rounded mb-6">
                   {renderBaZi('年柱', data.baZi.year)}
                   {renderBaZi('月柱', data.baZi.month)}
                   {renderBaZi('日柱', data.baZi.day)}
                   {renderBaZi('时柱', data.baZi.time)}
                </div>
             </div>
             <div className="absolute top-1 left-2 text-[10px] text-gray-300">东南</div>
             <div className="absolute bottom-1 right-2 text-[10px] text-gray-300">西北</div>
          </div>

          {renderPalace(9)}
          {renderPalace(3)}
          {renderPalace(10)}
          {renderPalace(2)}
          {renderPalace(1)}
          {renderPalace(0)}
          {renderPalace(11)}
       </div>

       {/* Bottom Control Bar */}
       <div className="bg-gray-200 border-t border-gray-300 flex divide-x divide-gray-300 h-12 shrink-0">
           
           {controlItems.filter(i => i.show).map((item, idx) => {
             const levelKey = item.id as ViewLevel;
             const hierarchyIdx = idx + 1; 
             const isDisabled = hierarchyIdx > currentLevelIdx + 1;
             const isActive = activeLevel === levelKey;

             return (
             <div 
                key={item.id} 
                onClick={() => !isDisabled && handleLevelSelect(levelKey)}
                className={`flex-1 flex items-center justify-between px-1 transition-colors relative 
                   ${isActive ? 'bg-white shadow-inner' : isDisabled ? 'opacity-40 cursor-not-allowed bg-gray-200' : 'bg-[#e5e7eb] hover:bg-gray-100 cursor-pointer'}
                `}
             >
                {/* Arrow Left */}
                <button 
                    disabled={!isActive}
                    onClick={(e) => { e.stopPropagation(); handleArrowClick(-1); }}
                    className={`p-1 ${isActive ? 'text-gray-500 hover:text-ziwei-blue active:scale-90' : 'text-gray-300 cursor-default'}`}
                >
                    <ChevronLeft size={14} />
                </button>
                
                {/* Label */}
                <div className="flex flex-col items-center">
                   <span className={`text-[10px] leading-tight font-bold ${isActive ? 'text-ziwei-blue' : 'text-gray-700'}`}>
                       {item.label.split(' ')[0]}
                   </span>
                   {item.label.split(' ')[1] && (
                       <span className="text-[9px] text-gray-500 leading-tight">
                           {item.label.split(' ').slice(1).join(' ')}
                       </span>
                   )}
                </div>

                {/* Arrow Right */}
                <button 
                    disabled={!isActive}
                    onClick={(e) => { e.stopPropagation(); handleArrowClick(1); }}
                    className={`p-1 ${isActive ? 'text-gray-500 hover:text-ziwei-blue active:scale-90' : 'text-gray-300 cursor-default'}`}
                >
                    <ChevronRight size={14} />
                </button>

                {/* Overlay to block interactions if disabled */}
                {isDisabled && <div className="absolute inset-0 bg-gray-200/50 cursor-not-allowed" />}
             </div>
           )})}
           
           <button onClick={handleReset} className="w-12 bg-gray-300 flex items-center justify-center hover:bg-ziwei-blue hover:text-white transition-colors">
               <RotateCcw size={18} />
           </button>
       </div>
    </div>
  );
};

export default Astrolabe;
