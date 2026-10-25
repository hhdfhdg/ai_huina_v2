"""Выполнение действий модели (инструменты, файлы, правки)."""
from .edit import _edit_error, _make_diff, apply_edit_request, edit_existing, tool_edit_file
import os
import threading

_RUNTIME_LOCK = threading.Lock()
_RUNTIME_SPEED_TPS = 0.0
_RUNTIME_IMAGE_INPUT = False

def set_runtime_capabilities(speed_tps=0.0, image_input_supported=False):
    global _RUNTIME_SPEED_TPS, _RUNTIME_IMAGE_INPUT
    with _RUNTIME_LOCK:
        _RUNTIME_SPEED_TPS = max(0.0, float(speed_tps or 0.0))
        _RUNTIME_IMAGE_INPUT = bool(image_input_supported)

def _runtime_capabilities():
    with _RUNTIME_LOCK:
        return _RUNTIME_SPEED_TPS, _RUNTIME_IMAGE_INPUT
from .file_tools import (
    _safe_path,
    tool_bash,
    tool_list_files,
    tool_move_file,
    tool_read_file,
    tool_send_file,
    tool_write_file,
)


def _short_arg(s, n=200) -> str:
    s = s if isinstance(s, str) else str(s)
    s = s.replace("\n", "\\n")
    return s if len(s) <= n else s[:n] + f"… [{len(s)} симв.]"


def perform_action(kind: str, payload: dict) -> dict:
    payload = payload or {}
    if kind == "write":
        path = str(payload.get("path") or "")
        content = payload.get("content")
        content = content if isinstance(content, str) else ("" if content is None else str(content))
        existed = False
        old = None
        try:
            p = _safe_path(path)
            if p.is_file():
                existed = True
                if p.stat().st_size <= 200_000 and b"\x00" not in p.read_bytes()[:4096]:
                    old = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            existed = False
            old = None
        msg = tool_write_file(path, content)
        ok = msg.startswith("[OK]")
        diff, summary = "", ("новый файл" if not existed else "перезаписан целиком")
        if ok and existed:
            msg += " Файл перезаписан целиком. Для точечных правок используй <edit>."
        if ok and old is not None:
            try:
                new = _safe_path(path).read_text(encoding="utf-8", errors="replace")
                plus, minus, diff = _make_diff(old, new, limit_lines=80)
                summary = f"перезаписан целиком · +{plus} −{minus}"
            except Exception:
                diff = ""
        return {
            "ok": ok, "text": msg, "path": path if ok else None,
            "action": "edited" if existed else "created",
            "summary": summary, "diff": diff if ok else "",
            "show_file": ok,
            "log_name": "write_file",
            "log_args": {"path": path, "content": _short_arg(content, 240)},
        }
    if kind == "edit":
        return apply_edit_request(payload.get("path") or "", body=payload.get("body"), attrs=payload.get("attrs"))
    if kind == "append":
        return edit_existing(payload.get("path") or "", append=payload.get("body") or "")
    if kind == "insert":
        attrs = payload.get("attrs") or {}
        return apply_edit_request(
            payload.get("path") or attrs.get("path") or "",
            body=payload.get("body") or "",
            attrs=attrs,
        )
    name = str(payload.get("name") or "")
    args = payload.get("args") if isinstance(payload.get("args"), dict) else {}
    if payload.get("bad"):
        return _edit_error("", "[ОШИБКА] Не разобрал JSON инструмента: " + str(payload.get("bad")))
    if name in ("edit_file", "str_replace", "replace"):
        return apply_edit_request(
            args.get("path") or "",
            old=args.get("old", args.get("search")),
            new=args.get("new", args.get("replace")),
            content=args.get("content"),
            start=args.get("start"),
            end=args.get("end"),
            append=args.get("append"),
            after=args.get("after"),
            before=args.get("before"),
            lines=args.get("lines"),
        )
    if name == "write_file":
        return perform_action("write", {"path": args.get("path", ""), "content": args.get("content", "")})
    msg = execute_tool(name, args) if name else "[ОШИБКА] Пустой инструмент"
    if not isinstance(msg, str):
        msg = str(msg)
    ok = not (msg.startswith("[ОШИБКА]") or msg.startswith("[ЗАПРЕЩЕНО]"))
    file_ok = msg.startswith("[OK]") and name in ("send_file", "write_file")
    path = args.get("path") if isinstance(args.get("path"), str) else None
    log_args = dict(args)
    description = str(payload.get("description") or "")[:180]
    if isinstance(log_args.get("content"), str):
        log_args["content"] = _short_arg(log_args["content"], 240)
    if isinstance(log_args.get("command"), str) and len(log_args["command"]) > 300:
        log_args["command"] = log_args["command"][:300] + "…"
    return {
        "ok": ok,
        "text": msg,
        "path": path if file_ok else None,
        "action": "created",
        "summary": "",
        "diff": "",
        "show_file": bool(file_ok and path),
        "log_name": name or "tool",
        "log_args": log_args,
        "description": description,
    }


def tool_run_python(path: str, args: str = "", timeout: int = 30) -> str:
    import shlex
    from .file_tools import _wd, _safe_path
    try:
        target = _safe_path(path)
        if not target.is_file() or target.suffix.lower() != ".py":
            return "[ОШИБКА] run_python ожидает существующий .py файл внутри рабочей папки"
        command = [__import__("sys").executable, str(target)] + shlex.split(args or "")
        result = __import__("subprocess").run(command, cwd=str(_wd()), capture_output=True, text=True,
            timeout=max(1, min(int(timeout or 30), 300)), encoding="utf-8", errors="replace")
        return "exit_code: " + str(result.returncode) + "\nstdout:\n" + result.stdout[:6000] + "\nstderr:\n" + result.stderr[:3000]
    except Exception as e:
        return "[ОШИБКА] run_python: " + str(e)


def tool_python_exec(code: str, timeout: int = 30) -> str:
    """Выполнить короткий Python-фрагмент в рабочей папке с тайм-аутом."""
    import os
    import subprocess
    import sys
    from .file_tools import _wd
    if not isinstance(code, str) or not code.strip():
        return "[ОШИБКА] Не передан Python-код"
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(_wd()), capture_output=True, text=True,
            timeout=max(1, min(int(timeout or 30), 60)),
            encoding="utf-8", errors="replace", env=os.environ.copy(),
        )
        return "exit_code: " + str(result.returncode) + "\nstdout:\n" + result.stdout[:6000] + "\nstderr:\n" + result.stderr[:3000]
    except subprocess.TimeoutExpired:
        return "[ОШИБКА] Python-код превысил тайм-аут " + str(timeout) + " сек"
    except Exception as e:
        return "[ОШИБКА] python_exec: " + str(e)


def tool_search_files(query: str, subdir: str = "", limit: int = 30) -> str:
    """Найти текстовый запрос внутри файлов рабочей папки."""
    from .file_tools import _safe_path, _wd
    query = str(query or "").strip()
    if not query:
        return "[ОШИБКА] Укажи непустой query"
    try:
        root = _safe_path(subdir) if subdir else _wd().resolve()
        if root.is_file():
            files = [root]
        else:
            files = [f for f in root.rglob("*") if f.is_file() and not any(part.startswith(".") or part == "__pycache__" for part in f.relative_to(_wd().resolve()).parts)]
        found = []
        qlow = query.casefold()
        for f in files:
            try:
                if f.stat().st_size > 1_000_000 or f.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".exe", ".dll", ".so", ".mp4", ".mp3"}:
                    continue
                content = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for n, line in enumerate(content.splitlines(), 1):
                if qlow in line.casefold():
                    try:
                        rel = f.relative_to(_wd().resolve()).as_posix()
                    except Exception:
                        rel = f.name
                    found.append(rel + ":" + str(n) + ": " + line.strip()[:240])
                    if len(found) >= max(1, min(int(limit or 30), 100)):
                        return "\n".join(found)
        return "\n".join(found) if found else "Совпадений не найдено."
    except Exception as e:
        return "[ОШИБКА] search_files: " + str(e)


def tool_render_video(html_path: str, script_path: str, output_path: str = "video.mp4", timeout: int = 180) -> str:
    """Запустить созданный рендер-скрипт и проверить результат."""
    import os
    import subprocess
    import sys
    from .file_tools import _safe_path, _wd
    try:
        html_file = _safe_path(html_path)
        script_file = _safe_path(script_path)
        output_file = _safe_path(output_path)
        if not html_file.is_file() or html_file.suffix.lower() not in (".html", ".htm"):
            return "[ОШИБКА] html_path должен указывать на существующий HTML-файл"
        if not script_file.is_file() or script_file.suffix.lower() != ".py":
            return "[ОШИБКА] script_path должен указывать на существующий Python-скрипт"
        result = subprocess.run(
            [sys.executable, str(script_file), "--html", str(html_file), "--output", str(output_file)],
            cwd=str(_wd()), capture_output=True, text=True,
            timeout=max(1, min(int(timeout or 180), 300)), encoding="utf-8", errors="replace",
        )
        details = "exit_code: " + str(result.returncode) + "\nstdout:\n" + result.stdout[-5000:] + "\nstderr:\n" + result.stderr[-3000:]
        if result.returncode != 0:
            return "[ОШИБКА] Рендерер завершился с ошибкой.\n" + details
        if not output_file.is_file() or output_file.stat().st_size <= 0:
            return "[ОШИБКА] Скрипт завершился, но выходное видео не создано или пустое.\n" + details
        return "[OK] Видео создано: " + output_file.relative_to(_wd().resolve()).as_posix() + " (" + str(output_file.stat().st_size) + " байт)\n" + details
    except subprocess.TimeoutExpired:
        return "[ОШИБКА] Рендер видео превысил тайм-аут " + str(timeout) + " сек"
    except Exception as e:
        return "[ОШИБКА] render_video: " + str(e)


def tool_delegate_task(task: str, context: str = "", timeout: int = 120) -> str:
    """Run a bounded independent subtask through a separate model call, gated by measured speed."""
    speed, _ = _runtime_capabilities()
    if speed <= 35:
        return "[ЗАПРЕЩЕНО] Делегирование отключено: измеренная скорость генерации должна быть выше 35 токенов/с. Текущая оценка: " + str(round(speed, 1))
    task = str(task or "").strip()
    if not task:
        return "[ОШИБКА] Для delegate_task нужно описать независимую подзадачу"
    try:
        from .llm import stream_model
        from . import config
        messages = [
            {"role": "system", "content": "Ты вспомогательный субагент ChatAihuina. Выполни только указанную независимую подзадачу. Не вызывай инструменты, не утверждай, что изменял файлы, если этого не делал. Верни краткий результат, предположения и риски."},
            {"role": "user", "content": "Подзадача:\n" + task + "\n\nКонтекст:\n" + str(context or "")[:12000]},
        ]
        parts = []
        started = __import__("time").monotonic()
        for piece in stream_model(messages, temperature=0.2, model_name=config.MODEL_NAME):
            parts.append(str(piece))
            if __import__("time").monotonic() - started > max(5, min(int(timeout or 120), 180)):
                break
        result = "".join(parts).strip()
        return ("[SUBAGENT RESULT]\n" + result[:10000]) if result else "[ОШИБКА] Субагент не вернул текстовый результат"
    except Exception as e:
        return "[ОШИБКА] delegate_task: " + str(e)


def tool_browser(action: str, url: str = "", selector: str = "", text: str = "", timeout: int = 30,
                 tokens_per_second: float = 0, image_input_supported: bool = False, steps=None) -> str:
    """Открыть страницу и выполнить одно действие либо последовательность действий."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return "[ОШИБКА] Для browser требуется установить playwright и браузер Chromium."

    from .file_tools import _safe_path, _wd
    import time
    try:
        sequence = steps if isinstance(steps, list) and steps else [{"action": action, "url": url, "selector": selector, "text": text}]
        if len(sequence) > 20:
            return "[ОШИБКА] В одном browser-вызове разрешено не более 20 шагов"
        screenshot_path = ""
        results = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1365, "height": 768}, device_scale_factor=1)
            page.set_default_timeout(max(1000, min(int(timeout or 30), 60) * 1000))
            for i, step in enumerate(sequence, 1):
                if not isinstance(step, dict):
                    results.append("Шаг " + str(i) + ": пропущен — ожидался объект")
                    continue
                act = str(step.get("action") or (action if len(sequence) == 1 else "text")).lower()
                step_url = str(step.get("url") or (url if i == 1 else ""))
                sel = str(step.get("selector") or (selector if i == 1 else ""))
                val = str(step.get("text") or (text if i == 1 else ""))
                if act in ("open", "text", "screenshot") and step_url:
                    if not step_url.startswith(("http://", "https://")):
                        results.append("Шаг " + str(i) + ": [ОШИБКА] разрешены только URL http:// и https://")
                        continue
                    page.goto(step_url, wait_until="domcontentloaded")
                elif step_url and step_url.startswith(("http://", "https://")) and page.url == "about:blank":
                    page.goto(step_url, wait_until="domcontentloaded")
                if act == "open":
                    results.append("Шаг " + str(i) + ": Открыто " + page.url + " · " + (page.title() or "") + "\n" + page.locator("body").inner_text()[:3500])
                elif act == "click":
                    if not sel:
                        results.append("Шаг " + str(i) + ": [ОШИБКА] для click нужен selector")
                    else:
                        page.locator(sel).first.click()
                        results.append("Шаг " + str(i) + ": клик выполнен · URL " + page.url + "\n" + page.locator("body").inner_text()[:2200])
                elif act == "fill":
                    if not sel:
                        results.append("Шаг " + str(i) + ": [ОШИБКА] для fill нужен selector")
                    else:
                        page.locator(sel).first.fill(val)
                        results.append("Шаг " + str(i) + ": поле заполнено; форма не отправлялась автоматически")
                elif act == "check":
                    if not sel:
                        results.append("Шаг " + str(i) + ": [ОШИБКА] для check нужен selector")
                    else:
                        page.locator(sel).first.check()
                        results.append("Шаг " + str(i) + ": checkbox/radio отмечен")
                elif act == "select":
                    if not sel:
                        results.append("Шаг " + str(i) + ": [ОШИБКА] для select нужен selector")
                    else:
                        page.locator(sel).first.select_option(val)
                        results.append("Шаг " + str(i) + ": выбран option " + val[:120])
                elif act == "text":
                    results.append("Шаг " + str(i) + ": " + page.locator(sel or "body").inner_text()[:5000])
                elif act == "screenshot":
                    speed, image_supported = _runtime_capabilities()
                    if speed <= 50 or not image_supported:
                        results.append("Шаг " + str(i) + ": [ЗАПРЕЩЕНО] Скриншоты для анализа отключены: нужна подтверждённая скорость >50 токенов/с и поддержка входных изображений.")
                    else:
                        screenshot_path = "browser_screenshot_" + str(int(time.time() * 1000)) + ".png"
                        target = _safe_path(screenshot_path)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(target), full_page=False, animations="disabled")
                        results.append("Шаг " + str(i) + ": [IMAGE_INPUT_FILE: " + screenshot_path + "] Скриншот сохранён для визуального анализа.")
                elif act == "wait":
                    page.wait_for_timeout(max(100, min(int(step.get("ms") or 500), 5000)))
                    results.append("Шаг " + str(i) + ": ожидание завершено")
                else:
                    results.append("Шаг " + str(i) + ": [ОШИБКА] неизвестное действие " + act)
            browser.close()
        return "\n\n".join(results)[:10000]
    except Exception as e:
        return "[ОШИБКА] browser: " + str(e)


TOOL_IMPL = {
    "bash":       tool_bash,
    "read_file":  tool_read_file,
    "write_file": tool_write_file,
    "edit_file":  tool_edit_file,
    "list_files": tool_list_files,
    "move_file":  tool_move_file,
    "send_file":  tool_send_file,
    "run_python": tool_run_python,
    "python_exec": tool_python_exec,
    "search_files": tool_search_files,
    "render_video": tool_render_video,
    "delegate_task": tool_delegate_task,
    "browser": tool_browser,
}


def execute_tool(name: str, args: dict) -> str:
    if name not in TOOL_IMPL:
        return f"[ОШИБКА] Неизвестный инструмент: {name}"
    if not isinstance(args, dict):
        args = {}
    try:
        return TOOL_IMPL[name](**args)
    except TypeError as e:
        return f"[ОШИБКА] Неверные аргументы для {name}: {e}"
    except Exception as e:
        return f"[ОШИБКА] {name}: {e}"
