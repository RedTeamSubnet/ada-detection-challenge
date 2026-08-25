# Research Policy

## Source Priority

1. Peer-reviewed papers, preprints from identified researchers, standards, and browser
   vendor documentation.
2. Official release notes and documentation for Chromium and the scheduled anti-detect
   browser products: AdsPower, Dolphin Anty, GoLogin, Multilogin, and Octo Browser.
3. Technical research from established bot-detection providers such as DataDome,
   Fingerprint, Cloudflare, Akamai, HUMAN, and Kasada.
4. Reputable independent technical analysis with reproducible evidence.

Do not treat marketing pages, anonymous posts, or undated summaries as authoritative.
Record the date accessed when a page has no publication date.

## Challenge Compliance

The challenge permits analysis of artifacts the scheduled product leaves in the page
environment. It does not permit browser fingerprinting. Research may describe fingerprinting
for awareness, but the resulting submission must not collect or combine stable device/browser
identity attributes. Do not treat generic WebDriver or CDP presence as target evidence.

Treat these as prohibited unless challenge maintainers clarify otherwise:

- persistent or cross-session identity construction;
- canvas, audio, font, WebGL, hardware, or device-property fingerprint aggregation;
- third-party fingerprinting SDKs or remote identity services;
- exfiltration of browser attributes for off-page classification.

Prefer transient, page-local evidence tied directly to a target product's injected code,
patched APIs, execution behavior, serialization, stack traces, or product-specific globals.
Evaluate every signal against a normal human-driven browser.

## Reporting Standard

- Distinguish observed facts from inference.
- Include contrary evidence and known evasions.
- Avoid long quotations; summarize and link.
- Never claim a technique is current without checking its date and present browser behavior.
- Never recommend a signal solely because a commercial provider says it works.
