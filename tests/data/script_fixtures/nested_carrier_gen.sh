#!/usr/bin/env bash
# Writers for the nested-string-carrier fixtures: each host carries a real D19 inner script (nested_carrier_src/) as an
# escaped / encoded string literal, written by the host language's own toolchain (node, perl, pwsh, php, ruby, python).
set -euo pipefail
cd "$(dirname "$0")"; S=nested_carrier_src; N=${NODE:-node}
# 1 JS: every char of the inner .csx as \uXXXX (JSON.stringify, then ASCII -> \u escapes)
$N -e 'const fs=require("fs");const t=fs.readFileSync(process.argv[1],"utf8");
const lit=JSON.stringify(t).slice(1,-1).replace(/\\(["\\nrt])|[\x20-\x7e]/g,(m,e)=>e?m:"\\u"+m.charCodeAt(0).toString(16).padStart(4,"0"));
fs.writeFileSync("nested_js_unicode.js","// host page\nconst EmbeddedCsx_79a211db = \""+lit+"\";\nmodule.exports = EmbeddedCsx_79a211db;\n")' $S/polyglot-csharp_script-staged-chain.csx
# 2 VBS: each line `""`-doubled, cut into 70-char chunks joined by `" & _` continuations, lines by `& vbCrLf &`
perl -e 'local $/; open my $f,"<",$ARGV[0]; my $t=<$f>; my @o; for my $l (split /\n/,$t){ $l=~s/"/""/g;
 my @c=unpack("(A70)*",$l); push @o, join(" & _\n    \"", map {"$_\""} @c) } my $b="\"".join(" & vbCrLf & _\n    \"",@o);
 open my $w,">","nested_vbs_concat.vbs"; print $w "Option Explicit\nDim EmbeddedPhp_2f\nEmbeddedPhp_2f = $b\nWScript.Echo Len(EmbeddedPhp_2f)\n"' $S/polyglot-php-dropper.php
# 3 PowerShell: single-quoted here-string holding base64 of the whole inner .pl
IN=$S/polyglot-perl-launcher.pl pwsh -NoProfile -Command '$b=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $PWD $env:IN)));
[IO.File]::WriteAllText((Join-Path $PWD "nested_ps_here_b64.ps1"), ("$" + "EmbeddedPl = @'"'"'`n" + ($b -replace ".{76}","$&`n").TrimEnd() + "`n'"'"'@`n" + "$" + "null = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($" + "EmbeddedPl))`n"))'
# 4 Python: triple-quoted literal, every [0-9a-f] of the inner .rb as \xHH (repr-style escapes)
python3 -c 'import sys,re;t=open(sys.argv[1]).read().replace("\\","\\\\");b=re.sub(r"[0-9a-fA-F=]",lambda m:"\\x%02x"%ord(m.group()),t)
open("nested_py_triple.py","w").write("EMBEDDED_RB = \"\"\"\\\n"+b+"\"\"\"\n")' $S/polyglot-ruby-downloader.rb
# 5 MSBuild: inline task <Code> (XML numeric entities for hex digits, &quot;) holding a C# verbatim @"" string of the inner .ts
perl -e 'local $/; open my $f,"<",$ARGV[0]; my $t=<$f>; $t=~s/"/""/g; my $cs="static readonly string EmbeddedTs = \@\"$t\";";
 $cs=~s/&/&amp;/g; $cs=~s/</&lt;/g; $cs=~s/>/&gt;/g; $cs=~s/"/&quot;/g; $cs=~s/([0-9A-Za-z+\/=])/sprintf("&#x%x;",ord $1)/ge if 0;
 $cs=~s/(HUNTRESS_ANALYSIS_V1:B64-)([A-Za-z0-9+\/=]+)/$1.join("",map{sprintf("&#x%x;",ord)}split\/\/,$2)/e;
 open my $w,">","nested_msbuild_entities.proj"; print $w "<Project xmlns=\"http://schemas.microsoft.com/developer/msbuild/2003\">\n  <UsingTask TaskName=\"T\" TaskFactory=\"CodeTaskFactory\" AssemblyFile=\"x.dll\">\n    <Task>\n      <Code Type=\"Class\" Language=\"cs\">$cs</Code>\n    </Task>\n  </UsingTask>\n</Project>\n"' $S/polyglot-typescript-launcher.ts
# 6 depth 3: PHP heredoc (\x escapes) -> JS template literal -> base64 of the whole inner .csx
B=$(base64 -w0 $S/polyglot-csharp_script-staged-chain.csx)
php -r '$js="const EmbeddedCsx = `".$argv[1]."`;\n"; $h=preg_replace_callback("/[A-Za-z0-9]/",fn($m)=>sprintf("\\x%02x",ord($m[0])),addcslashes($js,"\\\$"));
file_put_contents("nested_php_depth3.php","<?php\n\$EmbeddedJs = <<<EOT\n".$h."\nEOT;\n");' "$B"
# 7 Ruby: squiggly heredoc with \u escapes for every hex digit of the inner .csx (ASPX member body)
ruby -e 't=File.read(ARGV[0]).gsub("\\","\\\\\\\\").gsub("#","\\#").gsub(/[0-9a-f]/){|c| "\\u%04x" % c.ord}
File.write("nested_rb_squiggly.rb", "EMBEDDED = <<~ASPX\n" + t.lines.map{|l| "  "+l}.join + "ASPX\n")' $S/polyglot-csharp_script-staged-chain.csx
# 8 decoy: JS \u-escaped inner whose marker / descriptor material is replaced by random hex (no plan)
R=$(head -c 300 /dev/urandom | od -An -tx1 | tr -d ' \n')
$N -e 'const fs=require("fs");let t=fs.readFileSync(process.argv[1],"utf8").replace(/[0-9a-f]{64,}/g,process.argv[2]);
const lit=JSON.stringify(t).slice(1,-1).replace(/\\(["\\nrt])|[\x20-\x7e]/g,(m,e)=>e?m:"\\u"+m.charCodeAt(0).toString(16).padStart(4,"0"));
fs.writeFileSync("nested_decoy_random.js","const EmbeddedCsx_79a211db = \""+lit+"\";\n")' $S/polyglot-csharp_script-staged-chain.csx "$R"
# 9 decoy: VBS host carrying a benign escaped inner script (no marker, descriptor of plain words)
printf 'Dim EmbeddedJs\nEmbeddedJs = "// helper" & vbCrLf & _\n  "var descriptor_00 = ""hello world from a benign page"";" & vbCrLf & _\n  "WScript.Echo(descriptor_00);"\n' > nested_decoy_benign.vbs
# 10 Perl: qq{} literal, every hex digit of the inner .lua as \x{HH}
perl -e 'local $/; open my $f,"<",$ARGV[0]; my $t=<$f>; $t=~s/([\\\$\@{}])/\\$1/g; $t=~s/([0-9a-fA-F=])/sprintf("\\x{%x}",ord $1)/ge;
 open my $w,">","nested_perl_qq.pl"; print $w "my \$embedded_lua = qq{$t};\nprint length(\$embedded_lua), \"\\n\";\n"' $S/polyglot-lua-benign-utility.lua
# 11 D19 ASPX member as shipped (EmbeddedCsx_<8hex> C# regular string)
cp $S/host-aspx-inline-csharp-csharp-script.csx nested_aspx_d19.aspx
