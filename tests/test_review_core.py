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


def test_contrast_findings_flags_low_pair():
    from picasso_review import contrast_findings
    tokens = {"color-text": "#aaaaaa", "color-bg": "#ffffff"}
    rules = {f.rule for f in contrast_findings(tokens)}
    assert "contrast" in rules


def test_contrast_findings_passes_good_pair():
    from picasso_review import contrast_findings
    tokens = {"color-text": "#18181b", "color-bg": "#ffffff",
              "color-accent": "#2563eb", "color-accent-contrast": "#ffffff"}
    assert contrast_findings(tokens) == []


def test_contrast_findings_skips_unparsable_or_missing():
    from picasso_review import contrast_findings
    assert contrast_findings({"color-text": "var(--x)", "color-bg": "#fff"}) == []
    assert contrast_findings({}) == []
