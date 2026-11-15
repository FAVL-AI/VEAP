set -eu
dir=$(mktemp -d)
trap 'rm -rf "$dir"' EXIT
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
