from pathlib import Path

from api.endpoints.challenge import service
from api.endpoints.challenge.schemas import (
    PayloadPM,
    SubmissionPayloadsPM,
    _frameworks_names,
)

_ROOT = Path(__file__).resolve().parent.parent
_TEMPLATE_DIR = _ROOT / "src" / "ada_challenge" / "challenge" / "templates"


def _bundle_path() -> Path:
    """The React bundle name carries a content hash, so resolve it by glob."""
    bundles = sorted((_TEMPLATE_DIR / "static" / "js").glob("main.*.js"))
    bundles = [path for path in bundles if not path.name.endswith(".LICENSE.txt")]
    assert bundles, "no main.*.js bundle found"
    return bundles[0]


def test_headless_detector_is_loaded_before_browser_detectors():
    index_html = (_TEMPLATE_DIR / "index.html").read_text()

    headless_idx = index_html.index("static/detections/headless.js")
    browser_idx = index_html.index("static/detections/ads_power.js")

    assert headless_idx < browser_idx


def test_every_configured_browser_has_a_detector_script_tag():
    index_html = (_TEMPLATE_DIR / "index.html").read_text()

    for browser_name in _frameworks_names:
        assert f"static/detections/{browser_name}.js" in index_html


def test_bundle_reads_the_browser_roster_from_the_page_global():
    bundle = _bundle_path().read_text()

    assert "ADA_FRAMEWORK_NAMES" in bundle
    assert "ADA_RESULT_ENDPOINT" in bundle


def test_bundle_calls_headless_detector_before_browser_detectors():
    """The bundle awaits detect_headless_non_ua, then dispatches detect_<name>.

    Both calls live in the same minified async function, so their textual order
    there does reflect execution order.
    """
    bundle = _bundle_path().read_text()

    headless_idx = bundle.index("window.detect_headless_non_ua")
    dispatch_idx = bundle.index('"detect_".concat')

    assert headless_idx < dispatch_idx


def test_headless_detector_does_not_use_user_agent():
    detector = (_TEMPLATE_DIR / "static" / "detections" / "headless.js").read_text()
    executable_source = "\n".join(
        line for line in detector.splitlines() if not line.strip().startswith("*")
    )

    assert "navigator.userAgent" not in executable_source
    assert "navigator.userAgentData" not in executable_source


def _make_payload(headless: bool) -> SubmissionPayloadsPM:
    return SubmissionPayloadsPM(
        results=[
            PayloadPM(detected=False, raw=False, framework_name=name)
            for name in _frameworks_names
        ],
        headless=headless,
        order_number=0,
    )


def test_submission_payload_accepts_headless_field():
    payload = _make_payload(headless=True)

    assert payload.headless is True
    assert payload.model_dump()["headless"] is True


def test_submit_payload_preserves_headless_in_payload_manager(monkeypatch):
    captured = {}

    class _Manager:
        def submit_task(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(service, "payload_manager", _Manager())

    service.submit_payload(_make_payload(headless=True))

    assert captured["headless"] is True
