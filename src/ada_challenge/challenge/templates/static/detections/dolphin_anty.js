/**
 * Detector stub for the `Dolphin Anty` anti-detect browser.
 *
 * This module exposes `detect_dolphin_anty` and currently always returns false.
 * Replace the body with real detection logic: `Dolphin Anty` is a commercial
 * anti-detect browser driven over its local application API, so look for
 * artifacts it leaves in the page environment rather than for a WebDriver or
 * CDP automation flag.
 *
 * Browser fingerprinting is prohibited by the challenge rules.
 */

function detect_dolphin_anty() {
  return false;
}

if (typeof window !== 'undefined') window.detect_dolphin_anty = detect_dolphin_anty;
