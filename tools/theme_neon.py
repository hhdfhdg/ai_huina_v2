#!/usr/bin/env python3
"""Применяет стиль Premium Dark Glassmorphism (NeonUI showcase) к ChatAihuina UI."""
import io, re, sys

TARGETS = ["/workspace/aihuina/index.html", "/workspace/aihuina/web/index.html"]

NEW_ROOT = """:root{
  color-scheme:dark;
  --font:"Inter","Segoe UI Variable Text","Segoe UI",system-ui,-apple-system,Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:"JetBrains Mono","Cascadia Code",Consolas,ui-monospace,SFMono-Regular,Menlo,monospace;
  /* === Premium Dark Glassmorphism (NeonUI) === */
  --bg:#0a0a0c;
  --bg-2:#101014;
  --surface:#161619;
  --surface-2:#1d1d22;
  --surface-3:#2c2c31;
  --surface-glass:rgba(22,22,25,.78);
  --glass-bg:linear-gradient(180deg,rgba(30,30,34,.8) 0%,rgba(20,20,22,.9) 100%);
  --glass-border:rgba(255,255,255,.07);
  --glass-glow:inset 0 1px 0 rgba(255,255,255,.06);
  --line:var(--glass-border);
  --line-2:rgba(255,255,255,.11);
  --fg:#ffffff;
  --mut:#8e8e93;
  --dim:#6b6b78;
  --accent:#8b5cf6;
  --accent-2:#a78bfa;
  --accent-3:#7c3aed;
  --accent-blue:#3b82f6;
  --accent-pink:#ec4899;
  --accent-orange:#ff8a00;
  --accent-soft:rgba(139,92,246,.15);
  --accent-softer:rgba(139,92,246,.08);
  --ok:#34d399;
  --warn:#fbbf24;
  --err:#fb7185;
  --user-bg:#2c2c31;
  --user-fg:#f3f5fa;
  --code-bg:#0b0b0e;
  --code-fg:#e2e6ef;
  --shadow-deep:0 24px 48px -12px rgba(0,0,0,.9);
  --shadow-hover:0 32px 64px -12px rgba(0,0,0,1);
  --shadow-1:0 4px 12px rgba(0,0,0,.5);
  --shadow-2:var(--shadow-deep);
  --shadow-3:var(--shadow-hover);
  --ring:0 0 0 3px rgba(139,92,246,.22),0 0 20px rgba(139,92,246,.25);
  --transition:all .35s cubic-bezier(.25,.8,.25,1);
  --r-s:9px;--r-m:12px;--r-l:18px;--r-xl:24px;
  --b1:var(--line);--b2:var(--mut);--b3:var(--line-2);--glass-sh:var(--shadow-1);
}
"""

# глобальные цветовые замены (старый фиолетовый -> неон-violet палитры showcase)
COLOR_MAP = [
    ("rgba(139,123,255,", "rgba(139,92,246,"),
    ("rgba(99,85,230,",   "rgba(139,92,246,"),
    ("#8b7bff", "#8b5cf6"),
    ("#a99bff", "#a78bfa"),
    ("#7c6bff", "#7c3aed"),
    ("#6d5ce7", "#6d28d9"),
    ("#4c3fd1", "#4c1d95"),
    ("#5b4bd6", "#5b21b6"),
    ("#5a48d6", "#5b21b6"),
    ("#9d8dff", "#a78bfa"),
    ("#e3ddff", "#ddd6fe"),
    ("#f3f1ff", "#f5f3ff"),
    ("#c4b5fd", "#a78bfa"),
    # подсветки follow-up чипов ->统一的 violet glow
    ("border-color:rgba(167,139,250,.34)", "border-color:rgba(139,92,246,.4)"),
    ("rgba(167,139,250,.13)", "rgba(139,92,246,.14)"),
    ("rgba(167,139,250,.045)", "rgba(139,92,246,.05)"),
    # фоновая радиальная подсветка body -> как в showcase
    ("radial-gradient(1100px 720px at 88% -12%,rgba(139,92,246,.11),transparent 62%)",
     "radial-gradient(1100px 720px at 88% -12%,rgba(139,92,246,.13),transparent 62%)"),
    ("radial-gradient(900px 620px at -8% 108%,rgba(56,189,248,.05),transparent 58%)",
     "radial-gradient(circle at 50% 108%,#16121f 0%,rgba(10,10,12,0) 70%)"),
    # favicon
    ("fill='%236d5ce7'", "fill='%238b5cf6'"),
]

def apply(path):
    with io.open(path, encoding="utf-8") as f:
        html = f.read()
    orig = html

    # 1. Замена :root целиком
    m = re.search(r":root\{.*?\n\}\n", html, re.S)
    assert m, "root block not found in " + path
    html = html[:m.start()] + NEW_ROOT + html[m.end():]

    # 2. Глобальные цветовые замены
    for a, b in COLOR_MAP:
        html = html.replace(a, b)

    # 3. Точечные апгрейды стиля (skeuomorphic glass)
    def rep1(a, b):
        nonlocal html
        assert a in html, "NOT FOUND: " + a[:90]
        html = html.replace(a, b, 1)

    # стеклянные панели — фирменный градиент + внутренняя кромка showcase
    rep1(".glass{background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow-1)}",
         ".glass{background:var(--glass-bg);border:1px solid var(--glass-border);box-shadow:var(--shadow-1),var(--glass-glow)}")

    # кнопки объёмные (skeuomorphism) с бликом и неоновым hover-свечением
    rep1(".btn.primary{background:linear-gradient(135deg,var(--accent-2),var(--accent));border-color:transparent;color:#fff;box-shadow:0 8px 18px -10px rgba(139,92,246,.8)}",
         ".btn.primary{background:linear-gradient(180deg,#8b5cf6 0%,#6d28d9 100%);border-color:#a78bfa;color:#fff;box-shadow:0 4px 12px rgba(0,0,0,.5),var(--glass-glow),0 0 18px rgba(139,92,246,.35)}")

    # send-кнопка — неон
    rep1("#send{width:40px;height:40px;flex:none;display:grid;place-items:center;border:0;border-radius:50%;background:linear-gradient(135deg,var(--accent-2),var(--accent));color:#fff;cursor:pointer;box-shadow:0 8px 18px -8px rgba(139,92,246,.8),inset 0 1px 0 rgba(255,255,255,.2);transition:transform .15s,opacity .15s,background .2s,box-shadow .2s}",
         "#send{width:40px;height:40px;flex:none;display:grid;place-items:center;border:1px solid rgba(167,139,250,.6);border-radius:50%;background:linear-gradient(180deg,#8b5cf6 0%,#6d28d9 100%);color:#fff;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,.6),var(--glass-glow),0 0 20px rgba(139,92,246,.45);transition:transform .15s,opacity .15s,background .2s,box-shadow .35s cubic-bezier(.25,.8,.25,1)}")

    rep1("#send:hover:not(:disabled){transform:scale(1.06);box-shadow:0 10px 22px -8px rgba(139,92,246,.9),inset 0 1px 0 rgba(255,255,255,.24)}",
         "#send:hover:not(:disabled){transform:translateY(-2px) scale(1.04);box-shadow:0 8px 20px rgba(0,0,0,.6),var(--glass-glow),0 0 30px rgba(139,92,246,.65)}")

    # newbtn (primary CTA сайдбара) — объёмная кнопка со стеклянным бликом
    rep1("background:linear-gradient(145deg,#a78bfa,#6d28d9 52%,#4c1d95);color:#fff;",
         "background:linear-gradient(180deg,#8b5cf6 0%,#6d28d9 100%);color:#fff;position:relative;overflow:hidden;")
    rep1("box-shadow:0 8px 20px -8px rgba(139,92,246,.75),inset 0 1px 0 rgba(255,255,255,.32);",
         "box-shadow:0 4px 12px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.28),0 0 18px rgba(139,92,246,.3);")

    # s-save — как btn showcase
    rep1("background:linear-gradient(135deg,var(--accent-2),var(--accent));color:#fff;font-size:14px;font-weight:600;cursor:pointer;box-shadow:0 10px 22px -12px rgba(139,92,246,.8);transition:filter .15s,transform .15s}",
         "background:linear-gradient(180deg,#8b5cf6 0%,#6d28d9 100%);color:#fff;font-size:14px;font-weight:600;cursor:pointer;border:1px solid #a78bfa;box-shadow:0 4px 12px rgba(0,0,0,.5),var(--glass-glow),0 0 18px rgba(139,92,246,.3);transition:var(--transition)}")

    # thumb слайдера effort — белый шарик как в showcase
    rep1("background:radial-gradient(circle at 35% 30%,#fff 0%,#f4f4f6 45%,#d8d8dc 100%);box-shadow:0 4px 12px rgba(0,0,0,.7),0 0 0 1px rgba(0,0,0,.25),inset 0 0 0 2px rgba(255,255,255,.08),0 0 20px color-mix(in srgb,var(--c) 75%,transparent);",
         "background:radial-gradient(circle at 35% 30%,#ffffff 0%,#f4f4f6 45%,#d8d8dc 100%);box-shadow:0 4px 12px rgba(0,0,0,.7),0 0 0 1px rgba(0,0,0,.25),inset 0 0 0 2px rgba(255,255,255,.08),0 0 18px color-mix(in srgb,var(--c) 85%,transparent);")

    # ask-btn accept — неон-градиент showcase
    rep1("background:linear-gradient(180deg,#a78bfa,#6d28d9 60%,#5b21b6);",
         "background:linear-gradient(180deg,#8b5cf6 0%,#6d28d9 100%);")

    # логотип — dot-glow стиль
    rep1("background:radial-gradient(circle at 30% 24%,#ddd6fe 0%,#8b5cf6 44%,#5b21b6 100%);",
         "background:radial-gradient(circle at 30% 24%,#ddd6fe 0%,#8b5cf6 44%,#5b21b6 100%);box-shadow:0 22px 46px -16px rgba(139,92,246,.7),inset 0 1px 0 rgba(255,255,255,.38),0 0 24px rgba(139,92,246,.45);")

    # карточки cl-card / ask-card уже glass — добавляем верхнюю световую кромку через ::before только для slider-card-like? пропускаем.

    # hover-переходы nav-ссылок в чате (hicon/newbtn) — мягкий неон
    rep1(".newbtn:hover{filter:brightness(1.05);transform:translateY(-1px);box-shadow:0 16px 30px -14px rgba(139,92,246,.95),inset 0 1px 0 rgba(255,255,255,.24)}",
         ".newbtn:hover{filter:brightness(1.06);transform:translateY(-2px);box-shadow:0 8px 20px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.28),0 0 26px rgba(139,92,246,.5)}")

    # browser-panel — glass-bg showcase
    rep1("background:rgba(17,19,27,.88);box-shadow:var(--shadow-1),inset 0 1px 0 rgba(255,255,255,.035);backdrop-filter:blur(22px);",
         "background:var(--glass-bg);box-shadow:var(--shadow-deep),var(--glass-glow);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);")

    with io.open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{path}: applied ({len(orig)} -> {len(html)} bytes)")

for t in TARGETS:
    apply(t)
