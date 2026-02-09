function detect_websocket() {
	console.log(navigator.userAgent);
	return false;
}

if (typeof window !== 'undefined') window.detect_websocket = detect_websocket;
