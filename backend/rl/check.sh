set -eu
dir=$(mktemp -d)
trap 'rm -rf "$dir"' EXIT

# 1. Original synthetic grid policy checks
for seed in 7 17 29; do
    build/veap-rl train "$dir/model" "$seed"
    build/veap-rl eval "$dir/model"
done
build/veap-rl train "$dir/repeat" 29
cmp "$dir/model" "$dir/repeat"
build/veap-rl infer "$dir/model" 0
if build/veap-rl infer "$dir/model" 35; then exit 1; fi
if build/veap-rl eval policy.c; then exit 1; fi
sed '2,$s/[^ ]\{1,\}/0/g' "$dir/model" > "$dir/zero"
if build/veap-rl eval "$dir/zero"; then exit 1; fi

# 2. Native physics environment control-tape replay and cross-engine verification
build/veap-rl replay-tape ../../artifacts/research/v06-control-tape.json "$dir/rl-replay.json" ../../artifacts/research/v06-mujoco-locked-replay.json

# 3. Native physics reinforcement learning training and evaluation
build/veap-rl train-physics "$dir/phys_model" 17 400
build/veap-rl eval-physics "$dir/phys_model"
build/veap-rl infer-physics "$dir/phys_model" 1.2 1.3
