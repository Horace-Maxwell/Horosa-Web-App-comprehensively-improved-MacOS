#!/usr/bin/env python3

import argparse
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'Horosa-Web', 'flatlib-ctrad2'))

import swisseph  # noqa: E402
from flatlib import const  # noqa: E402
from flatlib.ephem import swe  # noqa: E402


MODE_FLAGS = {
    'SWIEPH': swisseph.FLG_SWIEPH | swisseph.FLG_SPEED,
    'MOSEPH': swisseph.FLG_MOSEPH | swisseph.FLG_SPEED,
    'JPL': swisseph.FLG_JPLEPH | swisseph.FLG_SPEED,
}

OBJECTS = {
    'Sun': const.SUN,
    'Moon': const.MOON,
    'Mercury': const.MERCURY,
    'Venus': const.VENUS,
    'Mars': const.MARS,
    'Jupiter': const.JUPITER,
    'Saturn': const.SATURN,
    'Uranus': const.URANUS,
    'Neptune': const.NEPTUNE,
    'Pluto': const.PLUTO,
    'North Node': const.NORTH_NODE,
}


def parse_args():
    parser = argparse.ArgumentParser(description='Inspect Horosa local Swiss/JPL ephemeris runtime.')
    parser.add_argument('--jd', type=float, default=2460737.5, help='Julian day to sample.')
    parser.add_argument(
        '--objects',
        default='Moon,Sun,North Node',
        help='Comma-separated object labels. Supported: %s' % ', '.join(OBJECTS.keys()),
    )
    parser.add_argument('--json', action='store_true', help='Emit JSON only.')
    return parser.parse_args()


def collect(flags, object_ids, sidereal=False):
    if sidereal:
        flags = flags | swisseph.FLG_SIDEREAL
    rows = {}
    for label in object_ids:
        obj = swe.sweObject(OBJECTS[label], args.jd, flags)
        rows[label] = {
            'lon': obj['lon'],
            'lat': obj['lat'],
            'ra': obj['ra'],
            'decl': obj['decl'],
        }
    return rows


args = parse_args()
requested = [item.strip() for item in args.objects.split(',') if item.strip()]
for item in requested:
    if item not in OBJECTS:
        raise SystemExit('Unsupported object: %s' % item)

runtime = swe.getRuntimeConfig()
result = {
    'runtime': runtime,
    'jd': args.jd,
    'objects': requested,
    'samples': {},
}

for mode, flags in MODE_FLAGS.items():
    if mode == 'JPL' and not runtime.get('jpl_file'):
        result['samples'][mode] = {'available': False}
        continue
    result['samples'][mode] = {
        'available': True,
        'flags': flags,
        'values': collect(flags, requested),
    }

if args.json:
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0)

print('runtime:', json.dumps(runtime, ensure_ascii=False, sort_keys=True))
print('jd:', args.jd)
for mode, payload in result['samples'].items():
    print('[%s] available=%s' % (mode, payload.get('available')))
    if not payload.get('available'):
        continue
    for label, values in payload['values'].items():
        print(
            '  %-10s lon=%11.8f lat=%10.8f ra=%11.8f decl=%10.8f'
            % (label, values['lon'], values['lat'], values['ra'], values['decl'])
        )
