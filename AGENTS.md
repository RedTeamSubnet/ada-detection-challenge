# ADA-3 Agent Guide

## Objective

Develop six browser-side JavaScript detectors that identify the expected anti-detect browser
without firing on human-driven browsers. Work only from evidence that is permitted by the
challenge; browser fingerprinting is prohibited.

Unlike ABS, the targets here are not Python automation frameworks. Each target is a
commercial anti-detect browser — a paid desktop application that launches a managed profile
and is driven over its own loopback API. Detection must therefore key on artifacts the
product itself leaves in the page environment, not on a WebDriver or CDP automation flag.

## Required Workflow

1. Use `research-bot-detection` for current papers, official product changes, and provider
   research. Mark fingerprinting findings as prohibited.
2. Edit the files in
   `src/ada_challenge/challenge/templates/static/detections`.
3. Use `validate-submission` before every score attempt.
4. Follow `docs/Testing_manuals.md` to start the challenge, call `/score`, and complete any
   requested human verification. The local score helper is not usable in miner workflows.
5. Review the score and available challenge output, then diagnose missed browsers,
   collisions, human failures, and headless failures; iterate.
6. Use `build-submission` only after the human states the achieved score and confirms it is
   satisfactory.

## Submission Files

The submission contains exactly:

- `ads_power.js` — AdsPower
- `dolphin_anty.js` — Dolphin Anty
- `gologin.js` — GoLogin
- `headless.js` — headless browser, any vendor
- `multilogin.js` — Multilogin
- `octo.js` — Octo Browser

Keep the existing function and `window` export names. Each file must be at most 500 lines and
must pass `examples/miner_commit/eslint.config.mjs`.

NSTBrowser is a sixth anti-detect browser that is deliberately **not** in this list yet. Its
prior integration is preserved under `docs/reference/nstbrowser/`. Do not add `nstbrowser.js`
to the contract until a bot-runner driver and preset exist — miners must never be asked for a
detector against a target that is never scheduled.

## Scoring Model

Human and headless detection are **pass/fail gates**. Getting them right earns no
points; getting either wrong zeroes the whole submission. Anti-detect browser
detection is the only scored component.

- Browser detection is 100% of the local score, weighted per browser.
- Collisions receive reduced credit (0.1 instead of 1.0 for that run).
- **Human gate:** any browser or headless detection during a human task makes the
  final score zero.
- **Headless gate:** a single wrong headless verdict on any driver run makes the
  final score zero. There is no allowance.
- Missing a browser costs that browser's share of the score, but does not trip the
  headless gate on its own.
- The protected endpoints use `X-API-Key` with `ADA_CHALLENGE_API_KEY`.

## Naming Note

The API, config, and payload schema still use `framework` as the generic term for "the target
under test" (`framework_images`, `framework_name`, `ADA_FRAMEWORK_NAMES`). In ADA-3 those
slots hold anti-detect browser names. The term is retained because it is baked into the
prebuilt React bundle shipped in `templates/static/js`, whose source lives outside this repo.

## Important Paths

- Detection source:
  `src/ada_challenge/challenge/templates/static/detections`
- Target/browser roster:
  `src/ada_challenge/challenge/api/configs/challenge.yml`
- API schema and endpoints:
  `src/ada_challenge/challenge/api/endpoints/challenge`
- Scoring implementation:
  `src/ada_challenge/challenge/api/endpoints/challenge/_payload_manager.py`
- Miner image template:
  `examples/miner_commit`
- Prepared image files:
  `examples/miner_commit/src/commit`
- Manual scoring instructions:
  `docs/Testing_manuals.md`
- Repository skills:
  `skills`

Do not publish an image without separate human confirmations for build and push. Use only a
fully tagged private Docker repository and build for `linux/amd64`.
