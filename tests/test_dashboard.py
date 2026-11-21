"""Basic functional checks for the complete bilingual Streamlit dashboard.

Tests run against the verified, synthetic data files in this repository.
"""
from streamlit.testing.v1 import AppTest

APP = "app_full_bilingue.py"
MODULES = ("summary", "commercial", "inventory", "scenario")

def assert_clean(at, context):
    errors = [str(x.message) for x in at.exception]
    if errors:
        raise AssertionError(f"{context}: {errors}")

def run():
    at = AppTest.from_file(APP, default_timeout=90).run()
    assert_clean(at, "Initial dashboard")
    titles = [x.value for x in at.title]
    assert "Control de rentabilidad mayorista" in titles, titles
    print("PASS: Spanish dashboard loads")

    def get_module():
        found = [x for x in at.radio if x.label in ("Módulo", "Module")]
        assert len(found) == 1, [(x.label, x.value) for x in at.radio]
        return found[0]

    for module in MODULES:
        get_module().set_value(module).run()
        assert_clean(at, f"Module {module}")
        print(f"PASS: module {module}")

    languages = [x for x in at.sidebar.radio if x.label == "Idioma / Language"]
    assert len(languages) == 1
    languages[0].set_value("English").run()
    assert_clean(at, "English mode")
    assert "Wholesale Management Cockpit" in [x.value for x in at.title]
    print("PASS: English dashboard loads")

if __name__ == "__main__":
    run()
