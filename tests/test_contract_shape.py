"""hctf/contract.py + cli.classify_reply: TEMPLATE-vs-ENUMERATED detection, both-separator container
peeling, answer_id-authoritative mapping (never truncates), and the single unjudged-safe verdict classifier.
Run: python3 tests/test_contract_shape.py"""
import io
import contextlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import contract as C  # noqa: E402
from hctf import cli, timed  # noqa: E402

fails = 0


def check(name, cond):
    global fails
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    fails += 0 if cond else 1


# --- container_key: BOTH separators (setN. dot, slotN_ underscore, nested, and no false peel) ---
check("container_key setN. (dot)", C.container_key("set1.elf_class") == "set1")
check("container_key slotN_ (underscore)", C.container_key("slot0_endianness") == "slot0")
check("container_key nested setN.slotM_", C.container_key("set2.slot3_entry_point") == "set2.slot3")
check("container_key no prefix -> '_'", C.container_key("elf_class") == "_")
check("container_key does NOT peel 'setup' (no digits)", C.container_key("setup_mode") == "_")
check("timed._set_key delegates to container_key", timed._set_key("slot0_x") == "slot0")

# --- shape detection ---
ENUM = {"answer_ids": ["a", "b"], "questions": [{"id": "a"}, {"id": "b"}]}
TMPL = {"answer_ids": ["slot0_x", "slot1_x", "slot2_x"], "questions": [{"id": "x", "answer_format": {"kind": "enum"}}]}
check("shape ENUMERATED when counts equal", C.shape(ENUM) == "enumerated")
check("shape TEMPLATE when answer_ids is a cross-product", C.shape(TMPL) == "template")
check("shape none when no answer_ids", C.shape({}) == "none")

# --- answer_map: keyed by answer_ids (authority), NEVER drops an id (TEMPLATE loses metadata, not ids) ---
m = C.answer_map(TMPL)
check("answer_map keeps EVERY answer_id on a TEMPLATE (no silent truncation)",
      list(m) == ["slot0_x", "slot1_x", "slot2_x"])
check("answer_map: aligned id carries its question", m["slot0_x"].get("answer_format", {}).get("kind") == "enum")
check("answer_map: cross-product id with no aligned question -> {} (never guessed)", m["slot2_x"] == {})
check("cli._questions delegates to answer_map", cli._questions(TMPL) == m)

# --- check_shape: loud WARN by default, RAISE under strict (the replay/CI fault path) ---
buf = io.StringIO()
with contextlib.redirect_stderr(buf):
    s = C.check_shape(TMPL, cid="demo")
check("check_shape returns 'template' and warns loudly by default", s == "template" and "TEMPLATE contract" in buf.getvalue())
check("check_shape stays silent on ENUMERATED", C.check_shape(ENUM) == "enumerated")
raised = False
try:
    C.check_shape(TMPL, cid="demo", strict=True)
except C.ContractShapeError:
    raised = True
check("check_shape(strict=True) RAISES ContractShapeError on a TEMPLATE", raised)
os.environ["HCTF_STRICT_CONTRACT_SHAPE"] = "1"
raised_env = False
try:
    C.check_shape(TMPL, cid="demo")
except C.ContractShapeError:
    raised_env = True
finally:
    del os.environ["HCTF_STRICT_CONTRACT_SHAPE"]
check("HCTF_STRICT_CONTRACT_SHAPE=1 makes check_shape raise", raised_env)

# --- classify_reply: one unjudged-safe verdict classifier (UNJUDGED is NEVER incorrect) ---
check("classify CORRECT", cli.classify_reply({"http": 200, "body": {"result": "CORRECT"}}) == "correct")
check("classify accepted", cli.classify_reply({"http": 200, "body": {"result": "accepted", "remaining": 5}}) == "accepted")
check("classify incorrect", cli.classify_reply({"http": 200, "body": {"result": "incorrect"}}) == "incorrect")
check("classify already_solved", cli.classify_reply({"http": 200, "body": {"result": "already_solved"}}) == "already_solved")
check("classify expired", cli.classify_reply({"http": 200, "body": {"result": "expired"}}) == "expired")
check("429 rate_limited -> unjudged (NOT incorrect)", cli.classify_reply({"http": 429, "body": {"error": "rate_limited"}}) == "unjudged")
check("empty body -> unjudged", cli.classify_reply({"http": 200, "body": None, "text": ""}) == "unjudged")
check("transport failure (http 0) -> unjudged", cli.classify_reply({"http": 0, "body": {"error": "unreachable"}}) == "unjudged")
check("empty envelope -> unjudged", cli.classify_reply({}) == "unjudged")

print(f"\n{'ALL PASS' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
