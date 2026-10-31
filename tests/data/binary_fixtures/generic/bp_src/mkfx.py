import json, subprocess, sys
FX = sys.argv[1]
G = {"bp_trace_records.elf": "gcc -O0 -o bp_trace_records.elf tr.c  # three const char[] JSON records + one %s/%d template (gen_generic.sh)",
     "bp_trace_wide.elf": "gcc -O0 -fshort-wchar -o bp_trace_wide.elf tw.c  # two L\"...\" UTF-16LE JSON records (gen_generic.sh)",
     "bp_trace_template.elf": "gcc -O0 -o bp_trace_template.elf tpl.c  # printf template only, no complete record (gen_generic.sh)",
     "bp_trace_records.jar": "javac --release 8 TraceRec.java && jar cfm bp_trace_records.jar m.txt TraceRec.class  # two static final String records (gen_generic.sh)",
     "d28--sample-family-a.elf": "GM artifact: Huntress D28 single_solve evidence.zip member d28--sample-family-a.elf (copied verbatim)",
     "d28--sample-false-friend.elf": "GM artifact: Huntress D28 single_solve evidence.zip member d28--sample-false-friend.elf (copied verbatim)"}
SRC = {"bp_trace_wide.elf": "strings -a -el {m}", "bp_trace_records.jar": "unzip -p {m} TraceRec.class | strings -a"}
U = "Use the unique {d}-- member whose basename ends {b}. "
C = [  # member, field, question, answer_format, jq filter over the parsed record array (None -> expected null)
 ("bp_trace_records.elf", "trace_record_count", "Count the complete huntress.binary.dynamic_trace.v1 JSON trace records embedded in the member (templates with format holes do not count).", {"kind": "integer"}, "length"),
 ("bp_trace_records.elf", "success_event_count", "Parse the embedded huntress.binary.dynamic_trace.v1 records and submit the event_count of the success branch record.", {"kind": "integer"}, '[.[]|select(.branch=="success")|.event_count][0]'),
 ("bp_trace_records.elf", "trace_family", "Submit the family value shared by the embedded dynamic trace records.", {"kind": "exact_text"}, '[.[].family]|unique|.[0]'),
 ("bp_trace_records.elf", "cluster_marker_positive", "Submit true when the embedded trace records carry cluster_marker_positive true, else false.", {"kind": "enum", "accepted_values": ["true", "false"]}, '[.[].cluster_marker_positive]|unique|.[0]|tostring'),
 ("bp_trace_wide.elf", "success_event_count", "Parse the embedded huntress.binary.dynamic_trace.v1 records and submit the event_count of the success branch record.", {"kind": "integer"}, '[.[]|select(.branch=="success")|.event_count][0]'),
 ("bp_trace_wide.elf", "trace_effects", "Submit the effects value of the embedded dynamic trace records.", {"kind": "exact_text"}, '[.[].effects]|unique|.[0]'),
 ("bp_trace_records.jar", "success_event_count", "Parse the embedded huntress.binary.dynamic_trace.v1 records and submit the event_count of the success branch record.", {"kind": "integer"}, '[.[]|select(.branch=="success")|.event_count][0]'),
 ("bp_trace_records.jar", "cluster_marker_positive", "Submit true when the embedded trace records carry cluster_marker_positive true, else false.", {"kind": "enum", "accepted_values": ["true", "false"]}, '[.[].cluster_marker_positive]|unique|.[0]|tostring'),
 ("bp_trace_template.elf", "success_event_count", "Parse the embedded huntress.binary.dynamic_trace.v1 records and submit the event_count of the success branch record.", {"kind": "integer"}, None),
 ("d28--sample-family-a.elf", "trace_record_count", "Count the complete huntress.binary.dynamic_trace.v1 JSON trace records embedded in the member.", {"kind": "integer"}, "length"),
 ("d28--sample-family-a.elf", "family_a_success_event_count", U.format(d="d28", b="family-a.elf") + "Parse its embedded dynamic trace records and submit the success branch record's event_count.", {"kind": "integer"}, '[.[]|select(.branch=="success")|.event_count][0]'),
 ("d28--sample-family-a.elf", "event_counts", "Submit the event_count of every embedded dynamic trace record in file order as a compact JSON integer array.", {"kind": "json"}, 'map(.event_count)|tojson'),
 ("d28--sample-false-friend.elf", "decoy_event_count", "Sum the event_count values of the embedded dynamic trace records whose branch is decoy.", {"kind": "integer"}, '[.[]|select(.branch=="decoy")|.event_count]|add'),
 ("d28--sample-false-friend.elf", "trace_campaign", "Submit the campaign value of the embedded dynamic trace records.", {"kind": "exact_text"}, '[.[].campaign]|unique|.[0]'),
 ("d28--sample-false-friend.elf", "failure_event_count", "Submit the event_count of the failure branch record.", {"kind": "integer"}, None),  # two failure records, no rule -> stays None
]
for m, f, q, af, flt in C:
    src = SRC.get(m, "strings -a {m}").format(m=m)
    oracle = f"{src} | grep -F huntress.binary.dynamic_trace.v1 | jq -cR 'fromjson? // empty' | jq -rs '{flt}'" if flt else \
        f"{src} | grep -F huntress.binary.dynamic_trace.v1 | jq -cR 'fromjson? // empty' | jq -s 'length'  # 0 complete records -> null" \
        if m == "bp_trace_template.elf" else f"{src} | grep -F huntress.binary.dynamic_trace.v1 | jq -cR 'fromjson? // empty' | jq -s '[.[]|select(.branch==\"failure\")|.event_count]'  # [1,8]: ambiguous -> null"
    out = subprocess.run(oracle.split("  #")[0], shell=True, cwd=FX, capture_output=True, text=True).stdout.strip()
    exp = out if flt else None
    d = {"kind": "generic_field", "member": m, "field": f, "question": q, "answer_format": af, "expected": exp,
         "generator_cmd": G[m], "oracle_cmd": oracle, "oracle_output": out}
    if exp is None:
        d["decoy"] = True
    open(f"{FX}/{m}.{f}.json", "w").write(json.dumps(d, indent=1) + "\n")
    print(m, f, repr(out), "->", exp)
