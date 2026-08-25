# Publish Checklist

- The human followed `docs/Testing_manuals.md`, states the achieved score, and explicitly
  accepts it.
- Source submission passes structural and ESLint validation.
- Repository includes a tag and the human confirms it is private.
- Prepared `examples/miner_commit/src/commit` contains exactly six JavaScript files:
  `ads_power.js`, `dolphin_anty.js`, `gologin.js`, `headless.js`, `multilogin.js`, and
  `octo.js`. It does not include `nstbrowser.js`.
- Prepared files pass validation.
- First confirmation authorizes the linux/amd64 Docker build.
- Build completes successfully.
- Second confirmation authorizes `docker push`.
- Push output includes a repository digest.

Never treat a previous conversation's general approval as confirmation for a new image tag.
