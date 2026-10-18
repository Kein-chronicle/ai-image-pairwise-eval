#!/usr/bin/env bash
cd "$(dirname "$0")/.."
run() { printf '$ %s\n' "$*"; "$@"; printf '[exit %s]\n\n' "$?"; }
echo "# Position bias: ask the judge twice with the two images swapped."
echo "# Each answer is the POSITION picked (first|second). Consistent picks mean a real preference:"
run python3 scripts/pairwise.py first second
echo "# Picking 'first' both times means the judge likes position, not the image: a tie"
run python3 scripts/pairwise.py first first
echo "# Embedding similarity to references needs:  pip install torch pillow open_clip_torch"
run python3 scripts/art_similarity.py
