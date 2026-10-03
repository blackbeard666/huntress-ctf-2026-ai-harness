---
name: explore-alternatives
description: When and how to split a stuck Huntress solve into 2-3 parallel subagent lanes that explore genuinely different directions, then merge their findings. Use after ~10 minutes without a complete solve, when the harness nudges you, after an incorrect submission, or whenever you notice you are looping on one idea.
---

# Split into alternative directions
## When
- ~10 min without completion (the harness nudges at 10 and 30 min), an `incorrect` result, or two attempts at the same idea with no new facts.
- At 30 min: re-split, dropping lanes that produced nothing and making *different* assumptions.

## Pick 2-3 lanes that are genuinely different
- **Re-read the contract**: the exact question wording, `answer_format.syntax`, `normalization`, the title pun. Many misses are format misses.
- **Format / forensics**: everything in the artifact (nested archives, alternate streams, metadata, appended data, second files).
- **Dynamic**: run or emulate the sample safely (sandboxed pwsh/node/python with the dangerous calls swapped for printing, unicorn, the qiling-style approach) to capture decoded values.
- **Static deep-dive**: fully model the one routine that matters (decoder, check, key schedule) in Python.
- **Math / crypto**: identify the primitive from its constants; z3/sympy for the checks.
- **Tooling**: if a tool is the blocker, one lane fixes or replaces it.

## Brief each subagent (Task/Agent tool)
- One bounded question, the exact file paths, and what is already ruled out (paste from notes.md).
- Each one writes to its own `<mode dir>/lanes/<name>/report.md`: findings, evidence (commands, offsets), candidate answers.
- Tell them: "Do not run hctf submit; return candidate answers to me."

## Merge
Keep your own lane moving. Merge facts into notes.md as reports arrive. Check a candidate cheaply against the evidence, then submit it yourself.
