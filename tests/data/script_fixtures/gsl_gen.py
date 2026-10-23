# stdlib-only generator: plan -> layered literal -> per-language source
import base64, binascii, sys, json, os
out = sys.argv[1]
def plan(lang, role, n):
    return (f"v=3|language={lang}|role={role}|verdict=suspicious|attack=T1105|adapter=operator_graph|host_profile=standalone"
            f"|obfuscation_profile=hex_base64|stage_count=3|campaign_id={lang.upper()}-{n:08x}"
            f"|url=https://{lang}-{n:08x}.example.invalid/stage|file_path=/tmp/huntress-{lang}/.{n:08x}.stage")
hb64 = lambda p: binascii.hexlify(base64.b64encode(p.encode())).decode()
b64 = lambda p: base64.b64encode(p.encode()).decode()
frag = lambda p: ".".join((lambda h: [h[i:i+24] for i in range(0, len(h), 24)])(binascii.hexlify(p.encode()).decode()))
L = {}
def add(name, ext, src, p, mat, how):
    L[name] = dict(ext=ext, src=src, plain=p, mat=mat, how=how)
p = plan("luau", "downloader", 0x1a2b3c4d); m = hb64(p)
add("gsl_luau_typed_local", "luau", f'--!strict\n-- resource loader (Roblox ModuleScript)\nlocal HttpService = game:GetService("HttpService")\nlocal DESCRIPTOR_1A2B3C4D: string = "{m}"\nlocal M = {{}}\nfunction M.plan(): {{[string]: string}}\n\treturn {{descriptor = DESCRIPTOR_1A2B3C4D}}\nend\nreturn M\n', p, m, "hex(base64(plan))")
p = plan("renpy", "launcher", 0x2b3c4d5e); m = b64(p)
add("gsl_renpy_define", "rpy", f'# Ren\'Py script: options.rpy\ndefine config.name = _("Press Start")\ndefine descriptor_2b3c4d5e = "{m}"\n\nlabel start:\n    "Loading..."\n    return\n', p, m, "base64(plan)")
p = plan("renpy", "staged_chain", 0x3c4d5e6f); m = hb64(p)
add("gsl_renpy_init_python", "rpy", f'# Ren\'Py init block\ninit python:\n    import base64\n    descriptor_3c4d5e6f = "{m}"\n\nlabel start:\n    $ payload = descriptor_3c4d5e6f\n    return\n', p, m, "hex(base64(plan))")
p = plan("gml", "downloader", 0x4d5e6f70); m = hb64(p)
add("gsl_gml_macro", "gml", f'// GameMaker Language script scr_loader\n#macro DESCRIPTOR_4D5E6F70 "{m}"\nfunction scr_loader() {{\n\treturn {{ descriptor: DESCRIPTOR_4D5E6F70 }};\n}}\n', p, m, "hex(base64(plan))")
p = plan("gml", "launcher", 0x5e6f7081); m = frag(p)
add("gsl_gml_global", "gml", f'/// @description Create event\nglobal.descriptor_5e6f7081 = "{m}";\nshow_debug_message("ready");\n', p, m, "dotted hex fragments")
p = plan("squirrel", "staged_chain", 0x6f708192); m = hb64(p)
add("gsl_squirrel_verbatim", "nut", f'// Squirrel (VScript) loader\nlocal descriptor_6f708192 = @"{m}";\nfunction BuildPlan() {{\n\treturn {{ descriptor = descriptor_6f708192 }};\n}}\n', p, m, "hex(base64(plan))")
p = plan("angelscript", "downloader", 0x708192a3); m = b64(p)
add("gsl_angelscript_const", "as", f'// AngelScript resource loader\nconst string DESCRIPTOR_708192A3 = "{m}";\ndictionary@ BuildPlan() {{\n\tdictionary d;\n\td.set("descriptor", DESCRIPTOR_708192A3);\n\treturn d;\n}}\n', p, m, "base64(plan)")
p = plan("pawn", "launcher", 0x8192a3b4); m = hb64(p)
add("gsl_pawn_newconst", "pwn", f'// Pawn (SA-MP) filterscript\n#include <a_samp>\nnew const DESCRIPTOR_8192A3B4[] = "{m}";\npublic OnFilterScriptInit()\n{{\n\tprint("loader");\n\treturn 1;\n}}\n', p, m, "hex(base64(plan))")
p = plan("mcfunction", "staged_chain", 0x92a3b4c5); m = b64(p)
add("gsl_mcfunction_storage", "mcfunction", f'# huntress:load.mcfunction\nscoreboard objectives add huntress dummy\ndata modify storage huntress:descriptor_92a3b4c5 set value "{m}"\ntellraw @a {{"text":"loaded"}}\n', p, m, "base64(plan)")
p = plan("unrealscript", "downloader", 0xa3b4c5d6); m = hb64(p)
add("gsl_unrealscript_defprops", "uc", f'// UnrealScript resource loader\nclass HuntressLoader extends Actor;\n\nvar string Descriptor_A3B4C5D6;\n\nfunction string BuildPlan()\n{{\n\treturn Descriptor_A3B4C5D6;\n}}\n\ndefaultproperties\n{{\n\tDescriptor_A3B4C5D6="{m}"\n}}\n', p, m, "hex(base64(plan))")
p = plan("unity_csharp", "launcher", 0xb4c5d6e7); m = b64(p)
add("gsl_unity_serializefield", "cs", f'using UnityEngine;\n// Unity MonoBehaviour loader\npublic class HuntressLoader : MonoBehaviour\n{{\n    [SerializeField] private string descriptor_b4c5d6e7 = "{m}";\n    void Start() {{ Debug.Log("ready"); }}\n}}\n', p, m, "base64(plan)")
p = plan("love_lua", "staged_chain", 0xc5d6e7f8); m = hb64(p)
add("gsl_love_lua_local", "lua", f'-- LÖVE main.lua\nlocal descriptor_c5d6e7f8 = "{m}"\nfunction love.load()\n  love.window.setTitle("Press Start")\nend\n', p, m, "hex(base64(plan))")
# decoys: benign game scripts with descriptor-shaped names but no plan
add("gsl_decoy_luau_benign", "luau", '-- Roblox leaderboard\nlocal DESCRIPTOR_TITLE: string = "Leaderboard v2 - press start"\nlocal Players = game:GetService("Players")\nreturn {}\n', None, None, "benign")
add("gsl_decoy_unrealscript_trunc", "uc", f'class Loader extends Actor;\nvar string Descriptor_X;\ndefaultproperties\n{{\n\tDescriptor_X="{hb64(plan("unrealscript","launcher",1))[:61]}"\n}}\n', None, None, "truncated odd-length hex")
os.makedirs(out, exist_ok=True)
for k, v in L.items():
    open(os.path.join(out, k + "." + v["ext"]), "w", encoding="utf-8").write(v["src"])
json.dump(L, open(os.path.join(out, "manifest.json"), "w"), indent=1)
# --- hard variants (second pass) ---
L.clear()
import textwrap
p = plan("squirrel", "downloader", 0xd6e7f809); js = json.dumps({"v": 3, "plan": p}, separators=(",", ":"))
m = js.replace('"', '""'); half = len(m) // 2
add("gsl_squirrel_verbatim_json", "nut", f'// Squirrel verbatim, multi-line, "" escapes\nlocal descriptor_d6e7f809 = @"{m[:half]}\n{m[half:]}";\nprint(descriptor_d6e7f809);\n', js[:len(js)], js, "raw JSON plan in @\"..\" with \"\" doubling, split over 2 lines")
p = plan("pawn", "staged_chain", 0xe7f8091a); m = hb64(p)
esc = "".join("\\x%02x;" % ord(c) if k % 7 == 0 else c for k, c in enumerate(m[:120])) + "\\\n" + m[120:]
add("gsl_pawn_escapes_packed", "pwn", f'#include <a_samp>\nstatic stock const DESCRIPTOR_E7F8091A[] = !"{esc[:200]}"\n    "{esc[200:]}";\nmain() {{ print("x"); }}\n', p, m, "hex(base64(plan)) with \\xHH; escapes, backslash-newline, packed !\"\", adjacent pieces")
esc2 = "".join("^%d;" % ord(c) if k % 5 == 0 else c for k, c in enumerate(m))
add("gsl_pawn_ctrlchar", "pwn", f'#pragma ctrlchar \'^\'\nnew const descriptor_e7f8091a[] = "{esc2}";\n', p, m, "hex(base64(plan)) with ^ddd; escapes under #pragma ctrlchar '^'")
p = plan("mcfunction", "downloader", 0xf8091a2b); m = b64(p)
add("gsl_mcfunction_continued", "mcfunction", f"# huntress:stage.mcfunction (1.20.2+ backslash continuation)\ndata modify storage huntress:plan descriptor_f8091a2b \\\n    set value '{m[:80]}\\\n    {m[80:]}'\nfunction huntress:run\n", p, m, "base64(plan), single-quoted SNBT split by backslash continuation")
add("gsl_decoy_pawn_benign", "pwn", 'new const DESCRIPTOR_NAME[] = "Press Start \\x41; Loader";\nmain() { print(DESCRIPTOR_NAME); }\n', None, None, "benign")
add("gsl_decoy_mcfunction_benign", "mcfunction", 'data modify storage huntress:descriptor_title set value "Press Start to Decode"\nsay hi\n', None, None, "benign")
for k, v in L.items():
    open(os.path.join(out, k + "." + v["ext"]), "w", encoding="utf-8").write(v["src"])
json.dump(L, open(os.path.join(out, "manifest2.json"), "w"), indent=1)
