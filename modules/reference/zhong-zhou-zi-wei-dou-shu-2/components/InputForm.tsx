
import React, { useState, useEffect } from 'react';
import { Gender, SavedProfile, ProfileCategory } from '../types';
import { Plus, Trash2, Edit, Play, Search, X, Check, ChevronDown } from 'lucide-react';

interface InputFormProps {
  onGenerate: (name: string, date: Date, timeIndex: number, gender: Gender, longitude?: number) => void;
}

const CATEGORIES: ProfileCategory[] = ['家人', '朋友', '同学', '同事', '客户', '名人', '其他', '分组'];

// Helper to get Time Index (Shi Chen) from Hour
const getTimeIndex = (hour: number) => {
    // Zi: 23-1 (Index 0)
    // Chou: 1-3 (Index 1)
    // Formula: (h + 1) / 2 floor % 12
    return Math.floor((hour + 1) / 2) % 12;
};

const TIME_LABELS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

// --- Custom Dropdown Picker Component ---
interface WheelPickerProps {
  isOpen: boolean;
  initialDate: Date;
  onConfirm: (date: Date) => void;
  onCancel: () => void;
}

const WheelPicker: React.FC<WheelPickerProps> = ({ isOpen, initialDate, onConfirm, onCancel }) => {
  if (!isOpen) return null;

  const [year, setYear] = useState(initialDate.getFullYear());
  const [month, setMonth] = useState(initialDate.getMonth() + 1);
  const [day, setDay] = useState(initialDate.getDate());
  const [hour, setHour] = useState(initialDate.getHours());
  const [minute, setMinute] = useState(initialDate.getMinutes());
  
  // Quick Input State
  const [quickInput, setQuickInput] = useState('');
  const [quickInputError, setQuickInputError] = useState(false);

  // Toggles for UI visual matching
  const [isLunar, setIsLunar] = useState(false); 
  const [isLeap, setIsLeap] = useState(false);

  // Sync state with initialDate whenever the modal opens
  useEffect(() => {
      if (isOpen) {
          setYear(initialDate.getFullYear());
          setMonth(initialDate.getMonth() + 1);
          setDay(initialDate.getDate());
          setHour(initialDate.getHours());
          setMinute(initialDate.getMinutes());
      }
  }, [isOpen, initialDate]);

  // Generate ranges
  const years = Array.from({ length: 150 }, (_, i) => 1900 + i);
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  const days = Array.from({ length: 31 }, (_, i) => i + 1); 
  const hours = Array.from({ length: 24 }, (_, i) => i);
  const minutes = Array.from({ length: 60 }, (_, i) => i);

  // Handle Quick Input
  const handleQuickInput = () => {
      // Format: YYYYMMDDHHmm (12 digits)
      const regex = /^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$/;
      const match = quickInput.match(regex);

      if (match) {
          const y = parseInt(match[1]);
          const m = parseInt(match[2]);
          const d = parseInt(match[3]);
          const h = parseInt(match[4]);
          const min = parseInt(match[5]);

          if (m < 1 || m > 12 || d < 1 || d > 31 || h < 0 || h > 23 || min < 0 || min > 59) {
              setQuickInputError(true);
              return;
          }

          setYear(y); setMonth(m); setDay(d); setHour(h); setMinute(min);
          setQuickInputError(false);
          setQuickInput(''); 
      } else {
          setQuickInputError(true);
      }
  };

  const handleConfirm = () => {
      const newDate = new Date(year, month - 1, day, hour, minute);
      onConfirm(newDate);
  };

  const SelectGroup = ({ label, value, options, onChange, format }: { label: string, value: number, options: number[], onChange: (v: number) => void, format?: (v: number) => string }) => (
      <div className="flex-1 flex flex-col gap-1">
          <label className="text-xs font-bold text-gray-500 text-center">{label}</label>
          <div className="relative">
              <select 
                  value={value}
                  onChange={(e) => onChange(parseInt(e.target.value))}
                  className="w-full appearance-none bg-gray-50 border border-gray-200 text-gray-900 font-bold py-2.5 pl-3 pr-8 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center shadow-sm text-lg"
              >
                  {options.map(opt => (
                      <option key={opt} value={opt}>{format ? format(opt) : opt}</option>
                  ))}
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-1 flex items-center px-2 text-gray-400">
                 <ChevronDown size={14} />
              </div>
          </div>
      </div>
  );

  return (
    <div className="fixed inset-0 z-[60] flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <div className="bg-white w-full max-w-[500px] rounded-xl overflow-hidden shadow-2xl animate-slide-up flex flex-col font-sans">
            
            {/* Quick Input Section */}
            <div className="bg-white p-3 flex gap-2 items-center">
                 <input 
                    className={`flex-1 bg-gray-50 border ${quickInputError ? 'border-red-500' : 'border-red-400'} rounded px-3 py-2 text-sm text-gray-600 outline-none focus:bg-white transition-colors`}
                    placeholder="快捷录入 (格式: 201806180408)"
                    value={quickInput}
                    onChange={(e) => { setQuickInput(e.target.value); setQuickInputError(false); }}
                    onKeyDown={(e) => e.key === 'Enter' && handleQuickInput()}
                    maxLength={12}
                 />
                 <button 
                   onClick={handleQuickInput}
                   className="bg-gray-200 hover:bg-gray-300 text-gray-600 rounded px-3 py-2 transition-colors"
                 >
                    <Check size={18} />
                 </button>
            </div>

            {/* Controls Bar */}
            <div className="bg-gray-50 px-4 py-3 flex justify-between items-center border-b border-gray-100">
                {/* Era Toggle */}
                <div className="flex items-center gap-3">
                    <span className="text-gray-900 font-bold text-sm">纪年方式:</span>
                    <div className="flex bg-gray-200 rounded-lg p-0.5">
                        <button onClick={() => setIsLunar(false)} className={`px-4 py-1 text-xs font-medium rounded-md transition-all ${!isLunar ? 'bg-[#007AFF] text-white shadow-sm' : 'text-gray-500'}`}>西元</button>
                        <button onClick={() => setIsLunar(true)} className={`px-4 py-1 text-xs font-medium rounded-md transition-all ${isLunar ? 'bg-[#007AFF] text-white shadow-sm' : 'text-gray-500'}`}>干支</button>
                    </div>
                </div>
                
                {/* Leap Toggle */}
                <div className="flex items-center gap-3">
                    <span className="text-gray-900 font-bold text-sm">是否闰月:</span>
                    <div className="flex bg-gray-200 rounded-lg p-0.5">
                        <button onClick={() => setIsLeap(true)} className={`px-4 py-1 text-xs font-medium rounded-md transition-all ${isLeap ? 'bg-[#007AFF] text-white shadow-sm' : 'text-gray-500'}`}>是</button>
                        <button onClick={() => setIsLeap(false)} className={`px-4 py-1 text-xs font-medium rounded-md transition-all ${!isLeap ? 'bg-[#007AFF] text-white shadow-sm' : 'text-gray-500'}`}>否</button>
                    </div>
                </div>
            </div>

            {/* Dropdown Body */}
            <div className="bg-white p-6 flex gap-2 justify-between items-end min-h-[160px]">
                <SelectGroup label="年" value={year} options={years} onChange={setYear} format={v => `${v}年`} />
                <SelectGroup label="月" value={month} options={months} onChange={setMonth} format={v => `${v}月`} />
                <SelectGroup label="日" value={day} options={days} onChange={setDay} format={v => `${v}日`} />
                <SelectGroup label="时" value={hour} options={hours} onChange={setHour} format={v => `${v.toString().padStart(2, '0')}时`} />
                <SelectGroup label="分" value={minute} options={minutes} onChange={setMinute} format={v => `${v.toString().padStart(2, '0')}分`} />
            </div>
            
            {/* Info Footer */}
            <div className="bg-white border-t border-gray-100 py-3 text-center shadow-[0_-2px_10px_rgba(0,0,0,0.02)] relative z-30">
                 <p className="text-sm text-gray-500 font-medium">
                     {year}年{month}月{day}日 {hour.toString().padStart(2, '0')}:{minute.toString().padStart(2, '0')} 
                     <span className="ml-2 font-bold text-[#007AFF]">({(TIME_LABELS[getTimeIndex(hour)] || '')}时)</span>
                 </p>
            </div>

            {/* Action Buttons */}
            <div className="flex border-t border-gray-200 bg-white relative z-30">
                <button onClick={onCancel} className="flex-1 py-4 text-gray-500 font-bold hover:bg-gray-50 transition-colors text-base">
                    取消
                </button>
                <div className="w-px bg-gray-200"></div>
                <button onClick={handleConfirm} className="flex-1 py-4 text-[#007AFF] font-bold hover:bg-blue-50 transition-colors text-base">
                    确定
                </button>
            </div>
        </div>
    </div>
  );
};


const InputForm: React.FC<InputFormProps> = ({ onGenerate }) => {
  // --- State ---
  const [profiles, setProfiles] = useState<SavedProfile[]>(() => {
      const saved = localStorage.getItem('ziwei_profiles');
      return saved ? JSON.parse(saved) : [];
  });
  
  const [activeTab, setActiveTab] = useState<ProfileCategory>('家人');
  const [search, setSearch] = useState('');
  const [selectedProfileId, setSelectedProfileId] = useState<string | null>(null);
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'create'|'edit'>('create');
  
  // Picker State
  const [isPickerOpen, setIsPickerOpen] = useState(false);

  // Initialize with Current Date/Time
  const [formData, setFormData] = useState<Partial<SavedProfile>>({
      name: '',
      gender: Gender.MALE,
      birthDate: new Date().toISOString(), // Store ISO string including time
      birthTimeIndex: 0, // Calculated
      category: '家人',
      notes: '',
      longitude: 120 // Default to 120E (Beijing Standard Time)
  });

  // Init Data on Load (Ensure default time is correct now)
  useEffect(() => {
      const now = new Date();
      // Set to current time on mount if creating new
      const idx = getTimeIndex(now.getHours());
      setFormData(prev => ({
          ...prev,
          birthDate: now.toISOString(),
          birthTimeIndex: idx
      }));
  }, []);

  // --- Effects ---
  useEffect(() => {
    localStorage.setItem('ziwei_profiles', JSON.stringify(profiles));
  }, [profiles]);

  // --- Handlers ---

  const handleSave = () => {
     if (!formData.name || !formData.birthDate) return;
     
     const dateObj = new Date(formData.birthDate);
     // Ensure time index is consistent with date's hour
     const tIdx = getTimeIndex(dateObj.getHours());

     const newProfile: SavedProfile = {
         id: modalMode === 'create' ? Date.now().toString() : formData.id!,
         name: formData.name,
         gender: formData.gender || Gender.MALE,
         birthDate: formData.birthDate, // Saves full ISO
         birthTimeIndex: tIdx,
         category: formData.category || '家人',
         notes: formData.notes || '',
         longitude: formData.longitude // Save longitude
     };

     if (modalMode === 'create') {
         setProfiles([...profiles, newProfile]);
     } else {
         setProfiles(profiles.map(p => p.id === newProfile.id ? newProfile : p));
     }
     setIsModalOpen(false);
  };

  const handleDelete = () => {
      if (!selectedProfileId) return;
      if (confirm('确定删除该档案吗？')) {
          setProfiles(profiles.filter(p => p.id !== selectedProfileId));
          setSelectedProfileId(null);
      }
  };

  const openCreate = () => {
      const now = new Date();
      setFormData({
          name: '',
          gender: Gender.MALE,
          birthDate: now.toISOString(),
          birthTimeIndex: getTimeIndex(now.getHours()),
          category: activeTab,
          notes: '',
          longitude: 120
      });
      setModalMode('create');
      setIsModalOpen(true);
  };

  const openEdit = () => {
      if (!selectedProfileId) return;
      const p = profiles.find(x => x.id === selectedProfileId);
      if (p) {
          setFormData({ ...p, longitude: p.longitude ?? 120 });
          setModalMode('edit');
          setIsModalOpen(true);
      }
  };

  const handleArrange = () => {
      if (!selectedProfileId) return;
      const p = profiles.find(x => x.id === selectedProfileId);
      if (p) {
          const d = new Date(p.birthDate);
          const tIdx = getTimeIndex(d.getHours());
          // Pass longitude to generator
          onGenerate(p.name, d, tIdx, p.gender, p.longitude);
      }
  };

  // Date Logic for Display
  const getDisplayDate = () => {
      if (!formData.birthDate) return '';
      const d = new Date(formData.birthDate);
      return `${d.getFullYear()}-${(d.getMonth()+1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
  };

  const getDisplayTime = () => {
      if (!formData.birthDate) return '00:00';
      const d = new Date(formData.birthDate);
      return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
  }

  // Filtered List
  const displayProfiles = profiles.filter(p => 
      (activeTab === '分组' || p.category === activeTab) &&
      (p.name.includes(search))
  );

  return (
    <div className="w-full max-w-4xl h-[600px] bg-white rounded-lg shadow-2xl flex flex-col overflow-hidden font-sans border border-gray-300">
        
        {/* Search Bar */}
        <div className="p-2 border-b border-gray-200 flex items-center bg-gray-50">
            <Search size={18} className="text-gray-500 ml-2" />
            <input 
               className="bg-transparent border-none outline-none ml-2 w-full text-sm text-gray-800 placeholder-gray-400"
               placeholder="搜索姓名..."
               value={search}
               onChange={e => setSearch(e.target.value)}
            />
            {search && <button onClick={() => setSearch('')}><X size={16} className="text-gray-400 mr-2"/></button>}
        </div>

        {/* Tabs */}
        <div className="flex bg-[#3b5998] text-white overflow-x-auto scrollbar-hide">
            {CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => setActiveTab(cat)}
                  className={`flex-1 py-2.5 text-sm font-medium whitespace-nowrap px-4 hover:bg-white/10 transition-colors border-b-2 ${activeTab === cat ? 'bg-white/10 border-white' : 'border-transparent'}`}
                >
                    {cat}
                </button>
            ))}
        </div>

        {/* List Header */}
        <div className="grid grid-cols-12 bg-[#2563eb] text-white text-xs py-1.5 px-3 font-bold">
            <div className="col-span-3">姓名</div>
            <div className="col-span-1 text-center">性别</div>
            <div className="col-span-4">生辰</div>
            <div className="col-span-4">备注</div>
        </div>

        {/* List Content */}
        <div className="flex-1 overflow-y-auto bg-gray-100">
            {displayProfiles.map((p, idx) => {
                const d = new Date(p.birthDate);
                const hStr = d.getHours().toString().padStart(2, '0');
                const mStr = d.getMinutes().toString().padStart(2, '0');
                return (
                <div 
                   key={p.id}
                   onClick={() => setSelectedProfileId(p.id)}
                   className={`grid grid-cols-12 text-sm py-2.5 px-3 border-b border-gray-200 cursor-pointer items-center ${
                       selectedProfileId === p.id 
                       ? 'bg-[#dbeafe] text-blue-900 font-medium' 
                       : idx % 2 === 0 ? 'bg-white text-gray-700' : 'bg-gray-50 text-gray-700'
                   } hover:bg-blue-50 transition-colors`}
                >
                    <div className="col-span-3 font-bold">{p.name}</div>
                    <div className="col-span-1 text-center">{p.gender}</div>
                    <div className="col-span-4 text-xs font-mono">
                        {d.getFullYear()}/{(d.getMonth()+1).toString().padStart(2,'0')}/{d.getDate().toString().padStart(2,'0')} {hStr}:{mStr}
                    </div>
                    <div className="col-span-4 text-xs truncate text-gray-500">{p.notes || '无'}</div>
                </div>
            )})}
            {displayProfiles.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                    <span className="text-4xl mb-2">📇</span>
                    <span>暂无档案</span>
                </div>
            )}
        </div>

        {/* Bottom Toolbar */}
        <div className="p-3 border-t border-gray-200 bg-gray-100 flex justify-between items-center shadow-[0_-2px_10px_rgba(0,0,0,0.05)] z-10">
            <div className="flex gap-2">
                <button onClick={openCreate} className="flex items-center gap-1 px-4 py-2 bg-white border border-gray-300 rounded shadow-sm text-sm text-blue-600 font-medium hover:bg-blue-50 active:translate-y-0.5 transition-all">
                    <Plus size={16}/> 新增
                </button>
                <button onClick={openEdit} disabled={!selectedProfileId} className="flex items-center gap-1 px-4 py-2 bg-white border border-gray-300 rounded shadow-sm text-sm text-gray-700 font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed active:translate-y-0.5 transition-all">
                    <Edit size={16}/> 修改
                </button>
                <button onClick={handleDelete} disabled={!selectedProfileId} className="flex items-center gap-1 px-4 py-2 bg-white border border-gray-300 rounded shadow-sm text-sm text-red-600 font-medium hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed active:translate-y-0.5 transition-all">
                    <Trash2 size={16}/> 删除
                </button>
            </div>
            <button onClick={handleArrange} disabled={!selectedProfileId} className="flex items-center gap-2 px-8 py-2 bg-[#4f46e5] text-white rounded shadow-md text-sm font-bold hover:bg-[#4338ca] disabled:opacity-50 disabled:cursor-not-allowed active:translate-y-0.5 transition-all">
                <Play size={16} fill="currentColor"/> 排盘
            </button>
        </div>

        {/* --- MODAL --- */}
        {isModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
                <div className="bg-white rounded-lg shadow-2xl w-full max-w-[500px] overflow-hidden animate-scale-in">
                    <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
                       <h3 className="text-lg font-bold text-gray-800">{modalMode === 'create' ? '新增档案' : '修改档案'}</h3>
                       <button onClick={() => setIsModalOpen(false)}><X size={20} className="text-gray-400 hover:text-gray-600"/></button>
                    </div>
                    
                    <div className="p-6 space-y-5">
                        {/* Name & Gender */}
                        <div className="flex gap-5">
                           <div className="flex-[1.5]">
                               <label className="block text-xs font-bold text-gray-500 mb-1.5">姓名</label>
                               <input 
                                 className="w-full bg-gray-800 text-white rounded px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[#6366f1] transition-all font-medium placeholder-gray-500"
                                 value={formData.name}
                                 onChange={e => setFormData({...formData, name: e.target.value})}
                                 placeholder="输入姓名"
                               />
                           </div>
                           <div className="flex-1">
                               <label className="block text-xs font-bold text-gray-500 mb-1.5">性别</label>
                               <div className="flex rounded border border-gray-300 overflow-hidden h-[42px]">
                                   <button 
                                     onClick={() => setFormData({...formData, gender: Gender.MALE})}
                                     className={`flex-1 text-sm font-bold transition-colors ${formData.gender === Gender.MALE ? 'bg-[#6366f1] text-white' : 'bg-white text-gray-500 hover:bg-gray-50'}`}
                                   >男</button>
                                   <div className="w-px bg-gray-300"></div>
                                   <button 
                                     onClick={() => setFormData({...formData, gender: Gender.FEMALE})}
                                     className={`flex-1 text-sm font-bold transition-colors ${formData.gender === Gender.FEMALE ? 'bg-pink-500 text-white' : 'bg-white text-gray-500 hover:bg-gray-50'}`}
                                   >女</button>
                               </div>
                           </div>
                        </div>

                        {/* Birth Date */}
                        <div>
                            <label className="block text-xs font-bold text-gray-500 mb-1.5">生辰 (西历)</label>
                            
                            {/* Visual Inputs Row */}
                            <div className="flex gap-2">
                                <div 
                                    className="flex-[2] bg-gray-800 text-white rounded px-3 py-2.5 text-sm cursor-pointer hover:bg-gray-700 transition-colors flex items-center justify-between"
                                    onClick={() => setIsPickerOpen(true)}
                                >
                                    <span>{getDisplayDate()}</span>
                                    <span className="text-gray-400 font-mono pl-2 border-l border-gray-600 ml-2">{getDisplayTime()}</span>
                                </div>
                                
                                <div className="flex rounded border border-gray-300 overflow-hidden bg-white">
                                    <button className="px-3 py-1 bg-[#6366f1] text-white text-xs font-bold shadow-sm">西历</button>
                                    <button className="px-3 py-1 bg-white text-gray-500 text-xs border-l hover:bg-gray-50">农历</button>
                                </div>
                            </div>
                            
                            {/* Time Display (Derived Chinese Hour) */}
                            <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
                                <span>对应时辰:</span>
                                <span className="font-bold text-[#6366f1]">{TIME_LABELS[getTimeIndex(new Date(formData.birthDate || Date.now()).getHours())]}时</span>
                            </div>
                        </div>

                        {/* Location */}
                        <div>
                             <label className="block text-xs font-bold text-gray-500 mb-1.5">出生地经度 (120为北京时间标准)</label>
                             <input 
                                 type="number"
                                 step="0.01"
                                 className="w-full border border-gray-300 rounded px-3 py-2.5 text-sm bg-white text-gray-800 placeholder-gray-400 outline-none focus:border-[#6366f1] transition-colors"
                                 placeholder="输入经度，排盘更精准 (例如: 116.40)"
                                 value={formData.longitude}
                                 onChange={(e) => setFormData({...formData, longitude: parseFloat(e.target.value) || undefined})}
                               />
                        </div>

                        {/* Category */}
                        <div>
                             <label className="block text-xs font-bold text-gray-500 mb-1.5">分类</label>
                             <div className="flex flex-wrap gap-2">
                                 {CATEGORIES.filter(c => c !== '分组').map(cat => (
                                     <button
                                       key={cat}
                                       onClick={() => setFormData({...formData, category: cat})}
                                       className={`text-xs px-3 py-1.5 rounded-full border transition-all ${formData.category === cat ? 'bg-[#6366f1] text-white border-[#6366f1] shadow-sm scale-105' : 'bg-white text-gray-600 border-gray-300 hover:border-gray-400'}`}
                                     >
                                         {cat}
                                     </button>
                                 ))}
                             </div>
                        </div>

                        {/* Notes */}
                        <div>
                             <label className="block text-xs font-bold text-gray-500 mb-1.5">备注</label>
                             <textarea 
                                className="w-full bg-gray-800 text-white rounded px-3 py-2 text-sm h-24 outline-none resize-none placeholder-gray-500 focus:ring-1 focus:ring-gray-600"
                                placeholder="限50字以内"
                                maxLength={50}
                                value={formData.notes}
                                onChange={e => setFormData({...formData, notes: e.target.value})}
                             />
                        </div>

                    </div>

                    <div className="flex border-t border-gray-200">
                        <button onClick={() => setIsModalOpen(false)} className="flex-1 py-4 text-gray-500 font-bold hover:bg-gray-50 text-sm transition-colors">取消</button>
                        <div className="w-px bg-gray-200"></div>
                        <button onClick={handleSave} className="flex-1 py-4 text-[#6366f1] font-bold hover:bg-indigo-50 text-sm transition-colors">确定</button>
                    </div>
                </div>
            </div>
        )}
        
        {/* Custom Wheel Picker */}
        <WheelPicker 
            isOpen={isPickerOpen}
            initialDate={formData.birthDate ? new Date(formData.birthDate) : new Date()}
            onCancel={() => setIsPickerOpen(false)}
            onConfirm={(d) => {
                const tIdx = getTimeIndex(d.getHours());
                setFormData({ ...formData, birthDate: d.toISOString(), birthTimeIndex: tIdx });
                setIsPickerOpen(false);
            }}
        />

    </div>
  );
};

export default InputForm;
