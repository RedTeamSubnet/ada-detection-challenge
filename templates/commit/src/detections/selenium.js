/**
 * Simple detector stub for `selenimu`.
 * This module exposes `detect_selenium` and always returns false.
 */

function detect_selenium() {
  return false;
}

if (typeof window !== 'undefined') window.detect_selenium = detect_selenium;
