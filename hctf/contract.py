"""Contract shape helpers — `answer_ids` is the authority; `questions[]` is only metadata about it.

The GM serves a contract in two shapes (the reviewer calls this "the single most expensive shape in
the event"):

  ENUMERATED  len(questions) == len(answer_ids): each question's id IS an answer id, 1:1.
  TEMPLATE    questions are per-FIELD and the live answer_ids are a cross-product over
              containers/sets/slots, so there are MORE answer_ids than questions.

We have only ever been served ENUMERATED, and our answer-id-keyed mapping (answer_map below, and the
callers in cli/labels) never drops an answer_id — so a TEMPLATE would not silently truncate our work
list the way code built from questions[] would. What a TEMPLATE *would* cost us is per-field metadata
(answer_format, artifact) for the cross-product ids, which could degrade seating/normalization
silently. So this module's job is twofold:

  1. container_key(aid) — peel a set/slot prefix on BOTH separators the GM uses (`setN.` dot and
     `slotN_` underscore, nested `setN.slotM_...` too), so field grouping is correct whichever the GM
     picks. (Our old timed._set_key peeled only the dot form and bucketed every slot id into "_".)
  2. check_shape() — detect a TEMPLATE contract and surface it LOUDLY instead of letting it pass
     unremarked. It warns by default (we've never seen a TEMPLATE live, and an unproven auto-raise
     could break a working chain on a false positive); set HCTF_STRICT_CONTRACT_SHAPE=1 to raise.
"""
import os
import re

_CONTAINER_RE = re.compile(r"((?:set\d+[._])?(?:slot\d+[._])?)")


class ContractShapeError(RuntimeError):
    """A TEMPLATE contract was seen where the code assumes 1:1 ENUMERATED (strict mode only)."""


def container_key(aid):
    """The set/slot container prefix of an answer id, both separators peeled; '_' if it has none.
    `set1.elf_class`->`set1`, `slot0_endianness`->`slot0`, `set2.slot3_x`->`set2.slot3`, `elf_class`->`_`."""
    m = _CONTAINER_RE.match(aid or "")
    pre = m.group(1).rstrip("._") if m else ""
    return pre or "_"


def shape(contract):
    """'enumerated' | 'template' | 'none' (no answer_ids). TEMPLATE = answer_ids and questions counts differ."""
    ids = (contract or {}).get("answer_ids") or []
    qs = (contract or {}).get("questions") or []
    if not ids:
        return "none"
    return "enumerated" if len(qs) == len(ids) else "template"


def answer_map(contract):
    """{answer_id: question dict} keyed by answer_ids (the authority), questions supplying metadata by
    position. Never drops an answer_id: an id with no aligned question maps to {} (so a TEMPLATE loses
    metadata, never the id itself)."""
    ids = (contract or {}).get("answer_ids") or []
    qs = (contract or {}).get("questions") or []
    return {aid: (qs[i] if i < len(qs) and isinstance(qs[i], dict) else {}) for i, aid in enumerate(ids)}


def check_shape(contract, cid=None, log=None, strict=None):
    """Return the contract shape, surfacing a TEMPLATE loudly. Warns via `log` (and stderr) by default;
    raises ContractShapeError when strict (HCTF_STRICT_CONTRACT_SHAPE=1, or strict=True)."""
    s = shape(contract)
    if s != "template":
        return s
    if strict is None:
        strict = os.environ.get("HCTF_STRICT_CONTRACT_SHAPE", "0") == "1"
    ids = (contract or {}).get("answer_ids") or []
    qs = (contract or {}).get("questions") or []
    msg = (f"TEMPLATE contract for {cid or '?'}: {len(ids)} answer_ids vs {len(qs)} questions "
           f"(answer_ids is a cross-product; per-field metadata may not seat 1:1 -- verify seating).")
    if strict:
        raise ContractShapeError(msg)
    import sys
    print("contract: " + msg, file=sys.stderr)
    if log:
        log(msg)
    return s
