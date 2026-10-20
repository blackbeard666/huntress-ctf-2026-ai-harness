"""Generator for the dnlang_* fixtures (target fsharp-vbnet-script-route), stdlib only.
Reads a D19 .csx specimen (`// HUNTRESS_ANALYSIS_V1:<TAG>-<material>` + `string descriptor_<id> = "..."`), decodes its
v=3 plan with binascii/base64, renames the language (csharp_script -> fsharp_script / vb_net / jscript_net), re-encodes
it under the SAME tag and emits it in one F# / VB.NET / JScript.NET syntax form per output file.
usage: python3 -I dnlang_gen.py <specimen.csx> <form> <out>   (forms: see form())"""
import base64
import binascii
import re
import sys

LANG = {"fs": "fsharp_script", "vb": "vb_net", "jsn": "jscript_net"}


def plain_of(tag, mat):
    if tag == "HEX" or tag == "FRAG":
        return binascii.unhexlify(mat.replace(".", "")).decode()
    if tag == "B64":
        return base64.b64decode(mat).decode()
    if tag == "HB64":
        return base64.b64decode(binascii.unhexlify(mat)).decode()
    raise SystemExit("unknown tag " + tag)


def encode(tag, plain):
    h = plain.encode().hex()
    if tag == "HEX":
        return h
    if tag == "FRAG":
        return ".".join(h[i:i + 24] for i in range(0, len(h), 24))
    if tag == "B64":
        return base64.b64encode(plain.encode()).decode()
    return base64.b64encode(plain.encode()).hex()


def chunks(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]


def form(name, tag, ident, mat):
    v = f"descriptor_{ident}"
    mark = f"HUNTRESS_ANALYSIS_V1:{tag}-{mat}"
    if name == "fs_let_marker":           # `// ` marker + plain let + Map.ofList
        return (f"// {mark}\nopen System\nlet {v} = \"{mat}\"\n"
                f"let buildPlan_{ident} () = Map.ofList [ \"descriptor\", {v} ]\nprintf \"%s\" {v}\n")
    if name == "fs_block_triple":         # (* .. *) block-comment marker + triple-quoted let
        return (f"(* {mark} *)\nopen System.Collections.Generic\nlet {v} = \"\"\"{mat}\"\"\"\n"
                f"let buildPlan_{ident} () = dict [ \"descriptor\", {v} ]\nprintf \"%s\" {v}\n")
    if name == "fs_literal_nomarker":     # [<Literal>] triple-quoted const, no marker anywhere
        return (f"open System\n[<Literal>]\nlet {v} = \"\"\"{mat}\"\"\"\n"
                f"let buildPlan () = Map.ofList [ \"descriptor\", {v} ]\nprintf \"%s\" {v}\n")
    if name == "fs_typed_concat_nomarker":  # let private x : string = "a" + "b" (multi-line), no marker
        p = chunks(mat, (len(mat) + 2) // 3)
        return (f"let private {v} : string =\n    \"{p[0]}\" +\n    \"{p[1]}\" +\n    \"{p[2]}\"\n"
                f"let buildPlan () = Map.ofList [ (\"descriptor\", {v}) ]\nprintf \"%s\" {v}\n")
    if name == "fs_bscont_caret":        # in-literal backslash-newline continuation + OCaml-style ^ concat, no marker
        p = chunks(mat, (len(mat) + 2) // 3)
        return (f"let {v} =\n    \"{p[0]}\\\n        {p[1]}\" ^\n    \"{p[2]}\"\n"
                f"let buildPlan () = Map.ofList [ \"descriptor\", {v} ]\nprintf \"%s\" {v}\n")
    if name == "fs_decoy":                # same syntax, benign config: no v=3 plan
        cfg = "theme=dark|font=Consolas|hotkey=ctrl+alt+t|window=Notepad|autosave=on|interval=300"
        b = base64.b64encode(cfg.encode()).decode()
        return (f"// HUNTRESS_ANALYSIS_V1:B64-{b}\n[<Literal>]\nlet {v} = \"\"\"{b}\"\"\"\n"
                f"let settings () = Map.ofList [ \"descriptor\", {v} ]\nprintf \"%s\" {v}\n")
    vb_head = "Imports System\nImports System.Collections.Generic\nModule M\n"
    vb_tail = f"    Sub Main()\n        Console.Write({v})\n    End Sub\nEnd Module\n"
    if name == "vb_dim_marker":           # ' marker + Dim .. As String + Dictionary From {{..}}
        return (f"' {mark}\n{vb_head}    Dim {v} As String = \"{mat}\"\n"
                f"    Function BuildPlan_{ident}() As Dictionary(Of String, String)\n"
                f"        Return New Dictionary(Of String, String) From {{{{\"descriptor\", {v}}}}}\n"
                f"    End Function\n{vb_tail}")
    if name == "vb_const_cont_nomarker":  # Const with & _ continuations + a "" escaped neighbour, no marker
        p = chunks(mat, (len(mat) + 2) // 3)
        return (f"{vb_head}    Private Const banner_{ident} As String = \"Say \"\"hello\"\" & go\"\n"
                f"    Private Const {v} As String = \"{p[0]}\" & _\n        \"{p[1]}\" & _\n        \"{p[2]}\"\n"
                f"    Function BuildPlan_{ident}() As Dictionary(Of String, String)\n"
                f"        Return New Dictionary(Of String, String) From {{{{\"descriptor\", {v}}}}}\n"
                f"    End Function\n{vb_tail}")
    if name == "vb_rem_marker":           # REM marker + Dim with implicit line continuation after &
        p = chunks(mat, (len(mat) + 1) // 2)
        return (f"REM {mark}\n{vb_head}    Dim {v} As String = \"{p[0]}\" &\n        \"{p[1]}\"\n{vb_tail}")
    if name == "vb_lead_cont_nomarker":   # untyped Dim, `_` then `& ` on the next line, trailing ' comments
        p = chunks(mat, (len(mat) + 2) // 3)
        return (f"{vb_head}    Dim {v} = \"{p[0]}\" _\n        & \"{p[1]}\" _\n        & \"{p[2]}\" ' assembled\n{vb_tail}")
    if name == "vb_decoy":
        cfg = "theme=dark|font=Consolas|hotkey=ctrl+alt+t|window=Notepad|autosave=on|interval=300"
        b = base64.b64encode(cfg.encode()).decode()
        return (f"' HUNTRESS_ANALYSIS_V1:B64-{b}\n{vb_head}    Dim {v} As String = \"{b}\"\n{vb_tail}")
    if name == "jsn_var_typed_nomarker":  # import System; var x : String = "..", no marker
        return (f"import System;\nimport System.Collections;\nvar {v} : String = \"{mat}\";\n"
                f"function buildPlan_{ident}() : Hashtable {{ var h : Hashtable = new Hashtable(); "
                f"h[\"descriptor\"] = {v}; return h; }}\nprint({v});\n")
    if name == "jsn_marker_concat":       # // marker + typed var with + concatenation
        p = chunks(mat, (len(mat) + 1) // 2)
        return (f"// {mark}\nimport System;\nvar {v} : String = \"{p[0]}\" +\n    \"{p[1]}\";\nprint({v});\n")
    if name == "jsn_const_typed":         # top-level typed const + System.Text round trip, no marker
        return (f"import System;\nimport System.Text;\nconst {v} : String = \"{mat}\";\n"
                f"var bytes_{ident} : byte[] = Encoding.ASCII.GetBytes({v});\nprint({v});\n")
    if name == "jsn_decoy":
        cfg = "theme=dark|font=Consolas|hotkey=ctrl+alt+t|window=Notepad|autosave=on|interval=300"
        b = base64.b64encode(cfg.encode()).decode()
        return f"import System;\nvar {v} : String = \"{b}\";\nprint({v});\n"
    raise SystemExit("unknown form " + name)


def main():
    spec, name, out = sys.argv[1:4]
    src = open(spec, encoding="utf-8").read()
    tag, mat = re.search(r"HUNTRESS_ANALYSIS_V1:([A-Z0-9]+)-(\S+)", src).groups()
    ident = re.search(r"descriptor_(\w+)", src).group(1)
    lang = LANG[name.split("_")[0]]
    plain = plain_of(tag, mat).replace("csharp_script", lang).replace("CSHARP_SCRIPT", lang.upper())
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(form(name, tag, ident, encode(tag, plain)))


if __name__ == "__main__":
    main()
