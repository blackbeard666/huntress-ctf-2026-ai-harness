#!/bin/bash
# usage: wasminv_oracle.sh file  -> one JSON object of the module's "doors", read ONLY from wabt's wasm-objdump -x
# (section headers "Import[5]:" = entries of that section, i.e. defined only; "<- env.log"; "pages: initial=1 max=16
# shared"; an Import "table[" line -> has_table; Elem "segment[] flags=" + "ref.func:2 <t_ping>"; "start function: 5
# <init>"; "mutable=1"; Data "segment[] ... init i32=" / "passive"; Custom "name:") + wasm-validate --enable-threads +
# grep -obUa HCFG; hcfg_mem_offset = active segment init + position of 48434647 in that segment's hexdump.
F="$1"
wasm-validate --enable-threads "$F" >/dev/null 2>&1 && V=true || V=false
OFF=$(grep -obUa HCFG "$F" | head -1 | cut -d: -f1); [ -z "$OFF" ] && OFF=none
wasm-objdump -x "$F" 2>/dev/null | perl -MJSON::PP -ne '
  BEGIN { %r = (valid => $ARGV[0] eq "true" ? JSON::PP::true : JSON::PP::false, hcfg_file_offset => $ARGV[1]);
          @ARGV = (); $r{$_} = 0 for qw(import_count export_count function_count table_count global_count elem_count
          data_segment_count mutable_global_count passive_data_segment_count); $r{$_} = [] for qw(imports exports
          indirect_targets data_offsets custom_sections); $r{start} = "none"; $r{memory_min} = "none";
          $r{memory_max} = "none"; $r{memory_shared} = JSON::PP::false }
  if (/^(\w+)\[(\d+)\]:/) { $sec = $1; my %m = (Import => "import_count", Export => "export_count",
     Function => "function_count", Table => "table_count", Global => "global_count", Elem => "elem_count",
     Data => "data_segment_count"); $r{$m{$sec}} = $2 + 0 if $m{$sec}; next }
  if (/^(Start|Custom|DataCount|Code|Type|Memory):/) { $sec = $1; next }
  if ($sec eq "Import" && /<- (\S+)$/) { push @{$r{imports}}, $1 }
  if ($sec eq "Export" && /-> "(.*)"$/) { push @{$r{exports}}, $1 }
  if (($sec eq "Import" || $sec eq "Memory") && /memory\[0\] pages: initial=(\d+)(?: max=(\d+))?( shared)?/) {
     $r{memory_min} = $1 + 0; $r{memory_max} = defined $2 ? $2 + 0 : "none"; $r{memory_shared} = $3 ? JSON::PP::true : JSON::PP::false }
  if ($sec eq "Import" && /^ - table\[/) { $imptab = 1 }
  if (($sec eq "Import" || $sec eq "Global") && /^ - global\[\d+\].*mutable=1/) { $r{mutable_global_count}++ }
  if ($sec eq "Elem" && /^ - segment\[\d+\] flags=(\d+)/) { $act = !($1 & 1) }
  if ($sec eq "Elem" && $act && /^  - elem\[\d+\] = ref\.func:\d+ <(.*)>/) { push @{$r{indirect_targets}}, $1 }
  if ($sec eq "Start" && /start function: (\d+) <(.*)>/) { $r{start} = $2 }
  if ($sec eq "Data" && /^ - segment\[\d+\].* init i32=(\d+)/) { push @{$r{data_offsets}}, $1 + 0 }
  if ($sec eq "Data" && /^ - segment/) { push @seg, { init => (/ init i32=(\d+)/ ? $1 : undef), hex => "" } }
  if ($sec eq "Data" && @seg && /^  - [0-9a-f]+: ((?:[0-9a-f]{2,4} ?)+)/) { (my $t = $1) =~ s/ //g; $seg[-1]{hex} .= $t }
  if ($sec eq "Data" && /^ - segment\[\d+\].* passive/) { $r{passive_data_segment_count}++ }
  if ($sec eq "Custom" && /^ - name: "(.*)"/) { push @{$r{custom_sections}}, $1 }
  END { $r{hcfg_mem_offset} = "none";
        for my $g (@seg) { my $i = index($g->{hex}, "48434647"); $i = index($g->{hex}, "48434647", $i + 1) while $i > 0 && $i % 2;
          if ($i >= 0) { $r{hcfg_mem_offset} = defined $g->{init} ? $g->{init} + $i / 2 : "none"; last } }
        $r{has_table} = ($r{table_count} || $imptab) ? JSON::PP::true : JSON::PP::false;
        print JSON::PP->new->canonical->encode(\%r), "\n" }' "$V" "$OFF"
