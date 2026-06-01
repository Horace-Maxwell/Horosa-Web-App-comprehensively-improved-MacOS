#!/usr/bin/env python3
"""Verify that Horosa app icons are truly transparent-rounded assets."""

from __future__ import annotations

import argparse
import pathlib
import struct
import subprocess
import sys
import tempfile
import zlib


DEFAULT_ICON_PATHS = [
    "assets/icon-source.png",
    "src-tauri/icons/icon.png",
    "src-tauri/icons/icon-1024.png",
    "src-tauri/icons/Horosa.iconset/icon_512x512@2x.png",
    "src-tauri/icons/icon.icns",
]


class IconError(Exception):
    pass


def paeth(left: int, up: int, upper_left: int) -> int:
    p = left + up - upper_left
    pa = abs(p - left)
    pb = abs(p - up)
    pc = abs(p - upper_left)
    if pa <= pb and pa <= pc:
        return left
    if pb <= pc:
        return up
    return upper_left


def parse_png_rgba(path: pathlib.Path) -> tuple[int, int, bytearray]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise IconError("not a PNG")

    offset = 8
    width = height = bit_depth = color_type = None
    idat = bytearray()
    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk_data[:10])
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None or bit_depth is None or color_type is None:
        raise IconError("missing PNG IHDR")
    if bit_depth != 8 or color_type not in (4, 6):
        raise IconError(f"expected 8-bit PNG with alpha, got bitDepth={bit_depth} colorType={color_type}")

    bytes_per_pixel = 2 if color_type == 4 else 4
    row_length = width * bytes_per_pixel
    raw = zlib.decompress(bytes(idat))
    expected = (row_length + 1) * height
    if len(raw) != expected:
        raise IconError(f"unexpected decompressed size: {len(raw)} != {expected}")

    rows: list[bytearray] = []
    pos = 0
    previous = bytearray(row_length)
    for _ in range(height):
        filter_type = raw[pos]
        pos += 1
        row = bytearray(raw[pos : pos + row_length])
        pos += row_length
        for i, value in enumerate(row):
            left = row[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
            up = previous[i]
            upper_left = previous[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
            if filter_type == 0:
                pass
            elif filter_type == 1:
                row[i] = (value + left) & 0xFF
            elif filter_type == 2:
                row[i] = (value + up) & 0xFF
            elif filter_type == 3:
                row[i] = (value + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                row[i] = (value + paeth(left, up, upper_left)) & 0xFF
            else:
                raise IconError(f"unsupported PNG filter {filter_type}")
        rows.append(row)
        previous = row

    alpha_offset = 1 if color_type == 4 else 3
    alpha = bytearray(width * height)
    for y, row in enumerate(rows):
        for x in range(width):
            alpha[y * width + x] = row[x * bytes_per_pixel + alpha_offset]
    return width, height, alpha


def png_from_icon(path: pathlib.Path, temp_dir: pathlib.Path) -> pathlib.Path:
    if path.suffix.lower() != ".icns":
        return path
    out_path = temp_dir / f"{path.stem}.png"
    subprocess.run(
        ["sips", "-s", "format", "png", str(path), "--out", str(out_path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    return out_path


def check_icon(path: pathlib.Path, corner_alpha_max: int, center_alpha_min: int, min_size: int) -> str:
    with tempfile.TemporaryDirectory(prefix="horosa-icon-alpha.") as temp:
        png_path = png_from_icon(path, pathlib.Path(temp))
        width, height, alpha = parse_png_rgba(png_path)

    if width < min_size or height < min_size:
        raise IconError(f"expected at least {min_size}x{min_size}, got {width}x{height}")
    corners = [
        alpha[0],
        alpha[width - 1],
        alpha[(height - 1) * width],
        alpha[(height - 1) * width + width - 1],
    ]
    center = alpha[(height // 2) * width + (width // 2)]
    if max(corners) > corner_alpha_max:
        raise IconError(f"corners are not transparent enough: {corners}")
    if center < center_alpha_min:
        raise IconError(f"center is not opaque enough: {center}")
    return f"icon alpha OK {path}: size={width}x{height} corners={corners} center={center}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--installer-root", default=pathlib.Path(__file__).resolve().parents[1])
    parser.add_argument("--paths", nargs="*", help="Explicit icon files to validate.")
    parser.add_argument("--corner-alpha-max", type=int, default=8)
    parser.add_argument("--center-alpha-min", type=int, default=240)
    parser.add_argument("--min-size", type=int, default=1024)
    args = parser.parse_args()

    root = pathlib.Path(args.installer_root).resolve()
    paths = [pathlib.Path(p) for p in (args.paths or DEFAULT_ICON_PATHS)]
    failures: list[str] = []
    for raw_path in paths:
        path = raw_path if raw_path.is_absolute() or raw_path.exists() else root / raw_path
        if not path.exists():
            failures.append(f"{path}: missing")
            continue
        try:
            print(check_icon(path, args.corner_alpha_max, args.center_alpha_min, args.min_size))
        except (IconError, subprocess.CalledProcessError, OSError, zlib.error) as exc:
            failures.append(f"{path}: {exc}")

    if failures:
        for failure in failures:
            print(f"icon alpha FAIL {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
