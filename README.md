# MAZE — 迷路パズル

レベル制の迷路パズル。スワイプ／ボタンで移動し、ゴールを目指す。

| 項目 | 内容 |
|---|---|
| 状態 | Web版 完成 |
| Web公開 | https://kiyotake1229.github.io/maze-puzzle/ （GitHub Pages） |
| 本体 | `index.html`（約54KB） |
| 通信 | なし（完全オフライン） |
| データ | 端末内のみ |
| PWA | 未対応 |
| iOS | 未着手 |

---

## 社内説明資料

岩崎さんに説明するときの資料一式は `資料/` にある。

| 資料 | 場所 |
|---|---|
| スライド（Claude Design。閲覧・修正・PDF書き出し） | https://claude.ai/code/artifact/dad654fa-2ff3-4609-8119-1cb7d7a42d57 |
| スライド（PDF） | `資料/プレゼン資料/MAZE_社内説明.pdf` |
| 話す台本 | [資料/プレゼンの進め方.md](資料/プレゼンの進め方.md) |
| スライドの生成元 | `資料/プレゼン資料/gen.py`（文言を直して `python3 gen.py`） |

---

## 主な機能

- レベル制。クリアで次のレベルへ
- モード切替（ノーマル ほか）
- テーマ切替（デフォルト / aurora / mono / sunset）
- ヒント機能、やり直し
- 実績システム（条件を満たすと解除）
- 効果音・BGM の ON/OFF

## ファイル構成

```
MAZE/
  index.html            アプリ本体（PWA用のmetaタグは設定済み）
  maze-artifact.html    index.html の Artifact 公開用コピー（下記参照）
  report.html           開発報告書（岩崎さん向け。ブラウザで開ける）
```

### `maze-artifact.html` について

`index.html` から `<!DOCTYPE>` `<html>` `<head>` を取り除いたもの。以前は Claude Artifact に公開する際にこの形式が必要だった。
**現在は `index.html` をそのまま公開できる**ため、このファイルは不要になっている。`index.html` を更新してもこちらは更新されないので、内容が古い可能性がある。

→ 削除して問題ない。残す場合は `index.html` と同期が取れていないことを前提に扱う。

## iOS化までに必要なこと

1. アイコン作成（`icon.svg` → 192 / 512 / apple-touch-icon）
2. PWA対応（`manifest.json` / `sw.js`）— `mahjong/` のものを写して書き換え
3. `ios-app/` の構築 — [../CLAUDE.md](../CLAUDE.md) の5章
4. 触覚フィードバックの組み込み（審査対策）
