# NSTBrowser — parked integration

NSTBrowser is an anti-detect browser and a legitimate ADA-3 target. It is **not**
in the active roster yet. This directory preserves the working integration that
existed in this repo before the ABS v6 restructure so it can be revived
deliberately rather than rediscovered by accident.

## Status

| | |
| --- | --- |
| In `challenge.yml` roster | No |
| In the submission contract | No — miners are not asked for `nstbrowser.js` |
| bot-runner driver | Does not exist |
| bot-runner preset | Does not exist |

Nothing imports the code in this directory. It is reference material.

## Why it was parked, not ported

The previous integration had the **challenge itself** spawn a
`nstbrowser/browserless:latest` container via `DockerClient`. ABS v6 moved all
browser lifecycle out of the challenge and into bot-runner, and `docker` is no
longer a dependency of this service. Porting `_nst_manager.py` as live code
would reintroduce the old architecture alongside the new one.

## Why it is worth reviving

Every vendor currently in the roster — AdsPower, Dolphin Anty, GoLogin,
Multilogin, Octo — is a **licensed desktop app** reached over loopback, which
means a human-installed, licensed application on the bot-runner host. NSTBrowser
runs as a **container**, so it is the one target that can plausibly work in CI
and on a clean runner.

It also supports headless directly (`headless: true` in the profile payload,
see `challenge.yml.snippet`), which the majority of the loopback vendors do not
currently expose through their bot-runner drivers.

## Files here

- `_nst_manager.py` — the original manager, verbatim. Container lifecycle,
  profile creation via `POST /api/v2/browsers/once`, and profile teardown.
- `challenge.yml.snippet` — the original `nstbrowser` config block and the
  `verification.extra` profile payload (fingerprint, screen, launch args).

The config schema it used:

```python
class NstbrowserConfig(FrozenBaseConfig):
    api_key: SecretStr = Field(..., min_length=12, max_length=128)
    host: str = Field(...)
    port: int = Field(..., ge=1, le=65535)
    protocol: str = Field(...)

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX_CHALLENGE}NSTBROWSER_")
```

## Reviving it

The work belongs in bot-runner, not here. Use
`drivers/antidetect/octo/driver.py` as the reference implementation — it is the
most complete of the five.

1. Add `drivers/antidetect/nstbrowser/driver.py` with a `VendorSpec`:
   - `default_api_url="http://localhost:8848"`
   - `profile_env="NSTBROWSER_PROFILE_ID"`
   - `token_env="NSTBROWSER_API_KEY"` — the local API is authenticated
2. Implement `start_call` against `POST /api/v2/browsers/once`, carrying the
   profile payload from `challenge.yml.snippet`. The response exposes
   `profileId` and `port`; attach over CDP to `127.0.0.1:<port>`.
3. Implement `stop_call` against `DELETE /api/v2/profiles/{profileId}`.
4. Add `driver-presets/nstbrowser-local.yml` mirroring `octo-local.yml`.
5. Only then add `nstbrowser` to `framework_images` here, add
   `nstbrowser.js` to `EXPECTED_FUNCTIONS` in both submission skills, and ship
   the detector stub.

### Known friction

`_base.py` authenticates with a one-shot `auth_call` handshake. NSTBrowser
expects `Authorization: Bearer <token>` on **every** request, so reviving this
likely needs `_base.py` to support persistent per-request headers rather than a
single handshake. Budget for that — it is a change to shared code, not just a
new plugin.
