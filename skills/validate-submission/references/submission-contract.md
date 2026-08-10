# Submission Contract

Required files and browser globals:

| File | Global function | Target |
| --- | --- | --- |
| `ads_power.js` | `window.detect_ads_power` | AdsPower |
| `dolphin_anty.js` | `window.detect_dolphin_anty` | Dolphin Anty |
| `gologin.js` | `window.detect_gologin` | GoLogin |
| `headless.js` | `window.detect_headless_non_ua` | headless browser (any vendor) |
| `multilogin.js` | `window.detect_multilogin` | Multilogin |
| `octo.js` | `window.detect_octo` | Octo Browser |

Every file must:

- be JavaScript and use its exact filename;
- contain no more than 500 lines;
- define and expose the expected function;
- return or resolve to a value interpreted as a boolean by the challenge page;
- pass `examples/miner_commit/eslint.config.mjs`.
