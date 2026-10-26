
import React, { useState, useEffect, useCallback } from 'react';
import InputForm from './components/InputForm';
import Astrolabe from './components/Astrolabe';
import SettingsModal from './components/SettingsModal';
import { ChartData, Gender, AppSettings, DEFAULT_SETTINGS } from './types';
import { calculateChart } from './services/ziweiMath';

const App: React.FC = () => {
  const [chartData, setChartData] = useState<ChartData | null>(null);
  
  // State for Input persistence to allow re-calculation
  const [inputState, setInputState] = useState<{name: string, date: Date, timeIndex: number, gender: Gender, longitude?: number} | null>(null);
  
  // Settings State with LocalStorage
  const [settings, setSettings] = useState<AppSettings>(() => {
    const saved = localStorage.getItem('ziwei_settings');
    return saved ? JSON.parse(saved) : DEFAULT_SETTINGS;
  });

  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem('ziwei_settings', JSON.stringify(settings));
    // If chart exists, re-calc when settings change
    if (inputState) {
        regenerateChart(inputState.date, inputState.timeIndex);
    }
  }, [settings]);

  const regenerateChart = useCallback((date: Date, timeIdx: number) => {
      if (!inputState) return;
      try {
        const data = calculateChart(inputState.name, date, timeIdx, inputState.gender, settings, inputState.longitude);
        setChartData(data);
      } catch (e) {
        console.error(e);
      }
  }, [inputState, settings]);

  const handleGenerate = (name: string, date: Date, timeIndex: number, gender: Gender, longitude?: number) => {
    setInputState({ name, date, timeIndex, gender, longitude });
    try {
      const data = calculateChart(name, date, timeIndex, gender, settings, longitude);
      setChartData(data);
    } catch (e) {
      console.error(e);
      alert("Error generating chart. Please check inputs.");
    }
  };

  const handleTimeTravel = (dayDelta: number, hourDelta: number) => {
    if (!inputState) return;
    
    const newDate = new Date(inputState.date);
    newDate.setDate(newDate.getDate() + dayDelta);
    
    let newTimeIdx = inputState.timeIndex + hourDelta;
    
    // Handle Time Index overflow/underflow (0-11)
    if (newTimeIdx > 11) {
        newTimeIdx = 0;
        newDate.setDate(newDate.getDate() + 1);
    } else if (newTimeIdx < 0) {
        newTimeIdx = 11;
        newDate.setDate(newDate.getDate() - 1);
    }
    
    setInputState(prev => ({ ...prev!, date: newDate, timeIndex: newTimeIdx }));
    regenerateChart(newDate, newTimeIdx);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 text-gray-900 font-sans">
      
      {!chartData ? (
        <div className="w-full flex justify-center items-center h-screen bg-gray-200">
             <InputForm onGenerate={handleGenerate} />
        </div>
      ) : (
        <div className="w-full max-w-5xl mx-auto shadow-2xl bg-white h-screen flex flex-col">
          <Astrolabe 
            data={chartData} 
            onReset={() => { setChartData(null); setInputState(null); }} 
            onTimeTravel={handleTimeTravel}
            onOpenSettings={() => setIsSettingsOpen(true)}
            settings={settings}
          />
        </div>
      )}

      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        onUpdate={setSettings}
      />
    </div>
  );
};

export default App;
