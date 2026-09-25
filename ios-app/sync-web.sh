#!/bin/bash
# 親フォルダのWebアプリ本体を www/ にコピーする（ネイティブアプリに同梱するため）
set -e
cd "$(dirname "$0")"
SRC=".."
DEST="www"
rm -rf "$DEST"
mkdir -p "$DEST"
# 同梱するファイルだけをコピー（sw.js はアプリ内では使わないので入れない）
for f in index.html manifest.json icon.svg icon-192.png icon-512.png icon-512-maskable.png apple-touch-icon.png; do
  if [ -f "$SRC/$f" ]; then cp "$SRC/$f" "$DEST/"; fi
done
echo "Web資産を www/ にコピーしました:"
ls -1 "$DEST"
