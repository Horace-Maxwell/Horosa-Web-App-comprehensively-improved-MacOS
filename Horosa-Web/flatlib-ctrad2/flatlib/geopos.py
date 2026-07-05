"""
    This file is part of flatlib - (C) FlatAngle
    Author: João Ventura (flatangleweb@gmail.com)
    

    This module provides functions and a class for handling 
    geographic positions. Each latitude/longitude is an angle 
    represented by a <float> value.

"""

import re

from . import angle


# Modes
LAT = 0
LON = 1

# Mappings
SIGN = {'N': '+', 'S': '-', 'E': '+', 'W': '-'}
CHAR = {
    LAT: {'+': 'N', '-': 'S'},
    LON: {'+': 'E', '-': 'W'},
}

# 纯十进制坐标串（'31.2' / '-121.5' / '39.9'）。历史 bug：这类串没有 N/S/E/W 方向字符，
# 会原样落进 DMS 分段解析（angle.strSlist 的 int('31.2')）直接抛 ValueError —— 前端字段在
# 表单/储存往返中常把数值坐标字符串化，排盘即报 param error。此处按浮点直读。
# 🔴 必须用正则甄别、绝不能用 float() 试探：'121e30'（东经 121°30' 的合法方向串）会被
# float() 误读成科学计数 1.21e+32，必须仍走下方 NSEW→DMS 路径。
_PLAIN_DECIMAL = re.compile(r'^[+-]?\d+(?:\.\d+)?$')
# 十进制+尾随方向字符（'26.07N' / '26N' / '121.5e'）。旧路径同样崩（替换后出现空段或带点段
# → int('') / int('26.07') 抛错），按方向符号+浮点直读。'121e30' 尾字符是数字，不会误入。
_DECIMAL_WITH_DIR = re.compile(r'^(\d+(?:\.\d+)?)([NSEW])$', re.IGNORECASE)


# === Conversions === #

def toFloat(value):
    """ Converts angle representation to float.
    Accepts angles and strings such as "12W30:00".

    """
    if isinstance(value, str):
        stripped = value.strip()
        if _PLAIN_DECIMAL.match(stripped):
            return float(stripped)
        m = _DECIMAL_WITH_DIR.match(stripped)
        if m:
            return float(SIGN[m.group(2).upper()] + m.group(1))
        # Find lat/lon char in string and insert angle sign
        value = value.upper()
        for char in ['N', 'S', 'E', 'W']:
            if char in value:
                value = SIGN[char] + value.replace(char, ':')
                break
    return angle.toFloat(value)

def toList(value):
    """ Converts angle float to signed list. """
    return angle.toList(value)

def toString(value, mode):
    """ Converts angle float to string. 
    Mode refers to LAT/LON.
    
    """
    string = angle.toString(value)
    sign = string[0]
    separator = CHAR[mode][sign]
    string = string.replace(':', separator, 1)
    return string[1:]


# ------------------ #
#    GeoPos Class    #
# ------------------ #

class GeoPos:
    """ This class represents a geographic position 
    on the planet specified by a given lat and lon.
    
    Objects of this class can be instantiated with
    GeoPos("45N32", "128W45") or another angle type
    such as strings, signed lists or floats. 
    
    """
    
    def __init__(self, lat, lon):
        self.lat = toFloat(lat)
        self.lon = toFloat(lon)
        
    def slists(self):
        """ Return lat/lon as signed lists. """
        return [
            toList(self.lat), 
            toList(self.lon)
        ]
    
    def strings(self):
        """ Return lat/lon as strings. """
        return [
            toString(self.lat, LAT),
            toString(self.lon, LON)
        ]
        
    def __str__(self):
        strings = self.strings()
        return '<%s %s>' % (strings[0], strings[1])