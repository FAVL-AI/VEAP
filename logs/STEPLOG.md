# VEAP X1 steplog (append-only)
Spec: /workspace/veap_plans/X1_PREREG_v1.md sha256 49e6f25e63ba020b801c2f1ef0ee86ba92c2811903d888a9c85d728a54a008f1 (verified on box before start).
Host: favl Linux 6.8.0-149-generic x86_64, 28 CPUs. Entries are appended by logs/slog.sh; never edited.

### step0.clone
- cmd: `git clone -q ~/veap ~/veap_x1 && git checkout -b x1-rebaseline 13ef67e1bf132b19af5a211ebca9d0e0728e520f`
- utc: 2026-11-15T21:42:30Z | london: 2026-11-15T21:42:30+0000
- cwd: /home/favl
- exit: clone 0, checkout 0 | wall_s: .057892189
- head: 13ef67e1bf132b19af5a211ebca9d0e0728e520f (source ~/veap HEAD also 13ef67e1…; origin/main on GitHub = db799e513f635b63e425ce6fd3bdd92470b72d5f, NOT used, per spec pin @13ef67e1)
- df -B1 avail before: 50689970176 | after: 50680528896
- output: NOT CAPTURED (quiet clone)
- deviation: steplog helper created after clone, so this entry was written by hand from captured shell values. Steplog file name follows spec (logs/STEPLOG.md), not the brief's X1_STEPLOG.md.

### step0.venv
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH /home/favl/miniforge3/bin/python3 -m venv .venv`
- utc: 2026-11-15T21:42:51Z | london: 2026-11-15T21:42:51+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: 1.061414634
- head: 13ef67e1bf132b19af5a211ebca9d0e0728e520f
- df -B1 avail before: 50680737792 | after: 50667765760
- output: /home/favl/veap_x1/logs/out/20261115T214251Z_step0_venv_.txt (sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855)
- deviation: -

### step0.pip_install
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PIP_DISABLE_PIP_VERSION_CHECK=1 .venv/bin/pip install -q -e .[test]`
- utc: 2026-11-15T21:42:53Z | london: 2026-11-15T21:42:53+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: 4.693448406
- head: 13ef67e1bf132b19af5a211ebca9d0e0728e520f
- df -B1 avail before: 50667765760 | after: 50631716864
- output: /home/favl/veap_x1/logs/out/20261115T214253Z_step0_pip_install_.txt (sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855)
- deviation: -

### note.spec_v2 (steering 21:43 London)
- Step 2 now follows /workspace/veap_plans/X1_PREREG_v2.md sha256 5de57cf7b51b417e760721cec40a8811ec2b0330ab67e6160febfe00dc6646e3 (verified on box). Parameter selection NOT run; X1_PARAMS.json NOT frozen pending reviewer ACCEPT of v2.

### step0.provenance
- cmd: `bash -c env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -VV; env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -c 'import sys;print(sys.executable)'; env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/pip freeze --exclude-editable; env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/pip --version; git rev-parse HEAD; git status --porcelain | head; uname -a; lscpu | grep -E 'Model name|^CPU\(s\)'; free -b | head -2; nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>&1 | head -1; echo CUDA_VISIBLE_DEVICES=[$CUDA_VISIBLE_DEVICES]`
- utc: 2026-11-15T21:43:14Z | london: 2026-11-15T21:43:14+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .280094291
- head: 13ef67e1bf132b19af5a211ebca9d0e0728e520f
- df -B1 avail before: 50631704576 | after: 50631700480
- output: /home/favl/veap_x1/logs/out/20261115T214314Z_step0_provenance_.txt (sha256 5b79949e6ed027ad1787067131ef33e6d5893bdd2bd4cf3abf578d047d164c2f)
- deviation: -

### step1.suite_reproduce
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m veap suite --seeds 0 1 2 --split all --out x1/step1/suite-summary.json`
- utc: 2026-11-15T21:43:25Z | london: 2026-11-15T21:43:25+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .322687279
- head: 13ef67e1bf132b19af5a211ebca9d0e0728e520f
- df -B1 avail before: 50631675904 | after: 50631512064
- output: /home/favl/veap_x1/logs/out/20261115T214325Z_step1_suite_reproduce_.txt (sha256 adde2244d3dea3e48364bdfd284b8ba6a2b6e6c6bba8e83f19bdd5ad37464456)
- deviation: --out x1/step1/suite-summary.json instead of default artifacts/suite-summary.json (keeps tracked tree clean)

### note.spec_v3 (steering 21:43–21:44 London)
- Spec superseded by /workspace/veap_plans/X1_PREREG_v3.md sha256 784382afe11be46c7863ef1a2a02f4f72a66d0cf1c57421f1830fa84f6aa10c7 (verified on box). Reviewer ACCEPT of v3 relayed by PHD via parent at 21:44 London; step-2 selection authorised on train+val seeds 0..19 only.

### step1.analyze
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH .venv/bin/python x1/step1_analyze.py`
- utc: 2026-11-15T21:44:13Z | london: 2026-11-15T21:44:13+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .024442394
- head: 13ef67e1bf132b19af5a211ebca9d0e0728e520f
- df -B1 avail before: 50631442432 | after: 50631434240
- output: /home/favl/veap_x1/logs/out/20261115T214413Z_step1_analyze_.txt (sha256 390375f4efd107ab103cc9d862f2ac40e5fac333615ed084a85cdd30dd58cb05)
- deviation: -

### step2.pytest_x1_and_full
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q -p no:cacheprovider`
- utc: 2026-11-15T21:45:54Z | london: 2026-11-15T21:45:54+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: 8.724065955
- head: 13ef67e1bf132b19af5a211ebca9d0e0728e520f
- df -B1 avail before: 50630336512 | after: 50628984832
- output: /home/favl/veap_x1/logs/out/20261115T214554Z_step2_pytest_x1_and_full_.txt (sha256 8cffa21cf836a25fb0e38ed40aeee4cf093c3507187cc94dc11c07f56ee0680a)
- deviation: -

### note.adversarial_fixture_count
- utc: 2026-11-15T21:46:31Z | london: 2026-11-15T21:46:31+0000 | cwd: /home/favl/veap_x1 | file: tests/test_adversarial_fixtures.py sha256 7104340a09001f95d2571af310c9240a7185c6fd8db18785e17b3b727e35243e @13ef67e1
- PHD/reviewer figure (prereg v3): fixtures numbered 1..37 and 38 test functions.
- Measured: `grep -cE '^def test_'` = 38 test functions; `grep -oE '^def test_fixture_[0-9]+'` = 37 functions, numbers 01..37 with no duplicates and no gaps; the 38th is test_gate1_adversarial_fixture_count_and_recall (aggregate, not a fixture); `pytest --collect-only` = 38 tests collected (no parametrisation).
- Result: MATCH. Cite only as "fixtures numbered 1..37 and 38 test functions".
- deviation: none (manual entry; commands run interactively, outputs captured in this note).

### deviation.steplog_edit
- While writing note.adversarial_fixture_count I appended a malformed placeholder line ('- utc: $(date) placeholder replaced below') and removed it with `sed -i '$d'` seconds later, before any other entry. This is the only non-append edit to this file; no prior content was changed.

### step2.selection
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python x1/step2_select.py`
- utc: 2026-11-15T21:46:52Z | london: 2026-11-15T21:46:52+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: 2.928169306
- head: 112a4af98312c37ad2644dd3a6ffeb4bfbf67e81
- df -B1 avail before: 50628763648 | after: 50628288512
- output: /home/favl/veap_x1/logs/out/20261115T214652Z_step2_selection_.txt (sha256 569f5d263daf3697ad38e2b520e62a832612c3999537674df633b2ac0c458b50)
- deviation: -

### step2.check_claims
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH .venv/bin/python scripts/check_claims.py`
- utc: 2026-11-15T21:47:23Z | london: 2026-11-15T21:47:23+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .025702833
- head: 112a4af98312c37ad2644dd3a6ffeb4bfbf67e81
- df -B1 avail before: 50628259840 | after: 50628255744
- output: /home/favl/veap_x1/logs/out/20261115T214723Z_step2_check_claims_.txt (sha256 a4c1a8debddecbb4f245c942214dffcc89cc76dafde65aaa3618bf68c8d75af1)
- deviation: -

### step2.freeze X1_PARAMS.json
- utc: 2026-11-15T21:47:23Z | london: 2026-11-15T21:47:23+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50628255744
- X1_PARAMS.json sha256 7924e78ec25fd5b52b27d49e229d310533c3e3fe6ea6efdd79b5141df0c3cd94; selection.json sha256 7297bb09184a7a8c61965db3eb38a0e95b4b21763a10b352246c7331508cabc1
- Seed entry point found: veap/sim.py run_episode, `rng = random.Random(seed)`, consumed ONLY by scenario perception_noise faults (uniform ±0.24 m) -> explains 4/20 seed-varying cells (distribution-shift only; hospital-inspection's noise fault did not change its digest).
- Condition table (train+val, seeds 0..19; (a) route+gate-on verified >=36/40; (b) min distinct digests over 8 train/val cells >=15/20):
  - L0: a 40/40 PASS | b 1/20 FAIL | qualifies NO
  - L1: a 40/40 PASS | b 20/20 PASS | qualifies YES
  - L2: a 40/40 PASS | b 20/20 PASS | qualifies YES
  - L3: a 40/40 PASS | b 20/20 PASS | qualifies YES
- Selected: L3 (largest qualifying). Qualification monotone/contiguous (L1–L3). L3 is the ladder ceiling, so the rule did not bind.
- Non-monotone pattern found (secondary, not used in selection): warehouse-transfer route gate-OFF verified 20/20 (L0), 16/20 (L1), 19/20 (L2), 18/20 (L3); violations 0, 30, 3, 15.
- Test split NOT run. Awaiting reviewer clearance of params.
- deviation: manual entry; selection itself logged by slog as step2.selection.

### gate.c hash-chained steplog (chain start)
- prev_entry_sha256: fb276510805d89d312e08ae718422052364e39eae548ec3ff596b81031abd860
- utc: 2026-11-15T21:49:54Z | london: 2026-11-15T21:49:54+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50631196672
- From this entry on, every entry carries prev_entry_sha256 = sha256 of the previous entry's bytes (from the start of its '### ' line to EOF, as computed by logs/prev_entry_sha.py). Implemented in logging tools only (logs/slog.sh, logs/note.sh, logs/prev_entry_sha.py); harness code untouched.
- Chain start = sha256 of last pre-existing entry ('### step2.freeze X1_PARAMS.json'): fb276510805d89d312e08ae718422052364e39eae548ec3ff596b81031abd860
- Freeze integrity re-checked before test: X1_PARAMS.json sha256 7924e78ec25fd5b52b27d49e229d310533c3e3fe6ea6efdd79b5141df0c3cd94; code_sha256 for veap/sim.py, verifier.py, x1_perturb.py, x1_stats.py all match; HEAD 864e660e48f1ea310c83ecbdc7a9d8978feb624e; tracked tree clean.

### gate.a_b trace inspection (validation scenario, L3, seed 0, greedy gate off)
- prev_entry_sha256: 455a37fe1bbe372065df84d476f20ebd6785319d69e734025fa546d2ac421e47
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH .venv/bin/python /tmp/x1_gates_ab.py`
- utc: 2026-11-15T21:50:09Z | london: 2026-11-15T21:50:09+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .084305661
- head: 864e660e48f1ea310c83ecbdc7a9d8978feb624e
- df -B1 avail before: 50630160384 | after: 50630156288
- output: /home/favl/veap_x1/logs/out/20261115T215009Z_gate_a_b_trace_inspection__validation_scenario__L3__seed_0__greedy_gate_off__.txt (sha256 5c05bc39a1b93551fd605ef0013621774493a1939df9c80c9b1bdf1f05f7217c)
- deviation: script /tmp/x1_gates_ab.py, output in logs/out; no test-split data touched

### gate.a_b findings
- prev_entry_sha256: 3457c27d00ed9fc3bb25034fcbd988d58132c3dab30d2eeb767c302483ea1bd4
- utc: 2026-11-15T21:50:30Z | london: 2026-11-15T21:50:30+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50631151616
- Gate (a) PASS: x1_actuation_dropout is inside the hashed trace. Code: veap/sim.py puts it in the "state" event payload; veap/ledger.py Ledger.emit hashes {seq,tick,kind,payload,prev_hash} via canonical JSON, so the flag feeds each event hash and the chained ledger_root_sha256 (= trace_sha256). Actual trace (warehouse-transfer [validation], greedy, gate off, L3, seed 0): 8 flagged state events = manifest actuation_dropout_ticks 8; event 3 hash f8c9f900…164a recomputes equal WITH the flag, NOT equal without it; check_chain(original)=valid, check_chain(flag stripped)=event digest mismatch at 3; root f5ed5cea…bfee = last event hash.
- Gate (b) PASS: violations are scored on the TRUE pose. Code: sim emits "state" x,y from the true integrated pos; noisy coordinates go only into "observation" events. verifier.py computes speed/segment/clearance violations exclusively from "state" events (lines 105-131); for "observation" it reads only target_present/sensor_ok (lines 144-146), never x/y. Same trace: verifier violations 29; observed x/y differ from prior-tick true pose by up to 1.9789 m (sensor_dropout fault stale pose + noise), and that does not enter scoring.
- Limitation recorded: the injected dropout is NOT a ledger "fault" event; verifier faults/recovered_faults cannot see it -> report as "not measured", never 0.
- Script: x1/gates_ab_check.py. Both gates pass; proceeding to the one-shot test split.

### step3.TEST_SPLIT_ONE_SHOT
- prev_entry_sha256: 52d1e20477f017df40f5da0452ef976a960ad8eee416bf223ad5d67ac2c34e6b
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python x1/step3_test_once.py`
- utc: 2026-11-15T21:50:30Z | london: 2026-11-15T21:50:30+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: 1.113110707
- head: 864e660e48f1ea310c83ecbdc7a9d8978feb624e
- df -B1 avail before: 50631143424 | after: 50630930432
- output: /home/favl/veap_x1/logs/out/20261115T215030Z_step3_TEST_SPLIT_ONE_SHOT_.txt (sha256 5d329371d8de665daee7a44d93dc4d886d18e857637222d699800e05d4305ae9)
- deviation: runner x1/step3_test_once.py written after freeze (new file; no change to frozen harness code, shas asserted)

### step4.analyze test records
- prev_entry_sha256: 664ff3ae494d5ca0687cdaada18563b8085e2b4908d07efed4904d31c59febdb
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH .venv/bin/python x1/step3_analyze.py`
- utc: 2026-11-15T21:50:58Z | london: 2026-11-15T21:50:58+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: 2.041228400
- head: 864e660e48f1ea310c83ecbdc7a9d8978feb624e
- df -B1 avail before: 50630901760 | after: 50630881280
- output: /home/favl/veap_x1/logs/out/20261115T215058Z_step4_analyze_test_records_.txt (sha256 36ff5ccd1c47860a1bf1b582924e5b0cd8748985e13876fb12044f9a4894ba2c)
- deviation: analysis script x1/step3_analyze.py written after freeze (new file)

### step4.results (test split, one shot, L3, seeds 0..19)
- prev_entry_sha256: 4faec673e4717a45ea47051f4340604597a6807f991e63bc135f8917e94cfa97
- utc: 2026-11-15T21:51:18Z | london: 2026-11-15T21:51:18+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50630864896
- Test split ran exactly once (step3.TEST_SPLIT_ONE_SHOT, exit 0, 240 records; 3 scenarios absence-rejection, distribution-shift, hospital-inspection). No rerun.
- PRIMARY greedy gate-off (completed - verified)/n = 34/60 = 0.5667 (completed 40, verified 6); scenario-clustered bootstrap 95% CI [0.0, 1.0], 10,000 resamples, seed 0, n = 3 scenarios; effective n = 60 distinct digests of 60. Per scenario: absence-rejection 0/20, distribution-shift 14/20, hospital-inspection 20/20.
- SECONDARY route gate-off mean violations 0.05 per run (3 total, all distribution-shift), clustered 95% CI [0.0, 0.2].
- Injected-dropout faults/recovered_faults: not measured (ledger has no fault event for it).
- Outputs + sha256: see x1/step3/SHA256SUMS.

### commit.step3
- prev_entry_sha256: f637515655931c6717bfc5234feda0a552147422ad2149aa2f59be28dd6d84ae
- utc: 2026-11-15T21:51:18Z | london: 2026-11-15T21:51:18+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50630672384
- Outputs committed locally on x1-rebaseline as b1f8d230730ecb47b09375e2dc363ff3a3372802 (author/committer Frank Asante Van Laarhoven <frankleroyvan@gmail.com>). Not pushed. This entry is committed in a follow-up steplog-only commit.
