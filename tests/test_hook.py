import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "scripts" / "slop_lint_hook.py"

def _payload(path, content):
    return {
        "tool_name": "Write",
        "tool_input": {"file_path": path, "content": content},
    }

def test_run_returns_warning_for_sloppy_css():
    import importlib.util
    spec = importlib.util.spec_from_file_location("slop_lint_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = mod.run(_payload("hero.css", ".h{background:linear-gradient(0deg,indigo,purple);}"))
    assert "purple-gradient" in out

def test_run_silent_for_clean_html():
    import importlib.util
    spec = importlib.util.spec_from_file_location("slop_lint_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = mod.run(_payload("index.html", "<section><h1>Hello</h1></section>"))
    assert out == ""

def test_hook_process_exits_zero_even_with_warnings():
    payload = _payload("hero.css", ".h{color:#000000;}")
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload), text=True, capture_output=True,
    )
    assert proc.returncode == 0  # warn-only never blocks
    assert "pure-black" in (proc.stderr + proc.stdout)

def test_hook_ignores_non_design_files():
    payload = _payload("data.json", '{"a": "b — c"}')
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload), text=True, capture_output=True,
    )
    assert proc.returncode == 0
    assert proc.stderr.strip() == ""

def test_hook_exits_zero_on_binary_file_without_content(tmp_path):
    f = tmp_path / "x.css"
    f.write_bytes(b"\xff\xfe\x00\x01 not utf8")
    payload = {"tool_name": "Edit", "tool_input": {"file_path": str(f)}}
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload), text=True, capture_output=True,
    )
    assert proc.returncode == 0

def test_hook_reads_file_when_content_absent(tmp_path):
    f = tmp_path / "hero.css"
    f.write_text(".h{color:#000000;}")
    payload = {"tool_name": "Edit", "tool_input": {"file_path": str(f)}}
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload), text=True, capture_output=True,
    )
    assert proc.returncode == 0
    assert "pure-black" in (proc.stdout + proc.stderr)

def test_run_returns_empty_for_non_string_content():
    import importlib.util
    spec = importlib.util.spec_from_file_location("slop_lint_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = mod.run({"tool_input": {"file_path": "x.css", "content": 123}})
    assert out == ""

def test_hook_applies_a_project_rule(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("slop_lint_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    (tmp_path / "rules.json").write_text(json.dumps({
        "picassoRulesVersion": "1",
        "rules": [{
            "identifier": "no-lorem",
            "title": "No lorem ipsum",
            "statement": "Copy must not contain placeholder latin.",
            "level": "must-not",
            "category": "content",
            "verification": "automated",
            "message": "Placeholder latin in shipped copy.",
            "check": {"scheme": "regex", "kinds": ["html"], "pattern": "lorem ipsum"},
            "examples": [
                {"outcome": "fail", "kind": "html", "content": "<p>lorem ipsum</p>"},
                {"outcome": "pass", "kind": "html", "content": "<p>real copy</p>"},
            ],
        }],
    }), encoding="utf-8")
    page = tmp_path / "index.html"
    message = mod.run(_payload(str(page), "<p>lorem ipsum dolor</p>"))
    assert "no-lorem" in message

def test_hook_honours_a_project_disable(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("slop_lint_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    (tmp_path / "rules.json").write_text(json.dumps({
        "picassoRulesVersion": "1",
        "rules": [{"identifier": "em-dash", "disabled": True}],
    }), encoding="utf-8")
    page = tmp_path / "index.html"
    message = mod.run(_payload(str(page), "<p>Build faster — ship smarter.</p>"))
    assert "em-dash" not in message

def test_hook_is_silent_on_a_broken_project_rules_file(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("slop_lint_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    (tmp_path / "rules.json").write_text("{ broken", encoding="utf-8")
    page = tmp_path / "index.html"
    message = mod.run(_payload(str(page), "<p>clean copy here</p>"))
    assert "Traceback" not in message

def test_hook_still_applies_core_rules_with_no_project_file(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("slop_lint_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    page = tmp_path / "index.html"
    message = mod.run(_payload(str(page), "<p>Build faster — ship smarter.</p>"))
    assert "em-dash" in message

def test_hook_reports_the_offending_url_via_snippet():
    import importlib.util
    spec = importlib.util.spec_from_file_location("slop_lint_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    html = '<img src="https://cdn.example.com/a.png" alt="a">'
    message = mod.run(_payload("index.html", html))
    assert "https://cdn.example.com/a.png" in message

def test_hook_warns_once_when_shipped_rules_are_broken(tmp_path, monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location("slop_lint_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    broken_core = tmp_path / "core.json"
    broken_core.write_text("{ broken", encoding="utf-8")
    import picasso_engine.rules as rules_mod
    monkeypatch.setattr(rules_mod, "CORE_PATH", str(broken_core))
    page = tmp_path / "index.html"
    message = mod.run(_payload(str(page), "<p>clean copy here</p>"))
    assert "shipped rules not applied" in message
