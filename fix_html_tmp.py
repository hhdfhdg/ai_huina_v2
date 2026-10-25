from pathlib import Path

p = Path('/workspace/aihuina/web/index.html')
s = p.read_text(encoding='utf-8')

# 1) Fix broken EMPTY_HTML concatenation (missing semicolon)
old1 = " +'<p>Опишите задачу в поле ниже. Я помогу с кодом, файлами, анализом и автоматизацией.</p>'\n\nlet ws=null"
new1 = " +'<p>Опишите задачу в поле ниже. Я помогу с кодом, файлами, анализом и автоматизацией.</p>';\n\nlet ws=null"
assert s.count(old1) == 1, "anchor1"
s = s.replace(old1, new1)

# 2) Insert real settings panel body before the stray modal div
old2 = '''    <button type="button" class="icon-x" id="settingsClose" aria-label="Закрыть">×</button>
  </div>

<div class="modal" id="fp"'''
new2 = '''    <button type="button" class="icon-x" id="settingsClose" aria-label="Закрыть">×</button>
  </div>

  <div class="s-group">
    <div class="s-group-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/></svg>Провайдер API</div>
    <label class="s-label" for="providerSelect">Провайдер</label>
    <select class="s-input" id="providerSelect"></select>
    <label class="s-label" for="apiUrlInput">API URL</label>
    <input class="s-input" id="apiUrlInput" spellcheck="false" autocomplete="off" placeholder="https://api.openai.com/v1 или http://127.0.0.1:1234/v1">
    <label class="s-label" for="apiKeyInput">API-ключ</label>
    <input class="s-input" id="apiKeyInput" type="password" spellcheck="false" autocomplete="new-password" placeholder="sk-…">
    <label class="s-clear-key"><input type="checkbox" id="clearApiKey"> Удалить сохранённый ключ</label>
    <div class="s-hint" id="apiKeyHint"></div>
    <button type="button" class="s-save" id="apiSaveBtn">Сохранить API</button>
  </div>

  <div class="s-group">
    <div class="s-group-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/></svg>Рабочая папка</div>
    <label class="s-label" for="wdInput">Путь к папке проекта</label>
    <div class="s-row">
      <input class="s-input" id="wdInput" spellcheck="false" autocomplete="off" placeholder="/path/to/project" style="flex:1">
      <button type="button" class="s-mini" id="wdBrowseBtn" title="Обзор папок">↑</button>
    </div>
    <button type="button" class="s-save secondary" id="wdSaveBtn">Применить папку</button>
  </div>
</div>

<div class="modal" id="fp"'''
assert s.count(old2) == 1, "anchor2"
s = s.replace(old2, new2)

# 3) Guard checklist/ask rendering during history replay
old3 = """    case 'checklist': renderChecklist(e.items||[]); break;
    case 'ask': renderAskCard(e.info||{}); break;"""
new3 = """    case 'checklist': if(!replaying) renderChecklist(e.items||[]); break;
    case 'ask': if(!replaying) renderAskCard(e.info||{}); break;"""
assert s.count(old3) == 1, "anchor3"
s = s.replace(old3, new3)

p.write_text(s, encoding='utf-8')
print("html fixes ok")
