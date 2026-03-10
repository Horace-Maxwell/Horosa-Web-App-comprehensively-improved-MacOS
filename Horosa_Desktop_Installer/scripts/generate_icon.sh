#!/usr/bin/env bash
set -euo pipefail

INSTALLER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ASSET_DIR="${INSTALLER_ROOT}/assets"
ICON_DIR="${INSTALLER_ROOT}/src-tauri/icons"
ICONSET_DIR="${ICON_DIR}/Horosa.iconset"
mkdir -p "${ICON_DIR}"
rm -rf "${ICONSET_DIR}"
mkdir -p "${ICONSET_DIR}"

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

BASE_PNG="${ASSET_DIR}/icon-base.png"
for spec in   "16 icon_16x16.png"   "32 icon_16x16@2x.png"   "32 icon_32x32.png"   "64 icon_32x32@2x.png"   "128 icon_128x128.png"   "256 icon_128x128@2x.png"   "256 icon_256x256.png"   "512 icon_256x256@2x.png"   "512 icon_512x512.png"   "1024 icon_512x512@2x.png"; do
  size="${spec%% *}"
  name="${spec#* }"
  sips -z "${size}" "${size}" "${BASE_PNG}" --out "${ICONSET_DIR}/${name}" >/dev/null
 done
iconutil -c icns "${ICONSET_DIR}" -o "${ICON_DIR}/icon.icns"
cp "${BASE_PNG}" "${ICON_DIR}/icon-1024.png"
echo "icons generated under ${ICON_DIR}"
