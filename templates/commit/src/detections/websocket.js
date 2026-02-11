function detect_websocket() {
	return false;
}

if (typeof window !== 'undefined') window.detect_websocket = detect_websocket;
