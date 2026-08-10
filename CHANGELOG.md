# Changelog

## v3.0.0 (unreleased)

Initial ADA-3 structure.

- Rebased the repository onto the ABS v6 project structure: `src/aad_challenge`
  Python package, nested challenge API, skills, config templates, and the
  four-stage release workflow.
- Replaced the automation-framework targets with five commercial anti-detect
  browsers: AdsPower, Dolphin Anty, GoLogin, Multilogin, and Octo Browser, each
  mapped to its bot-runner `antidetect` driver preset.
- Kept the `AAD_` environment prefix, `AADChallengeManager`, and `AADController`
  naming from ADA v2.
- Reduced the submission from nine detector files to six.
