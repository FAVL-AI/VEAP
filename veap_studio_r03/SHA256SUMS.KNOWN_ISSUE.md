# Known issue: `veap_studio_r03/SHA256SUMS.txt` has 11 failing entries (recorded 2026-11-15)

`SHA256SUMS.txt` is left unchanged and was **not** regenerated. Checked with `sha256sum -c SHA256SUMS.txt` run inside `veap_studio_r03/`, at base commit `13ef67e1bf132b19af5a211ebca9d0e0728e520f`. The `veap_studio_r03/` tree on branch `x1-rebaseline` is byte-identical to that base. The other 32 of the 43 entries pass.

| File (relative to `veap_studio_r03/`) | Expected sha256 (in SHA256SUMS.txt) | Actual sha256 at 13ef67e1 |
|---|---|---|
| `README.md` | `90be50197da420ce029eada679cfdc2d958f4d54a06a757f4708483276242c64` | `d87193e2339f86b5a8a381221cc977df837e3f5654906cad7d4e8b0617b4857c` |
| `VEAP_Studio_R03_Offline_Demo.html` | `238ea19741c9806b0682b9e65bb39ade3ebcb0750c8762216027dec6036e6b2e` | `36245778e4da8bb4cf691912d761a5674e24f052a6e8ce5876f786aa19fd8355` |
| `docs/RUNTIME_CONFIG.md` | `4e797a1a4c699d9e9a974804ed9fcc36518bbe6f0f507baf23b1c5c74e129948` | `e85203dfbf08623b6c1ca6aa05bf0b5737b5d1ed71af900f1c670ed53bfe853c` |
| `scripts/ubuntu_quickstart.sh` | `9ec97240b97f0f1699617be66917b857aae871fe9cce6efab6a3a1a482ad202b` | `ac1797399e40412706ec721106c9c3904782a7b9dba11d2af3d6b9b17ac08df5` |
| `veap_studio/api.py` | `08ee2766deddbe9e7691d3624c76efa3cdfb89ce2ff8503d59690a8949b861a6` | `02820fc7908217b8932fafd4ea8a5c1369741a02d45b169cdf1ea751e50f51f9` |
| `veap_studio/integrations.py` | `6666d1aaaa2d48b9627c96b325b211762cc7c54aba036ce29e49ca451b192ca3` | `be5636163de42bef387b4e91333924769abc04c110324351ea99bf6ee0e236ee` |
| `veap_studio/operations.py` | `895025f720507f24d10baecbad6f6f3c0fd45abbb280e1a18e38eae4fbcb0a23` | `b0de0c94bd6069a51684478e27c7627386f7e83430202bdf10ef5b9e8101d2a6` |
| `veap_studio/store.py` | `b1755a0d6c2bf845fa30dacbb3b949cf7cc29006e2260f1490d321b305129bd7` | `9a3d78ab1f2b93dcdca2feb12b8e3352e406685289661b92286583c32b1e6455` |
| `veap_studio/world_export.py` | `11eb59a8f142f76160b2d1862af6a0e578ff9d9e852b1122d8f5f392835cbae1` | `67ec7a3d70b1e3f72e89a509ad14f780e363ad5516299fceb7810c61b19181e7` |
| `web/app.js` | `232ef5ca673bdb71ac6680f06142cd93c7a7202a81565992c8ad4e7074462c6e` | `ed61d18d89a3c8c0c554ac21e91b04ab4dca46ac096e1180712fd88a6553bb19` |
| `web/index.html` | `52ad22231a4335fc5d30b379445d0a5ebad1aa16b638925e1bcb0d01a5c8b766` | `c6dd2889944fd35228be3b395dce7a4fcbe5e6b8552ebaf32e39164b222939ef` |

## Cause: unknown

What the evidence shows, and what it rules out:
- `SHA256SUMS.txt` and all 11 files were added in the same commit, `2d5d16c` (2026-11-14, "feat(veap): rename all VEAB components to VEAP and integrate VEAP Studio R0.3 and VEAP Evidence R1.1"). None of them changed after that commit. So no later commit modified the files after the sums were written. The mismatch already existed when they were imported.
- None of the 11 files contains CR characters, so CRLF/LF line-ending differences don't explain it.
- Mechanically reversing the VEAB→VEAP rename (`VEAP`→`VEAB`, and `veap`→`veab`, with and without the product-name change) doesn't reproduce any expected sha. `veap_studio/store.py` contains no `VEAP`/`veap` string at all and still fails, and passing files do contain `VEAP`. So the rename alone doesn't explain it.
- None of the 767 blobs in this clone's object store (42 commits) has any of the 11 expected sha256 values. The hashed versions were never committed here.

The likeliest explanation is that the sums were computed on a different snapshot of these files before they were imported, but the evidence available here doesn't show what that snapshot was.

## Scope

The X1 re-baseline (branch `x1-rebaseline`) doesn't touch any file under `veap_studio_r03/`. This note is the only addition.
