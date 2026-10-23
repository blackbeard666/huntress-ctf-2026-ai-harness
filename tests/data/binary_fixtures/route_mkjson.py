"""Writes route_*.json: expected member per (id, question), read off route_oracle.sh output (readelf / unzip -Z1 /
grep+binascii crc) by the routing semantics; member = basename or null (cannot route -> caller keeps the group)."""
import hashlib, json, pathlib, zipfile
H = pathlib.Path(__file__).parent
ALL = "In evidence.zip, Use all {d}-- members in ZIP central-directory order. "
SCAN = "Scan the specified member for literal HCFG magic and accept the first record whose bounds, CRC32, and decoded JSON validate."
EM = "Read the ELF e_machine field and submit its unsigned base-10 numeric value."
FX = {
 "route_3member": dict(note="loader + plugin_a + plugin_b; decoy (bad crc) HCFG in the loader; NEEDED libalpha.so = plugin_a SONAME; dlopen ./libbeta.so = plugin_b SONAME", routes=[
   ("d22_analysis_config_campaign", ALL.format(d="d22") + SCAN, "d22--variant-000-plugin_a.so", "config_campaign"),
   ("d22_analysis_loader_machine", ALL.format(d="d22") + EM, "d22--variant-000-loader.elf", "machine"),
   ("d22_analysis_plugin_a_exports", ALL.format(d="d22"), "d22--variant-000-plugin_a.so", "exports"),
   ("d22_analysis_plugin_b_config_url", ALL.format(d="d22") + SCAN, "d22--variant-000-plugin_b.so", "config_url"),
   ("d22_analysis_plugin_machine", ALL.format(d="d22") + EM, None, "plugin_machine"),
   ("d22_analysis_soname", "In evidence.zip, Use the member that exports beta_run. Read DT_SONAME.", "d22--variant-000-plugin_b.so", "soname"),
   ("d22_analysis_exports", "In evidence.zip, Use the library named by the loader's DT_NEEDED entry (not libc).", "d22--variant-000-plugin_a.so", "exports"),
   ("d22_analysis_soname", "In evidence.zip, Use the member loaded by the loader at run time via dlopen.", "d22--variant-000-plugin_b.so", "soname"),
   ("d22_analysis_machine", "In evidence.zip, Use the d22-- loader member. " + EM, "d22--variant-000-loader.elf", "machine"),
 ]),
 "route_renamed": dict(note="same bytes renamed without role tokens: roles by ELF kind (PT_INTERP = executable)", routes=[
   ("d23_analysis_loader_machine", ALL.format(d="d23") + EM, "d23--variant-001.elf", "machine"),
   ("d23_analysis_stub_entry_point", ALL.format(d="d23"), "d23--variant-001.elf", "entry_point"),
   ("d23_analysis_config_domain", ALL.format(d="d23") + SCAN, "d23--variant-002.so", "config_domain"),
   ("d23_analysis_payload_machine", ALL.format(d="d23") + EM, None, "payload_machine"),
   ("d23_analysis_exports", "Use the member which exports alpha_init.", "d23--variant-002.so", "exports"),
   ("d23_analysis_needed", "Use the plugin loaded by the host via dlopen.", "d23--variant-000.so", "needed"),
 ]),
 "route_days": dict(note="D15 / D16 / D21 question shapes (verbatim prefixes from the D21 contract)", routes=[
   ("d15_analysis_stripped_machine", "In evidence.zip, Use the unique d15-- member whose basename ends stripped.elf. " + EM, "d15--variant-000-stripped.elf", "machine"),
   ("d15_analysis_symbolized_config_campaign", "In evidence.zip, Use the unique d15-- member whose basename ends symbolized.elf. " + SCAN, "d15--variant-000-symbolized.elf", "config_campaign"),
   ("d16_analysis_compact_format", "In evidence.zip, Use the unique d16-- member whose basename ends compact.wasm. Classify final bytes by magic.", "d16--variant-000-compact.wasm", "format"),
   ("d16_analysis_direct_config_url", "In evidence.zip, Use the unique d16-- member whose basename ends direct.wasm. Parse the WebAssembly section stream.", "d16--variant-000-direct.wasm", "config_url"),
   ("d21_analysis_loader_machine", "In evidence.zip, Use the unique d21-- member whose basename ends loader.elf. " + EM, "d21--variant-000-loader.elf", "machine"),
   ("d21_analysis_plugin_machine", "In evidence.zip, Use the unique d21-- member whose basename ends plugin.cmxs. " + EM, "d21--variant-000-plugin.cmxs", "machine"),
   ("d21_analysis_config_campaign", "In evidence.zip, Use the d21-- plugin.cmxs member; the loader has no scored HCFG config. " + SCAN, "d21--variant-000-plugin.cmxs", "config_campaign"),
   ("d21_analysis_plugin_config_mutex", "In evidence.zip, Use the unique d21-- member whose basename ends plugin.cmxs. " + SCAN, "d21--variant-000-plugin.cmxs", "config_mutex"),
   ("d21_analysis_config_url", ALL.format(d="d21") + SCAN, "d21--variant-000-plugin.cmxs", "config_url"),
   ("d15_analysis_entry_point", ALL.format(d="d15"), None, "entry_point"),
 ]),
 "route_decoy": dict(decoy=True, note="DECOY: the only HCFG is the loader's bad-crc one (and a text impostor); plugin_x/plugin_y identical", routes=[
   ("d24_analysis_config_campaign", ALL.format(d="d24") + SCAN, None, "config_campaign"),
   ("d24_analysis_plugin_machine", ALL.format(d="d24") + EM, None, "plugin_machine"),
   ("d24_analysis_soname", "Use the member that exports beta_run.", None, "soname"),
   ("d24_analysis_soname", "Use the library named by the loader's DT_NEEDED entry.", None, "soname"),
   ("d24_analysis_plugin_x_soname", ALL.format(d="d24"), "d24--variant-000-plugin_x.so", "soname"),
 ]),
}
for stem, spec in FX.items():
    data = (H / f"{stem}.bin").read_bytes()
    z = zipfile.ZipFile(H / f"{stem}.bin")
    out = {"format": "zip of a multi-member dNN-- group", "members": z.namelist(),
           "expected_sha256": [hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()],
           "routes": [{"id": i, "question": q, "member": m, "residual": r} for i, q, m, r in spec["routes"]],
           "generator_cmd": "FX=$PWD bash route_gen.sh   # gcc -shared -Wl,-soname / gcc -ldl, strip, wat2wasm, python3 zlib.crc32 header, zip -X -j",
           "oracle_cmd": f"bash route_oracle.sh {stem}.bin   # unzip -Z1, readelf -hW/-lW/-dW/--dyn-syms, strings, grep -obUa HCFG + binascii.crc32",
           "decoy": spec.get("decoy", False), "note": spec["note"]}
    (H / f"{stem}.json").write_text(json.dumps(out, indent=1) + "\n")
