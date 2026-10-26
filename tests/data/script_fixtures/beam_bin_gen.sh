#!/usr/bin/env bash
# Generator for the compiled-BEAM / escript-archive fixtures (target erlang-beam-chunk-literals).
# Encodes plans with coreutils (gzip / base64 / xxd), compiles with real Erlang/OTP 27 erlc, packs the escript with
# escript:create/2, and takes `expected_plain` from the Erlang VM itself (code:load_binary + apply, then the shell
# decoder) -- never from lib.codec. Run from the repo root:  bash tests/data/script_fixtures/beam_bin_gen.sh
set -euo pipefail
export PATH="$PWD/tools/erlang-dl/root/usr/lib/erlang/bin:$PATH"
FX=tests/data/script_fixtures
W=$(mktemp -d "${TMPDIR:-/tmp}/beamgen.XXXX")

P1='v=3|language=erlang|role=launcher|verdict=malicious|attack=T1059|adapter=process_spawn|host_profile=compiled_beam|obfuscation_profile=gzip_base64|stage_profile=two_stage_download_execute|next_language=bash|stage_count=2|steps=acquire_remote,dispatch_process|campaign_id=ERLANG-7a1c09e2|url=https://erlang-7a1c09e2.example.invalid/stage|file_path=/tmp/huntress-erlang/.7a1c09e2.stage'
P2='v=3|language=erlang|role=stager|verdict=suspicious|attack=T1105|adapter=httpc_request|host_profile=compiled_beam|obfuscation_profile=hex_base64|stage_profile=fetch_and_load|next_language=elixir|stage_count=3|steps=fetch_module,load_binary,apply_entry|campaign_id=ERLANG-41d93b07|url=https://erlang-41d93b07.example.invalid/m.beam|file_path=/var/tmp/.41d93b07.beam'
P3='v=3|language=erlang|role=launcher|verdict=malicious|attack=T1059|adapter=escript_archive|host_profile=escript|obfuscation_profile=base64|stage_profile=single_stage|next_language=powershell|stage_count=1|steps=dispatch_process|campaign_id=ERLANG-c60e5f18|url=https://erlang-c60e5f18.example.invalid/run|file_path=/tmp/.c60e5f18.ps1'

M1=$(printf %s "$P1" | gzip -9n | base64 -w0)
H2=$(printf %s "$P2" | base64 -w0 | xxd -p | tr -d '\n')
M3=$(printf %s "$P3" | base64 -w0)
A2=$(printf %s "${H2:0:60}" | od -An -tu1 -v | tr -s ' \n' ',' | sed 's/^,//;s/,$//')

cat > "$W/hx_stage.erl" <<EOF
-module(hx_stage).
-export([descriptor_7a1c09e2/0, main/1]).
descriptor_7a1c09e2() -> <<"$M1">>.
main(_) -> io:format("~s~n", ["inert analysis fixture"]), {ok, <<"status">>, [1, 2, 3], 3.5}.
EOF
cat > "$W/hx_frag.erl" <<EOF
-module(hx_frag).
-export([descriptor_41d93b07/0]).
-define(PART_A, [$A2]).
descriptor_41d93b07() -> [?PART_A, "${H2:60:200}", <<"${H2:260}">>].
EOF
cat > "$W/hx_esc.erl" <<EOF
-module(hx_esc).
-export([main/1, descriptor_c60e5f18/0]).
descriptor_c60e5f18() -> "$M3".
main(_) -> _ = descriptor_c60e5f18(), ok.
EOF
cat > "$W/hx_status.erl" <<EOF
-module(hx_status).
-export([descriptor_status/0]).
descriptor_status() -> <<"$(printf %s 'status=ok;build=release-2026.10;channel=stable' | base64 -w0)">>.
EOF
(cd "$W" && erlc hx_stage.erl && erlc +debug_info hx_frag.erl && erlc hx_esc.erl && erlc hx_status.erl)
cp "$W/hx_stage.beam" "$FX/beam_bin_litt_gz64.beam"
cp "$W/hx_frag.beam" "$FX/beam_bin_iolist_hex.beam"
cp "$W/hx_status.beam" "$FX/beam_bin_decoy_status.beam"
head -c 300 "$W/hx_stage.beam" > "$FX/beam_bin_decoy_truncated.beam"
erl -noshell -eval '{ok, B} = file:read_file("'"$W"'/hx_esc.beam"),
  ok = escript:create("'"$FX"'/beam_bin_escript_archive.escript",
         [shebang, comment, {emu_args, "-escript main hx_esc"}, {archive, [{"hx_esc.beam", B}], []}]),
  halt().'

# oracles: the Erlang VM loads the module bytes and calls the descriptor; coreutils undo the encoding
ORA_BEAM='erl -noshell -eval "[F,M,Fn]=init:get_plain_arguments(),{ok,B}=file:read_file(F),{module,Mod}=code:load_binary(list_to_atom(M),F,B),io:put_chars(Mod:(list_to_atom(Fn))()),halt()." -extra'
ORA_ESC='erl -noshell -eval "[F,Fn]=init:get_plain_arguments(),{ok,S}=escript:extract(F,[]),{archive,Z}=lists:keyfind(archive,1,S),{ok,[{_,B}]}=zip:extract(Z,[memory]),{module,M}=code:load_binary(hx_esc,\"hx_esc.beam\",B),io:put_chars(M:(list_to_atom(Fn))()),halt()." -extra'
E1=$(eval "$ORA_BEAM $FX/beam_bin_litt_gz64.beam hx_stage descriptor_7a1c09e2" | base64 -d | gunzip)
E2=$(eval "$ORA_BEAM $FX/beam_bin_iolist_hex.beam hx_frag descriptor_41d93b07" | xxd -r -p | base64 -d)
E3=$(eval "$ORA_ESC $FX/beam_bin_escript_archive.escript descriptor_c60e5f18" | base64 -d)
[ "$E1" = "$P1" ] && [ "$E2" = "$P2" ] && [ "$E3" = "$P3" ]

python3 -I - "$FX" "$E1" "$E2" "$E3" <<'PY'
import json, sys
fx, e1, e2, e3 = sys.argv[1:]
gen = "bash tests/data/script_fixtures/beam_bin_gen.sh"
ob = ("PATH=tools/erlang-dl/root/usr/lib/erlang/bin:$PATH erl -noshell -eval \"[F,M,Fn]=init:get_plain_arguments(),"
      "{ok,B}=file:read_file(F),{module,Mod}=code:load_binary(list_to_atom(M),F,B),io:put_chars(Mod:(list_to_atom(Fn))()),"
      "halt().\" -extra ")
oe = ("PATH=tools/erlang-dl/root/usr/lib/erlang/bin:$PATH erl -noshell -eval \"[F,Fn]=init:get_plain_arguments(),"
      "{ok,S}=escript:extract(F,[]),{archive,Z}=lists:keyfind(archive,1,S),{ok,[{_,B}]}=zip:extract(Z,[memory]),"
      "{module,M}=code:load_binary(hx_esc,\\\"hx_esc.beam\\\",B),io:put_chars(M:(list_to_atom(Fn))()),halt().\" -extra ")
rows = {
 "beam_bin_litt_gz64": (e1, False, f"{gen}  (plan | gzip -9n | base64 -w0 -> `descriptor_7a1c09e2() -> <<\"..\">>.`; erlc, OTP 27: zlib LitT BINARY_EXT)",
                        ob + f"{fx}/beam_bin_litt_gz64.beam hx_stage descriptor_7a1c09e2 | base64 -d | gunzip"),
 "beam_bin_iolist_hex": (e2, False, f"{gen}  (plan | base64 -w0 | xxd -p -> iolist `[?PART_A(intlist), \"..\", <<\"..\">>]`; erlc +debug_info: LitT LIST_EXT of STRING_EXT + BINARY_EXT, Dbgi)",
                         ob + f"{fx}/beam_bin_iolist_hex.beam hx_frag descriptor_41d93b07 | xxd -r -p | base64 -d"),
 "beam_bin_escript_archive": (e3, False, f"{gen}  (plan | base64 -w0 -> charlist descriptor; erlc; escript:create([shebang, comment, {{emu_args, \"-escript main hx_esc\"}}, {{archive, [{{\"hx_esc.beam\", B}}], []}}]))",
                              oe + f"{fx}/beam_bin_escript_archive.escript descriptor_c60e5f18 | base64 -d"),
 "beam_bin_decoy_status": (None, True, f"{gen}  (benign `status=ok;..` | base64 -w0 in a descriptor binary; erlc)",
                           ob + f"{fx}/beam_bin_decoy_status.beam hx_status descriptor_status | base64 -d  # -> status=ok;build=release-2026.10;channel=stable, not a plan"),
 "beam_bin_decoy_truncated": (None, True, f"{gen}  (head -c 300 of the hx_stage beam: LitT chunk cut off)",
                              "file tests/data/script_fixtures/beam_bin_decoy_truncated.beam; " + ob + f"{fx}/beam_bin_decoy_truncated.beam hx_stage descriptor_7a1c09e2  # -> badarg/load error: truncated module, no plan"),
}
for name, (exp, decoy, g, o) in rows.items():
    ext = ".escript" if "escript" in name else ".beam"
    raw = open(f"{fx}/{name}{ext}", "rb").read()
    json.dump({"text": raw.decode("latin-1"), "text_encoding": f"latin-1 bytes of {name}{ext} (binary carrier: the "
               "sibling would be read utf-8 'replace', which destroys the zlib LitT)", "expected_plain": exp,
               "decoy": decoy, "target": "erlang-beam-chunk-literals", "generator_cmd": g, "oracle_cmd": o},
              open(f"{fx}/{name}.json", "w"), indent=1)
PY
rm -rf "$W"
echo ok
