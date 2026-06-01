#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ASSET_DIR="${INSTALLER_ROOT}/assets"
ICON_DIR="${INSTALLER_ROOT}/src-tauri/icons"
ICONSET_DIR="${ICON_DIR}/Horosa.iconset"
SOURCE_PNG="${ASSET_DIR}/icon-source.png"
BASE_PNG="${ASSET_DIR}/icon-base.png"
mkdir -p "${ICON_DIR}"
rm -rf "${ICONSET_DIR}"
mkdir -p "${ICONSET_DIR}"

force_rgba_pngs() {
  [ "$#" -gt 0 ] || return 0
  swift - "$@" <<'SWIFT'
import AppKit
import Foundation

for rawPath in CommandLine.arguments.dropFirst() {
    let url = URL(fileURLWithPath: rawPath)
    guard FileManager.default.fileExists(atPath: url.path),
          let image = NSImage(contentsOf: url) else {
        continue
    }
    var proposed = NSRect(origin: .zero, size: image.size)
    guard let cgImage = image.cgImage(forProposedRect: &proposed, context: nil, hints: nil),
          let rep = NSBitmapImageRep(
            bitmapDataPlanes: nil,
            pixelsWide: cgImage.width,
            pixelsHigh: cgImage.height,
            bitsPerSample: 8,
            samplesPerPixel: 4,
            hasAlpha: true,
            isPlanar: false,
            colorSpaceName: .deviceRGB,
            bytesPerRow: 0,
            bitsPerPixel: 0
          ) else {
        continue
    }
    let context = NSGraphicsContext(bitmapImageRep: rep)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = context
    context?.cgContext.clear(CGRect(x: 0, y: 0, width: cgImage.width, height: cgImage.height))
    context?.cgContext.draw(cgImage, in: CGRect(x: 0, y: 0, width: cgImage.width, height: cgImage.height))
    NSGraphicsContext.restoreGraphicsState()
    guard let png = rep.representation(using: .png, properties: [:]) else {
        continue
    }
    try png.write(to: url)
}
SWIFT
}

render_rounded_icon() {
  local input_png="$1"
  local output_png="$2"
  swift - "${input_png}" "${output_png}" <<'SWIFT'
import AppKit
import Foundation

let args = CommandLine.arguments
let input = URL(fileURLWithPath: args[1])
let output = URL(fileURLWithPath: args[2])
let canvas = NSSize(width: 1024, height: 1024)
let cornerRadius: CGFloat = 228

guard let source = NSImage(contentsOf: input),
      let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: Int(canvas.width),
        pixelsHigh: Int(canvas.height),
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
      ) else {
    exit(1)
}

let context = NSGraphicsContext(bitmapImageRep: rep)
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = context
context?.imageInterpolation = .high
let rect = NSRect(origin: .zero, size: canvas)
context?.cgContext.clear(CGRect(x: 0, y: 0, width: canvas.width, height: canvas.height))

let rounded = NSBezierPath(roundedRect: rect, xRadius: cornerRadius, yRadius: cornerRadius)
rounded.addClip()
source.draw(in: rect, from: .zero, operation: .sourceOver, fraction: 1.0)
NSGraphicsContext.restoreGraphicsState()

guard let png = rep.representation(using: .png, properties: [.interlaced: false]) else {
    exit(1)
}
try png.write(to: output)
SWIFT
}

if [ -f "${SOURCE_PNG}" ]; then
  render_rounded_icon "${SOURCE_PNG}" "${BASE_PNG}"
  force_rgba_pngs "${BASE_PNG}"
  cp "${BASE_PNG}" "${SOURCE_PNG}"
  cp "${BASE_PNG}" "${ICON_DIR}/icon.png"
else
  swift - <<'SWIFT' "${ASSET_DIR}" "${ICON_DIR}"
import AppKit
import Foundation

let args = CommandLine.arguments
let assetDir = URL(fileURLWithPath: args[1], isDirectory: true)
let iconDir = URL(fileURLWithPath: args[2], isDirectory: true)
let size = NSSize(width: 1024, height: 1024)
let image = NSImage(size: size)
image.lockFocus()
NSColor.clear.setFill()
NSBezierPath(rect: NSRect(origin: .zero, size: size)).fill()
let cardRect = NSRect(x: 64, y: 64, width: 896, height: 896)
let card = NSBezierPath(roundedRect: cardRect, xRadius: 196, yRadius: 196)
NSColor.white.setFill()
card.fill()
let style = NSMutableParagraphStyle()
style.alignment = .center
let attrs: [NSAttributedString.Key: Any] = [
  .font: NSFont.systemFont(ofSize: 280, weight: .bold),
  .foregroundColor: NSColor.black,
  .paragraphStyle: style
]
let text = NSString(string: "星阙")
let rect = NSRect(x: 0, y: 312, width: 1024, height: 400)
text.draw(in: rect, withAttributes: attrs)
image.unlockFocus()
let rep = NSBitmapImageRep(data: image.tiffRepresentation!)!
let png = rep.representation(using: .png, properties: [:])!
try png.write(to: assetDir.appendingPathComponent("icon-base.png"))
try png.write(to: iconDir.appendingPathComponent("icon.png"))
SWIFT
  force_rgba_pngs "${BASE_PNG}" "${ICON_DIR}/icon.png"
fi

for spec in   "16 icon_16x16.png"   "32 icon_16x16@2x.png"   "32 icon_32x32.png"   "64 icon_32x32@2x.png"   "128 icon_128x128.png"   "256 icon_128x128@2x.png"   "256 icon_256x256.png"   "512 icon_256x256@2x.png"   "512 icon_512x512.png"   "1024 icon_512x512@2x.png"; do
  size="${spec%% *}"
  name="${spec#* }"
  sips -z "${size}" "${size}" "${BASE_PNG}" --out "${ICONSET_DIR}/${name}" >/dev/null
 done
ICONSET_PNGS=()
while IFS= read -r -d '' png_path; do
  ICONSET_PNGS+=("${png_path}")
done < <(find "${ICONSET_DIR}" -type f -name '*.png' -print0)
force_rgba_pngs "${BASE_PNG}" "${ICON_DIR}/icon.png" "${ICONSET_PNGS[@]}"
iconutil -c icns "${ICONSET_DIR}" -o "${ICON_DIR}/icon.icns"
cp "${BASE_PNG}" "${ICON_DIR}/icon-1024.png"
force_rgba_pngs "${ICON_DIR}/icon-1024.png"
echo "icons generated under ${ICON_DIR}"
