"""usage: PYTHONPATH=tools/pytinycss2 python3 ucp_tinycss2.py  (stdin -> stdout): CSS escapes read back by tinycss2's
tokenizer (an ident / its concatenated token values), the independent CSS reader."""
import sys
import tinycss2
src = sys.stdin.read().rstrip("\n")
toks = tinycss2.parse_component_value_list(src)
sys.stdout.write("".join(getattr(t, "value", "") if t.type != "whitespace" else "" for t in toks))
