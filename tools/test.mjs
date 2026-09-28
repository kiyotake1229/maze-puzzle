// MAZE の自動テスト
// index.html のスクリプトをそのまま Node で動かし（画面の部品は最小限の偽物で置き換える）、
// 迷路の作り方・★・記録・デイリーなどの決まりごとが守られているかを確かめる。
// 使い方: node tools/test.mjs（要 Node.js 18 以降。ほかに入れるものは無い）
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
// MAZE_HTML で別のファイルを指定できる（わざと壊したコピーで、テストが失敗することを確かめる用）
const html = fs.readFileSync(process.env.MAZE_HTML || path.join(root, 'index.html'), 'utf8');
const script = html.slice(html.lastIndexOf('<script>') + 8, html.lastIndexOf('</script>'));

// ---- ブラウザの代わり（テストに必要な分だけ） ----
function makeApp({ capacitor } = {}) {
  const storage = new Map();
  const els = new Map();
  const makeEl = id => {
    const classes = new Set();
    return {
      id, textContent: '', innerHTML: '', className: '', style: { setProperty() {} }, dataset: {}, onclick: null,
      clientWidth: 400, clientHeight: 400,
      classList: {
        add: c => classes.add(c), remove: (...cs) => cs.forEach(c => classes.delete(c)), contains: c => classes.has(c),
        toggle: (c, on) => { const v = on === undefined ? !classes.has(c) : !!on; v ? classes.add(c) : classes.delete(c); return v; },
      },
      addEventListener() {}, querySelector: () => makeEl(''), getContext: () => ctx2d,
      click() { if (this.onclick) this.onclick(); },
    };
  };
  const get = id => { if (!els.has(id)) els.set(id, makeEl(id)); return els.get(id); };
  const ctx2d = new Proxy({}, { get: (t, p) => (p in t ? t[p] : () => ({ addColorStop() {} })), set: (t, p, v) => ((t[p] = v), true) });
  const localStorage = new Proxy({}, {
    get: (t, p) => ({
      getItem: k => (storage.has(k) ? storage.get(k) : null), setItem: (k, v) => storage.set(k, String(v)),
      removeItem: k => storage.delete(k), clear: () => storage.clear(),
    })[p],
    ownKeys: () => [...storage.keys()],
    getOwnPropertyDescriptor: (t, p) => (storage.has(p) ? { enumerable: true, configurable: true, value: storage.get(p) } : undefined),
  });
  const clock = { now: 0 };
  class AudioContext {
    constructor() { this.state = 'running'; this.currentTime = 0; this.destination = {}; }
    resume() {}
    createOscillator() { return { type: '', frequency: { value: 0 }, connect() {}, start() {}, stop() {} }; }
    createGain() { return { gain: { setValueAtTime() {}, exponentialRampToValueAtTime() {} }, connect() {} }; }
  }
  const document = {
    getElementById: get,
    querySelector: sel => (sel === '.overlay.show' ? ['overlay', 'achvOverlay'].map(get).find(e => e.classList.contains('show')) || null : null),
    querySelectorAll: () => [],
    documentElement: { setAttribute() {}, removeAttribute() {}, getAttribute() {} },
  };
  const ctx = {
    document, localStorage, AudioContext, console,
    navigator: { vibrate: () => true },
    location: { href: 'https://kiyotake1229.github.io/maze-puzzle/' },
    performance: { now: () => clock.now },
    devicePixelRatio: 1, innerWidth: 400, innerHeight: 800,
    matchMedia: () => ({ matches: false }), addEventListener() {},
    getComputedStyle: () => ({ getPropertyValue: () => '#123456' }),
    requestAnimationFrame: () => 0, cancelAnimationFrame() {},
    setTimeout: () => 0, clearTimeout() {}, setInterval: () => 0, clearInterval() {},
    Capacitor: capacitor,
  };
  ctx.window = ctx;
  vm.createContext(ctx);
  storage.set('maze_settings', JSON.stringify({ themeIdx: 0, soundOn: false, fogOn: false, mode: 'normal', bgmOn: false }));
  vm.runInContext(script, ctx);
  vm.runInContext(HELPERS, ctx);
  const ev = code => vm.runInContext(code, ctx);
  return { ev, storage, clock, get };
}

// テストだけで使う道具（アプリのグローバル変数を読むので、アプリと同じ場所で動かす）
const HELPERS = `
// 別の書き方で求めた最短マス数（二分ヒープ）。bestRoute の答え合わせ用
function refRoute(need) {
  const gi = new Map(gems.map((g, i) => [g.x + ',' + g.y, i]));
  const heap = [], push = e => { heap.push(e); let i = heap.length - 1; while (i) { const p = (i - 1) >> 1; if (heap[p][0] <= heap[i][0]) break; [heap[p], heap[i]] = [heap[i], heap[p]]; i = p; } };
  const pop = () => { const top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < heap.length && heap[l][0] < heap[m][0]) m = l; if (r < heap.length && heap[r][0] < heap[m][0]) m = r; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; i = m; } } return top; };
  const dist = new Map(); let best = Infinity; const s0 = [0, 0, 0, key ? 0 : 1]; dist.set(s0.join(), 0); push([0, s0]);
  while (heap.length) {
    const [d, s] = pop(); if (d > dist.get(s.join()) || d >= best) continue;
    for (const dir of ['up', 'right', 'down', 'left']) {
      let [x, y, mask, kg] = s, steps = 0, atGoal = false;
      for (;;) {
        if (cellAt(x, y).walls[wallIdx[dir]]) break;
        if (door && !kg && isDoorEdge(x, y, dir)) break;
        x += dir === 'right' ? 1 : dir === 'left' ? -1 : 0; y += dir === 'down' ? 1 : dir === 'up' ? -1 : 0; steps++;
        const g = gi.get(x + ',' + y); if (g !== undefined) mask |= 1 << g;
        if (key && !kg && key.x === x && key.y === y) kg = 1;
        if (x === goal.x && y === goal.y) { atGoal = true; break; }
        if (hasBranch(x, y, dir)) break;
      }
      if (!steps) continue;
      const nd = d + steps;
      if (atGoal) { if ((mask & need) === need) best = Math.min(best, nd); continue; }
      const ns = [x, y, mask, kg], k = ns.join();
      if (!dist.has(k) || nd < dist.get(k)) { dist.set(k, nd); push([nd, ns]); }
    }
  }
  return best;
}
// 今いる場所から、need の宝石を取ってゴールする最短の操作（方向の並び）
function planRoute(need) {
  const gemAt = new Map(gems.map((g, i) => [g.x + ',' + g.y, i])), seen = new Set();
  const got0 = gems.reduce((m, g, i) => g.got ? m | 1 << i : m, 0);
  const buckets = [[{ s: [player.x, player.y, got0, key && !key.got ? 1 : 0], prev: null }]];
  for (let d = 0; d < buckets.length; d++) for (const e of buckets[d] || []) {
    if (e.s === 'goal') { const dirs = []; for (let c = e; c.prev; c = c.prev) dirs.push(c.dir); return dirs.reverse(); }
    const id = e.s.join(); if (seen.has(id)) continue; seen.add(id);
    for (const dir in wallIdx) {
      let [x, y, got, locked] = e.s, steps = 0;
      while (!cellAt(x, y).walls[wallIdx[dir]] && !(locked && isDoorEdge(x, y, dir))) {
        x += dir === 'right' ? 1 : dir === 'left' ? -1 : 0; y += dir === 'down' ? 1 : dir === 'up' ? -1 : 0; steps++;
        if (gemAt.has(x + ',' + y)) got |= 1 << gemAt.get(x + ',' + y);
        if (locked && x === key.x && y === key.y) locked = 0;
        if ((x === goal.x && y === goal.y) || hasBranch(x, y, dir)) break;
      }
      if (!steps) continue;
      const atGoal = x === goal.x && y === goal.y;
      if (atGoal && (got & need) !== need) continue;
      (buckets[d + steps] = buckets[d + steps] || []).push({ s: atGoal ? 'goal' : [x, y, got, locked], prev: e, dir });
    }
  }
  return null;
}
function play(dirs) { for (const d of dirs) move(d); }
// スタートから、ゴールと（鍵を取る前の）扉を通らずに行けるマス
function reachable(blockDoor) {
  const seen = new Set(['0,0']), q = [[0, 0]];
  while (q.length) {
    const [x, y] = q.shift(), c = cellAt(x, y);
    for (const [dir, w, dx, dy] of [['up', 0, 0, -1], ['right', 1, 1, 0], ['down', 2, 0, 1], ['left', 3, -1, 0]]) {
      if (c.walls[w] || (blockDoor && isDoorEdge(x, y, dir))) continue;
      const nx = x + dx, ny = y + dy, k = nx + ',' + ny;
      if (seen.has(k) || (nx === goal.x && ny === goal.y)) continue;
      seen.add(k); q.push([nx, ny]);
    }
  }
  return seen;
}
function mazeHash() {
  const s = JSON.stringify([grid.map(c => c.walls.map(w => w ? 1 : 0).join('')).join(''), gems.map(g => [g.x, g.y]), key && [key.x, key.y], door && [door.ax, door.ay, door.bx, door.by]]);
  let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h.toString(16);
}
function startNow() { document.getElementById('overlay').classList.remove('show'); started = true; }
`;

// ---- テストの進め方 ----
const results = [];
function test(name, fn) {
  try { fn(); results.push([true, name]); }
  catch (e) { results.push([false, name, e.message]); }
}
function check(cond, msg) { if (!cond) throw new Error(msg); }

// ---- 迷路の作り方 ----
const configs = [['normal', 1], ['normal', 2], ['normal', 5], ['normal', 10], ['time', 3], ['hard', 1], ['hard', 10], ['daily', 1]];
for (const [m, lv] of configs) {
  test(`迷路の形（${m} Level ${lv}）: 道は木の形で全マスにつながり、ゴールは行き止まり、宝石と鍵は必ず取れる`, () => {
    const { ev } = makeApp();
    for (let i = 0; i < (m === 'daily' ? 1 : 60); i++) {
      ev(`mode = '${m}'; level = ${lv}; newLevel();`);
      const n = ev('cols'), open = ev('grid.reduce((s, c) => s + c.walls.filter(w => !w).length, 0) / 2');
      check(open === n * n - 1, `通路の数が ${open}（木なら ${n * n - 1}）`);
      check(ev('reachable(false).size') === n * n - 1, 'ゴール以外の全マスにスタートから行けない');
      check(ev('cellAt(goal.x, goal.y).walls.filter(w => !w).length') === 1, 'ゴールが行き止まりでない');
      check(ev('(() => { const r = reachable(false); return gems.every(g => r.has(g.x + "," + g.y)); })()'), 'ゴールの奥に宝石がある');
      if (ev('!!key')) {
        check(ev('reachable(true).has(key.x + "," + key.y)'), '鍵が扉の向こうにある');
        check(ev('(() => { const p = solve(); return p.some((c, i) => i && ((c.x === door.ax && c.y === door.ay && p[i-1].x === door.bx && p[i-1].y === door.by) || (c.x === door.bx && c.y === door.by && p[i-1].x === door.ax && p[i-1].y === door.ay))); })()'), '扉がゴールまでの道の上に無い');
      }
    }
  });
}

test('最短マス数（bestRoute）が別の書き方の答えと一致する（6種の大きさ × 各40面 × 3通り）', () => {
  const { ev } = makeApp();
  for (const [m, lv] of [['normal', 1], ['normal', 2], ['normal', 5], ['normal', 10], ['hard', 1], ['hard', 10]]) {
    for (let i = 0; i < 40; i++) {
      ev(`mode = '${m}'; level = ${lv}; newLevel();`);
      const full = ev('(1 << gems.length) - 1');
      for (const need of [0, full, Math.floor(Math.random() * (full + 1))]) {
        const a = ev(`bestRoute(${need})`), b = ev(`refRoute(${need})`);
        check(a === b, `${m} Level ${lv}: bestRoute(${need}) = ${a}、別解 = ${b}`);
      }
    }
  }
});

// ---- デイリー ----
test('デイリー: 2026/9/25 の迷路の指紋が 283469bc（迷路の作り方が変わっていない）', () => {
  const { ev } = makeApp();
  ev(`todayKey = () => 20260925; mode = 'daily'; newLevel();`);
  check(ev('mazeHash()') === '283469bc', `指紋が ${ev('mazeHash()')}。迷路の作り方を変えると、全員のデイリー迷路が変わる`);
});
test('デイリー: 同じ日は何度作っても同じ迷路、別の日は別の迷路、ノーマルは毎回ちがう', () => {
  const { ev } = makeApp();
  ev(`todayKey = () => 20261103; mode = 'daily'; newLevel();`); const a = ev('mazeHash()');
  ev('newLevel();'); check(ev('mazeHash()') === a, 'やり直すと迷路が変わった');
  const b = makeApp(); b.ev(`todayKey = () => 20261103; mode = 'daily'; newLevel();`);
  check(b.ev('mazeHash()') === a, '別の起動で迷路が変わった');
  ev(`todayKey = () => 20261104; newLevel();`); check(ev('mazeHash()') !== a, '次の日も同じ迷路');
  ev(`mode = 'normal'; level = 5; newLevel();`); const c = ev('mazeHash()'); ev('newLevel();');
  check(ev('mazeHash()') !== c, 'ノーマルで同じ迷路が続いた');
});
test('デイリー: 16×16・鍵あり・宝石3個・時間制限なし、Level の保存に影響しない', () => {
  const { ev, storage } = makeApp();
  ev(`todayKey = () => 20260928; setMode('daily'); startNow();`);
  check(ev('cols') === 16 && ev('!!key') && ev('gems.length') === 3, '大きさか鍵か宝石がちがう');
  play(ev, 'planRoute((1 << gems.length) - 1)');
  check(ev('document.getElementById("ov-title").textContent') === 'DAILY CLEAR!', 'クリア画面の見出しがちがう');
  check(!storage.has('maze_level_daily'), 'デイリーで Level が保存された');
  check(storage.get('maze_daily_20260928') !== undefined, 'その日の最速が保存されていない');
});

// ---- ★と記録 ----
function play(ev, route) { ev(`play(${route});`); }
test('★: 宝石を全部取る最短で★3、宝石を取らない最短で★2以上、遠回りすると手数の★が付かない', () => {
  const { ev } = makeApp();
  for (let i = 0; i < 20; i++) {
    ev(`mode = 'normal'; level = ${1 + (i % 6)}; newLevel(); startNow();`);
    play(ev, 'planRoute((1 << gems.length) - 1)');
    check(ev('lastResult.stars') === 3, `宝石全部の最短で ★${ev('lastResult.stars')}`);
    ev('newLevel(); startNow();');
    play(ev, 'planRoute(0)');
    check(ev('lastResult.stars') >= 2, `宝石なしの最短で ★${ev('lastResult.stars')}`);
  }
  // 遠回り: スタートから行って戻るを繰り返してから最短で行く
  ev(`mode = 'normal'; level = 3; newLevel(); startNow();`);
  const d0 = ev('planRoute(0)[0]'), back = { up: 'down', down: 'up', left: 'right', right: 'left' }[d0];
  for (let i = 0; i < 40; i++) ev(`move('${d0}'); move('${back}');`);
  play(ev, 'planRoute(0)');
  const taken = ev('gems.reduce((m, g, i) => g.got ? m | 1 << i : m, 0)');
  check(ev('moves') > ev(`bestRoute(${taken})`) * 1.4, 'テスト用の遠回りが足りない');
  check(ev('lastResult.stars') === 1 + (ev('gems.every(g => g.got)') ? 1 : 0), `遠回りで ★${ev('lastResult.stars')}`);
});
test('ヒント: 1迷路3回（スーパーハード1回）、動かずに押し直しても減らない、使うと★は2まで', () => {
  const { ev } = makeApp();
  ev(`mode = 'normal'; level = 1; newLevel(); startNow();`);
  check(ev('hintsLeft') === 3, 'ノーマルの回数が3でない');
  ev('showHint(); showHint();'); check(ev('hintsLeft') === 2, '動かずに押し直して減った');
  play(ev, 'planRoute((1 << gems.length) - 1)');
  check(ev('lastResult.stars') === 2, `ヒントを使って ★${ev('lastResult.stars')}`);
  ev(`setMode('hard'); startNow();`); check(ev('hintsLeft') === 1, 'スーパーハードの回数が1でない');
  ev('showHint(); move(planRoute(0)[0]); showHint();'); check(ev('hintsLeft') === 0, '回数を超えて使えた');
});
test('制限時間: タイムアタック・スーパーハードは「宝石を全部取る最短 × 0.9秒 / 0.6秒」', () => {
  const { ev } = makeApp();
  for (const [m, f, min] of [['time', 0.9, 8], ['hard', 0.6, 6]]) {
    for (let lv = 1; lv <= 6; lv++) {
      ev(`mode = '${m}'; level = ${lv}; newLevel();`);
      const expect = Math.max(min, Math.round(ev('bestRoute((1 << gems.length) - 1)') * f));
      check(ev('timeLimit') === expect, `${m} Level ${lv}: ${ev('timeLimit')} 秒（想定 ${expect} 秒）`);
    }
  }
});
test('実績画面・クリア画面が出ている間は動けない（クリアの水増しができない）', () => {
  const { ev } = makeApp();
  ev(`mode = 'normal'; level = 1; newLevel(); startNow();`);
  play(ev, 'planRoute(0)');
  const total = ev('totalCleared'), pos = ev('player.x + "," + player.y');
  ev('showAchv();');
  for (const d of ['up', 'left', 'down', 'right', 'up', 'left']) ev(`move('${d}')`);
  check(ev('player.x + "," + player.y') === pos && ev('totalCleared') === total, '実績画面の裏で動けた');
});
test('Level の保存: クリアで次の Level を保存し、モードを切り替えても続きから', () => {
  const { ev, storage } = makeApp();
  ev(`setMode('normal'); level = 1; newLevel(); startNow();`);
  play(ev, 'planRoute(0)');
  check(storage.get('maze_level_normal') === '2', 'クリア後の保存が 2 でない');
  ev(`setMode('time');`); check(ev('level') === 1, 'タイムアタックが Level 1 から始まらない');
  ev(`setMode('hard'); setMode('daily'); setMode('normal');`); check(ev('level') === 2, 'ノーマルに戻ったら続きからでない');
});
test('デイリー: 通算に入るのはその日の初回だけ。連続日数は毎日のクリアで増え、1日あけると1から', () => {
  const { ev } = makeApp();
  const day = (k) => { ev(`todayKey = () => ${k}; setMode('daily'); startNow();`); play(ev, 'planRoute(0)'); };
  day(20260926); day(20260927); day(20260928);
  check(ev('currentStreak(20260928)') === 3 && ev('!!unlocked.streak3'), `3日続けて ${ev('currentStreak(20260928)')}日`);
  const total = ev('totalCleared'); day(20260928);
  check(ev('totalCleared') === total && ev('currentStreak(20260928)') === 3, '同じ日の2回目で増えた');
  day(20260930);
  check(ev('currentStreak(20260930)') === 1, '1日あけても続いた');
  check(ev('prevDayKey(20261001)') === 20260930 && ev('prevDayKey(20270101)') === 20261231 && ev('prevDayKey(20280301)') === 20280229, '前日の計算がちがう');
});
test('記録を消す: 2回押すと maze_ の記録が消え、設定と案内の既読は残る', () => {
  const { ev, storage, clock } = makeApp();
  ev(`mode = 'normal'; level = 1; newLevel(); startNow();`); play(ev, 'planRoute(0)');
  storage.set('maze_tutorial', '1'); storage.set('other_app', 'x');
  clock.now = 10000; ev('resetRecords();');
  check(storage.has('maze_total'), '1回目で消えた');
  clock.now = 11000; ev('resetRecords();');
  const keys = [...storage.keys()].sort().join(',');
  check(keys === 'maze_settings,maze_tutorial,other_app', `残ったキー: ${keys}`);
  check(ev('totalCleared') === 0 && ev('Object.keys(unlocked).length') === 0 && ev('level') === 1, '画面の記録が 0 に戻らない');
});

// ---- iOS アプリの中（Capacitor を模す） ----
async function testAsync(name, fn) {
  try { await fn(); results.push([true, name]); }
  catch (e) { results.push([false, name, e.message]); }
}
function nativeApp() {
  const calls = [];
  const capacitor = {
    isNativePlatform: () => true,
    Plugins: {
      Haptics: {
        impact: o => (calls.push('impact:' + o.style), Promise.resolve()),
        notification: o => (calls.push('notification:' + o.type), Promise.resolve()),
      },
      LocalNotifications: {
        requestPermissions: () => (calls.push('permission'), Promise.resolve({ display: 'granted' })),
        schedule: o => (calls.push('schedule:' + JSON.stringify(o.notifications[0].schedule.on)), Promise.resolve()),
        cancel: () => (calls.push('cancel'), Promise.resolve()),
        addListener: () => Promise.resolve({ remove() {} }),
      },
    },
  };
  return { ...makeApp({ capacitor }), calls };
}
test('iOS アプリ: 触覚は壁・宝石・鍵・クリア・時間切れで Haptics を呼ぶ（Web の振動は使わない）', () => {
  const { ev, calls } = nativeApp();
  ev('navigator.vibrate = () => { throw new Error("Web の振動が呼ばれた"); };');
  ev('started = true; sfxBump(); sfxGem(); vib([20, 30], "MEDIUM"); win(); timeUp();');
  const h = calls.filter(c => /^(impact|notification)/.test(c)).join(',');
  check(h === 'impact:MEDIUM,impact:LIGHT,impact:MEDIUM,notification:SUCCESS,notification:ERROR', h);
});
await testAsync('iOS アプリ: 通知は許可のあと毎日8時に予約し、OFF で取り消す', async () => {
  const { ev, calls, storage } = nativeApp();
  check(ev('document.getElementById("notifyBtn").style.display') === '', '通知ボタンが出ていない');
  await ev('toggleNotify()');
  check(calls.join(',') === 'permission,cancel,schedule:{"hour":8,"minute":0}', calls.join(','));
  check(JSON.parse(storage.get('maze_settings')).notifyOn === true, 'ON が保存されない');
  calls.length = 0;
  await ev('toggleNotify()');
  check(calls.join(',') === 'cancel', calls.join(','));
  check(JSON.parse(storage.get('maze_settings')).notifyOn === false, 'OFF が保存されない');
});
test('Web 版では通知ボタンを出さない', () => {
  const { ev } = makeApp();
  check(ev('document.getElementById("notifyBtn").style.display') === 'none', '通知ボタンが出ている');
});

// ---- 結果 ----
let ok = 0;
for (const [pass, name, why] of results) {
  console.log(`${pass ? 'OK' : 'NG'}  ${name}${pass ? '' : `\n      → ${why}`}`);
  if (pass) ok++;
}
console.log(`\n${results.length}件中 ${ok}件 OK${ok === results.length ? '' : `、${results.length - ok}件 NG`}`);
process.exit(ok === results.length ? 0 : 1);
