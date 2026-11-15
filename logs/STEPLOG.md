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
