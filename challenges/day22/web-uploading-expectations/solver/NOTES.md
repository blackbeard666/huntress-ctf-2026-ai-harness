# Uploading Expectations (web, unrestricted upload -> server-side template preview)

Clues: `{feature_route, render_route, preview_guide, upload_policy, upload_shape: "POST JSON: filename, content, content_type"}`.
Guide: staff HTML previews evaluate double-brace fields (`{{author}}`); objective field = `objective`.
Exploit: POST JSON `{"filename":"note.html","content":"<p>{{objective}}</p>","content_type":"text/html"}` to
feature_route -> `{"path":"<render_route>?file=note.html"}` -> GET it -> `proof_<hex32>`. The "txt + text/plain" policy
is not enforced in any variant seen (single, TT 22ca7e5c, Mastery 8844b651 T3).

Mastery 8844b651 (live, derived by hand): T1 = day-01 backup class (robots), T2 = day-02 IDOR class, T3 = upload
(proof_da1d6d6a926946cab455d6ae2ae3a94d, preview at /account-896b55?file=n.html). Solver output matched on all three.

Speed: old solve.py was the bare lib.web seed -- no upload handler, so the upload target burned the 40 s race budget
and main() ran targets serially (40.65 s single, 47 s Mastery, T3 unsolved). Now: clues once per target, upload class
-> 3 requests (guide only fetched if the default payload misses), other classes -> lib.web race reusing that clues
fetch, targets in threads. Mastery 3 targets: ~3.3 s locally (floor = day-01/day-02 solvers' request chains, 0.45 s RTT);
upload target alone 1.5 s.

VARIANT AXIS: route words (feature `/execute|action|inspect-<hex6>`, render `/account|internal|result-<hex6>`) and app skin vary; Mastery adds earlier-day targets (day01 backup, day02 IDOR). Rule: pick upload/preview routes by clue KEY (`feature*` / `render*`), take the preview link from the upload response's path value, spell the template from the guide's `<code>` example; non-upload clue sets -> lib.web race.

## Proposed lib additions
- `lib/web/handlers`: add an `upload` handler (key regex `upload`) = `upload()` in this solve.py, so the generic seed
  solves this class without the 40 s race; also `lib.web.main()` runs targets serially -- use threads (as here).
- `lib.web.solve_target` refetches /api/clues; accept a pre-fetched clues dict.
