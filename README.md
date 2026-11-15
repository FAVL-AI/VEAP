# VEAP — Verifiable Embodied Agent Platform

[![CI — Integrated Scientific Gate](https://img.shields.io/badge/CI-Integrated_Scientific_Gate-2ea44f?style=flat-square)](#continuous-verification--governance)
[![Physics — MuJoCo 4.0.1](https://img.shields.io/badge/Physics-MuJoCo_4.0.1-0f172a?style=flat-square)](#tools--framework-architecture)
[![Physics — Isaac Lab 0.54.3](https://img.shields.io/badge/Physics-Isaac_Lab_0.54.3_%2F_Isaac_Sim_5.1-76b900?style=flat-square)](#tools--framework-architecture)
[![Robotics — ROS 2 & MCAP](https://img.shields.io/badge/Robotics-ROS_2_%2F_MCAP-22314e?style=flat-square)](#tools--framework-architecture)
[![Custody — Ed25519 & Rust Verifier](https://img.shields.io/badge/Custody-Ed25519_%2B_Rust_Verifier-b45309?style=flat-square)](#tools--framework-architecture)

**An evidence-first evaluation, cross-simulator replay, and runtime assurance platform for autonomous and embodied AI.**

> **Core Definition:** VEAP is a **model- and harness-agnostic evaluation protocol** that jointly measures **task success**, **constraint violations**, **recovery**, **resource cost**, and **independently checkable evidence** under **controlled faults**.

> **Evidence & Claim Boundaries:** Components carry explicit maturity labels (`Core v0.1.0`, `Evidence R1.1–R1.3`, `Studio R0.3 / VEAP Foundry`, `M3 Replay R0.1`, and `v0.6 kinematic planar cross-engine replay agreement — gate FAILED 18/20`). **No production readiness, SOTA superiority, independently attested hardware ground truth, or physical safety certification is claimed.**

---

## Tools & Framework Architecture

| Layer | Technologies & Frameworks | Role in VEAP | Evidence Boundary |
|---|---|---|---|
| **Core Benchmark & Safety Gate** | `Python 3.10+`, `Pydantic v2`, `FastAPI`, `Uvicorn`, `SQLite` | Deterministic scenario contracts (`veap-scenario/1`), greedy & A\* route planners, geometric safety gate, SHA-256 hash-linked event ledger | `veap/` (`v0.1.0`, deterministic 2-D kinematic benchmark) |
| **Native Physics & 3-D Scene Pipeline** | `MuJoCo 4.0.1`, `NVIDIA Isaac Lab 0.54.3` / `Isaac Sim 5.1.0.0` (`PhysX`, `CUDA`), `OpenUSD (.usda)`, `MJCF (.xml)`, `URDF`, `SDF 1.10`, `glTF 2.0 (.glb)` | Locked open-loop command-tape replay (`veab-control-tape/1`), `ENU_z_up_m` scene compilation, `ContactSensor` instrumentation, 40-trace held-out gate (FAILED 18/20) | `veap/simulation/` (`v0.6`, uncalibrated kinematic planar surrogate, gravity disabled; `eligible_for_physics_equivalence_claim = false`) |
| **Assurance Studio / VEAP Foundry** | `VEAP Studio R0.3`, `FastAPI`, `Vanilla JS / Canvas`, `OIDC` (`VEAP_OIDC_*`) | Read-only multi-tenant replay, assurance & contract monitor, native runtime workbench, evidence claim ladder (`G0–G3`) | `veap_studio_r03/`, `veap/enterprise/` (local evaluation; live IdP auth unverified) |
| **Cryptographic Custody & Verification** | `Ed25519` (`R1.3`), `HMAC-SHA256`, `Rust` (`backend/rust_verifier`), `Go` (`veap-go-orchestrator`) | Independent trace verification, three-valued evidence certificates, public-key reference custody | `veap_evidence_r1_1/`, `backend/` (software-tested custody; synthetic R1.1/R1.2 certificates) |
| **Robotics & Telemetry Ingest** | `ROS 2 Humble` (`rosbag2`), `MCAP` (`mcap_decode.py`), `JSONL` | Read-only external trajectory and bag metadata ingest with explicit untrusted-provenance labelling | `veap/m3_replay/` (`R0.1`, synthetic metadata contract; physical sensor gates open) |
| **Governance & CI/CD** | `GitHub Actions`, `Pytest`, `docs/CLAIMS_REGISTER.json`, `scripts/check_claims.py` | Continuous verification, scientific software gate, SHA-256 claims audit, native MuJoCo candidate gate | `.github/workflows/` |

---

## Visual Surfaces: VEAP Foundry

### 1. Physical AI Replay Operations
Multi-camera synchronized replay, 3-D digital twin viewport (`M3-WAREHOUSE` / `KEEP-OUT`), Assurance Inspector (`41 recorded events`), time-series telemetry, cross-engine discrepancy panel, and synchronized mission timeline.

![VEAP Foundry — Physical AI Replay Operations](docs/veap-foundry-replay.jpg)

### 2. VEAP Foundry / Studio R0.3 (`veap_studio_r03/`)
Enterprise & research assurance workbench featuring the **Evidence Claim Ladder (`G0–G3`)**, separate-process contract monitor, and native simulator runtime status.

| Assurance & Evidence Claim Ladder | Native Runtime Workbench |
|---|---|
| ![VEAP Foundry — Assurance & Verification](veap_studio_r03/screenshots/VEAP_Studio_R03_Assurance.png) | ![VEAP Foundry — Native Runtime Workbench](veap_studio_r03/screenshots/VEAP_Studio_R03_Runtime_Workbench.png) |

---

## Canonical Research Narrative: From Apparent Success to Verifiable Autonomy

### X1 re-baseline (v0.7-x1, branch `x1-rebaseline`, prereg `X1_PREREG_v3` sha `784382af…10c7`, params `X1_PARAMS.json` sha `7924e78e…cd94`)

In VEAP's deterministic 2-D toy benchmark (v0.7-x1; 3 held-out test scenarios × 20 seeded perturbations), an obstacle-ignoring greedy baseline without the safety gate reached its goal but failed verification by a verifier separate from the agent in 34 of 60 runs (0.57; scenario-clustered 95% CI 0–1, n = 3 scenarios). With the gate on, violations were 0 in all 60 runs. This demonstrates the metric; it is not an estimate of real-agent behaviour.

- **Conditional on completion:** 34 of 40 completed greedy gate-off runs failed verification (34/40, next to 34/60 of all runs; scenario-clustered 95% CI for 34/60 is 0–1, n = 3 scenarios).
- **Absence scenario:** greedy never completes `absence-rejection` (0/20); completion there means correctly declaring the target absent within budget, which the greedy baseline never does.
- **Per scenario (greedy, gate off; descriptive Wilson 95% CIs):** `absence-rejection` 0/20 completed−verified; `distribution-shift` 14/20 [0.48, 0.85]; `hospital-inspection` 20/20 [0.84, 1.00]. Every test cell has 20/20 distinct trace digests (effective n = nominal n per cell; clustered n = 3 scenarios).
- **Exploratory:** the route planner without the gate failed verification in 1 of 60 test runs (3 violations).
- **Faults:** faults / recovered faults for the injected actuation dropout are **not measured**. Limitation: the ledger cannot see injected dropout as a fault event (it is a hashed flag on `state` payloads only), so the verifier's fault counters do not include it.
- **Perturbation ladder (selected L3):** start-pose σ 0.20 m, obstacle jitter 0.20 m (uniform half-width), observation-noise σ 0.10 m, per-tick actuation-dropout p 0.15. L3 is the top of the pre-registered ladder; the selection rule (train+val only) did not bind below it.
- **Evidence:** [`x1/step3/X1_TEST_ANALYSIS.json`](x1/step3/X1_TEST_ANALYSIS.json) (sha `bfcac6bc3e93d69bdff62b4732fe8117d13b7ca7020b02ec2552d85ecd584d7c`), [`x1/step3/test_records_L3.json`](x1/step3/test_records_L3.json) (sha `0b66a0cb1a6fd16b0e7388e093c483253075c0c2c9ee8a81db5f1031ae7de33f`), claims E103–E108 in [`docs/CLAIMS_REGISTER.json`](docs/CLAIMS_REGISTER.json). Test split run once after the freeze; steplog `logs/STEPLOG.md` (hash-chained from the gate entries on).
- **Reproducibility note:** three scripts were written after the parameter freeze. They sit outside the harness (`veap/` is unchanged since the freeze) and each re-verifies the frozen shas (`X1_PARAMS.json` and the code shas it records) before use:
  - `x1/step3_test_once.py` sha `e4b448f1f6c9e7f5241f314597fba126375c080ebd1be0c80e26d6ae7151288b` (one-shot test runner; refuses to overwrite existing output)
  - `x1/step3_analyze.py` sha `4f143f375f3a94304063c5261095f45c35549a382be48ea9c9556b742b99868a` (scenario-clustered bootstrap, 10,000 resamples, seed 0; Wilson CIs descriptive only)
  - `x1/gates_ab_check.py` sha `a9c5e93c20b7aae3b847a6a1b2a8018b3aea35d8091e0a3e9959bcf3d849e2be` (pre-run gates: dropout flag is inside the hashed trace; violations scored on the true pose; validation data only)

### Legacy table — v0.x, seed-invariant (effective n = 5 scenarios)

Kept for the record. `5` scenarios × `3` seeds × `2` policies × `2` gate settings = 60 nominal runs, but in 16 of 20 (scenario, policy, gate) cells all 3 seeds produce the identical trace digest, so the effective n is 5 scenarios. Train, validation and test splits are mixed in this table and it has no CIs.

| Configuration | Task completion | Verified completion | Safety violations |
|---|---|---|---|
| **Greedy, gate off** | `12/15` | `3/15` | `147` |
| **Greedy, gate on** | `12/15` | `12/15` | `0` |
| **Route, gate off** | `15/15` | `15/15` | `0` |
| **Route, gate on** | `15/15` | `15/15` | `0` |

In this legacy table, ungated greedy runs that reached the goal but were rejected by the verifier occur in 3 of 5 scenarios (metric demonstration; greedy ignores obstacles by construction). Artifact: [`artifacts/research/reexecuted-factorial.json`](artifacts/research/reexecuted-factorial.json), regenerated on `x1-rebaseline` so `scenario_sha256` matches the current scenario contracts (new sha `682d53221a6c9d94f6d51269d88401c27f024c44353a5dc69abd6cc5039215e1`; results and trace digests identical to the previous file). The previous artifact, whose `scenario_sha256` values did not match the current contracts, is preserved byte-for-byte as [`artifacts/research/reexecuted-factorial.v0x-seed-invariant.json`](artifacts/research/reexecuted-factorial.v0x-seed-invariant.json) (sha `3f88031e7cc4397d13a27e926e919d025f4a49aa433b7dd3a3bb368d2c0e7f99`). See [docs/CANONICAL_NARRATIVE.md](docs/CANONICAL_NARRATIVE.md).

---

## v0.6 Kinematic Planar Cross-Engine Replay Agreement (`MuJoCo` × `Isaac Lab`) — gate FAILED 18/20

Executed on an **NVIDIA RTX 4080 SUPER** workstation (`MuJoCo 4.0.1` and `Isaac Lab 0.54.3 / Isaac Sim 5.1.0.0`) using frozen open-loop command tapes (`veab-control-tape/1`). Both engines run kinematic bodies with gravity disabled (`disabled_planar_surrogate_at_z_0.16m`), so this is a kinematic planar replay agreement, not native-physics equivalence. **Release gate result: `gate_passed = false` — gate FAILED 18/20.** Audit of the report was internal (an internal audit subagent), not external.

| Stage | Scope & Artifact | Recorded Outcome |
|---|---|---|
| **1. Pilot Localization** | [`v06-pilot-per-tick-diagnostic.json`](artifacts/research/v06-pilot-per-tick-diagnostic.json) | `0.20182817 m` pilot RMSE repeats with `0.0 m` drift; localized to tick-0 gravity drop (`z = 0.16 → 0.135 m`) + PhysX Coulomb static-friction stall (`ticks 2–18`) and `25/25` missing right contacts. The pilot divergence was resolved by disabling gravity, i.e. by removing that physics. |
| **2. Model Alignment & Contacts** | [`isaaclab_native_runner.py`](veap/simulation/isaaclab_native_runner.py), [`v06-stage2-contact-verification.json`](artifacts/research/v06-stage2-contact-verification.json) | Aligned `ENU_z_up_m` frames, explicit `WXYZ → XYZW` quaternions, `s⁻¹` damping, and `ContactSensor` instrumentation distinguishing `0`, `> 0`, and `null` (never coerced to `0`). |
| **3. Frozen Manifest** | [`v06-evaluation-manifest.json`](artifacts/research/v06-evaluation-manifest.json) | Froze criteria (`max_position_rmse_m <= 0.100 m`, `P90 <= 0.150 m`, `max <= 0.200 m`, `timegrid <= 1e-6 s`, `0` missing contacts), scene/asset hashes, preserved `0.20182817 m` pilot, and `20` `test`-split tapes across `3` task families (tapes from the same generator as the manifest). |
| **4. 40-Trace Release Gate** | [`v06-release-gate-report.json`](artifacts/research/v06-release-gate-report.json), [`v06-heldout-traces/`](artifacts/research/v06-heldout-traces/) | **gate FAILED 18/20** (`gate_passed = false`). 40 kinematic traces (`372` samples, about 9 per trace): `mean_rmse = 0.0135539 m`, `max_rmse = 0.06157238 m`, `max_error = 0.08551475 m`, `timegrid_err = 0.0 s`, `0` missing contacts. `insp-07` & `insp-08` failed (`0.0769` binary contact-state disagreement from a 1-tick PhysX contact-offset lead). Claim E106. |

See [README_V06.md](README_V06.md) and [docs/release/V06_NATIVE_ACCEPTANCE_PROTOCOL.md](docs/release/V06_NATIVE_ACCEPTANCE_PROTOCOL.md).

---

## Quick Start — Linux, macOS, or Windows (Python 3.10+)

```bash
git clone https://github.com/FAVL-AI/VEAP.git
cd VEAP
python -m venv .venv
source .venv/bin/activate             # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[test]'
python -m pytest -q
python -m uvicorn veap.api:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000** to launch the **VEAP Agent Observatory**. Select a scenario contract, choose a baseline (`route` or `greedy`), toggle the geometric safety gate, and run the benchmark. Exported evidence JSON bundles are independently verifiable via `python -m veap verify <bundle.json>`.

---

## Command-Line Experiments & Native Replay

```bash
# Discover task contracts and split labels
python -m veap scenarios

# Execute an auditable simulation trial with seed 17
python -m veap run --scenario warehouse-transfer --policy route --seed 17 --out artifacts/warehouse.json

# Independently verify a standalone evidence bundle
python -m veap verify artifacts/warehouse.json

# Run the legacy v0.x factorial suite (seed-invariant; effective n = 5 scenarios)
python -m veap suite --seeds 0 1 2 --split all --out artifacts/suite-summary.json

# v0.6 MuJoCo replay & 40-trace gate evaluation (recorded result: gate FAILED 18/20)
python scripts/veap_v06.py run-mujoco --tape artifacts/research/v06-control-tape.json --out artifacts/v06/mujoco
python scripts/veap_v06.py evaluate-gate \
  --manifest artifacts/research/v06-evaluation-manifest.json \
  --traces-dir artifacts/research/v06-heldout-traces \
  --out artifacts/research/v06-release-gate-report.json
```

---

## Continuous Verification & Governance

- **Claims governance:** Every registered claim in [`docs/CLAIMS_REGISTER.json`](docs/CLAIMS_REGISTER.json) is SHA-256 bound to its source artifact and validated by `python scripts/check_claims.py`. The headline claims are registered as E103–E108 (E100–E102 are reconstructed from a v0.5 snapshot).
- **Security boundary:** The default API binds `127.0.0.1` without authentication for local use only. Never expose it on an untrusted network without TLS, authentication (`VEAP_ADMIN_TOKEN` / `VEAP_OIDC_*`), and network isolation. See [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md).

## Repository Layout

```text
veap/                    Core spec, planners, simulator, ledger, verifier, M3 replay, native runners & v0.6 gate
veap_evidence_r1_1/      R1.1–R1.3 three-valued evidence & Ed25519 public-key custody extension
veap_studio_r03/         VEAP Foundry / Studio R0.3 multi-tenant UI, monitors, and offline demo
backend/                 Rust standalone verifier & Go orchestrator
scenarios/               Versioned public train / validation / test task contracts
web/                     VEAP Agent Observatory (vanilla JS + isometric 3-D projection)
artifacts/research/      Frozen v0.6 pilot, diagnostic, manifest, 40 kinematic traces & gate report (FAILED 18/20)
tests/                   Pytest unit, API, claims, studio, and native MuJoCo integration suites
docs/                    Protocols, threat model, claims policy, release train, and screenshots
```

## Peer-Reviewed Foundations & Technical References

1. Zhou, S. et al. (2024). **WebArena: A Realistic Web Environment for Building Autonomous Agents.** ICLR 2024. https://proceedings.iclr.cc/paper_files/paper/2024/hash/4410c0711e9154a7a2d26f9b3816d1ef-Abstract-Conference.html
2. Zhu, Y. et al. (2025). **Establishing Best Practices in Building Rigorous Agentic Benchmarks.** NeurIPS 2025, Datasets and Benchmarks. DOI: **10.52202/085713-5547**. https://proceedings.neurips.cc/paper_files/paper/2025/hash/f316275b44ee2de533102913828a8107-Abstract-Datasets_and_Benchmarks_Track.html
3. Xie, T. et al. (2024). **OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments.** NeurIPS 2024. https://os-world.github.io/
4. NVIDIA Isaac Lab Direct Workflow & Sensor Documentation: https://isaac-sim.github.io/IsaacLab/develop/source/tutorials/03_envs/create_direct_rl_env.html
5. MuJoCo Python API Documentation: https://mujoco.readthedocs.io/en/stable/python.html
6. ROS 2 `rosbag2` & MCAP Recording Specification: https://github.com/ros2/rosbag2 · https://mcap.dev/guides/getting-started/ros-2
