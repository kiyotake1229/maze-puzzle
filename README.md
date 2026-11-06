# MAZE — 迷路パズル

レベル制の迷路パズル。スワイプ／ボタンで移動し、ゴールを目指す。

| 項目 | 内容 |
|---|---|
| 状態 | Web版 完成 |
| Web公開 | https://kiyotake1229.github.io/maze-puzzle/ （GitHub Pages） |
| 本体 | `index.html`（約48KB） |
| 通信 | なし（完全オフライン） |
| データ | 端末内のみ |
| PWA | 対応済み（ホーム画面に追加可。一度開けば通信なしで起動。docs #0014） |
| iOS | プロジェクト作成済み（`ios-app/`。Bundle ID `work.ltv.maze`）。GitHub Actions（Xcode 26）でビルド確認済み（実機は未確認）。プライバシーマニフェストと暗号化の申告あり（docs #0025）。手順は [ios-app/岩崎さんへの引き渡し手順.md](ios-app/岩崎さんへの引き渡し手順.md) |
| サポート | https://kiyotake1229.github.io/maze-puzzle/support.html （プライバシーポリシーを含む） |

---

## 社内説明資料

岩崎さんに説明するときの資料一式は `資料/` にある（開発ドキュメントとは別）。

| 資料 | 場所 |
|---|---|
| スライド（Claude Design。閲覧・修正・PDF書き出し） | https://claude.ai/code/artifact/dad654fa-2ff3-4609-8119-1cb7d7a42d57 |
| スライド（PDF） | `資料/プレゼン資料/MAZE_社内説明.pdf` |
| 話す台本 | [資料/プレゼンの進め方.md](資料/プレゼンの進め方.md) |
| スライドの生成元 | `資料/プレゼン資料/gen.py`（文言を直して `python3 資料/プレゼン資料/gen.py`） |

## 開発ドキュメント

開発の記録は `docs/` で管理している。命名規則・連番のルールは [docs/README.md](docs/README.md)。

- 現状の仕様と構成（最初の1本）: [docs/20260915_DOC_0001_ALL_現状の仕様と構成.md](docs/20260915_DOC_0001_ALL_現状の仕様と構成.md)
- 機能追加・バグ修正・改善をしたら、1件ごとに文書を足して `bash docs/manager/generate_docs_json.sh` を実行する（一覧: `docs/manager/docs.json`）

---

## 主な機能

- レベル制。クリアで次のレベルへ。進み具合はモードごとに保存され、続きから遊べる（スタート画面から Level 1 にも戻せる）
- モード切替（ノーマル / タイムアタック / スーパーハード / デイリー）
- デイリー: 日付ごとに全員が同じ迷路。その日の最速タイムと連続日数を記録し、結果をシェアできる
- テーマ切替（ネオン / オーロラ / サンセット / モノ）
- ヒント（1つの迷路で3回まで。スーパーハードは1回。使うとその迷路の★は2つまで）、やり直し
- 実績システム（条件を満たすと解除）
- 効果音・BGM の ON/OFF
- iOS アプリ版のみ: 触覚フィードバック、毎朝8時の「今日の迷路」通知（ON/OFF）

## ファイル構成

```
MAZE/
  index.html            アプリ本体（HTML・CSS・JavaScript を1ファイルに）
  manifest.json         PWA の設定（名前・アイコン）
  sw.js                 Service Worker（通信なしで起動するための保存。更新時は CACHE の番号を上げる）
  icon.svg              アイコンの元データ
  icon-192.png / icon-512.png / icon-512-maskable.png / apple-touch-icon.png
                        icon.svg から作った PNG（bash tools/make-icons.sh で作り直せる）
  tools/make-icons.sh   アイコンの書き出しスクリプト（要 Node.js）
  tools/test.mjs        自動テスト（node tools/test.mjs。下の「テスト」参照）
  tools/make-screenshots.mjs  App Store 用スクリーンショットを作る（node tools/make-screenshots.mjs。要 Node.js 22 以降と Chrome）
  tools/screenshot-frame.html スクリーンショットの台紙（見出しとアプリ画面を並べる）
  support.html          サポートページ（遊び方・よくある質問・プライバシーポリシー・問い合わせ先）
  report.html           開発報告書（2026-08-21 時点。岩崎さん向け。ブラウザで開ける）
  ios-app/              iOS アプリ（Capacitor 7）。岩崎さんへの引き渡し手順.md、App Store 用スクリーンショット（screenshots/）あり
                        node_modules/ は Dropbox を軽くするため消してある（使うときは npm install）
  .github/workflows/ios-build.yml  iOS のビルド確認（GitHub Actions。push で動く。Xcode 26 に固定。docs #0025）
```

以前あった `maze-artifact.html`（Artifact 公開用の古いコピー）は、`index.html` をそのまま公開できるようになって不要になったため削除した（docs #0009）。

## テスト

index.html を直したら、コミットの前に次を実行する（要 Node.js。ほかに入れるものは無い）。

```bash
node tools/test.mjs
```

- 迷路の形、宝石・鍵が必ず取れること、最短ルートの計算、★、制限時間、デイリー、進み具合の保存、連続記録、ヒント、記録の消去、iOS アプリの触覚・通知（模した環境）を確かめる。全件 OK なら終了コード 0
- 「デイリー: 2026/9/25 の迷路の指紋」が NG になったら、迷路の作り方が変わって全員のデイリー迷路が変わるということ。意図した変更なら、テストの期待値を新しい指紋に書き換え、docs に記録する

## iOS化の状況

1. ~~アイコン作成（`icon.svg` → 192 / 512 / apple-touch-icon）~~ 済み（#0014）
2. ~~PWA対応（`manifest.json` / `sw.js`）~~ 済み（#0014）
3. ~~`ios-app/` の構築~~ 済み（#0016）
4. ~~触覚フィードバックの組み込み（審査対策）~~ 済み（#0016）
5. ~~サポートページ・プライバシーポリシー~~ 済み（#0015）
6. ~~毎朝の通知（ローカル通知）~~ 済み（#0020）
7. ~~App Store 用スクリーンショット~~ 済み（#0023。`ios-app/screenshots/`）
8. ~~プライバシーマニフェスト・暗号化の申告・ビルド確認（GitHub Actions、Xcode 26）~~ 済み（#0025）
9. **残り**: 実機確認、App Store 申請（岩崎さん） — [ios-app/岩崎さんへの引き渡し手順.md](ios-app/岩崎さんへの引き渡し手順.md)
