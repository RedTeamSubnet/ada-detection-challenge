function detect_webdriver() {
	console.log(navigator.userAgent);
	return false;
}

if (typeof window !== 'undefined') window.detect_webdriver = detect_webdriver;
