# ADA-3 Agent Guide

## Objective

Develop six browser-side JavaScript detectors that identify expected anti-detect browser
w/o firing on human-driven browsers. Work only from evidence that is permitted by
challenge; browser fingerprinting is prohibited.

Unlike ABS, targets here are not Python automation frameworks. Each target is
commercial anti-detect browser — paid desktop application that launches managed profile
and is driven over its own loopback API. Detection must therefore key on artifacts
product itself leaves in page environment, not on WebDriver or CDP automation flag.

## Required Workflow

1. Use `research-bot-detection` for current papers, official product changes, and provider
   research. Mark fingerprinting findings as prohibited.
2. Edit files in
   `src/ada_challenge/challenge/templates/static/detections`.
3. Use `validate-submission` before every score attempt.
4. Follow `docs/Testing_manuals.md` to start challenge, call `/score`and complete any
   requested human verification. local score helper is not usable in miner workflows.
5. Review score and available challenge output, then diagnose missed browsers,
   collisions, human failures, and headless failures; iterate.
6. Use `build-submission` only after human states achieved score and confirms it is
   satisfactory.

## Submission Files

submission contains exactly:

- `ads_power.js` — AdsPower
- `dolphin_anty.js` — Dolphin Anty
- `gologin.js` — GoLogin
- `headless.js` — headless browser, any vendor
- `multilogin.js` — Multilogin
- `octo.js` — Octo Browser

Keep existing fn `window` export names. Each file must be at most 500 lines
must pass `examples/miner_commit/eslint.config.mjs`.

NSTBrowser is sixth anti-detect browser that is deliberately **not** in this list yet. Its
prior integration is preserved under `docs/reference/nstbrowser/`. Do not add `nstbrowser.js`
to contract until bot-runner driver and preset exist — miners must never be asked for
detector against target that is never scheduled.

## Scoring Model

- Browser detection contributes 90% of current local score.
- Headless detection contributes 10%.
- Collisions receive reduced credit.
- Any browser or headless detection during human task makes final score zero.
- protected endpoints use `X-API-Key` w/ `ADA_CHALLENGE_API_KEY`.
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

API, config, and payload schema still use `framework` as generic term for "the target
under test" (`framework_images` `framework_name` `ADA_FRAMEWORK_NAMES`). In ADA-3 those
slots hold anti-detect browser names. term is retained b/c it is baked into
prebuilt React bundle shipped in `templates/static/js`whose source lives outside this repo.

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
- repo skills:
  `skills`

Do not publish image w/o separate human confirmations for build and push. Use only
fully tagged private Docker repo and build for `linux/amd64`.
