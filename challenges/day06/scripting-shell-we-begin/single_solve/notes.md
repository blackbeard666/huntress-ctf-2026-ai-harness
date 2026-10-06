# Shell We Begin single solve notes
hypothesis | evidence | result
- cumulative bundle: Day 1-5 PS/JS/Batch/VBS/Python + 6 Bash fixtures (399 ids, 42 bash) | zip listing (51 members, AES pw infected) | yes
- old lanes: vendor day05 solver unchanged (new bytes/values vs day05, re-derived) | solver.log: no decode errors | CORRECT
- bash plan = Material_<id> decoded per Codec_<id>='rep|transform|key' (key hex; add_modulo_256 decodes by subtracting) | codec decode == decode inferred from Load_/Decode_ bodies on all 6 | plans are v=1|steps=..|adapter=..|stage_count=..|campaign_id=..|indicators
- bash answers = plan values verbatim; steps joined by '>' ; stage-count = plan stage_count (NOT len(steps): host-context has 2 steps, stage_count=1) | | CORRECT (399/399 first submit)
- roles: decode_configuration,return_configuration=benign; acquire_remote,dispatch_pipe (wget -qO- | bash -s)=stager; decode_embedded,write_file=dropper; acquire_remote,write_file=downloader; locate_local,dispatch_process=launcher; profile_host..dispatch_process=staged_chain | role table | CORRECT (399/399 first submit)
- attack: benign none, stager/downloader T1105, dropper T1140, launcher/staged_chain T1059.004 (Unix Shell, host-language rule) | | CORRECT (399/399 first submit)
- solver: vendored day05 + bashplan.py (restricted Decode_ interpreter + Codec + regex inference, all agree) | hctf solver-test 30/30 cases ok; solver-run single_solve 399 answers, missing [] | done
- synthetic-mastery-bash case (6 re-encoded variants, other reps/transforms/loop syntax, no Codec, CRLF, split Material) | 84/84 match expected | done
