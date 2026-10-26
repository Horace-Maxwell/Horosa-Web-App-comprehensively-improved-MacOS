
import React, { useState } from 'react';
import { AppSettings } from '../types';
import { X } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: AppSettings;
  onUpdate: (newSettings: AppSettings) => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, settings, onUpdate }) => {
  if (!isOpen) return null;
  
  const [activeTab, setActiveTab] = useState<'basic' | 'anxing' | 'sihua' | 'display'>('basic');

  const updateSetting = (path: string[], value: any) => {
     const newSettings = { ...settings };
     let curr: any = newSettings;
     for (let i = 0; i < path.length - 1; i++) {
         curr = curr[path[i]];
     }
     curr[path[path.length - 1]] = value;
     onUpdate(newSettings);
  };

  const ToggleItem = ({ label, checked, onChange }: { label: string, checked: boolean, onChange: (v: boolean) => void }) => (
    <div className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
      <span className="text-gray-700 text-sm font-medium">{label}</span>
      <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
        <input 
          type="checkbox" 
          className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer transition-all duration-300 left-0" 
          style={{ top: '2px', left: checked ? '20px' : '2px', borderColor: checked ? 'transparent' : '#e5e7eb' }}
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <label 
          className={`toggle-label block overflow-hidden h-6 rounded-full cursor-pointer transition-colors duration-300 ${checked ? 'bg-ziwei-green' : 'bg-gray-300'}`}
        ></label>
      </div>
    </div>
  );

  const SelectItem = ({ label, value, options, onChange }: { label: string, value: string, options: {val: string, txt: string}[], onChange: (v: string) => void }) => (
    <div className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
      <span className="text-gray-700 text-sm font-medium">{label}</span>
      <select 
         value={value}
         onChange={(e) => onChange(e.target.value)}
         className="text-sm border border-gray-300 rounded p-1 bg-white text-gray-700 outline-none focus:border-ziwei-blue max-w-[150px]"
      >
         {options.map(opt => <option key={opt.val} value={opt.val}>{opt.txt}</option>)}
      </select>
    </div>
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white w-full max-w-lg rounded-xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-bold text-gray-800">设定</h2>
          <button onClick={onClose} className="p-1 rounded-full hover:bg-gray-200 transition-colors">
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
           {['basic', 'anxing', 'sihua', 'display'].map(tab => (
               <button 
                  key={tab}
                  onClick={() => setActiveTab(tab as any)}
                  className={`flex-1 py-3 text-sm font-bold transition-colors ${activeTab === tab ? 'text-ziwei-blue border-b-2 border-ziwei-blue bg-blue-50' : 'text-gray-500 hover:bg-gray-50'}`}
               >
                  {tab === 'basic' && '基础'}
                  {tab === 'anxing' && '安星'}
                  {tab === 'sihua' && '四化'}
                  {tab === 'display' && '显示'}
               </button>
           ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
          
          {/* Basic Settings */}
          {activeTab === 'basic' && (
            <div className="bg-white rounded-lg border border-gray-200 px-4 py-2">
              <ToggleItem 
                label="区分早晚子时" 
                checked={settings.earlyLateZi} 
                onChange={(v) => updateSetting(['earlyLateZi'], v)} 
              />
              <ToggleItem 
                label="真太阳时 (需经纬度)" 
                checked={settings.trueSolarTime} 
                onChange={(v) => updateSetting(['trueSolarTime'], v)} 
              />
              <SelectItem 
                label="闰月处理"
                value={settings.leapMonth}
                options={[
                    {val: 'current', txt: '随本月'},
                    {val: 'next', txt: '作下月'},
                    {val: 'split', txt: '月中分界'}
                ]}
                onChange={(v) => updateSetting(['leapMonth'], v)}
              />
            </div>
          )}

          {/* An Xing (Star Placement) */}
          {activeTab === 'anxing' && (
            <div className="space-y-3">
               <div className="bg-white rounded-lg border border-gray-200 px-4 py-2">
                  <h4 className="text-xs font-bold text-gray-400 uppercase mb-2 mt-1">基本规则</h4>
                  <SelectItem 
                     label="安天马"
                     value={settings.anXing.tianMa}
                     options={[{val: 'year', txt: '依据年支'}, {val: 'month', txt: '依据月支'}]}
                     onChange={(v) => updateSetting(['anXing', 'tianMa'], v)}
                  />
                  <SelectItem 
                     label="安天空"
                     value={settings.anXing.tianKong}
                     options={[{val: 'year', txt: '常规排法(年支)'}, {val: 'seq', txt: '顺加生时'}]}
                     onChange={(v) => updateSetting(['anXing', 'tianKong'], v)}
                  />
                  <SelectItem 
                     label="安截空旬空"
                     value={settings.anXing.jieKong}
                     options={[{val: 'dual', txt: '正副双星法'}, {val: 'single', txt: '常规单星法'}]}
                     onChange={(v) => updateSetting(['anXing', 'jieKong'], v)}
                  />
                  <SelectItem 
                     label="安魁钺 (庚/辛)"
                     value={settings.anXing.kuiYue}
                     options={[
                         {val: 'xin_hu_ma', txt: '六辛逢虎马 (预设)'},
                         {val: 'xin_ma_hu', txt: '六辛逢马虎'},
                         {val: 'geng_ma_hu', txt: '庚辛逢马虎'},
                         {val: 'geng_hu_ma', txt: '庚辛逢虎马'}
                     ]}
                     onChange={(v) => updateSetting(['anXing', 'kuiYue'], v)}
                  />
               </div>

               <div className="bg-white rounded-lg border border-gray-200 px-4 py-2">
                  <h4 className="text-xs font-bold text-gray-400 uppercase mb-2 mt-1">其他规则</h4>
                  <SelectItem 
                     label="星曜亮度"
                     value={settings.anXing.brightness}
                     options={[{val: 'zhongzhou', txt: '中州派理论'}, {val: 'quan', txt: '斗数全书'}]}
                     onChange={(v) => updateSetting(['anXing', 'brightness'], v)}
                  />
                  <SelectItem 
                     label="安命主"
                     value={settings.anXing.mingZhu}
                     options={[{val: 'quan', txt: '斗数全书'}, {val: 'zhongzhou', txt: '中州派理论'}]}
                     onChange={(v) => updateSetting(['anXing', 'mingZhu'], v)}
                  />
                  <SelectItem 
                     label="长生十二神"
                     value={settings.anXing.changSheng}
                     options={[{val: 'water_earth', txt: '水土共长生'}, {val: 'fire_earth', txt: '火土共长生'}]}
                     onChange={(v) => updateSetting(['anXing', 'changSheng'], v)}
                  />
               </div>
            </div>
          )}

          {/* Si Hua */}
          {activeTab === 'sihua' && (
            <div className="bg-white rounded-lg border border-gray-200 px-4 py-2">
               <SelectItem 
                 label="戊干 (贪阴右机)"
                 value={settings.siHua.wu}
                 options={[{val: 'tan_yin_you_ji', txt: '贪阴右机 (预设)'}, {val: 'tan_yin_yang_ji', txt: '贪阴阳机'}]}
                 onChange={(v) => updateSetting(['siHua', 'wu'], v)}
               />
               <SelectItem 
                 label="庚干 (阳武阴同)"
                 value={settings.siHua.geng}
                 options={[
                     {val: 'yang_wu_yin_tong', txt: '阳武阴同 (预设)'},
                     {val: 'yang_wu_tong_yin', txt: '阳武同阴'},
                     {val: 'yang_wu_fu_tong', txt: '阳武府同'},
                     {val: 'yang_wu_fu_xiang', txt: '阳武府相'},
                     {val: 'yang_wu_tong_xiang', txt: '阳武同相'}
                 ]}
                 onChange={(v) => updateSetting(['siHua', 'geng'], v)}
               />
               <SelectItem 
                 label="壬干 (梁紫左武)"
                 value={settings.siHua.ren}
                 options={[
                     {val: 'liang_zi_zuo_wu', txt: '梁紫左武 (预设)'},
                     {val: 'liang_zi_fu_wu', txt: '梁紫府武'},
                     {val: 'liang_zi_xiang_wu', txt: '梁紫相武'}
                 ]}
                 onChange={(v) => updateSetting(['siHua', 'ren'], v)}
               />
               <SelectItem 
                 label="癸干 (破巨阴贪)"
                 value={settings.siHua.gui}
                 options={[
                     {val: 'po_ju_yin_tan', txt: '破巨阴贪 (预设)'},
                     {val: 'po_ju_yang_tan', txt: '破巨阳贪'}
                 ]}
                 onChange={(v) => updateSetting(['siHua', 'gui'], v)}
               />
            </div>
          )}

          {/* Display */}
          {activeTab === 'display' && (
            <div className="space-y-3">
               <div className="bg-white rounded-lg border border-gray-200 px-4 py-2">
                 <h4 className="text-xs font-bold text-gray-400 uppercase mb-2 mt-1">界面布局</h4>
                 <ToggleItem label="显示流年" checked={settings.display.showLiuNian} onChange={(v) => updateSetting(['display', 'showLiuNian'], v)} />
                 <ToggleItem label="显示小限" checked={settings.display.showXiaoXian} onChange={(v) => updateSetting(['display', 'showXiaoXian'], v)} />
                 <ToggleItem label="显示流月" checked={settings.display.showLiuYue} onChange={(v) => updateSetting(['display', 'showLiuYue'], v)} />
                 <ToggleItem label="显示三方飞星箭头" checked={settings.display.showArrows} onChange={(v) => updateSetting(['display', 'showArrows'], v)} />
                 <ToggleItem label="紧凑模式" checked={settings.display.compactMode} onChange={(v) => updateSetting(['display', 'compactMode'], v)} />
               </div>

               <div className="bg-white rounded-lg border border-gray-200 px-4 py-2">
                 <h4 className="text-xs font-bold text-gray-400 uppercase mb-2 mt-1">流耀显示</h4>
                 <ToggleItem label="显示流耀 (总开关)" checked={settings.display.showFlowStars} onChange={(v) => updateSetting(['display', 'showFlowStars'], v)} />
                 {settings.display.showFlowStars && (
                     <div className="pl-4 border-l-2 border-gray-100 ml-1">
                        <ToggleItem label="显示流天马" checked={settings.display.showFlowMa} onChange={(v) => updateSetting(['display', 'showFlowMa'], v)} />
                        <ToggleItem label="显示流火铃" checked={settings.display.showFlowHuoLing} onChange={(v) => updateSetting(['display', 'showFlowHuoLing'], v)} />
                        <ToggleItem label="显示流红喜" checked={settings.display.showFlowHongXi} onChange={(v) => updateSetting(['display', 'showFlowHongXi'], v)} />
                        <ToggleItem label="显示流昌曲" checked={settings.display.showFlowChangQu} onChange={(v) => updateSetting(['display', 'showFlowChangQu'], v)} />
                     </div>
                 )}
               </div>
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50 text-center">
           <button 
             onClick={onClose}
             className="w-full bg-ziwei-blue text-white font-bold py-3 rounded-lg hover:bg-blue-600 transition-colors shadow-lg"
           >
             保存设置
           </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
