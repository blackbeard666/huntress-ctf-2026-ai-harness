"""Central store of GM vocabulary and answer conventions CONFIRMED by correct submissions.

Add to this whenever the Game Master accepts/rejects a specific spelling, so future solvers emit the
exact wording the GM wants instead of re-hitting the wrong-answer cap. Each entry notes where it was proven.
"""

# ELF header fields (binary-reverse-engineering), confirmed Day 1 "ELF Aware".
ELF_ENDIANNESS = {"ELFDATA2LSB": "little", "ELFDATA2MSB": "big"}        # GM rejected "little endian"
ELF_MACHINE = {"EM_X86_64": "x86-64", "EM_386": "x86", "EM_AARCH64": "AArch64", "EM_ARM": "ARM"}  # not "EM_X86_64"
ELF_CLASS = {"ELFCLASS32": "ELF32", "ELFCLASS64": "ELF64"}             # readelf style, not "ELFCLASS64"
ELF_TYPE_AS_IS = True   # e_type submitted as the constant, e.g. "ET_EXEC" (not "EXEC")

# MITRE ATT&CK technique the GM expects per scripting scenario (script-analysis), confirmed Day 1 "Power Play".
SCENARIO_ATTACK = {
    "resource_hijacking": "T1496",     # crypto-mining / resource hijacking
    "synthetic_collection": "T1555.003",  # Credentials from Web Browsers (Login Data/Cookies). GM rejected T1005/T1560/T1119
    "synthetic_impact": "T1486",       # data encrypted for impact (ransomware)
}

# Boolean answers are the lowercase words.
BOOL = {True: "true", False: "false"}
