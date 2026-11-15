# Erratum to `docs/ASSURANCE_v0.4_SHA256_MANIFEST.json` (2026-11-15)

The v0.4 manifest is a historical record and is left unchanged. It is **not** the current pin for any artifact.

| Path | Stale sha256 in v0.4 manifest | Current sha256 (2026-11-15, branch `x1-rebaseline`) |
|---|---|---|
| `artifacts/research/reexecuted-factorial.json` | `f45c908680766229be98876d608ed593793c523f0b75c0b4291cb8539839c15c` | `682d53221a6c9d94f6d51269d88401c27f024c44353a5dc69abd6cc5039215e1` |

- The value in the v0.4 manifest was already stale before the X1 re-baseline (the file in `main` @13ef67e1 had sha `3f88031e7cc4397d13a27e926e919d025f4a49aa433b7dd3a3bb368d2c0e7f99`, now preserved as `artifacts/research/reexecuted-factorial.v0x-seed-invariant.json`).
- On 2026-11-15 the artifact was regenerated so that its `scenario_sha256` values match the current scenario contracts; results and trace digests are unchanged.
- The current pin is the `artifact_sha256` of claim E108 in [`docs/CLAIMS_REGISTER.json`](CLAIMS_REGISTER.json).
