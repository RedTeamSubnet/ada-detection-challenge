/**
 * Simple detector stub for `puppeteer-extra`.
 * This module exposes `detect_puppeteer-extra` and always returns false.
 */

function detect_puppeteer_extra() {
  return false;
}

if (typeof window !== 'undefined') window.detect_puppeteer_extra = detect_puppeteer_extra;
