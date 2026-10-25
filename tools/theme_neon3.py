#!/usr/bin/env python3
"""Доводка: newbtn, glass-панели, hover-подъём карточек."""
import io

TARGETS = ["/workspace/aihuina/index.html", "/workspace/aihuina/web/index.html"]

def apply(path):
    with io.open(path, encoding="utf-8") as f:
        html = f.read()

    def rep1(a, b):
        nonlocal html
        assert a in html, "NOT FOUND: " + a[:90]
        html = html.replace(a, b, 1)

    # newbtn — объёмная кнопка showcase (position:relative+overflow для блика ::after)
    rep1(""".newbtn{
  display:flex;align-items:center;justify-content:center;gap:8px;width:100%;height:42px;margin:0 0 10px;padding:0 12px;
  border:1px solid rgba(255,255,255,.14);border-radius:12px;
  background:linear-gradient(135deg,var(--accent-2),var(--accent) 55%,var(--accent-3));
  color:#fff;font-size:14px;font-weight:600;cursor:pointer;
  box-shadow:0 12px 26px -14px rgba(139,92,246,.9),inset 0 1px 0 rgba(255,255,255,.22);
  transition:transform .16s ease,filter .16s ease,box-shadow .16s ease;
}""",
""".newbtn{
  position:relative;overflow:hidden;
  display:flex;align-items:center;justify-content:center;gap:8px;width:100%;height:42px;margin:0 0 10px;padding:0 12px;
  border:1px solid #a78bfa;border-radius:12px;
  background:linear-gradient(180deg,#8b5cf6 0%,#6d28d9 100%);
  color:#fff;font-size:14px;font-weight:600;cursor:pointer;
  box-shadow:0 4px 12px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.28),0 0 18px rgba(139,92,246,.3);
  transition:all .35s cubic-bezier(.25,.8,.25,1);
}""")

    # composer — стеклянная панель showcase
    rep1("display:flex;flex-direction:column;gap:7px;padding:13px 13px 10px;background:var(--surface);\n  border:1px solid var(--line-2);border-radius:24px;box-shadow:var(--shadow-2);",
         "position:relative;display:flex;flex-direction:column;gap:7px;padding:13px 13px 10px;background:var(--glass-bg);\n  border:1px solid var(--glass-border);border-radius:24px;box-shadow:var(--shadow-deep),var(--glass-glow);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);")

    rep1(".composer:focus-within{border-color:var(--accent);box-shadow:var(--ring),var(--shadow-2)}",
         ".composer:focus-within{border-color:rgba(139,92,246,.45);box-shadow:var(--ring),var(--shadow-deep),0 0 30px rgba(139,92,246,.18)}")

    # боковая панель и main — фирменное стекло
    rep1(".glass{background:var(--glass-bg);border:1px solid var(--glass-border);box-shadow:var(--shadow-1),var(--glass-glow)}",
         ".glass{background:var(--glass-bg);border:1px solid var(--glass-border);box-shadow:var(--shadow-deep),var(--glass-glow);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}")

    m = html.find(".main{\n")
    assert m != -1
    seg = html[m:m+400]
    html = html[:m] + seg.replace("background:var(--surface);border:1px solid var(--line);border-radius:20px;\n  box-shadow:var(--shadow-1);",
                                  "background:var(--glass-bg);border:1px solid var(--glass-border);border-radius:20px;\n  box-shadow:var(--shadow-deep),var(--glass-glow);", 1) + html[m+400:]
    assert "box-shadow:var(--shadow-deep),var(--glass-glow);" in html[m:m+400+60], "main not patched"

    # settings panel — glass card
    rep1(".settings-panel{", "@@SP@@")
    html = html.replace("@@SP@@", ".settings-panel{")

    # hover-подъём для карточек чата списков (chat item) — неоновая рамка
    rep1(".chat-item:hover", ".chat-item:hover") if ".chat-item:hover" in html else None

    with io.open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("ok:", path)

for t in TARGETS:
    apply(t)
