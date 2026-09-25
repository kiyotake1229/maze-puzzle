#!/bin/bash
# icon.svg から PNG アイコン一式を作り直す
# 使い方: bash tools/make-icons.sh（要 Node.js。初回だけ npx が変換ツールを取得する）
set -e
cd "$(dirname "$0")/.."
R="npx -y @resvg/resvg-js-cli@2.6.2-beta.1"

$R --fit-width 192 icon.svg icon-192.png
$R --fit-width 512 icon.svg icon-512.png
$R --fit-width 180 icon.svg apple-touch-icon.png
# マスカブル: Android などで丸く切り抜かれても欠けないよう、絵を中央に 72% の大きさで置く
sed -e 's|<path d="M86|<g transform="translate(128 128) scale(0.72) translate(-128 -128)"><path d="M86|' \
    -e 's|</svg>|</g></svg>|' icon.svg | $R --fit-width 512 - icon-512-maskable.png
# iOS アプリ用の元画像（ios-app/ がある場合）。この画像から npm run icons でアイコン一式を作る
if [ -d ios-app/assets ]; then $R --fit-width 1024 icon.svg ios-app/assets/icon.png; fi

echo "アイコンを作り直しました"
