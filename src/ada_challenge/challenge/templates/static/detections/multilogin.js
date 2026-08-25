/**
 * Detector stub for the `Multilogin` anti-detect browser.
 *
 * This module exposes `detect_multilogin` and currently always returns false.
 * Replace the body with real detection logic: `Multilogin` is a commercial
 * anti-detect browser driven over its local application API, so look for
 * artifacts it leaves in the page environment rather than for a WebDriver or
 * CDP automation flag.
 *
 * Browser fingerprinting is prohibited by the challenge rules.
 */

function detect_multilogin() {
  return false;
}

if (typeof window !== 'undefined') window.detect_multilogin = detect_multilogin;
