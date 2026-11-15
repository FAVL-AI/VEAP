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

### step5.regenerate_factorial
- prev_entry_sha256: 0d81876b267152714abe18314d15e6edb730fc608f2b710b812083ffe6f86c11
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m veap research-run --seeds 0 1 2 --split all --out artifacts/research/reexecuted-factorial.json`
- utc: 2026-11-15T21:54:38Z | london: 2026-11-15T21:54:38+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .320558550
- head: 0274dc13912b00ffeb0cf8978b3ab2feebefc3ca
- df -B1 avail before: 50630422528 | after: 50630344704
- output: /home/favl/veap_x1/logs/out/20261115T215438Z_step5_regenerate_factorial_.txt (sha256 d4322944514ba5ce6724993655d3653174ab15143800e8447802a455fd67dccf)
- deviation: old artifact preserved via git mv as reexecuted-factorial.v0x-seed-invariant.json (sha 3f88031e…7f99, unchanged bytes)

### step5.check_claims
- prev_entry_sha256: 1a40a754a1771446f33c41116a842ea12f8b7a476ea0441116180747b018aa3f
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH .venv/bin/python scripts/check_claims.py`
- utc: 2026-11-15T21:57:05Z | london: 2026-11-15T21:57:05+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .024608031
- head: 0274dc13912b00ffeb0cf8978b3ab2feebefc3ca
- df -B1 avail before: 50628636672 | after: 50628628480
- output: /home/favl/veap_x1/logs/out/20261115T215705Z_step5_check_claims_.txt (sha256 615c7ee2706949cafedc924d3b6b3a733a612ff03ef6b56c346babe4d20c28b3)
- deviation: -

### step5.pytest
- prev_entry_sha256: 9ff4cf2f6fe771e7092f8cef10997243abc82628cc26962cabe53616ea9d80c8
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q -p no:cacheprovider`
- utc: 2026-11-15T21:57:05Z | london: 2026-11-15T21:57:05+0000
- cwd: /home/favl/veap_x1
- exit: 1 | wall_s: 10.271951986
- head: 0274dc13912b00ffeb0cf8978b3ab2feebefc3ca
- df -B1 avail before: 50628624384 | after: 50619936768
- output: /home/favl/veap_x1/logs/out/20261115T215705Z_step5_pytest_.txt (sha256 532565f72a733b51e854a1f1f54b07a2ddf9acf9cb046f739abaab22181c6543)
- deviation: -

### step5.pytest_rerun
- prev_entry_sha256: 1a9e6c283363c2d417d702c27fa6786189b017e08052a9f6f4f4414b9ea77132
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q -p no:cacheprovider`
- utc: 2026-11-15T21:57:28Z | london: 2026-11-15T21:57:28+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: 8.850587142
- head: 0274dc13912b00ffeb0cf8978b3ab2feebefc3ca
- df -B1 avail before: 50619916288 | after: 50619969536
- output: /home/favl/veap_x1/logs/out/20261115T215728Z_step5_pytest_rerun_.txt (sha256 8b34643c4e3145bf9bda0777946748dcd640e97412d879aee07204fd1f2bc2d0)
- deviation: rerun after reverting edits to the two checksum-pinned / pre-registration PREREG_VEAP_NAV_PROTOCOL.md files (first run: 1 failed test_research_v030_exact_checksums)

### step5.check_claims_rerun
- prev_entry_sha256: 917dda0fd2b5a2970c74ca93639c05b868d1c42e0bf7d7f79689e0a43220f567
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH .venv/bin/python scripts/check_claims.py`
- utc: 2026-11-15T21:57:37Z | london: 2026-11-15T21:57:37+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .041831183
- head: 0274dc13912b00ffeb0cf8978b3ab2feebefc3ca
- df -B1 avail before: 50619969536 | after: 50619965440
- output: /home/favl/veap_x1/logs/out/20261115T215737Z_step5_check_claims_rerun_.txt (sha256 615c7ee2706949cafedc924d3b6b3a733a612ff03ef6b56c346babe4d20c28b3)
- deviation: -

### step5.summary
- prev_entry_sha256: 62ae11042b6d9604609e57a45ae53067c5dc4baf3e06c7414bd92064f50cbce0
- utc: 2026-11-15T21:58:08Z | london: 2026-11-15T21:58:08+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50619785216
- Factorial regenerated: artifacts/research/reexecuted-factorial.json new sha 682d53221a6c9d94f6d51269d88401c27f024c44353a5dc69abd6cc5039215e1 (scenario_sha256 = current contracts, 60/60; results and trace digests identical). Old artifact preserved byte-for-byte by git mv as reexecuted-factorial.v0x-seed-invariant.json sha 3f88031e7cc4397d13a27e926e919d025f4a49aa433b7dd3a3bb368d2c0e7f99.
- README: verbatim headline, 34/40, absence 0/20, exploratory route line, faults not measured + dropout limitation, post-freeze script shas, legacy table labelled 'v0.x, seed-invariant (effective n = 5 scenarios)', v0.6 retitled kinematic planar replay agreement, gate FAILED 18/20, internal audit. README_V06, CANONICAL_NARRATIVE, RESEARCH_PROTOCOL and 6 other docs de-overclaimed.
- CLAIMS_REGISTER: E103-E108 added (9 claims total). check_claims exit 0. pytest 226 passed, 2 skipped, 0 failed (first run 1 failed: test_research_v030_exact_checksums, caused by my edit to checksum-pinned docs/research/PREREG_VEAP_NAV_PROTOCOL.md; both PREREG copies reverted, rerun clean).
- Forbidden-word grep saved to x1/step5/forbidden_grep.txt. Verbatim headline contains 'independent verification' (flag to PHD: conflicts with the 'independent' ban and with veap/governance/claims.py HIGH_RISK regex; README is not in check_public_copy scope so it does not fail).
- Not fixed: docs/ASSURANCE_v0.4_SHA256_MANIFEST.json lists reexecuted-factorial.json with sha f45c9086… (already stale before X1; historical v0.4 manifest, left untouched).

### commit.step5
- prev_entry_sha256: d691a9eb44a09b22dc19a8ae0b8c7aedb93f7dd7123c6a4cfcabb996059d9ef9
- utc: 2026-11-15T21:58:24Z | london: 2026-11-15T21:58:24+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50620657664
- Step 5 committed locally as c5577ae71f3d4751e13d2db800a49469549f71f8 (Frank sole author/committer, not pushed). veap_evidence_r1_1/docs/R11_RESEARCH_RESULTS.md heading edit ('findings' -> 'results') was missed by that commit's pathspec and is committed in the follow-up commit together with this entry.

### ruling.check_claims
- prev_entry_sha256: b1b90e64e766da1975985958b0a1c26c6406bd3139293a09c12b3579726131ab
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH .venv/bin/python scripts/check_claims.py`
- utc: 2026-11-15T22:01:25Z | london: 2026-11-15T22:01:25+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .028234125
- head: eda9877f70da283af63073b62984bf764f6389b3
- df -B1 avail before: 50622685184 | after: 50622676992
- output: /home/favl/veap_x1/logs/out/20261115T220125Z_ruling_check_claims_.txt (sha256 ccf72bbaf0521332e461da260793e3c8f578bc52f87b498ccfa2803b7425f8ab)
- deviation: README.md, README_V06.md added to check_public_copy scan list

### ruling.pytest
- prev_entry_sha256: 87b1eb8b757d19efcc0386ef8efd6a22c2c65fce99d014dfd7b104a7c04fc2e5
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q -p no:cacheprovider`
- utc: 2026-11-15T22:01:36Z | london: 2026-11-15T22:01:36+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: 8.586744874
- head: eda9877f70da283af63073b62984bf764f6389b3
- df -B1 avail before: 50622648320 | after: 50622623744
- output: /home/favl/veap_x1/logs/out/20261115T220136Z_ruling_pytest_.txt (sha256 6e25f8ca97ab92418a0d933fbab119e6ffc4e391f332fd4f8a5f37185f7b5017)
- deviation: -

### ruling.summary (reviewer rulings 1-2, relayed 22:00 London)
- prev_entry_sha256: 4b6f5c6c5798e61948596bfd9be897addd8bf0a068a85ee6a812bb8761266d3e
- utc: 2026-11-15T22:02:31Z | london: 2026-11-15T22:02:31+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50622562304
- (1) Headline: 'failed independent verification' -> 'failed verification by a verifier separate from the agent' in README.md (only occurrence; README_V06.md has no headline) and E103 statement. No 'agent-independent' in the sentence. veap/governance/claims.py check_public_copy scan list += README.md, README_V06.md (files_checked 4 -> 6, valid). New tests/test_readme_public_copy.py (3 tests); negative control: restoring the old phrase makes the regex match. README lines 11 ('independently checkable evidence') and 106 ('independently verifiable via python -m veap verify') unchanged and do not trip the scan or the test.
- (2) docs/ASSURANCE_v0.4_SHA256_MANIFEST.json untouched; sidecar docs/ASSURANCE_v0.4_SHA256_MANIFEST.ERRATUM.md records stale f45c908680766229be98876d608ed593793c523f0b75c0b4291cb8539839c15c, current 682d53221a6c9d94f6d51269d88401c27f024c44353a5dc69abd6cc5039215e1, date 2026-11-15. grep: README.md, README_V06.md, CLAIMS_REGISTER.json do not cite the v0.4 manifest.
- SHA256SUMS: root SHA256SUMS.txt covers none of the changed files (33/33 OK, unchanged). veap_studio_r03/SHA256SUMS.txt has 11 pre-existing FAILED lines at base 13ef67e1 (files untouched by X1), left unchanged.
- check_claims exit 0 (9 claims; copy 6 files). pytest 229 passed, 2 skipped, 0 failed.

### commit.ruling
- prev_entry_sha256: 92a07605fc12e7f6dbd4de0cb3884ac6e6506a1b061ca0f69806774878874216
- utc: 2026-11-15T22:02:31Z | london: 2026-11-15T22:02:31+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50622410752
- Rulings committed locally as 41a49901229776a0a03579f7f44601f4cd6212d1 (Frank sole author/committer, not pushed). This entry is committed in a follow-up steplog-only commit.

### x1a.pytest
- prev_entry_sha256: ac548a9d8590d76a8f19f9244efc3503144094116fb6e55edb8da9056b643082
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q -p no:cacheprovider`
- utc: 2026-11-15T22:05:28Z | london: 2026-11-15T22:05:28+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: 8.668548084
- head: 6bbe92c0c45ce38d5c6ace6df8d9a8b3cc4c17b5
- df -B1 avail before: 50621059072 | after: 50621050880
- output: /home/favl/veap_x1/logs/out/20261115T220528Z_x1a_pytest_.txt (sha256 34ef39cd925bbb0d32902b75ae85886567a1dabcf5707c12dc4711a22918ac55)
- deviation: web/index.html:78 'Do not interpret toy-world scores as SOTA.' reworded to 'Toy-world scores are not SOTA evidence.' (same denial) so the scoped-denial qualifier in check_public_copy accepts it; regex unchanged. Pre-run without this fix: 2 failed (test_current_registry_passes, test_public_copy_scan_covers_readmes_and_passes)

### x1a.check_claims
- prev_entry_sha256: e1d9f3ef1ad24c079f2ff9fca48d040edef9b978b6735445b92aaa77e69884e8
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH .venv/bin/python scripts/check_claims.py`
- utc: 2026-11-15T22:05:37Z | london: 2026-11-15T22:05:37+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .042537860
- head: 6bbe92c0c45ce38d5c6ace6df8d9a8b3cc4c17b5
- df -B1 avail before: 50621046784 | after: 50621042688
- output: /home/favl/veap_x1/logs/out/20261115T220536Z_x1a_check_claims_.txt (sha256 c19ac085f235f97e44e989f34bd633d39605d4a4b4099c90b8f6031f92a458a8)
- deviation: -

### commit.x1a public copy (pre-push item a)
- prev_entry_sha256: 4166cd0061a489b4486cb68a789f841f8ef7938c9d2b578dd7a0bfe14330b2dc
- utc: 2026-11-15T22:06:02Z | london: 2026-11-15T22:06:02+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50621001728
- web/index.html: 'INDEPENDENT VERIFICATION' heading -> 'VERIFIER SEPARATE FROM THE AGENT'; 'Computed by independent verifier' -> 'Computed by a verifier separate from the agent'; 'Evaluation uses independently checked postconditions.' -> 'Evaluation checks postconditions with a verifier separate from the agent.'; 'Independent geometric gate' -> 'Separate geometric gate'. Kept: line 28 design quote 'can be independently checked' (capability statement) and roadmap item '05. Independent safety assurance' (future external work). Element ids unchanged. Also 'Do not interpret toy-world scores as SOTA.' -> 'Toy-world scores are not SOTA evidence.' (same denial; needed so the existing scoped-denial qualifier accepts it once the file is scanned; regex unchanged).
- veap/governance/claims.py: check_public_copy scan list += web/index.html (7 files). tests/test_readme_public_copy.py FILES += web/index.html (phrase-absent and on-scan-list checks loop over all three files).
- docs/CANONICAL_NARRATIVE.md: option = exact dated banner at top. Why: VEAP's own checks are called independent in 4 places across sections (lines 63, 70, 168, 204 pre-banner) plus many neighbouring 'independent(ly)' uses that are legitimate; a one-line banner is the smaller change and does not rewrite historical narrative text.
- docs/RESEARCH_PROTOCOL.md: option = exact dated banner at top. Why: self-references at lines 72 (RQ1 wording), 92 and 133 pre-banner; rewording RQ1 would alter a protocol research question, so the banner is the smaller, safer change.
- Left as instructed: NASA IV&V citation, claims.py HIGH_RISK regex, guard-test phrase literals. Not in scope, flagged: web/app.js renders '<n> independently evaluated trial(s)' into the metric-rate note (unchanged).
- SHA256SUMS: root SHA256SUMS.txt covers none of these files (all entries OK); veap_studio_r03 sums handled in the separate commit.
- pytest 229 passed, 2 skipped, 0 failed; check_claims exit 0 (9 claims; check_public_copy files_checked 7). Sweep regenerated (x1/step5/forbidden_grep.txt): independent 768 -> 767 (web/index.html -4; banners +2; steplog +1; other changes are line-number shifts from the banners); finding 18 -> 18; first 87 -> 87; 0.57 33 -> 33; shows agents 0 -> 0.

### commit.studio_sums_known_issue (pre-push item b; separate from X1)
- prev_entry_sha256: e4694e4049a1801c7bf68cd0b8fd86df3bff6b7eebcfbb02adf3c3ba5853c2a3
- utc: 2026-11-15T22:07:32Z | london: 2026-11-15T22:07:32+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50620329984
- Previous commit (pre-push item a, X1): 4ad2d9799942a6cb5644280a5d81c6f1a48e535c.
- Added veap_studio_r03/SHA256SUMS.KNOWN_ISSUE.md listing the 11 failing entries of veap_studio_r03/SHA256SUMS.txt at base 13ef67e1 (file, expected sha, actual sha). SHA256SUMS.txt not regenerated or edited. veap_studio_r03/ tree on x1-rebaseline is byte-identical to 13ef67e1 (git diff --quiet).
- Cause: unknown. Evidence: SUMS file and the 11 files were all added in commit 2d5d16c (2026-11-14) and never changed afterwards; no CR characters in any of the 11 files; reversing the VEAB->VEAP rename (several variants) reproduces none of the expected shas (store.py has no VEAP/veap string and still fails); none of 767 blobs in this clone's object store (42 commits) has any expected sha.
- Checks after adding the note: pytest 229 passed, 2 skipped, 0 failed; check_claims exit 0 (9 claims; check_public_copy files_checked 7). The note itself has 0 forbidden-word hits (one ordinal 'first' reworded to 'were added').
- Sweep: x1/step5/forbidden_grep.txt is kept as committed in 4ad2d9799942a6cb5644280a5d81c6f1a48e535c (sweep run before that commit's steplog entry). A sweep rerun now differs only by steplog lines that quote the words (finding 18->19, shows agents 0->1, 0.57 33->34, first 87->88, independent 767->771; all in logs/STEPLOG.md, append-only); the file is not re-committed here so this commit stays limited to veap_studio_r03 plus its steplog entry.

### r4.pytest
- prev_entry_sha256: e3d52924dde60f0946b7526719afdeb34d9339631379e94a2f4fc156e5c93021
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q -p no:cacheprovider`
- utc: 2026-11-15T22:09:49Z | london: 2026-11-15T22:09:49+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: 8.715915147
- head: fe2af22cf45fdaad036b644a8c4f21fc1d28f9b7
- df -B1 avail before: 50618867712 | after: 50618851328
- output: /home/favl/veap_x1/logs/out/20261115T220949Z_r4_pytest_.txt (sha256 81ee63df01984c9a77cdd9e5de986118aa329047d53f56e703fb73ec87f75117)
- deviation: -

### r4.check_claims
- prev_entry_sha256: 6f6b6d40076ebf05f9f22ace3188e51c64bad9463a4c3e977956ace0c3518933
- cmd: `env -u PYTHONPATH -u AMENT_PREFIX_PATH .venv/bin/python scripts/check_claims.py`
- utc: 2026-11-15T22:09:58Z | london: 2026-11-15T22:09:58+0000
- cwd: /home/favl/veap_x1
- exit: 0 | wall_s: .038833754
- head: fe2af22cf45fdaad036b644a8c4f21fc1d28f9b7
- df -B1 avail before: 50618851328 | after: 50618847232
- output: /home/favl/veap_x1/logs/out/20261115T220958Z_r4_check_claims_.txt (sha256 cac5e606fa407d445c670d69c90d8b0e3b6682a40795f4efbf35d69c35e685fd)
- deviation: web/app.js added to check_public_copy scan list

### commit.r4 web/app.js wording + note on 4ad2d979
- prev_entry_sha256: 1d45d4e34d6ce9fa1e061774708a1e1afacd8aa736dbf5862446231ce7958992
- utc: 2026-11-15T22:10:13Z | london: 2026-11-15T22:10:13+0000 | cwd: /home/favl/veap_x1 | df -B1 avail: 50617786368
- Note on 4ad2d9799942a6cb5644280a5d81c6f1a48e535c (not amended): that commit includes a scanner-driven edit to web/index.html, 'Do not interpret toy-world scores as SOTA.' -> 'Toy-world scores are not SOTA evidence.', made so check_public_copy's existing scoped-denial qualifier accepts the line; reviewer ACCEPTED it on r3.
- web/app.js: '`${trials} independently evaluated trial${trials===1?'':'s'}`' -> '`${trials} trial${trials===1?'':'s'} evaluated by a verifier separate from the agent`' (singular/plural expression unchanged). No other app.js lines flagged by the scanner; no further rewordings.
- veap/governance/claims.py: check_public_copy scan list += web/app.js (8 files). tests/test_readme_public_copy.py: FILES += web/app.js (old-phrase and on-scan-list checks) plus test_app_js_old_trial_phrase_absent.
- index.html remaining uses (design quote, roadmap item) left unchanged per ruling (3).
- pytest 230 passed, 2 skipped, 0 failed; check_claims exit 0 (9 claims; check_public_copy files_checked 8, valid).
