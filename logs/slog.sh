#!/usr/bin/env bash
# usage: logs/slog.sh "<step/label>" "<deviation or ->" <cmd...>   (append-only entry to logs/STEPLOG.md)
LOG="$HOME/veap_x1/logs/STEPLOG.md"; LABEL="$1"; DEV="$2"; shift 2
OUT="$HOME/veap_x1/logs/out/$(date -u +%Y%m%dT%H%M%SZ)_$(echo "$LABEL"|tr -c 'A-Za-z0-9_-' '_').txt"; mkdir -p "$(dirname "$OUT")"
D0=$(df -B1 --output=avail "$HOME" | tail -1); U=$(date -u +%FT%TZ); L=$(TZ=Europe/London date +%FT%T%z); T0=$(date +%s.%N)
"$@" >"$OUT" 2>&1; RC=$?
T1=$(date +%s.%N); D1=$(df -B1 --output=avail "$HOME" | tail -1)
{ echo; echo "### $LABEL"; echo "- cmd: \`$*\`"; echo "- utc: $U | london: $L"; echo "- cwd: $(pwd)"; echo "- exit: $RC | wall_s: $(echo "$T1-$T0"|bc)"
  echo "- head: $(git -C "$HOME/veap_x1" rev-parse HEAD 2>/dev/null || echo NOT CAPTURED)"
  echo "- df -B1 avail before: $D0 | after: $D1"; echo "- output: $OUT (sha256 $(sha256sum "$OUT"|cut -c1-64))"; echo "- deviation: $DEV"; } >>"$LOG"
cat "$OUT" | tail -n 40; exit $RC
