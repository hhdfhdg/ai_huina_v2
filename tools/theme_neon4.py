#!/usr/bin/env python3
"""Стекло для сайдбара, панели настроек; неоновый focus полей."""
import io

TARGETS = ["/workspace/aihuina/index.html", "/workspace/aihuina/web/index.html"]

def apply(path):
    with io.open(path, encoding="utf-8") as f:
        html = f.read()

    def rep1(a, b):
        nonlocal html
        assert a in html, "NOT FOUND: " + a[:90]
        html = html.replace(a, b, 1)

    # сайдбар — glass showcase
    rep1("padding:16px 14px 12px;background:var(--surface);border:1px solid var(--line);\n  border-radius:20px;box-shadow:var(--shadow-1);overflow:hidden;",
         "padding:16px 14px 12px;background:var(--glass-bg);border:1px solid var(--glass-border);\n  border-radius:20px;box-shadow:var(--shadow-deep),var(--glass-glow);overflow:hidden;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);")

    # панель настроек — glass dialog с верхней световой кромкой
    rep1("transform:translate(-50%,-50%);background:var(--surface);border:1px solid var(--line-2);\n  border-radius:22px;box-shadow:var(--shadow-3);animation:dialogIn .24s cubic-bezier(.2,.8,.2,1) both;\n}",
         "transform:translate(-50%,-50%);background:var(--glass-bg);border:1px solid var(--glass-border);\n  border-radius:22px;box-shadow:var(--shadow-hover),var(--glass-glow);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);animation:dialogIn .24s cubic-bezier(.2,.8,.2,1) both;\n}\n.settings-panel::before{content:\"\";position:absolute;top:0;left:10%;right:10%;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.2),transparent);pointer-events:none}")

    # поля ввода — утопленные (skeuomorphic inset) + неоновый focus
    rep1(".s-input:focus{border-color:var(--accent);background:var(--surface);box-shadow:var(--ring)}",
         ".s-input:focus{border-color:var(--accent);background:var(--surface);box-shadow:var(--ring),0 0 24px rgba(139,92,246,.2)}")
    rep1("border:1px solid var(--line-2);border-radius:10px;background:var(--surface-2);color:var(--fg);font-size:14px;transition:border-color .16s,box-shadow .16s,background .16s}",
         "border:1px solid var(--glass-border);border-radius:10px;background:linear-gradient(180deg,#1a1a1e 0%,#131316 100%);color:var(--fg);font-size:14px;box-shadow:inset 0 2px 6px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.05);transition:all .35s cubic-bezier(.25,.8,.25,1)}")

    # поиск в сайдбаре — тот же inset-стиль
    m = html.find(".search input{")
    assert m != -1
    seg = html[m:m+400]
    end = seg.find("}")
    rule = seg[:end+1]
    if "background:var(--surface-2)" in rule or "background:var(--surface)" in rule:
        newrule = rule.replace("background:var(--surface-2)", "background:linear-gradient(180deg,#1a1a1e 0%,#131316 100%)").replace("background:var(--surface)", "background:linear-gradient(180deg,#1a1a1e 0%,#131316 100%)")
        newrule = newrule[:-1] + "box-shadow:inset 0 2px 6px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.05)}"
        html = html[:m] + newrule + html[m+end+1:]

    # textarea инпута чата — inset как трек слайдера showcase
    m = html.find("#input{")
    if m != -1:
        seg = html[m:m+500]; end = seg.find("}")
        rule = seg[:end+1]
        if "background" in rule:
            import re as _re
            newrule = _re.sub(r"background:[^;]+;", "background:linear-gradient(180deg,#1a1a1e 0%,#131316 100%);box-shadow:inset 0 2px 8px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.05);", rule, count=1)
            html = html[:m] + newrule + html[m+end+1:]

    with io.open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("ok:", path)

for t in TARGETS:
    apply(t)
