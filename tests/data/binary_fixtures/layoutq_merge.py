"""Step 2 of the layoutq_* build: run layoutq_oracle.sh on every fixture, store its output as "expected" and resolve
the hand-written answer-id aliases ("ids": id -> oracle key, read off the question prose) to oracle values.
usage (tests/data/binary_fixtures): python3 layoutq_gen.py && python3 layoutq_merge.py"""
import json, pathlib, subprocess

AL = {
 "layoutq_rs20_d20": {"hcfg_resource_size": "hcfg_resource_length", "resource_size": "hcfg_resource_length",
   "d20_analysis_hcfg_resource_size": "hcfg_resource_length", "set2.d20_analysis_scratch_size": "scratch_length",
   "resource_length": "hcfg_resource_length", "scratch_sha256": "scratch_sha256", "hcfg_resource_offset": "hcfg_resource_offset",
   "scratch_offset": "scratch_offset", "overlay_offset": "overlay_offset", "overlay_size": "overlay_size",
   "hcfg_resource_sha256": "hcfg_resource_sha256_actual", "end_bounds_ok": "end_bounds_ok"},
 "layoutq_permuted_qx21": {"hcfg_resource_size": "hcfg_resource_length", "resource_size": "hcfg_resource_length",
   "scratch_size": "scratch_length", "scratch_sha256": "scratch_sha256", "hcfg_resource_offset": "hcfg_resource_offset",
   "scratch_offset": "scratch_offset", "end_bounds_ok": "end_bounds_ok"},
 "layoutq_bigendian_be77": {"payload_size": "payload_length", "footer_size": "footer_length", "entry_count": "entry_count",
   "count": "entry_count", "k1": "k1", "footer_offset": "footer_offset", "payload_sha256": "payload_sha256",
   "footer_sha256": "footer_sha256_actual", "overlay_size": "overlay_size"},
 "layoutq_u64_filerel_hx64": {"config_size": "config_length", "pad_size": "pad_length", "config_md5": "config_md5",
   "config_offset": "config_offset", "pad_offset": "pad_offset", "config_sha256": "config_sha256_actual"},
 "layoutq_pk19_d19": {"packed_size": "packed_length", "packed_length": "packed_length", "unpacked_sha256": "unpacked_sha256",
   "k1": "k1", "k2": "k2", "overlay_version": "version", "version": "version", "packed_offset": "packed_offset",
   "packed_sha256": "packed_sha256_actual", "overlay_offset": "overlay_offset"},
 "layoutq_decoy_impostor": {"hcfg_resource_size": "hcfg_resource_length", "resource_size": "hcfg_resource_length",
   "scratch_size": "scratch_length", "scratch_sha256": "hcfg_resource_length"},
 "layoutq_decoy_truncated": {"hcfg_resource_size": "hcfg_resource_length", "resource_size": "hcfg_resource_length",
   "scratch_sha256": "scratch_sha256", "hcfg_resource_body_size": "hcfg_resource_body_size", "end_bounds_ok": "end_bounds_ok"},
}
D = pathlib.Path(__file__).parent
for j in sorted(D.glob("layoutq_*.json")):
    f = json.loads(j.read_text())
    exp = json.loads(subprocess.check_output(["bash", str(D / "layoutq_oracle.sh"), str(j.with_suffix(".bin")),
                                              f["oracle_args"]]))
    f["expected"], f["ids"] = exp, {k: exp[v] for k, v in AL[j.stem].items()}
    f["generator_cmd"] = "python3 tests/data/binary_fixtures/layoutq_gen.py  (stdlib struct/hashlib writer)"
    f["oracle_cmd"] = ("bash tests/data/binary_fixtures/layoutq_oracle.sh %s.bin \"$(jq -r .oracle_args %s.json)\"  "
                       "(grep -obaF / od / dd|sha256sum / stat)" % (j.stem, j.stem))
    j.write_text(json.dumps(f, indent=1) + "\n")
