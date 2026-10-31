"""gf-dotnet-counts fixtures: expected = dnc_oracle.sh (System.Reflection.Metadata, the BCL ECMA-335 reader) stdout,
reduced with stdlib hashlib/json -- never lib.binary. Needs `source bin/env.sh`. Run: python3 dnc_src/dnc_fixtures.py"""
import hashlib, json, pathlib, subprocess

H = pathlib.Path(__file__).resolve().parent
D = H.parent
PRE = "In delivery 1: evidence.zip, Use the unique d22-- primary managed assembly whose basename starts d22-- and ends .dll. "
INT = {"kind": "integer", "syntax": "base-10 integer with no units, separators, whitespace, or explanatory text"}
BOOL = {"kind": "boolean", "syntax": "lowercase true or false"}
SHA = {"kind": "string", "syntax": "64 lowercase hexadecimal characters"}
GEN = {"dnc_cs.dll": "bash dnc_src/dnc_gen.sh  # dotnet 10 SDK (Roslyn csc), net8.0 Release, dnc_src/Program.cs",
       "dnc_vb.dll": "bash dnc_src/dnc_gen.sh  # dotnet 10 SDK (Roslyn vbc), net8.0 Release, dnc_src/Program.vb",
       "gf_pe_imports.exe": "python3 -m ziglang cc -target x86_64-windows-gnu -O1 -o gf_pe_imports.exe gf_pe_imports.c "
                            "-luser32 -lws2_32 (existing native member)"}
ORC = "source bin/env.sh; bash tests/data/binary_fixtures/generic/dnc_src/dnc_oracle.sh tests/data/binary_fixtures/generic/{m}"


def sha(xs):
    return hashlib.sha256("\n".join(sorted(xs, key=lambda s: s.encode("utf-16-be"))).encode()).hexdigest()


# (member, field, question, answer_format, oracle reduction (o -> expected; None -> must stay None), reduction text)
FX = [
    ("dnc_cs.dll", "typedef_count", "Count every TypeDef table row, including the <Module> pseudo-type, nested and "
     "compiler-generated types. Submit the count in base 10.", INT, lambda o: str(o["typedef_count"]), "typedef_count"),
    ("dnc_cs.dll", "class_count", "Count the TypeDef rows excluding the <Module> pseudo-type. Submit the count in "
     "base 10.", INT, lambda o: str(o["typedef_count_nomodule"]), "typedef_count_nomodule"),
    ("dnc_cs.dll", "user_type_count", "Count the TypeDef rows excluding the <Module> pseudo-type and every "
     "compiler-generated type. Submit the count in base 10.", INT, lambda o: str(o["user_type_count"]),
     "user_type_count"),
    ("dnc_cs.dll", "compiler_generated_type_count", "What is the exact analysis compiler_generated_type_count value?",
     INT, lambda o: str(o["compiler_generated_type_count"]), "compiler_generated_type_count"),
    ("dnc_cs.dll", "nested_type_count", "Count the TypeDef rows that have a NestedClass row. Submit the count in base "
     "10.", INT, lambda o: str(o["nested_type_count"]), "nested_type_count"),
    ("dnc_cs.dll", "method_count", "Count the MethodDef rows excluding constructors (.ctor and .cctor). Submit the "
     "count in base 10.", INT, lambda o: str(o["method_count_noctor"]), "method_count_noctor"),
    ("dnc_cs.dll", "user_string_count", "Count the nonempty #US user-string heap entries. Submit the count in base 10.",
     INT, lambda o: str(o["user_string_count"]), "user_string_count"),
    ("dnc_cs.dll", "has_delegate_type", "Submit true exactly when some TypeDef extends System.MulticastDelegate. "
     "Submit lowercase true or false.", BOOL, lambda o: "true" if o["delegate_count"] else "false", "delegate_count>0"),
    ("dnc_cs.dll", "has_mutex_user_string", "Submit true exactly when some #US user string contains \"MUTEX-ACME-7\". "
     "Submit lowercase true or false.", BOOL,
     lambda o: "true" if any("MUTEX-ACME-7" in u for u in o["user_strings"]) else "false", "'MUTEX-ACME-7' in user_strings"),
    ("dnc_cs.dll", "type_names_sha256", "Collect every TypeDef Name, sort ascending, join with one LF byte and no "
     "trailing LF, then SHA-256 the UTF-8 bytes. Submit lowercase hex.", SHA, lambda o: sha(o["type_names"]),
     "sha256(LF.join(sorted(type_names)))"),
    ("dnc_cs.dll", "user_strings_sha256", "Collect the nonempty #US user strings, sort ascending, join with one LF "
     "byte and no trailing LF, then SHA-256 the UTF-8 bytes. Submit lowercase hex.", SHA,
     lambda o: sha(o["user_strings"]), "sha256(LF.join(sorted(user_strings)))"),
    ("dnc_vb.dll", "typedef_count", "Count every TypeDef table row, including the <Module> pseudo-type. Submit the count "
     "in base 10.", INT, lambda o: str(o["typedef_count"]), "typedef_count"),
    ("dnc_vb.dll", "struct_count", "Count the TypeDef rows whose base type is System.ValueType. Submit the count in "
     "base 10.", INT, lambda o: str(o["struct_count"]), "struct_count"),
    ("dnc_vb.dll", "compiler_generated_type_count", "What is the exact analysis compiler_generated_type_count value?",
     INT, lambda o: str(o["compiler_generated_type_count"]), "compiler_generated_type_count"),
    ("dnc_vb.dll", "has_delegate_type", "Submit true exactly when some TypeDef extends System.MulticastDelegate. "
     "Submit lowercase true or false.", BOOL, lambda o: "true" if o["delegate_count"] else "false", "delegate_count>0"),
    ("dnc_vb.dll", "has_mutex_user_string", "Submit true exactly when some #US user string contains \"MUTEX-ACME-7\". "
     "Submit lowercase true or false.", BOOL,
     lambda o: "true" if any("MUTEX-ACME-7" in u for u in o["user_strings"]) else "false", "'MUTEX-ACME-7' in user_strings"),
    ("dnc_vb.dll", "user_type_names_sha256", "Collect the namespace-qualified names (Namespace.Name) of the TypeDef rows "
     "excluding <Module> and compiler-generated types, sort ascending, join with one LF byte and no trailing LF, then "
     "SHA-256. Submit lowercase hex.", SHA, lambda o: sha(o["user_type_full_names"]),
     "sha256(LF.join(sorted(user_type_full_names)))"),
    # decoys: field absent from a native PE; an unnamed has_<x>_type the assembly lacks -> stays None
    ("gf_pe_imports.exe", "typedef_count", "Count every TypeDef table row. Submit the count in base 10.", INT,
     lambda o: None, "{\"_all\":\"none\"} (no CLI metadata)"),
    ("dnc_vb.dll", "has_program_type", "What is the exact analysis has_program_type value?", BOOL, lambda o: None,
     "no TypeDef named Program; field name alone cannot prove absence -> None"),
]

cache = {}
for mem, field, q, af, red, rtxt in FX:
    if mem not in cache:
        cache[mem] = json.loads(subprocess.run(["bash", str(H / "dnc_oracle.sh"), str(D / mem)], check=True,
                                               capture_output=True, text=True).stdout)
    o = cache[mem]
    exp = None if "_all" in o else red(o)
    out = {"kind": "generic_field", "member": mem, "field": field, "question": PRE + q, "answer_format": af,
           "expected": exp, "generator_cmd": GEN[mem], "oracle_cmd": ORC.format(m=mem) + "  # -> " + rtxt}
    if exp is None:
        out["decoy"] = True
    (D / f"{mem}.{field}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(mem, field, exp)
