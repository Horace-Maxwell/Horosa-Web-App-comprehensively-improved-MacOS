#!/usr/bin/env python3
"""marker 剥离投影悬空校验(2026-07-31 辅盘实案制度化)。

对每个含 @horosa-private 块的 js/jsx/ts/tsx 文件:
  块内 import 的绑定名 × strip 投影(剥注释/字符串)文本 → 交集非空 = 悬空引用。
剥离后该名字成未定义自由变量 → 模块顶层 ReferenceError → 技法页干净安装必炸,
且首爆被预载 catch 吞、二次点击伪装成「Lazy chunk resolved empty」——真因极难排查。

用法: check_marker_projection.py <repo_ui_src_dir>
输出: 每个悬空点一行 "<file>\t<names>"; 全净则无输出, exit 0; 有悬空 exit 1。
"""
import os
import re
import sys


def block_import_names(text):
    names = set()
    in_block = False
    for line in text.splitlines():
        if '@horosa-private:end' in line:
            in_block = False
            continue
        if '@horosa-private:' in line:
            in_block = True
            continue
        if not in_block:
            continue
        m = re.match(r"\s*import\s+(.+?)\s+from\s+['\"]", line)
        if not m:
            continue
        clause = m.group(1).replace('* as', '')
        for part in re.split(r'[,{}]', clause):
            part = re.sub(r'^.*\bas\s+', '', part.strip())
            if re.match(r'^[A-Za-z_$][\w$]*$', part):
                names.add(part)
    return names


def strip_projection(text):
    out = []
    in_block = False
    for line in text.splitlines():
        if in_block:
            if '@horosa-private:end' in line:
                in_block = False
            continue
        if '@horosa-private:' in line:
            in_block = True
            continue
        out.append(line)
    proj = '\n'.join(out)
    proj = re.sub(r'//[^\n]*', '', proj)
    proj = re.sub(r'/\*.*?\*/', '', proj, flags=re.S)
    proj = re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`(?:\\.|[^`\\])*`", '""', proj, flags=re.S)
    return proj


def main():
    root = sys.argv[1]
    bad = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ('node_modules', '.umi', '.umi-production', 'dist', 'dist-file')]
        dirnames[:] = [d for d in dirnames if d != '__tests__']
        for fn in filenames:
            if not fn.endswith(('.js', '.jsx', '.ts', '.tsx')):
                continue
            # 测试文件不进产物构建,块外可自行 require 同名 → 文本级判据必误报,豁免
            if '.test.' in fn or '.spec.' in fn:
                continue
            p = os.path.join(dirpath, fn)
            try:
                text = open(p, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            if '@horosa-private:' not in text:
                continue
            names = block_import_names(text)
            if not names:
                continue
            proj = strip_projection(text)
            dangling = sorted(n for n in names if re.search(r'\b' + re.escape(n) + r'\b', proj))
            if dangling:
                print('%s\t%s' % (os.path.relpath(p, root), ' '.join(dangling)))
                bad += 1
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
