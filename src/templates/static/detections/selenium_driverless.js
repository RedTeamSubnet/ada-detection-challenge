/**
 * Simple detector stub for `selenium_driverless`.
 * This module exposes `detect_selenium_driverless` and always returns false.
 */

function detect_selenium_driverless() {
  return false;
}

if (typeof window !== 'undefined') window.detect_selenium_driverless = detect_selenium_driverless	;
