#!/bin/sh
# prebuild ruby-perl-pack-reps: each source is WRITTEN by its own interpreter (ruby / perl / tclsh / lua), never by lib.codec.
set -e
D=$(dirname "$0")
P_RB1='v=1|language=ruby|role=downloader|attack=T1105|steps=fetch_stage,write_stage,run|campaign_id=RB-7a3c19e2|url=https://rb-7a3c19e2.example.invalid/p'
P_RB2='v=1|language=ruby|role=persistence|attack=T1053.003|steps=write_cron,run|campaign_id=RW-0c4d2b11|file_path=/etc/cron.d/rw-0c4d2b11'
P_PL1='v=1|language=perl|role=exfil|attack=T1041|steps=collect,encode,post|campaign_id=PL-91fe33a0|url=https://pl-91fe33a0.example.invalid/up'
P_PL2='v=1|language=perl|role=loader|attack=T1027|steps=decode_payload,eval|campaign_id=PM-55aa0f17|host=pm-55aa0f17.example.invalid'
P_TC1='v=1|language=tcl|role=launcher|attack=T1059|steps=decode,exec|campaign_id=TC-3e8b6d04|path=/tmp/.tc-3e8b6d04'
P_LU1='v=1|language=lua|role=downloader|attack=T1105|steps=fetch,load,run|campaign_id=LU-d2f0a9c6|url=https://lu-d2f0a9c6.example.invalid/m'
# Ruby: base64 literal through .unpack1("m0"), xor_5a
P="$P_RB1" ruby -e 'x = ENV["P"].bytes.map { |b| b ^ 0x5a }.pack("C*")
puts "# frozen_string_literal: true", "require \"open-uri\"", "CODEC_RB7A = \"ruby_unpack1_m0|xor_5a|\"",
     "MATERIAL_RB7A = \"#{[x].pack("m0")}\".unpack1(\"m0\")", "$stage = MATERIAL_RB7A.bytesize"' > "$D/rb_tpl_unpack1_m0.rb"
# Ruby: %w[] hex word array -> map(&:hex).pack("C*"), add_7
P="$P_RB2" ruby -e 'w = ENV["P"].bytes.map { |b| format("%02x", (b + 7) % 256) }
puts "CODEC_RW0C = \"ruby_word_array_hex|add_7|\"", "MATERIAL_RW0C = %w[#{w.join(" ")}].map(&:hex).pack(\"C*\")"' > "$D/rb_tpl_words_hex.rb"
# Perl: pack("C*", qw(..)) decimal, repeating_key_xor key 1f2e3d
P="$P_PL1" perl -e 'my @k=(0x1f,0x2e,0x3d); my $i=0; my @c = map { $_ ^ $k[$i++ % 3] } unpack("C*", $ENV{P});
print "use strict;\nour \$Codec_pl91 = \"perl_pack_c|repeating_key_xor|1f2e3d\";\nour \$Material_pl91 = pack(\"C*\", qw(@c));\n"' > "$D/pl_tpl_pack_c.pl"
# Perl: use constant + MIME::Base64::decode, reverse
P="$P_PL2" perl -MMIME::Base64 -e 'my $b = encode_base64(scalar reverse($ENV{P}), "");
print "use MIME::Base64 ();\nuse constant CODEC_PM55 => q|perl_mime_base64|reverse||;\n" =~ s/q\|perl_mime_base64\|reverse\|\|/\x27perl_mime_base64|reverse|\x27/r,
      "use constant MATERIAL_PM55 => MIME::Base64::decode(\"$b\");\n"' > "$D/pl_tpl_mime_b64.pl"
# Tcl: set Codec_ {..} + [binary decode hex ".."], add_7
P="$P_TC1" tclsh <<'TCL' > "$D/tcl_tpl_binary_hex.tcl"
binary scan $env(P) c* bs
set out {}
foreach b $bs { append out [format %02x [expr {(($b & 0xff) + 7) % 256}]] }
puts "#!/usr/bin/env tclsh"
puts "set Codec_tc3e {tcl_binary_decode_hex|add_7|}"
puts "set Material_tc3e \[binary decode hex \"$out\"\]"
TCL
# Lua: decimal \ddd escapes, xor_5a
P="$P_LU1" lua5.4 -e 'local t = {} for i = 1, #os.getenv("P") do t[#t+1] = string.format("\\%03d", os.getenv("P"):byte(i) ~ 0x5a) end
print("-- loader") print("Codec_lud2 = \"lua_decimal_escapes|xor_5a|\"") print("Material_lud2 = \"" .. table.concat(t) .. "\"")' > "$D/lua_tpl_decimal_esc.lua"
# DECOY Ruby: pack("H*") of a benign banner under xor_5a (no plan inside)
P='this tool prints the build banner and exits' ruby -e 'x = ENV["P"].bytes.map { |b| b ^ 0x5a }.pack("C*")
puts "CODEC_DB01 = \"ruby_pack_hex|xor_5a|\"", "MATERIAL_DB01 = [\"#{x.unpack1("H*")}\"].pack(\"H*\")"' > "$D/rb_tpl_decoy_banner.rb"
# DECOY Tcl: [binary decode base64 ..] of a benign xor_5a'd config line (plan-free)
P='mode=quiet|retries=3|log=/var/log/updater.log' tclsh <<'TCL' > "$D/tcl_tpl_decoy_benign.tcl"
binary scan $env(P) c* bs
set x {}
foreach b $bs { append x [binary format c [expr {$b ^ 0x5a}]] }
puts "set Codec_tcd0 {tcl_binary_decode_base64|xor_5a|}"
puts "set Material_tcd0 \[binary decode base64 \"[binary encode base64 $x]\"\]"
TCL
