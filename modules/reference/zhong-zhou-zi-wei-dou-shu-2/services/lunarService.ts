
import { Solar, Lunar } from 'lunar-javascript';

export const getLunarDetails = (date: Date, timeIndex: number) => {
  // Determine hours based on timeIndex (0=Zi=23-01). 
  // We treat timeIndex 0 as 00:00 of the current day (Early Zi).
  const hours = timeIndex * 2;
  
  const solar = Solar.fromYmdHms(
    date.getFullYear(),
    date.getMonth() + 1,
    date.getDate(),
    hours,
    0,
    0
  );
  
  const lunar = solar.getLunar();
  
  return {
    lunarYear: lunar.getYear(),
    lunarMonth: lunar.getMonth(),
    lunarDay: lunar.getDay(),
    isLeap: lunar.toString().indexOf('闰') >= 0, 
    ganZhiYear: lunar.getYearInGanZhi(),
    ganZhiMonth: lunar.getMonthInGanZhi(),
    ganZhiDay: lunar.getDayInGanZhi(),
    timeGanZhi: lunar.getTimeInGanZhi(),
    lunarMonthChinese: lunar.getMonthInChinese(),
    lunarDayChinese: lunar.getDayInChinese(),
    eightChar: lunar.getEightChar(),
  };
};

// Helper for Flow Calculations
export const getLunarDateObj = (date: Date, timeIndex: number = 0): Lunar => {
   const hours = timeIndex * 2;
   const solar = Solar.fromYmdHms(
    date.getFullYear(),
    date.getMonth() + 1,
    date.getDate(),
    hours,
    0,
    0
  );
  return solar.getLunar();
}

export const getZodiacYearStemIndex = (year: number): number => {
  // 4 = Jia, 5 = Yi ...
  const i = (year - 4) % 10;
  return i < 0 ? i + 10 : i;
};

export const getZodiacYearBranchIndex = (year: number): number => {
  // 1984 (Rat) -> 1984 - 4 = 1980. 1980 % 12 = 0 -> Zi (Rat).
  // Array: Zi=0.
  const i = (year - 4) % 12;
  return i < 0 ? i + 12 : i;
};

// Calculate True Solar Time (Simplified to Longitude Correction only per request)
export const getTrueSolarTime = (date: Date, longitude: number): Date => {
    // 1. Longitude Correction (4 min per degree)
    // Beijing Standard Meridian = 120E
    // At 120E, offset is 0. 
    // East of 120 (e.g. 121) -> Time is earlier (sun rises earlier) -> Add 4 mins
    // West of 120 (e.g. 119) -> Time is later -> Subtract 4 mins
    const offsetMinutes = (longitude - 120) * 4;

    // Note: Equation of Time (EoT) is omitted here to satisfy the requirement 
    // that "at 120 degrees East there should be no deviation".
    // This results in Local Mean Solar Time.
    
    const totalOffsetMs = offsetMinutes * 60 * 1000;
    
    return new Date(date.getTime() + totalOffsetMs);
};
