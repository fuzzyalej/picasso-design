import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "picasso_review.py"

def test_cli_reports_clean_dir(tmp_path):
    (tmp_path / "tokens.css").write_text(":root{--color-accent:#2563eb;}")
    (tmp_path / "ok.html").write_text('<div style="color:var(--color-accent)">hi</div>')
    proc = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)],
                          text=True, capture_output=True)
    assert proc.returncode == 0
    assert "no slop tells" in proc.stdout.lower()

def test_cli_reports_findings_and_still_exits_zero(tmp_path):
    (tmp_path / "hero.css").write_text(".h{color:#000000;}")
    proc = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)],
                          text=True, capture_output=True)
    assert proc.returncode == 0
    assert "pure-black" in proc.stdout

def test_cli_explicit_tokens_flag(tmp_path):
    (tmp_path / "t.css").write_text(":root{--color-accent:#2563eb;}")
    (tmp_path / "p.html").write_text('<div style="color:var(--missing)">x</div>')
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "p.html"), "--tokens", str(tmp_path / "t.css")],
        text=True, capture_output=True)
    assert proc.returncode == 0
    assert "undefined-token" in proc.stdout
