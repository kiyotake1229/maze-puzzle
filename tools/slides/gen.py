# MAZE 社内説明資料（7枚）の生成。アプリ index.html の配色（デフォルトテーマ）をそのまま使う
# Python 3.9 のため f-string を入れ子にしない（部品を先に変数へ）
# 使い方: python3 tools/slides/gen.py  → このフォルダに Main.dc.html / S02〜.dc.html / canvas.json / deck.html、docs/ に PDF
#         そのあと docs/manager/generate_docs_json.sh を実行する
import json, os
OUT = os.path.dirname(os.path.abspath(__file__))
PDF_NAME = '20260915_DOC_0001_ALL_社内説明資料（MAZE）.pdf'  # docs/ の命名規則（YYYYMMDD_種別_連番_場所_内容）
APP, DATE, N = 'MAZE', '2026-09-15', 7

BG, WALL, PATH = '#0f1226', '#2b3168', '#1a1f45'
ACC, ACC2, PLAYER, GOAL = '#5eead4', '#a78bfa', '#fbbf24', '#34d399'
TEXT, MUTED, LINE = '#e5e7ff', '#8b90c4', 'rgba(229,231,255,.14)'
PAPER = '#F3F4FB'
THEMES = [('デフォルト', '#0f1226', '#2b3168', '#5eead4', '#fbbf24'), ('オーロラ', '#041b1a', '#0d4a44', '#4ade80', '#fde047'), ('サンセット', '#1c0a1e', '#5b2340', '#fb923c', '#fde68a'), ('モノ', '#0d0f12', '#3a3f47', '#e5e7eb', '#f59e0b')]

HEAD = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Noto+Sans+JP:wght@400;700;900&display=swap">
  <style>
    body { margin: 0; background: #0f1226; color: #e5e7ff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", "Hiragino Sans", "Noto Sans JP", sans-serif; -webkit-font-smoothing: antialiased; }
    a { color: #5eead4; } a:hover { color: #a78bfa; }
    .fd { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", "Hiragino Sans", "Noto Sans JP", sans-serif; font-weight: 800; }
    .fm { font-family: "Space Mono", "SFMono-Regular", Menlo, monospace; font-variant-numeric: tabular-nums; letter-spacing: .04em; }
    .ico { width: 24px; height: 24px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; flex: none; }
  </style>
</helmet>
'''
TAIL = '''</x-dc>
</body>
</html>
'''

ICON = {
 'feather': '<svg class="ico" viewBox="0 0 24 24"><path d="M20 4c-6 0-11 4-13 10l-3 6 6-3c6-2 10-7 10-13z"/><path d="M4 20l9-9"/></svg>',
 'zap': '<svg class="ico" viewBox="0 0 24 24"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg>',
 'smile': '<svg class="ico" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/></svg>',
 'swipe': '<svg class="ico" viewBox="0 0 24 24"><path d="M4 12h16M14 6l6 6-6 6"/></svg>',
 'flag': '<svg class="ico" viewBox="0 0 24 24"><path d="M5 21V4h12l-2 4 2 4H5"/></svg>',
 'layers': '<svg class="ico" viewBox="0 0 24 24"><path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/></svg>',
 'bulb': '<svg class="ico" viewBox="0 0 24 24"><path d="M9 18h6M10 21h4M8 12a4 4 0 1 1 8 0c0 2-2 3-2 5h-4c0-2-2-3-2-5z"/></svg>',
 'trophy': '<svg class="ico" viewBox="0 0 24 24"><path d="M8 21h8M12 17v4M6 4h12v4a6 6 0 0 1-12 0z"/><path d="M6 6H3v2a3 3 0 0 0 3 3M18 6h3v2a3 3 0 0 1-3 3"/></svg>',
 'palette': '<svg class="ico" viewBox="0 0 24 24"><path d="M12 3a9 9 0 1 0 0 18c1.5 0 2-1 2-2s-1-2 0-3 3 0 3-2a9 9 0 0 0-5-11z"/><circle cx="8" cy="10" r="1"/><circle cx="12" cy="7" r="1"/><circle cx="16" cy="10" r="1"/></svg>',
 'eye': '<svg class="ico" viewBox="0 0 24 24"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
 'gem': '<svg class="ico" viewBox="0 0 24 24"><path d="M6 4h12l4 6-10 11L2 10z"/><path d="M2 10h20M9 4l3 6 3-6M9 10l3 11 3-11"/></svg>',
 'music': '<svg class="ico" viewBox="0 0 24 24"><path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/></svg>',
 'check': '<svg class="ico" viewBox="0 0 24 24"><path d="M5 12l4 4L19 7"/></svg>',
 'clock': '<svg class="ico" viewBox="0 0 24 24"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2M9 3h6"/></svg>',
}

def maze(cells, size, gap=2, wall=WALL, path=PATH, player=PLAYER, goal=GOAL, trail=ACC):
    # cells: 文字列のリスト。# 壁 / . 道 / P プレイヤー / G ゴール / * 軌跡
    col = {'#': wall, '.': path, 'P': player, 'G': goal, '*': trail}
    n = len(cells[0])
    html = ''
    for row in cells:
        for ch in row:
            r = '50%' if ch in 'PG' else '2px'
            html += '<i style="display:block;background:%s;border-radius:%s"></i>' % (col[ch], r)
    return '<div style="display:grid;grid-template-columns:repeat(%d,%dpx);grid-auto-rows:%dpx;gap:%dpx;background:%s;padding:%dpx;border-radius:8px">%s</div>' % (n, size, size, gap, wall, gap, html)

MOTIF = maze(['#####', '#P..#', '#.#.#', '#..G#', '#####'], 5, 1)

def slide(n, body, eyebrow, title, title_size=44):
    foot = ('<div style="position:absolute;left:64px;bottom:30px;display:flex;align-items:center;gap:14px">'
            '<span class="fm" style="font-size:13px;color:%s">No. %02d / %02d</span>'
            '<span style="width:1px;height:14px;background:%s"></span>'
            '<span class="fm" style="font-size:12px;color:%s">%s · 社内説明 · %s</span></div>'
            '<div style="position:absolute;right:64px;bottom:28px">%s</div>') % (MUTED, n, N, LINE, MUTED, APP, DATE, MOTIF)
    head = ''
    if title:
        head = ('<div style="display:flex;flex-direction:column;gap:8px">'
                '<div class="fm" style="font-size:13px;color:%s">%s</div>'
                '<h1 class="fd" style="margin:0;font-size:%dpx;font-weight:900;line-height:1.2;letter-spacing:-.01em;color:%s;text-wrap:balance">%s</h1></div>') % (ACC, eyebrow, title_size, TEXT, title)
    glow = ('<div style="position:absolute;width:520px;height:520px;border-radius:50%%;background:radial-gradient(circle,#232a63 0%%,transparent 70%%);left:-160px;top:-200px;pointer-events:none"></div>'
            '<div style="position:absolute;width:520px;height:520px;border-radius:50%%;background:radial-gradient(circle,#3a1f5c 0%%,transparent 70%%);right:-180px;bottom:-220px;pointer-events:none"></div>')
    return HEAD + ('<div style="width:1280px;height:720px;position:relative;overflow:hidden;background:%s;padding:56px 64px 72px;box-sizing:border-box;display:flex;flex-direction:column;gap:28px">'
                   '%s<div style="position:relative;display:flex;flex-direction:column;gap:28px;flex:1;min-height:0">%s%s</div>%s</div>\n') % (BG, glow, head, body, foot) + TAIL

def paper(inner, extra=''):
    return '<div style="background:%s;color:#1a1d3a;border-radius:16px;padding:24px 26px;display:flex;flex-direction:column;gap:10px;box-shadow:0 14px 34px rgba(0,0,0,.45);%s">%s</div>' % (PAPER, extra, inner)

def card(inner, extra=''):
    return '<div style="background:%s;border:1px solid %s;border-radius:16px;padding:22px 24px;display:flex;flex-direction:column;gap:10px;%s">%s</div>' % (PATH, LINE, extra, inner)

def tag(text, color=ACC, bg='rgba(94,234,212,.14)'):
    return '<span class="fm" style="display:inline-flex;font-size:12px;padding:5px 9px;border-radius:6px;background:%s;color:%s">%s</span>' % (bg, color, text)

def head_row(icon, text, size=22, color=TEXT, icolor=ACC):
    return '<div style="display:flex;align-items:center;gap:10px;color:%s">%s<span class="fd" style="font-size:%dpx;color:%s">%s</span></div>' % (icolor, icon, size, color, text)

def p(text, size=16, color=MUTED, lh=1.8):
    return '<p style="margin:0;font-size:%spx;line-height:%s;color:%s">%s</p>' % (size, lh, color, text)

def grid(cols, items, gap=18):
    return '<div style="display:grid;grid-template-columns:repeat(%d,minmax(0,1fr));gap:%dpx;flex:1;align-content:start">%s</div>' % (cols, gap, ''.join(items))

def check_line(text, size=16):
    return '<div style="display:flex;gap:10px;align-items:flex-start;font-size:%dpx;line-height:1.7;color:%s"><span style="color:%s;margin-top:2px">%s</span><span>%s</span></div>' % (size, TEXT, GOAL, ICON['check'], text)

files = {}

# ---------- 01 表紙 ----------
big = maze(['#########', '#P**#...#', '###*#.#.#', '#..*..#.#', '#.#####.#', '#.#...#.#', '#.#.#.#.#', '#...#..G#', '#########'], 22, 3)
cover_body = ('<div style="flex:1;padding:44px 52px 40px;display:flex;flex-direction:column;gap:14px;min-width:0;justify-content:center">'
              '<div class="fm" style="font-size:14px;color:%s">社内説明 · アプリ開発 · %s</div>'
              '<div class="fd" style="font-size:120px;font-weight:900;line-height:.95;letter-spacing:.08em;color:%s">MAZE</div>'
              '<div style="font-size:26px;font-weight:700;line-height:1.5;color:%s">レベル制の迷路パズル。軽くて、すぐ遊べる</div>'
              '<div class="fm" style="display:flex;gap:28px;font-size:13px;color:%s;border-top:1px solid %s;padding-top:16px;margin-top:6px">'
              '<span>SINGLE HTML · 54KB</span><span>OFFLINE</span><span>kiyotake1229.github.io/maze-puzzle</span></div></div>') % (ACC, DATE, TEXT, MUTED, MUTED, LINE)
cover = ('<div style="display:flex;align-items:center;justify-content:center;flex:1">'
         '<div style="display:flex;align-items:center;gap:20px;width:1060px;background:%s;border:1px solid %s;border-radius:22px;box-shadow:0 30px 70px rgba(0,0,0,.6);padding:36px 40px;box-sizing:border-box">'
         '<div style="flex:none">%s</div>%s</div></div>') % (PATH, LINE, big, cover_body)
files['Main.dc.html'] = slide(1, cover, '', '')

# ---------- 02 ねらい ----------
aims = [
 ('feather', '54KBの単一HTML', '画像も音源もない。全部コードで描いて鳴らす。この一式の中でいちばん軽い。'),
 ('zap', '待ち時間ゼロ', '開いた瞬間に遊べる。読み込み画面もチュートリアルもいらない。'),
 ('smile', 'ルール説明がいらない', '迷路は誰でも知っている。スワイプするだけ。子どもから年配の方まで。'),
]
items = [paper(head_row(ICON[i], t, 26, '#1a1d3a', '#3b3f8a') + p(d, 17, '#474b6e', 1.85), 'min-height:250px') for i, t, d in aims]
body = grid(3, items, 22) + '<div style="font-size:18px;color:%s;line-height:1.7">「最小の構成で、ゲームとして成立するもの」を1本作った。iOS化のラインナップに最短で追加できる。</div>' % MUTED
files['S02.dc.html'] = slide(2, body, '01 · ねらい', '最小の構成で、ゲームとして成立させる')

# ---------- 03 遊び方 ----------
steps = [
 ('swipe', 'スワイプで動く', '上下左右になぞる。画面のボタンでも、PCなら矢印キーでも。'),
 ('gem', '宝石とスターを拾う', '道中の宝石を集める。スターは実績の条件になる。'),
 ('flag', 'ゴールで次へ', 'ゴールに着くと次のレベル。迷路は少しずつ大きく、複雑に。'),
 ('bulb', '詰まったらヒント', 'ヒントで道筋が光る。やり直しもすぐ。ストレスにしない。'),
]
items = []
for k, (i, t, d) in enumerate(steps):
    items.append(card('<div class="fm" style="font-size:12px;color:%s">STEP %d</div>' % (ACC, k + 1) + head_row(ICON[i], t) + p(d), 'min-height:250px'))
modes = ''.join(tag(m, c, b) for m, c, b in [('ノーマル', ACC, 'rgba(94,234,212,.14)'), ('スーパーハード', ACC2, 'rgba(167,139,250,.16)'), ('タイムアタック', PLAYER, 'rgba(251,191,36,.14)'), ('視界モード（暗闇）', '#1a1d3a', 'rgba(26,29,58,.1)')])
body = grid(4, items) + ('<div style="display:flex;align-items:center;gap:18px;background:%s;color:#1a1d3a;border-radius:16px;padding:18px 26px">'
                         '<span class="fd" style="font-size:24px;white-space:nowrap;flex:none">モードは4つ。</span>'
                         '<div style="display:flex;gap:8px;flex:none">%s</div>'
                         '<span style="font-size:14px;line-height:1.6;color:#5c6088;flex:1;min-width:0">視界モードは自分の周りだけ見える。スーパーハードでは常時ON。</span></div>') % (PAPER, modes.replace('font-size:12px', 'font-size:13px;white-space:nowrap'))
files['S03.dc.html'] = slide(3, body, '02 · 遊び方', 'なぞって、拾って、ゴールへ')

# ---------- 04 続ける仕掛け ----------
sw = ''
for name, bg, wall, acc, pl in THEMES:
    sw += ('<div style="display:flex;flex-direction:column;gap:8px;align-items:center">%s<span style="font-size:13px;color:%s">%s</span></div>'
           % (maze(['#######', '#P.#..#', '#.##.##', '#....G#', '#######'], 12, 2, wall, bg, pl, GOAL, acc), MUTED, name))
themes = card(head_row(ICON['palette'], 'テーマ4種', 21) + '<div style="display:flex;justify-content:space-between;gap:10px;margin-top:6px">%s</div>' % sw + p('気分で切り替える。壁・道・プレイヤーの色がまとめて変わる。', 14.5, MUTED, 1.7), 'grid-column:span 2')
ach = ['はじめの一歩', '迷路マスター', '迷宮の主', '宝石ハンター', '宝石王', 'スターコレクター', 'パーフェクト', 'スピードスター', '闇を照らす者', '大冒険家', '不屈の挑戦者']
chips = ''.join('<span style="font-size:13px;padding:5px 10px;border-radius:6px;background:%s;border:1px solid %s;color:%s">%s</span>' % (BG, LINE, TEXT, a) for a in ach)
items = [
 themes,
 card(head_row(ICON['trophy'], '実績 11種', 21) + '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px">%s</div>' % chips + p('クリア数・宝石・タイム・視界モードなど、遊び方ごとに解除される。', 14.5, MUTED, 1.7)),
 card(head_row(ICON['layers'], 'レベル制', 21) + p('クリアするたびに次のレベルへ。進み具合は端末に保存され、続きから遊べる。', 15, MUTED, 1.7), 'padding:18px 22px'),
 card(head_row(ICON['clock'], 'タイムアタック', 21) + p('同じ迷路を何秒で抜けられるか。「スピードスター」の実績につながる。', 15, MUTED, 1.7), 'padding:18px 22px'),
 card(head_row(ICON['music'], '効果音・BGM', 21) + p('Web Audio で合成。音源ファイルなし。設定でそれぞれ ON/OFF。', 15, MUTED, 1.7), 'padding:18px 22px'),
]
body = '<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:auto auto;gap:16px;align-content:start">%s</div>' % ''.join(items)
files['S04.dc.html'] = slide(4, body, '03 · 続ける仕掛け', 'テーマ・実績・タイムで、もう1面')

# ---------- 05 画面の構成 ----------
shot = ('<div style="width:300px;flex:none;background:%s;border:1px solid %s;border-radius:28px;padding:22px 18px;display:flex;flex-direction:column;gap:14px;box-shadow:0 20px 50px rgba(0,0,0,.6)">'
        '<div class="fm" style="display:flex;justify-content:space-between;font-size:12px;color:%s"><span>LEVEL 7</span><span>00:42</span><span style="color:%s">◆ 3</span></div>'
        '<div style="display:flex;justify-content:center">%s</div>'
        '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;width:150px;margin:0 auto">'
        '<i></i><i style="display:block;height:42px;border-radius:10px;background:%s;border:1px solid %s"></i><i></i>'
        '<i style="display:block;height:42px;border-radius:10px;background:%s;border:1px solid %s"></i><i style="display:block;height:42px;border-radius:10px;background:%s;border:1px solid %s"></i><i style="display:block;height:42px;border-radius:10px;background:%s;border:1px solid %s"></i></div>'
        '<div style="display:flex;gap:8px;justify-content:center">%s%s%s</div></div>') % (
    BG, LINE, MUTED, PLAYER,
    maze(['###########', '#P*#.....##', '#.*#.###..#', '#.*..#..#.#', '#.####.##.#', '#....#....#', '####.#.##.#', '#....#.#..#', '#.####.#.##', '#......#.G#', '###########'], 20, 2),
    WALL, LINE, WALL, LINE, WALL, LINE, WALL, LINE,
    tag('ヒント'), tag('やり直し'), tag('視界: OFF', MUTED, 'rgba(229,231,255,.08)'))
parts = [
 ('layers', '上：レベル・タイム・宝石', '今どこにいて、どれだけ集めたかが一目で分かる'),
 ('eye', '中：迷路', '道と壁は色で区別。通った道は軌跡として残るので、迷わない'),
 ('swipe', '下：十字ボタン', 'スワイプが苦手な人向け。片手の親指で届く位置'),
 ('bulb', '最下段：ヒント・やり直し・視界', '詰まった時の逃げ道を常に見えるところに'),
]
right = '<div style="display:flex;flex-direction:column;gap:12px;flex:1">' + ''.join(card(head_row(ICON[i], t, 19) + p(d, 14.5, MUTED, 1.65), 'padding:16px 20px;gap:6px') for i, t, d in parts) + '</div>'
body = '<div style="display:flex;gap:36px;flex:1;align-items:flex-start">%s%s</div>' % (shot, right)
files['S05.dc.html'] = slide(5, body, '04 · 画面の構成', '1画面に、必要なものだけ')

# ---------- 06 現状 ----------
done = ['Web版 完成・公開中（GitHub Pages）', '通信なし。進み具合・実績・設定は端末内のみ', 'レベル制、4モード、テーマ4種、実績11種、ヒント、効果音・BGM', 'PWA用の meta タグは設定済み。manifest と Service Worker は未作成', 'アイコン（192 / 512 / apple-touch）は未作成', '触覚フィードバックは未実装（審査対策として追加が必要）']
left = '<div style="display:flex;flex-direction:column;gap:9px">' + ''.join(check_line(d) for d in done) + '</div>'
right = paper('<div class="fm" style="font-size:12px;color:#5c6088">いま触れる</div>'
              '<div class="fd" style="font-size:22px;line-height:1.3">kiyotake1229.github.io/maze-puzzle/</div>'
              '<div style="font-size:15px;line-height:1.8;color:#474b6e">スマホのブラウザで開くだけ。読み込みは一瞬。</div>'
              '<div class="fm" style="display:flex;flex-wrap:wrap;gap:8px;border-top:1px dashed #c9cce0;padding-top:14px;font-size:12px;color:#5c6088"><span>単一 HTML</span><span>·</span><span>通信なし</span><span>·</span><span>端末内保存</span><span>·</span><span>約 54KB</span></div>', 'min-height:300px;justify-content:center')
body = '<div style="display:grid;grid-template-columns:minmax(0,1fr) 440px;gap:40px;flex:1;align-content:start">%s%s</div>' % (left, right)
files['S06.dc.html'] = slide(6, body, '05 · 現状', 'Web版は完成。PWA と iOS はこれから')

# ---------- 07 次のステップ ----------
road = [
 ('1', 'アイコンと PWA', 'icon.svg から 192 / 512 / apple-touch を生成。manifest.json と sw.js は麻雀のものを写して書き換え', '半日'),
 ('2', 'iOS 化', 'Capacitor で包む。コツコツの ios-app を雛形に。触覚フィードバックを組み込む（審査対策）', '半日'),
 ('3', '申請', '年齢制限 4+、カテゴリ「ゲーム／パズル」、「データを収集しません」、スクリーンショット3サイズ', '—'),
]
items = [card('<div class="fm" style="font-size:44px;font-weight:700;line-height:1;color:%s">%s</div><div class="fd" style="font-size:22px">%s</div>%s<div class="fm" style="font-size:12px;color:%s;border-top:1px solid %s;padding-top:10px">目安 %s</div>' % (ACC, n, t, p(d, 15, MUTED, 1.75).replace('<p style="', '<p style="flex:1;'), MUTED, LINE, w), 'min-height:270px') for n, t, d, w in road]
cost = paper('<div class="fm" style="font-size:12px;color:#5c6088">費用</div><div style="display:flex;align-items:baseline;gap:10px"><span class="fd" style="font-size:36px">¥12,800</span><span style="font-size:15px;color:#5c6088">/ 年 · Apple Developer Program のみ</span></div><div style="font-size:14px;color:#474b6e">素材もサーバーも使っていないので、他の費用は0</div>', 'flex:1;padding:18px 24px;gap:6px')
decide = card('<div class="fm" style="font-size:12px;color:%s">今日決めたいこと</div><div style="font-size:18px;font-weight:700;line-height:1.6">MAZE を iOS 化のラインナップに入れるか。軽いので、まとめて申請する「数」を増やす候補になる。</div>' % ACC, 'flex:1;padding:18px 24px;gap:6px;justify-content:center')
body = grid(3, items) + '<div style="display:flex;gap:20px">%s%s</div>' % (cost, decide)
files['S07.dc.html'] = slide(7, body, '06 · 次のステップ', '1日あれば iOS 化まで届く')

# ---------- 書き出し ----------
for name, src in files.items():
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(src)

names = ['Main.dc.html'] + ['S%02d.dc.html' % i for i in range(2, N + 1)]
W, H, GX, GY = 1280, 720, 80, 140
boards = []
for i, f in enumerate(names):
    r, c = divmod(i, 5)
    boards.append({'file': f, 'x': c * (W + GX), 'y': r * (H + GY), 'w': W, 'h': H, 'title': '%02d' % (i + 1)})
json.dump({'artboards': boards, 'launch': {'view': 'focused', 'file': 'Main.dc.html'}}, open(os.path.join(OUT, 'canvas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# PDF 用（全スライドを1ページずつ並べたHTML。Chrome で印刷して PDF にする）
helmet = HEAD.split('<helmet>')[1].split('</helmet>')[0]
pages = ''.join('<div style="width:1280px;height:720px;page-break-after:always;overflow:hidden">%s</div>' % files[f].split('</helmet>\n')[1].split('</x-dc>')[0] for f in names)
deck = '<!doctype html><html><head><meta charset="utf-8"><title>%s 社内説明</title>%s<style>@page{size:1280px 720px;margin:0}html,body{margin:0}</style></head><body>%s</body></html>' % (APP, helmet, pages)
open(os.path.join(OUT, 'deck.html'), 'w', encoding='utf-8').write(deck)
print('written', len(files))

# PDF（docs/ に書き出す。Chrome が無い環境ではスキップ）
import subprocess
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PDF = os.path.normpath(os.path.join(OUT, '..', '..', 'docs', PDF_NAME))
if os.path.exists(CHROME):
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--virtual-time-budget=8000',
                    '--print-to-pdf=' + PDF, 'file://' + os.path.join(OUT, 'deck.html')],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    print('pdf', PDF)
else:
    print('Chrome が見つからないため PDF は作っていません')
