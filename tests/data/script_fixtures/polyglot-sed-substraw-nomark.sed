#n
# sed fixture: descriptor only, no marker line
y/abc/xyz/
s/^.*$/v=3|language=sed|role=staged_chain|verdict=suspicious|attack=T1059|adapter=operation_graph|host_profile=standalone|obfuscation_profile=fragmented_hex|stage_profile=cross_language_handoff|next_language=vbscript|stage_count=3|steps=profile_host,decode_configuration,dispatch_language|campaign_id=SED-050fd535|url=https:\/\/sed-050fd535c2.example.invalid\/stage|file_path=\/tmp\/huntress-sed\/.050fd535c2d4ef8d.stage/p
q
