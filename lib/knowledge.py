"""Central store of GM vocabulary and answer conventions CONFIRMED by correct submissions.

Add to this whenever the Game Master accepts/rejects a specific spelling, so future solvers emit the
exact wording the GM wants instead of re-hitting the wrong-answer cap. Each entry notes where it was proven.
"""

# ELF header fields (binary-reverse-engineering), confirmed Day 1 "ELF Aware".
ELF_ENDIANNESS = {"ELFDATA2LSB": "little", "ELFDATA2MSB": "big"}        # GM rejected "little endian"
ELF_MACHINE = {"EM_X86_64": "x86-64", "EM_386": "x86", "EM_AARCH64": "AArch64", "EM_ARM": "ARM"}  # not "EM_X86_64"
ELF_CLASS = {"ELFCLASS32": "ELF32", "ELFCLASS64": "ELF64"}             # readelf style, not "ELFCLASS64"
ELF_TYPE_AS_IS = True   # e_type submitted as the constant, e.g. "ET_EXEC" (not "EXEC")
# Binary container "format" field (e.g. Day 2 "Mangled" cpp_format): lowercase container name.
# GM accepted "elf"; rejected "ELF", "ELF64", "elf64-x86-64", "HCFG", "json". "pe" is inferred, not yet confirmed.
BINARY_FORMAT = {"ELF": "elf", "PE": "pe", "MACHO": "macho"}

# MITRE ATT&CK technique the GM expects per scripting scenario (script-analysis), confirmed Day 1 "Power Play".
SCENARIO_ATTACK = {
    "resource_hijacking": "T1496",     # crypto-mining / resource hijacking
    "synthetic_collection": "T1555.003",  # Credentials from Web Browsers (Login Data/Cookies). GM rejected T1005/T1560/T1119
    "synthetic_impact": "T1486",       # data encrypted for impact (ransomware)
}

# Boolean answers are the lowercase words.
BOOL = {True: "true", False: "false"}

# WSH JScript plan roles (script-analysis), confirmed Day 2 "Host With the Most". Role comes from the ordered steps:
# any graph ending in handoff_script is "staged_chain" even when next_stage is a .js file (GM rejected "relay").
JSCRIPT_ROLE_ATTACK_CONFIRMED = {
    "benign_utility": "none", "downloader": "T1105", "stager": "T1105",  # acquire_remote(+write | +dispatch_memory)
    "impact": "T1486", "dropper": "T1140",          # decode_embedded+write_file = Deobfuscate/Decode Files
    "launcher": "T1059.007", "staged_chain": "T1059.007",  # dispatch_process / handoff graphs = JScript execution
    "uploader": "T1041",                            # upload_remote (adapter CertReq.exe)
}
# GM-rejected: launcher T1218.010 (even with adapter regsvr32.exe); stager T1059.007/T1620; dropper T1105/T1027.009
JSCRIPT_ATTACK_REJECTED = {"launcher": ["T1218.010"], "stager": ["T1059.007", "T1620"], "dropper": ["T1105", "T1027.009"]}
