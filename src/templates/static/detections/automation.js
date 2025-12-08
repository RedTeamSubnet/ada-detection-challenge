/**
 * Simple detector stub for `automation`.
 * This module exposes `detect_automation` and always returns false.
 */

function detect_automation() {
	console.log(navigator.userAgent);
	return false;
}

if (typeof window !== 'undefined') window.detect_automation = detect_automation;
