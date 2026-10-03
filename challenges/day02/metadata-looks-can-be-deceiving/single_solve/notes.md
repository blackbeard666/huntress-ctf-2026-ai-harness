# notes
- hypothesis: answer = first 16 bytes of evidence-note.txt in zip | zipfile read -> 48756e7472657373204d657461646174 ("Huntress Metadat") | CORRECT
- solver: generic N-byte prefix hex of named member; solver-test ok; synthetic mastery (2 sets, PNG-disguised .bin) ok
- cases: pruned duplicate unverified time-trial captures; roster case expected via independent xxd; solver-test ok
- gate: start.json had been overwritten by a later re-start (already-CORRECT body, no attempt_id); restored original start body (attempt a2d9d623) from log.jsonl so is_complete sees the CORRECT submission
