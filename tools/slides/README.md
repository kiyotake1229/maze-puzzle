# スライド生成（社内説明資料 #0001）

社内説明スライド（7枚）の生成元。できあがった文書は `docs/` にある。

- 公開URL（Claude Design。閲覧・文字の修正・PNG/PDF書き出し）: https://claude.ai/code/artifact/dad654fa-2ff3-4609-8119-1cb7d7a42d57
- PDF: [docs/20260915_DOC_0001_ALL_社内説明資料（MAZE）.pdf](../../docs/20260915_DOC_0001_ALL_社内説明資料（MAZE）.pdf)
- 説明文書: [docs/20260915_DOC_0001_ALL_社内説明資料（MAZE）.md](../../docs/20260915_DOC_0001_ALL_社内説明資料（MAZE）.md)
- 話す台本: [docs/20260915_DOC_0002_ALL_プレゼンの進め方（MAZE）.md](../../docs/20260915_DOC_0002_ALL_プレゼンの進め方（MAZE）.md)
- `gen.py` … スライド7枚（`Main.dc.html` = 表紙、`S02`〜）と `canvas.json`、PDF用の `deck.html` を生成し、PDF を `docs/` に書き出す
- 見た目はアプリ本体（index.html）のデフォルトテーマと同じ配色（紺の地・ティール・紫・黄のプレイヤー・緑のゴール）。迷路の図はCSSグリッドで描画
- 構成：表紙 / ねらい / 遊び方（4モード） / 続ける仕掛け（テーマ・実績） / 画面の構成 / 現状 / 次のステップと費用

## 作り直す

文言は `gen.py` を直す。アプリのフォルダで:

```bash
python3 tools/slides/gen.py
```

```bash
bash docs/manager/generate_docs_json.sh
```
