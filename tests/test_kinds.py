from picasso_engine.kinds import kind_for


def test_maps_known_extensions():
    assert kind_for("a/b/x.html") == "html"
    assert kind_for("X.HTM") == "html"
    assert kind_for("styles.css") == "css"
    assert kind_for("notes.md") == "copy"


def test_unknown_extension_is_none():
    assert kind_for("data.json") is None
    assert kind_for("noext") is None
