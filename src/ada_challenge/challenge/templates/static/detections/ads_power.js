/**
 * Detector stub for the `AdsPower` anti-detect browser.
 *
 * This module exposes `detect_ads_power` and currently always returns false.
 * Replace the body with real detection logic: `AdsPower` is a commercial
 * anti-detect browser driven over its local application API, so look for
 * artifacts it leaves in the page environment rather than for a WebDriver or
 * CDP automation flag.
 *
 * Browser fingerprinting is prohibited by the challenge rules.
 */

function detect_ads_power() {
  return false;
}

if (typeof window !== 'undefined') window.detect_ads_power = detect_ads_power;
