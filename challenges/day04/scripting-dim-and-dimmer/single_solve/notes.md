# Dim and Dimmer — single solve notes (script-analysis-day-04-shell-contrast)

evidence.zip (AES, pw `infected`) = 30 fixtures: the Day 3 PS1/JS/Batch set (159 ids) + 9 inert VBScript fixtures (72 ids).

hypothesis | evidence | result
---|---|---
Day 3 solver covers PS/JS/Batch unchanged | ran day03 solve.py on this contract: 159 answers | all accepted (batch with the 222)
VBS plan = `Const Material_<id>` -> `Load_<id>` -> `Decode_<id>` -> Chr join, plan `v=1|steps=..|adapter=..|campaign_id=..` | interpreted Load/Decode (vbsplan.py); matches a `Codec_<id>` const ("rep|transform|key")-driven decode on all 9 | plans decode
role/attack/adapter/campaign/indicators from plan, same role graph as JS/Batch; launcher+staged_chain -> T1059.005 | | accepted
representation/transform = Codec fields 1,2 (decimal_pipe, hex_compact, hex_colon, decimal_dash, reversed_decimal; subtract_modulo_256, repeating_key_xor, rolling_xor, single_byte_xor, reverse_bytes) | code agrees with codec in all 9 | accepted
submitted 222 non-control | | accepted, remaining 9
control: no construct -> `direct` | local-dispatch, memory-stage (single-line `If (2>1) Then .. Else ..` junk ignored) | accepted
control: Select Case 1 -> `select_case` | embedded-write, relay-handoff; host-context has an outer `If True Then` wrapper -> still select_case | accepted (If True wrapper = noise)
control: Do .. Exit Do .. Loop | `do_loop` REJECTED, `do_exit` REJECTED, `do_once` | do_once accepted (remote-write, outbound-transfer, staged-handoff)
control: While p<1 .. p=p+1 .. Wend | `while_wend` REJECTED, `while_loop` REJECTED, `while_once` | while_once accepted -> CORRECT 231/231
