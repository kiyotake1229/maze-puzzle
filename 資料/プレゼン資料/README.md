# プレゼン資料（社内説明・7枚）

- 公開URL（Claude Design。閲覧・文字の修正・PNG/PDF書き出し）: https://claude.ai/code/artifact/dad654fa-2ff3-4609-8119-1cb7d7a42d57
- PDF: `MAZE_社内説明.pdf`（このフォルダ。そのまま配れる）
- 話す台本: [../プレゼンの進め方.md](../プレゼンの進め方.md)
- `gen.py` … スライド7枚（`Main.dc.html` = 表紙、`S02`〜`S07`）と `canvas.json`、PDF用の `deck.html` を生成するスクリプト。文言を直すときはここを編集して `python3 gen.py`
- 見た目はアプリ本体（index.html）のデフォルトテーマと同じ配色（紺の地・ティール・紫・黄のプレイヤー・緑のゴール）。迷路の図はCSSグリッドで描画
- 構成：表紙 / ねらい / 遊び方（4モード） / 続ける仕掛け（テーマ・実績） / 画面の構成 / 現状 / 次のステップと費用

## PDFを作り直す

`python3 gen.py` のあと、このフォルダで:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer --virtual-time-budget=8000 --print-to-pdf="MAZE_社内説明.pdf" "file://$PWD/deck.html"
```
