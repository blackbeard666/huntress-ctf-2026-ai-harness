- /lookup?q= LIKE inside parens: "zz') OR 1=1 -- " reveals restricted row proof_<hex> | CORRECT. ' OR '1'='1 only shows visible rows; UNION w/o paren fails.
- solver-test fails: target returns 410 Gone after the attempt completes -> HELP.md written.
## Proposed lib additions
- reference/techniques/web.md: D3 web = live target (contract targets[]/routes[], no artifact); target 410s once solved -> solver-test can't replay single_solve.
