# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 08:25:17 2025

@author: hooki
"""

import datetime
from itertools import cycle, repeat
import  sxtwl
from sxtwl import fromSolar
import ephem


jqmc = ['小寒', '大寒', '立春', '雨水', '驚蟄', '春分', '清明', '穀雨', '立夏', '小滿', '芒種', '夏至', '小暑', '大暑', '立秋', '處暑', '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪', '冬至']
# 12「節」(每月之首,逢之換月柱;立春兼換年柱)。其餘12「氣」不換月柱。
JIE_TERMS = {'立春', '驚蟄', '清明', '立夏', '芒種', '小暑', '立秋', '白露', '寒露', '立冬', '大雪', '小寒'}
tian_gan = '甲乙丙丁戊己庚辛壬癸'
di_zhi = '子丑寅卯辰巳午未申酉戌亥'

#%% 甲子平支
def jiazi():
    return list(map(lambda x: "{}{}".format(tian_gan[x % len(tian_gan)],di_zhi[x % len(di_zhi)]),list(range(60))))


def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None

def new_list(olist, o):
    a = olist.index(o)
    res1 = olist[a:] + olist[:a]
    return res1
#%% 節氣計算
def get_jieqi_start_date(year, month, day, hour, minute):
    """
    Get the start date and time of the current solar term (jieqi) for the given date and time.
    Returns a dictionary with year, month, day, hour, minute, and the name of the solar term.
    """
    # Initialize the day object with the given date
    day = sxtwl.fromSolar(year, month, day)
    
    # Check if the given date has a solar term
    if day.hasJieQi():
        jq_index = day.getJieQi()
        jd = day.getJieQiJD()
        t = sxtwl.JD2DD(jd)
        return {
            "年": t.Y,
            "月": t.M,
            "日": t.D,
            "時": int(t.h),
            "分": round(t.m),
            "節氣": jqmc[jq_index-1],
            "時間":datetime.datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
        }
    else:
        # If no solar term on this day, find the previous solar term
        current_day = day
        while True:
            current_day = current_day.before(1)
            if current_day.hasJieQi():
                jq_index = current_day.getJieQi()
                jd = current_day.getJieQiJD()
                t = sxtwl.JD2DD(jd)
                return {
                    "年": t.Y,
                    "月": t.M,
                    "日": t.D,
                    "時": int(t.h),
                    "分": round(t.m),
                    "節氣": jqmc[jq_index-1],
                    "時間":datetime.datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
                }
            
def get_before_jieqi_start_date(year, month, day, hour, minute):
    """
    Get the start date and time of the next solar term (jieqi) after the given date and time.
    Returns a dictionary with year, month, day, hour, minute, and the name of the solar term.
    """
    # Initialize the day object with the given date
    day = sxtwl.fromSolar(year, month, day)
    
    # Start searching from the next day
    current_day = day.before(15)
    while True:
        if current_day.hasJieQi():
            jq_index = current_day.getJieQi()
            jd = current_day.getJieQiJD()
            t = sxtwl.JD2DD(jd)
            return {
                "年": t.Y,
                "月": t.M,
                "日": t.D,
                "時": int(t.h),
                "分": round(t.m),
                "節氣": jqmc[jq_index-1],
                "時間":datetime.datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
            }
        current_day = current_day.before(1)

def get_next_jieqi_start_date(year, month, day, hour, minute):
    """
    Get the start date and time of the next solar term (jieqi) after the given date and time.
    Returns a dictionary with year, month, day, hour, minute, and the name of the solar term.
    """
    # Initialize the day object with the given date
    day = sxtwl.fromSolar(year, month, day)
    
    # Start searching from the next day
    current_day = day.after(1)
    while True:
        if current_day.hasJieQi():
            jq_index = current_day.getJieQi()
            jd = current_day.getJieQiJD()
            t = sxtwl.JD2DD(jd)
            return {
                "年": t.Y,
                "月": t.M,
                "日": t.D,
                "時": int(t.h),
                "分": round(t.m),
                "節氣": jqmc[jq_index-1],
                "時間":datetime.datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
            }
        current_day = current_day.after(1)


def jq(year, month, day, hour, minute):
    """
    Get the current solar term (jieqi) for the given date and time.
    Returns the name of the solar term as a string.
    """
    try:
        current_datetime = datetime.datetime(year, month, day, hour, minute)
        jq_start_dict = get_jieqi_start_date(year, month, day, hour, minute)
        next_jq_start_dict = get_next_jieqi_start_date(year, month, day, hour, minute)
        
        if not (isinstance(jq_start_dict, dict) and isinstance(next_jq_start_dict, dict) and 
                "時間" in jq_start_dict and "時間" in next_jq_start_dict and
                "節氣" in jq_start_dict and "節氣" in next_jq_start_dict):
            raise ValueError(f"Invalid jieqi dictionary format for {year}-{month}-{day} {hour}:{minute}")
        
        jq_start_datetime = jq_start_dict["時間"]
        next_jq_start_datetime = next_jq_start_dict["時間"]
        jq_name = jq_start_dict["節氣"]
        
        if not (isinstance(jq_start_datetime, datetime.datetime) and isinstance(next_jq_start_datetime, datetime.datetime)):
            raise ValueError(f"Jieqi times are not datetime objects: {jq_start_datetime}, {next_jq_start_datetime}")
        
        # Check if current_datetime is within the current jieqi period
        if jq_start_datetime <= current_datetime < next_jq_start_datetime:
            return jq_name
        # If before the current jieqi start, get the previous jieqi
        elif current_datetime < jq_start_datetime:
            prev_jq_start_dict = get_before_jieqi_start_date(year, month, day, hour, minute)
            if not (isinstance(prev_jq_start_dict, dict) and "節氣" in prev_jq_start_dict):
                raise ValueError(f"Invalid previous jieqi dictionary format for {year}-{month}-{day}")
            return prev_jq_start_dict["節氣"]
        else:
            raise ValueError(f"Current datetime {current_datetime} not within any valid jieqi period")
    except Exception as e:
        raise ValueError(f"Error in jq for {year}-{month}-{day} {hour}:{minute}: {str(e)}")

# ===== 置閏轉盤：超神接氣置閏 定局所用節氣 =====
# 奇門換局以「符頭日」(甲/己日)為基準,五日一元,上中下三元配節氣局數。符頭較節氣每月約早到
# 10.5 小時(超神);於芒種/大雪累積≥9天時置閏(重複該節氣上中下三元一次)使符頭轉為落後(接氣)。
# 故定局實際所用之節氣,超神時會提前換到下一節氣,與當日曆法節氣 jq() 未必相同(見上游 issue #62)。
_SHANGYUAN_FUTOU = {'甲子', '甲午', '己卯', '己酉'}        # 上元符頭(甲己日且地支子午卯酉)
_JIE_SEQ_ZHIRUN = {
    '冬至': ['冬至', '小寒', '大寒', '立春', '雨水', '驚蟄', '春分', '清明', '穀雨', '立夏', '小滿', '芒種'],
    '夏至': ['夏至', '小暑', '大暑', '立秋', '處暑', '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪'],
}
_RUN_REPEAT = {'冬至': '大雪', '夏至': '芒種'}             # 置閏時重複之節氣(冬至前大雪/夏至前芒種)

def _day_gz(day):
    return tian_gan[day.getDayGZ().tg] + di_zhi[day.getDayGZ().dz]

def _solar_date(day):
    return datetime.date(day.getSolarYear(), day.getSolarMonth(), day.getSolarDay())

def _last_shangyuan_before(day_obj):
    """day_obj 之前(不含當日)最近的上元符頭日。"""
    cur = day_obj.before(1)
    for _ in range(20):
        if _day_gz(cur) in _SHANGYUAN_FUTOU:
            return cur
        cur = cur.before(1)
    return None

def _anchor_solstice(year, month, day):
    """管轄當日之『至』(其上元符頭 F* ≤ 當日)。先檢未來(下一至的超神前窗),再回溯。"""
    target = datetime.date(year, month, day)
    d = fromSolar(year, month, day)
    for _ in range(30):                       # 下一至若其 F* 已 ≤ 當日(當日落在其超神前窗)
        d = d.after(1)
        if d.hasJieQi() and jqmc[d.getJieQi() - 1] in ('冬至', '夏至'):
            f = _last_shangyuan_before(d)
            if f is not None and _solar_date(f) <= target:
                return jqmc[d.getJieQi() - 1], d
            break
    d = fromSolar(year, month, day)
    for _ in range(230):                      # 否則回溯最近一個其 F* ≤ 當日 的至
        if d.hasJieQi() and jqmc[d.getJieQi() - 1] in ('冬至', '夏至'):
            f = _last_shangyuan_before(d)
            if f is not None and _solar_date(f) <= target:
                return jqmc[d.getJieQi() - 1], d
        d = d.before(1)
    return None, None

def zhirun_jieqi(year, month, day, hour, minute):
    """置閏轉盤定局所用節氣(超神接氣置閏後);可能與當日曆法節氣 jq() 不同。"""
    znm, zday = _anchor_solstice(year, month, day)
    if znm is None:
        return jq(year, month, day, hour, minute)             # 保底:回退曆法節氣
    fstar = _last_shangyuan_before(zday)
    dgap = (_solar_date(zday) - _solar_date(fstar)).days        # 至 − 上元符頭(超神距)
    seq = _JIE_SEQ_ZHIRUN[znm]
    if dgap >= 9:                                              # 置閏:F* 組重複大雪/芒種,至之上元順延
        seq = [_RUN_REPEAT[znm]] + seq
    n = (_solar_date(fromSolar(year, month, day)) - _solar_date(fstar)).days // 5   # 自 F* 起第 n 元
    g = max(0, min(n // 3, len(seq) - 1))                      # 第 g 組節氣(每組三元)
    return seq[g]

def ke_jiazi_d(hour):
    t = [f"{h}:{m}0" for h in range(24) for m in range(6)]
    minutelist = dict(zip(t, cycle(repeat_list(1, find_lunar_ke(hour)))))
    return minutelist

def repeat_list(n, thelist):
    return [repetition for i in thelist for repetition in repeat(i,n)]


#五虎遁，起正月
def find_lunar_month(year):
    fivetigers = {
    tuple(list('甲己')):'丙寅',
    tuple(list('乙庚')):'戊寅',
    tuple(list('丙辛')):'庚寅',
    tuple(list('丁壬')):'壬寅',
    tuple(list('戊癸')):'甲寅'
    }
    if multi_key_dict_get(fivetigers, year[0]) == None:
        result = multi_key_dict_get(fivetigers, year[1])
    else:
        result = multi_key_dict_get(fivetigers, year[0])
    return dict(zip(range(1,13),new_list(jiazi(), result)[:12]))

#五鼠遁，起子時
def find_lunar_hour(day):
    fiverats = {
    tuple(list('甲己')):'甲子',
    tuple(list('乙庚')):'丙子',
    tuple(list('丙辛')):'戊子',
    tuple(list('丁壬')):'庚子',
    tuple(list('戊癸')):'壬子'
    }
    if multi_key_dict_get(fiverats, day[0]) == None:
        result = multi_key_dict_get(fiverats, day[1])
    else:
        result = multi_key_dict_get(fiverats, day[0])
    return dict(zip(list(di_zhi), new_list(jiazi(), result)[:12]))

#五馬遁，起子刻
def find_lunar_ke(hour):
    fivehourses = {
    tuple(list('丙辛')):'甲午',
    tuple(list('丁壬')):'丙午',
    tuple(list('戊癸')):'戊午',
    tuple(list('甲己')):'庚午',
    tuple(list('乙庚')):'壬午'
    }
    if multi_key_dict_get(fivehourses, hour[0]) == None:
        result = multi_key_dict_get(fivehourses, hour[1])
    else:
        result = multi_key_dict_get(fivehourses, hour[0])
    return new_list(jiazi(), result)

#農曆
def lunar_date_d(year, month, day):
    lunar_m = ['占位', '正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']
    day = fromSolar(year, month, day)
    return {"年":day.getLunarYear(),
            "農曆月": lunar_m[int(day.getLunarMonth())],
            "月":day.getLunarMonth(),
            "日":day.getLunarDay()}

#換算干支
def gangzhi1(year, month, day, hour, minute):
    if hour == 23:
        d = ephem.Date(round((ephem.Date("{}/{}/{} {}:00:00.00".format(
            str(year).zfill(4),
            str(month).zfill(2),
            str(day+1).zfill(2),
            str(0).zfill(2)))),3))
    else:
        d = ephem.Date("{}/{}/{} {}:00:00.00".format(
            str(year).zfill(4),
            str(month).zfill(2),
            str(day).zfill(2),
            str(hour).zfill(2)))
    dd = list(d.tuple())
    cdate = fromSolar(dd[0], dd[1], dd[2])
    yTG,mTG,dTG,hTG = "{}{}".format(
        tian_gan[cdate.getYearGZ().tg],
        di_zhi[cdate.getYearGZ().dz]), "{}{}".format(
            tian_gan[cdate.getMonthGZ().tg],
            di_zhi[cdate.getMonthGZ().dz]), "{}{}".format(
                tian_gan[cdate.getDayGZ().tg],
                di_zhi[cdate.getDayGZ().dz]), "{}{}".format(
                    tian_gan[cdate.getHourGZ(dd[3]).tg],
                    di_zhi[cdate.getHourGZ(dd[3]).dz])
    if year < 1900:
        mTG1 = find_lunar_month(yTG).get(lunar_date_d(year, month, day).get("月"))
    else:
        mTG1 = mTG
    hTG1 = find_lunar_hour(dTG).get(hTG[1])
    return [yTG, mTG1, dTG, hTG1]

def gangzhi(year, month, day, hour, minute):
    if hour == 23:
        d = ephem.Date(round((ephem.Date("{}/{}/{} {}:00:00.00".format(
            str(year).zfill(4),
            str(month).zfill(2),
            str(day+1).zfill(2),
            str(0).zfill(2)))),3))
    else:
        d = ephem.Date("{}/{}/{} {}:00:00.00".format(
            str(year).zfill(4),
            str(month).zfill(2),
            str(day).zfill(2),
            str(hour).zfill(2)))
    dd = list(d.tuple())
    cdate = fromSolar(dd[0], dd[1], dd[2])
    yTG,mTG,dTG,hTG = "{}{}".format(
        tian_gan[cdate.getYearGZ().tg],
        di_zhi[cdate.getYearGZ().dz]), "{}{}".format(
            tian_gan[cdate.getMonthGZ().tg],
            di_zhi[cdate.getMonthGZ().dz]), "{}{}".format(
                tian_gan[cdate.getDayGZ().tg],
                di_zhi[cdate.getDayGZ().dz]), "{}{}".format(
                    tian_gan[cdate.getHourGZ(dd[3]).tg],
                    di_zhi[cdate.getHourGZ(dd[3]).dz])
    if year < 1900:
        mTG1 = find_lunar_month(yTG).get(lunar_date_d(year, month, day).get("月"))
    else:
        mTG1 = mTG
    # 月柱按精確交節時刻校正：sxtwl 的 getMonthGZ 為日級，交節當日整日已跳入新月。
    # 若該日交的是 12「節」之一，且給定時刻早於精確交節時刻，仍屬前一節 → 沿用前一日之月柱
    # （立春兼換年柱）。其餘日不變。
    if year >= 1900:
        _sd = fromSolar(year, month, day)
        if _sd.hasJieQi() and jqmc[_sd.getJieQi() - 1] in JIE_TERMS:
            _t = sxtwl.JD2DD(_sd.getJieQiJD())
            _crossing = datetime.datetime(_t.Y, _t.M, _t.D, int(_t.h), round(_t.m))
            if datetime.datetime(year, month, day, hour, minute) < _crossing:
                _prev = _sd.before(1)
                mTG1 = tian_gan[_prev.getMonthGZ().tg] + di_zhi[_prev.getMonthGZ().dz]
                if jqmc[_sd.getJieQi() - 1] == '立春':
                    yTG = tian_gan[_prev.getYearGZ().tg] + di_zhi[_prev.getYearGZ().dz]
    hTG1 = find_lunar_hour(dTG).get(hTG[1])
    zi = gangzhi1(year, month, day, 0, 0)[3]
    if minute < 10 and minute >=0:
        reminute = "00"
    if minute < 20 and minute >=10:
        reminute = "10"
    if minute < 30 and minute >=20:
        reminute = "20"
    if minute < 40 and minute >=30:
        reminute = "30"
    if minute < 50 and minute >=40:
        reminute = "40"
    if minute < 60 and minute >=50:
        reminute = "50"
    hourminute = str(hour)+":"+str(reminute)
    gangzhi_minute = ke_jiazi_d(zi).get(hourminute)
    return [yTG, mTG1, dTG, hTG1, gangzhi_minute]

if __name__ == '__main__':
    year = 2005
    month = 5
    day = 5
    hour = 16
    minute = 30
    #print(liujiashun_dict())
    #print(qimen_ju_name_zhirun_raw(year, month, day, hour, minute))
    print(f"{year}-{month}-{day} {hour}:{minute}")
    #print( get_jieqi_start_date(year, month, day, hour, minute))
    #print( get_next_jieqi_start_date(year, month, day, hour, minute))
    #print( get_before_jieqi_start_date(year, month, day, hour, minute))
    print(gangzhi(year, month, day, hour, minute))
    #print(find_lunar_month(gangzhi(year, month, day, hour, minute)[0]))

        
