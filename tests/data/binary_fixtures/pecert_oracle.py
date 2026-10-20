"""Independent oracle for pecert_* fixtures: pefile (overlay start, Security dir, CheckSum generate/verify), struct
(WIN_CERTIFICATE walk), `openssl asn1parse` (PKCS#7 DER length), bytes.find for the HCFG magic. Prints expected_facts JSON.
usage (repo root): .venv/bin/python tests/data/binary_fixtures/pecert_oracle.py <file.bin>"""
import json, struct, subprocess, sys, tempfile, pefile
p = sys.argv[1]
data = open(p, "rb").read()
pe = pefile.PE(p)
ov = pe.get_overlay_data_start_offset()
d = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_SECURITY"]]
N = "none"
f = {"overlay_offset": str(ov) if ov is not None else N, "overlay_size": str(len(data) - ov) if ov is not None else N,
     "checksum": hex(pe.OPTIONAL_HEADER.CheckSum), "checksum_computed": hex(pe.generate_checksum()),
     "checksum_valid": "true" if pe.verify_checksum() else "false"}
ok = d.VirtualAddress and d.Size and d.VirtualAddress + d.Size <= len(data)
cert = dict.fromkeys(("certificate_offset", "certificate_size", "certificate_end", "cert_length", "cert_revision",
                      "cert_type", "cert_type_name", "certificate_count", "pkcs7_size", "cert_padding_size",
                      "cert_in_overlay", "data_after_certificate_offset", "data_after_certificate_size"), N)
f["has_certificate"] = "true" if ok else "false"
if ok:
    o, n = d.VirtualAddress, d.Size
    ln, rev, typ = struct.unpack_from("<IHH", data, o)
    with tempfile.NamedTemporaryFile(suffix=".der") as t:
        t.write(data[o + 8:o + ln]); t.flush()
        a = subprocess.run(["openssl", "asn1parse", "-inform", "DER", "-in", t.name], capture_output=True, text=True).stdout
    first = a.splitlines()[0]   # '    0:d=0  hl=4 l=1234 cons: SEQUENCE'
    hl, l = int(first.split("hl=")[1].split()[0]), int(first.split(" l=")[1].split()[0])
    sigs, q = 0, o   # WIN_CERTIFICATE entries, each dwLength rounded up to 8
    while q + 8 <= o + n and struct.unpack_from("<I", data, q)[0] >= 8:
        sigs, q = sigs + 1, q + (struct.unpack_from("<I", data, q)[0] + 7) // 8 * 8
    cert.update(certificate_offset=str(o), certificate_size=str(n), certificate_end=str(o + n), cert_length=str(ln),
                cert_revision="0x%04x" % rev, cert_type=str(typ),
                cert_type_name={2: "WIN_CERT_TYPE_PKCS_SIGNED_DATA"}.get(typ, N), certificate_count=str(sigs),
                pkcs7_size=str(hl + l), cert_padding_size=str(n - 8 - hl - l),
                cert_in_overlay="true" if ov is not None and o >= ov else "false",
                data_after_certificate_offset=str(o + n) if o + n < len(data) else N,
                data_after_certificate_size=str(len(data) - o - n) if o + n < len(data) else N)
f.update(cert)
h = data.find(b"HCFG", ov or 0)
f["hcfg_offset"] = str(h) if h >= 0 else N
if h < 0:
    f["hcfg_location"] = N
elif ok and o <= h < o + n:
    f["hcfg_location"] = "certificate_padding" if h >= o + 8 + hl + l else "certificate"
elif ok and h >= o + n:
    f["hcfg_location"] = "after_certificate"
else:
    f["hcfg_location"] = "overlay"
print(json.dumps(f, indent=1))
