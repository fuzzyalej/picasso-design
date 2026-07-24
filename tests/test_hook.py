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
