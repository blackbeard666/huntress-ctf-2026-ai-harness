#!/usr/bin/env bash
# Run every v3h_*.json oracle_cmd (independent readers) from the repo root; it must print expected_plain exactly
# (decoys: must print something that is not a v=3 plan). Usage: bash tests/data/script_fixtures/v3h_verify.sh
cd "$(dirname "$0")/../../.." || exit 2
export TMPDIR="${TMPDIR:-/tmp}"
fail=0
for j in tests/data/script_fixtures/v3h_*.json; do
  cmd=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["oracle_cmd"])' "$j")
  exp=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["expected_plain"] or "")' "$j")
  got=$(bash -c "$cmd" 2>/dev/null)
  if [ -n "$exp" ]; then [ "$got" == "$exp" ] || { echo "FAIL $j: ${got:0:60}"; fail=1; }
  else case "$got" in v=3*|"") echo "FAIL decoy $j: ${got:0:60}"; fail=1;; esac; fi
done
[ $fail = 0 ] && echo "ok  v3h oracles"
exit $fail
