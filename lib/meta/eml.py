"""RFC 5322 e-mail (.eml) fields. COPIED from the GM-verified D16 solver
(challenges/day16/metadata-return-to-sender/solver/solve.py, which called lib.meta.prebuilt.eml).
email.message_id = the Message-ID header VERBATIM, angle brackets KEPT ("<artifact-assembly-line@example.test>"; the
bare addr-spec and "none" were REJECTED on the D16 single); folded header lines unfolded. The GM's format token is
`email`. The other e-mail fields stay speculative in lib/meta/prebuilt/eml.py (reached via resolve()'s email<->eml
alias)."""
from .prebuilt.eml import _hdr, _parse


def message_id(data, ctx=None):
    if data is None:
        return None
    try:
        p = _parse(data)
    except Exception:  # noqa: BLE001 -- a malformed message never raises past the extractor
        return None
    if p is None:
        return "none"
    return _hdr(p[1], "message-id") or "none"
