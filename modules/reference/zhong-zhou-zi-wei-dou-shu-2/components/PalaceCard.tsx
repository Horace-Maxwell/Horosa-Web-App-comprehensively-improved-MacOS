
import React from 'react';
import { PalaceData, Star } from '../types';
import { PALACE_NAMES, PALACE_ABBR } from '../services/ziweiMath';
import { ViewMode } from './Astrolabe';

type ViewLevel = 'birth' | 'daxian' | 'year' | 'month' | 'day' | 'hour';

export type LayoutType = 'corner-tl' | 'top' | 'corner-tr' | 'right' | 'corner-br' | 'bottom' | 'corner-bl' | 'left';

interface PalaceCardProps {
  data: PalaceData;
  viewMode: ViewMode;
  flowMarkers: {
     isDaXian: boolean;
     isLiuNian: boolean;
     isLiuYue: boolean;
     isLiuRi: boolean;
     isLiuShi: boolean;
  };
  siHuaLayers: {
      birth: Record<string, string>;
      daxian: Record<string, string>;
      liunian: Record<string, string>;
      liuyue: Record<string, string>;
      liuri: Record<string, string>;
      liushi: Record<string, string>;
  };
  mingSiHua: Record<string, '禄'|'权'|'科'|'忌'>;
  flowIndices?: {
      daXianMingIdx: number;
      liuNianMingIdx: number;
      liuYueMingIdx: number;
      liuRiMingIdx: number;
      liuShiMingIdx: number;
      flowYearStem: number;
  };
  onClick?: () => void;
  isSelected?: boolean;
  highlightedSiHua?: Record<string, '禄'|'权'|'科'|'忌'>;
  activeLevel: ViewLevel;
  displaySettings: {
     showLiuNian: boolean;
     showXiaoXian: boolean;
     showLiuYue: boolean;
     compactMode: boolean;
     showFlowStars: boolean;
     showFlowMa: boolean;
     showFlowHuoLing: boolean;
     showFlowHongXi: boolean;
     showFlowChangQu: boolean;
  };
  // New Props for Flying Arrows
  flyingArrows?: {
      ziHua: ('禄'|'权'|'科'|'忌')[];
      xiangXin: ('禄'|'权'|'科'|'忌')[];
  };
  layoutType?: LayoutType;
}

const PURPLE_STARS = ['天魁', '天钺', '左辅', '右弼', '文曲', '文昌'];
const BLACK_STARS = ['擎羊', '陀罗', '火星', '铃星', '地空', '地劫'];

const PalaceCard: React.FC<PalaceCardProps> = ({ 
    data, 
    viewMode,
    flowMarkers, 
    siHuaLayers, 
    mingSiHua, 
    flowIndices, 
    onClick, 
    isSelected,
    highlightedSiHua,
    activeLevel,
    displaySettings,
    flyingArrows,
    layoutType = 'bottom'
}) => {
  
  // 1. Filter Stars based on View Mode
  let starsToRender: Star[] = [];
  
  if (viewMode === 'feixing') {
      // Fei Xing Mode: Major + Aux + Bad only (Filter out minor, gods)
      starsToRender = [
          ...data.majorStars,
          ...data.auxStars,
          ...data.badStars
      ];
  } else {
      // San He Mode: Show all (ordered)
      starsToRender = [
        ...data.majorStars,
        ...data.auxStars,
        ...data.badStars,
        ...data.minorStars
      ];
  }

  // Group 12 Gods (Only for San He Mode)
  const changShengGod = viewMode === 'sanhe' ? data.godsStars.find(s => s.type === 'chang') : null;
  const boShiGod = viewMode === 'sanhe' ? data.godsStars.find(s => s.type === 'bo') : null;
  const suiJianGod = viewMode === 'sanhe' ? data.godsStars.find(s => s.type === 'sui') : null;
  const jiangQianGod = viewMode === 'sanhe' ? data.godsStars.find(s => s.type === 'jiang') : null;

  // Hierarchy Logic
  const LEVELS = ['birth', 'daxian', 'year', 'month', 'day', 'hour'];
  const levelIdx = LEVELS.indexOf(activeLevel);
  const showDaXian = levelIdx >= 1;
  const showYear = levelIdx >= 2;
  const showMonth = levelIdx >= 3;
  const showDay = levelIdx >= 4;
  const showHour = levelIdx >= 5;
  
  const getSiHuaColor = (mod: string) => {
      switch(mod) {
          case '禄': return 'ziwei-green';
          case '权': return 'ziwei-purple';
          case '科': return 'ziwei-blue';
          case '忌': return 'ziwei-red';
          default: return 'gray-500';
      }
  };

  const getSiHuaBg = (mod: string) => {
      switch(mod) {
          case '禄': return 'bg-ziwei-green';
          case '权': return 'bg-ziwei-purple';
          case '科': return 'bg-ziwei-blue';
          case '忌': return 'bg-ziwei-red';
          default: return 'bg-gray-500';
      }
  };

  // --- Arrow Rendering Helper ---
  const renderFlyingArrow = (type: 'ziHua' | 'xiangXin', mods: ('禄'|'权'|'科'|'忌')[]) => {
      if (mods.length === 0) return null;

      const arrowSize = 12;
      
      // Map colors
      const getColor = (m: string) => {
          if (m === '禄') return '#34C759';
          if (m === '权') return '#AF52DE';
          if (m === '科') return '#007AFF';
          if (m === '忌') return '#FF3B30';
          return '#999';
      };

      // Determine rotation and positioning classes
      // Zi Hua (Out): Points AWAY from box.
      // Xiang Xin (In): Points TOWARDS center (so from edge inward).
      // Arrow base: points UP (0 deg).
      
      let rotation = 0;
      let posClass = '';
      
      switch (layoutType) {
          case 'corner-tl': // Top Left
              if (type === 'ziHua') { // Out from Top-Left corner (Diagonal)
                  posClass = '-top-[6px] -left-[6px] flex-row';
                  rotation = 315; // -45 deg
              } else { // In to Bottom-Right corner (Diagonal towards center)
                  posClass = '-bottom-[6px] -right-[6px] flex-row';
                  rotation = 135;
              }
              break;
          case 'top': // Top Row
              if (type === 'ziHua') { 
                  posClass = '-top-[8px] left-1/2 -translate-x-1/2 flex-row'; 
                  rotation = 0; 
              } else { 
                  posClass = '-bottom-[8px] left-1/2 -translate-x-1/2 flex-row'; 
                  rotation = 180; 
              }
              break;
          case 'corner-tr': // Top Right
              if (type === 'ziHua') { // Out from Top-Right corner (Diagonal)
                  posClass = '-top-[6px] -right-[6px] flex-row';
                  rotation = 45; 
              } else { // In to Bottom-Left corner (Diagonal towards center)
                  posClass = '-bottom-[6px] -left-[6px] flex-row';
                  rotation = 225;
              }
              break;
          case 'right': // Right Column
               if (type === 'ziHua') { 
                   posClass = '-right-[8px] top-1/2 -translate-y-1/2 flex-col'; 
                   rotation = 90; 
               } else { 
                   posClass = '-left-[8px] top-1/2 -translate-y-1/2 flex-col'; 
                   rotation = 270; 
               } 
               break;
          case 'corner-br': // Bottom Right
              if (type === 'ziHua') { // Out from Bottom-Right corner (Diagonal)
                  posClass = '-bottom-[6px] -right-[6px] flex-row';
                  rotation = 135; 
              } else { // In to Top-Left corner (Diagonal towards center)
                  posClass = '-top-[6px] -left-[6px] flex-row';
                  rotation = 315; 
              }
              break;
          case 'bottom': // Bottom Row
               if (type === 'ziHua') { 
                   posClass = '-bottom-[8px] left-1/2 -translate-x-1/2 flex-row'; 
                   rotation = 180; 
               } else { 
                   posClass = '-top-[8px] left-1/2 -translate-x-1/2 flex-row'; 
                   rotation = 0; 
               }
               break;
          case 'corner-bl': // Bottom Left
              if (type === 'ziHua') { // Out from Bottom-Left corner (Diagonal)
                  posClass = '-bottom-[6px] -left-[6px] flex-row';
                  rotation = 225; 
              } else { // In to Top-Right corner (Diagonal towards center)
                  posClass = '-top-[6px] -right-[6px] flex-row';
                  rotation = 45; 
              }
              break;
          case 'left': // Left Column
               if (type === 'ziHua') { 
                   posClass = '-left-[8px] top-1/2 -translate-y-1/2 flex-col'; 
                   rotation = 270; 
               } else { 
                   posClass = '-right-[8px] top-1/2 -translate-y-1/2 flex-col'; 
                   rotation = 90; 
               } 
               break;
      }

      return (
          <div className={`absolute z-30 flex gap-[2px] pointer-events-none ${posClass}`}>
              {mods.map((mod, i) => (
                  <svg key={i} width={arrowSize} height={arrowSize} viewBox="0 0 12 12" style={{ transform: `rotate(${rotation}deg)` }}>
                      <path d="M6 0 L12 8 L9 8 L9 12 L3 12 L3 8 L0 8 Z" fill={getColor(mod)} stroke="white" strokeWidth="0.5" />
                  </svg>
              ))}
          </div>
      );
  };

  const renderStar = (star: Star, index: number) => {
    // Si Hua Triggers
    const flyMod = highlightedSiHua?.[star.name]; // From clicking a palace (Flying Star)
    const birthMod = siHuaLayers.birth[star.name]; // Birth Year Si Hua
    const mingMod = mingSiHua[star.name]; // Ming Palace Si Hua (Self)

    // Flow Si Hua (San He only usually, or strictly defined for Fei Xing)
    // In Fei Xing, we prioritize Birth & Ming Si Hua.
    const daxianMod = siHuaLayers.daxian[star.name];
    const liunianMod = siHuaLayers.liunian[star.name];
    const liuyueMod = siHuaLayers.liuyue[star.name];
    const liuriMod = siHuaLayers.liuri[star.name];
    const liushiMod = siHuaLayers.liushi[star.name];

    // Determine Star Text Color & Box Styles
    let nameClasses = 'text-gray-800'; 
    // Always apply padding to prevent shift when highlighted background is added
    let containerClasses = 'rounded-[2px] py-[1px]'; 

    if (viewMode === 'feixing') {
        // --- FEI XING STYLING ---
        if (star.type === 'major') nameClasses = 'text-ziwei-red'; // Major Red
        else nameClasses = 'text-ziwei-purple'; // Others Purple
        
        // Flying Star Highlight (from Click)
        if (flyMod) {
             nameClasses = 'text-white';
             containerClasses += ` ${getSiHuaBg(flyMod)} shadow-sm -mx-[1px]`;
        }
    } else {
        // --- SAN HE STYLING ---
        if (flyMod) {
            nameClasses = 'text-white';
            containerClasses += ` ${getSiHuaBg(flyMod)} shadow-sm -mx-[1px]`;
        } else {
            // Updated Coloring Rules based on user request
            if (star.type === 'major') {
                nameClasses = 'text-ziwei-red';
            } else if (PURPLE_STARS.includes(star.name)) {
                nameClasses = 'text-ziwei-purple';
            } else if (BLACK_STARS.includes(star.name)) {
                nameClasses = 'text-gray-900'; // Black/Dark Grey
            } else {
                nameClasses = 'text-blue-600'; // All others Blue
            }
        }
    }

    // --- Si Hua Badges Logic ---
    const renderSiHuaBadges = () => {
        if (viewMode === 'feixing') {
            // Fei Xing: Specifically show Birth (Solid) and Ming (Border)
            // Fixed slots to ensure Ming Si Hua is below Birth Si Hua position
            return (
                <div className="flex flex-col mt-0.5 gap-[2px] items-center">
                    {/* Slot 1: Birth Year Si Hua */}
                    <div className="w-[14px] h-[14px]">
                        {birthMod && (
                            <div className={`w-full h-full flex items-center justify-center ${getSiHuaBg(birthMod)} rounded-[2px]`}>
                                <span className="text-white text-[10px] font-bold leading-none">{birthMod}</span>
                            </div>
                        )}
                    </div>
                    {/* Slot 2: Ming Palace Si Hua */}
                    <div className="w-[14px] h-[14px]">
                        {mingMod && (
                            <div className={`w-full h-full flex items-center justify-center border border-${getSiHuaColor(mingMod)} bg-transparent rounded-[2px]`}>
                                <span className={`text-${getSiHuaColor(mingMod)} text-[10px] font-bold leading-none`}>{mingMod}</span>
                            </div>
                        )}
                    </div>
                </div>
            );
        } else {
            // San He: Show stacked dots/squares for time layers
             const slots = [
                { show: true, mod: birthMod || star.modifier, color: 'bg-ziwei-red' },
                { show: showDaXian, mod: daxianMod, color: 'bg-green-600' },
                { show: showYear, mod: liunianMod, color: 'bg-blue-500' },
                { show: showMonth, mod: liuyueMod, color: 'bg-amber-500' },
                { show: showDay, mod: liuriMod, color: 'bg-purple-500' },
                { show: showHour, mod: liushiMod, color: 'bg-red-500' }
            ];
            const visibleSlots = slots.filter(s => s.show);
            if (visibleSlots.every(s => !s.mod)) return <div className="mt-0.5 h-[12px]"></div>;

            return (
                <div className="flex flex-col mt-0.5 gap-[1px] items-center">
                    {visibleSlots.map((slot, idx) => (
                        <div key={idx} className="w-[12px] h-[12px]">
                            {slot.mod ? (
                                <span className={`flex items-center justify-center w-full h-full ${slot.color} text-white text-[10px] rounded-[2px] leading-none`}>
                                    {slot.mod}
                                </span>
                            ) : null}
                        </div>
                    ))}
                </div>
            );
        }
    };

    return (
      <div key={`${star.name}-${index}`} className={`flex flex-col items-center mr-0.5 mb-1 w-4 ${flyMod ? 'z-10' : ''}`}>
        <div className={`flex flex-col items-center text-[13px] font-bold leading-none tracking-tighter transition-colors duration-200 ${nameClasses} ${containerClasses}`}>
             {star.name.split('').map((char, i) => <span key={i}>{char}</span>)}
             
             {/* Brightness - Always render in San He, adjust color if highlighted */}
             {viewMode === 'sanhe' && star.brightness && (
                 <span className={`text-[9px] mt-[1px] scale-90 ${flyMod ? 'text-white/90' : 'text-gray-400'}`}>
                     {star.brightness}
                 </span>
             )}
        </div>
        {renderSiHuaBadges()}
      </div>
    );
  };

  // Flow Stars (Bottom Right in San He)
  const renderFlowStars = () => {
      if (!displaySettings.showFlowStars || !data.flowStars || data.flowStars.length === 0) return null;
      // In Fei Xing, we might want to hide these or handle differently. For now, hide in Fei Xing to reduce clutter
      if (viewMode === 'feixing') return null;

      const getLayerColor = (layer?: string) => {
          switch(layer) {
              case 'daxian': return 'text-green-600';
              case 'liunian': return 'text-blue-600';
              case 'liuyue': return 'text-amber-600';
              case 'liuri': return 'text-purple-600';
              case 'liushi': return 'text-red-600';
              default: return 'text-gray-500';
          }
      };

      return (
          <div className="flex flex-row-reverse items-end gap-x-0.5">
              {data.flowStars.map((s, i) => (
                  <div key={i} className={`flex flex-col items-center leading-none ${getLayerColor(s.layer)}`}>
                      {s.name.split('').map((char, idx) => (
                          <span key={idx} className="text-[10px] font-medium leading-none scale-90">{char}</span>
                      ))}
                  </div>
              ))}
          </div>
      );
  }

  // Helper for relative palace naming
  const getAbbrName = (currentIdx: number, refMingIdx: number) => {
      const relIdx = (currentIdx - refMingIdx + 12) % 12;
      const fullName = PALACE_NAMES[relIdx];
      return PALACE_ABBR[fullName] || fullName.substring(0,1);
  }

  const getBorderClasses = () => {
      if (isSelected) return 'ring-2 ring-ziwei-gold ring-inset bg-yellow-50/30'; 
      return '';
  };
  
  // Layout Direction for Stars
  // San He: Left to Right (Default wrap)
  // Fei Xing: Right to Left (Row Reverse)
  const starsContainerClass = viewMode === 'feixing' 
     ? 'flex-row-reverse gap-x-[2px] justify-start' 
     : 'flex-row gap-x-[1px] content-start items-start';

  return (
    <div 
        onClick={onClick}
        className={`bg-white relative h-full transition-all duration-200 border-r border-b border-ziwei-grid overflow-visible cursor-pointer hover:bg-gray-50 ${getBorderClasses()}`}
    >
      {/* Flying Star Arrows (Absolute positioned on edges) */}
      {flyingArrows && (
          <>
             {renderFlyingArrow('ziHua', flyingArrows.ziHua)}
             {renderFlyingArrow('xiangXin', flyingArrows.xiangXin)}
          </>
      )}

      {/* Stars Area */}
      <div className={`absolute inset-0 p-1 flex flex-wrap ${starsContainerClass} ${displaySettings.compactMode ? 'gap-y-0' : ''}`}>
          {starsToRender.map((s, i) => renderStar(s, i))}
      </div>

      {/* --- Xiao Xian (Small Limit) - Centered --- */}
      {displaySettings.showXiaoXian && data.smallRange.length > 0 && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
             <div className="flex flex-col items-center justify-center opacity-70">
                 <span className="text-[9px] text-gray-400 font-medium leading-none mb-0.5">小限</span>
                 <div className="text-[9px] text-gray-400 text-center leading-none">
                     {(() => {
                         const mid = Math.ceil(data.smallRange.length / 2);
                         const p1 = data.smallRange.slice(0, mid).join(',');
                         const p2 = data.smallRange.slice(mid).join(',');
                         return (
                             <>
                               <div className="whitespace-nowrap">{p1}</div>
                               <div className="whitespace-nowrap mt-[1px]">{p2}</div>
                             </>
                         )
                     })()}
                 </div>
             </div>
          </div>
      )}

      {/* --- BOTTOM SECTION --- */}
      
      {/* Bottom Left: 12 Gods Rings (San He Only) */}
      {viewMode === 'sanhe' && (
          <div className="absolute bottom-1 left-1 flex flex-col items-start gap-0.5 z-10">
              {[boShiGod, suiJianGod, jiangQianGod].map((god, i) => god && (
                <span key={i} className="text-[9px] text-gray-500 leading-none scale-95 origin-left">
                    {god.name}
                </span>
              ))}
          </div>
      )}
      
      {/* Bottom Center: Age Range (DaXian) & Body Palace */}
      <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 z-10 flex flex-col items-center gap-0 w-24">
         <div className="flex items-center gap-0.5">
             {data.isBodyPalace && (
                 <span className="text-[9px] bg-ziwei-gold text-white px-[2px] rounded-[2px] leading-none shadow-sm">身</span>
             )}
             <span className="text-[10px] text-gray-800 font-bold bg-white/80 px-1 rounded shadow-sm border border-gray-100 whitespace-nowrap">
                {data.ageRange[0]}-{data.ageRange[1]}
             </span>
         </div>
      </div>

      {/* Bottom Right: Palace Names & Stems */}
      <div className="absolute bottom-1 right-1 flex items-end">
          
          {/* Column 1 (Left): Small Flows */}
          <div className="flex flex-col items-end mr-1 space-y-[1px]">
               {flowIndices && (
                   <>
                       {showHour && viewMode === 'sanhe' && (
                           <span className="text-[12px] font-bold text-red-500 leading-none">
                               时{getAbbrName(data.index, flowIndices.liuShiMingIdx)}
                           </span>
                       )}
                       {showDay && viewMode === 'sanhe' && (
                           <span className="text-[12px] font-bold text-purple-600 leading-none">
                               日{getAbbrName(data.index, flowIndices.liuRiMingIdx)}
                           </span>
                       )}
                       {(showMonth || displaySettings.showLiuYue) && viewMode === 'sanhe' && (
                           <span className="text-[12px] font-bold text-amber-500 leading-none">
                               月{getAbbrName(data.index, flowIndices.liuYueMingIdx)}
                           </span>
                       )}
                   </>
               )}
          </div>

          {/* Column 2 (Right): Big Flows (Year, DaXian, Main) */}
          <div className="flex flex-col items-end mr-1 space-y-[1px]">
               {flowIndices && (
                   <>
                       {(showYear || displaySettings.showLiuNian) && (
                           <span className="text-[12px] font-bold text-blue-600 leading-none">
                               年{getAbbrName(data.index, flowIndices.liuNianMingIdx)}
                           </span>
                       )}
                       {showDaXian && (
                           <span className="text-[12px] font-bold text-green-600 leading-none">
                               大{getAbbrName(data.index, flowIndices.daXianMingIdx)}
                           </span>
                       )}
                   </>
               )}
               {/* Palace Name (Red) */}
               <div className="flex items-center">
                   <span className={`text-[12px] font-bold leading-none ${data.name === '命宫' ? 'bg-ziwei-red text-white px-1 py-[1px] rounded' : 'text-ziwei-red'}`}>
                        {data.name}
                   </span>
               </div>
          </div>

          {/* Vertical Stem/Branch */}
          <div className="flex flex-col items-center justify-end leading-none ml-1 relative">
               
               {/* Flow Stars (San He Only) */}
               {viewMode === 'sanhe' && (
                   <div className="absolute bottom-full right-0 mb-3.5 pointer-events-none whitespace-nowrap">
                        {renderFlowStars()}
                   </div>
               )}

               {/* 12 Chang Sheng God (San He Only) */}
               {changShengGod && (
                   <span className="text-[10px] text-gray-400 mb-1 flex flex-col items-center leading-tight scale-90">
                       {changShengGod.name.split('').map((c,i) => <span key={i}>{c}</span>)}
                   </span>
               )}
               
               {/* Stem/Branch */}
               <div className="flex flex-col items-center text-sm font-serif font-bold leading-tight">
                   <span className="text-gray-500">{data.heavenlyStem}</span>
                   <span className="text-gray-500">{data.earthlyBranch}</span>
               </div>
          </div>

      </div>

    </div>
  );
};

export default PalaceCard;
