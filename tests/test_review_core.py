import picasso_review as R


def rules(findings):
    return {f.rule for f in findings}


def test_review_content_flags_undefined_token():
    out = R.review_content("x.html", '<div style="color:var(--nope)"></div>', {})
    assert "undefined-token" in rules(out)


def test_review_content_flags_external_dep():
    out = R.review_content("x.html", '<script src="https://cdn.example.com/a.js"></script>', {})
    assert "external-dep" in rules(out)


def test_review_content_combines_slop_and_structural():
    css = ".h{background:linear-gradient(0deg,indigo,purple);color:#000000;}"
    out = R.review_content("hero.css", css, {})
    got = rules(out)
    assert "purple-gradient" in got and "pure-black" in got


def test_review_content_ignores_unknown_kind():
    assert R.review_content("data.json", '{"a":"b"}', {}) == []


def test_review_content_copy_skips_structural_checks():
    # .md is copy: no external-dep / undefined-token, only copy slop rules
    out = R.review_content("notes.md", "var(--nope) and https://x.com", {})
    assert "undefined-token" not in rules(out)
    assert "external-dep" not in rules(out)


def test_review_paths_walks_dir_and_uses_tokens(tmp_path):
    (tmp_path / "tokens.css").write_text(":root{--color-accent:#2563eb;}")
    (tmp_path / "ok.html").write_text('<div style="color:var(--color-accent)">hi</div>')
    (tmp_path / "bad.html").write_text('<div style="color:var(--missing)">hi</div>')
    results = R.review_paths([str(tmp_path)], str(tmp_path / "tokens.css"))
    flagged = {path for path, f in results if f.rule == "undefined-token"}
    assert any(p.endswith("bad.html") for p in flagged)
    assert not any(p.endswith("ok.html") for p in flagged)


def test_format_report_clean():
    assert "no slop" in R.format_report([]).lower()


def test_format_report_groups_by_file():
    from picasso_engine.slop_lint import Finding
    results = [("a.css", Finding("pure-black", "warn", "m", 1, "s"))]
    text = R.format_report(results)
    assert "a.css" in text and "pure-black" in text


def test_review_paths_flags_missing_path():
    results = R.review_paths(["/nope/does-not-exist.html"], None)
    assert any(f.rule == "missing-path" for _p, f in results)


def test_review_paths_dedupes_file_and_its_dir(tmp_path):
    (tmp_path / "tokens.css").write_text(":root{--a:#111;}")
    bad = tmp_path / "bad.html"
    bad.write_text('<div style="color:var(--missing)">x</div>')
    results = R.review_paths([str(tmp_path), str(bad)], str(tmp_path / "tokens.css"))
    undef = [(_p, f) for _p, f in results if f.rule == "undefined-token" and _p.endswith("bad.html")]
    assert len(undef) == 1


def _contrast_criterion():
    from picasso_engine.rules import load_rules
    criteria, _errors = load_rules()
    return next(c for c in criteria if c.identifier == "contrast")


def _contrast_findings(tokens):
    from picasso_engine.slop_lint import findings_for
    return findings_for(_contrast_criterion(), "", "css", tokens)


def test_contrast_findings_flags_low_pair():
    tokens = {"color-text": "#aaaaaa", "color-bg": "#ffffff"}
    rules = {f.rule for f in _contrast_findings(tokens)}
    assert "contrast" in rules


def test_contrast_findings_passes_good_pair():
    tokens = {"color-text": "#18181b", "color-bg": "#ffffff",
              "color-accent": "#2563eb", "color-accent-contrast": "#ffffff"}
    assert _contrast_findings(tokens) == []


def test_contrast_findings_skips_unparsable_or_missing():
    assert _contrast_findings({"color-text": "var(--x)", "color-bg": "#fff"}) == []
    assert _contrast_findings({}) == []


def test_review_paths_contrast_fires_once_per_directory(tmp_path):
    (tmp_path / "tokens.css").write_text(
        ":root{--color-text:#777777;--color-bg:#ffffff;}")
    for i in range(3):
        (tmp_path / f"f{i}.html").write_text(f"<div>{i}</div>")
    results = R.review_paths([str(tmp_path)], str(tmp_path / "tokens.css"))
    contrast = [f for _p, f in results if f.rule == "contrast"]
    assert len(contrast) == 1


def test_contrast_min_ratio_can_tighten_the_default():
    from picasso_engine.schemes import run_check
    check = {
        "scheme": "token-pair", "minRatio": 7,
        "pairs": [["color-text", "color-bg"]],
    }
    tokens = {"color-text": "#767676", "color-bg": "#ffffff"}
    assert run_check(check, "", "css", tokens)


def test_rule_set_findings_attributes_project_error_to_project_file(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text("{ broken", encoding="utf-8")
    from picasso_engine.rules import load_rules
    _criteria, errors = load_rules(str(path))
    findings = R._rule_set_findings(errors, str(path))
    assert len(findings) == 1
    attributed_path, finding = findings[0]
    assert attributed_path == str(path)
    assert "falling back to the shipped rules" in finding.message.lower()


def test_rule_set_findings_collapses_multiple_core_errors_to_one_finding():
    errors = ["core.json: rule 0: missing required field 'title'",
              "core.json: rule 1: missing required field 'title'",
              "core.json: rule 2: missing required field 'title'"]
    from picasso_engine.rules import CORE_PATH
    findings = R._rule_set_findings(errors, None)
    assert len(findings) == 1
    attributed_path, finding = findings[0]
    assert attributed_path == CORE_PATH
    assert "3 error" in finding.message
    assert "shipped rules were not applied" in finding.message
