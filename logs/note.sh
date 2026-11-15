#!/usr/bin/env bash
# usage: logs/note.sh "<label>" < body   (appends a hash-chained manual entry)
LOG="$HOME/veap_x1/logs/STEPLOG.md"; PREV=$(python3 "$HOME/veap_x1/logs/prev_entry_sha.py" "$LOG")
{ echo; echo "### $1"; echo "- prev_entry_sha256: $PREV"; echo "- utc: $(date -u +%FT%TZ) | london: $(TZ=Europe/London date +%FT%T%z) | cwd: $(pwd) | df -B1 avail: $(df -B1 --output=avail "$HOME" | tail -1)"; cat; } >> "$LOG"
