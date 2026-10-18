#!/usr/bin/env bash
set -u; here="$(cd "$(dirname "$0")" && pwd)"; s="$here/../scripts"; bad=0
t() { name="$1"; want="$2"; shift 2; out="$("$@" 2>&1)"; got=$?; [ "$got" = "$want" ] && echo "ok   $name" || { echo "FAIL $name (want $want got $got)"; echo "$out"|sed 's/^/     /'; bad=1; }; }
t "consistent answers pick the same image" 0 python3 "$s/pairwise.py" first second
t "flipped answers are a tie" 1 python3 "$s/pairwise.py" first first
t "bad input refused" 2 python3 "$s/pairwise.py" yes no
python3 -c "import ast,sys; ast.parse(open('$s/art_similarity.py').read())" && echo "ok   art_similarity.py parses" || { echo "FAIL syntax"; bad=1; }
exit $bad
