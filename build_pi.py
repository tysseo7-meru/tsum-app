# Derive the Pi test build from the browser build (~/workspace/tsum-app/index.html)
src = open('/home/hatch/workspace/tsum-app/index.html', encoding='utf-8').read()
import re
ver = re.search(r"'Tsum v(\d+)'", src).group(1)
s = src
s = s.replace('<title>つむP</title>', '<title>つむP</title>\n<script src="https://sdk.minepi.com/pi-sdk.js"></script>', 1)
s = s.replace("'Tsum v" + ver + "'", "'Tsum Pi Test v" + ver + "'", 1)
s = s.replace("const GIFTS_ENABLED = false;", "const GIFTS_ENABLED = true;", 1)
old_id = """  // ---------------- player identity (browser build: local id) ----------------
  let PLAYER = null;
  try {
    let pid = localStorage.getItem('tsumPlayerId');
    if (!pid) { pid = 'local:' + Date.now().toString(36) + Math.floor(Math.random() * 1e6).toString(36); localStorage.setItem('tsumPlayerId', pid); }
    PLAYER = { id: pid, name: 'ゲスト' };
  } catch (e) { PLAYER = { id: 'local:anon', name: 'ゲスト' }; }"""
new_id = """  // ---------------- player identity (Pi build: set by Pi.authenticate below) ----------------
  let PLAYER = null;
  const PI_SANDBOX = true;   // testnet app
  const PINET_URL = '';"""
assert old_id in s; s = s.replace(old_id, new_id, 1)
s = s.replace("  function startSync() {\n", "  function startSync() {\n    if (!PLAYER) return;\n", 1)
s = s.replace("document.getElementById('userLine').textContent = 'プレイヤー： ' + PLAYER.name;",
              "document.getElementById('userLine').textContent = PLAYER ? ('プレイヤー： ' + PLAYER.name) : 'サインイン中…';", 1)
s = s.replace('<button class="btn" id="startBtn">スタート</button>', '<button class="btn" id="startBtn" disabled>スタート</button>', 1)
gate = """
<style>
  #pi-gate { position: fixed; inset: 0; z-index: 60; background: #0b2440; color: #fff;
             display: flex; flex-direction: column; align-items: center; justify-content: center;
             gap: 16px; padding: 24px; text-align: center; font-family: inherit; }
  #pi-gate a { color: #cfe8ff; font-weight: 700; }
</style>
<div id="pi-gate">
  <p id="gateMsg">サインイン中…</p><p id="gateHelp" style="display:none">このブラウザではサインインできません。<br>Piブラウザで開いてください。</p>
  <a id="pinetLink" href="#" style="display:none">PiNetで開く</a>
</div>
<script>
  const gateEl = document.getElementById('pi-gate');
  const pinetLink = document.getElementById('pinetLink');
  if (PINET_URL) { pinetLink.href = PINET_URL; pinetLink.style.display = ''; }
  function showGate() { document.getElementById('gateMsg').style.display = 'none'; document.getElementById('gateHelp').style.display = ''; }
  if (typeof Pi === 'undefined') {
    showGate();
  } else {
    try {
      Pi.init({ version: '2.0', sandbox: PI_SANDBOX });
      Pi.authenticate(['username'], function (payment) { /* no payments in this app */ })
        .then(function (auth) {
          PLAYER = { id: 'pi:' + auth.user.uid, name: auth.user.username };
          gateEl.style.display = 'none';
          document.getElementById('userLine').textContent = 'サインイン済み： ' + PLAYER.name;
          renderTitle();
          startSync();
        })
        .catch(function () { showGate(); });
    } catch (e) { showGate(); }
  }
  setTimeout(function () { if (!PLAYER) showGate(); }, 9000);
</script>
</body>"""
s = s.replace('</body>', gate, 1)
assert 'pi-sdk.js' in s, 'Pi SDK injection failed - title string mismatch?'
assert 'Pi.authenticate' in s, 'Pi gate block missing'
open('/home/hatch/workspace/tsum-app-pi-test/index.html', 'w', encoding='utf-8').write(s)
print('pi build regenerated, v' + ver)
