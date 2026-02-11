function detect_webdriver() {
	return false;
}

if (typeof window !== 'undefined') window.detect_webdriver = detect_webdriver;
