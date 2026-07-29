/**
 * Detector stub for the `GoLogin` anti-detect browser.
 *
 * This module exposes `detect_gologin` and currently always returns false.
 * Replace the body with real detection logic: `GoLogin` is a commercial
 * anti-detect browser driven over its local application API, so look for
 * artifacts it leaves in the page environment rather than for a WebDriver or
 * CDP automation flag.
 *
 * Browser fingerprinting is prohibited by the challenge rules.
 */

function detect_gologin() {
  return false;
}

if (typeof window !== 'undefined') window.detect_gologin = detect_gologin;
