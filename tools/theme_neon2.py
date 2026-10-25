#!/usr/bin/env python3
"""Финальные штрихи стиля NeonUI: градиентные заголовки, блик кнопок, чистка цветов."""
import io

TARGETS = ["/workspace/aihuina/index.html", "/workspace/aihuina/web/index.html"]

def apply(path):
    with io.open(path, encoding="utf-8") as f:
        html = f.read()

    def rep1(a, b):
        nonlocal html
        assert a in html, "NOT FOUND: " + a[:90]
        html = html.replace(a, b, 1)

    # остаточный старый оттенок свечения
    html = html.replace("rgba(109,92,231,", "rgba(139,92,246,")

    # аватар бота — объёмная плитка как icon-box в showcase
    rep1("""  background:linear-gradient(145deg,#a78bfa,#6d28d9 60%,#4c1d95);color:#fff;
  box-shadow:0 6px 16px -6px rgba(139,92,246,.7),inset 0 1px 0 rgba(255,255,255,.25);""",
         """  background:linear-gradient(180deg,#8b5cf6 0%,#6d28d9 100%);color:#fff;border:1px solid rgba(167,139,250,.5);
  box-shadow:0 4px 12px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.28),0 0 16px rgba(139,92,246,.4);""")

    # градиентный неоновый заголовок чата (как h1 span в showcase)
    rep1(".h-title{", ".h-title>#ctitle, .h-title .ctitle-txt{background:linear-gradient(90deg,var(--accent-blue),var(--accent),var(--accent-pink));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 14px rgba(139,92,246,.35))}\n.h-title{")

    # верхняя световая кромка для composer и карточек настроек (glass edge showcase)
    rep1(".composer{", ".composer::before{content:\"\";position:absolute;top:0;left:10%;right:10%;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.18),transparent);pointer-events:none}\n.composer{")

    # блик на primary-кнопках (skeuomorphism ::after half-gloss)
    gloss = """.btn.primary::after,.s-save:not(.secondary)::after,.newbtn::after{content:"";position:absolute;top:0;left:0;right:0;height:50%;background:linear-gradient(180deg,rgba(255,255,255,.12),rgba(255,255,255,0) 100%);pointer-events:none;border-radius:inherit}
"""
    rep1("#send{width:40px;", gloss + "#send{width:40px;")
    # newbtn уже имеет position:relative? проверяем — добавили ранее overflow:hidden+relative
    # hover с подъёмом для btn/primary (как translateY(-2px) в showcase)
    rep1(".btn.primary:hover", ".btn.primary:hover")  # noop check existence
    html = html.replace(".btn.primary:hover{", ".btn.primary:hover{transform:translateY(-2px);", 1) if ".btn.primary:hover{" in html else html

    # toast — glass card
    rep1("background:#15181f;color:#fff;font-size:13.5px;",
         "background:var(--glass-bg);border:1px solid var(--glass-border);box-shadow:var(--shadow-deep),var(--glass-glow),0 0 24px rgba(139,92,246,.2);backdrop-filter:blur(16px);color:#fff;font-size:13.5px;")

    with io.open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("ok:", path)

for t in TARGETS:
    apply(t)
